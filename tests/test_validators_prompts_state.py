from pathlib import Path

from unumdorlik.models import Script
from unumdorlik.prompts import fill, load_prompt, split_prompt
from unumdorlik.state import hash_paths
from unumdorlik.validators import validate_script


def test_valid_script_passes(script: Script):
    assert validate_script(script, script.count_words()) == []


def test_missing_block_and_vocab(script: Script):
    sc = script.model_copy(deep=True)
    sc.turns = [t for t in sc.turns if t.section != "STORY"]
    sc.vocabulary[0].word = "nonexistentword"
    errs = validate_script(sc, sc.count_words())
    assert any("STORY" in e for e in errs)
    assert any("nonexistentword" in e for e in errs)


def test_word_count_tolerance(script: Script):
    errs = validate_script(script, int(script.count_words() * 1.5))
    assert any("word_count" in e for e in errs)


def test_prompt_split_and_fill(repo: Path):
    system, user = load_prompt(repo, "01_dialogue_script.md", {
        "HOST_A_NAME": "Mia", "HOST_B_NAME": "James", "LEVEL": "A2", "TARGET_WORDS": 2500, "WPM": 140,
        "N": 4, "VOCAB_N": 10, "TOPIC_FILE_CONTENT": "topic"})
    assert "Mia" in system and "{{" not in system and "{{" not in user
    assert "topic" in user


def test_fill_strict_raises():
    import pytest

    with pytest.raises(KeyError):
        fill("hello {{X}}", {})
    assert fill("hello {{X}}", {}, strict=False) == "hello {{X}}"


def test_split_prompt_without_sections():
    s, u = split_prompt("just text")
    assert s == "" and u == "just text"


def test_hash_changes_with_content(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("1")
    h1 = hash_paths(f)
    f.write_text("2")
    assert hash_paths(f) != h1
    assert hash_paths(tmp_path / "missing") == hash_paths(tmp_path / "missing")
