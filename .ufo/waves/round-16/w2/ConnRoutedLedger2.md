# ConnRoutedLedger2 — final R1–R7 discharge ledger

Seat: `SoujiR16.ConnRoutedLedger2-4` (connector, leaf). Judged on calibration. Advisory; L1 integrates.
Scope: for each r15 routed defect R1–R7 (`corpus/lessons/round-15-verifier-spotcheck.md:122–131`) name the
artifact **committed at HEAD** that discharges it, or the honest residual. The r14 routed defects 1–5 that
the wave-1 ledger also tracked are carried in a short closing table.

## Measured base and drift

| fact | value |
|---|---|
| HEAD at assignment | `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` |
| HEAD observed for this ledger | `163158a706352f1c0ee3521c4da2e5289970db57` (moved mid-seat; commit subject "round-16: lesson, sources S043-S050, Q25/Q26, LOG correction and entries, SCORECARD, SKILL, README") |
| commit chain measured | `163158a → a6ec781 → 7a79dc2 → c6207bd → 0a70bef → cbf688a → b410186` |
| census bytes | `tools/souji-census.sh` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, 1877 lines; worktree bytes equal HEAD bytes; `bash -n` rc 0, `shellcheck -S warning` rc 0 (measured this seat) |
| round-16 wave tree | 69 committed paths under `.ufo/waves/round-16/` (63 `*.md`), including `w1/*`, `w1-spec.json`, `w1-dispatch.json`, `w2-spec.json`, `w2-dispatch.json`, `w2-dispatch-attempts.txt` |
| round reports | **zero committed paths** under `.ufo/reports` in this repository; `.ufo/reports/round-16/` does not exist |

Consequence: every claim below is resolved against `163158a`. A later commit may supersede it; the seat
does not own any lane file, so it cannot pin it.

## Axes

Calibration (judged), with operability and provenance read as effects. One bounded move is proposed at the
end; it improves calibration only and changes no runtime artifact.

## Ledger

| # | r15 routed defect (short) | committed artifact at HEAD | verdict |
|---|---|---|---|
| R1 | restore a parsing census; red-before/green-after; LOG correction + mention sweep | `tools/souji-census.sh` `64a60fd0…` at `0a70bef`; `census/round-16/c1-matrix-landing.json`; `LOG.md:817,836`; `SKILL.md:18,139,171`; `SCORECARD.md:15`; `corpus/README.md:191`; `corpus/lessons/round-16.md:63` | **holds**, with a documented historical exemption (`partial` on the literal r15-lesson/report rewrite) |
| R2 | r14 value-blind benign-config harm is admission-blocking | `census/round-16/c1-matrix-landing.json` (fixture `27474396…`), `tests/fixtures/r15-preservation-frozen/record.json`, `census/round-16/live-fleet-final.json`; `corpus/lessons/round-16.md:20`; `corpus/QUALITY.md` Q22/Q25 | **holds** behaviorally; **partial** on the claim surface (`LOG.md:840` overbroad; `SKILL.md:149` points at a superseded matrix) |
| R3 | carry the seat-reported known failure verbatim into report **and** lesson | lesson half committed: `corpus/lessons/round-16.md:39,43–61`; report half absent | **partial** |
| R4 | re-pin r15 frozen pins and record the frozen verdict with measured revision | `tests/fixtures/r15-preservation-frozen/expected.json`, `record.json`, `regenerate.py`; §R4 below | **holds** (mechanically reproduced from committed bytes) |
| R5 | enforce the seat no-probe rule, don't just record it | `tools/souji-seat-audit.py`; `census/round-16/seat-audit-w1.json`; `corpus/lessons/round-16.md:70`; `corpus/QUALITY.md` Q26 | **partial** (major write-violation voiding not stated per Q26) |
| R6 | explicit cross-domain evidence line (D2) | material committed at `.ufo/waves/round-16/w1/SiblingOverlap.md:39`; no round report at HEAD; `LOG.md:879` asserts it is "in the report" | **partial** |
| R7 | `rejected` registry row for git-status(1) | `corpus/SOURCES.md:58` (S044, 11 cells, `rejected`), `corpus/SOURCES.md:56` (S042 used-by), `corpus/lessons/round-16.md:27` | **holds**; one adjacent residual in S042 |

---

## R1 — parse restore, red/green, LOG correction, mention sweep

**Discharge (committed bytes).**
- Parse restore is committed at `0a70bef`; the bytes are unchanged at HEAD (sha256 above, measured). The
  worktree copy equals HEAD, `bash -n` exits 0, `shellcheck -S warning` exits 0 (measured this seat).
- Red-before/green-after is committed at `census/round-16/c1-matrix-landing.json`, measured at
  `lane_head=7a79dc2…` with `fixtures_sha256.r15-config=27474396…` (the HEAD fixture): `changed` 20/20
  pass, `r14-namespace` 12/12, `bash_n` rc 0, `shellcheck_warning` rc 0; `r15-baseline` (`b410186`)
  `bash_n` rc 2 and 20/20 cases fail; `r14-harm` (`cc21683`) 16/20 fail; `pre-harm` (`a31642d`) 8/20 fail.
  `census/round-16/c1-matrix-final.json` is the earlier run at `lane_head=0a70bef` (see R2 residual).
