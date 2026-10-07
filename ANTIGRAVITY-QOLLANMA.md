# Antigravity bilan bitta so'rovda ishga tushirish — qo'llanma

Bu paket: `C:\Users\texno\Downloads\Video\Unumdorlik` papkasiga ochiladi va Google Antigravity'da **bitta so'rov**
(`/start`) bilan butun liniyani ishga tushiradi. Qolgan hamma narsa (reja, kod, promptlar, workflow'lar) paket ichida.

## 0. Nima kerak (bir marta)
| Narsa | Qayerdan | Holat |
|---|---|---|
| Google Antigravity | https://antigravity.google → Windows installer, Google akkaunt bilan kiring (bepul) | siz |
| Antigravity Chrome kengaytmasi | Antigravity ichida "Browser" → Install extension; **shu Chrome profilida** Flow, NotebookLM, YouTube Studio'ga kiring | siz |
| Claude Code obunasi | `claude` → `/login` (bajarilgan ✅) | tayyor |
| GEMINI_API_KEY | aistudio.google.com → Get API key (billing'siz) | `.env` ga |
| Google AI Pro (Stack B) | Flow kreditlari, NotebookLM limitlari; bo'lmasa Stack A ham ishlaydi | ixtiyoriy |

## 1. Paketni joylash
1. ZIP'ni `C:\Users\texno\Downloads\Video\` ga saqlang va shu yerga oching → `...\Video\Unumdorlik\` papkasi hosil bo'ladi.
   (Muqobil: `git clone https://github.com/Pharmexpert/Unumdorlik -b claude/intelligent-newton-6jkr9h` shu papkaga.)
2. Antigravity → **Open Folder** → `C:\Users\texno\Downloads\Video\Unumdorlik`.
   Antigravity `.agent/rules` va `.agent/workflows` ni avtomatik o'qiydi (Customizations panelida ko'rinadi).

## 2. Bitta so'rov
Antigravity Agent Manager'da (Planning rejimi yoqilgan holda) yozing:

```
/start
```

Agent nima qiladi (hammasi `.agent/workflows/start.md` da):
1. `scripts\setup-windows.ps1` — uv, ffmpeg, Claude CLI o'rnatadi, Python muhitini yig'adi, `config\pipeline.yaml` va `.env` yaratadi.
2. `unumdorlik doctor --probe` — Claude va Gemini ulanishini tekshiradi; yetishmasa aniq nima qilishni aytadi.
3. Brauzerda Flow'ga kirib **Mia va James** character sheet'larini yaratadi → **sizdan tasdiq** (1-to'xtash).
4. `topics/inbox/` dagi birinchi mavzuni (tayyor: *Why Your Brain Forgets New Words*) 09:00/18:00 slotiga rejalashtiradi.
5. Skript → lug'at + PDF → ikki ovozli audio → vaqtlar → storyboard → Flow'da 30 ga yaqin Pixar-kadr → render → metadata/thumbnail → QA.
6. Walkthrough ko'rsatadi (3 kadr, thumbnail, sarlavha, tavsif, QA) → **sizdan tasdiq** (2-to'xtash).
7. YouTube Studio'da yuklab, belgilangan vaqtga rejalashtiradi → havolani beradi, natijani git'ga commit qiladi.

Agar `.env` da `GEMINI_API_KEY` bo'lmasa, agent 2-qadamda to'xtab so'raydi — kalitni **faylga** yozing, chatga emas.

## 3. Har kuni (2 epizod)
- Yangi mavzu: `topics/inbox/<slug>.md` (namuna: `EXAMPLE-topic.md`), so'ng Antigravity'da `/episode <slug>`.
- Yoki GitHub Actions avtomatik: har kuni 07:17 (Toshkent) inbox'dan 2 mavzuni 08-bosqichgacha olib boradi, PR ochadi;
  brauzer qadamlari (rasm, Studio) uchun Antigravity'da `/images-flow <slug>` va `/publish-studio <slug>`.

## 4. Fayllar xaritasi
| Yo'l | Nima |
|---|---|
| `BITTA-ZAPROS.txt` | Antigravity'ga yoziladigan so'rov (nusxa-yopishtirish uchun) |
| `.agent/workflows/` | `/start`, `/episode`, `/images-flow`, `/publish-studio`, `/character-sheet` |
| `.agent/rules/unumdorlik.md` | agent qoidalari (xavfsizlik, format, CLI) |
| `.agents/mcp_config.json` | MCP serverlar (GitHub, notebooklm-py, gflow — ixtiyoriy) |
| `scripts/setup-windows.ps1` | bir martalik o'rnatish |
| `src/unumdorlik/` | Python CLI, 9 bosqich |
| `prompts/` | AI promptlari (skript, lug'at, storyboard, metadata) |
| `config/profiles/` | `stack-a.yaml` ($0) / `stack-b.yaml` (obunalar) |
| `docs/01…06` | reja, yo'l xaritasi, format standarti, bepul variantlar, Antigravity, sozlash |
| `topics/inbox/` | mavzular (1 ta tayyor) |
| `assets/characters/PROMPTS.md` | boshlovchilar rasm promptlari |

## 5. Tez-tez uchraydigan to'xtashlar
| Agent xabari | Nima qilish |
|---|---|
| `claude CLI YO'Q` / `probe:claude_cli` xato | terminal: `claude` → `/login` → `/exit`, so'ng agentga "davom et" |
| `GEMINI_API_KEY YO'Q` | `.env` faylida `GEMINI_API_KEY=AIza...` qatorini to'ldiring |
| Flow "sign in" so'rayapti | Antigravity ishlatayotgan Chrome profilida flow.google.com ga kiring |
| `PAUSED 05 images` | `/images-flow <slug>` (agent o'zi chaqiradi; kvota tugasa ertaga davom etadi) |
| YouTube "private" | API orqali yuklangan va audit o'tmagan; Studio orqali yuklash (`/publish-studio`) yoki Studio'da qo'lda public |
