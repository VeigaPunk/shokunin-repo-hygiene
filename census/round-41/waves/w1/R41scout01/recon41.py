#!/usr/bin/env python3
"""R41scout01 — per-surface feasibility recon for the 19 refusal sites of the
pinned tools/souji-worktree-drift.py (r41 lane).

Exp A: raw syscall probes for every OS-dependent errno the table names.
Exp B: end-to-end run of the pinned tool once per probe id (21) + pristine.
Everything runs under /fast/scratch/hyaku/souji-r41/R41scout01 as uid 1000.
"""
import errno
import hashlib
import os
import shutil
import stat
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools", "souji-worktree-drift.py")
SEAT = "/fast/scratch/hyaku/souji-r41/R41scout01"
FX = os.path.join(SEAT, "fx")
LOGDIR = os.path.join(LANE, ".ufo", "waves", "round-41", "w1", "R41scout01")
LOG = os.path.join(LOGDIR, "recon-log.txt")
TMP = os.path.join(SEAT, "tmp")
EXPECT_SHA = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"

LINES = []


def say(s=""):
    LINES.append(s)
    print(s, flush=True)


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()


def try_open(path, flags, mode=None, dir_fd=None):
    try:
        if dir_fd is not None:
            fd = os.open(path, flags, 0o644 if mode is None else mode, dir_fd=dir_fd)
        else:
            fd = os.open(path, flags, 0o644 if mode is None else mode)
        return fd, None
    except OSError as e:
        return None, e


def errname(e):
    return "errno=%s(%s) %s" % (e.errno, errno.errorcode.get(e.errno, "?"), e.strerror)


def fs_type(path):
    return sh("stat -f -c %T " + sh_quote(path))


def sh_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def make_repo(path):
    p = subprocess.run(["git", "init", "-q", path], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    top = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    return top.stdout.strip()


def write_lines(path, lines):
    with open(path, "w") as h:
        h.write("\n".join(lines) + "\n")


def good_record(rows):
    ls = ["REPO\t%s\tregs=%d\tprunable=%d" % (n, r, p) for n, r, p in rows]
    ls.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % (
        len(rows), sum(r for _, r, _ in rows), sum(p for _, _, p in rows)))
    return ls


def run_tool(tag, probe, root, record, json_=None, timeout=None, extra=()):
    args = [sys.executable, TOOL, "--root", root, "--record", record]
    if json_ is not None:
        args += ["--json", json_]
    if timeout is not None:
        args += ["--timeout", str(timeout)]
    args += list(extra)
    env = dict(os.environ)
    env["TMPDIR"] = TMP
    p = subprocess.run(args, capture_output=True, text=True, env=env)
    refusal = ""
    for line in p.stderr.splitlines():
        if line.startswith("REFUSAL"):
            refusal = line
            break
    summary = ""
    for line in p.stdout.splitlines():
        if line.startswith("SUMMARY"):
            summary = line
            break
    return {"tag": tag, "probe": probe, "rc": p.returncode, "refusal": refusal,
            "summary": summary, "stderr": p.stderr.strip().splitlines()[:2]}


def check(tag, probe, res, want_class, want_substr=None):
    ok = res["refusal"].startswith("REFUSAL " + want_class)
    detail = ""
    if want_substr:
        sub_ok = want_substr in res["refusal"]
        ok = ok and sub_ok
        detail = " substr(%r)=%s" % (want_substr, sub_ok)
    verdict = "MATCH" if ok else "MISMATCH"
    say("%-4s %-5s rc=%d %s -> %s%s" % (tag, probe, res["rc"], verdict, res["refusal"], detail))
    if res["summary"]:
        say("      stdout: " + res["summary"])
    return ok


