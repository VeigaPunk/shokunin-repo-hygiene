# MutateGateCarry — round 16 wave 2

STATUS: PARTIAL — 6 of 13 isolated carry-channel mutants were killed; 7 survived both authorized suites. These are detector-coverage gaps, not demonstrated defects in the pristine gate.

## Scope and axes

Attacked only LG-SEAT-UNCARRIED / LG-OPEN-ADMITTED: the failure vocabulary, rejected prose phrase markers, fence/table exclusions, named heading and section boundary, normalization, carry disposition, HTML-comment stripping, and admitted/open calibration.

Axes: **failure sensitivity**, **quotation/format false-positive calibration**, **carry-section fidelity**, and **exact-byte reproducibility**. All 13 mutations were single behavior-bearing statement/constant changes in separate `/var/tmp/souji-r16-MutateGateCarry/m<k>.py` copies. No lane implementation or fixture was edited. This report is the only lane write. No dispatch, commits, staging, or tool installation/update.

## Detector and baseline

For every copy, ran exactly the same two detectors on pristine, mutated, and restored bytes:

1. `python3 <copy> --selftest`
2. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool <copy>`

78 completed detector invocations total, with at most six concurrent invocations. For **each** m1–m13, both the pristine and restored runs returned:

```text
selftest rc=0; stderr=''
SELFTEST	pass=18	fail=0
fixture rc=0; stderr=''
SUMMARY	total=15	failed=0
```

There was no baseline failure, timeout, or inconclusive probe. All mutated runs also had empty stderr. A kill below means an assertion failed, not a syntax/import crash. The external fixture was necessary for four kills that the built-in selftest missed (m1/m2/m3/m13).

## Mutants and observed results

Paths and line numbers below refer to the unmodified absolute source `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py`.

| Mutant | Source line | Single change | Calibration risk | Selftest rc / pass / fail | Fixture rc / total / failed | Verdict; killing case or gap |
|---|---:|---|---|---|---|---|
| m1 | 75 | Remove `"partial"` from FAILURE_STATUS_WORDS. | false negative | 0 / 18 / 0 | 1 / 15 / 1 | **killed**; fixture: marker-rewordings (SeatG missing) |
| m2 | 267 | Replace the no-STATUS return with a case-insensitive does-not-parse / does-not-ship prose regex (exact patch below). | false positive | 0 / 18 / 0 | 1 / 15 / 1 | **killed**; fixture: marker-rewordings (SeatC and SeatD unexpected) |
| m3 | 263 | Change `if in_fence or in_table:` to `if in_table:`. | false positive | 0 / 18 / 0 | 1 / 15 / 1 | **killed**; fixture: marker-rewordings (SeatF unexpected) |
| m4 | 264 | Change the fence/table guard return from `False` to `in_table`. | false positive | 1 / 17 / 1 | 1 / 15 / 1 | **killed**; selftest: fenced-and-table-ignored; fixture: marker-rewordings |
| m5 | 301 | Change the next-heading section terminator from `break` to `continue`. | false negative | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C5 |
| m6 | 81 | Broaden FAILURES_HEADING_RE from the named failure heading to `r"^##\s+"`. | false negative | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C6 |
| m7 | 242 | Delete the NFC-normalization statement. | false positive | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C7 |
| m8 | 243 | Delete removal of asterisks and backticks. | false positive | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C8 |
| m9 | 244 | Replace whitespace collapse with `text = text.strip()`. | false positive | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C9 |
| m10 | 85 | Remove `re.DOTALL` from the HTML-comment regex. | false negative | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C10 |
| m11 | 347 | Change `if lesson_admitted:` to `if not lesson_admitted:`. | both | 1 / 16 / 2 | 1 / 15 / 1 | **killed**; selftest: carried-open and open-admitted; fixture: open-marker-admitted-true |
| m12 | 338 | Remove `and CARRY_TOKEN_RE.search(nl)` from the carry predicate. | false negative | 0 / 18 / 0 | 0 / 15 / 0 | **survived**; survived; proposed C12 |
| m13 | 289 | Return `lesson_text.splitlines()` without HTML-comment removal. | false negative | 0 / 18 / 0 | 1 / 15 / 1 | **killed**; fixture: carry-inside-html-comment |

The exact m2 replacement was:

```python
return bool(re.search(r"does(?: not|n't) parse|do not ship", line, re.IGNORECASE))
```

This intentionally regresses the measured decision not to treat prose quotations as the STATUS failure channel; it does not propose reinstating phrase matching.

### Actual failing stdout

Every failure line is reproduced below, followed by its actual suite summary. Passing-case lines are omitted. For each survivor m5/m6/m7/m8/m9/m10/m12, actual mutated stdout instead ended in `SELFTEST	pass=18	fail=0` and `SUMMARY	total=15	failed=0`, both rc=0.

#### m1

```text
selftest rc=0; stderr=''
SELFTEST	pass=18	fail=0
fixture rc=1; stderr=''
CASE	marker-rewordings	FAIL	exit=1 lg_rows=3 FAIL(missing LG-SEAT-UNCARRIED ~ SeatG)
SUMMARY	total=15	failed=1
```

#### m2

```text
selftest rc=0; stderr=''
SELFTEST	pass=18	fail=0
fixture rc=1; stderr=''
CASE	marker-rewordings	FAIL	exit=1 lg_rows=6 FAIL(unexpected LG-SEAT-UNCARRIED ~ SeatC; unexpected LG-SEAT-UNCARRIED ~ SeatD)
SUMMARY	total=15	failed=1
```

#### m3

```text
selftest rc=0; stderr=''
SELFTEST	pass=18	fail=0
fixture rc=1; stderr=''
CASE	marker-rewordings	FAIL	exit=1 lg_rows=5 FAIL(unexpected LG-SEAT-UNCARRIED ~ SeatF)
SUMMARY	total=15	failed=1
```

#### m4

```text
selftest rc=1; stderr=''
CASE	FAIL	fenced-and-table-ignored	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
SELFTEST	pass=17	fail=1
fixture rc=1; stderr=''
CASE	marker-rewordings	FAIL	exit=1 lg_rows=7 FAIL(unexpected LG-SEAT-UNCARRIED ~ SeatF)
SUMMARY	total=15	failed=1
```

#### m11

```text
selftest rc=1; stderr=''
CASE	FAIL	carried-open	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	FAIL	open-admitted	exit=0 ids=[] err=None
SELFTEST	pass=16	fail=2
fixture rc=1; stderr=''
CASE	open-marker-admitted-true	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-OPEN-ADMITTED ~ SeatA/round-77/Seat-reported)
SUMMARY	total=15	failed=1
```

#### m13

```text
selftest rc=0; stderr=''
SELFTEST	pass=18	fail=0
fixture rc=1; stderr=''
CASE	carry-inside-html-comment	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-SEAT-UNCARRIED ~ SeatA)
SUMMARY	total=15	failed=1
```

## Survivor counterexamples and smallest fixes

**Coverage verdict: partial.** The authorized suites do not distinguish the seven changed implementations below from pristine bytes. Smallest fixes are additional cases in `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py`; do not relax the contract or change gate production logic on this evidence.

The following are **proposed, unrun cases [INFERENCE]**. Their expected differences follow from the cited source statements, not from additional execution. Each uses an otherwise clean synthetic fixture repo with SKILL.md, a parseable cited script, a report under `.ufo/waves/round-77/w1/SeatA.md`, and `admitted: false`. Unless specified otherwise, place the lesson carry under exactly `## Seat-reported failures`.

