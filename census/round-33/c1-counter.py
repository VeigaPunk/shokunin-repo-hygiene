#!/usr/bin/env python3
"""r33 C1 calibration counter (frozen at the r33 preregistration): capability-table currency.

Question: does the lane's self-assessment in SCORECARD.md (each capability row that names a runnable command and its
stated outcome) agree with what that command does at the measured revision?

Items: `census/round-33/c1-items.tsv`, read at --list-rev (never at --rev). Each item = one (command, stated outcome)
pair of a capability row at the r33 base (rule in that file's header).

Self-assessment read at --rev:
  * by default the item's original row (SCORECARD.md:<line>) is the statement, with the item's frozen predicate and exit;
  * an item is RESTATED by exactly one row in the appended section `### Round 33 capability currency` of SCORECARD.md
    at --rev, of the form
      | Kxx | SCORECARD.md:<line> | restated | <exit> | <run> | `<statement>` | <cause full40> | <reason> |
    <line> must equal the item's line; <exit> an integer; <run> is `same` (the item's frozen argv) or a backticked
    argv (lane-relative command; `{SCRATCH}` allowed); <statement> must equal, whitespace-collapsed, ONE complete line
    of the run's stdout or stderr, and that line must carry a digit (RESULTS items: `RESULTS:<path>:<n>`, judged as
    the frozen RESULTS predicate); <cause> must be a full 40-hex commit that is an ancestor of --list-rev with a
    parent, <reason> non-empty, and the cause is executed:
      - <run> `same` (value drift): the cause's `git show --name-only` names one of the item's frozen files, the item's
        frozen argv satisfies its frozen exit+predicate at the cause's first parent, and fails them at the cause (the
        commit where the original statement stopped being true);
      - <run> backticked (argv correction): the item's SCORECARD.md line text (at --list-rev) is absent from
        SCORECARD.md at the cause's parent and present at the cause (the cause wrote the row), and the item's frozen
        argv already fails its frozen exit+predicate at the cause (the row's command never produced its outcome).
  * SCORECARD.md at --rev must start with the bytes of SCORECARD.md at --list-rev (append-only), else
    COULD-NOT-EVALUATE.

Run: one private clone per item (`git clone --no-local --no-checkout`, origin removed, detached at --rev), cwd = the
clone root, environment = the caller's plus TMPDIR=<fresh dir under --scratch> and GIT_CONFIG_NOSYSTEM=1, timeout
--timeout seconds (expiry = exit 124).

Verdict per item: AGREE iff the run's exit equals the stated exit (`*` = any) AND the stated predicate holds;
otherwise MISMATCH (reason). A malformed, duplicated or misplaced restatement row is a MISMATCH (BAD-ROW).
Output: one ITEM line per item, then
    SUMMARY items=<n> agree=<a> mismatches=<m> restated=<r> rev=<REV>
Frozen target (preregistration): `mismatches=0` at the C1 landing commit and at the tip.
Exit 0 iff mismatches=0; 1 otherwise; 2 could-not-evaluate. Read-only on --root.
"""
import argparse
import concurrent.futures as cf
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
ITEMS_PATH = "census/round-33/c1-items.tsv"
SECTION = "### Round 33 capability currency"
ROW = re.compile(r"^\| (K\d{2}) \| (.*) \|\s*$")


def cne(msg):
    print(f"COULD-NOT-EVALUATE {msg}")
    sys.exit(2)


def git(root, *a, check=True):
    p = subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *a],
                       capture_output=True)
    if check and p.returncode:
        cne("git " + " ".join(a) + ": " + p.stderr.decode("utf-8", "replace").strip())
    return p


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return None if p.returncode else p.stdout


def collapse(s):
    return " ".join(s.split())


def load_items(root, list_rev):
    raw = blob(root, list_rev, ITEMS_PATH)
    if raw is None:
        cne(f"{ITEMS_PATH} absent at --list-rev")
    items = []
    for ln in raw.decode().splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        f = ln.split("\t")
        if len(f) != 6:
            cne(f"malformed item line: {ln!r}")
        iid, line, exit_, pred, files, argv = f
        items.append({"id": iid, "line": int(line), "exit": exit_, "pred": pred,
                      "files": [x for x in files.split(",") if x], "argv": argv})
    return items


def load_restatements(text):
    """Return {id: [cells, ...]} for rows under SECTION (until the next heading)."""
    rows = {}
    inside = False
    for ln in text.splitlines():
        if ln.startswith("#"):
            inside = ln.startswith(SECTION)
            continue
        if not inside:
            continue
        m = ROW.match(ln)
        if m:
            cells = [c.strip() for c in ("| " + m.group(2) + " |").strip("|").split(" | ")]
            rows.setdefault(m.group(1), []).append([c.strip() for c in cells])
    return rows


