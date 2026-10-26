# SwarmMutationTester27 — A3 mutation test, souji round 30 w2

## Status
STATUS: PASS — attack ran to completion: 10 mutants (8 tasked + 2 extra) against the A3 rules of `tools/souji-capability-agreement.py` at 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8, each probed with the same bounded detector on pristine, mutated and restored bytes; 10/10 KILLED, 0 survived, 0 inconclusive; bytes restored hash-exact after every probe; lane untouched.

## Evidence
- Target bytes: `tools/souji-capability-agreement.py` at lane tip 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8; pristine sha256 `88ffa768ac77868c18129977b97f5c3bd12a17c2cc60db76cfbb3786d9a6f3f2`. v1 blob at prereg d4928ec86b667e3d1ed0adb07fb088e500cf1631 diffed first to shape each revert faithfully.
- Detector (identical for P/M/R of every probe): `python3 -B work.py --root <scratch-clone> --rev <scenario-commit> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631 --scratch <scratch>/cw --timeout 120 --only R01[,R12]`; full stdout + exit code compared. Row choice per tasking: `--only` on 1 row (R01) in 9 scenarios, 2 rows (R01,R12) in S7.
- Fixtures: 10 scenario commits (branches `probe-S1..S10` from the tip in a scratch clone, origin removed). Each overwrites the row-command script `tests/fixtures/r12-maintenance-guard.sh` (and `tools/souji-declared-evidence.py` in S7) with a probe script, and appends `R30-CORRECTION` lines to SCORECARD.md (append-only preserved) except S7/S9, which deliberately break append-only to test fail-closed. R01 (line 152) and R12 (line 171) carry no landed correction, so no cross-talk with the C1 landing's corrections.
- Lane sanity (pristine counter, real lane tip, `--only R01`): exit 0, `observed=selftest=PASS ids=6/6 MATCH`, `SUMMARY k1=0 k2=0 mismatches=0 rows=1 pointers=10 partial=1` — baseline well-formed, matching the L1's C1-met reading.
- All 10 P baselines well-formed (no `COULD-NOT-EVALUATE`, no traceback); every R run byte-identical to its P run; `work.py` sha256 equal to pristine before and after every mutant. Lane `git status --porcelain` over SCORECARD.md SHONEN.md tools tests census: empty after all runs.
- Raw receipts: `SwarmMutationTester27-receipts/` (manifest.txt, lane-sanity.json, p-pass.json, mutant-results.json, scenarios.json, per-mutant `.diff`/`.M.out`/`.R.out`).

## Findings
1. No surviving mutant: every tasked A3 rule is enforced by the committed counter bytes. No coverage finding against the C1 instrument from this seat; this strengthens (does not by itself prove) the L1's C1-met reading against these 10 defect axes.
2. `kind=shape` containment (pristine.py:206 `all(n in nums_o for n in nums_s)`) is diagnostic-only: reverting it to v1's iterator-consumption (M10) changes only the `KINDS` line (`shape=1` becomes `value=1`), never SUMMARY or exit — the script itself labels it "(diagnostic; not part of the target)". Frozen target insensitive by design.
3. Dead code, hygiene only: `def first_path(argv):` (pristine.py:94) has zero call sites in the A3 bytes — v1 called it in the cmd= check (`first_path(cargv) is None or first_path(cargv) != first_path(argv)`), A3 replaced that with the argv-prefix check and left the helper behind. Removal is a no-op refactor; no behavior impact.
4. Tooling record: nothing installed or updated this run (preinstalled python3 3.14 and git only; no pacman, no uv, no downloads).

## Attack log
Verdict per attacked A3 rule (mutant killed ⇒ rule HOLDS; P = pristine, M = mutant, R = restored; scenario revs in receipts/scenarios.json):

