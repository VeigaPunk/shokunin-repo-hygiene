# Sibling-overlap scan — souji round 32 (wave 1), connector SwarmConnector41

Read-only scan of the fleet for overlap/contested scope against the round's three surfaces:
(a) cruft packs / object mtimes / gc.pruneExpire / unreachable-object pruning (C3 frontier F1);
(b) scratch/TMPDIR discipline of committed tools and bwrap/strace sandbox checks (C2);
(c) capability-table count binding (C1).

Scope scanned (all sibling lanes; souji itself skipped): `*/PROVINCE.md`, `*/SKILL.md`,
`*/corpus/README.md`, `*/corpus/knowledge/*.md` for the 20 non-souji lanes, plus
`scripts/hyaku/*.sh`. Terms: `cruft`, `pruneExpire`, `mtimes`, `/var/tmp`, `TMPDIR`,
`bwrap`, `capability` (plus `mtime` for context; `mtimes`/`cruft`/`pruneExpire`
re-swept with dedicated narrow passes to guarantee the display showed every hit).

## Verdict per surface

- (a) C3 ground (git cruft packs, gc.pruneExpire, per-object `.mtimes` clock under `git gc`):
  **no sibling claim anywhere in the scanned surfaces.** The only adjacent claim is
  kumitate's jj abandoned-object persistence note (below) — same subject family
  (jj abandoned commits), no mtime-clock/cruft content. C3's frontier is uncontested.
- (b) C2 ground (TMPDIR honoring, bwrap sandboxing with /tmp,/var/tmp,/dev/shm read-only):
  dense sibling activity, all on each lane's own tools. Norms split: several lanes claim
  positive TMPDIR discipline (kama, mori, kake, tabi, kotoba); others deliberately treat
  /var/tmp as the correct scratch (kaidoku, kotodama) or /tmp (revenger, mado history);
  the fleet's own `disk-guard.sh` uses the exact `${TMPDIR:-/var/tmp}` fallback pattern C2
  labels a defect (outside souji's write scope). No sibling claims any part of souji's
  toolset, so none of this is contested ownership — it is normative adjacency, reported below.
- (c) C1 ground (SCORECARD capability cells containing integers left unbound by row-level
  records): no sibling makes the same "cell integer unbound" claim about souji's
  SCORECARD; several lanes operate sibling instruments on their own cards that bind
  capability rows/cells to runnable evidence (tameshi executable self-assessment, mori
  capability-path resolution, kama repertoire audit, chousa line/receipt binding counters).
  Same class of calibration bookkeeping, different repositories.

No contested scope is absorbed. Report follows.

## Hits (lane, file:line, claim, overlap class)

### Surface (a) — cruft / object mtime / GC pruning
1. kumitate `corpus/knowledge/jj-workspace-seat-containment.md:102` — decision-table row:
   "abandoned commits still remain in the repository's object store and op log; only
   `jj op abandon` + `jj util gc` or a separate clone excludes them from storage"
   (demo key `forget_seat_commit_in_all=yes`, sources S198/S200/S199, jj 0.46.0 docs).
   Overlap: nearest neighbor to C3's subject (jj abandoned objects' fate), but claims
   persistence/exclusion only — no mtime clock, no cruft pack, no pruneExpire. Compatible
   with C3; not contested.
2. tsukuroi `corpus/knowledge/package-state-plane.md:73-81` — "pacman preserves upstream
   file mtimes on download; **mtime ≠ datetime of the local sync**" (use `%w`/`%z`);
   same correction re-derived in `calibration-synthesis.md:98-99`, `foreign-provenance-r6.md:256-259`,
   `SKILL.md:94-98,1231-1234,1463-1465`. Overlap: same epistemic care as C3's object-clock
   claim, different object class (pacman sync dbs). Not contested.
