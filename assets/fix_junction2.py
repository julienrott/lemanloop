#!/usr/bin/env python3
"""Fix the jump cut v2: push-in zoom at end of depart clip + crossfade into docking_reverse.
depart_norm.mp4 has an audio stream -> strip audio, map video only."""
import subprocess, os, av

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
out = base + 'lemanloop_depart_complet_v2.mp4'

vf_zoom = (
    "zoompan=z='min(1.0+((t-2.2)*0.45),1.35)':d=1:s=704x512:fps=30,format=yuv420p"
)
filter_complex = (
    f"[0:v]{vf_zoom}[va];"
    "[1:v]scale=704:512,setsar=1,fps=30,format=yuv420p[vb];"
    "[va][vb]xfade=transition=fade:duration=0.4:offset=2.63[v]"
)

cmd = [
    ff, '-y',
    '-i', '/tmp/depart_norm.mp4',
    '-i', base + 'lemanloop_3_docking_reverse.mp4',
    '-filter_complex', filter_complex,
    '-map', '[v]', '-an',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
    out
]
subprocess.run(cmd, check=True, capture_output=True)

c = av.open(out)
s = c.streams.video[0]
print('depart complet v2:', s.frames, 'frames,', round(os.path.getsize(out) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
