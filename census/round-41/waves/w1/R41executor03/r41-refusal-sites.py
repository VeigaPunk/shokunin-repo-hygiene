#!/usr/bin/env python3
"""tests/fixtures/r41-refusal-sites.py — r41 C3: one class-asserting probe per refusal site.

Reaches every refusal site of tools/souji-worktree-drift.py (19 sites, 21 probe ids, frozen in
census/round-41/c3-sites.tsv). Each probe builds its own trigger under --work, runs the tool and
asserts BOTH exit code 2 AND the exact stderr token `REFUSAL <CLASS>:` for the class its one site
raises, so rewriting that site's class label turns exactly that probe red.

  python3 -B tests/fixtures/r41-refusal-sites.py --tool PATH --work DIR
  stdout: probe-<ID>=PASS|FAIL [detail] per probe id, then SUMMARY probes=<n> pass=<p> fail=<f>
  exit 0 iff fail=0, 1 otherwise, 2 when run as uid 0 (the EACCES probes P02a/P18 need a
  non-root uid; the fixture refuses rather than skipping them).

Python standard library only; no network; every write stays under --work.
"""
import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile

RUN_TIMEOUT = 60


class Ctx:
    def __init__(self, tool, work):
        self.tool = tool
        self.work = work

    def dir(self, name):
        path = os.path.join(self.work, name)
        os.makedirs(path)
        return path

    def run(self, argv):
        env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": self.work}
        try:
            proc = subprocess.run(["python3", "-B", self.tool] + argv, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, check=False, env=env,
                                  cwd=self.work, timeout=RUN_TIMEOUT)
        except subprocess.TimeoutExpired:
            return None, "", "tool exceeded %ds" % RUN_TIMEOUT
        return proc.returncode, proc.stdout, proc.stderr


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def verdict(res, cls):
    rc, _out, err = res
    if rc is None:
        return False, err
    if rc != 2:
        return False, "rc=%d want 2; stderr=%r" % (rc, err[:200])
    if ("REFUSAL %s:" % cls) not in err:
        return False, "stderr lacks 'REFUSAL %s:'; stderr=%r" % (cls, err[:200])
    return True, "REFUSAL %s rc=2" % cls


GHOST = "REPO\tghost\tregs=1\tprunable=0\n"


def record_cases(ctx, name, text):
    d = ctx.dir(name)
    root = os.path.join(d, "root")
    os.mkdir(root)
    rec = os.path.join(d, "rec.tsv")
    write(rec, text)
    return d, root, rec


def probe_P01(ctx):
    d = ctx.dir("P01")
    root = os.path.join(d, "root")
    os.mkdir(root)
    return verdict(ctx.run(["--root", root, "--record", os.path.join(d, "absent.tsv")]), "RECORD-MALFORMED")


def probe_P02a(ctx):
    d, root, rec = record_cases(ctx, "P02a", GHOST)
    os.chmod(rec, 0)
    try:
        return verdict(ctx.run(["--root", root, "--record", rec]), "RECORD-MISSING")
    finally:
        os.chmod(rec, 0o600)


def probe_P02b(ctx):
    d = ctx.dir("P02b")
    root = os.path.join(d, "root")
    os.mkdir(root)
    os.symlink("loop-b", os.path.join(d, "loop-a"))
    os.symlink("loop-a", os.path.join(d, "loop-b"))
    return verdict(ctx.run(["--root", root, "--record", os.path.join(d, "loop-a")]), "RECORD-MISSING")


def probe_P03(ctx):
    d = ctx.dir("P03")
    root = os.path.join(d, "root")
    os.mkdir(root)
    recdir = os.path.join(d, "recdir")
    os.mkdir(recdir)
    return verdict(ctx.run(["--root", root, "--record", recdir]), "RECORD-MALFORMED")


def parse_probe(ctx, name, text, cls):
    d, root, rec = record_cases(ctx, name, text)
    return verdict(ctx.run(["--root", root, "--record", rec]), cls)


def probe_P04(ctx):
    return parse_probe(ctx, "P04", GHOST + GHOST, "RECORD-MALFORMED")


def probe_P05(ctx):
    return parse_probe(ctx, "P05", GHOST + "this line is not census schema\n", "RECORD-MALFORMED")


def probe_P06(ctx):
    return parse_probe(ctx, "P06", "# only a comment\n\n   \n# another\n", "RECORD-EMPTY")


def probe_P07(ctx):
    return parse_probe(ctx, "P07", GHOST + "TOTAL\trepos=2\tregs=1\tprunable=0\n", "RECORD-MALFORMED")


def probe_P08(ctx):
    return parse_probe(ctx, "P08", GHOST + "TOTAL\trepos=1\tregs=2\tprunable=0\n", "RECORD-MALFORMED")


def probe_P09(ctx):
    return parse_probe(ctx, "P09", GHOST + "TOTAL\trepos=1\tregs=1\tprunable=1\n", "RECORD-MALFORMED")


def json_probe(ctx, name, make_json, cls):
    """Valid record naming one ghost row (ABSENT drift, no git needed); --json built by make_json(d)."""
    d, root, rec = record_cases(ctx, name, GHOST)
    target = make_json(d)
    return verdict(ctx.run(["--root", root, "--record", rec, "--json", target]), cls)


def probe_P10a(ctx):
    def make(d):
        fifo = os.path.join(d, "out.fifo")
        os.mkfifo(fifo)
        return fifo
    return json_probe(ctx, "P10a", make, "JSON-NOT-REGULAR")


def probe_P10b(ctx):
    def make(d):
        out = os.path.join(d, "outdir")
        os.mkdir(out)
        return out
    return json_probe(ctx, "P10b", make, "JSON-NOT-REGULAR")


