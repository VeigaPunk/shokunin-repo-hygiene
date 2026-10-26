# deliver-cross-claim — round 30 wave 1 cross-claim map (C1 x C2 x C3 x r29 carry)

Seat SwarmConnector32, read-only connector. Lane HEAD read this run:
`df6afe817d096e4ad71ba2b9cc21a83f126eb658` (pre-seat-data tip); lane base
`9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; preregistration commit
`d4928ec86b667e3d1ed0adb07fb088e500cf1631`. All quotes below are from bytes
opened this run; none contains a pipe character.

## 1. C1 R05/R06 vs C2's gate change — the deepest coupling

Shared bytes: `tools/souji-landing-gate.py`. It is simultaneously (a) C2's
surface under change, (b) C1 row R05's executed command, (c) the C2 REGRESS
artifact, and (d) an LG-PARSE-REG registry-cited script.

- R05 (`SCORECARD.md:158`, stated `18/18`) observed at base
  `SELFTEST pass=65 fail=0` (census/round-30/records/c1-before.txt:6,
  "ROW R05 SCORECARD.md:158 stated=18/18 rc=0 observed=SELFTEST pass=65 fail=0 MISMATCH kind=value").
  The delivered C2 gate keeps the printer at
  `.ufo/waves/round-30/w1/deliver-souji-landing-gate.py:2317`
  ("print(\"SELFTEST\\tpass=%d\\tfail=%d\" % (passed, failed))"), same shape as
  base `tools/souji-landing-gate.py:2269`.
- The C2 counter's REGRESS leg is the ONLY guard that keeps R05/R06 stable
  after the gate change: census/round-30/c2-counter.py docstring,
  "REGRESS `python3 -B tools/souji-landing-gate.py --selftest` and
  `python3 -B tests/fixtures/r16-landing-gate.py`, each run inside the exported
  tree of BASE and of REV". Receipt at delivered rev
  `.ufo/waves/round-30/w1/receipt-SwarmExecutor01-c2-counter.txt:4-5`:
  "REGRESS tools/souji-landing-gate.py base=(0, 'SELFTEST\\tpass=65\\tfail=0')
  rev=(0, 'SELFTEST\\tpass=65\\tfail=0') same" and r16
  "base=(0, 'SUMMARY\\ttotal=15\\tfailed=0') rev=(0, 'SUMMARY\\ttotal=15\\tfailed=0') same".
- Consequence: C1's kill rule ("target after, at the C1 landing commit and
  again at the final lane tip", preregistration.txt:5) is enforceable only if
  C2's REGRESS holds at every later commit. Nothing in the C1 counter re-checks
  REGRESS; the coupling is one-directional and by contract only
  ("C2 is forbidden to change the selftest/r16 literals C1 reads",
  preregistration.txt:7).

## 2. C1 corrections vs the SCORECARD rows the round appends

- The C1 counter parses corrections ONLY from the SCORECARD.md tail and only
  while the base-prefix holds:
  `tools/souji-capability-agreement.py:98` "sc_append = sc_rev.startswith(sc_base)";
  frozen rule preregistration.txt:5 "SCORECARD.md/SHONEN.md at REV must begin
  with their base bytes, else every item counts."
- All nine correction-bearing rows coexist in one tail with the r29 measurement
  table (SCORECARD.md:304-307), the "Round 29 capability rows" (313-314), the
  r30 rows the L1 will append, and the r31 Planned block. Appends are benign to
  the counter (it regex-matches only `^R30-CORRECTION ` lines).
- Second instrument on the same bytes: `tools/souji-record-agreement.py` K1 is
  SCORECARD.md ("K1_RECORDS = (\"SCORECARD.md\",)," :55) and registry K2 pins
  SCORECARD.md:23 (`census/round-29/stale-statements.tsv` row 2,
  "SCORECARD.md 23 2 malformed newline-path records") with the append-only
  check `tools/souji-registry-agreement.py:156` "if not rb.startswith(bb):".
  Both requirements coincide (append-only); no conflict, but a single in-place
  edit (e.g. striking the r30 Planned bullet at SCORECARD.md:318) fails C1,
  registry K2, and the pointer sweep at once.
- Gate sweep check (SCORECARD.md is a sweep source, tools/souji-landing-gate.py
  "sources" set lines 916-928): every path token inside the nine draft
  correction lines (`tests/fixtures/r17-census-hygiene.py`, `tools/souji-census.sh`,
  `tools/souji-rev-pin.py`, `tests/fixtures/r24-coverage-agreement.py`,
  `tools/souji-coverage-agreement.py`, `tests/fixtures/r28-wave-evidence-capture.sh`)
  exists at base — verified by `git cat-file -e 9420341d9a...:<path>` for all
  ten paths this run. Correction lines are sweep-clean.
- Gap (finding F5): rows appended this round are NOT in the frozen
  enumeration (c1-rows.tsv is read as a blob at --list-rev
  `tools/souji-capability-agreement.py:76` "rows_tsv = blob(root, a.list_rev,
  \"census/round-30/c1-rows.tsv\")"), so their literals are never re-derived —
  exactly the defect R18 exhibits: "ROW R18 SCORECARD.md:314 stated=cases=15
  pass=15 rc=0 observed=Usage: bash tools/souji-wave-evidence-capture.sh
  <lane-abs> <round-N> [--verify [--rev <full40>]] MISMATCH kind=value"
  (c1-before.txt:22). R18 was born stale at append time (r29 rows, SCORECARD.md:313-314).

## 3. C3 fixture vs C1 enumeration — confirmed it cannot enter

- c1-rows.tsv is frozen at list-rev d4928ec; a working-tree edit cannot move
  it. None of the 18 row commands names `tests/fixtures/r30-jj-keep-expiry.sh`.
- C1's correction `cmd=` override cannot smuggle it in either: the counter
  requires the corrected argv's first path to equal the row's first path
  (tools/souji-capability-agreement.py:163-166 area, `first_path` check).
- The C3 fixture itself is scratch-disciplined:
  `.ufo/waves/round-30/w1/deliver-r30-jj-keep-expiry.sh:31-35` refuses TMPDIR
  inside the lane or the fleet ("die \"TMPDIR=$TMPDIR resolves inside the souji
  lane"), and every jj call names `-R` on the scratch repo (:58, :73-74).
- Reverse direction: C3's entry IS a gate sweep source (corpus/knowledge/*.md
  are swept, tools/souji-landing-gate.py:924-928 "path.startswith(\"corpus/knowledge/\")").
  Any `census/`-, `tools/`-, `tests/`-, `corpus/`-rooted token in
  `corpus/knowledge/jj-keep-ref-expiry.md` that does not resolve at the final
  tip prints LG-DANGLING-PTR and breaks C2's dangling=0. The frozen L4/L6 legs
  already force its `snapshot:`/`source:` citations to resolve inside the lane;
  the C2 surface adds the repo-relative-path constraint on the same prose.

## 4. r29 carry block vs the counters

- C2 is the only counter that reads round-29.md: the gate sweeps
  "corpus/lessons/round-%d.md" % round_no (:925) and its carry check reads the
  `## Seat-reported failures` section. Receipt proof in
  `.ufo/waves/round-30/w1/deliver-r29-carry-block.md`: before the append
  "LG-SEAT-UNCARRIED ... SUMMARY findings=12 ... carry_heading=0", after
  "SUMMARY findings=5 ... carry_heading=1 checked_reports=86", and the
  negative control (one bullet deleted) re-fires exactly one finding.
