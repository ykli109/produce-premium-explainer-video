#!/usr/bin/env python3
"""Peppa watering flowers in the garden (drawing-peppa-pig-20).
Peppa (red dress) holds a blue watering can (side handle, long spout + rose),
water drops arc onto a soil flower bed with tulips and tall sunflowers,
butterfly, sun, clouds, grass. Big flats = paint bucket; flowers/drops are
painted AFTER sky/grass fills so no stem breaks the sky/grass seal."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(20)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = [dict(o) for o in E['ops']]
# right arm pointing DOWN-right (holding the can): reflect arm strokes about y=410.8
REF = 821.6
for i in (16, 17, 18, 21, 22, 35):
    ops[i] = dict(ops[i]); ops[i]['pts'] = [[p[0], round(REF - p[1], 1)] for p in ops[i]['pts']]
out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['soil', [150, 95, 55]], ['soil2', [105, 62, 35]],
 ['can', [60, 130, 215]], ['water', [95, 175, 235]], ['seed', [120, 72, 30]],
 ['tulip', [235, 60, 70]], ['pink', [255, 130, 190]], ['purple', [165, 100, 215]],
 ['orange', [255, 160, 50]], ['cloud', [255, 255, 255]],
]
pal = pal[:19]
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
def ell(cx, cy, rx, ry, n=72, extra=4, rot=0):
    ca, sa = math.cos(rot), math.sin(rot)
    r = []
    for k in range(n + extra):
        a = 2 * math.pi * k / n; x, y = rx * math.cos(a), ry * math.sin(a)
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

# ---------- 1. Peppa ----------
PS, PX, PY = 0.62, 95, 100
out += char(PS, PX, PY)
out += [P(0.5)]
xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r, head_top, body_bot = min(xs), max(xs), min(ys), max(ys)
H = T((648, 452), PS, PX, PY)
print('peppa box', round(body_l), round(head_top), round(body_r), round(body_bot), 'hand', H)
MARK = {}
MARK['peppa_end'] = len(out)

# ---------- 2. Watering can (closed, bucket filled) ----------
CL = H[0] + 26; CT = H[1] - 38; CW_, CH_ = 112, 84
CR, CB = CL + CW_, CT + CH_
body = [(CL + 6, CT), (CR - 6, CT), (CR, CB), (CL, CB)]
out += [C('ink'), S(poly(body), 0.05, 0.009)]
# back handle loop (hand grips it)
hand_loop = cr([(CL + 3, CT + 10), (CL - 22, CT + 14), (H[0] - 2, H[1] + 2), (CL - 22, CT + 62), (CL + 2, CT + 66)], 8)
inner_loop = cr([(CL + 3, CT + 22), (CL - 10, CT + 26), (H[0] + 12, H[1] + 4), (CL - 10, CT + 50), (CL + 2, CT + 54)], 8)
out += [S(hand_loop, 0.05, 0.009), S(inner_loop, 0.05, 0.009)]
# spout: thin tube from upper-right of body up to the rose
SB = (CR - 4, CT + 30); ST = (CR + 92, CT - 46)
ang = math.atan2(ST[1] - SB[1], ST[0] - SB[0]); nx, ny = -math.sin(ang), math.cos(ang)
w0, w1 = 13, 8
spout = [(SB[0] + nx * w0, SB[1] + ny * w0), (ST[0] + nx * w1, ST[1] + ny * w1),
         (ST[0] - nx * w1, ST[1] - ny * w1), (SB[0] - nx * w0 + 2, SB[1] - ny * w0)]
out += [S(poly(spout), 0.05, 0.008)]
ROSE = (ST[0] + 14 * math.cos(ang), ST[1] + 14 * math.sin(ang))
out += [S(ell(ROSE[0], ROSE[1], 11, 20, 40, 4, ang), 0.03, 0.007)]
# top lid
out += [S(cr([(CL + 20, CT + 2), (CL + 40, CT - 12), (CL + 70, CT - 12), (CL + 92, CT + 2)], 8), 0.05, 0.008)]
out += [P(0.3)]
out += [C('can'), F((CL + CW_ / 2, CT + CH_ / 2), (CL + 30, CB - 15), (CR - 25, CT + 20),
                   ((SB[0] + ST[0]) / 2, (SB[1] + ST[1]) / 2), (CL + 56, CT - 5))]
out += [C('water'), F(ROSE)]
# can decoration: white stripe + a tiny flower sticker
out += [C('white'), S([(CL + 16, CT + 26), (CR - 16, CT + 26)], 0.0, 0.007),
        S([(CL + 16, CT + 30), (CR - 16, CT + 30)], 0.0, 0.007)]
out += [C('sun'), dot(CL + CW_ / 2, CT + 56, 7)]
out += [P(0.3)]
MARK['can_end'] = len(out)

# ---------- 3. Soil flower bed (closed, bucket filled) ----------
BX, BY, BRX, BRY = 925, 650, 360, 82
out += [C('ink'), S(ell(BX, BY, BRX, BRY, 120, 4), 0.1, 0.009)]
out += [C('soil'), F((BX, BY), (BX - 200, BY), (BX + 200, BY), (BX, BY + 40), (BX, BY - 40))]
out += [C('soil2')]
for dx, dy in [(-260, -10), (-150, 30), (-40, -30), (60, 20), (170, -20), (260, 15), (-210, 45), (110, 50)]:
    out.append(S(cr([(BX + dx - 22, BY + dy), (BX + dx, BY + dy - 6), (BX + dx + 22, BY + dy)], 5), 0.1, 0.008))
out += [P(0.3)]
MARK['bed_end'] = len(out)

# ---------- 4. Sun + clouds ----------
SUNX, SUNY, SUNR = 1235, 92, 50
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
CLOUDS = [(470, 72, 0.85), (760, 112, 0.75), (1000, 62, 0.8)]
out += [cloud(*c) for c in CLOUDS]
out += [P(0.3)]
MARK['sky_end'] = len(out)

# ---------- 5. Horizon (stops at the dress and at the can) ----------
GHY = int(T((469, 480), PS, PX, PY)[1])
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
assert CT + 8 < GHY < CB - 8, (CT, GHY, CB)
canL, canR = CL - 3, CR + 2   # body edges (slight taper) at GHY
fr = (GHY - CT) / CH_
canL = CL + 6 * (1 - fr) + 3; canR = CR - 6 * (1 - fr) - 3
print('GHY', GHY, 'dress gap', pl[0], pr[0], 'can', canL, canR)
out += [C('dkgreen')]
segs = [(2, pl[0]), (pr[0], canL), (canR, 1358)]
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
def in_can(x, y): return CL - 40 < x < ROSE[0] + 30 and ROSE[1] - 30 < y < CB + 10
def in_bed(x, y): return ((x - BX) / (BRX + 12)) ** 2 + ((y - BY) / (BRY + 12)) ** 2 < 1
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_cloud(x, y): return any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS)

# ---------- 6. Bucket fills: sky, grass, sun ----------
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_cloud(x, y) or in_sun(x, y) or in_can(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (pr[0] + 14, GHY - 12), (canR + 20, GHY - 12), (canL - 8, GHY - 12),
        (body_l - 20, GHY - 14), (H[0] + 8, H[1] - 20), (ROSE[0] + 30, ROSE[1] + 30)]
SKY = [(x, y) for x, y in SKY if y < GHY - 7]
out += [C('sky'), F(*SKY)]
G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if in_peppa(x, y) or in_bed(x, y) or in_can(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), (canL - 8, GHY + 12),
      (canR + 20, GHY + 14), ((pr[0] + canL) / 2, GHY + 14), (body_l + 30, body_bot + 25),
      ((body_l + body_r) / 2, body_bot - 30), (CL + 50, CB + 25), (H[0] - 4, H[1] + 40)]
out += [C('grass'), F(*G)]
out += [C('sun'), F((SUNX, SUNY), (SUNX - 15, SUNY), (SUNX + 15, SUNY), (SUNX, SUNY - 15), (SUNX, SUNY + 15))]
out += [P(0.4)]
MARK['fill_end'] = len(out)

# ---------- 7. Flowers in the bed (painted after fills) ----------
TULIPS = [(660, 520, 'tulip'), (760, 560, 'pink'), (860, 515, 'purple'), (720, 470, 'tulip')]
SUNF = [(990, 360, 44, 600), (1120, 300, 50, 640), (1245, 380, 40, 615)]
# stems + leaves
out += [C('dkgreen')]
STEM_B = {}
for x, y, c in TULIPS:
    by = BY + random.uniform(-20, 20)
    out.append(S(cr([(x, by), (x + 4, (y + by) / 2), (x, y + 14)], 8), 0.3, 0.009))
    out.append(S(cr([(x, by), (x + 4, (y + by) / 2), (x, y + 14)], 8), 0.3, 0.009))
    out.append(blob(x + 20, (y + by) / 2 + 20, 20, 7, -0.6, (1.0, .6, .3)))
for x, y, r, by in SUNF:
    for dx in (-3, 0, 3):
        out.append(S(cr([(x + dx, by), (x + dx - 6, (y + by) / 2), (x + dx, y + r)], 8), 0.3, 0.009))
    out.append(blob(x - 26, (y + by) / 2 + 30, 26, 9, 0.5, (1.0, .6, .3)))
    out.append(blob(x + 26, (y + by) / 2 - 10, 26, 9, -0.5, (1.0, .6, .3)))
out += [P(0.3)]
MARK['stems_end'] = len(out)
# tulip cups
for x, y, c in TULIPS:
    cup = [(x - 26, y - 22), (x - 14, y - 6), (x, y - 22), (x + 14, y - 6), (x + 26, y - 22),
           (x + 24, y + 4), (x + 12, y + 16), (x - 12, y + 16), (x - 24, y + 4), (x - 26, y - 22)]
    out += [C('ink'), S(cup + [cup[1]], 0.0, 0.008), C(c), F((x, y + 4))]
out += [P(0.3)]
MARK['tulips_end'] = len(out)
# sunflowers: petals ring + seed centre
for x, y, r, by in SUNF:
    out += [C('orange')]
    n = 10
    for k in range(n):
        a = 2 * math.pi * k / n
        out.append(blob(x + (r + 4) * math.cos(a), y + (r + 4) * math.sin(a), r * 0.44, r * 0.21, a, (1.0, .5)))
    out += [C('sun')]
    for k in range(n):
        a = 2 * math.pi * (k + .5) / n
        out.append(blob(x + (r + 1) * math.cos(a), y + (r + 1) * math.sin(a), r * 0.4, r * 0.19, a, (1.0, .45)))
    out += [C('seed'), dot(x, y, r * 0.62)]
    out += [C('soil2')] + [dot(x + r * .3 * math.cos(a), y + r * .3 * math.sin(a), 2.5) for a in [0, 1.6, 3.2, 4.7]]
out += [P(0.3)]
MARK['sunflowers_end'] = len(out)

# ---------- 8. Water drops from the rose to the tulips ----------
out += [C('water')]
DROPS = []
for i in range(5):
    sx = ROSE[0] + 10; sy = ROSE[1] + (i - 2) * 6
    tx = 640 + i * 35; ty = 470 + i * 4
    for j, t in enumerate((0.2, 0.45, 0.7, 0.9)):
        x = sx + (tx - sx) * t; y = sy + (ty - sy) * t - 50 * math.sin(math.pi * t) * (1 - t)
        DROPS.append((x, y))
        out.append(S(poly([(x, y - 9), (x + 5, y + 2), (x, y + 6), (x - 5, y + 2)]), 0.0, 0.006))
        out.append(S(ell(x, y + 1, 2.5, 3, 12, 1), 0, 0.006))
out += [C('white')] + [S([(x - 1, y - 3), (x - 1, y)], 0, 0.006) for x, y in DROPS[::2]]
out += [P(0.3)]
MARK['water_end'] = len(out)

# ---------- 9. Butterfly ----------
BFX, BFY = 1100, 175
out += [C('ink'), S([(BFX, BFY - 18), (BFX, BFY + 18)], 0.0, 0.008),
        S(cr([(BFX - 2, BFY - 18), (BFX - 10, BFY - 32)], 4), 0, 0.008),
        S(cr([(BFX + 2, BFY - 18), (BFX + 10, BFY - 32)], 4), 0, 0.008)]
out += [C('orange'), blob(BFX - 22, BFY - 10, 22, 16, -0.3), blob(BFX + 22, BFY - 10, 22, 16, 0.3),
        C('pink'), blob(BFX - 16, BFY + 14, 13, 10, 0.4), blob(BFX + 16, BFY + 14, 13, 10, -0.4),
        C('white'), dot(BFX - 24, BFY - 12, 4), dot(BFX + 24, BFY - 12, 4)]
out += [P(0.3)]
MARK['butterfly_end'] = len(out)

# ---------- 10. Details: sun rays, grass tufts, little flowers, birds ----------
out += [C('sun')]
for ang in range(0, 360, 30):
    a = math.radians(ang)
    out.append(S([(SUNX + (SUNR + 8) * math.cos(a), SUNY + (SUNR + 8) * math.sin(a)),
                  (SUNX + (SUNR + 28) * math.cos(a), SUNY + (SUNR + 28) * math.sin(a))], 0.1, 0.008))
MARK['rays_end'] = len(out)
out += [C('dkgreen')]
for x, y in [(45, GHY + 50), (150, GHY + 90), (60, 700), (200, 740), (330, 760), (480, 750),
             (560, 470), (420, 520), (1320, 480), (1200, 760), (1320, 740), (700, 770), (1000, 770), (140, 600)]:
    if in_peppa(x, y) or in_bed(x, y) or in_can(x, y): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)
for (x, y, fc) in [(80, GHY + 40, 'pink'), (250, 700, 'orange'), (440, 735, 'purple'), (520, 560, 'pink'),
                   (1300, 520, 'orange'), (130, 760, 'pink')]:
    if in_peppa(x, y) or in_bed(x, y) or in_can(x, y): continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]
out += [C('ink')]
for x, y in [(620, 60), (880, 40), (560, 200)]:
    out.append(S(cr([(x - 14, y), (x - 7, y - 6), (x, y), (x + 7, y - 6), (x + 14, y)], 5), 0, 0.008))
MARK['end'] = len(out)

# ---------- seed check (PIL simulation) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
LATE = {'tulip', 'pink', 'purple'}
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'can', 'water', 'soil', 'tulip', 'pink', 'purple', 'sun'}
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
                        if len(colors) == 1 and (im.getpixel((x, y)) == (255, 255, 255) or (o_c in LATE and im.getpixel((x, y)) != col['ink'])): ok = (x, y)
                if ok: break
            if ok:
                if o_c in PROTECTED:
                    probe = im.copy(); ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc) - sum(1 for p in im.getdata() if p == cc)
                    lim = 250000 if o_c == 'soil' else 60000
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
print('top', cnt.most_common(12))
assert im.getpixel((10, 200)) == col['sky'], im.getpixel((10, 200))
assert im.getpixel((50, 760)) == col['grass'], im.getpixel((50, 760))
assert cnt[col['sky']] > 150000 and cnt[col['grass']] > 120000, (cnt[col['sky']], cnt[col['grass']])
assert im.getpixel((int(BX), int(BY + 60))) == col['soil'], im.getpixel((int(BX), int(BY + 60)))
assert im.getpixel((int(CL + 30), int(CB - 12))) == col['can'], im.getpixel((int(CL + 30), int(CB - 12)))

# rough duration estimate (calibrated against pig-19: see est.py)
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
D = {'name': 'peppa-garden', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa watering flowers: red dress, blue watering can (side handle, spout, rose), water drops, soil bed with tulips and sunflowers, butterfly, sun, clouds, grass. Horizon gaps at dress and can.'}
json.dump(D, open('./peppa_garden_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa20\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa20.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_garden_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
