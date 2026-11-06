#!/usr/bin/env python3
"""souji-pointer-check.py — do the repo-relative paths a lesson or prereg cites exist at a revision?

Round 70 (lesson fix for r69 routed D1 and M14: cited evidence under the gitignored .ufo/waves/ tree
and prereg pointers to files that never existed). Reads each FILE from the revision (not the
worktree), extracts every token that starts with census/, corpus/, tests/, .ufo/ or tools/souji-
(bare tools/<x> tokens are fixture-internal paths in this lane's prose and are not checked) and
checks `git cat-file -e <rev>:<path>` (files and directories both count). In a file under
census/round-N/, tokens starting with probe/, probes/, records/, controls/ or battery/ are resolved
against that file's directory. Tokens holding a placeholder (`<`, `*`, `{`, `$`, `…`) are skipped.
  SUMMARY files=<n> checked=<n> missing=<n> skipped=<n>
  EXIT=0 iff missing=0; 1 iff missing>0; 2 = could not evaluate

Read-only; stdlib only.

Usage: python3 -B tools/souji-pointer-check.py --root LANE --rev FULL40 FILE [FILE...]
"""
import argparse
import re
import subprocess
import sys

TOKEN = re.compile(r"(?<![A-Za-z0-9_./-])((?:census|corpus|tests|\.ufo)/[^\s`'\"()\[\]|,;]+"
                   r"|tools/souji-[^\s`'\"()\[\]|,;]+"
                   r"|(?:probe|probes|records|controls|battery)/[^\s`'\"()\[\]|,;]+)")
LOCAL_PREFIXES = ("probe/", "probes/", "records/", "controls/", "battery/")
PLACEHOLDER = ("<", "*", "{", "$", "…")


def git(root, *args):
    env = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run(["git", "-C", root, *args], capture_output=True, env=env)


def main(argv):
    ap = argparse.ArgumentParser(prog="souji-pointer-check.py")
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("files", nargs="+")
    ns = ap.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", ns.rev):
        print("POINTER-CHECK-FATAL: --rev must be full 40-hex", file=sys.stderr)
        print("EXIT=2")
        return 2
    checked = missing = skipped = 0
    for rel in ns.files:
        r = git(ns.root, "show", f"{ns.rev}:{rel}")
        if r.returncode != 0:
            print(f"POINTER-CHECK-FATAL: {rel} not readable at {ns.rev}", file=sys.stderr)
            print("EXIT=2")
            return 2
        seen = set()
        for lineno, line in enumerate(r.stdout.decode("utf-8", "replace").splitlines(), 1):
            for m in TOKEN.finditer(line):
                path = re.sub(r":[0-9][0-9,\-]*$", "", m.group(1).rstrip(".:/")).rstrip("/")
                if path.startswith(LOCAL_PREFIXES):
                    if not rel.startswith("census/round-"):
                        continue
                    path = rel.rsplit("/", 1)[0] + "/" + path
                if any(p in path for p in PLACEHOLDER):
                    skipped += 1
                    continue
                if (path, lineno) in seen:
                    continue
                seen.add((path, lineno))
                checked += 1
                if git(ns.root, "cat-file", "-e", f"{ns.rev}:{path}").returncode != 0:
                    missing += 1
                    print(f"MISSING {rel}:{lineno} {path}")
    print(f"SUMMARY files={len(ns.files)} checked={checked} missing={missing} skipped={skipped}")
    rc = 0 if missing == 0 else 1
    print(f"EXIT={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
