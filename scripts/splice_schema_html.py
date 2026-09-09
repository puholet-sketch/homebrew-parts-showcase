# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html_path = root / "schema.html"
html = html_path.read_text(encoding="utf-8")

dist_path = root / "assets/svg/distiller.svg"
brew_path = root / "assets/svg/brewery.svg"
if not dist_path.exists():
    dist_path = root / "assets/svg/schema-distiller.svg"
if not brew_path.exists():
    brew_path = root / "assets/svg/schema-brewery.svg"

dist = dist_path.read_text(encoding="utf-8")
brew = brew_path.read_text(encoding="utf-8")
xml_decl = '<?xml version="1.0" encoding="UTF-8"?>'
dist = dist.replace(xml_decl, "").strip()
brew = brew.replace(xml_decl, "").strip()
if " hidden>" not in brew.split(">", 1)[0]:
    brew = brew.replace("<svg ", '<svg hidden ', 1)

start = html.index("          <!-- DISTILLER -->")
end = html.index("        </div>\n      </div>\n\n      <aside")
new = (
    "          <!-- DISTILLER -->\n          "
    + dist.replace("\n", "\n          ")
    + "\n\n          <!-- BREWERY -->\n          "
    + brew.replace("\n", "\n          ")
    + "\n"
)
html_path.write_text(html[:start] + new + html[end:], encoding="utf-8")
print("spliced ok", html_path.stat().st_size)
