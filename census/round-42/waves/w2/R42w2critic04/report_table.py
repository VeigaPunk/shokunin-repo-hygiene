#!/usr/bin/env python3
"""R42w2critic04: join matrix.json (mutant x fixture kill runs) with probes-results.json (differential
scenarios) into table.tsv and print the counts. Classifications below are the seat's reasoning; each is
backed by the cited scenario (probes-results.json) or by the matrix (fixture kill)."""
import json
import os
import sys

SEAT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SEAT)
from mutants import MUTANTS  # noqa: E402

LANDED = "r42-drift-conditions.py"
EQUIV = {
    "S18": "return value of parse_record's TOTAL is never read by run()",
    "S19": "1-byte reads concatenate to the same bytes (big-3000 identical)",
    "S28": "discovery order is erased: drift is sorted before printing",
    "S29": "root-name position is erased by the same sort",
    "S30": "a .git entry implies a directory, so the isdir guard is redundant",
    "S39": "git 2.56 rev-parse --absolute-git-dir already returns the resolved gitdir (gitdir-symlink identical)",
    "S41": "porcelain worktree lines are the only lines beginning 'worktree'",
    "S51": "inode check in the alias test still fires for a symlinked record (json-is-record-symlink identical)",
    "S65": "json.dump defaults to ensure_ascii, so the output is ASCII under either encoding",
    "S66": "a 1-byte truncate is followed by a write that sets the length (json-overwrite-long identical)",
    "S67": "bytes only: the trailing newline; parsed JSON identical (json-bytes-only)",
    "S68": "bytes only: indentation; parsed JSON identical (json-bytes-only)",
    "S69": "json_target is always absolute (realpath of abspath)",
    "S74": "stderr text only: the trailing newline of the REFUSAL line (stderr-text-only; class token kept)",
    "S75": "whitelisted child env has no HOME/XDG, so no global config can be read either way",
    "S76": "--no-optional-locks is also passed, so the env variable is redundant",
    "S77": "worktree list/prune consult no attributes; no /etc/gitattributes on this host",
}
NONEQ = {
    "S03": ("big-3000", "record cut at 64 KiB: rc 1->2 (partial row refused)"),
    "S11": ("total-junk", "TOTAL with 'prunable=0x' accepted: rc 2->0"),
    "S12": ("space-name", "REPO name with a space refused: rc 0->2"),
    "S13": ("empty-regs", "'regs=' empty field: rc 2->1 (uncaught ValueError traceback)"),
    "S17": ("total-prunable-small", "TOTAL prunable smaller than the row sum accepted: rc 2->1"),
    "S22": ("root-not-repo-named", "root named by its basename, not a repo: ABSENT becomes UNREACHABLE"),
    "S25": ("root-unreadable", "unreadable root: DRIFT ABSENT becomes a traceback (stdout lost)"),
    "S33": ("root-symlink", "symlinked --root refuses every row: rc 0->2 RECORD-OUTSIDE-ROOT"),
    "S34": ("rel-root-named", "--root . names the root repo '.', not its basename: rc 0->1 ABSENT"),
    "S35": ("timeout-fifo-head", "--timeout ignored by the gitdir probe: fast (<10 s) becomes slow (~20 s)"),
    "S42": ("NONE (race-only)", "prune-timeout re-raise needs prune to block where list does not; none found"),
    "S43": ("regs-up", "record 1, live 2: REGS-CHANGED dropped, rc 1->0"),
    "S44": ("prunable-down", "record prunable 1, live 0: PRUNABLE-CHANGED dropped, rc 1->0"),
    "S53": ("json-sibling-prefix", "--json in sibling rootX counted inside root: rc 0->2"),
    "S58": ("json-mode", "--json file mode 0600 instead of 0644 (mode differs)"),
    "S63": ("json-empty", "--json '' treated as a path (cwd): rc 0->2 JSON-NOT-REGULAR"),
    "S73": ("timeout-float", "--timeout 1.5 accepted: argparse rc 2 -> 0"),
}


def main():
    matrix = json.load(open(os.path.join(SEAT, "matrix.json"), encoding="utf-8"))
    probes = json.load(open(os.path.join(SEAT, "probes-results.json"), encoding="utf-8"))
    by = {}
    for r in matrix:
        by.setdefault(r["mutant"], {})[r["fixture"]] = r
    diffs = probes["diffs"]
    rows = ["mutant\tchange\tkilled_by\tequivalent\tprobe"]
    counts = {"landed": 0, "landed_only": 0, "prior_only": 0, "none": 0, "equiv": 0, "nonequiv": 0,
              "nonequiv_no_det_probe": 0}
    for mid, desc, _o, _n in MUTANTS:
        row = by[mid]
        land = row[LANDED]["killed"]
        prior = [f[:-3] for f in row if f != LANDED and row[f]["killed"]]
        if land:
            counts["landed"] += 1
            if not prior:
                counts["landed_only"] += 1
        elif prior:
            counts["prior_only"] += 1
        killed_by = []
        if land:
            killed_by.append("landed:" + ",".join(
                f.replace("case-", "") for f in row[LANDED]["fails"]))
        if prior:
            killed_by.append("prior:" + ",".join(prior))
        if not killed_by:
            killed_by.append("none")
            counts["none"] += 1
        if mid in EQUIV:
            eq, probe = "equivalent", "probes: no difference in 46 scenarios" if mid not in (
                "S67", "S68", "S74") else "probes: " + ("bytes only" if mid != "S74" else "stderr text only")
            if mid in ("S75", "S76", "S77"):
                probe = "argument only (env whitelist); no scenario can observe it"
            if mid == "S39":
                probe = "probes: gitdir-symlink identical"
            counts["equiv"] += 1
            reason = EQUIV[mid]
            probe = probe + " | " + reason
        elif mid in NONEQ:
            scen, what = NONEQ[mid]
            if scen.startswith("NONE"):
                eq = "non-equivalent (race only)"
                probe = "none deterministic: " + what
                counts["nonequiv_no_det_probe"] += 1
            else:
                eq = "non-equivalent"
                probe = "probes: %s = %s" % (scen, what)
            counts["nonequiv"] += 1
        else:
            eq = "no (killed)"
            probe = "fixture: " + ("; ".join(killed_by))
        if mid not in EQUIV and mid not in NONEQ and mid in diffs:
            hits = [n for n, _k in diffs[mid]]
            probe = probe + " | probes differ on: " + ",".join(hits[:3])
        rows.append("%s\t%s\t%s\t%s\t%s" % (mid, desc, " ".join(killed_by), eq, probe))
    text = "\n".join(rows) + "\n"
    open(os.path.join(SEAT, "table.tsv"), "w", encoding="utf-8").write(text)
    print(text)
    print("COUNTS mutants=%d killed_by_landed=%d landed_only=%d prior_only=%d survived_all_nine=%d "
          "equivalent=%d non_equivalent=%d (no_deterministic_probe=%d)" % (
              len(MUTANTS), counts["landed"], counts["landed_only"], counts["prior_only"], counts["none"],
              counts["equiv"], counts["nonequiv"], counts["nonequiv_no_det_probe"]))


if __name__ == "__main__":
    main()
