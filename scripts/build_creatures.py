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
        art_path = ASSETS / slug / "art.jpg"
        has_art = art_path.is_file()
        meta = load_meta(slug)

        status = meta.get("status") or ("ready" if has_art else "pending")
        if status == "ready" and not has_art:
            status = "pending"
        if status == "ready":
            ready_count += 1

        volume = meta.get("volume") or row["volume"]
        source = meta.get("source") or f"《山海经·{volume}》"
        blurb = meta.get("blurb") or make_blurb(row["appearance"], row["ability"])
        display_name = meta.get("name") or name

        creatures.append(
            {
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
                "art": f"assets/creatures/{slug}/art.jpg" if has_art else None,
                "holoUrl": meta.get("holoUrl")
                or (
                    "https://mattamior.github.io/holo-card/all-in-one/#lv=5&focus=yinglong"
                    if slug == "yinglong" and has_art
                    else None
                ),
            }
        )

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
