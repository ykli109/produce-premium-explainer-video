import json,math,random
random.seed(25)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],['shoe',[25,20,22]],
['sky',[38,52,110]],['hill',[86,160,80]],['hill2',[60,128,64]],['moon',[255,232,140]],['star',[255,214,60]],['scope',[90,150,220]],['metal',[150,150,160]],['flower',[255,180,210]],['lamp',[255,240,200]],['crater',[236,200,100]]]
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
PS,PX,PY=0.75,240,250
dress=ops[12]['pts']
def side(s,ox,oy,y,right):
    P=[T(p,s,ox,oy) for p in dress]; c=[p for p in P if abs(p[1]-y)<6]
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
def rect(x0,y0,x1,y1): return [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0-4)]
# 1) Peppa
PS,PX,PY=0.8,300,215
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.6}]
lh=T((292,392),PS,PX,PY)
def poly(P): return P+[P[0],P[1]]
def rot(cx,cy,pts,a):
    ca,sa=math.cos(a),math.sin(a); return [(cx+(x-cx)*ca-(y-cy)*sa, cy+(x-cx)*sa+(y-cy)*ca) for x,y in pts]
# 2) telescope on tripod (right of Peppa)
out+=[C('ink')]
TCX,TCY=900,430; a=-0.45
tube=rot(TCX,TCY,[(TCX-150,TCY-32),(TCX+150,TCY-42),(TCX+150,TCY+42),(TCX-150,TCY+32)],a)
out.append(S(poly(tube),0.3))
lens=rot(TCX,TCY,[(TCX+150,TCY-50),(TCX+190,TCY-54),(TCX+190,TCY+54),(TCX+150,TCY+50)],a)
out.append(S(poly(lens),0.2))
eye=rot(TCX,TCY,[(TCX-150,TCY-18),(TCX-190,TCY-16),(TCX-190,TCY+16),(TCX-150,TCY+18)],a)
out.append(S(poly(eye),0.2))
for fx in (-0.0,):
    pass
out.append(S([(TCX,TCY+40),(TCX-90,700)],0.2)); out.append(S([(TCX,TCY+40),(TCX+90,700)],0.2)); out.append(S([(TCX,TCY+40),(TCX,715)],0.2))
# 3) moon + stars
MX,MY=1170,150
out.append(S(ell(MX,MY,85,85,80,4),0.2,0.008))
def star(cx,cy,r):
    P=[(cx+(r if k%2==0 else r*.45)*math.cos(-math.pi/2+k*math.pi/5),cy+(r if k%2==0 else r*.45)*math.sin(-math.pi/2+k*math.pi/5)) for k in range(10)]
    return S(poly(P),0,0.007)
STARS=[(120,90,30),(330,60,24),(560,120,34),(760,70,26),(1010,190,26),(250,190,26),(680,250,20),(1300,320,22),(80,300,20),(1000,60,20)]
for x,y,r in STARS: out.append(star(x,y,r))
# 4) prop fills
out+=[C('scope'),F(*[(TCX+dx,TCY+dy) for dx,dy in [(-40,20),(40,-20),(0,0)]])]
out+=[C('metal'),F(*[rot(TCX,TCY,[(TCX+170,TCY)],a)[0], rot(TCX,TCY,[(TCX-170,TCY)],a)[0]])]
out+=[C('moon'),F((MX-50,MY+30),(MX+40,MY+40),(MX,MY-50),(MX+40,MY-30))]
out+=[C('crater')]+[dot(cx,cy,r) for cx,cy,r in [(1140,125,15),(1200,180,11),(1195,115,8),(1135,195,7)]]
out+=[C('star')]+[F((x,y)) for x,y,r in STARS]
out+=[{'op':'pause','s':0.4}]
# 5) hills (line stops at dress)
HY=600
pl=side(PS,PX,PY,HY,False); pr=side(PS,PX,PY,HY,True)
def hill(x): return 600-35*math.sin(math.pi*x/1360*1.3)
out+=[C('ink'),S(cr([(2,570),(120,560),(pl[0],pl[1])],8),0.4)]
out.append(S(cr([(pr[0],pr[1]),(700,585),(1000,570),(1200,555),(1358,540)],10),0.4))
out+=[C('hill'),F((TCX-30,690),(TCX+30,690),(TCX-30,620),(TCX+30,620),(60,700),(1300,700),(700,740),(TCX,740),(TCX-50,690),(TCX+50,690),(1200,620),(150,620),(1000,760),(560,760),(60,770),(TCX-110,620),(TCX+110,620))]
out+=[C('sky'),F((TCX-15,545),(TCX+15,545),(TCX-40,560),(TCX+40,560),(20,20),(680,20),(1340,20),(40,450),(1300,450),(700,420),(1100,360),(500,300),(250,420),(780,180),(1250,40),(450,40),(870,40),(1050,250),(180,40),(640,520),(1000,500),(850,560),(960,560),(1300,250),(400,180),(150,220),(1180,280),(1240,420),(30,520))]
out+=[{'op':'pause','s':0.5}]
# 6) details: tiny twinkles, flowers in grass
out+=[C('lamp')]
for x,y in [(650,180),(840,300),(1080,420),(200,480),(620,400),(1320,180),(30,200),(900,30)]:
    out.append(S([(x-9,y),(x+9,y)],0,0.01)); out.append(S([(x,y-9),(x,y+9)],0,0.01))
out+=[C('flower')]
for x,y in [(80,680),(170,740),(640,700),(1080,700),(1180,750),(1300,660),(720,770)]: out.append(dot(x,y,8))
out+=[C('star')]
for x,y in [(80,680),(170,740),(640,700),(1080,700),(1180,750),(1300,660),(720,770)]: out.append(dot(x,y,3))
out+=[C('hill')]
# preview + seed check
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
            for r in range(0,8):
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        x,y=x0+dx,y0+dy
                        if ok is None and im.crop((x-3,y-3,x+4,y+4)).getcolors(500)==[(49,(255,255,255))]: ok=(x,y)
                if ok: break
            if ok: ImageDraw.floodfill(im,ok,cc); keep.append(list(ok))
            else: print('drop seed',o_c,s)
        if not keep: im.save("preview_fail.png"); raise SystemExit("no seeds kept: "+o_c)
        o['seeds']=keep
out=[o for o in out if not (o['op']=='color' and o is out[-1])]
im.save('preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255)); print('white px left',white)
D={'name':'peppa-stargazing','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa stargazing on a night hill: telescope on a tripod, crescent moon, yellow stars, twinkles and flowers. Peppa reuses peppa_strokes.json geometry (scaled 0.8).'}
json.dump(D,open('peppa_stars_strokes.json','w'))
with open('peppa5.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa5\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out),'ops')
