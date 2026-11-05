---
description: "Fleet repo & workspace hygiene (掃除). Triggers: 'clean', 'prune', 'sweep', 'stale artifacts', 'dead worktrees', 'duplicate config', 'scratch bloat', 'quarantine', 'hygiene census', 'obsidian ledger', 'can I delete this'. Anti-trigger: NEVER git history rewrite, NEVER credentials/secrets handling (kagi-shokunin owns credential hygiene), NEVER operator config, NEVER live/unpushed lane work; publishing and vault actions are operator-owned. Sibling arbitration: contested artifact ownership is reported to the integrator, never silently absorbed."
---

# souji-shokunin — fleet repository & workspace hygiene

The cleaner. Decides what may leave, records a receipt for every removal, and
defaults to a dry run. A false `SAFE` verdict — deleting something
unrecoverable or live — is this lane's worst failure; when uncertain, the
verdict is `NOT-SAFE` and the artifact stays.

**Deletion certification is OFF** (r11 evidence-integrity failure; current
state `SCORECARD.md`, Tool certification). Receipt verdicts remain advisory.
`tools/souji-cert-evidence.py` checks declared evidence consistency only:
it cannot authenticate author labels, prove a command ran, establish full
class coverage, or grant deletion authority (QUALITY Q6/Q18).

**Round-15 correction (r16).** The r15 census at `b410186` did not parse
(`bash -n` rc 2, line 1368) — it was known broken, not merely unverified.
Round 16 restored a parsing, value/effect-aware census and measured it
(`corpus/lessons/round-16.md`): changed 20/20 config cases, 12/12 namespace,
38/38 selftest. Outside admission is pending, and residual contractions
versus the pre-harm census are listed there; read `error` and
`status-unverifiable` rows as "not measured", never as clean.

## Receipt taxonomy — every removal needs exactly one

The machine form of this table is `tools/souji-verify.sh` (installed
behavior wins over this prose; r6 reconciliation). Verdicts also include
`SAFE(metadata-prune)` for dead worktree registrations and fail-closed
refusals (`pushed-unverifiable`, `symlink-present`, `secrets-refusal`).

| Receipt | Qualifies when (as the tool checks it, r6) |
|---|---|
| `pushed` | the path exists now; its introducing commit (`git log --diff-filter=A --format=%H -1 -- <path>`) is an ancestor of the resolved default ref (`refs/remotes/origin/HEAD`, else the single `refs/remotes/origin/*` ref — existing refs only, NEVER `git fetch`, NEVER a local ref such as `refs/heads/master`); AND no unpushed commit touches the path (`git log --branches --not --remotes --oneline -- <path>` empty — bare `--not --remotes` alone returns nothing on git 2.55). Any failure → `pushed-unverifiable` / `unpushed-commits-touching`. |
| `moved-to-obsidian` | a ledger row whose canonical ABSOLUTE source path matches AND both sha256 pairs verify (vault side read-only). Symlinks in a digest scope → `symlink-present`. No row → no qualification. |
| `stale` | scratch type as the tool classifies: `.scratch/`, `*.out`, `*.log`, `launch-<id>.json`, `*-draft.*` (NOT `*.tmp`, not `out/`) AND zero live references (sweep excludes `.git`, `souji-shokunin/census/**`, `souji-shokunin/tests/**`, quarantine) AND mtime older than `--stale-days` (default 1). |

No receipt → no removal. Two receipts → the tool reports the first that
verifies (pushed before obsidian).

## Decision tables

### Classify an artifact

| Observation | Verdict |
|---|---|
| Owning repo has unpushed commits touching the artifact's path, or a dirty worktree over it | `NOT-SAFE` — live work; record and skip |
| Artifact's last commit is an ancestor of `origin/<default>` | `SAFE(pushed)` — removable after quarantine |
| Ledger row matches path + hash | `SAFE(moved-to-obsidian)` — source copy removable |
| Scratch type + zero live references + older than lane's last admitted round | `SAFE(stale)` — removable |
| Another artifact is offered as a duplicate (`cmp` byte-equality candidate or a same-content pair) | `NOT-SAFE` — no `duplicate` receipt class exists (taxonomy change, operator decision); before any verdict compare identity: `stat -c '%d:%i'` (or statx `stx_ino`/`stx_nlink`) reports one inode for two names — one file under two names, not two copies — and `cmp` exit 2 is trouble, never "different" |
| Anything else, any doubt, any credential-shaped content | `NOT-SAFE` — stay silent in the dry run |

### Removal flow (default dry run)

1. Dry-run census: classify every candidate, print the table, change nothing.
2. Operator approves the removal list.
3. Move into `<repo>/.ufo-quarantine/<utc-date>/...`: plain repo → `git mv` (or plain `mv` for untracked); colocated repo (`<repo>/.jj` present) → plain `mv` only (jj owns the index; staging is not a durable signal). Then commit BOTH paths (old `<rel>`, new `<qpath>`) by the Pre-quarantine commit route — quarantine is a normal commit in the owning repo.
4. Hold period (≥ one driver tick, 450s minimum; prefer 24h for anything not `pushed`).
5. Second check: re-run the receipt command; receipt must still hold.
6. Delete from quarantine. `pushed` artifacts need no hold beyond the second check.

### Never

- History rewrite (`reset --hard`, rebase, amend of published commits) — that
  stays with the operator (kura is unminted).
- Credentials, tokens, `op://` refs, `.env` content — kagi's province; souji
  cites paths and modes only.
- Operator config (`~/.config/**`), the driver (`scripts/`), `.ufo/state/`,
  `.ufo/watchdog.log`.
- Bare directory reads of the lane, fleet or census root when a protected
  artifact subtree must stay unopened: the reader can implicitly expand
  nested child names/metadata. Read named authority/code paths directly;
  do not disguise that expansion as a metadata-only exception (QUALITY Q45).
- A lane repo with dirty or unpushed work — quarantine-only, and even then
  the receipt must not depend on the dirty state.

## Error patterns (false-SAFE signatures)

- **Unpushed-lane trap**: `git worktree list` says `prunable`, but
  `git log --branches --not --remotes --oneline` in the owning repo is
  non-empty → the worktree metadata is NOT safe to prune yet; classify the
  *commits* first. Live instance: kotodama-shokunin 2026-10-18 (round-17..22
  unpushed, dirty tree, 553M `.scratch/`).
- **Superseded-snapshot drift**: a config copy claimed "byte-identical" that
  `cmp` shows differing from the live file — it is a stale *snapshot*, not a
  duplicate; classify as `stale` only after diff shows it holds no unique
  edits. Live instance: `shokunin.conf.full-roster-20261015` vs live
  `shokunin.conf` (3859 vs 4092 B, 2026-10-18).
- **Checkpoint-blob bloat**: fleet-root commits like `b2f2efa` that land
  launch JSON / PNG checkpoint files at the fleet root — classify per file;
  if pushed, they qualify for `pushed` receipts individually.
- **Worktree-with-unique-commits**: `git worktree list` + `git log <wt-sha> --oneline | head` —
  a prunable worktree whose tip has commits not on any branch is NOT-SAFE.
- **Git deletes without a receipt** (git ≥2.54, r12): a plain `git commit`
  spawns `git maintenance run --auto`, whose default geometric strategy runs
  `worktree prune --expire 3.months.ago` — an unlocked registration whose
  directory is gone and whose `worktrees/<id>/index` is older than 3 months
  vanishes, orphaning a detached HEAD's commits until `gc.pruneExpire`.
  Gate `tests/fixtures/r12-maintenance-guard.sh`; facts in
  `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`.
- **Unbounded staging or digest** (r13, round-12 M43/M44): a stalled move
  or a FIFO digest can outlive the round. Reject special files and special
  descendants, bound move/digest operations, and preserve quarantine residue
  after any timeout; never proceed to deletion. Recheck:
  `bash tests/fixtures/r13-quarantine-bounds.sh`.
- **Phantom fixture / wrong-byte verdict** (r13, round-12 K5 and r11 relay):
  a prose path is not evidence and a digest of a candidate is not the installed
  digest. Gate declared fragments with `python3 tools/souji-cert-evidence.py`;
  negative controls and frozen input pins are in its `--selftest` and
  `tests/fixtures/r13-cert-frozen/`. This is not a replacement safety suite.
