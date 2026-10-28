# R41w2mutationtester01 — mutation test of `tools/souji-freeze-check.py` against `census/round-41/c2-counter.py`

Seat: R41w2mutationtester01 (mutation-tester, wave 2, falsify). Judged on: operability. Milestone: r41 falsify landed claims.
Lane tip: `1d41c13574db490b712da7ce2a85f`. Tool blob sha256 `3c3e80baedd8…` (12-hex prefix, as the counter prints it). Frozen counter sha256 `85ffe2638a5ed0c83438ce96224f6dad07b2c99567d3d1a71e76e9316a1d1e11` (preregistration C2).
Scope: read-only on the lane. Mutants, probes and receipts live only under `.ufo/waves/round-41/w2/R41w2mutationtester01/`. Scratch under `/fast/scratch/hyaku/souji-r41/R41w2mutationtester01/` (deleted before yield). No installs or updates were made. No git mutation.

## Verdict

**C2 operability target: reproduced at tip (21/21, real ok, retro red, both stubs REJECTED). The frozen counter's coverage is not complete: 14 checks are never distinguished by any frozen case, and one blank-field input bypasses the freeze check with rc 0.**

- Baseline: the committed tool passes 21/21 under `score-candidate.sh c2`, and the lane-direct run matches (`results/baseline-score.txt`, `results/lane-direct.txt`).
- 63 single-defect mutants of the tool (every check deleted, inverted or boundary-shifted, plus strict-ancestor, Round, `.ready`, refusal and summary paths): **41 KILLED, 22 SURVIVED.**
  - 36 killed by a frozen case (`case-*=FAIL`).
  - 5 killed only by the real/retro legs, not by any of the 21 cases: M38 (retro), M41, M56, M60, M61 (real). The c2 cases alone do not detect these.
- The 22 survivors, classified by witness (`results/witness.txt`, `results/equivalence-M46-M48.txt`):
  - **14 genuine uncovered checks** (baseline and mutant give different output on a witness repo; no frozen case distinguishes them): M06, M10, M11, M21, M24, M27, M28, M34, M43, M45, M47, M51, M58, M59.
  - **4 message/detail-only** (exit code and `COULD-NOT-EVALUATE` marker preserved; text differs; the counter checks only rc and class multiset): M20, M52, M53, M54.
  - **3 equivalent** (identical output on the witness; reasoning in §4): M36, M46, M48.
  - **1 unreachable**: M62 (a prereg present at `--rev` implies a reachable adding commit; reasoned, not run).

Operability consequence: the spec-vs-code gaps in §3 (O1 in particular) are behaviours the operator would hit in practice, and the 21 green cases do not cover them.

## 1. Method

