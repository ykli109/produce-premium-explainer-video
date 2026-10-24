import json,math,random
random.seed(24)
E=json.load(open('/workspace/ppev-git/draw-process-video/examples/peppa_strokes.json'))
ops=E['ops']; out=[]
pal=[['ink',[40,30,32]],['dress',[214,38,48]],['skin',[247,172,196]],['cheek',[236,120,155]],['white',[255,255,255]],['shoe',[25,20,22]],
['wall',[255,238,190]],['floor',[214,170,118]],['wood',[150,92,52]],['sponge',[246,206,150]],['icing',[255,150,190]],['flame',[255,150,30]],
['candleB',[90,170,240]],['candleY',[255,215,60]],['balR',[235,60,70]],['balB',[70,140,230]],['balY',[255,205,40]],['flagG',[110,195,90]],
['gift',[120,90,200]],['ribbon',[255,225,80]]]
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
out+=char(PS,PX,PY,'dress'); out+=[{'op':'pause','s':0.6}]
lh=T((292,392),PS,PX,PY)   # her left hand (viewer's left)
# 2) table + cake (ink)
TX0,TX1,TY=770,1250,520
out+=[C('ink'),S(rect(TX0,TY,TX1,TY+30),0.3)]
for lx in (810,1190): out.append(S(rect(lx,TY+30,lx+24,748),0.2))
# bottom tier with drippy icing
B0,B1,BT,BB=850,1170,405,TY
out.append(S(rect(B0,BT,B1,BB),0.3))
def drip(x0,x1,y,n,dep):
    P=[(x0,y)]
    w=(x1-x0)/n
    for i in range(n):
        a=x0+i*w; P+=[(a+w*.25,y+dep*(.6 if i%2 else 1)),(a+w*.5,y+dep*(.6 if i%2 else 1)+4),(a+w*.75,y+4),(a+w,y)]
    return cr(P,6)
out.append(S(drip(B0,B1,BT+22,8,26),0.2))
# top tier
U0,U1,UT=915,1105,315
out.append(S(rect(U0,UT,U1,BT),0.3))
out.append(S(drip(U0,U1,UT+18,5,22),0.2))
# candles + flames
CX=[960,1010,1060]
for x in CX:
    out.append(S(rect(x-9,UT-58,x+9,UT),0.1))
for x in CX:
    out.append(S(cr([(x,UT-66),(x-12,UT-80),(x-6,UT-100),(x,UT-112),(x+6,UT-100),(x+12,UT-80),(x,UT-66)],6),0.1,0.008))
# 3) gift box on the floor
G0,G1,GT,GB=575,715,655,745
out.append(S(rect(G0,GT,G1,GB),0.3)); out.append(S(rect(G0-10,GT-28,G1+10,GT),0.3))
out.append(S([(645,GT-28),(645,GB)],0.1))
out.append(S(cr([(645,GT-30),(615,GT-58),(600,GT-44),(615,GT-32),(645,GT-30)],6),0.1))
out.append(S(cr([(645,GT-30),(675,GT-58),(690,GT-44),(675,GT-32),(645,GT-30)],6),0.1))
# 4) balloons held in her hand
BAL=[((80,265),'balR'),((185,215),'balB'),((70,410),'balY')]
for (bx,by),_ in BAL:
    out.append(S(ell(bx,by,46,56,60,4),0.3))
    out.append(S([(bx-7,by+62),(bx,by+54),(bx+7,by+62),(bx-7,by+62)],0))
for (bx,by),_ in BAL:
    out.append(S(cr([(bx,by+64),(bx+(lh[0]-bx)*.4+8,by+64+(lh[1]-by-64)*.45),(lh[0]-4,lh[1]-4)],10),0.3,0.008))
