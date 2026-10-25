---
name: draw-process-video
description: Produce a "real paint-app drawing process" video — a subject drawn stroke by stroke in a real painting program (KolourPaint) with visible cursor, sped up to ~70 s, with drawing SFX and a dense BGM bed. Use when asked to make a drawing/painting-process clip of a character or scene. Not for 3D explainers (use the parent skill).
version: 0.6.0
---

# Draw-Process Video (real paint app)

A real painting app is driven by synthetic mouse input on a private virtual display and screen-recorded. The result looks like a person drawing: line art, then bucket fills, then background, then details.

## 1. Inputs (ask only for what is missing)

| Input | Default |
|---|---|
| Subject | required. Character or scene. |
| Aspect / resolution | 4:3 **1440×1080**. Also supports 9:16 1080×1920 (recalibrate the `ui` block). |
| Target duration | **65–75 s** (70 s typical), including a ~4 s final hold |
| BGM source | chosen autonomously from the candidate pool (§5), a file/link the user supplies, or the original synthesized ditty (fallback) |

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
- **Big, obvious cursor (required).** `session.sh` sets `XCURSOR_THEME=DMZ-White XCURSOR_SIZE=64` (install `dmz-cursor-theme x11-xserver-utils`) and records with `-draw_mouse 1`, but KolourPaint's pen/brush cursor stays a tiny crosshair regardless. So `session.sh` also logs the pointer (`mouse.log`, ~50 Hz, plus `t0.txt`), and you burn in a marker before post: `scripts/cursor_overlay.py raw.mp4 mouse.log t0.txt raw_cur.mp4` (coral circle r=24 with white ring and a nib dot), then run `post.sh` on `raw_cur.mp4`. Check 3 mid-drawing frames that the marker is clearly visible. Park the cursor off the canvas at the end (`park_cursor`).
- **Palette load is automated:** `session.sh` opens Colors → Open… and types the `.gpl` path (`GPL=` env, default `peppa.gpl` next to the JSON). With no window manager, it clicks the filename field first to focus it, otherwise the keystrokes land on the canvas as tool shortcuts.
- **Seed check before recording:** simulate the JSON with PIL (9 px lines, bucket fills) and nudge each seed to a spot with ≥3 px of white around it; a seed that lands on an outline recolours the whole outline. `examples/peppa_puddle_gen.py` does this (and reuses the Peppa geometry, scaled, for Peppa + George). Tiny closed shapes (shoes at small scale) are drawn as concentric ellipses instead of filled.
- When re-checking `end.png` or frames after a re-take, copy them to a **new filename** first: an image viewer can show a cached older render of the same path.
- In the PIL seed-check preview, cap every stroke end with a round dot (r=4.5): PIL lines have butt ends, so a ground line clamped to x=2 leaves a 2 px white column at the canvas edge and the grass fill leaks into the sky in the preview only (KolourPaint's round brush closes it).
- Strokes are clamped 2 px inside the canvas after the wobble: a stroke starting at x=0 was lost off-canvas once, the hill line vanished and the sky fill flooded the grass.

### ⚠️ Cleanup pitfall (critical)
Record your own `Xvfb`, `kolourpaint` and `ffmpeg` PIDs and kill **only those** (`session.sh` uses a trap). **Never** run `pkill Xvfb`, `killall kolourpaint` or anything similar. The shared desktop also runs on Xvfb, and a broad pkill once took it down. Before starting, check that `/tmp/.X11-unix/X<N>` does not exist.

## 3. Recording and post

1. `scripts/session.sh strokes.json out/ 1440 1080 77` starts Xvfb, opens a blank canvas, records `raw.mp4` with x11grab at **native 60 fps** (`-framerate 60`, ultrafast crf 14; pointer logged every ~8 ms), drives the strokes, and writes `events.json` and `end.png`. `cursor_overlay.py` and `post.sh` keep 60 fps end to end; the speed-up only drops captured frames (no interpolation). Verify `ffprobe` r_frame_rate = avg_frame_rate = 60/1, 1440×1080, `pix_fmt=yuv420p` (post.sh forces it; without `-pix_fmt` the xfade output came out yuv444p / High 4:4:4, which many players reject).
2. Find where app startup ends (the first stroke, about 7 s in) from `events.json` (first `t`) or frames.
3. `TRANS=wipeleft scripts/post.sh out/raw_cur.mp4 out/video.mp4 <TRIM> <TARGET> 4 1.75` builds the clip in this order:
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
- **BGM bed:** `scripts/music_bed.py src bed.wav --dur T [--start auto|SEC]` takes ONE contiguous excerpt (default start = first note onset; pick a phrase start), 1.5 s fade-in, 4 s fade-out. If the track is shorter than T it loops the whole piece at a bar line with a 0.3 s crossfade.
- **No chop-and-stitch (hard rule, for tracks we source ourselves):** BGM must be one coherent continuous performance. Never cut silences or stitch fragments together; the old silence-chop bed made an analysis video sound messy (乱). Short musical rests inside the performance are fine; the mix's silencedetect still reads 0 gaps because the drawing SFX bridge them.
- **Mix:** `scripts/mix.sh video.mp4 bed.wav sfx.wav final.mp4 15`.
  - SFX get a 6 kHz lowpass and a de-esser and sit **14–16 dB under** the music. Keep them quiet.
  - Two-pass loudnorm to **−14 LUFS**, plus a limiter, so the AAC file measures **≤ −1.5 dBTP**. Loudnorm alone at TP −1.5 measured −0.8 after encoding.
  - The script then runs ebur128 and `silencedetect` (−45 dB, 0.4 s). Expect 0 gaps before the final fade.

## 5. BGM sourcing

- **User files:** use them as given (`ffmpeg -i file -vn src.wav`).
- **Douyin links:** direct download and yt-dlp return **403** because requests are signed. Instead, open snapany.com (Douyin parser) in the box browser, paste the link, save the mp4, then extract the audio.
- **User-supplied tracks are accepted as-is (user override, 2026-10-23):** do not screen them for gaps, splicing, background sounds or talking, and never reject or delete them. Stitching segments of a user-supplied track is OK (crossfade the joins). Still run the loudness/TP targets of the mix.
- **Candidate pool screening (hard rule, only for tracks we find ourselves):** every self-sourced BGM candidate must be a clean continuous performance. Discard analysis/tutorial, talking and medley videos. Screen each with whisper (trust only segments with low `no_speech_prob` (≈0.0–0.2) that repeat across `language=zh` and `en`; "作曲 李宗盛" / "Thanks for watching!" with high no_speech_prob are hallucinations on music), plus per-5 s key/tempo and an energy-gap scan. Delete failed candidates from the pool. Also md5sum the pool: duplicates under another name share the verdict.
- **Fixed pool (hard rule):** the ONLY allowed BGM tracks are `/workspace/uploads/peppa_user_b.mp4` (user-supplied, 小朱佩奇 看动画学英语, 312 s: the cartoon episode; use its music sections, stitching allowed, see below) and `/workspace/uploads/peppa_user_c.mp4` (user-supplied, 矢量漫步 Excel画小猪佩奇·摇铃铛, 124 s; an edited medley, use as-is). Pick between them by the rotation rule; do not ask. **Banned:** `peppa_clean_1.mp4` (Mr.Chen four-hands) — the user says it is not Peppa Pig music; never use it again (the file stays on disk, do not use it). Also never use `peppa_bgm*.mp4`, `peppa_clean_2.mp4` or `douyin_peppa.mp4`. **No self-found tracks without approval:** do not add any track you find yourself to the pool unless the user explicitly approves it; the screening rule above applies only after approval. Spectrogram tip: a voice shows as wavy harmonic glides, plucked/piano music as vertical onsets with flat partials.
- **`peppa_user_b.mp4` sections (user-supplied):** the audio has no detectable speech (whisper zh/en returns only hallucinations); music sections are the opening theme 1.1–15.9 s, a cue 42.9–68.8 s and the end-credits theme 286.05–301.1 s; between them are quiet ambience/engine stretches. `examples/peppa_birthday_bed_user_b.py` splices opening → cue → credits → opening again with 0.3 s equal-power crossfades into a 70 s bed.
- **Rotation rule:** alternate strictly between `peppa_user_b.mp4` and `peppa_user_c.mp4` so no two consecutive works use the same track. Check the previous work's track in the library entry or its run notes; for user_c, avoid overlapping its previous excerpt range where possible. Usage so far: drawing-peppa-pig and -2 used `peppa_clean_1.mp4` (now banned); drawing-peppa-pig-3 `peppa_user_c.mp4` 0.15–70.15 s (vocal tag after ~110 s avoided); drawing-peppa-pig-4 `peppa_user_b.mp4` (spliced 1.1–15.9 + 42.9–68.8 + 286.05–301.1 + 1.1–16.25 s); drawing-peppa-pig-5 `peppa_clean_1.mp4` 123.0–193.0 s (banned track, used before the ban). **Next: `peppa_user_c.mp4`**, then user_b, then user_c, and so on.
- **Speech check (self-sourced tracks only):** run whisper on the extracted audio. If it contains speech or voice-over, cut those spans with `--start/--end` or pick another phrase.
- **Fallback:** `scripts/ditty_fallback.py bgm.wav 70` synthesizes an original glockenspiel and ukulele ditty, so there is no copyright issue.
- **Copyright:** branded characters such as Peppa Pig, and their theme music, are for **personal use only**. Never post them publicly to Douyin or elsewhere unless the user explicitly asks. Ingest into the private asset library is the default (§7).

## 6. Douyin covers and publish pack

- **Covers:** `scripts/covers.py out/video_final.png "标题" covers/ --sub "副标题" --crop 69,58,1360,790` makes `cover_4x3.jpg` (1440×1080) and `cover_3x4.jpg` (1080×1440).
  - Each has a large bold title (about 11% of width) with an outline on a yellow pill; the finished art is fitted between the title and subtitle bands (never under the title) on a blurred fill.
  - Install a CJK bold font if needed: `fonts-noto-cjk-extra`.
  - Check that the title is readable at thumbnail size.
- **Publish pack:** `scripts/publish_pack.py --video final.mp4 --covers covers/ --title "..." --caption "..." --tags 简笔画 绘画过程 ... --out pack/` checks:
  - title ≤ 30 characters
  - 3–5 hashtags
  - both covers present
  - duration 65–75 s
  
  It copies the video and covers and writes `publish.json` and `checklist.md`, and exits 1 on any failure. The box has no `zip` binary: build the creator ZIP with Python `zipfile`. The pack is an asset set only. Posting to Douyin itself still needs the user's explicit go-ahead.

## 7. Asset library (white-motion-library, top-level section 绘画过程 at `/drawing`)

After the gates pass, **ingest without asking** into the white-motion-library project's **绘画过程** section: a top-level section at `/drawing`, a peer of 舞蹈资产 (`/`) and 科普视频 (`/science`), with its own nav entry. Since 2026-10-25 drawing works no longer appear on the science page. Add the entry to `工具/发布素材库/R2作品.json` with `"category": "绘画过程"` (id `drawing-<subject>-N`). The build (`python3 工具/白膜云端库/管理.py 构建`, or `工具.发布素材库.管理.build()`) routes it automatically into `绘画过程库.html` / `drawingPage` / `drawingIds`, and `npm run check:r2` fails if a drawing work shows up on `/science`. The library URL for a new work is `https://white-motion-library.video-maker.workers.dev/drawing`. Follow the parent skill's [local library adapter](../references/local-codex-library-adapter.md) (R2 + index + Worker deploy) and the project's AGENTS.md/README:

1. The `/drawing` section already exists; do not add drawing works to the science catalog. Keep all existing entries and pinned items.
2. Upload the final video, both covers, the contact sheet and `publish.json` to R2 with content-addressed keys: `<分区>/<类型>/<sha256>.<ext>`.
   - Use `wrangler r2 object put <bucket>/<key> --file <f> --remote` for files larger than ~8 MB.
   - On the box run `npm ci` in the library repo first and call `./node_modules/.bin/wrangler` (Node ≥22, e.g. `~/.local/node22/bin`); `npx wrangler` from there hits EACCES on the root-owned `/node_modules/.cache`.
   - Download every object again and verify its SHA-256.
3. Append the work to the index and run the project's tests. Commit and push to a clean main, then deploy.
4. **Deploy safety gate (hard rule, before any deploy):** the user also deploys dance updates from another machine, so the last version you remember is often stale; always take the **latest** deployment from `wrangler deployments list --config 工具/白膜云端库/部署配置.jsonc` as the baseline (and `git pull` right before committing). Find the previously deployed commit (`wrangler deployments list`; match the latest deploy time/message to `git log`), then compare against it the work count and the byte size of `工具/白膜云端库/公开目录.json` and `云端登记.json` after your build. Your change should only add (a drawing ingest leaves both at the same dance-work count, only the `updated` stamp changes; the drawing count in `drawingIds` goes up by one). If either the count or the size shrinks by more than your own change, **STOP, do not deploy, and report**. Dance works must remain present, and `science-chirality` must stay first in `workIds`.
5. Verify that the new entry plays in the browser and that protected media still returns 401 when logged out. The authenticated check (`管理.py 验证部署`) needs the local `工具/白膜云端库/.访问密码.txt`, which is not on the box; there, verify the R2 read-back decodes end to end (`ffmpeg -v error -i file -f null -`) and report that logged-in playback is left to the user.
6. Never put credentials or private URLs in this skill or in receipts.

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
- `scripts/cursor_overlay.py` — big coral pen marker synced to `mouse.log`.
- `scripts/post.sh` — trim, finished-picture hook, uniform speed-up, hold and contact sheet.
- `scripts/covers.py` — 4:3 and 3:4 Douyin covers.
- `scripts/publish_pack.py` — publish pack and checklist.
- `scripts/sfx_from_events.py`, `scripts/music_bed.py`, `scripts/mix.sh`, `scripts/ditty_fallback.py`
- `examples/peppa_strokes.json` and `examples/peppa.gpl` — the Peppa-in-a-meadow example, with the `ui` block for 1440×1080.
- `examples/peppa_puddle_strokes.json`, `examples/peppa2.gpl`, `examples/peppa_puddle_gen.py` — Peppa and George jumping by a muddy puddle, house on the hill (run with `GPL=examples/peppa2.gpl`).
- `examples/peppa_birthday_strokes.json`, `examples/peppa4.gpl`, `examples/peppa_birthday_gen.py` — birthday party indoors: Peppa holding three balloons, a two-tier cake with three candles on a table, gift box, bunting and confetti; wall/floor line stops at the dress (run with `GPL=examples/peppa4.gpl`; 20 colours still fit the 11×2 colour box). `examples/peppa_birthday_bed_user_b.py` builds its BGM bed.
- `examples/peppa_stars_strokes.json`, `examples/peppa5.gpl`, `examples/peppa_stars_gen.py` — stargazing at night: Peppa on a hill beside a blue telescope on a tripod, full moon with craters, yellow stars, twinkles and flowers; the tripod legs split the grass/sky, so each pocket gets its own seed (run with `GPL=examples/peppa5.gpl`).
- `examples/peppa_rain_strokes.json`, `examples/peppa3.gpl`, `examples/peppa_rain_gen.py` — rainy day: Peppa holding a yellow/orange umbrella (shaft angled clear of the snout to her raised hand), clouds, rain only outside the umbrella, snail and flowers (run with `GPL=examples/peppa3.gpl`).
