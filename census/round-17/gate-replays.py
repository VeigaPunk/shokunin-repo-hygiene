#!/usr/bin/env python3
"""round-17 D6 counting command: freeze the landing-gate replays.

The round-16 replay verdicts exist only as prose and seat transcripts
(`.ufo/waves/round-16/w2/RerunGateReplayR{13,14,15}.md`,
`corpus/lessons/round-16.md`, `corpus/lessons/round-16-verifier-spotcheck.md`).
This runner extracts `tools/souji-landing-gate.py` from a named revision
(`--gate-rev`, default `WORKTREE`) and replays it with `--json` on the
pinned revisions:

  b410186 round 15  (r15 landing: gate training instance)
  a31642d round 13  (admitted r13 landing: no-false-positive control)
  cc21683 round 14  (r14 landing: no-false-positive control)
  6ff91f5 round 16  (r16 landing after the wave-2 carry landed)
  79bbe7a round 16  (r16 pre-carry: wave-2 STATUS lines flagged uncarried)

No replay passes `--base`: the original runs did not, so `LG-PARSE-CHANGED`
is out of scope and `checked_reg` counts only registry-cited scripts.

Default mode compares each replay's exit code and exact (id, path) finding
multiset against `gate-replays-expected.json` and writes an output record
(`--output`, refuses overwrite). Divergence against expected is reported,
never repaired: the expected file is frozen evidence, not a fit target.

`--write-expected PATH` derives the expected file instead of comparing:
runs the same pinned replays under `--gate-rev` and writes the observed
verdicts (refuses overwrite; delete the file deliberately to re-derive).
The committed `gate-replays-expected.json` was derived under
`--gate-rev 5fa6017`, the r16 base, because the worktree gate is edited by
another seat while this runner lands.

`--selftest` additionally runs the extracted gate's own `--selftest` and
records its `SELFTEST\tpass=N\tfail=M` tail in the output record.

Every git read is `git -C LANE show|rev-parse`; nothing writes the lane.
Scratch (extracted gate, per-replay `--json` files) lives under
`--scratch` (default `/var/tmp`); the gate's own `bash -n` snapshot and
selftest repos also use `/var/tmp` internally (hardcoded
`tempfile.mkdtemp(dir='/var/tmp')` in the gate).

Usage:
  python3 census/round-17/gate-replays.py --gate-rev 5fa6017 --output out.json
  python3 census/round-17/gate-replays.py --gate-rev 5fa6017 \\
      --write-expected census/round-17/gate-replays-expected.json

Exit: 0 all replays match expected (or derivation written); 1 comparison
divergence; 2 usage/IO error (bad rev, gate missing, output exists, missing
expected file).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

LANE = Path(__file__).resolve().parents[2]
GATE_PATH = "tools/souji-landing-gate.py"
EXPECTED_DEFAULT = Path(__file__).resolve().with_name("gate-replays-expected.json")
RECORD_SCHEMA = 1

# Pinned replays, in the order the r16 closure's D6 row cites them. Each is
# (name, rev, round). Prose expectations recorded for cross-reference only —
# the expected JSON is authoritative and derived by observation.
REPLAYS = (
    ("r15-landing", "b410186", 15),
    ("r13-admitted", "a31642d", 13),
    ("r14-landing", "cc21683", 14),
    ("r16-landing", "6ff91f5", 16),
    ("r16-precarry", "79bbe7a", 16),
)

# What the r16 prose claimed (round-16-verifier-spotcheck.md:61-66, D6 row).
# Kept as documentation; never compared — observed truth wins.
PROSE_CLAIMS = {
    "r15-landing": "exit 1, 5 findings: LG-PARSE-REG, LG-FROZEN-PIN, "
                   "2x LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED",
    "r13-admitted": "exit 0, 0 findings",
    "r14-landing": "exit 0, 0 findings",
    "r16-landing": "exit 0, 0 findings (gate-landing.json resolved_rev 6ff91f5)",
    "r16-precarry": "exit 1, 29 LG-SEAT-UNCARRIED (LOG.md:902 prose says 28; "
                    "closure re-derived 30 markers / 29 uncarried)",
}

SELFTEST_RE = re.compile(r"^SELFTEST\tpass=(\d+)\tfail=(\d+)", re.MULTILINE)


def die(msg: str) -> "SystemExit":
    print("gate-replays: %s" % msg, file=sys.stderr)
    return SystemExit(2)


def git(*args: str, binary: bool = False):
    proc = subprocess.run(
        ["git", "-C", str(LANE), *args], capture_output=True
    )
    if proc.returncode != 0:
        raise die(
            "git %s failed rc=%d: %s"
            % (args[0], proc.returncode, proc.stderr.decode("utf-8", "replace")[:300])
        )
    return proc.stdout if binary else proc.stdout.decode("utf-8", "replace")


def extract_gate(gate_rev: str, scratch: Path) -> tuple[Path, str, str | None]:
    """Return (gate_file, sha256, resolved_rev). WORKTREE reads worktree
    bytes; anything else reads `<rev>:tools/souji-landing-gate.py`."""
    if gate_rev == "WORKTREE":
        data = (LANE / GATE_PATH).read_bytes()
        resolved = None
    else:
        resolved = git("rev-parse", "--verify", "%s^{commit}" % gate_rev).strip()
        data = git("show", "%s:%s" % (resolved, GATE_PATH), binary=True)
    digest = hashlib.sha256(data).hexdigest()
    gate_file = scratch / "souji-landing-gate.py"
    gate_file.write_bytes(data)
    return gate_file, digest, resolved


def run_replay(gate_file: Path, scratch: Path, rev: str, round_no: int) -> dict:
    """Run the extracted gate on one replay; return its --json payload plus
    process facts."""
    json_out = scratch / ("replay-%s-%s.json" % (rev[:12], round_no))
    cmd = [
        sys.executable,
        str(gate_file),
        "--root", str(LANE),
        "--rev", rev,
        "--round", str(round_no),
        "--json", str(json_out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    payload = None
    if json_out.exists():
        payload = json.loads(json_out.read_text(encoding="utf-8"))
        json_out.unlink()
    return {
        "process_rc": proc.returncode,
        "stdout": proc.stdout.splitlines(),
        "stderr_tail": proc.stderr.strip().splitlines()[-3:],
        "payload": payload,
    }


def run_gate_selftest(gate_file: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(gate_file), "--selftest"],
        capture_output=True, text=True, errors="replace",
    )
    m = SELFTEST_RE.search(proc.stdout)
    return {
        "process_rc": proc.returncode,
        "pass": int(m.group(1)) if m else None,
        "fail": int(m.group(2)) if m else None,
    }


def multiset(findings: list[dict]) -> list[list[str]]:
    """Sorted (id, path) multiset from a findings list."""
    return sorted([f["id"], f["path"]] for f in findings)


def compare(observed: dict, expected: dict) -> dict:
    """Compare one observed replay against its expected entry. Returns
    {match, divergences}."""
    divergences = []
    obs_exit = observed["payload"]["exit"] if observed["payload"] else None
    if observed["process_rc"] != expected["exit"] or obs_exit != expected["exit"]:
        divergences.append(
            "exit: observed process_rc=%s payload_exit=%s, expected %s"
            % (observed["process_rc"], obs_exit, expected["exit"])
        )
    obs_pairs = (
        multiset(observed["payload"]["findings"]) if observed["payload"] else []
    )
    obs_counter = Counter(tuple(p) for p in obs_pairs)
    exp_counter = Counter(tuple(p) for p in expected["findings"])
    if obs_counter != exp_counter:
        for pair in sorted(exp_counter - obs_counter):
            divergences.append("missing: %s x%d" % (list(pair), (exp_counter - obs_counter)[pair]))
        for pair in sorted(obs_counter - exp_counter):
            divergences.append("extra: %s x%d" % (list(pair), (obs_counter - exp_counter)[pair]))
    return {"match": not divergences, "divergences": divergences}


def write_json(path: Path, payload: dict) -> None:
    if path.exists():
        raise die("refusing to overwrite %s" % path)
    with open(path, "x", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="gate-replays.py",
        description="Round-17 D6: pinned landing-gate replay runner.",
    )
    ap.add_argument("--gate-rev", default="WORKTREE",
                    help="revision supplying tools/souji-landing-gate.py "
                         "(default WORKTREE)")
    ap.add_argument("--output", help="write the run record here (refuses overwrite)")
    ap.add_argument("--expected", default=str(EXPECTED_DEFAULT),
                    help="expected verdicts JSON (default: sibling "
                         "gate-replays-expected.json)")
    ap.add_argument("--write-expected", metavar="PATH",
                    help="derive expected verdicts instead of comparing; "
                         "writes PATH (refuses overwrite) and exits")
    ap.add_argument("--selftest", action="store_true",
                    help="also run the extracted gate's --selftest and record it")
    ap.add_argument("--scratch", default="/var/tmp",
                    help="scratch parent for extracted gate and --json files")
    args = ap.parse_args(argv)

    lane_head = git("rev-parse", "HEAD").strip()
    scratch = Path(tempfile.mkdtemp(prefix="souji-gate-replays-", dir=args.scratch))
    try:
        gate_file, gate_sha, gate_resolved = extract_gate(args.gate_rev, scratch)

        gate_record = {
            "gate_rev_arg": args.gate_rev,
            "resolved_rev": gate_resolved,
            "sha256": gate_sha,
            "path_in_repo": GATE_PATH,
        }

        record = {
            "record_schema": RECORD_SCHEMA,
            "lane_head": lane_head,
            "gate": gate_record,
            "replays": {},
            "selftest": None,
            "match": None,
        }

        for name, rev, round_no in REPLAYS:
            obs = run_replay(gate_file, scratch, rev, round_no)
            payload = obs["payload"] or {}
            entry = {
                "rev": rev,
                "round": round_no,
                "resolved_rev": payload.get("resolved_rev"),
                "process_rc": obs["process_rc"],
                "exit": payload.get("exit"),
                "error": payload.get("error"),
                "findings": multiset(payload.get("findings", [])),
                "finding_count": len(payload.get("findings", [])),
                "summary": payload.get("summary"),
                "stdout": obs["stdout"],
                "stderr_tail": obs["stderr_tail"],
            }
            record["replays"][name] = entry

        if args.selftest:
            record["selftest"] = run_gate_selftest(gate_file)

        if args.write_expected:
            expected_path = Path(args.write_expected)
            expected = {
                "expected_schema": 1,
                "note": "Derived by gate-replays.py --write-expected under "
                        "--gate-rev %s. Prose cross-reference: %s"
                        % (args.gate_rev, PROSE_CLAIMS),
                "gate": gate_record,
                "replays": {
                    name: {
                        "rev": record["replays"][name]["rev"],
                        "round": record["replays"][name]["round"],
                        "resolved_rev": record["replays"][name]["resolved_rev"],
                        "exit": record["replays"][name]["exit"],
                        "findings": record["replays"][name]["findings"],
                    }
                    for name, _, _ in REPLAYS
                },
            }
            write_json(expected_path, expected)
            print("gate-replays: wrote expected verdicts to %s" % expected_path)
            return 0

        expected_path = Path(args.expected)
        if not expected_path.exists():
            raise die("expected file %s does not exist; derive it with "
                      "--write-expected" % expected_path)
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        exp_gate_sha = expected.get("gate", {}).get("sha256")
        record["expected"] = {
            "path": str(expected_path),
            "gate_sha256": exp_gate_sha,
            "gate_sha256_match": exp_gate_sha == gate_sha,
        }

        all_match = True
        for name, _, _ in REPLAYS:
            exp_entry = expected["replays"].get(name)
            if exp_entry is None:
                record["replays"][name]["match"] = False
                record["replays"][name]["divergences"] = [
                    "no expected entry for %s" % name]
                all_match = False
                continue
            cmp_result = compare(
                {"process_rc": record["replays"][name]["process_rc"],
                 "payload": {"exit": record["replays"][name]["exit"],
                             "findings": [
                                 {"id": p[0], "path": p[1]}
                                 for p in record["replays"][name]["findings"]]}},
                exp_entry,
            )
            record["replays"][name]["match"] = cmp_result["match"]
            record["replays"][name]["divergences"] = cmp_result["divergences"]
            if not cmp_result["match"]:
                all_match = False
        record["match"] = all_match

        # Console table.
        print("name\trev\tround\texit\tfindings\tmatch")
        for name, rev, round_no in REPLAYS:
            e = record["replays"][name]
            print("%s\t%s\t%d\t%s\t%d\t%s" % (
                name, e["rev"], e["round"], e["exit"], e["finding_count"],
                e["match"]))
        print("gate\trev=%s\tsha256=%s\texpected_sha_match=%s" % (
            args.gate_rev, gate_sha[:16], record["expected"]["gate_sha256_match"]))

        if args.output:
            write_json(Path(args.output), record)
            print("gate-replays: wrote record to %s" % args.output)
        return 0 if all_match else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
