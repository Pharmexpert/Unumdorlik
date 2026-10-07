# Unumdorlik — AI podcast-video ishlab chiqarish liniyasi

Adabiyotdan tanlangan mavzu → ingliz tilidagi ikki boshlovchili podcast-dialog (BBC uslubi)
→ transkript PDF + A1–C2 lug'at → audio → Pixar uslubidagi slayd-rasmlar → video → YouTube.

Maqsad: inson faqat **mavzu tanlaydi** va **tasdiqlaydi**, qolgan hamma bosqich avtomatik bajariladi.

| Hujjat | Mazmuni |
|---|---|
| [docs/01-REJA.md](docs/01-REJA.md) | To'liq reja: arxitektura, bosqichlar, vositalar tanlovi, MCP ulanishlar, xarajat, xavflar |
| [docs/02-YOL-XARITASI.md](docs/02-YOL-XARITASI.md) | Bosqichma-bosqich yo'l xaritasi (haftalar, natijalar, qabul mezonlari) |
| [docs/03-FORMAT-STANDARTI.md](docs/03-FORMAT-STANDARTI.md) | Epizod formati standarti (namuna videolar tahlili asosida) |
| [prompts/](prompts/) | Har bir AI bosqichi uchun prompt shablonlari |
| [config/pipeline.example.yaml](config/pipeline.example.yaml) | Liniya konfiguratsiyasi namunasi |
| [topics/inbox/](topics/inbox/) | Yangi mavzular shu yerga qo'yiladi (bitta `.md` fayl = bitta epizod) |
| [episodes/](episodes/) | Har bir epizodning barcha artefaktlari (`episodes/<slug>/`) |

Ish jarayoni qisqacha:

```
topics/inbox/<slug>.md  ──►  01 script  ──►  02 vocab+pdf  ──►  03 audio (TTS)
      ──►  04 align (so'z vaqtlari)  ──►  05 storyboard+rasmlar  ──►  06 render (ffmpeg)
      ──►  07 thumbnail+metadata  ──►  08 QA/tasdiq  ──►  09 YouTube upload (scheduled)
```
