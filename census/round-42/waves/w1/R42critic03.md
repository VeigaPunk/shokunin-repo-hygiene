# R42critic03 — attack on C2 (operability): the `--selftest` and `patches` legs

Seat: R42critic03 (critic, leaf). Lane tip scored: afe17f416eec04dcf3f480b580a8f928de61d19d (scratch clones via score-candidate.sh; the lane was never written).
Frozen inputs read: census/round-42/c2-counter.py (full), census/round-42/preregistration.txt (C2 block), census/round-42/c2-cases.tsv, census/round-42/controls/c2-control.txt, tools/souji-freeze-check.py (base r41 tool).
Candidates and receipts: `.ufo/waves/round-42/w1/R42critic03/` (c01–c13, m1–m3 `.py`; score logs in `.ufo/waves/round-42/w1/R42critic03/logs/*.log`).
Tooling: no installs or updates. Only python3 3.14.8, git 2.56.0, bash, coreutils were used.

## Verdict

C2 is **not** measured cleanly by the frozen counter. The target is reachable by an honest tool (c01: 37/37, patches 3/3), so the target is not impossible. But the target is also reached by:

- two tools that implement the grammar dishonestly (c12 ignores nested wave files; c13 never reports a missing `Round:`) — no case in the 37 covers either rule;
- three tools whose self-test is dishonest (c03 sniffs `SOUJI_R42_PATCH`/`PYTHONPATH`; c05 runs one case and counts twelve skipped cases as passes; c10 fingerprints the stdlib function identities) — the patches leg only counts exit codes.

In the other direction the patches leg wrongly rejects honest code (c06 Popen, c07 `hashlib.new`, c08 separate `--diff-filter A` token, c09 `python -I` self-test), because it probes call spelling, not behaviour.

One expectation is not entailed by the docstring: `dup-base-differs` passes only if a duplicated key is evaluated at its **first** occurrence (c02 fails it, see D1). Under the stated grammar this is a policy the docstring does not state and arguably contradicts ("First-wins reading is gone").

The L1 should not land on target alone. Required before landing: the outside checks in the table below, a case for the any-depth DISPATCH clause, a case for missing `Round:`, and a behaviour-level (PATH-shim) git probe in the patches leg.

## Scored candidates (score-candidate.sh c2 … tools/souji-freeze-check.py=<file>)

Every SUMMARY line below is copied verbatim from the log in `logs/`. "Honest" means the grammar is implemented per the c2-counter.py docstring for the cases it exercises; the outside checks are run by hand (see the commands section).

