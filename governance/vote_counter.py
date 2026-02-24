"""
Tallies agent votes and formats the council summary comment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from config import APPROVAL_THRESHOLD, SUPERMAJORITY_THRESHOLD, SUMMARY_COMMENT_MARKER

VoteValue = Literal["APPROVE", "REJECT", "ABSTAIN", "ERROR", "DISABLED"]

VOTE_EMOJI = {
    "APPROVE": "✅",
    "REJECT": "❌",
    "ABSTAIN": "⚪",
    "ERROR": "⚠️",
    "DISABLED": "💤",
}


@dataclass
class AgentVoteRecord:
    agent_name: str
    company: str
    vote: VoteValue
    reasoning: str = ""
    error: str = ""


def tally(records: list[AgentVoteRecord], threshold: float = APPROVAL_THRESHOLD) -> dict:
    """
    Compute the vote outcome.

    Only APPROVE / REJECT votes from agents that actually responded (no ERROR)
    count toward the majority. ABSTAIN and ERROR are excluded from the denominator.
    DISABLED agents are shown for transparency but do not participate.
    Pass threshold=SUPERMAJORITY_THRESHOLD for governance/workflow changes.
    """
    approvals = sum(1 for r in records if r.vote == "APPROVE")
    rejections = sum(1 for r in records if r.vote == "REJECT")
    abstentions = sum(1 for r in records if r.vote == "ABSTAIN")
    errors = sum(1 for r in records if r.vote == "ERROR")
    disabled = sum(1 for r in records if r.vote == "DISABLED")

    denominator = approvals + rejections + abstentions + errors
    if denominator == 0:
        approved = False
        ratio = 0.0
    else:
        ratio = approvals / denominator
        approved = ratio > threshold

    return {
        "approved": approved,
        "approvals": approvals,
        "rejections": rejections,
        "abstentions": abstentions,
        "errors": errors,
        "disabled": disabled,
        "ratio": ratio,
        "threshold": threshold,
        "denominator": denominator,
    }


def format_summary_comment(
    records: list[AgentVoteRecord],
    tally_result: dict,
) -> str:
    """Build the markdown summary comment posted to GitHub."""
    lines: list[str] = [
        SUMMARY_COMMENT_MARKER,
        "## AgentLang Council Vote Summary",
        "",
        "| Agent | Company | Vote | Notes |",
        "|-------|---------|------|-------|",
    ]

    for r in records:
        emoji = VOTE_EMOJI.get(r.vote, "❓")
        vote_display = f"{emoji} {r.vote}"
        notes = ""
        if r.vote == "ERROR":
            notes = f"_{r.error}_" if r.error else "_API error_"
        elif r.vote == "DISABLED":
            notes = r.error or "_Not yet enabled_"
        lines.append(f"| {r.agent_name} | {r.company} | {vote_display} | {notes} |")

    lines.append("")

    t = tally_result
    threshold = t["threshold"]
    is_supermajority = threshold >= SUPERMAJORITY_THRESHOLD
    ratio_pct = f"{t['ratio']:.0%}"
    required_pct = f"{threshold:.0%}"
    counts = f"{t['approvals']} approve / {t['rejections']} reject / {t['abstentions']} abstain"

    if t["denominator"] == 0:
        result_line = "**Result: NO VOTE** — no eligible votes cast"
    elif t["approved"]:
        result_line = f"**Result: ✅ APPROVED** ({counts}, {ratio_pct} > {required_pct} required)"
    else:
        result_line = f"**Result: ❌ REJECTED** ({counts}, {ratio_pct} ≤ {required_pct} required)"

    lines.append(result_line)

    if is_supermajority:
        lines.append(
            f"\n> 🔒 This PR modifies governance or workflow files — "
            f"a super-majority (>{required_pct}) is required."
        )

    if t["errors"] > 0:
        lines.append(
            f"\n> ⚠️ {t['errors']} agent(s) encountered API errors and were excluded from the vote count."
        )

    lines.append("")
    vote_type = "Super-majority" if is_supermajority else "Simple majority"
    lines.append(
        f"_Votes cast by AI agents on the AgentLang Language Council. "
        f"{vote_type} (>{required_pct}) of all votes determines outcome._"
    )

    return "\n".join(lines)


def format_individual_vote_comment(record: AgentVoteRecord, pr_number: int) -> str:
    """Format a single agent's vote comment body."""
    from config import VOTE_COMMENT_MARKER

    emoji = VOTE_EMOJI.get(record.vote, "❓")
    lines = [
        f"<!-- agentlang-vote-{record.agent_name.lower().replace(' ', '-')}-comment -->",
        VOTE_COMMENT_MARKER,
        f"### {emoji} {record.agent_name} ({record.company}) — {record.vote}",
        "",
    ]
    if record.vote == "ERROR":
        lines.append(f"_Could not retrieve vote: {record.error}_")
    else:
        if record.reasoning:
            lines.append(record.reasoning)
    return "\n".join(lines)
