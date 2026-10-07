"""`unumdorlik` command-line interface."""

from __future__ import annotations

import os
import shutil
import sys
from datetime import UTC, datetime

import typer
from dotenv import load_dotenv
from rich import print as rprint
from rich.table import Table

from . import __version__
from .config import config_path, load_config
from .paths import EpisodePaths, repo_root
from .state import load_state

app = typer.Typer(help="Unumdorlik — AI podcast-video production line", no_args_is_help=True)
_profile_opt = typer.Option(None, "--profile", "-p", help="stack-a | stack-b | path to yaml (default: config/pipeline.yaml)")


def _cfg(profile: str | None):
    root = repo_root()
    load_dotenv(root / ".env")
    path = config_path(root, profile)
    return load_config(path), root, path


@app.callback()
def _main() -> None:
    pass


@app.command()
def version() -> None:
    rprint(__version__)


@app.command()
def doctor(profile: str | None = _profile_opt,
           probe: bool = typer.Option(False, help="claude -p va Gemini API'ga haqiqiy test so'rov yuboradi")) -> None:
    """Check binaries, keys, optional packages and the active profile."""
    cfg, root, path = _cfg(profile)
    t = Table(title=f"doctor — profil: {path.relative_to(root)}")
    t.add_column("tekshiruv")
    t.add_column("holat")
    t.add_column("izoh")

    def row(name: str, ok: bool | None, note: str = "") -> None:
        mark = "[green]OK[/green]" if ok else ("[yellow]—[/yellow]" if ok is None else "[red]YO'Q[/red]")
        t.add_row(name, mark, note)

    for b in ("ffmpeg", "ffprobe"):
        row(b, bool(shutil.which(b)))
    row("claude CLI", bool(shutil.which("claude")), "script.provider=claude_cli uchun")
    row("GEMINI_API_KEY", bool(os.environ.get("GEMINI_API_KEY")), "gemini_tts / gemini provider / gemini_image")
    row("ANTHROPIC_API_KEY", bool(os.environ.get("ANTHROPIC_API_KEY")) or None, "faqat provider=anthropic")
    for mod, extra in (("google.genai", "llm"), ("anthropic", "llm"), ("edge_tts", "audio"), ("reportlab", "pdf"),
                       ("whisperx", "align"), ("googleapiclient", "youtube"), ("PIL", "images")):
        try:
            __import__(mod)
            row(f"py:{mod}", True)
        except Exception:
            row(f"py:{mod}", None, f"uv sync --extra {extra}")
    row("YouTube token", (root / cfg.youtube.token_file).exists(), cfg.youtube.token_file)
    row("character sheet", any((root / cfg.hosts.character_sheet_dir).glob("*.png")), cfg.hosts.character_sheet_dir)
    row("CEFR wordlist", (root / cfg.script.cefr_wordlist).exists(), cfg.script.cefr_wordlist)
    if probe:
        from .llm import LLMError, complete

        for prov in {cfg.script.provider, "gemini"} & {"claude_cli", "gemini"}:
            try:
                r = complete(prov, "", "Reply with the single word OK", cfg.script.model if prov == "claude_cli" else None, timeout=180)
                row(f"probe:{prov}", "OK" in r.text.upper(), f"{r.model} → {r.text.strip()[:40]!r}")
            except LLMError as e:
                row(f"probe:{prov}", False, str(e)[:90])
    if os.environ.get("ANTHROPIC_API_KEY") and cfg.script.provider == "claude_cli":
        row("ANTHROPIC_API_KEY + claude_cli", False, "claude -p obuna o'rniga API kalitni ishlatadi (pullik!) — kalitni olib tashlang")
    rprint(t)
    rprint(f"engines: script={cfg.script.provider} audio={cfg.audio.engine} align={cfg.alignment.engine} "
           f"visuals={cfg.visuals.engine} publish_times={cfg.channel.publish_times} tz={cfg.channel.timezone}")


