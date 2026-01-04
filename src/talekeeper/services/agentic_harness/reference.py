"""Reference document parsing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ReferenceDocument:
    """Read-only reference document used to confirm completion criteria."""

    path: Path
    content: str
    acceptance_criteria: List[str]
    required_tests: List[str]
    final_objective: str

    @classmethod
    def load(cls, path: Path) -> "ReferenceDocument":
        resolved = Path(path)
        text = resolved.read_text(encoding="utf-8")
        acceptance = cls._parse_bullet_section(text, "Acceptance Criteria")
        required = cls._parse_bullet_section(text, "Required Qt6 Tests")
        objective = cls._parse_objective(text)
        return cls(
            path=resolved,
            content=text,
            acceptance_criteria=acceptance,
            required_tests=required,
            final_objective=objective,
        )

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_bullet_section(text: str, heading: str) -> List[str]:
        lines = text.splitlines()
        capture = False
        items: List[str] = []
        header = f"## {heading}"
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") and stripped == header:
                capture = True
                continue
            if capture and stripped.startswith("## ") and stripped != header:
                break
            if capture and stripped.startswith("- "):
                items.append(stripped[2:].strip())
        return items

    @staticmethod
    def _parse_objective(text: str) -> str:
        lines = text.splitlines()
        header = "## Objective"
        capture = False
        objective_lines: List[str] = []
        for line in lines:
            stripped = line.rstrip()
            if stripped == header:
                capture = True
                continue
            if capture:
                if stripped.startswith("## ") and stripped != header:
                    break
                objective_lines.append(stripped)
        return "\n".join([line.strip() for line in objective_lines if line.strip()])

