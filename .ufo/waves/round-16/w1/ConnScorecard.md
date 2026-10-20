# ConnScorecard — round 16 SCORECARD draft

Seat: SoujiR16.ConnScorecard (connector, leaf). Judged on: calibration.
Scope: draft the SCORECARD.md updates only. No SCORECARD edit was applied; this report is the only write.

Axes named: **calibration** (primary), **operability** (row correction and C1 measurement), **coverage** (unchanged). The lane policy is kept: a 0–10 number only where a recorded mapping from evidence to points exists; all r16 deltas stay numeric 0 and legacy-unmapped, and the evidence moves verdict text and (conditionally) the capabilities table.

## Evidence observed

| fact | observed | source |
|---|---|---|
| r16 C1 matrix exists and is self-consistent | `c1-matrix.json` sha256 `561393aa8466243f2fcd70598bf12c39e71e903574d86ebb2d0ffd063f794323`; `lane_head=cbf688a`, fixture digests equal the worktree files | `census/round-16/c1-matrix.json` |
| changed arm at `cbf688a` | r15-config 20 total / 0 failed; r14-namespace 12/0; legacy selftest 38 checks / 0 failed; `bash -n` rc 0; ShellCheck warning 0 findings | same |
| r14-harm arm `cc21683` | r15-config 20 / 16 failed; r14-namespace 12/0 | same |
| pre-harm arm `a31642d` | r15-config 20 / 8 failed; r14-namespace 12 / 10 failed — a contraction control, not a green "before" | same |
| r15-baseline `b410186` | `bash -n` rc 2 at line 1368; ShellCheck rc 1 / 4 findings; selftest rc 2; both fixtures all-fail | same |
| named controls | mixed fleet is `R15CFG-16` (benign first/last, exact rows); poisoned-HOME/env preserve is `R15CFG-18`; both green at changed, red at r14-harm | `tests/fixtures/r15-census-config.py:129-175` |
| real-fleet run (L1) | 23 rows, rc 0, 0 stderr; `cc21683` and `cbf688a` identical excluding mtime (`rows_identical_excluding_mtime: true`); `b410186` rc 2, no census; pre-harm not run by design | `census/round-16/live-fleet.json` sha256 `eafa5e6d84018b96459929e533c1e51ac982e589827a9ceff34fbb529b5413f4` |
| r15 frozen pin state at HEAD | `expected.json` still pins census `b5187351…` and config fixture `6314d45d…`; committed bytes are `fed43c71…` and `9151cde8…`; boundary fixture `e6a984b1…` matches; `record_sha256` `4749ad07…` still the r15 record | `tests/fixtures/r15-preservation-frozen/expected.json`; `RevengeFrozenPin.md` D1 |
| changed transcript contradiction | the record's saved `TOOL` line prints a relative path while both pinned fixtures print the resolved absolute path — the r15 changed transcript is not reproducible from the pinned fixture identity | `RevengeFrozenPin.md` §3 |
| r16 gate tooling | `tools/souji-landing-gate.py` and `tests/fixtures/r16-landing-gate.py` were still absent at every read of this seat; `tools/souji-preservation-evidence.py` still has no `degrade` class | `ls`; `PlanWalk.md` §1.2 |
| r15 marker material | `corpus/lessons/round-15.md` at `b410186` carries none of `ConfigRepair.md`'s three marker lines; the r15 wave dir is committed (70 files), so the gate's marker check is non-vacuous at `b410186` | `git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md`; `git show b410186:corpus/lessons/round-15.md` |
| r16 marker material | live count moved across two measurements (18 reports / 70 lines, then 19 / 64) as seats wrote; most hits are analysis prose or fenced probe commands, not seat failures. This report contributes 6, all inside its fenced Commands block (0 outside) | marker scans over `.ufo/waves/round-16/w1/*.md` |
| gate held-out precision (peer-measured) | applying the pinned regex to committed r13/r14/r15 wave reports: 2/2/3 hits, 0/12 true seat-known failures outside r15, and 0/1 recall on the r14 instance of the same class; A1/A2 replays are predictions, not gate runs | `CriticGateVacuity.md` F1/F4/F5; A1/A2 |
| r16 wave-dir publication | `.ufo/waves/round-16/` is untracked at `cbf688a`; a `--round 16` run at `cbf688a` therefore passes LG-SEAT-UNCARRIED vacuously ("no wave dir passes") | `git status --porcelain`; gate contract |
| worktree drift at draft end | `tools/souji-census.sh` was modified after `cbf688a` while `cbf688a` remained HEAD: current worktree sha256 `feba44c7a598888844debb84efe4d29d90869f0dd640ea3f0229969eacd1aa88`, diff +31/−18, mtime 11:27:20. The C1 numbers above are for the committed `fed43c71…` bytes, not these | `git diff --stat -- tools/souji-census.sh`; `sha256sum`; `stat` |

