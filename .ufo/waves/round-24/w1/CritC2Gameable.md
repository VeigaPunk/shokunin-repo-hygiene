# CritC2Gameable — souji r24 w1, attack on C2 (coverage-map agreement)

## Status
STATUS: PASS — attack complete. The frozen C2 predicate reaches `mismatches=0` without real agreement on 8 routes (A1, A2, A3, A3b, A4b, A6, A6b, A7), plus A4 under naive cell splitting. Two further routes hide a dangling path (A5, A6c). Only A1b is stopped by the kill rule. The base control was computed by hand: `grounded=4 mapped=2 dangling=0 mismatches=2`. No C2 tool exists yet, so every result below comes from a literal reference reading of the predicate, not from the lane tool.

## Evidence
Revisions: base `a65fac98964b445758e94c805728c9a19d302ff8`, prereg tip `f9db2181647d91470a724a12d626bd6106805076`. Read-only `git show`, `git ls-tree` and `git archive` against the lane. Scratch at `/var/tmp/souji-r24-CritC2Gameable/` was removed. No tools installed.

- `git ls-tree --name-only a65fac9 corpus/knowledge/` gives 13 files: 12 `.md` plus `obsidian-ledger.tsv`.
- Lines starting `ground:` (all are header lines before the first `#` heading; **no entry has a `---` front-matter block**):
  - `count-objects-garbage-readings-r25.md:5`: "ground: F2 — repository size census (what the two target-language communities say `garbage` counts"
  - `repo-size-census-readonly.md:6`: "ground: F2 — repository size census (the census instruments and the write side effect"
  - `quarantine-staging-no-copy-r23.md:6`: "ground: F4 — restorable quarantine (the staging primitive: no-clobber rename)"
  - `quarantine-origin-record-fields-r24.md:7`: "ground: F4 — restorable quarantine (the read side of a per-item origin record)"
  - Not counted (does not start the line): `git-repo-structure-readonly.md:7`: "Coverage-map ground: F2 repository size census."
- Coverage-map tables at base, matched on header first cell `ground` and third cell starting `entries`: `corpus/README.md` lines 36, 66, 214, 238 and 272. The line-454 table (first cell `claim`) is correctly excluded.
- Reference reader `ref.py`: header-block front matter, GFM `\|` escapes, README read at `--rev`, basename substring match in the third cell, backticked paths ending `knowledge/<name>`.

### Control (expected base output; the L1 should compare the tool's control against this)
```
MISMATCH	MISSING-FROM-MAP	corpus/knowledge/count-objects-garbage-readings-r25.md	ground=F2
MISMATCH	MISSING-FROM-MAP	corpus/knowledge/repo-size-census-readonly.md	ground=F2
grounded=4 mapped=2 dangling=0 mismatches=2      (exit 1; identical at f9db218)
```
How the control was derived by hand:
- The F2-token rows are README:40 (entries `—`), README:68 (entries cell: only `knowledge/git-repo-structure-readonly.md` plus tool/fixture/census paths) and README:217 (`F2 caveat`, entries are `../../.ufo/...` reports).
- Both missing basenames do appear in README:68, but only in the **status** cell: "**r23: the read side now holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md`)". The predicate correctly scores this as missing.
- The F4 entries are both in README:42's entries cell.
- `dangling=0`: all 11 backticked `knowledge/…` paths in entries cells exist (README:38, 39 ×2, 41, 42 ×4, 68, 216, 274).
- `mapped` is not defined in the prereg. Here it means "grounded entries found in the map". The alternative reading, "count of backticked knowledge paths in entries cells", gives `mapped=11`.

How the control changes under other readings:

| tool reading | grounded | mismatches |
|---|---|---|
| `---` YAML front matter | 0 | 0 (**false green at base**) |
| `ground:` matched anywhere in the line (counts `git-repo-structure-readonly.md`, which is mapped at README:68) | 5 | 2 (hand-derived from the lines above; not run) |
| naive split on every `\|` | 4 | 2 |
| fences and HTML comments skipped | 4 | 2 |

### Attack replay
Method: a scratch `git init` repo holding `git archive a65fac9 corpus/README.md corpus/knowledge`; one commit per attack; `ref.py --rev HEAD`.

| attack | result |
|---|---|
| CONTROL (unchanged copy) | `grounded=4 mapped=2 dangling=0 mismatches=2` exit=1 |
| A1 ground swap: rename the 2 unmapped entries' `ground:` key to `ground-was:` and prepend `ground: F4` to 2 already-mapped F4 entries | `grounded=4 mismatches=0` exit=0 |
| A1b rename `ground:` to `Ground:` with no compensation | `grounded=2 mismatches=0` exit=0 (kill rule fires: 2<4) |
| A2 junk row `F2 \| junk \| <names>` | `mismatches=0` exit=0 |
| A3 names placed in the `F2 caveat … no F2 capability claimed` row | `mismatches=0` exit=0 |
| A3b names placed in the superseded `F2 … frontier, no entry` row (README:40) | `mismatches=0` exit=0 |
| A4 names in the status column after an escaped `\|` | GFM split: `mismatches=2` (caught). Naive split: `mismatches=0` |
| A4b negated mention in the entries cell ("withdrawn, not mapped: <names>") | `mismatches=0` exit=0 |
| A5 un-backticked `knowledge/ghost-entry.md` in an entries cell | `dangling=0` |
| A5c the same path backticked (control) | `DANGLING-MAP-PATH knowledge/ghost-entry.md README:68`, `dangling=1` |
| A6 coverage-map-shaped table inside a fenced block | literal reading: `mismatches=0`; fence-aware: 2 |
| A6b the same table inside an `<!-- -->` comment | literal reading: `mismatches=0`; comment-aware: 2 |
| A6c backticked dangling path in a `ground \| entries \| status` table | `dangling=0` (invisible) |
| A7 move the 2 unmapped entries to `corpus/knowledge/archive/` and add 2 compensating F4 grounds | `grounded=4 mismatches=0` exit=0 |

