# 04 — Bepul variantlar ($0 va "deyarli $0" liniyalar)

Sana: 2026-10-07. Narx/limitlar tez o'zgaradi; har bosqichda "Tekshirish" ustuni bor.

## 1. Har bosqich uchun bepul muqobillar

| Bosqich | Pullik (01-REJA) | Bepul variant(lar) | Sifat | Cheklov / eslatma |
|---|---|---|---|---|
| 01 Skript | Claude API | **a)** Claude Code obunasi (sizda bor) — bosqich Claude Code ichida skill/komanda sifatida bajariladi, API to'lovi yo'q; **b)** Gemini API bepul darajasi (`gemini-*-flash`, kuniga cheklangan so'rov); **c)** Antigravity agenti (Gemini 3 Pro / Claude, bepul kvota) | a ≈ pullik; b yaxshi; c yaxshi | b: bepul darajada ma'lumotlar o'qitishga ishlatilishi mumkin; kunlik limit |
| 02 Lug'at/PDF | — | spaCy + ochiq CEFR ro'yxatlar (Oxford 3000/5000 ochiq PDF; GitHub'dagi `cefr`-ro'yxatlar; EVP ochiq qism) + `reportlab`/`weasyprint` | to'liq | Oxford ro'yxati litsenziyasi: shaxsiy foydalanish; tijorat uchun ochiq-litsenziyali ro'yxat tanlanadi |
| 03 Audio | Gemini 3.8 Flash TTS (pullik) | **a)** Gemini 3.8 Flash TTS **bepul darajasi** (kunlik limit, ikki ovoz, bir xil sifat); **b)** `edge-tts` (Microsoft neural ovozlar, bepul, 2 ovozni alohida sintez qilib birlashtiramiz, **so'z vaqtlarini beradi** → 04-bosqich kerak emas); **c)** Kokoro-82M (ochiq, lokal, CPU'da ham tez, so'z vaqtlari bor); **d)** NotebookLM veb (bepul, kuniga cheklangan audio) | a eng yaxshi; b yaxshi; c yaxshi; d juda tabiiy, lekin boshqarib bo'lmaydi | b norasmiy (Edge brauzer endpointi), har qanday vaqtda yopilishi mumkin |
| 04 Alignment | whisperx (bepul) | whisperx lokal/Colab; yoki edge-tts/Kokoro'ning tayyor vaqtlari | to'liq | GitHub Actions CPU'da 19 daq audio ≈ 5–8 daq |
| 05 Rasmlar | Nano Banana 2 API (pullik) | **a)** Google Flow'da rasm generatsiyasi **bepul** (kredit sarflamaydi), faqat videolar kredit yeydi → `gflow-cli` yoki Antigravity brauzer-agenti orqali; **b)** Google AI Studio veb (bepul, kuniga yuzlab rasm) — brauzer-agent orqali; **c)** FLUX.1-schnell / SDXL + Pixar-LoRA Colab bepul T4 GPU'da (to'liq ochiq, cheksiz); **d)** Gemini ilovasi (bepul, ~100 rasm/kun) | a, b ≈ pullik sifat; c yaxshi (sozlash kerak) | a, b: brauzer avtomatizatsiyasi — mo'rt; c: personaj barqarorligi uchun IP-Adapter/LoRA kerak |
| 06 Render | ffmpeg | ffmpeg | to'liq | — |
| 07 Thumbnail/metadata | Claude/Nano Banana | 01 va 05 dagi bepul yo'llar + Pillow | to'liq | — |
| 08 QA/tasdiq | GitHub PR | GitHub PR / Telegram bot (bepul) | to'liq | — |
| 09 YouTube | Data API | **a)** Data API (bepul, kvota 100 upload/kun) — audit o'tmaguncha private; **b)** YouTube Studio'ga brauzer-agent (Antigravity) orqali yuklash — audit talab qilmaydi, video darhol public/scheduled bo'ladi | to'liq | b: YouTube ToS avtomatlashtirilgan brauzer kirishini taqiqlaydi; o'z akkauntingizda, past chastotada xavf kam, lekin rasman "kulrang zona" |
| Orkestratsiya | GitHub Actions | GitHub Actions (public repo: cheksiz; private: 2000 daq/oy), Google Colab bepul, o'z kompyuteringiz + cron | to'liq | Actions'da brauzer-agent yo'q; brauzer kerak bo'lgan bosqichlar lokal mashinada |
| Video intro (Veo) | Veo 3.1 API | Flow bepul: kuniga 50 kredit (≈ 2 Fast yoki 5 Lite video) | yaxshi | faqat intro/trailer uchun yetarli |

