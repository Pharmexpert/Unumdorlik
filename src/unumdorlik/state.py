"""Per-episode state.json: stage status + input hashes for idempotent re-runs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .models import EpisodeState, StageState
from .paths import EpisodePaths


def hash_paths(*paths: Path, extra: str = "") -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p.name).encode())
        if p.exists() and p.is_file():
            h.update(p.read_bytes())
        else:
            h.update(b"<missing>")
    h.update(extra.encode())
    return h.hexdigest()[:16]


def load_state(ep: EpisodePaths) -> EpisodeState:
    if ep.state.exists():
        return EpisodeState.model_validate_json(ep.state.read_text(encoding="utf-8"))
    return EpisodeState(slug=ep.slug)


def save_state(ep: EpisodePaths, st: EpisodeState) -> None:
    ep.dir.mkdir(parents=True, exist_ok=True)
    ep.state.write_text(st.model_dump_json(indent=2), encoding="utf-8")


def is_fresh(st: EpisodeState, stage: str, input_hash: str) -> bool:
    s = st.stages.get(stage)
    return bool(s and s.status == "ok" and s.input_hash == input_hash)


def mark(st: EpisodeState, stage: str, status: str, input_hash: str = "", detail: str = "") -> None:
    st.stages[stage] = StageState(
        status=status, input_hash=input_hash, finished_at=datetime.now(UTC), detail=detail
    )


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else obj
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
