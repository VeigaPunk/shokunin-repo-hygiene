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
3. `git mv` (or plain `mv` for untracked) into `<repo>/.ufo-quarantine/<utc-date>/...` — quarantine is a normal commit in the owning repo, made with the guarded form in the Pre-quarantine checklist.
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
- [ ] Lane identity: `souji-shokunin <souji@shokunin.local>`
- [ ] Right repo: `git -C <repo> rev-parse --show-toplevel` prints the owning repo (never trust `cd`)
- [ ] Commit guarded and scoped: `git -C <repo> add -- <approved paths>` then `git -C <repo> -c maintenance.auto=false commit -- <same approved paths>` — never `git add -A` / `.`
- [ ] Pinned registrations stay pinned: `git -C <repo> worktree list --porcelain | awk '/^locked/{n++} END{print n+0}'` equals the pin count; pin new ones with `git -C <repo> worktree lock --reason "<why>" <worktree-path>`

## Gate registry

Gate map: 0 clean · 1 failed · 2 could-not-evaluate. Other codes are
explicit below. The four legacy receipt/action tools are **probes**, not
Gate-standard certifications: their live verdicts are data, expected baselines
are not pinned, and code 1 also carries setup failures. Embedded selftests
alone do not repair those interface debts. Always use `TMPDIR=/var/tmp`
for the legacy selftests; their historical fallback is not Q4-conformant.

| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| souji-verify | probe | `bash tools/souji-verify.sh <path>...` | 0 clean, SAFE/NOT-SAFE data; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest` | none; no pinned complete id set | read-only targets; isolated selftest under TMPDIR | souji |
| souji-vault-verify | probe | `bash tools/souji-vault-verify.sh --fallback <path>...` | 0 clean, VERIFIED/NOT-VERIFIED data; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest` | none; no pinned complete id set | read-only source/vault; isolated selftest under TMPDIR | souji |
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv]` | 0 clean; 3 failed differential comparison; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage/malformed baseline/protected or unsupported Git path (`path-protected`) | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | caller comparison is unpinned; no pinned complete legacy selftest id set | read-only census; compare capture and isolated selftest under `/var/tmp` | souji |
| souji-quarantine | probe | `bash tools/souji-quarantine.sh --dry-run <repo> <target>...` | 0 clean target outcome; 3 failed/refused/aborted; 4 could-not-evaluate live guard; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage | `TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest` | no complete safety-suite baseline; receipts advisory, certification OFF | dry-run read-only; explicitly authorized action moves targets within owning repo; selftest under TMPDIR | souji |
| r12-maintenance-guard | gate | `bash tests/fixtures/r12-maintenance-guard.sh` | 0 clean; 1 failed; 2 could-not-evaluate | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | expected counts and SELFTEST_EXPECTED_IDS in fixture; `tests/results/r12-maintenance-guard.txt` | isolated `/var/tmp/souji-r12-maintenance.*` | souji |
| souji-cert-evidence | gate | `python3 tools/souji-cert-evidence.py --root PATH --manifest PATH` or `--frozen DIR` | 0 clean declared consistency; 1 failed honest fragment; 2 could-not-evaluate malformed/inconsistent/tampered input | `python3 tools/souji-cert-evidence.py --selftest`; `python3 tests/fixtures/r13-cert-evidence.py` | embedded expected exit/finding ids; `tests/fixtures/r13-cert-frozen/expected.json` pins every input | inputs read-only; selftests isolated `/var/tmp`; never executes recorded commands | souji |
| souji-repo-structure | probe | `bash tools/souji-repo-structure.sh --repo PATH` | 0 clean metadata emitted; 2 could-not-evaluate usage/repo/promisor; 3 could-not-evaluate unsupported Git; 4 could-not-evaluate config/stderr/command/output | corresponding gate below | no live-data expected baseline | repository reads; capture-only `/var/tmp` directory removed on exit | souji |
| r13-repo-structure | gate | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | 0 clean; 1 failed; 2 could-not-evaluate | same `--selftest --probe` command | fixture SELFTEST_EXPECTED_IDS and case expectations; recorded run `census/round-13/verification.json` | isolated `/var/tmp/souji-r13-repo-structure.*` | souji |
| r13-quarantine-bounds | gate | `bash tests/fixtures/r13-quarantine-bounds.sh [--tool PATH]` | 0 clean; 1 failed case or id set; 2 could-not-evaluate usage/environment | same command, isolated positive/negative controls; baseline red arm uses `--tool` | fixture EXPECTED_IDS and per-case exit/finding/retention assertions; `census/round-13/verification.json` | isolated `/var/tmp/r13-qbounds.*` only | souji |
| souji-evidence-cache | gate | `python3 tools/souji-evidence-cache.py --root DIR --record PATH [--require REL...]` or `--frozen DIR` | 0 clean/reusable declared dependencies; 1 failed/stale/missing dependency or matched false; 2 could-not-evaluate malformed/legacy/protected/tampered input | `python3 tools/souji-evidence-cache.py --selftest`; external fixture below | literal embedded expected ids; `tests/fixtures/r14-cache-frozen/expected.json` input pins | inputs read-only; isolated selftest `/var/tmp`; never executes a recorded command | souji |
| r14-evidence-cache | gate | `python3 tests/fixtures/r14-evidence-cache.py [--tool PATH]` | 0 clean; 1 failed assertion; 2 could-not-evaluate missing prerequisite | same default self-invocation fixture; isolated positive/negative CLI calls | literal expected exits/finding ids in fixture; `tests/fixtures/r14-cache-frozen/expected.json` | isolated `/var/tmp/souji-r14-cache-fixture.*`; reads selected gate and committed snapshot | souji |
| r14-census-boundary | gate | `python3 tests/fixtures/r14-census-boundary.py --tool PATH` | 0 clean; 1 failed case/id-set; 2 could-not-evaluate missing prerequisite/trace/usage | same default self-invocation fixture, synthetic HOME with spy and strace access checks; `--tool` selects paired baseline | fixture EXPECTED_IDS and literal expected exits/finding/access assertions | isolated `/var/tmp/r14-census-boundary.*`; never a real credential-store probe | souji |

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
  (r6; per-repo worktrees/unpushed/dirty/scratch/mtime/flags).

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
or certify deletion safety. External mutable checks must run afresh.
The actual consumer is `census/round-13/run-verification.py`; its historical
JSON evidence is not rewritten. The isolated causal demonstration is
`census/round-14/cache-demonstration.py` (isolated synthetic inputs only).

The metadata census must refuse roots, ancestors, comparison paths and known
Git/worktree aliases into the credential store before enumeration or content
readers. Do not test this on a real store: use only the isolated fixture
`tests/fixtures/r14-census-boundary.py`. Symlink discovery is metadata outside
the protected tree, not permission to follow its target. Protected-namespace
checks are not a general sandbox against hostile hardlinks, bind mounts or
concurrent replacement. Source S040 explains filesystem-aware resolution;
QUALITY Q20/Q21 and `corpus/lessons/round-14.md` bind these limits.
