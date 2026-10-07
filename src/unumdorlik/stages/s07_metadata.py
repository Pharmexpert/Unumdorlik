"""07 — YouTube metadata (LLM, prompt 04) + thumbnail (best host shot + text overlay)."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..llm import LLMError, complete_json
from ..models import Alignment, Chapter, Metadata, Script, Storyboard
from ..prompts import load_prompt
from ..state import write_json
from .base import StageContext

ID, NAME = "07", "metadata"


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.script, ctx.ep.alignment, ctx.root / "prompts" / "04_youtube_metadata.md"]


def mmss(s: float) -> str:
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


def chapters_from(sc: Script, al: Alignment) -> list[Chapter]:
    titles = {s.id: s.title for s in sc.sections}
    names = {"HOOK": "Intro", "INTRO": "Intro", "STORY": "A Real Story", "PRACTICE": "Practice: Real-Life Situations",
             "SHADOWING": "Shadowing Practice", "RECAP": "Recap", "VOCABULARY": "Vocabulary Recap", "CHALLENGE": "Your Challenge"}
    out, last = [], -100.0
    for start, sec in al.chapters():
        if sec in ("CTA", "OUTRO") or (sec == "INTRO" and out):
            continue
        if start - last < 10:
            continue
        out.append(Chapter(time="0:00" if not out else mmss(start), title=titles.get(sec) or names.get(sec, sec.title())))
        last = start
    return out


def fallback_metadata(ctx: StageContext, sc: Script, chapters: list[Chapter]) -> Metadata:
    vocab = ", ".join(v.word for v in sc.vocabulary)
    desc = (f"{sc.hook_line}\n\nIn this episode, {sc.hosts['A']} and {sc.hosts['B']} talk about: {sc.title}.\n\n"
            "💡 What you'll learn:\n" + "\n".join(f"🔹 {s.takeaway or s.title}" for s in sc.sections) +
            f"\n\n📚 Vocabulary: {vocab}\n\n🔔 Subscribe and try today's challenge in the comments: {sc.challenge}\n\n⏱️ Timestamps:\n" +
            "\n".join(f"{c.time} {c.title}" for c in chapters) +
            f"\n\n#LearnEnglish #EnglishPodcast #{ctx.cfg.channel.name.replace(' ', '')}")
    tags = ["learn english", "english podcast", "english conversation practice", "english for beginners", "esl"] + \
           [v.word for v in sc.vocabulary][:10]
    return Metadata(title=sc.title[:70], description=desc[:4500], tags=tags, chapters=chapters,
                    thumbnail_text=sc.title.split(":")[0][:24], pinned_comment=sc.challenge,
                    hashtags=["#LearnEnglish", "#EnglishPodcast"])


def thumbnail(ctx: StageContext, text: str) -> str:
    sb = Storyboard.model_validate_json(ctx.ep.storyboard.read_text(encoding="utf-8")) if ctx.ep.storyboard.exists() else None
    src = None
    if sb:
        for s in sorted(sb.shots, key=lambda s: ("host" not in s.shot_type, s.id)):
            for ext in (".png", ".jpg"):
                f = ctx.ep.images_dir / f"shot_{s.id:03d}{ext}"
                if f.exists():
                    src = f
                    break
            if src:
                break
    if not src:
        return "thumbnail o'tkazildi (rasm yo'q)"
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        shutil.copy(src, ctx.ep.thumbnail)
        return "thumbnail = rasm nusxasi (Pillow yo'q: uv sync --extra images)"
    im = Image.open(src).convert("RGB").resize((1280, 720))
    d = ImageDraw.Draw(im)
    font_path = ctx.root / ctx.cfg.render.font
    try:
        font = ImageFont.truetype(str(font_path), 88)
    except OSError:
        font = ImageFont.load_default(size=88)
    lines = text.upper().split("\n")[:2] if "\n" in text else [text.upper()[:14], text.upper()[14:28]] if len(text) > 14 else [text.upper()]
    y = 720 - 60 - 100 * len(lines)
    for ln in lines:
        if not ln.strip():
            continue
        d.text((62, y + 4), ln, font=font, fill=(0, 0, 0))
        d.text((58, y), ln, font=font, fill=(255, 220, 60))
        y += 100
    im.save(ctx.ep.thumbnail, "PNG", optimize=True)
    return "thumbnail.png yozildi"


def run(ctx: StageContext) -> str:
    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    al = Alignment.model_validate_json(ctx.ep.alignment.read_text(encoding="utf-8"))
    chapters = chapters_from(sc, al)
    md: Metadata | None = None
    provider = ctx.cfg.script.provider
    if provider != "manual":
        system, user = load_prompt(ctx.root, "04_youtube_metadata.md", {
            "CHANNEL_NAME": ctx.cfg.channel.name, "ALT_TITLES": [sc.title, *sc.alt_titles], "HOOK_LINE": sc.hook_line,
            "CHAPTERS": [c.model_dump() for c in chapters], "VOCAB_WORDS": [v.word for v in sc.vocabulary],
            "CHALLENGE": sc.challenge, "PDF_URL": ctx.topic.meta.get("pdf_url", "(see pinned comment)")})
        try:
            data = complete_json(provider, system, user, ctx.cfg.script.model)
            data["chapters"] = [c.model_dump() for c in chapters]  # never trust LLM times
            md = Metadata.model_validate(data)
        except (LLMError, ValueError) as e:
            ctx.log(f"[yellow]LLM metadata xato ({str(e)[:100]}); fallback[/yellow]")
    if md is None:
        md = fallback_metadata(ctx, sc, chapters)
    md.tags = md.tags[: ctx.cfg.youtube.tags_max]
    md.title = md.title[:100]
    md.category_id = ctx.cfg.channel.category_id
    md.default_language = ctx.cfg.channel.default_language
    md.publish_at = ctx.topic.publish_at
    write_json(ctx.ep.metadata, md)
    note = thumbnail(ctx, md.thumbnail_text or sc.title)
    return f"title={md.title!r}, {len(md.tags)} teg, {len(chapters)} chapter; {note}"
