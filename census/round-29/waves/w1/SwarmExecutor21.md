# SwarmExecutor21 — SOURCES.md revision-diff instrument

## Status
STATUS: PASS — `.ufo/waves/round-29/w1/deliver-sources-diff.py` (252 lines, stdlib only, sha256 `52829de2b29b5e179ad5e8eae747778acb77aeb30b64927584fabb0b5b769ba9`) implements `--root LANE --from REV --to REV` over `git show` bytes, prints rows before->after, tier and status histograms, added ids with tier/status/kind, and per-column in-place changes with `APPEND-ONLY-VIOLATION`; verified on the r28 range (135 -> 139, S212-S215, zero in-place changes) with counts identical to the CORPUS.md census one-liners at both revisions, and on seven scratch probes (tier violation rc 1, status change rc 0, cell padding on a mutable vs a protected column, 2-space/4-space indent tolerance, dirty-worktree immunity, malformed row plus duplicate id rc 1, removed row rc 1) plus three argument-error paths (rc 2).

## Evidence

Usage and contract of the tool:

```
python3 -B deliver-sources-diff.py --root LANE --from <40-hex> --to <40-hex> [--width N]
# reads corpus/SOURCES.md at both revisions via `git -C LANE show REV:corpus/SOURCES.md`
# exit 0 clean; 1 APPEND-ONLY-VIOLATION / SHAPE-VIOLATION / duplicate id / malformed row; 2 usage, git or read error
```

### 1. Primary run — r28 range (lane work tree, committed bytes)

```
$ python3 -B .ufo/waves/round-29/w1/deliver-sources-diff.py --root . \
    --from 3a2a80d0d18940a5e352ebc526da22a57dad83c4 \
    --to   fec846dd1781a414ae3a7d71d2d8fa2fb17900eb
SOURCES.md diff  /home/vgpnk/Projects/shokunin/souji-shokunin
from 3a2a80d0d18940a5e352ebc526da22a57dad83c4  round-27 verifier spot-check (integrator, hyaku): non-author admit/reject
to   fec846dd1781a414ae3a7d71d2d8fa2fb17900eb  round-28: pin after measurements and source recheck receipts
rows 135 -> 139  (+4 -0)
indent before: 0-spaces=135 1-3-spaces=0
indent after:  0-spaces=139 1-3-spaces=0
tier before:   A=128 B=5 C=2
tier after:    A=132 B=5 C=2
status before: queued=15 mined=111 rejected=9
status after:  queued=15 mined=115 rejected=9
  + S212  tier=A status=mined kind=spec
  + S213  tier=A status=mined kind=spec
  + S214  tier=A status=mined kind=spec
  + S215  tier=A status=mined kind=docs
added: 4  removed: 0
changed cells (ids in both revisions):
changed_ids: 0  cell_changes: 0
SUMMARY rows_before=135 rows_after=139 added=4 removed=0 changed_ids=0 cell_changes=0 violations=0 malformed=0 dups=0
rc=0
```

Matches the assigned expectation (rows 135 -> 139, S212-S215 added). No in-place cell changed in the window, so the r28 source landing was append-only.

### 2. Cross-check against the CORPUS.md census one-liners, same two revisions

```
$ for R in 3a2a80d0d18940a5e352ebc526da22a57dad83c4 fec846dd1781a414ae3a7d71d2d8fa2fb17900eb; do echo "== $R"
    git show $R:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
    git show $R:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print "malformed="n+0}'
    git show $R:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}'
    git show $R:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}'
  done
== 3a2a80d0d18940a5e352ebc526da22a57dad83c4
135
malformed=0
A=128 B=5 C=2
mined=111 queued=15 rejected=9
== fec846dd1781a414ae3a7d71d2d8fa2fb17900eb
139
malformed=0
A=132 B=5 C=2
mined=115 queued=15 rejected=9
```

Rows, tier histogram and status histogram agree exactly with the tool's output; `malformed=0` at both revisions. Added-row metadata cross-checked independently:

```
$ git show fec846dd1781a414ae3a7d71d2d8fa2fb17900eb:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (i ~ /^S(21[2-5])$/) printf "%s tier=%s status=%s kind=%s\n", i,t,s,k}'
S212 tier=A status=mined kind=spec
S213 tier=A status=mined kind=spec
S214 tier=A status=mined kind=spec
S215 tier=A status=mined kind=docs
```

### 3. Synthetic tier violation — scratch clone (`git clone -q --no-local <lane> $D/c`)

Scratch was `/var/tmp/souji-r29-SwarmExecutor21.lULAP6` (`git -C "$D/c" rev-parse --show-toplevel` printed `/var/tmp/souji-r29-SwarmExecutor21.lULAP6/c`; throwaway identity set with `git -C "$D/c" config` only). Commits there, never elsewhere:

```
73e8a68  scratch: S005 status queued -> mined (legit in-place column)
a1a7177  scratch: S002 tier A -> B (synthetic append-only violation)
10526a5  scratch: S003 anchor double space (whitespace-only)
e91214b  scratch: cell padding on S006 status (mutable) and S007 tier (protected)
```

Tier flip, final script bytes, exit code captured without a pipe:

```
$ python3 -B deliver-sources-diff.py --root $D/c \
    --from 73e8a682ce2bc075f00117adcf3a346000232b0d --to a1a7177be244d4356a6365f67f82e09d353a62e9
tier before:   A=132 B=5 C=2
tier after:    A=131 B=6 C=2
  ~ S002 tier: A -> B  APPEND-ONLY-VIOLATION
SUMMARY rows_before=139 rows_after=139 added=0 removed=0 changed_ids=1 cell_changes=1 violations=1 malformed=0 dups=0
tier-violation rc=1
```

Legitimate status change, same tool, rc 0 (only `status`, `recheck`, `used-by` are mutable):

```
  ~ S005 status: queued -> mined
SUMMARY rows_before=139 rows_after=139 added=0 removed=0 changed_ids=1 cell_changes=1 violations=0 malformed=0 dups=0
rc=0
```

Internal-whitespace edit inside a protected column (`anchor` double space at `10526a5`) is reported and flagged, rc 1:

```
  ~ S003 anchor: § COMMANDS lock, prune; ... -> § COMMANDS  lock, prune; ...  APPEND-ONLY-VIOLATION
```

Cell-padding probe in a fresh fixture repo (`$D/fx`, base = r28-from bytes, commit `26a73b1` -> `8265cff`), final script bytes:

```
  ~ S006 status: queued -> queued (whitespace-only:  queued  ->   queued  )
  ~ S007 tier: A -> A (whitespace-only:  A  ->   A  )  APPEND-ONLY-VIOLATION
SUMMARY rows_before=135 rows_after=135 added=0 removed=0 changed_ids=2 cell_changes=2 violations=1 malformed=0 dups=0
rc=1
```

### 4. Census fidelity — 0-3 leading spaces, 4+ ignored (clean fixture repo)

Fixture base = `3a2a80d...:corpus/SOURCES.md` (commit `7e1b154`), after = same plus a 2-space-indented `S998` row and a 4-space-indented `S999` row (commit `0f4753b`):

```
rows 135 -> 136  (+1 -0)
indent before: 0-spaces=135 1-3-spaces=0
indent after:  0-spaces=135 1-3-spaces=1
  + S998  tier=A status=queued kind=docs
SUMMARY rows_before=135 rows_after=136 added=1 removed=0 changed_ids=0 cell_changes=0 violations=0 malformed=0 dups=0
indent-tolerance rc=0
```

Same revision through the two census spellings:

```
$ git show 0f4753b:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'          # frozen v1, column-zero
135
$ git show 0f4753b:corpus/SOURCES.md | grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'    # maintained-parser note
136
```

The tool implements the maintained-parser tolerance (136); `S999` at 4 spaces is invisible to both, as the note requires.

### 5. Committed-bytes property (no worktree read)

With `git status --short` showing ` M corpus/SOURCES.md` (an uncommitted teaches edit) in the scratch clone, the same two committed revisions produced the identical result as on a clean worktree: `rows 139 -> 139 ... changed_ids=1 cell_changes=1 violations=1`, i.e. only the committed S002 tier flip. The uncommitted text never entered the diff.

### 6. Shape and id guards — malformed row, duplicate id, removed row (fixture repos)

Fixture `$D/fx` base commit `17ee3e8` (two well-formed rows); after commit `ba527f9` drops S001's `used-by` cell and appends a second `S002`:

```
rows 2 -> 3  (+0 -0)
tier before:   A=1 B=1        tier after:    A=1 B=1 C=1
status before: queued=1 mined=1   status after:  queued=1 mined=2
  ~ S001 shape: 13 fields -> 12 fields  SHAPE-VIOLATION
  ~ S001 used-by: — -> 
  ! after line 5 S001: 12 fields, expected 13  MALFORMED
  ! duplicate id S002 (extra rows before=0 after=1)
SUMMARY rows_before=2 rows_after=3 added=0 removed=0 changed_ids=1 cell_changes=1 violations=1 malformed=1 dups=1
rc=1
```

Census rows (3) exceed id-keyed ids (2) exactly by the duplicated row, and the id-keyed diff reports it; nothing is silently dropped. The `used-by` cell edit is a mutable column, so only the shape change is counted as a violation.

