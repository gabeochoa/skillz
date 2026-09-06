#!/usr/bin/env python3
"""Composite an animated cursor + click-pulse onto a base frame to SHOW an interaction
(e.g. "the user clicked this toggle"). Produces a frame sequence you loop into the video.

Usage:
  python3 cursor_anim.py --base frame.png --outdir out/click \
    --target 290,122 --start 760,470 --n 18 --fps 15
"""
import argparse, os, math
from PIL import Image, ImageDraw

def make_cursor(size=30):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(2,2),(2,int(s*0.72)),(int(s*0.2),int(s*0.56)),(int(s*0.32),int(s*0.86)),
           (int(s*0.44),int(s*0.81)),(int(s*0.32),int(s*0.52)),(int(s*0.54),int(s*0.52))]
    d.polygon(pts, fill=(255,255,255,255), outline=(0,0,0,255))
    d.line(pts+[pts[0]], fill=(0,0,0,255), width=4, joint="curve")
    return im.resize((size, size), Image.LANCZOS)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--target", required=True, help="x,y of click point")
    ap.add_argument("--start", required=True, help="x,y where cursor begins")
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--fps", type=int, default=15)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    tx, ty = map(int, a.target.split(",")); sx, sy = map(int, a.start.split(","))
    base = Image.open(a.base).convert("RGB"); cur = make_cursor(30)
    for i in range(a.n):
        fr = base.copy(); t = i / (a.n - 1)
        if t < 0.62:
            te = t / 0.62; ease = 1 - (1 - te) ** 2
            cx = sx + (tx - sx) * ease; cy = sy + (ty - sy) * ease
        else:
            cx, cy = tx, ty
            pt = (t - 0.62) / 0.38  # click pulse
            d = ImageDraw.Draw(fr, "RGBA")
            r = int(6 + pt * 26); alpha = int(200 * (1 - pt))
            d.ellipse([tx-r, ty-r, tx+r, ty+r], outline=(255,255,255,alpha), width=3)
            if pt < 0.25:
                d.ellipse([tx-8, ty-8, tx+8, ty+8], fill=(255,255,255,int(120*(1-pt*4))))
        fr.paste(cur, (int(cx), int(cy)), cur)
        fr.save(f"{a.outdir}/click_{i:02d}.png")
    print(f"wrote {a.n} click frames to {a.outdir}")

if __name__ == "__main__":
    main()
