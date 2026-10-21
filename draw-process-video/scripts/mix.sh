#!/usr/bin/env bash
# usage: mix.sh video.mp4 bed.wav sfx.wav out.mp4 [SFX_DB_UNDER=15]
# SFX: 6 kHz lowpass + de-ess, sits ~14-16 dB under music. Two-pass loudnorm -14 LUFS; targets TP -2.5 so the AAC file still measures <= -1.5 dBTP.
set -euo pipefail
V=$1; B=$2; S=$3; O=$4; U=${5:-15}
F="[1:a]volume=0dB[m];[2:a]lowpass=f=6000,deesser,volume=-${U}dB[s];[m][s]amix=inputs=2:normalize=0[a]"
J=$(ffmpeg -hide_banner -i "$V" -i "$B" -i "$S" -filter_complex "$F;[a]loudnorm=I=-14:TP=-2.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -loglevel error -i "$V" -i "$B" -i "$S" -filter_complex \
 "$F;[a]loudnorm=I=-14:TP=-2.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000,alimiter=limit=0.75:level=false:attack=2:release=50[o]" \
 -map 0:v -map "[o]" -c:v copy -c:a aac -b:a 192k -shortest "$O"
echo "--- verify"; ffmpeg -hide_banner -i "$O" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
ffmpeg -hide_banner -i "$O" -af silencedetect=n=-45dB:d=0.4 -f null - 2>&1 | { grep -c silence_start || true; } | sed 's/^/silences>0.4s (expect 0 before final fade): /'
