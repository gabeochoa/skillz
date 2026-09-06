#!/usr/bin/env python3
"""Spot-check sync/animation without re-watching: extract frames at given timestamps and montage.
Usage: python3 contact_sheet.py video.mp4 --times 1 8 15 20 26 36 44 --out sheet.png
"""
import argparse, subprocess, os, tempfile
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--times", nargs="+", type=float, required=True)
    ap.add_argument("--out", default="/tmp/contact_sheet.png"); ap.add_argument("--cols", type=int, default=2)
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(); paths = []
    for t in a.times:
        p = f"{tmp}/t{t}.png"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(t),"-i",a.video,"-frames:v","1",p], check=True)
        paths.append((t, p))
    ims = [(t, Image.open(p)) for t, p in paths]
    w, h = ims[0][1].size; sc = 0.36; tw, th = int(w*sc), int(h*sc)
    cols = a.cols; rows = (len(ims) + cols - 1) // cols; lab = 26; pad = 8
    sheet = Image.new("RGB", (cols*tw+(cols+1)*pad, rows*(th+lab)+pad), (20,20,20))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(sheet)
    try: f = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 16)
    except Exception: f = ImageFont.load_default()
    for i, (t, im) in enumerate(ims):
        r, c = divmod(i, cols); x = pad + c*(tw+pad); y = pad + r*(th+lab)
        d.text((x, y), f"t={t}s", font=f, fill=(230,230,230))
        sheet.paste(im.resize((tw, th)), (x, y+lab))
    sheet.save(a.out); print("wrote", a.out, sheet.size)

if __name__ == "__main__":
    main()
