# R43critic03 — claim-sizing findings

Axes: C1 calibration (self-assessment truth); C2 operability (runnable freeze gate); C3 coverage (new behavioural edge classes). Read-only instrument review; no candidate execution, admission decision, or instrument edit. Frozen instruments remain untouched.

## C1 — do-nothing red, but wrong correction values can reach the target

**Control checked:** `census/round-43/controls/c1-donothing.txt` prints `required=3 registered=0 missing=3 ... rederived=0 ... new_mismatches=0`. The corroborating `controls/c1-resume-before.txt` records the command at pinned master `13de0e84b45efd1113f077d58fc1e89bc586a013`, the same SUMMARY, and `EXIT=1`. Correct reason: three absent corrections, not a refusal or unrelated mismatch. Do-nothing does not satisfy the predicate.

**Cheapest partial-work control:** leave SCORECARD and the required register unchanged; create only the three column-zero correction lines copied from `tests/fixtures/r43-correction-prose.py:45-51`. This supplies the correction bookkeeping, not broader narrative or a new counter. One copied line alone reaches `registered=1` and, if the frozen re-derivation succeeds, `rederived=1`; three honest lines are the fixture's declared all-target control (lines 74-77). No new run was made here.

**Counterexample attacking correction truth:** in those three lines replace each `derived=` token with `derived=WRONG`, retaining all other fields. The parser captures `derived` at counter line 240, but the equality at 248 checks only `(path, field, stale, crev)`. Line 253 invokes `rederive` with the required register row, not the correction's captured value. Consequently wrong declared values take exactly the honest lines' scoring path. **[INFERENCE, source-proven branch equivalence; not executed]** They can reach the same target while the self-assessment says the wrong thing. This is a fixable instrument defect, not an acceptable calibration/operability tradeoff. Smallest safe correction for a future instrument version: bind the correction's `derived` to the frozen required value before registration/re-derivation. For this frozen round: disclose the defect and independently compare every landed correction's declared value; do not claim the counter verifies that comparison.

**Axis sizing:** calibration is the right surface, but the instrument reads a deliberately narrow correction language, not unrestricted prose. `RETRACT-CORRECTION id=...` is detected; the ordinary-language retraction used by the r42 fixture (`The line=14 correction above is retracted.`) is not a generic language-understanding capability. Also, removal of the old `rewritten` check is not proof that append-only history is now enforced: lines 265-283 only inspect mismatches after the base line count. Preserve those limits in the report.

## C2 — baseline red for genuine grammar gaps; memorizer rejection has false provenance

**Control checked:** `census/round-43/controls/c2-before.txt` reports `newtable=2/9 r42table=ok hidden=RED hidden_ctrl=REJECTED real=RED selftest=ok tmpdir=ok`. Seven visible failures name the claimed holes: first bad duplicate loses BASE evaluation; malformed heading drops its key; zero-padded/fullwidth Round falsely clean; Control symlink falsely clean; Control/prereg edits falsely clean. Correct do-nothing-red reason already follows from those seven visible mismatches, regardless of the unexplained `real=RED`. The receipt contains no command, revision header, or EXIT line; do not infer the reason for `real=RED` from it.

**Cheapest partial-work control:** unchanged r42 tool already reaches r42 retention, selftest, TMPDIR fallback, and 2/9 new cases. A first-wins-only repair should add the `dup-key-first-bad` case without closing the six other failing classes. **[INFERENCE; no candidate built/run.]** Thus individual green legs are not evidence of the whole operability claim.

**Counterexample attacking `hidden_ctrl=REJECTED`:** the generated memorizer starts with `import hashlib, sys` (c2-counter line 310) but calls `os.path.exists(path)` at 317 without importing `os`. Every ordinary hidden scenario supplies a nonempty path. The stub therefore raises NameError before using its memorized answers. The audit reads those wrong exits as scenario failures; the outer counter accepts any nonzero audit exit as rejection (349-350). **[INFERENCE from the generated source and audit branches; not executed.]** Rejection cannot currently establish that held-out variation defeats a functioning memorizer. Candidate `hidden=ok` remains a separate meaningful arm; this defect does not make do-nothing all-target. Smallest safe future correction: import `os` and establish that the control first answers all visible cases before testing its hidden failure. Frozen-round action: disclose the negative-control defect, not repair the committed instrument.

