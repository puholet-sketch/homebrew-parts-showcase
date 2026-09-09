# -*- coding: utf-8 -*-
import json, re
from pathlib import Path

p = Path(r"D:/projects/homebrew-parts-showcase")
data = json.loads((p / "assets/data/parts.json").read_text(encoding="utf-8"))
t = (p / "schema.html").read_text(encoding="utf-8")
print("valid json")
print("back", "schema-back" in t)
print("coverage", "schema-coverage" in t)
print("hit--path", t.count("hit--path"))
print("blob hose hit gone", "M430 70 C580 50" not in t)
print("viewBox d", re.search(r'svg-distiller[^>]+viewBox="([^"]+)"', t).group(1))
print("viewBox b", re.search(r'svg-brewery[^>]+viewBox="([^"]+)"', t).group(1))

d = t.split('id="svg-distiller"')[1].split('id="svg-brewery"')[0]
b = t.split('id="svg-brewery"')[1].split("</svg>")[0]
ds, bs = set(), set()
for i in set(re.findall(r'data-id="([^"]+)"', d)):
    n = data["modes"]["distiller"]["nodes"].get(i)
    if n and n.get("skuId"):
        ds.add(str(n["skuId"]).zfill(2))
for i in set(re.findall(r'data-id="([^"]+)"', b)):
    n = data["modes"]["brewery"]["nodes"].get(i)
    if n and n.get("skuId"):
        bs.add(str(n["skuId"]).zfill(2))
all_ = ds | bs
print("distiller", len(ds), sorted(ds))
print("brewery", len(bs), sorted(bs))
print("union", len(all_), sorted(all_))
print("missing", sorted({f"{i:02d}" for i in range(1, 33)} - all_))

# check SVG well-formed-ish: balance g tags in layers
for name, chunk in [("distiller", d), ("brewery", b)]:
    opens = len(re.findall(r"<g[\s>]", chunk))
    closes = chunk.count("</g>")
    print(name, "g open/close", opens, closes)
