#!/usr/bin/env python3
"""souji-declared-evidence (candidate B) — declared-evidence calibration audit.

Round 22 attempt 2, claim C1. A self-assessment file is parsed at a named
revision; every machine-checkable assertion it makes about this repository is
re-derived from committed bytes at that revision.

Extraction strategy (candidate B, deliberately unlike a raw-text scanner):
  1. split a line into Markdown table cells first (pipe-aware, backtick-aware);
  2. split each cell into backticked spans and bare runs second;
  3. classify each span / token as candidate class A, B or C;
  4. resolve only the survivors against `git` plumbing.
A raw-text scanner reads the same bytes in token order and therefore can
disagree about tokens embedded in command spans or in prose. The frozen
classes are the contract; this docstring records the boundary this candidate
picked. See the report for the enumerated disagreements.

Frozen classes (preregistration .ufo/waves/round-22/attempt2/preregistration.txt):
  A. a backticked repo-relative path ending .py/.sh/.json/.tsv/.md/.txt,
     optionally suffixed :<line>, optionally part of a glob (*) -> the path,
     glob expanded over tracked files at --rev, must be present at --rev;
  B. a bare (standalone, not glued to word characters) hex token of length
     7..40 inside a table cell that also names a revision context (the words
     commit/rev/revision/measured/at, or a census/round-<N>/ path in the same
     cell) -> `git cat-file -e <tok>^{commit}` must succeed;
  C. a 64-hex token in the same cell as exactly one backticked path -> it must
     equal sha256 of that path's bytes at --rev.

Read-only: the only writes are inside an `mkdtemp` directory under /var/tmp
(selftest only), removed by this tool. Never /tmp. No network.  Subprocess use
is limited to git plumbing (cat-file, ls-tree, show/init/add/commit in the
selftest scratch repo) and hashlib.

Counts line, exactly one line on stdout:
  assertions=<N> resolved=<R> skipped=<S> mismatches=<M>
Exit 0 iff M == 0 (1 if M > 0, 2 on tool error).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

SCRATCH_PARENT = "/var/tmp"

EXTS = ("py", "sh", "json", "tsv", "md", "txt")
# A token candidate is "path-shaped" when it ends in an auditable extension,
# optionally with a :<line> suffix.  Glob '*' is allowed inside.
EXT_TAIL_RE = re.compile(r"\.(?:" + "|".join(EXTS) + r")(?::\d+)?$", re.I)
PURE_HEX_RE = re.compile(r"[0-9a-f]{7,64}")
# Standalone hex token inside a cell.  Boundaries exclude word characters and
# '-', '.', '/', so `from195715...`, `<6ff3413-proc-file>`, `c1-matrix-4f48343.json`
# and `foo/deadbeef/report.md` do not yield tokens; `41553adb...` in
# `show 41553adb...:path` is one (':' is not a path separator here).
HEX_TOKEN_RE = re.compile(
    r"(?<![0-9A-Za-z_./-])([0-9a-f]{7,64})(?![0-9A-Za-z_./-])")
SPAN_RE = re.compile(r"`([^`\n]+)`")
REV_CONTEXT_RE = re.compile(r"\b(?:commit|rev|revision|measured|at)\b", re.I)
CENSUS_CONTEXT_RE = re.compile(r"census/round-\d+/")

GIT_CONFIG = [
    "-c", "maintenance.auto=false",
    "-c", "core.fsmonitor=false",
    "-c", "core.hooksPath=/dev/null",
]


class ToolError(RuntimeError):
    """A refusal or environment failure; exit 2, never a verdict."""


def git_env():
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
    })
    return env


def git(root, *args):
    cmd = ["git", "-C", root, *GIT_CONFIG, *args]
    return subprocess.run(cmd, capture_output=True, env=git_env())


def read_declaration(root, rel_file, rev):
    """Bytes of the declaration file as committed at --rev.

    The audit reads the declaration from the measured revision so a concurrent
    working-tree edit cannot change the declaration under measurement.  If the
    file is untracked at that revision the worktree copy is used and the
    provenance is reported on stderr (never on the counts line).
    """
    rel = rel_file.replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    if rel.startswith("/") or ".." in rel.split("/"):
        raise ToolError("--file must be repo-relative and must not contain '..'")
    rp = git(root, "cat-file", "blob", f"{rev}:{rel}")
    if rp.returncode == 0:
        fallback = os.path.join(root, rel)
        if os.path.isfile(fallback):
            with open(fallback, "rb") as handle:
                if handle.read() != rp.stdout:
                    print(f"note: worktree {rel} differs from {rev}:{rel}; "
                          "auditing committed bytes", file=sys.stderr)
        return rp.stdout, f"{rev}:{rel}"
    fallback = os.path.join(root, rel)
    if os.path.isfile(fallback):
        with open(fallback, "rb") as handle:
            print(f"note: {rel} absent at {rev}; auditing worktree bytes",
                  file=sys.stderr)
        return handle.read(), f"worktree:{rel}"
    raise ToolError(f"declaration file {rel} absent at {rev} and in the worktree")


def tracked_files(root, rev):
    rp = git(root, "ls-tree", "-r", "-z", "--name-only", rev)
    if rp.returncode != 0:
        raise ToolError(f"--rev {rev} does not name a readable tree: "
                        f"{rp.stderr.decode(errors='replace').strip()}")
    return [name for name in rp.stdout.decode("utf-8", "replace").split("\0")
            if name]


def is_table_row(line):
    return line.lstrip().startswith("|") and line.count("|") >= 2


def split_cells(line):
    """Split one Markdown table row into (start, end, text) cells.

    '|' inside backticks or escaped as '\\|' does not delimit a cell.  The
    synthetic empty cells produced by the leading/trailing pipes are dropped.
    """
    bounds = []
    start = 0
    in_tick = False
    index = 0
    size = len(line)
    while index < size:
        char = line[index]
        if char == "\\" and index + 1 < size and line[index + 1] == "|" and not in_tick:
            index += 2
            continue
        if char == "`":
            in_tick = not in_tick
        elif char == "|" and not in_tick:
            bounds.append((start, index))
            start = index + 1
        index += 1
    bounds.append((start, size))
    cells = [(a, b, line[a:b]) for a, b in bounds]
    if cells and not cells[0][2].strip():
        cells = cells[1:]
    if cells and not cells[-1][2].strip():
        cells = cells[:-1]
    return cells


def cell_index(cells, position):
    for index, (start, end, _text) in enumerate(cells):
        if start <= position < end:
            return index
    return None


def has_whitespace(text):
    return any(char.isspace() for char in text)


def glob_to_regex(pattern):
    # Only '*' is a metacharacter in the frozen class-A glob; it may span '/'.
    return re.compile("^" + "".join(".*" if ch == "*" else re.escape(ch)
                                    for ch in pattern) + "$")


def classify_path_token(token):
    """Return ('assert', core_path) or ('skip', reason)."""
    match = re.search(r":(\d+)$", token)
    core = token[:match.start()] if match else token
    if core.startswith("/"):
        return "skip", "absolute path, not repo-relative"
    if "://" in core or core.startswith(("http:", "https:")):
        return "skip", "URL, not a repo path"
    if re.search(r"[{}]", core):
        return "skip", "brace pattern, not a * glob over tracked files"
    if re.search(r"[<>\u2026]", core):
        return "skip", "placeholder/template path"
    if ":" in core:
        return "skip", "revision-qualified <rev>:<path> or non-path colon"
    if core.startswith("~"):
        return "skip", "tilde-expanded path, not repo-relative"
    if any(char in core for char in ("|", "\\", '"', "'")):
        return "skip", "non-path character in token"
    return "assert", core


def revision_context(cell_text):
    return bool(REV_CONTEXT_RE.search(cell_text)
                or CENSUS_CONTEXT_RE.search(cell_text))


def resolve_path(root, rev, tracked, tracked_set, lineno, token):
    kind, value = classify_path_token(token)
    if kind == "skip":
        return None, {"line": lineno, "token": token, "class": "-",
                      "status": "skipped", "detail": value}
    if "*" in value:
        regex = glob_to_regex(value)
        matches = [name for name in tracked if regex.match(name)]
        if matches:
            return {"line": lineno, "token": token, "class": "A",
                    "status": "resolved",
                    "detail": f"{len(matches)} match(es) at {rev}"}, None
        return {"line": lineno, "token": token, "class": "A",
                "status": "mismatch:glob-absent",
                "detail": f"no tracked file matches {value} at {rev}"}, None
    if value in tracked_set:
        return {"line": lineno, "token": token, "class": "A",
                "status": "resolved", "detail": f"present at {rev}"}, None
    return {"line": lineno, "token": token, "class": "A",
            "status": "mismatch:path-absent", "detail": f"not in tree at {rev}"}, None


def resolve_commit(root, lineno, token):
    rp = git(root, "cat-file", "-e", f"{token}^{{commit}}")
    if rp.returncode == 0:
        return {"line": lineno, "token": token, "class": "B",
                "status": "resolved", "detail": "commit/object resolves"}
    return {"line": lineno, "token": token, "class": "B",
            "status": "mismatch:commit-absent",
            "detail": f"git cat-file -e {token}^{{commit}} failed"}


def resolve_digest(root, rev, lineno, token, path):
    rp = git(root, "cat-file", "blob", f"{rev}:{path}")
    if rp.returncode != 0:
        return {"line": lineno, "token": token, "class": "C",
                "status": "mismatch:path-absent",
                "detail": f"digest undefined; {path} absent at {rev}"}
    actual = hashlib.sha256(rp.stdout).hexdigest()
    if actual == token:
        return {"line": lineno, "token": token, "class": "C",
                "status": "resolved", "detail": f"sha256 matches {path}"}
    return {"line": lineno, "token": token, "class": "C",
            "status": "mismatch:digest-mismatch",
            "detail": f"sha256={actual} for {path}"}


def evaluate(root, rel_file, rev):
    tracked = tracked_files(root, rev)
    text, source = read_declaration(root, rel_file, rev)
    tracked_set = set(tracked)
    assertions = []
    skipped = []
    fenced = False
    for lineno, raw_line in enumerate(text.decode("utf-8", "replace").split("\n"), 1):
        line = raw_line.rstrip("\r")
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        spans = [(match.start(), match.end(), match.group(1))
                 for match in SPAN_RE.finditer(line)]
        cells = split_cells(line) if is_table_row(line) else []
        # Backticked whole-span paths per cell, for class C adjacency.
        cell_paths = {}
        for start, _end, content in spans:
            index = cell_index(cells, start)
            if index is None:
                continue
            stripped = content.strip()
            if stripped and not has_whitespace(stripped) and EXT_TAIL_RE.search(stripped):
                cell_paths.setdefault(index, []).append(stripped)
        for start, _end, content in spans:
            stripped = content.strip()
            if not stripped:
                continue
            if has_whitespace(stripped):
                # A command span.  Its inner path-shaped words are seen and
                # excluded here, not silently dropped.
                for word in stripped.split():
                    if EXT_TAIL_RE.search(word):
                        skipped.append({"line": lineno, "token": word, "class": "-",
                                        "status": "skipped",
                                        "detail": "path token inside a command span"})
                continue
            if EXT_TAIL_RE.search(stripped):
                row, skip = resolve_path(root, rev, tracked, tracked_set,
                                         lineno, stripped)
                if row:
                    assertions.append(row)
                if skip:
                    skipped.append(skip)
                continue
            if PURE_HEX_RE.fullmatch(stripped):
                # Cell-scoped hex is enumerated by the cell scan below so a
                # token is counted once.  Only a prose token is handled here.
                if cell_index(cells, start) is None:
                    skipped.append({"line": lineno, "token": stripped, "class": "-",
                                    "status": "skipped",
                                    "detail": "hex token outside a table cell "
                                              "(class B/C are cell-scoped)"})
        for index, (_start, _end, cell_text) in enumerate(cells):
            paths = cell_paths.get(index, [])
            for match in HEX_TOKEN_RE.finditer(cell_text):
                token = match.group(1)
                length = len(token)
                if length == 64:
                    if len(paths) == 1:
                        assertions.append(resolve_digest(root, rev, lineno, token,
                                                         paths[0]))
                    else:
                        skipped.append({
                            "line": lineno, "token": token, "class": "-",
                            "status": "skipped",
                            "detail": f"64-hex digest cell names {len(paths)} "
                                      "backticked paths (class C needs exactly one)"})
                elif length <= 40:
                    if revision_context(cell_text):
                        assertions.append(resolve_commit(root, lineno, token))
                    else:
                        skipped.append({
                            "line": lineno, "token": token, "class": "-",
                            "status": "skipped",
                            "detail": "hex token in a table cell with no revision context"})
                else:
                    skipped.append({
                        "line": lineno, "token": token, "class": "-",
                        "status": "skipped",
                        "detail": f"hex token length {length}: not 7..40 (B) "
                                  "and not 64 (C)"})
    assertions.sort(key=lambda row: (row["line"], row["token"]))
    skipped.sort(key=lambda row: (row["line"], row["token"]))
    counts = {
        "assertions": len(assertions),
        "resolved": sum(1 for row in assertions if row["status"] == "resolved"),
        "skipped": len(skipped),
        "mismatches": sum(1 for row in assertions
                          if row["status"].startswith("mismatch")),
    }
    if counts["assertions"] != counts["resolved"] + counts["mismatches"]:
        raise ToolError("internal invariant violated: N != R + M")
    return assertions, skipped, counts, source


def counts_line(counts):
    return ("assertions={assertions} resolved={resolved} skipped={skipped} "
            "mismatches={mismatches}".format(**counts))


def exit_for(counts):
    return 0 if counts["mismatches"] == 0 else 1


def format_tsv(rows):
    return "\n".join("\t".join(str(row[key]) for key in
                               ("line", "token", "class", "status", "detail"))
                     for row in rows)


# ---------------------------------------------------------------------------
# selftest: five fixtures on a synthetic repository under /var/tmp
# ---------------------------------------------------------------------------

def write_file(root, relative, content):
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def commit_all(root, message):
    git(root, "add", "-A")
    rp = git(root, "commit", "-q", "-m", message)
    if rp.returncode != 0:
        raise ToolError("selftest commit failed: "
                        + rp.stderr.decode(errors="replace"))


def selftest():
    scratch = tempfile.mkdtemp(prefix="souji-declared-evidence-", dir=SCRATCH_PARENT)
    if not scratch.startswith(SCRATCH_PARENT + "/"):
        shutil.rmtree(scratch, ignore_errors=True)
        raise ToolError("scratch directory escaped /var/tmp")
    repo = os.path.join(scratch, "repo")
    checks = []
    try:
        os.makedirs(repo)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "selftest")
        git(repo, "config", "user.email", "selftest@example.invalid")
        git(repo, "config", "commit.gpgsign", "false")
        write_file(repo, "docs/a.md", "alpha\n")
        write_file(repo, "docs/old-only.md", "old\n")
        write_file(repo, "tools/ok.py", "print(1)\n")
        write_file(repo, "census/round-1/one.json", "{}\n")
        commit_all(repo, "base")
        rev1 = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
        write_file(repo, "census/round-2/two.json", "{}\n")
        os.remove(os.path.join(repo, "docs/old-only.md"))
        commit_all(repo, "second")
        rev2 = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
        digest = hashlib.sha256(git(repo, "cat-file", "blob",
                                    f"{rev2}:docs/a.md").stdout).hexdigest()
        wrong_digest = hashlib.sha256(b"not the file").hexdigest()
        dangling = "0123456789abcdef0123456789abcdef01234567"

        fixtures = {
            "fixtures/good.md":
                "# good\n\n| axis | evidence |\n|---|---|\n"
                "| a | paths present `docs/a.md`, `census/round-2/two.json` |\n"
                f"| b | measured commit {rev2} |\n"
                f"| c | digest `docs/a.md` {digest} |\n",
            "fixtures/missing-path.md":
                "# bad path\n\n| axis | evidence |\n|---|---|\n"
                "| a | absent `docs/nope.md` |\n",
            "fixtures/dangling-rev.md":
                "# bad revision\n\n| axis | evidence |\n|---|---|\n"
                f"| a | measured commit {dangling} |\n",
            "fixtures/wrong-digest.md":
                "# bad digest\n\n| axis | evidence |\n|---|---|\n"
                f"| a | digest `docs/a.md` {wrong_digest} |\n",
            "fixtures/other-rev.md":
                "# path only at an earlier revision\n\n"
                "| axis | evidence |\n|---|---|\n"
                "| a | historical `docs/old-only.md` |\n",
        }
        for relative, content in fixtures.items():
            write_file(repo, relative, content)
        commit_all(repo, "fixtures")
        rev3 = git(repo, "rev-parse", "HEAD").stdout.decode().strip()

        def run(relative):
            return evaluate(repo, relative, rev3)

        def report(label, relative, want):
            assertions, _skipped, counts, _source = run(relative)
            ok = (counts["mismatches"] == 0) if want == 0 else (counts["mismatches"] >= 1)
            checks.append(ok)
            print(f"fixture {label:<34} {counts_line(counts)} "
                  f"(want mismatches {'0' if want == 0 else '>0'}) "
                  f"{'PASS' if ok else 'FAIL'}")
            return assertions, counts

        # Fixture 1 must also exercise all three frozen classes: a parser that
        # silently drops B or C could still print mismatches=0.
        good_rows, good = report("1 all-good", "fixtures/good.md", 0)
        classes = {row["class"] for row in good_rows}
        good_ok = good["assertions"] == 5 and classes == {"A", "B", "C"}
        checks[0] = checks[0] and good_ok
        print(f"fixture 1 class coverage{'':<21} "
              f"assertions={good['assertions']} classes={sorted(classes)} "
              f"{'PASS' if good_ok else 'FAIL'}")

        red_specs = [
            ("2 nonexistent path", "fixtures/missing-path.md"),
            ("3 dangling revision", "fixtures/dangling-rev.md"),
            ("4 wrong digest", "fixtures/wrong-digest.md"),
            ("5 path only at other rev", "fixtures/other-rev.md"),
        ]
        for label, relative in red_specs:
            report(label, relative, 1)

        # The always-zero control reads nothing; it must fail every red
        # fixture, otherwise the kill rule would accept a false green.
        control = {"assertions": 0, "resolved": 0, "skipped": 0, "mismatches": 0}
        control_ok = all(control["mismatches"] < 1 for _label, _relative in red_specs)
        checks.append(control_ok)
        print(f"control always-zero rejected{'':<14} "
              f"{'PASS' if control_ok else 'FAIL'} ({len(red_specs)}/{len(red_specs)} "
              f"red fixtures reject mismatches=0)")

        line_ok = bool(re.fullmatch(
            r"assertions=\d+ resolved=\d+ skipped=\d+ mismatches=\d+",
            counts_line(good)))
        checks.append(line_ok)
        print(f"counts line format{'':<25} "
              f"{'PASS' if line_ok else 'FAIL'} ({counts_line(good)})")

        exit_ok = (exit_for(dict(good, mismatches=0)) == 0
                   and exit_for(dict(good, mismatches=2)) == 1)
        checks.append(exit_ok)
        print(f"exit-code semantics{'':<22} "
              f"{'PASS' if exit_ok else 'FAIL'} (M=0 -> 0, M=2 -> 1)")

        passed = sum(1 for ok in checks if ok)
        print(f"selftest {passed}/{len(checks)} {'PASS' if passed == len(checks) else 'FAIL'}")
        if passed == len(checks):
            print("control=FALSE-GREEN-REJECTED")
        return 0 if passed == len(checks) else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="re-derive a self-assessment file's declared evidence "
                    "from committed bytes at a named revision")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--file", help="declaration file, repo-relative")
    parser.add_argument("--rev", help="revision the assertions resolve against")
    parser.add_argument("--format", choices=("counts", "tsv", "skips"),
                        default="counts",
                        help="counts (default), tsv assertions, or skips "
                             "(diagnostic extension: excluded candidates)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        try:
            return selftest()
        except ToolError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
    if not args.file or not args.rev:
        parser.error("--file and --rev are required unless --selftest")
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return 2
    try:
        assertions, skipped, counts, source = evaluate(root, args.file, args.rev)
    except ToolError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if source.startswith("worktree:"):
        print(f"note: declaration read from {source}", file=sys.stderr)
    if args.format == "tsv":
        if assertions:
            print(format_tsv(assertions))
    elif args.format == "skips":
        if skipped:
            print(format_tsv(skipped))
    print(counts_line(counts))
    return exit_for(counts)


if __name__ == "__main__":
    sys.exit(main())
