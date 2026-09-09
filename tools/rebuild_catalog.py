# -*- coding: utf-8 -*-
"""Rebuild catalog cards in index.html with facts-bar UI + new PNG paths."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PARTS = ROOT / "assets" / "data" / "parts.json"

# icon keys used in sprite
SKUS = [
    {
        "id": "01",
        "slug": "clamp-15",
        "alt": "Кламп 1,5 дюйма в сборе",
        "title": "Кламп 1,5″ в сборе",
        "price": "от 220 ₽",
        "tg": "Кламп 1,5″",
        "facts": [("steel", "AISI 304"), ("size", "Ø 50,5 мм"), ("gasket", "с прокладкой")],
    },
    {
        "id": "02",
        "slug": "clamp-20",
        "alt": "Кламп 2 дюйма в сборе",
        "title": "Кламп 2″ в сборе",
        "price": "от 220 ₽",
        "tg": "Кламп 2″",
        "facts": [("size", "2″ DN51"), ("clamp", "быстрый съём"), ("steel", "пищевая сталь")],
    },
    {
        "id": "03",
        "slug": "ten-clamp",
        "alt": "ТЭН под кламп 2 дюйма",
        "title": "ТЭН под кламп 2″ (2–3,5 кВт)",
        "price": "от 1 300 ₽",
        "tg": "ТЭН кламп 2″",
        "facts": [("power", "3 кВт 220 В"), ("clamp", "кламп 2″"), ("steel", "AISI 304")],
    },
    {
        "id": "04",
        "slug": "gaskets",
        "alt": "Силиконовая прокладка на кламп",
        "title": "Прокладка силикон на кламп 1,5″",
        "price": "от 25 ₽",
        "tg": "Прокладка кламп 1,5″",
        "facts": [("gasket", "пищевой силикон"), ("size", "1,5″"), ("seal", "герметичность")],
    },
    {
        "id": "05",
        "slug": "airlock",
        "alt": "Гидрозатвор трёхсоставной",
        "title": "Гидрозатвор трёхсоставной + пробка",
        "price": "от 80 ₽",
        "tg": "Гидрозатвор",
        "facts": [("packing", "трёхсоставной"), ("quiet", "тихий"), ("lid", "с пробкой")],
    },
    {
        "id": "06",
        "slug": "hose",
        "alt": "Шланг силиконовый пищевой",
        "title": "Шланг силикон пищевой 8–12 мм",
        "price": "от 99 ₽/м",
        "tg": "Шланг силикон",
        "facts": [("hose", "пищевой"), ("size", "Ø 8–12 мм"), ("temp", "до +200°C")],
    },
    {
        "id": "07",
        "slug": "fermenter",
        "alt": "Ферментер 30 литров",
        "title": "Ферментер 30 л с крышкой",
        "price": "от 1 400 ₽",
        "tg": "Ферментер 30 л",
        "facts": [("volume", "30 л"), ("lid", "с крышкой"), ("tap", "под кран")],
    },
    {
        "id": "08",
        "slug": "dimroth",
        "alt": "Холодильник Димрота",
        "title": "Холодильник Димрота / змеевик",
        "price": "от 2 200 ₽",
        "tg": "Димрот",
        "facts": [("glass", "Димрот"), ("clamp", "кламп 1,5″"), ("hose", "проходной")],
    },
    {
        "id": "09",
        "slug": "pid",
        "alt": "PID терморегулятор с SSR",
        "title": "PID / терморегулятор + SSR",
        "price": "от 1 950 ₽",
        "tg": "PID + SSR",
        "facts": [("temp", "PID"), ("power", "SSR комплект"), ("temp", "щуп К")],
    },
    {
        "id": "10",
        "slug": "hose-clamps",
        "alt": "Хомуты червячные нержавеющие",
        "title": "Хомуты червячные нерж. набор",
        "price": "от 150 ₽",
        "tg": "хомуты червячные",
        "facts": [("steel", "нерж."), ("packing", "набор"), ("hose", "на шланг")],
    },
    {
        "id": "11",
        "slug": "cube-lid",
        "alt": "Крышка куба с кламп-портами",
        "title": "Крышка куба с кламп-портами",
        "price": "от 3 900 ₽",
        "tg": "Крышка куба",
        "facts": [("clamp", "кламп-порты"), ("steel", "AISI 304"), ("lid", "съёмная")],
    },
    {
        "id": "12",
        "slug": "tsarga",
        "alt": "Царга 1,5 дюйма 50 см",
        "title": "Царга 1,5″ ~50 см",
        "price": "от 850 ₽",
        "tg": "Царга 1,5″",
        "facts": [("size", "50 см"), ("size", "1,5″"), ("packing", "под насадку")],
    },
    {
        "id": "13",
        "slug": "diopter",
        "alt": "Диоптр стеклянная царга",
        "title": "Диоптр (стеклянная царга)",
        "price": "от 2 750 ₽",
        "tg": "Диоптр",
        "facts": [("glass", "стекло"), ("clamp", "кламп"), ("glass", "обзор флегмы")],
    },
    {
        "id": "14",
        "slug": "takeoff",
        "alt": "Узел отбора по жидкости",
        "title": "Узел отбора по жидкости",
        "price": "от 2 090 ₽",
        "tg": "Узел отбора",
        "facts": [("needle", "игольчатый кран"), ("size", "2″"), ("hose", "доохладитель")],
    },
    {
        "id": "15",
        "slug": "parrot",
        "alt": "Попугай проточный",
        "title": "Попугай (проточный под ареометр)",
        "price": "от 990 ₽",
        "tg": "Попугай",
        "facts": [("temp", "онлайн °"), ("glass", "под АСП"), ("steel", "нерж.")],
    },
    {
        "id": "16",
        "slug": "hydrometer",
        "alt": "Ареометр",
        "title": "Ареометр / рефрактометр",
        "price": "от 260 ₽",
        "tg": "Ареометр",
        "facts": [("glass", "АС-3 / АСП"), ("size", "Brix"), ("temp", "контроль")],
    },
    {
        "id": "17",
        "slug": "malt-yeast",
        "alt": "Солод и дрожжи",
        "title": "Солод пилснер + дрожжи пивные",
        "price": "от 390 ₽",
        "tg": "солод + дрожжи",
        "facts": [("packing", "пилснер"), ("packing", "элевые дрожжи"), ("volume", "домашнее")],
    },
    {
        "id": "18",
        "slug": "sanitizer",
        "alt": "Средство дезинфекции",
        "title": "Дезинфекция для ПВК и ферментера",
        "price": "от 299 ₽",
        "tg": "Bio San",
        "facts": [("seal", "без ополаск."), ("power", "кислотный"), ("volume", "ПВК/ферм.")],
    },
    {
        "id": "19",
        "slug": "ball-valve",
        "alt": "Кран шаровый кламп",
        "title": "Кран шаровый кламп 1,5″",
        "price": "от 1 200 ₽",
        "tg": "Кран кламп 1,5″",
        "facts": [("tap", "полнопроход"), ("clamp", "кламп 1,5″"), ("steel", "AISI")],
    },
    {
        "id": "20",
        "slug": "thermometer",
        "alt": "Термометр биметаллический кламп",
        "title": "Термометр биметаллический кламп 1,5″",
        "price": "от 2 380 ₽",
        "tg": "термометр кламп",
        "facts": [("temp", "биметалл"), ("clamp", "кламп 1,5″"), ("temp", "0–120°C")],
    },
    {
        "id": "21",
        "slug": "spn",
        "alt": "Насадка СПН",
        "title": "Насадка СПН (спирально-призматическая)",
        "price": "от 890 ₽/л",
        "tg": "СПН",
        "facts": [("packing", "СПН нерж."), ("packing", "насыпная"), ("clamp", "для царги")],
    },
    {
        "id": "22",
        "slug": "rpn",
        "alt": "Насадка РПН",
        "title": "Насадка РПН (регулярная проволочная)",
        "price": "от 1 450 ₽",
        "tg": "РПН",
        "facts": [("packing", "РПН"), ("packing", "рулон"), ("packing", "высокая эфф.")],
    },
    {
        "id": "23",
        "slug": "gasket-20",
        "alt": "Прокладка силикон 2 дюйма",
        "title": "Прокладка силикон на кламп 2″",
        "price": "от 35 ₽",
        "tg": "Прокладка 2″",
        "facts": [("gasket", "пищевой силикон"), ("size", "2″"), ("seal", "герметичность")],
    },
    {
        "id": "24",
        "slug": "drain",
        "alt": "Кран слива куба",
        "title": "Кран слива куба",
        "price": "от 650 ₽",
        "tg": "Кран слива",
        "facts": [("tap", "полнопроход"), ("steel", "нерж."), ("tap", "нижний слив")],
    },
    {
        "id": "25",
        "slug": "chiller",
        "alt": "Чиллер погружной",
        "title": "Чиллер погружной / змеевик",
        "price": "от 1 800 ₽",
        "tg": "Чиллер",
        "facts": [("hose", "погружной"), ("steel", "медь/нерж."), ("temp", "охлаждение")],
    },
    {
        "id": "26",
        "slug": "prv",
        "alt": "Воздушный клапан",
        "title": "Воздушный / вакуумный клапан",
        "price": "от 480 ₽",
        "tg": "Воздушный клапан",
        "facts": [("seal", "вакуум-защита"), ("clamp", "кламп"), ("lid", "страховка крышки")],
    },
    {
        "id": "27",
        "slug": "receiver",
        "alt": "Приёмная ёмкость",
        "title": "Приёмная ёмкость 3–5 л",
        "price": "от 190 ₽",
        "tg": "Приёмная ёмкость",
        "facts": [("volume", "3–5 л"), ("seal", "пищевой"), ("glass", "под попугай")],
    },
    {
        "id": "28",
        "slug": "adapter",
        "alt": "Переходник кламп",
        "title": "Переходник кламп 1,5↔2″",
        "price": "от 420 ₽",
        "tg": "Переходник кламп",
        "facts": [("size", "1,5↔2″"), ("steel", "AISI 304"), ("clamp", "без сварки")],
    },
    {
        "id": "29",
        "slug": "blank",
        "alt": "Заглушка кламп",
        "title": "Заглушка кламп 1,5″",
        "price": "от 180 ₽",
        "tg": "Заглушка кламп",
        "facts": [("size", "1,5″"), ("gasket", "с прокладкой"), ("seal", "закрыть порт")],
    },
    {
        "id": "30",
        "slug": "mash",
        "alt": "Заторный котёл",
        "title": "Заторный котёл / ПВК",
        "price": "от 8 900 ₽",
        "tg": "Заторный котёл",
        "facts": [("power", "под ТЭН"), ("volume", "домашний объём"), ("steel", "нерж.")],
    },
    {
        "id": "31",
        "slug": "needle",
        "alt": "Игольчатый кран",
        "title": "Игольчатый кран (на отбор)",
        "price": "от 790 ₽",
        "tg": "Игольчатый кран",
        "facts": [("needle", "тонкая регул."), ("steel", "нерж."), ("needle", "на отбор")],
    },
    {
        "id": "32",
        "slug": "clamp-extra",
        "alt": "Хомут кламп 2 дюйма",
        "title": "Хомут кламп 2″ (дополнительный)",
        "price": "от 190 ₽",
        "tg": "Хомут кламп 2″",
        "facts": [("size", "2″"), ("steel", "нерж."), ("clamp", "запас на стык")],
    },
]

SPRITE = """
<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" class="icon-sprite" aria-hidden="true" focusable="false" style="position:absolute">
  <defs>
    <style>.icon-sprite symbol * { fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }</style>
  </defs>
  <symbol id="i-volume" viewBox="0 0 24 24"><path d="M7 8h10l1 12H6L7 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/><path d="M10 12h4"/></symbol>
  <symbol id="i-lid" viewBox="0 0 24 24"><path d="M5 11h14v2H5z"/><path d="M7 11V9a5 5 0 0 1 10 0v2"/><circle cx="12" cy="7" r="1"/></symbol>
  <symbol id="i-tap" viewBox="0 0 24 24"><path d="M4 10h10a3 3 0 0 1 3 3v2"/><path d="M17 15v3a2 2 0 0 1-4 0"/><path d="M4 10V7h4"/></symbol>
  <symbol id="i-steel" viewBox="0 0 24 24"><path d="M12 3l8 4v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V7l8-4z"/></symbol>
  <symbol id="i-size" viewBox="0 0 24 24"><circle cx="12" cy="12" r="7"/><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-gasket" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/></symbol>
  <symbol id="i-clamp" viewBox="0 0 24 24"><path d="M6 10h12v4H6z"/><path d="M8 10V8h8v2M8 14v2h8v-2"/><path d="M18 12h2"/></symbol>
  <symbol id="i-hose" viewBox="0 0 24 24"><path d="M4 8c4 0 4 8 8 8s4-8 8-8"/><path d="M4 12c4 0 4 8 8 8s4-8 8-8"/></symbol>
  <symbol id="i-temp" viewBox="0 0 24 24"><path d="M10 14.5V6a2 2 0 1 1 4 0v8.5a3.5 3.5 0 1 1-4 0z"/><path d="M12 17v-5"/></symbol>
  <symbol id="i-power" viewBox="0 0 24 24"><path d="M13 2L6 13h5l-1 9 8-12h-5l0-8z"/></symbol>
  <symbol id="i-glass" viewBox="0 0 24 24"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="3"/><path d="M12 5v2M12 17v2M5 12h2M17 12h2"/></symbol>
  <symbol id="i-packing" viewBox="0 0 24 24"><path d="M4 8h16M4 12h16M4 16h16"/><path d="M8 6v12M12 6v12M16 6v12"/></symbol>
  <symbol id="i-needle" viewBox="0 0 24 24"><path d="M5 12h10"/><path d="M15 8v8"/><path d="M18 12l3-2v4l-3-2z"/></symbol>
  <symbol id="i-quiet" viewBox="0 0 24 24"><path d="M8 10v4"/><path d="M12 8v8"/><path d="M16 10v4"/></symbol>
  <symbol id="i-seal" viewBox="0 0 24 24"><path d="M12 3l2.2 4.5L19 8.2l-3.5 3.4.8 4.9L12 14.8 7.7 16.5l.8-4.9L5 8.2l4.8-.7L12 3z"/></symbol>
