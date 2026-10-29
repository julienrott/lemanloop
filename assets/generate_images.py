#!/usr/bin/env python3
"""Generate LémanLoop hero/concept images via HF Space FLUX.1-schnell."""
import sys
from pathlib import Path
from gradio_client import Client

OUT = Path.home() / "github" / "lemanloop" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

PROMPTS = {
    "hero.jpg": (
        "Cinematic wide shot: futuristic suspended maglev pod train, small glass-domed panoramic "
        "cabin hanging from an elevated monorail rail, gliding low over a vast deep-blue alpine "
        "lake at golden dawn, snow-capped Alps on the horizon, teal and deep blue tones, mist over "
        "water, swiss precision engineering, photorealistic, serene"
    ),
    "concept.jpg": (
        "Close-up of a sleek futuristic suspended maglev train pod with panoramic glass windows, "
        "silently gliding on an overhead rail above a lakeside promenade with palm trees, deep "
        "blue lake and alpine mountains behind, daylight, teal accents, photorealistic"
    ),
    "experience.jpg": (
        "Interior of a small futuristic panoramic train cabin, ten seats, floor-to-ceiling curved "
        "glass windows showing a huge blue lake and snowy Alps, minimalist white and silver "
        "interior, soft ambient light, eco-friendly design, photorealistic"
    ),
}

def main():
    only = sys.argv[1:] or list(PROMPTS)
    client = Client("black-forest-labs/FLUX.1-schnell")
    for name in only:
        prompt = PROMPTS[name]
        print(f"[{name}] generating...", flush=True)
        try:
            result = client.predict(
                prompt=prompt, seed=0, randomize_seed=True,
                width=1344, height=768, num_inference_steps=4,
                api_name="/infer",
            )
        except Exception as e:
            print(f"[{name}] FAILED: {e}", flush=True)
            continue
        # result = (image_path, seed)
        src = result[0] if isinstance(result, (list, tuple)) else result
        dest = OUT / name
        import shutil
        shutil.copyfile(src, dest)
        print(f"[{name}] OK -> {dest} ({dest.stat().st_size} bytes)", flush=True)

if __name__ == "__main__":
    main()
