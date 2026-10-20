STATUS: DONE — vadv54-run is a round-4 commit that captured a harness run's residue; the empty `p6repo/.git` was a run-time repo-root marker that no committed verdict depends on at rest, and quarantining it changes no committed result or census field.

# RevengeStubOrigin — provenance and evidence impact of `tests/vault/vadv54-run/p/p6repo/.git`

Scope: reconstruction only. No file in the lane was edited; no harness or tool under test was executed
(PROBE RULE). Evidence below is from read/stat/sha256sum/`bash -n` and read-only git on named paths.
No tools installed or upgraded.

## 1. Which round/commit added the tree

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --diff-filter=A \
    --format='%h %ad %s' --date=iso -- tests/vault/vadv54-run
48a64d8 2026-10-18 15:09:36 -0300 round-4 (amended): obsidian claim withdrawn by operator;
        ledger-verify tool installed (impl-20, d312263a), CLI findings banked
```

- One commit only: `git rev-list --count HEAD -- tests/vault/vadv54-run` → `1`;
  `git log --name-status` for the tree and the harness lists `48a64d8` with 30 `A` rows
  (`tests/vault/vadv54-harness.sh` + the 29 fixture files). No later commit touches either path.
- Commit `48a64d8` parent `78694ac`, on `master`; HEAD is the assignment base `5fa6017`.
- Round: **r4**, adversarial seat S54 (`vadv54-harness.sh:1-24`: "seat S54 adversarial probes, round 4";
  `tests/results/vadv-54.json` `"round": 4, "seat": "S54"`).
- The committed tree is a **run product, not hand-authoring**: file mtimes are `2026-10-18 14:51`
  (harness itself `14:09`), commit is `15:09`; `q/led-p.tsv` embeds absolute `/home/vgpnk/...` source
  and vault paths plus run-computed digests. The harness rebuilds `$SCRIPT_DIR/vadv54-run` from scratch
  on every invocation (`vadv54-harness.sh:47 rm -rf -- "$WORK"`, `:49-52` mkdir, then fixture writes).
- Because git cannot track an empty directory, `p6repo/.git` was **never in the commit**. It existed only
  as at-rest residue from the 14:51 run: my first `ls -la` at the start of this seat showed the directory
  present with mtime `Oct 18 14:51` (size 0).

## 2. Why `p6repo` has an empty `.git` (harness `:176` semantics)

As built at HEAD (`5fa6017`, harness sha `966ee19a…`):

```
:47  rm -rf -- "$WORK"
:63  dir_digest() { ... find . -path './.git' -prune -o -type f -print0 ... }
:176 mkdir -p "$P/p6repo/.git" "$P/p6repo/inner"
:177 printf 'p6 payload one\n'   > "$P/p6repo/one.txt"
:178 printf 'p6 payload inner\n' > "$P/p6repo/inner/keep.txt"
:193 P6_DIG=$(dir_digest "$P/p6repo")
:194 P6I_DIG=$(dir_digest "$P/p6repo/inner")
:208 printf '... vault-nested-in-source\n' "$P/p6repo" "$P6_DIG" "$P/p6repo/inner" "$P6I_DIG"
:274 run_tool "$LED_P" "$P/p6repo"
```

Case semantics:

1. P6's oracle is `vault-inside-source`: the ledger row names a "vault" copy (`p6repo/inner`) living
   inside the artifact that would be removed (`p6repo`), so SAFE would destroy the copy
   (`vadv54-harness.sh:284-287`).
2. The `.git` exists so the fixture also **classifies as a repo root** for the tool's directory branch:
   `[ -d "$target" ] && [ -d "$target/.git" ] → evaluate_repo_root`
   (r2 tool `9435e46:tools/souji-verify.sh:381-382`; r4 tool `tools/souji-vault-verify.impl-20.sh:549-551`;
   current `tools/souji-verify.sh:421-423`). P6 therefore tests the nested-vault rule on the branch that
   treats a directory as a repository, not only on a plain directory artifact.
3. It is **empty on purpose/consequence**: (a) both digest implementations prune `./.git`
   (`vadv54-harness.sh:63-65`; tool `:155-167`; impl-20 `dir_digest`), so a stub contributes zero bytes
   to `P6_DIG`; (b) no `HEAD`/index/objects means every `git -C p6repo` query fails, so the repo-root
   fallback would report `unpushed=0 dirty=0` — the verdict stays attributable to the ledger rule, not to
   repo dirtiness; (c) an empty directory cannot be committed, so it can only ever be residue.
4. Cost of that marker: jj treats `p6repo/` as a nested repo and reports the two tracked files as deleted
   (`D p6repo/one.txt`, `D p6repo/inner/keep.txt`); a directory pathspec jj commit commits those deletions
   (`/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md:76`), and removal is the
   documented pre-colocation step (`:87`). This is C3(e).

## 3. Do any committed verdicts depend on the stub existing at rest? No.

Three independent proofs:

**(a) Process.** `:47 rm -rf -- "$WORK"` deletes the whole at-rest tree, stub included, before any fixture
is built; any stub a run evaluates is one that same run just created. The at-rest copy is never read.

**(b) Digest equality (empirical, strongest).** The committed ledger row was generated at 14:51 **with**
the stub present:

```
$ awk -F'\t' 'NR>1 {print NR": "$1" | "$2" | "$3" | "$4}' tests/vault/vadv54-run/q/led-p.tsv | tail -2
9: .../p/p6repo | 94bf987aac85a30c27ab0ba79d64f7e6d4c0e2f89109aee52070b804c1b6382b | .../p/p6repo/inner | ae48c282ee80a2f834343018e75f6d0a78a52caeea02d2323f32a3d043819e9c

