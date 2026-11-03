# S56reviewer01 — C1 adversarial review

VERDICT: ATTACK-FOUND

Recommendation only; no admission, integration, or frozen-file edit.

## Scope, axes, and provenance

Calibration 7 (C1), coverage 8, operability 8; this seat attacks C1 calibration/no-harm only. Measured source revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83`; lane base: `fafe371694fea41c5d23f63083865d5ccf3f1d36`. Preregistration was read before probing. Counter/builder/expected pins all matched committed `git show` bytes before execution (receipt below). Counters ran byte-exact scratch copies, not lane working-tree scripts. Each v4/v5 comparison used exactly the same fixture commit, base, record pin, and source revisions.

The L1 clarified the contradictory bounds: committed builder/helpers may init/config/add/commit only under this seat's asserted scratch fixture roots; lane/fleet/sibling mutations remain forbidden. Every fixture commit was guarded by `git rev-parse --show-toplevel == fixture root` and scratch ancestry. Only those fixture-local mutations occurred. No lane tracked file was changed. No other runtime or subagent was dispatched. The LSP device is not mounted (`read xd://lsp`: No such tool); textual code inspection is fallback, not semantic-reference proof.

Disk guard before the passes: `/fast/scratch/hyaku` free 405.5G (50% used), `/tmp` free 95.9G. No ENOSPC. Installed scratch-only `markdown-it-py 4.2.0` and dependency `mdurl 0.1.2` via official PyPI using existing `uv 0.13.0`; purpose: independent CommonMark rendering evidence. No pacman, PATH-directory change, or service restart.

## Findings by severity

### HIGH — actual hidden corrections pass after the opener narrowing (HARM B4 and C4)

At `census/round-56/c1-counter.py:237-241`, the v4 `if '<!--' in ln` opener became `indent <= 3 and stripped.startswith('<!--')`. At `:338`, that hidden set feeds `:422-424` (CORRECTION-IN-FENCE) and `:506-507` (filedness). A real inline HTML comment is not necessarily a block-start comment.

* **B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION**: exact prefix is UTF-8 `c2 a0 3c 21 2d 2d` (`\u00a0<!--`), followed by both honest R52 correction lines and `-->`. It is not the frozen F29 prose-token fixture. CommonMark parser output contains both correction tokens inside a real HTML comment, with **zero visible paragraph/code tokens**. v4 refuses with CORRECTION-IN-FENCE, exit 1. v5 passes with `mismatches=2 filed=2 unfiled=0 fenced=0`, exit 0. Hidden lines are admitted as filings.
* **C4-INLINE-COMMENT-SPANS-CORRECTIONS**: `Note: prose opens an inline comment <!-- here` followed by the two corrections and a later `-->`. Unlike F29's mere unclosed mention, this is a closed multiline inline comment; the independent render hides both corrections. v4 refuses, exit 1; v5 passes, exit 0. This shares the F29 opener family but demonstrates real semantic over-acceptance, not an honest visible repair. Do not count it as a separate root cause from B4.

Receipts below include exact bytes, both commands, fixture commit IDs, findings, and exit codes. Independent rendered HTML is preserved in `reproduction/b4_nbsp_prefix_opener_hides_correction.html` and `reproduction/c4_inline_comment_spans_corrections.html`.

### MEDIUM — disclosed exotic fence closer limit remains reproducible (LIMIT D1–D5)

At `census/round-56/c1-counter.py:217,223-229`, unrestricted `rstrip()` removes VT, FF, NEL, and U+2028 after a closing run. Both counters pass D1–D5 with corrections marked filed. The CommonMark parser keeps the fence open and puts both correction tokens in **code**, not live paragraph text. D6 with a trailing TAB is the legal closer control and leaves both corrections as paragraph text. These are existing/disclosed A09–A13-class limits (`:117-119`), not new narrowing and not an assertion that the frozen fixture predicates failed.

### MEDIUM — unchanged binary pair sites have no file-level refusal (LIMIT F1–F3)

At `census/round-56/c1-counter.py:439-454`, LOG.md and corpus/README.md are decoded and regex-scanned without the correction file's NUL check (`:323-327`). `3\x00 -> 4` evades the pair regex; `corpus/SOURCES\x00.md` evades the literal path test. F1–F3 are unchanged base→tip, so the numstat refusal at `:426-437` is unavailable. Both versions exit 0. F4, the otherwise equivalent unchanged LOG overstatement without NUL, gets UNFILED-SOURCES-ANNOTATION and exit 1 in both. This is a byte-integrity/malformed-annotation limit, not proof that an intact syntactically valid pair annotation is missed. README bytes and empty pair-site numstats are separately preserved.

### LOW — stale named-limit documentation

`census/round-56/c1-counter.py:113-116` still says a prose mention of `<!--` opens a region, conflicting with `:51` and the actual `:237` implementation. This does not alter the measured counter results but makes the disclosed boundary misleading.

## Primary output: all narrowing HARM rows

The seat definition calls any v4 refusal→v5 pass outside the exact deliberate F29 fixture a HARM. Five attack rows satisfy that mechanical rule; semantic severity differs:

| Row | v4 | v5 | Interpretation |
|---|---|---|---|
| B2 TAB opener around corrections | 1 CORRECTION-IN-FENCE | 0 | HARM mechanically; CommonMark renders filings visibly. Benign false-positive repair, not hidden-filing defect. |
| B3 four-space opener around corrections | 1 CORRECTION-IN-FENCE | 0 | HARM mechanically; likewise visible in CommonMark; related to the explicitly deliberate S2 repair. |
| B4 NBSP prefix opener | 1 CORRECTION-IN-FENCE | 0 | **Actual hidden-filing HARM**, strongest non-prose witness. |
| B5 BOM at byte zero | 1 CORRECTION-IN-FENCE | 0 | HARM mechanically; parser did NOT hide the filings in this exact fixture. No BOM-rendering vulnerability claimed. |
| C4 closed multiline inline comment | 1 CORRECTION-IN-FENCE | 0 | **Actual hidden-filing HARM**, F29-family boundary failure; same root cause as B4. |

The 33 committed fixture controls reproduce the frozen v5 expected rc/first-finding matrix: all 33 pass. Their only v4-refusal→v5-pass row is F29; their tightening set is exactly F24/F26/F28. Thus this review does **not** assert failure of the frozen finite matrix targets T1–T5. It identifies out-of-fixture harm/limits for routing, without broadening that finite claim.

## Complete attack table

`—` means no FINDING line, not necessarily success. Each named row links to its full receipt below. NAMED = a printed finding; HARM = v4 nonzero/v5 zero; LIMIT = unrefused known/malformed-byte boundary; OK = expected control/refusal without a named finding.

| Attack | v4 rc:first | v5 rc:first | Class |
|---|---|---|---|
| CTRL-DEFAULT-HONEST | 0:- | 0:- | OK |
| A1-ONELINE2-HIDDEN-THEN-HONEST | 1:CORRECTION-IN-FENCE | 1:CORRECTION-IN-FENCE | NAMED |
| A1b-ONELINE1-ONLY | 1:CORRECTION-IN-FENCE | 1:CORRECTION-IN-FENCE | NAMED |
| A1c-ONELINE3-TRAILING-TEXT | 1:- | 1:- | OK (unfiled, unnamed refusal) |
| A2-MULTILINE-COMMENT-HONEST | 1:CORRECTION-IN-FENCE | 1:CORRECTION-IN-FENCE | NAMED |
| B1-TAB-OPENER-HIDES-PAIR-LOG | 0:- | 1:UNFILED-SOURCES-ANNOTATION | NAMED |
| B2-TAB-OPENER-HIDES-CORRECTION | 1:CORRECTION-IN-FENCE | 0:- | HARM |
| B3-FOUR-SPACE-OPENER-HIDES-CORRECTION | 1:CORRECTION-IN-FENCE | 0:- | HARM |
| B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION | 1:CORRECTION-IN-FENCE | 0:- | HARM |
| B5-BOM-LINE1-COMMENT-OPENER | 1:CORRECTION-IN-FENCE | 0:- | HARM |
| C1-FENCE-IN-COMMENT-PAIR-FILING | 0:- | 1:UNFILED-SOURCES-ANNOTATION | NAMED |
| C2-COMMENT-IN-FENCE-PAIR-FILING | 0:- | 1:UNFILED-SOURCES-ANNOTATION | NAMED |
| C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED | 0:- | 1:UNFILED-SOURCES-ANNOTATION | NAMED |
| C4-INLINE-COMMENT-SPANS-CORRECTIONS | 1:CORRECTION-IN-FENCE | 0:- | HARM |
| C5-INLINE-COMMENT-HIDES-PAIR-LOG | 0:- | 1:UNFILED-SOURCES-ANNOTATION | NAMED |
| D1-VT-CLOSER-FENCE | 0:- | 0:- | LIMIT |
| D2-FF-CLOSER-FENCE | 0:- | 0:- | LIMIT |
| D3-NEL-CLOSER-FENCE | 0:- | 0:- | LIMIT |
| D4-LS-CLOSER-FENCE | 0:- | 0:- | LIMIT |
| D5-TILDE-VT-CLOSER-FENCE | 0:- | 0:- | LIMIT |
| D6-TAB-CLOSER-FENCE-CONTROL | 0:- | 0:- | OK |
| E1-NUL-BOGUS-LINE-HONEST-DEFAULT | 1:DELETED-LINES | 1:CORRECTION-FILE-BINARY | NAMED |
| E2-NUL-ON-HONEST-SC-FILING | 1:DELETED-LINES | 1:CORRECTION-FILE-BINARY | NAMED |
| E3-NUL-INSIDE-FENCE-LINE | 1:DELETED-LINES | 1:CORRECTION-FILE-BINARY | NAMED |
| E4-NUL-BEFORE-TOKEN-SAME-LINE | 1:DELETED-LINES | 1:CORRECTION-FILE-BINARY | NAMED |
| F1-NUL-IN-LOG-PAIR-UNCHANGED | 0:- | 0:- | LIMIT |
| F2-NUL-IN-README-PAIR-UNCHANGED | 0:- | 0:- | LIMIT |
| F3-NUL-IN-PATH-TOKEN-UNCHANGED | 0:- | 0:- | LIMIT |
| F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL | 1:UNFILED-SOURCES-ANNOTATION | 1:UNFILED-SOURCES-ANNOTATION | NAMED |

