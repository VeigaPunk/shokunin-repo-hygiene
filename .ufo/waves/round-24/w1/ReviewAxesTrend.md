# ReviewAxesTrend — souji r24 w1

## Status

STATUS: PASS — all three deliverables answered from bytes opened this run at lane HEAD `f9db2181647d91470a724a12d626bd6106805076` (base `a65fac98964b445758e94c805728c9a19d302ff8`). As planned, r24 earns `expansion: improved` only through a capability or a frontier move, not through "F2 entries 3→4". `quality: improved` needs a work item the plan does not yet contain.

## Evidence

- `git rev-parse HEAD` → `f9db2181647d91470a724a12d626bd6106805076`; `git --version` → `git version 2.56.0`.
- `rg -n '^verified-at' corpus/knowledge/`: three entries still pin Git 2.55.0, while the host runs 2.56.0:
  - `git-auto-maintenance-prunes-worktrees.md:2` "verified-at: 2026-10-19 — host git 2.55.0; source tag v2.55.0"
  - `git-grace-periods-and-expire-to.md:2` "verified-at: 2026-10-19 — installed Git man pages 2.55.0; host git 2.55.0"
  - `git-repo-structure-readonly.md:2` "verified-at: 2026-10-20; host Git 2.55.0 (package 2.55.0-1), web docs 2.56.0"
- Hand derivation of the C2 base state. This is my own read-only `python3 -B` parse of `git show a65fac9:corpus/README.md` plus `corpus/knowledge/*.md`. It is **not** the frozen C2 tool. Output:
  - `md entries 12 grounded {count-objects-garbage-readings-r25.md: F2, quarantine-origin-record-fields-r24.md: F4, quarantine-staging-no-copy-r23.md: F4, repo-size-census-readonly.md: F2}`
  - `count-objects-garbage-readings-r25.md F2 entries-cell rows: NONE -> MISSING-FROM-MAP`
  - `repo-size-census-readonly.md F2 entries-cell rows: NONE -> MISSING-FROM-MAP`
  - `F2 rows: [(40,...), (68,...), (217,...)]`
  - [INFERENCE] The frozen tool, if it is faithful to the prereg, would read `grounded=4 … mismatches=2` at base.
- SHONEN pointers checked:
  - `git cat-file -e HEAD:<p>` returns yes for `census/round-21/run-acceptance.py`, `census/round-21/accepted-matrix.json`, `census/round-21/remote-source-after.json`, `.ufo/waves/round-21/w1/ConnSiblingOverlap.md` and `corpus/lessons/round-21.md`.
  - `LOG.md:362` is "## 2026-10-19 — operator sweep (execution): root-wide receipts + home-wide cache/tmp cleanup".
  - SKILL headings are present: `SKILL.md:42/78/147/167` (Decision tables, Error patterns, Checklists, Gate registry).
  - S100–S103 are at `corpus/SOURCES.md:120-123`.
  - `PROVINCE.md:161` reads "### Round21 privacy boundary". `corpus/lessons/round-21.md:25` reads "## Gate".
  - `git log -- SHONEN.md` → last change `4eb2fda 2026-10-21 round-21`.

## Findings

### 1. The `improved` rule per trend, why r23 was graded `unprovable-but-better`, and what r24 needs

**Fleet rule** (`/home/vgpnk/Projects/shokunin/LEARNING.md`):

| Trend | Rule (LEARNING.md) |
|---|---|
| expansion | :33 `improved` when "net new admitted entries on uncovered ground, each citing its coverage-map row". The observable column on the same line also lists "frontier areas entered; new kinds of source; a capability admitted to `SCORECARD.md`". |
| quality | :34 "a weaker entry is superseded by a stronger one, or stale entries re-verify, with no admitted entry failing its re-check" |
| discernment | :35 "the spot-check agrees with the gate on admits *and* rejects, or a disagreement becomes a lesson that adds a grounded `QUALITY.md` criterion" |
| trade guard | :37-38 "`expansion: improved` with `quality: harmed` is a trade, reported as a trade, never admitted." |
| outside judgment | :46-48 "An exploratory round claim (`unprovable-but-better`) is admitted only through this gate: a named non-author reviewer" |

`AXES.md:21-22` maps the trends to axes: "Expansion ↔ `coverage` + `adjacency`; quality ↔ `depth` + `freshness` + `operability`; discernment ↔ `calibration`."

**r23 expansion → `unprovable-but-better`.** `corpus/lessons/round-23-verifier-spotcheck.md:34`: "F2 already had one entry and LEARNING's `improved` rule requires net entries on ground the map did not hold; F2 remains the same map ground." The lane had self-graded `improved (bounded)` at `corpus/lessons/round-23.md:215`, and the closure overrode it.

- **What changes it:** an admitted entry whose coverage-map row did not exist at base, or an accepted capability or frontier move. Both are covered in Finding 3.

