#!/usr/bin/env python3
"""transcript-manifest.py — write and verify MANIFEST.sha256 for a transcript bundle.

Usage:
    transcript-manifest.py --write <dir>   # (re)generate <dir>/MANIFEST.sha256
    transcript-manifest.py --check <dir>   # verify <dir> against its MANIFEST.sha256

MANIFEST.sha256 format: one line per regular file, `sha256  relpath`
(two spaces, GNU sha256sum text format), sorted by relpath in LC_ALL=C
byte order. MANIFEST.sha256 itself is excluded from enumeration both when
writing and when checking. Only regular files are enumerated; non-regular
entries (symlinks, sockets, fifos) are ignored in both directions.

Exit codes:
    0  write succeeded, or check verified every line and found no extras
    1  check failed: hash mismatch, manifest-listed file missing, or
       on-disk regular file not listed in the manifest (extra)
    2  usage error: bad arguments, missing/unreadable dir, or (for
       --check) absent/unparseable MANIFEST.sha256
"""

import argparse
import hashlib
import os
import sys

MANIFEST_NAME = "MANIFEST.sha256"


def iter_regular_files(root):
    """Yield relpaths (posix-style, relative to root) of every regular file
    under root, excluding the top-level MANIFEST.sha256."""
    relpaths = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            if rel == MANIFEST_NAME:
                continue
            if not os.path.isfile(full):
                continue
            relpaths.append(rel)
    return relpaths


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def c_order_key(relpath):
    """LC_ALL=C byte-order sort key."""
    return os.fsencode(relpath)


def build_lines(root, relpaths):
    lines = []
    for rel in sorted(relpaths, key=c_order_key):
        digest = sha256_file(os.path.join(root, rel))
        lines.append("{}  {}".format(digest, rel))
    return lines


def cmd_write(root):
    relpaths = iter_regular_files(root)
    lines = build_lines(root, relpaths)
    manifest_path = os.path.join(root, MANIFEST_NAME)
    tmp_path = manifest_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
        for line in lines:
            fh.write(line + "\n")
    os.replace(tmp_path, manifest_path)
    print("wrote {} ({} files)".format(manifest_path, len(lines)))
    return 0


def parse_manifest_line(line):
    # sha256sum text format: 64 hex chars, two spaces, relpath.
    if len(line) < 67:
        return None
    digest = line[:64]
    if line[64:66] != "  ":
        return None
    if any(c not in "0123456789abcdef" for c in digest):
        return None
    rel = line[66:]
    if not rel or rel.startswith("/") or ".." in rel.split("/"):
        return None
    return digest, rel


def cmd_check(root):
    manifest_path = os.path.join(root, MANIFEST_NAME)
    if not os.path.isfile(manifest_path):
        print("error: no manifest at {}".format(manifest_path), file=sys.stderr)
        return 2
    listed = {}
    with open(manifest_path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            if not line:
                continue
            parsed = parse_manifest_line(line)
            if parsed is None:
                print(
                    "error: unparseable manifest line {}: {!r}".format(
                        lineno, line[:80]
                    ),
                    file=sys.stderr,
                )
                return 2
            digest, rel = parsed
            listed[rel] = digest

    failures = 0
    for rel in sorted(listed, key=c_order_key):
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            print("missing: {}".format(rel), file=sys.stderr)
            failures += 1
            continue
        actual = sha256_file(full)
        if actual != listed[rel]:
            print(
                "mismatch: {} (manifest {}, actual {})".format(
                    rel, listed[rel], actual
                ),
                file=sys.stderr,
            )
            failures += 1

    on_disk = set(iter_regular_files(root))
    for rel in sorted(on_disk - set(listed), key=c_order_key):
        print("extra: {}".format(rel), file=sys.stderr)
        failures += 1

    if failures:
        print("check FAILED: {} problem(s)".format(failures), file=sys.stderr)
        return 1
    print("check OK: {} files verified".format(len(listed)))
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", metavar="DIR", help="write DIR/MANIFEST.sha256")
    group.add_argument("--check", metavar="DIR", help="verify DIR/MANIFEST.sha256")
    args = parser.parse_args(argv)

    target = args.write or args.check
    if not os.path.isdir(target):
        print("error: not a directory: {}".format(target), file=sys.stderr)
        return 2
    if args.write:
        return cmd_write(target)
    return cmd_check(target)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