## Draft SCORECARD.md fragment

### 1. Axes table — replace lines 14–15; leave line 13 (coverage) unchanged

```markdown
| calibration | 7 | r15 C2 remains unprovable: the preservation checker, its self-invocation fixture and the frozen declarations landed, but no selftest, external, frozen or actual-record verdict was ever run, and the frozen pin named bytes no committed revision holds. r16 C2 adds a stdlib-only landing gate (pinned findings LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-SEAT-UNCARRIED); its parse checks are syntax-only and rest on S043 (GNU Bash `set -n`), which cannot ground behavior (`CriticGateVacuity` F6). Before: the r15 closure found the same three landing defects by hand and no mechanical detector existed, so the mechanical count is 0/3; after: `[L1: observed K of 3, with exits]`. Held-out measurement is the caveat: the pinned predicate scores 0/12 true seat-known failures outside r15 and 0/1 recall on the r14 instance of the same class (`CriticGateVacuity.md` F1), so a b410186-shaped red is training-set replay, not calibration proof. Acceptance is a matrix bound to the pushed landing commit, not to cbf688a: `b410186 --round 15` red; `a31642d --round 15` must not emit marker false positives; `cc21683 --round 14` must not be cited as detecting the r14 harm; final revision `--round 16 --base cc21683` green only after pin-provenance verification, the re-measured frozen record, the wave reports and the lesson are committed, and the marker predicate's scope (STATUS declarations versus any matching prose) is pinned. Absent those held-out conditions the verdict is `unprovable-but-better`, not `improved`. No capability is admitted and no score number moves until then; numeric delta 0, legacy-unmapped | `python3 tools/souji-landing-gate.py --selftest`; `python3 tools/souji-landing-gate.py --root . --rev b410186 --round 15`; same `--rev a31642d --round 15`; same `--rev <pushed-HEAD> --round 16 --base cc21683`; runs stored in `census/round-16/landing-gate-final.json` | r15 `b410186` red control; r16 `<pushed-HEAD>` pending | r16 |
| operability | 8 | r15's bare "numeric delta 0" is corrected: `b410186` landed a census that fails `bash -n` (rc 2, line 1368), so r15's measured direction was negative; the heading 8 is legacy, not an endorsement. r16 C1 measured at `cbf688a`: `tests/fixtures/r15-census-config.py` 20/20 vs r14-harm `cc21683` 4/20 and pre-harm `a31642d` 12/20; `tests/fixtures/r14-census-boundary.py` 12/12 (pre-harm 2/12); legacy `--selftest` 38 checks, 0 failed (retained, but non-discriminating: r14-harm also passes it); `bash -n` rc 0; ShellCheck warning 0 findings. The discriminating reds include mixed fleet `R15CFG-16` and poisoned-HOME preserve `R15CFG-18`; changed passes every ID any arm passes and all the others. Live fleet (23 rows): `cc21683` and `cbf688a` identical excluding mtime, rc 0, 0 stderr; `b410186` produced no census; pre-harm not run because it lacks hooks/fsmonitor neutralization. Bounds: synthetic config classes plus a fleet-neutral live run; no universal config or hardlink claim; among repository-config outcomes, only a protected-namespace reach is a whole-run exit 2 (usage and malformed-baseline remain exit 2 by interface). Numeric delta 0, legacy-unmapped; net admission is L1's. The numbers are revision-bound to `cbf688a`; if the final landing carries different `tools/souji-census.sh` bytes (worktree drift was observed), rerun the matrix and the live fleet there and replace the values | `python3 census/round-16/run-matrix.py --changed cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --output census/round-16/c1-matrix.json`; live command recorded in `census/round-16/live-fleet.json` | a31642d / cc21683 / b410186 vs cbf688a; live fleet 2026-10-20 | r16 |
```

Coverage row line 13: keep byte-identical. r16 adds no coverage-map ground and ran no coverage count, so its `measured commit` and `last change` stay `a31642d → 552cae4` / `r13`.

