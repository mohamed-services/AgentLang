"""
AgentLang Governance Orchestrator
Entry point for GitHub Actions.

Usage:
  python orchestrator.py --validate-only   # Validate .al files; post comment on failure
  python orchestrator.py --vote            # Run council vote; post results
  python orchestrator.py --flag-readme     # Post warning if README.md is changed
"""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
import traceback

# Make governance/ importable as top-level (agents/ lives alongside this file)
sys.path.insert(0, os.path.dirname(__file__))

import config as cfg
import github_client as gh
from prompts import build_system_prompt, build_user_prompt
from validator import validate_al_files, format_validation_status
from vote_counter import (
    AgentVoteRecord,
    tally,
    format_summary_comment,
    format_individual_vote_comment,
)


# ─── Environment ──────────────────────────────────────────────────────────────

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


PR_NUMBER    = int(_env("PR_NUMBER", "0"))
PR_TITLE     = _env("PR_TITLE")
PR_BODY      = _env("PR_BODY")
BASE_SHA     = _env("BASE_SHA")
HEAD_SHA     = _env("HEAD_SHA")
REPO         = _env("REPO_FULL_NAME")


# ─── Agent loader ─────────────────────────────────────────────────────────────

def load_agent(agent_cfg: dict):
    """Dynamically import and instantiate the agent class."""
    module_name, class_name = agent_cfg["agent_class"].rsplit(".", 1)
    module = importlib.import_module(f"agents.{module_name}")
    cls = getattr(module, class_name)
    return cls(agent_cfg)


# ─── Validate .al files ───────────────────────────────────────────────────────

def cmd_validate_only() -> int:
    """Validate all .al files in the PR diff. Return exit code."""
    results = validate_al_files(BASE_SHA, HEAD_SHA)
    failures = [r for r in results if not r.passed]

    if not failures:
        print("All .al files passed validation.")
        return 0

    # Build and post a comment
    lines = [
        cfg.VALIDATION_COMMENT_MARKER,
        "## ⚠️ AgentLang Validation Failure",
        "",
        "The following `.al` files have validation errors:",
        "",
    ]
    for r in failures:
        lines.append(f"**`{r.file_path}`**")
        lines.append(f"> {r.error}")
        lines.append("")
    lines.append(
        "_All `.al` source files must declare their version on the first line "
        "(printable ASCII only), e.g. `AgentLang 0.1.0-alpha`._"
    )

    body = "\n".join(lines)
    gh.upsert_comment(REPO, PR_NUMBER, cfg.VALIDATION_COMMENT_MARKER, body)
    print(f"Posted validation failure comment for {len(failures)} file(s).")
    return 1  # Fail the CI job


# ─── README flag ──────────────────────────────────────────────────────────────

def cmd_flag_readme() -> int:
    """If README.md is modified, ensure the summary will include the human-approval warning."""
    changed_files = gh.get_changed_files(REPO, BASE_SHA, HEAD_SHA)
    if "README.md" in changed_files:
        print("README.md detected in changed files — human approval warning will be included.")
    return 0


# ─── Agent vote ───────────────────────────────────────────────────────────────

async def run_single_agent(agent_cfg: dict, system_prompt: str, user_prompt: str) -> AgentVoteRecord:
    """Call one agent and return its vote record."""
    name    = agent_cfg["name"]
    company = agent_cfg["company"]

    # Check API key presence
    api_key_env = agent_cfg.get("api_key_env")
    if api_key_env and not os.environ.get(api_key_env):
        print(f"  [{name}] API key env {api_key_env!r} not set — skipping.")
        return AgentVoteRecord(
            agent_name=name,
            company=company,
            vote="ABSTAIN",
            reasoning="",
            error=f"API key `{api_key_env}` not configured.",
        )

    try:
        agent = load_agent(agent_cfg)
        vote_value, reasoning = await agent.vote(system_prompt, user_prompt)
        print(f"  [{name}] voted {vote_value}")
        return AgentVoteRecord(
            agent_name=name,
            company=company,
            vote=vote_value,  # type: ignore[arg-type]
            reasoning=reasoning,
        )
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [{name}] ERROR: {exc}\n{tb}")
        return AgentVoteRecord(
            agent_name=name,
            company=company,
            vote="ERROR",
            error=str(exc),
        )


