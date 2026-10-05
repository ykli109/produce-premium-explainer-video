#!/usr/bin/env python3
"""Generate and structurally validate a local workflow report (standard library).

Evidence is a nonempty reference or observation supplied by the operator. This
validator checks structure and internal consistency, not the truth of evidence,
media aesthetics, legal permission, external uploads, or whether tests ran.
It never edits a Skill, executes checks, installs software, or contacts a network.
Exit codes: 0 valid/created, 2 invalid input or filesystem error.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import stat
import sys


CHECK_STATUSES = {"pass", "fail", "not_run", "blocked", "n/a"}
MODES = {"topic", "planning", "full-video", "asset-pack", "local-library-import", "retrospective-improve"}
RUN_STATUSES = {"not_run", "in_progress", "completed", "blocked", "failed"}
CLASSIFICATIONS = {"project_preference", "generalizable", "temporary_fact"}
EVOLUTION_STATUSES = {"not_run", "no_change", "candidate", "diff_ready", "testing", "local_applied", "remote_synced", "failed", "rolled_back", "blocked"}
STAGES = [("topic", "选题"), ("facts", "事实核查"), ("script", "脚本与标题"),
          ("storyboard", "视觉方向与连续分镜"), ("voice", "配音"), ("sample", "有声核心样片"),
          ("production", "全片制作"), ("review", "成片验收"), ("packaging", "封面与发布素材"),
          ("delivery", "交付入库与发布交接")]
CHECKS = [("topic_value", "topic", "问题、受众与长期知识价值"),
          ("fact_sources", "facts", "事实、来源、日期与适用条件"),
          ("script_logic", "script", "开头承诺、口语可懂性与因果连续"),
          ("visual_continuity", "storyboard", "对象状态、空间与镜头连续"),
          ("voice_consistency", "voice", "声音参考、错读、接缝与一致性"),
          ("audible_sample", "sample", "真实可播放的有声核心段"),
          ("full_timeline", "production", "全片时序、同步与连续动作"),
          ("technical_validation", "review", "技术检测；记录命令、范围与结果"),
          ("actual_watch_listen", "review", "实际看听；记录人、文件版本与范围"),
          ("publication_assets", "packaging", "标题、封面、简介与实际内容匹配"),
          ("local_manifest", "delivery", "本地素材清单与哈希验证"),
          ("upload_readback", "delivery", "上传后下载回读与原始清单验证"),
          ("delivery_access", "delivery", "目标收件人的实际访问与播放")]


class ReportError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReportError(message)


def obj(value, keys, where):
    require(isinstance(value, dict), where + " must be an object")
    require(set(value) == set(keys.split()), where + " requires exactly: " + keys)
    return value


def string(value, where, empty=False, nullable=False):
    if nullable and value is None:
        return
    require(isinstance(value, str), where + " must be a string")
    require(empty or bool(value.strip()), where + " must not be blank")


def enum(value, allowed, where):
    require(isinstance(value, str) and value in allowed,
            where + " must be one of: " + ", ".join(sorted(allowed)))


def strings(value, where, nonempty=False):
    require(isinstance(value, list), where + " must be an array")
    require(not nonempty or bool(value), where + " must contain evidence or a reference")
    for index, item in enumerate(value):
        string(item, where + "[" + str(index) + "]")
    require(len(value) == len(set(value)), where + " must not contain duplicates")


def identifier(value, where):
    string(value, where)
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value) is not None,
            where + " must be a portable 1-128 character identifier")


def records(value, where, fields):
    require(isinstance(value, list), where + " must be an array")
    result = {}
    for index, item in enumerate(value):
        loc = where + "[" + str(index) + "]"
        obj(item, fields, loc)
        identifier(item["id"], loc + ".id")
        require(item["id"] not in result, "duplicate " + where + " id: " + item["id"])
        result[item["id"]] = item
    return result


def result(value, where, fields="status evidence note", statuses=CHECK_STATUSES):
    obj(value, fields, where)
    enum(value["status"], statuses, where + ".status")
    strings(value["evidence"], where + ".evidence", nonempty=value["status"] == "pass")
    string(value["note"], where + ".note", empty=value["status"] not in {"blocked", "n/a"})


def timestamp(value, where, nullable=False):
    if nullable and value is None:
        return None
    string(value, where)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReportError(where + " must be an ISO-8601 timestamp") from exc
    require(parsed.tzinfo is not None, where + " must include a timezone")
    return parsed


def unique_object(pairs):
    data = {}
    for key, value in pairs:
        require(key not in data, "duplicate JSON key: " + key)
        data[key] = value
    return data


def blank_result():
    return {"status": "not_run", "evidence": [], "note": ""}


def new_report(run_id, mode):
    scope_ids = {
        "topic": {"topic", "facts"},
        "planning": {"topic", "facts", "script", "storyboard"},
        "full-video": {key for key, _ in STAGES},
        "asset-pack": {"storyboard", "voice", "packaging", "delivery"},
        "local-library-import": {"delivery"},
        "retrospective-improve": {"retrospective"},
    }.get(mode, set())
    stage_specs = [(key, label) for key, label in STAGES if key in scope_ids]
    check_specs = [(key, stage, label) for key, stage, label in CHECKS if stage in scope_ids]
    if mode == "retrospective-improve":
        stage_specs = [("retrospective", "复盘与改进")]
        check_specs = [("retrospective_record", "retrospective", "记录问题、纠正、反馈与有证据的候选"),
                       ("evolution_record", "retrospective", "复核变更、测试、版本和本地/远端状态；无改动也须准确记录")]
    tests = {key: {"required": True, **blank_result()} for key in ("structure", "regression", "behavior")}
    tests["regression"].update(defect_evidence=[], normal_path_evidence=[])
    return {
        "schema_version": 1,
        "run": {"run_id": run_id, "mode": mode, "status": "not_run",
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "started_at": None, "finished_at": None, "scope": "",
                "synthetic_example": False,
                "notes": "Blank template. No production, verification, or Skill change has been performed by this command."},
        "stages": [{"id": key, "label": label, **blank_result()} for key, label in stage_specs],
        "checks": [{"id": key, "stage": stage, "description": description, **blank_result()}
                   for key, stage, description in check_specs],
        "issues": [],
        "learning_candidates": [],
        "evolution": {"status": "not_run", "candidate_ids": [], "minimal_diff": None,
                      "tests": tests,
                      "writeback": {"status": "not_run", "evidence": [], "note": ""},
                      "version": {"before": None, "after": None, "rollback_ref": None},
                      "remote_sync": blank_result(), "note": ""},
        "artifacts": [],
        "permissions": []}


def validate(data):
    obj(data, "schema_version run stages checks issues learning_candidates evolution artifacts permissions", "report")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "unsupported report schema_version")
    run = obj(data["run"], "run_id mode status created_at started_at finished_at scope synthetic_example notes", "run")
    identifier(run["run_id"], "run.run_id")
    enum(run["mode"], MODES, "run.mode")
    enum(run["status"], RUN_STATUSES, "run.status")
    created = timestamp(run["created_at"], "run.created_at")
    started = timestamp(run["started_at"], "run.started_at", nullable=True)
    finished = timestamp(run["finished_at"], "run.finished_at", nullable=True)
    string(run["scope"], "run.scope", empty=run["status"] == "not_run")
    string(run["notes"], "run.notes", empty=True)
    require(type(run["synthetic_example"]) is bool, "run.synthetic_example must be boolean")
    if started is not None:
        require(started >= created, "run.started_at must not precede created_at")
    if finished is not None:
        require(started is not None and finished >= started, "finished_at requires and must not precede started_at")
    if run["status"] in {"in_progress", "completed", "failed"}:
        require(started is not None, "active or finished run requires started_at")
    if run["status"] in {"completed", "failed"}:
        require(finished is not None, "completed or failed run requires finished_at")
    if run["status"] == "not_run":
        require(started is None and finished is None, "not_run must not have started_at or finished_at")

    stages = records(data["stages"], "stages", "id label status evidence note")
    require(bool(stages), "stages must contain at least the requested stage")
    for key, stage in stages.items():
        result(stage, "stage " + key, "id label status evidence note", CHECK_STATUSES | {"in_progress"})
        string(stage["label"], "stage.label")
    checks = records(data["checks"], "checks", "id stage description status evidence note")
    require(bool(checks), "checks must contain at least one applicable check")
    for key, check in checks.items():
        result(check, "check " + key, "id stage description status evidence note")
        string(check["stage"], "check.stage")
        require(check["stage"] in stages, "check references unknown stage: " + check["stage"])
        string(check["description"], "check.description")
        parent_status = stages[check["stage"]]["status"]
        require(not (check["status"] in {"pass", "fail"} and parent_status in {"not_run", "n/a"}),
                "executed check contradicts unexecuted stage: " + key)
        require(not (parent_status == "pass" and check["status"] not in {"pass", "n/a"}),
                "passed stage has unfinished or failing check: " + key)

    issues = records(data["issues"], "issues", "id description correction feedback affected_stages severity status evidence")
    for key, issue in issues.items():
        string(issue["description"], "issue.description")
        string(issue["correction"], "issue.correction", empty=True)
        string(issue["feedback"], "issue.feedback", empty=True)
        strings(issue["affected_stages"], "issue.affected_stages", nonempty=True)
        require(set(issue["affected_stages"]) <= set(stages) | {"evolution"}, "issue references an unknown stage")
        enum(issue["severity"], {"low", "medium", "high", "critical"}, "issue.severity")
        enum(issue["status"], {"open", "in_progress", "resolved", "deferred"}, "issue.status")
        strings(issue["evidence"], "issue.evidence", nonempty=issue["status"] == "resolved")

    candidates = records(data["learning_candidates"], "learning_candidates", "id summary classification status evidence")
    for candidate in candidates.values():
        string(candidate["summary"], "learning_candidate.summary")
        enum(candidate["classification"], CLASSIFICATIONS, "learning_candidate.classification")
        enum(candidate["status"], {"proposed", "accepted", "rejected", "deferred", "applied"}, "learning_candidate.status")
        strings(candidate["evidence"], "learning_candidate.evidence", nonempty=True)

    evolution = obj(data["evolution"], "status candidate_ids minimal_diff tests writeback version remote_sync note", "evolution")
    enum(evolution["status"], EVOLUTION_STATUSES, "evolution.status")
    strings(evolution["candidate_ids"], "evolution.candidate_ids")
    for key in evolution["candidate_ids"]:
        require(key in candidates, "evolution references unknown candidate: " + key)
        require(candidates[key]["classification"] == "generalizable", "only generalizable candidates belong in Skill evolution")
    string(evolution["minimal_diff"], "evolution.minimal_diff", nullable=True)
    string(evolution["note"], "evolution.note", empty=True)
    tests = obj(evolution["tests"], "structure regression behavior", "evolution.tests")
    for key, test in tests.items():
        fields = "required status evidence note"
        if key == "regression":
            fields += " defect_evidence normal_path_evidence"
        result(test, "evolution.tests." + key, fields)
        require(type(test["required"]) is bool, "evolution test.required must be boolean")
        if key in {"structure", "regression"}:
            require(test["required"], key + " test is always required when applying a Skill change")
        if key == "regression":
            strings(test["defect_evidence"], "regression.defect_evidence", nonempty=test["status"] == "pass")
            strings(test["normal_path_evidence"], "regression.normal_path_evidence", nonempty=test["status"] == "pass")
    writeback = obj(evolution["writeback"], "status evidence note", "evolution.writeback")
    enum(writeback["status"], {"not_run", "local_applied", "kept_previous", "rolled_back", "blocked", "n/a"}, "evolution.writeback.status")
    strings(writeback["evidence"], "evolution.writeback.evidence", nonempty=writeback["status"] in {"local_applied", "kept_previous", "rolled_back"})
    string(writeback["note"], "evolution.writeback.note", empty=writeback["status"] not in {"blocked", "n/a"})
    version = obj(evolution["version"], "before after rollback_ref", "evolution.version")
    for key, value in version.items():
        string(value, "evolution.version." + key, nullable=True)
    result(evolution["remote_sync"], "evolution.remote_sync")

    state = evolution["status"]
    if state in {"candidate", "diff_ready", "testing", "local_applied", "remote_synced", "rolled_back"}:
        require(bool(evolution["candidate_ids"]), "evolution state requires linked candidates")
    if state in {"diff_ready", "testing", "local_applied", "remote_synced", "rolled_back"}:
        require(evolution["minimal_diff"] is not None, "evolution state requires a minimal_diff reference")
        require(all(candidates[key]["status"] in {"accepted", "applied"} for key in evolution["candidate_ids"]),
                "a Skill diff requires accepted generalizable candidates")
    if state in {"local_applied", "remote_synced"}:
        require(all(test["status"] == "pass" if test["required"] else test["status"] in {"pass", "n/a"}
                    for test in tests.values()), "applied evolution requires required tests to pass; optional behavior may be n/a with a reason")
        require(writeback["status"] == "local_applied", "applied evolution requires applied writeback")
        require(all(version.values()) and version["before"] != version["after"], "applied evolution requires distinct before/after versions and a rollback reference")
    if writeback["status"] == "local_applied":
        require(state in {"local_applied", "remote_synced"}, "local_applied writeback requires local_applied or remote_synced evolution")
    if state == "failed":
        require(writeback["status"] in {"kept_previous", "rolled_back"}, "failed evolution must record preserved or restored previous version")
        require(version["before"] is not None, "failed evolution requires previous version")
    if writeback["status"] == "kept_previous":
        require(version["before"] is not None and version["after"] in {None, version["before"]}, "kept_previous must retain the previous version")
    if state == "rolled_back" or writeback["status"] == "rolled_back":
        require(state in {"failed", "rolled_back"} and writeback["status"] == "rolled_back", "rollback state and writeback must agree")
        require(all(version.values()) and version["after"] == version["before"], "rollback requires restored previous version and rollback reference")
    if state in {"not_run", "no_change", "candidate", "diff_ready"}:
        require(writeback["status"] in {"not_run", "n/a"}, "unapplied evolution must not claim writeback")
        require(all(test["status"] in {"not_run", "n/a"} for test in tests.values()), "evolution state contradicts executed tests")
    if state == "blocked":
        require(bool(evolution["note"].strip()), "blocked evolution requires a note describing the blocker")
    if state == "no_change":
        require(bool(evolution["note"].strip()), "no_change requires a note describing the review and why no Skill change is needed")
    if state == "not_run":
        require(not evolution["candidate_ids"] and evolution["minimal_diff"] is None and not any(version.values()), "not_run evolution must be a blank record")
    if evolution["remote_sync"]["status"] == "pass":
        require(state in {"remote_synced", "rolled_back"}, "passed remote sync requires remote_synced or rolled_back state")
    if state == "remote_synced":
        require(evolution["remote_sync"]["status"] == "pass", "remote_synced requires evidenced passed remote sync")

    artifacts = records(data["artifacts"], "artifacts", "id path kind status evidence")
    for artifact in artifacts.values():
        string(artifact["path"], "artifact.path")
        path = artifact["path"]
        require(not path.startswith("/") and "\\" not in path and ":" not in path
                and all(part not in {"", ".", ".."} for part in path.split("/"))
                and not any(ord(c) < 32 or ord(c) == 127 for c in path), "artifact.path must be a canonical relative path")
        string(artifact["kind"], "artifact.kind")
        enum(artifact["status"], {"planned", "created", "verified", "missing"}, "artifact.status")
        strings(artifact["evidence"], "artifact.evidence", nonempty=artifact["status"] == "verified")

    permissions = records(data["permissions"], "permissions", "id action target status evidence note")
    for permission in permissions.values():
        string(permission["action"], "permission.action")
        string(permission["target"], "permission.target")
        enum(permission["status"], {"not_requested", "requested", "approved", "denied", "not_required"}, "permission.status")
        strings(permission["evidence"], "permission.evidence", nonempty=permission["status"] == "approved")
        string(permission["note"], "permission.note", empty=permission["status"] != "not_required")

    if run["status"] == "not_run":
        require(all(item["status"] in {"not_run", "n/a", "blocked"} for item in list(stages.values()) + list(checks.values())), "not_run report cannot claim executed stages or checks")
        require(state in {"not_run", "no_change", "candidate", "blocked"}, "not_run report cannot claim executed Skill evolution")
        require(all(test["status"] in {"not_run", "n/a"} for test in tests.values()), "not_run report cannot claim executed evolution tests")
    if run["status"] == "completed":
        require(state != "not_run", "completed report requires an evolution review; use no_change with a reason when no patch is appropriate")
        require(all(item["status"] in {"pass", "n/a"} for item in list(stages.values()) + list(checks.values())), "completed report contains unfinished or failing stages/checks")
        require(any(check["status"] == "pass" for check in checks.values()), "completed report requires an evidenced passed check")
        require(not any(issue["severity"] in {"high", "critical"} and issue["status"] != "resolved" for issue in issues.values()), "completed report has unresolved high/critical issues")
    return {"status": "valid", "schema_version": 1, "run_id": run["run_id"],
            "run_status": run["status"], "stage_count": len(stages), "check_count": len(checks),
            "notice": "Structural validation only; no evidence authenticity, media quality, permission, or external state was verified."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="create a blank not_run report; never overwrite")
    new.add_argument("--run-id", required=True)
    new.add_argument("--mode", choices=sorted(MODES), required=True)
    new.add_argument("--output", required=True)
    check = commands.add_parser("validate", help="validate JSON structure and status consistency")
    check.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            report = new_report(args.run_id, args.mode)
            validate(report)
            with Path(args.output).open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
            response = {"status": "created", "run_id": args.run_id, "run_status": "not_run"}
        else:
            path = Path(args.input)
            require(not path.is_symlink(), "report input must not be a symlink")
            require(stat.S_ISREG(path.stat().st_mode), "report input must be a regular file")
            with path.open("r", encoding="utf-8") as stream:
                report = json.load(stream, object_pairs_hook=unique_object,
                                   parse_constant=lambda value: (_ for _ in ()).throw(ReportError("non-JSON number: " + value)))
            response = validate(report)
        print(json.dumps(response, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