- LOG correction is committed at `LOG.md:817` ("round 16 correction: round 15 landed a census that does
  not parse"), naming rc 2 at line 1368 and the `b410186` bytes; the round-16 C1/C2 entry is `LOG.md:836`.
- Mention sweep is committed in the current-state surfaces: `SKILL.md:18` (round-15 correction note),
  `SKILL.md:139` (census registry row, now "usage/malformed baseline/protected-path refusal"),
  `SKILL.md:171` (census bullet), `SCORECARD.md:15` (operability row, explicitly retracts "numeric delta 0"),
  `corpus/README.md:191` (round-16 correction to the r15 section).

**Residual (partial on the literal instruction).** The routed text says "Sweep ... the r15 lesson and report
wording". The r16 lesson explicitly declines the rewrite: `corpus/lessons/round-16.md:63–65` says r15 lesson
lines 94–101 and `.ufo/reports/round-15/souji.md` "are historical and not rewritten"; `git diff b410186 HEAD
-- corpus/lessons/round-15.md` is empty, and the r15 lesson still says "unverified candidate"
(`corpus/lessons/round-15.md:94–95`). This is consistent with the lane's own norm that corrections are new
entries, never rewrites (`LOG.md:31–32`), and the exemption is disclosed rather than hidden, so the
substance of R1 holds. The discoverability cost is real: a reader who opens only the r15 lesson sees the
understatement with no pointer forward.
Smallest fix: append one correction-pointer line to `corpus/lessons/round-15.md` (a new entry, not a
rewrite), or accept the documented exemption explicitly in the final report.

## R2 — value-blind benign-config harm

**Discharge (committed evidence; recomputed from committed bytes).**
- `census/round-16/c1-matrix-landing.json` is bound to the HEAD fixture (`27474396…`) and records:
  changed 20/20, r14 namespace 12/12, `bash_n` 0, `shellcheck_warning` 0; `r14-harm` 16/20 fail;
  `pre-harm` 8/20 fail; `r15-baseline` 20/20 fail with `bash_n` 2.
- I recomputed the class partition from `tests/fixtures/r15-preservation-frozen/record.json` (the
  `c6207bd` record, same fixture) plus `CASE_CLASSES`/`HARM_CASES` at HEAD
  (`tests/fixtures/r15-census-config.py:161–179`): changed benign 10/10, degrade 1/1, preserve 3/3,
  refusal 4/4, safety 2/2; `r14-harm` fails all 15 HARM_CASES ids **plus** `R15CFG-19` (16), benign 0/10;
  `pre-harm` fails exactly `02,03,08,11,14,17,18,19` (the lesson's list, `corpus/lessons/round-16.md:20`),
  benign 10/10. The lesson's "fails all 15 HARM_CASES ids plus 19" is exact.
- Live fleet: `census/round-16/live-fleet-final.json` has 21 rows per arm and
  `rows_identical_excluding_mtime: true`; its own `note` limits the claim to preservation of live rows
  (no live repo carried an r14-refused key), which the lesson states. No overclaim there.

**Defect F1 (committed claim surface, calibration).** `LOG.md:840–841` says "only a config-named path
overlapping a protected root keeps the whole-run exit 2". That is falsified by the tool's own contract,
`tools/souji-census.sh:132–134` ("2 usage, malformed baseline, or protected-path refusal"), and by
`tests/fixtures/r15-census-config.py:153` (`R15CFG-20` malformed baseline, rc 2). The same overbreadth was
already flagged pre-integration by a committed seat: `.ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md:295`
("C1's 'only a protected-namespace reach keeps whole-run exit 2' is contradicted by `usage_err` and by
non-namespace `protected_fail` classes"). The lesson avoided the sentence (`corpus/lessons/round-16.md` has
no "whole-run") and `SKILL.md:139` is correctly scoped, so the defect is isolated to the LOG entry.
Smallest fix: scope `LOG.md:840` to config outcomes, or enumerate all exit-2 causes as the tool header does.

**Defect F2 (stale pointer, low severity).** `SKILL.md:149` names `census/round-16/c1-matrix-final.json`
as the observed path, but that artifact pins `fixtures_sha256.r15-config=85de2a43…` while HEAD's fixture is
`27474396…`; it is a superseded measurement at `lane_head=0a70bef`. The HEAD-bound run is
`census/round-16/c1-matrix-landing.json` (all four arms, fixture `27474396…`). A non-author following the
SKILL pin path measures a fixture revision that is not committed. Smallest fix: point the row at
`c1-matrix-landing.json`, or mark `c1-matrix-final.json` superseded in the row and in the lesson citation.

Outside acceptance remains pending by design (author verdict, not admission); that is not a defect.

## R3 — seat-reported known failure into report and lesson, verbatim

**Discharge (lesson half, committed).** `corpus/lessons/round-16.md:39` opens
`## Seat-reported failures`; `:43–54` carry 12 round-16 seat lines and `:58–61` carry four round-15 lines
including `ConfigRepair.md:7` and `ConfigRepair.md:9–13`. I verified mechanically (normalized whole-line
substring against each committed report line) that all 12 round-16 quotes are verbatim, and that the two
retained `ConfigRepair.md:9–13` spans are verbatim substrings of the committed block:
"`bash -n` reports: `line 1368: syntax error near unexpected token '}'`" and "**The file in tree does NOT
parse.** L1 must either complete the repair or revert to `cc21683` before any acceptance run; do not ship
this state as working." The `AdmissionChecker.md:73–75` carry is also present verbatim-in-substance.

**Residuals (partial).**
1. **Report half absent.** The routed defect requires the L1 report as well; this repository has zero
   tracked paths under `.ufo/reports` at HEAD, and `.ufo/reports/round-16/` does not exist. Nothing
   committed discharges the report half.
2. **The block is not whole-line verbatim.** `ConfigRepair.md:9–13` is reproduced as two verbatim spans
   joined by a marked `…`; the parenthetical "(the `}` closing `list_repos`). Edits were in flight when the
   operator wrap-up halted work." is omitted. The failure and its remedy survive intact, but a strict
   "verbatim 7–13" reading is not met.
3. **No mechanical guard for the r15→r16 carry.** `check_carry` scans `.ufo/waves/round-N/` against
   `corpus/lessons/round-N.md` (`tools/souji-landing-gate.py:306–352`); the round-16 scan sees only the one
   round-16 channel marker (below), and the r15 carry is outside its universe. The gate that proves R1/R2
   cannot prove R3.

Smallest fix: commit the round report with the 7–13 block pasted verbatim (or de-elide the lesson), and
either add a `--carry-from ROUND` input to the gate or state in the lesson that the r15 carry is manual and
by inspection only.

## R4 — re-pin r15 frozen pins and record measured revision

**Discharge (mechanically reproduced from committed bytes).**
- `tests/fixtures/r15-preservation-frozen/expected.json` pins `tools/souji-census.sh` at
  `64a60fd0…`, `tests/fixtures/r15-census-config.py` at `27474396…`, `tests/fixtures/r14-census-boundary.py`
  at `e6a984b1…`; all three equal the HEAD blobs (measured). `record_sha256=173db777…` equals the HEAD
  `record.json` bytes (measured).
- `record.json` records `measured_commit=c6207bd…`; at `c6207bd` the three pinned files hash to exactly the
  pinned digests (measured), so `LG-FROZEN-MEASURED` would be empty and the declared verdict `clean` is
  mechanically coherent at HEAD.
- `record.json` carries all three arms at the pinned fixture: `baseline_preharm` (`a31642d`, 8/20 fail),
  `baseline` (`cc21683`, 16/20 fail), `changed` (`c6207bd`, 0/20 fail), each with full stdout and a tool
  sha256.
- `tests/fixtures/r15-preservation-frozen/regenerate.py` is committed and binds runs to a revision
  (item `RevengeFrozenPin`). Caveat: `record.json` declares `declared_consistency_only: true`; no captured
  `--frozen` stdout is committed. The verdict is declared consistency, which is exactly what the record
  says it is; it is not re-executed by this seat (no `ALLOWED-EXEC` in this item).

**Verdict: holds.** The r15 pin defect (bytes no commit held, measured_commit holding different bytes) is
gone: pin → committed bytes, measured_commit → the bytes the record pins.

## R5 — enforce the seat no-probe rule

**Discharge (committed).** `tools/souji-seat-audit.py` is committed; `census/round-16/seat-audit-w1.json`
records `seats_audited=65`, `calls=3173`, `major=1`, `minor=19`, `missing_transcripts=[]`, with per-seat
violations. The tool's selftest has 19 table cases plus a wave-summary check = 20 executed (count-verified
from source; not executed here). `corpus/lessons/round-16.md:70` names the counts, the major seat
(`SrcGitNoLazyFetch`, attempted out-of-scope write; file absent), all 12 minor seats, the voiding rule, and
L1's re-derivation of S046/S049. `corpus/QUALITY.md` Q26 now states the transcript-audited rule and its
lower-bound limit.

**Residual (partial).** Q26's rule is explicit: "an executing or writing violation voids the seat's
evidence". The lesson's disposition sentence applies voiding to "read-only out-of-class commands" and then
records that L1 re-derived S046/S049; it never states that the one **major, writing** violation voids
`SrcGitNoLazyFetch`'s evidence. The re-derivation of S049 (that seat's row) implies it, but the committed
adjudication text does not say it. Under the round's own criterion this is an enforcement-statement gap,
not a detector gap.
Smallest fix: add one sentence to `corpus/lessons/round-16.md:70`: "`SrcGitNoLazyFetch`: attempted write →
evidence voided per Q26; S049 re-derived by L1."

