# S67MutKill — round-67 kill power (C1 frozen matrix) and routed decision on K3/K4/K6/K7

Seat: S67MutKill (mutation-tester, leaf). Scope: Part A (kill power of the frozen 31-row C1 matrix against writer mutants
built from the CANDIDATE bytes), Part B (routed defect 6: K3/K4/K6/K7 decisions, see `k67-decision.md`). No candidate
bytes were modified; the frozen counter and matrix were read-only copies (sha verified against the committed instruments
commit: `c1-counter.py` 69f11706…f136b2, `c1-matrix.tsv` 5d26b341…a692).

## Reference (unmutated candidate)

- Candidate: `.ufo/waves/round-67/w1/S67ExecWriter/candidate/souji-receipt-write.py`, sha256
  `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725` (matches its SHA256SUMS).
- Frozen counter on the candidate (base `3639087917…`, `--new-tool`): `SUMMARY matrix=31 base_forgeries=2 base_honest=6
  new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS`, `EXIT=0`. The frozen target is met by my run too.
- Do-nothing (base bytes in the new slot): `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=2
  new_honest=6 class_mismatches=2 regress=PASS`, `EXIT=1` (reproduces `census/round-67/controls/c1-do-nothing.txt`).
- Per-row reference: W1 and W2 refuse with `RECEIPT-ENV-COMMONDIR-MISMATCH`; W3 accepts; all other rows as the frozen
  expectations.

## Part A — kill matrix (`kill-matrix.tsv`, per-row in `kill-rows.tsv`)

A mutant is killed when a row's (verdict, class) differs from the reference. "Frozen" = the 31 frozen rows; "proposed" =
the PROPOSED rows in `recipes/k67-proposed.py` (not frozen, not claim evidence). Every mutant was built with asserted
anchors on the candidate (`recipes/k67-mutants.py`; `mutants/SHA256SUMS`).

| mutant | edit | frozen rows that flip | frozen SUMMARY | proposed rows that flip | writer self-test (37 cases) | verdict |
|---|---|---|---|---|---|---|
| K1 | remove RECEIPT-ENV-CONFIG-SET gate (5 lines) | E1, E2 (refuse without the class token) | class_mismatches=2, EXIT 1 | - | 36/37 | killed (frozen) |
| K2 | remove RECEIPT-ENV-REDIRECT-SET gate | E4, E5, E6 (accept) | new_forgeries=3, EXIT 1 | - | 36/37 | killed (frozen) |
| K3 | remove `-c core.excludesFile` pin | none (31/31 pass) | identical to reference, EXIT 0 | PK3 (accept) | 37/37 | survived frozen; killed by PK3 |
| K4 | remove GIT_CONFIG_GLOBAL devnull pin | none (31/31 pass) | identical, EXIT 0 | PK4 (accept) | 37/37 | survived frozen; killed by PK4 |
| K5 | mask `0o7777` -> `0o777` | MOD2, MOD3 (accept) | new_forgeries=2, EXIT 1 | - | 36/37 | killed (frozen) |
| K6 | remove GIT_NO_REPLACE_OBJECTS pin | none (31/31 pass) | identical, EXIT 0 | PK6 (accept) | 37/37 | survived frozen; killed by PK6 |
| K7 | remove GIT_CONFIG_NOSYSTEM pin | none (31/31 pass) | identical, EXIT 0 | PK7 (accept) | 37/37 | survived frozen; killed by PK7 |
| K8 | remove RECEIPT-INDEX-ENV-SET gate (3 lines) | N3, P13 (accept) | new_forgeries=2, EXIT 1 | - | 34/37 | killed (frozen) |
| K34 | K3 + K4 pins together (pair) | E3 (accept) | new_forgeries=1, EXIT 1 | PK3, PK4 | 37/37 | killed (frozen) |
| M-CD-CALL | remove `_check_env_commondir(root)` call | W2 (accept); W1 (refuse, dirty class, not the mismatch class) | new_forgeries=1, class_mismatches=2, EXIT 1 | PCD-empty (accept) | 34/37 | killed (frozen) |
| M-CD-EMPTY | drop the `value == ""` refusal | none (31/31 pass) | identical, EXIT 0 | PCD-empty (accept) | 37/37 | survived frozen; killed by PCD-empty |
| M-CD-NCABS | non-canonical: abspath both sides, no realpath | none (31/31 pass) | identical, EXIT 0 | PCD-alias (refuse, honest) | 37/37 | survived frozen; killed by PCD-alias |
| M-CD-NCRAW | non-canonical: raw string compare of rev-parse output | W3 (refuse; new_honest=5) | new_honest=5, EXIT 1 | PCD-alias, PCD-up (refuse) | 36/37 | killed (frozen) |
| M-CD-SCRUB | drop GIT_COMMON_DIR from the git() scrub tuple | W1, W2 (accept) | new_forgeries=2, EXIT 1 | PCD-up (refuse; see note) | 36/37 | killed (frozen) |
| M-CD-ROOTREL | relative value resolved against root, not the writer's cwd | none (31/31 pass) | identical, EXIT 0 | PCD-up (refuse, honest) | 37/37 | survived frozen; killed by PCD-up |

