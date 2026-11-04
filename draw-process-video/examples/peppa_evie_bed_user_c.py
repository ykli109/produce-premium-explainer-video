# BGM bed for drawing-peppa-pig-16 from user-supplied peppa_user_c.mp4
import numpy as np,soundfile as sf
x,sr=sf.read('src_c.wav')
def seg(a,b): return x[int(a*sr):int(b*sr)].copy()
X=int(0.3*sr); N=int(70*sr)
A=seg(72.55,109.0)
B=seg(0.15,0.15+(N-len(A)+X)/sr+0.05)
t=np.linspace(0,np.pi/2,X)[:,None]
y=np.concatenate([A[:-X],A[-X:]*np.cos(t)+B[:X]*np.sin(t),B[X:]])[:N]
fi=int(1.5*sr); y[:fi]*=np.linspace(0,1,fi)[:,None]; fo=int(4*sr); y[-fo:]*=np.linspace(1,0,fo)[:,None]
sf.write('bed.wav',y,sr,subtype='PCM_16')
b_end=0.15+(N-len(A)+X)/sr
print(len(y)/sr,'s; A 72.55-109.00 + B 0.15-%.2f (xfade 0.3s)'%b_end)
