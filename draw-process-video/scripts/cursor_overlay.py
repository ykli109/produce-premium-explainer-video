#!/usr/bin/env python3
"""Draw a big coral pen marker (radius ~24, white ring) on raw.mp4, synced to mouse.log.
KolourPaint's pen/brush cursor is a tiny crosshair even with XCURSOR_SIZE=64, so the brush
position is made obvious in post. mouse.log lines: "<epoch> X=.. Y=.." (session.sh); t0.txt = ffmpeg start.
usage: cursor_overlay.py raw.mp4 mouse.log t0.txt out.mp4 [--r 24] [--lag 0.0]"""
import argparse,bisect,re,subprocess,numpy as np
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser(); ap.add_argument('raw'); ap.add_argument('log'); ap.add_argument('t0'); ap.add_argument('out')
ap.add_argument('--r',type=int,default=24); ap.add_argument('--lag',type=float,default=0.0,help='shift (s) if marker leads/trails the ink')
a=ap.parse_args(); T0=float(open(a.t0).read())
T=[];P=[]
for l in open(a.log):
    m=re.match(r'([\d.]+)\s+X=(\d+)\s+Y=(\d+)',l)
    if m: T.append(float(m[1])-T0); P.append((int(m[2]),int(m[3])))
W,H=map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',a.raw]).decode().split(','))
dec=subprocess.Popen(['ffmpeg','-loglevel','error','-i',a.raw,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','60','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',a.out],stdin=subprocess.PIPE)
r=a.r; n=0; FS=W*H*3
while True:
    b=dec.stdout.read(FS)
    if len(b)<FS: break
    t=n/60-a.lag; n+=1; im=Image.frombuffer('RGB',(W,H),b)
    if T and t>=T[0]:
        i=min(len(T)-1,max(0,bisect.bisect_right(T,t)-1)); x,y=P[i]
        if i+1<len(T) and T[i+1]>T[i]:  # interpolate between samples
            f=min(1,(t-T[i])/(T[i+1]-T[i])); x+= (P[i+1][0]-x)*f; y+=(P[i+1][1]-y)*f
        ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        d.ellipse([x-r-5,y-r-5,x+r+5,y+r+5],fill=(255,255,255,235))
        d.ellipse([x-r,y-r,x+r,y+r],fill=(255,111,97,150),outline=(235,80,70,255),width=3)
        d.ellipse([x-3,y-3,x+3,y+3],fill=(120,30,30,255))   # exact nib point
        im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
    enc.stdin.write(im.tobytes())
enc.stdin.close(); enc.wait(); print(f'{n} frames -> {a.out}')
