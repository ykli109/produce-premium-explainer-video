#!/usr/bin/env python3
"""Peppa blowing soap bubbles outdoors (drawing-peppa-pig-19).
Outdoor grass, red dress, bubble wand, soap bubbles of several sizes,
soap bottle, sun + clouds + flowers. Large flats use paint-bucket;
bubbles/props use concentric strokes so sky fill stays clean."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(19)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['wood', [160, 100, 55]], ['wood2', [120, 70, 40]],
 ['soap', [90, 170, 220]],   # soap liquid cyan-blue
 ['bubble', [180, 230, 255]], # pale bubble tint
 ['bottle', [255, 150, 80]],  # orange soap bottle
 ['cap', [70, 140, 200]],     # bottle cap
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
def cloud(cx, cy, sc):
    P = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        P.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(P + P[:3], 0.1, 0.008)

# ---- Peppa left-center ----
PS, PX, PY = 0.60, 120, 95
out += char(PS, PX, PY, 'dress')
out += [{'op': 'pause', 's': 0.4}]

xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r = min(xs), max(xs)
head_top, body_bot = min(ys), max(ys)
print('peppa box', round(body_l), round(head_top), round(body_r), round(body_bot))
LH = T((320, 400), PS, PX, PY)
RH = T((620, 400), PS, PX, PY)
print('hands', LH, RH)

# ---- Bubble wand (plastic stick + ring) from right hand ----
GRIP = (RH[0] - 4, RH[1] + 6)
TIP = (620, 160)  # ring center up-right of Peppa
# stick
out += [C('wood')] + rod_strokes(GRIP, (TIP[0] - 10, TIP[1] + 55), 5, 6)
out += [C('wood2')] + rod_strokes(GRIP, (TIP[0] - 10, TIP[1] + 55), 2, 3)
# ring (wand head) — double ink + pale soap film concentric
RING_R = 38
out += [C('ink')]
for f in (1.0, 0.92):
    out.append(S(ell(TIP[0], TIP[1], RING_R * f, RING_R * f, 56, 4), 0.05, 0.007))
# connector from stick to ring
out += [C('wood')] + rod_strokes((TIP[0] - 10, TIP[1] + 55), (TIP[0], TIP[1] + RING_R - 2), 4, 4)
# soap film inside ring (concentric pale)
out += [C('bubble')]
for f in (0.85, 0.65, 0.45, 0.25):
    out.append(S(ell(TIP[0], TIP[1], RING_R * f, RING_R * f, 40, 2), 0.0, 0.005))
out += [C('white'),
        S(cr([(TIP[0] - 12, TIP[1] - 10), (TIP[0] - 4, TIP[1] - 16), (TIP[0] + 4, TIP[1] - 12)], 5), 0, 0.006)]
out += [{'op': 'pause', 's': 0.3}]

# ---- Soap bottle / bucket near feet (right of Peppa) ----
BX, BY = body_r + 95, body_bot - 10  # bottle center
BRX, BRY = 32, 48
# bottle body outline
out += [C('ink')]
bot = [(BX - BRX, BY - BRY + 12), (BX - BRX + 4, BY + BRY),
       (BX + BRX - 4, BY + BRY), (BX + BRX, BY - BRY + 12),
       (BX + 14, BY - BRY - 8), (BX - 14, BY - BRY - 8)]
out.append(S(poly(bot), 0.05, 0.008))
# neck
out.append(S(poly([(BX - 10, BY - BRY - 8), (BX - 10, BY - BRY - 28),
                   (BX + 10, BY - BRY - 28), (BX + 10, BY - BRY - 8)]), 0.05, 0.008))
# fill bottle orange concentric-ish via bucket after seal; also paint concentric
out += [C('bottle')]
for f in (1.0, 0.8, 0.6, 0.4, 0.2):
    out.append(S(ell(BX, BY + 4, BRX * 0.85 * f, BRY * 0.85 * f, 36, 2), 0.0, 0.005))
out += [C('soap')]
for f in (0.7, 0.5, 0.3):
    out.append(S(ell(BX, BY + 10, BRX * 0.6 * f, BRY * 0.45 * f, 28, 2), 0.0, 0.005))
out += [C('cap')]
for f in (1.0, 0.6, 0.3):
    out.append(S(ell(BX, BY - BRY - 30, 12 * f, 8 * f, 24, 1), 0.0, 0.005))
# label squiggle
out += [C('white'),
        S(cr([(BX - 12, BY - 5), (BX - 2, BY - 12), (BX + 8, BY - 4), (BX + 14, BY - 10)], 6), 0, 0.006)]
# small bucket/dish of soap solution next to bottle
DX, DY = BX + 70, BY + 30
out += [C('ink'), S(ell(DX, DY, 36, 16, 48, 4), 0.05, 0.008)]
out += [C('soap')]
for f in (1.0, 0.7, 0.4):
    out.append(S(ell(DX, DY, 30 * f, 12 * f, 32, 2), 0.0, 0.005))
out += [C('white'),
        S(cr([(DX - 14, DY - 4), (DX - 4, DY - 8), (DX + 6, DY - 3)], 4), 0, 0.006)]
out += [{'op': 'pause', 's': 0.3}]

# ---- Floating soap bubbles (painted AFTER sky fill as concentric strokes) ----
# Keep every bubble fully above horizon so sky/grass seal never breaks.
BUBBLES = [
    (520, 120, 50), (700, 175, 38), (880, 130, 62), (1040, 195, 32),
    (760, 250, 40), (960, 250, 26), (600, 240, 20), (1160, 240, 34),
    (440, 185, 16), (840, 75, 22), (1080, 115, 18), (1260, 180, 28),
    (680, 95, 14), (920, 210, 18), (500, 250, 24),
]
# outlines deferred — drawn with fills after sky

# ---- Sun + clouds ----
SUNX, SUNY, SUNR = 1180, 85, 48
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
CLOUDS = [(380, 70, 0.9), (650, 100, 0.75), (920, 55, 0.7)]
out += [cloud(*c) for c in CLOUDS]
out += [{'op': 'pause', 's': 0.25}]

# ---- Horizon ----
dress_mid_y = T((469, 480), PS, PX, PY)[1]
GHY = int(dress_mid_y)
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
print('GHY', GHY, 'gap', round(pl[0],1), round(pr[0],1))
out += [C('dkgreen')]
segs = [(2, pl[0]), (pr[0], 1358)]
for a, b in segs:
    if b - a > 8:
        out.append(S([(a, GHY), (b, GHY)], 0.05, 0.009))
        out.append(S([(a, GHY + 3), (b, GHY + 3)], 0.05, 0.009))
        out.append(S([(a, GHY - 2), (b, GHY - 2)], 0.05, 0.009))
out += [S([(2, GHY - 2), (2, 787)], 0.05, 0.009),
        S([(5, GHY - 2), (5, 787)], 0.05, 0.009),
        S([(1358, GHY - 2), (1358, 787)], 0.05, 0.009),
        S([(1355, GHY - 2), (1355, 787)], 0.05, 0.009),
        S([(2, 787), (1358, 787)], 0.05, 0.009),
        S([(2, 784), (1358, 784)], 0.05, 0.009),
        S([(2, 2), (1358, 2)], 0.05, 0.01),
        S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
# seal dress gap ends
out += [dot(pl[0], GHY, 6), dot(pr[0], GHY, 6)]
out += [{'op': 'pause', 's': 0.3}]

def in_bubble(x, y, pad=4):
    for cx, cy, r in BUBBLES:
        if (x - cx) ** 2 + (y - cy) ** 2 < (r + pad) ** 2:
            return True
    return False

def in_sun(x, y):
    return (x - SUNX) ** 2 + (y - SUNY) ** 2 < (SUNR + 6) ** 2

def in_bottle(x, y):
    return abs(x - BX) < BRX + 8 and BY - BRY - 35 < y < BY + BRY + 4

def in_dish(x, y):
    return ((x - DX) / 40) ** 2 + ((y - DY) / 20) ** 2 < 1.0

def near_wand(x, y):
    # stick segment + ring
    if (x - TIP[0]) ** 2 + (y - TIP[1]) ** 2 < (RING_R + 8) ** 2:
        return True
    # rough stick AABB
    ax, ay = GRIP; bx, by = TIP[0] - 10, TIP[1] + 55
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
    px, py = ax + t * dx, ay + t * dy
    return (x - px) ** 2 + (y - py) ** 2 < 18 ** 2

# ---- Bucket fills: sky then grass ----
# Bubbles are closed outlines — leave white inside for later bubble tint;
# sky seeds must NOT land inside bubbles/sun/clouds/wand/Peppa.
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 16, 32):
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < GHY + 4:
            continue
        if any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS):
            continue
        if in_sun(x, y) or near_wand(x, y):
            continue
        SKY.append((x, y))
SKY += [(40, 180), (40, 280), (200, 40), (300, 200),
        (500, 40), (600, 200), (800, 40), (1000, 40), (1300, 160),
        (200, 320), (body_r + 50, 160), (body_r + 80, 260),
        (body_l - 30, 200), (400, GHY - 30), (70, GHY - 30),
        (200, GHY - 40), (300, 250), (50, 100), (150, 150), (480, 160),
        (1100, 200), (1250, 280), (900, 180), (700, 50)]
SKY = [(x, y) for x, y in SKY if y < GHY - 8]
# densify between bubbles
for x in range(40, 1360, 70):
    for y in range(40, GHY - 20, 50):
        if in_sun(x, y) or near_wand(x, y):
            continue
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < GHY + 4:
            continue
        if any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS):
            continue
        SKY.append((x, y))
out += [C('sky'), F(*SKY)]

G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if body_l - 8 < x < body_r + 8 and head_top - 4 < y < body_bot + 8:
            continue
        if in_bottle(x, y) or in_dish(x, y):
            continue
        G.append((x, y))
G += [(40, 560), (80, 620), (120, 700), (200, 730), (300, 750),
      (420, 740), (480, 760), (650, 750), (750, 720), (900, 760),
      (1100, 740), (1280, 700), (1320, 640), (1300, 750), (50, 760),
      (250, 600), (body_l - 25, body_bot - 10), (body_r + 25, body_bot - 10),
      (body_l - 15, body_bot + 20), (body_r + 15, body_bot + 20),
      (body_l + 20, body_bot + 30), (100, 580), (380, 700),
      (600, 720), (800, 700), (1000, 720), (1200, 740)]
out += [C('grass'), F(*G)]

# Sun fill
out += [C('sun'), F((SUNX, SUNY), (SUNX - 14, SUNY), (SUNX + 14, SUNY),
                    (SUNX, SUNY - 14), (SUNX, SUNY + 14))]
out += [{'op': 'pause', 's': 0.35}]

# ---- Bubble interiors + highlights (on top of sky) ----
out += [C('bubble')]
for cx, cy, r in BUBBLES:
    for f in (0.9, 0.7, 0.5, 0.3, 0.12):
        out.append(S(ell(cx, cy, r * f, r * f, 36, 2), 0.0, 0.005))
out += [C('white')]
for cx, cy, r in BUBBLES:
    # highlight arc top-left
    hx, hy = cx - r * 0.35, cy - r * 0.35
    out.append(S(cr([(hx - r * 0.2, hy), (hx - r * 0.05, hy - r * 0.15),
                     (hx + r * 0.15, hy - r * 0.05)], 5), 0, 0.005))
    if r > 30:
        out.append(dot(cx + r * 0.25, cy + r * 0.2, max(2, r * 0.08)))
# re-ink bubble outlines so they stay crisp
out += [C('ink')]
for cx, cy, r in BUBBLES:
    out.append(S(ell(cx, cy, r, r, 48, 3), 0.0, 0.006))

# ---- Details: sun rays, grass tufts, flowers ----
out += [C('sun')]
for ang in range(0, 360, 30):
    a = math.radians(ang)
    out.append(S([(SUNX + (SUNR + 8) * math.cos(a), SUNY + (SUNR + 8) * math.sin(a)),
                  (SUNX + (SUNR + 28) * math.cos(a), SUNY + (SUNR + 28) * math.sin(a))], 0.1, 0.008))

out += [C('dkgreen')]
for x, y in [(50, GHY + 50), (140, GHY + 70), (280, 730), (420, 750),
             (650, 760), (780, 740), (980, 755), (1180, 720),
             (1320, 745), (90, 660), (200, 690), (480, 710),
             (50, 590), (850, 700), (1100, 690)]:
    if body_l < x < body_r and y < body_bot + 10: continue
    if in_bottle(x, y) or in_dish(x, y): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))

for (x, y, fc) in [(70, GHY + 40, 'flower'), (260, 710, 'flower2'), (420, 730, 'flower'),
                   (700, 720, 'flower2'), (900, 740, 'flower'), (1100, 700, 'flower2'),
                   (1280, 680, 'flower'), (150, 720, 'flower2'), (550, 760, 'flower')]:
    if body_l < x < body_r and head_top < y < body_bot: continue
    if in_bottle(x, y) or in_dish(x, y): continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]

# tiny birds
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
assert white < 150000, white
assert im.getpixel((10, 200)) == (140, 200, 245), im.getpixel((10, 200))
print('grass px', im.getpixel((50, 720))); assert im.getpixel((50, 720)) == (110, 185, 70), im.getpixel((50, 720))
# bubble interior should be pale
bc = im.getpixel((880, 140))
print('big bubble', bc)
assert bc in ((180, 230, 255), (40, 30, 32)), bc
sc = im.getpixel((SUNX, SUNY))
print('sun', sc); assert sc == (255, 215, 60), sc
print('sky', im.getpixel((10,200)), 'grass', im.getpixel((50,720)), 'sun', sc, 'bubble', bc)
sky_n = sum(1 for p in im.getdata() if p == (140, 200, 245))
grass_n = sum(1 for p in im.getdata() if p == (110, 185, 70))
assert sky_n > 150000 and grass_n > 180000, (sky_n, grass_n)

D = {'name': 'peppa-bubbles', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa blowing soap bubbles outdoors: red dress, bubble wand with ring, soap bottle+dish, bubbles of several sizes, sun, clouds, grass, flowers. Horizon gap at dress. Bucket fills for sky/grass/sun; concentric bubbles/props.'}
json.dump(D, open('./peppa_bubbles_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa19\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa19.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_bubbles_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors')
