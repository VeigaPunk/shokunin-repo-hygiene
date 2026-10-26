## Status

STATUS: PASS — the replay and all three new cheats ran and were scored; the frozen instruments hold, A1/A2/A3 each lost a leg to a new cheat.

## Evidence

- Replay of `census/round-30/controls.sh` and `census/round-30/controls-amended.sh` at the lane tip `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`, `HYAKU_SCRATCH=/fast/scratch/hyaku/souji-r30/ControlsReplay`, scratch clones with origin removed: 13 of 14 frozen/amended control rows reproduce their recorded SUMMARY numbers exactly; one differs (`C1-do-nothing(base)` k1/mismatches 13→12) and is localized to an unpinned tool path. A second consecutive run reproduces run 1 exactly (deterministic).
- Receipts retained at `.ufo/waves/round-30/w2/SwarmExecutor07-receipts/` (raw tsv/out files, the three cheat patches, `l1-readings-check.txt`, `regress-localization.txt`, `trailing-slash-guard.txt`); scratch dirs removed.
- Cheat commits live only in throwaway clones: A1 `d7bd0d7b53fa5c4746df90cfd77335ce95157a91`, A2 `24343621c2afd00b05d02d2bc2cd8c2b83d00bd8`, A3 `c53ca1e3f2d3841a42e831a3977f4b18cb59f3c7` and `0d638e5072bfc89c9eec0b190c313c08889ede43`. No lane write, no `git`/`jj` mutation in the lane, no signals.
- Tooling: no install or update was performed this run (installed channel unused); `jj 0.45.1-7c41cdeb…` and `git` on the host were read only as version strings.

## Findings

1. **The frozen-controls harness is unpinned, so its own recorded C1 row no longer replays.** `census/round-30/controls.sh:16` reads `python3 -B "$LANE/tools/souji-capability-agreement.py" --root "$C" --rev "$1" --base $B` — the live lane file, whose blob changed from `4073c97e` (prereg `d4928ec`) to `9b74d734` (A3, commit `02aea48`). Replay therefore scored the A3 instrument and printed `k1=12 mismatches=12`, while `records/controls.tsv` records `k1=13 mismatches=13`. Running the pinned blob `d4928ec:tools/souji-capability-agreement.py` against the same BASE clone reproduces `k1=13 k2=0 mismatches=13 rows=18 pointers=10` exactly: the instrument reproduces, the harness does not pin it. No other control row moved (13/14; run-to-run stable).

2. **Both control harnesses abort before emitting rows when `HYAKU_SCRATCH` ends in `/`** (the value this seat was given). `controls.sh` builds `SCR=${HYAKU_SCRATCH}/souji-r30/…` and then guards with `[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ]`; a double slash in `$D/c` is normalized by git, the string comparison fails, and the script prints `toplevel mismatch` on stdout and exits 2 with a header-only tsv (`trailing-slash-guard.txt`). Same construction at `controls-amended.sh:10-13`.

3. **A1's REGRESS-FULL exemption is dead code, so the A1 target is unreachable at the lane tip, not just at the C2 landing commit.** `census/round-30/c2-counter-v2.py:69` strips only a tab-joined tail: `re.sub(r"\terr=.*$", "", l) if l.startswith("CASE\t") else l for l in out.splitlines()`. The selftest never joins `err=` with a tab — measured on the base run: 0 lines contain `\terr=`, 59 contain ` err=`. The leg therefore compares the reworded no-reports message that A1 was written to exempt (amendments.txt:12 — `REGRESS-FULL (every selftest/r16 line equal between BASE and REV except the free-text err= tail`). Consequence at the honest tip `9dcd367`: `SUMMARY-V2 … regress_full=differs`, while the frozen v1 counter at the same revision meets its target (`regress=same`). Localized diff after the counter's own normalization: exactly two CASE lines, both the C2 reword `.ufo/waves/round-18/` → `.ufo/waves/round-18/ or census/round-18/waves/` (`regress-localization.txt`). The L1's reading attributes this to the counter correctly, but records C2 as resolved at the capture commit under A1; at the tip A1's added leg still fails, so "C2 met" is true only under the frozen v1 instrument.

4. **A1's FIXTURE/REDARM legs are forgeable and carry no weight (BROKEN).** `c2-counter-v2.py:147` runs the lane-authored fixture (`frc, fout = run([sys.executable, "-B", fx, "--tool", gate_rev], w, tmp)`) and judges only its printed verdict shape (docstring:18 `FIXTURE  / REDARM as in v1`); no pinned bytes, no minimum assertion. Cheat: keep the honest gate, add a comment marker, and replace `tests/fixtures/r30-landing-gate-discovery.py` with a stub that greps the marker and prints `CASE D1..D7 PASS` — liveness against the BASE tool (which lacks the marker) keeps REDARM green. Scored SUMMARY-V2 at the cheat rev is leg-for-leg identical to the honest tip (`bind=ok nocap=ok ptrarm=ok fixture=ok redarm=ok regress_full=differs`), i.e. zero new failing legs. To show the fixture is the only arm that matters, the same cheat also double-counts reports in `check_carry` (appending the capture set even when the wave set exists, against the gate's own comment `# wave dir alone is read, so no report is ever counted twice.`): the honest fixture rejects it (`CASE D3 FAIL … FAIL(checked_reports=2 want 1 (double count?))`, `cases=7 pass=6`), while A1 reports `bind=ok nocap=ok ptrarm=ok`. Replacing the fixture is enough to hide a real regression in the claim.

