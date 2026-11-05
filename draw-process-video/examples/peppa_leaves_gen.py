#!/usr/bin/env python3
"""Peppa jumping in autumn leaf pile outdoors (drawing-peppa-pig-17).
Fills use paint-bucket seeds; large flats are never brush-painted.
Thin props (trunks, rake, leaf accents) use solid concentric/parallel strokes."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(17)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['wood', [160, 100, 55]], ['wood2', [120, 70, 40]],
 ['leaf1', [230, 120, 40]],   # orange
 ['leaf2', [240, 190, 50]],   # gold
 ['leaf3', [200, 55, 45]],    # red
 ['leaf4', [180, 95, 35]],    # brown-orange
]
assert len(pal) <= 22

def T(p, s, ox, oy):
    return [round(ox + (p[0] - 289) * s, 1), round(oy + (p[1] - 40) * s, 1)]
def char(s, ox, oy, body='dress'):
    r = []
    for o in ops[:44]:
        o = dict(o)
        if o['op'] == 'stroke':
            o['pts'] = [T(p, s, ox, oy) for p in o['pts']]
        if o['op'] == 'fill' and o['seeds'][0][1] > 600:
            for cx in (419, 523):
                pts = []
                for f in (0.75, 0.5, 0.25):
                    pts += [T((cx + 30 * f * math.cos(2 * math.pi * k / 30),
                               679 + 12 * f * math.sin(2 * math.pi * k / 30)), s, ox, oy)
                            for k in range(31)]
                r.append({'op': 'stroke', 'amp': 0, 'dl': 0.006, 'pts': pts})
            continue
        if o['op'] == 'fill':
            o['seeds'] = [T(p, s, ox, oy) for p in o['seeds']]
        if o['op'] == 'color' and o['c'] == 'dress':
            o['c'] = body
        r.append(o)
    return r
def S(pts, amp=1.0, dl=0.009):
    return {'op': 'stroke', 'amp': amp, 'dl': dl, 'pts': [[round(x, 1), round(y, 1)] for x, y in pts]}
def C(c): return {'op': 'color', 'c': c}
def F(*seeds): return {'op': 'fill', 'seeds': [list(x) for x in seeds]}
def cr(P, n=10):
    P = [P[0]] + P + [P[-1]]; o = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1:i + 3]
        for k in range(n):
            t = k / n
            o.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t
                                 + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return o + [P[-2]]
def ell(cx, cy, rx, ry, n=72, extra=4):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n))
            for k in range(n + extra)]
def dot(cx, cy, r):
    pts = []
    for rr in [r, r * .66, r * .33, 1]:
        pts += ell(cx, cy, rr, rr, 24, 1)
    return S(pts, 0, 0.006)
def poly(P): return list(P) + [P[0], P[1]]
def side(s, ox, oy, y, right):
    dress = ops[12]['pts']
    P = [T(p, s, ox, oy) for p in dress]
    c = [p for p in P if abs(p[1] - y) < 14]
    if not c:
        c = sorted(P, key=lambda q: abs(q[1] - y))[:8]
    p = max(c, key=lambda q: q[0]) if right else min(c, key=lambda q: q[0])
    return [p[0] + (-6 if right else 6), p[1]]
def irregular_oval(cx, cy, rx, ry, n=80, wobble=0.08):
    P = []
    for k in range(n):
        a = 2 * math.pi * k / n
        b = 1 + wobble * math.sin(3 * a + 0.4) + 0.04 * math.sin(5 * a)
        P.append((cx + rx * b * math.cos(a), cy + ry * b * math.sin(a)))
    return P + P[:3]
def leaf_shape(cx, cy, rx, ry, rot=0.0, n=36):
    P = []
    for k in range(n):
        t = 2 * math.pi * k / n
        r = (0.55 + 0.45 * abs(math.sin(t)))
        x = rx * r * math.cos(t)
        y = ry * r * math.sin(t)
        ca, sa = math.cos(rot), math.sin(rot)
        P.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return P + P[:3]
def rod_strokes(a, b, w=6, n=5):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    rs = []
    for i in range(n):
        o = -w + 2 * w * i / max(1, n - 1)
        rs.append(S([(ax + nx * o, ay + ny * o), (bx + nx * o, by + ny * o)], 0.0, 0.007))
    return rs
def fill_oval_conc(cx, cy, rx, ry, steps=8, n=40):
    """Solid concentric ovals — reliable fill for medium shapes."""
    rs = []
    for i in range(steps):
        f = 1.0 - i / steps
        rs.append(S(ell(cx, cy, rx * f, ry * f, n, 2), 0.0, 0.006))
    return rs
def fill_irreg_conc(cx, cy, rx, ry, wobble=0.1, steps=7):
    rs = []
    for i in range(steps):
        f = 1.0 - i / (steps + 0.2)
        P = irregular_oval(cx, cy, rx * f, ry * f, 48, wobble * f)
        rs.append(S(P, 0.0, 0.006))
    return rs

# ---- Peppa left-center ----
PS, PX, PY = 0.64, 150, 75
out += char(PS, PX, PY, 'dress')
out += [{'op': 'pause', 's': 0.4}]

xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r = min(xs), max(xs)
head_top, body_bot = min(ys), max(ys)
print('peppa box', (body_l - 12, head_top - 12, body_r + 12, body_bot + 12))

# ---- Leaf pile: well-sealed mild-wobble oval ----
PCX, PCY, PRX, PRY = 820, 630, 330, 140
PILE = irregular_oval(PCX, PCY, PRX, PRY, 160, 0.05)
PILE = PILE + PILE[:16]
out += [C('ink'), S(PILE, 0.04, 0.007)]
PILE2 = irregular_oval(PCX, PCY, PRX - 7, PRY - 5, 120, 0.04)
out += [S(PILE2 + PILE2[:12], 0.04, 0.007)]
PILE3 = irregular_oval(PCX, PCY, PRX - 14, PRY - 10, 100, 0.03)
out += [S(PILE3 + PILE3[:10], 0.0, 0.006)]

# ---- Trees: trunks as parallel wood strokes; crowns as concentric ----
TREES = [
    # trunk_x, trunk_top, trunk_bot, half_w, crown_cx, crown_cy, crx, cry, main_color
    (200, 250, 500, 14, 200, 210, 90, 75, 'leaf1'),
    (560, 180, 490, 16, 560, 155, 105, 85, 'leaf2'),
    (1160, 220, 510, 14, 1160, 195, 95, 78, 'leaf3'),
]

# Trunk outlines + solid wood fill via parallel strokes
for tx, tt, tb, tw, *_ in TREES:
    out += [C('ink'),
            S(poly([(tx - tw, tt), (tx + tw, tt), (tx + tw + 3, tb), (tx - tw - 3, tb)]), 0.05, 0.008)]
    out += [C('wood')] + rod_strokes((tx, tt), (tx, tb), tw - 1, max(5, tw // 2))
    out += [C('wood2')] + rod_strokes((tx, tt + 20), (tx, tb - 10), max(3, tw // 3), 3)

# Crown outlines (for visual ink) then concentric color fill
for tx, tt, tb, tw, ccx, ccy, crx, cry, cc in TREES:
    out += [C('ink'),
            S(irregular_oval(ccx, ccy, crx, cry, 100, 0.10) + irregular_oval(ccx, ccy, crx, cry, 100, 0.10)[:8], 0.06, 0.008)]
    out += [C(cc)] + fill_irreg_conc(ccx, ccy, crx - 3, cry - 3, 0.08, 14)
    out.append(dot(ccx, ccy, 12))

# Extra canopy blobs (concentric only — no bucket)
CROWN_EXTRA = [
    (150, 180, 42, 34, 'leaf2'), (250, 185, 40, 32, 'leaf3'),
    (510, 125, 48, 36, 'leaf1'), (610, 130, 45, 34, 'leaf3'), (560, 100, 38, 28, 'leaf4'),
    (1120, 165, 42, 32, 'leaf1'), (1200, 170, 44, 34, 'leaf2'),
]
for cx, cy, rx, ry, cc in CROWN_EXTRA:
    out += [C('ink'), S(irregular_oval(cx, cy, rx, ry, 50, 0.1) + irregular_oval(cx, cy, rx, ry, 50, 0.1)[:5], 0.05, 0.007)]
    out += [C(cc)] + fill_irreg_conc(cx, cy, rx - 2, ry - 2, 0.08, 10)
    out.append(dot(cx, cy, 8))

# ---- Wooden rake ----
RAKE_TOP = (1100, 390)
RAKE_BOT = (1230, 710)
out += [C('wood')] + rod_strokes(RAKE_TOP, RAKE_BOT, 6, 6)
out += [C('wood2')] + rod_strokes(RAKE_TOP, RAKE_BOT, 3, 3)
HX, HY = RAKE_BOT[0] - 8, RAKE_BOT[1] - 6
out += [C('ink'),
        S([(HX - 42, HY - 10), (HX + 38, HY + 16)], 0.05, 0.007),
        S([(HX - 42, HY - 2), (HX + 38, HY + 24)], 0.05, 0.007)]
out += [C('wood')]
for i in range(6):
    t = i / 5.0
    bx = HX - 38 + 76 * t
    by = HY - 6 + 20 * t
    out.append(S([(bx, by), (bx + 5, by + 26)], 0.0, 0.006))
out += [C('ink'),
        S([(RAKE_TOP[0] - 7, RAKE_TOP[1]), (RAKE_BOT[0] - 7, RAKE_BOT[1])], 0.0, 0.007),
        S([(RAKE_TOP[0] + 7, RAKE_TOP[1]), (RAKE_BOT[0] + 7, RAKE_BOT[1])], 0.0, 0.007)]

# ---- Sun + clouds ----
SUNX, SUNY, SUNR = 980, 78, 48
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
def cloud(cx, cy, sc):
    P = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        P.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(P + P[:3], 0.1, 0.008)
CLOUDS = [(400, 68, 0.8), (720, 95, 0.65), (1260, 70, 0.7)]
out += [cloud(*c) for c in CLOUDS]

# ---- Horizon with dress gaps ----
dress_mid_y = T((469, 480), PS, PX, PY)[1]
GHY = int(dress_mid_y)
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
print('GHY', GHY, 'gap', pl[0], pr[0])
out += [C('dkgreen')]
segs = [(2, pl[0]), (pr[0], 1358)]
print('horizon segs', segs)
for a, b in segs:
    if b - a > 8:
        out.append(S([(a, GHY), (b, GHY)], 0.15, 0.01))
out += [S([(2, GHY), (2, 787)], 0.1, 0.01),
        S([(1358, GHY), (1358, 787)], 0.1, 0.01),
        S([(2, 787), (1358, 787)], 0.1, 0.01)]
out += [{'op': 'pause', 's': 0.35}]

# ---- FILLS (bucket for large flats) ----
def in_pile(x, y):
    dx = (x - PCX) / PRX
    dy = (y - PCY) / PRY
    return dx * dx + dy * dy < 0.82

def near_trunk(x, y):
    for tx, tt, tb, tw, *_ in TREES:
        if abs(x - tx) < tw + 12 and tt - 8 < y < tb + 5:
            return True
    return False

def in_crown(x, y):
    for tx, tt, tb, tw, ccx, ccy, crx, cry, _cc in TREES:
        if ((x - ccx) / (crx + 6)) ** 2 + ((y - ccy) / (cry + 6)) ** 2 < 1.05:
            return True
    for cx, cy, rx, ry, _c in CROWN_EXTRA:
        if ((x - cx) / (rx + 6)) ** 2 + ((y - cy) / (ry + 6)) ** 2 < 1.05:
            return True
    return False

def near_rake(x, y, tol=16):
    ax, ay = RAKE_TOP; bx, by = RAKE_BOT
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
    px, py = ax + t * dx, ay + t * dy
    if (x - px) ** 2 + (y - py) ** 2 < tol * tol:
        return True
    if abs(y - HY) < 45 and HX - 55 < x < HX + 55:
        return True
    return False

# Leaf pile base fill (single color leaf1) — carefully seeded interior
PILE_SEEDS = []
for x in range(int(PCX - PRX) + 40, int(PCX + PRX) - 30, 36):
    for y in range(int(PCY - PRY) + 30, int(PCY + PRY) - 25, 28):
        if not in_pile(x, y):
            continue
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < body_bot + 8:
            continue
        PILE_SEEDS.append((x, y))
PILE_SEEDS += [(820, 630), (760, 620), (880, 620), (800, 670), (900, 670),
               (740, 650), (960, 640), (850, 680), (780, 680), (920, 600),
               (700, 630), (1000, 630), (820, 600), (820, 660)]
out += [C('leaf1'), F(*PILE_SEEDS)]

# Grass
G = []
for x in range(25, 1360, 42):
    for y in range(GHY + 14, 790, 32):
        if body_l - 8 < x < body_r + 8 and head_top - 4 < y < body_bot + 8:
            continue
        if in_pile(x, y):
            continue
        if near_trunk(x, y):
            continue
        if near_rake(x, y, 20):
            continue
        G.append((x, y))
G += [(40, 520), (80, 600), (120, 700), (200, 730), (300, 750),
      (420, 740), (520, 760), (600, 750), (1080, 740), (1280, 700),
      (1320, 620), (1300, 750), (50, 760), (250, 580),
      (body_l - 25, body_bot - 10), (body_r + 25, body_bot - 10),
      (body_l - 15, body_bot + 20), (body_r + 15, body_bot + 20),
      (body_l + 20, body_bot + 30), (100, 540), (380, 700)]
for ang in range(0, 360, 14):
    a = math.radians(ang)
    rr = 1.06 + 0.02 * math.sin(3 * a)
    px = PCX + (PRX + 32) * rr * math.cos(a)
    py = PCY + (PRY + 26) * rr * math.sin(a)
    if not (body_l - 8 < px < body_r + 8 and head_top - 4 < py < body_bot + 8):
        G.append((px, py))
out += [C('grass'), F(*G)]

out += [C('sun'), F((SUNX, SUNY), (SUNX - 14, SUNY), (SUNX + 14, SUNY),
                    (SUNX, SUNY - 14), (SUNX, SUNY + 14))]

SKY = []
for x in range(28, 1360, 48):
    for y in range(22, GHY - 10, 34):
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < GHY + 4:
            continue
        if any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS):
            continue
        if abs(x - SUNX) < SUNR + 22 and abs(y - SUNY) < SUNR + 22:
            continue
        if in_crown(x, y):
            continue
        if near_trunk(x, y):
            continue
        if near_rake(x, y, 16):
            continue
        SKY.append((x, y))
SKY += [(40, 180), (40, 280), (40, 360), (340, 40), (450, 200),
        (680, 40), (800, 200), (900, 40), (1050, 200), (1300, 250),
        (1300, 360), (200, 320), (body_r + 40, 160), (body_r + 50, 260),
        (body_l - 30, 200), (400, GHY - 30), (750, GHY - 25),
        (1000, GHY - 30), (70, GHY - 30), (480, 300), (860, 310)]
out += [C('sky'), F(*SKY)]
out += [{'op': 'pause', 's': 0.4}]

# ---- DETAILS: leaf accents ON TOP of pile (concentric multi-color) ----
LEAF_ACCENTS = [
    (700, 590, 48, 24, -0.4, 'leaf2'),
    (780, 570, 42, 22, 0.6, 'leaf3'),
    (860, 585, 46, 22, -0.2, 'leaf4'),
    (940, 600, 40, 20, 0.8, 'leaf2'),
    (740, 650, 44, 22, 0.3, 'leaf3'),
    (840, 660, 50, 24, -0.5, 'leaf2'),
    (920, 650, 38, 18, 0.2, 'leaf4'),
    (1000, 620, 36, 18, -0.7, 'leaf3'),
    (680, 650, 36, 18, 0.9, 'leaf4'),
    (800, 620, 32, 16, -1.0, 'leaf2'),
    (880, 620, 34, 16, 1.1, 'leaf3'),
    (960, 670, 34, 16, 0.4, 'leaf2'),
]
for cx, cy, rx, ry, rot, colname in LEAF_ACCENTS:
    out += [C(colname)]
    for f in (1.0, 0.75, 0.5, 0.25):
        out.append(S(leaf_shape(cx, cy, rx * f, ry * f, rot, 28), 0.0, 0.005))

# sun rays
out += [C('sun')]
for k in range(10):
    a = 2 * math.pi * k / 10
    out.append(S([(SUNX + (SUNR + 10) * math.cos(a), SUNY + (SUNR + 10) * math.sin(a)),
                  (SUNX + (SUNR + 30) * math.cos(a), SUNY + (SUNR + 30) * math.sin(a))], 0, 0.008))

# grass tufts
out += [C('dkgreen')]
for x, y in [(50, GHY + 50), (140, GHY + 70), (280, 730), (420, 750),
             (580, 760), (1080, GHY + 55), (1280, 710), (1320, 745),
             (90, 660), (200, 690), (480, 710), (50, 570)]:
    if body_l < x < body_r and y < body_bot + 10:
        continue
    if in_pile(x, y):
        continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))

# flowers
for (x, y, fc) in [(70, 530, 'flower'), (260, 710, 'flower2'), (460, 730, 'flower'),
                   (1260, 580, 'flower2'), (1320, 690, 'flower'), (110, 710, 'flower2')]:
    if body_l < x < body_r and head_top < y < body_bot:
        continue
    if in_pile(x, y):
        continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]

# airborne falling leaves
AIR_LEAVES = [
    (420, 260, 18, 10, 0.5, 'leaf1'),
    (640, 300, 16, 9, -0.8, 'leaf2'),
    (880, 270, 17, 10, 0.3, 'leaf3'),
    (1040, 310, 15, 8, 1.0, 'leaf1'),
    (500, 380, 14, 8, -0.4, 'leaf4'),
    (740, 340, 16, 9, 0.7, 'leaf2'),
    (320, 340, 13, 7, -1.1, 'leaf3'),
]
for cx, cy, rx, ry, rot, colname in AIR_LEAVES:
    out += [C(colname)]
    for f in (1.0, 0.6, 0.25):
        out.append(S(leaf_shape(cx, cy, rx * f, ry * f, rot, 28), 0.0, 0.005))
    out += [C('ink'), S(leaf_shape(cx, cy, rx, ry, rot, 32), 0.05, 0.006)]

# scattered ground leaves
for cx, cy, rx, ry, rot, colname in [
    (120, 650, 16, 9, 0.4, 'leaf1'), (350, 720, 14, 8, -0.6, 'leaf2'),
    (520, 755, 15, 8, 0.9, 'leaf3'), (1080, 730, 14, 7, -0.3, 'leaf1'),
    (1280, 660, 13, 7, 0.5, 'leaf4'), (60, 730, 12, 6, -0.9, 'leaf2'),
]:
    out += [C(colname)]
    for f in (1.0, 0.5):
        out.append(S(leaf_shape(cx, cy, rx * f, ry * f, rot, 24), 0.0, 0.005))

# birds
out += [C('ink')]
for x, y in [(480, 55), (820, 48)]:
    out.append(S(cr([(x - 16, y), (x - 8, y - 7), (x, y), (x + 8, y - 7), (x + 16, y)], 5), 0, 0.008))

# ---- seed-check preview ----
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p):
    return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'sun', 'leaf1'}
for o in out:
    if o['op'] == 'color':
        cc = col[o['c']]; o_c = o['c']
    if o['op'] == 'stroke':
        o['pts'] = [clamp(p) for p in o['pts']]
        d.line([tuple(p) for p in o['pts']], fill=cc, width=9, joint='curve')
        for q in (o['pts'][0], o['pts'][-1]):
            d.ellipse([q[0] - 4.5, q[1] - 4.5, q[0] + 4.5, q[1] + 4.5], fill=cc)
    if o['op'] == 'fill':
        keep = []
        for s in o['seeds']:
            x0, y0 = map(int, s); ok = None
            for r in range(0, 12):
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        x, y = x0 + dx, y0 + dy
                        if not (0 <= x < 1360 and 0 <= y < 790) or ok is not None:
                            continue
                        pix = im.getpixel((x, y))
                        colors = im.crop((x - 3, y - 3, x + 4, y + 4)).getcolors(500) or []
                        if len(colors) == 1 and pix == (255, 255, 255):
                            ok = (x, y)
                if ok:
                    break
            if ok:
                before = im.getpixel(CORNER)
                if o_c in PROTECTED:
                    probe = im.copy()
                    ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc)
                    limit = 60000 if o_c in ('skin', 'dress', 'cheek', 'shoe', 'sun') else 200000
                    if o_c == 'leaf1':
                        limit = 220000
                    if probe.getpixel(CORNER) != before or filled > limit:
                        print('reject leak seed', o_c, ok, 'filled', filled)
                        continue
                ImageDraw.floodfill(im, ok, cc)
                keep.append(list(ok))
            else:
                print('drop seed', o_c, s)
        if not keep:
            im.save('./preview_fail.png')
            raise SystemExit('no seeds kept: ' + str(o_c))
        o['seeds'] = keep
im.save('./preview.png')
white = sum(1 for p in im.getdata() if p == (255, 255, 255))
print('white px left', white)
print('top', Counter(im.getdata()).most_common(14))
skin = sum(1 for p in im.getdata() if p == (247, 172, 196))
assert skin < 90000, skin
assert white < 100000, white
assert im.getpixel((10, 200)) == (140, 200, 245), im.getpixel((10, 200))
pc = im.getpixel((820, 630))
print('pile center', pc)
assert pc == (230, 120, 40), pc  # leaf1
# grass sample
g = im.getpixel((50, 720))
print('grass sample', g)
assert g == (110, 185, 70), g
# center tree should be leaf2 gold, not white
ct = im.getpixel((560, 155))
print('center crown', ct)
assert ct != (255, 255, 255), ct

D = {'name': 'peppa-leaves', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa jumping in autumn leaf pile outdoors: orange leaf mound with multi-color leaf accents, 3 autumn trees, wooden rake, sun, clouds, grass, airborne leaves. Horizon gaps at dress. Bucket fills for pile/grass/sky/sun.'}
json.dump(D, open('./peppa_leaves_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa17\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa17.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
print(len(out), 'ops', len(pal), 'colors')