$ ( cd tests/vault/vadv54-run/p/p6repo && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 )      # stub ABSENT now
94bf987aac85a30c27ab0ba79d64f7e6d4c0e2f89109aee52070b804c1b6382b
$ ( cd tests/vault/vadv54-run/p/p6repo/inner && ...same... )
ae48c282ee80a2f834343018e75f6d0a78a52caeea02d2323f32a3d043819e9c
```

Identical with and without the stub, so every directory-digest input (P0-P6) is stub-invariant.

**(c) Receipt attribution.** P6 rows across all six committed result files
(`tests/results/vadv-54*.json`, row 27 in each):

| file | tool / sha256 | P6 | receipt/verdict text |
|---|---|---|---|
| vadv-54.json | souji-vault-verify.impl-20.sh d4f037fa8ea0 | PASS | `vault-inside-source` (containment rule fired) |
| vadv-54.impl-17.json | impl-17.sh 70c05b60b942 | PASS | `source-equals-vault` / `vault-nested-in-source` |
| vadv-54.impl-21.json | impl-21.sh ed1881e8fd82 | FAIL | SAFE `ledger-row` (no containment rule) |
| vadv-54.souji-vault-verify.impl-20.json | impl-20.sh 52885564f324 | FAIL | SAFE `ledger-row` (mid-write revision) |
| vadv-54.souji-verify.json | souji-verify.sh 7efda63bd760 (r2, `9435e46`) | FAIL | SAFE `ledger=source+vault-digest` |
| vadv-54.souji-vault-verify.impl-24.json | impl-24.sh 2b224647abed | PASS | `source-absent … unreadable` |

The r4 PASS row's receipt is the containment rule, not the repo-root fallback; the FAIL rows are explained
by the tool lacking that rule (`git show 9435e46:tools/souji-verify.sh` contains no `vault-inside` string,
and still has the `-d "$target/.git"` branch at `:381-382`). Every generation calls the ledger/containment
check first inside the repo-root branch (r2 `:292-294`; impl-20 `:456-458`), so the verdict does not change
when the stub is absent and the artifact branch runs instead.

Caveat, marked inference: the stub still changes *which branch runs* at run time. For a hypothetical tool
whose repo-root branch skipped the ledger, the empty stub would yield `NOT-SAFE/none` (0 unpushed/0 dirty)
rather than a false-SAFE — a coverage caveat, not an evidence dependency. That path is not exercised by any
committed tool version [INFERENCE from code reading; tools not executed].

## 4. Does quarantining the at-rest stub change any committed evidence? No.

- **Results JSONs:** static records of tool sha + verdict text; no path or digest in them depends on the
  stub (see §3). A replay is unaffected because a replay recreates the fixture via `:47`/`:176`.
- **Census:** `census/round-7/seat-09.json` row `vadv54-run` records `files 29, bytes 5146, tracked_files 29,
  dirty_lines 0, ignored_children 0, newest_mtime 2026-10-18 14:51`. All of these are stub-invariant:
  - `du -sb -P tests/vault/vadv54-run` now (stub absent) → `5146`, exactly the recorded value. GNU apparent
    size sums regular files only (`du -sb p/p6repo` → 32 = `one.txt` 15 + `inner` 17; the directory's own
    `st_size` is excluded), so an empty directory contributes 0.
  - `git ls-files --others --exclude-standard tests/vault/vadv54-run` → empty; `git add --dry-run -n
    tests/vault/vadv54-run/p/p6repo` → empty. Git never reports an embedded `.git` as untracked, so the
    r17 census D1 dirty count cannot see it either (`tools/souji-census.sh:1020-1041`, `:1070-1076`
    prunes `.git` for `newest_mtime`).
  - `git diff --stat -- tests/vault/vadv54-run` → empty: no tracked fixture byte changes.
- **Caveat, wording only:** `corpus/knowledge/jj-colocation-receipts.md:59` (untracked, new this round)
  states the directory "contains an empty `.git/`" in the present tense. After the quarantine that sentence
  is false at rest; reword to past tense ("contained … until the r17 harness fix") before C3(c) lands. No
  committed bytes are affected.
- **Forward-looking caveat:** the current verify tool refuses a directory target that contains a nested
  `.git` (`tools/souji-verify.sh:417-419`), pruning only the target's own `./.git`. While the stub sat at
  rest, evaluating the parent `tests/vault/vadv54-run` as a target would have returned
  `nested-repo-or-unverifiable`; with it gone that refusal disappears. No committed result file evaluates
  that parent path, so no committed evidence moves. (`tests/vault` overall still holds 7 other nested
  `.git` fixtures under `vadv-49`, per `JjTrialSouji.md:14`.)

## 5. Observed as-built state (file was being edited concurrently)

- `13:33:25` — the at-rest stub was removed (`tests/vault/vadv54-run/p/p6repo` mtime today; `stat
  .../p6repo/.git` → ENOENT). The harness at that moment was still HEAD bytes (`966ee19a…`, having created
  the stub at `:176`), so removal alone was temporary: the next run would recreate it.
- Harness snapshots observed during this read: `966ee19a…` (== HEAD `5fa6017`) → `00370e8e…` at 13:35
  (transient, broken: an insertion before the payload files with a stray literal line `PUT 274.=280.:`,
  which `bash -n` accepts but executes as `PUT: command not found`, and an early P6 record against a then
  nonexistent ledger) → **`b55df92d5eb8589a0696cd9004eea6364033c59852012fd677834450349e42fa`, 13:37:48,
  28077 bytes, final**.
- Final working-tree patch (`git diff`, 10 insertions / 2 deletions):
  - `:176` `mkdir -p "$P/p6repo/inner"` (no `.git` at fixture-build time);
  - `:273-282` P6 block: comment, `mkdir -- "$P/p6repo/.git"` at `:277` immediately before
    `run_tool "$LED_P" "$P/p6repo"` at `:280`, `trap 'rmdir … || true' EXIT` at `:279`, `rmdir` at `:281`,
    `trap - EXIT` at `:282`.
  - `bash -n tests/vault/vadv54-harness.sh` → rc 0.
- This is the durable form of the quarantine: the stub exists only for the P6 evaluation, so P6 still
  exercises the repo-root branch and every committed verdict replays identically, while the at-rest tree
  is clean. `tests/vault/vadv54-run/p/p6repo/` now contains only `inner/` and `one.txt`; 29 tracked files;
  no untracked entries.
- Residual defect in the final patch (smallest fix): the non-empty branch `rmdir … || printf 'refusing…'`
  leaves a nested `.git` at rest if the tool under test writes into it, with exit 0 — the jj hazard returns
  and no case fails. `$P/p6repo/.git` is provably test-owned (`:47` wiped `$WORK`; `:277` created it), so
  use `rm -rf -- "$P/p6repo/.git"` (drop the diagnostic) or turn the refusal into a P6 FAIL.

## 6. Verdict

| question | verdict |
|---|---|
| which round/commit added `tests/vault/vadv54-run` | r4, `48a64d8` (2026-10-18 15:09:36), single commit; tree = residue of the 14:51 harness run |
| why an empty `.git` in `p6repo` | `:176` repo-root marker for the `vault-nested-in-source` case; digest-inert because both digesters prune `.git`; untrackable, so always residue |
| committed verdict depending on the stub at rest | none — `:47` destroys the at-rest tree; digests proven equal; P6 receipts trace to the containment rule |
| quarantining the at-rest stub changes committed evidence | no — 0 results change, census row recomputes byte-identically (`du -sb` 5146), no tracked byte changes; only the untracked knowledge row's tense needs updating |
| as-built fix at report time | run-scoped stub with EXIT trap, sha `b55df92d…`; replace `rmdir` with `rm -rf` on the test-owned path |

Confidence: high on §1-§4 (git/commit facts and digest/byte recomputation are observed, not inferred);
high on the branch-ordering reading (code read in three pinned tool bytes); medium-high on the "hypothetical
ledger-skipping tool" caveat, which is inference and explicitly labeled.

## 7. Exact commands run (evidence)

```
git log --diff-filter=A --format='%h %ad %s' --date=iso -- tests/vault/vadv54-run
git log --format='%h %ad %s' --date=iso --name-status -- tests/vault/vadv54-run tests/vault/vadv54-harness.sh
git rev-list --count HEAD -- tests/vault/vadv54-run
git ls-tree -r --name-only 48a64d8 -- tests/vault/vadv54-run        # 29 paths
git ls-files tests/vault/vadv54-run | wc -l                          # 29
git ls-files --others --exclude-standard tests/vault/vadv54-run      # empty
git add --dry-run -n tests/vault/vadv54-run/p/p6repo                 # empty
git diff --stat -- tests/vault/                                      # harness only
git diff -- tests/vault/vadv54-harness.sh                            # 10 insertions / 2 deletions
git cat-file -p HEAD:tests/vault/vadv54-harness.sh | sha256sum       # 966ee19a…
git show 9435e46:tools/souji-verify.sh | sed -n '285,320p'           # repo-root branch, no containment
grep -n 'vault-inside' tools/souji-verify.sh tools/souji-vault-verify.impl-20.sh
sed -n '200,270p' tools/souji-vault-verify.impl-20.sh                # containment at :243-253
sed -n '395,445p' tools/souji-verify.sh                              # nested-git gate :417-419
sha256sum tests/vault/vadv54-harness.sh                              # b55df92d… (final)
stat -c '%y %s' tests/vault/vadv54-harness.sh                        # 2026-10-20 13:37:48, 28077
bash -n tests/vault/vadv54-harness.sh                                # rc 0
( cd tests/vault/vadv54-run/p/p6repo && find . -path './.git' -prune -o -type f -print0 \
  | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 )     # 94bf987aac85…
awk -F'\t' 'NR>1 {print NR": "$1" | "$2" | "$3" | "$4}' tests/vault/vadv54-run/q/led-p.tsv | tail -2
du -sb -P -- tests/vault/vadv54-run                                  # 5146 (== r7 census bytes)
python3 -c '<P6 verdict table over tests/results/vadv-54*.json>'
```

Not run (forbidden): `tests/vault/vadv54-harness.sh`, `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`,
`tools/souji-census.sh` against any real tree. No network, no credential files, no `jj`, no git write.
