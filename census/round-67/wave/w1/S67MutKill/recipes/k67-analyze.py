#!/usr/bin/env python3
"""k67-analyze.py — build kill-matrix.tsv and kill-rows.tsv from the S67MutKill run outputs (scratch only).

Reference = the unmutated candidate. A mutant KILLS a row when that row's (verdict, class-hit) differs from the
reference. Frozen rows come from work/frozen-<NAME>.out (CASE lines); proposed rows from work/prop-<NAME>.out
(PROP lines, slot=base). Writer self-test counts come from work/wst/<NAME>.out (SELFTEST line).
"""
import os
import re
import sys

S = "/fast/scratch/hyaku/souji-r67/S67MutKill"
W = os.path.join(S, "work")
MUTANTS = ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K34",
           "M-CD-CALL", "M-CD-EMPTY", "M-CD-NCABS", "M-CD-NCRAW", "M-CD-SCRUB", "M-CD-ROOTREL"]
EDIT = {
    "K1": "remove RECEIPT-ENV-CONFIG-SET gate (r66 pin family, 5 lines)",
    "K2": "remove RECEIPT-ENV-REDIRECT-SET gate (5 lines)",
    "K3": "remove git() `-c core.excludesFile=<devnull>` pin",
    "K4": "remove git() GIT_CONFIG_GLOBAL=os.devnull pin",
    "K5": "snapshot mode mask 0o7777 -> 0o777",
    "K6": "remove git() GIT_NO_REPLACE_OBJECTS=1 pin",
    "K7": "remove git() GIT_CONFIG_NOSYSTEM=1 pin",
    "K8": "remove RECEIPT-INDEX-ENV-SET gate (3 lines)",
    "K34": "remove K3 and K4 pins together (pair)",
    "M-CD-CALL": "remove the _check_env_commondir(root) call",
    "M-CD-EMPTY": "drop the empty-value refusal",
    "M-CD-NCABS": "non-canonical compare: abspath both sides (no realpath)",
    "M-CD-NCRAW": "non-canonical compare: raw string compare of rev-parse output",
    "M-CD-SCRUB": "drop GIT_COMMON_DIR from the git() scrub tuple",
    "M-CD-ROOTREL": "resolve relative value against root, not the writer's cwd",
}
CASE_RE = re.compile(r"^CASE (\S+) expect=(\S+) base=(\S+) base_findings=(.*?) new=(\S+) new_findings=(.*)$")
PROP_RE = re.compile(r"^PROP (\S+) slot=(\S+) expect=(\S+) verdict=(\S+) class=(.*?) rc=(\d+) stderr=")
SUM_RE = re.compile(r"^SUMMARY (.*)$")
EXIT_RE = re.compile(r"^EXIT=(\d+)$")
ST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def frozen_rows(path):
    rows, summary, exitc = {}, "", None
    for line in read(path):
        m = CASE_RE.match(line)
        if m:
            case, expect, base, bfind, new, nfind = m.groups()
            rows[case] = {"expect": expect, "base": base, "new": new,
                          "new_class": nfind if nfind != "-" else "-"}
            continue
        m = SUM_RE.match(line)
        if m:
            summary = m.group(1)
        m = EXIT_RE.match(line)
        if m:
            exitc = int(m.group(1))
    return rows, summary, exitc


def proposed_rows(path):
    rows = {}
    for line in read(path):
        m = PROP_RE.match(line)
        if m:
            row, slot, expect, verdict, klass, rc = m.groups()
            rows[row] = {"expect": expect, "verdict": verdict, "class": klass}
    return rows


def selftest(path):
    if not os.path.isfile(path):
        return "-"
    for line in read(path):
        m = ST_RE.match(line)
        if m:
            return f"cases={m.group(1)} pass={m.group(2)} fail={m.group(3)}"
    return "no-SELFTEST-line"


def norm_frozen(row):
    return (row["new"], row["new_class"])


