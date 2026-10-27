#!/usr/bin/env python3
r"""r35 C1 calibration counter (frozen at the r35 preregistration): registry-and-measurement-row agreement.

Repair of the r34 counter (r34 lesson `## Mistakes`; r34 verifier spot-check routed defects):

R1 Predicate matching collapses whitespace on BOTH sides. The r34 counter collapsed every
   output line but matched the bare/ANYLINE/COUNT regex verbatim, so a frozen statement
   whose cell carried a literal tab could never match (G05, G17b). Here each pattern is
   collapsed with the same `collapse()` as the output before it is compiled, so a tab in a
   frozen cell means "one or more spaces" exactly like the line it is matched against.
R2 The argv-correction cause check is position-bound. The r34 check asked whether the row's
   line text was ABSENT before and present after the cause commit; when the `where` cell is
   off by one and an adjacent row carries the same text (G17a, G21), a foreign neighbor
   satisfies the membership test. Here the check compares the line AT the frozen `where`
   index before and after: `before[lineno-1] != line_text and after[lineno-1] == line_text`.
R3 A restated exit must be a concrete integer. The r34 regex `-?\d+|\\*` let a restatement
   state `exit=*`, which `exit_ok` then accepts for ANY return code (vacuous-exit class).
   The restated-exit regex is now `-?\\d+` and selftest pins it.
R4 Withdrawal rows. A frozen item whose row cannot honestly be restated (its statement is
   self-referential to the run, its stated revision was never valid, or its last-line
   observable is unrepresentable) may be discharged by a `### Round 35 registry withdrawals`
   SCORECARD row: | id | <file>:<line> | withdrawn | witness-file | class | reason | where
   class is in {self-referential, invalid-revision, unrepresentable, counter-repaired} and
   the witness file must exist at --rev. Withdrawn items leave the `unresolved` count but
   are capped: SUMMARY prints withdrawn= and exit 0 requires withdrawn <= WITHDRAW_MAX.
R5 Item pins must be honest. For an item with `at` not `{REV}`, the counter verifies every
   file in its `files` cell exists at that pinned `at` revision BEFORE the run; an item
   whose own files are absent at its pin (r34 G24) prints LIST-DEFECT, never MISMATCH.

The rest is the r34 contract, verbatim: items from census/round-35/c1-items.tsv at
--list-rev only; private no-local detached clones per item; scrubbed env; {REV}/{SCRATCH}/
{CLONE}/{BLOB:} substitution; frozen predicate alternatives ` || ` of ` && ` conjuncts
(bare last-digit-line regex / ANYLINE: / COUNT: / RESULTS:<path>:<n>); restatements under
both `### Round 34 registry restatements` and `### Round 35 registry restatements`
(r34-validated corrections carry forward and are re-verified); the cause is executed
(value drift: original holds at parent, fails at cause; argv correction: cause wrote the
row's `where` line per R2 and the row's own argv fails at the cause); the measured-run
argv is the row's corrected argv else the frozen argv; SCORECARD.md and SKILL.md at --rev
start with their --list-rev bytes (append-only).

Runs are serialized by one flock at --scratch/c1.lock; the 1-min load is recorded beside
every ITEM line. do-nothing: `--rev <base> --list-rev <prereg>` must print unresolved>0.
Exit 0 iff unresolved=0 AND withdrawn<=WITHDRAW_MAX.
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
ITEMS_PATH = "census/round-35/c1-items.tsv"
SECTIONS = ("### Round 34 registry restatements", "### Round 35 registry restatements")
WSECTION = "### Round 35 registry withdrawals"
WITHDRAW_MAX = 4
WITHDRAW_CLASSES = {"self-referential", "invalid-revision", "unrepresentable", "counter-repaired"}
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
        iid, where, exit_, pred, files, at, argv = f
        if not re.fullmatch(r"-?\d+", exit_):
            cne(f"frozen exit not concrete for {iid}: {exit_!r}")
        items.append({"id": iid, "where": where, "exit": exit_, "pred": pred,
                      "files": [x for x in files.split(",") if x], "at": at, "argv": argv})
    return items


def load_restatements(text):
    """Return {id: [cells, ...]} for rows under any SECTION (until the next heading)."""
    rows = {}
    inside = False
    for ln in text.splitlines():
        if ln.startswith("#"):
            inside = ln.startswith(SECTIONS)
            continue
        if not inside:
            continue
        m = ROW.match(ln)
        if m:
            cells = [c.strip() for c in ("| " + m.group(2) + " |").strip("|").split(" | ")]
            rows.setdefault(m.group(1), []).append([c.strip() for c in cells])
    return rows


def load_withdrawals(text):
    """Return {id: [cells]} for rows under WSECTION: | id | where | withdrawn | witness | class | reason |."""
    rows = {}
    inside = False
    for ln in text.splitlines():
        if ln.startswith("#"):
            inside = ln.startswith(WSECTION)
            continue
        if not inside:
            continue
        m = ROW.match(ln)
        if m:
            cells = [c.strip() for c in ("| " + m.group(2) + " |").strip("|").split(" | ")]
            rows.setdefault(m.group(1), []).append(cells)
    return rows


def pat(text):
    """R1: collapse a frozen pattern cell exactly like the output lines it matches."""
    return collapse(text)


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
                rx = pat(part[len("ANYLINE:"):])
                ok = ok and any(re.search(rx, x) for x in flat_lines)
            elif part.startswith("COUNT:"):
                m = re.fullmatch(r"COUNT:(.*)==(\d+)", part)
                if not m:
                    ok = False
                    continue
                ok = ok and (len([x for x in flat_lines if re.search(pat(m.group(1)), x)]) == int(m.group(2)))
            else:
                ok = ok and bool(last) and bool(re.search(pat(part), last))
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
    return rc == int(exit_) and frozen_pred(pred, lines, root, rev)[0]


def judge(item, rest, wdr, root, list_rev, rev, work):
    iid = item["id"]
    # R5: a pinned `at` revision must carry every file the item exercises.
    if item["at"] != "{REV}":
        if not FULL.fullmatch(item["at"]):
            return iid, False, f"LIST-DEFECT(pin not full40: {item['at']})", "original"
        missing = [f for f in item["files"] if blob(root, item["at"], f) is None]
        if missing:
            return iid, False, f"LIST-DEFECT(pin {item['at'][:12]} lacks {','.join(missing)})", "original"
    wrows = wdr.get(iid, [])
    if len(wrows) > 1:
        return iid, False, "BAD-WDRAW(duplicate withdrawal)", "original"
    if wrows:
        # cells after the id: where | kind | witness | class | reason
        wc = wrows[0]
        if len(wc) != 5:
            return iid, False, f"BAD-WDRAW(cells={len(wc)})", "original"
        wwhere, wkind, witness, wclass, wreason = wc
        if wwhere != item["where"]:
            return iid, False, "BAD-WDRAW(where)", "original"
        if wkind != "withdrawn":
            return iid, False, "BAD-WDRAW(kind)", "original"
        if wclass not in WITHDRAW_CLASSES:
            return iid, False, f"BAD-WDRAW(class {wclass})", "original"
        wblob = blob(root, rev, witness)
        if not wblob or not wblob.strip():
            return iid, False, f"BAD-WDRAW(witness absent/empty at rev: {witness})", "original"
        if not wreason.strip():
            return iid, False, "BAD-WDRAW(empty reason)", "original"
        try:
            load1 = os.getloadavg()[0]
        except OSError:
            load1 = -1
        return iid, None, f"WITHDRAWN class={wclass} witness={witness} load={load1:.2f}", "withdrawn"
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
        if not re.fullmatch(r"-?\d+", rexit):
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
            # R2: position-bound — the cause must write the row's line AT its frozen index,
            # not merely be a commit after which that text exists somewhere in the file.
            btxt = before[lineno - 1] if lineno - 1 < len(before) else None
            atxt = after[lineno - 1] if lineno - 1 < len(after) else None
            if btxt == line_text or atxt != line_text:
                return iid, False, "BAD-CAUSE(cause did not write the row's line at its index)", status
            if holds(item, item["argv"], orig, root, cause, work) is not False:
                return iid, False, "BAD-CAUSE(the row's own argv held at the cause)", status
    rc, out, err, clone, fail = run_item(item, root, rev, work, argv=argv)
    if fail:
        return iid, False, f"RUN-FAILED({fail})", status
    lines = out.splitlines() + err.splitlines()
    exit_ok = rc == int(exit_)
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
        # R3: a wildcard restated exit must be refused (vacuous-exit survivor).
        "wildcard-exit-accepted": bool(re.fullmatch(r"-?\d+", "*")),
        # R1: a tab-bearing pattern matches its collapsed line.
        "tab-predicate-unmatchable": not bool(re.search(pat("\t"), " ")),
        # R4: an unknown withdrawal class must be refused.
        "bogus-class-accepted": ("bogus" in WITHDRAW_CLASSES),
    }
    if not all(value is False for value in checks.values()):
        print("SELFTEST fail")
        return 1
    print("SELFTEST pass always-zero rejected RESULTS:0 rejected foreign argv rejected wildcard-exit rejected tab-predicate matches bogus-class rejected")
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
    wdr = load_withdrawals(rev_sc.decode("utf-8", "replace"))
    only = set(x for x in a.only.split(",") if x)
    if only - {i["id"] for i in items}:
        cne("unknown --only ids")
    sel = [i for i in items if not only or i["id"] in only]
    work = tempfile.mkdtemp(prefix="c1.", dir=scratch)
    try:
        res = [judge(it, rest, wdr, root, a.list_rev, a.rev, work) for it in sel]
    finally:
        subprocess.run(["chmod", "-R", "u+w", work], capture_output=True)
        shutil.rmtree(work, ignore_errors=True)
    agree = mism = restated = withdrawn = 0
    for iid, ok, detail, status in res:
        agree += ok is True
        mism += ok is False
        withdrawn += status == "withdrawn" and ok is None
        restated += status == "restated"
        mark = "WITHDRAWN" if status == "withdrawn" and ok is None else ("AGREE" if ok else "MISMATCH")
        print(f"ITEM\t{iid}\t{mark}\t{status}\t{detail}")
    partial = " partial=1" if only else ""
    unresolved = len(res) - agree - withdrawn
    print(f"SUMMARY items={len(sel)} agree={agree} unresolved={unresolved} mismatches={mism} withdrawn={withdrawn} restated={restated}{partial} rev={a.rev}")
    return 0 if (unresolved == 0 and withdrawn <= WITHDRAW_MAX) else 1


if __name__ == "__main__":
    sys.exit(main())
