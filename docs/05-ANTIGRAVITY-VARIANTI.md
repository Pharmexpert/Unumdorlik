# 05 — Google Antigravity orqali amalga oshirish varianti

Antigravity — Google'ning agentli IDE'si (Gemini 3 Pro va boshqa modellar, bepul "Individual" daraja).
Bizning liniya uchun uning uchta xususiyati hal qiluvchi:

1. **Brauzer sub-agenti** (Chrome kengaytmasi orqali): flow.google.com, notebooklm.google.com,
   aistudio.google.com va studio.youtube.com kabi **API bermaydigan** veb-ilovalarni odam kabi
   boshqaradi — bu Flow va NotebookLM'ni bepul va rasmiy sahifa orqali ishlatish imkonini beradi.
2. **Rasm generatsiyasi** (Nano Banana) IDE ichida agent vositasi sifatida — kvota doirasida.
3. **Agent Manager + artefaktlar**: vazifa ro'yxati, reja, "walkthrough", brauzer yozuvlari —
   tasdiq uchun qulay; `.agent/rules`, `.agent/workflows`, `.agents/mcp_config.json` bilan
   loyiha darajasida sozlanadi.

Cheklovlar (2026-10): bepul daraja agent so'rovlari soni kunlik/haftalik kvota bilan cheklangan
(manbalar 20 so'rov/kun, 5 soatda yangilanish deb yozadi; o'zgarib turadi); **rejalashtirilgan
(cron) ishga tushirish yo'q** — agent qo'lda yoki Antigravity CLI orqali tashqi cron bilan
chaqiriladi; brauzer-agent **sizning kompyuteringizda** ishlaydi (bulut runner'da emas).

## 1. Arxitektura: Antigravity = "qo'l-oyoq", Python CLI = "skelet"

```
 siz: "/episode <slug>"  ──►  Antigravity Agent Manager
                                   │
            ┌──────────────────────┼─────────────────────────┐
            ▼                      ▼                         ▼
   terminal: `unumdorlik run`   brauzer-agent              rasm vositasi
   (skript, lug'at, PDF,         (Flow rasm/Veo intro,      (Nano Banana,
    TTS, align, render,           NotebookLM audio,          storyboard kadrlari)
    metadata, QA)                 YouTube Studio upload)
            │                      │                         │
            └──────────► episodes/<slug>/ (artefaktlar) ◄────┘
                                   │
                        walkthrough + PR → siz tasdiqlaysiz
```

Qoida: **determinik ishlar kodda** (`unumdorlik` CLI), **faqat brauzer talab qiladigan ishlar
agentda**. Shunda agent kvotasi tejaladi (1 epizod ≈ 3–5 agent so'rovi) va natija takrorlanadi.

## 2. Bosqichlarni Antigravity'da taqsimlash

| Bosqich | Kim bajaradi | Qanday |
|---|---|---|
| 01 Skript | Antigravity agent (Gemini 3 Pro) **yoki** CLI (Gemini bepul API) | Workflow `/episode` ichida `prompts/01_dialogue_script.md` ni o'qib `script.json` yozadi; validator CLI'da |
| 02 Lug'at/PDF | CLI | `unumdorlik run <slug> --from 02 --to 02` |
| 03 Audio A | CLI | Gemini TTS bepul darajasi / edge-tts |
| 03 Audio B | brauzer-agent | NotebookLM: notebook yaratish → `transcript.pdf` yuklash → "Audio Overview" (custom prompt: "two hosts, follow the script order") → yuklab olish → `episodes/<slug>/audio/notebooklm.m4a` |
| 04 Align | CLI | whisperx |
| 05 Rasmlar | brauzer-agent (Flow) **yoki** agentning rasm vositasi | `storyboard.json` dagi har prompt → Flow "Image" → 16:9 → yuklab olish `images/shot_NN.png`; personaj referenslari Flow "Ingredients" sifatida bir marta yuklanadi |
| 05 Intro | brauzer-agent (Flow, Veo) | 8 s intro; kuniga 50 bepul kredit |
| 06 Render | CLI | ffmpeg |
| 07 Metadata/thumbnail | agent + CLI | metadata JSON; thumbnail Flow/Nano Banana + Pillow |
| 08 QA | CLI + agent walkthrough | agent walkthrough'da 3 kadr, 30 s audio, thumbnail ko'rsatadi; siz "approve" deysiz |
| 09 YouTube | CLI (Data API) **yoki** brauzer-agent (Studio) | Studio: Upload → fayl → sarlavha/tavsif/teglar/thumbnail/captions/schedule → "Schedule" |

## 3. Loyiha fayllari (repoda tayyor)

- `.agent/rules/unumdorlik.md` — agent uchun doimiy qoidalar (format standarti, "faqat CLI chaqir",
  brauzer xavfsizligi, hech qachon to'lov/parol kiritmaslik).
- `.agent/workflows/episode.md` — `/episode <slug>`: to'liq epizod.
- `.agent/workflows/images-flow.md` — `/images-flow <slug>`: faqat Flow rasmlar.
- `.agent/workflows/publish-studio.md` — `/publish-studio <slug>`: faqat YouTube Studio.
- `.agents/mcp_config.json` — MCP serverlar (GitHub, notebooklm-py, gflow, Composio ixtiyoriy).

Eslatma: Antigravity versiyasiga qarab kataloglar `.agent/` yoki `.agents/` bo'ladi; IDE
"Customizations" panelidan tekshiring. `.agent*/` kataloglarini `.gitignore`ga **qo'shmang**.

## 4. Sozlash tartibi (30–45 daqiqa)

1. Antigravity'ni o'rnating (antigravity.google), Google akkaunt bilan kiring (bepul daraja).
2. Chrome'ga Antigravity brauzer kengaytmasini o'rnating; **shu Chrome profilida** Google (Flow,
   NotebookLM, AI Studio) va YouTube Studio'ga kiring — agent sizning sessiyangizdan foydalanadi.
3. Repo'ni oching → `.agent/rules` va `.agent/workflows` avtomatik indekslanadi.
4. `uv sync` (Python CLI), `ffmpeg` o'rnatilgan bo'lsin, `.env` da `GEMINI_API_KEY` (bepul).
5. Agent Manager'da "Planning" rejimini yoqing (reja → tasdiq → bajarish), brauzer uchun
   "ask before purchases/forms" himoyasini qoldiring.
6. Sinov: `/images-flow example` — 3 kadr; so'ng `/episode <slug>`.

## 5. Antigravity vs Claude Code vs GitHub Actions — qaysi biri qachon

| Mezon | Antigravity | Claude Code (bu sessiya) | GitHub Actions |
|---|---|---|---|
| Narx | bepul (kvota) | obuna | bepul (limit) |
| Brauzer-ilovalar (Flow, NotebookLM, Studio) | **ha, kuchli tomoni** | faqat Chrome kengaytmasi bilan, lokal | yo'q |
| Rejalashtirilgan ishga tushirish | yo'q (CLI + cron bilan) | bulut sessiya + Routine (bor) | **ha, cron** |
| Determinik, takrorlanuvchi | o'rta (agent) | o'rta (agent) | **yuqori** |
| Qayerda ishlaydi | sizning kompyuteringiz | bulut/lokal | bulut |

**Tavsiya etilgan kombinatsiya:** GitHub Actions — kodli bosqichlar (01–04, 06–08) har kuni avtomatik;
Antigravity — brauzer bosqichlari (05 Flow, 03-B NotebookLM, 09 Studio) kuniga bir marta
`/episode-browser` bilan; Claude Code — ishlab chiqish, tahlil, yangi mavzular, tuzatishlar.
Agar hammasi bitta joyda bo'lsin desangiz: Antigravity + o'z kompyuteringizda cron
(`antigravity` CLI yoki `unumdorlik watch`) — to'liq bepul, lekin kompyuter yoqiq turishi kerak.
