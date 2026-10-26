# SwarmCritic24 — C1 item K26 falsifier (SCORECARD.md:489)

## Status
STATUS: PASS — verdict **HOLDS**: at 2d9bca5 the frozen argv prints `lines=17 bad=4` and exits 1 in five runs (three fresh `TMPDIR`, two `TMPDIR` unset), the frozen predicate is a faithful and effectively exact reading of the row's cell, the cell's other stated outcomes are current, and the counter prints `agree=1 mismatches=0` at both the freeze and the tip. Three out-of-set residuals reported (one latent frozen-mechanism attack, two coverage gaps); none moves C1's target.

## Evidence

Measured revision: `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Clone `/fast/scratch/hyaku/souji-r33/AuditK26/c` (`git clone --no-local`, origin removed, `rev-parse --show-toplevel` = the clone). Two extra scratch repos `m5repo` (mutant) and `attrepo` (probe), same construction. All runs `python3 -B`, cwd = clone root.

Row read at base (`git show 6017a48:SCORECARD.md | sed -n 489p`), evidence cell verbatim:

`python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt --contract census/round-32/m1-r31-contract.txt` -> `lines=17 bad=4`, exit 1 (`census/round-32/records/m1-red-before.txt`)

Item row: `census/round-33/c1-items.tsv:40` — `K26  489  1  lines=17 bad=4  tools/souji-record-contract.py  python3 -B tools/souji-record-contract.py --record …`.

**(1) Determinism — 5 runs, identical bytes, no writes.**

```
run1 TMPDIR=<fresh tmp1>  rc=1  run2 TMPDIR=<fresh tmp2>  rc=1
run5 LC_ALL=C TMPDIR=<fresh tmp5>  rc=1
run3 env -u TMPDIR  rc=1   run4 env -u TMPDIR  rc=1
stdout (all five):
BAD 16 arm=reflog-only outside descendant|solo
BAD 17 arm=reflog-only outside descendant|solo
BAD 18 arm=reflog-only outside descendant|solo
BAD 19 arm=reflog-only outside descendant|solo
lines=17 bad=4
stderr: empty.   git status --porcelain after the runs: empty.   ls -A tmp1 tmp2 tmp5: empty.
```
Last digit-bearing line, all runs: `lines=17 bad=4`. Deterministic.

**(2) Predicate fidelity.** The cell states one command and one outcome pair: `lines=17 bad=4`, exit 1. The frozen item states exit `1` and predicate `lines=17 bad=4`; `frozen_pred` (`census/round-33/c1-counter.py:130-146`) applies it as `re.search` over collapsed stdout+stderr, and `judge` (`:240-252`) conjoins `rc == 1`. That is the cell, no more and no less.

Not stricter: every element of the cell is carried; nothing extra is demanded (no BAD-line text, no ordering, no receipt compare).

Not laxer, in reachable output space: `lines=` is printed once, at column 0 (`tools/souji-record-contract.py:77`), and `check()` (`:41-59`) appends at most one entry per record line, so `bad <= lines`; with `lines` pinned to 17 by the same literal, the two-digit `bad` values `4` could prefix-match (`40`-`49`) are unreachable, and the literal `lines=17 ` blocks `lines=170`. Probe: pattern matches `lines=17 bad=40` and `xlines=17 bad=4`, rejects `lines=170 bad=4`; the first two shapes cannot be emitted by the tool as it stands. Effectively exact for this item.

**(3) Other stated outcomes in the same cell (outside the rule) — all current, none stale.**

- "fails the r31 record's `arm=reflog-only` lines": `grep -c 'arm=reflog-only' census/round-31/records/jj-object-clock-run.txt` = `4` (record lines 16-19); the tool flags exactly lines 16, 17, 18, 19 and nothing else. All and only — holds.
- "Literal-prefix: a mixed record with a `RESULT:` line passes (a2w1 `SwarmCritic26.md`)": reproduced on a crafted record (one conforming `RESULT` line + one `RESULT:` line with `arm=reflog-only`) → `lines=1 bad=0`, rc 0. The disclosed weakness is still present, so the cell is not overstating it.
- Evidence pointer `census/round-32/records/m1-red-before.txt` (blob `aac7f6b4266821dd31ab17ca3f166178ede714e6` at base, freeze and tip) contains the same four BAD lines, `lines=17 bad=4` and `exit=1`. Not stale.
- `lines=17` re-derived: record has 19 lines, 2 header lines (`jj-version`, `git-version`), 17 `^RESULT ` lines.

**(4) Counter.**

```
$ python3 -B …/census/round-33/c1-counter.py --root …/souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/AuditK26/cnt --only K26
ITEM	K26	AGREE	original	rc=1 expect_exit=1 predicate holds last=lines=17 bad=4
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter_rc=0
```
Tip reading (blobs unchanged, `git diff --stat 2d9bca5..fef88f2` touches only `census/round-33/records/*`):
```
ITEM	K26	AGREE	original	rc=1 expect_exit=1 predicate holds last=lines=17 bad=4
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=fef88f2159f6380a4d1360f73365b3d595973a37
counter_rc=0
```
Blob identity for every K26 input at base / freeze / tip: `tools/souji-record-contract.py` `f01b652b…`, record `63502d12…`, contract `cab08ec9…`, red-before `aac7f6b4…`. No drift, so no restatement is due and `restated=0` is correct.

## Findings

1. **HOLDS — no defect in the item.** Location `census/round-33/c1-items.tsv:40` + `SCORECARD.md:489`. Deterministic, faithful, reproducible at freeze and tip.

2. **RESIDUAL (coverage; prose broader than stated outcome).** The row's prose asserts three checks — prefix, "exact keys in order", enumerated values — but the row states an outcome for one record whose only failures are value-membership failures. Consequence: a tool that has lost the other two checks still satisfies K26. Reproduced on mutants built from the frozen blob, each run against the K26 record with the frozen contract:
   - M1 (`keys in order` comparison deleted, `mut/m1-noorder.py`): `lines=17 bad=4`, rc 1 — passes. The lost check is real: on `RESULT arm=solo step=abandon reflog_hits=8 target_keep=yes keep_refs=1 object_present=yes` pristine prints `BAD 1 keys […] != […]`, rc 1; M1 prints `lines=1 bad=0`, rc 0.
   - M2 (only `arm` value checked, `mut/m2-armonly.py`): `lines=17 bad=4`, rc 1 — passes. On `target_keep=maybe` pristine prints `BAD 1 target_keep=maybe outside no|yes`, rc 1; M2 prints `lines=1 bad=0`, rc 0.
   - M5 (tool can no longer pass any record — `return 1` on the conforming branch, committed in `m5repo` as `be41551e2016693137b29c2f15ce9dd16724df19`): the row's own output is unchanged (`lines=17 bad=4`, rc 1) and the *green* arm inverts — r32 record `lines=22 bad=0` goes rc 1 (pristine rc 0). Counter at that rev: `ITEM K26 AGREE … mismatches=0`, `counter_rc=0`.
   Impacted axis: coverage, not calibration — the frozen enumeration makes one item per (command, stated outcome) pair and this tool has no other item (`grep -n souji-record-contract census/round-33/c1-items.tsv` → only line 40). C1's target is untouched. Smallest safe correction: no change to K26; a later round's enumeration can add the row's green arm (`census/round-32/records/jj-mtime-clock-run.txt` × `census/round-32/c3-contract.txt`, `lines=22 bad=0`, rc 0) as its own item — stricter-only, next round, L1's call.

3. **ATTACK (reproduced, latent; frozen mechanism).** A restatement's cause must be an ancestor of `--list-rev` (`c1-counter.py` docstring, `judge` `:214-216`), so a drift that first appears *after* the freeze is unrecoverable. Reproduced in `attrepo`: commit `ac2872f41ddc7d249811b1e91710a218fc4fd099` edits only `census/round-32/m1-r31-contract.txt` (`arm: solo|descendant` → `… |reflog-only`; tool and record untouched), which moves the row to `lines=17 bad=0`, rc 0; a correct value-drift restatement on top (commit `83e644e4…`) yields
   `ITEM K26 MISMATCH restated BAD-ROW(cause not an ancestor of the list revision)` / `mismatches=1`, `counter_rc=1`.
   Second, narrower edge on the same mechanism: the value-drift branch also requires the cause to name one of the item's `files` (`:222-225`), and K26's `files` cell (`c1-items.tsv:40`) names only `tools/souji-record-contract.py`, while the stated outcome is a function of two further committed files; a record- or contract-caused drift would therefore be `BAD-ROW(cause touches none of the item files)` — the r31 L29 unbindability class. [INFERENCE] from the code path; not reproducible without rewriting pre-freeze history.
   Neither is live this round: C2's declared file set (`tools/souji-census.sh`, `tools/souji-evidence-cache.py`, `tools/souji-round9-selftest.sh`, `tools/souji-verify.sh`, `tests/fixtures/r15-census-config.py`, `tests/fixtures/r15-preservation-frozen/regenerate.py`, per preregistration `== C2`) does not intersect the K26 command's three files, and those blobs are identical at base, freeze and tip. Smallest safe correction: none now; if the L1 wants the hazard closed, the stricter-only route is for a later round to widen `files` (or to admit post-freeze causes), never to relax anything here.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic24.md` (this report).

Scratch removed: `/fast/scratch/hyaku/souji-r33/AuditK26` (clones `c`, `m5repo`, `attrepo`; mutant copies; `cnt`, `cnt2`, `cnt3`, `cnt4`). Nothing outside it written; no `pacman`; no tool installs.
