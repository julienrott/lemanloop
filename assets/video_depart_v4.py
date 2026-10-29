#!/usr/bin/env python3
"""Regenerate the depart clip with last_frame = frame 25 of docking_reverse.
Frame 25 is the best-matching composition to the depart clip's natural end framing,
giving LTX-2 the most plausible interpolation target -> fluid hard-cut junction."""
import os, shutil, subprocess, av
from pathlib import Path
from PIL import Image
from gradio_client import Client, handle_file

base = '/home/hermes/github/lemanloop/assets/'
HOST = "alexnasa/ltx-2-TURBO"

ffmpeg = 'ffmpeg'
def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# extract frame 25 (0-based, 26th frame) of docking_reverse as the target last frame
TMP = '/tmp/jg2'
os.makedirs(TMP, exist_ok=True)
run([ffmpeg, '-y', '-i', base + 'lemanloop_3_docking_reverse.mp4',
     '-vf', "select='eq(n,25)'", '-vsync', '0', '-frames:v', '1',
     os.path.join(TMP, 'target.png')])
assert os.path.exists(os.path.join(TMP, 'target.png')), 'failed to extract target frame'

# upscale target to 768x512 for LTX (it expects min 768x512)
im = Image.open(os.path.join(TMP, 'target.png')).convert('RGB')
im = im.resize((768, 512), Image.LANCZOS)
im.save('/tmp/target_768.png')

FIRST = '/home/hermes/github/lemanloop/assets/v1b_last.jpg'
LAST = '/tmp/target_768.png'
OUT = Path.home() / 'github' / 'lemanloop' / 'assets' / 'video_depart_v4.mp4'

PROMPT = (
    "The white panoramic maglev pod glides away from the futuristic dome station platform, "
    "moving smoothly along the elevated curved guideway toward the open landscape, reflections "
    "of golden sunset slide across its curved glass dome, gentle steady acceleration, "
    "camera static at platform level, photorealistic, cinematic, smooth natural motion"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

def main():
    c = Client(HOST, verbose=False, token=os.environ.get('HF_TOKEN'))
    result = c.predict(
        first_frame=handle_file(FIRST),
        end_frame=handle_file(LAST),
        prompt=PROMPT,
        input_video=None,
        generation_mode='Image-to-Video',
        enhance_prompt=False,
        seed=10,
        randomize_seed=True,
        height=512,
        width=768,
        api_name='/generate_video',
    )
    src = result[0] if isinstance(result, (list, tuple)) else result
    if isinstance(src, dict):
        src = src.get('video') or src.get('path')
    if not src:
        raise SystemExit(f'no file: {result}')
    shutil.copyfile(src, str(OUT))
    print('SAVED:', OUT)

if __name__ == '__main__':
    from PIL import Image
    main()
