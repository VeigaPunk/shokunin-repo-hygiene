# S67MutKill — routed decision on the r66 survivors K3, K4, K6, K7 (routed defect 6)

Reference: the unmutated r67 candidate, sha256 `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725`
(the frozen target `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0
regress=PASS`, EXIT=0, reproduced). Each mutant is one edit off the candidate (anchors asserted; see `recipes/k67-mutants.py`).
Each of the four candidate-built mutants makes the same single-line edit as the r66 mutants K3, K4, K6, K7 (`S66MutKill/mutants`): rebuilt from the base bytes, the r66-equivalent mutant files are byte-identical to those r66 files (`cmp`), and on the candidate the same anchor is removed with the candidate's added code left in place.

Every decision below rests on a PROPOSED row built in `recipes/k67-proposed.py`. The proposed rows are NOT the frozen
matrix (`census/round-67/c1-matrix.tsv` is not edited). Each defect row has an honest control with the same fixture
minus the defect; both controls accept on base, the candidate and all four mutants. Verdicts are in `logs/prop-*.out`
and `kill-rows.tsv`.

Table of results (the frozen 31-row matrix is identical to the reference for all four mutants: every row passes):

| mutant | frozen 31 rows | proposed defect row | defect row under mutant | honest control under mutant | decision |
|---|---|---|---|---|---|
| K3 (drop `-c core.excludesFile` pin) | survives (0 flips) | PK3 (repo-local core.excludesFile) | accept (base and candidate: refuse) | accept | fixture-proposed |
| K4 (drop `GIT_CONFIG_GLOBAL=devnull` pin) | survives (0 flips) | PK4 (global core.fileMode=false) | accept (base and candidate: refuse) | accept | fixture-proposed |
| K6 (drop `GIT_NO_REPLACE_OBJECTS=1` pin) | survives (0 flips) | PK6 (replace ref forging HEAD's instrument) | accept (base and candidate: refuse) | accept | fixture-proposed |
| K7 (drop `GIT_CONFIG_NOSYSTEM=1` pin) | survives (0 flips) | PK7 (GIT_CONFIG_SYSTEM core.fileMode=false) | accept (base and candidate: refuse) | accept | fixture-proposed |

Pair evidence for K3/K4 (`K34` = both pins removed): the frozen row E3 flips to accept (`new_forgeries=1`, EXIT=1).
Removing one of the two pins alone leaves E3 refused, which is the mutual redundancy named in the r66 lesson. The two pins
are redundant for E3 only; each still protects its own route (below).

---

## K3 — remove `git()`'s `-c core.excludesFile=<devnull>` pin

Frozen matrix: survives (`SUMMARY` identical to reference; all 31 rows pass, E3 included when K4 still pins). Pair K34 is
killed only through E3, because K3 and K4 cover the same row.

What the pin still protects: a REPOSITORY-LOCAL `core.excludesFile` (a key in the repository's own `.git/config`, which is
repo state, not a caller env var). Measured on the fixture `PK3`: an untracked `tools/hidden.txt` named by the repo-local
excludes file is INVISIBLE to `git status` without the pin, and is visible (refused, dirty) with the pin.
The pin wins over repo-local config because `-c` is the highest-precedence config source. A direct probe (no writer,
scratch repo) gave the same: plain `git status` shows only `?? excl.txt`; `git -c core.excludesFile=/dev/null status`
shows `?? excl.txt` and `?? hidden.txt`.

Missing fixture class: repo-local excludes config. The frozen counter has no such row. The named limit L1 in
`census/round-67/c1-counter.py` and the prereg says a repository-local `core.excludesFile` "still hides untracked content
on BOTH slots". That is measured FALSE for the pinned writer: base and candidate both refuse `PK3`.

Proposed row PK3 (refuse, dirty) and honest control PK3h (accept): base refuse / accept, candidate refuse / accept,
K3 accept / accept (PK3 flips).

decision: fixture-proposed

Reason: K3 is killed by its own fixture (PK3), not only through the E3 redundancy; the pin closes a repo-state route the
frozen claim currently describes as open. The frozen matrix cannot take the row this round. The L1 must record the
named-limit correction (L1 parenthetical) and the row as a proposal for the next frozen counter.

---

## K4 — remove `git()`'s `GIT_CONFIG_GLOBAL=os.devnull` pin

Frozen matrix: survives (identical to reference, all 31 rows pass). E3 is the only frozen row touched by K4 and it stays
refused because K3's `-c` pin still covers `core.excludesFile`.

What the pin still protects: a CALLER-named global config file (`GIT_CONFIG_GLOBAL`, an env route the r66 gate does NOT
refuse; it is pinned away instead). Any key the `-c` pins do not cover is then read from the caller's file. The
decisive key is `core.fileMode`, which the writer does not pin. Measured on the fixture `PK4` (repo-local
`core.filemode` UNSET so the global value is effective; tracked 755->644):

- base and candidate (pin in place): `refuse` (lane worktree is dirty), the mode change is visible;
- K4 (pin removed): `accept`, the caller's global `fileMode=false` hides the mode change; a receipt is written.

Note for the L1: `GIT_CONFIG_GLOBAL` was not a measured row before this round; the frozen E3 row uses excludes, which
the `-c` pin covers. The `fileMode` key is the row that is not covered by any `-c` pin.

Missing fixture class: a caller-named global config carrying a non-excludes key.

Proposed row PK4 (refuse, dirty) and honest control PK4h (accept): base refuse / accept, candidate refuse / accept,
K4 accept / accept (PK4 flips).

decision: fixture-proposed

Reason: the pin protects a route the excludes-only frozen rows (E3) cannot see. K4 is not defence-in-depth: its own
fixture is a live, measured forgery on the mutant. The redundancy with K3 concerns E3 only.

---

## K6 — remove `git()`'s `GIT_NO_REPLACE_OBJECTS=1` pin

Frozen matrix: survives (identical to reference, all 31 rows pass). No frozen row creates a replace ref.

What the pin still protects: the repository's OWN `refs/replace/*` namespace (repo state, not caller env: the
`GIT_REPLACE_REF_BASE` env route is already refused by the r66 gate). A replace ref makes `git cat-file`, `ls-tree` and
`status` read a replacement object in place of the real commit.

