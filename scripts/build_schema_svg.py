# -*- coding: utf-8 -*-
"""Build catalog-style side-view SVGs for schema.html (stainless still + brewery)."""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets" / "svg"


def defs(p: str) -> str:
    return f"""
  <defs>
    <linearGradient id="{p}metal" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5c6369"/>
      <stop offset="14%" stop-color="#9aa1a8"/>
      <stop offset="30%" stop-color="#e4e8eb"/>
      <stop offset="44%" stop-color="#f5f7f8"/>
      <stop offset="58%" stop-color="#c8cdd3"/>
      <stop offset="80%" stop-color="#8a9199"/>
      <stop offset="100%" stop-color="#4e555b"/>
    </linearGradient>
    <linearGradient id="{p}metalV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e8ecef"/>
      <stop offset="45%" stop-color="#b7bec5"/>
      <stop offset="100%" stop-color="#7e868e"/>
    </linearGradient>
    <radialGradient id="{p}lid" cx="42%" cy="38%" r="62%">
      <stop offset="0%" stop-color="#f3f5f6"/>
      <stop offset="55%" stop-color="#c8cdd3"/>
      <stop offset="100%" stop-color="#7a8289"/>
    </radialGradient>
    <linearGradient id="{p}dark" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2a2d31"/>
      <stop offset="35%" stop-color="#4a5056"/>
      <stop offset="70%" stop-color="#32363b"/>
      <stop offset="100%" stop-color="#1c1e21"/>
    </linearGradient>
    <linearGradient id="{p}glass" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#6a8a96" stop-opacity="0.45"/>
      <stop offset="22%" stop-color="#d7eef5" stop-opacity="0.55"/>
      <stop offset="48%" stop-color="#f6fcff" stop-opacity="0.28"/>
      <stop offset="78%" stop-color="#8fb3bf" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="#4d6b75" stop-opacity="0.5"/>
    </linearGradient>
    <linearGradient id="{p}glassV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#6d8b96" stop-opacity="0.2"/>
    </linearGradient>
    <linearGradient id="{p}hoseIn" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#c5e4f0"/>
      <stop offset="50%" stop-color="#7eb6c9"/>
      <stop offset="100%" stop-color="#4e8fa6"/>
    </linearGradient>
    <linearGradient id="{p}hoseOut" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f0d4c5"/>
      <stop offset="50%" stop-color="#c98e6e"/>
      <stop offset="100%" stop-color="#a0664a"/>
    </linearGradient>
    <linearGradient id="{p}cu" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7a3e16"/>
      <stop offset="25%" stop-color="#e0a15a"/>
      <stop offset="50%" stop-color="#f3d09a"/>
      <stop offset="75%" stop-color="#c47a38"/>
      <stop offset="100%" stop-color="#6b3412"/>
    </linearGradient>
    <linearGradient id="{p}amber" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#d9b56a" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#a67c3a" stop-opacity="0.45"/>
    </linearGradient>
    <linearGradient id="{p}plastic" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8d949c"/>
      <stop offset="30%" stop-color="#d5dbe0"/>
      <stop offset="70%" stop-color="#b7c0c7"/>
      <stop offset="100%" stop-color="#6e767e"/>
    </linearGradient>
    <linearGradient id="{p}wood" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#d7c4a8"/>
      <stop offset="100%" stop-color="#b89a74"/>
    </linearGradient>
    <filter id="{p}shadow" x="-20%" y="-10%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="8" flood-color="#1a1a1a" flood-opacity="0.18"/>
    </filter>
    <filter id="{p}soft" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="0.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="{p}cubeCut">
      <path d="M80 90 h520 v640 h-520 z M80 90 L360 280 L360 700 L80 700 z"/>
    </clipPath>
    <clipPath id="{p}Spn"><rect x="342" y="160" width="116" height="320" rx="2"/></clipPath>
    <clipPath id="{p}Rpn"><rect x="342" y="500" width="116" height="280" rx="2"/></clipPath>
  </defs>
"""


def helix_p(p: str, cx: float, y0: float, y1: float, rx: float, turns: float, sw: float = 3.2) -> str:
    n = int(turns * 28)
    d = []
    for i in range(n + 1):
        t = i / n * turns * math.pi * 2
        x = cx + rx * math.sin(t)
        y = y0 + (y1 - y0) * (i / n)
        d.append(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}")
    path = " ".join(d)
    return (
        f'<path d="{path}" fill="none" stroke="url(#{p}cu)" stroke-width="{sw}" '
        f'stroke-linecap="round"/>'
        f'<path d="{path}" fill="none" stroke="#f6e2c0" stroke-width="{max(1, sw * 0.28)}" '
        f'stroke-linecap="round" opacity="0.5" transform="translate(-1.1,0)"/>'
    )


def spn_fill(x: float, y: float, w: float, h: float, seed: int = 1) -> str:
    parts = []
    rng = seed
    rows = int(h / 7)
    cols = int(w / 8)
    for r in range(rows):
        for c in range(cols):
            rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
            jx = (rng % 5) - 2
            rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
            jy = (rng % 5) - 2
            px = x + 4 + c * 8 + jx
            py = y + 4 + r * 7 + jy
            rot = (c * 37 + r * 19) % 180
            parts.append(
                f'<path d="M{px:.1f},{py:.1f} q2,-3 5,0 q-2,3 -5,0" fill="none" '
                f'stroke="#9aa3ab" stroke-width="0.7" transform="rotate({rot} {px:.1f} {py:.1f})"/>'
            )
    return "".join(parts)