Removal probe (fixture `7871c31` two rows -> `147f493` one row): append-only forbids dropping a row, so it exits 1.

```
rows 2 -> 1  (+0 -1)
  - S002  tier=B status=mined kind=docs  APPEND-ONLY-VIOLATION
SUMMARY rows_before=2 rows_after=1 added=0 removed=1 changed_ids=0 cell_changes=0 violations=1 malformed=0 dups=0
rc=1
```

Renumbering a row therefore surfaces as `removed=1` plus `added=1` and a violation, never as a silent in-place edit.

### 7. Argument validation

```
$ deliver-sources-diff.py --root . --from 3a2a80d --to fec846dd...
error: --from must be a full 40-hex revision, got '3a2a80d'                  rc=2
$ deliver-sources-diff.py --root . --from 0000...0000 --to fec846dd...
error: git show 0000...:corpus/SOURCES.md failed: fatal: path 'corpus/SOURCES.md' exists on disk, but not in '0000...'   rc=2
$ deliver-sources-diff.py --root /var/tmp --from 3a2a80d... --to fec846dd...
error: not a git work tree: /var/tmp                                        rc=2
```

Row parsing reuses the existing lane convention rather than inventing a second one: `tools/souji-registry-agreement.py:17` `ROW = re.compile(r'^ {0,3}\|\s*(S\d{3,})\s*\|')` and `l.split('|')` + strip (its `c[1]` id, `c[11]` used-by are this tool's `cells[0]`, `cells[10]`; awk field numbers $2/$4/$5/$9/$12 match the census one-liners).

Scratch removed: `ls -d /var/tmp/souji-r29-SwarmExecutor21*` prints nothing. No tool installs or upgrades were made. Lane writes: the delivery file and this report only.

## Findings

1. **r28 source landing was append-only clean.** Between `3a2a80d0d18940a5e352ebc526da22a57dad83c4` and `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb`, `corpus/SOURCES.md` gains rows S212-S215 (A/spec, A/spec, A/spec, A/docs) and changes no in-place cell (`changed_ids=0`, `violations=0`, exit 0). Location: `corpus/SOURCES.md` rows S212-S215.
2. **Two census spellings diverge only by design, and today agree.** The frozen v1 one-liner (`^\|`) is column-zero-only; the maintained-parser note at `/home/vgpnk/Projects/shokunin/CORPUS.md:152-155` grants 0-3 leading spaces (frozen census one-liners at `/home/vgpnk/Projects/shokunin/CORPUS.md:133-147`; the lane has no `CORPUS.md` of its own). Both target revisions carry zero indented rows (`indent before/after: 0-spaces=135/139`), so 135/139 hold under both spellings; a future indented row would make the frozen one-liner undercount by one per indented row.
3. **Tracked byte-code inside the lane.** Five `__pycache__` `.pyc` files are tracked at HEAD: `.ufo/waves/round-26/assimilation/validate/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc`, `.ufo/waves/round-26/assimilation/validate/tools/__pycache__/{souji-axis-check,souji-gate-check,souji-landing-gate}.cpython-314.pyc`, `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (`git ls-files | grep __pycache__`). Hygiene defect, outside this seat's write scope: no action taken.
4. **The delivery file is untracked by design.** `.gitignore:1` is `.ufo/waves/`, so `git status` does not show any round-29 wave artifact; landing needs `git add -f` or a copy into `tools/`. Location: `.gitignore:1`.
5. **Renumbered rows are indistinguishable from remove+add.** If a row's `id` cell is edited, the tool reports the old id removed (violation, exit 1, measured in §6's removal probe) and the new id added (measured on the r28 additions), but it cannot attribute the edit to one row, so a renumber looks like a removal defect rather than an in-place edit. `[INFERENCE]` for the combined case only; not observed in the r28 window.
6. **Whitespace-only edits are strict.** Raw bytes in a protected column are compared, so a padding-only change (`| A |` -> `|  A  |`) is reported `(whitespace-only: ...)` and still flagged; a padding-only change in `status`/`recheck`/`used-by` is reported without a violation. This is stricter than a trimmed-value comparison and cannot hide an edit.

## Attack log

Not an attack seat; no counter, predicate or case set was attacked or amended. Finding 5 is the only gaming path observed while building the instrument, and it only suppresses attribution, not detection.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-sources-diff.py` — sha256 `52829de2b29b5e179ad5e8eae747778acb77aeb30b64927584fabb0b5b769ba9`, 252 lines, stdlib only (`argparse`, `re`, `subprocess`, `sys`, `collections`).
- `.ufo/waves/round-29/w1/SwarmExecutor21.md` — this report.
