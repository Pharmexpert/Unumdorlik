"""Deterministic checks on script.json (no AI)."""

from __future__ import annotations

import re

from .models import Script

REQUIRED_ORDER = ["HOOK", "INTRO", "CTA", "SECTION_1", "STORY", "PRACTICE",
                  "SHADOWING", "RECAP", "VOCABULARY", "CHALLENGE", "OUTRO"]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def validate_script(sc: Script, target_words: int, tolerance: float = 0.08,
                    min_examples: int = 4, min_practice_turns: int = 6,
                    vocab_items: int = 10) -> list[str]:
    errors: list[str] = []
    wc = sc.count_words()
    lo, hi = int(target_words * (1 - tolerance)), int(target_words * (1 + tolerance))
    if not (lo <= wc <= hi):
        errors.append(f"word_count {wc} chegaradan tashqarida [{lo}, {hi}]")

    present = [t.section for t in sc.turns]
    first_idx = {}
    for i, s in enumerate(present):
        first_idx.setdefault(s, i)
    for s in REQUIRED_ORDER:
        if s not in first_idx:
            errors.append(f"majburiy blok yo'q: {s}")
    order = [s for s in REQUIRED_ORDER if s in first_idx]
    if [first_idx[s] for s in order] != sorted(first_idx[s] for s in order):
        errors.append("bloklar tartibi buzilgan")

    sections = sorted({s for s in present if s.startswith("SECTION_")})
    if len(sections) < 3:
        errors.append(f"SECTION soni {len(sections)} < 3")
    for s in sections:
        txt = sc.text_of(s)
        # crude example count: sentences with quotes or "for example"/"like" or numbered lists
        n = len(re.findall(r"[\"“”]", txt)) // 2 + len(re.findall(r"\bfor example\b|\bfor instance\b", txt, re.IGNORECASE))
        if n < min_examples and len(txt.split()) < 250:
            errors.append(f"{s}: misollar kam ({n}) va bo'lim qisqa")

    practice = [t for t in sc.turns if t.section == "PRACTICE"]
    if len(practice) < min_practice_turns:
        errors.append(f"PRACTICE almashinuvlari {len(practice)} < {min_practice_turns}")

    shadow = [t for t in sc.turns if t.section == "SHADOWING" and t.slow]
    if len(shadow) < 3:
        errors.append(f"SHADOWING da `slow: true` gaplar {len(shadow)} < 3")

    if not (vocab_items - 2 <= len(sc.vocabulary) <= vocab_items + 2):
        errors.append(f"vocabulary soni {len(sc.vocabulary)} (kutilgan {vocab_items}±2)")
    full = _norm(sc.text_of())
    for v in sc.vocabulary:
        if _norm(v.word) not in full:
            errors.append(f"lug'at so'zi skriptda yo'q: {v.word!r}")
        if v.example and _norm(v.example)[:40] not in full:
            errors.append(f"lug'at misoli skriptda yo'q: {v.word!r}")
        if v.cefr.lstrip("~") not in {"A1", "A2", "B1", "B2", "C1", "C2"}:
            errors.append(f"CEFR noto'g'ri: {v.word} -> {v.cefr}")

    long_turns = [t.i for t in sc.turns if len(t.text.split()) > 90]
    if long_turns:
        errors.append(f"90 so'zdan uzun replikalar: {long_turns[:5]}")
    if len(sc.title) > 70:
        errors.append("title 70 belgidan uzun")
    speakers = {t.speaker for t in sc.turns}
    if speakers != {"A", "B"}:
        errors.append(f"ikkala boshlovchi ham gapirishi kerak: {speakers}")
    return errors
