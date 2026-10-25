# ScoutShonen — round 26 SHONEN box pointers and promotion readiness

Seat: scout (read-only). Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`;
lane HEAD observed at close `e78ac7c4837b81b634db4a927605a751a7f006ba` (the
round-26 verifier spot-check landed during this seat's run; the lane tip before it
was `166baa18f808071bc385187691713044a26bd663`). No lane file was written except
this report; no `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no
`rm`/`mv`, no signal. Scratch: none created (`TMPDIR` pointed at a
`/var/tmp/souji-r26-ScoutShonen` path that no tool materialised — verified absent
at close; nothing under `/var/tmp` was created by this seat). Tool
installs/updates: **none**.

## Status

STATUS: PASS — all four `SHONEN.md` boxes resolve at the observed lane tip, each to a
concrete line/row/artifact, and **no box moves to `[x]`**: the only non-author
verifier of record for round 26 explicitly declined the promotion check
("No `[x]` written; no non-author promotion check claimed"), so r26 does not
discharge the r25 D4 route. Report-ready SHONEN lines are in `## Findings` F5.

## Evidence

### E1 — `SHONEN.md` is byte-identical across the round (base → tip)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --name-only \
    0eca7c8a5d10bcbfdae50d0c390d277deec63bfd..HEAD -- SHONEN.md
(empty)
$ grep -cE '\[x\]' /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
0
```

`SHONEN.md` (12 lines, unchanged) names four boxes, each with a pointer sub-line:

```
5:- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
6:  SKILL.md Decision tables/Error patterns/Checklists/Gate registry; corpus/SOURCES.md S100-S103; corpus/lessons/round-21.md Gate
7:- [~] At least one end-to-end domain task executed and logged in LOG.md
8:  LOG.md:362 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed)
9:- [~] Instructions executable by an agent without oral context
10:  census/round-21/run-acceptance.py; census/round-21/accepted-matrix.json (3/3 sources, each18/18); census/round-21/remote-source-after.json
11:- [~] No cross-domain bleed (PROVINCE.md still accurate)
12:  PROVINCE.md Round21 privacy boundary; .ufo/waves/round-21/w1/ConnSiblingOverlap.md; corpus/lessons/round-21.md Boundaries
```

### E2 — the r25 D4 note, verbatim (source of this assignment's premise)

`corpus/lessons/round-25-verifier-spotcheck.md:74` (237 bytes, one line):

> 4. SHONEN boxes remain `[~]`-only: all four are plausibly non-author checkable next round (box 1 cites resolvable sources; box 2 logged; box 3 runnable fixtures; box 4 PROVINCE) — promotion is operator-owned; flagged for the operator.

### E3 — the promotion gate text (fleet `PROTOCOL.md:66-68`)

```
  evidence pointer. The lane's own assessment is `[~]` asserted (with its evidence pointer); only a
  non-author `<id>` may write `[x]`, and any `[x]` carrying no named non-author verifier is author
  attestation counting as `[~]` for the gate. Minimum bar: the seed below changes only with this gate text.
