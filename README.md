# Unumdorlik — AI podcast-video ishlab chiqarish liniyasi

Adabiyotdan tanlangan mavzu → ingliz tilidagi ikki boshlovchili podcast-dialog (BBC uslubi)
→ transkript PDF + A1–C2 lug'at → audio → Pixar uslubidagi slayd-rasmlar → video → YouTube.

Maqsad: inson faqat **mavzu tanlaydi** va **tasdiqlaydi**, qolgan hamma bosqich avtomatik bajariladi.

| Hujjat | Mazmuni |
|---|---|
| [ANTIGRAVITY-QOLLANMA.md](ANTIGRAVITY-QOLLANMA.md) | **Boshlash shu yerdan:** paketni ochish va Antigravity'da `/start` bilan bitta so'rovda ishga tushirish |
| [docs/01-REJA.md](docs/01-REJA.md) | To'liq reja: arxitektura, bosqichlar, vositalar tanlovi, MCP ulanishlar, xarajat, xavflar |
| [docs/02-YOL-XARITASI.md](docs/02-YOL-XARITASI.md) | Bosqichma-bosqich yo'l xaritasi (haftalar, natijalar, qabul mezonlari) |
| [docs/03-FORMAT-STANDARTI.md](docs/03-FORMAT-STANDARTI.md) | Epizod formati standarti (namuna videolar tahlili asosida) |
| [docs/04-BEPUL-VARIANTLAR.md](docs/04-BEPUL-VARIANTLAR.md) | Har bosqich uchun bepul muqobillar va uchta tayyor stack ($0 / $20 oy / $2 epizod) |
| [docs/05-ANTIGRAVITY-VARIANTI.md](docs/05-ANTIGRAVITY-VARIANTI.md) | Google Antigravity orqali amalga oshirish: brauzer-agent bilan Flow, NotebookLM, YouTube Studio |
| [docs/06-SOZLASH.md](docs/06-SOZLASH.md) | Sozlash yo'riqnomasi: Gemini kaliti, Claude Code login/token, character sheet, YouTube OAuth |
| [.agent/](.agent/) | Antigravity qoidalari va `/episode`, `/images-flow`, `/publish-studio` workflow'lari |
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

## CLI (skelet, v0.1)

```bash
uv sync --extra llm --extra audio --extra pdf --extra images   # (+ --extra align, --extra youtube kerak bo'lsa)
cp config/profiles/stack-b.yaml config/pipeline.yaml           # yoki stack-a.yaml; yoki UNUMDORLIK_PROFILE=stack-a
cp .env.example .env                                           # GEMINI_API_KEY (bepul daraja) va h.k.

uv run unumdorlik doctor                 # muhit tekshiruvi
uv run unumdorlik inbox                  # topics/inbox dagi mavzular
uv run unumdorlik schedule --apply       # kuniga 2 ta bo'sh slot (config.channel.publish_times) biriktiradi
uv run unumdorlik run <slug> --from 01 --to 08
uv run unumdorlik status                 # bosqichlar holati
uv run unumdorlik images-check <slug>    # Antigravity /images-flow dan keyin
uv run unumdorlik approve <slug> && uv run unumdorlik upload <slug>
uv run unumdorlik process --limit 2 --to 08   # GitHub Actions har kuni shuni chaqiradi
```

Chiqish kodlari: `0` ok, `1` xato, `3` PAUSED (brauzer/inson qadami kerak — xabarda nima qilish yozilgan).

| Bosqich | Stack A (bepul) | Stack B (obunalar) |
|---|---|---|
| 01 skript | `claude_cli` (Claude Code obunasi) yoki `gemini` (bepul daraja) | `claude_cli` |
| 03 audio | `edge_tts` (so'z vaqtlari bilan) yoki `gemini_tts` bepul daraja | `gemini_tts` → limitda avtomatik `edge_tts` |
| 04 align | edge vaqtlari → whisperx → baho | auto |
| 05 rasm | Flow (bepul rasm) — Antigravity `/images-flow` | Flow (AI Pro) — Antigravity `/images-flow` |
| 09 YouTube | Data API (audit o'tmaguncha private) | Data API |

Profil farqi faqat YAML'da; kod yo'li bir xil (`config/profiles/`).
