"""Repository and episode path conventions (single source of truth)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def repo_root() -> Path:
    env = os.environ.get("UNUMDORLIK_ROOT")
    if env:
        return Path(env).resolve()
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / "pyproject.toml").exists() and (p / "topics").exists():
            return p
    return here


@dataclass(frozen=True)
class EpisodePaths:
    slug: str
    root: Path

    @property
    def dir(self) -> Path:
        return self.root / "episodes" / self.slug

    @property
    def topic(self) -> Path:
        return self.dir / "topic.md"

    @property
    def script(self) -> Path:
        return self.dir / "script.json"

    @property
    def glossary(self) -> Path:
        return self.dir / "glossary.json"

    @property
    def transcript_pdf(self) -> Path:
        return self.dir / "transcript.pdf"

    @property
    def audio_dir(self) -> Path:
        return self.dir / "audio"

    @property
    def audio(self) -> Path:
        return self.audio_dir / "dialogue.wav"

    @property
    def audio_m4a(self) -> Path:
        return self.audio_dir / "dialogue.m4a"

    @property
    def alignment(self) -> Path:
        return self.dir / "alignment.json"

    @property
    def storyboard(self) -> Path:
        return self.dir / "storyboard.json"

    @property
    def images_dir(self) -> Path:
        return self.dir / "images"

    @property
    def render_dir(self) -> Path:
        return self.dir / "render"

    @property
    def video(self) -> Path:
        return self.render_dir / "video.mp4"

    @property
    def subtitles(self) -> Path:
        return self.dir / "subtitles.srt"

    @property
    def thumbnail(self) -> Path:
        return self.dir / "thumbnail.png"

    @property
    def metadata(self) -> Path:
        return self.dir / "metadata.json"

    @property
    def qa_report(self) -> Path:
        return self.dir / "qa_report.json"

    @property
    def youtube(self) -> Path:
        return self.dir / "youtube.json"

    @property
    def state(self) -> Path:
        return self.dir / "state.json"

    def ensure(self) -> None:
        for d in (self.dir, self.audio_dir, self.images_dir, self.render_dir):
            d.mkdir(parents=True, exist_ok=True)
