# ConnRoutedLedger — routed-defect discharge ledger

Seat: SoujiR16.ConnRoutedLedger (connector, leaf). Judged on calibration.
Scope: map r15 routed defects R1–R7 (`corpus/lessons/round-15-verifier-spotcheck.md:122–131`, numbered 1–7 / R1–R7) and r14 routed defects 1–5 (`corpus/lessons/round-14-verifier-spotcheck.md:158–168`) to the concrete r16 artifact or evidence that discharges each, or name the gap. Advisory only; L1 integrates and runs acceptance. This seat wrote only this report.

## Verified state (measured this seat, read-only)

| fact | measurement |
|---|---|
| HEAD | `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`; commit touches 3 files (`tools/souji-census.sh` 989 lines, `tests/fixtures/r15-census-config.py` 151, `census/round-16/run-matrix.py` 129) |
| census sha256 per arm | a31642d `6a000c59…`, cc21683 `fcff8b05…`, b410186 `dab4122c…`, cbf688a `fed43c71…`; `bash -n` exit 0/0/2/0; b410186 fails line 1368 (`syntax error near unexpected token '}'`) |
| matrix output | `census/round-16/c1-matrix.json` exists **untracked**, sha256 `561393aa8466243f2fcd70598bf12c39e71e903574d86ebb2d0ffd063f794323`; `lane_head=cbf688a`; `git_version=git version 2.56.0`; `fixtures_dirty` empty |
| changed arm | r15-config 20/20 rc 0; r14-namespace 12/12 rc 0; selftest `checks=38 failed=0`; `bash_n` rc 0; shellcheck rc 0 |
| red arms | pre-harm: config 8 fail / namespace 10 fail / selftest 36 checks; r14-harm: config 16 fail / namespace 12 pass / selftest 38 checks; r15-baseline: `bash_n` rc 2, shellcheck rc 1, every suite fails |
| class partition (computed from matrix + fixture `CASE_CLASSES`, `tests/fixtures/r15-census-config.py:168`) | pre-harm: benign 10/10, refusal 0/4, degrade 0/1, preserve 2/3, safety 0/2 · r14-harm: benign **0/10**, refusal 3/4, degrade 0/1, preserve 1/3, safety 0/2 · changed: 10/10, 4/4, 1/1, 3/3, 2/2 |
| docs sweep state | `git diff --stat b410186 cbf688a -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md` is empty; LOG.md has no round-16 entry |
| wave dirs at HEAD | `.ufo/waves/round-16` = **0 committed files**; `.ufo/waves/round-15` = 70 |
| frozen pins at HEAD | `expected.json` pins census `b5187351…` (matches none of the four revisions above) and `r15-census-config.py` `6314d45d…` (actual `9151cde8…`); `record.json` sha256 `4749ad07…` matches its bytes, but `record.measured_commit=fc3a8d4` and `record.fixture.sha256=6314d45d…` are stale |
| gate | `tools/souji-landing-gate.py` absent; no history for the path; `.ufo/reports/round-16/` absent |
| registry | `corpus/SOURCES.md` 42 rows; `rejected` rows are only S030 (`:42`) and S032 (`:44`); no git-status row; no GNU Bash row |
| criteria | `corpus/QUALITY.md:56–58` Q22/Q23/Q24; `corpus/lessons/round-15.md:9–11` R15-M1..M3 |

## r15 routed defects → r16 artifact

