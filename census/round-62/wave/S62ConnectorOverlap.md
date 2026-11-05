# S62ConnectorOverlap — sibling-overlap scan, souji round 62 (C1: index-flag concealment vs receipt writer)

Read-only everywhere: no sibling tool executed, no writes outside this seat's delivery dir, no git/jj
mutation anywhere (read-only `rev-parse`/`ls-files` in the lane only). Scratch
`/fast/scratch/hyaku/souji-r62/S62ConnectorOverlap/` created then removed before yield.

## Baseline re-verified (ran every cited command)

| command | observed | exit |
|---|---|---|
| `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` | `16fa821fdce00e709d6895ccfc7aaffa465af195` (= round base) | 0 |
| `git -C <lane> ls-files \| wc -l` | `17350` | 0 |
| `git -C <lane> ls-files -v \| cut -d' ' -f1 \| sort \| uniq -c` | `17350 H` — zero non-`H` tags | 0 |

The frozen precondition holds: an unconditional non-`H` refusal blocks no honest run on today's lane.
Surface read `tools/souji-receipt-write.py:131-133` (behaviour 7): `git status --porcelain` alone;
refusal class `lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override`
— matches the round claim byte-for-byte. `tests/fixtures/r60-receipt-write.py` present (`ls` exit 0).

## Hit table (scope = */tools, */corpus/knowledge, scripts/hyaku)

| path | lane / owner | decision | evidence |
|---|---|---|---|
| `souji-shokunin/tools/souji-receipt-write.py` | souji (this lane) | **souji-owned — C1 surface** | dirty check porcelain-only (`:131-133`); PROVINCE.md:3-4 "receipt-gated removal" domain |
| `souji-shokunin/tools/cand-d1-{census,quarantine,vault,verify}.sh` | souji | **souji-owned — the predicate already exists in-lane** (r10 cluster-D closure): `ls-files -v` non-`H` → refuse, classes `index-flag-assume-unchanged` / `index-flag-skip-worktree` / `index-flag-skip-worktree+assume-unchanged` / `index-flag-<tag>`; unreadable index → `index-unverifiable rc=` (cand-d1-quarantine.sh:707-749); scoped `-- pathspec`, receipt scope only |
| `souji-shokunin/tools/souji-idx-repair.py` | souji | souji-owned index writer; PROVINCE.md:63-76 ("`git status --porcelain` never empties" host; repair via `update-index --add --cacheinfo`, r48). Its `--cacheinfo` entries default to `H` — cannot trip C1's refusal |
| `souji-shokunin/corpus/knowledge/skip-worktree-concealment.md` | souji | **souji-owned — C1 is its routed fix**: S291; r61 HIGH-1; `:34-36` "refuses any skip-worktree or assume-unchanged entry (`git ls-files -v` lowercase or `S`). Neither is implemented in round 61: this is named and routed to round 62, not claimed" |
| 103 souji tools using `porcelain` (impl-40, souji-census, souji-quarantine/-vault-verify, souji-verify*, cand-merge-*, cand-d2-verify, impl-42 …) | souji | souji-owned; temp-index plumbing (`GIT_INDEX_FILE … update-index -q --refresh` + `diff-index`) is tree/fixture plumbing, not flag ground |
| `kasegi-shokunin/corpus/knowledge/considerthese-proposals-ledger.md:156` | kasegi (sibling) | sibling names the exact class; says its `g-gate.py:113` porcelain check "does not cover the three mechanisms `corpus/instruments/r41-closure.sh:1392-1405` names (gitignored entries, `assume-unchanged`/`skip-worktree` markers)". **No PROVINCE claim line for it** (kasegi PROVINCE hits are CSAF/NVD "flags", not git index flags). Instrument verified: `corpus/instruments/r41-closure.sh` `worktree_state()` (`:1392-1405`) counts `S`/lowercase `ls-files -v` tags; comment: "`git status --porcelain` alone misses all three mechanisms (the round-40 wave-2 F8 escape)" — sibling closed this class for its own closure gate in r41 |
| `kaidoku-shokunin/tools/round-29/prefile-check.sh:6,22`; `round-46/prefile-gate.py:107-109`; `round-46/gate.py:134`; round-40/41/42/43 counters (fixture-clean checks) | kaidoku (sibling) | sibling-owned porcelain-only clean-tree gates; index-flag blindness unnamed in kaidoku PROVINCE.md (sweep showed no clean-tree/index-flag line) |
| `kama-shokunin/tools/pre-report-gate.py:38,666` (arm 6 round-clean), `round72-round-scope.py:22-26,253`, `round73-round-scope-cases.py:23-40` | kama (sibling) | sibling-owned; PROVINCE.md:314-315 claims them: "plus `worktree`, `ignored-older-label` and `submodule`; the pre-report gate's arm 6" — porcelain-only, flags unnamed |
| `mori-shokunin/tools/mori-index-clean.sh` (+ 7 more mori porcelain tools) | mori (sibling) | sibling-owned index-state reporter: porcelain v1+v2 cross-check for intent-to-add (`:53-78,110-113`); no `ls-files -v` flag check |
| `mado-shokunin/tools/mado-tripwire.py` | mado (sibling) | adjacent (1 porcelain file in tools) |
| `tameshi-shokunin/tools/trace-inputs.py:19` (`ls-files -z --cached --full-name`), `executor-source-pin-measure-v2.py:217` (`update-index --chmod=±x`), `design-blob-audit.py`, `mutate-and-run.sh` | tameshi (sibling) | adjacent: ls-files without `-v` tags; fixture index writes — not the concealment ground |
| `tsukuroi-shokunin/tools/receipt-write.py` + `receipt-run.py` | tsukuroi (sibling) | **no overlap**: the writer chain performs no git clean-tree/index check at all (pattern sweep `status|dirty|clean|porcelain|diff-index|ls-files|skip-worktree|assume-unchanged|update-index` → zero hits). PROVINCE.md:8-9 owns pacman `.pkg.tar.zst` receipt discipline, not this |
| `chousa-shokunin/tools/receipt-pin.py`, `digest-in-tree.py` | chousa (sibling) | adjacent-complementary: receipt provenance verifiers (header/blob consistency; pinned digests re-derive from committed bytes). They catch receipts pinning uncommitted bytes but do not see flag-concealed divergence of the instrument itself. chousa PROVINCE.md contains zero occurrences of "receipt" (`grep -c` = 0) — tools unclaimed in province |
| `kotodama-shokunin/tools/gates/**/freeze.txt` (9 files) | kotodama (sibling) | freeze receipts asserting `git status --porcelain tools/gates/` empty — porcelain-only, adjacent |
| `scripts/hyaku/{closure-prompt.md:26, inline.sh:157,172, jj-lane.sh:179,387,491,721, jj-lane-selftest.sh, lane-addendum.md:314}` | **fleet-tooling** (not a lane) | all porcelain-only leftover/dirty checks in the dispatcher/closure path; no `skip-worktree`/`assume-unchanged`/`ls-files -v` anywhere in hyaku. C1's class applies to the fleet's own closure gates too (e.g. inline.sh:172 lane-dirty warning) — report, don't absorb |

