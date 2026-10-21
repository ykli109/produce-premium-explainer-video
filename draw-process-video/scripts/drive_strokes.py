#!/usr/bin/env python3
"""Drive KolourPaint with xdotool from a stroke JSON (canvas coords).
ops: color{c} | stroke{pts,amp,dl} | fill{seeds} | pause{s}. Logs events for SFX:
["s",t_start,t_end] per stroke, ["f",t] per bucket click (seconds since --t0)."""
import argparse,json,math,random,subprocess,time
ap=argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('--display',default=':77')
ap.add_argument('--t0',type=float,default=None); ap.add_argument('--events',default='events.json')
ap.add_argument('--speed',type=float,default=1.0,help='>1 = faster pen (shorter per-point sleep)')
a=ap.parse_args(); D=json.load(open(a.json)); U=D['ui']; random.seed(5)
T0=a.t0 or time.time(); log=[]; cur=None
PAL=[p[0] for p in D['palette']]; OX,OY=U['canvas_origin']; CW,CH=D['canvas']
def X(c): subprocess.run(['xdotool','-'],input='\n'.join(c)+'\n',text=True,env={'DISPLAY':a.display,'PATH':'/usr/bin:/bin'})
def M(p): return (OX+min(CW-1,max(0,p[0])),OY+min(CH-1,max(0,p[1])))
def resample(pts,step=4):
    out=[pts[0]]
    for p,q in zip(pts,pts[1:]):
        n=max(1,int(math.dist(p,q)/step)); out+=[(p[0]+(q[0]-p[0])*k/n,p[1]+(q[1]-p[1])*k/n) for k in range(1,n+1)]
    return out
def tool(t):
    global cur
    if t==cur: return
    x,y=U['tool_xy'][t]; X([f'mousemove --sync {x} {y}','sleep 0.25','click 1','sleep 0.2'])
    if t=='brush' and U.get('brush_size_xy'): bx,by=U['brush_size_xy']; X([f'mousemove {bx} {by}','sleep 0.2','click 1','sleep 0.2'])
    cur=t
def color(n):
    r,c=divmod(PAL.index(n),U['palette_cols']); x0,y0=U['palette_origin']; s=U['palette_cell']
    X([f'mousemove {x0+s*c} {y0+s*r}','sleep 0.3','click 1','sleep 0.25'])
def stroke(pts,amp=1.0,dl=0.009):
    tool('brush'); pts=resample([M(p) for p in pts]); ph=random.random()*9; dl=dl/a.speed
    pts=[(x+amp*math.sin(k*.21+ph),y+amp*math.cos(k*.17+ph)) for k,(x,y) in enumerate(pts)]  # hand wobble
    pts=[(min(OX+CW-3,max(OX+2,x)),min(OY+CH-3,max(OY+2,y))) for x,y in pts]  # wobble must not push a stroke off the canvas edge (lost hill line -> sky leaked into grass)
    c=[f'mousemove {int(pts[0][0])} {int(pts[0][1])}','sleep 0.12','mousedown 1']
    for x,y in pts[1:]: c+=[f'mousemove {int(round(x))} {int(round(y))}',f'sleep {dl:.4f}']
    c+=['mouseup 1','sleep 0.12']; t=time.time()-T0; X(c); log.append(['s',t,time.time()-T0])
def fill(seeds):
    tool('fill')
    for s in seeds:
        x,y=M(s); X([f'mousemove {int(x)} {int(y)}','sleep 0.35','click 1','sleep 0.3']); log.append(['f',time.time()-T0])
for o in D['ops']:
    k=o['op']
    if k=='color': color(o['c'])
    elif k=='stroke': stroke(o['pts'],o.get('amp',1.0),o.get('dl',0.009))
    elif k=='fill': fill(o['seeds'])
    elif k=='pause': time.sleep(o['s'])
if U.get('park_cursor'): X(['mousemove %d %d'%tuple(U['park_cursor'])])
json.dump(log,open(a.events,'w')); print('drawing done in %.1fs'%(time.time()-T0))
