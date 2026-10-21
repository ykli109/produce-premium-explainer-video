#!/usr/bin/env bash
# usage: post.sh raw.mp4 out.mp4 TRIM_START_S TARGET_S [HOLD_S=4] [HOOK_S=1.75]
# Opens with the FINISHED picture for HOOK_S as a hook, 0.3s fade to the blank canvas, then the drawing.
# trims app startup, uniform speed-up so drawing+hold == TARGET, freezes last frame HOLD s, writes contact sheet.
set -euo pipefail
IN=$1; OUT=$2; A=$3; TGT=$4; HOLD=${5:-4}; HOOK=${6:-1.75}; XF=0.3
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
SP=$(python3 -c "print(($DUR-$A)/($TGT-$HOLD-$HOOK+$XF))")
ffmpeg -y -loglevel error -ss $A -i "$IN" -vf "setpts=PTS/$SP,tpad=stop_mode=clone:stop_duration=$HOLD,fps=30,format=yuv420p" \
  -an -c:v libx264 -crf 18 "${OUT%.*}_body.mp4"
ffmpeg -y -loglevel error -sseof -0.1 -i "${OUT%.*}_body.mp4" -frames:v 1 -update 1 "${OUT%.*}_final.png"
ffmpeg -y -loglevel error -loop 1 -t $HOOK -framerate 30 -i "${OUT%.*}_final.png" -i "${OUT%.*}_body.mp4" -filter_complex \
 "[0:v]fps=30,format=yuv420p,setsar=1,settb=1/30[h];[1:v]fps=30,format=yuv420p,setsar=1,settb=1/30[b];[h][b]xfade=transition=fade:duration=$XF:offset=$(python3 -c "print($HOOK-$XF)"),tpad=stop_mode=clone:stop_duration=15[v]" \
 -map "[v]" -t $TGT -an -c:v libx264 -crf 18 "$OUT"
ffmpeg -y -loglevel error -i "$OUT" -vf "fps=12/$TGT,scale=480:-1,tile=4x3" -frames:v 1 "${OUT%.*}_contact.jpg"
echo "trim=$A speed=$SP  -> $OUT  (sfx: --trim $A --speed $SP --offset $(python3 -c "print($HOOK-$XF)"))"