## R6 — explicit cross-domain evidence line

**Material (committed).** `.ufo/waves/round-16/w1/SiblingOverlap.md:39` is a single 821-character
`CROSS-DOMAIN:` line naming the split ownership (tameshi pin classification, kumitate `round-gate.mjs` at
rev `364f1d5…`/blob `f890e277…`, souji's own gate reading pins via `git show <rev>:<path>`) with exact
paths and revisions. The same report lists the second-order risks (name proximity, pin resolution,
ledger absorption, per-detector provenance).

**Residual (partial).** The routed defect is a line in the round report (D2 report contract), and no round
report is committed at HEAD. `LOG.md:879` states "R6 cross-domain line ... are in the report"; at HEAD that
is true only if "report" means the wave-1 seat report, which is not the artifact the routing names. This is
a forward reference in a committed LOG entry.
Smallest fix: paste the `SiblingOverlap.md:39` line into the round report when it lands; meanwhile reword
the LOG sentence to "drafted in SiblingOverlap.md (wave 1); round report pending".

## R7 — `rejected` registry row for git-status(1)

**Discharge (committed).** `corpus/SOURCES.md:58` is S044: git-status(1), docs, tier A, status `rejected`,
11 cells, scope "porcelain output stability and status display/performance config, not which config values
abort or neutralize a command", anchor with the accessed version lines ("last updated in 2.53.0",
"2.54.0 → 2.56.0 no changes"), and a flip condition. `corpus/lessons/round-16.md:27` cites it with its
located quote; `corpus/SOURCES.md:56` (S042) now lists `corpus/lessons/round-16.md` in `used-by`. The
registry has 50 rows; S043–S050 are all 11-cell rows. The w1 version-cell conflict was avoided: S044 anchors
the web manual, not an installed-version header.

**Adjacent residual (does not falsify R7).** `corpus/SOURCES.md:56` (S042) still says "installed 2.55.0
corresponding sections"; the committed measurement `census/round-16/c1-matrix-landing.json` records
`git_version="git version 2.56.0"`, and `.ufo/waves/round-16/w1/ScoutGitHostVersion.md:124` says the
"installed 2.55" premise is false (pacman 2.56.0-1). Two committed seats flagged the same stale anchor
(`SrcGitStatusRejected.md:66`, `SrcGitConfigIncludesRecheck.md:295`). The lesson states "no other existing
cell changed", so Contradiction E from the wave-1 ledger was avoided, not resolved.
Smallest fix: correct S042's installed-version phrase to 2.56.0 (or drop the installed claim and keep the
web-manual anchor), citing the committed `git_version`.

---

## Cross-cutting calibration checks (what the ledger relied on)

