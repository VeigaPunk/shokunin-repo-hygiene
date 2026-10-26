# deliver-r29-carry-block — append-only carry block for corpus/lessons/round-29.md

Seat SwarmScribe15, round 30 attempt 1, wave 1, lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Read-only seat: the lane's `corpus/lessons/round-29.md` was NOT modified. The block below is the
paste-ready text for the L1 to append; the proof ran in a throwaway clone.

Lane state read this run: HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658`; lane base for round 30
`9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; `git diff --stat 9420341d… HEAD -- <the 7 reports>
corpus/lessons/round-29.md` printed nothing, so the quoted STATUS paragraphs are byte-identical at
base and at tip. `git diff --stat 9420341d… -- tools/souji-landing-gate.py` also printed nothing:
the gate used for the proof is the round-30 base gate.

## Gate carry contract (tools/souji-landing-gate.py at lane tip)

- Heading looked for: `FAILURES_HEADING_RE` (line 108) matches a `##`-level heading whose text is
  `Seat-reported failures`, case-insensitive.
- Section body: `failures_section_lines` (line 383) takes every line after that heading up to the next
  heading; a second such heading later in the file is also read, so an append is legal and nothing
  above it has to move.
- A carried entry must also carry a token: `CARRY_TOKEN_RE` (line 110) requires the entry to contain
  the word `open` or a `resolved@` plus 7+ hex characters.
- The unit carried is the marker's whole paragraph: `status_paragraph` (line 421) is the STATUS
  physical line plus its wrapped continuation lines, ending at the first fence, table row, quote,
  HTML block, heading, bullet, thematic break or new STATUS line (`_continues_paragraph`, line 407).
- Matching (`carries`, line 446): either the normalized whole paragraph occurs, or a normalized
  prefix that stops at one of the source's physical line ends occurs and the very next characters are
  an ellipsis; a mid-line ellipsis never carries. The whole-paragraph branch is used here, so no cut
  mark is needed and the gate's hint `paragraph continues at line N (mark the cut with ...)` is moot.
- Normalization (`norm_line`, line 330): NFC, drop asterisks and backticks, collapse whitespace.
- Strict wrap matching applies from round 18 (`WRAP_STRICT_FROM_ROUND`, line 122), so round 29 is
  strict: a first-physical-line-only quote without an ellipsis does NOT carry.
- `LG-OPEN-ADMITTED` fires only when the lesson also declares `admitted: true`
  (`ADMITTED_TRUE_RE`, line 111). Sweep this run:
  `git grep -c -iE 'admitted[[:space:]]*:[[:space:]]*true' -- corpus/lessons/round-29.md` -> 0, so
  marking the entries `open` adds no finding.

## The block (append verbatim at end of corpus/lessons/round-29.md)

