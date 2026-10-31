#!/usr/bin/env python3
"""Peppa at an outdoor swimming pool (drawing-peppa-pig-12).
Fills use paint-bucket seeds; large flats are never brush-painted."""
import json,math,random
from collections import Counter
from PIL import Image,ImageDraw
random.seed(42)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[
 ['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],
 ['white',[255,255,255]],['shoe',[25,20,22]],
 ['sky',[140,200,245]],['grass',[110,185,70]],['water',[70,170,230]],['water2',[40,130,200]],
 ['rim',[210,195,160]],['board',[235,200,120]],['float',[255,210,40]],['sun',[255,215,60]],
 ['dkgreen',[55,120,40]],['flower',[255,130,190]],
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

PS,PX,PY=0.62,70,40
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.5}]
GHY=470

# Single closed pool (perspective trapezoid) + parallel outer stroke for deck lip (stroke only)
WTL,WTR,WBR,WBL=(520,520),(1220,520),(1320,740),(440,740)
out+=[C('ink'),S(poly([WTL,WTR,WBR,WBL]),0.12,0.009)]
# outer lip as offset parallel strokes (NOT a second closed fill region)
out+=[C('rim'),
      S([(500,500),(1240,500)],0.05,0.01),
      S([(1240,500),(1345,755)],0.05,0.01),
      S([(1345,755),(410,755)],0.05,0.01),
      S([(410,755),(500,500)],0.05,0.01)]

# Diving board on grass just above pool (closed)
out+=[C('ink'),S(poly([(1000,478),(1165,478),(1165,512),(1000,512)]),0.08,0.009)]
# ladder: ink strokes entirely OUTSIDE the water poly, on left grass/deck lip
out+=[S([(455,530),(455,750)],0.05,0.01),S([(495,530),(495,750)],0.05,0.01)]
for yy in (720,675,630,585):
    out.append(S([(455,yy),(495,yy)],0.05,0.01))

FX,FY,FRX,FRY=880,620,80,48
out+=[S(ell(FX,FY,FRX,FRY,72,4),0.05,0.008)]
out+=[S(ell(FX,FY,FRX*0.48,FRY*0.48,48,4),0.05,0.008)]

SX,SY,SR=1180,110,56
out+=[C('ink'),S(ell(SX,SY,SR,SR,64,4),0.05,0.008)]
def cloud(cx,cy,sc):
    P=[]
    for k in range(90):
        a=2*math.pi*k/90; b=1+0.18*abs(math.sin(2.5*a)) if math.sin(a)<0.2 else 1
        P.append((cx+80*sc*b*math.cos(a),cy+36*sc*b*math.sin(a)))
    return S(P+P[:3],0.1,0.008)
CLOUDS=[(680,95,1.0),(1060,130,0.95),(1285,85,0.7)]
out+=[cloud(*c) for c in CLOUDS]

out+=[C('dkgreen'),
      S([(2,GHY),(1358,GHY)],0.15,0.01),
      S([(2,GHY),(2,787)],0.1,0.01),
      S([(1358,GHY),(1358,787)],0.1,0.01),
      S([(2,787),(1358,787)],0.1,0.01)]
out+=[{'op':'pause','s':0.4}]

# fills
out+=[C('board'),F((1080,495),(1040,495),(1120,495))]
# water — skip float disk
WATER=[]
for x in range(500,1280,50):
    for y in range(545,720,38):
        t=(y-520)/max(1,(740-520))
        left=520+(440-520)*t+20
        right=1220+(1320-1220)*t-20
        if not (left<=x<=right): continue
        if ((x-FX)/FRX)**2+((y-FY)/FRY)**2 < 1.15: continue
        WATER.append((x,y))
WATER+=[(700,600),(1000,600),(750,680),(1050,680),(600,650),(1150,650),(900,560),(800,580)]
out+=[C('water'),F(*WATER)]
out+=[C('float'),F((FX+FRX*0.74,FY),(FX-FRX*0.74,FY),(FX,FY+FRY*0.74),(FX,FY-FRY*0.74),
                    (FX+55,FY+18),(FX-55,FY-18))]
out+=[C('water'),F((FX,FY),(FX-8,FY),(FX+8,FY))]

G=[]
for x in range(25,1360,55):
    for y in range(485,790,42):
        t=(y-520)/max(1,(740-520))
        if t<0: t=0
        if t>1: t=1
        left=520+(440-520)*t
        right=1220+(1320-1220)*t
        if y>=520 and (left-6)<=x<=(right+6) and y<=740: continue
        G.append((x,y))
