STATUS: DONE — the carry check's first-physical-line match is confirmed blind to all 7 wrapped round-16 quotes; an exact wrap-aware rule is specified with 3 selftest cases; measured over the five pinned replays it changes only r16-landing (0 → 7) unless gated at `--round ≥ 18`; no edits made.

Seat: `SoujiR18.ScoutCarryWrap` (scout, leaf). The gate/census/fixtures/selftest were not executed. The only code run was a throwaway in-memory re-implementation reading `git show`/`ls-tree` output of named revisions (disclosure at the end).

# Axes

1. **Carry exactness** — does a carried quote reproduce the source STATUS paragraph, or mark where it stops?
2. **False-fail avoidance** — can a correct carry be rejected because either side wraps at a physical line?
3. **Replay stability** — does the rule preserve the pinned r17 verdict multiset (`census/round-17/gate-replays-expected.json`) unless a regeneration is deliberate?

# What the code does now (observed)

- `check_carry` (`tools/souji-landing-gate.py:368-430`) takes each failure marker from `seat_failure_lines` (`:325-336`), which yields only the **first physical line** of a wrapped STATUS paragraph — continuation lines do not begin with `STATUS:` and are never yielded.
- The needle is that one line: `needle = norm_line(raw)` (`:402`); the match is `needle in nl` against one normalized lesson physical line plus `CARRY_TOKEN_RE` (`:406`, regex `:102`).
- `norm_line` (`:291-298`) is NFC, drop `*`/backticks, collapse whitespace, strip. Nothing joins a report paragraph or a lesson entry.
- Consequence A (false pass): a lesson that quotes the first physical line and stops mid-phrase passes, because the needle is exactly that first line.
- Consequence B (false fail): if the lesson bullet itself wraps (quote or `— open` on the next physical line), no single lesson line contains the needle, so a correct carry is reported uncarried.
- `corpus/lessons/round-17.md:72` (D5) already records this: "The carry gate still matches only the first physical line (open)."

At `6ff91f5` there are exactly **7** failure markers whose STATUS paragraph wraps, and every corresponding round-16 quote stops at the first physical-line end with no `…`:

| lesson line | source | source first line ends | lesson quote ends |
|---|---|---|---|
| `corpus/lessons/round-16.md:73` | `…/w2/ReopenS048.md:102` | `stretched over` | same |
| `:74` | `…/w2/RerunGateFixture.md:12` | `null-stub` | same |
| `:78` | `…/w2/RerunSeatAudit.md:157` | `and the` | same |
| `:79` | `…/w2/RevCensusStatusFinal.md:359` | `(bound filters never execute;` | same |
| `:82` | `…/w2/RevengeSeatViolations.md:260` | `are not violations` | same |
| `:83` | `…/w2/ScoutLsFilesPathspec.md:179` | `for both consumers` | same |
| `:84` | `…/w2/ScoutOptionalPrefix.md:238` | `parses literally` | same |

D5 names 5; `RevD5Carry.md` disclosed the other 2 (`:82`, `:83`) as clause-boundary truncations. Both are still silent cuts — the paragraph continues — so a mechanical rule counts 7. The committed replay records 0 findings for that revision (`gate-replays-expected.json`, `r16-landing`: `exit 0`, `findings []`), i.e. the gate was green over all 7.

# The rule (exact, minimal)

**Definitions (pinned).**
A *marker paragraph* is the marker physical line plus every immediately following line for which `_continues_paragraph` is true. Normalization is the existing `norm_line` over the block joined with single spaces.

```python
WRAP_STRICT_FROM_ROUND = 18
ELLIPSIS_RE = re.compile(r'\s*["”]?\s*(?:…|\.\.\.)')
LIST_ITEM_RE = re.compile(r"^([-*+]|\d+\.)\s+")
THEMATIC_RE = re.compile(r"^([-*_])(?:\s*\1){2,}$")

def _continues_paragraph(line):
    """A wrapped STATUS paragraph continues through prose only."""
    s = line.strip()
    return bool(s) and not (
        s.startswith(("```", "|", ">", "<"))   # fence / table / quote / html block
        or HEADING_RE.match(s)                 # new section
        or LIST_ITEM_RE.match(s)               # new bullet
        or THEMATIC_RE.match(s)                # thematic break
        or status_value(line) is not None      # a new STATUS opens
    )

def status_paragraph(lines, idx):
    block = [lines[idx]]
    j = idx + 1
    while j < len(lines) and _continues_paragraph(lines[j]):
        block.append(lines[j])
        j += 1
    return block

def carry_entries(carry_lines):
    """Join a carry bullet's own wrapped continuation lines into one entry."""
    ents = []
    for line in carry_lines:
        if ents and _continues_paragraph(line):
            ents[-1] += " " + line
        else:
            ents.append(line)
    return [norm_line(e) for e in ents]

def carries(block, entry):
    full = norm_line(" ".join(block))
    if full and full in entry:                 # (a) complete paragraph
        return True
    for k in range(1, len(block)):             # (b) cut at a source line end
        prefix = norm_line(" ".join(block[:k]))
        for m in re.finditer(re.escape(prefix), entry):
            if ELLIPSIS_RE.match(entry, m.end()):
                return True
    return False
