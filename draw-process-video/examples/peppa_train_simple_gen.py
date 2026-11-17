#!/usr/bin/env python3
"""佩奇看火车 v2 (drawing-peppa-pig-28, same-id replacement 2026-11-17): LOW-DIFFICULTY scene drawn with
human pacing and 4 real mistakes+corrections. Peppa + engine (boiler, chimney, cab) + ONE carriage,
4 big wheels, 2 smoke puffs, sun, one cloud, horizon/border, one rail, hubs, 8 rays, 3 tufts."""
import json, math, random, sys
from collections import Counter
from PIL import Image, ImageDraw
sys.path.insert(0, '/workspace/produce-premium-explainer-video/draw-process-video/scripts')
from stroke_geom import played_path, scrub
random.seed(28)
E = json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops = [dict(o) for o in E['ops']]
out = []; MARK = {}
# speeds px/s: FAST long simple lines, MED outlines, SLOW careful details
FAST, MED, SLOW, TINY = 760, 360, 190, 150
def S(pts, amp=1.0, speed=MED, smooth=True, **kw):
    d = {'op': 'stroke', 'amp': amp, 'speed': speed, 'pts': [[round(x, 1), round(y, 1)] for x, y in pts]}
    if not smooth: d['smooth'] = False
    d.update(kw); return d
def C(c): return {'op': 'color', 'c': c}
def F(*seeds): return {'op': 'fill', 'seeds': [list(x) for x in seeds]}
def P(s): return {'op': 'pause', 's': s}
def H(s, to=None):
    d = {'op': 'hover', 's': s}
    if to: d['to'] = [round(to[0], 1), round(to[1], 1)]
    return d
def UNDO(): return {'op': 'undo'}
def ERASE(box, pitch=9, speed=420, pad=6): return {"op": "erase", "pts": [[round(x, 1), round(y, 1)] for x, y in scrub(box, pitch, pad)], 'speed': speed}
def ell(cx, cy, rx, ry, n=72, extra=4, rot=0, a0=0):
    ca, sa = math.cos(rot), math.sin(rot); r = []
    for k in range(n + extra):
        a = a0 + 2 * math.pi * k / n; x, y = rx * math.cos(a), ry * math.sin(a)
        r.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return r
def dot(cx, cy, r, speed=TINY):
    pts = []
    for rr in [r, r * .66, r * .33, 1]: pts += ell(cx, cy, rr, rr, 24, 1)
    return S(pts, 0, speed, smooth=False)
def cloud(cx, cy, sc, speed=MED):
    Pc = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        b = 1 + 0.18 * abs(math.sin(2.5 * a)) if math.sin(a) < 0.2 else 1
        Pc.append((cx + 80 * sc * b * math.cos(a), cy + 36 * sc * b * math.sin(a)))
    return S(Pc + Pc[:3], 0.3, speed)
def rect(x0, y0, x1, y1, speed=MED):
    return S([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0), (x1, y0)], 0.6, speed)

pal = [['ink', [40, 30, 32]], ['dress', [214, 38, 48]], ['skin', [247, 172, 196]], ['cheek', [236, 120, 155]],
       ['white', [255, 255, 255]], ['shoe', [25, 20, 22]], ['sky', [140, 200, 245]], ['grass', [110, 185, 70]],
       ['dkgreen', [55, 120, 40]], ['sun', [255, 215, 60]], ['loco', [50, 110, 210]], ['cab', [230, 50, 45]],
       ['car', [255, 150, 40]], ['smoke', [215, 215, 222]], ['rail', [140, 95, 60]]]
