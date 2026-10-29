#!/usr/bin/env python3
"""Generate LémanLoop video 1: concept.jpg (image-to-video) via LTX-Video Space."""
import shutil
from pathlib import Path
from gradio_client import Client, handle_file

IMG = str(Path.home() / "github" / "lemanloop" / "assets" / "concept.jpg")
OUT = Path.home() / "github" / "lemanloop" / "assets" / "video1_cruise.mp4"

PROMPT = (
    "Cinematic aerial tracking shot: a sleek white futuristic maglev pod train with a huge "
    "panoramic glass dome gliding silently on an elevated monorail guideway above a vast deep "
    "blue alpine lake at golden hour, snow-capped Alps on the horizon, the pod glides forward "
    "steadily along the track over the water, mist over the lake, teal and deep blue color "
    "grade, photorealistic, serene, smooth motion"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

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
