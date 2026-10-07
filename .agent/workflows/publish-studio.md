---
description: Upload a finished episode to YouTube via YouTube Studio in the browser and schedule it
---
# /publish-studio <slug>

Precondition: `episodes/<slug>/qa_report.json` has `"status": "pass"` and the user approved.

1. Read `episodes/<slug>/metadata.json` (title, description, tags, chapters, pinned_comment, publish_at).
2. Open https://studio.youtube.com → Create → Upload videos → select `episodes/<slug>/render/video.mp4`.
3. Details: title, description (verbatim, chapters included), thumbnail `episodes/<slug>/thumbnail.png`,
   playlist from config, audience "No, it's not made for kids", tags, language English,
   category Education, altered content: "Yes" for synthetic voice/visuals if the form asks.
4. Video elements: upload subtitles `episodes/<slug>/subtitles.srt` (English).
5. Visibility: "Schedule" at `publish_at` (channel timezone); if missing, "Private".
6. Wait for processing checks; copy the video link into `episodes/<slug>/youtube.json`
   (`{"video_id": "...", "status": "scheduled", "publish_at": "..."}`).
7. Do NOT publish immediately, do not post comments, do not change any channel setting.
