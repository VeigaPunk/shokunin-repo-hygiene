# SwarmExecutor13 — r32 w1, C2 items T16 T19 T24 (receipt tool + fixtures honour the caller's scratch root)

## Status
STATUS: PASS — `tools/souji-receipt-run.py` and `tests/fixtures/{r23-receipt-run,r24-receipt-verify,r25-receipt-stderr}.py` now root scratch at the caller's TMPDIR (else `/var/tmp`) instead of a literal `/var/tmp`; the C2 counter reads `fail=0` for T16/T19/T24 at patched rev `bedde7ab7308b638c3bedc3c3f38bc6884d1ad84` and `fail=3` at the unpatched rev `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; every run's exit code and digit-bearing last line is identical to base, with TMPDIR set and with TMPDIR unset.

## Evidence

### 1. Counter, patched rev (4 files changed, committed in a scratch clone)
```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py \
  --root /fast/scratch/hyaku/souji-r32/C2Receipt/c \
  --rev bedde7ab7308b638c3bedc3c3f38bc6884d1ad84 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only T16,T19,T24 --scratch /fast/scratch/hyaku/souji-r32/C2Receipt/cnt
```
```
ITEM	T16	PASS	base=rc0:W486:selftest=8/8	sbox=rc0:W488:selftest=8/8
ITEM	T19	PASS	base=rc0:W154:cases=8 pass=8 refusals=2/2 regress=5/5	sbox=rc0:W156:cases=8 pass=8 refusals=2/2 regress=5/5
ITEM	T24	PASS	base=rc0:W3:cases=1 pass=1	sbox=rc0:W4:cases=1 pass=1
SUMMARY items=3 pass=3 fail=0 partial=1 rev=bedde7ab7308b638c3bedc3c3f38bc6884d1ad84
```
Exit 0. `(b)` creation counts hold: 488 vs 486, 156 vs 154, 4 vs 3.

### 2. Control — same counter against the unpatched rev (red-before)
```
--rev 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 --only T16,T19,T24 (all other args identical)
```
```
ITEM	T16	FAIL	base=rc0:W482:selftest=8/8	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
ITEM	T19	FAIL	base=rc0:W155:cases=8 pass=8 refusals=2/2 regress=5/5	sbox=rc1:W0:cases=8 pass=0 refusals=0/2 regress=0/5	regress work-dropped
ITEM	T24	FAIL	base=rc0:W3:cases=1 pass=1	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
SUMMARY items=3 pass=0 fail=3 partial=1 rev=7a6667cd27652baf8d704b5cdb8e3200bd6e27a1
```
Exit 1. The unpatched fixtures hit `EROFS` on the read-only `/var/tmp`; the patched ones do not. The frozen predicate is `census/round-32/c2-counter.py:21`: "SBOX's W is at least half of BASE's W (a tool that stops doing its work to dodge the sandbox fails)." Target quoted from `census/round-32/c2-counter.py:24`: "Frozen target (preregistration): `fail=0` over the enumerated set at the C2 landing commit and at the tip."

### 3. Each patched command, TMPDIR set and TMPDIR unset (rc, last digit-bearing line)
Run from the scratch clone root; TMPDIR set to `/fast/scratch/hyaku/souji-r32/C2Receipt/work/tmp`; "unset" is `env -u TMPDIR`.

| item | argv | base, TMPDIR set | patched, TMPDIR set | base, TMPDIR unset | patched, TMPDIR unset |
|---|---|---|---|---|---|
| T16 | `python3 -B tests/fixtures/r23-receipt-run.py` | rc0 `selftest=8/8` | rc0 `selftest=8/8` | rc0 `selftest=8/8` | rc0 `selftest=8/8` |
| T19 | `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-root .` | rc0 `cases=8 pass=8 refusals=2/2 regress=5/5` | rc0 `cases=8 pass=8 refusals=2/2 regress=5/5` | rc0 `cases=8 pass=8 refusals=2/2 regress=5/5` | rc0 `cases=8 pass=8 refusals=2/2 regress=5/5` |
| T24 | `python3 -B tests/fixtures/r25-receipt-stderr.py --rev 85b61a151923986e7e6b48f7084b9122561b5f3d` | rc0 `cases=1 pass=1` | rc0 `cases=1 pass=1` | rc0 `cases=1 pass=1` | rc0 `cases=1 pass=1` |

