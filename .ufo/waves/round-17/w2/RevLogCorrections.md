STATUS: DONE — draft holds in substance; two citation defects (891-893 not 892-894; sentence spans 902-903) and one D7-class phrasing found; 30th marker identified; "29" upgraded to a measured replay; final text below.

# RevLogCorrections — round 17 wave 2 (FALSIFY pass on ScribeLogCorrections.md)

Scope: the two append-only LOG correction drafts in
`.ufo/waves/round-17/w1/ScribeLogCorrections.md`, attacked against
`LOG.md:850-906` (raw bytes) and closure D3
(`corpus/lessons/round-16-verifier-spotcheck.md:136`). Read-only; no gate,
census, fixture or verifier executed; nothing outside this report written.

## Findings

### F1 [defect, must fix before landing] — cross-reference off by one line

- Draft (F2 and LOG-entry 2): "the wave-2 corrections at `LOG.md:892-894`
  already state the right list".
- Actual bytes: the corrected-list statement spans **891-893**:
  - `LOG.md:891` "fixes from wave-1 reviews, not all 65; pre-harm fails 02, 03, 08, 11, 14,"
  - `LOG.md:892` "17, 18, 19 — refusal/safety plus 03 (degrade) and 18 (preserve), not "only"
  - `LOG.md:893` "refusal/safety"; the fixture is synthetic and same-round, not held-out, and"
  - `:894` is a different clause ("the r13/r14 zero-finding replays …").
- Smallest fix: cite `LOG.md:891-893`.

### F2 [defect, minor] — sentence span for the "28" quote

- Draft entry 1 cites `LOG.md:902` for "The landing gate flagged 28 uncarried
  wave-2 STATUS lines; they are carried in `corpus/lessons/round-16.md`."
  The sentence spans **902-903** (`:902` ends "…flagged 28 uncarried wave-2";
  `:903` is "STATUS lines; they are carried in …"). The figure "28" itself is
  on :902, and closure D3 (:136) also cites :902, so :902 alone is defensible;
  the full-sentence quote should cite :902-903.

### F3 [defect, D7-class] — "at `6ff91f5`" repeats routed imprecision

- Draft entry 1: "(`checked_markers` 30, `findings` 0, at `6ff91f5`)".
  D7 (spotcheck:137-ish, routed item 7) flagged exactly this shape: the file
  `census/round-16/gate-landing.json` lands at `c46eabf` and **records a run
  whose `resolved_rev` is `6ff91f534eece9adde5f667cb7dad400c145351b`**. The
  JSON confirms: `"resolved_rev": "6ff91f534ee…"`, `checked_markers: 30`,
  `findings: 0`. Smallest fix: write "`resolved_rev` `6ff91f5`" (and do not
  say "the gate at `6ff91f5`").

### F4 [draft's open point — resolved] — the 30th marker is `ConnLogConvention.md:385`

The draft left "one marker was not uncarried at `79bbe7a`" unidentified.
Identified, with evidence:

- Gate semantics (`tools/souji-landing-gate.py:88-101,285-422`): a marker is a
  non-fence, non-table line matching `^[#*\s]*STATUS[*]*\s*[:—]` whose first
  value word ∈ {incomplete, fail, failed, fails, failing, failure, blocked,
  broken, partial, harmed, red, unrun, error, regression, known}; carried =
  its normalized line is a substring of a line under `## Seat-reported
  failures` containing `open` or `resolved@<7+hex>`.
- At `79bbe7a`, `.ufo/waves/round-16/` holds 63 w1 + 78 w2 = 141 `.md`
  (= `checked_reports` 141), so markers come only from w1+w2.
- w1 STATUS-channel lines at `79bbe7a`: 57 (case-insensitive, tab-inclusive
  scan). Exactly two have a vocabulary first word:
  `ConnLogConvention.md:221` and `:385`, both
  "## STATUS: INCOMPLETE — file has an unresolved syntax error".
