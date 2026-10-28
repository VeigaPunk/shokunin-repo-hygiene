# R40w2simplifier01 — YAGNI review of the landed C1 counter

Seat: R40w2simplifier01 (role simplifier, leaf, no subagents). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Target bytes: `census/round-40/c1-counter.py` at landed instrument commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`.
Those bytes are identical at measured tip `549d9ec53a1f5932337ff14438fcd22b0621828d` (checked with
`git diff --stat 128e412 549d9ec -- census/round-40/c1-counter.py`, empty). Later HEAD `994de3b` changes the counter
(see §5); it is recorded as context, not attacked as the landed bytes.

Re-run: `python3 -B .ufo/waves/round-40/w2/R40w2simplifier01-repro.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --work <empty scratch dir>`
(output of the run that this report quotes: `.ufo/waves/round-40/w2/R40w2simplifier01-repro.out`). The script reads the lane
only through `git show`, builds every fixture repo and counter copy under `--work`, and writes nothing else.

## Verdict

**FALSIFIED** — the proposition "every arm of the landed C1 counter is load-bearing" is false. Seven arms (R1–R6 and R8 in §2)
are verdict-neutral: duplicates of reconciler checks, label-only, unreachable, or no-ops. R7 and R9 are candidates with inferred
effect. Two arms are NOT redundant: L221 and L225 are the only verdict-level guards for the strict-descendant predicate (SAFE, §3).
The counter's own forged control is closure-only and can pass with the control missing (§4, calibration; not a YAGNI item).

Verdict per candidate is in §2; the decisive commands are in §1 and §3.

## 1. Commands run (exact) and what they showed

Lane reads (no writes in the lane):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e
git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 128e412b0ced3c243dc27c3dd3332054a611bc2e HEAD   # YES at 549d9ec
git -C .../souji-shokunin diff --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e 549d9ec53a1f5932337ff14438fcd22b0621828d -- census/round-40/c1-counter.py tests/fixtures/r40-c1-evidence.py   # empty
git -C .../souji-shokunin diff 128e412 994de3b -- census/round-40/c1-counter.py                                     # later HEAD, L258-262 changed
cat -n census/round-40/c1-counter.py ; cat -n census/round-40/preregistration.txt
```

Real L1 command at the measured tip (lane items, register read from `549d9ec`), landed counter:

```
python3 -B <scratch>/landed/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
  --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3
```
real output, rc 0:
```
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
```
(matches `census/round-40/records/c1-after-d.txt`.) The same command against `--rev 128e412...` exits 1 with `ITEM ... OPEN ANCHOR-ABSENT` and
`REGISTER-ABSENT`: the evidence and anchors postdate the instrument commit, so the landed rev is not a measurement point.

Git exit-code probes (read-only on the lane; the config probe used a scratch file):

```
git -C R merge-base --is-ancestor 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39  -> rc 0   (equal is an ancestor of itself)
git -C R merge-base --is-ancestor 0000000000000000000000000000000000000000 HEAD -> "fatal: Not a valid commit name", rc 128
git -C R merge-base --is-ancestor 6ded1248b6d0 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39 -> rc 0
git -C R cat-file -e 0000000000000000000000000000000000000000^{commit} -> rc 128
git -C <fixture> with a fake system file [alias] zz=status, env GIT_CONFIG_GLOBAL=/dev/null:
  GIT_CONFIG_SYSTEM=<file>                       -> prints "status", rc 0
  GIT_CONFIG_SYSTEM=/dev/null                    -> rc 1 (nothing)
  GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_SYSTEM=/dev/null -> rc 1 (nothing)
  GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_SYSTEM=<file> -> rc 1 (nothing)
git -C /nonexistent-dir cat-file -e HEAD^{commit} -> "fatal: cannot change to ...", rc 128
TMPDIR=<dir> python3 -B -c "import tempfile;print(tempfile.gettempdir())" -> <dir>
```

