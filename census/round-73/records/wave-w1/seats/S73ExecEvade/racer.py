#!/usr/bin/env python3
"""S73ExecEvade route (d): detached racer spawned by the wrapped command.

Waits until the stage-W receipt writer has created its temp receipt file (the writer creates
`<out>.<rand>.tmp` only after every pre/post check has passed), then atomically replaces a tracked
worktree file with a prepared forged file, and records whether the receipt OUT already existed at
that instant (it must not: `out_before` False proves the forge landed before publication).

argv: repo rel prepared outdir outbase log
"""
import glob
import json
import os
import sys
import time


def main() -> int:
    repo, rel, prepared, outdir, outbase, logpath = sys.argv[1:7]
    target = os.path.join(repo, rel)
    out = os.path.join(outdir, outbase)
    pattern = os.path.join(glob.escape(outdir), glob.escape(outbase) + ".*.tmp")
    log = {"ok": False, "reason": "no-tmp", "target": rel}
    deadline = time.monotonic() + 120.0
    tmp = None
    while time.monotonic() < deadline:
        hits = glob.glob(pattern)
        if hits:
            tmp = hits[0]
            break
        time.sleep(0.00005)
    if tmp is None:
        json.dump(log, open(logpath, "w"))
        return 3
    log["tmp"] = os.path.basename(tmp)
    log["hit_ns"] = time.time_ns()
    log["out_before"] = os.path.exists(out)
    try:
        os.replace(prepared, target)
        log["ok"] = True
    except OSError as exc:
        log["reason"] = f"replace-failed: {exc}"
    log["done_ns"] = time.time_ns()
    log["out_after"] = os.path.exists(out)
    json.dump(log, open(logpath, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
