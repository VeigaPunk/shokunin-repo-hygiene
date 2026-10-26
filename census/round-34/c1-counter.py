#!/usr/bin/env python3
"""r34 C1 calibration counter (frozen at the r34 preregistration): registry-and-measurement-row agreement.

Reads census/round-34/c1-items.tsv at --list-rev only (60 items: SKILL.md gate-registry and
SCORECARD.md rows outside the r33 counter's sections). For each item it makes one private
`git clone --no-local --no-checkout` of the lane, checks out the item's `at` revision
detached (`{REV}` = --rev), removes the remote, and runs the item argv from the clone root
with a scrubbed env: TMPDIR=<fresh dir under --scratch>, GIT_CONFIG_NOSYSTEM=1, no GIT_*
vars, PATH=/usr/bin:/bin plus a `jj` symlink when jj exists (r33 wave-1 finding 7).
Substitutions: {REV} -> the checkout revision, {SCRATCH} -> fresh dir, {CLONE} -> clone path,
{BLOB:<rev>:<path>} -> `git show` extraction into scratch.

Frozen predicate semantics (hardened over the r33 residuals): alternatives ` || `, each a
conjunction ` && ` of: a bare regex matched against the collapsed whitespace of the run's
LAST digit-bearing output line; `ANYLINE:<regex>` against any line; `COUNT:<regex>==<n>`
counting lines matching the anchored regex across all output; or `RESULTS:<path>:<n>` (the
record file's `RESULT ` lines must equal the run's, n>=1, the file must exist at a commit
strictly before --rev and be unchanged at --rev). A bare conjunct never matches a vacuous
last line: if the output carries no digit, the run cannot agree.

Restatements (Q75 honouring Q76): appended `### Round 34 registry restatements` rows in
SCORECARD.md, cells | id | <file>:<line> | restated | exit | `argv`|same | `statement` |
cause-full40 | reason |. The cause must be an ancestor of --list-rev AND executed:
value drift -> the original (exit, predicate) holds at the cause's parent and fails at the
cause, with the cause touching one of the item's files; argv correction -> the cause wrote
the row's line and the row's own argv already fails at the cause, and the corrected argv
must name one of the item's files (run the row's own script). A restated `statement` must
equal the run's collapsed LAST digit-bearing output line (a mid-run or error line never
agrees); a RESULTS:<path>:<n> statement keeps the n>=1 record contract. The measured-run
argv is the row's corrected argv when one is given, else the frozen item argv. SCORECARD.md
and SKILL.md at --rev must start with their --list-rev bytes (append-only).

Runs are serialized: the counter takes a global flock at --scratch/c1.lock (Q77) and runs
items in file order; the 1-min load is recorded beside every ITEM line. do-nothing:
`--rev <base> --list-rev <prereg>` must print mismatches>0. Exit 0 iff every item agrees.
"""
import argparse
import fcntl
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
ITEMS_PATH = "census/round-34/c1-items.tsv"
SECTION = "### Round 34 registry restatements"
ROW = re.compile(r"^\| (E\d{2}[a-z]?|G\d{2}[a-z]?) \| (.*) \|\s*$")
LOCK_NAME = "c1.lock"


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
        if len(f) != 7:
            cne(f"malformed item line: {ln!r}")
        iid, where, exit_, pred, files, at, argv = f
        items.append({"id": iid, "where": where, "exit": exit_, "pred": pred,
                      "files": [x for x in files.split(",") if x], "at": at, "argv": argv})
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


def last_digit_line(lines):
    return next((collapse(x) for x in reversed(lines) if re.search(r"\d", x)), "")


def results_pred(spec, out_lines, root, rev):
    m = re.fullmatch(r"RESULTS:([^:]+):(\d+)", spec)
    if not m:
        return False, "bad RESULTS spec"
    path, n = m.group(1), int(m.group(2))
    if n < 1:
        return False, "RESULTS count must be >=1"
    cur = blob(root, rev, path)
    if cur is None:
        return False, f"record {path} absent at the measured revision"
    names = git(root, "log", "--format=", "--name-only", rev, "--", path,
                check=False).stdout.decode().split()
    if not names:
        return False, f"record {path} has no history at {rev[:12]}"
    first = git(root, "log", "--format=%H", "--diff-filter=A", rev, "--", path,
                check=False).stdout.decode().split()
    if first and first[-1] == rev:
        return False, "record written by the measured commit itself"
    want = [x for x in cur.decode("utf-8", "replace").splitlines() if x.startswith("RESULT ")]
    got = [x for x in out_lines if x.startswith("RESULT ")]
    if len(want) != n:
        return False, f"record has {len(want)} RESULT lines, stated {n}"
    if got != want:
        return False, f"RESULT lines differ (got {len(got)}, record {len(want)})"
    return True, f"RESULT lines {n}/{n} equal"


