"""06 — ffmpeg render: Ken Burns slideshow + audio + subtitles (+ chapter titles). Missing images -> generated placeholder."""

from __future__ import annotations

from pathlib import Path

from ..models import Alignment, Script, Storyboard
from .base import StageContext, StageError, ffprobe_duration, require_bin, run_cmd

ID, NAME = "06", "render"


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.audio, ctx.ep.alignment, ctx.ep.storyboard]


def srt_time(s: float) -> str:
    ms = round(s * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def build_srt(sc: Script, al: Alignment, max_chars: int = 84) -> str:
    """Line subtitles: split each turn into chunks of <= max_chars using word times."""
    out, n = [], 1
    for t, tt in zip(sc.turns, al.turns, strict=False):
        words = tt.words or []
        if not words:
            out.append(f"{n}\n{srt_time(tt.start)} --> {srt_time(tt.end)}\n{sc.hosts[t.speaker]}: {t.text}\n")
            n += 1
            continue
        chunk, c_start = [], words[0].s
        for w in words:
            if chunk and len(" ".join(x.w for x in chunk) + " " + w.w) > max_chars:
                out.append(f"{n}\n{srt_time(c_start)} --> {srt_time(chunk[-1].e)}\n{' '.join(x.w for x in chunk)}\n")
                n += 1
                chunk, c_start = [], w.s
            chunk.append(w)
        if chunk:
            out.append(f"{n}\n{srt_time(c_start)} --> {srt_time(chunk[-1].e)}\n{' '.join(x.w for x in chunk)}\n")
            n += 1
    return "\n".join(out)


def placeholder(ctx: StageContext, path: Path, text: str) -> None:
    ffmpeg = require_bin("ffmpeg")
    w, h = ctx.cfg.render.width, ctx.cfg.render.height
    safe = text.replace("'", "").replace(":", " ").replace("\\", "")[:60]
    run_cmd([ffmpeg, "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x1f2a44:s={w}x{h}",
             "-vf", f"drawtext=text='{safe}':fontcolor=white:fontsize=56:x=(w-text_w)/2:y=(h-text_h)/2",
             "-frames:v", "1", str(path)])


def shot_image(ctx: StageContext, sid: int, scene: str) -> Path:
    for ext in (".png", ".jpg"):
        f = ctx.ep.images_dir / f"shot_{sid:03d}{ext}"
        if f.exists():
            return f
    f = ctx.ep.images_dir / f"shot_{sid:03d}_placeholder.png"
    if not f.exists():
        placeholder(ctx, f, scene)
    return f


def kb_filter(kind: str, frames: int, w: int, h: int, fps: int) -> str:
    zoom = {"zoom_in": "min(zoom+0.0006,1.25)", "zoom_out": "if(eq(on,1),1.25,max(zoom-0.0006,1.0))",
            "pan_left": "1.15", "pan_right": "1.15"}[kind]
    x = {"pan_left": f"iw-(iw/zoom)-(on/{frames})*(iw-iw/zoom)", "pan_right": f"(on/{frames})*(iw-iw/zoom)"}.get(kind, "iw/2-(iw/zoom/2)")
    y = "ih/2-(ih/zoom/2)"
    # upscale first so zoompan does not jitter, then zoompan, then back to target size
    return (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps},format=yuv420p")


def run(ctx: StageContext) -> str:
    ffmpeg = require_bin("ffmpeg")
    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    al = Alignment.model_validate_json(ctx.ep.alignment.read_text(encoding="utf-8"))
    sb = Storyboard.model_validate_json(ctx.ep.storyboard.read_text(encoding="utf-8"))
    r = ctx.cfg.render
    total = ffprobe_duration(ctx.ep.audio)
    ctx.ep.subtitles.write_text(build_srt(sc, al), encoding="utf-8")

    clips: list[Path] = []
    clip_dir = ctx.ep.render_dir / "clips"
    clip_dir.mkdir(parents=True, exist_ok=True)
    for k, s in enumerate(sb.shots):
        end = total if k == len(sb.shots) - 1 else s.t_end
        dur = max(end - s.t_start, 1.0)
        img = shot_image(ctx, s.id, s.scene)
        clip = clip_dir / f"clip_{s.id:03d}.mp4"
        frames = int(dur * r.fps) + 1
        run_cmd([ffmpeg, "-y", "-loglevel", "error", "-loop", "1", "-i", str(img), "-t", f"{dur:.3f}",
                 "-vf", kb_filter(s.ken_burns if r.subtitles != "none" and ctx.cfg.visuals.ken_burns else "zoom_in", frames, r.width, r.height, r.fps),
                 "-r", str(r.fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-an", str(clip)], timeout=3600)
        clips.append(clip)
        ctx.log(f"clip {s.id}/{len(sb.shots)} ({dur:.0f}s)")

    lst = clip_dir / "concat.txt"
    lst.write_text("\n".join(f"file '{c.resolve()}'" for c in clips), encoding="utf-8")
    silent = ctx.ep.render_dir / "video_silent.mp4"
    run_cmd([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], timeout=3600)

    vf = []
    if r.subtitles != "none":
        srt = str(ctx.ep.subtitles.resolve()).replace("\\", "/").replace(":", "\\:")
        vf.append(f"subtitles='{srt}':force_style='FontSize=20,Outline=2,Shadow=1,MarginV=40'")
    if r.chapter_titles:
        titles = {s.id: s.title for s in sc.sections}
        for start, sec in al.chapters():
            title = titles.get(sec, sec.replace("_", " ").title())
            if sec.startswith(("HOOK", "OUTRO", "CTA")):
                continue
            end = start + 6
            safe = title.replace("'", "").replace(":", "")[:48]
            vf.append(f"drawtext=text='{safe}':fontcolor=white:fontsize=34:box=1:boxcolor=black@0.45:boxborderw=12:"
                      f"x=40:y=40:enable='between(t,{start:.2f},{end:.2f})'")
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(silent), "-i", str(ctx.ep.audio)]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(r.crf), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(ctx.ep.video)]
    run_cmd(cmd, timeout=7200)
    vdur = ffprobe_duration(ctx.ep.video)
    if abs(vdur - total) > 1.5:
        raise StageError(f"video ({vdur:.1f}s) va audio ({total:.1f}s) davomiyligi mos emas")
    return f"{vdur / 60:.1f} daqiqa, {len(clips)} kadr, subtitr={r.subtitles}"
