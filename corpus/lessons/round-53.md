# Round 53 — the annotation and capture counters amended (v2), with the kill-power shown over committed fixtures

Fresh-start reading: not applicable (round 53 of a lane with no streak block). The r52
non-author spot-check (corpus/lessons/round-52-verifier-spotcheck.md, verdict ok/admitted)
routed: item 1 (the counter limits) is this round's C1+C2; item 2 (fleet-side wave
artifacts uncommitted) is routed to the protocol integrator again, unchanged; item 3 (the
two open L0 rulings) stays open and routed around; item 4 (attribution note) is recorded;
item 5 (SHONEN promotion) stays operator-owned.

Claims (frozen in census/round-53/preregistration.txt, freeze 61838b54112354acae5ae0534425f366c14e658c;
base 9bf9234ae4d11c7b31706354302a9e95ad0d1f81):
- C1 calibration 7 (the lowest-scoring axis): the annotation-agreement counter is amended
  (census/round-53/c1-counter.py, v2) to close the five named r52 limits, shown able to
  fail over six committed fixtures; the frozen v1 counter is the do-nothing control arm.
- C2 coverage 8: the capture counter is amended (census/round-53/c2-counter.py, v2) to
  instrument sort order, `#`-leading names and RECEIPT_VERSION=1 run-receipt binding,
  over four committed fixtures plus a fresh committed round-53 capture (commit
  1a53bcabc91d97b1a930abeb0d9d23ffbae19b81).
No exploratory claim. No assimilation (shokuknow's merge/souji package stays held by the
open r46 L0 question on mass id drift). considerthese/: no such directory in this lane
(`ls | grep -ci consider` → 0, checked 2026-11-03).

## Gate

- Admitted: S276 — gitignore(1) manual, PATTERN FORMAT, comment lines.
  URL https://git-scm.com/docs/gitignore; access date 2026-11-03; `curl -sSL` HTTP 200,
  no redirect, 50560 bytes, sha256 8b10cfe3d03aabce47fb5259b00d6ac7071d9c2c034d6b4410cbc2abaa983fcd
  (census/round-53/sources/s276-gitignore-page.html). Located quote, 9 words, section
  "PATTERN FORMAT": "A line starting with # serves as a comment."
  (census/round-53/sources/s276-located-quote.txt; opened live by seat S53scribe01).
  Use is the C2 capture grammar's comment-ambiguity refusal (knowledge entry
  fleet-root-capture-receipt-grammar.md): a capture grammar that defines no escaping
  cannot carry a `#`-leading name, so such a capture is refused fail-closed instead of
  reading the row as a comment and losing the entry silently. The page's own escape
  sentence ("Put a backslash … in front of the first hash", 17 words, also verified a
  substring of the same capture) is the contrast that grounds the refusal.
- Admitted (knowledge): corpus/knowledge/fleet-root-capture-receipt-grammar.md, source
  S276; provenance trio first (source / verified-at 2026-11-03 / recheck = the v2 counter
  command); the RECEIPT_VERSION=1 grammar, the three v2 checks, the gitignore grounding,
  and the named limits (including the measured `#`-shape residual).
- Rejected this round: none. Reject sample: the round opened exactly one page (S276). No
  candidate was screened and rejected, because none beyond S276 was opened (sweep
  honesty; the same shape as r52).
- Status changes old→new: S276 drafted `queued` (seat draft) → landed `mined` (the entry
  it cites lands in the same commit). No existing row's status, recheck or used-by cell
  changed.
- Quote check (independent, L1 re-run on the committed capture):
  `python3 -c "import re,html; raw=open('census/round-53/sources/s276-gitignore-page.html',encoding='utf-8',errors='replace').read(); t=re.sub(r'(?is)<(script|style)\b.*?</\1>',' ',raw); t=re.sub(r'<[^>]+>','',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t); q='A line starting with # serves as a comment.'; print('substring:', q in t); print('words:', len(q.split()))"`
  → `substring: True`, `words: 9`; the escape sentence → `substring: True`, `words: 17`.
- Spot-check result: pending the round's non-author closure (LEARNING.md). The lane does
  not claim it.

## Claim evidence

