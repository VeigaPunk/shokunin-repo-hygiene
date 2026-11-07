# Round 77 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatch digest (copied from `.ufo/watchdog.log` because the log is mutable):
`2026-11-06T22:49:06-03:00 launch souji round=77 pgid=419010 driver=hyaku-inline attempt=1`;
`2026-11-06T23:40:34-03:00 complete souji round=77; hyaku-inline attempt=1`.
Lane base `d4f515637884695b3aa016da169d859d3ece6ac4`, lane tip `a5a186667ea8f790bdcb313e6acb06683bed345e`.
The closure authored no round byte and ran no lane gate, counter, probe or selftest (PROTOCOL §Gate standard,
Closure consequence; every r77 counter is registered as a `gate` in SKILL.md rows 941-942). Gate/counter numbers
below are evidence-verified from committed receipts (`git show a5a18666:<path> | grep`), with every pinned
instrument, population and gate blob re-hashed by the closure. The C2 ledger resolutions (MOVED byte identity,
CAPTURED digests, TOKEN/FLEET target existence), source bytes, quotes, the SOURCES row count and the census were
re-measured by the closure itself.

## Conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-77/souji.md` | `souji-shokunin <souji@shokunin.local> 895efab25ec15c8d35e72e156ad9935d7746155e 2026-11-06 23:40:05 -0300`; after the lane tip (23:39:55), before `complete` (23:40:34) | pass |
| `SHONEN` heading, one line per box | read report lines 109-114 | one `## SHONEN` heading, 4 lines, all `[~]`, each with an evidence pointer | pass |
| cited lane commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> master` for the 10 cited full hashes (43822328 … a5a18666) plus the base | all `ok`; all 10 round commits authored by `souji-shokunin`; `git log d4f51563..master` lists exactly these 10 | pass |
| lane pushed, nothing left over | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `state branch=master local=a5a18666… remote=a5a18666… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; ls-remote `a5a18666…` | pass |
| prompt carries the template contract | `diff <(grep -v '{{' templates/round-prompt.md \| sed -n 1,140p) <(sed -n 1,140p .ufo/prompts/souji-round-77.md)` | only placeholder-bearing lines differ (lane/round/fleet-root substitutions); §1-§5 headings identical to the template, then hyaku addendum §6/§7 and run15 notes; prompt committed `7269ba69` at 22:49:03, before launch | pass |
| chronology P → F → W → K → L → A → R | `git log d4f51563..master` subjects + receipts' `rev=` lines | controls `rev=d4f51563` (base) in P `43822328`; prereg alone in F `a9979807`; gate in W `9b496b08`; freeze-check receipt `SUMMARY claims=2 findings=0` EXIT=0 | pass |
| prereg digests / frozen inputs untouched | `git show <P\|tip>:<path> \| sha256sum` | c1-nonreg-counter `e511bd57…5115`, c1-population `b4d50bef…bab4`, c2-pointer-counter `8904de85…b54b`, c2-population `bbc19ac6…889e` — equal at P and at tip and equal the prereg | pass |
| gate blobs | `git show <c>:tools/souji-pre-report-gate.sh \| sha256sum` | base `90bdd8c7…47f3` (= prereg "before"), W and L `28a51355…16be` (= `c1-after.txt` bind line), R and tip `5d08f547…df55a` (= `c1-at-repair.txt` and domain-trial bind lines); writer `70bbf1c2…defa` unchanged base→tip | pass |
| fleet misroot | report Misroot sweep; `git -C /home/vgpnk/Projects/shokunin status --porcelain` | only orchestrator `.scratch/*` and pre-existing `?? trail-ids.txt` | pass |

## Claims

### C1 — operability (gate refuses non-regular exclude/attribute sources): **improved** (evidence-verified)

