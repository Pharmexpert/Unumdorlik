"""03 — two-voice audio. Engines: gemini_tts (free tier, multi-speaker), edge_tts (free, word timestamps).
Auto-fallback gemini -> edge on quota/auth errors. Output: audio/dialogue.wav (+ audio/segments/, edge_timestamps.json)."""

from __future__ import annotations

import asyncio
import json
import os
import struct
import wave
from pathlib import Path

from ..models import Script
from .base import StageContext, StageError, StageManual, ffprobe_duration, require_bin, run_cmd

ID, NAME = "03", "tts"

EDGE_DEFAULT = {"A": "en-US-AriaNeural", "B": "en-GB-RyanNeural"}


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.script]


def _groups(sc: Script) -> list[list]:
    """Group turns by section so each TTS call stays within input limits."""
    groups, cur, cur_sec = [], [], None
    for t in sc.turns:
        if t.section != cur_sec and cur:
            groups.append(cur)
            cur = []
        cur_sec = t.section
        cur.append(t)
    if cur:
        groups.append(cur)
    return groups


def _write_wav(path: Path, pcm: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def _silence_wav(path: Path, ms: int, rate: int) -> None:
    _write_wav(path, struct.pack("<h", 0) * int(rate * ms / 1000), rate)


def gemini_tts(ctx: StageContext, sc: Script, seg_dir: Path) -> list[Path]:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise StageError("GEMINI_API_KEY yo'q")
    try:
        from google import genai
    except ImportError as e:
        raise StageError("google-genai o'rnatilmagan: uv sync --extra llm") from e
    client = genai.Client(api_key=key)
    names = {"A": ctx.cfg.hosts.A.name, "B": ctx.cfg.hosts.B.name}
    voices = {"A": ctx.cfg.hosts.A.tts_voice, "B": ctx.cfg.hosts.B.tts_voice}
    rate = ctx.cfg.audio.sample_rate
    files: list[Path] = []
    for gi, grp in enumerate(_groups(sc)):
        parts = [{"text": t.text, "speech_metadata": {"speaker": names[t.speaker],
                  "style": (t.style or getattr(ctx.cfg.hosts, t.speaker).style) + (", slow and clear" if t.slow else "")}}
                 for t in grp]
        resp = client.models.generate_content(
            model=ctx.cfg.audio.gemini_tts_model,
            contents=[{"role": "user", "parts": parts}],
            config={"response_modalities": ["AUDIO"], "speech_config": {"multi_speaker_voice_config": {
                "speaker_voice_configs": [
                    {"speaker": names[k], "voice_config": {"prebuilt_voice_config": {"voice_name": voices[k]}}}
                    for k in ("A", "B")]}}},
        )
        pcm = b"".join(p.inline_data.data for c in resp.candidates for p in c.content.parts if getattr(p, "inline_data", None))
        if not pcm:
            raise StageError(f"Gemini TTS bo'sh audio qaytardi (guruh {gi})")
        f = seg_dir / f"g{gi:03d}_{grp[0].section}.wav"
        _write_wav(f, pcm, rate)
        files.append(f)
        ctx.log(f"TTS guruh {gi + 1} ({grp[0].section}) ok")
    return files


def edge_tts(ctx: StageContext, sc: Script, seg_dir: Path) -> list[Path]:
    try:
        import edge_tts
    except ImportError as e:
        raise StageError("edge-tts o'rnatilmagan: uv sync --extra audio") from e
    voices = {k: (getattr(ctx.cfg.hosts, k).tts_voice if "Neural" in getattr(ctx.cfg.hosts, k).tts_voice else EDGE_DEFAULT[k])
              for k in ("A", "B")}
    stamps: dict[int, list] = {}

    async def one(t):
        rate = "-15%" if t.slow else "-5%"
        com = edge_tts.Communicate(t.text, voices[t.speaker], rate=rate)
        mp3 = seg_dir / f"t{t.i:04d}.mp3"
        words = []
        with open(mp3, "wb") as f:
            async for chunk in com.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    words.append({"w": chunk["text"], "s": chunk["offset"] / 1e7, "e": (chunk["offset"] + chunk["duration"]) / 1e7})
        stamps[t.i] = words
        return mp3

    async def all_turns():
        sem = asyncio.Semaphore(4)

        async def guarded(t):
            async with sem:
                return await one(t)
        return await asyncio.gather(*(guarded(t) for t in sc.turns))

    mp3s = asyncio.run(all_turns())
    ffmpeg = require_bin("ffmpeg")
    wavs = []
    for t, mp3 in zip(sc.turns, mp3s, strict=False):
        wav = seg_dir / f"t{t.i:04d}.wav"
        run_cmd([ffmpeg, "-y", "-loglevel", "error", "-i", str(mp3), "-ar", str(ctx.cfg.audio.sample_rate), "-ac", "1", str(wav)])
        wavs.append(wav)
    (ctx.ep.audio_dir / "edge_timestamps.json").write_text(json.dumps(stamps), encoding="utf-8")
    return wavs


def concat(ctx: StageContext, sc: Script, files: list[Path], per_turn: bool) -> None:
    ffmpeg = require_bin("ffmpeg")
    rate = ctx.cfg.audio.sample_rate
    gap_t = ctx.ep.audio_dir / "gap_turn.wav"
    gap_s = ctx.ep.audio_dir / "gap_section.wav"
    _silence_wav(gap_t, ctx.cfg.audio.turn_gap_ms, rate)
    _silence_wav(gap_s, ctx.cfg.audio.section_gap_ms, rate)
    lst = ctx.ep.audio_dir / "concat.txt"
    lines, prev_sec = [], None
    units = list(zip(sc.turns, files, strict=False)) if per_turn else [(None, f) for f in files]
    for t, f in units:
        sec = t.section if t else f.stem.split("_", 1)[1]
        if lines:
            lines.append(f"file '{(gap_s if sec != prev_sec else gap_t).resolve()}'")
        lines.append(f"file '{f.resolve()}'")
        prev_sec = sec
    lst.write_text("\n".join(lines), encoding="utf-8")
    raw = ctx.ep.audio_dir / "dialogue_raw.wav"
    run_cmd([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-ar", str(rate), "-ac", "1", str(raw)])
    run_cmd([ffmpeg, "-y", "-loglevel", "error", "-i", str(raw),
             "-af", f"loudnorm=I={ctx.cfg.audio.loudness_lufs}:TP=-1.5:LRA=11", "-ar", str(rate), str(ctx.ep.audio)])
    run_cmd([ffmpeg, "-y", "-loglevel", "error", "-i", str(ctx.ep.audio), "-c:a", "aac", "-b:a", "128k", str(ctx.ep.audio_m4a)])


def run(ctx: StageContext) -> str:
    sc = Script.model_validate_json(ctx.ep.script.read_text(encoding="utf-8"))
    engine = ctx.cfg.audio.engine
    if engine == "notebooklm":
        raise StageManual("NotebookLM rejimi: Antigravity `/episode` workflow 03-B qadamini bajaring va audio/dialogue.wav ni joylang")
    seg_dir = ctx.ep.audio_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    used = engine
    if engine == "gemini_tts":
        try:
            files = gemini_tts(ctx, sc, seg_dir)
            per_turn = False
        except Exception as e:  # quota / auth / network -> free fallback
            ctx.log(f"[yellow]Gemini TTS ishlamadi ({str(e)[:160]}); edge-tts ga o'tiladi[/yellow]")
            files = edge_tts(ctx, sc, seg_dir)
            per_turn, used = True, "edge_tts(fallback)"
    else:
        files = edge_tts(ctx, sc, seg_dir)
        per_turn = True
    concat(ctx, sc, files, per_turn)
    dur = ffprobe_duration(ctx.ep.audio)
    (ctx.ep.audio_dir / "engine.txt").write_text(used, encoding="utf-8")
    return f"{used}: {dur / 60:.1f} daqiqa, {len(files)} segment"