C1 (calibration). Before (v1 arm, the do-nothing control instrument):
census/round-53/records/c1-matrix-v1.tsv — the frozen v1 counter exits 0 on ALL SIX
fixtures, including the five attack states (F2 multi-annotation, F3 inert, F4 fenced,
F5 in-place rewrite, F6 record drift). After (v2 arm): census/round-53/records/
c1-matrix-v2.tsv — v2 exits 1 with the named finding on each attack (F2
MULTIPLE-ANNOTATIONS, F3 INERT-CORRECTION, F4 CORRECTION-IN-FENCE, F5 DELETED-LINES,
F6 RECORD-SHA-MISMATCH) and exits 0 on the honest fixture F1. Real lane at the content
tip: census/round-53/records/c1-tip.txt (exit 0, unfiled=0, record_sha=ok, appended=ok,
multi=0 inert=0 fenced=0). Do-nothing control: census/round-53/controls/
c1-control-donothing.txt (PRISTINE FAIL C1V2-COUNTER-ABSENT at base; discloses that the
honest state was already green under v2 at base — the r52 filing predates this round;
the claim's work is the instrument's kill-power).

C2 (coverage). Before (v1 arm): census/round-53/records/c2-matrix-v1.tsv — the frozen v1
counter exits 0 on ALL FOUR fixtures, including the three attack captures (FA1 unsorted,
FA2 `#`-leading row struck from ENTRIES/COUNT, FA3 tampered capture). After (v2 arm):
census/round-53/records/c2-matrix-v2.tsv — v2 exits 1 with the named finding on each
attack (FA1 ROWS-UNSORTED, FA2 COMMENT-AMBIGUOUS-NAME, FA3 CAPTURE-RECEIPT-MISMATCH) and
exits 0 on the honest fixture FH. Real capture: census/round-53/records/c2-tip.txt at
1a53bcab (exit 0, receipt=ok sorted=ok). Do-nothing control: census/round-53/controls/
c2-control-donothing.txt (PRISTINE FAIL FLEET-CENSUS-ABSENT at base).

## Wave findings (the 12-seat wave; attacks and what they changed)

Wave shape: one v1 wave, 12 seats (scout ×1, executor ×3, scribe ×1, reviewer ×2, critic
×1, mutation-tester ×1, sentinel ×1, connector ×1, revenger ×1); attack seats 4 of 12
(33%); connectors 1; band 8–16; WAVE-DONE received for all 12; no dead seats. Results:
`.ufo/waves/round-53/w1-results.json` (lane-local wave dir is gitignored; the findings
are copied here). Independent reproduction: executor01 AGREE 12/12 C1 matrix cells;
executor02 PASS on every C2 predicate line.