```

**Match semantics.** A marker is carried by a lesson entry iff `CARRY_TOKEN_RE.search(entry)` and either
(a) the normalized **whole paragraph** occurs in the entry, or
(b) the normalized text of its first `k` physical lines (`1 ≤ k < len(block)`) occurs in the entry and the very next non-space characters are `…` or `...` (an optional closing `"`/`”` may sit between).

No other multi-line match carries. A cut at a source physical-line boundary with no ellipsis yields `LG-SEAT-UNCARRIED`; the detail gains `; paragraph continues at line <N+1> (mark the cut with …)`. `LG-OPEN-ADMITTED` keeps using the matched entry.

**Why the cut point is the source's physical-line end, not the lesson's.** The lesson's line end is authored, so comparing only up to it cannot distinguish a complete quote from a truncated one. The source's wrap is the only auditable evidence that text follows the quoted span; requiring the ellipsis exactly there is what closes the hole. Accepting an ellipsis after *any* shorter prefix would be vacuous (`STATUS: PARTIAL …` would "carry" anything).

**Why `carry_entries` is part of the rule.** It is symmetric with the report-side join and closes the false-fail direction (consequence B). It is also provably inert on history: with the old first-line test, per-line and joined-entry matching give identical verdicts at every replay (measured below), because every historical carry bullet is one physical line.

# Replay impact (measured)

Re-implementation of the documented functions over `git ls-tree`/`git show` at each revision (findings counted with the FULL `check_carry`, i.e. including the carry-token requirement):

| replay | rev | old (per physical line) | old + entry join | strict wrap + entry join |
|---|---|---|---|---|
| r13-admitted | `a31642d` | 0 | 0 | 0 |
| r14-landing | `cc21683` | 0 | 0 | 0 |
| r15-landing | `b410186` | 1 | 1 | 1 |
| r16-landing | `6ff91f5` | 0 | 0 | **7** |
| r16-precarry | `79bbe7a` | 29 | 29 | 29 |
| r17 tip | `95519a7` | 4 | 4 | 4 |
| r17 landing | `4f48343` | 0 | 0 | 0 |

The 7 strict-only findings are exactly the table above. The rule is a strict strengthening: every match it accepts also satisfied the old first-line test (complete paragraphs contain their first line; marked cuts contain it too), so it can only add findings.

**Scope decision.** Unconditional application makes `census/round-17/gate-replays-expected.json` (`r16-landing`: exit 0, no findings) and the r17 lesson's D6 statement ("all `match: true`") false, because `gate-replays.py` compares the exact `(id, path)` multiset (`multiset()`/`compare()`). Recommended: gate the strict branch at `round_no >= WRAP_STRICT_FROM_ROUND` (18), mirroring the round-18 `LG-DANGLING-PTR` ≥18 gate — all five pinned replays then stay byte-identical, and round 17 has 0 wrap cuts under either rule (measured), so no currently known defect is hidden. The alternative (apply unconditionally and regenerate both replay files with the 7 disclosed findings) is defensible but is a calibration-record decision for L1, not a code decision.

# 3 test cases

The selftest harness hardcodes the round: `res = evaluate(repo, rev, 16, base=base)` (`tools/souji-landing-gate.py:888`). Add `round_no=16` to `check()` and pass it through; the cases below use round 18, consistent with the scoping above.

Shared world:

```python
f = _frozen_world(_base_files())
f[".ufo/waves/round-18/w1/SeatWrap.md"] = (
    "# SeatWrap\n\n"
    "STATUS: PARTIAL — guarded repos measured and the\n"
    "remaining arm never runs under a bound.\n"
)
```
Line 3 is the marker; line 4 is its continuation; the paragraph normalizes to `STATUS: PARTIAL — guarded repos measured and the remaining arm never runs under a bound.`

**TC1 `wrap-unmarked` (must fail).**

```python
f["corpus/lessons/round-18.md"] = (
    "# Round 18\n\n## Seat-reported failures\n\n"
    "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
    "\"STATUS: PARTIAL — guarded repos measured and the\" — open\n"
)
repo, g, (rev,) = build("wrap-unmarked", f)
check("wrap-unmarked", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev,
      expect_n=1, round_no=18,
      expect_counts={"checked_markers": 1, "checked_reports": 1,
                     "status_lines": 1, "carry_heading": 1})
```
Fails on the pre-fix gate (it passes with 0 findings); passes only when the unmarked physical-line cut is rejected.

**TC2 `wrap-marked` (must pass).** Same report; the quote ends `…` before the closing quote:

```python
f["corpus/lessons/round-18.md"] = (
    "# Round 18\n\n## Seat-reported failures\n\n"
    "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
    "\"STATUS: PARTIAL — guarded repos measured and the …\" — open\n"
)
check("wrap-marked", repo, 0, rev=rev, expect_n=0, round_no=18,
      expect_counts={"checked_markers": 1, "checked_reports": 1,
                     "status_lines": 1, "carry_heading": 1})
```
Fails if the rule wrongly demands the whole paragraph even when the cut is marked.

