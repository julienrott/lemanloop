#!/usr/bin/env python3
"""Clip 1b: deceleration into the station — LTX-2 first/last-frame.
first = last frame of approach clip (pod on viaduct, open landscape)
last  = first frame of video2 (pod docked at the platform)
The model interpolates the arrival: pod approaches, slows, docks.
"""
import os, shutil
from pathlib import Path
from gradio_client import Client, handle_file

FIRST = '/home/hermes/github/lemanloop/assets/v0_last.jpg'
LAST = '/home/hermes/github/lemanloop/assets/v2_first.jpg'
OUT = Path.home() / "github" / "lemanloop" / "assets" / "video1b_dock.mp4"

PROMPT = (
    "The white panoramic maglev pod glides forward along the elevated guideway and arrives at "
    "a futuristic lakeside station platform, decelerating smoothly until it comes to a stop "
    "docked at the platform, reflections of golden sunset slide across its curved glass dome, "
    "camera static at platform level, gentle continuous deceleration, photorealistic, cinematic"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

def main():
    c = Client("alexnasa/ltx-2-TURBO", verbose=False, token=os.environ.get("HF_TOKEN"))
    result = c.predict(
        first_frame=handle_file(FIRST),
        end_frame=handle_file(LAST),
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
