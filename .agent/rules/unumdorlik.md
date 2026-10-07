# Unumdorlik — agent rules (workspace)

You are operating the "Unumdorlik" podcast-video production line. Read `docs/01-REJA.md`
and `docs/03-FORMAT-STANDARTI.md` once per session before any episode work.

## Division of labour
- Deterministic stages run through the CLI: `uv run unumdorlik run <slug> --from NN --to NN`.
  Never re-implement a stage in chat; if the CLI is missing a feature, stop and report.
- Use the browser sub-agent ONLY for: flow.google.com (images, intro video),
  notebooklm.google.com (optional audio B), studio.youtube.com (upload/schedule),
  aistudio.google.com (fallback image generation).
- Every artifact goes to `episodes/<slug>/` with the exact file names in `docs/01-REJA.md` §2.

## Content rules
- Follow the episode structure in `docs/03-FORMAT-STANDARTI.md` exactly (HOOK … OUTRO).
- Hosts, voices and visual style come from `config/pipeline.yaml`; never change them ad hoc.
- Images: 16:9, Pixar/3D style block from `prompts/03_storyboard_pixar.md`, no readable text in images.
- Stay inside the facts of the topic file; no invented statistics or citations.

## Browser safety
- Never enter passwords, payment details, or accept purchases/subscriptions. If a page asks, stop and report.
- Never change channel settings, delete videos, or post comments. Upload/schedule only.
- Default YouTube visibility: `Scheduled` at the `publish_at` from the topic file; if absent, `Private`.
- Download generated media to `episodes/<slug>/images/` or `episodes/<slug>/audio/`, then verify file count.

## Finishing
- Run `uv run unumdorlik qa <slug>` and include its report in the walkthrough.
- Walkthrough must show: 3 sample images, thumbnail, 30 s audio snippet path, metadata title/description, QA result.
- Do not mark the task complete until `episodes/<slug>/state.json` shows every stage `ok`.