def rpn_fill(x: float, y: float, w: float, h: float) -> str:
    parts = []
    yy = y + 4
    while yy < y + h - 4:
        parts.append(
            f'<path d="M{x+3:.1f},{yy:.1f} h{w-6:.1f}" fill="none" stroke="#a8b0b7" stroke-width="0.8"/>'
        )
        yy += 5
        parts.append(
            f'<path d="M{x+3:.1f},{yy:.1f} h{w-6:.1f}" fill="none" stroke="#7d868e" stroke-width="0.6"/>'
        )
        yy += 4
    return "".join(parts)


def clamp_band(p: str, cx: float, cy: float, rx: float, ry: float = 6) -> str:
    wing = cx + rx + 8
    return f"""
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{p}metalV)" stroke="#6a7178" stroke-width="0.8"/>
    <rect x="{cx-rx}" y="{cy-4}" width="{rx*2}" height="8" fill="url(#{p}metal)" stroke="#5c6369" stroke-width="0.6"/>
    <ellipse cx="{cx}" cy="{cy-3.5}" rx="{rx*0.92}" ry="{ry*0.55}" fill="#eef1f3" opacity="0.55"/>
    <circle cx="{wing}" cy="{cy}" r="6.5" fill="url(#{p}metal)" stroke="#5c6369" stroke-width="0.7"/>
    <circle cx="{wing}" cy="{cy}" r="2.2" fill="#4e555b"/>
    <rect x="{wing-1.4}" y="{cy-11}" width="2.8" height="8" rx="0.6" fill="#8a9199"/>
    """


def cyl(p, cx, y_top, y_bot, rx, ry=None, fill=None):
    ry = rx * 0.22 if ry is None else ry
    fill = fill or f"url(#{p}metal)"
    left, right = cx - rx, cx + rx
    shine_w = max(3, rx * 0.12)
    return f"""
    <path fill="{fill}" d="M {left:.1f},{y_top:.1f} L {left:.1f},{y_bot:.1f}
      A {rx:.1f},{ry:.1f} 0 0 0 {right:.1f},{y_bot:.1f}
      L {right:.1f},{y_top:.1f}
      A {rx:.1f},{ry:.1f} 0 0 1 {left:.1f},{y_top:.1f} Z"/>
    <ellipse cx="{cx}" cy="{y_top}" rx="{rx}" ry="{ry}" fill="url(#{p}lid)" stroke="#6a7178" stroke-width="0.7"/>
    <ellipse cx="{cx}" cy="{y_bot}" rx="{rx}" ry="{ry}" fill="url(#{p}metalV)" opacity="0.9"/>
    <rect x="{left+rx*0.18:.1f}" y="{y_top+ry:.1f}" width="{shine_w:.1f}" height="{max(8, y_bot-y_top-ry*2):.1f}" rx="{shine_w/2:.1f}" fill="url(#{p}glassV)" opacity="0.55"/>
    """


def pipe(p: str, cx: float, y0: float, y1: float, rx: float) -> str:
    return cyl(p, cx, y0, y1, rx, max(5, rx * 0.22))


def glass_cyl(p, cx, y_top, y_bot, rx):
    return cyl(p, cx, y_top, y_bot, rx, max(6, rx * 0.22), fill=f"url(#{p}glass)")


def barrel(p: str, cx: float, y_top: float, y_bot: float, rx: float, hoops: bool = True) -> str:
    ry = rx * 0.16
    body = cyl(p, cx, y_top, y_bot, rx, ry)
    hoop = ""
    if hoops:
        h = y_bot - y_top
        for t in (0.22, 0.5, 0.78):
            yy = y_top + h * t
            hoop += (
                f'<path fill="#9aa2a9" fill-opacity="0.55" d="M {cx-rx-2:.1f},{yy-4:.1f} '
                f'L {cx-rx-2:.1f},{yy+4:.1f} A {rx+2:.1f},3.2 0 0 0 {cx+rx+2:.1f},{yy+4:.1f} '
                f'L {cx+rx+2:.1f},{yy-4:.1f} A {rx+2:.1f},3.2 0 0 1 {cx-rx-2:.1f},{yy-4:.1f} Z"/>'
            )
    return body + hoop


def hit(d: str) -> str:
    return f'<path class="hit" d="{d}" fill="rgba(192,0,0,0)" stroke="none"/>'


