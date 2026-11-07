author: hyaku closure (non-author integrator, @m_zfl)

# souji round 78 — verifier spot-check (non-author closure)

Round: souji lane-round 78. Lane base `a8558d410e9855a9d990d6542a24a9a3a365ab6c`, after
`4632b99f5e887e969e7f6ad942fd16bfe1010dcf` (branch `master`). Report `.ufo/reports/round-78/souji.md`
(fleet repo). Driver digest (copied from `.ufo/watchdog.log`):
`2026-11-06T23:45:56-03:00 launch souji round=78 pgid=310313 driver=hyaku-inline attempt=1`;
`2026-11-07T01:46:56-03:00 complete souji round=78; hyaku-inline attempt=1`.
Written 2026-11-07. This file is the only artifact the closure writes in the lane.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-78/souji.md` (fleet) | `souji-shokunin b86ad310083f62768c67a44ac3f4ea6e53b21436` | ok |
| SHONEN heading, one line per box | `grep -c '^## SHONEN' <report>`; `grep -cE '^- \[[ x~]\]' SHONEN.md` | 1; 4 boxes, 4 `[~]` lines | ok |
| every cited lane commit is an ancestor of `master` | `git merge-base --is-ancestor <h> master` for a0dcfa8d, 007404ea, ed22dc9c, d90740fe, a0f3b91f, 87d45617, 319109b0, bbd199da, 3221566c, 6a49837d, 723295a4, e6910259, 62b35a33, a500ee69, 4632b99f | all 15 `ok` | ok |
| lane pushed, clean | `scripts/hyaku/jj-lane.sh state souji-shokunin`; `git status --porcelain` | `local=remote=4632b99f… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty | ok |
| commits by lane identity | `git log --format='%an <%ae>' a8558d41..4632b99f \| sort -u` | `souji-shokunin <souji@shokunin.local>` only | ok |
| prompt carries the template contract | `.ufo/prompts/souji-round-78.md` (933 lines): Before → after, Trend verdicts, SHONEN sections and §6 hyaku addendum present | present | ok |
| append-only lane files | `git diff --numstat a8558d41 4632b99f \| awk '$2>0'` | only `corpus/SOURCES.md` (1 line: S321 cell correction, routed r77 defect 1) and `tools/souji-pre-report-gate.sh` (the claimed gate change); r77 lesson got an appended `## Correction` | ok |
| SHONEN/PROVINCE untouched | `git diff --stat a8558d41 4632b99f -- SHONEN.md PROVINCE.md` | empty | ok |

Report is a real report (checkable work and commits), not a marker. Status `ok`.

Conformance notes (status-neutral): the domain-trial receipt graded the first 112 report lines
(`head -n 112 <report> | sha256sum` = `765e575f…e349`, re-run here, equal to the receipt) and the
report was extended afterwards — disclosed in the report itself. The L commit message `a0f3b91f`
miscounts ledger classes (says FLEET 6, ABSENT 7; ledger holds FLEET 5, ABSENT 6) — self-recorded as
lesson M3.

## 2. Claims re-check

Both claims rest on lane-registered gates (SKILL.md rows: r78 C1 git-discovery-source counter, r78
C2 location-bound pointer resolution counter, pointer-existence check). Per PROTOCOL §Gate standard
(Closure consequence) those were **not executed**; their committed receipts were evidence-verified and
re-counted with plain grep/git over committed bytes, and C2's outcome was independently re-measured
with `git cat-file -e` and sha256.

### C1 — operability (sourced, S323/S324)

Re-count of committed receipts at `4632b99f` (`git show <R>:census/round-78/<f> | grep -c '^ROW'`,
`grep -c '^ROW.*match=no'`, plus the SUMMARY/EXIT lines):

