#!/usr/bin/env python3
"""souji-coverage-agreement.py — coverage-map agreement instrument (round 24, C2).

Coverage map: corpus/README.md tables whose header's first cell is `ground` and third cell begins
`entries` (case-insensitive). A row carries F<k> when its ground cell matches ^F[0-9]+ then space,
`-` or end. Knowledge path: a backticked entries-cell span ending `knowledge/<name>`.
  MISSING-FROM-MAP   entry with front-matter `ground: F<k>` named by no knowledge path of any F<k> row
  DANGLING-MAP-PATH  knowledge path (one per README line and name) absent from corpus/knowledge at rev
Output: sorted MISMATCH<TAB><class><TAB><path><TAB><detail> rows, then
  grounded=G mapped=M dangling=D mismatches=X   (mapped: every F<k> of the entry is mapped)
Exit 0 iff X == 0, 1 otherwise, 2 refused (argv, non-40-hex rev, not a commit, git failure).
Reads committed bytes only (`git show <rev>:<path>`, `git ls-tree`). Contract: round-24 prereg C2.
"""
from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

README = "corpus/README.md"
KNOWLEDGE = "corpus/knowledge"
FULL_REV = re.compile(r"[0-9a-fA-F]{40}")
GROUND_TOKEN = re.compile(r"^F([0-9]+)(?=[ \-]|$)")
FRONT_GROUND = re.compile(r"^ground:\s*F([0-9]+)")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
KNOWLEDGE_PATH = re.compile(r"(?:^|/)knowledge/([^/\s]+)$")


class Refused(Exception):
    """Exit-2 refusal: argv, revision or git failure."""


def git(root: str, *args: str) -> bytes:
    env = dict(os.environ, LC_ALL="C", GIT_OPTIONAL_LOCKS="0")
    proc = subprocess.run(["git", "-C", root, *args], capture_output=True, env=env)
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip()
        raise Refused(f"git {' '.join(args)} exited {proc.returncode}: {err}")
    return proc.stdout


def show(root: str, rev: str, path: str) -> str:
    return git(root, "show", "--no-textconv", f"{rev}:{path}").decode("utf-8", "replace")


def knowledge_tree(root: str, rev: str) -> dict[str, str]:
    """name -> object type for every direct child of corpus/knowledge at rev."""
    out: dict[str, str] = {}
    for rec in filter(None, git(root, "ls-tree", "-z", rev, "--", f"{KNOWLEDGE}/").split(b"\0")):
        meta, _, path = rec.decode("utf-8", "surrogateescape").partition("\t")
        out[path.rsplit("/", 1)[-1]] = meta.split()[1]
    return out


def cells(line: str) -> list[str]:
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [c.strip() for c in CELL_SPLIT.split(body)]


def map_rows(readme: str):
    """Yield (lineno, ground_cell, entries_cell) for every coverage-map table row."""
    in_map = in_table = False
    for lineno, line in enumerate(readme.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            in_map = in_table = False
            continue
        row = cells(line)
        if not in_table:
            in_table = True
            in_map = (len(row) >= 3 and row[0].lower() == "ground"
                      and row[2].lower().startswith("entries"))
            continue
        if not in_map or all(SEPARATOR_CELL.match(c) for c in row if c):
            continue
        yield lineno, row[0], (row[2] if len(row) >= 3 else "")


def front_grounds(text: str) -> set[int]:
    ks: set[int] = set()
    for line in text.splitlines():
        if line.startswith("# "):
            break
        m = FRONT_GROUND.match(line)
        if m:
            ks.add(int(m.group(1)))
    return ks


def measure(root: str, rev: str) -> tuple[list[tuple[str, str, str]], dict[str, int]]:
    tree = knowledge_tree(root, rev)
    mapped_by_k: dict[int, set[str]] = {}
    rows_by_k: dict[int, int] = {}
    mismatches: list[tuple[str, str, str]] = []
    for lineno, ground, entries in map_rows(show(root, rev, README)):
        tok = GROUND_TOKEN.match(ground)
        names: list[str] = []
        for span in CODE_SPAN.findall(entries):
            m = KNOWLEDGE_PATH.search(span.strip())
            if m and m.group(1) not in names:
                names.append(m.group(1))
                if m.group(1) not in tree:
                    mismatches.append(("DANGLING-MAP-PATH", f"{KNOWLEDGE}/{m.group(1)}",
                                       f"{README}:{lineno} span={span.strip()}"))
        if tok:
            k = int(tok.group(1))
            rows_by_k[k] = rows_by_k.get(k, 0) + 1
            mapped_by_k.setdefault(k, set()).update(names)
    dangling = len(mismatches)
    grounded = mapped = 0
    for name in sorted(tree):
        if not name.endswith(".md") or tree[name] != "blob":
            continue
        ks = front_grounds(show(root, rev, f"{KNOWLEDGE}/{name}"))
        if not ks:
            continue
        grounded += 1
        missing = [k for k in sorted(ks) if name not in mapped_by_k.get(k, set())]
        mapped += not missing
        for k in missing:
            mismatches.append(("MISSING-FROM-MAP", f"{KNOWLEDGE}/{name}",
                               f"ground=F{k} map_rows_F{k}={rows_by_k.get(k, 0)}"))
    mismatches.sort()
    counts = {"grounded": grounded, "mapped": mapped, "dangling": dangling,
              "mismatches": len(mismatches)}
    return mismatches, counts


class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        raise Refused(f"argv: {message}")


def main(argv: list[str]) -> int:
    parser = Parser(description="coverage-map agreement over committed bytes (r24 C2)")
    parser.add_argument("--root", required=True)
    parser.add_argument("--rev", required=True)
    try:
        args = parser.parse_args(argv)
        if not FULL_REV.fullmatch(args.rev):
            raise Refused(f"--rev must be a full 40-hex commit id, got {args.rev!r}")
        git(args.root, "rev-parse", "--verify", "--quiet", f"{args.rev}^{{commit}}")
        mismatches, counts = measure(args.root, args.rev)
    except Refused as exc:
        print(f"souji-coverage-agreement: refused: {exc}", file=sys.stderr)
        return 2
    for cls, path, detail in mismatches:
        print(f"MISMATCH\t{cls}\t{path}\t{detail}")
    print(" ".join(f"{k}={v}" for k, v in counts.items()))
    return 0 if counts["mismatches"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
