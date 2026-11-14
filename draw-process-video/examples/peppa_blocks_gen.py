#!/usr/bin/env python3
"""Peppa building blocks in the playroom (drawing-peppa-pig-25, 佩奇搭积木)."""
import json, math, random
from collections import Counter
from PIL import Image, ImageDraw
random.seed(25)
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
 ['wall', [255, 238, 196]], ['floor', [222, 170, 112]], ['wood', [160, 105, 60]], ['sky', [140, 200, 245]],
 ['bred', [235, 55, 55]], ['bblue', [60, 130, 225]], ['byellow', [255, 215, 50]], ['bgreen', [90, 190, 80]],
 ['borange', [255, 150, 40]], ['bpurple', [150, 90, 210]], ['roof', [255, 120, 180]], ['curtain', [250, 160, 90]],
]
assert len(pal) <= 22
MARK = {}
# ---------- 1. Peppa ----------
PS, PX, PY = 0.75, 70, 95
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

def rect(x0, y0, x1, y1):
    return S([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0), (x1, y0)], 0.03, 0.012)
# ---------- 2. Block tower 3-2-1 + roof + flag ----------
BW, BH, B = 120, 100, 655
ROW1 = [(640 + BW * i, B - BH, 640 + BW * (i + 1), B) for i in range(3)]
ROW2 = [(700 + BW * i, B - 2 * BH, 700 + BW * (i + 1), B - BH) for i in range(2)]
ROW3 = [(760, B - 3 * BH, 880, B - 2 * BH)]
RC1 = ['bred', 'bblue', 'byellow']; RC2 = ['bgreen', 'borange']; RC3 = ['bpurple']
out += [C('ink')]
for i, r in enumerate(ROW1):
    out.append(rect(*r)); out.append(P(0.35)); MARK['row1_%d' % i] = len(out)
out += [P(0.3)]
for i, r in enumerate(ROW2):
    out.append(rect(*r)); out.append(P(0.35)); MARK['row2_%d' % i] = len(out)
out += [P(0.3)]
out.append(rect(*ROW3[0])); MARK['row3'] = len(out)
RY = B - 3 * BH; APX = (820, RY - 110)
out.append(S([(745, RY), APX, (895, RY), (745, RY), APX], 0.03, 0.008)); MARK['roof_line'] = len(out)
FT = (820, APX[1] - 80)
out.append(S([APX, FT], 0.03, 0.008))
out.append(S([FT, (885, FT[1] + 20), (820, FT[1] + 40), FT, (885, FT[1] + 20)], 0.03, 0.008))
MARK['flag_line'] = len(out)
out += [P(0.8)]
MARK['tower_line'] = len(out)

# ---------- 3. Window + clock on the wall ----------
WX0, WY0, WX1, WY1 = 450, 60, 650, 250
WMX, WMY = (WX0 + WX1) / 2, (WY0 + WY1) / 2
out += [C('ink'), rect(WX0, WY0, WX1, WY1)]
out += [S([(WMX, WY0), (WMX, WY1)], 0.03, 0.008), S([(WX0, WMY), (WX1, WMY)], 0.03, 0.008)]
MARK['window_line'] = len(out)
CKX, CKY, CKR = 1170, 140, 62
out += [S(ell(CKX, CKY, CKR, CKR, 64, 4), 0.04, 0.008)]
MARK['clock_line'] = len(out)
def curtain(xo, xi):
    # xo outer edge, xi inner (wavy) edge
    pts = [(xo, WY0 - 12), (xi, WY0 - 12)]
    pts += [(xi + (6 if xi > xo else -6) * math.sin(k / 3.0), WY0 - 12 + (WY1 + 40 - WY0) * k / 24) for k in range(1, 25)]
    pts += [(xo, WY1 + 28), (xo, WY0 - 12), (xi, WY0 - 12)]
    return S(pts, 0.02, 0.012)
