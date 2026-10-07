"""Pydantic schemas for every JSON artifact in episodes/<slug>/."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SECTION_ORDER = [
    "HOOK", "INTRO", "CTA", "SECTION", "STORY", "PRACTICE",
    "SHADOWING", "RECAP", "VOCABULARY", "CHALLENGE", "OUTRO",
]
CEFR = Literal["A1", "A2", "B1", "B2", "C1", "C2", "~A1", "~A2", "~B1", "~B2", "~C1", "~C2"]


class Turn(BaseModel):
    i: int
    section: str  # HOOK | INTRO | CTA | SECTION_1.. | STORY | PRACTICE | SHADOWING | RECAP | VOCABULARY | CHALLENGE | OUTRO
    speaker: Literal["A", "B"]
    text: str
    style: str = ""
    slow: bool = False
    visual_cue: str = ""


class SectionInfo(BaseModel):
    id: str
    title: str
    takeaway: str = ""


class VocabItem(BaseModel):
    word: str
    pos: str = ""
    cefr: str = "B1"
    ipa: str = ""
    definition: str
    example: str = ""
    collocation: str = ""
    first_turn: int | None = None


class Script(BaseModel):
    slug: str
    title: str
    alt_titles: list[str] = Field(default_factory=list)
    hook_line: str = ""
    hosts: dict[str, str]
    sections: list[SectionInfo] = Field(default_factory=list)
    turns: list[Turn]
    vocabulary: list[VocabItem] = Field(default_factory=list)
    recap_points: list[str] = Field(default_factory=list)
    challenge: str = ""
    word_count: int = 0

    def text_of(self, section_prefix: str | None = None) -> str:
        return " ".join(t.text for t in self.turns if not section_prefix or t.section.startswith(section_prefix))

    def count_words(self) -> int:
        return sum(len(t.text.split()) for t in self.turns)


class Glossary(BaseModel):
    glossary: list[VocabItem]
    bonus_c1_c2: list[VocabItem] = Field(default_factory=list)


class WordTime(BaseModel):
    w: str
    s: float
    e: float


class TurnTime(BaseModel):
    i: int
    section: str
    speaker: str
    start: float
    end: float
    words: list[WordTime] = Field(default_factory=list)


class Alignment(BaseModel):
    engine: str
    duration: float
    turns: list[TurnTime]

    def chapters(self) -> list[tuple[float, str]]:
        """(start_seconds, section_id) for each first turn of a section."""
        seen: set[str] = set()
        out: list[tuple[float, str]] = []
        for t in self.turns:
            if t.section not in seen:
                seen.add(t.section)
                out.append((t.start, t.section))
        return out


class Shot(BaseModel):
    id: int
    t_start: float
    t_end: float
    turn_from: int
    turn_to: int
    shot_type: str
    scene: str
    camera: str = ""
    mood: str = ""
    prompt: str
    ken_burns: Literal["zoom_in", "zoom_out", "pan_left", "pan_right"] = "zoom_in"
    file: str | None = None  # relative to images/


class Storyboard(BaseModel):
    shots: list[Shot]


class Chapter(BaseModel):
    time: str
    title: str


class Metadata(BaseModel):
    title: str
    description: str
    tags: list[str]
    chapters: list[Chapter] = Field(default_factory=list)
    thumbnail_text: str = ""
    pinned_comment: str = ""
    hashtags: list[str] = Field(default_factory=list)
    publish_at: datetime | None = None
    category_id: int = 27
    default_language: str = "en"


class QACheck(BaseModel):
    name: str
    ok: bool
    detail: str = ""


class QAReport(BaseModel):
    status: Literal["pass", "fail"]
    checks: list[QACheck]


class StageState(BaseModel):
    status: Literal["ok", "failed", "skipped", "pending", "manual"] = "pending"
    input_hash: str = ""
    finished_at: datetime | None = None
    detail: str = ""


class EpisodeState(BaseModel):
    slug: str
    stages: dict[str, StageState] = Field(default_factory=dict)
    publish_at: datetime | None = None
