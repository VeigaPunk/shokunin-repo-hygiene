#!/usr/bin/env python3
"""S88ScoutSources round-88 C2 reproducer: does a C1 control byte that is NOT a
str.splitlines boundary reach the K4 detail raw?

Uses the tool's OWN public path (a tool copy beside a fake writer), exactly as
tests/fixtures/r88-k4-flagfail.py does. Writes only under its --work dir.
"""
import os, shutil, subprocess, sys

LANE = os.environ.get("SOUJI_LANE", "/home/vgpnk/Projects/shokunin/souji-shokunin")

FAKE = r"""
class P:
    def __init__(self, rc, out=b"", err=b""): self.returncode, self.stdout, self.stderr = rc, out, err
def git(*a, **k):
    # SOH (0x01, C0), NEL (0x85, C1) and U+2028 are all str.splitlines boundaries;
    # U+009F is a C1 control that is NOT a splitlines boundary.
    err = b"fatal: \x01 \x85 \xe2\x80\xa8 \xc2\x9f marker\n"
    return P(1, b"", err)
def _truth_refusal(root): return ""
def _flag_refusal(*a): return None
"""

def main(argv):
    work = os.path.abspath(argv[0])
    if os.path.exists(work): shutil.rmtree(work)
    tools = os.path.join(work, "tools"); os.makedirs(tools)
    shutil.copyfile(os.path.join(LANE, "tools", "souji-record-agreement.py"),
                    os.path.join(tools, "souji-record-agreement.py"))
    open(os.path.join(tools, "souji-receipt-write.py"), "w").write(FAKE)
    repo = os.path.join(work, "repo"); os.makedirs(repo)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
                "GIT_AUTHOR_NAME": "r88", "GIT_AUTHOR_EMAIL": "r@x.invalid",
                "GIT_COMMITTER_NAME": "r88", "GIT_COMMITTER_EMAIL": "r@x.invalid",
                "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})
    def git(*a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, env=env).stdout
    git("init", "-q")
    open(os.path.join(repo, "a.txt"), "w").write("seed\n")
    git("add", "--", "a.txt"); git("commit", "-q", "--no-verify", "-m", "seed")
    rev = git("rev-parse", "HEAD").decode().strip()
    p = subprocess.run([sys.executable, "-B", os.path.join(tools, "souji-record-agreement.py"),
                        "--root", repo, "--rev", rev], capture_output=True, env=env)
    out = p.stdout.decode("utf-8", "backslashreplace")
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    SOH, NEL, LS, APC = chr(1), chr(0x85), chr(0x2028), chr(0x9f)
    print("K4 rows: %d" % len(rows))
    for r in rows:
        cells = r.split("\t", 4)
        detail = cells[4] if len(cells) == 5 else "<short-row>"
        print("detail repr: %r" % detail)
        print("raw SOH  in output: %s   (escaped as \\x01: %s)" % (SOH in out, "\\x01" in detail))
        print("raw NEL  in output: %s   (escaped as \\x85: %s)" % (NEL in out, "\\x85" in detail))
        print("raw U+2028 in output: %s   (escaped as \\u2028: %s)" % (LS in out, "\\u2028" in detail))
        print("raw U+009F (C1, NOT a splitlines boundary) in output: %s" % (APC in out))
        print("detail splitlines count: %d  -> the cell is still ONE physical line" % len(detail.splitlines()))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
