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

## 3. Claude Code (skript uchun) — batafsil, 10–15 daqiqa

Maqsad: (a) kompyuteringizda `claude -p` obunangiz bilan ishlashi, (b) GitHub Actions'da ham API kalitsiz,
obuna orqali ishlashi. Manba: code.claude.com/docs (setup, authentication, headless, cli-reference).

### 3.1. O'rnatish

| OS | Buyruq |
|---|---|
| macOS / Linux | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Windows PowerShell | `irm https://claude.ai/install.ps1 \| iex` |
| Windows CMD | `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd` |
| Muqobil (npm, Node ≥ 22) | `npm install -g @anthropic-ai/claude-code` |

Tekshirish: `claude --version` (masalan `2.1.x`).

### 3.2. Obuna bilan kirish

1. Terminalda `claude` deb yozing → brauzer ochiladi → Claude Pro/Max akkauntingiz bilan kiring.
2. Claude ichida `/status` yozing. Kutilgan: **Login method: claude.ai** va emailingiz.
   Agar **Login method: API key** chiqsa — muhitda `ANTHROPIC_API_KEY` bor va u obunadan **ustun** turadi
   (API hisobidan pul sarflaydi). Yechim: `unset ANTHROPIC_API_KEY` (Windows: `Remove-Item Env:ANTHROPIC_API_KEY`),
   `.env`/profil fayllaridan olib tashlang, `/status` bilan qayta tekshiring.
3. Chiqish: `/exit`.

Kredensiallar: macOS — Keychain; Linux — `~/.claude/.credentials.json` (0600); Windows — `%USERPROFILE%\.claude\.credentials.json`.
Chiqib ketish: `claude` ichida `/logout`. "Your login expires in 3 days" chiqsa — `/login`.

### 3.3. Headless (`-p`) test — liniya aynan shu rejimda ishlaydi

```bash
echo "Reply with the single word OK" | claude -p --output-format text --model claude-opus-5-5 --tools "" --max-turns 1
```
Kutilgan chiqish: `OK`. Shu bilan bir xil buyruqni `unumdorlik` 01-bosqichda chaqiradi (`src/unumdorlik/llm.py`):
`--tools ""` — vositalarsiz, faqat matn; `--max-turns 1` — bitta javob; prompt stdin orqali (10 MB gacha).
`--model` qiymatlari: `opus`, `sonnet`, `haiku` yoki to'liq ID (`claude-opus-5-5`, `claude-sonnet-5-5`).

Liniya orqali tekshirish (ikkalasini bir vaqtda):
```bash
uv run unumdorlik doctor --probe      # probe:claude_cli OK  (va GEMINI_API_KEY bo'lsa probe:gemini OK)
```

Limitlar: `-p` rejimi **obuna kvotasidan** sarflaydi. Ikki xil limit bor: sessiya limiti (bir necha soatda tiklanadi)
va haftalik limit; Opus va Sonnet uchun alohida "chelaklar". Opus limiti tugasa, Sonnet'ga o'tish ishlaydi:
`config/pipeline.yaml` → `script.model: claude-sonnet-5-5`. Kuniga 2 epizod ≈ 4–6 so'rov (skript, lug'at,
storyboard, metadata) — Pro uchun ham yetarli; Opus'da 1 skript ≈ 8 daqiqa.

### 3.4. GitHub Actions uchun token (`claude setup-token`)

`setup-token` — obuna uchun bir yillik OAuth token chiqaradi (Pro, Max, Team, Enterprise). CLI uni
`CLAUDE_CODE_OAUTH_TOKEN` o'zgaruvchisidan o'qiydi; token faqat model so'rovlari uchun ishlaydi.

```bash
claude setup-token        # brauzer ochiladi → tasdiqlang → terminalda token bir marta ko'rsatiladi (saqlanmaydi!)
```
Tokenni nusxalab GitHub'ga qo'ying — **faqat shu ikki usuldan biri**, chatga yoki faylga yozmang:
- Veb: repo → Settings → Secrets and variables → Actions → New repository secret → Name `CLAUDE_CODE_OAUTH_TOKEN`.
- Terminal (gh CLI bo'lsa): `gh secret set CLAUDE_CODE_OAUTH_TOKEN` → tokenni yopishtiring → Enter.

Workflow (`.github/workflows/pipeline.yml`) tokenni `env` orqali beradi va `npm i -g @anthropic-ai/claude-code`
o'rnatadi — qo'shimcha sozlash kerak emas. **Muhim:** `ANTHROPIC_API_KEY` secret'ini **qo'ymang** (yoki bo'sh qoldiring);
u bo'lsa CLI obuna tokenini emas, API kalitni ishlatadi va pul sarflaydi.

Tekshirish: Actions → **pipeline** → Run workflow → `slug` bo'sh, `to` = `01` → logda
`01 script ok — ~2500 so'z` chiqsa tayyor (yoki `doctor` qadamida `claude CLI OK`).

Xavfsizlik: token 1 yil amal qiladi, hujjatlarda bekor qilish buyrug'i yo'q — sizib chiqsa `/logout` qilib
qayta `setup-token` oling va secret'ni yangilang. Token hech qachon repoga, `.env.example`ga yoki chatga tushmasin.

### 3.5. Muammolar

| Belgi | Sabab | Yechim |
|---|---|---|
| `claude: command not found` | PATH | terminalni qayta oching; npm bo'lsa `npm bin -g` ni PATH'ga qo'shing |
| `Not logged in · Please run /login` | `-p` ishlatishdan oldin interaktiv kirish qilinmagan | `claude` → `/login` → brauzer → claude.ai akkaunt → `/status` → `/exit`, so'ng testni qayta bajaring |
| npm: `allow-scripts ... postinstall: node install.cjs` (Windows) | npm o'rnatish skriptlarini bloklagan | `npm install -g --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code` yoki native: `irm https://claude.ai/install.ps1 \| iex` |
| Windows: "PowerShell (x86)" / `C:\windows\system32` dan ishlash | 32-bit konsol, admin katalog | oddiy 64-bit "Windows PowerShell" yoki "Terminal"ni oching, `cd ~` qiling; loyiha ham shu yerda klonlanadi |
| `/status` → API key | `ANTHROPIC_API_KEY` o'rnatilgan | o'zgaruvchini olib tashlang |
| `-p` javob bermaydi / login so'raydi | kirilmagan | `claude` → brauzerda kiring |
| Actions'da `claude -p` 401/"not logged in" | secret yo'q yoki nomi xato | `CLAUDE_CODE_OAUTH_TOKEN` nomini tekshiring |
| "You've hit your Opus limit" | sessiya/haftalik limit | `script.model: claude-sonnet-5-5` yoki kuting |
| `claude -p` ishlaydi, lekin JSON emas | model izoh qo'shgan | liniya 1 marta "faqat JSON" deb qayta so'raydi; 2-xatoda bosqich FAILED — logni yuboring |

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
