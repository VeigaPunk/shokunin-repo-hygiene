# S65ConnectorOverlap — sibling overlap scan (round 65, read-only)

Scope: `tools/` of kaidoku, chousa, kotodama, tsukuroi, mori; `scripts/` of kumitate and tabi (both lanes have no `tools/` directory: `ls` of kumitate and tabi shows none). `corpus/knowledge/` was searched for the same tokens; hits there are prose and are not listed except where noted. Searches used the read-only grep tool; no sibling file was written and no sibling command was executed.

Verdict key: **souji ground** = the same class as a round-65 claim (C1 visibility/env routing, or the r55 line-model defect); **sibling ground** = the sibling's own scope, no overlap to a souji claim; **neither** = no overlap.

## 1. Status visibility flags (C1 V1/V2 class: `status.showUntrackedFiles`)

| path | what it does | verdict |
|---|---|---|
| kaidoku-shokunin/tools/round-29/prefile-check.sh:22 | `GIT_OPTIONAL_LOCKS=0 git -C "$root" status --porcelain` — no explicit untracked flag, so `status.showUntrackedFiles=no` in config hides untracked paths from the "tree is clean" step (line 6: "no modified, staged or untracked path") | **souji ground** — the concealment class of V1; a config-sensitive false-green of a tree-clean gate. Sibling-lane fact, not a defect of this round's claims. |
| kumitate-shokunin/scripts/round-gate.mjs:91 (doc comment for the TREE_DIRTY error; the check is `git status --porcelain`) | close-time tree check, no explicit untracked flag | **souji ground** — same config-sensitive class as above. Named for kumitate's lane. |
| kaidoku-shokunin/tools/round-25/ruler.py:73 | `git status --porcelain=v1 -z --untracked-files=all` inside a state hash | **souji ground (same mechanism, correct)** — explicit `=all` overrides config, the V1 fix pattern. No defect. |
| kaidoku-shokunin/tools/round-42/prefile-gate.py:107–111 | `_status_z`: `status --porcelain=v1 -z -uall` | **souji ground (same mechanism, correct)** — explicit flag. |
| mori-shokunin/tools/mori-misroot-sweep.py:110 | `status --porcelain=v1 -z --untracked-files=all` (reads untracked bytes) | **souji ground (same mechanism, correct)**. |
| mori-shokunin/tools/mori-unlanded-check.py:58 | `status --porcelain=v1 -z --untracked-files=all` | **souji ground (same mechanism, correct)**. |
| mori-shokunin/tools/mori-round13-regressions.py:1251–1262, mori-round14-regressions.py:396–452, mori-round15-regressions.py:807 | `--untracked-files=all` recorded as evidence scope | **souji ground (same mechanism, correct)** — explicit flag, recorded in evidence. |
| mori-shokunin/tools/mori-pin-check.py:1588, 1617 | `status --porcelain --ignored --untracked-files=all` as the "left-over" check after a run | **souji ground (same mechanism, correct)**. |
| mori-shokunin/tools/mori-index-clean.sh:71, 77, 101 | `status --porcelain --untracked-files=no -z` and `status --porcelain=v2 --untracked-files=no` — deliberately tracked-only (intent-to-add count) | **sibling ground** for its own scope (index-clean is defined over tracked paths). It hides untracked by construction, so it is the concealment class in form; its scope is stated in the script. |
| tabi-shokunin/scripts/check-selfassessment.mjs:482 | `status --porcelain --untracked-files=all` | **souji ground (same mechanism, correct)**. |

No hits for `skip-worktree`, `assume-unchanged`, or `allow-dirty` in any scanned sibling `tools/` or `scripts/` file. `ls-files -v` appears nowhere in the scanned set.

## 2. Environment routing (`GIT_INDEX_FILE` and siblings — C1 P13 class and the named limits)

