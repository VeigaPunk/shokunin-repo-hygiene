# ReviewQualityBar — round-24 admission bar for the F2 entry and its SOURCES rows

Seat: L1Souji24.ReviewQualityBar (read-only reviewer). Lane rev `f9db2181647d91470a724a12d626bd6106805076` (HEAD = preregistration commit). Date 2026-10-25.
No scratch created, no tools installed or upgraded, nothing written except this report.

## Status
STATUS: PARTIAL — the bar, the commit list and the exact gate command are complete. I did not run the gate on the new entry because it does not exist yet. I also report one scope deviation of my own (Finding 0).

## Evidence
- `sha256sum corpus/QUALITY.md tools/souji-gate-check.py tests/fixtures/r23-locator-heading.py` gave `3fe34abb…a247ef`, `d5ed0805…cdc9d` and `120807e6…39acb8`. The gate digest equals the `tool_sha256=` in `census/round-23/records/gate-check-c3.tsv:4`, so the gate is unchanged since r23.
- `python3 -B tools/souji-gate-check.py --help` gave rc=0 and the usage `[--root ROOT] [--round-date ROUND_DATE] [--entries ENTRIES [ENTRIES ...]] [--snapshot-dir SNAPSHOT_DIR] [--slice SLICE_REL] [--slice-verdicts VERDICTS_REL] [--selftest]`. I also ran `--help` for `souji-landing-gate.py`, `souji-receipt-run.py`, and `souji-receipt-run.py run` and `verify`, all rc=0. These are the only lane tool runs I made.
- `sha256sum -c census/round-23/sources/SHA256SUMS --status` run from the lane root gave rc=0, so all 5 snapshots match. The paths inside are lane-relative, so the same check fails if run from inside `sources/`.
- `git ls-tree -r --name-only HEAD census/round-23/sources` lists `SHA256SUMS`, `csdn-count-objects-vh.raw`, `git-count-objects.1.txt`, `git-fsck.1.txt`, `git-prune.1.txt` and `qiita-gc-auto.raw`. `census/round-24/` does not exist yet.
- r23 gate argv, from `census/round-23/records/gate-check-c3.tsv:5`: `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md --snapshot-di…`. It used `--slice census/round-23/records/empty-slice` and the result was `slice_verdicts=0 slice_total=0`.
- Wave plan: `.ufo/waves/round-24/w1-spec.json` names the entry `count-objects-linked-worktree-garbage.md` ("placeholder name; the L1 confirms").
- Rendering the installed `git-worktree` man page at `MANWIDTH=100` hyphenates lines, for example `ex‐ cept refs/bisect` and `direc‐ tory`. At `MANWIDTH=2000 … | col -bx`, DETAILS is line 167 and the next heading, `LIST OUTPUT FORMAT`, is line 182, with whole unbroken sentences.

## Findings

### 0. Own deviation (disclose; void nothing else)
While looking for the SOURCES contract file I ran `rg -n 'SOURCES-CONTRACT-v1' -l . ../` from the lane root. That search covered the fleet root (`../`, including `.scratch/` and `.ufo/state/`) and the lane's untracked `census/operator-sweep-20261019/`. Under Q45/Q47 that is a V-RECURSIVE / V-READ-ROOT shape.
- What was printed: only 5 matching paths, all inside the lane (`corpus/lessons/round-12.md`, `corpus/SOURCES.md`, `census/round-12/planner.md`, `postreview.md`, `sources-census.sh`).
- No content from a forbidden tree was printed or used. No finding below depends on it.

### 1. Criteria a new F2 knowledge entry must pass (`corpus/QUALITY.md`, line = row)

