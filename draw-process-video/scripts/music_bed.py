#!/usr/bin/env python3
"""BGM bed from ONE coherent continuous performance. Never chops silences or stitches fragments.
Default: one contiguous excerpt of --dur seconds starting at --start (or 'auto' = first note onset,
snapped to a beat), with --fadein and --fade at the end.
If the source (after --start) is shorter than --dur, the WHOLE piece is looped at a bar boundary
(beat-tracked, 4/4 assumed via --beats-per-bar) with a short --xfade crossfade.
usage: music_bed.py src.(wav|mp4) bed.wav --dur 70 [--start auto|SEC] [--fadein 1.5 --fade 4 --xfade 0.3]"""
import argparse,subprocess,numpy as np,wave
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--dur',type=float,required=True)
ap.add_argument('--start',default='auto'); ap.add_argument('--fadein',type=float,default=1.5); ap.add_argument('--fade',type=float,default=4)
ap.add_argument('--xfade',type=float,default=0.3); ap.add_argument('--beats-per-bar',type=int,default=4)
a=ap.parse_args(); SR=44100
raw=subprocess.run(['ffmpeg','-v','error','-i',a.src,'-ac','2','-ar',str(SR),'-f','s16le','-'],capture_output=True,check=True).stdout
x=np.frombuffer(raw,'<i2').reshape(-1,2).astype(float)/32768
def beats(sig):
    import librosa
    _,b=librosa.beat.beat_track(y=sig.mean(1).astype(np.float32),sr=SR,units='samples'); return b
if a.start=='auto':
    fr=int(.05*SR); r=np.sqrt((x[:len(x)//fr*fr].reshape(-1,fr,2)**2).mean((1,2)))
    i0=int(np.argmax(r>r.max()*10**(-30/20)))*fr          # first real note (skip leading silence only)
    st=max(0,i0-int(.05*SR))
else: st=int(float(a.start)*SR)
N=int(a.dur*SR); x=x[st:]
if len(x)>=N: y=x[:N].copy(); how=f'contiguous excerpt {st/SR:.2f}-{(st+N)/SR:.2f}s'
else:   # loop whole piece, cut at last bar line, crossfade into the top of the piece
    b=beats(x); bars=b[::a.beats_per_bar]; cut=int(bars[-1]) if len(bars)>1 and bars[-1]>len(x)*.6 else len(x)
    piece=x[:cut]; X=int(a.xfade*SR); y=piece.copy()
    while len(y)<N:
        r=np.linspace(0,1,X)[:,None]; y[-X:]=y[-X:]*(1-r)+piece[:X]*r; y=np.concatenate([y,piece[X:]])
    y=y[:N]; how=f'whole piece {st/SR:.2f}-{(st+cut)/SR:.2f}s looped at bar line, {a.xfade}s xfade'
fi=int(a.fadein*SR); y[:fi]*=np.linspace(0,1,fi)[:,None]
fo=int(a.fade*SR); y[-fo:]*=np.linspace(1,0,fo)[:,None]
w=wave.open(a.out,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y*32767).clip(-32767,32767).astype('<i2').tobytes()); w.close(); print(how,'->',a.out)
