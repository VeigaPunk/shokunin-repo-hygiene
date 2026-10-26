# SwarmScribe28 — Q60/Q61/Q62 criteria and gate-registry rows (r29 w1)

## Status
STATUS: PASS — both deliverables are written merge-ready: three QUALITY.md criteria with a
runnable check cell each and three `SKILL.md` gate-registry rows in the file's existing 8-column
shape. Every check command in the criteria executes as written (Q60/Q61/Q62 run by this seat;
one further fixture arm run by this seat), and the one gate-map defect found — the frozen counter
has no exit code 2 — is written into its row rather than smoothed over. No lane file other than
these two was written; no tool installed; scratch removed.

## Evidence

Lane revision for every read: `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (HEAD at start and at
finish); base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; `git -C <lane> status --porcelain`
shows only the pre-existing ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`, which I did not touch.

1. **Shape sources.** `corpus/QUALITY.md` ends at `:143` (Q59) under `## Round 25 criteria`
   (`:137`), whose header row at `:139` is
   `| id | criterion | applies to | check | motivating evidence |`; `SKILL.md:167` opens
   `## Gate registry`, its last row is `souji-pre-report-gate` at `SKILL.md:224`, followed by
   `Sources for this skill:` at `:225`. No row in SKILL.md mentions
   `souji-registry-agreement`, `souji-wave-evidence-capture`, or any `r28-`/`r29-` fixture
   (`grep -n` over SKILL.md → no match).

