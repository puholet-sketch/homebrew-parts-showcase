# -*- coding: utf-8 -*-
from pathlib import Path
import re

idx = Path(__file__).resolve().parents[1] / "index.html"
html = idx.read_text(encoding="utf-8")

html = html.replace(
    "Ходовые SKU: клампы, ТЭНы, царги, расходники. Интерактивная схема аппарата — наведите на узел. Самовывоз Москва. Цены — ориентиры розницы.",
    "Каталог по категориям: арматура, краны, КИПиА, ТЭНы, шланги. Интерактивная схема аппарата — наведите на узел. Самовывоз Москва. Цены — ориентиры витрины.",
)

new_catalog = """    <section class=\"section\" id=\"catalog\">
      <div class=\"section__head\">
        <h2>Каталог · запчасти</h2>
        <p>Цены «от … ₽» по витрине партнёра. Наличие и точную цену уточняйте при заказе. Схема узлов (архивные позиции): <a href=\"schema.html\">собрать глазами</a>.</p>
      </div>

      <div class=\"catalog-toolbar\" id=\"catalog-toolbar\" role=\"navigation\" aria-label=\"Категории каталога\">
        <div class=\"catalog-filters\" id=\"catalog-filters\"></div>
        <p class=\"catalog-meta\" id=\"catalog-meta\" aria-live=\"polite\"></p>
      </div>

      <div class=\"catalog\" id=\"catalog-grid\">
        <p class=\"catalog-loading\">Загружаем каталог…</p>
      </div>
    </section>"""

html2, n = re.subn(
    r'    <section class="section" id="catalog">.*?</section>\n\n    <section class="section--ink" id="order">',
    new_catalog + "\n\n    <section class=\"section--ink\" id=\"order\">",
    html,
    count=1,
    flags=re.S,
)

html2 = html2.replace(
    "Фото — рендеры карточек для согласования вида; живые кадры с полки появятся после согласия на съёмку.",
    "Фото и цены — с витрины партнёра (ориентиры). Живые кадры со склада появятся после согласия на съёмку.",
)

if n != 1:
    raise SystemExit(f"catalog replace failed: n={n}")

idx.write_text(html2, encoding="utf-8")
print("index.html catalog replaced OK, size", len(html2))
