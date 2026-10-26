# SwarmCritic08 — falsify C1 item K08 (SCORECARD.md:161)

## Status

STATUS: PASS — K08 reproduces deterministically at the measured revision (3/3 runs rc=0, `SUMMARY total=35 failed=0 skipped=2`) and the counter prints AGREE; the predicate matches the cell exactly and rejects both controls I built. Verdict **HOLDS**. Four residuals reported, none reachable from committed bytes at the measured revision: one fixture defect that makes the row host-conditional (jj absent), one out-of-set stale-by-revision parenthetical, and two reproduced predicate escape hatches.

## Evidence

All commands run from the scratch clone `/fast/scratch/hyaku/souji-r33/AuditK08/c` (rev `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`), created with `git clone -q --no-local <lane> "$D/c" && git -C "$D/c" remote remove origin`; `git -C "$D/c" rev-parse --show-toplevel` printed `/fast/scratch/hyaku/souji-r33/AuditK08/c`; `git -C "$D/c" status --porcelain | wc -l` = `0`.

Cell under test, SCORECARD.md:161 at base `6017a482e7068d5afb7617640198fbb0fe743357` (quoted verbatim, 15 words):
> `` `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` 35/0 (5fa6017 tools: 13 fail) ``

Its meaning is fixed by the measured tool's own documented output format, `tests/fixtures/r17-jj-receipts.sh:63` (verbatim):
> `and SUMMARY<TAB>total=PASS+FAIL<TAB>failed=N<TAB>skipped=N. Exit 0 when no`

so `35/0` = total 35, failed 0, i.e. conjuncts `total=35` and `failed=0`.

### 1. Determinism — three runs of the frozen argv

`TMPDIR="$D/t1" bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` (cwd = clone root), run 1; run 2 with `TMPDIR="$D/t2"`; run 3 with `TMPDIR` unset:

| run | rc | SUMMARY | CASE lines | SKIP |
|---|---|---|---|---|
| 1 | 0 | `SUMMARY	total=35	failed=0	skipped=2` | 37 | J6-verify, J6-vault |
| 2 | 0 | `SUMMARY	total=35	failed=0	skipped=2` | 37 | same |
| 3 | 0 | `SUMMARY	total=35	failed=0	skipped=2` | 37 | same |

`awk -F'\t' '$1=="CASE"{print $2, $3}'` columns are identical across all three (`diff v1 v2`, `diff v1 v3` empty). Full-output diffs show only synthesized commit ids in detail fields (`SCENARIO seed tip=af3be1fc37a7` vs `tip=cbee3c2cb9b4` vs `tip=a4f8e0f9333d`), i.e. the fixture's own commit timestamps — no verdict moves. stderr was 0 bytes in all three.

### 2. Predicate match at base

