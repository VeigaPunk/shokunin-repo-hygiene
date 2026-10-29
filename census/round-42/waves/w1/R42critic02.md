# R42critic02 — attack on C2 (operability), frozen counter `census/round-42/c2-counter.py`

Seat: R42critic02 (critic). Lane tip read: `afe17f416eec04dcf3f480b580a8f928de61d19d` (freeze). Base: `bf618f6c5c09d302994871c94903abbea2deb60d`. Nothing in the lane, tracked tree, tools/, census/ or corpus/ was written. All candidates, receipts and attack harnesses are under `.ufo/waves/round-42/w1/R42critic02/`. Scratch under `/fast/scratch/hyaku/souji-r42/R42critic02/` was removed before this report was written.

## Verdict

**C2 as frozen does not measure operability.** Its target (`cases=37 pass=37 fail=0 ... selftest=ok patches=3/3`) is reached by:

1. **Two non-implementations** that answer from the counter's own synthetic repositories: K5 (keys on the basename of `--root`, which the counter names `cand-<case>`) and K5b (keys on a repository-shape hash: normalised prereg text, commit subjects, tree paths and blobs, Base ancestry). Both score 37/37 and 3/3. Held-out fixtures written from the docstring, not from the table, catch them: 6/11 each.
2. **Three honest-grammar candidates whose `--selftest` is fake** (K2 literal summary plus a PYTHONPATH check; K3 identity guard on two stdlib functions; K4 literal summary plus an `assert` that crashes under patch). Each scores 37/37 and 3/3 while its self-test detects no logic defect. The frozen counter reads `selftest=ok` on the three logic-mutated K2 builds, including one with `real=FAIL`.

The target is also reachable honestly (K1, §3), but **one target-relevant expectation is reading-dependent** (`dup-base-differs`, §4): an implementer who follows the docstring's "First-wins reading is gone" literally scores 36/37. A second expectation (`population-symlink`) is entailed only weakly. The counter cannot tell K1 from K2–K5b on the leg that is meant to measure the self-test, and its held-out coverage is zero.

## 1. Candidate table

`SUMMARY` values are verbatim in §2. "Reaches target" means `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` under `score-candidate.sh c2`.

