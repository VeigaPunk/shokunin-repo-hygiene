#!/usr/bin/env python3
"""souji r89 C2 fixture: the K4 delegation's index-flag failure detail is ONE escaped line that keeps both ends of
the writer's stderr, measured through the tool's public path.

Each case runs a copy of the tool under test beside a fake receipt writer in a hermetic scratch repository. The fake
writer's `git()` fails the delegated `ls-files -v -z` read with a chosen stderr, so the bootstrap's FLAGFAIL branch
fires with no lane byte involved. The tool is run as a subprocess and its `MISMATCH\tK4\t...` records are read back
exactly as a line-oriented consumer would.

Cases:
  KFF1 short     a single-line message: the detail names it.
  KFF2 trace     a three-line traceback ending `AttributeError: boom`: the detail is ONE physical line that names the
                 exception (the r87 tool printed it raw, so the row split and the K4 line lost the name).
  KFF3 long      a 400-character line starting `AttributeError: `: the head (the type name) and the tail survive the
                 200-character bound (the r87 tool kept the tail only).
  KFF4 controls  a line carrying SOH, NEL and U+2028: the detail escapes all three and stays one physical line
                 (the r87 tool embedded them raw; `str.splitlines()` tears NEL and U+2028).
  KFF5 empty     empty stderr: `no stderr`, never an empty parenthesis.
  KFC1 clean     the delegated ls-files read succeeds: no K4 row (a blanket refusal is not a gain).
  KFC2 refused   the writer refuses with a second, forged MISMATCH line: one escaped REFUSED detail, no injected row.
  KFF6 badbyte   stderr carrying an invalid UTF-8 byte: one escaped line, surrounding text kept (S88Sentinel F1).
  KFF7 literal   stderr carrying the literal escape spelling: the detail differs from KFF6 (injectivity).
  KFF8 headctl   25 leading SOH bytes then `AttributeError: boom`: the type name stays in the head (S88Sentinel F2).

The same table runs on `--before` (the r87 tool bytes): every case the before tool fails is the do-nothing control.
Exit 0 iff every case passes on `--tool` and the before tool passes strictly fewer; 1 otherwise; 2 on usage or a
fixture failure. Writes only under --work (never /tmp), removes what it builds, and reads the lane read-only.

Stdlib only. Python 3.14, git 2.56.0; the fixture repo is synthetic and hermetic.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

FAKE_WRITER = '''# r89 fake receipt writer for the K4 delegation fixture (one rule: no file, no network)
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    mode = os.environ.get("R89_STDERR_MODE", "short")
    if mode == "clean":
        return P(0, b"H a.txt\\0")
    err = {
        "short": b"fatal: cannot read index\\n",
        "trace": b"Traceback (most recent call last):\\n  File \\"w\\", line 1\\nAttributeError: boom\\n",
        "long": b"AttributeError: " + b"x" * 380 + b"\\n",
        "controls": b"fatal: \\x01 \\x85 \\xe2\\x80\\xa8 marker\\n",
        "empty": b"",
        "badbyte": b"bad \\xff tail\\n",
        "literal": b"literal \\\\xff tail\\n",
        "headctl": b"\\x01" * 25 + b"AttributeError: boom" + b"y" * 240 + b"\\n",
    }[mode]
    return P(1, b"", err)


def _truth_refusal(root):
    if os.environ.get("R89_REFUSED") == "1":
        raise SystemExit("r89 refused: bad\\nMISMATCH\\tK4\\t.\\tforged\\tinjected")
    return ""


def _flag_refusal(*args):
    return None
'''

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r89 fixture", "GIT_AUTHOR_EMAIL": "fixture@r89.invalid",
            "GIT_COMMITTER_NAME": "r89 fixture", "GIT_COMMITTER_EMAIL": "fixture@r89.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})


class FixtureError(Exception):
    pass


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_kit(root, tool):
    """A tool copy beside a fake writer, and a hermetic repo with one commit."""
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(tool, copy)
    with open(os.path.join(tools, "souji-receipt-write.py"), "w", encoding="utf-8") as f:
        f.write(FAKE_WRITER)
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("seed\n")
    git(repo, "add", "--", "a.txt")
    git(repo, "commit", "-q", "--no-verify", "-m", "r89 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


def run_case(kit, mode, refused=False):
    toolcopy, repo, rev = kit
    env = dict(ENV)
    env["R89_STDERR_MODE"] = mode
    env["R89_REFUSED"] = "1" if refused else "0"
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out = p.stdout.decode("utf-8", "backslashreplace")
    rows = []
    for line in out.split("\n"):
        if not line.startswith("MISMATCH\tK4\t"):
            continue
        cells = line.split("\t", 4)
        rows.append(cells[4] if len(cells) == 5 else "<short-row>")
    return out, rows


def case_short(out, rows):
    return len(rows) == 1 and "fatal: cannot read index" in rows[0]


def case_trace(out, rows):
    return (len(rows) == 1 and "AttributeError: boom" in rows[0] and "\\n" in rows[0]
            and "\n  File " not in out)


def case_long(out, rows):
    return (len(rows) == 1 and "AttributeError" in rows[0] and "\u2026" in rows[0]
            and len(rows[0]) <= 260)


def case_controls(out, rows):
    return (len(rows) == 1 and "\\x01" in rows[0] and "\\x85" in rows[0] and "\\u2028" in rows[0]
            and "\x01" not in out and "\x85" not in out and "\u2028" not in out)


def case_empty(out, rows):
    return len(rows) == 1 and "no stderr" in rows[0]


def case_clean(out, rows):
    return len(rows) == 0


def case_badbyte(out, rows):
    # KFF6 (S88Sentinel F1): the raw byte 0xFF renders as ONE backslash spelling (exactly one backslash before "xff").
    bs = chr(92)
    return len(rows) == 1 and "bad " in rows[0] and rows[0].count(bs + "xff") == 1 and rows[0].count(bs * 2 + "xff") == 0 and "tail" in rows[0]



def case_literal(out, rows):
    # KFF7 (S88Sentinel F1): the literal characters render with a DOUBLED backslash (the backslash doubled, none bare).
    bs = chr(92)
    return len(rows) == 1 and "literal " in rows[0] and rows[0].count(bs * 2 + "xff") == 1 and rows[0].count(bs + "xff") == 1


def case_headctl(out, rows):
    # KFF8 (S88Sentinel F2): 25 leading control bytes must not consume the head; the type name stays visible.
    return len(rows) == 1 and "AttributeError" in rows[0] and "boom" in rows[0]



def case_refused(out, rows):
    return len(rows) == 1 and "the receipt writer refused the tree" in rows[0] and "injected" not in out


CASES = (
    ("KFF1", "short", False, case_short),
    ("KFF2", "trace", False, case_trace),
    ("KFF3", "long", False, case_long),
    ("KFF4", "controls", False, case_controls),
    ("KFF5", "empty", False, case_empty),
    ("KFC1", "clean", False, case_clean),
    ("KFC2", "short", True, case_refused),
    ("KFF6", "badbyte", False, case_badbyte),
    ("KFF7", "literal", False, case_literal),
    ("KFF8", "headctl", False, case_headctl),
)


def score(kit):
    result = {}
    for cid, mode, refused, check in CASES:
        try:
            out, rows = run_case(kit, mode, refused)
            result[cid] = bool(check(out, rows))
        except (OSError, subprocess.SubprocessError, KeyError) as exc:
            print(f"# case {cid} fixture error: {type(exc).__name__}: {exc}")
            result[cid] = False
    return result


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, help="tools/souji-record-agreement.py under test")
    ap.add_argument("--before", required=True, help="the r87 tool bytes (do-nothing control)")
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("R89-FIXTURE-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"R89-FIXTURE-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    tool, before = os.path.abspath(ns.tool), os.path.abspath(ns.before)
    print(f"# tool path={tool} sha256={sha(tool)}")
    print(f"# before path={before} sha256={sha(before)}")
    print(f"# fixture sha256={sha(os.path.abspath(__file__))}")
    try:
        after_kit = make_kit(os.path.join(work, "after"), tool)
        before_kit = make_kit(os.path.join(work, "before"), before)
    except (FixtureError, OSError, subprocess.SubprocessError) as exc:
        print(f"R89-FIXTURE-FATAL: fixture: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    after, old = score(after_kit), score(before_kit)
    # KFF6/KFF7 injectivity pair: the bad-byte detail and the literal detail must differ on the tool under test.
    _o6, _r6 = run_case(after_kit, "badbyte", False)
    _o7, _r7 = run_case(after_kit, "literal", False)
    _pair_ok = _r6 != _r7 and len(_r6) == 1 and len(_r7) == 1
    after = dict(after, KFF6=bool(after["KFF6"] and _pair_ok), KFF7=bool(after["KFF7"] and _pair_ok))
    for cid, _mode, _refused, _check in CASES:
        print(f"CASE {cid} tool={'pass' if after[cid] else 'fail'} before={'pass' if old[cid] else 'fail'}")
    a, b = sum(after.values()), sum(old.values())
    print(f"SUMMARY cases={len(CASES)} tool_pass={a} before_pass={b}")
    if a != len(CASES):
        print("R89-FIXTURE-FAIL: the tool under test does not pass every case", file=sys.stderr)
        return 1
    if b >= a:
        print("R89-FIXTURE-FAIL: the do-nothing control passes as many cases (no measured delta)",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