29 cases: 5 mechanical HARM, 8 LIMIT, 13 NAMED, 3 OK. Required classes (a)–(g) are covered by A, B, C, D, E, F, and the HARM table respectively.

### Harness expectation mismatches (reported, not suppressed or rerun)

A1c has trailing text after `-->`, so the anchored correction regex does not lex it: both counters refuse via `unfiled=1`, with **no** FINDING line, not the harness's predicted CORRECTION-IN-FENCE. E1/E3/E4 were predicted v4-pass but actually v4-refuse with DELETED-LINES, because SCORECARD changes to binary across base→tip; v5 still refuses with CORRECTION-FILE-BINARY as required. These four expectation errors remain explicitly marked in raw receipts and the raw table. Observed results, not predictions, drive this report. There was no rerun to erase them.

### Invocation and reproducibility

Executed from this seat's scratch root, with TMPDIR set there:

```text
<scratch>/venv/bin/python -B <scratch>/bin/attacks.py control
EXIT=0
<scratch>/venv/bin/python -B <scratch>/bin/attacks.py attacks
EXIT=0
```

The harness imports the committed builder and uses its `init_repo`, `sc_base_lines`, `pre_base_lines`, `RECORD_BODY`, `REGISTRY_3ROWS`, `write`, and guarded `commit_all` pattern. Its 29 attack branches are preserved in `reproduction/attacks.py`; exact frozen builder and counter bytes are alongside it. It uses fixed fixture dates. To reproduce after scratch cleanup, recreate this seat's scratch/bin, copy those preserved files there, create a scratch venv with the recorded parser versions, and invoke the above two modes. All per-case invocations below are exact executed commands, not suggestions.

## Residual risk and verification gaps

* This is a bounded 29-case attack, not exhaustive parser equivalence, saturation, or a production Markdown-renderer audit. The CommonMark evidence is markdown-it-py 4.2.0's commonmark preset, not a test of the lane's actual renderer.
* NUL-corrupted pair shapes are malformed-text boundaries; the report does not equate a replacement character with a valid numeric pair.
* The finite committed matrix held. I did not rerun the counter's CLI `--selftest` pin-validation path, the real-lane measurement, C2, other runtime admission/rerouting logic, or resume_continuity_v1. Those are outside this C1 leaf's scope; no claims about them are made.
* LSP references/definition/diagnostics could not run because no LSP device is mounted. Source-line evidence is committed text plus black-box counter receipts, not semantic server proof.
* Scratch is removed before terminal handoff. Reproduction sources/bytes/receipts and two independent render outputs remain in the seat directory.

## Self-evaluation

Accuracy 4/5: raw expectations had four documented mismatches; report uses observed outcomes and distinguishes benign narrowing from actual hidden filings. Completeness 5/5: every required attack class has paired receipts. Clarity 4/5: large embedded receipts are needed for auditability. Actionability 5/5: exact root cause, source lines, fixture branches, pins and commands preserved. Conciseness 4/5: full receipts add length but avoid an evidence-only external dependency. Overall 4.4/5. Highest-impact improvements were applied: qualify benign HARM rows, keep malformed-NUL limits narrow, and preserve actual parser renders. The user should be able to distinguish evidence from interpretation.

## Embedded command receipts

### A1-ONELINE2-HIDDEN-THEN-HONEST.txt

```text
CASE A1-ONELINE2-HIDDEN-THEN-HONEST
KIND named  CLASS NAMED(both-refuse)
NOTE two-space `<!--` one-line comment carries a correction; honest filing on next line
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1_oneline2_hidden_then_honest base=c01b89e41eb9ddb719e3d43c874d32eb475fba95 tip=58f2a890f7053c00ae5b0bc8e0556bbefe4861a9
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, a1_oneline2_hidden_then_honest)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n  <!-- R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79 -->\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=1; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1_oneline2_hidden_then_honest --rev 58f2a890f7053c00ae5b0bc8e0556bbefe4861a9 --base c01b89e41eb9ddb719e3d43c874d32eb475fba95 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 58f2a890f7053c00ae5b0bc8e0556bbefe4861a9 --sources-rev-after 58f2a890f7053c00ae5b0bc8e0556bbefe4861a9 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A1-ONELINE2-HIDDEN-THEN-HONEST
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=58f2a890f705 base=c01b89e41eb9
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1_oneline2_hidden_then_honest --rev 58f2a890f7053c00ae5b0bc8e0556bbefe4861a9 --base c01b89e41eb9ddb719e3d43c874d32eb475fba95 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 58f2a890f7053c00ae5b0bc8e0556bbefe4861a9 --sources-rev-after 58f2a890f7053c00ae5b0bc8e0556bbefe4861a9 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A1-ONELINE2-HIDDEN-THEN-HONEST
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=58f2a890f705 base=c01b89e41eb9
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=58f2a890f705 base=c01b89e41eb9
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=58f2a890f705 base=c01b89e41eb9
EXPECTATION-CHECK ok
EXIT=0
```

### A1b-ONELINE1-ONLY.txt

```text
CASE A1b-ONELINE1-ONLY
KIND named  CLASS NAMED(both-refuse)
NOTE one-space `<!--` one-line comment is the only SCORECARD filing
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1b_oneline1_only base=fdbb64bc191fcf1da5338d72c11c7a0db3e0a1ee tip=350b0803ed3d08b8034e229baef6689fb4e85cbd
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, a1b_oneline1_only)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n <!-- R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79 -->\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=1 code=0 hidden_comment=1; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1b_oneline1_only --rev 350b0803ed3d08b8034e229baef6689fb4e85cbd --base fdbb64bc191fcf1da5338d72c11c7a0db3e0a1ee --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 350b0803ed3d08b8034e229baef6689fb4e85cbd --sources-rev-after 350b0803ed3d08b8034e229baef6689fb4e85cbd --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A1b-ONELINE1-ONLY
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=350b0803ed3d base=fdbb64bc191f
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1b_oneline1_only --rev 350b0803ed3d08b8034e229baef6689fb4e85cbd --base fdbb64bc191fcf1da5338d72c11c7a0db3e0a1ee --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 350b0803ed3d08b8034e229baef6689fb4e85cbd --sources-rev-after 350b0803ed3d08b8034e229baef6689fb4e85cbd --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A1b-ONELINE1-ONLY
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=350b0803ed3d base=fdbb64bc191f
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=350b0803ed3d base=fdbb64bc191f
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=1 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=350b0803ed3d base=fdbb64bc191f
EXPECTATION-CHECK ok
EXIT=0
```

### A1c-ONELINE3-TRAILING-TEXT.txt

```text
CASE A1c-ONELINE3-TRAILING-TEXT
KIND named  CLASS NAMED(both-refuse)
NOTE three-space one-line comment, text after the closer, sole SCORECARD filing
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1c_oneline3_trailing_text base=819633b2ddb5faea4e7fa99b605493bcb928862c tip=3438d359841ae5fafc1243370bd0b6456b712fa3
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, a1c_oneline3_trailing_text)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n   <!-- R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79 --> trailing\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=1 code=0 hidden_comment=1; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1c_oneline3_trailing_text --rev 3438d359841ae5fafc1243370bd0b6456b712fa3 --base 819633b2ddb5faea4e7fa99b605493bcb928862c --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 3438d359841ae5fafc1243370bd0b6456b712fa3 --sources-rev-after 3438d359841ae5fafc1243370bd0b6456b712fa3 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A1c-ONELINE3-TRAILING-TEXT
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=3438d359841a base=819633b2ddb5
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a1c_oneline3_trailing_text --rev 3438d359841ae5fafc1243370bd0b6456b712fa3 --base 819633b2ddb5faea4e7fa99b605493bcb928862c --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 3438d359841ae5fafc1243370bd0b6456b712fa3 --sources-rev-after 3438d359841ae5fafc1243370bd0b6456b712fa3 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A1c-ONELINE3-TRAILING-TEXT
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=3438d359841a base=819633b2ddb5
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=3438d359841a base=819633b2ddb5
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=3438d359841a base=819633b2ddb5
EXPECTATION-CHECK MISMATCH
EXIT=0
```

### A2-MULTILINE-COMMENT-HONEST.txt

