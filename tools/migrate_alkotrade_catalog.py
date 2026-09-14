# -*- coding: utf-8 -*-
"""Migrate alkotrade scrape → archive old SKUs, build parts.json + download images."""
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "data" / "_alko_raw" / "catalog_scraped.json"
PARTS = ROOT / "assets" / "data" / "parts.json"
ARCHIVE = ROOT / "assets" / "data" / "archive-sku-old.json"
IMG_DIR = ROOT / "assets" / "img" / "alko"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HomebrewPartsMigrate/1.0"}

CATEGORIES = [
    {"id": "fittings", "name": "Хомуты и царги"},
    {"id": "valves", "name": "Краны и переходники"},
    {"id": "lab", "name": "КИПиА и лаборатория"},
    {"id": "other", "name": "Прочее оборудование"},
    {"id": "electro", "name": "Электрооборудование"},
    {"id": "hoses", "name": "Шланги"},
    {"id": "membranes", "name": "Мембраны"},
    {"id": "silicone", "name": "Прокладки и уплотнения"},
]


def encode_url(url: str) -> str:
    """Percent-encode path for Cyrillic filenames (urllib needs ASCII URL)."""
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def fetch(url: str) -> bytes:
    req = urllib.request.Request(encode_url(url), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_text(url: str) -> str:
    return fetch(url).decode("utf-8", errors="replace")

def clean(s: str) -> str:
    s = html_lib.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_price(block: str) -> str:
    m = re.search(r"woocommerce-Price-amount[^>]*>\s*([\d\s]+[,.]?\d*)", block, re.I | re.S)
    if not m:
        return ""
    raw = m.group(1).replace("\xa0", " ").replace(" ", "").replace(",", ".")
    try:
        val = float(raw)
    except ValueError:
        return ""
    if val == int(val):
        num = f"{int(val):,}".replace(",", " ")
    else:
        num = f"{val:.2f}".replace(".", ",")
    return f"{num} ₽"


def scrape_extra_gaskets() -> list[dict]:
    """Silicone clamp gaskets live under fittings subcategory."""
    url = (
        "https://alkotrademsk.ru/product-category/"
        "%d1%81%d0%b8%d0%bb%d0%b8%d0%ba%d0%be%d0%bd%d0%be%d0%b2%d0%b0%d1%8f-"
        "%d0%bf%d1%80%d0%be%d0%ba%d0%bb%d0%b0%d0%b4%d0%ba%d0%b0-%d0%bf%d0%be%d0%b4-%d0%ba%d0%bb%d0%b0%d0%bc%d0%bf/"
    )
    try:
        page = fetch_text(url)
    except Exception as e:
        print("gasket scrape fail", e)
        return []
    cards = re.findall(r'<li[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</li>', page, re.I | re.S)
    items = []
    for card in cards:
        href_m = re.search(r'href="(https://alkotrademsk.ru/product/[^"]+)"', card)
        if not href_m:
            continue
        href = href_m.group(1).split("?")[0]
        title_m = re.search(
            r'class="[^"]*woocommerce-loop-product__title[^"]*"[^>]*>(.*?)</',
            card,
            re.I | re.S,
        )
        if not title_m:
            title_m = re.search(r"<h2[^>]*>(.*?)</h2>", card, re.I | re.S)
        name = clean(title_m.group(1) if title_m else "")
        img_m = re.search(r'<img[^>]+(?:src|data-src)="([^"]+)"', card, re.I)
        img = img_m.group(1) if img_m else ""
        price = parse_price(card)
        items.append(
            {
                "category_id": "silicone",
                "category": "Прокладки и уплотнения",
                "name": name,
                "price": price,
                "image": img,
                "url": href,
                "excerpt": "",
            }
        )
    print(f"extra gaskets: {len(items)}")
    return items


def slugify(name: str) -> str:
    s = name.lower()
    s = s.replace("″", "in").replace("\"", "in").replace("«", "").replace("»", "")
    trans = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    out = []
    for ch in s:
        if ch in trans:
            out.append(trans[ch])
        elif ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug[:48] or "item"


def pick_facts(item: dict) -> list[dict]:
    name = item["name"].lower()
    cat = item["category_id"]
    price = item.get("price") or ""

    facts: list[tuple[str, str]] = []

    def add(icon: str, text: str) -> None:
        if len(facts) >= 3:
            return
        text = text[:28]
        if any(t == text for _, t in facts):
            return
        facts.append((icon, text))

    # size / DN
    m = re.search(r"dn\s*([0-9]+(?:[.,][0-9]+)?)", name, re.I)
    if m:
        add("size", f"DN {m.group(1).replace('.', ',')}")
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:″|\"|дюйм)", name, re.I)
    if m:
        add("size", f"{m.group(1).replace('.', ',')}″")
    m = re.search(r"(\d+)\s*мм", name, re.I)
    if m:
        add("size", f"Ø {m.group(1)} мм")
    m = re.search(r"(\d+)\s*мл", name, re.I)
    if m:
        add("volume", f"{m.group(1)} мл")
    m = re.search(r"(\d+)\s*л\b", name, re.I)
    if m:
        add("volume", f"{m.group(1)} л")
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*квт", name, re.I)
    if m:
        add("power", f"{m.group(1)} кВт")

    if "aisi" in name or "304" in name or "нерж" in name:
        add("steel", "AISI 304")
    if "силикон" in name:
        add("gasket", "силикон")
    if "кламп" in name:
        add("clamp", "кламп")
    if "термо" in name:
        add("temp", "термометрия")
    if "кран" in name or "игольч" in name:
        add("needle", "регулировка")
    if "шланг" in name:
        add("hose", "шланг")
    if "мембран" in name:
        add("seal", "обратный осмос")
    if "стекл" in name:
        add("glass", "стекло")
    if "пластик" in name:
        add("packing", "пластик")

    if cat == "fittings":
        add("steel", "пищевая сталь")
        add("clamp", "арматура")
        add("seal", "для колонны")
    elif cat == "valves":
        add("tap", "быстрый съём")
        add("steel", "нерж.")
        add("hose", "контур")
    elif cat == "lab":
        add("glass", "измерения")
        add("temp", "контроль")
        add("packing", "лаборатория")
    elif cat == "electro":
        add("power", "220 В")
        add("temp", "электроника")
        add("seal", "комплект")
    elif cat == "hoses":
        add("hose", "пищевой")
        add("temp", "гибкий")
        add("size", "метр")
    elif cat == "membranes":
        add("seal", "Vontron")
        add("packing", "фильтрация")
        add("water", "вода")  # may not exist — fallback below
    elif cat == "silicone":
        add("gasket", "уплотнение")
        add("seal", "герметичность")
        add("clamp", "под кламп")
    elif cat == "other":
        add("packing", "комплектация")
        add("steel", "для аппарата")
        add("seal", "расходник")

    if price:
        add("seal", "в наличии")

    # ensure exactly 3 with valid icons that exist in sprite
    valid = {
        "volume", "lid", "tap", "steel", "size", "gasket", "clamp", "hose",
        "temp", "power", "glass", "packing", "needle", "quiet", "seal",
    }
    out = []
    for icon, text in facts:
        if icon not in valid:
            icon = "seal"
        out.append({"icon": icon, "text": text})
        if len(out) == 3:
            break
    while len(out) < 3:
        fillers = [
            {"icon": "seal", "text": "для дома"},
            {"icon": "packing", "text": "витрина"},
            {"icon": "steel", "text": "комплектация"},
        ]
        out.append(fillers[len(out)])
    return out[:3]