| path | what it does | verdict |
|---|---|---|
| kaidoku-shokunin/tools/round-25/instrument-custody.py:~98–102 (docstring of the env scrub) | drops **all** `GIT_*` variables ("not a sampled subset"); the names it lists are GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_NAMESPACE | **souji ground** — covers the two env redirects souji's preregistration names as *unread* (GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES) plus GIT_INDEX_FILE. The scrub is a drop, not a refusal, so its policy differs from souji's P13 refusal. Its blanket "all GIT_*" wording also covers GIT_REPLACE_REF_BASE by policy, which souji's named limit leaves unread. |
| kotodama-shokunin/tools/check-claim-separability.py:114–117 | `GIT_LOCATION_VARS` tuple: GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_COMMON_DIR, GIT_NAMESPACE | **souji ground** (same env-routing class). Its explicit list names the three redirects souji's named limit leaves unread; GIT_REPLACE_REF_BASE is not in the tuple as printed. |
| kotodama-shokunin/tools/check-judged-object.py:99–102 | pops GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY from a copied env (GIT_ALTERNATE_OBJECT_DIRECTORIES not popped) | **souji ground** — a partial list of the same shape the prereg's named limit describes. |
| kaidoku-shokunin/tools: round-29 c1-fresh-naming.py:412, c2-filtered-unseen.py:229, prefile-check.sh:18; round-30 axis-fit-gate.py:301; round-31 c1-sqlite-positive.py:252, c2-sqlite-refusals.py:408, cited-runs-gate.py:30; round-32 c1-arm64x-positive.py:91, freeze-integrity.py:27; round-33 freeze-integrity.py:45–49, timestamps/run-gate-hashed.py:41, 241, build-hashed-fixture.sh:17, run-hashed-selftest.sh:11; round-34 freeze-integrity.py:57, 118 | pop or unset GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE (drop, not refuse) on subprocess env | **souji ground** (same env-routing class, drop policy). Several are copies of one helper; no new defect shown. |
| kaidoku-shokunin/tools/round-50/selftest-r49-c2.py:129–130 | sets `GIT_INDEX_FILE=<scratch>/graft.idx` for a fixture | **sibling ground** — writes the variable into its own fixture; not a reader. |

## 3. The r55 line-model defect class (`str.splitlines` versus LF-only numbering)

Souji's `corpus/knowledge/splitlines-line-model.md` (S278) records the defect: a counter whose hidden-line set and reported line numbers come from different line breakers can go dark. Sibling hits:

| path | what it does | verdict |
|---|---|---|
| kaidoku-shokunin/tools/round-59/annotation-audit.py:116 | `lines = text.splitlines()`; `enumerate(lines, start=1)` numbers the command and annotation lines, and every finding cites those numbers. Numbering and reading use the same breaker, so it is internally consistent; it disagrees with an LF-only numbering (`git show`, `sed -n`) only if the receipt holds `\r`, `\x0b`, `\x0c`, `\x1c–\x1e`, `\x85`, `\u2028`, `\u2029`. | **souji ground** — the r55 class. Not demonstrated as a defect here; receipt bytes were not tested. |
| chousa-shokunin/corpus/evidence/round50/stale-count-check.py:26, 37, 69 | `receipt_rows` counts `splitlines()` non-empty rows; `scan(path.read_text().splitlines(), m)` reports line numbers that CORRECTION lines are matched against (`NAMES` regex `:N` / `line N`) | **souji ground** — same class: receipt row count and cited line number use splitlines, while `sed`/`git show` numbering is LF. A `\x1c` in a cell would miscount rows and shift named lines. Not demonstrated. Path is `corpus/evidence/round50/`, not `tools/`. |
| chousa-shokunin/tools/claims-audit.py:100, claims-audit-v2.py:117 | `lines = text.splitlines()`; `next(i for i, l in ...)` reports a line index | **souji ground** (same class) — the line index appears in the audit detail. |
| tsukuroi-shokunin/tools/check-adjacency-overlap.py:249 | iterates `text.splitlines()` with fence tracking (`expandtabs(4)`) | **souji ground** (fence/line-model class). |
| chousa-shokunin/tools/argv-witness.py:334, 338; mechanism-witness.py:282, 286 | parse of a command's own stdout by line | **sibling ground** — parses its own subprocess output; no line-number citation. |
| kaidoku-shokunin/tools/round-26/c1-id-identity.py:114, 158, 183, 233; round-27/c1-rename-identity.py:128, 146, 159 | one family mixes `splitlines()` and `split("\n")` | **souji ground** — mixing the two breakers in one family is the failure shape the r55 entry names. Only the `split("\n")` form is LF-only. A pairing to check, not a defect shown. |

## 4. Other notes

- kaidoku and mori `corpus/knowledge/` and `tools/gates` freeze text contain many `git status --porcelain` prose hits. They document the same checks; they are not code and are not counted.
- The only sibling code that sets `GIT_OPTIONAL_LOCKS=0` beside a status read is kaidoku `round-29/prefile-check.sh:22`. Not a defect.

## 5. Overlap summary

- Shared ground with souji (C1 flags and env routing): kaidoku `round-29/prefile-check.sh` (config-sensitive tree-clean), kumitate `scripts/round-gate.mjs` (config-sensitive close check), kaidoku `round-25/instrument-custody.py` and kotodama `check-claim-separability.py` (env scrub lists that name the redirects souji leaves unread).
- Same r55 line-model class: kaidoku `round-59/annotation-audit.py:116`; chousa `corpus/evidence/round50/stale-count-check.py:26/37/69`; chousa `claims-audit*.py:100/117`; tsukuroi `check-adjacency-overlap.py:249`.
- Nothing in the scanned sibling code shows a defect this round's claims must absorb; the overlap is informational. No sibling file was edited.