3. mado `corpus/knowledge/province-accuracy-selfaudit.md:117-121` (and :315, reproducibility):
   mechanism claim that `git status --porcelain` refreshes the index stat cache — index
   mtime +1 s, tracked content sha unchanged (scratch proof `/tmp/w4-m4-3/gitmech/`).
   Overlap: measured "metadata mtimes move without content change" side effect; context for
   C3's clock design, not the same ground (index stat cache, not object fate). Not contested.
4. kagi `corpus/knowledge/handler-on-disk-state.md:183-189` and `surface-census.md:131-134`:
   SQLite live-file reads advance `-shm` mtime, so pins avoid mtime entirely. Same
   read-mutates-mtime theme as (3); different substrate.
5. kotoba `corpus/knowledge/substrate-pin-guard-round23.md:11-18` — omp binary mtime pinned
   ns-exact; "opencode's mtime is a 1985 packer constant and unpinnable; only its sha is
   enforced." Binary-substrate mtime limits; unrelated to git/jj objects; not contested.
6. Negative: sweep for `cruft|pruneExpire` across all 20 sibling knowledge dirs and hyaku
   scripts returned zero matches (full page-through completed). No sibling claims cruft-pack
   handling, gc.pruneExpire, or `.mtimes`-carried object clocks. C3's ground is unclaimed.

### Surface (b) — scratch/TMPDIR discipline, bwrap/strace sandboxing
7. Fleet `scripts/hyaku/disk-guard.sh:291-293` — `local base=${TMPDIR:-/var/tmp}` then
   `mktemp -d "$base/disk-guard.XXXXXX"` (same at :976 for the selftest), while :936-937
   passes `TMPDIR="$ST_BASE/tmp"` to a child. Overlap: the exact `${TMPDIR:-/var/tmp}`
   fallback pattern C2's enumeration flags, present in fleet tooling outside souji. Normative
   adjacency; outside souji write scope (reported, never absorbed).
8. kaidoku `SKILL.md:449` — scratch-root fallback `$CUSTODY_PAIR_SCRATCH` else `/dev/shm`
   else `/var/tmp` with "(`/tmp` never — EDQUOT hazard)"; repeated in knowledge entries
   (`2026-10-19-arc3-r12-go-evidence-id-domain.md:7`: "set `TMPDIR` to a directory under
   `/var/tmp` (never `/tmp`, which has a quota problem on this host)"; `...r11-inspect-artifact...md:7`;
   `2026-10-19-arc3-r3-evm-...md:7`; `...r4-evm-vyper-leg.md:7`). Overlap: a sibling norm
   that treats /var/tmp as the sanctioned scratch — directionally opposite to C2's
   read-only-/var/tmp sandbox. Lane-owned practice; not souji's to change.
9. kotodama `SKILL.md:456-459` — "Run scratch-writing tools only after `export TMPDIR=$PWD/.scratch`";
   mirror-safety leg "requires its own external temporary directory (for example `/var/tmp`)".
   Same /var/tmp-positive norm as (8).
10. revenger `SKILL.md:180-182,471-475` — registered measurement contract: `cwd=/`,
    "TMPDIR under lane-owned `/tmp/revenger-r66-*`", never the working tree. /tmp-based
    lane-owned scratch claim; divergent from the operator `/fast/scratch` directive but
    lane-local and self-consistent.
11. kama `SKILL.md:1029-1030` — grid "honors an existing caller TMPDIR rather than a
    host-specific shared root; an unusable requested root is could-not-evaluate";
    `corpus/knowledge/instrument-run-agreement.md:36-39` (fresh TMPDIR per run; state
    outside TMPDIR invisible to the tool); `corpus/knowledge/ollama-evidence-replay.md:259-261`
    (selftest temp location follows Python tempfile: TMPDIR/TEMP/TMP). Direction aligned
    with C2's target; claims about kama's own tools.
