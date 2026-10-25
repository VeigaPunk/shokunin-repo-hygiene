# MutC2Survivors — independent reproduction of the C2 mutation matrix (souji r25, wave 2)

Seat: L1Souji25.MutC2Survivors (mutation-tester, leaf). Attacked artifact: W1 `w1/MutSizeCensus.md`
(seat MutSizeCensus-2, canonical path; the sibling `w1/MutSizeCensus-s1.md` uses its own mutant ID scheme
and is not compared here). No lane files edited or written except this report; no git/jj mutations; no
tools installed or updated.

## Status
STATUS: PASS — the C2 mutation matrix in `w1/MutSizeCensus.md` is reproduced byte-for-verdict on an
independent mutant reconstruction: 8-case fixture kills 6/20, 12-case fixture kills 12/20, the r24
11-mutant subset goes 4/11 → 6/11, and the surviving set after extension is exactly
m02, m05, m06, m07, m09, m14, m19, m20. Five survivor witnesses (promisor-only, linked label,
unreachable count, alternates, environment) were re-run; each shows the pristine tool and the mutant
diverging exactly as the matrix claims.

## Method
- Tool bytes: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe:tools/souji-size-census.py`
  → sha256 `c5690681b4e86afd4a2a019847c8d18315cea51c2d58d67b3cbc1260143a6eb3`
  (identical to the current lane worktree file, same hash; blob `182001dbc9aecbd5c877af34301a383fe79c8e02`).
- 8-case fixture: `a6d2d15:tests/fixtures/r24-size-census.py` → sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f`.
- 12-case drafts: `w1/r24-size-census.py` (draft B) sha256 `5bd7e74fb7344e2b583858eaeee761272aadc0d3a0a4cfbbec89fd8f68754238`;
  `w1/ExecC2-2/r24-size-census.py` (draft A) sha256 `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528` —
  the latter is byte-identical to the current lane worktree `tests/fixtures/r24-size-census.py`.
- Mutants: rebuilt independently from the canonical table's clause descriptions + line numbers plus
  source inspection. Each mutant is an exact string replacement, every replacement asserted to occur
  exactly once in the frozen source (`mutate.py`); pristine never edited (pristine hash unchanged at
  the end: `c5690681…`). All 21 files pass `py_compile`.
- Detector: `python3 -B <fixture> --tool <tool>` (fixture exit non-zero = kill). Each full sweep ran
  twice; every `cases=`/`CASE … FAIL` line was identical across passes. Environment: git 2.56.0,
  Python 3.14.8. Scratch `/var/tmp/souji-r25-MutC2Survivors/` only; removed after this report.

## Matrix (reproduced)
Legend: K = killed, with failing case(s); — = survived. Case names: clean1 dangling2 garbage3 linked4
alternates5 refusal6 detector7 control8, bare-nonempty9 bare-empty10 subdir11 partialClone-only12.

| mutant | clause broken | 8-case | 12-case (failing cases) |
|---|---|---|---|
| m01 | count-objects addressed `-C <path>` instead of `--git-dir=<common>` | K | K (3,4) |
| m02 | alternates counted from raw `objects/info/alternates` lines | — | — |
| m03 | `objects/pack/*.promisor` scan dropped | K (6) | K (6) |
| m04 | subdir refusal `realpath(path) != realpath(top)` → `False` | — | K (11) |
| m05 | env allowlist → `dict(os.environ)` | — | — |
| m06 | `timeout=TIMEOUT_S` dropped | — | — |
| m07 | `-c core.fsmonitor=false` dropped | — | — |
| m08 | `size_garbage=0` literal | K (3) | K (3) |
| m09 | `fsck --dangling`, counts `dangling ` | — | — |
| m10 | garbage-warning allowlist → any stderr fails | K (3) | K (3) |
| m11 | stderr-is-failure dropped at all 6 sites | — | K (10) |
| m12 | bare special case dropped (`if bare == "true": top = gitdir` → `if False:`) | — | K (9,10) |
| m13 | `extensions.partialClone` refusal dropped | — | K (12) |
| m14 | `remote.*.promisor` refusal dropped | — | — |
| m15 | `invoked_from=bare` → `main` | — | K (9) |
| m16 | stderr ignored in `checked()` only | — | K (10) |
| m17 | counts line not last (`census.end=ok` trailer appended) | K (1–5) | K (1–5,9) |
| m18 | extra argv accepted (`len(argv) != 2` → `< 2`) | K (6) | K (6) |
| m19 | linked worktree labelled `main` | — | — |
| m20 | stderr ignored at 5 non-`checked` sites | — | — |
| pristine | — | pass 8/8 rc 0 | pass 12/12 rc 0 |
| stub | constant all-zero emitter | REJECTED 4/8 | REJECTED 4/12 |

