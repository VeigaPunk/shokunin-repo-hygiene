#!/usr/bin/env python3
"""S80MutTool probe: does a PROPOSED c2 population row (q13: fork-bomb at the file-digest hang point)
distinguish the pristine W2 tool from a mutant that lost q_kill_session's STOP pass (M01) or its
repeat passes (M02)?  Reuses the frozen counter's row machinery unchanged; only the sha256sum shim differs:
it marks, then starts a continuous forker in the worker session, then blocks.
Not a counter run: one row per tool, printed for the record."""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
spec = importlib.util.spec_from_file_location(
    "c2c", os.path.join(LANE, "census", "round-80", "c2-signal-counter.py"))
c2c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2c)

FORKBOMB = r'''last=; for last in "$@"; do :; done
if [[ ${SOUJI_R80_POINT:-} == file-digest && $last == "$SOUJI_R80_TARGET" ]]; then
  r80_mark sha256sum "$@"
  ( while :; do sleep 600 & done ) &
  exec sleep 600
fi
exec ''' + c2c.which("sha256sum") + r''' "$@"
'''


def probe(tool, label, work):
    rowdir = os.path.join(work, "row-" + label)
    os.makedirs(rowdir)
    shimdir = os.path.join(rowdir, "shim")
    stubs = c2c.make_shims(shimdir)
    with open(os.path.join(shimdir, "sha256sum"), "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n" + c2c.MARK_FN + FORKBOMB)
    os.chmod(os.path.join(shimdir, "sha256sum"), 0o755)
    r = c2c.run_row(tool, os.path.join(os.path.dirname(tool), "souji-verify.sh"), stubs, rowdir,
                    "q13-term-file-digest-forkbomb", "TERM", "file-digest", "file", "safe",
                    "SIGNALED", shimdir)
    ok, exited, rc, sigline, verdict, ns, nl, secs, ign, where, text = r
    print(f"PROBE {label} tool_sha={c2c.sha(tool)} ok={ok} exited={exited} rc={rc} "
          f"signal_line={'y' if sigline else 'n'} survivors={ns} tmpleft={nl} secs={secs:.1f} "
          f"at={where} expect=SIGNALED/143")
    return ok


def main():
    work = os.path.abspath(sys.argv[1])
    S = "/fast/scratch/hyaku/souji-r80/S80MutTool"
    probes = [("pristine", os.path.join(S, "base", "souji-quarantine.sh")),
              ("M01", os.path.join(S, "mut", "M01-no-sigstop-pass", "souji-quarantine.sh")),
              ("M02", os.path.join(S, "mut", "M02-single-kill-pass", "souji-quarantine.sh"))]
    os.makedirs(work, exist_ok=True)
    res = {}
    for label, tool in probes:
        res[label] = probe(tool, label, work)
    print("PROBE-SUMMARY " + " ".join(f"{k}={'killed' if not v else 'survived'}" for k, v in res.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
