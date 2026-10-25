# W2Reverify — falsify the r24 re-verification of `git-repo-structure-readonly`

Seat: L1Souji24.W2Reverify (reviewer, read-only). Target: `corpus/knowledge/git-repo-structure-readonly.md`
at `ca7fc1cb6dd1333096c6f3bdbad304686691d126`. Lane `master` had moved to `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`
(wave-1 reports only). `git merge-base --is-ancestor ca7fc1c master` succeeds, and
`git diff ca7fc1c master -- corpus/knowledge/git-repo-structure-readonly.md` is empty.

## Status
STATUS: PASS — **survives.** The receipt verifies, and the unchanged `recheck:` reproduces `selftest=PASS ids=5/5`, rc 0, on Git 2.56.0 in a `/var/tmp` clone at ca7fc1c. Under LEARNING.md's quality rule, the entry re-verifies. The note has no false statement. It has three scope or traceability overreaches (findings 1–3) and two honest-but-thin points (findings 4–5).

## Evidence
All commands were run this seat. Scratch was `/var/tmp/souji-r24-W2Reverify/`, a `git clone --no-hardlinks` of the lane, with `ca7fc1c` checked out.

| # | Command | Output excerpt |
|---|---|---|
| E1 | `python3 -B tools/souji-receipt-run.py verify --root <lane> census/round-24/records/r13-recheck-receipt.tsv` | `verify=ok rev=778747eb671f8e85ef5387bc3d7023337b30467c tool=tests/fixtures/r13-repo-structure.sh tool_sha256=b6bf5205…179f`, rc=0 |
| E2 | same verify, with `--root <clone@ca7fc1c>` | identical `verify=ok`, rc=0 |
| E3 | `git --version`; `pacman -Q git` (query only) | `git version 2.56.0`; `git 2.56.0-1` |
| E4 | `sha256sum tests/fixtures/r13-repo-structure.sh tools/souji-repo-structure.sh` (clone) | `b6bf5205…179f`, `80025137…aec2`. These match the receipt and the r13 digests in the w1 review. |
| E5 | `git log -- tests/fixtures/r13-repo-structure.sh tools/souji-repo-structure.sh` | only `6ed10a7 2026-10-20 round-13: …`. The note's "run unchanged" holds. |
| E6 | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` (clone) | rc=0, empty stderr; all five ids PASS (`object-metrics checks=29`, `bogus-repo plain_dir_rc=2 missing_rc=2`, `promisor-refusal promisor_rc=2 partial_rc=2`); `selftest=PASS ids=5/5` |
| E7 | `diff` of E6 vs the committed `.out`, and of the receipt's stdout block vs the `.out`, both ignoring `fixture_*` lines | both identical. Only the mktemp dirs differ: `.out` `petQHu`, receipt `wUrYU8`, mine `Xgym14`. |
| E8 | no-op probe (`exit 0`, never runs git) as `--probe` | `write-free … verdict=PASS`, while object-metrics, bogus-repo and promisor-refusal give `verdict=FAIL`; `selftest=FAIL ids=5/5 … failed_verdicts=1`, rc=1 |
| E9 | `curl` raw `builtin/repo.c` at v2.55.0 and v2.56.0, then `diff` | The changes are `#include "path.h"`, `#include "setup.h"`, the `is_bare_repository(the_repository)` signature, and four new `repo info` keys `path.{commondir,gitdir}.{absolute,relative}`. `structure_count_references`, `count_objects` and `cmd_repo_structure` show no hunk. |
| E10 | same diff for `Documentation/git-repo.adoc` | only the four `path.*` key docs were added. v2.56.0 l.19 reads "THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY CHANGE." `git help -m repo` l.73 reads "…not intended for machine parsing." |
| E11 | sibling 2.55.0-stale rechecks: `git-auto-maintenance-prunes-worktrees.md:3` (gc.c at v2.56.0) and the `git-grace-periods-and-expire-to.md:23` corrected `man git-gc` command | gc.c count `2` (expect 2). The man command prints all six defaults (`2.weeks.ago`, `3.months.ago`, `defaults to 90/30 days`, `default is 60/15 days`). |
| E12 | `python3 -B tools/souji-coverage-agreement.py --root <clone> --rev ca7fc1c…` | `grounded=6 mapped=6 dangling=0 mismatches=0` |
| E13 | `git show --stat 778747e` / `ca7fc1c`; `git log --format=%cI` | The `.out` landed in `778747e` (committed 09:33:39Z, together with the note). The receipt (`utc=2026-10-25T09:34:49Z`) landed in `ca7fc1c` (09:34:57Z). |

## Findings

1. **The `verified-at:` header was not refreshed. LEARNING's freshness observable is therefore unchanged in the field it names.**
   - `corpus/knowledge/git-repo-structure-readonly.md:2`: "verified-at: 2026-10-20; host Git 2.55.0 (package 2.55.0-1), web docs 2.56.0".
   - LEARNING.md:34 lists the quality observable as "entries re-verified, deepened, or superseded by stronger ones; `verified-at` freshness".
   - LEARNING.md:68 says entries open with "`verified-at:` (commit or date) and `recheck:`".
   - The r24 date and 2.56.0 appear only in body prose (l.49). Any reader or tool keyed on the header still sees 2026-10-20 / 2.55.0.
   - ReviewAxesTrend option (a) explicitly said to "bump `verified-at`". This was not done.
   - QUALITY.md Q1 (l.25) still passes in substance ("the entry's `verified-at:` names a version; its `recheck:` runs on the host version"), because the host-version re-run is now recorded. The header nonetheless overstates staleness rather than freshness.
   - Remedy shape (not applied, since this seat is read-only): append the re-verified date and version to l.2, or record why the header is frozen.

