# ScribeEntryA — round 26, entry A draft (C2, F1 trigger set)

## Status

STATUS: PASS — `entry-git-auto-maintenance-trigger-set.md` drafted in this directory with claims 1-3 re-grounded from bytes opened this run; my draft passes both the assimilation gate and the Q54 locator fixture (`entries=1 ok=1 fail=0`, exit 0; `locators=1 locators_bad=0`, exit 0). One integration blocker found in the already-landed corpus copy (Finding 4).

## Evidence

Lane revision (read-only): `git rev-parse HEAD` → `44531281914ddd200432cdc7dae8ad958c5447e3`; base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; prereg + amendments 1-2 read from `.ufo/waves/round-26/`.

| command | output excerpt |
|---|---|
| `sha256sum -c census/round-26/sources/SHA256SUMS` | 7/7 `OK` |
| `for f in fetch merge rebase am commit pull; do grep -c run_auto_maintenance census/round-26/sources/git-builtin-$f.c; done` | `1 1 1 1 1 0` |
| `grep -n run_auto_maintenance` on the five snapshots | `fetch.c:2926`, `merge.c:509`, `rebase.c:572`, `am.c:1942`, `commit.c:1965` |
| whole-tree scan, `git-2.56.0.tar.gz` extracted in `/var/tmp/souji-r26-ScribeEntryA` | `grep -rn run_auto_maintenance --include=*.c --include=*.h` → those five lines only, plus `run-command.h:247` declaration and `run-command.c:1987` definition; no `builtin/*.h` exists |
| `curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/$f.c \| sha256sum` vs snapshot | fetch `f14e15eb…`, merge `b6f5b663…`, rebase `72b4d351…`, am `aa5ac1ce…`, commit `e566f209…`, pull `538aa964…` — identical for all six |
| `grep -n enable_auto_gc census/round-26/sources/git-builtin-fetch.c` | `2528: int enable_auto_gc = 1;`, `2619`/`2621` OPT_BOOL `auto-maintenance`/`auto-gc`, `2909: if (enable_auto_gc) {` |
| `awk NR>=1956 && NR<=1986 run-command.c` (tarball) | `1961` reads `maintenance.auto`, `1963` falls back to `gc.auto`, `1966-1967` returns without spawning |
| `grep -rn '"auto-maintenance"\|"auto-gc"' builtin/*.c` (tarball) | only `builtin/fetch.c:2619,2621` — the flag is fetch's alone |
| `zcat /usr/share/man/man1/git-fetch.1.gz` (Git 2.56.0) | `267` option list, `274` "at the end to perform automatic repository maintenance if needed" |
| `grep -n auto-maintenance Documentation/fetch-options.adoc` (tarball) | `170-176`, same paragraph as upstream source |
| `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts` | `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`, exit 0 |
| `python3 -B tests/fixtures/r23-locator-heading.py --entries .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md --snapshot-dir census/round-26/sources` | `entries=1 locators=1 locators_bad=0`, exit 0 |

Deliverable: `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md` (7 Gate rows: 6 ADMIT, 1 REJECT; 3 `source:` lines S128/S129/S130; `verified-at: 2026-10-25`; `recheck: 90d` carried from the staged entry, parameterised to the host tag; `ground: F1`).

## Findings

1. **Staged entry A's comment spans are off by one.** It cites `builtin/merge.c:506-509` and `builtin/rebase.c:569-572` as the "ignore errors" comments. Bytes: merge comment `505-508`, call `509`; rebase comment `568-571`, call `572-573` (`census/round-26/sources/git-builtin-merge.c:505-509`, `git-builtin-rebase.c:568-573`). The draft uses the byte-exact spans.
2. **The two comments are not the same sentence.** Staged: both carry "We ignore errors in 'gc --auto' …". Bytes: merge says `'gc --auto'` (`merge.c:506`), rebase says `'git maintenance run --auto'` (`rebase.c:569`). A grep for the staged wording misses rebase; the draft quotes each separately and says so.
3. **Claim 1 can be stated more strongly without new measurement.** The staged "five of the candidate builtins" is now "exactly five callers in the whole v2.56.0 tree" — call-site evidence only (`builtin/*.c` scan plus non-builtin `*.c`/`*.h` scan; `run-command.c:1987` definition, `run-command.h:247` declaration). No behavioural claim was added; entry B remains the fixture.
4. **BLOCKER for the L1: the already-landed corpus copy would fail C2 K2.** `corpus/knowledge/git-auto-maintenance-trigger-set.md` (untracked, lane tip 4453128) has no `## Gate`; `souji-gate-check.py` on it prints `FAIL … check1-no-gate` and exits 1, so K2 cannot reach `entries=2 ok=2`. It also cites `(S131)` while row S131's used-by (`corpus/SOURCES.md:152`) lists only the r23 entry, which risks the C2 kill rule "any admitted entry citing a row not appended / used-by exact". My draft carries a passing Gate and refers to the sibling entry by path only; copying the w1 file over the corpus path resolves both.
5. **Q54 holds for the docs locator.** `§ OPTIONS` resolves to `git-fetch.1.txt:2995` (`<h2 id="_options">OPTIONS</h2>`); the Gate's only § token, so `locators=1 locators_bad=0`. Inline-sourced python: `census/round-26/sources/git-fetch.1.txt:3190-3193` (four spellings), `3199-3202` (the default sentence).
6. **Refused subset is absent and recorded.** No `S119`/`S120`/`S121` token appears in the draft (`grep -cE 'S119|S120|S121'` → 0). The `## Limits` bullet cites `corpus/lessons/round-26.md` `## Gate` (landed during this run, 4385 B) and paraphrases its recorded reasons: unprovable zh/ja version alignment, vendor page quoting an older workflow. It does not cite their rows.
7. **One literal `|` remains in the draft**, inside the `recheck:` pipeline only (`line 5`); the Gate block and every row-shaped line are pipe-free. A pipe is intrinsic to the staged re-grep command; flagged in case any check is stricter than the frozen row rule.
8. **Coverage-map side already consistent.** `corpus/README.md:39` (uncommitted modification by another seat) names both `knowledge/git-auto-maintenance-trigger-set.md` and `…-trigger-set-r23.md` under the F1 ground cell; the draft's `ground: F1` line matches K1's `^ground: F1` form.

## Attack log

None — this is a draft seat, not an attack seat. No counter, predicate or case set was disputed; Findings 1-3 are locator/wording corrections inside the admitted entry, not changes to the frozen contract.

## Bounds

- Wrote only `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md` and this report. No git/jj mutation, no writes under `corpus/`, `census/`, `tools/`, or outside `souji-shokunin/`; `/home/vgpnk/Projects/shokuknow` opened read-only.
- Scratch `/var/tmp/souji-r26-ScribeEntryA/` (tarball, six upstream copies) removed before yield; no `/tmp` use.
- No tools installed or upgraded; no pacman transaction; `python3 -B` used throughout.
- Not verified by this seat: C2 as a whole (K1-K4), entry B, registry rows S128-S132 as landed cells. Only the entry A draft, its gate and its Q54 locator are claimed.