# ---------- 1. Peppa ----------
PS, PX, PY = 0.70, 70, 150
def T(p): return [round(PX + (p[0] - 289) * PS, 1), round(PY + (p[1] - 40) * PS, 1)]
PEPPA_SPEED = {1: MED, 2: SLOW, 3: TINY, 4: TINY, 5: SLOW, 6: TINY, 7: SLOW, 8: TINY, 9: SLOW, 10: MED, 11: MED, 12: MED,
               13: FAST, 14: FAST, 15: FAST, 16: FAST, 17: FAST, 18: FAST, 19: TINY, 20: TINY, 21: TINY, 22: TINY,
               23: FAST, 24: FAST, 25: FAST, 26: FAST, 27: FAST, 28: FAST, 29: SLOW, 30: SLOW,
               34: FAST, 35: FAST, 36: FAST, 37: FAST, 39: 520}
for i, o in enumerate(ops[:44]):
    o = dict(o)
    if o['op'] == 'stroke':
        sm = o.get('amp', 1) > 0 and len(o['pts']) > 6
        st = S([T(p) for p in o['pts']], min(o.get('amp', 1.0), 0.8), PEPPA_SPEED.get(i, MED), smooth=sm)
        if i == 5: out += [H(0.9, T((526, 120)))]                      # think before the eyes
        if i == 7:                                                     # MISTAKE 1: second eye too low on the snout
            wrong = [[p[0] - 110, p[1] + 80] for p in o['pts']]; wp = [T(p) for p in wrong]
            out += [S(wp, 0.5, SLOW, smooth=True, wrong=True)]; MARK['m1_wrong'] = len(out)
            out += [H(1.0)]
            xs = [p[0] for p in wp]; ys = [p[1] for p in wp]
            out += [ERASE((min(xs) - 5, min(ys) - 5, max(xs) + 5, max(ys) + 5), 8, 260, 0)]; MARK['m1_erase'] = len(out)
            wpup = [[p[0] - 110, p[1] + 80] for p in ops[8]['pts']]
            out[-3:-2] = [out[-3], S([T(p) for p in wpup], 0, TINY, smooth=False, wrong=True)]   # its pupil too
            MARK['m1_wrong'] = len(out) - 2
            out += [H(0.6, T((576, 108)))]
        if i in (19, 29): out += [H(0.6, st['pts'][0])]
        out.append(st)
        if i == 1: MARK['head'] = len(out)
        if i == 8: MARK['eyes'] = len(out)
        if i == 11: MARK['ears'] = len(out)
        if i == 12: MARK['dress'] = len(out)
        if i == 22: MARK['arms'] = len(out)
        if i == 30: MARK['legs'] = len(out)
        continue
    if o['op'] == 'fill' and o['seeds'][0][1] > 600:      # shoes: concentric strokes (too small to bucket)
        for cx in (419, 523):
            pts = []
            for f in (0.75, 0.5, 0.25):
                pts += [T((cx + 30 * f * math.cos(2 * math.pi * k / 30), 679 + 12 * f * math.sin(2 * math.pi * k / 30))) for k in range(31)]
            out.append(S(pts, 0, 240, smooth=False))
        continue
    if o['op'] == 'fill': o['seeds'] = [T(p) for p in o['seeds']]
    out.append(o)
    if o['op'] == 'fill' and o['seeds'] and i == 33: MARK['skin_fill'] = len(out)
MARK['peppa_end'] = len(out)
out += [P(0.4)]
xs, ys = [], []
for o in ops[:44]:
    if o['op'] == 'stroke':
        for p in o['pts']: q = T(p); xs.append(q[0]); ys.append(q[1])
body_l, body_r, head_top, body_bot = min(xs), max(xs), min(ys), max(ys)
GHY = int(T((469, 480))[1]); print('peppa box', round(body_l), round(head_top), round(body_r), round(body_bot), 'GHY', GHY)
def side(y, right):
    Pd = [T(p) for p in ops[12]['pts']]
    c = [p for p in Pd if abs(p[1] - y) < 14] or sorted(Pd, key=lambda q: abs(q[1] - y))[:8]
    p = max(c, key=lambda q: q[0]) if right else min(c, key=lambda q: q[0])
    return [p[0] + (-6 if right else 6), p[1]]
