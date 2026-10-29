#!/usr/bin/env python3
"""Generate new LémanLoop hero matching the concept image pod design."""
import shutil, time, sys
from pathlib import Path
from gradio_client import Client

OUT = Path.home() / "github" / "lemanloop" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

PROMPT = (
    "Cinematic wide shot, dawn golden hour: a sleek white futuristic monorail pod train with a "
    "huge teal-tinted panoramic glass dome windshield, pill-shaped aerodynamic body, gliding on a "
    "thin elevated white monorail guideway on slim white pillars, suspended above a vast deep blue "
    "alpine lake, dramatic snow-capped Alps mountains on both sides, turquoise teal glass reflecting "
    "mountains, photorealistic, teal and deep blue color grade, low angle tracking shot from the water, "
    "serene mist over the lake, swiss precision infrastructure"
)

def main():
    client = Client("black-forest-labs/FLUX.1-schnell")
    for attempt in range(3):
        try:
            result = client.predict(
                prompt=PROMPT, seed=0, randomize_seed=True,
                width=1344, height=768, num_inference_steps=4,
                api_name="/infer",
            )
            src = result[0] if isinstance(result, (list, tuple)) else result
            dest = OUT / "hero_v2.webp"
            shutil.copyfile(src, dest)
            print(f"OK -> {dest} ({dest.stat().st_size} bytes)", flush=True)
            return
        except Exception as e:
            print(f"attempt {attempt+1} FAILED: {e}", flush=True)
            if attempt < 2:
                time.sleep(180)
    sys.exit(1)

if __name__ == "__main__":
    main()