def results_pred(spec, out_lines, clone):
    m = re.fullmatch(r"RESULTS:([^:]+):(\d+)", spec)
    if not m:
        return False, "bad RESULTS spec"
    path, n = m.group(1), int(m.group(2))
    try:
        rec = open(os.path.join(clone, path), errors="replace").read().splitlines()
    except OSError:
        return False, f"record {path} unreadable"
    want = [x for x in rec if x.startswith("RESULT ")]
    got = [x for x in out_lines if x.startswith("RESULT ")]
    if len(want) != n:
        return False, f"record has {len(want)} RESULT lines, stated {n}"
    if got != want:
        return False, f"RESULT lines differ (got {len(got)}, record {len(want)})"
    return True, f"RESULT lines {n}/{n} equal"


def frozen_pred(pred, out, err, clone):
    """Alternatives ` || `, each a conjunction ` && ` of regexes over the collapsed text or one RESULTS part."""
    flat = collapse(out + "\n" + err)
    whys = []
    for alt in pred.split(" || "):
        ok = True
        for part in alt.split(" && "):
            part = part.strip()
            if part.startswith("RESULTS:"):
                r, why = results_pred(part, out.splitlines(), clone)
                whys.append(why)
                ok = ok and r
            else:
                ok = ok and bool(re.search(part, flat))
        if ok:
            return True, "predicate holds" + (f" ({whys[-1]})" if whys else "")
    return False, "predicate fails" + (f" ({whys[-1]})" if whys else "")


def run_item(item, argv, root, rev, work):
    d = tempfile.mkdtemp(prefix=item["id"] + ".", dir=work)
    clone = os.path.join(d, "c")
    tmp = os.path.join(d, "tmp")
    os.makedirs(tmp)
    os.makedirs(os.path.join(d, "s"))
    try:
        p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], capture_output=True)
        if p.returncode:
            return None, "", "", clone, "clone failed"
        git(clone, "remote", "remove", "origin")
        git(clone, "checkout", "-qf", "--detach", rev)
        if git(clone, "rev-parse", "--show-toplevel").stdout.decode().strip() != clone:
            return None, "", "", clone, "clone toplevel mismatch"
        cmd = argv.replace("{SCRATCH}", shlex.quote(os.path.join(d, "s")))
        env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")
        for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            env.pop(k, None)
        try:
            q = subprocess.run(["bash", "-c", cmd], cwd=clone, env=env, capture_output=True, timeout=ARGS.timeout)
            rc, out, err = q.returncode, q.stdout.decode("utf-8", "replace"), q.stderr.decode("utf-8", "replace")
        except subprocess.TimeoutExpired as e:
            rc, out, err = 124, (e.stdout or b"").decode("utf-8", "replace"), (e.stderr or b"").decode("utf-8", "replace")
        return rc, out, err, clone, None
    except SystemExit:
        return None, "", "", clone, "git failure"

def holds(item, argv, orig, root, rev, work):
    """True/False: does the frozen (exit, predicate) hold for argv at rev; None when the run itself failed."""
    rc, out, err, clone, fail = run_item(item, argv, root, rev, work)
    if fail:
        return None
    exit_, pred = orig
    return (exit_ == "*" or rc == int(exit_)) and frozen_pred(pred, out, err, clone)[0]



