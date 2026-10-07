"""Load prompts/*.md and fill {{PLACEHOLDERS}}. SYSTEM / USER sections are split on '## SYSTEM' / '## USER'."""

from __future__ import annotations

import re
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


def split_prompt(text: str) -> tuple[str, str]:
    """Return (system, user) blocks from a prompt markdown file."""
    sys_m = re.search(r"^## SYSTEM\s*$(.*?)(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    usr_m = re.search(r"^## USER\s*$(.*?)(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    system = sys_m.group(1).strip() if sys_m else ""
    user = usr_m.group(1).strip() if usr_m else text.strip()
    return system, user


def fill(template: str, values: dict[str, object], strict: bool = True) -> str:
    missing: list[str] = []

    def rep(m: re.Match) -> str:
        k = m.group(1)
        if k in values:
            return str(values[k])
        missing.append(k)
        return m.group(0)

    out = PLACEHOLDER.sub(rep, template)
    if strict and missing:
        raise KeyError(f"Prompt placeholders to'ldirilmadi: {sorted(set(missing))}")
    return out


def load_prompt(root: Path, name: str, values: dict[str, object]) -> tuple[str, str]:
    text = (root / "prompts" / name).read_text(encoding="utf-8")
    system, user = split_prompt(text)
    return fill(system, values), fill(user, values)