```

Verbatim fragment used as a cited quote (16 words, one line, no pipe):
> non-author `<id>` may write `[x]`, and any `[x]` carrying no named non-author verifier is author

### E4 — round 26 DOES have a non-author verifier, and it declined the box check

`corpus/lessons/round-26-verifier-spotcheck.md` exists at HEAD (commit
`e78ac7c4837b81b634db4a927605a751a7f006ba`, "round-26 verifier spot-check
(integrator, hyaku): non-author admit/reject"; `git merge-base --is-ancestor
e78ac7c HEAD` → ancestor ok). Its author line reads:

```
author: hyaku closure (non-author integrator, @m_kfc)
```

Its SHONEN conformance bullet (line 10), verbatim (17 words, no pipe):

> No `[x]` written; no non-author promotion check claimed. Boxes carry resolvable pointers; full promotion checkability is operator-owned.

The same file verifies C1/C2/C3 (`re-measured — verified.`, `Re-measured + evidence-verified.`)
and re-measures the box-4 question only as claim-level evidence. It names no
SHONEN box for promotion.

### E5 — box 1 pointers resolve (HEAD)

```
$ git show HEAD:SKILL.md | grep -nE '^## (Decision tables|Error patterns|Checklists|Gate registry)'
42:## Decision tables
78:## Error patterns (false-SAFE signatures)
147:## Checklists
167:## Gate registry
$ git show HEAD:corpus/SOURCES.md | grep -nE '^\| *S1(0[0-3]) *\|'   → 121,122,123,124
$ git show HEAD:corpus/lessons/round-21.md | grep -nE '^#{2,3} (Gate|Boundaries)'
25:## Gate
38:### Boundaries and teaching
```

Corroborating detail a non-author must know (all read this run):

* `SKILL.md` contains **no** external URL — `grep -oE 'https?://[^ )]+' SKILL.md`
  returns nothing; its source citations are registry ids at `SKILL.md:354`
  ("Evidence/source bindings: S100/S101 and") and `SKILL.md:376`
  ("bit-identical reproducible-build claim (S103).").
* `S102` is **not** cited anywhere in `SKILL.md` (`grep -c S102 SKILL.md` → 0);
  its `used-by` is `corpus/lessons/round-21.md`.
* `S103`'s registry status is `rejected` and its `used-by` is `—`; the row records
  "REJECTED: equal acceptance outcomes are not a bit-identical build-artifact comparison".
* `SKILL.md` is **unchanged this round** (`git diff --name-only base..HEAD --
  SKILL.md` → empty) and contains **no** row for the round's new instrument
  (`grep -c "souji-axis-check" SKILL.md` → 0 at HEAD and in the worktree). The
  drafted Gate-registry rows exist only in the unlanded wave deliverable
  `.ufo/waves/round-26/w1/axis-check-docs.md:67-68`.
* `corpus/QUALITY.md:143` (Q59) **is** landed at HEAD.

### E6 — box 2 pointer resolves, and r26's own LOG block is not landed

```
$ git show HEAD:LOG.md | sed -n '362p'
## 2026-10-19 — operator sweep (execution): root-wide receipts + home-wide cache/tmp cleanup
$ git show HEAD:census/round-3/operator-approval-list.tsv | tail -n +2 | wc -l
96
```

The lane `LOG.md` is 1741 lines; `git log --oneline -1 -- LOG.md` →
`a877325 round-25: land final receipts, R7 witness and honest-stop records`;
`grep -nE 'Round ?26' LOG.md` → **no match** (the r26 block is absent).
The r26 LOG text exists only as the tracked wave draft
`.ufo/waves/round-26/w1/log-r26.md`, whose line 1 reads:

> # Round 26 — LOG.md block draft (paste at LOG.md tail, after `### Round25 final evidence addendum`)

Because the paste target is the **tail**, the `LOG.md:362` pointer stays stable.
Note the pointer is lane-relative: the fleet-root `LOG.md:362` is unrelated text
(`— self-defect 20. Related, and worse because a sibling can see it: **138 unqualified cross-repo citations** in this`), so a
checker must resolve `LOG.md` inside `souji-shokunin/`.

### E7 — box 3 pointers resolve and were re-read this run

```
$ python3 -c "import json;d=json.load(open('census/round-21/accepted-matrix.json')); ..."
scenarios 3 replayed 3 summaries_equal True
S1 all_matched True matched_command_count 18 rc 0 src_unchanged True
S2 all_matched True matched_command_count 18 rc 0 src_unchanged True
S3 all_matched True matched_command_count 18 rc 0 src_unchanged True
$ python3 -c "...remote-source-after.json..."
all_matched = True ; expected_command_count = 18 ; matched_command_count = 18
inputs_unchanged = True ; source_sample_unchanged = True
$ python3 -B census/round-21/run-acceptance.py --help   → usage text, rc 0
```

The round's **new** runnable pair, executed by this seat:

```
$ TMPDIR=/var/tmp/souji-r26-ScoutShonen python3 -B tools/souji-axis-check.py \
    --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0                     rc=0
$ TMPDIR=/var/tmp/souji-r26-ScoutShonen python3 -B tests/fixtures/r26-axis-check.py \
    --tool tools/souji-axis-check.py
... CASE 12 control-always-green-stub PASS stub_passed=2/11 discriminator=PASS control=FALSE-GREEN-REJECTED
cases=12 pass=12 control=FALSE-GREEN-REJECTED   rc=0     (run twice, identical output)
```

But the fixture is **not** self-invoking:

```
$ python3 -B tests/fixtures/r26-axis-check.py
usage: r26-axis-check.py [-h] --tool TOOL
r26-axis-check.py: error: the following arguments are required: --tool      rc=2
```

and neither r26 instrument has a `SKILL.md` Gate-registry row, so an agent
without oral context cannot find or invoke them from `SKILL.md` alone.

### E8 — box 4 pointers resolve, and no cross-domain write occurred

```
$ git show HEAD:PROVINCE.md | grep -n 'Round21 privacy boundary'
161:### Round21 privacy boundary
$ git cat-file -e HEAD:.ufo/waves/round-21/w1/ConnSiblingOverlap.md   → present (17396 bytes)
$ git show HEAD:corpus/lessons/round-21.md | grep -nE '^### Boundaries'
38:### Boundaries and teaching
```

Round-26 write scope, from the committed delta (`git diff --name-only
0eca7c8..HEAD`): 41 paths, all lane-internal (`SCORECARD.md`,
`census/round-26/*`, `corpus/*`, `tools/souji-axis-check.py`,
`tests/fixtures/r26-axis-check.py`, `.ufo/waves/round-26/*`). No sibling lane
repo and no fleet-root file appears in the delta. Campaign source untouched —
read-only evidence, mtimes predate the round:

```
-rw-r--r-- 2026-10-24 23:33:20  /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
-rw-r--r-- 2026-10-23 18:27:26  /home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh
-rw-r--r-- 2026-10-23 18:28:31  /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out
```

`considerthese/` is absent in the lane (`ls -d considerthese` → No such file or
directory), as the r26 report states.

### E9 — pointer-root nuance for S131/S132 (box 1 / box 3 resolvability)

The admitted own-work rows cite `lanes/souji/round2/fixtures/r23-trigger-prune.sh`
and `lanes/souji/round2/evidence/r23-worktree-census.out`. That path form resolves
under the **campaign repo root**, not under the staged-package directory the
prereg names (`/home/vgpnk/Projects/shokuknow/merge/souji`, which holds only
`MERGE-REPORT.json`, `MERGE-REPORT.md`, `SOURCES.append.md`, `knowledge/`):

```
$ ls -d /home/vgpnk/Projects/shokuknow/merge/souji/lanes   → No such file or directory
$ ls -la /home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh   → present, sha256 11c136aa71066733d50d
$ ls -la /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out → present
$ ls -d lanes                                                → No such file or directory (inside the lane)
```

Same form as the pre-existing `S109` row (`corpus/SOURCES.md:130`), so this is
the lane's established convention, not a round-26 novelty.

## Findings

1. **Box 1 pointer (resolves; no promotion this round).**
   `SHONEN.md:6` names — verbatim — "SKILL.md Decision tables/Error patterns/Checklists/Gate registry; corpus/SOURCES.md S100-S103; corpus/lessons/round-21.md Gate".
   Resolved at HEAD: `SKILL.md:42/:78/:147/:167`, `corpus/SOURCES.md:121-124`,
   `corpus/lessons/round-21.md:25`. The r25 note's premise ("box 1 cites
   resolvable sources") holds — with the nuances in E5: `SKILL.md` carries no
   direct URL (citations are registry ids), `S102` is cited only by the r21
   lesson, and `S103` is a **rejected** row cited as a refusal. `SKILL.md` was not
   modified in r26, and the round's new axis-check instrument has no
   Gate-registry row, so r26 adds **no** new box-1 cite inside `SKILL.md`.
   **Would qualify for `[x]`:** a named non-author verifier checks (a) the four
   named `SKILL.md` sections still hold a decision table, an error-pattern list
   and a checklist, (b) each cited source resolves — `corpus/SOURCES.md:121-124`
   present, `used-by` paths present, `S103`'s rejected status consistent with how
   `SKILL.md:376` uses it, `S102`'s absence from `SKILL.md` explained by its
   `used-by` — and writes `[x] <verifier-id>` with that pointer.

