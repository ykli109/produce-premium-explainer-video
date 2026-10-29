#!/usr/bin/env python3
"""Peppa + carved Halloween jack-o'-lantern (drawing-peppa-pig-9).
Fills use paint-bucket seeds; large flats are never brush-painted."""
import json,math,random
from collections import Counter
from PIL import Image,ImageDraw
random.seed(29)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[
 ['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],
 ['white',[255,255,255]],['shoe',[25,20,22]],
 ['sky',[92,70,150]],['grass',[92,150,55]],['dkgreen',[45,95,35]],
 ['pumpkin',[235,120,30]],['pdark',[180,70,15]],['stem',[60,120,45]],
 ['moon',[255,230,140]],['glow',[255,210,80]],
 ['leaf1',[230,90,40]],['leaf2',[240,180,50]],['leaf3',[200,50,50]],
 ['bat',[35,30,40]],['bucket',[90,50,160]],['fence',[140,95,55]],
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

# Peppa mid-left (placement proven to seal skin fill)
PS,PX,PY=0.70,140,55
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.5}]
shoeL=T((419,679),PS,PX,PY); shoeR=T((523,679),PS,PX,PY)
print('shoes',shoeL,shoeR)

# Big jack-o'-lantern
PCX,PCY,PRX,PRY=1000,455,200,165
out+=[C('ink')]
out.append(S(ell(PCX,PCY,PRX,PRY,84,5),0.25,0.008))  # closed body
# interior lobe marks — stop short of outline so body stays one fill region
for dx in (-80,-25,25,80):
    out.append(S([(PCX+dx,PCY-PRY+45),(PCX+dx+6,PCY),(PCX+dx,PCY+PRY-50)],0.1,0.01))
# stem (closed)
STEM=poly([(PCX-16,PCY-PRY+12),(PCX-8,PCY-PRY-50),(PCX+10,PCY-PRY-58),(PCX+20,PCY-PRY-18),(PCX+12,PCY-PRY+14)])
out.append(S(cr(STEM,8),0.2,0.009))
# face features drawn after pumpkin fill (glow scribbles) — avoids leaky cutouts

# candy bucket
BX,BY=520,620
out+=[C('ink')]
out.append(S(poly([(BX-52,BY-65),(BX-48,BY+32),(BX+48,BY+32),(BX+52,BY-65)]),0.2,0.009))
out.append(S(cr([(BX-38,BY-65),(BX,BY-108),(BX+38,BY-65)],10),0.2,0.01))
# tiny jack face on bucket drawn as dots (too small for reliable bucket fill)
out+=[C('glow'),dot(BX-14,BY-32,5),dot(BX+14,BY-32,5),dot(BX,BY-12,4)]
out+=[C('ink')]

# moon
MX,MY,MR=1180,120,52
out+=[C('ink'),S(ell(MX,MY,MR,MR,64,4),0.2,0.008)]

# bats
def bat(cx,cy,sc=1.0):
    P=[(cx-38*sc,cy),(cx-26*sc,cy-16*sc),(cx-8*sc,cy-6*sc),(cx,cy-20*sc),
       (cx+8*sc,cy-6*sc),(cx+26*sc,cy-16*sc),(cx+38*sc,cy),(cx+20*sc,cy+5*sc),
       (cx+6*sc,cy-2*sc),(cx,cy+8*sc),(cx-6*sc,cy-2*sc),(cx-20*sc,cy+5*sc)]
    return S(cr(poly(P),5),0.15,0.008)
BATS=[(700,110,1.0),(840,75,0.72),(1100,190,0.85)]
out+=[C('ink')]+[bat(x,y,s) for x,y,s in BATS]

# fence behind Peppa
out+=[C('ink')]
for fx in (30,90,150):
    out.append(S([(fx,400),(fx,520)],0.15,0.01))
out.append(S([(20,430),(170,430)],0.15,0.01))
out.append(S([(20,480),(170,480)],0.15,0.01))

# ground line — FULL WIDTH to seal sky/grass (overlaps Peppa legs + pumpkin; avoids KolourPaint wobble leaks)
GHY=520
out+=[C('dkgreen')]
out.append(S([(2,GHY),(1358,GHY)],0.2,0.01))
out.append(S([(2,GHY),(2,787)],0.2,0.01))
out.append(S([(1358,GHY),(1358,787)],0.2,0.01))
# second pass slightly thicker via parallel line
out.append(S([(2,GHY+3),(1358,GHY+3)],0.15,0.01))
out+=[{'op':'pause','s':0.4}]

# ---- bucket fills ----
out+=[C('pumpkin'),F((PCX,PCY+50),(PCX-110,PCY+10),(PCX+110,PCY+10),(PCX,PCY-60),(PCX-50,PCY+90),(PCX+50,PCY+90),(PCX-140,PCY-20),(PCX+140,PCY-20))]
out+=[C('stem'),F((PCX+2,PCY-PRY-28),(PCX+6,PCY-PRY-40))]
out+=[C('stem'),dot(PCX+2,PCY-PRY-30,8),dot(PCX+4,PCY-PRY-42,6)]
# jack-o'-lantern face: ink outline then glow concentric fills via scribbles (not bucket)
out+=[C('ink')]
out.append(S(tri(PCX-68,PCY-38,26,30),0.1,0.008))
out.append(S(tri(PCX+68,PCY-38,26,30),0.1,0.008))
out.append(S(tri(PCX,PCY+8,16,20),0.1,0.008))
SM=[]
for k in range(30):
    a=math.pi*0.2+math.pi*0.6*k/29
    SM.append((PCX+88*math.cos(a), PCY+58+48*math.sin(a)))
