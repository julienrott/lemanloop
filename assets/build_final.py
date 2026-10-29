#!/usr/bin/env python3
"""Final montage: depart(seed131, best-landing) + reverse(search best seam pair, color-matched).
No zoom, no fade — best achievable hard cut."""
import subprocess, os, av, glob
from PIL import Image

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
TMP = '/tmp/jfinal'
os.makedirs(TMP, exist_ok=True)
OUT = base + 'lemanloop_depart_final.mp4'

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 1) normalize the best candidate (seed131)
run([ff, '-y', '-i', base + 'video_depart_seed131.mp4',
     '-vf', 'scale=704:512:force_original_aspect_ratio=decrease,pad=704:512:(ow-iw)/2:(oh-ih)/2,fps=30',
     '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
     os.path.join(TMP, 'a.mp4')])
run([ff, '-y', '-i', base + 'lemanloop_3_docking_reverse.mp4', os.path.join(TMP, 'b_%04d.png')])
run([ff, '-y', '-i', os.path.join(TMP, 'a.mp4'), os.path.join(TMP, 'a_%04d.png')])
a = sorted(glob.glob(os.path.join(TMP, 'a_*.png')))
b = sorted(glob.glob(os.path.join(TMP, 'b_*.png')))

def diff(f1, f2):
    g1 = Image.open(f1).convert('L').resize((64, 46))
    g2 = Image.open(f2).convert('L').resize((64, 46))
    p1 = list(g1.getdata()); p2 = list(g2.getdata())
    return sum(abs(x - y) for x, y in zip(p1, p2)) / len(p1)

# search best (a_tail x b) pair overall
best = None
for ia in range(len(a) - 10, len(a)):
    for ib in range(0, 46):
        d = diff(a[ia], b[ib])
        if best is None or d < best[0]:
            best = (d, ia, ib)
d, ia, ib = best
print('best seam: depart#%d <-> reverse#%d diff=%.1f' % (ia, ib, d))

# color-match b segment's first ~15 frames (function of gains at seam) — light correction
A_ref = Image.open(a[ia]).convert('RGB').resize((128, 92))
B_ref = Image.open(b[ib]).convert('RGB').resize((128, 92))
gains = []
for ch in range(3):
    mA = sum(p[ch] for p in A_ref.getdata()) / (128 * 92)
    mB = sum(p[ch] for p in B_ref.getdata()) / (128 * 92)
    g = min(2.0, max(0.5, mA / max(8, mB)))
    gains.append(g)
print('gains:', [round(g, 2) for g in gains])

# copy matched frames
for fr in b[:ib]:
    os.rename(fr, fr)  # keep
out_frames = a[:ia + 1]
seqdir = os.path.join(TMP, 'seq')
os.makedirs(seqdir, exist_ok=True)
# clear old
for f in glob.glob(os.path.join(seqdir, 's_*.png')):
    os.remove(f)
n = 0
for fpath in out_frames:
    n += 1
    os.replace(fpath, os.path.join(seqdir, 's_%04d.png' % n))
# apply color-match per frame on the remaining reverse frames (cheap PIL match)
for fpath in b[ib:]:
    im = Image.open(fpath).convert('RGB')
    px = im.load()
    for x in range(0, im.width, 4):
        for y in range(0, im.height, 4):
            r, g, bl = px[x, y]
            px[x, y] = (min(255, int(r * gains[0])), min(255, int(g * gains[1])), min(255, int(bl * gains[2])))
    im.save(fpath)
    n += 1
    os.replace(fpath, os.path.join(seqdir, 's_%04d.png' % n))
total = n

run([ff, '-y', '-framerate', '30', '-i', os.path.join(seqdir, 's_%04d.png'),
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', OUT])
c = av.open(OUT)
s = c.streams.video[0]
print('final:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's, seam diff %.1f' % d)
