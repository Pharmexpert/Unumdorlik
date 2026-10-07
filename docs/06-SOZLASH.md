# 06 — Sozlash: siz bajaradigan 4 qadam (Stack B)

Taxminiy vaqt: 30–40 daqiqa (character sheet'siz 15 daqiqa).

## 1. GEMINI_API_KEY (bepul daraja) — 3 daqiqa

1. https://aistudio.google.com → chapda **Get API key** → **Create API key** (yangi loyiha yoki mavjud).
2. Hisob-kitob (billing) **ulamang** — bepul daraja yetarli: TTS (`gemini-3.8-flash-tts`), `gemini` provider.
   Rasm modeli (`gemini-3.1-flash-image`) bepul darajada yo'q — biz uni ishlatmaymiz (Flow ishlatiladi).
3. Lokal: repo ildizida `.env` yarating:
   ```
   GEMINI_API_KEY=AIza...
   UNUMDORLIK_PROFILE=stack-b
   ```
4. GitHub Actions uchun: repo → **Settings → Secrets and variables → Actions → New repository secret**
   → nomi `GEMINI_API_KEY`. (Yoki terminalda: `gh secret set GEMINI_API_KEY`.)
5. Tekshirish: `uv run unumdorlik doctor` → `GEMINI_API_KEY OK`.

## 2. Mavzu fayli — tayyor

`topics/inbox/why-your-brain-forgets-new-words.md` — birinchi mavzu (Ebbinghaus, Cepeda 2006, Roediger & Karpicke 2006
asosida). Keyingi mavzular uchun `topics/inbox/EXAMPLE-topic.md` ni nusxalang; fayl nomi = `slug`.
Qoidalar: slug faqat `a-z 0-9 -`; mazmun ≥ 30 so'z; `publish_at` bo'sh qolsa `schedule --apply` keyingi bo'sh slotni beradi.

## 3. Claude Code (skript uchun) — 5 daqiqa

**Lokal mashinada:**
```bash
npm install -g @anthropic-ai/claude-code
claude            # birinchi ishga tushirishda brauzer orqali obunangiz bilan kiring
echo "Reply OK" | claude -p --model claude-opus-5-5   # "OK" qaytsa — tayyor
```
**GitHub Actions uchun (obuna bilan, API kalitsiz):**
```bash
claude setup-token     # uzoq muddatli OAuth token chiqaradi (bir marta ko'rsatiladi)
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```
Eslatma: Actions'dagi `claude -p` obuna limitlaridan sarflaydi (kuniga 2 epizod ≈ 4–6 so'rov, muammo emas).
Agar obuna token'ini CI'da ishlatmoqchi bo'lmasangiz: workflow'da `profile: stack-a` + `script.provider: gemini`
(bepul Gemini darajasi) ishlating — kod o'zgarmaydi.

## 4. Character sheet — 15–20 daqiqa (bir marta)

Variant A (tavsiya): Antigravity'da `/character-sheet` — `assets/characters/PROMPTS.md` dagi promptlar bilan Flow'da
8 ta rasm yaratadi, har boshlovchining birinchi rasmini siz tasdiqlaysiz.
Variant B (qo'lda): https://flow.google.com → Image → promptlarni `PROMPTS.md` dan nusxalang → yuklab oling →
`assets/characters/mia_front.png` … `james_full.png` nomlari bilan saqlang.
Tekshirish: `uv run unumdorlik doctor` → `character sheet OK`. Keyin `git add assets/characters && git commit`.

## 5. YouTube (keyinroq, 09-bosqich uchun)

1. https://console.cloud.google.com → yangi loyiha → **YouTube Data API v3** yoqing.
2. **OAuth consent screen** (External, test users: o'zingiz) → **Credentials → OAuth client ID → Desktop app** →
   JSON yuklab oling → `secrets/youtube_client_secret.json`.
3. Lokal: `uv sync --extra youtube && uv run unumdorlik youtube-auth` → brauzerda ruxsat → `secrets/youtube_token.json`.
4. Actions'da yuklash uchun `youtube_token.json` mazmunini `YOUTUBE_TOKEN_JSON` secret qilib qo'ying (workflow'ga
   keyin qo'shiladi). **Audit arizasi**: YouTube API Services → "Audit and Quota Extension Form" — darhol topshiring.

## Birinchi epizod (sozlashdan keyin)

```bash
uv sync --extra llm --extra audio --extra pdf --extra images
uv run unumdorlik doctor
uv run unumdorlik schedule --apply
uv run unumdorlik run why-your-brain-forgets-new-words --from 01 --to 04   # skript, lug'at/PDF, audio, align
uv run unumdorlik run why-your-brain-forgets-new-words --from 05 --to 05   # storyboard → PAUSED: Antigravity /images-flow
uv run unumdorlik images-check why-your-brain-forgets-new-words
uv run unumdorlik run why-your-brain-forgets-new-words --from 06 --to 08   # render, metadata, QA
```