1. **Q25(c) at HEAD passes by construction, but narrowly.** Static replication of
   `tools/souji-landing-gate.py:235–352` over the 63 committed round-16 `*.md` reports finds exactly **one**
   failure-channel marker: `.ufo/waves/round-16/w1/ConnLogConvention.md:385`
   (`## STATUS: INCOMPLETE — file has an unresolved syntax error`, a quotation of the r15 line), and the
   lesson carries it verbatim at `corpus/lessons/round-16.md:43` (the carry line ends `resolved@0a70bef`).
   A first replication pass used a stricter parenthesized carry token and reported the marker uncarried;
   that is not the gate's rule. With the gate's exact `CARRY_TOKEN_RE`
   (`\bopen\b|resolved@[0-9a-f]{7,}`) the result is 0 uncarried over 63 reports and 1 marker. No
   `admitted: true` marker exists, so
   `LG-OPEN-ADMITTED` is empty. The gate's `SUMMARY` now prints `checked_reg/checked_pins/checked_markers/
   checked_reports` (`tools/souji-landing-gate.py:600`), and `check_carry` raises could-not-evaluate on an
   absent wave dir (`:306–315`), so the w1 empty-universe false-green is closed. The caveat: the 12 lines
   the lesson carries are a superset of the channel; the gate would not have caught 11 of them (their first
   value word is outside the pinned vocabulary), so the lesson's parenthetical "every non-ok STATUS line
   that reports a defect" is a human standard, not a gated one.
2. **The b410186 replay's "5 findings" is arithmetically correct.** Static replication of the gate checks at
   `b410186` gives: 1 `LG-PARSE-REG` (census `bash -n` rc 2); 1 `LG-FROZEN-PIN` (census pinned to
   `b5187351…`, actual `dab4122c…`; the r15 fixture and record pins match at `b410186`); 2
   `LG-FROZEN-MEASURED` (census at `fc3a8d4` hashes `fcff8b05…`; the r15 fixture is absent at `fc3a8d4`);
   1 `LG-SEAT-UNCARRIED` (the only r15 channel marker, `ConfigRepair.md:7`, uncarried in
   `corpus/lessons/round-15.md`). Total 5, matching `corpus/lessons/round-16.md:21` and `SCORECARD.md:14`.
   This is replication of the committed checks, not a gate run.
3. **Claimed test counts are structurally consistent.** Gate selftest: 15 `check(...)` calls + 3 manual
   result checks = 18. Held-out fixture: 14 `case(...)` calls + the in-fixture `vacuity-stub` = 15. Audit
   selftest: 19 table cases + 1 wave-summary = 20. None was executed by this seat (no `ALLOWED-EXEC`).

## r14 routed defects 1–5 (carried, one line each)

| # | status at HEAD |
|---|---|
| 1 benign-config repair without namespace weakening | same artifacts as R2: namespace 12/12 on changed and on r14-harm (landing matrix), benign 10/10 changed vs 0/10 r14-harm; acceptance pending |
| 2 mine the outside disagreement into lesson + criterion | discharged r15: `corpus/lessons/round-15.md:9–11`, `corpus/QUALITY.md` Q22–Q24; carried |
| 3 capability wording matches exercised boundary | `SKILL.md:15–22` keeps "outside admission pending"; no upgrade in the r16 lesson; holds |
| 4 enforce the mid-flight probe prohibition | same as R5: detector/audit committed, major-write voiding statement missing → partial |
| 5 retain original observations, no cache relabelling | landing matrix binds each arm to `rev` + `sha256`, frozen record binds `tool.commit`/`tool.sha256` per run; holds |

## Proposed move (one, bounded)

Before the round report is committed, land the four smallest edits that close the residuals without touching
runtime behavior: (1) scope `LOG.md:840` or enumerate the exit-2 causes as `tools/souji-census.sh:134` does;
(2) point `SKILL.md:149` at `census/round-16/c1-matrix-landing.json` (or mark `c1-matrix-final.json`
superseded in both SKILL and lesson); (3) add the Q26 writing-violation/voiding sentence for
`SrcGitNoLazyFetch` to `corpus/lessons/round-16.md:70`; (4) paste the `SiblingOverlap.md:39` CROSS-DOMAIN
line and the `ConfigRepair.md:7–13` block into the round report when it exists, and reword `LOG.md:879`
until it does.

Axes: **calibration improves** (four committed claim/carry mismatches removed, all with existing evidence);
operability, coverage, depth, freshness and adjacency are unchanged. Risks: edits are a new integration
commit, not a rewrite; R3/R6 remain partial until a report artifact is committed in this repository, no
matter how good the lesson is.

## Limits of this seat

No item-level `ALLOWED-EXEC` was supplied, so this seat **did not execute** the landing gate, its fixture,
the preservation checker, the seat audit, the matrix runner, or the census. Behavioral claims are either
committed artifacts parsed here, or a static replication of the gate's own checks against committed blobs
(labeled as such). `bash -n` and `shellcheck` were run on named files only, as the contract permits.
No tool installs or updates. No lane file was modified; this report is the only write.

## Probe-rule disclosure

Read-only. To replicate the gate's checks I read committed blobs under `.ufo/waves/round-16/` (69 paths) and
`.ufo/waves/round-15/` (64 `*.md` at `b410186`) via `git ls-tree` + `git show` per enumerated path — no
`find`, no recursive `grep`, no lane-root listing. `census/operator-sweep-20261019/`, `.ufo/state`,
`.ufo/watchdog.log`, `MANIFEST.json`, `~/.omp` beyond the rules file, and sibling lanes were not touched.
Own report only; no commits, no `git add/stash/reset/checkout`.

STATUS: ok — ledger complete; six committed-artifact claim/carry defects named with file:line and smallest
fix, R1/R2/R4/R7 substantively discharged at `163158a`, R3/R5/R6 partial with stated residuals. No check run
by this seat failed.

## Commands

```bash
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ 2>&1; echo ---; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ 2>&1
ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ | sort
python3 -c "
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2-spec.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
print(json.dumps(d, indent=1)[:3000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -o '"[^"]*R[1-7][^"]*"' .ufo/waves/round-16/w2-dispatch.json | sort -u | head -60; echo ===; python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w2-dispatch.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== census bytes ==" && git show HEAD:tools/souji-census.sh | sha256sum && echo "== census lines ==" && git show HEAD:tools/souji-census.sh | wc -l && echo "== bash -n ==" && git show HEAD:tools/souji-census.sh > /var/tmp/r16-led2-census.sh && bash -n /var/tmp/r16-led2-census.sh; echo "bash_n_rc=$?"; rm -f /var/tmp/r16-led2-census.sh; echo "== 0a70bef stat ==" && git show --stat --oneline 0a70bef | head -20; echo "== c6207bd stat ==" && git show --stat --oneline c6207bd | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== HEAD ==" && git rev-parse HEAD && echo "== log ==" && git log --oneline -25 && echo "== tracked round-16/reports/tools ==" && git ls-tree -r --name-only HEAD -- census/round-16 tools .ufo/reports/round-16 corpus/lessons | sort
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== frozen expected ==" && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json | head -60 && echo "== frozen record ==" && git show HEAD:tests/fixtures/r15-preservation-frozen/record.json | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== r15 spotcheck 118-136 ==" && git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | sed -n '118,136p' && echo "== r14 spotcheck 154-170 ==" && git show HEAD:corpus/lessons/round-14-verifier-spotcheck.md | sed -n '154,170p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== waves committed ==" && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | wc -l && git ls-tree -r --name-only HEAD -- .ufo/waves/round-15 | wc -l && echo "== reports committed ==" && git ls-tree -r --name-only HEAD -- .ufo/reports | head -20 && echo "== LOG round16 ==" && git show HEAD:LOG.md | grep -nEi 'round[- ]16|non-parsing|does not parse|correction' | tail -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SOURCES rows ==" && git show HEAD:corpus/SOURCES.md | grep -cE '^\|\s*S[0-9]{3,}\s*\|' && echo "== S043+ ==" && git show HEAD:corpus/SOURCES.md | grep -nE '^\|\s*S0(4[3-9]|5[0-9])\s*\|' | cut -c1-220 && echo "== git-status row ==" && git show HEAD:corpus/SOURCES.md | grep -niE 'git-status' | cut -c1-220 && echo "== rejected rows ==" && git show HEAD:corpus/SOURCES.md | grep -nE '\|\s*rejected\s*\|' | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== HEAD fixture ==" && git show HEAD:tests/fixtures/r15-census-config.py | sha256sum && echo "== HEAD r14 fixture ==" && git show HEAD:tests/fixtures/r14-census-boundary.py | sha256sum && echo "== HEAD record/expected ==" && git show HEAD:tests/fixtures/r15-preservation-frozen/record.json | sha256sum && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json | sha256sum && echo "== c6207bd census/fixture ==" && git show c6207bd:tools/souji-census.sh | sha256sum && git show c6207bd:tests/fixtures/r15-census-config.py | sha256sum && echo "== fixture changed after c6207bd? ==" && git diff --stat c6207bd..HEAD -- tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== committed round16 wave files ==" && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | sed -n '1,80p' && echo "== build dir? ==" && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16/build | wc -l
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== LOG 770-830 ==" && git show HEAD:LOG.md | sed -n '768,830p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== worktree SOURCES S043-S050 ==" && grep -nE '^\|\s*S0(4[3-9]|5[0-2])\s*\|' corpus/SOURCES.md | cut -c1-260; echo "== worktree row count ==" && grep -cE '^\|\s*S[0-9]{3,}\s*\|' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== 7a79dc2 stat ==" && git show --stat --oneline 7a79dc2 | head -90 && echo "== a6ec781 stat ==" && git show --stat --oneline a6ec781 | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== docs diff b410186..HEAD ==" && git diff --stat b410186..HEAD -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md corpus/lessons/round-15-verifier-spotcheck.md corpus/SOURCES.md && echo "== sk203 lines ==" && git show HEAD:SKILL.md | sed -n '130,175p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print("keys:", list(r))
for k,v in r.items():
    if k in ('fixture','namespace_controls','cases','config_cases','argv'): continue
    print(k,"=",str(v)[:200])
for k in ('config_cases','cases','namespace_controls'):
    v=r.get(k)
    if isinstance(v,dict):
        print(k,"keys:",list(v)[:10])
        print("  argv:",str(v.get('argv'))[:160])
        cs=v.get('cases',[])
        print("  cases:",len(cs),"statuses:",{s:sum(1 for c in cs if c.get('status')==s) for s in set(c.get('status') for c in cs)})
    elif isinstance(v,list):
        print(k,"list:",len(v),"statuses:",{s:sum(1 for c in v if c.get('status')==s) for s in set(c.get('status') for c in v)})
PY
echo "== record tail ==" && git show HEAD:tests/fixtures/r15-preservation-frozen/record.json | tail -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
a=json.load(open('census/round-16/seat-audit-w1.json'))
print("keys:", list(a))
for k,v in a.items():
    s=json.dumps(v) if isinstance(v,(dict,list)) else str(v)
    print("--",k,":",s[:400])
PY
echo "== c1 final summary ==" && python3 - <<'PY'
import json
m=json.load(open('census/round-16/c1-matrix-final.json'))
print("keys:", list(m))
for k,v in m.items():
    if k=='arms': continue
    print(k,"=",str(v)[:300])
for arm,v in m.get('arms',{}).items():
    print("==",arm)
    for kk,vv in v.items():
        if isinstance(vv,dict) and ('total' in vv):
            print("  ",kk,{x:vv.get(x) for x in ('total','failed','rc')})
        elif isinstance(vv,dict) and 'rc' in vv:
            print("  ",kk,"rc=",vv.get('rc'))
        else: print("  ",kk,str(vv)[:100])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== landing matrix params ==" && python3 - <<'PY'
import json
m=json.load(open('census/round-16/c1-matrix-landing.json'))
print({k:m[k] for k in m if k!='arms'})
for arm,v in m['arms'].items():
    print(arm, v.get('rev'), v.get('r15-config',{}).get('total'), v.get('r15-config',{}).get('failed'), v.get('r14-namespace',{}).get('failed'), "bash_n", v.get('bash_n',{}).get('rc') if isinstance(v.get('bash_n'),dict) else v.get('bash_n'))
PY
echo "== HARM/classes names ==" && grep -nE 'HARM|CASE_CLASSES|CLASSES' tests/fixtures/r15-census-config.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/lessons/round-16.md | sed -n '30,75p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== r15 lesson mentions ==" && git show HEAD:corpus/lessons/round-15.md | grep -nEi 'unverified candidate|does not parse|parse|non-parsing|ConfigRepair|48f8945' | cut -c1-240 && echo "== r15 lesson head claims ==" && git show HEAD:corpus/lessons/round-15.md | sed -n '90,105p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== S042 row ==" && git show HEAD:corpus/SOURCES.md | grep -nE '^\|\s*S042\s*\|' && echo "== pipe counts S043-S050 ==" && git show HEAD:corpus/SOURCES.md | awk -F'|' '/^\| S0(4[3-9]|50) /{print $1"|"$2" cells="NF-2}' && echo "== gate selftest check count ==" && git show HEAD:tools/souji-landing-gate.py | grep -cE '^\s+check\(' && echo "== fixture case count ==" && git show HEAD:tests/fixtures/r16-landing-gate.py | grep -cE '^\s+case\(' && git show HEAD:tests/fixtures/r16-landing-gate.py | grep -nE 'def main|CASE|EXPECTED' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | sed -n '235,360p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== QUALITY corrections ==" && git show HEAD:corpus/QUALITY.md | grep -nEi 'sweep every mention|correction' | cut -c1-260 && echo "== Q25 Q26 ==" && git show HEAD:corpus/QUALITY.md | sed -n '56,70p' | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '155,200p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== 163158a cross-domain mentions ==" && git show 163158a | grep -nE '^\+.*[Cc]ross-domain' | cut -c1-240; echo "== SKILL diff ==" && git diff a6ec781 163158a -- SKILL.md | sed -n '1,120p' && echo "== SCORECARD diff ==" && git diff a6ec781 163158a -- SCORECARD.md | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | sed -n '55,110p' && echo "== admitted regex ==" && git show HEAD:tools/souji-landing-gate.py | grep -nE 'ADMITTED_TRUE_RE|CARRY_TOKEN_RE|HEADING_RE|HTML_COMMENT_RE' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json,re
src=open('tests/fixtures/r15-census-config.py').read()
lines=src.splitlines()
harm=set(); cls={}
mode=None
for ln in lines:
    if ln.startswith('HARM_CASES = frozenset({'): mode='harm'; continue
    if ln.startswith('CASE_CLASSES = {'): mode='cls'; continue
    if mode=='harm':
        if ln.strip().startswith('})'): mode=None; continue
        harm.update(re.findall(r'"(R15CFG-\d+)"',ln))
    elif mode=='cls':
        if ln.strip().startswith('}'): mode=None; continue
        for m in re.finditer(r'"(R15CFG-\d+)":\s*"([a-z]+)"',ln): cls[m.group(1)]=m.group(2)
print("harm n=",len(harm),sorted(harm))
rec=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm in ('baseline_preharm','baseline','changed'):
    cases={c['id']:c for c in rec['runs'][arm]['cases']}
    byc={}
    for cid,c in cases.items():
        k=cls.get(cid,'?'); byc.setdefault(k,[0,0]); byc[k][1]+=1
        if c['status']=='pass': byc[k][0]+=1
    fails=sorted(cid for cid,c in cases.items() if c['status']!='pass')
    print(arm, {k:f"{a}/{b}" for k,(a,b) in sorted(byc.items())}, "nfail",len(fails))
    print("   fails:",fails)
    print("   harm_fail",len([f for f in fails if f in harm]),"harm_pass",sorted(set(harm)-set(fails)))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re,unicodedata
def show(p): return subprocess.run(['git','show','HEAD:'+p],capture_output=True,check=True).stdout.decode('utf-8','replace')
STATUS_PREFIX_RE=re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$",re.IGNORECASE)
FAILURE_STATUS_WORDS=frozenset(w.lower() for w in [])
# recover vocabulary from gate source instead of guessing
gs=show('tools/souji-landing-gate.py')
m=re.search(r'FAILURE_STATUS_WORDS = frozenset\((.*?)\)',gs,re.S)
vocab=set(w.lower() for w in re.findall(r'"([A-Za-z]+)"',m.group(1)))
print("vocab:",sorted(vocab))
def status_value(line):
    mm=STATUS_PREFIX_RE.match(line.strip())
    return mm.group(1) if mm else None
def is_failure(line,in_fence,in_table):
    if in_fence or in_table: return False
    v=status_value(line)
    if v is None: return False
    f=re.match(r"[*:—\s]*(\S+)",v)
    w=f.group(1).strip("*:—").lower() if f else ""
    return w in vocab
def scan(text):
    out=[]; fence=False
    for i,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if s.startswith("```"): fence=not fence; continue
        if is_failure(line,fence,s.startswith("|")): out.append((i,line))
    return out
files=subprocess.run(['git','ls-tree','-r','--name-only','HEAD','.ufo/waves/round-16/'],capture_output=True,text=True,check=True).stdout.split()
md=[f for f in files if f.endswith('.md')]
print("reports:",len(md))
total=0; allm=[]
for f in md:
    for ln,raw in scan(show(f)):
        total+=1; allm.append((f,ln,raw))
print("markers:",total)
def norm(t):
    t=unicodedata.normalize("NFC",t).replace("*","").replace("`","")
    return re.sub(r"\s+"," ",t).strip()
lesson=show('corpus/lessons/round-16.md')
HTML_COMMENT_RE=re.compile(r"<!--.*?-->",re.S)
ll=[x for x in HTML_COMMENT_RE.sub("",lesson).splitlines()]
HEADING_RE=re.compile(r"^#{1,6}\s")
FAILURES_HEADING_RE=re.compile(r"^##\s+Seat-reported failures\b",re.IGNORECASE)
carry=[]; inside=False
for x in ll:
    if FAILURES_HEADING_RE.match(x.strip()): inside=True; continue
    if inside and HEADING_RE.match(x.strip()): break
    if inside: carry.append(x)
CARRY_TOKEN_RE=re.compile(r"\((?:open|resolved@[0-9a-f]{7,40})\)")
print("carry lines:",len(carry))
miss=[]
for f,ln,raw in allm:
    needle=norm(raw); ok=False
    for c in carry:
        nl=norm(c)
        if needle and needle in nl and CARRY_TOKEN_RE.search(nl): ok=True; break
    if not ok: miss.append((f,ln,needle))
print("UNCARRIED:",len(miss))
for x in miss: print("  ",x[0],x[1],x[2][:200])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== sweep standard ==" && git show HEAD:SKILL.md | grep -nEi 'sweep every mention|evidence standard' | cut -c1-260; git show HEAD:corpus/QUALITY.md | grep -nEi 'sweep every mention|evidence standard' | cut -c1-260; echo "== lesson admitted true ==" && git show HEAD:corpus/lessons/round-16.md | grep -nE 'admitted:\s*true|admitted: true' | cut -c1-160; echo done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re
def show(p): return subprocess.run(['git','show','HEAD:'+p],capture_output=True,check=True).stdout.decode('utf-8','replace')
files=[f for f in subprocess.run(['git','ls-tree','-r','--name-only','HEAD','.ufo/waves/round-16/'],capture_output=True,text=True,check=True).stdout.split() if f.endswith('.md')]
pat=re.compile(r'STATUS\s*[:—]',re.I)
n=0
for f in files:
    for i,l in enumerate(show(f).splitlines(),1):
        if pat.search(l):
            n+=1
            print(f"{f}:{i}: {l[:220]}")
print("total STATUS lines:",n)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== ConfigRepair 1-16 HEAD ==" && git show HEAD:.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '1,16p' && echo "== 58ace9f ConfigRepair e? ==" && git cat-file -e 58ace9f:.ufo/waves/round-15/w1/ConfigRepair.md && echo present
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== run_selftest ==" && git show HEAD:tools/souji-landing-gate.py | sed -n '748,975p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SCORECARD operability full ==" && git show HEAD:SCORECARD.md | sed -n '15p' && echo "== SKILL corrections standard ==" && git show HEAD:SKILL.md | grep -nEi 'correction|sweep|mention' | head -20 | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SiblingOverlap ==" && git show HEAD:.ufo/waves/round-16/w1/SiblingOverlap.md | sed -n '1,122p' | cut -c1-260
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== README diff ==" && git diff a6ec781 163158a -- corpus/README.md | sed -n '1,60p' && echo "== README sweep mentions ==" && git show HEAD:corpus/README.md | grep -nEi 'sweep every|correction|mention' | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== lesson process full ==" && git show HEAD:corpus/lessons/round-16.md | sed -n '66,76p' && echo "== seat-audit selftest checks ==" && git show HEAD:tools/souji-seat-audit.py | grep -cE 'def case_|self\.check\(|cases\.append|check\(' && git show HEAD:tools/souji-seat-audit.py | grep -nE 'def run_selftest|SELFTEST|cases = |for name' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== live fleet summary ==" && python3 - <<'PY'
import json
d=json.load(open('census/round-16/live-fleet-final.json'))
print("keys:",list(d))
for k,v in d.items():
    if k in ('arms','repos','rows'): print(k,"type",type(v).__name__,len(v) if hasattr(v,'__len__') else '')
    else: print(k,"=",str(v)[:220])
PY
echo "== fixture case names ==" && git show HEAD:tests/fixtures/r16-landing-gate.py | grep -nE 'case\("|cid =|CASES|def main' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-seat-audit.py | grep -nE 'SELFTEST|selftest|CASES|def ' | head -30 && echo "== audit selftest body ==" && git show HEAD:tools/souji-seat-audit.py | sed -n '/def run_selftest/,/return/p' | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== lesson 17-24 ==" && git show HEAD:corpus/lessons/round-16.md | sed -n '17,24p' && echo "== LOG 836-860 ==" && git show HEAD:LOG.md | sed -n '836,862p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('census/round-16/live-fleet-final.json'))
for k,v in d['arms'].items():
    rows=v.get('rows') or v.get('tsv') or []
    print(k,"keys:",list(v)[:10],"rows:",len(rows) if hasattr(rows,'__len__') else rows,"rc:",v.get('rc'),"sha:",v.get('sha256'))
print("identical:",d['rows_identical_excluding_mtime'])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r16-landing-gate.py | sed -n '480,525p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess
t=subprocess.run(['git','show','HEAD:.ufo/waves/round-16/w1/SiblingOverlap.md'],capture_output=True,text=True,check=True).stdout
for i,l in enumerate(t.splitlines(),1):
    if l.startswith('CROSS-DOMAIN'):
        print(i,len(l)); print(l)
print("---")
d=subprocess.run(['git','show','HEAD:.ufo/waves/round-16/w1/DraftR15Correction.md'],capture_output=True,text=True,check=True).stdout
for i,l in enumerate(d.splitlines(),1):
    if 'does NOT parse' in l or 'unresolved syntax error' in l or 'do not ship' in l:
        print(i,l[:300])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess
row=subprocess.run(['git','show','HEAD:SCORECARD.md'],capture_output=True,text=True,check=True).stdout.splitlines()[14]
cells=row.split('|')
for i,c in enumerate(cells):
    print(i, c.strip()[:400])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess
def line(p,n):
    t=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,check=True).stdout.splitlines()
    return t[n-1] if n<=len(t) else '<missing>'
for p,n in [('.ufo/waves/round-16/w1/RevBoundFilters.md',36),('.ufo/waves/round-16/w1/RevIncludeResolve.md',16),('.ufo/waves/round-16/w1/RevStatusInfoFile.md',213),('.ufo/waves/round-16/w1/CriticFixtureOverfit.md',49),('.ufo/waves/round-16/w1/SrcGitNoLazyFetch.md',69),('.ufo/waves/round-16/w1/RevGateSpec.md',226),('.ufo/waves/round-16/w1/SrcGitStatusRejected.md',66),('.ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md',295)]:
    print("\n==",p,n,"==")
    print(line(p,n))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess
t=subprocess.run(['git','show','HEAD:corpus/lessons/round-16.md'],capture_output=True,text=True,check=True).stdout.splitlines()
for n in (69,70,71):
    print(n, len(t[n-1])); print(t[n-1])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== census exit header ==" && git show HEAD:tools/souji-census.sh | sed -n '100,140p' && echo "== fixture case20 ==" && grep -n 'R15CFG-20' tests/fixtures/r15-census-config.py | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== Q25 full ==" && git show HEAD:corpus/QUALITY.md | grep -n 'Q25' && git show HEAD:corpus/QUALITY.md | sed -n '60,66p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re,unicodedata
def show(p): return subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,check=True).stdout
lesson=show('corpus/lessons/round-16.md').splitlines()
def norm(t):
    t=unicodedata.normalize("NFC",t).replace("*","").replace("`","")
    return re.sub(r"\s+"," ",t).strip()
