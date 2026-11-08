#!/usr/bin/env python3
"""S87Sentinel — one-command reproducer for the C2 K4 delegation-boundary findings.

Usage:
    python3 -B repro.py                 # run every probe
    python3 -B repro.py --probe TOCTOU  # one probe

Scratch: /fast/scratch/hyaku/souji-r87/S87Sentinel (created and removed by this script).
The lane tree is READ-ONLY to this script: the tool under test is COPIED into a scratch kit
beside a chosen writer. No git state in the lane is touched.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools", "souji-record-agreement.py")
WRITER = os.path.join(LANE, "tools", "souji-receipt-write.py")
SCRATCH = "/fast/scratch/hyaku/souji-r87/S87Sentinel"
K4RE = re.compile(r"^MISMATCH\tK4\t([^\t]*)\t([^\t]*)\t(.*)$", re.M)

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r87 probe", "GIT_AUTHOR_EMAIL": "probe@r87.invalid",
            "GIT_COMMITTER_NAME": "r87 probe", "GIT_COMMITTER_EMAIL": "probe@r87.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, timeout=120)
    if check and p.returncode != 0:
        raise SystemExit("git %s rc=%d: %s" % (args, p.returncode, p.stderr.decode()))
    return p


def mkrepo(tag):
    d = tempfile.mkdtemp(prefix=tag + ".", dir=SCRATCH)
    git(d, "init", "-q", "-b", "master")
    top = git(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise SystemExit("toplevel mismatch")
    return d


def seed(d, files):
    for rel, data in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
    git(d, "add", "-A")
    git(d, "commit", "-q", "--no-verify", "-m", "seed")
    return git(d, "rev-parse", "HEAD").stdout.decode().strip()


def kit(tag, writer_bytes=None):
    k = tempfile.mkdtemp(prefix="kit-" + tag + ".", dir=SCRATCH)
    shutil.copyfile(TOOL, os.path.join(k, "souji-record-agreement.py"))
    if writer_bytes is None:
        shutil.copyfile(WRITER, os.path.join(k, "souji-receipt-write.py"))
    else:
        open(os.path.join(k, "souji-receipt-write.py"), "wb").write(writer_bytes)
    return k


def run(tool, root, rev):
    return subprocess.run([sys.executable, "-B", tool, "--root", root, "--rev", rev],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=SCRATCH, env=ENV, timeout=600)


def rows(p):
    return [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l.startswith("MISMATCH\tK4")]


# ---------------------------------------------------------------- probes

def probe_TOCTOU():
    """The '# writer path=... sha256=...' header names bytes that were NOT the ones compiled."""
    d = mkrepo("toctou")
    rev = seed(d, {"keep.txt": b"keep\n"})
    k = kit("toctou")
    tool = os.path.join(k, "souji-record-agreement.py")
    wpath = os.path.join(k, "souji-receipt-write.py")
    good = open(wpath, "rb").read()
    A, B = os.path.join(k, "A.py"), os.path.join(k, "B.py")
    open(A, "wb").write(good)
    evil = (b"def _truth_refusal(root):\n"
            b"    return 'RECEIPT-WORKTREE-STAT-CONCEALED: EVIL-WRITER-RAN'\n")
    open(B, "wb").write(evil)
    os.remove(wpath)
    os.symlink(A, wpath)
    proc = subprocess.Popen([sys.executable, "-B", tool, "--root", d, "--rev", rev],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=SCRATCH, env=ENV)
    header = proc.stdout.readline().decode().strip()          # the header is printed BEFORE the compile
    os.remove(wpath)                                          # swap the writer
    os.symlink(B, wpath)
    out, _ = proc.communicate(timeout=300)
    lines = out.decode("utf-8", "replace").splitlines()
    claim = header.split("sha256=")[-1]
    ran = any("EVIL-WRITER-RAN" in l for l in lines)
    print("header        :", header)
    print("header sha256 :", claim)
    print("bytes executed: sha256=%s  (EVIL writer ran: %s)" % (hashlib.sha256(evil).hexdigest(), ran))
    print("BOUND?        :", "NO — the header names bytes that did not run" if ran and
          claim != hashlib.sha256(evil).hexdigest() else "yes")
    return ran and claim != hashlib.sha256(evil).hexdigest()


def probe_STDOUT():
    """A writer that writes to stdout displaces its own stderr line from the K4 detail."""
    stub = ("import sys\n"
            "print('writer banner noise')\n"
            "def _truth_refusal(root):\n"
            "    raise AttributeError('SECRET-STDERR-EXCEPTION-NAME')\n")
    d = mkrepo("stdout")
    rev = seed(d, {"keep.txt": b"keep\n"})
    p = run(os.path.join(kit("stdout", stub.encode()), "souji-record-agreement.py"), d, rev)
    det = rows(p)[0].split("\t")[4] if rows(p) else ""
    print("detail        :", repr(det))
    print("stderr name present?", "SECRET-STDERR-EXCEPTION-NAME" in det)
    return "SECRET-STDERR-EXCEPTION-NAME" not in det


def probe_CLEAN():
    """A writer that prints the token CLEAN and then dies: the tool reports a CLEAN verdict."""
    stub = ("import sys\n"
            "print('CLEAN')\n"
            "raise AttributeError('never got to the truth check')\n")
    d = mkrepo("clean")
    rev = seed(d, {"keep.txt": b"keep\n"})
    p = run(os.path.join(kit("clean", stub.encode()), "souji-record-agreement.py"), d, rev)
    print("K4 rows       :", rows(p))
    print("=> the tool concluded the tracked bytes ARE verified (no K4 row):", not rows(p))
    return not rows(p)


def probe_INJECT():
    """A writer SystemExit message carrying a newline injects a second MISMATCH row."""
    stub = ("import sys\n"
            "def _truth_refusal(root):\n"
            "    sys.exit('x\\nMISMATCH\\tK4\\tINJECTED-ROW\\tuncommitted-path\\t??')\n")
    d = mkrepo("inject")
    rev = seed(d, {"keep.txt": b"keep\n"})
    p = run(os.path.join(kit("inject", stub.encode()), "souji-record-agreement.py"), d, rev)
    hits = K4RE.findall(p.stdout.decode("utf-8", "replace"))
    for h in hits:
        print("  counter-regex row:", h)
    print("rows the frozen counter's own regex sees:", len(hits))
    return len(hits) > 1


def probe_ESCAPE():
    """Two different files (literal backslash-n vs a real newline) collapse to one record cell."""
    d = mkrepo("escape")
    rev = seed(d, {"keep.txt": b"keep\n"})
    open(os.path.join(d, "same\\nname.txt"), "w").write("literal\n")
    open(os.path.join(d, "same\nname.txt"), "w").write("real\n")
    p = run(os.path.join(kit("escape"), "souji-record-agreement.py"), d, rev)
    cells = [x.split("\t")[2] for x in rows(p)]
    print("worktree      :", sorted(os.listdir(d)))
    print("record cells  :", cells)
    print("collide?      :", len(cells) == 2 and cells[0] == cells[1])
    return len(cells) == 2 and cells[0] == cells[1]


def probe_SPLITLINES():
    """A path carrying U+2028 tears one K4 record into two lines for a splitlines() reader."""
    d = mkrepo("split")
    rev = seed(d, {"keep.txt": b"keep\n"})
    open(os.path.join(d, "sep\u2028name.txt"), "w").write("x\n")
    p = run(os.path.join(kit("split"), "souji-record-agreement.py"), d, rev)
    out = p.stdout.decode("utf-8")
    pieces = [l for l in out.splitlines() if "MISMATCH\tK4" in l or "name.txt" in l]
    print("splitlines()  :", pieces)
    print("bytes         :", " ".join("%02x" % b for b in
          out[out.find("MISMATCH\tK4"):out.find("MISMATCH\tK4") + 40].encode()))
    print("torn?         :", len(pieces) > 1)
    return len(pieces) > 1


def probe_DETAIL():
    """The DETAIL cell is not escaped: the REAL writer's own refusal message carries a path with
    U+2028 and one K4 record is torn into two lines for a str.splitlines() reader.
    No forged writer -- the audited tree alone is enough."""
    d = mkrepo("detail")
    rev = seed(d, {"keep.txt": b"k\n"})
    open(os.path.join(d, "sep\u2028name.txt"), "w").write("v1\n")
    git(d, "add", "-A")
    git(d, "commit", "-q", "--no-verify", "-m", "seed")
    open(os.path.join(d, "sep\u2028name.txt"), "w").write("v2-longer\n")
    git(d, "update-index", "--skip-worktree", "sep\u2028name.txt")
    p = run(os.path.join(kit("detail"), "souji-record-agreement.py"), d, rev)
    txt = p.stdout.decode("utf-8")
    sl = txt.splitlines()
    row = [l for l in sl if l.startswith("MISMATCH\tK4")]
    cont = sl[sl.index(row[0]) + 1] if row else ""
    torn = bool(cont and not cont.startswith("MISMATCH"))
    print("K4 record (splitlines) :", repr(row[0]) if row else "-")
    print("continuation line      :", repr(cont))
    print("detail bytes carry U+2028 (e2 80 a8)?", b"\xe2\x80\xa8" in p.stdout)
    print("torn?                  :", torn)
    return torn


PROBES = {"TOCTOU": probe_TOCTOU, "STDOUT": probe_STDOUT, "CLEAN": probe_CLEAN,
          "INJECT": probe_INJECT, "ESCAPE": probe_ESCAPE, "SPLITLINES": probe_SPLITLINES,
          "DETAIL": probe_DETAIL}

# severity of each shape against the filed bytes; "sound" = no reader can be misled
SEVERITY = {"TOCTOU": "HIGH", "STDOUT": "sound (stderr wins; the exception name is carried)",
            "CLEAN": "MEDIUM", "INJECT": "MEDIUM", "ESCAPE": "sound (distinct spellings)",
            "SPLITLINES": "sound (record cell escaped)", "DETAIL": "LOW/MEDIUM"}

if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    want = sys.argv[sys.argv.index("--probe") + 1] if "--probe" in sys.argv else None
    print("tool under test:", TOOL, hashlib.sha256(open(TOOL, "rb").read()).hexdigest())
    for name, fn in PROBES.items():
        if want and name != want:
            continue
        print("\n=== %s ===  severity: %s" % (name, SEVERITY[name]))
        fn()
