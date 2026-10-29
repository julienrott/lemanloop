#!/usr/bin/env python3
"""v6: minimize the visible seam WITHOUT zoom/fade:
- search the (depart_v4 tail frame x reverse frame) pair with the smallest pixel diff
- trim: depart ends at that frame, reverse starts at that frame
- also try skipping a near-duplicate if reverse#26 equals #25
"""
import subprocess, os, av, glob
from PIL import Image

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
TMP = '/tmp/jv6'
os.makedirs(TMP, exist_ok=True)
OUT = base + 'lemanloop_depart_complet_v6.mp4'

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# extract all frames of both normalized sources
run([ff, '-y', '-i', os.path.join('/tmp/jv5', 'a.mp4'), os.path.join(TMP, 'a_%04d.png')])
run([ff, '-y', '-i', base + 'lemanloop_3_docking_reverse.mp4', os.path.join(TMP, 'b_%04d.png')])
a = sorted(glob.glob(os.path.join(TMP, 'a_*.png')))
b = sorted(glob.glob(os.path.join(TMP, 'b_*.png')))

def diff(f1, f2):
    g1 = Image.open(f1).convert('L').resize((64, 46))
    g2 = Image.open(f2).convert('L').resize((64, 46))
    p1 = list(g1.getdata()); p2 = list(g2.getdata())
    return sum(abs(x - y) for x, y in zip(p1, p2)) / len(p1)

# search: depart tail (last 12 frames) x reverse (frames 10..45)
best = None
for ia in range(len(a) - 12, len(a)):
    for ib in range(10, 46):
        if ib >= len(b): break
        d = diff(a[ia], b[ib])
        if best is None or d < best[0]:
            best = (d, ia, ib)
d, ia, ib = best
print('best seam: depart#%d <-> reverse#%d  diff=%.1f' % (ia, ib, d))

seq = os.path.join(TMP, 'seq')
os.makedirs(seq, exist_ok=True)
n = 0
for list_ in (a[:ia + 1], b[ib:]):
    for fpath in list_:
        n += 1
        os.replace(fpath, os.path.join(seq, 's_%04d.png' % n))
total = n
run([ff, '-y', '-framerate', '30', '-i', os.path.join(seq, 's_%04d.png'),
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', OUT])
c = av.open(OUT)
s = c.streams.video[0]
print('v6:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's (seam diff %.1f)' % d)
