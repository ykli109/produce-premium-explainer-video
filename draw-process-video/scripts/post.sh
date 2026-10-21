#!/usr/bin/env bash
# usage: post.sh raw.mp4 out.mp4 TRIM_START_S TARGET_S [HOLD_S=4]
# trims app startup, uniform speed-up so drawing+hold == TARGET, freezes last frame HOLD s, writes contact sheet.
set -euo pipefail
IN=$1; OUT=$2; A=$3; TGT=$4; HOLD=${5:-4}
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
SP=$(python3 -c "print(($DUR-$A)/($TGT-$HOLD))")
ffmpeg -y -loglevel error -ss $A -i "$IN" -vf "setpts=PTS/$SP,tpad=stop_mode=clone:stop_duration=$HOLD,fps=30,format=yuv420p" \
  -t $TGT -an -c:v libx264 -crf 18 "$OUT"
ffmpeg -y -loglevel error -i "$OUT" -vf "fps=12/$TGT,scale=480:-1,tile=4x3" -frames:v 1 "${OUT%.*}_contact.jpg"
echo "trim=$A speed=$SP  -> $OUT  (pass A and SP to sfx_from_events.py)"
