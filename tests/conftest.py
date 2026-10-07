from pathlib import Path

import pytest

from unumdorlik.models import Script, SectionInfo, Turn, VocabItem


def make_script(words_per_turn: int = 40, n_sections: int = 4) -> Script:
    turns, i = [], 0

    def add(section, speaker, text, slow=False):
        nonlocal i
        i += 1
        turns.append(Turn(i=i, section=section, speaker=speaker, text=text, slow=slow))

    filler = " ".join(["word"] * words_per_turn)
    add("HOOK", "A", "Did you know some learners freeze when they speak? " + filler)
    add("INTRO", "B", "Welcome back, I'm James. " + filler)
    add("CTA", "A", "Please subscribe and share. " + filler)
    for s in range(1, n_sections + 1):
        for k in range(6):  # noqa: B007
            add(f"SECTION_{s}", "A" if k % 2 == 0 else "B",
                'For example, "I want to sleep because I am tired" is a formula. ' + filler)
    add("STORY", "B", "Last year at the airport I froze completely. " + filler)
    for k in range(8):
        add("PRACTICE", "A" if k % 2 == 0 else "B", "I want to visit Korea because I love the food. " + filler)
    for _ in range(5):
        add("SHADOWING", "A", "I want to learn English.", slow=True)
    add("RECAP", "A", "Four formulas, hundreds of sentences. " + filler)
    add("VOCABULARY", "B", "Formula: a fixed pattern. Confident: feeling sure. " + filler)
    add("CHALLENGE", "A", "Write one sentence in the comments. " + filler)
    add("OUTRO", "B", "See you tomorrow. Bye. " + filler)
    vocab = [VocabItem(word=w, cefr="B1", definition="d", example=ex) for w, ex in [
        ("formula", "Formula: a fixed pattern."), ("confident", "Confident: feeling sure."),
        ("freeze", "Did you know some learners freeze when they speak?"), ("airport", "Last year at the airport I froze completely."),
        ("subscribe", "Please subscribe and share."), ("sentence", "Write one sentence in the comments."),
        ("pattern", "Formula: a fixed pattern."), ("tomorrow", "See you tomorrow."),
        ("learners", "some learners freeze"), ("comments", "in the comments")]]
    return Script(slug="test-ep", title="Test Episode: One Formula", hosts={"A": "Mia", "B": "James"},
                  sections=[SectionInfo(id=f"SECTION_{s}", title=f"Formula {s}") for s in range(1, n_sections + 1)],
                  turns=turns, vocabulary=vocab, challenge="Write one sentence.", hook_line="Did you know?")


@pytest.fixture
def script() -> Script:
    return make_script()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch) -> Path:
    """A minimal repo layout (prompts + profiles copied from the real repo)."""
    import shutil

    real = Path(__file__).resolve().parents[1]
    (tmp_path / "topics" / "inbox").mkdir(parents=True)
    (tmp_path / "episodes").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    shutil.copytree(real / "prompts", tmp_path / "prompts")
    shutil.copytree(real / "config", tmp_path / "config")
    monkeypatch.setenv("UNUMDORLIK_ROOT", str(tmp_path))
    return tmp_path
