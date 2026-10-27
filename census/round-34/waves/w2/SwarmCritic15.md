# SwarmCritic15 — seat report (AttackE15c)

w2 falsification seat, lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only.
Full analysis with commands and line-level citations:
`.ufo/waves/round-34/w2/AttackE15c.md` (authoritative for this seat).

## Verdict on W1's E15c finding

- **Do-nothing MISMATCH: CONFIRMED, reproduced.** Frozen argv
  (`c1-items.tsv:58`, `git diff a65fac98964b445758e94c8057280c9a19d302ff8 778747e… -- corpus/knowledge/`)
  exits 128 `fatal: bad revision …` in the live repo, matching the committed control
  (`census/round-34/records/controls-c1-do-nothing.txt:42`) and W1's deliverable. Not an
  artifact: no object store anywhere (11,497 objects scanned), no alternates/replace/jj escape.
- **W1 root-cause class FALSIFIED.** W1 labels E15c "missing/unresolvable pinned revision"
  (with G24). In fact the frozen pin is a **41-character malformed string** — the real 40-hex
  commit `a65fac98964b445758e94c805728c9a19d302ff8` exists, is an ancestor of base, and the
  row's stated counting claim (`+ground:`×2 / `-ground:`×0) holds at the tip (executed: rc=0,
  counts 2/0). The defect is a freeze-time transcription slip in the frozen item list
  (introduced `2b59192…`, the only commit ever touching `c1-items.tsv`), corroborated by
  sibling E14a (`c1-items.tsv:54`) carrying the identical corrupted SHA.
- **Honest route W1 missed: EXISTS, gate-verified.** A Q75/Q76/A1 argv-correction restatement
  with cause `315422ba9970f03c27f8a9184446783b7fcdf0a7` (round-24 final — authored line 68's
  text; ancestor of list-rev `2b0171e…`) passes every executable gate in
  `census/round-34/c1-counter.py:245-323`: line-authorship at cause(parent absent/present ✓),
  frozen-argv-fails-at-cause ✓, corrected argv names `corpus/knowledge` ✓, corrected run at
  `--rev` exits 0 with the frozen predicate holding ✓, Q76 no prior binding ✓. End-to-end
  counter execution NOT performed (labeled [INFERENCE] from executed gates).

## Impacted axes

- C1 calibration: E15c is reachable to AGREE (unlike W1's implied stuck class), so the
  `SUMMARY items=60 agree=60 mismatches=0` target is not blocked by this item, provided the
  lane appends the restatement row. If the lane instead treats E15c as unresolvable content,
  it may wrongly restate with a *different* base revision (unnecessary and semantically wrong);
  the correct repair is the same command with the correctly-spelled 40-hex SHA.
- Preregistration hygiene: the frozen enumeration's full-SHA expansion needs a length-40 check
  (would have caught both E14a and E15c before freeze).

## Attack log (summary)

Adversarial falsification of W1 in five probes: verbatim reproduction → artifact sweep
(store/alternates/replace/jj) → length/typo diff (41 vs 40, one inserted `0`) → direct
existence+ancestry+claim-truth test → restatement-gate walk of the frozen counter. No lane
file modified; no commits; no fixture execution; no writes outside the two report files and
a `/tmp` diff capture.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE15c.md` — full report (Status / Evidence / Findings /
  Attack log / Deliveries) with exact file:line and revisions.
- This file — scoped seat report.