def pick_use(item: dict) -> str:
    name = item["name"]
    cat = item["category_id"]
    excerpt = (item.get("excerpt") or "").strip()
    if excerpt and len(excerpt) > 40:
        # first sentence-ish
        cut = re.split(r"(?<=[.!?])\s+", excerpt)[0]
        if 20 < len(cut) < 180:
            return cut.rstrip(".") + "."

    templates = {
        "fittings": f"Узел трубопроводной арматуры: {name} — соединение и комплектация колонны/куба.",
        "valves": f"{name}: переключение потоков, отбор и быстросъём на контурах аппарата.",
        "lab": f"{name}: контроль плотности, температуры или объёма при домашнем производстве.",
        "electro": f"{name}: электроника и нагрев для стабильного процесса на домашней установке.",
        "hoses": f"{name}: контур охлаждения и переливы — пищевой шланг для домашней пивоварни/колонны.",
        "membranes": f"{name}: элемент очистки воды (обратный осмос) для подготовки к процессу.",
        "silicone": f"{name}: герметичность кламп-стыка — сменный расходник.",
        "other": f"{name}: дополнительная комплектация домашнего аппарата и ферментера.",
    }
    return templates.get(cat, f"{name}: комплектующее для домашнего оборудования.")


def ext_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    ext = Path(path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def download_image(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 500:
        return True
    try:
        data = fetch(url)
        if len(data) < 200:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print("  img fail", dest.name, e)
        return False


def main() -> None:
    old = json.loads(PARTS.read_text(encoding="utf-8"))
    old_skus = old.get("skus", {})
    modes = old.get("modes", {})

    # 1) Archive old catalog list
    archive = {
        "archived_at": "2026-09-15",
        "note": "Прежний каталог Homebrew Parts SKU 01–32 до миграции на витрину по данным alkotrademsk.ru. Схема аппарата (schema.html) продолжает ссылаться на эти позиции как архивные.",
        "disclaimer": old.get("disclaimer"),
        "skus": old_skus,
    }
    ARCHIVE.write_text(json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Archived", len(old_skus), "SKUs →", ARCHIVE)

    # 2) Load scrape + gaskets
    scraped = json.loads(RAW.read_text(encoding="utf-8"))
    extra = scrape_extra_gaskets()
    by_url: dict[str, dict] = {}
    for it in scraped + extra:
        u = it["url"].rstrip("/")
        # prefer silicone category if gasket
        if u in by_url and it["category_id"] != "silicone":
            continue
        by_url[u] = it
    items = list(by_url.values())
    # stable sort: category order then name
    cat_order = {c["id"]: i for i, c in enumerate(CATEGORIES)}
    items.sort(key=lambda x: (cat_order.get(x["category_id"], 99), x["name"].lower()))
    print("Live products:", len(items))

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    new_skus: dict[str, dict] = {}
    for i, it in enumerate(items, start=1):
        sku_id = f"{i:03d}"
        slug = slugify(it["name"])
        ext = ext_from_url(it.get("image") or "")
        fname = f"sku-{sku_id}-{slug}{ext}"
        rel = f"assets/img/alko/{fname}"
        dest = ROOT / rel
        ok = False
        if it.get("image"):
            # prefer full-size: strip -300x300
            img_url = re.sub(r"-\d+x\d+(\.(?:jpg|jpeg|png|webp))$", r"\1", it["image"], flags=re.I)
            ok = download_image(img_url, dest)
            if not ok and img_url != it["image"]:
                ok = download_image(it["image"], dest)
        if not ok:
            rel = "assets/img/alko/_placeholder.svg"
        facts = pick_facts(it)
        use = pick_use(it)
        price = it.get("price") or "цена по запросу"
        if price and not price.startswith("от ") and "запрос" not in price:
            price_disp = f"от {price}"
        else:
            price_disp = price
        new_skus[sku_id] = {
            "name": it["name"],
            "price": price_disp,
            "href": f"index.html#sku-{sku_id}",
            "slug": slug,
            "image": rel,
            "category": it["category_id"],
            "categoryName": it.get("category") or "",
            "sourceUrl": it["url"],
            "facts": facts,
            "use": use,
            "tg": it["name"][:80],
        }
        if i % 20 == 0:
            print(f"  processed {i}/{len(items)}")
            time.sleep(0.15)

    # placeholder svg if needed
    ph = IMG_DIR / "_placeholder.svg"
    if not ph.exists():
        ph.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">'
            '<rect fill="#F3F1EF" width="600" height="600"/>'
            '<rect x="180" y="180" width="240" height="240" fill="none" stroke="#C00000" stroke-width="4"/>'
            '<text x="300" y="320" text-anchor="middle" fill="#666" font-family="sans-serif" font-size="28">нет фото</text>'
            "</svg>",
            encoding="utf-8",
        )

    missing_img = sum(1 for s in new_skus.values() if "placeholder" in s["image"])
    print(f"Images: {len(new_skus) - missing_img} ok, {missing_img} placeholder")

    parts = {
        "disclaimer": "Для домашнего использования. Спирт и готовый алкоголь не продаём. Цены — ориентиры «от X ₽» по витрине партнёра (alkotrademsk.ru), не оферта.",
        "source": {
            "name": "Алкотрейд",
            "url": "https://alkotrademsk.ru/",
            "migrated": "2026-09-15",
            "archive": "assets/data/archive-sku-old.json",
        },
        "categories": CATEGORIES,
        "skus": new_skus,
        "modes": modes,
    }
    PARTS.write_text(json.dumps(parts, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote parts.json:", len(new_skus), "SKUs,", len(CATEGORIES), "categories")
    print("modes preserved:", list(modes.keys()))


if __name__ == "__main__":
    main()
