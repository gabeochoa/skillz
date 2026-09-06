---
name: demo-video-assembly
description: >
  Stitch captured UI frames and a voiceover track into a polished, frame-accurate demo video with
  ffmpeg. Maps each frame's on-screen span to narration beat timings (from tts-narration) so cuts
  land exactly on the spoken words, loops animated transient bursts (spinners), composites an
  animated cursor + click-pulse to show interactions, and handles the encoding gotchas (retina
  normalization, even h264 dimensions, constant frame rate, tail padding). Use when combining
  screenshots + audio into a video, syncing visuals to narration, adding a cursor/click indicator,
  building a product/feature demo, or when the user says "stitch the video", "assemble the demo",
  "sync frames to audio", "make the demo video", "add a cursor", "show the click", "loop the
  spinner", or "mux the narration". Pairs with ui-capture-cdp, tts-narration, and
  feature-demo-studio. Runs on a CLI node with ffmpeg + Python Pillow (use a venv).
node: cli
---

# Demo Video Assembly

Combine real UI frames + a voiceover into a clean, beat-synced demo video.

## Pipeline

```diagram
frames (ui-capture-cdp) ─┐
                         ├─ normalize → map to beats → slideshow → mux narration → demo.mp4
narration + beats.json ──┘         (cursor anim + spinner loop composited in)
```

## Steps

### 1. Normalize frames (fix retina 2× mismatch)
```bash
bash normalize_frames.sh ~/frames_raw ~/frames 1280 773
```
CDP screenshots can come back 2× (2560×1483) or 1× — get them all to ONE resolution first.

### 2. (Optional) Cursor-click annotation
Show an interaction by compositing a moving cursor + click-pulse onto the base frame:
```bash
python3 cursor_anim.py --base ~/frames/F1.png --outdir ~/frames/click_anim \
  --target 290,122 --start 760,470 --n 18 --fps 15
```
Find the click point's pixel coords by cropping the frame around the element and eyeballing.

### 3. Assemble (frame-accurate to beats)
Edit the TIMELINE in `assemble_video.py` (vocabulary below), then:
```bash
python3 assemble_video.py --base ~/work --frames ~/frames \
  --beats ~/narration_beats.json --wav ~/narration.wav --out ~/demo.mp4
```

### Timeline vocabulary
- `hold(path, dur)` — show a static frame for `dur` seconds
- `animate(frame_glob, span, fps)` — loop a frame sequence (spinner burst / cursor anim) over `span`
- `bs(i)` — start time of beat `i` (from beats.json); `END` — total audio + tail pad
Build each segment's duration from beat starts so visuals track the narration. Split ONE beat
across multiple frames when the sentence spans states (e.g. spinner → resolved).

### 4. Spot-check sync (don't re-watch)
```bash
python3 contact_sheet.py ~/demo.mp4 --times 1 8 15 20 26 36 44 --out /tmp/sheet.png
```
Montage frames at beat midpoints; confirm each frame lands on its intended beat and that
animated sections show real motion (spinner at different angles).

## Encoding gotchas (all handled in assemble_video.py)
- **Even dimensions**: odd height (773) fails libx264 → `pad=ceil(iw/2)*2:ceil(ih/2)*2`.
- **CFR, not vfr+r**: `-vsync vfr` together with `-r` conflicts → use `-fps_mode cfr -r 30`.
- **Concat demuxer**: per-image `duration` lines; repeat the LAST file with no duration.
- **Tail pad ~0.8s** past audio end so the last frame doesn't cut abruptly.
- **Real UI only** — never synthesize product states; only true browser chrome (address bar) may
  be composited.

## Companion files
- `normalize_frames.sh` — unify frame resolution (retina fix) with pad
- `cursor_anim.py` — animated cursor + click-pulse frame generator
- `assemble_video.py` — beat-synced slideshow + narration mux (edit TIMELINE)
- `contact_sheet.py` — montage frames at timestamps to verify sync