# ---------- 2. Engine ----------
B = 590
BO = (470, 480, 700, B); CAB = (700, 390, 840, B); CR = (688, 366, 852, 390); CWIN = (735, 420, 805, 488)
CH_ = (515, 420, 565, 480)
out += [C('ink'), H(0.8, (BO[0], BO[1])), rect(*BO, speed=360)]; MARK['boiler'] = len(out)
# MISTAKE 2: chimney too tall and leaning -> Undo button -> redraw
out += [H(0.7, (CH_[0], CH_[3])), S([(CH_[0], CH_[3]), (CH_[0] + 22, CH_[1] - 70), (CH_[2] + 30, CH_[1] - 66), (CH_[2], CH_[3])], 0.4, 240, wrong=True)]
MARK['m2_wrong'] = len(out)
out += [H(1.1), UNDO()]; MARK['m2_undo'] = len(out)
out += [H(0.6, (CH_[0], CH_[3])), S([(CH_[0], CH_[3]), (CH_[0] - 4, CH_[1]), (CH_[2] + 4, CH_[1]), (CH_[2], CH_[3])], 0.4, 220)]
MARK['chimney'] = len(out)
out += [rect(*CAB, speed=360)]; MARK['cab'] = len(out)
out += [rect(*CR, speed=300)]; MARK['cab_roof'] = len(out)
out += [H(0.5, (CWIN[0], CWIN[1])), rect(*CWIN, speed=230)]; MARK['cab_window'] = len(out)
out += [P(0.3)]
# ---------- 3. One carriage ----------
CAR = (890, 420, 1250, B); CROOF = (878, 396, 1262, 420)
W1 = (930, 450, 1030, 522); W2 = (1110, 450, 1210, 522)
out += [rect(*CAR, speed=380)]; MARK['car_body'] = len(out)
out += [rect(*CROOF, speed=320)]; MARK['car_roof'] = len(out)
out += [H(0.5, (W1[0], W1[1])), rect(*W1, speed=230), rect(*W2, speed=230)]; MARK['car_windows'] = len(out)
out += [S([(CAB[2], 560), (CAR[0], 560)], 0.2, 200)]; MARK['coupling'] = len(out)
# ---------- 4. Four big wheels (slow, careful) ----------
WR, WCY = 30, B + 16
WX = [545, 640, 770, 1000, 1150][:0] or [550, 650, 1000, 1150]
WX = [560, 770, 990, 1150]
out += [H(1.0, (WX[0] + WR, WCY))]
for x in WX:
    out += [S(ell(x, WCY, WR, WR, 72, 6), 0.4, SLOW)]
    MARK.setdefault('wheel_each', []).append(len(out))
MARK['wheels'] = len(out)
out += [P(0.3)]
# ---------- 5. Smoke: MISTAKE 3 (puff far too big -> eraser) then two small puffs ----------
SM = [(548, 365, 0.45), (610, 295, 0.62)]
WRONG_PUFF = (545, 290, 1.0)
out += [H(0.6, (WRONG_PUFF[0] + 80, WRONG_PUFF[1])), cloud(*WRONG_PUFF, speed=280)]; out[-1]['wrong'] = True; MARK['m3_wrong'] = len(out)
out += [H(1.0)]
wx, wy, ws = WRONG_PUFF
out += [ERASE((wx - 80 * ws * 1.2 - 5, wy - 36 * ws * 1.2 - 5, wx + 80 * ws * 1.2 + 5, wy + 36 * ws * 1.2 + 5), 14, 700)]; MARK["m3_erase"] = len(out)
out += [H(0.6, (SM[0][0] + 36, SM[0][1]))]
for cx, cy, sc in SM: out.append(cloud(cx, cy, sc, speed=220))
MARK['smoke'] = len(out)
out += [P(0.3)]
# ---------- 6. Sun + one cloud ----------
SUX, SUY, SUR = 1180, 112, 50
out += [S(ell(SUX, SUY, SUR, SUR, 72, 5), 0.4, 260)]; MARK['sun_line'] = len(out)
CL = (830, 120, 0.95)
out += [cloud(*CL, speed=300)]; MARK['cloud'] = len(out)
out += [P(0.3)]
# ---------- 7. Horizon (stops at dress, chimney, cab, carriage) + border ----------
pl, pr = side(GHY, False), side(GHY, True)
out += [C('dkgreen')]
SEG = [(2, pl[0]), (pr[0], CH_[0] - 2 + 2), (CH_[2] + 2 - 2, CAB[0] + 2), (CAB[2] - 2, CAR[0] + 2), (CAR[2] - 2, 1358)]
for a_, b_ in SEG:
    for dy in (0, 3): out.append(S([(a_, GHY + dy), (b_, GHY + dy)], 0.4, FAST))
