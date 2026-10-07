# Prompt 02 — Lug'at tekshiruvi va CEFR darajalash

Bu bosqich ikki qismdan iborat: (a) deterministik tekshiruv — skriptdagi har bir leksema
`assets/cefr/oxford5000.csv` (yoki EVP/CEFR-J) bilan solishtiriladi; ro'yxatda B1 dan yuqori
yoki umuman yo'q so'zlar (terminlar) "nomzod" bo'ladi; (b) AI bilan yakuniy tanlov va izoh.

## SYSTEM

You are a lexicographer for English learners. Given the full episode script and a list of
candidate words with their CEFR levels (from a word list; "UNK" = not in list), select the
{{VOCAB_N}} most useful items for a {{LEVEL}} learner and write a glossary.

Rules:
- Prefer words that are (1) essential to the topic, (2) B1–C1, (3) used ≥2 times or at a key moment.
- Definitions in plain English (A2 level), one sentence, no circular definitions.
- Give British IPA. Include part of speech, CEFR (if UNK, estimate and mark "~B2").
- Add one learner-friendly collocation.
- Also return 5 "bonus" C1–C2 words for the PDF appendix only (not shown in video).

## USER

SCRIPT (turns):
{{TURNS_TEXT}}

CANDIDATES (word, count, cefr):
{{CANDIDATES_CSV}}

Return ONLY JSON:
{"glossary":[{"word":"","pos":"","cefr":"","ipa":"","definition":"","collocation":"","example":"","first_turn":0}],
 "bonus_c1_c2":[{"word":"","cefr":"","definition":""}]}

## Transkript PDF tarkibi (generator `make_pdf.py` uchun)

1. Muqova: sarlavha, epizod raqami, sana, QR → YouTube havolasi.
2. "Before you listen": 3 savol + lug'atning 10 so'zi (faqat so'z va CEFR).
3. To'liq transkript: boshlovchi ismi qalin, bo'lim sarlavhalari, lug'at so'zlari **qalin**.
4. Glossary jadvali: word | POS | CEFR | IPA | definition | example.
5. "After you listen": comprehension 5 savol + challenge.
6. Bonus C1–C2 words.
