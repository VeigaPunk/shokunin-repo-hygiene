# SwarmCritic07 — w2 scoped findings (AttackG24)

Seat: SwarmCritic07. Target: W1 finding for C1 item G24. Read-only; no lane edits, no commits.
Full report with all commands and outputs: `.ufo/waves/round-34/w2/AttackG24.md` (same lane).

## Verdict on W1's G24 finding

**PARTIALLY FALSIFIED — impossibility claim refuted by executed emulation; defect analysis confirmed.**

- W1 is right that the item cells are defective: `at=9420341d…` predates the script's introduction
  (`d4928ec…`, ~11 min later; `git cat-file -e` fatal at the pin, reproduced), so the frozen argv dies
  rc=2 at every evaluation (committed do-nothing record `census/round-34/records/controls-c1-do-nothing.txt:24`
  agrees); the frozen exit `0` contradicts the row's own committed outcome column
  (`9c76c72:SKILL.md:249` maps a `k1=12 mismatches=12` line to exit 1); no Q76 prior row binds G24
  (base and tip greps). Addendum: the frozen predicate can never match any run — the script's last
  digit-bearing line is `KINDS …`, printed after `SUMMARY …` (base script :240-:241; reproduced by probe,
  rc=1, `SUMMARY k1=12 …` + `KINDS value=4 shape=7 rc=1`).
- W1 is wrong that no rule-conforming row exists. The frozen counter's own `{BLOB:rev:path}` substitution
  (c1-counter.py:174-192) materializes the row's own script into scratch. Emulating the frozen `judge()`
  directly (importlib, `rev=tip`, both list revs `2b591924…` and `2b0171e2…`): a restated row
  `{BLOB:9c76c72…:tools/souji-capability-agreement.py} --root . --rev {REV} --base {REV} --list-rev d4928ec…`,
  exit `1`, statement `` `KINDS value=4 shape=7 rc=1 (diagnostic; not part of the target)` ``, cause
  `f7329785…` (pickaxe-verified sole author of the row's exact line; ancestor of both list revs) returns
  **('G24', True, …)** — AGREE — at both list revisions. A second shape (pipe through `grep '^SUMMARY'`,
  exit `0`, SUMMARY statement) also AGREEs; the value-drift `same` shape is dead exactly as W1 said
  (`BAD-CAUSE original at parent=False at cause=False` — the at-pin blocks both holds probes).
- Honesty (assessment, not execution): the {BLOB} route is letter-conforming and fully disclosable — true
  provenance, exit correction grounded in the row's own outcome column, genuine reproducible measurement
  (corroborated by committed `census/round-30/records/c1-before.txt` red arm). The residual tradeoff —
  the measured checkout lacks the executable, so the run certifies a counterfactual for the pinned revision —
  is one the frozen bytes themselves permit; the canonical judge/L1 must decide it. It is not the absolute
  impossibility W1 asserted. Recommended shape if pursued: exit `1` {BLOB} row (not the grep-filtered one).
- Minor W1 claims checked: "correct row at the list revision" and "`f7329785` first wrote the row's line"
  are accurate at the r34 list revs (my initial contradictions used the script's `--list-rev` `d4928ec`,
  where line 249 is blank — artifact, withdrawn). W1's refusal of the `git show > tools/…` workaround stands;
  the frozen `{BLOB}` path is the non-mutating equivalent.

## Method notes

- Executed: git/cat-file/pickaxe/merge-base checks; one bounded probe running the extracted script
  (`9c76c72` version) against the live lane with the frozen argv semantics (rc=1, output in scratch
  `run-base.out`); judge emulation via importlib calling `c1.judge()` with crafted restatement rows
  (`judge-probe.py`), cleaned after (0 bytes left).
- Scratch: `/fast/scratch/hyaku/souji-r34/SwarmCritic07/` only; lane untouched; ceiling respected.
- Peer cross-check: SwarmReviewer06 (AttackG23) independently found W1's "unreachable" verdict falsified
  for G23 via a different, engine-valid row — consistent with this seat's conclusion that W1's impossibility
  claims overreach; G24's distinct blocker (at-pin predates script) is what forces the {BLOB} shape.
