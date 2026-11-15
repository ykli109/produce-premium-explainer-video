#!/usr/bin/env python3
"""Peppa watching fireworks at night (drawing-peppa-pig-26, 佩奇看烟花)."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(26)
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

pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['night', [32, 44, 102]], ['grass', [62, 135, 70]], ['dkgreen', [34, 92, 44]],
 ['moon', [255, 226, 96]], ['wall', [250, 232, 192]], ['roof', [196, 72, 58]], ['window', [255, 200, 60]],
 ['door', [150, 96, 56]], ['fred', [255, 70, 70]], ['fyellow', [255, 236, 80]], ['fgreen', [110, 230, 120]],
 ['fpurple', [196, 120, 255]], ['fblue', [100, 190, 255]], ['spark', [255, 250, 200]], ['pink', [255, 140, 200]],
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
HAND = T((655, 381), PS, PX, PY)

def rect(x0, y0, x1, y1):
    return S([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0), (x1, y0)], 0.03, 0.012)
# ---------- 2. House on the right, sitting on the horizon ----------
HX0, HX1, HT, HB = 1070, 1250, GHY - 140, GHY + 30
RA = (1160, HT - 95)
out += [C('ink'), rect(HX0, HT, HX1, HB)]
MARK['house_wall'] = len(out)
out += [S([(HX0 - 22, HT), RA, (HX1 + 22, HT), (HX0 - 22, HT), RA], 0.03, 0.012)]
MARK['house_roof'] = len(out)
WIN = [(1092, HT + 26, 1142, HT + 76), (1178, HT + 26, 1228, HT + 76)]
for w in WIN: out.append(rect(*w))
MARK['house_windows'] = len(out)
DOOR = (1138, HT + 96, 1182, HB)
out += [S([(DOOR[0], HB), (DOOR[0], DOOR[1]), (DOOR[2], DOOR[1]), (DOOR[2], HB)], 0.03, 0.012)]
MARK['house_door'] = len(out)
out += [P(0.4)]
# ---------- 3. Crescent moon ----------
MX, MY, MR = 1290, 82, 44
IX, IY, IR = 1308, 68, 38
out += [S(ell(MX, MY, MR, MR, 64, 4), 0.03, 0.008)]
inner = []
for k in range(0, 73):
    a = 2 * math.pi * k / 72; x, y = IX + IR * math.cos(a), IY + IR * math.sin(a)
    if (x - MX) ** 2 + (y - MY) ** 2 <= (MR + 3) ** 2: inner.append((x, y))
# order the inside arc as a continuous polyline (start at the largest gap)
ang = sorted(math.atan2(y - IY, x - IX) for x, y in inner)
gaps = [(ang[(i + 1) % len(ang)] - ang[i]) % (2 * math.pi) for i in range(len(ang))]
st = (gaps.index(max(gaps)) + 1) % len(ang)
arcp = [(IX + (IR) * math.cos(a), IY + IR * math.sin(a)) for a in ang[st:] + ang[:st]]
out += [S(arcp, 0, 0.008)]
MARK['moon_line'] = len(out)
out += [P(0.3)]
# ---------- 4. Horizon (stops at the dress and at the house) + border ----------
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
out += [C('dkgreen')]
for a, b in [(2, pl[0]), (pr[0], HX0 + 2), (HX1 - 2, 1358)]:
    for dy in (0, 3, -2):
        out.append(S([(a, GHY + dy), (b, GHY + dy)], 0.05, 0.006))
MARK['horizon_line'] = len(out)
out += [S([(2, GHY - 2), (2, 787)], 0.05, 0.009), S([(5, GHY - 2), (5, 787)], 0.05, 0.009),
        S([(1358, GHY - 2), (1358, 787)], 0.05, 0.009), S([(1355, GHY - 2), (1355, 787)], 0.05, 0.009),
        S([(2, 787), (1358, 787)], 0.05, 0.009), S([(2, 784), (1358, 784)], 0.05, 0.009),
        S([(2, 2), (1358, 2)], 0.05, 0.01), S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [dot(pl[0], GHY, 6), dot(pr[0], GHY, 6)]
out += [P(0.3)]
MARK['horizon_end'] = len(out)
# ---------- 5. House + moon fills ----------
out += [C('wall'), F((HX0 + 14, HT + 100), (HX1 - 14, HT + 100), ((HX0 + HX1) / 2, HT + 12), (HX0 + 12, HB - 12), (HX1 - 12, HB - 12))]
MARK['wall_fill'] = len(out)
out += [C('roof'), F((RA[0], HT - 30), (RA[0] - 50, HT - 10), (RA[0] + 50, HT - 10))]
MARK['roof_fill'] = len(out)
out += [C('window'), F(*[((w[0] + w[2]) / 2, (w[1] + w[3]) / 2) for w in WIN])]
MARK['window_fill'] = len(out)
out += [C('door'), F(((DOOR[0] + DOOR[2]) / 2, (DOOR[1] + HB) / 2))]
MARK['door_fill'] = len(out)
out += [C('moon'), F((1266, 100), (1256, 82), (1275, 118))]
MARK['moon_fill'] = len(out)
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_house(x, y): return HX0 - 30 < x < HX1 + 30 and RA[1] - 10 < y < HB + 10
def in_moon(x, y): return (x - MX) ** 2 + (y - MY) ** 2 < (MR + 10) ** 2
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_house(x, y) or in_moon(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (pr[0] + 14, GHY - 12), (body_l - 20, GHY - 14), (HX0 - 14, GHY - 12), (HX1 + 14, GHY - 12),
        (HX0 - 10, HT - 6), (HX1 + 10, HT - 6), (IX + 12, IY - 4), (IX + 4, IY + 14)]
SKY = [(x, y) for x, y in SKY if y < GHY - 7]
out += [C('night'), F(*SKY)]
MARK['sky_fill'] = len(out)
G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if in_peppa(x, y) or in_house(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), (body_l + 30, body_bot + 25), ((body_l + body_r) / 2, body_bot - 30),
      (HX0 - 12, HB), (HX1 + 12, HB), ((HX0 + HX1) / 2, HB + 14)]
out += [C('grass'), F(*G)]
MARK['grass_fill'] = len(out)
out += [P(0.4)]
MARK['fill_end'] = len(out)
# ---------- 6. House details ----------
out += [C('ink')]
for w in WIN:
    cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
    out += [S([(cx, w[1]), (cx, w[3])], 0, 0.012), S([(w[0], cy), (w[2], cy)], 0, 0.012)]
MARK['window_cross'] = len(out)
out += [C('window'), dot(DOOR[2] - 10, (DOOR[1] + HB) / 2 + 4, 4)]
MARK['door_knob'] = len(out)
# ---------- 7. Fireworks ----------
def trail(cx, cy, R):
    x0, y0 = cx - 30, GHY - 18; y1 = cy + R + 14
    pts = cr([(x0, y0), (x0 + 12, (y0 + y1) / 2 + 20), (cx - 4, y1)], 12)
    segs = [pts[i:i + 5] for i in range(0, len(pts) - 4, 8)]
    return [S(s, 0, 0.01) for s in segs]
def burst(cx, cy, R, n, rot):
    r = []
    for k in range(n):
        a = rot + 2 * math.pi * k / n
        r.append(S([(cx + 0.22 * R * math.cos(a), cy + 0.22 * R * math.sin(a)), (cx + R * math.cos(a), cy + R * math.sin(a))], 0.02, 0.011))
    return r
def sparks(cx, cy, R, n, rot):
    r = []
    for k in range(n):
        a = rot + math.pi / n + 2 * math.pi * k / n
        r.append(S([(cx + 0.72 * R * math.cos(a), cy + 0.72 * R * math.sin(a)), (cx + 0.86 * R * math.cos(a), cy + 0.86 * R * math.sin(a))], 0, 0.011))
    return r
FW = [('fred', 520, 150, 82, 12, 0.0, True), ('fyellow', 705, 275, 60, 10, 0.2, True), ('fgreen', 840, 112, 80, 12, 0.13, False),
      ('fblue', 668, 72, 44, 8, 0.4, False), ('fpurple', 975, 232, 56, 10, 0.3, False)]
for c, cx, cy, R, n, rot, tr in FW:
    if tr:
        out += [C('spark')] + trail(cx, cy, R)
        MARK['trail_' + c] = len(out)
    out += [C(c)] + burst(cx, cy, R, n, rot)
    MARK['burst_' + c] = len(out)
    out += [C('spark')] + sparks(cx, cy, R, n // 2, rot) + [dot(cx, cy, 5)]
    MARK['sparks_' + c] = len(out)
    out += [P(0.25)]
MARK['fireworks_end'] = len(out)
# ---------- 8. Sparkler in Peppa's hand ----------
SX, SY = HAND[0] + 46, HAND[1] - 64
out += [C('ink'), S([(HAND[0] + 2, HAND[1] - 2), (SX, SY)], 0, 0.012)]
MARK['stick'] = len(out)
out += [C('fyellow')]
for k in range(8):
    a = 2 * math.pi * k / 8 + 0.2
    out.append(S([(SX + 6 * math.cos(a), SY + 6 * math.sin(a)), (SX + 24 * math.cos(a), SY + 24 * math.sin(a))], 0, 0.011))
out += [C('spark'), dot(SX, SY, 5)]
MARK['sparkler'] = len(out)
# ---------- 9. Stars, tufts, flowers ----------
def busy(x, y):
    return any(math.dist((x, y), (cx, cy)) < R + 26 for _, cx, cy, R, *_ in FW) or in_moon(x, y) or in_house(x, y) or in_peppa(x, y) or math.dist((x, y), (SX, SY)) < 50
out += [C('moon')]
STARS = [(60, 50), (200, 40), (300, 110), (40, 250), (420, 330), (600, 360), (760, 230), (900, 330), (1120, 40), (1020, 100), (1200, 150), (1330, 200), (1300, 330), (230, 300)]
st_n = 0
for x, y in STARS:
    if busy(x, y) or y > GHY - 22: continue
    out += [S([(x - 9, y), (x + 9, y)], 0, 0.01), S([(x, y - 9), (x, y + 9)], 0, 0.01)]
    st_n += 1
print('stars', st_n)
MARK['stars_end'] = len(out)
out += [C('dkgreen')]
TUFT = [(45, GHY + 50), (150, GHY + 120), (60, 700), (200, 740), (330, 760), (480, 720), (620, 690), (560, 520),
        (760, 600), (960, 520), (1100, 760), (1300, 700), (1180, 610), (700, 480)]
for x, y in TUFT:
    if in_peppa(x, y) or in_house(x, y): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)
FL = [(250, 690, 'pink'), (600, 600, 'window'), (880, 650, 'pink')]
fl_marks = []
for (x, y, fc) in FL:
    if in_peppa(x, y): continue
    out += [C('dkgreen'), S([(x, y + 22), (x, y + 6)], 0.1, 0.008)]
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5) for k in range(5)] + [C('white'), dot(x, y, 4)]
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
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'wall', 'roof', 'window', 'door', 'moon'}
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
assert im.getpixel((10, 200)) == col['night'], im.getpixel((10, 200))
assert im.getpixel((50, 760)) == col['grass'], im.getpixel((50, 760))
assert im.getpixel((HX0 + 20, HT + 110)) == col['wall'], im.getpixel((HX0 + 20, HT + 110))
assert im.getpixel((RA[0], HT - 30)) == col['roof']
assert im.getpixel((1266, 100)) == col['moon']
assert im.getpixel((IX + 12, IY - 4)) == col['night'], im.getpixel((IX + 12, IY - 4))
assert im.getpixel((HX1 + 40, GHY + 40)) == col['grass']
print('estimate s', round(est(out), 1))
D = {'name': 'peppa-fireworks', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa at night on the grass holding a sparkler, watching fireworks: house with lit windows on the right sitting on the horizon (horizon stops at the dress and house walls), crescent moon, night sky + grass bucket fills, then five fireworks bursts (red/yellow/green/blue/purple radial strokes + pale sparks, rocket trails for the first two) painted after the sky fill, twinkle stars, tufts, flowers.'}
json.dump(D, open('./peppa_fireworks_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa26\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa26.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_fireworks_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