def main():
    os.makedirs(FX, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)

    sha = hashlib.sha256(open(TOOL, "rb").read()).hexdigest()
    say("== environment ==")
    say("uid: " + sh("id -u") + "  python: " + sys.version.split()[0] + "  git: " + sh("git --version"))
    say("pinned tool sha256: " + sha)
    say("pinned tool sha256 matches preregistration: " + str(sha == EXPECT_SHA))
    say("df -T: " + sh("df -T " + SEAT + " /tmp " + LANE).replace("\n", " | "))
    say("stat -f: scratch=%s tmp=%s lane=%s dev_null=%s" % (
        fs_type(FX), fs_type(TMP), fs_type(LANE), fs_type("/dev/null")))

    # ---------------- Exp A: raw syscall probes ----------------
    say("")
    say("== Exp A: raw errno probes on " + fs_type(FX) + " ==")
    raw = os.path.join(FX, "raw")
    shutil.rmtree(raw, ignore_errors=True)
    os.makedirs(raw)

    # A0 ENOENT: missing record path
    _, e = try_open(os.path.join(raw, "absent.rec"), os.O_RDONLY | os.O_NONBLOCK)
    say("A0 open(missing, O_RDONLY|O_NONBLOCK)      -> " + (errname(e) if e else "OPENED?"))

    # A1 EACCES: chmod 000 record, unprivileged uid
    f1 = os.path.join(raw, "noread.rec")
    write_lines(f1, ["# x"])
    os.chmod(f1, 0o000)
    _, e = try_open(f1, os.O_RDONLY | os.O_NONBLOCK)
    say("A1 open(chmod000, O_RDONLY|O_NONBLOCK)     -> " + (errname(e) if e else "OPENED?"))

    # A2 ELOOP: self-referential symlink record
    l1 = os.path.join(raw, "loop")
    os.symlink(l1, l1)
    _, e = try_open(l1, os.O_RDONLY | os.O_NONBLOCK)
    say("A2 open(self-symlink, O_RDONLY|O_NONBLOCK) -> " + (errname(e) if e else "OPENED?"))

    # A3 ENXIO: FIFO no reader, O_WRONLY|O_NONBLOCK (the open_nofollow leaf flags)
    fp = os.path.join(raw, "pipe.fifo")
    os.mkfifo(fp)
    _, e = try_open(fp, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK)
    say("A3 open(fifo, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK) -> " + (errname(e) if e else "OPENED?"))

    # A4 directory as record: opens O_RDONLY|O_NONBLOCK, fstat is not regular
    ddir = os.path.join(raw, "recdir")
    os.makedirs(ddir)
    fd, e = try_open(ddir, os.O_RDONLY | os.O_NONBLOCK)
    if fd is not None:
        say("A4 open(dir, O_RDONLY|O_NONBLOCK)          -> OPENS; S_ISREG=%s" %
            stat.S_ISREG(os.fstat(fd).st_mode))
        os.close(fd)
    else:
        say("A4 open(dir, O_RDONLY|O_NONBLOCK)          -> " + errname(e))

    # A5 EISDIR: directory as --json leaf (open_nofollow flags)
    _, e = try_open(ddir, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=None)
    _, e = try_open(os.path.join(raw, "recdir"), os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK)
    say("A5 open(dir, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK)  -> " + (errname(e) if e else "OPENED?"))

    # A6 /dev/null as --json: opens, fstat is a character device
    fd = os.open("/dev/null", os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o644)
    st = os.fstat(fd)
    os.close(fd)
    say("A6 open(/dev/null, O_WRONLY|...)           -> OPENS; S_ISREG=%s S_ISCHR=%s" %
        (stat.S_ISREG(st.st_mode), stat.S_ISCHR(st.st_mode)))

    # A7 two-link file outside the root
    h1 = os.path.join(raw, "hard.txt")
    write_lines(h1, ["KEEP"])
    h2 = os.path.join(raw, "hard2.txt")
    os.link(h1, h2)
    say("A7 st_nlink of hardlinked pair             -> %d" % os.stat(h1).st_nlink)

    # A8 EACCES: create in unwritable directory
    lock = os.path.join(raw, "locked")
    os.makedirs(lock)
    os.chmod(lock, 0o555)
    _, e = try_open(os.path.join(lock, "out.json"), os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK)
    say("A8 open(locked/out.json, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK) -> " + (errname(e) if e else "OPENED?"))
    os.chmod(lock, 0o755)

    # A9 RECORD-OUTSIDE-ROOT geometry: ../sibling resolves outside the root
    root9 = os.path.join(raw, "root")
    os.makedirs(os.path.join(root9, "inner"))
    resolved = os.path.realpath(os.path.join(root9, "..", "sibling"))
    import posixpath
    inside = False
    try:
        inside = os.path.commonpath([resolved, os.path.realpath(root9)]) == os.path.realpath(root9)
    except ValueError:
        pass
    say("A9 realpath(root/../sibling)=%s inside=%s" % (resolved, inside))

    # ---------------- Exp B: end-to-end runs of the pinned tool ----------------
    say("")
    say("== Exp B: pinned tool, one run per probe id (21) + pristine ==")
    results = []
    ok_all = True

    def fresh(tag):
        d = os.path.join(FX, tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.join(d, "outside"))
        os.makedirs(os.path.join(d, "root"))
        return d

    # pristine baseline
    d = fresh("pristine")
    top = make_repo(os.path.join(d, "root", "alpha"))
    say("pristine: git -C root/alpha rev-parse --show-toplevel -> " + top)
    write_lines(os.path.join(d, "rec.txt"), good_record([("alpha", 1, 0)]))
    r = run_tool("pristine", "-", os.path.join(d, "root"), os.path.join(d, "rec.txt"),
                 json_=os.path.join(d, "outside", "out.json"))
    say("pristine rc=%d refusal=%r" % (r["rc"], r["refusal"]))
    say("pristine " + r["summary"])
    say("pristine json written: " + str(os.path.isfile(os.path.join(d, "outside", "out.json"))))

    # S01 P01 missing record -> RECORD-MALFORMED
    d = fresh("S01")
    absent_rec = os.path.join(d, "absent.rec")  # never created
    r = run_tool("S01", "P01", os.path.join(d, "root"), absent_rec)
    ok_all &= check("S01", "P01", r, "RECORD-MALFORMED", "is not a regular file")

    # S02a P02a chmod 000 record -> RECORD-MISSING EACCES
    d = fresh("S02a")
    rec = os.path.join(d, "rec.txt")
    write_lines(rec, good_record([("ghost", 1, 0)]))
    os.chmod(rec, 0o000)
    r = run_tool("S02a", "P02a", os.path.join(d, "root"), rec)
    ok_all &= check("S02a", "P02a", r, "RECORD-MISSING", "Errno 13")

    # S02b P02b symlink loop record -> RECORD-MISSING ELOOP
    d = fresh("S02b")
    rec = os.path.join(d, "rec.txt")
    os.symlink(rec, rec)
    r = run_tool("S02b", "P02b", os.path.join(d, "root"), rec)
    ok_all &= check("S02b", "P02b", r, "RECORD-MISSING", "Errno 40")

    # S03 P03 record is a directory -> RECORD-MALFORMED
    d = fresh("S03")
    recd = os.path.join(d, "recdir")
    os.makedirs(recd)
    r = run_tool("S03", "P03", os.path.join(d, "root"), recd)
    ok_all &= check("S03", "P03", r, "RECORD-MALFORMED", "is not a regular file")

    # S04 P04 duplicate REPO rows -> RECORD-MALFORMED
    d = fresh("S04")
    write_lines(os.path.join(d, "rec.txt"), [
        "REPO\talpha\tregs=1\tprunable=0",
        "REPO\talpha\tregs=2\tprunable=0",
        "TOTAL\trepos=2\tregs=3\tprunable=0",
    ])
    r = run_tool("S04", "P04", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S04", "P04", r, "RECORD-MALFORMED", "duplicates")

    # S05 P05 junk line -> RECORD-MALFORMED schema
    d = fresh("S05")
    write_lines(os.path.join(d, "rec.txt"), [
        "# comment",
        "REPO\talpha\tregs=1\tprunable=0",
        "HELLO world",
        "TOTAL\trepos=1\tregs=1\tprunable=0",
    ])
    r = run_tool("S05", "P05", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S05", "P05", r, "RECORD-MALFORMED", "schema")

    # S06 P06 comments only -> RECORD-EMPTY
    d = fresh("S06")
    write_lines(os.path.join(d, "rec.txt"), ["# only", "", "# comments"])
    r = run_tool("S06", "P06", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S06", "P06", r, "RECORD-EMPTY", "no REPO rows")

    # S07 P07 TOTAL repos mismatch
    d = fresh("S07")
    write_lines(os.path.join(d, "rec.txt"), [
        "REPO\talpha\tregs=1\tprunable=0",
        "TOTAL\trepos=2\tregs=1\tprunable=0",
    ])
    r = run_tool("S07", "P07", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S07", "P07", r, "RECORD-MALFORMED", "TOTAL repos=2 but 1 REPO rows")

    # S08 P08 TOTAL regs mismatch
    d = fresh("S08")
    write_lines(os.path.join(d, "rec.txt"), [
        "REPO\talpha\tregs=1\tprunable=0",
        "TOTAL\trepos=1\tregs=99\tprunable=0",
    ])
    r = run_tool("S08", "P08", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S08", "P08", r, "RECORD-MALFORMED", "TOTAL regs=99")

    # S09 P09 TOTAL prunable mismatch
    d = fresh("S09")
    write_lines(os.path.join(d, "rec.txt"), [
        "REPO\talpha\tregs=1\tprunable=0",
        "TOTAL\trepos=1\tregs=1\tprunable=7",
    ])
    r = run_tool("S09", "P09", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S09", "P09", r, "RECORD-MALFORMED", "TOTAL prunable=7")

    # S10a P10a --json FIFO no reader -> JSON-NOT-REGULAR (ENXIO)
    d = fresh("S10a")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    fifo = os.path.join(d, "outside", "pipe.fifo")
    os.mkfifo(fifo)
    r = run_tool("S10a", "P10a", os.path.join(d, "root"), os.path.join(d, "rec.txt"), json_=fifo)
    ok_all &= check("S10a", "P10a", r, "JSON-NOT-REGULAR", "is not a regular file")

    # S10b P10b --json directory -> JSON-NOT-REGULAR (EISDIR)
    d = fresh("S10b")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    jdir = os.path.join(d, "outside", "adir")
    os.makedirs(jdir)
    r = run_tool("S10b", "P10b", os.path.join(d, "root"), os.path.join(d, "rec.txt"), json_=jdir)
    ok_all &= check("S10b", "P10b", r, "JSON-NOT-REGULAR", "is not a regular file")

    # S11 P11 --json /dev/null -> JSON-NOT-REGULAR (character device)
    d = fresh("S11")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    r = run_tool("S11", "P11", os.path.join(d, "root"), os.path.join(d, "rec.txt"), json_="/dev/null")
    ok_all &= check("S11", "P11", r, "JSON-NOT-REGULAR", "is not a regular file")

    # S12 P12 --root not a directory -> USAGE
    d = fresh("S12")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    notadir = os.path.join(d, "outside", "notadir.txt")
    write_lines(notadir, ["x"])
    r = run_tool("S12", "P12", notadir, os.path.join(d, "rec.txt"))
    ok_all &= check("S12", "P12", r, "USAGE", "is not a directory")

    # S13 P13 REPO row ../sibling -> RECORD-OUTSIDE-ROOT
    d = fresh("S13")
    os.makedirs(os.path.join(d, "sibling"))
    write_lines(os.path.join(d, "rec.txt"), good_record([("../sibling", 1, 0)]))
    r = run_tool("S13", "P13", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S13", "P13", r, "RECORD-OUTSIDE-ROOT", "resolves outside")

    # S14 P14 .git file pointing outside -> RECORD-OUTSIDE-ROOT (gitdir)
    d = fresh("S14")
    gitdir = os.path.join(d, "outside", "linked.git")
    p = subprocess.run(["git", "init", "-q", "--bare", gitdir], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    os.makedirs(os.path.join(d, "root", "linked"))
    with open(os.path.join(d, "root", "linked", ".git"), "w") as h:
        h.write("gitdir: %s\n" % gitdir)
    rp = subprocess.run(["git", "-C", os.path.join(d, "root", "linked"), "rev-parse", "--absolute-git-dir"],
                        capture_output=True, text=True)
    say("S14 pre-check: git rev-parse --absolute-git-dir rc=%d -> %s" % (rp.returncode, rp.stdout.strip()))
    write_lines(os.path.join(d, "rec.txt"), good_record([("linked", 1, 0)]))
    r = run_tool("S14", "P14", os.path.join(d, "root"), os.path.join(d, "rec.txt"))
    ok_all &= check("S14", "P14", r, "RECORD-OUTSIDE-ROOT", "gitdir resolves outside")

    # S15 P15 --json is --record -> JSON-IS-RECORD
    d = fresh("S15")
    rec = os.path.join(d, "rec.txt")
    write_lines(rec, good_record([("ghost", 1, 0)]))
    r = run_tool("S15", "P15", os.path.join(d, "root"), rec, json_=rec)
    ok_all &= check("S15", "P15", r, "JSON-IS-RECORD", "is the record file")

    # S16 P16 --json under a measured repository -> JSON-INSIDE-MEASURED-TREE
    d = fresh("S16")
    make_repo(os.path.join(d, "root", "alpha"))
    write_lines(os.path.join(d, "rec.txt"), good_record([("alpha", 1, 0)]))
    r = run_tool("S16", "P16", os.path.join(d, "root"), os.path.join(d, "rec.txt"),
                 json_=os.path.join(d, "root", "alpha", "inside.json"))
    ok_all &= check("S16", "P16", r, "JSON-INSIDE-MEASURED-TREE", "is under")

    # S17 P17 --json two-link file -> JSON-HARDLINKED (content must survive)
    d = fresh("S17")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    jt = os.path.join(d, "outside", "shared.txt")
    write_lines(jt, ["KEEP"])
    os.link(jt, os.path.join(d, "outside", "shared-link.txt"))
    r = run_tool("S17", "P17", os.path.join(d, "root"), os.path.join(d, "rec.txt"), json_=jt)
    ok_all &= check("S17", "P17", r, "JSON-HARDLINKED", "has 2 links")
    say("S17 post-check: target content preserved=%r" % open(jt).read().strip())

    # S18 P18 --json in unwritable directory -> JSON-UNWRITABLE (EACCES)
    d = fresh("S18")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    lockd = os.path.join(d, "outside", "locked")
    os.makedirs(lockd)
    os.chmod(lockd, 0o555)
    r = run_tool("S18", "P18", os.path.join(d, "root"), os.path.join(d, "rec.txt"),
                 json_=os.path.join(lockd, "out.json"))
    os.chmod(lockd, 0o755)
    ok_all &= check("S18", "P18", r, "JSON-UNWRITABLE", "Errno 13")

    # S19 P19 --timeout 0 -> USAGE
    d = fresh("S19")
    write_lines(os.path.join(d, "rec.txt"), good_record([("ghost", 1, 0)]))
    r = run_tool("S19", "P19", os.path.join(d, "root"), os.path.join(d, "rec.txt"), timeout=0)
    ok_all &= check("S19", "P19", r, "USAGE", "--timeout must be >= 1")

    say("")
    say("== verdict: all 21 probe classes match the table: %s ==" % ok_all)
    say("probes run: 21 of 21 (P01..P19 incl. P02a/P02b, P10a/P10b) + 1 pristine; filesystem: %s (xfs)" % fs_type(FX))

    # receipt: copy this script next to the log
    shutil.copy(os.path.abspath(__file__), os.path.join(LOGDIR, "recon41.py"))
    with open(LOG, "w") as h:
        h.write("\n".join(LINES) + "\n")
    say("")
    say("receipts: %s %s" % (LOG, os.path.join(LOGDIR, "recon41.py")))


if __name__ == "__main__":
    main()
