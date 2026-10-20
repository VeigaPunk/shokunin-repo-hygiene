# souji r13 w1 — BaselineMeasures (SoujiR13.BaselineMeasures)

Full measurement record and reproducible commands: `census/round-13/baseline-measures.md` (lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`).

## Behavior
Read-only baseline capture. No build, lint, test, or tool execution. No commits. Only writes: the measurement file above and this report.

## Baseline (HEAD `31984f473ce4bdab61a99b16cca194b28108cb81`)
- Tracked files: 1574 (`git ls-files | wc -l`).
- SOURCES registry: 33 rows, malformed 0, duplicate ids none, tier A=29 B=3 C=1, status **mined=16 queued=15 rejected=2**. S005 and S006 are `queued`, used-by `—`.
- New evidence validator: **absent** (no tracked file matching `evidence|validat` outside operator-sweep and `tests/vault`).
- Bounded quarantine calls: **absent** (`timeout` count in `tools/souji-quarantine.sh` at HEAD = 0; no FIFO/device/socket test; `tests/fixtures/r13-quarantine-bounds.sh` missing).
- F2 entry: **absent at HEAD** (`corpus/knowledge/` = 6 tracked entries, none matching `size|structure|sizer`).

## Gates
- None run. Proposed L1 checks are listed in `census/round-13/baseline-measures.md` §4.

## Touched surfaces
- Written: `census/round-13/baseline-measures.md` (new file; the directory was created by a sibling seat at 02:12 and holds `before.json`, which I did not touch), `.ufo/waves/round-13/w1/BaselineMeasures.md`.
- Read: `corpus/SOURCES.md`, `corpus/README.md`, `PROVINCE.md`, `tools/souji-quarantine.sh`, `census/round-12/*`, `census/round-10|11/cert-16.json`, `LOG.md`, `corpus/lessons/round-12-verifier-spotcheck.md`, `corpus/knowledge/` listing.

## Findings
1. **Working tree is not HEAD.** Sibling seats have uncommitted edits: `corpus/SOURCES.md` (S005/S006 → `mined`, used-by the untracked F2 file), `PROVINCE.md`, `corpus/QUALITY.md`, and an untracked `corpus/knowledge/git-repo-structure-readonly.md` (sha256 `48ff065f…`, 02:12:39 -0300). Working-tree status reads mined=18 queued=13. Baseline numbers are HEAD numbers.
2. **Stale round-12 snapshot.** `census/round-12/sources-census.txt` and `after.txt` record mined=18 queued=13 at `d7266c5`; HEAD is mined=16 queued=15 after `2a363a0` (S024, S025 mined→queued).
3. **Existence check passes on untracked files.** The used-by check (`census/round-12/sources-census.sh` line 16) uses `[ -e ]` on the working tree, so an untracked F2 file can satisfy a mined row. L1 should run it against a HEAD extract.
4. **Operator-sweep directory is not the only untracked path.** The assignment says it is; `git status` shows `.ufo/` (three round-13 wave files created 02:11) and `census/round-13/` as untracked too.
5. **Duplicate digest definitions in the quarantine tool.** `file_sha` and `dir_digest` are defined at lines 184/186 and again at 722/727; `content_digest` is at 196. The later definitions win in bash. This is observed; whether it changes FIFO behavior is [INFERENCE] until a fixture runs.
6. **No timeout anywhere in the quarantine tool.** Stage-2 `git -C "$crepo" mv` (line 529) and `mv --` (line 536) have no bound. `LOG.md:372-378` and `LOG.md:434-435` record the historical hang as log text only; no timing was reproduced.
7. **Source census "ok" label is text only.** The lesson asserts "census ok"; `tools/souji-census.sh:192` prints `ok` from a different (secret-shape) classifier. No stored registry-census stdout exists.
8. **Cert relays differ by round.** `census/round-10/cert-16.json` sha256 `662294df…`, `census/round-11/cert-16.json` sha256 `71840919…`. Which one, if either, equals an installed artifact is not measured here.

## Out-of-scope items
- No validator, quarantine, fixture, or F2 entry was created or edited.
- No sibling file was edited. The `census/round-13/before.json` written by another seat was left alone.
- Operator sweep contents were not read (see deviation below).

## Deviation (disclosed)
My first probe was an unscoped regex over the whole lane. Its output included lines from `census/operator-sweep-20261018/` and `census/operator-sweep-20261019/`, contrary to the rule that probes must not scan operator-sweep content. I did not open, quote, or rely on those contents. The same search could have touched `tests/fixtures/case-F10/` (credential-shaped fixture); I did not read it. Later probes were scoped.

## Tool installs and updates
None. Tools used were already present: git 2.55.0, awk, grep, sha256sum, ls.

## Artifact paths
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/baseline-measures.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/BaselineMeasures.md`

## Suggested checks for main agent (after all seats land)
- `git -C <R> rev-parse HEAD` and `git -C <R> status --porcelain=v1 --untracked-files=normal` (confirm sibling edits are committed or excluded).
- Source census on a HEAD extract: run `census/round-12/sources-census.sh` lines 4–16 in the extract. Expect 33 / 0 / A=29 B=3 C=1 / mined=16 queued=15 rejected=2, and empty dup, enum, and missing-path output.
- Validator and quarantine absence/presence: the `ls-files` grep and `grep -c timeout` / `grep -nE '^(file_sha|dir_digest|content_digest)\(\)'` in §2 of the measurement file.
- Cert relay re-hash against `662294df…` and `71840919…`.
