# Current State — shanhaijing-gallery

Updated: 2026-10-22 (Asia/Shanghai)

## Project
《山海经》 creature gallery (dark cinematic static site). Live: https://mattamior.github.io/shanhaijing-gallery/

## Shipped
- Catalog ~198 entries from `source/creatures.csv` → `data/creatures.json` via `scripts/build_creatures.py`.
- Grid + detail hash routes (e.g. `#/yinglong`); ungenerated entries gray placeholder.
- **应龙** ready: `assets/creatures/yinglong/{art.jpg,meta.json,anim/}` with L3 loop @10fps when `anim.frames > 0`.
- **夔** ready (2026-10-20): `assets/creatures/kui/art-4x3.jpg` (4:3 mother, 1448×1086, AI-assisted redraw approved by Principal). Identity lock v2: bovine short blunt muzzle, no horns, 苍身 cold blue-grey, **one fin-shaped foot** (《大荒东经》「一足」), spiral curled tail, one continuous flat fringed dorsal fin neck→tail base, one pair of pectoral fin-fans, no hooves. Old twin-sheet lock kept as evidence at `.agnir/evidence/2026-10-12-kui-approved-kaimu-lock.png`.
- Art pipeline: 美术专家 delivers **landscape 4:3 mother** `art.jpg`; site crops **3:4** for grid/card using center or meta focus (`cropCenterX` / related fields as agreed).
- **䳋䳅** ready, corrected 2026-10-22 after Principal approval: `assets/creatures/zhizhi/art-4x3.jpg` (4:3 mother, 1448×1086; SHA-256 `dacefd4e7172ee219aae0578bdff096b1640a77ba3719cd8cf67bf7325402edc`). Three heads, six distinguishable legs/feet, three visible wing shapes (left/right + dorsal); four eyes visible, far-side eyes occluded, no extra eyes observed. Full mother has intact tips and margins. Earlier five-leg / extra-wing artwork and the 2026-10-20 sheet are historical only, not valid anatomy locks; see `.agnir/evidence/2026-10-22-zhizhi-corrected-qc.md`. Grid AND detail modal crop to 3:4, clipping lateral wing tips; neither is a full-mother preview.
- Yinglong card copy aligned to classics (see companion `/workspace/yinglong-card-copy.md` / gallery meta blurb).
- Shareable filter state: `?volume=&priority=&ready=1&q=`, composed with the detail hash; filter changes use `replaceState`.
- Detail modal focus management: Tab trap inside dialog, Esc/backdrop close, focus returns to the originating card.
- Canonical + Open Graph + Twitter card + JSON-LD on `index.html`.
- `scripts/check_site.py`: validates slugs, status/priority, art/anim file references, crop ranges, non-BMP name glyph coverage, and `total`/`ready` counts.
- Rare name glyphs: self-hosted HanaMinB subset `assets/fonts/hanamin-b-rare.woff2` (7 non-BMP chars, `unicode-range` fallback, OFL/Hanazono license included).
- Dark-theme controls: custom checkbox, accent `:focus-visible` rings on cards/buttons/inputs, brighter card meta / filter labels / footer for contrast.

## Constraints
- Local image generation is ruled out (Decisions 2026-10-20): no available local model both fits this 24GB Mac and runs under mflux; new art must come from an external image API or a human artist.

## Related Projects
- Holo preview: `mattamior/holo-card` `feature/all-in-one` (not bound as the gallery runtime).
- Style guide / lock art live under `/workspace/shanhaijing-*` workspace files owned by 美术专家.