Per-lane file counts matching `porcelain` in tools (bash `grep -rl`, complete, exit 0): kaidoku 15,
kama 5, kotodama 9, mado 1, mori 8, souji 103, tameshi 2; hyaku 5 files.

## Package check (shokuknow, read-only)

`/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` read in full once. Term sweep
`skip-worktree|assume-unchanged|index.?flag|ls-files|porcelain|dirty|receipt|clean.?tree|update-index`
over the file: only "receipt" matches, all in quarantine-taxonomy rows (`duplicate-receipt-class-decision-r25/r26`,
`origin-record-writer-r27` — GLib origin-record durability), a different receipt domain. Zero hits for
skip-worktree, assume-unchanged, index flags, porcelain, ls-files, update-index, clean tree. Package
themes: git auto-maintenance/prune/grace period, quarantine staging, duplicate verdicts, origin records,
reclamation deadlines, near-duplicate thresholds, community worktree literature.

## Recommended assimilation line

`Assimilation: none — the staged souji package (134 rows, 68 entries, rounds 1-16) holds no index-flag, skip-worktree, assume-unchanged, porcelain or clean-tree theme; its only 'receipt' rows cover quarantine receipt taxonomy (duplicate class, origin-record writer), not the receipt writer's clean-tree check; C1's ground is already souji-owned (S291 re-opened, S292; r61 HIGH-1 routed to round 62 in corpus/knowledge/skip-worktree-concealment.md).`

## Non-obvious move (connector synthesis)

C1's frozen predicate is the **third fleet implementation of a twice-established concealment rule**,
applied to the one surface that mints honesty receipts — no sibling owns or claims it, so the L1 has a
clean integration line:

1. kasegi r41 `worktree_state()` — counts `S`/lowercase `ls-files -v` tags (report-and-grade, its closure gate).
2. souji r10 cluster-D `cand-d1-*` helpers — refuse on any non-`H` tag inside the receipt scope, named classes, `#rc=` sentinel for unreadable index.
3. C1 candidate — refuse **unconditionally** (`--allow-dirty` cannot override) on any non-`H` tag across the whole lane index, before behaviour 7.

Counter cross-check hooks for the frozen matrix (rows D/E/F/G): tag semantics are identical to
cand-d1-quarantine.sh:740-744 (`H` pass; `h` assume-unchanged; `S` skip-worktree; `s` both; anything
else → `index-flag-<tag>`), so the counter can reuse cand-d1's expected-class strings; kasegi's awk test
(`t == "S" || t ~ /[a-z]/`) selects the same population as an independent second reader.

Second-order effects: runtime is one index read over 17350 entries (no worktree walk, no measurable
latency); the unconditional refusal is stricter than both precedents, justified because a receipt
attests worktree bytes — fail-closed turns silent concealment into a named refusal. Named risks:
(a) jj-colocated lanes — souji PROVINCE.md:25-30 records "the git index is not a signal" there (jj
rewrites the index on snapshot); a receipt minted on such a lane with non-`H` residue would be refused
— fail-closed, and today's lane is plain git (17350 `H` verified); (b) souji's own idx-repair writes
`--cacheinfo` entries that default to `H`, so the lane's repair tool cannot trip the refusal;
(c) an operator deliberately skipping generated files gets refused — exactly matrix row F's intent
(a clean claim cannot be verified under the flag).

## Limits

- Scan scope = the assignment's three roots; `corpus/instruments/`, `.ufo/`, `census/`, `plans/` not swept except the targeted verification of kasegi's cited instrument (`r41-closure.sh:1387-1413` read) and the C1 surface.
- The `receipt` term matches 166+ files; classification done at file level via narrower sweeps (`allow.dirty|worktree is dirty` → only souji-receipt-write.py; `receipt-write` name → souji + tsukuroi). Both complete.
- `porcelain` census is complete file-level counts; the grep tool paginates content matches at 20/file on large files (counts unaffected).
- kasegi ledger's `g-gate.py:113` citation not independently opened; `r41-closure.sh` verified.
- Sibling tools never executed; PROVINCE quotes are current worktree bytes at the verified HEAD.
