# r13 w1 — AttackCoverage (critic, C3 F2 size census)

Seat: SoujiR13.AttackCoverage, a leaf critic. Not an independent non-author seat and not a judge. Certification is OFF.
Axes: calibration, operability, coverage. Writes: this report only. Scratch: two `mktemp` dirs under `/var/tmp` with trap cleanup, already removed (`ls -d /var/tmp/souji-r13-attackcov*` → no match). Tool installs: none. strace 7.0-1 and git 2.55.0-1 were already installed.

## Verdict

The C3 claim (`census/round-13/claims.json` C3 "after") says "A sourced F2 entry, read-only structure probe and isolated before/after Git-directory manifest fixture demonstrate the bounded capability". As planned, that claim is **falsifiable and partly false**:

1. Under the exact guards SizeProbe plans to use, `git repo structure` **writes to `.git` and runs fetches** on a partial clone. A plain-repo fixture cannot detect this.
2. It **exits 0 on an incomplete census**: silent undercount, and also undercount with error lines on stderr. "Exit zero and real metrics" is a false-success test.
3. Its "reachable" and "disk_size" values leave out detached HEAD and unreachable objects. That is exactly the orphan class souji cares about (Q12).
4. The working tree **already declares acquisition** before the artifacts exist. This is the same defect class as r12 K5.

A narrow F2 entry is admissible. Its scope is given below. The entry as drafted is not admissible yet.

## Counterexamples. Observed facts are marked (O); inference is marked [INFERENCE]

Probe environment for every case: `HOME=$T/home GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_OPTIONAL_LOCKS=0 LC_ALL=C`. Each case ran `git -C <wt> repo structure --format=lines` under `strace -f -e trace=openat,rename*,unlink*,mkdir*,execve,connect`. The full `.git` manifest (name, size and sha256) was taken before and after. Upstream: 3 commits of `d/f1..f3` plus an annotated tag, `uploadpack.allowFilter=true`, cloned via `file://`.

| case | rc | stderr | .git manifest diff | children | counts (trees/blobs) |
|---|---|---|---|---|---|
| A plain repo (the planned fixture class) | 0 | empty | none | none | 6 / 3 |
| B `--filter=blob:none` clone, checked out | 0 | empty | none | none | 6 / 3 (all blobs local here; not a counterexample) |
| **C `--filter=tree:0` clone** | **0** | **empty** | **+12 files: 3 × `objects/pack/pack-*.{idx,pack,promisor,rev}`** | 3 × `git fetch origin --no-tags --no-write-fetch-head --recurse-submodules=no --filter=blob:none --stdin`, 3 × `index-pack --stdin --fix-thin --promisor`, 3 × `git-upload-pack` | **3 / 0** (upstream: 6 / 3) |
| **C rerun with `-c maintenance.auto=false` added (the full SizeProbe guard set)** | **0** | **empty (0 bytes)** | **.git files 28 → 40** | same 3 × fetch / index-pack | **3 / 0** |
| C without `-c maintenance.auto=false` | 0 | empty | as in C | as in C | — plus 3 × `openat(.git/objects/maintenance.lock, O_RDWR\|O_CREAT\|O_EXCL)` then `unlink`: the lazy-fetch children entered auto-maintenance, which a final-state manifest cannot see |
| **C2 `tree:0` clone + `GIT_NO_LAZY_FETCH=1`** | **0** | 3 × `error: bad tree object <oid>` | none | none | **0 / 0** |
| D detached-HEAD commit + 1 MiB unreachable blob (`hash-object -w`) | 0 | empty | none | none | commits=3, but `rev-list --all HEAD` → 4 commits; Σdisk_size = 349+263+12645+102 = 13,359 B vs `du -sk .git` = 1232 KiB |
| E run from a linked worktree (`worktree add --detach`) | 0 | empty | none | none | identical to A (common-dir refs and objects) |