2. **"This closes the r16 freshness note" claims more than the cited evidence covers.**
   - The r16 note (l.47) is entry-wide: "this entry was verified on 2.55.0 and has not been re-verified on 2.56.0".
   - The cited recheck exercises only the probe and fixture behaviour.
   - The entry's source-derived claims rest on S037 pinned at `v2.55.0` (l.1), and the lane did not re-open them. l.39-41 is one example: "starts traversal at refs, skips failed object-info reads, and returns zero after reporting statistics". `census/round-24/sources/` holds `path.c` and `builtin/count-objects.c` only, not `builtin/repo.c`.
   - The closure is *substantively true*: E9 shows no structure-code hunk between v2.55.0 and v2.56.0. At v2.56.0, `builtin/repo.c:848-851` still does `odb_read_object_info_extended(...OBJECT_INFO_SKIP_FETCH_OBJECT … ) < 0) continue;`, and `cmd_repo_structure` ends `return 0;` (l.980).
   - That support exists only in this seat's scratch, not in the note. The note should either scope itself to "the empirical recheck" or cite a v2.56.0 source re-open.

3. **The cited `.out` and the receipt are two different executions. Only the receipt is bound.**
   - The note says "output `…git2.56.0.out`, receipt `…r13-recheck-receipt.tsv`", which reads as one run.
   - The `.out` (tmpdir `petQHu`) has no rev, digest, rc or utc. It was committed in `778747e` with the note, before the receipt existed.
   - The receipt (tmpdir `wUrYU8`) is a later `run` at `rev=778747e`.
   - Content is identical modulo tmpdir (E7), so nothing false is recorded. Under QUALITY Q55, however, the quoted `ids=5/5` and `exit 0` are carried by the receipt alone, and the unbound `.out` is redundant evidence.

4. **The receipt binds the fixture digest, not the probe or Git.**
   - `tool=tests/fixtures/r13-repo-structure.sh` is digested. The executed probe `tools/souji-repo-structure.sh` and the git binary are not bound.
   - This is harmless at this rev: the probe is unchanged since `6ed10a7` (E4/E5), and the receipt stdout records `git_version=git version 2.56.0`.
   - It is the named C3 limit ("argv membership binds the label to recorded text, not to the executed program"). The re-verification inherits it.

5. **The note's disclosed weakness is accurate. The aggregate is still discriminating.**
   - E8 reproduces the note's "write-free case also passes a probe that does nothing".
   - The same no-op fails 3 of 5 ids and the selftest exits 1. `selftest=PASS ids=5/5` is therefore not satisfiable by a skip-the-work probe.
   - The write-free no-persistent-change claim stays bounded exactly as l.12 says: main worktree, isolated fixture, this host version.

## Judgement against LEARNING.md's quality rule
- **Rule:** LEARNING.md:34 says `improved` when "a weaker entry is superseded by a stronger one, or stale entries re-verify, with no admitted entry failing its re-check".
- **Re-verification:** the entry was stale and marked (l.47, so not `harmed`). Its declared `recheck:` (l.3, the LEARNING.md:68 "command … that re-verifies it") now passes on the host version, under a verifying receipt. I reproduced it (E1, E2, E6). **The entry re-verifies.**
- **The no-failing-re-check clause:** the other two 2.55.0-stale entries were not rechecked by the lane. They remain marked "pending recheck" (`git-auto-maintenance-prunes-worktrees.md:27`, `git-grace-periods-and-expire-to.md:37`). That is still marked, not `harmed`. This seat ran both rechecks on 2.56.0 and both pass (E11). No 2.55.0-stale entry fails its re-check.
  - [INFERENCE] No recheck was run for the other 10 entries in the 13-entry corpus. The clause "no admitted entry failing" is established only for the entries that were rechecked.
- **`ground: F2` line:** this is a metadata re-tag of prose that already existed (l.8 "Coverage-map ground: F2…"). The C2 count `grounded=6 mapped=6 mismatches=0` (E12) is consistent. It adds no knowledge and must not be counted toward expansion or quality.
- **Verdict:** `quality: improved` is supportable on this one entry. Findings 1–3 should be fixed or disclosed alongside that claim.

## Attack log
| Attack | Command | Result |
|---|---|---|
| Receipt forged or stale digest | E1, E2 | survives (`verify=ok`; digest equals blob at 778747e and in clone) |
| Recheck does not reproduce on 2.56.0 | E6 | survives (5/5, rc 0, empty stderr) |
| Fixture/probe changed since r13 ("unchanged" false) | E4, E5 | survives |
| Recorded output fabricated | E7 | survives (receipt and `.out` identical to mine modulo tmpdir); finding 3 |
| PASS obtainable by a do-nothing probe | E8 | survives (selftest rc 1) |
| Source claims broken by 2.56.0 | E9, E10 | survives, but only via this seat's scratch; finding 2 |
| Header freshness | read l.2 | **lands** (finding 1) |
| Sibling stale entries fail their rechecks | E11 | survives |

Tooling: no installs. Scratch `/var/tmp/souji-r24-W2Reverify/` removed. The fixture's own `/var/tmp/souji-r13-repo-structure.*` and `souji-repo-structure.*` dirs were all trap-cleaned (none remain). No lane writes other than this report.
