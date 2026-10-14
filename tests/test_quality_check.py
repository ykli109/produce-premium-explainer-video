"""quality_check.py tests on synthetic ffmpeg lavfi media (skipped without ffmpeg)."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "quality_check.py"
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], check=True, timeout=120)


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg/ffprobe not available")
class QualityCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.bad = base / "bad.mp4"
        # Slow, dull, 24fps, single static shot, quiet voice-like audio with gaps.
        ffmpeg("-f", "lavfi", "-i", "color=c=0x103040:s=1080x1920:r=24:d=8",
               "-f", "lavfi", "-i", "sine=f=220:d=8,volume='if(lt(mod(t,2),1),1,0)':eval=frame,volume=-20dB",
               "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(cls.bad))
        cls.good = base / "good.mp4"
        # 30fps 1080x1920, a hard cut every 2s between moving saturated sources, continuous bed at ~-14 LUFS.
        parts = []
        for i, src in enumerate(["testsrc2", "rgbtestsrc", "testsrc2", "rgbtestsrc"]):
            p = base / f"p{i}.mp4"
            hue = f",hue=h={i*90}" if src == "testsrc2" else ",hue=h=" + str(i * 40)
            ffmpeg("-f", "lavfi", "-i", f"{src}=s=1080x1920:r=30:d=2{hue},eq=saturation=2,scroll=h=0.004:v=0.006",
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", str(p))
            parts.append(p)
        lst = base / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        cat = base / "cat.mp4"
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat))
        ffmpeg("-i", str(cat), "-f", "lavfi", "-i", "anoisesrc=d=8:c=pink:a=0.3",
               "-af", "loudnorm=I=-14:TP=-2:LRA=7,aresample=48000", "-shortest",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(cls.good))
        cls.sb = base / "storyboard.csv"
        cls.sb.write_text("shot_id,画面开始秒,画面结束秒\n1,0,2\n2,2,4\n3,4,6\n4,6,8\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_check(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
                              text=True, encoding="utf-8", timeout=120)
        return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr

    def status(self, report, name):
        return next(i["status"] for i in report["items"] if i["item"] == name)

    def test_bad_video_fails_hard_items(self):
        code, report, _ = self.run_check(self.bad)
        self.assertEqual(code, 1)
        for name in ("fps", "detected_max_shot_s", "motion_mean", "saturation_mean",
                     "integrated_loudness", "continuous_audio_bed_heuristic", "first_second_motion"):
            self.assertEqual(self.status(report, name), "fail", name)
        self.assertFalse(report["delivery_allowed"])

    def test_good_video_passes_automatic_items_but_manual_pending(self):
        code, report, err = self.run_check(self.good, "--storyboard", self.sb)
        self.assertEqual(code, 0, (report and report["hard_failures"], err))
        self.assertGreaterEqual(report["shots_detected"]["shot_count"], 4)
        self.assertEqual(report["shots_storyboard"]["max_shot_s"], 2.0)
        self.assertEqual(report["delivery_allowed"], "only_after_manual_items_reviewed")
        self.assertTrue(all(i["status"] == "manual_required" for i in report["items"]
                            if i["item"] in report["manual_pending"]))

    def test_long_storyboard_shot_fails(self):
        sb = Path(self.tmp.name) / "long.csv"
        sb.write_text("shot_id,画面开始秒,画面结束秒\n1,0,7\n2,7,8\n", encoding="utf-8")
        code, report, _ = self.run_check(self.good, "--storyboard", sb)
        self.assertEqual(code, 1)
        self.assertEqual(self.status(report, "storyboard_max_shot_s"), "fail")

    def test_usage_errors(self):
        code, _, _ = self.run_check(Path(self.tmp.name) / "missing.mp4")
        self.assertEqual(code, 2)
        out = Path(self.tmp.name) / "exists.json"
        out.write_text("{}")
        code, _, err = self.run_check(self.bad, "--output", out)
        self.assertEqual(code, 2)
        self.assertIn("exists", err)


if __name__ == "__main__":
    unittest.main()