```text
CASE A2-MULTILINE-COMMENT-HONEST
KIND named  CLASS NAMED(both-refuse)
NOTE multi-line comment opened at 2 spaces wraps honest SCORECARD filings
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/a2_multiline_comment_honest base=fb268e223ef2714aa21c51677f6127421c4a7876 tip=1519661c96b4ca54a28696d77490f3ca7ce9a385
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, a2_multiline_comment_honest)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n  <!-- open\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n  -->\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=0 hidden_comment=2; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a2_multiline_comment_honest --rev 1519661c96b4ca54a28696d77490f3ca7ce9a385 --base fb268e223ef2714aa21c51677f6127421c4a7876 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 1519661c96b4ca54a28696d77490f3ca7ce9a385 --sources-rev-after 1519661c96b4ca54a28696d77490f3ca7ce9a385 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A2-MULTILINE-COMMENT-HONEST
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=1519661c96b4 base=fb268e223ef2
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/a2_multiline_comment_honest --rev 1519661c96b4ca54a28696d77490f3ca7ce9a385 --base fb268e223ef2714aa21c51677f6127421c4a7876 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 1519661c96b4ca54a28696d77490f3ca7ce9a385 --sources-rev-after 1519661c96b4ca54a28696d77490f3ca7ce9a385 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/A2-MULTILINE-COMMENT-HONEST
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=1519661c96b4 base=fb268e223ef2
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=1519661c96b4 base=fb268e223ef2
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=1519661c96b4 base=fb268e223ef2
EXPECTATION-CHECK ok
EXIT=0
```

### B1-TAB-OPENER-HIDES-PAIR-LOG.txt

```text
CASE B1-TAB-OPENER-HIDES-PAIR-LOG
KIND named  CLASS NAMED(tightened)
NOTE tab-indented `<!--` in LOG.md hides an overstated pair line (v4 skips it)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/b1_tab_opener_hides_pair_log base=33143b70c25c4f2c37988d2f9f95e2beb4e8475d tip=b635e06272279839c568779e145ff08647352658
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, b1_tab_opener_hides_pair_log)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
'# fixture log\n\t<!-- side note\n- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.\n\t-->\n'
CM (markdown-it-py 4.2.0 commonmark): corpus/SOURCES.md para=1 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b1_tab_opener_hides_pair_log --rev b635e06272279839c568779e145ff08647352658 --base 33143b70c25c4f2c37988d2f9f95e2beb4e8475d --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before b635e06272279839c568779e145ff08647352658 --sources-rev-after b635e06272279839c568779e145ff08647352658 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B1-TAB-OPENER-HIDES-PAIR-LOG
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=b635e0627227 base=33143b70c25c
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b1_tab_opener_hides_pair_log --rev b635e06272279839c568779e145ff08647352658 --base 33143b70c25c4f2c37988d2f9f95e2beb4e8475d --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before b635e06272279839c568779e145ff08647352658 --sources-rev-after b635e06272279839c568779e145ff08647352658 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B1-TAB-OPENER-HIDES-PAIR-LOG
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:3 claims 999 -> 1000 rows but the registry holds 3; no pair-form filing names it
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=b635e0627227 base=33143b70c25c
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=b635e0627227 base=33143b70c25c
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=b635e0627227 base=33143b70c25c
EXPECTATION-CHECK ok
EXIT=0
```

### B2-TAB-OPENER-HIDES-CORRECTION.txt

```text
CASE B2-TAB-OPENER-HIDES-CORRECTION
KIND harm  CLASS HARM
NOTE tab-indented `<!--` opens a region in v4 that hides honest SCORECARD filings
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/b2_tab_opener_hides_correction base=a733ac32e19a9c56e49663f6e974d97be5fb10d7 tip=459c162e39d2926e8b318d24b6a5d8b553c7c575
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, b2_tab_opener_hides_correction)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n\t<!--\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\t-->\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b2_tab_opener_hides_correction --rev 459c162e39d2926e8b318d24b6a5d8b553c7c575 --base a733ac32e19a9c56e49663f6e974d97be5fb10d7 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 459c162e39d2926e8b318d24b6a5d8b553c7c575 --sources-rev-after 459c162e39d2926e8b318d24b6a5d8b553c7c575 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B2-TAB-OPENER-HIDES-CORRECTION
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=459c162e39d2 base=a733ac32e19a
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b2_tab_opener_hides_correction --rev 459c162e39d2926e8b318d24b6a5d8b553c7c575 --base a733ac32e19a9c56e49663f6e974d97be5fb10d7 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 459c162e39d2926e8b318d24b6a5d8b553c7c575 --sources-rev-after 459c162e39d2926e8b318d24b6a5d8b553c7c575 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B2-TAB-OPENER-HIDES-CORRECTION
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=459c162e39d2 base=a733ac32e19a
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=459c162e39d2 base=a733ac32e19a
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=459c162e39d2 base=a733ac32e19a
EXPECTATION-CHECK ok
EXIT=0
```

### B3-FOUR-SPACE-OPENER-HIDES-CORRECTION.txt

```text
CASE B3-FOUR-SPACE-OPENER-HIDES-CORRECTION
KIND harm  CLASS HARM
NOTE four-space `<!--` (S2 class, deliberate repair) hides honest filings in v4
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/b3_four_space_opener_hides_correction base=9f1180352ef95e5bd7f99b0984878a085f28ad36 tip=f288c88f9445987d4f244449c1cb70556b6b7863
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, b3_four_space_opener_hides_correction)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n    <!--\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n    -->\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b3_four_space_opener_hides_correction --rev f288c88f9445987d4f244449c1cb70556b6b7863 --base 9f1180352ef95e5bd7f99b0984878a085f28ad36 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before f288c88f9445987d4f244449c1cb70556b6b7863 --sources-rev-after f288c88f9445987d4f244449c1cb70556b6b7863 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B3-FOUR-SPACE-OPENER-HIDES-CORRECTION
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=f288c88f9445 base=9f1180352ef9
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b3_four_space_opener_hides_correction --rev f288c88f9445987d4f244449c1cb70556b6b7863 --base 9f1180352ef95e5bd7f99b0984878a085f28ad36 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before f288c88f9445987d4f244449c1cb70556b6b7863 --sources-rev-after f288c88f9445987d4f244449c1cb70556b6b7863 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B3-FOUR-SPACE-OPENER-HIDES-CORRECTION
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f288c88f9445 base=9f1180352ef9
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=f288c88f9445 base=9f1180352ef9
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f288c88f9445 base=9f1180352ef9
EXPECTATION-CHECK ok
EXIT=0
```

### B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION.txt

```text
CASE B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION
KIND harm  CLASS HARM
NOTE NBSP before `<!--` is not indentation: v5 sees no opener; CommonMark reads an inline comment
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/b4_nbsp_prefix_opener_hides_correction base=bd087251ea34ef1b2588689be8d61eb05bfcd7ef tip=2f6c590dcdd37d7a447009bbd9d9f03e17c5860e
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, b4_nbsp_prefix_opener_hides_correction)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n\xa0<!--\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n-->\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=0 hidden_comment=2; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b4_nbsp_prefix_opener_hides_correction --rev 2f6c590dcdd37d7a447009bbd9d9f03e17c5860e --base bd087251ea34ef1b2588689be8d61eb05bfcd7ef --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 2f6c590dcdd37d7a447009bbd9d9f03e17c5860e --sources-rev-after 2f6c590dcdd37d7a447009bbd9d9f03e17c5860e --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=2f6c590dcdd3 base=bd087251ea34
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b4_nbsp_prefix_opener_hides_correction --rev 2f6c590dcdd37d7a447009bbd9d9f03e17c5860e --base bd087251ea34ef1b2588689be8d61eb05bfcd7ef --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 2f6c590dcdd37d7a447009bbd9d9f03e17c5860e --sources-rev-after 2f6c590dcdd37d7a447009bbd9d9f03e17c5860e --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=2f6c590dcdd3 base=bd087251ea34
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=2f6c590dcdd3 base=bd087251ea34
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=2f6c590dcdd3 base=bd087251ea34
EXPECTATION-CHECK ok
EXIT=0
```

### B5-BOM-LINE1-COMMENT-OPENER.txt

```text
CASE B5-BOM-LINE1-COMMENT-OPENER
KIND harm  CLASS HARM
NOTE UTF-8 BOM at byte 0 precedes a `<!--` opener on line 1 (comment spans the tail)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/b5_bom_line1_comment_opener base=0cb71375c9330f7c742fb0073d4e33fa0e7b1409 tip=8b3394f3788e6040490041fcd795681f477369e9
SCORECARD.md tip bytes (repr):
'\ufeff<!-- BOM opener at byte 0\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n-->\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b5_bom_line1_comment_opener --rev 8b3394f3788e6040490041fcd795681f477369e9 --base 0cb71375c9330f7c742fb0073d4e33fa0e7b1409 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 8b3394f3788e6040490041fcd795681f477369e9 --sources-rev-after 8b3394f3788e6040490041fcd795681f477369e9 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B5-BOM-LINE1-COMMENT-OPENER
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=8b3394f3788e base=0cb71375c933
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/b5_bom_line1_comment_opener --rev 8b3394f3788e6040490041fcd795681f477369e9 --base 0cb71375c9330f7c742fb0073d4e33fa0e7b1409 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 8b3394f3788e6040490041fcd795681f477369e9 --sources-rev-after 8b3394f3788e6040490041fcd795681f477369e9 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/B5-BOM-LINE1-COMMENT-OPENER
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=8b3394f3788e base=0cb71375c933
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=8b3394f3788e base=0cb71375c933
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=8b3394f3788e base=0cb71375c933
EXPECTATION-CHECK ok
EXIT=0
```

