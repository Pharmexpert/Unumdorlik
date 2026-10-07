"""Run stages for one episode with idempotency (input hashes in state.json)."""

from __future__ import annotations

import shutil
from pathlib import Path

from .config import PipelineConfig
from .paths import EpisodePaths
from .stages import ORDER, STAGES, StageContext, StageError, StageManual
from .state import hash_paths, is_fresh, load_state, mark, save_state
from .topics import Topic, parse_topic


class PipelinePaused(Exception):
    """A stage needs manual/browser work; message explains what to do."""


def episode_topic(root: Path, slug: str) -> Topic:
    """Topic file: episodes/<slug>/topic.md (copied) or topics/inbox|done/<slug>.md."""
    ep = EpisodePaths(slug, root)
    for cand in (ep.topic, root / "topics" / "inbox" / f"{slug}.md", root / "topics" / "done" / f"{slug}.md"):
        if cand.exists():
            t = parse_topic(cand, expected_slug=slug)
            if cand != ep.topic:
                ep.ensure()
                shutil.copy(cand, ep.topic)
            return t
    raise FileNotFoundError(f"Mavzu topilmadi: {slug}")


def run_episode(cfg: PipelineConfig, root: Path, slug: str, start: str = "01", stop: str = "09",
                force: bool = False, only: list[str] | None = None) -> dict[str, str]:
    topic = episode_topic(root, slug)
    ep = EpisodePaths(slug, root)
    ep.ensure()
    ctx = StageContext(cfg=cfg, ep=ep, topic=topic, root=root, force=force)
    st = load_state(ep)
    if st.publish_at is None and topic.publish_at:
        st.publish_at = topic.publish_at
    results: dict[str, str] = {}
    ids = only or [s for s in ORDER if start <= s <= stop]
    for sid in ids:
        mod = STAGES[sid]
        h = hash_paths(*mod.inputs(ctx), extra=cfg.model_dump_json(include={"script", "audio", "alignment", "visuals", "render"}))
        if not force and is_fresh(st, sid, h):
            results[sid] = "fresh (skip)"
            ctx.log(f"[green]{sid} {mod.NAME}[/green] o'zgarmagan, o'tkazildi")
            continue
        for p in mod.inputs(ctx):
            if not p.exists():
                mark(st, sid, "failed", h, f"kirish yo'q: {p.name}")
                save_state(ep, st)
                raise StageError(f"{sid} {mod.NAME}: kirish fayli yo'q: {p}")
        ctx.log(f"[bold]{sid} {mod.NAME}[/bold] boshlandi")
        try:
            detail = mod.run(ctx)
        except StageManual as e:
            mark(st, sid, "manual", h, str(e))
            save_state(ep, st)
            raise PipelinePaused(f"{sid} {mod.NAME}: {e}") from e
        except StageError as e:
            mark(st, sid, "failed", h, str(e))
            save_state(ep, st)
            raise
        mark(st, sid, "ok", h, detail)
        save_state(ep, st)
        results[sid] = detail
        ctx.log(f"[green]{sid} {mod.NAME} ok[/green] — {detail}")
    return results
