#!/usr/bin/env python3
"""Peppa picking apples in the orchard (drawing-peppa-pig-21).
Peppa (red dress) reaches up holding a freshly picked red apple; a big apple tree
beside her and a smaller one on the right (bumpy crowns bucket-filled green, trunks
bucket-filled brown, crossing the horizon so the horizon stops at each trunk); a wicker
basket on the grass full of apples (apple tops are closed bumps on the rim, bucket red);
apples on the crowns painted after all big fills (outline + bucket red + stem + leaf);
fallen apples, sun, cloud, birds, tufts, flowers."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(21)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = [dict(o) for o in E['ops']]
out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['leaf', [60, 150, 60]], ['trunk', [140, 90, 50]],
 ['basket', [215, 160, 85]], ['weave', [160, 105, 45]], ['apple', [232, 35, 45]],
 ['stem', [95, 60, 30]], ['orange', [255, 160, 50]], ['pink', [255, 130, 190]], ['purple', [165, 100, 215]],
]
assert len(pal) <= 22

def T(p, s, ox, oy):
    return [round(ox + (p[0] - 289) * s, 1), round(oy + (p[1] - 40) * s, 1)]
def char(s, ox, oy):
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
        r.append(o)
    return r
def S(pts, amp=1.0, dl=0.009):
    return {'op': 'stroke', 'amp': amp, 'dl': dl, 'pts': [[round(x, 1), round(y, 1)] for x, y in pts]}
def C(c): return {'op': 'color', 'c': c}
def F(*seeds): return {'op': 'fill', 'seeds': [list(x) for x in seeds]}
def P(s): return {'op': 'pause', 's': s}
def cr(Pp, n=10):
    Pp = [Pp[0]] + Pp + [Pp[-1]]; o = []
    for i in range(1, len(Pp) - 2):
        p0, p1, p2, p3 = Pp[i - 1:i + 3]
        for k in range(n):
            t = k / n
            o.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t
                                 + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return o + [Pp[-2]]
def ell(cx, cy, rx, ry, n=72, extra=4, rot=0, a0=0):
    ca, sa = math.cos(rot), math.sin(rot)
    r = []
    for k in range(n + extra):
        a = a0 + 2 * math.pi * k / n; x, y = rx * math.cos(a), ry * math.sin(a)
        r.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return r
def dot(cx, cy, r):
    pts = []
    for rr in [r, r * .66, r * .33, 1]:
        pts += ell(cx, cy, rr, rr, 24, 1)
    return S(pts, 0, 0.006)
def blob(cx, cy, rx, ry, rot=0, fs=(1.0, .75, .5, .25)):
    pts = []
    for f in fs:
        pts += ell(cx, cy, rx * f, ry * f, 32, 1, rot)
    pts.append((cx, cy))
    return S(pts, 0, 0.005)
def poly(Pp): return list(Pp) + [Pp[0], Pp[1]]
def side(s, ox, oy, y, right):
    Pd = [T(p, s, ox, oy) for p in ops[12]['pts']]
    c = [p for p in Pd if abs(p[1] - y) < 14] or sorted(Pd, key=lambda q: abs(q[1] - y))[:8]
    p = max(c, key=lambda q: q[0]) if right else min(c, key=lambda q: q[0])
    return [p[0] + (-6 if right else 6), p[1]]
def cloud(cx, cy, sc):
    Pc = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        Pc.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(Pc + Pc[:3], 0.1, 0.008)
def crown_r(a, rx, ry, bumps):
    # bumpy crown radius scale at angle a
    return 1 + 0.07 * abs(math.sin(bumps * a / 2))
def crown_pts(cx, cy, rx, ry, bumps, n=150):
    pts = []
    for k in range(n + 4):
        a = 2 * math.pi * k / n; b = crown_r(a, rx, ry, bumps)
        pts.append((cx + rx * b * math.cos(a), cy + ry * b * math.sin(a)))
    return pts
def crown_bottom_y(cx, cy, rx, ry, bumps, x):
    best = None
    for k in range(2000):
        a = math.pi * k / 2000  # lower half (y grows down)
        b = crown_r(a, rx, ry, bumps)
        px, py = cx + rx * b * math.cos(a), cy + ry * b * math.sin(a)
        if best is None or abs(px - x) < abs(best[0] - x): best = (px, py)
    return best[1]

MARK = {}
# ---------- 1. Peppa (right arm raised, as in the base drawing) ----------
PS, PX, PY = 0.62, 95, 100
out += char(PS, PX, PY)
out += [P(0.5)]
xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r, head_top, body_bot = min(xs), max(xs), min(ys), max(ys)
hand_pts = [T(p, PS, PX, PY) for i in (21, 22) for p in ops[i]['pts']] + [T(p, PS, PX, PY) for p in ops[17]['pts']]
HX = max(p[0] for p in hand_pts); HY = min(p[1] for p in hand_pts)
print('peppa box', round(body_l), round(head_top), round(body_r), round(body_bot), 'hand tip', HX, HY)
MARK['peppa_end'] = len(out)

# ---------- 2. The apple in Peppa's hand ----------
HA = (HX + 14, HY - 14, 19)
out += [C('ink'), S(ell(HA[0], HA[1], HA[2], HA[2] * 0.95, 48, 4), 0.02, 0.008)]
out += [C('apple'), F((HA[0], HA[1] + 2))]
out += [C('stem'), S([(HA[0], HA[1] - HA[2] + 2), (HA[0] + 3, HA[1] - HA[2] - 12)], 0, 0.008)]
out += [C('leaf'), blob(HA[0] + 12, HA[1] - HA[2] - 8, 9, 4.5, -0.4, (1.0, .5))]
out += [C('white'), dot(HA[0] - 7, HA[1] - 6, 3)]
out += [P(0.4)]
MARK['handapple_end'] = len(out)

# ---------- 3. Big apple tree: crown + trunk ----------
GHY = int(T((469, 480), PS, PX, PY)[1])
T1 = dict(cx=640, cy=200, rx=225, ry=140, bumps=9)
T1B = 600  # trunk bottom
T1L, T1R = 612, 672
out += [C('ink'), S(crown_pts(**T1), 0.15, 0.008)]
yl = crown_bottom_y(**T1, x=T1L) - 2; yr = crown_bottom_y(**T1, x=T1R) - 2
out += [S(cr([(T1L, yl), (T1L - 2, (yl + T1B) / 2), (T1L - 14, T1B)], 8), 0.1, 0.009),
        S(cr([(T1R, yr), (T1R + 2, (yr + T1B) / 2), (T1R + 14, T1B)], 8), 0.1, 0.009),
        S(cr([(T1L - 16, T1B), (T1L + 20, T1B + 8), (T1R - 20, T1B + 8), (T1R + 16, T1B)], 6), 0.05, 0.009)]
out += [P(0.3)]
MARK['tree1_end'] = len(out)
# ---------- 4. Small apple tree on the right ----------
T2 = dict(cx=1175, cy=215, rx=150, ry=110, bumps=7)
T2B = 520
T2L, T2R = 1155, 1197
out += [S(crown_pts(**T2), 0.15, 0.008)]
yl2 = crown_bottom_y(**T2, x=T2L) - 2; yr2 = crown_bottom_y(**T2, x=T2R) - 2
out += [S(cr([(T2L, yl2), (T2L - 1, (yl2 + T2B) / 2), (T2L - 10, T2B)], 8), 0.1, 0.009),
        S(cr([(T2R, yr2), (T2R + 1, (yr2 + T2B) / 2), (T2R + 10, T2B)], 8), 0.1, 0.009),
        S(cr([(T2L - 12, T2B), (T2L + 12, T2B + 6), (T2R - 12, T2B + 6), (T2R + 12, T2B)], 6), 0.05, 0.009)]
out += [P(0.3)]
MARK['tree2_end'] = len(out)
# ---------- 5. Basket on the grass, full of apples ----------
BL, BR, BT, BB = 362, 558, 520, 610
out += [S(poly([(BL, BT), (BR, BT), (BR - 18, BB), (BL + 18, BB)]), 0.05, 0.009)]
APB = [(424, 20), (460, 21), (496, 20)]
for x, r in APB:
    out.append(S([(x - r, BT)] + [(x + r * math.cos(math.pi + math.pi * k / 30), BT + r * 0.95 * math.sin(math.pi + math.pi * k / 30)) for k in range(31)], 0.0, 0.008))
out += [S(cr([(BL + 6, BT), (BL + 14, BT - 78), ((BL + BR) / 2, BT - 104), (BR - 14, BT - 78), (BR - 6, BT)], 10), 0.05, 0.009),
        S(cr([(BL + 30, BT), (BL + 38, BT - 62), ((BL + BR) / 2, BT - 82), (BR - 38, BT - 62), (BR - 30, BT)], 10), 0.05, 0.009)]
out += [P(0.3)]
MARK['basket_end'] = len(out)
# ---------- 6. Bucket fills: crowns, trunks, basket, basket apples ----------
out += [C('leaf'), F((T1['cx'], T1['cy']), (T1['cx'] - 150, T1['cy']), (T1['cx'] + 150, T1['cy']),
                     (T1['cx'], T1['cy'] - 100), (T1['cx'], T1['cy'] + 100),
                     (T2['cx'], T2['cy']), (T2['cx'] - 100, T2['cy']), (T2['cx'] + 100, T2['cy']))]
MARK['leaf_fill'] = len(out)
out += [C('trunk'), F(((T1L + T1R) / 2, 450), ((T1L + T1R) / 2, T1B - 10), ((T2L + T2R) / 2, 420))]
MARK['trunk_fill'] = len(out)
# (handle pockets: regions between the two handle arcs is basket colour too)
out += [C('basket'), F(((BL + BR) / 2, BB - 20), (BL + 40, BB - 30), (BR - 40, BB - 30),
                       (BL + 21, BT - 40), (BR - 21, BT - 40), ((BL + BR) / 2, BT - 93))]
MARK['basket_fill'] = len(out)
out += [C('apple'), F(*[(x, BT - 10) for x, r in APB])]
out += [P(0.4)]
MARK['bfill_end'] = len(out)

# ---------- 7. Sun + cloud ----------
SUNX, SUNY, SUNR = 932, 82, 44
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
CLOUDS = [(205, 52, 0.62)]
out += [cloud(*c) for c in CLOUDS]
out += [P(0.3)]
MARK['sky_end'] = len(out)

# ---------- 8. Horizon (stops at the dress and at both trunks) ----------
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
def trunk_x(xa, xb_, ya, yb, dxend, y):
    # piecewise approx of the trunk side at height y (cr through 3 points, nearly straight)
    t = (y - ya) / (yb - ya)
    return xa + (dxend) * max(0, t - 0.5) * 2 * 0.5 + (xb_ - xa) * 0
t1l = T1L - 1; t1r = T1R + 1; t2l = T2L; t2r = T2R
print('GHY', GHY, 'dress gap', pl[0], pr[0], 'trunks', t1l, t1r, t2l, t2r)
assert yl < GHY - 20 and yl2 < GHY - 20
out += [C('dkgreen')]
segs = [(2, pl[0]), (pr[0], t1l), (t1r, t2l), (t2r, 1358)]
for a, b in segs:
    if b - a > 8:
        for dy in (0, 3, -2):
            out.append(S([(a, GHY + dy), (b, GHY + dy)], 0.05, 0.006))
out += [S([(2, GHY - 2), (2, 787)], 0.05, 0.009), S([(5, GHY - 2), (5, 787)], 0.05, 0.009),
        S([(1358, GHY - 2), (1358, 787)], 0.05, 0.009), S([(1355, GHY - 2), (1355, 787)], 0.05, 0.009),
        S([(2, 787), (1358, 787)], 0.05, 0.009), S([(2, 784), (1358, 784)], 0.05, 0.009),
        S([(2, 2), (1358, 2)], 0.05, 0.01), S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [dot(pl[0], GHY, 6), dot(pr[0], GHY, 6)]
out += [P(0.3)]
MARK['horizon_end'] = len(out)

def in_sun(x, y): return (x - SUNX) ** 2 + (y - SUNY) ** 2 < (SUNR + 8) ** 2
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_cloud(x, y): return any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS)
def in_tree(x, y):
    for t in (T1, T2):
        if ((x - t['cx']) / (t['rx'] * 1.1 + 10)) ** 2 + ((y - t['cy']) / (t['ry'] * 1.1 + 10)) ** 2 < 1: return True
    return (T1L - 25 < x < T1R + 25 and y < T1B + 20) or (T2L - 20 < x < T2R + 20 and y < T2B + 15)
def in_basket(x, y): return BL - 12 < x < BR + 12 and BT - 105 < y < BB + 12
def in_ha(x, y): return (x - HA[0]) ** 2 + (y - HA[1]) ** 2 < (HA[2] + 22) ** 2

# ---------- 9. Bucket fills: sky, grass, sun ----------
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_cloud(x, y) or in_sun(x, y) or in_tree(x, y) or in_ha(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (pr[0] + 14, GHY - 12), (t1l - 16, GHY - 12), (t1r + 16, GHY - 12),
        (t2l - 14, GHY - 12), (t2r + 14, GHY - 12), (body_l - 20, GHY - 14)]
SKY = [(x, y) for x, y in SKY if y < GHY - 7]
out += [C('sky'), F(*SKY)]
MARK['sky_fill'] = len(out)
G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if in_peppa(x, y) or in_tree(x, y) or in_basket(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), (t1l - 14, GHY + 14), (t1r + 14, GHY + 14),
      (t2l - 12, GHY + 14), (t2r + 12, GHY + 14), (body_l + 30, body_bot + 25),
      ((body_l + body_r) / 2, body_bot - 30), ((BL + BR) / 2, BT - 45), (BL + 50, BT - 40), (BR - 50, BT - 40),
      (BL - 20, BB - 10), (BR + 20, BB - 10), (T1L - 30, T1B + 30), (T1R + 30, T1B + 30)]
out += [C('grass'), F(*G)]
MARK['grass_fill'] = len(out)
out += [C('sun'), F((SUNX, SUNY), (SUNX - 15, SUNY), (SUNX + 15, SUNY), (SUNX, SUNY - 15), (SUNX, SUNY + 15))]
out += [P(0.4)]
MARK['fill_end'] = len(out)

# ---------- 10. Apples on the crowns (outline, bucket red, stem, leaf, shine) ----------
TA1 = [(500, 170), (585, 105), (700, 125), (790, 190), (560, 260), (690, 275), (480, 245), (630, 190)]
TA2 = [(1100, 180), (1215, 150), (1260, 245), (1140, 270)]
def apple(x, y, r=18):
    return [C('ink'), S(ell(x, y, r, r * 0.95, 44, 4), 0.02, 0.008), C('apple'), F((x, y + 2))]
for x, y in TA1:
    out += apple(x, y)
MARK['apples1_end'] = len(out)
for x, y in TA2:
    out += apple(x, y, 16)
MARK['apples2_end'] = len(out)
out += [C('stem')]
for x, y in TA1 + TA2:
    out.append(S([(x, y - 16), (x + 2, y - 27)], 0, 0.008))
out += [C('white')] + [dot(x - 6, y - 5, 3) for x, y in TA1 + TA2]
out += [P(0.3)]
MARK['stems_end'] = len(out)

# ---------- 11. Fallen apples on the grass ----------
FA = [(770, 655), (1010, 700), (880, 560)]
for x, y in FA:
    out += apple(x, y, 17)
out += [C('stem')] + [S([(x, y - 15), (x - 2, y - 25)], 0, 0.008) for x, y in FA]
out += [C('white')] + [dot(x - 6, y - 5, 3) for x, y in FA]
out += [P(0.3)]
MARK['fallen_end'] = len(out)

# ---------- 12. Basket weave ----------
out += [C('weave')]
for k in range(1, 6):
    x = BL + 18 + k * (BR - BL - 36) / 6
    out.append(S([(x - 4 + 3 * (k - 3) / 3, BT + 12), (x - 4 + 2 * (k - 3) / 3 * 0.6, BB - 10)], 0.1, 0.008))
for y in (BT + 32, BT + 58):
    f = (y - BT) / (BB - BT)
    out.append(S([(BL + 14 + 18 * f, y), (BR - 14 - 18 * f, y)], 0.1, 0.008))
out += [P(0.3)]
MARK['weave_end'] = len(out)

# ---------- 13. Details: sun rays, tufts, flowers, birds ----------
out += [C('sun')]
for ang in range(0, 360, 30):
    a = math.radians(ang)
    out.append(S([(SUNX + (SUNR + 8) * math.cos(a), SUNY + (SUNR + 8) * math.sin(a)),
                  (SUNX + (SUNR + 26) * math.cos(a), SUNY + (SUNR + 26) * math.sin(a))], 0.1, 0.008))
MARK['rays_end'] = len(out)
out += [C('dkgreen')]
TUFT = [(45, GHY + 50), (150, GHY + 110), (60, 700), (200, 740), (330, 760), (480, 750), (620, 720),
        (720, 470), (840, 760), (960, 600), (1100, 760), (1300, 700), (1320, 470), (1050, 480), (330, 650)]
for x, y in TUFT:
    if in_peppa(x, y) or in_basket(x, y) or in_tree(x, y): continue
    if any(math.dist((x, y), q) < 40 for q in FA): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)
for (x, y, fc) in [(80, GHY + 40, 'pink'), (250, 700, 'orange'), (440, 700, 'purple'), (600, 640, 'pink'),
                   (1250, 600, 'orange'), (130, 760, 'pink'), (1180, 700, 'purple'), (980, 470, 'pink')]:
    if in_peppa(x, y) or in_basket(x, y) or in_tree(x, y): continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]
MARK['flowers_end'] = len(out)
out += [C('ink')]
for x, y in [(400, 60), (985, 300), (1040, 45)]:
    out.append(S(cr([(x - 14, y), (x - 7, y - 6), (x, y), (x + 7, y - 6), (x + 14, y)], 5), 0, 0.008))
MARK['end'] = len(out)

# ---------- seed check (PIL simulation) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
LATE = {'apple'}
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'leaf', 'trunk', 'basket', 'apple', 'sun'}
for o in out:
    if o['op'] == 'color': cc = col[o['c']]; o_c = o['c']
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
                        if not (3 <= x < 1357 and 3 <= y < 787) or ok is not None: continue
                        colors = im.crop((x - 3, y - 3, x + 4, y + 4)).getcolors(500) or []
                        if len(colors) == 1 and (im.getpixel((x, y)) == (255, 255, 255) or (o_c in LATE and im.getpixel((x, y)) not in (col['ink'], cc))): ok = (x, y)
                if ok: break
            if ok:
                if o_c in PROTECTED:
                    probe = im.copy(); ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc) - sum(1 for p in im.getdata() if p == cc)
                    lim = 160000 if o_c == 'leaf' else 60000
                    if probe.getpixel(CORNER) != im.getpixel(CORNER) or filled > lim:
                        print('reject leak seed', o_c, ok, 'filled', filled); continue
                ImageDraw.floodfill(im, ok, cc); keep.append(list(ok))
            else:
                print('drop seed', o_c, s)
        if not keep:
            im.save('./preview_fail.png'); raise SystemExit('no seeds kept: ' + str(o_c))
        o['seeds'] = keep
im.save('./preview.png')
cnt = Counter(im.getdata())
print('white px left', cnt[(255, 255, 255)])
print('top', cnt.most_common(14))
assert im.getpixel((10, 200)) == col['sky'], im.getpixel((10, 200))
assert im.getpixel((50, 760)) == col['grass'], im.getpixel((50, 760))
assert im.getpixel((T1['cx'] - 120, T1['cy'] + 40)) == col['leaf']
assert im.getpixel((int((T1L + T1R) / 2), 500)) == col['trunk']
assert im.getpixel((BL + 30, BB - 25)) == col['basket'], im.getpixel((BL + 30, BB - 25))
def est(ops_):
    t = 0
    for o in ops_:
        if o['op'] == 'stroke':
            n = 1
            for p, q in zip(o['pts'], o['pts'][1:]): n += max(1, int(math.dist(p, q) / 4))
            t += 0.3 + n * (o.get('dl', 0.009) + 0.0021)
        elif o['op'] == 'fill': t += 0.72 * len(o['seeds']) + 0.5
        elif o['op'] == 'color': t += 0.6
        elif o['op'] == 'pause': t += o['s']
    return t
print('estimate s', round(est(out), 1))
D = {'name': 'peppa-apple', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa picking apples: red dress, raised hand holding an apple, big and small apple trees (crowns+trunks bucket-filled; horizon stops at trunks and dress), wicker basket full of apples, apples on crowns, fallen apples, sun, cloud, birds, grass.'}
json.dump(D, open('./peppa_apple_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa21\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa21.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_apple_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
