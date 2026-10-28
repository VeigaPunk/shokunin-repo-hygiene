# Round 37 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Scope: souji round 37, hyaku run 11, attempt 1. Lane base `0d974ffcb7dfb70617947531cab2d7e96cd8f9fd`;
lane HEAD and `origin/master` at closure `cb443f5499fe4ccaa1f1f035050b0752aefadd92`. Report
`.ufo/reports/round-37/souji.md` (last filed `7c63d1d9a80ac3d187874b353f4e4db1ca9822f6`). This
reviewer ran no lane gate (PROTOCOL.md §Gate standard, Closure consequence): every claim that
rests on a lane-owned instrument is evidence-verified against its committed receipt, and the
static facts around it are re-derived independently. Commands below were run 2026-10-28 from
`/home/vgpnk/Projects/shokunin` (fleet root) and `/home/vgpnk/Projects/shokunin/souji-shokunin`
(lane), read-only.

## Conformance (step 1)

| check | command | observed | verdict |
|---|---|---|---|
| report path + attribution | `git log --format='%an <%ae> %H' -- .ufo/reports/round-37/souji.md` | 10 commits, all `souji-shokunin <souji@shokunin.local>`; first `1f344c9c`, last `7c63d1d9` | pass |
| cited lane commits exist and are ancestors of the branch | for every 40-hex and 7-hex hash in the report: `git -C souji-shokunin cat-file -t <h>`; `git -C souji-shokunin merge-base --is-ancestor <h> master` | 11×40-hex + 19×7-hex, all type `commit`, all ancestor of `master` | pass |
| lane pushed, no uncommitted round work | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git -C souji-shokunin status --porcelain`; `git -C souji-shokunin ls-remote origin refs/heads/master` | `branch=master local=cb443f5 remote=cb443f5 ahead=0 behind=0`; porcelain empty; remote `cb443f5499fe…` | pass |
| `SHONEN` heading, one line per box | `grep -n '^## SHONEN' .ufo/reports/round-37/souji.md` → 149; four following `- [~]` lines | `## SHONEN` + four `[~]` lines, each with a resolvable pointer; no `[x]` | pass |
| SHONEN.md not edited | `git -C souji-shokunin diff --stat 0d974ff cb443f5 -- SHONEN.md` | empty | pass |
| prompt carries the template contract | `.ufo/prompts/souji-round-37.md` vs `templates/round-prompt.md` (`render_prompt()` substitutions, whitespace-normalised line diff) | only the rendered repo path differs; §1–§5 verbatim; §6 hyaku addendum appended (64–128 seats, 256 ceiling, ≥25 % attack, run-11 route map) | pass |
| L2 route map vs MISSION | `MISSION.md:53-65`, `shokunin.conf` | MISSION states the ≥8-one-batched-call floor and class-level buckets it calls *advisory*; `shokunin.conf` carries no role pins; the prompt's concrete alias map therefore contradicts nothing | pass |
| report contract sections in order | report §Work performed … §Trend verdicts, §SHONEN before the errata | present, in order; errata appended after the filed bytes | pass |
| fleet-repo write scope | `git log --since=2026-10-28T12:00 --author=souji --name-only` | `.ufo/prompts/souji-round-37.md` (`2edd8931`), `.ufo/reports/round-37/souji.md` ×10 | minor defect (R8) |
| waves on disk | `souji-shokunin/.ufo/waves/round-37/{w1,w2}`; `w1-dispatch.json`, `w2-dispatch.json` | 37 and 32 seat specs (`total: 37` / `32`), policy `waveMinLanes 32 / waveMaxLanes 64`, 37 `w1/*.md` + 32 `w2/*.md`; `.gitignore:1` is `.ufo/waves/` as the report discloses | corroborated (untracked, disclosed) |
| driver digest | `.ufo/watchdog.log` lines 1841, 1847 | `2026-10-28T12:14:23-03:00 launch souji round=37 pgid=3758298 driver=hyaku-inline attempt=1`; `2026-10-28T13:15:38-03:00 complete souji round=37; hyaku-inline attempt=1` | pass (log is mutable; this digest is the pointer) |

Report is real, not a marker: it names work, evidence pointers, nine lane commits and a checkable
citation. Status `ok`.

## Per-claim re-check

### C1 calibration (lowest non-retired axis, score 7) — **re-measured**

