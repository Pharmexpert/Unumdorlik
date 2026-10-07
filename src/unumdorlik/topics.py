"""Topic inbox (topics/inbox/*.md with YAML frontmatter) and the 2-per-day publish scheduler."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")


@dataclass
class Topic:
    slug: str
    path: Path
    meta: dict = field(default_factory=dict)
    body: str = ""

    @property
    def publish_at(self) -> datetime | None:
        v = self.meta.get("publish_at")
        if not v:
            return None
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=UTC)
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))


class TopicError(ValueError):
    pass


def parse_topic(path: Path, expected_slug: str | None = None) -> Topic:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise TopicError(f"{path.name}: frontmatter (--- … ---) topilmadi")
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2).strip()
    slug = str(meta.get("slug") or expected_slug or path.stem)
    if not SLUG_RE.match(slug):
        raise TopicError(f"{path.name}: slug noto'g'ri: {slug!r} (a-z, 0-9, '-')")
    if slug != (expected_slug or path.stem):
        raise TopicError(f"{path.name}: slug ({slug}) fayl nomi bilan bir xil bo'lishi kerak")
    if len(body.split()) < 30:
        raise TopicError(f"{path.name}: mavzu mazmuni juda qisqa (≥ 30 so'z kerak)")
    return Topic(slug=slug, path=path, meta=meta, body=body)


def list_inbox(root: Path) -> list[Path]:
    inbox = root / "topics" / "inbox"
    if not inbox.exists():
        return []
    return sorted(p for p in inbox.glob("*.md") if not p.name.startswith("EXAMPLE-"))


def scheduled_times(root: Path) -> set[datetime]:
    """publish_at values already claimed by episodes (state.json / youtube.json)."""
    import json

    out: set[datetime] = set()
    for st in (root / "episodes").glob("*/state.json"):
        try:
            v = json.loads(st.read_text(encoding="utf-8")).get("publish_at")
        except Exception:
            continue
        if v:
            out.add(datetime.fromisoformat(v.replace("Z", "+00:00")).astimezone(UTC))
    return out


def next_slot(
    now: datetime,
    publish_times: list[str],
    taken: set[datetime],
    tz: str = "UTC",
    min_lead_hours: int = 6,
) -> datetime:
    """First free slot (today or later) at one of the configured local times."""
    zone = ZoneInfo(tz)
    local_now = now.astimezone(zone)
    earliest = now + timedelta(hours=min_lead_hours)
    times = sorted(time.fromisoformat(t) for t in publish_times)
    for day in range(60):
        d = (local_now + timedelta(days=day)).date()
        for t in times:
            cand = datetime.combine(d, t, tzinfo=zone).astimezone(UTC)
            if cand >= earliest and cand not in taken:
                return cand
    raise RuntimeError("60 kun ichida bo'sh slot topilmadi")
