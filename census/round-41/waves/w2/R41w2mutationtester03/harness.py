#!/usr/bin/env python3
"""R41w2mutationtester03: single-defect mutants of tools/souji-worktree-drift.py, each run
through the committed tests/fixtures/r41-refusal-sites.py (unmodified) and through a set of
supplementary probes that are NOT committed (used only to classify fixture survivors).

Mutants are generated in memory from the frozen tool bytes; every replacement must match
exactly once or the run aborts. Nothing is written into the lane."""
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/souji-r41/R41w2mutationtester03"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL_SRC = LANE + "/tools/souji-worktree-drift.py"
FIX_SRC = LANE + "/tests/fixtures/r41-refusal-sites.py"
TOOL_SHA = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
FIX_SHA = "f32022e28fe2293af44d7fee1cb73f9a39221fbcc534022b78d77a8c96551978"

# (id, group, description, old, new). old must occur exactly once in the frozen tool.
MUTANTS = [
    ("A1", "errno", "parse_record: ENOENT branch tests EACCES instead", "if exc.errno == errno.ENOENT:", "if exc.errno == errno.EACCES:"),
    ("A2", "errno", "parse_record: ELOOP folded into the ENOENT (MALFORMED) branch", "if exc.errno == errno.ENOENT:", "if exc.errno in (errno.ENOENT, errno.ELOOP):"),
    ("A3", "errno", "parse_record: ENOENT branch condition inverted", "if exc.errno == errno.ENOENT:", "if exc.errno != errno.ENOENT:"),
    ("A4", "errno", "open_nofollow: ENXIO dropped from not-regular translation", "if exc.errno in (errno.ENXIO, errno.EISDIR):", "if exc.errno in (errno.EISDIR,):"),
    ("A5", "errno", "open_nofollow: EISDIR dropped from not-regular translation", "if exc.errno in (errno.ENXIO, errno.EISDIR):", "if exc.errno in (errno.ENXIO,):"),
    ("A6", "errno", "open_nofollow: not-regular translation disabled", "if exc.errno in (errno.ENXIO, errno.EISDIR):", "if False:"),
    ("A7", "errno", "open_nofollow: EACCES folded into not-regular translation", "if exc.errno in (errno.ENXIO, errno.EISDIR):", "if exc.errno in (errno.ENXIO, errno.EISDIR, errno.EACCES):"),
    ("B1", "O_NONBLOCK", "parse_record: record opened without O_NONBLOCK", "fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)", "fd = os.open(path, os.O_RDONLY)"),
    ("B2", "O_NONBLOCK", "open_nofollow: --json leaf opened without O_NONBLOCK", "os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,", "os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW,"),
    ("B3", "O_NONBLOCK", "parse_record: set_blocking(True) before read removed", "os.set_blocking(fd, True)\n        chunks = []", "chunks = []"),
    ("B4", "O_NONBLOCK", "open_nofollow: set_blocking(True) before return removed", "os.set_blocking(fd, True)\n        return fd", "return fd"),
    ("C1", "S_ISREG", "parse_record: fstat S_ISREG gate removed", "if not stat.S_ISREG(os.fstat(fd).st_mode):", "if False:"),
    ("C2", "S_ISREG", "open_nofollow: post-open S_ISREG gate removed", "if not stat.S_ISREG(mode):", "if False:"),
    ("D1", "nlink", "run: multi-link threshold 1 -> 2", "if st.st_nlink > 1:", "if st.st_nlink > 2:"),
    ("D2", "nlink", "run: multi-link test removed", "if st.st_nlink > 1:", "if False:"),
    ("D3", "nlink", "run: multi-link test over-refuses (>= 1)", "if st.st_nlink > 1:", "if st.st_nlink >= 1:"),
    ("E1", "commonpath", "run: record-row containment test removed", "if not inside:", "if False:"),
    ("E2", "commonpath", "run: record-row containment uses commonprefix (string prefix)", "inside = os.path.commonpath([resolved, root_real]) == root_real", "inside = os.path.commonprefix([resolved, root_real]) == root_real"),
    ("E3", "commonpath", "run: gitdir containment test removed", "if not gitdir_inside:", "if False:"),
    ("E4", "commonpath", "run: gitdir containment uses commonprefix (string prefix)", "gitdir_inside = os.path.commonpath([gitdir, root_real]) == root_real", "gitdir_inside = os.path.commonprefix([gitdir, root_real]) == root_real"),
    ("E5", "commonpath", "run: JSON guard loops over [root] only", "for base in measured:", "for base in [root_real]:"),
    ("E6", "commonpath", "run: JSON-INSIDE-MEASURED-TREE test removed", "if inside:", "if False:"),
    ("E7", "commonpath", "run: gitdir not appended to measured list", "measured.append(gitdir)", "pass"),
    ("E8", "commonpath", "run: root not seeded into measured list", "measured = [root_real]", "measured = []"),
    ("E9", "commonpath", "run: repo path not appended to measured list", "measured.append(resolved)", "pass"),
    ("F1", "alias", "run: path-equality alias test removed", "alias = record_abs == json_target", "alias = False"),
    ("F2", "alias", "run: inode-equality alias test removed", "alias = (rec_st.st_dev, rec_st.st_ino) == (out_st.st_dev, out_st.st_ino)", "alias = False"),
    ("F3", "alias", "run: JSON-IS-RECORD refusal removed", "if alias:", "if False:"),
    ("G1", "timeout", "main: timeout lower bound < 0 (was < 1)", "if args.timeout < 1:", "if args.timeout < 0:"),
    ("G2", "timeout", "main: timeout lower bound <= 1 (boundary moved)", "if args.timeout < 1:", "if args.timeout <= 1:"),
    ("G3", "timeout", "argparse: --timeout default 20 -> 1", "default=20", "default=1"),
    ("G4", "timeout", "measure: list-timeout handler re-raises", 'return None, None, "UNREACHABLE:list-timeout"', "raise"),
    ("G5", "timeout", "measure: worktree-list nonzero-rc check removed", "if listed.returncode != 0:", "if False:"),
    ("G6", "timeout", "measure: worktree-prune nonzero-rc check removed", "if dry.returncode != 0:", "if False:"),
    ("H1", "argparse", "argparse: --root no longer required", 'ap.add_argument("--root", required=True)', 'ap.add_argument("--root", default=".")'),
    ("H2", "argparse", "argparse: --record no longer required", 'ap.add_argument("--record", required=True)', 'ap.add_argument("--record", default=None)'),
    ("H3", "argparse", "argparse: --skip-unrecorded store_false", 'action="store_true"', 'action="store_false"'),
    ("H4", "argparse", "argparse: --json default empty string", 'ap.add_argument("--json")', 'ap.add_argument("--json", default="")'),
    ("I1", "discover", "discover: symlinked-child skip removed", "if os.path.islink(path):", "if False:"),
    ("J1", "record", "parse_record: duplicate-name refusal removed", 'if name in [r["name"] for r in rows]:', "if False:"),
    ("J2", "record", "parse_record: TOTAL repos check removed", 'if total["repos"] != len(rows):', "if False:"),
    ("J3", "record", "parse_record: TOTAL regs check removed", 'if total["regs"] != sum(r["regs"] for r in rows):', "if False:"),
    ("J4", "record", "parse_record: TOTAL prunable check removed", 'if total["prunable"] != sum(r["prunable"] for r in rows):', "if False:"),
    ("J5", "record", "parse_record: only the last TOTAL row kept (r40 M40-4 regression)", "totals.append(total)", "totals[:] = [total]"),
    ("J6", "record", "parse_record: '#' comment-line skip removed", 'if not line.strip() or line.startswith("#"):', "if not line.strip():"),
    ("J7", "record", "parse_record: RECORD-EMPTY refusal removed", "if not rows:", "if False:"),
    ("J8", "record", "parse_record: schema-mismatch refusal replaced by skip", 'raise Refusal("RECORD-MALFORMED: line %d does not match the census schema" % lineno)', "continue"),
    ("J9", "record", "ROW regex: regs accepts a single digit only", r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d+)", r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d)"),
    ("K1", "usage", "run: --root is-a-directory USAGE check removed", "if not os.path.isdir(root):", "if False:"),
    ("L1", "nofollow", "open_nofollow: O_NOFOLLOW removed from ancestor walk", "os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd", "os.O_RDONLY | os.O_DIRECTORY, dir_fd=dirfd"),
    ("L2", "nofollow", "open_nofollow: O_NOFOLLOW removed from leaf open", "os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,", "os.O_WRONLY | os.O_CREAT | os.O_NONBLOCK,"),
    ("M1", "write", "run: ftruncate before JSON write removed", "os.ftruncate(fd, 0)", "pass"),
    ("N1", "exit", "run: drift exit code 1 -> 0", "return 0 if not drift else 1", "return 0"),
    ("P1", "exit", "main: refusal exit code 2 -> 1", 'sys.stderr.write("REFUSAL %s\\n" % exc)\n        return 2', 'sys.stderr.write("REFUSAL %s\\n" % exc)\n        return 1'),
    ("T1", "drift", "run: ABSENT branch removed", "        path = repo_path(root, name)\n        if path is None:", "        path = repo_path(root, name)\n        if False:"),
    ("X1", "env", "CHILD_ENV: GIT_CONFIG_GLOBAL entry removed", '    "GIT_CONFIG_GLOBAL": os.devnull,\n', ""),
]


