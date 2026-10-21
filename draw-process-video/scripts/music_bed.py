#!/usr/bin/env python3
"""Dense continuous BGM bed: drop silences >0.4s, rank 2s windows by energy (busiest phrases),
concatenate with 0.25s crossfades, loop to --dur, fade last --fade s.
usage: music_bed.py src.(wav|mp4) bed.wav --dur 70 [--start 0 --end 0 --keep 0.6]"""
import argparse,subprocess,numpy as np,wave
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--dur',type=float,required=True)
ap.add_argument('--fade',type=float,default=4); ap.add_argument('--keep',type=float,default=0.6,help='fraction of busiest windows kept')
ap.add_argument('--start',type=float,default=0); ap.add_argument('--end',type=float,default=0,help='seconds to cut off the end (e.g. speech/outro)')
a=ap.parse_args(); SR=44100
raw=subprocess.run(['ffmpeg','-v','error','-i',a.src,'-ac','2','-ar',str(SR),'-f','s16le','-'],capture_output=True,check=True).stdout
x=np.frombuffer(raw,'<i2').reshape(-1,2).astype(float)/32768; x=x[int(a.start*SR):len(x)-int(a.end*SR)]
fr=int(.05*SR); rms=np.sqrt((x[:len(x)//fr*fr].reshape(-1,fr,2)**2).mean((1,2))); loud=rms>10**(-40/20)
keep=np.ones(len(rms),bool); i=0
while i<len(rms):  # remove quiet runs >0.4s
    if not loud[i]:
        j=i
        while j<len(rms) and not loud[j]: j+=1
        if (j-i)*0.05>0.4: keep[i:j]=False
        i=j
    else: i+=1
x=np.concatenate([x[k*fr:(k+1)*fr] for k in np.where(keep)[0]])
W=2*SR; segs=[x[k:k+W] for k in range(0,len(x)-W,W)]
e=np.array([np.sqrt((g**2).mean()) for g in segs]); thr=np.quantile(e,1-a.keep)
segs=[g for g,v in zip(segs,e) if v>=thr]  # keep original order of busy phrases
xf=int(.25*SR); ramp=np.linspace(0,1,xf)[:,None]; out=segs[0]
while len(out)<a.dur*SR+xf:
    for g in segs[1:]+segs[:1]:
        out=np.concatenate([out[:-xf],out[-xf:]*(1-ramp)+g[:xf]*ramp,g[xf:]])
out=out[:int(a.dur*SR)]; f=int(a.fade*SR); out[-f:]*=np.linspace(1,0,f)[:,None]
w=wave.open(a.out,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).clip(-32767,32767).astype('<i2').tobytes()); w.close()
