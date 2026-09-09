# -*- coding: utf-8 -*-
"""One-shot patch: hose hits, split clamps, missing SKU hotspots, chrome."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "schema.html"
text = path.read_text(encoding="utf-8")

# --- hero: coverage + modes wrap ---
old_hero_modes = """      <div class="schema-modes" role="group" aria-label="Режим схемы">
        <button type="button" data-mode="distiller" aria-pressed="true">Колонна / дистиллятор</button>
        <button type="button" data-mode="brewery" aria-pressed="false">Пивоварня</button>
      </div>
    </section>"""

new_hero_modes = """      <div class="schema-hero__meta">
        <div class="schema-modes" role="group" aria-label="Режим схемы">
          <button type="button" data-mode="distiller" aria-pressed="true">Колонна / дистиллятор</button>
          <button type="button" data-mode="brewery" aria-pressed="false">Пивоварня</button>
        </div>
        <p class="schema-coverage" id="schema-coverage" aria-live="polite">Покрытие каталога: …</p>
      </div>
    </section>"""

if "schema-coverage" not in text:
    if old_hero_modes not in text:
        raise SystemExit("hero modes block not found")
    text = text.replace(old_hero_modes, new_hero_modes, 1)

# --- crumb + back ---
old_crumb = """        <div class="schema-crumb" id="schema-crumb" aria-label="Навигация по узлам"></div>"""
new_crumb = """        <div class="schema-crumb-row">
          <button type="button" class="schema-back" id="schema-back" hidden>← Назад</button>
          <div class="schema-crumb" id="schema-crumb" aria-label="Навигация по узлам"></div>
        </div>"""
if "schema-back" not in text:
    if old_crumb not in text:
        raise SystemExit("crumb block not found")
    text = text.replace(old_crumb, new_crumb, 1)

# --- tighter viewBoxes (larger apparatus, less empty) ---
text = text.replace(
    'id="svg-distiller" class="schema-svg" viewBox="0 0 860 1080"',
    'id="svg-distiller" class="schema-svg" viewBox="20 30 720 1020"',
    1,
)
# brewery may have duplicate hidden attrs
text = re.sub(
    r'id="svg-brewery"[^>]*viewBox="0 0 980 820"',
    'id="svg-brewery" hidden class="schema-svg" viewBox="20 150 900 660"',
    text,
    count=1,
)

# --- replace root hoses hotspot ---
hose_old = """    <g class="hotspot" id="part-hoses" data-id="hoses" tabindex="0" role="button" aria-label="Шланги охлаждения">
      <path d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="url(#dhoseIn)" stroke-width="7" stroke-linecap="round"/>
      <path d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="#eaf6fb" stroke-width="2" transform="translate(0,-1.6)"/>
      <path d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="url(#dhoseOut)" stroke-width="7" stroke-linecap="round"/>
      <path d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="#f8e6da" stroke-width="2" transform="translate(0,-1.4)"/>
      <circle cx="668" cy="260" r="6" fill="#8a9199"/>
      <circle cx="668" cy="430" r="6" fill="#8a9199"/>
      <path class="hit" d="M430 70 C580 50 700 150 690 270 C690 360 650 430 650 450 L690 450 C700 300 720 80 430 55 Z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

