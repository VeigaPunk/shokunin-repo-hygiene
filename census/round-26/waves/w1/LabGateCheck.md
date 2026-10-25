# LabGateCheck — C2 K2 gate command, dry run before scoring

## Status
STATUS: PASS — probe executed, red arm demonstrated, every check named, frozen CLI matches. But the tip red is NOT the predicted "entries absent": the two committed admitted entries carry no `## Gate` heading, so K2 fails for check1, while the untracked staged copies at the same path do go green.

## Evidence

### 1. Red arm at the base revision (entries genuinely absent)
Base tree extracted read-only (`git -C <lane> archive 0eca7c8 | tar -x -C /var/tmp/souji-r26-LabGateCheck/base`); tool invoked from the lane, `--root` at the extracted tree, same flags and dates as the frozen K2:

```
FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md entry-missing: corpus/knowledge/git-auto-maintenance-trigger-set.md
FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md entry-missing: corpus/knowledge/git-auto-maintenance-trigger-set-r23.md
FAIL slice slice-missing
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=3
EXIT=1
```
`git cat-file -e 0eca7c8:corpus/knowledge/git-auto-maintenance-trigger-set.md` -> `fatal: ... not in 0eca7c8` (rc 128). Gate fires. Third failure is expected: `census/round-26/records/empty-slice` is a tip-only artifact.

### 2. Red at the current tip, on the admitted paths (the live defect)
Exact command from the brief (absolute `--root`, 2026-10-25), run at HEAD `d2e6253`:

```
FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md check1-no-gate: corpus/knowledge/git-auto-maintenance-trigger-set.md
FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md check1-no-gate: corpus/knowledge/git-auto-maintenance-trigger-set-r23.md
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2
EXIT=1
```
The prereg's literal form `--root .` produces the identical two lines and `EXIT=1`, so the absolute/relative root forms agree. Entry sha256 at measurement: `69775ab0…b7b25f` (A, mtime 14:20:45), `8adbb1fb…65f6f9` (B, 14:21:11); `git status --porcelain` for both paths is empty, so these are the committed bytes, not a dirty worktree. `git show HEAD:<entry> | grep -cE '^## Gate'` -> `0` and `0`. Committing commits: `0833de9` (both), `ea0bbe6` (Entry B enriched).

### 3. Green control at the same flags — the gate is data-sensitive, not broken
Untracked staged copies under `w1/` (14:30) carry `## Gate` (B at line 102) and pass:
```
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
EXIT=0
```
Tool selftest: `python3 -B tools/souji-gate-check.py --selftest` -> `selftest=9/9`, `EXIT=0`.

### 4. CLI confirmation (frozen command == actual CLI)
`argparse` at `tools/souji-gate-check.py:296-302` declares exactly `--root` (default `.`), `--round-date`, `--entries` (`nargs="+"`), `--snapshot-dir`, `--slice` (dest `slice_rel`), `--slice-verdicts` (dest `verdicts_rel`), `--selftest`. The prereg K2 spelling uses all six with those exact names; `--round-date` and `--entries` are the only required pair when not selftesting, and both are supplied. No flag rename, no positional drift, no `--slice-verdict`/`--verdicts` alias. CLI is a verbatim match.

### 5. Every check the tool runs (line-anchored)
| # | Check | Failure label(s) |
|---|---|---|
| 1 | entry file exists; `\n## Gate` section present (`text.find`, L56) | `entry-missing` L69; `check1-no-gate` L74 |
| 2a | Gate names >=1 `https://` URL | `check2-no-url` L76 |
| 2b | Gate carries `opened: <round-date>` with the exact date | `check2-opened-date` L79 |
| 3a | every double-quoted Gate line span has a locator token after `snapshot:` is stripped | `check3-no-locator-gate-line-N` L89 |
| 3b | quoted span <=25 whitespace-collapsed words | `check3-quote-N-words-gate-line-N` L95 |
| 3c | >=1 located quote with a resolvable snapshot exists | `check3-no-located-quote-with-snapshot` L116 |
| 4a | the quote's Gate line names `snapshot:` | `check4-no-snapshot-named-line-N` L98 |
| 4b | snapshot realpath is inside `--snapshot-dir` | `check4-snapshot-outside-dir-line-N` L104 |
| 4c | snapshot file exists | `check4-snapshot-missing-line-N` L107 |
| 4d | quote appears verbatim, whitespace-collapsed, in the snapshot bytes | `check4-quote-absent-from-snapshot-line-N` L112 |
| 5a | at least one `source: S<digits>` line exists in the entry | `check5-no-source-citation` L125 |
| 5b | every cited id resolves to a `^\s{0,3}\|\s*(S\d{3,})` row in `corpus/SOURCES.md` | `check5-dangling-source` L128 |
| 6a | Gate has >=1 `- ADMIT:` | `check6-no-admit` L131 |
| 6b | Gate has >=1 `- REJECT:` | `check6-no-reject` L133 |
| 6c | each ADMIT/REJECT row carries `reason:` + a non-space, non-dash char | `check6-row-without-reason` L136 |
| S | slice file must exist | `slice-missing` L146 |
| S | verdict row `id<TAB>class<TAB>evidence`, class in present/accepted/unverifiable/refused, non-empty evidence, unique id | `verdict-short-row`, `verdict-bad-class`, `verdict-no-evidence`, `verdict-duplicate` L161-171 |