2. **Box 2 pointer (resolves; r26's own log block not yet in `LOG.md`).**
   `SHONEN.md:8` names — verbatim — "LOG.md:362 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed)".
   Resolved at HEAD: lane `LOG.md:362` is the operator-sweep heading, and the
   96-row receipt re-derives from `census/round-3/operator-approval-list.tsv`
   (97 lines = header + 96 data rows) — the r25 note's "box 2 logged" premise
   holds. Two facts a non-author must weigh: the r26 LOG block is **not** in
   `LOG.md` (only the tracked wave draft `w1/log-r26.md`, which specifies a
   tail paste that keeps line 362 stable), and the pointer is lane-relative
   (the fleet-root `LOG.md:362` is unrelated text, E6). The r26 lane report's
   own box-2 pointer ("`LOG.md`-equivalent round records (lesson file receipts)")
   is **not** a resolvable `LOG.md` line — it points at the lesson file.
   **Would qualify for `[x]`:** the r26 LOG block is landed at the tail of the
   lane `LOG.md`, and a named non-author verifier re-derives the 96-row approval
   list and confirms the logged end-to-end domain task is real and completed.

3. **Box 3 pointer (resolves; the round's new instruments are not self-discoverable).**
   `SHONEN.md:10` names — verbatim — "census/round-21/run-acceptance.py; census/round-21/accepted-matrix.json (3/3 sources, each18/18); census/round-21/remote-source-after.json".
   Resolved and re-read this run (E7): 3/3 scenarios, each 18/18, `all_matched`,
   `summaries_equal`, remote-source 18/18 with `inputs_unchanged`; the runner
   prints its own usage. The r25 premise "box 3 runnable fixtures" holds for the
   named artifacts. r26 strengthens it with two new runnable instruments that
   this seat executed successfully (`claims=3 flags=0`; `cases=12 pass=12
   control=FALSE-GREEN-REJECTED`, twice) — **but** `tests/fixtures/r26-axis-check.py`
   requires an explicit `--tool PATH` (bare run → usage error, rc 2) and neither
   instrument is registered in the `SKILL.md` Gate registry, so "executable by an
   agent without oral context" does not yet reach them.
   **Would qualify for `[x]`:** the `souji-axis-check` / `r26-axis-check` rows
   land in the `SKILL.md` Gate registry with their exact invocation, and a named
   non-author verifier runs the instrument from `SKILL.md` alone in a fresh
   `/var/tmp` world (fixture included) and writes `[x] <verifier-id>`.

4. **Box 4 pointer (resolves; no cross-domain bleed observed this round).**
   `SHONEN.md:12` names — verbatim — "PROVINCE.md Round21 privacy boundary; .ufo/waves/round-21/w1/ConnSiblingOverlap.md; corpus/lessons/round-21.md Boundaries".
   Resolved at HEAD: `PROVINCE.md:161`, the round-21 connector report (present,
   17396 bytes), `corpus/lessons/round-21.md:38`. The r26 committed delta is
   lane-internal only and the campaign source is untouched (E8), so the r25
   premise "box 4 PROVINCE" holds. The one nuance worth a checker's attention is
   the own-work path root for S131/S132 (E9): it resolves under the campaign
   repo root, not under `merge/souji` and not inside the lane — consistent with
   the existing `S109` convention, so a cross-domain reading must be argued from
   `PROVINCE.md` + `merge/souji/MERGE-REPORT.md`, not from path absence.
   **Would qualify for `[x]`:** a named non-author verifier confirms the r26
   additions (F1 entries, rows S128-S132, the `corpus/README.md:39` map row)
   stay inside the lane's declared F1 surface, that no sibling source tree was
   written, and that `PROVINCE.md` still describes the surfaces r26 touched —
   then writes `[x] <verifier-id>`.

5. **Report-ready SHONEN lines (paste target: the lane report's `## SHONEN`
   section).** All four stay `[~]`; each line keeps the `SHONEN.md` box text and
   adds the r26-updated resolvable pointer. This is what the report should carry
   — note the r26 report's current box-2 pointer (`LOG.md`-equivalent round
   records) is not a resolvable `LOG.md` line, and its box-1 pointer does not
   name the four sections.

   ```
   [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — `SKILL.md:42` Decision tables, `:78` Error patterns, `:147` Checklists, `:167` Gate registry; `corpus/SOURCES.md:121-124` S100-S103; `corpus/lessons/round-21.md:25` Gate. SKILL.md unchanged this round and the round's new axis-check instrument has no Gate-registry row, so it is not yet a box-1 cite. No non-author verifier checked this box.
   [~] At least one end-to-end domain task executed and logged in LOG.md — lane `LOG.md:362` (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed), receipt re-derived from `census/round-3/operator-approval-list.tsv` (96 data rows). The round-26 LOG block is still a wave draft (`w1/log-r26.md`) and is not yet in `LOG.md`. No non-author verifier checked this box.
   [~] Instructions executable by an agent without oral context — `census/round-21/run-acceptance.py` (prints its own usage), `census/round-21/accepted-matrix.json` (3/3 sources, each 18/18, all matched, summaries equal), `census/round-21/remote-source-after.json` (18/18, inputs unchanged). Round 26 adds `tools/souji-axis-check.py` (`claims=3 flags=0`) and `tests/fixtures/r26-axis-check.py` (`cases=12 pass=12 control=FALSE-GREEN-REJECTED`), but the fixture needs an explicit `--tool PATH` and neither is in the SKILL.md Gate registry. No non-author verifier checked this box.
   [~] No cross-domain bleed (PROVINCE.md still accurate) — `PROVINCE.md:161` Round21 privacy boundary, `.ufo/waves/round-21/w1/ConnSiblingOverlap.md`, `corpus/lessons/round-21.md:38` Boundaries. The round-26 committed delta is lane-internal only and the campaign source was opened read-only. No non-author verifier checked this box.
   ```

   Corresponding `SHONEN.md` checklist form (unchanged bytes this round; no `[x]`
   may be written by the lane):

   ```
   - [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
     SKILL.md Decision tables/Error patterns/Checklists/Gate registry; corpus/SOURCES.md S100-S103; corpus/lessons/round-21.md Gate
   - [~] At least one end-to-end domain task executed and logged in LOG.md
     LOG.md:362 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed)
   - [~] Instructions executable by an agent without oral context
     census/round-21/run-acceptance.py; census/round-21/accepted-matrix.json (3/3 sources, each18/18); census/round-21/remote-source-after.json
   - [~] No cross-domain bleed (PROVINCE.md still accurate)
     PROVINCE.md Round21 privacy boundary; .ufo/waves/round-21/w1/ConnSiblingOverlap.md; corpus/lessons/round-21.md Boundaries
   ```

6. **The r25 D4 route is NOT discharged by round 26.** D4 asked for the four
   boxes to become non-author-checkable "next round"; r26 is that next round and
   it produced a non-author verifier (`@m_kfc`, commit `e78ac7c`) that verified
   the three claims and the discernment table but **declined the box promotion
   check** — "no non-author promotion check claimed ... full promotion checkability is operator-owned"
   (`corpus/lessons/round-26-verifier-spotcheck.md:10`). Under
   `PROTOCOL.md:66-68` a `[x]` needs a named non-author `<id>` writing it; a
   lane-dispatched seat (including this one) is still the lane. **No box moves to
   `[x]` on r26 evidence.** The three prerequisites that r26 could still close
   from the lane side, in order of cheapness: (i) land the r26 LOG block at the
   tail of the lane `LOG.md` (box 2 becomes checkable against r26's own record);
   (ii) land the two `SKILL.md` Gate-registry rows for
   `souji-axis-check` / `r26-axis-check` from
   `.ufo/waves/round-26/w1/axis-check-docs.md:67-68` (box 3 becomes checkable
   without oral context); (iii) have a non-author verifier check the four boxes
   and write `[x] <id>` — promotion itself, then `SHONEN.md` deletion and the
   `MANIFEST.json` rank update, is operator-owned and outside the lane's write
   scope.

7. **Two adjacent hygiene items the non-author reviewer will meet** (reported,
   not acted on — outside this seat's write scope and not box-specific):
   the lane has **no `.gitignore` at HEAD**, while untracked `__pycache__/`
   trees (`tools/`, `tests/fixtures/`) and the untracked
   `census/operator-sweep-20261019/` tree remain in the working tree; the r26
   verifier spot-check routes both (its defects 1 and 3). A `[x]`-grade box-3
   check runs the fixtures in a clean `/var/tmp` world and should be run from a
   committed tree, so these residue paths should be swept first.

## Attack log

None — this seat read committed bytes and executed two read-only instruments; no
frozen predicate, target, case set or axis is challenged here. F5's report-ready
lines are a wording/pointer upgrade for the lane report's `## SHONEN` section,
not a change to any frozen counter.