Tallies over the 14 single mutants (K34 is a pair): frozen matrix kills **7 of 14 (50%)**; with the proposed rows, **14 of 14**.
The candidate's own writer self-test (37 cases, not the frozen counter) kills exactly the same 7 as the frozen matrix.

Survivors and the rows that pass them: K3, K4, K6, K7, M-CD-EMPTY, M-CD-NCABS, M-CD-ROOTREL pass **all 31 frozen rows**
identically to the reference (the SUMMARY line is byte-identical to the reference). K34 passes 30 rows and fails only E3.

Caveats on the proposed kills (mechanism, not just the verdict):
- M-CD-SCRUB via PCD-up: the kill comes from git itself. With the scrub entry gone, git reads the relative value
  `../.git` against `-C root`, so the base-style lookup breaks and the writer refuses. It is a real flip, but the
  mechanism is not the W-rule. The principled kill for the scrub mutant is W1/W2.
- PCD-up under the BASE writer refuses for the same accidental reason (base has no check; git reads the relative value
  against the repo root). So PCD-up is not a base-honest row; the candidate accepts it by the cwd rule (L2). Recorded
  as an artifact, not a finding about the base.

## Non-canonical compare (M-CD-NCABS, M-CD-NCRAW): the required analysis

- The task expected a non-canonical compare to die on W1. It does not, under either non-canonical variant, and the reason
  is structural. W1 is refused by the canonical AND the non-canonical compare, because its value (a copy of `.git` beside
  the repository) names a different tree-state; the copy path differs lexically from `.git` too, so the lexical difference
  adds nothing. W1's refusal is correct under every compare variant. Only the W3 row and the alias/relative rows can
  discriminate compare variants.
- **Equivalence on every frozen row (M-CD-NCABS):** the frozen counter always passes the honest value as
  `os.path.realpath(<repo>/.git)` (W3), and the fixture root `/fast/scratch/hyaku/...` has no symlink (`realpath` equals
  `abspath` there, checked). So abspath-only comparison equals realpath comparison on W3, and on W1/W2 both refuse.
  NCABS is therefore EQUIVALENT to canonical on all 31 frozen rows. The limit is the matrix's fixtures, not the compare.
- **Rows that discriminate:** PCD-alias (a symlink alias of `.git`: canonical accepts, NCABS and NCRAW refuse the honest
  value), PCD-up (a relative `../.git` from `tools/`: canonical accepts; ROOTREL refuses). Under NCRAW the frozen W3 row
  itself refuses the honest value (new_honest=5), so NCRAW is killed by a frozen row.
- The candidate's own self-test does not bind the symlink case (its case_35 uses a realpath value and a relative `.git`
  from the root, both equivalent under NCABS). NCABS survives the writer self-test (37/37).

## M-CD-EMPTY: the empty-value refusal is not bound by anything in the round

- The explicit `value == ""` refusal is not exercised by the frozen matrix (no row sets an empty value).
- Mechanism of the masking: `os.path.realpath("")` is the writer's CWD. Frozen runs and the candidate's own selftest run
  with cwd = repo root, so `realpath("")` = root, which is not `root/.git`, and the mismatch refusal fires anyway. The
  empty check is redundant in those runs.
- With cwd = `<repo>/.git` (PCD-empty), `realpath("")` equals the common dir, so the mutant ACCEPTS (`PCD-empty` accept) and
  the candidate REFUSES (`RECEIPT-ENV-COMMONDIR-MISMATCH`). So the explicit empty refusal is necessary and is not bound by
  any frozen row or any writer self-test case. Candidate case_36 ("presence is the test") passes under M-CD-EMPTY (37/37):
  it is vacuous for the presence rule. Routed as a named limit (see below).

## Measured findings for the L1 (scratch probes and proposed rows; NOT claim evidence)

1. **L1 parenthetical is wrong for the repository-local `core.excludesFile`.** The frozen L1 text (prereg and counter
   docstring) says a repository-local `core.excludesFile` "still hides untracked content ... on BOTH slots". Measured:
   a repo-local excludes file naming an untracked `tools/hidden.txt` is REFUSED (dirty) by base and candidate (PK3), and a
   direct probe shows `git -c core.excludesFile=/dev/null status --porcelain` lists the file as untracked while plain
   `git status` hides it. The `-c` pin (present on base since r66) overrides repo-local config. The L1 wording should be
   corrected at the next counter; this round's predicates are unaffected (the frozen rows never test it).
2. **The live repo-local residual is `core.fileMode`, and it is accepted.** Repo-local `core.fileMode=false` (a key in the
   repository's own config, the L0 361 scope) with a tracked 755->644 change is ACCEPTED by base and candidate (PRL-fm,
   measured; the writer neither pins nor refuses repo-local mode config). This is the concrete residual for the L0 361
   ruling: the operator decides whether repo-local `core.fileMode` is in scope.