### C1-FENCE-IN-COMMENT-PAIR-FILING.txt

```text
CASE C1-FENCE-IN-COMMENT-PAIR-FILING
KIND named  CLASS NAMED(tightened)
NOTE pair filing inside a fence inside an HTML comment; overstated LOG.md pair
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/c1_fence_in_comment_pair_filing base=05ef3b0cabb7b910c048f49d5e7f6d446081c7f9 tip=181af2e2ae5bff3e5bebe3add6eef5bf594918c9
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, c1_fence_in_comment_pair_filing)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n<!--\n```text\nR53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3\n```\n-->\n\n'
LOG.md tip bytes (repr):
'# fixture log\n- the r52 note said corpus/SOURCES.md 3 -> 4 rows.\n'
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=1
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c1_fence_in_comment_pair_filing --rev 181af2e2ae5bff3e5bebe3add6eef5bf594918c9 --base 05ef3b0cabb7b910c048f49d5e7f6d446081c7f9 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 181af2e2ae5bff3e5bebe3add6eef5bf594918c9 --sources-rev-after 181af2e2ae5bff3e5bebe3add6eef5bf594918c9 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C1-FENCE-IN-COMMENT-PAIR-FILING
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=181af2e2ae5b base=05ef3b0cabb7
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c1_fence_in_comment_pair_filing --rev 181af2e2ae5bff3e5bebe3add6eef5bf594918c9 --base 05ef3b0cabb7b910c048f49d5e7f6d446081c7f9 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 181af2e2ae5bff3e5bebe3add6eef5bf594918c9 --sources-rev-after 181af2e2ae5bff3e5bebe3add6eef5bf594918c9 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C1-FENCE-IN-COMMENT-PAIR-FILING
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it
FINDING PAIR-FILING-HIDDEN LOG.md:2 matching filing sits in a hidden line (fence or comment); it does not file
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=181af2e2ae5b base=05ef3b0cabb7
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=181af2e2ae5b base=05ef3b0cabb7
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=181af2e2ae5b base=05ef3b0cabb7
EXPECTATION-CHECK ok
EXIT=0
```

### C2-COMMENT-IN-FENCE-PAIR-FILING.txt

```text
CASE C2-COMMENT-IN-FENCE-PAIR-FILING
KIND named  CLASS NAMED(tightened)
NOTE HTML comment inside a fence; pair filing inside that comment; overstated LOG.md pair
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/c2_comment_in_fence_pair_filing base=3f219ab0860e33b94d5d1020cbbf990d78c00ca3 tip=38ecc54b9f257d2535f5f2f83d564769a428cbc4
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, c2_comment_in_fence_pair_filing)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n```text\n<!--\nR53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3\n-->\n```\n\n'
LOG.md tip bytes (repr):
'# fixture log\n- the r52 note said corpus/SOURCES.md 3 -> 4 rows.\n'
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=1 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c2_comment_in_fence_pair_filing --rev 38ecc54b9f257d2535f5f2f83d564769a428cbc4 --base 3f219ab0860e33b94d5d1020cbbf990d78c00ca3 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 38ecc54b9f257d2535f5f2f83d564769a428cbc4 --sources-rev-after 38ecc54b9f257d2535f5f2f83d564769a428cbc4 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C2-COMMENT-IN-FENCE-PAIR-FILING
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=38ecc54b9f25 base=3f219ab0860e
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c2_comment_in_fence_pair_filing --rev 38ecc54b9f257d2535f5f2f83d564769a428cbc4 --base 3f219ab0860e33b94d5d1020cbbf990d78c00ca3 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 38ecc54b9f257d2535f5f2f83d564769a428cbc4 --sources-rev-after 38ecc54b9f257d2535f5f2f83d564769a428cbc4 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C2-COMMENT-IN-FENCE-PAIR-FILING
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it
FINDING PAIR-FILING-HIDDEN LOG.md:2 matching filing sits in a hidden line (fence or comment); it does not file
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=38ecc54b9f25 base=3f219ab0860e
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=38ecc54b9f25 base=3f219ab0860e
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=38ecc54b9f25 base=3f219ab0860e
EXPECTATION-CHECK ok
EXIT=0
```

### C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED.txt

```text
CASE C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED
KIND named  CLASS NAMED(tightened)
NOTE comment closes, then a fence opens and never closes; pair filing inside it
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/c3_fence_opened_after_comment_unclosed base=8bdaf1daf45aa19245672345e86b8fe394ddb784 tip=803ce1f16928974d4c2f81a0b7ac9b608272a823
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, c3_fence_opened_after_comment_unclosed)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n<!--\n```\n-->\n```text\nR53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3\n\n'
LOG.md tip bytes (repr):
'# fixture log\n- the r52 note said corpus/SOURCES.md 3 -> 4 rows.\n'
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=1 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c3_fence_opened_after_comment_unclosed --rev 803ce1f16928974d4c2f81a0b7ac9b608272a823 --base 8bdaf1daf45aa19245672345e86b8fe394ddb784 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 803ce1f16928974d4c2f81a0b7ac9b608272a823 --sources-rev-after 803ce1f16928974d4c2f81a0b7ac9b608272a823 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=803ce1f16928 base=8bdaf1daf45a
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c3_fence_opened_after_comment_unclosed --rev 803ce1f16928974d4c2f81a0b7ac9b608272a823 --base 8bdaf1daf45aa19245672345e86b8fe394ddb784 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 803ce1f16928974d4c2f81a0b7ac9b608272a823 --sources-rev-after 803ce1f16928974d4c2f81a0b7ac9b608272a823 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it
FINDING PAIR-FILING-HIDDEN LOG.md:2 matching filing sits in a hidden line (fence or comment); it does not file
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=803ce1f16928 base=8bdaf1daf45a
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=803ce1f16928 base=8bdaf1daf45a
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=803ce1f16928 base=8bdaf1daf45a
EXPECTATION-CHECK ok
EXIT=0
```

### C4-INLINE-COMMENT-SPANS-CORRECTIONS.txt

```text
CASE C4-INLINE-COMMENT-SPANS-CORRECTIONS
KIND harm  CLASS HARM
NOTE prose `<!--` mid-line (F29 family) opens a CommonMark inline comment that spans the honest SCORECARD filings
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/c4_inline_comment_spans_corrections base=a6291a8fd549aeecee0e599886c304f3c7255cdf tip=7e2038fe525137b1b8083206e63593b0e721380a
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, c4_inline_comment_spans_corrections)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nNote: prose opens an inline comment <!-- here\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\nand it closes here --> now.\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=0 hidden_comment=2; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c4_inline_comment_spans_corrections --rev 7e2038fe525137b1b8083206e63593b0e721380a --base a6291a8fd549aeecee0e599886c304f3c7255cdf --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 7e2038fe525137b1b8083206e63593b0e721380a --sources-rev-after 7e2038fe525137b1b8083206e63593b0e721380a --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C4-INLINE-COMMENT-SPANS-CORRECTIONS
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5)
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3)
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=7e2038fe5251 base=a6291a8fd549
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c4_inline_comment_spans_corrections --rev 7e2038fe525137b1b8083206e63593b0e721380a --base a6291a8fd549aeecee0e599886c304f3c7255cdf --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 7e2038fe525137b1b8083206e63593b0e721380a --sources-rev-after 7e2038fe525137b1b8083206e63593b0e721380a --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C4-INLINE-COMMENT-SPANS-CORRECTIONS
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=7e2038fe5251 base=a6291a8fd549
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=7e2038fe5251 base=a6291a8fd549
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=7e2038fe5251 base=a6291a8fd549
EXPECTATION-CHECK ok
EXIT=0
```

### C5-INLINE-COMMENT-HIDES-PAIR-LOG.txt

```text
CASE C5-INLINE-COMMENT-HIDES-PAIR-LOG
KIND named  CLASS NAMED(tightened)
NOTE mid-line inline comment in LOG.md hides an overstated pair line (v4 skips it, v5 scans it)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/c5_inline_comment_hides_pair_log base=7a87c4823d9b8852db8fcaadb021bc8d88689b6a tip=35ced56010ab99e2b0cf954b5081896778e23124
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, c5_inline_comment_hides_pair_log)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
'# fixture log\nsee <!-- here\n- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.\n--> closes\n'
CM (markdown-it-py 4.2.0 commonmark): corpus/SOURCES.md para=1 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c5_inline_comment_hides_pair_log --rev 35ced56010ab99e2b0cf954b5081896778e23124 --base 7a87c4823d9b8852db8fcaadb021bc8d88689b6a --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 35ced56010ab99e2b0cf954b5081896778e23124 --sources-rev-after 35ced56010ab99e2b0cf954b5081896778e23124 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C5-INLINE-COMMENT-HIDES-PAIR-LOG
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=35ced56010ab base=7a87c4823d9b
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/c5_inline_comment_hides_pair_log --rev 35ced56010ab99e2b0cf954b5081896778e23124 --base 7a87c4823d9b8852db8fcaadb021bc8d88689b6a --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 35ced56010ab99e2b0cf954b5081896778e23124 --sources-rev-after 35ced56010ab99e2b0cf954b5081896778e23124 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/C5-INLINE-COMMENT-HIDES-PAIR-LOG
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:3 claims 999 -> 1000 rows but the registry holds 3; no pair-form filing names it
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=35ced56010ab base=7a87c4823d9b
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=35ced56010ab base=7a87c4823d9b
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=35ced56010ab base=7a87c4823d9b
EXPECTATION-CHECK ok
EXIT=0
```

