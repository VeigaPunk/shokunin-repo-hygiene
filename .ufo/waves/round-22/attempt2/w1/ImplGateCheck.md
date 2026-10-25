STATUS: PASS

# ImplGateCheck — C2 gate-check candidate, frozen predicate conformance

Seat: L1Souji22.ImplGateCheck (leaf). Item: implement a candidate
`tools/souji-gate-check.py` to the frozen C2 predicate and prove it rejects the
FALSE-GREEN fixture. Nothing in the lane repo was modified: the candidate and
its evidence live only under the named evidence path, and the tool writes
nothing (scratch under `mktemp -d /var/tmp` is removed by the tool itself).

- Candidate: `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/souji-gate-check.py`
  (21 688 B, sha256 `66c7af71840470e929d5e4b645dd7ff697adf9f1b184ad20e1dccc15898e7ed1`,
  python3 3.14.8, stdlib only; no installs, no host upgrade, no
  service restart, no pacman transaction).
- Frozen contract read first: `.ufo/waves/round-22/attempt2/preregistration.txt`
  (C2 block). No counter, predicate, class set or kill rule was redefined below.
- Lane bounds honoured: no subagent was dispatched (the single labrat allowance
  was not needed — every check was executable in this seat).

## 1. Selftest — 7/7 (executed)

`python3 -B .../souji-gate-check.py --selftest` (fixtures under
`mktemp -d /var/tmp/souji-gate-check-*`, removed in `finally`):

```
PASS fixture-1-no-round-date [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1] expected-fail=check2 got-fail=check2
PASS fixture-2-quote-26-words [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1] expected-fail=check3 got-fail=check3
PASS fixture-3-quote-absent-from-snapshot [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1] expected-fail=check4 got-fail=check4
PASS fixture-4-dangling-source-id [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1] expected-fail=check5 got-fail=check5
PASS fixture-5-no-reject-row [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1] expected-fail=check6 got-fail=check6
PASS fixture-7-good-entry [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0] expected-fail=none got-fail=none
PASS fixture-6-staged-entry-copy [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1] sha256=f13fb769c418d7e4 byte-exact=True got-fail=check1
selftest=7/7
PASS slice-missing-row-not-counted-in-V-or-F [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=0]
control=FALSE-GREEN-REJECTED
selftest_rc=0 wall_ms=28
```

The selftest asserts the **exact set** of failed check ids per fixture, not just
"failed": fixture 1 fails only check2, fixture 2 only check3, …, fixture 6 only
check1. A tool that fails a fixture for the wrong reason is caught.

Notable fixture construction:
- **fixture 2** puts a 26-word quoted span in the Gate *and in the named
  snapshot verbatim*. Only the word cap can reject it; a tool that ignores the
  cap passes the fixture and is caught. (`LONG_QUOTE` = 26 whitespace words.)
- **fixture 6 is a byte-exact copy** of
  `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md`
  (read-only source; sha256 `f13fb769c418d7e4575ddfebaedae2c8199e47afbd08477ded8fd7ee4efa7e48`).
  The tool hashes source and copy in the same run and requires equality
  (`byte-exact=True`) before crediting the fixture. The copy has no `## Gate`
  heading, so check1 rejects it with `ok=0 fail=1 rc=1`. A tool returning ok for
  it is FALSE-GREEN; `control=FALSE-GREEN-REJECTED` is printed only when that
  fixture actually failed on `check1`.
- Fixtures 1–5, 7 are synthetic entries/snapshots authored in the selftest; the
  staged entry is used for fixture 6 and as the real-data control in §3 (N1).

## 2. Exact counts line on the current repo state (executed)

From the lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`:

```
python3 -B .ufo/waves/round-22/attempt2/w1/evidence/impl-gate/souji-gate-check.py \
  --root . --round-date 2026-10-25 \
  --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
            corpus/knowledge/quarantine-origin-record-fields-r24.md \
  --snapshot-dir census/round-22/attempt2/sources \
  --slice census/round-22/attempt2/quarantine-slice \
  --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