**r23 quality → `unprovable-but-better`.** `round-23-verifier-spotcheck.md:35`: "the trend's observable is corpus-entry re-verification/deepening/supersession; no evidence here establishes that corpus quality criterion." Tools and receipts serve the operability axis. They do not count as corpus quality.

- **What changes it in r24, option (a): re-verify the three stale entries.** The three Git-2.55.0 entries listed in Evidence are stale against host 2.56.0. Re-run each entry's own `recheck:` on 2.56.0 and bump `verified-at`, with no entry failing its re-check. This is "stale entries re-verify" exactly.
- **What changes it in r24, option (b): supersede the weaker r25 entry.** Let the C1 entry, grounded in source code (`builtin/count-objects.c` / `path.c` at v2.56.0), *name and supersede* the weaker community-page reading `count-objects-garbage-readings-r25.md`. The r23 closure already found that entry's support thin at `:30`: "S118's reopened source supports the quoted threshold but does not support a garbage-field gloss."
- **Gap:** neither (a) nor (b) is a preregistered r24 claim. C1, C2 and C3 are tool, counter and receipt moves. With the plan as it stands, expect `quality: unprovable-but-better` again unless one of these lands and is recorded as such.

**r23 discernment → `improved`** (`:36`): "including both an admit and reject".

- **What r24 needs, first path (sample):** the prereg assimilation already supplies a sample at prereg `:126-128`: "At most 2 admitted, at least 1 rejected". A non-author must re-open at least one admit and one reject and agree.
- **What r24 needs, second path (lesson + criterion):** the r23 closure's routed disagreement must become a lesson and a criterion. The routed note is `round-23-verifier-spotcheck.md:41`: "Next round should reconcile the current map table with its own 'read side now holds three' prose." It needs a `## Mistakes` row plus a new `QUALITY.md` criterion citing that lesson. The last criterion is Q55 (`corpus/QUALITY.md:129`), so the next free number is Q56. C2 mechanizes the check but is not itself the criterion.

**r24 claims vs trends:**

- C2 (calibration) serves discernment.
- C3 (operability) serves quality *as an axis* but not the quality *trend* observable.
- C1 (coverage) serves expansion only as described in Finding 3.

### 2. SHONEN boxes the round touches (all currently `[~]`; file unchanged since r21 `4eb2fda`)

| Box | Current state (SHONEN.md) | r24 touch |
|---|---|---|
| :5 SKILL.md real tables / errors / checklists / cited sources | `[~]`, pointers resolve (SKILL :42/:78/:147/:167; S100–S103) | C1 adds SOURCES rows. It touches SKILL only if an F2 rule lands. A frontier move also needs a SKILL rule: `PROVINCE.md:61-62` "each row moves to Core only with an admitted `corpus/knowledge/` entry and a SKILL rule". |
| :7 end-to-end domain task logged in LOG.md | `[~]`, `LOG.md:362` resolves | C1's lane-bound measurement `census/round-24/size-census-lane.txt`. Per prereg `:67-68` it is "a figure about this repo only; no fleet figure is claimed". It is read-only, so at most it adds an own-repo task. |
| :9 instructions executable without oral context | `[~]`, round-21 runner/matrices tracked | C1 and C3 frozen CLIs with fixtures. C3 closes the r23 residual at prereg `:98-99`: "`verify` accepts a non-durable rev while `run` refuses it". |
| :11 no cross-domain bleed (PROVINCE accurate) | `[~]`, `PROVINCE.md:161` resolves | Linked worktrees border kumitate (`PROVINCE.md:80` "kumitate-shokunin locks live task worktrees during dispatch"). F2 frontier text is internally inconsistent (finding 4c). |

Promotion marks are operator-owned (`round-23-verifier-spotcheck.md:42`: "No promotion marks added; SHONEN promotion remains operator-owned."). The SHONEN evidence pointers are stale by two rounds: they cite r21 only, even though r22/r23 landed. Calibration's signal (`AXES.md:15`) is "SHONEN.md/SCORECARD entries match observed repo state". The pointers resolve, but they understate the current state.

### 3. Does "F2 entries 3→4" count as expansion? No. What would count

**Why not.** F2 is held map ground at base:

- `corpus/README.md:40` F2 row.
- `:68` "**r23: the read side now holds three entries**".
- `:217` F2 caveat row.

The linked-worktree reading is partly held already: `corpus/knowledge/git-repo-structure-readonly.md:43-44` says "Linked-worktree outputs describe the shared common store, so do not sum them as independent repositories." A fourth F2 entry is the same ground under the r23 closure's reading, so it is not `improved`.

**"3→4" is itself miscounted** (calibration):

- Only 2 of the 3 F2 entries carry a `ground: F2` front-matter line. `git-repo-structure-readonly.md` uses prose instead (`:7` "Coverage-map ground: F2 repository size census.").
- By C2's own `grounded` definition, F2 goes 2→3, not 3→4. The two counting rules for "F2 entries" disagree, so r24's report must name which one it uses.

**What would count** (strongest first):

