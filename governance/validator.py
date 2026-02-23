"""
Validates .al source files.
Rule: The first line must be non-empty and consist entirely of printable ASCII (U+0020–U+007E).
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field

PRINTABLE_ASCII_RE = re.compile(r"^[ -~]+$")


@dataclass
class ValidationResult:
    file_path: str
    passed: bool
    error: str = ""


def validate_al_content(content: str, file_path: str) -> ValidationResult:
    """Validate the content of a single .al file."""
    lines = content.splitlines()
    if not lines or not lines[0].strip():
        return ValidationResult(
            file_path=file_path,
            passed=False,
            error="First line is empty. .al files must declare their version on line 1 "
                  "(e.g. `AgentLang 0.1.0-alpha`).",
        )
    first_line = lines[0]
    if not PRINTABLE_ASCII_RE.match(first_line):
        return ValidationResult(
            file_path=file_path,
            passed=False,
            error=f"First line contains non-printable or non-ASCII characters: {first_line!r}",
        )
    return ValidationResult(file_path=file_path, passed=True)


def get_changed_al_files(base_sha: str, head_sha: str) -> list[str]:
    """Return list of .al files added or modified in the diff."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", base_sha, head_sha],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.splitlines() if f.endswith(".al")]


def validate_al_files(base_sha: str, head_sha: str) -> list[ValidationResult]:
    """Validate all .al files changed between base_sha and head_sha."""
    al_files = get_changed_al_files(base_sha, head_sha)
    results: list[ValidationResult] = []
    for path in al_files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            results.append(validate_al_content(content, path))
        except FileNotFoundError:
            # File was deleted — skip validation
            pass
        except Exception as exc:
            results.append(ValidationResult(
                file_path=path,
                passed=False,
                error=f"Could not read file: {exc}",
            ))
    return results


def format_validation_status(results: list[ValidationResult]) -> str:
    """Return a short human-readable validation summary for the vote prompt."""
    if not results:
        return "No .al files changed."
    lines: list[str] = []
    for r in results:
        if r.passed:
            lines.append(f"- `{r.file_path}`: VALID")
        else:
            lines.append(f"- `{r.file_path}`: INVALID — {r.error}")
    return "\n".join(lines)
