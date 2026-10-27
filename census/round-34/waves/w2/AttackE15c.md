# AttackE15c — adversarial falsification of W1's E15c finding

Seat SwarmCritic15 (w2). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `9c76c7222a8abff027af42e37f0d160d52526bba`; C1/C2 list frozen at
`2b0171e2071fdc9c16a69bed12b0d040e574d8c8`. Target: C1 item E15c.

## Status

W1's **verdict is confirmed, its root-cause class is falsified, and W1 missed an honest
rule-conforming route to AGREE** that is fully gate-verified against the frozen counter.

- CONFIRMED (reproduced): E15c do-nothing MISMATCH — frozen argv exits 128
  (`fatal: bad revision 'a65fac98964b445758e94c8057280c9a19d302ff8'`), predicate fails,
  rc ≠ stated exit 0. Not a measurement artifact: the pinned string names no object in
  the store, so every counter clone (base, tip, any cause) fails identically.
- FALSIFIED: W1's classification "missing/unresolvable pinned revision" (SwarmExecutor13.md:32,55,
  grouping E15c with genuinely-absent-content G24). The commit W1 believes unresolvable
  **exists**, is an ancestor of base, and the row's stated counting command is verifiably
  TRUE today. The defect is a **41-character transcription corruption in the frozen item
  list's argv** (a spurious `0` inserted into the 40-hex SHA), not repo content loss.
- ROUTE FOUND (gate-verified; not end-to-end executed): an argv-correction restatement under
  Q75/Q76/A1 with cause `315422ba9970f03c27f8a9184446783b7fcdf0a7` satisfies every
  executable check in `census/round-34/c1-counter.py:245-323` and would make E15c AGREE.

## Evidence

All commands run read-only against the live lane repo (cwd
`/home/vgpnk/Projects/shokunin/souji-shokunin`), 2026-10-27. No lane file modified.

1. Frozen item (`census/round-34/c1-items.tsv:58`, identical at list-rev
   `2b0171e…` — verified `git show 2b0171e:census/round-34/c1-items.tsv`):

   `E15c  SCORECARD.md:68  0  COUNT:^\+ground:.*$==2 && COUNT:^-ground:.*$==0  corpus/knowledge  {REV}  bash -c "git diff a65fac98964b445758e94c8057280c9a19d302ff8 778747eb671f8e85ef5387bc3d7023337b30467c -- corpus/knowledge/"`

2. Verbatim reproduction of the frozen argv (live repo):

   ```
   $ bash -c "git diff a65fac98964b445758e94c8057280c9a19d302ff8 778747eb671f8e85ef5387bc3d7023337b30467c -- corpus/knowledge/"
   fatal: bad revision 'a65fac98964b445758e94c8057280c9a19d302ff8'   (rc=128)
   ```

   Matches committed do-nothing record `census/round-34/records/controls-c1-do-nothing.txt:42`
   (`ITEM E15c MISMATCH original rc=128 expect_exit=0 predicate fails last=fatal: bad revision …`)
   and W1's `deliver-c1-do-nothing-check.txt:47`. The counter's clone inherits the object store
   (`c1-counter.py:194-231`, `git clone --no-local` of the lane at `{REV}`), so the verdict is
   cwd- and environment-independent; load (Q77) cannot move it.

3. Whole-store scan: `git cat-file --batch-all-objects --batch-check` over all 11,497 objects —
   no object matches the frozen pin; `.git/objects/info/alternates` absent; `git replace -l`
   empty; single worktree. The string is **41 characters**, not 40:

   ```
   frozen: a65fac98964b445758e94c80572 8 0 c 9 a19d302ff8   (len 41)
   real:   a65fac98964b445758e94c80572 8   c 9 a19d302ff8   (len 40)
   $ git rev-parse --verify a65fac98964b445758e94c8057280c9a19d302ff8
   fatal: Needed a single revision
   ```

4. The real commit exists and is ancestral:

   ```
   $ git cat-file -t a65fac98964b445758e94c805728c9a19d302ff8
   commit        # round-23 verifier spot-check (integrator, hyaku), 2026-10-25 06:06:38 -0300
   ```

   It sits in `778747eb…`'s parent chain (`git log 778747eb | sed -n 5p`) and
   `git merge-base --is-ancestor a65fac…728c9a… 9c76c72…` → true.

