# SwarmReviewer23 — r30 w1 review of the L1's frozen-counter controls

## Status

STATUS: PASS — all three claims' controls reviewed and 8 junk states constructed and scored in a scratch clone (origin removed); two junk states pass the frozen counters fully green (C2, C3) and one passes C1 via the contract's `cmd=` form; filed as ATTACKs for the L1. No lane writes beyond this report and its receipt.

## Evidence

Scratch clone `/fast/scratch/hyaku/souji-r30/ReviewControls/r.V4H5gT/c` (`git clone --no-local` of the lane, `origin` removed, `rev-parse --show-toplevel` verified). Counters run from lane paths with `--root <clone>`; every junk state built from base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b, prereg d4928ec86b667e3d1ed0adb07fb088e500cf1631. Full transcripts: `.ufo/waves/round-30/w1/SwarmReviewer23-runs.txt`.

Base facts measured this run: base gate `--selftest` rc=0, last line `SELFTEST pass=65 fail=0`; base gate with no args rc=2 (usage, no digit-bearing line → counter sentinel `NONE`); sha256 of base `tools/souji-landing-gate.py` = `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`.

L1's committed controls (`census/round-30/records/controls.tsv`) reproduce the prereg's base values (C1 `k1=13 k2=0 mismatches=13 rows=18 pointers=10`; C2 `reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same`; C3 `legs=9 fail=8 f1_entries=2`). Their junk states are all rejected, but each is the naive form of its cheat; cheaper or sneakier forms below.

### C1 (calibration) — junk states scored with the frozen counter (`--only` diagnostic rows)

| state | rev | SUMMARY | counter |
|---|---|---|---|
| J1 corrections whose `observed=` is copied verbatim from `census/round-30/records/c1-before.txt` (R05+R10) | b6bfa345d22c… | `k1=0 k2=0 mismatches=0 rows=2 pointers=10 partial=1` | **ACCEPTS** (exit 0) |
| J2 `R30-CORRECTION` line inserted before the base bytes end (SCORECARD.md line 2) | c254be530cfb… | `k1=1 k2=0 mismatches=1 rows=1 pointers=10 partial=1` | rejects (exit 1, `MISMATCH(append-only-violated)`) |
| J3 `cmd=` substitution: healthy row R05 "corrected" against a no-arg invocation (`rc=2 observed=NONE`) while its own command is healthy (rc=0, `SELFTEST pass=65 fail=0`) | b23c09778707… | `k1=0 k2=0 mismatches=0 rows=1 pointers=10 partial=1` | **ACCEPTS** (exit 0) |

J1 argument (asked by the item): the counter re-runs the row's command at REV and requires the recorded `rc`/`observed` to equal its own fresh observation ("rc and observed must equal what the counter observes", preregistration.txt:5), so a copied value is accepted only when it is true. It is therefore not a truth cheat — but it means a seat can meet the C1 target with zero measurement, delegating the calibration run to the counter's own scoring pass. Cheapest accepted state for C1; the do-nothing control is not it.

### C2 (operability) — junk states scored with the frozen counter

| state | rev | SUMMARY | counter |
|---|---|---|---|
| J1 stub gate printing hard-coded `checked_reports=86`, selftest line faked from base bytes + hard-coded fixture | 64e5c332349b… | `reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=fail regress=differs` | rejects (exit 1) — caught by REDARM and by the r16 regress leg (`SUMMARY total=15 failed=13`) |
| J2 stub gate + fixture that detects the base tool by sha256 digest (pass=0 at base, all-pass at rev) | 547082e67f18… | `… fixture=ok redarm=ok regress=differs` | rejects (exit 1) — REDARM defeated, r16 regress still bites |
| J3 real gate behind a delegation shim that rewrites only `--fleet-root` invocations (`checked_reports:=86`, `LG-DANGLING-PTR`/`COULD-NOT-EVALUATE` lines dropped) + digest fixture | 633f6f05af5f… | `reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same` | **ACCEPTS** (exit 0) |

