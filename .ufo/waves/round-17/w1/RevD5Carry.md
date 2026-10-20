STATUS: DONE — D5 verified: all four routed items hold, but the wrap-truncation item undercounts its class (2 named, 5 in the same channel); nine corrected carry lines drafted; the shipped gate still accepts every wrap-truncated quote (0 findings at `6ff91f5`).

Seat: `SoujiR17-3.RevD5Carry` (reviewer, leaf). Read-only; no lane tool, gate, fixture, census or selftest executed. The r16 lesson is historical and was not edited; every "corrected line" below is drafted for the round-17 lesson's corrections section.

# Axes

1. Carry exactness — does each carried line reproduce its source STATUS (all physical lines, no unmarked cut)?
2. Carry completeness — are all non-vocabulary defect lines accounted for, and does the gate's channel reach them?
3. Disposition honesty — does each carried line cite a revision or a verified `open`, and does the cited revision exist?

# Verdicts against the routed D5 items

| routed item | verdict | evidence |
|---|---|---|
| `round-16.md:54` `resolved:` without `@<hex>` | **holds** | the only bare `resolved:` in the lesson (`grep -n 'resolved:'` → line 54; `grep -c 'resolved@'` → 26) |
| `ReopenS048.md:102` quote stops at a wrap, no ellipsis | **holds** | source is `:102-103`; lesson `:73` reproduces only the first physical line, dropping "shellcheck output; anchor unpinned) while rejected / 365d / used-by — hold." |
| `ScoutOptionalPrefix.md:238` quote stops at a wrap, no ellipsis | **holds** | source is `:238-240`; lesson `:84` drops "(`setup.c:597` `xstrdup`); … can abort the whole run on a benign config and, for relative values, resolve one level away from git's effective worktree." |
| round-15 carry lines `:91` and `:93` joined / paraphrased | **holds, both** | `round-16.md:91` joins `ConfigRepair.md:9-13` across `…`, dropping the structural cause and the operator-halt context; `round-16.md:93` paraphrases `ConfigFixture.md:54-59` and names 4 of its 6 conflicts |
| `RevGateSpec.md:226` uncarried non-vocabulary defect line | **holds** | first word `review`, absent from `FAILURE_STATUS_WORDS` (`tools/souji-landing-gate.py:72-78`); the r16 lesson carries no such line |
| **class extension** | **partial — D5 undercounts** | the same wrap cut appears in 3 more wave-2 carries: `RerunGateFixture.md:12`, `RerunSeatAudit.md:157`, `RevCensusStatusFinal.md:359` (lesson `:74,:78,:79`) |

Note on the referent of "round-15 lines :91 and :93": `corpus/lessons/round-15.md:91` is blank and `:93` is the operator-stop prose ("file an honest report because the operator was waiting to reboot"), which the lesson never quotes. The only two Round-15 carry lines are `round-16.md:91` and `:93`, so D5 is read that way and verified there.

# Findings

## F1 — HIGH — the wrap cut is a class of five, and the gate cannot see any of them

The shipped carry check makes the needle the whole normalized **first physical line** of a marker and requires that needle in a single lesson line:

- `tools/souji-landing-gate.py:334` `needle = norm_line(raw)`
- `:338` `if needle and needle in nl and CARRY_TOKEN_RE.search(nl):`
- vocabulary `:72-78` (all five quotes start `STATUS: PARTIAL`, so all are markers)
- `norm_line` `:239-246` (NFC, drop `*`/backticks, collapse whitespace, strip)

A lesson that copies the first physical line and stops passes. Five wave-2 carries do exactly that and are incomplete (source paragraph continues, no `…`):

