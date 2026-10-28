# R40scout53 — C2 operability attack

Seat: R40scout53 (scout). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Read-only on lane bytes. No production file, frozen claim, git index, or jj change. No package install (pacman paused; nothing else required).

Named edge: **`json-symlink-resolved` vs the wrapped `JSON-UNWRITABLE` continuation** (`refused` and `O_NOFOLLOW` sit only on the second physical line of that class entry).

This is the committed fixture case `json-symlink-resolved`, not the preregistration's synthetic wrapped-trigger probe.

Axes walked: commit-bound bytes, a pair the r39 one-line extractor never stores, runtime of that pair, and a kill the current bytes already meet.

## Verdict

**Falsifier.** On the committed r39 drift bytes, joining the `JSON-UNWRITABLE` continuation produces a class entry whose symlink clause disagrees with observed runtime.

- Joined entry: a symlinked `--json` path component is a failed write, refused by the `O_NOFOLLOW` walk, class `JSON-UNWRITABLE`.
- Observed runtime of a leaf symlink (the fixture's own case, re-run here): exit 0, stderr empty, JSON written at the realpath target, `JSON-UNWRITABLE` absent.

An r40 analyzer that joins continuation lines and then requires every observed class/trigger pair to match runtime fails this pair on the pristine r39 tool. An analyzer that only detects a synthetic token on the following line can pass while this pair stays wrong. The kill sentence in the frozen predicate ("any observed class mapping disagrees with runtime behavior") already fires for this pair. No r40 counter exists in the tree yet (`census/round-40/` contains only `preregistration.txt`).

LSP: no `lsp` tool is mounted in this session. Call sites below are from a file-scoped search and a full read of `census/round-39/c2-counter.py`.

## Frozen predicate attacked

`census/round-40/preregistration.txt` lines 7–8 (untracked at measurement; text read from that path):

> r40 L4 docstring analyzer joins wrapped continuation lines into one class entry and verifies all observed class/trigger pairs in the frozen list; a synthetic wrapped-trigger probe is detected while the r39 one-line analyzer misses it. Control: r39 `docstring_classes` extracts only the first class line. Kill if wrapped trigger is missed, or if any observed class mapping disagrees with runtime behavior.

The preregistration names "the frozen list" and does not enumerate a single class/trigger pair.

## Control: what r39 actually extracts

Definition: `census/round-39/c2-counter.py` `docstring_classes` lines 133–144. Callers: lines 227–228 only (search of that file for `docstring_classes`).

The function keeps the first docstring line that starts with `RECORD-MISSING` or `RECORD-MALFORMED`. It never stores `JSON-UNWRITABLE`.

Committed bytes used for every probe below:

- Revision: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (preregistered round-39 tip). `git merge-base --is-ancestor` of that rev against `HEAD` returned 0.
- `HEAD` at measurement: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`. `git diff --stat 02420859 HEAD -- tools/souji-worktree-drift.py census/round-39/c2-counter.py` printed nothing.
- `git -C <lane> rev-parse --show-toplevel` printed `/home/vgpnk/Projects/shokunin/souji-shokunin` before the fixture `git init`.
- Drift blob `02420859:tools/souji-worktree-drift.py` = worktree `git hash-object` = `5a2b32941bc5c3da628ee92f75be1c33192ca311`. sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` (matches the drift half of `census/round-39/records/c2-after.txt` `tool_sha=…/e48ed08e6728`).
- Counter blob `953810db16fa0f7f308311b0aa65a49ad1d80223`, sha256 `732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11`.
- Fixture blob `02420859:tests/fixtures/r38-drift-write-envelope.py` identical to the worktree, sha256 `d6fed4af1e8a17b7d87febb95192a9394ea9b891e322b3d0f538465577738efd`.

`euid=1000`. Scratch `TMPDIR=/fast/scratch/hyaku/souji-r40/R40scout53` (removed after this report was written).

## The continuation

Module docstring of `tools/souji-worktree-drift.py` at the revision above, file lines 59–60 (docstring line index 57, from `ast.get_docstring(..., clean=False).split("\n")`):

```
  JSON-UNWRITABLE        the --json write failed (including a symlinked path
                         component, refused by the O_NOFOLLOW walk)
```

Measured split (`measure_exists_clause.py` entry dump):

- Physical line 1 contains `symlinked` and `failed`. It does not contain `refused` or `O_NOFOLLOW`.
- Physical line 2 contains `refused` and `O_NOFOLLOW`.
- `tokens_only_after_first_line=O_NOFOLLOW` for the token set that dump checked. `refused` is on line 2 only (visible in the `repr` of that line).

Joined entry: the `--json` write failed, including a symlinked path component refused by the `O_NOFOLLOW` walk.

The writer does not walk that spelling. `run` resolves first (`tools/souji-worktree-drift.py` lines 313–319):

```python
json_target = os.path.realpath(os.path.abspath(args.json))
```

`open_nofollow` then walks `json_target`. A symlink already collapsed by `realpath` is not a component of that walk.

## Runtime of the observed pair

Committed fixture `tests/fixtures/r38-drift-write-envelope.py` lines 26 and 240–250 name the case `json-symlink-resolved` and state that a `--json` leaf symlink is written at its resolved path, and that the case asserts that contract rather than a refusal.

Re-run on the extracted r39 tool (`/fast/scratch/hyaku/souji-r40/R40scout53/souji-worktree-drift-r39.py`, bytes of `git show 02420859:tools/souji-worktree-drift.py`), euid 1000, `TMPDIR` the scratch dir:

1. `git init -q -b main` of `/fast/scratch/hyaku/souji-r40/R40scout53/leaf-fleet/alpha` (rc 0). `git -C` that path `rev-parse --show-toplevel` printed that same path before and after the commit. Toplevel stayed under the scratch dir.
2. One commit of `file.txt` (`git -C <fixture> add` rc 0, `commit -qm base` rc 0). Author identity came from the process environment, not `git config`.
3. Record `REPO alpha regs=1 prunable=0` plus a matching `TOTAL` row.
4. `symlink-out` → `/fast/scratch/hyaku/souji-r40/R40scout53/symlink-target.json` (target absent before the run). `readlink` confirmed that target. After the run, `readlink` was unchanged, `symlink-target.json` was a regular file (`islink` false), and the link was still a symlink.

Command:

```
python3 -B <extracted drift> --root <scratch>/leaf-fleet --record <scratch>/leaf-record.tsv --timeout 20 --skip-unrecorded --json <scratch>/symlink-out
```

Output:

```
LEAF_RC=0
LEAF_STDERR=
LEAF_STDOUT=SUMMARY record=.../leaf-record.tsv record_repos=1 record_regs=1 record_prunable=0 live_repos=1 live_regs=1 live_prunable=0 drift_rows=0 unreachable=0
TARGET_ISFILE=True TARGET_ISLINK=False LINK_STILL_SYMLINK=True
JSON_UNWRITABLE_IN_OUTPUT=False
TARGET_BYTES_HEAD={  "drift": [],  "summary": {   "drift_rows": 0,   "live_prunable": 0,   "live_regs": 1,   "live_repos": 1,   "record":
```

A parent symlink shows the same follow. Earlier in the same scratch, `linkdir` → `realdir`, `--json <scratch>/linkdir/out.json`, record row `missingrepo` (so the run also prints an `ABSENT` drift row):

```
PROBE rc=1 class=NO-CLASS
  stderr=
  stdout=DRIFT	ABSENT	missingrepo	recorded regs=0 | SUMMARY record=.../good.tsv ... drift_rows=1 unreachable=0
JSON_CREATED=True
```

`rc=1` is the drift-row exit after a successful write (`return 0 if not drift else 1`). Stderr was empty. The file landed at `realdir/out.json`. Class was not `JSON-UNWRITABLE`.

A self-symlink loop does refuse, so the class is not dead. `json-loop` readlink was `/fast/scratch/hyaku/souji-r40/R40scout53/json-loop`. `--json <scratch>/json-loop/out.json` on the same clean fleet:

```
LOOP_RC=2
LOOP_STDERR=REFUSAL JSON-UNWRITABLE: [Errno 20] Not a directory: 'json-loop'
LOOP_STDOUT=SUMMARY record=.../leaf-record.tsv ... drift_rows=0 unreachable=0
```

The joined sentence does not distinguish that loop from the leaf the fixture already observes. The leaf is the observed pair, and it is a successful write.

## Why the r39 control cannot catch it

`docstring_classes` on the extracted drift file returned only:

```
R39_LINE RECORD-MISSING exists_in_line=False
  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
R39_LINE RECORD-MALFORMED exists_in_line=False
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
```

`JSON-UNWRITABLE` is absent from that map, so L4's `"EACCES" in line` / `"missing" in line` checks (`c2-counter.py` lines 230–238) never read `refused` or `O_NOFOLLOW`. The r39 control misses this pair because the class is outside the hardcoded token set, and the disagreement's mechanism words are on the continuation line the control drops.

`census/round-39/records/c2-after.txt` L4 is `PASS missing=RECORD-MALFORMED locked=RECORD-MISSING`. That pass uses the two first lines above. It is silent on `JSON-UNWRITABLE`.

## Bounded measurement for the r40 counter

Run against candidate bytes and against `0242085909fb6a4ee041c5443d76316ac6d59d4b`, tool extracted with `git show <rev>:tools/souji-worktree-drift.py` into an explicit scratch directory. Pass condition for "joined entry agrees with runtime" on this pair:

| probe | path shape | result on r39 bytes (measured) | agreement with the joined `JSON-UNWRITABLE` sentence |
|---|---|---|---|
| leaf symlink | `--json` is a symlink to a nonexistent regular path outside `--root` | rc 0, target is a regular file, stderr empty, no `JSON-UNWRITABLE` | disagrees |
| parent symlink | a parent component of `--json` is a symlink to a real directory outside `--root` | file created at the real directory, stderr empty | disagrees |
| self-symlink component | `--json` parent is a symlink to itself | rc 2, `REFUSAL JSON-UNWRITABLE: [Errno 20] Not a directory: 'json-loop'` | this shape matches the class and still does not match the leaf |

Kill the operability predicate if the counter's frozen list treats "symlinked path component" / `O_NOFOLLOW` as a `JSON-UNWRITABLE` trigger and the leaf probe is anything other than a recorded disagreement. A list that omits the pair leaves the kill sentence unmeasured: the preregistration does not contain the list.

Fixture anchor already in the tree: `tests/fixtures/r38-drift-write-envelope.py` case `json-symlink-resolved` (lines 240–250). Re-running that single case is enough for the leaf row. The parent row and the loop row are the two shapes that stop the sentence from being read as "every symlink refuses" or "no symlink refuses".

## Adjacent pair from the same docstring walk

Not this seat's named edge. Recorded because the same extractor run measured it, and it is another continuation the r39 map drops.

`RECORD-MISSING` file lines 44–45. Line 2 is the only line containing `exists`:

```
  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
                         exists but cannot be opened or read
```

`R39_LINE RECORD-MISSING exists_in_line=False`. The open branch (`tools/souji-worktree-drift.py` lines 133–136) maps every `OSError` other than `ENOENT` to `RECORD-MISSING`. Probes on the extracted tool, empty `--root` under scratch, `--skip-unrecorded --timeout 5`:

| probe | open errno | `os.path.exists` | tool |
|---|---|---|---|
| absent path | `ENOENT(2)` | False | rc 2 `RECORD-MALFORMED` `is not a regular file` |
| mode-0 regular file | `EACCES(13)` | True | rc 2 `RECORD-MISSING` `[Errno 13] Permission denied` |
| `not-a-dir/child.tsv` with `not-a-dir` a regular file (`PARENT_IS_REG=True`) | `ENOTDIR(20)` | False | rc 2 `RECORD-MISSING` `[Errno 20] Not a directory` |
| child of a mode-0 directory | `EACCES(13)` | False | rc 2 `RECORD-MISSING` `[Errno 13]` |
| symlink to itself | `ELOOP(40)` | False (`lexists` True) | rc 2 `RECORD-MISSING` `[Errno 40]` |
| 300-byte component | `ENAMETOOLONG(36)` | False | rc 2 `RECORD-MISSING` `[Errno 36]` |

The joined sentence says the path exists. The `ENOTDIR` path does not exist (`exists` and `lexists` both false) and is still `RECORD-MISSING`. Joining line 2 is what adds `exists` to the class entry. The r39 stored line does not contain it.

Depth bound, same walk: `RECORD-MALFORMED` is three physical lines (file lines 46–48). `TOTAL` is only on line 3 (`tokens_only_after_first_two_lines=TOTAL`). A record `REPO foo regs=1 prunable=0` plus `TOTAL repos=2 regs=1 prunable=0` returned rc 2 `RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows`. A joiner that appends only the next physical line still misses `TOTAL`. `--root` for `RECORD-OUTSIDE-ROOT` is only on line 2, and `REPO ../outside-marker` returned rc 2 `RECORD-OUTSIDE-ROOT` with the resolved path outside `probe-root`. That pair agrees once line 2 is joined; the `TOTAL` pair agrees only if the join keeps line 3.

## Commands

Lane checks (read-only; toplevel printed the lane):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 0242085909fb6a4ee041c5443d76316ac6d59d4b
git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 0242085909fb6a4ee041c5443d76316ac6d59d4b HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 0242085909fb6a4ee041c5443d76316ac6d59d4b HEAD -- tools/souji-worktree-drift.py census/round-39/c2-counter.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin hash-object tools/souji-worktree-drift.py
```

`HEAD` was `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`. Ancestor rc was 0. Diff stat was empty. Both blob hashes were `5a2b32941bc5c3da628ee92f75be1c33192ca311`.

Docstring split and the errno probes:

```
TMPDIR=/fast/scratch/hyaku/souji-r40/R40scout53 python3 -B /fast/scratch/hyaku/souji-r40/R40scout53/measure_exists_clause.py
```

The script `git show`s the drift and counter blobs at `02420859` into the scratch dir, reprints `docstring_classes`, and runs the probes above. `worktree_drift_identical=True`. Full probe table is in the adjacent section. Scratch script was removed with the scratch dir after these outputs were copied here.

Leaf and loop re-run: inline Python in that scratch dir, `git show` of the fixture blob for the sha256, then the `git init` / commit / `--json` invocation quoted above. Fixture toplevel was asserted equal to `leaf-fleet/alpha` before the commit.

## Limits

The loop refusal is `ENOTDIR` on the component name, measured once. No attempt to race a symlink into the path between `realpath` and `open_nofollow`. That race is the walk the code comment at lines 314–317 describes; it was not timed. The leaf result does not depend on it.

No r40 analyzer was executed, because none is committed. The falsifier is the predicate applied to the r39 bytes the predicate names as its control.