12. kengaku `PROVINCE.md:318-333` — cross-lane bwrap inventory: tameshi defect-probes
    (children under a read-only bwrap envelope) and env-diff.py (runs under bwrap);
    kumitate cap-run.mjs (bwrap `--ro-bind / / --unshare-pid ...`, tmpfs /tmp,/run, cwd
    bound rw); mado c1-r40-live-v2.py / c1-r41-globals.py (bwrap `--unshare-all
    --cap-drop ALL`, fresh /proc,/dev, tmpfs /tmp); kake sealed_count_v2.py, c42_count.py,
    c57_idresolver_gate.py (bwrap variants); mori count-c2-a1.py (bwrap `--ro-bind / /`,
    tmpfs /home,/fast); kotodama isolation-replay protocol (Tier A bwrap mount-namespace
    replay, "TMPDIR inside the sandbox"); kaidoku carrier-guard.py (records bwrap exists
    but is not used). All are claims about each lane's own tools; collectively they show a
    sibling-wide norm of bwrap sandboxes with private/read-only tmp roots — same method
    class as C2, no contested ownership.
13. kumitate `corpus/knowledge/mount-order-and-bind-scope.md:7-9` — bwrap applies FS
    operations in argument order (S095); cap-run "mounts fresh `/tmp` and `/run` tmpfs
    roots before appending bind requests" and refuses binds targeting the whole /tmp root.
    Methodological claim; compatible with C2's read-only-bind approach.
