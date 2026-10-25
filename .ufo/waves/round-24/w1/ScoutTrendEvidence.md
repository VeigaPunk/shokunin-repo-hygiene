# ScoutTrendEvidence — round 24, wave 1 (read-only scout)

## Status
STATUS: PASS — all three F2 entries' `recheck:` values are dated and assessed for due status; every entry claim is mapped to a frozen C1 case or marked uncovered; evidence was read at lane HEAD f9db2181647d91470a724a12d626bd6106805076. One recheck is overdue: `git-repo-structure-readonly`. C1 covers none of that entry's own claims.

## Evidence
All lane paths are relative to /home/vgpnk/Projects/shokunin/souji-shokunin. Lane HEAD is `f9db218` (preregistration commit). C1 tool and fixture are not yet tracked (`git cat-file -e HEAD:tools/souji-size-census.py` → no; same for `tests/fixtures/r24-size-census.py`).

| Command | Output excerpt |
|---|---|
| `git --version; pacman -Q git` | `git version 2.56.0` / `git 2.56.0-1` |
| grep of /var/log/pacman.log for `installed git (` and `upgraded git (` (read only) | l.452 `[2026-10-03T20:42:26+0000] [ALPM] installed git (2.55.0-1)`; l.2698 `[2026-10-20T09:16:37-0300] [ALPM] upgraded git (2.55.0-1 -> 2.56.0-1)`. This is the last git transaction. |
| `python3 -B` read of `census/round-13/verification.json` result `structure-selftest` | exit 0, measured_commit `6ed10a7…`, stdout begins `git_version=git version 2.55.0`; file `recorded_at` `2026-10-20T05:45:21Z` (before the 12:16Z upgrade) |
| `git log -- tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh` | only `6ed10a7 2026-10-20 round-13: …`. Probe and fixture bytes have not changed since the 2.55.0 run. |
| `git log -- corpus/knowledge/git-repo-structure-readonly.md` | `fb23b12 round-16: … knowledge freshness notes (host git 2.56.0)`, `6ed10a7`. No later re-verification commit exists. |
| `sha256sum -c census/round-23/sources/SHA256SUMS` (lane root) | 5/5 `OK` (csdn, git-count-objects.1, git-fsck.1, git-prune.1, qiita). This checks extract integrity only. It is not the 180d live re-fetch. |
| Scratch probe `/var/tmp/souji-r24-ScoutTrendEvidence/` (git 2.56.0; removed, `scratch-removed` printed). Two junk files in `objects/pack`: first 10 B, then an added 5000 B | 10 B: `garbage: 1` `size-garbage: 0`; 10 B + 5000 B: `garbage: 2` `size-garbage: 4`. Scout evidence, not claim data. |
| `grep -n mktemp tests/fixtures/r13-repo-structure.sh` | l.107 `HERMETIC: hard-coded mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX`; l.108 `(TMPDIR ignored; no tmpfs fallback)` |

Tools installed: none.

## Recheck status

