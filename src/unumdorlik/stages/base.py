from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..config import PipelineConfig
from ..paths import EpisodePaths
from ..topics import Topic


class StageError(RuntimeError):
    """Stage failed; pipeline stops."""


class StageManual(RuntimeError):
    """Stage needs a human / browser-agent step; pipeline pauses with instructions."""


@dataclass
class StageContext:
    cfg: PipelineConfig
    ep: EpisodePaths
    topic: Topic
    root: Path
    force: bool = False

    def log(self, msg: str) -> None:
        from rich import print as rprint

        rprint(f"[dim]{self.ep.slug}[/dim] {msg}")


def run_cmd(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise StageError(f"{cmd[0]} xato: {proc.stderr[-800:]}")
    return proc


def require_bin(name: str) -> str:
    exe = shutil.which(name)
    if not exe:
        raise StageError(f"`{name}` topilmadi (PATH)")
    return exe


def ffprobe_duration(path: Path) -> float:
    exe = require_bin("ffprobe")
    out = run_cmd([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.stdout.strip())
