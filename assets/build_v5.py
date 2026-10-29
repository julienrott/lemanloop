#!/usr/bin/env python3
"""Build v5 montage: depart_v4 (normalized) + docking_reverse trimmed to start at frame 25 (its target).
Hard junction on near-matching composition, no zoom, no fade."""
import subprocess, os, av

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'
TMP = '/tmp/jv5'
os.makedirs(TMP, exist_ok=True)
OUT = base + 'lemanloop_depart_complet_v5.mp4'

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 1) normalize depart_v4 to 704x512@30
run([ff, '-y', '-i', base + 'video_depart_v4.mp4',
     '-vf', 'scale=704:512:force_original_aspect_ratio=decrease,pad=704:512:(ow-iw)/2:(oh-ih)/2,fps=30',
     '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
     os.path.join(TMP, 'a.mp4')])

# 2) docking_reverse from frame 25 (skip the matched part already covered by depart_v4's end)
run([ff, '-y', '-i', base + 'lemanloop_3_docking_reverse.mp4',
     '-vf', "select='gte(n,25)'", '-vsync', 'cfr', '-an',
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
     os.path.join(TMP, 'b.mp4')])

# 3) concat
lst = os.path.join(TMP, 'list.txt')
open(lst, 'w').write(f"file '{TMP}/a.mp4'\nfile '{TMP}/b.mp4'\n")
run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', OUT])

c = av.open(OUT)
s = c.streams.video[0]
print('v5:', s.frames, 'frames,', round(os.path.getsize(OUT) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
