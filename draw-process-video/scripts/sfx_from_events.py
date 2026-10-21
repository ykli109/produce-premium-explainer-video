#!/usr/bin/env python3
"""Pencil scratch per stroke + soft bloop per fill, re-timed to the edited video.
t_video = (t_event - trim) / speed.  usage: sfx_from_events.py events.json out.wav --trim A --speed SP --dur 70"""
import argparse,json,wave,numpy as np
ap=argparse.ArgumentParser(); ap.add_argument('events'); ap.add_argument('out')
ap.add_argument('--trim',type=float,required=True); ap.add_argument('--speed',type=float,required=True); ap.add_argument('--dur',type=float,required=True)
a=ap.parse_args(); SR=44100; N=int(SR*a.dur); s=np.zeros(N); rng=np.random.default_rng(7)
def add(t0,x):
    i=int(t0*SR)
    if 0<=i<N: j=min(N,i+len(x)); s[i:j]+=x[:j-i]
for e in json.load(open(a.events)):
    if e[0]=='s':
        t0=(e[1]-a.trim)/a.speed; n=int(((e[2]-a.trim)/a.speed-t0)*SR)
        if n<=0: continue
        x=np.convolve(np.diff(rng.normal(0,1,n),prepend=0),np.ones(3)/3,'same'); tt=np.arange(n)/SR
        am=0.6+0.4*np.abs(np.sin(2*np.pi*3.3*tt+rng.uniform(0,6))); fade=np.minimum(1,np.minimum(tt,tt[-1]-tt)/0.03)
        add(t0,0.05*x*am*fade)
    else:
        tt=np.arange(int(.25*SR))/SR; add((e[1]-a.trim)/a.speed,0.12*np.sin(2*np.pi*(300+2000*tt)*tt)*np.exp(-tt*18))
w=wave.open(a.out,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.repeat(s[:,None],2,1)*32767).clip(-32767,32767).astype('<i2').tobytes()); w.close()