| candidate | SUMMARY (verbatim) | reaches target? | the gap |
|---|---|---|---|
| c01-honest.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=32eb816b0735` | yes | none found. Honest baseline; duplicated keys evaluated at first occurrence (needed for dup-base-differs, see D1). |
| c02-lastwins.py | `SUMMARY cases=37 pass=36 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=2ddd6f0659c9` | no | c01 with last-wins for duplicated keys. Fails `dup-base-differs`: `findings=[('C1', 'BASE-UNRESOLVED'), ('C1', 'KEY-DUPLICATE')]`. Evidence for D1. |
| c03-envcheat.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=ed6551d7cf54` | **yes** | Grammar honest. `--selftest` returns 1 when `SOUJI_R42_PATCH` or `PYTHONPATH` is set (the patch leg sets both; the unpatched leg sets neither). Outside check: `--selftest` with a no-op `sitecustomize` on PYTHONPATH → c03 rc=1, c01 rc=0. The self-test sniffs its environment instead of testing its logic. |
| c04-fixedline.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=16bfd7589976` | no | `--selftest` prints a fixed `SELFTEST cases=13 pass=13 fail=0`, exit 0. Killed by the patches leg (0/3). Counter behaves correctly here. |
| c05-padded.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=b1b1d7c3d4ec` | **yes** | Self-test runs only the `clean` case (which exercises digest, freeze and ancestry); the other 12 are counted as passes (`passed += 1; continue`). Outside check: c05's self-test on m1 (HEADING-MALFORMED emission removed) → `rc=0 SELFTEST cases=13 pass=13 fail=0`; the honest c01 on m1 → rc=1 (`m1-noheading` selftest FAIL 12/13). Also m3 (c05 plus the same mutation) → rc=0. The grammar is still killed by the 37 cases (m3 SUMMARY 33/37), so the gap is in the self-test predicate, not the grade. |
| c06-popen.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=1/3 tool_sha=4201d5ff7273` | no (honest wrongly rejected) | `Repo.run` uses `subprocess.Popen` (not `subprocess.run`). P2/P3 patch only `subprocess.run`, so git is never intercepted → 1/3. Outside check: PATH-shim git (below) → c06 selftest rc=1. |
| c07-newhash.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=2/3 tool_sha=664bafbfd608` | no (honest wrongly rejected) | `hashlib.new("sha256", …)` instead of `hashlib.sha256`. P1 replaces only the `hashlib.sha256` attribute → 2/3. The digests are correct, so the rejection is a probe gap. No outside check run for digests. |
| c08-argvsplit.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=2/3 tool_sha=e6e39c7cb76e` | no (honest wrongly rejected) | `"--diff-filter", "A"` as two argv tokens (git accepts it: selftest and real legs ok). P2 matches the literal `'--diff-filter=A' in argv` → 2/3. Outside check: PATH-shim → rc=1. |
| c09-isolated.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=759423c939b8` | no (honest, patch-immune) | `--selftest` re-executes itself as `python3 -I -B … --selftest-inner`. `-I` drops PYTHONPATH, so the child never sees sitecustomize → 0/3. Outside check: PATH-shim is inherited through the child's env → child fails → c09 rc=1. |
| c10-identity.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=dc6e151c87eb` | **yes** | Behaviour honest; self-test first checks `subprocess.run.__module__ == "subprocess"` and `hashlib.sha256.__module__ == "_hashlib"` (fingerprint of the three hook shapes). Gap: the gate fingerprints the three shapes, not behaviour. Outside check: no-op sitecustomize → rc=0 (correct). A wrapper that changes identity but not behaviour would be rejected (wrong reject); any other hook is invisible. |
| c11-parseonly.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=7de3856f8c02` | no | In-memory `parse()` self-test with 12 checks (passes the `>=12` predicate). No digest/freeze/ancestry → 0/3. Shows the patches leg does kill partial self-tests. |
| c12-toponly.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=76788e3b6054` | **yes** | Grammar dishonest: DISPATCH only scans top-level files of `.ufo/waves/round-N/`, not "any depth". No case in the 37 has a nested wave file before freeze. Outside check: nested `…/w1/Seat-dispatch.json` committed before freeze → c01 rc=1 `DISPATCH-BEFORE-FREEZE`; c12 rc=0. |
| c13-noround.py | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=381a92f204f5` | **yes** | Grammar dishonest: a prereg without `Round:` yields no `FIELD-MISSING C0 Round` (the r41 rule the docstring says is retained). No case in the 37 omits `Round:`. Outside check: no-Round fixture → c01 rc=1 `FIELD-MISSING C0 Round`; c12 rc=1 (same); c13 rc=0. |
| m1-noheading.py | `SUMMARY cases=37 pass=33 fail=4 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=b783af6e30b7` | no | c01 with HEADING-MALFORMED emission removed. Killed by the four heading cases (counter works). |
| m2-nodup.py | `SUMMARY cases=37 pass=34 fail=3 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=bb0406ebb356` | no | c01 with KEY-DUPLICATE emission removed. Killed by three duplicate cases. |
| m3-padded-noheading.py | `SUMMARY cases=37 pass=33 fail=4 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=1d82d1842c22` | no | c05 with HEADING-MALFORMED removed. Self-test and patches legs both green while the grammar is broken; only the 37 cases fail. Shows the two self-test-side legs do not measure grammar. |

Control receipts (census/round-42/controls/c2-control.txt, run by the L1) were consistent with these results: the always-green self-test control reports `patches=0/3` (same as c04).

## Counter findings (for the L1, not edits)