**Axis sizing:** operability is appropriate for the runnable gate and explicit grammar changes. Nine visible and ten fixed held-out scenarios do not dispose of the entire 30-survivor part-A mutation set. The inherited r42 patch legs retain their API/environment-sensitive limitations.

**Provenance distinction:** `c2-before.txt` is committed at pinned master, but absent from `git ls-tree f8c805db...` for that path. It must not be described as a receipt present in the instruments commit. The three inspected counter blobs are identical at that commit, pinned master, and the inspected working files.

## C3 — baseline red, but history and load-stability predicates are incomplete

**Control checked:** `census/round-43/controls/c3-donothing.txt` reports `killed=0 survived=16 ... cases=0 ... n10_before=no-fixture n10_after=no-refusal rc=1 ... shim=FAIL ... anchors=ok population=ok`. Correct red reasons: absent new fixture and no N10 refusal. `prior=0/9` is NOT evidence that nine old fixtures fail: counter lines 337-359 skip the entire prior-fixture arm when the new fixture is absent. The receipt has no outer EXIT line; `rc=1` belongs to `n10_after`, not an independently recorded counter exit.

**Cheapest partial-work controls:** fixture-only work can improve kill/case legs but leave the direct N10 refusal red. Conversely a tool-only pre-resolution leaf-symlink refusal can improve `n10_after` while leaving the absent-fixture kill/case/shim legs red. **[INFERENCE; neither control executed.]** Each is narrower than completing C3. The do-nothing receipt already satisfies anchors, population, zero crashes/timeouts/equivalent kills, and stderr discrimination without coverage work.

**Counterexample attacking before/after provenance:** `n10_before` becomes `base-receipt` solely when the candidate tool hash differs from the pinned hash (lines 298, 323); the candidate fixture is then never tested on pinned bytes. Moreover `target` at 408-410 does not test `n10_before` at all. A new fixture that never had the required exactly-one-failure pinned behaviour therefore receives the history label without evidence for that fixture. **[INFERENCE; source-level missing dependency, not an executed all-target candidate.]** Smallest safe future correction: run each submitted fixture against the pinned tool, require precisely `case-json-symlink-leaf`, and include that result in the predicate. Frozen-round action: obtain and cite a separate candidate-specific pinned-byte receipt; the automatic label is not that receipt.

**Counterexample attacking load-stable coverage:** oldscore returns `timed-out` at 373-374, but only `KILL` is accumulated at 379. Those timeouts never contribute to target `timed_out`. This can make `old_killed=0` look like survival when old fixtures were inconclusive. Separately, `PRE42` is defined but unused: the loop tests all nine PRIOR fixtures, not the eight stated for `old_killed` in the docstring (25). Correcting the old timeout tally and aligning the advertised population are future-version fixes, not changes seats may make now. Explicit timeout handling in candidate-mutant runs is an improvement, but it does not establish general load robustness for all arms.

**Axis sizing:** coverage is appropriate for sixteen behavioural survivor classes plus the leaf-symlink class, not a claim that the drift tool is now exhaustive. S42 remains explicitly race-only and unscored. Invocation-count shim and EQUIV guard are not by themselves proof that every reported case checks behaviour (r42 N-C3a remains a relevant named limit).

## Routed items not disposed of — report lines owed

Against `corpus/lessons/round-42-verifier-spotcheck.md:161-175`:

1. **Item 1, R1:** no r43 claim versions or retires the unsatisfiable r1-counter predicate. Record retirement/reason or explicit outstanding status; do not count the already-green landed repair as an instrument fix.
2. **Item 2, load stability:** C3 partially addresses outer timeouts and traceback attribution; oldscore timeout accounting and inner/load-sensitive fixture readings remain unclosed. Report scoped evidence, not general load stability.
3. **Item 3, C1:** correction grammar, fences and boundary counting are addressed in intent; ordinary prose/marker handling and append-only enforcement are not generally disposed of. The captured-derived defect above specifically blocks a broad truth-verification reading.
4. **Item 4, C2:** the named nine-case grammar holes are targeted, but the full 30 part-A survivor inventory is not enumerated as disposed of. Retain a coverage-limit line and the inherited patch-leg limitations.
5. **Item 5, S259:** none of C1-C3 supersedes/narrows the registry row or supplies the missing `using/cmdline` authority. A source-disposition/report line is still owed.
6. **Item 6, run-11 results:** historical missing results.json remains a disclosed evidence limitation; the spotcheck explicitly requires no new action beyond the note.

