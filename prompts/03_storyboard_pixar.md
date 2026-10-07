# Prompt 03 — Storyboard va Pixar-uslub rasm promptlari

**Kirish:** `script.json` + `alignment.json` (har turn boshlanish vaqti).
**Chiqish:** `storyboard.json` — har 25–45 soniyaga 1 kadr; har kadr uchun rasm prompti.

## Doimiy uslub bloki (har promptga qo'shiladi)

STYLE_BLOCK =
"3D animated film still, Pixar / Disney animation style, soft global illumination, subsurface
scattering skin, expressive big eyes, warm cinematic color grading, shallow depth of field,
16:9 widescreen, ultra-detailed, no text, no captions, no watermark, no logos."

CHARACTER_BLOCK (character sheet asosida, `assets/characters/` dagi referens rasmlar bilan yuboriladi) =
"{{HOST_A_NAME}}: {{HOST_A_DESCRIPTION}}. {{HOST_B_NAME}}: {{HOST_B_DESCRIPTION}}.
Keep faces, hair, clothing and proportions identical to the reference images."

## SYSTEM (storyboard rejalashtiruvchi)

You are a storyboard artist for an animated educational podcast. Given the dialogue with
timestamps, plan one image every 25–45 seconds so that the picture changes at natural idea
boundaries (new example, new section, story moment). For each shot output:
- `t_start` (seconds), `t_end`, `turn_from`, `turn_to`
- `shot_type`: one of `hosts_two_shot | host_A_closeup | host_B_closeup | concept_scene | example_scene | story_flashback | vocab_card | recap_board`
- `scene`: 1–2 sentences describing a concrete, visual, story-like scene (NO abstract concepts; show a
  situation: "James at an airport check-in desk, frozen, thought bubble with tangled grammar")
- `camera`: e.g. "medium shot, eye level, 35mm"
- `mood`: 2–3 words
- `prompt`: STYLE_BLOCK + CHARACTER_BLOCK (only if hosts present) + scene + camera + lighting.
- `ken_burns`: "zoom_in | zoom_out | pan_left | pan_right"
Rules: ≥40% of shots must include at least one host; vary shot types; story segments use
`story_flashback` with a slightly desaturated palette; never show readable text in the image.

## USER

TURNS WITH TIMES:
{{TURNS_WITH_TIMES}}

Return ONLY JSON: {"shots":[...]}

## Rasm generatsiya eslatmalari

- Asosiy yo'l: Gemini API, `gemini-3.1-flash-image` (Nano Banana 2), `aspect_ratio: 16:9`,
  referens rasmlar (≤14) orqali personaj barqarorligi; 2K ≈ $0.10/rasm, 1K ≈ $0.07/rasm.
- Muqobil: Google Flow (flow.google.com) — rasmiy API yo'q; `gflow-cli` (norasmiy, Playwright
  brauzer sessiyasi) yoki useapi.net. Faqat "hero" kadrlar va Veo intro uchun tavsiya etiladi.
- Character sheet: har boshlovchi uchun 1 marta 4 ta rakurs (front, 3/4, profile, full body)
  yaratiladi va tasdiqlanadi; keyin barcha epizodlar shu referenslar bilan ishlaydi.
