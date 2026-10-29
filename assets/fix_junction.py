#!/usr/bin/env python3
"""Fix the jump cut: push-in zoom at the end of the depart clip + short crossfade into docking_reverse.
Reads as a camera pull-back reveal (depart ends CLOSE, docking_reverse starts WIDE)."""
import subprocess, os, av

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
out = base + 'lemanloop_depart_complet_v2.mp4'

# 1) depart_norm (3.03s): push-in zoom over the last ~0.8s, centered slightly left (on the pod)
#    zoompan d=1 processes each frame; zoom ramps 1.0 -> ~1.35 from t=2.2s
vf_zoom = (
    "zoompan=z='if(lt(t,2.2),1.0,min(1.0+((t-2.2)*0.45),1.35))'"
    ":x='iw/2-(iw/zoom/2)-iw*0.08':y='ih/2-(ih/zoom/2)':d=1:s=704x512:fps=30"
)

# 2) crossfade 0.4s into docking_reverse
filter_complex = (
    f"[0:v]{vf_zoom},format=yuv420p[va];"
    "[1:v]scale=704:512,setsar=1,fps=30,format=yuv420p[vb];"
    "[va][vb]xfade=transition=fade:duration=0.4:offset=2.63[v]"
)

cmd = [
    ff, '-y',
    '-i', '/tmp/depart_norm.mp4',
    '-i', base + 'lemanloop_3_docking_reverse.mp4',
    '-filter_complex', filter_complex,
    '-map', '[v]', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
    out
]
subprocess.run(cmd, check=True, capture_output=True)

c = av.open(out)
s = c.streams.video[0]
print('depart complet v2:', s.frames, 'frames,', round(os.path.getsize(out) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
