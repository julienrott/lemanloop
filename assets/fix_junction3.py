#!/usr/bin/env python3
"""Junction fix v3:
1. split depart into head (0..66) + tail (67..90, 24 frames with accelerating zoom 1.0->1.35)
2. concat head+tail
3. crossfade 0.4s into docking_reverse
"""
import subprocess, os, av

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
A = '/tmp/depart_norm.mp4'
B = base + 'lemanloop_3_docking_reverse.mp4'
OUT = base + 'lemanloop_depart_complet_v2.mp4'

# head: fastest-stream copy; tail: zoompan building from zoom 1.0, +0.0145/frame -> ~1.35
def run(cmd):
    r = subprocess.run(cmd, check=True, capture_output=True)
    return r

# head frames 0-66 (select), stream copy is tricky with select -> re-encode fast
run([ff, '-y', '-i', A, '-vf', "select='lt(n,67)'", '-an', '-vsync', 'cfr',
     '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '/tmp/head.mp4'])
# tail frames 67-90 zoom ramp
run([ff, '-y', '-i', A, '-vf', "select='gte(n,67)',zoompan=z='min(1.0+(floor(n-67)*0.0146),1.36)':d=1:s=704x512:fps=30",
     '-an', '-vsync', 'cfr', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '/tmp/tail.mp4'])

lst = '/tmp/c_head_tail.txt'
open(lst, 'w').write("file '/tmp/head.mp4'\nfile '/tmp/tail.mp4'\n")
run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '/tmp/pushed.mp4'])

# crossfade 0.4s into docking_reverse (approach end is CLOSE; reverse starts WIDE -> pull-back reveal)
filter_complex = "[0:v]fps=30,format=yuv420p[va];[1:v]scale=704:512,setsar=1,fps=30,format=yuv420p[vb];[va][vb]xfade=transition=fade:duration=0.4:offset=2.63[v]"
run([ff, '-y', '-i', '/tmp/pushed.mp4', '-i', B, '-filter_complex', filter_complex,
     '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', OUT])

c = av.open(OUT)
s = c.streams.video[0]
print('depart complet v2:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