Every cell identical: base and patched print the same last line at the same exit code, both with TMPDIR set (patched writes under TMPDIR; base wrote under `/var/tmp`) and with TMPDIR unset (both take the `/var/tmp` fallback). Leftovers after the patched runs: `TMPDIR` is empty; the `/var/tmp` listing taken immediately before and after the three runs differs only by another seat's concurrent `souji-census-now.<suffix>` churn, and the subset matching this seat's fixture prefixes (`souji-r23-`, `souji-r24-`, `souji-r25-`, `souji-receipt-`; 38 pre-existing entries) compares byte-identical (`cmp` of the sorted subsets).

### 4. The `--out` policy, probed at `--rev bedde7ab…`
`run` with tool `tools/souji-rev-pin.py`, command `python3 -B tools/souji-rev-pin.py --selftest`:

| probe | TMPDIR | `--out` | result |
|---|---|---|---|
| P1 | set | `$TMPDIR/probe/receipt.txt` | rc0, receipt written (641 bytes) |
| P2 | set | `/var/tmp/r32-c2-probe.receipt` | rc2 `OUT-OUTSIDE-SCRATCH  receipts are written under the caller's scratch root (/fast/scratch/hyaku/souji-r32/C2Receipt/work/tmp) ...`, no file |
| P3 | set | `/tmp/r32-c2-probe.receipt` | rc2 `OUT-UNDER-TMP  receipts go outside /tmp (Q4)`, no file |
| P4 | `$C` (repo root) | `$C/r32-probe.receipt` | rc2 `OUT-IN-REPO`, no file |
| P5 | unset | `/var/tmp/r32-c2-unset-probe.receipt` | rc0, receipt written (fallback root) |
| P6 | unset | `/fast/scratch/hyaku/souji-r32/C2Receipt/tmp/x.receipt` | rc2 `OUT-OUTSIDE-SCRATCH ... (/var/tmp)`, no file |

Probe files were removed; nothing was left under `/tmp` or `/var/tmp` by this seat.

### 5. Revision and byte facts
- lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`, preregistration `3ec84fc81b3243429c834a051880b0bcde06291c`, controls `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; the four target files are byte-identical between base and controls (`git diff --stat` empty).
- patched rev `bedde7ab7308b638c3bedc3c3f38bc6884d1ad84` (scratch clone `git clone --no-local`, `origin` removed, `rev-parse --show-toplevel` = the clone): `4 files changed, 31 insertions(+), 15 deletions(-)`; `git status --porcelain` empty after the commit.
- delivered bytes: `deliver-souji-receipt-run.py` sha256 `3e4442b9…29080`, `deliver-r23-receipt-run.py` `d569bff7…43034`, `deliver-r24-receipt-verify.py` `c4a976aa…e47b`, `deliver-r25-receipt-stderr.py` `dfb9586c…3b050`, `deliver-C2Receipt.diff` `ee6a15e8…4b731`.
- syntax check of all four files passed (`compile(source)`, no bytecode written); lane Python run with `-B`.
- `git apply --check -v deliver-C2Receipt.diff` against a fresh `--no-local` clone checked out at base `85b61a151923986e7e6b48f7084b9122561b5f3d` prints all four `Checking patch …` lines clean: the diff is `a/`…`b/` prefixed and applies with `-p1`.
- no tool install or upgrade was needed; no pacman transaction, no host service touched.

## Findings

