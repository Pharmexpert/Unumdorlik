# Character sheet promptlari (Flow / Nano Banana / AI Studio)

Har boshlovchi uchun 4 ta rasm, **1:1** (sheet) yoki **16:9** — fayl nomlari pastda. Avval `_front` ni yarating,
tasdiqlang, so'ng qolgan 3 tasini o'sha rasmni referens ("Ingredient") qilib yarating — shunda yuz bir xil chiqadi.

## STYLE (har promptga qo'shiladi)
3D animated character design, Pixar / Disney animation style, soft global illumination, subsurface scattering skin,
expressive big eyes, warm cinematic color grading, clean neutral light-grey studio background, no text, no watermark, no logo.

## Mia (HOST_A — teacher)
Asos: a woman in her early 30s, shoulder-length dark wavy hair, round glasses, mustard-yellow cardigan over a white
t-shirt, kind confident smile, small gold earrings.

| Fayl | Prompt qo'shimchasi |
|---|---|
| `mia_front.png` | front view, head and shoulders, looking at camera, friendly smile |
| `mia_34.png` | three-quarter view, head and shoulders, explaining with one hand raised, warm expression |
| `mia_profile.png` | side profile view, head and shoulders, listening thoughtfully |
| `mia_full.png` | full body, standing, relaxed pose, holding a small notebook, dark jeans, white sneakers |

## James (HOST_B — learner)
Asos: a man in his late 20s, short curly brown hair, light stubble, navy-blue hoodie, expressive eyebrows, curious
open smile, slightly playful energy.

| Fayl | Prompt qo'shimchasi |
|---|---|
| `james_front.png` | front view, head and shoulders, looking at camera, curious smile |
| `james_34.png` | three-quarter view, head and shoulders, surprised "oh I see it now" expression |
| `james_profile.png` | side profile view, head and shoulders, listening and nodding |
| `james_full.png` | full body, standing, hands in hoodie pocket, light jeans, white sneakers |

## Birgalikda (ixtiyoriy, thumbnail/intro uchun)
`hosts_two_shot.png` — Mia and James side by side at a cozy podcast table with two microphones, warm wooden studio
with bookshelves and a plant, both looking at camera, 16:9.

Tayyor fayllar `assets/characters/` ga qo'yilgach: `uv run unumdorlik doctor` → "character sheet OK".
`config` dagi `hosts.*.description` matni shu asoslar bilan bir xil bo'lishi kerak (05-bosqich promptlarida ishlatiladi).