### CE1 — operability and coverage: the "read-only" claim fails on promisor repos (strongest case)
- (O) Case C and its guarded rerun: `GIT_OPTIONAL_LOCKS=0` plus `-c maintenance.auto=false` does **not** stop writes. The command spawned network-class fetches and added promisor packs.
- (O) Source, `builtin/repo.c@v2.55.0`:
  - `count_objects` reads with `OBJECT_INFO_SKIP_FETCH_OBJECT | OBJECT_INFO_QUICK` (`:798-799`). That flag covers only the per-object size read.
  - The object walk `walk_objects_by_path(&info)` (`:872`) goes through `path-walk.c@v2.55.0:146`, `repo_parse_tree_gently(ctx->repo, tree, 1)`, which carries no skip-fetch flag.
  - [INFERENCE] `path-walk.c:146` is the call site that triggers the observed lazy fetches. The fetches themselves are observed; the call site is not traced.
- (O) S006 does not cover this. git(1) § ENVIRONMENT `GIT_OPTIONAL_LOCKS` (installed `git.1.gz`, sha256 `8b58cbf7…26ed`, roff :2195) speaks only of optional lock-taking sub-operations. The control that does apply is `GIT_NO_LAZY_FETCH` (roff :2122; rendered: "tells Git not to lazily fetch missing objects from the promisor remote on demand"). Case C2 confirms it prevents the write.
- [INFERENCE] With a real `https://` promisor, the same path means network access and a credential-helper invocation inside a "census". The no-credentials rule would be at risk.
- Planned fixture gap: SizeProbe's assignment (`w1-spec.json`, SizeProbe: "isolated /var/tmp git repo with file+commit") covers only case A. A green result there proves nothing about C.

### CE2 — calibration: exit 0 is not success
- (O) `cmd_repo_structure` ends `return 0;` unconditionally (`builtin/repo.c@v2.55.0:930`). A failed object read is skipped with `continue;` (`:801`).
- (O) In case C2, rc=0 while trees and blobs both read 0 and stderr carries errors.
- (O) In case C, rc=0 with **empty stderr** while trees read 3 against 6 and blobs 0 against 3: a silent undercount.
  - [INFERENCE] The mechanism may be `OBJECT_INFO_QUICK` missing packs fetched mid-walk. It is unverified; the undercount itself is observed.
- So SizeProbe's acceptance test "structure exits zero and outputs real object metrics" admits false success. A nonempty-stderr check alone would still pass case C.
- The draft entry's decision row "Command unavailable or rejects the repository → could-not-evaluate" (`corpus/knowledge/git-repo-structure-readonly.md:20`) does not cover an rc=0 partial census.

### CE3 — coverage and calibration: what "reachable" and "disk size" mean
- (O) The only roots are `refs_for_each_ref(get_main_ref_store(repo), …)` (`builtin/repo.c@v2.55.0:744`), with `add_pending_oid` in `count_references`. HEAD is not added.
- (O) Case D: a detached-HEAD commit is not counted. [INFERENCE from the same code] Reflog-only, index-only and other-worktree-HEAD objects are not counted either.
- These are the Q12 orphaned commits ("a pruned detached worktree HEAD"), the class souji's receipts must reason about. The census is blind to them.
- (O) `disk_size` totals cover ref-reachable objects only. In case D they were about 1% of the `.git` footprint. The draft entry's wording "not recoverable disk space" (`:18`) is right but too weak. Without a separate unreachable census, any F2 use of these numbers for space or receipt reasoning is a category error. The entry must also say "refs/ roots only, HEAD excluded".

### CE4 — coverage: worktree attribution
- (O) Case E: running from a linked worktree reports the shared common-dir store, the same as the main checkout.
- [INFERENCE] A fleet-wide size census that sums per-worktree probe outputs double-counts the shared store. Attribution must key on `git rev-parse --git-common-dir`.

