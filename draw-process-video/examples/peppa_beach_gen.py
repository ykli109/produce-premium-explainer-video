import json,math,random
random.seed(27)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],['shoe',[25,20,22]],
['sky',[150,205,245]],['sea',[60,150,215]],['shore',[35,100,170]],['sand',[246,218,150]],['castle',[226,178,100]],['door',[150,95,50]],
['sun',[255,206,50]],['cloudline',[120,150,190]],['cloud',[246,249,255]],['bucket',[70,130,225]],['star',[255,140,50]],['shell',[255,170,205]],['sunray',[255,170,40]]]
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
# 1) Peppa (left)
PS,PX,PY=0.8,230,215
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.6}]
# 2) sandcastle silhouette: three crenellated towers on a wall
def tower(x0,top,u=22):
    return [(x0,top),(x0,top-u),(x0+u,top-u),(x0+u,top),(x0+2*u,top),(x0+2*u,top-u),(x0+3*u,top-u),(x0+3*u,top),(x0+4*u,top),(x0+4*u,top-u),(x0+5*u,top-u),(x0+5*u,top)]
BASE=762
P=[(860,BASE)]+tower(860,620)+[(970,672),(1000,672)]+tower(1000,590)+[(1110,672),(1140,672)]+tower(1140,620)+[(1250,BASE)]
out+=[C('ink'),S(poly(P),0.25,0.009)]
# door arch on the centre tower (closed by the base line)
door=[(1032,BASE+2),(1032,722)]+[(1055-23*math.cos(math.pi*k/16),722-26*math.sin(math.pi*k/16)) for k in range(1,16)]+[(1078,722),(1078,BASE+2)]
out.append(S(door,0.2,0.009))
# flag on the centre merlon
out.append(S([(1055,568),(1055,500)],0.1,0.009))
out.append(S([(1055,502),(1104,516),(1055,531)],0.15,0.009))
# 3) bucket with handle
BK=[(628,662),(732,662),(716,748),(644,748)]
out+=[S(poly(BK),0.2,0.009)]
out.append(S([(636,664)]+[(680-46*math.cos(math.pi*k/20),664-40*math.sin(math.pi*k/20)) for k in range(1,20)]+[(724,664)],0.15,0.009))
# 4) sun + clouds
SX,SY,SR=115,105,62
out+=[S(ell(SX,SY,SR,SR,72,4),0.2,0.008)]
def cloud(cx,cy,w):
    P=[(cx-w,cy+20),(cx-w-8,cy),(cx-w*.6,cy-22),(cx-w*.2,cy-30),(cx+w*.2,cy-38),(cx+w*.6,cy-24),(cx+w+6,cy-2),(cx+w,cy+20),(cx,cy+24),(cx-w,cy+20)]
    return S(cr(P,8)+[(cx-w-8,cy+8)],0.5)
CL=[(640,110,100),(1150,190,85)]
out+=[C('cloudline')]+[cloud(*c) for c in CL]
# 5) prop fills
out+=[C('castle'),F((915,700),(1055,640),(1195,700),(985,720),(1120,720),(880,610),(1235,610),(1010,580),(1100,580))]
out+=[C('door'),F((1055,742))]
out+=[C('dress'),F((1068,516))]
out+=[C('bucket'),F((680,705))]
out+=[C('sun'),F((SX,SY),(SX-30,SY+20),(SX+30,SY-20)),C('cloud'),F(*[(cx,cy) for cx,cy,w in CL])]
out+=[{'op':'pause','s':0.4}]
# 6) horizon + wavy shoreline (both stop at the dress)
HY,SHY=455,545
hl=side(PS,PX,PY,HY,False); hr=side(PS,PX,PY,HY,True)
out+=[C('shore'),S([(2,HY),(hl[0],HY)],0.2),S([(hr[0],HY),(1358,HY)],0.2)]
sl=side(PS,PX,PY,SHY,False); sr=side(PS,PX,PY,SHY,True)
def wavy(x0,x1,y,ph):
    n=max(2,int((x1-x0)/20)); return [(x0+(x1-x0)*k/n,y+7*math.sin((x0+(x1-x0)*k/n)/38+ph)) for k in range(n+1)]
L=wavy(2,sl[0]-6,SHY,0); L[-1]=(sl[0],sl[1]); R=wavy(sr[0]+6,1358,SHY,0); R[0]=(sr[0],sr[1])
out+=[S(L,0.2),S(R,0.2)]
out+=[C('sand'),F((60,700),(200,620),(500,700),(560,620),(780,640),(800,760),(600,770),(1300,700),(1320,600),(960,600),(1180,600),(300,775),(450,770),(680,640),(1055,570),(1300,770))]
out+=[C('sea'),F((60,500),(200,520),(280,470),(620,500),(800,500),(1000,480),(1200,500),(1320,520),(1080,540),(1030,500),(560,470))]
out+=[C('sky'),F((300,30),(900,30),(1300,30),(40,420),(1300,420),(700,420),(1100,330),(500,300),(250,420),(780,250),(1250,40),(450,40),(870,200),(640,300),(1000,430),(150,260),(30,300),(950,30),(1350,200),(1350,330),(400,180),(1150,110))]
out+=[{'op':'pause','s':0.5}]
# 7) details
out+=[C('sunray')]
for k in range(8):
    a=math.pi*2*k/8+0.2; out.append(S([(SX+(SR+14)*math.cos(a),SY+(SR+14)*math.sin(a)),(SX+(SR+40)*math.cos(a),SY+(SR+40)*math.sin(a))],0,0.01))
out+=[C('ink')]
for x,y,s in [(420,90,1.0),(500,140,0.8),(880,280,0.9),(1290,80,0.8)]:
    out.append(S(cr([(x-24*s,y-6*s),(x-12*s,y-12*s),(x,y)],6)+cr([(x,y),(x+12*s,y-12*s),(x+24*s,y-6*s)],6)[1:],0,0.008))
# castle windows
for x,y in [(915,680),(1195,680),(1055,640)]: out.append(dot(x,y,9))
out+=[C('white')]
for x,y in [(70,490),(160,520),(620,485),(760,515),(880,480),(1180,480),(1300,505),(950,520)]:
    out.append(S([(x-18,y+4),(x-9,y-3),(x,y),(x+9,y-3),(x+18,y+4)],0,0.009))
# starfish
out+=[C('star')]
for cx,cy in [(110,720),(790,735)]:
    for k in range(5):
        a=-math.pi/2+2*math.pi*k/5; out.append(S([(cx,cy),(cx+24*math.cos(a),cy+24*math.sin(a))],0,0.009))
    out.append(dot(cx,cy,9))
out+=[C('shell')]+[dot(x,y,11) for x,y in [(250,760),(560,700),(1310,740),(800,620)]]
# bucket stripe
out+=[C('white'),S([(638,690),(722,690)],0,0.009)]
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
D={'name':'peppa-beach-sandcastle','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa at the seaside: sandcastle with three crenellated towers, arched door and red flag, blue bucket, sea with waves, sun, clouds, seagulls, starfish and shells. Peppa reuses peppa_strokes.json geometry (scaled 0.8).'}
json.dump(D,open('peppa_beach_strokes.json','w'))
with open('peppa7.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa7\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out),'ops')
