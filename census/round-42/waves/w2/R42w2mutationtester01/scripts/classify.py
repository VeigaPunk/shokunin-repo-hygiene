#!/usr/bin/env python3
"""Build the classified mutant table for R42w2mutationtester01 from the seat's results.tsv.

Reads (all inside the seat directory):
  results.tsv   per-mutant counter case table, --selftest, other legs (written by run.py)
  manifest.tsv  per-mutant line, kind, old, new (written by mutants.py)
Writes:
  table.md          the 64-row table
  counter-summaries.txt  every counter SUMMARY line verbatim, one per mutant
The verdict for a survivor is decided by probe evidence (probe*.py, logs/) recorded below.
"""
import csv
import os

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# survivor -> (class, evidence pointer, one-line reason)
#   EQUIV     behaviour-equivalent on every branch probed (or reasoned, marked)
#   GAP       observable behaviour change that no counter leg and no --selftest observes
#   GAP-LANE  observable change caught only by the counter's `real`/`retro_clean` legs
#             (the lane's own preregistration), not by the 37-case table
EVID = {
    "M02": ("GAP", "logs/probe2.txt", "FULL40 accepts uppercase hex: pristine BASE-UNRESOLVED, mutant clean"),
    "M03": ("GAP", "logs/m03-confirm.txt", "FULL40 without `$`: --rev of 41 hex accepted (pristine refuses rc=2, mutant rc=0)"),
    "M09": ("GAP", "logs/probe1.txt", "KEYLINE keeps trailing blanks: Base 'sha   ' -> BASE-UNRESOLVED"),
    "M13": ("GAP", "logs/probe2.txt", "ROUND loses BOM tolerance: BOM before Round: -> FIELD-MISSING Round (pristine clean)"),
    "M14": ("EQUIV", "logs/probe2.txt", "re.match already anchors at line start; `^` redundant"),
    "M15": ("GAP", "logs/probe2.txt", "EXIT_LINE loses `$`: control 'EXIT=1 (red)' read as red (pristine CONTROL-NOT-RED)"),
    "M18": ("GAP", "logs/probe2.txt", "GIT_NO_REPLACE_OBJECTS dropped: a git replace ref changes the verdict (pristine rc=1, mutant rc=2)"),
    "M19": ("EQUIV", "logs/probe5-equiv.txt", "GIT_CONFIG_SYSTEM=/dev/null still set, so system config stays unread in the mutant env"),
    "M20": ("EQUIV", "logs/probe2.txt", "mailmap affects author/committer fields only; tool reads %H and names"),
    "M21": ("EQUIV", "logs/probe5-equiv.txt", "rev-parse -q X^{commit} prints a full 40-hex name on SHA-1 repos; post-check redundant"),
    "M22": ("GAP", "logs/probe3.txt", "NUL in a path: uncaught ValueError (traceback, no SUMMARY) instead of COUNTER-MISSING"),
    "M24": ("EQUIV", "logs/probe5-equiv.txt", "blob() gates: git cat-file rejects non-normalised paths (rc 128), so is_symlink never sees them"),
    "M28": ("GAP", "logs/probe2.txt", "drop --reverse: freeze = newest add; prereg re-added after counter change: pristine COUNTER-DIGEST, mutant clean"),
    "M29": ("GAP", "logs/probe2.txt", "ids[-1]: freeze = newest add; same scenario as M28"),
    "M30": ("EQUIV", "logs/probe5-equiv.txt", "git log failure yields empty stdout; `ids` non-empty implies rc 0"),
    "M31": ("GAP", "logs/m31-lane-r40.txt", "missing Round line: class FIELD-MISSING becomes FIELD-EMPTY (lane r40 prereg); no case lacks Round"),
    "M39": ("EQUIV", "logs/probe5-equiv.txt", "format lines carry no trailing blanks, so strip() is a no-op on SHA-1 repos"),
    "M40": ("GAP", "logs/probe2.txt", "setdefault keeps newest dispatch add: pristine DISPATCH-BEFORE-FREEZE, mutant clean"),
    "M41": ("EQUIV", "logs/probe4-equivalence.txt", "pattern starts with ^, so re.search == re.match"),
    "M43": ("GAP", "logs/probe1.txt", "fallback takes whole value: 'census/c1.py extra' -> COUNTER-MISSING instead of COUNTER-DIGEST"),
    "M57": ("EQUIV", "logs/probe4-equivalence.txt", "main() sorts all findings; set iteration order unobservable"),
    "M59": ("GAP", "logs/probe3.txt", "duplicated key still evaluated: first-empty Target adds FIELD-EMPTY"),
    "M61": ("GAP-LANE", "logs/probe3.txt", "'## ' heading no longer closes a claim: lane prereg gains 5x KEY-DUPLICATE (counter real=FAIL)"),
    "M62": ("GAP-LANE", "logs/probe3.txt", "non-C '## ' heading no longer closes a claim: same lane effect as M61 (counter real=FAIL)"),
    "M63": ("EQUIV", "logs/probe4-equivalence.txt", "KEYLINE already strips leading blanks; .strip() is a no-op"),
}


def esc(s):
    return s.replace("|", "\\|").replace("\n", "\\n")


def main():
    rows = list(csv.DictReader(open(os.path.join(SEAT, "results.tsv")), delimiter="\t"))
    man = {r["id"]: r for r in csv.DictReader(open(os.path.join(SEAT, "manifest.tsv")), delimiter="\t")}
    out, summ, n_case, n_self, n_surv = [], [], 0, 0, 0
    counts = {"EQUIV": 0, "GAP": 0, "GAP-LANE": 0}
    out.append("| mutant | line / kind | change (old -> new) | counter cases pass/fail | --selftest | verdict | evidence / reason |")
    out.append("|---|---|---|---|---|---|---|")
    for r in rows:
        m = man[r["id"]]
        legs = r["counter_legs"]
        pas = legs.split("pass=")[1].split()[0]
        fail = legs.split("fail=")[1].split()[0]
        st = r["selftest_line"].replace("SELFTEST ", "")
        if int(fail) > 0:
            verdict = "killed by counter cases"
            ev = "counter case(s): " + (r["failed_cases"] or "-")
            n_case += 1
        elif "fail=0" not in r["selftest_line"]:
            verdict = "killed only by --selftest"
            ev = "selftest"
            n_self += 1
        else:
            cls, path, reason = EVID[r["id"]]
            counts[cls] += 1
            n_surv += 1
            verdict = {"EQUIV": "survives both: EQUIVALENT", "GAP": "survives both: GAP (coverage limit)",
                       "GAP-LANE": "survives case table: GAP, caught only by counter real leg"}[cls]
            ev = "%s; %s" % (path, reason)
        out.append("| %s | L%s %s | `%s` -> `%s` | %s/%s | %s | %s | %s |" % (
            r["id"], m["line"], m["kind"], esc(m["old"]), esc(m["new"]), pas, fail, st, verdict, esc(ev)))
        summ.append("%s %s" % (r["id"], r["counter_summary"]))
    open(os.path.join(SEAT, "table.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    open(os.path.join(SEAT, "counter-summaries.txt"), "w", encoding="utf-8").write("\n".join(summ) + "\n")
    print("total=%d killed_by_counter_cases=%d killed_only_by_selftest=%d survivors=%d "
          "equivalent=%d gap=%d gap_lane_only=%d" % (
              len(rows), n_case, n_self, n_surv, counts["EQUIV"], counts["GAP"], counts["GAP-LANE"]))


if __name__ == "__main__":
    main()