### 2. Correction paragraph — apply Draft A, do not restate it

Insert `Draft A` from `.ufo/waves/round-16/w1/DraftR15Correction.md` verbatim directly after the axes table (before `Correction (r12 post-review …)`). The two rows above are written to be consistent with it. Add this one-line r16 policy note after Draft A:

```markdown
r16 numeric policy (2026-10-20): no recorded 0–10 scale maps fixture case counts or gate
findings to points, so every r16 delta stays 0 and legacy-unmapped. The evidence moves the
verdict text and, only after an observed run, the capabilities table — never the number.
```

### 3. Capabilities — replace line 46; insert the new row after it only on its entry condition

```markdown
| value/effect-aware census config guard (protected-namespace census; r14 namespace gains retained) | classify repository config per key and value: among config outcomes, a protected-namespace reach is the only whole-run refusal (exit 2; usage and malformed-baseline exit 2 by interface); a cannot-evaluate config degrades that repository to one `error` row (exit 0, no git command); a bound filter driver skips status for that repository only; hooksPath, fsmonitor, alternateRefsCommand, promisor and partialClone are inert; the r14 12-case namespace boundary stays green in the same run. Bounded: synthetic fixture classes plus a fleet-neutral live run; no universal config or hardlink claim; net admission remains L1's | `census/round-16/c1-matrix.json` (sha256 `561393aa8466243f2fcd70598bf12c39e71e903574d86ebb2d0ffd063f794323`; arms a31642d/cc21683/b410186/cbf688a) and `census/round-16/live-fleet.json` (sha256 `eafa5e6d84018b96459929e533c1e51ac982e589827a9ceff34fbb529b5413f4`), both measured against the `cbf688a` bytes (`fed43c71…`); rerun at the final landing revision if those bytes change; fixtures `tests/fixtures/r15-census-config.py`, `r14-census-boundary.py` | r14 namespace demonstration (rejected-harmed as net admission); r16 value/effect-aware bounded demonstration |
```

New row — **insert only after L1 records the selftest tally, both runs, and the held-out bar in `CriticGateVacuity.md` (A1/A2 plus one fix each from F2–F5)** (AXES.md: a capability without a passing demonstration in the round report is pre-claiming):

```markdown
| souji-landing-gate | mechanically detect landing defects in one committed revision without executing repository code: registry-cited scripts that fail `bash -n` or ast.parse, missing cited paths, parse regressions in BASE..REV, frozen-pin mismatches, and seat failure markers absent from the round lesson; stdlib only, `git archive` snapshot under /var/tmp removed in `finally` | `python3 tools/souji-landing-gate.py --selftest` → `SELFTEST pass=12 fail=0` `[L1 to record]`; `--rev b410186 --round 15` → exit 1 with LG-PARSE-REG, LG-FROZEN-PIN, LG-SEAT-UNCARRIED; `--rev <pushed-HEAD> --round 16 --base cc21683` → exit 0, `SUMMARY findings=0`; stdout+exit in `census/round-16/landing-gate-final.json` | r16 |
```

### 4. Planned — replace the stale r16 bullet, add the r17 row

```markdown
- **r16 (planned r15; ran 2026-10-20):** C1 measurements are in the operability row
  (matrix plus live fleet); C2 is declared, not accepted. The operator-stopped r15 checks
  were re-run only where the rows above cite a measured result; no unrun check counts as
  passed.
- **r17 (planned r16):** two claims on distinct axes. (1) calibration/capability: if the
  r16 gate is accepted, extend LG-FROZEN-PIN with commit binding — a pin may name a commit
  only when `git cat-file blob <commit>:<path>` equals the pinned digest — which is the class
  the `b5187351…` provenance left open; otherwise complete the r16 acceptance first, at the
  pushed landing commit and with every seat marker carried verbatim. (2) coverage/frontier:
  move F2 wider size attribution or one unexercised quarantine site into core.
  Certification stays OFF, K5 HELD; no new round is started here.
```

## Proposed move (one, bounded)