```

stdout, exactly one line (verified: `| wc -l` → `1`), stderr empty
(`counts.stderr` = 0 bytes):

```
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
counter_rc=0 wall_ms=32
```

Run time: 32 ms wall (selftest 28 ms), `date +%s%N` around the process.
Python 3.14.8.

The state moved while this seat worked: lane tip advanced from `70af563` (where
this seat first read `git status`) through `3216c19` to `5ff5041` ("seat-driven
corrections (locators, slice verdicts, stale digest, lesson M17-M21)"). After
that commit the four inputs are clean (`git status --porcelain -- corpus/knowledge
census/round-22/attempt2` → empty), so the measured state is now the committed
tip. Every counter invocation (four runs spanning two r24 revisions) printed the
**same** counts line; the last one, on tip `5ff5041d64964d4e6e8374b0eefb8b12010b9997`:

```
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0 wall_ms=33
```

Input hashes for that measurement (`evidence/impl-gate/counts-latest.txt`):

```
80a6a89515f96a5455d1ea38a8e428f455b71b627071d5b9b4932d10b22762de  corpus/knowledge/quarantine-staging-no-copy-r23.md
f47efc7b80003767888a07df8d45ee6bf3e7119182a76f8f66ac6c351202b2f1  corpus/knowledge/quarantine-origin-record-fields-r24.md
12d3c325649ca6026bdb9b98b1edb1ebd2d2dcc61ac519bfa14d7d084c5da7e6  census/round-22/attempt2/quarantine-slice
12cad84e887e6e342c37f6f09001d5f861956791bc2beb7b3f35dd4b22dfca24  census/round-22/attempt2/slice-verdicts.tsv
```

The earlier in-flight measurement (`evidence/impl-gate/inputs.sha256`, r24 at
`8a21704d…` before the locator corrections landed) produced the identical line
with `rc=0 wall_ms=32`.

Slice reading: the slice file carries 8 id lines (`S114 S123 S124 S126 S131
S133 S138 S118`; the last two tokens on the S118 line are an id followed by a
backtick and prose) and the TSV carries 8 rows, one per id, all classes in the
frozen four-set → `slice_verdicts=8 slice_total=8`.
This matches the preregistration's after-state (`entries=2 ok=2
slice_verdicts=8/8 fail=0`, exit 0) **for this repo state**; it is a measurement,
not a claim that the C2 round work is otherwise complete.

## 3. Real-data negative controls (executed)

| # | Input | Observed | Required by frozen text |
|---|---|---|---|
| N1 | the real staged package entry passed as `--entries` (no `## Gate`) | `FAIL check1 …: no-##-Gate-heading`, `entries=1 ok=0 … fail=1`, rc=1 | fixture 6 / FALSE-GREEN kill |
| N2 | real slice + a 7-row copy of the 8-row verdicts TSV | `entries=2 ok=2 slice_verdicts=7 slice_total=8 fail=0`, rc=1 | missing row counted in **neither** V nor F; V<T forces exit 1 |
| N3 | real r24 entry with only `opened:` changed to 2026-10-24 | `FAIL check2 … opened-date-mismatch: found=['2026-10-24'] want=2026-10-25`, `ok=0 fail=1`, rc=1 | per-entry check 2 must fail alone |

Scratch for N1–N3 was `mktemp -d /var/tmp/gate-neg-*`, removed in the same
command (`scratch removed` printed). No lane file was written.

## 4. Frozen predicate → implementation (executed mapping)

Each row below is exercised by the fixture named; none is asserted from source
alone.

| Frozen check | Rule implemented | Isolated by |
|---|---|---|
| 1 exists + `## Gate` heading | file resolved under `--root`; heading matched as a full line `## Gate`, section ends at the next `##` heading | fixture 6 (real bytes), N1 |
| 2 https URL + `opened:` = round date | any `https://` token inside the Gate; an `opened: YYYY-MM-DD` inside the Gate equal to `--round-date` | fixture 1, N3 |
| 3 ≥1 located quote ≤25 words | a quoted span counts only on a line that also names a locator (`§`, section, line, paragraph, DESCRIPTION); words = whitespace tokens | fixture 2 (quote present in snapshot, still rejected) |
| 4 every quoted span verbatim (ws-collapsed) in the named snapshot under `--snapshot-dir` | per-line `snapshot: <path>`; `realpath` containment under `realpath(--snapshot-dir)` (blocks `..` and symlink escape); `squash(quote) in squash(snapshot)`; applied to **every** span, including >25-word ones | fixture 3, N3 (still passes check4) |
| 5 every `source: S<digits>` in frontmatter resolves | frontmatter = text before the first ATX heading; ids from `^source:` lines; registry rows from `^\| S<digits> \|` in `corpus/SOURCES.md` | fixture 4 |
| 6 ≥1 ADMIT and ≥1 REJECT, reason each | ADMIT row's reason = attribution after its last quoted span (locator + snapshot); REJECT row requires an explicit `reason:`/`because`/`justification:` clause with non-empty text | fixture 5 |
| slice: one row `<id>\t<class>\t<evidence>` per id line, class in 4 | ids from `\bS\d{3,}\b` on each non-empty slice line; TSV rows keyed by id; bad id/class/empty evidence/duplicate/short row are structural failures; **missing row contributes to neither V nor F** | selftest `slice-missing-row-not-counted-in-V-or-F`, N2 |

Counts line is the only stdout write in counter mode; every diagnostic goes to
stderr, so the one-line contract holds. Exit is
`ok == entries and V == T and F == 0`; `fail` counts one per (entry, failed
check id) plus one per structural slice failure.

## 5. Interpretations I had to fix (flagged, not hidden)

The frozen text is terse in three places; these are the readings implemented.
None changes any verdict on the current repo state or on the seven fixtures, and
none redefines a counter or class.

