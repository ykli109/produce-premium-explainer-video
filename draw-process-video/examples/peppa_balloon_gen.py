#!/usr/bin/env python3
"""Peppa in a hot-air balloon (drawing-peppa-pig-22).
Large vertically striped rainbow balloon in the upper/middle sky, wicker basket
with rigging, Peppa (red dress, classic head) standing in the basket with hands
on the rim; sun, bumpy white clouds, birds; thin ground strip with tiny houses
and trees. Object fills before sky/ground; late details after big fills."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(22)
E = json.load(open('/workspace/produce-premium-explainer-video/draw-process-video/examples/peppa_strokes.json'))
ops = [dict(o) for o in E['ops']]
out = []
pal = [
    ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]],
    ['cheek', [236, 120, 155]], ['white', [255, 255, 255]],
    ['sky', [150, 210, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
    ['sun', [255, 215, 60]], ['yellow', [255, 228, 70]], ['blue', [55, 145, 230]],
    ['green', [50, 185, 95]], ['orange', [255, 145, 50]], ['pink', [255, 125, 185]],
    ['basket', [215, 160, 85]], ['weave', [160, 105, 45]], ['trunk', [140, 90, 50]],
    ['wall', [255, 236, 200]], ['roof', [196, 58, 48]], ['window', [255, 236, 140]],
]
assert len(pal) <= 22
STRIPE = ['dress', 'yellow', 'green', 'blue', 'orange', 'pink']  # 6 rainbow gores

def T(p, s, ox, oy):
    return [round(ox + (p[0] - 289) * s, 1), round(oy + (p[1] - 40) * s, 1)]

# Peppa upper body only (head + dress + face fills). Arms are redrawn onto the rim.
HEAD_DRESS = set(range(0, 13)) | {31, 32, 33, 38, 39, 40, 41, 44}

def char(s, ox, oy):
    r = []
    for i, o in enumerate(ops[:45]):
        if i not in HEAD_DRESS:
            continue
        o = dict(o)
        if o['op'] == 'stroke':
            o['pts'] = [T(p, s, ox, oy) for p in o['pts']]
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
def poly(Pp):
    return list(Pp) + [Pp[0], Pp[1]]
def cloud(cx, cy, sc):
    Pc = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        Pc.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(Pc + Pc[:3], 0.1, 0.008)

MARK = {}

# ---------- layout ----------
CX = 680
BTOP, BBOT, BRX, TRX = 42, 308, 228, 50  # taller onion-shaped envelope, room above for the flag
CAP_T = 0.16
RIM_Y, BASK_BOT = 578, 682
BASK_TOP_W, BASK_BOT_W = 250, 214
GHY = 716
PS, PX, PY = 0.44, 599.7, 349.6
# dress bottom ≈ PY+(581-40)*PS = 587.6, slightly over the rim; ears clearly below the throat

# Precompute balloon silhouette (left half points, top→throat)
BH = BBOT - BTOP
sil_ctrl = [
    (CX, BTOP),
    (CX - BRX * 0.38, BTOP + BH * 0.07),
    (CX - BRX * 0.72, BTOP + BH * 0.18),
    (CX - BRX * 0.96, BTOP + BH * 0.32),
    (CX - BRX,        BTOP + BH * 0.42),  # widest in the upper-middle
    (CX - BRX * 0.92, BTOP + BH * 0.56),
    (CX - BRX * 0.70, BTOP + BH * 0.72),
    (CX - BRX * 0.40, BTOP + BH * 0.88),
    (CX - TRX,        BBOT),
]
sil_left = cr(sil_ctrl, 16)
# right side: mirror of left, throat → apex
sil_right = [(2 * CX - x, y) for x, y in reversed(sil_left)]
# throat lip (slight downward curve) + a straight throat BAR that closes every gore
lip = cr([(CX - TRX, BBOT), (CX, BBOT + 11), (CX + TRX, BBOT)], 12)
throat_bar = [(CX - TRX, BBOT), (CX + TRX, BBOT)]
# outline: left apex→throat, lip to right throat, right throat→apex, overlap close
envelope = sil_left + lip[1:] + sil_right[1:]
if math.dist(envelope[0], envelope[-1]) > 0.5:
    envelope = envelope + [envelope[0], envelope[1]]
else:
    envelope = envelope + [envelope[1]]

def lr(y):
    """Left/right envelope x at y, linearly interpolated along the left silhouette."""
    y = max(BTOP, min(BBOT, y))
    pts = sil_left
    if y <= pts[0][1]:
        return pts[0][0], 2 * CX - pts[0][0]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        lo, hi = (y1, y2) if y1 <= y2 else (y2, y1)
        if lo <= y <= hi:
            t = 0 if abs(y2 - y1) < 1e-6 else (y - y1) / (y2 - y1)
            x = x1 + (x2 - x1) * t
            return x, 2 * CX - x
    x = pts[-1][0]
    return x, 2 * CX - x

CAP_Y = BTOP + BH * CAP_T
Lcap, Rcap = lr(CAP_Y)
# almost-horizontal cap line, endpoints cross the envelope for a T-junction
cap_line = [(Lcap - 6, CAP_Y), (Rcap + 6, CAP_Y)]

def seam_pts(frac):
    # cross the cap line and the throat bar so every gore is closed
    pts = []
    y0, y1 = CAP_Y - 8, BBOT + 1
    n = 48
    for k in range(n + 1):
        t = k / n
        y = y0 + (y1 - y0) * t
        yy = min(max(y, BTOP + 1), BBOT)
        L, R = lr(yy)
        x = L + (R - L) * frac
        pts.append((x, y))
    return pts

# ---------- 1. Basket outline ----------
BL = CX - BASK_TOP_W / 2
BR = CX + BASK_TOP_W / 2
BLb = CX - BASK_BOT_W / 2
BRb = CX + BASK_BOT_W / 2
# slightly rounded rim + trapezoid body, closed
rim = cr([(BL - 4, RIM_Y + 6), (BL, RIM_Y), (CX, RIM_Y - 3), (BR, RIM_Y), (BR + 4, RIM_Y + 6)], 8)
body = cr([(BR, RIM_Y + 4), (BRb, BASK_BOT - 8), (CX, BASK_BOT), (BLb, BASK_BOT - 8), (BL, RIM_Y + 4)], 10)
# closed silhouette
bask_outline = (
    cr([(BL, RIM_Y), (CX, RIM_Y - 3), (BR, RIM_Y)], 8)
    + cr([(BR, RIM_Y), (BRb, BASK_BOT - 6), (CX, BASK_BOT)], 8)[1:]
    + cr([(CX, BASK_BOT), (BLb, BASK_BOT - 6), (BL, RIM_Y)], 8)[1:]
    + [(BL, RIM_Y), (CX, RIM_Y - 3)]
)
out += [C('ink'), S(bask_outline, 0.08, 0.009)]
# inner rim lip (closed band look, not a leak path: short inner line only, not closing a hole)
out += [S(cr([(BL + 14, RIM_Y + 16), (CX, RIM_Y + 12), (BR - 14, RIM_Y + 16)], 8), 0.05, 0.008)]
out += [P(0.35)]
MARK['basket_end'] = len(out)

# ---------- 2. Peppa (upper body) + hands on the rim ----------
out += char(PS, PX, PY)
# shoulders from original dress sides ~ y=382, x left/right
sh_l = T((345, 382), PS, PX, PY)
sh_r = T((598, 382), PS, PX, PY)
# hands rest on the rim, a little outside the body
hand_l = (CX - 92, RIM_Y + 2)
hand_r = (CX + 92, RIM_Y + 2)
def arm(sh, hand, sign):
    # 3 parallel strokes, slight elbow bend outward
    mid = ((sh[0] + hand[0]) / 2 + sign * 16, (sh[1] + hand[1]) / 2 + 6)
    strokes = []
    for off in (-3.5, 0, 3.5):
        # offset roughly perpendicular
        dx, dy = hand[0] - sh[0], hand[1] - sh[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * off, dx / L * off
        pts = cr([(sh[0] + nx, sh[1] + ny), (mid[0] + nx, mid[1] + ny), (hand[0] + nx * 0.4, hand[1] + ny * 0.4)], 8)
        strokes.append(S(pts, 0.15, 0.007))
    # little hand blob on the rim
    strokes.append(blob(hand[0], hand[1] + 2, 9, 6, 0, (1.0, 0.55)))
    return strokes
out += [C('ink')] + arm(sh_l, hand_l, -1) + arm(sh_r, hand_r, +1)
# arm skin (after ink, before remaining peppa fills already happened — add skin strokes now)
# Character fills already issued inside char(). Add skin colour along arms on top.
out += [C('skin')]
for sh, hand, sign in ((sh_l, hand_l, -1), (sh_r, hand_r, +1)):
    mid = ((sh[0] + hand[0]) / 2 + sign * 16, (sh[1] + hand[1]) / 2 + 6)
    out.append(S(cr([sh, mid, (hand[0], hand[1] - 1)], 8), 0, 0.006))
    out.append(blob(hand[0], hand[1] + 2, 6.5, 4.5, 0, (1.0, 0.5)))
out += [P(0.45)]
MARK['peppa_end'] = len(out)
xs, ys = [], []
for o in out:
    if o['op'] == 'stroke':
        for p in o['pts']:
            # only peppa-ish region
            if RIM_Y - 220 < p[1] < RIM_Y + 20 and CX - 130 < p[0] < CX + 130:
                xs.append(p[0]); ys.append(p[1])
# tighter box from transformed original head+dress
def peppa_box():
    px, py = [], []
    for i, o in enumerate(ops[:45]):
        if i not in HEAD_DRESS or o['op'] != 'stroke':
            continue
        for p in o['pts']:
            q = T(p, PS, PX, PY)
            px.append(q[0]); py.append(q[1])
    return min(px), min(py), max(px), max(py)
body_l, head_top, body_r, body_bot = peppa_box()
print('peppa box', round(body_l), round(head_top), round(body_r), round(body_bot),
      'shoulders', sh_l, sh_r, 'hands', hand_l, hand_r)

# ---------- 3. Balloon envelope, cap, vertical seams ----------
out += [C('ink'), S(envelope, 0.12, 0.008)]
out += [S(throat_bar, 0.0, 0.008)]  # closes every vertical gore at the throat
out += [S(cap_line, 0.06, 0.008)]
# 5 interior seams for 6 stripes
SEAMS = [1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6]
for f in SEAMS:
    out.append(S(seam_pts(f), 0.08, 0.008))
out += [P(0.35)]
MARK['balloon_end'] = len(out)

# ---------- 4. Rigging ropes ----------
# attach under the throat lip to basket rim (corners + mid-sides)
attach = [
    (CX - TRX + 6, BBOT + 8),
    (CX - 18, BBOT + 12),
    (CX + 18, BBOT + 12),
    (CX + TRX - 6, BBOT + 8),
]
land = [
    (BL + 18, RIM_Y + 2),
    (CX - 40, RIM_Y - 1),
    (CX + 40, RIM_Y - 1),
    (BR - 18, RIM_Y + 2),
]
for a, b in zip(attach, land):
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 10)  # slight sag
    out.append(S(cr([a, mid, b], 8), 0.12, 0.008))
out += [P(0.3)]
MARK['ropes_end'] = len(out)

# ---------- 5. Sun + clouds ----------
SUNX, SUNY, SUNR = 128, 96, 44
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
CLOUDS = [(250, 52, 0.58), (1165, 78, 0.72), (1228, 300, 0.48)]
out += [cloud(*c) for c in CLOUDS]
out += [P(0.3)]
MARK['sky_end'] = len(out)

# ---------- 6. Tiny houses + trees + horizon + canvas border ----------
# houses: (cx, base_y, w, wall_h, roof_h, wall_color, roof_color)
HOUSES = [
    dict(cx=110, w=48, wall_h=34, roof_h=22, wall='wall', roof='orange'),
    dict(cx=250, w=42, wall_h=30, roof_h=20, wall='wall', roof='roof'),
    dict(cx=620, w=46, wall_h=32, roof_h=24, wall='wall', roof='dress'),
    dict(cx=820, w=40, wall_h=28, roof_h=18, wall='wall', roof='orange'),
    dict(cx=1120, w=50, wall_h=36, roof_h=24, wall='wall', roof='roof'),
]
# trees: pines and lollipops  (cx, base, kind, h)
TREES = [
    dict(cx=175, kind='pine', h=62),
    dict(cx=430, kind='lolli', h=58),
    dict(cx=960, kind='pine', h=66),
    dict(cx=1245, kind='lolli', h=54),
]

def house_geom(h):
    L, R = h['cx'] - h['w'] / 2, h['cx'] + h['w'] / 2
    base = GHY + 30
    top = base - h['wall_h']
    peak = top - h['roof_h']
    return L, R, base, top, peak

def add_house(h):
    L, R, base, top, peak = house_geom(h)
    body = poly([(L, top), (R, top), (R, base), (L, base)])
    roof = poly([(L - 5, top), (h['cx'], peak), (R + 5, top)])
    return [C('ink'), S(body, 0.04, 0.008), S(roof, 0.04, 0.008)]

def fat_rect(cx, y0, y1, w):
    """Solid small rectangle (concentric), used for tiny trunks that cannot be bucket-filled."""
    pts = []
    for f in (1.0, 0.65, 0.3):
        pts += poly([(cx - w * f, y0), (cx + w * f, y0), (cx + w * f, y1), (cx - w * f, y1)])
    return S(pts, 0, 0.005)

def add_tree(t):
    cx, base, h = t['cx'], GHY + 28, t['h']
    ops_ = []
    if t['kind'] == 'pine':
        ops_ += [C('trunk'), fat_rect(cx, base, base - 18, 8)]
        # stacked triangles, painted solid in dkgreen (too small to bucket reliably)
        ops_ += [C('dkgreen')]
        layers = [(base - 16, 26, 20), (base - 32, 22, 18), (base - 48, 17, 20)]
        for by, hw, hh in layers:
            pts = []
            for f in (1.0, 0.62, 0.28):
                pts += poly([(cx - hw * f, by), (cx, by - hh * f), (cx + hw * f, by)])
            ops_.append(S(pts, 0, 0.005))
    else:
        ops_ += [C('trunk'), fat_rect(cx, base, base - 20, 8)]
        cy, rx, ry = base - 20 - 18, 22, 20
        pts = []
        for k in range(56 + 3):
            a = 2 * math.pi * k / 56
            b = 1 + 0.12 * abs(math.sin(3.5 * a))
            pts.append((cx + rx * b * math.cos(a), cy + ry * b * math.sin(a)))
        ops_ += [C('ink'), S(pts, 0.06, 0.007)]
        t['crown'] = (cx, cy)  # seed later
    return ops_

for h in HOUSES:
    out += add_house(h)
for t in TREES:
    out += add_tree(t)
MARK['houses_end'] = len(out)

# object x-ranges at the horizon for gaps
def obj_gaps():
    gaps = []
    for h in HOUSES:
        L, R, base, top, peak = house_geom(h)
        # walls cross GHY; use wall sides (roof overhang is above)
        gaps.append((L - 1, R + 1))
    for t in TREES:
        gaps.append((t['cx'] - 10, t['cx'] + 10))
    gaps.sort()
    # merge
    m = []
    for a, b in gaps:
        if not m or a > m[-1][1] + 4:
            m.append([a, b])
        else:
            m[-1][1] = max(m[-1][1], b)
    return m

gaps = obj_gaps()
segs = []
cur = 2
for a, b in gaps:
    if a - cur > 8:
        segs.append((cur, a))
    cur = max(cur, b)
if 1358 - cur > 8:
    segs.append((cur, 1358))
print('GHY', GHY, 'horizon segs', [(round(a), round(b)) for a, b in segs], 'gaps', [(round(a), round(b)) for a, b in gaps])

out += [C('dkgreen')]
for a, b in segs:
    for dy in (0, 3, -2):
        out.append(S([(a, GHY + dy), (b, GHY + dy)], 0.05, 0.006))
# cap gap ends so preview doesn't leak
for a, b in gaps:
    out += [dot(a, GHY, 5), dot(b, GHY, 5)]
# canvas borders (ground box + sky box)
out += [S([(2, GHY - 2), (2, 787)], 0.05, 0.009), S([(5, GHY - 2), (5, 787)], 0.05, 0.009),
        S([(1358, GHY - 2), (1358, 787)], 0.05, 0.009), S([(1355, GHY - 2), (1355, 787)], 0.05, 0.009),
        S([(2, 787), (1358, 787)], 0.05, 0.009), S([(2, 784), (1358, 784)], 0.05, 0.009),
        S([(2, 2), (1358, 2)], 0.05, 0.01), S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [P(0.3)]
MARK['horizon_end'] = len(out)

# ---------- helpers for seed grids ----------
def in_sun(x, y): return (x - SUNX) ** 2 + (y - SUNY) ** 2 < (SUNR + 8) ** 2
def in_peppa(x, y):
    return body_l - 10 < x < body_r + 10 and head_top - 8 < y < max(body_bot, RIM_Y) + 10
def in_cloud(x, y):
    return any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS)
def in_balloon(x, y):
    if y < BTOP - 4 or y > BBOT + 16:
        return False
    if BTOP <= y <= BBOT:
        L, R = lr(y)
        return L - 8 <= x <= R + 8
    # lip bump
    return (x - CX) ** 2 / (TRX + 10) ** 2 + (y - BBOT) ** 2 / 18 ** 2 < 1
def in_basket(x, y):
    if y < RIM_Y - 10 or y > BASK_BOT + 10:
        return False
    t = (y - RIM_Y) / (BASK_BOT - RIM_Y)
    t = min(1, max(0, t))
    half = (BASK_TOP_W / 2) * (1 - t) + (BASK_BOT_W / 2) * t
    return abs(x - CX) <= half + 10
def in_house(x, y):
    for h in HOUSES:
        L, R, base, top, peak = house_geom(h)
        if L - 8 <= x <= R + 8 and peak - 4 <= y <= base + 4:
            return True
    return False
def in_tree(x, y):
    for t in TREES:
        if abs(x - t['cx']) < 28 and (GHY - t['h'] - 4) <= y <= (GHY + 32):
            return True
    return False

# ---------- 7. Object fills: stripes, cap, basket, houses, trees, sun ----------
# cap seed
cap_seed = (CX, (BTOP + CAP_Y) / 2 + 4)
# stripe seeds: mid-y of each gore, mid-x of the fraction band
stripe_seeds = []
mid_y = (CAP_Y + BBOT) / 2
for i in range(6):
    f0, f1 = i / 6, (i + 1) / 6
    fm = (f0 + f1) / 2
    # several seeds along the gore (top, mid, lower) in case of pinch
    seeds = []
    for ty in (CAP_Y + 18, mid_y, BBOT - 28):
        L, R = lr(ty)
        seeds.append((L + (R - L) * fm, ty))
    stripe_seeds.append((STRIPE[i], seeds))

out += [C('yellow'), F(cap_seed, (CX - 10, cap_seed[1] + 4), (CX + 10, cap_seed[1] + 4), (CX, CAP_Y - 8))]
MARK['cap_fill'] = len(out)
for col, seeds in stripe_seeds:
    out += [C(col), F(*seeds)]
MARK['stripe_fill'] = len(out)

# basket fill (avoid peppa body — seeds in side pockets and below dress)
bask_seeds = [
    (CX - 90, RIM_Y + 40), (CX + 90, RIM_Y + 40),
    (CX - 70, BASK_BOT - 30), (CX + 70, BASK_BOT - 30),
    (CX, BASK_BOT - 22),
    (BL + 30, RIM_Y + 28), (BR - 30, RIM_Y + 28),
    # slivers along the rim beside the dress hem and under the hands
    (CX - 40, RIM_Y + 8), (CX + 40, RIM_Y + 8),
    (CX - 70, RIM_Y + 6), (CX + 70, RIM_Y + 6),
    (CX + 55, RIM_Y + 10), (CX - 55, RIM_Y + 10),
    (744, RIM_Y + 6), (616, RIM_Y + 6),
]
out += [C('basket'), F(*bask_seeds)]
MARK['basket_fill'] = len(out)

# houses
for h in HOUSES:
    L, R, base, top, peak = house_geom(h)
    out += [C(h['wall']), F(((L + R) / 2, (top + base) / 2))]
    out += [C(h['roof']), F((h['cx'], (peak + top) / 2 + 2))]
MARK['house_fill'] = len(out)

# trees: pines already painted solid; bucket only the lollipop crowns
for t in TREES:
    if t['kind'] == 'lolli':
        cx, cy = t['cx'], GHY + 28 - 20 - 18
        out += [C('dkgreen'), F((cx, cy))]
MARK['tree_fill'] = len(out)

out += [C('sun'), F((SUNX, SUNY), (SUNX - 15, SUNY), (SUNX + 15, SUNY), (SUNX, SUNY - 15), (SUNX, SUNY + 15))]
out += [P(0.4)]
MARK['obj_fill_end'] = len(out)

# ---------- 8. Sky (skip clouds / balloon / peppa / basket / sun / houses/trees) then ground ----------
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_cloud(x, y) or in_sun(x, y) or in_balloon(x, y) or in_basket(x, y) or in_house(x, y) or in_tree(x, y):
            continue
        SKY.append((x, y))
# extra seeds near floating basket / peppa / balloon / horizon gaps
SKY += [
    (body_l - 18, head_top + 20), (body_r + 18, head_top + 20),
    (CX - 160, RIM_Y + 40), (CX + 160, RIM_Y + 40),
    (CX, BASK_BOT + 28), (CX - 80, BASK_BOT + 36), (CX + 80, BASK_BOT + 36),
    (CX - TRX - 24, BBOT + 8), (CX + TRX + 24, BBOT + 8),
    (40, GHY - 16), (1320, GHY - 16),
]
# closed pockets between the rigging ropes, Peppa and the basket rim
POCKETS = [
    (600, 400), (590, 450), (600, 500), (610, 530), (595, 360), (620, 380),
    (630, 500), (615, 460), (605, 420),
    (750, 380), (770, 410), (790, 450), (760, 500), (780, 530), (800, 400),
    (740, 360), (755, 440), (745, 520),
    (680, 330), (660, 340), (700, 340),  # just under the throat, between the ears and balloon
    (650, 550), (710, 550), (640, 520), (720, 520),
    (730, 540), (735, 500), (725, 560), (740, 530), (715, 545),
    (655, 540), (645, 560),
]
SKY += POCKETS
for a, b in segs:
    SKY.append(((a + b) / 2, GHY - 12))
SKY = [(x, y) for x, y in SKY if y < GHY - 6 and not (in_balloon(x, y) or in_basket(x, y) or in_peppa(x, y) or in_cloud(x, y) or in_sun(x, y) or in_house(x, y) or in_tree(x, y))]
# re-add rigging pockets (in_peppa uses a wide bbox that would drop them)
SKY += [s for s in POCKETS if not in_balloon(*s) and not in_basket(*s)]
out += [C('sky'), F(*SKY)]
MARK['sky_fill'] = len(out)

G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 28):
        if in_house(x, y) or in_tree(x, y):
            continue
        G.append((x, y))
# near houses/trees at ground
for h in HOUSES:
    L, R, base, top, peak = house_geom(h)
    G += [(L - 16, base + 8), (R + 16, base + 8), ((L + R) / 2, base + 18)]
for t in TREES:
    G += [(t['cx'] - 16, GHY + 30), (t['cx'] + 16, GHY + 30)]
out += [C('grass'), F(*G)]
MARK['grass_fill'] = len(out)
out += [P(0.35)]
MARK['fill_end'] = len(out)

# ---------- 9. Late details: weave, windows, flag, heart, shine, rays, birds, tufts ----------
# basket weave
out += [C('weave')]
for k in range(1, 6):
    t = k / 6
    x0 = BL + 16 + t * (BR - BL - 32)
    x1 = BLb + 14 + t * (BRb - BLb - 28)
    out.append(S([(x0, RIM_Y + 20), (x1, BASK_BOT - 10)], 0.1, 0.008))
for y in (RIM_Y + 36, RIM_Y + 62, RIM_Y + 86):
    f = (y - RIM_Y) / (BASK_BOT - RIM_Y)
    half = (BASK_TOP_W / 2) * (1 - f) + (BASK_BOT_W / 2) * f
    out.append(S([(CX - half + 16, y), (CX + half - 16, y)], 0.1, 0.008))
MARK['weave_end'] = len(out)

# windows painted solid (too small to bucket reliably; also avoids late-fill leaks)
for h in HOUSES:
    L, R, base, top, peak = house_geom(h)
    cy = (top + base) / 2 - 2
    for sx in (-9, 9) if h['w'] >= 44 else (0,):
        wx, wy = h['cx'] + sx, cy
        out += [C('ink'), S(poly([(wx - 5, wy - 5), (wx + 5, wy - 5), (wx + 5, wy + 5), (wx - 5, wy + 5)]), 0, 0.006)]
        out += [C('window'), blob(wx, wy, 3.5, 3.5, 0, (1.0, 0.55, 0.2))]
MARK['windows_end'] = len(out)

# flag on the very top (pole + triangular flag), painted after fills
FLAG_BASE = (CX + 6, BTOP + 4)
FLAG_TIP = (CX + 12, BTOP - 22)
out += [C('ink'), S([FLAG_BASE, FLAG_TIP], 0, 0.007)]
# triangular flag to the right, painted solid pink
flag = [(FLAG_TIP[0], FLAG_TIP[1] + 1), (FLAG_TIP[0] + 36, FLAG_TIP[1] + 10), (FLAG_TIP[0], FLAG_TIP[1] + 20)]
out += [S(poly(flag), 0, 0.006), C('pink')]
for f in (1.0, 0.7, 0.4, 0.15):
    mid = (FLAG_TIP[0] + 18 * f, FLAG_TIP[1] + 10)
    out.append(S(poly([
        (FLAG_TIP[0], FLAG_TIP[1] + 1 + 3*(1-f)),
        (FLAG_TIP[0] + 36 * f, FLAG_TIP[1] + 10),
        (FLAG_TIP[0], FLAG_TIP[1] + 20 - 3*(1-f)),
    ]), 0, 0.005))
MARK['flag_end'] = len(out)

# small heart on a mid-right stripe (after fills, on already-coloured balloon)
# right-of-center yellow/green area around frac 0.75, y around 150
Lh, Rh = lr(148)
# put it on the yellow gore (index 1, mid 1.5/6)
heart_x = Lh + (Rh - Lh) * (1.5 / 6)
def heart_pts(cx, cy, s=16):
    # classic heart parametric, closed
    pts = []
    for k in range(60 + 3):
        t = 2 * math.pi * k / 60
        x = s * 16 * math.sin(t) ** 3 / 16
        y = -s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16
        pts.append((cx + x, cy + y * 0.9))
    return pts
out += [C('ink'), S(heart_pts(heart_x, 148, 16), 0.02, 0.007), C('pink')]
for sc in (14, 10, 6, 3):
    out.append(S(heart_pts(heart_x, 148, sc), 0, 0.005))
MARK['heart_end'] = len(out)

# shine highlights on balloon (white dots / small crescents) after fills
out += [C('white')]
for (sx, sy, r) in [(CX - 90, 110, 7), (CX - 70, 175, 5), (CX + 40, 100, 4)]:
    if in_balloon(sx, sy):
        out.append(dot(sx, sy, r))
MARK['shine_end'] = len(out)

# sun rays
out += [C('sun')]
for ang in range(0, 360, 30):
    a = math.radians(ang)
    p0 = (SUNX + (SUNR + 8) * math.cos(a), SUNY + (SUNR + 8) * math.sin(a))
    p1 = (SUNX + (SUNR + 26) * math.cos(a), SUNY + (SUNR + 26) * math.sin(a))
    if in_cloud(*p1) or in_balloon(*p1):
        continue
    out.append(S([p0, p1], 0.1, 0.008))
MARK['rays_end'] = len(out)

# tufts on the ground strip
out += [C('dkgreen')]
TUFT = [(40, GHY + 40), (70, 760), (330, 750), (500, 735), (700, 770), (900, 748),
        (1040, 765), (1300, 740), (1340, GHY + 36), (560, 755), (200, 770)]
for x, y in TUFT:
    if in_house(x, y) or in_tree(x, y):
        continue
    for dx in (-8, 0, 8):
        out.append(S([(x, y + 12), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)

# birds (M-shape) after fills, in open sky
out += [C('ink')]
for x, y in [(400, 70), (980, 250), (1080, 50), (200, 250)]:
    if in_balloon(x, y) or in_cloud(x, y) or in_sun(x, y):
        continue
    out.append(S(cr([(x - 14, y), (x - 7, y - 6), (x, y), (x + 7, y - 6), (x + 14, y)], 5), 0, 0.008))
MARK['end'] = len(out)

# ---------- seed check (PIL simulation) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
LATE = set()
PROTECTED = {'skin', 'dress', 'cheek', 'yellow', 'blue', 'green', 'orange', 'pink',
             'basket', 'sun', 'wall', 'roof', 'dkgreen', 'trunk', 'window'}

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
            for r in range(0, 14):
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        x, y = x0 + dx, y0 + dy
                        if not (3 <= x < 1357 and 3 <= y < 787) or ok is not None:
                            continue
                        colors = im.crop((x - 3, y - 3, x + 4, y + 4)).getcolors(500) or []
                        pix = im.getpixel((x, y))
                        if len(colors) == 1 and (pix == (255, 255, 255) or (o_c in LATE and pix not in (col['ink'], cc))):
                            ok = (x, y)
                    if ok:
                        break
                if ok:
                    break
            if ok:
                if o_c in PROTECTED:
                    probe = im.copy(); ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc) - sum(1 for p in im.getdata() if p == cc)
                    lim = 80000 if o_c in ('yellow', 'dress', 'green', 'blue', 'orange', 'pink', 'basket') else 40000
                    if o_c == 'dress':
                        # dress is both Peppa's dress (~few k) and a stripe / heart
                        lim = 80000
                    if probe.getpixel(CORNER) != im.getpixel(CORNER) or filled > lim:
                        print('reject leak seed', o_c, ok, 'filled', filled)
                        continue
                ImageDraw.floodfill(im, ok, cc); keep.append(list(ok))
            else:
                print('drop seed', o_c, s)
        if not keep:
            im.save('./preview_fail.png')
            raise SystemExit('no seeds kept: ' + str(o_c))
        o['seeds'] = keep

im.save('./preview.png')
cnt = Counter(im.getdata())
print('white px left', cnt[(255, 255, 255)])
print('top', cnt.most_common(16))

# assertions
assert im.getpixel((20, 200)) == col['sky'], im.getpixel((20, 200))
assert im.getpixel((80, 770)) == col['grass'], im.getpixel((80, 770))
assert im.getpixel((600, 500)) == col['sky'], ('left rigging pocket', im.getpixel((600, 500)))
assert im.getpixel((770, 450)) == col['sky'], ('right rigging pocket', im.getpixel((770, 450)))
assert im.getpixel((740, 520)) == col['sky'], ('right dress/arm pocket', im.getpixel((740, 520)))
# yellow stripe must stay yellow (heart must not flood it)
L, R = lr(mid_y)
qx, qy = int(L + (R - L) * (1.5 / 6)), int(mid_y)
assert im.getpixel((qx, qy)) == col['yellow'], ('yellow stripe flooded', im.getpixel((qx, qy)), qx, qy)
assert im.getpixel((SUNX, SUNY)) == col['sun']
# balloon cap yellow
assert im.getpixel((CX, int(cap_seed[1]))) == col['yellow'], im.getpixel((CX, int(cap_seed[1])))
# a mid stripe
L, R = lr(mid_y)
# stripe 0 (red/dress) near left
sx = int(L + (R - L) * (0.5 / 6)); sy = int(mid_y)
assert im.getpixel((sx, sy)) == col['dress'], ('stripe0', im.getpixel((sx, sy)), sx, sy)
sx = int(L + (R - L) * (3.5 / 6))
assert im.getpixel((sx, sy)) == col['blue'], ('stripe3', im.getpixel((sx, sy)), sx, sy)
# basket
assert im.getpixel((580, 598)) == col['basket'], im.getpixel((580, 598))
# peppa dress
dx, dy = map(int, T((469.6, 457.6), PS, PX, PY))
assert im.getpixel((dx, dy)) == col['dress'], ('peppa dress', im.getpixel((dx, dy)), dx, dy)
# peppa skin (forehead, above the blush)
assert im.getpixel((660, 400)) == col['skin'], ('skin', im.getpixel((660, 400)))
# a house wall (offset so we don't land on a window)
L, R, base, top, peak = house_geom(HOUSES[0])
assert im.getpixel((int((L + R) / 2), int(base - 6))) == col['wall'], im.getpixel((int((L + R) / 2), int(base - 6)))
# clouds stay white-ish (outline may be ink; interior white)
cx, cy, sc = CLOUDS[0]
assert im.getpixel((int(cx), int(cy))) == (255, 255, 255), im.getpixel((int(cx), int(cy)))

def est(ops_):
    t = 0
    for o in ops_:
        if o['op'] == 'stroke':
            n = 1
            for p, q in zip(o['pts'], o['pts'][1:]):
                n += max(1, int(math.dist(p, q) / 4))
            t += 0.3 + n * (o.get('dl', 0.009) + 0.0021)
        elif o['op'] == 'fill':
            t += 0.72 * len(o['seeds']) + 0.5
        elif o['op'] == 'color':
            t += 0.6
        elif o['op'] == 'pause':
            t += o['s']
    return t
print('estimate s', round(est(out), 1))
D = {
    'name': 'peppa-balloon',
    'canvas': [1360, 790],
    'palette': pal,
    'ops': out,
    'ui': E['ui'],
    'marks': MARK,
    'notes': 'Peppa riding a rainbow-striped hot-air balloon: Peppa (red dress) stands in the wicker basket with hands on the rim; large vertically striped balloon (red/yellow/green/blue/orange/pink) with yellow cap, rigging ropes, flag and heart; sun, white clouds, birds; thin ground strip with tiny houses and trees. Object fills before sky/ground; late details after.',
}
json.dump(D, open('./peppa_balloon_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa22\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa22.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
import shutil
shutil.copy('./peppa_balloon_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
