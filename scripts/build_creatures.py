#!/usr/bin/env python3
"""Build data/creatures.json from source CSV + assets/creatures/<slug>/."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

try:
    from pypinyin import Style, lazy_pinyin
except ImportError:
    lazy_pinyin = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "source" / "creatures.csv"
SLUG_MAP_PATH = Path(__file__).resolve().parent / "slug-map.json"
ASSETS = ROOT / "assets" / "creatures"
OUT = ROOT / "data" / "creatures.json"

# Manual overrides: Chinese display name → slug (maintain for Top / 高优先级)
# Rare glyphs that pypinyin cannot romanize also live here.
SLUG_OVERRIDES: dict[str, str] = {
    "应龙": "yinglong",
    "九尾狐": "jiuweihu",
    "凤凰（凤皇）": "fenghuang",
    "帝江（帝鸿/混沌）": "dijiang",
    "西王母": "xiwangmu",
    "狍鸮（饕餮）": "paoxiao",
    "穷奇（西山）": "qiongqi-xishan",
    "窫窳（北山）（窥窳）": "yayu-beishan",
    "肥遗（蛇）（肥䗷）": "feiyi-she",
    "蛮蛮（比翼）（比翼鸟）": "manman",
    "英招（招司）": "yingzhao",
    "驳（駮）": "bo",
    "山𤞤（山猨/山嗘）": "shanhu",
    "䳋䳅（𪁺𩿧）": "zhizhi",
    "䍺": "huan-wukou",
    "鸓": "lei-shuangshou",
    "䂿𥕿": "tatian",
    "䍶䍶": "tongtong",
    "䴅": "fen-niao",
    "𪄀𪃑": "qiqi",
    "㺨": "si-quan",
    "䴦": "hao-renmu",
    "㔮": "nuo-shu",
}


def primary_name(name: str) -> str:
    primary = re.split(r"[（(]", name, maxsplit=1)[0].strip()
    primary = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", primary)
    if not primary:
        primary = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", name)
    return primary


def auto_slug(name: str) -> str:
    if lazy_pinyin is None:
        raise SystemExit("pypinyin required: pip install pypinyin")
    primary = primary_name(name)
    py = "".join(lazy_pinyin(primary, style=Style.NORMAL))
    py = re.sub(r"[^a-z0-9]", "", py.lower())
    return py or "creature"


def make_blurb(appearance: str, ability: str) -> str:
    parts = []
    a = (appearance or "").strip().rstrip("。；;")
    b = (ability or "").strip().rstrip("。；;")
    if a:
        parts.append(a)
    if b and b not in a:
        parts.append(b)
    text = "；".join(parts)
    if len(text) > 80:
        text = text[:78] + "…"
    return text + "。" if text and not text.endswith("。") else text



def detect_anim(slug: str):
    """Return anim manifest for assets/creatures/<slug>/anim/ or None."""
    root = ASSETS / slug / "anim"
    if not root.is_dir():
        return None
    meta_path = root / "meta.json"
    meta = {}
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"warn: bad anim meta {meta_path}: {e}", file=sys.stderr)

    fps = int(meta.get("fps") or 8)
    raw_frames = meta.get("frames")
    if isinstance(raw_frames, list) and raw_frames:
        urls = []
        for name in raw_frames:
            p = root / str(name)
            if p.is_file():
                urls.append(f"assets/creatures/{slug}/anim/{p.name}")
        if urls:
            return {
                "format": "sequence",
                "frames": len(urls),
                "fps": fps,
                "urls": urls,
                "size": meta.get("size"),
                "status": meta.get("status"),
            }

    seq = sorted(root.glob("f*.jpg"))
    frame_n = int(raw_frames) if isinstance(raw_frames, int) else 0
    if not frame_n and seq:
        frame_n = len(seq)
    if frame_n > 0 and seq:
        return {
            "format": "sequence",
            "frames": frame_n,
            "fps": fps,
            "urls": [f"assets/creatures/{slug}/anim/f{str(i).zfill(2)}.jpg" for i in range(1, frame_n + 1)],
            "size": meta.get("size"),
            "status": meta.get("status"),
        }

    sheet = None
    for name in ("sheet.webp", "sheet.png", "sheet.jpg"):
        if (root / name).is_file():
            sheet = f"assets/creatures/{slug}/anim/{name}"
            break
    if sheet and meta.get("cols") and meta.get("rows") and frame_n > 0:
        return {
            "format": "sheet",
            "sheet": sheet,
            "frames": frame_n,
            "fps": fps,
            "cols": meta.get("cols"),
            "rows": meta.get("rows"),
            "size": meta.get("size"),
        }

    if meta.get("status") == "awaiting-art":
        return {"format": "sequence", "frames": 0, "fps": fps, "status": "awaiting-art"}
    return None



def resolve_art(slug: str, meta: dict):
    """Pick art file: meta.art → art.jpg → art-4x3.jpg."""
    root = ASSETS / slug
    names = []
    if meta.get("art"):
        names.append(str(meta["art"]))
    names.extend(["art.jpg", "art-4x3.jpg"])
    seen = set()
    for name in names:
        name = name.lstrip("./")
        if name in seen:
            continue
        seen.add(name)
        p = root / name
        if p.is_file():
            return f"assets/creatures/{slug}/{p.name}"
    return None


def normalize_crop(meta: dict):
    """Return {focusX, focusY, zoom} only when aspect is 4:3 (landscape master)."""
    aspect = str(meta.get("aspect") or "").replace(" ", "")
    if aspect not in ("4:3", "4/3"):
        return None, None  # vertical / unset → no forced crop
    crop = meta.get("crop") if isinstance(meta.get("crop"), dict) else {}
    out = {
        "focusX": float(crop.get("focusX", 0.5)),
        "focusY": float(crop.get("focusY", 0.45)),
        "zoom": float(crop.get("zoom", 1.0)),
    }
    # clamp
    out["focusX"] = max(0.0, min(1.0, out["focusX"]))
    out["focusY"] = max(0.0, min(1.0, out["focusY"]))
    out["zoom"] = max(1.0, min(3.0, out["zoom"]))
    return "4:3", out


def load_meta(slug: str) -> dict:
    meta_path = ASSETS / slug / "meta.json"
    if not meta_path.is_file():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"warn: bad meta {meta_path}: {e}", file=sys.stderr)
        return {}


def main() -> None:
    if not CSV_PATH.is_file():
        raise SystemExit(f"missing {CSV_PATH}")

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig")))
    used: dict[str, str] = {}
    slug_map: dict[str, str] = {}

    for row in rows:
        name = row["name"]
        if name in SLUG_OVERRIDES:
            slug = SLUG_OVERRIDES[name]
        else:
            slug = auto_slug(name)
        if slug in used and used[slug] != name:
            n = 2
            cand = f"{slug}-{n}"
            while cand in used:
                n += 1
                cand = f"{slug}-{n}"
            slug = cand
        used[slug] = name
        slug_map[name] = slug

    SLUG_MAP_PATH.write_text(
        json.dumps(slug_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    creatures = []
    ready_count = 0
    for row in rows:
        name = row["name"]
        slug = slug_map[name]
        meta = load_meta(slug)
        art = resolve_art(slug, meta)
        has_art = art is not None
        aspect, crop = normalize_crop(meta)

        status = meta.get("status") or ("ready" if has_art else "pending")
        if status == "ready" and not has_art:
            status = "pending"
        if status == "ready":
            ready_count += 1

        volume = meta.get("volume") or row["volume"]
        source = meta.get("source") or f"《山海经·{volume}》"
        blurb = meta.get("blurb") or make_blurb(row["appearance"], row["ability"])
        display_name = meta.get("name") or name

        entry = {
            "slug": slug,
            "name": display_name,
            "csvName": name,
            "volume": volume,
            "source": source,
            "blurb": blurb,
            "appearance": row["appearance"],
            "ability": row["ability"],
            "artKeywords": row["art_keywords"],
            "priority": row["priority"],
            "status": status,
            "art": art,
            "anim": detect_anim(slug),
            "holoUrl": meta.get("holoUrl")
            or (
                "https://mattamior.github.io/holo-card/all-in-one/#lv=5&focus=yinglong"
                if slug == "yinglong" and has_art
                else None
            ),
        }
        if aspect:
            entry["aspect"] = aspect
        if crop:
            entry["crop"] = crop
        creatures.append(entry)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(creatures),
        "ready": ready_count,
        "creatures": creatures,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({ready_count}/{len(creatures)} ready, {len(slug_map)} slugs)")


if __name__ == "__main__":
    main()
