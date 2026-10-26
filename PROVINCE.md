# souji-shokunin — PROVINCE

**Domain:** fleet repository & workspace hygiene (掃除) — receipt-gated
removal of stale, duplicate, and already-preserved artifacts.

## Owns

- The fleet root repo's hygiene surfaces: stray checkpoint/scratch files,
  superseded config snapshots, quarantine staging.
- Lane-repo hygiene surfaces, per-lane and only with a receipt:
  `.scratch/`, dead worktree *metadata* (`git worktree prune` after the
  commits are proven pushed or empty), duplicate configs, stale generated
  output with no live references.
- The Obsidian-preservation ledger: `corpus/knowledge/obsidian-ledger.tsv`
  (source path+hash, vault path+hash). Nothing qualifies as
  "moved to Obsidian" without a matching row.
- Dry-run censuses and removal-list proposals for operator approval.

## Work surfaces (resolve and re-verify each round)

- `$SHOKUNIN_ROOT` (fleet repo, cwd `.`)
- `$SHOKUNIN_ROOT/<lane>-shokunin/` for every rostered + probation lane
- GitHub remotes (`origin`) of the fleet and lane repos — read-only, for
  `pushed` receipt checks only
- jj-colocated lane repos (`<lane>-shokunin/.jj` beside `.git` — seven
  colocated lanes at r17, `.ufo/waves/round-17/w1/ScoutFleetJjKeep.md`): HEAD is normally detached, the
  git index is not a signal, and `refs/jj/keep/*` pins jj-created commits
  as garbage-collection grace refs — never durable receipt roots.
  Re-resolve per round; a repo without `.jj`/`refs/jj` is a plain git repo
  and every receipt path is unchanged.

## Refuses

- Git history rewrite in any repo (reset/rebase/amend of published commits)
  — operator-owned; kura is unminted.
- Credentials, secrets, tokens, vault refs — kagi-shokunin's province.
  Souji cites paths/modes only and never reads secret content.
- Operator config (`~/.config/**`, driver `scripts/`, driver runtime
  `.ufo/state/`, `.ufo/watchdog.log`).
- Any artifact whose owning lane has dirty or unpushed work touching it.
- Publishing, vault approval, remote creation — operator-owned.
- Live lane work products (current-round drafts, uncommitted reports).
- Signalling inherited or unrelated processes. Census watchdogs, selftests
  and fixtures may signal only workers they spawned, using their recorded
  identity/group/session; a listed residue process requires operator
  approval and fresh (pid, starttime, boot_id) verification (QUALITY Q32).

## Adjacency

- mori-shokunin observes fleet and host health (liveness, kill/OOM,
  runway) and reports; souji lists only its own uid's scratch residue and
  routes liveness or resource findings to mori. Complementary.
- tsukuroi-shokunin repairs host operability and never removes packages;
  souji removes files and never touches the OS.
- kagi-shokunin owns credential hygiene evidence; souji routes any
  credential-shaped finding to kagi.

## Core / Frontier / Adjacent (r12, LEARNING.md shape — appended, sections above stand)

- **Core** — the surfaces under `## Owns` and `## Work surfaces` above.
- **Frontier** (being explored; each row moves to Core only with an admitted
  `corpus/knowledge/` entry and a SKILL rule; index in `corpus/README.md`):
  - F1 git-native housekeeping vs receipts — git's own deleters
    (`maintenance --auto` worktree-prune, gc/reflog grace periods) acting on
    surfaces souji gates.
  - F2 repository size census (`git repo structure`, `count-objects`) —
    bounded structure probe and isolated write-safety fixture acquired r13;
    whole-workspace size attribution and unreachable-object census remain frontier.
  - F3 duplicate verdicts — byte-identical copies; a `duplicate` receipt
    class would be a taxonomy change (operator decision).
  - F4 restorable quarantine and file-system semantics — trash layout,
    same-device rename vs copy+remove.
  - F5 process residue (r18, observed, list-only) — current-uid deleted
    cwd links (any location) or vanished scratch argv/fd paths under
    `/var/tmp`, `/tmp`, `/dev/shm`, listed by `tools/souji-proc-census.sh`
    with `tests/fixtures/r18-proc-census.sh`; nominations, not receipts.
    Tool + gate but no knowledge entry, so frontier, not Core. Reaping,
    other uids and host-wide liveness (mori) remain outside it.