bullets=[l for l in lesson[38:60] if l.startswith('- `') or l.startswith('- .')]
print("bullets:",len(bullets))
bad=[]
for b in bullets:
    m=re.match(r'- `([^`:]+):(\d+)` (.*)',b)
    if not m:
        print("NOMATCH:",b[:120]); continue
    path,ln,rest=m.group(1),int(m.group(2)),m.group(3)
    q=rest.strip()
    if q.startswith('"'):
        end=q.rfind('"')
        quote=q[1:end] if end>0 else q[1:]
    else:
        quote=q.split(' — ')[0].strip('"')
    try:
        raw=show('.ufo/waves/round-16/w1/'+path).splitlines()[ln-1]
    except Exception as e:
        bad.append((path,ln,str(e))); continue
    ok=norm(quote) in norm(raw)
    print(("OK  " if ok else "MISS"),path,ln,"quote_len",len(quote))
    if not ok: bad.append((path,ln,quote[:160],raw[:160]))
print("mismatches:",len(bad))
for x in bad: print(x)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== census exit lines ==" && git show HEAD:tools/souji-census.sh | grep -nE '^#   2 usage|^#   0 census|^#   3 compare|^#   1 selftest' && echo "== ConnLog 380-390 ==" && git show HEAD:.ufo/waves/round-16/w1/ConnLogConvention.md | sed -n '380,392p' && echo "== gate SUMMARY ==" && git show HEAD:tools/souji-landing-gate.py | grep -nE 'SUMMARY' | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess
t=subprocess.run(['git','show','HEAD:corpus/lessons/round-16.md'],capture_output=True,text=True,check=True).stdout.splitlines()
l=t[69]
print("len",len(l)); print("TAIL:",repr(l[-160:]))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== b410186 expected ==" && git show b410186:tests/fixtures/r15-preservation-frozen/expected.json && echo "== b410186 record keys ==" && git show b410186:tests/fixtures/r15-preservation-frozen/record.json | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:d[k] for k in d if k not in ('runs','namespace_controls')})"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | sed -n '360,470p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re,unicodedata
def show(rev,p): return subprocess.run(['git','show',rev+':'+p],capture_output=True,text=True,check=True).stdout
STATUS_PREFIX_RE=re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$",re.IGNORECASE)
vocab={"incomplete","fail","failed","fails","failing","failure","blocked","broken","partial","harmed","red","unrun","error","regression","known"}
def scan(text):
    out=[]; fence=False
    for i,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if s.startswith("```"): fence=not fence; continue
        if fence or s.startswith('|'): continue
        m=STATUS_PREFIX_RE.match(s)
        if not m: continue
        f=re.match(r"[*:—\s]*(\S+)",m.group(1)); w=f.group(1).strip("*:—").lower() if f else ''
        if w in vocab: out.append((i,line))
    return out
