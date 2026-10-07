"""08 — deterministic QA gate. Writes qa_report.json; fails the pipeline on any failed check."""

from __future__ import annotations

from pathlib import Path

from ..models import Metadata, QACheck, QAReport, Script, Storyboard
from ..state import write_json
from .base import StageContext, StageError, ffprobe_duration

ID, NAME = "08", "qa"
BANNED = {"as an ai", "language model", "lorem ipsum"}


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.video, ctx.ep.metadata, ctx.ep.subtitles]


def run(ctx: StageContext) -> str:
    checks: list[QACheck] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append(QACheck(name=name, ok=ok, detail=detail))

    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    md = Metadata.model_validate_json(ctx.ep.metadata.read_text(encoding="utf-8"))
    sb = Storyboard.model_validate_json(ctx.ep.storyboard.read_text(encoding="utf-8"))

    vdur = ffprobe_duration(ctx.ep.video)
    adur = ffprobe_duration(ctx.ep.audio)
    add("duration_range", 8 * 60 <= vdur <= 25 * 60, f"{vdur / 60:.1f} min")
    add("av_sync_length", abs(vdur - adur) <= 1.5, f"video {vdur:.1f}s / audio {adur:.1f}s")
    add("video_size", ctx.ep.video.stat().st_size > 2_000_000, f"{ctx.ep.video.stat().st_size / 1e6:.1f} MB")
    placeholders = list(ctx.ep.images_dir.glob("*_placeholder.png"))
    add("no_placeholder_images", not placeholders, f"{len(placeholders)} placeholder")
    add("shots_count", 8 <= len(sb.shots) <= 60, str(len(sb.shots)))
    add("title_length", 10 <= len(md.title) <= 100, str(len(md.title)))
    add("description_length", 200 <= len(md.description) <= 5000, str(len(md.description)))
    add("tags_length", 0 < sum(len(t) + 2 for t in md.tags) <= 500, str(len(md.tags)))
    add("chapters", len(md.chapters) >= 3 and md.chapters[0].time == "0:00", str(len(md.chapters)))
    add("thumbnail", ctx.ep.thumbnail.exists() and ctx.ep.thumbnail.stat().st_size < 2_000_000, "")
    add("subtitles", ctx.ep.subtitles.exists() and ctx.ep.subtitles.stat().st_size > 1000, "")
    txt = (sc.text_of() + " " + md.description).lower()
    add("banned_phrases", not any(b in txt for b in BANNED), "")
    add("vocab_count", 6 <= len(sc.vocabulary) <= 14, str(len(sc.vocabulary)))

    status = "pass" if all(c.ok for c in checks) else "fail"
    write_json(ctx.ep.qa_report, QAReport(status=status, checks=checks))
    failed = [c for c in checks if not c.ok]
    if failed:
        raise StageError("QA: " + "; ".join(f"{c.name} ({c.detail})" for c in failed))
    return f"{len(checks)} tekshiruv o'tdi"
