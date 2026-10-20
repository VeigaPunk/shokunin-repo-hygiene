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
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv]` | 0 census emitted — `dirty` is normal-mode (a wholly untracked directory is one collapsed line) and, D1, measured with explicit `--untracked-files=normal` so it is independent of a repo-local, include-carried or `config.worktree` `status.showUntrackedFiles`; rows may carry `error`/`status-unverifiable`/`not-a-repo` for degraded repositories, so a wholly degraded fleet still exits 0 — placeholders, not measurements; D2: a hardlinked, non-regular or unresolvable `$GIT_DIR/info/attributes` degrades that repository only (stderr `souji-census: git-metadata-unsupported <reason> <path>`; when a degraded config also fires, its soft line prints too); or header-only diff; 3 failed differential comparison; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage/malformed baseline/whole-run `path-protected: git-metadata-*` refusal for config, HEAD, index, packed-refs, commondir, info/exclude or alternates | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | historical r16: `census/round-16/c1-matrix-final.json`; r17 behavior: `census/round-17/c1-matrix.json` (L1) read with `r17-census-hygiene` below | read-only census; compare capture and isolated selftest under `/var/tmp` | souji |
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
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--base REV] [--json OUT]` | 0 no findings; 1 findings (LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED); 2 could-not-evaluate and total: usage/unknown rev/no SKILL.md/missing wave dir, an unreadable blob, a failed git read or a falsy `files` pin — never demoted to a finding | `python3 tools/souji-landing-gate.py --selftest` (exact finding-id sets per case, 28 cases) | literal finding ids, failure vocabulary and frozen-path rule in the tool; committed replays `census/round-17/gate-replays-expected.json` with record `census/round-17/gate-replays-ddb7347.json` (L1) | reads committed blobs; private `/var/tmp` snapshot removed; runs only `bash -n` and Python `compile()` | souji |
| r16-landing-gate | gate | `python3 tests/fixtures/r16-landing-gate.py [--tool PATH]` | 0 clean; 1 failed case; 2 could-not-evaluate prerequisite | same; includes a vacuity stub that must fail | historical r15 replay pins and synthetic same-round cases in the fixture | isolated `/var/tmp` git repos removed afterwards | souji |
| r17-gate-replays | gate | `python3 census/round-17/gate-replays.py [--gate-rev REV] --output <new.json>` | 0 every pinned replay's exact (id, path) multiset and exit code equal `census/round-17/gate-replays-expected.json` (b410186 → 1 with 5 ids; a31642d → 0; cc21683 → 0; 6ff91f5 → 0; 79bbe7a → 1 with 29 LG-SEAT-UNCARRIED), the gate's own `--selftest` tail recorded; 1 any divergence (extra/missing row or exit code); 2 could-not-evaluate bad rev/missing gate/output exists/missing expected file/usage | identity run `--gate-rev 5fa6017` against the expected file derived from that same gate exits 0; the changed-gate run is the differential and must be explained, never fitted to prose | `census/round-17/gate-replays-expected.json` (committed at ddb7347) and record `census/round-17/gate-replays-4f48343.json` (committed at 95519a7; r18 correction — the earlier `ddb7347` record name was never committed) | extracts the gate to private `/var/tmp` (also hardcoded in the gate's selftest); writes only `--output`/`--write-expected` | souji |
| souji-seat-audit | gate | `python3 tools/souji-seat-audit.py --spec W.json --transcripts DIR --lane LANE [--json OUT]` | 0 no major violation — majors are `V-SURFACE`, `V-LIVE-CENSUS`, `V-WRITE-SCOPE`, `V-WRITE-RELATIVE`, `V-EXEC`; `V-WRITE-UNPARSED` is status-aware (major on `⇒ ok`, minor on `⇒ error`), `V-PROBE`/`V-RECURSIVE`/`V-WRITE-AMBIGUOUS`/`V-WRITE-HEADER-INFERRED` are minors; exit 0 is a disclosure floor, never proof the probe rule held; 1 at least one major; 2 could-not-evaluate usage/unreadable spec or transcript | `python3 tools/souji-seat-audit.py --selftest` (severity-exact; `SELFTEST pass=66 fail=0` at b576341) | literal class set and per-case expected class sets in the tool; r16 replay record regenerated by `census/round-17/seat-audit-replay.py` over `census/round-16/transcripts` (MANIFEST-checked): `census/round-17/seat-audit-r16-replay-base5fa6017.json` / `census/round-17/seat-audit-r16-replay-4f48343.json` (r18 correction: was `-ddb7347.json`, never committed) | reads exported transcripts read-only; writes only `--json` (refuses overwrite) | souji |
| r17-transcript-manifest | gate | `python3 census/round-17/transcript-manifest.py --check DIR` | 0 every listed digest matches, no listed file missing, no unlisted file present; 1 mismatch/missing/extra; 2 usage/unreadable directory | `--write` then `--check` on a private `/var/tmp` copy exits 0; a one-byte mutation of one file makes `--check` exit 1 (negative control) | `census/round-16/transcripts/MANIFEST.sha256` (sorted `sha256  relpath`, `LC_ALL=C`) over the byte-exact r16 w1/w2 transcripts | `--write` creates `MANIFEST.sha256` inside the named directory only; `--check` read-only; never alters transcript bytes | souji |

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
