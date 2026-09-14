# -*- coding: utf-8 -*-
"""One-time gather of alkotrademsk.ru catalog (name, price, image, category)."""
from __future__ import annotations

import html as html_lib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "data" / "_alko_raw"
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HomebrewPartsGather/1.0"}

# Top-level categories from site menu / shop (short labels for our UX)
CATEGORIES = [
    {
        "id": "fittings",
        "name": "Хомуты и царги",
        "url": "https://alkotrademsk.ru/product-category/%d1%85%d0%be%d0%bc%d1%83%d1%82%d1%8b-%d1%86%d0%b0%d1%80%d0%b3%d0%b8-%d0%b8-%d0%bf%d1%80%d0%be%d1%87%d0%b0%d1%8f-%d1%82%d1%80%d1%83%d0%b1%d0%be%d0%bf%d1%80%d0%be%d0%b2%d0%be%d0%b4%d0%bd%d0%b0%d1%8f/",
    },
    {
        "id": "lab",
        "name": "КИПиА и лаборатория",
        "url": "https://alkotrademsk.ru/product-category/%d0%ba%d0%be%d0%bd%d1%82%d1%80%d0%be%d0%bb%d1%8c%d0%bd%d0%be-%d0%b8%d0%b7%d0%bc%d0%b5%d1%80%d0%b8%d1%82%d0%b5%d0%bb%d1%8c%d0%bd%d0%be%d0%b5-%d0%b8-%d0%bb%d0%b0%d0%b1%d0%be%d1%80%d0%b0%d1%82%d0%be/",
    },
    {
        "id": "electro",
        "name": "Электрооборудование",
        "url": "https://alkotrademsk.ru/product-category/%d1%8d%d0%bb%d0%b5%d0%ba%d1%82%d1%80%d0%be%d0%be%d0%b1%d0%be%d1%80%d1%83%d0%b4%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5/",
    },
    {
        "id": "valves",
        "name": "Краны и переходники",
        "url": "https://alkotrademsk.ru/product-category/%d0%b4%d0%b8%d0%b2%d0%b5%d1%80%d1%82%d0%be%d1%80%d1%8b-%d0%ba%d1%80%d0%b0%d0%bd%d1%8b-%d0%bf%d0%b5%d1%80%d0%b5%d1%85%d0%be%d0%b4%d0%bd%d0%b8%d0%ba%d0%b8-%d0%b1%d1%8b%d1%81%d1%82%d1%80%d0%be%d1%81/",
    },
    {
        "id": "other",
        "name": "Прочее оборудование",
        "url": "https://alkotrademsk.ru/product-category/%d0%bf%d1%80%d0%be%d1%87%d0%b5%d0%b5-%d0%be%d0%b1%d0%be%d1%80%d1%83%d0%b4%d0%be%d0%b2%d0%b0%d0%bd%d0%b8%d0%b5/",
    },
    {
        "id": "hoses",
        "name": "Шланги",
        "url": "https://alkotrademsk.ru/product-category/%d1%88%d0%bb%d0%b0%d0%bd%d0%b3%d0%b8/",
    },
    {
        "id": "silicone",
        "name": "Силиконовые кольца",
        "url": "https://alkotrademsk.ru/product-category/%d1%81%d0%b8%d0%bb%d0%b8%d0%ba%d0%be%d0%bd%d0%be%d0%b2%d1%8b%d0%b5-%d0%ba%d0%be%d0%bb%d1%8c%d1%86%d0%b0/",
    },
    {
        "id": "accessories",
        "name": "Аксессуары",
        "url": "https://alkotrademsk.ru/product-category/%d0%b0%d0%ba%d1%81%d0%b5%d1%81%d1%81%d1%83%d0%b0%d1%80%d1%8b/",
    },
    {
        "id": "membranes",
        "name": "Мембраны",
        "url": "https://alkotrademsk.ru/product-category/%d0%bc%d0%b5%d0%bc%d0%b1%d1%80%d0%b0%d0%bd%d1%8b-%d0%be%d0%b1%d1%80%d0%b0%d1%82%d0%bd%d0%be%d0%be%d1%81%d0%bc%d0%be%d1%82%d0%b8%d1%87%d0%b5%d1%81%d0%ba%d0%b8%d0%b5/",
    },
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), r.headers


def clean_text(s: str) -> str:
    s = html_lib.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_price(block: str) -> str | None:
    # <span class="woocommerce-Price-amount amount">17,00&nbsp;<span class="woocommerce-Price-currencySymbol">₽</span></span>
    m = re.search(
        r'woocommerce-Price-amount[^>]*>\s*([\d\s]+[,.]?\d*)',
        block,
        re.I | re.S,
    )
    if not m:
        m = re.search(r"([\d\s]+[,.]?\d*)\s*(?:₽|&nbsp;₽|руб)", block)
    if not m:
        return None
    raw = m.group(1).replace("\xa0", " ").replace(" ", "").replace(",", ".")
    try:
        val = float(raw)
    except ValueError:
        return None
    if val == int(val):
        num = f"{int(val):,}".replace(",", " ")
    else:
        num = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
    return f"{num} ₽"