| lesson line | source | first line ends | what is dropped |
|---|---|---|---|
| `round-16.md:73` | `ReopenS048.md:102-103` | `…stretched over` | `shellcheck output; anchor unpinned) while rejected / 365d / used-by — hold.` |
| `round-16.md:84` | `ScoutOptionalPrefix.md:238-240` | `…parses literally` | ``(`setup.c:597` `xstrdup`); `souji-census.sh:660` can abort the whole run on a benign config and, for relative values, resolve one level away from git's effective worktree.`` |
| `round-16.md:74` | `RerunGateFixture.md:12-16` | `…null-stub` | `run exit 1 with 14/15 FAIL), but the fixture's own vacuity case (F1) is tautological — it prints PASS in that very null-stub run — and its contract prose (F2) still advertises free-text phrase markers the gate dropped. The headline claim holds; the case that claims to prove it, and the prose beside it, do not.` |
| `round-16.md:78` | `RerunSeatAudit.md:157-162` | `…and the` | `single major holds as an attempted (failed) out-of-scope edit; the 19-minor figure is not calibrated: 4 false positives (3 exact-file grep -rn, 1 aborted write()), 3 positives built on truncated text, 6 confirmed misses …, plus 3 item-authorized MANIFEST.json reads …` |
| `round-16.md:79` | `RevCensusStatusFinal.md:359-364` | `…(bound filters never execute;` | `protected reaches refuse; unmeasurable status never becomes a false count or a false clean). F1 (newline worktree path truncation), F2 (relative XDG_CONFIG_HOME/empty HOME), F3 (wt-dirty meaning) and F4 (--include-root gitfile row) are live …` — the quote also leaves an unclosed parenthesis |

Measured gate outcome on the landing: `census/round-16/gate-landing.json` → `checked_markers: 30`, `findings: 0`, `exit: 0`, `resolved_rev: 6ff91f53…`. The gate was green while all five quotes were incomplete. There is no selftest case for a wrapped continuation (`grep -n 'wrapped\|continuation\|first physical\|second line' tools/souji-landing-gate.py` → rc 1, no match).

Two further quotes end at a clause boundary (`ScoutLsFilesPathspec.md:179` "…for both consumers" before a parenthetical; `RevengeSeatViolations.md:260` "…are not violations" before an appositive list). They are not counted as defects here because the quoted clause is syntactically complete; the five above are mid-phrase or mid-parenthesis.

Smallest fix (two parts):

1. Marker = the STATUS **paragraph**, not its first physical line: in `check_carry`, accumulate `raw` plus following physical lines until a blank line (or a line whose first token opens a new heading/STATUS/bullet), normalize the joined block, and use that as `needle`. Lesson carry bullets are already single physical lines, so the existing substring test still works.
2. Add a selftest case where a wrapped STATUS carried only through its first line must fail (`LG-SEAT-UNCARRIED`), and a full-paragraph carry passes.

## F2 — MEDIUM — `round-16.md:54` is the one `resolved:` with no revision

`round-16.md:54`:

> ``- `DraftLessonGate.md:98` "STATUS: skeleton only." — resolved: this lesson supersedes the skeleton.``

Facts: `DraftLessonGate.md:98` is `STATUS: skeleton only. No C1 or C2 decision is made; the lead must run the measurements and open S043 before the \`## Gate\` is final. Census not run by this seat.` The lesson quotes only the first sentence. `skeleton` is not in `FAILURE_STATUS_WORDS` (`tools/souji-landing-gate.py:72-78`), so the gate never treats line 54 as a marker; the bare `resolved:` is invisible to `CARRY_TOKEN_RE` (`:83`, `open|resolved@[0-9a-f]{7,}`) because the line is never evaluated. The lesson has 27 `resolved` forms: 26 `resolved@` lines plus this one bare `resolved:`.

Disposition: `resolved@163158a` is correct — `git log --format='%H %s' -- corpus/lessons/round-16.md` shows the lesson first landed at `163158a` ("round-16: lesson, sources S043-S050, …"), which supersedes the seat's skeleton.

Smallest fix: write the revision (line C1 below). The class rule — every carried `resolved` cites `@<hex>` or `open`, and the gate's vocabulary reaches non-failure STATUS lines that make a claim — is stated at the end of the corrected-lines section.

## F3 — MEDIUM — `round-16.md:91` joins `ConfigRepair.md:9-13` and drops the cause and halt context