## Findings
1. **Ground swap evades the kill rule (A1, A7). Caught: no. Matters: yes (calibration).**
   - Prereg:91 reads "Kill rule: grounded(tip) < grounded(base) -> C2 fails (no entry may be deleted or un-grounded to reach 0)". It compares a count, not identity.
   - 8 of the 12 `.md` entries are ungrounded but already mapped, so each un-grounding can be offset by grounding one of them at zero map cost.
   - Moving entries out of the non-recursive `corpus/knowledge/*.md` set (A7) is the same hole.
2. **Unanchored F-token rows (A2, A3, A3b). Caught: no. Matters: yes.**
   - Any row whose ground cell starts with `F2` satisfies MISSING-FROM-MAP. That includes:
     - a junk row;
     - the README:217 row, which says "no F2 capability claimed" and "observed, not claimed";
     - the README:40 row, "frontier, no entry (r12 candidate deferred", which only prose supersedes: README:65 "## Round 13 current coverage (supersedes the r12 F2 row)".
   - Mapping an entry into a row that disclaims capability inverts calibration.
3. **Stale status at base that `mismatches=0` will not clear. Caught: no. Matters: yes.**
   - README:40 still declares F2 "frontier, no entry", while 2 F2 entries exist at base and 3 or more at the tip.
   - C2 never compares status cells across rows, so a green C2 can coexist with that contradiction (a duplicate authority).
4. **The front-matter definition is unpinned. Matters: yes (calibration and operability).**
   - Prereg:82–83 reads "an entry corpus/knowledge/<n>.md at rev carrying a front-matter line `ground: F<k>`". No entry has `---` delimiters.
   - A YAML-faithful tool reads `grounded=0 mismatches=0` at base and passes the kill rule (0<0 is false). The control would then never show red.
5. **Non-entries column (A4). Caught: yes under GFM cell splitting; no under naive `split('|')`.**
   - Base README:40 already holds `\|` inside a status cell, so the split choice is live.
6. **Mentions count, existence is unchecked. Caught: no. Matters: low to medium.**
   - "Basename appears" is a substring test, so a negated or withdrawn mention maps the entry (A4b).
   - DANGLING checks only backticked paths, so un-backticked dangling paths (A5) and dangling paths in non-matching table shapes (A6c) are invisible.
   - Not exploited at base: `dangling=0`.
7. **Hidden tables (A6, A6b). Caught: no under a literal line reader; yes if fences and comments are skipped.**
   - The prereg does not say which. Base README has one fence (303–309) and no `<!--`, so skipping them does not change the control.
8. **README revision unspecified. Matters: operability.**
   - DANGLING and entries are scored "at rev"; prereg:77 names "the corpus/README.md coverage-map tables" without a revision. If the tool reads README from the worktree, uncommitted edits can produce a 0.
9. **`mapped=M` is undefined (prereg:80). Matters: calibration of the receipt.**
   - The counts line carries a field with no frozen meaning. Readings give 2 or 11 at base.

## Attack log — smallest safe corrections (no predicate or case-set change; integrator-side disclosure at the landing tip)
- **Findings 1 and 7 (A1, A1b, A7).** `git diff a65fac9 <tip> -- corpus/knowledge/ | grep -E '^-ground:'` must be empty. `git diff --name-status -M a65fac9 <tip> -- corpus/knowledge/` must show no `D` or `R`. Report the base→tip `(basename, F<k>)` set, not only the count.
- **Findings 2 and 3 (A2, A3, A3b).**
  - Name the README line where each of the 2 basenames, plus C1's new F2 entry, lands. The honest target is the README:68 row's entries cell.
  - The README diff must add no row starting `| F2` and no new `| ground` header.
  - Disclose the README:40 stale "no entry" row as a residual, or retire it in the same landing.
- **Finding 7 (A6, A6b).** The README diff must add no line starting with three backticks and no `<!--`.
- **Findings 4, 5, 8 and 9 (tool choices inside the frozen wording).** Pin these in the tool and fixture before any seat scores:
  - front matter = lines before the first `#` heading;
  - GFM `\|` escapes;
  - README read via `git show <rev>:corpus/README.md`;
  - one definition of `mapped`.
  
  The fixture should also assert the base control `grounded=4 mismatches=2` with the two rows above. A tool that prints `grounded=0` at base is the finding-4 false green and should be reported as an ATTACK, not accepted.
- **Impacted axes:** calibration (findings 1–4, 6, 9), operability (findings 5, 8). Coverage is not affected.