G+=[(60,520),(140,620),(220,720),(50,750),(350,490),(380,760),
    (1320,520),(1300,650),(1280,760),(800,770),(600,770),(1000,770),(200,490),(100,700)]
out+=[C('grass'),F(*G)]

out+=[C('sun'),F((SX,SY),(SX-20,SY),(SX+20,SY),(SX,SY-20),(SX,SY+20))]
SKY=[(x,y) for x in range(30,1360,70) for y in range(25,460,50)
     if not (50<x<340 and y>50)
     and not any(abs(x-a)<95*k and abs(y-b)<48*k for a,b,k in CLOUDS)
     and not (abs(x-SX)<SR+20 and abs(y-SY)<SR+20)]
SKY+=[(40,180),(40,380),(450,40),(480,380),(720,40),(900,220),(1100,40),(1300,200),(1300,380),
      (550,440),(800,440),(1050,440),(200,440),(50,440),(400,200)]
out+=[C('sky'),F(*SKY)]
out+=[{'op':'pause','s':0.45}]

# board legs into pool (stroke details)
out+=[C('board'),S([(1035,512),(1035,590)],0.1,0.008),S([(1130,512),(1130,590)],0.1,0.008),
      S([(1035,590),(1130,590)],0.1,0.008)]
out+=[C('water2')]
for yy,ph in [(575,0.0),(620,1.1),(670,0.4)]:
    pts=[]
    for x in range(520,1260,16):
        t=(yy-520)/max(1,(740-520))
        left=520+(440-520)*t+28
        right=1220+(1320-1220)*t-28
        if not (left<=x<=right):
            if len(pts)>2: out.append(S(pts,0.12,0.008)); pts=[]
            continue
        if ((x-FX)/FRX)**2+((yy-FY)/FRY)**2 < 1.05:
            if len(pts)>2: out.append(S(pts,0.12,0.008)); pts=[]
            continue
        pts.append((x,yy+4.5*math.sin(x/28+ph)))
    if len(pts)>2: out.append(S(pts,0.12,0.008))

out+=[C('sun')]
for k in range(10):
    a=2*math.pi*k/10
    out.append(S([(SX+(SR+12)*math.cos(a),SY+(SR+12)*math.sin(a)),
                  (SX+(SR+34)*math.cos(a),SY+(SR+34)*math.sin(a))],0,0.008))
out+=[C('dkgreen')]
for x,y in [(45,GHY+40),(150,GHY+55),(280,GHY+35),(360,760),(180,700),(70,640),
            (1320,GHY+45),(1240,760),(700,765),(1000,768),(55,760)]:
    for dx in (-10,0,10): out.append(S([(x,y+14),(x+dx,y)],0.2))
for (x,y) in [(75,560),(190,745),(300,540),(390,755),(1285,540),(1210,745),(55,745)]:
    out+=[C('flower')]+[dot(x+8*math.cos(2*math.pi*k/5),y+8*math.sin(2*math.pi*k/5),5) for k in range(5)]+[C('sun'),dot(x,y,4)]
out+=[C('white')]+[dot(FX+98,FY-8,4),dot(FX+105,FY+12,3),dot(FX-100,FY+6,3)]
out+=[C('ink')]
for x,y in [(780,60),(860,90),(1170,50)]:
    out.append(S(cr([(x-16,y),(x-8,y-7),(x,y),(x+8,y-7),(x+16,y)],5),0,0.008))

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
            for r in range(0,8):
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        x,y=x0+dx,y0+dy
                        if 0<=x<1360 and 0<=y<790 and ok is None and len(im.crop((x-3,y-3,x+4,y+4)).getcolors(500) or [0,0])==1 and im.getpixel((x,y))==(255,255,255):
                            ok=(x,y)
                if ok: break
            if ok:
                ImageDraw.floodfill(im,ok,cc)
                keep.append(list(ok))
            else: print('drop seed',o_c,s)
        if not keep:
            im.save('./preview_fail.png'); raise SystemExit('no seeds kept: '+str(o_c))
        o['seeds']=keep
im.save('./preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255))
print('white px left',white)
print('top',Counter(im.getdata()).most_common(12))
skin=sum(1 for p in im.getdata() if p==(247,172,196))
assert skin<80000, skin
assert white<120000, white

D={'name':'peppa-pool','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa at outdoor swimming pool: rectangular blue pool, yellow float ring, diving board, ladder, sun, clouds, grass, flowers. Bucket fills for flats.'}
json.dump(D,open('./peppa_pool_strokes.json','w'))
gpl='GIMP Palette\nName: Peppa12\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal)
open('./peppa12.gpl','w').write(gpl)
open('./peppa.gpl','w').write(gpl)
print(len(out),'ops')