- Fence map of `ConnLogConvention.md` at `79bbe7a`: ```` ```markdown ```` at
  :204, close at :375, so **:221 is inside the fence (not a marker)** and
  **:385 is outside** (next fence opens at :429). So w1 markers = exactly 1.
- Arithmetic closes: 30 markers = 29 w2 (all flagged) + 1 w1 (:385, already
  carried by the lesson's wave-1 bullet — `corpus/lessons/round-16.md:43` at
  `79bbe7a`, quoting the same line with token `resolved@0a70bef`).

### F5 [improvement] — "29" has a measured replay in the lane; the draft under-cites

`census/round-17/gate-replays-ddb7347.json`, replay `r16-precarry`:
`exit: 1`, `finding_count: 29`, `process_rc: 1`, `resolved_rev:
"79bbe7a62199260694943ec7186fef6ebff9d41a"`, SUMMARY
`findings=29 … checked_markers=30 carry_heading=1 checked_reports=141`. The
29 finding paths are **file-for-file identical** to the 29 carry bullets at
`corpus/lessons/round-16.md:58-86` (verified by set comparison; 86−58+1 = 29,
one bullet per line, `:58` = ConnQuality2 … `:86` = SentinelGateSafety).
The same record's `r16-landing` gives findings 0, markers 30 at `6ff91f5`,
matching `gate-landing.json`. The draft's "re-derived (static, closure)"
should cite this executed measurement.

### F6 [gap in closure D3, flagged for L1] — "the lesson, the report … give 29" is half false

- `corpus/lessons/round-16.md:21` (lesson prose) repeats the wrong figure:
  "At this landing it flagged **28** uncarried wave-2 STATUS lines before
  they were carried below." Only the lesson's carry list (:58-86) gives 29.
  The final text grounds the count on the carry list + replay + landing
  record, and discloses the lesson-prose residue.
- The "report" leg is **unverifiable in this repo**: `.ufo/reports/round-16/`
  does not exist in the worktree, `git log --all -- <path>` is empty, and the
  closure's step-1 commit `85f2aa9b9f275109f69c7485c79046cb166efe6d` is not
  an object (`git cat-file -e` → rc 1). The corrected LOG text therefore does
  not cite the report. (Consistent with the scribe's "not found" note; likely
  a jj history rewrite — outside this lane.)

### F7 [confirmed — draft's core numbers hold]

- `LOG.md:858-859` raw: "…r14-harm fails every HARM_CASES id; pre-harm fails
  only / refusal/safety cases; …" — the draft's quote and span are exact.
- Pre-harm `a31642d` r15-config: `failed: 8`, `total: 20`; failing ids
  exactly **R15CFG-02, 03, 08, 11, 14, 17, 18, 19**
  (`census/round-16/c1-matrix-final.json`, `.arms["pre-harm"]["r15-config"].cases`).
- R15CFG-03 = degrade class ("r-inc-cycle: finding config-unsupported missing
  from stderr; … r-inc-fifo: exit=124 want 0"); R15CFG-18 = benign
  preservation ("a-benign/m-safe-config/z-benign: worktrees=0 want 1;
  verdict_flags=error want clean"). Neither is refusal/safety.
- `corpus/lessons/round-16.md:20` carries the correct list ("…fails 02, 03,
  08, 11, 14, 17, 18, 19 — refusal/safety cases plus 03 (degrade) and 18
  (preserve…"). Lesson line 20 confirmed by numbered grep.
- `79bbe7a62199260694943ec7186fef6ebff9d41a` = "round-16: final wave-2 seat
  reports", type commit. Spotcheck :66 table row "`79bbe7a` → 29 uncarried"
  and D3 item 3 at :136 confirmed. Spotcheck :44 does say "Pre-harm fails 03
  only" (contradicted by its own :43 matrix row and by the JSON) — the draft
  rightly never cites it.
- Append-only form and house style match (`## 2026-10-20 — round 16 …`,
  "stands as written", "withdrawn"). `LOG.md` is exactly 906 lines; both
  entries append at end-of-file. No pre-existing "29 uncarried" line in LOG.md.

## Final text (replaces the draft's two entries; append after LOG.md:906)

```
## 2026-10-20 — round 16 correction: the uncarried wave-2 count is 29, not 28

Correction to "The landing gate flagged 28 uncarried wave-2 STATUS lines; they
are carried in `corpus/lessons/round-16.md`" (LOG.md:902-903 above; the figure
itself is the "28" on :902; the wave-2 entry stands as written). Found by the
round-16 non-author closure (`corpus/lessons/round-16-verifier-spotcheck.md:66`,
routed defect D3, item 3) and re-measured by the round-17 landing-gate replay
at rev `79bbe7a` (`round-16: final wave-2 seat reports`): 30 gate markers, 29
uncarried (`census/round-17/gate-replays-ddb7347.json`, replay `r16-precarry`,
exit 1, `checked_markers` 30). The thirtieth marker — `.ufo/waves/round-16/w1/
ConnLogConvention.md:385`, the only wave-1 failure-vocabulary STATUS line
outside a fence — was already carried in the lesson's wave-1 list. The carry
list `corpus/lessons/round-16.md:58-86` holds 29 wave-2 bullets, one per
uncarried line. The marker count matches `census/round-16/gate-landing.json`
(`checked_markers` 30, `findings` 0, `resolved_rev` `6ff91f5`; the file lands
at `c46eabf`). The figure 28 is withdrawn. The lesson's own prose
(`corpus/lessons/round-16.md:21`) repeats the 28 figure; its carry list is the
correct 29.

## 2026-10-20 — round 16 correction: pre-harm fails R15CFG-03 and R15CFG-18, not only refusal/safety cases

Correction to "pre-harm fails only refusal/safety cases" (LOG.md:858-859, the
round-16 C1 entry above; the wave-2 corrections at LOG.md:891-893 already
state the right list). Found by the round-16 non-author closure
(`corpus/lessons/round-16-verifier-spotcheck.md:136`, routed defect D3, item
3). The pre-harm arm `a31642d` fails eight r15-config cases: 02, 03, 08, 11,
14, 17, 18, 19 (`census/round-16/c1-matrix-final.json`,
`.arms["pre-harm"]["r15-config"]`: failed 8 of 20). R15CFG-03 is the
per-repository degrade class (expected `config-unsupported` findings missing
from stderr; `r-inc-fifo` hangs, exit=124 want 0) and R15CFG-18 is
benign-config preservation (`a-benign`, `m-safe-config`, `z-benign`:
`verdict_flags=error want clean`); neither is refusal/safety. This matches
`corpus/lessons/round-16.md:20`. The closure's own C1 table row "Pre-harm
fails 03 only" (`round-16-verifier-spotcheck.md:44`) is a slip contradicted by
its matrix row above and by the matrix record; the matrix is the record.
```

