# W2C3Mut — mutation test of the C3 runner changes (souji r24 w2, FALSIFY)

## Status
STATUS: PARTIAL. I ran 13 mutants: 11 primary (one per new clause, with each of the 4 new `COUNTS_RE` alternatives as its own mutant) and 2 variants. Every mutant was restored byte-exact.
- The r23 + r24 fixtures kill only the verify durable check and the verify argv check (M1, M1b, M2, M2b).
- 9 of the 11 primary mutants survive both fixtures.
- The per-element redaction clause produces receipts that `verify` refuses (Attack A1).

uncovered=9

## Evidence
- Target bytes: `tools/souji-receipt-run.py` at after-receipts `ca7fc1cb6dd1333096c6f3bdbad304686691d126`, sha256 `9df0738c…82ff`. The runner and both fixtures are byte-identical from `ca7fc1c` to master `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (`git diff --quiet` exit 0). Clauses come from `git diff a65fac9 ca7fc1c -- tools/souji-receipt-run.py` (+31/−4).
- Detectors:
  - `r23` = `tests/fixtures/r23-receipt-run.py` (`18f4da11…`).
  - `r24` = `tests/fixtures/r24-receipt-verify.py` (`f8c4c391…`), run with `--lane-root` = lane.
  - Supplementary, not preregistered:
    - `sweep`: `verify --root <lane>` over the 5 r23 receipts and the 9 committed r24 receipts.
    - `probe`: my own probe, one subcase per clause the fixtures never present, plus 5 run→verify symmetry witnesses.
- Isolation: all work was in `/var/tmp/souji-r24-W2C3Mut/`. The scratch copies changed only `SCRATCH_ROOT`/`SCRATCH_PARENT`, pointing them at `…/W2C3Mut/tmp`, and the r23 copy prints `ok=<0|1>` per case (output only). The same copies were used for the pristine, mutated and restored runs. Copy hashes: runner `59f74c08…c476`, r23 `c8ba2b24…8e05`, r24 `9b6b1804…806e`.
- Protocol per mutant: apply via an exact anchor with count==1, hash, run all 4 detectors, restore, hash. All 13 mutants: `restored_eq_pristine=True`. Final `restored sha=59f74c08…c476 eq_pristine=True`.
- Baselines (pristine and restored, identical):
  - `r23 selftest=8/8`.
  - `r24 cases=8 pass=8 refusals=2/2 regress=5/5`.
  - `sweep receipts_ok=14/14`.
  - `probe probe_pass=7/10`; the 3 failures are symmetry witnesses (Attack A1). No baseline subcase that I score is failing.
- git 2.56.0, Python 3.14.8. No tools installed or updated. I found no `godspeed` skill file under `/home/vgpnk/.omp`, so none was read.

| id | clause (ca7fc1c line) | mutation | r23 | r24 | sweep | probe |
|---|---|---|---|---|---|---|
| M1 | verify durable check (296) | block deleted | survived 8/8 | **killed** a (`refusals=1/2`) | survived 14/14 | survived |
| M1b | verify durable check | any ref counts (`for-each-ref --contains` with no namespace) | survived | **killed** a: the jj-keep-only instance gives `verify rc=0` | survived | survived |
| M2 | verify argv check (306) | block deleted | survived | **killed** b | survived | killed sym-bearer flips to ok |
| M2b | verify argv check | `tool not in header["cmd"]` (substring) | survived | **killed** b (substring instance gives `rc=0`) | survived | survived |
| M3 | verify `command_refusal` mirror (303) | block deleted | survived | survived 8/8 | survived | **killed** v-command-refused (`rc=0 verify=ok`) |
| M4 | MALFORMED on shlex error (299) | try/except removed | survived | survived | survived | **killed** v-shlex-malformed (`rc=1 Traceback`) |
| M5 | run TOOL-NOT-IN-ARGV (178) | block deleted | survived | survived | survived | **killed** r-tool-not-in-argv (`rc=0 wrote=True`) |
| M6 | run TOOL-PATH-REDACTED (180) | block deleted | survived | survived | survived | **killed** r-tool-path-redacted (`rc=0 wrote=True then_verify_rc=2 RECEIPT-TOOL-NOT-IN-ARGV`) |
| M7 | per-element redaction (239) | reverted to `redact(shlex.join(args.command))` | survived | survived | survived | distinguished, mutant better: sym-token and sym-password flip to verify ok (A1) |
| M8a | COUNTS_RE `grounded=` (67) | alternative deleted | survived | survived | **killed** 12/14 (c2-after, c2-control-base: COUNTS-ABSENT) | survived |
| M8b | COUNTS_RE `cases= pass=` (68) | alternative deleted | survived | survived | **killed** 10/14 (c1-after, c1-control-stub, c3-after, c3-control-base-runner) | survived |
| M8c | COUNTS_RE `garbage=` (69) | alternative deleted | survived | survived | **survived** 14/14 | survived |
| M8d | COUNTS_RE `selftest=` (70) | alternative deleted | survived | survived | **killed** 13/14 (r13-recheck-receipt) | survived |

uncovered=9 (M3 M4 M5 M6 M7 M8a M8b M8c M8d survive both preregistered fixtures). Including the supplementary detectors, M8c survives everything, and M7 is only distinguished by inputs where the mutant behaves better than the landed code.

Key excerpts (this run):
- `M1 r24`: `jj-keep-only(rev=53d8176b075b refs=refs/jj/keep/r24-fixture digest_equal=True) verify rc=0 out=verify=ok`
- `M1b r24`: `no-ref … verify rc=2 out=RECEIPT-REV-NOT-DURABLE …; jj-keep-only(rev=eea64467bf16 refs=refs/jj/keep/r24-fixture …) verify rc=0`
- `M2b r24`: `substring(tool=counter.py) rc=0 out=verify=ok`
- `M3 probe`: `probe=v-command-refused ok=0 rc=0 stdout=<verify=ok …>`
- `M4 probe`: `probe=v-shlex-malformed ok=0 rc=1 stderr=<Traceback (most recent call last): …>`
- `pristine probe`: `probe=sym-token-elem ok=0 run_rc=0 recorded=<cmd=/usr/bin/python3 tools/tiny-counter.py '--token=[REDACTED]> verify_rc=2 verify=<RECEIPT-MALFORMED cmd= does not parse as shell words: No closing quotation>`
- `M7 probe`: `probe=sym-token-elem ok=1 run_rc=0 recorded=<cmd=/usr/bin/python3 tools/tiny-counter.py --token=[REDACTED]> verify_rc=0`

