# R40reviewer18 — C3 coverage attack

Seat: reviewer (leaf; no subagent dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Judged axis: **coverage**. Milestone: r40 claim attacks and evidence.
Tool installs/upgrades: none; `pacman` untouched; no network fetch performed.

Frozen claim read first: `census/round-40/preregistration.txt:10-12` (C3).
Base revision named by the preregistration and used throughout: `0242085909fb6a4ee041c5443d76316ac6d59d4b`
(`git rev-parse 0242085…^{commit}` resolves; `git rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`).
Lane `git status --short` after this seat: `?? census/round-40/` only (pre-existing untracked census area, left untouched).

## Explicitly distinct edge case (item 18)

**The scoring-contract edge: the r40 C3 kill verdict is *fixture-level*, so a mutant can be killed by a case that belongs to a different branch than the one the mutant targets — and, worse, a mutant the fixture genuinely detects can be scored as a SURVIVOR because the committed `score()` crash probe reads the wrong stream.**

Concretely, my edge is **kill attribution and kill-admissibility under the committed r39 C3 scoring contract**, not the semantics of any one branch. Peers in this wave attack the branch semantics themselves: `R40executor39` and `R40executor51` attack duplicate-`TOTAL` multiplicity/cardinality, `R40revenger36` attacks conflicting duplicate `TOTAL` rows (first-invalid/last-valid), `R40executor63` attacks the invalid-UTF-8 decode boundary, `R40revenger48` attacks decoder replacement of invalid UTF-8 in an otherwise valid record. None of those reports tests whether a *kill verdict* is attributable to the branch case that is supposed to cover the mutant. I test exactly that, plus whether the verdict can be wrong in either direction.

## Summary of findings

| # | Severity | Finding | Kind |
|---|----------|---------|------|
| **F1** | **HIGH** | A mutant the fixture genuinely detects can be scored **SURVIVED** by the committed `score()`, because the fixture echoes the *tool's* stderr (including its traceback) into the *fixture's* stdout and the crash probe scans the fixture's streams. | concrete falsifier |
| **F2** | **HIGH** | A kill is **not attributable to a branch**: the discovery-dead mutant is killed by the `unrecorded-default` case, while the `skip-unrecorded` case **passes** on it. The frozen C3 predicate names three branches but the receipt (`SUMMARY mutants=… killed=… survived=…`) carries no per-branch attribution. | concrete falsifier |
| **F3** | MEDIUM | The `--skip-unrecorded` case alone is **non-discriminating** for the discovery-dead mutant: with only that case present, the mutant survives. The branch needs a *paired* case. | concrete falsifier |
| **F4** | MEDIUM | The invalid-UTF-8 branch has a **fixture-side** failure mode: a mutant whose tool output carries an undecodable byte makes the *fixture* crash (text-mode `subprocess` decode) and the fixture then emits **no** `SUMMARY` — tripping the frozen "fixture has no own failure summary" kill condition for the wrong reason. | concrete falsifier |
| **F5** | LOW (positive) | The three branches are **genuinely uncovered** by every committed fixture at the base revision; a candidate fixture that adds them does kill branch-specific mutants, and the ablation shows each group is load-bearing. | positive control |

## F1 — HIGH: a detected mutant can be scored SURVIVED (kill-admissibility defect)

**Mechanism.** The committed r39 C3 counter scores a kill at `census/round-39/c3-counter.py:87-104`:

```
101:    crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)
102:    killed = proc.returncode == 1 and fails > 0 and not crash
```

`proc` here is the **fixture** process. The probe is meant to catch a *fixture* that crashes (the r38 A5 contract, `census/round-38/preregistration.txt:189-195`: "a kill now requires the fixture's own `SUMMARY … fail=N` with `N > 0` and no `Traceback` on either stream"). But the committed r39 fixture **echoes the tool's combined stdout+stderr into its own stdout**:

- `tests/fixtures/r39-drift-record-rules.py:76` — `out = proc.stdout + proc.stderr` (the *tool's* streams)
- `tests/fixtures/r39-drift-record-rules.py:79-80` — `results.append((name, ok, "… out=%r" % (…, out.replace("\n", " ")[:160])))`
- `tests/fixtures/r39-drift-record-rules.py:103-104` — same echo for the `crlf` case

So when the **tool** raises an uncaught exception, its traceback text is laundered through the fixture's own stdout and the counter's crash probe fires on it, scoring `killed=no` for a mutant the fixture *did* detect.

**Evidence A — committed r39 fixture, committed `score()`, one-character tool defect.**
Tool mutant: `if total is not None:` → `if totol is not None:` (NameError on every record with a TOTAL row).

```
K1  committed r39 fixture  x  TYPO mutant (tool NameError)
   committed score(): killed=no  [rc=1 fails=4 crash=True] cases=7
   fixture rc=1 own_summary=['SUMMARY cases=7 pass=3 fail=4'] failing_cases=4
   traceback marker present in fixture stdout+stderr: True

K2  CONTROL r39 fixture, BOTH echo sites neutralised  x  TYPO mutant
   committed score(): killed=yes [rc=1 fails=4 crash=False] cases=7
   fixture rc=1 own_summary=['SUMMARY cases=7 pass=3 fail=4'] failing_cases=4
   traceback marker present in fixture stdout+stderr: False
```

Same fixture bytes (`sha256 567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d`), same tool bytes, same mutant, same `fail=4` and same exit 1. The **only** difference is whether the fixture echoes the tool's output. The verdict flips `killed=no` → `killed=yes`. The false survivor is produced by the *diagnostic echo*, not by the fixture's assertions.

**Evidence B — end-to-end receipt from the committed counter's own `main()`.**
I ran `census/round-39/c3-counter.py`'s `main()` unchanged (only its `MUTANTS` tuple was replaced *in this scratch process*; the lane file was not touched) against a scratch r40-style candidate fixture, once with the committed echo convention and once with the echo neutralised:

```
### candidate fixture: ECHO (committed r39 convention)
MUTANT MA1 killed=yes base_killed=no rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
MUTANT MB1 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT MC1 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT MD1 killed=no  base_killed=no rc=1 fails=2 crash=True  base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=3 survived=1 pristine=ok base_killed=0 cases=12 tool_sha=e48ed08e6728 fixture_sha=eafc0e1e187d
   counter exit rc=1

### candidate fixture: NO-ECHO (control)
MUTANT MA1 killed=yes base_killed=no rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
MUTANT MB1 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT MC1 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT MD1 killed=yes base_killed=no rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=12 tool_sha=e48ed08e6728 fixture_sha=f805fd745ec6
   counter exit rc=0
```

MD1 is `.decode("utf-8","replace")` → `.decode("utf-8","strict")` — the *exact* invalid-UTF-8 mutant the frozen C3 branch is about, and the same mutant already identified as N4 in committed r39 evidence (`.ufo/waves/round-39/w1/W1MutDriftRules.md:90,124`). Under the committed echo convention the receipt reads `survived=1` and the counter exits 1; with the echo removed the identical battery reads `survived=0` and exits 0. **The frozen C3 verdict for the invalid-UTF-8 branch is decided by the fixture's diagnostic formatting, not by its assertions.**

Note this is *not* the r38 A5 stub scenario A5 was written for (a fixture that prints `=FAIL` + `SUMMARY` and then itself raises — `.ufo/waves/round-38/w2/W2RevHarm.md:132`). Here the fixture is healthy; the **tool** crashed; the fixture reported honestly (`fail=2`, exit 1, own `SUMMARY`); the counter still refused the kill.

**Consequence for the frozen claim.** `census/round-40/preregistration.txt:12` kills C3 if "any mutant survives". Under the committed scoring contract an r40 candidate fixture can satisfy every assertion, detect every mutant, print its own summary, and still be reported as `survived>=1` — because its own failure detail happens to quote the tool's stderr. The frozen predicate is therefore not decidable from the receipt as printed unless the counter's crash probe is scoped to the *fixture's own* traceback (e.g. probe the fixture's stderr, or the fixture's own frame, not the echoed tool output).

## F2 — HIGH: a kill is not attributable to the branch it is claimed to cover

The committed `score()` returns one boolean for the whole fixture (`census/round-39/c3-counter.py:103`). It records **which case failed** nowhere; the receipt line (`census/round-39/c3-counter.py:184`) is `SUMMARY mutants=%d killed=%d survived=%d pristine=ok base_killed=%d cases=%d …`. The frozen C3 predicate names three branches (`census/round-40/preregistration.txt:11`) but the receipt has no branch dimension.

**Measured attribution.** Candidate fixture case verdicts per mutant:

```
   pristine               killed=no  [rc=0 fails=0 crash=False]
        skip-unrecorded=PASS unrecorded-default=PASS utf8-in-name=PASS utf8-in-number=PASS
   MB1 flag-ignored       killed=yes [rc=1 fails=1 crash=False]
        skip-unrecorded=FAIL unrecorded-default=PASS utf8-in-name=PASS utf8-in-number=PASS
   MC1 discovery-dead     killed=yes [rc=1 fails=1 crash=False]
        skip-unrecorded=PASS unrecorded-default=FAIL utf8-in-name=PASS utf8-in-number=PASS
   MD1 strict-decode      killed=no  [rc=1 fails=2 crash=True]
        skip-unrecorded=PASS unrecorded-default=PASS utf8-in-name=FAIL utf8-in-number=FAIL
```

MC1 (`if not args.skip_unrecorded:` → `if False:` — discovery never runs) is counted `killed=yes`, but the failing case is **`unrecorded-default`**, a case that does not pass `--skip-unrecorded` at all. The `skip-unrecorded` case **PASSES** on MC1. So a receipt line `killed=4 survived=0` is consistent with a fixture whose `--skip-unrecorded` case never discriminates anything about the flag — the kill is silently credited to another branch's case.

## F3 — MEDIUM: the `--skip-unrecorded` case alone does not discriminate the branch

Removing only the `unrecorded-default` case (leaving the `skip-unrecorded` case):

```
== PAIRED-CASE TEST: fixture WITHOUT the 'unrecorded-default' case ==
   pristine               skip-unrecorded=PASS killed=no  [rc=0 fails=0 crash=False]
   MB1 flag-ignored       skip-unrecorded=FAIL killed=yes [rc=1 fails=1 crash=False]
   MC1 discovery-dead     skip-unrecorded=PASS killed=no  [rc=0 fails=0 crash=False]
   -> MC1 (discovery dead) is NOT distinguished by the skip case alone
```

The skip case observes `rc 0 / drift_rows=0` in the pristine world **and** in the discovery-dead world (nothing to discover), so it cannot distinguish "the flag works" from "discovery is dead entirely". The branch requires a **paired** case (`without the flag` + `with the flag`). The ablation below confirms the pairing is load-bearing in both directions.

## F4 — MEDIUM: the invalid-UTF-8 branch has a fixture-side failure mode

A second invalid-UTF-8 mutant, `.decode("utf-8","replace")` → `.decode("utf-8","surrogateescape")`, makes the **tool** emit a lone surrogate that its C-locale stdout encodes back to a raw `0xff` byte:

```
[ME1-surrogateescape] tool rc=1 stdout_bytes=b'DRIFT\tABSENT\tbe\xffta\trecorded regs=1\nDRIFT\tUNRECORDED\tbeta\tlive regs=1 prunable=0\nSUMMARY record=/fast/…'
      fixture text-mode decode of tool stdout: UnicodeDecodeError 'utf-8' codec can't decode byte 0xff in position 15: invalid start byte
```

The fixture invokes the tool with `text=True` (`tests/fixtures/r39-drift-record-rules.py:74`, `:100`), so the fixture's own `subprocess.run` raises. The fixture **crashes**, prints **no** `SUMMARY`, and the counter reports `NO-SUMMARY rc=1` (`census/round-39/c3-counter.py:99-100`). The frozen C3 kill list includes "fixture has no own failure summary" (`census/round-40/preregistration.txt:12`) — so this branch can trip a kill condition for a reason that is a *fixture harness* defect (text-mode decode of deliberately-invalid bytes), not a coverage gap. An r40 fixture that adds an invalid-UTF-8 case must read the tool's output as **bytes** (or with `errors="replace"`), or it will fail the frozen kill rule on its own harness.

## F5 — positive control: the branches are genuinely uncovered, and a good candidate fixture does kill them

**Lane-wide mutant × fixture matrix** (base revision `0242085…` bytes; committed fixtures `r36`, `r37disc`, `r38`, `r39`; `killed=yes` means the committed `score()` reports a kill):

```
== PRISTINE (base rev 0242085) ==
  CAND-r40scratch  rc=0 summary=['SUMMARY cases=12 pass=12 fail=0'] score_killed=False[rc=0 fails=0 crash=False] cases=12
  r36              rc=0 summary=['SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED'] … cases=12
  r37disc          rc=0 summary=['SUMMARY cases=6 pass=6 fail=0'] … cases=6
  r38              rc=0 summary=['SUMMARY cases=10 pass=10 fail=0'] … cases=10
  r39              rc=0 summary=['SUMMARY cases=7 pass=7 fail=0'] … cases=7

== MUTANTS ==
MUTANT MA1-dup-total-first-wins
   CAND-r40scratch  killed=yes [rc=1 fails=2 crash=False] failing_cases=['dup-total-conflict-then-valid', 'dup-total-valid-then-conflict']
   r36/r37disc/r38/r39  killed=no  (all)
MUTANT MB1-skip-unrecorded-noop
   CAND-r40scratch  killed=yes [rc=1 fails=1 crash=False] failing_cases=['skip-unrecorded']
   r36/r37disc/r38/r39  killed=no  (all)
MUTANT MC1-discovery-dead
   CAND-r40scratch  killed=yes [rc=1 fails=1 crash=False] failing_cases=['unrecorded-default']
   r36              killed=yes [rc=1 fails=2 crash=False] failing_cases=['unrecorded', 'live-repos-non-negative']
   r37disc          killed=yes [rc=1 fails=2 crash=False] failing_cases=['unrecorded-exact', 'unrecorded-unreachable']
   r38/r39          killed=no  (both)
MUTANT MD1-utf8-strict-decode
   CAND-r40scratch  killed=no  [rc=1 fails=2 crash=True] failing_cases=['utf8-in-name', 'utf8-in-number']
   r36/r37disc/r38/r39  killed=no  (all)
MUTANT MD2-utf8-ignore-decode
   CAND-r40scratch  killed=yes [rc=1 fails=2 crash=False] failing_cases=['utf8-in-name', 'utf8-in-number']
   r36/r37disc/r38/r39  killed=no  (all)
MUTANT ME1-utf8-surrogateescape
   CAND-r40scratch  killed=no  [NO-SUMMARY rc=1]
   r36/r37disc/r38/r39  killed=no  (all)
```

So: the duplicate-`TOTAL`, `--skip-unrecorded`, and invalid-UTF-8 branches are **not** covered by any committed fixture, and a candidate fixture that adds them does kill branch-specific mutants (MA1, MB1, MD2) while leaving every committed fixture's mutants surviving. This supports the frozen claim's premise. MC1 is the one exception worth flagging: it is already killed by the *older* `r36` and `r37disc` fixtures (cases `unrecorded`, `live-repos-non-negative`, `unrecorded-exact`, `unrecorded-unreachable`), so it is **not** a net-new coverage gap and should not be used as the branch's evidence mutant.

**Ablation — each case group is load-bearing** (whole `run_case(...)` blocks removed, committed `score()` re-run):

```
VARIANT full               MA1 killed=yes  MB1 killed=yes  MC1 killed=yes  MD2 killed=yes
VARIANT drop-dup-total     MA1 killed=no   MB1 killed=yes  MC1 killed=yes  MD2 killed=yes
VARIANT drop-skip-unrecorded MA1 killed=yes MB1 killed=no   MC1 killed=no   MD2 killed=yes
VARIANT drop-utf8          MA1 killed=yes  MB1 killed=yes  MC1 killed=yes  MD2 killed=no
```

Each group is the sole discriminator for its mutants — the fixture-side coverage is real, provided each branch has its own case (and, for `--skip-unrecorded`, a paired case per F3).

**Pristine branch behaviour at the base revision** (committed tool bytes, real git fixtures):

```
--- dup-total: two IDENTICAL TOTAL rows                       rc=0  SUMMARY … drift_rows=0
--- dup-total: valid TOTAL then conflicting TOTAL              rc=2  REFUSAL RECORD-MALFORMED: TOTAL repos=9 but 2 REPO rows
--- dup-total: conflicting TOTAL then valid TOTAL              rc=0  SUMMARY … drift_rows=0
--- skip-unrecorded: WITHOUT the flag (gamma unrecorded)        rc=1  DRIFT UNRECORDED gamma …
--- skip-unrecorded: WITH --skip-unrecorded                     rc=0  SUMMARY … drift_rows=0
--- utf8: invalid byte in a REPO NAME field                     rc=1  DRIFT ABSENT be�ta / DRIFT UNRECORDED beta
--- utf8: invalid byte in a numeric field                       rc=2  REFUSAL RECORD-MALFORMED: line 2 does not match the census schema
--- utf8: invalid byte in a comment line                        rc=0  SUMMARY … drift_rows=0
```

`tools/souji-worktree-drift.py:147` decodes with `errors="replace"`, so an invalid byte in a *name* field is silently replaced and the record is accepted (the repo then reads as `ABSENT`), while the same byte in a *numeric* field breaks the `$`-anchored schema and is refused. The docstring at `:44-60` names no refusal class for undecodable bytes, so "invalid UTF-8 record bytes" has **no documented expected verdict** — an r40 fixture must choose one and pin it.

## Bounded measurement plan for the r40 C3 counter (the falsifier to run)

Whoever measures r40 should run exactly this, at the candidate revision, with the r40 fixture as candidate and `tests/fixtures/r39-drift-record-rules.py` as the base arm:

1. **Declare the battery and the attribution map up front.** For each mutant, name the *case id* that must fail. Require the receipt to carry it (e.g. `MUTANT <id> killed=yes case=<case-id>`), not just a fixture-level boolean. Without that, F2 is undetectable.
2. **Scope the crash probe to the fixture's own execution.** The r38 A5 intent is "the fixture did not crash". Implement it as: run the fixture with the tool's output redirected away, or capture the fixture's stderr separately from the tool's echoed output, or probe for a traceback whose frames are all inside the fixture file. At minimum, re-check `crash` against the fixture's **stderr only** and confirm the counter still rejects the r38 A5 stub (`.ufo/waves/round-38/w2/W2RevHarm.md:132` records the stub's expected `killed=no rc=1 fails=1 crash=True`).
3. **Require the fixture to read the tool's output as bytes** for the invalid-UTF-8 branch (`text=False`, decode with `errors="replace"`), so the fixture cannot destroy its own summary (F4). Verify the fixture still prints `SUMMARY cases=… fail=…` for every mutant.
4. **Pair the `--skip-unrecorded` branch**: one case with the flag (expect `drift_rows=0`, no `UNRECORDED`) and one without (expect `UNRECORDED` + rc 1), and require the *skip* case — not the paired one — to be the discriminator for the flag-ignored mutant (F3).
5. **Pin the invalid-UTF-8 expected verdict** in the fixture's own docstring before writing the case (accepted-with-replacement vs refused), because the tool documents no class for it; then require the *strict-decode* mutant to be killed **without** a traceback in the fixture's own stream (F1) — a strict-decode kill that only shows up as `crash=True` is not a kill.
6. **Re-run the base arm** and require every mutant to survive `tests/fixtures/r39-drift-record-rules.py`; and confirm that no mutant chosen for the new branches is already killed by `r36-worktree-drift.py` or `r37-drift-discrimination.py` (MC1 is — see F5).

## Commands actually run

All lane reads were `read`/`grep`/`bash` against committed bytes; all scratch writes were under `/fast/scratch/hyaku/souji-r40/R40reviewer18` with `TMPDIR` set explicitly to the same path. No git/jj mutation, no index write, no commit, no push.

1. `read /home/vgpnk/.omp/agent/RULES.md` — read (tooling directive; no install needed).
2. `read …/souji-shokunin/census/round-40/preregistration.txt` — read the frozen C3 predicate.
3. `git -C …/souji-shokunin log --oneline -12; git status --short; git rev-parse --show-toplevel` → tip `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`, status `?? census/round-40/`.
4. `git show 0242085…:<path>` for `tools/souji-worktree-drift.py`, `tests/fixtures/r39-drift-record-rules.py`, `tests/fixtures/r38-drift-record.py`, `tests/fixtures/r36-worktree-drift.py` → scratch copies; `sha256sum` → tool `e48ed08e6728…`, r39 fixture `567c37a679f5…`, r38 fixture `ac0be0e7a49e…`.
5. `python3 -B mutants.py` — pristine control + 4-mutant battery against r39/r38/r36 committed fixtures (first pass, before the candidate fixture existed).
6. `python3 -B probe.py` — pristine behaviour of the three branches (dup-TOTAL orderings, skip flag on/off, invalid UTF-8 in name/number/comment).
7. `python3 -B score.py` — candidate fixture + committed `score()` per mutant, base arms r39/r38.
8. `python3 -B final.py` — lane-wide matrix over r39/r38/r37disc/r36 + candidate fixture, with per-case FAIL attribution.
9. `python3 -B counterfactual.py` — echo-vs-quiet isolation of the crash probe on the candidate fixture.
10. `python3 -B confirm.py` — per-case attribution table for MC1 and MD1.
11. `python3 -B false_survivor.py` — the same isolation on the **committed** r39 fixture (K1–K4).
12. `python3 -B kill_attribution.py` — K1–K4 with both echo sites neutralised as the control.
13. `python3 -B mechanism.py` — byte-level mechanism for ME1 (tool stdout carries raw `0xff`) and MD1 (tool stderr carries the traceback).
14. `python3 -B ablation.py` / `python3 -B ablation2.py` — block-aware case-group ablation (the first pass's regex over-removed blocks; `ablation2.py` is the precise run quoted above).
15. `python3 -B paired.py` — paired-case requirement for `--skip-unrecorded`, plus the crash-probe counterfactual.
16. `python3 -B receipt.py` — end-to-end receipt from the committed counter's own `main()` (its `MUTANTS` tuple replaced in-process only; lane file untouched), run with the echo convention and with the echo neutralised.
17. `grep -n "crash" census/round-39/c3-counter.py`; `grep -n "out=%r" tests/fixtures/r39-drift-record-rules.py tests/fixtures/r38-drift-record.py`; `grep -n "A5" census/round-38/preregistration.txt`; `grep -n "N4" .ufo/waves/round-39/w1/W1MutDriftRules.md` — evidence pointers quoted above.
18. `git status --short` (final) → `?? census/round-40/`; lane tracked files unchanged.

## Verdict

**Bounded falsifier against the frozen C3 claim, with the r40 candidate itself unmeasured.**

- **F1 (HIGH) is a concrete falsifier** of the frozen C3 measurement as it would be run with the committed r39 scoring contract: the receipt's `survived` count — the exact field the frozen kill rule reads — flips on whether the candidate fixture *echoes* the tool's stderr, with no change to any assertion, any mutant, or any exit status. The invalid-UTF-8 branch is the one that triggers it, because the natural mutant for that branch (`"replace"` → `"strict"`, already named N4 in committed r39 evidence) makes the **tool** raise. The counter's crash probe is aimed at the fixture but is satisfied by the fixture faithfully reporting the tool's crash.
- **F2/F3 (HIGH/MEDIUM) are concrete falsifiers** of the "coverage" reading of the claim: a `killed=… survived=0` receipt is achievable while the `--skip-unrecorded` case discriminates nothing, and that case alone cannot discriminate the discovery-dead mutant without a paired case.
- **F4 (MEDIUM)** is a concrete falsifier of a *naive* r40 fixture design: adding an invalid-UTF-8 case to a text-mode harness makes the fixture lose its own `SUMMARY`, tripping the frozen "fixture has no own failure summary" kill condition for a harness reason.
- **F5** confirms the claim's premise: the three branches are genuinely uncovered at `0242085…`, a well-formed candidate fixture does kill branch-specific mutants, every committed fixture's mutants survive, and each branch's case group is the sole discriminator for its mutants. The frozen claim is sound in substance; the defect is in the **instrument** that would certify it.

**Not claimed:** no r40 counter, r40 fixture, r40 mutant, or r40 receipt exists in the lane (`census/round-40/` contains only `preregistration.txt`), so pristine-pass, candidate-mutant-killed and base-mutant-survive are **unverified, not pass** for r40. The scratch candidate fixture used here is my own construction, not an r40 artifact; it exists only to make the attribution and kill-admissibility properties measurable against the committed `score()`. The r40 fixture author may legitimately choose a different byte-level design, in which case F1's *trigger* disappears — but F1's *class* (a fixture-level kill boolean plus a crash probe that reads the tool's diagnostics laundered through the fixture) is a property of the inherited contract, not of any one fixture.

**No frozen claim was altered; no production file was written.** The only lane write is this assigned report at `.ufo/waves/round-40/w1/R40reviewer18.md`. Scratch was confined to `/fast/scratch/hyaku/souji-r40/R40reviewer18` and is removed before yield.
