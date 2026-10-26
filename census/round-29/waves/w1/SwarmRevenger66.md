## Status
STATUS: PASS — the r28 C3 failure is a single causal chain, reconstructed from committed bytes and reproduced end-to-end in scratch; all checks below were run this seat. One closure figure diverges (15 symlinks claimed, 14 measured).

## Evidence
Lane revs: base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; capture commit `765fe8bd602ac679d01e7a0790711485209ab8bd`. All git calls read-only (`log/show/diff/ls-tree/cat-file/status/check-ignore/ls-files`).

- `git show 765fe8b -- .gitignore` → new file, 3 lines: `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`. The ignore file and the r26+r27 capture land in the **same commit**.
- `git ls-tree -r 691dd29 census/round-26/waves` → 1245 paths = 1231 regular + 14 symlinks (mode 120000).
- Manifest vs committed tree at 691dd29 (script decoding GNU escapes, comparing `ls-tree`/`cat-file`): `records=1382 missing=152 present=1230`; `failed` blobs = 0, so every failure is a *path absent from the commit*.
- `git check-ignore -v --no-index` per missing path, grouped:
  - 138 `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:1:fixture/` (depth 8)
  - 4 `.gitignore:3:__pycache__/` (depth 0, unanchored → matches at every depth)
  - 4 `…/vault/case-V6/.gitignore:6:/ledger*.tsv` (depth 8)
  - 2 `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:2:shims/` (depth 8)
  - 1 `…/vault/case-V6/.gitignore:4:/src/` (depth 8)
  - 1 `…/vault/case-V6/.gitignore:5:/vault/` (depth 8)
  - 1 `…/tests/fixtures/case-F7/repo-tree/.scratch/.gitignore:1:*` (depth 10)
  - 1 `…/tests/fixtures/case-F8/repo-tree/.scratch/.gitignore:1:*` (depth 10)
  - total 152. The 5th nested ignore, `…/fixtures/.gitignore` (`tests/fixtures/*/repo/`), matches nothing (its slash-bearing patterns are relative to its own directory, so they point at a non-existent `tests/fixtures/tests/…`).
- `git status --porcelain census/round-26/waves` → 0 lines; `git status --porcelain --ignored=matching census/round-26/waves` → 12 `!!` entries covering exactly those 152 files. Visibility, not byte state, is what changed.
- `git ls-files | grep __pycache__` at HEAD `b8cb4b3` → 5 tracked: 4 under `.ufo/waves/round-26/assimilation/validate/tools|tests/fixtures/__pycache__/` and `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`.
- `git ls-tree -r --name-only b8cb4b3 .ufo/ | wc -l` → 3016 tracked files under `.ufo`; `.ufo/waves/round-26` alone 1218.
- Sizes on disk: `.ufo/waves/round-26` = 1381 regular files + 17 symlinks (NUL-counted); `census/round-26/waves` = 1383 regular files (= 1381 + manifest + summary). Manifest has 1382 lines because two names contain newlines and are GNU-escaped one-per-line; both escaped records are present in the tree.
- Scratch reproduction (`/var/tmp/souji-r29-SwarmRevenger66.*`, removed after the run): copy of the tool on a synthetic lane with one nested `.gitignore` (`fixture/`), one `__pycache__/*.pyc`, one symlink, root `.gitignore` written before `git add`:
  `tool_rc=0` then `add_rc=0`, `porcelain_lines=0`, `manifest_minus_committed:` `pyc/__pycache__/x.pyc`, `sub/fixture/on-disk-only.txt`, and `--verify` afterwards still prints `captured+verified`, `verify_rc=0`. The symlink committed but never entered the manifest (the uncovered class).
