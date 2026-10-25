STATUS: PASS

PASS on the frozen C1 enumeration for this slice: **assertions=7 resolved=7 skipped=9 mismatches=0** (6× class A, 1× class B, 0× in-cell class C) over `SCORECARD.md` `## Capabilities` data rows 11–15, measured at `4edb25dfe262515d0da63224bbba71e02e36cba5`. No `mismatch:*` row exists in this slice, so no class repair is owed; three out-of-enum defects (F1–F3) and one boundary observation (F4) are disclosed below rather than folded into the verdict.

Evidence census (one row per token): `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap3.tsv` (46 token rows = 7 assertions + 39 skipped, plus a header block).

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
    --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format counts
assertions=56 resolved=53 skipped=33 mismatches=3          # exit 1, whole file
$ … --rev HEAD --format counts
assertions=56 resolved=56 skipped=36 mismatches=0          # exit 0, whole file
```

## Measured revision and slice

- Measured revision: `4edb25dfe262515d0da63224bbba71e02e36cba5` (`git cat-file -e 4edb25d…^{commit}` → rc 0). Lane HEAD during this audit: `70af563c3086d5799a7fdaf988ba3b687f3b128c`.
- Slice: `SCORECARD.md` `## Capabilities` data rows **11–15 = base-rev lines 55–59** (header line 43, separator 44; row index counted as `45→row1 … 55→row11 … 59→row15`, matching the partition convention of `AuditCap1` for rows 1–5).
- The five rows are **byte-identical** at base lines 55–59 and HEAD lines 60–64 (`sed -n '<n>p' | sha256sum` per row → all five pairs equal: `ffa0f64c…`, `3e567d03…`, `9c53cb25…`, `5ced9f18…`, `edbeea9a…`). Line numbers moved +5 because `SCORECARD.md` grew after the freeze (`git diff --stat 4edb25d HEAD -- SCORECARD.md` → `15 insertions(+), 6 deletions(-)`). The TSV uses base-rev line numbers so it addresses the measured revision.
- Token inventory of the slice: 15 backticked spans, exactly one bare 7-hex token (`5fa6017`), **zero** 64-hex tokens (`grep -oE '\b[0-9a-f]{64}\b'` → empty), zero `:<line>`-suffixed paths, two glob spans. No 4-digit year token occurs; `rNN` are round ids.

## Exact command per class (all read-only; no writes to the lane, no git/jj writes)

| class | command | observed |
|---|---|---|
| rev exists | `git -C . cat-file -e '4edb25d…^{commit}'` | rc 0 |
| A — single path | `git -C . cat-file -e '<rev>:<path>'` (presence) + `git ls-tree -r <rev> --name-only \| grep -Fxq -- <path>` (membership) | 5/5 path spans PRESENT |
| A — glob | `git ls-tree -r <rev> --name-only` (3545 entries) → `fnmatch` the glob | `census/round-17/jj-receipts-*.txt` → 2 matches (`jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt`) |
| B — revision token | `git -C . cat-file -e '5fa6017^{commit}'`; `git rev-parse '5fa6017^{commit}'`; `git rev-parse --disambiguate=5fa6017 \| wc -l`; `git merge-base --is-ancestor 5fa6017 4edb25d` | rc 0 → `5fa6017ddcae9f6bd4412df44765f6360cb16294`; disambiguate=1; ancestor-of-base=yes |
| C — digest | `git show <rev>:<path> \| sha256sum` | **0 in-cell 64-hex assertions**; command defined but unexercised in this slice |
| in-cell C scan | `grep -oE '\b[0-9a-f]{64}\b'` over lines 55–59 | empty |

Class A resolutions: `corpus/lessons/round-16.md` (line 55, line 56), `census/round-16/c1-matrix-final.json`, `census/round-21/oracle-acceptance.json`, `census/round-17/c1-matrix-4f48343.json`, and the `jj-receipts-*.txt` glob. All six A-class cells at base lines 55–59 resolve; the single B-class token resolves.

