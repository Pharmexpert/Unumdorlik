# 01 — To'liq reja: AI podcast-video ishlab chiqarish liniyasi

Sana: 2026-10-07. Holat: tasdiqlash uchun taklif.

## 0. Qisqacha xulosa (TL;DR)

- Inson ishi: **mavzu faylini** `topics/inbox/` ga qo'yish va tayyor videoni **tasdiqlash**. Boshqa hamma narsa avtomatik.
- Liniya 9 bosqichdan iborat; har bosqich alohida ishga tushadi, qayta bajarilsa natija o'zgarmaydi (idempotent), artefaktlar `episodes/<slug>/` da saqlanadi.
- **Asosiy texnologik qaror:** audio uchun NotebookLM emas, **Gemini 3.8 Flash TTS** (ikki ovozli dialog, rasmiy API) tavsiya etiladi. Sabab: skript = transkript = subtitr = lug'at vaqtlari bir-biriga 100 % mos bo'ladi, bu avtomatlashtirish uchun hal qiluvchi. NotebookLM ikkinchi (ixtiyoriy) rejim sifatida saqlanadi.
- **Rasmlar:** Gemini API `gemini-3.1-flash-image` (Nano Banana 2) — rasmiy, 16:9, referens rasm orqali personaj barqarorligi. Google Flow rasmiy API bermaydi; u faqat qo'lda/`gflow-cli` orqali "hero" kadrlar va Veo intro uchun.
- **YouTube:** Data API v3 orqali yuklash. Muhim: audit qilinmagan API loyihasidan yuklangan videolar **majburan private** bo'ladi; auditga **1-kundan** ariza beriladi (2–6 hafta).
- Epizod tannarxi (API): ≈ **$3–6**. Birinchi ishlaydigan epizod: **2 hafta**. To'liq avtomatik rejim: **4–5 hafta**.

## 1. Maqsad va mahsulot