out += [curtain(WX0 - 62, WX0 - 14), curtain(WX1 + 62, WX1 + 14)]
MARK['curtain_line'] = len(out)
PF = (925, 70, 1060, 190)
out += [rect(*PF)]
HB = (965, 130, 1022, 178)
out += [S([(HB[0], HB[1]), (HB[0], HB[3]), (HB[2], HB[3]), (HB[2], HB[1])], 0.02, 0.012),
        S([(HB[0] - 12, HB[1]), (993.5, 92), (HB[2] + 12, HB[1]), (HB[0] - 12, HB[1]), (993.5, 92)], 0.02, 0.012)]
MARK['picture_line'] = len(out)
out += [P(0.8)]

# ---------- 4. Floor line (stops at Peppa and at the tower) + border ----------
pl = side(PS, PX, PY, GHY, False)
pr = side(PS, PX, PY, GHY, True)
TL, TR = ROW3[0][0], ROW3[0][2]
out += [C('wood')]
for a, b in [(2, pl[0]), (pr[0], TL + 2), (TR - 2, 1358)]:
    for dy in (0, 3, -2):
        out.append(S([(a, GHY + dy), (b, GHY + dy)], 0.05, 0.006))
MARK['floor_line'] = len(out)
out += [S([(2, GHY - 2), (2, 787)], 0.05, 0.009), S([(5, GHY - 2), (5, 787)], 0.05, 0.009),
        S([(1358, GHY - 2), (1358, 787)], 0.05, 0.009), S([(1355, GHY - 2), (1355, 787)], 0.05, 0.009),
        S([(2, 787), (1358, 787)], 0.05, 0.009), S([(2, 784), (1358, 784)], 0.05, 0.009),
        S([(2, 2), (1358, 2)], 0.05, 0.01), S([(2, 2), (2, GHY)], 0.05, 0.01),
        S([(1358, 2), (1358, GHY)], 0.05, 0.01)]
out += [dot(pl[0], GHY, 6), dot(pr[0], GHY, 6)]
out += [P(0.3)]
MARK['border_end'] = len(out)

def cen(r): return ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
def seeds(r):
    cx, cy = cen(r); return [(cx, cy), (cx - 30, cy - 22), (cx + 30, cy + 22)]
# ---------- 5. Block fills, one bucket per block ----------
for i, r in enumerate(ROW1):
    out += [C(RC1[i]), F(*seeds(r))]; MARK['fill_' + RC1[i]] = len(out)
for i, r in enumerate(ROW2):
    out += [C(RC2[i]), F(*seeds(r))]; MARK['fill_' + RC2[i]] = len(out)
out += [C(RC3[0]), F(*seeds(ROW3[0]))]; MARK['fill_bpurple'] = len(out)
out += [C('roof'), F((820, RY - 30), (800, RY - 18), (840, RY - 18))]; MARK['fill_roof'] = len(out)
out += [C('bred'), F((840, FT[1] + 20))]; MARK['fill_flag'] = len(out)
out += [P(0.4), C('curtain'), F((WX0 - 38, WMY), (WX0 - 38, WY0 + 20), (WX0 - 38, WY1 + 5)), F((WX1 + 38, WMY), (WX1 + 38, WY0 + 20), (WX1 + 38, WY1 + 5))]; MARK['fill_curtain'] = len(out)
out += [C('byellow'), F(((HB[0] + HB[2]) / 2, (HB[1] + HB[3]) / 2 + 4))]; MARK['fill_house'] = len(out)
out += [C('bred'), F((993.5, 118))]; MARK['fill_hroof'] = len(out)
out += [C('sky'), F((PF[0] + 18, PF[1] + 18), (PF[2] - 18, PF[1] + 18), (PF[0] + 18, PF[3] - 15), (PF[2] - 18, PF[3] - 15))]; MARK['fill_pic'] = len(out)
out += [P(0.4)]
out += [P(0.4)]
MARK['blocks_fill_end'] = len(out)

