"""End-to-end offline run: manual LLM provider, synthetic audio, placeholder images, 360p render."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import make_script

from unumdorlik.config import load_config
from unumdorlik.paths import EpisodePaths
from unumdorlik.runner import PipelinePaused, run_episode
from unumdorlik.stages import StageError
from unumdorlik.state import write_json

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg kerak")


def _profile(repo: Path) -> Path:
    data = yaml.safe_load((repo / "config" / "profiles" / "stack-a.yaml").read_text())
    data["script"]["provider"] = "manual"
    data["visuals"]["engine"] = "manual"
    data["visuals"]["seconds_per_image"] = 60
    data["render"].update({"width": 640, "height": 360, "fps": 12, "crf": 30})
    data["approval"]["required"] = False
    p = repo / "config" / "pipeline.yaml"
    p.write_text(yaml.safe_dump(data))
    return p


def test_offline_pipeline(repo: Path):
    cfg = load_config(_profile(repo))
    slug = "test-ep"
    (repo / "topics" / "inbox" / f"{slug}.md").write_text(
        "---\nslug: test-ep\nlevel: A2\n---\n" + "mazmun " * 50, encoding="utf-8")
    ep = EpisodePaths(slug, repo)

    # 01 manual -> paused with prompt file
    with pytest.raises(PipelinePaused):
        run_episode(cfg, repo, slug, "01", "01")
    assert (ep.dir / "prompt_01.md").exists()

    # human/agent provides script.json
    sc = make_script(words_per_turn=12)
    write_json(ep.script, sc)
    res = run_episode(cfg, repo, slug, "02", "02")
    assert "so'z" in res["02"]
    assert (ep.dir / "transcript.md").exists()

    # 03: synthesize a fake 8.5-minute dialogue (sine) instead of TTS
    ep.audio_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=510",
                    "-ar", "24000", "-ac", "1", str(ep.audio)], check=True)
    res = run_episode(cfg, repo, slug, "04", "04")
    assert "estimate" in res["04"]
    al = json.loads(ep.alignment.read_text())
    assert abs(al["turns"][-1]["end"] - 510) < 0.5

    # 05 manual -> paused with TODO list, storyboard exists
    with pytest.raises(PipelinePaused):
        run_episode(cfg, repo, slug, "05", "05")
    sb = json.loads(ep.storyboard.read_text())
    assert 6 <= len(sb["shots"]) <= 12
    assert (ep.images_dir / "TODO.md").exists()

    # 06 render with placeholders, 07 metadata fallback
    res = run_episode(cfg, repo, slug, "06", "07")
    assert ep.video.exists() and ep.subtitles.exists() and ep.metadata.exists()
    md = json.loads(ep.metadata.read_text())
    assert md["chapters"][0]["time"] == "0:00" and len(md["chapters"]) >= 3
    assert len(md["tags"]) <= cfg.youtube.tags_max

    # 08 QA must fail because of placeholder images, report written
    with pytest.raises(StageError):
        run_episode(cfg, repo, slug, "08", "08")
    qa = json.loads(ep.qa_report.read_text())
    assert qa["status"] == "fail"
    assert any(c["name"] == "no_placeholder_images" and not c["ok"] for c in qa["checks"])

    # idempotency: rerunning 06 is skipped
    res = run_episode(cfg, repo, slug, "06", "06")
    assert res["06"] == "fresh (skip)"
