#!/usr/bin/env python3
"""Peppa on a playground swing outdoors (drawing-peppa-pig-14).
Fills use paint-bucket seeds; large flats are never brush-painted."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(14)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = E['ops']; out = []
pal = [
 ['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
 ['white', [255, 255, 255]], ['shoe', [25, 20, 22]],
 ['sky', [140, 200, 245]], ['grass', [110, 185, 70]], ['dkgreen', [55, 120, 40]],
 ['sun', [255, 215, 60]], ['flower', [255, 130, 190]], ['flower2', [255, 170, 50]],
 ['wood', [160, 100, 55]], ['wood2', [120, 70, 40]], ['rope', [90, 70, 50]],
 ['seat', [185, 125, 70]],
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
    c = [p for p in P if abs(p[1] - y) < 14]
    if not c:
        c = sorted(P, key=lambda q: abs(q[1] - y))[:8]
    p = max(c, key=lambda q: q[0]) if right else min(c, key=lambda q: q[0])
    return [p[0] + (-6 if right else 6), p[1]]
def thick_seg(a, b, w=14):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w, dx / L * w
    return poly([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])

# Safe placement (verified no skin leak)
PS, PX, PY = 0.58, 400, 95
out += char(PS, PX, PY, 'dress')
out += [{'op': 'pause', 's': 0.4}]

xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']:
            q = T(p, PS, PX, PY); xs.append(q[0]); ys.append(q[1])
body_l, body_r = min(xs), max(xs)
head_top, body_bot = min(ys), max(ys)
pb = (body_l - 12, head_top - 12, body_r + 12, body_bot + 12)
print('peppa box', pb)

LH = T((320, 400), PS, PX, PY)
RH = T((620, 400), PS, PX, PY)
print('hands', LH, RH)

# A-frames left and right of Peppa
LA_PEAK = (180, 95)
LA_L = (70, 670)
LA_R = (300, 670)
RA_PEAK = (1180, 95)
RA_L = (1060, 670)
RA_R = (1300, 670)
BEAM_Y = 108
BEAM_L, BEAM_R = 180, 1180
shoe_y = T((469, 679), PS, PX, PY)[1]
SEAT_Y0, SEAT_Y1 = shoe_y - 28, shoe_y + 6  # tuck under dress hem
SEAT_X0 = body_l - 35
SEAT_X1 = body_r + 40
ROPE_LX = max(SEAT_X0 + 25, LH[0])
ROPE_RX = min(SEAT_X1 - 25, RH[0])
print('seat', SEAT_X0, SEAT_X1, SEAT_Y0, SEAT_Y1, 'ropes', ROPE_LX, ROPE_RX)

# Closed leg capsules from dress hem down onto the seat
LEG_TOP = T((469, 555), PS, PX, PY)[1]
print('LEG_TOP', LEG_TOP)
LLX = T((419, 600), PS, PX, PY)[0]
RLX = T((523, 600), PS, PX, PY)[0]
def leg_poly(cx, top, bot, half=18):
    return poly([(cx-half, top), (cx+half, top), (cx+half, bot), (cx-half, bot)])
out += [C('ink'),
        S(leg_poly(LLX, LEG_TOP, SEAT_Y0 + 8, 16), 0.05, 0.008),
        S(leg_poly(RLX, LEG_TOP, SEAT_Y0 + 8, 16), 0.05, 0.008)]
out += [C('skin'),
        F((LLX, (LEG_TOP+SEAT_Y0)/2), (LLX-6, (LEG_TOP+SEAT_Y0)/2), (LLX+6, (LEG_TOP+SEAT_Y0)/2),
          (LLX, LEG_TOP+10), (LLX, SEAT_Y0-5)),
        F((RLX, (LEG_TOP+SEAT_Y0)/2), (RLX-6, (LEG_TOP+SEAT_Y0)/2), (RLX+6, (LEG_TOP+SEAT_Y0)/2),
          (RLX, LEG_TOP+10), (RLX, SEAT_Y0-5))]

out += [C('ink')]
out += [S(thick_seg(LA_PEAK, LA_L, 14), 0.08, 0.009),
        S(thick_seg(LA_PEAK, LA_R, 14), 0.08, 0.009),
        S(thick_seg(RA_PEAK, RA_L, 14), 0.08, 0.009),
        S(thick_seg(RA_PEAK, RA_R, 14), 0.08, 0.009)]
out += [S(poly([(BEAM_L - 10, BEAM_Y - 11), (BEAM_R + 10, BEAM_Y - 11),
                (BEAM_R + 10, BEAM_Y + 13), (BEAM_L - 10, BEAM_Y + 13)]), 0.1, 0.009)]
out += [S([(LA_L[0] + 40, 540), (LA_R[0] - 40, 540)], 0.1, 0.01),
        S([(RA_L[0] + 40, 540), (RA_R[0] - 40, 540)], 0.1, 0.01)]

def rope_quad(x, y0, y1, w=5):
    return poly([(x - w, y0), (x + w, y0), (x + w, y1), (x - w, y1)])
out += [C('rope'),
        S(rope_quad(ROPE_LX, BEAM_Y + 13, SEAT_Y0, 4), 0.0, 0.008),
        S(rope_quad(ROPE_RX, BEAM_Y + 13, SEAT_Y0, 4), 0.0, 0.008),
        # center line so the thin quad reads as a solid rope
        S([(ROPE_LX, BEAM_Y + 13), (ROPE_LX, SEAT_Y0)], 0.0, 0.008),
        S([(ROPE_RX, BEAM_Y + 13), (ROPE_RX, SEAT_Y0)], 0.0, 0.008)]
out += [C('ink'),
        S(poly([(SEAT_X0, SEAT_Y0), (SEAT_X1, SEAT_Y0),
                (SEAT_X1, SEAT_Y1), (SEAT_X0, SEAT_Y1)]), 0.1, 0.009)]

# arms: use Peppa default pose; ropes hang beside hands

SUNX, SUNY, SUNR = 820, 75, 48
out += [C('ink'), S(ell(SUNX, SUNY, SUNR, SUNR, 64, 4), 0.05, 0.008)]
def cloud(cx, cy, sc):
    P = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        P.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(P + P[:3], 0.1, 0.008)
CLOUDS = [(450, 70, 0.75), (1050, 120, 0.9), (150, 100, 0.65)]
out += [cloud(*c) for c in CLOUDS]

dress_mid_y = T((469, 480), PS, PX, PY)[1]
GHY = int(dress_mid_y)
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
print('GHY', GHY, 'gap', pl[0], pr[0])

def ax_at_y(peak, foot, y):
    t = (y - peak[1]) / max(1e-6, (foot[1] - peak[1]))
    return peak[0] + (foot[0] - peak[0]) * t
la_l = ax_at_y(LA_PEAK, LA_L, GHY); la_r = ax_at_y(LA_PEAK, LA_R, GHY)
ra_l = ax_at_y(RA_PEAK, RA_L, GHY); ra_r = ax_at_y(RA_PEAK, RA_R, GHY)
m = 20
segs = [(2, la_l - m), (la_r + m, pl[0]), (pr[0], ra_l - m), (ra_r + m, 1358)]
print('horizon segs', segs)
out += [C('dkgreen')]
for a, b in segs:
    if b - a > 8:
        out.append(S([(a, GHY), (b, GHY)], 0.15, 0.01))
out += [S([(2, GHY), (2, 787)], 0.1, 0.01),
        S([(1358, GHY), (1358, 787)], 0.1, 0.01),
        S([(2, 787), (1358, 787)], 0.1, 0.01)]
out += [{'op': 'pause', 's': 0.35}]

def seed_along(a, b, fracs=(0.25, 0.4, 0.55, 0.7, 0.85)):
    return [((a[0] + (b[0] - a[0]) * f), (a[1] + (b[1] - a[1]) * f)) for f in fracs]
def near_leg(x, y, peak, foot, tol=24):
    ax, ay = peak; bx, by = foot
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
    px, py = ax + t * dx, ay + t * dy
    return (x - px) ** 2 + (y - py) ** 2 < tol * tol

out += [C('wood')]
for a, b in [(LA_PEAK, LA_L), (LA_PEAK, LA_R), (RA_PEAK, RA_L), (RA_PEAK, RA_R)]:
    out.append(F(*seed_along(a, b)))
out += [C('wood2'), F(*[(x, BEAM_Y) for x in range(260, 1150, 70)] +
                        [(480, BEAM_Y + 2), (700, BEAM_Y - 2), (950, BEAM_Y + 1)])]
# ropes stay as ink strokes (too thin to bucket-fill reliably)

seat_seeds = []
for x in range(int(SEAT_X0) + 10, int(SEAT_X1) - 6, 18):
    for y in (SEAT_Y0 + 5, SEAT_Y1 - 5, (SEAT_Y0 + SEAT_Y1) / 2):
        # only skip shoe dots
        if (abs(x-LLX)<22 or abs(x-RLX)<22) and y > SEAT_Y0 + 8:
            continue
        seat_seeds.append((x, y))
seat_seeds += [(SEAT_X0 + 12, SEAT_Y0 + 4), (SEAT_X1 - 12, SEAT_Y0 + 4),
               (SEAT_X0 + 12, SEAT_Y1 - 4), (SEAT_X1 - 12, SEAT_Y1 - 4)]
out += [C('seat'), F(*seat_seeds)]

G = []
for x in range(25, 1360, 44):
    for y in range(GHY + 16, 790, 34):
        if body_l - 6 < x < body_r + 6 and head_top - 4 < y < SEAT_Y0 - 2:
            continue  # skip body above seat; allow grass under seat
        if SEAT_X0 - 3 < x < SEAT_X1 + 3 and SEAT_Y0 - 3 < y < SEAT_Y1 + 3:
            continue
        if any(near_leg(x, y, p, f) for p, f in
               [(LA_PEAK, LA_L), (LA_PEAK, LA_R), (RA_PEAK, RA_L), (RA_PEAK, RA_R)]):
            continue
        G.append((x, y))
G += [(60, 720), (200, 750), (400, 730), (580, 760), (750, 740), (880, 755),
      (1020, 730), (1160, 760), (1280, 730), (1320, 760), (100, 680), (300, 700),
      (500, 690), (920, 700), (1080, 690), (70, 780), (420, 780), (650, 700),
      (130, 640), (230, 640), (340, 640), (1120, 640), (1220, 640)]
# under-seat / beside-legs grass pockets (were left white in recording)
# beside/between legs above the seat (below horizon → grass)
for y in range(int(max(GHY + 8, LEG_TOP - 5)), int(SEAT_Y0) + 4, 10):
    for x in range(int(body_l + 5), int(body_r - 5), 12):
        # skip interior of leg capsules
        if abs(x - LLX) < 18 or abs(x - RLX) < 18:
            continue
        G.append((x, y))
# also force a few known pocket seeds from QA
for x,y in [(450,420),(450,430),(580,420),(580,430),(500,420),(520,425),
            (430,415),(600,415),(470,410),(550,410)]:
    G.append((x,y))

for x in range(int(SEAT_X0) - 10, int(SEAT_X1) + 15, 18):
    G.append((x, SEAT_Y1 + 14))
    G.append((x, SEAT_Y1 + 28))
    G.append((x, SEAT_Y1 + 48))
for x in (body_l - 20, body_l - 8, body_r + 8, body_r + 20):
    for y in range(int(SEAT_Y0) - 30, int(SEAT_Y1) + 60, 16):
        G.append((x, y))

out += [C('grass'), F(*G)]

out += [C('sun'), F((SUNX, SUNY), (SUNX - 14, SUNY), (SUNX + 14, SUNY),
                    (SUNX, SUNY - 14), (SUNX, SUNY + 14))]

SKY = []
for x in range(28, 1360, 50):
    for y in range(22, GHY - 12, 36):
        if body_l - 4 < x < body_r + 4 and head_top - 4 < y < GHY + 4:
            continue
        if any(abs(x - a) < 95 * k and abs(y - b) < 48 * k for a, b, k in CLOUDS):
            continue
        if abs(x - SUNX) < SUNR + 22 and abs(y - SUNY) < SUNR + 22:
            continue
        if any(near_leg(x, y, p, f, 26) for p, f in
               [(LA_PEAK, LA_L), (LA_PEAK, LA_R), (RA_PEAK, RA_L), (RA_PEAK, RA_R)]):
            continue
        if BEAM_L - 14 < x < BEAM_R + 14 and BEAM_Y - 16 < y < BEAM_Y + 16:
            continue
        if abs(x - ROPE_LX) < 9 and BEAM_Y < y < SEAT_Y0:
            continue
        if abs(x - ROPE_RX) < 9 and BEAM_Y < y < SEAT_Y0:
            continue
        SKY.append((x, y))
# pocket between ropes above head
for y in range(int(BEAM_Y + 22), int(head_top - 4), 24):
    for x in range(int(ROPE_LX + 14), int(ROPE_RX - 10), 30):
        SKY.append((x, y))
for y in range(int(head_top), GHY - 8, 28):
    SKY.append((body_l - 30, y))
    SKY.append((body_r + 30, y))
# force-fill known rope-corridor pockets around Peppa
for y in range(int(BEAM_Y + 20), int(GHY - 5), 18):
    for x in (int(ROPE_LX + 20), int((ROPE_LX + ROPE_RX) / 2), int(ROPE_RX - 20)):
        if not (body_l + 15 < x < body_r - 15 and head_top + 10 < y < body_bot - 20):
            SKY.append((x, y))
for x,y in [(430,130),(450,130),(470,130),(490,130),(510,130),(530,130),(550,130),
            (430,160),(500,160),(560,160),(430,200),(500,200),(560,200),
            (430,240),(500,240),(560,240),(430,280),(560,280),(430,320),(560,320),
            (400,140),(400,200),(400,260),(620,140),(620,200),(620,260)]:
    SKY.append((x,y))
SKY += [(40, 200), (40, 300), (520, 40), (620, 240), (900, 40), (1140, 55),
        (1300, 220), (1300, 320), (200, 250), (70, GHY - 30),
        (340, 200), (1080, 250), (740, 200), (960, 280)]
out += [C('sky'), F(*SKY)]
out += [{'op': 'pause', 's': 0.4}]

out += [C('sun')]
for k in range(10):
    a = 2 * math.pi * k / 10
    out.append(S([(SUNX + (SUNR + 10) * math.cos(a), SUNY + (SUNR + 10) * math.sin(a)),
                  (SUNX + (SUNR + 30) * math.cos(a), SUNY + (SUNR + 30) * math.sin(a))], 0, 0.008))
out += [C('rope')]
for y in range(int(BEAM_Y + 28), int(SEAT_Y0 - 12), 26):
    out.append(S([(ROPE_LX - 5, y), (ROPE_LX + 5, y + 3)], 0.05, 0.008))
    out.append(S([(ROPE_RX - 5, y), (ROPE_RX + 5, y + 3)], 0.05, 0.008))
out += [C('ink')]
for x in range(int(BEAM_L) + 40, int(BEAM_R) - 20, 75):
    out.append(S([(x, BEAM_Y - 5), (x + 16, BEAM_Y + 5)], 0.05, 0.008))
out += [C('dkgreen')]
for x, y in [(50, GHY + 55), (190, GHY + 70), (310, 735), (550, 750), (720, 735),
             (870, 755), (1030, 730), (1180, 745), (1300, GHY + 50), (90, 705),
             (470, 695), (960, 695), (150, 765), (650, 720)]:
    if body_l < x < body_r and y < body_bot + 10:
        continue
    if any(near_leg(x, y, p, f, 30) for p, f in
           [(LA_PEAK, LA_L), (LA_PEAK, LA_R), (RA_PEAK, RA_L), (RA_PEAK, RA_R)]):
        continue
    for dx in (-10, 0, 10):
        out.append(S([(x, y + 14), (x + dx, y)], 0.2))
for (x, y, fc) in [(85, 665, 'flower'), (270, 735, 'flower2'), (500, 715, 'flower'),
                   (760, 725, 'flower2'), (1000, 705, 'flower'), (1260, 715, 'flower'),
                   (600, 760, 'flower2'), (1330, 675, 'flower'), (170, 705, 'flower')]:
    if body_l < x < body_r and head_top < y < body_bot:
        continue
    if any(near_leg(x, y, p, f, 32) for p, f in
           [(LA_PEAK, LA_L), (LA_PEAK, LA_R), (RA_PEAK, RA_L), (RA_PEAK, RA_R)]):
        continue
    out += [C(fc)] + [dot(x + 8 * math.cos(2 * math.pi * k / 5), y + 8 * math.sin(2 * math.pi * k / 5), 5)
                      for k in range(5)] + [C('sun'), dot(x, y, 4)]
out += [C('ink')]
for x, y in [(560, 48), (920, 62), (1120, 46)]:
    out.append(S(cr([(x - 16, y), (x - 8, y - 7), (x, y), (x + 8, y - 7), (x + 16, y)], 5), 0, 0.008))

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
                # probe flood on copy for leak guard on character fills
                if o_c in ('skin', 'dress', 'cheek', 'shoe', 'wood', 'wood2', 'rope', 'seat', 'sun'):
                    probe = im.copy()
                    ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc)
                    # character parts must stay small; wood legs ~few tens of k
                    limit = 60000 if o_c in ('skin', 'dress', 'cheek', 'shoe') else 120000
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

D = {'name': 'peppa-swing', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'],
     'notes': 'Peppa on a playground swing outdoors: wooden A-frame swing set, ropes, seat, sun, clouds, grass, flowers. Horizon stops at dress and A-frame legs. Bucket fills.'}
json.dump(D, open('./peppa_swing_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa14\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa14.gpl', 'w').write(gpl)
open('./peppa.gpl', 'w').write(gpl)
print(len(out), 'ops', len(pal), 'colors')