MARK['horizon_line'] = len(out)
out += [S([(2, GHY - 2), (2, 787)], 0.2, 900), S([(1358, GHY - 2), (1358, 787)], 0.2, 900),
        S([(2, 786), (1358, 786)], 0.3, 1000), S([(2, 782), (1358, 782)], 0.3, 1000)]
MARK['border_bottom'] = len(out)
out += [S([(2, 3), (1358, 3)], 0.3, 1000), S([(2, 2), (2, GHY)], 0.2, 900), S([(1358, 2), (1358, GHY)], 0.2, 900)]
out += [dot(pl[0], GHY, 6), dot(pr[0], GHY, 6)]
MARK['horizon_end'] = len(out)
out += [P(0.4)]
# ---------- 8. Bucket fills ----------
out += [C('loco'), F(((BO[0] + BO[2]) / 2, 535), (BO[0] + 20, 500), (BO[2] - 20, 570))]; MARK['boiler_fill'] = len(out)
out += [C('shoe'), F(((CH_[0] + CH_[2]) / 2, 455), ((CH_[0] + CH_[2]) / 2, 435))]; MARK['chimney_fill'] = len(out)
out += [C('cab'), F((770, 540), (720, 410), (820, 410), (720, 560), (820, 560), (770, 505))]; MARK['cab_fill'] = len(out)
out += [C('cab'), F((770, 378), (705, 378), (835, 378), *[(x, CROOF[1] + 12) for x in (900, 1070, 1240)])]; MARK['roof_fill'] = len(out)
out += [C('car'), F((1070, 560), (1070, 440), (960, 560), (1180, 560), (1070, 500), (905, 440), (1235, 440))]; MARK['car_fill'] = len(out)
out += [C('sun'), F(((CWIN[0] + CWIN[2]) / 2, (CWIN[1] + CWIN[3]) / 2), ((W1[0] + W1[2]) / 2, (W1[1] + W1[3]) / 2), ((W2[0] + W2[2]) / 2, (W2[1] + W2[3]) / 2))]; MARK['window_fill'] = len(out)
out += [C('shoe'), F(*[(x, WCY + 10) for x in WX])]; MARK['wheel_fill'] = len(out)
out += [C('smoke'), F(*[(cx, cy) for cx, cy, sc in SM])]; MARK['smoke_fill'] = len(out)
out += [C('sun'), F((SUX, SUY), (SUX - 20, SUY + 12))]; MARK['sun_fill'] = len(out)
def in_peppa(x, y): return body_l - 8 < x < body_r + 8 and head_top - 6 < y < body_bot + 8
def in_train(x, y): return 455 < x < 1270 and 355 < y < WCY + WR + 12
def in_chim(x, y): return CH_[0] - 12 < x < CH_[2] + 12 and CH_[1] - 12 < y < CH_[3] + 5
def in_sun(x, y): return (x - SUX) ** 2 + (y - SUY) ** 2 < (SUR + 12) ** 2
def in_cloud(x, y): return any(abs(x - cx) < 100 * sc and abs(y - cy) < 52 * sc for cx, cy, sc in [CL] + SM)
SKY = []
for x in range(28, 1360, 50):
    for y in range(24, GHY - 12, 36):
        if in_peppa(x, y) or in_train(x, y) or in_chim(x, y) or in_sun(x, y) or in_cloud(x, y): continue
        SKY.append((x, y))