Routed defects (numbered; each is a named limit of the FROZEN bytes — never an edit —
and routes to the next round's amendment):

- R1 (C1 fence grammar): `CORRECTION-IN-FENCE` recognises only backtick fences; a
  correction inside a `~~~` tilde fence or a 4-backtick outer fence (parity toggle) is
  accepted as a filing (reviewer01 F7/F8; sentinel S2 MEDIUM). HTML comments are a named
  limit (reviewer01 F9).
- R2 (C1 zone edge): the frozen ZONE=32 truncates — a legitimate `(79)` planted at offset
  30 is read as `stated=7` (reviewer01 F2, routed); tokens at offset ≥31 or
  whitespace-padded past the zone are accepted (reviewer01 F1, named limit).
- R3 (C1 inert coverage): a correction's `recomputed=` value is never validated against
  the record count when the site matches — a bogus recomputed on a matched site is
  accepted silently (reviewer01 F4/F5, routed).
- R4 (C2 `#`-shape): the COMMENT-AMBIGUOUS-NAME matcher `^#\S*(\t\S+){5}$` fires only on
  a `#`-leading row whose name has no whitespace; a name with a space (or a 7-field row)
  is swallowed as a free-form comment and can be made consistent (scribe shape matrix
  census/round-53/sources/s276-comment-shape-matrix.txt; reviewer02 5b/5d/5e/5f; sentinel
  S1 HIGH). The committed tool can emit such a name (it refuses only tab/newline names).
- R5 (C2 receipt extras): unknown `# KEY=VALUE` receipt keys are accepted (reviewer02
  2e/2f, routed low); a CRLF capture is caught but the finding is unnamed (3a, routed).
- R6 (C2 tool pin): the tool bytes are not pinned by argument — a substituted tool whose
  digest matches the capture header verifies (reviewer02 6a, named limit of the
  committed-bytes trust model; hardening routed: a `--tool-sha256` argument mirroring
  C1's `--record-sha256`).
- R7 (fixture coverage): the receipt-ENTRIES branch (M-F1) and the symlink class branch
  (M-F2) have zero kill-power over the committed fixtures — both kill correctly on
  scratch probes but no committed fixture exercises them (mutation01 8/10 killed,
  2 survivors; executor02 D6 agrees).
- R8 (builder hardening): the builder's `run()` helper has no `timeout=` and its git
  calls omit the `-c core.fsmonitor=false -c core.hooksPath=/dev/null` flags (sentinel
  S3 LOW; no reachable exploit — the builder only targets dirs it just created).
- R9 (oracle pinning): the selftest oracle and builder are working-tree reads/execs with
  no digest pin in the prereg (sentinel S4, named limit of the r52 L2 class).
- R10 (fixture rev determinism): fixture commit ids are wall-clock dependent (no
  GIT_*_DATE pinned); file bytes and verdicts reproduce exactly (executor02 D2).
- R11 (receipt binds bytes, not path): the same capture bytes at a different path verify
  against the unchanged receipt (executor02 D3, named limit).
- R12 (exit-code ambiguity, inherited): an unresolvable 40-hex revision exits 1
  (PRISTINE FAIL) while a malformed short rev exits 2 (executor02 D5; v1 behaves
  identically).
- R13 (wording drifts, critic): the claim titles say "closes the five named limits" /
  "instruments `#`-leading names", but the closures are partial (R1–R4); under the
  prereg's rules these are named limits to route, not kill-rule fires — both claims
  SURVIVE the frozen predicate. The prereg also uses "do-nothing control" for two
  different artifacts (the absent-file control and the v1 arm) — wording defect.

Closed r52 items:

- The `.omp` name-rule dedicated control (r52 Mistakes row 4, "not yet shown able to
  fail") is CLOSED: revenger01's fixture shows the narrowed rule discriminating — a
  tracked `.omp/` directory is accepted (rc 0, tracked row present) while a
  credential-shaped `.env` refuses the run (rc 2, nothing written); the control also
  kills the pre-narrowing bytes. Receipt: wave dir S53revenger01/receipts; the control
  design's own named limit (a single run cannot display both verdicts — the refusal
  precedes row construction) is disclosed.
- Freeze-message discipline (r52 process note): revenger01 verified the r53 freeze
  commit's message against `git show --stat 61838b54` — every named artifact is in the
  commit; PASS.
- Dated observations: scout01's census examined 17 live-claim rows — 12 are expired
  dated observations (prune performed and recorded, subject removed, or a live magnitude
  that moved on), 3 reproduce exactly today, 2 are not re-derivable without another
  round's tool; none is a transcription defect; no correction proposed. The two rows the
  r52 scout raised (LOG.md:18, corpus/README.md:40) reproduce at the r53 tip.
- Connector: no sibling overlap on the three declared surfaces (annotation-agreement
  counters, fleet-root census captures / RECEIPT grammar, append-only correction
  filing); the r52 `ignored`-derivation L0 question remains open and routed around.
- Standing receipts (executor03): r52 c1/c2 counters green at the tip; r51
  routed-corrections and workspace counters green; landing suite
  `assertions=556 mismatches=70 registered=70 corrected=0 exempted=0 unfiled=0` rc 0 on
  a clean clone (its dirty-tree guard refuses a live lane mid-wave — named limit L-N2;
  the L1 re-runs it after integration); NTFS exclusion tolerance not widened (6 at the
  r51 base, 6 at the r53 tip, same bytes).

Defect found after the wave (the L1's own sweep):

- Two r52 annotations state "corpus/SOURCES.md 274 -> 275 rows": LOG.md:2527 (the r52
  entry) and corpus/README.md:870 (the r52 frontier note). The census command
  `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` recomputes 198
  at f778b9d1 and 199 at 9bf9234a (200 with S276 landed this round). The 274/275 figures
  are the last row's S-ids (S274/S275) misread as a row count. Filed as R53-CORRECTION
  lines in SCORECARD.md (append-only; the stale texts stay). The r52 verifier's own grep
  had the right numbers (198→199); the annotations slipped past both the r52 wave and
  the verifier.

Misroot incident (the L1's own, disclosed):

- The round-53 LOG entry was appended twice to the FLEET ROOT's LOG.md (the protocol
  lane's file) by a relative-path `cat >> LOG.md` run from a temporary shell whose cwd
  was the fleet root; the lane's LOG.md was untouched both times. Both times the fleet
  diff showed exactly the 52 appended lines and nothing else, the file was restored from
  HEAD byte-exact (`git show HEAD:LOG.md > LOG.md`; `git status --porcelain -- LOG.md`
  empty after), and the entry then landed in the lane's LOG.md through an absolute-path
  write. Captured-by: the wave context's own rule ("every path you read or write MUST be
  ABSOLUTE") — violated by the L1 itself; fix: absolute paths for every lane write, no
  relative-path redirects; recorded here and in the round report.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| an instrument's kill-power is narrower than its title: the v2 counters' fence check is backtick-only, the `#`-name refusal is no-whitespace-only, a correction's `recomputed=` is never validated, and the zone truncates at offset 30 — each demonstrated by an attack seat on the frozen bytes | reviewer01 F2/F4/F5/F7/F8; reviewer02 5b/5d/5e/5f; sentinel S1/S2; scribe shape matrix; critic NL-C1/NL-C2 | none (the selftest asserted only the six/four committed fixture shapes; the prereg's predicate sentence was implemented narrower than written) | routed to r54 as counter-v3 items (tilde/HTML fences, zone-edge grammar, recomputed validation, `#`-shape widening); the attack receipts are the red-before states a fix must flip |
| the selftest oracle and builder are working-tree reads/execs with no digest pin: editing the oracle or the builder changes what "selftest pass" means without any pin noticing | sentinel S4 (tampered-builder and edited-oracle repros, receipts 06-oracle-builder.txt) | none (the prereg pins the counters and the builder's bytes but the selftest path itself is unpinned) | routed: pin the builder/oracle digests in the next prereg and have the selftest verify them before exec |
| fixture commit ids are wall-clock dependent: the builder pins identity but not GIT_*_DATE, so a rebuild reproduces bytes and verdicts but not the manifest's rev column | executor02 D2 (two rebuilds, different tips, identical bytes/verdicts) | none | routed: pin GIT_AUTHOR_DATE/GIT_COMMITTER_DATE in a future builder version |
| the fixture builder's subprocess helper has no timeout and its git calls omit the counters' `-c` hardening flags | sentinel S3 LOW (code reading + probe) | none (Q4/Q8 govern fixtures' scratch roots and tools' staging, not a builder's git env) | routed: carry the counters' git env + timeout into the builder next time it changes |
| a pasteable count annotation in two r52 records carried S-id numbers as a row count: the r52 LOG entry and the r52 README frontier note say "corpus/SOURCES.md 274 -> 275 rows" where the census command recomputes 198 -> 199 | `git show f778b9d1:corpus/SOURCES.md \| grep -cE ...` → 198; at 9bf9234a → 199; worktree with S276 → 200; LOG.md:2527 and corpus/README.md:870 | none (the r52 scout's dated-observation sweep predated the r52 LOG/README notes and did not sweep them; the r52 verifier recomputed the right numbers but did not file the annotations) | R53-CORRECTION lines filed in SCORECARD.md (append-only; the stale texts stay); the r54 C1 enumeration is the candidate instrument for LOG/README annotations |
| the round's own LOG entry was appended twice to the fleet root's LOG.md (the protocol lane's file) by a relative-path redirect from a temporary shell whose cwd was the fleet root | `git -C <fleet> diff --stat -- LOG.md` → 52 insertions (twice); restored from HEAD byte-exact both times; the entry landed in the lane's LOG.md via an absolute-path write | the wave context's own rule ("every path you read or write MUST be ABSOLUTE") — violated by the L1 | absolute paths for every lane write; no relative-path redirects; disclosed in the lesson and the report |
| the first do-nothing-control design for C1 was green, not red: running v2 at the base revision exits 0 because the r52 corrections already existed there — the control was redesigned (absent-instrument receipt + the v1 arm) before the freeze | the green run is recorded in census/round-53/controls/c1-control-donothing.txt (disclosed inside) | §9 (a control that meets the target means the counter or target is wrong — the rule fired correctly) | the committed control names both artifacts and why each is the control; no further action |

## Named limits carried into r54 (consolidated)

R1–R13 above, plus the standing holds: certification OFF, K5 HELD, NAMESPACE/reap holds,
execution-audit attribution open; the two open L0 rulings (credential-shaped names
refuse-vs-redact; `ignored`-column derivation) and the r46 mass-id-drift L0 (assimilation
held); the fleet-side wave-artifact commit duty (routed to the protocol integrator).
