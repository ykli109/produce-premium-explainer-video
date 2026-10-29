import json,math,random
random.seed(28)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],['shoe',[25,20,22]],
['sky',[150,205,245]],['grass',[120,195,80]],['dkgreen',[50,120,45]],['path',[210,175,110]],['pathline',[160,120,70]],
['sun',[255,206,50]],['cloudline',[120,150,190]],['cloud',[246,249,255]],['sunray',[255,170,40]],
['bike',[45,110,210]],['tire',[35,35,40]],['hub',[220,225,235]],['flower',[255,170,205]]]
def T(p,s,ox,oy): return [round(ox+(p[0]-289)*s,1),round(oy+(p[1]-40)*s,1)]
def char(s,ox,oy,body):
    r=[]
    for o in ops[:44]:
        o=dict(o)
        if o['op']=='stroke': o['pts']=[T(p,s,ox,oy) for p in o['pts']]
        if o['op']=='fill' and o['seeds'][0][1]>600:
            for cx in (419,523):
                pts=[]
                for f in (0.75,0.5,0.25): pts+=[T((cx+30*f*math.cos(2*math.pi*k/30),679+12*f*math.sin(2*math.pi*k/30)),s,ox,oy) for k in range(31)]
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
def F(*s): return {'op':'fill','seeds':[list(x) for x in s]}
def cr(P,n=10):
    P=[P[0]]+P+[P[-1]]; o=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1:i+3]
        for k in range(n):
            t=k/n; o.append(tuple(.5*(2*p1[j]+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t*t+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t**3) for j in (0,1)))
    return o+[P[-2]]
def ell(cx,cy,rx,ry,n=72,extra=4): return [(cx+rx*math.cos(2*math.pi*k/n),cy+ry*math.sin(2*math.pi*k/n)) for k in range(n+extra)]
def dot(cx,cy,r):
    pts=[]
    for rr in [r,r*.66,r*.33,1]: pts+=ell(cx,cy,rr,rr,24,1)
    return S(pts,0,0.006)
def poly(P): return P+[P[0],P[1]]

PS,PX,PY=0.70,260,50
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.55}]
shoeL=T((419,679),PS,PX,PY); shoeR=T((523,679),PS,PX,PY)
seat_x=(shoeL[0]+shoeR[0])/2
seat_y=shoeL[1]-48
GY=shoeL[1]+82
WR=70
RWX=seat_x-140
FWX=seat_x+210
BBX,BBY=(RWX+FWX)/2+10, GY+6
HEADX,HEADY=FWX-38, GY-105
STEM_TOP=HEADY-52
HB_L,HB_R=HEADX-55,HEADX+70
print('shoes',shoeL,shoeR,'seat',round(seat_x,1),round(seat_y,1),'wheels',round(RWX,1),round(FWX,1),round(GY,1))

# wheels
out+=[C('ink')]
out.append(S(ell(RWX,GY,WR,WR,72,4),0.25,0.008))
out.append(S(ell(FWX,GY,WR,WR,72,4),0.25,0.008))
# blue frame tubes
out+=[C('bike')]
out.append(S([(seat_x,seat_y),(BBX,BBY)],0.15,0.01))
out.append(S([(seat_x,seat_y),(HEADX,HEADY)],0.15,0.01))
out.append(S([(HEADX,HEADY),(BBX,BBY)],0.15,0.01))
out.append(S([(RWX+10,GY-8),(BBX,BBY)],0.15,0.01))
out.append(S([(RWX+10,GY+8),(BBX,BBY)],0.15,0.01))
out.append(S([(HEADX,HEADY),(FWX,GY)],0.15,0.01))
out+=[C('ink'),S(ell(seat_x+8,seat_y-8,38,14,48,3),0.2,0.008)]
out+=[C('bike')]
out.append(S([(HEADX,HEADY),(HEADX+5,STEM_TOP)],0.15,0.01))
out.append(S([(HB_L,STEM_TOP),(HB_R,STEM_TOP)],0.2,0.01))
out+=[C('ink')]
out.append(S(ell(HB_L,STEM_TOP,10,10,24,2),0.1,0.008))
out.append(S(ell(HB_R,STEM_TOP,10,10,24,2),0.1,0.008))
out.append(S([(BBX,BBY),(BBX+32,BBY+26)],0.15,0.009))
out.append(S([(BBX+22,BBY+22),(BBX+48,BBY+22)],0.15,0.009))
out.append(S([(BBX,BBY),(BBX-30,BBY-24)],0.15,0.009))
out.append(S([(BBX-42,BBY-24),(BBX-16,BBY-24)],0.15,0.009))

