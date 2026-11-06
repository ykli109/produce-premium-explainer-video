#!/usr/bin/env python3
"""Peppa camping outdoors at dusk (drawing-peppa-pig-18).
Tent + campfire + moon/stars. Large flats (sky/grass/moon) use paint-bucket;
enclosed props use concentric strokes to avoid corner leaks."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(18)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [55, 70, 140]], ['grass', [90, 160, 55]], ['dkgreen', [45, 100, 35]],
 ['moon', [255, 240, 180]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['wood', [160, 100, 55]], ['wood2', [110, 65, 35]],
 ['tent', [240, 210, 150]], ['tent2', [210, 150, 80]],
 ['flame1', [255, 120, 30]], ['flame2', [255, 210, 60]],
 ['pack', [70, 130, 200]], ['star', [255, 245, 160]],
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
def flame_blob(cx, cy, rx, ry, tip_pull=-1.0, n=40):
    P = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rmod = 1.0 + 0.35 * math.sin(a)
        if a > math.pi:
            rmod *= 0.85
        x = cx + rx * rmod * math.cos(a)
        y = cy + ry * rmod * math.sin(a)
        if math.sin(a) < -0.3:
            y += tip_pull * ry * 0.45 * (-math.sin(a) - 0.3)
        P.append((x, y))
    return P + P[:3]

# ---- Peppa ----
PS, PX, PY = 0.60, 145, 100
out += char(PS, PX, PY, 'dress')
out += [{'op': 'pause', 's': 0.35}]

xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r = min(xs), max(xs)
head_top, body_bot = min(ys), max(ys)
dress_mid_y = T((469, 480), PS, PX, PY)[1]
GHY = int(dress_mid_y)
print('peppa', round(body_l), round(head_top), round(body_r), round(body_bot), 'GHY', GHY)

# ---- Tent ----
TXL, TXR, TYB = 780, 1220, 560
TPX, TPY = 1000, 180

def tent_x_at_y(y, left=True):
    t = (y - TPY) / (TYB - TPY)
    return TPX + t * ((TXL if left else TXR) - TPX)

def tri_at(f):
    cx = (TPX + TXL + TXR) / 3.0
    cy = (TPY + 2 * TYB) / 3.0
    def L(p):
        return (cx + (p[0] - cx) * f, cy + (p[1] - cy) * f)
    return [L((TPX, TPY)), L((TXL, TYB)), L((TXR, TYB))]

out += [C('ink')]
# Thick parallel edges so horizon crossing is watertight
def thick_edge(a, b, w=7, n=6):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    for i in range(n):
        o = -w + 2 * w * i / max(1, n - 1)
        out.append(S([(ax + nx * o, ay + ny * o), (bx + nx * o, by + ny * o)], 0.0, 0.006))
    out.append(dot(ax, ay, 7)); out.append(dot(bx, by, 7))
thick_edge((TPX, TPY), (TXL, TYB), 8, 7)
thick_edge((TXL, TYB), (TXR, TYB), 8, 7)
thick_edge((TXR, TYB), (TPX, TPY), 8, 7)
# Extra seal at horizon crossings on both side walls
for side_left in (True, False):
    xh = tent_x_at_y(GHY, side_left)
    # local tangent along side
    x0 = tent_x_at_y(GHY - 35, side_left)
    x1 = tent_x_at_y(GHY + 35, side_left)
    thick_edge((x0, GHY - 35), (x1, GHY + 35), 9, 8)

out += [C('tent')]
for f in [i / 40 for i in range(40, 0, -1)]:
    out.append(S(poly(tri_at(f)), 0.0, 0.004))

# right-panel shade
out += [C('tent2')]
for t in [0.18, 0.30, 0.42, 0.54, 0.66, 0.78, 0.90]:
    xs = TPX + 10 + t * (TXR - TPX - 40)
    y_top = TPY + 30 + t * 50
    out.append(S([(xs, y_top), (xs + 25 * (1 - t), TYB - 14)], 0.0, 0.006))

# Door concentric
DOOR_TOP = (TPX, TYB - 140); DOOR_BL = (TPX - 55, TYB - 8); DOOR_BR = (TPX + 55, TYB - 8)
out += [C('ink'), S(poly([DOOR_TOP, DOOR_BL, DOOR_BR]), 0.05, 0.007)]
out += [dot(*DOOR_TOP, 4), dot(*DOOR_BL, 4), dot(*DOOR_BR, 4)]
Dcx = (DOOR_TOP[0] + DOOR_BL[0] + DOOR_BR[0]) / 3
Dcy = (DOOR_TOP[1] + DOOR_BL[1] + DOOR_BR[1]) / 3
out += [C('wood2')]
for f in [0.95, 0.8, 0.65, 0.5, 0.35, 0.2, 0.08]:
    def dl(p, f=f):
        return (Dcx + (p[0] - Dcx) * f, Dcy + (p[1] - Dcy) * f)
    out.append(S(poly([dl(DOOR_TOP), dl(DOOR_BL), dl(DOOR_BR)]), 0.0, 0.005))

out += [C('ink'), S([(TPX, TPY + 12), (TPX, TYB - 12)], 0.1, 0.008)]
out += [C('wood')]
out += rod_strokes((TXL + 8, TYB - 5), (TPX - 4, TPY + 10), w=5, n=4)
out += rod_strokes((TXR - 8, TYB - 5), (TPX + 4, TPY + 10), w=5, n=4)
out += [C('ink'),
        S([(TXL + 5, TYB - 15), (TXL - 80, TYB + 50)], 0.2, 0.008),
        S([(TXR - 5, TYB - 15), (TXR + 80, TYB + 50)], 0.2, 0.008)]
out += [C('wood2'),
        S([(TXL - 85, TYB + 45), (TXL - 75, TYB + 60)], 0, 0.006),
        S([(TXR + 75, TYB + 45), (TXR + 85, TYB + 60)], 0, 0.006)]

# ---- Campfire ----
FCX, FCY = 540, 640
out += [C('wood')]
LOGS = [
    (FCX - 55, FCY + 18, FCX + 55, FCY + 8, 10),
    (FCX - 50, FCY + 35, FCX + 45, FCY + 42, 9),
    (FCX - 30, FCY + 8, FCX + 20, FCY + 50, 8),
]
for ax, ay, bx, by, w in LOGS:
    out += rod_strokes((ax, ay), (bx, by), w=w, n=5)
for cx, cy, r in [(FCX - 58, FCY + 18, 12), (FCX + 58, FCY + 8, 11),
                  (FCX - 52, FCY + 36, 10), (FCX + 48, FCY + 42, 10)]:
    for f in (1.0, 0.6, 0.25):
        out.append(S(ell(cx, cy, r * f, r * f * 0.7, 28, 2), 0.0, 0.006))

FLAMES = [
    (FCX, FCY - 55, 38, 70, -1.2),
    (FCX - 28, FCY - 30, 22, 45, -0.9),
    (FCX + 30, FCY - 35, 24, 50, -1.0),
]
out += [C('ink')]
for cx, cy, rx, ry, tip in FLAMES:
    out.append(S(flame_blob(cx, cy, rx, ry, tip), 0.04, 0.007))
out += [C('flame1')]
for cx, cy, rx, ry, tip in FLAMES:
    for f in (0.92, 0.75, 0.58, 0.42, 0.28, 0.14):
        out.append(S(flame_blob(cx, cy, rx * f, ry * f, tip, 32), 0.0, 0.005))

# ---- Backpack ----
BPX, BPY = 690, max(GHY + 45, 475)
out += [C('ink'), S(ell(BPX, BPY, 42, 50, 48, 3), 0.05, 0.007)]
out += [S(ell(BPX, BPY, 36, 44, 40, 2), 0.0, 0.006)]
out += [S(cr([(BPX - 38, BPY - 20), (BPX, BPY - 55), (BPX + 38, BPY - 20)], 8), 0.1, 0.008)]
out += [C('wood2'),
        S([(BPX - 20, BPY - 10), (BPX - 25, BPY + 40)], 0.1, 0.007),
        S([(BPX + 20, BPY - 10), (BPX + 25, BPY + 40)], 0.1, 0.007)]
out += [C('pack')]
for f in (0.92, 0.75, 0.58, 0.40, 0.22, 0.08):
    out.append(S(ell(BPX, BPY, 42 * f, 50 * f, 36, 2), 0.0, 0.005))

# ---- Moon (concentric + bucket seed backup later) ----
MOONX, MOONY, MOONR = 1180, 120, 55
out += [C('ink'), S(ell(MOONX, MOONY, MOONR, MOONR, 64, 3), 0.04, 0.007)]
out += [C('moon')]
for f in (0.92, 0.78, 0.64, 0.50, 0.36, 0.22, 0.10):
    out.append(S(ell(MOONX, MOONY, MOONR * f, MOONR * f, 48, 2), 0.0, 0.005))
out.append(dot(MOONX, MOONY, 12))
out.append(dot(MOONX, MOONY, 8))
# crater rings (after fill)
out += [C('ink'),
        S(ell(MOONX - 15, MOONY - 8, 8, 7, 20, 1), 0.0, 0.006),
        S(ell(MOONX + 12, MOONY + 15, 6, 5, 16, 1), 0.0, 0.006),
        S(ell(MOONX + 5, MOONY - 20, 5, 4, 14, 1), 0.0, 0.006)]

# ---- Clouds ----
CLOUDS = [(220, 100, 1.0), (480, 70, 0.75), (720, 90, 0.85)]
out += [C('ink')]
for a, b, k in CLOUDS:
    out.append(S(ell(a, b, 90 * k, 38 * k, 48, 2), 0.2, 0.01))
    out.append(S(ell(a - 45 * k, b + 8, 55 * k, 28 * k, 36, 2), 0.2, 0.01))
    out.append(S(ell(a + 48 * k, b + 6, 50 * k, 26 * k, 36, 2), 0.2, 0.01))

STARS = [(80, 60), (160, 140), (350, 45), (550, 130), (650, 40),
         (850, 80), (1050, 50), (1280, 180), (100, 220), (400, 180),
         (900, 160), (1100, 200), (60, 300), (500, 250), (1300, 90)]

# ---- Horizon ----
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
tl_h = tent_x_at_y(GHY, True)
tr_h = tent_x_at_y(GHY, False)
print('horizon dress', round(pl[0],1), round(pr[0],1), 'tent', round(tl_h,1), round(tr_h,1))

out += [C('dkgreen')]
# Dress gap only; tent walls are the seal on the right (no horizon gap at tent)
segs = [(2, pl[0]), (pr[0], 1358)]
print('segs', [(round(a,1), round(b,1)) for a,b in segs], 'tent_cross', round(tl_h,1), round(tr_h,1))
for a, b in segs:
    if b - a > 8:
        # straight thick horizon (avoid sine gaps); stop short of tent walls then resume
        # split around tent so we don't cut a green scar through fabric: meet walls
        pieces = []
        if a < tl_h - 6 and b > tr_h + 6:
            pieces = [(a, tl_h - 6), (tr_h + 6, b)]
        else:
            pieces = [(a, b)]
        for aa, bb in pieces:
            if bb - aa > 8:
                out.append(S([(aa, GHY), (bb, GHY)], 0.05, 0.009))
# reinforce meeting tent walls
out += [S([(tl_h - 14, GHY), (tl_h + 2, GHY)], 0.0, 0.007),
        S([(tr_h - 2, GHY), (tr_h + 14, GHY)], 0.0, 0.007)]
out += [S([(2, GHY), (2, 787)], 0.1, 0.01),
        S([(1358, GHY), (1358, 787)], 0.1, 0.01),
        S([(2, 787), (1358, 787)], 0.1, 0.01),
        S([(2, 2), (1358, 2)], 0.05, 0.01),
        S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [{'op': 'pause', 's': 0.3}]

def in_tent(x, y):
    if y < TPY + 5 or y > TYB - 2: return False
    return tent_x_at_y(y, True) + 8 < x < tent_x_at_y(y, False) - 8

def in_flame(x, y):
    for cx, cy, rx, ry, tip in FLAMES:
        if ((x - cx) / (rx + 4)) ** 2 + ((y - cy) / (ry + 8)) ** 2 < 0.85:
            return True
    return False

def near_logs(x, y, tol=22):
    for ax, ay, bx, by, w in LOGS:
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
        px, py = ax + t * dx, ay + t * dy
        if (x - px) ** 2 + (y - py) ** 2 < (tol + w) ** 2:
            return True
    return False

def in_backpack(x, y):
    return ((x - BPX) / 48) ** 2 + ((y - BPY) / 56) ** 2 < 1.0

def in_moon(x, y):
    return (x - MOONX) ** 2 + (y - MOONY) ** 2 < (MOONR + 4) ** 2

# ---- Bucket fills: sky then grass ----
SKY = []
for x in range(28, 1360, 48):
    for y in range(22, GHY - 12, 34):
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < GHY + 4:
            continue
        if any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS):
            continue
        if in_moon(x, y) or in_tent(x, y) or in_backpack(x, y):
            continue
        SKY.append((x, y))
SKY += [(40, 180), (40, 280), (40, 360), (340, 40), (450, 200),
        (600, 40), (800, 40), (950, 40), (1050, 250), (1300, 280),
        (1300, 360), (200, 320), (body_r + 40, 160), (body_r + 50, 260),
        (body_l - 30, 200), (400, GHY - 30), (650, GHY - 25),
        (70, GHY - 30), (480, 300), (200, GHY - 40),
        (500, 350), (300, 250), (750, 200)]
for y in range(TPY + 20, GHY - 10, 28):
    SKY.append((tl_h - 35, y))
    SKY.append((tr_h + 35, y))
out += [C('sky'), F(*SKY)]

G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if body_l - 8 < x < body_r + 8 and head_top - 4 < y < body_bot + 8:
            continue
        if in_tent(x, y) or in_flame(x, y) or near_logs(x, y, 18) or in_backpack(x, y):
            continue
        G.append((x, y))
G += [(40, 560), (80, 620), (120, 700), (200, 730), (300, 750),
      (420, 740), (480, 760), (650, 750), (750, 720), (1280, 700),
      (1320, 640), (1300, 750), (50, 760), (250, 600),
      (body_l - 25, body_bot - 10), (body_r + 25, body_bot - 10),
      (body_l - 15, body_bot + 20), (body_r + 15, body_bot + 20),
      (body_l + 20, body_bot + 30), (100, 580), (380, 700),
      (600, 720), (680, 700), (720, 760), (1100, 700), (1200, 740)]
for ang in range(0, 360, 20):
    a = math.radians(ang)
    G.append((FCX + 95 * math.cos(a), FCY + 70 * math.sin(a)))
out += [C('grass'), F(*G)]
out += [{'op': 'pause', 's': 0.35}]

# ---- Details ----
out += [C('flame2')]
for cx, cy, rx, ry, tip in FLAMES:
    for f in (0.55, 0.35, 0.18):
        out.append(S(flame_blob(cx, cy + 5, rx * f, ry * f * 0.85, tip * 0.8, 28), 0.0, 0.005))

out += [C('star')]
for sx, sy in STARS:
    out.append(dot(sx, sy, 4 if (sx + sy) % 3 else 5))
out += [C('white')]
for sx, sy in [(180, 90), (600, 55), (1020, 100)]:
    out.append(S([(sx - 7, sy), (sx + 7, sy)], 0, 0.006))
    out.append(S([(sx, sy - 7), (sx, sy + 7)], 0, 0.006))

out += [C('dkgreen')]
for x, y in [(50, GHY + 50), (140, GHY + 70), (280, 730), (420, 750),
             (650, 760), (750, 740), (1280, 710), (1320, 745),
             (90, 660), (200, 690), (480, 710), (50, 590),
             (1100, 720), (1180, 760)]:
    if body_l < x < body_r and y < body_bot + 10: continue
    if in_tent(x, y) or in_flame(x, y) or near_logs(x, y, 16): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))

for (x, y, fc) in [(70, GHY + 40, 'flower'), (260, 710, 'flower2'), (420, 730, 'flower'),
                   (1260, 600, 'flower2'), (1320, 690, 'flower'), (110, 710, 'flower2'),
                   (680, 720, 'flower'), (200, 600, 'flower2')]:
    if body_l < x < body_r and head_top < y < body_bot: continue
    if in_tent(x, y) or in_flame(x, y) or near_logs(x, y, 20) or in_backpack(x, y): continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('moon'), dot(x, y, 4)]

out += [C('wood')]
stick_a = (body_r + 10, min(body_bot - 40, GHY + 30))
stick_b = (FCX - 40, FCY - 50)
out += rod_strokes(stick_a, stick_b, w=3, n=3)
out += [C('white')]
for f in (1.0, 0.6, 0.3):
    out.append(S(ell(FCX - 40, FCY - 55, 10 * f, 8 * f, 20, 1), 0.0, 0.005))

out += [C('ink')]
for x, y in [(480, 55), (820, 48)]:
    out.append(S(cr([(x - 14, y), (x - 7, y - 6), (x, y), (x + 7, y - 6), (x + 14, y)], 5), 0, 0.008))

# ---- seed-check ----
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p):
    return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
PROTECTED = {'skin', 'dress', 'cheek', 'shoe'}
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
                    if probe.getpixel(CORNER) != before or filled > 60000:
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
print('top', Counter(im.getdata()).most_common(12))
skin = sum(1 for p in im.getdata() if p == (247, 172, 196))
assert skin < 90000, skin
assert white < 120000, white
assert im.getpixel((10, 200)) == (55, 70, 140), im.getpixel((10, 200))
assert im.getpixel((50, 720)) == (90, 160, 55), im.getpixel((50, 720))
assert im.getpixel((900, 400)) == (240, 210, 150), im.getpixel((900, 400))
fc=im.getpixel((540, 580)); print('flame',fc); assert fc in ((255,120,30),(255,210,60)), fc
mc=im.getpixel((1180, 120)); print('moon',mc); assert mc in ((255,240,180),(40,30,32)), mc
pc=im.getpixel((int(BPX), int(BPY))); print('pack',pc); assert pc==(70,130,200), pc
print('sky', im.getpixel((10,200)), 'grass', im.getpixel((50,720)),
      'tent', im.getpixel((900,400)), 'flame', fc, 'moon', mc, 'pack', pc)
sky_n=sum(1 for p in im.getdata() if p==(55,70,140))
grass_n=sum(1 for p in im.getdata() if p==(90,160,55))
assert sky_n>200000 and grass_n>200000, (sky_n, grass_n)

D = {'name': 'peppa-camp', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa camping at dusk: triangular tent with door, campfire with flames+logs, roasting marshmallow stick, backpack, moon, stars, dusk sky, grass, flowers. Horizon gaps at dress and tent. Bucket fills for sky/grass; concentric props.'}
json.dump(D, open('./peppa_camp_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa18\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa18.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_camp_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors')