```markdown

## Seat-reported failures

Appended in round 30: the round-29 landing gate could not read committed reports — it only read the
uncommitted wave directory — so these seven seat-reported failure lines went uncarried at the round-29
landing. Each entry quotes that report's STATUS paragraph verbatim (bytes as committed at lane tip
`df6afe817d096e4ad71ba2b9cc21a83f126eb658`) and marks it open: no `resolved@` receipt for any of them
exists in `corpus/lessons/round-29.md` or `census/round-29/records/controls.tsv`.

- `census/round-29/waves/w1/SwarmCritic49.md` line 5 — open: STATUS: PARTIAL — the claim is real but its instrumentation is not: a restatement pair reaches every C3 counter with zero new ground (measured), the delivered pair's genuine increment is about one entry rather than two, and one admit's Broder ground contradicts the round's own reject reason. A stricter-only correction that keeps every frozen target is measured below.
- `census/round-29/waves/w1/SwarmCritic51.md` line 7 — open: STATUS: FAIL — K2 as frozen is satisfiable without any true correction. All nine junk states I constructed score `k2=0` under the frozen tool, including an empty-content marker (`R29-CORRECTION LOG.md:1758` and nothing else), a marker that *denies* the defect, and a state that keeps the pinned phrase verbatim while inverting the sentence around it. The lane's own frozen control already records this: `C1-junk1(markers only)` → `k2=0` with the marker text `junk marker`. A stricter-only second condition is specified below and tested: it rejects all nine, accepts a fact-carrying append, and leaves the base control at 10.
- `census/round-29/waves/w1/SwarmCritic53.md` line 5 — open: STATUS: PARTIAL — the plan satisfies 13 of 23 clauses outright, 6 with a named condition, one is excluded for this lane (wave-4 quarantine-first lists four other lanes), and 3 are missed (per-entry QUALITY bar never applied; the report carries no place for the two id lists, the collision count and the renumber map and mis-maps S217-S219; the S118 quarantine verdict says "not adopted" while S217 adopts the same document). No delivery changes a counter, predicate, kill rule or target, so the frozen C1/C2/C3 claims survive; every correction below is documentation, one row cell, one verdict line or one Gate clause.
- `census/round-29/waves/w1/SwarmExecutor17.md` line 3 — open: STATUS: PARTIAL — the deliverable is complete and every command shape in it was executed and verified at base `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, but I breached the read-only bound once (Finding 1: a scratch-clone `push` landed on the lane's `refs/heads/master`); I restored the ref byte-exactly and re-verified `ahead=0 behind=0`, no ref on the stray object, and reported it here rather than hiding it.
- `census/round-29/waves/w1/SwarmReviewer40.md` line 3 — open: STATUS: PARTIAL — my own verifier over an independently exported byte set reproduces the frozen counter exactly per round (r26 1382/152/14, r27 124/0/0, r28 75/0/0) and the frozen counter never traces back on hostile names (space, tab, newline, backslash, CR, non-UTF-8 file and directory names, symlink/empty/dir manifests, bad revs). Partial because the frozen instrument has three reach defects found by testing, and the naive r26 recapture required by C2 is unsafe today: the receipt cannot detect a path-permuted copy, its GNU-only unescape false-fails the `\r` escape that this host's own `sha256sum` emits, and the capture tool reports `--verify` green while 12 r26 wave source files differ from the receipt (one of them currently dirty).
- `census/round-29/waves/w1/SwarmReviewer42.md` line 5 — open: STATUS: PARTIAL — the Broder source is sound and the row is admissible at tier B under corrected wording; the staged S118 as written is not admissible (wrong venue, source cell names only a non-dereferenceable DOI, `used-by` names a path absent at HEAD), and the landed S217 carries two residual wording defects.
- `census/round-29/waves/w1/SwarmReviewer43.md` line 5 — open: STATUS: PARTIAL — the base literals for all three claims re-derive exactly and the axis assignment is clean (`claims=3 flags=0`), but 11 findings are actionable before any scoring: C3's gate literal is not base-derivable and its instrument reads the working tree, C2's target is reachable by deleting evidence and its fixture growth is not a literal, C1's K2 clears without content and its K1 used-by arm is substring-only, the control receipt binds neither sha256 nor reachable junk revs, both SUMMARY shapes are misquoted, the "causally separable" sentence is contradicted by C3's own target, one universal survives the R4 scan, the round-start census count is unbound, and C1 binds no SHONEN claim.
```

Each bullet is one physical line, so `carry_entries` (line 431) yields exactly one entry per report;
the verbatim paragraph is on that same line because a continuation line beginning with `STATUS:`
would be refused as a new paragraph by `_continues_paragraph`.

## Proof

Scratch `C=$(mktemp -d /fast/scratch/hyaku/souji-r30/SwarmScribe15/r.XXXXXX)/c`,
`git clone -q --no-local <lane> "$C"` then `git -C "$C" remote remove origin`
(`git -C "$C" remote -v` printed 0 lines; `rev-parse --show-toplevel` printed the scratch root).
Throwaway identity set with `git -C "$C" config` only. TMPDIR exported into the scratch dir.

Commit 1 `f9dd108bb25576430c646652ee4ed80d37022d51` — capture only:
`cp -r "$C/census/round-29/waves" "$C/.ufo/waves/round-29"` then `git -C "$C" add -f .ufo/waves/round-29`
(86 `.md` reports present; the capture keeps its `w1/` level, and the gate's prefix match is
recursive, so all 86 are read).

```
$ python3 -B tools/souji-landing-gate.py --root "$C" --rev f9dd108bb25576430c646652ee4ed80d37022d51 --round 29
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at f9dd108bb255
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at f9dd108bb255
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at f9dd108bb255
LG-DANGLING-PTR	census/round-	corpus/QUALITY.md:150 cites path absent at f9dd108bb255
LG-DANGLING-PTR	corpus/lessons/round-	corpus/QUALITY.md:150 cites path absent at f9dd108bb255
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmCritic49.md	line 5: STATUS: PARTIAL — the claim is real but its instrumentation is not: a restatement pair reaches every; paragraph continues at line 6 (mark the cut with ...)
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmCritic51.md	line 7: STATUS: FAIL — K2 as frozen is satisfiable without any true correction. All nine junk states I constructed score k2=0 under the frozen tool, including an empty-content marker (R29-CORRECTION LOG.md:1758 and nothing else)
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmCritic53.md	line 5: STATUS: PARTIAL — the plan satisfies 13 of 23 clauses outright, 6 with a named condition, one is; paragraph continues at line 6 (mark the cut with ...)
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmExecutor17.md	line 3: STATUS: PARTIAL — the deliverable is complete and every command shape in it was executed and; paragraph continues at line 4 (mark the cut with ...)
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmReviewer40.md	line 3: STATUS: PARTIAL — my own verifier over an independently exported byte set reproduces the frozen; paragraph continues at line 4 (mark the cut with ...)
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmReviewer42.md	line 5: STATUS: PARTIAL — the Broder source is sound and the row is admissible at tier B under corrected wording; the staged S118 as written is not admissible (wrong venue, source cell names only a non-dereferenceable DOI, used-
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmReviewer43.md	line 5: STATUS: PARTIAL — the base literals for all three claims re-derive exactly and the axis; paragraph continues at line 6 (mark the cut with ...)
SUMMARY	findings=12	checked_reg=58	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=7	status_lines=69	carry_heading=0	checked_reports=86
before_rc=1
```

7 LG-SEAT-UNCARRIED — the reported count reproduced exactly, with `carry_heading=0` and
`checked_reports=86`, so the failure channel was exercised and the carry axis was empty.

Commit 2 `170908a094a279a3228051019bc4b60a4e8c2f1f` — block appended, nothing above edited
(prefix diff of the first 88 lines against the pre-append file printed no difference):

```
$ python3 -B tools/souji-landing-gate.py --root "$C" --rev 170908a094a279a3228051019bc4b60a4e8c2f1f --round 29
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at 170908a094a2
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at 170908a094a2
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at 170908a094a2
LG-DANGLING-PTR	census/round-	corpus/QUALITY.md:150 cites path absent at 170908a094a2
LG-DANGLING-PTR	corpus/lessons/round-	corpus/QUALITY.md:150 cites path absent at 170908a094a2
SUMMARY	findings=5	checked_reg=58	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=7	status_lines=69	carry_heading=1	checked_reports=86
after_rc=1
```

Zero LG-SEAT-UNCARRIED, `carry_heading=1`, `checked_markers=7`, `checked_reports=86`. The 5 remaining
LG-DANGLING-PTR findings are the same 5 present before the block (baseline had 12 = 5 + 7) and live in
`corpus/README.md`, `corpus/QUALITY.md` and `corpus/knowledge/jj-colocation-receipts.md`; the block
adds none, because every path it names exists at the rev.

Negative control, commit `5cf6612a3dbf39a1656a006c7fad4afbb03f5d14` — only the SwarmCritic51 bullet
deleted, then reset to `170908a`:

```
$ python3 -B tools/souji-landing-gate.py --root "$C" --rev 5cf6612a3dbf39a1656a006c7fad4afbb03f5d14 --round 29
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at 5cf6612a3dbf
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at 5cf6612a3dbf
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at 5cf6612a3dbf
LG-DANGLING-PTR	census/round-	corpus/QUALITY.md:150 cites path absent at 5cf6612a3dbf
LG-DANGLING-PTR	corpus/lessons/round-	corpus/QUALITY.md:150 cites path absent at 5cf6612a3dbf
LG-SEAT-UNCARRIED	.ufo/waves/round-29/w1/SwarmCritic51.md	line 7: STATUS: FAIL — K2 as frozen is satisfiable without any true correction. All nine junk states I constructed score k2=0 under the frozen tool, including an empty-content marker (R29-CORRECTION LOG.md:1758 and nothing else)
SUMMARY	findings=6	checked_reg=58	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=7	status_lines=69	carry_heading=1	checked_reports=86
neg_rc=1
```

Exactly one finding, for the deleted entry, so the carry is load-bearing and not satisfied by the
section heading or the prose.

## Limits

- Not run in the lane: the lane lesson is unmodified by this seat; the L1 appends. The proof clone is
  removed (`rm -rf` of the scratch dir) after this file was written.
- The block marks all 7 entries `open`. That is the token the gate requires and matches what was
  verified: `grep -c 'resolved@' corpus/lessons/round-29.md` -> 0 and no `resolved@` marker naming any
  of the 7 seats in `census/round-29/records/`, so no entry is claimed resolved.
- `checked_changed=0` on every run (no `--base` supplied); the registry/pin branches are reported but
  are not what this proof asserts.
- No tool was installed or upgraded for this item.
