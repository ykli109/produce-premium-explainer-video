#!/usr/bin/env python3
"""Douyin covers from the finished frame: 4:3 1440x1080 and 3:4 1080x1440, large bold outlined title.
usage: covers.py final.png "标题" outdir [--sub "副标题"]"""
import argparse,os,glob
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ap=argparse.ArgumentParser(); ap.add_argument('img'); ap.add_argument('title'); ap.add_argument('out'); ap.add_argument('--sub',default=''); ap.add_argument('--crop',default='',help='x,y,w,h canvas region (ui.canvas_origin + canvas) so covers show the art, not the app chrome')
a=ap.parse_args(); os.makedirs(a.out,exist_ok=True)
FONTS=[f for p in ['/usr/share/fonts/**/*CJK*Bold*','/usr/share/fonts/**/*CJK*Black*','/usr/share/fonts/**/*Heavy*','/usr/share/fonts/**/*CJK*'] for f in glob.glob(p,recursive=True)]
if not FONTS: raise SystemExit('install a CJK bold font: sudo apt-get install -y fonts-noto-cjk-extra')
def font(sz): return ImageFont.truetype(FONTS[0],sz)
src=Image.open(a.img).convert('RGB')
if a.crop: x,y,w,h=map(int,a.crop.split(',')); src=src.crop((x,y,x+w,y+h))
for W,H,tag in [(1440,1080,'4x3'),(1080,1440,'3x4')]:
    bg=src.resize((W,H)).filter(ImageFilter.GaussianBlur(30))           # blurred fill
    s=min(W/src.width,H/src.height); fg=src.resize((int(src.width*s),int(src.height*s)))
    bg.paste(fg,((W-fg.width)//2,(H-fg.height)//2)); d=ImageDraw.Draw(bg)
    sz=int(W*0.11)
    while d.textlength(a.title,font=font(sz))>W*0.9: sz-=4
    f=font(sz); tw=d.textlength(a.title,font=f); y=int(H*0.06)
    d.rounded_rectangle([(W-tw)/2-30,y-15,(W+tw)/2+30,y+sz*1.25],30,fill=(255,224,64))
    d.text(((W-tw)/2,y),a.title,font=f,fill=(30,20,20),stroke_width=max(4,sz//14),stroke_fill='white')
    if a.sub:
        f2=font(int(sz*0.45)); t2=d.textlength(a.sub,font=f2)
        d.text(((W-t2)/2,H-int(sz*0.45)-int(H*0.07)),a.sub,font=f2,fill='white',stroke_width=6,stroke_fill=(30,20,20))
    bg.save(f'{a.out}/cover_{tag}.jpg',quality=92); print(f'{a.out}/cover_{tag}.jpg')
