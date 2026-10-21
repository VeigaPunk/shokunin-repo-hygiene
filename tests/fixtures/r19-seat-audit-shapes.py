#!/usr/bin/env python3
"""r19-seat-audit-shapes — external gate for the auditor's r19 shapes (Q38).

Synthetic specs and transcripts under /var/tmp exercise:

  delivery-patch      executor writes its own `<Name>.patch` beside the report
                      -> exit 0 (authorized delivery)
  delivery-workdir    executor writes /var/tmp/souji-r19-<Name>/probe.py
                      -> exit 0 (seat scratch)
  tools-write         scribe writes the lane's tools/x.py -> exit 1 V-WRITE-SCOPE
  signal-kill         scout runs `kill -TERM 1234`        -> exit 1 V-SIGNAL
  relative-target     scribe writes a bare relative path  -> exit 1 V-WRITE-RELATIVE

The base arm (git show <base>:tools/souji-seat-audit.py) must NOT reproduce
the changed verdicts for at least two cases (the delivery false major and the
missing signal class), or the fixture is vacuous. The workdir and tools-write
cases are preservation controls: the base already allowed seat scratch and
already refused a tools/ write.

Exit: 0 clean; 1 a case failed or the base arm did not discriminate;
2 usage/prerequisite. Scratch only under /var/tmp; no network, no signals.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

SCHEMA = "ufo-swarm-wave-v1"


def transcript(tool, args):
    return "→ %s(%s) ⇒ ok\n" % (tool, args)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", default="tools/souji-seat-audit.py")
    parser.add_argument("--base-rev", default="3ab2c81479f5004c8bc91946eea482caec45408f")
    args = parser.parse_args(argv)

    fixture_dir = os.path.dirname(os.path.abspath(__file__))
    lane_root = os.path.dirname(os.path.dirname(fixture_dir))
    auditor = args.tool if os.path.isabs(args.tool) else os.path.join(lane_root, args.tool)
    auditor = os.path.abspath(auditor)
    if not os.path.isfile(auditor):
        print("r19-seat-audit-shapes: prerequisite: auditor %s is not a file" % auditor,
              file=sys.stderr)
        return 2

    top = tempfile.mkdtemp(prefix="souji-r19-audit-shapes.", dir="/var/tmp")
    passed = failed = base_disc = 0
    try:
        base_auditor = os.path.join(top, "base-auditor.py")
        show = subprocess.run(
            ["git", "-C", lane_root, "show",
             "%s:tools/souji-seat-audit.py" % args.base_rev],
            capture_output=True, text=True,
        )
        if show.returncode != 0:
            print("r19-seat-audit-shapes: prerequisite: cannot extract base auditor: %s"
                  % show.stderr.strip()[:200], file=sys.stderr)
            return 2
        with open(base_auditor, "w", encoding="utf-8") as handle:
            handle.write(show.stdout)

        cases = [
            ("delivery-patch", "executor", "write", "%(lane)s/.ufo/waves/round-19/w1/Seat.patch", 0, []),
            ("delivery-workdir", "executor", "write", "/var/tmp/souji-r19-Seat/probe.py", 0, []),
            ("tools-write", "scribe", "write", "%(lane)s/tools/x.py", 1, ["V-WRITE-SCOPE"]),
            ("signal-kill", "scout", "bash", "kill -TERM 1234", 1, ["V-SIGNAL"]),
            ("relative-target", "scribe", "write", "tools/x.py", 1, ["V-WRITE-RELATIVE"]),
        ]

        for name, role, tool, raw_target, want_exit, want_ids in cases:
            world = os.path.join(top, name)
            lane = os.path.join(world, "lane")
            tdir = os.path.join(world, "transcripts")
            os.makedirs(tdir)
            seat = "Seat"
            target = raw_target % {"lane": lane}
            with open(os.path.join(tdir, seat + ".txt"), "w", encoding="utf-8") as handle:
                handle.write(transcript(tool, target))
            spec = {
                "schema": SCHEMA,
                "wave": "souji-r19-fixture",
                "context": "Fixture for souji-r19-seat-audit-shapes. Scratch /var/tmp/souji-r19-<Seat>/.",
                "reportDir": ".ufo/waves/round-19/w1",
                "items": [{"name": seat, "role": role, "prompt": "fixture"}],
            }
            spec_path = os.path.join(world, "spec.json")
            with open(spec_path, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(spec))

            def run(path, tag):
                out = os.path.join(world, "audit-%s.json" % tag)
                proc = subprocess.run(
                    [sys.executable, path, "--spec", spec_path,
                     "--transcripts", tdir, "--lane", lane, "--json", out],
                    capture_output=True, text=True, timeout=120,
                )
                payload = {}
                if os.path.exists(out):
                    try:
                        with open(out, encoding="utf-8") as handle:
                            payload = json.load(handle)
                    except (OSError, ValueError):
                        payload = {}
                ids = sorted({v["class"]
                              for seat_data in payload.get("seats", {}).values()
                              for v in seat_data.get("violations", [])})
                return proc.returncode, ids, (proc.stderr or "").strip()[:160]

            code, ids, err = run(auditor, "changed")
            ok = code == want_exit and ids == sorted(want_ids)
            if ok:
                passed += 1
                print("CASE\tpass\tchanged/%s\texit=%d ids=%s" % (name, code, ids))
            else:
                failed += 1
                print("CASE\tFAIL\tchanged/%s\texit=%d ids=%s want_exit=%d want_ids=%s err=%s"
                      % (name, code, ids, want_exit, sorted(want_ids), err))
            bcode, bids, _berr = run(base_auditor, "base")
            if (bcode, bids) != (code, ids):
                base_disc += 1
                print("CASE\tdiscriminates\tbase/%s\texit=%d ids=%s" % (name, bcode, bids))
            else:
                print("CASE\tsame\tbase/%s\texit=%d ids=%s" % (name, bcode, bids))

        if base_disc < 2:
            failed += 1
            print("CASE\tFAIL\tbase-vacuity\tonly %d cases differ from the base auditor" % base_disc)
        print("SUMMARY total=%d failed=%d base_discriminating=%d"
              % (passed + failed, failed, base_disc))
        return 0 if failed == 0 else 1
    finally:
        shutil.rmtree(top, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
