import json,math,random
random.seed(23)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],
['grass',[120,195,80]],['dkgreen',[40,90,35]],['sky',[176,206,232]],['cloud',[214,220,230]],['cloudline',[105,120,150]],
['shoe',[25,20,22]],['umbY',[255,208,45]],['umbO',[250,135,40]],['rain',[55,125,215]],['fpink',[255,120,160]],
['fyellow',[255,240,90]],['shell',[200,120,60]],['snail',[245,215,150]]]
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
PS,PX,PY=0.75,384,255
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
# 1) Peppa
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.6}]
# 2) umbrella (ink): dome + scalloped rim, ribs, spike, shaft to her raised hand
UX,UY,UW,UH,NS=740,232,330,165,6
dome=[(UX-UW*math.cos(math.pi*k/60),UY-UH*math.sin(math.pi*k/60)) for k in range(61)]
J=[UX-UW+i*2*UW/NS for i in range(NS+1)]
rim=[]
for i in range(NS,0,-1):
    a,b=J[i],J[i-1]
    rim+=[((a+b)/2+(a-b)/2*math.cos(math.pi*k/12),UY-20*math.sin(math.pi*k/12)) for k in range(13)]
out+=[C('ink'),S(dome+rim+[(UX-UW+4,UY-14)],0.5)]
for i in range(1,NS):
    x=J[i]; mid=((x+UX)/2+(x-UX)*0.18,(UY+UY-UH)/2-10)
    out.append(S(cr([(UX,UY-UH-4),mid,(x,UY+4)],12),0.3))
out.append(S([(UX,UY-UH+2),(UX,UY-UH-26)],0.2)); out.append(dot(UX,UY-UH-30,7))
hand=T((650,368),PS,PX,PY)
out.append(S([(UX,UY+2)]+[(UX+(hand[0]-UX)*t/20,UY+(hand[1]-UY)*t/20) for t in range(1,21)],0.2,0.008))
# J hook below the hand
hx,hy=hand; dx,dy=(hand[0]-UX),(hand[1]-UY); L=math.hypot(dx,dy); ux,uy=dx/L,dy/L
out.append(S(cr([(hx,hy),(hx+ux*26,hy+uy*26),(hx+ux*34-14,hy+uy*34+4),(hx+ux*24-24,hy+uy*24-2)],8),0.1))
# 3) umbrella fills
seeds=[]
for i in range(NS):
    xm=(J[i]+J[i+1])/2+(8 if i==0 else -8 if i==NS-1 else 0); yy=UY-50
    seeds.append((i,(xm,yy)))
out+=[C('umbY'),F(*[p for i,p in seeds if i%2==0]),C('umbO'),F(*[p for i,p in seeds if i%2==1]),{'op':'pause','s':0.4}]
# 4) ground line, stopped at the dress
GY0=600
pl=side(PS,PX,PY,GY0,False); pr=side(PS,PX,PY,GY0,True)
out+=[C('dkgreen'),S(cr([(0,628),(150,612),(pl[0]-40,pl[1]+4),tuple(pl)])),
      S(cr([tuple(pr),(pr[0]+40,pr[1]-2),(900,596),(1100,610),(1250,600),(1359,590)]))]
# 5) clouds
def cloud(cx,cy,w):
    P=[(cx-w,cy+20),(cx-w-8,cy),(cx-w*.6,cy-22),(cx-w*.2,cy-30),(cx+w*.2,cy-38),(cx+w*.6,cy-24),(cx+w+6,cy-2),(cx+w,cy+20),(cx,cy+24),(cx-w,cy+20)]
    return S(cr(P,8)+[(cx-w-8,cy+8)],0.5)
