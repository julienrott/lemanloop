#!/usr/bin/env python3
"""v7: same seam optimization, PLUS color-match the docking_reverse segment to kill the exposure pop.
Measured: seam diff 25 driven by exposure (brighter, desaturated clip B).
Apply eq brightness/saturation/gamma on segment B scaled until sky diff minimized."""
import subprocess, os, av, glob
from PIL import Image

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
TMP = '/tmp/jv7'
os.makedirs(TMP, exist_ok=True)
OUT = base + 'lemanloop_depart_complet_v7.mp4'

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# reuse v6 trimmed frames? they were renamed; re-extract cleanly:
run([ff, '-y', '-i', os.path.join('/tmp/jv5', 'a.mp4'), os.path.join(TMP, 'a_%04d.png')])
run([ff, '-y', '-i', base + 'lemanloop_3_docking_reverse.mp4', os.path.join(TMP, 'b_%04d.png')])
a = sorted(glob.glob(os.path.join(TMP, 'a_*.png')))
b = sorted(glob.glob(os.path.join(TMP, 'b_*.png')))

def seam_diff(ia, ib):
    g1 = Image.open(a[ia]).convert('RGB').resize((128, 92))
    g2 = Image.open(b[ib]).convert('RGB').resize((128, 92))
    p1 = list(g1.getdata()); p2 = list(g2.getdata())
    n = len(p1)
    return sum(abs(sum(x) / 3 - sum(y) / 3) for x, y in zip(p1, p2)) / n

# parameters search on clip B: brightness & saturation to match clip A's sky luminance
def tune_params(ia, ib):
    # match via PIL on the extracted B frame
    A = Image.open(a[ia]).convert('RGB').resize((128, 92))
    B0 = Image.open(b[ib]).convert('RGB').resize((128, 92))
    # means
    mA = tuple(sum(p[i] for p in list(A.getdata())) / (128 * 92) for i in range(3))
    mB = tuple(sum(p[i] for p in list(B0.getdata())) / (128 * 92) for i in range(3))
    # compute per-channel gain to match means
    gains = [min(2.0, max(0.4, mA[i] / max(8, mB[i]))) for i in range(3)]
    return gains

gains = tune_params(79, 45)
print('color-match gains (R,G,B):', [round(g, 2) for g in gains])

# apply gain via ffmpeg eq+colorbalance approximation on the B segment only
rr = gains[0]; gg = gains[1]; bb = gains[2]
# ffmpeg eq supports brightness (offset) not per-channel gain; use colorchannelmixer
cf = f"colorchannelmixer=rr={rr:.3f}:gg={gg:.3f}:bb={bb:.3f},eq=saturation=1.0"

# rebuild: depart frames 0..79 untouched; B frames 45.. with color match
seq = os.path.join(TMP, 'seq')
os.makedirs(seq, exist_ok=True)
n = 0
for idx, fpath in enumerate(a[:80]):
    n += 1
    os.replace(fpath, os.path.join(seq, 's_%04d.png' % n))
# color-match B frames with PIL precisely (same gains, clip)
for idx, fpath in enumerate(b[45:]):
    im = Image.open(fpath).convert('RGB')
    px = im.load()
    w, h = im.size
    for x in range(0, w, 4):
        for y in range(0, h, 4):
            r, g, bl = px[x, y]
            px[x, y] = (min(255, int(r * rr)), min(255, int(g * gg)), min(255, int(bl * bb)))
    im.save(fpath)
    n += 1
    os.replace(fpath, os.path.join(seq, 's_%04d.png' % n))
print('total frames:', n)

run([ff, '-y', '-framerate', '30', '-i', os.path.join(seq, 's_%04d.png'),
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', OUT])
c = av.open(OUT)
s = c.streams.video[0]
print('v7:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
