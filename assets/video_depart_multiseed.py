#!/usr/bin/env python3
"""Try 2 extra seeds for the depart interpolation; keep the candidate whose LAST frame
is closest to the target (reverse's first frame) -> best possible hard-cut junction."""
import os, shutil, subprocess, av
from pathlib import Path
from PIL import Image
from gradio_client import Client, handle_file

base = '/home/hermes/github/lemanloop/assets/'
FIRST = base + 'v1b_last.jpg'
LAST = '/tmp/target_768.png'   # frame 25 of docking_reverse
PROMPT = (
    "The white panoramic maglev pod glides away from the futuristic dome station platform, "
    "moving smoothly along the elevated curved guideway toward the open landscape, reflections "
    "of golden sunset slide across its curved glass dome, gentle steady acceleration, "
    "camera static at platform level, photorealistic, cinematic, smooth natural motion"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

def gen(seed, out):
    c = Client('alexnasa/ltx-2-TURBO', verbose=False, token=os.environ.get('HF_TOKEN'))
    result = c.predict(
        first_frame=handle_file(FIRST), end_frame=handle_file(LAST),
        prompt=PROMPT, input_video=None, generation_mode='Image-to-Video',
        enhance_prompt=False, seed=seed, randomize_seed=False,
        height=512, width=768, api_name='/generate_video')
    src = result[0] if isinstance(result, (list, tuple)) else result
    if isinstance(src, dict):
        src = src.get('video') or src.get('path')
    shutil.copyfile(src, out)
    print('SAVED', out, 'seed', seed)
    shutil.copyfile(src, out)
    # measure last-frame diff vs target
    ff = 'ffmpeg'
    def run(cmd):
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run([ff, '-y', '-i', out, '-vf', 'scale=704:512,fps=30', '-an',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '/tmp/cand_n.mp4'])
    c = av.open('/tmp/cand_n.mp4')
    last = None
    i = 0
    for f in c.decode(c.streams.video[0]):
        last = f; i += 1
    p = '/tmp/last_%d.png' % seed
    last.to_image().save(p)
    t = Image.open(LAST).convert('L').resize((64, 46))
    l = Image.open(p).convert('L').resize((64, 46))
    pa = list(l.getdata()); pb = list(t.getdata())
    d = sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)
    print('seed %s: last-frame diff vs target = %.1f' % (seed, d))
    return d, out

results = []
for seed in (7, 131):
    try:
        results.append(gen(seed, base + 'video_depart_seed%d.mp4' % seed))
    except Exception as e:
        print('seed %s failed: %s' % (seed, str(e)[:150]))
results.sort()
print('BEST:', results[0])