## Findings
1. **The fixtures kill only M1, M1b, M2 and M2b, all in r24 cases a and b; r23 kills none of the 13 mutants.**
   - The amendment's jj-keep instance now kills M1b. This closes wave-1 MutRunnerPlan finding 5, where the same mutant survived.
   - Location: `tests/fixtures/r24-receipt-verify.py:206`, "for label, holder in (("no-ref", None), ("jj-keep-only", JJ_KEEP_REF)):".
2. **The verify-side symmetry clauses are uncovered: M3 and M4.**
   - No case presents a `cmd=` that `command_refusal` refuses, or one that is unparseable.
   - Each mutant is non-equivalent: the probe kills it. M3 turns a refusal into `verify=ok`; M4 turns rc=2 into a traceback.
   - Location: `tools/souji-receipt-run.py:299-305` @ca7fc1c, "argv = shlex.split(header["cmd"])".
3. **The run-side clauses are uncovered: M5 and M6.**
   - Every fixture `run` passes `--tool` as an exact, unredactable argv element. r24: `tests/fixtures/r24-receipt-verify.py:147`, `"--out", out, "--", sys.executable, TOOL_REL)`. r23: `tests/fixtures/r23-receipt-run.py:218`.
   - The probe kills both: the mutants write a receipt that the tip's `verify` refuses.
   - Location: `tools/souji-receipt-run.py:178-181`, "if redact(tool) != tool:".
