---
description: One-request bootstrap — set up the machine, verify auth, create character sheets, and produce the first episode
---
# /start

Goal: from a fresh Windows machine to a scheduled first episode with as little human input as possible.
Stop and ask the user ONLY at the three approval points marked [APPROVAL].

## Phase A — environment (terminal)
1. In the project root run: `powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1`.
   If winget prompts for admin, tell the user to approve the UAC dialog.
2. Run `uv run unumdorlik doctor --probe`. Interpret the table:
   - `claude CLI YO'Q` → stop; tell the user to open a terminal, run `claude`, then `/login`, then retry.
   - `probe:claude_cli` not OK → same as above.
   - `GEMINI_API_KEY YO'Q` → ask the user to paste the key into `.env` (do NOT ask them to paste it in chat), then retry.
   - `character sheet YO'Q` → go to Phase B.
3. Read `.agent/rules/unumdorlik.md` and `docs/03-FORMAT-STANDARTI.md` once.

## Phase B — hosts (browser, once)
4. Follow `/character-sheet`. [APPROVAL] Show Mia's and James's front images; wait for "ok".
5. Confirm `uv run unumdorlik doctor` now shows `character sheet OK`.

## Phase C — first episode
6. `uv run unumdorlik inbox`. If empty, ask the user for a topic in the `topics/inbox/EXAMPLE-topic.md` format
   (or offer to draft one from a source they name) and write it to `topics/inbox/<slug>.md`.
7. `uv run unumdorlik schedule --apply` (assigns the next free 09:00/18:00 Tashkent slot).
8. Follow `/episode <slug>` end to end. Expected pauses: images (`/images-flow`, browser) and the
   [APPROVAL] walkthrough before upload.
9. Publish per `/publish-studio <slug>` (browser) unless the user prefers the API (`uv run unumdorlik upload <slug>`).

## Phase D — hand-off
10. Commit `episodes/<slug>/*.json|*.md|*.srt|thumbnail.png`, `assets/characters/*.png`, `topics/**` and push.
11. Final report: YouTube link + scheduled time, QA summary, what was approved, and the single next command
    for the next episode: "put a new topic file in topics/inbox/ and say `/episode <slug>`".