SKY += [(body_r + 12, GHY - 14), (body_l - 20, GHY - 14), (CH_[0] - 14, GHY - 10), ((CH_[2] + CAB[0]) / 2, GHY - 10), (CAB[2] + 25, GHY - 10), (CAR[2] + 40, GHY - 10)]
out += [C('sky'), F(*SKY)]; MARK['sky_fill'] = len(out)
G = []
for x in range(25, 1360, 44):
    for y in range(GHY + 14, 780, 34):
        if in_peppa(x, y) or in_train(x, y): continue
        G.append((x, y))
G += [(body_l - 20, body_bot - 10), (body_r + 20, body_bot - 10), ((body_l + body_r) / 2, body_bot - 30),
      ((CH_[2] + CAB[0]) / 2, GHY + 12), (CAB[2] + 25, 520), (CAB[2] + 25, 600), (BO[0] - 10, 520), (CAR[2] + 40, 520), (600, 646), (880, 646), (1070, 646)]
out += [C('grass'), F(*G)]; MARK['grass_fill'] = len(out)
out += [P(0.4)]
MARK['fill_end'] = len(out)
# ---------- 9. Details: rail (MISTAKE 4: slanted rail -> Undo), hubs, rays, tufts ----------
RY = WCY + WR + 6
out += [C('rail'), H(0.6, (40, RY - 30)), S([(40, RY - 26), (1320, RY + 34)], 0.5, 560, smooth=False, wrong=True)]; MARK['m4_wrong'] = len(out)
out += [H(1.1), UNDO()]; MARK['m4_undo'] = len(out)
out += [H(0.6, (6, RY)), S([(4, RY), (1356, RY)], 0.5, 520)]; MARK['rail'] = len(out)
out += [C('white'), H(0.6, (WX[0], WCY))] + [S(ell(x, WCY, 7, 7, 24, 2) + ell(x, WCY, 3, 3, 12, 1), 0, TINY, smooth=False) for x in WX]
MARK['hubs'] = len(out)
out += [C('sun')]
for k in range(8):
    a_ = 2 * math.pi * k / 8 + 0.2
    out.append(S([(SUX + (SUR + 14) * math.cos(a_), SUY + (SUR + 14) * math.sin(a_)), (SUX + (SUR + 38) * math.cos(a_), SUY + (SUR + 38) * math.sin(a_))], 0.2, 200))
MARK['sun_rays'] = len(out)
out += [C('dkgreen')]
TUFT = [(60, 700), (420, 740), (1300, 720)]
for x, y in TUFT:
    for dx in (-12, 0, 12): out.append(S([(x, y + 16), (x + dx, y)], 0.2, 200))
MARK['tufts'] = len(out)
MARK['end'] = len(out)
# ---------- seed check + mistake check (PIL simulation with the PLAYED path) ----------
im = Image.new('RGB', (1360, 790), 'white'); d = ImageDraw.Draw(im)
col = dict((n, tuple(c)) for n, c in pal); cc = None; o_c = None
def clamp(p): return [min(max(p[0], 2), 1357), min(max(p[1], 2), 787)]
CORNER = (8, 8)
PROTECTED = {'skin', 'dress', 'cheek', 'shoe', 'loco', 'cab', 'car', 'smoke', 'sun'}
def draw_path(img, pts, colr, w):
    dd = ImageDraw.Draw(img); dd.line([tuple(p) for p in pts], fill=colr, width=w, joint='curve')
    for q in (pts[0], pts[-1]): dd.ellipse([q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2], fill=colr)