- Before: `controls/c1-K-a-do-nothing.txt` → `rev=d4f51563…`, rows n1-n7 and n10 `clean=HANG secs=30.0 match=no`, n8 `clean=PASS match=no` (policy row), `SUMMARY rows=16 mismatches=9 errors=0 hangs=8`, `EXIT=1`.
- Controls stay red: K-b `mismatches=7 hangs=0` EXIT=1; K-c (M09) `mismatches=11 hangs=8` EXIT=1 with o1/o2 `clean=PASS match=no` (M09 killed, r76 routed defect 3 partly closed); K-d `mismatches=7 hangs=4` EXIT=1.
- After: `records/c1-after.txt` → all 16 `match=yes` (n-rows `class=RECEIPT-NONREGULAR-SOURCE rc=1 secs≤0.1`), `SUMMARY rows=16 mismatches=0 errors=0 hangs=0`, `EXIT=0`, bound gate `28a51355…` = W blob. `records/wave-repair/c1-at-repair.txt` identical with `5d08f547…` = tip blob.
- Regression conjuncts: r76 `SUMMARY rows=30 mismatches=0 errors=0` EXIT=0; r36 `cases=21 pass=21 fail=0 control=STUB-REJECTED` EXIT=0; r27 `cases=4 pass=4 control=FALSE-GREEN-REJECTED` EXIT=0; identical at the repair.
- Repair probes: `repair-probes.txt` `SUMMARY arms=10 as_expected=10` EXIT=0; failed run 1 kept (`attempts/repair-probes-run1.txt` `arms=9 as_expected=8` EXIT=1).
- Domain trial `records/c1-domain-trial.txt`: `check-tip/report/shonen/clean/prereg=PASS`, `EXIT=0`, `rev=adc11389`. Closure re-derived its bindings: `git show a5a18666:census/round-77/probes/domain-trial.sh | sha256sum` = `5f199c54…2e5d` (= receipt); `head -n 131 .ufo/reports/round-77/souji.md | sha256sum` = `6d56f71b…d669` (= receipt `report_sha256`) on both the working file and the committed bytes. r76 routed defects 1-2 closed.
- Source behind the claim (S321) re-opened: `add_patterns` does a blocking `open(fname, O_RDONLY)` before any fstat (lines 1164-1169), and `st` feeds only `size` afterwards — the hang mechanism holds.
- Result: matches the report (9 → 0, hangs 8 → 0, EXIT 1 → 0, K-b/K-c/K-d red, 30/30, 21/21, 4/4, trial PASS).
- Qualifications disclosed and accepted: o1-o3/p1-p4 do not discriminate base from candidate; n8 is a policy row; the 300 s backstop, XDG and relative-path branches have no frozen row; FIFO `.git/config`/`HEAD`/`packed-refs` hang check 1 (out of surface); `wall_seconds=` empty because `bc` is absent. The domain-trial receipt binds only the repaired blob; the W→R amendment's two digests are recorded in the report and the repair receipts, not in the trial receipt.

### C2 — calibration (self-assessment pointer resolution): **improved** (evidence-verified; ledger re-measured)

- Before: `controls/c2-K-a-no-ledger.txt` → `rev=d4f51563…`, `SUMMARY items=35 resolved=0 unresolved=35 refused=0 mismatched=0 errors=0`, `EXIT=1`.
- Forgery controls red: K-b blanket ABSENT `resolved=4 refused=31` EXIT=1; K-c no capture `unresolved=31 refused=4` EXIT=1; K-d stub `mismatched=4` EXIT=1; K-e name-only MOVED `unresolved=32 refused=3` EXIT=1.
- After: `records/c2-after.txt` → `rev=8bf42fc6`, `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0`, `EXIT=0`; `records/c2-pointer-check-after.txt` `SUMMARY files=6 checked=2198 missing=31` (35 − 4 captured).
- Closure re-measurement of the ledger (`git show a5a18666:<target> | sha256sum` vs the population digest column): MOVED P04 P05 P07 P25 P26 P29 P30 P34 P35 → all `match`; P31 directory present (1 file). CAPTURED P09/P10 `.ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py` = `eba4f7e0…586f` (= population); P11/P18 `S64ExecFreeze/` 13 files in tree; capture commit K adds exactly 14 files. TOKEN targets (round-73 `c2-after-D1..D5.txt`, `tools/souji-worktree-drift.py`, round-29 prereg and lesson) all in tree. FLEET targets (`.ufo/state`, `.ufo/watchdog.log`, `.ufo/l0-questions.md`, the souji mint scope file) exist under the fleet root. Ledger class histogram: MOVED 10, FLEET 8, TOKEN 6, ABSENT 3, LOCAL-POLICY 3, QUARANTINED 1 (31 rows) + 4 CAPTURED = 35.
- Result: matches the report (resolved 0 → 35, pointer-check missing 35 → 31, four forgery controls red).
- Qualifications disclosed and accepted: thin (31/35 resolve without a new byte; a mechanical ledger generator reaches 35/35); counter kill power is aggregate-only (6 forged single rows pass: QUARANTINED unbound, TOKEN prefix-only, MOVED location unchecked, R0 unexercised); P15/P16 rest on empty-directory digests. The closure's own target re-checks show the shipped ledger is true row by row, so the predicate holds; the instrument weakness is routed (r78 successor counter), not a falsification.

### Axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 (frozen 16-row counter 9 → 0, hangs 8 → 0; controls red; r76/r36/r27 green; domain trial PASS) |
| calibration | improved | C2 (35 → 35 resolved, forgery controls red, pointer check 35 → 31; ledger re-measured true) |
| coverage | unchanged | `git diff d4f51563 a5a18666 -- SCORECARD.md`: axis scores unchanged (calibration 7, coverage 8, operability 8); two capability rows added, r77 measurements block and r78 plan appended; no row rewritten |

No axis harmed.

## Discernment spot-check (`corpus/lessons/round-77.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S321 git dir.c `add_patterns` v2.56.0 | admit (A, mined) | `curl https://raw.githubusercontent.com/git/git/v2.56.0/dir.c` → HTTP 200, 115474 bytes, sha256 `53e5ed2b…20a6` (= row); lines 1164-1167 verbatim | agree | primary code at a pinned tag; quote exact (13 words ≤25); grounds C1's hang mechanism; tier A, kind code correct |
| S322 git-add(1) `--force` v2.56.0 | admit (A, mined) | `curl …/v2.56.0/Documentation/git-add.adoc` → HTTP 200, 16586 bytes, sha256 `42089b80…65db` (= row); line 78 "Allow adding otherwise ignored files." | agree | official docs at a pinned tag; quote exact (5 words); supports the C2 capture of ignored files at their path |
| dir.c line 1169 anchor | reject (quote) | same dir.c capture, line 1169 `if (fd < 0 \|\| fstat(fd, &st) < 0) {` | agree | the `\|\|` would split the 11-column registry row; paraphrase instead of quote is the right call |

SOURCES re-open: S322 row (`grep -nE '^\| *S322 ' corpus/SOURCES.md`) quote column is the 5-word line 78 text, located by file and line — matches the fetched bytes. Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 86 W04 (all pre-existing duplicate-URL warnings), EXIT=0; rows `grep -cE '^ {0,3}\| *S[0-9]{3,}'` 243 (base) → 245 (now).

## Trend verdicts

- **expansion: improved** — two mined tier-A rows on ground the lane did not hold (S321 how git opens exclude files; S322 committing ignored files at their path), a new knowledge entry `corpus/knowledge/self-assessment-pointer-resolution.md` (+60 lines, cites S322) and an r77 section in `filter-filemode-witness.md` (+41, cites S321); QUALITY Q138/Q139; two capability rows, each demonstrated by a receipt above.
- **quality: improved** — the gate's seven wave-found defects were repaired with W-vs-R probes that can fail (run 1 at 8/9 kept), frozen counters stay at 0 at the repair; S321/S322 re-opened by a non-L1 seat before landing with two corrections applied; S064 anchor drift recorded and routed rather than left unmarked. No admitted entry failed the closure's re-check.
- **discernment: improved** — the closure agrees with the gate on both admits and the reject; the lane recorded its own instrument and expectation errors (M2, M3, M5) and accepted critics' thin-C2 and aggregate-red findings as qualifications.

## Routed defects (lane fixes next round)

1. Correction not swept (PROTOCOL §Evidence standard, "Corrections sweep every mention"): S77ScoutSources' accepted correction says `add_patterns` never tests the file type (fstat feeds the size only), yet "the fstat type read follows at line 1169" still stands in the S321 row's anchor cell (`corpus/SOURCES.md:280`) and in `corpus/lessons/round-77.md` `## Gate`. Reword both (append-only correction for the lesson).
2. C2 counter kill power: six forged single ledger rows pass the frozen counter (QUARANTINED unbound, TOKEN prefix-only, MOVED location unchecked, R0 unexercised) — carry until the r78 successor counter with per-row forged-ledger expectations lands.
3. C1 out-of-surface hangs: FIFO `.git/config`, `include.path`, `HEAD`, `packed-refs`, `config.worktree` hang check 1 before the pre-check; SIGTERM leaves check-4 children running (S77ExecEvade, S77Sentinel MEDIUM-2/3). The 300 s backstop, XDG and relative-path branches have no frozen row.
4. Domain-trial script calls `bc`, absent on this host, so `wall_seconds=` is empty; and the trial receipt binds only the repaired gate blob — print the amendment (`28a51355… -> 5d08f547…`) in the receipt itself, as r76's did.
5. Carried from r76: K03/K04 tally kill power and the filename-separable r76 C2 population; status-trusting tools `tools/souji-verify.sh:550,594` and `souji-census.sh` (lane r77 lesson (b)/(c), routed r78).

SHONEN: all four boxes `[~]` with pointers a non-author can check (SKILL gate rows at `e104ef24`, LOG "## Round 77" with the domain trial, seats reproducing prereg commands, PROVINCE/adjacency notes). Promotion is operator-owned; noted for the operator only.
