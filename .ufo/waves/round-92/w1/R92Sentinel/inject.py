#!/usr/bin/env python3
"""R92Sentinel: public-path injection probe. A hermetic fixture-style kit (tool copy + fake writer that returns a
chosen stderr via a payload FILE, since 10 MB cannot ride an environment variable). Runs the tool as a subprocess
and reads back its MISMATCH\\tK4 rows the way a line-oriented consumer does."""
import os
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
SCR = "/fast/scratch/hyaku/souji-r92/R92Sentinel"
KIT = os.path.join(SCR, "inj", "kit")
PAY = os.path.join(SCR, "inj", "payload.bin")
LANE_TOOL = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py"

WRITER = '''# R92Sentinel fake receipt writer: git() returns the payload file bytes as stderr with rc 1
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    with open(os.environ["S_PAYLOAD"], "rb") as f:
        return P(1, b"", f.read())


def _truth_refusal(root):
    return ""


def _flag_refusal(*args):
    return None
'''

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r92 sentinel", "GIT_AUTHOR_EMAIL": "sentinel@r92.invalid",
            "GIT_COMMITTER_NAME": "r92 sentinel", "GIT_COMMITTER_EMAIL": "sentinel@r92.invalid",
            "GIT_AUTHOR_DATE": "2026-11-09T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-09T00:00:00Z"})


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise SystemExit(f"git {args} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def make_kit():
    if os.path.exists(KIT):
        shutil.rmtree(KIT)
    tools = os.path.join(KIT, "tools")
    os.makedirs(tools)
    shutil.copyfile(LANE_TOOL, os.path.join(tools, "souji-record-agreement.py"))
    with open(os.path.join(tools, "souji-receipt-write.py"), "w", encoding="utf-8") as f:
        f.write(WRITER)
    repo = os.path.join(KIT, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    assert git(repo, "rev-parse", "--show-toplevel") == os.path.realpath(repo), "fixture toplevel mismatch"
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("seed\n")
    git(repo, "add", "--", "a.txt")
    git(repo, "commit", "-q", "--no-verify", "-m", "r92 sentinel seed")
    return os.path.join(tools, "souji-record-agreement.py"), repo, git(repo, "rev-parse", "HEAD")


SEP = ("\n", "\r", "\t", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")


def run(kit, payload, label):
    toolcopy, repo, rev = kit
    with open(PAY, "wb") as f:
        f.write(payload)
    env = dict(ENV)
    env["S_PAYLOAD"] = PAY
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    dt = time.perf_counter() - t0
    out = p.stdout.decode("utf-8", "backslashreplace")
    lines = out.split("\n")
    rows = [l for l in lines if l.startswith("MISMATCH\tK4\t")]
    mm_any = [l for l in lines if l.startswith("MISMATCH")]
    fields = [len(r.split("\t")) for r in rows]
    cell = rows[0].split("\t", 4)[4] if len(rows) == 1 and fields[0] >= 5 else None
    raw_seps = [s for s in SEP if cell is not None and s in cell]
    ctrl = [hex(ord(c)) for c in (cell or "") if ord(c) < 0x20 or ord(c) == 0x7f]
    inj = bool(cell and ("forged" in cell or "injected" in cell) and "MISMATCH" in cell and "\\n" not in cell)
    print(f"CASE {label} payload_bytes={len(payload)} rc={p.returncode} t={dt:.2f}s stdout_lines={len(lines)} "
          f"mismatch_lines_any={len(mm_any)} k4_rows={len(rows)} row_fields={fields} "
          f"raw_separators_in_cell={raw_seps} raw_ctrl_in_cell={ctrl} "
          f"cell_chars={len(cell) if cell is not None else None} "
          f"forged_text_in_cell_unescaped_check={'SUSPECT' if inj else 'ok'} stderr_tail={p.stderr.decode('utf-8','replace')[-160:]!r}")
    print(f"    cell_head={(cell or '')[:150]!r}")
    print(f"    cell_tail={(cell or '')[-120:]!r}")
    return rows, cell


def main():
    kit = make_kit()
    print(f"KIT tool_sha256={__import__('hashlib').sha256(open(kit[0],'rb').read()).hexdigest()[:16]} repo={kit[1]} rev={kit[2][:12]}")
    inj = b"MISMATCH\tK4\t.\tforged\tinjected\n"
    small = [
        ("control-empty", b""),
        ("nl-injection", b"fatal: x\n" + inj),
        ("cr-injection", b"fatal: x\r" + inj.replace(b"\n", b"\r\n")),
        ("nel-char-injection", b"fatal: x\xc2\x85" + inj[:-1]),
        ("nel-byte-injection", b"fatal: x\x85" + inj[:-1]),
        ("ls-injection", b"fatal: x\xe2\x80\xa8" + inj[:-1]),
        ("ps-injection", b"fatal: x\xe2\x80\xa9" + inj[:-1]),
        ("tab-injection", b"fatal: x\t" + inj[:-1]),
        ("vt-ff-fs-gs-rs", b"a\x0b\x0c\x1c\x1d\x1e" + inj[:-1]),
        ("esc-sequence", b"\x1b[2J\x1b[31mRED\x1b[0m"),
        ("bidi-rlo-report-only", b"fatal: \xe2\x80\xae" + b"tuoheresed"),
        ("u10ffff-noncharacter", b"fatal: \xf4\x8f\xbf\xbf"),
        ("len200-ascii", b"A" * 200),
        ("len201-ascii", b"A" * 201),
        ("len202-ascii", b"A" * 202),
        ("len203-ascii", b"A" * 203),
    ]
    for label, pl in small:
        run(kit, pl, label)
    # boundary injections: an injected line placed so that the head or tail cut lands inside / next to it
    for n in (201, 202, 203, 204, 260):
        for off in range(92, 108, 1):
            for sep in (b"\n", b"\xc2\x85", b"\xe2\x80\xa8", b"\r"):
                body = b"x" * off + sep + b"MISMATCH\tK4\t.\tforged\tinjected"
                pl = (body + b"y" * max(0, n - len(body)))[:n]
                rows, cell = run_quiet(kit, pl)
                if rows is None or len(rows) != 1 or any(s in (cell or "") for s in SEP):
                    print(f"BOUNDARY-FAIL n={n} off={off} sep={sep!r} rows={0 if rows is None else len(rows)}")
                    run(kit, pl, f"boundary-fail n={n} off={off}")
    print("BOUNDARY-SWEEP-DONE")
    # tail-cut straddle with a well-formed separator just before the tail window (len-99)
    for n in (300, 301, 302, 303):
        for k in range(0, 6):
            tail_start = n - 99
            sep = [b"\n", b"\xc2\x85", b"\xe2\x80\xa8", b"\xf0\x9f\x98\x80", b"\xf0\x80"][k % 5]
            body = b"z" * (tail_start - len(sep) - 4 + k) + sep + inj[:-1]
            pl = (body + b"q" * n)[:n]
            rows, cell = run_quiet(kit, pl)
            if rows is None or len(rows) != 1 or any(s in (cell or "") for s in SEP):
                print(f"TAIL-FAIL n={n} k={k} rows={0 if rows is None else len(rows)}")
    print("TAIL-SWEEP-DONE")
    # 10 MB payloads through the public path
    MB = 1_000_000
    big = [
        ("10MB-injection-repeated", inj * (10 * MB // len(inj))),
        ("10MB-F4-8F-BF-BF", b"\xf4\x8f\xbf\xbf" * (10 * MB // 4)),
        ("10MB-NEL-char", b"\xc2\x85" * (10 * MB // 2)),
        ("10MB-NUL", b"\x00" * (10 * MB)),
        ("10MB-continuation-80", b"\x80" * (10 * MB)),
    ]
    for label, pl in big:
        run(kit, pl, label)
    shutil.rmtree(KIT, ignore_errors=True)
    print("KIT-REMOVED")


def run_quiet(kit, pl):
    toolcopy, repo, rev = kit
    with open(PAY, "wb") as f:
        f.write(pl)
    env = dict(ENV)
    env["S_PAYLOAD"] = PAY
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out = p.stdout.decode("utf-8", "backslashreplace")
    rows = [l for l in out.split("\n") if l.startswith("MISMATCH\tK4\t")]
    if len(rows) != 1 or len(rows[0].split("\t")) != 5:
        return rows, None
    return rows, rows[0].split("\t", 4)[4]


if __name__ == "__main__":
    main()