- **jj: `refs/jj/keep/*` is not a durable receipt root** (r17, colocation): jj writes a keep ref for every commit it creates, visible or hidden, so an all-refs root set counts unbookmarked work as durable and an absent-worktree head held only by keep refs can wrongly earn `SAFE(metadata-prune)`. Receipt roots are every ref EXCEPT `refs/jj/*` (`for-each-ref --exclude='refs/jj/'` — `refs/stash`, `refs/original` and friends stay roots): the live `s18_evaluate_worktree_one` root query in `tools/souji-verify.sh`, `tools/souji-vault-verify.sh` and `tools/souji-quarantine.sh`.
- **jj: unbookmarked / keep-only content is invisible to branch queries**: a jj commit detaches HEAD and moves no branch, so `--branches --not --remotes` returns empty for work that exists. A keep-only commit touching the target refuses a `pushed` receipt only when the blob it introduces there is novel — absent from every pushed blob at the path (`jj_keep_novel`, `jj_keep_novel` in the three receipt tools; gated on a `refs/jj/keep/` probe, so plain repositories run nothing new). Deletions and identical-content rebase/metaedit predecessors do not refuse. Prose queries without the novelty check stay blind — prefer the tool's verdict.
- **jj: a keep ref is removed by jj's ref-set rewrite, and a packed one skips the age gate** (r30, F1; headline corrected in round 30 wave 2 — the first wording claimed the operation log owns the lifetime, refuted by step 4 of the record — and the lever corrected in round 31 from the routed closure defect: packedness, not the threshold, is what the record discriminates): `git gc --prune=now` leaves a `refs/jj/keep/*` ref naming an abandoned commit in place, while `jj util gc --expire=now` removes that ref, and `jj op abandon ..@-` before a second `jj util gc` takes six keep refs to two (`keep_refs` 6 to 2 at step 5, none of them naming the abandoned commit). The ref's storage form decides whether the age gate can save it: a ref packed by `git gc` or `git pack-refs --all` has no loose file whose mtime the gate reads, so a default-threshold `jj util gc` deleted it (8 to 6) while the loose control kept it — the `--expire=now` threshold is sourced (S220, S054), not measured. The default threshold is two weeks ("By default, only obsolete objects and operations older than 2 weeks are pruned." — `jj util gc --help`, jj 0.45.1) and `--expire` accepts only the string `now`, so an unrun `util gc` keeps a keep-only head alive and a kept ref is not evidence the content is reachable from a durable root. The commit object stayed present at every step of the record, so a dropped keep ref is not a deleted object; what holds or drops that object is `corpus/knowledge/jj-dropped-keep-object-lifetime.md`. Facts, source rows and limits: `corpus/knowledge/jj-keep-ref-expiry.md`; recheck `bash tests/fixtures/r30-jj-keep-expiry.sh`.
- **jj: an object outlives its keep ref, so presence is not a receipt** (r31, F1): once the `refs/jj/keep/*` ref naming an abandoned commit is gone, its object can still be held, and each arm of the recorded fixture isolates one holder — a keep ref naming a descendant (object present until those refs are deleted and git pruned), a live descendant commit whose refs the keep set is rebuilt from (S054), and a reflog entry naming the commit (S222, S063), which is the only holder left after the keep refs are dropped by hand and which releases the object only when the entries are expired before the prune. Expiring every reflog entry naming the commit removes no object while a keep ref still reaches it, and a fourth holder is sourced rather than measured: the object's own modification time inside the two-week `gc.pruneExpire` window (S063). So `git cat-file -e <id>` succeeding proves that no deletion completed, and nothing about whether one was attempted or authorised; the receipt-grade observation is the other direction — the id absent after a `git gc` whose prune date is at or after the object's mtime, with the reflog entries naming it expired (or their windows asserted), and that `git gc` must be one the lane ran or whose argv it recorded. Facts, source rows and limits: `corpus/knowledge/jj-dropped-keep-object-lifetime.md`; recheck `bash tests/fixtures/r31-jj-object-clock.sh`. (Superseded for that fourth holder by the r32 bullet below: the object's own mtime is now measured, `corpus/knowledge/jj-abandoned-object-mtime-clock.md`.)
- **jj: nested `.git` → phantom deletions**: a directory containing a `.git` (even an empty stub) is a nested repository to jj; its files read as `D` and a directory pathspec commits those deletions. Use file-exact pathspecs; never commit a directory that contains a nested `.git` (the helper refuses a committed deletion of a file still on disk). The r16 stub `tests/vault/vadv54-run/p/p6repo/.git` is quarantined at `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`; the rule holds for any nested `.git`.
- **jj: detached HEAD is not a citable pin**: under colocation `git rev-parse @{u}` fails and `git branch --show-current` prints nothing. Read branch tips as `git rev-parse refs/heads/<b>` and remotes as `refs/remotes/origin/<b>`; never cite `HEAD` or `@{u}` as the measured commit.
- **A type guard is not a bound: post-guard FIFO swap** (r18, S064/S062): git opens `$GIT_DIR/info/attributes` with a plain blocking `open(2)` and checks the type only afterwards, and a work-tree `.gitignore`/`.gitattributes` FIFO needs no race at all — a census that stat-checks then reads blocks forever, losing every row. Bound every per-repository step (list-phase guards included) in its own process group (`--repo-timeout`, default 600 s); a timed-out repository is an `error` row, "not measured". Recheck: `python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh`.
- **A fixture timeout that kills only its child leaves git blocked forever** (r18, S067): `subprocess.run(timeout=)` kills the direct child; the census and its git grandchild stay blocked on a FIFO whose directory the fixture then deletes — 58 such orphans were on this host at round 18 start (`census/round-18/leaked-procs-before-1631.txt`). Run every census in its own session and on timeout SIGKILL every pid whose `/proc/<pid>/stat` field 6 equals the leader (S068), since the r18 census forks per-repository process groups that escape `killpg(leader)`. List residue with `bash tools/souji-proc-census.sh`; killing a listed process is the operator's call (QUALITY Q32).

- **A first-physical-line quote hides a wrapped cut** (r19, Q36): a lesson
  entry that quotes only the first physical line of a wrapped STATUS
  paragraph looks carried to a line matcher, and a correct quote whose own
  bullet wraps looks uncarried. Match the paragraph (continuations joined)
  and require the ellipsis exactly at a source line end; mid-line ellipses
  are not cut points. Recheck:
  `python3 tests/fixtures/r19-carry-wrap.py --tool tools/souji-landing-gate.py`.
- **A `HEAD`-stamped record binds nothing** (r19, Q37): under jj colocation
  HEAD is normally detached, can sit on a keep-only commit, and can predate
  uncommitted working-copy bytes. Resolve the current 40-hex commit, require
  reachability from `refs/heads|refs/tags|refs/remotes` (never `refs/jj`), and
  for working-tree runners require `git diff --quiet <rev> -- <measured
  paths>`; otherwise exit 2 and write no record. Recheck:
  `python3 tools/souji-rev-pin.py --selftest`.
- **Process residue is a nomination, not a receipt** (r19, Q32–Q33): the
  census lists own-uid deleted cwd links and vanished scratch argv/fd paths;
  it never signals, never reads `environ`, redacts secret-shaped argv, and
  compares inodes when a literal live name ends in ` (deleted)`. The docs
  state the suffix only for `exe` (S076); the cwd/fd rule is fixture-carried.
  Knowledge: `corpus/knowledge/process-residue-observations.md`.
- **jj: an unreferenced object dies by its own mtime, so presence is not a receipt** (r32, F1):
  after the `refs/jj/keep/*` refs naming an abandoned commit and the reflog entries naming it are
  gone, and with no recent object reaching it and no `gc.recentObjectsHook` in play, the object's own
  modification time is what decides its fate under `git gc` — a recent object is kept inside the
  `gc.pruneExpire` window and an old one is dropped, the clock is carried per
  object where a cruft pack holds it (its `.mtimes` file, sourced in the entry's Gate),
  `gc.pruneExpire=never` keeps the old object, and
  `gc.cruftPacks=false` leaves the recent object loose instead of in a cruft pack. The five arms
  and their measured lines are in `corpus/knowledge/jj-abandoned-object-mtime-clock.md`:
  `RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes`,
  `RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no`,
  `RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no`,
  `RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes`,
  `RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no`;
  record `census/round-32/records/jj-mtime-clock-run.txt`, fixture
  `tests/fixtures/r32-jj-mtime-clock.sh`. A `git cat-file -e` that succeeds therefore says only
  that no prune reaching the object has completed — never that a deletion was proved absent.
- **A trailing slash in `TMPDIR` makes a string comparison miss a kernel-canonical path** (r33, C2; S224, S225, S226): repeated slashes collapse to one in pathname resolution (S224), but a shell `case` pattern and a ledger row comparison are byte comparisons, and `readlink -- /proc/<pid>/fd/1` also prints the file under the kernel's single separators (S225). With `TMPDIR=/s/` the census pattern `"${TMPDIR:-/tmp}"/souji-census-now.*/*` is `/s//souji-census-now.*/*` and never matches, and `mktemp -d "${TMPDIR}/…"` hands back a `//`-spelled scratch path whose ledger rows stop matching the canonical spelling: with `TMPDIR` ending in `/` `bash tools/souji-census.sh --selftest` prints `selftest: 69 checks, 10 failed` and `bash tools/souji-verify.sh --selftest` prints `selftest: 49 checks, 2 failed` (the two `FAIL R9 … ledger revocation was reached` checks), each `0 failed` under the same `TMPDIR` written without the trailing slash. The failing-check count moves with the run — 10 in `feasibility.txt:168`, 12 in `controls.txt`, 13 in a wave-1 re-run (seat SwarmScribe47) at the same base bytes — so quote the exit code and the `failed` verdict, never the count, as the stable observation. Canonicalise the caller's `TMPDIR` once at entry — strip trailing slashes, keep `/` — never widen a skip or normalise only one side of one comparison. Recheck: `python3 -B census/round-33/c2-counter.py --root . --rev <full40> --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch <dir> --only O4,O5`.
- **A green-looking restatement is not evidence when its frozen binding points elsewhere** (r34, C1): `census/round-34/c1-items.tsv` has off-by-one `where` cells for 21/22 SKILL registry items, and the counter's `argv-correction` cause check reads that wrong line. A foreign neighbour commit can therefore be accepted while the actual row writer is rejected. Separately, `ANYLINE:`/`COUNT:` predicates are matched against whitespace-collapsed lines, so a frozen tab-delimited expression can be unreachable. Do not alter the frozen list after data; report the target miss and reproduced cause-binding attack. Evidence: `census/round-34/records/controls.txt`, captured W1 attack reports in `census/round-34/waves/`.
- **A line-start-only comment opener is an over-acceptance, not a simplification** (r56/r57, Q114/Q115): a `<!--` that
  does not start the line still opens an inline HTML comment in CommonMark §6.6 and hides every line through the first
  `-->`, including a later one; an NBSP before the opener is a character, not indentation. The r56 v5 narrowing repaired
  the F29 over-hide and created the opposite harm: B4 (NBSP opener) and C4 (closed multi-line inline comment) hid real
  filings while v5 counted them filed. Pin both directions in the same frozen set — a visible prose-token control and a
  closed-inline control — and verify the visibility judgement with an independent renderer, not with the counter itself.
  Recheck: `python3 -B census/round-57/c1-counter.py --selftest --work DIR` (B4/C4 exit 1, F29/C6 exit 0).

The repository-content bound is not a kernel/filesystem sandbox: initial
root/compare resolution and enumeration remain outside it; stopped or
unreapable groups and a descendant that changes session/group have the
limits stated in QUALITY Q34. The timer must still enforce its bound after
parent death, even when it cannot write its state marker. An observed proc
row never grants signal authority over an inherited process (Q33).

## Checklists

Pre-removal (all must answer yes):
- [ ] Receipt class named and its command re-run at decision time
- [ ] Owning repo has no unpushed commits touching the artifact (`git log --not --remotes --oneline -- <path>` empty)
- [ ] Owning repo worktree is clean over the artifact (`git status --porcelain -- <path>` empty)
- [ ] Entry is in a dry-run table the operator has seen, unless receipt is `pushed` and quarantine hold elapsed
- [ ] Nothing references the artifact (`rg -l` across owning repo, 0 hits)

Pre-quarantine commit:
- [ ] Quarantine path is inside the owning repo (`.ufo-quarantine/<date>/`)
- [ ] Commit message names the receipt class and the evidence pointer
- [ ] Commit identity follows the route: souji lane helper and plain repo → `souji-shokunin <souji@shokunin.local>`; owning lane's helper → `--as <owner-id>` stamps `<owner>-shokunin <owner>@shokunin.local` (the helper refuses any other id except `protocol`)
- [ ] Right repo: `git -C <repo> rev-parse --show-toplevel` prints the owning repo (never trust `cd`)
- [ ] Commit route is chosen by repo kind — first `git -C <repo> rev-parse --git-dir` must succeed (a nested empty `.git` directory is not a repo; for a linked worktree resolve the main repo with `--git-common-dir`); never `git add -A` / `.`:
  - [ ] souji lane itself: helper only — `"$SHOKUNIN_ROOT/scripts/hyaku/jj-lane.sh" commit <lane> --as souji -m "<receipt class + evidence pointer>" -- <paths>`; the helper demands its own init (`snapshot.auto-track="none()"`, present in this lane since the hyaku jj migration), refuses any `--as` but the lane id or `protocol`, and ends in a push.
  - [ ] repo souji cleans with `<repo>/.jj` present: the OWNING lane's helper naming BOTH paths — `"$SHOKUNIN_ROOT/scripts/hyaku/jj-lane.sh" commit <repo> --as <owner-id> -m "<receipt class + evidence pointer>" -- <rel> <qpath>`; a one-sided request commits only that half and is NOT refused, so post-check both: `git -C <repo> cat-file -e <landed>:<rel>` fails and `git -C <repo> cat-file -e <landed>:<qpath>` succeeds; cite only the helper's `landed <hash>` line (it prints after ls-remote — the commit also pushes). Never `jj-lane.sh init` a repo souji merely cleans; a refusal (uninitialized, foreign `--as`, path guard, phantom deletion) is a stop, never a git fallback, never a raw `git commit` under colocation.
  - [ ] plain repo (no `.jj`): `git -C <repo> add -- <rel> <qpath>` then `git -C <repo> -c maintenance.auto=false commit -- <rel> <qpath>` — both paths in both commands; a destination-only commit splits the move.
- [ ] Pinned registrations stay pinned: `git -C <repo> worktree list --porcelain | awk '/^locked/{n++} END{print n+0}'` equals the pin count; pin new ones with `git -C <repo> worktree lock --reason "<why>" <worktree-path>`

## Gate registry

Gate map: 0 clean · 1 failed · 2 could-not-evaluate. Other codes are
explicit below. The four legacy receipt/action tools are **probes**, not
Gate-standard certifications: their live verdicts are data, expected baselines
are not pinned, and code 1 also carries setup failures. Embedded selftests
alone do not repair those interface debts. Always use `TMPDIR=/var/tmp`
for the legacy selftests; their historical fallback is not Q4-conformant.
`evidence` rows are measurement producers, not gates: 0 means the record was written and is internally valid, 1 is unused by code (a red arm is data, not a runner failure), 2 means could-not-evaluate; a row whose self-test cannot fail is a `probe` or an `evidence` row, never a `gate`.

| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r43-c1-counter | gate | `python3 -B census/round-43/c1-counter.py --root LANE --rev FULL40 --scratch DIR` | 0 exact frozen Target; 1 unmet; 2 could-not-evaluate | `python3 -B tests/fixtures/r43-correction-prose.py --lane-root LANE --rev43 FULL40 --work DIR` (external discrimination fixture, not a counter self-invocation; conformance debt disclosed) | `census/round-43/c1-required.tsv`, `census/round-43/preregistration.txt` | read-only git blobs; caller scratch | souji |
| r43-c2-counter | gate | `python3 -B census/round-43/c2-counter.py --root LANE --rev FULL40 --scratch DIR` | 0 exact frozen Target; 1 unmet; 2 could-not-evaluate; current target honestly red due to hidden-audit oracle conflict | built-in always-clean/findings/memorizer controls; no self-invocation mode (conformance debt) | `census/round-43/c2-cases.tsv`, `census/round-43/c2-hidden-audit.py`, `census/round-43/preregistration.txt` | isolated git fixtures and shared clone in caller scratch | souji |
| r43-c3-counter | gate | `python3 -B census/round-43/c3-counter.py --root LANE --rev FULL40 --scratch DIR` | 0 exact frozen Target; 1 unmet; 2 could-not-evaluate; no fixture installed this round because prior symlink behavior conflicts with new target | embedded stderr-discrimination pair and sniffing control; no self-invocation mode (conformance debt) | `census/round-43/c3-survivors.tsv`, `census/round-43/preregistration.txt` | read-only lane blobs; isolated caller scratch | souji |
| souji-verify | probe | `bash tools/souji-verify.sh <path>...` | 0 clean, SAFE/NOT-SAFE data; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest` | none; no pinned complete id set | read-only targets; isolated selftest under TMPDIR | souji |
| souji-vault-verify | probe | `bash tools/souji-vault-verify.sh --fallback <path>...` | 0 clean, VERIFIED/NOT-VERIFIED data; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest` | none; no pinned complete id set | read-only source/vault; isolated selftest under TMPDIR | souji |
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv] [--repo-timeout N]` | 0 census emitted, including degraded `error`/`status-unverifiable`/`not-a-repo` placeholders, never clean measurements; dirty uses explicit `--untracked-files=normal`; hardlinked/non-regular info/attributes degrades one repo (D2). After enumeration, preflight content guards and `census_one` run separately in their worker groups under the timeout (integer 1..86400, default 600, last option wins; invalid → 2). Timeout emits `error` plus `repo-timeout`; unreaped group emits `repo-timeout-unreaped`; other repos continue. Root/compare resolution and discovery are not filesystem sandboxes; descendants escaping their group are not contained. 3 differential drift; 1 selftest/setup failure; 2 usage/malformed baseline/detected protected metadata refusal. Early closed stdout may return SIGPIPE 141. | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (69/0 at 4800fd7) | `census/round-18/c1-matrix-4800fd7.json`; historical r17 `census/round-17/c1-matrix-4f48343.json`; final batch `census/round-18/final-verification-4800fd7.json` | read-only targets; temporary capture/selftest under /var/tmp; signals only its spawned workers/timer, including parent-interruption cleanup | souji |
| souji-quarantine | probe | `bash tools/souji-quarantine.sh --dry-run <repo> <target>...` | 0 clean target outcome; 3 failed/refused/aborted; 4 could-not-evaluate live guard; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest` | no complete safety-suite baseline; receipts advisory, certification OFF | dry-run read-only; explicitly authorized action moves targets within owning repo; selftest under TMPDIR | souji |
| r12-maintenance-guard | gate | `bash tests/fixtures/r12-maintenance-guard.sh` | 0 clean; 1 failed; 2 could-not-evaluate | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | expected counts and SELFTEST_EXPECTED_IDS in fixture; `tests/results/r12-maintenance-guard.txt` | isolated `/var/tmp/souji-r12-maintenance.*` | souji |
| souji-cert-evidence | gate | `python3 tools/souji-cert-evidence.py --root PATH --manifest PATH` or `--frozen DIR` | 0 clean declared consistency; 1 failed honest fragment; 2 could-not-evaluate malformed/inconsistent/tampered input | `python3 tools/souji-cert-evidence.py --selftest`; `python3 tests/fixtures/r13-cert-evidence.py` | embedded expected exit/finding ids; `tests/fixtures/r13-cert-frozen/expected.json` pins every input | inputs read-only; selftests isolated `/var/tmp`; never executes recorded commands | souji |
| souji-repo-structure | probe | `bash tools/souji-repo-structure.sh --repo PATH` | 0 clean metadata emitted; 2 could-not-evaluate usage/repo/promisor; 3 could-not-evaluate unsupported Git; 4 could-not-evaluate config/stderr/command/output | corresponding gate below | no live-data expected baseline | repository reads; capture-only `/var/tmp` directory removed on exit | souji |
| r13-repo-structure | gate | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | 0 clean; 1 failed; 2 could-not-evaluate | same `--selftest --probe` command | fixture SELFTEST_EXPECTED_IDS and case expectations; recorded run `census/round-13/verification.json` | isolated `/var/tmp/souji-r13-repo-structure.*` | souji |
| r13-quarantine-bounds | gate | `bash tests/fixtures/r13-quarantine-bounds.sh [--tool PATH]` | 0 clean; 1 failed case or id set; 2 could-not-evaluate usage/environment | same command, isolated positive/negative controls; baseline red arm uses `--tool` | fixture EXPECTED_IDS and per-case exit/finding/retention assertions; `census/round-13/verification.json` | isolated `/var/tmp/r13-qbounds.*` only | souji |
| souji-evidence-cache | gate | `python3 tools/souji-evidence-cache.py --root DIR --record PATH [--require REL...]` or `--frozen DIR` | 0 clean/reusable declared dependencies; 1 failed/stale/missing dependency or matched false; 2 could-not-evaluate malformed/legacy/protected/tampered input | `python3 tools/souji-evidence-cache.py --selftest`; external fixture below | literal embedded expected ids; `tests/fixtures/r14-cache-frozen/expected.json` input pins | inputs read-only; isolated selftest `/var/tmp`; never executes a recorded command | souji |
| r14-evidence-cache | gate | `python3 tests/fixtures/r14-evidence-cache.py [--tool PATH]` | 0 clean; 1 failed assertion; 2 could-not-evaluate missing prerequisite | same default self-invocation fixture; isolated positive/negative CLI calls | literal expected exits/finding ids in fixture; `tests/fixtures/r14-cache-frozen/expected.json` | isolated `/var/tmp/souji-r14-cache-fixture.*`; reads selected gate and committed snapshot | souji |
| r14-census-boundary | gate | `python3 tests/fixtures/r14-census-boundary.py --tool PATH` | 0 clean; 1 failed case/id-set; 2 could-not-evaluate missing prerequisite/trace/usage | same default self-invocation fixture, synthetic HOME with spy and strace access checks; `--tool` selects paired baseline | fixture EXPECTED_IDS and literal expected exits/finding/access assertions | isolated `/var/tmp/r14-census-boundary.*`; never a real credential-store probe | souji |
| r15-census-config | gate | `python3 tests/fixtures/r15-census-config.py --tool PATH` | 0 clean; 1 failed case/id-set; 2 could-not-evaluate prerequisite/trace/usage | same full default invocation over isolated synthetic HOME; selected tool supplies pre-harm, harmed or changed arm; first executed and revised r16 (degrade/benign/safety classes, mixed fleets, positive controls) | fixture literal EXPECTED_IDS, HARM_CASES, CASE_CLASSES and per-case exits/rows; `census/round-16/c1-matrix-final.json` | isolated `/var/tmp`; no real store or live fleet probe | souji |
| r17-census-hygiene | gate | `python3 tests/fixtures/r17-census-hygiene.py --census PATH` (`--tool` accepted as an alias) | 0 clean; 1 failed case or id-set, or a census run exceeding the per-case timeout (rc 124 is FAIL, never SKIP); 2 could-not-evaluate missing prerequisite/usage | same default self-invocation over an isolated synthetic HOME and private tempdir; `--case`/`--list` are debugging only, never admission; `--json` emits per-case records | fixture literal `EXPECTED_IDS` compared as an exact ordered tuple with per-case class (`repair`/`preserve`/`refuse`) and expected exit/row; `census/round-17/c1-matrix.json` (L1) | isolated private tempdir under `/var/tmp`; never a real fleet root or credential store | souji |
| r17-census-matrix | evidence | `python3 census/round-17/run-matrix.py --changed <rev or WORKTREE> --output <new.json>` | 0 record written and every suite valid (fixture exit agrees with its SUMMARY; all fixtures clean, or dirty fixtures recorded via `--allow-dirty-fixtures`); 1 unused by code — the runner returns only 0 or 2, an unhandled crash is an unstructured nonzero, never a fixture verdict; 2 could-not-evaluate invalid suite/unknown revision/missing fixture/dirty fixtures without the flag/refused `--output` overwrite/usage | `python3 -m py_compile census/round-17/run-matrix.py`; the runner's selector table supplies each suite's flag (`--census` for r17-hygiene, `--tool` for r15/r14); no in-file behavioral selftest — the record is only as strong as the fixtures it runs | `census/round-17/c1-matrix.json` (L1) read with the r17-census-hygiene, r15-census-config and r14-census-boundary rows | per-fixture isolated `/var/tmp`; writes only `--output` (refuses overwrite) | souji |
| r17-jj-receipts | gate | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir DIR` | 0 clean with every case counted (a case the selected tools cannot express prints `SKIP`; SKIP is never PASS; jj absent → the optional real-jj J9 arm SKIPs); 1 failed case/id-set; 2 could-not-evaluate missing git, missing `--tool-dir`, usage | same default invocation with `--tool-dir tools`; the paired red arm over `5fa6017`-extracted tools must fail J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree; `--baseline-dir` absent → J6 SKIP | fixture CASE/SUMMARY literals; C3 root rule: receipt roots are every ref except `refs/jj/*` (`for-each-ref --exclude='refs/jj/'`), and a keep-only commit refuses only a novel blob at the target (`jj_keep_novel` in the three receipt tools) | isolated `mktemp -d` under `/var/tmp` (sandbox repos removed); never a real fleet repo; `jj` runs only inside the sandbox | souji |
| souji-preservation-evidence | gate | `python3 tools/souji-preservation-evidence.py --root DIR --record FILE` or `--frozen DIR` | 0 clean declared consistency; 1 failed honest evidence; 2 could-not-evaluate malformed/tampered/unavailable input | `python3 tools/souji-preservation-evidence.py --selftest` (47/47 at r16; 24/47 as landed r15); external fixture below | checker literal r16 case universe and baseline digests; `tests/fixtures/r15-preservation-frozen/expected.json` pins every snapshot input; record regenerated from real runs by `regenerate.py --rev <rev>` | records read-only; self-invocations isolated `/var/tmp`; never runs recorded commands | souji |
| r15-preservation-evidence | gate | `python3 tests/fixtures/r15-preservation-evidence.py` | 0 clean; 1 failed expected exit/finding; 2 could-not-evaluate missing prerequisite | same default self-invocation fixture (8/8 at r16) | fixture literal positive/negative expectations and `tests/fixtures/r15-preservation-frozen/` | isolated `/var/tmp`; inputs read-only | souji |
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--base REV] [--fleet-root FLEET] [--json OUT]` | 0 no findings; 1 findings (parse, missing registry target, frozen pins/measured commit, uncarried STATUS); at round ≥18 also LG-DANGLING-PTR and LG-DANGLING-PTR-EXEMPT-STALE, including .ufo/quarantine citations. Exact synthetic placeholder exemption only; all same-round LOG sections scanned; lane-local pointers cannot be cleared by a fleet collision. 2 could-not-evaluate/usage/bad revision/malformed exemptions/unreadable git input; pointer findings retained when the carry check cannot evaluate. This is scoped consistency, not complete prose understanding. | `python3 tools/souji-landing-gate.py --selftest` (65/0 at r19: 61 + four wrap cases); `python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` (11/0) | `census/round-18/final-verification-4800fd7.json`; historical old-grammar before/after `census/round-18/gate-pointers-before-b576341.json`, `census/round-18/gate-pointers-after-5efb519.json`; exemptions `corpus/pointer-exemptions.tsv` | committed blobs at REV; explicit fleet citations checked against selected fleet working tree; private /var/tmp removed; only bash -n and Python compile executed on inspected code | souji |
| r16-landing-gate | gate | `python3 tests/fixtures/r16-landing-gate.py [--tool PATH]` | 0 clean; 1 failed case; 2 could-not-evaluate prerequisite | same; includes a vacuity stub that must fail | historical r15 replay pins and synthetic same-round cases in the fixture | isolated `/var/tmp` git repos removed afterwards | souji |
| r17-gate-replays | gate | `python3 census/round-17/gate-replays.py [--gate-rev REV] --output <new.json>` | 0 all five pinned replay exits and exact (id,path) multisets match expected (b410186 1/5, a31642d 0/0, cc21683 0/0, 6ff91f5 0/0, 79bbe7a 1/29); 1 divergence; 2 bad revision/input/existing output/usage. Semantic equality, not JSON byte identity; selftest is a separate check, not recorded in the old null selftest field. | identity run --gate-rev 5fa6017; installed gate selftest separately | `census/round-17/gate-replays-expected.json`; original record `census/round-17/gate-replays-4f48343.json`; final replay `census/round-18/gate-replays-final-4800fd7.json`; final selftest `census/round-18/final-verification-4800fd7.json` | private /var/tmp extraction; writes only named exclusive output | souji |
| souji-seat-audit | gate | `python3 tools/souji-seat-audit.py --spec W.json --transcripts DIR --lane LANE [--json OUT]` | 0 no recorded major, possibly partial coverage (inspect missing_transcripts); 1 recorded major; 2 unreadable/nonregular/changed input, usage or refused output. Parsed write/edit/ast_edit targets use exact explicit grants, not all suffixes; truncated successful targets cannot be cleared by a scratch prefix. V-SIGNAL is a visible signal-shaped class, including kill -0, not proof of signal delivery. | `python3 tools/souji-seat-audit.py --selftest` (literal severity-exact cases; r19 historical 73/0); external r20 oracle below | embedded expected classes; `tests/fixtures/r20-audit-contract.py` REQUIRED_CASE_IDS and BASE_BROAD_CASE_IDS; historical transcript replay `census/round-17/seat-audit-r16-replay-4f48343.json` | reads selected exported inputs only, fingerprints consumed bytes, rejects detected repeat/read/import-source drift; JSON exclusive create; no shell-execution/authorship/atomic-snapshot certificate | souji |
| r17-transcript-manifest | gate | `python3 census/round-17/transcript-manifest.py --check DIR` | 0 every listed digest matches, no listed file missing, no unlisted file present; 1 mismatch/missing/extra; 2 usage/unreadable directory | `--write` then `--check` on a private `/var/tmp` copy exits 0; a one-byte mutation of one file makes `--check` exit 1 (negative control) | `census/round-16/transcripts/MANIFEST.sha256` (sorted `sha256  relpath`, `LC_ALL=C`) over the byte-exact r16 w1/w2 transcripts | `--write` creates `MANIFEST.sha256` inside the named directory only; `--check` read-only; never alters transcript bytes | souji |
| r18-census-bounded | gate | `python3 tests/fixtures/r18-census-bounded.py --census PATH` | 0 clean; 1 failed case (outer timeout is FAIL, never SKIP); 2 usage/prerequisite | full invocation B1–B12; case selection is debugging, not admission | `census/round-18/c1-matrix-4800fd7.json`: b576341 12/9 failed → changed 12/0. B1–B4/B8 FIFO reads, B5 slow finite control, B6 residue, B7 protected refusal, B9 TERM-ignoring target, B10 parent TERM/KILL, B11 raw-newline inputs, B12 gitfile-preflight timeout row | private /var/tmp scratch, synthetic HOME and PATH shims; session cleanup, no unrelated signals | souji |
| r18-census-matrix | evidence | `python3 census/round-18/run-matrix.py --changed <rev or WORKTREE> --output <new.json>` | 0 valid record; 2 invalid/unrunnable suite, bad inputs, missing/dirty fixtures without permission, or refused overwrite; a valid failing suite is data, not a runner crash | py_compile plus recorded fixture runs | `census/round-18/c1-matrix-4800fd7.json`; exact resolved changed revision pinned once; complete CASE details retained | private suite sessions; only owned session killed; preexisting argv-prefix matches recorded separately, new (pid,starttime) observations counted without prefix-based signalling | souji |
| souji-proc-census | probe | `bash tools/souji-proc-census.sh [--prefix DIR]... [--min-age S]` | 0 observation table, never reap permission; 2 usage; 1 selftest failure | `bash tools/souji-proc-census.sh --selftest` | header boot_id; columns pid, ppid, pgid, sid, age_s, starttime, state, wchan, reason, cmd; cwd > argv > fd precedence; `census/round-18/proc-agreement-counterfix.json` | own uid; cwd-deleted any location, --prefix limits argv/fd only; literal live suffix confirmed by inode, identity rechecked; never environ; argv redacted/truncated; signals only workers created by --selftest | souji |
| r18-proc-census | gate | `bash tests/fixtures/r18-proc-census.sh --tool PATH` | 0 clean; 1 failed; 2 usage/prerequisite | full P1–P19; header-only stub fails P1/P2 | `census/round-18/final-verification-4800fd7.json`: 19/0; literal cwd/fd names, header/AWS/Slack redaction, prefix sibling and reason precedence added; P7 traces signal syscalls instead of liveness alone | /var/tmp, fixture-owned workers only | souji |
| r18-leak-count | evidence | `python3 census/round-18/leak-count.py [--json OUT]` | 0 emitted; 1 selftest/IO error or refused overwrite; 2 usage | `python3 census/round-18/leak-count.py --selftest` | independent counter; `census/round-18/proc-agreement-counterfix.json` (two consecutive 66=66 pid-identical snapshots); older dated 65=65 in `census/round-18/leak-count-live-1721.json` | own uid /proc read-only; no signalling outside selftest; exclusive JSON create; scan does not exclude unrelated ancestors | souji |
| souji-rev-pin | gate | `python3 tools/souji-rev-pin.py --root DIR --rev REV --path PATH... [--no-tree-check]` | 0 full40 durable revision whose selected owned regular file/directory byte set matches committed raw blobs; 2 refused HEAD/branch/short/keep-only/missing/added/changed/nonregular/symlink/escaped/protected input; 1 selftest failure | `python3 tools/souji-rev-pin.py --selftest` (r19 historical 11/0); current caller fixture registered after integration | embedded refusal expectations; `census/round-19/c2-smoke.txt` historical only | bounded named repository inputs, safe Git selection environment, no operator-sweep ancestor enumeration; isolated selftests; no external-runtime/atomic-filesystem authority | souji |
| r19-rev-pin | gate | `python3 tests/fixtures/r19-rev-pin.py [--tool PATH]` | 0 clean; 1 failed case, wiring leftover, or base arm that accepts every refusal (vacuity); 2 prerequisite/usage | same default invocation; base stub must accept all six refusal cases | fixture literal expectations; `census/round-19/c2-smoke.txt` | /var/tmp git sandbox only | souji |
| r19-carry-wrap | gate | `python3 tests/fixtures/r19-carry-wrap.py [--tool PATH] [--base-rev REV]` | 0 four exact cases, both named baseline discriminators and branch counters match; 1 any mismatch or changed discriminator set; 2 prerequisite/usage | same default invocation in four isolated /var/tmp Git worlds | literal expected exit/finding IDs, required wrap-unmarked and wrap-bullet-wrapped base mismatches, exact report/marker/status/heading counters | /var/tmp only; no historical evidence overwrite | souji |
| probe-carry-invariants | probe | `python3 census/round-19/probe-carry-invariants.py` | 0 every seeded invariant held; 1 a violation; 2 prerequisite | deterministic seeded run itself (no separate selftest; a breaking rule change fails it) | `census/round-19/carry-invariants.txt` (400 paragraphs, 562 boundary cuts, 842 midline cuts, 0 violations) | none (in-memory; no repo writes) | souji |
| r19-seat-audit-shapes | gate | `python3 tests/fixtures/r19-seat-audit-shapes.py [--tool PATH]` | 0 all literal cases match and baseline differs on at least two; 1 failed case/vacuity; 2 prerequisite/usage | same default synthetic spec/transcript invocation; explicit DELIVER/SCRATCH controls, tools patch refusal, kill/killpg/sudo/loop/xargs/variable shapes and root=/prefix controls | expected case table in fixture; `census/round-19/c1-audit.txt` is historical, not the r20 run | /var/tmp only; recorded Bash/Python commands are inert transcript text | souji |
| verify-agreement-pin | gate | `python3 census/round-19/verify-agreement-pin.py --root <original-byte-tree> --check RECORD` (historical use; current replay stages it through r21-acceptance) | 0 pinned digests match; 1 mismatch/missing; 2 malformed/unreadable/refuse-overwrite | `python3 census/round-19/verify-agreement-pin.py --selftest` (5/0 historical) | r21 runner's agreement-pin-check stages original tool/counter revisions and verifies immutable digests; upgraded proc bytes are not r18 bytes | isolated historical inputs; no live census | souji |
| r20-audit-contract | gate | `python3 tests/fixtures/r20-audit-contract.py [--tool PATH] [--base-tool PATH]` | 0 exact primary inventory plus literal outputs/digests/drift refusals; with baseline all eleven named over-authorizations must reproduce; 1 any mismatch/missing case/baseline witness; 2 prerequisite/usage | same default invocation over fresh synthetic worlds; baseline mode required for claim's before/after | fixture REQUIRED_CASE_IDS and BASE_BROAD_CASE_IDS, independent preregistration `.ufo/waves/round-20/preregistration.txt` | isolated /var/tmp; imports selected auditor only, never executes transcript commands; temporary source variants only | souji |
| r20-input-binding | gate | `python3 tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812` | 0 exact caller/helper/historical-counter inventory plus all seven old-producer/current-refusal pairs; 1 any behavioral/inventory mismatch; 2 prerequisite/usage | same default invocation has 36 literal cases; named baseline adds seven actual entrypoint guard pairs, with suites stopped by a producer tripwire | fixture expected_case_ids and BASELINE_PAIR_CASE_IDS, frozen oracle `.ufo/waves/round-20/preregistration.txt` | bounded source copies and isolated /var/tmp Git repos only; actual changed CLI refusals, no live census or signal suites; paired main calls do not run measurement producers | souji |
| r21-acceptance (r22 result-contract repair) | evidence | `python3 census/round-21/run-acceptance.py --root <local-clone-or-bare-repo> --rev <full40> --output <new-absolute-json>` | 0 all18 frozen programs satisfy typed counter values, empty summary stderr, exact33 cache-check names/four ordered phase labels; 1 retained mismatch; 2 refused revision/input/output; source HEAD may differ or be unresolved | `bash census/round-21/replay-matrix.sh --runner census/round-21/run-acceptance.py --lane <source-repo> --rev <full40> --work <new-var-tmp-dir>`; result-only oracle below | step-inventory.json preserves original18 programs/expected summaries; r22 runner constants separately pin cache identities; source_sample_unchanged is HEAD/bare/tracked-status only | private no-local clone at rev; output outside source; original agreement staging; not producer-execution authentication or whole-source integrity proof | souji |
| r21-read-root | gate | `python3 tests/fixtures/r21-read-root.py --tool tools/souji-seat-audit.py --base-tool <6ff3413-auditor-file>` | 0 all32 literal expectations/prior classes; 1 mismatch; 2 usage/baseline-identity refusal | same in-memory invocation, never executes recorded commands | base SHA256 b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389; baseline18/32→32/32 | no production writes | souji |
| r21-reason-canary | gate | `bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base <6ff3413-proc-file>` | 0 all27 controls; 1 mismatch; 2 usage or baseline-identity refusal | `--baseline-as-tool` same oracle fails21 old-emission cases; changed-base synthetic control exits2 | baseline SHA25637c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64; leaks19→0, max454→160 | synthetic /var/tmp input files; --reason-only only, no live proc selftest | souji |
| r21-read-render-edges | gate | `python3 tests/fixtures/r21-read-render-edges.py --tool tools/souji-seat-audit.py` | 0 four no-overreach controls; 1 mismatch; 2 usage | same isolated in-memory invocation | mixed/uppercase URI and conflicts selectors red0/4→4/4 | no writes | souji |
| r21-replay-boundaries | gate | `python3 tests/fixtures/r21-replay-boundaries.py --tool census/round-21/run-acceptance.py --base-tool <8513d6ac-runner-file>` | 0 eight literal output-path expectations; 1 mismatch; 2 usage | same temp-tree invocation; old runner fails4/8 | corpus/lessons/round-21.md; census/round-21/replay-boundaries.txt | own /var/tmp synthetic paths, never invokes runner main | souji |
| r21-source-head | gate | `python3 tests/fixtures/r21-source-head.py --tool census/round-21/run-acceptance.py --base-tool <522dcd76-runner-file>` | 0 three source-state expectations; 1 mismatch; 2 usage | same isolated bare-repository invocation; old runner fails1/3 | census/round-21/source-head-before.txt, source-head-after.txt | own /var/tmp Git fixture only | souji |
| r21-source-refs | gate | `python3 tests/fixtures/r21-source-refs.py --runner census/round-21/run-acceptance.py --root <local-source> --rev <full40> --work <new-var-tmp-dir> [--keep-only]` | 0 expected remote-only18/18 or keep-only exit2/no-result; 1 mismatch; 2 usage | same isolated bare-source construction in each mode | census/round-21/remote-source-before.json, remote-source-after.json, final-code-verification.json | own /var/tmp Git graph only; no source writes or live proc | souji |
| r22-result-oracle | gate | `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` | 0 all258 literal decisions match (original214 plus11+20+13 appended adequacy guards); 1 R22-RESULT-CONTRACT mismatch (including exception); 2 could-not-evaluate input/usage, R22-ORACLE-INPUT-TAMPERED or unknown-case | same committed public18-step outputs plus fabricated deltas; base41553adb graded by `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py \| python3 -B census/round-22/mutation-adequacy.py --grade-stdin` is red:99/258 at observed3.14.8/8192-KiB stack/depth100000 raises | tests/fixtures/r22-result-oracle.json pins receipt/inventory SHA256 and literal wants. Cache positives also require live tools/souji-evidence-cache.py digest dd279ba9…39d6, not hashed by oracle | read-only source/JSON imports; no subprocess, /proc, scratch tree or scanner | souji |
| r22-mutation-adequacy | gate | `python3 -B census/round-22/mutation-adequacy.py [--oracle FILE] [--grade-stdin]` | 0 pristine passes, all expect=killed listed mutants killed, equivalent marks survive; 1 disagreement/pristine failure; 2 missing/ambiguous anchor or usage; stdin mode follows oracle exit map. Receipts bind probe hash, interpreter, soft stack bytes and direct depth100000 decode outcome | historical245 oracle bytes with current59-mutant list must be red (14 non-equivalent survivors, census/round-22/mutation-adequacy-listed59-oracle245.json). A decode that succeeds makes counter/cache-recursion survive rather than proving a catch repair |59 literal replacements; census/round-22/mutation-adequacy-oracle258.json (52 killed,7 named equivalent, observed8192-KiB stack). No exhaustive mutant-space claim | in-memory compile only; no writes, subprocess, /proc or scanner | souji |
| souji-pre-report-gate | gate | `bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS --prereg ABS` | 0 all five checks PASS; 1 any check FAIL; 2 usage; checks branch tip==remote, nonempty report, exactly one SHONEN heading, clean lane worktree, required prereg | `bash tests/fixtures/r27-pre-report-gate.sh` (four isolated real-Git cases and always-pass FALSE-GREEN control) | No pinned baseline; remote branch tip and report/prereg are live inputs | read-only git queries; fixture creates and removes isolated `/var/tmp` repositories | souji  r36 adds `--contract`: predicate 6 runs `tools/souji-report-contract.py` and prints `check-report-contract` PASS or FAIL; without the flag the gate prints `check-report-contract=SKIPPED (no --contract)` and predicates 1-5 behave exactly as r27 froze them. |
| souji-report-contract | gate | `python3 tools/souji-report-contract.py --report ABS --shonen ABS` | 0 every predicate passes; 1 any predicate FAIL; 2 usage/unreadable report or SHONEN.md; predicates: canonical section order (work performed, landed changes, before/after measurements, sources & frontier, trend verdicts, stale-lane), one SHONEN line per SHONEN.md box, one verdict line per learning trend, the stale-lane line, a measurement row carrying a counting command and a measured commit, 1-3 claim ids, an evidence pointer | `python3 tools/souji-report-contract.py --selftest` (9 crafted-report cases, `cases=9 pass=9`, each expecting its exact failing-predicate set; receipt `census/round-36/records/c2-after.txt` @ 1e771ed) | literal expected failing-predicate sets in the selftest table; the report and SHONEN.md are live inputs | reads the report and SHONEN.md only; writes nothing | souji |
| r36-report-gate | gate | `python3 tests/fixtures/r36-report-gate.py [--gate PATH]` | 0 cases=21 pass=21 (21/21 cases) AND the always-pass stub control is rejected; 1 a failed case, a control that replicates the defect verdicts, or usage | same default invocation, one isolated bare-origin clone per case | literal per-case expected exit code and output text plus the STUB-GATE control; receipt `census/round-36/records/c2-after.txt` @ 1e771ed | isolated `TMPDIR` repositories, removed on exit | souji |
| r36-worktree-drift | gate | `python3 tests/fixtures/r36-worktree-drift.py [--tool PATH]` | 0 cases=12 pass=12 (12/12 cases) AND the always-equal stub control is rejected; 1 a failed case, an accepted stub, or usage | same default invocation over synthetic fleets and a real prunable worktree | literal case table (match, regs-changed, prunable-changed, absent, malformed, total-mismatch, empty, unrecorded, read-only) plus the stub control; receipt `census/round-36/records/c3-after.txt` @ 1e771ed | isolated `TMPDIR` fleets, removed on exit | souji |
| r37-citation-reconcile | gate | `python3 tools/souji-citation-reconcile.py --root LANE --rev REV --register TSV --register-rev REV` | 0 `mismatches=0`; 1 any MISMATCH line — citation (`ANCHOR-COUNT`, `EXPECTED-MISSING`, `RECEIPT-UNNAMED`, `STALE-PRESENT`), receipt (`RECEIPT-REV-UNRESOLVED`, `RECEIPT-REV-NOT-ANCESTOR`, `RECEIPT-ABSENT`, `RECEIPT-DISAGREES`) or commit (`COMMIT-UNRESOLVED`, `COMMIT-NOT-ANCESTOR`, `COMMIT-UNNAMED`, `COMMIT-RECEIPT-ABSENT`, `COMMIT-RECEIPT-DISAGREES`); 2 usage / malformed register / non-40-hex rev / non-regular or symlinked register | `python3 tests/fixtures/r37-citation-reconcile.py` -> `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` | register `census/round-37/citation-cells.tsv`; receipts pinned per row at 1e771ed | git show only; working tree never read, nothing written | souji |
| r38-counter-arms | gate | `python3 -B tests/fixtures/r38-counter-arms.py [--tool PATH]` | 0 six cases pass and the always-zero stub is rejected (`control=FALSE-GREEN-REJECTED`); 1 any case fails or the stub passes; 2 usage | same default invocation over a private scratch Git world | literal case ids and expectations: `baseline-ok` rc 0; `comment-tail`, `receipt-rev-not-ancestor`, `receipt-rev-unresolved` each rc 1 with their class; `register-fifo` and `register-symlink` rc 2 `REFUSAL USAGE` inside a 15 s bound | own scratch repo, FIFO and symlink, removed on exit; the lane is read-only | souji |
| r37-drift-escapes | gate | `python3 tests/fixtures/r37-drift-escapes.py [--tool PATH] [--base-tool PATH]` | 0 candidate fail=0 AND base_fail>=8 AND escapes>=6 with `--base-tool` (`control=ESCAPE-REPRODUCED`); a control-free run exits 1; 1 otherwise; 2 usage | `python3 tests/fixtures/r37-drift-escapes.py --base-tool <r36 blob>` -> `cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` | escape cases: out-of-root record row, --json write, GIT_TRACE_REFS, child-env witness, plus two r36 regressions | synthetic fleets under `$TMPDIR`; the base tool is a blob, never the lane worktree | souji |
| r37-drift-discrimination | gate | `python3 tests/fixtures/r37-drift-discrimination.py [--tool PATH]` | 0 `cases=6 pass=6 fail=0`; 1 any case FAIL; 2 usage | `python3 tests/fixtures/r37-drift-mutants.py --fixture tests/fixtures/r37-drift-discrimination.py` -> `mutants=6 killed=6 survived=0` | literal summary fields (live_repos, live_regs, live_prunable, drift_rows, unreachable) and drift classes | synthetic fleets under `$TMPDIR`, removed on exit | souji |
| souji-worktree-drift | gate | `python3 tools/souji-worktree-drift.py --root FLEET --record CENSUS.tsv [--timeout N] [--json OUT]` | 0 no drift rows; 1 drift rows (REGS-CHANGED, PRUNABLE-CHANGED, ABSENT, UNREACHABLE, UNRECORDED); 2 RECORD-MISSING / RECORD-MALFORMED / RECORD-EMPTY / RECORD-OUTSIDE-ROOT / JSON-INSIDE-MEASURED-TREE / JSON-IS-RECORD (the output aliases the record by path or inode) / JSON-NOT-REGULAR (a FIFO, socket or directory is refused without a blocking open) / JSON-HARDLINKED / JSON-UNWRITABLE / USAGE | `python3 tests/fixtures/r36-worktree-drift.py`; `python3 tests/fixtures/r37-drift-discrimination.py`; `python3 tests/fixtures/r37-drift-escapes.py --base-tool <r36 blob>` | none: the record is the live input and the drift is the observation | reads the fleet read-only; `--root` is a containment boundary; the child git env is a whitelist (config neutralised, no inherited GIT_*); `worktree prune` only with `--dry-run -v`; `--json` refused inside any measured path and written through an O_NOFOLLOW descriptor | souji |
| souji-registry-agreement | gate | `python3 -B tools/souji-registry-agreement.py --root LANE --rev REV --list-rev PREREG [--stale-list PATH]` | 0 `mismatches=0`; 1 `mismatches>0`, one line per K1/K2 disagreement; 2 could-not-evaluate (usage, non-40-hex or unresolvable rev, unreadable stale list, list line not 3 TSV fields). Reads `git cat-file`/`-e` only: the working tree is never consulted | `python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py` → `cases=20 pass=20 control=FALSE-GREEN-REJECTED`, rc 0; red arms: the frozen v1 tool → `cases=20 pass=8`; a copy with the entry→row reverse check deleted → `cases=20 pass=15` (`census/round-29/records/c1-fixture-red-before.txt`) | fixture's literal 20-case table; `census/round-29/stale-statements.tsv` (4 frozen statements); base witness `mismatches=10` in `census/round-29/records/preregistration.txt` | committed bytes only, never writes; fixture scratch under `/var/tmp/souji-r29-c1-fixture` | souji |
| souji-wave-evidence-capture v2 (committed-bytes) | probe | `bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]` | 0 captured+verified, or `verified:` / `verify-rev … failed=0 uncovered=0`; 1 usage error, `--rev` without `--verify`, non-40-hex or unknown revision; 2 source directory missing; 3 refusal (special file, path escape, nested src-dst, stored-name collision); 4 verification failed (manifest mismatch, missing or uncovered record, receipt/source set mismatch, lane not a git repository under `--verify --rev`); 5 copy/receipt write failure. A verify verdict is data; the gate is `r29-c2-counter` | `bash tests/fixtures/r28-wave-evidence-capture.sh` → `cases=15 pass=15 control=TAMPER-REJECTED`, rc 0 against these tool bytes; red arm `SOUJI_CAPTURE_TOOL=<base tool blob b8cb4b31>` → `cases=15 pass=8 control=TAMPER-REJECTED`, rc 1 (`census/round-29/records/c2-fixture-red-before.txt`; cases 7–12 and 15 are the committed-bytes layout) | fixture's 15 literal cases (1–6 preserved from the r28 six-case file; a `.git` component is stored as `.git.captured`); limits from the C2 fixture: symlinks.tsv column 1 is the bare path relative to `census/round-N/waves` | writes only `<lane>/census/round-N/waves/`; `--verify` read-only (git plumbing, no mutation); never network; fixture scratch under `/var/tmp/souji-r29-wave-capture-fixtureV2` | souji |
| r29-c2-counter | gate | `python3 -B census/round-29/c2-counter.py --root LANE --rev REV` | 0 `SUMMARY manifests=<m> failed=0 uncovered=0 floor_violations=0` with m ≥ 1; 1 any failed/uncovered record or floor violation, and also could-not-evaluate — no code 2 exists (bad revision or git failure prints `COULD-NOT-EVALUATE …` and exits 1) | red arm reproducible from committed history: at `691dd29211c53d0ef94fa072394cb9c8a69fe92e` → `manifests=3 failed=152 uncovered=14 floor_violations=0`, rc 1; green arm: the round's landing tip must print `failed=0 uncovered=0`, rc 0. Discriminating scratch arms in `census/round-29/waves/w1/deliver-c2-history.tsv`: dropped escaped records → `uncovered=16`; zeroed hash → `failed=153` | embedded `FLOORS` (r26 1230, r27 124, r28 75) frozen by `census/round-29/records/preregistration.txt` C2; stricter amendment A3 `census/round-29/c2-counter-v2.py --base-rev PREREG` (adds lost, fidelity, r26 floor 1378, tool_unchanged) | `git ls-tree`/`cat-file` only, never the working tree, never writes | souji |
| souji-capability-agreement | gate | `python3 -B tools/souji-capability-agreement.py --root LANE --rev REV --base BASE --list-rev PREREG [--only R01,...]` | 0 `SUMMARY k1=0 k2=0 mismatches=0`; 1 any `MISMATCH` row or unresolved SHONEN pointer (`ROW`/`PTR` lines say which; `KINDS` is diagnostic); 2 could-not-evaluate (non-40-hex rev, rows file absent at PREREG) | red arm at base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`: `k1=13` (v1) / `k1=12` (A3), `census/round-30/records/c1-before.txt`, `controls-amended.tsv`; A3 refuses `cmd=python3 -c pass <script>` and banner observations | rows `census/round-30/c1-rows.tsv` read at PREREG; v1 blob at `d4928ec86b667e3d1ed0adb07fb088e500cf1631` | private `git clone --no-local` per run under `--scratch` (origin removed), deleted on exit; never the lane | souji |
| r30-landing-gate-discovery | gate | `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py` | 0 `cases=7 pass=7 control=FALSE-GREEN-REJECTED`; 1 any `CASE D<k> FAIL` or an accepted always-zero control; 2 missing prerequisite (TMPDIR unset, tool absent) | red arm: base gate at `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` prints `cases=7 pass=3` (D1 D4 D6 D7 FAIL), `census/round-30/records/c2-fixture-red-before.txt`; the C2 v2 counter adds counter-owned NOCAP and PTRARM arms | cases D1-D7 frozen in `census/round-30/records/preregistration.txt` C2 | synthetic repos under `$TMPDIR` only | souji |
| r30-jj-keep-expiry | probe | `TMPDIR=<scratch> bash tests/fixtures/r30-jj-keep-expiry.sh` | 0 prints `jj-version:`, `git-version:` and eight `RESULT step=... keep_refs=N object_present=yes/no` lines; 2 refused (TMPDIR unset, or resolving inside the souji lane or the fleet root) | replay equality with `census/round-30/records/jj-keep-expiry-run.txt` is the C3 v2 E3 leg (`census/round-30/c3-counter-v2.py`) | jj 0.45.1, git 2.56.0 (version lines in the record) | jj-colocated scratch repos under `$TMPDIR`, every jj call `-R`, every git call `-C`; never a lane | souji |
| souji-capability-cells | gate | `python3 -B tools/souji-capability-cells.py --root LANE --rev REV --base BASE --list-rev PREREG [--only L01,...]` | 0 `unbound=0 mismatches=0` over `items=41`; 1 any `ITEM` line whose verdict is `UNBOUND`, `RUN-MISMATCH`, `RECORD-MISMATCH` or `BAD-ROW`; 2 could-not-evaluate (non-40-hex or unresolvable revision, enumeration absent at PREREG, git failure). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; red arms `C1-do-nothing(base)` (`unbound=22 mismatches=34`) and `C1-junk1` through `C1-junk5` in `census/round-31/records/controls.tsv`, `C1-junk-A2(non-count literal)` in `controls-amended.tsv`, four A4 shapes in `controls-a4.tsv`; green 41/41 is not reached at r31 (L29 honest miss, `unbound=1 mismatches=1`) and is reachable by a substitution binding the counter cannot refuse, so a green run is audited, never accepted | enumeration `census/round-31/c1-cells.tsv` read at PREREG, 41 items at base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; `SCORECARD.md` base bytes must prefix REV | one private `git clone --no-local` per run under `--scratch`, origin removed, deleted on exit; executes only the bound script from the base blob, never a shell; never the lane worktree | souji |
| r31-landing-gate-precision | gate | `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool PATH` | 0 a `CASE G1` to `CASE G10 PASS` line each and last line `cases=N pass=N control=FALSE-GREEN-REJECTED`, N at least 10; 1 any `FAIL` case or an accepted always-zero control; 2 missing prerequisite (tool absent, no git, TMPDIR unset or resolving inside the lane or the fleet root) | same default invocation; red arm is the base tool blob, which prints `cases=10 pass=3` and fails exactly G1 G3 G4 G5 G6 G7 G8 while G2 G9 G10 stay green (this is the C2 counter's REDARM leg) | cases G1 to G10 frozen in `census/round-31/records/preregistration.txt` C2; G8 is the contract's prose-alternation case and carries the letters-only blind spot | synthetic rounds under `$TMPDIR` only, removed in `finally`; never writes in a lane checkout | souji |
| r31-jj-object-clock | probe | `TMPDIR=<scratch> bash tests/fixtures/r31-jj-object-clock.sh` | 0 prints a `jj-version:` line, a `git-version:` line and 17 `RESULT arm=… step=… keep_refs=N target_keep=… reflog_hits=N object_present=yes-or-no` lines; 2 refused (TMPDIR unset, empty, not a directory, or resolving inside the souji lane or the fleet root) or interrupted | no self-test; the judging instruments are the C3 counter's legs L8 (record shape), L9 (two replays equal the record), L12 (jj and git argv logged through a shim) and L13 (remover subtraction, M1 reflog expire and M2 gc/prune) | `census/round-31/records/jj-object-clock-run.txt` (17 RESULT lines, jj 0.45.1, git 2.56.0, recorded at the C3 landing commit and re-run byte-identical at the tip) | jj-colocated scratch repositories under `$TMPDIR`, every jj call `-R`, every git call `-C`; never a lane | souji |
| r32-jj-mtime-clock | probe | `TMPDIR=<scratch> bash tests/fixtures/r32-jj-mtime-clock.sh` | 0 prints a `jj-version:` line, a `git-version:` line and 22 `RESULT arm=… step=… obj=… mtime=… where=… object_present=…` lines per `census/round-32/c3-contract.txt`, every arm of that contract carrying a `gc-` step and `mixed` carrying one for `obj=B` and one for `obj=C`; 2 refused (TMPDIR unset, empty, not a directory, or resolving inside the souji lane or the fleet root; `jj`, `git` or `touch` absent from PATH; an `mktemp` base resolving into either root) or interrupted | no self-test; the judging instrument is the r32 C3 counter's legs L8 (record shape and arm coverage), L9 (two replays equal the record), L12 (jj, git and touch argv through a shim) and L13 (M2 gc/prune/repack and M3 touch subtraction mutants), plus amendment A1's `census/round-32/c3-counter-v2.py` legs L15 (an independent plain-git recent/old probe), L16 (shimmed call exit statuses) and L17 (live re-fetch of every snapshot) | `census/round-32/records/jj-mtime-clock-run.txt`; field contract `census/round-32/c3-contract.txt` | jj-colocated scratch repos under `$TMPDIR`, backdating only by `touch -d` on loose object files, every jj call `-R`, every git call `-C`; never a lane | souji |
| souji-record-contract | gate | `python3 -B tools/souji-record-contract.py --record PATH --contract PATH` | 0 `lines=<n> bad=0` with n ≥ 1 (every record line carrying the contract prefix has exactly the frozen keys in order, each value in its set); 1 any `BAD <line> <reason>` line, or a record with no prefixed line; 2 could-not-evaluate (unreadable record or contract, malformed contract line, no prefix line, no key line) | red arm from committed bytes: the r31 object-clock record against the r31 contract prints `BAD 16` to `BAD 19` and `lines=17 bad=4`, rc 1 (`census/round-32/records/m1-red-before.txt`); green arm: the r32 run record against `census/round-32/c3-contract.txt` prints `lines=<n> bad=0`, rc 0, which is the r32 C3 counter's L14 | reconstructed r31 contract `census/round-32/m1-r31-contract.txt`; r32 contract `census/round-32/c3-contract.txt` | read-only; writes nothing | souji |
| r32-c2-counter | gate | `python3 -B census/round-32/c2-counter.py --root LANE --rev REV --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev PREREG` | 0 `SUMMARY items=27 pass=27 fail=0`; 1 any `ITEM` line without `PASS` (the sandboxed run's exit code or normalized last digit-bearing line differs from the base run's, or its successful file-creating syscalls are below half of the base run's, so a tool that stops working to dodge the sandbox fails); 2 could-not-evaluate (usage, non-40-hex or unresolvable revision, items file absent at `--list-rev`, `bwrap` or `strace` absent, git failure). `--only` prints `partial=1` and is diagnostic, never a pass | red arm reproducible from committed bytes: the same command with `--rev 85b61a151923986e7e6b48f7084b9122561b5f3d` prints `SUMMARY items=27 pass=1 fail=26`, rc 1 (`census/round-32/records/controls.tsv`, control `C2-do-nothing(prereg)`); the frozen target `fail=0`, rc 0 was NOT reached: the C2 landing commit and the round-32 tip print `fail=1` or `fail=2` (T18's `baseline_mismatches` anchor moves with any edit to its closure files, and T12's timed census selftest flips under the strace-wrapped sandbox; `census/round-32/records/c2-after-v1.txt`, `census/round-32/records/a2-l1-salvage-tip-measure.txt`), so a green arm has not been observed | item set `census/round-32/c2-items.tsv` read at `--list-rev`; base commit 85b61a151923986e7e6b48f7084b9122561b5f3d | private `git clone --no-local` per run under `--scratch` (origin removed), one fresh `$TMPDIR` per run, `bwrap` read-only /tmp, /var/tmp and /dev/shm; read-only on `--root` | souji |
| r32-c1-counter | gate | `python3 -B census/round-32/c1-counter.py --root LANE --rev REV --base BASE --list-rev PREREG [--only N01,...]` | 0 `SUMMARY items=44 … unbound=0 mismatches=0` with `withdrawn<=8`; 1 any ITEM line whose verdict is `UNBOUND`, a `BAD-ROW(...)` form, `MISMATCH(append-only-violated)`, `RUN-MISMATCH`, `RECORD-MISMATCH` or `FIELD-MISMATCH`, or `withdrawn` above 8; 2 could-not-evaluate (non-40-hex or unresolvable revision, enumeration absent at PREREG, SCORECARD.md absent at BASE or REV, clone failure or clone toplevel mismatch, git failure). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; `bash census/round-32/controls.sh 3ec84fc81b3243429c834a051880b0bcde06291c` reproduces the red arms as TSV (its output, redirected, is `census/round-32/records/controls.tsv`) (`C1-do-nothing` `unbound=44 mismatches=44`; `C1-junk1` `withdrawn=44`, refused by the withdrawal cap; `C1-junk2` `bound_record=39 unbound=1 mismatches=5`). Amendment A0's stricter readings are in `census/round-32/records/controls-a0.tsv` (same binder `bound_record=5 mismatches=39`; cited-record binder `bound_record=13 mismatches=31`), produced by `census/round-32/controls-a0.sh` | enumeration `census/round-32/c1-items.tsv` read at PREREG (44 items); `SCORECARD.md` base bytes must prefix REV; stricter amendment A0 `census/round-32/c1-counter-v2.py` must print the same target; observed at the C1 landing commit and at the round-32 tip: `withdrawn=17 unbound=6 mismatches=6` under both, so this target was missed (`census/round-32/records/c1-after-v1.txt`) | one private `git clone --no-local` per run under `--scratch`, origin removed and the tree cleaned before every bound run, deleted on exit; executes only the bound script taken from the `--base` blob, never a shell; never the lane worktree | souji |
| r32-c3-counter | gate | `python3 -B census/round-32/c3-counter.py --root LANE --rev REV --base BASE --list-rev PREREG` | 0 `SUMMARY legs=14 fail=0 f1_entries=5`; 1 any failed leg; 2 could-not-evaluate (non-40-hex revision, jj, git or touch absent, `git archive` export of REV failed) | no embedded selftest; the red readings are pinned in `census/round-32/records/controls.tsv` — do-nothing `legs=14 fail=13 f1_entries=4`, and `C3-junk(sourceless entry + typed record + cat fixture)` `legs=14 fail=6 f1_entries=5`, so a typed record and a fixture that cats it are refused by the replay, shim and subtraction legs | contract `census/round-32/c3-contract.txt` read at PREREG and required unchanged at REV (L14); entry, fixture and record read at REV | `git archive` export of REV plus fixture scratch under `--scratch`, removed on exit; fixture calls its own `TMPDIR`; every jj call `-R`, every git call `-C`; never the lane worktree | souji |
| r33-c1-counter | gate | `python3 -B census/round-33/c1-counter.py --root LANE --rev REV --list-rev PREREG --scratch DIR [--only K01,...]` | 0 `SUMMARY items=24 agree=24 mismatches=0 restated=<n>` (exit 0 iff mismatches=0); 1 any ITEM line that is not `AGREE`, including a `BAD-ROW(...)`, `BAD-CAUSE(...)` or `RUN-FAILED(...)` detail; 2 could-not-evaluate (non-40-hex or unresolvable `--rev`/`--list-rev`, `census/round-33/c1-items.tsv` absent or malformed at `--list-rev`, `SCORECARD.md` absent at either revision or not starting with its `--list-rev` bytes, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, unknown `--only` id, git failure). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; `census/round-33/records/controls.txt` holds the do-nothing red arm `SUMMARY items=24 agree=19 mismatches=5` rc 1 (K04 K05 K16 K17 K18), and `census/round-33/records/feasibility.txt` holds the two scratch-list-rev arms — the junk rows (`65812db`) each `MISMATCH … BAD-CAUSE`, for a substring statement and for a true line with a non-causal commit, so neither binds, and the feasibility leg (`190b4b1`) binding K05 and K18 `AGREE … restated`; both hashes are scratch commits, present only in that receipt | `census/round-33/c1-items.tsv` read at PREREG and never at REV; the `### Round 33 capability currency` rows of `SCORECARD.md` read at REV, each cause commit executed at the cause's parent and at the cause | private `git clone --no-local --no-checkout` per item under `--scratch` (origin removed, detached at REV, `{SCRATCH}` a per-item dir), removed after the run; read-only on `--root` | souji |
| r33-c2-counter | gate | `python3 -B census/round-33/c2-counter.py --root LANE --rev REV --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev PREREG --scratch DIR [--only O1,...]` | 0 `SUMMARY legs=11 pass=5 fail=0 harm=0` (exit 0 iff fail=0 and harm=0); 1 any O leg that is not `PASS`, or any FAILed G guard; 2 could-not-evaluate (non-40-hex or unresolvable `--rev`/`--base`/`--list-rev`, `bwrap` or `strace` absent, `census/round-33/c2-legs.tsv` absent or malformed at `--list-rev`, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, unknown `--only` id, clone failure or clone toplevel mismatch). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; the same command with `--rev` at the preregistration commit (tools identical to base `6017a48`) reads `SUMMARY legs=11 pass=0 fail=5 harm=0` rc 1 in `census/round-33/records/controls.txt`; the feasibility leg in `census/round-33/records/feasibility.txt` (scratch commit `6a409e1`) turns O2 and O4 green while G4 reds on the changed r15 pin (`legs=4 pass=2 fail=0 harm=1 partial=1`), which is the declared Q73 re-pin step, not a pass | `census/round-33/c2-legs.tsv` read at PREREG, leg kinds and per-kind PASS rules in its header: base line equality for every kind, the sandbox leg's half-of-base file-creating syscall count, and the slash leg's equality with the same `TMPDIR` spelled without the trailing slash | two private `git clone --no-local --no-checkout` copies (base, rev) under `--scratch`, `git clean -fdx` before every run, `bwrap` with read-only empty `/tmp`, `/var/tmp`, `/dev/shm`, strace logs in `--scratch`, all removed after the run; read-only on `--root` | souji |
| r34-c1-counter | gate | `python3 -B census/round-34/c1-counter.py --root LANE --rev REV --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch DIR [--only G01,...]` | 0 `SUMMARY items=60 agree=60 mismatches=0`; 1 any item MISMATCH/BAD-ROW/BAD-CAUSE/RUN-FAILED; 2 could-not-evaluate (invalid or missing revision/input, non-persistent scratch root, malformed items, failed clone). The target was not reached: base control `agree=35 mismatches=25`; W1 proved frozen unreachable predicates/cause bindings, including G05/G17b/G24/E23b. A targeted counter row may be diagnostic only; `--only`/`partial=1` is never a gate pass | `python3 -B census/round-34/c1-counter.py --selftest` is a literal tripwire only; the behavioral forged-row control is `python3 -B tests/fixtures/r34-c1-junk.py --counter census/round-34/c1-counter.py --scratch DIR` (`cases=3 pass=3 control=STUB-REJECTED`, frozen-control revision only) | frozen item set `census/round-34/c1-items.tsv` at list revision 2b0171e; base and control receipts in `census/round-34/records/controls.txt`; append-only valid corrections at `SCORECARD.md` `### Round 34 registry restatements`; overall target remains unmet | read-only lane input; one clone per selected item under caller scratch, origin removed, detached; Q77 lock under scratch | souji |
| r34-c2-counter | gate | `python3 -B census/round-34/c2-counter.py --root LANE --rev REV --base 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch DIR` | 0 `SUMMARY legs=13 pass=13 fail=0 harm=0`; 1 any LEG not PASS; 2 could-not-evaluate (invalid revisions, absent/malformed legs, unavailable bwrap/strace, ephemeral scratch, clone failure). Repaired feasibility is red: `legs=13 pass=9 fail=4 harm=0` (W2, W3, N3, J1 fail); no C2 pass is claimed | `python3 -B census/round-34/c2-counter.py --selftest` behaviorally refuses witness-dropped/junk-less legs; J1 fixture `python3 -B tests/fixtures/r34-sandbox-junk.py --counter census/round-34/c2-counter.py --scratch DIR` timed out at 900 s, not a pass | frozen legs `census/round-34/c2-legs.tsv`; re-pinned counter 2b0171e; feasibility and junk outcomes in `census/round-34/records/controls.txt` | private per-leg clones, bwrap sandbox with TMPDIR and private `/var/tmp` bind; real `/var/tmp` canary checked for N3; lane working tree read-only | souji |
| c1-counter (r39) | gate | `python3 -B census/round-39/c1-counter.py --root LANE --rev REV --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv [--register-rev REV] [--min-cells N] [--min-commit-distinct N] [--scratch DIR]` | 0 `SUMMARY items=16 open=0 register_cells>=6 register_mismatches=0 commit_distinct>=2`; 1 any OPEN item or register mismatch/floor; 2 usage, malformed items/register or an unresolvable revision. A register absent at a resolvable revision is not exit 2: it prints `REGISTER cells=0` and exits 1 on the floor. A `--scratch` parent that does not exist is refused as could-not-evaluate (exit 2). Reads committed bytes only and prints `items_sha=`; the item list is an instrument read from the working tree. | base control `census/round-39/records/c1-before.txt` (`open=16`); after `c1-after.txt` | items `census/round-39/c1-items.tsv`, register `census/round-39/cells.tsv` (emitted by `census/round-39/make-cells.py --write`; absent until landed) | `git show` and a private scratch extraction only; no writes | souji |
| c2-counter (r39) | gate | `python3 -B census/round-39/c2-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]` | 0 `SUMMARY legs=6 pass=6 fail=0 harm=0`; 1 any failing leg or consumer regression; 2 usage or could-not-evaluate input. L1/L2 unresolvable `--rev` classes, L3 `--register-rev` harm, L4 drift docstring class map, L5 `tests/fixtures/r39-citation-rev.py` discrimination, L6 the five consumer fixtures in `CONSUMERS` (the frozen prereg's L6 prose says six; the counter has carried five since the freeze commit b769bfb). A `--scratch` parent that does not exist is refused as could-not-evaluate (exit 2). Both tool revisions come from `git show`; fixtures from the working tree. | base control `census/round-39/records/c2-before.txt` (`pass=2 fail=4`); after `c2-after.txt` | none pinned; receipts name the measured revision | private scratch only | souji |
| c3-counter (r39) | gate | `python3 -B census/round-39/c3-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]` | 0 `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`; 1 any survivor, base kill, pristine failure or short fixture; 2 usage/CNE; a `--scratch` parent that does not exist is refused as could-not-evaluate (exit 2), while an absent `--fixture` path still raises `FileNotFoundError` (rc 1) and is a named limit. Mutants M11-M14 over the drift record parser; a kill needs the fixture's own `fail>0` and no traceback (r38 A5). | base control `census/round-39/records/c3-before.txt`, reproduced exactly by `--rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py` (`killed=0 survived=4 cases=10`); after `c3-after.txt`. The counter mutates whichever tool `--rev` names and reads the candidate fixture from the working tree, so `--rev base-rev` with the landed fixture prints the same green summary (only `tool_sha` differs): C3 measures the fixture's coverage, not the tool repair; the frozen control separates the arms only by pairing the base fixture with base tool bytes | fixture `tests/fixtures/r39-drift-record-rules.py`; tool bytes at `--rev` | private scratch only | souji |
| r39-citation-rev | gate | `python3 -B tests/fixtures/r39-citation-rev.py [--tool PATH] [--work DIR]` | 0 eight revision-resolution cases pass; 1 any case mismatch; 2 usage. Cases: absent/blob/tree/short/tag revisions (`REV-UNRESOLVED` or `USAGE`), a clean run, `--register-rev` unresolvable, register absent at a resolvable revision. | same default invocation against the base blob (`rc=1`, `fails=4`) | literal case table in the fixture; `census/round-39/records/c2-after.txt` L5 | isolated scratch Git repository only | souji |
| r39-drift-record-rules | gate | `python3 -B tests/fixtures/r39-drift-record-rules.py [--tool PATH] [--work DIR]` | 0 seven record-file cases pass; 1 any case mismatch; 2 usage. Cases: good, trailing-space refused, TOTAL-before-rows accepted, CRLF accepted, outside-root refused, indented comment refused, comments+TOTAL → `RECORD-EMPTY`. | the base tool passes 7/7 (`cases=7 pass=7`: the behaviours pre-exist; the round adds the assertions), so the failing arm is the mutant battery — `census/round-39/c3-counter.py` kills M11-M14 against the audited bytes (`fails=1` each) | literal case table in the fixture; `census/round-39/records/c3-after.txt` | isolated scratch Git fleet only | souji |
| r38-citation-commit | gate | `python3 -B tests/fixtures/r38-citation-commit.py [--tool PATH] [--work DIR]` | 0 `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED`; 1 any case mismatch; 2 usage. | same invocation; the always-zero emitter is rejected on 14 cases | literal case table; `census/round-38/records/c1-after8.txt` | isolated scratch Git only | souji |
| r38-drift-write-envelope | gate | `python3 -B tests/fixtures/r38-drift-write-envelope.py [--tool PATH] [--base-tool PATH] [--work DIR]` | 0 `cases=12 pass=12 fail=0`; 1 any case mismatch; 2 usage. | same invocation with the r37 blob (`4c257b7:tools/souji-worktree-drift.py`) as `--base-tool` reproduces `base_fail=6 behavioral_fail=3` (`docstring-enum`, `fifo-json-refused`, `record-alias-refused`) | literal case table; `census/round-38/records/c2-after7.txt` | isolated scratch only | souji |
| r38-drift-record | gate | `python3 -B tests/fixtures/r38-drift-record.py [--tool PATH] [--work DIR]` | 0 `cases=10 pass=10 fail=0`; 1 any case mismatch; 2 usage. | same invocation; the M7-M10 battery (`r38-drift-mutants.py`) is the failing arm: with `--fixture tests/fixtures/r37-drift-discrimination.py` it reads `survived=4`, rc 1 | literal case table; `census/round-38/records/c3-arms-filed.txt` | isolated scratch Git fleet only | souji |
| r38-drift-mutants | gate | `python3 -B tests/fixtures/r38-drift-mutants.py --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py [--work DIR]` | 0 `mutants=4 killed=4 survived=0 pristine=ok base_killed=0`; 1 any survivor or pristine failure; 2 usage. | the battery is its own control (it refuses a fixture without a summary and a kill without `fail>0`); its failing arm is `--fixture tests/fixtures/r37-drift-discrimination.py` → `survived=4`, rc 1 | mutant list literal; `census/round-38/records/c3-arms-filed.txt` | isolated scratch only | souji |
| souji-freeze-check | gate | `python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40` | 0 `SUMMARY claims=<n> findings=0`; 1 one or more `FINDING <claim> <CLASS> <detail>` lines (NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST, POPULATION-MISSING, POPULATION-DIGEST, POPULATION-EMPTY, CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE; prereg-wide findings use claim label `C0`); 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE:` on stderr: `--root` not a directory, `--rev` not a full40 commit, PATH absent at `--rev`). Reads the preregistration as a git blob at `--rev`, never the work tree. Named limits (r41 lesson N13): duplicate keys read first-wins, a malformed `## C` heading is dropped, an unlisted dispatch file name is not checked. | `python3 -B census/round-41/c2-counter.py --root LANE --rev FULL40` (21 synthetic-repo cases, two always-same stubs that must be rejected, a real leg and a retro leg) | `census/round-41/preregistration.txt` (claims=3 findings=0); the counter's literal case table (`census/round-41/c2-cases.tsv`) | reads git blobs only; counter scratch under `TMPDIR` | souji |
| r41-freeze-check-cases | gate | `python3 -B census/round-41/c2-counter.py --root LANE --rev FULL40 [--tool PATH-IN-REV] [--scratch DIR]` | 0 `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red`; 1 target unmet (any case fails, a stub accepted, real not ok, retro not red, tool absent at `--rev`); 2 could-not-evaluate (scratch not a directory, `--rev` not a resolvable full40 commit). | the failing arms are `census/round-41/controls/c2-control.txt` (tool absent: pass=0; always-clean stub: pass=2 of 21, `EXIT=1`) | frozen digest in `census/round-41/preregistration.txt` C2; `census/round-41/c2-cases.tsv` | isolated scratch git repositories under `--scratch` | souji |
| r41-refusal-sites | gate | `python3 -B tests/fixtures/r41-refusal-sites.py --tool tools/souji-worktree-drift.py --work DIR` | 0 `SUMMARY probes=21 pass=21 fail=0`; 1 any probe FAIL; 2 usage or euid 0 (the EACCES probes change class under root). Each of 21 probes asserts exit 2 and `REFUSAL <CLASS>:` for the site `census/round-41/c3-sites.tsv` maps it to. Scored by `python3 -B census/round-41/c3-counter.py --root LANE --rev FULL40 [--scratch DIR]` (0 `sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`; 1 target unmet; 2 could-not-evaluate). | the counter rewrites each site's class label in a scratch copy of the pinned tool and requires the failing probe set to equal the mapped set; failing arms `census/round-41/controls/c3-control.txt` (fixture absent; all-PASS stub survives 19 of 19) | `census/round-41/c3-sites.tsv`; tool sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` | isolated scratch under `--work`; never writes outside it | souji |
| r41-drift-record-order | gate | `python3 -B tests/fixtures/r41-drift-record-order.py [--tool PATH] [--work DIR]` | 0 `SUMMARY cases=12 pass=12 fail=0`; 1 any case mismatch; 2 usage. Scored by `python3 -B census/round-41/r1-counter.py --root LANE --rev FULL40 [--scratch DIR]` (0 `mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6`; 1 target unmet; 2 could-not-evaluate). | the counter applies mutants M11-M21 (M19 last-TOTAL-only, M20 root dropped from discovery, M21 root-basename row unresolved); failing arms `census/round-41/controls/r1-control.txt` (fixture absent; stub kills 8, new_killed 0/3) | mutant table in `census/round-41/r1-counter.py`; tool sha256 as above | isolated scratch Git fleet only | souji |
| r41-c1-corrections | gate | `python3 -B census/round-41/c1-counter.py --root LANE --rev FULL40` | 0 `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`; 1 target unmet; 2 could-not-evaluate (rev unresolved, measured revision absent, items table differs from its pinned digest). It reads `corpus/lessons/round-41.md`, `corpus/SOURCES.md` and the three filed files as git blobs. Shape-only: it does not read correction prose (r41 lesson N1-N4). | failing arms `census/round-41/controls/c1-control.txt` (no lesson: corrected=0; junk lesson: junk=3) | `census/round-41/c1-items.tsv` sha256 `2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf` | read-only | souji |
| r42-c1-counter | gate | `python3 -B census/round-42/c1-counter.py --root LANE --rev FULL40 [--base FULL40] [--scratch DIR]` | 0 `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=K corrected=K junk=0 rewritten=0 new_mismatches=0` (K = 5 frozen in the preregistration); 1 target unmet; 2 could-not-evaluate (bad rev/base, tool or items absent, scratch). The 70 items are the `mismatches=70` of `python3 -B tools/souji-declared-evidence.py --file SCORECARD.md --rev BASE`. | `census/round-42/controls/c1-control.txt` (no register: `registered=0`; forged all-resolved register: `class_ok=42`); `census/round-42/controls/c1-forged-register.tsv` | `census/round-42/c1-items.tsv` sha256 `b2601340eb20f70b0298542806acd47ef6e60586eacac92efdf94b1b231a8d39`; counter `census/round-42/c1-counter.py` sha256 `0ab07cd3c99e6bbe26220d9e36672b6a7acd45150b96fff1868d0e082dcd46aa`; register `census/round-42/c1-register.tsv`; lesson `corpus/lessons/round-42.md` CORRECTION-DE lines | read-only lane; scratch under `--scratch` only | souji |
| r42-c2-counter | gate | `python3 -B census/round-42/c2-counter.py --root LANE --rev FULL40 [--tool PATH-IN-REV] [--scratch DIR]` | 0 `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3`; 1 target unmet (any case fails, either built-in stub accepted, real not ok, retro not red, retro_clean not ok, selftest not ok, fewer than 3 patches rejected; an absent tool is included); 2 could-not-evaluate. | `census/round-42/controls/c2-control.txt` (the r41 tool: `pass=24` of 37 and no selftest; the r41 tool with an always-green `--selftest`: `patches=0/3`); `census/round-42/controls/c2-stub-tool.py` | `census/round-42/c2-cases.tsv` sha256 `148b7b87411eb282e0207cf5471d55be81e03d4a26ffafd96df37b4db4fd4511`; counter `census/round-42/c2-counter.py` sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1`; source S259 (Python `site` documentation) | scratch repositories and runtime-patch directories under `--scratch` / `TMPDIR`; lane read-only | souji |
| r42-freeze-check-selftest | gate | `python3 -B tools/souji-freeze-check.py --selftest` | 0 iff `SELFTEST cases=<n> pass=<p> fail=0` with n >= 12 (the counter's docstring names no other code; any nonzero exit is a failure); non-zero otherwise. Driven by the C2 counter's `selftest` and `patches=3/3` legs: P1 sha256 digests reversed, P2 `git log --diff-filter` returns nothing, P3 `git merge-base` always fails. **Unreached classes (Q105):** the patch reaches the tool only when it runs in an interpreter started with the patch directory on PYTHONPATH and without `-I`/`-E`/`-S`; a child started with those flags, or an external program, is not patched (`census/round-42/waves/w1/R42scribe07/receipts/python-startup-probe.txt`). | the three runtime patches of `census/round-42/c2-counter.py` (`patches=0/3` on the always-green stub is the failing arm) | tool bytes at the landing commit (`tools/souji-freeze-check.py`; not pinned at freeze, the counter pins its behaviour, not its digest) | synthetic git repositories under `TMPDIR` (removed by the self-test) | souji |
| r42-c3-counter | gate | `python3 -B census/round-42/c3-counter.py --root LANE --rev FULL40 [--fixture PATH-IN-REV] [--scratch DIR] [--survey]` | 0 `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok`; 1 target unmet; 2 could-not-evaluate (bad rev, uid 0, pinned bytes differ, anchor defect). `--survey` prints which prior fixtures kill each mutant and is never a verdict. | `census/round-42/controls/c3-control.txt` (fixture absent: `survived=13`; always-pass stub: `survived=13`; byte-sniffing stub: `equiv_killed=6`); `census/round-42/controls/c3-stub-allpass.py`, `c3-stub-sniff.py` | `census/round-42/c3-mutants.tsv` sha256 `2f6f8df39ed6dd66cda22806012b68db9e12712e5572931286daed60a4bab205`; counter `census/round-42/c3-counter.py` sha256 `bf0ebf4fef0cf0070daf2dd89184e83575bfabe4e4e82fa50511b3c6c8585d76`; pinned tool `tools/souji-worktree-drift.py` sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` | scratch copies of the pinned tool under `--scratch`; lane read-only | souji |
| r42-drift-conditions | gate | `python3 -B tests/fixtures/r42-drift-conditions.py --tool tools/souji-worktree-drift.py --work DIR` | 0 `SUMMARY cases=<n> pass=<p> fail=0` (exit 0 iff fail=0); 1 any case FAIL. Scored by `python3 -B census/round-42/c3-counter.py` (the counter reads this fixture as the candidate; `pristine=ok` needs cases >= 13). Codes other than 0 and 1 are not named by the counter docstring. | the thirteen condition-level mutants of `census/round-42/c3-mutants.tsv` (B1 E2 E4 G2 G3 G4 G5 H1 H2 I1 J9 M1 D4) and the six equivalents that the fixture must NOT kill (B3 B4 E5 E7 E9 H4) | `tests/fixtures/r42-drift-conditions.py` sha256 (recorded at landing; the counter scores the landed bytes) | `--work DIR` only; the fixture's mutant copies live under `--work` | souji |
| r42-r1-counter | gate | `python3 -B census/round-42/r1-counter.py --root LANE --rev FULL40 [--base FULL40] [--scratch DIR]` | 0 `SUMMARY findings=0 deleted=0 rows_added=3 stale=0`; 1 target unmet; 2 could-not-evaluate (scratch not a directory, bad revision, `git archive` failure). The gate it runs is `python3 -B tools/souji-landing-gate.py --root LANE --rev REV --round 41` with NO `--fleet-root` (Q103). Frozen predicate found wrong in r42 (lesson M42-2): three exemption rows read green without `--fleet-root` and `findings=2` (`LG-DANGLING-PTR-EXEMPT-STALE`) with it; the landed repair is a repoint (README and the jj-colocation entry cite `census/round-42/jj-w1-reports/`), which this counter reads `findings=0 deleted=2 rows_added=0 stale=0` = red by its letter; both gate modes read `findings=0` (`census/round-42/records/gate-both-modes.txt`) | `census/round-42/controls/r1-control.txt` (`SUMMARY findings=3 deleted=0 rows_added=0 stale=0`, `rc=1`) | `census/round-42/r1-counter.py` sha256 `f2dcbd06eecdb864e5ca215154aa82e564f7dbba586f617ad5543c0a811cc1bb`; base `bf618f6c5c09d302994871c94903abbea2deb60d` | scratch export under `--scratch` / `TMPDIR` (the gate runs from a `git archive` of `tools` and `corpus` at REV); lane read-only | souji |

| souji-idx-repair | gate | `python -B tools/souji-idx-repair.py --root LANE --rev FULL40 [--receipt PATH] [--dry-run]` / `--selftest` | 0 worktree restored to the frozen Amendment-1 tolerance (or already inside it; selftest `SELFTEST cases=5 pass=5 fail=0`); 1 fail-closed refusal — any unexpected porcelain row (renames, conflicts, missing disk files, byte mismatches, control-char names outside the tolerated set, unpaired untracked) and NOTHING is repaired; 2 could-not-evaluate. Repairs only paths whose disk bytes sha256-match the rev's blob bytes, via `update-index --add --cacheinfo` with the rev's own mode+blob; never touches commits, refs, worktree bytes or remotes; never widens the six-path tolerance. Enumerates with `-uall` (plain porcelain collapses wholly-untracked directories into one `?? dir/` row — r48 Amendment 1) and re-checks the after-state on the plain form the r46 counter reads. Named limit: a receipt written into the repo during a run pollutes the next run's porcelain — stage receipts outside the repo until they land | `census/round-48/records/idx-repair-selftest.txt` (cases=5 pass=5 fail=0); real drift receipts `census/round-48/records/idx-repair-base.txt` (BEFORE 38 rows tolerated=6 → AFTER rows=6 unexpected=0), `-refused-plain-porcelain.txt` (the pre-amendment bytes' fail-closed refusal — the failing arm) | r48 preregistration `census/round-48/preregistration.txt` + `census/round-48/amendment-1.txt` (tool pin fd66d4f1…; the r46 standing counter stays digest-pinned byte-unchanged) | receipt via `--receipt` (stage outside the repo); selftest repos under `TMPDIR` (removed) | souji |
| souji-census-run | probe | `bash tools/souji-census-run.sh --fleet-root DIR --lane souji [--out PATH]` / `--selftest` | exits with the explicit-lane-directory form's code (0 clean/warnings; 1 E-findings; 2 usage/environment) and prints CONF-FORM and DIR-FORM sections plus the final `CENSUS-RUN lane=… conf_rc=… dir_rc=…` line; selftest 0 iff `SELFTEST cases=3 pass=3 fail=0`. Records the conf form's raw rc-2 `souji missing` verdict on this host — disclosed, never masked — beside the working dir-form verdict, with the fleet script's sha256 for provenance; read-only on the fleet root | `census/round-48/records/census-runner-selftest.txt` (cases=3 pass=3 fail=0; arm A1 reproduces the host condition synthetically with the REAL fleet script copied into the fixture); real receipt `census/round-48/records/census-runner-output.txt` (`CENSUS-RUN lane=souji conf_rc=2 dir_rc=0`) | fleet script bytes recorded per-run via the receipt's `# fleet-script sha256=` line (the fleet root is read-only to this lane; the script is never edited) | none (read-only; `--out` writes where the caller points) | souji |

R39-C1-06 — four r38 gate fixtures had no registry row (r38 routed defect R6): `r38-citation-commit`, `r38-drift-write-envelope`, `r38-drift-record` and `r38-drift-mutants` now carry `gate` rows above, beside the five r39 rows this round adds (`c1-counter`, `c2-counter`, `c3-counter`, `r39-citation-rev`, `r39-drift-record-rules`); every one of the nine names a failing arm in its self-test cell, so none is a `probe`.

Sources for this skill: `corpus/SOURCES.md`; admission bar: `corpus/QUALITY.md`.

## Known surfaces (fleet, refreshed r6)

- Fleet root: the 96 pushed-receipt checkpoint artifacts (r3 approval list)
  were REMOVED 2026-10-19 (fleet commit e20f4fa, operator sweep; recovery
  via origin blobs). 15 shell strays were already removed by a1b44b1.
- lore-shokunin: 19 dead worktree registrations PRUNED r3 (list now 1); a
  small `.scratch` (218 KB) flagged by the r6 fleet census.
- game-dev-2d-shokunin: 2 detached registrations pruned r3; 3 named-branch
  registrations PINNED (locks held; each branch has 1 unpushed commit) —
  a 5th worktree appeared by r6 (live lane work; classified by census).
- kotodama-shokunin: `.scratch` measured 553M → 1.9G → 16G → **40.4 GB**
  across r1–r6, live-written by its unpushed round-14..53 work — NOT-SAFE;
  handoff note at `census/round-6/kotodama-scratch-handoff.md`.
- Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`
  (r6; per-repo worktrees/unpushed/dirty/scratch/mtime/flags). r15's
  `b410186` copy did not parse; r16 restored and measured it (config
  semantics below and in the tool header).

## Repository structure census (F2, bounded r13 capability)

Run `bash tools/souji-repo-structure.sh --repo <absolute-repo>` for a
versioned `git repo structure --format=lines` census. Source S035 says the
default table is not intended for machine parsing. S036 suppresses optional
locks, not every possible write; the probe also suppresses lazy fetch,
refuses partial/promisor repositories and reports the common Git directory.
The isolated fixture measures persistent state on this host
(`bash tests/fixtures/r13-repo-structure.sh --selftest`); S037 explains why
raw zero exit does not prove complete accounting.

| Need / observation | Action |
|---|---|
| Reachable-object statistics | Use the probe; retain its version, command and output. |
| Unavailable command or invalid repository | Record could-not-evaluate, never zero bytes. |
| Recoverable disk space or a deletion decision | Structure output is insufficient; apply the per-artifact receipt workflow. |

Checklist: no maintenance/fetch/rewrite; machine-friendly format; record
Git version; preserve actual output; never equate reachable-object disk size
with reclaimable filesystem space. Full scope and failure case:
`corpus/knowledge/git-repo-structure-readonly.md` (S035/S036/S037).

## Retained evidence and protected census paths (round 14)

Before reusing a previous green result, run
`python3 tools/souji-evidence-cache.py --root <lane> --record <record.json>`.
The record declares `name`, boolean `matched`, its own `measured_commit`,
and nonempty `dependencies` mapping contained relative paths to SHA-256.
Capture those digests with the original observation and require identical
before/after bytes; do not manufacture current digests when retaining an old
result. Exit 0 means only declared-byte eligibility. Exit 1 means stale or
failed, and exit 2 means malformed/legacy/refused input; neither reuses green.
An optional repeated `--require <relative-path>` prevents a known minimum
dependency set from silently disappearing. Preserve the original declared
revision: no fallback to a file-level revision or current HEAD.

This does not discover omitted/transitive dependencies, bind external binary
versions or environment, authenticate authors, prove historical execution,
or certify deletion safety. Checks with known external mutable data inputs
run afresh; external runtime variation remains outside declared-file proof.
The actual consumer is `census/round-13/run-verification.py`; historical JSON
is never rewritten. Its entry requires explicit `--round N --output
census/round-N/<new>.json` and exclusively creates that output; a default
invocation refuses with exit 2. The isolated causal demonstration is
`census/round-14/cache-demonstration.py`: actual `attempt_reuse` decisions
on synthetic records only. Full migrated dispatch and positive production
retention were not exercised; source wiring is not that observation (Q23).

The metadata census must refuse roots, ancestors, comparison paths and known
Git/worktree aliases into the credential store before enumeration or content
readers. Do not test this on a real store: use only the isolated fixture
`tests/fixtures/r14-census-boundary.py`. Symlink discovery is metadata outside
the protected tree, not permission to follow its target. Protected-namespace
checks are not a general sandbox against hostile hardlinks, bind mounts or
concurrent replacement. Source S040 explains filesystem-aware resolution;
QUALITY Q20/Q21 and `corpus/lessons/round-14.md` bind these limits.
R14's blanket local-configuration refusal was rejected as harmed by the
outside closure. R15 landed a candidate that did not parse. R16 restored a
parsing census whose config guard is value/effect-aware: a config-named path
overlapping the store still refuses the whole run; unevaluable config
degrades one repository to an `error` row; a bound filter driver skips
status for that repository; hooks, fsmonitor and lazy fetch are neutralized
on every git call. Measured with the r15 config fixture, the r14 namespace
fixture and the selftest (`census/round-16/c1-matrix-final.json`);
residual contractions versus pre-harm: `corpus/lessons/round-16.md`.

## Round 20 repair contract (supersedes broad r19 authority/binding wording)

Round19 was **rejected-harmed**, not admitted
(`corpus/lessons/round-19-verifier-spotcheck.md`). The preceding r19 revision-stamp
pattern proves only its listed inputs, and the five-suffix audit allowance was broader
than the per-item grant. Q39–Q41 and `corpus/lessons/round-20.md` define the repair:

| Need | Required boundary |
|---|---|
| Audit a delivery write | Own report always; any sibling artifact only when that exact per-item filename is requested. A matching stem/extension or an incidental prose mention is not a grant. |
| Audit private scratch | Only an explicit own scratch root, including its actual wave-slot spelling; never broad `/var/tmp` fallback or another seat/slot. |
| Claim a repeatable re-audit | Bind the actual auditor, spec, manifest and consumed transcript bytes; preserve missing inputs and classifier limits. A row is retrospective classification, not authenticated historical misconduct. |
| Stamp working-tree measurements | Name every owned code/helper/wrapper/executed fixture/corpus input actually contributing the record; require matching revision and stable before/after digests before writing. A durable commit alone is insufficient. |
| Reproduce historical counts | Use the full40 durable-ID command index in `corpus/README.md` Round20; read committed inputs, not the current worktree. Old LOG/JSON commands remain historical and receive named append-only replacements. |

Full-ID/durable-ref checks remain; HEAD/branch/short/keep-only guards are not weakened to
make an obsolete command green. Declared input binding does not authenticate author labels,
external binaries/environment, concurrent filesystem behavior or measurement sufficiency.
The repair oracle is fixed before implementation in
`.ufo/waves/round-20/preregistration.txt`; only observed final evidence may grade it.

### F5 list / nominate / reap precision

`bash tools/souji-proc-census.sh` **lists** eligible readable own-uid residue and **nominates**
it for operator review; it never reaps or signals in census mode. Self/descendants
recognized by the bounded parent-chain snapshot are excluded; unreadable/racing data is skipped. Raw argv is read before output redaction, not
guaranteed secret-free; `reason` and `cmd` have separate sanitation. See the exact source/code/
fixture bindings and inference limits appended to
`corpus/knowledge/process-residue-observations.md` (S082, S086–S088, S075/S076), and Q42.
Historical scanner recheck (NOT run or newly authorized in r21): `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh`. R21 rechecks only the proc-free reason mode.
Other-uid residue is outside this tool, not wholesale ownership assigned to Mori.

The specific `souji | round-18` F5 reap and NAMESPACE_SHA256 requests remain **HELD**;
historical58-orphan observations are dated, not current counts. No listing grants killing,
quarantine or deletion. Certification **OFF**, K5 **HELD**.

### Round21 F5 privacy repair — synthetic evidence only

Reason-path output now shares cmd's eight secret-pattern transformations and
160-byte whole-field bound; a selected secret-bearing argv element keeps its
provenance and emits `argv-path-gone:[REDACTED]`. Ordinary short path controls
remain exact. Proc-free replay uses `--reason-only argv` (NUL stdin) or `fd`
(one target); `tests/fixtures/r21-reason-canary.sh` applies27 literal cases,
including old-function red controls. Evidence/source bindings: S100/S101 and
`corpus/knowledge/process-residue-observations.md`; QUALITY Q49.

Raw argv/fd values are still read before printing; unknown/encoded patterns
and historical exposure remain unproved. L1 measurements used no live
process census or private-value probe. A seat's prohibited historical-snapshot
search is disclosed and excluded in the r21 lesson; the round is not
process-scope-clean. Operator/Kagi owns exposure assessment; inherited
reap/NAMESPACE holds, certification OFF and K5 HELD are unchanged.

### Round21 relative-read and replay contracts

Audit targets are resolved from the contract fleet cwd, not guessed from the
lane: V-READ-ROOT (minor) flags visible outside-lane relative read/grep/glob
targets and a complete pathless grep. Truncated targets remain unknown.
V-RECURSIVE and all older violation classes are retained (Q47).

Current acceptance uses the r21 runner, which selects the named durable
commit in a private clone; neither the caller path nor its HEAD is authority.
The r20 runner/receipt is immutable historical evidence, not a current command.
The r21 historical agreement step checks original artifact bytes, not an
upgraded proc tool against an old digest (Q48). Replay outcomes are not a
bit-identical reproducible-build claim (S103).

Replay setup also imports original source `refs/remotes/*` into private
`refs/remotes/souji-source/*`: an unborn-HEAD, remote-ref-only source can
therefore replay its advertised durable commit. It never imports `refs/jj/*`
or creates a durable ref merely from the requested SHA. `source_sample_unchanged`
means sampled HEAD/bare/tracked-status equality, not all source bytes.
The eighteen executed programs and frozen expected summaries remain unchanged.
Round22 strengthens their result predicates: decoded types must match, summary
stderr must be empty, and cache checks/phases must match reviewed identities.
See S104/S105, Q51 and `tests/fixtures/r22-result-oracle.py`. This is bounded
result-contract calibration, not malicious-producer attestation, pass-line
identity, duplicate-key rejection or execution authentication. Historical r21
source/receipts remain available at their recorded revisions; never run current
source while labeling it as the historical implementation.

## Round 43 freeze-check contract

The current `souji-freeze-check` entry keeps its CLI and 0/1/2 map. Beyond the historical r42
class list, it reports ROUND-MALFORMED for a present non-positive-ASCII Round value,
UNATTACHED-KEY after a malformed claim heading, and CONTROL-SYMLINK without reading link text.
Repeated keys are first-wins with one KEY-DUPLICATE per further occurrence; FROZEN-EDITED also
compares the Control and preregistration blobs. `--selftest` includes the r43 cases.
These are the lane's own hygiene-evidence checks, not fleet dispatch authority or deletion
certification. The r43 frozen hidden audit has two oracle defects (lesson M43-1); no passing
whole-claim verdict is inferred from the repaired tool's newtable=9/9 or self-test alone.

## Round 44 defensive output and audit contracts

The drift census now refuses a `--json` final-component symlink with
`JSON-TARGET-SYMLINK` before resolving it, including dangling links. A symlinked
parent still resolves; parent traversal errors retain `JSON-UNWRITABLE`, not
tracebacks. This caller-output restriction is not preservation proof or deletion
authority. The r38 consumer was cut over jointly; the r43 failed target remains
historical. Certification OFF, K5 HELD and NAMESPACE hold are unchanged.

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| leaf-symlink refusal battery | gate | `python3 -B tests/fixtures/r44-drift-symlink-refusal.py --tool tools/souji-worktree-drift.py --work DIR` | 0 clean; 1 failed; 2 could-not-evaluate | entry command constructs isolated fixtures, including positive outputs and parent-error cases | `census/round-44/c3-surface.tsv`; assertions in fixture | explicit scratch DIR only | souji |
| repaired hidden audit | gate | `python3 -B census/round-44/c2-hidden-audit.py --tool tools/souji-freeze-check.py --work DIR` | 0 clean; 1 failed; 2 could-not-evaluate | isolated ten-scenario audit; controls through frozen C2 counter | `census/round-44/c2-scenarios.tsv` | explicit scratch DIR only | souji |

The repaired audit retains repeated finding-class multiplicities and the
post-freeze FROZEN-EDITED expectation (S264; round-44 lesson). Its fixed-case
output is not execution authentication: the wave's size-branching memorizer
survives the counter. C1's new registration counter has incompatible internal
key tuples and cannot establish token-binding success; do not treat its
`corrections=66` display as accepted corrections. See the round-44 lesson and
the frozen red receipts before reusing either instrument.

## Round 45 historical register verifier

`python3 -B census/round-45/c1-counter.py --root LANE --rev FULL40 --scratch EXTERNAL_DIR`
checks the filed R44 register using one `(line, token, class)` identity and derives
referents from its declared historical revision. Exit 0 means the finite 66-key
register agrees; 1 means findings; 2 means unavailable or malformed inputs.
`--register-file` is a caller-owned discrimination fixture, not committed claim evidence.
External fixture: `python3 -B tests/fixtures/r45-register-feasibility.py --root LANE --rev FULL40 --scratch EXTERNAL_DIR`.
Round 46 adds `--selftest` (r46 C2): it builds isolated synthetic git repos under the caller scratch only and asserts the frozen verification semantics — exit codes and the stable finding identifiers (registered/missing/derived_mismatches/junk/fenced/duplicate/retracted) plus the refusal classes — over 11 cases pinned in `census/round-46/records/c2-selftest-expected.tsv`; the default path is proven byte-behavior-identical to the r45 bytes by exact reproduction of the r45 after and wrong-token receipts. The disclosed no-built-in-self-invocation interface debt is closed. The R44 counter and its red verdict are unchanged. Historical factual credit is zero:
this repairs measurement, not the already-accounted facts. It does not authenticate
execution, prove universal correction-language coverage or authorize cleanup.

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r45-register-verifier | gate | `python3 -B census/round-45/c1-counter.py --root LANE --rev FULL40 --scratch EXTERNAL_DIR` | 0 finite register agreement; 1 findings; 2 could-not-evaluate | `python3 -B census/round-45/c1-counter.py --selftest --scratch DIR` (r46 C2: 11 cases over isolated synthetic repos in caller scratch; expected table `census/round-46/records/c2-selftest-expected.tsv`; external r45 fixture retained; default path proven byte-identical by `census/round-46/records/c2-repro-after.txt` and `c2-repro-wrong.txt`) | census/round-45/preregistration.txt; immutable census/round-44/c1-population.tsv digest in code; r46 expected table | committed git blobs read-only; temporary extracted instrument and selftest fixtures in caller scratch | souji |

## Round 48 host-index and census-runner contracts

Two r47-closure carry-in items became committed contracts this round (r48).

Host index drift (calibration surface). Landings made through the index-free
plumbing helper — or integrator commits landed elsewhere and fetched here —
enter HEAD without this host's index gaining the entries, so the worktree
drifts outside the frozen Amendment-1 tolerance and the standing r46
landing-suite counter exits 2 could-not-evaluate at EVERY revision. This
recurred at the r48 pre-flight exactly as the r47 lesson's mistake 1
predicted (the r47 spot-check commit 8e17a4b1; control receipt
`census/round-48/controls/c1-control-donothing.txt`, EXIT=2). The standing
practice is now: after every landing, run
`python -B tools/souji-idx-repair.py --root <lane> --rev <full40>` — it
repairs only paths whose disk bytes sha256-match the rev's blob bytes, via
`git update-index --add --cacheinfo` with the rev's own mode+blob (S271),
fail-closes on anything it cannot prove, and never widens the six-path
control-char tolerance. Plain porcelain collapses a wholly-untracked
directory into one `?? dir/` row; the tool enumerates `-uall` and re-checks
the after-state on the plain form (r48 Amendment 1,
`census/round-48/amendment-1.txt`). Stage its receipts OUTSIDE the repo
until they land — a receipt written into the repo pollutes the next run's
porcelain.

Census conf-name form (operability surface). The round contract's census
command names the conf form, which exits rc 2 `souji missing` on this host
(the conf resolves `souji-shokunin/`; the real checkout here is
`shokunin-repo-hygiene/`). The committed adapter
`bash tools/souji-census-run.sh --fleet-root <fleet> --lane souji` runs the
conf form first and records its raw verdict — the disclosure is the point,
never masked — then runs the documented explicit-lane-directory form against
this checkout and exits with its code, printing the fleet script's sha256
for provenance. The fleet instrument stays read-only to this lane; the
contract-vs-host mismatch is routed to the operator (L0 round-48).

## Round 49 selftest-fixture contract

One r48-closure routed defect became a committed contract this round (r49).

Digest-bound fixture bytes (calibration surface). A fixture written through a
text-mode handle (`open(..., "w")`) lets the platform choose the bytes: on
this Windows host every `\n` becomes CRLF, so a literal LF digest
(`SHA_C/SHA_P/SHA_P1` in `tools/souji-freeze-check.py`) can never match and
the r42 registry gate `r42-freeze-check-selftest` had no obtainable green
here (raw red receipt `census/round-49/controls/
freeze-selftest-base-red.txt`, cases=41 pass=4 fail=37; grounded on S272 —
text mode translates `\n` to `os.linesep` on writing, binary mode does not
translate). The standing rules are now: (1) digest-bound fixture bytes are
written binary (`open(..., "wb")` + explicit UTF-8 encode) — fixed in
`tools/souji-freeze-check.py` r49, verdict code byte-identical (diff receipt
`census/round-49/records/tool-diff-base-to-fix.txt`); (2) a counter that
stands over such an instrument writes no digest-bound fixtures itself and
launches children with `sys.executable`, never the `python3` name (this host
has none — the r42 counter's own named limit here); (3) a receipt destined
for a grammar-parsing field is written in that grammar and the freeze-check
verdict is run against a freeze commit BEFORE building on it (the r49
attempt-1 CONTROL-NOT-RED catch; superseded by attempt 2 before any
after-data); (4) receipts embed an instrument's exit code only as
`cmd > file; rc=$?` — never after a pipe. Frozen census counters that carry
the text-mode class (r41 c3, r42 c2, r43 c2/c3) are named limits: their bytes
are pinned, they are never edited, and their green verdicts were produced on
the old Linux host, not here.

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r49 freeze-selftest fixture gate | gate | `python -B census/round-49/c1-counter.py --root LANE --rev FULL40 --scratch DIR` | 0 `SUMMARY selftest=ok patches=3/3 real=ok retro=red retro_clean=ok tool_sha=<12hex>`; 1 target unmet (at the pre-r49 base this is the expected red: `selftest=FAIL (41, 4, 37)`); 2 could-not-evaluate | the counter's patches leg is the self-test of record: P1 reversed digests, P2 empty `--diff-filter=A`, P3 failing `merge-base` must each flip the tool's selftest to non-zero (3/3) | `census/round-49/c1-arms.tsv` (leg -> expected verdict at tip/base); counter digest in `census/round-49/preregistration-r2.txt` | explicit scratch DIR only (tool extracted there; TMPDIR under it) | souji |

## Round 50 contracts

Two r49-closure routed items became committed instruments this round (r50).

Token readings name their scope (calibration surface). A page-token reading
in any receipt or record names both scopes and how they are counted:
`tools/souji-page-token-count.py` counts a case-insensitive token prefix at
RAW-BYTES scope (case-insensitive byte-prefix count over the exact response
bytes) and at CONTENT scope (HTML text content via `html.parser` with
character references decoded per S273; script/style/header/nav/footer
elements and elements whose class list contains `footer` are excluded —
site chrome), and every record carries the METHOD line stating exactly
that. A content-scope zero and a raw-scope nonzero are different facts and
can never again be stated as one number (the r49 S267 receipt's "zero
occurrences of 'histor*'" was the content fact only; the erratum line
`S267-COUNT-ERRATUM` in `corpus/lessons/round-50.md` records it
append-only). A quote-count command strips tags display-faithfully (empty
replacement, never a space) — a space substitution turns a verbatim
displayed quote into a non-substring (r50 mistake 1, fourth occurrence of
the quote-counting class).

Census receipts are digest-bound and verifiable (operability surface). The
contract's census before→after receipts are captured through
`tools/souji-census-receipt.py capture` into a v1 receipt: header keys
(LANE, FLEET-ROOT, FLEET-SCRIPT-SHA256, ADAPTER-SHA256, CONF-RC, DIR-RC,
DIR-RESULT, DIR-WARN-W04, ADAPTER-EXIT), a RECEIPT-SHA256 line digesting
every byte above it, and the adapter's raw output embedded verbatim.
`verify` re-derives every header value from the embedded raw output and
re-hashes both scripts; each refusal names its class (RECEIPT-MALFORMED,
RECEIPT-DIGEST-MISMATCH, RECEIPT-RC-INCONSISTENT, RECEIPT-COUNT-MISMATCH,
RECEIPT-SCRIPT-DRIFT, RECEIPT-ADAPTER-DRIFT). Receipts are staged outside
the repo (the tool refuses an `--out` at/inside the lane root) and copied
in before a commit (the r48 receipt-staging discipline, now enforced by the
tool). The conf form's raw rc-2 verdict stays inside every receipt —
disclosed, never masked.

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| souji-page-token-count | evidence | `python -B tools/souji-page-token-count.py --url URL --token STR [--out PATH] [--timeout N]` / `--capture FILE --token STR` | 0 record emitted (`# page-token-count v1` header; SOURCE-MODE; URL/FINAL-URL/HTTP-STATUS or CAPTURE-PATH; BYTES; SHA256; TOKEN; SCOPE-RAW-MATCHES; SCOPE-CONTENT-MATCHES; METHOD; PAGE-TOKEN-COUNT-EXIT=0); 2 could-not-evaluate (exactly one of --url/--capture, --token required, fetch/HTTP failure, capture missing, selftest environment refusal) | `TMPDIR=<scratch> python -B tools/souji-page-token-count.py --selftest` → `SELFTEST cases=8 pass=8 fail=0` (fixtures: body-text, footer-class-only, script-only, absent, case-insensitive, charref-decoded, footer-tag-only, content-resumes-after-footer; the footer arms are the anti-always-zero discriminators) | `census/round-50/sources/s267-reopen-count-receipt.txt` (content histor=0 / raw histor=1 / factual 0-0 over the committed capture `s267-stdtypes-capture.html`, sha256 0a9474e3…f5d3); S273 capture + located quote beside it | stdout + caller-named `--out` only; the page is held in memory; selftest fixtures under TMPDIR (refused unset/empty or at/inside the lane root), removed | souji |
| souji-census-receipt | evidence | `python -B tools/souji-census-receipt.py capture --fleet-root DIR --lane souji --out PATH` / `verify --receipt PATH [--fleet-root DIR]` | capture: 0 receipt written with the census dir form exit 0 (else the census's code; 2 environment/grammar); verify: 0 `VERIFY ok …` listing every check (grammar,digest,raw-section,rc,w04,result,adapter-sha,fleet-script-sha), 1 a named refusal (RECEIPT-MALFORMED / RECEIPT-DIGEST-MISMATCH / RECEIPT-RC-INCONSISTENT / RECEIPT-COUNT-MISMATCH / RECEIPT-SCRIPT-DRIFT / RECEIPT-ADAPTER-DRIFT), 2 could-not-evaluate | `TMPDIR=<scratch> python -B tools/souji-census-receipt.py --selftest` → `SELFTEST cases=6 pass=6 fail=0` (capture+verify over a synthetic adapter; five tamper/malform arms each asserting its exact refusal class) | `census/round-50/records/census-before-receipt.txt` (FLEET-SCRIPT-SHA256 3fb72615…4e30, ADAPTER-SHA256 a159f2db…f74b, CONF-RC=2, DIR-RC=0, DIR-RESULT=ok, DIR-WARN-W04=59; verified ok over all checks) | runs the r48 adapter read-only; the only write is the caller-named `--out`, refused at/inside the lane root (receipt-staging discipline enforced) | souji |

## Round 51 contracts

Workspace-census captures are point-in-time facts (coverage surface). The
session-workspace census (the r46 method, re-run r51) commits its capture as
the frozen state: a census row records what existed at capture time, never a
live guarantee (the live workspace grew 86 -> 89 foreign scratch dirs between
two r51 takes of the same round). A drift receipt against an earlier capture
derives every COUNT line and its ADDED/REMOVED key rows from the two
COMMITTED captures — never from a re-run — and its key derivation excludes
table header rows on both sides (a two-sided derivation that filters a header
on one side only reads the format artifact as workspace drift — r51 mistake
1). The pushed receipt inside the census compares HEAD with the LOCAL
refs/remotes/origin/master (offline metadata) and names its copied-history
limit (S274: a rebased/cherry-picked/am'd-then-pushed lane reads unpushed to
the sha comparison; git-cherry(1) resolves it) — the limit is disclosed even
in rounds where no lane row is in that state. The census scope is
r46-comparable non-hidden top-level entries, disclosed in the method note;
every named candidate gets a per-artifact receipt (souji-verify.sh,
advisory, certification OFF) and nothing is moved, deleted, or proposed for
removal without operator approval.

Record corrections to prior rounds' artifacts are append-only with the
untouched bytes proven (calibration surface). When a closure routes a defect
in a prior round's lesson or receipt, the fix is an appended correction line
naming the defect (the R51-CORRECTION shape) or an appended receipt field
with a provenance note — and the frozen counter of the round that lands it
proves the original bytes unchanged (byte-occurrence counts at both the base
and the tip revs; an in-place edit fails). A missing receipt field is added
beside a note naming the sibling receipt that carries it; the listing the
numbers were counted from is never rewritten.

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r51 routed-corrections gate | gate | `python -B census/round-51/c1-counter.py --root LANE --rev FULL40 --base-rev d1b8734d835171c7329225fdaab249c5c6799de8 --scratch DIR` | 0 `SUMMARY corr=ok dup=ok ntfs=ok listing=ok corr_lines=1 dup_base=2 dup_tip=2`; 1 target unmet (at the pre-r51 base this is the expected red: corr/ntfs FAIL); 2 could-not-evaluate | the committed do-nothing control is the discrimination of record (red at the base, EXIT=1); pre-freeze synthetic feasibility red/green receipts under census/round-51/records/ | census/round-51/c1-arms.tsv; counter digest in census/round-51/preregistration.txt | explicit scratch DIR only (diagnostics; nothing written inside the repo) | souji |
| r51 workspace-census gate | gate | `python -B census/round-51/c2-counter.py --root LANE --rev FULL40 --base-rev d1b8734d835171c7329225fdaab249c5c6799de8 --scratch DIR` | 0 `SUMMARY shape=ok drift=ok receipts=ok limit=ok rows=126 added=79 removed=2`; 1 target unmet (PRISTINE FAIL WORKSPACE-CENSUS-ABSENT at the pre-r51 base — the expected red); 2 could-not-evaluate | the committed do-nothing control is the discrimination of record (red at the base, EXIT=1); pre-freeze synthetic feasibility red/green receipts under census/round-51/records/ (three counter defects caught and fixed there, mined in the r51 lesson) | census/round-51/c2-arms.tsv; counter digest in census/round-51/preregistration.txt | explicit scratch DIR only (diagnostics; nothing written inside the repo) | souji |

## Round 52 contracts

The fleet-root census (r52 C2) is read-only and dry-run. It lists the top-level entries of the fleet root with kind (lstat), tracked (first component of `git ls-files --cached`), ignored (`git check-ignore --no-index` on each top-level name — never a listing, which would walk operator-protected subtrees such as `.ufo/state/`), class and report-only disposition. Every git call carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null` and the frozen GIT_* environment; a repository config carrying include/includeIf or core.worktree refuses the run; a credential-shaped top-level name refuses the run (no redaction; operator ruling pending); a root inside ~/.omp, ~/.ssh, ~/.gnupg, ~/.aws, ~/.kube, ~/.docker or ~/.config/gh refuses; --out inside the root refuses. The capture is written outside the root and copied in byte-exact (census/round-52/records/fleet-root-census-run.txt).

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r52 fleet-root census | tool | `python3 -B tools/souji-fleet-root-census.py --fleet-root <ROOT> --out <PATH outside ROOT>` | 0 `CENSUS ENTRIES=n tracked=n ignored=n untracked-stray=n symlink=n out=<PATH>`; 2 refused (nothing written: symlink/non-dir/not-own-toplevel, credential namespace or name, include/worktree config, in-root --out, tab/newline name, git failure) | `python3 -B tools/souji-fleet-root-census.py --selftest` (census/round-52/records/tool-selftest.txt: checks=39 failures=0) | tools/souji-fleet-root-census.py (TOOL_SHA256 in every capture); census/round-52/preregistration.txt (format and class rule) | --out only, O_EXCL, outside the fleet root; nothing removed or moved | souji |
| r52 C1 gate | gate | `python3 -B census/round-52/c1-counter.py --root LANE --rev FULL40 --scratch DIR` | 0 `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0` (both enumerated annotations filed by R52-CORRECTION lines); 1 unfiled mismatch (base: `unfiled=2`, the expected red); 2 could-not-evaluate | the committed do-nothing control census/round-52/controls/c1-control-donothing.txt (red, EXIT=1) | census/round-52/c1-counter.py sha256 f5cd614c006dfd4d02f5575bde0d4bf22183daa7759114187b2c6789b90ef24d (pinned in census/round-52/preregistration.txt) | explicit scratch DIR only | souji |
| r52 C2 gate | gate | `python3 -B census/round-52/c2-counter.py --root LANE --rev FULL40 --scratch DIR` | 0 `SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok`; 1 any failing check or PRISTINE FAIL FLEET-CENSUS-ABSENT (the base); 2 could-not-evaluate | the committed do-nothing control census/round-52/controls/c2-control-donothing.txt (red, EXIT=1) | census/round-52/c2-counter.py sha256 863a551dcbbc2896ca7752362615d19c6be0112e56c8714b1e01df3d4a1c0444 (pinned in census/round-52/preregistration.txt) | explicit scratch DIR only | souji |

## Round 53 contracts

Both r52 counters are amended as NEW frozen versions (the r52 bytes are never edited and
stay the standing do-nothing control arm). Fixtures are built by
census/round-53/fixtures/build-fixtures.py (deterministic file bytes; commit ids are
wall-clock dependent — named limit R10); expected verdicts are committed in
census/round-53/records/c1-selftest-expected.tsv and c2-selftest-expected.tsv.

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r53 C1 gate (annotation counter v2) | gate | `python3 -B census/round-53/c1-counter.py --root LANE --rev FULL40 --base 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --scratch DIR` | 0 `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0`; 1 any finding (MULTIPLE-ANNOTATIONS, RECORD-SHA-MISMATCH, INERT-CORRECTION, CORRECTION-IN-FENCE, DELETED-LINES) or unfiled mismatch; 2 could-not-evaluate | `python3 -B census/round-53/c1-counter.py --selftest --work DIR` (census/round-53/records/c1-selftest.txt: SELFTEST pass cases=6); do-nothing control census/round-53/controls/c1-control-donothing.txt (red: C1V2-COUNTER-ABSENT) | census/round-53/c1-counter.py sha256 a7928d05df794f14d5d0213ddb78d042f62819b52f5c49b3c838a1b96da1ed15; record pin 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 (census/round-53/preregistration.txt) | explicit scratch DIR only (--work for the selftest) | souji |
| r53 C2 gate (capture counter v2) | gate | `python3 -B census/round-53/c2-counter.py --root LANE --rev FULL40 --capture census/round-53/records/fleet-root-census.tsv --receipt census/round-53/records/fleet-root-census-run.txt --scratch DIR` | 0 `SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok`; 1 any finding (ROWS-UNSORTED, COMMENT-AMBIGUOUS-NAME, CAPTURE-RECEIPT-MISMATCH, RECEIPT-MALFORMED) or PRISTINE FAIL FLEET-CENSUS-ABSENT; 2 could-not-evaluate | `python3 -B census/round-53/c2-counter.py --selftest --work DIR` (census/round-53/records/c2-selftest.txt: SELFTEST pass cases=4); do-nothing control census/round-53/controls/c2-control-donothing.txt (red: FLEET-CENSUS-ABSENT) | census/round-53/c2-counter.py sha256 6515b97553dd6f6d207d638de2520c4367a56a1a37ff7329b9d914c329a349b7; capture census/round-53/records/fleet-root-census.tsv sha256 922112361cdd257451e2f62820815ce19493c7d94d06c73c1b40f5dc9756f904 (census/round-53/preregistration.txt + the run receipt) | explicit scratch DIR only (--work for the selftest) | souji |

Named limits of the frozen v2 bytes (routed to r54, consolidated in
corpus/lessons/round-53.md): R1 fence grammar backtick-only; R2 zone-edge truncation; R3
correction `recomputed=` never validated; R4 `#`-shape no-whitespace-only; R5 receipt
extra keys / CRLF unnamed; R6 tool pin absent; R7 fixture coverage (receipt-ENTRIES +
symlink branches); R8 builder hardening; R9 oracle pinning; R10 fixture rev
determinism; R11 receipt binds bytes not path; R12 exit-code ambiguity; R13 wording
drifts.

## Round 54 contracts

Both r53 counters are amended as NEW frozen versions (the r53 bytes are never edited and stay
the standing v2 acceptance-control arm). Fixtures are built by
census/round-54/fixtures/build-fixtures.py with pinned GIT_AUTHOR_DATE/GIT_COMMITTER_DATE
(fixture revs reproduce across builds; verified by two builds). The selftests verify the
builder and expected-TSV sha256 pins BEFORE exec (`--builder-sha256`, `--expected-sha256`).
Expected verdicts: census/round-54/records/c1-selftest-expected.tsv (13 rows) and
c2-selftest-expected.tsv (10 rows).

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r54 C1 gate (annotation counter v3) | gate | `python3 -B census/round-54/c1-counter.py --root LANE --rev FULL40 --base fe12daad2549f534650d406ebdbac9113d59313f --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR` | 0 `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0`; 1 any finding (MULTIPLE-ANNOTATIONS, RECORD-SHA-MISMATCH, INERT-CORRECTION, CORRECTION-IN-FENCE, DELETED-LINES, ZONE-TOKEN-STRADDLES-EDGE, BOGUS-RECOMPUTED, UNFILED-SOURCES-ANNOTATION, SOURCES-RECOMPUTE-MISMATCH) or unfiled mismatch; 2 could-not-evaluate (incl. a flagged pair filing without --sources-rev-before/after) | `python3 -B census/round-54/c1-counter.py --selftest --work DIR --builder-sha256 ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba --expected-sha256 4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7` (census/round-54/records/c1-selftest.txt: SELFTEST pass cases=13); do-nothing control census/round-54/controls/c1-control-donothing.txt (red: C1V3-COUNTER-ABSENT at base) | census/round-54/c1-counter.py sha256 f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e; census/round-54/records/c1-selftest-expected.tsv sha256 4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7 | scratch DIR only; reads committed bytes | souji |
| r54 C2 gate (capture counter v3) | gate | `python3 -B census/round-54/c2-counter.py --root LANE --rev FULL40 --capture census/round-54/records/fleet-root-census.tsv --receipt census/round-54/records/fleet-root-census-run.txt --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b --scratch DIR` | 0 `SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok`; 1 any finding (ROWS-UNSORTED, COMMENT-AMBIGUOUS-NAME, CAPTURE-RECEIPT-MISMATCH, RECEIPT-MALFORMED, RECEIPT-UNKNOWN-KEY, CAPTURE-CRLF, RECEIPT-CRLF, TOOL-SHA-ARG-MISMATCH) or PRISTINE FAIL FLEET-CENSUS-ABSENT; 2 could-not-evaluate (incl. a malformed --tool-sha256) | `python3 -B census/round-54/c2-counter.py --selftest --work DIR --builder-sha256 ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba --expected-sha256 e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d` (census/round-54/records/c2-selftest.txt: SELFTEST pass cases=10); do-nothing control census/round-54/controls/c2-control-donothing.txt (red: C2V3-COUNTER-ABSENT at base) | census/round-54/c2-counter.py sha256 84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09; census/round-54/records/c2-selftest-expected.tsv sha256 e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d | scratch DIR only; reads committed bytes | souji |

Named limits of the frozen v3 bytes (routed to r55, consolidated in corpus/lessons/round-54.md):
R1 hidden-correction swallow behind a wrapper or with leading spaces; R2 dual-anchor aliasing;
R3 pair-filing stale drop; R4 rows-word dodge in the pair scan; R5 fence over-hide against
CommonMark 0.31.2; R6 pair scan does not hide-fenced lines; NL-1 to NL-5 (capture `#` rows
with four tabs, prose comments with five, uppercase-only unknown keys, whitespace-variant
keys, pin shapes); M2, M7, M11 coverage gaps (fixtures F8b, F12c and selftest arm FA9 named).
The `--tool-sha256` branch is demonstrated on the real lane, not in the selftest (ERRATUM-R54-1).
The C1 gate is defeatable by exotic line separators (sentinel01 S1, HIGH: two form-feed lines above a `~~~` fence turn the committed F7 shape into exit 0; reproduction `census/round-54/records/s1-formfeed-reproduction.txt`); the pair scan is ASCII-only (S2) and the pointer exemption is path-unscoped (connector01 PTR). Counter v4 is the first r55 item (L0 pending on C1's admission).

## Round 55 contracts

The r54 counters are amended as NEW frozen versions (the r54 bytes are never edited and
stay the standing v3 acceptance-control arm). Fixtures come from
census/round-55/fixtures/build-fixtures.py (pinned GIT_AUTHOR_DATE/GIT_COMMITTER_DATE; the
selftests verify builder and expected-TSV sha256 pins BEFORE exec). Expected verdicts:
census/round-55/records/c1-selftest-expected.tsv (27 rows) and c2-selftest-expected.tsv
(15 rows, including the two selftest-only pin arms FA9-WRONG-TOOL-PIN and FB4-PIN-SHAPE).

| name | kind | entry command | verdict map | self-test | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r55 C1 gate (annotation counter v4) | gate | `python3 -B census/round-55/c1-counter.py --root LANE --rev FULL40 --base f056aaa031bb65de27e7fa5daa38b0d4a443aedc --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR` | 0 every check holds (`unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0`); 1 any finding; 2 could-not-evaluate (bad CLI, missing file, zero or duplicate anchor line, no annotation in the zone, a flagged filing without pinned source revs) | `python3 -B census/round-55/c1-counter.py --selftest --work DIR --builder-sha256 e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62 --expected-sha256 ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e` → `SELFTEST pass cases=27`, exit 0 | census/round-55/preregistration.txt; `census/round-55/records/c1-selftest-expected.tsv` sha256 ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e | committed git blobs read-only; selftest fixtures under --work (--scratch is an alias) | souji |
| r55 C2 gate (capture counter v4) | gate | `python3 -B census/round-55/c2-counter.py --root LANE --rev FULL40 --capture census/round-55/records/fleet-root-census.tsv --receipt census/round-55/records/fleet-root-census-run.txt --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b --scratch DIR` | 0 `receipt=ok sorted=ok tool_pin=ok` with no finding; 1 any finding; 2 could-not-evaluate (bad CLI, bad revision, tool absent at rev, `--tool-sha256` not lowercase 64-hex: `TOOL-SHA-ARG-MALFORMED`) | `python3 -B census/round-55/c2-counter.py --selftest --work DIR --builder-sha256 e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62 --expected-sha256 63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc` → `SELFTEST pass cases=15`, exit 0 | census/round-55/preregistration.txt; `census/round-55/records/c2-selftest-expected.tsv` sha256 63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc | committed git blobs read-only; selftest fixtures under --work | souji |

The v4 counters amend the r54 surfaces named in corpus/lessons/round-54.md ("Named limits
carried into r55"): S1 (one LF line model for every line count in the C1 filing counter),
R1 (prefix-tolerant correction lexing), R2 (every anchor occurrence on a site line is judged),
R3 (PAIR-FILING-INERT), R4/S2 (pair annotation with or without `rows`, with `->` or `→`), R5
(CommonMark 0.31.2 fence start conditions: at most three spaces of indent, no backtick in a
backtick fence's info string), R6 (pair scan hides fenced lines), the connector PTR narrowing
(a dot before the colon and a digit after; a ratio such as `2.5:1` still exempts a line, ERRATUM-R55-2),
M2/M7/N5 committed fixtures, NL-1 (any tab-bearing `#` capture line is refused), NL-3/NL-4 (receipt
keys tolerant of case and whitespace; the first-character class is narrower than v3's, a no-harm
failure reported as RD-A, corpus/lessons/round-55.md), NL-5 (named TOOL-SHA-ARG-MALFORMED), M11
(selftest pin arm FA9), and the FA8 unnamed-kill-row defect (the class mismatch is named
CLASS-MISMATCH). Named limits of the frozen v4 bytes are in census/round-55/preregistration.txt
"Named limits carried into v4" and in corpus/lessons/round-55.md "Wave findings" (routed list for r56,
including the pair-filing-in-fence false pass N1, the highest-severity limit). Certification stays OFF.

## Round 56 contracts

The round-56 frozen counters are the current instruments; the round-55 counters stay as the
before arms and their bytes are unchanged. Frozen predicate and pins: census/round-56/preregistration.txt
(freeze cce21b555a617cadda782613ec1e9d3a0c12ac83).

| gate | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r56 C1 correction-filing counter (v5) | gate | `python3 -B census/round-56/c1-counter.py --root LANE --rev FULL40 --base fafe371694fea41c5d23f63083865d5ccf3f1d36 --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR` | 0 every check holds (`unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0`); 1 any finding (named); 2 could-not-evaluate | `python3 -B census/round-56/c1-counter.py --selftest --work DIR --builder-sha256 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a --expected-sha256 48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb` → `SELFTEST pass cases=33` | census/round-56/records/c1-selftest-expected.tsv (pinned) | read-only git blobs at the revision; scratch under --work | souji |
| r56 C2 capture counter (v5) | gate | `python3 -B census/round-56/c2-counter.py --root LANE --rev FULL40 --capture census/round-55/records/fleet-root-census.tsv --receipt census/round-55/records/fleet-root-census-run.txt --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b --scratch DIR` | 0 `receipt=ok sorted=ok tool_pin=ok`; 1 any finding (named, e.g. RECEIPT-UNKNOWN-KEY, TOOL-SHA-ARG-MISMATCH); 2 could-not-evaluate (bad CLI or `--tool-sha256` not lowercase 64-hex) | `python3 -B census/round-56/c2-counter.py --selftest --work DIR --builder-sha256 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a --expected-sha256 90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3` → `SELFTEST pass cases=18` | census/round-56/records/c2-selftest-expected.tsv (pinned) | read-only git blobs at the revision; scratch under --work | souji |
| r56 matrix runner | evidence | `bash census/round-56/fixtures/run-matrix.sh <scratch> <outdir>` after `python3 -B census/round-56/fixtures/build-fixtures.py --work <scratch>/selftest` | writes four TSVs; each row carries exit and first finding | — | census/round-56/records/matrix-dryrun/ (pre-freeze), c1/c2-matrix-v{4,5}.tsv (post-freeze, byte-identical) | scratch only | souji |
| r57 C1 correction-filing counter (v6) | gate | `python3 -B census/round-57/c1-counter.py --root LANE --rev FULL40 --base b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR` | 0 every check holds (`unfiled=0 … fenced=0`); 1 any finding (CORRECTION-IN-FENCE with `hidden_by=fence|block|inline`, PAIR-FILING-HIDDEN, …); 2 could-not-evaluate (bad CLI/revision/record pin, no annotation in zone) | `python3 -B census/round-57/c1-counter.py --selftest --work DIR --builder-sha256 2b8b657b8d86541d4a6f38345cd8d67f1a520603a7cda08f0a5bc3038924633b --expected-sha256 538d902e2f65ddc26bc0c532f4f7de67f89c08020f69151563a982d923d8e105` → `SELFTEST pass cases=36` asserting the FULL ordered finding list | `census/round-57/records/c1-selftest-expected.tsv`, `census/round-57/preregistration.txt` | read-only git blobs; caller scratch | souji |
| r57 receipt revision-binding gate | gate | `python3 -B census/round-57/c2-counter.py --root LANE --manifest PATH` | 0 every receipt binds a durable full40 `rev=`, an `EXIT=` and a matching `instrument_sha256=`; 1 any named finding (RECEIPT-REV-MISSING/SHORT/NOT-FULL40/ABSENT/KEEP-ONLY, RECEIPT-EXIT-MISSING, RECEIPT-INSTRUMENT-PIN-MISSING/DIGEST-MISMATCH/NAME-MISMATCH, RECEIPT-SYMLINK, RECEIPT-MISSING); 2 could-not-evaluate (bad CLI, unreadable/3-column manifest, non-directory root) | `TMPDIR=DIR python3 -B census/round-57/c2-counter.py --selftest --work DIR` → `SELFTEST pass cases=8`, `control=FALSE-GREEN-REJECTED` | `census/round-57/records/c2-selftest-expected.tsv`, `census/round-57/preregistration.txt` | read-only git plumbing; isolated selftest in caller scratch | souji |
| r57 receipt recorder | evidence | `bash census/round-57/record-receipt.sh LANE FULL40 INSTRUMENT OUT -- <cmd...>` | 0/1 = the recorded command's rc; 2 = refused (non-full40 rev, instrument absent at that rev) | — (the recorder refuses; its refusals are exercised by the revenger and sentinel seats) | writes `OUT` only; instrument digest read from committed bytes | caller scratch/OUT | souji |
| r57 matrix runner | evidence | `bash census/round-57/fixtures/run-matrix.sh <scratch> <outdir>` after `python3 -B census/round-57/fixtures/build-fixtures.py --work <scratch>/selftest --manifest <scratch>/selftest/fixture-manifest.tsv` | writes two TSVs (v5 arm, v6 arm); each row carries exit, first finding, full finding list, SUMMARY | — | `census/round-57/records/matrix-dryrun/` (pre-freeze), `census/round-57/records/c1-matrix-v{5,6}.tsv` (post-freeze, byte-identical) | scratch only | souji |

## Round 58 current receipt interface

Use `census/round-58/c2-gate.py` for new receipt checks. The r57 receipt-gate row above is historical replay only; its frozen bytes remain evidence of the raw-tag/confinement defects, not the current interface. The r57 recorder is unchanged and still has dirty-tree/overwrite debt; do not infer that this gate authenticates execution. C1's r58 record correction does not repair the rejected Markdown visibility instruments.

| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r58 receipt interface | gate | `python3 -B census/round-58/c2-gate.py --root LANE --manifest PATH` | 0 clean declared binding; 1 failed named finding, including RECEIPT-PATH-UNCONFINED, RECEIPT-REV-ABSENT for raw tag OIDs, RECEIPT-REV-CONFLICT for distinct standalone headers; 2 could-not-evaluate usage/manifest/expected-table errors | `python3 -B census/round-58/c2-gate.py --selftest --work DIR` | `census/round-58/c2-selftest-expected.tsv`; independent frozen oracle `census/round-58/c2-acceptance.py`; predicate `census/round-58/preregistration.txt` | receipt/repository reads; unique owned selftest child under caller work, removed in finally | souji |
| r58 assessment comparison | gate | `python3 -B census/round-59/assessment-gate.py --root LANE --rev FULL40` (r59 current successor; stable registry identity R58-KIND) | 0 two exact correction-note substrings present with committed matrix-derived values; 1 ASSESSMENT-MISMATCH; 2 CANNOT-EVALUATE or CLI usage | `python3 -B census/round-59/assessment-gate.py --selftest --work DIR` | `census/round-59/assessment-selftest-expected.tsv`; predecessor `census/round-58/c1-counter.py` retained unchanged for historical replay only | normal mode read-only Git blobs; selftest unique owned child under caller DIR, then removed; requires lane history at pinned base | souji |

Receipt boundary: path checks precede content read for the three static escape classes; they are pathname-based, not atomic descriptor confinement. Stable receipt FIFOs/nonregular files refuse before reading; manifest intake and regular receipt reads remain unbounded legacy hazards. A standalone full revision header takes precedence over SUMMARY body tokens; identical duplicate headers are allowed, differing ones refused. Without standalone headers the legacy token grammar remains. Selftest compares rc and full finding strings after documented scratch-prefix/hash normalization, not exact hash bytes. No deletion certification or privacy guarantee follows.

## Round 59 assessment registration correction

The `r58 assessment comparison` row retains its stable R58-KIND identity: its kind is corrected from evidence to gate and its command now selects the r59 self-invoking successor. No shadow `r59 assessment comparison` row is added. This corrects one named self-description mismatch; it does not certify the full registry.

Normal derivation remains the predecessor's exact note-presence predicate, with ASSESSMENT-MISMATCH on failure and a structured could-not-evaluate exit 2 on input errors. Limits remain: substring matches include fences/archived sections; zip truncates unequal matrix lengths; the exit column is positional. No Markdown visibility, row-cardinality, contradiction detection or execution authenticity follows. Selftest asserts rc, ordered finding ids, summary fields and exact case set for five persisted cases; its built-in always-clean comparison is a table-level meta-check, not an executed mutant.

| name | kind | entry command | verdict map | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r59 registry-kind calibration | gate | `python3 -B census/round-59/c1-counter.py --root LANE --rev FULL40` | 0 selected row kind gate; 1 REGISTRY-KIND-MISMATCH (legacy unstructured Git errors also exit 1); 2 REGISTRY-ROW-SHAPE or CLI usage | `python3 -B census/round-59/c1-counter.py --selftest --work DIR` | census/round-59/population.tsv and preregistration.txt; controls.py literal rc/finding expectations | normal read-only Git blobs; selftest unique owned caller-work child; requires lane path and pinned base | souji |

The frozen calibration counter is raw-line, classification-only and prefers a shadow r59 prefix if present; it does not validate Markdown visibility, instrument existence or selftest support. Thus its count alone never proves the round's kill-rule conjunction. The actual stable r58 row, committed gate and public selftest require separate substance checks. Known frozen limits and the Q99 missing Round-header defect are retained in corpus/lessons/round-59.md; certification OFF.

## Round 60 — freeze-record substance binding and atomic receipt writing

The `tools/souji-freeze-check.py` row above is the base grammar; the r60 change is an **opt-in**
`--substance` arm on the same tool. Without the flag its stdout, stderr and exit are byte-identical to
the base bytes at `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4` (`census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt`
reproduces this over the selftest and three real preregistrations). The r57 recorder
(`census/round-57/record-receipt.sh`) stays as filed for historical replay; `tools/souji-receipt-write.py`
supersedes it for new receipts, and the r57 dirty-tree/overwrite/atomicity debt is what it closes — its
own selftest and the r60 fixture are the only authority for that, not this prose.

| name | kind | entry command | verdict map | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r60 freeze-record substance arm | gate | `python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40 --substance` | 0 every claim's control receipt is bound; 1 CONTROL-INSTRUMENT-MISSING/MISMATCH/DUPLICATE, CONTROL-REV-MISSING/INVALID/NOT-BEFORE-FREEZE/DUPLICATE, CONTROL-COMMAND-MISSING/MISMATCH/DUPLICATE; 2 could-not-evaluate (base classes unchanged) | `python3 -B tools/souji-freeze-check.py --selftest --substance` → `cases=12 pass=12`; default `--selftest` stays `cases=41 pass=41` | `census/round-60/preregistration.txt`; matrix `census/round-60/c1-matrix.tsv` + `census/round-60/matrix/`; counter `census/round-60/c1-counter.py` | read-only git object store; selftest scratch under `$TMPDIR` | souji |
| r60 atomic receipt writer | gate | `python3 -B tools/souji-receipt-write.py --root LANE --rev FULL40 --instrument PATH --out FILE [--max-bytes N] [--allow-dirty] [--allow-outside] (--command CMD \| -- ARGV...)` | exit = wrapped command's rc; 2 refuses: non-full-40 or non-commit rev, instrument absent/symlink/non-regular at rev, worktree differing from the committed blob, existing or racing `out`, dirty worktree without `--allow-dirty`, capture over `--max-bytes`, out directory resolving outside `--root` without `--allow-outside`, missing out directory | `python3 -B tools/souji-receipt-write.py --selftest --work DIR` → `cases=12 pass=12`; fixture `python3 -B tests/fixtures/r60-receipt-write.py --tool tools/souji-receipt-write.py --work DIR` → `pass=8 fail=0` | `census/round-60/c2-cases.tsv`; receipts `census/round-60/records/c{1,2}-after.txt`, controls `census/round-60/controls/` | writes only `out` and its temp sibling; reads the lane read-only | souji |

Binding semantics and their limits are in `corpus/knowledge/freeze-record-substance-binding.md`: the arm
binds bytes, a graph relation and an argv token — never execution, never wall-clock chronology, and a
truthful forgery still passes. The writer's dirty-tree guard is `git status --porcelain`, so an ignored
file does not make the tree dirty and a file modified *during* the run is not caught (named limits,
`corpus/lessons/round-60.md`). The C1 matrix pins each case's expected verdict but not its finding class,
and `forgery-rev-at-freeze` names the freeze commit through a tag because a receipt inside that commit
cannot name it. Certification OFF, K5 HELD.

## Round 61 — control-chronology binding by content

The `--substance` arm of `tools/souji-freeze-check.py` gains one check: a claim's red `Control:` receipt must
have its exact bytes at a strict ancestor of the freeze commit (`CONTROL-ADDED-NOT-BEFORE-FREEZE`). The rule
is content-bound (blob equality over `git rev-list -- <path>` from the freeze's parents), not add-commit bound,
so a receipt added green in an ancestor and rewritten red at the freeze commit is refused. Default output
without `--substance` is unchanged (lane sweep over 37 preregistrations: zero plain differences).

| name | kind | entry command | verdict map | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r61 control-chronology arm | gate | `python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40 --substance` | 0 every control's bytes exist at a strict ancestor of freeze; 1 also CONTROL-ADDED-NOT-BEFORE-FREEZE | `python3 -B tools/souji-freeze-check.py --selftest --substance` → `cases=15 pass=15`; `--selftest` → `cases=41 pass=41` | `census/round-61/preregistration.txt`; counter `census/round-61/c1-counter.py`; matrix `census/round-61/c1-matrix.tsv` + `census/round-61/matrix/` | read-only git object store | souji |

Binding limits: bytes, not execution; a fabricated receipt committed before freeze passes; history-bounded
(fail closed on hidden ancestors). Rounds 41–55 records gain the same class on their control receipts; they
are historical and unrewritten. Not in this round: the receipt writer's skip-worktree blindness
(`corpus/knowledge/skip-worktree-concealment.md`; closed by the `tools/souji-receipt-write.py` refusals `RECEIPT-INDEX-FLAG-CONCEALED`, `RECEIPT-STATE-CHANGED-DURING-RUN` and `RECEIPT-INDEX-ENV-SET`; see `## Round 62` and `## Round 65`), the r61 fixture for C2 (not claimed),
and the preregistration `## MACHINE BLOCK` (critic F13). Certification OFF, K5 HELD.

## Round 62 — index-flag refusal (C1 operability) and stale-statement count (C2 calibration)

Frozen claims: `census/round-62/preregistration-freeze3.txt` (freeze commit c5af0e0a; controls commit 57a85817; the two earlier freeze attempts stay in history, refused by the checker for receipt grammar). Candidate writer commit a0b396cd.

- C1 counter: `python3 -B census/round-62/c1-counter.py --root . --matrix census/round-62/c1-matrix.tsv --base-rev 16fa821fdce00e709d6895ccfc7aaffa465af195 --rev <full40> --tool tools/souji-receipt-write.py --work DIR` (DIR must not live under /tmp). Frozen target: `SUMMARY matrix=7 base_forgeries=3 base_honest=2 new_forgeries=0 new_honest=2 class_mismatches=0 regress=PASS` and `EXIT=0`. Measured at a0b396cd: `census/round-62/records/c1-after.txt`. Do-nothing (base bytes in the new slot): `census/round-62/controls/c1-do-nothing.txt`, `new_forgeries=3`, `EXIT=1`.
- C2 counter: `python3 -B census/round-62/c2-counter.py --root . --rev <full40>`. Frozen target: `stale_open=0 landed>=3 verdict=PASS`, `EXIT=0`. Do-nothing at the base revision: `census/round-62/controls/c2-do-nothing.txt`, `stale_open=4 landed=0`, `EXIT=1`.
- Writer rule, extended in round 65: `tools/souji-receipt-write.py` refuses, before its dirty check and regardless of `--allow-dirty`, any tracked index entry whose `git ls-files -v` tag is not `H`, with a message beginning `RECEIPT-INDEX-FLAG-CONCEALED:` (S292 defines the tags, S291 the manual caveat); a flag set, or a file edited, while the wrapped command runs is refused with `RECEIPT-STATE-CHANGED-DURING-RUN` (the gap the round-62 sentinel probes 27–29 named, `census/round-62/wave/S62SentinelScope/`, closed by the r63/r64/r65 in-run re-reads); and an unmerged index entry is refused with `RECEIPT-INDEX-UNMERGED`. Scope of the in-run check, qualified in round 65 (lesson M9, M12): it covers tracked and untracked content visible to porcelain and to the snapshot; an edit restored to its exact prior bytes before the post-run read is accepted; a gitignored in-run edit is not checked; a permission change is checked on its permission bits only (setuid, setgid and sticky bits are not).
- Named limits, not claimed: the check is whole-index; the class check is a stderr substring; the r60 fixture is non-regression only.

## Round 65 — writer concealment refusals (C1 operability) and live-marker statement agreement (C2 calibration)

Frozen predicates: `census/round-65/preregistration.txt` (freeze `d2850b3eb160ae65c1c65b93753dfec7f4153b45`;
instruments `2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`; controls `3c5bfdc0db50785cb7b2ec60e509facf2d7e9f25`).
Base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`. Do-nothing controls: `census/round-65/controls/c1-do-nothing.txt`
(`new_forgeries=12`, `EXIT=1`) and `census/round-65/controls/c2-do-nothing.txt` (`findings=2`, `EXIT=1`).

- C1 counter (19 rows): `python3 -B census/round-65/c1-counter.py --root . --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b --rev <full40> --tool tools/souji-receipt-write.py --work DIR`. Frozen target: `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`. Realizability probes: `census/round-65/probes/` (r64 M1 N4 dispute and M5 N2 shapes, resolved pre-freeze).
- C2 counter (4 statements, live markers): `python3 -B census/round-65/c2-counter.py --root . --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 --rev <full40>`. Frozen target: `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`. A needle counts only on an uncommented `refuse(`/`return` line; the dead-token second-polarity mutant (tokens kept, refusals dead) produces findings (selftest 13/13).
- Writer deltas landed this round: every status read overrides `status.showUntrackedFiles=all` (V1/V2); the snapshot payload records each regular file's mode beside its digest (MOD); a symlink inside an untracked directory is recorded by name and target string, never followed (SY1/SY2, the r64 M5 rule); `GIT_INDEX_FILE` present in the environment refuses even when it names a nonexistent path (P13). Named limit: env redirects beyond GIT_INDEX_FILE (GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE) are unread; the C2 live read is lexical and does not prove reachability.

| name | kind | entry command | verdict map | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r65 writer concealment matrix | gate | `python3 -B census/round-65/c1-counter.py --root LANE --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b --rev FULL40 --tool tools/souji-receipt-write.py --work DIR` | 0 = `new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`; 1 otherwise; 2 could-not-evaluate | `python3 -B census/round-65/c1-counter.py --selftest --root LANE --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b --work DIR` → `cases=8 pass=8` | prereg `census/round-65/preregistration.txt`; controls `census/round-65/controls/`; probes `census/round-65/probes/` | writes only under `--work` and `--receipt` | souji |
| r65 live-marker statement agreement | gate | `python3 -B census/round-65/c2-counter.py --root LANE --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 --rev FULL40` | 0 `findings=0 verdict=PASS`; 1 findings>0; 2 usage error | `python3 -B census/round-65/c2-counter.py --selftest` → `cases=13 pass=13` | population `census/round-65/c2-statements.tsv` at `2761f0aa`; control `census/round-65/controls/c2-do-nothing.txt` | none (read-only, in-memory selftest) | souji |
| r65 freeze chronology arm | gate | `python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40 --chronology` (composes with `--substance`) | 0 = every Control `rev=` strict ancestor of freeze and every `After:` receipt strict descendant; 1 CONTROL-REV-NOT-BEFORE-FREEZE, RECEIPT-MEASURED-BEFORE-FREEZE, AFTER-MISSING/SYMLINK/REV-MISSING/REV-INVALID/EMPTY | `python3 -B tools/souji-freeze-check.py --selftest --chronology` → `cases=52 pass=52`; plain `--selftest` stays `cases=41 pass=41`; default output byte-identical over 33 committed preregistrations | candidate `.ufo/waves/round-64/w1/S64ExecFreeze/` (r64 seat), landed this round; sweep in the round-65 lesson | read-only git object store | souji |

Certification OFF, K5 HELD.
