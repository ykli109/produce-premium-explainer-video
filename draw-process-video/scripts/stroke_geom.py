"""Shared stroke geometry for drive_strokes.py and scene generators (PIL seed checks must use the
same smoothed path that the driver plays). Pure python, no X."""
import math
def dense(pts, step=1.0):
    out = [tuple(pts[0])]
    for p, q in zip(pts, pts[1:]):
        L = math.dist(p, q); n = max(1, int(L / step))
        out += [(p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n) for k in range(1, n + 1)]
    return out
def turn(P, i, k):
    a_, b_, c_ = P[max(0, i - k)], P[i], P[min(len(P) - 1, i + k)]
    v1 = (b_[0] - a_[0], b_[1] - a_[1]); v2 = (c_[0] - b_[0], c_[1] - b_[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 < 1e-6 or n2 < 1e-6: return 0.0
    return math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2))))
def gauss(seg, sig, closed=False):
    if len(seg) < 5 or sig <= 0: return seg
    r = int(3 * sig); w = [math.exp(-0.5 * (j / sig) ** 2) for j in range(-r, r + 1)]; n = len(seg); out = []
    for i in range(n):
        sx = sy = sw = 0.0
        for j, wj in zip(range(-r, r + 1), w):
            k = i + j
            if closed: k %= n
            elif k < 0: k = -k            # reflect, keeps endpoints in place
            elif k >= n: k = 2 * (n - 1) - k
            k = min(max(k, 0), n - 1); sx += seg[k][0] * wj; sy += seg[k][1] * wj; sw += wj
        out.append((sx / sw, sy / sw))
    if not closed: out[0], out[-1] = seg[0], seg[-1]
    return out
def smooth_path(pts, sig=None):
    P = dense(pts, 1.0)
    if len(P) < 8: return P
    L = len(P); sig = sig if sig is not None else min(6.0, max(1.5, L / 40))
    closed = math.dist(P[0], P[-1]) < 6 and L > 60
    k = 9; ang = [turn(P, i, k) for i in range(L)]
    cor = [i for i in range(k, L - k) if ang[i] > math.radians(55) and ang[i] == max(ang[max(0, i - 8):i + 9])]
    if cor: closed = False
    cuts = [0] + cor + [L - 1]; out = []
    for s0, s1 in zip(cuts, cuts[1:]):
        seg = gauss(P[s0:s1 + 1], sig, closed and not cor)
        out += seg if not out else seg[1:]
    return out

def played_path(pts, smooth=True):
    """Canvas-space path the driver draws (before the +-amp px wobble): smoothed, 2 px spacing."""
    P = smooth_path(pts) if smooth else dense(pts, 1.0)
    return dense(P[::2] + [P[-1]], 2.0) if len(P) > 3 else P

def scrub(box, pitch=9, pad=6):
    """Zig-zag eraser path covering box=(x0,y0,x1,y1) (+pad), horizontal passes `pitch` px apart."""
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    pts, y, k = [], y0, 0
    while y <= y1 + 0.1:
        pts += [(x0, y), (x1, y)] if k % 2 == 0 else [(x1, y), (x0, y)]
        y += pitch; k += 1
    return pts
