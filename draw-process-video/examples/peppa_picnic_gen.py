#!/usr/bin/env python3
"""Peppa + carved picnic (drawing-peppa-pig-10).
Fills use paint-bucket seeds; large flats are never brush-painted."""
import json,math,random
from collections import Counter
from PIL import Image,ImageDraw
random.seed(31)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[
 ['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],
 ['white',[255,255,255]],['shoe',[25,20,22]],
 ['sky',[140,200,245]],['grass',[110,185,70]],['dkgreen',[55,120,40]],
 ['blanket',[225,60,70]],['cream',[255,240,200]],['basket',[200,140,70]],['basket2',[160,100,45]],
 ['sun',[255,215,60]],['bread',[240,200,130]],['lettuce',[120,190,60]],['apple',[220,40,40]],
 ['juice',[255,160,40]],['melon',[240,80,90]],['cookie',[170,110,60]],['flower',[255,130,190]],
]
def T(p,s,ox,oy): return [round(ox+(p[0]-289)*s,1),round(oy+(p[1]-40)*s,1)]
def char(s,ox,oy,body='dress'):
    r=[]
    for o in ops[:44]:
        o=dict(o)
        if o['op']=='stroke': o['pts']=[T(p,s,ox,oy) for p in o['pts']]
        if o['op']=='fill' and o['seeds'][0][1]>600:
            for cx in (419,523):
                pts=[]
                for f in (0.75,0.5,0.25):
                    pts+=[T((cx+30*f*math.cos(2*math.pi*k/30),679+12*f*math.sin(2*math.pi*k/30)),s,ox,oy) for k in range(31)]
                r.append({'op':'stroke','amp':0,'dl':0.006,'pts':pts})
            continue
        if o['op']=='fill': o['seeds']=[T(p,s,ox,oy) for p in o['seeds']]
        if o['op']=='color' and o['c']=='dress': o['c']=body
        r.append(o)
    return r
dress=ops[12]['pts']
def side(s,ox,oy,y,right):
    P=[T(p,s,ox,oy) for p in dress]; c=[p for p in P if abs(p[1]-y)<6]
    if not c:
        P2=sorted(P,key=lambda q:abs(q[1]-y))[:8]
        p=max(P2,key=lambda q:q[0]) if right else min(P2,key=lambda q:q[0])
        return [p[0]+(-3 if right else 3), y]
    p=max(c,key=lambda q:q[0]) if right else min(c,key=lambda q:q[0])
    return [p[0]+(-3 if right else 3),p[1]]
def S(pts,amp=1.0,dl=0.009): return {'op':'stroke','amp':amp,'dl':dl,'pts':[[round(x,1),round(y,1)] for x,y in pts]}
def C(c): return {'op':'color','c':c}
def F(*seeds): return {'op':'fill','seeds':[list(x) for x in seeds]}
def cr(P,n=10):
    P=[P[0]]+P+[P[-1]]; o=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1:i+3]
        for k in range(n):
            t=k/n
            o.append(tuple(.5*(2*p1[j]+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t*t+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t**3) for j in (0,1)))
    return o+[P[-2]]
def ell(cx,cy,rx,ry,n=72,extra=4):
    return [(cx+rx*math.cos(2*math.pi*k/n),cy+ry*math.sin(2*math.pi*k/n)) for k in range(n+extra)]
def dot(cx,cy,r):
    pts=[]
    for rr in [r,r*.66,r*.33,1]: pts+=ell(cx,cy,rr,rr,24,1)
    return S(pts,0,0.006)
def poly(P): return list(P)+[P[0],P[1]]
def tri(cx,cy,w,h):
    return poly([(cx,cy-h),(cx-w,cy+h*0.55),(cx+w,cy+h*0.55)])

PS,PX,PY=0.70,140,55
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.5}]
GHY=520
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
# blanket (trapezoid, 4x2 checker)
TL,TR,BR,BL=(700,600),(1300,600),(1335,768),(660,768)
out+=[C('ink'),S(poly([TL,TR,BR,BL]),0.2,0.009)]
for f in (0.25,0.5,0.75):
    a=lerp(TL,TR,f); b=lerp(BL,BR,f); out.append(S([(a[0],a[1]-3),(b[0],b[1]+3)],0.1,0.01))
