from pathlib import Path

out = Path("assets/img")
items = [
    ("21", "spn", "СПН насадка"),
    ("22", "rpn", "РПН насадка"),
    ("23", "gasket-20", "Прокладка 2″"),
    ("24", "drain", "Кран слива"),
    ("25", "chiller", "Чиллер"),
    ("26", "prv", "Воздушный клапан"),
    ("27", "receiver", "Приёмная ёмкость"),
    ("28", "adapter", "Переходник кламп"),
    ("29", "blank", "Заглушка кламп"),
    ("30", "mash", "Заторный котёл"),
    ("31", "needle", "Игольчатый кран"),
    ("32", "clamp-extra", "Хомут кламп 2″"),
]

tpl = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <rect width="600" height="600" fill="#ffffff"/>
  <rect x="48" y="48" width="504" height="504" fill="none" stroke="#E8E4E1" stroke-width="2"/>
  <path d="M286 118 L318 118 L330 162 L274 162 Z" fill="#C00000"/>
  <rect x="230" y="200" width="140" height="200" rx="3" fill="#FAF9F8" stroke="#1A1A1A" stroke-width="2.5"/>
  <line x1="250" y1="250" x2="350" y2="250" stroke="#C00000" stroke-width="2"/>
  <line x1="250" y1="300" x2="350" y2="300" stroke="#C00000" stroke-width="2" opacity="0.55"/>
  <line x1="250" y1="350" x2="350" y2="350" stroke="#C00000" stroke-width="2" opacity="0.3"/>
  <circle cx="300" cy="420" r="8" fill="#C00000"/>
  <text x="300" y="500" text-anchor="middle" font-family="system-ui,sans-serif" font-size="20" fill="#1A1A1A" font-weight="600">SKU {num}</text>
  <text x="300" y="530" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" fill="#666666">{title}</text>
</svg>
"""

for num, slug, title in items:
    (out / f"sku-{num}-{slug}.svg").write_text(tpl.format(num=num, title=title), encoding="utf-8")

print("wrote", len(items), "placeholders")