# ---------- 6. Loose toys on the floor: cube, triangle block, ball ----------
CUBE = (430, 625, 515, 705)
TRI = [(1040, 735), (1150, 735), (1095, 650)]
BALL = (1255, 640, 55)
out += [C('ink'), rect(*CUBE)]; MARK['cube_line'] = len(out)
out += [C('bblue'), F(cen(CUBE), (cen(CUBE)[0] - 18, cen(CUBE)[1] - 15))]; MARK['cube_fill'] = len(out)
out += [C('ink'), S(TRI + [TRI[0], TRI[1]], 0.03, 0.008)]; MARK['tri_line'] = len(out)
out += [C('borange'), F((1095, 708), (1080, 718), (1110, 718))]; MARK['tri_fill'] = len(out)
ARCH = (545, 680, 655, 760)
apts = [(625, 760), (655, 760), (655, 680), (545, 680), (545, 760), (575, 760)] + [(600 - 25 * math.cos(math.pi * k / 16), 760 - 28 * math.sin(math.pi * k / 16)) for k in range(17)]
out += [C('ink'), S(apts, 0.02, 0.012)]; MARK['arch_line'] = len(out)
out += [C('bgreen'), F((560, 705), (640, 705), (600, 695))]; MARK['arch_fill'] = len(out)
out += [C('ink'), S(ell(BALL[0], BALL[1], BALL[2], BALL[2], 64, 4), 0.03, 0.008)]; MARK['ball_line'] = len(out)
out += [C('byellow'), F((BALL[0], BALL[1]), (BALL[0] - 20, BALL[1] - 20), (BALL[0] + 20, BALL[1] + 20))]; MARK['ball_fill'] = len(out)
out += [P(0.4)]

def in_box(x, y, b, m=8): return b[0] - m < x < b[2] + m and b[1] - m < y < b[3] + m
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
TOWER = (ROW1[0][0], FT[1], ROW1[-1][2], B)
def in_tower(x, y):
    if not in_box(x, y, TOWER, 10): return False
    if y > ROW2[0][1] - 10: return in_box(x, y, (ROW1[0][0], ROW2[0][1], ROW1[-1][2], B), 10) and (y > ROW1[0][1] - 10 or in_box(x, y, (ROW2[0][0], ROW2[0][1], ROW2[-1][2], B)))
    if y > RY - 10: return in_box(x, y, ROW3[0], 10)
    return 735 < x < 905
WIN = (WX0, WY0, WX1, WY1)
def in_clock(x, y): return math.dist((x, y), (CKX, CKY)) < CKR + 10
def in_toys(x, y): return in_box(x, y, CUBE, 10) or in_box(x, y, (1040, 650, 1150, 735), 10) or math.dist((x, y), BALL[:2]) < BALL[2] + 10 or in_box(x, y, ARCH, 10)

# ---------- 7. Wall, window panes, floor ----------
WL = []
for x in range(28, 1360, 46):
    for y in range(22, GHY - 10, 34):
        if in_peppa(x, y) or in_tower(x, y) or in_box(x, y, (WX0 - 70, WY0 - 20, WX1 + 70, WY1 + 36), 10) or in_clock(x, y) or in_box(x, y, PF, 10): continue
        WL.append((x, y))
WL += [(body_r + 12, GHY - 14), (pr[0] + 14, GHY - 12), (TL - 20, GHY - 14), (TR + 20, GHY - 14), (740, RY - 8), (900, RY - 8)]
WL = [(x, y) for x, y in WL if y < GHY - 7]
out += [C('wall'), F(*WL)]; MARK['wall_fill'] = len(out)
PANES = [((WX0 + WMX) / 2, (WY0 + WMY) / 2), ((WMX + WX1) / 2, (WY0 + WMY) / 2), ((WX0 + WMX) / 2, (WMY + WY1) / 2), ((WMX + WX1) / 2, (WMY + WY1) / 2)]
out += [C('sky'), F(*PANES)]; MARK['sky_fill'] = len(out)
FLR = []
for x in range(25, 1360, 42):
    for y in range(GHY + 14, 785, 32):
        if in_peppa(x, y) or in_tower(x, y) or in_toys(x, y): continue
        FLR.append((x, y))
FLR += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), ((body_l + body_r) / 2, body_bot - 30), ((body_l + body_r) / 2 - 20, GHY + 30)]
out += [C('floor'), F(*FLR)]; MARK['floor_fill'] = len(out)
out += [P(0.4)]
MARK['fill_end'] = len(out)
out += [P(0.5)]

