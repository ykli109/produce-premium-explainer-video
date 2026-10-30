#!/usr/bin/env python3
"""Peppa building a snowman (drawing-peppa-pig-11).
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
 ['sky',[150,200,240]],['snow',[228,239,250]],['snowman',[250,251,255]],['carrot',[255,140,30]],
 ['tree',[40,130,75]],['trunk',[125,80,45]],['scarf',[50,105,215]],['scarf2',[255,215,60]],['foot',[180,198,222]],
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

PS,PX,PY=0.70,140,140
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.5}]
GHY=490
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
# ---- snowman ----
BX,BY,BRX,BRY=930,560,125,115
HX,HY,HRX,HRY=930,397,70,62
out+=[C('ink'),S(ell(BX,BY,BRX,BRY,90,4),0.15,0.008),S(ell(HX,HY,HRX,HRY,72,4),0.15,0.008)]
# top hat: brim + crown (crown sits on brim)
out+=[S(poly([(858,313),(1002,313),(1002,336),(858,336)]),0.05,0.009),
      S([(887,316),(887,222),(973,222),(973,316)],0.05,0.009)]
# carrot nose outline
out+=[S(poly([(938,392),(1010,404),(938,414)]),0.05,0.008)]
# trees
def pine(cx,base,sc):
    P=[(0,-220),(50,-140),(28,-140),(80,-70),(50,-70),(105,0),(-105,0),(-50,-70),(-80,-70),(-28,-140),(-50,-140)]
    return [(cx+x*sc,base+y*sc) for x,y in P]
TREES=[(600,462,1.0),(1235,468,0.8)]
for cx,b,sc in TREES:
    out+=[C('ink'),S(poly(pine(cx,b,sc)),0.1,0.009)]
    out+=[S([(cx-15*sc,b-3),(cx-15*sc,GHY+4)],0.05,0.01),S([(cx+15*sc,b-3),(cx+15*sc,GHY+4)],0.05,0.01)]
# clouds
def cloud(cx,cy,sc):
    P=[]
    for k in range(90):
        a=2*math.pi*k/90; b=1+0.18*abs(math.sin(2.5*a)) if math.sin(a)<0.2 else 1
        P.append((cx+80*sc*b*math.cos(a),cy+36*sc*b*math.sin(a)))
    return S(P+P[:3],0.1,0.008)
CLOUDS=[(640,95,1.0),(1180,120,1.05)]
out+=[C('ink')]+[cloud(*c) for c in CLOUDS]
# snowy horizon: stops at the dress and at the snowman body
dl=side(PS,PX,PY,GHY,False); dr=side(PS,PX,PY,GHY,True)
dy=GHY-BY; dx=BRX*math.sqrt(1-(dy/BRY)**2)
def wav(x0,x1):
    n=max(2,int((x1-x0)/40)); return [(x0+(x1-x0)*k/n, GHY+ (0 if k in (0,n) else 6*math.sin(k*1.3))) for k in range(n+1)]
out+=[C('ink'),S(wav(2,dl[0]+2),0.0,0.01),S(wav(dr[0]-2,BX-dx+4),0.0,0.01),S(wav(BX+dx-4,1358),0.0,0.01)]
out+=[{'op':'pause','s':0.4}]
# ---- bucket fills ----
out+=[C('snowman'),F((BX,BY+20),(BX-60,BY+50),(BX+60,BY+50),(BX,BY-60)),F((HX-30,HY+15),(HX,HY-30),(HX+20,HY+35))]
out+=[C('carrot'),F((955,403))]
out+=[C('shoe'),F((930,325),(875,325),(985,325)),F((930,270),(900,240),(960,290))]
for cx,b,sc in TREES:
    out+=[C('tree'),F((cx,b-30*sc),(cx,b-100*sc),(cx,b-170*sc),(cx-70*sc,b-15*sc),(cx+70*sc,b-15*sc))]
    out+=[C('trunk'),F((cx,(b+GHY)/2))]
G=[(x,y) for x in range(30,1360,70) for y in range(515,790,55)]
out+=[C('snow'),F(*G)]
SKY=[(x,y) for x in range(30,1360,75) for y in range(25,485,60) if not any(abs(x-a)<100*k and abs(y-b)<50*k for a,b,k in CLOUDS)]+[(870,350),(990,350),(860,300),(1000,300),(870,450),(990,450),(470,480),(760,480),(1100,480),(840,480),(1020,480)]
out+=[C('sky'),F(*SKY)]
out+=[{'op':'pause','s':0.45}]
# ---- details ----
out+=[C('dress'),S([(889,300),(971,300)],0,0.008),S([(889,306),(971,306)],0,0.008)]   # hat band
out+=[C('ink'),dot(905,377,8),dot(955,377,8)]
for k in range(5):
    a=math.pi*(0.25+0.5*k/4); out.append(dot(HX+30*math.cos(a)-2,HY+2+28*math.sin(a),4))
for y in (520,575,630): out.append(dot(BX,y,9))
# scarf (narrow band, strokes)
sc=[(868,455),(900,468),(930,472),(960,468),(992,455)]
out+=[C('scarf')]+[S([(x,y+o) for x,y in sc],0.05,0.008) for o in (-6,0,6)]
out+=[S([(970,470),(980,510)],0.05,0.008),S([(980,470),(990,508)],0.05,0.008),S([(960,470),(970,512)],0.05,0.008)]
out+=[C('scarf2'),S([(890,466),(892,472)],0,0.008),S([(930,472),(930,478)],0,0.008),S([(975,500),(983,500)],0,0.008)]
# stick arms
out+=[C('trunk'),S([(812,515),(760,470),(720,438)],0.2,0.009),S([(760,470),(752,438)],0.1,0.009),
      S([(1048,515),(1100,470),(1140,438)],0.2,0.009),S([(1100,470),(1108,438)],0.1,0.009)]
# snow caps on trees
out+=[C('white')]
for cx,b,sc in TREES:
    for yy,w in ((-140,22),(-70,40),(0,60)):
        out.append(S([(cx-w*sc,b+yy*sc-6),(cx,b+yy*sc-12),(cx+w*sc,b+yy*sc-6)],0.1,0.008))
# snowballs on ground
out+=[C('ink'),S(ell(1150,690,32,30,48,4),0.1,0.008),S(ell(1215,710,22,20,40,4),0.1,0.008),C('snowman'),F((1150,690)),F((1215,710))]
# footprints
out+=[C('foot')]+[dot(x,y,6) for x,y in [(470,700),(520,680),(575,705),(625,684),(680,708),(730,690)]]
# falling snowflakes (sky only)
random.seed(7); FL=[]
while len(FL)<26:
    x,y=random.randint(30,1330),random.randint(25,460)
    if 100<x<460 and y>60: continue           # Peppa
    if 480<x<720 and y>220: continue           # left tree
    if 780<x<1080 and y>200: continue          # snowman+hat
    if 1130<x<1340 and y>260: continue         # right tree
    if any(abs(x-a)<105*k and abs(y-b)<55*k for a,b,k in CLOUDS): continue
    if any(abs(x-p)<55 and abs(y-q)<55 for p,q in FL): continue
    FL.append((x,y))
out+=[C('white')]
for x,y in FL:
    r=9 if random.random()<0.5 else 6
    for a in (0,60,120):
        t=math.radians(a); out.append(S([(x-r*math.cos(t),y-r*math.sin(t)),(x+r*math.cos(t),y+r*math.sin(t))],0,0.006))
FOODS={'carrot','snowman'}

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
            im.save('./preview_fail.png'); raise SystemExit('no seeds kept: '+str(o_c))
        o['seeds']=keep
im.save('./preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255))
print('white px left',white)
print('top',Counter(im.getdata()).most_common(10))
skin=sum(1 for p in im.getdata() if p==(247,172,196))
assert skin<80000, skin
assert white<120000, white

D={'name':'peppa-snowman','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa building a snowman: snowman with top hat, carrot nose, scarf and stick arms; pine trees with snow caps, snowballs, footprints, clouds and falling snowflakes. Bucket fills for flats.'}
json.dump(D,open('./peppa_snowman_strokes.json','w'))
gpl='GIMP Palette\nName: Peppa11\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal)
open('./peppa11.gpl','w').write(gpl)
open('./peppa.gpl','w').write(gpl)
print(len(out),'ops')