def judge(item, rest, root, list_rev, rev, work):
    iid = item["id"]
    rows = rest.get(iid, [])
    if len(rows) > 1:
        return iid, False, "BAD-ROW(duplicate restatement)", "restated"
    status = "original"
    argv, exit_, pred, stmt = item["argv"], item["exit"], item["pred"], None
    if rows:
        status = "restated"
        c = rows[0]
        if len(c) != 7:
            return iid, False, f"BAD-ROW(cells={len(c)})", status
        where, kind, rexit, rrun, rstmt, cause, reason = c
        if where != f"SCORECARD.md:{item['line']}" or kind != "restated":
            return iid, False, "BAD-ROW(line or kind)", status
        if not re.fullmatch(r"-?\d+", rexit):
            return iid, False, "BAD-ROW(exit)", status
        exit_ = rexit
        if rrun != "same":
            m = re.fullmatch(r"`([^`]+)`", rrun)
            if not m:
                return iid, False, "BAD-ROW(run)", status
            argv = m.group(1)
        m = re.fullmatch(r"`([^`]+)`", rstmt)
        if not m:
            return iid, False, "BAD-ROW(statement)", status
        stmt = m.group(1)
        if not FULL.fullmatch(cause):
            return iid, False, "BAD-ROW(cause not full40)", status
        if git(root, "merge-base", "--is-ancestor", cause, list_rev, check=False).returncode:
            return iid, False, "BAD-ROW(cause not an ancestor of the list revision)", status
        if not reason.strip():
            return iid, False, "BAD-ROW(empty reason)", status
        parent = git(root, "rev-parse", "--verify", "-q", cause + "^1", check=False).stdout.decode().strip()
        if not FULL.fullmatch(parent):
            return iid, False, "BAD-ROW(cause has no parent)", status
        orig = (item["exit"], item["pred"])
        if rrun == "same":
            # value drift: the stated outcome held at the cause's parent and stopped holding at the cause
            names = git(root, "show", "--name-only", "--format=", cause, check=False).stdout.decode().split()
            if not set(names) & set(item["files"]):
                return iid, False, "BAD-ROW(cause touches none of the item files)", status
            held = holds(item, item["argv"], orig, root, parent, work)
            stops = holds(item, item["argv"], orig, root, cause, work)
            if held is not True or stops is not False:
                return iid, False, f"BAD-CAUSE(original at parent={held} at cause={stops}; need True/False)", status
        else:
            # argv correction: the cause wrote the row's line, and the row's own argv already failed there
            line_text = blob(root, list_rev, "SCORECARD.md").decode("utf-8", "replace").split("\n")[item["line"] - 1]
            before = blob(root, parent, "SCORECARD.md") or b""
            after = blob(root, cause, "SCORECARD.md") or b""
            if line_text in before.decode("utf-8", "replace").split("\n") or \
                    line_text not in after.decode("utf-8", "replace").split("\n"):
                return iid, False, "BAD-CAUSE(cause did not write the row's line)", status
            if holds(item, item["argv"], orig, root, cause, work) is not False:
                return iid, False, "BAD-CAUSE(the row's own argv held at the cause)", status
    rc, out, err, clone, fail = run_item(item, argv, root, rev, work)
    if fail:
        return iid, False, f"RUN-FAILED({fail})", status
    lines = out.splitlines() + err.splitlines()
    exit_ok = exit_ == "*" or rc == int(exit_)
    if stmt is None:
        ok, why = frozen_pred(pred, out, err, clone)
    elif stmt.startswith("RESULTS:"):
        ok, why = results_pred(stmt, out.splitlines(), clone)
    else:
        target = collapse(stmt)
        ok = bool(re.search(r"\d", target)) and any(collapse(x) == target for x in lines)
        why = "statement is an output line" if ok else "statement is not a digit-bearing output line"
    last = next((collapse(x) for x in reversed(lines) if re.search(r"\d", x)), "NONE")[:200]
    verdict = exit_ok and ok
    detail = f"rc={rc} expect_exit={exit_} {why} last={last}"
    return iid, verdict, detail, status


def main():
    global ARGS
    ap = argparse.ArgumentParser(prog="c1-counter.py")
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-33/c1-items.tsv")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only", default="")
    ARGS = a = ap.parse_args()
    root = os.path.abspath(a.root)
    for name in ("rev", "list_rev"):
        if not FULL.fullmatch(getattr(a, name)):
            cne(f"--{name.replace('_', '-')} must be a full 40-hex revision")
        git(root, "cat-file", "-e", getattr(a, name) + "^{commit}")
    scratch = os.path.abspath(a.scratch)
    for bad in ("/tmp", "/var/tmp", "/dev/shm"):
        if scratch == bad or scratch.startswith(bad + "/"):
            cne("--scratch must not be under /tmp, /var/tmp or /dev/shm")
    items = load_items(root, a.list_rev)
    base_sc = blob(root, a.list_rev, "SCORECARD.md")
    rev_sc = blob(root, a.rev, "SCORECARD.md")
    if base_sc is None or rev_sc is None:
        cne("SCORECARD.md absent")
    if not rev_sc.startswith(base_sc):
        cne("SCORECARD.md at --rev does not start with its --list-rev bytes (not append-only)")
    rest = load_restatements(rev_sc.decode("utf-8", "replace"))
    only = set(x for x in a.only.split(",") if x)
    if only - {i["id"] for i in items}:
        cne("unknown --only ids")
    sel = [i for i in items if not only or i["id"] in only]
    os.makedirs(scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="c1.", dir=scratch)
    try:
        with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            res = list(ex.map(lambda it: judge(it, rest, root, a.list_rev, a.rev, work), sel))
    finally:
        subprocess.run(["chmod", "-R", "u+w", work], capture_output=True)
        shutil.rmtree(work, ignore_errors=True)
    agree = mism = restated = 0
    for iid, ok, detail, status in res:
        agree += ok
        mism += not ok
        restated += status == "restated"
        print(f"ITEM\t{iid}\t{'AGREE' if ok else 'MISMATCH'}\t{status}\t{detail}")
    partial = " partial=1" if only else ""
    print(f"SUMMARY items={len(sel)} agree={agree} mismatches={mism} restated={restated}{partial} rev={a.rev}")
    return 0 if mism == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
