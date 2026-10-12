# Current State — shanhaijing-gallery

Updated: 2026-10-12 (Asia/Shanghai)

## Project
《山海经》 creature gallery (dark cinematic static site). Live: https://mattamior.github.io/shanhaijing-gallery/

## Shipped
- Catalog ~198 entries from `source/creatures.csv` → `data/creatures.json` via `scripts/build_creatures.py`.
- Grid + detail hash routes (e.g. `#/yinglong`); ungenerated entries gray placeholder.
- **应龙** ready: `assets/creatures/yinglong/{art.jpg,meta.json,anim/}` with L3 loop @10fps when `anim.frames > 0`.
- Art pipeline: 美术专家 delivers **landscape 4:3 mother** `art.jpg`; site crops **3:4** for grid/card using center or meta focus (`cropCenterX` / related fields as agreed).
- Yinglong card copy aligned to classics (see companion `/workspace/yinglong-card-copy.md` / gallery meta blurb).

## Withdrawn / pending redraw
- **夔** (`kui`): withdrawn from ready catalog — user not finalizing art (feels ugly); seeking new references. `assets/creatures/kui/` kept (`art-4x3.jpg` + crop meta); `meta.status=pending`, note `withdrawn pending redraw`. `data/creatures.json` ready count = 1 (应龙 only).

## Related Projects
- Holo preview: `mattamior/holo-card` `feature/all-in-one` (not bound as the gallery runtime).
- Style guide / lock art live under `/workspace/shanhaijing-*` workspace files owned by 美术专家.