- `git cat-file -e 50443f5:<path>` for three r26 paths: `case-V6/ledger-crlf.tsv` ABSENT, `vadv-49/fixture/a1/source/link.txt` ABSENT, `fixtures/__pycache__/r26-axis-check.cpython-314.pyc` present.
- `sha256sum --version` → `sha256sum 0.8.0` (uutils); r28 `c3-after.tsv` → `round26_sha256sum_check=rc0; 1380 OK; WARNING 2 improperly formatted newline-path records`.
- r28 frozen C3 counter, `census/round-28/records/preregistration.txt:9`, verbatim: "a missing or non-verifying manifest for a claimed round" (the only verification-quality word in the kill rule).
- Capture tool, `tools/souji-wave-evidence-capture.sh:73-75`, verbatim: "Symlink entries are copied verbatim (never dereferenced) and, like the frozen recipe's `find -type f`, are not part of the manifest hash set."
- Fixture, `tests/fixtures/r28-wave-evidence-capture.sh:126-127`, verbatim: "supplementary (not a case): symlink entries are preserved verbatim, never dereferenced, and sit outside the manifest hash set".
- r29 counter floor, `census/round-29/c2-counter.py:34`: `FLOORS = {'26': 1230, '27': 124, '28': 75}`.

## Findings

### 1. Causal chain (numbered, each step with its evidence)
1. **r26 evidence tree is committed with fixture-owned ignore files inside it.** `50443f5` (r26 wave assimilation) adds 1218 files under `.ufo/waves/round-26`, including 5 `.gitignore` files copied from the `assimilation/validate` self-test tree (`tests/vault/vadv-49/.gitignore`, `tests/vault/case-V6/.gitignore`, `tests/fixtures/case-F{7,8}/repo-tree/.scratch/.gitignore`, `tests/fixtures/.gitignore`). Evidence: `git ls-tree -r 50443f5 .ufo/waves/round-26 | grep -c 'vadv-49/fixture'` → 0, while the same files exist in the wave source.
2. **Those same nested rules already dropped 148 files at r26, silently.** Measured: of the 152 paths absent at 691dd29, **148 are also absent from `50443f5:.ufo/waves/round-26/<same path>`**; the only 4 that *were* present there are the `__pycache__` `.pyc` files, which stayed tracked until the r28 rule made their census twins uncommittable. Sample: `git cat-file -e 50443f5:.ufo/waves/round-26/assimilation/validate/tests/vault/case-V6/ledger-crlf.tsv` → absent; `…/vadv-49/fixture/a1/source/link.txt` → absent. The drop is not an r28 creation; r28 only re-exposed it in a new destination.
3. **r28's instrument copies the disk tree verbatim.** `cp -a -- "$src/." "$dst/"` (`tools/souji-wave-evidence-capture.sh:100`) carries the nested `.gitignore` files, the ignored-by-design fixture artifacts, the 17 symlinks and the `__pycache__` into `census/round-26/waves`.
4. **The manifest is built from `find . -type f` on the receipt.** `tools/souji-wave-evidence-capture.sh:157-159`; 1382 records, including every `.gitignore`-ignored file that exists on disk and excluding every symlink by construction (line 73-75 comment).
5. **Root `.gitignore` is added in the same commit as the capture** (`765fe8b`), and its third line `__pycache__/` is unanchored, so it also applies inside `census/round-26/waves/…`: 4 more records become uncommittable. (Before r28 there was no root ignore file: `git show 765fe8b -- .gitignore` is a pure addition; r27's `gitignore-draft.md` records `.gitignore` as non-existent at `e78ac7c`.)
6. **`git add` (index/commit-tree assembly) is the step that creates the 152 absent records.** It applies root + nested ignore rules, skips the matched paths with exit 0, and reports nothing; `git status --porcelain` then shows an empty tree because the skipped files are `!!`. Reproduced in scratch: `add_rc=0`, `porcelain_lines=0`, 2 of 5 manifest records absent from the commit.
7. **Every verification before the closure compared disk to disk.** Tool `--verify`: recompute hashes over `find . -type f` in `$dst` and `cmp` to the stored manifest (`:174-176`), then compare source-vs-receipt hash *multisets* (`:184-190`) — both sides are the same on-disk tree. No `ls-tree`, `cat-file`, `check-ignore`, `ls-files` appears anywhere in the tool. After the drop the tool still printed `captured+verified` (scratch run, `verify_rc=0`). The closure was the first check to read committed bytes (`git archive` + `sha256sum -c`) and it fired: r26 `ok=1228`, 152 "FAILED open or read".

### 2. Why the r28 fixture could not see it — what each check compared
| check | location | what it compared | blind to |
|---|---|---|---|
| case 1 | `r28-wave-evidence-capture.sh:46-69` | tool rc + `summary.tsv` line count | nothing about git |
| case 3 | `:77-98` | manifest byte-flip on disk → `--verify` rc 4 | a *missing member* caused by git, not by tampering |
| cases 2/4/5/6 | `:72-75,100-106,107-111,112-124` | rc codes for missing src, fifo, traversal, empty dir | ignore semantics |
| supplementary (explicitly "not a case") | `:126-146` | asserts `in-link` is **not** in the manifest | encodes the omission as a requirement: a symlink record would be scored a FAIL |
| seat runs (r28 w1) | `SwarmExecutor14.md:11`, `c3-after.tsv` | `sha256sum -c` in the receipt directory on disk | commit content; and uutils 0.8.0 keeps rc 0 across 2 unparsed lines |
| post-commit seat check | `SwarmExecutor16.md:7` | `git status`, `rev-parse`, `ls-remote`, file sizes | ignored files are invisible to `git status` |
| frozen C3 counter | `census/round-28/records/preregistration.txt:9` | `git status` dirty count, `test -s manifest`, fixture 6/6 | verifiability of records |

The fixture never creates a git repository (all cases run under `${TMPDIR:-/var/tmp}` mktemp dirs), so the one behaviour that actually breaks — ignore rules at `git add` — is structurally untestable by it.

### 3. Why the symlinks are uncovered (14, not 15)
- 17 symlinks exist in the source wave tree; `cp -a` preserves all 17 in the receipt.
- 3 are dropped by `vadv-49/.gitignore:1:fixture/` (verified with `check-ignore -v` on `a1/source/link.txt`, `a2/source/link.txt`, `a4/vault/copy.txt`) — so 14 are committed.
- All 14 committed symlinks carry no manifest record, because the manifest is `find -type f` (line 74) and the fixture *requires* that a symlink not leak into it (`:139`). `census/round-26/waves/symlinks.tsv` does not exist at 691dd29, so the r29 counter's only exemption path is unavailable → `uncovered=14`.
- Divergence: `corpus/lessons/round-28-verifier-spotcheck.md:80` says "15 tracked r26 receipt paths (symlinks …)". Measured at both `fec846d` and `691dd29`: 14 (`git ls-tree -r … | grep -c '^120000'`); census-wide symlinks at 691dd29 = 14. The closure's 15 is not reproducible; the uncovered count (14) is.

### 4. Intent of the three `.gitignore` additions, and what a safe narrower rule looks like
- `.ufo/waves/` — keep ephemeral wave evidence (seat reports, dispatch json) out of git now that `census/round-N/waves/` is the durable receipt (r28 prereg line 9: capture into "a committable `census/round-<N>/waves/` receipt"). Root-anchored by construction (pattern contains `/`). Intent sound, but ineffective for the past: 3016 files stay tracked under `.ufo` at HEAD, and it converts 163 visible dirty paths into invisible ones rather than removing them.
- `census/operator-sweep-*/` — keep operator-sweep contents (read-forbidden) out of git. Root-anchored; cannot reach into `census/round-N/waves/`. No defect.
- `__pycache__/` — keep bytecode untracked (r27 draft intent: "`__pycache__/` + `*.pyc`", `census/round-27/waves/w1/gitignore-draft.md:11-12`). **Unanchored**, so it matches at every depth, including inside receipts. This is the one rule of the three that bit the capture (4 records).
- Safe narrower form: anchor bytecode rules to the code trees, e.g. `/tools/__pycache__/`, `/tests/fixtures/__pycache__/`, `/census/round-10/__pycache__/`; never add a slash-free name pattern (`__pycache__/`, `*.pyc`) at lane root while `census/` holds receipts. Note that no ignore pattern can rescue the 148 nested-fixture records — those must be handled by the capture tool (`git add -f` for captured paths, or an explicit `excluded.tsv` carrying each matched rule), which is the r29 contract's "accounted as excluded, never silently dropped".
- Asymmetry proving the mechanism: the same four `.pyc` bytes are *tracked* under `.ufo/waves/round-26/…/__pycache__/` (committed at 50443f5, before any ignore existed) and *absent* at the identical path under `census/round-26/waves/…/__pycache__/` (committed after the ignore existed). Ignore state, not content, decides.

### 5. Earlier rounds with the same defect in a different surface — yes, three
- **r26, `.ufo/waves/round-26` evidence commit `50443f5`**: 148 of the r26-missing entries were already absent there (`vadv-49/fixture` count 0; `case-V6/ledger-crlf.tsv` absent), committed with the nested `.gitignore` files that caused it. Same mechanism, different destination, four rounds earlier. r26's C3 receipts could not see it either: `census/round-26/records/c3-{before,after}.tsv` are tool-presence receipts (`axis_check_tool=absent` → `present`), with no byte binding to any tree.
- **r27, pre-report gate**: `tools/souji-pre-report-gate.sh:34-36` decides "clean" from `git --no-optional-locks -C "$lane" status --porcelain=v1 --untracked-files=all`. Success is *absence of visible change* — exactly the predicate that a `.gitignore` satisfies without changing bytes. r28's C3 counter (`git status … | awk` on `.ufo/waves`) is the same instrument shape, which is why the frozen counter could not detect the 152 (they were never `??`, they were `!!`).
- **r27, pycache premise**: `census/round-27/waves/w1/ExecPycacheFix.md` records that the intended hygiene check fails at base (`census/round-10/__pycache__/…pyc` tracked), `.gitignore` absent, and that untracking needs `git rm --cached` outside a read-only seat. The deferred remedy shipped in r28 as the unanchored `__pycache__/` line, i.e. the r27 defect's fix became the r28 drop's cause; the tracked `census/round-10` pyc is still tracked at HEAD.
- Control surface: the other five committed hash manifests (`census/round-16/transcripts/MANIFEST.sha256` 144, r18 170, r20 ×3 64/64/64) verify with `failed=0` — the manifest instrument itself is sound where the tree carries no ignore files or symlinks. The defect is specific to evidence trees containing fixture-owned ignore files/links.

### 6. The r29 floor is calibrated on the broken count
`census/round-29/c2-counter.py:34` sets the r26 floor to **1230**, which is exactly the post-drop record count measured at 691dd29 (1382 − 152). A re-capture that re-drops the same 152 files therefore still satisfies `floor_violations=0`; only the `failed`/`uncovered` arms catch it. (Stated as a property of the frozen instrument, not a proposed change.)

### 7. Pre-existing lane state (not mine, untouched)
`git status --porcelain` at base shows one modified tracked file: `.ufo/waves/round-26/w1/ScribeGateDraft.md`. No write, revert or classification performed.

## Minimal design rule that would have prevented it
**No receipt record may name a path that git will not commit at the destination, and no verifier may resolve a record through the filesystem.**

Machine-checkable form, two predicates over the destination `census/round-N/waves/`:
1. capture: for each planned record `p`, `git -C <lane> check-ignore --quiet --no-index -- "census/round-N/waves/$p"` must be false, or `p` must be written to `excluded.tsv` with the matched `file:line:pattern`; symlinks are recorded in `symlinks.tsv` with their targets. Silence is a failure (non-zero exit), not a note.
2. verify: recompute the record set from the object database at a named rev (`ls-tree` + `cat-file`), never from `find`/`cp` output; a record that does not resolve at the rev is a failure.

Cheapest sufficient guard for the r28 commit: a post-capture `git add -n`/`git ls-files --others --ignored --exclude-standard census/round-N/waves` must be empty, and the root ignore file must contain no slash-free name pattern that can reach `census/`.

## Deliveries
- `.ufo/waves/round-29/w1/SwarmRevenger66.md` (this report). No other file written; scratch removed.
