#!/usr/bin/env python3
"""Create and verify portable SHA-256 manifests using only the standard library.

This tool reads local regular files. It does not upload, download, grant access,
judge media quality, or establish the authenticity of a manifest. Use a quiescent
directory and a trusted original manifest. Output files must be outside the root.
Exit codes: 0 success, 1 content mismatch, 2 invalid input or filesystem error.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


class ManifestError(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError("duplicate JSON key: " + key)
        result[key] = value
    return result


def relative_path(value):
    """Accept canonical, portable POSIX relative file paths only."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ManifestError("path must be a nonempty POSIX relative path")
    parts = value.split("/")
    if (value.startswith("/") or any(p in ("", ".", "..") for p in parts)
            or any(ord(c) < 32 or ord(c) == 127 for c in value)
            or any(":" in p for p in parts)
            or str(PurePosixPath(value)) != value):
        raise ManifestError("unsafe or noncanonical relative path: " + repr(value))
    return value


def root_directory(value):
    root = Path(os.path.abspath(value))
    if root.is_symlink():
        raise ManifestError("root must not be a symlink")
    if not root.is_dir():
        raise ManifestError("root must be an existing directory")
    return root.resolve()


def outside_root(value, root):
    path = Path(os.path.abspath(value))
    if path.is_symlink():
        raise ManifestError("manifest must not be a symlink")
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return path
    raise ManifestError("manifest must be outside root to prevent self-reference")


def scan_tree(root):
    files = {}

    def walk(directory):
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda item: item.name)
        for entry in children:
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            relative_path(relative)
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise ManifestError("symlink is not allowed: " + relative)
            if stat.S_ISDIR(info.st_mode):
                walk(path)
            elif stat.S_ISREG(info.st_mode):
                files[relative] = path
            else:
                raise ManifestError("non-regular file is not allowed: " + relative)

    walk(root)
    return files


def file_record(relative, path):
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ManifestError("file is not a regular file: " + relative)
    # O_NOFOLLOW prevents final-component symlink races where the OS supports it.
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ManifestError("file changed while opening: " + relative)
        digest = hashlib.sha256()
        size = 0
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    current = path.lstat()
    signature = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    if size != before.st_size or signature(before) != signature(after) or signature(after) != signature(current):
        raise ManifestError("file changed while hashing: " + relative)
    return {"path": relative, "size": size, "sha256": digest.hexdigest()}


def load_manifest(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ManifestError("manifest must be a regular file")
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream, object_pairs_hook=unique_object)
    if not isinstance(data, dict) or set(data) != {"schema_version", "algorithm", "files"}:
        raise ManifestError("manifest must contain schema_version, algorithm, and files only")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1 or data["algorithm"] != "sha256":
        raise ManifestError("unsupported manifest schema or algorithm")
    if not isinstance(data["files"], list):
        raise ManifestError("files must be an array")
    seen = set()
    for entry in data["files"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise ManifestError("each file needs path, size, and sha256 only")
        name = relative_path(entry["path"])
        if name in seen:
            raise ManifestError("duplicate manifest entry: " + name)
        seen.add(name)
        if type(entry["size"]) is not int or entry["size"] < 0:
            raise ManifestError("size must be a nonnegative integer: " + name)
        if not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise ManifestError("sha256 must contain 64 lowercase hexadecimal characters: " + name)
    return data


def create(root, output):
    files = scan_tree(root)
    manifest = {"schema_version": 1, "algorithm": "sha256",
                "files": [file_record(name, files[name]) for name in sorted(files)]}
    # Exclusive creation never replaces an existing record. Parent must exist.
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    return {"status": "created", "file_count": len(files),
            "total_bytes": sum(entry["size"] for entry in manifest["files"])}


def verify(root, manifest_path, strict):
    expected = load_manifest(manifest_path)
    actual = scan_tree(root)
    wanted = {entry["path"]: entry for entry in expected["files"]}
    missing = sorted(set(wanted) - set(actual))
    extra = sorted(set(actual) - set(wanted))
    damaged = []
    for name in sorted(set(wanted) & set(actual)):
        current = file_record(name, actual[name])
        if current != wanted[name]:
            damaged.append({"path": name, "expected_size": wanted[name]["size"],
                            "actual_size": current["size"],
                            "expected_sha256": wanted[name]["sha256"],
                            "actual_sha256": current["sha256"]})
    ok = not missing and not damaged and (not strict or not extra)
    return {"status": "pass" if ok else "fail", "strict": strict,
            "expected_files": len(wanted), "matched_files": len(wanted) - len(missing) - len(damaged),
            "missing": missing, "damaged": damaged, "extra": extra}, 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("create", help="hash a stable local directory into a new external manifest")
    make.add_argument("--root", required=True)
    make.add_argument("--output", required=True, help="new JSON file outside --root; parent must exist")
    check = commands.add_parser("verify", help="compare any local/read-back directory against the original manifest")
    check.add_argument("--root", required=True)
    check.add_argument("--manifest", required=True)
    check.add_argument("--strict", action="store_true", help="fail on extra files; otherwise report but allow them")
    args = parser.parse_args(argv)
    try:
        root = root_directory(args.root)
        path = outside_root(args.output if args.command == "create" else args.manifest, root)
        if args.command == "create":
            result, code = create(root, path), 0
        else:
            result, code = verify(root, path, args.strict)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return code
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