hose_new = """    <g class="hotspot" id="part-hoses" data-id="hoses" tabindex="0" role="button" aria-label="Шланги охлаждения">
      <path class="hl" d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="#c00000" stroke-width="12" stroke-linecap="round"/>
      <path class="hl" d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="#c00000" stroke-width="12" stroke-linecap="round"/>
      <path d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="url(#dhoseIn)" stroke-width="7" stroke-linecap="round"/>
      <path d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="#eaf6fb" stroke-width="2" transform="translate(0,-1.6)"/>
      <path d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="url(#dhoseOut)" stroke-width="7" stroke-linecap="round"/>
      <path d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="#f8e6da" stroke-width="2" transform="translate(0,-1.4)"/>
      <path class="hit hit--path" d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="transparent" stroke-width="22" stroke-linecap="round"/>
      <path class="hit hit--path" d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="transparent" stroke-width="22" stroke-linecap="round"/>
    </g>
    <g class="hotspot" id="part-hose-clamps" data-id="hose-clamps" tabindex="0" role="button" aria-label="Хомуты червячные">
      <ellipse cx="668" cy="260" rx="11" ry="9" fill="url(#dmetal)" stroke="#5c6369" stroke-width="1.2"/>
      <rect x="662" y="252" width="12" height="16" rx="1.5" fill="#8a9199"/>
      <ellipse cx="668" cy="430" rx="11" ry="9" fill="url(#dmetal)" stroke="#5c6369" stroke-width="1.2"/>
      <rect x="662" y="422" width="12" height="16" rx="1.5" fill="#8a9199"/>
      <circle cx="456" cy="108" r="7" fill="url(#dmetal)" stroke="#5c6369"/>
      <circle cx="456" cy="228" r="7" fill="url(#dmetal)" stroke="#5c6369"/>
      <path class="hit" d="M650 244 h36 v36 h-36 z M650 414 h36 v36 h-36 z M444 96 h24 v24 h-24 z M444 216 h24 v24 h-24 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

if hose_old not in text:
    raise SystemExit("root hose block not found")
text = text.replace(hose_old, hose_new, 1)

# --- hydro near parrot (insert before receiver or after parrot) ---
if 'data-id="hydro"' not in text.split('id="svg-distiller"')[1].split('id="svg-brewery"')[0]:
    parrot_marker = 'id="part-parrot"'
    # find end of parrot hotspot group — next hotspot after parrot hit
    m = re.search(
        r'(<g class="hotspot" id="part-parrot"[\s\S]*?</g>\s*)(<g class="hotspot" id="part-receiver")',
        text,
    )
    if not m:
        raise SystemExit("parrot/receiver not found")
    hydro = """    <g class="hotspot" id="part-hydro" data-id="hydro" tabindex="0" role="button" aria-label="Ареометр">
      <rect x="610" y="430" width="14" height="78" rx="3" fill="#dfe8ec" stroke="#7a929c"/>
      <ellipse cx="617" cy="430" rx="9" ry="4" fill="#eef6f8" stroke="#7a929c"/>
      <path d="M610 470 h14" stroke="#c00000" stroke-width="1.2"/>
      <path class="hit" d="M600 420 h34 v96 h-34 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
"""
    text = text[: m.end(1)] + hydro + text[m.start(2) :]

# --- cube detail: valve, blank, adapter, clamp2 ---
cube_end = re.search(
    r'(<g class="layer" data-layer="cube-detail"[\s\S]*?)(</g>\s*<!-- TSARGA|</g>\s*<g class="layer" data-layer="tsarga-detail")',
    text,
)
if not cube_end:
    # try without comment
    cube_end = re.search(
        r'(<g class="layer" data-layer="cube-detail"[\s\S]*?)(\n  </g>\n\n  <!-- |\n  </g>\n  <g class="layer" data-layer="tsarga-detail")',
        text,
    )

# Find cube-detail closing more simply
idx_cube = text.find('data-layer="cube-detail"')
idx_tsarga = text.find('data-layer="tsarga-detail"')
if idx_cube < 0 or idx_tsarga < 0:
    raise SystemExit("cube/tsarga layers missing")
cube_section = text[idx_cube:idx_tsarga]
if 'data-id="valve"' not in cube_section:
    extras = """
    <g class="hotspot" id="part-valve-d" data-id="valve" tabindex="0" role="button" aria-label="Кран шаровый">
      <rect x="470" y="760" width="70" height="28" rx="4" fill="url(#dmetal)"/>
      <circle cx="540" cy="774" r="12" fill="#6a7178"/>
      <path class="hit" d="M460 748 h96 v50 h-96 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
    <g class="hotspot" id="part-blank-d" data-id="blank" tabindex="0" role="button" aria-label="Заглушка кламп">
      <ellipse cx="280" cy="180" rx="28" ry="10" fill="url(#dmetal)" stroke="#5c6369"/>
      <ellipse cx="280" cy="180" rx="14" ry="5" fill="#eef1f3"/>
      <path class="hit" d="M248 160 h64 v40 h-64 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
    <g class="hotspot" id="part-adapter-d" data-id="adapter" tabindex="0" role="button" aria-label="Переходник">
      <ellipse cx="520" cy="180" rx="34" ry="12" fill="url(#dmetal)" stroke="#5c6369"/>
      <ellipse cx="520" cy="180" rx="18" ry="7" fill="#c8cdd3"/>
      <text x="500" y="210" font-size="11" fill="#6a7178" font-family="Onest,sans-serif">1.5↔2</text>
      <path class="hit" d="M480 160 h80 v56 h-80 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
    <g class="hotspot" id="part-clamp2-d" data-id="clamp2" tabindex="0" role="button" aria-label="Кламп 2 дюйма">
      <ellipse cx="400" cy="150" rx="70" ry="12" fill="url(#dmetalV)" stroke="#6a7178"/>
      <circle cx="478" cy="150" r="8" fill="url(#dmetal)" stroke="#5c6369"/>
      <text x="360" y="130" font-size="11" fill="#6a7178" font-family="Onest,sans-serif">2″</text>
      <path class="hit" d="M320 128 h180 v44 h-180 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