5. The intended measurement is TRUE today (corrected argv executed):

   ```
   $ git diff a65fac98964b445758e94c805728c9a19d302ff8 778747eb671f8e85ef5387bc3d7023337b30467c -- corpus/knowledge/
   rc=0;  grep -c '^+ground:' → 2;  grep -c '^-ground:' → 0
   ```

   exactly the frozen predicate `COUNT:^\+ground:.*$==2 && COUNT:^-ground:.*$==0`. The frozen
   target (exit 0 + predicate) would AGREE with the correctly-spelled SHA.

6. Corruption origin: the correct full SHA is printed in the same SCORECARD section the item
   cites — base `SCORECARD.md:63` header: "lane base a65fac98964b445758e94c805728c9a19d302ff8".
   The TSV expanded the prose's short `a65fac9` and produced the 41-char string. The corrupted
   string occurs only in r34 artifacts (`c1-items.tsv:54,58`, the control record echoing git's
   error, and w1 spec/render/dispatch files); `git log --follow -- census/round-34/c1-items.tsv`
   shows a single authoring commit `2b59192…` (the r34 freeze) — born corrupted at the freeze.
   Sibling item E14a (`c1-items.tsv:54`) carries the identical corrupted SHA (its argv
   `git cat-file -e a65fac…7280c9a…:tests/fixtures/r24-size-census.py` fails with
   "invalid object name"), corroborating a systematic expansion slip, not per-row content loss.
   (E14a is another seat's target; cited as evidence only.)

7. Q76 independent check: `git show 9c76c72:SCORECARD.md | grep -nE 'SCORECARD\.md:68([^0-9]|$)'`
   → 0 hits; no `SKILL.md:68` pointer; no prior restatement binds E15c. Confirms W1 finding 3/4
   for this cell.

## Findings

1. **W1's verdict stands; its cause label is wrong.** The do-nothing MISMATCH is real,
   reproduced byte-for-byte (rc=128, same `fatal:` line), and unmovable by load or environment.
   But "missing/unresolvable pinned revision" misattributes the defect: nothing is missing from
   the repository. `a65fac…728c9a…` exists, is an ancestor of base, and the row's stated
   counting claim (`+ground:`×2 / `-ground:`×0) holds as of the tip. The true class is
   **frozen-item-list transcription corruption** — the item's own argv carries a malformed
   41-hex string that never named an object at any commit, introduced by the r34 enumeration
   (freeze commit `2b59192…`) and frozen at list-rev `2b0171e…`. W1 was misled by git's error
   wording ("bad revision" conflates malformed-string with absent-commit) and did not test the
   string's length or search the store for the neighboring commit.

2. **Honest rule-conforming route W1 missed (gate-verified, source-inspected).** Under the
   frozen contract the item list cannot be edited (read at `--list-rev`, post-data), so the
   sanctioned repair is an appended `### Round 34 registry restatements` row (Q75/Q76,
   A1). For E15c every executable gate in `census/round-34/c1-counter.py:245-323` passes with:
   - `| E15c | SCORECARD.md:68 | restated | 0 | \`bash -c "git diff a65fac…728c9a… 778747e… -- corpus/knowledge/"\` | \`<last digit-bearing line of the run>\` | 315422ba9970f03c27f8a9184446783b7fcdf0a7 | <reason> |`
   - Gate checks verified:
     - `where`/`kind` match the item; `rexit` numeric; restated statement in backticks (A1(c)).
     - Corrected argv names the item's file (`corpus/knowledge`) — passes the A1(b) basename
       test at `c1-counter.py:267`.
     - Cause full40 and **ancestor of list-rev**: `git merge-base --is-ancestor 315422ba… 2b0171e…` → YES (executed). 315422ba is "round-24: final — post-wave-2 repairs …" (2026-10-25 06:58), the commit pickaxe `-S` identifies as the sole author of line 68's current text.
     - "Cause wrote the row's line": exact base/list-rev line-68 text is absent at `315422ba^`
       (grep -cF → 0) and present at `315422ba` (→ 1) — matches `c1-counter.py:294-298`.
     - "Row's own argv already failed at the cause": the frozen 41-char argv fails at every rev
       (rc=128 ≠ 0 ⇒ `holds()` returns False) ⇒ `is not False` test at `c1-counter.py:299` passes.
     - Final run at `--rev` with the corrected argv: rc=0, predicate holds (executed, Evidence 5);
       statement equals the run's last digit-bearing line (computable; the diff's tail
       `+Re-verification (r24, 2026-10-25): … selftest=PASS ids=5/5 …` line).
   - Honesty: the corrected argv runs the row's own counting command with the very SHA the
     SCORECARD row itself names (short `a65fac9`); the repair changes no semantics — it fixes
     the enumeration's transcription of the row. This is exactly the argv-correction path A1(a)
     exists to make evaluable. So E15c is **not** stuck like truly-lost-content items; it is
   reachable to AGREE at the landing commit and the tip.
   - Caveat (stated, not executed): I verified each gate with targeted commands and source
     inspection; I did **not** run the counter end-to-end with a forged restatement row
     (fixture-execution avoidance; no such claim is made). The `holds(frozen argv @ cause)` gate
     is logically identical to the committed do-nothing reading at base (same store, same absent
     object) — [INFERENCE] from executed components.
   - Residual semantic caveat: the SCORECARD row's prose command never failed (it works today);
     the argv that "already failed at the cause" is the frozen item argv, which fails
     everywhere. A strict reading of the cause template's intent fits imperfectly, but the
     frozen contract defines validity by the counter's executable checks — all of which pass.

