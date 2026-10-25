#!/usr/bin/env python3
"""souji-coverage-agreement.py — coverage-map agreement instrument (round 24 C2, round 25 C1).

Coverage map: corpus/README.md tables whose header's first cell is `ground` and third cell begins
`entries` (case-insensitive). A row carries F<k> when its ground cell matches ^F[0-9]+ then space,
`-` or end. Knowledge path: a backticked entries-cell span ending `knowledge/<name>`.
  MISSING-FROM-MAP   entry with front-matter `ground: F<k>` named by no knowledge path of any F<k> row
  DANGLING-MAP-PATH  knowledge path (one per README line and name) absent from corpus/knowledge at rev
  KILL-RULE          (--base-rev only) entry grounded at base that at rev is not a blob, or lacks a
                     front-matter `ground: F<k>` line for some base F<k> (extra grounds allowed);
                     one row per entry
Output: sorted MISMATCH<TAB><class><TAB><path><TAB><detail> rows, then
  grounded=G mapped=M dangling=D mismatches=X   (mapped: every F<k> of the entry is mapped)
with --base-rev the counts line gains ` kill_tested=N kill_violations=V` (N: entries grounded at
base; V: entries with a KILL-RULE row; X counts map rows only). Without --base-rev the output is
the r24 output. --base-rev is refused like --rev.
Exit 0 iff X == 0 and V == 0, 1 otherwise, 2 refused (argv, non-40-hex rev, not a commit, git
failure). Reads committed bytes only (`git show <rev>:<path>`, `git ls-tree`).
Contract: round-24 prereg C2; round-25 prereg C1 (--base-rev) and its amendments 1 and 3.
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


def entry_grounds(root: str, rev: str, tree: dict[str, str]) -> dict[str, set[int]]:
    """name -> front-matter F<k> set for every grounded `.md` blob of the knowledge tree."""
    out: dict[str, set[int]] = {}
    for name in sorted(tree):
        if not name.endswith(".md") or tree[name] != "blob":
            continue
        ks = front_grounds(show(root, rev, f"{KNOWLEDGE}/{name}"))
        if ks:
            out[name] = ks
    return out


def kill_rule(root: str, base_rev: str, tree: dict[str, str],
              grounds: dict[str, set[int]]) -> tuple[list[tuple[str, str, str]], int]:
    """One KILL-RULE row per base-grounded entry lost or re-grounded at rev; entries tested."""
    base = entry_grounds(root, base_rev, knowledge_tree(root, base_rev))
    rows: list[tuple[str, str, str]] = []
    for name, base_ks in base.items():
        path = f"{KNOWLEDGE}/{name}"
        kind = tree.get(name)
        got = grounds.get(name, set())
        had = ",".join(f"F{k}" for k in sorted(base_ks))
        if kind != "blob":
            rows.append(("KILL-RULE", path, f"base_grounds={had} rev={kind or 'absent'}"))
        elif not base_ks <= got:
            lost = ",".join(f"F{k}" for k in sorted(base_ks - got))
            have = ",".join(f"F{k}" for k in sorted(got)) or "none"
            rows.append(("KILL-RULE", path,
                         f"base_grounds={had} lost={lost} rev_grounds={have}"))
    return rows, len(base)


def measure(root: str, rev: str, base_rev: str | None = None
            ) -> tuple[list[tuple[str, str, str]], dict[str, int]]:
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
    grounds = entry_grounds(root, rev, tree)
    mapped = 0
    for name, ks in grounds.items():
        missing = [k for k in sorted(ks) if name not in mapped_by_k.get(k, set())]
        mapped += not missing
        for k in missing:
            mismatches.append(("MISSING-FROM-MAP", f"{KNOWLEDGE}/{name}",
                               f"ground=F{k} map_rows_F{k}={rows_by_k.get(k, 0)}"))
    counts = {"grounded": len(grounds), "mapped": mapped, "dangling": dangling,
              "mismatches": len(mismatches)}
    if base_rev is not None:
        kills, tested = kill_rule(root, base_rev, tree, grounds)
        mismatches += kills
        counts["kill_tested"] = tested
        counts["kill_violations"] = len(kills)
    mismatches.sort()
    return mismatches, counts


class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        raise Refused(f"argv: {message}")


def commit_rev(root: str, flag: str, rev: str) -> None:
    if not FULL_REV.fullmatch(rev):
        raise Refused(f"{flag} must be a full 40-hex commit id, got {rev!r}")
    git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")


def main(argv: list[str]) -> int:
    parser = Parser(description="coverage-map agreement over committed bytes (r24 C2, r25 C1)")
    parser.add_argument("--root", required=True)
    parser.add_argument("--rev", required=True)
    parser.add_argument("--base-rev")
    try:
        args = parser.parse_args(argv)
        commit_rev(args.root, "--rev", args.rev)
        if args.base_rev is not None:
            commit_rev(args.root, "--base-rev", args.base_rev)
        mismatches, counts = measure(args.root, args.rev, args.base_rev)
    except Refused as exc:
        print(f"souji-coverage-agreement: refused: {exc}", file=sys.stderr)
        return 2
    for cls, path, detail in mismatches:
        print(f"MISMATCH\t{cls}\t{path}\t{detail}")
    print(" ".join(f"{k}={v}" for k, v in counts.items()))
    return 0 if counts["mismatches"] == 0 and counts.get("kill_violations", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