"""
    # insert before closing of cube-detail: last </g> before tsarga-detail
    # find the position of cube-detail's closing tag: the </g> immediately preceding tsarga
    # Walk back from idx_tsarga to find </g>
    close_pos = text.rfind("</g>", idx_cube, idx_tsarga)
    # That might be last hotspot's close. Need the layer close.
    # Structure: layer opens, hotspots, then </g> for layer.
    # idx_tsarga points at data-layer="tsarga-detail" — find previous </g>\n
    pre = text[:idx_tsarga]
    # Find `<g class="layer" data-layer="tsarga-detail"` start
    layer_start = text.rfind("<g class=\"layer\" data-layer=\"tsarga-detail\"", 0, idx_tsarga + 80)
    insert_at = text.rfind("</g>", idx_cube, layer_start)
    text = text[:insert_at] + extras + "\n  " + text[insert_at:]

# refresh indices after insert
idx_tsarga = text.find('data-layer="tsarga-detail"')
idx_dimroth = text.find('data-layer="dimroth-detail"')
tsarga_section = text[idx_tsarga:idx_dimroth]
if 'data-id="gasket2"' not in tsarga_section:
    extras_t = """
    <g class="hotspot" id="part-gasket2-t" data-id="gasket2" tabindex="0" role="button" aria-label="Прокладка 2 дюйма">
      <ellipse cx="400" cy="130" rx="70" ry="9" fill="#f4f4f0" stroke="#c8c8c0" stroke-width="1.2"/>
      <text x="430" y="124" font-size="10" fill="#8a9199" font-family="Onest,sans-serif">2″</text>
      <path class="hit" d="M320 112 h160 v36 h-160 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
    <g class="hotspot" id="part-clamp-extra-t" data-id="clamp-extra" tabindex="0" role="button" aria-label="Хомут кламп 2 дюйма">
      <ellipse cx="400" cy="60" rx="88" ry="11" fill="url(#dmetal)" stroke="#5c6369"/>
      <circle cx="496" cy="60" r="7" fill="url(#dmetal)" stroke="#4e555b"/>
      <text x="318" y="54" font-size="10" fill="#6a7178" font-family="Onest,sans-serif">2″ spare</text>
      <path class="hit" d="M300 42 h210 v36 h-210 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
    <g class="hotspot" id="part-clamp2-t" data-id="clamp2" tabindex="0" role="button" aria-label="Кламп 2 дюйма">
      <ellipse cx="400" cy="990" rx="88" ry="11" fill="url(#dmetal)" stroke="#5c6369"/>
      <circle cx="496" cy="990" r="7" fill="url(#dmetal)" stroke="#4e555b"/>
      <text x="430" y="1018" font-size="10" fill="#6a7178" font-family="Onest,sans-serif">2″</text>
      <path class="hit" d="M300 972 h210 v40 h-210 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
"""
    layer_start = text.find('<g class="layer" data-layer="dimroth-detail"')
    insert_at = text.rfind("</g>", idx_tsarga, layer_start)
    text = text[:insert_at] + extras_t + "\n  " + text[insert_at:]

# --- dimroth hoses ---
dim_hose_old = """    <g class="hotspot" id="part-hoses-d" data-id="hoses" tabindex="0" role="button" aria-label="Шланги">
      <rect x="500" y="140" width="40" height="16" rx="3" fill="url(#dmetal)"/>
      <rect x="500" y="780" width="40" height="16" rx="3" fill="url(#dmetal)"/>
      <path d="M540 148 C640 148, 680 220, 700 300" fill="none" stroke="url(#dhoseIn)" stroke-width="10" stroke-linecap="round"/>
      <path d="M540 788 C640 788, 700 700, 720 600" fill="none" stroke="url(#dhoseOut)" stroke-width="10" stroke-linecap="round"/>
      <path class="hit" d="M498 120 h240 v700 h-80 v-500 h-160 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