SX,SY,SR=120,105,60
out+=[C('ink'),S(ell(SX,SY,SR,SR,72,4),0.2,0.008)]
def cloud(cx,cy,w):
    P=[(cx-w,cy+18),(cx-w-10,cy),(cx-w*.55,cy-24),(cx-w*.15,cy-32),(cx+w*.25,cy-40),(cx+w*.6,cy-26),(cx+w+8,cy-4),(cx+w,cy+18),(cx,cy+22),(cx-w,cy+18)]
    return S(cr(P,10)+[(cx-w-6,cy+6)],0.45)
CL=[(640,105,100),(1220,170,85)]
out+=[C('cloudline')]+[cloud(*c) for c in CL]

out+=[C('tire'),F((RWX,GY),(RWX-25,GY),(RWX+25,GY),(RWX,GY-30),(FWX,GY),(FWX-25,GY),(FWX+25,GY),(FWX,GY-30))]
out+=[C('shoe'),dot(seat_x+8,seat_y-8,12)]
out+=[C('bike'),dot(HB_L,STEM_TOP,8),dot(HB_R,STEM_TOP,8)]
out+=[C('sun'),F((SX,SY),(SX-20,SY+10),(SX+20,SY-10))]
out+=[C('cloud'),F(*[(cx,cy) for cx,cy,w in CL])]
out+=[{'op':'pause','s':0.4}]

# FULL-WIDTH path top/bottom to seal bands; grass/sky split at GHY via Peppa
HY=GY+WR-2
PATH_TOP=HY-28; PATH_BOT=min(784,HY+48)
out+=[C('pathline')]
# full width sealed path edges
out.append(S([(2,PATH_TOP),(1358,PATH_TOP)],0.2,0.01))
out.append(S([(2,PATH_BOT),(1358,PATH_BOT)],0.2,0.01))
# also close path ends at canvas sides
out.append(S([(2,PATH_TOP),(2,PATH_BOT)],0.2,0.01))
out.append(S([(1358,PATH_TOP),(1358,PATH_BOT)],0.2,0.01))

GHY=400
pl=side(PS,PX,PY,GHY,False); pr=side(PS,PX,PY,GHY,True)
out+=[C('dkgreen')]
# left grass-sky divider into Peppa; right out of Peppa — Peppa body seals the gap
out.append(S([(2,GHY),(pl[0],pl[1])],0.25,0.01))
out.append(S([(pr[0],pr[1]),(1358,GHY)],0.25,0.01))
# vertical seals at canvas sides from GHY down to PATH_TOP (grass band)
out.append(S([(2,GHY),(2,PATH_TOP)],0.2,0.01))
out.append(S([(1358,GHY),(1358,PATH_TOP)],0.2,0.01))

# path band only
out+=[C('path'),F(
    (100, (PATH_TOP+PATH_BOT)/2),(400,(PATH_TOP+PATH_BOT)/2),(700,(PATH_TOP+PATH_BOT)/2),
    (1000,(PATH_TOP+PATH_BOT)/2),(1200,(PATH_TOP+PATH_BOT)/2),(200,(PATH_TOP+PATH_BOT)/2+10)
)]
# grass band ONLY between GHY and PATH_TOP (and tiny strip below PATH_BOT)
mid_g=(GHY+PATH_TOP)/2
out+=[C('grass'),F(
    (80,mid_g),(300,mid_g),(600,mid_g),(900,mid_g),(1200,mid_g),(1100,mid_g-20),(200,mid_g+20),
    (100,PATH_BOT+20),(400,PATH_BOT+25),(800,PATH_BOT+20),(1200,PATH_BOT+22),(700,770)
)]
# sky ONLY above GHY
out+=[C('sky'),F(
    (80,40),(400,40),(800,40),(1200,40),(200,200),(600,180),(1000,160),(1300,120),
    (80,300),(500,280),(900,250),(1200,220),(300,350),(700,330),(1100,GHY-30),(200,GHY-40)
)]
out+=[{'op':'pause','s':0.5}]