- **(a) A capability admitted to the SCORECARD capabilities table.** Candidate: a debris census reporting count-objects `garbage`/`size-garbage`/alternates and fsck unreachable, with a measured no-write envelope and a refused `--lost-found`. It is distinct from the r13 row "repository structure census" (`SCORECARD.md:75`, refs-rooted reachable metrics).
  - It is listed in the expansion *observable* (LEARNING:33). Precedent: the r18 closure granted `improved` on capabilities alone (`corpus/lessons/round-18-verifier-spotcheck.md:139` "Three capabilities enter with committed evidence … No knowledge-entry growth is claimed").
  - Counter-precedent: the r16 closure refused it (`round-16-verifier-spotcheck.md:128` "No knowledge entry or frontier row advanced, so the LEARNING 'improved' predicate is not met"). See ATTACK A1.
- **(b) A frontier area entered.** `PROVINCE.md:67-68` names F2's remainder as "whole-workspace size attribution and unreachable-object census remain frontier". C1 counts fsck unreachable. Moving "unreachable-object census" into Core needs three things together: an admitted entry, a SKILL rule (`PROVINCE.md:61-62`), and a map row.
- **(c) A new edge-class row that did not exist at base.** Precedent: r17 added "F1-jj jj-colocated lane repos (edge class of F1)" (`corpus/README.md:216`). Its closure (`round-17-verifier-spotcheck.md:143`) graded "expansion: improved. The admitted knowledge entry `jj-colocation-receipts.md` covers new ground (F1-jj, PROVINCE boundary)".
  - The r24 analogue would be an `F2-wt` row: linked-worktree common-dir reads, i.e. the `worktrees/<id>/refs` → `garbage: 1` false positive the prereg probe recorded at `:15-17`. That probe is design input, not claim data.
  - Bar for the row:
    - It is absent at `a65fac9`.
    - Its content is not already held by `git-repo-structure-readonly.md:43-44`.
    - The entry cites the row.
    - A non-author accepts it as distinct ground, not a relabel of F2.
  - C2 compatibility: a ground cell `F2-wt …` matches C2's token rule (prereg `:84-85` "F<k> followed by a space, `-`, or end of cell"), so a `ground: F2` entry listed there leaves C2 at 0.

### 4. Lower-severity calibration findings

**(a) C2 base discriminates.** By my approximation, the base has 2 MISSING-FROM-MAP: `repo-size-census-readonly.md` and `count-objects-garbage-readings-r25.md` appear only in the *status* cell of `corpus/README.md:68`, never in an entries cell. This is exactly the r23 routed defect, so the do-nothing control should be red. [INFERENCE until the frozen tool runs.]

**(b) C2 covers only 4 of 12 `.md` entries.** Eight entries have no `ground:` line: F1×2, F3, the F4 legacy pair, F5, F1-jj and the F2 structure entry. `mismatches=0` therefore certifies map agreement for those 4 only. The report must say so rather than claim "the map agrees". See ATTACK A2.

**(c) F2 frontier text disagrees across three places:**

- `corpus/README.md:47` "next: the /var/tmp write-safety fixture for `git repo structure`"
- `PROVINCE.md:67` "bounded structure probe and isolated write-safety fixture acquired r13"
- `corpus/README.md:486-487` "the `/var/tmp` write-safety fixture that must exclude `git fsck --lost-found`"

The first is stale. The other two are about different instruments (structure vs count-objects/fsck). This is not a C2 counter target, but it is calibration debt that C1's landing should reconcile in prose.

## Attack log

- **A1 — the expansion predicate is ambiguous** (rule level, not lane-fixable). LEARNING.md:33's observable lists "a capability admitted to `SCORECARD.md`", but its `improved when` cell lists only entries on uncovered ground. Non-author closures split: r18 said `improved` for capabilities, while r16 and r23 said `unprovable-but-better`. r24 should state *in advance* which reading it claims and accept the closure's ruling. Grading itself `improved` on a capability is the r23 overreach repeated. Route this to the fleet (protocol lane), not to a souji counter change.
- **A2 — C2 can be dodged by omission.** A new C1 F2 entry that omits the `ground:` line escapes MISSING-FROM-MAP while still being reported as "F2 entries 3→4". The kill rule (prereg `:91` "grounded(tip) < grounded(base) -> C2 fails") blocks un-grounding existing entries, but nothing requires *new* entries to be grounded. Check that every r24-landed entry carries `ground: F<k>` and that grounded(tip) = grounded(base) + new entries. This is reported, not a request to change the frozen predicate.
- **A3 — a row split could be used to manufacture expansion.** Option 3(c) is gameable if any F2 sub-topic gets its own row. The distinctness bar in 3(c) is the guard. The verdict belongs to the non-author closure, not the lane.

Residual and verification gaps:

- I did not run the frozen C1, C2 or C3 counters (their tools are not committed at HEAD).
- The C2 base figure is my approximation.
- No `recheck:` command of the stale entries was executed.
- I installed no tools, created no scratch, and wrote no files other than this report.
