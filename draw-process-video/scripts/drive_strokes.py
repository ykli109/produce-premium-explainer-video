#!/usr/bin/env python3
"""Drive KolourPaint with xdotool from a stroke JSON (canvas coords) like a human hand.

ops (canvas coordinates):
  color{c}                      pick a palette cell (cursor travels there)
  stroke{pts, amp, dl|speed, pace, smooth, wrong}
                                brush stroke. Points are re-sampled to 1 px, smoothed (corner-aware
                                Gaussian + dense 2 px re-sampling, so arcs never show polyline facets),
                                given a low-frequency hand wobble (amp px, tapered to 0 at the ends),
                                and played with a speed profile: ease-in/out at both ends, slower in
                                tight curves, per-stroke jitter. speed = px/s (default 4/dl, i.e. the
                                legacy dl=0.009 -> 444 px/s); pace multiplies the duration (2 = twice
                                as slow). smooth=false keeps the raw polyline. wrong=true only tags it.
  fill{seeds}                   paint-bucket clicks (着色桶)
  pause{s}                      hand rests (cursor still)
  hover{s, to?}                 "thinking": the brush drifts slowly near its position (or toward `to`)
  undo{}                        cursor travels to the toolbar Undo button and clicks it (ui.undo_xy)
  erase{pts, size?, pace?}      eraser tool scrub along pts (ui.tool_xy.eraser, ui.eraser_size_xy)
Every pen-up move between targets is a smooth eased travel, never a teleport.
Events (seconds since --t0): ["s",t0,t1] per stroke, ["f",t] per bucket click, ["h",t0,t1] hover,
["u",t] undo click, ["e",t0,t1] eraser scrub, ["p",t0,t1] pause.
--dry prints the estimated duration without touching X."""
import argparse, json, math, random, subprocess, time
ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('--display', default=':77')
ap.add_argument('--t0', type=float, default=None); ap.add_argument('--events', default='events.json')
ap.add_argument('--speed', type=float, default=1.0, help='>1 = faster pen overall')
ap.add_argument('--dry', action='store_true', help='estimate only (writes planned events to --events if given explicitly)')
ap.add_argument('--overhead', type=float, default=0.0012, help='per xdotool move cost (s), for --dry')
a = ap.parse_args(); D = json.load(open(a.json)); U = D['ui']; rnd = random.Random(5)
a.speed *= D.get('speed_scale', 1.0)   # per-scene global tempo (fit the ~174 s drawing budget)
T0 = a.t0 or time.time(); log = []; cur = None; pos = [700.0, 1000.0]; clock = [0.0]
PAL = [p[0] for p in D['palette']]; OX, OY = U['canvas_origin']; CW, CH = D['canvas']

def now(): return clock[0] if a.dry else time.time() - T0
def pre_time(c, until):
    """planned seconds before the first `until` command (pen-up travel + dwell), so events mark real ink."""
    t = 0.0
    for x in c:
        if x.startswith(until): break
        if x.startswith('sleep'): t += float(x.split()[1])
        elif x.startswith('mousemove'): t += a.overhead
    return t
def X(c):
    if a.dry:
        for s in c:
            if s.startswith('sleep'): clock[0] += float(s.split()[1])
            elif s.startswith('mousemove'): clock[0] += a.overhead
        return
    subprocess.run(['xdotool', '-'], input='\n'.join(c) + '\n', text=True, env={'DISPLAY': a.display, 'PATH': '/usr/bin:/bin'})
def M(p): return (OX + min(CW - 1, max(0, p[0])), OY + min(CH - 1, max(0, p[1])))

def travel(to, dur=None):
    """pen-up eased move along a slight arc (minimum-jerk timing)."""
    x0, y0 = pos; x1, y1 = to; d = math.dist(pos, to)
    if d < 1.5: return []
    dur = dur or min(0.75, max(0.14, 0.10 + d * 0.00042)) / a.speed
    n = max(3, int(dur / 0.012)); bow = rnd.uniform(-0.08, 0.08) * d
    nx, ny = (-(y1 - y0) / d, (x1 - x0) / d); c = []
    for k in range(1, n + 1):
        u = k / n; s = 10 * u**3 - 15 * u**4 + 6 * u**5; b = 4 * s * (1 - s) * bow
        c += [f'mousemove {int(round(x0 + (x1 - x0) * s + nx * b))} {int(round(y0 + (y1 - y0) * s + ny * b))}', f'sleep {dur / n:.4f}']
    pos[:] = [x1, y1]; return c

def tool(t):
    global cur
    if t == cur: return
    x, y = U['tool_xy'][t]; X(travel((x, y)) + ['sleep 0.18', 'click 1', 'sleep 0.15'])
    if t == 'brush' and U.get('brush_size_xy'): X(travel(U['brush_size_xy']) + ['sleep 0.15', 'click 1', 'sleep 0.15'])
    if t == 'eraser' and U.get('eraser_size_xy'): X(travel(U['eraser_size_xy']) + ['sleep 0.15', 'click 1', 'sleep 0.15'])
    cur = t

def color(n):
    r, c = divmod(PAL.index(n), U['palette_cols']); x0, y0 = U['palette_origin']; s = U['palette_cell']
    X(travel((x0 + s * c, y0 + s * r)) + ['sleep 0.22', 'click 1', 'sleep 0.2'])

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_geom import dense, turn, gauss, smooth_path