**Make the gate measure what it claims before C2 is credited, and make R4 a re-measurement rather than a digest rewrite.** In one integration pass: (a) treat a missing `.ufo/waves/round-N/` as exit 2 and report `checked_reports`, so the green cannot be vacuous at a revision where the wave dir is absent (`CriticGateVacuity` F4); (b) verify pin provenance — `git cat-file blob <measured_commit>:<path>` and the record's own `TOOL … sha256=` line must equal the pin (`F5`, `RevengeFrozenPin` D2); (c) anchor the marker net to `STATUS:` declarations with a pinned benign allowlist and exclude fenced code and table cells (`F2`), which removes the 70-line paste pressure measured above; if L1 keeps the pinned predicate instead, the only honest green is a mechanically generated verbatim carry block, and the row must say it enforces transcription, not disclosure (`F3`); (d) re-capture `record.json` from the three arms at the integration commit and re-pin **both** stale entries (`RevengeFrozenPin` D5); (e) run at the pushed landing commit with `--base cc21683`, after the reports and lesson are committed. This is the compatible synthesis of DraftR15Correction (D), DraftLessonGate (R3/verbatim, independent pin), PlanWalk (P4.2/P6.3 ordering) and CriticGateVacuity (F2–F5). It improves calibration — the green becomes falsifiable and the historical defect actually closed — and harms no other axis: no runtime artifact changes, no coverage claim, no score move.

## Affected axes

- **calibration (primary):** row rewritten with a 0/3 → observed detector count and a non-vacuous acceptance matrix; capability row conditional.
- **operability:** r15 delta direction corrected; r16 C1 measurement recorded with the real-fleet neutral result and explicit bounds.
- **coverage:** unchanged; no count run and no new ground claimed.

## Risks

1. **Pre-claiming.** The gate did not exist at any read; the selftest tally and both run exits are placeholders. Do not insert the capability row or claim 3/3 until L1 records them.
2. **False green at `cbf688a`.** The r16 wave dir is untracked there, so on the pinned contract LG-SEAT-UNCARRIED passes vacuously; the F4 correction would make that exit 2. `cbf688a` also still carries both stale pins. A green measured before the final commit proves nothing.
3. **Marker over-breadth.** The pinned predicate matches any line containing the historical failure vocabulary, not only `STATUS:` lines. Measured twice at draft time: 18 reports / 70 lines, then 19 / 64 as seats wrote; this report contributes 6, all inside its fenced command block. `CriticGateVacuity` F1 measured 0/12 true positives on held-out r13/r14 history. Final `--round 16` green therefore requires either a pinned scope correction (STATUS declarations plus a benign allowlist, code/table excluded) or a mechanically generated verbatim carry block of every matching line — and if it is the block, the row must state that it enforces transcription, not disclosure. The F2 code-fence exclusion removes this report's 6 and most command-line hits. Draft D's paraphrase does not carry `ConfigRepair.md`'s lines, so the `--round 15` replay stays red at the corrected revision unless L1 appends them.
4. **Digest-only re-pin is laundering.** The r15 README recipe refreshes digests while keeping a transcript produced by other or no bytes; `RevengeFrozenPin` D5 shows it would manufacture a `clean` verdict. Re-pinning must re-run and re-capture each arm, and the changed transcript's relative `TOOL` path must be explained or regenerated.
5. **Two stale pins, not one.** R4 named the census tool; the r16 fixture revision also invalidated `tests/fixtures/r15-census-config.py` (`9151cde8…`). Fixing only the tool leaves LG-FROZEN-PIN red.
6. **Commit binding is unverified.** LG-FROZEN-PIN compares file digests, not `git cat-file blob` provenance; the r17 proposal addresses this. The r16 green must not be read as closing D2.
7. **Score inflation.** Keep 8 / 8 / 7 and deltas 0; if any row number changes, the saturation prose and every prose number must be updated in the same edit (PlanWalk Q10).
8. **Training-set fit.** A red on `b410186` is the gate's own construction case; without the held-out replays (a31642d r13/r14 false-positive check, cc21683 r14 miss) the verdict is `unprovable-but-better`. The calibration row and capability entry must carry that wording until the held-out bar is measured.
9. **Final-bytes drift.** `tools/souji-census.sh` changed in the worktree after `cbf688a` (sha `feba44c7…`, +31/−18) while HEAD stayed `cbf688a`. The rows and capability evidence are measured against the committed `fed43c71…` bytes. If the landing commit includes the new bytes, the matrix, the live fleet and the frozen re-pin must all be rerun and the measured-commit cells replaced; do not copy the cbf688a values forward.

**Self-match note for the integrator:** six lines in this report's fenced `## Commands` block contain the pinned marker literals because the probes that produced the evidence quote them (0 outside the fence). Without the F2 code-fence exclusion they count as uncarried markers at `--round 16`; the same is true for many sibling reports. L1 must either scope the predicate or carry them (or the generated block) before claiming green.

