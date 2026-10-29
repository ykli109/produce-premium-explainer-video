#!/usr/bin/env python3
"""Burn in a big paintbrush marker on raw.mp4, synced to mouse.log.
KolourPaint's pen/brush cursor stays a tiny crosshair even with XCURSOR_SIZE=64, so
the brush tip is made obvious in post. Tip sits exactly at (x,y); handle angles up-right.
mouse.log lines: "<epoch> X=.. Y=.." (session.sh); t0.txt = ffmpeg start.
usage: cursor_overlay.py raw.mp4 mouse.log t0.txt out.mp4 [--scale 1.0] [--lag 0.0]"""
import argparse,bisect,math,re,subprocess
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser(); ap.add_argument('raw'); ap.add_argument('log'); ap.add_argument('t0'); ap.add_argument('out')
ap.add_argument('--scale',type=float,default=1.0,help='brush size multiplier')
ap.add_argument('--lag',type=float,default=0.0,help='shift (s) if marker leads/trails the ink')
# keep --r as a soft alias for older call sites (maps to scale via r/24)
ap.add_argument('--r',type=int,default=None,help=argparse.SUPPRESS)
a=ap.parse_args(); T0=float(open(a.t0).read())
if a.r is not None: a.scale=a.r/24.0
T=[];P=[]
for l in open(a.log):
    m=re.match(r'([\d.]+)\s+X=(\d+)\s+Y=(\d+)',l)
    if m: T.append(float(m[1])-T0); P.append((int(m[2]),int(m[3])))
W,H=map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',a.raw]).decode().split(','))
dec=subprocess.Popen(['ffmpeg','-loglevel','error','-i',a.raw,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','60','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',a.out],stdin=subprocess.PIPE)

def brush_overlay(W,H,x,y,s=1.0):
    """Paintbrush with tip at (x,y). Angled ~40° up-right so it reads as a brush, not a pen."""
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    ang=math.radians(-52)  # tip points down-left toward the ink; handle up-right
    ca,sa=math.cos(ang),math.sin(ang)
    def R(px,py):  # local (along, across) -> screen; origin at tip
        return (x+px*ca-py*sa, y+px*sa+py*ca)
    S=36*s
    # soft white halo so tip stays visible on dark fills
    d.ellipse([x-10*s,y-10*s,x+10*s,y+10*s],fill=(255,255,255,200))
    # bristle tip (wedge pointing at the ink point)
    tip=[R(0,0),R(S*0.55,-S*0.38),R(S*0.70,0),R(S*0.55,S*0.38)]
    d.polygon(tip,fill=(40,55,90,245),outline=(20,25,40,255))
    # bristle lines
    for t in (-0.22,-0.08,0.08,0.22):
        p0,p1=R(S*0.08,S*t*0.9),R(S*0.52,S*t)
        d.line([p0,p1],fill=(220,230,245,220),width=max(1,int(1.5*s)))
    # metal ferrule
    ferr=[R(S*0.55,-S*0.28),R(S*0.95,-S*0.28),R(S*0.95,S*0.28),R(S*0.55,S*0.28)]
    d.polygon(ferr,fill=(190,200,210,250),outline=(90,100,110,255))
    for u in (0.65,0.80):
        d.line([R(S*u,-S*0.26),R(S*u,S*0.26)],fill=(120,130,140,230),width=max(1,int(s)))
    # wooden handle
    hand=[R(S*0.95,-S*0.20),R(S*2.55,-S*0.14),R(S*2.70,0),R(S*2.55,S*0.14),R(S*0.95,S*0.20)]
    d.polygon(hand,fill=(196,120,55,250),outline=(120,60,25,255))
    # handle highlight
    d.line([R(S*1.05,-S*0.06),R(S*2.45,-S*0.04)],fill=(230,180,110,200),width=max(1,int(2*s)))
    # exact tip dot (dark, so the contact point is unambiguous)
    d.ellipse([x-3*s,y-3*s,x+3*s,y+3*s],fill=(15,20,35,255))
    return ov

n=0; FS=W*H*3
while True:
    b=dec.stdout.read(FS)
    if len(b)<FS: break
    t=n/60-a.lag; n+=1; im=Image.frombuffer('RGB',(W,H),b)
    if T and t>=T[0]:
        i=min(len(T)-1,max(0,bisect.bisect_right(T,t)-1)); x,y=P[i]
        if i+1<len(T) and T[i+1]>T[i]:
            f=min(1,(t-T[i])/(T[i+1]-T[i])); x+= (P[i+1][0]-x)*f; y+=(P[i+1][1]-y)*f
        im=Image.alpha_composite(im.convert('RGBA'),brush_overlay(W,H,x,y,a.scale)).convert('RGB')
    enc.stdin.write(im.tobytes())
enc.stdin.close(); enc.wait(); print(f'{n} frames -> {a.out} (paintbrush marker)')
