#!/usr/bin/env python3
"""Peppa feeding the hen and chicks on the farm (drawing-peppa-pig-27, 佩奇喂小鸡)."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(27)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = [dict(o) for o in E['ops']]
out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['rred', [235, 50, 50]], ['rorange', [255, 150, 40]], ['ryellow', [255, 230, 70]],
 ['rgreen', [90, 195, 80]], ['rblue', [60, 130, 225]], ['rpurple', [150, 90, 210]],
 ['pink', [255, 130, 190]], ['orange', [255, 160, 50]], ['leaf', [60, 150, 60]], ['snail', [200, 140, 80]],
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

from shapely.geometry import Polygon
from shapely.ops import unary_union
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['barn', [200, 52, 45]], ['roof', [120, 72, 52]], ['hen', [226, 156, 92]],
 ['wing', [176, 104, 58]], ['chick', [255, 222, 60]], ['beak', [255, 150, 40]], ['comb', [232, 40, 40]],
 ['bowl', [70, 140, 220]], ['grain', [236, 196, 96]], ['nest', [196, 146, 72]], ['pink', [255, 140, 200]],
]
assert len(pal) <= 22
MARK = {}
# ---------- 1. Peppa ----------
PS, PX, PY = 0.64, 90, 150
out += char(PS, PX, PY)
out += [P(0.5)]
xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r, head_top, body_bot = min(xs), max(xs), min(ys), max(ys)
print('peppa box', round(body_l), round(head_top), round(body_r), round(body_bot))
MARK['peppa_end'] = len(out)
GHY = int(T((469, 480), PS, PX, PY)[1]); print('GHY', GHY)
HAND = T((655, 381), PS, PX, PY); print('HAND', HAND)

def rect(x0, y0, x1, y1):
    return S([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0), (x1, y0)], 0.03, 0.012)
def outline(geom, start_deg=0):
    c = list(geom.exterior.coords)[:-1]
    return S(c + c[:3], 0.03, 0.009)
def E_(cx, cy, rx, ry, rot=0, n=72):
    return Polygon(ell(cx, cy, rx, ry, n, 0, rot))
# ---------- 2. Grain bowl in Peppa's hand ----------
BX, BY = HAND[0] + 42, HAND[1] - 16
out += [C('ink'), S(ell(BX, BY, 46, 12, 64, 4), 0.02, 0.009)]
bowl = [(BX - 46 + 92 * k / 40, BY + 40 * math.sin(math.pi * k / 40) ** 0.8) for k in range(41)]
out += [S([(BX - 48, BY - 2)] + bowl + [(BX + 48, BY - 2)], 0.02, 0.009)]
MARK['bowl_line'] = len(out)
out += [P(0.3)]
# ---------- 3. Red barn on the right, sitting on the horizon ----------
HX0, HX1, HT, HB = 1070, 1250, GHY - 130, GHY + 36
RA = (1160, HT - 92)
out += [rect(HX0, HT, HX1, HB)]
MARK['barn_wall'] = len(out)
out += [S([(HX0 - 22, HT), RA, (HX1 + 22, HT), (HX0 - 22, HT), RA], 0.03, 0.012)]
MARK['barn_roof'] = len(out)
LX, LY, LR = 1160, HT - 34, 17
out += [S(ell(LX, LY, LR, LR, 48, 4), 0, 0.009)]
MARK['barn_loft'] = len(out)
DOOR = (1124, HT + 66, 1196, HB)
out += [S([(DOOR[0], HB), (DOOR[0], DOOR[1]), (DOOR[2], DOOR[1]), (DOOR[2], HB)], 0.03, 0.012)]
MARK['barn_door'] = len(out)
out += [P(0.4)]
# ---------- 4. Sun + clouds ----------
SUX, SUY, SUR = 585, 96, 44
out += [S(ell(SUX, SUY, SUR, SUR, 64, 4), 0.03, 0.008)]
MARK['sun_line'] = len(out)
CL = [(880, 112, 1.0), (330, 62, 0.62)]
for cx, cy, sc in CL: out.append(cloud(cx, cy, sc))
MARK['clouds'] = len(out)
out += [P(0.3)]
# ---------- 5. Hen ----------
HNX, HNY = 820, 590
hen = unary_union([E_(HNX, HNY, 86, 58), E_(HNX + 62, HNY - 64, 34, 34), E_(HNX - 76, HNY - 30, 34, 17, -0.95)]).simplify(0.6)
out += [outline(hen)]
MARK['hen_body'] = len(out)
WX, WY = HNX - 8, HNY + 2
out += [S(ell(WX, WY, 44, 25, 60, 4, -0.18), 0.02, 0.009)]
MARK['hen_wing'] = len(out)
out += [C('beak')]
for lx in (HNX - 22, HNX + 26):
    out += [S([(lx, HNY + 56), (lx, HNY + 86)], 0, 0.01)]
    for dx in (-12, 0, 12): out.append(S([(lx, HNY + 86), (lx + dx, HNY + 98)], 0, 0.01))
MARK['hen_legs'] = len(out)
out += [P(0.3)]
# ---------- 6. Chicks ----------
CH = [(450, 664, 1), (598, 722, 1), (652, 604, -1)]
chick_geo = []
for i, (cx, cy, fd) in enumerate(CH):
    g = unary_union([E_(cx, cy, 32, 28), E_(cx + 22 * fd, cy - 30, 20, 20)]).simplify(0.6)
    chick_geo.append(g)
    out += [C('ink'), outline(g)]
    MARK['chick%d' % i] = len(out)
out += [P(0.3)]
# ---------- 7. Nest with eggs by the barn ----------
NX, NY = 1150, 600
out += [C('ink'), S(ell(NX, NY, 70, 26, 72, 4), 0.02, 0.009)]
for ex in (NX - 24, NX + 22):
    out += [S(ell(ex, NY - 22, 19, 25, 48, 4), 0, 0.009)]
MARK['nest'] = len(out)
out += [P(0.3)]
# ---------- 8. Horizon (stops at the dress and at the barn) + border ----------
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
out += [C('dkgreen')]
for a, b in [(2, pl[0]), (pr[0], HX0 + 2), (HX1 - 2, 1358)]:
    for dy in (0, 3, -2):
        out.append(S([(a, GHY + dy), (b, GHY + dy)], 0.05, 0.006))
MARK['horizon_line'] = len(out)
out += [S([(2, GHY - 2), (2, 787)], 0.05, 0.009), S([(5, GHY - 2), (5, 787)], 0.05, 0.009),
        S([(1358, GHY - 2), (1358, 787)], 0.05, 0.009), S([(1355, GHY - 2), (1355, 787)], 0.05, 0.009),
        S([(2, 787), (1358, 787)], 0.05, 0.009), S([(2, 784), (1358, 784)], 0.05, 0.009)]
MARK['border_bottom'] = len(out)
out += [S([(2, 2), (1358, 2)], 0.05, 0.01), S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [dot(pl[0], GHY, 6), dot(pr[0], GHY, 6)]
out += [P(0.3)]
MARK['horizon_end'] = len(out)
# ---------- 9. Fills (paint bucket) ----------
out += [C('bowl'), F((BX - 18, BY + 24), (BX + 18, BY + 24), (BX, BY + 28))]
MARK['bowl_fill'] = len(out)
out += [C('grain'), F((BX, BY), (BX - 20, BY), (BX + 20, BY))]
MARK['grain_fill'] = len(out)
out += [C('barn'), F((HX0 + 22, HT + 80), (HX1 - 22, HT + 80), ((HX0 + HX1) / 2, HT + 26), (HX0 + 14, HB - 12), (HX1 - 14, HB - 12))]
MARK['barn_fill'] = len(out)
out += [C('roof'), F((RA[0] - 52, HT - 12), (RA[0] + 52, HT - 12), (RA[0], HT - 70), (RA[0] - 30, HT - 30), (RA[0] + 30, HT - 30))]
MARK['roof_fill'] = len(out)
out += [C('sun'), F((SUX, SUY), (SUX - 20, SUY + 10))]
MARK['sun_fill'] = len(out)
out += [C('hen'), F((HNX + 50, HNY + 20), (HNX - 50, HNY + 34), (HNX + 62, HNY - 68), (HNX - 84, HNY - 36), (HNX + 40, HNY - 40), (HNX - 40, HNY - 36))]
MARK['hen_fill'] = len(out)
out += [C('wing'), F((WX, WY), (WX + 18, WY - 4))]
MARK['wing_fill'] = len(out)
out += [C('chick'), F(*[(cx, cy + 6) for cx, cy, fd in CH] + [(cx + 22 * fd, cy - 32) for cx, cy, fd in CH])]
MARK['chick_fill'] = len(out)
out += [C('nest'), F((NX, NY + 12), (NX - 52, NY + 4), (NX + 52, NY + 4), (NX, NY - 8))]
MARK['nest_fill'] = len(out)
out += [C('roof'), F(((DOOR[0] + DOOR[2]) / 2, DOOR[1] + 22), ((DOOR[0] + DOOR[2]) / 2, HB - 20), (DOOR[0] + 18, (DOOR[1] + HB) / 2), (DOOR[2] - 18, (DOOR[1] + HB) / 2))]
MARK['door_fill'] = len(out)
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_barn(x, y): return HX0 - 30 < x < HX1 + 30 and RA[1] - 10 < y < HB + 10
def in_sun(x, y): return (x - SUX) ** 2 + (y - SUY) ** 2 < (SUR + 12) ** 2
def in_cloud(x, y): return any(abs(x - cx) < 100 * sc and abs(y - cy) < 52 * sc for cx, cy, sc in CL)
def in_bowl(x, y): return BX - 60 < x < BX + 60 and BY - 24 < y < BY + 52
def in_hen(x, y): return hen.buffer(14).contains(Point(x, y))
def in_chick(x, y): return any(g.buffer(14).contains(Point(x, y)) for g in chick_geo) or any(abs(x - cx) < 26 and cy + 20 < y < cy + 52 for cx, cy, _ in CH)
def in_nest(x, y): return NX - 84 < x < NX + 84 and NY - 60 < y < NY + 40
def in_legs(x, y): return HNX - 50 < x < HNX + 50 and HNY + 40 < y < HNY + 110
from shapely.geometry import Point
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_barn(x, y) or in_sun(x, y) or in_cloud(x, y) or in_bowl(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (pr[0] + 14, GHY - 12), (body_l - 20, GHY - 14), (HX0 - 14, GHY - 12), (HX1 + 14, GHY - 12),
        (HX0 - 10, HT - 6), (HX1 + 10, HT - 6)]
SKY = [(x, y) for x, y in SKY if y < GHY - 7]
out += [C('sky'), F(*SKY)]
MARK['sky_fill'] = len(out)
G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if in_peppa(x, y) or in_barn(x, y) or in_hen(x, y) or in_chick(x, y) or in_nest(x, y) or in_legs(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), (body_l + 30, body_bot + 25), ((body_l + body_r) / 2, body_bot - 30),
      (HX0 - 12, HB), (HX1 + 12, HB)]
out += [C('grass'), F(*G)]
MARK['grass_fill'] = len(out)
out += [P(0.4)]
MARK['fill_end'] = len(out)
# ---------- 10. Barn details ----------
out += [C('white')]
d0 = 7
out += [S([(DOOR[0] + d0, DOOR[1] + d0), (DOOR[2] - d0, HB - d0)], 0, 0.012), S([(DOOR[2] - d0, DOOR[1] + d0), (DOOR[0] + d0, HB - d0)], 0, 0.012)]
MARK['door_x'] = len(out)
out += [C('ink'), S([(LX - LR, LY), (LX + LR, LY)], 0, 0.012), S([(LX, LY - LR), (LX, LY + LR)], 0, 0.012)]
MARK['loft_cross'] = len(out)
# ---------- 11. Hen face ----------
HHX, HHY = HNX + 62, HNY - 64
out += [C('comb')] + [dot(HHX - 14 + 13 * k, HHY - 36 + (4 if k != 1 else -2), 9) for k in range(3)]
MARK['hen_comb'] = len(out)
tri = [(HHX + 30, HHY - 8), (HHX + 54, HHY + 2), (HHX + 30, HHY + 12)]
def solid_tri(tr, n=4):
    cx, cy = sum(p[0] for p in tr) / 3, sum(p[1] for p in tr) / 3; pts = []
    for f in [1 - k / n for k in range(n)]:
        q = [(cx + (p[0] - cx) * f, cy + (p[1] - cy) * f) for p in tr]; pts += q + [q[0]]
    return S(pts + [(cx, cy)], 0, 0.008)
out += [C('beak'), solid_tri(tri)]
MARK['hen_beak'] = len(out)
out += [C('comb'), dot(HHX + 30, HHY + 22, 7)]
MARK['hen_wattle'] = len(out)
out += [C('ink'), dot(HHX + 10, HHY - 8, 5)]
MARK['hen_eye'] = len(out)
# ---------- 12. Chick faces ----------
for i, (cx, cy, fd) in enumerate(CH):
    hx, hy = cx + 22 * fd, cy - 30
    out += [C('ink'), dot(hx + 6 * fd, hy - 4, 4)]
    out += [C('beak'), solid_tri([(hx + 17 * fd, hy - 3), (hx + 31 * fd, hy + 2), (hx + 17 * fd, hy + 8)], 3)]
    out += [C('ink'), S([(cx - 18 * fd, cy - 4), (cx - 10 * fd, cy + 8), (cx + 4 * fd, cy + 10)], 0, 0.01)]
    out += [C('beak')]
    for lx in (cx - 8, cx + 10):
        out += [S([(lx, cy + 26), (lx, cy + 40)], 0, 0.01), S([(lx - 7, cy + 42), (lx + 7, cy + 42)], 0, 0.01)]
    MARK['chick_face%d' % i] = len(out)
# ---------- 13. Sun rays ----------
out += [C('sun')]
for k in range(12):
    a = 2 * math.pi * k / 12 + 0.13
    out.append(S([(SUX + (SUR + 12) * math.cos(a), SUY + (SUR + 12) * math.sin(a)), (SUX + (SUR + 34) * math.cos(a), SUY + (SUR + 34) * math.sin(a))], 0, 0.011))
MARK['sun_rays'] = len(out)
# ---------- 14. Grain: thrown arc + piles on the ground ----------
out += [C('grain')]
x0, y0, x1, y1 = BX + 30, BY - 6, 545, 640
arc = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - 120 * math.sin(math.pi * t)) for t in [k / 9 for k in range(1, 9)]]
for x, y in arc: out.append(dot(x, y, 4))
MARK['grain_arc'] = len(out)
GR = [(520, 630), (552, 652), (530, 680), (565, 690), (505, 702), (585, 640), (790, 716), (850, 712), (884, 730)]
gr_n = 0
for x, y in GR:
    if in_chick(x, y) or in_legs(x, y): continue
    out.append(dot(x, y, 4)); gr_n += 1
print('grain on ground', gr_n)
MARK['grain_ground'] = len(out)
# ---------- 15. Tufts, flowers ----------
def busy(x, y):
    return in_peppa(x, y) or in_barn(x, y) or in_hen(x, y) or in_chick(x, y) or in_nest(x, y) or in_legs(x, y) or any(math.dist((x, y), g) < 22 for g in GR)
out += [C('dkgreen')]
TUFT = [(45, GHY + 50), (150, GHY + 120), (60, 700), (330, 760), (400, 520), (700, 760), (960, 520),
        (1100, 760), (1300, 700), (1290, 520), (460, 470), (1220, 660)]
for x, y in TUFT:
    if busy(x, y): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)
FL = [(250, 690, 'pink'), (990, 712, 'sun')]
fl_marks = []
for (x, y, fc) in FL:
    if busy(x, y): print('skip flower', x, y); continue
    out += [C('dkgreen'), S([(x, y + 22), (x, y + 6)], 0.1, 0.008)]
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5) for k in range(5)] + [C('white' if fc != 'sun' else 'beak'), dot(x, y, 4)]
    fl_marks.append(len(out))
MARK['flowers_end'] = len(out)
MARK['flower_each'] = fl_marks
MARK['end'] = len(out)
# ---------- seed check (PIL simulation) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
LATE = set()
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'bowl', 'grain', 'barn', 'roof', 'sun', 'hen', 'wing', 'chick', 'nest'}
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
                    lim = 60000
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
A_ = [((10, 200), 'sky'), ((50, 760), 'grass'), ((HX0 + 20, HT + 110), 'barn'), ((RA[0], HT - 60), 'roof'), ((SUX, SUY + 20), 'sun'),
      ((HNX + 50, HNY + 30), 'hen'), ((HHX - 10, HHY + 10), 'hen'), ((WX, WY + 5), 'wing'), ((BX, BY + 18), 'bowl'), ((NX, NY + 14), 'nest'), (((DOOR[0] + DOOR[2]) / 2, DOOR[1] + 24), 'roof'), ((BX, BY + 26), 'bowl'), ((BX - 10, BY + 2), 'grain'),
      ((HX1 + 40, GHY + 40), 'grass'), ((880, 112), 'white'), ((1000, 300), 'sky'), ((700, 500), 'grass')]
for (x, y), c in A_: assert im.getpixel((x, y)) == col[c], ((x, y), c, im.getpixel((x, y)))
for cx, cy, fd in CH: assert im.getpixel((cx, cy + 18)) == col['chick'], (cx, cy, im.getpixel((cx, cy + 18)))
D = {'name': 'peppa-chicks', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa feeding the hen and chicks on the farm: grain bowl in her hand, red barn on the horizon at the right (horizon stops at the dress and barn walls), sun + 2 clouds, a hen (one union outline of body+head+tail, wing ellipse), three chicks (union body+head outlines), nest with two eggs; bucket fills for bowl/grain/barn/roof/sun/hen/wing/chicks/nest then sky and grass seed grids; then door brace, comb/beak/wattle/eye, chick faces and wings, sun rays, thrown grain arc and grain on the ground, tufts and flowers.'}
json.dump(D, open('./peppa_chicks_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa27\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa27.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_chicks_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