def distiller() -> str:
    p = "d"
    cx = 390
    # vertical stack
    # dimroth 70-250, takeoff 250-330, diopter 330-420, tsarga 420-680, lid 680-742, cube 742-980
    d_helix = helix_p(p, cx, 92, 232, 26, 7.2, 3.4)
    return f"""<svg id="svg-distiller" class="schema-svg" viewBox="0 0 860 1080" xmlns="http://www.w3.org/2000/svg" aria-label="Дистиллятор в профиле, нержавеющая колонна">
{defs(p)}
  <g class="layer" data-layer="root">
    <ellipse cx="400" cy="1028" rx="230" ry="18" fill="#1a1a1a" opacity="0.12"/>
    <path d="M120 1038 h620" stroke="#1a1a1a" stroke-opacity="0.06" stroke-width="2"/>

    <!-- hoses first (behind column fittings) -->
    <g class="hotspot" id="part-hoses" data-id="hoses" tabindex="0" role="button" aria-label="Шланги охлаждения">
      <path d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="url(#{p}hoseIn)" stroke-width="7" stroke-linecap="round"/>
      <path d="M448 108 C560 90, 640 160, 668 260" fill="none" stroke="#eaf6fb" stroke-width="2" transform="translate(0,-1.6)"/>
      <path d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="url(#{p}hoseOut)" stroke-width="7" stroke-linecap="round"/>
      <path d="M448 228 C540 250, 620 340, 668 430" fill="none" stroke="#f8e6da" stroke-width="2" transform="translate(0,-1.4)"/>
      <circle cx="668" cy="260" r="6" fill="#8a9199"/>
      <circle cx="668" cy="430" r="6" fill="#8a9199"/>
      {hit("M430 70 C580 50 700 150 690 270 C690 360 650 430 650 450 L690 450 C700 300 720 80 430 55 Z")}
    </g>

    <g class="hotspot" id="part-cube" data-id="cube" tabindex="0" role="button" aria-label="Перегонный куб">
      {barrel(p, cx, 760, 978, 148)}
      <!-- legs -->
      <rect x="268" y="978" width="14" height="42" rx="2" fill="url(#{p}metalV)"/>
      <rect x="498" y="978" width="14" height="42" rx="2" fill="url(#{p}metalV)"/>
      <rect x="330" y="978" width="14" height="46" rx="2" fill="url(#{p}metalV)"/>
      <rect x="436" y="978" width="14" height="46" rx="2" fill="url(#{p}metalV)"/>
      <ellipse cx="275" cy="1022" rx="12" ry="4" fill="#3a3a3a" opacity="0.35"/>
      <ellipse cx="505" cy="1022" rx="12" ry="4" fill="#3a3a3a" opacity="0.35"/>
      <ellipse cx="337" cy="1026" rx="12" ry="4" fill="#3a3a3a" opacity="0.35"/>
      <ellipse cx="443" cy="1026" rx="12" ry="4" fill="#3a3a3a" opacity="0.35"/>
      <!-- handles -->
      <path d="M242 820 q-28 20 -8 55" fill="none" stroke="url(#{p}metal)" stroke-width="7" stroke-linecap="round"/>
      <path d="M538 820 q28 20 8 55" fill="none" stroke="url(#{p}metal)" stroke-width="7" stroke-linecap="round"/>
      <!-- drain visible on cube -->
      <g pointer-events="none">
        <rect x="372" y="968" width="36" height="18" rx="3" fill="url(#{p}metal)"/>
        <circle cx="408" cy="977" r="7" fill="#6a7178"/>
        <rect x="404" y="984" width="8" height="16" rx="1" fill="#8a9199"/>
      </g>
      {hit("M242 748 h296 v240 h-40 v40 h-216 v-40 h-40 z")}
    </g>

    <g class="hotspot" id="part-ten" data-id="ten" tabindex="0" role="button" aria-label="ТЭН">
      <!-- clamp flange on cube wall -->
      <ellipse cx="246" cy="888" rx="22" ry="28" fill="url(#{p}metal)" stroke="#5c6369" stroke-width="1"/>
      <ellipse cx="246" cy="888" rx="10" ry="14" fill="#4e555b"/>
      <rect x="168" y="868" width="82" height="40" rx="8" fill="url(#{p}metal)"/>
      <rect x="174" y="874" width="70" height="10" fill="#fff" opacity="0.25"/>
      <circle cx="176" cy="888" r="9" fill="url(#{p}dark)"/>
      <rect x="148" y="882" width="28" height="12" rx="3" fill="#2a2d31"/>
      {clamp_band(p, 246, 860, 20, 5)}
      {hit("M145 850 h120 v80 h-120 z")}
    </g>

    <g class="hotspot" id="part-pid" data-id="pid" tabindex="0" role="button" aria-label="PID">
      <rect x="36" y="820" width="96" height="78" rx="3" fill="url(#{p}dark)" stroke="#1a1a1a" stroke-width="1"/>
      <rect x="46" y="832" width="76" height="28" rx="1" fill="#0d1210"/>
      <rect x="50" y="836" width="48" height="20" fill="#1a2a22"/>
      <text x="54" y="851" font-family="ui-monospace,monospace" font-size="11" fill="#c00000">78.4</text>
      <circle cx="108" cy="846" r="4" fill="#c00000" opacity="0.85"/>
      <rect x="50" y="870" width="22" height="14" rx="1" fill="#3a4046"/>
      <rect x="78" y="870" width="22" height="14" rx="1" fill="#3a4046"/>
      <rect x="106" y="870" width="14" height="14" rx="1" fill="#8a0000"/>
      <!-- cables to TEN -->
      <path d="M132 888 C170 888, 200 888, 168 888" fill="none" stroke="#2a2d31" stroke-width="4"/>
      <path d="M132 896 C160 930, 200 910, 168 888" fill="none" stroke="#c00000" stroke-width="2.2"/>
      {hit("M32 816 h108 v90 h-108 z")}
    </g>

    <g class="hotspot" id="part-lid" data-id="lid" tabindex="0" role="button" aria-label="Крышка куба">
      <ellipse cx="{cx}" cy="758" rx="132" ry="22" fill="url(#{p}lid)" stroke="#6a7178" stroke-width="1"/>
      <path d="M270 752 Q{cx} 700 {cx+120} 752" fill="url(#{p}lid)" stroke="#7a8289" stroke-width="0.8"/>
      <ellipse cx="{cx}" cy="712" rx="36" ry="10" fill="url(#{p}metal)"/>
      {clamp_band(p, cx, 724, 40, 7)}
      <!-- extra port -->
      <circle cx="470" cy="738" r="9" fill="url(#{p}metal)" stroke="#5c6369"/>
      <circle cx="470" cy="738" r="4" fill="#dfe3e6"/>
      {hit("M258 698 h264 v70 h-264 z")}
    </g>

    <g class="hotspot" id="part-tsarga-assy" data-id="tsarga-assy" tabindex="0" role="button" aria-label="Царга">
      {pipe(p, cx, 430, 708, 32)}
      {clamp_band(p, cx, 438, 38, 6)}
      {clamp_band(p, cx, 530, 36, 5)}
      {clamp_band(p, cx, 622, 36, 5)}
      {clamp_band(p, cx, 700, 38, 6)}
      {hit("M350 420 h80 v292 h-80 z")}
    </g>

    <g class="hotspot" id="part-diopter" data-id="diopter" tabindex="0" role="button" aria-label="Диоптр">
      {clamp_band(p, cx, 338, 38, 6)}
      {glass_cyl(p, cx, 342, 422, 30)}
      <path d="M{cx-18} 352 l22 18" stroke="#fff" stroke-width="3" opacity="0.55" stroke-linecap="round"/>
      <path d="M{cx-10} 368 q8 10 -2 22" fill="none" stroke="#c00000" stroke-opacity="0.25" stroke-width="1.5"/>
      {clamp_band(p, cx, 426, 38, 6)}
      {hit("M350 328 h80 v108 h-80 z")}
    </g>

    <g class="hotspot" id="part-takeoff" data-id="takeoff" tabindex="0" role="button" aria-label="Узел отбора">
      {pipe(p, cx, 252, 336, 34)}
      {clamp_band(p, cx, 258, 40, 6)}
      {clamp_band(p, cx, 328, 40, 6)}
      <!-- side arm -->
      <rect x="{cx+34}" y="286" width="86" height="22" rx="4" fill="url(#{p}metal)"/>
      <rect x="{cx+110}" y="278" width="48" height="38" rx="4" fill="url(#{p}metalV)" stroke="#5c6369" stroke-width="0.7"/>
      <circle cx="{cx+158}" cy="297" r="11" fill="url(#{p}metal)" stroke="#4e555b"/>
      <rect x="{cx+154}" y="274" width="8" height="16" rx="1" fill="#8a9199"/>
      <path d="M{cx+134} 316 v18 h24" fill="none" stroke="#8a9199" stroke-width="4" stroke-linecap="round"/>
      {hit("M356 248 h210 v100 h-210 z")}
    </g>

    <g class="hotspot" id="part-dimroth" data-id="dimroth" tabindex="0" role="button" aria-label="Холодильник Димрота">
      {clamp_band(p, cx, 248, 42, 6)}
      {glass_cyl(p, cx, 78, 248, 40)}
      {d_helix}
      <!-- water nipples -->
      <rect x="{cx+40}" y="100" width="22" height="10" rx="2" fill="url(#{p}metal)"/>
      <rect x="{cx+40}" y="220" width="22" height="10" rx="2" fill="url(#{p}metal)"/>
      <ellipse cx="{cx}" cy="70" rx="28" ry="8" fill="url(#{p}metalV)" stroke="#5c6369"/>
      <rect x="{cx-8}" y="52" width="16" height="20" rx="2" fill="url(#{p}metal)"/>
      <path d="M{cx-22} 92 l16 14" stroke="#fff" stroke-width="3.5" opacity="0.5" stroke-linecap="round"/>
      {hit("M340 48 h110 v214 h-110 z")}
    </g>

    <g class="hotspot" id="part-parrot" data-id="parrot" tabindex="0" role="button" aria-label="Попугай">
      <path d="M{cx+134} 334 C{cx+180} 350, {cx+190} 390, {cx+186} 430" fill="none" stroke="url(#{p}metal)" stroke-width="4"/>
      <rect x="548" y="430" width="52" height="78" rx="4" fill="url(#{p}glass)" stroke="#6d8b96" stroke-width="1.2"/>
      <ellipse cx="574" cy="430" rx="26" ry="7" fill="#eef8fb"/>
      <ellipse cx="574" cy="508" rx="26" ry="7" fill="url(#{p}metalV)"/>
      <rect x="542" y="500" width="64" height="10" rx="2" fill="url(#{p}metal)"/>
      <path d="M600 470 h18 v40" fill="none" stroke="#8a9199" stroke-width="3" stroke-linecap="round"/>
      <rect x="566" y="448" width="6" height="40" rx="1" fill="#c8cdd3" opacity="0.8"/>
      {hit("M530 410 h100 v110 h-100 z")}
    </g>

    <g class="hotspot" id="part-receiver" data-id="receiver" tabindex="0" role="button" aria-label="Приёмная ёмкость">
      <ellipse cx="700" cy="980" rx="48" ry="10" fill="#1a1a1a" opacity="0.1"/>
      <path d="M658 820 q-8 90 0 160 h84 q8 -70 0 -160 z" fill="url(#{p}glass)" stroke="#7a929c" stroke-width="1.3"/>
      <ellipse cx="700" cy="820" rx="42" ry="12" fill="#f3fafc" stroke="#8fb3bf"/>
      <path d="M662 880 q38 20 76 0 v70 q-38 16 -76 0 z" fill="url(#{p}amber)"/>
      <rect x="686" y="800" width="28" height="22" rx="2" fill="url(#{p}metal)"/>
      {hit("M648 798 h104 v190 h-104 z")}
    </g>
  </g>

  <!-- CUBE CUTAWAY -->
  <g class="layer" data-layer="cube-detail" hidden>
    <ellipse cx="430" cy="1000" rx="260" ry="16" fill="#1a1a1a" opacity="0.1"/>
    <g class="hotspot" id="part-cube-inner" data-id="cube" tabindex="0" role="button" aria-label="Куб">
      {barrel(p, 400, 220, 820, 200, True)}
      <!-- cutaway overlay: inner liquid + wall thickness -->
      <path d="M200 240 L400 360 L400 800 L200 800 z" fill="#f3f1ef" opacity="0.55"/>
      <path d="M218 360 L400 360 L400 790 L218 790 z" fill="url(#{p}amber)"/>
      <path d="M200 240 L400 360 L400 800 L218 800 L218 250 z" fill="none" stroke="#c00000" stroke-width="1.2" stroke-dasharray="5 4" opacity="0.55"/>
      {hit("M190 200 h420 v640 h-420 z")}
    </g>
    <g class="hotspot" id="part-lid-d" data-id="lid" tabindex="0" role="button" aria-label="Крышка">
      <ellipse cx="400" cy="218" rx="188" ry="28" fill="url(#{p}lid)" stroke="#6a7178"/>
      <path d="M230 210 Q400 150 570 210" fill="url(#{p}lid)"/>
      {clamp_band(p, 400, 188, 48, 8)}
      {hit("M210 145 h380 v90 h-380 z")}
    </g>
    <g class="hotspot" id="part-ten-d" data-id="ten" tabindex="0" role="button" aria-label="ТЭН">
      <ellipse cx="210" cy="620" rx="28" ry="36" fill="url(#{p}metal)" stroke="#5c6369"/>
      <rect x="80" y="598" width="140" height="44" rx="8" fill="url(#{p}metal)"/>
      {helix_p(p, 320, 580, 720, 70, 4.5, 4)}
      <circle cx="88" cy="620" r="10" fill="url(#{p}dark)"/>
      {hit("M70 560 h340 v190 h-340 z")}
    </g>
    <g class="hotspot" id="part-drain-d" data-id="drain" tabindex="0" role="button" aria-label="Кран слива">
      <rect x="372" y="808" width="56" height="28" rx="4" fill="url(#{p}metal)" stroke="#5c6369"/>
      <circle cx="428" cy="822" r="10" fill="#6a7178"/>
      <rect x="420" y="832" width="16" height="28" rx="2" fill="#8a9199"/>
      {hit("M360 800 h90 v70 h-90 z")}
    </g>
    <g class="hotspot" id="part-thermo-d" data-id="thermo" tabindex="0" role="button" aria-label="Термометр">
      <circle cx="560" cy="300" r="36" fill="url(#{p}metalV)" stroke="#5c6369" stroke-width="2"/>
      <circle cx="560" cy="300" r="26" fill="#f4f1ea"/>
      <circle cx="560" cy="300" r="3" fill="#c00000"/>
      <path d="M560 300 L572 278" stroke="#c00000" stroke-width="2"/>
      {hit("M520 260 h80 v80 h-80 z")}
    </g>
    <g class="hotspot" id="part-prv-d" data-id="prv" tabindex="0" role="button" aria-label="Клапан">
      <rect x="500" y="168" width="44" height="36" rx="4" fill="url(#{p}metal)" stroke="#5c6369"/>
      <circle cx="522" cy="176" r="8" fill="#dfe3e6"/>
      <rect x="516" y="148" width="12" height="22" rx="2" fill="#8a9199"/>
      {hit("M490 145 h70 v70 h-70 z")}
    </g>
  </g>

  <!-- TSARGA CUTAWAY -->
  <g class="layer" data-layer="tsarga-detail" hidden>
    <g class="hotspot" id="part-tsarga-d" data-id="tsarga" tabindex="0" role="button" aria-label="Царга">
      {pipe(p, 400, 80, 980, 70)}
      {hit("M320 70 h160 v920 h-160 z")}
    </g>
    <g class="hotspot" id="part-spn" data-id="packing-spn" tabindex="0" role="button" aria-label="СПН">
      <g clip-path="url(#dSpn)">
        <rect x="342" y="160" width="116" height="320" fill="#d8dde1"/>
        {spn_fill(342, 160, 116, 320, 7)}
      </g>
      {hit("M340 158 h120 v324 h-120 z")}
    </g>
    <g class="hotspot" id="part-rpn" data-id="packing-rpn" tabindex="0" role="button" aria-label="РПН">
      <g clip-path="url(#dRpn)">
        <rect x="342" y="500" width="116" height="280" fill="#cfd5da"/>
        {rpn_fill(342, 500, 116, 280)}
      </g>
      {hit("M340 498 h120 v284 h-120 z")}
    </g>
    <g class="hotspot" id="part-clamp-t" data-id="clamp-tsarga" tabindex="0" role="button" aria-label="Кламп">
      {clamp_band(p, 400, 88, 82, 10)}
      {clamp_band(p, 400, 972, 82, 10)}
      {hit("M300 70 h200 v40 h-200 z M300 950 h200 v40 h-200 z")}
    </g>
    <g class="hotspot" id="part-gasket-t" data-id="gasket-tsarga" tabindex="0" role="button" aria-label="Прокладка">
      <ellipse cx="400" cy="102" rx="58" ry="8" fill="#f4f4f0" stroke="#c8c8c0" stroke-width="1.2"/>
      <ellipse cx="400" cy="958" rx="58" ry="8" fill="#f4f4f0" stroke="#c8c8c0" stroke-width="1.2"/>
      {hit("M340 90 h120 v24 h-120 z M340 946 h120 v24 h-120 z")}
    </g>
  </g>

  <!-- DIMROTH CUTAWAY -->
  <g class="layer" data-layer="dimroth-detail" hidden>
    <g class="hotspot" id="part-dimroth-d" data-id="dimroth" tabindex="0" role="button" aria-label="Димрот">
      <rect x="300" y="80" width="200" height="820" rx="16" fill="url(#{p}glass)" stroke="#5f7f8a" stroke-width="2"/>
      <ellipse cx="400" cy="80" rx="100" ry="22" fill="#eef8fb" stroke="#8fb3bf" stroke-width="1.4"/>
      <ellipse cx="400" cy="900" rx="100" ry="22" fill="url(#{p}glass)" stroke="#5f7f8a"/>
      {hit("M290 58 h220 v870 h-220 z")}
    </g>
    <g class="hotspot" id="part-coil" data-id="dimroth" tabindex="0" role="button" aria-label="Змеевик">
      {helix_p(p, 400, 130, 850, 62, 14, 6)}
      {hit("M330 120 h140 v740 h-140 z")}
    </g>
    <g class="hotspot" id="part-hoses-d" data-id="hoses" tabindex="0" role="button" aria-label="Шланги">
      <rect x="500" y="140" width="40" height="16" rx="3" fill="url(#{p}metal)"/>
      <rect x="500" y="780" width="40" height="16" rx="3" fill="url(#{p}metal)"/>
      <path d="M540 148 C640 148, 680 220, 700 300" fill="none" stroke="url(#{p}hoseIn)" stroke-width="10" stroke-linecap="round"/>
      <path d="M540 788 C640 788, 700 700, 720 600" fill="none" stroke="url(#{p}hoseOut)" stroke-width="10" stroke-linecap="round"/>
      {hit("M498 120 h240 v700 h-80 v-500 h-160 z")}
    </g>
  </g>

  <!-- TAKEOFF DETAIL -->
  <g class="layer" data-layer="takeoff-detail" hidden>
    <g class="hotspot" id="part-takeoff-d" data-id="takeoff" tabindex="0" role="button" aria-label="Узел отбора">
      {pipe(p, 320, 200, 780, 70)}
      <rect x="390" y="430" width="180" height="48" rx="8" fill="url(#{p}metal)"/>
      {clamp_band(p, 320, 220, 80, 10)}
      {clamp_band(p, 320, 760, 80, 10)}
      {hit("M240 190 h360 v610 h-360 z")}
    </g>
    <g class="hotspot" id="part-needle" data-id="needle" tabindex="0" role="button" aria-label="Игольчатый кран">
      <rect x="560" y="410" width="120" height="88" rx="8" fill="url(#{p}metalV)" stroke="#5c6369" stroke-width="1"/>
      <circle cx="680" cy="454" r="22" fill="url(#{p}metal)" stroke="#4e555b"/>
      <rect x="672" y="400" width="16" height="36" rx="2" fill="#8a9199"/>
      <path d="M620 498 v40 h50" fill="none" stroke="#8a9199" stroke-width="8" stroke-linecap="round"/>
      {hit("M550 390 h160 v160 h-160 z")}
    </g>
    <g class="hotspot" id="part-hoses-to" data-id="hoses" tabindex="0" role="button" aria-label="Шланги">
      <path d="M670 538 C760 560, 780 640, 740 720" fill="none" stroke="url(#{p}hoseOut)" stroke-width="8" stroke-linecap="round"/>
      {hit("M650 520 h140 v220 h-140 z")}
    </g>
  </g>
</svg>"""