Whitespace-collapsed stdout+stderr (the counter's `flat`), per run: `\btotal=35\b` 1 occurrence, `\bfailed=0\b` 1 occurrence, `\b35/35\b` **0** occurrences. No `N/M` shape occurs anywhere in the output (`grep -oE '[0-9]+/[0-9]+'` empty), so the disjunction's second alternative is inert.

### 3. Counter

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/AuditK08/cnt --only K08
ITEM	K08	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=35 failed=0 skipped=2
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
exit=0
```

### 4. Controls I built (would a regressed input still pass?)

- Regressed tool arm: `tools/` copied to scratch, `souji-verify.sh` given a two-line always-`verdict=SAFE` prologue → `SUMMARY total=35 failed=20 skipped=2`, rc=1; collapsed text has `total=35` **present**, `failed=0` **absent**, `35/35` **absent** → predicate FALSE.
- Skip-inflation arm: tool dir holding only `souji-verify.sh` + `souji-quarantine.sh` → `SUMMARY total=23 failed=0 skipped=14`, **rc=0**; `total=35` absent → predicate FALSE. Exit code alone does not carry the claim; the total conjunct does.

### 5. Second stated outcome in the same cell — `(5fa6017 tools: 13 fail)`

Provenance: `git show 5fa6017:tools/souji-verify.sh | sha256sum` = `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd`, identical to the `TOOL` line of `census/round-17/jj-receipts-base5fa6017.txt` (same for `souji-vault-verify.sh` `f9e778ca…`, `souji-quarantine.sh` `df407511…`). Re-executed both ways:

| fixture bytes | tool dir | SUMMARY |
|---|---|---|
| `4f48343:tests/fixtures/r17-jj-receipts.sh` (35 case ids) | tools at `5fa6017` | `total=33 failed=13 skipped=2`, rc=1 |
| current fixture (37 case ids) | tools at `5fa6017` | `total=35 failed=15 skipped=2`, rc=1 |

The committed record states `SUMMARY	total=33	failed=13	skipped=2` — an exact match for the round-17 fixture, not for current bytes.

### 6. Environment: jj absent

Same argv, `env HOME=/fast/scratch/.../AuditK08/fakehome PATH=/usr/local/bin:/usr/bin:/bin` (real jj exists only at `/home/vgpnk/.local/bin/jj`):

```
JJ	none	none
CASE	J9-file	SKIP	jj absent (optional real-jj arm)
CASE	J9-worktree	SKIP	jj absent (optional real-jj arm)
CASE	J13	FAIL	cannot create jj-colocated kama-shokunin fixture
CASE	J13-own	FAIL	cannot create jj-colocated souji-shokunin fixture
SUMMARY	total=33	failed=2	skipped=4      (rc=1; total=35 ABSENT -> predicate FALSE)
```

Control with the same HOME and jj on `PATH`: `JJ	/home/vgpnk/.local/bin/jj	jj 0.45.1-…` → `total=35 failed=0 skipped=2`, rc=0. So the 2 failures are jj-absence, not the sandbox. `bash -x` trace at the failure (`tests/fixtures/r17-jj-receipts.sh:317`): `+317: '[' -z '?? .jj/' ']'`.

## Findings

1. **The claim holds at the measured bytes.** 3/3 identical verdict columns, exact `SUMMARY` match, counter AGREE, and the predicate is bound to the tool's documented format, not to an incidental string. Location: `tests/fixtures/r17-jj-receipts.sh:63`, run at `2d9bca55…`.
2. **The predicate is faithful, not lax, for the tool surface.** With `total=PASS+FAIL`, `total=35 && failed=0` also implies the 2 SKIPs did not grow: my no-vault arm shows a silently degraded case set keeps rc=0 but drops `total` to 23. Location: `census/round-33/c1-items.tsv` K08 row.
3. **Fixture defect (measured body, outside the predicate but inside the item's `files`): J13/J13-own are not jj-optional.** The fixture's stated contract is `real jj is used only by J9.` (`tests/fixtures/r17-jj-receipts.sh:46`), yet the emulated branch writes `.jj/repo/config.toml` without excluding it, so the post-build guard at `:316-317` sees `?? .jj/`, `recipe_build_repo` returns 1, and `case_j13_recipe` calls `fail_case` (`:770`, `:775`) instead of `skip_case`. Result: on a host without jj 0.45.1 the row's `35/0` reads `total=33 failed=2`. The counter is unaffected only because it inherits this host's `PATH`.
4. **Out-of-set residual — `(5fa6017 tools: 13 fail)` is fixture-revision-pinned.** It re-derives exactly (`total=33 failed=13`) only with the round-17 fixture bytes; with the fixture at `2d9bca55…` and the same 5fa6017 tools it is 15. The cell names the tool revision but not the fixture revision, so a literal reader executing the parenthetical gets 15, not 13. Correctly outside the frozen rule (it is not an outcome of the frozen argv), but stale as written. Location: `SCORECARD.md:161`.
5. **Record pointer resolves, both records differ.** `census/round-17/jj-receipts-*.txt` = `jj-receipts-4f48343.txt` (`total=35 failed=0 skipped=0`, baseline arm) and `jj-receipts-base5fa6017.txt` (`total=33 failed=13 skipped=2`). The `35/0` half of the cell is evidenced only by the first, and only with `--baseline-dir` (skipped=0), which the frozen argv does not pass.
6. **Detail fields are not reproducible, verdicts are.** `SCENARIO`/`CASE … head=` ids change every run (synthesized commits). Harmless for this cell (a count), but a restatement that quotes a detail line with a commit id in it would be non-reproducible.

## Attack log

**A1 — dead alternative `\b35/35\b` is a gameable surface.** The fixture can never print a fraction (0 `N/M` occurrences in 3 runs), so the alternative adds no discrimination at base; but the counter applies it as an OR alternative (`c1-counter.py:131-143`, `ok = ok and bool(re.search(part, flat))`). Reproduced: a scratch copy of the fixture with one injected line before the summary, run against the always-SAFE tool dir, gives

```
CASES	35/35 all cases passed
SUMMARY	total=35	failed=20	skipped=2
```
collapsed text then has `35/35` present and `failed=0` absent → the K08 predicate evaluates TRUE for a revision whose fixture reports 20 failures. Impacted axis: calibration (C1), predicate fidelity. Smallest safe correction (L1-only, stricter-only): for this item the predicate should be the conjunction alone, `\btotal=35\b && \bfailed=0\b` — the cell's `35/0` is total/failed, never pass/total.

**A2 — cross-line conjunction.** `flat = collapse(out + "\n" + err)` (`c1-counter.py:132`) joins all output before matching, so the two conjuncts need not come from the same line. Reproduced: a scratch fixture copy printing `NOTE	all guards ok failed=0` before a real `SUMMARY	total=35	failed=20	skipped=2` satisfies both conjuncts. A stale or invariant echo line containing `failed=0` is enough. Impacted axis: calibration. Smallest safe correction: none available without amending the frozen predicate (per-item line anchoring); reported, not proposed — this hazard is shared by every multi-conjunct item in `c1-items.tsv`.

**A3 — host-conditional outcome (fixture, not predicate).** With jj absent the honest command yields `failed=2` and the row's stated `35/0` does not reproduce; the fixture's own docstring promises the jj-free path. This defeats the preregistration's Q70b stability reading (three base runs were on one host, `feasibility.txt`) as evidence of portability. Impacted axis: calibration currency of this row; measured surface integrity. Smallest safe correction: exclude `.jj/` in the emulated branch (or `skip_case` J13/J13-own when `RECIPE_JJ_MODE=emulated`) — a fixture repair, outside C1's surface and not by this seat.

Verdict: **HOLDS** — deterministic at `2d9bca55…`, predicate equal to the cell's stated outcome, both cheaper controls rejected; A1/A2 are unreachable from committed bytes at base, A3 is a defect in the measured fixture on a jj-less host, and Finding 4 is a wording gap in the row, not a false count.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic08.md` (this report).

Notes: no tool installed or upgraded (nothing needed). Scratch `/fast/scratch/hyaku/souji-r33/AuditK08` removed after collecting the receipts above; `ls -d /var/tmp/r17-jj-receipts.*` returned 0 entries (the fixture's own EXIT trap cleans it). No lane file, git/jj state, or path outside `souji-shokunin/.ufo/waves/round-33/w1/` was written.