2. **Q60 checker (executor's literal, re-run here).**
   ```
   $ python3 -B -c '<Q60 script from deliver-q60-q62-red-before.tsv:8>' <lane> 691dd29211c53d0ef94fa072394cb9c8a69fe92e 28
   Q60 clauses=1 readings=0 unread=1
   UNREAD S119 138
   rc=1
   $ ... <lane> b8cb4b31ce80e2e3314b88e85d40ea9873180804 29
   Q60 clauses=0 readings=0 unread=0
   rc=2
   ```
   Matches the recorded `base_result` (`deliver-q60-q62-red-before.tsv:8`). The repaired arm
   `clauses=1 readings=1 unread=0`, rc 0 at `69b06858c4f327e443cf03167be01abef6fc78fa` is that
   seat's record (evidence-verified, not re-run). r28 clause read back from bytes:
   `git show 691dd29…:census/round-28/records/preregistration.txt` →
   `(the three POSIX rows; S119 row, if appended, is not counted in this claim)`.

3. **Q61 command run here.**
   ```
   $ python3 -B census/round-29/c2-counter.py --root <lane> --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
   r26 records=1382 failed=152 uncovered=14 floor_violation=0
   r27 records=124 failed=0 uncovered=0 floor_violation=0
   r28 records=75 failed=0 uncovered=0 floor_violation=0
   SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804
   rc=1
   $ python3 -B census/round-29/c2-counter.py --root . --rev deadbeef
   COULD-NOT-EVALUATE rev must be a full 40-hex revision        (stderr; rc=1)
   ```

4. **Q62 command run here.**
   ```
   $ python3 -B tools/souji-registry-agreement.py --root <lane> --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
   ... K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md ...
   SUMMARY k1=6 k2=4 mismatches=10 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804   rc=1
   $ ... --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
   COULD-NOT-EVALUATE stale list 691dd29…:census/round-29/stale-statements.tsv unreadable   rc=2
   $ ... --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
   SUMMARY k1=6 k2=4 mismatches=10   rc=1
   ```

5. **Capture fixture arms run here** (delivered tool sha256 `3db37453e0fd…`,
   md5 `d00c545fcd2be2aecf93319e1f4a7c7f`; fixture sha256 `700e202b5907…`; both runs
   `SOUJI_R29_C2FIXTURE_BASE` under this seat's `/var/tmp/souji-r29-SwarmScribe28/`):
   `cases=12 pass=12 control=TAMPER-REJECTED`, exit 0 against the v2 tool; red arm
   `SOUJI_CAPTURE_TOOL=tools/souji-wave-evidence-capture.sh` (committed base v1) →
   `cases=12 pass=6 control=TAMPER-REJECTED`, exit 1.

6. **Registry fixture** `cases=12 pass=12 control=FALSE-GREEN-REJECTED` (red copy `pass=9`) is
   `SwarmExecutor01`'s recorded run of `deliver-r29-registry-agreement-fixture.py` (sha256
   `eea7388922b1…`); not re-run here because its scratch root is hard-coded to
   `/var/tmp/souji-r29-C1Fixture`, outside this seat's scratch namespace.

7. **Post-write validation of the delivery.** Each new QUALITY row parses as exactly 5 columns and
   each gate row as exactly 8 (`re.split(r'(?<!\\)\|', …)`); the Q60 cell was extracted back out of
   the delivery, its `\|` unescaped, run, and reproduced `Q60 clauses=1 readings=0 unread=1` /
   `UNREAD S119 138`, rc 1.

8. **r26 uncovered reconciliation** (read-only, `git ls-tree`/`cat-file` at `b8cb4b31…`):
   `census/round-26/waves/` holds 14 mode-`120000` entries, none with a manifest record, and two
   newline-named regular files whose GNU-escaped records exist. 14 uncovered is what the counter
   reports.

## Findings

1. **The frozen counter is called a gate but defines no code 2.**
   `census/round-29/c2-counter.py:16-20` (`git()` → `raise SystemExit('COULD-NOT-EVALUATE git …')`
   at `:20`) and `:34` (`raise SystemExit('COULD-NOT-EVALUATE rev must be a full 40-hex revision')`)
   both exit **1**, the same code as a measured failure; measured above. The docstring (`:12`) states
   only `0 … ; 1 otherwise`, so this is a gate-map gap, not a mis-stated contract. Written into the
   `r29-c2-counter` row verbatim ("no code 2 exists") so a reader cannot mistake could-not-evaluate
   for a red measurement. No predicate, target or case set was proposed for change (claims frozen).
2. **The registry check is revision-dependent.** The stale list `census/round-29/stale-statements.tsv`
   is introduced by the preregistration commit, so at `691dd29…` the bare Q62 command exits 2
   (`COULD-NOT-EVALUATE stale list … unreadable`); C1's declared form already carries
   `--list-rev <prereg-commit>` (`census/round-29/records/preregistration.txt`, C1 line) and the
   Q62 cell records the same caveat. Location: `tools/souji-registry-agreement.py:104-105`
   (`--list-rev` default = `--rev`; `--stale-list` default `census/round-29/stale-statements.tsv`).
3. **A prior round's citation over-counts by one.** `corpus/lessons/round-28-verifier-spotcheck.md:80`
   says "15 tracked r26 receipt paths (symlinks …) carry no manifest record"; the committed tree at
   `b8cb4b31…` has exactly 14 mode-`120000` entries under `census/round-26/waves/`, and the frozen
   counter reports `uncovered=14` for r26. `deliver-c2-history.tsv` records `touches_waves=no` for
   `b8cb4b31`, so the r26 waves tree is unchanged between `fec846d` and the tip. The Q61 cells cite
   the 152-record defect and name symlinks generically, never the 15, so the criterion inherits no
   bad count. Not an attack: r28's C3 kill rule rests on the 152, which is corroborated.
4. **All three new rows point at a lesson that lands this round.** `corpus/lessons/round-29.md` is
   absent at `b8cb4b31…` (`ls corpus/lessons/` has no round-29 file), so the pointers resolve only
   at the landing revision — the Q31 pointer check must run after the lesson lands. Flagged in the
   delivery's integration notes.
5. **Q60 is not applicable to r29 itself.** The r29 preregistration contains no
   `not counted in this claim` clause (measured `clauses=0`, rc 2 above), so the criterion is
   admitted for the class with the r28 witness only. Its wording says the clause is read from the
   frozen text, so a future round cannot manufacture one.
6. **`records=` is a unique-name count.** `census/round-29/c2-counter.py:63` stores records in
   a dict (`recs[name] = …`), so duplicate manifest lines collapse and the floor compares unique
   names; unparsable lines are counted separately in `bad`. A limit of the instrument, not a
   claim change; the Q61 cell does not promise duplicate detection.

## Out of scope

- No edit to `corpus/QUALITY.md`, `SKILL.md`, `corpus/lessons/round-29.md` or any tool/counter:
  the L1 lands the two blocks, and the lesson is not mine to write.
- No counter predicate, target, floor or case set was proposed for change; no ATTACK filed. The
  code-2 gap is a gate-map statement about existing bytes.
- The registry fixture was not executed here (scratch root hard-coded to `/var/tmp/souji-r29-C1Fixture`);
  its pass/red arms are `SwarmExecutor01`'s recorded runs.
- `tools/souji-axis-check.py` was not run on the new rows: they are QUALITY/SKILL text, not the
  preregistration machine block it parses.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-quality-skill.md` —
  `## Round 29 criteria` block for `corpus/QUALITY.md` (Q60, Q61, Q62) and three rows to append
  after `SKILL.md:224` (`souji-registry-agreement`, `souji-wave-evidence-capture v2`,
  `r29-c2-counter`), plus per-row provenance and L1 integration notes.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmScribe28.md` — this
  report.
