# CriticGateVacuity — round 16 w1 (critic, calibration)

Seat: SoujiR16.CriticGateVacuity (leaf critic). I own only this report.
Target: the pinned C2 design of `tools/souji-landing-gate.py`, taken from the LandingGate and LandingGateFixture items in `.ufo/waves/round-16/w1-spec.json`. **The gate file did not exist at either of my two reads**, so this review covers the pinned contract only, not an implementation. I measured by applying the pinned regexes, verbatim, to committed historical bytes. I did not execute the gate.

Axes: calibration (primary; the C2 claim). Operability is unaffected: the gate is additive.

## Verdict

The design is **training-set-fit**. The required historical red on `b410186` replays the very three defects the gate was written from. Measured over held-out history, its third check (LG-SEAT-UNCARRIED) has **0 true positives out of 12 marker hits** outside the r15 training seat, and **misses the real held-out instance** of the same defect class (r14). Its frozen-pin check can be satisfied by re-hashing alone, without re-measuring. Its carry check can be satisfied by pasting lines. "Red on b410186, green at round end" therefore does not show calibration improvement. C2 as worded ("mechanically detects the three r15 landing defects") is true by construction. The judge should treat that wording as no evidence of improvement unless the held-out cases below (A1–A12) are in the fixture and pass.

Fixable defects: F1–F6 below. One tradeoff must be disclosed rather than claimed: a substring carry check enforces *transcription*, not *disclosure* (F3).

## Findings

### F1. Marker regex: measured precision and recall outside r15

Pinned regex: `(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b`. I applied it to every committed `*.md` under `.ufo/waves/round-{13,14,15}/w1/`. Those files are byte-identical at HEAD and b410186 (`git diff --stat b410186 -- …` empty). Each matched line was checked for a stripped-substring carry in `corpus/lessons/round-N.md`.

| round | marker hits | true seat-known-failure | carried in lesson | hits |
|---|---|---|---|---|
| 13 (held-out) | 2 | 0 | 0 | `EvidenceConnection.md:165` (a shell snippet that echoes the phrase), `SourceTimeout.md:78` (a table row describing timeout exit 125) |
| 14 (held-out) | 2 | 0 | 0 | `CachePrecedent.md:159` (a mutation recipe), `CachePrecedent.md:220` (an exit-code taxonomy) |
| 15 (training) | 3 | 3 | 0 | `ConfigRepair.md:7,9,11` |
| 16 so far (10 reports present at read time) | 8 | 0 | n/a | `DraftLessonMistakes.md:14,58`, `DraftR15Correction.md:11,23,36,53,78,150`. All quote r15 history or list commands. |

- **Self-check:** under the pinned regex, this report itself adds 3 marker hits. None of them is a seat-known failure, so the round-16 false-positive load is now at least 11/11.

- **Precision outside the training seat: 0/12.** Prediction [INFERENCE: pinned regex applied to identical bytes; gate not run]: `--rev a31642d --round 13` and `--rev cc21683 --round 14` each emit 2 LG-SEAT-UNCARRIED false positives and exit 1. The cc21683 red is dangerous: it is the right verdict for the wrong reason, and could be cited as if the gate detected the r14 harm.
- **Recall on the held-out instance of the same class: 0/1.** Round 14's seat disclosed the defect that became the r14 rejected-harmed verdict. `.ufo/waves/round-14/w1/CensusBoundary.md:241-244` reads: "Unsupported local configs (LFS `filter.*`, includes, hooks path, alternate refs command, promisor/partial clone, worktreeConfig) refuse the whole census with exit 2. This is fail-closed operability debt, not normal-config support." `corpus/lessons/round-14-verifier-spotcheck.md:7` calls it "disclosed value-blind Git-configuration refusals", and a grep of `corpus/lessons/round-14.md` for `operability debt|whole census|CensusBoundary|value-blind` finds nothing. The regex does not match the seat line (probe below), so the gate is silent on the one held-out case that matters.
- **Round-end greening is driven by false positives.** All 8 round-16 hits must be pasted into `corpus/lessons/round-16.md`, or the gate stays red at cbf688+ for reasons unrelated to any landing defect. This report adds more hits, because it quotes the vocabulary. The gate therefore trains L1 to paste bulk quotations, and that is exactly F3.

### F2. Rewording dodges (each line run through the pinned regex; pure string evaluation)

Matched: `## STATUS: INCOMPLETE — …`, `Status: incomplete`, `STATUS: BLOCKED on operator`, `bash: line 3: syntax error: unexpected end of file`, and the false-positive table row from r13.

Missed, though each states a known failure:

