# W2ScorecardDraft — SCORECARD.md and LOG.md appends for round 24 (souji r24 w2)

Seat: L1Souji24.W2ScorecardDraft (scribe, read-only for the lane). Lane tip read this run:
`git rev-parse master` -> `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (wave-1 reports commit on top of
after-receipts `ca7fc1cb6dd1333096c6f3bdbad304686691d126`; `git diff --stat 778747e master` adds only
receipts, the lane census and wave-1 reports). Measured commit for every after-figure:
`778747eb671f8e85ef5387bc3d7023337b30467c`. Controls: `1efe406e7f39b8fe736be2a566053703a571ffc0`.
Base `a65fac98964b445758e94c805728c9a19d302ff8`.

## Status

STATUS: PASS — all three blocks are drafted below, and every number in them was checked against its receipt (see the number-check table). All 9 receipts under `census/round-24/records/` return `verify=ok`. Every receipt's `tool_sha256` equals `git show <rev>:<tool> | sha256sum`. Two draft-relevant defects were found and are kept out of the receipt-backed table. First, `census/round-24/size-census-lane.txt` is not a v1 receipt: `verify` refuses it with `RECEIPT-MALFORMED`. Second, the r23 C2 grep counter now reads 15 at the lane tip, and one of those 15 is that malformed file. The r25 line is drafted from the wave-1 reports and the 3 of 35 wave-2 reports that had landed (W2C2Rerun, W2Misroot, W2SrcPath). Fold the other 32 in when they land.

## Evidence

All commands were run from `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only. Host: git 2.56.0, Python 3.14.

1. Receipt verify, each file (`python3 -B tools/souji-receipt-run.py verify --root . <r>`):
   ```
   c1-after.tsv               verify=ok rev=778747eb… tool=tests/fixtures/r24-size-census.py tool_sha256=373ef1f0…
   c1-control-stub.tsv        verify=ok rev=1efe406e… tool=tests/fixtures/r24-size-census.py tool_sha256=373ef1f0…
   c2-after.tsv               verify=ok rev=778747eb… tool=tools/souji-coverage-agreement.py tool_sha256=71b89eb3…
   c2-control-base.tsv        verify=ok rev=1efe406e… tool=tools/souji-coverage-agreement.py tool_sha256=71b89eb3…
   c2-fixture-after.tsv       verify=ok rev=778747eb… tool=tests/fixtures/r24-coverage-agreement.py tool_sha256=42259756…
   c3-after.tsv               verify=ok rev=778747eb… tool=tests/fixtures/r24-receipt-verify.py tool_sha256=f8c4c391…
   c3-control-base-runner.tsv verify=ok rev=1efe406e… tool=tests/fixtures/r24-receipt-verify.py tool_sha256=f8c4c391…
   gate-check-r24-entry.tsv   verify=ok rev=778747eb… tool=tools/souji-gate-check.py tool_sha256=d5ed0805…
   r13-recheck-receipt.tsv    verify=ok rev=778747eb… tool=tests/fixtures/r13-repo-structure.sh tool_sha256=b6bf5205…
   census/round-24/size-census-lane.txt   RECEIPT-MALFORMED  header order or fences do not match receipt v1   rc=2
   ```
