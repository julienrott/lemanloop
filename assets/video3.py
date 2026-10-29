#!/usr/bin/env python3
"""Clip 3: disembark focus — image-to-video seeded by the last frame of video 2."""
import shutil
from pathlib import Path
from gradio_client import Client, handle_file

IMG = '/home/hermes/github/lemanloop/assets/v2_last.jpg'
OUT = Path.home() / "github" / "lemanloop" / "assets" / "video3_disembark.mp4"

PROMPT = (
    "A passenger in dark clothing walks calmly out of the stopped pod through the open glass "
    "door onto the platform, then a second and a third passenger exit one after another and "
    "walk away along the platform by the lake, a few other people wait nearby ready to board, "
    "natural human walking movement, camera static at platform level, warm golden hour light, "
    "photorealistic, smooth natural motion"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed, extra limbs"

def main():
    c = Client("Lightricks/ltx-video-distilled", verbose=False)
    result = c.predict(
        prompt=PROMPT,
        negative_prompt=NEG,
        input_image_filepath=handle_file(IMG),
        input_video_filepath=None,
        height_ui=512,
        width_ui=704,
        mode="image-to-video",
        duration_ui=2,
        ui_frames_to_use=9,
        seed_ui=42,
        randomize_seed=True,
        ui_guidance_scale=3.0,
        improve_texture_flag=True,
        api_name="/image_to_video",
    )
    info, seed = result
    src = isinstance(info, dict) and info.get("video") or info.get("path")
    if not src:
        raise SystemExit(f"no file: {result}")
    shutil.copyfile(src, str(OUT))
    print("SEED:", seed)
    print("SAVED:", OUT)

if __name__ == "__main__":
    main()