1. **The policy, exactly.** `run` now accepts `--out` only (i) not under `/tmp` (unchanged `OUT-UNDER-TMP`, Q4 — absolute, even if TMPDIR itself points into `/tmp`), (ii) under the scratch root, defined as `TMPDIR` when it is set (absolute, via `tempfile.gettempdir()`) and `/var/tmp` when it is not, (iii) not inside `--root` (unchanged `OUT-IN-REPO`); the `OUT-PROTECTED` and `OUT-SIBLING-LANE` guards and their order are unchanged. The refusal for (ii) is renamed `OUT-OUTSIDE-VAR-TMP` → `OUT-OUTSIDE-SCRATCH` because the root is no longer a literal directory; the message names the resolved root. Location: `tools/souji-receipt-run.py:189-195` (patched: `/tmp` guard at 190, scratch-root guard at 192-195, `OUT-IN-REPO` at 196-197), docstring restated at `:29-31` and `:46-47`. The same root governs the private measured clone: `tempfile.mkdtemp(prefix="souji-receipt-", dir=scratch_root())` at `:221` (was `:211`, `dir=SCRATCH_ROOT`).
2. **One resolution rule, one helper, four files.** `tools/souji-receipt-run.py:70-72` defines `scratch_root()`; the three fixtures carry the identical expression as their scratch parent: `tests/fixtures/r23-receipt-run.py:50` (`SCRATCH_PARENT`), `r24-receipt-verify.py:47` (`SCRATCH_PARENT`), `r25-receipt-stderr.py:20` (`SCRATCH`). Agreement is load-bearing, not cosmetic: r23 case 1 (plus its `--fail 3` rc-probe), cases 7 and 8, and r24 case c hand the runner `--out` under `SCRATCH_PARENT`, so a fixture root the runner would refuse fails the item — the `/var/tmp` fallback keeps the TMPDIR-unset path byte-identical to base instead of drifting to `/tmp` (where `/tmp` is refused), which is why the fallback is `/var/tmp` and not `tempfile.gettempdir()`'s own `/tmp` default.
3. **No other behaviour moved.** `FORBIDDEN_OUT_PARENT = "/tmp"` (case 6's subject) is untouched; no case text, argv, exit code, header field or output line changed apart from the docstrings that described the old literal root (`r23:4-7`, `r24:22-24`, `r25` has no such sentence). Child environments already inherit the caller's `TMPDIR` unchanged (`r23-receipt-run.py:117` `self.env = dict(os.environ)`; `r24-receipt-verify.py:87-102` copies `os.environ` minus git redirections); no file in the set sets a child `TMPDIR`/`HOME` to `/var/tmp` (grep over the four files).
4. **No collateral caller.** A grep over `tools/` and `tests/` for `souji-receipt-run` shows the only executors are `tests/fixtures/r23-receipt-run.py`, `r24-receipt-verify.py`, `r25-receipt-stderr.py` — all inside my item set; no committed tool invokes `run` with an `--out` of its own, so the narrowed/relocated out policy has no other client at the tip.
5. **Residual risk, unexercised by the frozen set.** If a caller sets `TMPDIR` to a path that is not a usable directory, `tempfile.gettempdir()` falls back to `/tmp`: scratch for the measured clone would be created there while a receipt under that path is refused (`OUT-UNDER-TMP`). Base never had this mode (it always used `/var/tmp`). The counter always passes a fresh writable TMPDIR, so T16/T19/T24 cannot observe it; I did not add a fallback guard because that would be a second convention and would mask a caller error. `[INFERENCE]` for any environment that sets an unusable TMPDIR.
6. **Rename reach.** `OUT-OUTSIDE-VAR-TMP` survives only in historical material (`corpus/lessons/round-24.md:333`, the r24/r26 records and `.ufo/` copies) where it is a statement about what the r24 tool emitted; nothing in `tools/`, `tests/`, `SKILL.md` or `SCORECARD.md` binds the literal, and r23's case matcher is the generic `CODE` regex (`r23-receipt-run.py:75`), so the renamed code is still accepted as "an explicit refusal code".

## Deliveries
- `.ufo/waves/round-32/w1/deliver-souji-receipt-run.py` (whole file)
- `.ufo/waves/round-32/w1/deliver-r23-receipt-run.py` (whole file)
- `.ufo/waves/round-32/w1/deliver-r24-receipt-verify.py` (whole file)
- `.ufo/waves/round-32/w1/deliver-r25-receipt-stderr.py` (whole file)
- `.ufo/waves/round-32/w1/deliver-C2Receipt.diff` (`git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- <4 files>`)
- this report

Seat scope: patch + measure only; the lane was not written outside the two directories above, no git/jj mutation outside the scratch clone (which was removed), no sibling lane or fleet path touched.
