#!/usr/bin/env bash
# Private Xvfb + KolourPaint + x11grab session. Kills ONLY its own PIDs.
# usage: session.sh <strokes.json> <outdir> [W] [H] [DISPLAY_NUM]
set -euo pipefail
JSON=$(realpath "$1"); OUT=$(realpath -m "$2"); W=${3:-1440}; H=${4:-1080}; DN=${5:-77}
mkdir -p "$OUT"; cd "$OUT"; HERE=$(dirname "$(realpath "$0")")
[ -e /tmp/.X11-unix/X$DN ] && { echo "display :$DN in use, pick another"; exit 1; }
Xvfb :$DN -screen 0 ${W}x${H}x24 -nolisten tcp >xvfb.log 2>&1 & XPID=$!
KPID=""; FPID=""
cleanup(){ # NEVER pkill Xvfb/kolourpaint broadly: shared desktop runs Xvfb too
  [ -n "$FPID" ] && kill -INT $FPID 2>/dev/null && wait $FPID 2>/dev/null || true
  [ -n "$KPID" ] && kill $KPID 2>/dev/null || true
  kill $XPID 2>/dev/null || true; }
trap cleanup EXIT
sleep 1.5; export DISPLAY=:$DN
python3 -c "from PIL import Image;import json;d=json.load(open('$JSON'));Image.new('RGB',tuple(d['canvas']),'white').save('blank.png')"
kolourpaint blank.png >kp.log 2>&1 & KPID=$!
sleep 4; WID=$(xdotool search --sync --onlyvisible --class kolourpaint | head -1)
xdotool windowmove $WID 0 0 windowsize $WID $W $H; sleep 1.5
import -window root ui_check.png   # verify toolbox/palette coords vs ui block BEFORE recording
if [ "${CALIBRATE:-0}" = 1 ]; then echo "calibration shot: $OUT/ui_check.png"; exit 0; fi
T0=$(date +%s.%N)
ffmpeg -y -loglevel error -f x11grab -draw_mouse 1 -framerate 30 -video_size ${W}x${H} -i :$DN \
  -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p raw.mp4 >rec.log 2>&1 & FPID=$!
python3 "$HERE/drive_strokes.py" "$JSON" --display :$DN --t0 $T0 --events events.json
sleep 2; import -window root end.png
echo "raw: $OUT/raw.mp4 events: $OUT/events.json"