5. **A2's E3 binds record↔fixture self-consistency, not fixture↔reality (BROKEN).** `c3-counter-v2.py:72` is `e3 = p.returncode == 0 and got and got == keep(rec)`: the committed record is compared with a replay of the committed fixture, and both are authored by the same commit — the amendment's own framing (amendments.txt:18-19: `E3 the committed fixture tests/fixtures/r30-jj-keep-expiry.sh is replayed and its version/RESULT lines equal the committed record`). Cheat: a `printf`-only fixture that builds no repository and runs neither jj nor git, a record rewritten to those canned lines, and the entry's Observed/Conclusion rewritten to claim that `git gc --prune=now` alone removes the keep ref and the commit — directly contradicting the S063 quote the entry still carries. Scored `SUMMARY-V2 e1=ok e2=ok e3=ok e4=ok f1_exact=3`; the frozen v1 counter also passes (`legs=9 fail=0 f1_entries=3`). E1/E2/E4 are provenance-shaped checks that survive; nothing compares the prose to the quoted bytes, so the coverage entry can assert the opposite of its own snapshot.

6. **A3's MATCH takes the last digit-bearing stdout line, so a trailing label shadows the result (BROKEN).** `tools/souji-capability-agreement.py:172` documents `# A3: stdout's last digit-bearing line wins; stderr only when stdout has none`, and `:184` sets `verdict = "MATCH"` on substring presence with digit boundaries. Cheat: append one documentation label after each row's real summary — `5/5 lanes documented in README` after `selftest=PASS ids=7/7` (r13-repo-structure.sh, SCORECARD:155 states 5/5), and `8/8 size measurements listed in the knowledge entry` after `cases=12 pass=12` (r24-size-census.py, SCORECARD:174 states 8/8). Scored `ROW R04 … observed=5/5 lanes documented in README MATCH` and `ROW R15 … observed=8/8 size measurements listed in the knowledge entry MATCH`; the full run falls from `k1=12` (A3 at base) to `k1=10`. The two rows whose stated counts are false are now graded true; two rows were forged, the mechanism is per-row and does not need the stated count to be right.

7. **The other L1 readings replay as recorded.** C1 at `7b16731`: `k1=0 k2=0 mismatches=0` under both the pinned v1 blob and A3 (HOLDS). C3 at `76c94eb`: v1 `legs=9 fail=0 f1_entries=3`, v2 `e1..e4=ok f1_exact=3` (HOLDS). C2 at landing `68447afe`: v1 `reports=86 cne=0 dangling=1 other=7 … regress=same` (MISSED, as the L1 recorded). C2 at tip: v1 target met (HOLDS); A1 target unmet (Finding 3).

## Attack log

| attacked item | how | verdict |
|---|---|---|
| frozen `controls.sh` (8 rows) | replayed twice, diffed numbers against `records/controls.tsv` | HOLDS (7/8 numbers; the 8th is a harness defect, Finding 1) |
| amended `controls-amended.sh` (6 rows) | replayed, diffed against `records/controls-amended.tsv` | HOLDS (6/6 numbers) |
| reproducibility guard of both harnesses | ran with the assigned trailing-slash `HYAKU_SCRATCH` | DEFECT-NOT-FATAL (Finding 2) |
| C1 instrument reproducibility | pinned blob vs live file at BASE | DEFECT-NOT-FATAL (instrument reproduces 13; harness unpinned) |
| C1 target at `7b16731` | v1 blob and A3, full 18 rows + 10 pointers | HOLDS |
| C3 target at `76c94eb` | v1 and v2 | HOLDS |
| C2 at landing `68447afe` and at tip, frozen v1 | full counter | HOLDS |
| C2 at tip, A1 | full counter | BROKEN (`regress_full=differs`) — instrument defect makes the leg unpassable |
| A1 FIXTURE/REDARM | marker-stub fixture + double-count gate | BROKEN (cheat survives; honest fixture would have caught it) |
| A2 E1–E4 | canned fixture + fabricated record + false conclusion | BROKEN (cheat survives A2 and frozen v1) |
| A3 MATCH semantics | trailing-label forge on R04 and R15 | BROKEN (cheat survives; k1 12→10)|
| A3 bypass/banner/substring fixes of A3 | replayed the recorded amended controls | HOLDS (bypass and banner rows still mismatch) |

Axis harm: none. Read-only seat; the only writes are this report, `deliver-controls-replay.txt` and the receipts directory. Calibration (7), operability (8) and coverage (8) surfaces were attacked, not modified.

## Deliveries

- `.ufo/waves/round-30/w2/SwarmExecutor07.md` (this report)
- `.ufo/waves/round-30/w2/deliver-controls-replay.txt` (replay diffs, guard row, three scored cheats, L1-reading checks)
- `.ufo/waves/round-30/w2/SwarmExecutor07-receipts/` — `replay-controls.tsv`, `replay-controls-run2.tsv`, `replay-controls-amended.tsv`, `st-base.out`, `st-rev.out`, `regress-localization.txt`, `trailing-slash-guard.txt`, `cheat-A1.patch`, `cheat-A2.patch`, `cheat-A3.patch`, `a3-base-full.txt`, `a3-cheat-full.txt`, `c2-tip-baseline.txt`, `c2-cheat-rev.txt`, `c3-cheat-rev.txt`, `l1-readings-check.txt`