def probe_P11(ctx):
    return json_probe(ctx, "P11", lambda d: "/dev/null", "JSON-NOT-REGULAR")


def probe_P12(ctx):
    d = ctx.dir("P12")
    rec = os.path.join(d, "rec.tsv")
    write(rec, GHOST)
    notdir = os.path.join(d, "not-a-directory")
    write(notdir, "plain file\n")
    return verdict(ctx.run(["--root", notdir, "--record", rec]), "USAGE")


def probe_P13(ctx):
    d = ctx.dir("P13")
    root = os.path.join(d, "root")
    os.mkdir(root)
    os.mkdir(os.path.join(d, "sibling"))
    rec = os.path.join(d, "rec.tsv")
    write(rec, "REPO\t../sibling\tregs=1\tprunable=0\n")
    return verdict(ctx.run(["--root", root, "--record", rec]), "RECORD-OUTSIDE-ROOT")


def probe_P14(ctx):
    d = ctx.dir("P14")
    root = os.path.join(d, "root")
    os.mkdir(root)
    ext = os.path.join(d, "ext")
    os.mkdir(ext)
    genv = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "HOME": d,
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "TMPDIR": ctx.work}
    init = subprocess.run(["git", "-C", ext, "init", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False, env=genv, timeout=RUN_TIMEOUT)
    if init.returncode != 0:
        return False, "git init failed: %r" % init.stderr[:200]
    repo = os.path.join(root, "r")
    os.mkdir(repo)
    write(os.path.join(repo, ".git"), "gitdir: %s\n" % os.path.join(ext, ".git"))
    rec = os.path.join(d, "rec.tsv")
    write(rec, "REPO\tr\tregs=1\tprunable=0\n")
    return verdict(ctx.run(["--root", root, "--record", rec]), "RECORD-OUTSIDE-ROOT")


def probe_P15(ctx):
    d, root, rec = record_cases(ctx, "P15", GHOST)
    return verdict(ctx.run(["--root", root, "--record", rec, "--json", rec]), "JSON-IS-RECORD")


def probe_P16(ctx):
    d, root, rec = record_cases(ctx, "P16", GHOST)
    return verdict(ctx.run(["--root", root, "--record", rec, "--json", os.path.join(root, "out.json")]),
                   "JSON-INSIDE-MEASURED-TREE")


def probe_P17(ctx):
    d, root, rec = record_cases(ctx, "P17", GHOST)
    out = os.path.join(d, "out.json")
    write(out, "keep\n")
    os.link(out, os.path.join(d, "alias.json"))
    ok, detail = verdict(ctx.run(["--root", root, "--record", rec, "--json", out]), "JSON-HARDLINKED")
    if ok:
        with open(out, encoding="utf-8") as handle:
            if handle.read() != "keep\n":
                return False, "hardlinked target was modified"
    return ok, detail


def probe_P18(ctx):
    d, root, rec = record_cases(ctx, "P18", GHOST)
    ro = os.path.join(d, "ro")
    os.mkdir(ro)
    os.chmod(ro, 0o555)
    try:
        return verdict(ctx.run(["--root", root, "--record", rec, "--json", os.path.join(ro, "out.json")]),
                       "JSON-UNWRITABLE")
    finally:
        os.chmod(ro, 0o755)


def probe_P19(ctx):
    d = ctx.dir("P19")
    root = os.path.join(d, "root")
    os.mkdir(root)
    rec = os.path.join(d, "rec.tsv")
    write(rec, GHOST)
    return verdict(ctx.run(["--root", root, "--record", rec, "--timeout", "0"]), "USAGE")


PROBES = [
    ("P01", probe_P01), ("P02a", probe_P02a), ("P02b", probe_P02b), ("P03", probe_P03),
    ("P04", probe_P04), ("P05", probe_P05), ("P06", probe_P06), ("P07", probe_P07),
    ("P08", probe_P08), ("P09", probe_P09), ("P10a", probe_P10a), ("P10b", probe_P10b),
    ("P11", probe_P11), ("P12", probe_P12), ("P13", probe_P13), ("P14", probe_P14),
    ("P15", probe_P15), ("P16", probe_P16), ("P17", probe_P17), ("P18", probe_P18),
    ("P19", probe_P19),
]


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r41-refusal-sites: refusing to run as uid 0: the EACCES probes (P02a, P18) "
                         "change class under a privileged runner\n")
        return 2
    if not os.path.isdir(args.work):
        sys.stderr.write("r41-refusal-sites: --work %s is not a directory\n" % args.work)
        return 2
    work = tempfile.mkdtemp(prefix="r41-sites.", dir=os.path.realpath(args.work))
    ctx = Ctx(os.path.realpath(args.tool), work)
    passed = failed = 0
    try:
        for pid, fn in PROBES:
            try:
                ok, detail = fn(ctx)
            except Exception as exc:  # a probe that cannot build or run its trigger is a FAIL
                ok, detail = False, "probe error: %s: %s" % (type(exc).__name__, exc)
            print("probe-%s=%s %s" % (pid, "PASS" if ok else "FAIL", detail.replace("\n", " ")))
            if ok:
                passed += 1
            else:
                failed += 1
        print("SUMMARY probes=%d pass=%d fail=%d" % (len(PROBES), passed, failed))
    finally:
        for dirpath, dirnames, _files in os.walk(work):
            for dn in dirnames:
                try:
                    os.chmod(os.path.join(dirpath, dn), stat.S_IRWXU)
                except OSError:
                    pass
        shutil.rmtree(work, ignore_errors=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
