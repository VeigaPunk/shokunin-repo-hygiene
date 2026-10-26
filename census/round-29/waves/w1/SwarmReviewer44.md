# SwarmReviewer44 — r29 controls review: are the junk controls the cheapest target-reaching states?

## Status

STATUS: PASS — all seven control rows in `census/round-29/records/controls.tsv` reproduce byte-for-byte and the freeze verifies (6/6 digests), but for every axis the cheapest state that reaches the frozen target is cheaper than anything the L1 scored, and the three cheats compose into one tip that satisfies every target at once (finding 1). The controls are honest measurements; they are not evidence that the counters resist junk.

## Evidence

Lane read-only. Scratch clone `/var/tmp/souji-r29-SwarmReviewer44.UsQjse/c` (`git -C ... rev-parse --show-toplevel` = `.../c`); all revisions below are scratch commits, not lane commits. Lane tip `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.

Do-nothing rows, rerun at base (matches `controls.tsv`):

```
python3 -B tools/souji-registry-agreement.py --root $C --rev 691dd29... --list-rev b8cb4b3...
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29...            rc=1
python3 -B census/round-29/c2-counter.py --root $C --rev 691dd29...
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29...   rc=1
C3: F3_entries=0 rows=139
```

L1 junk rows, rerun (all seven reproduce exactly): `C1-junk1` k1=6 k2=0 → 6; `C1-junk2` → 10; `C1-junk3` k1=64 k2=4 → 68; `C2-junk1` records=1230 failed=0 uncovered=14 floor=0; `C2-junk2` floor_violations=3; `C3-junk` F3=2 rows=139, C1=12, gate `entries=2 ok=0 ... fail=2` at rev a385ee7. Additional L1 omission: `souji-coverage-agreement.py` on that C3 junk state is `grounded=15 mapped=13 mismatches=2 rc=1` (never measured by the control).

Freeze check (`git cat-file blob b8cb4b3:<path> | sha256sum` against `records/frozen-digests.txt`): `OK` for all six files — the frozen counters are the prereg bytes.

Cheap states I built and scored (scratch revs):

| state | axis | result | rev |
|---|---|---|---|
| citation-hide + body token + marker-only | C1 | `mismatches=0` rc 0 | 3de2c27 |
| citation-hide + 4-space-indented row + marker-only | C1 | `mismatches=0`; row count 139→138 | a71a057 |
| delete row S215 only | C1 | `k1=5` → 9 (no row floor) | f34b5f6 |
| rename entry only | C1 | 16 (fails) | 8eb89ff |
| junk stub named in a used-by cell | C1 | 10, no new mismatch (accepted) | 1ab93dd |
| drop 152 record lines + delete 14 symlinks | C2 | `records=1230 failed=0 uncovered=0 floor_violations=0` rc 0 | f433612 |
| hand-written manifest over committed bytes | C2 | `records=1231` 0/0/0 rc 0 | 8ae3906 |
| + one 1-record r29 manifest | C2 | `manifests=4` 0/0/0 rc 0 | a0ab646 |
| symlinks.tsv naming every path | C2 | failed=152 uncovered=15 (fails) | 6e565d8 |
| fabricated rows/entries/snapshots/slice | C3 | F3=2 rows=143 coverage 15/15 gate 2/2 slice 8/8 | e32513f |
| empty snapshot, real quote | C3 | gate `check4-quote-absent` (fails) | worktree |
| 2-byte snapshot + 2-word quote | C3 | gate `entries=1 ok=1` | worktree |
| all three cheats on one tip | all | C1 0, C2 manifests=4 0/0/0, C3 all pass | 702ac00 |

## Findings

**1. CRITICAL — the whole round is satisfiable without any of the claimed work, on one tip.** Scratch rev 702ac00 (base `b8cb4b3`): `tools/souji-registry-agreement.py` `k1=0 k2=0 mismatches=0`; `c2-counter.py` `r26 1230/0/0, r27 124/0/0, r28 75/0/0, r29 1/0/0, SUMMARY manifests=4 failed=0 uncovered=0 floor_violations=0`; `git grep -lE '^ground: F3' | wc -l` = 2; rows = 143; `souji-coverage-agreement.py` `grounded=15 mapped=15 dangling=0 mismatches=0`; `souji-gate-check.py` `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`. Diff: 32 files, 80 insertions, 175 deletions. No source was opened, no capture tool changed, no fixture added, no r26 evidence recovered. Location: `census/round-29/records/preregistration.txt` C1/C2/C3 targets vs the three counters.
Strictest fix: bind instrument evidence to the counters — a committed `census/round-29/waves/capture.json` naming the capture tool's blob sha256 at REV and a non-empty tool diff vs the prereg commit (C2), and a committed fetch receipt per snapshot (C3), so a counter-only state cannot pass. Add the composition state to `controls.sh` as the final control row.

**2. HIGH — C1's three predicates are individually evadable with 9 lines and zero registry corrections.** `tools/souji-registry-agreement.py:64` stops reading `source:` at the first `^#\s` line, so relocating five citation lines below the heading removes five mismatches (3de2c27); `:57` accepts the bare row id anywhere in the file, so appending `S215` to a body satisfies `used-by-no-cite`; `:17` only parses rows with 0–3 leading spaces, so 4-space-indenting row S215 removes the sixth mismatch and silently drops the row from both row counts (139→138, a71a057). Strictest fix: scan `source:` to EOF and count any `source:` below the first heading as a mismatch; require `used-by-no-cite` to be satisfied by a front-matter `source:` citation of that id; parse `^\s*\|` and flag ≥4-space indentation; add `rows(REV) ≥ 139` and "no base row id disappears".