Differences from the draft's versions: :891-893 (not :892-894); :902-903
sentence span; `resolved_rev` phrasing (D7-proof); measured `r16-precarry`
replay cited; 30th marker named; lesson-prose "28" residue disclosed; the
spotcheck:44 slip called out so a reader who checks the cited closure is not
misled one row below the cited row.

## Commands run (all read-only)

| # | command / read | result |
|---|---|---|
| 1 | `read LOG.md:raw:850-906`; grep -n `uncarried\|pre-harm fails` LOG.md | 858/859 quote exact; "28" sentence spans 902-903; corrected list spans 891-893; no other "uncarried" hit |
| 2 | grep -n lesson round-16.md (`Round 16 wave 2`, bullets, `refusal/safety cases plus`) | line 20 correct list; heading :56; bullets :58-86 (29) |
| 3 | read `census/round-16/c1-matrix-final.json?q=…` (keys + failing + cases 03/18) | failed 8/20; ids 02,03,08,11,14,17,18,19; 03/18 class details as quoted |
| 4 | read `census/round-16/gate-landing.json` | markers 30, findings 0, resolved_rev 6ff91f534ee… |
| 5 | read `census/round-17/gate-replays-ddb7347.json` (full) | r16-precarry exit 1 / 29 findings / markers 30 @79bbe7a; r16-landing 0 / 30 @6ff91f5; finding paths == carry bullets |
| 6 | `git log -1 --format='%H %s' 79bbe7a`; `cat-file -t 79bbe7a` | `79bbe7a62199… round-16: final wave-2 seat reports`; commit |
| 7 | gate source `tools/souji-landing-gate.py:88-101,285-422` | marker/carry definitions quoted above |
| 8 | `git show 79bbe7a:corpus/lessons/round-16.md` (failures section) | wave-1 list present (bullet :43 quotes :385's line, `resolved@0a70bef`); no wave-2 list |
| 9 | `git grep -nIE -i` STATUS-prefix scans at 79bbe7a over w1 (colon + em-dash, tab-inclusive) | 57 lines; vocabulary first words only at ConnLogConvention :221 (fenced) and :385 (unfenced); `DraftReportSkeleton.md:3` "Status: skeleton only" not vocabulary |
| 10 | `git show 79bbe7a:.ufo/waves/round-16/w1/ConnLogConvention.md` fence map | ```` ```markdown ```` :204→:375 fences :221; :385 unfenced (next fence :429) |
| 11 | `git ls-tree -r --name-only 79bbe7a .ufo/waves/round-16/` per-subdir count | 63 w1 + 78 w2 = 141 = checked_reports |
| 12 | `git cat-file -e 85f2aa9b9f27…`; `git log --all -- .ufo/reports/round-16/souji.md` | rc 1 (object absent); no ref tracks the report path |
| 13 | grep -n spotcheck (`Pre-harm fails 03 only`, `D3, append-only`, `29 uncarried`) | :44 slip; :66 table row; :136 D3 |
| 14 | `wc -l LOG.md` | 906 lines — append point is EOF |

## Residual risk / verification gaps

- The `r16-precarry` replay ran the gate as landed at `ddb7347` (sha
  `c7e8eea5…`), not the `6ff91f5`-era gate; marker semantics could differ
  between versions. Mitigation: both the committed `gate-landing.json`
  (measured then) and the `r16-landing` replay report `checked_markers` 30,
  and the `expected.gate_sha256_match: false` divergence is already disclosed
  in the replay record (D6's business, not this entry's).
- I did not execute the gate (not ALLOWED-EXEC); the 30/1-marker derivation is
  static from pinned regexes plus the two committed measurement records.
- The `85f2aa9` report-commit disappearance suggests post-closure history
  rewriting; whether the round-16 report text said "29" is unverifiable in
  this repo. The final text does not depend on it.
- Tool installs/updates: none.