J3 is fully green: the gate never evaluated a single report. The r16 fixture and `--selftest` stay byte-identical because the shim delegates verbatim whenever `--fleet-root` is absent (the counter's GATE leg passes `--fleet-root`; the r16 fixture's own invocations do not — tests/fixtures/r16-landing-gate.py:150-151).

### C3 (coverage) — junk states scored with the frozen counter

| state | rev | SUMMARY | counter |
|---|---|---|---|
| J1 fully fabricated evidence: junk 900-byte "page" never fetched, self-consistent SHA256SUMS + fetch-receipts.tsv row (http 200), invented `jj-keep-expiry-run.txt` (3 RESULT lines, no jj run), fabricated S220 SOURCES row, README F1 map edit | bc46d6a2f82e… | `legs=9 fail=0 f1_entries=3` | **ACCEPTS** (exit 0) |
| J2 F1-count laundering: both real F1 entries demoted, 3 unmapped junk `ground: F1` files added | bf0691ec1ec7… | `legs=9 fail=7 f1_entries=3` | rejects (exit 1) — L1 passes with zero real F1 entries, L2's map consistency catches the junk |

## Findings

1. **[ATTACK, high] C2 accepts a gate that never evaluated any report.** `census/round-30/c2-counter.py:86` reads only `m = re.search(r"checked_reports=(\d+)", out)` and `:118` `return 0 if reports > 0 and cnef == 0 and dangling == 0 and fok and rok and same else 1` — the GATE leg is regex-counting with no cross-check that `checked_reports` equals the committed capture (`git ls-tree` count, which the prereg itself defines as 86), and GATE rc is ignored. Both remaining defenses are scored from seat-committed bytes: REDARM trusts the seat-authored fixture (defeated by digest detection), REGRESS compares only (rc, last digit-bearing line) of `--selftest` and the r16 fixture (defeated by delegation). Junk rev 633f6f05af5f… scores the exact target SUMMARY, exit 0. Stricter-only amendment shape for the L1: assert `checked_reports` == `git ls-tree -r --name-only <rev> -- census/round-29/waves/ | wc -l`, and/or run the r16 fixture with a `--fleet-root`-bearing argv.
2. **[ATTACK, high] C3 accepts fully fabricated evidence.** `census/round-30/c3-counter.py:106` checks only `if data is None or len(data) < 512 or sums.get(os.path.basename(sp)) != h or fr.get(sp, ("", ""))[1] != h or fr.get(sp, ("", ""))[0] != "200"` — internal bookkeeping consistency, no fetch provenance; `:121-122` checks only run-record shape (`nres = sum(1 for l in run.splitlines() if l.startswith("RESULT "))`, a `jj-version: jj 0.45.1` line, the strings `refs/jj/keep`/`util gc` in the entry) — no execution proof. Junk rev bc46d6a2f82e… reaches `fail=0` with a never-fetched page, invented receipts and an invented jj run. The counter cannot distinguish measured from invented; only a human/reviewer pass can.
3. **[ATTACK, medium] C1's `cmd=` form launders a healthy row against an argv the SCORECARD never stated.** `tools/souji-capability-agreement.py:178` pins only `if first_path(cargv) is None or first_path(cargv) != first_path(argv):` — the script path. Junk rev b23c09778707… "corrects" R05 (stated 18/18; the command actually prints `SELFTEST pass=65 fail=0`, rc=0) with `cmd=python3 tools/souji-landing-gate.py rc=2 observed=NONE` (no-arg usage failure) → CORRECTED, k1=0. The mechanism is contract-sanctioned (preregistration.txt:5 allows `[cmd=<argv>]` keeping the script path), so this is a contract hole, not a counter bug; stricter-only amendment could pin the full argv or require the recorded observation to come from the row's own stated argv.
4. **[observation, low] C1's cheapest accepted state requires no measurement.** Copied-from-c1-before.txt corrections (rev b6bfa345d22c…) are accepted; truth is enforced by the counter's rerun, so provenance is irrelevant by design — but the "each capability row's stated count re-run" work is delegable to the scoring run itself. No amendment needed unless the L1 wants provenance (e.g. require the correction's `observed` to differ from the base receipt when the tool changed).
5. **[ok] C1's append-only guard bites placement tricks.** A correction inserted before the base bytes end (rev c254be530cfb…) forces `sc_append = sc_rev.startswith(sc_base)` (souji-capability-agreement.py:123) false → every run row `MISMATCH(append-only-violated)`, exit 1. Rejected.
6. **[ok] C2's naive stub is caught twice.** L1's stub + hard-coded fixture form (my J1, rev 64e5c332349b…) is caught by REDARM and by the r16 regress leg; my J2 shows REDARM alone is digest-defeatable, leaving r16 as the only catcher — consistent with controls.tsv's `redarm=fail regress=differs`.
7. **[ok] C3's L1 is a pure count but L2 partially covers laundering.** Rev bf0691ec1ec7… passes L1 with three junk files and zero real F1 entries; L2's map consistency flags the unmapped junk (mismatches=3). Residual: mapped junk (README row edit) sails through L1+L2 — subsumed by finding 2.
8. **[observation, low] C3's SHA256SUMS lookup requires bare filenames.** `census/round-30/c3-counter.py:106` keys `sums[f[1]]` and looks up `os.path.basename(sp)`; a SHA256SUMS line carrying the full path (`<sha>  census/round-30/sources/<name>`) would fail L4 for honest work. The wave must write bare filenames in SHA256SUMS.

## Attack log

- C1-J1 (copied observed, R05+R10): rev b6bfa345d22c55dd5faf13ff414860b74b27cd6f → `SUMMARY k1=0 k2=0 mismatches=0 rows=2 pointers=10 partial=1`, exit 0 — accepted; argued as by-design (rerun enforces truth), work-skip noted (finding 4).
- C1-J2 (correction before base bytes end): rev c254be530cfbe3979d2661a59935397400d0a1c2 → `k1=1 … append-only-violated`, exit 1 — rejected.
- C1-J3 (`cmd=` argv substitution): rev b23c09778707719873ebecfa3e5406301d2de905 → `k1=0 k2=0 mismatches=0 rows=1 pointers=10 partial=1`, exit 0 — accepted; contract hole (finding 3).
- C2-J1 (stub + faked selftest + hard-coded fixture): rev 64e5c332349bb23fd457ff2de558c31be5d1b723 → `redarm=fail regress=differs`, exit 1 — rejected.
- C2-J2 (stub + digest fixture): rev 547082e67f18fbff63bcae9c0933d68d9f6cbcdc → `redarm=ok regress=differs`, exit 1 — rejected by r16 regress alone.
- C2-J3 (real gate + `--fleet-root` rewrite shim + digest fixture): rev 633f6f05af5f956d4f3034bc1c0a7e4f52d818cc → `reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same`, exit 0 — **fully green junk; counter accepts** (finding 1).
- C3-J1 (fully fabricated evidence): rev bc46d6a2f82e64635540715cece57a8ce24d0c05 → `legs=9 fail=0 f1_entries=3`, exit 0 — **fully green junk; counter accepts** (finding 2).
- C3-J2 (F1-count laundering): rev bf0691ec1ec76f4ad4a564b3d5967167a2fedc88 → `legs=9 fail=7 f1_entries=3`, exit 1 — rejected by L2.

No counter, predicate, target or case set was changed; these are reports, not amendments. No tool installs were needed (system python3/git/sha256sum only).

## Deliveries

- `.ufo/waves/round-30/w1/SwarmReviewer23.md` — this report.
- `.ufo/waves/round-30/w1/SwarmReviewer23-runs.txt` — full transcript of the 8 junk-state runs (counter ROW/PTR/leg lines, SUMMARY lines, exit codes, junk revs).
