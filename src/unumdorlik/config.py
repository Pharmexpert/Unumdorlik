"""Pipeline configuration: config/pipeline.yaml (falls back to pipeline.example.yaml)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from .paths import repo_root


class HostCfg(BaseModel):
    name: str
    role: str = "host"
    tts_voice: str = "en-US-AriaNeural"
    style: str = ""
    description: str = ""  # Pixar character description used in image prompts


class HostsCfg(BaseModel):
    A: HostCfg
    B: HostCfg
    character_sheet_dir: str = "assets/characters"


class ChannelCfg(BaseModel):
    name: str = "Unumdorlik English"
    niche: str = ""
    category_id: int = 27
    default_language: str = "en"
    timezone: str = "UTC"
    publish_times: list[str] = Field(default_factory=lambda: ["04:00", "13:00"])  # 2/day
    privacy_default: Literal["private", "unlisted", "public"] = "private"
    playlist_id: str | None = None


class ScriptCfg(BaseModel):
    provider: Literal["claude_cli", "gemini", "anthropic", "manual"] = "claude_cli"
    model: str = "claude-opus-5-5"
    target_words: int = 2500
    words_per_minute: int = 140
    vocab_items: int = 10
    sections: int = 4
    level: str = "A2-B1"
    cefr_wordlist: str = "assets/cefr/wordlist.csv"


class NotebookLMCfg(BaseModel):
    mode: Literal["notebooklm-py", "enterprise_api", "browser"] = "browser"
    format: str = "deep-dive"
    length: str = "long"


class AudioCfg(BaseModel):
    engine: Literal["gemini_tts", "edge_tts", "notebooklm"] = "gemini_tts"
    gemini_tts_model: str = "gemini-3.8-flash-tts"
    sample_rate: int = 24000
    loudness_lufs: float = -16.0
    turn_gap_ms: int = 450
    section_gap_ms: int = 900
    music_intro: str | None = None
    music_outro: str | None = None
    notebooklm: NotebookLMCfg = Field(default_factory=NotebookLMCfg)


class AlignCfg(BaseModel):
    engine: Literal["auto", "tts_timestamps", "whisperx", "estimate"] = "auto"
    model: str = "large-v3"


class IntroVideoCfg(BaseModel):
    enabled: bool = False
    model: str = "veo-3.1"


class VisualsCfg(BaseModel):
    engine: Literal["gemini_image", "flow_browser", "flow_gflow", "manual"] = "flow_browser"
    model: str = "gemini-3.1-flash-image"
    aspect_ratio: str = "16:9"
    resolution: str = "2K"
    style_prompt_file: str = "prompts/03_storyboard_pixar.md"
    seconds_per_image: int = 35
    ken_burns: bool = True
    intro_video: IntroVideoCfg = Field(default_factory=IntroVideoCfg)


class RenderCfg(BaseModel):
    width: int = 1920
    height: int = 1080
    fps: int = 30
    subtitles: Literal["word_sync", "line", "none"] = "line"
    vocab_cards: bool = True
    chapter_titles: bool = True
    font: str = "assets/fonts/Inter.ttf"
    xfade_seconds: float = 0.5
    crf: int = 18


class ThumbnailCfg(BaseModel):
    model: str = "gemini-3.1-flash-image"
    variants: int = 2


class YouTubeCfg(BaseModel):
    client_secrets: str = "secrets/youtube_client_secret.json"
    token_file: str = "secrets/youtube_token.json"
    upload_captions: bool = True
    made_for_kids: bool = False
    tags_max: int = 20


class ApprovalCfg(BaseModel):
    required: bool = True
    channel: Literal["github_pr", "telegram", "none"] = "github_pr"


class PipelineConfig(BaseModel):
    channel: ChannelCfg = Field(default_factory=ChannelCfg)
    hosts: HostsCfg
    script: ScriptCfg = Field(default_factory=ScriptCfg)
    audio: AudioCfg = Field(default_factory=AudioCfg)
    alignment: AlignCfg = Field(default_factory=AlignCfg)
    visuals: VisualsCfg = Field(default_factory=VisualsCfg)
    render: RenderCfg = Field(default_factory=RenderCfg)
    thumbnail: ThumbnailCfg = Field(default_factory=ThumbnailCfg)
    youtube: YouTubeCfg = Field(default_factory=YouTubeCfg)
    approval: ApprovalCfg = Field(default_factory=ApprovalCfg)

    @property
    def root(self) -> Path:
        return repo_root()


def config_path(root: Path | None = None, profile: str | None = None) -> Path:
    """Resolution: explicit profile > $UNUMDORLIK_PROFILE > config/pipeline.yaml > profiles/stack-b.yaml."""
    import os

    root = root or repo_root()
    profile = profile or os.environ.get("UNUMDORLIK_PROFILE")
    if profile:
        p = Path(profile)
        if p.exists():
            return p
        cand = root / "config" / "profiles" / f"{profile}.yaml"
        if cand.exists():
            return cand
        raise FileNotFoundError(f"Profil topilmadi: {profile}")
    real = root / "config" / "pipeline.yaml"
    return real if real.exists() else root / "config" / "profiles" / "stack-b.yaml"


def load_config(path: Path | None = None) -> PipelineConfig:
    path = path or config_path()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return PipelineConfig.model_validate(data)