| # | A3 rule attacked | Mutant (exact change) | Scenario | P → M | Verdict |
|---|---|---|---|---|---|
| M1 | stdout-first observation | return line → v1 concat `normalize(out + err, work)` (v1: `(q.stdout + q.stderr).decode`) | S1 f71d3e90, R01; probe prints `6/6` stdout + `warn=9` stderr | rc 0→1, `observed=6/6 MATCH` → `observed=warn=9 MISMATCH kind=value`, k1 0→1 | HOLDS (killed) |
| M2 | digit-boundary match | `elif rc == 0 and re.search(r"(?<!\d)" + re.escape(stated) + r"(?!\d)", s):` → v1 `elif stated in s and rc == 0:` | S2 69c5524e, R01; probe prints `16/6` | rc 1→0, `MISMATCH kind=shape` → `MATCH`, k1 1→0 | HOLDS (killed) |
| M3 | cmd= adds no `-c` | forbidden tuple drops `"-c"` (keeps -h/--help/--version) | S3 e7a9d9be, R01; correction `cmd=… --selftest -c pass rc=0 observed=fixed=1` | rc 1→0, `MISMATCH kind=value` → `CORRECTED`, k1 1→0 | HOLDS (killed) |
| M4 | banner never accepted | `if BANNER.search(rs): continue` deleted | S4 3d0665b1, R01; probe exits 2 with stderr `usage: guard.sh [--count 3]`; correction rc=2 observed=that line | rc 1→0, `MISMATCH kind=rc` → `CORRECTED`, k1 1→0 | HOLDS (killed) |
| M5 | banner breadth | `BANNER = re.compile(r"(?i)^usage:…")` → `BANNER = re.compile(r":")` (any line with a colon) | S5 79c4bec9, R01; probe prints `note: rows=1`; correction rc=0 observed=that line | rc 0→1, `CORRECTED` → `MISMATCH kind=value`, k1 0→1 | HOLDS (killed) |
| M6 | cmd= argv-prefix identity | `cargv[:len(argv)] != argv` → `first_path(cargv) != first_path(argv)` (v1's check) | S6 7852a458, R01; correction `cmd=… --probe other rc=0 observed=probed=1` (same first path, not a prefix) | rc 1→0, `MISMATCH kind=value` → `CORRECTED`, k1 1→0 | HOLDS (killed) |
| M7 | SCORECARD append-only fail-closed | `sc_append = sc_rev.startswith(sc_base)` → `sc_append = True` | S7 61dd3e51, R01,R12; SCORECARD.md line inserted at top (base bytes no longer a prefix); probes print stated `6/6`/`8/8` | rc 1→0, both rows `MISMATCH(append-only-violated)` → `MATCH`, k1 2→0 | HOLDS (killed) |
| M8 | enumerated set frozen at --list-rev | `rows_tsv = blob(root, a.list_rev, "census/round-30/c1-rows.tsv")` → `blob(root, a.rev, …)` | S8 65ffd627, R01; c1-rows.tsv rewritten at --rev without R01; probe prints `mutprobe=7` | rc 1→0, ROW line for R01 disappears entirely (mutant enumerates from --rev), k1 1→0 | HOLDS (killed) |
| M9 | SHONEN append-only fail-closed (extra) | `sh_append = sh_rev.startswith(sh_base)` → `sh_append = True` | S9 adc7feba, R01; SHONEN.md line inserted at top | rc 1→0, all 10 pointers `MISMATCH(append-only-violated)` → `RESOLVES`, k2 10→0 | HOLDS (killed) |
| M10 | kind=shape containment (extra) | `all(n in nums_o for n in nums_s)` → v1 `it = iter(nums_o)` + `all(n in it for n in nums_s)` | S10 f29eca5e, R01; probe prints `6/7` vs stated `6/6` | rc 1→1, SUMMARY unchanged; `KINDS value=0 shape=1 rc=0` → `KINDS value=1 shape=0 rc=0` | HOLDS (killed, diagnostic line only) |

Restoration evidence: after each probe the working copy was rewritten with pristine bytes and re-hashed (`88ffa768…f3f2` every time) and the scenario re-run reproduced the P output byte-for-byte (R_rc == P_rc, R stdout == P stdout, all 10). Scratch clone and probe commits deleted after receipts were copied out.

## Deliveries
- Report: `.ufo/waves/round-30/w2/SwarmMutationTester27.md` (this file)
- Receipts: `.ufo/waves/round-30/w2/SwarmMutationTester27-receipts/` — manifest.txt, lane-sanity.json, p-pass.json, mutant-results.json, scenarios.json, M1–M10 `.diff` / `.M.out` / `.R.out`