**Mahsulot:** 15–20 daqiqalik, ikki boshlovchili inglizcha o'quv podcast-videosi (namuna: English Talk Sessions kanali), har epizodga:
1. `video.mp4` (1080p, Pixar-uslub slayd-shou, so'zma-so'z subtitr, lug'at kartalari);
2. `transcript.pdf` (transkript + A1–C2 lug'at + mashqlar);
3. `audio.m4a` (podcast platformalari uchun);
4. YouTube'da metadata, chapters, caption, thumbnail bilan rejalashtirilgan nashr.

**Format standarti** alohida hujjatda: `docs/03-FORMAT-STANDARTI.md`.

## 2. Arxitektura

```
            ┌────────────────────────── inson ──────────────────────────┐
            │  mavzu (topics/inbox/*.md)            tasdiq (PR / Telegram) │
            └──────────┬─────────────────────────────────┬──────────────┘
                       ▼                                 │
  ┌─────────────────────────────────────────────────────────────────────┐
  │  orchestrator  (Python CLI `unumdorlik`, GitHub Actions / cron)      │
  │                                                                       │
  │  01 script ──► 02 vocab+pdf ──► 03 tts ──► 04 align ──► 05 images     │
  │      │                                                      │         │
  │      └──► 07 metadata ◄── 06 render ◄───────────────────────┘         │
  │                 │                                                     │
  │            08 QA gate ──► [tasdiq] ──► 09 youtube upload (publishAt)  │
  └─────────────────────────────────────────────────────────────────────┘
          │               │              │               │
      Claude API     Gemini TTS     Gemini Image     YouTube Data API
   (skript, lug'at,  (2 ovoz)      (Nano Banana 2)   (OAuth, upload,
    storyboard,                     / Flow (opt.)     captions, thumb)
    metadata)
```

Har epizod katalogi:

```
episodes/<slug>/
  topic.md            # kirish nusxasi
  script.json         # 01
  glossary.json       # 02
  transcript.pdf      # 02
  audio/dialogue.wav  # 03   (gitignore)
  alignment.json      # 04   so'z/turn vaqtlari
  storyboard.json     # 05
  images/shot_01.png  # 05   (gitignore)
  render/video.mp4    # 06   (gitignore)
  subtitles.srt       # 06
  thumbnail.png       # 07
  metadata.json       # 07
  qa_report.json      # 08
  youtube.json        # 09   video_id, holat, publishAt
  state.json          # bosqichlar holati, hashlar (qayta ishga tushirish uchun)
```

## 3. Bosqichlar (batafsil)

### 01 — Skript (Claude)
- Kirish: mavzu fayli (frontmatter + mazmun). Prompt: `prompts/01_dialogue_script.md`.
- Model: `claude-opus-5-5` (sifat) yoki `claude-sonnet-5-5` (arzon). Chiqish qat'iy JSON.
- Validatsiya (kod, AI emas): so'z soni ±8 %, barcha majburiy bloklar bor, har SECTION ≥ 4 misol, PRACTICE ≥ 6 almashinuv, lug'atdagi `example` matn skriptda mavjud. Xato bo'lsa — 1 marta "fix" prompti bilan qayta so'raladi, bo'lmasa bosqich `FAILED`.
- Qo'shimcha: `turns[].visual_cue` — storyboard uchun ko'rsatma.

### 02 — Lug'at + transkript PDF
- Deterministik qism: skript leksemalari (spaCy lemmatizer) → `assets/cefr/oxford5000.csv` (Oxford 3000/5000 CEFR darajalari; muqobil — English Vocabulary Profile) bilan solishtiriladi → nomzodlar.
- AI qism: `prompts/02_vocabulary_glossary.md` → yakuniy 8–12 so'z + 5 bonus C1–C2.
- PDF: `reportlab` yoki HTML→PDF (`weasyprint`). Tarkib prompt faylida belgilangan. PDF Google Drive'ga yuklanadi (Drive MCP bor) va havolasi tavsifga qo'shiladi.

### 03 — Audio
**A rejim (asosiy): Gemini TTS, ikki ovoz, bitta chaqiruv.**
- Model `gemini-3.8-flash-tts` (2026-09 chiqdi; 2000+ ovoz, ikki ovozli dialog, `[laughs]`, `[slow]` kabi teglar). Narx ≈ $0.037/daqiqa → 19 daqiqa ≈ $0.70.
- Kirish uzunligi chegaralangani uchun skript **bo'limlar bo'yicha** (HOOK+INTRO, SECTION_1, …) alohida sintez qilinadi, so'ng `ffmpeg concat` + 0.6 s pauza + intro/outro musiqa (royalty-free) + loudness normalizatsiya `-16 LUFS` (`ffmpeg loudnorm`).
- Har bo'lim uchun `speech_metadata.style` skriptdagi `style` maydonidan olinadi.
- Ovozlar `config` da: A → "Kore", B → "Puck" (sinovdan keyin tanlanadi). Keyinchalik 30 soniyalik namuna bilan custom ovoz.

**B rejim (ixtiyoriy): NotebookLM Audio Overview.**
- Rasmiy yo'l: *Gemini Notebook Enterprise API* (`notebooks.audioOverviews.create`, Pre-GA preview, Google Cloud loyihasi kerak).
- Norasmiy yo'l: `notebooklm-py` (CLI + MCP server + Claude Code skill; brauzer-cookie autentifikatsiya; "undocumented API, may break"). Buyruqlar: `notebooklm create`, `source add transcript.pdf`, `generate audio "…" --wait`, `download audio`.
- Kamchilik: NotebookLM o'zi skript yozadi → bizning transkript/lug'at/subtitr unga mos kelmaydi; audio chiqqach uni Whisper bilan qayta transkripsiya qilish va lug'atni qayta hisoblash kerak. Shuning uchun B rejim faqat "variant epizod" yoki ilhom manbai sifatida ishlatiladi; nazorat qilinadigan avtomatik liniya uchun A rejim.
- Qaror: Phase 1 da A rejim; Phase 4 da B rejim "NotebookLM Deep Dive" seriyasi sifatida sinab ko'riladi.

### 04 — Vaqt sinxronizatsiyasi (forced alignment)
- TTS so'z vaqtlarini bermaydi. Skript matni + audio → `whisperx` (large-v3, alignment rejimi) → har so'z `start/end`. Skript ma'lum bo'lgani uchun aniqlik juda yuqori.
- Natija: `alignment.json` (turn va so'z darajasida). Undan: chapters vaqtlari, lug'at kartalari vaqti, subtitr, storyboard chegaralari.

### 05 — Storyboard va rasmlar
- Claude → `prompts/03_storyboard_pixar.md` → `storyboard.json` (25–40 kadr, har biriga prompt, kamera, Ken Burns yo'nalishi).
- Generatsiya: Gemini API `gemini-3.1-flash-image`, `aspect_ratio 16:9`, 2K; hostlar bo'lgan kadrlarda `assets/characters/` dan referens rasmlar yuboriladi (≤14 ta) — personaj bir xil chiqadi.
- Character sheet (bir marta): har host uchun 4 rakurs → inson tasdiqlaydi → referens sifatida muzlatiladi.
- Parallel generatsiya (5 oqim), har kadr uchun 2 urinish; moderatsiya rad etsa prompt yumshatiladi.
- Google Flow: rasmiy API yo'q. Variantlar: (1) `gflow-cli` (Playwright, haqiqiy Chrome login, alpha, reverse-engineered) — serverda ishlashi qiyin; (2) useapi.net (pullik, uchinchi tomon). Tavsiya: Flow'ni faqat 8 soniyalik Veo 3.1 intro-klip va kanal trailer uchun **qo'lda** ishlatish; agar Veo kerak bo'lsa — Gemini API `veo-3.1` rasmiy yo'li.

### 06 — Render (ffmpeg)
- Har kadr: `zoompan` (Ken Burns), `xfade` o'tishlar (0.5 s), audio bilan vaqt bo'yicha mos.
- Overlay qatlamlari (ASS subtitr fayli bilan bitta `subtitles` filtri): so'zma-so'z subtitr (karaoke `\k` teglari), bo'lim sarlavhasi (yuqori chap), lug'at kartasi (so'z birinchi aytilganda 5 s), SHADOWING bo'limida gaplar katta shriftda.
- Chiqish: `video.mp4` (H.264, CRF 18, AAC 192k), `subtitles.srt`, `audio.m4a`.
- Tekshiruv: davomiylik audio bilan ±0.5 s; kadrlar soni; rasm yo'q joyda fallback (gradient + sarlavha).

### 07 — Thumbnail + metadata
- `prompts/04_youtube_metadata.md` → sarlavha, tavsif (timestamps `alignment.json` dan), 15–20 teg, pinned comment, thumbnail matni.
- Thumbnail: Nano Banana 2 bilan 2 variant (hostlar + ifoda), `Pillow` bilan ≤5 so'zli matn, 1280×720, <2 MB. vidIQ MCP `score_title` / `score_thumbnail` (kredit bo'lsa) bilan baholash.

### 08 — QA darvozasi va tasdiq
- Avtomatik: skript validatsiyasi, audio loudness, video davomiyligi, subtitr sinxron tekshiruvi (random 5 so'z), rasm soni, metadata uzunliklari, taqiqlangan so'zlar.
- Inson: orchestrator `episodes/<slug>/` ni branch'ga push qilib **PR ochadi** (preview: thumbnail, 60 s preview klip, PDF havolasi). PR merge = tasdiq. Muqobil: Telegram bot (approve/reject tugmalari).

### 09 — YouTube yuklash
- YouTube Data API v3: `videos.insert` (resumable), `thumbnails.set`, `captions.insert` (srt), `status.publishAt` (rejalashtirish), `privacyStatus: private` → `publishAt` kelganda avtomatik public.
- Kvota: "Video Uploads" alohida buckets — 100 upload/kun; boshqa chaqiruvlar 10 000 birlik/kun. Bizga kuniga 1–3 video yetarli.
- **Blokator:** 2020-07-28 dan keyin yaratilgan, audit qilinmagan API loyihasidan yuklangan videolar **private** holatda qulflanadi, Studio orqali ham public qilib bo'lmaydi. Yechim: Google Cloud loyihasini yaratib, "YouTube API Services – Audit and Quota Extension" formasini **1-haftada** to'ldirish. Audit tugaguncha: video API orqali private yuklanadi, so'ng vaqtincha **YouTube Studio'da qo'lda** public qilinadi (bu ruxsat etilmagan bo'lishi mumkin — shuning uchun audit tugaguncha "qo'lda yuklash" fallback'i ham saqlanadi).
- OAuth: `youtube.upload` + `youtube.force-ssl` scope; refresh token bir marta olinadi, `secrets/` da saqlanadi (serverda GitHub Secrets).
- Nashr jadvali: `config.publish_slots` bo'yicha keyingi bo'sh slot.

## 4. Orkestratsiya va avtomatlashtirish

**Dvigatel:** Python 3.12 CLI (`uv` bilan), `typer` buyruqlar: `unumdorlik run <slug> [--from 03] [--to 06]`, `unumdorlik watch`, `unumdorlik status`. Har bosqich `state.json` ga kirish hashlarini yozadi; kirish o'zgarmasa bosqich o'tkazib yuboriladi.

**Trigger variantlari:**
| Variant | Qanday ishlaydi | Afzallik | Kamchilik |
|---|---|---|---|
| **GitHub Actions (tavsiya)** | `topics/inbox/*.md` push → workflow; `cron` kuniga 1 marta "inbox tekshir" | Server kerak emas, loglar, secrets, PR-tasdiq tabiiy | Runner 6 soat limit (yetarli), whisperx CPU'da sekin (~5 daq) |
| Lokal cron / VPS | `unumdorlik watch` daemon | GPU, tezlik | Serverni boshqarish kerak |
| n8n / Make | Vizual oqim, Telegram tasdiq | Oson sozlash | Murakkab render bosqichlari baribir kodda |

**Yakuniy:** GitHub Actions asosiy; render og'irlashsa VPS runner (self-hosted) qo'shiladi.

**Mavzu kiritish kanallari (bittasi tanlanadi, qolganlari keyin):**
1. Git: `topics/inbox/<slug>.md` (eng sodda, versiyalanadi) — **boshlang'ich**.
2. Google Drive papkasi `Unumdorlik/Inbox` — Drive MCP orqali o'qiladi (siz Docs'da yozasiz).
3. Gmail: `#podcast` yorlig'i bilan xat — Gmail MCP orqali.

## 5. MCP va integratsiyalar (Claude Code ichida ishlash uchun)

`.mcp.json` (loyiha darajasida) — rejalashtirilgan ulanishlar:

| Server | Vazifa | Holat |
|---|---|---|
| `github` (mavjud) | PR-tasdiq, Actions ishga tushirish, loglar | tayyor |
| `Google_Drive` (mavjud) | mavzu inbox, PDF nashr | tayyor |
| `Gmail` (mavjud) | mavzu qabul qilish, hisobot | tayyor |
| `vidIQ` (mavjud, kredit kerak) | sarlavha/thumbnail baholash, raqobatchi tahlil, keyword | kredit tugagan |
| `notebooklm-py` MCP (`notebooklm mcp`) | B rejim audio, "video overview", slide-deck | o'rnatiladi (norasmiy) |
| `gflow-cli` MCP (`gflow mcp run`) | Flow orqali rasm/video | ixtiyoriy, alpha |
| Custom `unumdorlik-mcp` (o'zimiz yozamiz, FastMCP) | `run_stage`, `episode_status`, `approve`, `youtube_upload` | Phase 2 |

Gemini (TTS, image, Veo) va Claude API to'g'ridan-to'g'ri SDK orqali chaqiriladi; MCP shart emas.

## 6. Xarajatlar (1 epizod, 19 daqiqa, API narxlari 2026-10)

| Bosqich | Hisob | Taxm. |
|---|---|---|
| Skript + lug'at + storyboard + metadata (Claude) | ~60k kirish / 15k chiqish token | $0.5–1.5 |
| TTS (Gemini 3.8 Flash TTS) | 19 daq × $0.037 | $0.70 |
| Rasmlar (Nano Banana 2, 2K) | 32 × $0.10 + 2 thumbnail | $3.4 |
| Alignment (whisperx, CPU) | GitHub runner | $0 |
| Render | ffmpeg | $0 |
| **Jami** | | **≈ $4.5–6** (1K rasmlar bilan ≈ $3.5) |

Obunalar (ixtiyoriy): Google AI Pro/Ultra (Flow kreditlari, NotebookLM limitlari), vidIQ MCP kreditlari.

## 7. Xavflar va chora-tadbirlar

| Xavf | Ehtimol | Chora |
|---|---|---|
| YouTube audit kechikadi → videolar private | yuqori | 1-haftada ariza; vaqtincha qo'lda nashr; kanalni "official" ko'rinishda to'ldirish |
| Norasmiy NotebookLM/Flow kutubxonalari sinadi | yuqori | Asosiy liniya faqat rasmiy API (Gemini, Claude, YouTube); norasmiylar ixtiyoriy |
| Personaj ko'rinishi epizodlar orasida o'zgaradi | o'rta | Character sheet + referens rasmlar; QA'da 3 kadr inson ko'zi bilan |
| TTS talaffuz xatosi (atamalar) | o'rta | Lug'atdagi so'zlar uchun IPA/fonetik yozuv promptga; `[slow]` teg |
| Mualliflik: manba matnidan ko'chirish | o'rta | Prompt "faqat faktlar, so'zma-so'z ko'chirmaslik"; tavsifda manba keltiriladi |
| Musiqa litsenziyasi | past | YouTube Audio Library yoki sotib olingan trek |
| AI-kontent siyosati (YouTube "altered content" belgisi) | past | Yuklashda `containsSyntheticMedia` belgisi qo'yiladi (talab qilinsa) |

## 8. Hal qilinishi kerak bo'lgan qarorlar (sizdan)

1. **Boshlovchilar ismi/ovozi/ko'rinishi** — 3 variant character sheet tayyorlanadi, bittasini tanlaysiz.
2. **Audio rejimi:** A (Gemini TTS, tavsiya) yoki B (NotebookLM) asosiy bo'lsinmi?
3. **Mavzu kiritish kanali:** Git inbox (tavsiya) / Google Drive / Gmail.
4. **Tasdiq kanali:** GitHub PR (tavsiya) / Telegram.
5. **Nashr chastotasi:** haftasiga 3 (tavsiya boshlang'ich) yoki har kuni.
6. **Google Cloud loyihasi va YouTube kanali** kimning akkauntida bo'ladi (audit arizasi shu akkauntdan).
7. Birinchi 3 mavzu — Phase 1 sinovi uchun.