Register `census/round-37/citation-cells.tsv`: 11 cells (`wc -l` 12 incl. header). Independent
re-derivation (this reviewer's own script, not `tools/souji-citation-reconcile.py`): for each row,
count the anchor in the named file at a revision, require exactly one hit, the `expected` token in
that line, the `stale` token absent, the receipt path named in the line, and the `expected` token
present in the receipt blob at `1e771ed59301ed10f68e22d4edf35d5218bacf1a`.

```
at 0d974ff (base, final register): cells=11 mismatches=11
at cb443f5 (tip, final register):  each cell anchors=1 exp=True stale_absent=True
                                   receipt_named=True receipt_has_exp=True  (11/11 -> mismatches=0)
```

Reported before→after `SUMMARY cells=11 mismatches=11` rc 1 → `cells=11 mismatches=0` rc 0 plus
fixture `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED`: **agrees**. `c1-after.txt` names
`93a10b6`; `git diff --stat 93a10b6 cb443f5 -- tools/ tests/ census/round-37/citation-cells.tsv`
is empty, so the receipt describes the tip. The fixture carries 16 distinct case ids
(`tests/fixtures/r37-citation-reconcile.py`), matching the receipt. The two selftest-arm cells
(C1-10, C1-11) are receipt-backed: the r36 `c2-after.txt` blob at `1e771ed` carries
`cases=9 pass=9`, and `SKILL.md:247` carries the same token.

Caveat (R7): the report's "the frozen nine-cell register reads 9 at the base and 3 at the landing"
is revision-sensitive. At `e987a27` the frozen register's three defective cells are exactly
C1-5 (unnamed receipt), C1-6 and C1-7 (non-unique anchors) — matching the counter's 3; at
`0be9bd0` a plain anchor count finds **four** non-unique anchors (C1-1 gains two mentions once the
reconciliation table lands). The number is right for the revision the receipt names; the prose
should name it.

### C2 operability (score 8) — **evidence-verified + static re-derivation**

`census/round-37/records/c2-after.txt` (`93a10b6`): `SUMMARY cases=12 pass=12 fail=0 base_fail=9
escapes=9 control=ESCAPE-REPRODUCED`, rc 0 — matches the report. `tools/souji-worktree-drift.py`,
`tests/fixtures/r37-drift-escapes.py` and the register are byte-identical from `93a10b6` to the
tip, so the receipt covers the tip. Static re-derivation of the claim's mechanism:

```
git show 1e771ed:tools/souji-worktree-drift.py | grep -c 'RECORD-OUTSIDE-ROOT|open_nofollow|CHILD_ENV'
  -> 0        (the r36 blob has none of the guards: the 9 base escapes are plausible, not asserted by me)
grep -n 'CHILD_ENV|open_nofollow|RECORD-OUTSIDE-ROOT|JSON-HARDLINKED' tools/souji-worktree-drift.py
  -> 57 CHILD_ENV, 193 open_nofollow, 231/248 RECORD-OUTSIDE-ROOT, 341 JSON-HARDLINKED; Refusal -> rc 2 (365, 368-370)
grep 'out\["' tests/fixtures/r37-drift-escapes.py
  -> 12 cases incl. record-escape, json-write-escape, json-hardlink, record-fifo,
     json-gitfile-write, json-symlink-child, record-symlink, env-witness, measured
git diff --stat 0d974ff cb443f5 -- tests/fixtures/r36-worktree-drift.py tests/fixtures/r36-report-gate.py
  -> empty    (r36 consumers byte-identical; consumers-after.txt 12/12, 21/21, 4/4)
```

The claim holds at the receipt revision and at the tip. Defect (R2): the report table and the
SCORECARD row name measured commit `0be9bd0`, where the surface was **not** the measured one —
`git diff --stat 0be9bd0 cb443f5 -- tools/souji-worktree-drift.py tests/fixtures/r37-drift-escapes.py`
is `2 files changed, 85 insertions(+), 8 deletions(-)` (21 lines in the tool, 72 in the fixture; A2.7 landed at `4c257b7`), and the lane's own erratum 9 concedes the landing
blob failed three of the later cases.

### C3 coverage (score 8) — **evidence-verified**

`census/round-37/records/c3-after.txt` (`e6be059`): `mutants=6 killed=6 survived=0`, rc 0; base
control `c3-before.txt`: `mutants=6 killed=4 survived=2`, rc 1 — matches the report.
`tests/fixtures/r37-drift-mutants.py` defines exactly six single-defect mutants (`MUTANTS`,
lines 32–49) and requires a `SUMMARY cases=… fail>0` line before recording a kill (lines 73–101),
so a crashing fixture cannot score as a kill. The discrimination fixture is byte-identical from
`0be9bd0` to the tip and unchanged after `e6be059` (`git log --oneline e6be059..cb443f5 --
tests/fixtures/r37-drift-discrimination.py tests/fixtures/r37-drift-mutants.py` is empty), so the
receipt describes the tip. The r36 fixture is byte-identical (above).

## Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | **improved** | C1 re-measured 11 → 0 mismatches against the committed register and receipt blobs; two selftest-arm cells added and receipt-backed |
| operability | **improved** | C2 evidence-verified 12/12 base_fail=9 escapes=9; the r36 tool blob carries none of the new guards; r36 consumers 12/12, 21/21, 4/4 |
| coverage | **improved** | C3 evidence-verified 6/6 killed vs 4/6 on the r36 fixture; the battery cannot count a crash as a kill |
| depth / freshness / adjacency | unchanged | not claimed by the round; no file outside the lane's three axes moved |
| harmed | **none** | SCORECARD +40/−0, LOG +13/−0, QUALITY +8/−0, SOURCES +4/−0 (`git diff --numstat 0d974ff cb443f5 -- …`); SKILL.md 7+/4− are stale-value corrections (11/11→21/21, 9/9→12/12, new r37 rows, exit map); r36 fixtures byte-identical; r35 census record untouched; every amendment is tighter-only or reverted-and-disclosed (A2.6 at `e6be059`) |

## Discernment spot-check (LEARNING.md)

| item | decision | re-opened source | agree? | reason |
|---|---|---|---|---|
| S236 git(1) `GIT_TRACE_REFS` | admit (tier A, mined) | `MANWIDTH=100 man git`, git 2.56.0 — heading line 1212, sentence line 1213: “Enables trace messages for operations on the ref database.” | **agree** | quote is verbatim at the stated lines (9 words, ≤25); it grounds the inherited path-valued trace variable the escape fixture models, and the scope narrows it to the `GIT_TRACE` output target |
| S237 git(1) `GIT_CONFIG_NOSYSTEM` | admit (tier A, mined) | `MANWIDTH=100 man git` — heading line 1153, sentence line 1154: “Whether to skip reading settings from the system-wide $(prefix)/etc/gitconfig file.” and the adjacent “create a predictable environment for a picky script” | **agree** | verbatim at the stated lines (11 words); it is exactly the child-env neutralisation the C2 repair relies on, and the `GIT_CONFIG_GLOBAL/SYSTEM=/dev/null` handling sits beside it |
| S238 git-config(1) `GIT_CONFIG_COUNT` | reject (tier A, reason + flip) | `MANWIDTH=100 man git-config`, git 2.56.0 — heading line 405, quote lines 406–408: “all environment pairs … up to that number will be added to the process's runtime configuration” | **agree** | the page documents env-injected runtime config but says nothing that makes it reach trace2 initialisation; the lane's own probe wrote no trace while a config-file control did, and the row names a flip. Defect R5 is about the citation of that control, not the decision |

Registry: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` →
`souji ok …/corpus/SOURCES.md`, rc 0, 162 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`
= 162; base 159; malformed rows 0). S236/S237 `mined` with `used-by` `corpus/lessons/round-37.md`;
S238 `rejected`, `used-by` —.