**TC3 `wrap-complete` (must pass).** The whole paragraph, quoted on one lesson line:

```python
f["corpus/lessons/round-18.md"] = (
    "# Round 18\n\n## Seat-reported failures\n\n"
    "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
    "\"STATUS: PARTIAL — guarded repos measured and the remaining arm "
    "never runs under a bound.\" — open\n"
)
check("wrap-complete", repo, 0, rev=rev, expect_n=0, round_no=18,
      expect_counts={"checked_markers": 1, "checked_reports": 1,
                     "status_lines": 1, "carry_heading": 1})
```
Fails if an ellipsis is wrongly required for a complete quote.

**Optional 4th (Part B control).** Write TC3's bullet across two physical lines — break after `and the` and put `never runs … — open` on an unindented continuation line. Expected 0; it fails if `carry_entries` is not implemented (the old per-line matcher reports `LG-SEAT-UNCARRIED`), which makes the false-fail direction executable.

# Deliberately excluded

- Mid-line `…` (e.g. `"STATUS: PARTIAL — guarded …"`): not a verifiable cut point; accepting it would make the check vacuous.
- Quoting from the paragraph's second line onward: not a carry; the format starts at the STATUS line.
- Single-physical-line paragraphs: unchanged (complete test degenerates to the old needle), which is why r13/r14/r15/r16-precarry/r17 verdicts do not move.
- Curly single quotes as closing delimiters: `ELLIPSIS_RE` allows `"`/`”` only; the corpus uses straight quotes.
- `LG-OPEN-ADMITTED`'s `\bopen\b` test still reads the whole entry, so entry joining widens the text it sees by one continuation line. No measured verdict changes; a continuation that says "open" inside quoted text could trip it. Pre-existing weakness, disclosed, not fixed here.

# Adjacent observation (for C2's counting claim)

At `b576341` there is no `.ufo/waves/round-18/` report and no `corpus/lessons/round-18.md` (`git ls-tree -r b576341 -- .ufo/waves/round-18/ corpus/lessons/round-18.md` prints nothing). `check_carry` raises `EvalError("no .md reports under .ufo/waves/round-18/ at <rev>")` → exit 2, so a literal `--rev b576341 --round 18` "before" run cannot be 0 findings; it is could-not-evaluate. The C2 before/after count needs either the round tip for both sides or an explicitly seeded base.

# Verdict and smallest fix

- **Premise holds.** The gate is blind to all 7 wrapped round-16 quotes; they pass on the first physical line (`:402`, `:406`), and the landing replay is 0 findings.
- **Rule.** Add `WRAP_STRICT_FROM_ROUND`, `_continues_paragraph`, `status_paragraph`, `carry_entries`, `carries`; in `check_carry` precompute `entries`, branch on `round_no >= WRAP_STRICT_FROM_ROUND`, and append the continuation hint to `LG-SEAT-UNCARRIED` details. Add the three cases and the `round_no` parameter to `check()` (`:882-888`).
- **Replay.** Gate at ≥18; otherwise regenerate `gate-replays-expected.json`/`gate-replays-4f48343.json` with the 7 disclosed findings.

# Commands run (excerpted output)

```
grep -n '^def ' tools/souji-landing-gate.py
→ 291 norm_line, 325 seat_failure_lines, 344 failures_section_lines, 368 check_carry
grep -n 'needle = norm_line|if needle and needle in nl|evaluate(repo, rev, 16' …
→ 402 needle = norm_line(raw); 406 if needle and needle in nl and CARRY_TOKEN_RE.search(nl);
  888 res = evaluate(repo, rev, 16, base=base)
grep -n 'ReopenS048|RerunGateFixture|RerunSeatAudit|RevCensusStatusFinal|RevengeSeatViolations|ScoutLsFilesPathspec|ScoutOptionalPrefix' corpus/lessons/round-16.md
→ 73, 74, 78, 79, 82, 83, 84 (all seven carries)
git show 6ff91f5:<report> | sed -n '<line>p'
→ each source's first physical line ends exactly where its lesson quote ends (table above)
python3 (in-memory re-implementation, see disclosure): replay table above; 7 multi-line STATUS
  paragraphs at 6ff91f5, all 7 unmarked; 0 at r13/r14/r17; 29 at r16-precarry; 1 at r15
git ls-tree -r --name-only b576341 -- .ufo/waves/round-18/ corpus/lessons/round-18.md
→ (empty)
```

# Probe disclosure

Two `python3 - <<PY` snippets read only `git -C . show`/`ls-tree` output for named revisions and re-implemented the documented gate functions in memory; they write nothing, signal nothing, use no network, and did not run `tools/souji-landing-gate.py`, the census, or any fixture. The gate's selftest was not run: the case expectations above are derived from its harness (`:868-920`) and the counters defined in `check_carry`/`status_line_count`, not observed. Tool installs/updates: none.
