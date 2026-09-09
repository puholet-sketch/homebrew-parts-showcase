# -*- coding: utf-8 -*-
"""Patch rebuild_catalog.py: add USES + card/modal markup, then rebuild."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PARTS = ROOT / "assets" / "data" / "parts.json"
REBUILD = ROOT / "tools" / "rebuild_catalog.py"

USES = {
    "01": "Быстросъёмное соединение узлов колонны и куба на 1,5″.",
    "02": "Соединение крупных узлов: ТЭН, царга, отбор на 2″.",
    "03": "Электроподогрев куба или заторника через кламп-фланец.",
    "04": "Герметичность каждого кламп-стыка 1,5″ — сменный расходник.",
    "05": "Сброс CO₂ при брожении без доступа воздуха в ферментер.",
    "06": "Вода на холодильник и переливы сусла / продукта.",
    "07": "Ёмкость брожения сусла для домашнего пива.",
    "08": "Конденсация паров и охлаждение на колонне.",
    "09": "Удержание температуры ТЭНа и пауз затирания.",
    "10": "Фиксация силиконовых шлангов на штуцерах.",
    "11": "Крышка куба с портами под царгу и контрольные приборы.",
    "12": "Секция колонны под насадку СПН или РПН.",
    "13": "Визуальный контроль флегмы и кипения в колонне.",
    "14": "Точный отбор по жидкости с игольчатым краном.",
    "15": "Проточный карман под ареометр на выходе продукта.",
    "16": "Контроль плотности и крепости сусла / дистиллята.",
    "17": "Сырьё для домашнего пива: солод и пивные дрожжи.",
    "18": "Санитарная обработка ПВК, шлангов и ферментера.",
    "19": "Перекрытие потока на сливе ферментера или линии отбора.",
    "20": "Визуальный контроль температуры в кубе без электроники.",
    "21": "Насадка в царге: больше поверхность контакта пара и флегмы.",
    "22": "Альтернатива СПН — регулярная проволочная насадка в царгу.",
    "23": "Герметичность кламп-стыка 2″ — сменный расходник.",
    "24": "Слив куба после прогона или мойки.",
    "25": "Охлаждение сусла перед внесением дрожжей.",
    "26": "Сброс и выравнивание давления — защита крышки куба.",
    "27": "Приём дистиллята с попугая рядом с отбором.",
    "28": "Стык кламп 1,5″ и 2″ без сварки.",
    "29": "Закрытие незанятого порта на крышке или кубе.",
    "30": "Затирание и кипячение сусла в домашней пивоварне.",
    "31": "Тонкая регулировка потока на узле отбора.",
    "32": "Запасной хомут на стык кламп 2″.",
}

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

MODAL = """
  <div class="sku-modal" id="sku-modal" hidden>
    <div class="sku-modal__backdrop" data-close-modal></div>
    <div class="sku-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="sku-modal-title">
      <button type="button" class="sku-modal__close" data-close-modal aria-label="Закрыть">×</button>
      <div class="sku-modal__grid">
        <div class="sku-modal__media">
          <img id="sku-modal-img" src="" alt="" width="600" height="600" />
          <ul class="facts-bar" id="sku-modal-facts" aria-label="Факты о товаре"></ul>
        </div>
        <div class="sku-modal__body">
          <span class="card__sku" id="sku-modal-sku"></span>
          <h2 class="sku-modal__title" id="sku-modal-title"></h2>
          <p class="sku-modal__use"><strong>Для чего:</strong> <span id="sku-modal-use"></span></p>
          <div class="card__price" id="sku-modal-price"></div>
          <div class="sku-modal__actions">
            <a class="btn btn--primary" id="sku-modal-order" href="#" target="_blank" rel="noopener">Заказать</a>
            <a class="btn btn--ghost" id="sku-modal-schema" href="schema.html">На схеме</a>
            <button type="button" class="btn btn--ghost" data-close-modal>Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  </div>
"""


def load_skus_from_rebuild() -> list[dict]:
    """Exec SKUS list from rebuild_catalog.py without running main."""
    ns: dict = {}
    code = REBUILD.read_text(encoding="utf-8")
    # take only up to SPRITE / before def tg_href — safer: extract SKUS via regex eval
    m = re.search(r"SKUS = (\[.*?\n\])\n", code, flags=re.S)
    if not m:
        raise SystemExit("SKUS not found in rebuild_catalog.py")
    skus = eval(m.group(1), {"__builtins__": {}})  # noqa: S307 — local trusted file
    return skus


def tg_href(text: str) -> str:
    return f"https://t.me/puholet?text={quote('Заказ: ' + text)}"


def card_html(s: dict) -> str:
    use = USES[s["id"]]
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
    return f"""        <article class="card reveal" id="sku-{s['id']}" data-sku="{s['id']}">
          <button type="button" class="card__hit" data-open-sku="{s['id']}" aria-label="Открыть карточку: {s['title']}">
            <div class="card__media">
              <div class="card__photo">
                <img src="{img}" alt="{s['alt']}" width="600" height="600" loading="lazy" />
              </div>
              <ul class="facts-bar" aria-label="Факты о товаре">
{facts_block}
              </ul>
            </div>
          </button>
          <div class="card__body">
            <span class="card__sku">SKU {s['id']}</span>
            <h3 class="card__title">
              <button type="button" class="card__title-btn" data-open-sku="{s['id']}">{s['title']}</button>
            </h3>
            <p class="card__use"><span class="card__use-label">Для чего</span> {use}</p>
            <div class="card__price">{s['price']}</div>
            <div class="card__actions">
              <button type="button" class="btn btn--ghost btn--sm" data-open-sku="{s['id']}">Подробнее</button>
              <a class="btn btn--primary btn--sm" href="{tg_href(s['tg'])}">Заказать</a>
            </div>
          </div>
        </article>"""


def main() -> None:
    skus = load_skus_from_rebuild()
    html = INDEX.read_text(encoding="utf-8")
    cards = "\n\n".join(card_html(s) for s in skus)
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

    # ensure modal once before footer/script
    if 'id="sku-modal"' not in html2:
        html2 = html2.replace('<script src="assets/js/main.js"></script>', MODAL + '\n  <script src="assets/js/main.js"></script>')
    else:
        html2 = re.sub(
            r'<div class="sku-modal"[^>]*>.*?</div>\s*(?=<script src="assets/js/main.js")',
            MODAL + "\n  ",
            html2,
            count=1,
            flags=re.S,
        )

    INDEX.write_text(html2, encoding="utf-8")

    data = json.loads(PARTS.read_text(encoding="utf-8"))
    for s in skus:
        entry = data["skus"].setdefault(s["id"], {})
        entry.update(
            {
                "name": s["title"],
                "price": s["price"],
                "href": f"index.html#sku-{s['id']}",
                "slug": s["slug"],
                "image": f"assets/img/sku-{s['id']}-{s['slug']}.png",
                "use": USES[s["id"]],
                "tg": s["tg"],
                "facts": [{"icon": i, "text": t} for i, t in s["facts"]],
            }
        )
    PARTS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated catalog+modal+use ({len(skus)} skus)")


if __name__ == "__main__":
    main()