| receipt | ROW lines | match=no | SUMMARY | EXIT |
|---|---|---|---|---|
| controls/c1-K-a-do-nothing.txt (before) | 17 | 12 | rows=17 mismatches=12 hangs=12 | 1 |
| controls/c1-K-b-refuse-any-include.txt | 17 | 14 | mismatches=14 hangs=12 | 1 |
| controls/c1-K-c-config-only.txt | 17 | 10 | mismatches=10 hangs=10 | 1 |
| controls/c1-K-d-timeout-only.txt | 17 | 11 | mismatches=11 hangs=11 | 1 |
| records/c1-after.txt (after) | 17 | 0 | rows=17 mismatches=0 hangs=0 | 0 |
| records/c1-regress-r77 / r76 | 16 / 30 | 0 / 0 | 16/16, 30/30 | 0 |
| records/c1-regress-r36 / r27 | — | — | `cases=21 pass=21`; `cases=4 pass=4` | 0 |
| records/wave-repair/c1-at-repair.txt | 17 | 0 | mismatches=0 hangs=0 | 0 |
| records/wave-repair/repair-probes.txt (run1 kept under attempts/) | — | — | arms=10 as_expected=10 (run1 9/8, EXIT 1) | 0 |

Revision measured: receipt binds `tools/souji-pre-report-gate.sh sha256=b746bd9d…4eef`;
`git show ed22dc9c:tools/souji-pre-report-gate.sh | sha256sum` = `b746bd9da677aefe67116a192626151685a8b9f23e7bfee96987e04e645b4eef` (equal).
Gate blob at master and at repair `3221566c` both `5f5cb865…a853`, equal to the domain-trial receipt's
`gate_blob_at_master_sha256` and its printed `amendment=b746bd9d… -> 5f5cb865…`.
Before → after 12 → 0 mismatches, 12 → 0 hangs: **matches the report**. Verdict: evidence-verified,
re-counted. Qualification carried from the lane's own critics stands: a bound-everything variant also
reaches hangs=0, so the delta is the refusal ordering/class (K-d still red at 11).

### C2 — calibration

Independent re-measurement: the 22 MISSING paths of committed `records/c2-pointer-check-before.txt`
tested with `git cat-file -e <rev>:<path>`: at base 20 unique paths absent (22 items, L02/L03 and
L16/L18 share a path); at `4632b99f` 17 absent, 3 present (`.ufo/waves/round-27`,
`.ufo/waves/round-53/w1-results.json`, `.ufo/waves/round-68/w1` = L10, L14, L20). `grep -c '^MISSING'`
on before/after receipts: 22 → 19; `diff` of the MISSING lines removes exactly those three.
Ledger at `87d45617` (`census/round-78/c2-pointer-ledger.tsv`): 19 rows, ids unique (`uniq -d` empty),
L10/L14/L20 absent by design; classes ABSENT 6, FLEET 5, LOCAL-POLICY 2, MOVED 4, QUARANTINED 1, TOKEN 1.
MOVED byte-equality spot-checked: `git show 4632b99f:census/round-44/waves/w1-results.json | sha256sum`
= `ddc9eada…37b7` (population L12 pin), `census/round-69/records/wave-w1/w1-results.json` = `1110b413…6a6`
(L21), `census/round-54/wave/S54critic01.md` = `d74bf320…6872` (L15), captured
`.ufo/waves/round-53/w1-results.json` = `8cd69971…e85e` (L14) — all equal to their population pins.
FLEET L01/L16 resolve on disk (`../.ufo/scopes/souji-mint-20261018/mint-roster-scan.json`,
`../.ufo/l0-questions.md`).
Committed receipts: `controls/c2-K-a-no-ledger.txt` `items=22 resolved=0` EXIT=1;
`records/c2-after.txt` (`--rev 87d45617…`) `items=22 resolved=22 unresolved=0 refused=0 mismatched=0`,
`FORGE-SUMMARY forged=12 matched=12 accepted=0` EXIT=0; `records/c2-regress-r77.txt` 35/35, forged 7
matched 7. Before → after 0 → 22, pointer-check 22 → 19: **matches the report**. Verdict:
re-measured (capture/move outcome) + evidence-verified (counter verdict). Qualification stands: over
the 19-of-22 mechanical ceiling the delta is the three captures.

### Owned axes

`git diff a8558d41 4632b99f -- SCORECARD.md`: appends only (r78 done row, r79 planned, measurements and
capability rows); "No owned axis score changed (calibration 7, coverage 8, operability 8)". No harm
found in spot reads of SKILL.md (+2 gate rows), QUALITY (+2), README (+5 frontier), LOG (+11).

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 12 → 0 mismatches/hangs, regressions green at W and R |
| calibration | improved | C2 0 → 22 resolved, forgeries refused, pointer check 22 → 19 |
| coverage | unchanged | no claim; S323/S324 + knowledge entry counted under expansion |

