#!/bin/bash
# Lay a music bed under a narrated video at a fixed VO:music fader split.
# Usage: VO=70 mix.sh <video.mp4> [music.mp3] [out.mp4]
# VO is the voice share of a VO:music fader split (70 = 70:30). The music is set that far
# under the voice's measured loudness (70:30 = 7.4 dB under), constant, no ducking.
# Splice (default for Ephemeral Beauty, SPLICE=0 to turn off): play the song from the top,
# crossfade over 2 s inside its quiet stretch (JOIN, ~118-132 s) into the section that runs
# into its natural ending (OUTRO_END), so the song ends with the video instead of fading early.
# Without a splice: 2 s fade in, 4 s fade out at the video's end. Video stream copied.
set -euo pipefail
IN="$1"
MUSIC="${2:-/Users/zharris/Downloads/Ephemeral Beauty (1).mp3}"
VO="${VO:-70}"
SPLICE="${SPLICE:-1}"; JOIN="${JOIN:-125}"; OUTRO_END="${OUTRO_END:-204}"
OUT="${3:-${IN%.mp4}.music$VO.mp4}"
VOL=$(ffmpeg -hide_banner -i "$IN" -af ebur128 -f null - 2>&1 | awk '/^ +I:/{v=$2} END{print v}')
TARGET=$(python3 -c "import math;print(round($VOL-20*math.log10($VO/(100-$VO)),1))")
# Ride (when <video>.spans.json exists, {"spans":[[start,end],...]}): the bed sits at GAP:100-GAP
# between lines and dips to VO:100-VO under each span, 300 ms attack before, 600 ms release after.
SPANS="${IN%.mp4}.spans.json"; GAP="${GAP:-60}"; RIDE=""
# Voice polish (VOXFX=0 to turn off): remove rumble and residual room tone, pull out the boxy
# low mids, add presence and air. Bed EQ makes a pocket in the music where the voice lives.
VOXFX="${VOXFX:-1}"
if [ "$VOXFX" = "1" ]; then
  VCHAIN="highpass=f=90,afftdn=nr=10:nf=-45:tn=1,equalizer=f=300:t=q:w=1:g=-3.5,equalizer=f=650:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1:g=3,treble=g=2.5:f=9000,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1.5"
  BEQ=",equalizer=f=400:t=q:w=1:g=-4,equalizer=f=2500:t=q:w=1:g=-3"
else VCHAIN="anull"; BEQ=""; fi
if [ -f "$SPANS" ]; then
  TARGET=$(python3 -c "import math;print(round($VOL-20*math.log10($GAP/(100-$GAP)),1))")
  RIDE=$(python3 -c "
import json,math
s=json.load(open('$SPANS'))['spans']
dip=20*math.log10($VO/(100-$VO))-20*math.log10($GAP/(100-$GAP))
r=['clip((t-%.3f)/0.3,0,1)*clip((%.3f-t)/0.6,0,1)'%(a-0.3,b+0.6) for a,b in s]
e=r[0]
for x in r[1:]: e='max(%s,%s)'%(e,x)
print(',volume=eval=frame:volume=\'pow(10,-%.2f*(%s)/20)\''%(dip,e))")
fi
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
# Splice plan: X = where the head ends (in the quiet stretch, or earlier for short videos),
# T = where the tail starts so the song's own ending lands at the video's end.
read X T < <(python3 -c "
d=$DUR; j=$JOIN; e=$OUTRO_END; xf=2
x=min(j, d-24)          # keep at least 24 s of tail so the ending is heard
t=e-(d-x)-xf/2
print(round(x+1,2), round(t,2)) if $SPLICE and x>10 and t>x else print(0, 0)")
if [ "$X" != "0" ]; then
  BED="[1:a]aresample=48000,asplit=2[h][t];
[h]atrim=0:$X,asetpts=PTS-STARTPTS,afade=t=in:d=2[hh];
[t]atrim=start=$T,asetpts=PTS-STARTPTS[tt];
[hh][tt]acrossfade=d=2:c1=tri:c2=tri,loudnorm=I=$TARGET:TP=-6:LRA=11,atrim=0:$DUR$BEQ$RIDE[bed];"
  LOOP=()
else
  FADE=$(python3 -c "print(max(0,$DUR-4))")
  BED="[1:a]aresample=48000,loudnorm=I=$TARGET:TP=-6:LRA=11,atrim=0:$DUR,afade=t=in:d=2,afade=t=out:st=$FADE:d=4$BEQ$RIDE[bed];"
  LOOP=(-stream_loop -1)
fi
ffmpeg -y -loglevel error -i "$IN" ${LOOP[@]+"${LOOP[@]}"} -i "$MUSIC" -filter_complex "
[0:a]aresample=48000,$VCHAIN[vo];
$BED
[vo][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest "$OUT"
[ "$X" != "0" ] && SP=", splice ending ${X}s into song ${T}s" || SP=", no splice"
[ -n "$RIDE" ] && SP="$SP, ride from $(basename $SPANS)"
echo "$OUT (voice $VOL LUFS, music $TARGET LUFS$SP)"