### CTRL-DEFAULT-HONEST.txt

```text
CASE CTRL-DEFAULT-HONEST
KIND ctrl  CLASS PASS-BOTH
NOTE frozen F1 layout, honest visible filings
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/ctrl_default_honest base=2984704c370b5d7cd6fa5401ccfa2c6d05eb3711 tip=aff8dcf28b97d65d072a9987c20599756d965081
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, ctrl_default_honest)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/ctrl_default_honest --rev aff8dcf28b97d65d072a9987c20599756d965081 --base 2984704c370b5d7cd6fa5401ccfa2c6d05eb3711 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before aff8dcf28b97d65d072a9987c20599756d965081 --sources-rev-after aff8dcf28b97d65d072a9987c20599756d965081 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/CTRL-DEFAULT-HONEST
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=aff8dcf28b97 base=2984704c370b
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/ctrl_default_honest --rev aff8dcf28b97d65d072a9987c20599756d965081 --base 2984704c370b5d7cd6fa5401ccfa2c6d05eb3711 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before aff8dcf28b97d65d072a9987c20599756d965081 --sources-rev-after aff8dcf28b97d65d072a9987c20599756d965081 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/CTRL-DEFAULT-HONEST
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=aff8dcf28b97 base=2984704c370b
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=aff8dcf28b97 base=2984704c370b
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=aff8dcf28b97 base=2984704c370b
EXPECTATION-CHECK ok
EXIT=0
```

### D1-VT-CLOSER-FENCE.txt

```text
CASE D1-VT-CLOSER-FENCE
KIND limit  CLASS LIMIT
NOTE closing run followed by vertical tab; CommonMark keeps the fence open, v4 and v5 close it
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/d1_vt_closer_fence base=c9f2cc02adc13ebdd9b03b2e0bbda49621ed91a7 tip=de9a18c8455d880a7a79cb9755a028cb87c84b84
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, d1_vt_closer_fence)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n```text\nsample\n```\x0b\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d1_vt_closer_fence --rev de9a18c8455d880a7a79cb9755a028cb87c84b84 --base c9f2cc02adc13ebdd9b03b2e0bbda49621ed91a7 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before de9a18c8455d880a7a79cb9755a028cb87c84b84 --sources-rev-after de9a18c8455d880a7a79cb9755a028cb87c84b84 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D1-VT-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=de9a18c8455d base=c9f2cc02adc1
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d1_vt_closer_fence --rev de9a18c8455d880a7a79cb9755a028cb87c84b84 --base c9f2cc02adc13ebdd9b03b2e0bbda49621ed91a7 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before de9a18c8455d880a7a79cb9755a028cb87c84b84 --sources-rev-after de9a18c8455d880a7a79cb9755a028cb87c84b84 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D1-VT-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=de9a18c8455d base=c9f2cc02adc1
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=de9a18c8455d base=c9f2cc02adc1
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=de9a18c8455d base=c9f2cc02adc1
EXPECTATION-CHECK ok
EXIT=0
```

### D2-FF-CLOSER-FENCE.txt

```text
CASE D2-FF-CLOSER-FENCE
KIND limit  CLASS LIMIT
NOTE closing run followed by form feed
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/d2_ff_closer_fence base=992ea20dc3edf26e10b6b29db7b404bb03697a6a tip=f29e3098897b0cdf9ea28e2097c53e01a8864842
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, d2_ff_closer_fence)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n```text\nsample\n```\x0c\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d2_ff_closer_fence --rev f29e3098897b0cdf9ea28e2097c53e01a8864842 --base 992ea20dc3edf26e10b6b29db7b404bb03697a6a --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before f29e3098897b0cdf9ea28e2097c53e01a8864842 --sources-rev-after f29e3098897b0cdf9ea28e2097c53e01a8864842 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D2-FF-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=f29e3098897b base=992ea20dc3ed
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d2_ff_closer_fence --rev f29e3098897b0cdf9ea28e2097c53e01a8864842 --base 992ea20dc3edf26e10b6b29db7b404bb03697a6a --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before f29e3098897b0cdf9ea28e2097c53e01a8864842 --sources-rev-after f29e3098897b0cdf9ea28e2097c53e01a8864842 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D2-FF-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f29e3098897b base=992ea20dc3ed
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=f29e3098897b base=992ea20dc3ed
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f29e3098897b base=992ea20dc3ed
EXPECTATION-CHECK ok
EXIT=0
```

### D3-NEL-CLOSER-FENCE.txt

```text
CASE D3-NEL-CLOSER-FENCE
KIND limit  CLASS LIMIT
NOTE closing run followed by NEL (U+0085)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/d3_nel_closer_fence base=b950a52eebaec39a95ae7760249804eaa485301a tip=8873387daffa03681af3990823c0a54cb773a779
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, d3_nel_closer_fence)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n```text\nsample\n```\x85\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d3_nel_closer_fence --rev 8873387daffa03681af3990823c0a54cb773a779 --base b950a52eebaec39a95ae7760249804eaa485301a --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 8873387daffa03681af3990823c0a54cb773a779 --sources-rev-after 8873387daffa03681af3990823c0a54cb773a779 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D3-NEL-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=8873387daffa base=b950a52eebae
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d3_nel_closer_fence --rev 8873387daffa03681af3990823c0a54cb773a779 --base b950a52eebaec39a95ae7760249804eaa485301a --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 8873387daffa03681af3990823c0a54cb773a779 --sources-rev-after 8873387daffa03681af3990823c0a54cb773a779 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D3-NEL-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=8873387daffa base=b950a52eebae
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=8873387daffa base=b950a52eebae
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=8873387daffa base=b950a52eebae
EXPECTATION-CHECK ok
EXIT=0
```

### D4-LS-CLOSER-FENCE.txt

```text
CASE D4-LS-CLOSER-FENCE
KIND limit  CLASS LIMIT
NOTE closing run followed by U+2028
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/d4_ls_closer_fence base=a1a78e61c846d979ebad1fce5dbcb3d52cee85f5 tip=f392be01547753551e4b645ae9939d0e7d66863c
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, d4_ls_closer_fence)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n```text\nsample\n```\u2028\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d4_ls_closer_fence --rev f392be01547753551e4b645ae9939d0e7d66863c --base a1a78e61c846d979ebad1fce5dbcb3d52cee85f5 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before f392be01547753551e4b645ae9939d0e7d66863c --sources-rev-after f392be01547753551e4b645ae9939d0e7d66863c --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D4-LS-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=f392be015477 base=a1a78e61c846
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d4_ls_closer_fence --rev f392be01547753551e4b645ae9939d0e7d66863c --base a1a78e61c846d979ebad1fce5dbcb3d52cee85f5 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before f392be01547753551e4b645ae9939d0e7d66863c --sources-rev-after f392be01547753551e4b645ae9939d0e7d66863c --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D4-LS-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f392be015477 base=a1a78e61c846
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=f392be015477 base=a1a78e61c846
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f392be015477 base=a1a78e61c846
EXPECTATION-CHECK ok
EXIT=0
```

### D5-TILDE-VT-CLOSER-FENCE.txt

```text
CASE D5-TILDE-VT-CLOSER-FENCE
KIND limit  CLASS LIMIT
NOTE tilde fence closed by a run followed by vertical tab
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/d5_tilde_vt_closer_fence base=a315f81a03bed52c136ef7a50a27893aab413ae6 tip=5a66618b9cebb523c98e718b43535a53cef0dcba
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, d5_tilde_vt_closer_fence)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n~~~\nsample\n~~~\x0b\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d5_tilde_vt_closer_fence --rev 5a66618b9cebb523c98e718b43535a53cef0dcba --base a315f81a03bed52c136ef7a50a27893aab413ae6 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 5a66618b9cebb523c98e718b43535a53cef0dcba --sources-rev-after 5a66618b9cebb523c98e718b43535a53cef0dcba --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D5-TILDE-VT-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=5a66618b9ceb base=a315f81a03be
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d5_tilde_vt_closer_fence --rev 5a66618b9cebb523c98e718b43535a53cef0dcba --base a315f81a03bed52c136ef7a50a27893aab413ae6 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 5a66618b9cebb523c98e718b43535a53cef0dcba --sources-rev-after 5a66618b9cebb523c98e718b43535a53cef0dcba --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D5-TILDE-VT-CLOSER-FENCE
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=5a66618b9ceb base=a315f81a03be
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=5a66618b9ceb base=a315f81a03be
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=5a66618b9ceb base=a315f81a03be
EXPECTATION-CHECK ok
EXIT=0
```

### D6-TAB-CLOSER-FENCE-CONTROL.txt