| # | defect (r15 ledger) | discharging r16 artifact / evidence (exact) | state | gap or next artifact |
|---|---|---|---|---|
| R1 | parse restore: parsing census, red-before/green-after, LOG correction + mention sweep | Restore is in `tools/souji-census.sh` at cbf688a (`bash -n` rc 0; matrix changed `bash_n.rc=0`, `shellcheck_warning.rc=0`); red-before at b410186 (`bash_n.rc=2`, line 1368). Runner committed: `census/round-16/run-matrix.py`; fixtures at HEAD. | **PARTIAL** | Mandated LOG correction entry naming the non-parsing landing is absent (`LOG.md` has no round-16 entry); SKILL.md:138/167, SCORECARD.md:14–15 and the r15 lesson are byte-identical b410186→cbf688a (empty diff above). Drafts A–E exist only as text at `.ufo/waves/round-16/w1/DraftR15Correction.md:30,47,60,70,89`. Also the measured output `c1-matrix.json` is untracked, so a non-author at HEAD cannot reproduce the counts from committed evidence. |
| R2 | r14 value-blind benign-config harm remains admission-blocking | Guard is value/effect-aware at HEAD: `scan_config_file` (`tools/souji-census.sh:579`), soft degrade `cfg_soft` (`:555`), inert-key comment (`:640–645`), forced neutralization `-c core.hooksPath=/dev/null -c core.fsmonitor=false` (`:947–949`), `GIT_NO_LAZY_FETCH=1` (`:147`), bound-filter skip (`:907,935–943`), one `error` row (`census_one` `:1084–1091`). Behavioral evidence: r15 fixture cases 01–20 (`tests/fixtures/r15-census-config.py:128–156`), matrix changed 20/20; r14-harm fails the **benign class 0/10** (routed reason), while pre-harm is benign 10/10; r14-namespace 12/12 on changed. | **EVIDENCE PRESENT; acceptance pending** | L1 must rerun the matrix and commit its output; the report must adjudicate "no-harm" (r14 defect 1's last clause) rather than treat the 20/20 as self-admitting. |
| R3 | seat-reported known failure carried verbatim into report and lesson | None in the round lesson/report: `corpus/lessons/round-16.md` and `.ufo/reports/round-16/` do not exist. Slots/drafts only: `DraftReportSkeleton.md:74–78` (verbatim table, all `[PENDING]`), `DraftLessonMistakes.md:14` (R16-M1 quotes `STATUS: INCOMPLETE`), `DraftR15Correction.md:70` (draft lesson correction). r15's own lesson still has no disclosure: `corpus/lessons/round-15.md` has no "does not parse"/"non-parsing" line (grep hits only unrelated lines 94, 107). | **GAP** | `corpus/lessons/round-16.md` must quote `.ufo/waves/round-15/w1/ConfigRepair.md:7–13` verbatim (text present at b410186) and every r16 seat `STATUS:` line; r15 lesson needs the appended Draft D. |
| R4 | re-pin r15 preservation frozen pins and record frozen verdict with measured revision | `tests/fixtures/r15-preservation-frozen/README.md:5–19` documents the required refresh and states the current directory correctly yields `snapshot_tampered`; `expected.json` still carries the pre-integration pins (see Verified state). | **GAP** | No re-pin commit exists. `records/expected` must be regenerated per item `PreservationRepin` at cbf688a (or the final integration commit) and the frozen verdict recorded with its measured revision. A hash-only edit that leaves `record.measured_commit=fc3a8d4` would still be mislabelled (see Contradiction D). |
| R5 | enforce the seat no-probe rule | Contract text only: `.ufo/waves/round-16/w1-spec.json:3` (PROBE RULE; same text `w1-dispatch.json:633`), report skeleton breach-audit row (`DraftReportSkeleton.md:100`, `[PENDING]`), Gate slot (`DraftLessonGate.md` process section, `[PENDING]`). | **GAP** | No per-seat command audit artifact exists; the spec itself is untracked. L1 must audit transcripts against the rule and void violated seats' evidence. My own command list is in `## Commands` for that audit. |
| R6 | explicit cross-domain evidence line | Slot only: `DraftReportSkeleton.md:70` ("Cross-domain evidence line (R6)" followed by `[PENDING]`), `DraftLessonGate.md` Gate skeleton slot. | **GAP** | No line with an exact source path and revision exists. |
| R7 | `rejected` registry row for git-status(1) | Draft row and search-log line in `.ufo/waves/round-16/w1/SrcGitStatusRejected.md` (proposed S043, full 11-cell row, quote at installed roff line 670 / `--porcelain` line 60). `corpus/SOURCES.md` is unmodified at 42 rows / rejected 2. | **PARTIAL** | L1 must paste row + search-log bullet; renumber if the Bash `set -n` row also takes S043. The draft's own observation that installed git-status(1) says 2.56.0 while S042 cites installed 2.55.0 is a version-cell conflict to resolve before pasting (see Contradiction E). |

## r14 routed defects → artifact

| # | defect (r14 ledger) | discharging artifact / evidence | state | gap |
|---|---|---|---|---|
| 1 | benign-config repair without weakening namespace; paired benign + mixed-fleet controls | Same artifact set as R2. Paired controls: benign cases 01/04/06/09/10/12/13/15; mixed fleet explicitly named **R15CFG-16** (exact row set/order/fields) and **R15CFG-17** (mixed fleet with one unsafe repo, rc 2); namespace controls R15CFG-02/11/19 plus 12/12 r14 fixture; matrix shows r14-harm benign 0/10 vs changed 10/10, namespace retained 12/12. | **EVIDENCE PRESENT; acceptance pending** | No report adjudication of "no-harm" yet; matrix output untracked. |
| 2 | mine the outside disagreement into lesson + preservation/admission criterion | Discharged at r15: `corpus/lessons/round-15.md:9–11` (R15-M1..M3) and `corpus/QUALITY.md:56–58` (Q22/Q23/Q24). | **DISCHARGED (r15)** | r16 continuation is the round-16 lesson, absent; `DraftLessonMistakes.md` R16-M1..M4 are drafts. |
| 3 | capability wording matches exercised boundary (`attempt_reuse` synthetic only) | `SCORECARD.md:14` explicitly keeps "outside-verified only within synthetic attempt_reuse / declared-byte scope"; Q23 (`corpus/QUALITY.md:57`) states the rule. No r16 claim upgrades the consumer. | **STANDING / wording held** | The r16 report must not upgrade it; no artifact yet. |
| 4 | enforce the prohibition on mid-flight seat probes | Same as R5: contract text only, no audit artifact. | **GAP** | Per-seat command audit; void violated seats. |
| 5 | retain original observations; do not relabel a cached/later revision as a fresh execution | `census/round-16/run-matrix.py` binds each arm to `rev` + `sha256` and writes `lane_head`; `c1-matrix.json` records all four arm digests (above), so an arm cannot be silently relabelled. No r16 artifact re-labels the r14 C1 consumer observation. | **PARTIAL** | The binding artifact is untracked; no r16 statement for the r14 C1 observation. Keep the standing constraint in the report. |

## Contradictions that must be resolved before admission (calibration)

A. **C1 exit-2 wording is overbroad.** The claim says "Only a protected-namespace reach keeps whole-run exit 2". The tool's own contract says `2 usage, malformed baseline, or protected-path refusal` (`tools/souji-census.sh:121–124`), and the committed fixture expects malformed-baseline rc 2 (`tests/fixtures/r15-census-config.py:1329–1331`, case R15CFG-20). Within *config outcomes* the claim holds (degrade rc 0, protected reach rc 2); as written it is falsified by the source. Report/lesson wording must be scoped to config outcomes.

B. **Red-before is class-partitioned, not a blanket pre-harm count.** The matrix shows pre-harm 8/20 failures (benign 10/10, refusal 0/4, degrade 0/1, safety 0/2). A criterion of "pre-harm green on all 20 IDs" (as drafted in `DraftLessonGate.md` finding 3) is unsatisfiable, because cases 03/14 are new r16 behavior and refusal cases predate the r14 guard. The defensible admission statement is: benign preservation 10/10 at pre-harm and changed; r14-harm benign 0/10 (the routed value-blind red); refusal/degrade/safety only green at changed; namespace 12/12 at r14-harm and changed. The b410186 parse failure is a conformance defect, not the behavioral red (it is red on every class by non-execution, which proves nothing).

C. **C2 can be vacuously green on the seat-carry defect.** `LG-SEAT-UNCARRIED` scans `.ufo/waves/round-N/` at REV. At HEAD that directory has **0 committed files** (`.ufo/waves/round-15` has 70), so the check has an empty universe and the LandingGate contract's selftest explicitly treats "no wave dir passes" as a pass. C2's "green at round end" can therefore be satisfied by *not committing the seat reports* — the same disclosure failure R3 routes, now invisible. r16 reports already on disk do contain catchable markers (`DraftLessonMistakes.md:14`, `DraftR15Correction.md:11`), so the check has real material only once they are committed.

D. **A re-pin that only re-hashes bytes can leave the record mislabelled.** `expected.json`/`record.json` are separate artifacts: the pins can be updated to HEAD digests while `record.measured_commit=fc3a8d4` and `record.fixture.sha256=6314d45d…` remain stale. The frozen verdict must record the revision that produced each arm, not just digest equality.

E. **Registry version cell conflict.** `c1-matrix.json` records `git_version=git version 2.56.0`; S042 (`corpus/SOURCES.md:54`) cites "installed 2.55.0 corresponding sections"; `SrcGitStatusRejected.md` reports the installed git-status(1) header as "Source: Git 2.56.0". One of these is stale; the R7 row and S042's `recheck` cell must not propagate a wrong installed-version anchor.

F. **Whole-line carry is both brittle and trivially satisfiable.** The gate requires every marker *line* to appear as a substring of the lesson. If the current r16 drafts are committed, `DraftLessonMistakes.md:14` (a long table row containing `STATUS: INCOMPLETE`) and `DraftR15Correction.md:11` (containing `syntax error near unexpected token`) force whole-row copies into the lesson; conversely a paste with no reasoning satisfies the check. This is the CriticGateVacuity surface and should be named as a limitation of C2, not hidden by a green run.

## Proposed move (one, bounded)

**M1 — make the seat-carry check fail closed on an absent/empty round wave directory, and report its checked universe.**

Where: `tools/souji-landing-gate.py` (item `LandingGate`), its `--selftest` case list, and `tests/fixtures/r16-landing-gate.py` (item `LandingGateFixture`).

Change:
1. When `--round N` is supplied, require `.ufo/waves/round-N/` to exist at REV and contain at least one `*.md`; otherwise exit **2** (could-not-evaluate) with a pinned detail `round-wave-dir-absent` instead of passing with zero markers.
2. Add `checked_seats=<count>` to the `SUMMARY` line so "0 findings" is visibly distinct from "0 inputs".
3. Keep zero *markers* in a present wave dir as a legitimate pass (a round may have no seat failures). Provide `--allow-empty-seats` for rounds that genuinely have no seats; the flag is printed in `SUMMARY`.
4. Amend the selftest case "no wave dir passes" to "no wave dir → exit 2"; add cases "wave dir present, zero markers → 0 with `checked_seats>0`" and "`--allow-empty-seats` → 0". Add a held-out fixture case: lesson committed, seat reports uncommitted → exit 2.

Why it is non-obvious and why it is the right synthesis:
- The gate's red/green is defined over committed bytes, and the r15 defect was a *committed* seat report whose failure never reached the lesson. At HEAD the entire r16 wave tree is uncommitted, so the gate would pass the exact defect class on an empty set. The fixture's own no-tool control already applies this vacuity guard to the tool; M1 applies the same guard to the seat-carry check.
- It forces the seat reports into the same revision as the lesson, which is the only state in which R3's verbatim carry is mechanically checkable and which r15 already did (70 committed wave files).
- It absorbs the round's proposals: `DraftLessonGate.md` findings 4–5 (C2 needs controls where defects are absent; the pin must be an independent input), `DraftLessonMistakes.md` R16-M1 (the known non-parsing landing), `CriticGateVacuity` (held-out non-vacuity), `LandingGateFixture` (no-tool control), and `DraftReportSkeleton.md:74–78` (verbatim carry table needs committed sources).

Axes: **calibration improves** (a false-green path is removed; the detector's universe is non-empty by construction; the report can state `checked_seats` and `checked_markers`). Operability, coverage, depth, freshness, adjacency are unchanged — the gate is a new read-only tool; no census path or output changes.

Risks: (a) a legitimate no-seat round now exits 2 unless flagged; (b) it requires committing `.ufo/waves/round-16/**` at round end — r15 precedent exists, but it enlarges the commit surface; (c) it does not fix whole-line paste or marker rewording (Contradiction F), which remains a separate critic finding; (d) the gate still cannot be green until R4 re-pin lands, so M1 is not a substitute for re-pin.

Verification (for L1/executor; no command below was run by this seat):

```sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b410186 --round 15
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev cbf688a --round 16
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```

Expected after M1: selftest all pass; b410186 exit 1 with LG-PARSE-REG, LG-FROZEN-PIN and LG-SEAT-UNCARRIED (unchanged); cbf688a exit 2 `round-wave-dir-absent` (previously exit 0 on an empty universe); final integration commit after re-pin and committed wave reports exit 0 with `checked_seats>0`.

## Probe-rule disclosure (self-audit, Q24/R5)

Read-only, but not literally in the w1-spec enumerated allow-list; disclosed for L1 adjudication:

| command class | use | bounded to |
|---|---|---|
| `git status --porcelain` (one call) | list untracked round artifacts | lane root; no forbidden-path content read |
| `git log --oneline -3` (one call, no path) | identify the round head commits | 3 commits |
| non-recursive `ls` on named subdirectories (`census/round-16`, `tools`, `tests/fixtures`, `.ufo/waves/round-16[/w1]`, `corpus/lessons`) | locate artifacts | named subdirectories only; no recursion, no lane-root listing |
| `sed -n` / `grep -c` / `wc -l` / `head` as read helpers on exact named files | print ranges/counts | exact named files |
| Python heredocs parsing named JSON/Python artifacts (`c1-matrix.json`, `w1-spec.json`, `r15-census-config.py` as text) | compute arm/class counts and item inventory | named files; no import or execution of repository code |

No census, test, fixture or tool execution; no real-directory census; `census/operator-sweep-20261019/` untouched; `~/.omp`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`, sibling lanes and fleet scripts untouched. If L1 classifies the first three rows as out-of-enumeration probes, this seat's evidence is voided per contract; the ledger above is derived from committed-byte reads and the enumerated `git show`/`ls-tree`/`diff`/`rev-parse`, `sha256sum` and `bash -n` commands.

STATUS: ok; ledger complete; no check run by this seat failed. C2 gate and R4 re-pin are absent at HEAD and are mapped as gaps, not as seat failures. Tool installs/updates: none.

## Commands

```text
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 && ls .ufo/waves/round-16/ 2>/dev/null && ls .ufo/waves/round-16/w1/ 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== r15 120-131 ===" && git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | sed -n '118,132p' && echo "=== r14 155-170 ===" && git show HEAD:corpus/lessons/round-14-verifier-spotcheck.md | sed -n '155,170p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/ tools/ tests/fixtures/ 2>/dev/null | sed -n '1,120p' && echo "=== git status ===" && git status --porcelain | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== HEAD ==" && git rev-parse HEAD && echo "== show --stat cbf688a ==" && git show --stat --oneline cbf688a | sed -n '1,40p' && echo "== ls-tree round-16 ==" && git ls-tree -r --name-only HEAD -- census/round-16 tools/souji-landing-gate.py tests/fixtures/r15-preservation-frozen tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186 HEAD; do echo "== $r =="; git show $r:tools/souji-census.sh > /var/tmp/r16-ledger-$$.sh 2>/dev/null && sha256sum /var/tmp/r16-ledger-$$.sh | cut -d' ' -f1; bash -n /var/tmp/r16-ledger-$$.sh; echo "bash-n=$?"; done; rm -f /var/tmp/r16-ledger-$$.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== frozen expected ==" && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json | sed -n '1,80p' && echo "== gate present? ==" && git ls-tree HEAD tools/souji-landing-gate.py && ls -la .ufo/reports/round-16/ 2>&1 | sed -n '1,10p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== gate file? ==" && ls -la tools/souji-landing-gate.py 2>&1 && echo "== sha fixture/record ==" && sha256sum tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json tools/souji-census.sh && echo "== diff pins ==" && git diff HEAD --stat -- tools/souji-census.sh tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== LOG round16 ==" && grep -nEi 'round 16|round-16|non-parsing|does not parse|correction' LOG.md | tail -n 40 && echo "== SKILL lines 130-175 ==" && sed -n '130,175p' SKILL.md && echo "== SCORECARD operability ==" && grep -nE 'operability|calibration' SCORECARD.md | head -n 30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SOURCES bash set -n ==" && grep -nE '^\|\s*S0[0-9]{2,}' corpus/SOURCES.md | tail -n 8 && echo "== git-status rejected row ==" && grep -niE 'git-status' corpus/SOURCES.md | head -n 10 && echo "== lessons r16 ==" && ls corpus/lessons/ | tail -n 8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print("top keys:", list(d.keys()))
print("arms:", list(d.get('arms',{}).keys()))
for arm,v in d.get('arms',{}).items():
    print("\n==",arm,"==")
    for k in v:
        val=v[k]
        if isinstance(val,dict) and 'total' in val:
            print(f"  {k}: total={val.get('total')} failed={val.get('failed')} rc={val.get('rc')}")
        elif isinstance(val,dict) and 'rc' in val:
            print(f"  {k}: rc={val.get('rc')} stderr={str(val.get('stderr'))[:120]}")
        else:
            print(f"  {k}: {str(val)[:120]}")
for k in d:
    if k!='arms': print(k, '=>', str(d[k])[:400])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== hashes ==" && sha256sum tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json tools/souji-census.sh && echo "== record ==" && sed -n '1,40p' tests/fixtures/r15-preservation-frozen/record.json && echo "== gate log ==" && git log --oneline --all -- tools/souji-landing-gate.py | sed -n '1,5p'; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print("props:", [k for k in d if k!='items'])
for it in d['items']:
    print("\n---", it.get('name'), "|", it.get('agent'), "|", it.get('report',''))
    t=it.get('task') or it.get('brief') or ''
    print(t[:600].replace('\n',' '))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '60,170p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '630,700p' tools/souji-census.sh && echo "---- 700-860 ----" && sed -n '700,860p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== exit2 sites ==" && grep -nE 'exit 2|protected_fail|path-protected|could-not-evaluate' tools/souji-census.sh | sed -n '1,60p' && echo "== fixture ids ==" && grep -nE 'EXPECTED_IDS|^CASES|^\s*\("|"id"' tests/fixtures/r15-census-config.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== lessons ==" && ls corpus/lessons/ | grep -E 'round-1[456]' && echo "== skill census line ==" && grep -n 'Repeatable fleet census\|souji-census.sh --root' SKILL.md && echo "== sources bash ==" && grep -niE 'set -n|GNU Bash|bash\(1\)' corpus/SOURCES.md | sed -n '1,20p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '520,635p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '900,1040p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '128,160p' tests/fixtures/r15-census-config.py && echo "---- CASES ----" && sed -n '1336,1400p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm in ('changed','r14-harm','pre-harm'):
    v=d['arms'][arm]
    print("==",arm,"selftest:",json.dumps(v.get('selftest'))[:300])
    rc=v.get('r15-config',{})
    cases=rc.get('cases',{})
    fails=[k for k,val in cases.items() if val.get('verdict')!='PASS']
    print(" r15 cases:",len(cases),"fails:",len(fails), fails[:25])
print("changed sha:",d['arms']['changed']['sha256'])
print("fixtures:",d['fixtures_sha256'], "dirty:",repr(d['fixtures_dirty']))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== Q22-24 ==" && grep -nE 'Q2[2-4]' corpus/QUALITY.md | sed -n '1,20p' && echo "== CFG soft emit ==" && grep -n 'CFG_SOFT_REASON\|error row\|error"\|souji-census: error\|config-unsupported' tools/souji-census.sh | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== r15 lesson disclosure ==" && grep -nE 'does not parse|non-parsing|ConfigRepair|b410186|parse' corpus/lessons/round-15.md | sed -n '1,30p' && echo "== rejected rows ==" && grep -nE '\| rejected \|' corpus/SOURCES.md | sed -n '1,10p' && echo "== row count ==" && grep -cE '^\|\s*S[0-9]{3,}\s*\|' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
it=d['items'][0]
print(json.dumps(it, indent=1)[:1200])
PY
echo "== w1 dir now =="; ls .ufo/waves/round-16/w1/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' tests/fixtures/r15-preservation-frozen/README.md && echo "== grep PROBE RULE line ==" && grep -n 'PROBE RULE' .ufo/waves/round-16/w1-spec.json .ufo/waves/round-16/w1-dispatch.json 2>/dev/null | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== LOG round 16 ==" && grep -n 'round 16\|Round 16' LOG.md; echo "== LOG tail ==" && sed -n '780,815p' LOG.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json,textwrap
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    if it['name'] in ('LandingGate','LandingGateFixture','PreservationRepin','CriticGateVacuity','RevengeFrozenPin'):
        print("\n=====",it['name'],"=====")
        print(textwrap.fill(it['prompt'], width=170))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== ConfigRepair at b410186? ==" && git cat-file -e b410186:.ufo/waves/round-15/w1/ConfigRepair.md && echo present && git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '1,14p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== r16 census sha by rev ==" && for r in a31642d cc21683 b410186 cbf688a; do printf '%s ' $r; git show $r:tools/souji-census.sh | sha256sum | cut -d' ' -f1; done && echo "== pin match check ==" && for d in b51873514d1f6d34a5e3427bf30c95686a5d27b6ec9b8332034c3a3ba7868e02 6314d45db6be7281b405b13b8f0fd3fa8418eaa693f62c3efee781ecd6a7839f; do echo "pin $d"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== census anchors ==" && grep -nE '^# Exit codes|^#   2 usage|^#   Degraded|^#   Refused|^#   Accepted|^#   Global/system' tools/souji-census.sh && echo "== guard anchors ==" && grep -nE '^cfg_soft|^scan_config_file|^guard_config_file_kind|^guard_git_config|^guard_bound_filters|^count_dirty|GIT_NO_LAZY_FETCH=1|config-unsupported: %s|core\.hooksPath=/dev/null' tools/souji-census.sh && echo "== loop error row ==" && sed -n '1075,1095p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== r15 lesson M-rows ==" && grep -nE 'R15-M[123]|attempt_reuse|48f8945|552cae4|synthetic' corpus/lessons/round-15.md | sed -n '1,25p' && echo "== quality Q22 line ==" && sed -n '56,58p' corpus/QUALITY.md | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== wave dir at HEAD ==" && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | wc -l && echo "== wave dir r15 at HEAD ==" && git ls-tree -r --name-only HEAD -- .ufo/waves/round-15 | wc -l && echo "== preservation tool ==" && git ls-tree HEAD tools/souji-preservation-evidence.py && echo "== matrix digest ==" && sha256sum census/round-16/c1-matrix.json && echo "== r16 status markers ==" && grep -lE '\bSTATUS:\s*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-16/w1/*.md 2>/dev/null || echo "none"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== fixture docstring/classes ==" && grep -nE 'Round-16 revisions|HARM_CASES|CASE_CLASSES|degrade' tests/fixtures/r15-census-config.py | sed -n '1,30p' && echo "== case20 malformed ==" && grep -n 'malformed' tests/fixtures/r15-census-config.py | sed -n '1,10p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== w1 files now ==" && ls .ufo/waves/round-16/w1/ && echo "== markers ==" && grep -nE '\bSTATUS:\s*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-16/w1/DraftLessonMistakes.md .ufo/waves/round-16/w1/DraftR15Correction.md | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== DraftE anchors ==" && grep -n 'Draft E\|Draft A\|Draft B\|Draft C\|Draft D\|## Notes' .ufo/waves/round-16/w1/DraftR15Correction.md && echo "== DraftLessonMistakes R16-M1 ==" && grep -n 'R16-M1' .ufo/waves/round-16/w1/DraftLessonMistakes.md && echo "== Skeleton R6/R3 anchors ==" && grep -n 'Cross-domain evidence line\|Seat-reported failures\|STATUS:' .ufo/waves/round-16/w1/DraftReportSkeleton.md | sed -n '1,12p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json,re
m=json.load(open('census/round-16/c1-matrix.json'))
src=open('tests/fixtures/r15-census-config.py').read()
block=src[src.index('CASE_CLASSES = {'):]
block=block[:block.index('}')+1]
cls=dict(re.findall(r'"(R15CFG-\d+)":\s*"([a-z]+)"',block))
print("classes:",cls)
for arm in ('pre-harm','r14-harm','changed'):
    cases=m['arms'][arm]['r15-config']['cases']
    byclass={}
    for cid,v in cases.items():
        c=cls.get(cid,'?')
        byclass.setdefault(c,[0,0]); byclass[c][1]+=1
        if v.get('verdict')=='PASS': byclass[c][0]+=1
    print(arm, {k:f"{p}/{t}" for k,(p,t) in byclass.items()})
    print("   sample case:", list(cases.items())[0])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== docs unchanged b410186..cbf688a ==" && git diff --stat b410186 cbf688a -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md && echo "(empty above = unchanged)" && echo "== matrix output tracked? ==" && git ls-tree HEAD census/round-16/ && echo "== HEAD tree round-16 ==" && git ls-tree -r --name-only HEAD -- census/round-16/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'Degraded to one|A filter\.<name>|^census_one|^count_dirty|status-skipped|^guard_git_surface|^# Emit one TSV|r15-config|EXPECTED_IDS = \(' tools/souji-census.sh tests/fixtures/r15-census-config.py | sed -n '1,25p'
```

Non-shell reads (exact named files only): `corpus/lessons/round-15-verifier-spotcheck.md`, `corpus/lessons/round-14-verifier-spotcheck.md`, `.ufo/waves/round-16/w1-spec.json`, `census/round-16/run-matrix.py`, `census/round-16/c1-matrix.json`, `.ufo/waves/round-16/w1/DraftLessonGate.md`, `.ufo/waves/round-16/w1/DraftReportSkeleton.md`, `.ufo/waves/round-16/w1/DraftR15Correction.md`, `.ufo/waves/round-16/w1/SrcGitStatusRejected.md`.
