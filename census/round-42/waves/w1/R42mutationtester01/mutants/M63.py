#!/usr/bin/env python3
"""census/round-42/c1-counter.py — r42 C1 (calibration): the SCORECARD's own unresolvable declared-evidence assertions, accounted for.

Claim. `tools/souji-declared-evidence.py` (r22) re-derives the machine-checkable assertions of a
self-assessment file from committed bytes. Run over `SCORECARD.md` at the round-42 base revision
BASE it prints `assertions=474 resolved=404 skipped=780 mismatches=70`: seventy declared-evidence
tokens the lane's own instrument cannot resolve. The frozen population `census/round-42/c1-items.tsv`
holds those 70 rows (line, token, class, result, detail). The claim is that after the round every one
of the 70 is ACCOUNTED FOR and the genuinely wrong ones are CORRECTED, append-only:

  register   `census/round-42/c1-register.tsv` (tab separated, header `line token class resolved_to`)
             holds exactly one row per item (a token cited twice on one line is two items and two identical rows). `class` is `resolved` (the token is a shorthand for a
             committed path; `resolved_to` names it) or `unresolved` (`resolved_to` is `-`).
  derivation the counter derives each item's class itself, from the BASE tree and the BASE
             SCORECARD.md, with the fixed rules below, and the register row must agree exactly.
  correction every item the counter derives as `unresolved` needs exactly one line
             `CORRECTION-DE line=<n> token=<tok> derived=<D> rev=<BASE>` in
             `corpus/lessons/round-42.md` (outside code fences; a duplicate, fenced, unmatched or
             malformed CORRECTION-DE line is `junk`). D is `rev-unresolved`, `path-absent`, or
             `sha256=<hex>` (the actual digest from the item's `detail`), by the item's `result`.
  append-only SCORECARD.md at REV keeps every BASE line byte-identical (`rewritten=0`) and the BASE
             tool run at REV reports no mismatch on a line beyond the BASE line count
             (`new_mismatches=0`): rows added this round must cite paths the instrument resolves.

Fixed derivation rules (first match wins; "tree" is `git ls-tree -r --name-only BASE`):
  R1  token `.ufo/waves/round-<N>/<rest>`  -> `census/round-<N>/waves/<rest>` when that path is in the tree
  R2  the paths of the tree that end with `/<token>` (or equal it) and contain `round-<C>/`, where C is
      the round number of the nearest heading line (`#`..`####`, contains `Round <C>`) above the item's
      SCORECARD line; exactly one match -> resolved to it. (When several match and some lie under
      `/waves/`, the non-`/waves/` matches are the candidate set.)
  R3  exactly one path of the tree ends with `/<token>` or equals it -> resolved to it
  R4  a bare token whose basename is `corpus/knowledge/<token>` in the tree -> resolved to it
  otherwise `unresolved`. Rev and digest items (`result` mismatch:rev-unresolved / mismatch:digest)
  are always `unresolved`: they are not paths.

Controls scored by this same counter: absent register (`registered=0`), and a forged register that
labels every item `resolved` (`class_ok` falls short).

CLI:
  python3 -B census/round-42/c1-counter.py --root LANE --rev FULL40 [--base FULL40] [--scratch DIR]
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate (bad rev/base, tool or items absent, scratch).
Target (K = number of items the derivation marks unresolved; frozen in the preregistration):
  `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=K corrected=K junk=0 rewritten=0 new_mismatches=0`
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
TOOL = "tools/souji-declared-evidence.py"
ITEMS = "census/round-42/c1-items.tsv"
REGISTER = "census/round-42/c1-register.tsv"
LESSON = "corpus/lessons/round-42.md"
SCORECARD = "SCORECARD.md"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
HEADING = re.compile(r"^#{1,4}\s.*?\bRound\s+(\d+)\b")
CORR = re.compile(r"^CORRECTION-DE line=(\d+) token=(\S+) derived=(\S+) rev=([0-9a-f]{40})\s*$")


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git(root, scratch, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env(scratch), check=False)


def show(root, rev, path, scratch):
    p = git(root, scratch, "show", "%s:%s" % (rev, path))
    return p.stdout if p.returncode != 0 else None


def resolves(root, rev, scratch):
    return git(root, scratch, "cat-file", "-e", rev + "^{commit}").returncode == 0


def parse_items(blob):
    rows = []
    for n, line in enumerate(blob.decode("utf-8").split("\n")):
        if n == 0 or not line.strip():
            continue
        f = line.split("\t")
        if len(f) < 5:
            return None
        rows.append((int(f[0]), f[1], f[2], f[3], f[4]))
    return rows


def derive(item, tree, context):
    line, tok, _cls, result, _detail = item
    if result != "mismatch:path-absent":
        return ("unresolved", "-")
    m = re.match(r"^\.ufo/waves/round-(\d+)/(.*)$", tok)
    if m:
        cand = "census/round-%s/waves/%s" % (m.group(1), m.group(2))
        if cand in tree:
            return ("resolved", cand)
    ends = sorted(p for p in tree if p == tok or p.endswith("/" + tok))
    ctx = context.get(line)
    if ctx is not None:
        sel = [p for p in ends if ("round-%d/" % ctx) in p]
        if len(sel) > 1:
            non_waves = [p for p in sel if "/waves/" not in p]
            sel = non_waves or sel
        if len(sel) == 1:
            return ("resolved", sel[0])
    if len(ends) == 1:
        return ("resolved", ends[0])
    k = "corpus/knowledge/" + tok
    if "/" not in tok and k in tree:
        return ("resolved", k)
    return ("unresolved", "-")


def wanted_correction(item):
    _line, _tok, _cls, result, detail = item
    if result == "mismatch:rev-unresolved":
        return "rev-unresolved"
    if result == "mismatch:digest":
        m = re.search(r"sha256 is ([0-9a-f]{64})", detail)
        return "sha256=" + m.group(1) if m else "sha256=?"
    return "path-absent"


def run_tool(tool, root, rev, scratch):
    p = subprocess.run(["python3", "-B", tool, "--root", root, "--rev", rev, "--file", SCORECARD,
                        "--format", "tsv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, env=env(scratch), check=False, timeout=600)
    rows = []
    for line in p.stdout.split("\n"):
        f = line.split("\t")
        if len(f) >= 5 and f[3].startswith("mismatch"):
            rows.append((int(f[0]), f[1], f[2], f[3], f[4]))
    return rows, p.returncode


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    scratch_root = args.scratch or os.environ.get("TMPDIR")
    if not scratch_root or not os.path.isdir(scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory\n")
        return 2
    for label, rev in (("--rev", args.rev), ("--base", args.base)):
        if not REV.match(rev) or not resolves(args.root, rev, scratch_root):
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s must name a resolvable full40 commit\n" % label)
            return 2
    scratch = tempfile.mkdtemp(prefix="souji-r42-c1.", dir=scratch_root)
    try:
        tool_b = show(args.root, args.base, TOOL, scratch_root)
        items_b = show(args.root, args.rev, ITEMS, scratch_root)
        score_b = show(args.root, args.base, SCORECARD, scratch_root)
        if tool_b is None or items_b is None or score_b is None:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: tool at base, items at rev or SCORECARD at base absent\n")
            return 2
        items = parse_items(items_b)
        if items is None:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: items table malformed\n")
            return 2
        tool = os.path.join(scratch, "declared-evidence.py")
        with open(tool, "wb") as handle:
            handle.write(tool_b)
        base_rows, _rc = run_tool(tool, args.root, args.base, scratch)
        population = "ok" if sorted(base_rows) == sorted(items) else "DRIFT"
        tp = git(args.root, scratch_root, "ls-tree", "-r", "--name-only", args.base)
        tree = set(tp.stdout.decode("utf-8").split("\n")) - {""}
        base_lines = score_b.decode("utf-8").split("\n")
        context, cur = {}, None
        for n, text in enumerate(base_lines, 1):
            m = HEADING.match(text)
            if m:
                cur = int(m.group(1))
            context[n] = cur
        reg_b = show(args.root, args.rev, REGISTER, scratch_root)
        register = {}
        if reg_b is not None:
            for n, text in enumerate(reg_b.decode("utf-8").split("\n")):
                f = text.split("\t")
                if n == 0 or len(f) != 4:
                    continue
                register.setdefault((f[0], f[1]), []).append((f[2], f[3]))
        registered = class_ok = unresolved = 0
        wants = {}
        multiplicity = {}
        for item in items:
            multiplicity[(str(item[0]), item[1])] = multiplicity.get((str(item[0]), item[1]), 0) + 1
        for item in items:
            key = (str(item[0]), item[1])
            cls, path = derive(item, tree, context)
            if cls == "unresolved":
                unresolved += 1
                wants[(item[0], item[1])] = wanted_correction(item)
            got = register.get(key, [])
            # one register row per item: a token cited twice on one line is two items and two identical rows
            if len(got) == multiplicity[key]:
                registered += 1
                gc, gp = got[0]
                if all(g == (cls, path) for g in got) and (
                        cls == "unresolved" or git(args.root, scratch_root, "cat-file", "-e",
                                                   "%s:%s" % (args.rev, path)).returncode == 0):
                    class_ok += 1
        lesson_b = show(args.root, args.rev, LESSON, scratch_root)
        seen, junk, fenced = {}, 0, False
        if lesson_b is not None:
            for text in lesson_b.decode("utf-8").split("\n"):
                if text.lstrip().startswith("```"):
                    fenced = not fenced
                    if "CORRECTION-DE" in text:
                        junk += 1
                    continue
                if "CORRECTION-DE" not in text:
                    continue
                m = CORR.match(text)
                if fenced or not m or m.group(4) != args.base:
                    junk += 1
                    continue
                key = (int(m.group(1)), m.group(2))
                if key in seen or key not in wants or m.group(3) != wants[key]:
                    junk += 1
                    continue
                seen[key] = True
        corrected = len(seen)
        rev_b = show(args.root, args.rev, SCORECARD, scratch_root)
        rewritten = len(base_lines)
        new_mismatches = -1
        if rev_b is not None:
            rev_lines = rev_b.decode("utf-8").split("\n")
            rewritten = sum(1 for i, b in enumerate(base_lines) if i >= len(rev_lines) or rev_lines[i] != b)
            now_rows, _rc = run_tool(tool, args.root, args.rev, scratch)
            new_mismatches = sum(1 for r in now_rows if r[0] > len(base_lines))
        print("SUMMARY items=%d population=%s registered=%d class_ok=%d unresolved=%d corrected=%d junk=%d "
              "rewritten=%d new_mismatches=%d" % (len(items), population, registered, class_ok, unresolved,
                                                  corrected, junk, rewritten, new_mismatches))
        met = (len(items) == 70 and population == "ok" and registered == 70 and class_ok == 70
               and corrected == unresolved and junk == 0 and rewritten == 0 and new_mismatches == 0)
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
