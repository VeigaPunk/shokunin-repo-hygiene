#!/usr/bin/env python3
"""k67-mutants.py — single-edit mutants of a souji-receipt-write.py source (S67MutKill, scratch only).

Usage: k67-mutants.py SOURCE OUTDIR [NAME ...]

Every anchor is content-based and asserted before the edit:
  kind "lines": the line whose text starts with FIRST is located (must occur exactly once); the mutant removes
                N consecutive lines from it (N asserted; the last removed line must end with LAST_SUFFIX).
  kind "subs":  one or more (old, new) substring replacements; each old must occur exactly once.
Writes OUTDIR/<NAME>.py; prints MUTANT name sha256 bytes desc. Never writes SOURCE.
"""
import hashlib
import os
import sys

MUTANTS = {
    # ---- r66 pins and gates (carried; anchors unchanged on the r67 candidate) ----
    "K1": ("remove RECEIPT-ENV-CONFIG-SET gate (5 lines)", "lines",
           ("    cfg_env = sorted(k for k in os.environ", 5, 'unset them and retry")')),
    "K2": ("remove RECEIPT-ENV-REDIRECT-SET gate (5 lines)", "lines",
           ("    redirect_env = sorted(k for k in os.environ", 5, 'unset them and retry")')),
    "K3": ("remove git() `-c core.excludesFile=<devnull>` pin", "subs",
           [('"-c", f"core.excludesFile={os.devnull}", *args]', "*args]")]),
    "K4": ("remove git() GIT_CONFIG_GLOBAL=os.devnull pin", "lines",
           ('    env["GIT_CONFIG_GLOBAL"] = os.devnull', 1, '    env["GIT_CONFIG_GLOBAL"] = os.devnull')),
    "K5": ("snapshot mode mask 0o7777 -> 0o777", "subs",
           [("st_mode & 0o7777", "st_mode & 0o777")]),
    "K6": ("remove git() GIT_NO_REPLACE_OBJECTS=1 pin", "lines",
           ('    env["GIT_NO_REPLACE_OBJECTS"] = "1"', 1, '    env["GIT_NO_REPLACE_OBJECTS"] = "1"')),
    "K7": ("remove git() GIT_CONFIG_NOSYSTEM=1 pin", "lines",
           ('    env["GIT_CONFIG_NOSYSTEM"] = "1"', 1, '    env["GIT_CONFIG_NOSYSTEM"] = "1"')),
    "K8": ("remove RECEIPT-INDEX-ENV-SET gate (3 lines)", "lines",
           ('    if "GIT_INDEX_FILE" in os.environ:', 3, '"(value not shown); unset it and retry")')),
    # ---- r67 GIT_COMMON_DIR check (candidate-only anchors) ----
    "M-CD-CALL": ("remove the GIT_COMMON_DIR check call (_check_env_commondir(root))", "lines",
                  ("    _check_env_commondir(root)", 1, "    _check_env_commondir(root)")),
    "M-CD-EMPTY": ("drop the empty-value refusal (value == \"\")", "subs",
                   [('    if value == "":\n        refuse(mismatch)\n', "")]),
    "M-CD-NCABS": ("non-canonical compare: abspath on both sides, no realpath", "subs",
                   [("common = os.path.realpath(os.path.join(root, os.fsdecode(r.stdout).rstrip(\"\\n\")))",
                     "common = os.path.abspath(os.path.join(root, os.fsdecode(r.stdout).rstrip(\"\\n\")))"),
                    ("if os.path.realpath(value) != common:", "if os.path.abspath(value) != common:")]),
    "M-CD-NCRAW": ("non-canonical compare: raw string compare of rev-parse output vs value", "subs",
                   [("common = os.path.realpath(os.path.join(root, os.fsdecode(r.stdout).rstrip(\"\\n\")))",
                     "common = os.fsdecode(r.stdout).rstrip(\"\\n\")"),
                    ("if os.path.realpath(value) != common:", "if value != common:")]),
    "M-CD-SCRUB": ("drop GIT_COMMON_DIR from the git() scrub tuple", "subs",
                   [('if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")',
                     'if k not in ("GIT_DIR", "GIT_WORK_TREE")')]),
    "M-CD-ROOTREL": ("relative value resolved against root, not the writer's cwd", "subs",
                     [("if os.path.realpath(value) != common:",
                       "if os.path.realpath(os.path.join(root, value)) != common:")]),
}


def _apply_lines(text: str, name: str, first: str, count: int, last_suffix: str) -> str:
    lines = text.splitlines(keepends=True)
    idx = [i for i, l in enumerate(lines) if l.startswith(first)]
    if len(idx) != 1:
        raise SystemExit(f"{name}: first-line anchor occurs {len(idx)} times: {first!r}")
    i = idx[0]
    last_line = lines[i + count - 1].rstrip("\n")
    if not last_line.endswith(last_suffix):
        raise SystemExit(f"{name}: line {i + count} is {last_line!r}, expected suffix {last_suffix!r}")
    if count == 1 and lines[i].rstrip("\n") != first:
        raise SystemExit(f"{name}: single-line anchor is {lines[i].rstrip()!r}, expected exact {first!r}")
    return "".join(lines[:i] + lines[i + count:])


def build(src_bytes: bytes, name: str) -> tuple[bytes, str]:
    desc, kind, payload = MUTANTS[name]
    text = src_bytes.decode("utf-8")
    if kind == "subs":
        out = text
        for old, new in payload:
            n = out.count(old)
            if n != 1:
                raise SystemExit(f"{name}: anchor occurs {n} times, expected 1: {old!r}")
            out = out.replace(old, new, 1)
    else:
        first, count, last_suffix = payload
        out = _apply_lines(text, name, first, count, last_suffix)
    if out == text:
        raise SystemExit(f"{name}: edit changed nothing")
    return out.encode("utf-8"), desc


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    src_path, outdir = argv[0], argv[1]
    names = argv[2:] or sorted(MUTANTS)
    with open(src_path, "rb") as f:
        src = f.read()
    os.makedirs(outdir, exist_ok=True)
    for name in names:
        data, desc = build(src, name)
        path = os.path.join(outdir, f"{name}.py")
        with open(path, "wb") as f:
            f.write(data)
        os.chmod(path, 0o755)
        sha = hashlib.sha256(data).hexdigest()
        print(f"MUTANT {name} sha256={sha} bytes={len(data)} desc={desc!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
