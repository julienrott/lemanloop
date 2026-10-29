#!/usr/bin/env python3
"""Redo the depart clip with LEFTWARD motion (same direction as 3_docking_reverse).
Strategy: generate several candidates (different seeds) with an explicitly directional prompt,
verify the actual travel direction by tracking the pod's white-blob centroid, keep the one
that moves left, then seam-match into 3_docking_reverse (no zoom, no fade).
"""
import os, shutil, subprocess, glob, sys
import numpy as np
import av
from pathlib import Path
from PIL import Image
from gradio_client import Client, handle_file

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
TMP = '/tmp/jredo'
os.makedirs(TMP, exist_ok=True)
FINAL = base + 'lemanloop_depart_complet_v8.mp4'

FIRST = base + 'v1b_last.jpg'          # pod near the dome station
PROMPT = (
    "The white panoramic maglev pod departs the futuristic dome station and glides leftward "
    "away along the elevated curved guideway, leaving the dome behind on the right side of "
    "the frame, monotone steady motion to the left, reflections of golden sunset slide across "
    "its curved glass dome, camera static at platform level, photorealistic, cinematic, "
    "smooth consistent leftward travel"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def gen_clip(seed, out):
    c = Client('alexnasa/ltx-2-TURBO', verbose=False, token=os.environ.get('HF_TOKEN'))
    result = c.predict(
        first_frame=handle_file(FIRST), end_frame=None,
        prompt=PROMPT, input_video=None, generation_mode='Image-to-Video',
        enhance_prompt=False, seed=seed, randomize_seed=False,
        height=512, width=768, api_name='/generate_video')
    src = result[0] if isinstance(result, (list, tuple)) else result
    if isinstance(src, dict):
        src = src.get('video') or src.get('path')
    shutil.copyfile(src, out)
    return out

def pod_track(mp4):
    """Track centroid x of near-white pixels in the pod band; returns per-frame x list."""
    c = av.open(mp4)
    xs = []
    for frame in c.decode(c.streams.video[0]):
        img = frame.to_image().convert('RGB')
        a = np.asarray(img).astype(int)
        # pod band: rows 38-62% of height; near-white mask
        h, w, _ = a.shape
        band = a[int(h * 0.38):int(h * 0.62), :, :]
        mask = (band[:, :, 0] > 205) & (band[:, :, 1] > 205) & (band[:, :, 2] > 200)
        if mask.sum() > 50:
            xs.append(mask.sum(axis=0).astype(float) @ np.arange(w) / mask.sum())
        else:
            xs.append(None)
    return xs

def direction_slope(xs):
    pts = [(i, x) for i, x in enumerate(xs) if x is not None]
    if len(pts) < 5:
        return None
    idx = np.array([p[0] for p in pts], float)
    val = np.array([p[1] for p in pts], float)
    slope = np.polyfit(idx, val, 1)[0]
    return slope  # negative = moving left

# generate candidates
cands = []
for seed in (5, 9, 21):
    try:
        clip = os.path.join(TMP, f'dep_{seed}.mp4')
        gen_clip(seed, clip)
        # normalize to 704x512
        norm = os.path.join(TMP, f'dep_{seed}_n.mp4')
        run([ff, '-y', '-i', clip,
             '-vf', 'scale=704:512:force_original_aspect_ratio=decrease,pad=704:512:(ow-iw)/2:(oh-ih)/2,fps=30',
             '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', norm])
        xs = pod_track(norm)
        slope = direction_slope(xs)
        print(f'seed {seed}: slope = {slope:.1f} px/frame')
        if slope is not None and slope < -1:   # moving LEFT
            cands.append((slope, seed, norm))
        else:
            print(f'seed {seed}: REJECTED (not clearly leftward)')
    except Exception as e:
        print(f'seed {seed} failed:', str(e)[:160])

if not cands:
    sys.exit('no candidate with leftward motion — abort before montage')

cands.sort()
slope, seed, clip = cands[0]
print(f'using seed {seed} (leftward slope {slope:.1f})')

# seam-match into 3_docking_reverse: search best (depart_tail x reverse_start) pair
a_png = os.path.join(TMP, 'a_%04d.png')
b_png = os.path.join(TMP, 'b_%04d.png')
for f in glob.glob(os.path.join(TMP, 'a_*.png')): os.remove(f)
for f in glob.glob(os.path.join(TMP, 'b_*.png')): os.remove(f)
run([ff, '-y', '-i', clip, a_png])
run([ff, '-y', '-i', base + 'lemanloop_3_docking_reverse.mp4', b_png])
a = sorted(glob.glob(a_png)); b = sorted(glob.glob(b_png))
# color-feed skip: extract grayscale arrays
def arr(f):
    return np.asarray(Image.open(f).convert('L').resize((64, 46)), dtype=float)
A_ALL = [arr(f) for f in a]; B_ALL = [arr(f) for f in b]
def diff(ia, ib):
    return float(np.abs(A_ALL[ia] - B_ALL[ib]).mean())

best = None
for ia in range(len(a) - 12, len(a)):
    for ib in range(0, 40):
        d = diff(ia, ib)
        if best is None or d < best[0]:
            best = (d, ia, ib)
d, ia, ib = best
print('best seam: depart#%d <-> reverse#%d diff=%.1f' % (ia, ib, d))

# color-match reverse start frames to the depart frame (per-channel gain)
A_ref = np.asarray(Image.open(a[ia]).convert('RGB').resize((160, 116)), dtype=float)
B_ref = np.asarray(Image.open(b[ib]).convert('RGB').resize((160, 116)), dtype=float)
gains = np.clip(A_ref.mean(axis=(0, 1)) / np.maximum(8, B_ref.mean(axis=(0, 1))), 0.6, 1.6)
print('gains:', np.round(gains, 2))

seq = os.path.join(TMP, 'seq')
os.makedirs(seq, exist_ok=True)
for f in glob.glob(os.path.join(seq, 's_*.png')): os.remove(f)
n = 0
for fr in a[:ia + 1]:
    n += 1
    os.replace(fr, os.path.join(seq, 's_%04d.png' % n))
for fr in b[ib:]:
    im = Image.open(fr).convert('RGB').resize((768, 512), Image.LANCZOS)
    p = np.asarray(im, dtype=float) * gains
    im2 = Image.fromarray(np.clip(p, 0, 255).astype('uint8'))
    im2.save(os.path.join(seq, 's_%04d.png' % n))
    n += 1

run([ff, '-y', '-framerate', '30', '-i', os.path.join(seq, 's_%04d.png'),
     '-vf', 'scale=704:512', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
     '-pix_fmt', 'yuv420p', FINAL])
c = av.open(FINAL)
s = c.streams.video[0]
print('FINAL:', FINAL, s.frames, 'frames,', round(os.path.getsize(FINAL) / 1024), 'Ko,',
      round(s.frames / 30, 1), 's, seam diff %.1f' % d)
