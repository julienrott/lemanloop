#!/usr/bin/env python3
"""Junction fix v4: extract tail frames as PNGs, zoom them with Python (PIL), rebuild tail.mp4,
then head + tail concat + crossfade into docking_reverse."""
import subprocess, os, av, glob
from PIL import Image

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
A = '/tmp/depart_norm.mp4'
B = base + 'lemanloop_3_docking_reverse.mp4'
OUT = base + 'lemanloop_depart_complet_v2.mp4'
TMP = '/tmp/jfix'
os.makedirs(TMP, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r

# 1) extract all frames
run([ff, '-y', '-i', A, os.path.join(TMP, 'f_%04d.png')])
frames = sorted(glob.glob(os.path.join(TMP, 'f_*.png')))
print('total frames:', len(frames))

# 2) zoom the tail (last 24 frames): incremental scale 1.0 -> 1.36, center crop 704x512
tail_start = len(frames) - 24
for idx in range(tail_start, len(frames)):
    im = Image.open(frames[idx])
    z = 1.0 + (idx - tail_start) * (0.36 / 24)
    w = int(704 * z); h = int(512 * z)
    zoomed = im.resize((w, h), Image.LANCZOS)
    left = (w - 704) // 2
    top = (h - 512) // 2
    zoomed.crop((left, top, left + 704, top + 512)).save(frames[idx])

# 3) rebuild video from all frames at 30fps
run([ff, '-y', '-framerate', '30', '-i', os.path.join(TMP, 'f_%04d.png'),
     '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
     '/tmp/pushed.mp4'])
c = av.open('/tmp/pushed.mp4')
print('pushed frames:', c.streams.video[0].frames)

# 4) crossfade into docking_reverse
filter_complex = ("[0:v]fps=30,format=yuv420p[va];"
                  "[1:v]scale=704:512,setsar=1,fps=30,format=yuv420p[vb];"
                  "[va][vb]xfade=transition=fade:duration=0.4:offset=2.63[v]")
run([ff, '-y', '-i', '/tmp/pushed.mp4', '-i', B, '-filter_complex', filter_complex,
     '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
     '-pix_fmt', 'yuv420p', OUT])

c = av.open(OUT)
s = c.streams.video[0]
print('depart complet v2:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