- `mutants/baseline.py` = `git show 1d41c13…:tools/souji-freeze-check.py` (byte-identical to the counter's tool_sha).
- `mutate.py` (helper) generates 63 mutants by one exact `str.replace` per mutant. Every pattern must occur exactly once in the baseline, or the generator refuses; all 63 matched once. Mutant text is in `mutants/M*.py`; `mutants/MANIFEST.tsv` lists id, check, kind, old→new.
- Each mutant ran through the committed scorer on a fresh clone: `bash census/round-41/score-candidate.sh c2 $TMPDIR tools/souji-freeze-check.py=<mutant>`. Verdict: exit 0 = survived, exit 1 = killed (the counter's own `met` bit). Per-case lines and SUMMARY are in `results/M*.txt`; table in `results/SUMMARY-table.txt` (Appendix A).
- Survivors were then run as witnesses: a synthetic repo built by `probe.py`, the committed tool and the mutant run on identical input (Appendix B).

## 2. Kill attribution (from `results/M*.txt`)

Killed by a c2 case (36): M01 no-claims; M02 field-missing-base/counter/two-claims; M03 field-missing inversion; M04 field-empty-target; M05 field-empty inversion; M07 two-claims-one-bad; M08 base-unresolved (crash path); M09 base-unresolved inversion; M12 base-not-ancestor; M13 ancestor inversion; M14 counter-missing/population-missing (crash path); M15 counter-missing class; M16 population-missing class; M17 digest deletion; M18 digest inversion; M19 population-digest class; M22/M23 frozen-edited (both Counter and Population); M25/M26 population-empty threshold and deletion; M29 control-missing; M30/M31/M32/M33 control-not-red (deletion, inversion, boundary, last-line); M35/M37/M39/M40/M42/M44 dispatch-before-freeze, Round regex, dispatch scope and json branch; M49/M50 is_ancestor; M55 refusal exit code; M57 SUMMARY findings count; M63 exit-code inversion.

Killed only by legs outside the 21 cases (5):
- M38 (no-Round guard deleted): retro leg crashes (round-40 prereg has no `Round:` line).
- M41 (dispatch tree widened to `.ufo/waves/`): real leg reports 26 findings (round-13…40 dispatch files predate the freeze).
- M56 (SUMMARY claims off by one): real leg `summary=(4, 0)` vs `(3, 0)`. The c2 cases never check the claims count.
- M60 (non-claim `##` header keeps the previous claim): real leg `summary=(5, 0)`.
- M61 (key lines before first claim): real leg crashes.

## 3. Genuine uncovered checks (14) and spec gaps

Each row: witness output (baseline vs mutant) is in Appendix B.

| Mutant | Check not exercised by any frozen case | Witness difference |
|---|---|---|
| M06 | `FIELD-EMPTY` scope drops `Kill` (only `Target` is checked for blank) | baseline `FIELD-EMPTY Kill`; mutant rc 0 |
| M10 | FULL40 gate on `Base` removed; symbolic `Base: HEAD~1` accepted | baseline `BASE-UNRESOLVED`; mutant rc 0 |
| M11 | `BASE-NOT-ANCESTOR` equality arm (`Base` equal to freeze) | baseline flags; mutant rc 0 |
| M21 | no-`sha256=` value classed `COUNTER-MISSING` instead of `COUNTER-DIGEST` | class differs |
| M24 | `POPULATION-EMPTY` boundary: 2 non-blank lines (header + one item) must pass | baseline rc 0; mutant flags |
| M27 | population blank-line filter | baseline `POPULATION-EMPTY` (1 non-blank line plus two blank lines); mutant rc 0 |
| M28 | population emptiness judged on the blob at `--rev`, not at freeze | baseline `POPULATION-EMPTY` + `FROZEN-EDITED`; mutant only `FROZEN-EDITED` |
| M34 | control blank-line filter (trailing blank after `EXIT=1`) | baseline rc 0; mutant `CONTROL-NOT-RED` |
| M43 | `.ready` branch of dispatch scan (also not covered by the real leg) | baseline flags `w1.ready`; mutant rc 0 |
| M45 | oldest-adding-commit selection when a dispatch file is added, deleted, re-added | baseline flags; mutant rc 0 |
| M47 | `FREEZE-REV` oldest-add when the prereg is deleted and re-added | baseline `FROZEN-EDITED`; mutant `COUNTER-DIGEST` |
| M51 | `--rev` must-be-full40 refusal (`--rev HEAD` accepted) | baseline rc 2 refusal; mutant rc 0 |
| M58 | duplicate key in a claim block: first-wins | baseline rc 0; mutant `BASE-UNRESOLVED` |
| M59 | claim-header lookahead `(?![0-9A-Za-z_])` (`## C1x` must not be a claim) | baseline `NO-CLAIMS`; mutant rc 0 |

Message/detail-only survivors (4): M20 (`COUNTER-DIGEST` detail reads `stated None` instead of `has no sha256`), M52 (`--root` not a directory now reported as `--rev … does not resolve`), M53 (absent prereg now reported as `no commit reachable … adds`), M54 (unresolved `--rev` now reported as `prereg.txt is absent at None`, a misleading message). The counter's refusal leg checks only rc 2 and the `COULD-NOT-EVALUATE` marker, so these pass.

### Spec-vs-code observations (outside the mutants; not caught by any c2 case)

- **O1 (operability; highest weight).** A blank `Base`, `Counter`, `Population` or `Control` value passes silently: rc 0, `SUMMARY claims=1 findings=0` (`p-blank-base`, `p-blank-counter`, `p-blank-pop`, `p-blank-control`). The tool's `if f.get(…)` guards skip the check entirely. The documented grammar (tool docstring and counter docstring) says `BASE-UNRESOLVED` for a Base that is not a full40 resolving commit, and `*-MISSING` for a path with no blob. Blank is at least not a blob, so `COUNTER-MISSING` / `POPULATION-MISSING` / `CONTROL-MISSING` are the documented classes [INFERENCE on blank-as-no-blob; the grammar does not state the blank case]. Either way, a freeze line can be blanked and the checklist still exits 0. The c2 cases blank only `Target`.
- **O2.** A missing or malformed `Round:` line silently disables `DISPATCH-BEFORE-FREEZE` (`p-dispatch-no-round`, rc 0). The retro prereg has no `Round:` line, so the retro leg never exercises the dispatch scan at all.
- **O3 (scope note).** Post-freeze edits to the prereg's own `Target`/`Kill` are not detected (`p-edit-after-freeze`, rc 0). The docstring guards Counter and Population bytes only; whether that is in scope for "freeze" is a judgement for the main agent.

## 4. Equivalent and unreachable mutants

- **M36** (drop `c == freeze` in the dispatch scan): `merge-base --is-ancestor X X` is true, so the equality arm is redundant. Witness `w-m36` output is identical for baseline and mutant.
- **M46** (drop `--diff-filter=A` in the dispatch log): the oldest commit touching a new path is its adding commit, so the oldest-selection is unchanged. Identical output on `w-m45` (`results/equivalence-M46-M48.txt`).
- **M48** (drop `--diff-filter=A` in `freeze_rev`): same argument; identical output on `w-m47`.
- **M62** (`if freeze is None` guard): unreachable when the prereg is present at `--rev`, because some reachable commit adds it. [INFERENCE; not run.]

## 5. Limits

- Mutants are single-site string replacements; a multi-site defect was not tested.
- Witness repos are synthetic (`probe.py`) and match the counter's style. Wall-clock timing is not a finding.
- I did not edit any candidate. Recommended cases for the counter, if the main agent admits a revision: blank Base/Counter/Population/Control (O1); absent `Round:` (O2); blank Kill; Base equal to freeze; a 2-line population; a `.ready` file before freeze; a re-added dispatch file; a re-added prereg; a `--rev HEAD` refusal; a duplicate key; a `## C1x` header. These are recommendations only; nothing was implemented.

## 6. Artifacts (all under `.ufo/waves/round-41/w2/R41w2mutationtester01/`)

- `mutate.py` (helper), `probe.py` (witness helper), `mutants/baseline.py`, `mutants/M01.py…M63.py`, `mutants/MANIFEST.tsv`.
- `results/M01.txt…M63.txt` (per-mutant scorer output), `results/SUMMARY-table.txt`, `results/baseline-score.txt`, `results/lane-direct.txt`, `results/witness.txt`, `results/equivalence-M46-M48.txt`.

Appendices A–D below are generated from those files by `cat` and are the exact receipts.

## Appendix A. Per-mutant verdicts and SUMMARY lines (`results/SUMMARY-table.txt`)

Verdict: exit 0 of `score-candidate.sh` = SURVIVED, exit 1 = KILLED. Full per-case output in `results/M*.txt`.

```
# id | class/branch | kind | verdict(score-candidate exit: 0=survived 1=killed) | SUMMARY line
M01 | NO-CLAIMS	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=145a9bed2a87
M02 | FIELD-MISSING	delete | KILLED | cases=21 pass=18 fail=3 control_clean=REJECTED control_findings=REJECTED real=ok retro=FAIL tool_sha=5e436dd23375
M03 | FIELD-MISSING	invert | KILLED | cases=21 pass=3 fail=18 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=f98bbf6b059c
M04 | FIELD-EMPTY	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=c15378c3bf29
M05 | FIELD-EMPTY	invert | KILLED | cases=21 pass=4 fail=17 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=92cfe5ed90a7
M06 | FIELD-EMPTY	scope drops Kill | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=ae67f1abb5d6
M07 | FIELD-MISSING	required keys drop Kill | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=adf6c1fe8243
M08 | BASE-UNRESOLVED	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=8485c150c946
M09 | BASE-UNRESOLVED	invert | KILLED | cases=21 pass=4 fail=17 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=7ccba672bda7
M10 | BASE format gate	delete FULL40 gate | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=bfb68a33a5ad
M11 | BASE-NOT-ANCESTOR strict test	drop equality arm | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c2515ebafa0
M12 | BASE-NOT-ANCESTOR	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=0b8ae286cb25
M13 | BASE-NOT-ANCESTOR	invert ancestor test | KILLED | cases=21 pass=5 fail=16 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=2ed9e5251e2f
M14 | COUNTER-MISSING / POPULATION-MISSING	delete early return | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=e8535c670d92
M15 | COUNTER-MISSING	class swap on Counter call | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=26b800c797d4
M16 | POPULATION-MISSING	class swap on Population call | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3e609ea7b102
M17 | COUNTER-DIGEST / POPULATION-DIGEST	delete | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=af08fd224ef4
M18 | COUNTER-DIGEST / POPULATION-DIGEST	invert | KILLED | cases=21 pass=3 fail=18 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=b5de067c6855
M19 | POPULATION-DIGEST	class swap on Population call | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=54847834dbbe
M20 | no-sha256 branch (Counter/Population value lacks sha256=)	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=9d0c76eba610
M21 | no-sha256 branch	class swap | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=79879a0d34fe
M22 | FROZEN-EDITED	delete | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=2c914edcb584
M23 | FROZEN-EDITED	compare freeze with freeze | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=567f11e068f7
M24 | POPULATION-EMPTY	threshold 2 -> 3 | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=9b2c8c42eea4
M25 | POPULATION-EMPTY	threshold 2 -> 1 | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=5736686e3638
M26 | POPULATION-EMPTY	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=199395e1cd87
M27 | POPULATION-EMPTY	drop blank-line filter | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=4324ba4bf410
M28 | POPULATION-EMPTY source	count lines of blob at rev, not freeze | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=b24e3aa9c357
M29 | CONTROL-MISSING	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=293d05da5429
M30 | CONTROL-NOT-RED	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=ca4b46516257
M31 | CONTROL-NOT-RED	invert | KILLED | cases=21 pass=4 fail=17 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=d38b6832c984
M32 | CONTROL-NOT-RED nonzero boundary	!= 0 becomes > 1 | KILLED | cases=21 pass=5 fail=16 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=8734b209b519
M33 | CONTROL-NOT-RED last line	lines[-1] becomes lines[0] | KILLED | cases=21 pass=5 fail=16 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=b6f53d78e09f
M34 | CONTROL blank-line filter	drop blank-line filter | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=c55e128669e9
M35 | DISPATCH-BEFORE-FREEZE	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=850fb07eff9b
M36 | DISPATCH-BEFORE-FREEZE strict test	drop equality arm | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=66f7fb4d4da8
M37 | DISPATCH-BEFORE-FREEZE	invert ancestor direction | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=dee987df4209
M38 | Round parse guard	delete no-Round return | KILLED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=FAIL tool_sha=3aceafdaf98c
M39 | Round parse	digits (\d+) -> (\d) | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=824224574874
M40 | Round parse	drop re.M | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=7f2040173f03
M41 | dispatch scope	tree widened to .ufo/waves/ | KILLED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=49294d83d960
M42 | dispatch scope	tree points at round N-1 | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=25861a30b03a
M43 | dispatch .ready branch	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=f195a3aacd8c
M44 | dispatch -dispatch.json branch	delete | KILLED | cases=21 pass=20 fail=1 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=c5efa9ec12a4
M45 | dispatch first-add selection	newest instead of oldest | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=cd68fbdff0ca
M46 | dispatch --diff-filter=A	drop filter | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=948bf9a972b7
M47 | freeze_rev oldest-add	drop --reverse | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=565f207c930b
M48 | freeze_rev --diff-filter=A	drop filter | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=4b09d3f1ded6
M49 | is_ancestor (strict-ancestor primitive)	always True | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=eac0ae8eb8ef
M50 | is_ancestor (strict-ancestor primitive)	invert exit test | KILLED | cases=21 pass=5 fail=16 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=a925bd88755c
M51 | refusal: --rev full40 gate	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=d57ce5c8cd2a
M52 | refusal: --root directory gate	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=44496cc3b87b
M53 | refusal: prereg absent at rev	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=f025e4caf904
M54 | refusal: --rev unresolved	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=8a9e804ca1bb
M55 | refusal exit code	2 becomes 1 | KILLED | cases=21 pass=19 fail=2 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=b189b46aa10e
M56 | SUMMARY claims count	claims off by one | KILLED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=78e32f35b36a
M57 | SUMMARY findings count	findings reported as 0 | KILLED | cases=21 pass=4 fail=17 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=58f6b117a291
M58 | parse: duplicate key first-wins	last-wins | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3096f9ee81e9
M59 | parse: claim header lookahead	drop (?![0-9A-Za-z_]) | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=fb6b424166a8
M60 | parse: non-claim ## header ends block	keep previous claim | KILLED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=18ad2087f16f
M61 | parse: key lines before first claim	if cur is not None: -> always | KILLED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red tool_sha=2b8fda0fdeb7
M62 | freeze_rev is None guard	delete | SURVIVED | cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=c893dcc6173c
M63 | return 1 vs 0 on findings	invert | KILLED | cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5f8977dba2fa
```

KILLED: 41. SURVIVED: 22. Total: 63.

## Appendix B. Witness probes: committed tool (baseline) vs mutant on identical synthetic repos (`results/witness.txt`)

```
W w-clean (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m06 (mutant M06)
  baseline: rc=1 | FINDING C1 FIELD-EMPTY Kill ; SUMMARY claims=1 findings=1 | stderr: -
  M06     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m10 (mutant M10)
  baseline: rc=1 | FINDING C1 BASE-UNRESOLVED HEAD~1 ; SUMMARY claims=1 findings=1 | stderr: -
  M10     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m11 (mutant M11)
  baseline: rc=1 | FINDING C1 BASE-NOT-ANCESTOR 9b414facd33590e7c4ade739e6ff2b967884d6d0 is not a strict ancestor of freeze 9b414facd335 ; SUMMARY claims=1 findings=1 | stderr: -
  M11     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m20 (mutant M20)
  baseline: rc=1 | FINDING C1 COUNTER-DIGEST census/c1.py has no sha256=<64 hex> in 'census/c1.py' ; SUMMARY claims=1 findings=1 | stderr: -
  M20     : rc=1 | FINDING C1 COUNTER-DIGEST census/c1.py at freeze hashes d2ee596e966884b00f76999c981ff76524b6d9759fa48321833fe4a18f2c7c6c, stated None ; SUMMARY claims=1 findings=1 | stderr: -
W w-m21 (mutant M21)
  baseline: rc=1 | FINDING C1 COUNTER-DIGEST census/c1.py has no sha256=<64 hex> in 'census/c1.py' ; SUMMARY claims=1 findings=1 | stderr: -
  M21     : rc=1 | FINDING C1 COUNTER-MISSING census/c1.py has no sha256=<64 hex> in 'census/c1.py' ; SUMMARY claims=1 findings=1 | stderr: -
W w-m24 (mutant M24)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
  M24     : rc=1 | FINDING C1 POPULATION-EMPTY census/pop.tsv has 2 non-blank line(s) ; SUMMARY claims=1 findings=1 | stderr: -
W w-m27 (mutant M27)
  baseline: rc=1 | FINDING C1 POPULATION-EMPTY census/pop.tsv has 1 non-blank line(s) ; SUMMARY claims=1 findings=1 | stderr: -
  M27     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m28 (mutant M28)
  baseline: rc=1 | FINDING C1 FROZEN-EDITED census/pop.tsv differs between freeze 74947efb364b and f277d169b9a9 ; FINDING C1 POPULATION-EMPTY census/pop.tsv has 1 non-blank line(s) ; SUMMARY claims=1 findings=2 | stderr: -
  M28     : rc=1 | FINDING C1 FROZEN-EDITED census/pop.tsv differs between freeze 74947efb364b and f277d169b9a9 ; SUMMARY claims=1 findings=1 | stderr: -
W w-m34 (mutant M34)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
  M34     : rc=1 | FINDING C1 CONTROL-NOT-RED census/control.txt last line '' is not EXIT=<nonzero> ; SUMMARY claims=1 findings=1 | stderr: -
W w-m36 (mutant M36)
  baseline: rc=1 | FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/w1-dispatch.json first added at cf27d8152c3f, not after freeze cf27d8152c3f ; SUMMARY claims=1 findings=1 | stderr: -
  M36     : rc=1 | FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/w1-dispatch.json first added at cf27d8152c3f, not after freeze cf27d8152c3f ; SUMMARY claims=1 findings=1 | stderr: -
W w-m43 (mutant M43)
  baseline: rc=1 | FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/w1.ready first added at bf62b1097f49, not after freeze ffedb0ed0d21 ; SUMMARY claims=1 findings=1 | stderr: -
  M43     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m45 (mutant M45)
  baseline: rc=1 | FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/w1-dispatch.json first added at afaf28e10b0c, not after freeze f504cdb076ab ; SUMMARY claims=1 findings=1 | stderr: -
  M45     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m47 (mutant M47)
  baseline: rc=1 | FINDING C1 FROZEN-EDITED census/c1.py differs between freeze 5417e84a4e1e and 6f835df9b4b2 ; SUMMARY claims=1 findings=1 | stderr: -
  M47     : rc=1 | FINDING C1 COUNTER-DIGEST census/c1.py at freeze hashes 7e0b72c004b60013a1a41c83637a5b54af47eff8143806f482597dc0c2f949d2, stated d2ee596e966884b00f76999c981ff76524b6d9759fa48321833fe4a18f2c7c6c ; SUMMARY claims=1 findings=1 | stderr: -
W w-m51 (mutant M51)
  baseline: rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id
  M51     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W w-m52 (mutant M52)
  baseline: rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: --root /nonexistent-root-r41 is not a directory
  M52     : rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: --rev 8cbd11124b262dc3f86f0ea7b8f044a6eaffab8d does not resolve to a commit in /nonexistent-root-r41
W w-m53 (mutant M53)
  baseline: rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: absent.txt is absent at 8cbd11124b262dc3f86f0ea7b8f044a6eaffab8d
  M53     : rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: no commit reachable from 8cbd11124b262dc3f86f0ea7b8f044a6eaffab8d adds absent.txt
W w-m54 (mutant M54)
  baseline: rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: --rev ffffffffffffffffffffffffffffffffffffffff does not resolve to a commit in /fast/scratch/hyaku/souji-r41/R41w2mutationtester01/probe-w-m54
  M54     : rc=2 | - | stderr: REFUSAL COULD-NOT-EVALUATE: prereg.txt is absent at None
W w-m58 (mutant M58)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
  M58     : rc=1 | FINDING C1 BASE-UNRESOLVED 0000000000000000000000000000000000000000 ; SUMMARY claims=1 findings=1 | stderr: -
W w-m59 (mutant M59)
  baseline: rc=1 | FINDING C0 NO-CLAIMS no '## C<digits>' block in prereg.txt ; SUMMARY claims=0 findings=1 | stderr: -
  M59     : rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W p-blank-base (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W p-blank-counter (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W p-blank-pop (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W p-blank-control (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W p-edit-after-freeze (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
W p-dispatch-no-round (mutant -)
  baseline: rc=0 | SUMMARY claims=1 findings=0 | stderr: -
EXIT=0
```

## Appendix C. Equivalence checks for M46 and M48 (`results/equivalence-M46-M48.txt`)

```
== w-m45 under M46 (rev d0f2627eb0d1ebc5324c3f0936eb39494425bbf0)
baseline: FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/w1-dispatch.json first added at afaf28e10b0c, not after freeze f504cdb076ab SUMMARY claims=1 findings=1 
M46: FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/w1-dispatch.json first added at afaf28e10b0c, not after freeze f504cdb076ab SUMMARY claims=1 findings=1 
== w-m47 under M48 (rev 6f835df9b4b26d4a5d3f82c0b87a168ad067a5dd)
baseline: FINDING C1 FROZEN-EDITED census/c1.py differs between freeze 5417e84a4e1e and 6f835df9b4b2 SUMMARY claims=1 findings=1 
M48: FINDING C1 FROZEN-EDITED census/c1.py differs between freeze 5417e84a4e1e and 6f835df9b4b2 SUMMARY claims=1 findings=1 
```

## Appendix D. Receipts for the baseline and commands run

Baseline through the committed scorer (`results/baseline-score.txt`):

```
case-clean=PASS
case-clean-dispatch-after=PASS
case-no-claims=PASS
case-field-missing-base=PASS
case-field-missing-counter=PASS
case-field-empty-target=PASS
case-base-unresolved=PASS
case-base-not-ancestor=PASS
case-counter-missing=PASS
case-counter-digest=PASS
case-population-missing=PASS
case-population-digest=PASS
case-population-empty=PASS
case-control-missing=PASS
case-control-not-red=PASS
case-frozen-edited-counter=PASS
case-frozen-edited-population=PASS
case-dispatch-before-freeze=PASS
case-two-claims-one-bad=PASS
case-unresolved-rev=PASS
case-absent-prereg=PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
EXIT=0
```

Lane-direct run of the committed counter (`results/lane-direct.txt`):

```
case-clean=PASS
case-clean-dispatch-after=PASS
case-no-claims=PASS
case-field-missing-base=PASS
case-field-missing-counter=PASS
case-field-empty-target=PASS
case-base-unresolved=PASS
case-base-not-ancestor=PASS
case-counter-missing=PASS
case-counter-digest=PASS
case-population-missing=PASS
case-population-digest=PASS
case-population-empty=PASS
case-control-missing=PASS
case-control-not-red=PASS
case-frozen-edited-counter=PASS
case-frozen-edited-population=PASS
case-dispatch-before-freeze=PASS
case-two-claims-one-bad=PASS
case-unresolved-rev=PASS
case-absent-prereg=PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
EXIT=0
```

Commands actually run (repo root `/home/vgpnk/Projects/shokunin/souji-shokunin`, `TMPDIR=/fast/scratch/hyaku/souji-r41/R41w2mutationtester01`):

```
git rev-parse HEAD                                    # -> 1d41c13574db490b712da7ce2a85f
git show $TIP:tools/souji-freeze-check.py > mutants/baseline.py ; sha256sum mutants/baseline.py   # 3c3e80baedd8...
python3 -B mutate.py mutants/baseline.py mutants      # wrote 63 mutants
python3 -B census/round-41/c2-counter.py --root $PWD --rev $TIP --scratch $TMPDIR   # results/lane-direct.txt
bash census/round-41/score-candidate.sh c2 $TMPDIR    # results/baseline-score.txt
ls mutants/M*.py | xargs -P 6 -I{} bash -c 'id=$(basename {} .py); bash census/round-41/score-candidate.sh c2 $TMPDIR tools/souji-freeze-check.py={} > results/$id.txt; echo "EXIT=$?" >> results/$id.txt'
python3 -B probe.py > results/witness.txt            # witness repos under $TMPDIR only
for pair in "w-m45 M46" "w-m47 M48"; do set -- $pair; d=$TMPDIR/probe-$1; rev=$(git -C $d rev-parse HEAD); python3 -B mutants/baseline.py --root $d --prereg prereg.txt --rev $rev; python3 -B mutants/$2.py --root $d --prereg prereg.txt --rev $rev; done   # results/equivalence-M46-M48.txt (outputs echoed with labels there)
# SUMMARY-table.txt built by a shell loop over results/M*.txt (EXIT line -> SURVIVED/KILLED; SUMMARY line verbatim)
rm -rf /fast/scratch/hyaku/souji-r41/R41w2mutationtester01   # own scratch, after receipts copied
```

Installs or updates: none. Mutating git/jj commands: none in the lane.
