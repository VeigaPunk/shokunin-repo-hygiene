#!/usr/bin/env python3
"""S88Sentinel probes, part 5: the escape set of the FLAGFAIL detail (C1 controls other than NEL), and the
order-sensitivity of the LD1 duplicate-id refusal.

Part A (escape set): the delegated stderr carries a single character from the C1 block (U+0080..U+009F) encoded
as UTF-8, and separately U+2028/U+2029, and separately the splitlines boundaries that are NOT in the escaped set.
For each we report whether the tool's stdout carries that byte RAW.

Part B (LD1 order): the counter's `_ledger` keeps the FIRST row for an id and refuses a later duplicate. We build
(a) the frozen r77 ledger + an appended duplicate (the harness's LD1 shape), (b) a ledger whose FIRST P01 row is a
forged resolving row followed by the frozen ledger (the reverse order), and (c) a ledger with the frozen rows and a
forged duplicate whose class resolves the item. We report the item's verdict, the LEDGER-REFUSED marker and the exit
code for each.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
POP = "census/round-77/c2-population.tsv"
LEDGER = "census/round-77/c2-pointer-ledger.tsv"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_AUTHOR_NAME": "s88 sentinel", "GIT_AUTHOR_EMAIL": "s88@s88.invalid",
            "GIT_COMMITTER_NAME": "s88 sentinel", "GIT_COMMITTER_EMAIL": "s88@s88.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

CHARS = [0x80, 0x81, 0x84, 0x86, 0x8D, 0x90, 0x9B, 0x9F, 0x85, 0x2028, 0x2029,
         0x0B, 0x0C, 0x1C, 0x1D, 0x1E, 0x7F]

STUB = r'''
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    cp = os.environ.get("R88_CP")
    return P(1, b"", chr(int(cp, 16)).encode("utf-8"))


def _truth_refusal(root):
    return ""


def _flag_refusal(*args):
    return None
'''


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_kit(root, toolpath):
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(toolpath, copy)
    with open(os.path.join(tools, "souji-receipt-write.py"), "w", encoding="utf-8") as f:
        f.write(STUB)
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    top = git(repo, "rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(repo):
        raise RuntimeError("fixture toplevel mismatch")
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("seed\n")
    git(repo, "add", "--", "a.txt")
    git(repo, "commit", "-q", "--no-verify", "-m", "s88 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


def part_a(work, toolpath, label):
    print(f"===== PART A escape set, TOOL {label} sha256={sha(toolpath)}")
    for cp in CHARS:
        kit = make_kit(os.path.join(work, f"kitA-{label}-{cp:04x}"), toolpath)
        toolcopy, repo, rev = kit
        env = dict(ENV)
        env["R88_CP"] = f"{cp:04x}"
        p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        raw = p.stdout
        ch = chr(cp).encode("utf-8")
        n = raw.count(ch)
        rows = [l for l in raw.decode("utf-8", "backslashreplace").split("\n") if l.startswith("MISMATCH\tK4\t")]
        cells = len(rows[0].split("\t")) if rows else 0
        detail = rows[0].split("\t")[4] if rows and len(rows[0].split("\t")) > 4 else ""
        splits = "SPLITS" if n and b"\n" not in ch else ""
        print(f"  U+{cp:04X} raw_bytes_in_stdout={n} cells={cells} "
              f"escaped_in_detail={'\\u%04x' % cp in detail or ('\\x%02x' % cp) in detail} detail={detail[:90]!r}")


def run_counter(ledger_path, label):
    p = subprocess.run([sys.executable, "-B", COUNTER, "--root", LANE, "--rev", BASE, "--fleet-root", FLEET,
                        "--population", os.path.join(LANE, POP), "--ledger", ledger_path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, env=ENV)
    out = p.stdout.decode("utf-8", "replace")
    items = [l for l in out.splitlines() if l.startswith("ITEM P01 ")]
    refused = [l for l in out.splitlines() if l.startswith("LEDGER-REFUSED")]
    summary = [l for l in out.splitlines() if l.startswith("SUMMARY")]
    print(f"--- {label} rc={p.returncode}")
    print(f"    {items[0] if items else '<no P01 item>'}")
    print(f"    LEDGER-REFUSED: {refused if refused else '<none>'}")
    print(f"    {summary[0] if summary else '<no summary>'}")


def part_b(work):
    print("===== PART B LD1 order sensitivity")
    base = open(os.path.join(LANE, LEDGER), "rb").read()
    if base and not base.endswith(b"\n"):
        base += b"\n"
    # (a) harness LD1 shape: frozen ledger + appended duplicate P01
    a = os.path.join(work, "led-a.tsv")
    with open(a, "wb") as f:
        f.write(base + b"P01\tABSENT\t-\tr88 LD1 duplicate-id control\n")
    run_counter(a, "A frozen ledger + appended duplicate P01 (the harness's LD1 shape)")
    # (b) reverse order: a forged P01 row FIRST, then the frozen ledger
    b = os.path.join(work, "led-b.tsv")
    with open(b, "wb") as f:
        f.write(b"P01\tTOKEN\t-\tr88 forged FIRST row\n" + base)
    run_counter(b, "B forged resolving P01 row FIRST, frozen rows after")
    # (c) frozen ledger + a duplicate whose class resolves the item
    c = os.path.join(work, "led-c.tsv")
    with open(c, "wb") as f:
        f.write(base + b"P01\tTOKEN\t-\tr88 duplicate with a resolving class\n")
    run_counter(c, "C frozen ledger + duplicate P01 whose class resolves")
    # (d) a duplicate id that is NOT in the population
    d = os.path.join(work, "led-d.tsv")
    with open(d, "wb") as f:
        f.write(base + b"P999\tABSENT\t-\tr88 duplicate for an id outside the population\n")
    run_counter(d, "D frozen ledger + duplicate for an id outside the population")
    # (e) a malformed row (fewer than 3 fields) for a population id
    e = os.path.join(work, "led-e.tsv")
    with open(e, "wb") as f:
        f.write(base + b"P01\tonly-two-fields\n")
    run_counter(e, "E frozen ledger + a malformed P01 row (2 fields)")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("S88-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"S88-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    pinned = os.path.join(work, "pinned-tool.py")
    shutil.copyfile(os.path.join(LANE, "tools/souji-record-agreement.py"), pinned)
    part_a(work, pinned, "current")
    part_b(work)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
