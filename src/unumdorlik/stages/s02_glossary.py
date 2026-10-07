"""02 — CEFR candidate extraction (deterministic) + optional LLM refinement + transcript PDF."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

from ..llm import LLMError, complete_json
from ..models import Glossary, Script
from ..prompts import load_prompt
from ..state import write_json
from .base import StageContext

ID, NAME = "02", "glossary"

STOP = set(["a", "an", "the", "and", "or", "but", "if", "then", "so", "because", "of", "to", "in", "on", "at", "for", "with", "from", "by", "as", "is", "are", "was", "were", "be", "been", "being", "am", "do", "does", "did", "have", "has", "had", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their", "this", "that", "these", "those", "there", "here", "what", "which", "who", "whom", "when", "where", "why", "how", "not", "no", "yes", "very", "just", "really", "also", "too", "can", "could", "will", "would", "should", "may", "might", "must", "shall", "let's", "lets", "ok", "okay", "oh", "hey", "well", "now", "today", "every", "each", "all", "some", "any", "many", "much", "more", "most", "one", "two", "three", "four", "five", "ten", "twenty", "hundred", "about", "into", "over", "out", "up", "down", "off", "again", "once", "ever", "never", "always", "only", "own", "same", "than", "too", "s", "t", "m", "re", "ve", "ll", "d", "don", "didn", "doesn", "isn", "aren", "wasn", "weren", "won", "wouldn", "couldn", "shouldn"])
LEVEL_RANK = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.script, ctx.root / "prompts" / "02_vocabulary_glossary.md"]


def load_wordlist(path: Path) -> dict[str, str]:
    """CSV with columns word,cefr (any extra columns ignored). Missing file -> empty dict."""
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            w = (row.get("word") or "").strip().lower()
            lv = (row.get("cefr") or row.get("level") or "").strip().upper()[:2]
            if w and lv in LEVEL_RANK:
                out[w] = lv
    return out


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z'-]+", text.lower()) if w not in STOP and len(w) > 2]


def candidates(sc: Script, wordlist: dict[str, str], min_level: str = "B1") -> list[tuple[str, int, str]]:
    cnt = Counter(tokens(sc.text_of()))
    out = []
    for w, n in cnt.most_common():
        lv = wordlist.get(w, "UNK")
        if lv == "UNK" or LEVEL_RANK[lv] >= LEVEL_RANK[min_level]:
            out.append((w, n, lv))
    return out[:120]


def run(ctx: StageContext) -> str:
    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    wl = load_wordlist(ctx.root / ctx.cfg.script.cefr_wordlist)
    cands = candidates(sc, wl)
    glossary: Glossary
    provider = ctx.cfg.script.provider
    if provider == "manual" or not cands or not wl:
        # Without a CEFR word list the candidates are unranked noise; the script's own vocabulary is better.
        if not wl:
            ctx.log("[yellow]CEFR ro'yxati yo'q (assets/cefr/wordlist.csv); skript lug'ati ishlatiladi[/yellow]")
        glossary = Glossary(glossary=sc.vocabulary)
    else:
        turns_text = "\n".join(f"[{t.i}] {sc.hosts[t.speaker]}: {t.text}" for t in sc.turns)
        cand_csv = "\n".join(f"{w},{n},{lv}" for w, n, lv in cands)
        system, user = load_prompt(ctx.root, "02_vocabulary_glossary.md", {
            "VOCAB_N": ctx.cfg.script.vocab_items, "LEVEL": ctx.topic.meta.get("level", ctx.cfg.script.level),
            "TURNS_TEXT": turns_text, "CANDIDATES_CSV": cand_csv,
        })
        try:
            data = complete_json(provider, system, user, ctx.cfg.script.model)
            glossary = Glossary.model_validate(data)
        except (LLMError, ValueError) as e:
            ctx.log(f"[yellow]LLM lug'at o'tkazib yuborildi ({e}); skript lug'ati ishlatiladi[/yellow]")
            glossary = Glossary(glossary=sc.vocabulary)
    for item in glossary.glossary:
        if item.first_turn is None:
            item.first_turn = next((t.i for t in sc.turns if item.word.lower() in t.text.lower()), None)
    write_json(ctx.ep.glossary, glossary)
    pdf_note = make_pdf(ctx, sc, glossary)
    return f"{len(glossary.glossary)} so'z, {len(cands)} nomzod; {pdf_note}"


def make_pdf(ctx: StageContext, sc: Script, gl: Glossary) -> str:
    md = ctx.ep.dir / "transcript.md"
    lines = [f"# {sc.title}", "", f"Hosts: {sc.hosts['A']} & {sc.hosts['B']}", "", "## Before you listen", ""]
    lines += [f"- **{v.word}** ({v.cefr})" for v in gl.glossary]
    lines += ["", "## Transcript", ""]
    cur = ""
    for t in sc.turns:
        if t.section != cur:
            cur = t.section
            lines += ["", f"### {cur.replace('_', ' ').title()}", ""]
        lines.append(f"**{sc.hosts[t.speaker]}:** {t.text}")
    lines += ["", "## Glossary", "", "| Word | POS | CEFR | IPA | Definition | Example |", "|---|---|---|---|---|---|"]
    lines += [f"| {v.word} | {v.pos} | {v.cefr} | {v.ipa} | {v.definition} | {v.example} |" for v in gl.glossary]
    if gl.bonus_c1_c2:
        lines += ["", "## Bonus C1–C2", ""] + [f"- **{v.word}** ({v.cefr}): {v.definition}" for v in gl.bonus_c1_c2]
    lines += ["", "## Challenge", "", sc.challenge]
    md.write_text("\n".join(lines), encoding="utf-8")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        return "PDF o'tkazildi (reportlab yo'q: uv sync --extra pdf); transcript.md yozildi"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(ctx.ep.transcript_pdf), pagesize=A4, title=sc.title)
    flow = [Paragraph(sc.title, styles["Title"]), Spacer(1, 12)]
    for ln in lines[1:]:
        if ln.startswith("### "):
            flow.append(Paragraph(ln[4:], styles["Heading3"]))
        elif ln.startswith("## "):
            flow.append(Paragraph(ln[3:], styles["Heading2"]))
        elif ln.startswith("|"):
            continue
        elif ln.strip():
            flow.append(Paragraph(ln.replace("**", "<b>", 1).replace("**", "</b>", 1), styles["BodyText"]))
    flow.append(Paragraph("Glossary", styles["Heading2"]))
    for v in gl.glossary:
        flow.append(Paragraph(f"<b>{v.word}</b> ({v.pos}, {v.cefr}) {v.ipa} — {v.definition}<br/><i>{v.example}</i>", styles["BodyText"]))
    doc.build(flow)
    return "transcript.pdf yozildi"