dim_hose_new = """    <g class="hotspot" id="part-hoses-d" data-id="hoses" tabindex="0" role="button" aria-label="Шланги">
      <path class="hl" d="M540 148 C640 148, 680 220, 700 300" fill="none" stroke="#c00000" stroke-width="14" stroke-linecap="round"/>
      <path class="hl" d="M540 788 C640 788, 700 700, 720 600" fill="none" stroke="#c00000" stroke-width="14" stroke-linecap="round"/>
      <rect x="500" y="140" width="40" height="16" rx="3" fill="url(#dmetal)"/>
      <rect x="500" y="780" width="40" height="16" rx="3" fill="url(#dmetal)"/>
      <path d="M540 148 C640 148, 680 220, 700 300" fill="none" stroke="url(#dhoseIn)" stroke-width="10" stroke-linecap="round"/>
      <path d="M540 788 C640 788, 700 700, 720 600" fill="none" stroke="url(#dhoseOut)" stroke-width="10" stroke-linecap="round"/>
      <path class="hit hit--path" d="M540 148 C640 148, 680 220, 700 300" fill="none" stroke="transparent" stroke-width="26" stroke-linecap="round"/>
      <path class="hit hit--path" d="M540 788 C640 788, 700 700, 720 600" fill="none" stroke="transparent" stroke-width="26" stroke-linecap="round"/>
    </g>
    <g class="hotspot" id="part-hose-clamps-d" data-id="hose-clamps" tabindex="0" role="button" aria-label="Хомуты">
      <ellipse cx="540" cy="148" rx="14" ry="11" fill="url(#dmetal)" stroke="#5c6369"/>
      <ellipse cx="540" cy="788" rx="14" ry="11" fill="url(#dmetal)" stroke="#5c6369"/>
      <ellipse cx="700" cy="300" rx="12" ry="10" fill="url(#dmetal)" stroke="#5c6369"/>
      <ellipse cx="720" cy="600" rx="12" ry="10" fill="url(#dmetal)" stroke="#5c6369"/>
      <path class="hit" d="M520 130 h40 v36 h-40 z M520 770 h40 v36 h-40 z M684 284 h36 v32 h-36 z M704 584 h36 v32 h-36 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
    <g class="hotspot" id="part-chiller-link" data-id="chiller-link" tabindex="0" role="button" aria-label="Чиллер альтернатива">
      <rect x="120" y="420" width="120" height="72" rx="8" fill="#faf9f8" stroke="#c8cdd3"/>
      <text x="136" y="450" font-size="12" fill="#6a7178" font-family="Onest,sans-serif">альт.</text>
      <text x="136" y="470" font-size="13" font-weight="600" fill="#c00000" font-family="Onest,sans-serif">Чиллер</text>
      <path class="hit" d="M112 410 h136 v92 h-136 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

if dim_hose_old not in text:
    raise SystemExit("dimroth hose block not found")
text = text.replace(dim_hose_old, dim_hose_new, 1)

# --- takeoff hose ---
to_hose_old = """    <g class="hotspot" id="part-hoses-to" data-id="hoses" tabindex="0" role="button" aria-label="Шланги">
      <path d="M670 538 C760 560, 780 640, 740 720" fill="none" stroke="url(#dhoseOut)" stroke-width="8" stroke-linecap="round"/>
      <path class="hit" d="M650 520 h140 v220 h-140 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

to_hose_new = """    <g class="hotspot" id="part-hoses-to" data-id="hoses" tabindex="0" role="button" aria-label="Шланги">
      <path class="hl" d="M670 538 C760 560, 780 640, 740 720" fill="none" stroke="#c00000" stroke-width="12" stroke-linecap="round"/>
      <path d="M670 538 C760 560, 780 640, 740 720" fill="none" stroke="url(#dhoseOut)" stroke-width="8" stroke-linecap="round"/>
      <path class="hit hit--path" d="M670 538 C760 560, 780 640, 740 720" fill="none" stroke="transparent" stroke-width="24" stroke-linecap="round"/>
    </g>
    <g class="hotspot" id="part-hose-clamps-to" data-id="hose-clamps" tabindex="0" role="button" aria-label="Хомуты">
      <ellipse cx="670" cy="538" rx="11" ry="9" fill="url(#dmetal)" stroke="#5c6369"/>
      <ellipse cx="740" cy="720" rx="11" ry="9" fill="url(#dmetal)" stroke="#5c6369"/>
      <path class="hit" d="M654 522 h32 v32 h-32 z M724 704 h32 v32 h-32 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

if to_hose_old not in text:
    raise SystemExit("takeoff hose block not found")
text = text.replace(to_hose_old, to_hose_new, 1)

# --- brewery hoses ---
brew_hose_old = """    <g class="hotspot" id="part-brew-hoses" data-id="brew-hoses" tabindex="0" role="button" aria-label="Шланги">
      <path d="M250 560 C300 620, 380 640, 470 600" fill="none" stroke="url(#bhoseIn)" stroke-width="7" stroke-linecap="round"/>
      <path d="M560 430 C620 500, 680 620, 760 650" fill="none" stroke="url(#bhoseOut)" stroke-width="6" stroke-linecap="round"/>
      <path class="hit" d="M240 540 h200 v90 h-200 z M540 420 h250 v250 h-80 v-160 h-170 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

