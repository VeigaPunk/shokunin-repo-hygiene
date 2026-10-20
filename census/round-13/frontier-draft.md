# round-13 frontier draft — F2 coverage map, PROVINCE movement, SKILL additions

Seat: SoujiR13.FrontierDraft (leaf executor). Drafted 2026-10-20. Baseline
HEAD `31984f4` (`31984f473ce4bdab61a99b16cca194b28108cb81`). Write scope: this
file and `.ufo/waves/round-13/w1/FrontierDraft.md` only. No shared doc was
edited. Observation was read-only except one disposable fixture under
`/var/tmp`, removed by the same process; no live repository was censused, no
file was deleted, no tool was installed.

Status words used below: **observed** (seen in this session),
**bounded** (true for the isolated fixture and host version only),
**[INFERENCE]** (my reading, not directly observed), **to-verify** (L1 check
listed in §6).

## 1. Artifact state at drafting time

Hashes and presence are point observations; peers were still writing while
this draft was authored. A hash that differs at integration is not evidence
against the artifact, only against treating this table as current.

| path | state at observation | sha256 |
|---|---|---|
| `corpus/knowledge/git-repo-structure-readonly.md` | untracked, 3061 B | `48ff065ff1fa19fb43a145282cf4e7aaa86029af7cd6e2d285365fefdc3b04e1` |
| `tests/fixtures/r13-repo-structure.sh` | untracked, 4 pinned ids; hash changed once during drafting (`6c94f7fc…` → `5968a460…`) | `5968a4600174eff59890e7cf3d5f22ac268c331557cb522e9922342c138f6578` |
| `tools/souji-repo-structure.sh` | untracked; hash changed twice during drafting (`42ae8040…` → `6be5e321…` → `97b324a7…`) | `97b324a7590bb68676edbd4af71e88abe5e6aebb0dfc3b59d2b69785e32bc92e` |
| `census/round-13/verification.json` | **absent** | — |
| `SKILL.md` | modified in working tree (§ F2 at line 142) | `6561c948c98e928074ab5275493f24bbfc2f080b73265ea9cd541404dbade281` |
| `PROVINCE.md` | modified in working tree (§ Round 13 boundary refinement at line 72) | `dad81c3de8132325f3570cf5a15c18bb6e1b182eb532a5bb16bb0a423ac44d65` |
| `corpus/README.md` | modified; new F2 row at line 68 | `ef9086c13c09f31a78cebab42f1a9055d7951b76361accefd4b46b14b3c3a8e9` |
| `corpus/SOURCES.md` | modified; S035/S036 supersede S005/S006, S037 opens tagged source | not hashed (moved during drafting) |

Registry facts as read (`corpus/SOURCES.md:42-45`): S035 (git-repo, 2.56.0 web
plus installed 2.55.0) and S036 (git(1), same) are `mined` and name
`corpus/knowledge/git-repo-structure-readonly.md` in `used-by`; S037
(`builtin/repo.c`@v2.55.0, `:744`, `:798-801`, `:930`; `path-walk.c:146`) is
`mined` and adds the load-bearing limit: the walk starts from refs, skips
object-info errors, and returns zero after statistics. S034 (timeout) is
unrelated to F2.

`census/operator-sweep-20261019/` was not opened, scanned or staged.

## 2. F2 coverage map (minimal)

F2's declared ground (`PROVINCE.md:55`) is "repository size census
(`git repo structure`, `count-objects`)". It decomposes as follows; only the
first block is within the round-13 capability.