**3. HIGH — C2's r26 floor is exactly the post-deletion survivor count, so deletion is a passing state.** `census/round-29/c2-counter.py:23` sets `FLOORS['26']=1230`; base records 1382 with 152 failing → dropping those 152 lines leaves 1230. Deleting the 14 uncovered symlinks then makes `failed=0 uncovered=0 floor_violations=0` with 166 deletions and zero insertions (f433612). A hand-written manifest over committed bytes also passes (`records=1231`, 8ae3906), and a one-file r29 capture gives the final-tip `manifests=4` (a0ab646). Nothing in the counter distinguishes tool capture from hand editing. Strictest fix: forbid silent loss — any manifest record or committed path present at the prereg commit and absent at REV must be declared in a committed `dropped.tsv` with path, old sha256 and reason (`:90` fails undeclared drops); add `capture.json` as in finding 1; require a third `symlinks.tsv` column carrying the symlink blob sha256.

**4. HIGH — C3 passes on fabricated sources: 4 rows with reserved-TLD URLs, 2-byte snapshots, 2-word quotes, fabricated slice.** At e32513f every C3 counter is green (see table). `tools/souji-gate-check.py:37` accepts any quote of 2–400 chars and `:110` only checks substring presence in a local file; no counter opens a URL, and the row's `source` URL is never compared with the Gate `url`. `check_slice` accepts any 8 S-ids against any 8 verdict rows. Strictest fix: a `census/round-29/records/fetch-receipts.tsv` (url, http status, fetched-at, bytes, sha256) that each snapshot must match, snapshot floor ≥512 bytes, quote floor ≥5 words, Gate url present in the `source` cell of a cited row, reject reserved TLDs, F3 count with a word boundary (`^ground: F3([[:space:]]|$)` — the current `^ground: F3` also matches F30–F39), and slice ids restricted to rows existing at the prereg commit.

**5. MEDIUM — the C3 gate reads the working tree, not committed bytes.** `souji-gate-check.py:70`, `:102` and `:110` open the worktree path; the C3 counter line in the prereg passes no revision. A seat can pass the gate on disposable snapshots and commit different bytes. Location: prereg C3 counter line vs `souji-gate-check.py:101`. Strictest fix: add `--rev` (read entries, snapshots and SOURCES via `git show`) and require it in the C3 counter line.

**6. MEDIUM — C1 carries no row floor, so deleting a mismatching row "counts".** Deleting row S215 alone takes 10→9 (f34b5f6); the registry loses a source and no counter notices. Row deletion cannot reach 0 by itself (the five entry→row citations become `cited-no-row`), so the state is not a full cheat, but it is an unmeasured loss. Strictest fix: row-id superset vs the prereg commit, as in finding 2.