## Verification (not run by this seat)

L1 should run and store raw stdout+exit:

```bash
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b410186cea626a67c92396ac58fbd57fb86876ac --round 15
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev a31642d14006830ec62edf40b0354c3699728c4a --round 15
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev a31642d14006830ec62edf40b0354c3699728c4a --round 13
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev cc2168325768d5356a82c039dcdf787377c55784 --round 14
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev cc2168325768d5356a82c039dcdf787377c55784 --round 15
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <pushed-HEAD> --round 16 --base cc2168325768d5356a82c039dcdf787377c55784
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed <pushed-HEAD> --output /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/<new>.json
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --quiet cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh || echo DRIFT-RERUN-REQUIRED
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file blob <pinned-commit>:tools/souji-census.sh | sha256sum
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-preservation-evidence.py --frozen /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen
```

`run-matrix.py` refuses an existing output path, so use a new JSON each run. The a31642d run is green only on the parse check; on the pinned contract its pin and marker checks are vacuous (targets absent), while under the F4 correction it would exit 2 for the missing wave dir. Either way it is not a green control for LG-FROZEN-PIN or LG-SEAT-UNCARRIED; the selftest's synthetic cases and the b410186 red are the falsifiable controls, and the held-out replays are the calibration tests.

## Coordination notes

- `DraftR15Correction.md` Draft A is the authoritative historical correction text; my rows do not duplicate it.
- `PlanWalk.md` P5.6 names the same two capabilities rows and the r17 row; P6.3 supplies the final gate command and output path used above.
- `tools/souji-seat-audit.py` (new, untracked) is an R5-enforcement capability candidate outside this item's named rows; L1 should decide separately whether it earns a capabilities row after its selftest runs.
- This seat ran no tool, fixture, census, gate, or checker; it read only named files and ran `bash -n`, `ast.parse` and `git`/`sha256sum`/`grep` probes on named paths.

## Tooling

No install or upgrade; no pacman transaction.

STATUS: draft complete; every observed value above is cited; gate tallies and final-run exits remain placeholders until L1 runs them. No failed check.

## Commands

Shell commands run by this seat, verbatim:

```bash
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -12 && echo --- && git status --porcelain | head -40 && echo --- && git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print(json.dumps(d, indent=1)[:4000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tools/ | grep -Ei 'census|landing|gate|preserv' ; echo ---; ls tests/fixtures | grep -Ei 'r15|r14|census|gate' ; echo ---; ls census/round-16/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(type(spec), list(spec)[:20] if isinstance(spec,dict) else len(spec))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "ConnScorecard\|landing-gate\|Scorecard" .ufo/waves/round-16/w1-spec.json | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it.get('name') in ('ConnScorecard','LandingGate'):
        print('='*20, it['name'])
        print(it['prompt'][:6000])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it.get('name')=='LandingGate':
        p=it['prompt']
        print(p[600:6000])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/lessons/ && echo --- && grep -n "numeric delta\|score\|rejected-harmed\|R1\|R4\|D1" corpus/lessons/round-15-verifier-spotcheck.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it.get('name')=='LandingGate':
        p=it['prompt']
        for i in range(900, len(p), 1500):
            print('---',i)
            print(p[i:i+1500])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it.get('name')=='LandingGate':
        p=it['prompt']
        for i in range(2150, min(2700,len(p)), 400):
            print('---',i)
            print(p[i:i+400])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it.get('name')=='LandingGate':
        p=it['prompt']
        for i in range(1450, 2150, 350):
            print('---',i)
            print(p[i:i+350])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1; echo ---; ls .ufo/waves/round-16/w1/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm,v in d['arms'].items():
    print(arm, v.get('rev'))
    print('  bash_n', v['bash_n'])
    for k in ('r15-config','r14-namespace'):
        if k in v: print('  ',k, v[k].get('total'), 'failed',v[k].get('failed'),'rc',v[k].get('rc'))
    if 'selftest' in v: print('  selftest', v['selftest'])
    if 'shellcheck_warning' in v: print('  shellcheck', v['shellcheck_warning'])
print('top keys', [k for k in d if k!='arms'])
for k in d:
    if k!='arms': print(k, json.dumps(d[k])[:500])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '110,180p' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S04[0-9]\|S05[0-9]" corpus/SOURCES.md | tail -20; echo ---; tail -30 corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/lessons/round-16.md 2>&1; grep -n "round 16\|round-16" LOG.md | tail -20; echo ---; sed -n '1,60p' census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w1 .ufo/waves/round-16/build 2>&1 | head -60; echo ---; grep -n "numeric delta\|legacy-unmapped\|Correction (r1" corpus/lessons/round-14.md corpus/lessons/round-15.md | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && cat tests/fixtures/r15-preservation-frozen/expected.json; echo ---; sha256sum tools/souji-census.sh; git rev-parse b410186:tools/souji-census.sh 2>/dev/null; git show b410186:tools/souji-census.sh | sha256sum; git show cc21683:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json; echo ---; git show b410186:tests/fixtures/r15-census-config.py | sha256sum; echo ---; python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'));print(json.dumps(d,indent=1)[:2500])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '95,120p' corpus/lessons/round-14.md; echo ===; grep -n "SCORECARD" corpus/lessons/round-15.md | head; echo ===; tail -12 LOG.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "error\|status-unverifiable\|config-unsupported\|path-protected" tools/souji-census.sh | head -40; echo ===; sed -n '1,80p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '80,140p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "R15-M\|## Gate\|three r15\|landing" corpus/lessons/round-15.md | head -30; echo ===; sed -n '1,40p' corpus/lessons/round-15.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    p=it['prompt']
    if 'SCORECARD' in p or 'score card' in p.lower():
        print('='*10, it['name'])
        print(p[:2500])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it['name'] in ('DraftR15Correction','DraftLessonGate'):
        print('='*10, it['name'])
        print(it['prompt'][:2600])
EOF
sed -n '1,60p' /home/vgpnk/Projects/shokunin/AXES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w1/ && ls tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1
sed -n '58,130p' /home/vgpnk/Projects/shokunin/AXES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -niE '\bSTATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' .ufo/waves/round-16/w1/*.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm in ('pre-harm','r14-harm'):
    print('='*8, arm)
    for cid,c in d['arms'][arm]['r15-config']['cases'].items():
        print(cid, c['verdict'], c['detail'])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "R15CFG-\|def case\|mixed\|benign\|on-fleet\|m-safe" tests/fixtures/r15-census-config.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-16/c1-matrix.json census/round-16/run-matrix.py; stat -c '%y %n' census/round-16/c1-matrix.json tools/souji-census.sh tests/fixtures/r15-census-config.py; echo ---; sed -n '60,200p' census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat && git status --porcelain=v1; echo ---; sed -n '138,160p' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    p=it['prompt']
    if 'live-fleet' in p or 'real fleet' in p.lower() or 'real directory' in p.lower():
        print('='*10, it['name'])
        print(p[:1800])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('census/round-16/live-fleet.json'));print(type(d));print(json.dumps(d,indent=1)[:1200])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/live-fleet.json'))
print('keys', list(d))
for arm,v in d.get('arms',{}).items():
    print('='*8, arm, v.get('rev'))
    for k in v:
        if k not in ('rows','stdout','stderr'):
            print(' ',k,':',json.dumps(v[k])[:300])
for k in d:
    if k not in ('arms',):
        print(k, json.dumps(d[k])[:800])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only b410186 -- .ufo/waves/round-15 | head -20; echo "count=$(git ls-tree -r --name-only b410186 -- .ufo/waves/round-15 | wc -l)"; echo ---; git ls-tree -r --name-only b410186 -- corpus/lessons/round-15.md; echo ---; git show b410186:SKILL.md | grep -nE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '1,20p'; echo ===; git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | grep -niE '\bSTATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b'; echo ===LESSON; git show b410186:corpus/lessons/round-15.md | grep -niE 'does NOT parse|\bsyntax error\b|STATUS:[[:space:]]*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in spec['items']:
    if it['name'] in ('PreservationRepin','LandingGateFixture','MutateScanConfig'):
        print('='*12, it['name'])
        print(it['prompt'][:3000])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-16/live-fleet.json; echo ---; grep -n "^| coverage\|^| calibration\|^| operability\|^## Capabilities\|^| protected-namespace\|^## Planned\|^## Saturation\|^## Correction (r12\|^## Tool certification" SCORECARD.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain=v1; ls tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' tools/souji-seat-audit.py; echo ---; python3 -c "import ast;ast.parse(open('tools/souji-seat-audit.py').read());print('ast ok')"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re,pathlib
pat=re.compile(r'(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b')
for p in sorted(pathlib.Path('.ufo/waves/round-16/w1').glob('*.md')):
    for i,line in enumerate(p.read_text().splitlines(),1):
        if pat.search(line):
            print(f'{p}:{i}: {line[:400]}')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1; ls -la .ufo/waves/round-16/w1/ | tail -20; git status --porcelain=v1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "SCORECARD\|landing.gate\|frozen\|numeric" .ufo/waves/round-16/w1/PlanWalk.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '40,75p' .ufo/waves/round-16/w1/PlanWalk.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re
p='.ufo/waves/round-16/w1/ConnScorecard.md'
pat=re.compile(r'(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b')
hits=[(i,l) for i,l in enumerate(open(p).read().splitlines(),1) if pat.search(l)]
print('marker hits:',len(hits))
for i,l in hits: print(i,l[:200])
EOF
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only a31642d -- tests/fixtures/r15-preservation-frozen .ufo/waves/round-15 | wc -l; echo ---; awk '/^## Planned/,/^## Saturation/' /home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md | grep -c r17
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import re,pathlib
pat=re.compile(r'(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b')
files={}
for p in sorted(pathlib.Path('.ufo/waves/round-16/w1').glob('*.md')):
    n=sum(1 for l in p.read_text().splitlines() if pat.search(l))
    if n: files[p.name]=n
print(len(files),'files;',sum(files.values()),'lines')
for k,v in files.items(): print(k,v)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import re
p='.ufo/waves/round-16/w1/ConnScorecard.md'
t=open(p).read()
print('lines',len(t.splitlines()))
for line in t.splitlines():
    if line.startswith('| calibration |') or line.startswith('| operability |') or line.startswith('| value/effect-aware') or line.startswith('| souji-landing-gate |'):
        print(line.split('|')[0] or line[:40], 'cells=', len(line.split('|'))-2)
pat=re.compile(r'(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b')
hits=[(i,l) for i,l in enumerate(t.splitlines(),1) if pat.search(l)]
print('marker hits',len(hits),[i for i,_ in hits])
print('has r17 in planned block:', 'r17' in t.split('## Planned')[0] if '## Planned' in t else 'no planned heading')
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('.ufo/waves/round-16/w1/swarm-registry.json'))
print(type(d), list(d)[:10] if isinstance(d,dict) else len(d))
s=json.dumps(d)
for k in ('LandingGate','PreservationRepin','DraftR15Correction'):
    i=s.find(k)
    print(k, i, s[max(0,i-120):i+160] if i>=0 else '')
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1; echo ---; git status --porcelain=v1; echo ---; ls -la .ufo/waves/round-16/w1/ | tail -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- tools/souji-census.sh; sha256sum tools/souji-census.sh; stat -c '%y %s' tools/souji-census.sh; git diff -- tools/souji-census.sh | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import re,pathlib
pat=re.compile(r'(?i)\bSTATUS:' + r'\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|' + 'does NOT ' + 'parse|' + r'\bsyntax ' + 'error\b')
total=0; files={}
for p in sorted(pathlib.Path('.ufo/waves/round-16/w1').glob('*.md')):
    n=sum(1 for l in p.read_text().splitlines() if pat.search(l))
    if n: files[p.name]=n; total+=n
print(len(files),'files;',total,'lines')
print('mine',files.get('ConnScorecard.md'))
t=pathlib.Path('.ufo/waves/round-16/w1/ConnScorecard.md').read_text().splitlines()
fenced=False; fenced_hits=0; all_hits=0
for l in t:
    if l.strip().startswith('```'): fenced = not fenced; continue
    if pat.search(l):
        all_hits+=1
        if fenced: fenced_hits+=1
print('mine all',all_hits,'fenced',fenced_hits,'outside',all_hits-fenced_hits)
PY
```

Non-shell reads: `read` on `SCORECARD.md`, `SCORECARD.md:43-80`, `.ufo/waves/round-16/w1/DraftReportSkeleton.md`, `DraftSkillSection.md`, `DraftR15Correction.md`, `DraftLessonGate.md`, `RevengeFrozenPin.md`, `CriticGateVacuity.md`, `corpus/lessons/round-15-verifier-spotcheck.md`; `grep` tool over named files only. No gate, fixture, census, checker or selftest was executed.