def main():
    ref_rows, ref_sum, ref_exit = frozen_rows(os.path.join(W, "frozen-CAND.out"))
    ref_prop = proposed_rows(os.path.join(W, "prop-CAND.out"))
    prop_order = [l.split()[1] for l in read(os.path.join(W, "prop-CAND.out")) if l.startswith("PROP ")]
    prop_order = list(dict.fromkeys(prop_order))
    frozen_order = list(ref_rows.keys())
    base_rows, base_sum, base_exit = frozen_rows(os.path.join(W, "donothing.out"))
    base_prop = proposed_rows(os.path.join(W, "prop-BASE.out"))

    kill_rows_lines = []
    header = ["mutant", "edit"] + [f"F:{c}" for c in frozen_order] + [f"P:{p}" for p in prop_order]
    kill_rows_lines.append("\t".join(["slot"] + header[1:]))
    ref_cells = [f"{ref_rows[c]['new']}/{ref_rows[c]['new_class']}" for c in frozen_order] + \
                [f"{ref_prop[p]['verdict']}/{ref_prop[p]['class']}" for p in prop_order]
    kill_rows_lines.append("\t".join(["CAND-reference", "unmutated candidate"] + ref_cells))
    base_cells = [f"{base_rows[c]['new']}/{base_rows[c]['new_class']}" for c in frozen_order] + \
                 [f"{base_prop[p]['verdict']}/{base_prop[p]['class']}" for p in prop_order]
    kill_rows_lines.append("\t".join(["BASE-r66-writer", "base bytes in the new slot (do-nothing)"] + base_cells))

    km = ["mutant\tedit\tfrozen_SUMMARY\tfrozen_EXIT\tfrozen_flipped_rows\tproposed_flipped_rows\t"
          "frozen_verdict\tproposed_verdict\twriter_selftest\tfinal_verdict"]
    for m in MUTANTS:
        fpath = os.path.join(W, f"fc-{m}.out")
        rows, summ, exitc = frozen_rows(fpath)
        flips = [c for c in frozen_order if c in rows and norm_frozen(rows[c]) != norm_frozen(ref_rows[c])]
        pflips = []
        ppath = os.path.join(W, f"prop-{m}.out")
        prows = proposed_rows(ppath)
        for p in prop_order:
            if p in prows and (prows[p]["verdict"], prows[p]["class"]) != (ref_prop[p]["verdict"], ref_prop[p]["class"]):
                pflips.append(p)
        st = selftest(os.path.join(W, "wst", f"{m}.out"))
        st_fail = bool(re.search(r"fail=[1-9]", st))
        frozen_kill = bool(flips) or (exitc not in (0, None) and summ != ref_sum)
        prop_kill = bool(pflips)
        verdict = "killed" if (frozen_kill or prop_kill) else "SURVIVED"
        fv = "killed" if frozen_kill else "survived"
        pv = "killed" if prop_kill else "survived"
        km.append("\t".join([m, EDIT[m], summ, str(exitc), ",".join(flips) or "-", ",".join(pflips) or "-",
                             fv, pv, st, verdict + ("(writer-selftest also)" if st_fail else "")]))
        cells = []
        for c in frozen_order:
            if c in rows:
                cur = norm_frozen(rows[c])
                cells.append(cur[0] + "/" + cur[1] if cur == norm_frozen(ref_rows[c]) else f"FLIP:{cur[0]}/{cur[1]}")
            else:
                cells.append("missing")
        for p in prop_order:
            if p in prows:
                cur = (prows[p]["verdict"], prows[p]["class"])
                refp = (ref_prop[p]["verdict"], ref_prop[p]["class"])
                cells.append(f"{cur[0]}/{cur[1]}" if cur == refp else f"FLIP:{cur[0]}/{cur[1]}")
            else:
                cells.append("missing")
        kill_rows_lines.append("\t".join([m, EDIT[m]] + cells))
    with open(os.path.join(W, "kill-matrix.tsv"), "w") as f:
        f.write("\n".join(km) + "\n")
    with open(os.path.join(W, "kill-rows.tsv"), "w") as f:
        f.write("\n".join(kill_rows_lines) + "\n")
    print("\n".join(km))
    print()
    print("\n".join(kill_rows_lines[:2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
