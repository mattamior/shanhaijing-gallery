# 山海经 · 异兽图鉴

《山海经》异兽形象画廊：网格展示已出图 / 待出图，点开看大图、出处与短简介。纯静态站点，GitHub Pages 托管。

**在线访问：** https://mattamior.github.io/shanhaijing-gallery/

仓库：https://github.com/mattamior/shanhaijing-gallery

## 本地预览

```bash
# 从 CSV + assets 重建 data/creatures.json（需要 pypinyin）
python3 -m venv .venv && .venv/bin/pip install pypinyin
.venv/bin/python scripts/build_creatures.py

python3 -m http.server 8766
```

浏览器打开：http://localhost:8766

## 目录结构

```
assets/creatures/<slug>/
  art.jpg          # 竖版 3:4 出图（建议 ≥768×1024）
  meta.json        # 可选：覆盖名称/出处/简介/状态
  anim/            # 可选：L3 序列帧 f01.jpg… 或 sheet + meta.json
data/creatures.json
source/creatures.csv
scripts/build_creatures.py
scripts/slug-map.json   # 构建时生成的 中文名→slug 表
```

## 给美术专家的上图约定

1. **slug**：用拼音（应龙 → `yinglong`）。完整对照见构建后的 `scripts/slug-map.json`；高优先级与罕见字在 `scripts/build_creatures.py` 的 `SLUG_OVERRIDES` 里维护。
2. **落盘路径**：`assets/creatures/<slug>/art.jpg`（覆盖即更新）。
3. **可选 meta.json**（同目录），字段均可选：

```json
{
  "name": "应龙",
  "volume": "大荒东经 / 大荒北经",
  "blurb": "有翼之龙。助黄帝杀蚩尤与夸父，处南极；旱时仿其形，乃得大雨。",
  "source": "《山海经·大荒东经》 / 《大荒北经》",
  "status": "ready",
  "holoUrl": "https://mattamior.github.io/holo-card/all-in-one/#lv=5&focus=yinglong"
}
```

- 无 `meta.json` 时：简介由 CSV 的外形+本事拼短句；出处为 `《山海经·{篇目}》`。
- **文案边界**：只写典籍能站住的事迹与出处；白金羽翼等经文未写内容勿写进 `blurb`（可写在画风备注，不进卡面短文）。
4. **画风**：见项目画风规范 v4（电影 CG、竖版 3:4、无字无水印）。锁定样张只作质感锚点，不套龙外形到其他兽。
5. **上线**：放入 `art.jpg`（+ 可选 meta）后跑 `scripts/build_creatures.py`，提交 `assets/` 与 `data/creatures.json` 推 `main`。Pages 约 1–2 分钟生效。

### 工作区同步（可选）

开发机上也可先落到共享目录再拷进仓：

`/workspace/shanhaijing-gallery-assets/creatures/<slug>/{art.jpg,meta.json}`

→ 拷贝到本仓 `assets/creatures/<slug>/` 后重建 JSON。



## 4:3 横版母图 → 3:4 展示裁切

美术可交 **4:3 横版** `art.jpg` 或 `art-4x3.jpg`。网格与详情的展示框仍是 **3:4**，用 CSS `object-fit: cover` + `object-position` 按焦点裁，不另存竖版文件。

`meta.json` 例：

```json
{
  "art": "art-4x3.jpg",
  "aspect": "4:3",
  "crop": { "focusX": 0.5, "focusY": 0.45, "zoom": 1.0 }
}
```

- `art`：选用的文件名（默认先 `art.jpg` 再 `art-4x3.jpg`）
- `aspect: "4:3"`：启用横版→竖框裁切；**竖图（如应龙现有 3:4）不要写 `aspect: "4:3"`**，不强制裁
- `crop.focusX` / `focusY`：0–1，焦点；`zoom`：≥1 轻微放大

闪卡（holo-card）应龙插画窗按 **4:3 横版 contain** 显示母图，与图鉴竖裁分流。

## 应龙 L3 序列帧（`anim/`）

与 holo-card 共用投放目录：

`/workspace/shanhaijing-gallery-assets/creatures/yinglong/anim/`

```
f01.jpg … fNN.jpg     # 或
sheet.webp + meta.json
meta.json 例：{"frames":12,"fps":8,"cols":4,"rows":3,"size":[960,540]}
```

同步进本仓并重建 JSON：

```bash
python3 /workspace/aio/sync-yinglong-anim.py
python3 scripts/build_creatures.py   # 或 .venv/bin/python …
```

详情页若 `creatures.json` 含 `anim.frames > 0`，会自动循环播放；否则显示静帧 `art.jpg`。

## 筛选

- 篇目（南山经、西山经…大荒诸经等）
- 优先级（高 / 中 / 低）
- 仅已出图
- 名称 / 出处搜索

详情可用 hash：`#/yinglong`。

## 授权与引用

经文内容公有领域；现代译注与本站代码按仓库惯例。卡面 CG 为项目原创资产。

## Agnir Project Instructions

This section is a **backward-compatible locator only**. Canonical Agnir activation and Project-operation instructions live in [`AGNIR.md`](./AGNIR.md). Do not duplicate or fork that procedure here.

Fresh activation path: `AGENTS.md` → `AGNIR.md` → `AGNIR.yaml` → declared `.agnir/` memory.