**D1 — `dup-base-differs` expectation is not entailed by the grammar.** Docstring: "one finding per duplicated key … First-wins reading is gone." The expected multiset `[("C1","KEY-DUPLICATE")]` holds only if the tool evaluates the first occurrence (c01). A tool that checks every occurrence or the last (c02) also emits `BASE-UNRESOLVED` for the `0`×40 duplicate, and the case fails. The docstring names no policy. Evidence: `logs/c02-lastwins.log`, line `case-dup-base-differs=FAIL rc=1 … findings=[('C1', 'BASE-UNRESOLVED'), ('C1', 'KEY-DUPLICATE')] want=[('C1', 'KEY-DUPLICATE')]`. Fix options for the L1: state the policy in the docstring (and then the case can stay), or make the fixture's duplicate value resolvable so the case no longer depends on which occurrence is used.

**D2 — no case for the any-depth clause of the DISPATCH widening.** The docstring says "(any depth)". All 14 dispatch cases use top-level files (`w1-dispatch.json`, …); `w1/Seat01.md` is nested but not a wave-file name. c12 passes all 37. Evidence: fixture run below (c01 rc=1, c12 rc=0).

**D3 — no case for a missing `Round:`.** The base docstring and r42 docstring retain `FIELD-MISSING C0 Round`. No case omits `Round:`. c13 passes all 37. Evidence: fixture run below.

**D4 — the patches leg probes call spelling, so honest code is rejected.** P2 matches the literal token `--diff-filter=A` in argv; P3 matches `merge-base` as a list element; P1 replaces only the `hashlib.sha256` attribute; all three replace only `subprocess.run`. Honest variants c06 (Popen), c07 (`hashlib.new`), c08 (split token) and c09 (`-I` child) are rejected (1/3, 2/3, 2/3, 0/3). A spelling-independent probe catches c06, c08 and c09 (PATH-shim git below, rc=1 each). No spelling-independent digest probe was found; c07 remains a false rejection.

**D5 — the patches leg counts any nonzero exit as "rejected".** [INFERENCE from c2-counter.py line 410: `patches += 1 if (selftest == "ok" and p_rc not in (0, 124))`.] A self-test that crashes under PYTHONPATH, or calls `sys.exit(1)` for any reason, counts. Not tested by a separate candidate.

**D6 — the selftest predicate (`SELFTEST cases>=12`, `pass==cases`, `fail==0`) does not check that cases are real.** c05 and m3 show vacuous and grammar-blind self-tests reach `selftest=ok patches=3/3`.

**D7 — the patches leg cannot separate sniffing from testing.** c03 (env sniffing) and c10 (identity fingerprint) reach 3/3. Neither is caught by any counter leg. Outside check: a no-op sitecustomize must leave the self-test green (c03 fails it).

## Outside checks (commands run and their output)

All commands run from the scratch dir `/fast/scratch/hyaku/souji-r42/R42critic03` (deleted at the end); candidates from `.ufo/waves/round-42/w1/R42critic03/`.

1. Scoring: `bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42critic03 tools/souji-freeze-check.py=<file>` for each candidate (logs copied to `logs/`). Each run took ~7 s. Outputs are the SUMMARY lines in the table.

2. Self-test sensitivity (no counter):
```
for v in c01-honest c03-envcheat c05-padded c10-identity c11-parseonly c12-toponly c13-noround m1-noheading m2-nodup; do
  d=$(mktemp -d -p …); out=$(env -i PATH=/usr/bin:/bin TMPDIR=$d python3 -B $W/$v.py --selftest 2>&1); rc=$?; …; done
c01-honest rc=0 SELFTEST cases=13 pass=13 fail=0
c03-envcheat rc=0 SELFTEST cases=13 pass=13 fail=0
c05-padded rc=0 SELFTEST cases=13 pass=13 fail=0
c10-identity rc=0 SELFTEST cases=13 pass=13 fail=0
c11-parseonly rc=0 SELFTEST cases=12 pass=12 fail=0
c12-toponly rc=0 SELFTEST cases=13 pass=13 fail=0
c13-noround rc=0 SELFTEST cases=13 pass=13 fail=0
m1-noheading rc=1 SELFTEST cases=13 pass=12 fail=1
m2-nodup rc=1 SELFTEST cases=13 pass=12 fail=1
```