3. **Smallest safe correction** (for the lane, not performed by this seat — read-only):
   append the single restatement row in Finding 2 for E15c; the identical repair pattern
   (correct 40-hex SHA) applies to E14a's argv (`c1-items.tsv:54`) with the same cause class.
   This is strictly safer than any history/object-store surgery (e.g., grafting an object under
   the 41-char name is impossible — 41-hex strings name nothing).

## Attack log

Adversarial probes against the W1 claim, in order:
1. Reproduced the frozen argv verbatim → rc=128, matching the committed control record and
   W1's table. Verdict survives.
2. Tested the artifact hypothesis: whole-object-store scan (11,497 objects), alternates,
   replace refs, worktrees, jj colocation (`jj log -r a65fac…7280c9a…` → "doesn't exist"; the
   colocated jj uses the git store, `.jj/repo/store/git_target`) — the 41-char string names no
   object anywhere. Not a clone/cwd/load artifact.
3. Tested the typo hypothesis: compared frozen pin to the commit in 778747's ancestry — exact
   match after deleting one `0` at position 29; lengths 41 vs 40. Confirmed.
4. Tested the "unresolvable" hypothesis directly: `git cat-file -t a65fac…728c9a…` → commit;
   ancestor of base; the row's diff claim holds at the tip (2/0). Falsified.
5. Tested whether W1's "no route" implicit claim holds: enumerated the restatement gates in
   `c1-counter.py` and verified each (ancestry, line authorship at `315422ba(^)`, argv-failure
   semantics, corrected-run outcome, statement computation, Q76 absence). Route confirmed
   reachable in principle.
6. Sibling cross-check: E14a shares the corrupted SHA → systematic freeze-time expansion slip,
   strengthening Finding 1's class label.

No frozen artifact was modified; no commit, push, or fixture execution performed; nothing
written outside the two report files and `/tmp/e15c-diff.txt` (scratch diff capture).

## Deliveries

- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackE15c.md`
- Seat report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/SwarmCritic15.md`
- Reproduced: frozen-argv failure (rc=128); frozen pin length 41 vs real 40; real commit exists
  and is ancestral; corrected argv yields rc=0 with predicate 2/0; cause-commit gates for the
  restatement route.
- Findings for the canonical judge: W1 E15c verdict CONFIRMED; W1 root-cause class FALSIFIED
  (transcription corruption, not missing revision); honest argv-correction restatement route
  EXISTS and is gate-verified (end-to-end execution not claimed).
