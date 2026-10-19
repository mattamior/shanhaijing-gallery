#!/usr/bin/env python3
"""Validate data/creatures.json against the files it references.

Run after scripts/build_creatures.py and before committing/pushing:

    .venv/bin/python scripts/check_site.py

Exit code 1 when any error is found. Warnings do not fail the run.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "creatures.json"
CSS = ROOT / "styles.css"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
UNICODE_RANGE_RE = re.compile(r"unicode-range:\s*([^;]+);", re.IGNORECASE)
STATUSES = {"ready", "pending"}
PRIORITIES = {"高", "中", "低"}
ASPECTS = {"4:3", "4/3"}

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def note(message: str) -> None:
    warnings.append(message)


def parse_unicode_ranges() -> set[int]:
    """Codepoints declared by @font-face unicode-range rules in styles.css."""
    if not CSS.is_file():
        return set()
    covered: set[int] = set()
    for match in UNICODE_RANGE_RE.finditer(CSS.read_text(encoding="utf-8")):
        for token in match.group(1).split(","):
            token = token.strip().upper()
            if token.startswith("U+"):
                token = token[2:]
            if not token:
                continue
            if "-" in token:
                low, high = token.split("-", 1)
                covered.update(range(int(low, 16), int(high, 16) + 1))
            else:
                covered.add(int(token, 16))
    return covered


def resolve(rel_path: str, label: str) -> Path | None:
    """Resolve a JSON path field, rejecting absolute/escaping paths."""
    if not isinstance(rel_path, str) or not rel_path.strip():
        fail(f"{label}: not a non-empty string")
        return None
    rel = rel_path.strip()
    if rel.startswith("./"):
        rel = rel[2:]
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        fail(f"{label}: path escapes repository root: {rel_path}")
        return None
    return path


def check_file(rel_path: str, label: str) -> bool:
    path = resolve(rel_path, label)
    if path is None:
        return False
    if not path.is_file():
        fail(f"{label}: missing file {rel_path}")
        return False
    if path.stat().st_size == 0:
        fail(f"{label}: empty file {rel_path}")
        return False
    return True


def check_number(value: object, low: float, high: float, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        fail(f"{label}: expected number, got {value!r}")
        return
    if not low <= value <= high:
        fail(f"{label}: out of range [{low}, {high}]: {value}")


def check_anim(slug: str, anim: object, label: str) -> int:
    if not isinstance(anim, dict):
        fail(f"{label}: expected object")
        return 0
    frames = anim.get("frames")
    if not isinstance(frames, int) or isinstance(frames, bool) or frames < 0:
        fail(f"{label}.frames: expected integer >= 0, got {frames!r}")
        return 0
    if frames == 0:
        return 0

    fps = anim.get("fps", 8)
    check_number(fps, 1, 60, f"{label}.fps")

    fmt = anim.get("format")
    if fmt == "sequence":
        urls = anim.get("urls")
        if not isinstance(urls, list) or not urls:
            fail(f"{label}.urls: required for sequence anim")
            return 0
        if len(urls) != frames:
            fail(f"{label}.urls: {len(urls)} entries, frames={frames}")
        for i, url in enumerate(urls):
            check_file(url, f"{label}.urls[{i}]")
        return len(urls)

    if fmt == "sheet":
        sheet = anim.get("sheet")
        if isinstance(sheet, str):
            check_file(sheet, f"{label}.sheet")
        for key in ("cols", "rows"):
            value = anim.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                fail(f"{label}.{key}: expected integer >= 1, got {value!r}")
        return 1

    fail(f"{label}.format: expected 'sequence' or 'sheet', got {fmt!r}")
    return 0


def main() -> int:
    if not DATA.is_file():
        print(f"error: missing {DATA}", file=sys.stderr)
        return 1
    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {DATA}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("error: data/creatures.json root must be an object", file=sys.stderr)
        return 1

    creatures = data.get("creatures")
    if not isinstance(creatures, list):
        print("error: creatures must be a list", file=sys.stderr)
        return 1

    slugs: set[str] = set()
    ready_count = 0
    art_count = 0
    anim_count = 0

    for index, creature in enumerate(creatures):
        label = f"creatures[{index}]"
        if not isinstance(creature, dict):
            fail(f"{label}: expected object")
            continue

        slug = creature.get("slug")
        if not isinstance(slug, str) or not SLUG_RE.match(slug):
            fail(f"{label}.slug: expected lowercase pinyin slug, got {slug!r}")
            continue
        label = f"creatures[{index}] ({slug})"
        if slug in slugs:
            fail(f"{label}: duplicate slug")
        slugs.add(slug)

        name = creature.get("name")
        if not isinstance(name, str) or not name.strip():
            fail(f"{label}.name: required")
        if not isinstance(creature.get("volume"), str) or not creature.get("volume"):
            fail(f"{label}.volume: required")

        status = creature.get("status")
        if status not in STATUSES:
            fail(f"{label}.status: expected one of {sorted(STATUSES)}, got {status!r}")
        priority = creature.get("priority")
        if priority not in PRIORITIES:
            fail(f"{label}.priority: expected one of {sorted(PRIORITIES)}, got {priority!r}")

        art = creature.get("art")
        if art:
            if check_file(art, f"{label}.art"):
                art_count += 1
        elif status == "ready":
            fail(f"{label}: status=ready but no art")

        aspect = creature.get("aspect")
        if aspect is not None:
            normalized = str(aspect).replace(" ", "")
            if normalized not in ASPECTS:
                fail(f"{label}.aspect: expected '4:3', got {aspect!r}")
            crop = creature.get("crop")
            if not isinstance(crop, dict):
                fail(f"{label}.crop: required when aspect is 4:3")
            else:
                check_number(crop.get("focusX", 0.5), 0, 1, f"{label}.crop.focusX")
                check_number(crop.get("focusY", 0.45), 0, 1, f"{label}.crop.focusY")
                check_number(crop.get("zoom", 1.0), 1, 3, f"{label}.crop.zoom")

        if status == "ready":
            ready_count += 1
            if not art:
                fail(f"{label}: status=ready but art is empty")

        anim = creature.get("anim")
        if anim is not None:
            anim_count += check_anim(slug, anim, f"{label}.anim")

    rare = {
        ord(ch)
        for creature in creatures
        if isinstance(creature, dict) and isinstance(creature.get("name"), str)
        for ch in creature["name"]
        if ord(ch) > 0xFFFF
    }
    covered = parse_unicode_ranges()
    for cp in sorted(rare - covered):
        fail(
            f"non-BMP name glyph U+{cp:05X} ({chr(cp)}) is not covered by "
            "@font-face unicode-range in styles.css; regenerate assets/fonts/hanamin-b-rare.woff2"
        )

    total = data.get("total")
    if total != len(creatures):
        fail(f"total: {total!r} does not match {len(creatures)} creatures")
    ready_field = data.get("ready")
    if ready_field != ready_count:
        fail(f"ready: {ready_field!r} does not match {ready_count} ready creatures")

    for message in warnings:
        print(f"warn: {message}", file=sys.stderr)
    if errors:
        for message in errors:
            print(f"error: {message}", file=sys.stderr)
        print(f"FAILED: {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(
        f"OK: {len(creatures)} creatures "
        f"({ready_count} ready), {art_count} art file(s), {anim_count} anim frame(s)/sheet(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