out.append(S(SM,0.15,0.008))
out+=[C('glow')]
# eyes / nose solid via dots
for cx,cy,r in [(PCX-68,PCY-32,14),(PCX+68,PCY-32,14),(PCX,PCY+12,10)]:
    out.append(dot(cx,cy,r))
# smile glow: thick parallel arcs
for off in range(-10,12,4):
    arc=[(PCX+ (88-abs(off)*0.3)*math.cos(a), PCY+58+off + (48-abs(off)*0.2)*math.sin(a))
         for a in [math.pi*0.22+math.pi*0.56*k/24 for k in range(25)]]
    out.append(S(arc,0,0.007))
out+=[C('bucket'),F((BX,BY-15),(BX-15,BY+5),(BX+15,BY-35))]
out+=[C('moon'),F((MX,MY),(MX-12,MY+8),(MX+12,MY-8))]
out+=[C('bat')]
for x,y,sc in BATS:
    out.append(dot(x,y,10*sc))
    out.append(dot(x-16*sc,y-4*sc,7*sc))
    out.append(dot(x+16*sc,y-4*sc,7*sc))
out+=[C('fence'),F((60,450),(120,455),(60,500))]
out+=[C('grass'),F(
    (60,650),(250,700),(450,640),(650,720),(850,660),(1050,700),(1250,650),
    (150,560),(500,550),(800,560),(1150,570),(350,760),(750,770),(1100,750),
    (100,GHY+40),(400,GHY+50),(700,GHY+30),(1000,GHY+45),(1300,GHY+35),
    (300,600),(900,600),(1200,620),(600,680)
)]
out+=[C('sky'),F(
    (60,30),(350,30),(700,30),(1100,30),(1300,40),
    (100,180),(400,150),(800,140),(1200,160),
    (80,320),(450,300),(850,280),(1200,260),
    (200,GHY-50),(550,GHY-45),(900,GHY-40),(1250,GHY-50)
)]
out+=[{'op':'pause','s':0.45}]

# details
LEAVES=[(50,600),(130,690),(210,560),(300,730),(420,690),(580,750),(720,590),
        (800,710),(1140,640),(1260,690),(1320,560),(180,750),(960,755),(40,750)]
for i,(lx,ly) in enumerate(LEAVES):
    out+=[C(['leaf1','leaf2','leaf3'][i%3]), dot(lx,ly,8)]
out+=[C('leaf2'),dot(BX-16,BY-52,6),dot(BX+12,BY-58,5)]
out+=[C('leaf1'),dot(BX+4,BY-45,5)]
out+=[C('white'),dot(BX-4,BY-55,4)]
out+=[C('dkgreen')]
for x,y in [(40,GHY+35),(170,GHY+50),(380,GHY+30),(640,GHY+45),(1080,GHY+35),(1280,GHY+40),(580,755),(880,760)]:
    for dx in (-10,0,10): out.append(S([(x,y+14),(x+dx,y)],0.2))
out+=[C('pdark')]
out.append(S([(PCX-145,PCY-10),(PCX-135,PCY+50),(PCX-125,PCY+95)],0.1,0.01))
out+=[C('moon')]
for x,y in [(200,90),(340,50),(480,130),(620,45),(980,45),(1280,85),(70,170)]:
    out.append(S([(x-6,y),(x+6,y)],0,0.008)); out.append(S([(x,y-6),(x,y+6)],0,0.008))

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
                        if 0<=x<1360 and 0<=y<790 and ok is None and im.crop((x-3,y-3,x+4,y+4)).getcolors(500)==[(49,(255,255,255))]:
                            ok=(x,y)
                if ok: break
            if ok:
                ImageDraw.floodfill(im,ok,cc)
                keep.append(list(ok))
            else: print('drop seed',o_c,s)
        if not keep:
            im.save('/workspace/peppa9/preview_fail.png'); raise SystemExit('no seeds kept: '+str(o_c))
        o['seeds']=keep
im.save('/workspace/peppa9/preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255))
print('white px left',white)
print('top',Counter(im.getdata()).most_common(10))
skin=sum(1 for p in im.getdata() if p==(247,172,196))
assert skin<80000, skin
assert white<80000, white

D={'name':'peppa-halloween-pumpkin','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':"Peppa with a carved Halloween jack-o'-lantern: orange pumpkin with glowing triangle eyes/nose/smile, green stem, purple candy bucket, dusk purple sky, moon, bats, autumn leaves, fence. Peppa from peppa_strokes.json (scale 0.70). Bucket fills for flats."}
json.dump(D,open('/workspace/peppa9/peppa_halloween_strokes.json','w'))
gpl='GIMP Palette\nName: Peppa9\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal)
open('/workspace/peppa9/peppa9.gpl','w').write(gpl)
open('/workspace/peppa9/peppa.gpl','w').write(gpl)
print(len(out),'ops')