files=[f for f in subprocess.run(['git','ls-tree','-r','--name-only','b410186','.ufo/waves/round-15/'],capture_output=True,text=True,check=True).stdout.split() if f.endswith('.md')]
print("r15 reports:",len(files))
tot=0
for f in files:
    for ln,raw in scan(show('b410186',f)):
        tot+=1; print(f"{f}:{ln}: {raw[:200]}")
print("markers:",tot)
lesson=show('b410186','corpus/lessons/round-15.md')
print("lesson has ConfigRepair line:", 'INCOMPLETE — file has an unresolved syntax error' in lesson)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in b410186 fc3a8d4; do echo "== $rev =="; for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json; do printf '%s ' "$p"; git show $rev:$p 2>/dev/null | sha256sum | cut -d' ' -f1; done; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | sed -n '470,520p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re,unicodedata
def show(p): return subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,check=True).stdout
def norm(t):
    t=unicodedata.normalize("NFC",t).replace("*","").replace("`","")
    return re.sub(r"\s+"," ",t).strip()
cr=show('.ufo/waves/round-15/w1/ConfigRepair.md').splitlines()
blk=norm(" ".join(cr[6:13]))
spans=["bash -n reports: `line 1368: syntax error near unexpected token '}'`",
       "**The file in tree does NOT parse.** L1 must either complete the repair or revert to `cc21683` before any acceptance run; do not ship this state as working."]
