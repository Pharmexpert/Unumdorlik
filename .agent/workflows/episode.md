---
description: Produce a full episode from topics/inbox/<slug>.md (code stages via CLI, browser stages via sub-agent)
---
# /episode <slug>

1. Confirm `topics/inbox/<slug>.md` exists and has valid frontmatter. If not, stop.
2. Run `uv run unumdorlik run <slug> --from 01 --to 04` (script → glossary/PDF → TTS → alignment).
   On validation failure, read the error, fix the topic file or rerun once, then stop if it fails again.
3. Run `uv run unumdorlik storyboard <slug>` to produce `episodes/<slug>/storyboard.json`.
4. Images: follow `/images-flow <slug>` (browser). If Flow is unavailable, run
   `uv run unumdorlik images <slug> --engine gemini_image` (requires billing) or ask the user.
5. Run `uv run unumdorlik run <slug> --from 06 --to 08` (render → metadata/thumbnail → QA).
6. Produce a walkthrough (3 images, thumbnail, title, description, QA report) and WAIT for approval.
7. After approval: `/publish-studio <slug>` (browser) or `uv run unumdorlik upload <slug>` (Data API).
8. Move `topics/inbox/<slug>.md` to `topics/done/`, commit `episodes/<slug>/*.json|*.pdf|*.srt|*.png`
   (media files are git-ignored), and report the YouTube link.