- Therefore the carry block is LOAD-BEARING for C2's frozen SUMMARY: at the
  delivered gate rev the C2 counter already prints
  ".ufo/waves/round-30/w1/receipt-SwarmExecutor01-c2-counter.txt:1
  \"GATE rc=1 reports=86 cne=0 dangling=0 other=7\"" — the 7 are the
  LG-SEAT-UNCARRIED the carry block clears. Gate change alone cannot reach the
  target shape; the lesson append is a C2 dependency.
- C1 and C3 do not read round-29.md (verified: not in C1's blob set; c3-counter
  reads corpus/knowledge + corpus/SOURCES.md only).
- Ordering hazard: the carry block's section must stay contiguous. The D4
  correction appends its own `## Gate` H2 to the same file
  (.ufo/waves/round-30/w1/deliver-r29-gate-correction.md). Whichever appends
  last must not place an H2 between the carry heading and its bullets; the
  gate's `failures_section_lines` stops at the next heading
  (deliver-r29-carry-block.md "Section body: failures_section_lines (line 383)
  takes every line after that heading up to the next heading").

## 5. D4 r29 Gate correction vs souji-registry-agreement.py K2 — no disturbance

- K2's stale statements live in LOG.md:1758, SCORECARD.md:23,
  corpus/lessons/round-28.md:22,40 (`census/round-29/stale-statements.tsv`,
  4 rows read verbatim this run). round-29.md is not a K2 record.
- The D4 block's marker lines start `R30-CORRECTION `, which cannot satisfy or
  spoof K2's `x.startswith('R29-CORRECTION ')` filter
  (tools/souji-registry-agreement.py:166), and its append keeps every pinned
  file base-prefixed, so K2's three checks (missing / rewritten-not-appended /
  statement-moved-or-edited) stay inert.
- R14/R17 (record/registry fixtures) build synthetic repos under /var/tmp and
  honour --root (`tests/fixtures/r23-record-agreement.py:11` "It builds a
  synthetic lane repo under /var/tmp (hard-coded; never /tmp)";
  `tests/fixtures/r29-registry-agreement.py:141` runs the tool with
  `--root repo ... --list-rev list_rev` on the synthetic repo), so the real
  round-29.md append cannot move R14 or R17 either.