2. Independent digest check: `git show <rev>:<path> | sha256sum` at a65fac9 / 1efe406 / 778747e. The first 16 hex digits match each receipt. Base blobs are the empty-input digest `e3b0c442…`, i.e. absent, for both r24 fixtures, `souji-size-census.py` and `souji-coverage-agreement.py`. The runner `tools/souji-receipt-run.py` is `e13d0c83…` at both a65fac9 and 1efe406, so the C3 control ran the base runner bytes. At 778747e it is `9df0738c…`. `tools/souji-size-census.py` is `09bb8e0d…` at 778747e (`7ad5cc76…` at 1efe406). The C1 receipts bind the fixture, not this tool. The stub `census/round-24/controls/stub-size-census.py` at 1efe406 is `9908b9be…` and is not bound by any receipt.
3. Base absence: `git cat-file -e a65fac9:<p>` fails for `tests/fixtures/r24-size-census.py`, `tools/souji-size-census.py`, `tools/souji-coverage-agreement.py` and `tests/fixtures/r24-receipt-verify.py`.
4. Grounded entries, `git grep -l '^ground: F' <rev> -- corpus/knowledge/ | wc -l`: a65fac9 → 4, 1efe406 → 4, 778747e → 6. `git diff --name-status -M a65fac9 778747e -- corpus/knowledge/` shows `A count-objects-linked-worktree-garbage.md` and `M git-repo-structure-readonly.md`. The diff contains only `+ground:` lines and no `-ground:` line. So all 4 base-grounded entries (2×F2, 2×F4) carry the same F<k> at the tip. F2 grounded: 2 → 4. Tip `.md` entries: 13 (`git ls-tree`).
5. Registry rows, `git show <rev>:corpus/SOURCES.md | grep -cE '^\| ?S[0-9]{3}'`: 119 → 123 (S120–S123 added in 778747e). This count comes from the seat, not from a receipt.
6. Source snapshots: `git archive 778747e census/round-24/sources` into `/var/tmp/souji-r24-W2ScorecardDraft/`, then `sha256sum -c SHA256SUMS` → 6/6 OK. Scratch removed afterwards (`ls` → No such file).
7. Re-run of the r23 C2 counter at master c3ca7ad: `git grep -lE '^tool_sha256=[0-9a-f]{64}$' master -- census/` lists 15 files (at a65fac9: 5; at 778747e: 8). 14 of the 15 return `verify=ok`. The 15th is `census/round-24/size-census-lane.txt` → `RECEIPT-MALFORMED`.
8. Re-run of the r23 C1 counter at the after-state (run by this seat, unreceipted; it is read-only with `--no-worktree`): `python3 -B tools/souji-record-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c --no-worktree` → `keys=4 records=4 occurrences=17 mismatches=0`, rc=0, 35.6 s. `git status --porcelain` was identical before and after.
9. The assimilation Gate in `git show 778747e:corpus/knowledge/count-objects-linked-worktree-garbage.md` (`## Gate` at line 125) has 2 staged-package ADMIT lines (r27 re-sourced, line 140; the r25 five-mode matrix only, line 141). It has 4 REJECT lines (the r25 headline, r26, semantics-r23, and the staged provenance cells; lines 142–145). That is within the prereg bound of "at most 2 admitted, at least 1 rejected".
10. Wave sizes from `w1-spec.json` and `w2-spec.json` `items`:
    - w1: 38 seats (12 scout, 10 executor, 4 critic, 4 scribe, 3 reviewer, and one each of sentinel, simplifier, revenger, mutation-tester and connector).
    - w2: 35 seats (10 reviewer, 10 critic, 6 scout, 4 mutation-tester, 3 sentinel, 2 scribe).

Contract quotes (bytes opened this run):
- prereg line 64: "After target: `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit 0."
- prereg line 90: "After target: mismatches=0 at the landing tip."
- prereg line 111: "Before (control): the base runner -> refusals=0/2. After target: refusals=2/2 regress=5/5, exit 0."
- amendment-1 line 38: "Pinned target line: `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0."
- SCORECARD.md line 134: "re-run the r23 counters at the new tip, and close the residual C1/C2 limits named above."

## Number check (every figure in the drafts below → its source; all checked this run)

