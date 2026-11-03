#!/usr/bin/env python3
"""Peppa fishing by a pond outdoors (drawing-peppa-pig-15).
Fills use paint-bucket seeds; large flats are never brush-painted.
Thin props (rod, bobber, fish) use solid concentric/parallel strokes."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(15)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['water', [70, 170, 230]], ['water2', [40, 130, 200]],
 ['sun', [255, 215, 60]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['wood', [160, 100, 55]], ['wood2', [120, 70, 40]],
 ['lily', [70, 160, 80]], ['bobber', [230, 50, 50]],
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
def irregular_oval(cx, cy, rx, ry, n=80, wobble=0.12):
    P = []
    for k in range(n):
        a = 2 * math.pi * k / n
        b = 1 + wobble * math.sin(3 * a + 0.4) + 0.06 * math.sin(5 * a)
        P.append((cx + rx * b * math.cos(a), cy + ry * b * math.sin(a)))
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

# ---- Peppa on left bank ----
PS, PX, PY = 0.58, 100, 90
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
LH = T((320, 400), PS, PX, PY)
RH = T((620, 400), PS, PX, PY)
print('hands', LH, RH)

# ---- Fishing rod (parallel wood strokes) ----
GRIP = (RH[0] - 8, RH[1] + 8)
TIP = (720, 130)
MID = (480, 180)
out += [C('wood')] + rod_strokes(GRIP, MID, 7, 7) + rod_strokes(MID, TIP, 5, 6)
out += [C('wood2')] + rod_strokes(GRIP, MID, 3, 3)
out += [C('ink')]
for a, b, w in [(GRIP, MID, 7), (MID, TIP, 5)]:
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w, dx / L * w
    out += [S([(ax + nx, ay + ny), (bx + nx, by + ny)], 0.0, 0.007),
            S([(ax - nx, ay - ny), (bx - nx, by - ny)], 0.0, 0.007)]

BOBX, BOBY = 900, 520
out += [C('ink'), S([(TIP[0], TIP[1]), (BOBX, BOBY - 18)], 0.0, 0.007)]

# Bobber — concentric red + white band
out += [C('bobber')]
for f in (1.0, 0.75, 0.5, 0.3, 0.1):
    out.append(S(ell(BOBX, BOBY, 14 * f, 18 * f, 36, 2), 0.0, 0.006))
out += [C('white')]
for f in (0.55, 0.35):
    out.append(S([(BOBX - 10 * f, BOBY), (BOBX + 10 * f, BOBY)], 0.0, 0.006))
out += [C('ink'),
        S(ell(BOBX, BOBY, 14, 18, 48, 4), 0.05, 0.007),
        S(cr([(BOBX, BOBY + 18), (BOBX + 6, BOBY + 28), (BOBX - 2, BOBY + 36), (BOBX + 8, BOBY + 42)], 6), 0.05, 0.007)]

# ---- Pond ----
PCX, PCY, PRX, PRY = 880, 600, 320, 140
# Double-stroke a nearly-elliptical pond; keep wobble mild and over-close heavily
POND = irregular_oval(PCX, PCY, PRX, PRY, 120, 0.06)
POND = POND + POND[:12]
out += [C('ink'), S(POND, 0.05, 0.008)]
# second slightly inset stroke to seal gaps from wobble/brush ends
POND2 = irregular_oval(PCX, PCY, PRX - 6, PRY - 5, 100, 0.05)
POND2 = POND2 + POND2[:10]
out += [S(POND2, 0.05, 0.008)]

LILIES = [(720, 560, 38, 22), (1020, 640, 42, 24), (940, 555, 30, 18), (780, 680, 34, 20)]
# outlines only here; solid lily paint happens AFTER water fill (avoids bucket leak)
for lx, ly, lrx, lry in LILIES:
    out.append(S(ell(lx, ly, lrx, lry, 56, 6), 0.05, 0.008))

# Jumping fish — concentric orange strokes
FX0, FY0 = 1125, 475
out += [C('flower2')]
for f in (1.0, 0.8, 0.6, 0.4, 0.2):
    out.append(S(ell(FX0, FY0, 48 * f, 22 * f, 40, 2), 0.0, 0.006))
for f in (1.0, 0.6, 0.3):
    out.append(S(poly([(1085, 478), (1055, 460 + 5 * (1 - f)), (1058, 495 - 5 * (1 - f))]), 0.0, 0.006))
out += [C('ink'),
        S(ell(FX0, FY0, 48, 22, 48, 4), 0.05, 0.007),
        S(poly([(1085, 478), (1055, 460), (1058, 495)]), 0.05, 0.007),
        dot(1165, 470, 4),
        S(cr([(1100, 510), (1120, 502), (1145, 508), (1170, 500), (1190, 512)], 6), 0.15, 0.008),
        S(cr([(1110, 520), (1135, 514), (1160, 522)], 5), 0.15, 0.008),
        S([(1145, 455), (1155, 440), (1165, 458)], 0.1, 0.008)]

# Reeds
def reed(x, y0, h, lean=0):
    tip = (x + lean, y0 - h)
    return [S([(x, y0), tip], 0.05, 0.008),
            S([(tip[0], tip[1]), (tip[0] - 10, tip[1] + 14)], 0.1, 0.008),
            S([(tip[0], tip[1]), (tip[0] + 10, tip[1] + 14)], 0.1, 0.008)]
out += [C('dkgreen')]
for rx, ry0, rh, lean in [(560, 470, 55, -8), (590, 475, 70, 5), (620, 468, 48, -3),
                           (1180, 480, 60, 6), (1210, 475, 72, -4), (1240, 482, 50, 8),
                           (520, 485, 40, 4), (1270, 490, 45, -6)]:
    out += reed(rx, ry0, rh, lean)

# Sun + clouds
SUNX, SUNY, SUNR = 1180, 85, 50
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
def cloud(cx, cy, sc):
    P = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        P.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(P + P[:3], 0.1, 0.008)
CLOUDS = [(420, 75, 0.85), (700, 110, 0.7), (980, 70, 0.8)]
out += [cloud(*c) for c in CLOUDS]

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

# ---- FILLS (bucket for large flats only) ----
def in_pond(x, y):
    dx = (x - PCX) / PRX
    dy = (y - PCY) / PRY
    return dx * dx + dy * dy < 0.82

def near_lily(x, y):
    for lx, ly, lrx, lry in LILIES:
        if ((x - lx) / (lrx + 6)) ** 2 + ((y - ly) / (lry + 6)) ** 2 < 1.0:
            return True
    return False

# Water FIRST (pond empty except bobber/fish); lily outlines may sit on water
WATER = []
for x in range(int(PCX - PRX) + 30, int(PCX + PRX) - 20, 36):
    for y in range(int(PCY - PRY) + 25, int(PCY + PRY) - 20, 28):
        if not in_pond(x, y):
            continue
        if abs(x - BOBX) < 24 and abs(y - BOBY) < 28:
            continue
        if ((x - FX0) / 58) ** 2 + ((y - FY0) / 30) ** 2 < 1.15:
            continue
        WATER.append((x, y))
WATER += [(880, 600), (750, 600), (1000, 600), (850, 660), (950, 570),
          (700, 620), (1050, 620), (820, 690), (980, 670), (900, 640),
          (760, 580), (1100, 590), (860, 580), (920, 700), (800, 640),
          (940, 620), (860, 640), (1000, 660)]
out += [C('water'), F(*WATER)]

# Lily pads as concentric green strokes ON TOP of water (no bucket)
out += [C('lily')]
for lx, ly, lrx, lry in LILIES:
    for f in (1.0, 0.8, 0.6, 0.4, 0.2):
        out.append(S(ell(lx, ly, lrx * f, lry * f, 36, 2), 0.0, 0.006))
    out.append(S([(lx, ly), (lx + lrx * 0.55, ly - 3)], 0.0, 0.006))


G = []
for x in range(25, 1360, 42):
    for y in range(GHY + 14, 790, 32):
        if body_l - 8 < x < body_r + 8 and head_top - 4 < y < body_bot + 8:
            continue
        if in_pond(x, y):
            continue
        G.append((x, y))
G += [(40, 500), (80, 600), (150, 700), (200, 550), (280, 720), (350, 500),
      (400, 650), (450, 750), (500, 520), (550, 700), (1280, 520), (1320, 650),
      (1300, 750), (600, 760), (1100, 760), (70, 760), (250, 500), (380, 580),
      (body_l - 25, body_bot - 10), (body_r + 25, body_bot - 10),
      (body_l - 15, body_bot + 20), (body_r + 15, body_bot + 20),
      (body_l + 20, body_bot + 30), (120, 500), (300, 500)]
for ang in range(0, 360, 18):
    a = math.radians(ang)
    rr = 1.02 + 0.02 * math.sin(3 * a)
    G.append((PCX + (PRX + 28) * rr * math.cos(a), PCY + (PRY + 22) * rr * math.sin(a)))
out += [C('grass'), F(*G)]

out += [C('sun'), F((SUNX, SUNY), (SUNX - 14, SUNY), (SUNX + 14, SUNY),
                    (SUNX, SUNY - 14), (SUNX, SUNY + 14))]

def near_rod(x, y, tol=16):
    for a, b in [(GRIP, MID), (MID, TIP)]:
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
        px, py = ax + t * dx, ay + t * dy
        if (x - px) ** 2 + (y - py) ** 2 < tol * tol:
            return True
    ax, ay = TIP; bx, by = BOBX, BOBY - 18
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
    px, py = ax + t * dx, ay + t * dy
    return (x - px) ** 2 + (y - py) ** 2 < 12 * 12

SKY = []
for x in range(28, 1360, 48):
    for y in range(22, GHY - 10, 34):
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < GHY + 4:
            continue
        if any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS):
            continue
        if abs(x - SUNX) < SUNR + 22 and abs(y - SUNY) < SUNR + 22:
            continue
        if near_rod(x, y, 18):
            continue
        SKY.append((x, y))
SKY += [(40, 180), (40, 280), (500, 40), (600, 200), (800, 40), (900, 200),
        (1100, 40), (1300, 200), (1300, 300), (200, 200), (350, 50),
        (body_r + 40, 150), (body_r + 50, 250), (body_l - 30, 200),
        (550, GHY - 30), (750, GHY - 25), (1000, GHY - 30), (70, GHY - 30)]
for y in range(100, GHY - 5, 28):
    SKY.append((TIP[0] + 40, y))
    SKY.append((TIP[0] - 50, y))
out += [C('sky'), F(*SKY)]
out += [{'op': 'pause', 's': 0.4}]

# ---- DETAILS ----
out += [C('sun')]
for k in range(10):
    a = 2 * math.pi * k / 10
    out.append(S([(SUNX + (SUNR + 10) * math.cos(a), SUNY + (SUNR + 10) * math.sin(a)),
                  (SUNX + (SUNR + 32) * math.cos(a), SUNY + (SUNR + 32) * math.sin(a))], 0, 0.008))

out += [C('water2')]
for yy, ph in [(560, 0.0), (620, 1.2), (680, 0.5)]:
    pts = []
    for x in range(int(PCX - PRX) + 40, int(PCX + PRX) - 30, 18):
        if not in_pond(x, yy) or near_lily(x, yy) or (abs(x - BOBX) < 20 and abs(yy - BOBY) < 24):
            if len(pts) > 2:
                out.append(S(pts, 0.12, 0.008)); pts = []
            continue
        pts.append((x, yy + 4.5 * math.sin(x / 28 + ph)))
    if len(pts) > 2:
        out.append(S(pts, 0.12, 0.008))

out += [C('dkgreen')]
for x, y in [(50, GHY + 50), (180, GHY + 70), (320, 720), (450, 740), (550, 500),
             (1280, GHY + 40), (1320, 700), (200, 650), (100, 720), (400, 680),
             (480, 760), (600, 730), (1200, 740), (70, 560)]:
    if body_l < x < body_r and y < body_bot + 10:
        continue
    if in_pond(x, y):
        continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))

for (x, y, fc) in [(70, 520, 'flower'), (220, 700, 'flower2'), (380, 640, 'flower'),
                   (500, 720, 'flower2'), (1260, 540, 'flower'), (1320, 680, 'flower2'),
                   (150, 600, 'flower'), (430, 530, 'flower2'), (80, 700, 'flower')]:
    if body_l < x < body_r and head_top < y < body_bot:
        continue
    if in_pond(x, y):
        continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]

out += [C('ink')]
for x, y in [(520, 55), (820, 48), (1050, 60)]:
    out.append(S(cr([(x - 16, y), (x - 8, y - 7), (x, y), (x + 8, y - 7), (x + 16, y)], 5), 0, 0.008))

# ---- seed-check preview ----
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p):
    return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
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
                if o_c in ('skin', 'dress', 'cheek', 'shoe', 'lily', 'sun', 'water'):
                    probe = im.copy()
                    ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc)
                    limit = 60000 if o_c in ('skin', 'dress', 'cheek', 'shoe', 'lily') else 120000
                    if o_c == 'water':
                        limit = 200000  # pond only
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
assert skin < 80000, skin
assert white < 120000, white
assert im.getpixel((10, 200)) == (140, 200, 245), im.getpixel((10, 200))
assert im.getpixel((880, 600)) == (70, 170, 230), im.getpixel((880, 600))

D = {'name': 'peppa-fish', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa fishing by a pond outdoors: wooden rod + line + bobber, irregular blue pond, lily pads, jumping fish, reeds, sun, clouds, grass, flowers. Horizon gaps at dress. Bucket fills.'}
json.dump(D, open('./peppa_fish_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa15\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa15.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
print(len(out), 'ops', len(pal), 'colors')