def scrape_category(cat: dict) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    page = 1
    while page <= 20:
        url = cat["url"] if page == 1 else cat["url"].rstrip("/") + f"/page/{page}/"
        try:
            html = fetch(url)
        except Exception as e:
            print(f"  fail page {page}: {e}")
            break
        # product cards: li.product or .product
        cards = re.findall(
            r'<li[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</li>',
            html,
            re.I | re.S,
        )
        if not cards:
            # Storefront sometimes uses div
            cards = re.findall(
                r'<div[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</div>\s*</div>',
                html,
                re.I | re.S,
            )
        if not cards and page == 1:
            # dump for debug
            (OUT / f"debug_{cat['id']}.html").write_text(html, encoding="utf-8")
            print(f"  no cards, dumped debug_{cat['id']}.html")
            break
        if not cards:
            break

        added = 0
        for card in cards:
            href_m = re.search(r'href="(https://alkotrademsk.ru/product/[^"]+)"', card)
            if not href_m:
                continue
            href = href_m.group(1).split("?")[0]
            if href in seen:
                continue
            title_m = re.search(
                r'class="[^"]*woocommerce-loop-product__title[^"]*"[^>]*>(.*?)</',
                card,
                re.I | re.S,
            )
            if not title_m:
                title_m = re.search(r"<h2[^>]*>(.*?)</h2>", card, re.I | re.S)
            if not title_m:
                title_m = re.search(r"<h3[^>]*>(.*?)</h3>", card, re.I | re.S)
            name = clean_text(title_m.group(1) if title_m else "")
            if not name:
                # last resort: link text after product url
                tm = re.search(
                    rf'href="{re.escape(href)}"[^>]*>([^<]{{3,160}})<',
                    card,
                )
                name = clean_text(tm.group(1) if tm else "")
            img_m = re.search(r'<img[^>]+(?:src|data-src)="([^"]+)"', card, re.I)
            img = img_m.group(1) if img_m else ""
            if img.startswith("data:"):
                img_m2 = re.search(r'data-large_image="([^"]+)"', card)
                img = img_m2.group(1) if img_m2 else img
            price = parse_price(card) or ""
            seen.add(href)
            items.append(
                {
                    "category_id": cat["id"],
                    "category": cat["name"],
                    "name": name,
                    "price": price,
                    "image": img,
                    "url": href,
                }
            )
            added += 1
        print(f"  {cat['id']} page {page}: +{added} (total {len(items)})")
        # pagination check
        if f"/page/{page + 1}/" not in html and f"page/{page + 1}" not in html:
            # also check next link
            if not re.search(rf'page/{page + 1}/?', html):
                break
        page += 1
        time.sleep(0.35)
    return items


def load_wp_products() -> dict[str, dict]:
    """Map product URL -> image/excerpt from WP REST (already gathered or fetch)."""
    slim_path = OUT / "products_slim.json"
    if slim_path.exists():
        slim = json.loads(slim_path.read_text(encoding="utf-8"))
    else:
        slim = []
        page = 1
        while page <= 10:
            url = f"https://alkotrademsk.ru/wp-json/wp/v2/product?per_page=100&page={page}&_embed=1"
            data, headers = fetch_json(url)
            slim_page = []
            for p in data:
                title = clean_text(p.get("title", {}).get("rendered", ""))
                content = clean_text(p.get("content", {}).get("rendered", ""))[:400]
                img = ""
                media = (p.get("_embedded") or {}).get("wp:featuredmedia") or []
                if media:
                    img = media[0].get("source_url") or ""
                yoast = p.get("yoast_head_json") or {}
                og = (yoast.get("og_image") or [{}])[0]
                if not img:
                    img = og.get("url") or ""
                slim_page.append(
                    {
                        "id": p["id"],
                        "slug": urllib.parse.unquote(p.get("slug", "")),
                        "title": title,
                        "link": p.get("link"),
                        "image": img,
                        "excerpt": content,
                    }
                )
            slim.extend(slim_page)
            pages = int(headers.get("X-WP-TotalPages") or 1)
            print(f"WP page {page}/{pages}: {len(slim_page)}")
            if page >= pages:
                break
            page += 1
            time.sleep(0.2)
        slim_path.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")

    by_url: dict[str, dict] = {}
    for s in slim:
        link = (s.get("link") or "").rstrip("/") + "/"
        by_url[link] = s
        by_url[link.rstrip("/")] = s
    return by_url


def main() -> None:
    wp = load_wp_products()
    print("WP products indexed:", len(wp) // 2)

    all_items: list[dict] = []
    for cat in CATEGORIES:
        print("Category:", cat["name"])
        items = scrape_category(cat)
        for it in items:
            key = it["url"].rstrip("/") + "/"
            meta = wp.get(key) or wp.get(it["url"].rstrip("/")) or {}
            if not it.get("image") and meta.get("image"):
                it["image"] = meta["image"]
            if meta.get("excerpt"):
                it["excerpt"] = meta["excerpt"]
            if meta.get("id"):
                it["wp_id"] = meta["id"]
            # Prefer larger image from WP
            if meta.get("image") and ("-300x300" in (it.get("image") or "") or not it.get("image")):
                it["image"] = meta["image"]
        all_items.extend(items)
        time.sleep(0.4)

    # Dedupe by URL (product can appear in parent+child)
    dedup: dict[str, dict] = {}
    for it in all_items:
        u = it["url"].rstrip("/")
        if u not in dedup:
            dedup[u] = it
        else:
            # keep first category assignment; fill missing price/image
            cur = dedup[u]
            if not cur.get("price") and it.get("price"):
                cur["price"] = it["price"]
            if not cur.get("image") and it.get("image"):
                cur["image"] = it["image"]

    final = list(dedup.values())
    # Prefer items with prices
    with_price = sum(1 for x in final if x.get("price"))
    print(f"TOTAL unique: {len(final)}, with price: {with_price}")

    (OUT / "categories.json").write_text(
        json.dumps(CATEGORIES, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "catalog_scraped.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Wrote", OUT / "catalog_scraped.json")


if __name__ == "__main__":
    main()
