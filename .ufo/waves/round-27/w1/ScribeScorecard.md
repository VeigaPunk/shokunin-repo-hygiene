## Status
STATUS: PARTIAL — paste-ready Round 27 measurement block and planned bullet drafted; all landing-tip values remain `[PENDING]` for the L1.

## Evidence
| # | command | output excerpt | revision |
|---|---|---|---|
| E1 | `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` (as recorded in `ExecScorecardDraft.md:5`) | `e78ac7c4837b81b634db4a927605a751a7f006ba` | frozen base |
| E2 | `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin` (as recorded in `ExecScorecardDraft.md:6`) | `SUMMARY findings=2 checked_reg=50 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0` | e78ac7c4837b81b634db4a927605a751a7f006ba |

## Round 27 measurements block

```markdown
### Round 27 measurements (2026-10-25; lane base e78ac7c4837b81b634db4a927605a751a7f006ba)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 internal landing-gate dangling-pointer findings | calibration 7 | `findings=2` at base `e78ac7c4837b81b634db4a927605a751a7f006ba`; the two `LG-DANGLING-PTR` findings are `corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118` (observed by running the frozen gate at base) | `[PENDING]` — expected `findings=0`; replace only with final-tip measurement | `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --round 27 --fleet-root /home/vgpnk/Projects/shokunin` | `[PENDING]` |
| C2 grounded F4 origin-record entries and registry assimilation (S152/S210/S211) | coverage 8 | `registry_rows=132`, `grounded_F4=2` at base `e78ac7c4837b81b634db4a927605a751a7f006ba` (frozen preregistration) | `[PENDING]` — expected `registry_rows=135`, `grounded_F4=4`, gate `entries=2 ok=2 fail=0`, sources-census rc 0 | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`; `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`; `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md --snapshot-dir census/round-27/sources --slice census/round-27/records/empty-slice --slice-verdicts census/round-27/records/empty-verdicts`; `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | `[PENDING]` |
| C3 pre-report gate and isolated false-green fixture | operability 8 | gate absent at base `e78ac7c4837b81b634db4a927605a751a7f006ba` | `[PENDING]` — expected gate present; fixture `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0; C3 receipt verify=ok | `bash tests/fixtures/r27-pre-report-gate.sh`; `tools/souji-receipt-run.py verify --root . census/round-27/records/c3-after.tsv` | `[PENDING]` |

Score delta: `[PENDING]` — L1 to record final evidence and confirm no owned-axis score changed. Certification OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.
```

## Planned bullet

```markdown
- **r28 (planned r27):** (a) calibration continuation: re-audit the pointer-exemption counter and its exact-token/non-overmatch boundary against any newly surfaced internal landing-gate citation sites; keep all source citations intact and append corrections rather than rewriting prior records. (b) coverage continuation: continue bounded F4 origin-record assimilation only where fresh primary-source grounding supports a distinct mechanism; re-ground existing F4 entries and retain explicit admit/reject gates. (c) operability continuation: exercise the pre-report gate against additional report/worktree/remote edge cases without weakening the r27 four-case contract or changing its false-green rejection requirement. No axis harm; certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged.
```

## Findings
1. Table shape follows the Round 26 measurement table: six columns, identical header/separator rows. Round 26 reference: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/scorecard-r26.md:20-24`. Quote: “| claim | axis | before | after | counting command | measured commit |”
2. Frozen claims and expected counter values are defined at `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:5-9`. Quote: “C1 — axis calibration (score 7, lowest non-retired;”
3. Base C1 command/output and base revision are recorded at `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/ExecScorecardDraft.md:5-6`. Quote: “SUMMARY findings=2 checked_reg=50”
4. After-state figures are placeholders; this seat did not measure them. No PASS claim is made for C2/C3 or for a landing tip.

## Attack log
- None filed by this reporting seat.
