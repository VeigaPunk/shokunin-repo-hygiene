# R42w3reviewer01 — independent re-measurement of C1/C2/C3 (+ landing gate) at the final tip 6a3f759…

Seat: R42w3reviewer01 (wave 3, role reviewer; re-issued from the wrap-up-stopped wave 2). Judged on: calibration, operability, coverage.
Measured tip: `6a3f75941d3604e3459011d599c2c16f3a97b44c` (lane `git rev-parse HEAD` = `6a3f759…`, `git status --porcelain` empty at read time). Base: `bf618f6c5c09d302994871c94903abbea2deb60d`.
No git/jj mutation anywhere; nothing written outside this seat file and my scratch (`/fast/scratch/hyaku/souji-r42/R42w3reviewer01/`, deleted before yield). No tools installed or upgraded.

## Reused vs redone (wave-2 partial work)

The wave-2 seat report `.ufo/waves/round-42/w2/R42w2reviewer01.md` exists (17829 bytes, landed 2026-10-28 22:57) but all of its measurements were taken at the run-11 tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8`, **not** the final tip `6a3f759…`, so none of its counter outputs can serve as this closure's receipt.

- **Reused (verified, not re-run):** its lesson fact-check findings are already consumed in the landed lesson at this tip — E-3 (SCORECARD:697 "six receipts, not five"; staged entry "26 registrations across 10 lane repos"; live fleet 30 regs/29 repos), E-9 (65 resolved rows mechanical, 5 derived correction values reproduce), and the wave-2 tip C1 reading cited at lesson line 221. I confirmed these citations by reading `corpus/lessons/round-42.md:219,221,227` — no re-measurement needed; they are lesson-text matters, not the three claims.
- **Redone (this report):** all three frozen-counter measurements and the landing-gate readings, re-run by me at `6a3f759…` with fresh scratch dirs, exactly as the seat spec commands.

## Commands run (exact) and observed output

Host state at start: `uptime` → `load average: 18.61, 42.16, 44.21` (32 cores); scratch dirs `c1 c2 c3` created first (`/fast/scratch/hyaku/souji-r42/R42w3reviewer01/{c1,c2,c3}`), `TMPDIR` pointed into each.

**C1 (calibration)** — `export TMPDIR=…/c1 && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 6a3f75941d3604e3459011d599c2c16f3a97b44c --scratch /fast/scratch/hyaku/souji-r42/R42w3reviewer01/c1`:
```
SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0
EXIT=0
```

**C2 (operability)** — same shape, `c2-counter.py`, `--scratch …/c2`:
```
case-clean=PASS            …(all 37 case lines PASS; full output preserved in this seat's transcript)…
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest ok rc=0 summary=(31, 31, 0)
SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb
EXIT=0
```
(All 37 `case-*=PASS` lines observed individually, from `case-clean` through `case-absent-prereg`.)

**Landing gate (R1-adjacent, both modes, `--round 42`)** — run from the lane dir:
```
$ python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 6a3f75941d3604e3459011d599c2c16f3a97b44c --round 42
SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=2	carry_heading=0	checked_reports=200
rc=0
$ python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 6a3f75941d3604e3459011d599c2c16f3a97b44c --round 42 --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=2	carry_heading=0	checked_reports=200
rc=0
```

**C3 (coverage)** — one gated run. I first sampled `/proc/loadavg` every 15 s for 24 min waiting for `load1 < 8`; the shared host never reached it (other tenants' stakker-polish gifski/blender/playwright churn; 1-min load swung 11–35). The single run then executed at the best window the gate allowed:
```
=== uptime BEFORE c3 ===  load average: 23.74, 29.29, 36.52
$ export TMPDIR=…/c3 && python3 -B …/census/round-42/c3-counter.py --root … --rev 6a3f75941d3604e3459011d599c2c16f3a97b44c --scratch /fast/scratch/hyaku/souji-r42/R42w3reviewer01/c3
MUTANT B1 candidate=killed prior=-    …(all 13 population mutants killed)…
MUTANT D4 candidate=killed prior=-
EQUIV B3 candidate=survived prior=-     …(all 6 equivalent mutants survived)…
EQUIV H4 candidate=survived prior=-
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
EXIT=0
=== uptime AFTER c3 ===  load average: 17.75, 23.81, 33.16
```
(Run wall time ≈ 171 s; counter exit 0.)

## Comparison against the committed receipts and the round report

| counter | SUMMARY at tip `6a3f759…` | receipt value | differing fields |
|---|---|---|---|
| C1 `census/round-42/records/c1-after.txt` | `items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` (exit 0) | identical SUMMARY (receipt header: measured at `34e33a66…` before the SCORECARD/LOG appends; report says L1 re-ran at tip) | **none** |
| C2 `census/round-42/records/c2-after.txt` | `cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb` (exit 0) | identical SUMMARY (receipt at `5ad7046…`) | **none** |
| C3 `census/round-42/records/c3-after.txt` | `mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (exit 0) | identical SUMMARY (receipt at `5ad7046…`, idle host) | **none** |
| Landing gate `census/round-42/records/gate-both-modes.txt` | `--round 42`: `findings=0` both modes, rc=0; `checked_reg=113 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=2 carry_heading=0 checked_reports=200` | report R1 after-column: "landing gate `findings=0` in both modes with `--round 42` at the final tip" | `findings` matches; counts differ from the receipt because the receipt is a **round-41** reading at the repoint rev (`checked_reg=107, status_lines=0, checked_reports=165`) — the round-42 rows landed since; expected, not a defect |

## Verdict per claim

- **C1 calibration — reaches target** at `6a3f75941d3604e3459011d599c2c16f3a97b44c`. Every frozen-target field reproduces byte-for-byte against `c1-after.txt`, exit 0.
- **C2 operability — reaches target** at the tip. All 37 cases PASS, controls REJECTED, real/retro/retro_clean/selftest legs as targeted, `patches=3/3`, identical to `c2-after.txt` including `tool_sha=9ddd596b98fb`, exit 0.
- **C3 coverage — reaches target** on this measurement at the tip: `killed=13 survived=0 old_killed=0 equiv_killed=0 anchors=ok`, identical to `c3-after.txt` including the pinned-tool sha `b2a603cf4247`, exit 0. Caveat below.
- **Landing gate / R1 closure — consistent**: `findings=0` in both modes with `--round 42` at the tip, rc=0, exactly as the round report's before→after table states.

## Residual risk and verification gaps

1. **C3 idle-host condition not fully met.** The shared host never dropped below `load1 8` within a 24-minute gate (other tenants' jobs), so the single C3 run went out at `load1 23.74` and finished at `17.75`. Per the known named limit (lesson E-1 / N-C3c; report: "not stable under load") the C3 value is a load-dependent reading, so my run **corroborates** the frozen target and the committed idle-host receipt — no field differed — but it is not itself a canonical idle-host receipt. The canonical idle-host receipt remains `census/round-42/records/c3-after.txt`; this is a verification gap, not a field difference.
2. No differing SUMMARY field was found for any claim; nothing observed contradicts the three receipts or the round report's before→after table at the final tip.
3. The C1 receipt was taken before the round's bookkeeping appends and the round report says the L1 re-ran C1 at the tip; my independent run confirms the tip value equals the receipt, so no gap there.

Tools installed/upgraded: none. Scratch `/fast/scratch/hyaku/souji-r42/R42w3reviewer01` removed after this report was written.
