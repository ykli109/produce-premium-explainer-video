#!/usr/bin/env python3
"""Peppa looking at a rainbow after the rain (drawing-peppa-pig-24, 佩奇看彩虹)."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(24)
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

MARK = {}
# ---------- 1. Peppa (right arm raised, pointing up at the rainbow) ----------
PS, PX, PY = 0.62, 95, 100
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
GHY = int(T((469, 480), PS, PX, PY)[1])

# ---------- 2. Rainbow: 7 nested half-ellipse arcs standing on the horizon ----------
RCX = 860; RX0, RY0, BW = 440, 330, 30
BANDS = ['rred', 'rorange', 'ryellow', 'rgreen', 'rblue', 'rpurple']
def arc(rx, ry, ext=2, n=None):
    n = n or int(rx / 3)
    pts = [(RCX - rx, GHY + ext)]
    for k in range(n + 1):
        a = math.pi + math.pi * k / n
        pts.append((RCX + rx * math.cos(a), GHY + ry * math.sin(a)))
    pts.append((RCX + rx, GHY + ext))
    return pts
out += [C('ink')]
for k in range(7):
    out.append(S(arc(RX0 - BW * k, RY0 - BW * k), 0.04, 0.009))
    if k in (0, 3): MARK['arc%d' % k] = len(out)
out += [P(0.4)]
MARK['rainbow_line'] = len(out)

# ---------- 3. Sun + clouds ----------
SUNX, SUNY, SUNR = 1268, 92, 42
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
MARK['sun_line'] = len(out)
CLOUDS = [(215, 52, 0.62), (RCX + 10, GHY - 88, 0.5)]
out += [cloud(*c) for c in CLOUDS]
out += [P(0.3)]
MARK['sky_end'] = len(out)

# ---------- 4. Horizon (stops at the dress) + border ----------
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
out += [C('dkgreen')]
for a, b in [(2, pl[0]), (pr[0], 1358)]:
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

# ---------- 5. Rainbow bands, bucket by bucket ----------
for k, c in enumerate(BANDS):
    rx = RX0 - BW * k - BW / 2; ry = RY0 - BW * k - BW / 2
    seeds = [(RCX + rx * math.cos(math.radians(a)), GHY - ry * math.sin(math.radians(a))) for a in (90, 40, 140, 15, 165)]
    out += [C(c), F(*seeds)]
    MARK['band_' + c] = len(out)
out += [P(0.4)]
MARK['bands_end'] = len(out)

def in_sun(x, y): return (x - SUNX) ** 2 + (y - SUNY) ** 2 < (SUNR + 8) ** 2
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_cloud(x, y): return any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS)
def in_rb(x, y):
    o = ((x - RCX) / (RX0 + 8)) ** 2 + ((y - GHY) / (RY0 + 8)) ** 2
    i = ((x - RCX) / (RX0 - 6 * BW - 8)) ** 2 + ((y - GHY) / (RY0 - 6 * BW - 8)) ** 2
    return o < 1 and i > 1 and y < GHY + 12

# ---------- 6. Sun, sky (outside and under the arch), grass ----------
out += [C('sun'), F((SUNX, SUNY), (SUNX - 15, SUNY), (SUNX + 15, SUNY), (SUNX, SUNY - 15), (SUNX, SUNY + 15))]
MARK['sun_fill'] = len(out)
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_cloud(x, y) or in_sun(x, y) or in_rb(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (pr[0] + 14, GHY - 12), (body_l - 20, GHY - 14),
        (RCX - RX0 - 14, GHY - 12), (RCX + RX0 + 14, GHY - 12), (RCX - RX0 + 6 * BW + 20, GHY - 12),
        (RCX + RX0 - 6 * BW - 20, GHY - 12), (RCX, GHY - 20)]
SKY = [(x, y) for x, y in SKY if y < GHY - 7]
out += [C('sky'), F(*SKY)]
MARK['sky_fill'] = len(out)
G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if in_peppa(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), (body_l + 30, body_bot + 25),
      ((body_l + body_r) / 2, body_bot - 30)]
for k in range(7):
    for sgn in (-1, 1):
        G.append((RCX + sgn * (RX0 - BW * k), GHY + 14))
out += [C('grass'), F(*G)]
MARK['grass_fill'] = len(out)
out += [P(0.4)]
MARK['fill_end'] = len(out)

# ---------- 7. Details ----------
out += [C('sun')]
for ang in range(0, 360, 30):
    a = math.radians(ang)
    p1 = (SUNX + (SUNR + 26) * math.cos(a), SUNY + (SUNR + 26) * math.sin(a))
    if in_rb(*p1) or p1[0] > 1350 or p1[1] < 8: continue
    out.append(S([(SUNX + (SUNR + 8) * math.cos(a), SUNY + (SUNR + 8) * math.sin(a)), p1], 0.1, 0.008))
MARK['rays_end'] = len(out)
# snail on the grass (shell outline + bucket + spiral + body)
SN = (1080, 640, 30)
out += [C('ink'), S(ell(SN[0], SN[1], SN[2], SN[2], 56, 4), 0.02, 0.008)]
MARK['snail_line'] = len(out)
out += [C('snail'), F((SN[0], SN[1] + 4), (SN[0] - 10, SN[1] - 8))]
MARK['snail_fill'] = len(out)
sp = [(SN[0] + (3 + 15 * t / (4 * math.pi)) * math.cos(t), SN[1] + (3 + 15 * t / (4 * math.pi)) * math.sin(t)) for t in [i * 0.15 for i in range(84)]]
out += [C('ink'), S(sp, 0, 0.008)]
out += [S(cr([(SN[0] - 34, SN[1] + 28), (SN[0] + 10, SN[1] + 34), (SN[0] + 52, SN[1] + 30), (SN[0] + 60, SN[1] + 6)], 8), 0.05, 0.008),
        S([(SN[0] + 56, SN[1] + 8), (SN[0] + 62, SN[1] - 22)], 0, 0.008), S([(SN[0] + 64, SN[1] + 8), (SN[0] + 76, SN[1] - 18)], 0, 0.008),
        dot(SN[0] + 62, SN[1] - 24, 4), dot(SN[0] + 77, SN[1] - 20, 4)]
MARK['snail_end'] = len(out)
out += [C('dkgreen')]
TUFT = [(45, GHY + 50), (150, GHY + 110), (60, 700), (200, 740), (330, 760), (480, 750), (620, 720),
        (720, 470), (840, 760), (960, 600), (1100, 760), (1300, 700), (1320, 470), (1210, 520), (330, 650), (560, 560)]
for x, y in TUFT:
    if in_peppa(x, y) or math.dist((x, y), SN[:2]) < 90: continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)
FL = [(80, GHY + 40, 'pink'), (250, 700, 'orange'), (440, 690, 'pink'), (600, 640, 'orange'),
      (780, 600, 'pink'), (900, 720, 'orange'), (1250, 600, 'pink'), (1180, 740, 'orange'), (130, 760, 'pink')]
fl_marks = []
for (x, y, fc) in FL:
    if in_peppa(x, y) or math.dist((x, y), SN[:2]) < 70: continue
    out += [C('leaf'), S([(x, y + 22), (x, y + 6)], 0.1, 0.008)]
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]
    fl_marks.append(len(out))
MARK['flowers_end'] = len(out)
MARK['flower_each'] = fl_marks
out += [C('ink')]
for x, y in [(420, 70), (560, 120), (1130, 230)]:
    if in_rb(x, y): continue
    out.append(S(cr([(x - 14, y), (x - 7, y - 6), (x, y), (x + 7, y - 6), (x + 14, y)], 5), 0, 0.008))
MARK['end'] = len(out)

# ---------- seed check (PIL simulation) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
LATE = {'snail'}
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'sun', 'snail', 'rred', 'rorange', 'ryellow', 'rgreen', 'rblue', 'rpurple'}
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
assert im.getpixel((10, 200)) == col['sky'], im.getpixel((10, 200))
assert im.getpixel((50, 760)) == col['grass'], im.getpixel((50, 760))
assert im.getpixel((RCX, int(GHY - RY0 + BW / 2))) == col['rred'], im.getpixel((RCX, int(GHY - RY0 + BW / 2)))
assert im.getpixel((RCX, int(GHY - RY0 + 5.5 * BW))) == col['rpurple']
assert im.getpixel((RCX - 200, GHY - 30)) == col['sky'], im.getpixel((RCX - 200, GHY - 30))
assert im.getpixel((RCX, GHY + 40)) == col['grass']
assert sum(1 for q in im.crop((SN[0]-30,SN[1]-30,SN[0]+30,SN[1]+30)).getdata() if q == col['snail']) > 300
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
D = {'name': 'peppa-rainbow', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa after the rain pointing up at a big rainbow: 7 nested half-ellipse arcs standing on the horizon, 6 bands bucket-filled red/orange/yellow/green/blue/purple; sun, two clouds (one under the arch), snail, tufts, flowers, birds.'}
json.dump(D, open('./peppa_rainbow_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa24\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa24.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_rainbow_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
