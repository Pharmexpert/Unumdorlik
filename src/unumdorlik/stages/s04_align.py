"""04 — word/turn timing. auto: edge_timestamps -> whisperx -> proportional estimate."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import Alignment, Script, TurnTime, WordTime
from ..state import write_json
from .base import StageContext, StageError, ffprobe_duration

ID, NAME = "04", "align"


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.script, ctx.ep.audio]


def from_edge(ctx: StageContext, sc: Script, total: float) -> Alignment | None:
    f = ctx.ep.audio_dir / "edge_timestamps.json"
    if not f.exists():
        return None
    stamps = {int(k): v for k, v in json.loads(f.read_text(encoding="utf-8")).items()}
    seg_dir = ctx.ep.audio_dir / "segments"
    turns, cursor, prev_sec = [], 0.0, None
    for t in sc.turns:
        wav = seg_dir / f"t{t.i:04d}.wav"
        if not wav.exists():
            return None
        if turns:
            cursor += (ctx.cfg.audio.section_gap_ms if t.section != prev_sec else ctx.cfg.audio.turn_gap_ms) / 1000
        dur = ffprobe_duration(wav)
        words = [WordTime(w=w["w"], s=cursor + w["s"], e=cursor + w["e"]) for w in stamps.get(t.i, [])]
        turns.append(TurnTime(i=t.i, section=t.section, speaker=t.speaker, start=cursor, end=cursor + dur, words=words))
        cursor += dur
        prev_sec = t.section
    return Alignment(engine="edge_timestamps", duration=total, turns=turns)


def from_whisperx(ctx: StageContext, sc: Script, total: float) -> Alignment | None:
    try:
        import whisperx  # noqa: F401
    except ImportError:
        return None
    import whisperx as wx

    device = "cpu"
    audio = wx.load_audio(str(ctx.ep.audio))
    model_a, meta = wx.load_align_model(language_code="en", device=device)
    # One segment per turn with a rough window; whisperx refines the word times inside.
    est = estimate(sc, total)
    segments = [{"text": t.text, "start": tt.start, "end": tt.end} for t, tt in zip(sc.turns, est.turns, strict=False)]
    res = wx.align(segments, model_a, meta, audio, device, return_char_alignments=False)
    turns = []
    for t, seg in zip(sc.turns, res["segments"], strict=False):
        words = [WordTime(w=w["word"], s=w.get("start", seg["start"]), e=w.get("end", seg["end"])) for w in seg.get("words", [])]
        turns.append(TurnTime(i=t.i, section=t.section, speaker=t.speaker, start=seg["start"], end=seg["end"], words=words))
    return Alignment(engine="whisperx", duration=total, turns=turns)


def estimate(sc: Script, total: float) -> Alignment:
    """Proportional estimate by word count (slow turns weighted 1.3x). Good enough for slide timing."""
    weights = [len(t.text.split()) * (1.3 if t.slow else 1.0) + 2.0 for t in sc.turns]
    scale = total / sum(weights)
    turns, cursor = [], 0.0
    for t, w in zip(sc.turns, weights, strict=False):
        dur = w * scale
        words = t.text.split()
        per = dur / max(len(words), 1)
        wt = [WordTime(w=x, s=cursor + k * per, e=cursor + (k + 1) * per) for k, x in enumerate(words)]
        turns.append(TurnTime(i=t.i, section=t.section, speaker=t.speaker, start=cursor, end=cursor + dur, words=wt))
        cursor += dur
    return Alignment(engine="estimate", duration=total, turns=turns)


def run(ctx: StageContext) -> str:
    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    total = ffprobe_duration(ctx.ep.audio)
    eng = ctx.cfg.alignment.engine
    al: Alignment | None = None
    if eng in ("auto", "tts_timestamps"):
        al = from_edge(ctx, sc, total)
    if al is None and eng in ("auto", "whisperx"):
        al = from_whisperx(ctx, sc, total)
    if al is None:
        if eng == "whisperx":
            raise StageError("whisperx o'rnatilmagan: uv sync --extra align")
        al = estimate(sc, total)
    write_json(ctx.ep.alignment, al)
    return f"{al.engine}: {len(al.turns)} replika, {total / 60:.1f} daqiqa"