for s in spans: print("ConfigRepair span ok:", norm(s) in blk, "|", s[:80])
ac=show('.ufo/waves/round-15/w1/AdmissionChecker.md').splitlines()
print("\nAdmissionChecker 73-75:")
for i in (72,73,74): print(i+1, ac[i][:260])
lesson=show('corpus/lessons/round-16.md')
for phrase in ["Frozen fixture ships pre-integration pins", "snapshot_tampered/pinned-mismatch"]:
    print("lesson has:",phrase[:40],"->", phrase in lesson)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== worktree hashes vs HEAD ==" && sha256sum tools/souji-census.sh tests/fixtures/r15-census-config.py && git show HEAD:tools/souji-census.sh | sha256sum && echo "== shellcheck ==" && shellcheck -S warning tools/souji-census.sh; echo "shellcheck_rc=$?"; echo "== 7a79dc2 bytes ==" && git show 7a79dc2:tools/souji-census.sh | sha256sum && git show 7a79dc2:tests/fixtures/r15-census-config.py | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== lesson line index ==" && git show HEAD:corpus/lessons/round-16.md | grep -nE '^## |^### |R16-M[1-6]|ConnLogConvention.md:385|CriticNoHarmPreharm.md:14|SrcGitCheckAttr.md:113|ConfigRepair.md:9-13|AdmissionChecker.md:73-75|Corrections \(R1 sweep\)|Seat audit \(R5' | cut -c1-140 && echo "== LOG anchors ==" && git show HEAD:LOG.md | grep -nE 'round 16 correction|round 16: parsing|R6 cross-domain|R5\.|R4\.' | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SKILL anchors ==" && git show HEAD:SKILL.md | grep -nE 'Round-15 correction \(r16\)|souji-landing-gate|r15-census-config|Repeatable fleet census|r15.*copy did not parse' | cut -c1-180 && echo "== SCORECARD anchors ==" && git show HEAD:SCORECARD.md | grep -nE '^\| (calibration|operability|landing-claim gate|seat transcript audit)' | cut -c1-80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re,unicodedata