4. **The per-element redaction clause (M7) is uncovered by every detector.** No fixture argv contains a secret shape. The only distinguishing inputs I found favour the mutant (Attack A1), so the landed clause has no input where it is observably better than the line it replaced.
   - Location: `tools/souji-receipt-run.py:239`, `f"cmd={redact(shlex.join([redact(a) for a in args.command]))}",`.
5. **The new `COUNTS_RE` alternatives are uncovered by both fixtures**, whose counters print only the old `assertions=` shape.
   - The committed r24 receipts happen to kill M8a, M8b and M8d.
   - Nothing kills M8c: no committed receipt carries a `garbage=` counts line without a `cases=` line. `census/round-24/size-census-lane.txt` is not a receipt.
   - Location: `tools/souji-receipt-run.py:63`, "COUNTS_RE = re.compile(".
6. **No harm under any mutant.** `regress=5/5` and the r23 `selftest=8/8` held for all 13. This is a C3 harm check, not a clause detector.
7. **Lane bytes moved during my run, by another seat.**
   - The lane runner was `9df0738c…` (= committed) before the run, `705cf40a…` after the driver finished, and `fd25a6e4…` at the snapshot.
   - `git status` shows ` M tools/souji-receipt-run.py`, mtime 2026-10-25 06:42:45 −0300.
   - I wrote only under `/var/tmp/souji-r24-W2C3Mut/` and this report. The edit is uncommitted; it is not the landed artifact and is not scored above.

## Attack log
- **A1. The per-element redaction makes `run` write receipts that `verify` refuses.** It is a new run→verify asymmetry, introduced by the clause that was meant to restore symmetry.
  - Mechanism, measured on the pristine copy: `--token=abc123` → per-element `--token=[REDACTED]` → `shlex.join` quotes it (`[` is shell-unsafe) → the outer `redact()` pattern `\S+` consumes the closing `'`.
  - Result: `cmd=… '--token=[REDACTED]` → `verify rc=2 RECEIPT-MALFORMED … No closing quotation`. `password=hunter2` behaves the same way.
  - The reverted line (M7) records `--token=[REDACTED]` unquoted, which verifies (`verify_rc=0`).
  - The frozen target contract for symmetry is the amendment, "`verify` mirrors run's command_refusal (RECEIPT-COMMAND-REFUSED) and reports an unparsable cmd=" (`.ufo/waves/round-24/preregistration-amendment-1.txt`, C3 section). The asymmetry is outside its case set, so C3's counter cannot see it.
  - Reported, not a counter change.
- **A2. TOOL-PATH-REDACTED checks the tool in isolation, but the joined-line redaction can still rewrite the tool element.**
  - argv `python3 -c <print counts> Authorization: Bearer tools/tiny-counter.py` → `run rc=0`.
  - Recorded `cmd=… Authorization: Bearer [REDACTED]` → `verify rc=2 RECEIPT-TOOL-NOT-IN-ARGV` (sym-bearer-cross-elem, pristine).
  - Wave-1 MutRunnerPlan A1 (a redaction false refusal) therefore survives the run clause meant to close it.
  - Location: `tools/souji-receipt-run.py:180` @ca7fc1c.
- **A3. The uncommitted working-tree edit (fd25a6e4) changes A1 and A2 from verify refusals into run refusals, under a misleading code.** Informational, not claim evidence: I ran a snapshot copy once (`r23 selftest=8/8`; `r24 cases=8 pass=8 refusals=2/2 regress=5/5`).
  - The single-element `--token=abc123` is refused as `CMD-SECRET-SPANS-ARGV a secret pattern spans argv elements`. The secret does not span elements; the re-redaction of the quoted `[REDACTED]` is what fires.
  - So any `--token=`/`password=` argv cannot get a receipt at all.
  - [INFERENCE] The edit's author is the seat working on A1; it was not landed at master `c3ca7ad3`.
- **A4. The C3 case set reaches 2 of the 8 named clauses.** Recorded as a coverage finding (Findings 2–5); no predicate, target or case-set change is proposed.

Scratch `/var/tmp/souji-r24-W2C3Mut/` removed after writing this report.