| figure in draft | source checked | how |
|---|---|---|
| C1 before: base absent → `cases=0 pass=0` | `git cat-file -e a65fac9:tests/fixtures/r24-size-census.py` fails | executed (Evidence 3). The figure is the contract's definition; no receipt can exist |
| C1 control `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc=1; stub fails cases 2, 3, 5, 6 | `c1-control-stub.tsv` stdout/rc | read + verify=ok |
| C1 after `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc=0; case 3 counts `1,2,0,0` both arms; case 4 `raw_linked_garbage=1`; case 7 `manifest_changed=4` | `c1-after.tsv` | read + verify=ok |
| C2 control `grounded=4 mapped=2 dangling=0 mismatches=2`, rc=1, two MISSING-FROM-MAP rows | `c2-control-base.tsv` (cmd `--rev a65fac9…`) | read + verify=ok |
| C2 after `grounded=6 mapped=6 dangling=0 mismatches=0`, rc=0 | `c2-after.tsv` | read + verify=ok |
| C2 fixture `cases=9 pass=9 control=FALSE-GREEN-REJECTED`; the always-zero control fails 9/9 | `c2-fixture-after.tsv` | read + verify=ok |
| C2 per-entry kill rule holds (4/4 base-grounded, same F<k>) | git diff (Evidence 4); agrees with W2C2Rerun | executed; not a receipt |
| C3 control `cases=8 pass=6 refusals=0/2 regress=5/5`, rc=1 | `c3-control-base-runner.tsv` | read + verify=ok; runner blob e13d0c83… equal at base and 1efe406 (Evidence 2) |
| C3 after `cases=8 pass=8 refusals=2/2 regress=5/5`, rc=0 | `c3-after.tsv` | read + verify=ok |
| gate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` | `gate-check-r24-entry.tsv` | read + verify=ok |
| slice: 7 accepted, 1 unverifiable (S118) | `census/round-24/records/slice-verdicts.tsv` | read (not a receipt) |
| r13 recheck `selftest=PASS ids=5/5`, git 2.56.0 | `r13-recheck-receipt.tsv` | read + verify=ok |
| every tool/fixture sha256 named | `git show <rev>:<path> \| sha256sum` | executed (Evidence 2) |
| registry 119 → 123 | grep count (Evidence 5) | executed; **not receipt-bound**, so prose only |
| lane figure `garbage=0 size_garbage=0 unreachable=1093 alternates=0` | `census/round-24/size-census-lane.txt` | read; **not a receipt** (`RECEIPT-MALFORMED`), so prose only |
| r23 C1 counter at 778747e `mismatches=0` | seat run (Evidence 8) | executed; **unreceipted**, so prose only |
| r23 C2 counter 15 files, 14 verify=ok | Evidence 7 | executed |
| wave sizes 38 + 35 | spec `items` | executed |

---

## Draft A — SCORECARD.md append

Insert the table below directly above `### Round 23 measurements` (newest first, matching the file's order). Leave the Axes table scores unchanged: no score move is claimed (see Findings 6).