# ---------- 8. Details ----------
def letter_pts(ch, cx, cy, s=26):
    if ch == 'A': return [[(cx - s * .7, cy + s), (cx, cy - s), (cx + s * .7, cy + s)], [(cx - s * .38, cy + s * .2), (cx + s * .38, cy + s * .2)]]
    if ch == 'B':
        top = [(cx - s * .5, cy - s)] + [(cx + s * .05 + s * .45 * math.sin(math.pi * k / 12), cy - s * .5 - s * .5 * math.cos(math.pi * k / 12)) for k in range(13)] + [(cx - s * .5, cy)]
        bot = [(cx - s * .5, cy)] + [(cx + s * .1 + s * .5 * math.sin(math.pi * k / 12), cy + s * .5 - s * .5 * math.cos(math.pi * k / 12)) for k in range(13)] + [(cx - s * .5, cy + s)]
        return [[(cx - s * .5, cy + s), (cx - s * .5, cy - s)], top, bot]
    if ch == 'C': return [[(cx + s * .75 * math.cos(math.radians(a)), cy - s * math.sin(math.radians(a))) for a in range(40, 321, 8)]]
out += [C('white')]
for ch, r in zip('ABC', ROW1):
    cx, cy = cen(r)
    for pts in letter_pts(ch, cx, cy):
        out.append(S(pts, 0, 0.018))
    MARK['letter_' + ch] = len(out)
# star on orange, circle on green, heart on purple
g = cen(ROW2[0]); out.append(S(ell(g[0], g[1], 24, 24, 40, 3), 0, 0.012)); MARK['circle'] = len(out)
o_ = cen(ROW2[1]); st = []
for k in range(11):
    a = -math.pi / 2 + k * math.pi * 2 / 5 * 2 / 2
    rr = 28 if k % 2 == 0 else 12
    st.append((o_[0] + rr * math.cos(-math.pi / 2 + k * math.pi / 5), o_[1] + rr * math.sin(-math.pi / 2 + k * math.pi / 5)))
out.append(S(st, 0, 0.012)); MARK['star'] = len(out)
h = cen(ROW3[0]); ht = [(h[0] + 1.3 * 16 * math.sin(t) ** 3, h[1] - 1.3 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))) for t in [i * 2 * math.pi / 60 for i in range(62)]]
out.append(S([(x, y + 3) for x, y in ht], 0, 0.012)); MARK['heart'] = len(out)
out += [P(0.4)]
cx_, cy_ = cen(CUBE)
for dx, dy in ((-22, -22), (22, -22), (0, 0), (-22, 22), (22, 22)):
    out.append(dot(cx_ + dx, cy_ + dy, 6))
MARK['dice'] = len(out)
out += [P(0.4)]
# ball stripes
out += [C('bred'), S([(BALL[0] - 50, BALL[1] - 18), (BALL[0], BALL[1] - 30), (BALL[0] + 50, BALL[1] - 18)], 0, 0.012),
        S([(BALL[0] - 51, BALL[1] - 10), (BALL[0], BALL[1] - 22), (BALL[0] + 51, BALL[1] - 10)], 0, 0.012)]
out += [C('bblue'), S([(BALL[0] - 50, BALL[1] + 18), (BALL[0], BALL[1] + 30), (BALL[0] + 50, BALL[1] + 18)], 0, 0.012),
        S([(BALL[0] - 51, BALL[1] + 10), (BALL[0], BALL[1] + 22), (BALL[0] + 51, BALL[1] + 10)], 0, 0.012)]
MARK['ball_end'] = len(out)
out += [P(0.5)]
# clock hands + ticks
out += [C('ink'), S([(CKX, CKY), (CKX, CKY - 42)], 0, 0.012), S([(CKX, CKY), (CKX + 30, CKY + 8)], 0, 0.012), dot(CKX, CKY, 6)]
MARK['hands'] = len(out)
for a in range(0, 360, 90):
    out.append(dot(CKX + 48 * math.sin(math.radians(a)), CKY - 48 * math.cos(math.radians(a)), 4))
