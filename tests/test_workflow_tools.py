"""Real standard-library CLI tests; all input media/report claims are synthetic.

Run with: "$CODEX_PRIMARY_RUNTIME_PYTHON" -m unittest discover -s tests -v
No production library, user files, network, or installed third-party packages.
"""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


class CLITestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def invoke(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=20)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout if expected in (0, 1) else result.stderr)


class AssetManifestTests(CLITestCase):
    def setUp(self):
        super().setUp()
        self.root = self.base / "assets"
        (self.root / "nested").mkdir(parents=True)
        (self.root / "nested" / "sample.bin").write_bytes(b"synthetic\x00asset\xff")
        (self.root / "说明.txt").write_text("Synthetic test fixture only.\n", encoding="utf-8")
        self.manifest = self.base / "manifest.json"

    def create(self, expected=0):
        return self.invoke("asset_manifest.py", "create", "--root", self.root,
                           "--output", self.manifest, expected=expected)

    def verify(self, strict=False, expected=0, root=None):
        args = ["verify", "--root", root or self.root, "--manifest", self.manifest]
        if strict:
            args.append("--strict")
        return self.invoke("asset_manifest.py", *args, expected=expected)

    def edit_manifest(self, change):
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        change(data)
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

    def test_create_and_strict_verify(self):
        result = self.create()
        self.assertEqual(result["file_count"], 2)
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(data["algorithm"], "sha256")
        self.assertEqual(data["files"][0]["path"], "nested/sample.bin")
        self.assertEqual(data["files"][0]["size"], 16)
        self.assertEqual(len(data["files"][0]["sha256"]), 64)
        verified = self.verify(strict=True)
        self.assertEqual(verified["status"], "pass")
        self.assertEqual(verified["matched_files"], 2)

    def test_manifest_is_deterministic_and_root_independent(self):
        self.create()
        readback = self.base / "downloaded-copy"
        shutil.copytree(self.root, readback)
        self.assertEqual(self.verify(root=readback, strict=True)["status"], "pass")
        another = self.base / "another.json"
        self.invoke("asset_manifest.py", "create", "--root", readback, "--output", another)
        self.assertEqual(self.manifest.read_bytes(), another.read_bytes())

    def test_same_size_tamper_is_detected(self):
        self.create()
        path = self.root / "nested" / "sample.bin"
        original = path.read_bytes()
        path.write_bytes(b"X" + original[1:])
        result = self.verify(expected=1)
        self.assertEqual(result["damaged"][0]["path"], "nested/sample.bin")
        self.assertEqual(result["damaged"][0]["expected_size"], result["damaged"][0]["actual_size"])

    def test_missing_file_is_detected(self):
        self.create()
        (self.root / "nested" / "sample.bin").unlink()
        result = self.verify(expected=1)
        self.assertEqual(result["missing"], ["nested/sample.bin"])

    def test_extra_files_reported_and_strictly_rejected(self):
        self.create()
        (self.root / "extra.txt").write_text("fixture", encoding="utf-8")
        self.assertEqual(self.verify()["extra"], ["extra.txt"])
        self.assertEqual(self.verify(strict=True, expected=1)["status"], "fail")

    def test_output_inside_root_is_rejected_before_creation(self):
        self.manifest = self.root / "self.json"
        self.assertIn("outside root", self.create(expected=2)["error"])
        self.assertFalse(self.manifest.exists())

    def test_verification_manifest_inside_root_is_rejected(self):
        self.create()
        inside = self.root / "self.json"
        shutil.copyfile(self.manifest, inside)
        self.manifest = inside
        self.assertIn("outside root", self.verify(expected=2)["error"])

    def test_existing_output_is_not_overwritten(self):
        self.create()
        original = self.manifest.read_bytes()
        self.create(expected=2)
        self.assertEqual(original, self.manifest.read_bytes())

    def test_empty_root_is_supported(self):
        root = self.base / "empty"
        root.mkdir()
        self.invoke("asset_manifest.py", "create", "--root", root, "--output", self.manifest)
        self.assertEqual(self.verify(root=root, strict=True)["expected_files"], 0)

    def test_unsafe_paths_rejected(self):
        self.create()
        original = json.loads(self.manifest.read_text(encoding="utf-8"))
        for bad in ("../escape", "/absolute", "C:/absolute", "nested\\file", "nested/../file",
                    "./file", "nested//file", "nested/", "", "line\nbreak", None):
            with self.subTest(path=bad):
                data = copy.deepcopy(original)
                data["files"][0]["path"] = bad
                self.manifest.write_text(json.dumps(data), encoding="utf-8")
                self.verify(expected=2)

    def test_duplicate_entries_rejected(self):
        self.create()
        self.edit_manifest(lambda data: data["files"].append(copy.deepcopy(data["files"][0])))
        self.assertIn("duplicate manifest entry", self.verify(expected=2)["error"])

    def test_duplicate_json_keys_rejected(self):
        self.manifest.write_text('{"schema_version":1,"schema_version":1,"algorithm":"sha256","files":[]}', encoding="utf-8")
        self.assertIn("duplicate JSON key", self.verify(expected=2)["error"])

    def test_invalid_size_hash_and_schema_rejected(self):
        self.create()
        original = json.loads(self.manifest.read_text(encoding="utf-8"))
        mutations = [lambda d: d.update(schema_version=True),
                     lambda d: d["files"][0].update(size=True),
                     lambda d: d["files"][0].update(size=-1),
                     lambda d: d["files"][0].update(sha256="bad"),
                     lambda d: d["files"][0].update(extra="unexpected")]
        for mutate in mutations:
            data = copy.deepcopy(original)
            mutate(data)
            self.manifest.write_text(json.dumps(data), encoding="utf-8")
            self.verify(expected=2)

    def symlink(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable on this platform")

    def test_file_symlink_rejected_on_create(self):
        self.symlink(self.root / "link", self.root / "说明.txt")
        self.assertIn("symlink", self.create(expected=2)["error"])

    def test_directory_symlink_rejected_on_verify(self):
        self.create()
        self.symlink(self.root / "linked-dir", self.root / "nested", directory=True)
        self.assertIn("symlink", self.verify(expected=2)["error"])

    def test_root_symlink_rejected(self):
        link = self.base / "root-link"
        self.symlink(link, self.root, directory=True)
        self.root = link
        self.assertIn("symlink", self.create(expected=2)["error"])

    def test_manifest_symlink_rejected(self):
        self.create()
        link = self.base / "manifest-link.json"
        self.symlink(link, self.manifest)
        self.manifest = link
        self.assertIn("symlink", self.verify(expected=2)["error"])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unsupported on this platform")
    def test_special_file_rejected_without_blocking(self):
        os.mkfifo(self.root / "pipe")
        self.assertIn("non-regular", self.create(expected=2)["error"])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unsupported on this platform")
    def test_special_manifest_rejected_without_blocking(self):
        os.mkfifo(self.manifest)
        self.assertIn("regular file", self.verify(expected=2)["error"])


class RunReportTests(CLITestCase):
    def setUp(self):
        super().setUp()
        self.path = self.base / "run.json"
        self.invoke("run_report.py", "new", "--run-id", "synthetic-fixture", "--mode", "full-video", "--output", self.path)
        self.blank = json.loads(self.path.read_text(encoding="utf-8"))

    def validate(self, data, expected=0):
        self.path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return self.invoke("run_report.py", "validate", "--input", self.path, expected=expected)

    def executed_fixture(self):
        """Only a schema fixture; these strings never claim real video checks."""
        data = copy.deepcopy(self.blank)
        data["run"].update(status="completed", scope="Synthetic structural validation fixture",
                           synthetic_example=True, notes="Invented evidence references for validator tests only.",
                           started_at=data["run"]["created_at"], finished_at=data["run"]["created_at"])
        data["evolution"].update(status="no_change", note="Synthetic review found no reusable change")
        data["stages"] = data["stages"][:1]
        data["checks"] = data["checks"][:1]
        for item in data["stages"] + data["checks"]:
            item.update(status="pass", evidence=["Synthetic fixture assertion, not a media-quality result"])
        return data

    def evolution_fixture(self):
        data = self.executed_fixture()
        data["run"]["mode"] = "retrospective-improve"
        data["learning_candidates"] = [{"id": "candidate-1", "summary": "Synthetic generalizable change",
                                       "classification": "generalizable", "status": "accepted",
                                       "evidence": ["Synthetic fixture observation"]}]
        evo = data["evolution"]
        evo.update(status="local_applied", candidate_ids=["candidate-1"], minimal_diff="fixture/change.diff")
        for test in evo["tests"].values():
            test.update(status="pass", evidence=["Synthetic test record; no Skill was edited"])
        evo["tests"]["regression"].update(defect_evidence=["Synthetic old-defect check"], normal_path_evidence=["Synthetic normal-path check"])
        evo["writeback"].update(status="local_applied", evidence=["Synthetic writeback record"])
        evo["version"].update(before="fixture-v1", after="fixture-v2", rollback_ref="fixture/rollback.json")
        return data

    def test_new_is_valid_and_does_not_claim_execution(self):
        self.assertEqual(self.validate(self.blank)["run_status"], "not_run")
        self.assertTrue(all(item["status"] == "not_run" and not item["evidence"]
                            for item in self.blank["stages"] + self.blank["checks"]))
        self.assertEqual(self.blank["evolution"]["status"], "not_run")

    def test_six_modes_are_supported(self):
        for mode in ("topic", "planning", "full-video", "asset-pack", "local-library-import", "retrospective-improve"):
            with self.subTest(mode=mode):
                data = copy.deepcopy(self.blank)
                data["run"]["mode"] = mode
                self.validate(data)

    def test_new_never_overwrites(self):
        before = self.path.read_bytes()
        self.invoke("run_report.py", "new", "--run-id", "other", "--mode", "topic", "--output", self.path, expected=2)
        self.assertEqual(before, self.path.read_bytes())

    def test_valid_completed_synthetic_fixture(self):
        data = self.executed_fixture()
        data["issues"] = [{"id": "issue-1", "description": "Synthetic issue", "correction": "Synthetic correction", "feedback": "Synthetic feedback",
                           "affected_stages": ["topic"], "severity": "low", "status": "resolved",
                           "evidence": ["Synthetic corrected fixture"]}]
        data["learning_candidates"] = [{"id": "learning-1", "summary": "Synthetic project preference",
                                       "classification": "project_preference", "status": "proposed",
                                       "evidence": ["Synthetic observation"]}]
        data["artifacts"] = [{"id": "artifact-1", "path": "fixtures/sample.bin", "kind": "fixture",
                              "status": "verified", "evidence": ["Synthetic integrity observation"]}]
        data["permissions"] = [{"id": "permission-1", "action": "Synthetic local action", "target": "fixture",
                                "status": "not_required", "evidence": [], "note": "Only a synthetic report fixture"}]
        self.assertEqual(self.validate(data)["status"], "valid")

    def test_false_pass_without_evidence_rejected(self):
        for category in ("stages", "checks"):
            with self.subTest(category=category):
                data = self.executed_fixture()
                data[category][0]["evidence"] = []
                self.assertIn("evidence", self.validate(data, expected=2)["error"])

    def test_blank_evidence_and_non_string_evidence_rejected(self):
        for evidence in (["   "], [True], "not-an-array"):
            data = self.executed_fixture()
            data["checks"][0]["evidence"] = evidence
            self.validate(data, expected=2)

    def test_not_run_cannot_claim_pass(self):
        data = self.executed_fixture()
        data["run"].update(status="not_run", started_at=None, finished_at=None)
        self.assertIn("not_run", self.validate(data, expected=2)["error"])

    def test_completed_requires_review_even_when_no_change(self):
        data = self.executed_fixture()
        data["evolution"]["status"] = "not_run"
        self.assertIn("evolution review", self.validate(data, expected=2)["error"])
        data["evolution"].update(status="no_change", note="")
        self.validate(data, expected=2)
        data["evolution"]["note"] = "Synthetic review: no reusable change"
        self.validate(data)

    def test_completed_cannot_contain_unrun_or_failed_checks(self):
        for state in ("not_run", "fail", "blocked"):
            data = self.executed_fixture()
            data["checks"][0].update(status=state, note="Synthetic unfinished check")
            self.validate(data, expected=2)

    def test_in_progress_stage_can_have_partial_checks(self):
        data = self.executed_fixture()
        data["run"].update(status="in_progress", finished_at=None)
        data["stages"][0]["status"] = "in_progress"
        extra = copy.deepcopy(data["checks"][0])
        extra.update(id="pending-check", status="not_run", evidence=[])
        data["checks"].append(extra)
        self.validate(data)

    def test_invalid_enums_rejected(self):
        mutations = [lambda d: d["run"].update(mode="invalid-mode"),
                     lambda d: d["run"].update(status="magic-success"),
                     lambda d: d["checks"][0].update(status="skip"),
                     lambda d: d["stages"][0].update(status="done"),
                     lambda d: d["evolution"].update(status="deployed")]
        for mutate in mutations:
            data = copy.deepcopy(self.blank)
            mutate(data)
            self.validate(data, expected=2)

    def test_na_requires_reason(self):
        data = copy.deepcopy(self.blank)
        data["checks"][0]["status"] = "n/a"
        self.validate(data, expected=2)
        data["checks"][0]["note"] = "Outside this synthetic run scope"
        self.validate(data)

    def test_unknown_stage_and_duplicate_ids_rejected(self):
        data = copy.deepcopy(self.blank)
        data["checks"][0]["stage"] = "unknown"
        self.validate(data, expected=2)
        data = copy.deepcopy(self.blank)
        data["checks"].append(copy.deepcopy(data["checks"][0]))
        self.assertIn("duplicate", self.validate(data, expected=2)["error"])

    def test_completed_with_unresolved_high_issue_rejected(self):
        data = self.executed_fixture()
        data["issues"] = [{"id": "critical-issue", "description": "Synthetic unresolved issue", "correction": "Synthetic pending correction", "feedback": "",
                           "affected_stages": ["topic"], "severity": "high", "status": "open", "evidence": []}]
        self.assertIn("unresolved", self.validate(data, expected=2)["error"])

    def test_local_application_and_remote_sync_are_distinct(self):
        data = self.evolution_fixture()
        self.validate(data)
        data["evolution"]["status"] = "remote_synced"
        self.validate(data, expected=2)
        data["evolution"]["remote_sync"].update(status="pass", evidence=["Synthetic remote readback record"])
        self.validate(data)
        data["evolution"]["status"] = "local_applied"
        self.validate(data, expected=2)

    def test_required_tests_cannot_be_failed_unrun_or_waived_when_applied(self):
        for name in ("structure", "regression", "behavior"):
            for state in ("fail", "not_run", "blocked", "n/a"):
                with self.subTest(test=name, status=state):
                    data = self.evolution_fixture()
                    data["evolution"]["tests"][name].update(status=state, evidence=[], note="Synthetic nonpass")
                    self.validate(data, expected=2)

    def test_optional_behavior_may_be_na_with_reason(self):
        data = self.evolution_fixture()
        data["evolution"]["tests"]["behavior"].update(required=False, status="n/a", evidence=[], note="Synthetic structure-only correction; no behavioral logic changed")
        self.validate(data)
        data["evolution"]["tests"]["behavior"]["note"] = ""
        self.validate(data, expected=2)

    def test_structure_and_regression_cannot_be_waived(self):
        for name in ("structure", "regression"):
            data = self.evolution_fixture()
            data["evolution"]["tests"][name].update(required=False, status="n/a", evidence=[], note="Synthetic waiver")
            self.validate(data, expected=2)

    def test_regression_needs_defect_and_normal_path_evidence(self):
        for field in ("defect_evidence", "normal_path_evidence"):
            data = self.evolution_fixture()
            data["evolution"]["tests"]["regression"][field] = []
            self.validate(data, expected=2)

    def test_mode_templates_only_include_relevant_stages(self):
        expected = {"topic": {"topic", "facts"}, "planning": {"topic", "facts", "script", "storyboard"},
                    "local-library-import": {"delivery"}, "retrospective-improve": {"retrospective"}}
        for mode, stages in expected.items():
            destination = self.base / (mode + ".json")
            self.invoke("run_report.py", "new", "--run-id", "fixture", "--mode", mode, "--output", destination)
            data = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual({stage["id"] for stage in data["stages"]}, stages)
            self.validate(data)

    def test_evolution_false_pass_without_evidence_rejected(self):
        data = self.evolution_fixture()
        data["evolution"]["tests"]["behavior"]["evidence"] = []
        self.validate(data, expected=2)

    def test_failed_evolution_must_preserve_previous(self):
        data = self.evolution_fixture()
        evo = data["evolution"]
        evo["status"] = "failed"
        evo["tests"]["behavior"].update(status="fail", evidence=["Synthetic failing test"])
        self.validate(data, expected=2)
        evo["writeback"].update(status="kept_previous", evidence=["Synthetic preserved-version record"])
        evo["version"]["after"] = "fixture-v1"
        self.validate(data)
        evo["version"]["after"] = "fixture-v2"
        self.validate(data, expected=2)

    def test_rollback_requires_restored_version_and_reference(self):
        data = self.evolution_fixture()
        evo = data["evolution"]
        evo["status"] = "rolled_back"
        evo["writeback"].update(status="rolled_back", evidence=["Synthetic restoration record"])
        self.validate(data, expected=2)
        evo["version"]["after"] = "fixture-v1"
        self.validate(data)
        evo["version"]["rollback_ref"] = None
        self.validate(data, expected=2)

    def test_project_preferences_and_temporary_facts_cannot_enter_global_evolution(self):
        for classification in ("project_preference", "temporary_fact", "invalid"):
            data = self.evolution_fixture()
            data["learning_candidates"][0]["classification"] = classification
            self.validate(data, expected=2)

    def test_applied_evolution_requires_minimal_diff_versions_and_accepted_candidate(self):
        mutations = [lambda d: d["evolution"].update(minimal_diff=None),
                     lambda d: d["evolution"]["version"].update(rollback_ref=None),
                     lambda d: d["evolution"]["version"].update(after="fixture-v1"),
                     lambda d: d["learning_candidates"][0].update(status="proposed")]
        for mutate in mutations:
            data = self.evolution_fixture()
            mutate(data)
            self.validate(data, expected=2)

    def test_permissions_and_verified_artifacts_require_evidence(self):
        data = self.executed_fixture()
        data["permissions"] = [{"id": "permission", "action": "synthetic action", "target": "fixture",
                                "status": "approved", "evidence": [], "note": ""}]
        self.validate(data, expected=2)
        data["permissions"] = []
        data["artifacts"] = [{"id": "artifact", "path": "fixture.bin", "kind": "test",
                              "status": "verified", "evidence": []}]
        self.validate(data, expected=2)
        data["artifacts"][0].update(status="planned", path="../outside")
        self.validate(data, expected=2)

    def test_invalid_json_duplicate_keys_and_nonfinite_numbers_rejected(self):
        for raw in ('{', '{"schema_version":1,"schema_version":1}', '{"schema_version":NaN}'):
            self.path.write_text(raw, encoding="utf-8")
            self.invoke("run_report.py", "validate", "--input", self.path, expected=2)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unsupported on this platform")
    def test_special_report_rejected_without_blocking(self):
        fifo = self.base / "report-fifo"
        os.mkfifo(fifo)
        self.assertIn("regular file", self.invoke("run_report.py", "validate", "--input", fifo, expected=2)["error"])

    def test_example_is_explicitly_synthetic_and_unexecuted(self):
        example = SKILL_ROOT / "templates" / "run-report.example.json"
        data = json.loads(example.read_text(encoding="utf-8"))
        self.assertTrue(data["run"]["synthetic_example"])
        self.assertEqual(data["run"]["status"], "not_run")
        self.assertIn("合成", data["run"]["notes"])
        self.invoke("run_report.py", "validate", "--input", example)


if __name__ == "__main__":
    unittest.main()