No exploratory claim was declared.

## 3. Discernment spot-check

Sources re-opened live (curl, 2026-11-07):

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S323 git config.adoc Includes | admit (A, mined) | `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config.adoc` HTTP 200, 21095 B, sha256 `a6e644cb…b2c9` | agree | sha equals the row; lines 99-100 carry the quote verbatim (22 words ≤25); it is the primary statement that includes are read inline, which C1's include rows rest on |
| S324 git setup.c get_common_dir_noenv | admit (A, mined) | `…/v2.56.0/setup.c` HTTP 200, 83214 B, sha256 `8316b1ad…c589` | agree | sha equals the row; lines 327-329 hold the quoted commondir build/file_exists/strbuf_read_file; line 373 `open(path, O_RDONLY)` supports the HEAD note being outside the quote, as the lesson records |
| Documentation/config/include.adoc | reject | `…/v2.56.0/Documentation/config/include.adoc` | agree | HTTP 404 (14 B) reproduced; nothing to admit |
| gitrepository-layout(5) as open-behaviour source | reject | `…/v2.56.0/Documentation/gitrepository-layout.adoc` HTTP 200, 11890 B, sha256 `39ce8d13…9439` | agree | lines 268-273 define what commondir means, not that/how git opens it; the semantics are already held as S124 (`corpus/SOURCES.md:159`) |

SOURCES row re-opened: `corpus/SOURCES.md:282` (S323) quote "The contents of the included file are
inserted immediately, as if they had been found at the location of the include directive." — 22 words,
verbatim at capture/live lines 99-100. Row count `grep -cE '^ {0,3}\| *S[0-9]{3,}' corpus/SOURCES.md`:
245 at base → 247 at `4632b99f`.

Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` →
`souji ok …/corpus/SOURCES.md`, EXIT=0 (warnings W04 only; new W04 `S324 duplicate url … setup.c across
scopes` is the declared S300 overlap in the SOURCES `Round-78 provenance` line).

## 4. Trend verdicts

- **expansion: improved** — +2 tier-A mined rows (245 → 247), new `corpus/knowledge/git-discovery-sources.md`
  (68 lines), QUALITY Q140/Q141, two capability rows backed by receipts.
- **quality: improved** — wave repair of the gate with probes that failed first (run1 8/9 kept) then
  10/10, frozen C1 at repair 17/17; r77 routed defect 1 closed in both S321 cells plus an append-only
  correction in the r77 lesson.
- **discernment: improved** — outside spot-check agrees 4/4 (2 admits, 2 rejects); the lane recorded its
  own instrument/process errors (M1–M8, incl. the L ledger duplicate and the commit-message miscount)
  and filed critics' qualifications instead of contesting them.

## 5. Routed defects (lane fixes next round)

1. `a0f3b91f` commit message class counts are wrong (FLEET 6/ABSENT 7 vs 5/6); M3 records it — carry a
   LOG.md pointer to M3 wherever the L message is cited as a count source.
2. Preregistration Surface attributes the HEAD read to S324, whose quoted lines cover commondir only;
   either add a row for setup.c validate_headref (line ~350-373) or stop citing S324 for HEAD.
3. C2 counter: four mutants survive every frozen artifact and five false single rows pass (lane's own
   S78MutCounter) — add rows that kill them; C1 counter lacks a duration predicate (m13) and its killpg
   misses `timeout`'s own process group.
4. Domain-trial receipt graded a 112-line prefix of the report; grade the final report bytes (or
   pin the final report hash in a follow-up receipt) so the trial covers what was filed.
5. Carried from the report: SIGTERM path and check-4 300 s backstop row (SCORECARD "r79 (planned)").
6. Pointer check over LOG.md still reports missing=19 by design (classified, not present); keep the
   ledger as the authority and do not let the raw pointer check read as a regression.

Operator note: all four SHONEN boxes are `[~]` with pointers that resolve at `4632b99f`; whether any is
fully checkable for promotion is the operator's call.
