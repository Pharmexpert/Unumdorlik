---
description: Create the two hosts' Pixar-style character sheets in Google Flow and save them to assets/characters/
---
# /character-sheet

1. Read `assets/characters/PROMPTS.md`.
2. Open https://flow.google.com (browser sub-agent), project "Unumdorlik", Image mode, aspect ratio 1:1.
3. Generate `mia_front` (STYLE + Mia base + row prompt). Show the best candidate and WAIT for the user's approval.
4. Add the approved image as an ingredient; generate `mia_34`, `mia_profile`, `mia_full` with it attached.
5. Repeat steps 3–4 for James.
6. Download all 8 files with the exact names into `assets/characters/`.
7. Run `uv run unumdorlik doctor` and confirm "character sheet OK". Report which images were approved.