ml=lerp(TL,BL,0.5); mr=lerp(TR,BR,0.5); out.append(S([(ml[0]-3,ml[1]),(mr[0]+3,mr[1])],0.1,0.01))
def cell(r,c):
    y0=600+84*r+42; L=lerp(TL,BL,(y0-600)/168); R=lerp(TR,BR,(y0-600)/168)
    return lerp(L,R,(c+0.5)/4)
# basket on grass
out+=[C('ink'),S(poly([(470,600),(650,600),(628,705),(492,705)]),0.2,0.009)]
out.append(S([(470,652),(650,652)],0.1,0.01))
out.append(S(cr([(492,602),(560,532),(628,602)],10),0.2,0.01))
# sun + clouds
SX,SY,SR=1230,115,58
out+=[C('ink'),S(ell(SX,SY,SR,SR,64,4),0.2,0.008)]
def cloud(cx,cy,sc):
    P=[]
    for k in range(90):
        a=2*math.pi*k/90; b=1+0.18*abs(math.sin(2.5*a)) if math.sin(a)<0.2 else 1
        P.append((cx+80*sc*b*math.cos(a),cy+36*sc*b*math.sin(a)))
    return S(P+P[:3],0.1,0.008)
CLOUDS=[(700,120,1.1),(960,230,0.85),(560,300,0.7)]
out+=[cloud(*c) for c in CLOUDS]
out+=[C('dkgreen'),S([(2,GHY),(1358,GHY)],0.2,0.01),S([(2,GHY),(2,787)],0.2,0.01),S([(1358,GHY),(1358,787)],0.2,0.01),S([(2,GHY+3),(1358,GHY+3)],0.15,0.01)]
out+=[{'op':'pause','s':0.4}]
# fills
for r in range(2):
    for c in range(4):
        x,y=cell(r,c); out+=[C('blanket' if (r+c)%2==0 else 'cream'),F((x,y),(x-30,y+15),(x+30,y-15))]
out+=[C('basket'),F((560,625),(520,625),(600,625)),C('basket2'),F((560,680),(520,680),(600,680))]
G=[(x,y) for x in range(30,1360,70) for y in range(545,790,55)]
out+=[C('grass'),F(*(G+[(560,585),(545,590),(575,590)]))]
out+=[C('sun'),F((SX,SY),(SX-15,SY+10))]
SKY=[(x,y) for x in range(30,1360,75) for y in range(25,510,60) if not (120<x<440) and not any(abs(x-a)<100*k and abs(y-b)<50*k for a,b,k in CLOUDS)]+[(80,100),(80,400),(470,60),(470,470),(262,470),(255,490),(270,455)]
out+=[C('sky'),F(*SKY)]
out+=[{'op':'pause','s':0.45}]
# food on blanket
cx,cy=cell(0,0)   # sandwich
out+=[C('ink'),S(poly([(cx-34,cy+22),(cx+34,cy+22),(cx,cy-28)]),0.1,0.008),C('bread'),F((cx,cy+8)),C('lettuce'),S([(cx-26,cy+16),(cx+26,cy+16)],0.4,0.008)]
cx,cy=cell(0,2)   # second sandwich
out+=[C('ink'),S(poly([(cx-30,cy+22),(cx+30,cy+22),(cx-6,cy-26)]),0.1,0.008),C('bread'),F((cx-4,cy+8)),C('lettuce'),S([(cx-22,cy+16),(cx+22,cy+16)],0.4,0.008)]
cx,cy=cell(0,3)   # apple
out+=[C('ink'),S(ell(cx,cy+4,24,22,48,4),0.1,0.008),C('apple'),F((cx,cy+4)),C('cookie'),S([(cx,cy-18),(cx+4,cy-30)],0,0.008),C('lettuce'),dot(cx+12,cy-26,6)]
cx,cy=cell(1,0)   # juice cup
out+=[C('ink'),S(poly([(cx-20,cy-30),(cx+20,cy-30),(cx+16,cy+28),(cx-16,cy+28)]),0.1,0.008),C('juice'),F((cx,cy+5)),C('ink'),S([(cx+6,cy-30),(cx+14,cy-48)],0,0.008)]
cx,cy=cell(1,2)   # watermelon
arc=[(cx+38*math.cos(a),cy-10+36*math.sin(a)) for a in [math.pi*k/30 for k in range(31)]]
out+=[C('dkgreen'),S(arc+[arc[0],arc[1]],0.05,0.008),C('melon'),F((cx,cy+5))]
out+=[C('ink')]+[dot(cx+dx,cy+dy,2.5) for dx,dy in [(-12,2),(0,12),(12,2)]]
for (r,c) in [(1,1),(1,3)]:
    cx,cy=cell(r,c); out+=[C('cookie')]+[dot(cx+dx,cy+dy,9) for dx,dy in [(-24,-8),(8,-14),(-4,14),(26,8)]]