snap = None; pending = None
for idx, o in enumerate(out):
    if o['op'] == 'color': cc = col[o['c']]; o_c = o['c']
    if o['op'] == 'stroke':
        o['pts'] = [clamp(p) for p in o['pts']]
        if o.get('wrong') and snap is None: snap = im.copy()
        draw_path(im, played_path(o['pts'], o.get('smooth', True)), cc, 10 if o.get('wrong') else 9)
        d = ImageDraw.Draw(im)
    if o['op'] == 'undo':
        im = snap; snap = None; d = ImageDraw.Draw(im)
    if o['op'] == 'erase':
        big = im.copy(); draw_path(big, o["pts"], (255, 255, 255), 24)      # widest plausible footprint
        small = im.copy(); draw_path(small, o['pts'], (255, 255, 255), 17)  # measured eraser width
        from PIL import ImageChops
        bb = ImageChops.difference(big, snap).getbbox()
        if bb: snap.crop((bb[0]-60,bb[1]-60,bb[2]+60,bb[3]+60)).resize(((bb[2]-bb[0]+120)*3,(bb[3]-bb[1]+120)*3)).save('erase_fail.png'); im.crop((bb[0]-60,bb[1]-60,bb[2]+60,bb[3]+60)).resize(((bb[2]-bb[0]+120)*3,(bb[3]-bb[1]+120)*3)).save('erase_fail_wrong.png')
        assert bb is None, ('eraser footprint touches other ink at op %d' % idx, bb)
        assert list(small.getdata()) == list(snap.getdata()), 'eraser misses part of the wrong stroke at op %d' % idx
        im = small; snap = None; d = ImageDraw.Draw(im)
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
                        if len(colors) == 1 and im.getpixel((x, y)) == (255, 255, 255): ok = (x, y)
                if ok: break
            if ok:
                if o_c in PROTECTED:
                    probe = im.copy(); ImageDraw.floodfill(probe, ok, cc)
                    filled = sum(1 for p in probe.getdata() if p == cc) - sum(1 for p in im.getdata() if p == cc)
                    if probe.getpixel(CORNER) != im.getpixel(CORNER) or filled > 70000:
                        print('reject leak seed', o_c, ok, 'filled', filled); continue
                ImageDraw.floodfill(im, ok, cc); keep.append(list(ok))
            else: print('drop seed', o_c, s)
        if not keep: im.save('./preview_fail.png'); raise SystemExit('no seeds kept: ' + str(o_c))
        o['seeds'] = keep
im.save('./preview.png')
cnt = Counter(im.getdata()); print('white px left', cnt[(255, 255, 255)]); print('top', cnt.most_common(12))
A_ = [((10, 200), 'sky'), ((50, 760), 'grass'), ((585, 535), 'loco'), ((540, 455), 'shoe'), ((770, 540), 'cab'), ((770, 378), 'cab'),
      ((770, 454), 'sun'), ((1070, 560), 'car'), ((980, 486), 'sun'), ((WX[0], WCY + 12), 'shoe'), ((610, 295), 'smoke'), ((SUX, SUY + 20), 'sun'),
      ((830, 120), 'white'), ((CAB[2] + 25, 520), 'grass'), ((CAR[2] + 40, 520), 'grass'), ((632, 471), "grass"), ((640, 430), 'sky')]
for (x, y), c in A_: assert im.getpixel((x, y)) == col[c], ((x, y), c, im.getpixel((x, y)))
D = {'name': 'peppa-train-simple', 'canvas': [1360, 790], 'palette': pal, 'ops': out,
     'ui': dict(E['ui'], tool_xy=dict(E['ui']['tool_xy'], eraser=[17, 160]), eraser_size_xy=[45, 380], undo_xy=[270, 39]),
     'marks': MARK, 'notes': __doc__, 'speed_scale': 1.4}
json.dump(D, open('./strokes.json', 'w'))
gpl = 'GIMP Palette\nName: Peppa28\nColumns: 6\n#' + ''.join('\n%3d %3d %3d %s' % (*c, n) for n, c in pal) + '\n'
open('./peppa28.gpl', 'w').write(gpl); open('./peppa.gpl', 'w').write(gpl)
print(len(out), 'ops', len(pal), 'colors', Counter(o['op'] for o in out))
print({k: v for k, v in MARK.items()})