def show(p): return subprocess.run(['git','show','HEAD:'+p],capture_output=True,check=True).stdout.decode('utf-8','replace')
gs=show('tools/souji-landing-gate.py')
vocab=set(w.lower() for w in re.findall(r'"([A-Za-z]+)"',re.search(r'FAILURE_STATUS_WORDS = frozenset\((.*?)\)',gs,re.S).group(1)))
STATUS_PREFIX_RE=re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$",re.IGNORECASE)
CARRY_TOKEN_RE=re.compile(r"(?i)\bopen\b|resolved@[0-9a-f]{7,}")
def scan(text):
    out=[]; fence=False
    for i,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if s.startswith("```"): fence=not fence; continue
        if fence or s.startswith('|'): continue
        m=STATUS_PREFIX_RE.match(s)
        if not m: continue
        f=re.match(r"[*:—\s]*(\S+)",m.group(1)); w=f.group(1).strip("*:—").lower() if f else ''
        if w in vocab: out.append((i,line))
    return out
def norm(t):
    t=unicodedata.normalize("NFC",t).replace("*","").replace("`","")
    return re.sub(r"\s+"," ",t).strip()
lesson=show('corpus/lessons/round-16.md')
ll=[x for x in re.sub(r"<!--.*?-->","",lesson,flags=re.S).splitlines()]
carry=[];inside=False
for x in ll:
    if re.match(r"^##\s+Seat-reported failures\b",x.strip(),re.I): inside=True;continue
    if inside and re.match(r"^#{1,6}\s",x.strip()): break
    if inside: carry.append(x)
reports=[f for f in subprocess.run(['git','ls-tree','-r','--name-only','HEAD','.ufo/waves/round-16/'],capture_output=True,text=True,check=True).stdout.split() if f.endswith('.md')]
tot=0;miss=0
for f in reports:
    for ln,raw in scan(show(f)):
        tot+=1; needle=norm(raw); ok=any(needle and needle in norm(c) and CARRY_TOKEN_RE.search(norm(c)) for c in carry)
        print(("CARRIED" if ok else "UNCARRIED"),f,ln)
        miss += 0 if ok else 1
print("reports",len(reports),"markers",tot,"uncarried",miss)
PY
```

Non-shell reads (tool `read` on exact named paths): `skill://godspeed`; none other outside the files named
in the commands above. No `read` of `census/operator-sweep-20261019/`, `.ufo/state`,
`.ufo/watchdog.log`, `MANIFEST.json`, or sibling lanes.