out+=[C('cloudline'),cloud(185,95,115),cloud(1215,105,105)]
# 6) snail on the grass (right)
SX,SY=1110,705
out+=[C('ink'),S(cr([(SX-70,SY+28),(SX-40,SY+34),(SX+40,SY+34),(SX+62,SY+20),(SX+70,SY-12),(SX+82,SY-20),(SX+92,SY-6),(SX+84,SY+20),(SX+70,SY+40),(SX+30,SY+46),(SX-50,SY+44),(SX-76,SY+36),(SX-70,SY+28)],6),0.3),
      S(ell(SX,SY,46,40,60,3),0.3),
      S([(SX+6*t/40*math.cos(t/40*4.2*math.pi)*1.0+0, SY+0) for t in range(0)],0) if False else S([(SX+ (28*(1-t/60))*math.cos(t/60*3.6*math.pi), SY+(24*(1-t/60))*math.sin(t/60*3.6*math.pi)) for t in range(61)],0.1,0.007),
      S([(SX+80,SY-18),(SX+74,SY-46)],0.1),S([(SX+88,SY-16),(SX+98,SY-42)],0.1),dot(SX+74,SY-48,5),dot(SX+99,SY-44,5),dot(SX+82,SY-4,3)]
# 7) background fills
out+=[C('cloud'),F((185,92),(1215,100)),C('shell'),F((SX-34,SY-6),(SX+34,SY+10),(SX,SY-32),(SX,SY+30)),C('snail'),F((SX-56,SY+38),(SX+76,SY+24)),
      C('grass'),F((60,700),(1300,700),(675,770),(150,650),(1300,640),(800,650),(560,775),(440,770),(930,760),(1000,640),(250,770),(520,700),(400,720)),
      C('sky'),F((40,30),(500,30),(900,20),(1300,30),(40,420),(600,420),(700,300),(950,300),(1300,280),(560,300),(400,420),(830,420),(380,250),(880,400),(200,300),(1100,260),(1100,480),(250,520),(760,520),(860,560),(470,380),(1340,560),(20,580),(520,250),(620,250),(720,270),(1000,270)),
      {'op':'pause','s':0.5}]
# 8) details: rain (outside the umbrella), splashes, tufts, flowers
out+=[C('rain')]
def free(x,y):
    if 395<x<1085 and y<595: return False
    if y<150 and (x<330 or x>1080): return False
    return True
drops=[]
for gx in range(30,1360,70):
    for gy in range(165,575,62):
        x=gx+random.uniform(-14,14)+(31 if (gy//62)%2 else 0); y=gy+random.uniform(-10,10)
        if 15<x<1345 and free(x,y) and free(x-6,y+24): drops.append((x,y))
random.shuffle(drops)
for x,y in drops: out.append(S([(x,y),(x-3,y+12),(x-6,y+24)],0.0,0.012))
for x,y in [(80,660),(230,690),(300,745),(1250,660),(1330,720),(960,690)]:
    out.append(S([(x-14,y),(x-8,y-8)],0)); out.append(S([(x+14,y),(x+8,y-8)],0))
out+=[C('dkgreen')]
for x,y in [(40,640),(170,740),(330,660),(1290,610),(1220,750),(960,620),(1000,745),(60,760),(1340,690),(860,740)]:
    for dx in (-11,0,11): out.append(S([(x,y+22),(x+dx,y)],0.2))
for c,(x,y) in [('fyellow',(130,700)),('fpink',(1300,770)),('white',(270,640)),('fpink',(880,680)),('fyellow',(1275,722)),('white',(780,770))]:
    out+=[C(c),dot(x,y,12)]
out+=[C('umbO')]
for x,y in [(130,700),(1300,770),(270,640),(880,680),(1275,722),(780,770)]: out.append(dot(x,y,4))
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
im.save('preview.png')
white=sum(1 for p in im.getdata() if p==(255,255,255)); print('white px left',white)
D={'name':'peppa-rainy-umbrella','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa under a yellow/orange umbrella on a rainy day, grey clouds, raindrops outside the umbrella, snail and flowers on the grass. Peppa reuses peppa_strokes.json geometry (scaled 0.75).'}
json.dump(D,open('peppa_rain_strokes.json','w'))
with open('peppa3.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa3\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out),'ops',len(drops),'drops')