```text
CASE D6-TAB-CLOSER-FENCE-CONTROL
KIND ctrl  CLASS PASS-BOTH
NOTE closing run followed by a tab (CommonMark-legal closer)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/d6_tab_closer_fence_control base=8316a5a0ccd6d0f51440b87328f2938e0f89d355 tip=7287c908bd0766e6d2a97ac981792686521609bc
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, d6_tab_closer_fence_control)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\n```text\nsample\n```\t\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d6_tab_closer_fence_control --rev 7287c908bd0766e6d2a97ac981792686521609bc --base 8316a5a0ccd6d0f51440b87328f2938e0f89d355 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 7287c908bd0766e6d2a97ac981792686521609bc --sources-rev-after 7287c908bd0766e6d2a97ac981792686521609bc --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D6-TAB-CLOSER-FENCE-CONTROL
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=7287c908bd07 base=8316a5a0ccd6
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/d6_tab_closer_fence_control --rev 7287c908bd0766e6d2a97ac981792686521609bc --base 8316a5a0ccd6d0f51440b87328f2938e0f89d355 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 7287c908bd0766e6d2a97ac981792686521609bc --sources-rev-after 7287c908bd0766e6d2a97ac981792686521609bc --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/D6-TAB-CLOSER-FENCE-CONTROL
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=7287c908bd07 base=8316a5a0ccd6
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=7287c908bd07 base=8316a5a0ccd6
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=7287c908bd07 base=8316a5a0ccd6
EXPECTATION-CHECK ok
EXIT=0
```

### E1-NUL-BOGUS-LINE-HONEST-DEFAULT.txt

```text
CASE E1-NUL-BOGUS-LINE-HONEST-DEFAULT
KIND named  CLASS NAMED(both-refuse)
NOTE NUL on a bogus correction-looking line; honest default filings present
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/e1_nul_bogus_line_honest_default base=49fa6c754f6c2b7bc56b51da6f02ae448878509c tip=fb881a2657b5c41cc24b5f394af308b196397151
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, e1_nul_bogus_line_honest_default)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=83\x00\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=3 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e1_nul_bogus_line_honest_default --rev fb881a2657b5c41cc24b5f394af308b196397151 --base 49fa6c754f6c2b7bc56b51da6f02ae448878509c --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before fb881a2657b5c41cc24b5f394af308b196397151 --sources-rev-after fb881a2657b5c41cc24b5f394af308b196397151 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E1-NUL-BOGUS-LINE-HONEST-DEFAULT
FINDING DELETED-LINES SCORECARD.md deletions=-1 between 49fa6c754f6c..fb881a2657b5
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=fb881a2657b5 base=49fa6c754f6c
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e1_nul_bogus_line_honest_default --rev fb881a2657b5c41cc24b5f394af308b196397151 --base 49fa6c754f6c2b7bc56b51da6f02ae448878509c --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before fb881a2657b5c41cc24b5f394af308b196397151 --sources-rev-after fb881a2657b5c41cc24b5f394af308b196397151 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E1-NUL-BOGUS-LINE-HONEST-DEFAULT
FINDING CORRECTION-FILE-BINARY SCORECARD.md carries NUL bytes; correction lines cannot be lexed
FINDING DELETIONS-UNREADABLE-BINARY SCORECARD.md deletions unreadable (binary numstat entry) between 49fa6c754f6c..fb881a2657b5
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=fb881a2657b5 base=49fa6c754f6c
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=fb881a2657b5 base=49fa6c754f6c
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=fb881a2657b5 base=49fa6c754f6c
EXPECTATION-CHECK MISMATCH
EXIT=0
```

### E2-NUL-ON-HONEST-SC-FILING.txt

```text
CASE E2-NUL-ON-HONEST-SC-FILING
KIND named  CLASS NAMED(both-refuse)
NOTE NUL on the honest SCORECARD filing line (the filing is unlexable)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/e2_nul_on_honest_sc_filing base=5c82657746ab0a07f496592faaa0a317d3a4caa2 tip=1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, e2_nul_on_honest_sc_filing)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\x00\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e2_nul_on_honest_sc_filing --rev 1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0 --base 5c82657746ab0a07f496592faaa0a317d3a4caa2 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0 --sources-rev-after 1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E2-NUL-ON-HONEST-SC-FILING
FINDING DELETED-LINES SCORECARD.md deletions=-1 between 5c82657746ab..1bbd282dda48
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=1bbd282dda48 base=5c82657746ab
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e2_nul_on_honest_sc_filing --rev 1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0 --base 5c82657746ab0a07f496592faaa0a317d3a4caa2 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0 --sources-rev-after 1bbd282dda48ab50d8cf3ed99ffc5cdf4a1497a0 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E2-NUL-ON-HONEST-SC-FILING
FINDING CORRECTION-FILE-BINARY SCORECARD.md carries NUL bytes; correction lines cannot be lexed
FINDING DELETIONS-UNREADABLE-BINARY SCORECARD.md deletions unreadable (binary numstat entry) between 5c82657746ab..1bbd282dda48
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=1bbd282dda48 base=5c82657746ab
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=1bbd282dda48 base=5c82657746ab
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=1 unfiled=1 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=1bbd282dda48 base=5c82657746ab
EXPECTATION-CHECK ok
EXIT=0
```

### E3-NUL-INSIDE-FENCE-LINE.txt

```text
CASE E3-NUL-INSIDE-FENCE-LINE
KIND named  CLASS NAMED(both-refuse)
NOTE NUL on a line inside a fence (silent under v4)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/e3_nul_inside_fence_line base=ecb94b2879770df6467502adaeb62eed7e4cf2f1 tip=cb00a0a10f0ecd51fc2562438c99c279f0665698
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, e3_nul_inside_fence_line)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n```text\nfiller\x00\n```\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e3_nul_inside_fence_line --rev cb00a0a10f0ecd51fc2562438c99c279f0665698 --base ecb94b2879770df6467502adaeb62eed7e4cf2f1 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before cb00a0a10f0ecd51fc2562438c99c279f0665698 --sources-rev-after cb00a0a10f0ecd51fc2562438c99c279f0665698 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E3-NUL-INSIDE-FENCE-LINE
FINDING DELETED-LINES SCORECARD.md deletions=-1 between ecb94b287977..cb00a0a10f0e
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=cb00a0a10f0e base=ecb94b287977
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e3_nul_inside_fence_line --rev cb00a0a10f0ecd51fc2562438c99c279f0665698 --base ecb94b2879770df6467502adaeb62eed7e4cf2f1 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before cb00a0a10f0ecd51fc2562438c99c279f0665698 --sources-rev-after cb00a0a10f0ecd51fc2562438c99c279f0665698 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E3-NUL-INSIDE-FENCE-LINE
FINDING CORRECTION-FILE-BINARY SCORECARD.md carries NUL bytes; correction lines cannot be lexed
FINDING DELETIONS-UNREADABLE-BINARY SCORECARD.md deletions unreadable (binary numstat entry) between ecb94b287977..cb00a0a10f0e
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=cb00a0a10f0e base=ecb94b287977
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=cb00a0a10f0e base=ecb94b287977
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=cb00a0a10f0e base=ecb94b287977
EXPECTATION-CHECK MISMATCH
EXIT=0
```

### E4-NUL-BEFORE-TOKEN-SAME-LINE.txt

```text
CASE E4-NUL-BEFORE-TOKEN-SAME-LINE
KIND named  CLASS NAMED(both-refuse)
NOTE NUL before a correction-looking token on a bogus line
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/e4_nul_before_token_same_line base=031a403b22cbfa593e915f7b2f0eaf126e3c2a85 tip=0196f7bf28dceb2ec8a21f403d5103a41d8ef01e
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, e4_nul_before_token_same_line)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n\x00R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=83\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): R52-CORRECTION para=3 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e4_nul_before_token_same_line --rev 0196f7bf28dceb2ec8a21f403d5103a41d8ef01e --base 031a403b22cbfa593e915f7b2f0eaf126e3c2a85 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 0196f7bf28dceb2ec8a21f403d5103a41d8ef01e --sources-rev-after 0196f7bf28dceb2ec8a21f403d5103a41d8ef01e --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E4-NUL-BEFORE-TOKEN-SAME-LINE
FINDING DELETED-LINES SCORECARD.md deletions=-1 between 031a403b22cb..0196f7bf28dc
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=0196f7bf28dc base=031a403b22cb
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/e4_nul_before_token_same_line --rev 0196f7bf28dceb2ec8a21f403d5103a41d8ef01e --base 031a403b22cbfa593e915f7b2f0eaf126e3c2a85 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 0196f7bf28dceb2ec8a21f403d5103a41d8ef01e --sources-rev-after 0196f7bf28dceb2ec8a21f403d5103a41d8ef01e --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/E4-NUL-BEFORE-TOKEN-SAME-LINE
FINDING CORRECTION-FILE-BINARY SCORECARD.md carries NUL bytes; correction lines cannot be lexed
FINDING DELETIONS-UNREADABLE-BINARY SCORECARD.md deletions unreadable (binary numstat entry) between 031a403b22cb..0196f7bf28dc
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=0196f7bf28dc base=031a403b22cb
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=0196f7bf28dc base=031a403b22cb
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=0196f7bf28dc base=031a403b22cb
EXPECTATION-CHECK MISMATCH
EXIT=0
```

### F1-NUL-IN-LOG-PAIR-UNCHANGED.txt

