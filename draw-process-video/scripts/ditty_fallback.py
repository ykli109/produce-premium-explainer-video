#!/usr/bin/env python3
"""Original synthesized glockenspiel/ukulele ditty (no copyright issues). usage: ditty_fallback.py out.wav DUR"""
import numpy as np, json, wave, sys
SR=44100; DUR=float(sys.argv[2]); N=int(SR*DUR); rng=np.random.default_rng(7)
mus=np.zeros(N)
BPM=116; b=60/BPM
def nf(m): return 440*2**((m-69)/12)
def glock(t0,m,v=0.3,d=1.2):
    n=int(d*SR); t=np.arange(n)/SR; f=nf(m)
    s=(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*8)+0.2*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*14))*np.exp(-t*3.2)
    add(mus,t0,s*v)
def uke(t0,m,v=0.12,d=0.9):
    f=nf(m); L=int(SR/f); buf=rng.uniform(-1,1,L); n=int(d*SR); out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%L]; buf[i%L]=0.5*(buf[i%L]+buf[(i+1)%L])*0.996
    add(mus,t0,out*v*np.exp(-np.arange(n)/SR*2))
def add(buf,t0,s):
    i=int(t0*SR); j=min(N,i+len(s))
    if i<N: buf[i:j]+=s[:j-i]
def kick(t0):
    t=np.arange(int(.25*SR))/SR; add(mus,t0,0.45*np.sin(2*np.pi*(50+90*np.exp(-t*30))*t)*np.exp(-t*14))
def shaker(t0,v=0.05):
    t=np.arange(int(.08*SR))/SR; n=rng.normal(0,1,len(t)); n=np.diff(n,prepend=0); add(mus,t0,v*n*np.exp(-t*50))
# original melody (C major), 8-bar phrases; (scale degree midi, beats)
melA=[(72,.5),(76,.5),(79,1),(77,.5),(76,.5),(74,1),(72,.5),(74,.5),(76,.5),(79,.5),(81,2),
      (79,.5),(81,.5),(79,.5),(77,.5),(76,1),(72,1),(74,.5),(76,.5),(74,.5),(71,.5),(72,2)]
melB=[(76,1),(77,.5),(79,.5),(84,1),(81,1),(79,.5),(77,.5),(76,.5),(74,.5),(72,2),
      (69,.5),(72,.5),(74,1),(76,.5),(79,.5),(77,1),(76,.5),(74,.5),(72,.5),(71,.5),(72,2)]
chords={0:[48,55,60,64],1:[45,52,57,60],2:[41,48,53,57],3:[43,50,55,59]}
prog=[0,3,1,2, 0,2,3,0]; progB=[2,0,3,0, 1,2,3,0]
t=0.6; sec=0
while t<DUR-6:
    mel=melA if sec%2==0 else melB; pr=prog if sec%2==0 else progB
    for bar in range(8):
        tb=t+bar*4*b
        for k in range(4):
            kick(tb+k*b) if k in (0,2) else None
            for h in (0,.5): shaker(tb+k*b+h*b, .06 if h else .035)
        c=chords[pr[bar]]
        for k,off in enumerate([0,1,1.5,2,3,3.5]):
            for m in c[1:]: uke(tb+off*b+0.01*m%3*0.003,m+12 if m<52 else m,0.05)
        uke(tb,c[0]-12+12,0.12,1.5)
    tm=t
    for m,d in mel:
        if tm<DUR-5: glock(tm,m,0.28,max(.6,d*b*2))
        tm+=d*b
    t+=32*b; sec+=1
glock(DUR-5.2,72,.3,3); glock(DUR-5.2,76,.2,3); glock(DUR-5.2,79,.2,3); glock(DUR-5.2,84,.25,3.5)
env=np.ones(N); fo=int(3*SR); env[-fo:]=np.linspace(1,0,fo); mus*=env
out=mus/np.abs(mus).max()*0.9
st=np.stack([out,out],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st*32767).astype('<i2').tobytes()); w.close()
