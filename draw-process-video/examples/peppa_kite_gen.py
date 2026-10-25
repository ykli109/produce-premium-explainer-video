import json,math,random
random.seed(26)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],['shoe',[25,20,22]],
['sky',[150,205,245]],['grass',[120,195,80]],['dkgreen',[50,120,45]],['sun',[255,206,50]],['cloudline',[120,150,190]],['cloud',[246,249,255]],
['kiteY',[255,214,60]],['kiteB',[70,130,225]],['string',[110,90,80]],['bow',[240,90,120]],['flower',[255,170,205]],['sunray',[255,170,40]]]
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
# 1) Peppa (left), arm toward the kite
PS,PX,PY=0.8,230,215
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.6}]
hand=T((646,378),PS,PX,PY)
# 2) kite (ink): diamond + cross spars
KX,KT,KB,KL,KR,KY=1060,40,350,955,1165,165
top,bot,lft,rgt=(KX,KT),(KX,KB),(KL,KY),(KR,KY)
out+=[C('ink'),S(poly([top,rgt,bot,lft]),0.3)]
out.append(S([(KX,KT+4),(KX,KB-4)],0.2)); out.append(S([(KL+4,KY),(KR-4,KY)],0.2))
# 3) kite string from Peppa's hand up to the bottom of the kite (gentle sag)
out+=[C('string'),S(cr([(hand[0]+2,hand[1]-2),(700,470),(900,420),(KX,KB+2)],14),0.2,0.008)]
# 4) kite tail with bows
tail=cr([(KX,KB),(1090,400),(1060,450),(1110,500),(1150,520)],12)
out+=[C('ink'),S(tail,0.2,0.008)]
BOWS=[tail[12],tail[24],tail[36]]
# 5) sun + clouds outlines
SX,SY,SR=115,105,62
out+=[C('ink'),S(ell(SX,SY,SR,SR,72,4),0.2,0.008)]
def cloud(cx,cy,w):
    P=[(cx-w,cy+20),(cx-w-8,cy),(cx-w*.6,cy-22),(cx-w*.2,cy-30),(cx+w*.2,cy-38),(cx+w*.6,cy-24),(cx+w+6,cy-2),(cx+w,cy+20),(cx,cy+24),(cx-w,cy+20)]
    return S(cr(P,8)+[(cx-w-8,cy+8)],0.5)
CL=[(640,110,100),(1275,330,70)]
out+=[C('cloudline')]+[cloud(*c) for c in CL]
# 6) prop fills: kite quarters, sun, clouds
out+=[C('kiteY'),F((KX-30,KY-40),(KX+40,KY+60)),C('kiteB'),F((KX+30,KY-40),(KX-40,KY+60))]
out+=[C('sun'),F((SX,SY),(SX-30,SY+20),(SX+30,SY-20)),C('cloud'),F(*[(cx,cy) for cx,cy,w in CL])]
out+=[C('bow')]
for x,y in BOWS: out+=[dot(x-14,y,10),dot(x+14,y,10)]
out+=[C('ink')]+[dot(x,y,4) for x,y in BOWS]
out+=[{'op':'pause','s':0.4}]
# 7) ground line (stops at the dress)
HY=600
pl=side(PS,PX,PY,HY,False); pr=side(PS,PX,PY,HY,True)
out+=[C('dkgreen'),S(cr([(2,585),(100,575),(pl[0],pl[1])],8),0.4)]
out.append(S(cr([(pr[0],pr[1]),(650,592),(900,575),(1150,585),(1358,565)],10),0.4))
out+=[C('grass'),F((60,700),(1300,700),(700,740),(150,650),(1300,640),(800,650),(560,775),(440,770),(930,760),(1000,640),(250,770),(520,700),(400,720),(1200,760))]
out+=[C('sky'),F((300,30),(900,30),(1300,30),(40,450),(1300,450),(700,420),(1100,260),(500,300),(250,420),(780,250),(1250,40),(450,40),(870,200),(1050,480),(640,540),(1000,550),(850,560),(1300,250),(400,180),(150,260),(1240,420),(30,520),(30,300),(950,30),(1350,200),(560,480),(800,520),(1200,520))]
out+=[{'op':'pause','s':0.5}]
# 8) details: sun rays, birds, grass tufts, flowers
out+=[C('sunray')]
for k in range(8):
    a=math.pi*2*k/8+0.2; out.append(S([(SX+(SR+14)*math.cos(a),SY+(SR+14)*math.sin(a)),(SX+(SR+40)*math.cos(a),SY+(SR+40)*math.sin(a))],0,0.01))
out+=[C('ink')]
for x,y,s in [(420,90,1.0),(500,140,0.8),(820,250,0.9)]:
    out.append(S(cr([(x-24*s,y-6*s),(x-12*s,y-12*s),(x,y)],6)+cr([(x,y),(x+12*s,y-12*s),(x+24*s,y-6*s)],6)[1:],0,0.008))
out+=[C('dkgreen')]
for x,y in [(60,650),(170,740),(640,690),(1290,620),(1220,750),(960,630),(1000,745),(860,740)]:
    for dx in (-11,0,11): out.append(S([(x,y+22),(x+dx,y)],0.2))
FL=[(110,700),(300,760),(720,650),(1100,690),(1320,700),(820,770),(560,710)]
out+=[C('flower')]+[dot(x,y,11) for x,y in FL]
out+=[C('sun')]+[dot(x,y,4) for x,y in FL]
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
D={'name':'peppa-flying-kite','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa flying a yellow/blue diamond kite with a bow tail on a sunny day: sun with rays, clouds, birds, grass tufts and flowers. Peppa reuses peppa_strokes.json geometry (scaled 0.8).'}
json.dump(D,open('peppa_kite_strokes.json','w'))
with open('peppa6.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa6\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out),'ops')