Fixture (the r40 counter's own cases) against the landed counter and against single-arm deletions of the landed bytes
(`python3 -B tests/fixtures/r40-c1-evidence.py --counter <copy> --base-counter census/round-39/c1-counter.py --work <scratch>`), reproduced in
`R40w2simplifier01-repro.out` §1:

```
landed                     rc=0 SUMMARY cases=8 pass=8 fail=0
no-L221-equal              rc=1 SUMMARY cases=8 pass=7 fail=1 case-register-equal-rejected=FAIL rc=1 violations=0 ...
no-L229-notancestor        rc=0 SUMMARY cases=8 pass=8 fail=0
no-L252-evidence-resolve   rc=0 SUMMARY cases=8 pass=8 fail=0
no-L217-register-resolve   rc=0 SUMMARY cases=8 pass=8 fail=0
later-HEAD (994de3b)       rc=0 SUMMARY cases=8 pass=8 fail=0
```

Single-arm probes (`R40w2simplifier01-repro.out` §4–§5; fixture repo built by the lane's own `build_repo`, scratch only).

## 2. Candidate deletions in the landed counter

Line numbers are `census/round-40/c1-counter.py` @128e412. "Reconciler" is `tools/souji-citation-reconcile.py`
(same bytes at 128e412 and HEAD), which `register_leg` runs first (c1-counter.py:191-204) and whose `mismatches=` gates the
verdict (c1-counter.py:339).

| # | Where (landed) | Arm | Status | What deleting it changes (observed) | Recommendation |
|---|---|---|---|---|---|
| R1 | c1-counter.py:229-231 | `if not is_ancestor(root, commit, rev)` → `notancestor` | **Verdict-neutral duplicate** of reconciler `COMMIT-NOT-ANCESTOR` (reconciler.py:222-223, same `--rev`). Also untested by the r40 fixture (no case reaches it). | Probe S3 with the block removed: `ROW-SIDE` still fails: `REGISTER cells=1 mismatches=1 commit_rows=1 commit_hashes=1 violations=0 ok`, rc 1. Only the `violations=` count and the `REGISTER … NOT-ANCESTOR-OF-REV` line disappear. | Delete, or add a fixture case if the count is wanted. |
| R2 | c1-counter.py:217 `git_resolves(root, commit)` half | unresolvable-commit label | **Label-only duplicate** of reconciler `COMMIT-UNRESOLVED` (reconciler.py:217-218, gated at :295). | Probe S4 with the half removed: `REGISTER ROW-ZERO BACKWARDS commit-not-descendant 0000…`; rc 1; `mismatches=1` from the reconciler is unchanged. Only the label changes. | Delete the half (label cost only). |
| R3 | c1-counter.py:217 `REV.match(commit)` half | non-hex commit | **Unreachable today.** The reconciler refuses a non-40-hex commit before the counter loop (reconciler.py:165-166) → `register leg produced no SUMMARY` → rc 2. Observed in the repro §4 C path for `receipt_rev`; for `commit` the same guard (probe run earlier: `REFUSAL USAGE: register … line 2 commit is not 40-hex`, rc 2). | No change today. | Dead under the current reconciler; keep only as a guard if the reconciler stops refusing. Low value either way. |
| R4 | c1-counter.py:252-253 `git_resolves(root, evidence_rev)` | evidence-rev unresolved | **Label-only.** `merge-base --is-ancestor` on an unknown rev exits 128 (not 0), so L254 returns `EVIDENCE-NOT-ANCESTOR` for the same input. | Fixture 8/8 unchanged; L1 rc unchanged; the forged reason text changes from `EVIDENCE-REV-UNRESOLVED` to `EVIDENCE-NOT-ANCESTOR`. `census/round-40/records/c1-after-d.txt` (and SCORECARD C1 row, line 791) would then quote a stale reason. | Delete the branch only with the records updated; otherwise keep for the label. |
| R5 | c1-counter.py:258 `evidence_rev.lower()` | case fold of the 40-hex | **No-op.** `parse_items` enforces `REV = ^[0-9a-f]{40}$` (L55, L146), so `evidence_rev` is already lowercase. | None. `line.lower()` stays (it is the only case-folding that matters). | Delete `evidence_rev.lower()`. |
| R6 | c1-counter.py:297 `or os.environ.get("TMPDIR") or "/var/tmp"` | scratch fallback | **Redundant with the stdlib.** `tempfile.mkdtemp(dir=None)` already honours `TMPDIR` (checked: `tempfile.gettempdir()` returned the TMPDIR value). The literal `/var/tmp` is the hardcoded path the contract forbids in spirit (`avoid hardcoded /tmp`). Every L1 run passes `--scratch`. | None observable. | Replace with `dir=args.scratch`. |
| R7 | c1-counter.py:265-267 `isdir(root)` | usage refusal for a missing root | **Redundant exit path** [INFERENCE from the verified git rc 128 and the `run()` flow]: `git_resolves` on a missing `-C` directory fails, giving `REFUSAL COULD-NOT-EVALUATE` with exit 2. The observed landed output today is `REFUSAL USAGE: --root … is not a directory`, rc 2. | Exit code identical (2); the message changes. | Optional; keep for the clearer message. |
| R8 | c1-counter.py:58 `GIT_CONFIG_NOSYSTEM` | disable /etc/gitconfig | **Redundant with L60** `GIT_CONFIG_SYSTEM=/dev/null` (checked in §1 config probe: each alone disables the file; the pair is equivalent). | None. | Keep one of the two. |
| R9 | c1-counter.py:57, 61–63 `LC_ALL`, `GIT_ATTR_NOSYSTEM`, `GIT_OPTIONAL_LOCKS`, `GIT_TERMINAL_PROMPT` | locale / attributes / locks / prompt | [INFERENCE] inert for the read-only plumbing used (`show`, `cat-file -e`, `merge-base --is-ancestor`): the counter does not parse git's human text and runs no filter/checkout. Not probed. | Not measured. | Candidates only; delete one by one with the fixture. |
| R10 | c1-counter.py:136–137 duplicate-id guard; :130–131 header guard | input validation | Verdict-neutral (each row is evaluated independently; a duplicate only inflates `items=`). The header guard enforces the documented contract. | Probe I: `REFUSAL USAGE … duplicates id DUP`, rc 2. | Keep; `items=` counts are cited (SCORECARD C1 row). |

**Not deletable as-is (cited by a recorded receipt):** `commit_hashes=` (c1-counter.py:330-334, `distinct_hashes` L175)
is the must-token of `census/round-40/c1-items.tsv:4` (`R40-CLAIM-D3`, `commit_rows=,commit_hashes=`) and appears in the
SCORECARD C1 row (line 791). `forged_open=` (L330-334) is in the same SCORECARD row. Deleting either makes the recorded L1
receipt stop reproducing. `items_sha=`/`forged_sha=` (L293-294) are provenance and not gated: keep.

## 3. Arms that are NOT redundant (checked with a sole-arm probe)

The sole-arm probes (`R40w2simplifier01-repro.out` §4–§5; S1/S2) use an anchored line that **names the commit**, so the
reconciler's commit checks pass and only the counter's own arm can reject the row:

- **L221 `commit == receipt_rev` (c1-counter.py:221-224) is load-bearing.** S1 with the landed counter:
  `REGISTER ROW-EQ BACKWARDS commit-equals-receipt_rev 4ca7…`, `mismatches=0 … violations=1`, rc 1. With L221 removed:
  `mismatches=0 … violations=0`, rc 1 only because `commit_rows=0` trips `--min-commit-rows 1`. That is an accidental second
  guard, not a verdict-level one. The fixture case `register-equal-rejected` (fixture 177-182, assertion at 180) catches
  the removal: `case-register-equal-rejected=FAIL rc=1 violations=0`.
  Equal-by-object is caught only because `merge-base --is-ancestor X X` exits 0 (checked), so L221 is needed.
- **L225 `is_ancestor(receipt_rev, commit)` (c1-counter.py:225-228) is load-bearing.** S2 (`ROW-BK`, receipt c1, commit c0,
  anchor names c0): `commit-not-descendant`, `mismatches=0 … violations=1`, rc 1. Removing L225 is not run here; the
  strict-descendant relation is the only thing that rejects the row (the reconciler checks ancestry of `commit` vs `--rev`
  only, reconciler.py:219-223).
- **L146 evidence `REV` parse (c1-counter.py:146)** is load-bearing: `receipts/r0.txt@HEAD` → `REFUSAL USAGE … has no 40-hex revision`, rc 2 (probe P4), because
  `HEAD` and abbreviated revisions would otherwise resolve.
- **Abbreviated `receipt_rev` (string-equality hole at L221)** is NOT reachable: the reconciler refuses a non-40-hex
  `receipt_rev` (reconciler.py:163-164). Observed (`R40w2simplifier01-repro.out` §4 C): `REFUSAL USAGE: register reg-abbr.tsv
  line 2 receipt_rev is not 40-hex`, rc 2. The counter's L221 string compare is safe only because of that reconciler check.

## 4. Calibration findings (not YAGNI; for the attack seats)

- **F1 — the forged control gate can pass without the control.** c1-counter.py:335-342 gates on `forged_closed == 0` only.
  - No `--forged`: `ITEM BOUND-1 CLOSED … forged=0 forged_open=0 forged_closed=0`, rc 0 (repro §4 A).
  - Forged row with a misspelt file: `FORGED FORGE-TYPO OPEN FILE-ABSENT`, rc 0 (repro §4 B). An anchor typo likewise (J).
  The "forged token-only line stays OPEN" predicate passes without testing the token-only line.
- **F2 — landed bytes accept an uncited pointer path.** `PATH-UNCITED` item (`receipts/r1b.txt@c1`, a path that exists at
  c1, on a line that cites only `receipts/r0.txt` and `c1`) is `ITEM PATH-UNCITED CLOSED`, rc 0 (repro §4 D; c1-counter.py:258-259 checks only the revision on the line). **At 994de3b** the same item is `OPEN EVIDENCE-NOT-BOUND`, rc 1 (repro §5 `later-HEAD`; the HEAD diff at c1-counter.py:258-262 adds a backtick path check). So F2 is a landed-bytes falsifier that HEAD fixes.
- **F3 — reconciler detail is dropped.** `register_leg` captures the reconciler's stdout and parses only `SUMMARY` (c1-counter.py:199-209). `mismatches=1` is printed with no `MISMATCH …` line (R1/S3 output), so the L1 cannot say why it failed.
- **F4 — the r40 fixture never reaches most arms.** Fixture cases: bound/forged/clean/equal/backwards/r39 control (fixture 154-203). Deleting R1 or R2 still gives 8/8 (§1). Not reached: L186 REGISTER-ABSENT, L238 FILE-ABSENT, L241 ANCHOR-ABSENT, L248-250 PREDICATE-MISSING, `mustnot` (L139, L246), L256 EVIDENCE-PATH-ABSENT, L217 unresolved commit, L229 NOT-ANCESTOR-OF-REV, the refusal exits. (Probes N, H, S3, S4, P3, P5 exercise them by hand.)
- **F5 — the later HEAD fails its own measured command.** At `994de3b` the same L1 command exits 1: `ITEM R40-CLAIM-D3 OPEN EVIDENCE-NOT-BOUND census/round-40/c1-counter.py@8a5fbdb…` (repro §2 `later-HEAD`), because the anchored SCORECARD line does not cite the path in backticks. The SCORECARD C1 row (line 791) records rc 0 at 549d9ec. A re-measure is needed before that row is reused.
- **F6 — cross-version fixture.** Running the 994de3b fixture (9 cases) against the landed counter gives 2 FAILs (`forged-path-uncited-open`, `register-clean-accepted` with `rc=1 violations=0 mismatches=0`). That is the counter and fixture disagreeing across versions, not a landed-bytes result (observed, not re-measured after cleanup).

## 5. Later HEAD (context)

`994de3b round-40: bind evidence path as well as revision; add path-substitution control` changes only c1-counter.py:258-262 in
the counter, plus the fixture (+9 lines), SCORECARD, QUALITY and lesson. With the 994de3b counter the 9-case 994de3b fixture passes 9/9 (observed in a scratch run, not in the repro output); the 128e412 fixture passes 8/8 against it (repro §1). The L1 command fails on R40-CLAIM-D3 (F5). R1–R9 apply to the 994de3b counter unchanged, since the diff touches only the `evidence` check.

## 6. Scope, tools, scratch

- Installs: none. No pacman, no `uv`/`npm`/`cargo` installs. Tools used: system `git` 2.56.0 and `python3` 3.14 (both already present).
- Lane writes: none. Lane reads: `git show`, `git log`, `git rev-parse`, `git diff`, `git merge-base`, `git cat-file`, `cat`, and running the lane's own fixture from a scratch copy of its tree.
- Files written by this seat: `.ufo/waves/round-40/w2/R40w2simplifier01.md` (this report), `.ufo/waves/round-40/w2/R40w2simplifier01-repro.py` (self-contained reproduction), `.ufo/waves/round-40/w2/R40w2simplifier01-repro.out` (its output, quoted above). Everything else went under `/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier01/`.
- Scratch removal: `/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier01/` was removed with `rm -rf` and verified absent (`test ! -e`) before this report was finished. The repro script regenerates everything under an explicit `--work`.
- Lane working tree at the final check (not analysed here): `git diff --stat` showed uncommitted edits to `census/round-40/c1-counter.py` (26 changed lines: adds `EVIDENCE-DISAGREES` / `EVIDENCE-STALE` checks, `len(forged) > 0` and `forged_open == len(forged)` gates, and a committed-tree read for items), `tests/fixtures/r40-c1-evidence.py`, `SCORECARD.md` and `corpus/*`. Those edits are not mine and were not committed by this seat. They appear to answer F1 (forged-gate vacuity) and F2 (path binding); the new arms they add have not been reviewed by this seat. The verdicts above concern the committed landed bytes at 128e412 (identical to 549d9ec) and HEAD 994de3b only.
