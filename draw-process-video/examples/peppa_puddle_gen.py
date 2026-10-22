import json,math
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],
['grass',[120,195,80]],['dkgreen',[40,90,35]],['sky',[160,215,245]],['sun',[255,215,60]],['sunray',[240,170,30]],
['mud',[150,100,60]],['mudline',[90,55,30]],['cloudline',[120,150,190]],['shoe',[25,20,22]],['george',[60,110,210]],
['house',[250,222,130]],['roof',[205,60,45]],['door',[110,65,35]],['fpink',[255,120,160]],['fyellow',[255,240,90]]]
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
PS,PX,PY=0.72,250,130; GS,GX,GY=0.58,640,205
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
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.5}]
out+=char(GS,GX,GY,'george'); out+=[{'op':'pause','s':0.6}]
GY0=490
pl=side(PS,PX,PY,GY0,False); pr=side(PS,PX,PY,GY0,True); gl=side(GS,GX,GY,GY0,False); gr=side(GS,GX,GY,GY0,True)
print(pl,pr,gl,gr)
out+=[C('dkgreen'),S(cr([(0,515),(120,500),(pl[0]-30,pl[1]+2),tuple(pl)])),
      S(cr([tuple(pr),(pr[0]+25,pr[1]-4),((pr[0]+gl[0])/2,486),(gl[0]-25,gl[1]-3),tuple(gl)])),
      S(cr([tuple(gr),(gr[0]+40,gr[1]-8),(980,450),(1040,335),(1100,303),(1160,298),(1220,303),(1285,335),(1359,372)]))]
# house
out+=[C('ink'),S([(1080,317),(1080,215),(1220,215),(1220,317)],0.4),S([(1052,218),(1150,138),(1248,218),(1052,218)],0.4),
      S([(1192,178),(1192,148),(1214,148),(1214,196)],0.3),S([(1136,302),(1136,258),(1164,258),(1164,302)],0.3),
      S([(1094,234),(1121,234),(1121,258),(1094,258),(1094,234)],0.2),S([(1179,234),(1206,234),(1206,258),(1179,258),(1179,234)],0.2)]
# sun, clouds, puddle
out+=[C('sun'),S(ell(135,115,52,52),0.5)]
out+=[C('cloudline')]
def cloud(cx,cy,w):
    P=[(cx-w,cy+20),(cx-w-8,cy),(cx-w*.6,cy-22),(cx-w*.2,cy-30),(cx+w*.2,cy-38),(cx+w*.6,cy-24),(cx+w+6,cy-2),(cx+w,cy+20),(cx,cy+24),(cx-w,cy+20)]
    return S(cr(P,8)+[(cx-w-8,cy+8)],0.5)
out+=[cloud(760,95,90),cloud(1010,70,60)]
out+=[C('mudline'),S(ell(675,692,420,62,90,5),0.6)]
# fills
out+=[C('house'),F((1100,290),(1200,290)),C('roof'),F((1150,190),(1203,165)),C('door'),F((1150,280)),
      C('sky'),F((1107,246),(1192,246)),C('sun'),F((135,115)),C('white'),F((760,90),(1010,68)),C('mud'),F((675,700)),
      C('grass'),F((60,700),(1300,700),(675,775),(150,560),(1300,500),(700,560),(440,600),(365,600),(780,590),(1150,318)),
      C('sky'),F((40,30),(500,30),(900,30),(1300,30),(40,420),(600,420),(700,300),(950,250),(1300,280),(560,300),(400,420),(830,420),(560,250),(880,330),(200,300)),
      {'op':'pause','s':0.5}]
# details: rays, splashes, tufts, flowers
out+=[C('sunray')]
for k in range(8):
    a=2*math.pi*k/8+.2; out.append(S([(135+68*math.cos(a),115+68*math.sin(a)),(135+92*math.cos(a),115+92*math.sin(a))],0.3))
out+=[C('mud')]
for x,y,r in [(300,612,9),(360,596,7),(470,606,8),(520,590,6),(700,604,8),(745,586,6),(840,600,9),(890,585,6),(410,625,6),(800,622,6)]: out.append(dot(x,y,r))
out+=[C('mudline')]
for x,y,r in [(325,630,5),(505,628,5),(715,628,5),(865,626,5),(285,595,5),(540,578,5)]: out.append(dot(x,y,r))
out+=[C('dkgreen')]
for x,y in [(80,600),(200,720),(160,560),(1290,600),(1230,750),(1000,560),(1120,420),(960,520),(60,760),(1320,470)]:
    for dx in (-11,0,11): out.append(S([(x,y+22),(x+dx,y)],0.2))
for c,(x,y) in [('fyellow',(120,655)),('fpink',(1310,690)),('white',(250,610)),('fpink',(1060,600)),('fyellow',(1180,560)),('white',(1270,420))]:
    out+=[C(c),dot(x,y,12)]
out+=[C('sunray')]
for x,y in [(120,655),(1310,690),(250,610),(1060,600),(1180,560),(1270,420)]: out.append(dot(x,y,4))
# preview render
from PIL import Image,ImageDraw
im=Image.new('RGB',(1360,790),'white');d=ImageDraw.Draw(im);col=dict((n,tuple(c)) for n,c in pal);cc=None
for o in out:
    if o['op']=='color':cc=col[o['c']];o_c=o['c']
    if o['op']=='stroke':d.line([tuple(p) for p in o['pts']],fill=cc,width=9,joint='curve')
    if o['op']=='fill':
        keep=[]
        for s in o['seeds']:
            x0,y0=map(int,s); ok=None
            for r in range(0,6):
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        x,y=x0+dx,y0+dy
                        if ok is None and im.crop((x-3,y-3,x+4,y+4)).getcolors(500)==[(49,(255,255,255))]: ok=(x,y)
                if ok: break
            if ok: ImageDraw.floodfill(im,ok,cc); keep.append(list(ok))
            else: print('drop seed',o_c,s)
        assert keep,o_c
        o['seeds']=keep
im.save('preview.png')
D={'name':'peppa-george-puddle-jump','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa and George jumping in a muddy puddle, house on the hill. Characters reuse the peppa_strokes.json geometry (scaled); George = smaller copy with blue shirt.'}
json.dump(D,open('peppa_puddle_strokes.json','w'))
with open('peppa2.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa2\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out))