1. **ADMIT "reason string".** Real ADMIT rows carry no literal `reason:`; they
   carry `— § <locator> — snapshot: <path>`, which is the row's justification.
   I treat that attribution tail as the reason. Requiring `reason:` on ADMIT
   would fail the two real entries and contradict the frozen after-state, so
   that reading is excluded by the preregistration itself. REJECT does require
   an explicit marker (the real REJECT rows have `— reason: …`).
2. **Check 5 with zero citations.** "Every cited id resolves" is vacuous if
   nothing is cited, which would let a source-less entry pass. I fail
   `check5-no-source-citation-in-frontmatter`. This is a derived strengthening;
   both real entries and every fixture cite sources, so it is inert here.
3. **Check 3 scope.** The frozen text requires *≥1* located short quote, not
   that every quote be located; check 4 independently requires *every* quoted
   span to resolve. I therefore do not fail a Gate merely for an extra
   unlocated quote, but that quote still has to resolve in a named snapshot.
   An unbalanced ASCII `"` on a Gate line is a check3 failure (a malformed
   located-quote record would otherwise be silently skipped — a false-green
   hole).

## 6. Bounded findings for the parent

1. **Committed `tools/souji-gate-check.py` diverges from the frozen slice
   rule.** At lines ~166–169 it appends `verdict-missing:<id>` to `fails`, so a
   missing verdict row increments `fail`. The preregistration says the missing
   row "is counted in neither V nor F". On a partial TSV the committed tool
   would print `fail=1`, my candidate `fail=0` (both exit 1 via V<T). If the
   round's counter line must match the frozen wording byte-for-byte semantics,
   the committed tool's F is wrong. (Source-inferred from its text; not run
   against a partial TSV — the seat does not modify tools/.)
2. **Same tool requires no reason on ADMIT** (checks only `ADMIT:` presence) and
   checks the reason only on REJECT → frozen check 6 is half-enforced there.
3. **Its fixture 6 is synthetic** ("# fixture entry without a gate"), not a
   byte-exact copy of the staged package entry, so its own selftest never
   demonstrates rejection of the staged bytes. My candidate does (fixture 6,
   sha equality asserted).
4. **Its check 3 fails any quoted line lacking a locator**, stricter than the
   frozen "≥1 located quote"; harmless on current data, but it is a predicate
   extension.
5. **Concurrent sibling edits (observation, not a defect).** When this seat
   started, both entries were clean at HEAD `70af563`; they changed under me at
   03:46:44 and 03:47:36 and a sibling then committed the corrections at
   `5ff5041`. The diffs are locator corrections only (`§ OPTIONS --no-copy` →
   `§ DESCRIPTION, option --no-copy`; `paragraph, Trash Info key/value list` →
   `§ 6 Contents of a trash directory, key/value list`; one r23 path reference
   re-pointed to the package file). The counts line is stable across both
   revisions (§2); the input hashes for the committed state are in
   `counts-latest.txt`. If a further edit lands, re-run the counter rather than
   reusing the line.
6. **Slice line form.** The 8th slice line is ` S118` immediately followed by a
   backtick and prose (` S118` then a backtick then "the cited source could not
   be fetched…"), unlike the uniform ` S1NN   ` + backticked-token shape of the
   other seven. An id is still extractable (T=8), so no verdict changes; if the
   round report's frozen awk is supposed to emit one shape, that line is worth a
   look by whoever owns the slice (not this seat's file to change).

## 7. Risks / limits of this candidate

- Locator and snapshot attribution are **line-scoped**. A Gate that wraps a
  quote across physical lines would be reported as a failure rather than parsed
  (real entries and fixtures do not wrap).
- Word counting is whitespace tokens; a hyphenated compound counts as one word.
  Fixture 2 proves the cap is enforced, not that the tokenizer matches any
  external definition.
- `realpath` containment treats a symlinked snapshot directory as its target;
  correct for escape prevention, but a Gate naming a snapshot through a symlink
  outside `--snapshot-dir` will fail.
- The tool reads only: no git write, no index touch, no `.ufo/state`, no
  `MANIFEST.json`, no shokuknow write (the staged entry is opened `rb` only).

## 8. Checks not run (lane rule)

Per the editing-wave rule, no build/lint/formatter gate was run by this seat;
the parent owns post-integration gates. Nothing here is reported as passing
except the executed runs above (selftest §1, counter §2, the three negatives
§3). No tool/package was installed; Python 3.14.8 stdlib only.

## Files written (all under the named evidence path + this report)

- `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/souji-gate-check.py`
- `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/selftest.log`
- `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/counts.txt`
- `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/counts-latest.txt`
  (committed-tip measurement: hashes + counts line + rc + wall)
- `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/counts.stderr` (0 bytes)
- `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/inputs.sha256`
- `.ufo/waves/round-22/attempt2/w1/ImplGateCheck.md` (this report)

No lane file outside these paths was created or modified.