# details
out+=[C('sun')]
for k in range(10):
    a=2*math.pi*k/10; out.append(S([(SX+(SR+12)*math.cos(a),SY+(SR+12)*math.sin(a)),(SX+(SR+36)*math.cos(a),SY+(SR+36)*math.sin(a))],0,0.008))
for i,(x,y) in enumerate([(60,600),(200,700),(330,580),(420,740),(560,760),(80,760),(1350-30,560),(1000,560),(600,550),(260,560)]):
    out+=[C('flower')]+[dot(x+8*math.cos(2*math.pi*k/5),y+8*math.sin(2*math.pi*k/5),5) for k in range(5)]+[C('sun'),dot(x,y,4)]
out+=[C('dkgreen')]
for x,y in [(40,GHY+30),(170,GHY+45),(390,GHY+28),(690,GHY+40),(880,GHY+35),(1180,GHY+38),(450,775),(140,640)]:
    for dx in (-10,0,10): out.append(S([(x,y+14),(x+dx,y)],0.2))
out+=[C('ink')]
for x,y in [(820,60),(870,85),(1080,150)]:
    out.append(S(cr([(x-16,y),(x-8,y-7),(x,y),(x+8,y-7),(x+16,y)],5),0,0.008))
FOODS={'bread','apple','juice','melon'}
# ---- seed-check preview ----
im=Image.new('RGB',(1360,790),'white');d=ImageDraw.Draw(im)
col=dict((n,tuple(c)) for n,c in pal); cc=None; o_c=None
def clamp(p): return [min(max(p[0],2),1357),min(max(p[1],2),787)]
for o in out:
    if o['op']=='color': cc=col[o['c']]; o_c=o['c']
    if o['op']=='stroke':
        o['pts']=[clamp(p) for p in o['pts']]
        d.line([tuple(p) for p in o['pts']],fill=cc,width=9,joint='curve')
        for q in (o['pts'][0],o['pts'][-1]): d.ellipse([q[0]-4.5,q[1]-4.5,q[0]+4.5,q[1]+4.5],fill=cc)
    if o['op']=='fill':
        keep=[]
        for s in o['seeds']:
            x0,y0=map(int,s); ok=None
            for r in range(0,6):  # tight radius — larger r can step outside a sealed outline
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        x,y=x0+dx,y0+dy
                        if 0<=x<1360 and 0<=y<790 and ok is None and len(im.crop((x-3,y-3,x+4,y+4)).getcolors(500) or [0,0])==1 and (o_c in FOODS or im.getpixel((x,y))==(255,255,255)):
                            ok=(x,y)
                if ok: break
            if ok:
                ImageDraw.floodfill(im,ok,cc)
                keep.append(list(ok))
            else: print('drop seed',o_c,s)
        if not keep:
            im.save('/workspace/peppa10/preview_fail.png'); raise SystemExit('no seeds kept: '+str(o_c))
        o['seeds']=keep
im.save('/workspace/peppa10/preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255))
print('white px left',white)
print('top',Counter(im.getdata()).most_common(10))
skin=sum(1 for p in im.getdata() if p==(247,172,196))
assert skin<80000, skin
assert white<80000, white

D={'name':'peppa-picnic','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa picnic: checkered red/cream blanket with sandwiches, apple, juice, watermelon, cookies; wicker basket; sun, clouds, birds, flowers. Bucket fills for flats.'}
json.dump(D,open('/workspace/peppa10/peppa_picnic_strokes.json','w'))
gpl='GIMP Palette\nName: Peppa10\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal)
open('/workspace/peppa10/peppa10.gpl','w').write(gpl)
open('/workspace/peppa10/peppa.gpl','w').write(gpl)
print(len(out),'ops')
