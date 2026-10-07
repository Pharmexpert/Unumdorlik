"""05 — storyboard (LLM) + images. Engines: flow_browser (Antigravity /images-flow), manual, gemini_image (API, paid)."""

from __future__ import annotations

import os
from pathlib import Path

from ..llm import LLMError, complete_json
from ..models import Alignment, Script, Shot, Storyboard
from ..prompts import load_prompt
from ..state import write_json
from .base import StageContext, StageError, StageManual

ID, NAME = "05", "images"


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.script, ctx.ep.alignment, ctx.root / ctx.cfg.visuals.style_prompt_file]


def style_blocks(ctx: StageContext) -> tuple[str, str]:
    text = (ctx.root / ctx.cfg.visuals.style_prompt_file).read_text(encoding="utf-8")
    import re

    sb = re.search(r'STYLE_BLOCK =\s*"(.*?)"', text, re.DOTALL)
    style = " ".join(sb.group(1).split()) if sb else "3D animated film still, Pixar style, 16:9, no text."
    a, b = ctx.cfg.hosts.A, ctx.cfg.hosts.B
    chars = (f"{a.name}: {a.description or 'adult female host, friendly'}. "
             f"{b.name}: {b.description or 'adult male host, curious'}. "
             "Keep faces, hair, clothing and proportions identical to the reference images.")
    return style, chars


def fallback_storyboard(ctx: StageContext, sc: Script, al: Alignment) -> Storyboard:
    """No LLM: one shot per ~seconds_per_image at turn boundaries, alternating shot types."""
    style, chars = style_blocks(ctx)
    step = ctx.cfg.visuals.seconds_per_image
    shots, start_i, t0, sid = [], 0, 0.0, 1
    types = ["hosts_two_shot", "concept_scene", "host_A_closeup", "example_scene", "host_B_closeup"]
    kb = ["zoom_in", "pan_right", "zoom_out", "pan_left"]
    for k, tt in enumerate(al.turns):
        last = k == len(al.turns) - 1
        if tt.end - t0 >= step or last:
            cue = next((t.visual_cue for t in sc.turns[start_i:k + 1] if t.visual_cue), "")
            scene = cue or f"{sc.hosts['A']} and {sc.hosts['B']} discussing: {sc.turns[start_i].text[:120]}"
            st = types[(sid - 1) % len(types)]
            prompt = f"{style} {chars if 'host' in st else ''} {scene}. medium shot, eye level, soft warm lighting."
            shots.append(Shot(id=sid, t_start=t0, t_end=tt.end, turn_from=sc.turns[start_i].i, turn_to=sc.turns[k].i,
                              shot_type=st, scene=scene, prompt=" ".join(prompt.split()), ken_burns=kb[(sid - 1) % 4]))
            sid, t0, start_i = sid + 1, tt.end, k + 1
    return Storyboard(shots=shots)


def make_storyboard(ctx: StageContext) -> Storyboard:
    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    al = Alignment.model_validate_json(ctx.ep.alignment.read_text(encoding="utf-8"))
    provider = ctx.cfg.script.provider
    if provider != "manual":
        turns_txt = "\n".join(f"[{t.i} @ {tt.start:.0f}-{tt.end:.0f}s {t.section}] {sc.hosts[t.speaker]}: {t.text}"
                              for t, tt in zip(sc.turns, al.turns, strict=False))
        system, user = load_prompt(ctx.root, "03_storyboard_pixar.md", {
            "HOST_A_NAME": ctx.cfg.hosts.A.name, "HOST_B_NAME": ctx.cfg.hosts.B.name,
            "HOST_A_DESCRIPTION": ctx.cfg.hosts.A.description, "HOST_B_DESCRIPTION": ctx.cfg.hosts.B.description,
            "TURNS_WITH_TIMES": turns_txt})
        try:
            data = complete_json(provider, system, user, ctx.cfg.script.model)
            shots = [Shot.model_validate({"id": i + 1, **s}) for i, s in enumerate(data["shots"])]
            sb = Storyboard(shots=shots)
            if len(sb.shots) >= 8:
                write_json(ctx.ep.storyboard, sb)
                return sb
            ctx.log("[yellow]LLM storyboard juda qisqa; fallback ishlatiladi[/yellow]")
        except (LLMError, KeyError, ValueError) as e:
            ctx.log(f"[yellow]LLM storyboard xato ({str(e)[:120]}); fallback[/yellow]")
    sb = fallback_storyboard(ctx, sc, al)
    write_json(ctx.ep.storyboard, sb)
    return sb