Source `ConfigRepair.md:9-13`:

```
`bash -n` reports: `line 1368: syntax error near unexpected token '}'` (the
`}` closing `list_repos`). Edits were in flight when the operator wrap-up
halted work. **The file in tree does NOT parse.** L1 must either complete the
repair or revert to `cc21683` before any acceptance run; do not ship this
state as working.
```

The lesson keeps the ellipsis but elides the two sentences that say the fault is a structural imbalance from in-flight edits and that the operator wrap-up halted work — the only context that makes the disposition ("resolved@cbf688a") auditable. The quote is otherwise verbatim and the ellipsis is marked; the defect is the join, not a silent cut.

Smallest fix: line C4 below (full `:9-13` quote).

## F4 — MEDIUM — `round-16.md:93` paraphrases `ConfigFixture.md:54-59` and drops 2 of 6 conflicts

The lesson line reads "(fixture and repair disagreed on alternateRefsCommand, promisor, includeIf and hooksPath shapes)". `ConfigFixture.md:54-59` flags **six** conflicts: (1) alternateRefsCommand, (2) promisor, (3) unbound non-empty filters, (4) includeIf gitdir + store, (5) `r-wtc-on` `core.worktree = ..`, (6) hooksPath→store. Items 3 and 5 are omitted, and the parenthetical is not marked as a partial summary.

The encodings at `0a70bef` are verifiable (all six):

- 1/2: fixture docstring `:19-22` (promisor never refused; alternateRefsCommand any value), `:61`;
- 3: `R15CFG-13` benign (`:145`), `r-filter-crypt` expected `CLEAN` (`:1283`);
- 4: condition-blind include guarding (`:29-35`, `:475-483`);
- 5: `r-wtc-on` expected `("2","0","0","clean")` (`:655-665`, `:1248`);
- 6: hooksPath accepted for ANY value, neutralized (`:37-39`, `:397`).

Smallest fix: line C5 below (complete six-item enumeration with the `resolved@0a70bef` mapping). The existing disposition remains correct; only its scope was understated.

## F5 — MEDIUM — `RevGateSpec.md:226` never entered any channel

`RevGateSpec.md:226`:

> `STATUS: review complete — no blocking defect in this deliverable; C2's contract needs P1–P9 applied (G1–G6 are pre-adoption blockers) and cannot be green at cbf688a as written.`

First value word `review` is outside `FAILURE_STATUS_WORDS` (`:72-78`) and the line is not backtick-wrapped, so it is not a marker; the r16 lesson's wave-1 list does not carry it, and `DraftReportFinal.md:115` records it as item 25 "G1–G6 blockers; not carried". `RevWaveOneDispositions.md:174-186` later adjudicated it "partial (P3, P6 open)": P1/P4/P5/P7/P8/P9 applied, P3 (`--report`) and P6 (tree scan / mandatory `--base`) not.

Re-checked at HEAD:

- P1: STATUS-anchored, fences/table rows skipped — `tools/souji-landing-gate.py:62-78`, `:257-289`.
- P4: empty wave dir → `EvalError` → exit 2 — `:313-314`, `:586-589`.
- P5: both payload pins present (`tests/fixtures/r15-preservation-frozen/expected.json`: census `64a60fd0…`, r15 config `27474396…`), plus `record_sha256` — `:371-453`.
- P7: `--diff-filter=AM` scripts parsed at REV — `:555-566`.
- P8: record-relative resolution present, but a missing `record` yields `LG-FROZEN-PIN`/exit 1, not the exit 2 P8 specifies (`:428-437`) — the routed RevGateSnapshot S1/S2 exit-2 residual.
- P9: config paths use `cfg_soft` (`tools/souji-census.sh:641-661`); cited per `RevWaveOneDispositions.md:181-182`.
- P2's STATUS-anchored granularity is present, but the continuation of a wrapped STATUS is still not part of the needle (F1) — the disposition should not be read as "wrapped prose carried".
- The material claim "cannot be green at cbf688a as written" is correct: the gate file did not exist there (the seat itself records `ls` → absent). The round-end run is green at `6ff91f5`, not `cbf688a` (`census/round-16/gate-landing.json`).