</svg>
"""


def tg_href(text: str) -> str:
    from urllib.parse import quote

    return f"https://t.me/puholet?text={quote('Заказ: ' + text)}"


def card_html(s: dict) -> str:
    facts = []
    for icon, text in s["facts"]:
        facts.append(
            f"""            <li class="facts-bar__item">
              <span class="facts-bar__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#i-{icon}"></use></svg></span>
              <span class="facts-bar__text">{text}</span>
            </li>"""
        )
    facts_block = "\n".join(facts)
    img = f'assets/img/sku-{s["id"]}-{s["slug"]}.png'
    return f"""        <article class="card reveal" id="sku-{s['id']}">
          <div class="card__media">
            <img src="{img}" alt="{s['alt']}" width="600" height="600" loading="lazy" />
            <ul class="facts-bar" aria-label="Факты о товаре">
{facts_block}
            </ul>
          </div>
          <div class="card__body">
            <span class="card__sku">SKU {s['id']}</span>
            <h3 class="card__title">{s['title']}</h3>
            <div class="card__price">{s['price']}</div>
            <div class="card__actions"><a class="btn btn--primary btn--sm" href="{tg_href(s['tg'])}">Заказать</a></div>
          </div>
        </article>"""


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    cards = "\n\n".join(card_html(s) for s in SKUS)
    catalog = f'      <div class="catalog">\n{cards}\n\n      </div>'
    html2, n = re.subn(
        r'<div class="catalog">.*?</div>\s*</section>',
        catalog + "\n    </section>",
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"catalog replace failed: {n}")

    html2 = re.sub(
        r'<svg[^>]*class="icon-sprite"[^>]*>.*?</svg>\s*',
        "",
        html2,
        count=1,
        flags=re.S,
    )
    html2 = html2.replace("<body>", "<body>\n" + SPRITE, 1)

    INDEX.write_text(html2, encoding="utf-8")

    data = json.loads(PARTS.read_text(encoding="utf-8"))
    for s in SKUS:
        entry = data["skus"].setdefault(s["id"], {})
        entry.update(
            {
                "name": s["title"],
                "price": s["price"],
                "href": f"index.html#sku-{s['id']}",
                "slug": s["slug"],
                "image": f"assets/img/sku-{s['id']}-{s['slug']}.png",
                "facts": [{"icon": i, "text": t} for i, t in s["facts"]],
            }
        )
    PARTS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated {INDEX.name} + parts.json ({len(SKUS)} skus)")


if __name__ == "__main__":
    main()
