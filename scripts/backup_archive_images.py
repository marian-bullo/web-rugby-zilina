#!/usr/bin/env python3
"""
Jednorazová záloha fotiek zo starých článkov (postimg.cc, ibb.co, wordpress.com)
do assets/archive/. Prepíše odkazy v data/posts*.json na lokálne súbory.
Spúšťa sa ručne cez GitHub Actions → "Záloha fotiek z archívu" → Run workflow.
"""
import glob
import os
import re

from common import INDEX, POSTS_DIR, load_json, save_image, save_json

EXT = re.compile(r"https?://(?:i\.postimg\.cc|i\.ibb\.co|[a-z0-9-]+\.wordpress\.com|i\d\.wp\.com)/[^\s\"'<>)]+", re.I)


def main():
    index = load_json(INDEX, [])
    mapping = {}
    for path in sorted(glob.glob(f"{POSTS_DIR}/*.json")):
        post = load_json(path, {})
        if post.get("source") != "archiv":
            continue
        slug = post["id"]
        html = post.get("html", "")
        urls = []
        for u in EXT.findall(html) + ([post["thumb"]] if post.get("thumb") else []):
            if re.search(r"\.(jpe?g|png|gif|webp)(\?|$)", u, re.I) and u not in urls:
                urls.append(u)
        print(f"{slug}: {len(urls)} fotiek")
        for n, u in enumerate(urls, 1):
            if u not in mapping:
                rel = save_image(u.split("?")[0] if "wordpress.com" in u else u, f"assets/archive/{slug}/{n:03d}.jpg", max_side=1280, quality=75)
                if rel:
                    mapping[u] = rel
        # odkazy na stránky postimg (nie na obrázok) odstránime, obrázok ostane
        html = re.sub(r'<a [^>]*href="https?://postimg\.cc/[^"]*"[^>]*>(.*?)</a>', r"\1", html, flags=re.S)
        for u, rel in mapping.items():
            html = html.replace(u, rel)
        post["html"] = html
        if post.get("thumb") in mapping:
            post["thumb"] = mapping[post["thumb"]]
        save_json(path, post)
    for p in index:
        if p.get("thumb") in mapping:
            p["thumb"] = mapping[p["thumb"]]
    save_json(INDEX, index, indent=1)
    print(f"Zálohovaných {len(mapping)} fotiek.")


if __name__ == "__main__":
    main()
