# 180 s BGM bed for drawing-peppa-pig-26 from user-supplied peppa_user_c.mp4
# section loop starting on the 72.55 s section break (previous user_c work, -24, started at 0.15):
# 72.55-109.0 -> 0.15-109.0 -> 0.15-36.0, 0.3 s equal-power crossfades, trimmed to 180 s, 1.5 s in / 4 s out
import numpy as np, soundfile as sf
x, sr = sf.read('src_c.wav')
def seg(a, b): return x[int(a*sr):int(b*sr)].copy()
X = int(0.3*sr); N = int(180*sr)
t = np.linspace(0, np.pi/2, X)[:, None]
def join(A, B): return np.concatenate([A[:-X], A[-X:]*np.cos(t) + B[:X]*np.sin(t), B[X:]])
y = join(join(seg(72.55, 109.0), seg(0.15, 109.0)), seg(0.15, 36.0))
print('raw bed', len(y)/sr)
assert len(y) >= N
y = y[:N]
fi = int(1.5*sr); y[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(4*sr); y[-fo:] *= np.linspace(1, 0, fo)[:, None]
sf.write('bed.wav', y, sr, subtype='PCM_16')
print(len(y)/sr, 's; 72.55-109.00 + 0.15-109.00 + 0.15-36.0 (xfade 0.3 s), trimmed to 180 s')