- **Adjacent** (report, don't absorb) — the `## Adjacency` rows above, plus:
  - kumitate-shokunin locks live task worktrees during dispatch; souji prunes
    only dead, unlocked registrations and never removes a lock it did not set.
  - chousa-shokunin owns the research method and source hierarchy; souji's
    `corpus/SOURCES.md` applies it and does not restate it.
  - Credential-bearing history (git-filter-repo `--sensitive-data-removal`)
    routes to kagi-shokunin and the operator; souji never rewrites history.
  Sweep r12: no sibling claims F1/F3/F4 ground
  (`census/round-12/connector.md` §1, 0 hits per frontier).

## Round 13 boundary refinement

Core now includes the bounded read-only `git repo structure --format=lines`
probe (`tools/souji-repo-structure.sh`, sourced entry
`corpus/knowledge/git-repo-structure-readonly.md`). This reports reachable
objects, not recoverable disk space and not removal authorization. F2 as a
whole stays frontier. Evidence-integrity checking is limited to souji's own
receipt/certification fragments; it does not become fleet orchestration or
an independent promotion authority.

## Round 14 boundary clarification

The census must refuse credential-store roots, ancestor roots and known
aliases before enumeration; this is a refusal fence, not credential hygiene
or a secret-content scanner. Kagi retains credential operations. Local
declared-dependency eligibility checks serve souji's own evidence fragments
and do not infer historical command execution or acquire kumitate's fleet
orchestration authority. Known namespace checks are not a universal defense
against hostile bind mounts, hardlinks or concurrent filesystem replacement.
R13's unexercised quarantine sites remain unproved; deletion certification
stays OFF and K5 stays HELD. Source and routing rationale:
`corpus/lessons/round-14.md`; `.ufo/waves/round-14/w1/SiblingOverlap.md`.

## Round 17 boundary refinement (jj-colocated lanes)

Core now includes (candidate; admission pending the non-author closure) the bounded jj receipt-root rule (entry
`corpus/knowledge/jj-colocation-receipts.md`, the matching SKILL rule,
fixture `tests/fixtures/r17-jj-receipts.sh`): in a colocated repo the
durable receipt roots are every ref except `refs/jj/*`
(`for-each-ref --exclude='refs/jj/'`) — `refs/stash`, `refs/original` and
every other ref keep their pre-r17 root status, so a repository without
`refs/jj` produces byte-identical output. `refs/jj/keep/*` is jj's
garbage-collection grace ref, never a receipt of record: an
absent-worktree head held only by keep refs is NOT-SAFE, never
`SAFE(metadata-prune)`. The unpushed-touching refusal additionally refuses
a keep-only commit only when it introduces novel content at the target
(`C:<path>` exists and no remote-reachable blob at the path matches);
keep-only deletions and identical-content predecessors do not refuse, and
a git failure keeps the existing history-unverifiable path. The census
`unpushed` column stays branch-based and reads 0 while this lane holds
keep-only commits — disclosed, not widened. This is not a jj capability:
souji's tools never invoke `jj`, commits stay operator/helper-owned, and
`## Refuses` is unchanged. F1 as a whole stays frontier; how long jj keeps
a `refs/jj/keep/*` ref remains unmeasured.

## Round 19 boundary refinement (F5 observation surface)

F5 process residue now has an admitted knowledge entry
(`corpus/knowledge/process-residue-observations.md`, S082–S088) and a matching SKILL
rule. The *observation* surface — the own-uid cwd/argv/fd listing produced by
`tools/souji-proc-census.sh` and gated by `tests/fixtures/r18-proc-census.sh` — is Core.
The earlier frontier sentence saying F5 has no knowledge entry is superseded for that
surface only. Reaping stays outside the lane: operator approval, fresh (pid, starttime,
boot_id) verification at act time and LOG receipts are required; other uids and host-wide
liveness remain mori's ground. F1, F2, F3 and F4 are unchanged.

## Round 20 boundary precision (supersedes broad r19 adjacency wording)

The F5 observation surface remains Core, list-only, on eligible readable own-uid
candidates; self/descendants recognized by the bounded parent-chain snapshot are excluded, and unreadable/racing entries skipped. Reading raw
argv before output redaction is part of the actual tool boundary, not secret-free
inspection or a universal redaction guarantee. The complete owned-code read-set and
source/fixture bindings are appended in `corpus/knowledge/process-residue-observations.md`.

Other uids are outside this tool; the r19 sentence assigning all other-uid work to Mori
does not adjudicate its province. Health/liveness/resource findings may route to Mori,
host repair to Tsukuroi and credential concerns to Kagi; contested scope stays with the
operator. F5 reap and NAMESPACE_SHA256 remain HELD under the specific round18 requests.
Process listings never authorize killing, quarantine or deletion; certification OFF,
K5 HELD. This round repairs evidence/consumer contracts only and acquires no cleanup,
host-management or fleet-orchestration authority.

### Round21 privacy boundary

The Refuses policy is not proof that the scanner avoids raw private values:
it still reads raw eligible same-uid argv/fd paths. R21 repairs the reason
output using the shared secret patterns, secret-bearing argv provenance and
a 160-byte bound, tested only on fabricated inputs through --reason-only.
Historical exposure, unknown/encoded secret syntax and universal output
privacy remain unproved. Operator/Kagi retains exposure assessment; no
private snapshot or live-process inspection is authorized by this repair.
See S100/S101, QUALITY Q49 and the r21 section of
`corpus/knowledge/process-residue-observations.md`. List-only, inherited reap
and NAMESPACE holds, certification OFF and K5 HELD are unchanged.

## Round 29 boundary note (F3 duplicate verdicts)

F3 now holds two admitted, re-grounded entries — `corpus/knowledge/duplicate-verdict-identity.md`
(S216, S217, S218) and `corpus/knowledge/duplicate-verdict-byte-equality.md` (S219, S218) — beside the r12 held entry `corpus/knowledge/dupe-finders-detect-then-act.md`. The
identity half is the `link(2)`/`statx(2)` rule: two names may be one file, so a duplicate
verdict compares inodes (`stx_ino`, `stx_nlink`), never path strings. The byte-equality half
is the documented three-valued `cmp(1)` contract: 0 same, 1 different, 2 trouble — exit 2 is
trouble, never "different". Broder's resemblance and containment are vocabulary only.

What F3 does **not** hold: no `duplicate` receipt class (a taxonomy change, so an operator
decision — `## Core / Frontier / Adjacent` above at `:69-70` is unchanged), no
near-duplicate threshold (document-similarity ground sits outside this frontier's
byte-identical scope), and no tool change — nothing in `tools/` acquires a duplicate
verdict. The round-29 SKILL classify row states the rule; it creates no receipt and no
runnable verdict.

Core and Frontier are otherwise unchanged: Core is the `## Owns` and `## Work surfaces`
list above (`:60`), and this round adds no entry to either; F3 stays frontier. Certification
OFF, K5 HELD. Sources: `census/round-29/records/preregistration.txt` claim C3; the two
entries and their Gates.

## Round 30 boundary note (F1 keep-ref expiry)

F1 now holds a measured entry — `corpus/knowledge/jj-keep-ref-expiry.md` — beside the four
entries its map row at `corpus/README.md:39` already named. One entry does not promote F1 to
Core: Core stays the `## Owns` and `## Work surfaces` list above (`:60`), the F1 row keeps the
status `frontier, entries held`, and this round adds nothing to either list. What the entry
records is the git-side lifetime of a keep ref: `git gc --prune=now` leaves a `refs/jj/keep/*`
ref in place, `jj util gc --expire=now` removes the ref of an abandoned commit while an
operation still names it, `jj op abandon ..@-` before a second `jj util gc --expire=now` leaves
two keep refs where eight stood, and the two-week default is the threshold that keeps a ref
until the lever is pulled. What it does not
record: jj's own store GC stays out of scope — this lane runs neither `jj op abandon` nor
`jj util gc` on a lane repository, acquires no authority to, and leaves the operator's store
alone; the object-prune clock that follows a dropped keep ref is unmeasured here; and no
receipt tool changes, so the r17 receipt rules stand unchanged. Certification OFF, K5 HELD.
Sources: `census/round-30/records/preregistration.txt` claim C3; the entry and its Gate; the
run record `census/round-30/records/jj-keep-expiry-run.txt`.

## Round 31 boundary note (F1 object lifetime)

F1 now holds a measured entry — `corpus/knowledge/jj-dropped-keep-object-lifetime.md` — beside
the four that carried the ground before it and the r30 keep-ref lifetime entry, all named by its
map row at `corpus/README.md:39`. The entry answers what the r30 note left open: after a
`refs/jj/keep/*` ref naming an abandoned commit is removed, that commit's object can still be
held, and three recordings isolate one holder each — a keep ref naming a descendant (the `solo`
arm keeps the object until those refs are deleted), a live descendant commit whose refs and
operation log keep the set alive (the `descendant` arm), and a reflog entry naming the commit
(the `reflog-only` arm, where the object goes only once every reflog entry naming it is expired
before the prune). Expiring the reflog is not by itself a removal: in the first two arms it left
the object present. A fourth holder is sourced, not measured: the object's own modification time
inside the two-week `gc.pruneExpire` window (`git-gc(1)`). One consequence is boundary, not
authority: an object that is present is not evidence of a completed deletion, so a receipt must
name the expiry and the prune date it observed, and the deletion it observed is one the lane ran
or whose argv it recorded. One entry does not promote F1 to Core: Core stays the `## Owns` and
`## Work surfaces` list above (`:60`), the F1 row keeps the status `frontier, entries held`, and
this round adds nothing to either list. What it does not record: which reflog file carries the
naming entries, git's cruft-pack handling of unreachable objects, and the real 90/30-day windows
(sourced from git-reflog(1) and the `gc.*` config, not waited out). Nothing in `tools/` changes —
no receipt class, gate or verdict is added, jj's store GC stays outside this lane, and the r17
receipt-root rule is untouched. Certification OFF, K5 HELD. Sources:
`census/round-31/records/preregistration.txt` claim C3; the entry and its Gate; the run record
`census/round-31/records/jj-object-clock-run.txt`.

## Round 32 boundary note (F1 mtime clock)

F1 now holds a measured entry — `corpus/knowledge/jj-abandoned-object-mtime-clock.md` — beside the
six entries its map row at `corpus/README.md:39` already named, and it measures the one holder the
r30 and r31 notes called sourced rather than measured: the abandoned commit's own modification
time. With the keep refs and the reflog entries naming the object gone, the fixture's five arms
isolate that clock — a recent object and an old one in separate repositories and in one, under a
default `git gc`, under `gc.pruneExpire=never` and under `gc.cruftPacks=false` — and the record's
`where` field separates an object kept loose from one kept inside a cruft pack, whose `.mtimes`
file carries the clock per object (sourced in the entry's Gate). Two boundary consequences follow,
and they are the r31 ones restated: an object that survives a prune is not evidence that a deletion
completed, because the prune date may simply be older than the object's mtime or `gc.pruneExpire`
may reach it; and absence is not proved by an object count the lane did not run. What this does not
record: which reflog file carries the naming entries, the real 90/30-day windows (sourced from
git-reflog(1) and the `gc.*` config, not waited out), the fleet exposure numerator, and jj's own
store GC, which stays outside this lane — no `jj op abandon` and no `jj util gc` runs on a lane
repository and the operator's store is left alone. One entry does not promote F1 to Core: Core stays
the `## Owns` and `## Work surfaces` list above (`:60`), the F1 row keeps the status
`frontier, entries held`, and this round adds nothing to either list. The round's one tool change is
`tools/souji-record-contract.py`, a record-versus-contract check that creates no receipt class, no
receipt and no deletion verdict; the r17 receipt-root rule is untouched. Certification OFF, K5 HELD.
Sources: `census/round-32/records/preregistration.txt` claim C3; the entry and its Gate; the run
record `census/round-32/records/jj-mtime-clock-run.txt`.

Round 32 attempt-2 corrections (append-only; wave a2w1 `.ufo/waves/round-32/a2w1/SwarmCritic20.md` F15-F16):
the sentence "The round's one tool change is `tools/souji-record-contract.py`" holds for this note's claim C3
only — round 32's claim C2 (commit 98e5203d45b4e419a9e72801733d93303acc7ebd) changed 12 files under `tools/`
and 15 fixtures so that their scratch follows `TMPDIR`, and `tools/souji-record-contract.py` was added earlier,
at the preregistration commit 3ec84fc81b3243429c834a051880b0bcde06291c; attempt 2 then restored the write-scope
strength of `tools/souji-receipt-run.py` (`OUT-IN-GIT-TREE`, wave a2w1 `SwarmReviewer13.md`) and reverted
`tools/souji-evidence-cache.py` to its base bytes, because two registered gates pin that file's digest
(wave a2w1 `SwarmExecutor16.md` H1-H2). None of these
changes creates a receipt class or a deletion verdict. The clause "absence is not proved by an object count the
lane did not run" names no count; read it as the r31 rule — a receipt must name the expiry and the prune date it
observed. The opening clause "the one holder the r30 and r31 notes called sourced rather than
measured" is the r31 note's wording only; the r30 note called the object-prune clock unmeasured
(wave a2w1 `.ufo/waves/round-32/a2w1/SwarmReviewer27.md` finding 5).