## Exact observation commands and outputs

All paths below are absolute in the executed calls. `read` is the file-reading tool, not a shell command; it returned the cited numbered source lines and receipt contents. No counters, fixtures, scoring clones, other runtimes, tests, or installs were invoked. No scratch directory was created, so none remains to remove.

Read calls (prefix `/home/vgpnk/Projects/shokunin/souji-shokunin/`):

- `read census/round-43` (directory inventory).
- `read census/round-43/c1-required.tsv:1-70`; `read census/round-43/c2-cases.tsv:1-70`; `read census/round-43/c3-survivors.tsv:1-70` → three required correction rows, nine gate rows, sixteen survivor rows respectively.
- `read census/round-43/c1-counter.py:1-120` and `:140-298` → grammar, captured-but-uncompared derived token, final predicate quoted above.
- `read census/round-43/c2-counter.py:1-130` and `:275-408` → normative grammar, stub source, negative-control acceptance and final predicate quoted above.
- `read census/round-43/c3-counter.py:1-130`, `:250-425`, `:133-248` → frozen anchors, skip branches, n10 history label, timeout and target branches quoted above.
- `read census/round-43/c2-hidden-audit.py:1-100` and `:107-172` → ten fixed scenarios and nonzero-on-failed-scenarios audit.
- `read census/round-43/controls/c1-donothing.txt:1-50`; `read census/round-43/controls/c2-before.txt:1-80`; `read census/round-43/controls/c3-donothing.txt:1-60`; `read census/round-43/controls/c1-resume-before.txt:1-30` → exact baseline SUMMARY fields reported above.
- `read corpus/lessons/round-42.md:1-180` and `:181-244`; `read corpus/lessons/round-42-verifier-spotcheck.md:1-180` → Named limits, wave-3 outcomes and six routed items.
- `read tests/fixtures/r43-correction-prose.py:1-85` and `:86-119` → honest three-line control and ten discrimination scenarios; no false-derived scenario present in that list.

Shell commands run, all read-only:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 census/round-43/c1-counter.py census/round-43/c2-counter.py census/round-43/c3-counter.py census/round-43/controls/c1-donothing.txt census/round-43/controls/c2-before.txt census/round-43/controls/c3-donothing.txt
```

Observed blobs: c1-counter `7eff5b00a030674d9c17012d81f4e97ecd3a6612`; c2-counter `09bd4580be0717eabf8e514c39c00e9854d049df`; c3-counter `5429d5d9fd1752a34b900035770af6d81e9ab4ed`; c1-donothing `0f3ec4aa53fa3b9b90b763e44a78e3dfe1578ff5`; c3-donothing `fe387e59fb8a57fbf6ece77de77f66da062ffa21`. No c2-before entry.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin hash-object /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c1-counter.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c2-counter.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c3-counter.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/controls/c2-before.txt
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree 13de0e84b45efd1113f077d58fc1e89bc586a013 census/round-43/controls/c2-before.txt census/round-43/c1-counter.py census/round-43/c2-counter.py census/round-43/c3-counter.py
```

Observed: both commands identify the same three counter blobs above and c2-before `cb0ad1de4168667dbacf092eb94f16d8fc705ebf`. All three shell calls completed successfully. Additional tooling reads: `read skill://godspeed`, `read skill://agent-self-evaluation`; scoped `glob` for `.../.ufo/waves/round-43/w1/R43critic03*` returned no files before report creation.

**Review verdict:** all three do-nothing controls are red for substantive target deficits; none proves all-or-nothing work. C1 declared-value binding, C2 functioning-negative-control provenance, and C3 candidate-specific before evidence are fixable defects requiring frozen-round disclosure, not seat edits. Runtime reachability claims above are explicitly unrun, not passes.

Self-check: accuracy 4 (source-backed, runtime predictions unexercised); completeness 4 (all requested claims/routes covered, partial controls described rather than run under critic constraint); clarity 4 (separates receipt facts from inferred branches); actionability 4 (smallest future fixes plus frozen-round dispositions); conciseness 4 (command ledger adds length). Overall 4.0; highest-impact follow-up is independent execution of the bounded controls by an authorized measurement seat, without changing frozen instruments.
