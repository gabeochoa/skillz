#!/usr/bin/env python3
"""Assemble a demo video: map UI frames to narration beats (frame-accurate), build a slideshow,
and mux the voiceover. Handles the encoding gotchas we hit (retina normalize, even dims, cfr).

This is a TEMPLATE — edit the TIMELINE for your demo. Requires ffmpeg.

Inputs:
  - normalized frames (all same resolution) in FRAMES_DIR
  - narration WAV + its *_beats.json (from tts-narration)
Optional:
  - animated sub-sequences (spinner burst, cursor-click anim) as frame globs
"""
import json, subprocess, os, glob, argparse

def build(base, frames_dir, beats_json, narration_wav, timeline, out, tail_pad=0.8, fps=30):
    beats = json.load(open(beats_json))["beats"]
    TOTAL = json.load(open(beats_json))["total_s"]
    def bs(i): return beats[i]["start"]
    END = TOTAL + tail_pad

    rows = []  # (path, dur)
    def hold(path, dur): rows.append((path, max(dur, 0.03)))
    def animate(frame_glob, span, afps):
        frames = sorted(glob.glob(frame_glob))
        if not frames: raise SystemExit("no frames: " + frame_glob)
        per = 1.0 / afps
        for k in range(max(1, int(round(span / per)))):
            rows.append((frames[k % len(frames)], per))

    # timeline is a list of dicts describing each segment; see SKILL.md for the vocabulary
    ctx = {"hold": hold, "animate": animate, "bs": bs, "END": END, "FR": frames_dir, "beats": beats}
    timeline(ctx)

    concat = f"{base}/_frames_concat.txt"
    with open(concat, "w") as c:
        for p, d in rows:
            c.write(f"file '{p}'\n"); c.write(f"duration {round(d,4)}\n")
        c.write(f"file '{rows[-1][0]}'\n")
    vid_dur = sum(d for _, d in rows)
    print(f"{len(rows)} rows, video ~{vid_dur:.2f}s, audio {TOTAL:.2f}s")

    silent = f"{base}/_silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", concat,
        "-fps_mode", "cfr", "-r", str(fps),
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:color=0x171717",  # even dims for h264
        "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "medium", silent], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", narration_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", out], check=True)
    print("WROTE", out)

# ---- EXAMPLE TIMELINE (edit for your demo) --------------------------------
def example_timeline(ctx):
    hold, animate, bs, END, FR = ctx["hold"], ctx["animate"], ctx["bs"], ctx["END"], ctx["FR"]
    # beats 0-1: F1 static, then a 1.2s cursor-click anim ending as the dialog opens (beat 2)
    click_span = 1.2
    hold(f"{FR}/F1.png", bs(2) - click_span)
    animate(f"{FR}/click_anim/click_*.png", click_span, 15)
    hold(f"{FR}/F2.png", bs(3) - bs(2))
    hold(f"{FR}/F3.png", bs(4) - bs(3))
    hold(f"{FR}/F0.png", bs(6) - bs(4))
    # beat 6 spans a transient: animated spinner then resolved
    spin_span = 3.8
    animate(f"{FR}/spinner/frame_*.png", spin_span, 14)
    hold(f"{FR}/F5.png", (bs(7) - bs(6)) - spin_span)
    hold(f"{FR}/F6.png", bs(9) - bs(7))
    hold(f"{FR}/F5.png", bs(10) - bs(9))
    hold(f"{FR}/F6.png", END - bs(10))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--beats", required=True)
    ap.add_argument("--wav", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.base, a.frames, a.beats, a.wav, example_timeline, a.out)