14. tameshi `corpus/knowledge/hermetic-env-differential.md:25-28` — env-diff "starts the
    selftest in a fresh bwrap scratch with a read-only root, private writable `/tmp/w`, and
    no network"; `guard-kill-closure.md:129` (bwrap envelope with env -i, private /tmp,
    isolated PID/network namespaces); `SKILL.md:1779-1785` (fixtures under env -i with
    private HOME/TMPDIR; "scrubs; it does not confine ... use `bwrap` when mutants are
    untrusted"). Aligned practice claims.
15. mori `SKILL.md:174` (selftest "(TMPDIR required, not /tmp)"), `:604-605` ("do not let
    an invalid TMPDIR fall back to /tmp"), `:606` (heavy scratch under
    /fast/scratch/hyaku/mori-r23), and knowledge recheck lines requiring
    `TMPDIR=$PWD/.scratch` with "TMPDIR must not be under /tmp" (`dispatch-ledger-r18.md:3`,
    `evidence-minimization-r18.md:3`, `freeze-order-r18.md:3`, `retention-reconciliation-r22.md:3`).
    Strongly aligned with C2's target. Caveat: mori's own r44 write-scope cells were later
    superseded (`SKILL.md:193-196`) because the counters execute ledger rows through
    `bash -c` with the caller's cwd/env — "writes only under the caller TMPDIR" was false
    as written. This is precisely the overclaim class C2 is built to catch; prior art, no
    conflict.
16. kake `SKILL.md:592-593,636-637,774-775,885-888,956-960` — citing_set fixtures under
    `--tmpdir` (scratch outside the lane), default private dir under
    `/fast/scratch/hyaku/kake-r27` removed on exit, refusal of `os.pathsep`-containing
    tmpdir. Aligned.
17. tabi `SKILL.md` registry rows (e.g. :2543, :2558-2559, :2575-2576) — "self-test writes
    and deletes only its own temporary repositories under TMPDIR"; knowledge
    `harness-hardening-round-18.md:36-39` documents browser TMPDIR = tmpdir() outside
    tmpBase and Playwright artifacts under `os.tmpdir()` (S091). Aligned claims.
18. kotoba `SKILL.md:490` — `fault_injection_corpus.sh`: "temp clones under
    `${TMPDIR:-/tmp}` (removed)"; many other kotoba verifier rows write only under
    `$TMPDIR` (:453-490). The `${TMPDIR:-/tmp}` fallback is exactly the pattern C2's
    enumeration flags (in a committed sibling tool).
19. chousa `SKILL.md:734-736` — env-pin capture covers BASH_ENV only; "`ENV`/`SHELLOPTS`/`TMPDIR`
    are named debt"; `corpus/README.md:102` notes a selftest run "under a `TMPDIR` scratch
    while the host `/tmp` quota was intermittent". Naming TMPDIR as a live env channel is
    the same awareness C2 codifies; no conflict.
20. tsukuroi `SKILL.md:2754` — child-env allowlist row: "Ambient HOME, TZ, TMPDIR, LANGUAGE
    and PATH are each a demonstrated channel (round-32 SentinelAllowKeep)" — children must
    not inherit ambient TMPDIR. Directional difference to note: C2 requires children to
    inherit the caller's TMPDIR (never /var/tmp); tsukuroi strips ambient TMPDIR from its
    probe children. Different subjects (their probe children vs C2's fixture commands), no
    conflict, but worth surfacing so C2's rule is not read as a universal convention.
21. mado historical `/tmp` scratch usage (e.g. `corpus/knowledge/gate-standing-use.md:8`,
    `province-accuracy-selfaudit.md:31`, `executor-test-sufficiency.md:17`,
    `waybar-walker-semantics.md:450`, `walker-deep.md:596`) — recorded scratch under /tmp;
    historical lane practice, not a claim on current fleet discipline.

### Surface (c) — capability-table count binding
22. tameshi `corpus/knowledge/executable-self-assessment.md:7-10` — "A standing capability row
    says what a tool can do and quotes what its command printed. A standing axis row states
    a score. Each is a claim about the repository at some revision"; rounds 46/47 re-state
    SCORECARD rows against frozen commands (`corpus/README.md:462,579,589`). Same calibration
    class as C1 (cell literals vs runnable evidence), on tameshi's own card.
23. mori `corpus/knowledge/source-drift-content-anchor-r38.md:33-35` — "Every path the
    SCORECARD capability row cites must resolve at the measured revision from the repository
    root"; plus `SKILL.md:183-196` C1 counters over ledger rows. Binding discipline sibling.
24. kama `SKILL.md:1380` — round-34 capability-repertoire audit: "the canonical repertoire
    table does not carry every demonstrated capability, or a canonical row has no resolving
    evidence pointer" (`listed L observed O missing M unsubstantiated U met True`); round-42
    C1 self-description reconcile (:1404). Same class.
25. chousa `SKILL.md:98-107` — round-31/32/40/41 counters enumerate exact binding-match
    counts (LINE_BINDING_MATCH=120/120, RECEIPT_BINDING_MATCH=8/8, CAPTURE_PIN_MATCH=12/12
    ...). Evidence-binding at cell granularity; sibling precedent for C1-style binding.
26. tsukuroi `corpus/README.md:169` — "The latest complete SKILL registry is operative; all
    earlier registry rows are explicitly historical/non-operative" plus the correction
    record at `SKILL.md:1953-1954` ("Do not copy a selftest tally into a second registry
    cell"). Meta-calibration conventions; no overlap with souji's SCORECARD cells.
27. game-dev-2d `corpus/knowledge/seed.md:20-23` — "Verified capability ladder" prose; no
    count-binding claim. audio/game-dev-3d/lore: no relevant hits in scanned surfaces.

## Notes
- No sibling lane's PROVINCE/SKILL/corpus claims ownership of souji's tools, SCORECARD,
  or counters; no contested scope. Only the /var/tmp-vs-TMPDIR norm split (items 8-10 vs
  11,15-17) and the fleet `disk-guard.sh` fallback (item 7) sit on the same *norm* C2
  asserts; none is a claim souji would take ground from.
- C3's nearest neighbor (item 1) is compatible and does not pre-empt the F1 frontier:
  kumitate claims persistence until explicit jj gc; C3 measures how the object's own
  mtime decides fate under `git gc` (cruft packs, gc.pruneExpire) once keep refs/reflog
  entries are gone.
