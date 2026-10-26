# SwarmConnector28 — sibling-overlap re-scan after landing (wave 2, round 31)

Seat: sibling-overlap re-scan (read-only) over every lane under /home/vgpnk/Projects/shokunin/*-shokunin except souji-shokunin. Surfaces scanned per sibling: PROVINCE.md, SKILL.md, corpus/README.md, corpus/knowledge/ (20 sibling lanes; souji excluded). Contract files read first: census/round-31/records/preregistration.txt and amendments.txt (A0-A5). Lane surface anchors used: C3 = corpus/knowledge/jj-dropped-keep-object-lifetime.md; C2 = tools/souji-landing-gate.py; C1 = tools/souji-capability-cells.py.

## Status
STATUS: PASS — 20 sibling lanes scanned on the four mandated surfaces; no sibling holds the round's landed surfaces by their distinctive identifiers (LG-DANGLING-PTR, LG-SEAT-UNCARRIED, `## Seat-reported failures`, c1-cells.tsv, R30-CORRECTION, tools/souji-landing-gate.py, tools/souji-capability-cells.py). Contested/adjacent scope found in five lanes and reported below; one sibling claim (kumitate) qualifies C3's precedence result and is reported as a qualification gap, not a contradiction. No attack raised; all items are independent re-derivations.

## Evidence
Commands (all read-only, grep tool, `python3 -B` not needed):
- `read` preregistration.txt + amendments.txt (first).
- `grep` across all sibling PROVINCE.md, SKILL.md, corpus/README.md, corpus/knowledge/ for:
  - `reflog|keep-ref|keep_ref|keep ref|object.?lifetime|object.?clock|recentObjectsHook|pruneExpire|colocat`
  - `LG-DANGLING|LG-SEAT|Seat-reported|landing-gate|landing gate|tokeniz|\.captured|ellipsis|printf template|letters-only`
  - `capability cell|capability-cell|supersession|SCORECARD.*literal|bound_run|unbound=|c1-cells|R30-CORRECTION`
  - literal `reflog` sweep; `util gc|keep-ref|keep_ref|refs/jj/keep|colocat` sweep over sibling knowledge dirs.
- `read` kengaku corpus/knowledge/tb2-git-leak-recovery-grader.md:25-53; kaidoku PROVINCE.md:1-23; kumitate corpus/knowledge/agent-isolation-substrates.md, jj-workspace-seat-containment.md; mori corpus/knowledge/jj-branch-anchor-r17.md; tameshi corpus/knowledge/guard-kill-closure.md:31-47; mado corpus/knowledge/tripwire-precision-r20.md:69-72.

Result counts: no match for LG-* codes, `## Seat-reported failures`, `c1-cells`, `R30-CORRECTION`, `bound_run`, `unbound=`, or `\.captured` anywhere in sibling surfaces. `SCORECARD` matched only inside sibling-owned supersession conventions (no capability-cell rows). `reflog` matched in kengaku (claims), kasegi (usage), kotodama (usage), kaidoku (selector refusal), mado (usage). `keep-ref|keep_ref|refs/jj/keep` matched in kumitate, mado, tameshi (jj-era HEAD notes via S061), mori, kaidoku (S036).

## Findings
1. kengaku holds measured plain-git reflog/object-retention ground overlapping C3's topic but on a distinct surface (Terminal-Bench 2 git-leak grader; git 2.56.0; no jj). It is consistent with C3 roles 1-2: "neither expiring the reflog alone nor `gc --prune=now` alone closes the gap either" (corpus/knowledge/tb2-git-leak-recovery-grader.md:214-215); "the reset-away commit lives in the reflog/object store; the reflog is not a ref" (:155-156); PROVINCE.md:387-389; SKILL.md:894-907. Axis: coverage — adjacent claim, no harm, no contradiction.
2. kumitate holds jj keep-ref/snapshot/gc ground and explicitly routes jj/git internals to souji: "jj and git substrate internals → souji: `souji-shokunin/corpus/knowledge/jj-colocation-receipts.md`" (corpus/knowledge/agent-isolation-substrates.md:14-15). One generic claim qualifies C3's precedence result: "abandoned commits still remain in the repository's object store and op log; only `jj op abandon` + `jj util gc` or a separate clone excludes them from storage" (jj-workspace-seat-containment.md:102). C3 measured that with a live descendant keep ref, `jj op abandon`+`jj util gc --expire=now` does NOT remove the object (roles 3-4); kumitate's sentence omits that condition. Qualification gap, not a falsification. Axis: coverage.
3. mado observed keep-ref creation as a jj side effect: "the working copy is snapshotted before the dry-run return" with `refs/jj/keep` incremented (corpus/knowledge/tripwire-precision-r20.md:70). Compatible with C3 keeper A (jj rewrites keep refs from heads). Axis: coverage.
4. Colocation-semantics holders (none claim reflog expiry or object lifetime): kaidoku S036 "jj usually leaves Git HEAD detached" (SKILL.md:569-573); mori "A colocated .jj repo without a valid mirror/ref is unavailable, not silently graded from HEAD" (corpus/knowledge/jj-branch-anchor-r17.md:82-84); tameshi "In a colocated repository, Git HEAD is the working-copy parent `@-`" measured on jj 0.45.1 and git 2.56.0 (corpus/knowledge/guard-kill-closure.md:31-33); tabi SKILL.md:1901-1905. All consistent with C3's detached-HEAD / logs-HEAD fixture premise. Axis: coverage.
5. C2 tokenizer parallels exist but are distinct instruments, none citing souji's gate: kotoba classifies "schematic: the token contains an ellipsis (`…` or `...`) or a literal `round-N` path segment" (corpus/knowledge/checklist-execution-round17.md:156-158) with a quoted-context rule (cold-run-round11.md:337-340); revenger Q14 "an ellipsis-truncated run carries no length" (SKILL.md:160); chousa token-boundary matcher (corpus/README.md:11); kagi tokenizer last-token defect (corpus/knowledge/claim-ledger.md:355-358). Axis: operability — no overlap in holdings, no harm.
6. C1 parallels are each lane's own supersession conventions, none touching SCORECARD capability-cell rows: tsukuroi PASS(n) restatement chains (SKILL.md:689-693,1598-1600); kama row count supersessions "line 576's append-only '14 cases' is replaced by the round-18 **42/42** selftest" (SKILL.md:630); kotodama registry supersession settlement (SKILL.md:473-487); kasegi "records=40 bound=40 unbound=0" manifest binding (SKILL.md:1082); tabi declared-supersession pins (SKILL.md:1395-1499); mado source supersession ledger (SKILL.md:1973-1977); kaidoku instrument_supersessions (SKILL.md:764-778). Axis: calibration — vocabulary parallels only, no contested ground.
7. No sibling uses the round's distinctive identifiers (LG-DANGLING-PTR, LG-SEAT-UNCARRIED, `## Seat-reported failures`, c1-cells.tsv, R30-CORRECTION, tools/souji-landing-gate.py, tools/souji-capability-cells.py) — the C1/C2/M1 surfaces are held only by souji.
8. kaidoku rejects reflog selectors as mutable `--rev` aliases in its own pin gate (SKILL.md:448) — a distinct discipline (revision-pin validation), not reflog-expiry ground.

## Attack log
No attack filed. No sibling claim contradicts the C3, C2 or C1 landed entries as written; the closest item is kumitate's unconditional phrasing in Finding 2 (qualification gap), which is reported, not absorbed (per seat mandate, never absorb).

## Deliveries
- .ufo/waves/round-31/w2/SwarmConnector28.md (this report; the only deliverable of this seat).
- No tools installed; no scratch created; no writes outside the report path.
