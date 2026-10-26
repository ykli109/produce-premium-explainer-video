# peppa_user_b (user-supplied, accepted as-is): whole sections spliced, 0.3 s crossfades.
# music cue 42.9-68.8 | end-credits theme 286.05-301.1 | opening theme 1.1-15.9 | music cue again (runs into the 4 s fade)
import numpy as np,subprocess,wave
SR=44100; DUR=70.0; XF=0.3
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','b44.wav','-f','s16le','-ac','2','-ar',str(SR),'-'],capture_output=True,check=True).stdout,'<i2').reshape(-1,2).astype(float)/32768
secs=[(42.9,68.8),(286.05,301.1),(1.1,15.9),(42.9,80.0)]
X=int(XF*SR); y=None
for a,b in secs:
    s=x[int(a*SR):int(b*SR)].copy()
    if y is None: y=s; continue
    r=np.linspace(0,np.pi/2,X)[:,None]
    y[-X:]=y[-X:]*np.cos(r)+s[:X]*np.sin(r); y=np.concatenate([y,s[X:]])
N=int(DUR*SR); y=y[:N]
fi=int(0.3*SR); y[:fi]*=np.linspace(0,1,fi)[:,None]
fo=int(4*SR); y[-fo:]*=np.linspace(1,0,fo)[:,None]
w=wave.open('bed.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y*32767).clip(-32767,32767).astype('<i2').tobytes()); w.close()
t=0
for i,(a,b) in enumerate(secs):
    L=b-a-(XF if i else 0); print(f'bed {t:.2f}-{min(t+L,DUR):.2f}s <- src {a}-{min(b,a+(DUR-t)+(XF if i else 0)):.2f}s'); t+=L
    if t>=DUR: break
