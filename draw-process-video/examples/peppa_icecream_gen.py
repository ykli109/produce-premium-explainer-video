#!/usr/bin/env python3
"""Peppa eating ice cream in a park (drawing-peppa-pig-13).
Fills use paint-bucket seeds; large flats are never brush-painted."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(13)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['cone', [210, 150, 70]], ['cream', [255, 245, 220]], ['swirl', [255, 160, 190]],
 ['cherry', [220, 40, 55]], ['wood', [150, 95, 55]], ['sign', [255, 95, 120]],
 ['bench', [170, 120, 70]],
]
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
    c = [p for p in P if abs(p[1] - y) < 12]
    if not c:
        c = sorted(P, key=lambda q: abs(q[1] - y))[:8]
    p = max(c, key=lambda q: q[0]) if right else min(c, key=lambda q: q[0])
    return [p[0] + (-6 if right else 6), p[1]]

# Peppa on left; ice cream clear to her right (no head overlap)
PS, PX, PY = 0.68, 40, 80
out += char(PS, PX, PY, 'dress')
out += [{'op': 'pause', 's': 0.45}]

RH = T((650, 378), PS, PX, PY)  # right hand
# Cone held out to the right of the hand, clear of head
CX = RH[0] + 95
TIPY = RH[1] + 10
TOPY = TIPY - 110
print('RH', RH, 'cone', CX, TOPY, TIPY)

# Arm extension from hand to cone tip (holding)
out += [C('ink'),
        S(cr([tuple(RH), (RH[0] + 40, RH[1] + 6), (CX - 4, TIPY - 2)], 8), 0.2, 0.008),
        S(cr([(RH[0], RH[1] + 5), (RH[0] + 40, RH[1] + 10), (CX - 2, TIPY + 2)], 8), 0.2, 0.008)]

# Waffle cone (closed triangle)
out += [S(poly([(CX - 32, TOPY), (CX + 32, TOPY), (CX, TIPY)]), 0.1, 0.009)]

# 3 stacked scoops — vertically separated enough to stay closed pockets
S1 = (CX, TOPY - 30, 50, 34)
S2 = (CX + 6, TOPY - 88, 44, 32)
S3 = (CX - 4, TOPY - 140, 36, 30)
out += [S(ell(*S1[:2], S1[2], S1[3], 64, 4), 0.05, 0.008),
        S(ell(*S2[:2], S2[2], S2[3], 64, 4), 0.05, 0.008),
        S(ell(*S3[:2], S3[2], S3[3], 64, 4), 0.05, 0.008)]
CHX, CHY, CHR = S3[0] + 2, S3[1] - S3[3] - 12, 14
out += [S(ell(CHX, CHY, CHR, CHR, 48, 4), 0.05, 0.008)]
out += [S(cr([(CHX, CHY - CHR + 2), (CHX + 8, CHY - CHR - 14), (CHX + 18, CHY - CHR - 8)], 6), 0.1, 0.008)]

# Stand sign (far right)
SX0, SY0 = 1120, 410
out += [C('ink'),
        S(poly([(SX0 - 8, SY0), (SX0 + 8, SY0), (SX0 + 8, 635), (SX0 - 8, 635)]), 0.1, 0.009),
        S(poly([(SX0 - 100, SY0 - 100), (SX0 + 100, SY0 - 100),
                (SX0 + 100, SY0 + 14), (SX0 - 100, SY0 + 14)]), 0.12, 0.009)]
ICX, ICY = SX0 - 10, SY0 - 45
# mini cone on sign — keep well inside board, closed
out += [S(poly([(ICX - 20, ICY + 2), (ICX + 20, ICY + 2), (ICX, ICY + 42)]), 0.1, 0.009),
        S(ell(ICX, ICY - 18, 26, 20, 48, 4), 0.08, 0.008)]

# Bench far left (may sit partly under peppa-x — place carefully left of shoes)
BX0, BY0 = 30, 580
# only if clear of peppa — peppa shoes around x~T(419/523,679)
shoe_l = T((419, 679), PS, PX, PY)
print('shoe_l', shoe_l)
if BX0 + 160 < shoe_l[0] - 20:
    BENCH = True
else:
    # move bench to right side instead, left of sign
    BX0, BY0 = 780, 560
    BENCH = True
out += [C('ink'),
        S(poly([(BX0, BY0), (BX0 + 150, BY0), (BX0 + 150, BY0 + 16), (BX0, BY0 + 16)]), 0.1, 0.009),
        S(poly([(BX0, BY0 - 40), (BX0 + 150, BY0 - 40), (BX0 + 150, BY0 - 26), (BX0, BY0 - 26)]), 0.1, 0.009),
        S([(BX0 + 12, BY0 + 16), (BX0 + 12, BY0 + 55)], 0.05, 0.01),
        S([(BX0 + 138, BY0 + 16), (BX0 + 138, BY0 + 55)], 0.05, 0.01),
        S([(BX0 + 12, BY0 - 26), (BX0 + 12, BY0)], 0.05, 0.01),
        S([(BX0 + 138, BY0 - 26), (BX0 + 138, BY0)], 0.05, 0.01)]

SUNX, SUNY, SUNR = 1220, 100, 52
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]

def cloud(cx, cy, sc):
    P = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        P.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(P + P[:3], 0.1, 0.008)
CLOUDS = [(620, 90, 1.0), (900, 130, 0.85), (300, 105, 0.7)]
out += [cloud(*c) for c in CLOUDS]

# Horizon through mid-dress so gap is real
dress_mid_y = T((469, 480), PS, PX, PY)[1]
GHY = int(dress_mid_y)
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
print('GHY', GHY, 'gap', pl[0], pr[0])
out += [C('dkgreen'),
        S([(2, GHY), (pl[0], GHY)], 0.15, 0.01),
        S([(pr[0], GHY), (1358, GHY)], 0.15, 0.01),
        S([(2, GHY), (2, 787)], 0.1, 0.01),
        S([(1358, GHY), (1358, 787)], 0.1, 0.01),
        S([(2, 787), (1358, 787)], 0.1, 0.01)]
out += [{'op': 'pause', 's': 0.4}]

# FILLS
out += [C('cone'), F((CX, TIPY - 50), (CX - 10, TIPY - 70), (CX + 10, TIPY - 70), (CX, TIPY - 30))]
out += [C('cream'), F((S1[0], S1[1]), (S1[0] - 18, S1[1]), (S1[0] + 18, S1[1]), (S1[0], S1[1] - 12))]
out += [C('swirl'), F((S2[0], S2[1]), (S2[0] - 14, S2[1]), (S2[0] + 14, S2[1]), (S2[0], S2[1] - 10))]
out += [C('cream'), F((S3[0], S3[1]), (S3[0] - 12, S3[1]), (S3[0] + 12, S3[1]), (S3[0], S3[1] - 10))]
out += [C('cherry'), F((CHX, CHY), (CHX - 4, CHY), (CHX + 4, CHY), (CHX, CHY - 4))]

# icon fills BEFORE sign board so board flood cannot leak into scoop/cone
out += [C('cream'), F((ICX, ICY - 18), (ICX - 8, ICY - 18), (ICX + 8, ICY - 18), (ICX, ICY - 25))]
out += [C('cone'), F((ICX, ICY + 18), (ICX - 5, ICY + 14), (ICX + 5, ICY + 14), (ICX, ICY + 28))]
out += [C('sign'), F((SX0 - 55, SY0 - 70), (SX0 + 55, SY0 - 70),
                     (SX0 - 55, SY0 - 5), (SX0 + 55, SY0 - 5),
                     (SX0 - 70, SY0 - 40), (SX0 + 70, SY0 - 40))]
out += [C('wood'), F((SX0, SY0 + 50), (SX0, SY0 + 20), (SX0, SY0 + 140), (SX0, SY0 + 100))]
out += [C('bench'), F((BX0 + 70, BY0 + 7), (BX0 + 70, BY0 - 33),
                      (BX0 + 30, BY0 + 7), (BX0 + 110, BY0 + 7))]

xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
pb = (min(xs) - 14, min(ys) - 14, max(xs) + 14, max(ys) + 14)
print('peppa box', pb)

G = []
for x in range(25, 1360, 48):
    for y in range(GHY + 20, 790, 38):
        if pb[0] < x < pb[2] and pb[1] < y < pb[3]:
            continue
        if BX0 - 10 < x < BX0 + 160 and BY0 - 50 < y < BY0 + 65:
            continue
        if SX0 - 120 < x < SX0 + 120 and min(SY0, GHY) < y < 660:
            continue
        G.append((x, y))
G += [(60, 720), (250, 750), (450, 730), (650, 760), (850, 740), (1000, 755),
      (1280, 730), (1320, 760), (550, 690), (920, 700), (80, 680), (350, 770),
      (1050, 690), (720, 680), (200, 700)]
out += [C('grass'), F(*G)]

out += [C('sun'), F((SUNX, SUNY), (SUNX - 16, SUNY), (SUNX + 16, SUNY), (SUNX, SUNY - 16), (SUNX, SUNY + 16))]

SKY = []
for x in range(30, 1360, 60):
    for y in range(25, GHY - 14, 44):
        if pb[0] - 10 < x < pb[2] + 20 and y < pb[3] + 5:
            continue
        if any(abs(x - a) < 100 * k and abs(y - b) < 50 * k for a, b, k in CLOUDS):
            continue
        if abs(x - SUNX) < SUNR + 24 and abs(y - SUNY) < SUNR + 24:
            continue
        if abs(x - CX) < 65 and CHY - 20 < y < TIPY + 10:
            continue
        if SX0 - 115 < x < SX0 + 115 and SY0 - 115 < y < SY0 + 25:
            continue
        SKY.append((x, y))
SKY += [(40, 200), (40, 380), (500, 40), (520, 380), (760, 40), (1000, 55),
        (1300, 220), (1300, 380), (580, 430), (840, 430), (200, 430), (70, 430),
        (420, 220), (1080, 260), (220, 280), (960, 300), (700, 260)]
out += [C('sky'), F(*SKY)]
out += [{'op': 'pause', 's': 0.45}]

# DETAILS
out += [C('ink')]
for yy in range(int(TOPY + 10), int(TIPY - 10), 14):
    t = (yy - TOPY) / max(1, (TIPY - TOPY))
    half = 32 * (1 - t)
    if half > 5:
        out.append(S([(CX - half + 3, yy), (CX + half - 3, yy)], 0.05, 0.008))
for xx in (-18, 0, 18):
    out.append(S([(CX + xx, TOPY + 6), (CX + xx * 0.1, TIPY - 8)], 0.05, 0.008))

out += [C('swirl'),
        S(cr([(S1[0] - 28, S1[1] - 4), (S1[0] - 8, S1[1] + 10), (S1[0] + 24, S1[1] - 2)], 6), 0.25, 0.008),
        S(cr([(S2[0] - 24, S2[1]), (S2[0], S2[1] + 12), (S2[0] + 24, S2[1] - 4)], 6), 0.25, 0.008),
        S(cr([(S3[0] - 18, S3[1] + 2), (S3[0] + 4, S3[1] + 10), (S3[0] + 20, S3[1] - 2)], 6), 0.25, 0.008)]

out += [C('sun')]
for k in range(10):
    a = 2 * math.pi * k / 10
    out.append(S([(SUNX + (SUNR + 12) * math.cos(a), SUNY + (SUNR + 12) * math.sin(a)),
                  (SUNX + (SUNR + 34) * math.cos(a), SUNY + (SUNR + 34) * math.sin(a))], 0, 0.008))

out += [C('dkgreen')]
for x, y in [(50, GHY + 55), (200, GHY + 70), (380, 720), (560, 745), (720, 730),
             (900, 750), (1040, 725), (1200, 740), (1300, GHY + 50), (100, 700),
             (480, 690), (980, 690)]:
    if pb[0] < x < pb[2] and y < pb[3]:
        continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))

for (x, y, fc) in [(100, 660, 'flower'), (280, 730, 'flower2'), (500, 710, 'flower'),
                   (700, 720, 'flower2'), (950, 700, 'flower'), (1260, 710, 'flower'),
                   (600, 755, 'flower2'), (1330, 670, 'flower')]:
    if pb[0] < x < pb[2] and pb[1] < y < pb[3]:
        continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]

out += [C('ink')]
for x, y in [(540, 55), (820, 75), (1080, 50)]:
    out.append(S(cr([(x - 16, y), (x - 8, y - 7), (x, y), (x + 8, y - 7), (x + 16, y)], 5), 0, 0.008))

out += [C('white'),
        dot(S1[0] - 22, S1[1] - 10, 4),
        dot(S2[0] + 18, S2[1] - 8, 3),
        dot(S3[0] - 12, S3[1] - 8, 3),
        dot(CHX - 5, CHY - 5, 3)]
out += [C('ink'),
        S(cr([(SX0 - 45, SY0 - 10), (SX0, SY0 + 2), (SX0 + 45, SY0 - 10)], 6), 0.1, 0.008)]

# PIL seed-check
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p):
    return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
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
assert white < 140000, white

D = {'name': 'peppa-icecream', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa in a park eating a tall soft-serve ice cream (waffle cone + cream/pink scoops + cherry); sun, clouds, flowers, bench, stand sign. Horizon stops at dress. Bucket fills.'}
json.dump(D, open('./peppa_icecream_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa13\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa13.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
print(len(out), 'ops', len(pal), 'colors')
