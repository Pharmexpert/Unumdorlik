---
description: Generate storyboard images in Google Flow (free image generation) and download them
---
# /images-flow <slug>

Input: `episodes/<slug>/storyboard.json` (array `shots`, each with `id`, `prompt`, `shot_type`).

1. Open https://flow.google.com in the browser sub-agent; open or create project "Unumdorlik".
2. Once per project: upload host reference images from `assets/characters/` as ingredients
   (skip if they already exist in the project).
3. For each shot, in order:
   - Select "Image" generation, aspect ratio 16:9.
   - If `shot_type` includes a host, attach the matching host ingredient(s).
   - Paste `prompt` verbatim; generate; pick the best of the results (faces consistent, no text).
   - Download to `episodes/<slug>/images/shot_<id>.png` (zero-padded id).
   - If generation is refused, soften the prompt (remove brand/people words) and retry once.
4. Verify: file count equals number of shots; run `uv run unumdorlik images-check <slug>`.
5. Report the count, any skipped shots, and credits used (images should use none).