**7. LOW — K2 accepts a marker with no correction, and matches the tag by substring.** `souji-registry-agreement.py:96` requires only a line starting `R29-CORRECTION ` containing the tag, so `LOG.md:17580` satisfies `LOG.md:1758` and junk text after the tag passes. The L1's own `C1-junk1` demonstrates k2=0 with no correction. Strictest fix: require `old="<frozen phrase>" new="<≥8 words>"` on the marker line and an exact tag token.

**8. LOW — a used-by cell may name any file that contains the id.** I appended `corpus/knowledge/stub-s001.md` (content `S001`) to row S001's used-by: C1 unchanged, row cell count clean (1ab93dd). The predicate never requires the target to be a knowledge entry. Strictest fix: used-by targets must be direct children of `corpus/knowledge/` with a front-matter `source:` citation of the row.

**9. LOW — the lane worktree carries another seat's uncommitted edit under a tracked `.ufo/waves/` path.** At review time `git -C <lane> status --porcelain` reports ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` (+2/−1); `.ufo/waves/` is gitignored (`.gitignore:1`) but this file is tracked, so the ignore rule does not protect it. Not mine — I wrote only this report. Because all three counters read committed bytes, no counter sees it, and an integrator `git add -A` would land an unreviewed edit into a round-26 receipt. Strictest fix: the landing gate refuses a dirty worktree for tracked paths under `.ufo/waves/` at integration, or the L1 commits/clears it before measuring.

**10. LOW — the freeze is declared, not enforced at measurement time.** No tool reads `records/frozen-digests.txt` (`grep -rn` over `tools/`, `tests/`, `census/round-29` finds no consumer), and `souji-registry-agreement.py:105` lets the runner choose `--stale-list` at `--list-rev`. Strictest fix: the counter verifies its own and the stale list's sha256 against the frozen record before evaluating, and the enumerate line pins `--stale-list`.

## Attack log

Attempted and scored this run; "target" = the frozen C1/C2/C3 target state.

| attack | verdict |
|---|---|
| C1 hide `source:` lines below the first heading | **passes** (0) — finding 2 |
| C1 append bare row id to an entry body | **passes** — finding 2 |
| C1 4-space-indent the mismatching row | **passes** (0) and hides the row from both row counts — findings 2, 6 |
| C1 delete the mismatching row | partial: 10→9, cannot reach 0 — finding 6 |
| C1 rename an entry | fails: 16 |
| C1 point used-by at a junk stub containing the id | **passes** undetected — finding 8 |
| C1 marker-only K2 correction | **passes** k2=0 — finding 7 |
| C2 drop failing records + delete uncovered symlinks | **passes** 0/0/0 at records=1230 — finding 3 |
| C2 drop failing records only | fails: uncovered=14 (L1 junk1, reproduced) |
| C2 hand-regenerate manifest over committed bytes | **passes** 1231 records — finding 3 |
| C2 one-file r29 manifest for `manifests=4` | **passes** — finding 3 |
| C2 `symlinks.tsv` listing every path as a symlink with target text | fails: mode gate `c2-counter.py:87` ignores non-120000 rows (uncovered=15) — no finding |
| C2 manifest records for files that exist | **passes** (same as hand-regenerate) — finding 3 |
| C3 `ground: F3` entries + 4 new junk rows + empty snapshots | fails: an empty body cannot contain a ≥2-char quote (`gate-check.py:37`, `:110`) |
| C3 same with 2-byte snapshots and 2-word quotes | **passes** every C3 counter — finding 4 |
| C3 gate on uncommitted snapshots | **passes** — finding 5 |

## Deliveries

- `.ufo/waves/round-29/w1/SwarmReviewer44.md` (this report)

## Residual risk and gaps

- The cheat revisions are scratch-only (`/var/tmp/souji-r29-SwarmReviewer44.UsQjse/c`, removed after review); the lane, its index and its jj state were not touched. The states are reproducible from the recipes in the evidence table.
- "Cheapest" is ordered by edited lines/files from a hand-built state, not by wall time; the L1's junk states remain cheaper to write but fail, which is the point.
- I did not execute the fleet `sources-census.sh validate` (outside this lane's write scope); row-schema passage was checked with the awk predicates copied from `census/round-12/sources-census.sh:6,14,16`. `tools/souji-landing-gate.py` and `tools/souji-seat-audit.py` were not run against these states — a landing gate may still catch some of them, which would lower findings 1–4 in practice but not in the counters.
- No tool was installed or upgraded this run.
