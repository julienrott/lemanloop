#!/usr/bin/env python3
"""Generate LémanLoop video 2: station arrival + disembark/embark via LTX text-to-video."""
import shutil
from pathlib import Path
from gradio_client import Client

OUT = Path.home() / "github" / "lemanloop" / "assets" / "video2_station.mp4"

PROMPT = (
    "Interior view of a futuristic minimal train station platform by an alpine lake: a sleek "
    "white panoramic maglev pod with curved glass dome arrives smoothly at the platform and "
    "stops, glass doors open, a few passengers step out calmly, other passengers board, doors "
    "close, warm daylight reflecting on the glass, clean white architecture with teal accents, "
    "photorealistic, cinematic side angle, natural human motion, smooth movement"
)
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed"

def main():
    c = Client("Lightricks/ltx-video-distilled", verbose=False)
    result = c.predict(
        prompt=PROMPT,
        negative_prompt=NEG,
        input_image_filepath=None,
        input_video_filepath=None,
        height_ui=512,
        width_ui=704,
        mode="text-to-video",
        duration_ui=2,
        ui_frames_to_use=9,
        seed_ui=42,
        randomize_seed=True,
        ui_guidance_scale=3.0,
        improve_texture_flag=True,
        api_name="/text_to_video",
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
