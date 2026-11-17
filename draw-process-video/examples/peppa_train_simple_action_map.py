import json, subprocess, numpy as np
d=json.load(open('strokes.json')); e=json.load(open('out/events_ink.json')); ops=d['ops']
pal={n:tuple(c) for n,c in d['palette']}
TRIM=1.6; SP=1.0711353022056718; OFF=1.45
def v(t): return (t-TRIM)/SP+OFF
emap=[]; k=0; cur=None
for i,o in enumerate(ops):
    if o['op']=='color': cur=o['c']
    if o['op'] in ('stroke','erase','hover','pause','undo'):
        ev=e[k]; k+=1; assert ev[0]==dict(stroke='s',erase='e',hover='h',pause='p',undo='u')[o['op']]
        emap.append(dict(op=i,kind=o['op'],color=cur,wrong=bool(o.get('wrong')),t0=ev[1],t1=ev[2]))
    elif o['op']=='fill':
        ts=[]
        for s in o['seeds']: assert e[k][0]=='f'; ts.append(e[k][1]); k+=1
        emap.append(dict(op=i,kind='fill',color=cur,clicks=ts,seeds=o['seeds'],t0=ts[0],t1=ts[-1]))
assert k==len(e),(k,len(e))
json.dump(emap,open('event_op_map.json','w'))
probes=[]
for m in emap:
    if m['kind']!='fill': continue
    s=m['seeds'][0]; probes.append(dict(op=m['op'],color=m['color'],x=int((s[0]+69)/2),y=int((s[1]+58)/2),pred=v(m['clicks'][0])))
W,H=720,540
p=subprocess.Popen(['ffmpeg','-v','error','-i','out/video.mp4','-vf','scale=720:540:flags=area','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
fs=W*H*3; fi=0; onset={}
while True:
    b=p.stdout.read(fs)
    if len(b)<fs: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3); t=fi/60
    for q in probes:
        if q['op'] in onset or t<q['pred']-3 or t<2.0: continue
        px=f[q['y']-1:q['y']+2,q['x']-1:q['x']+2].reshape(-1,3).astype(int)
        if np.all(np.abs(px-np.array(pal[q['color']])).max(axis=1)<=22): onset[q['op']]=t
    fi+=1
res=[]
for q in probes:
    o=onset.get(q['op']); res.append(dict(q,visual=o,resid=None if o is None else round(o-q['pred'],3)))
json.dump(res,open('fill_onsets_raw.json','w'),indent=1)
r=[x['resid'] for x in res if x['resid'] is not None and abs(x['resid'])<2]
print('fills',len(res),'measured',len(r),'median',np.median(r),'min',min(r),'max',max(r))
med=float(np.median(r))
A=[]
for m in emap:
    if m['kind']!='fill': A.append(dict(op=m['op'],kind=m['kind'],color=m['color'],wrong=m['wrong'],start=round(v(m['t0']),3),end=round(v(m['t1']),3)))
    else:
        vis=onset.get(m['op']); st=vis if vis is not None and abs(vis-v(m['clicks'][0]))<2 else v(m['clicks'][0])+med
        A.append(dict(op=m['op'],kind='fill',color=m['color'],start=round(st,3),end=round(v(m['clicks'][-1])+med+0.3,3),visual=vis))
json.dump(A,open('action_map.json','w'),indent=0)
for x in res: print(x['op'],x['color'],round(x['pred'],2),x['visual'],x['resid'])
print('last action end',A[-1])