### C5 — heading ends the carry section (m5; source:300–301)

Report: `STATUS: FAIL — boundary-probe`.

Lesson tail:

```markdown
## Seat-reported failures

## Other evidence

STATUS: FAIL — boundary-probe — open
```

Expected pristine result: rc=1 and LG-SEAT-UNCARRIED for SeatA. The mutant continues after the next heading and incorrectly accepts this outside-section carry. Smallest fix: add this one section-boundary negative control. Current fixture marker-one-char-off (fixture:361–381) only tests text mismatch, not the end of the designated section.

### C6 — only the named heading is a carry target (m6; source:81,297)

Report: `STATUS: FAIL — heading-probe`.

The lesson has **no** `## Seat-reported failures` heading; instead:

```markdown
## Other evidence

STATUS: FAIL — heading-probe — open
```

Expected pristine result: rc=1 and LG-SEAT-UNCARRIED. The broadened regex accepts any second-level heading. Smallest fix: add this wrong-heading negative control, rather than treating mention anywhere in the lesson as carry.

### C7 — canonical Unicode equivalence (m7; source:240–242)

Report body: `STATUS: FAIL — cafe\u0301-probe` (interpret the escape as U+0065 U+0301).
Lesson carry: `STATUS: FAIL — café-probe — open` (U+00E9).