### CE5 — calibration: false provenance and premature saturation already in the working tree
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short` (O), at the time of this review:

- `PROVINCE.md` (modified, +13/−1) claims "bounded structure probe and isolated write-safety fixture **acquired r13**" and "Core now includes … (`tools/souji-repo-structure.sh` …)". `ls` → **No such file** for both `tools/souji-repo-structure.sh` and `tests/fixtures/r13-repo-structure.sh`. This is also a Core/identity boundary change made in a mid-flight write.
- `corpus/knowledge/git-repo-structure-readonly.md` (untracked):
  - `:2` cites `census/round-13/verification.json`, which is **absent**. `census/round-13/` holds only `baseline-measures.md before.json claims.json mistake-draft.md source-draft.md`.
  - `:3` recheck is `bash tests/fixtures/r13-repo-structure.sh --selftest`, which is **absent**.
  - `:2` `verified-at:` names no git version, so it fails Q1 as written.
  - It cites no source code, although the docs are silent on writes. Q2 needs `<file>@<tag>:<line>` or a committed fixture.
- `corpus/SOURCES.md` S005/S006 are already flipped `queued → mined` with `used-by` set to that entry. The draft's own gate order (`census/round-13/source-draft.md:30`: "(a) write the F2 entry file, (b) confirm its path exists, (c) flip the cells") was satisfied only by an **untracked** file. `baseline-measures.md:72` already names this false pass.
- S006 `teaches` still says "the doc basis for a read-only census". CE1 falsifies that reading. `source-draft.md:44` proposes the narrowing, but it is still PENDING while the status is already `mined`.
- S005 `teaches` ends "table may change and is not for machine parsing, lines and nul (-z) are". The installed page states only the negative for `table` (`git-repo.1.gz` roff :166). The "better suited for being parsed" text (roff :73) belongs to `repo info`, not `structure`. The whole command is "EXPERIMENTAL. THE BEHAVIOR MAY CHANGE" (roff :44), and no key-stability promise exists for `structure --format=lines`. The installed man page sha256 is `71a61384…065f`.
- This is the r12 K5 defect class: a Gate claiming a fixture that does not exist (`corpus/lessons/round-12-verifier-spotcheck.md:13`). The draft Q17 in the modified `corpus/QUALITY.md` would reject it.

## Smallest safe correction: admissible narrow scope

The F2 entry may claim, and only claim, the following:

> On git 2.55.0 (record `git --version`), `git repo structure --format=lines` was run with these settings:
> - `GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1 -c maintenance.auto=false`
> - isolated config (`GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null`, `HOME` in the mktemp dir)
> - against a **complete (non-promisor) repository** in a `/var/tmp` fixture
>
> In that run it left the `.git` file set and contents unchanged and issued no write-class syscalls. It reports counts and sizes of objects reachable from `refs/` only: not HEAD, reflogs, index or unreachable objects. It is a ref-reachable-volume census. It is not a reclaimable-space measure, not a receipt, and not removal authorization.

The probe and the entry must also state the following:
- **Could-not-evaluate** (never numbers) when `git config --get extensions.partialClone` is set, when any `remote.<name>.promisor=true`, on rc≠0, or on any stderr byte. CE2 shows the stderr check alone is insufficient: case C emitted nothing.
- Always set `GIT_NO_LAZY_FETCH=1`. Cite git(1) § ENVIRONMENT `GIT_NO_LAZY_FETCH`, not S006, as the no-write control.
- Record `git rev-parse --git-common-dir` so that worktrees sharing a store are not summed.
- Q2 grounding: add a code-tier SOURCES row (id for L1 to assign; `source-draft.md` already proposes S034 for something else) citing `builtin/repo.c@v2.55.0:744,:798-801,:872,:930` and `path-walk.c@v2.55.0:146`, following the S009 pattern.
- S006 `teaches`: narrow it to "skips optional lock-taking sub-operations; not a read-only guarantee", or keep S006 `queued` and leave it out of `used-by`.
- S005 `teaches`: drop "lines and nul (-z) are" [for machine parsing]. Replace it with "no stability promise; EXPERIMENTAL; pin the version".
- PROVINCE: revert "acquired r13" and the "Core now includes" paragraph until the files exist and the fixture has run green. Moving F2 into Core is a boundary change, so its owner should decide it rather than a mid-flight write. F2 stays frontier either way.

## Evidence required before admission (exact checks for L1)

1. `test -f tools/souji-repo-structure.sh && test -f tests/fixtures/r13-repo-structure.sh && test ! -L tests/fixtures/r13-repo-structure.sh`. Then `git ls-files --error-unmatch` on both after the commit, so that untracked files cannot satisfy the gate (Q17).
2. `grep -c 'TMPDIR:-/tmp' tests/fixtures/r13-repo-structure.sh` → 0; `grep -c '/var/tmp' …` ≥ 1; `grep -n 'trap' …` ≥ 1 (Q4).
3. `grep -n 'GIT_NO_LAZY_FETCH=1' tools/souji-repo-structure.sh` ≥ 1, plus a partial-clone refusal check (`extensions.partialClone` / `remote.*.promisor`).
4. `bash tests/fixtures/r13-repo-structure.sh --selftest` must cover, at minimum:
   - (a) plain repo: manifest unchanged, rc 0, metrics present;
   - (b) a `--filter=tree:0` clone from a local `file://` upstream with `uploadpack.allowFilter=true`: the probe reports could-not-evaluate **and** the `.git` manifest is unchanged. This is the discriminating case: a naive probe goes red (writes, undercounts), the corrected probe goes green;
   - (c) a bogus or non-repo path rejected;
   - (d) a detached-HEAD-only commit asserted absent from `objects.commits.count`, which pins the documented scope.
