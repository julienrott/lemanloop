#!/usr/bin/env python3
"""AVANT: LTX-2 first/last-frame — capsule departing the dome station → first frame of 3_docking_reverse."""
import os, shutil
from pathlib import Path
from gradio_client import Client, handle_file

FIRST = '/home/hermes/github/lemanloop/assets/v1b_last.jpg'   # pod docked near dome station (end of original docking clip)
LAST  = '/home/hermes/github/lemanloop/assets/v2_first.jpg'   # first frame of 3_docking_reverse (pod moving away)
OUT   = Path.home() / "github" / "lemanloop" / "assets" / "video_depart_gare.mp4"

PROMPT = (
    "The white panoramic maglev pod glides away from the futuristic dome station platform, "
    "moving smoothly along the elevated curved guideway toward the open landscape, reflections "
    "of golden sunset slide across its curved glass dome, gentle steady acceleration, "
    "camera static at platform level, photorealistic, cinematic, smooth natural motion"
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