3. **Caller system config route (`GIT_CONFIG_SYSTEM`) is pinned, not refused.** The r66 gate refuses COUNT / PARAMETERS /
   KEY_ / VALUE_ only. `GIT_CONFIG_SYSTEM` is neutralised by the NOSYSTEM pin alone (K7 accepts PK7). The prereg's
   named-limit L3 lists `GIT_NAMESPACE` and `GIT_CEILING_DIRECTORIES` and does not mention `GIT_CONFIG_SYSTEM`.
4. **K6 binds forged bytes to a real rev.** With the replace pin removed, a receipt over the real HEAD records
   `instrument_sha256=e2d379ffe28c…` (the forged bytes); the real instrument blob is `8f513b9f361acb…`. Only a
   replacement-honouring read reaches this; the candidate refuses (dirty).
5. **The candidate's GIT_COMMON_DIR empty/alias/relative cases are not in the frozen matrix or the candidate's own self-test
   in the forms that discriminate** (sections above). This is a coverage finding for the next counter, not a candidate
   defect in the frozen claim.

## Named limits this seat adds (not counted as passes)

- Frozen-matrix kill power: 7 of 14 single writer mutants killed by the frozen 31 rows (K3, K4, K6, K7, M-CD-EMPTY,
  M-CD-NCABS, M-CD-ROOTREL survive). Matches the r66 named limit "C1, kill power" for the pin family; now measured for the
  candidate's GIT_COMMON_DIR check too.
- The frozen matrix has no empty, symlink-alias, or cwd-relative `GIT_COMMON_DIR` row; its W-rows all run with cwd = root
  and realpath values.
- The candidate's own self-test has no symlink-alias case and its empty-value case is masked by the mismatch check (above).

## Routed defect 6 — decision (see `k67-decision.md`)

- K3: fixture-proposed (PK3, repo-local excludes; also the L1 correction).
- K4: fixture-proposed (PK4, global `core.fileMode`; K3/K4 are redundant for E3 only, shown by K34).
- K6: fixture-proposed (PK6, forged replace ref; measured forged receipt binding).
- K7: fixture-proposed (PK7, `GIT_CONFIG_SYSTEM`; route not named in L3).

No survivor is decided defence-in-depth: each pin protects a live route that a fixture demonstrates.

## Tooling

No tool was installed or upgraded. Used host Python 3.14.8 and git 2.56.0 as found. No pacman, no sysctl, no service
change. `disk-guard.sh status` listed the scratch roots before the passes (/fast had 412G available); no mutant or fixture pass ran under pressure.

## Lane and provenance

- The lane was read-only for this seat: `git clone --shared` of the lane into scratch and read-only `git show` / `git
  status`. No lane file, index or ref was written. `git status --porcelain` on the lane shows ` M corpus/QUALITY.md`,
  which is not this seat's edit and was not touched.
- Everything else lives under `/fast/scratch/hyaku/souji-r67/S67MutKill/` (scratch, removed at yield after copying the
  receipts) and this delivery directory. The delivered `recipes/` scripts reference the scratch frozen copy by absolute
  path (`FROZEN = /fast/scratch/hyaku/souji-r67/S67MutKill/frozen/c1-counter.py`); its sha matches the committed bytes.
- `logs/` holds every counter and driver output used in this report: `frozen-CAND.out` (reference), `donothing.out`
  (control), `fc-*.out` (candidate mutants), `frozen-*.out` (r66 mutants run on the BASE bytes, context only), `prop-*.out`
  (proposed rows per slot), `selftest/` (writer self-test per mutant), `analysis.out`.

## Limits

- Mutants are built on the candidate bytes sha `b811ee2a…`. If the candidate changes, rebuild with
  `recipes/k67-mutants.py` (anchors are content-based and assert a unique match; a changed anchor fails loudly).
- Proposed rows are scratch fixtures; they are not in the frozen matrix and are not claim evidence. Their verdicts are
  against the candidate and the base writer, measured once each.
- No regress arm was re-derived beyond the counter's own regress (PASS in every run).
- `M-CD-*` mutants of the candidate's check were not built against any alternative candidate design.

## Suggested lesson input (L1 decides wording)

- Frozen kill power on the C1 matrix: 7/14 single mutants (50%); survivors are the pin family (K3, K4, K6, K7) and the
  empty / non-canonical / root-relative value checks.
- The writer's own self-test does not bind the empty-value refusal (masked by the mismatch check when cwd is the root) or a
  symlink alias. Both are proposed rows (PCD-empty, PCD-alias) for the next frozen counter, not this round's matrix.
- Named-limit corrections: L1 repo-local `core.excludesFile` is closed by the `-c` pin (measured); the live repo-local
  residual is `core.fileMode` (PRL-fm, accepted on base and candidate).