Expected pristine result: rc=0, no LG-SEAT-UNCARRIED. Without NFC the visually identical marker is incorrectly uncarried. Smallest fix: add a decomposed/composed pair on the opposite sides of the comparison. The report and lesson must not reuse the exact same byte string.

### C8 — formatting must differ across report and lesson (m8; source:243)

Report: `**STATUS:** FAIL — formatting-probe`.
Lesson carry: `STATUS: FAIL — formatting-probe — open`.

Expected pristine result: rc=0, no LG-SEAT-UNCARRIED. Without stripping decoration the mutant raises a false positive. Smallest fix: add this asymmetric-decoration pair, plus the same shape with backticks around only `formatting-probe` in the report. The existing selftest carried-resolved (source:902–912) copies the same decorated marker into the lesson; its survival shows that decoration present on both sides does not exercise normalization.

### C9 — collapse internal whitespace, not only trim ends (m9; source:244)

Report: `STATUS: FAIL — spaced\tprobe` (interpret `\t` as one tab).
Lesson carry: `STATUS: FAIL — spaced probe — open`.

Expected pristine result: rc=0. The `.strip()` mutant cannot match internal tab versus space and incorrectly emits LG-SEAT-UNCARRIED. Smallest fix: add this asymmetric-whitespace positive control.

### C10 — multiline HTML comment is not visible carry (m10; source:85,289)

Report: `STATUS: FAIL — multiline-comment-probe`.
Lesson tail:

```markdown
## Seat-reported failures

<!--
STATUS: FAIL — multiline-comment-probe — open
-->
```

Expected pristine result: rc=1 and LG-SEAT-UNCARRIED. Removing DOTALL leaves the hidden marker available as a carry. Smallest fix: add this multiline companion to fixture carry-inside-html-comment (fixture:417–429), whose current comment is entirely on one line. The same existing case kills complete comment-strip removal (m13) but does not kill this narrower defect.

### C12 — a repeated marker without disposition is not carried (m12; source:338)

Report: `STATUS: FAIL — disposition-probe`.
Lesson carry line: `STATUS: FAIL — disposition-probe` with **neither** `open` nor `resolved@<hex>` anywhere on that line.

Expected pristine result: rc=1 and LG-SEAT-UNCARRIED. Removing CARRY_TOKEN_RE makes the bare repetition count as carry. Smallest fix: add a missing-disposition negative control; preserve the required open/resolved contract. Existing carried lines in fixture:373–376 and 481–483 all already provide valid dispositions.

## Byte and restoration evidence

Original source SHA-256 (**B**, before and after the whole probe):

```text
e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2
```

Unmodified external fixture SHA-256 (before and after):

```text
aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f
```

All 13 copies were hashed before mutation, after mutation, and after exact inverse edits. **Before = B and restored = B for every row**; mutated hashes were:

| Copy | Before | Mutated SHA-256 | Restored |
|---|---|---|---|
| m1.py | B | `caa098ed27650962885d03edb49063a3d3d97a2ba19873bd801ded25c45f30b3` | B |
| m2.py | B | `5da635406042dde3df77611da4e1e4d797d0eaa13b71c4b2e154406ade32bb61` | B |
| m3.py | B | `a26e3b4bb9d47a260aaf0a95df63812d0780665e97fe388f8e3a986a0479aaf7` | B |
| m4.py | B | `06fc61728cc78c9c555f9996064903999302f8691b51b15734ee5307b134c2e2` | B |
| m5.py | B | `acd23433436460392bd8f53c7b90877298b0fc0eab2aff7ae9cd74cbb833ef01` | B |
| m6.py | B | `cdc097deb5cf6122900eeee38ec650a1085cbbc7ae99e4cf388aa26bd60c40f9` | B |
| m7.py | B | `3b61abb6accea8dfc988517564277a201450691917c111b2aa6c4d3e3b05e667` | B |
| m8.py | B | `3fa6a262079c1d41bb816aa338d8743a52a506a76e604527466a967623a91bbd` | B |
| m9.py | B | `e097d729566286a9fad42d6b0c5c4bceac0bb471091504aa3419a81b76a2165f` | B |
| m10.py | B | `4df914ea88ba6061f7c4d525cac4d3c30e8388aa3ee3a5506c16feeae9b7ce0c` | B |
| m11.py | B | `c62d340a335f22a675abf8c8be413ac563d02ab9916302b16b6b7fdd74684ed7` | B |
| m12.py | B | `58fc17cf0592c2caca1f97279039d3ef5aeeb927175c2e4e4e210b337b8233ad` | B |
| m13.py | B | `dc37302facca6e1086fc1d0bf36372550503cf3a96df7c1326878711dafeb0ac` | B |

Restored tests were run after checking exact byte restoration, not on newly introduced variants. The scratch tree was then deleted with the cleanup command below; the trailing `test ! -e` succeeded. No report-only survivor case above was executed. No gate was run as a general census or against a working directory outside the explicitly authorized selftest/fixture workflows.

## Commands

No tools were installed or upgraded. The only direct shell invocations were the following (the two identical sha256sum invocations are both listed). The detector argv lines below were launched through Python asyncio subprocess-exec, not a shell; they are included verbatim for complete executable-command disclosure. At most six detectors ran concurrently.

Setup:

```sh
mkdir -p /var/tmp/souji-r16-MutateGateCarry/support && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m1.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m2.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m3.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m4.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m5.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m6.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m7.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m8.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m9.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m10.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m11.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m12.py && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateCarry/m13.py
```

Before-input hash command:

```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```

The following exact 26 detector argv lines were each executed **three times**, once in each phase in order: pristine, mutated, restored. Within a phase their completion order was concurrent; no other detector command was used.

```sh
python3 /var/tmp/souji-r16-MutateGateCarry/m1.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m1.py
python3 /var/tmp/souji-r16-MutateGateCarry/m2.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m2.py
python3 /var/tmp/souji-r16-MutateGateCarry/m3.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m3.py
python3 /var/tmp/souji-r16-MutateGateCarry/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m4.py
python3 /var/tmp/souji-r16-MutateGateCarry/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m5.py
python3 /var/tmp/souji-r16-MutateGateCarry/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m6.py
python3 /var/tmp/souji-r16-MutateGateCarry/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m7.py
python3 /var/tmp/souji-r16-MutateGateCarry/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m8.py
python3 /var/tmp/souji-r16-MutateGateCarry/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m9.py
python3 /var/tmp/souji-r16-MutateGateCarry/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m10.py
python3 /var/tmp/souji-r16-MutateGateCarry/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m11.py
python3 /var/tmp/souji-r16-MutateGateCarry/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m12.py
python3 /var/tmp/souji-r16-MutateGateCarry/m13.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateCarry/m13.py
```

Authorized detector-internal temporary directories, disclosed per L1's explicit exception: `/var/tmp/souji-landing-gate-selftest-*` (source:749), `/var/tmp/souji-landing-gate-*` (source:527), and `/var/tmp/souji-r16-lgfixture-*` (fixture:224–226). Their unmodified implementations remove their scratch directories in `finally` (source:589–590,967–968; fixture:521–522). Exact generated suffixes are not printed by the detectors, and were not independently enumerated. No sitecustomize, wrapper, runtime substitution, or temp-path patch was applied. The empty `support` directory created during setup was unused and removed with the rest of the seat scratch tree. Fixture/selftest child git commands operate on their synthetic scratch repos, except the fixture's authorized read-only historical replay.

After-input hash command:

```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```

Cleanup (successful):

```sh
rm -rf -- /var/tmp/souji-r16-MutateGateCarry && test ! -e /var/tmp/souji-r16-MutateGateCarry
```