```text
CASE F1-NUL-IN-LOG-PAIR-UNCHANGED
KIND limit  CLASS LIMIT
NOTE NUL splits an overstated pair annotation in LOG.md (unchanged base->tip)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/f1_nul_in_log_pair_unchanged base=738b3c5bf7727b0db1b7d1ed3f6d0855772caecf tip=24d86cd6e9eae6e5b500f57f3ab45858a08f70c6
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, f1_nul_in_log_pair_unchanged)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
'# fixture log\n- the r52 note said corpus/SOURCES.md 3\x00 -> 4 rows.\n'
CM (markdown-it-py 4.2.0 commonmark): corpus/SOURCES.md para=1 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f1_nul_in_log_pair_unchanged --rev 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 --base 738b3c5bf7727b0db1b7d1ed3f6d0855772caecf --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 --sources-rev-after 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F1-NUL-IN-LOG-PAIR-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=24d86cd6e9ea base=738b3c5bf772
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f1_nul_in_log_pair_unchanged --rev 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 --base 738b3c5bf7727b0db1b7d1ed3f6d0855772caecf --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 --sources-rev-after 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F1-NUL-IN-LOG-PAIR-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=24d86cd6e9ea base=738b3c5bf772
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=24d86cd6e9ea base=738b3c5bf772
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=24d86cd6e9ea base=738b3c5bf772
EXPECTATION-CHECK ok
EXIT=0
```

### F2-NUL-IN-README-PAIR-UNCHANGED.txt

```text
CASE F2-NUL-IN-README-PAIR-UNCHANGED
KIND limit  CLASS LIMIT
NOTE NUL splits an overstated pair annotation in corpus/README.md (unchanged)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged base=f3294baad924e7291180224e7639ff7c3a0c5c95 tip=2e066e5389d1d44e99e6e8443cb9d74389ebf79b
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, f2_nul_in_readme_pair_unchanged)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): n/a
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged --rev 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --base f3294baad924e7291180224e7639ff7c3a0c5c95 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --sources-rev-after 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F2-NUL-IN-README-PAIR-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged --rev 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --base f3294baad924e7291180224e7639ff7c3a0c5c95 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --sources-rev-after 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F2-NUL-IN-README-PAIR-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
EXPECTATION-CHECK ok
EXIT=0
```

### F3-NUL-IN-PATH-TOKEN-UNCHANGED.txt

```text
CASE F3-NUL-IN-PATH-TOKEN-UNCHANGED
KIND limit  CLASS LIMIT
NOTE NUL inside the path token of an overstated LOG.md pair (unchanged)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/f3_nul_in_path_token_unchanged base=34581d4581f08c1267214780f189c5f414f92c7f tip=05f93c5cf6369059ac8683a1bca87d012e6d74f2
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, f3_nul_in_path_token_unchanged)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
'# fixture log\n- the r52 note said corpus/SOURCES\x00.md 3 -> 4 rows.\n'
CM (markdown-it-py 4.2.0 commonmark): corpus/SOURCES.md para=0 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f3_nul_in_path_token_unchanged --rev 05f93c5cf6369059ac8683a1bca87d012e6d74f2 --base 34581d4581f08c1267214780f189c5f414f92c7f --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 05f93c5cf6369059ac8683a1bca87d012e6d74f2 --sources-rev-after 05f93c5cf6369059ac8683a1bca87d012e6d74f2 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F3-NUL-IN-PATH-TOKEN-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=05f93c5cf636 base=34581d4581f0
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f3_nul_in_path_token_unchanged --rev 05f93c5cf6369059ac8683a1bca87d012e6d74f2 --base 34581d4581f08c1267214780f189c5f414f92c7f --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 05f93c5cf6369059ac8683a1bca87d012e6d74f2 --sources-rev-after 05f93c5cf6369059ac8683a1bca87d012e6d74f2 --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F3-NUL-IN-PATH-TOKEN-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=05f93c5cf636 base=34581d4581f0
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=05f93c5cf636 base=34581d4581f0
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=05f93c5cf636 base=34581d4581f0
EXPECTATION-CHECK ok
EXIT=0
```

### F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL.txt

```text
CASE F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL
KIND named  CLASS NAMED(both-refuse)
NOTE control: the same overstated pair, no NUL, LOG.md unchanged
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/f4_control_log_pair_unchanged_no_nul base=790a4512808d76581ea64948bd03dd2110fcac9e tip=350452c8cdc9a55a166b1bcfbcd4e5570297718f
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, f4_control_log_pair_unchanged_no_nul)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
'# fixture log\n- the r52 note said corpus/SOURCES.md 3 -> 4 rows.\n'
CM (markdown-it-py 4.2.0 commonmark): corpus/SOURCES.md para=1 code=0 hidden_comment=0
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f4_control_log_pair_unchanged_no_nul --rev 350452c8cdc9a55a166b1bcfbcd4e5570297718f --base 790a4512808d76581ea64948bd03dd2110fcac9e --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 350452c8cdc9a55a166b1bcfbcd4e5570297718f --sources-rev-after 350452c8cdc9a55a166b1bcfbcd4e5570297718f --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=350452c8cdc9 base=790a4512808d
EXIT=1
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f4_control_log_pair_unchanged_no_nul --rev 350452c8cdc9a55a166b1bcfbcd4e5570297718f --base 790a4512808d76581ea64948bd03dd2110fcac9e --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 350452c8cdc9a55a166b1bcfbcd4e5570297718f --sources-rev-after 350452c8cdc9a55a166b1bcfbcd4e5570297718f --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=350452c8cdc9 base=790a4512808d
EXIT=1
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=350452c8cdc9 base=790a4512808d
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=350452c8cdc9 base=790a4512808d
EXPECTATION-CHECK ok
EXIT=0
```

### committed-pins.txt

```text
CMD: git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cce21b555a617cadda782613ec1e9d3a0c12ac83:<each listed path> | sha256sum
975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179  census/round-56/c1-counter.py (git-show EXIT=0)
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8  census/round-56/c2-counter.py (git-show EXIT=0)
2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a  census/round-56/fixtures/build-fixtures.py (git-show EXIT=0)
a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3  census/round-56/fixtures/run-matrix.sh (git-show EXIT=0)
48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb  census/round-56/records/c1-selftest-expected.tsv (git-show EXIT=0)
90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3  census/round-56/records/c2-selftest-expected.tsv (git-show EXIT=0)
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py (git-show EXIT=0)
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py (git-show EXIT=0)
All match assignment pins.
EXIT=0
```

### parser-version.txt

```text
INSTALL: uv venv -q <scratch>/venv; uv pip install --python <scratch>/venv/bin/python markdown-it-py
CHANNEL: official PyPI via uv 0.13.0; scratch venv only; reason: CommonMark visibility evidence.
markdown-it-py=4.2.0
mdurl=0.1.2
EXIT=0
EXIT=0
```

### unchanged-pair-sites.txt

```text
CMD: git -C /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f1_nul_in_log_pair_unchanged diff --numstat 738b3c5bf7727b0db1b7d1ed3f6d0855772caecf 24d86cd6e9eae6e5b500f57f3ab45858a08f70c6 -- LOG.md

EXIT=0
Exact LOG.md bytes: b'# fixture log\n- the r52 note said corpus/SOURCES.md 3\x00 -> 4 rows.\n'
CMD: git -C /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged diff --numstat f3294baad924e7291180224e7639ff7c3a0c5c95 2e066e5389d1d44e99e6e8443cb9d74389ebf79b -- corpus/README.md

EXIT=0
Exact corpus/README.md bytes: b'# corpus readme\n- the r52 note said corpus/SOURCES.md 3\x00 -> 4 rows.\n'
CMD: git -C /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f3_nul_in_path_token_unchanged diff --numstat 34581d4581f08c1267214780f189c5f414f92c7f 05f93c5cf6369059ac8683a1bca87d012e6d74f2 -- LOG.md

EXIT=0
Exact LOG.md bytes: b'# fixture log\n- the r52 note said corpus/SOURCES\x00.md 3 -> 4 rows.\n'
No pair-site numstat output in all three cases: file unchanged.
EXIT=0
```

### attack-table.tsv