| Entry | `recheck:` value (verbatim head) | verified-at | Due? |
|---|---|---|---|
| `corpus/knowledge/git-repo-structure-readonly.md` l.3 | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` (command, no cadence) | 2026-10-20, Git 2.55.0 | **DUE (overdue).** The host has run 2.56.0 since 2026-10-20 12:16Z (pacman.log l.2698). The entry's own l.45 note says it is pending a recheck routed to r17. No later run was found in `corpus/lessons/round-1[7-9]*`, `round-2[0-3]*` (freshness was "unchanged" or "not claimed" in every spot-check). |
| `corpus/knowledge/repo-size-census-readonly.md` l.5 | `on-release — re-read man git-count-objects, man git-fsck, man git-prune after a host git upgrade` | 2026-10-25, git 2.56.0-1 | **Not due.** There has been no git transaction since 2026-10-20, and the host still runs 2.56.0-1, the verified version. |
| `corpus/knowledge/count-objects-garbage-readings-r25.md` l.4 | `180d — re-fetch both community pages live and re-grep each Gate span against the LIVE page bytes … and re-hash the committed extracts against census/round-23/sources/SHA256SUMS` | 2026-10-25 | **Not due** until 2027-04-23. The re-hash half passes today (5/5 OK), but the live-page half is the binding test and was not run. |

## Entry / claim / case / currently-verified-by

"Effect" uses the LEARNING quality observable: R = empirical re-verification, D = deepening (new bounded fact), S = supersession of an entry sentence, — = none.

| Entry | Claim (entry location) | C1 case | Currently verified by | Effect if C1 lands |
|---|---|---|---|---|
| repo-size-census-readonly | 1: `count-objects -v` `garbage` counts files that are neither valid loose objects nor valid packs (l.15-19) | 3 (`garbage=1`) | doc snapshot S115 `census/round-23/sources/git-count-objects.1.txt` (digest OK); documentation only | R |
| repo-size-census-readonly | 1: the `alternate` field must be read (l.20-22) | 5 (`alternates=1`) | S115 snapshot only | R for field presence. The double-count consequence is not tested. |
| repo-size-census-readonly | 1: ignoring `garbage`/`size-garbage` under-reports disk use (l.18-20) | 3 asserts `garbage` only; `size_garbage` is not in the case-3 predicate | S115 snapshot | — (partial; see Finding 5) |
| repo-size-census-readonly | 2: `fsck --unreachable` prints objects reachable from no reference node (l.23-25) | 2 (`unreachable=1`, no `.git/lost-found`) | S116 `git-fsck.1.txt` snapshot | R |
| repo-size-census-readonly | 2: the `--dangling` and `--unreachable` classes differ; `--no-reflogs` and the default head set (index, refs, reflogs) (l.25-28) | none. A single unreferenced blob is both dangling and unreachable, and no reflog-only commit is built. | S116 snapshot | — |
| repo-size-census-readonly | 3: `fsck --lost-found` WRITES `.git/lost-found/{commit,other}/` (l.29-35) | **7** (detector → `WRITE-DETECTED`); 6 fences it (tool refuses `--lost-found`, manifest unchanged) | S116 snapshot; r23 lesson l.79 marks the read side as documentation-absence, not empirical | **R** (the first empirical binding of the write claim) |
| repo-size-census-readonly | 3: for a blob, the contents (not the object name) are written (l.30-31) | 7 checks that `other/<oid>` exists and the manifest changed; file content is not in the predicate | S116 snapshot | — unless the fixture also compares content |
| repo-size-census-readonly | 4: `git prune` is narrower than unreachable (unpacked only) (l.36-40) | none | S117 `git-prune.1.txt` snapshot | — |
| repo-size-census-readonly | Not established: concurrency safety; the write-safety fixture "is still owed" (l.53-55) | 1, 2, 3, 6 (manifest identical before/after, sequential, fixture repos) | nothing (stated as owed) | S/D partial: the sequential no-write envelope stops being owed; concurrency stays owed |
| repo-size-census-readonly | Not established: no size figure for this lane or the fleet (l.56-58) | prereg lane-bound run → `census/round-24/size-census-lane.txt` | nothing | S for the lane half only; the fleet half stands |
| (not in any entry) | the linked worktree `garbage` false positive; the common-dir read gives `garbage: 0` | **4** | pre-freeze L1 probe only (prereg l.15-17: "design input, not claim data") | D (the assimilation theme) |
| git-repo-structure-readonly | `repo structure` probe leaves no persistent Git-directory change on the isolated fixture (l.11) | none | `census/round-13/verification.json` `structure-selftest` exit 0 on **Git 2.55.0** | —. Only its own recheck re-verifies it (Finding 2). |
| git-repo-structure-readonly | Decision row: unreachable accounting needs a separate read-only object census (l.19) | 2 supplies that census | nothing empirical (entry points outward) | D (cross-link) |
| git-repo-structure-readonly | Linked-worktree outputs describe the shared common store; do not sum them (l.43-44) | 4 is the analogue for `count-objects` (the tool reads the common dir) | AttackCoverage r13 narrative; not this instrument | D by analogy; not R |
| git-repo-structure-readonly | Wrapper refuses partial/promisor repositories (l.37-40) | 6 (partialClone → exit 2) uses a different tool | r13 AttackCoverage observation (2.55.0) | — (a parallel guard, not R) |
| count-objects-garbage-readings-r25 | 1: the ZH page glosses `garbage` as a size, which is a unit error against the manual (l.14-22) | 3, conditionally (Finding 5) | committed extract `csdn-count-objects-vh.raw` + SHA256SUMS (OK today) | R of the manual-side unit, only if case 3 records `size_garbage` ≠ `garbage` |
| count-objects-garbage-readings-r25 | 2: the JA page never glosses the field (l.23-29) | none (page-content negative; only a live re-fetch tests it) | committed `qiita-gc-auto.raw` | — |
| count-objects-garbage-readings-r25 | 3: the staged "both languages agree" claim is unsupported (l.30-33) | none | the two extracts | — |
| count-objects-garbage-readings-r25 | Not established: no fleet figure (l.36-41) | the lane-bound run does not touch the fleet | — | — (unchanged) |

## Findings
1. **C1 can produce LEARNING's quality observable, but only if the corpus entry changes.** Cases 2, 3, 5 and 7 give `repo-size-census-readonly` claims 1-3 their first empirical binding. Today those claims rest on snapshots alone. `corpus/lessons/round-23.md` l.79: "The page documents no write side effect; that is documentation-absence, not an empirical read-only proof." The prereg l.117 says C1 "touches … one knowledge entry". If that is a *new* entry and `repo-size-census-readonly.md`'s `verified-at` and l.53-55 "still owed" sentence are not amended to cite the fixture receipt, then no existing entry is re-verified or superseded. [INFERENCE] Quality would then stay at r23's verdict (`corpus/lessons/round-23-verifier-spotcheck.md` l.35: "the trend's observable is corpus-entry re-verification/deepening/supersession; no evidence here establishes that corpus quality criterion.").
2. **The overdue recheck is the cheapest legitimate quality gain, and C1 does not cover it.** `git-repo-structure-readonly.md` l.45: "this entry was verified on 2.55.0 and has not been re-verified on 2.56.0. Treat it as pending recheck (routed to r17)". The probe and fixture bytes are unchanged since `6ed10a7`, so running the l.3 command on 2.56.0 would be a clean like-for-like re-verification. The fixture writes to `/var/tmp/souji-r13-repo-structure.XXXXXX` (l.107-108, TMPDIR ignored), which is outside any seat's `souji-r24-<Name>` scratch prefix, so it needs an L1-authorized run. **Not run by this seat; not passed.** Also open: `corpus/lessons/round-17.md` l.88 notes "`souji-repo-structure.sh` counts inflate with keep refs", an unrecorded deepening for this entry.
3. **Two of three entries are not due.** `repo-size-census-readonly` is not due because there has been no git release since its verify date. `count-objects-garbage-readings-r25` is not due until 2027-04-23. Neither can contribute a legitimate recheck-based "re-verification" this round. Any freshness claim for them would be inflated.
4. **The case 4 deepening is new knowledge, not a re-verification.** No current F2 entry states the linked-worktree `garbage` false positive. Case 4 is its only empirical support. The prereg probe (l.15-17) is explicitly not claim data.
5. **Attack: case 3 is not guaranteed to discriminate count from size.** The scratch probe on 2.56.0 shows 10 B → `garbage: 1` `size-garbage: 0` and 5010 B → `size-garbage: 4` (KiB, floor). [INFERENCE] A junk file of 1024-2047 B would give `garbage=1 size_garbage=1`, so case 3 would not corroborate the manual's count unit against the ZH page's size gloss (`count-objects-garbage-readings-r25` claim 1). The frozen predicate checks only `garbage=1`, so this is reported, not proposed as a change. Whatever value the receipt prints is what either supports the unit or does not.
6. **Attack: claim coverage gaps inside C1 limit what can be called "re-verified".** These are uncovered: the `--dangling` vs `--unreachable` distinction, `--no-reflogs` and the head set (case 2 uses one blob and no reflog-only commit), blob-content materialization under lost-found (case 7 checks the path and the manifest), prune's scope (no case), and concurrency (sequential only). A lesson that says "repo-size-census-readonly re-verified" without those bounds would overclaim. Each uncovered claim stays snapshot-verified only.

## Attack log
- Findings 5 and 6 are attacks on how far C1 can support the quality claim, not on C1's counters. No predicate, target or case set is proposed for change.