@app.command()
def inbox(profile: str | None = _profile_opt) -> None:
    """List and validate topics in topics/inbox/."""
    from .topics import TopicError, list_inbox, parse_topic

    _, root, _ = _cfg(profile)
    files = list_inbox(root)
    if not files:
        rprint("[yellow]topics/inbox bo'sh[/yellow]")
        return
    for f in files:
        try:
            tp = parse_topic(f)
            st = load_state(EpisodePaths(tp.slug, root))
            done = [k for k, v in st.stages.items() if v.status == "ok"]
            rprint(f"[green]✓[/green] {tp.slug}  publish_at={tp.publish_at or '-'}  stages_ok={done}")
        except TopicError as e:
            rprint(f"[red]✗[/red] {e}")


@app.command("next-slot")
def next_slot_cmd(profile: str | None = _profile_opt, count: int = 1) -> None:
    """Show the next free publish slot(s) (2/day by default)."""
    from .topics import next_slot, scheduled_times

    cfg, root, _ = _cfg(profile)
    taken = scheduled_times(root)
    now = datetime.now(UTC)
    for _ in range(count):
        s = next_slot(now, cfg.channel.publish_times, taken, cfg.channel.timezone)
        taken.add(s)
        rprint(s.isoformat())


@app.command()
def run(slug: str, profile: str | None = _profile_opt,
        start: str = typer.Option("01", "--from"), stop: str = typer.Option("09", "--to"),
        force: bool = False, only: str | None = typer.Option(None, help="masalan 03,04")) -> None:
    """Run stages --from .. --to for one episode (idempotent)."""
    from .runner import PipelinePaused, run_episode
    from .stages import StageError

    cfg, root, _ = _cfg(profile)
    try:
        run_episode(cfg, root, slug, start, stop, force, only.split(",") if only else None)
    except PipelinePaused as e:
        rprint(f"[yellow]PAUSED[/yellow] {e}")
        raise typer.Exit(3) from None
    except StageError as e:
        rprint(f"[red]FAILED[/red] {e}")
        raise typer.Exit(1) from None


@app.command()
def status(slug: str | None = None, profile: str | None = _profile_opt) -> None:
    """Stage status for one or all episodes."""
    from .stages import ORDER, STAGES

    _, root, _ = _cfg(profile)
    slugs = [slug] if slug else sorted(p.name for p in (root / "episodes").glob("*") if (p / "state.json").exists())
    t = Table(title="episodes")
    t.add_column("slug")
    for s in ORDER:
        t.add_column(f"{s} {STAGES[s].NAME}")
    t.add_column("publish_at")
    icons = {"ok": "[green]✓[/green]", "failed": "[red]✗[/red]", "manual": "[yellow]✋[/yellow]", "pending": "·", "skipped": "-"}
    for sl in slugs:
        st = load_state(EpisodePaths(sl, root))
        t.add_row(sl, *[icons[st.stages[s].status] if s in st.stages else "·" for s in ORDER], str(st.publish_at or "-"))
    rprint(t)


@app.command()
def storyboard(slug: str, profile: str | None = _profile_opt, force: bool = False) -> None:
    """(Re)generate storyboard.json only (no images)."""
    from .runner import episode_topic
    from .stages import StageContext
    from .stages.s05_images import make_storyboard

    cfg, root, _ = _cfg(profile)
    topic = episode_topic(root, slug)
    ctx = StageContext(cfg, EpisodePaths(slug, root), topic, root, force)
    sb = make_storyboard(ctx)
    rprint(f"{len(sb.shots)} kadr → {ctx.ep.storyboard}")


@app.command("images-check")
def images_check(slug: str, profile: str | None = _profile_opt) -> None:
    """Verify every storyboard shot has an image file."""
    from .models import Storyboard
    from .runner import episode_topic
    from .stages import StageContext
    from .stages.s05_images import missing_shots, write_todo

    cfg, root, _ = _cfg(profile)
    ctx = StageContext(cfg, EpisodePaths(slug, root), episode_topic(root, slug), root)
    sb = Storyboard.model_validate_json(ctx.ep.storyboard.read_text(encoding="utf-8"))
    missing = missing_shots(ctx, sb)
    if missing:
        rprint(f"[yellow]{len(missing)}/{len(sb.shots)} kadr yo'q[/yellow] → {write_todo(ctx, sb, missing)}")
        raise typer.Exit(2)
    rprint(f"[green]{len(sb.shots)}/{len(sb.shots)} kadr mavjud[/green]")


