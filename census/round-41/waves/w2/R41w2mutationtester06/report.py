#!/usr/bin/env python3
"""Builds ../R41w2mutationtester06.md from mutants/out/SUMMARY.tsv (verbatim SUMMARY lines) and the verdict map."""
import os
SEAT = os.path.dirname(os.path.abspath(__file__))
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(SEAT, "mutants/out/SUMMARY.tsv"), encoding="utf-8")][1:]
man_rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(SEAT, "mutants/manifest.tsv"), encoding="utf-8")][1:]
man = {r[0]: r for r in man_rows}
CAUGHT = "COUNTER"
V = {}
for m in ["L01","L02","L03","L04","L05","L06","L07","L08","L09","L10","L11","L12","L13","L14","L16","L17","L22",
          "S04","S05","S06","S08","S09","S10","S12","S13","S14","S17","M01","M02","M03","M05"]:
    V[m] = (CAUGHT, "detected: SUMMARY target unmet (exit 1)")
V["L15"] = ("GAP", "duplicate I3 line passes; counter has no duplicate check (N1); only a human diff catches it")
V["L18"] = ("GAP", "I4 CORRECTION line inside a code fence still counted; counter is fence-blind (N1); human reads the fence")
V["L19"] = ("GAP (calibration)", "prose says the three corrections are withdrawn; SUMMARY still corrected=3; no committed check reads prose (N1); human only")
V["L20"] = ("BENIGN-PASS", "trailing space on a CORRECTION line; target still met, correct")
V["L21"] = ("OUT-OF-SCOPE", "lesson header attempt number not read by any counter; not a claim-level change; human only")
V["L23"] = ("GAP", "duplicate I1 line passes (N1 class); human only")
V["S01"] = ("HUMAN-ONLY", "S033 status cell; counter derives rows at MEASURED so tip registry edits cannot move I1; registry census COULD-NOT-EVALUATE (exit 2)")
V["S02"] = ("HUMAN-ONLY", "S033 tier cell A->B; same as S01")
V["S03"] = ("HUMAN-ONLY", "S033 quote cell; same as S01")
V["S07"] = ("HUMAN-ONLY", "S258 location-cell date; counter reads only tier/status/date cells 3,7,8 and the v2.56.0/worktree.c blob (cells 1,5)")
V["S11"] = ("GAP (calibration, new)", "second S258 row (tier B, queued) after the original passes: sourced() returns on first match; no duplicate-id check in the counter; registry census inoperable")
V["S15"] = ("GAP", "S258 row inside a code fence still matched; sourced() is fence-blind (N2 class)")
V["S16"] = ("BENIGN-PASS", "extra space in S258 status cell; cells are stripped; target still met, correct")
V["S18"] = ("GAP (census-only)", "S258 used-by changed to corpus/lessons/round-40.md (contains 0 occurrences of S258); counter does not read used-by; K1 would flag it but registry census COULD-NOT-EVALUATE")
V["M04"] = ("BENIGN-PASS", "pure append to round-40.md (append-only rule allows it); target still met, correct")
V["M01"] = ("COUNTER (rewritten)", "detected: rewritten=1 (anchor absent at tip); mismatched stays 3 because present/derived read MEASURED")
V["M02"] = ("COUNTER (rewritten)", "detected: rewritten=1 (append-only prefix broken)")
V["M03"] = ("COUNTER (rewritten)", "detected: rewritten=1 (prefix broken)")
V["M05"] = ("COUNTER (rewritten)", "detected: rewritten=1")
assert set(V) == set(man), set(man) ^ set(V)
det = sum(1 for v in V.values() if v[0].startswith("COUNTER"))
surv_nonbenign = [k for k, v in V.items() if not v[0].startswith("COUNTER") and not v[0].endswith("PASS")]
out = []
w = out.append
w("# R41w2mutationtester06 — mutation evidence for the landed C1 corrections (r41 wave 2)\n")
w("Seat: R41w2mutationtester06 (role mutation-tester). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `1d41c13574db80fdd9a4bde490b712da7ce2a85f`; landed C1 commit `31e4d3e758bb903808a9270018d7e5be99ce38a4`. Counter `census/round-41/c1-counter.py` (sha256 pinned in the counter; items digest checked at run time). Target: `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`.\n")
w("## Verdict\n")
w("**Calibration: partial.** The counter's SUMMARY leaves the target for 31 of 46 single-defect edits. Every edit to a field it reads is caught: the three derived values, the MEASURED rev (wrong hex, truncated, real-but-other commit), the CORRECTION id, file and filed tokens, the I1 source id (absent or S033), deletion of any CORRECTION line, trailing text, an unknown-id junk line, the S258 tier, status, date, version, cell count and presence, and every rewrite of the filed round-40 anchor or prefix. The three benign controls (L20, S16, M04) correctly leave the target met. Twelve non-benign edits leave it met: duplicate lines (L15, L23), a fenced CORRECTION line (L18), a prose retraction of all three corrections (L19), a lesson header edit (L21), a duplicate S258 row after the original (S11, new), a fenced S258 row (S15), the S033 status/tier/quote cells (S01-S03, human-only by design), the S258 location date (S07), and the S258 used-by cell (S18, census-only). L19, S11 and S18 are the calibration-relevant survivors; the rest are named limits N1/N2 or cells no committed check reads.\n")
w("Pre-existing at tip, reported not repaired: `tools/souji-landing-gate.py --round 41` at tip reports `findings=4` (including `LG-DANGLING-PTR corpus/lessons/round-41.md:113 cites path absent at 1d41c13`, the untracked `.ufo/waves/round-40/w2-run.err`) and exits 2; every mutant also exits 2, so the landing gate discriminates nothing here. `tools/souji-registry-agreement.py` exits 2 (`COULD-NOT-EVALUATE derived facts are trivial`) at tip with both list-rev `1d41c13` and freeze `e2a7431`, so no operable census reads the registry; the S01-S03, S07, S11, S15 and S18 survivors have no census catcher at this lane.\n")
w("## What was run\n")
w("All commands ran from the lane root or from my scratch `/fast/scratch/hyaku/souji-r41/R41w2mutationtester06`; nothing was committed, pushed or written to the lane. Installs: none.\n")
w("1. Baseline (read-only): `python3 -B census/round-41/c1-counter.py --root <LANE> --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch <SCR>` → `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, EXIT=0 (`mutants/out/baseline.txt`). Same at the landed commit `31e4d3e` (exit 0).")
w("2. No-edit control through the harness: `bash census/round-41/score-candidate.sh c1 <SCR>` → the same SUMMARY, EXIT=0.")
w("3. Mutant generation: `make.py` and `make_reg.py` (in this seat dir) read tip bytes with `git -C <LANE> show 1d41c13...:<path>` and apply one exact-substring edit each, asserting the substring occurs once in its row/line (`mutants/manifest.tsv`, 46 mutants, `mutants/*.md`).")
w("4. Scoring: `run.py` runs each mutant (a) through `bash census/round-41/score-candidate.sh c1 <SCR> <dest>=<mutant>` for the allowlisted dests `corpus/lessons/round-41.md` and `corpus/SOURCES.md` (`mutants/out/<id>.score.txt`), and (b) in a private clone made the same way (`git clone --shared`, copy, commit in the clone with GIT_AUTHOR/COMMITTER env, `rev-parse --show-toplevel` asserted) for every mutant including the round-40 mutants, which are outside the allowlist and so were not sent through the harness (`mutants/out/<id>.clone.txt`). Clones were removed after each run. Landing gate was run in the same clone (`mutants/out/<id>.clone.txt`, tail).")
w("5. Census probes: `tools/souji-registry-agreement.py --root <LANE> --rev 1d41c13... --list-rev {1d41c13..., e2a7431...}` → `COULD-NOT-EVALUATE derived facts are trivial`, EXIT=2 (`mutants/out/baseline.txt`). Grep: `git show 1d41c13...:corpus/lessons/round-40.md | grep -c S258` → 0; `...:corpus/lessons/round-41.md | grep -c S258` → 7.\n")
w("Mutation receipts: `mutants/out/SUMMARY.tsv` (one row per mutant), `mutants/out/*.score.txt`, `mutants/out/*.clone.txt`. Scratch clones and base copies were deleted; the scratch dir itself is removed before yield.\n")
w("## Per-mutant results\n")
w("Columns: id; edit; harness SUMMARY (score-candidate, EXIT); clone SUMMARY (EXIT); verdict. `—` = not allowlisted, harness not run; the clone line is the same counter at a private commit.\n")
w("| id | edit | harness SUMMARY (EXIT) | clone SUMMARY (EXIT) | verdict | why |")
w("|---|---|---|---|---|---|")
for r in rows:
    mid, dest, desc, exp, sexit, ssum, cexit, csum, gexit = r
    h = ("%s (EXIT=%s)" % (ssum, sexit)) if sexit != "None" else "— (EXIT=n/a)"
    v = V[mid]
    w("| %s | %s | `%s` | `%s` (EXIT=%s) | %s | %s |" % (mid, desc.replace("|", "/"), h.replace("|", "/"), csum.replace("|", "/"), cexit, v[0], v[1].replace("|", "/")))
