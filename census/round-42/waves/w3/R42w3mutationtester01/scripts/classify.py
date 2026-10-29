#!/usr/bin/env python3
"""Build the classified mutant table for R42w3mutationtester01 from results.tsv.

Reads (all inside the seat directory):
  results.tsv                 per-mutant counter case table, --selftest, the other legs
  mutants/manifest.tsv        per-mutant line, kind, old, new
  logs/survivor-classification.tsv   this seat's W-mutant survivor verdicts
                                    (id, class, evidence, reason; tab separated)
  logs/inherited-survivor-classification.tsv
                                    the inherited w2 seat's M-mutant survivor
                                    verdicts, transcribed from
                                    census/round-42/waves/w2/R42w2mutationtester01/scripts/classify.py
                                    (its EVID map) and re-verified by this seat.

Writes:
  table.md                 the table
  counter-summaries.txt    every counter SUMMARY line verbatim, one per mutant

The verdict of a SURVIVOR is decided by probe evidence:
  EQUIVALENT  behaviour-equivalent on every branch probed
  GAP         an observable behaviour change that no counter leg and no
              --selftest case observes
  GAP-LANE    an observable change caught only by the counter's `real` leg (the
              lane's own preregistration), not by the 37-case table
"""
import csv
import os
import sys

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_tsv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def load_class(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            out[parts[0]] = (parts[1].strip(), parts[2].strip(), "\t".join(parts[3:]).strip())
    return out


def esc(s):
    return s.replace("|", "\\|").replace("\n", "\\n")


def main():
    results = load_tsv(os.path.join(SEAT, "results.tsv"))
    manifest = {r["id"]: r for r in load_tsv(os.path.join(SEAT, "mutants", "manifest.tsv"))}
    ev = {}
    ev.update(load_class(os.path.join(SEAT, "logs", "inherited-survivor-classification.tsv")))
    ev.update(load_class(os.path.join(SEAT, "logs", "survivor-classification.tsv")))
    lines = []
    counts = {"EQUIVALENT": 0, "GAP": 0, "GAP-LANE": 0}
    n_kc = n_ks = n_surv = 0
    unclassified = []
    for r in results:
        mid = r["id"]
        m = manifest.get(mid, {})
        if r["verdict"] == "killed by counter cases":
            n_kc += 1
            verdict = "killed by counter cases"
            why = "counter case(s) fail: %s" % (r["failed_cases"] or "(none listed)")
        elif r["verdict"] == "killed only by --selftest":
            n_ks += 1
            verdict = "killed only by --selftest"
            why = ("the 37-case table passes (pass=%s fail=%s); the mutant's own --selftest "
                   "fails: %s" % (r["counter_cases_pass"], r["counter_cases_fail"], r["selftest_line"]))
        else:
            n_surv += 1
            e = ev.get(mid)
            if e is None:
                verdict = "SURVIVES both: UNCLASSIFIED"
                why = "no probe evidence recorded"
                unclassified.append(mid)
            else:
                counts[e[0]] = counts.get(e[0], 0) + 1
                verdict = {"EQUIVALENT": "survives both: EQUIVALENT",
                           "GAP": "survives both: GAP (coverage limit)",
                           "GAP-LANE": "survives both: GAP (caught only by the counter's real leg)"}[e[0]]
                why = "%s (evidence: %s)" % (e[2], e[1])
        lines.append("| %s | L%s %s | `%s` -> `%s` | %s/%s | %s | %s | %s |" % (
            mid, m.get("line", "?"), m.get("kind", "?"), esc(m.get("old", "")), esc(m.get("new", "")),
            r["counter_cases_pass"], r["counter_cases_fail"], r["selftest_line"].replace("SELFTEST ", ""),
            verdict, esc(why)))
    header = ("| mutant | line / kind | change (old -> new) | counter cases pass/fail | --selftest | "
              "verdict | evidence / reason |\n|---|---|---|---|---|---|---|---|")
    out = os.path.join(SEAT, "table.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# R42w3mutationtester01 — mutant table (tools/souji-freeze-check.py, part A)\n\n")
        fh.write("Counter cases pass/fail are the frozen counter's own 37-case table "
                 "(`SUMMARY cases=37 pass=N fail=M`), read from a scoring run over the lane tip "
                 "plus the mutant. `--selftest` is the mutant's own `SELFTEST cases=31 pass=P fail=F`.\n\n")
        fh.write(header + "\n" + "\n".join(lines) + "\n")
    with open(os.path.join(SEAT, "counter-summaries.txt"), "w", encoding="utf-8") as fh:
        for r in results:
            fh.write("%s\t%s\n" % (r["id"], r["counter_summary"]))
    print("total=%d killed_by_counter_cases=%d killed_only_selftest=%d survivors=%d"
          % (len(results), n_kc, n_ks, n_surv))
    print("survivor split: equivalent=%d gap=%d gap_lane_only=%d"
          % (counts.get("EQUIVALENT", 0), counts.get("GAP", 0), counts.get("GAP-LANE", 0)))
    if unclassified:
        print("UNCLASSIFIED survivors: %s" % " ".join(unclassified))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
