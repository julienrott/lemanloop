#!/usr/bin/env python3
"""Merge: depart clip (normalized) + lemanloop_3_docking_reverse -> lemanloop_depart_complet.mp4"""
import subprocess, os, av

ff = 'ffmpeg'
base = '/home/hermes/github/lemanloop/assets/'

subprocess.run([
    ff, '-y', '-i', base + 'video_depart_gare.mp4',
    '-vf', 'scale=704:512:force_original_aspect_ratio=decrease,pad=704:512:(ow-iw)/2:(oh-ih)/2,fps=30',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
    '/tmp/depart_norm.mp4'
], check=True, capture_output=True)

lst = '/tmp/concat5.txt'
with open(lst, 'w') as f:
    f.write("file '/tmp/depart_norm.mp4'\n")
    f.write(f"file '{base}lemanloop_3_docking_reverse.mp4'\n")

out = base + 'lemanloop_depart_complet.mp4'
subprocess.run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out],
               check=True, capture_output=True)

c = av.open(out)
s = c.streams.video[0]
print('depart complet:', s.frames, 'frames,', round(os.path.getsize(out) / 1024), 'Ko,', round(s.frames / 30, 1), 's')
