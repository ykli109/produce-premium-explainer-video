#!/usr/bin/env python3
"""Measure a rendered video against references/douyin-quality-standard.md.

Uses only the Python standard library plus local ffmpeg/ffprobe. It measures
technical proxies (format, cuts, motion, saturation, loudness, silence gaps);
it cannot judge hook wording, beauty, facts or subtitle legibility, which are
listed as manual items and never reported as passed.

Exit codes: 0 all hard items pass; 1 at least one hard item fails;
2 usage/input/tool error.
"""

import argparse
import csv
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

STANDARD = {
    "width": 1080, "height": 1920, "fps": 30.0, "fps_tol": 0.05,
    "shot_max_s": 5.0, "shot_avg_max_s": 3.5, "shots_per_60s_min": 20,
    "first_second_motion_min": 1.5, "first_frame_luma_min": 20.0,
    "motion_mean_min": 3.0, "saturation_mean_min": 28.0, "contrast_min": 120.0,
    "lufs_target": -14.0, "lufs_tol": 1.0, "true_peak_max": -1.0,
    "silence_lufs": -50.0, "silence_fraction_max": 0.05, "floor_gap_max_lu": 20.0,
    "scdet_threshold": 8.0, "analysis_width": 360,
}

MANUAL_ITEMS = [
    "hook_title_and_question_within_3s", "subtitle_bold_64px_stroke_safe_area_keyword_highlight",
    "no_small_unreadable_info_bars", "lighting_key_fill_rim_dof_hdri", "per_section_palette_shift",
    "scene_reuse_max_6s_without_new_angle", "sfx_on_cuts_and_text_pops", "ending_save_or_comment_trigger",
    "cover_big_text", "title_formula", "series_ip_and_source_citation", "bgm_sfx_license_recorded",
]


class ToolError(Exception):
    pass


def run(cmd):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise ToolError(f"missing tool: {cmd[0]}") from exc
    if proc.returncode != 0:
        raise ToolError(f"{cmd[0]} failed: {proc.stderr.strip()[-400:]}")
    return proc


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout
    data = json.loads(out)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if video is None:
        raise ToolError("no video stream")
    num, _, den = video.get("avg_frame_rate", "0/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0.0
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0)
    return {"width": int(video["width"]), "height": int(video["height"]), "fps": round(fps, 3),
            "duration_s": round(duration, 3), "audio_streams": len(audio)}


def parse_metadata(path):
    frames, cur = [], None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("frame:"):
            m = re.search(r"pts_time:([-\d.e]+)", line)
            cur = {"t": float(m.group(1)) if m else 0.0}
            frames.append(cur)
        elif "=" in line and cur is not None:
            key, _, value = line.partition("=")
            try:
                cur[key.strip()] = float(value)
            except ValueError:
                pass
    return frames


def video_stats(path, tmp):
    width = STANDARD["analysis_width"]
    stats_file, cut_file = Path(tmp) / "stats.txt", Path(tmp) / "cuts.txt"
    graph = (f"[0:v]scale={width}:-2,split[a][b];"
             f"[a]signalstats,metadata=mode=print:file={stats_file}[s];"
             f"[b]scdet=threshold={STANDARD['scdet_threshold']},"
             f"metadata=mode=print:key=lavfi.scd.time:file={cut_file}[c]")
    run(["ffmpeg", "-hide_banner", "-nostats", "-v", "error", "-i", str(path), "-filter_complex", graph,
         "-map", "[s]", "-f", "null", "-", "-map", "[c]", "-f", "null", "-"])
    frames = parse_metadata(stats_file)
    cuts = sorted({f["t"] for f in parse_metadata(cut_file) if f["t"] > 0}) if cut_file.exists() else []
    if not frames:
        raise ToolError("no video frames analysed")
    ydif = [f.get("lavfi.signalstats.YDIF", 0.0) for f in frames[1:]] or [0.0]
    first = [f.get("lavfi.signalstats.YDIF", 0.0) for f in frames[1:] if f["t"] <= 1.0] or [0.0]
    return {
        "frames_analysed": len(frames),
        "first_frame_luma": round(frames[0].get("lavfi.signalstats.YAVG", 0.0), 2),
        "first_second_motion": round(statistics.mean(first), 3),
        "motion_mean_ydif": round(statistics.mean(ydif), 3),
        "saturation_mean": round(statistics.mean(f.get("lavfi.signalstats.SATAVG", 0.0) for f in frames), 3),
        "contrast_mean": round(statistics.mean(f.get("lavfi.signalstats.YHIGH", 0.0) - f.get("lavfi.signalstats.YLOW", 0.0)
                                               for f in frames), 3),
        "cuts": [round(c, 3) for c in cuts],
    }


