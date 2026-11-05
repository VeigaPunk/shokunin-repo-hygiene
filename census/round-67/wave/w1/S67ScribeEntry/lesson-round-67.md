# Draft — `corpus/lessons/round-67.md` skeleton (round 67, seat S67ScribeEntry)

**STATUS: the lesson was landed by the L1 before this seat delivered** (commit
`e41f022f0dd018390fa68c7edab1dff734fcfc4f`, 2026-11-05 13:48:45 -0300; the lesson file is
`corpus/lessons/round-67.md`, 97 lines added). The landed lesson carries `## Gate`, `## Claims`,
`## Mistakes` (M1–M10), named limits, a sweep and verdicts.

What this file delivers is therefore: (a) the **skeleton shape** the seat was asked for, mapped onto the
landed sections so the L1 can see what is already covered and what is still a placeholder; (b) the two
**known L1 mistakes** as the seat was asked to record them, each with this seat's independently re-measured
evidence; and (c) the **two corrections** the landed lesson still owes (the "65 hex" narrative mismatch and
the S298 `used-by` log line).

---

## 1. Skeleton shape, mapped onto the landed lesson

```
# Round 67 — <title>
   [landed: "value-checked GIT_COMMON_DIR (C1 operability) and the redirect-claim marker check (C2 calibration)"]

Attempt 1. Base <40-hex>. Freeze <40-hex> (attempt 4; attempts 1-3 kept in history).
Landed writer <40-hex> (sha256 …). Measured records: census/round-67/records/.
   [landed]

## Claims
   C1 operability … / C2 calibration …   (frozen predicates, quoted not restated)
   [landed]

## Gate
   - Sources opened this round.  … located quotes, per-capture digests, the match test.
   - Admitted … / Rejected inside the entry …
   - Sourced claim (frontier step, CORPUS.md §2b item 4).
   - Census. Before / after, with the command.
   - Assimilation: none.
   - Probes (scratch; not claim evidence).

## Mistakes
   M1 … M10 (table: class | evidence pointer | captured-by | fix)

## Sweep / Named limits / Verdicts
```

Every section the seat was asked for is present in the landed file. The two known L1 mistakes are M1 and M2
there; the wave seats' rows are M3–M10.

---

## 2. The two known L1 mistakes

### M-candidate 1 — the attempt-2/3 digest transcription failures (class: number-drift)

**Evidence pointer**
`census/round-67/preregistration-attempt{2,3}.txt` + the freeze-check `POPULATION-DIGEST` findings.

**Captured by:** the freeze checker (on attempts 2 and 3).

**Fix:** programmatic digest derivation in attempt 4.

**Re-measured by this seat** (read-only `git show` at each freeze commit, plus a whitespace-collapsing
byte matcher against the measured digest of the committed matrix blob):

| attempt | commit | C1 Population digest length | relation to the true 64-hex digest |
|---|---|---|---|
| 1 (`preregistration.txt`) | `832a4d43` | **63** | truth minus the `f` at index 39 |
| 2 (`preregistration-attempt2.txt`) | `b3aa70fe` | **63** | same 63-hex string as attempt 1 |
| 3 (`preregistration-attempt3.txt`) | `d874bf0d` | **62** | truth minus `1f` at index 40 |
| 4 (`preregistration-attempt4.txt`) | `4c61efcb` | **64** | `5d26b341e4718ba1dc62b8bec2d6ba0d29fafdcf1fdb302d1435736cd976a692` = the measured `sha256sum` of the committed matrix blob |

Freeze-checker output, reproduced by this seat in a scratch clone at each attempt commit:

```
attempt 2: FINDING C1 POPULATION-DIGEST census/round-67/c1-matrix.tsv has no sha256=<64 hex> in '…9fafdc1fdb302…a692'
            SUMMARY claims=2 findings=1    EXIT=1
attempt 3: FINDING C1 POPULATION-DIGEST census/round-67/c1-matrix.tsv has no sha256=<64 hex> in '…9fafdcfdb302…a692'
            SUMMARY claims=2 findings=1    EXIT=1
attempt 4: SUMMARY claims=2 findings=0    EXIT=0
```

At attempt 1 the checker prints **two** findings — the digest **and**
`C2 CONTROL-ADDED-NOT-BEFORE-FREEZE` (the C2 controls landed in the same commit as the attempt-1 file).

**Correction this seat recommends the L1 add to M1.** The landed M1 row states the attempt-2 length as **63
hex** and the attempt-3 length as **62 hex** — this seat's measurement confirms both exactly. But the frozen
preregistration headers state something different, and they are frozen, never edited:

> attempt-3 header: "the stated matrix sha256 carried a transcribed extra character (**65 hex**, rejected by the
> freeze checker POPULATION-DIGEST)"
> attempt-4 header: "attempt 2 transcribed **65 hex** and attempt 3 transcribed 62 hex by hand"

The committed attempt-2 blob carries **63** hex, not 65, and both transcriptions are **deletions** of truth
characters, not an "extra character". So the frozen narrative of the defect mis-states the length by two hex
digits and mis-states its direction, while the lesson's own numbers are right. The record does not reconcile the
two. **Recommended lesson note (not a prereg edit — the prereg is frozen):**

> M1 addendum: the frozen attempt-3 and attempt-4 headers describe the attempt-2 defect as "65 hex, a
> transcribed extra character"; the committed attempt-2 blob carries **63** hex and is the true digest with the
> `f` at index 39 deleted (a deletion, not an extra character). The M1 row's lengths (63 / 62) are the measured
> ones. The attempt-3 blob is the true digest with `1f` at index 40 deleted. The frozen headers are not edited.

**Second correction this seat recommends (chronology sweep).** `git log --all -- census/round-67/preregistration-attempt2.txt`
returns two commits: the landed `b3aa70fe` and **`5b57138076b7de3410aa9bce1ce83959e60eb94e`** (parent
`832a4d43`, 2026-11-05 13:28:31 -0300), which is **not an ancestor of `master`** and is in no branch. Its
attempt-2 blob also carries 63 hex (not a different digest variant) — it is a stray pre-landing attempt-2
commit. It is unreachable from any ref and cannot affect the freeze, but it is unreferenced history that a
reader of `--all` meets. The lesson's sweep, which is meant to account for the round's chronology, does not
mention it.

---

### M-candidate 2 — the first m10-s5 selftest case was vacuous on `redirects_closed` (class: survivor)

**Evidence pointer**
`census/round-67/probes/l1-w2-repro.md` **P4**.

**Captured by:** none — the catch was running the reverted-rule recipe pre-freeze.

**Fix:** the frozen case binds `env_closed`, and the recipe run is now part of instrument building.

**Re-measured by this seat.** The frozen C2 counter's own selftest, and the reverted-rule mutant built from the
frozen bytes by the frozen recipe `census/round-67/c2-mutate.py`, both run in this seat's scratch clone:

```
declared counter   --selftest : SELFTEST pass cases=17 fail=0                        EXIT=0
reverted-rule      --selftest : SELFTEST-CASE m10-s5-assertion-line-not-live:
                                  findings=0 want=1 MISMATCH
                                  SELFTEST pass cases=17 fail=1                       EXIT=1
```

**The vacuity is reproducible and its shape is exactly as P4 records.** The frozen counter's own comment on the
case says it outright (counter source, the `m10-s5-assertion-line-not-live` entry):

