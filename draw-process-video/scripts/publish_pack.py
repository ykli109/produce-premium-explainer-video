#!/usr/bin/env python3
"""Douyin publish pack: copies video+covers, writes publish.json and a checklist (title<=30 chars, 3-5 hashtags).
usage: publish_pack.py --video final.mp4 --covers dir --title T --caption C --tags 绘画 简笔画 ... --out pack/"""
import argparse,json,os,shutil,subprocess,sys
ap=argparse.ArgumentParser()
for k in ('video','covers','title','caption','out'): ap.add_argument('--'+k,required=True)
ap.add_argument('--tags',nargs='+',required=True); a=ap.parse_args()
err=[]
if len(a.title)>30: err.append(f'title {len(a.title)} chars >30')
if not 3<=len(a.tags)<=5: err.append(f'{len(a.tags)} hashtags (need 3-5)')
cv=[f'{a.covers}/cover_4x3.jpg',f'{a.covers}/cover_3x4.jpg']; err+=[f'missing {c}' for c in cv if not os.path.exists(c)]
dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',a.video],capture_output=True,text=True).stdout)
if not 65<=dur<=75: err.append(f'duration {dur:.1f}s outside 65-75 (ok only if user asked)')
os.makedirs(a.out,exist_ok=True)
for f in [a.video]+cv: shutil.copy(f,a.out)
tags=['#'+t.lstrip('#') for t in a.tags]
json.dump({'title':a.title,'caption':a.caption,'hashtags':tags,'video':os.path.basename(a.video),'covers':[os.path.basename(c) for c in cv],'duration_s':round(dur,2)},open(f'{a.out}/publish.json','w'),ensure_ascii=False,indent=1)
ck=f"""# 抖音发布清单
- [{'x' if len(a.title)<=30 else ' '}] 标题（≤30 字）：{a.title}
- [x] 文案：{a.caption}
- [{'x' if 3<=len(tags)<=5 else ' '}] 话题（3–5 个）：{' '.join(tags)}
- [x] 封面 4:3 cover_4x3.jpg / 3:4 cover_3x4.jpg
- [x] 视频 {os.path.basename(a.video)}（{dur:.1f}s）
- [ ] 人工：开头 1.5–2s 成品钩子、接触表 QA、−14 LUFS / TP≤−1.5、无工具/AI 字样
"""
open(f'{a.out}/checklist.md','w').write(ck); print(ck)
if err: print('FAIL:',*err,sep='\n - '); sys.exit(1)
