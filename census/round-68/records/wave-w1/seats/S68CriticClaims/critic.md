# S68CriticClaims: falsification of round-68 C1 (calibration) and C2 (operability)

Read-only. Frozen instruments untouched (sha256 verified: counter ab3ac5c7…, matrix bb56e69a…, mutate-writer 23e19b8e…, SHA256SUMS e7635614…; candidate blob f70da577 = sha256 b811ee2a…; base a8c47d36…). The full 42-row counter was NOT run. All row evidence comes from the frozen counter's own `evaluate()` on row SUBSETS, in-process, via `repro-subset.py` (output `repro-subset.out`). Scratch: `$HYAKU_SCRATCH/souji-r68/S68CriticClaims` (deleted before yield). No lane, fleet or sibling file written; no mutating git.

Reproduce: `python3 -B .ufo/waves/round-68/w1/S68CriticClaims/repro-subset.py` (from the lane root; writes repro-subset.out beside itself).

## Summary table

| # | Attack | Verdict | Severity of the strongest finding |
|---|---|---|---|
| 1 | C1 denominator: every mutant removes a behaviour-relevant protection; equivalents named | BROKEN (partial) | HIGH (see F1) |
| 2 | C1 kill rule: refuted by crash path or honest flip, not by behaviour | BROKEN | MEDIUM (F2) |
| 3 | C2 flips metric: can ambient pass while wrong? predicate vs counted lines | SURVIVES, two named gaps | LOW (F4) |
| 4 | Non-vacuity: do-nothing EXIT=1, 7/14 before, flips 35 | numbers SURVIVE; before-arm wording BROKEN | MEDIUM (F5) |
| 5 | MACHINE BLOCK vs claim text (axis, surface class, enumerate lists) | BROKEN (wording) | LOW (F6) |
| 6 | Declared-protection inventory (extra, from the writer's own docstring) | BROKEN | MEDIUM (F3) |
| 7 | Replace-ref source (PK6 route, git-replace(1), S301) | mechanism SURVIVES; S301 row UNVERIFIED | LOW |
| 8 | Candidate subset sanity | SURVIVES | — |

## Attack 1: C1 denominator and equivalence

Mutants regenerated from the frozen recipe into scratch; all 14 match battery/SHA256SUMS (`MATCH 14 of 14`). Diff against candidate f70da577 (`difflib`, scratch copy):

| Mutant | Diff vs candidate | Normal-run path (no env, regular 0755 file) | Refuting rows (subset) | Route |
|---|---|---|---|---|
| K1 | -5 lines, CONFIG-SET gate (candidate.py:319-323) | equivalent | E1, E2 | **label only** (accept/refuse identical; new_findings=-) |
| K2 | -5 lines, REDIRECT gate (:324-328) | equivalent | E4, E5, E6 (accept) | forgery |
| K3 | drops `-c core.excludesFile=devnull` (:106) | changes only if an excludes file exists in host config (none here: no ~/.config/git/ignore) | PK3 (accept) | forgery |
| K4 | drops GIT_CONFIG_GLOBAL pin (:102) | changes only if host global config has relevant keys (XDG config keys checked: none) | PK4 (accept); E3 non-discriminating (the -c excludes pin masks it) | forgery via PK4 |
| K5 | mask 0o7777→0o777 (:183) | equivalent for non-special-bit files | MOD2, MOD3 (accept) | forgery |
| K6 | drops GIT_NO_REPLACE_OBJECTS pin (:104) | changes only if refs/replace exists (lane has 0) | PK6 (accept) | forgery |
| K7 | drops GIT_CONFIG_NOSYSTEM pin (:103) | changes only if /etc/gitconfig exists (absent) | PK7 (accept) | forgery |
| K8 | -3 lines, INDEX env gate (:333-335) | equivalent | N3, P13 (accept) | forgery |
| M-CD-CALL | drops `_check_env_commondir(root)` (:338) | equivalent | W1, W2 | forgery |
| M-CD-EMPTY | drops `value == ""` refusal (:302-303) | equivalent unless cwd == common dir | W5 (cwd=.git, accept) | forgery, only because W5 sets cwd to .git |
| M-CD-NCABS | abspath instead of realpath (:307-308) | equivalent when GIT_COMMON_DIR unset | W6 (honest, refuse) | **honest flip only**, no forgery |
| M-CD-NCRAW | raw rev-parse string compare (:307-308) | equivalent when GIT_COMMON_DIR unset | W3, W6 (honest, refuse) | **honest flip only**, no forgery |
| M-CD-ROOTREL | join(root, value) before realpath (:308) | equivalent when GIT_COMMON_DIR unset | W4 (refuse, class differs) | **label only**, no forgery |
| M-CD-SCRUB | drops GIT_COMMON_DIR from scrub tuple (:99) | equivalent unless value passes into the check's own rev-parse | W1, W2 (accept) | forgery |

Subset output (decisive lines, `repro-subset.out`):
```
--- K1 rows=['E1','E2'] new_forg=0 new_honest=0/0 class_mis=2 error_rows=0 => REFUTED-shape
--- M-CD-ROOTREL rows=['W4'] new_forg=0 new_honest=0/0 class_mis=1 error_rows=0 => REFUTED-shape
--- M-CD-NCABS rows=['W6','W3'] new_forg=0 new_honest=1/2 class_mis=0 error_rows=0 => REFUTED-shape
--- M-CD-NCRAW rows=['W3','W6'] new_forg=0 new_honest=0/2 class_mis=0 error_rows=0 => REFUTED-shape
```
K1 on E1 (stderr): candidate `refused: RECEIPT-ENV-CONFIG-SET ...`; K1 `refused: lane worktree is dirty` (the `-c excludesFile` pin already neutralises an excludes payload). So K1 is forgery-equivalent on the frozen matrix and is refuted only by a refusal label.

Verdict: **BROKEN (partial)**. No mutant is an equivalent on every path, so "0 false mismatches" holds (no survivor). But four of fourteen are refuted for a reason other than the protection they name: K1 and M-CD-ROOTREL by label, M-CD-NCABS and M-CD-NCRAW by over-refusal of honest aliases. Those four do not evidence forgery-protection sensitivity.

Denominator scope: the MACHINE BLOCK and claim say "the r67 C1 claim", yet K1–K8 are r66 pins (mutate-writer.py header: "r66 pins and gates (carried)"). The denominator also excludes declared pins with no battery mutant (Attack 6).

## Attack 2: C1 kill rule

Predicate: refuted = counter exit 1 with zero `new=error` rows. The counter (c1-counter.py:736-741 `judge`) maps writer rc 0 to accept, rc 2 with no output to refuse, anything else to error. So a writer exit 2 is a legitimate refusal and an exit 1 is an error. Probes (scratch only, one anchored edit each on candidate.py):

```
--- CRASH-EXIT2 rows=['A','C','D','E1'] new_forg=0 new_honest=0/1 class_mis=3 error_rows=0 => REFUTED-shape
    CASE A expect=accept base=accept base_findings=- new=refuse new_findings=-
--- CRASH-EXIT1 rows=['A','C'] new_forg=0 new_honest=0/1 class_mis=1 error_rows=2 => ERROR-ROWS (kill)
--- GIT-PLUMBING-FAIL rows=['A','C','E1','PK3'] new_forg=0 new_honest=0/1 class_mis=2 error_rows=0 => REFUTED-shape
    CASE A expect=accept base=accept base_findings=- new=refuse new_findings=-
    new_stderr: refused: rev is not a commit object (...: unknown option: --r68-no-such-option ...)
```
GIT-PLUMBING-FAIL is the requested crash-path refutation: it removes no protection (it adds an unknown option to the git() argv, candidate.py:105), yet the frozen predicate counts it refuted with zero error rows.

Verdict: **BROKEN**. The kill rule ("exits 1, zero error rows") does not check which row refuted. An exit-2 writer crash, or a broken git plumbing call, is refuted; only exit-1 crashes are killed. For the candidate verdict the honest rows still guard against this, so the candidate's verdict is unaffected; the calibration number is inflated by non-protection failures.

## Attack 3: C2 flips metric

- Predicate text vs counted lines agree: the `^(CASE|SUMMARY|REGRESS|EXIT=)` grep matches the lines c1-counter.py emits (`CASE`, `SUMMARY`, `REGRESS base=`, `EXIT=`; emit calls at :1162-1168).
- Recount of the before arm (r67): `diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' census/round-68/controls/ambient/r67-clean.txt) <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' census/round-68/controls/ambient/r67-ambient.txt) | grep -c '^[<>]'` → `35`. The ambient file is one line, `EXIT=2`, from `C1-COUNTER-FATAL: candidate bytes unreadable … not a git repository` (r67-ambient.stderr).
- Gap A (structural): every child process of the r68 counter gets `clean_env()`, which strips `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` (c1-counter.py:400-412; scrub list :406-407). The writer never sees the ambient values, so the after-arm flips=0 is guaranteed by the scrub. The candidate's response to an ambient `GIT_COMMON_DIR` is never exercised; by code reading it would refuse every row, because `_check_env_commondir` (candidate.py:297-309) runs before any row logic [INFERENCE, not run]. C2 therefore measures scrub completeness for three names, not operability of the writer under the operator shell.
- Gap B (predicate): the flips formula alone passes two identical no-output runs. The kill rule covers this ("either run exits non-zero"), so only the wording is loose. SUMMARY is not in the kill rule; this is harmless because exit 0 forces the SUMMARY (claim_upheld, c1-counter.py:923-926: new_forgeries=0, new_honest=n_accept, class_mismatches=0, regress=PASS).
- Gap C: `# detail` lines carry stderr and are excluded from flips; a divergence in the refusal reason that keeps the class would not flip.

Verdict: **SURVIVES** as written; gaps A-C are named and LOW.

## Attack 4: non-vacuity

| Claim | Recount | Result |
|---|---|---|
| c1-do-nothing EXIT=1 | `grep -h '^EXIT=' census/round-68/controls/c1-do-nothing.txt` → `EXIT=1`; `SUMMARY … new_forgeries=2 … class_mismatches=4`; `grep -c 'new=error'` → 0 | SURVIVES |
| c2-do-nothing-ambient EXIT=1 | same lines, identical CASE lines to c1 (diff of CASE lines → 0) | SURVIVES |
| 7 of 14 refuted before | `grep -c 'exit=1$' census/round-68/controls/r67-counter-battery/index.txt` → 7 (lines 3 K5, 5 K2, 6 K1, 7 M-CD-CALL, 9 M-CD-NCRAW, 11 K8, 13 M-CD-SCRUB); 7 exit=0 | SURVIVES |
| flips 35 before | recount above → 35 | SURVIVES |

Wording gap (F5): the Target says "before (the do-nothing control, 7 refuted)". c1-do-nothing.txt is one base-writer run (42 CASE lines), with no mutant results. The 7 come from the r67 index, a different counter with 31 rows, which the prereg itself calls "a comparison arm, not the control". The C1 before-arm is therefore not the do-nothing control as worded.

Verdict: numbers **SURVIVE**; the before-arm description is **BROKEN** (wording).

## Attack 5: MACHINE BLOCK vs claim text

- C1 axis calibration, C2 axis operability; surface class bookkeeping-file in both. The measured subject of both claims is the writer (`tools/souji-receipt-write.py`) through the counter; the class label describes the counter only (LOW).
- C1 enumerate lists match: 14 mutant names equal the SHA256SUMS entries; matrix rows A..PK7h are the 42 rows in CASE_ORDER (load_matrix enforces order; spec_agreement=None).
- C2 enumerate lists match the three ambient names in the Target.
- Mismatch M1: the Target's before-arm wording (Attack 4).
- Mismatch M2: the C1 scope "the r67 C1 claim" vs K1–K8 (r66 pins) in the denominator.
- Mismatch M3: the axis-harm paragraph refers to "the 31 r67 rows … the clean-run SUMMARY is the same reference". The r68 clean run reports `matrix=42`; the 31-row SUMMARY exists only in census/round-68/controls/ambient/r67-clean.txt (r67 counter). No MACHINE BLOCK predicate checks this clause.
- Mismatch M4: C1 kill says "exits 2 (not evaluated)"; a writer exit 2 is a verdict under judge() (Attack 2).

Verdict: **BROKEN** (wording/scope), LOW.

## Attack 6: declared-protection inventory (candidate docstring and git() pins)

Declared pins with no battery mutant: `core.fsmonitor=false` (candidate.py:105, r63 docstring: "every git call the writer makes runs with core.fsmonitor=false"), `GIT_OPTIONAL_LOCKS=0` (:100). Both are outside the 14-mutant denominator.

Repo-local `core.fsmonitor` probe (scratch FSM-PIN-DROP = candidate minus the fsmonitor pin; hook logs its pwd and exits 1; X2 row = honest, env-free):
```
--- X2-cand rows=['X2'] new_forg=0 new_honest=1/1 class_mis=0 error_rows=0 => SUBSET-PASS
    repo-local fsmonitor hook executions during X2-cand: 0
--- X2-FSM-PIN-DROP rows=['X2'] new_forg=0 new_honest=1/1 class_mis=0 error_rows=0 => SUBSET-PASS
    repo-local fsmonitor hook executions during X2-FSM-PIN-DROP: 8
```
Both slots produce identical CASE lines. The frozen matrix cannot observe the pin: removing it runs a repo-controlled program eight times with zero verdict change. Covered only by reading the code. Pins covered by rows but not by battery mutants: the showUntrackedFiles=all override (candidate.py:158, 393, 495; row V1) and the :(top) pathspec (:119, 381, 494; row N4).

Verdict: **BROKEN** (MEDIUM, F3).

## Attack 7: replace-ref source (PK6)

- `git help replace` (git 2.56.0): line 15 "Adds a replace reference in refs/replace/ namespace"; line 45 "The GIT_NO_REPLACE_OBJECTS environment variable can be set to achieve the …". These support the mechanism behind candidate.py:104 and row PK6 (matrix :40).
- Subset: K6 accepts PK6 (new_forg=1), candidate refuses it with the dirty class. The mechanism is real under this git.
- S301: `grep -n "S301" corpus/SOURCES.md` returns nothing in the working tree; the S68ReviewerSources draft notes registry-row-S301.md not yet present. The registry row is UNVERIFIED by me. The PK6 mechanism does not depend on it.

Verdict: mechanism **SURVIVES**; S301 **UNVERIFIED**.

## Attack 8: candidate subset sanity

`cand rows=[A,W3,W4,W5,W6,E1,E3,MOD2,PK3,PK3h,PK4,PK4h,PK6,PK6h,PK7,PK7h] new_forg=0 new_honest=7/7 class_mis=0 error_rows=0 => SUBSET-PASS`. W4 base refusal is for the L1 reason (detail: base `refused: rev is not a commit object (… fatal: not a git repository …)`), so base-side W4 is not a forgery measurement, as the prereg says.

Verdict: **SURVIVES**.

## Findings (ranked)

- **F1 HIGH.** C1 refutes K1 and M-CD-ROOTREL by refusal label, not by protection. K1's real forgery is absent from the frozen matrix: a scratch row X1 (`GIT_CONFIG_COUNT=1 core.fileMode=false`, mode change) is refused by candidate (`RECEIPT-ENV-CONFIG-SET`) and accepted by K1 (`X1-K1 … new_forg=1`). The frozen 42-row matrix has no non-excludes CONFIG row, so the calibration of the CONFIG gate is an artifact of the excludes pin. Smallest correction for a later round (not this one, rows are frozen): add a non-excludes CONFIG row; make the forgery count label-independent.
- **F2 MEDIUM.** Kill rule counts writer exit 2 as refusal: GIT-PLUMBING-FAIL and CRASH-EXIT2 are refuted with zero error rows (judge, c1-counter.py:736). NCABS and NCRAW are refuted only by honest-row over-refusal.
- **F3 MEDIUM.** Denominator omits declared pins that the matrix cannot observe: core.fsmonitor=false (fsmonitor hook ran 8 times on pin drop, verdict unchanged) and GIT_OPTIONAL_LOCKS=0.
- **F4 LOW.** C2 is satisfied structurally by clean_env (c1-counter.py:406-407): the candidate never receives the ambient values; the metric does not test writer behaviour under them. Predicate kill omits SUMMARY (harmless).
- **F5 MEDIUM.** Before-arm wording: "do-nothing control, 7 refuted" points at a file that holds no mutant results; the 7 come from the r67 index (different counter, 31 rows).
- **F6 LOW.** Scope/wording: "r67 C1 claim" vs r66 pins K1–K8; "31 r67 rows … same reference" clause has no predicate and conflicts with the 42-row SUMMARY; surface-class label describes the counter, not the writer.
- Host: `~/.config/git/config` (1620 bytes) is read by the counter's fixture git calls (no `core.fileMode`, `core.excludesFile`, replace or status keys; keys include `[filter "lfs"]`, `[safe]`, `[user]`). It is outside C2's three-name list; no row is affected today. LOW.

## Files written

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68CriticClaims/critic.md (this file)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68CriticClaims/repro-subset.py
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68CriticClaims/repro-subset.out
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68CriticClaims.md (Report path; same content)

Tools installed: none. Scratch removed before yield.
