# ScoutQualityGaps — r21 wave 1, quality-criteria coverage of r20 routed defects and preregistered claims

Seat: SoujiR21.ScoutQualityGaps-3 (scout, source-only, read-only). Date: 2026-10-21.
Base read: `544c8358039a07e8b45e6db72312da5c8d965275` (git show / git grep at this rev; no lane mutation, no execution, no fixtures, no installs).

Inputs (exact files read):
- `corpus/QUALITY.md` (Q1–Q46 full text)
- `census/round-21/r20-closure-excerpt.json` (full, incl. verification + notes)
- `.ufo/waves/round-21/preregistration.txt` (full, frozen oracle)

Method: every verdict below quotes the governing criterion text; source counterexamples were confirmed by reading pinned bytes, not inferred. Static expectation is labelled as such throughout.

## 1. Routed defects (r20 closure) enumerated

From `r20-closure-excerpt.json` `notes` (verbatim):

- **D1 — F5 reason-field redaction gap**: "`tools/souji-proc-census.sh` reason column (argv-path-gone/fd-path-gone) gets sanitize_field only while cmd gets redact_command (lines 346-368)"; routed: "synthetic-only reason-field redaction+length bound with canary fixture should land next round independent of the historical-exposure ruling unless operator holds it".
- **D2 — ruling-wording overstatement**: "report's 'operator explicitly upheld' overstates the lesson's 'Parent Main confirmed operator/Kagi ownership'".
- **D3 — own-wave write deviation**: "AuditCase07 wrote a fleet-root report (copied to lane, fleet copy removed)".
- **D4 — implicit root-namespace reads**: "implicit root-namespace reads by 5+ seats" (also routed by preregistration as C1's motivation; prereg: "Q45 covers only exact root reads").
- **D5 — relative-path edit attempts**: listed with D3 as disclosed own-wave scope deviations.
- **D6 — render-limit audit noise**: "final wave audit still 3 major/recovery 37 major clipped/unparsed payloads".
- **D7 — acceptance runner not non-author-replayable**: "acceptance runner not non-author-replayable at final HEAD (route: accept --rev without HEAD equality via clean clone)"; verification confirms: "runner refuses non-lane root and requires HEAD==rev, so a non-author cannot replay it at 6ff3413 without mutating the lane checkout".

Preregistration `Frontier:` names exactly four defect→criteria routes: "runner replayability, report/lesson ruling-wording fidelity, implicit root reads, reason redaction" → D7, D2, D4, D1. D3/D5/D6 come from the closure notes' status-neutral list; drafts for their residuals are included but flagged lower-priority (see §5).

## 2. Routed defects → Q coverage

| defect | verdict | governing Q text and reason |
|---|---|---|
| D1 reason-field redaction | **partial** (Q46, Q42, Q33) | Q46 requires the defect be "marked explicitly and routed for operator/Kagi assessment" and "any later canary repair synthetic-only under its own scope" — disclosure/routing only, no repair admission bar. Q42: "Raw argv is read before output redaction, which is not a universal secret-free-read or output-redaction proof" and its test anticipates "a harmless synthetic witness" — names the escalation path, not the bar. Q33's redaction controls are cmd-only ("fake header/AWS/Slack redaction"). **Missing: the repair bar** (pattern parity, byte bound, byte-exact non-secrets, /proc-free entry, canary counts). → Q49 |
| D2 ruling overstatement | **partial** (Q23) | Q23: "Capability wording matches the exercised boundary … retain explicit unobserved labels instead of extrapolating" — about capability claims, applies-to includes reports, but says nothing about paraphrasing an authority's ruling. Q36 gives paragraph-matching discipline but only for STATUS carry. **Missing: authority-paraphrase fidelity.** → Q50 |
| D3 fleet-root report write | **full** for detection (Q39) | Q39: "Only the own report, an exact per-item requested delivery artifact, exact absolute OWN ONLY targets and explicitly granted own scratch roots are allowed … other slots and traversal remain refused." A fleet-root report is outside the declared reportDir → major. The deviation was disclosed and remedied (status-neutral), i.e. Q39 worked. No new criterion needed for the parsed case. Residual: bash-mediated writes → Q51 |
| D4 implicit root-namespace reads | **partial** (Q45, Q26) | Q45: auditor "flags exact root read/glob/grep calls as V-RECURSIVE" — exact root calls only; a relative target resolving at the fleet root is unflagged. Q26 audits "recursive reads over lane or fleet roots" and discloses "rendered arguments truncate". **Missing: relative read-target resolution predicate + oracle-precision bar.** → Q47 |
| D5 relative-path edit attempts | **full** for parsed edits (Q27) | Q27: "a relative write target is `V-WRITE-RELATIVE` (major; relative paths resolve at the fleet root)". Residual: edits issued through Bash are outside the parser (Q44's disclosed limit) → Q51 |
| D6 clipped/unparsed audit payloads | **partial** (Q27, Q26) | Q27 classifies unparsed targets (`V-WRITE-UNPARSED`, major on `⇒ ok`) and requires disposition prose to "name the transcript line it rests on"; Q26 discloses truncation. Neither requires summaries to separate render-limit classifications from confirmed findings, so closure prose can read "37 major" as breaches. → Q52 (optional, wording-level) |
| D7 acceptance replayability | **partial** (Q37, Q24, Q40) | Q37 supplies the full-ID/durable-ref refusal discipline and the "consumer that reads every byte from the revision may name a historical commit" carve-out (the seed of C2's design) but governs `measured_commit` records, not acceptance replay roots. Q24 makes acceptance an L1-only run — the very limitation routed. Q40 binds inputs but not replay-from-clone. **Missing: the non-author-replayable property.** → Q48 |

## 3. Preregistered claims → Q coverage

| claim | verdict | governing Q text and reason |
|---|---|---|
| **C1** V-READ-ROOT (implicit fleet-root-namespace reads; oracle-equal precision+recall; base-discriminating fixture; harm guards) | **partial** (Q45, Q26; regression suites Q27/Q38-era) | Q45 covers explicit root reads only — prereg itself routes on this ("Q45 covers only exact root reads"). No existing Q defines a read-side relative-resolution class, its minor severity + exit-1-on-majors-only semantics, the truncated-target lower bound, or an oracle-equality (precision and recall both exact) admission test. Harm guards reuse existing suites named in Q27/Q39 checks (selftest 118/0; r19-seat-audit-shapes 17/0; r20-audit-contract 78/78/0). → Q47 |
| **C2** run-acceptance.py non-author replay from any local repo, fail-closed refusals, SRC untouched | **partial** (Q37, Q24, Q40) | see D7. Q37 covers C2's full-40-hex/short-refusal rule but not the replay property; Q40's "never writes into SRC" analogue ("external runtime … remain explicit limits") is adjacent, not the same obligation; no Q requires identical per-step summaries across scenario sources or SRC digest/status invariance. → Q48 |
| **C3** reason-field redaction r1–r5, `--reason-only` /proc-free entry point, canary fixture, coverage 1/2→2/2, SOURCES row | **partial** (Q46, Q42, Q33) | see D1. Q42's test line — "keep any reason-field redaction concern explicitly inference unless a harmless synthetic witness establishes it" — is exactly what C3's canary discharges, but no Q sets the repair bar (0 leaks on baseline-construction comparison at 6ff3413 bodies, ≤160 bytes, byte-exact controls, exit-3 no-gone-path, exits before /proc). The C3 SOURCES row (CWE-532 / OWASP Logging Cheat Sheet) needs **no new Q**: corpus admission is the CORPUS.md fleet floor plus Q2-style source citation. → Q49 |

## 4. Source counterexamples observed at 544c8358 (grounding, not execution)

- `tools/souji-seat-audit.py:418,424` — V-RECURSIVE is flagged for calls "rooted at" lane/fleet root (selftest cases :541–543 `read({lane})`, `read({fleet})`, `grep(foo in {lane}/)`); a relative `read("census/round-20/x")` from the seats' fleet-root cwd matches no flag → confirms Q45's gap (D4/C1).
- `tools/souji-proc-census.sh:347,353,367` — gone-path and `reason` emitted through `sanitize_field` only; `:364` cmd through `redact_command` → confirms the D1 asymmetry the closure reports.
- `census/round-20/run-acceptance.py:519` — `raise Refusal("--rev must be the committed current HEAD …")` → confirms the D7 HEAD-equality refusal blocking non-author replay.

## 5. Drafted missing criteria (Q47+ rows; columns per QUALITY.md convention: criterion | applies-to | test | lesson/evidence)

Priority order: Q47–Q50 are the four preregistration-named routes; Q51–Q52 cover the residual status-neutral defects and are optional.

**Q47 — implicit relative read targets (C1/D4).**
| id | criterion | applies-to | test | evidence |
|---|---|---|---|---|
| Q47 | Extends Q45 to implicit read/grep/glob targets: a visible, complete tool-call target that is relative (no leading `/` or `~`, not a URI) resolves lexically at the contract's fleet root (the seats' cwd); when its normalized resolution lands outside the lane it is a minor `V-READ-ROOT`, once per call, `;`-separated components judged per component. Read selectors (`:N`, `:N-M`, `:raw`, comma lists) are stripped before judging; grep with complete untruncated args and no `@` separator is implicit-cwd. Absolute, `~` and URI targets are never read-root; a target truncated by transcript rendering is a disclosed lower bound, never a clearance. Severity and exit semantics are unchanged (exit 1 on majors only); Q45's exact-root `V-RECURSIVE` class is untouched. | `tools/souji-seat-audit.py`; published audit dispositions | the changed auditor over every committed r20 transcript equals an independent per-call oracle in precision and recall (both exact; any disagreement falsifies); `tests/fixtures/r21-read-root.py --tool T --base-tool B`: every positive case base-discriminating; harm guards: auditor `--selftest` 118/0, r19-seat-audit-shapes 17/0 (12 base-disc), r20-audit-contract 78/78/0 (11 base-disc), no existing per-class verdict change on committed r20 transcripts | r20 closure notes "implicit root-namespace reads by 5+ seats"; corpus/lessons/round-20.md R20-M17 (Q45's origin); preregistration C1; observation `tools/souji-seat-audit.py:418,424` @544c8358 |

**Q48 — non-author acceptance replay (C2/D7).**
| id | criterion | applies-to | test | evidence |
|---|---|---|---|---|
| Q48 | An acceptance or evidence command that measures a revision is non-author-replayable: it runs from any local git repository containing the rev (working clone, bare mirror, the lane), never requires the source path to equal the lane or source HEAD to equal the rev, and measures a private clone (quiet, `--no-local --no-checkout`, hooks disabled, detached checkout verified, clean status) instead of the source tree. It refuses fail-closed (exit 2, no output, nothing written into the source) a rev whose executed step programs embed the literal absolute lane path, short or non-durable revs, an existing output path, or an output inside the clone or any measured input directory. Extends Q37's full-ID/durable-ref rule without relaxing it; converts Q24's L1-only acceptance into a property any seat can re-derive. | census/round-NN acceptance runners and evidence-producing commands; landing receipts | scenario matrix — S1 scratch clone HEAD≠rev, S2 bare mirror, S3 lane root HEAD≠rev: baseline runner refuses all three (0/3); changed runner exit 0, all_matched 18/18, identical per-step summaries across scenarios (3/3); source digest and `git status --porcelain` identical before and after; refused rev classes still refuse | r20 closure verification "Evidence-verified only (not re-run) … runner refuses non-lane root and requires HEAD==rev, so a non-author cannot replay it at 6ff3413 without mutating the lane checkout"; r20 closure notes routed "acceptance runner not non-author-replayable at final HEAD"; observation `census/round-20/run-acceptance.py:519` @544c8358 |

**Q49 — free-text output-field redaction parity with byte bound (C3/D1).**
| id | criterion | applies-to | test | evidence |
|---|---|---|---|---|
| Q49 | Every free-text output field that can carry path text drawn from another process's argv or fd names is sanitized by the same secret patterns as the tool's already-redacted field, control-byte-replaced, and bounded to a fixed byte length (160); non-secret text stays byte-exact. The repair is synthetic-only — fabricated canaries, never real credentials, never live /proc, never the r18 live fixture or a live census — and any new entry point that renders the field exits before any /proc or boot_id read and calls the same functions as the census loop. Grounds Q46's anticipated repair as an admission bar; discharges Q42's inference-until-synthetic-witness wording with the witness. | `tools/souji-proc-census.sh` reason field; PROVINCE privacy wording; SKILL F5 capability row | `tests/fixtures/r21-reason-canary.sh --tool T [--base B]`: baseline reason construction from the exact 6ff3413 function bodies leaks every argv/fd canary; changed tool leaks 0, every reason ≤160 bytes, non-secret controls byte-exact; `--reason-only argv\|fd` prints exactly the census-loop field (exit 0), nothing + exit 3 when no gone path; coverage observation free-text secret redaction 1/2 → 2/2 (cmd, reason) | r20 closure F5 RULING + routed "synthetic-only reason-field redaction+length bound with canary fixture"; Q46; corpus/lessons/round-20.md final F5 privacy disposition; SOURCES row on CWE-532 / OWASP Logging Cheat Sheet (opened when C3 lands); observation `tools/souji-proc-census.sh:347,353,367` vs `:364` @544c8358 |

**Q50 — authority-paraphrase fidelity (D2).**
| id | criterion | applies-to | test | evidence |
|---|---|---|---|---|
| Q50 | A report, lesson, SCORECARD or closure sentence that characterizes what an authority said (operator, lesson, ruling, MANIFEST verdict, outside disposition) may not strengthen the source: uphold/approve/admit/confirm/own wording is carried as a bounded verbatim quote (≤25 words) with its location, or as the exact normalized paragraph per Q36's matching; paraphrase stays at or below the source's commitment. Extends Q23 from capability wording to authority wording. | round reports, round lessons, SCORECARD trend rows, closure notes | for each authority-characterizing sentence, resolve the cited source at its recorded revision and compare; a fidelity check must fail "operator explicitly upheld" where the source says only ownership confirmation and pass the corrected wording; existing Q36 carry and Q31 pointer checks unchanged | r20 closure notes routed "report's 'operator explicitly upheld' overstates the lesson's 'Parent Main confirmed operator/Kagi ownership'"; corpus/lessons/round-20.md (source wording); r20 closure rechecks S096 ≤25-word quote discipline |

**Q51 — Bash-mediated write classification (D3/D5 residual; optional).**
| id | criterion | applies-to | test | evidence |
|---|---|---|---|---|
| Q51 | A Bash call whose rendered text contains a fully visible write destination (`>`, `>>`, `tee`, `cp`/`mv`/`install` destination, heredoc target) is classified by the same shapes as parsed write/edit targets: relative destinations are `V-WRITE-RELATIVE` (Q27), protected or unrequested destinations stay major (Q39); a destination made unparsable by parameter expansion, quoting or truncation is `V-WRITE-UNPARSED`, never certified clean. Lexical only; the command is never executed or expanded. Resolves Q44's disclosed "arbitrary Bash-generated writes remain outside that parser" limit for the visible-destination class without claiming shell semantics. | seat auditor Bash-call classification; wave contracts | baseline/changed auditor fixture: fleet-root redirect, relative redirect, `tee` outside reportDir flagged; parameter-expansion and truncated destinations reported unparsed (major on `⇒ ok`); r19-seat-audit-shapes and r20-audit-contract suites unchanged | r20 closure notes "own-wave scope deviations disclosed — AuditCase07 wrote a fleet-root report …, relative-path edit attempts"; Q44; corpus/lessons/round-20.md R20-M11 |

**Q52 — render-limit findings disclosed in summaries (D6; optional, wording-level).**
| id | criterion | applies-to | test | evidence |
|---|---|---|---|---|
| Q52 | A published audit summary or wave closure that cites audit findings separates confirmed parsed findings from lower-bound render-limit classifications (`V-WRITE-UNPARSED` on truncated targets; truncated-target read lower bounds) and discloses the unparsed share. Severity is not lowered (Q27 stands); a count quoted without the split may not be read as confirmed scope breaches. Extends Q26's disclosed-limits wording into the summary layer. | seat-audit JSON summaries, round reports, closure notes | replay over the r20 transcript set reports per-class counts with a truncated-target split; a closure citing the r20 "3 major/recovery 37 major" figure carries the unparsed share; existing verdict bytes unchanged | r20 closure notes "final wave audit still 3 major/recovery 37 major clipped/unparsed payloads"; Q26; Q27 |

## 6. Limits and calibration notes

- Source-only seat: nothing executed — no fixtures, selftests, census, or live /proc; all pass/fail counts cited above are preregistration/closure expectations, not my observations. Observation limited to: `git grep`/`git show` at 544c8358 over named paths (tools, census/round-20) and the three input files.
- D3's parsed case and D5's parsed case are already fully covered (Q39, Q27) — I draft no replacement row for them; drafting one would duplicate existing criteria (the QUALITY.md rule: supersede by naming, never rewrite).
- The preregistration `Held:` items (certification OFF, K5, F5 reap, r14 NAMESPACE pin, F5 historical-exposure assessment) are operator-held authority, not routed defects; Q14/Q42/Q46 already mark their boundaries. No criterion drafted — adding one would re-litigate operator L0 scope.
- Coverage-observation wording in C3 ("1/2 → 2/2") is a SCORECARD/PROVINCE claim whose admission is already governed by Q23 (capability wording matches exercised boundary); Q49 references it as evidence, not as a new bar.
- No tool installs or upgrades performed (none needed). No VCS mutation anywhere.
