#!/usr/bin/env python3
"""Clip 0 (approach) via LTX-2 first/last-frame: start = distant pod, end = v2_first (pod at dock)."""
import shutil
from pathlib import Path
import os
from gradio_client import Client, handle_file

# first frame of the approach = a frame of video1 (pod cruising on the lake, far from station)
FIRST_SRC = '/home/hermes/github/lemanloop/assets/v2_first.jpg'   # docked pod (end state)
# We need a START image: pod far away. Use video1's first frame (cruising wide shot).
CRUISE = '/home/hermes/github/lemanloop/assets/v1_first.jpg'

OUT = Path.home() / "github" / "lemanloop" / "assets" / "video0_approach.mp4"

PROMPT = (
    "The white panoramic maglev pod glides forward along the elevated guideway toward the "
    "lakeside station platform, decelerating smoothly as it approaches the dock, reflections "
    "of golden sunset sliding across its curved glass dome, camera static, gentle continuous "
    "motion, photorealistic, cinematic"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

def main():
    c = Client("alexnasa/ltx-2-TURBO", verbose=False, token=os.environ.get("HF_TOKEN"))
    result = c.predict(
        first_frame=handle_file(CRUISE),
        end_frame=handle_file(FIRST_SRC),
        prompt=PROMPT,
        input_video=None,
        generation_mode="Image-to-Video",
        enhance_prompt=False,
        seed=10,
        randomize_seed=True,
        height=512,
        width=768,
        api_name="/generate_video",
    )
    src = result[0] if isinstance(result, (list, tuple)) else result
    if isinstance(src, dict):
        src = src.get("video") or src.get("path")
    if not src:
        raise SystemExit(f"no file: {result}")
    shutil.copyfile(src, str(OUT))
    print("SAVED:", OUT)

if __name__ == "__main__":
    main()