Smallest fix: line C6 below; the two enforcement patches remain round-17 work.

# Corrected carry lines (draft for the round-17 corrections section)

Written in the r16 lesson's carry style. Source text is verbatim across physical wraps; gate normalization (`norm_line`: NFC, drop `*`/backticks, collapse whitespace) makes the code spans immaterial to the needle. The r16 lesson is not rewritten.

**C1 — replaces `round-16.md:54` (D5-a):**

- `DraftLessonGate.md:98` "STATUS: skeleton only. No C1 or C2 decision is made; the lead must run the measurements and open S043 before the `## Gate` is final. Census not run by this seat." — resolved@163158a (the round-16 lesson first landed at `163158a`, superseding the seat's skeleton; the STATUS reports the seat's own draft, not a lane defect).

**C2 — replaces `round-16.md:73` (D5-b, ReopenS048):**

- `ReopenS048.md:102-103` "STATUS: PARTIAL — S048 fails narrow cell support (scope "parse error"; `(S043)` stretched over shellcheck output; anchor unpinned) while `rejected` / `365d` / `used-by —` hold." — open (r17: narrow the rejected row's scope and anchor cells).

**C3 — replaces `round-16.md:84` (D5-b, ScoutOptionalPrefix):**

- `ScoutOptionalPrefix.md:238-240` "STATUS: FAIL — census strips `:(optional)` for `core.worktree`, which git parses literally (`setup.c:597` `xstrdup`); `souji-census.sh:660` can abort the whole run on a benign config and, for relative values, resolve one level away from git’s effective worktree." — open (r17: stop stripping `:(optional)` for `core.worktree`).

**C4 — replaces `round-16.md:91` (D5-c, ConfigRepair join):**

- `.ufo/waves/round-15/w1/ConfigRepair.md:9-13` "`bash -n` reports: `line 1368: syntax error near unexpected token '}'` (the `}` closing `list_repos`). Edits were in flight when the operator wrap-up halted work. **The file in tree does NOT parse.** L1 must either complete the repair or revert to `cc21683` before any acceptance run; do not ship this state as working." — resolved@cbf688a (r16 C1 restored a parsing census).

**C5 — replaces `round-16.md:93` (D5-c, ConfigFixture paraphrase; complete six-item enumeration, not a quote):**

- `.ufo/waves/round-15/w1/ConfigFixture.md:54-59` — six flagged conflicts, all six: (1) `alternateRefsCommand` non-empty (fixture REFUSE; `AlternateRefs.md` argues inert); (2) promisor markers, RESOLVED by L1, encoded 06/07/09; (3) unbound non-empty filters green per L1, `r-filter-crypt` (R15CFG-13); (4) `includeIf` `gitdir:`/nonexistent + store target, REFUSE condition-blind; (5) `r-wtc-on` `core.worktree = ..`, expected clean; (6) `hooksPath`→store accepted-neutralized. — resolved@0a70bef: 1/2 inert at the fixture docstring (`:19-22`, `:61`); 3 green (`:145`, `:1283`); 4 condition-blind (`:29-35`, `:475-483`); 5 pinned `("2","0","0","clean")` (`:655-665`, `:1248`); 6 any value accepted (`:37-39`, `:397`).

**C6 — new, replaces the uncarried `RevGateSpec.md:226` (D5-d):**

- `.ufo/waves/round-16/w1/RevGateSpec.md:226` "STATUS: review complete — no blocking defect in this deliverable; C2's contract needs P1–P9 applied (G1–G6 are pre-adoption blockers) and cannot be green at cbf688a as written." — partial: P3 (`--report`) and P6 (tree scan / mandatory `--base`) open; P1/P4/P5/P7/P9 present at HEAD; P8's record-relative resolution present but a missing `record` is a finding/exit 1, not exit 2; "cannot be green at cbf688a" holds (gate file absent there) and the round-end run is green at `6ff91f5` (`census/round-16/gate-landing.json`: exit 0, 0 findings, 30 markers).

**C7 — replaces `round-16.md:74` (F1, RerunGateFixture):**

- `RerunGateFixture.md:12-16` "STATUS: PARTIAL — both required executions reproduce (real gate 15/15 PASS, exit 0; null-stub run exit 1 with 14/15 FAIL), but the fixture's own vacuity case (F1) is tautological — it prints PASS in that very null-stub run — and its contract prose (F2) still advertises free-text phrase markers the gate dropped. The headline claim holds; the case that claims to prove it, and the prose beside it, do not." — resolved@fb23b12 (vacuity case now expects exit 0 so only the replay rows decide; fixture docstring's `LG-SEAT-UNCARRIED` description corrected to vocabulary-only; 15/15 re-run).

**C8 — replaces `round-16.md:78` (F1, RerunSeatAudit):**

- `RerunSeatAudit.md:157-162` "STATUS: PARTIAL — selftest, transcript coverage and the 3173-call census hold exactly, and the single major holds as an attempted (failed) out-of-scope edit; the 19-minor figure is not calibrated: 4 false positives (3 exact-file `grep -rn`, 1 aborted `write()`), 3 positives built on truncated text, 6 confirmed misses under the wave text (3 directory-rooted `grep` tool calls, 2 truncation-hidden in-lane recursive commands, 1 bash lane deletion), plus 3 item-authorized `MANIFEST.json` reads that the auditor cannot record as either violation or exception." — resolved@4f9a4e8 (audit restated as neither complete nor precise in Q26, SCORECARD and the lesson).

**C9 — replaces `round-16.md:79` (F1, RevCensusStatusFinal):**

- `RevCensusStatusFinal.md:359-364` "STATUS: PARTIAL — core operability holds (bound filters never execute; protected reaches refuse; unmeasurable status never becomes a false count or a false clean). F1 (newline worktree path truncation), F2 (relative `XDG_CONFIG_HOME`/empty HOME), F3 (`wt-dirty` meaning) and F4 (`--include-root` gitfile row) are live and narrow; the relative-`gitdir` guard base is an adjacent, untested defect outside the assigned five." — open (r17: F1-F4 and the relative gitdir base).

The channel rule for round 17 (smallest complete form): a carried line must reproduce every physical line of the source STATUS paragraph, or end the quote with `…`; a bare `resolved:` is written `resolved@<hex>` or `open`.

# Commands run and observed output

```
grep -n 'resolved:' corpus/lessons/round-16.md
→ 54:- `DraftLessonGate.md:98` "STATUS: skeleton only." — resolved: this lesson supersedes the skeleton.
grep -c 'resolved@' corpus/lessons/round-16.md → 26

grep -n 'STATUS' .ufo/waves/round-16/w2/ReopenS048.md
→ 102:STATUS: PARTIAL — S048 fails narrow cell support (scope "parse error"; `(S043)` stretched over
  103:shellcheck output; anchor unpinned) while `rejected` / `365d` / `used-by —` hold.
grep -n 'STATUS' .ufo/waves/round-16/w2/ScoutOptionalPrefix.md
→ 238:STATUS: FAIL — census strips `:(optional)` for `core.worktree`, which git parses literally
  239:(`setup.c:597` `xstrdup`); `souji-census.sh:660` can abort the whole run on a benign config and, for
  240:relative values, resolve one level away from git’s effective worktree.
grep -n 'STATUS' .ufo/waves/round-16/w1/RevGateSpec.md
→ 226:STATUS: review complete — no blocking defect in this deliverable; C2's contract needs P1–P9 applied (G1–G6 are pre-adoption blockers) and cannot be green at cbf688a as written.

grep -n '' .ufo/waves/round-15/w1/ConfigRepair.md | sed -n '9,13p'
→ the five source lines quoted in C4
grep -n '' .ufo/waves/round-15/w1/ConfigFixture.md | sed -n '54,59p'
→ items 1-6 (alternateRefsCommand, promisor, unbound filters, includeIf, core.worktree=.., hooksPath)

git log --format='%H %s' -- corpus/lessons/round-16.md
→ 6ff91f5… carry wave-2 STATUS lines
  4f9a4e8… wave-2 honesty corrections
  163158a… lesson, sources S043-S050, Q25/Q26, LOG correction and entries, SCORECARD, SKILL, README
git show 163158a:corpus/lessons/round-16.md | grep -n 'DraftLessonGate'
→ 54:- `DraftLessonGate.md:98` "STATUS: skeleton only." — resolved: this lesson supersedes the skeleton.

grep -n 'FAILURE_STATUS_WORDS\s*=\|CARRY_TOKEN_RE =\|needle = norm_line\|needle and needle in nl' tools/souji-landing-gate.py
→ 72:FAILURE_STATUS_WORDS = frozenset(
  83:CARRY_TOKEN_RE = re.compile(r"(?i)\bopen\b|resolved@[0-9a-f]{7,}")
  334:            needle = norm_line(raw)
  338:                if needle and needle in nl and CARRY_TOKEN_RE.search(nl):
grep -n 'wrapped\|continuation\|first physical\|second line' tools/souji-landing-gate.py → rc 1 (no match)

python3 -c "import json;d=json.load(open('census/round-16/gate-landing.json')); …"
→ resolved_rev 6ff91f534eece9adde5f667cb7dad400c145351b; summary {checked_markers: 30, checked_pins: 16, checked_reg: 21, checked_reports: 141, findings: 0}; exit 0

python3 (in-kernel audit): 29 wave-2 bullets; 9 quotes equal their source's first physical line
while the paragraph continues; 5 of those are incomplete (table in F1); the other 4 end at a
complete clause, a colon, or a period.

git show 0a70bef:tests/fixtures/r15-census-config.py | grep -n 'wtc-on\|filter-crypt\|hooksPath\|alternateRefsCommand\|promisor\|includeIf'
→ docstring :19-22/:37-39/:61; R15CFG-12/:144, R15CFG-13/:145; r-wtc-on :655-665 expected :1248
  ("2","0","0","clean"); r-filter-crypt CLEAN :1283

python3 -c "json.load(tests/fixtures/r15-preservation-frozen/expected.json)"
→ files keys: tests/fixtures/r14-census-boundary.py e6a984b1…, tests/fixtures/r15-census-config.py
  27474396…, tools/souji-census.sh 64a60fd0…; record record.json, record_sha256 173db777…

git show --stat --format='%h %s' fb23b12  (+ diff tests/fixtures/r16-landing-gate.py)
→ fixture docstring: phrase markers are NOT a channel since L1 revision 2; vacuity case expects 0
```

# Residual risk and verification gaps

- **Not run:** the gate, census, fixtures and selftests were not executed (probe rule). The F1 blindness proof rests on committed source (`:330-343`) plus the committed landing run (`gate-landing.json`), not on a fresh run.
- The five incomplete quotes are classified by syntax (mid-phrase / unclosed parenthesis); the two clause-boundary truncations are disclosed but not counted.
- C7/C8 reuse the r16 dispositions; `fb23b12`'s diff was read for F1/F2 but the fixture was not re-run. C9's disposition is the r16 one; the full STATUS adds no new claim.
- The `RevGateSpec` P-status is adopted from `RevWaveOneDispositions.md:174-186` with spot checks at the named HEAD lines; P9's census lines were not re-read end to end.
- All line numbers are at HEAD `5fa6017…`; the r16 lesson is historical and unmodified.

# Probe disclosure

Two shell searches used a `*.md` wildcard over the single directory `.ufo/waves/round-16/w2/` (one `grep -rn`, one multi-file `grep -n`) to locate cross-references; neither traversed the lane root or a directory tree. Other reads were exact named files, `git show`/`log`/`cat-file` on named paths, and `sed -n` line ranges on named files. No `jj`, no git write, no lane tool run, no write outside this report.

Tool installs/updates: none.