def brewery() -> str:
    p = "b"
    return f"""<svg id="svg-brewery" class="schema-svg" viewBox="0 0 980 820" xmlns="http://www.w3.org/2000/svg" aria-label="Домашняя пивоварня в профиле" hidden="hidden">
{defs(p)}
  <g class="layer" data-layer="brew-root">
    <ellipse cx="490" cy="790" rx="380" ry="18" fill="#1a1a1a" opacity="0.1"/>
    <rect x="40" y="772" width="900" height="16" rx="2" fill="url(#{p}wood)" opacity="0.55"/>

    <g class="hotspot" id="part-brew-hoses" data-id="brew-hoses" tabindex="0" role="button" aria-label="Шланги">
      <path d="M250 560 C300 620, 380 640, 470 600" fill="none" stroke="url(#{p}hoseIn)" stroke-width="7" stroke-linecap="round"/>
      <path d="M560 430 C620 500, 680 620, 760 650" fill="none" stroke="url(#{p}hoseOut)" stroke-width="6" stroke-linecap="round"/>
      {hit("M240 540 h200 v90 h-200 z M540 420 h250 v250 h-80 v-160 h-170 z")}
    </g>

    <g class="hotspot" id="part-mash" data-id="mash" tabindex="0" role="button" aria-label="Заторник">
      {barrel(p, 230, 220, 560, 130, True)}
      <ellipse cx="230" cy="218" rx="118" ry="20" fill="url(#{p}lid)" stroke="#6a7178"/>
      <path d="M130 214 Q230 168 330 214" fill="url(#{p}lid)"/>
      <rect x="214" y="178" width="32" height="28" rx="3" fill="url(#{p}metal)"/>
      <!-- handles -->
      <path d="M100 320 q-24 18 -6 48" fill="none" stroke="url(#{p}metal)" stroke-width="7" stroke-linecap="round"/>
      <path d="M360 320 q24 18 6 48" fill="none" stroke="url(#{p}metal)" stroke-width="7" stroke-linecap="round"/>
      <rect x="216" y="560" width="28" height="36" rx="2" fill="url(#{p}metalV)"/>
      <ellipse cx="230" cy="598" rx="16" ry="5" fill="#3a3a3a" opacity="0.3"/>
      {hit("M96 168 h268 v430 h-268 z")}
    </g>

    <g class="hotspot" id="part-ten-brew" data-id="ten-brew" tabindex="0" role="button" aria-label="ТЭН">
      <ellipse cx="104" cy="430" rx="20" ry="26" fill="url(#{p}metal)" stroke="#5c6369"/>
      <rect x="40" y="414" width="70" height="32" rx="7" fill="url(#{p}metal)"/>
      <circle cx="46" cy="430" r="8" fill="url(#{p}dark)"/>
      {hit("M32 400 h90 v60 h-90 z")}
    </g>

    <g class="hotspot" id="part-pid-brew" data-id="pid-brew" tabindex="0" role="button" aria-label="PID">
      <rect x="48" y="250" width="88" height="70" rx="3" fill="url(#{p}dark)"/>
      <rect x="56" y="260" width="72" height="24" fill="#0d1210"/>
      <text x="62" y="278" font-family="ui-monospace,monospace" font-size="12" fill="#c00000">65.0</text>
      <rect x="56" y="292" width="20" height="14" fill="#3a4046"/>
      <rect x="82" y="292" width="20" height="14" fill="#3a4046"/>
      <path d="M92 320 C92 360, 70 390, 48 414" fill="none" stroke="#2a2d31" stroke-width="3.5"/>
      {hit("M44 246 h96 v80 h-96 z")}
    </g>

    <g class="hotspot" id="part-chiller" data-id="chiller" tabindex="0" role="button" aria-label="Чиллер">
      <rect x="430" y="240" width="14" height="320" rx="3" fill="url(#{p}cu)"/>
      <rect x="546" y="240" width="14" height="320" rx="3" fill="url(#{p}cu)"/>
      {helix_p(p, 495, 250, 540, 58, 9, 5)}
      <rect x="424" y="228" width="144" height="16" rx="3" fill="url(#{p}cu)"/>
      <rect x="470" y="200" width="18" height="36" fill="url(#{p}metal)"/>
      <rect x="502" y="200" width="18" height="36" fill="url(#{p}metal)"/>
      <path d="M479 200 C400 160, 360 180, 340 210" fill="none" stroke="url(#{p}hoseIn)" stroke-width="6"/>
      <path d="M511 200 C600 150, 640 180, 660 230" fill="none" stroke="url(#{p}hoseOut)" stroke-width="6"/>
      {hit("M418 190 h160 v390 h-160 z")}
    </g>

    <g class="hotspot" id="part-fermenter" data-id="fermenter" tabindex="0" role="button" aria-label="Ферментер">
      <path d="M700 260 l70 -10 l70 10 v390 l-70 16 l-70 -16 z" fill="url(#{p}plastic)" stroke="#6e767e" stroke-width="1.2"/>
      <ellipse cx="770" cy="250" rx="72" ry="18" fill="#e8edf0" stroke="#8a9298"/>
      <ellipse cx="770" cy="650" rx="70" ry="16" fill="url(#{p}metalV)"/>
      <path d="M712 420 q58 24 116 0 v200 q-58 20 -116 0 z" fill="#c9a24a" opacity="0.28"/>
      <rect x="748" y="236" width="44" height="18" rx="2" fill="url(#{p}metal)"/>
      <!-- spigot -->
      <rect x="838" y="580" width="40" height="16" rx="3" fill="url(#{p}metal)"/>
      <circle cx="878" cy="588" r="8" fill="#6a7178"/>
      {hit("M698 230 h160 v450 h-160 z")}
    </g>

    <g class="hotspot" id="part-airlock" data-id="airlock" tabindex="0" role="button" aria-label="Гидрозатвор">
      <rect x="760" y="188" width="20" height="50" rx="3" fill="#dfe8ec" stroke="#7a929c"/>
      <ellipse cx="770" cy="188" rx="16" ry="7" fill="#eef6f8" stroke="#7a929c"/>
      <path d="M754 210 h32" stroke="#8fb3bf" stroke-width="2"/>
      <circle cx="770" cy="210" r="5" fill="#9ec5d8" opacity="0.8"/>
      {hit("M748 170 h44 v70 h-44 z")}
    </g>

    <g class="hotspot" id="part-sanitizer" data-id="sanitizer" tabindex="0" role="button" aria-label="Дезинфекция">
      <rect x="40" y="640" width="36" height="88" rx="4" fill="#3d6b5c"/>
      <rect x="46" y="648" width="24" height="40" fill="#2a4e44"/>
      <rect x="50" y="622" width="16" height="20" rx="2" fill="#8a9199"/>
      <ellipse cx="58" cy="640" rx="16" ry="6" fill="#4e8a74"/>
      {hit("M36 618 h44 v116 h-44 z")}
    </g>

    <g class="hotspot" id="part-malt" data-id="malt" tabindex="0" role="button" aria-label="Солод и дрожжи">
      <path d="M92 700 q8 -70 28 -70 q20 0 28 70 z" fill="#c4a36a" stroke="#8a7040"/>
      <ellipse cx="120" cy="700" rx="28" ry="8" fill="#a9844a"/>
      <rect x="150" y="668" width="22" height="36" rx="3" fill="#7a1f1f"/>
      <rect x="154" y="658" width="14" height="12" fill="#c00000"/>
      {hit("M88 624 h90 v90 h-90 z")}
    </g>
  </g>

  <g class="layer" data-layer="mash-detail" hidden>
    <g class="hotspot" id="part-mash-d" data-id="mash" tabindex="0" role="button" aria-label="Заторник">
      {barrel(p, 400, 140, 700, 210, True)}
      <path d="M190 160 L400 280 L400 680 L190 680 z" fill="#f3f1ef" opacity="0.5"/>
      <path d="M210 300 L400 300 L400 660 L210 660 z" fill="#c9a24a" opacity="0.35"/>
      {hit("M180 120 h440 v600 h-440 z")}
    </g>
    <g class="hotspot" id="part-ten-bd" data-id="ten-brew" tabindex="0" role="button" aria-label="ТЭН">
      <rect x="80" y="430" width="150" height="48" rx="8" fill="url(#{p}metal)"/>
      {helix_p(p, 340, 400, 620, 90, 4, 5)}
      {hit("M70 390 h360 v250 h-360 z")}
    </g>
    <g class="hotspot" id="part-pid-bd" data-id="pid-brew" tabindex="0" role="button" aria-label="PID">
      <rect x="700" y="180" width="120" height="90" rx="3" fill="url(#{p}dark)"/>
      <rect x="712" y="194" width="96" height="32" fill="#0d1210"/>
      <text x="720" y="216" font-family="ui-monospace,monospace" font-size="14" fill="#c00000">65.0</text>
      {hit("M690 170 h140 v110 h-140 z")}
    </g>
    <g class="hotspot" id="part-drain-b" data-id="drain-brew" tabindex="0" role="button" aria-label="Кран слива">
      <rect x="372" y="688" width="56" height="28" rx="4" fill="url(#{p}metal)"/>
      <rect x="420" y="714" width="14" height="30" rx="2" fill="#8a9199"/>
      {hit("M360 680 h90 v80 h-90 z")}
    </g>
  </g>

  <g class="layer" data-layer="fermenter-detail" hidden>
    <g class="hotspot" id="part-ferm-d" data-id="fermenter" tabindex="0" role="button" aria-label="Ферментер">
      <path d="M320 160 l140 -18 l140 18 v520 l-140 22 l-140 -22 z" fill="url(#{p}plastic)" stroke="#6e767e" stroke-width="1.4"/>
      <ellipse cx="460" cy="142" rx="144" ry="24" fill="#e8edf0" stroke="#8a9298"/>
      <path d="M340 360 q120 40 240 0 v280 q-120 36 -240 0 z" fill="#c9a24a" opacity="0.3"/>
      {hit("M310 120 h300 v600 h-300 z")}
    </g>
    <g class="hotspot" id="part-air-d" data-id="airlock" tabindex="0" role="button" aria-label="Гидрозатвор">
      <rect x="440" y="40" width="40" height="110" rx="6" fill="#dfe8ec" stroke="#7a929c" stroke-width="1.4"/>
      <ellipse cx="460" cy="40" rx="28" ry="10" fill="#eef6f8" stroke="#7a929c"/>
      <circle cx="460" cy="90" r="10" fill="#9ec5d8"/>
      <circle cx="460" cy="118" r="7" fill="#7eb6c9"/>
      {hit("M420 24 h80 v140 h-80 z")}
    </g>
    <g class="hotspot" id="part-valve-b" data-id="valve-brew" tabindex="0" role="button" aria-label="Кран">
      <rect x="598" y="560" width="80" height="28" rx="4" fill="url(#{p}metal)"/>
      <circle cx="678" cy="574" r="14" fill="#6a7178"/>
      {hit("M590 548 h110 v55 h-110 z")}
    </g>
  </g>
</svg>"""


def splice_into_html() -> None:
    import re

    html_path = Path(__file__).resolve().parents[1] / "schema.html"
    html = html_path.read_text(encoding="utf-8")
    d = distiller()
    b = brewery()
    if " hidden" not in b[:120]:
        b = b.replace('<svg id="svg-brewery"', '<svg id="svg-brewery" hidden', 1)
    new_html, n = re.subn(
        r'<svg id="svg-distiller"[\s\S]*?</svg>\s*(?:<!--.*?-->\s*)?<svg[^>]*id="svg-brewery"[\s\S]*?</svg>',
        d + "\n          " + b,
        html,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"schema.html splice failed, replacements={n}")
    html_path.write_text(new_html, encoding="utf-8")
    print("spliced into", html_path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "distiller.svg").write_text(distiller(), encoding="utf-8")
    (OUT / "brewery.svg").write_text(brewery(), encoding="utf-8")
    splice_into_html()
    print("wrote", OUT / "distiller.svg", OUT / "brewery.svg")


if __name__ == "__main__":
    main()
