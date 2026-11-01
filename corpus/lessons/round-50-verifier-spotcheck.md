author: hyaku closure (non-author integrator, zcode subagent (fresh session, non-author))

# souji round 50 — non-author verifier spot-check (closure)

Verifier: hyaku closure judge, fresh session, did not author this round. Every
command below was run by the verifier at closure time (2026-11-01, UTC) against
the committed bytes. Lane repo:
`C:/Users/jpvei/.zcode/workspace/95b1ba4d-5089-47a4-9fd8-54adebbce2ae/fleet/shokunin-repo-hygiene`
(branch `master`). Range under review: `5f921fe261770b68266793c767d35a56758536c5`
.. `6683497581f7423495f833c8795d5d93d4cad3e3`. All git reads were index-free
(`rev-parse`, `cat-file`, `ls-tree`, `diff-tree`, `merge-base --is-ancestor`,
`show`, `log`, `ls-remote`); no mutating git command ran anywhere.

## 1. Conformance (step 1)

| check | command (abridged) | observed | result |
|---|---|---|---|
| report committed by lane identity | `git -C <fleet> log --format='%an <%ae> %H' -1 -- .ufo/reports/round-50/souji.md` | `souji-shokunin <souji@shokunin.local> 2440a2dabb8189820384b4dc869f3f23d48d60ed round-50: souji report (hyaku zcode run 14)` | PASS |
| SHONEN heading in committed report | `git -C <fleet> show HEAD:.ufo/reports/round-50/souji.md` | `## SHONEN` at line 261 with four `[~]` box lines (263/267/271/276) | PASS |
| cited commits exist | `rev-parse --verify <h>^{commit}` for 3cc69c45…, 6d94929f…, 6683497581f7…, 5f921fe2… | all four exist | PASS |
| cited commits are ancestors of master | `merge-base --is-ancestor <h> refs/heads/master` | all four: yes | PASS |
| linear ordering | `rev-parse <c>^` | 6d94929^ = 3cc69c4; 6683497^ = 6d94929; freeze^ = 5f921fe2 (the stated round base) | PASS |
| lane tip pushed | `rev-parse refs/heads/master` vs `ls-remote origin refs/heads/master` | both `6683497581f7423495f833c8795d5d93d4cad3e3` | PASS |
| range authorship | `log --format='%an <%ae> %s' 5f921fe2..6683497` | exactly 3 commits, all `souji-shokunin <souji@shokunin.local>` (freeze / content / end receipts) | PASS |
| cited work reachable in range | `diff-tree -r --name-status 5f921fe2 6683497` | every path the report's "Landed changes" table names appears in the range (freeze: prereg+counters+arms+fixtures+controls+pre-flight receipts+source captures; content: both tools, lesson, SOURCES, SCORECARD, LOG, SKILL; end: tip receipts + census-after + freeze-check + NTFS tip) | PASS |
| PROVINCE.md untouched | range name-status | absent from the diff — matches the report's bleed claim | PASS |

Conformance defects: none found. (Status-neutral observations are in §7.)

## 2. Claim re-checks (step 2) — both claims RE-MEASURED by the verifier

