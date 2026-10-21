---
name: draw-process-video
description: Produce a "real paint-app drawing process" video — a subject drawn stroke by stroke in a real painting program (KolourPaint) with visible cursor, sped up to ~70 s, with drawing SFX and a dense BGM bed. Use when asked to make a drawing/painting-process clip of a character or scene. Not for 3D explainers (use the parent skill).
version: 0.2.0
---

# Draw-Process Video (real paint app)

A real painting app is driven by synthetic mouse input on a private virtual display and screen-recorded. The result looks like a person drawing: line art, then bucket fills, then background, then details.

## 1. Inputs (ask only for what is missing)

| Input | Default |
|---|---|
| Subject | required. Character or scene. |
| Aspect / resolution | 4:3 **1440×1080**. Also supports 9:16 1080×1920 (recalibrate the `ui` block). |
| Target duration | **65–75 s** (70 s typical), including a ~4 s final hold |
| BGM source | a file the user supplies, a Douyin link the user gives, or the original synthesized ditty (fallback) |

## 2. Drawing

- Install: `sudo apt-get install -y kolourpaint xvfb xdotool ffmpeg imagemagick`.
- Use a **private Xvfb display** (`:77`, or any free number). Never draw on the shared desktop.
- Describe the subject as a **stroke JSON** in canvas coordinates. See `examples/peppa_strokes.json`.
  - Ops: `color{c}`, `stroke{pts,amp,dl}` (sampled polyline, resampled to 4 px, with small sine wobble), `fill{seeds}` (bucket clicks), `pause{s}`.
  - Build the geometry with Catmull-Rom curves and ellipses in Python, then dump the JSON. Thick limbs are 3 parallel strokes offset ±5 px. A dot is concentric ellipses.
- **Order:** line art → character fills (bucket) → background lines (hills, sun, cloud, tree, puddle) → background fills (sky last; use several seeds) → details (rays, grass tufts, flowers, splashes).
  - Draw details last, and only where no later fill will cover them.
  - Close every outline so bucket fills don't leak. Extend open ends a few px. Stop the hill line short of the character (the gap around x≈344–590 in the example) so it never cuts through the dress.
- **Custom palette:** one named colour per cell, in the order of `palette` in the JSON. Ship a `.gpl` (`examples/peppa.gpl`) and load it into KolourPaint's colour box. The `ui.palette_origin/cell/cols` values must match where the cells sit on screen.
- **Calibrate the UI** for the resolution: `CALIBRATE=1 scripts/session.sh strokes.json out/` saves `ui_check.png`. Read off `canvas_origin`, the tool button positions (`brush`, `fill`), the brush-size button and the palette cells.
- The cursor stays visible because ffmpeg records with `-draw_mouse 1`. Park it off the canvas at the end (`park_cursor`).

### ⚠️ Cleanup pitfall (critical)
Record your own `Xvfb`, `kolourpaint` and `ffmpeg` PIDs and kill **only those** (`session.sh` uses a trap). **Never** run `pkill Xvfb`, `killall kolourpaint` or anything similar. The shared desktop also runs on Xvfb, and a broad pkill once took it down. Before starting, check that `/tmp/.X11-unix/X<N>` does not exist.

## 3. Recording and post

1. `scripts/session.sh strokes.json out/ 1440 1080 77` starts Xvfb, opens a blank canvas, records `raw.mp4` with x11grab at 30 fps, drives the strokes, and writes `events.json` and `end.png`.
2. Find where app startup ends (the first stroke, about 7 s in) from `events.json` (first `t`) or frames.
3. `scripts/post.sh out/raw.mp4 out/video.mp4 <TRIM> <TARGET> 4 1.75` builds the clip in this order:
   - **Hook (mandatory):** the video opens on the **finished picture** for ~1.5–2 s, then a 0.3 s fade into the **blank canvas**, and the drawing starts.
   - **Drawing:** startup is trimmed and one uniform speed-up fits hook, drawing and hold into the target exactly.
   - **Hold:** the last frame is frozen for ~4 s.
   
   It also writes `video_final.png` and `video_contact.jpg` (4×3), and prints the `--trim/--speed/--offset` values for the SFX script.
4. **Contact-sheet QA** (look at it yourself):
   - The subject is recognizable.
   - Proportions are right (head, body and limbs).
   - No fill leaked (for example, sky into grass, or the hill line through the dress).
   - Details are not covered by later fills.
   - The cursor is visible while drawing.
   
   If anything fails, fix the JSON and re-record.

## 4. Audio

