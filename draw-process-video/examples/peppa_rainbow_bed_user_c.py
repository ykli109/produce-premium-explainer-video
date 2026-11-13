# 180 s BGM bed for drawing-peppa-pig-24 from user-supplied peppa_user_c.mp4
# whole-section loop: 0.15-109.0 (full run up to the section break before the vocal tag)
# -> 0.15-72.55 (ends on the section break), 0.3 s equal-power crossfade, 1.5 s in / 4 s out
import numpy as np, soundfile as sf
x, sr = sf.read('src_c.wav')
def seg(a, b): return x[int(a*sr):int(b*sr)].copy()
X = int(0.3*sr); N = int(180*sr)
A = seg(0.15, 109.0); B = seg(0.15, 72.55)
t = np.linspace(0, np.pi/2, X)[:, None]
y = np.concatenate([A[:-X], A[-X:]*np.cos(t) + B[:X]*np.sin(t), B[X:]])
print('raw bed', len(y)/sr)
assert len(y) >= N
y = y[:N]
fi = int(1.5*sr); y[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(4*sr); y[-fo:] *= np.linspace(1, 0, fo)[:, None]
sf.write('bed.wav', y, sr, subtype='PCM_16')
print(len(y)/sr, 's; 0.15-109.00 + 0.15-72.55 (xfade 0.3 s), trimmed to 180 s')