3. Padded self-test on a broken grammar (m3, derived from c05):
```
m3 rc=0 SELFTEST cases=13 pass=13 fail=0
m3 counter rc=1
SUMMARY cases=37 pass=33 fail=4 … selftest=ok patches=3/3 …
```

4. PATH shim (`shim/git`: `*merge-base*` → exit 1; `*--diff-filter*` → exit 0 with no output; otherwise `exec /usr/bin/git "$@"`), selftest run with `PATH=$shim:/usr/bin:/bin`:
```
c01-honest shimmed rc=1 SELFTEST cases=13 pass=0 fail=13
c06-popen shimmed rc=1 SELFTEST cases=13 pass=0 fail=13
c08-argvsplit shimmed rc=1 SELFTEST cases=13 pass=0 fail=13
c09-isolated shimmed rc=1 SELFTEST cases=13 pass=0 fail=13
c10-identity shimmed rc=1 SELFTEST cases=13 pass=0 fail=13
c11-parseonly shimmed rc=0 SELFTEST cases=12 pass=12 fail=0
```
The shim catches every git-using variant and correctly does not catch the parse-only self-test (c11, which never calls git).

5. No-op sitecustomize (`PYTHONPATH=<dir with a comment-only sitecustomize.py> SOUJI_R42_PATCH=NOOP`):
```
c01-honest no-op-hook rc=0 SELFTEST cases=13 pass=13 fail=0
c03-envcheat no-op-hook rc=1 SELFTEST cases=13 pass=13 fail=0
c05-padded no-op-hook rc=0 SELFTEST cases=13 pass=13 fail=0
c10-identity no-op-hook rc=0 SELFTEST cases=13 pass=13 fail=0
```
(c03 with no hook: rc=0.)

6. Fixtures for D2 and D3 (python in an isolated scratch repo, `git -C` on every call, digests computed in the driver; `TMPDIR` set; removed after):
```
[nested] c01-honest.py rc=1 FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-42/w1/Seat-dispatch.json first added at 19abeff9e511, not after freeze 8374c030585e | SUMMARY claims=1 findings=1
[nested] c12-toponly.py rc=0 SUMMARY claims=1 findings=0
[nested] c13-noround.py rc=1 FINDING C0 DISPATCH-BEFORE-FREEZE … | SUMMARY claims=1 findings=1
[noround] c01-honest.py rc=1 FINDING C0 FIELD-MISSING Round | SUMMARY claims=1 findings=1
[noround] c12-toponly.py rc=1 FINDING C0 FIELD-MISSING Round | SUMMARY claims=1 findings=1
[noround] c13-noround.py rc=0 SUMMARY claims=1 findings=0
```

7. Mutant checks: `c2` score of m1/m2/m3 are in the table; they are killed by the counter as expected.

## Checks of the CASES table against the docstring

Read against the docstring grammar, all 37 expected multisets are entailed except as follows:
- `dup-base-differs` — see D1 (policy-dependent).
- Coverage gaps, not wrong expectations: D2 (any-depth dispatch), D3 (missing Round). The expectations that exist are consistent with the docstring: `heading-*` (valid `##C2`/`## c2`/`## C 2`/`## C2x` malformed; `## C2 - …` valid), `counter-symlink` / `population-symlink` ("this finding alone"), `dispatch-*-before` / `*-after` / `notes-before`, `heading-valid-tail` (six FIELD-MISSING for an empty claim), `two-claims-one-bad`, `unresolved-rev` / `absent-prereg` (exit 2). Case count: 16 r42 + 21 r41 = 37, matching the preregistration.

## Limits of this attack

- Only c01 is a full honest grammar implementation; the honest-variant claims for c06–c09 are in the table only for the patches leg, not for the other legs.
- The PATH-shim and no-op checks are by hand, not a frozen counter. They are recommendations for the L1, not a measurement.
- A digest-side outside check for c07 was not found; D4's digest gap is stated, not closed.
- D5 is from code reading and is not run.
- Nothing was landed, committed, or written to the lane, the fleet, tools/, census/ or corpus/.