Spot-check sample: 2 admits + 1 reject, all three re-opened. **3/3 agree.**

## Trend verdicts

| trend | verdict | evidence |
|---|---|---|
| expansion | **improved** | census 159 → 162 rc 0 (re-run by this reviewer), two new mined tier-A rows on ground the coverage map did not hold (`GIT_TRACE_REFS`, `GIT_CONFIG_NOSYSTEM`), three QUALITY criteria Q83–Q85 each citing `corpus/lessons/round-37.md`, one capability row (`self-assessment receipt reconciliation (r37)`), three registered instruments with fixtures |
| quality | **improved** | nine write escapes closed on the drift tool (`c2-before` 3/12 → `c2-after` 12/12, r36 consumers unchanged and byte-identical); six frozen mutants now killed (4/6 → 6/6); citation counter binds both arms; no admitted entry fails its re-check |
| discernment | **improved** | this spot-check agrees on all three gate decisions; the round's own wave falsified its instruments and it disclosed every unclosed finding as a named limit rather than claiming a fix; routed r36 defects 1/3/4 are closed or explicitly narrowed |

The round re-commits its own M1 class in sibling cells (R2, R3, R7). That is a defect to route,
not a discernment harm: every sampled gate decision is right and every disagreement-class item it
found is disclosed in the lesson's `## Named limits`.