| Q | line | one-line test for this entry |
|---|---|---|
| Q1 | 25 | `verified-at:` names git 2.56.0 (tag and host), and `recheck:` re-runs on the host version (`on-release`, as S115–S117 do). |
| Q2 | 26 | Every code claim cites `<file>@v2.56.0:<line>` (path.c, builtin/count-objects.c, odb/source-packed.c), or cites the committed fixture `tests/fixtures/r24-size-census.py`. Installed behaviour outranks prose. |
| Q3 | 27 | Applies only if the entry states a deletion mechanism (prune or `--lost-found`). If it does, the body names a located failure case. [INFERENCE: a read-only census entry is otherwise out of scope.] |
| Q4 | 28 | Any fixture or recheck the entry cites runs under `/var/tmp` only and cleans up. Test: `grep -c 'TMPDIR:-/tmp'` → 0 and `grep -c '/var/tmp'` ≥ 1, plus a trap or finally. |
| Q13 | 37 | The lane measurement lands at `census/round-24/size-census-lane.txt`, and nothing new appears at the repo root. |
| Q17 | 41 | Every fixture or evidence path the entry names is a regular, non-symlink file at the landing revision. |
| Q23 | 57 | The wording stays within what was exercised: a lane-only figure, the common-dir figure for a linked worktree, and no fleet claim (the preregistration says "no fleet figure is claimed"). |
| Q25/Q31/Q35 | 64/80/84 | The landing gate resolves every path token in the entry, README and lesson at the tip (`LG-DANGLING-PTR`). Snapshots, fixture, tool and records must therefore be committed in or before the landing commit. |
| Q37/Q40 | 91 | Any `measured_commit` or receipt `rev=` is a full 40-hex id on a durable ref (not `refs/jj/*`, not HEAD). |
| Q50 | 114 | The ADMIT/REJECT wording does not overstate operator authority. |
| **Q54** | 128 | Every `§ <NAME>` in the Gate must resolve to a heading-like line in one of the Gate's own `snapshot:` files (see Finding 4 for the run command). Quote: "must have every `§ <NAME>` locator resolve to a heading-like line in one of those snapshots". |
| **Q55** | 129 | Every count in the entry, README, SCORECARD or LOG (the `garbage=`/`unreachable=` figures and the gate counts line) names a receipt binding `rev=` and `tool_sha256=`. `souji-receipt-run.py verify --root . <receipt>` must exit 0. |

`tools/souji-gate-check.py` (lines 7–16 docstring, `check_entry`) is the machine bar for the assimilated entry:
1. A `## Gate` section exists.
2. The Gate has at least one `https://` URL and the line `opened: 2026-10-25`.
3. Each quote line has a double-quoted span of at most 25 words plus a locator token (`§`, "section", "line ", "lines", "paragraph", DESCRIPTION, OPTIONS, COMMANDS, SYNOPSIS or "heading").
4. Each quote appears verbatim, whitespace-collapsed, in the `snapshot:` named on the same line, and that snapshot is inside `--snapshot-dir`. Quote from the docstring: "every quoted span appears verbatim (whitespace-collapsed) in the committed snapshot the same line names via 'snapshot: <path>'".
5. Every `source: S<nnn>` resolves in `corpus/SOURCES.md`.
6. The Gate has at least one `- ADMIT:` and at least one `- REJECT:`, each with `reason:`.

C2 coupling (preregistration lines 120–121): the entry needs a `ground: F2 …` front-matter line, and its basename must appear in the F2 row's `entries` cell of `corpus/README.md`. Otherwise MISSING-FROM-MAP leaves mismatches above 0.

### 2. Criteria a new SOURCES row must pass
- **Contract v1 shape** (`census/round-12/sources-census.sh`, copied from SOURCES-CONTRACT-v1):
  - 11 cells. Quote from line 5: "# malformed rows — 11 columns means NF=13; must print 0". So no `|` may appear anywhere in a row, which matters for C code such as `||`.
  - The id is unique, tier is in `A B C`, and kind is one of `spec docs paper code tool dataset talk book community own-work` (path.c and count-objects.c rows are `code`). Status is `queued`, `mined` or `rejected`. A `community` row is never tier A.
  - A `mined` row's `used-by` paths must exist from the lane root, so the entry must land in the same commit as its rows.