- `**STATUS:** INCOMPLETE — file does not run` (markdown bold breaks `STATUS:\s*`)
- `STATUS — INCOMPLETE`
- `STATUS: fails selftest 11/13` and `STATUS: failing` (`FAIL(?:ED)?\b` rejects `fails`/`failing`)
- `STATUS: PARTIAL — 3 cases red`
- `STATUS: known failure: legacy selftest 37/38`
- `STATUS: UNRUN`, `STATUS: harmed`, `STATUS: red`, `STATUS: DO NOT SHIP`
- `The file in tree doesn't parse.` and `… fails to parse.`
- `SyntaxError: invalid syntax` and `IndentationError: …`. This is Python's own wording for exactly what the gate's `.py` check detects.
- `parse error near …`
- the r14 CensusBoundary sentence above
- `F-A BLOCKING: fail-open …` (`BoundaryReviewRoot.md:140`, r14)
- `R14C2-09 FAIL`

The shared Contract tells seats to put "any known failure on a line starting `STATUS:`" in free vocabulary. So the gate's vocabulary is narrower than the protocol's own disclosure channel. Smallest correction: invert the rule.
- Every line matching `^\W*STATUS\W*:` (bold and heading prefixes tolerated) counts as a marker unless its value is in a pinned *benign* allowlist (`ok`, `complete`, `none`, `no known failure`, `design-only`, `advisory`).
- The existing parse-failure phrases stay as a secondary net, extended with `SyntaxError`, `IndentationError`, `parse error`, `does(?:n't| not) (?:parse|run)` and `fails? to parse`.
- Lines inside fenced code blocks and markdown table cells are excluded from the secondary net only. That removes all 4 held-out false positives (3 code/recipe lines, 1 table row) [INFERENCE from the line shapes above].

### F3. LG-SEAT-UNCARRIED is satisfiable by pasting, without disclosure

The check is "stripped line is a substring of `corpus/lessons/round-N.md`". Each of these passes it while disclosing nothing [INFERENCE from the pinned rule; not exercised]:
- (a) an appendix `## Seat lines` that dumps the lines into a fenced block;
- (b) the lines inside an HTML comment `<!-- … -->`, which is invisible when rendered;
- (c) the lines carried next to a lesson decision that still says `admitted: true` / `ok`;
- (d) a short marker such as `STATUS: FAIL` from seat A, satisfied by an unrelated seat B line that contains the same substring.

It also checks only the lesson. R3 requires "the L1 report **and** lesson verbatim", and the r15 closure's D1 grep covered LOG, SKILL, SCORECARD and census/round-15 as well. The fleet report (`.ufo/reports/round-N/souji.md`) is outside `--root LANE`, so R3 can be at most half covered.

Correction:
- Strip HTML comments before matching.
- Require carried lines to sit under one pinned heading (`## Seat-reported failures`), each followed on the same line by a disposition token (`open` or `resolved@<rev>`). Verify that `<rev>` is an ancestor of REV.
- Emit a new id, LG-OPEN-ADMITTED, when any disposition is `open` and the lesson/disposition says admitted.
- Match per (seat file, line) pair, not by global substring.

Tradeoff that the judge must not credit as solved: no mechanical check proves disclosure *quality*. The claim must read "enforces marker carry", not "enforces disclosure".

### F4. Vacuous pass when the wave directory is not committed

The pinned selftest case "no wave dir passes" makes the cheapest dodge official: do not commit `.ufo/waves/round-N/` at REV (or commit it after the evaluated REV). That yields 0 markers and a green gate. SUMMARY reports `checked_markers=C` but not how many reports were scanned. Correction:
- Add `checked_reports=R` to SUMMARY.
- Exit 2 (could-not-evaluate) when `--round N` is given and `.ufo/waves/round-N/` is absent at REV, or holds 0 `*.md`.
- Keep "no wave dir passes" only behind an explicit `--allow-no-waves` flag.

History has a wave dir in every round: r13–r15 are all committed (`git ls-tree` above).

### F5. LG-FROZEN-PIN checks the current hash, not the measured provenance

The R4 defect was "pin matches **no committed revision**". The pinned check only compares `expected.json.files` against REV bytes. Two counterexamples:

- **Re-hash-only repair passes.** `tests/fixtures/r15-preservation-frozen/README.md:12-18` instructs the integrator to *edit* `measured_commit`, the tool/fixture sha256 fields and `record_sha256` to the new digests. Doing exactly that without re-running the fixture turns LG-FROZEN-PIN green. Meanwhile `record.json` still holds the old run's `stdout`, whose line 82 reports `TOOL … sha256=b5187351…`. The gate never compares the pin with the record's own measurement.
- **`measured_commit` is never resolved.** `record.json:7` says `measured_commit: fc3a8d4…`, but per the closure (spot-check line 56) fc3a8d4's census is `fcff8b05…`, not the measured `b5187351…`. A pin can match REV while the record describes bytes from no commit, and the gate stays green.
- **Shadowing.** "Resolve relative to frozen dir if that file exists there, else snapshot root" lets a copy at `tests/fixtures/r15-preservation-frozen/tools/souji-census.sh` satisfy the pin while the shipped `tools/souji-census.sh` differs.

Correction:
- For every `files` entry, also require `sha256(git show <record.measured_commit>:<path>) == pin`, with measured_commit an ancestor of REV.
- Require that the record's own run sha fields (`runs.*.tool.sha256`, the `TOOL … sha256=` line in `namespace_controls.stdout`) equal the pin.
- Emit an ambiguity finding when both resolution bases exist and differ.

Scope: two other frozen dirs already match the glob (`r13-cert-frozen`, `r14-cache-frozen`). Both have `files` pinned to files inside their own frozen dir. Those pins are self-referential and can only fail by in-place edit, so they add count (`checked_pins`) but not signal. Report self-contained pins separately so the pin count is not inflated.

### F6. The parse checks are syntax-only; held-out landing defects pass them

Covered by design: non-parsing cited script, missing cited path, non-parsing changed script with `--base`. Missed classes:

1. **The r14 harm class.** A parsing script with a behavioral regression (value-blind refusal → exit 2). The closure records that cc21683's census passes `bash -n` and shellcheck (spot-check line 41). All five checks are silent. This is the routed R2 class, and the gate cannot claim it.
2. **Python compile-stage errors that `ast.parse` accepts**: `return`/`yield` outside a function, module-level `nonlocal`, and top-level `await` [INFERENCE from CPython's parser/compiler split; not executed]. Correction: use `compile(src, path, "exec", dont_inherit=True)`. It still never executes repository code, and it is what `py_compile` (already allowed by the Contract) does.
3. **`bash -n` exits 0 on an unterminated here-document**, with only a warning [INFERENCE from bash semantics; not executed]. An in-flight edit truncated mid-heredoc (the r15 failure mode, "edits were in flight", `ConfigRepair.md:10`) parses clean, with the rest of the file swallowed as heredoc body. Correction: any `bash -n` stderr counts as a finding, and run `shellcheck -S error` when it is present.
4. **Path coverage.** The pinned path regex allows no `/` after the prefix, so a `tools/lib/x.sh` path is invisible, as are extensionless executables and `.bash` files. Today SKILL.md's 18 cited paths are all captured, with 0 near-misses (measured). Also, the C1 counting command `census/round-16/run-matrix.py` is not SKILL-cited, so it is checked only when L1 passes `--base`. L1 must run with `--base b410186`, or C1's own runner goes unchecked.
5. **Failures reported outside wave `*.md`** (agent messages, JSON results) are invisible.

## Falsifiable acceptance cases (held-out; none copied from the r15 trio)

Exit and ids follow the pinned contract. Cases marked (+fix) need the correction named in that row.

| id | input | expected |
|---|---|---|
| A1 | replay `--rev a31642d --round 13` | gate must NOT emit LG-SEAT-UNCARRIED for `EvidenceConnection.md:165` / `SourceTimeout.md:78` (code/table false positives). As pinned it does [INFERENCE] → red until F2 fix. |
| A2 | replay `--rev cc21683 --round 14` | must NOT be cited as detecting r14 harm. Assert the findings list contains no LG-SEAT-UNCARRIED for `CachePrecedent.md:159,220` (+fix F2). Document it as a known miss for `CensusBoundary.md:241-244`, or (+fix F2 STATUS inversion plus a `debt`/`refuse the whole` phrase) assert it is flagged. |
| A3 | synthetic seat line `**STATUS:** INCOMPLETE — does not run`, absent from lesson | exit 1, LG-SEAT-UNCARRIED (+fix F2) |
| A4 | synthetic seat line `STATUS: fails selftest 11/13` | exit 1, LG-SEAT-UNCARRIED (+fix F2) |
| A5 | synthetic seat line `SyntaxError: invalid syntax` | exit 1 (+fix F2) |
| A6 | marker carried only inside `<!-- … -->` in the lesson | exit 1 (+fix F3) |
| A7 | marker carried with disposition `open` while the lesson says `admitted: true` | exit 1, LG-OPEN-ADMITTED (+fix F3) |
| A8 | `--round N` where `.ufo/waves/round-N/` is absent at REV | exit 2 (+fix F4) |
| A9 | frozen `expected.json` re-hashed to REV bytes, `record.json` stdout still `sha256=<old>` | exit 1, LG-FROZEN-PIN (+fix F5) |
| A10 | pin matches REV but `git show <measured_commit>:path` differs | exit 1, LG-FROZEN-PIN (+fix F5) |
| A11 | cited `.py` whose only defect is module-level `return 0` | exit 1, LG-PARSE-REG (+fix F6.2) |
| A12 | cited `.sh` truncated inside `cat <<EOF` with no terminator | exit 1, LG-PARSE-REG (+fix F6.3) |
| A13 | mutation control: the fixture's own no-tool stub must fail every case above | fixture exit 1 (already pinned, case 3) |

Minimum bar for crediting C2: A1/A2 measured on real history, and at least one case each from F2, F3, F4 and F5 green. Without those, the result is training-set replay only, and the most it supports is unprovable-but-better.

## Smallest safe corrections (ordered)

1. F4: exit 2 on a missing wave dir, and add `checked_reports`. One condition, and it closes the vacuous-pass route.
2. F5: verify `measured_commit` bytes, the record's self-reported sha and resolution ambiguity.
3. F2: STATUS-line inversion with a benign allowlist, plus code-fence/table exclusion for the phrase net.
4. F3: strip HTML comments, pinned section, disposition token, per-pair matching.
5. F6.2/6.3: `compile()` instead of `ast.parse`, and treat `bash -n` stderr as a finding.
6. Claim wording: C2 must say "marker carry", list F6.1 (behavioral regression) as an explicit non-goal, and run with `--base b410186`.

STATUS: gate file absent at review time — findings are against the pinned contract only; the held-out replays A1/A2 are predictions from the regex applied to committed bytes, not gate runs.

Tool installs/updates: none.

## Commands

Shell commands (verbatim):
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b410186 -- .ufo/waves/round-13 .ufo/waves/round-14 .ufo/waves/round-15 corpus/lessons/round-13.md corpus/lessons/round-14.md corpus/lessons/round-15.md tests/fixtures/r15-preservation-frozen`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/expected.json`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b410186 -- .ufo/waves/round-13 .ufo/waves/round-14 .ufo/waves/round-15 corpus/lessons/round-13.md corpus/lessons/round-14.md corpus/lessons/round-15.md`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %an %s' b410186..cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- SKILL.md tests/fixtures/r15-preservation-frozen`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools tests/fixtures`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only a31642d -- corpus/lessons/round-13.md .ufo/waves/round-13/w1/EvidenceConnection.md .ufo/waves/round-13/w1/SourceTimeout.md`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cc21683 -- corpus/lessons/round-14.md .ufo/waves/round-14/w1/CachePrecedent.md .ufo/waves/round-14/w1/CensusBoundary.md`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat a31642d b410186 -- .ufo/waves/round-13/w1/EvidenceConnection.md .ufo/waves/round-13/w1/SourceTimeout.md corpus/lessons/round-13.md`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat cc21683 b410186 -- .ufo/waves/round-14/w1/CachePrecedent.md .ufo/waves/round-14/w1/CensusBoundary.md corpus/lessons/round-14.md`

Non-shell (read-only, exact named files):
- read: `skill://godspeed`; `corpus/lessons/round-15-verifier-spotcheck.md`; `.ufo/waves/round-15/w1/ConfigRepair.md:1-20`; `.ufo/waves/round-14/w1/CensusBoundary.md:165-185,236-256`; `.ufo/waves/round-14/w1/BoundaryReviewRoot.md:138-150,170-180`; the three `tests/fixtures/*-frozen/expected.json`; `tests/fixtures/r15-preservation-frozen/{record.json,README.md}`.
- Attempted reads of `tools/souji-landing-gate.py`, twice: not found.
- Directory reads: `.ufo/waves/round-16/` and `.ufo/waves/round-16/w1/` (non-recursive).
- grep: `.ufo/waves/round-16/w1-spec.json`; `corpus/lessons/round-14.md` + `round-14-verifier-spotcheck.md`; `tools/souji-census.sh` (`shopt|heredoc`).
- Python eval (in-process, no subprocess): `json.load` of `w1-spec.json`. `open()` of the exact r13/r14/r15 w1 report names from the ls-tree listing above, the 10 named round-16 w1 reports and the r13/r14/r15 lessons, with the pinned regexes applied in memory. The pinned regexes were also applied to the literal probe strings listed in F2. No repository code was executed and no /var/tmp scratch was created.
