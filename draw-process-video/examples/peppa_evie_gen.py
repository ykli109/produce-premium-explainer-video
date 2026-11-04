#!/usr/bin/env python3
"""Peppa with baby sister Evie in a nursery (drawing-peppa-pig-16).
Fills use paint-bucket seeds; large flats are never brush-painted.
Evie = smaller piglet in purple onesie (Season 12 baby look)."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(16)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['evie', [168, 110, 205]],  # purple onesie
 ['wall', [255, 242, 225]], ['floor', [214, 170, 120]], ['dkwood', [140, 95, 55]],
 ['sky', [140, 200, 245]], ['sun', [255, 215, 60]],
 ['blanket', [255, 190, 210]], ['blanket2', [255, 230, 240]],
 ['curtain', [150, 175, 230]], ['wood', [180, 125, 75]],
 ['teddy', [210, 145, 80]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['bottle', [230, 245, 255]],
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
            # shoes: concentric ellipses at small scale (no bucket on tiny shoes)
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
def box_pts(xs):
    xs2, ys2 = [], []
    for o in ops[:44]:
        if o['op'] == 'stroke':
            for p in o['pts']:
                q = T(p, *xs); xs2.append(q[0]); ys2.append(q[1])
    return min(xs2), max(xs2), min(ys2), max(ys2)

# ---- Peppa (left) ----
PS, PX, PY = 0.55, 90, 95
out += char(PS, PX, PY, 'dress')
out += [{'op': 'pause', 's': 0.35}]
pl, pr, pt, pb = box_pts((PS, PX, PY))
print('peppa box', (pl - 10, pt - 10, pr + 10, pb + 10))

# ---- Baby Evie (smaller, purple onesie, right of Peppa) ----
ES, EX, EY = 0.38, 400, 220  # baby sister, still clearly smaller
out += char(ES, EX, EY, 'evie')
out += [{'op': 'pause', 's': 0.4}]
el, er, et, eb = box_pts((ES, EX, EY))
print('evie box', (el - 8, et - 8, er + 8, eb + 8))

# Baby bottle next to Evie (simple closed shape for bucket)
BOT = (er + 70, eb - 20)

# pacifier (baby cue) near Evie snout tip
PACX, PACY = er + 8, et + (eb - et) * 0.22
out += [C('ink'), S(ell(PACX, PACY, 12, 10, 32, 3), 0.05, 0.007)]
out += [C('flower2')]
for f in (1.0, 0.6, 0.25):
    out.append(S(ell(PACX, PACY, 10 * f, 8 * f, 28, 2), 0.0, 0.005))

out += [C('ink'),
        S(ell(BOT[0], BOT[1], 16, 28, 56, 6), 0.05, 0.008),
        S(ell(BOT[0], BOT[1], 12, 24, 48, 4), 0.0, 0.006),  # inner seal
        S(poly([(BOT[0] - 9, BOT[1] - 28), (BOT[0] - 7, BOT[1] - 44),
                (BOT[0] + 7, BOT[1] - 44), (BOT[0] + 9, BOT[1] - 28)]), 0.05, 0.008),
        S(ell(BOT[0], BOT[1] - 48, 8, 6, 28, 3), 0.05, 0.008)]
# solid bottle body with concentric strokes (tiny, reliable)
out += [C('bottle')]
for f in (1.0, 0.8, 0.6, 0.4, 0.2, 0.05):
    out.append(S(ell(BOT[0], BOT[1], 14 * f, 26 * f, 40, 2), 0.0, 0.005))
out.append(dot(BOT[0], BOT[1], 6))
out += [C('flower')]  # pink nipple tip
for f in (1.0, 0.5):
    out.append(S(ell(BOT[0], BOT[1] - 48, 7 * f, 5 * f, 20, 1), 0.0, 0.005))

# Teddy bear (left of Peppa feet / on blanket)
TX, TY = 160, 620
out += [C('ink'),
        S(ell(TX, TY, 38, 34, 48, 4), 0.05, 0.008),           # body
        S(ell(TX, TY - 42, 26, 24, 40, 4), 0.05, 0.008),       # head
        S(ell(TX - 22, TY - 58, 10, 10, 24, 2), 0.05, 0.008),  # ear L
        S(ell(TX + 22, TY - 58, 10, 10, 24, 2), 0.05, 0.008),  # ear R
        S(ell(TX - 28, TY + 10, 12, 10, 24, 2), 0.05, 0.008),  # arm L
        S(ell(TX + 28, TY + 10, 12, 10, 24, 2), 0.05, 0.008),  # arm R
        ]

# Rattle
RX, RY = 760, 700
out += [C('ink'),
        S(ell(RX, RY, 22, 22, 40, 4), 0.05, 0.008),
        S([(RX, RY + 22), (RX + 4, RY + 70)], 0.1, 0.008),
        S(ell(RX + 4, RY + 78, 8, 6, 20, 2), 0.05, 0.008)]

# ---- Crib (right side) ----
# Outer rectangle + rails + mattress
CRIB = dict(x0=980, y0=280, x1=1320, y1=620)
cx0, cy0, cx1, cy1 = CRIB['x0'], CRIB['y0'], CRIB['x1'], CRIB['y1']
out += [C('ink')]
# outer frame (closed)
out += [S(poly([(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)]), 0.1, 0.008)]
# headboard / footboard top bar
out += [S([(cx0, cy0 + 40), (cx1, cy0 + 40)], 0.1, 0.008)]
# vertical rails
for x in range(cx0 + 30, cx1 - 10, 36):
    out.append(S([(x, cy0), (x, cy0 + 40)], 0.05, 0.008))
# mattress top line (pocket for blanket fill inside crib)
MY = cy1 - 90
out += [S([(cx0 + 8, MY), (cx1 - 8, MY)], 0.1, 0.008)]
# legs
for x in (cx0 + 10, cx1 - 10):
    out.append(S([(x, cy1), (x, cy1 + 40)], 0.1, 0.008))

# ---- Window (upper left of wall area, above characters somewhat right-center) ----
WX0, WY0, WX1, WY1 = 860, 40, 1180, 220
out += [C('ink'),
        S(poly([(WX0, WY0), (WX1, WY0), (WX1, WY1), (WX0, WY1)]), 0.1, 0.008),
        S([(WX0, (WY0 + WY1) / 2), (WX1, (WY0 + WY1) / 2)], 0.1, 0.008),
        S([((WX0 + WX1) / 2, WY0), ((WX0 + WX1) / 2, WY1)], 0.1, 0.008)]
# curtains (left and right panels as closed shapes)
out += [S(poly([(WX0 - 50, WY0 - 5), (WX0 + 5, WY0 - 5), (WX0 + 5, WY1 + 15), (WX0 - 50, WY1 + 15)]), 0.1, 0.008),
        S(poly([(WX1 - 5, WY0 - 5), (WX1 + 50, WY0 - 5), (WX1 + 50, WY1 + 15), (WX1 - 5, WY1 + 15)]), 0.1, 0.008)]
# sun in window
SUNX, SUNY, SUNR = 1020, 95, 28
out += [S(ell(SUNX, SUNY, SUNR, SUNR, 48, 4), 0.05, 0.008)]

# ---- Soft blanket on floor (irregular rounded rect under both pigs) ----
# Closed wavy oval under Peppa+Evie
BLCX, BLCY, BLRX, BLRY = 420, 680, 360, 90
BL = []
for k in range(90):
    a = 2 * math.pi * k / 90
    b = 1 + 0.08 * math.sin(3 * a)
    BL.append((BLCX + BLRX * b * math.cos(a), BLCY + BLRY * b * math.sin(a)))
BL = BL + BL[:5]
out += [C('ink'), S(BL, 0.05, 0.008)]

# Floor / wall horizon — stop at Peppa dress, Evie, crib legs
# Wall/floor line around y of mid-dress for Peppa
GHY = int(T((469, 480), PS, PX, PY)[1])
print('GHY', GHY)
# gaps at Peppa and Evie and crib
p_gap_l = side(PS, PX, PY, GHY, False)[0]
p_gap_r = side(PS, PX, PY, GHY, True)[0]
e_gap_l = side(ES, EX, EY, GHY, False)[0]
e_gap_r = side(ES, EX, EY, GHY, True)[0]
print('gaps peppa', p_gap_l, p_gap_r, 'evie', e_gap_l, e_gap_r)

out += [C('dkwood')]
# wall/floor line in segments avoiding characters and stopping before crib left
segs = [(2, p_gap_l), (p_gap_r, e_gap_l), (e_gap_r, cx0 - 4), (cx1 + 4, 1358)]
# also need floor edge under crib? crib stands on floor — horizon through crib would cut mattress.
# Stop horizon at crib outer edges (already in segs).
for a, b in segs:
    if b - a > 10:
        out.append(S([(a, GHY), (b, GHY)], 0.15, 0.01))
# floor border
out += [S([(2, GHY), (2, 787)], 0.1, 0.01),
        S([(1358, GHY), (1358, 787)], 0.1, 0.01),
        S([(2, 787), (1358, 787)], 0.1, 0.01),
        S([(2, 2), (1358, 2)], 0.05, 0.01),
        S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [{'op': 'pause', 's': 0.3}]

# ---- FILLS ----
# Character fills already in char(). Order for scene:
# bottle, teddy, rattle, crib wood parts, mattress, blanket, curtains, sun, sky-in-window, floor, wall

# bottle painted solid above

# teddy solid paint (dense concentric) — small shape, no bucket
out += [C('teddy')]
for f in [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1]:
    out.append(S(ell(TX, TY, 34 * f, 30 * f, 40, 2), 0.0, 0.005))
    out.append(S(ell(TX, TY - 42, 22 * f, 20 * f, 36, 2), 0.0, 0.005))
for f in [1.0, 0.6, 0.25]:
    out.append(S(ell(TX - 22, TY - 58, 9 * f, 9 * f, 20, 1), 0.0, 0.005))
    out.append(S(ell(TX + 22, TY - 58, 9 * f, 9 * f, 20, 1), 0.0, 0.005))
    out.append(S(ell(TX - 28, TY + 10, 11 * f, 9 * f, 20, 1), 0.0, 0.005))
    out.append(S(ell(TX + 28, TY + 10, 11 * f, 9 * f, 20, 1), 0.0, 0.005))
out.append(dot(TX, TY, 8))
out.append(dot(TX, TY - 42, 6))

out += [C('flower2'), F((RX, RY), (RX - 6, RY), (RX + 6, RY), (RX, RY - 6))]  # rattle head yellow

# crib wood (frame region above mattress + rails pocket)
CRIB_WOOD = []
for x in range(cx0 + 16, cx1 - 12, 28):
    for y in range(cy0 + 8, MY - 6, 22):
        # skip if in a rail gap? rails are thin; fill whole upper crib as wood
        CRIB_WOOD.append((x, y))
CRIB_WOOD += [(cx0 + 40, cy0 + 20), (cx1 - 40, cy0 + 20), ((cx0 + cx1) / 2, cy0 + 18)]
# lower apron below mattress inside crib outer? mattress pocket separate
out += [C('wood'), F(*CRIB_WOOD)]

# mattress (cream/blanket2) between MY and cy1 inside crib
MAT = []
for x in range(cx0 + 20, cx1 - 16, 30):
    for y in range(MY + 12, cy1 - 12, 24):
        MAT.append((x, y))
MAT += [((cx0 + cx1) / 2, (MY + cy1) / 2), (cx0 + 50, MY + 30), (cx1 - 50, MY + 30)]
out += [C('blanket2'), F(*MAT)]

# soft blanket under pigs
def in_blanket(x, y):
    dx = (x - BLCX) / BLRX
    dy = (y - BLCY) / BLRY
    return dx * dx + dy * dy < 0.85

BLANKET = []
for x in range(int(BLCX - BLRX) + 20, int(BLCX + BLRX) - 15, 32):
    for y in range(int(BLCY - BLRY) + 15, int(BLCY + BLRY) - 12, 26):
        if not in_blanket(x, y):
            continue
        if pl - 6 < x < pr + 6 and pt - 4 < y < pb + 6:
            continue
        if el - 6 < x < er + 6 and et - 4 < y < eb + 6:
            continue
        if abs(x - TX) < 45 and abs(y - TY) < 50:
            continue
        if abs(x - RX) < 30 and abs(y - RY) < 40:
            continue
        if abs(x - BOT[0]) < 22 and abs(y - BOT[1]) < 40:
            continue
        BLANKET.append((x, y))
BLANKET += [(BLCX, BLCY), (BLCX - 120, BLCY), (BLCX + 120, BLCY),
            (BLCX, BLCY + 40), (BLCX - 80, BLCY + 30), (BLCX + 100, BLCY - 20),
            (BLCX - 150, BLCY + 20), (BLCX + 160, BLCY + 15)]
out += [C('blanket'), F(*BLANKET)]

# curtains
out += [C('curtain'),
        F((WX0 - 25, (WY0 + WY1) / 2), (WX0 - 30, WY0 + 40), (WX0 - 20, WY1 - 20)),
        F((WX1 + 25, (WY0 + WY1) / 2), (WX1 + 30, WY0 + 40), (WX1 + 20, WY1 - 20))]

out += [C('sun'), F((SUNX, SUNY), (SUNX - 8, SUNY), (SUNX + 8, SUNY), (SUNX, SUNY - 8))]

# sky inside window panes (4 panes)
SKY_W = []
for x in range(WX0 + 12, WX1 - 10, 28):
    for y in range(WY0 + 10, WY1 - 8, 22):
        if abs(x - SUNX) < SUNR + 10 and abs(y - SUNY) < SUNR + 10:
            continue
        # skip curtain overlap
        if x < WX0 + 2 or x > WX1 - 2:
            continue
        SKY_W.append((x, y))
SKY_W += [(WX0 + 40, WY0 + 30), (WX1 - 40, WY0 + 30),
          (WX0 + 40, WY1 - 30), (WX1 - 40, WY1 - 30),
          ((WX0 + WX1) / 2 - 40, (WY0 + WY1) / 2 - 25),
          ((WX0 + WX1) / 2 + 40, (WY0 + WY1) / 2 + 25)]
out += [C('sky'), F(*SKY_W)]

# FLOOR (below GHY), skip blanket, crib, characters, toys
FLOOR = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if pl - 8 < x < pr + 8 and pt - 4 < y < pb + 8:
            continue
        if el - 8 < x < er + 8 and et - 4 < y < eb + 8:
            continue
        if in_blanket(x, y):
            continue
        if cx0 - 4 < x < cx1 + 4 and cy0 - 4 < y < cy1 + 50:
            continue
        if abs(x - TX) < 48 and abs(y - TY) < 55:
            continue
        if abs(x - RX) < 32 and abs(y - RY) < 85:
            continue
        if abs(x - BOT[0]) < 24 and abs(y - BOT[1]) < 55:
            continue
        FLOOR.append((x, y))
FLOOR += [(40, 700), (80, 750), (200, 760), (800, 750), (900, 700),
          (950, 760), (1340, 700), (1340, 760), (600, 760),
          (cx0 - 30, 700), (cx1 + 30, 700), (cx1 + 40, cy1 + 30),
          (cx0 + 20, cy1 + 30), (cx1 - 20, cy1 + 30)]
out += [C('floor'), F(*FLOOR)]

# WALL (above GHY), skip window, curtains, characters, crib upper
WALL = []
for x in range(25, 1360, 44):
    for y in range(18, GHY - 10, 32):
        if pl - 6 < x < pr + 6 and pt - 4 < y < GHY + 4:
            continue
        if el - 6 < x < er + 6 and et - 4 < y < GHY + 4:
            continue
        if WX0 - 55 < x < WX1 + 55 and WY0 - 10 < y < WY1 + 20:
            continue
        if cx0 - 6 < x < cx1 + 6 and cy0 - 6 < y < GHY + 4:
            continue
        WALL.append((x, y))
WALL += [(40, 80), (40, 200), (200, 50), (400, 80), (600, 50),
         (700, 120), (800, 50), (1300, 80), (1300, 200),
         (500, GHY - 30), (200, GHY - 25), (750, GHY - 30),
         (pr + 30, 150), (el - 30, 200), (er + 30, 180)]
out += [C('wall'), F(*WALL)]
out += [{'op': 'pause', 's': 0.35}]

# ---- DETAILS ----
# sun rays inside window
out += [C('sun')]
for k in range(8):
    a = 2 * math.pi * k / 8
    out.append(S([(SUNX + (SUNR + 4) * math.cos(a), SUNY + (SUNR + 4) * math.sin(a)),
                  (SUNX + (SUNR + 16) * math.cos(a), SUNY + (SUNR + 16) * math.sin(a))], 0, 0.008))

# teddy face
out += [C('ink'),
        dot(TX - 8, TY - 44, 3),
        dot(TX + 8, TY - 44, 3),
        S(cr([(TX - 8, TY - 32), (TX, TY - 26), (TX + 8, TY - 32)], 5), 0.1, 0.007)]

# rattle dots
out += [C('flower')]
for k in range(5):
    a = 2 * math.pi * k / 5
    out.append(dot(RX + 12 * math.cos(a), RY + 12 * math.sin(a), 3))

# blanket stitch lines
out += [C('blanket2')]
for yy in (BLCY - 25, BLCY + 5, BLCY + 35):
    pts = []
    for x in range(int(BLCX - BLRX) + 40, int(BLCX + BLRX) - 30, 20):
        if not in_blanket(x, yy):
            if len(pts) > 2:
                out.append(S(pts, 0.1, 0.008)); pts = []
            continue
        if pl - 4 < x < pr + 4 and pt < yy < pb + 4:
            if len(pts) > 2:
                out.append(S(pts, 0.1, 0.008)); pts = []
            continue
        if el - 4 < x < er + 4 and et < yy < eb + 4:
            if len(pts) > 2:
                out.append(S(pts, 0.1, 0.008)); pts = []
            continue
        pts.append((x, yy + 2 * math.sin(x / 25)))
    if len(pts) > 2:
        out.append(S(pts, 0.1, 0.008))

# flowers on floor corners
for (x, y, fc) in [(60, 720, 'flower'), (100, 760, 'flower2'), (820, 740, 'flower'),
                   (880, 700, 'flower2'), (1340, 650, 'flower'), (50, 560, 'flower2')]:
    if in_blanket(x, y):
        continue
    if cx0 < x < cx1 and cy0 < y < cy1 + 40:
        continue
    out += [C(fc)] + [dot(x + 7 * math.cos(2 * math.pi * k / 5), y + 7 * math.sin(2 * math.pi * k / 5), 4)
                      for k in range(5)] + [C('sun'), dot(x, y, 3)]

# mobile stars above crib
out += [C('flower2')]
for x, y in [(1050, 250), (1120, 235), (1200, 250), (1080, 220), (1160, 215)]:
    out.append(dot(x, y, 5))
out += [C('ink')]
out.append(S([(1100, 200), (1050, 248), (1120, 233), (1200, 248), (1160, 213)], 0.15, 0.008))

# ---- seed-check preview ----
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p):
    return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
CHAR_FILL = ('skin', 'dress', 'cheek', 'shoe', 'evie')
SMALL_FILL = ('sun', 'bottle', 'teddy', 'flower2', 'curtain')
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
                if o_c in CHAR_FILL + SMALL_FILL + ('wood', 'blanket', 'blanket2', 'floor', 'wall', 'sky'):
                    probe = im.copy()
                    ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc)
                    limit = 60000 if o_c in CHAR_FILL else 150000
                    if o_c in ('floor', 'wall'):
                        limit = 450000
                    if o_c in ('blanket', 'wood', 'blanket2'):
                        limit = 150000
                    if o_c in SMALL_FILL:
                        limit = 40000
                    # Corner must stay white only for fills that should NOT reach the canvas edge
                    edge_ok = o_c in ('floor', 'wall', 'sky', 'grass')
                    if (not edge_ok and probe.getpixel(CORNER) != before) or filled > limit:
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
assert skin < 100000, skin
assert white < 150000, white
# sample checks
assert im.getpixel((40, 100)) == (255, 242, 225), ('wall', im.getpixel((40, 100)))
assert im.getpixel((40, 720)) == (214, 170, 120), ('floor', im.getpixel((40, 720)))

D = {'name': 'peppa-evie-nursery', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa with baby sister Evie (purple onesie) in a nursery: soft blanket, teddy, rattle, baby bottle, wooden crib with mattress, window with sun and curtains. Horizon gaps at dress/Evie/crib. Bucket fills.'}
json.dump(D, open('./strokes.json', 'w'))
json.dump(D, open('./peppa_evie_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa16\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa16.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
print(len(out), 'ops', len(pal), 'colors')
