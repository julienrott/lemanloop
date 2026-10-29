#!/usr/bin/env python3
"""Smooth junction WITHOUT zoom/fade:
- keep depart_norm frames as-is (no zoom)
- find the frame of docking_reverse that best matches depart's last frame (framing search)
- trim depart's wobbly final frames (last 6) and start reverse at the best-match frame
- direct concat (hard cut on nearly-identical composition = invisible cut)
"""
import subprocess, os, av, glob
from PIL import Image, ImageFilter

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
A = '/tmp/depart_norm.mp4'
B = base + 'lemanloop_3_docking_reverse.mp4'
TMP = '/tmp/jsmooth'
os.makedirs(TMP, exist_ok=True)
OUT = base + 'lemanloop_depart_complet_v3.mp4'

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# extract frames of both clips as PNGs
run([ff, '-y', '-i', A, os.path.join(TMP, 'a_%04d.png')])
run([ff, '-y', '-i', B, os.path.join(TMP, 'b_%04d.png')])
a_frames = sorted(glob.glob(os.path.join(TMP, 'a_*.png')))
b_frames = sorted(glob.glob(os.path.join(TMP, 'b_*.png')))
print('depart frames:', len(a_frames), '| reverse frames:', len(b_frames))

def sim(i1, i2):
    """0..1 similarity: compare downscaled grayscale."""
    g1 = Image.open(i1).convert('L').resize((64, 46)).filter(ImageFilter.GaussianBlur(1.5))
    g2 = Image.open(i2).convert('L').resize((64, 46)).filter(ImageFilter.GaussianBlur(1.5))
    p1 = list(g1.getdata()); p2 = list(g2.getdata())
    n = len(p1)
    m1 = sum(p1) / n; m2 = sum(p2) / n
    num = sum((a - m1) * (b - m2) for a, b in zip(p1, p2))
    den = (sum((a - m1) ** 2 for a in p1) * sum((b - m2) ** 2 for b in p2)) ** 0.5
    return num / den if den else 0

# depart frames to test as junction: last 12 (skip the most wobbly last 2)
cand_a = a_frames[-14:-2]
# reverse frames to test: first 14
cand_b = b_frames[:14]

best = None
for ia, fa in enumerate(cand_a):
    for ib, fb in enumerate(cand_b):
        s = sim(fa, fb)
        if best is None or s > best[0]:
            best = (s, ia, ib, fa, fb)
print('best match score=%.3f depart_frame=%d reverse_frame=%d' % (best[0], best[1], best[2]))

# rebuild depart WITHOUT its wobbly last frames: keep up to (best depart frame)
keep_a = a_frames[: best[1] + 1]
listing = '/tmp/jsmooth_list.txt'
with open(listing, 'w') as f:
    for fr in keep_a:
        f.write(f"frame '{fr}' 1\n")
    for fr in b_frames[best[2]:]:
        f.write(f"frame '{fr}' 1\n")
# concat demuxer needs video; use image file sequence instead: simplest -> copy all kept frames to one folder with sequential names
seq = os.path.join(TMP, 'seq')
os.makedirs(seq, exist_ok=True)
n = 0
for src in keep_a + b_frames[best[2]:]:
    n += 1
    os.replace(src, os.path.join(seq, 's_%04d.png' % n))
total = n
run([ff, '-y', '-framerate', '30', '-i', os.path.join(seq, 's_%04d.png'),
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', OUT])
c = av.open(OUT)
s = c.streams.video[0]
print('v3 smooth:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
