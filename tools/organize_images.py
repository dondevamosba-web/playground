"""
Organize images in ~/Downloads into a clean folder structure with AI-generated names.

Modes:
  --dry-run [--limit N]  Print what would happen (no files moved)
  --execute [--batch N]  Move files in batches (default batch=200)

Output structure:
  ~/Downloads/organized/
    screenshots/YYYY-MM/
    whatsapp/YYYY-MM/
    photos/work/YYYY-MM/
    photos/holidays/YYYY-MM/
    photos/other/YYYY-MM/
    misc/YYYY-MM/

Filenames: YYYY-MM_descriptive-name.ext  (AI-generated for unclear names)
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

load_dotenv()

SOURCE_DIR = Path.home() / "Downloads"
DEST_DIR = Path.home() / "Downloads" / "organized"
PROGRESS_FILE = Path(__file__).parent.parent / ".tmp" / "organize_progress.json"
LARGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".tiff", ".tif", ".raw"}

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
_HASH_RE = re.compile(r"^[0-9a-f]{20,}$", re.I)
_IMG_NUM_RE = re.compile(r"^(IMG_\d+|\d+\.jpg|\d+\.heic|\d+)$", re.I)


def needs_ai_name(path: Path) -> bool:
    stem = path.stem
    if _UUID_RE.match(stem):
        return True
    if _HASH_RE.match(stem):
        return True
    if _IMG_NUM_RE.match(stem):
        return True
    if re.match(r"^\d+$", stem):
        return True
    # Long hex-like strings (e.g. Facebook IDs)
    if re.match(r"^[0-9A-F]{8}-", stem, re.I):
        return True
    # Unix timestamp filenames like 1682525027056-lg
    if re.match(r"^\d{10,}-", stem):
        return True
    return False


_geo_cache: dict[tuple, str | None] = {}


def _dms_to_dd(dms, ref: str) -> float:
    d, m, s = float(dms[0]), float(dms[1]), float(dms[2])
    dd = d + m / 60 + s / 3600
    if ref in ("S", "W"):
        dd = -dd
    return dd


def get_gps_coords(path: Path) -> tuple[float, float] | None:
    try:
        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            if TAGS.get(tag_id) == "GPSInfo":
                gps = {GPSTAGS.get(k, k): v for k, v in value.items()}
                lat = _dms_to_dd(gps["GPSLatitude"], gps["GPSLatitudeRef"])
                lon = _dms_to_dd(gps["GPSLongitude"], gps["GPSLongitudeRef"])
                return (lat, lon)
    except Exception:
        pass
    return None


def reverse_geocode(lat: float, lon: float) -> str | None:
    key = (round(lat, 3), round(lon, 3))
    if key in _geo_cache:
        return _geo_cache[key]
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=10"
        req = urllib.request.Request(url, headers={"User-Agent": "organize_images/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        addr = data.get("address", {})
        parts = [
            addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county"),
            addr.get("country_code", "").upper() or None,
        ]
        result = "-".join(p.lower().replace(" ", "-") for p in parts if p)
        result = re.sub(r"[^a-z0-9-]", "", result) or None
        _geo_cache[key] = result
        time.sleep(0.5)  # Nominatim rate limit: 1 req/sec
        return result
    except Exception:
        _geo_cache[key] = None
        return None


def get_location_tag(path: Path) -> str | None:
    coords = get_gps_coords(path)
    if coords:
        return reverse_geocode(*coords)
    return None


def get_exif_date(path: Path) -> datetime | None:
    try:
        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTimeOriginal":
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None
    return None


def get_filename_date(name: str) -> datetime | None:
    patterns = [
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{4})_(\d{2})_(\d{2})",
        r"(?<!\d)(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?!\d)",
    ]
    for pattern in patterns:
        m = re.search(pattern, name)
        if m:
            try:
                year = int(m.group(1))
                if year < 2000 or year > 2030:
                    continue
                return datetime(year, int(m.group(2)), int(m.group(3)))
            except ValueError:
                continue
    return None


def get_date(path: Path) -> datetime:
    d = get_exif_date(path)
    if d:
        return d
    d = get_filename_date(path.name)
    if d:
        return d
    return datetime.fromtimestamp(path.stat().st_mtime)


def classify_by_name(path: Path) -> str | None:
    name = path.name
    if "screenshot" in name.lower():
        return "screenshots"
    if "whatsapp" in name.lower():
        return "whatsapp"
    return None


def is_phone_photo(path: Path) -> bool:
    name = path.name.upper()
    return name.startswith("IMG_") or path.suffix.lower() == ".heic"


def _find_claude_bin() -> str:
    import shutil as _shutil
    found = _shutil.which("claude")
    if found:
        return found
    for p in sorted((Path.home() / ".vscode/extensions").rglob("claude"), reverse=True):
        if p.is_file() and p.stat().st_size > 1_000_000:
            return str(p)
    raise FileNotFoundError("claude CLI not found")


def _call_claude_vision(path: Path, prompt: str) -> str:
    ext = path.suffix.lower().lstrip(".")
    media_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                 "gif": "image/gif", "webp": "image/webp", "heic": "image/jpeg",
                 "tiff": "image/png", "tif": "image/png"}
    media_type = media_map.get(ext, "image/jpeg")

    with open(path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    message = json.dumps({
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                {"type": "text", "text": prompt}
            ]
        }
    })

    result = subprocess.run(
        [_find_claude_bin(), "--model", "claude-haiku-4-5-20251001",
         "--input-format", "stream-json", "--output-format", "stream-json", "--verbose", "-p"],
        input=message, capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    for line in result.stdout.strip().splitlines():
        try:
            evt = json.loads(line)
            if evt.get("type") == "result":
                return evt.get("result", "").strip()
        except json.JSONDecodeError:
            continue
    return ""


def get_ai_info(path: Path, need_category: bool) -> dict:
    """Returns {"category": str, "name": str} via one AI call."""
    try:
        if need_category:
            prompt = (
                'Respond with a JSON object only, no markdown. '
                'Keys: "category" (one of: work, holidays, other) and "name" '
                '(3-5 word kebab-case description of what is in the image, e.g. '
                '"sunset-beach-patagonia" or "office-meeting-whiteboard"). '
                'Example: {"category":"holidays","name":"sunset-beach-patagonia"}'
            )
        else:
            prompt = (
                'Respond with a JSON object only, no markdown. '
                'Key: "name" (3-5 word kebab-case description of what is in the image, '
                'e.g. "meta-ads-campaign-dashboard" or "client-exterior-painting"). '
                'Example: {"name":"meta-ads-campaign-dashboard"}'
            )

        raw = _call_claude_vision(path, prompt)
        # Strip markdown fences if present
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        data = json.loads(raw)

        name = re.sub(r"[^a-z0-9-]", "", data.get("name", "image").lower().replace(" ", "-").replace("_", "-"))
        name = re.sub(r"-+", "-", name).strip("-") or "image"

        category = data.get("category", "other")
        if category not in ("work", "holidays", "other"):
            category = "other"

        return {"category": category, "name": name}
    except Exception as e:
        print(f"  [AI error on {path.name}: {e}]", file=sys.stderr)
        return {"category": "other", "name": None}


def build_new_stem(path: Path, date: datetime, ai_name: str | None, location: str | None = None) -> str:
    date_prefix = date.strftime("%Y-%m")
    base = ai_name or (path.stem if not re.match(r"^\d{4}-\d{2}", path.stem) else None)
    parts = [date_prefix] + ([base] if base else []) + ([location] if location else [])
    return "_".join(parts)


def destination(path: Path, category: str, new_stem: str, is_large: bool) -> Path:
    month_folder = new_stem[:7]  # YYYY-MM
    if is_large:
        month_folder += "_large"
    filename = new_stem + path.suffix.lower()

    if category == "screenshots":
        return DEST_DIR / "screenshots" / month_folder / filename
    elif category == "whatsapp":
        return DEST_DIR / "whatsapp" / month_folder / filename
    elif category in ("work", "holidays", "other"):
        return DEST_DIR / "photos" / category / month_folder / filename
    else:
        return DEST_DIR / "misc" / month_folder / filename


def load_progress() -> set:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
        return set(data.get("done", []))
    return set()


def save_progress(done: set):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"done": list(done)}, f)


def collect_images() -> list[Path]:
    images = []
    for p in SOURCE_DIR.rglob("*"):
        if p.suffix.lower() in IMAGE_EXTENSIONS and DEST_DIR not in p.parents:
            images.append(p)
    return sorted(images)


def safe_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    n = 1
    while True:
        candidate = dest.parent / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def process_file(path: Path, execute: bool, done: set) -> dict:
    key = str(path)
    if key in done:
        return {"status": "skipped", "reason": "already processed"}

    try:
        date = get_date(path)
        is_large = path.stat().st_size > LARGE_SIZE_BYTES
        category = classify_by_name(path)
        ai_name = None

        use_ai = needs_ai_name(path) or is_phone_photo(path) or category == "screenshots"

        if category is None:
            if use_ai:
                info = get_ai_info(path, need_category=True)
                category = info["category"]
                ai_name = info["name"]
            else:
                category = "misc"
        elif use_ai:
            info = get_ai_info(path, need_category=False)
            ai_name = info["name"]

        location = get_location_tag(path)
        new_stem = build_new_stem(path, date, ai_name, location)
        dest = destination(path, category, new_stem, is_large)
        dest = safe_dest(dest)

        if execute:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(path), str(dest))
            path.unlink()
            done.add(key)

        return {"status": "ok", "src": str(path), "dest": str(dest),
                "category": category, "date": date.strftime("%Y-%m"), "large": is_large}

    except Exception as e:
        return {"status": "error", "src": str(path), "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch", type=int, default=200)
    args = parser.parse_args()

    images = collect_images()
    print(f"Found {len(images)} image files in {SOURCE_DIR}")

    if args.dry_run:
        sample = images[:args.limit] if args.limit else images
        print(f"\nDry run on {len(sample)} files:\n")
        print(f"{'SOURCE':<55} {'→ DEST':<75} {'CAT':<10}")
        print("-" * 145)
        for path in sample:
            result = process_file(path, execute=False, done=set())
            if result["status"] == "ok":
                src_short = str(path).replace(str(Path.home()), "~")
                dest_short = result["dest"].replace(str(Path.home()), "~")
                print(f"{src_short:<55} {dest_short:<75} {result['category']:<10}")
            else:
                print(f"ERROR: {result}")

    elif args.execute:
        done = load_progress()
        remaining = [p for p in images if str(p) not in done]
        print(f"{len(done)} already processed, {len(remaining)} remaining")

        batch = remaining[:args.batch]
        errors, moved = 0, 0

        for i, path in enumerate(batch, 1):
            result = process_file(path, execute=True, done=done)
            if result["status"] == "ok":
                moved += 1
                dest_name = Path(result["dest"]).name
                print(f"[{i}/{len(batch)}] {result['category']:10} {dest_name}")
            elif result["status"] == "error":
                errors += 1
                print(f"[{i}/{len(batch)}] ERROR: {result['error']} — {path.name}")

            if i % 25 == 0:
                save_progress(done)

        save_progress(done)
        print(f"\nDone. Moved: {moved}, Errors: {errors}, Remaining: {len(remaining) - len(batch)}")
        if len(remaining) > args.batch:
            print(f"Run again to process the next batch of up to {args.batch}.")


if __name__ == "__main__":
    main()
