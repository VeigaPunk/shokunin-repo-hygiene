#!/usr/bin/env python3
# R41w2sentinel01 second driver: worktree-root .mailmap cases (git opens <root>/.mailmap on every run).
# Reuses the helpers of attack_freeze_check.py (same pinned tool, same strace analysis). Scratch only.
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attack_freeze_check as A  # noqa: E402


def main():
    A.setup()
    os.makedirs(f"{A.SEATDIR}/receipts", exist_ok=True)
    recs = []
    # clean fixture, then a FIFO named .mailmap in the work tree (never committed)
    F1 = A.build("wt-fifo-mailmap", A.base_files(), freeze=A.clean_freeze(), gitlinks=A.GITLINKS)
    A.put(F1["D"], ".mailmap", "FIFO")
    recs.append(A.run("wt-fifo-mailmap", F1["D"], ["--prereg", A.PRE], F1["F"], timeout=30))
    # clean fixture, regular hostile .mailmap in the work tree (never committed)
    F2 = A.build("wt-mailmap-content", A.base_files(), freeze=A.clean_freeze(), gitlinks=A.GITLINKS)
    A.put(F2["D"], ".mailmap", b"Mallory <m@example.invalid> <r41@example.invalid>\n")
    recs.append(A.run("wt-mailmap-content", F2["D"], ["--prereg", A.PRE], F2["F"], timeout=60))
    # same fixture, a committed freeze-time digest mismatch: does a worktree .mailmap change the verdict?
    F3 = A.build("wt-mailmap-bad-digest", A.base_files(),
                 freeze={A.PRE: lambda c: A.doc(A.claim(c, counter="census/c1.py sha256=" + "0" * 64))},
                 gitlinks=A.GITLINKS)
    A.put(F3["D"], ".mailmap", b"Mallory <m@example.invalid> <r41@example.invalid>\n")
    recs.append(A.run("wt-mailmap-content-bad-digest", F3["D"], ["--prereg", A.PRE], F3["F"], timeout=60))
    with open(f"{A.SEATDIR}/receipts/runs-mailmap.json", "w") as f:
        json.dump({"runs": recs}, f, indent=1, sort_keys=True)
    for r in recs:
        print(f"{r['tag']:<36} rc={r['rc']} to={r['timed_out']} secs={r['secs']} wt={r.get('worktree_opens')} "
              f"writes={r.get('writes')} execs={r.get('execs_ok')} | {r['stdout'].strip()[:160]} | "
              f"{r['stderr'].strip()[-120:]}")


if __name__ == "__main__":
    main()