| # | sub-ground | status | grounding | gap / next |
|---|---|---|---|---|
| 1 | One structure run leaves no persistent `.git` delta, normal repo | **observed, bounded** | §3 run: 3 manifest diffs empty (content+mtime+size) on git 2.55.0 | packs, submodules, hooks, alternates, concurrent writers untested; atime/ctime excluded |
| 2 | Reachable-object metrics: ref counts, per-type counts, inflated and disk sizes, largest objects | covered | S005/S035; S037 `repo.c:744,798-801,930`; 28-key `lines` inventory observed | key set is EXPERIMENTAL; no stability promise |
| 3 | Machine-readable format | covered as a constraint | S005 roff :44 ("THIS COMMAND IS EXPERIMENTAL"), :166 (default table "may change and is not intended for machine parsing"); `-h` lists `--format=(table\|lines\|nul)` and `-z` | parsing the table, or pinning the 28-key set without a version, is the failure mode |
| 4 | Optional-lock suppression and its bound | covered, bounded | S006/S036 roff :2195-2200; observed: `.git/index` mtime and bytes unchanged under `GIT_OPTIONAL_LOCKS=0`, index rewritten under `=1` after a stat-stale touch | mandatory writes, hooks, alternates, promisor and concurrent writers are not excluded by the variable |
| 5 | Invalid, bare and linked-worktree repositories | partially observed | this run: plain dir → rc 128; bare → rc 0; linked worktree → rc 0, one call each on 2.55.0 | no manifest diff and no metric parse for bare/linked; probe's refusal (exit 2) was not run |
| 6 | Partial-clone / promisor refusal | implemented, **not fixture-tested** | probe guards `extensions.partialClone` and `remote.*.promisor` before the walk (tool lines 192-227 at observed sha `97b324a7…`); fixture header excludes promisor (line 93) | add a fixture case, or the refusal stays a design claim |
| 7 | Unreachable/loose object accounting (`count-objects`) | **not covered** | one `git count-objects -v` output observed (`count: 6`, `size: 24`, `in-pack: 0`); no source row opened; `corpus/SOURCES.md` § Leads lists git-count-objects(1) unopened | open a source row before any entry cites its semantics |
| 8 | Reclaimable disk / a path's own footprint | **not covered by design** | structure totals are object bytes rooted at refs (S037); a worktree deletion frees checked-out files, not objects still reachable from another ref | needs per-path filesystem measurement plus the receipt taxonomy |
| 9 | Reclamation authorization (`gc`, `repack --expire-to`, prune) | out of province for this capability | S002/S004 govern timing (F1 entries); K2 in `corpus/lessons/round-12.md` § Gate leaves the hold change to the operator | operator decision; a census authorizes nothing |
| 10 | Comparative size tooling (`git-sizer`) | not admitted | S013/S014 queued | no entry; not required for the bounded capability |

Row 10 is recorded only so the map is exhaustive; it is not a round-13 task.

## 3. Observed isolated run

Method: Python `subprocess` driver; `tempfile.mkdtemp(prefix=…, dir="/var/tmp")`;
`shutil.rmtree` in a `finally` block; environment scrubbed of inherited `GIT_*`
and then set to `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`,
`GIT_OPTIONAL_LOCKS=0`; every git call carried `-c maintenance.auto=false`
plus fixture `user.name`/`user.email`/`commit.gpgsign=false`. Every operation
after creation named its repository with `-C`; the two `init` calls used an
explicit absolute `cwd` under the temp root. I did not pass
`maintenance.autoDetach=false`; the probe does. Two fixtures were used: a
two-commit repo (manifest and status comparisons) and a one-commit repo (key
inventory). The lane probe was read for its documented behaviour, not
executed; every command in this section was the raw installed git.

Observed results, git 2.55.0:

| observation | result |
|---|---|
| `git repo structure --format=lines` | rc 0; 28 lines; keys `references.{branches,tags,remotes,others}.count`, `objects.{commits,trees,blobs,tags}.{count,inflated_size,disk_size,max_size,max_size_oid}` (plus `max_parents`/`max_entries` and their `_oid`); two-commit repo reported counts 2/2/2 |
| `git repo structure --format=nul` | rc 0; 28 NUL-delimited pairs; first pair `references.branches.count\n1\0` |
| `git repo structure` (default table) | rc 0; header `\| Repository structure \| Value \|` |
| `--progress` | rc 0, empty stderr |
| `.git` manifest around each structure call | no added, removed or changed file (content sha256 + mtime_ns + size) across `lines`, `nul`, and `table`+`count-objects` |
| `git status --porcelain`, `GIT_OPTIONAL_LOCKS=0`, after `os.utime` made the index stat-stale | index mtime unchanged (`1792473359884131555` → same); no file changed |
| same status, `GIT_OPTIONAL_LOCKS=1` | index mtime advanced to `1792473359890009788`; manifest `changed: ["index"]` |
| `git -C <plain-dir> repo structure` | rc 128; stderr `fatal: not a git repository (or any of the parent directories): .git` |
| `git -C <bare> repo structure --format=lines` | rc 0 |
| `git -C <linked-worktree> repo structure --format=lines` | rc 0; `git worktree add` rc 0 |
| cleanup | temp root removed |

Bound of the result: one host (git 2.55.0), one filesystem, normal SHA-1
repositories, no packs, tags, remotes, alternates, submodules, hooks or
concurrent writers. It is an observed no-persistent-delta for these runs, not
a universal write-safety proof and not deletion authority. The durable,
re-runnable form is the committed fixture (`--selftest`), which this seat did
not execute.

## 4. PROVINCE movement / retention recommendation

**Decision: retain F2 as a frontier row; admit only the bounded read-only
census to Core — and only if the supporting artifacts land in the same
commit.**