- **SFX** from the drawing events: `scripts/sfx_from_events.py events.json sfx.wav --trim A --speed SP --dur T` makes a pencil scratch per stroke and a soft bloop per fill, timed with `t_video=(t-A)/SP + offset`. Pass `--offset` (hook length minus the crossfade) from the post.sh output.
- **BGM bed:** `scripts/music_bed.py src bed.wav --dur T` drops silences >0.4 s, keeps the busiest 2 s phrases, joins them with 0.25 s crossfades, loops to length, and fades the last 4 s. Use `--start/--end` to cut intros or spoken parts.
- **Mix:** `scripts/mix.sh video.mp4 bed.wav sfx.wav final.mp4 15`.
  - SFX get a 6 kHz lowpass and a de-esser and sit **14–16 dB under** the music. Keep them quiet.
  - Two-pass loudnorm to **−14 LUFS**, plus a limiter, so the AAC file measures **≤ −1.5 dBTP**. Loudnorm alone at TP −1.5 measured −0.8 after encoding.
  - The script then runs ebur128 and `silencedetect` (−45 dB, 0.4 s). Expect 0 gaps before the final fade.

## 5. BGM sourcing

- **User files:** use them as given (`ffmpeg -i file -vn src.wav`).
- **Douyin links:** direct download and yt-dlp return **403** because requests are signed. Instead, open snapany.com (Douyin parser) in the box browser, paste the link, save the mp4, then extract the audio.
- **Speech check:** run whisper on the extracted audio. If it contains speech or voice-over, cut those spans with `--start/--end` or pick another phrase.
- **Fallback:** `scripts/ditty_fallback.py bgm.wav 70` synthesizes an original glockenspiel and ukulele ditty, so there is no copyright issue.
- **Copyright:** branded characters such as Peppa Pig, and their theme music, are for **personal use only**. Never post them publicly to Douyin or elsewhere unless the user explicitly asks. Ingest into the private asset library is the default (§7), but tag the entry with a rights note.

## 6. Douyin covers and publish pack

- **Covers:** `scripts/covers.py out/video_final.png "标题" covers/ --sub "副标题" --crop 69,58,1360,790` makes `cover_4x3.jpg` (1440×1080) and `cover_3x4.jpg` (1080×1440).
  - Each has a large bold title (about 11% of width) with an outline on a yellow pill, over the finished art on a blurred fill.
  - Install a CJK bold font if needed: `fonts-noto-cjk-extra`.
  - Check that the title is readable at thumbnail size.
- **Publish pack:** `scripts/publish_pack.py --video final.mp4 --covers covers/ --title "..." --caption "..." --tags 简笔画 绘画过程 ... --out pack/` checks:
  - title ≤ 30 characters
  - 3–5 hashtags
  - both covers present
  - duration 65–75 s
  
  It copies the video and covers and writes `publish.json` and `checklist.md`, and exits 1 on any failure. The pack is an asset set only. Posting to Douyin itself still needs the user's explicit go-ahead.

## 7. Asset library (white-motion-library, category 绘画过程)

After the gates pass, **ingest without asking** into the white-motion-library project under a new **drawing-process (`绘画过程`)** category. Follow the parent skill's [local library adapter](../references/local-codex-library-adapter.md) (R2 + index + Worker deploy) and the project's AGENTS.md/README:

1. Add the category to the project index or config if it doesn't exist yet. Keep all existing entries and pinned items.
2. Upload the final video, both covers, the contact sheet and `publish.json` to R2 with content-addressed keys: `<分区>/<类型>/<sha256>.<ext>`.
   - Use `wrangler r2 object put <bucket>/<key> --file <f> --remote` for files larger than ~8 MB.
   - Download every object again and verify its SHA-256.
3. Append the work to the index and run the project's tests. Commit and push to a clean main, then deploy.
4. Verify that the new entry plays in the browser and that protected media still returns 401 when logged out.
5. Never put credentials or private URLs in this skill or in receipts.
6. Add a `rights: personal-use (branded character/music)` note to the entry metadata when it applies.

## 8. Delivery checklist

- [ ] The video opens on the finished picture (1.5–2 s), then shows a blank canvas and the drawing.
- [ ] 4:3 and 3:4 covers and the publish pack pass `publish_pack.py`.
- [ ] Library ingest is done (upload, read-back, index, deploy, playback check).
- [ ] Resolution and duration match the request (65–75 s, ~4 s hold at the end).
- [ ] Contact sheet passes QA.
- [ ] −14 LUFS ±1, TP ≤ −1.5 dBTP, no silence gaps.
- [ ] SFX are audible but soft.
- [ ] Viewer-facing content has no tool or process mentions.
- [ ] Deliver the mp4 and the contact sheet. Keep the stroke JSON so you can re-render.

## Files

- `scripts/session.sh` — private Xvfb, KolourPaint, recording and drive. Cleanup kills its own PIDs only.
- `scripts/drive_strokes.py` — xdotool driver for the stroke JSON. Writes `events.json`.
- `scripts/post.sh` — trim, finished-picture hook, uniform speed-up, hold and contact sheet.
- `scripts/covers.py` — 4:3 and 3:4 Douyin covers.
- `scripts/publish_pack.py` — publish pack and checklist.
- `scripts/sfx_from_events.py`, `scripts/music_bed.py`, `scripts/mix.sh`, `scripts/ditty_fallback.py`
- `examples/peppa_strokes.json` and `examples/peppa.gpl` — the Peppa-in-a-meadow example, with the `ui` block for 1440×1080.