| candidate | SUMMARY (key fields) | reaches target? | the gap |
|---|---|---|---|
| K0 `tools/souji-freeze-check.py` (r41 tool, unchanged) | `cases=37 pass=24 fail=13 ... selftest=FAIL patches=0/3` | no | none; reproduces control A exactly (`tool_sha=8131847bcfc5`) |
| K1 `K1-honest-grammar.py` (my honest reference: four r42 rules plus a real 15-case self-test) | `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` | **yes, honestly** | none in grammar or self-test; held-out 11/11; the one reading-dependent expectation it satisfies is `dup-base-differs` (first-wins evaluation, see §4) |
| K2 `K2-literal-selftest.py` (K1 grammar; `--selftest` prints `SELFTEST cases=15 pass=15 fail=0` and runs nothing; exits 1 iff `PYTHONPATH` set) | `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` | **yes** | the self-test checks nothing; it detects only the harness's `PYTHONPATH`. Logic-mutant outside check: K2 **0/3 caught** (K1 3/3). Counter: K2 mutants `digest-inverted`, `freeze-none`, `ancestry-inverted` each give `selftest=ok patches=3/3` (`real=FAIL` in all three). Outside check that catches it: `attacks/mutant-check.py` (mutate the tool's own digest, freeze and ancestry logic; require `--selftest` rc≠0). |
| K3 `K3-identity-selftest.py` (K1 grammar; self-test refuses iff `hashlib.sha256.__module__ != '_hashlib'` or `subprocess.run.__module__ != 'subprocess'`, otherwise literal) | `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` | **yes** | the self-test is an identity check on two stdlib functions, the same functions the counter's P1/P2/P3 patches replace; it runs no case. Logic-mutant check: 0/3 caught. Outside check: `mutant-check.py`, plus require the self-test to build a repo and call `evaluate()`. |
| K4 `K4-assert-crash-selftest.py` (K1 grammar; literal summary, then `assert not os.environ.get('PYTHONPATH')`) | `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` | **yes** | the counter's patch leg counts any non-zero exit as "rejected", including a crash. Under P1 the self-test exits 1 with `AssertionError: interpreter environment not pristine` and a traceback, and `run_selftest` returns `(1, (15, 15, 0), True)`, which the leg counts. Outside check: require a SELFTEST line with fail>0 and no traceback under each patch. Logic-mutant check: 0/3 caught. |
| K5 `K5-dirname-table.py` (no grammar; table copied from the counter's CASES, keyed on the basename of `--root`; literal self-test) | `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` | **yes** | keys on `cand-<case>` directory names the counter's `build()` creates. Held-out harness `heldout-check.py`: **6/11** (fails H1, H2, H5, H6, H10). Outside check: held-out fixtures (done), and rename-invariance (rename the scratch directories and the verdict must not change). |
| K5b `K5b-shape-table.py` (no grammar and no directory names; key = normalised prereg text, commit subjects, `ls-tree -r` paths/modes/blobs, Base ancestry bit; table generated by running the counter's own `build()`) | `cases=37 pass=37 fail=0 ... selftest=ok patches=3/3` | **yes** | keys on the synthetic commit messages and tree shape the counter's build() produces. Held-out: **6/11** (fails H1, H2, H5, H6, H10). Outside check: held-out fixtures, plus a shape perturbation (change one commit subject and one file name in a held-out fixture and check the verdict). |
| K6 `K6-no-keydup.py` (K1 with KEY-DUPLICATE deleted; sensitivity control) | `cases=37 pass=34 fail=3 ... selftest=FAIL patches=0/3` | no | none; shows the counter is sensitive to a missing r42 rule (3 dup cases fail; held-out fails H5, H6) |
| K7 `K7-last-wins.py` (K1 evaluating the last occurrence of a duplicated key) | `cases=37 pass=36 fail=1 ... selftest=ok patches=3/3` | no (misses `dup-base-differs` by one) | reading gap: `dup-base-differs` expects one finding, KEY-DUPLICATE alone; last-wins adds BASE-UNRESOLVED from the zero Base. The docstring says "First-wins reading is gone", so it does not entail the expectation (§4). |
| K8 `K8-symlink-emptiness.py` (K1 where a symlink still gets POPULATION-EMPTY on its link text) | `cases=37 pass=36 fail=1 ... selftest=FAIL patches=0/3` | no (misses `population-symlink` by one) | reading gap: the docstring says POPULATION-SYMLINK is "the same" as COUNTER-SYMLINK ("this finding alone"); the expectation's suppression of POPULATION-EMPTY is entailed only through that phrase (§4, weak). |

## 2. Verbatim SUMMARY lines (exact commands in §5; files under this seat directory)

```
score-K0-base.txt:            SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=8131847bcfc5
score-K1-honest-grammar.txt:  SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=38113487bc85
score-K2-literal-selftest.txt:SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=2a49bd1515ff
score-K3-identity-selftest.txt:SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=c93c674382fd
score-K4-assert-crash-selftest.txt:SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9f85a64e2274
score-K5-dirname-table.txt:   SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=53cee1180143
score-K5b-shape-table.txt:    SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=2e2a9fca5dc6
score-K6-no-keydup.txt:       SUMMARY cases=37 pass=34 fail=3 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=b795c83cca73
score-K7-last-wins.txt:       SUMMARY cases=37 pass=36 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=22fbd0524592
score-K8-symlink-emptiness.txt:SUMMARY cases=37 pass=36 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=d6a090a324be
score-K2-mut-digest-inverted.txt: SUMMARY cases=37 pass=3 fail=34 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red retro_clean=FAIL selftest=ok patches=3/3 tool_sha=934ee615f459
score-K2-mut-freeze-none.txt:     SUMMARY cases=37 pass=2 fail=35 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL retro_clean=FAIL selftest=ok patches=3/3 tool_sha=a03ce78aac77
score-K2-mut-ancestry-inverted.txt: SUMMARY cases=37 pass=5 fail=32 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red retro_clean=FAIL selftest=ok patches=3/3 tool_sha=5a5361e219a1
```

Per-leg detail for K1 (`score-K1-honest-grammar.txt`): `real ok rc=0 findings=0 summary=(3, 0)`; `retro red rc=1 findings=19 summary=(3, 19)`; `retro_clean ok rc=0 findings=0 summary=(3, 0)`; `selftest ok rc=0 summary=(15, 15, 0)`.

The K0 line is the same as control A in `census/round-42/controls/c2-control.txt` (line 45, `tool_sha=8131847bcfc5`), so the harness reproduces the do-nothing control on this machine.

## 3. Held-out differential check (`heldout-check.py`, `heldout-results.txt`)

Eleven fixtures, none in `c2-cases.tsv` or `CASES`. Each expectation was written from the docstring before any candidate was run. The fixtures cover: dispatch file names under the wave tree (`-dispatch` at any depth, `.ready` nested, `-spec.json.bak` clean, another round clean), KEY-DUPLICATE with three copies and with two keys, `###` and `## C` (no digit) headings, `##C` with no digit, a dangling counter symlink, and trailing spaces in a value.

Results (`HELDOUT-SUMMARY`):

```
souji-freeze-check.py (r41 base)   pass=7  fail=4  n=11   (fails H1, H5, H6, H10)
K1-honest-grammar.py               pass=11 fail=0  n=11
K2-literal-selftest.py             pass=11 fail=0  n=11
K3-identity-selftest.py            pass=11 fail=0  n=11
K4-assert-crash-selftest.py        pass=11 fail=0  n=11
K5-dirname-table.py                pass=6  fail=5  n=11   (fails H1, H2, H5, H6, H10)
K5b-shape-table.py                 pass=6  fail=5  n=11   (fails H1, H2, H5, H6, H10)
K6-no-keydup.py                    pass=9  fail=2  n=11   (fails H5, H6)
K7-last-wins.py                    pass=11 fail=0  n=11
K8-symlink-emptiness.py            pass=11 fail=0  n=11
```

The held-out oracle agrees with the honest K1 on all 11, so the docstring grammar is internally consistent on these shapes. K2–K4 pass only because they carry K1's grammar.

## 4. Audit of the 37 expectations against the docstring

I checked each `CASES` row against the docstring grammar and class list. Thirty-five are entailed by a stated rule. Two are not entailed without a reading choice:

- **`dup-base-differs` → `[C1 KEY-DUPLICATE]` alone. NOT entailed.** The docstring says KEY-DUPLICATE is "one finding per duplicated key (detail: the key). First-wins reading is gone." Three readings of the value to evaluate:
  - first occurrence: `{KEY-DUPLICATE}` (satisfies the expectation; K1)
  - last occurrence (K7): `{BASE-UNRESOLVED, KEY-DUPLICATE}` (`pass=36`)
  - all occurrences or a skipped key: adds `BASE-UNRESOLVED` or `FIELD-MISSING Base`

  Only first-wins evaluation satisfies the expectation, and the docstring disowns it. The expectation therefore resolves an ambiguous docstring in one direction without saying so. Defect to report: the expectation or the docstring must state which occurrence is evaluated. Not fixed here (frozen).
- **`population-symlink` → `[C1 POPULATION-SYMLINK]` alone. Weakly entailed.** The docstring says POPULATION-SYMLINK is "the same" as COUNTER-SYMLINK, which "this finding alone, no digest comparison is made". The stated reason ("the link text is not the counter") concerns digests, not the line-count check. K8 (emptiness still checked on the link text) gives `{POPULATION-EMPTY, POPULATION-SYMLINK}` and scores `pass=36`. Reported as a limit, not a clear defect.

The other 35 expectations: the four dispatch name rules (`-spec.json`, `-results.json`, `-dispatch`, `.ready`) and the clean cases (`notes.md`, `w1/Seat01.md`, dispatch after freeze) follow the docstring text; `HEADING-MALFORMED` for `##C2`, `## c2`, `## C 2`, `## C2x` matches the docstring's four examples; `heading-valid-tail` (`## C2 - empty second claim`, six FIELD-MISSING under C2) follows from the claim-block rule; the refusal rows (exit 2) follow the docstring's `REFUSAL COULD-NOT-EVALUATE` clause; the "21 r41 cases" in the docstring equals the 19 CASES rows plus the two refusal checks (`total = len(CASES) + 2`), and "16 new" equals the 16 r42 rows. Counts are consistent.

## 5. Commands run (exact) and what they showed

Environment: `TMPDIR=/fast/scratch/hyaku/souji-r42/R42critic02`, cwd the lane (`/home/vgpnk/Projects/shokunin/souji-shokunin`). No tools installed or upgraded; only `python3` and `git` were used.

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` → the lane root. `git log --oneline -3` → `afe17f4` tip.
2. Read the preregistration (C2 block), `c2-counter.py` (all 428 lines), `c2-cases.tsv`, `controls/c2-control.txt`, `tools/souji-freeze-check.py`, `score-candidate.sh`.
3. `bash census/round-42/score-candidate.sh c2 $S tools/souji-freeze-check.py=tools/souji-freeze-check.py` → K0 line (§2), matching control A.
4. Wrote `K1-honest-grammar.py`. First scored: `cases=37 pass=37 ... selftest=ok patches=2/3 tool_sha=a0e48d788491`. Direct check showed P1 undetected: the self-test computed fixture digests with `hashlib.sha256`, the function P1 reverses, so reversal cancelled. Fixed by using `hashlib.new("sha256", ...)` in the fixture only. Re-scored → `patches=3/3 tool_sha=38113487bc85` (§2).
5. `python3 -B K1-honest-grammar.py --selftest` → `SELFTEST cases=15 pass=15 fail=0`, rc 0. `python3 -B K1 --root <lane> --prereg census/round-42/preregistration.txt --rev afe17f4...` → `SUMMARY claims=3 findings=0`, rc 0.
6. Per-patch run via `c2-counter.run_selftest` (imported read-only): K1 P1 `(1, (15, 1, 14), False)` after the fix; P2 `(1, (15, 0, 15), False)`; P3 `(1, (15, 3, 12), False)`. Before the fix P1 gave `(0, (15, 15, 0), False)`.
7. `gen-variants.py` and `gen-shape-and-readings.py` (copies in `attacks/`) generated K2, K3, K4, K5, K6 and K5b, K7, K8 from K1. K5b's table is produced by running the counter's own `build()` for all 35 CASES and recording its expectations; the generator asserted no two cases share a key (`cases=35 keys=35 collisions=[]`).
8. Scored K2, K3, K4, K5, K6, K5b, K7, K8 with `score-candidate.sh c2` (outputs in §2 and `score-*.txt`). Scored K2 mutants `digest-inverted`, `freeze-none`, `ancestry-inverted` the same way (`score-K2-mut-*.txt`).
9. `python3 -B heldout-check.py --scratch $S <tools...>` → `heldout-results.txt` (§3).
10. `python3 -B attacks/mutant-check.py --scratch $S K1 K2 K3 K4 K5 K5b K7 K8` → `attacks/mutant-check-output.txt`:
    ```
    K1-honest-grammar.py      | digest-inverted rc=1 ... | freeze-none rc=1 ... | ancestry-inverted rc=1 ... | CAUGHT 3/3
    K2-literal-selftest.py    | digest-inverted rc=0 SELFTEST cases=15 pass=15 fail=0 | freeze-none rc=0 ... | ancestry-inverted rc=0 ... | MISSED
    K3-identity-selftest.py   | ... rc=0 (all three)  | MISSED
    K4-assert-crash-selftest.py | ... rc=0 (all three) | MISSED
    K5-dirname-table.py       | ANCHOR-MISSING(0) x3 | MISSED   (no logic to mutate)
    K5b-shape-table.py        | ANCHOR-MISSING(0) x3 | MISSED   (no logic to mutate)
    K7-last-wins.py           | CAUGHT 3/3
    K8-symlink-emptiness.py   | CAUGHT 3/3
    ```
11. K4 under P1 (crash counted): `run_selftest(K4, scratch, 'P1')` → `(1, (15, 15, 0), True)`; the traceback ends `AssertionError: interpreter environment not pristine`.

Verdicts per candidate are in §1. All checks were run; none is inferred.

## 6. Limits and what would catch them outside the counter

- **Self-test not exercising the tool (K2–K4).** Counter gap: patch leg checks only that the self-test exits non-zero under three stdlib patches, and the case leg does not check the self-test. Outside check: `attacks/mutant-check.py` (K1 3/3, K2–K4 0/3). Also require the self-test to emit fail>0 under each patch and to produce no traceback.
- **Memorised cases (K5, K5b).** Counter gap: the 37 cases are a closed, public set (the table in `c2-counter.py` is readable from the lane). Outside check: `heldout-check.py` (6/11 each) and rename / shape-perturbation invariance.
- **Reading-dependent expectations (K7, K8).** Counter gap: the expectation pins a reading the docstring does not state. Not fixable in r42 (frozen). For the L1: either state in the docstring which occurrence is evaluated for a duplicated key and whether a symlink still gets emptiness checks, or accept that the target is missed by one under a literal reading.
- **Patch leg counts crashes.** `run_selftest` returns a crash as rc 1 and the leg counts `p_rc not in (0, 124)`. Outside check: require a SELFTEST line with fail>0 under each patch.
- **K1 is a reference build, not a shipped tool.** It reaches the target and passes held-out 11/11. Its only reading choice is first-wins evaluation of duplicated keys (§4).

## 7. Files (all under `.ufo/waves/round-42/w1/R42critic02/`)

- Candidates: `K1-honest-grammar.py`, `K2-literal-selftest.py`, `K3-identity-selftest.py`, `K4-assert-crash-selftest.py`, `K5-dirname-table.py`, `K5b-shape-table.py`, `K6-no-keydup.py`, `K7-last-wins.py`, `K8-symlink-emptiness.py`.
- Scores: `score-K0-base.txt`, `score-K1-honest-grammar.txt`, `score-K2-literal-selftest.txt`, `score-K3-identity-selftest.txt`, `score-K4-assert-crash-selftest.txt`, `score-K5-dirname-table.txt`, `score-K5b-shape-table.txt`, `score-K6-no-keydup.txt`, `score-K7-last-wins.txt`, `score-K8-symlink-emptiness.txt`, `score-K2-mut-{digest-inverted,freeze-none,ancestry-inverted}.txt`.
- Harnesses: `heldout-check.py`, `heldout-results.txt`; `attacks/mutant-check.py`, `attacks/mutant-check-output.txt`; `attacks/gen-variants.py`, `attacks/gen-shape-and-readings.py` (scratch generators, copied in).

Tooling recorded: none installed or changed. Host state: no pacman, no root, no signals sent.

## Yield summary (≤10 lines)

- Target `cases=37 pass=37 patches=3/3` reached by K5 and K5b (no grammar; K5 keys on `cand-<case>` dirnames, K5b on commit subjects and tree shape). Held-out: 6/11 each.
- Reached by K2, K3, K4: honest grammar but fake self-tests (literal summary / identity guard / crash). Logic-mutant check 0/3 caught; the counter reads `selftest=ok` on broken K2 builds.
- Honest K1 reaches 37/37 and held-out 11/11; the reference needed first-wins evaluation of duplicated keys.
- Expectation defect: `dup-base-differs` requires first-wins, which the docstring disowns; last-wins scores 36/37 (K7). Weak: `population-symlink` suppression of POPULATION-EMPTY (K8 36/37).
- Patch leg accepts a crash as rejection (K4 traceback counted).
- Not a claim-level failure of the lane: K1 reaches target, so the round can be measured, but the counter as frozen does not separate honest from memorised tools.
- Reports: `R42critic02.md` (this), with evidence files listed in §7.
