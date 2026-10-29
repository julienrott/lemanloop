#!/usr/bin/env python3
"""Resize/optimize LémanLoop assets for web."""
from PIL import Image
from pathlib import Path

A = Path.home() / "github" / "lemanloop" / "assets"

# concept.jpg: 2752x1536 -> resize to 1920 wide, quality 82
im = Image.open(A / "concept.jpg").convert("RGB")
w, h = im.size
nw = 1920
nh = round(h * nw / w)
im = im.resize((nw, nh), Image.LANCZOS)
im.save(A / "concept.jpg", "JPEG", quality=82, optimize=True, progressive=True)
print("concept:", im.size, (A / "concept.jpg").stat().st_size, "bytes")

# hero.jpg: check current
im2 = Image.open(A / "hero.jpg")
print("hero:", im2.size, im2.mode, (A / "hero.jpg").stat().st_size, "bytes")