Measured on the fixture `PK6`: a replace ref for HEAD whose replacement tree carries FORGED instrument bytes, with the
index and worktree carrying those same forged bytes.

- base (pin in place): `refuse` (dirty: the replacement is not honoured, so the index differs from the real HEAD tree);
- K6 (pin removed): `accept`, rc 0. The receipt is written with `instrument_sha256=e2d379ffe28c…` (the FORGED bytes). The
  real HEAD instrument blob (`git cat-file` with replacement disabled) is `8f513b9f361acb7e6e153948d216edb82488d912c9c394dfb3e57604fdd4ea6e`.
  So K6 writes a receipt that binds instrument bytes the commit does not contain.

Missing fixture class: a repo-state replace ref for the rev.

Proposed row PK6 (refuse) and honest control PK6h (accept, no replace ref): base refuse / accept, candidate refuse /
accept, K6 accept / accept (PK6 flips).

decision: fixture-proposed

Reason: K6 is a live forgery of the receipt's instrument binding (measured above). The pin's job is visible only in a
repo-state route no frozen row creates. The base refusal in PK6 is produced by the dirty check, not by a replace-specific
check; the replacement pin is what makes the forgery visible as dirty. The L1 should cite both facts, not just "refused".

---

## K7 — remove `git()`'s `GIT_CONFIG_NOSYSTEM=1` pin

Frozen matrix: survives (identical to reference, all 31 rows pass). No frozen row sets a system config.

What the pin still protects: a CALLER-named SYSTEM config (`GIT_CONFIG_SYSTEM`, an env route the r66 gate does NOT refuse,
since it refuses only COUNT / PARAMETERS / KEY_* / VALUE_*). The NOSYSTEM pin is the only defence for it on base and
candidate. The r66 lesson says it is "inert once GIT_CONFIG_NOSYSTEM=1 is pinned"; the prereg's named-limit L3 names only
GIT_NAMESPACE and GIT_CEILING_DIRECTORIES and does not mention GIT_CONFIG_SYSTEM.

Measured on the fixture `PK7` (repo-local `core.filemode` UNSET; `GIT_CONFIG_SYSTEM` names a file with
`core.fileMode=false`; tracked 755->644):

- base and candidate (pin in place): `refuse` (lane worktree is dirty);
- K7 (pin removed): `accept`, rc 0.

Missing fixture class: a caller-named system config carrying a non-excludes key.

Proposed row PK7 (refuse, dirty) and honest control PK7h (accept): base refuse / accept, candidate refuse / accept,
K7 accept / accept (PK7 flips).

decision: fixture-proposed

Reason: the route is live, not theoretical, and the r66 gate does not name it. Whether the L1 adds GIT_CONFIG_SYSTEM to the
caller-route enumeration (a predicate change, so next round) is the operator's ruling; this round it remains pinned.

---

## Summary for the L1 (routed defect 6)

- All four survivors are killed by a proposed fixture; none is a defence-in-depth-only pin in this measurement.
- The K3/K4 redundancy is real for E3 only (pair K34 flips E3).
- Every proposed row is outside the frozen matrix and is not claim evidence. They are candidates for the next frozen
  counter (a new counter, not an amendment, per the r66 M2 class).
