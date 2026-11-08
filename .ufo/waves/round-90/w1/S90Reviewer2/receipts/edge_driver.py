#!/usr/bin/env python3
"""S90Reviewer2 edge probe: the K4 FLAGFAIL detail cell for byte/character payloads.

Drives the tool under test through its PUBLIC K4 path (fake receipt writer beside a copy of
the tool, hermetic git repo) and prints, for each stderr payload: the 5th MISMATCH cell as
`repr` plus the count of the two spellings.  A direct `_one_line_bytes` cell is printed too,
so a window effect can be separated from the escaping rule.
"""
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

FAKE_WRITER = '''# edge fake writer (one rule: no file, no network)
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    return P(1, b"", bytes.fromhex(os.environ["R90X_STDERR_HEX"]))


def _truth_refusal(root):
    return ""


def _flag_refusal(*args):
    return None
'''

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r90 edge", "GIT_AUTHOR_EMAIL": "edge@r90.invalid",
            "GIT_COMMITTER_NAME": "r90 edge", "GIT_COMMITTER_EMAIL": "edge@r90.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise SystemExit(f"refusing git -C {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise SystemExit(f"git failed: {p.stderr.decode()[:300]}")
    return p.stdout.decode().strip()


def make_kit(root, tool):
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
    git(repo, "commit", "-q", "--no-verify", "-m", "r90 edge seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


def run_payload(kit, payload):
    toolcopy, repo, rev = kit
    env = dict(ENV)
    env["R90X_STDERR_HEX"] = payload.hex()
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


PAYLOADS = [
    ("raw85 short", b"fatal: nel \x85 marker\n"),
    ("charU0085 short", b"fatal: nel \xc2\x85 marker\n"),
    ("both short", b"fatal: nel \x85 and \xc2\x85 marker\n"),
    ("literal x85", b"fatal: nel \\x85 marker\n"),
    ("literal u0085", b"fatal: nel \\u0085 marker\n"),
    ("raw85 x2", b"fatal: \x85\x85 marker\n"),
    ("charU0085 x2", b"fatal: \xc2\x85\xc2\x85 marker\n"),
    ("char after 99x", b"x" * 99 + b"\xc2\x85" + b" marker\n"),
    ("cut char head (99x+C285+99y)", b"x" * 99 + b"\xc2\x85" + b"y" * 99),
    ("cut char tail (101p+C285+98s)", b"p" * 101 + b"\xc2\x85" + b"s" * 98),
    ("twin with 86 (101p+86 85+98s)", b"p" * 101 + b"\x86\x85" + b"s" * 98),
    ("long char mid", b"head " + b"m" * 150 + b"\xc2\x85" + b" tail " + b"t" * 100),
    ("long raw mid", b"head " + b"m" * 150 + b"\x85" + b" tail " + b"t" * 100),
    ("long both", b"a" * 90 + b"\x85" + b"b" * 30 + b"\xc2\x85" + b"c" * 90),
]


def main():
    tool, work = sys.argv[1], os.path.abspath(sys.argv[2])
    kit = make_kit(os.path.join(work, "kit"), tool)
    for name, payload in PAYLOADS:
        out, rows = run_payload(kit, payload)
        cell = rows[0] if len(rows) == 1 else f"<rows={len(rows)}>"
        bs = chr(92)
        print(f"PAYLOAD {name!r} len={len(payload)} hex={payload.hex()}")
        print(f"  rows={len(rows)} cell={cell!r}")
        if len(rows) == 1:
            c = rows[0]
            print(f"  count_x85={c.count(bs + 'x85')} count_u0085={c.count(bs + 'u0085')} "
                  f"physical_lines={c.count(chr(10)) + 1}")
    print("done")


if __name__ == "__main__":
    main()
