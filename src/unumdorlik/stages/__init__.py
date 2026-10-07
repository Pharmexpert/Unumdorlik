"""Stage registry. Each stage: id ("01".."09"), name, inputs(ctx) -> list[Path], run(ctx) -> detail str."""

from __future__ import annotations

from . import (
    s01_script,
    s02_glossary,
    s03_tts,
    s04_align,
    s05_images,
    s06_render,
    s07_metadata,
    s08_qa,
    s09_upload,
)
from .base import StageContext, StageError, StageManual

STAGES = {
    "01": s01_script,
    "02": s02_glossary,
    "03": s03_tts,
    "04": s04_align,
    "05": s05_images,
    "06": s06_render,
    "07": s07_metadata,
    "08": s08_qa,
    "09": s09_upload,
}
ORDER = list(STAGES)

__all__ = ["ORDER", "STAGES", "StageContext", "StageError", "StageManual"]