- Sweep check for the D4 table: its root-prefixed tokens
  (`corpus/knowledge/dupe-finders-detect-then-act.md:34`,
  `census/round-29/waves/w1/deliver-f3-scope-table.tsv`,
  `corpus/lessons/round-28.md:47-52`) all resolve at base; bare basenames
  (`PROVINCE.md:69-70`, `duplicate-verdict-identity.md:35`) are invisible to
  POINTER_PATH_RE, which requires a `(?:census|tests|tools|corpus|\.ufo/waves|
  \.ufo/quarantine)/` prefix (tools/souji-landing-gate.py:141-145).

## 6. Recurring mistake classes in corpus/lessons/round-2[5-9].md ## Mistakes

| class | where | r30 recurrence risk |
|---|---|---|
| number-drift / stale literal | r25 R25-M1 (prereg literal copied, not re-derived); r28 stale-premise row; r29 row 1 ("the committed-bytes count is 152 absent records", corpus/lessons/round-29.md ## Mistakes) | HIGH for new SCORECARD rows (R18 was born stale); LOW for the 13 corrections — seats ran the counter (c1-corrections-acceptance.txt, "SUMMARY k1=0 k2=0 mismatches=0 rows=4 pointers=10 partial=1") |
| vacuous / gameable counter | r29 row 4 ("a K2 that accepts an empty marker (Critic51)") | LOW-MED: r30 counters carry content-binding (rc+observed re-run, FALSE-GREEN-REJECTED, legs L1-L9) |
| scope / hygiene breach | r29 rows 5-6 (clone `origin` push landed on lane master; parked-seat edit) | MED: mitigated by the drop-origin and scratch TMPDIR directives; C3's jj fixture is the live jj mutation surface and it self-refuses outside scratch |
| attribution | r25 R25-M1 duplicate dispatch; r29 row 3 ("self-ruled the r28 C2 target missed at 139") | MED: the other=7 SUMMARY ambiguity (below) is this round's instance |
| reference-drift | r29 row 2 (S215 used-by one-directional) | LOW: C3 L6 forces reciprocity for new rows |

## 7. Contract tension (stated, not smoothed)

preregistration.txt:7 says both "other= is reported, not targeted" and
"Kill rule: any other SUMMARY at the C2 landing commit or the final tip is a
miss", while the disclosed probe says discovery surfaces 7 LG-SEAT-UNCARRIED.
The c2-counter exit code ignores `other` ("Exit 0 iff reports>0, cne=0,
dangling=0 and the three legs are ok"), but the kill rule reads the whole
SUMMARY line. Landing the carry block before the C2 landing commit is the only
path that satisfies both sentences literally (other returns to 0).

## 8. Proposed move (one, bounded)

Land order + append discipline, no counter change:

1. Land the r29 carry block AND the D4 Gate correction in a commit at or
   before the C2 landing commit, appends ordered so the
   `## Seat-reported failures` section stays contiguous (carry block wholly
   before or wholly after the D4 `## Gate` section, never interleaved).
   Effect: C2's SUMMARY becomes byte-stable at `other=0`, resolving the
   tension in §7 by construction rather than by interpretation.
2. Author every SCORECARD.md row the L1 appends for r30 (measurement table,
   capability rows, Planned) from a fresh scratch-clone run of the row's
   command at the landing rev — paste the observed last summary line, never a
   hand-copied literal — or reference the census receipt instead of an inline
   count. Effect: calibration (axis 7) improves by removing the R18
   born-stale pattern from the round's own append step; round 31's frozen
   enumeration then re-derives literals that were true at birth.
3. Record both decisions in corpus/lessons/round-30.md `## Mistakes` as the
   mined mistake ("appended rows carry literals never re-run at append time;
   R18 instance") — this is the frontier step's planned mistake slot, so it
   costs no extra surface.

Axis check: operability ↑ (C2 SUMMARY stable), calibration ↑ (new literals
true at birth), coverage untouched (C3 bytes unaffected), no counter/target/
predicate/case-set change, no harm to any axis.

Risks: (a) ordering slip — if C2 lands first, the landing SUMMARY prints
other=7 and the kill-rule tension surfaces; mitigation is the order itself,
verifiable in the commit sequence. (b) Fresh-run authoring could observe
environment-dependent output; mitigation — the C1 counter's normalize() already
pins hex/tmp/duration tokens, and the acceptance receipt shows the pattern
works. (c) Both appends to round-29.md must keep base prefix; both deliveries
already are append-only.

Verification for the L1 after integration:
- `python3 -B census/round-30/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <final40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --fleet-root /home/vgpnk/Projects/shokunin` -> `SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same`.
- `python3 -B tools/souji-capability-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <final40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` -> `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10`.
- `git diff --stat 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b <final40> -- SCORECARD.md SHONEN.md corpus/lessons/round-28.md` shows additions only.