Excluded tokens, each with its reason in the TSV: 9 spans fall outside class A (`error`, `info/attributes` ×2, `status.showUntrackedFiles`, 3 command spans, `refs/jj/*`), `4f48343` is not a *bare* hex token (it sits inside a backticked filename), and the remaining rows are counts, exit codes, round ids, and `S###` source ids. No token was silently dropped.

## Executed non-class corroboration (observations, never class verdicts)

- Line 55 (exit-2 refusals): the cited `census/round-16/c1-matrix-final.json` records `arms.changed.r15-config.total=20 failed=0` with `observed_exit=2 / observed_finding=path-protected:include-protected` cases → consistent with the claim.
- Line 56 (`18/18`, `15/15`): `corpus/lessons/round-16.md:21` states "Self-test 18/18; synthetic fixture `tests/fixtures/r16-landing-gate.py` 15/15". Numbers hold; the same lesson records at `:76` an independence caveat ("two cases pass with the named mechanism dead") that the scorecard row does not repeat.
- Line 57 (`oracle2372 keys over192 files, tp3/fp0/fn0`, `all401`): `census/round-21/oracle-acceptance.json` → `files=192`, `oracle.labelled=2372`, `oracle.tp=3`, `oracle.fp=0`, `oracle.fn=0`, `prior_verdicts` length 401. Counts corroborated; tuple *identity* not re-derived by me.
- Line 58 (`29/0`): cited `census/round-17/c1-matrix-4f48343.json` → `arms.changed["r17-hygiene"] = {total:29, failed:0, rc:0, valid:true}`.
- Line 59 (`35/0`, `13 fail`): `census/round-17/jj-receipts-4f48343.txt` → `SUMMARY total=35 failed=0 skipped=0`; `census/round-17/jj-receipts-base5fa6017.txt` → `CASE` tally PASS=20, SKIP=2, **FAIL=13** (20+2+13=35), matching "(5fa6017 tools: 13 fail)".
- Source ids cited by the slice resolve: `S043 S045 S046 S047 S049 S050 S054 S060` each have exactly one row in `corpus/SOURCES.md` at the base rev (supplementary to the frozen classes).

## Repairs

**No repair rows: the slice has zero `mismatch:*` tokens.** The three whole-file mismatches at the base rev — line 3 `AXES.md`, line 63 `reason-after.txt`, line 77 `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` — lie outside rows 11–15 and belong to other slices. At HEAD they are gone: line 63→68 now resolves against `census/round-21/reason-after.txt` (genuine path repair), line 77 is rewritten to disclose absence, and line 3 is discussed in F4.

Optional hardening (not owed; would *add* class-B assertions, each verified to resolve, without deleting any capability claim):

- Row 11's `measured commit` cell names only `r16`/`r14`. Its own receipt `census/round-16/c1-matrix-final.json` records `lane_head=0a70beff3becff2c64944595860a31fc6e193076` (resolves, ancestor of base, 2026-10-20). Naming that revision makes the row's measurement pinnable by class B.
- Row 12 could name `4f48343` (lane head recorded by `census/round-17/gate-replays-4f48343.json`) or `d98065d` (`gate-landing.json resolved_rev`); both resolve.
- Row 14 could name `4f48343` (= `c1-matrix-4f48343.json lane_head`); row 15 could name `5fa6017`/`4f48343`, the two receipts it already cites.
- Row 13 is the one gap with no receipt-side anchor: `census/round-21/oracle-acceptance.json` carries **no** `lane_head`/`rev` field (keys: `calls, classes, files, inputs, oracle, prior_verdicts, prior_verdicts_sha256, read_root, rows`). The minimal truth-preserving repair is the *missing committed receipt*: add the measurement revision to that JSON (or name it in the cell). The only revision the committed prose pins for r21 is the landing commit `f2248c026bcce5f3a919fa6ac57cd8d9ca18cffa` (resolves, ancestor), which is **not** the same thing as the oracle's measurement revision — do not substitute it silently.

## Findings

**F1 — medium, operability/reproducibility (executed).** `git ls-tree` in this environment does not expand wildcard pathspecs, and it fails silently (rc 0, no output) instead of erroring:

```
$ git ls-tree -r 4edb25d --name-only -- 'census/round-17/jj-receipts-*.txt' | wc -l   → 0
$ git ls-tree -r 4edb25d --name-only -- '*.md' | wc -l                                → 0   (3545 tracked files)
$ git ls-tree 4edb25d --name-only corpus/round-17/ | wc -l                            → 14  (literal dir pathspec works)
$ git ls-files -- '*.md' | wc -l                                                      → 1334 (other commands' wildcards work)
```
A re-derivation that checks class-A globs with a git pathspec would report `mismatch:path-absent` for a glob that in fact matches 2 tracked files — a false red, and a trap for anyone auditing the C1 counter. The canonical tool is safe because it lists the whole tree and `fnmatch`es locally (`Repo.tracked` + `fnmatch`), which I reproduced: 2 matches. Any independent check of C1 must copy that method, not the pathspec form.

**F2 — low, coverage (executed).** 9 of the slice's 15 backticked spans fall outside class A, including three command spans that contain **four** repo-relative paths (`tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py`, `tests/fixtures/r17-census-hygiene.py`, `tools/souji-census.sh`, plus `tests/fixtures/r17-jj-receipts.sh`). All five are present at the measured rev, so no claim is false — but the frozen enum never asserts them, and the rows' four normative numeric claims (`18/18`, `15/15`, `29/0`, `35/0`) are uncheckable by any frozen class. Consequence for the round's claim: `M_after = 0` means "no enumerated token fails", **not** "every declared claim in these rows is machine-verified". That reading must be stated wherever C1's target is reported.

**F3 — low, calibration/wording (executed).** Line 57's `literal32/32 (base18/32)` — the counts are corroborated (`corpus/lessons/round-21.md:7` "baseline18/32 versus changed32/32"; `:192` "read32/32, renderer4/4"), but the qualifier `literal` is not a category name in any committed receipt (`grep -oE 'literal[0-9]+/[0-9]+'` over `census/round-21/` and `corpus/lessons/round-21*` → no hits). Minimal truth-preserving repair: write `read32/32 (base18/32)` — keeps the numbers and the capability, drops the unsupported label. `renderer4/4` is verbatim supported (`:192`).

**F4 — boundary, outside this slice (executed; for the C1 owner).** The base-rev mismatch at line 3 (`AXES.md`, `mismatch:path-absent`) is repaired at HEAD by replacing the repo-relative token with `/home/vgpnk/Projects/shokunin/AXES.md` (file exists, 5160 B, 2026-10-16). That token now fails class A's repo-relative shape and falls into `skipped` — so this one mismatch leaves `M` by leaving the enumerated class, not by resolving inside it. It is one of the three that `M_before=3 → M_after=0` depends on. The preregistration permits "drops the evidence role of the token" as a repair; a fleet-root absolute path arguably retains the evidence role while evading the class. Whoever lands C1's calibration row should say which of the two it is, or pin the assertion to a lane-relative pointer.

## Residual risk and verification gaps

- I did **not** execute `18/18`, `15/15`, `29/0`, `35/0` (selftests/fixtures); they are corroborated only from committed receipts, and the r16 lesson itself records an independence caveat for two of its 15 fixture cases.
- `all401 old tuples identical` — count corroborated (`prior_verdicts` = 401); the identity comparison was not re-derived.
- Class C is unexercised in this slice (no 64-hex token), so the slice provides no evidence about digest re-derivation.
- The glob assertion is pattern-fragile: renaming `census/round-17/jj-receipts-*.txt` would break it; it is resolved today, so no repair is owed.
- Whole-file `M` moved during the round: base 3, HEAD 0. My slice contributes 0 at both. HEAD also moved between seats (`AuditCap1` measured `2a130b4`; I measured `70af563c`) — the five slice rows are byte-identical at every point measured. The worktree `SCORECARD.md` was edited by another seat at 03:51 while this audit ran (2 insertions/2 deletions, not touching rows 11–15); every token here was read from committed objects, never from that worktree copy.
- No mutating cleanup, no process signalling, no deletion authority, no writes outside `.ufo/waves/round-22/attempt2/w1/AuditCap3.md` and `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap3.tsv`. No tool installed or updated in this seat; `git 2.56.0` and `python3` (stdlib only) were already present.