def shot_metrics(boundaries, duration):
    edges = [0.0] + [b for b in boundaries if 0 < b < duration] + [duration]
    lengths = [round(b - a, 3) for a, b in zip(edges, edges[1:]) if b - a > 0.05]
    if not lengths:
        lengths = [duration]
    return {"shot_count": len(lengths), "avg_shot_s": round(statistics.mean(lengths), 3),
            "max_shot_s": round(max(lengths), 3),
            "shots_per_60s": round(len(lengths) * 60.0 / duration, 2) if duration else 0.0}


def storyboard_bounds(path):
    starts, ends = [], []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            s = row.get("画面开始秒") or row.get("start") or ""
            e = row.get("画面结束秒") or row.get("end") or ""
            try:
                starts.append(float(s)); ends.append(float(e))
            except ValueError:
                continue
    if not starts:
        raise ToolError("storyboard has no numeric 画面开始秒/画面结束秒 (or start/end) rows")
    return sorted(set(starts[1:] if min(starts) == 0 else starts)), max(ends)


def audio_stats(path):
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true",
                "-f", "null", "-"])
    err = proc.stderr
    momentary = [float(m) for m in re.findall(r"\bM:\s*(-?[\d.]+)", err)]
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else ""
    i_match = re.search(r"I:\s*(-?[\d.]+) LUFS", summary)
    p_match = re.search(r"True peak:\s*Peak:\s*(-?[\d.inf]+)", summary, re.S)
    if not i_match:
        raise ToolError("could not parse integrated loudness")
    integrated = float(i_match.group(1))
    peak = float(p_match.group(1)) if p_match else None
    inner = momentary[5:-5] if len(momentary) > 20 else momentary
    silent = sum(1 for m in inner if m < STANDARD["silence_lufs"]) / len(inner) if inner else 1.0
    active = sorted(m for m in inner if m > -70)
    floor = active[len(active) // 10] if active else -120.0
    return {"integrated_lufs": integrated, "true_peak_dbtp": peak,
            "silent_window_fraction": round(silent, 4), "floor_p10_lufs": round(floor, 2),
            "floor_gap_lu": round(integrated - floor, 2)}


def item(name, hard, value, target, ok):
    return {"item": name, "hard": hard, "value": value, "target": target, "status": "pass" if ok else "fail"}


def evaluate(path, storyboard=None, bgm_stem=None):
    s = STANDARD
    info = probe(path)
    with tempfile.TemporaryDirectory() as tmp:
        vs = video_stats(path, tmp)
    shots = shot_metrics(vs["cuts"], info["duration_s"])
    items = [
        item("resolution", True, f"{info['width']}x{info['height']}", f"{s['width']}x{s['height']}",
             (info["width"], info["height"]) == (s["width"], s["height"])),
        item("fps", True, info["fps"], s["fps"], abs(info["fps"] - s["fps"]) <= s["fps_tol"]),
        item("first_frame_not_black", True, vs["first_frame_luma"], f">={s['first_frame_luma_min']} YAVG",
             vs["first_frame_luma"] >= s["first_frame_luma_min"]),
        item("first_second_motion", True, vs["first_second_motion"], f">={s['first_second_motion_min']} YDIF",
             vs["first_second_motion"] >= s["first_second_motion_min"]),
        item("detected_shots_per_60s", True, shots["shots_per_60s"], f">={s['shots_per_60s_min']}",
             shots["shots_per_60s"] >= s["shots_per_60s_min"]),
        item("detected_avg_shot_s", True, shots["avg_shot_s"], f"<={s['shot_avg_max_s']}",
             shots["avg_shot_s"] <= s["shot_avg_max_s"]),
        item("detected_max_shot_s", True, shots["max_shot_s"], f"<={s['shot_max_s']} (justified exceptions in storyboard)",
             shots["max_shot_s"] <= s["shot_max_s"]),
        item("motion_mean", True, vs["motion_mean_ydif"], f">={s['motion_mean_min']} YDIF", vs["motion_mean_ydif"] >= s["motion_mean_min"]),
        item("saturation_mean", True, vs["saturation_mean"], f">={s['saturation_mean_min']} SATAVG",
             vs["saturation_mean"] >= s["saturation_mean_min"]),
        item("contrast_mean", False, vs["contrast_mean"], f">={s['contrast_min']} YHIGH-YLOW", vs["contrast_mean"] >= s["contrast_min"]),
    ]
    result = {"file": Path(path).name, "probe": info, "video": vs, "shots_detected": shots}
    if storyboard:
        bounds, end = storyboard_bounds(storyboard)
        sb = shot_metrics(bounds, max(end, 0.1))
        result["shots_storyboard"] = sb
        items += [
            item("storyboard_shots_per_60s", True, sb["shots_per_60s"], f">={s['shots_per_60s_min']}", sb["shots_per_60s"] >= s["shots_per_60s_min"]),
            item("storyboard_max_shot_s", True, sb["max_shot_s"], f"<={s['shot_max_s']}", sb["max_shot_s"] <= s["shot_max_s"]),
        ]
    if info["audio_streams"] == 0:
        items.append(item("audio_present", True, 0, ">=1 stream", False))
    else:
        au = audio_stats(path)
        result["audio"] = au
        items += [
            item("integrated_loudness", True, au["integrated_lufs"], f"{s['lufs_target']}±{s['lufs_tol']} LUFS",
                 abs(au["integrated_lufs"] - s["lufs_target"]) <= s["lufs_tol"]),
            item("true_peak", True, au["true_peak_dbtp"], f"<={s['true_peak_max']} dBTP",
                 au["true_peak_dbtp"] is not None and au["true_peak_dbtp"] <= s["true_peak_max"]),
        ]
        continuous = (au["silent_window_fraction"] <= s["silence_fraction_max"]
                      and au["floor_gap_lu"] <= s["floor_gap_max_lu"])
        bed = item("continuous_audio_bed_heuristic", True,
                   {"silent_window_fraction": au["silent_window_fraction"], "floor_gap_lu": au["floor_gap_lu"]},
                   f"silent<={s['silence_fraction_max']} and gap<={s['floor_gap_max_lu']} LU", continuous)
        bed["note"] = "heuristic: speech pauses without a music bed look voice-only; does not identify music"
        items.append(bed)
        if bgm_stem:
            stem = audio_stats(bgm_stem)
            items.append(item("bgm_stem_present", True, stem["integrated_lufs"], "> -60 LUFS",
                              stem["integrated_lufs"] > -60))
    items += [{"item": m, "hard": True, "status": "manual_required"} for m in MANUAL_ITEMS]
    hard_fail = [i["item"] for i in items if i["hard"] and i["status"] == "fail"]
    result.update({"standard": "douyin-quality-standard v1", "items": items, "hard_failures": hard_fail,
                   "manual_pending": MANUAL_ITEMS, "automatic_hard_pass": not hard_fail,
                   "delivery_allowed": False if hard_fail else "only_after_manual_items_reviewed"})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("video")
    parser.add_argument("--storyboard", help="storyboard.csv with 画面开始秒/画面结束秒")
    parser.add_argument("--bgm-stem", help="separate BGM stem audio file, if available")
    parser.add_argument("--output", help="write JSON report here (refuses to overwrite)")
    args = parser.parse_args(argv)
    for p in (args.video, args.storyboard, args.bgm_stem):
        if p and not Path(p).is_file():
            print(f"error: not a file: {p}", file=sys.stderr); return 2
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("error: ffmpeg/ffprobe not found", file=sys.stderr); return 2
    try:
        result = evaluate(args.video, args.storyboard, args.bgm_stem)
    except (ToolError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        out = Path(args.output)
        if out.exists():
            print(f"error: output exists: {out}", file=sys.stderr); return 2
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if result["hard_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
