# SwarmCritic12 — C1 item K14 falsification (SCORECARD.md:171)

STATUS: PASS — K14 AGREES at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; verdict HOLDS (deterministic, predicate faithful).
One out-of-set residual (stale `/var/tmp scratch` in the same cell) and one self-attestation observation are reported below.

## Evidence

### E1 — the cell (base 6017a482e7068d5afb7617640198fbb0fe743357, SCORECARD.md:171)

Capability cell, pipe-free verbatim fragments:
- `parse a self-assessment file at a named revision and re-derive its backticked-path, revision-token and sha256 assertions from committed bytes`
- `read-only, git plumbing only, /var/tmp scratch`
- `its fixtures reject the cheapest always-zero control`

Evidence cell, pipe-free verbatim fragment (the item's command and stated outcome):
- `` `python3 tools/souji-declared-evidence.py --selftest` 8/8; `census/round-22/attempt2/declared-evidence-before.tsv`; S109–S114 ``

Frozen item row (`census/round-33/c1-items.tsv:28`): `K14  171  0  \b8/8\b  tools/souji-declared-evidence.py  python3 tools/souji-declared-evidence.py --selftest`

### E2 — determinism (own scratch clone, cwd = clone root)

```
git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r33/AuditK14/c
git -C .../c remote remove origin ; git -C .../c checkout 2d9bca55a9f042a2c9ed60a797a8069e74c41f46
git -C .../c rev-parse --show-toplevel -> /fast/scratch/hyaku/souji-r33/AuditK14/c
```
run1 TMPDIR=$D/tmp/r1 (fresh)  rc=0  last line: `selftest=8/8`
run2 TMPDIR=$D/tmp/r2 (fresh)  rc=0  last line: `selftest=8/8`
run3 `env -u TMPDIR` (inherited/absent)  rc=0  last line: `selftest=8/8`
run4/run5 = the frozen argv exactly, no `-B`, fresh TMPDIR each  rc=0  `selftest=8/8`; `diff run4 run5` -> IDENTICAL.
All five runs printed the same 8 PASS lines then `selftest=8/8`. `git -C .../c status --porcelain` after the runs: empty (read-only in the clone).

### E3 — counter (both runs, stable)

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/AuditK14/cnt --only K14
```
```
ITEM	K14	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest=8/8
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```
Second run with `--scratch .../cnt2`: byte-identical two lines, rc=0. (`partial=1` is the `--only` marker, c1-counter.py:307.)

### E4 — predicate strength (mutants against the frozen argv, scratch clone working tree only; restored with `cmp` identical after each)

- M1 — hollow one fixture expectation (`fixture2 ... rc == 1 and "mismatches=1" in line` -> `True`): rc=0, `selftest=8/8`. The row's stated outcome is still printed.
- M2 — real regression of the audited logic (class `A` forced to `resolved` in `evaluate()`): rc=1, `FAIL fixture2 absent path -> mismatch`, `FAIL fixture5 path only at other rev -> mismatch`, `selftest=6/8`.
- M3 — delete one `checks.append` (fixture7), all remaining pass: rc=0, `selftest=7/7`.
Count logic (`tools/souji-declared-evidence.py:313-316` at the measured rev): `ok = sum(1 for _, good, _ in checks if good)`; `selftest=%d/%d` with `len(checks)`; `return 0 if ok == len(checks) else 1`.

### E5 — residual re-derivation (`/var/tmp scratch`)

- At base, `tools/souji-declared-evidence.py:266`: `base = tempfile.mkdtemp(prefix="souji-declared-evidence-")` with `:265` comment `no dir= : the fixture tree lives under the caller's TMPDIR, never a literal /var/tmp`.
- Parent of 98e5203: `base = tempfile.mkdtemp(prefix="souji-declared-evidence-", dir="/var/tmp")`.
- `git log -S "never a literal /var/tmp"` -> `98e5203d45b4e419a9e72801733d93303acc7ebd round-32: C2 scratch discipline — 26 tools and fixtures take scratch from TMPDIR ...`; `git merge-base --is-ancestor 98e5203 2d9bca5` -> YES; blame at 2d9bca5 puts :265-266 on 98e5203.
- Other cell artifacts are live: `census/round-22/attempt2/declared-evidence-before.tsv` exists at base and at list-rev; S109–S114 are committed SOURCES rows (`corpus/SOURCES.md:130-135` at base).

## Findings

1. **K14 HOLDS — deterministic.** Five runs (three TMPDIR variants, two exact frozen-argv runs) give rc=0 and `selftest=8/8` at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; the counter prints `K14 AGREE` in two runs. No nondeterminism observed. Location: SCORECARD.md:171; census/round-33/c1-items.tsv:28.
2. **The frozen predicate `\b8/8\b` + exit 0 is a faithful reading of the evidence cell for THIS command, and not lax on genuine regressions.** The row states exactly the selftest's own count line; `8/8` is printed only when all eight fixture expectations hold (M2 -> 6/8, rc 1), and the denominator is bound too (M3 -> 7/7, no `8/8`). Not stricter either: no `8/8` string occurs in any per-fixture line, so the conjunct cannot be satisfied spuriously, and the code ties the count to the exit code. Location: tools/souji-declared-evidence.py:313-316; c1-items.tsv:28.
3. **RESIDUAL (out-of-set, stale cell text): `read-only, git plumbing only, /var/tmp scratch`.** The tool's only scratch is the selftest's, and since 98e5203d45b4e419a9e72801733d93303acc7ebd (r32 C2 scratch discipline, ancestor of base) it follows the caller's TMPDIR with no `dir=`, defaulting to Python's tempdir, not `/var/tmp`. The row's own file was the cause; the claim was true before 98e5203 and is false at base and at list-rev. It is outside the C1 enumeration rule (no backticked command with a stated outcome), so it is not a K14 mismatch and needs no restatement row — it is a SCORECARD text residual. Location: SCORECARD.md:171 capability cell; tools/souji-declared-evidence.py:265-266.
4. **OBSERVATION (self-attesting evidence, not a predicate defect).** The row's evidence is a selftest count, so a tool whose selftest was hollowed while its audit logic survived still prints `8/8` (M1: rc=0, `selftest=8/8`). Any faithful predicate over `--selftest` has this property; the frozen predicate cannot be tightened without going stricter than the row. Consequence for C1: `mismatches=0` at the tip is not evidence that the declared-evidence capability itself still works — only that its selftest still reports eight of eight. `[INFERENCE]` this is a row-quality issue, not a C1 rule defect.

## Attack log

- Tried: repeated/inherited-TMPDIR runs, exact frozen argv without `-B`, TMPDIR unset — no drift.
- Tried: value-drift mutant of the audited logic (class A forced resolved) — predicate catches it (6/8).
- Tried: check-count removal — predicate catches it (7/7); denominator is bound.
- Tried: fixture-hollowing mutant — predicate does not catch it (8/8), but the cell's stated outcome is unchanged, so this is a gaming vector against the row's evidence quality, not a predicate mismatch. Reported as Finding 4.
- Tried: other cell artifacts (tsv, S109–S114) — live, not stale; only `/var/tmp scratch` is stale (Finding 3).
- Verdict: **HOLDS**. No LAX-PREDICATE, no STRICT-PREDICATE, no NONDETERMINISTIC finding.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic12.md` (this report).

Scratch `/fast/scratch/hyaku/souji-r33/AuditK14` removed after these receipts were copied; no tool installs were needed.
