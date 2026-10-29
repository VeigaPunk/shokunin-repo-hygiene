#!/usr/bin/env python3
"""r42-drift-conditions.py — r42 C3: condition-level behaviours of tools/souji-worktree-drift.py.

Every case builds a scenario of its own under --work, runs `python3 -B <tool>` as a subprocess and asserts
only what the run shows (exit code, stdout/stderr, the --json file's bytes). One probe per condition:
  errno        a FIFO record must be refused, not block the tool
  containment  a sibling directory sharing a name prefix with --root is outside it (record row and gitdir)
  timeout      --timeout 1 is valid; the default is long enough for a slow git; a list timeout is reported
  argparse     --root and --record are required arguments
  discovery    a symlinked child of --root is not an unrecorded repository
  record       a REPO row accepts a multi-digit regs count; invalid UTF-8 in a name is replaced, not escaped
  write        a longer old --json file leaves no tail after the write
  decode       the replacement-decoded name finds the directory it spells
Prints case-<name>=PASS|FAIL and SUMMARY cases=<n> pass=<p> fail=<f>; exit 0 iff fail=0.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

CASE_TIMEOUT = 60


def sh_git(path, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
           "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["git", "-C", path] + list(args), env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=CASE_TIMEOUT, check=False)


def mkrepo(path):
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    os.makedirs(path)
    p = sh_git(path, "init", "-q")
    if p.returncode != 0:
        raise RuntimeError("git init failed: %r" % p.stderr)
    top = sh_git(path, "rev-parse", "--show-toplevel").stdout.decode("utf-8", "replace").strip()
    if os.path.realpath(top) != os.path.realpath(path):
        raise RuntimeError("fixture repo is not its own toplevel")


def row(name, regs=1, prunable=0):
    return b"REPO\t" + name + b"\tregs=%d\tprunable=%d\n" % (regs, prunable)


class Scenario:
    """A fresh <case>/root fleet, <case>/rec record directory and <case>/out output directory."""

    def __init__(self, base, name):
        self.dir = os.path.join(base, name)
        self.root = os.path.join(self.dir, "root")
        self.rec = os.path.join(self.dir, "rec")
        self.out = os.path.join(self.dir, "out")
        for d in (self.root, self.rec, self.out):
            os.makedirs(d)

    def record(self, body, name="record.tsv"):
        path = os.path.join(self.rec, name)
        with open(path, "wb") as handle:
            handle.write(body)
        return path

    def wrapper(self, script):
        """A `git` shim directory placed first on PATH; `script` is a sh body, REAL is the real git."""
        d = os.path.join(self.dir, "bin")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "git")
        with open(path, "w") as handle:
            handle.write("#!/bin/sh\nREAL=%s\n%s\n" % (shutil.which("git") or "/usr/bin/git", script))
        os.chmod(path, 0o755)
        return d


def run_tool(tool, args, cwd, path_prefix=None):
    path = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
    if path_prefix:
        path = path_prefix + ":" + path
    env = {"PATH": path, "PYTHONUTF8": "1", "HOME": cwd, "TMPDIR": cwd}
    try:
        p = subprocess.run(["python3", "-B", tool] + args, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=CASE_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        return None, "", "", True
    return (p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), False)


def basic(tool, sc, record, extra=None, **kw):
    return run_tool(tool, ["--root", sc.root, "--record", record] + (extra or []), sc.dir, **kw)


def refusal(res, cls):
    rc, _out, err, hung = res
    ok = (not hung) and rc == 2 and ("REFUSAL %s:" % cls) in err and "Traceback" not in err
    return ok, "rc=%s hung=%s refusal=%s" % (rc, hung, cls in err)


# ---------------------------------------------------------------- cases

def case_errno_fifo_record(tool, base):
    sc = Scenario(base, "errno")
    mkrepo(os.path.join(sc.root, "a"))
    fifo = os.path.join(sc.rec, "fifo.tsv")
    os.mkfifo(fifo)
    res = basic(tool, sc, fifo, ["--skip-unrecorded"])
    return refusal(res, "RECORD-MALFORMED")


def case_containment_record_sibling(tool, base):
    sc = Scenario(base, "contrec")
    mkrepo(os.path.join(sc.root, "a"))
    sib = sc.root + "-sibling"
    os.makedirs(sib)
    with open(os.path.join(sib, ".git"), "w") as handle:  # work tree outside root, its gitdir inside root
        handle.write("gitdir: " + os.path.join(sc.root, "a", ".git") + "\n")
    rec = sc.record(row(b"../root-sibling"))
    return refusal(basic(tool, sc, rec, ["--skip-unrecorded"]), "RECORD-OUTSIDE-ROOT")


def case_containment_gitdir_sibling(tool, base):
    sc = Scenario(base, "contgit")
    gd = sc.root + "-gd"
    os.makedirs(os.path.join(gd, "objects"))
    os.makedirs(os.path.join(gd, "refs"))
    with open(os.path.join(gd, "HEAD"), "w") as handle:
        handle.write("ref: refs/heads/main\n")
    os.makedirs(os.path.join(sc.root, "r"))
    with open(os.path.join(sc.root, "r", ".git"), "w") as handle:
        handle.write("gitdir: " + gd + "\n")
    rec = sc.record(row(b"r"))
    return refusal(basic(tool, sc, rec, ["--skip-unrecorded"]), "RECORD-OUTSIDE-ROOT")


def case_timeout_one_accepted(tool, base):
    sc = Scenario(base, "to1")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a"))
    rc, out, err, hung = basic(tool, sc, rec, ["--timeout", "1", "--skip-unrecorded"])
    ok = (not hung) and rc in (0, 1) and "REFUSAL" not in err and "Traceback" not in err
    return ok, "rc=%s hung=%s" % (rc, hung)


def case_timeout_default_tolerates_slow_git(tool, base):
    sc = Scenario(base, "todef")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a"))
    shim = sc.wrapper('sleep 2\nexec "$REAL" "$@"')
    rc, out, err, hung = basic(tool, sc, rec, ["--skip-unrecorded"], path_prefix=shim)
    ok = (not hung) and rc == 0 and "UNREACHABLE" not in out + err and "Traceback" not in err
    return ok, "rc=%s hung=%s unreachable=%s" % (rc, hung, "UNREACHABLE" in out + err)


def case_timeout_list_reported_unreachable(tool, base):
    sc = Scenario(base, "tolist")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a"))
    shim = sc.wrapper('case "$*" in *worktree*list*) exec sleep 30;; esac\nexec "$REAL" "$@"')
    rc, out, err, hung = basic(tool, sc, rec, ["--timeout", "1", "--skip-unrecorded"], path_prefix=shim)
    ok = (not hung) and rc == 1 and "UNREACHABLE" in out + err and "Traceback" not in err
    return ok, "rc=%s hung=%s unreachable=%s tb=%s" % (rc, hung, "UNREACHABLE" in out + err, "Traceback" in err)


def case_list_nonzero_reported(tool, base):
    sc = Scenario(base, "listrc")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a"))
    shim = sc.wrapper('case "$*" in *worktree*list*) echo "fatal: forced" >&2; exit 128;; esac\n'
                      'exec "$REAL" "$@"')
    rc, out, err, hung = basic(tool, sc, rec, ["--skip-unrecorded"], path_prefix=shim)
    ok = (not hung) and rc == 1 and "UNREACHABLE" in out + err and "Traceback" not in err
    return ok, "rc=%s hung=%s unreachable=%s" % (rc, hung, "UNREACHABLE" in out + err)


def case_argparse_root_required(tool, base):
    sc = Scenario(base, "noroot")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a"))
    rc, out, err, hung = run_tool(tool, ["--record", rec, "--skip-unrecorded"], sc.root)
    ok = (not hung) and rc == 2 and "required" in err and "--root" in err and "Traceback" not in err
    return ok, "rc=%s hung=%s" % (rc, hung)


def case_argparse_record_required(tool, base):
    sc = Scenario(base, "norec")
    mkrepo(os.path.join(sc.root, "a"))
    rc, out, err, hung = run_tool(tool, ["--root", sc.root, "--skip-unrecorded"], sc.dir)
    ok = (not hung) and rc == 2 and "required" in err and "--record" in err and "Traceback" not in err \
        and "REFUSAL" not in err
    return ok, "rc=%s hung=%s" % (rc, hung)


def case_discovery_skips_symlinked_child(tool, base):
    sc = Scenario(base, "disc")
    mkrepo(os.path.join(sc.root, "a"))
    ext = os.path.join(sc.dir, "ext", "repo")
    mkrepo(ext)
    os.symlink(ext, os.path.join(sc.root, "link"))
    rec = sc.record(row(b"a"))
    rc, out, err, hung = basic(tool, sc, rec)
    ok = (not hung) and rc == 0 and "UNRECORDED" not in out + err and "Traceback" not in err
    return ok, "rc=%s hung=%s unrecorded=%s" % (rc, hung, "UNRECORDED" in out + err)


def case_record_multidigit_regs(tool, base):
    sc = Scenario(base, "regs10")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a", regs=10))
    rc, out, err, hung = basic(tool, sc, rec, ["--skip-unrecorded"])
    ok = (not hung) and rc == 1 and "REGS-CHANGED" in out + err and "RECORD-MALFORMED" not in err \
        and "Traceback" not in err
    return ok, "rc=%s hung=%s" % (rc, hung)


def case_record_invalid_utf8_name_replaced(tool, base):
    sc = Scenario(base, "utf8")
    mkrepo(os.path.join(sc.root, "a"))
    mkrepo(os.path.join(sc.root.encode(), b"bad\xef\xbf\xbdname"))  # the directory U+FFFD spells
    rec = sc.record(row(b"a") + row(b"bad\xffname"))
    rc, out, err, hung = basic(tool, sc, rec, ["--skip-unrecorded"])
    ok = (not hung) and rc == 0 and "ABSENT" not in out + err and "Traceback" not in err
    return ok, "rc=%s hung=%s absent=%s" % (rc, hung, "ABSENT" in out + err)


def case_write_truncates_old_json(tool, base):
    sc = Scenario(base, "wr")
    mkrepo(os.path.join(sc.root, "a"))
    rec = sc.record(row(b"a"))
    target = os.path.join(sc.out, "out.json")
    with open(target, "wb") as handle:
        handle.write(b"X" * 20000)
    rc, out, err, hung = basic(tool, sc, rec, ["--skip-unrecorded", "--json", target])
    with open(target, "rb") as handle:
        data = handle.read()
    try:
        json.loads(data.decode("utf-8"))
        parsed = True
    except ValueError:
        parsed = False
    ok = (not hung) and rc == 0 and parsed and b"XXXX" not in data and "Traceback" not in err
    return ok, "rc=%s hung=%s parsed=%s bytes=%d" % (rc, hung, parsed, len(data))


def case_baseline_clean_run(tool, base):
    sc = Scenario(base, "clean")
    mkrepo(os.path.join(sc.root, "a"))
    mkrepo(os.path.join(sc.root, "b"))
    rec = sc.record(row(b"a") + row(b"b") + b"TOTAL\trepos=2\tregs=2\tprunable=0\n")
    rc, out, err, hung = basic(tool, sc, rec)
    return (not hung) and rc == 0 and "Traceback" not in err, "rc=%s hung=%s" % (rc, hung)


CASES = (
    ("baseline-clean-run", case_baseline_clean_run),
    ("errno-fifo-record-refused", case_errno_fifo_record),
    ("containment-record-prefix-sibling", case_containment_record_sibling),
    ("containment-gitdir-prefix-sibling", case_containment_gitdir_sibling),
    ("timeout-one-accepted", case_timeout_one_accepted),
    ("timeout-default-tolerates-slow-git", case_timeout_default_tolerates_slow_git),
    ("timeout-list-reported-unreachable", case_timeout_list_reported_unreachable),
    ("list-nonzero-reported", case_list_nonzero_reported),
    ("argparse-root-required", case_argparse_root_required),
    ("argparse-record-required", case_argparse_record_required),
    ("discovery-skips-symlinked-child", case_discovery_skips_symlinked_child),
    ("record-multidigit-regs", case_record_multidigit_regs),
    ("write-truncates-longer-old-json", case_write_truncates_old_json),
    ("decode-invalid-utf8-name-replaced", case_record_invalid_utf8_name_replaced),
)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r42-drift-conditions: refusing to run as root\n")
        return 2
    tool = os.path.realpath(a.tool)
    os.makedirs(a.work, exist_ok=True)
    base = os.path.realpath(tempfile.mkdtemp(prefix="r42-cond.", dir=a.work))
    passed = failed = 0
    try:
        for name, fn in CASES:
            try:
                ok, detail = fn(tool, base)
            except Exception as exc:  # a scenario that cannot be built is a failed case, never a traceback
                ok, detail = False, "scenario error %s: %s" % (type(exc).__name__, exc)
            passed += bool(ok)
            failed += not ok
            print("case-%s=%s %s" % (name, "PASS" if ok else "FAIL", detail))
            sys.stdout.flush()
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("SUMMARY cases=%d pass=%d fail=%d" % (passed + failed, passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
