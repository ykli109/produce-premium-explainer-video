#!/usr/bin/env python3
"""Peppa watching the little train (drawing-peppa-pig-28, 佩奇看火车)."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(28)
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

from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['loco', [50, 110, 210]], ['cab', [230, 50, 45]], ['car1', [255, 150, 40]],
 ['car2', [150, 90, 210]], ['roof', [120, 72, 52]], ['wheel', [70, 70, 80]], ['window', [255, 238, 150]],
 ['smoke', [215, 215, 222]], ['rail', [140, 95, 60]], ['pink', [255, 140, 200]], ['gold', [255, 200, 40]],
]
assert len(pal) <= 22
MARK = {}
# ---------- 1. Peppa (waving) ----------
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
def rect(x0, y0, x1, y1, dl=0.012):
    return S([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0), (x1, y0)], 0.03, dl)
B = 590  # train floor line
# ---------- 2. Locomotive ----------
out += [C('ink')]
BO = (600, 500, 780, B)
out += [rect(*BO)]
MARK['boiler'] = len(out)
out += [S([(634, 500), (628, 452), (680, 452), (674, 500)], 0.02, 0.012)]
MARK['chimney'] = len(out)
CW = [(600, 548), (600, B), (562, B), (600, 548)]
out += [S(CW + [CW[1]], 0.02, 0.012)]
MARK['cowcatcher'] = len(out)
CAB = (780, 420, 900, B)
out += [rect(*CAB)]
MARK['cab'] = len(out)
CR = (768, 398, 912, 420)
out += [rect(*CR)]
MARK['cab_roof'] = len(out)
CWIN = (806, 446, 874, 502)
out += [rect(*CWIN)]
MARK['cab_window'] = len(out)
out += [P(0.3)]
# ---------- 3. Two carriages ----------
CARS = [(935, 1105), (1140, 1310)]
CT = 410
WINS = []
for i, (x0, x1) in enumerate(CARS):
    out += [rect(x0, CT, x1, B)]
    MARK['car%d_body' % i] = len(out)
    out += [rect(x0 - 10, CT - 22, x1 + 10, CT)]
    MARK['car%d_roof' % i] = len(out)
    ws = [(x0 + 20, 448, x0 + 76, 506), (x1 - 76, 448, x1 - 20, 506)]
    for w in ws: out += [rect(*w)]
    WINS += ws
    MARK['car%d_windows' % i] = len(out)
    out += [P(0.2)]
# ---------- 4. Wheels ----------
WR, WCY = 22, B + 18
WX = [640, 740, 815, 870, 975, 1065, 1180, 1270]
for x in WX:
    out += [S(ell(x, WCY, WR, WR, 56, 4), 0, 0.009)]
MARK['wheels'] = len(out)
out += [P(0.3)]
# ---------- 5. Smoke puffs ----------
SM = [(662, 392, 0.40), (712, 322, 0.52), (782, 246, 0.64)]
for cx, cy, sc in SM: out.append(cloud(cx, cy, sc))
MARK['smoke'] = len(out)
out += [P(0.3)]
# ---------- 6. Sun + clouds ----------
SUX, SUY, SUR = 1225, 104, 44
out += [S(ell(SUX, SUY, SUR, SUR, 64, 4), 0.03, 0.008)]
MARK['sun_line'] = len(out)
CL = [(470, 92, 0.62), (985, 120, 0.85)]
for cx, cy, sc in CL: out.append(cloud(cx, cy, sc))
MARK['clouds'] = len(out)
out += [P(0.3)]
# ---------- 7. Horizon (stops at dress, cab, carriages) + border ----------
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
out += [C('dkgreen')]
SEG = [(2, pl[0]), (pr[0], CAB[0] + 2), (CAB[2] - 2, CARS[0][0] + 2), (CARS[0][1] - 2, CARS[1][0] + 2), (CARS[1][1] - 2, 1358)]
for a, b in SEG:
    for dy in (0, 3):
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
# ---------- 8. Fills (paint bucket) ----------
out += [C('loco'), F((690, 545), (620, 520), (760, 570), (720, 515))]
MARK['boiler_fill'] = len(out)
out += [C('shoe'), F((654, 476), (654, 490))]
MARK['chimney_fill'] = len(out)
out += [C('cab'), F((589, 578), (592, 570))]
MARK['cow_fill'] = len(out)
out += [C('cab'), F((840, 548), (795, 570), (885, 570), (840, 432), (792, 470), (888, 470))]
MARK['cab_fill'] = len(out)
out += [C('roof'), F((840, 409), (790, 409), (890, 409))]
MARK['cab_roof_fill'] = len(out)
out += [C('car1'), F(*[((CARS[0][0] + CARS[0][1]) / 2, y) for y in (430, 480, 545)] + [(CARS[0][0] + 14, 560), (CARS[0][1] - 14, 560)])]
MARK['car0_fill'] = len(out)
out += [C('car2'), F(*[((CARS[1][0] + CARS[1][1]) / 2, y) for y in (430, 480, 545)] + [(CARS[1][0] + 14, 560), (CARS[1][1] - 14, 560)])]
MARK['car1_fill'] = len(out)
out += [C('roof'), F(*[(x, CT - 11) for x0, x1 in CARS for x in ((x0 + x1) / 2, x0 + 20, x1 - 20)])]
MARK['car_roof_fill'] = len(out)
out += [C('window'), F(((CWIN[0] + CWIN[2]) / 2, (CWIN[1] + CWIN[3]) / 2), *[((w[0] + w[2]) / 2, (w[1] + w[3]) / 2) for w in WINS])]
MARK['window_fill'] = len(out)
out += [C('wheel'), F(*[(x, WCY + 6) for x in WX])]
MARK['wheel_fill'] = len(out)
out += [C('smoke'), F(*[(cx, cy) for cx, cy, sc in SM] + [(cx - 30 * sc, cy) for cx, cy, sc in SM] + [(cx + 30 * sc, cy) for cx, cy, sc in SM])]
MARK['smoke_fill'] = len(out)
out += [C('sun'), F((SUX, SUY), (SUX - 20, SUY + 10))]
MARK['sun_fill'] = len(out)
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_train(x, y): return 550 < x < 1322 and 380 < y < WCY + WR + 12
def in_chim(x, y): return 615 < x < 692 and 440 < y < 505
def in_sun(x, y): return (x - SUX) ** 2 + (y - SUY) ** 2 < (SUR + 12) ** 2
def in_cloud(x, y): return any(abs(x - cx) < 100 * sc and abs(y - cy) < 52 * sc for cx, cy, sc in CL + SM)
SKY = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 12, 32):
        if in_peppa(x, y) or in_train(x, y) or in_chim(x, y) or in_sun(x, y) or in_cloud(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (body_l - 20, GHY - 14), (CAB[0] - 14, GHY - 12), (CAB[2] + 16, GHY - 8), (CARS[0][1] + 16, GHY - 8),
        (CARS[1][1] + 24, GHY - 10), (CARS[0][0] - 16, GHY - 8), (CARS[1][0] - 16, GHY - 8)]
SKY = [(x, y) for x, y in SKY if y < GHY - 7]
out += [C('sky'), F(*SKY)]
MARK['sky_fill'] = len(out)
G = []
for x in range(25, 1360, 40):
    for y in range(GHY + 14, 790, 30):
        if in_peppa(x, y) or in_train(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), (body_l + 30, body_bot + 25), ((body_l + body_r) / 2, body_bot - 30),
      (CAB[2] + 17, 520), (CARS[0][1] + 17, 520), (CARS[0][1] + 17, 600), (CAB[2] + 17, 600), (690, 615), (900, 640), (1120, 640), (1340, 520), (560, 520)]
out += [C('grass'), F(*G)]
MARK['grass_fill'] = len(out)
out += [P(0.4)]
MARK['fill_end'] = len(out)
# ---------- 9. Rails and sleepers ----------
RY = WCY + WR + 3
out += [C('rail')]
out += [S([(2, RY), (1358, RY)], 0.03, 0.006)]
MARK['rail_top'] = len(out)
out += [S([(2, RY + 18), (1358, RY + 18)], 0.03, 0.006)]
MARK['rail_bottom'] = len(out)
for x in range(40, 1358, 64):
    out.append(S([(x, RY + 2), (x - 6, RY + 18)], 0, 0.01))
MARK['sleepers'] = len(out)
# ---------- 10. Train details ----------
out += [C('ink')]
for x0, x1 in [(CAB[2], CARS[0][0]), (CARS[0][1], CARS[1][0])]:
    out.append(S([(x0, 570), (x1, 570)], 0, 0.012))
MARK['couplings'] = len(out)
out += [C('gold')]
for x in (660, 720):
    out.append(S([(x, 504), (x, B - 4)], 0, 0.011))
MARK['boiler_bands'] = len(out)
out += [dot(612, 522, 9)]
MARK['headlight'] = len(out)
out += [S([(634, 452), (628, 446), (680, 446), (674, 452)], 0, 0.011)]
MARK['chimney_rim'] = len(out)
out += [C('ink'), S([(640, WCY), (740, WCY)], 0, 0.012), S([(815, WCY), (870, WCY)], 0, 0.012)]
MARK['rods'] = len(out)
out += [C('white')] + [S(ell(x, WCY, 5, 5, 20, 1) + ell(x, WCY, 2, 2, 10, 1), 0, 0.006) for x in WX]
MARK['hubs'] = len(out)
out += [C('white')]
for x0, x1 in CARS:
    out.append(S([(x0 + 14, 530), (x1 - 14, 530)], 0, 0.009))
MARK['car_stripes'] = len(out)
# ---------- 11. Sun rays ----------
out += [C('sun')]
for k in range(12):
    a = 2 * math.pi * k / 12 + 0.13
    out.append(S([(SUX + (SUR + 12) * math.cos(a), SUY + (SUR + 12) * math.sin(a)), (SUX + (SUR + 34) * math.cos(a), SUY + (SUR + 34) * math.sin(a))], 0, 0.011))
MARK['sun_rays'] = len(out)
# ---------- 12. Birds ----------
out += [C('ink')]
for bx, by in [(560, 200), (610, 170), (1080, 230)]:
    out.append(S(cr([(bx - 18, by - 4), (bx - 9, by - 10), (bx, by)], 6) + cr([(bx, by), (bx + 9, by - 10), (bx + 18, by - 4)], 6), 0, 0.01))
MARK['birds'] = len(out)
# ---------- 13. Tufts, flowers ----------
def busy(x, y):
    return in_peppa(x, y) or in_train(x, y) or RY - 10 < y < RY + 30
out += [C('dkgreen')]
TUFT = [(45, GHY + 50), (60, 700), (400, 520), (520, 470), (640, 740), (1060, 740), (1300, 700), (1200, 470)]
for x, y in TUFT:
    if busy(x, y): continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
MARK['tufts_end'] = len(out)
FL = [(250, 712, 'pink'), (860, 735, 'sun')]
fl_marks = []
for (x, y, fc) in FL:
    if busy(x, y): print('skip flower', x, y); continue
    out += [C('dkgreen'), S([(x, y + 22), (x, y + 6)], 0.1, 0.008)]
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5) for k in range(5)] + [C('white' if fc != 'sun' else 'car1'), dot(x, y, 4)]
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
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'loco', 'cab', 'car1', 'car2', 'roof', 'window', 'wheel', 'smoke', 'sun'}
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
A_ = [((10, 200), 'sky'), ((50, 760), 'grass'), ((690, 545), 'loco'), ((654, 480), 'shoe'), ((840, 548), 'cab'), ((840, 409), 'roof'),
      ((840, 474), 'window'), ((1020, 560), 'car1'), ((1225, 560), 'car2'), ((640, WCY + 10), 'wheel'), ((712, 322), 'smoke'), ((SUX, SUY + 20), 'sun'),
      ((985, 120), 'white'), ((700, 470), 'grass'), ((918, 520), 'grass'), ((1122, 520), 'grass'), ((1340, 520), 'grass'), ((918, 412), 'sky')]
for (x, y), c in A_: assert im.getpixel((x, y)) == col[c], ((x, y), c, im.getpixel((x, y)))
D = {'name': 'peppa-train', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa waving at a little steam train: blue boiler with chimney and cowcatcher, red cab with roof and window, orange and purple carriages with brown roofs and windows, eight wheels; three smoke puffs, sun, two clouds; horizon stops at the dress, cab and both carriages; bucket fills per object then sky and grass seed grids; then rails and sleepers, couplings, boiler bands, headlight, hubs, rods, stripes, sun rays, birds, tufts and flowers.'}
json.dump(D, open('./peppa_train_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa28\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa28.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_train_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
