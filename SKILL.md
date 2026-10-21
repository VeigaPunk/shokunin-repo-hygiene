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
| `stale` | scratch type as the tool classifies: `.scratch/`, `*.out`, `*.log`, `launch-*.json`, `*-draft.*` (NOT `*.tmp`, not `out/`) AND zero live references (sweep excludes `.git`, `souji-shokunin/census/**`, `souji-shokunin/tests/**`, quarantine) AND mtime older than `--stale-days` (default 1). |

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
| r22-result-oracle | gate | `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` | 0 all225 literal decisions match (original214 plus11 appended `adequacy` guards); 1 R22-RESULT-CONTRACT mismatch (including exception); 2 could-not-evaluate input/usage, R22-ORACLE-INPUT-TAMPERED or unknown-case | same self-invocation over committed public18-step outputs plus fabricated deltas; base 41553adb source graded in memory via `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py \| python3 -B census/round-22/mutation-adequacy.py --grade-stdin` must be red (69/225) | tests/fixtures/r22-result-oracle.json pins original receipt/frozen inventory SHA256 and expected booleans; each receipt binds oracle/runner SHA256 | read-only source/JSON imports; no subprocess, /proc, scratch tree or scanner invocation | souji |
| r22-mutation-adequacy | gate | `python3 -B census/round-22/mutation-adequacy.py [--oracle FILE] [--grade-stdin]` | 0 pristine runner passes and every expect=killed literal mutant is killed (equivalent marks must survive); 1 a non-equivalent survivor or pristine failure; 2 missing/ambiguous anchor or usage; `--grade-stdin` grades stdin runner source in memory with the oracle's exit map | `--oracle <exported b912328d00d19f26918240710d0b5e0f334880ff:tests/fixtures/r22-result-oracle.json>` (214 vectors) must be red: 11 non-equivalent survivors (`census/round-22/mutation-adequacy-oracle214.json`) | literal replacement pairs in the probe; `census/round-22/mutation-adequacy-oracle225.json` | in-memory compile only; no file write, subprocess, /proc or scanner | souji |

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