Reasons, in the lane's own rules:

1. PROVINCE's movement rule (`PROVINCE.md:49-50`) requires an admitted
   `corpus/knowledge/` entry and a SKILL rule. Both exist only in the working
   tree at drafting time (entry untracked; SKILL modified, § F2 at line 142).
   At HEAD, neither resolves.
2. F2's declared ground includes `count-objects`, which has no opened source
   row; admitting the whole row would claim unopened ground. The probe does
   not run it either.
3. S037 shows a zero exit does not establish complete object accounting
   (object-info errors are skipped). Q18 separates integrity/measurement from
   safety; a size census cannot authorize reclamation.
4. The reclaiming operations (`gc`, `repack --expire-to`, prune) are governed
   by F1's grace-period facts and left to the operator (K2). Moving them into
   Core under the census would silently absorb an operator decision.

Conditions for the Core sentence (all must be true at the closing commit):

- C-a the entry is admitted by the round Gate **from HEAD** (Q17), not from
  the worktree;
- C-b `tests/fixtures/r13-repo-structure.sh` is committed and its
  `--selftest` prints `selftest=PASS ids=4/4` (L1 run);
- C-c `tools/souji-repo-structure.sh` is committed;
- C-d S035/S036/S037 `used-by` names the admitted entry's actual filename;
- C-e `census/round-13/verification.json` exists if the entry, README row or
  PROVINCE text cites it — otherwise the citation is removed (Q17).

If any condition fails, drop the Core sentence and leave F2 unchanged; a
partial move is worse than no move.

Proposed replacement for `PROVINCE.md:72-80` (the in-flight text is close;
this version states the condition and the remainder explicitly):

```
## Round 13 boundary refinement

The bounded read-only structure census becomes Core only when the entry, the
probe and the write-safety fixture land in the same commit and the round Gate
admits `corpus/knowledge/git-repo-structure-readonly.md` from HEAD. It reports
reachable objects rooted at refs: not unreachable objects, not recoverable
disk space, and not removal authorization (S037, builtin/repo.c:744,798-801).
F2's remainder stays frontier: unreachable-object accounting (`git
count-objects` and `git rev-list --disk-usage` remain unopened leads) and any
reclamation decision (`gc`, `repack`, prune), which is the operator's.
Evidence-integrity checking is limited to souji's own receipt/certification
fragments; it does not become fleet orchestration or an independent promotion
authority.
```

Proposed replacement for the frontier bullet at `PROVINCE.md:55-56`:

```
  - F2 repository size census & reclamation boundary — the bounded read-only
    `git repo structure` census is Core with the r13 entry; open ground is
    unreachable/loose accounting (`git count-objects`,
    `git rev-list --disk-usage`) and who authorizes reclamation (operator).
```

Proposed replacement for `corpus/README.md:47`:

```
- F2 repository size census — bounded read-only structure census is Core as of
  r13 (entry + probe + fixture); next: unreachable-object accounting
  (`git count-objects`/`git rev-list --disk-usage`, unopened) and the operator
  decision on reclamation.
```

`corpus/README.md:68` currently cites `../census/round-13/verification.json`;
that file was absent at drafting. Either it lands (condition C-e) or the row
must drop the citation.

## 5. SKILL additions (draft only; not applied)

The in-flight SKILL section (line 142) already states the probe command, the
S005 format warning and the S006 bound, and carries a three-row table and a
one-paragraph checklist. The safe additions below fill only what is still
missing; they are written to be appended, not to rewrite existing lines.

### 5.1 Decision-table rows — append to the table at `SKILL.md:150-154`

```
| Unreachable/loose object account, or `count-objects` numbers | Not delivered by the structure probe; no source row is open for `count-objects`. Open one, run a separate census, and never infer it from `objects.*` reachable totals. |
| `extensions.partialClone` set or `remote.*.promisor=true` | Refuse: the probe's documented behaviour is exit 2 before the walk (not run by this seat). A zero exit from a partial clone is not complete accounting (S037: object-info errors are skipped). |
| Bare repository or linked worktree | The command runs (rc 0 observed on 2.55.0), but write-safety and metric shape were established only for one normal repo. Record the layout; treat the counts as exploratory, not a receipt. |
```

### 5.2 Error patterns — append under `## Error patterns (false-SAFE signatures)` (`SKILL.md:66`)