def _build_disabled_record(agent_cfg: dict) -> AgentVoteRecord:
    reason = agent_cfg.get("abstain_reason", "Not yet enabled")
    return AgentVoteRecord(
        agent_name=agent_cfg["name"],
        company=agent_cfg["company"],
        vote="DISABLED",
        error=reason,
    )


async def cmd_vote() -> int:
    """Run the full council vote and post results. Return exit code."""
    changed_files = gh.get_changed_files(REPO, BASE_SHA, HEAD_SHA)
    has_readme = "README.md" in changed_files

    # Auto-reject PRs that touch the root README.md
    if has_readme:
        body = "\n".join([
            cfg.SUMMARY_COMMENT_MARKER,
            "## AgentLang Council Vote Summary",
            "",
            "**Result: ❌ AUTOMATICALLY REJECTED** — This PR modifies the root `README.md`.",
            "",
            "> Per governance rules, any pull request that changes `README.md` is automatically rejected.",
        ])
        gh.upsert_comment(REPO, PR_NUMBER, cfg.SUMMARY_COMMENT_MARKER, body)
        print("PR automatically rejected: modifies root README.md")
        return 1

    # Fetch diff
    diff = gh.get_pr_diff(REPO, BASE_SHA, HEAD_SHA, max_chars=cfg.MAX_DIFF_CHARS)

    # Validation status for prompt context
    val_results = validate_al_files(BASE_SHA, HEAD_SHA)
    validation_status = format_validation_status(val_results)

    system_prompts: dict[str, str] = {}
    user_prompt = build_user_prompt(
        pr_number=PR_NUMBER,
        pr_title=PR_TITLE,
        pr_body=PR_BODY,
        changed_files=changed_files,
        diff=diff,
        validation_status=validation_status,
    )

    # Split agents into active vs disabled
    active_agents = [a for a in cfg.AGENTS if a["enabled"] and a.get("agent_class")]
    disabled_agents = [a for a in cfg.AGENTS if not a["enabled"]]

    # Build system prompts for active agents
    for agent_cfg in active_agents:
        system_prompts[agent_cfg["id"]] = build_system_prompt(
            agent_name=agent_cfg["name"],
            company=agent_cfg["company"],
        )

    print(f"Calling {len(active_agents)} active agent(s) concurrently...")
    tasks = [
        run_single_agent(agent_cfg, system_prompts[agent_cfg["id"]], user_prompt)
        for agent_cfg in active_agents
    ]
    active_records: list[AgentVoteRecord] = await asyncio.gather(*tasks)

    # Combine with disabled records (for display only)
    disabled_records = [_build_disabled_record(a) for a in disabled_agents]
    all_records = list(active_records) + disabled_records

    # Post individual vote comments (active agents only)
    for record in active_records:
        marker = f"<!-- agentlang-vote-{record.agent_name.lower().replace(' ', '-')}-comment -->"
        body = format_individual_vote_comment(record, PR_NUMBER)
        try:
            gh.upsert_comment(REPO, PR_NUMBER, marker, body)
        except Exception as exc:
            print(f"  Warning: could not post comment for {record.agent_name}: {exc}")

    # Tally and post summary (active records only for the vote count)
    tally_result = tally(active_records)
    summary_body = format_summary_comment(all_records, tally_result, has_readme)
    gh.upsert_comment(REPO, PR_NUMBER, cfg.SUMMARY_COMMENT_MARKER, summary_body)

    print(f"\nVote result: {'APPROVED' if tally_result['approved'] else 'REJECTED'} "
          f"({tally_result['approvals']}✅ / {tally_result['rejections']}❌ / "
          f"{tally_result['abstentions']}⚪)")

    # Exit 1 if rejected (turns the CI check red)
    return 0 if tally_result["approved"] else 1


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="AgentLang governance orchestrator")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--vote",          action="store_true")
    parser.add_argument("--flag-readme",   action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        return cmd_validate_only()
    elif args.flag_readme:
        return cmd_flag_readme()
    elif args.vote:
        return asyncio.run(cmd_vote())
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