def env_for(tmp):
    return {"PATH": os.environ["PATH"], "TMPDIR": tmp, "LC_ALL": "C"}


def setup_env(tmp):
    return {"PATH": os.environ["PATH"], "TMPDIR": tmp, "LC_ALL": "C", "HOME": S + "/home",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


def git_init(path, tmp, bare=False):
    args = ["git", "init", "-q"] + (["--bare"] if bare else []) + [path]
    subprocess.run(args, env=setup_env(tmp), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write(path, text):
    with open(path, "w") as f:
        f.write(text)
    return path


def run_tool(tool, tmp, args, timeout=40):
    try:
        return subprocess.run(["python3", "-B", tool] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=timeout, env=env_for(tmp))
    except subprocess.TimeoutExpired:
        return None


def refused(p, cls):
    if p is None:
        return False, "timeout"
    ok = p.returncode == 2 and ("REFUSAL %s:" % cls) in p.stderr
    return ok, "rc=%d stderr=%s" % (p.returncode, p.stderr.strip().splitlines()[-1:] if p.stderr.strip() else "")


def base(W, tmp):
    R, O = W + "/root", W + "/o"
    os.makedirs(R)
    os.makedirs(O)
    git_init(R + "/r", tmp)  # real repository: regs=1 prunable=0
    return R, O


ROW_R = "REPO\tr\tregs=1\tprunable=0\n"


def p_x01(tool, W, tmp):  # row resolves to sibling sharing the root's string prefix
    R, O = base(W, tmp)
    rec = write(O + "/rec", "REPO\t../root2\tregs=1\tprunable=0\n")
    return refused(run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"]), "RECORD-OUTSIDE-ROOT")


def p_x02(tool, W, tmp):  # gitdir resolves to sibling sharing the root's string prefix
    R, O = base(W, tmp)
    os.makedirs(W + "/rootX")
    gd2 = W + "/rootX/gd2"
    git_init(gd2, tmp, bare=True)
    os.makedirs(R + "/s")
    write(R + "/s/.git", "gitdir: " + gd2 + "\n")
    rec = write(O + "/rec", "REPO\ts\tregs=1\tprunable=0\n")
    return refused(run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"]), "RECORD-OUTSIDE-ROOT")


def p_x03(tool, W, tmp):  # --json directly under --root, not under any measured repository
    R, O = base(W, tmp)
    rec = write(O + "/rec", ROW_R)
    return refused(run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--json", R + "/loose.json"]), "JSON-INSIDE-MEASURED-TREE")


def p_x04(tool, W, tmp):  # --json is a hardlink (different path) of the record
    R, O = base(W, tmp)
    ok = write(O + "/rec", ROW_R)
    os.link(ok, O + "/rec_ln")
    return refused(run_tool(tool, tmp, ["--root", R, "--record", ok, "--skip-unrecorded", "--json", O + "/rec_ln"]), "JSON-IS-RECORD")


def p_x05(tool, W, tmp):  # two TOTAL rows: first disagrees, last agrees
    R, O = base(W, tmp)
    rec = write(O + "/rec", "REPO\ta\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return refused(run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"]), "RECORD-MALFORMED")


def p_x06(tool, W, tmp):  # FIFO as the record path
    R, O = base(W, tmp)
    os.mkfifo(O + "/rfifo")
    return refused(run_tool(tool, tmp, ["--root", R, "--record", O + "/rfifo", "--skip-unrecorded"]), "RECORD-MALFORMED")


def p_x07(tool, W, tmp):  # --timeout 1 is a valid value (boundary)
    R, O = base(W, tmp)
    rec = write(O + "/rec", "REPO\ta\tregs=1\tprunable=0\n")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--timeout", "1"])
    good = p is not None and p.returncode == 1 and "DRIFT\tABSENT\ta" in p.stdout
    return good, "rc=%s" % (p.returncode if p else "timeout")


def p_x08(tool, W, tmp):  # git blocks on a FIFO HEAD: list-timeout branch
    R, O = base(W, tmp)
    git_init(R + "/t", tmp)
    os.remove(R + "/t/.git/HEAD")
    os.mkfifo(R + "/t/.git/HEAD")
    rec = write(O + "/rec", "REPO\tt\tregs=1\tprunable=0\n")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--timeout", "1"])
    good = p is not None and p.returncode == 1 and "DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout" in p.stdout
    return good, "rc=%s stdout=%s" % (p.returncode if p else "timeout", p.stdout.strip()[:200] if p else "")


def p_x09(tool, W, tmp):  # empty .git directory: worktree list nonzero rc
    R, O = base(W, tmp)
    os.makedirs(R + "/u/.git")
    rec = write(O + "/rec", "REPO\tu\tregs=1\tprunable=0\n")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"])
    good = p is not None and p.returncode == 1 and "DRIFT\tUNREACHABLE\tu\tUNREACHABLE:list-rc=" in p.stdout
    return good, "rc=%s stdout=%s" % (p.returncode if p else "timeout", p.stdout.strip()[:200] if p else "")


def valid_json(path):
    try:
        with open(path) as f:
            d = json.load(f)
        return "summary" in d and d.get("drift") == []
    except Exception as exc:  # noqa: BLE001 - report any parse failure as a probe failure
        return False


def p_x10(tool, W, tmp):  # positive control: clean run writes valid JSON
    R, O = base(W, tmp)
    rec = write(O + "/rec", ROW_R)
    out = O + "/pos_out.json"
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--json", out])
    return (p is not None and p.returncode == 0 and valid_json(out)), "rc=%s" % (p.returncode if p else "timeout")


def p_x11(tool, W, tmp):  # positive control: pre-existing longer target is truncated, not appended to
    R, O = base(W, tmp)
    rec = write(O + "/rec", ROW_R)
    out = write(O + "/pos_big.json", "x" * 5000)
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--json", out])
    return (p is not None and p.returncode == 0 and valid_json(out)), "rc=%s" % (p.returncode if p else "timeout")


def p_x12(tool, W, tmp):  # drift present -> exit 1
    R, O = base(W, tmp)
    rec = write(O + "/rec", "REPO\tr\tregs=2\tprunable=0\n")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"])
    good = p is not None and p.returncode == 1 and "DRIFT\tREGS-CHANGED\tr" in p.stdout
    return good, "rc=%s" % (p.returncode if p else "timeout")


def p_x13(tool, W, tmp):  # recorded repo absent -> ABSENT drift, exit 1
    R, O = base(W, tmp)
    rec = write(O + "/rec", "REPO\ta\tregs=1\tprunable=0\n")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"])
    good = p is not None and p.returncode == 1 and "DRIFT\tABSENT\ta" in p.stdout
    return good, "rc=%s" % (p.returncode if p else "timeout")


def p_x14(tool, W, tmp):  # discovery: unrecorded repo reported; symlinked child skipped
    R, O = base(W, tmp)
    git_init(R + "/u2", tmp)
    os.symlink(R + "/u2", R + "/lnk")
    rec = write(O + "/rec", ROW_R)
    p = run_tool(tool, tmp, ["--root", R, "--record", rec])
    good = p is not None and p.returncode == 1 and "DRIFT\tUNRECORDED\tu2" in p.stdout and "UNRECORDED\tlnk" not in p.stdout
    return good, "rc=%s stdout=%s" % (p.returncode if p else "timeout", p.stdout.strip()[:300] if p else "")


def p_x15a(tool, W, tmp):  # argparse: --record missing
    R, O = base(W, tmp)
    p = run_tool(tool, tmp, ["--root", R])
    return (p is not None and p.returncode == 2 and "required" in p.stderr), "rc=%s" % (p.returncode if p else "timeout")


def p_x15b(tool, W, tmp):  # argparse: --root missing
    R, O = base(W, tmp)
    rec = write(O + "/rec", ROW_R)
    p = run_tool(tool, tmp, ["--record", rec])
    return (p is not None and p.returncode == 2 and "required" in p.stderr), "rc=%s" % (p.returncode if p else "timeout")


def p_x16(tool, W, tmp):  # two-digit regs in a record row
    R, O = base(W, tmp)
    rec = write(O + "/rec", "REPO\tr\tregs=10\tprunable=0\n")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded"])
    good = p is not None and p.returncode == 1 and "record=10 live=1" in p.stdout
    return good, "rc=%s" % (p.returncode if p else "timeout")


def p_x17(tool, W, tmp):  # --json through a symlinked ancestor resolves (realpath) and writes outside root
    R, O = base(W, tmp)
    rec = write(O + "/rec", ROW_R)
    os.makedirs(O + "/real")
    os.symlink(O + "/real", O + "/lnkdir")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--json", O + "/lnkdir/x.json"])
    return (p is not None and p.returncode == 0 and os.path.exists(O + "/real/x.json")), "rc=%s" % (p.returncode if p else "timeout")


def p_x18(tool, W, tmp):  # --json whose leaf is a symlink resolves to its target and writes there
    R, O = base(W, tmp)
    rec = write(O + "/rec", ROW_R)
    os.symlink(O + "/real2.json", O + "/lnkleaf")
    p = run_tool(tool, tmp, ["--root", R, "--record", rec, "--skip-unrecorded", "--json", O + "/lnkleaf"])
    return (p is not None and p.returncode == 0 and os.path.exists(O + "/real2.json")), "rc=%s" % (p.returncode if p else "timeout")


PROBES = [(n, f) for n, f in sorted(globals().items()) if n.startswith("p_x")]


def run_supp(tool, tag):
    out = []
    for name, fn in PROBES:
        W = os.path.realpath(os.path.join(S, "work", tag, name))
        shutil.rmtree(W, ignore_errors=True)
        os.makedirs(W)
        tmp = os.path.join(S, "tmp", tag)
        os.makedirs(tmp, exist_ok=True)
        try:
            good, detail = fn(tool, W, tmp)
        except Exception as exc:  # noqa: BLE001 - harness error is recorded, not hidden
            good, detail = False, "HARNESS-ERROR %r" % exc
        out.append((name, good, detail))
        shutil.rmtree(W, ignore_errors=True)
    return out


def run_fixture(tool, tag):
    work = os.path.join(S, "work", tag, "fixture")
    tmp = os.path.join(S, "tmp", tag, "fixture")
    os.makedirs(work, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    p = subprocess.run(["python3", "-B", S + "/fixture.py", "--tool", tool, "--work", work],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=900, env=env_for(tmp))
    fails = [ln.split("=")[0][len("probe-"):] for ln in p.stdout.splitlines() if ln.startswith("probe-") and "=FAIL" in ln]
    summary = [ln for ln in p.stdout.splitlines() if ln.startswith("SUMMARY")]
    return {"rc": p.returncode, "fails": fails, "summary": summary[0] if summary else "NO-SUMMARY", "stdout": p.stdout, "stderr": p.stderr}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_one(tag, tool):
    fx = run_fixture(tool, tag)
    sp = run_supp(tool, tag)
    sp_fail = [n for n, g, _ in sp if not g]
    with open(os.path.join(S, "results", tag + ".txt"), "w") as f:
        f.write("TOOL_SHA256 %s\n" % sha(tool))
        f.write("FIXTURE rc=%d %s\n%s" % (fx["rc"], fx["summary"], fx["stdout"]))
        if fx["stderr"].strip():
            f.write("FIXTURE-STDERR\n%s" % fx["stderr"])
        for n, g, d in sp:
            f.write("SUPP %s=%s %s\n" % (n, "PASS" if g else "FAIL", d))
    return {"tag": tag, "fixture_fails": fx["fails"], "fixture_rc": fx["rc"], "fixture_summary": fx["summary"],
            "supp_fails": sp_fail, "supp_detail": {n: d for n, _, d in sp}}


def main():
    os.makedirs(S + "/results", exist_ok=True)
    os.makedirs(S + "/mut", exist_ok=True)
    src = open(TOOL_SRC).read()
    assert sha(TOOL_SRC) == TOOL_SHA, "frozen tool sha mismatch"
    assert sha(FIX_SRC) == FIX_SHA, "committed fixture sha mismatch"
    assert sha(S + "/fixture.py") == FIX_SHA
    jobs = [("BASE", "BASE", "unmodified frozen tool", None)]
    records = {}
    for mid, group, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            print("MUTANT %s ABORT: old occurs %d times" % (mid, n), file=sys.stderr)
            sys.exit(3)
        mut = src.replace(old, new, 1)
        path = "%s/mut/%s.py" % (S, mid)
        open(path, "w").write(mut)
        jobs.append((mid, path, desc, group))
        records[mid] = {"group": group, "desc": desc, "mutant_sha256": sha(path), "old": old, "new": new}
    open(S + "/mut/BASE.py", "w").write(src)
    tools = {}
    for j in jobs:
        tools[j[0]] = j[1] if j[0] == "BASE" else j[1]
    tools["BASE"] = S + "/mut/BASE.py"
    results = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(run_one, mid, tools[mid]): mid for mid, _, _, _ in jobs}
        for fut in cf.as_completed(futs):
            r = fut.result()
            results[r["tag"]] = r
    json.dump({"records": records, "results": results}, open(S + "/results/summary.json", "w"), indent=1, sort_keys=True)
    base = results["BASE"]
    print("BASE fixture:", base["fixture_summary"], "fails=", base["fixture_fails"], "supp_fails=", base["supp_fails"])
    print("ID\tGROUP\tFIXTURE_FAILS\tFIXTURE_SUMMARY\tSUPP_FAILS\tDESC")
    for mid, _, _, _ in jobs[1:]:
        r = results[mid]
        print("%s\t%s\t%s\t%s\t%s\t%s" % (mid, records[mid]["group"], ",".join(r["fixture_fails"]) or "-",
                                       r["fixture_summary"], ",".join(r["supp_fails"]) or "-", records[mid]["desc"]))


if __name__ == "__main__":
    main()
