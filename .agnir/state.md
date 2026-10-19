# Current State — shanhaijing-gallery

Updated: 2026-10-19 (Asia/Shanghai)

## Project
《山海经》 creature gallery (dark cinematic static site). Live: https://mattamior.github.io/shanhaijing-gallery/

## Shipped
- Catalog ~198 entries from `source/creatures.csv` → `data/creatures.json` via `scripts/build_creatures.py`.
- Grid + detail hash routes (e.g. `#/yinglong`); ungenerated entries gray placeholder.
- **应龙** ready: `assets/creatures/yinglong/{art.jpg,meta.json,anim/}` with L3 loop @10fps when `anim.frames > 0`.
- Art pipeline: 美术专家 delivers **landscape 4:3 mother** `art.jpg`; site crops **3:4** for grid/card using center or meta focus (`cropCenterX` / related fields as agreed).
- Yinglong card copy aligned to classics (see companion `/workspace/yinglong-card-copy.md` / gallery meta blurb).
- Shareable filter state: `?volume=&priority=&ready=1&q=`, composed with the detail hash; filter changes use `replaceState`.
- Detail modal focus management: Tab trap inside dialog, Esc/backdrop close, focus returns to the originating card.
- Canonical + Open Graph + Twitter card + JSON-LD on `index.html`.
- `scripts/check_site.py`: validates slugs, status/priority, art/anim file references, crop ranges, and `total`/`ready` counts.

## Withdrawn / pending redraw
- **夔** (`kui`): still `pending` / withdrawn from ready catalog. **Identity lock set 2026-10-12**: Principal-approved Kai Mu twin sheet at `.agnir/evidence/2026-10-12-kui-approved-kaimu-lock.png` and `/workspace/shanhaijing-refs/kui/user-approved-kaimu-lock.png`. Redraw brief: match that twin look; mid-flank continuous flat foldable board-fin (shoulder→near tail), not a swollen ridge; no extra front/belly fins; no horns/hooves drift. Prior `assets/creatures/kui/` art retained on disk but must not be re-promoted until lock match. Ready count remains 1 (应龙 only).

## Related Projects
- Holo preview: `mattamior/holo-card` `feature/all-in-one` (not bound as the gallery runtime).
- Style guide / lock art live under `/workspace/shanhaijing-*` workspace files owned by 美术专家.