## Routed defects (status-neutral; the lane owes these in r38)

1. **Stale tip claims (report).** Line 76 says `git ls-remote … prints 131ea876… (the lane tip)`;
   errata 7, 8 and the closing record say `a269e72` = `origin/master`. At closure the lane HEAD and
   `origin/master` are `cb443f5` (`git ls-remote origin refs/heads/master` →
   `cb443f5499fe4ccaa1f1f035050b0752aefadd92`), a lane commit at 13:06:24 that predates the last
   report erratum (13:12:35) and is named in neither the report nor `LOG.md`. Append an erratum
   naming `cb443f5` and the receipt commits (`93a10b6`, `bbefcee`, `b491596`, `e6be059`, `4c257b7`).
2. **Receipt/revision pairing.** The report's measurement table and the SCORECARD `Round 37
   measurements` rows pair receipts with a revision they do not describe: C1's after cell quotes
   fixture `cases=12` while `c1-fixture-after.txt` (at `939a8fc`) reads 16/16; C2/C3 name measured
   commit `0be9bd0` while the receipts are at `93a10b6`/`e6be059`, and for C2 the tool and fixture
   changed after `0be9bd0`. Append corrected rows (SCORECARD is append-only; the report takes an
   erratum).
3. **Residual stale counts — the round's own M1 class, left in sibling cells.** SCORECARD C2
   before cell: "reproduce six escapes" against its own `escapes=9`; `LOG.md` C2: "six escapes …
   `cases=9 pass=3 fail=6 base_fail=6`" and "the final landing `b491596`" (the final receipt is
   12 cases / base_fail 9 / escapes 9 at `93a10b6`); `corpus/QUALITY.md` Q84 evidence:
   "`c2-before.txt` (4 escapes)" (the final before-control reads 9); report §Work performed live
   reading `live_regs=23 drift_rows=5` vs the committed `live-run-after.txt` `live_regs=24
   drift_rows=6`. Sweep every mention against the final receipts.
4. **In-place corpus rewrite.** `corpus/lessons/round-36.md:23` was rewritten in place
   (`cases=20` → `cases=21`, `git diff 0d974ff cb443f5 -- corpus/lessons/round-36.md` shows one
   deleted line) under an "in-place branch" the r37 prereg asserts (prereg:25). CORPUS.md requires
   corrections as new entries, never rewrites. Keep the settlement block, but land the correction
   as an appended entry in r38 rather than a rewrite.
5. **Unreachable pointer in a corpus row.** SOURCES S238 `teaches` cites
   `.ufo/waves/round-37/w1/W1ScribeGate.md` (gitignored, unreachable at closure) and a byte count
   (9812 B) that disagrees with the lesson's `## Gate` (11365 B) for the same control. Point at
   the committed counter arm (`c2-after.txt`, `case-env-witness=PASS`) and drop or commit the
   control; a numeric claim needs its command.
6. **Docstring vs code exit map.** `tools/souji-worktree-drift.py` docstring's exit-2 enumeration
   names only RECORD-MISSING/MALFORMED/EMPTY/usage, while the code returns 2 for
   RECORD-OUTSIDE-ROOT, JSON-HARDLINKED, JSON-INSIDE-MEASURED-TREE and JSON-UNWRITABLE (the SKILL
   row was updated, the docstring was not). C2 is "the write envelope matches its docstring"; make
   the enumeration match.
7. **Revision naming for the frozen-register number.** "reads 9 at the base and 3 at the landing":
   name the revision (3 at `e987a27`, the revision `c1-before.txt`'s A1.1 block reports; 4
   non-unique anchors by plain anchor count at `0be9bd0`).
8. **Prompt committed by the lane.** `2edd8931` commits `.ufo/prompts/souji-round-37.md` under the
   lane identity; PROTOCOL.md assigns `.ufo/prompts/*.md` to the integrator's round-integration
   commit, and a lane's main-repo commit is pathspec-limited to its own report. Durable and
   harmless, but it is a scope deviation to record; do not repeat it.

## Notes for the operator

- No promotion or mint is claimed or implied; all four SHONEN boxes are `[~]` (author-asserted)
  with pointers, and all four look checkable by a non-author. Promotion remains operator-owned.
- No axis is harmed and every declared claim verifies at the revision its receipt names (and, for
  C1–C3, at the tip: tools, tests and register are byte-identical from the receipt revisions to
  `cb443f5`). Verdict: admitted.