# details
out+=[C('hub')]
for cx in (RWX,FWX):
    out.append(dot(cx,GY,16))  # scribble hub on tire (no flood — interior is tire-colored)
out+=[C('ink')]
for cx in (RWX,FWX):
    r2=WR-22
    out.append(S([(cx,GY-r2),(cx,GY+r2)],0,0.009))
    out.append(S([(cx-r2,GY),(cx+r2,GY)],0,0.009))
    out.append(S([(cx-r2*0.7,GY-r2*0.7),(cx+r2*0.7,GY+r2*0.7)],0,0.009))
    out.append(S([(cx-r2*0.7,GY+r2*0.7),(cx+r2*0.7,GY-r2*0.7)],0,0.009))
out+=[C('sunray')]
for k in range(8):
    a=math.pi*2*k/8+0.25
    out.append(S([(SX+(SR+12)*math.cos(a),SY+(SR+12)*math.sin(a)),(SX+(SR+38)*math.cos(a),SY+(SR+38)*math.sin(a))],0,0.01))
out+=[C('ink')]
for x,y,s in [(420,80,1.0),(520,135,0.85),(1000,60,0.9)]:
    out.append(S(cr([(x-24*s,y-6*s),(x-12*s,y-12*s),(x,y)],6)+cr([(x,y),(x+12*s,y-12*s),(x+24*s,y-6*s)],6)[1:],0,0.008))
out+=[C('dkgreen')]
for x,y in [(60,GHY+30),(180,PATH_BOT+18),(650,PATH_BOT+22),(1280,GHY+25),(1220,PATH_BOT+16),(970,GHY+20),(320,PATH_BOT+28)]:
    for dx in (-11,0,11): out.append(S([(x,y+16),(x+dx,y)],0.2))
FL=[(100,PATH_BOT+35),(300,765),(750,PATH_BOT+30),(1120,PATH_BOT+35),(1320,PATH_BOT+25),(200,mid_g),(500,mid_g-10),(900,mid_g)]
out+=[C('flower')]+[dot(x,y,11) for x,y in FL]
out+=[C('sun')]+[dot(x,y,4) for x,y in FL]
out+=[C('pathline')]
for x0 in range(50,1330,75):
    out.append(S([(x0,HY),(x0+38,HY)],0,0.01))
out+=[C('sun'),dot(HB_R-20,STEM_TOP-18,9)]
out+=[C('ink'),S(ell(HB_R-20,STEM_TOP-18,9,9,24,1),0,0.008)]

from PIL import Image,ImageDraw
im=Image.new('RGB',(1360,790),'white');d=ImageDraw.Draw(im);col=dict((n,tuple(c)) for n,c in pal);cc=None
def clamp(p): return [min(max(p[0],2),1357),min(max(p[1],2),787)]
for o in out:
    if o['op']=='color':cc=col[o['c']];o_c=o['c']
    if o['op']=='stroke':
        o['pts']=[clamp(p) for p in o['pts']]
        d.line([tuple(p) for p in o['pts']],fill=cc,width=9,joint='curve')
        for q in (o['pts'][0],o['pts'][-1]): d.ellipse([q[0]-4.5,q[1]-4.5,q[0]+4.5,q[1]+4.5],fill=cc)
    if o['op']=='fill':
        keep=[]
        for s in o['seeds']:
            x0,y0=map(int,s); ok=None
            for r in range(0,12):
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        x,y=x0+dx,y0+dy
                        if 0<=x<1360 and 0<=y<790 and ok is None and im.crop((x-3,y-3,x+4,y+4)).getcolors(500)==[(49,(255,255,255))]: ok=(x,y)
                if ok: break
            if ok: ImageDraw.floodfill(im,ok,cc); keep.append(list(ok))
            else: print('drop seed',o_c,s)
        if not keep: im.save("preview_fail.png"); raise SystemExit("no seeds kept: "+o_c)
        o['seeds']=keep
im.save('preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255)); print('white px left',white)
from collections import Counter
print('top',Counter(im.getdata()).most_common(8))
D={'name':'peppa-riding-bike','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa riding a blue bicycle on a sunny grassy path: two spoked wheels, blue frame, handlebars, seat, pedals; dirt path, grass, sun, clouds, birds, flowers. Peppa reuses peppa_strokes.json geometry (scaled 0.70).'}
json.dump(D,open('peppa_bike_strokes.json','w'))
with open('peppa8.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa8\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out),'ops')