w("")
w("Counts: detected by the counter %d; non-benign survivors %d (%s); benign controls correctly passing 3 (L20, S16, M04).\n" % (det, len(surv_nonbenign), ", ".join(sorted(surv_nonbenign))))
w("## Distinguishing counter detections from human/census-only catches\n")
w("- Counter-detected (%d): every edit that changes a value, id, rev, token, line count or the S258 tier/status/date/version/cell-count/presence, plus the four round-40 rewrites (M01-M03, M05). The counter sees these at its own SUMMARY (`corrected`, `uncorrected`, `junk`, `rewritten`, `sourced`)." % det)
w("- Human-only (no committed checker reads the edited cell): S01-S03 (S033 status, tier, quote), S07 (S258 location date), L21 (header attempt number), L15/L23 (duplicate lines, only a diff shows them), L18/S15 (fenced lines, a reader sees the fence), L19 (prose retraction).")
w("- Census-only: S18 (used-by names round-40.md, which has no S258; census K1 would flag it). Registry census inoperable at this lane (exit 2 at two list-revs), so no committed check catches it today.")
w("- New calibration gap, not named in N1/N2: S11 (duplicate S258 row after the original). `sourced()` returns on the first ID match, so a second tier-B/queued row passes. Suggested named limit: N2 should cover duplicate ids; no fix made here (frozen counter).\n")
w("## Limits of this probe\n")
w("- Mutants are single-defect substring edits chosen by me; they do not exhaust the space. A survivor is a coverage finding, not a contract change.")
w("- Round-40 mutants and the landing-gate runs used a private clone with the same procedure as the harness, not the harness itself (dest not on the allowlist).")
w("- The registry census and landing gate could not discriminate any mutant at this lane (exit 2 on baseline), so their columns are recorded but carry no weight.")
w("- No candidate was written to the lane. The counter's MEASURED rev (`bffcc0f...`) is the fixed measurement point; registry edits at tip cannot move derived values by design, which is why S01-S03 survive.\n")
w("## Commands and files\n")
w("- `.ufo/waves/round-41/w2/R41w2mutationtester06/make.py`, `make_reg.py`, `run.py`, `report.py` (helpers); `mutants/` (46 mutants, manifest); `mutants/out/` (receipts).")
open(os.path.join(SEAT, "..", "R41w2mutationtester06.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("detected", det, "survivors", len(surv_nonbenign), sorted(surv_nonbenign))