Frozen instruments were extracted from the freeze commit `3cc69c45` and run
over the lane repo with `--rev` (git object store only, isolated scratch under
the verifier's session scratch; nothing written inside the repo). The frozen
bytes match the preregistration's own pins, so "the SAME counter bytes measure
both ends" is byte-verified, not asserted:

- `sha256(census/round-50/c1-counter.py @ 3cc69c4)` = `a3eadff84fe8d67e…e6e29aa` — equals the prereg's declared value
- `sha256(census/round-50/c2-counter.py @ 3cc69c4)` = `0acefa7edffcb3c1…6e3ac123` — equals the prereg's declared value
- `sha256(c1-arms.tsv)` = `e4812c413efde9db…5041e4`; `sha256(c2-arms.tsv)` = `0f6dfd5f86480dab…2c0a19` — both equal the prereg's declared values

### C1 — calibration (lowest non-retired axis, score 7): S267 token readings re-derivable by committed command

| run | command | observed output | exit |
|---|---|---|---|
| RED at base | `python -B c1-counter.py --root LANE --rev 5f921fe2… --scratch DIR` | `PRISTINE FAIL TOOL-ABSENT tools/souji-page-token-count.py at 5f921fe2…` / `SUMMARY reading=FAIL footer=FAIL body=FAIL erratum=FAIL sourced=FAIL selftest=FAIL tool_sha=absent` | 1 |
| GREEN at content tip | same, `--rev 6d94929f…` | `SUMMARY reading=ok footer=ok body=ok erratum=ok sourced=ok selftest=ok content_histor=0 raw_histor=1 content_factual=0 raw_factual=0 tool_sha=5923b315fe6f` | 0 |
| GREEN at final tip | same, `--rev 66834975…` | identical SUMMARY line, `tool_sha=5923b315fe6f` | 0 |

Reported values match byte-for-byte, including the committed do-nothing
controls (`c1-control-donothing.txt` / `c2-control-donothing.txt` at the
freeze read exactly the RED lines above with `EXIT=1`).

Plain re-measurement behind the headline (verifier's own run of the extracted
content-tip tool over the committed capture):

- `--capture s267-stdtypes-capture.html --token histor` → `SCOPE-RAW-MATCHES=1`,
  `SCOPE-CONTENT-MATCHES=0`, METHOD line present, `BYTES=814236`,
  `SHA256=0a9474e3b83b8fb3…1c8f5d3` — capture is 814236 bytes and the sha256
  matches the report and the committed count receipt (`0a9474e3…f5d3`).
- `--token factual` → `SCOPE-RAW-MATCHES=0`, `SCOPE-CONTENT-MATCHES=0`.
- Raw-scope occurrence located by the verifier: exactly one case-insensitive
  `histor` hit in the committed capture bytes, at line 7330
  (`History and License`), inside the `<div class="footer">` opened at line
  7322 — exactly the site-chrome footer occurrence the erratum names.
- Standalone selftest: `SELFTEST cases=8 pass=8 fail=0`, exit 0 (matches the
  registry row's `--selftest 8/8` and includes the `charref-decoded`
  raw=0/content=1 discriminator arm).

Erratum leg: `corpus/lessons/round-50.md` at the tip carries the column-0
`S267-COUNT-ERRATUM …` line naming `tools/souji-page-token-count.py` and the
exact commands (re-derived by the counter's erratum leg = ok). Sourced leg:
the `| S273 |` row exists in `corpus/SOURCES.md` naming html.parser.

**C1 verdict: calibration improved** (record-accuracy instrument landed; the
r49 wording class is now two named scopes with a committed re-derivation; the
numeric score stays 7, which the SCORECARD discloses honestly).

### C2 — operability (capability acquisition): census receipts that verify

| run | command | observed output | exit |
|---|---|---|---|
| RED at base | `python -B c2-counter.py --root LANE --rev 5f921fe2… --scratch DIR` | `PRISTINE FAIL TOOL-ABSENT tools/souji-census-receipt.py at 5f921fe2…` / `SUMMARY receipts=0 verified=0 selftest=FAIL before=FAIL tool_sha=absent` | 1 |
| GREEN at content tip | same, `--rev 6d94929f…` | `receipts census-before-receipt.txt rc=0 ok` / `SUMMARY receipts=1 verified=1 selftest=ok before=ok tool_sha=1d092142eb73` | 0 |
| GREEN at final tip | same, `--rev 66834975…` | `receipts census-after-receipt.txt rc=0 ok; census-before-receipt.txt rc=0 ok` / `SUMMARY receipts=2 verified=2 selftest=ok before=ok tool_sha=1d092142eb73` | 0 |

Reported values match byte-for-byte. Standalone selftest of the extracted
tool: `SELFTEST cases=6 pass=6 fail=0`, exit 0, with the five tamper/malform
arms each observed passing at its named class (digest-mismatch,
count-mismatch, rc-inconsistent, adapter-drift, malformed-raw-section) — the
negative controls refuse. Committed evidence: `census-after-verify.txt` reads
`VERIFY ok receipt=…census-after-receipt.txt lane=souji conf_rc=2 dir_rc=0
w04=59 result=ok checks=grammar,digest,raw-section,rc,w04,result,adapter-sha,
fleet-script-sha adapter=ok`, `AFTER-VERIFY-EXIT=0`. The before-receipt
header carries `CONF-RC=2` / `DIR-RC=0` / `DIR-RESULT=ok` / `DIR-WARN-W04=59`
with the conf form's raw `souji missing` rc-2 verdict embedded verbatim in the
RAW-SECTION — disclosed, never masked.

**C2 verdict: operability improved** (capability acquisition verified: the
contract-mandated census receipts are now digest-bound, re-derivable, and
tamper-refusing; capability row entered the SCORECARD table in the same
round; numeric score stays 8, disclosed).

### No owned axis harmed

`git diff-tree -r -p 5f921fe2 6683497 -- SCORECARD.md` shows a single
append-only hunk (+38 lines at end of file): the r50 landing section, the
capability row, and the planned-r51 section. No existing axis row was
modified; calibration 7 / operability 8 / coverage 8 unchanged. Spot reads of
the surrounding SCORECARD context confirm the hunk appends after the r49
section. **No axis harmed.**

## 3. Freeze discipline (coordinator-directed check) — VERIFIED BY EXECUTION

Structural facts (re-derived): the freeze commit `3cc69c4` adds prereg +
counters + populations + fixtures + red controls + pre-flight receipts (census
before raw + v1 receipt, porcelain-at-base, NTFS base, idx-repair refusal) and
source captures; the first claim-tip receipts (`c1-tip-50.txt`,
`c2-tip-content-50.txt`) appear only in the end commit `6683497`; the frozen
blobs are byte-identical to the prereg's declared sha256 pins (see §2).

Re-executed: `tools/souji-freeze-check.py` (extracted from the tip) over
`--prereg census/round-50/preregistration.txt`:

| rev | output | exit |
|---|---|---|
| freeze `3cc69c4` | `SUMMARY claims=2 findings=0` | 0 |
| content tip `6d94929` | `SUMMARY claims=2 findings=0` | 0 |
| final tip `6683497` | `SUMMARY claims=2 findings=0` | 0 |

The committed receipt `records/freeze-check-at-content-tip.txt`
(`SUMMARY claims=2 findings=0` / `FREEZE-CHECK-TIP-EXIT=0`) is reproduced by
the verifier's own run. The freeze was green before any claim receipt existed.

## 4. S273 grounding (coordinator-directed check) — VERIFIED

- Live re-open (verifier's own curl, 2026-11-01):
  `https://docs.python.org/3/library/html.parser.html` → HTTP 200, no
  redirect, 55260 bytes, sha256
  `13ba271cea644c22a10c51836844e7a1089bf53af82ef1da5978338bf7c777f4` —
  byte-identical to the committed capture `s273-htmlparser-page.html` and to
  the S273 row's recorded digest.
- Quote in retained bytes: the verifier re-ran the located-quote command
  (display-faithful tag stripping, empty replacement; whitespace flattened)
  over the committed capture → `True 20`. The quote "all character references
  (except the ones in elements like script and style) are automatically
  converted to the corresponding Unicode characters" is a verbatim substring
  of the retained page text; 20 words ≤ the 25-word Gate bound.
- Grounding fit: the quote is the `HTMLParser(convert_charrefs=True)`
  contract — exactly the behavior the content-scope counter relies on for
  character-reference decoding; the tool's selftest has a dedicated
  `charref-decoded` arm (raw=0 content=1) demonstrating the behavior. The row
  and the instrument's METHOD line correctly scope the grounding (char-ref
  decoding is grounded by S273; the site-chrome element-exclusion policy is
  the instrument's own named policy).

## 5. Discernment spot-check (step 3)

Gate sample: 1 admit (S273) + 1 reject (standing S267 re-open). Both sources
re-opened live by the verifier; the ≤25-word quote check was run against the
newly written SOURCES row.

| item | decision | re-opened source (verifier's observation) | agree/disagree | reason |
|---|---|---|---|---|
| S273 Python html.parser docs | admit (tier A docs, scope: the char-ref decoding behind the r50 content-scope counter) | live fetch HTTP 200, no redirect, 55260 bytes, sha256 `13ba271c…77f4` byte-identical to the committed capture; located quote re-derived `True 20` | AGREE | authoritative official docs; the quoted convert_charrefs contract genuinely grounds the content scope's decoding; tier/scope/anchor discipline correct; used-by resolves (corpus/lessons/round-50.md exists) |
| S267 standing reject (re-opened with counting method named) | reject holds, no row cell changed | live fetch HTTP 200, 814236 bytes, sha256 `0a9474e3…f5d3` byte-identical to the r49 fetch claim and the committed capture; verifier's own instrument run: content histor=0 / raw histor=1 (footer "History and License") / factual 0/0 | AGREE | the re-open receipt names the method and pastes command+output (the exact r49 routed fix); the counting precision confirms the record while the rejection rationale (equality semantics do not validate historical referents) is unaffected; keeping it rejected with a corrected reading is the calibrated outcome |
| reject-sample sweep (Gate: exactly one candidate fetched, zero new reject rows) | stated explicitly | the two-fetch bound is consistent with the committed receipts: s267-stdtypes-capture.html + s273-htmlparser-page.html are the only round-50 source captures | AGREE | negative claim carries its sweep (both fetch receipts committed) |

Census: the verifier ran
`bash <fleet>/scripts/sources-census.sh validate --root <fleet> souji` →
`souji missing <fleet>/souji-shokunin/corpus/SOURCES.md`, exit 2. This
reproduces exactly the documented conf-form host state disclosed inside both
committed census receipts (`CONF-RC=2`, the raw `souji missing` line embedded
verbatim); the explicit-lane-directory form's `ok` verdict (59 W04, rows
196→197, dir_rc=0) is digest-bound in the v1 receipts and was re-verified by
the verifier's own c2-counter runs (`verify ok` over all checks including
adapter-sha and fleet-script-sha). The conf-form breakage is the carried r48
L0 question; the lane routed it to the operator with a consolidated proposal
line (fleet `.ufo/l0-questions.md` line 252) instead of masking it —
AGREE with that routing; nothing assumed answered.

## 6. Per-axis verdicts and trend verdicts

| axis | verdict | evidence |
|---|---|---|
| calibration | improved | C1 re-measured red→green (§2); S267 readings re-derivable at two named scopes; append-only erratum on file; honest refusal to claim numeric-score credit (stays 7) |
| operability | improved | C2 capability acquisition re-measured red→green (§2); receipts verify digest-bound with named refusal classes; capability row entered same round (score stays 8, disclosed) |
| coverage | unchanged | no PROVINCE change, no new surface (PROVINCE.md absent from the range diff); SOURCES 196→197 is one docs row on already-held docs-host ground |

| trend | verdict | evidence |
|---|---|---|
| expansion | unchanged | no `corpus/knowledge/` entry, no Core promotion, no new province surface; +1 SOURCES row on held ground; capability grows the repertoire on existing census ground; coverage stays 8 |
| quality | improved | the census receipt class — a contract-mandated artifact produced every round — upgraded from raw captures to digest-bound, tamper-refusing, script-drift-detecting receipts (verifier re-ran verify + selftest); token readings re-derivable by committed command (verifier re-ran); both tools' selftests refuse their negative controls |
| discernment | improved | three mistakes mined with same-round executed fixes (lesson §Mistakes, each with evidence); the pre-freeze feasibility leg caught two counter defects before the freeze (disclosed in the prereg); the S267 erratum names its own counting method — the exact r49 routed fix; fresh-start rulings re-derived against r43/r44/r45; both claims' controls red at base with greens re-derived from committed bytes by this verifier |

These verdicts match the report's trend verdicts and are the ones carried
into the closure JSON.

## 7. Defects and routed items

Status-neutral defects (recorded here and in the closure notes; never bar
admission):

1. **Duplicated Gate bullet (route to the lane, fix next round).**
   `corpus/lessons/round-50.md` `## Gate` carries the "Reject sample (stated
   explicitly, r48-closure carry-in practice)…" bullet TWICE, verbatim
   identical, consecutively. Lessons are append-only: the fix is an appended
   correction line in the r51 lesson naming the duplicated text, never an
   in-place edit.
2. **Carried, operator-owned (not a lane defect).** The literal census
   conf-form command still exits 2 on this host (`souji missing`); the
   consolidated L0 proposal (fleet `.ufo/l0-questions.md`, `souji | round-50`
   line) awaits an operator ruling; the lane routed around with disclosure
   (rc-2 verbatim inside every receipt). Operator action requested on options
   (a)/(b)/(c).
3. **Cosmetic (no action required).** The NTFS tip receipt omits the
   `quoted_d_rows=6` line present in the base receipt (`count=6` and the six
   quoted paths are present at both ends, so the numbers-without-listing
   class is not recurring); noted only for receipt-shape consistency.

NTFS tolerance (coordinator-directed check): base receipt `count=6` with the
same six quoted control-char paths; tip receipt `count=6`, identical six
paths. **Not widened.** Worktree integrity receipts: base idx-repair refused
fail-closed (`14 unexpected row(s)`, receipt committed), suite receipt at the
staged state honestly recorded `COULD-NOT-EVALUATE dirty worktree … 31
unexpected rows` exit 2 (`c1-suite-tip-50.txt`) — the disclosed ordering
practice (the suite run belongs after the terminal repair).

SHONEN note for the operator: all four SHONEN.md boxes are `[~]`
(asserted-by-author) and the report claims no `[x]`; no box is checkable
without a non-author verifier writing it. This verifier re-derived the
evidence pointers the boxes cite (instruments, receipts, LOG entry) but does
not write `[x]` from the closure role; if the operator wants promotion
progress, a dedicated non-author promotion review should re-file the boxes.

## 8. Closure ruling

Both claims re-measured green by the verifier's own execution of the frozen
counters and tools; red states re-measured at the base; frozen bytes
byte-verified against the preregistration pins; freeze-check re-executed
green at freeze/content-tip/final-tip; S273 grounding re-opened live and
quote re-derived in retained bytes; NTFS tolerance 6 at both ends; no axis
harmed; the single defect found is status-neutral and routed. **souji round
50: status ok, admitted.**