- **Anchor**: follow the S009/S037/S064 precedent, which gives tag, file, function and `:line`. Example: `tag v2.56.0 (a018953688f1b10bddf91bff8747068f5f4746a4) path.c common_dir:89-96, common_list:98-124, report_linked_checkout_garbage:365-385` (the line numbers come from ScoutPathC, which I did not re-derive).
- **git-worktree**: S003 (2.55.0) and S058 (2.56.0, `config.worktree` scope only) already cite this URL. A new row is allowed only with a different scope, and the provenance paragraph must say so (the S049/S057/S059 precedent).
- **Ids**: the next free lane id is S120. The staged package also uses S120–S123 (`.ufo/waves/round-24/assimilation/staged-ids:12-15`). Mint lane ids, re-point citations by document as in r22 (LOG.md: "citations were re-pointed by document"), and record the new collision count.
- **Provenance paragraph**: the SOURCES header has `Round-N provenance` paragraphs only up to round 19. S100–S119 (r20–r23) have none (`rg -n '^Round-?2[0-4]' corpus/SOURCES.md` returns nothing). r24 should add one that names the new ids, the open date, and where the located quotes live. This is a convention, not a Q criterion.
- **Located quote (fleet floor and the contract's "a quote its location")**: each row's quote is at most 25 words and pipe-free, copied from bytes opened this round, and sits in the entry Gate and the round lesson Gate.

### 3. What the L1 must commit this round for the planned entry
All snapshots go under **one** directory, `census/round-24/sources/`. The gate confines check 4 to a single `--snapshot-dir` (`check4-snapshot-outside-dir`), so a Gate that also quotes `census/round-23/sources/*` fails. Re-commit any r23 page the entry quotes, or do not quote it.
1. `census/round-24/sources/path.c@v2.56.0` (the name is the L1's choice):
   - Commit the **whole file**, not an excerpt, so every `:line` anchor can be checked with `sed -n <n>p` against committed bytes.
   - sha256 must equal ScoutPathC's `f98ba3446d768e3cd9ce8411d5707e35af576a7bd7ad2e7365d26759125d21d2` (identical from GitHub raw and kernel.org).
2. `census/round-24/sources/count-objects.c@v2.56.0`, the whole file (ScoutCountObjectsC: `ec13ae40…e03e`).
   - If the entry cites `report_garbage`, which is in `odb/source-packed.c` at v2.56.0 per ScoutCountObjectsC, commit that file too (`bfb57f4c…21d2`).
3. `census/round-24/sources/git-worktree.1.txt`, rendered from the installed git 2.56.0-1 page with `MANWIDTH=2000 man -P cat git-worktree | col -bx`.
   - At normal width the render hyphenates, so a quote crossing `ex‐ cept` or `direc‐ tory` fails check 4.
   - Copy U+2019 apostrophes as they appear in the page (`repository’s`).
   - If the entry quotes the live HTML page instead, commit that page (ScoutWorktreeDoc: HTML sha256 `fa25690b…`).
   - Record the render command, because r23's `git-count-objects.1.txt` digest does not match a `MANWIDTH=2000` render and its render width cannot be recovered from its bytes.
4. `census/round-24/sources/SHA256SUMS` with lane-relative paths, checked from the lane root with `sha256sum -c census/round-24/sources/SHA256SUMS`. This follows the r23 convention; no Q-row requires it.
5. Slice evidence: `census/round-24/quarantine-slice` (or cite the committed `.ufo/waves/round-24/assimilation/quarantine-slice`) and `census/round-24/slice-verdicts.tsv`.
   - The verdicts file needs one `<id>\t<present|accepted|unverifiable|refused>\t<evidence>` row for each of S114, S118, S123, S124, S126, S131, S133 and S138.
6. The entry itself, its SOURCES rows, the README F2 row update, `census/round-24/size-census-lane.txt`, and a gate receipt under `census/round-24/records/`, all in or before the landing commit (Q31/Q55).

### 4. Exact gate commands for the new entry (run from the lane root at the landing tip)
```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
  --entries corpus/knowledge/count-objects-linked-worktree-garbage.md \
  --snapshot-dir census/round-24/sources \
  --slice census/round-24/quarantine-slice \
  --slice-verdicts census/round-24/slice-verdicts.tsv
# target: entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0, exit 0
python3 -B tests/fixtures/r23-locator-heading.py \
  --entries corpus/knowledge/count-objects-linked-worktree-garbage.md \
  --snapshot-dir census/round-24/sources        # Q54: locators_bad=0; must report locators>0 (Finding 5b)
python3 -B tests/fixtures/r23-locator-heading.py --selftest --snapshot-dir census/round-23/sources   # 2/2 control
sha256sum -c census/round-24/sources/SHA256SUMS
python3 -B tools/souji-receipt-run.py run --root . --rev <full40-landing> --tool tools/souji-gate-check.py \
  --out census/round-24/records/gate-check-c1.tsv python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 …(same argv)
python3 -B tools/souji-receipt-run.py verify --root . census/round-24/records/gate-check-c1.tsv
```
Notes on these commands:
- Replace the entry name if the L1 renames the placeholder.
- The Q54 fixture resolves `snapshot:` relative to the **cwd**, so it must run from the lane root.
- The receipt-run argv shape comes from `run --help` (`--root --rev --tool --out` followed by positional `command ...`) and the r23 `cmd=` line. The exact positional separator is [INFERENCE], since I did not execute it.

## Attack log
5a. **Default-slice false green (operability/calibration).** `souji-gate-check.py:299-301` defaults `--snapshot-dir`, `--slice` and `--slice-verdicts` to r22 paths, and both slice files still exist at HEAD (`git cat-file -e` succeeded for both). If r24 runs without the three flags, the gate scores the r22 8/8 slice and r22 snapshots: the slice part goes green while the r24 slice is never checked. The flags in Finding 4 are mandatory.

5b. **Vacuous Q54 pass.** In `r23-locator-heading.py`, only `§` tokens count as locators, and line 142 is `return 0 if bad == 0 else 1`. A Gate whose locators are all of the "line N" form, which suits C snapshots, reports `locators=0` and exits 0. C source has no heading lines, so a `§` locator on a path.c line can only pass by matching a heading from another snapshot (5c). Nothing machine-checks that a quote actually sits at the line it cites. The L1 must check `sed -n <n>p census/round-24/sources/path.c…` by hand or with its own check.

5c. **Q54 substring and union matching.** Line 115 is `if not head or not any(head.lower() in h for h in heads):`. The heading set is the union over all of the Gate's snapshots, and matching is by substring. Consequences:
- `§ D` or `§ OPT` passes.
- A `§ DETAILS` locator on a path.c quote line passes because git-worktree.1.txt has DETAILS.
- The locator is not bound to the snapshot on its own line, so Q54 is weaker than its prose "the Gate's own snapshot".
- I am reporting this, not proposing a change: Q54 is r23 bar text, not an r24 frozen counter.

5d. **Date-only freshness.** Check 2 accepts `opened: 2026-10-25`, which is also r23's date. The preregistration requires "every cited source re-opened this round", and the gate cannot tell an r23 opening from an r24 one. Evidence of reopening has to come from this round's fetch digests (ScoutPathC/ScoutCountObjectsC/ScoutWorktreeDoc sha256 equal to the committed snapshots). That is not machine-enforced.

5e. **Locator prose bypass.** The check-3 probe (`QUOTE_RE.sub("", SNAPSHOT_RE.sub("", line))`) searches the whole remaining line, reason prose included, case-insensitively. A reason that contains "line " or "section" satisfies the locator check with no real locator.

5f. **Id ambiguity in slice verdicts.** Slice ids S114 and S118 are staged ids that also name different lane rows (S114 statx, S118 Qiita). `check_slice` keys only on the id string, so a verdict row cannot show which document it judged. Each evidence cell should name the staged document, not only the id.

5g. **Empty-slice precedent.** r23 passed with `slice_total=0` because it ran against an empty slice. r24 has a real 8-row slice (preregistration line 131), so reusing an empty slice would satisfy V==T without any hand-checks.

## Residual risk / verification gaps
- The gate and the Q54 fixture were not run on the new entry, because it is absent at this revision. Unrun checks have not passed.
- I did not re-fetch path.c or count-objects.c; their digests and line numbers come from peer seats.
- I did not read SOURCES-CONTRACT-v1 itself; the row shape is from the lane's verbatim copy, `census/round-12/sources-census.sh`.