def stroke(o, the_tool='brush'):
    tool(the_tool)
    raw = [M(p) for p in o['pts']]
    P = smooth_path(raw) if o.get('smooth', True) else dense(raw, 1.0)
    P = dense(P[::2] + [P[-1]], 2.0) if len(P) > 3 else P
    amp = o.get('amp', 1.0); L = len(P)
    # low-frequency hand wobble along the normal, tapered at both ends so joints still meet
    ph1, ph2 = rnd.random() * 6.3, rnd.random() * 6.3; lam1, lam2 = rnd.uniform(140, 220), rnd.uniform(55, 90)
    W = []
    for i, (x, y) in enumerate(P):
        j0, j1 = max(0, i - 2), min(L - 1, i + 2); tx, ty = P[j1][0] - P[j0][0], P[j1][1] - P[j0][1]; tn = math.hypot(tx, ty) or 1
        s = 2.0 * i; taper = min(1, s / 12, 2.0 * (L - 1 - i) / 12)
        off = amp * taper * (0.65 * math.sin(2 * math.pi * s / lam1 + ph1) + 0.35 * math.sin(2 * math.pi * s / lam2 + ph2))
        W.append((x - ty / tn * off, y + tx / tn * off))
    P = [(min(OX + CW - 3, max(OX + 2, x)), min(OY + CH - 3, max(OY + 2, y))) for x, y in W]
    # speed profile (px/s): base * ease-in/out * curvature slowdown * per-stroke jitter
    v = o.get('speed') or 4.0 / o.get('dl', 0.009)
    v = v * a.speed / o.get('pace', 1.0) * rnd.uniform(0.9, 1.1)
    total = 2.0 * (L - 1) or 1.0; c = travel(P[0]) + [f'sleep {rnd.uniform(0.07, 0.14):.3f}', 'mousedown 1']
    acc = 0.0
    for i in range(1, L):
        s = 2.0 * i; u = min(s / max(18, total * 0.12), (total - s) / max(18, total * 0.12), 1)
        ease = 0.45 + 0.55 * (u * u * (3 - 2 * u))
        kap = turn(P, i, 3) / 6.0          # rad per px
        vl = max(60.0, v * ease / (1 + 22 * kap))
        step = min(8.0, max(2.0, vl * 0.006))  # fast straight runs: fewer, longer moves (~6 ms each); curves stay 2 px
        acc += 2.0
        if acc + 1e-6 < step and i < L - 1: continue
        x, y = P[i]; c += [f'mousemove {int(round(x))} {int(round(y))}', f'sleep {max(0.0025, acc / vl):.4f}']; acc = 0.0
    c += ['mouseup 1', f'sleep {rnd.uniform(0.05, 0.1):.3f}']
    t = now() + pre_time(c, 'mousedown'); X(c); pos[:] = list(P[-1]); return t, now()   # t = pen touches paper

def fill(seeds):
    tool('fill')
    for s in seeds:
        x, y = M(s); c = travel((x, y)) + ['sleep 0.3', 'click 1', 'sleep 0.25']; t = now() + pre_time(c, 'click'); X(c); log.append(['f', t])  # t = bucket click

def hover(sec, to=None):
    t = now(); n = max(2, int(sec / 0.03)); x0, y0 = pos; tx, ty = (M(to) if to else (x0, y0))
    r = rnd.uniform(5, 11); ph = rnd.random() * 6.3; c = []
    for k in range(1, n + 1):
        u = k / n; s = u * u * (3 - 2 * u)
        x = x0 + (tx - x0) * s + r * math.sin(ph + 2.2 * math.pi * u) * math.sin(math.pi * u)
        y = y0 + (ty - y0) * s + 0.6 * r * math.sin(ph + 3.1 * math.pi * u) * math.sin(math.pi * u)
        c += [f'mousemove {int(round(x))} {int(round(y))}', f'sleep {sec / n:.4f}']
    X(c); pos[:] = [tx, ty]; log.append(['h', t, now()])

def undo():
    back = list(pos); x, y = U.get('undo_xy', (270, 39))
    c = travel((x, y)) + ['sleep 0.35', 'click 1', 'sleep 0.35'] + travel(back)
    t = now() + pre_time(c, 'click'); X(c); log.append(['u', t, now()])     # t = the Undo click

prof = {}
for o in D['ops']:
    k = o['op']; _t = now()
    if k == 'color': color(o['c'])
    elif k == 'stroke': t0, t1 = stroke(o); log.append(['s', t0, t1])
    elif k == 'fill': fill(o['seeds'])
    elif k == 'pause': t = now(); X([f"sleep {o['s']}"]); log.append(['p', t, now()])
    elif k == 'hover': hover(o['s'], o.get('to'))
    elif k == 'undo': undo()
    elif k == 'erase': t0, t1 = stroke(dict(o, amp=0, smooth=False, speed=o.get('speed', 380)), 'eraser'); log.append(['e', t0, t1])
    prof[k] = prof.get(k, 0) + now() - _t
    if os.environ.get('PROFILE'): print(k, o.get('c', ''), round(now() - _t, 2), o.get('speed', ''), len(o.get('pts', [])))
if U.get('park_cursor'): X(travel(U['park_cursor']))
if not a.dry or a.events != 'events.json': json.dump(log, open(a.events, 'w'))
print('drawing done in %.1fs' % now(), {k: round(v, 1) for k, v in prof.items()})
