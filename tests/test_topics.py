from datetime import UTC, datetime
from pathlib import Path

import pytest

from unumdorlik.topics import TopicError, list_inbox, next_slot, parse_topic

BODY = "\n".join(["Mavzu mazmuni " + "so'z " * 40])


def write(p: Path, slug: str, extra: str = "") -> Path:
    f = p / "topics" / "inbox" / f"{slug}.md"
    f.write_text(f"---\nslug: {slug}\ntitle_hint: X\n{extra}---\n\n{BODY}\n", encoding="utf-8")
    return f


def test_parse_ok(repo):
    f = write(repo, "why-brains-forget", "publish_at: 2026-10-15T04:00:00Z\n")
    t = parse_topic(f)
    assert t.slug == "why-brains-forget"
    assert t.publish_at == datetime(2026, 10, 15, 4, tzinfo=UTC)


def test_slug_must_match_filename(repo):
    f = repo / "topics" / "inbox" / "a-b.md"
    f.write_text(f"---\nslug: other\n---\n{BODY}", encoding="utf-8")
    with pytest.raises(TopicError):
        parse_topic(f)


def test_example_skipped(repo):
    write(repo, "EXAMPLE-topic")
    write(repo, "real-topic")
    assert [p.stem for p in list_inbox(repo)] == ["real-topic"]


def test_next_slot_two_per_day():
    now = datetime(2026, 10, 7, 0, 0, tzinfo=UTC)
    times = ["09:00", "18:00"]
    taken: set[datetime] = set()
    slots = []
    for _ in range(4):
        s = next_slot(now, times, taken, "Asia/Tashkent", min_lead_hours=6)
        taken.add(s)
        slots.append(s)
    # 09:00 Tashkent = 04:00 UTC (< 6h lead) -> first is 18:00 Tashkent = 13:00 UTC
    assert slots[0] == datetime(2026, 10, 7, 13, tzinfo=UTC)
    assert slots[1] == datetime(2026, 10, 8, 4, tzinfo=UTC)
    assert slots[2] == datetime(2026, 10, 8, 13, tzinfo=UTC)
    assert slots[3] == datetime(2026, 10, 9, 4, tzinfo=UTC)