Exit contract: `0` iff `ok == n and v == t and total_f == 0`, else `1` (L196); argparse exits `2` on a missing required flag. Counts line at L20-21. The tool writes nothing (`Read-only; no writes anywhere`, docstring L23) except its own `/var/tmp` selftest sandbox, which it removes.

## Findings

1. **K2 cannot go green on the committed entries.** Both admitted paths at HEAD `d2e6253` have zero `## Gate` headings; the gate short-circuits at `check1-no-gate` before any provenance work runs. The Gate text exists only in the untracked staged copies `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md` and `…-r23.md` (14:30) and in `corpus/lessons/round-26.md:9`. The prereg's as-written K2 target (`entries=2 ok=2 fail=0`, exit 0) is met by the staged bytes and not by the admitted bytes — the Gate sections must land in `corpus/knowledge/` before K2 is scorable. Location: `corpus/knowledge/git-auto-maintenance-trigger-set.md`, `…-r23.md` at HEAD; staged at `.ufo/waves/round-26/w1/`.
2. **The brief's premise was stale, not wrong to test.** At dispatch time the entries were absent; by measurement they were committed (`0833de9`, `ea0bbe6`) but Gate-less. The red arm therefore had to be taken at base `0eca7c8`, where it is `entry-missing` (plus `slice-missing`, because the empty-slice artifacts are tip-only). Location: `tools/souji-gate-check.py:69,146`; base tree from `0eca7c8`.
3. **"pipe-escapes" is NOT a check in this tool.** The brief names it among the gate's checks, but the only `|` in `tools/souji-gate-check.py` is the SOURCES.md row-parse regex at L122; there is no scan of entry or row bytes for a literal or escaped `|`. C2's kill-rule clause "any appended row carrying a literal or escaped `|`" is therefore enforced only by K3 (`scripts/sources-census.sh validate`) and by eye, not by the K2 instrument. Location: `tools/souji-gate-check.py:122`; prereg C2 kill rule.
4. **Q54's heading resolution is unenforced.** `LOCATOR_RE` (L42) only requires one of the tokens `§|section|line |lines |paragraph|DESCRIPTION|OPTIONS|COMMANDS|SYNOPSIS|heading` to appear on the Gate line; nothing resolves the named section against actual heading lines in the snapshot. The C2 clause "any admitted entry's Gate locator failing Q54 (every snapshot § locator resolves to a heading line)" is not mechanically checked by the K2 tool. Location: `tools/souji-gate-check.py:42,83-92`.
5. **`fail=0` does not mean success.** A missing verdict row is deliberately counted in neither `v` nor `f` (comment above L173), so the counts line can print `fail=0` while the process exits `1` on `v != t`. Prereg K2 also demands exit 0, so the frozen literal is not gameable as written; a re-scoring that greps only `entries=2 ok=2 fail=0` would be. Location: `tools/souji-gate-check.py:173-196`.
6. **Locator probe strips the snapshot path but not the URL.** `QUOTE_RE.sub("", SNAPSHOT_RE.sub("", line))` leaves the URL in place, so a URL containing `section`, `paragraph` or `OPTIONS` satisfies check 3a with no real location. All current snapshots are fine, but the check is satisfiable by URL text alone. Location: `tools/souji-gate-check.py:84`.
7. **Quotes over 400 chars are invisible, not failing.** `QUOTE_RE` is `"([^"]{2,400})"`; a longer quoted span is not captured, so it is neither counted nor rejected. Any super-long quote on a Gate line silently escapes validation if another valid quote exists. Location: `tools/souji-gate-check.py:37`.
8. **Selftest covers 6 of 20 failure paths.** `selftest=9/9` exercises `check1-no-gate`, `check2-opened-date`, `check3-quote-words`, `check4-quote-absent`, `check5-dangling-source`, `check6-no-reject`, the `v!=t`/`fail=0` arm, and the always-green control. No fixture exercises `entry-missing`, `slice-missing`, `check2-no-url`, `check3-no-locator`, `check3-no-located-quote`, `check4-no-snapshot-named`, `check4-snapshot-outside-dir`, `check4-snapshot-missing`, `check5-no-source-citation`, `check6-no-admit`, `check6-row-without-reason`, or the four `verdict-*` labels. I am not proposing a change to the frozen r22 fixture set; recording the coverage boundary. Location: `tools/souji-gate-check.py:139-291`.
9. Findings 3, 4 and 5 are the three the L1 should consider logging as ATTACKs: each names a C2 kill-rule clause that the K2 instrument cannot detect. I did not open or run the campaign tools, so I make no claim that K3 covers 3 and 5 in practice beyond the fact that its CLI is the one the prereg names.

## Notes
- Read-only seat: no writes outside this report. Scratch `/var/tmp/souji-r26-LabGateCheck` (base-tree extraction) created and removed; no repo was initialized there.
- Lane revisions used: base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` (confirmed ancestor of prereg commit `89e0fceeefcf28db313c94120be6d25e03c60094`), tip `d2e62533bc485bc68fae2c8ef083af0c36a1e1e3`.
- No tools installed or upgraded this run. No pacman transaction. No `agent://all`.
- Kept out of scope by standing holds: certification OFF, K5 HELD, F5 reap and NAMESPACE holds untouched; `/home/vgpnk/Projects/shokuknow` never written, fetched or executed.
