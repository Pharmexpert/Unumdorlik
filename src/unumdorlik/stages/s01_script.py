"""01 — dialogue script via LLM + deterministic validation."""

from __future__ import annotations

from pathlib import Path

from ..llm import LLMError, complete_json
from ..models import Script
from ..prompts import load_prompt
from ..state import write_json
from ..validators import validate_script
from .base import StageContext, StageError, StageManual

ID, NAME = "01", "script"


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.topic.path, ctx.root / "prompts" / "01_dialogue_script.md"]


def _values(ctx: StageContext) -> dict:
    s = ctx.cfg.script
    return {
        "HOST_A_NAME": ctx.cfg.hosts.A.name,
        "HOST_B_NAME": ctx.cfg.hosts.B.name,
        "LEVEL": ctx.topic.meta.get("level", s.level),
        "TARGET_WORDS": int(ctx.topic.meta.get("duration_min", 0) or 0) * s.words_per_minute or s.target_words,
        "WPM": s.words_per_minute,
        "N": s.sections,
        "VOCAB_N": s.vocab_items,
        "TOPIC_FILE_CONTENT": ctx.topic.path.read_text(encoding="utf-8"),
    }


def run(ctx: StageContext) -> str:
    vals = _values(ctx)
    system, user = load_prompt(ctx.root, "01_dialogue_script.md", vals)
    provider = ctx.cfg.script.provider
    if provider == "manual":
        out = ctx.ep.dir / "prompt_01.md"
        out.write_text(f"# SYSTEM\n\n{system}\n\n# USER\n\n{user}\n", encoding="utf-8")
        raise StageManual(f"Promptni {out} dan oling, javobni {ctx.ep.script} ga saqlang, keyin qayta ishga tushiring")

    target = int(vals["TARGET_WORDS"])
    last_errors: list[str] = []
    for attempt in range(2):
        try:
            data = complete_json(provider, system, user, ctx.cfg.script.model)
        except LLMError as e:
            raise StageError(str(e)) from e
        data.setdefault("slug", ctx.ep.slug)
        data.setdefault("hosts", {"A": ctx.cfg.hosts.A.name, "B": ctx.cfg.hosts.B.name})
        try:
            sc = Script.model_validate(data)
        except Exception as e:  # pydantic
            last_errors = [f"schema: {e}"]
        else:
            sc.word_count = sc.count_words()
            last_errors = validate_script(sc, target, vocab_items=ctx.cfg.script.vocab_items)
            if not last_errors:
                write_json(ctx.ep.script, sc)
                return f"{sc.word_count} so'z, {len(sc.turns)} replika, {len(sc.vocabulary)} lug'at"
        ctx.log(f"[yellow]validatsiya xatolari ({attempt + 1}):[/yellow] {last_errors[:6]}")
        user = user + "\n\nYour previous answer had these problems; fix ALL of them and return the full JSON again:\n- " + "\n- ".join(last_errors)
    raise StageError("Skript validatsiyadan o'tmadi: " + "; ".join(last_errors[:8]))
