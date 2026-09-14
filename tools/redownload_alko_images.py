# -*- coding: utf-8 -*-
"""Re-download alko images with proper URL encoding; update parts.json paths."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "assets" / "data" / "parts.json"
RAW = ROOT / "assets" / "data" / "_alko_raw" / "catalog_scraped.json"
IMG_DIR = ROOT / "assets" / "img" / "alko"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HomebrewPartsMigrate/1.0"}


def encode_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def fetch(url: str) -> bytes:
    req = urllib.request.Request(encode_url(url), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main() -> None:
    parts = json.loads(PARTS.read_text(encoding="utf-8"))
    ok = fail = 0
    for sku_id, sku in parts["skus"].items():
        src = sku.get("sourceUrl")
        img_path = Path(sku.get("image") or "")
        dest = ROOT / img_path
        # rebuild dest from existing relative path even if placeholder
        if "placeholder" in str(img_path):
            # need original remote URL — look up by sourceUrl in raw + gasket names
            pass
        remote = None
        # Prefer stored remote if we add it; else derive from scrape by matching sourceUrl
        remote = sku.get("remoteImage")
        if not remote:
            continue
        try:
            full = re.sub(r"-\d+x\d+(\.(?:jpg|jpeg|png|webp))$", r"\1", remote, flags=re.I)
            data = fetch(full)
            if len(data) < 200:
                data = fetch(remote)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # fix extension from content? keep path
            if "placeholder" in str(dest):
                continue
            dest.write_bytes(data)
            ok += 1
        except Exception as e:
            fail += 1
            if fail < 5:
                print("fail", sku_id, e)
        if ok and ok % 25 == 0:
            print("ok", ok)
            time.sleep(0.2)
    print("done ok", ok, "fail", fail, "(needs remoteImage field)")


if __name__ == "__main__":
    # Better: re-run migrate with fixed fetch — patch parts from RAW by matching URL
    parts = json.loads(PARTS.read_text(encoding="utf-8"))
    raw_items = json.loads(RAW.read_text(encoding="utf-8"))
    # also load gaskets from parts sourceUrl matching
    by_url = {x["url"].rstrip("/"): x for x in raw_items}

    # gaskets may only be in parts — use image field from parts if we still have remote in scrape
    # Re-scrape gasket list quickly from product pages? Use WP featured from slim
    slim = json.loads((ROOT / "assets/data/_alko_raw/products_slim.json").read_text(encoding="utf-8"))
    slim_by_link = {(s.get("link") or "").rstrip("/"): s for s in slim}

    ok = fail = 0
    for sku_id, sku in parts["skus"].items():
        src = (sku.get("sourceUrl") or "").rstrip("/")
        remote = ""
        if src in by_url:
            remote = by_url[src].get("image") or ""
        if not remote and src in slim_by_link:
            remote = slim_by_link[src].get("image") or ""
        if not remote:
            # try with trailing slash variants
            remote = (by_url.get(src + "/") or {}).get("image") or remote
        if not remote:
            fail += 1
            print("no remote", sku_id, sku.get("name"))
            continue

        rel = sku["image"]
        if "placeholder" in rel:
            # invent filename from slug
            slug = sku.get("slug") or sku_id
            ext = ".jpg"
            path = urllib.parse.urlparse(remote).path
            e = Path(path).suffix.lower()
            if e in {".jpg", ".jpeg", ".png", ".webp"}:
                ext = ".jpg" if e == ".jpeg" else e
            rel = f"assets/img/alko/sku-{sku_id}-{slug}{ext}"
            sku["image"] = rel

        dest = ROOT / rel
        if dest.exists() and dest.stat().st_size > 500:
            ok += 1
            continue
        try:
            full = re.sub(r"-\d+x\d+(\.(?:jpg|jpeg|png|webp))$", r"\1", remote, flags=re.I)
            try:
                data = fetch(full)
            except Exception:
                data = fetch(remote)
            if len(data) < 200:
                raise RuntimeError("too small")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            ok += 1
        except Exception as e:
            fail += 1
            if fail <= 8:
                print("fail", sku_id, remote[:80], e)
        if ok % 30 == 0:
            print(f"progress ok={ok} fail={fail}")
            time.sleep(0.1)

    PARTS.write_text(json.dumps(parts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DONE images ok={ok} fail={fail}")