MARK['ticks'] = len(out)
out += [P(0.5)]
# window: cloud and bird in the panes
out += [C('white'), blob(WX0 + 52, WY0 + 42, 26, 13), blob(WX0 + 72, WY0 + 34, 18, 11)]
MARK['wcloud'] = len(out)
out += [C('ink'), S(cr([(WMX + 25, WMY + 45), (WMX + 35, WMY + 37), (WMX + 45, WMY + 45), (WMX + 55, WMY + 37), (WMX + 65, WMY + 45)], 5), 0, 0.01)]
MARK['wbird'] = len(out)
out += [P(0.5), C('byellow')]
def star(cx, cy, R=20, r=8):
    return S([(cx + (R if k % 2 == 0 else r) * math.cos(-math.pi / 2 + k * math.pi / 5), cy + (R if k % 2 == 0 else r) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(12)], 0, 0.014)
for sx, sy in ((770, 95), (1290, 300), (420, 320), (1110, 290), (860, 50), (1300, 60)):
    out.append(star(sx, sy))
MARK['wstars'] = len(out)
out += [P(0.5)]
# floorboards
out += [C('wood')]
fb = []
for y in (GHY + 70, GHY + 150, GHY + 230, GHY + 310):
    if y > 775: continue
    xs_ = [x for x in range(14, 1350, 4)]
    seg = []
    for x in xs_:
        ok = not (in_peppa(x, y) or in_tower(x, y) or in_toys(x, y))
        if ok: seg.append(x)
        elif seg:
            if seg[-1] - seg[0] > 40: fb.append((seg[0] + 6, seg[-1] - 6, y))
            seg = []
    if seg and seg[-1] - seg[0] > 40: fb.append((seg[0] + 6, seg[-1] - 6, y))
for a, b, y in fb:
    out.append(S([(a, y), (b, y)], 0.3, 0.016))
MARK['floorboards'] = len(out)
# little seams between boards (short verticals)
for a, b, y in fb:
    for x in range(int(a) + 90, int(b) - 30, 230):
        out.append(S([(x, y + 6), (x, y + 70)], 0.2, 0.012) if y + 74 < 784 and not any(in_peppa(x, yy) or in_tower(x, yy) or in_toys(x, yy) for yy in range(int(y), int(y) + 75, 5)) else P(0))
out = [o for o in out if not (o['op'] == 'pause' and o['s'] == 0)]
MARK['end'] = len(out)

# ---------- seed check (PIL simulation) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
LATE = set()
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'sky', 'bred', 'bblue', 'byellow', 'bgreen', 'borange', 'bpurple', 'roof', 'curtain'}
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
assert im.getpixel((10, 200)) == col['wall'], im.getpixel((10, 200))
assert im.getpixel((50, 760)) == col['floor'], im.getpixel((50, 760))
for r, cc_ in list(zip(ROW1, RC1)) + list(zip(ROW2, RC2)) + list(zip(ROW3, RC3)):
    q = im.getpixel((int(r[0] + 15), int(r[1] + 15))); assert q == col[cc_], (cc_, q)
assert im.getpixel((820, RY - 25)) == col['roof'], im.getpixel((820, RY - 25))
assert im.getpixel((int(PANES[3][0]), int(PANES[3][1]) - 30)) == col['sky']
assert im.getpixel((BALL[0] - 30, BALL[1])) == col['byellow']
assert im.getpixel((470, 690)) == col['bblue']
assert im.getpixel((1025, 600)) == col['floor'] and im.getpixel((700, 300)) == col['wall'], (im.getpixel((1025, 600)), im.getpixel((700, 300)))
print('estimate s', round(est(out), 1))

D = {'name': 'peppa-blocks', 'canvas': [1360, 790], 'palette': pal, 'ops': out, 'ui': E['ui'], 'marks': MARK,
     'notes': 'Peppa in the playroom building a 3-2-1 block tower (red/blue/yellow, green/orange, purple) with a pink roof and red flag; window with sky panes, wall clock, loose blue cube, orange triangle block, yellow ball; ABC letters, star, circle, heart, floorboards.'}
json.dump(D, open('./peppa_blocks_strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa25\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa25.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
import shutil; shutil.copy('./peppa_blocks_strokes.json', './strokes.json')
print(len(out), 'ops', len(pal), 'colors', MARK)
