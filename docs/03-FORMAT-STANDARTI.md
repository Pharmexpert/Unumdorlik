# 03 — Epizod formati standarti

Namuna sifatida berilgan videolar: `https://youtu.be/c-xuV-WnD3E` (English Talk Sessions,
"This 1 Formula Builds 500 English Sentences", 19:09, Education) va `https://youtu.be/l6rbcL_Eun0`.
Ikkinchisining sahifasi tarmoq cheklovi tufayli o'qilmadi; birinchisining to'liq transkripti
va tavsifi tahlil qilindi. Ikkalasi bir kanal formatida deb qabul qilinadi.

## 1. Namuna videoning tuzilishi (c-xuV-WnD3E tahlili)

| Blok | Davomiylik (taxm.) | Mazmuni |
|---|---|---|
| Cold open (hook) | 0:00–0:20 | "Did you know ... ?" — muammo bayoni, savol |
| Salomlashuv | 0:20–0:50 | "Welcome back to … I'm Mia / And I'm James" |
| Mavzu e'loni + va'da | 0:50–1:20 | "By the end of today's episode …" |
| CTA (subscribe/bell/share) | 1:20–1:30 | Qisqa, bir marta |
| Asosiy qism: 3–4 bo'lim | 1:30–15:00 | Har bo'lim: tushuntirish → 4–6 misol → "math"/xulosa → hikoya (anekdot) |
| Umumiy xato / hikoya | oraliq | Boshlovchining shaxsiy tajribasi (aeroport, kofe) |
| Amaliyot (practice) | 9:30–15:00 | Bir boshlovchi vazifa beradi, ikkinchisi bajaradi; real vaziyatlar |
| Shadowing | 15:20–16:30 | "Repeat after us slowly" — 5–7 gap |
| Recap | 16:30–17:30 | Formulalar/asosiy fikrlar ro'yxati |
| Vocabulary recap | 17:30–18:30 | 5 so'z, har biri 1 jumlali izoh bilan |
| Challenge + xayrlashuv | 18:30–19:09 | "Write one sentence in the comments…", "see you tomorrow" |

Uslub belgilari:
- Ikki boshlovchi: biri "o'qituvchi" (Mia), biri "o'rganuvchi/qiziquvchi" (James). Dialog
  savol-javob, tasdiqlash ("Exactly", "Perfect"), yengil hazil, `[laughter]`, `[music]` belgilari.
- Sekin, sodda, qayta-qayta takrorlanadigan ingliz tili (A2–B1 asosiy, ba'zi B2 so'zlar).
- Har bo'limda raqamli "isbot" (20 fe'l × 10 sabab = 200 gap) — konkretlik.
- Tavsifda: 1 abzats annotatsiya, "What you'll learn" ro'yxati, timestamps (chapters),
  subscribe CTA, 6–8 hashtag. Teglar 15–18 ta.

## 2. Bizning epizod standarti (shundan kelib chiqib)

**Davomiylik:** 15–20 daqiqa. Nutq tezligi ~135–145 so'z/daqiqa → skript **2300–2700 so'z**.

**Boshlovchilar (doimiy personajlar):**
- `HOST_A` — mutaxassis-tushuntiruvchi (ayol ovoz, iliq, aniq).
- `HOST_B` — qiziquvchi hamkor (erkak ovoz, jonli, savol beruvchi).
- Ismlar va ovozlar `config/pipeline.yaml` da belgilanadi, Pixar uslubidagi tashqi ko'rinishi
  bir marta "character sheet" sifatida generatsiya qilinib, barcha epizodlarda qayta ishlatiladi.

**Majburiy bloklar (skript generatori tekshiradi):**
1. HOOK (≤ 60 so'z, savol bilan)
2. INTRO + mavzu + va'da
3. CTA (bir marta, ≤ 40 so'z)
4. 3–4 ta SECTION, har birida: tushuntirish, ≥ 4 misol, 1 mini-xulosa
5. STORY — kamida 1 shaxsiy hikoya
6. PRACTICE — savol-javob mashqi (≥ 6 almashinuv)
7. SHADOWING — 5–7 gap, sekin o'qish belgisi `[slow]`
8. RECAP
9. VOCABULARY — 8–12 so'z, har biri CEFR darajasi (A1–C2) va 1 jumlali inglizcha izoh bilan
10. CHALLENGE + OUTRO

**Lug'at (A1–C2) qoidasi:** skriptdagi barcha so'zlar CEFR ro'yxati bilan solishtiriladi;
B1+ dan yuqori yoki mavzuga xos atamalar lug'atga kiradi; har bir so'z uchun:
`word | POS | CEFR | IPA | plain-English definition | example from the episode`.
Videoda so'z birinchi marta aytilganda ekranda 4–6 soniyalik "vocab card" chiqadi.

**Vizual standart:** 16:9, 1920×1080, Pixar/3D-animatsiya uslubi, iliq rang palitrasi,
har 25–45 soniyada 1 rasm (epizodga 25–40 rasm), Ken Burns (sekin zoom/pan) harakati,
pastda subtitr (so'zma-so'z sinxron), yuqori chapda bo'lim nomi, vocab kartalar.

**YouTube metadata:** sarlavha ≤ 70 belgi (raqam yoki va'da bilan), tavsif (annotatsiya +
"What you'll learn" + timestamps + CTA + hashtag), 15–20 teg, kategoriya 27 (Education),
til `en`, chapters avtomatik, caption (`.srt`) yuklanadi, thumbnail 1280×720 (< 2 MB).