```markdown
### Round 24 measurements (2026-10-25, lane base a65fac98964b445758e94c805728c9a19d302ff8)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 F2 debris census (write-safety fixture) | coverage 8 | at base the fixture and tool are absent (`git cat-file -e a65fac9:tests/fixtures/r24-size-census.py` fails), so `cases=0 pass=0` by the frozen definition; skip-the-work control (the case-8 stub as `--tool`, fixture bytes of `1efe406`): `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 1 — the stub fails cases 2 dangling, 3 garbage, 5 alternates, 6 refusal (`census/round-24/records/c1-control-stub.tsv`, `rev=1efe406e7f39b8fe736be2a566053703a571ffc0`) | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0 (`census/round-24/records/c1-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`); case 3 reads `garbage=1 size_garbage=2` on the main and the linked path, case 4 reads `garbage=0` while raw `git -C <linked> count-objects -v` reads `garbage: 1`, case 7 sees `fsck --lost-found` change the manifest | `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` | fixture `tests/fixtures/r24-size-census.py` sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f` (bound by both receipts); tool `tools/souji-size-census.py` at 778747e sha256 `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` (not bound by the receipt; `git show 778747e:tools/souji-size-census.py \| sha256sum`) |
| C2 coverage-map agreement | calibration 7 | `grounded=4 mapped=2 dangling=0 mismatches=2`, rc 1, at base `a65fac9` with the tool bytes of `1efe406`: `count-objects-garbage-readings-r25.md` and `repo-size-census-readonly.md` were MISSING-FROM-MAP (named only in a status cell) (`census/round-24/records/c2-control-base.tsv`) | `grounded=6 mapped=6 dangling=0 mismatches=0`, rc 0 (`census/round-24/records/c2-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`); fixture `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (`census/round-24/records/c2-fixture-after.tsv`); per-entry kill rule (amendment 1): all 4 base-grounded entries present at the tip with the same F<k> (`git diff a65fac9 778747e -- corpus/knowledge/` adds two `ground:` lines and removes none) | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | tool `tools/souji-coverage-agreement.py` sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`; fixture sha256 `42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44` |
| C3 receipt verify/run symmetry | operability 8 | base runner (`tools/souji-receipt-run.py` sha256 `e13d0c83…`, identical at `a65fac9` and `1efe406`): `cases=8 pass=6 refusals=0/2 regress=5/5`, rc 1 — case a (non-durable rev, no-ref and `refs/jj/keep`-only) and case b (`tool=` not in argv) both `verify=ok` (`census/round-24/records/c3-control-base-runner.tsv`) | `cases=8 pass=8 refusals=2/2 regress=5/5`, rc 0 (`census/round-24/records/c3-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`): `RECEIPT-REV-NOT-DURABLE` for both case-a instances, `RECEIPT-TOOL-NOT-IN-ARGV` for the absent and substring-only labels, the five r23 receipts still `verify=ok` | `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-root .` | fixture sha256 `f8c4c391097ee9745b72cbf5eef51aec235a89946c22831d10a1db7badc708b2`; runner at 778747e sha256 `9df0738c…` (not bound by the receipt) |
| assimilation (rides inside C1; no claim slot) | coverage 8 | F2 grounded entries 2 (`ground: F2` lines at `a65fac9`); quarantine slice not yet checked | gate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` (`census/round-24/records/gate-check-r24-entry.tsv`); entry `corpus/knowledge/count-objects-linked-worktree-garbage.md` (S120–S123), 2 staged packages admitted (r27 re-sourced, r25 matrix only), 4 rejected; slice 7 accepted + 1 unverifiable (S118) | `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/count-objects-linked-worktree-garbage.md --snapshot-dir census/round-24/sources --slice census/round-24/records/quarantine-slice --slice-verdicts census/round-24/records/slice-verdicts.tsv` | gate tool sha256 `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d`; snapshots `census/round-24/sources/*` (`sha256sum -c SHA256SUMS` 6/6) |
| r13 structure entry recheck (freshness; not a claim) | — | `git-repo-structure-readonly.md` verified on git 2.55.0 only, r16 note "pending recheck" | `selftest=PASS ids=5/5` on git 2.56.0 (`census/round-24/records/r13-recheck-receipt.tsv`) | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | fixture sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` |

Each round-24 counter scored the amended (amendment 1, stricter-only, written before any control
or after receipt) bytes pinned above. Controls were committed in `ce5971c` before any after-data. A
disclosed deviation: the L1 ran sanity executions of the C2 tool and C3 fixture before the
amendment; those runs are not claim evidence. Named limits:

- **C1.** The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases on git 2.56.0.
  The manifest excludes atime/ctime, so a tool that restores directory mtimes after a write is
  invisible to it. The stderr contract (`census.warning=` lines, exit 1 on other stderr) and the
  not-a-repository exit 2 have no case. No case plants hostile config or environment: the tool
  carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null` and a scrubbed env, but no counter
  exercises them. Cases 7 and 8 pass for any `--tool`.
- **C2.** C2 covers the 6 grounded entries out of 13 `.md` entries. The per-entry kill rule was
  checked by `git diff`, not by the tool. `mismatches=0` does not retire the stale
  "frontier, no entry" F2 row at `corpus/README.md:40`.