Totals: 8-case killed=6 survived=14; 12-case killed=12 survived=8; inconclusive=0.
- r24 set (m01–m11): 8-case killed 4 / survived 7 → 12-case killed 6 / survived 5 (case 11 kills m04,
  case 10 kills m11). This is the claimed 4/11 → 6/11.
- **Surviving set after extension: m02, m05, m06, m07, m09, m14, m19, m20** (8/20), matching the W1 report.
- Draft A ≡ draft B: identical pass/fail verdicts for every tool on the 12-case fixture (f12A/f12B
  outputs agree line-for-line on `cases=` and every CASE verdict).

## Survivor witnesses (re-run; same input to pristine and mutant)
Command: `python3 -B witness.py` (own mkdtemp repos, `env` stripped of GIT_* except where noted).

1. **m14 promisor-only** — repo with only `remote.origin.promisor=true` (no `extensions.partialClone`,
   no `.promisor` pack): pristine `rc=2` stderr `souji-size-census: refused: promisor remote (remote.origin.promisor true)`;
   mutant `rc=0` `garbage=0 size_garbage=0 unreachable=0 alternates=0`.
2. **m19 linked label** — `--repo <linked worktree>`: pristine `census.invoked_from=linked`, mutant
   `census.invoked_from=main` (exit codes and counts identical, 0,0,0,0).
3. **m09 unreachable count** — orphan tree holding one blob (`hash-object -w` + `mktree`, uncommitted):
   pristine `unreachable=2`, mutant `unreachable=1` (fsck `--unreachable` sees tree+blob; `--dangling`
   sees the tree only).
4. **m02 alternates** — `objects/info/alternates` with `# comment` + one real path: pristine `alternates=1`,
   mutant `alternates=2` (raw line count, comment included).
5. **m05 environment** — caller `GIT_TRACE=1`: pristine `rc=0`; mutant `rc=1`
   `souji-size-census: git failure: … --version exited 0: 10:10:58.447075 git.c:506 trace: built-in: git vers…`
   (allowlist strips the trace; passthrough leaks it onto stderr → `checked()` fails).

## Receipt/byte checks
- `w1/ExecC2-receipts/c2-green.tsv` matches my green run exactly (same fixture sha `5bd7e74f…`,
  tool sha `c5690681…`, 12/12, rc 0). `c2-red.tsv` (old blob 1efe406e → 11/12, case 11 only),
  `c2-mid.tsv` (778747eb → 10/12, cases 9+10) and `c2-stub.tsv` (4/12) are consistent with the
  red-arm split; not re-run here (out of this item's scope).
- Worktree bytes: `tools/souji-size-census.py` = frozen base `c5690681…`; `tests/fixtures/r24-size-census.py`
  = draft A `9c8a512f…`.

## Findings
1. The W1 mutated matrix is fully reproducible; no verdict differs on an independently reconstructed
   mutant set (same clauses, same failing cases).
2. Detail: m13's kill manifests as a GitFailure `rc=1` (the post-refusal guard `if rc != 1 or err:`
   fires on `rc=0` once the refusal is dropped), not a silent pass-through; case 12 still fails as
   claimed. Same for m03/m18 under case 6: the refusal is gone, so the arm expects `rc=2` and gets
   `rc=0` (or a later failure).
3. Stub control: internal CASE 8 passes in every run (`stub_failed=dangling,garbage,alternates`);
   the stub as `--tool` fails 4/8 and 4/12 → `control=FALSE-GREEN-REJECTED` holds on both fixtures.
4. No new survivors or kills beyond the W1 matrix; the disclosed D3 survivor set is unchanged.

Lane writes: this report only. Scratch `/var/tmp/souji-r25-MutC2Survivors/` removed at the end.