```text
case	kind	v4_rc	v4_first	v5_rc	v5_first	class	expect	note	cm_reading
CTRL-DEFAULT-HONEST	ctrl	0	-	0	-	PASS-BOTH	exp-ok	frozen F1 layout, honest visible filings	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
A1-ONELINE2-HIDDEN-THEN-HONEST	named	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	NAMED(both-refuse)	exp-ok	two-space `<!--` one-line comment carries a correction; honest filing on next line	R52-CORRECTION para=2 code=0 hidden_comment=1; R53-CORRECTION para=0 code=0 hidden_comment=0
A1b-ONELINE1-ONLY	named	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	NAMED(both-refuse)	exp-ok	one-space `<!--` one-line comment is the only SCORECARD filing	R52-CORRECTION para=1 code=0 hidden_comment=1; R53-CORRECTION para=0 code=0 hidden_comment=0
A1c-ONELINE3-TRAILING-TEXT	named	1	-	1	-	NAMED(both-refuse)	EXPECT-MISMATCH	three-space one-line comment, text after the closer, sole SCORECARD filing	R52-CORRECTION para=1 code=0 hidden_comment=1; R53-CORRECTION para=0 code=0 hidden_comment=0
A2-MULTILINE-COMMENT-HONEST	named	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	NAMED(both-refuse)	exp-ok	multi-line comment opened at 2 spaces wraps honest SCORECARD filings	R52-CORRECTION para=0 code=0 hidden_comment=2; R53-CORRECTION para=0 code=0 hidden_comment=0
B1-TAB-OPENER-HIDES-PAIR-LOG	named	0	-	1	UNFILED-SOURCES-ANNOTATION	NAMED(tightened)	exp-ok	tab-indented `<!--` in LOG.md hides an overstated pair line (v4 skips it)	corpus/SOURCES.md para=1 code=0 hidden_comment=0
B2-TAB-OPENER-HIDES-CORRECTION	harm	1	CORRECTION-IN-FENCE	0	-	HARM	exp-ok	tab-indented `<!--` opens a region in v4 that hides honest SCORECARD filings	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
B3-FOUR-SPACE-OPENER-HIDES-CORRECTION	harm	1	CORRECTION-IN-FENCE	0	-	HARM	exp-ok	four-space `<!--` (S2 class, deliberate repair) hides honest filings in v4	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION	harm	1	CORRECTION-IN-FENCE	0	-	HARM	exp-ok	NBSP before `<!--` is not indentation: v5 sees no opener; CommonMark reads an inline comment	R52-CORRECTION para=0 code=0 hidden_comment=2; R53-CORRECTION para=0 code=0 hidden_comment=0
B5-BOM-LINE1-COMMENT-OPENER	harm	1	CORRECTION-IN-FENCE	0	-	HARM	exp-ok	UTF-8 BOM at byte 0 precedes a `<!--` opener on line 1 (comment spans the tail)	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
C1-FENCE-IN-COMMENT-PAIR-FILING	named	0	-	1	UNFILED-SOURCES-ANNOTATION	NAMED(tightened)	exp-ok	pair filing inside a fence inside an HTML comment; overstated LOG.md pair	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=1
C2-COMMENT-IN-FENCE-PAIR-FILING	named	0	-	1	UNFILED-SOURCES-ANNOTATION	NAMED(tightened)	exp-ok	HTML comment inside a fence; pair filing inside that comment; overstated LOG.md pair	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=1 hidden_comment=0
C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED	named	0	-	1	UNFILED-SOURCES-ANNOTATION	NAMED(tightened)	exp-ok	comment closes, then a fence opens and never closes; pair filing inside it	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=1 hidden_comment=0
C4-INLINE-COMMENT-SPANS-CORRECTIONS	harm	1	CORRECTION-IN-FENCE	0	-	HARM	exp-ok	prose `<!--` mid-line (F29 family) opens a CommonMark inline comment that spans the honest SCORECARD filings	R52-CORRECTION para=0 code=0 hidden_comment=2; R53-CORRECTION para=0 code=0 hidden_comment=0
C5-INLINE-COMMENT-HIDES-PAIR-LOG	named	0	-	1	UNFILED-SOURCES-ANNOTATION	NAMED(tightened)	exp-ok	mid-line inline comment in LOG.md hides an overstated pair line (v4 skips it, v5 scans it)	corpus/SOURCES.md para=1 code=0 hidden_comment=0
D1-VT-CLOSER-FENCE	limit	0	-	0	-	LIMIT	exp-ok	closing run followed by vertical tab; CommonMark keeps the fence open, v4 and v5 close it	R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
D2-FF-CLOSER-FENCE	limit	0	-	0	-	LIMIT	exp-ok	closing run followed by form feed	R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
D3-NEL-CLOSER-FENCE	limit	0	-	0	-	LIMIT	exp-ok	closing run followed by NEL (U+0085)	R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
D4-LS-CLOSER-FENCE	limit	0	-	0	-	LIMIT	exp-ok	closing run followed by U+2028	R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
D5-TILDE-VT-CLOSER-FENCE	limit	0	-	0	-	LIMIT	exp-ok	tilde fence closed by a run followed by vertical tab	R52-CORRECTION para=0 code=2 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
D6-TAB-CLOSER-FENCE-CONTROL	ctrl	0	-	0	-	PASS-BOTH	exp-ok	closing run followed by a tab (CommonMark-legal closer)	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
E1-NUL-BOGUS-LINE-HONEST-DEFAULT	named	1	DELETED-LINES	1	CORRECTION-FILE-BINARY	NAMED(both-refuse)	EXPECT-MISMATCH	NUL on a bogus correction-looking line; honest default filings present	R52-CORRECTION para=3 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
E2-NUL-ON-HONEST-SC-FILING	named	1	DELETED-LINES	1	CORRECTION-FILE-BINARY	NAMED(both-refuse)	exp-ok	NUL on the honest SCORECARD filing line (the filing is unlexable)	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
E3-NUL-INSIDE-FENCE-LINE	named	1	DELETED-LINES	1	CORRECTION-FILE-BINARY	NAMED(both-refuse)	EXPECT-MISMATCH	NUL on a line inside a fence (silent under v4)	R52-CORRECTION para=2 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
E4-NUL-BEFORE-TOKEN-SAME-LINE	named	1	DELETED-LINES	1	CORRECTION-FILE-BINARY	NAMED(both-refuse)	EXPECT-MISMATCH	NUL before a correction-looking token on a bogus line	R52-CORRECTION para=3 code=0 hidden_comment=0; R53-CORRECTION para=0 code=0 hidden_comment=0
F1-NUL-IN-LOG-PAIR-UNCHANGED	limit	0	-	0	-	LIMIT	exp-ok	NUL splits an overstated pair annotation in LOG.md (unchanged base->tip)	corpus/SOURCES.md para=1 code=0 hidden_comment=0
F2-NUL-IN-README-PAIR-UNCHANGED	limit	0	-	0	-	LIMIT	exp-ok	NUL splits an overstated pair annotation in corpus/README.md (unchanged)	n/a
F3-NUL-IN-PATH-TOKEN-UNCHANGED	limit	0	-	0	-	LIMIT	exp-ok	NUL inside the path token of an overstated LOG.md pair (unchanged)	corpus/SOURCES.md para=0 code=0 hidden_comment=0
F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL	named	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	NAMED(both-refuse)	exp-ok	control: the same overstated pair, no NUL, LOG.md unchanged	corpus/SOURCES.md para=1 code=0 hidden_comment=0

EXIT=0
```

### committed-control-matrix.tsv

```text
name	v4_rc	v4_first	v5_rc	v5_first	frozen_rc	frozen_finding	v5_vs_frozen
F1-HONEST-TIP	0	-	0	-	0	-	pass
F2-MULTI-ANNOT	1	MULTIPLE-ANNOTATIONS	1	MULTIPLE-ANNOTATIONS	1	MULTIPLE-ANNOTATIONS	pass
F3-INERT	1	INERT-CORRECTION	1	INERT-CORRECTION	1	INERT-CORRECTION	pass
F4-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F5-REWRITE	1	DELETED-LINES	1	DELETED-LINES	1	DELETED-LINES	pass
F6-RECORD-DRIFT	1	RECORD-SHA-MISMATCH	1	RECORD-SHA-MISMATCH	1	RECORD-SHA-MISMATCH	pass
F7-TILDE-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F8-BT4-PARITY	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F9-HTML-COMMENT	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F10-STRADDLE	1	ZONE-TOKEN-STRADDLES-EDGE	1	ZONE-TOKEN-STRADDLES-EDGE	1	ZONE-TOKEN-STRADDLES-EDGE	pass
F11-BOGUS-RECOMP	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	pass
F12-LOG-UNFILED	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	pass
F12b-LOG-FILED	0	-	0	-	0	-	pass
F7-FF	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F12c-LOG-POINTER-EXEMPT	0	-	0	-	0	-	pass
F8b-BT4-SHORT-RUN	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F13-DUAL-ANCHOR	1	ANCHOR-ALIAS-MISMATCH	1	ANCHOR-ALIAS-MISMATCH	1	ANCHOR-ALIAS-MISMATCH	pass
F14-PAIR-STALE-FILING	1	PAIR-FILING-INERT	1	PAIR-FILING-INERT	1	PAIR-FILING-INERT	pass
F15-PAIR-NOROWS	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	pass
F16-PAIR-ARROW	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	pass
F17-INDENT4-FENCE	0	-	0	-	0	-	pass
F18-BTINFO-FENCE	0	-	0	-	0	-	pass
F19-PAIR-IN-FENCE	0	-	0	-	0	-	pass
F20-R1-INDENT-SWALLOW	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	pass
F21-R1-ONELINE-SWALLOW	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	pass
F22-PTR-TIMESTAMP	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	pass
F23-SOURCES-RECOMP	1	SOURCES-RECOMPUTE-MISMATCH	1	SOURCES-RECOMPUTE-MISMATCH	1	SOURCES-RECOMPUTE-MISMATCH	pass
F7-FF2	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	pass
F24-PAIR-HIDDEN-FILING	0	-	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	pass
F26-INDENT4-COMMENT-OPENER	0	-	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	pass
F27-BINARY-NUMSTAT	1	DELETED-LINES	1	DELETIONS-UNREADABLE-BINARY	1	DELETIONS-UNREADABLE-BINARY	pass
F28-NUL-CORRECTION-UNCHANGED	0	-	1	CORRECTION-FILE-BINARY	1	CORRECTION-FILE-BINARY	pass
F29-PROSE-COMMENT-MENTION	1	CORRECTION-IN-FENCE	0	-	0	-	pass

EXIT=0
```

EXIT=0
