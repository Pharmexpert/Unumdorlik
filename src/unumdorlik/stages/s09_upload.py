"""09 — YouTube Data API v3 upload (resumable) + thumbnail + captions + publishAt. Writes youtube.json."""

from __future__ import annotations

import json
from datetime import UTC
from pathlib import Path

from ..models import Metadata, QAReport
from ..state import write_json
from .base import StageContext, StageError, StageManual

ID, NAME = "09", "upload"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]


def inputs(ctx: StageContext) -> list[Path]:
    return [ctx.ep.video, ctx.ep.metadata, ctx.ep.qa_report]


def youtube_client(ctx: StageContext):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as e:
        raise StageError("YouTube kutubxonalari yo'q: uv sync --extra youtube") from e
    tok = ctx.root / ctx.cfg.youtube.token_file
    if not tok.exists():
        raise StageError(f"OAuth token yo'q: {tok}. `unumdorlik youtube-auth` ni lokal brauzerli mashinada bajaring")
    creds = Credentials.from_authorized_user_file(str(tok), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def run(ctx: StageContext) -> str:
    qa = QAReport.model_validate_json(ctx.ep.qa_report.read_text(encoding="utf-8"))
    if qa.status != "pass":
        raise StageError("QA pass emas")
    if ctx.cfg.approval.required and not (ctx.ep.dir / "APPROVED").exists():
        raise StageManual(f"Tasdiq kerak: `unumdorlik approve {ctx.ep.slug}` (yoki PR merge) → episodes/{ctx.ep.slug}/APPROVED")
    md = Metadata.model_validate_json(ctx.ep.metadata.read_text(encoding="utf-8"))
    if ctx.ep.youtube.exists():
        prev = json.loads(ctx.ep.youtube.read_text(encoding="utf-8"))
        if prev.get("video_id"):
            return f"allaqachon yuklangan: {prev['video_id']}"

    from googleapiclient.http import MediaFileUpload

    yt = youtube_client(ctx)
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": ctx.cfg.youtube.made_for_kids}
    if md.publish_at:
        status["publishAt"] = md.publish_at.astimezone(UTC).isoformat().replace("+00:00", "Z")
    body = {"snippet": {"title": md.title, "description": md.description, "tags": md.tags,
                        "categoryId": str(md.category_id), "defaultLanguage": md.default_language,
                        "defaultAudioLanguage": md.default_language},
            "status": status}
    media = MediaFileUpload(str(ctx.ep.video), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            ctx.log(f"upload {int(st.progress() * 100)}%")
    vid = resp["id"]
    out = {"video_id": vid, "url": f"https://youtu.be/{vid}", "status": "scheduled" if md.publish_at else "private",
           "publish_at": status.get("publishAt")}
    try:
        if ctx.ep.thumbnail.exists():
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(ctx.ep.thumbnail))).execute()
            out["thumbnail"] = True
        if ctx.cfg.youtube.upload_captions and ctx.ep.subtitles.exists():
            yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English"}},
                                 media_body=MediaFileUpload(str(ctx.ep.subtitles), mimetype="application/octet-stream")).execute()
            out["captions"] = True
        if ctx.cfg.channel.playlist_id:
            yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": ctx.cfg.channel.playlist_id,
                                      "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
    except Exception as e:  # video is up; extras are best-effort
        out["warning"] = str(e)[:300]
    write_json(ctx.ep.youtube, out)
    return f"{out['url']} ({out['status']})"