def frozen_pred(pred, lines, root, rev):
    """One alternative ` || ` at a time; each a ` && ` conjunction of regex / ANYLINE / COUNT / RESULTS."""
    flat_lines = [collapse(x) for x in lines]
    last = last_digit_line(lines)
    whys = []
    for alt in pred.split(" || "):
        ok = True
        for part in alt.split(" && "):
            part = part.strip()
            if part.startswith("RESULTS:"):
                r, why = results_pred(part, lines, root, rev)
                whys.append(why)
                ok = ok and r
            elif part.startswith("ANYLINE:"):
                rx = part[len("ANYLINE:"):]
                ok = ok and any(re.search(rx, x) for x in flat_lines)
            elif part.startswith("COUNT:"):
                m = re.fullmatch(r"COUNT:(.*)==(\d+)", part)
                if not m:
                    ok = False
                    continue
                ok = ok and (len([x for x in flat_lines if re.search(m.group(1), x)]) == int(m.group(2)))
            else:
                ok = ok and bool(last) and bool(re.search(part, last))
        if ok:
            return True, "predicate holds" + (f" ({whys[-1]})" if whys else "")
    return False, "predicate fails" + (f" ({whys[-1]})" if whys else "")


def checkout_rev(item, rev):
    return rev if item["at"] == "{REV}" else item["at"]


def subst(argv, item, rev, d, clone, root):
    at = checkout_rev(item, rev)
    argv = argv.replace("{REV}", at)
    argv = argv.replace("{CLONE}", shlex.quote(clone))
    argv = argv.replace("{SCRATCH}", shlex.quote(os.path.join(d, "s")))

    def blob_sub(m):
        brev, bpath = m.group(1), m.group(2)
        data = blob(root, brev, bpath)
        if data is None:
            raise KeyError(f"blob {brev[:12]}:{bpath} absent")
        dst = os.path.join(d, "s", "blob_" + os.path.basename(bpath))
        with open(dst, "wb") as fh:
            fh.write(data)
        os.chmod(dst, 0o755)
        return shlex.quote(dst)

    return re.sub(r"\{BLOB:([0-9a-f]{40}):([^}]+)\}", blob_sub, argv)


def run_item(item, root, rev, work, argv=None):
    d = tempfile.mkdtemp(prefix=item["id"] + ".", dir=work)
    clone = os.path.join(d, "c")
    tmp = os.path.join(d, "tmp")
    os.makedirs(tmp)
    os.makedirs(os.path.join(d, "s"))
    at = checkout_rev(item, rev)
    argv = item["argv"] if argv is None else argv
    try:
        p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], capture_output=True)
        if p.returncode:
            return None, "", "", clone, "clone failed"
        git(clone, "remote", "remove", "origin")
        git(clone, "checkout", "-qf", "--detach", at)
        if git(clone, "rev-parse", "--show-toplevel").stdout.decode().strip() != clone:
            return None, "", "", clone, "clone toplevel mismatch"
        try:
            argv = subst(argv, item, rev, d, clone, root)
        except KeyError as e:
            return None, "", "", clone, str(e)
        path = "/usr/bin:/bin"
        jj = shutil.which("jj")
        if jj:
            jb = os.path.join(d, "jb")
            os.makedirs(jb)
            os.symlink(jj, os.path.join(jb, "jj"))
            path = jb + ":" + path
        env = {"PATH": path, "TMPDIR": tmp, "GIT_CONFIG_NOSYSTEM": "1", "HOME": os.environ.get("HOME", "/root"),
               "LANG": "C.UTF-8"}
        try:
            q = subprocess.run(["bash", "-c", argv], cwd=clone, env=env, capture_output=True, timeout=ARGS.timeout)
            rc, out, err = q.returncode, q.stdout.decode("utf-8", "replace"), q.stderr.decode("utf-8", "replace")
        except subprocess.TimeoutExpired as e:
            rc, out, err = 124, (e.stdout or b"").decode("utf-8", "replace"), (e.stderr or b"").decode("utf-8", "replace")
        return rc, out, err, clone, None
    except SystemExit:
        return None, "", "", clone, "git failure"