- **C3.** Argv membership binds the label to recorded text, not to the executed program. A tool
  named as an operand while another program runs still verifies. Of the 20 r23 residuals, C3
  closes 1 and narrows 6.

The lane-bound figure `census/round-24/size-census-lane.txt` (`garbage=0 size_garbage=0
unreachable=1093 alternates=0`, tool sha256 `09bb8e0d…`) describes this repository at the moment of
the run (jj keep refs plus a cruft pack). It is not a fleet figure and not a plain-clone figure. It
is a measurement file, not a v1 receipt: `verify` returns `RECEIPT-MALFORMED`. Registry 119 → 123
(S120–S123) is a grep count over committed bytes, not a receipt.
```

Capabilities rows (append at the end of `## Capabilities`, after `record agreement audit (r23)`):

```markdown
| debris census (r24) | read `count-objects -v` garbage / size-garbage / alternates against the resolved common git dir (so a linked worktree's private-gitdir `garbage: 1` is not reported) and count `fsck --unreachable --no-reflogs` lines, under a scrubbed environment with `core.fsmonitor=false` and `core.hooksPath=/dev/null`; refuse `--lost-found`, promisor/partialClone repositories (including a leftover `objects/pack/*.promisor`) and non-repositories with exit 2. The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases (manifest excludes atime/ctime); unreachable includes alternates when alternates>0; one lane-bound figure, no fleet figure, no deletion authority | `tools/souji-size-census.py`; `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` 8/8 `control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (`census/round-24/records/c1-after.tsv`); stub control 4/8 (`c1-control-stub.tsv`); `corpus/knowledge/count-objects-linked-worktree-garbage.md`, S120–S123 | r24 |
| coverage-map agreement (r24) | at a full 40-hex revision, from committed bytes only, flag every `ground: F<k>` knowledge entry not named by a backticked `knowledge/<name>` in the entries column of a coverage-map row whose ground cell starts with F<k> (status-column mentions never map), and every backticked entries-column `knowledge/` path absent at that revision; its fixture fails the always-zero emitter on all nine cases. Scope: grounded entries only (6 of 13 at 778747e); the per-entry kill rule is not mechanized | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `census/round-24/records/c2-control-base.tsv` (2 at base), `c2-after.tsv` (0); `tests/fixtures/r24-coverage-agreement.py` 9/9 (`c2-fixture-after.tsv`) | r24 |
```

Optional same-landing correction (calibration, RevR23Residuals R3): the `blob-bound receipts (r23)`
row still says "tool sha256 of the bytes the command ran against". Since r24 the digest binds the
labelled file's committed bytes, and that label must appear in argv. It does not bind the executed
program. Append a dated note to the row; do not rewrite the r23 sentence.

Planned (append after the existing `- **r24 — planned:** …` line, keeping it, as the r16–r19 pairs do):

```markdown
- **r24 (planned r23) — done, see `corpus/lessons/round-24.md`:** C1 F2 debris census with a `/var/tmp` write-safety fixture that refuses `--lost-found` (8/8), C2 coverage-map agreement (2 → 0 mismatches), C3 receipt verify/run symmetry (refusals 0/2 → 2/2, regress 5/5), as measured in the Round 24 table; one assimilated F2 entry (S120–S123), `git-repo-structure-readonly.md` re-verified on git 2.56.0. Of the planned "re-run the r23 counters": C3 case d re-verifies the five r23 receipts at the tip; the r23 record-agreement counter has no r24 receipt. Of "close the residual C1/C2 limits": 1 of 20 closed (verify durability), 6 narrowed, 12 open, 1 open by design (`.ufo/waves/round-24/w1/RevR23Residuals.md`). Certification OFF, K5 HELD.
- **r25 (planned r24):** (a) calibration: make C2's per-entry kill rule (base-grounded entry absent or re-grounded at tip) a tool row instead of a hand `git diff`; retire or mark superseded the stale F2 "frontier, no entry" row at `corpus/README.md:40`; turn `census/round-24/size-census-lane.txt` into a v1 receipt or relabel it; replace the r23 `tool_sha256=` grep counter with a count of `verify=ok` receipts; receipt the r23 record-agreement counter at the tip; carry the open r23 residuals R3, R7 (counts read from stderr), R15 (K1 decoy) and R17 (K1 trailing shadow). (b) coverage: put `tools/souji-repo-structure.sh` under the r24 common-dir manifest envelope, then the colocated/plain byte-comparison precondition (README `### Frontier (r24)`); add the untested C1 contract parts — `census.warning=` and exit 1 on other stderr, not-a-repository exit 2, hostile `core.fsmonitor`/env cases, and a ctime or read-only-`.git` arm against mtime-restore writes; re-verify the two remaining git-2.55.0 entries (`git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`) on 2.56.0. (c) operability: bind the receipt label to the program position (interpreter's first script argument), not just argv membership. Fleet route: the LEARNING.md expansion predicate (capability vs entry-on-uncovered-ground) is unresolved. Certification stays OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.
```

---

## Draft B — LOG.md append (`Round24` block, r23 shape)

```text
Round24 (2026-10-25) — F2 debris census, coverage-map agreement, receipt verify symmetry
========================================================================================
Three claims frozen before data in .ufo/waves/round-24/preregistration.txt
against lane base a65fac98964b445758e94c805728c9a19d302ff8, tightened before
any control or after receipt by the append-only
.ufo/waves/round-24/preregistration-amendment-1.txt (stricter only). Inbound:
SCORECARD "r24 — planned" (the F2 write-safety fixture that must exclude
git fsck --lost-found; the residual r23 C1/C2 limits) and the r23 non-author
spot-check's routed defect (coverage-map table vs its own "read side now
holds three" prose, corpus/lessons/round-23-verifier-spotcheck.md:41).

C1 coverage (8). tools/souji-size-census.py reads count-objects -v
(garbage, size-garbage, alternates) against the resolved common git dir and
counts fsck --unreachable --no-reflogs lines, under a scrubbed environment
with core.fsmonitor=false and core.hooksPath=/dev/null; it refuses
--lost-found, promisor/partialClone repositories and non-repositories with
exit 2. Counter python3 -B tests/fixtures/r24-size-census.py --tool
tools/souji-size-census.py. Before: fixture and tool absent at base
(cases=0 pass=0 by definition); the case-8 stub as --tool scored cases=8
pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED, rc 1
(receipt census/round-24/records/c1-control-stub.tsv, rev 1efe406e7f39b8fe736be2a566053703a571ffc0).
After: cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED,
rc 0 (census/round-24/records/c1-after.tsv, rev 778747eb671f8e85ef5387bc3d7023337b30467c).
Lane-bound figure census/round-24/size-census-lane.txt: garbage=0
size_garbage=0 unreachable=1093 alternates=0 at the moment of the run, this
repository only (jj keep refs, a cruft pack); it is a measurement file, not
a v1 receipt (verify: RECEIPT-MALFORMED). No fleet figure is claimed.
Named limits: no-write is a /var/tmp fixture claim on git 2.56.0; the
manifest excludes atime/ctime; the stderr contract, the not-a-repo exit and
hostile config/env have no case.

C2 calibration (lowest axis, 7). tools/souji-coverage-agreement.py
re-derives, at a full revision, whether every `ground: F<k>` entry is named
by a backticked knowledge/<name> in an F<k> row's entries column and whether
every such path exists. Control (do nothing) = the same tool at base:
grounded=4 mapped=2 dangling=0 mismatches=2, rc 1 — the two r23 F2 entries
named only in a status cell (census/round-24/records/c2-control-base.tsv).
After: grounded=6 mapped=6 dangling=0 mismatches=0, rc 0
(census/round-24/records/c2-after.tsv, rev 778747eb671f8e85ef5387bc3d7023337b30467c); fixture
cases=9 pass=9 control=FALSE-GREEN-REJECTED (c2-fixture-after.tsv). The
per-entry kill rule holds: all four base-grounded entries carry the same
F<k> at the tip (git diff adds two ground: lines, removes none). The rule is
checked by hand, not by the tool. Grounded entries are 6 of 13.

C3 operability (8). tools/souji-receipt-run.py verify now refuses a
non-durable rev (RECEIPT-REV-NOT-DURABLE, including a refs/jj/keep-only
commit) and a tool= label that is not an argv element of cmd=
(RECEIPT-TOOL-NOT-IN-ARGV); run refuses the same label shapes
(TOOL-NOT-IN-ARGV, TOOL-PATH-REDACTED; runner lines 179-181 at 778747e, no
counter case exercises the run side). Counter
python3 -B tests/fixtures/r24-receipt-verify.py --tool
tools/souji-receipt-run.py --lane-root . Before (base runner bytes):
cases=8 pass=6 refusals=0/2 regress=5/5, rc 1
(census/round-24/records/c3-control-base-runner.tsv). After: cases=8 pass=8
refusals=2/2 regress=5/5, rc 0 (census/round-24/records/c3-after.tsv).
Named limit kept: argv membership binds the label to recorded text, not to
the executed program. Of the 20 r23 C1/C2 residuals, 1 is closed, 6 are
narrowed and 12 stay open (.ufo/waves/round-24/w1/RevR23Residuals.md).

Assimilation (inside C1). One F2 entry,
corpus/knowledge/count-objects-linked-worktree-garbage.md, grounded on
git.git path.c at v2.56.0 and v2.30.0, builtin/count-objects.c at v2.56.0
and git-worktree(1) § REFS (S120-S123; snapshots census/round-24/sources/
with SHA256SUMS). Staged packages: 2 admitted (r27 re-sourced, r25 matrix
only), 4 rejected. Quarantine slice 8 rows: 7 accepted, 1 unverifiable
(S118). Gate entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0
(census/round-24/records/gate-check-r24-entry.tsv). Registry 119 -> 123.
corpus/knowledge/git-repo-structure-readonly.md gains a ground: F2 line and
is re-verified on git 2.56.0: selftest=PASS ids=5/5
(census/round-24/records/r13-recheck-receipt.tsv).

r23 counters at the new tip. C3 case d re-verifies the five r23 receipts
(regress=5/5). The r23 tool_sha256 grep counter now lists 15 files under
census/, of which 14 verify=ok; the fifteenth is the lane-bound census file
above. The r23 record-agreement counter carries no r24 receipt.

Wave. Wave 1, 38 seats (12 scout, 10 executor, 4 critic, 4 scribe,
3 reviewer, 1 sentinel, 1 simplifier, 1 revenger, 1 mutation-tester,
1 connector), from .ufo/waves/round-24/w1-spec.json; wave 2 (35 falsify
seats) from .ufo/waves/round-24/w2-spec.json — 73 seats in total. No deletion
outside this repo, no history rewrite, no credentials, no live /proc census,
no operator-sweep contents. Certification OFF, K5 HELD, F5 reap and
NAMESPACE holds unchanged.
```

---

## Findings

1. **The lane-bound size figure is not a receipt.** `census/round-24/size-census-lane.txt` has no `receipt=v1` header, and `verify` returns `RECEIPT-MALFORMED` (rc 2). The file's line 1 says: "this repository only, at the moment of the run; not a fleet figure, not a plain-clone figure". The drafts cite it only in prose, never as `verify=ok`. Commit message `ca7fc1c` calls it a "lane-bound size census", and that is accurate.
2. **The r23 C2 counter overcounts at the tip.** The SCORECARD r23 row counts `grep -rlE '^tool_sha256=…' census/ \| wc -l`. At master c3ca7ad it lists 15 files, and one of them (Finding 1) fails verify. Reporting "15 bound receipts" would overstate the number by 1. The draft says 14 verify=ok out of 15.
3. **The planned item "re-run the r23 counters at the new tip" is only partly evidenced.** `census/round-24/records/` has no record-agreement receipt. This seat's own run at 778747e gives `keys=4 records=4 occurrences=17 mismatches=0` (Evidence 8), but it is unreceipted and is not used as table data. The r25 line asks for it to be receipted.
4. **The C3 receipt's `cmd=` differs from the frozen counter string by `--lane-root .`.** Prereg line 100 says: "Counter (frozen): python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py". The receipt adds `--lane-root .`. The fixture's line 22 says: "--lane-root defaults to the git toplevel containing --tool." [INFERENCE] The two invocations are equivalent when run from the clone root, so this is information for the judge, not a deviation in the measured result. The draft's counting-command cell copies the receipt's argv.
5. **Some receipts bind the fixture, not the instrument under test.** In `c1-*.tsv` and `c3-*.tsv`, `tool_sha256` is the fixture's digest. The measured tool (`souji-size-census.py` 09bb8e0d…, runner 9df0738c…/e13d0c83…) and the C1 stub (9908b9be…) are bound only through `rev`. The table names those digests separately and marks them "not bound by the receipt".
6. **No axis score move is drafted.** ReviewAxesTrend (w1, A1) shows that LEARNING.md's expansion predicate is ambiguous about capability rows: r18 granted `improved` on capabilities, while r16 and r23 refused. The two new capability rows are evidence, not a self-graded `improved`. The r25 line routes the predicate question to the fleet.
7. **F2 entry count: say which rule you use.** Under C2's `ground:` rule, F2 goes from 2 to 4 grounded entries. `git-repo-structure-readonly.md` became grounded only by format; its base text carried the ground in body prose (W2C2Rerun F2). The new README F2 row names 4 entries. The draft uses the `ground:` rule.
8. **Wave-2 residuals folded so far.**
   - W2C2Rerun F3: the per-entry kill rule is enforced by hand. This went into the C2 limit and into r25 (a).
   - W2SrcPath F1: the entry header line 2 labels "line 101-136 (common_list)", but common_list is L110-136. This is low severity and entry-only, so it is left for the lesson rather than r25.
   - W2Misroot F2/F3: a `/var/tmp/souji-r24-ScribeEntry*` leftover contradicts a committed w1 report. This is a hygiene item for the L1, not a planned-line item.
   - 32 w2 reports had not landed when this was written. Re-check the r25 line against them.
9. **There is an unrelated uncommitted worktree state.** Present before and after this seat: `M corpus/QUALITY.md`, `M .ufo/waves/round-23/w2/{W2D3,W2K1}.md`, `M .ufo/waves/round-24/make-spec.py`, and `?? .ufo/waves/round-24/w2-dispatch.json`. None of it was touched by this seat; reported only.

## Attack log

- Attacked "every SCORECARD number is receipt-backed" against the drafts. Two figures that the round produced are not receipt-backed: the lane census (Finding 1) and the registry count (Evidence 5). Both were moved to prose and labelled. **Holds after the move.**
- Attacked "the controls measured base bytes". C2's control receipt has `rev=1efe406`, but its argv measures `--rev a65fac9`. C3's control ran runner bytes that are identical at both revisions (`e13d0c83…`). C1's control is the stub, by contract. **Survives.**
- Attacked "C2 reached 0 without un-grounding". `git diff` shows only `+ground:` lines, with name-status A/M only. **Survives** (it agrees with W2C2Rerun).
- Attacked "r23 counters re-run at tip". **Partly falsified**: see Findings 2 and 3.

Touched surfaces: this report only. Scratch `/var/tmp/souji-r24-W2ScorecardDraft/` was created and removed. No tools were installed or upgraded. Out of scope: editing SCORECARD.md/LOG.md themselves (left to the L1), any commit, and the 32 pending w2 reports.