@app.command()
def qa(slug: str, profile: str | None = _profile_opt) -> None:
    """Run the QA gate only."""
    run(slug, profile, "08", "08", True, None)


@app.command()
def approve(slug: str, profile: str | None = _profile_opt) -> None:
    """Mark an episode approved for upload (creates episodes/<slug>/APPROVED)."""
    _, root, _ = _cfg(profile)
    ep = EpisodePaths(slug, root)
    ep.ensure()
    (ep.dir / "APPROVED").write_text(datetime.now(UTC).isoformat(), encoding="utf-8")
    rprint(f"[green]approved[/green] {slug}")


@app.command()
def upload(slug: str, profile: str | None = _profile_opt) -> None:
    """Upload to YouTube (stage 09)."""
    run(slug, profile, "09", "09", True, None)


@app.command("youtube-auth")
def youtube_auth(profile: str | None = _profile_opt) -> None:
    """One-time OAuth (needs a browser): writes the token file used by stage 09."""
    from .stages.s09_upload import SCOPES

    cfg, root, _ = _cfg(profile)
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        rprint("[red]uv sync --extra youtube[/red]")
        raise typer.Exit(1) from None
    secrets = root / cfg.youtube.client_secrets
    if not secrets.exists():
        rprint(f"[red]client secret yo'q: {secrets}[/red]")
        raise typer.Exit(1)
    flow = InstalledAppFlow.from_client_secrets_file(str(secrets), SCOPES)
    creds = flow.run_local_server(port=0)
    tok = root / cfg.youtube.token_file
    tok.parent.mkdir(parents=True, exist_ok=True)
    tok.write_text(creds.to_json(), encoding="utf-8")
    rprint(f"[green]token yozildi[/green] {tok}")


@app.command()
def schedule(profile: str | None = _profile_opt, apply: bool = False) -> None:
    """Assign the next free slots (2/day) to inbox topics without publish_at. --apply writes state.json."""
    from .state import save_state
    from .topics import list_inbox, next_slot, parse_topic, scheduled_times

    cfg, root, _ = _cfg(profile)
    taken = scheduled_times(root)
    now = datetime.now(UTC)
    for f in list_inbox(root):
        tp = parse_topic(f)
        ep = EpisodePaths(tp.slug, root)
        st = load_state(ep)
        if st.publish_at or tp.publish_at:
            continue
        slot = next_slot(now, cfg.channel.publish_times, taken, cfg.channel.timezone)
        taken.add(slot)
        rprint(f"{tp.slug} → {slot.isoformat()}")
        if apply:
            st.publish_at = slot
            save_state(ep, st)


@app.command()
def process(profile: str | None = _profile_opt, limit: int = 2, stop: str = typer.Option("08", "--to")) -> None:
    """Process up to --limit inbox topics (default 2/day) through --to; used by GitHub Actions."""
    from .runner import PipelinePaused, run_episode
    from .stages import StageError
    from .topics import list_inbox, parse_topic

    cfg, root, _ = _cfg(profile)
    n, failures = 0, 0
    for f in list_inbox(root):
        if n >= limit:
            break
        tp = parse_topic(f)
        st = load_state(EpisodePaths(tp.slug, root))
        if st.stages.get(stop) and st.stages[stop].status == "ok":
            continue
        n += 1
        try:
            run_episode(cfg, root, tp.slug, "01", stop)
        except PipelinePaused as e:
            rprint(f"[yellow]PAUSED[/yellow] {e}")
        except StageError as e:
            failures += 1
            rprint(f"[red]FAILED[/red] {tp.slug}: {e}")
    if failures:
        raise typer.Exit(1)


if __name__ == "__main__":
    sys.exit(app())
