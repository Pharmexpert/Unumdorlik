# 02 — Yo'l xaritasi (roadmap)

Boshlanish: 2026-10-08. Har bosqich oxirida aniq, tekshiriladigan natija (qabul mezoni) bor.
Umumiy muddat: 6 hafta → to'liq avtomatik rejim; birinchi tayyor epizod 2-hafta oxirida.

## Phase 0 — Hisoblar va ruxsatlar (1-hafta, parallel boshlanadi)

| # | Ish | Mas'ul | Natija |
|---|---|---|---|
| 0.1 | Google Cloud loyihasi; YouTube Data API v3 yoqish; OAuth consent screen; `youtube.upload` scope | siz | `client_secret.json` |
| 0.2 | **YouTube API audit arizasi** (Audit & Quota Extension form) — kanal, ilova tavsifi, demo video | siz + men (matn) | ariza raqami |
| 0.3 | Gemini API kaliti (billing yoqilgan) — TTS, image, Veo | siz | `GEMINI_API_KEY` |
| 0.4 | Anthropic API kaliti | siz | `ANTHROPIC_API_KEY` |
| 0.5 | GitHub repo Secrets'ga kalitlar; Actions yoqish | men | Secrets ro'yxati |
| 0.6 | Google AI Pro/Ultra obunasi (Flow + NotebookLM limitlari) — ixtiyoriy | siz | — |
| 0.7 | Royalty-free intro/outro musiqa (YouTube Audio Library) | siz | `assets/music/` |

**Qabul:** barcha kalitlar Secrets'da; `unumdorlik doctor` buyrug'i har API'ga test chaqiruv qilib "OK" qaytaradi.

## Phase 1 — MVP: yarim-avtomatik birinchi epizod (1–2-hafta)

