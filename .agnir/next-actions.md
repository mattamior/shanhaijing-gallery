# Next Actions — shanhaijing-gallery

Updated: 2026-10-20 (Asia/Shanghai)

1. Ingest new creatures as 美术专家 drops `assets/creatures/<slug>/{art.jpg,meta.json}` (4:3 mother); rebuild JSON.
2. When Yinglong L3 frames improve (true pose sequence, landscape matching `art.jpg`), sync anim folder + rebuild; keep Pages in sync.
3. Document/stabilize crop focus fields in meta if artists need non-center framing.
4. Keep placeholders for pending beasts; do not invent lore text.
5. Run `scripts/check_site.py` after every rebuild and before commit; keep README in sync with URL params / checks.
6. New non-BMP name glyphs: regenerate `assets/fonts/hanamin-b-rare.woff2` and its `unicode-range` (see `assets/fonts/README.md`); `check_site.py` fails until covered.
7. On material changes: checkpoint evaluation → commit `main` → push → verify Pages.