brew_hose_new = """    <g class="hotspot" id="part-brew-hoses" data-id="brew-hoses" tabindex="0" role="button" aria-label="Шланги">
      <path class="hl" d="M250 560 C300 620, 380 640, 470 600" fill="none" stroke="#c00000" stroke-width="12" stroke-linecap="round"/>
      <path class="hl" d="M560 430 C620 500, 680 620, 760 650" fill="none" stroke="#c00000" stroke-width="11" stroke-linecap="round"/>
      <path d="M250 560 C300 620, 380 640, 470 600" fill="none" stroke="url(#bhoseIn)" stroke-width="7" stroke-linecap="round"/>
      <path d="M560 430 C620 500, 680 620, 760 650" fill="none" stroke="url(#bhoseOut)" stroke-width="6" stroke-linecap="round"/>
      <path class="hit hit--path" d="M250 560 C300 620, 380 640, 470 600" fill="none" stroke="transparent" stroke-width="22" stroke-linecap="round"/>
      <path class="hit hit--path" d="M560 430 C620 500, 680 620, 760 650" fill="none" stroke="transparent" stroke-width="22" stroke-linecap="round"/>
    </g>
    <g class="hotspot" id="part-brew-hose-clamps" data-id="hose-clamps-brew" tabindex="0" role="button" aria-label="Хомуты">
      <ellipse cx="250" cy="560" rx="10" ry="8" fill="url(#bmetal)" stroke="#5c6369"/>
      <ellipse cx="470" cy="600" rx="10" ry="8" fill="url(#bmetal)" stroke="#5c6369"/>
      <ellipse cx="560" cy="430" rx="10" ry="8" fill="url(#bmetal)" stroke="#5c6369"/>
      <ellipse cx="760" cy="650" rx="10" ry="8" fill="url(#bmetal)" stroke="#5c6369"/>
      <path class="hit" d="M234 544 h32 v32 h-32 z M454 584 h32 v32 h-32 z M544 414 h32 v32 h-32 z M744 634 h32 v32 h-32 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>"""

if brew_hose_old not in text:
    raise SystemExit("brew hose block not found")
text = text.replace(brew_hose_old, brew_hose_new, 1)

# hydro on brewery root if missing
if 'id="part-hydro-brew"' not in text:
    malt_m = re.search(
        r'(<g class="hotspot" id="part-malt"[\s\S]*?</g>\s*)(</g>\s*<g class="layer" data-layer="mash-detail")',
        text,
    )
    if not malt_m:
        raise SystemExit("malt/mash-detail boundary not found")
    hydro_b = """    <g class="hotspot" id="part-hydro-brew" data-id="hydro" tabindex="0" role="button" aria-label="Ареометр">
      <rect x="200" y="640" width="12" height="70" rx="3" fill="#dfe8ec" stroke="#7a929c"/>
      <ellipse cx="206" cy="640" rx="8" ry="4" fill="#eef6f8" stroke="#7a929c"/>
      <path d="M200 678 h12" stroke="#c00000" stroke-width="1.2"/>
      <path class="hit" d="M188 628 h36 v90 h-36 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
"""
    text = text[: malt_m.end(1)] + hydro_b + text[malt_m.start(2) :]

# dimroth-link card on brewery near chiller — optional small chip
if 'data-id="dimroth-link"' not in text:
    chill_m = re.search(
        r'(<g class="hotspot" id="part-chiller"[\s\S]*?</g>\s*)(<g class="hotspot" id="part-fermenter")',
        text,
    )
    if chill_m:
        chip = """    <g class="hotspot" id="part-dimroth-link" data-id="dimroth-link" tabindex="0" role="button" aria-label="Димрот альтернатива">
      <rect x="560" y="300" width="100" height="56" rx="8" fill="#faf9f8" stroke="#c8cdd3"/>
      <text x="572" y="324" font-size="11" fill="#6a7178" font-family="Onest,sans-serif">альт.</text>
      <text x="572" y="342" font-size="12" font-weight="600" fill="#c00000" font-family="Onest,sans-serif">Димрот</text>
      <path class="hit" d="M552 290 h116 v76 h-116 z" fill="rgba(192,0,0,0)" stroke="none"/>
    </g>
"""
        text = text[: chill_m.end(1)] + chip + text[chill_m.start(2) :]

path.write_text(text, encoding="utf-8")
print("patched", path)
print("hit--path count", text.count("hit--path"))
print("hose-clamps", text.count("hose-clamps"))
print("coverage chrome", "schema-coverage" in text)
