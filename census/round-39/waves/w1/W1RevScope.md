# W1RevScope — review: write scope for souji round 39 wave 1

Seat: W1RevScope (reviewer, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `ed30b7f5b77939c9073348d810730bc4f355708d`, HEAD at audit time
`2201778e7736af82e7d8a42dec2494f115bf3923`. Every command below was run with an absolute lane/repo
path; no mutating git/jj command was issued anywhere.

Verdict key: PASS / FAIL / NOTE (informational, no contract breach).

---

## R1 — Lane working tree: dirty-tracked bytes and unlanded artifacts

Command:
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain
```
Output:
```
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```
Command:
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat HEAD
```
Output: empty (no output; rc 0).

**Verdict: PASS on scope, FAIL on landing.** All five dirty paths are lane-relative and inside the
round's write scope (lane repo). No file outside the lane repo is dirty, and no tracked lane file is
modified-but-unstaged. But four of the five are *evidence*, not code: `c2-after.txt`, `c3-after.txt`
are the after-receipts the frozen register rows name, and `census-before.txt`/`census-after.txt` are
the SOURCES-census pair (`rows=170` → `rows=173`, `census_rc=1` → `census_rc=0`). Nothing in the
round's shipped claims is reproducible from committed bytes for these four until the L1 lands them.
`make-cells.py` is the register generator and is likewise unlanded (see R7).

## R2 — Lane history since base

Command:
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %an %s' ed30b7f5b77939c9073348d810730bc4f355708d..HEAD
```
Output:
```
2201778 souji-shokunin round-39: PROVINCE boundary note — two tool contracts repaired, no receipt class, certification OFF
790d16b souji-shokunin round-39: C2 — drop unreachable EISDIR from the RECORD-MISSING line (wave-1 W1ExecC2Docstring)
094e531 souji-shokunin round-39: C1 — R7 line names the reaped path as $HYAKU_SCRATCH, not a literal scratch root
50972f0 souji-shokunin round-39: C1 — single-line anchor bullets for R5/R7/R15 closures
c0b007b souji-shokunin round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
601195a souji-shokunin round-39: C2 — drift docstring puts each trigger on its class line (single-line rule)
bbd9b97 souji-shokunin round-39: C2 — resolve --rev/--register-rev (exit 2), drift RECORD-MISSING/MALFORMED contract, r39-citation-rev fixture
b769bfb souji-shokunin round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
```
**Verdict: PASS.** Eight commits, single author `souji-shokunin`, all subjects `round-39:`. No seat
authored a commit (seats are commit-forbidden; the history is consistent with L1-only landing).

Command:
```
git -C .../souji-shokunin diff --numstat ed30b7f5b77939c9073348d810730bc4f355708d..HEAD
```
Output (22 rows):
```
6	0	LOG.md
15	0	PROVINCE.md
4	0	SCORECARD.md
11	0	SKILL.md
4	0	census/round-38/preregistration.txt
265	0	census/round-39/c1-counter.py
22	0	census/round-39/c1-items.tsv
286	0	census/round-39/c2-counter.py
187	0	census/round-39/c3-counter.py
123	0	census/round-39/preregistration.txt
18	0	census/round-39/records/c1-before.txt
7	0	census/round-39/records/c2-before.txt
5	0	census/round-39/records/c3-before.txt
4	0	corpus/QUALITY.md
5	0	corpus/SOURCES.md
4	0	corpus/lessons/round-36.md
8	0	corpus/lessons/round-38.md
123	0	corpus/lessons/round-39.md
128	0	tests/fixtures/r39-citation-rev.py
141	0	tests/fixtures/r39-drift-record-rules.py
35	3	tools/souji-citation-reconcile.py
5	3	tools/souji-worktree-drift.py
```
**Verdict: PASS.** Every knowledge file is append-only (`0` deletions per row). Only the two repaired
tools carry deletions (`35/3`, `5/3`), which is the expected repair shape. No path escapes the lane.

## R3 — Fleet-root strays naming souji / round-39

Command:
```
git -C /home/vgpnk/Projects/shokunin status --porcelain | grep -Ei 'souji|round-39' || echo "NO_MATCH"
```
Output:
```
NO_MATCH
```
Command:
```
git -C /home/vgpnk/Projects/shokunin status --porcelain        # full, 9 entries
```
Output:
```
 M .scratch/goal-20261028-hyaku-run11.md
?? .scratch/closure-mado-r50.json
?? .scratch/closure-r54/
?? .scratch/source-routing-queue.md
?? .ufo/reports/round-49/tsukuroi.md
?? lane3/
?? o.bin
?? oldrep1.out
?? oldrep2.out
```
Attribution, by mtime (`ls -la`, `find . -maxdepth 1 -newermt '2026-10-28 14:39'`):
- `.scratch/goal-20261028-hyaku-run11.md` — 14:07, before round start; not r39 bytes.
- `o.bin` 2026-10-27 16:58, `oldrep1.out` 09:10, `oldrep2.out` 09:11 — pre-round.
- `.ufo/reports/round-49/tsukuroi.md`, `.scratch/closure-*`, `.scratch/source-routing-queue.md` —
  other-lane/round artifacts.
- `lane3/` — created 14:59 (inside the round window) but **not** an r39 artifact: `lane3/.git/config`
  names `url = /home/vgpnk/Projects/shokunin/kengaku-shokunin` and `git -C lane3 log` heads with
  `297e179 kengaku-shokunin round-50: …`. No souji/souji-shokunin byte in it.

**Verdict: PASS.** No fleet-root stray names souji or round-39. `lane3/` is a fleet-root untracked
clone inside the round window but is attributable to another lane's round, not to r39 seats — recorded
so the L1 does not credit or debit it to this round.

Command:
```
find /home/vgpnk/Projects/shokunin/.ufo -newermt '2026-10-28 14:39' -type f
```
Output:
```
.ufo/reports/round-50/kengaku.md
.ufo/reports/round-55/tameshi.md
.ufo/prompts/closure/kengaku-round-50.md
.ufo/prompts/closure/tameshi-round-55.md
.ufo/prompts/kengaku-round-51.md
.ufo/state/disk-guard.log
.ufo/state/inline-dispatcher.log
.ufo/state/kengaku.report-baseline
.ufo/watchdog.log
```
**Verdict: PASS for r39 scope.** No `.ufo/reports/round-39/` in the fleet repo (`ls .ufo/reports/`
shows no round-39 entry) — the round-39 report belongs in the lane, and no seat wrote it to the fleet
root. `.ufo/state/*` and `.ufo/watchdog.log` are harness-written and outside any seat's discretion.

## R4 — Fleet MANIFEST.json mtime inside the round window

Command:
```
cd /home/vgpnk/Projects/shokunin && git ls-files --error-unmatch MANIFEST.json && git diff --stat -- MANIFEST.json; stat -c '%y %n' MANIFEST.json
git hash-object MANIFEST.json ; git rev-parse HEAD:MANIFEST.json
```
Output:
```
TRACKED
(nothing from git diff --stat)
2026-10-28 14:55:02.731638092 -0300 MANIFEST.json
worktree: 290a006e971ae3181a4fb6a41954218efc280bda
HEAD:     290a006e971ae3181a4fb6a41954218efc280bda
```
**Verdict: NOTE.** The mtime falls inside the round window, but the content hash equals HEAD's blob,
so no byte was written to the fleet-root tracked manifest. Recorded because the round's guard names
`MANIFEST.json`; the observable state is a touch, not a write.

## R5 — Preregistration immutability (freeze commit vs HEAD vs worktree)

Command:
```
git -C .../souji-shokunin rev-parse b769bfb…:census/round-39/preregistration.txt
git -C .../souji-shokunin rev-parse HEAD:census/round-39/preregistration.txt
git -C .../souji-shokunin hash-object census/round-39/preregistration.txt
```
Output:
```
8c33fc34f6896430233d30d1b26a2dcc8507e03b   (freeze)
1183883668be22c1aa75f2756fffeff5a768d1a3   (HEAD)
1183883668be22c1aa75f2756fffeff5a768d1a3   (worktree)
```
Command:
```
git -C .../souji-shokunin log --format='%h %ci %s' ed30b7f…..HEAD -- census/round-39/preregistration.txt
git -C .../souji-shokunin diff b769bfb…..HEAD -- census/round-39/preregistration.txt | head -40
```
Output:
```
bbd9b97 2026-10-28 14:50:05 -0300 round-39: C2 — resolve --rev/--register-rev (exit 2), …
b769bfb 2026-10-28 14:44:44 -0300 round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
...
@@ -112,3 +112,12 @@
+## Amendment A1 — r39-citation-rev case class (2026-10-28, tighter-only, before any claim measurement)
+… (9 added lines)
```
**Verdict: PASS with a calibration note.** The worktree is not rewriting the frozen bytes (worktree
hash == HEAD hash), and the only post-freeze delta is amendment A1, appended `+9/-0` at `bbd9b97`
(14:50:05), which names the superseded L5 expectation ("the frozen L5 case `register-rev-gone`
expected the substring `not at`") and lands before the first after-receipt (`c2-after.txt`, 14:57).
Note for the L1: **the hash named in the contract as "freeze commit b769bfb…" no longer identifies
the preregistration bytes** (114 lines at freeze, 123 at HEAD). Any report sentence of the form "the
frozen contract at b769bfb" is one commit stale with respect to A1; cite `bbd9b97` or the blob
`1183883…` for the contract as amended.

## R6 — Frozen artifacts unchanged since freeze

Command:
```
for f in census/round-39/{c1-items.tsv,c1-counter.py,c2-counter.py,c3-counter.py} \
         census/round-39/records/c{1,2,3}-before.txt; do
  a=$(git rev-parse b769bfb…:$f); b=$(git rev-parse HEAD:$f); [ "$a" = "$b" ] && echo "SAME $f" || echo "DIFF $f"
done
```
Output:
```
SAME census/round-39/c1-items.tsv
SAME census/round-39/records/c1-before.txt
SAME census/round-39/records/c2-before.txt
SAME census/round-39/records/c3-before.txt
SAME census/round-39/c1-counter.py
SAME census/round-39/c2-counter.py
SAME census/round-39/c3-counter.py
```
**Verdict: PASS.** Items list, all three counters and all three before-receipts are byte-identical at
freeze and HEAD — the guards "do not edit `c1-items.tsv` / frozen receipts" hold. `git show --stat
b769bfb` confirms the counters, items, prereg, three controls and both new fixtures entered at freeze
(10 files, +1173).

## R7 — C1 counter at HEAD: the register arm has no lane bytes

Command:
```
cd .../souji-shokunin && python3 -B census/round-39/c1-counter.py --root . \
  --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
  --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
```
Output:
```
ITEM R39-C1-01 CLOSED
ITEM R39-C1-02 CLOSED
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-05 CLOSED
…
ITEM R39-C1-16 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
EXIT=1
```
Command:
```
ls -la census/round-39/ ; git -C .../souji-shokunin ls-tree -r --name-only HEAD census/round-39/
grep -c 'R39-REG-0' SCORECARD.md LOG.md corpus/QUALITY.md
```
Output:
```
… c1-counter.py c1-items.tsv c2-counter.py c3-counter.py make-cells.py preregistration.txt records/ __pycache__/
HEAD tree: c1-counter.py c1-items.tsv c2-counter.py c3-counter.py preregistration.txt
           records/c1-before.txt records/c2-before.txt records/c3-before.txt
SCORECARD.md: 0
LOG.md: 0
corpus/QUALITY.md: 0
```
**Verdict: FAIL — C1's register claim is unwritten in lane bytes at HEAD.**
1. `census/round-39/cells.tsv` — the `--register` argument the frozen predicate names — exists neither
   in HEAD nor on disk. `cells=0`, `commit_distinct=0`, both below the floors `>=6` and `>=2`.
2. `census/round-39/cells-lines.md` and the six `R39-REG-01…06` anchored lines are absent:
   `grep -c 'R39-REG-0'` returns `0` for each of `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`. The
   register binds an anchor *inside the named file*, so even a landed `cells.tsv` would fail until
   those six lines exist in those three files.
3. The generator `census/round-39/make-cells.py` (charset: writes `cells.tsv` + `cells-lines.md` with
   `--write`) is untracked — the register cannot be reproduced from committed bytes at any revision.
4. Two items read OPEN on absent receipts the capture step owes:
   `R39-C1-03 census/round-39/records/waves-wait.txt` (must `dead=0`, mustnot `waves=1,dead=0`) and
   `R39-C1-04 census/round-39/records/waves-capture.txt` (must `SUMMARY`, `records=,failed=0,uncovered=0`).
Both receipts must be **committed**, not merely written: the counter reads `git show <rev>:<path>`.

## R8 — C2 predicate at HEAD

Command:
```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1RevScope python3 -B census/round-39/c2-counter.py --root . \
  --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
```
Output:
```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
EXIT=0
```
Untracked receipt `census/round-39/records/c2-after.txt` carries the byte-identical `SUMMARY` line
(same `tool_sha=59f1e57d7af0/e48ed08e6728`, same `fixture_sha=7ab7c3d85a81`).
**Verdict: PASS.** C2 predicate is met by committed bytes, and the untracked receipt is a faithful,
reproducible copy rather than an unverifiable claim.

## R9 — C3 predicate at HEAD

Command:
```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1RevScope python3 -B census/round-39/c3-counter.py --root . \
  --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
```
Output:
```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
EXIT=0
```
Untracked `c3-after.txt` carries the same five lines and the same `fixture_sha=567c37a679f5`.
**Verdict: PASS.** `killed=4 survived=0 base_killed=0 cases=7` meets `cases>=6` and the base-killed
floor; receipt is reproducible.

## R10 — R4 capture list: every file under `.ufo/waves/round-39` that git cannot see

Command:
```
git -C .../souji-shokunin status --porcelain --ignored=matching | grep -E '\.ufo/waves/round-39'
git -C .../souji-shokunin check-ignore -v .ufo/waves/round-39/w1.ready .ufo/waves/round-39/w1/W1ExecCapture.md
find .ufo/waves/round-39 -type f | sort   # 21 files at 14:59; 27 at 15:03:59 (R10 snapshot below)
```
Output:
```
!! .ufo/waves/round-39/
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1.ready
.gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1/W1ExecCapture.md
```
`.gitignore` in full: `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/` — one line covers the
whole wave, no negation re-includes any file.

Snapshot, taken with
```
find .ufo/waves/round-39 -type f -printf '%s %TH:%TM %p\n' | sort -k3   # date '+snapshot %F %T' → 15:03:59
```
so this is the tree at **15:03:59**, i.e. 27 files and growing while the audit ran:
```
0      14:48 .ufo/waves/round-39/w1-gen.err
0      14:48 .ufo/waves/round-39/w1-validation.err
150    14:48 .ufo/waves/round-39/w1.ready
2180   15:03 .ufo/waves/round-39/w1.ready.partial
46870  14:48 .ufo/waves/round-39/gen-w1-spec.py
103142 14:48 .ufo/waves/round-39/w1-spec.json
141185 14:48 .ufo/waves/round-39/w1-dispatch.json
19132  14:48 .ufo/waves/round-39/w1/swarm-registry.json
12277  14:54 .ufo/waves/round-39/w1/W1ExecC2Docstring.md
10178  14:54 .ufo/waves/round-39/w1/W1ExecC2Repro.md
18478  14:55 .ufo/waves/round-39/w1/W1ExecC1Items.md
17446  14:52 .ufo/waves/round-39/w1/W1ExecC1Base.md
12642  14:57 .ufo/waves/round-39/w1/W1ExecC3Baseline.md
12975  14:57 .ufo/waves/round-39/w1/W1ExecConsumers.md
13536  14:57 .ufo/waves/round-39/w1/W1ExecSources.md
22009  14:58 .ufo/waves/round-39/w1/W1ExecC3Fixture.md
14241  14:58 .ufo/waves/round-39/w1/W1ExecCapture.md
18616  14:58 .ufo/waves/round-39/w1/W1ExecReportGate.md
17272  14:59 .ufo/waves/round-39/w1/W1ExecC1Anchors.md
13356  15:00 .ufo/waves/round-39/w1/W1ExecCommitList.md
15599  15:01 .ufo/waves/round-39/w1/W1ExecRegistry.md
20066  15:02 .ufo/waves/round-39/w1/W1ExecPrereg.md
23510  15:02 .ufo/waves/round-39/w1/W1ExecRound36.md
12236  15:02 .ufo/waves/round-39/w1/W1MutC1.md
19762  15:03 .ufo/waves/round-39/w1/W1ExecDeadSeats.md
27071  15:03 .ufo/waves/round-39/w1/W1ExecScratch.md
23913  15:03 .ufo/waves/round-39/w1/W1RevScope.md        (this report)
```
`COUNT=27` (7 top level + 20 in `w1/` = 8 non-report + 19 reports + `swarm-registry.json`). The
earlier 14:59 enumeration of the same tree read 21 files (7 + 14): the wave added six reports mid-audit
(`W1ExecDeadSeats`, `W1ExecPrereg`, `W1ExecRegistry`, `W1ExecRound36`, `W1ExecScratch`, `W1MutC1`) and
`w1.ready.partial` grew 1372 → 2180 B. **The capture step must re-run this enumeration at landing, not
trust this list.** `stat -c '%s %n'` cross-checked every byte count above.

`python3` over `w1-spec.json` at 15:04 prints `items 71 … present 19 missing 52 … extra []`, so every
present report belongs to a spec seat and 52 are still in flight.

Stray bytecode inside the ignored tree, for the capture step to exclude deliberately rather than by
accident: `census/round-39/__pycache__/c1-counter.cpython-314.pyc` (14:51) and
`tests/fixtures/__pycache__/r39-drift-record-rules.cpython-314.pyc` — both matched by
`.gitignore:3:__pycache__/`, so they will never land; they evidence that a seat imported
`c1-counter` and the C3 candidate fixture as modules instead of running them as scripts.

**Verdict: PASS on scope (all inside the lane), FAIL on capture if these 27 files are not copied into
the round's committed evidence.** Two of them — `w1.ready` and `w1.ready.partial` — disagree in kind:
`w1.ready` (14:48) is `{"lane":"souji","round":39,"wave":"w1","dispatch":"…/w1-dispatch.json","l1":"SoujiR39"}`,
while `w1.ready.partial` (15:00, written *after* it) is a seat→retry-id map
(`{"W1ExecC1Base": "W1ExecC1Base-2", … "W1ExecC2Repro": "W1ExecC2Repro-5", …}`). A capture that reads
"the ready marker" must state which of the two it read; the `.partial` name is not a completion signal.

## R11 — Round report and L0 question file

Command:
```
ls -la .ufo/reports/round-39/ 2>&1 ; ls -la .ufo/l0-questions.md 2>&1
find . -path ./.git -prune -o -path ./.jj -prune -o -iname '*l0*' -print
```
Output:
```
ls: cannot access '.ufo/reports/round-39/': No such file or directory
ls: cannot access '.ufo/l0-questions.md': No such file or directory
(only pre-existing files: census/round-18/…, census/round-31/…, .ufo/waves/round-17/…, round-18, round-31, round-35 …)
```
**Verdict: NOTE — pending, not a breach.** The round's own report path
(`.ufo/reports/round-39/souji.md`) and the L0 question file do not exist yet; no seat wrote an
L0-question file anywhere else in the round (no in-round `*l0*` file). If a seat asked L0 a question
without a path, it left no lane bytes — the L1 should reconcile that against the seat reports.

## R12 — Protected paths outside the lane (templates/, scripts/, ~/.local/bin, ~/.config)

Command:
```
cd /home/vgpnk/Projects/shokunin && find templates scripts -newermt '2026-10-28 14:39' -type f
find ~/.local/bin ~/.config -maxdepth 2 -newermt '2026-10-28 14:39'
```
Output:
```
templates: (none)
scripts:   (none)
/home/vgpnk/.config/chromium/Default, …/chromium/Safe Browsing, …/fcitx5, …/fcitx5/conf,
…/fcitx5/profile, …/ai-usage, …/ai-usage/selected (14:58), …/Grok Bot, …/Grok Bot/sand-statsig-bootstrap.json
```
**Verdict: PASS.** No lane or seat wrote `templates/`, `scripts/`, `~/.local/bin`, or `~/.config`.
The `~/.config` touches are session/harness state (Chromium, fcitx5, an ai-usage tracker) and carry no
souji bytes. No tool was installed for this seat; nothing to record under the tooling authorization.

## R13 — Scratch

`/fast/scratch/hyaku/souji-r39/` holds 28 seat dirs, 122 files (L1 scratch included). My own
`/fast/scratch/hyaku/souji-r39/W1RevScope/` is empty (`find … -type f | wc -l` = `0`) and was removed
at the end of this audit. `/tmp` was not used. No lane was cloned.

---

## Findings by severity

**HIGH — 1. C1's register arm has zero lane bytes at HEAD.** `census/round-39/cells.tsv` absent from
the tree and disk; `R39-REG-01…06` absent from `SCORECARD.md`/`LOG.md`/`corpus/QUALITY.md` (count 0
each); generator `make-cells.py` untracked. Measured: `REGISTER cells=0 mismatches=0
commit_distinct=0`, `SUMMARY … register_cells=0 … commit_distinct=0`, exit 1. The frozen predicate
requires `register_cells>=6 register_mismatches=0 commit_distinct>=2`; the r38 limit C1 exists to
answer ("every row carries commit == receipt_rev") is therefore still unanswered in bytes. Also
`corpus/QUALITY.md` does not yet contain `open=16` (0 occurrences), the token REG-06 expects to anchor.

**HIGH — 2. Two of the 16 C1 items read OPEN on absent receipts.** `R39-C1-03`/`R39-C1-04` name
`census/round-39/records/waves-wait.txt` and `waves-capture.txt`; both `FILE-ABSENT`. The counter reads
committed bytes only, so writing them is insufficient — they must be landed before the landing
revision, or C1 misses on `open=2` regardless of the register.

**MEDIUM — 3. Four evidence receipts and the register generator are unlanded working-tree files.**
`c2-after.txt`, `c3-after.txt`, `census-before.txt`, `census-after.txt`, `make-cells.py` are `??`.
Their content is reproducible (I reran C2 and C3 at HEAD and got byte-identical SUMMARY lines and
hashes), so this is a landing gap, not a fabrication risk — but the register rows REG-01…05 name
`c2-after.txt`/`c3-after.txt` as their receipts, and a row whose receipt is unlanded cannot verify.

**LOW — 4. The contract's named freeze commit no longer identifies the contract bytes.** A1 was
appended at `bbd9b97` (14:50:05, `+9/-0`, before `c2-after.txt` at 14:57), so
`b769bfb:preregistration.txt` = `8c33fc3…` (114 lines) while `HEAD` = `1183883…` (123 lines).
The append is legitimate under the round-38 amendment rule it cites; the hazard is a report sentence
that says "frozen at b769bfb" and quotes A1.

**LOW — 5. Marker ambiguity in the ignored wave tree.** `w1.ready.partial` postdates `w1.ready` and
lists retry ids for 20 seats; both are invisible to git. The capture step must name which marker it
read, and the two 0-byte `.err` files plus the 0-byte-looking `W1ExecRegistry.md` entry must not be
counted as evidence of success on their size alone.

**INFO — 6. Bytecode strays** `census/round-39/__pycache__/c1-counter.cpython-314.pyc` and
`tests/fixtures/__pycache__/r39-drift-record-rules.cpython-314.pyc` sit inside the lane; both are
ignored (`.gitignore:3`), so they cannot land, but they show the counters/fixture were imported
rather than executed by at least one seat.

**INFO — 7. Fleet-root mtime-only touches.** `MANIFEST.json` mtime 14:55 with content hash identical
to HEAD (`290a006e…`); `lane3/` (origin `kengaku-shokunin`, head `297e179 kengaku round-50`) created
14:59. Neither carries a souji round-39 byte.

## Residual risk

- My C1 measurement reads HEAD `2201778`; the L1 is still landing (the wave is mid-flight: 58 of 71
  seats had no report at audit time). Findings 1–3 are "not yet", and can be closed by later commits;
  they are misses only if HEAD is near the landing revision.
- C2/C3 pass at HEAD but their receipts are untracked; if the L1 lands the receipts but rewrites a
  counter or fixture afterwards, the receipts' `tool_sha`/`fixture_sha` would no longer match the
  landed bytes. Land receipts after the last counter/fixture edit, or re-run them at the landing rev.
- I audited the fleet root by `git status` and by mtime for the round window; a seat that wrote to a
  path already ignored and outside `.ufo/waves/round-39` would show only as an mtime change. No such
  path appeared in `find` for `templates/`, `scripts/`, `~/.local/bin`, `~/.config`, or lane top level.

## Verification gaps (explicitly not checked)

- `.ufo/waves/round-39/w1/*.md` contents: I verified every present report belongs to a spec seat and
  that the tree is ignored; I did not audit the 19 reports' own claims (that is the other reviewer
  seats' scope).
- `.jj` state: the lane has `.jj/` (ignored). I did not inspect jj op logs, so I can only say the *git*
  history and worktree are scope-clean, not that no seat ran a mutating jj command.
- The `sources-census.sh` numbers inside `census-before.txt`/`census-after.txt` were quoted, not
  recomputed.