5. `--probe <baseline>`: running the fixture against a probe without `GIT_NO_LAZY_FETCH` and without the promisor refusal must fail case (b). That shows the red→green delta is causal.
6. `shellcheck -S warning` on both scripts → 0 (Q9).
7. Recompute the SOURCES census after the cell edits, against HEAD-extracted and post-commit SOURCES (`baseline-measures.md:83`).
8. `grep -n 'verification.json' corpus/knowledge/git-repo-structure-readonly.md`: the cited path must exist and be committed, or the citation must be removed. `verified-at:` must name `git 2.55.0`.

## Limitations
- One host, git 2.55.0-1, local `file://` promisor only. No https promisor or credential path was exercised. That risk is [INFERENCE].
- Not tested: bare repos, `--separate-git-dir`, shallow clones, reftable ref storage, alternates, submodules, hooks, concurrent writers.
- Case B passed only because every blob was checked out. A `blob:none --no-checkout` clone with history blobs absent was not run; source `:798-801` predicts a silent blob undercount without a fetch [INFERENCE].
- The `count_objects` undercount mechanism in case C (`OBJECT_INFO_QUICK`) is not verified.
- Manifests compare names, sizes and contents only. Transient writes were caught by strace, not by the manifest (case C `maintenance.lock`).
- I did not run, build or lint any lane tool, and I did not review SizeProbe code (absent). The reviewed draft entry, PROVINCE, SOURCES and QUALITY edits are mid-flight, uncommitted working-tree state as of this review.

## Reproduction (scratch script, deleted after the run; core lines)
```bash
T=$(mktemp -d /var/tmp/souji-r13-attackcov.XXXXXX); trap 'rm -rf -- "$T"' EXIT
export HOME="$T/home" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_OPTIONAL_LOCKS=0 LC_ALL=C
G() { git -c maintenance.auto=false -c gc.auto=0 "$@"; }
G init -q -b main "$T/up"; mkdir -p "$T/up/d"
for i in 1 2 3; do head -c 4096 /dev/urandom | base64 > "$T/up/d/f$i"; G -C "$T/up" add d; G -C "$T/up" commit -qm c$i; done
G -C "$T/up" config uploadpack.allowFilter true
G clone -q --no-checkout --no-local --filter=tree:0 "file://$T/up" "$T/pt"
find "$T/pt/.git" -type f | wc -l                                   # 28
strace -f -qq -e trace=execve,openat -o "$T/s" \
  git -C "$T/pt" -c maintenance.auto=false repo structure --format=lines; echo rc=$?   # rc=0
find "$T/pt/.git" -type f | wc -l                                   # 40
GIT_NO_LAZY_FETCH=1 git -C <fresh tree:0 clone> repo structure --format=lines   # rc=0, 'error: bad tree object' ×3, trees=0
```
