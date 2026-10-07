"""Spoločné pomôcky pre skripty webu Žilina Bears."""
import io
import json
import os
import requests
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
POSTS_DIR = os.path.join(DATA, "posts")
INDEX = os.path.join(DATA, "posts.json")
UA = {"User-Agent": "ZilinaBearsWebBot/1.0 (+https://github.com)"}


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data, indent=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def save_image(url, dest_rel, max_side=1600, quality=78):
    """Stiahne obrázok, zmenší ho a uloží ako JPEG. Vráti relatívnu cestu alebo None."""
    dest = os.path.join(ROOT, dest_rel)
    if os.path.exists(dest):
        return dest_rel
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(r.content)))
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
        return dest_rel
    except Exception as e:  # noqa: BLE001 – jeden zlý obrázok nesmie zastaviť celý beh
        print(f"  ! obrázok sa nepodarilo stiahnuť: {url} ({e})")
        return None