> "The claim is env_closed, NOT redirects_closed: a cdred-requiring claim would fail on the stub's absent cdred
> marker regardless of the token rule — the exact vacuity shape the round-66 case suffered (bound to an outcome
> its mutation cannot move; caught by this lane's own pre-freeze mutant run, round-67 lesson)."

That is the same defect class as the round-66 M4 (the r66 case `m10-returncode-line-not-live` bound row s3, whose
finding came from a missing SKILL sentence rather than the marker read, so reverting the token repair left
`--selftest` at 14/14). The r67 case binds a row whose outcome **depends on the token rule**: the writer stub
carries the env needles only on `r.returncode` assertion lines (no `refuse(`, no return-literal), the SKILL blob
resolves the statement, and the claim `env_closed` needs both env markers live. Repaired rule → dead → finding;
reverted rule → live → no finding → the case MISMATCHes. The mutant run in the table above is the witness that
the guard is not vacuous.

**Second re-measurement (the enum half of the same M-candidate's claim family).** The `enum-weakened` mutant,
built by the same frozen recipe and run at the pinned historical state `c13fbb4e`:

```
MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=1 envred=1 cdred=0
SUMMARY rows=5 findings=0 verdict=PASS rev=c13fbb4e1b563a78278ddc14316c20252e9a6d8d    EXIT=0
```

against the declared counter at the same state:

```
FINDING SCOPE-OVERREACH s5: stable wording: claim redirects_closed needs writer markers cdred; writer blob lacks them
SUMMARY rows=5 findings=1 verdict=FAIL rev=c13fbb4e1b563a78278ddc14316c20252e9a6d8d    EXIT=1
```

So the finding is enumeration-driven, not a hardcoded string — the second half of the frozen C2 kill-power target.

---

## 3. Placeholders for wave seats to fill

The landed lesson already carries the wave seats' rows (M3–M10). This seat's item was to leave placeholders
for seats still to report; the seat's own findings are the two above. The template the seats' rows took:

```
| M<n> | <class>: <one-line defect statement> | <committed evidence pointer: path + the command that produced it> | <who captured it: the seat, or "none"> | <the fix, or "not fixed this round; routed to round 68"> |
```

Note the r66 lesson's mistake-table convention, which the landed r67 lesson follows: `captured-by` names the
**seat or tool** that caught the defect, and a defect caught by nobody reads `none` — the r67 M2 row does exactly
that ("none in the lane; caught by running the `c2-mutate.py reverted-rule` recipe before any commit"), and the
r66 M2 row names "none (the critic found it, not the L1)".

---

## 4. The Gate section the seat was asked to shape

The seat's item: "## Gate section placeholder listing the round's candidates (S300 admit; the s5-scope rejection
carried from r66)".

The landed Gate carries, in order: sources opened this round (S300 with its two located quotes and the
whitespace-normalization note); admitted (S300, tier A, scope common-dir resolution); rejected inside the entry
(two claims: "git scrubs `GIT_COMMON_DIR` for every child process" — not established, since `local_repo_env[]`
shows membership, not a universal child scrub; and "a relative value is canonicalized against the writer cwd,
the same rule git applies" — the prereg L2 wording, which the probes contradict); the sourced claim (frontier
step); the census (222 → 223 rows, rc 0); assimilation (none); and the scratch probes (PK3, the relative-value
probe, the W2 mechanism re-run).

**The s5-scope rejection carried from r66** is the second of those two rejections: the r66 lesson's M5 recorded
that the s5 statement overreached ("closed for the caller-injected config and object-redirect routes" as a
universal claim) and routed it to r67; the r67 counter now scores exactly that overreach as
`FINDING SCOPE-OVERREACH s5` at the pinned state. The landed Gate's "Rejected inside the entry" bullet records
it as a rejection from the **entry's** claims, and the lesson's M4/M5 rows carry the mechanism.

### 4.1 What the Gate still owes (this seat's findings)

1. **The S298 `used-by` log line.** The correction the registry gate demands (see `sources-rows.md` §3) makes
   the sentence in **`corpus/README.md:990`** false — the r67 frontier section's sources bullet reads *"S300
   added (…, rc 0, 223 rows). **S298/S299 unchanged.**"* `SOURCES-CONTRACT-v1` rule 2 requires the old→new to
   be logged in the round lesson; the landed LOG entry already has a **"Corrections (append-only; the frozen
   files are not edited)"** bullet, which is its natural home. The lesson must carry: *S298 `used-by`:
   `corpus/knowledge/caller-env-routes-receipt-writer.md` →
   `corpus/knowledge/caller-env-routes-receipt-writer.md, corpus/knowledge/common-dir-route-receipt-writer.md`.*
2. **The one quote row whose stated offset does not reproduce raw** (`environment.html` @ 189753 → 189853,
   delta 100). The Gate already says the match test is whitespace-normalized; naming the one row that differs
   by 100 bytes raw closes the disclosure.
3. **M1's addendum** about the frozen headers' "65 hex" (§2 above).
4. **The dangling pre-landing commit `5b571380`** in the chronology sweep (§2 above).

---

## 5. The rest of the landed lesson, checked by this seat

* `## Claims` restates the two frozen predicates without widening them (C1: value-check, mismatch/empty refuse
  `RECEIPT-ENV-COMMONDIR-MISMATCH`, equal value accepted (W3); C2: exactly one `SCOPE-OVERREACH s5` at the
  pinned state, r66 counter `findings=0`).
* `## Named limits` and `## Verdicts` are present; the relative-value trade is routed to the operator and is
  **not** counted as an improvement without that ruling — which matches the r66 precedent of naming a trade
  rather than folding it into the verdict.
* The landed lesson's trend statements carry **no** score change (calibration 7, coverage 8, operability 8),
  consistent with the frozen claims' axes.

**Not restated here:** the two claims' predicates, the counters' target literals, and the wave seats' rows
M3–M10. Those are committed bytes; this seat did not write them and does not paraphrase them.