| # | Ish | Natija |
|---|---|---|
| 1.1 | Python loyiha skeleti (`uv`, `typer`, `pydantic` sxemalar `script.json`/`storyboard.json` uchun) | `unumdorlik --help` |
| 1.2 | Bosqich 01: skript generatori + validator (prompts/01) | 3 mavzu uchun `script.json` |
| 1.3 | Bosqich 02: CEFR ro'yxat (Oxford 5000) yuklash, lemmatizatsiya, glossary, PDF | `transcript.pdf` |
| 1.4 | Bosqich 03: Gemini TTS ikki ovoz, bo'limlab sintez, concat, loudnorm | `dialogue.wav` 15–20 daq |
| 1.5 | Ovoz tanlovi: 6 ovoz juftligi namunasi → siz tanlaysiz | `config.hosts` |
| 1.6 | Character sheet: 3 uslub varianti × 2 host → tanlov | `assets/characters/` |
| 1.7 | Bosqich 05 (sodda): storyboard + Nano Banana 2 rasmlar | 30 rasm |
| 1.8 | Bosqich 06 (sodda): ffmpeg Ken Burns + xfade, **qatorli** subtitr (whisperx hali yo'q) | `video.mp4` |
| 1.9 | Qo'lda YouTube'ga yuklash (unlisted) → sifatni ko'rib chiqish | 1-epizod havolasi |

**Qabul:** 1 ta to'liq epizod unlisted holatda; siz 10 ballik shkalada ≥7 baho berasiz; aniqlangan kamchiliklar Phase 2 backlog'iga yoziladi.

## Phase 2 — To'liq avtomatlashtirish (3–4-hafta)

| # | Ish | Natija |
|---|---|---|
| 2.1 | Bosqich 04: whisperx forced alignment → so'z vaqtlari | `alignment.json` |
| 2.2 | Render yangilanishi: karaoke-subtitr (ASS), lug'at kartalari, bo'lim sarlavhalari, shadowing ekrani | `video.mp4` v2 |
| 2.3 | Bosqich 07: metadata + thumbnail (2 variant) | `metadata.json`, `thumbnail.png` |
| 2.4 | Bosqich 08: QA tekshiruvlari + PR-preview (60 s klip, thumbnail, PDF) | avtomatik PR |
| 2.5 | Bosqich 09: YouTube upload (resumable), captions, thumbnail, `publishAt` | `youtube.json` |
| 2.6 | GitHub Actions: `on: push(topics/inbox/**)` + `schedule` (cron) + `workflow_dispatch` | `.github/workflows/pipeline.yml` |
| 2.7 | `state.json` + qayta ishga tushirish (`--from`), xatolarda Telegram/Gmail xabar | barqarorlik |
| 2.8 | Drive/Gmail inbox (tanlangan bo'lsa) | mavzu → repo avtomatik |

**Qabul:** `topics/inbox/x.md` push qilinadi → 40–60 daqiqada PR ochiladi → merge → video belgilangan vaqtda YouTube'da (audit o'tgan bo'lsa public, bo'lmasa private + xabar). Inson aralashuvi: 0 (tasdiqdan tashqari).

## Phase 3 — Sifat va o'sish (5-hafta)

| # | Ish |
|---|---|
| 3.1 | Custom MCP server `unumdorlik-mcp` (Claude Code'dan `run_stage`, `status`, `approve`) |
| 3.2 | Talaffuz lug'ati (atamalar uchun fonetik yozuv), TTS style tuning, `[laughs]`/`[slow]` me'yorlari |
| 3.3 | Thumbnail A/B (YouTube "Test & compare"), vidIQ bilan sarlavha ballari |
| 3.4 | Analitika: YouTube Analytics API → haftalik hisobot (retention egri chizig'i → skript uzunligi/pacing tuzatish) |
| 3.5 | Shorts: har epizoddan 2–3 ta 45 s vertikal klip (9:16 qayta render, vocab card asosida) |
| 3.6 | Veo 3.1 intro-klip (8 s) va kanal traileri (Flow'da qo'lda yoki API) |

**Qabul:** haftasiga 3 epizod + 6 Shorts avtomatik; hisobot Gmail'ga keladi.

## Phase 4 — Kengaytirish (6-hafta va keyin)

- NotebookLM "Deep Dive" seriyasi (B rejim) — `notebooklm-py` MCP orqali, Whisper bilan transkripsiya, alohida playlist.
- Ko'p tilli variantlar: o'zbek/rus subtitrlari (`captions.insert`), ikkinchi audio trek.
- Podcast RSS (Spotify/Apple) — `audio.m4a` + PDF.
- Mavzu avtomatik taklifi: vidIQ keyword/outlier tahlili + adabiyot ro'yxati → haftalik "mavzu menyusi".
- Custom ovoz (30 s namuna) — kanal "brend ovozi".

## Haftalik jadval (qisqa ko'rinish)

```
Hafta 1 : Phase 0 + 1.1–1.5   (kalitlar, skelet, skript, lug'at, TTS, ovoz tanlovi)
Hafta 2 : 1.6–1.9             (personajlar, rasmlar, render, 1-epizod unlisted)   ◄ MILESTONE 1
Hafta 3 : 2.1–2.4             (alignment, karaoke subtitr, metadata, QA/PR)
Hafta 4 : 2.5–2.8             (YouTube API, Actions, inbox)                       ◄ MILESTONE 2: to'liq avtomat
Hafta 5 : Phase 3             (MCP, A/B, analitika, Shorts)
Hafta 6+: Phase 4             (NotebookLM seriyasi, tillar, RSS)
```

## Birinchi qadam (bugun)

1. Siz: Phase 0 dagi 0.1–0.4 ni boshlang (eng uzun — 0.2 audit).
2. Siz: `docs/01-REJA.md` 8-bo'limdagi 7 ta qarorga javob bering.
3. Siz: `topics/inbox/` ga birinchi 3 mavzuni `EXAMPLE-topic.md` formatida qo'ying.
4. Men: kalitlar kelishi bilan 1.1–1.4 ni amalga oshiraman.