def missing_shots(ctx: StageContext, sb: Storyboard) -> list[Shot]:
    out = []
    for s in sb.shots:
        f = ctx.ep.images_dir / f"shot_{s.id:03d}.png"
        if not (f.exists() or f.with_suffix(".jpg").exists()):
            out.append(s)
    return out


def write_todo(ctx: StageContext, sb: Storyboard, missing: list[Shot]) -> Path:
    todo = ctx.ep.images_dir / "TODO.md"
    refs = ", ".join(p.name for p in (ctx.root / ctx.cfg.hosts.character_sheet_dir).glob("*.png")) or "(character sheet yo'q)"
    lines = [f"# Images to generate for `{ctx.ep.slug}` — {len(missing)} of {len(sb.shots)} missing", "",
             f"Aspect ratio 16:9. Save as `episodes/{ctx.ep.slug}/images/shot_NNN.png`. Host references: {refs}", ""]
    for s in missing:
        lines += [f"## shot_{s.id:03d}  ({s.shot_type}, {s.t_start:.0f}–{s.t_end:.0f}s)", "", s.prompt, ""]
    todo.write_text("\n".join(lines), encoding="utf-8")
    return todo


def gemini_images(ctx: StageContext, shots: list[Shot]) -> int:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise StageError("GEMINI_API_KEY yo'q")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    refs = []
    for p in sorted((ctx.root / ctx.cfg.hosts.character_sheet_dir).glob("*.png"))[:6]:
        refs.append(types.Part.from_bytes(data=p.read_bytes(), mime_type="image/png"))
    n = 0
    for s in shots:
        parts = ([*refs] if "host" in s.shot_type else []) + [s.prompt]
        resp = client.models.generate_content(
            model=ctx.cfg.visuals.model, contents=parts,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"],
                                               image_config=types.ImageConfig(aspect_ratio=ctx.cfg.visuals.aspect_ratio)))
        img = next((p.inline_data.data for p in resp.candidates[0].content.parts if getattr(p, "inline_data", None)), None)
        if img:
            (ctx.ep.images_dir / f"shot_{s.id:03d}.png").write_bytes(img)
            n += 1
            ctx.log(f"shot {s.id} ok")
    return n


def run(ctx: StageContext) -> str:
    sb = make_storyboard(ctx) if (ctx.force or not ctx.ep.storyboard.exists()) else \
        Storyboard.model_validate_json(ctx.ep.storyboard.read_text(encoding="utf-8"))
    missing = missing_shots(ctx, sb)
    if not missing:
        return f"{len(sb.shots)} kadr, barchasi mavjud"
    eng = ctx.cfg.visuals.engine
    if eng == "gemini_image":
        n = gemini_images(ctx, missing)
        missing = missing_shots(ctx, sb)
        if missing:
            raise StageError(f"{len(missing)} kadr yaratilmadi")
        return f"{n} kadr Gemini orqali"
    todo = write_todo(ctx, sb, missing)
    hint = {"flow_browser": "Antigravity: `/images-flow " + ctx.ep.slug + "`",
            "flow_gflow": "gflow image t2i ... (gflow-cli)", "manual": "qo'lda"}[eng]
    raise StageManual(f"{len(missing)}/{len(sb.shots)} kadr kerak → {hint}; ro'yxat: {todo}")