```
- **Reachable-size-as-reclaimable**: `git repo structure` totals count
  reachable objects rooted at refs (S005/S035; S037 `repo.c:744,798-801`).
  They are not the bytes a path or worktree deletion frees, and
  `objects.*.disk_size` is not a filesystem measurement. Observed r13: the
  structure totals for 6 reachable objects sat beside `git count-objects -v`
  reporting `count: 6`, `size: 24` — different definitions, and the
  `count-objects` unit is not sourced this round; mixing them manufactures a
  saving figure. Flip: a receipt naming the path's own bytes before/after and
  every ref still holding its blobs.
- **Optional-locks overclaim**: `GIT_OPTIONAL_LOCKS=0` skips optional
  lock-taking sub-operations such as the `git status` index refresh
  (S006/S036 roff :2195-2200; observed: index unchanged under `=0`, rewritten
  under `=1`). It does not forbid mandatory writes, hooks, alternates,
  promisor fetches or concurrent writers; a "no writes at all" claim from
  setting the variable is false-SAFE.
```

### 5.3 Pre-census checklist — append after `SKILL.md:156-159`

```
Pre-census (all must answer yes):
- [ ] Repo resolves (`git -C <repo> rev-parse --show-toplevel` /
      `--absolute-git-dir`); normal, bare or linked layout recorded
- [ ] `git --version` and the exact argv are retained; `--format=lines`
      (never the default table, S005 roff :166)
- [ ] `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`, `-c maintenance.auto=false`;
      no fetch, maintenance, `gc` or `repack`
- [ ] Partial-clone/promisor refused; output stored under `census/round-<N>/`;
      no deletion decision derived from it
```

## 6. Proposed final checks for L1 (exact)

Ordered; run after integration, not by this seat.

1. **Gate (behaviour).**
   `bash tests/fixtures/r13-repo-structure.sh --selftest`
   expected final line `selftest=PASS ids=4/4`.
   With the probe: `bash tests/fixtures/r13-repo-structure.sh --selftest
   --probe tools/souji-repo-structure.sh`, same expected line.
2. **Q4 literal (fails as authored).**
   `grep -c 'TMPDIR:-/tmp' tests/fixtures/r13-repo-structure.sh` → observed
   **1** at line 88 (fixture sha `5968a460…`), a comment reading "(TMPDIR
   ignored; no ${TMPDIR:-/tmp} literal)". Q4's test demands 0. Reword the
   comment (e.g. "no TMPDIR fallback literal") before admission;
   `grep -c '/var/tmp'` → 4 satisfies the other half.
3. **Admission provenance (Q17).**
   `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e
   HEAD:tests/fixtures/r13-repo-structure.sh` and the same for
   `HEAD:corpus/knowledge/git-repo-structure-readonly.md`; both must exit 0
   at the closing commit (use its hash once HEAD has moved). A worktree
   `test -e` is not the check.
4. **Cited evidence resolves.**
   `test -e census/round-13/verification.json` → required iff the entry or
   README still cites it (C-e).
5. **SOURCES `used-by` consistency.**
   `awk -F'|' '$2 ~ /S03[567]/ {print $2 "|" $12}' corpus/SOURCES.md`
   must name `corpus/knowledge/git-repo-structure-readonly.md`. Note:
   `census/round-13/source-draft.md:37` proposes the slug
   `size-census-git-repo-structure.md`; the actual file is
   `git-repo-structure-readonly.md` — the draft's slug is stale.
6. **Coverage row.** `grep -n '^| F2' corpus/README.md` must name the admitted
   entry and must not cite an absent verification file.
7. **Optional, bounded reproduction of §3** (not a gate, not on a live repo):
   run the fixture with `--probe`; its `write-free` case is the durable form.
   Do not run the probe across live fleet repositories as an admission check.

## 7. Limitations, risks, blockers

- All F2 artifacts were in flight; the probe's hash moved twice while this
  draft was written. Re-read, do not trust §1 hashes at integration.
- The fixture's header limits it to one fresh SHA-1, loose-object,
  single-commit, normal repository; promisor, packs, bare, linked, alternates,
  submodules and concurrent writers are explicitly out. The probe's promisor
  refusal is therefore a design claim until a case exercises it.
- `census/round-13/verification.json` was absent; the entry's `verified-at`
  sentence and the README row both depend on it.
- `git count-objects` and `git rev-list --disk-usage` have no opened row;
  they stay Leads.
- The bounded result is observed write-safety in isolation, not certification
  and not deletion authority; certification remains OFF.
- No live fleet repository was probed and no live file was removed. The only
  removal was the disposable fixture root under `/var/tmp`, deleted by the
  same process and verified absent afterwards.

## 8. Tooling record

No install or upgrade was performed, so there is no tool/version/channel entry
to report. Git used was the host's `git 2.55.0`; Python was the host runtime
used for the disposable fixture only.