# 5) fills: character props
out+=[C('sponge'),F((900,480),(1120,480),(1010,495),(940,370),(1080,380))]
out+=[C('icing'),F((900,415),(1120,415),(1010,418),(960,328),(1050,328))]
out+=[C('candleB'),F((960,UT-30),(1060,UT-30)),C('candleY'),F((1010,UT-30)),C('flame'),F(*[(x,UT-90) for x in CX])]
out+=[C('gift'),F((610,700),(690,700),(605,GT-14),(690,GT-14)),C('ribbon'),F((620,GT-44),(672,GT-44))]
for (bx,by),c in BAL: out+=[C(c),F((bx,by))]
out+=[C('wood'),F((1000,TY+15),(822,640),(1202,640),(822,720),(1202,720))]
out+=[{'op':'pause','s':0.4}]
# 6) bunting across the top
out+=[C('ink')]
def gar(x): # garland y at x
    return 34+40*abs(math.sin(math.pi*x/680))
gl=[(x,gar(x)) for x in range(0,1361,20)]
out.append(S(gl,0.3))
FL=[]
for x in range(70,1360,110):
    a,b=x-28,x+28; ya,yb=gar(a),gar(b)
    tip=(x,max(ya,yb)+52)
    out.append(S([(a,ya),tip,(b,yb)],0.1)); FL.append((x,(ya+yb)/2+18))
# 7) floor line (stops at the dress), wall/floor fills
WY=630
pl=side(PS,PX,PY,WY,False); pr=side(PS,PX,PY,WY,True)
out+=[C('wood'),S([(2,WY),(pl[0],pl[1])],0.3),S([(pr[0],pr[1]),(G0-10,WY)],0.3),S([(G1+10,WY),(1358,WY)],0.3)]
fc=['balR','balY','balB','flagG']
for i,(x,y) in enumerate(FL): out+=[C(fc[i%4]),F((x,y))]
out+=[C('floor'),F((40,700),(300,770),(520,700),(520,770),(760,700),(900,700),(1300,700),(1000,760),(740,770),(460,705),(560,640),(1230,700))]
out+=[C('wall'),F((20,20),(680,20),(1340,20),(30,560),(300,170),(600,300),(700,500),(1300,400),(1300,200),(400,580),(560,560),(740,600),(1020,600),(1230,600),(800,200),(1200,300),(140,140),(130,330),(150,480),(30,330),(230,330),(520,200),(600,150),(1250,150),(30,150),(250,140),(600,600),(760,560),(870,580),(1170,580),(830,280),(1150,250))]
out+=[{'op':'pause','s':0.5}]
# 8) details: cake dots, candle stripes, balloon shines, confetti
out+=[C('white')]
for (bx,by),_ in BAL: out.append(S(cr([(bx-26,by-14),(bx-22,by-32),(bx-8,by-42)],6),0,0.008))
for x,y in [(890,470),(950,490),(1010,465),(1070,490),(1130,470),(945,385),(1010,375),(1070,385)]: out.append(dot(x,y,7))
out+=[C('balR')]
for x,y in [(920,470),(1040,480),(1100,465),(980,390),(1040,395)]: out.append(dot(x,y,6))
conf=[(360,160),(470,190),(560,120),(700,180),(770,120),(860,190),(1190,170),(1290,230),(650,260),(720,350),(1280,330),(640,430),(1300,480),(740,470)]
cols=['balR','balB','balY','flagG','gift']
for i,(x,y) in enumerate(conf):
    out+=[C(cols[i%5]),S([(x-8,y-5),(x+8,y+5)],0,0.01)]
out+=[C('floor')]
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
D={'name':'peppa-birthday-cake','canvas':[1360,790],'palette':pal,'ops':out,'ui':E['ui'],
   'notes':'Peppa birthday party: Peppa holding three balloons, a two-tier pink birthday cake with candles on a table, a gift box, bunting and confetti. Peppa reuses peppa_strokes.json geometry (scaled 0.75).'}
json.dump(D,open('peppa_birthday_strokes.json','w'))
with open('peppa4.gpl','w') as f:
    f.write('GIMP Palette\nName: Peppa4\nColumns: 6\n#\n'+''.join('%3d %3d %3d %s\n'%(*c,n) for n,c in pal))
print(len(out),'ops')