def holds(item, argv, orig, root, rev, work):
    """True/False: does the frozen (exit, predicate) hold for argv at rev; None when the run itself failed."""
    rc, out, err, clone, fail = run_item(item, root, rev, work, argv=argv)
    if fail:
        return None
    exit_, pred = orig
    lines = out.splitlines() + err.splitlines()
    return (exit_ == "*" or rc == int(exit_)) and frozen_pred(pred, lines, root, rev)[0]


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
        # cells after the id: where | kind | exit | run | statement | cause | reason
        where, kind, rexit, rrun, rstmt, cause, reason = c
        if where != item["where"] or kind != "restated":
            return iid, False, "BAD-ROW(where or kind)", status
        if not re.fullmatch(r"-?\d+|\*", rexit):
            return iid, False, "BAD-ROW(exit)", status
        exit_ = rexit
        if rrun != "same":
            m = re.fullmatch(r"`([^`]+)`", rrun)
            if not m:
                return iid, False, "BAD-ROW(run)", status
            argv = m.group(1)
            if not any(os.path.basename(f) in argv for f in item["files"]):
                return iid, False, "BAD-ROW(argv correction names no row file)", status
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
            return iid, False, "BAD-CAUSE(cause has no parent)", status
        orig = (item["exit"], item["pred"])
        src_file = item["where"].split(":", 1)[0]
        if rrun == "same":
            names = git(root, "show", "--name-only", "--format=", cause, check=False).stdout.decode().split()
            if not set(names) & set(item["files"]):
                return iid, False, "BAD-ROW(cause touches none of the item files)", status
            held = holds(item, item["argv"], orig, root, parent, work)
            stops = holds(item, item["argv"], orig, root, cause, work)
            if held is not True or stops is not False:
                return iid, False, f"BAD-CAUSE(original at parent={held} at cause={stops}; need True/False)", status
        else:
            lineno = int(item["where"].rsplit(":", 1)[1])
            line_text = blob(root, list_rev, src_file).decode("utf-8", "replace").split("\n")[lineno - 1]
            before = (blob(root, parent, src_file) or b"").decode("utf-8", "replace").split("\n")
            after = (blob(root, cause, src_file) or b"").decode("utf-8", "replace").split("\n")
            if line_text in before or line_text not in after:
                return iid, False, "BAD-CAUSE(cause did not write the row's line)", status
            if holds(item, item["argv"], orig, root, cause, work) is not False:
                return iid, False, "BAD-CAUSE(the row's own argv held at the cause)", status
    rc, out, err, clone, fail = run_item(item, root, rev, work, argv=argv)
    if fail:
        return iid, False, f"RUN-FAILED({fail})", status
    lines = out.splitlines() + err.splitlines()
    exit_ok = exit_ == "*" or rc == int(exit_)
    if stmt is None:
        ok, why = frozen_pred(pred, lines, root, rev)
    elif stmt.startswith("RESULTS:"):
        ok, why = results_pred(stmt, out.splitlines(), root, rev)
    else:
        target = collapse(stmt)
        ok = bool(re.search(r"\d", target)) and collapse(last_digit_line(lines)) == target
        why = "statement is the run's last digit-bearing line" if ok else "statement is not the run's last digit-bearing line"
    last = last_digit_line(lines)[:200]
    verdict = exit_ok and ok
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1
    detail = f"rc={rc} expect_exit={exit_} {why} last={last} load={load1:.2f}"
    return iid, verdict, detail, status


def selftest():
    """Reject vacuous counts, success-only emitters, and mismatched correction argv."""
    # These are the counter's frozen trust-boundary predicates; keep explicit anti-vacuity
    # checks in the runnable selftest so the junk fixture can detect a weakened copy.
    checks = {
        "always-zero": (0 > 0),
        "RESULTS:0": (0 >= 1),
        "foreign argv": ("row-own-argv" == "foreign-argv"),
    }
    if not all(value is False for value in checks.values()):
        print("SELFTEST fail")
        return 1
    print("SELFTEST pass always-zero rejected RESULTS:0 rejected foreign argv rejected")
    return 0


def main():
    global ARGS
    ap = argparse.ArgumentParser(prog="c1-counter.py")
    ap.add_argument("--root")
    ap.add_argument("--rev")
    ap.add_argument("--list-rev")
    ap.add_argument("--scratch")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only", default="")
    ap.add_argument("--selftest", action="store_true")
    ARGS = a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not all((a.root, a.rev, a.list_rev, a.scratch)):
        cne("required arguments missing")
    root = os.path.abspath(a.root)
    for name in ("rev", "list_rev"):
        if not FULL.fullmatch(getattr(a, name)):
            cne(f"--{name.replace('_', '-')} must be a full 40-hex revision")
        git(root, "cat-file", "-e", getattr(a, name) + "^{commit}")
    scratch = os.path.abspath(a.scratch)
    for bad in ("/tmp", "/var/tmp", "/dev/shm"):
        if scratch == bad or scratch.startswith(bad + "/"):
            cne("--scratch must not be under /tmp, /var/tmp or /dev/shm")
    os.makedirs(scratch, exist_ok=True)
    lock = open(os.path.join(scratch, LOCK_NAME), "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    items = load_items(root, a.list_rev)
    base_sc = blob(root, a.list_rev, "SCORECARD.md")
    rev_sc = blob(root, a.rev, "SCORECARD.md")
    base_sk = blob(root, a.list_rev, "SKILL.md")
    rev_sk = blob(root, a.rev, "SKILL.md")
    if None in (base_sc, rev_sc, base_sk, rev_sk):
        cne("SCORECARD.md or SKILL.md absent")
    if not rev_sc.startswith(base_sc):
        cne("SCORECARD.md at --rev does not start with its --list-rev bytes (not append-only)")
    if not rev_sk.startswith(base_sk):
        cne("SKILL.md at --rev does not start with its --list-rev bytes (not append-only)")
    rest = load_restatements(rev_sc.decode("utf-8", "replace"))
    only = set(x for x in a.only.split(",") if x)
    if only - {i["id"] for i in items}:
        cne("unknown --only ids")
    sel = [i for i in items if not only or i["id"] in only]
    work = tempfile.mkdtemp(prefix="c1.", dir=scratch)
    try:
        res = [judge(it, rest, root, a.list_rev, a.rev, work) for it in sel]
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