## 2. Uchta tayyor "stack"

### Stack A — "Nol dollar" (to'liq bepul, API hisob-kitobsiz)

```
Mavzu (git inbox)
 → Skript: Claude Code (obuna) yoki Gemini bepul darajasi
 → Lug'at/PDF: spaCy + ochiq CEFR + reportlab
 → Audio: Gemini 3.8 Flash TTS bepul darajasi; limit tugasa edge-tts (fallback)
 → Vaqtlar: whisperx (Colab/lokal) yoki edge-tts WordBoundary
 → Rasmlar: Google Flow (bepul rasm) gflow-cli/Antigravity orqali; fallback: FLUX-schnell Colab
 → Render: ffmpeg
 → YouTube: Data API (private) + Studio'da qo'lda public  |  yoki Antigravity brauzer-agent → Studio
```
Tannarx: **$0/epizod**. Narx: vaqt (brauzer-agent nazorati) va mo'rtlik (norasmiy yo'llar).
Avtomatlik darajasi: ~80 % (rasm va YouTube bosqichlari vaqti-vaqti bilan inson aralashuvini talab qiladi).

### Stack B — "Obunalar bilan" (sizda bor/arzon obunalar, API yo'q)

- Claude Code (bor) — skript, lug'at, storyboard, metadata, orkestratsiya.
- **Google AI Pro ($19.99/oy)** — Flow 1000 kredit/oy (Veo intro, rasm cheksiz), NotebookLM kengaytirilgan limit, Gemini ilovasi Nano Banana Pro, 2 TB Drive.
- Bepul: TTS (Gemini bepul darajasi/edge-tts), whisperx, ffmpeg, GitHub Actions, YouTube API.

Tannarx: **$20/oy** barcha epizodlar uchun. Eng mantiqli "o'rta" yo'l: siz allaqachon Flow'dan foydalanmoqchisiz.

### Stack C — "Minimal pullik" (faqat rasmlar API orqali)

Stack A + rasmlar `gemini-3.1-flash-image` API (1K ≈ $0.07 × 32 ≈ $2.2/epizod). Rasm bosqichi 100 % barqaror va avtomatik bo'ladi; qolgani bepul.
Tannarx: **≈ $2–2.5/epizod**.

## 3. Tavsiya

1. **Boshlash:** Stack B (Claude Code + Google AI Pro). Flow/NotebookLM'ni siz baribir ishlatmoqchisiz, AI Pro ularning limitini ochadi, API hisob ochish shart emas.
2. **Avtomatlikni oshirish:** rasm bosqichi mo'rt bo'lsa, Stack C'ga o'tish (faqat $2/epizod).
3. **YouTube:** Data API'ni audit uchun hoziroq topshiring; audit o'tgunga qadar "API → private → Studio'da 1 klik public" (kuniga 1 daqiqa inson ishi). Brauzer-agent orqali Studio'ga yuklashni **faqat** audit rad etilsa ishlating.
4. TTS uchun avvalo Gemini 3.8 Flash TTS bepul darajasini sinab ko'ring; kunlik limit 3 epizod/haftaga yetadimi — 1-haftada o'lchanadi. Yetmasa edge-tts.

## 4. Bepul yo'llarning xavflari

| Xavf | Chora |
|---|---|
| Bepul darajalar kutilmaganda kamayadi (Antigravity 250 → 20 so'rov/kun kabi) | Har bosqichda 2 ta yo'l (asosiy + fallback) konfiguratsiyada; `unumdorlik doctor` limitni tekshiradi |
| Norasmiy kutubxonalar (edge-tts, gflow-cli, notebooklm-py) sinadi | Pin qilingan versiyalar; rasmiy API fallback (Stack C) |
| Brauzer-agent YouTube/Google tomonidan bloklanadi | Past chastota, real Chrome profili, 2FA bilan o'z akkaunt; API yo'liga qaytish |
| Bepul API darajasida ma'lumot o'qitishga ishlatiladi | Skript/manba maxfiy bo'lmasa muammo emas; maxfiy bo'lsa — pullik daraja |
