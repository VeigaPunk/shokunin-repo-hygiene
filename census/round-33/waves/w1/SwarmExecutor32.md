# SwarmExecutor32 — r33 w1, C2 leg O5

## Status

STATUS: PASS — Q71 repair of `tools/souji-round9-selftest.sh` built in scratch at prereg `2d9bca5`; the O5 leg flips from `rev-slash=rc1:49 checks, 2 failed` (prereg) to `PASS … rev-slash=rc0:49 checks, 0 failed` (candidate `e1608b2`), and every no-slash consumer output is byte-identical to base.

## Evidence

Scratch clone `/fast/scratch/hyaku/souji-r33/FixO5/c` (`--no-local`, origin dropped, toplevel confirmed before first commit), prereg checkout as second clone `b`. Candidate commit `e1608b2b4644b9c7c29f6a02c49d9446765b12f1` over `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; counter base `6017a482e7068d5afb7617640198fbb0fe743357` as frozen.

1. Cause, executed. At prereg, `TMPDIR=<scratch>/tmp/ bash tools/souji-verify.sh --selftest` → rc1, `ROUND9	14	2`, and the two reds are the ledger ones:
```
FAIL R9 file ledger revocation was reached: … obsidian=no-matching-ledger-row; stale=not-scratch-type
FAIL R9 directory ledger revocation was reached: … obsidian=no-matching-ledger-row; stale=not-scratch-type
```
   Same command with `TMPDIR=<scratch>/tmp` → rc0 `ROUND9	16	0`. Mechanism: line 7/14 propagated the trailing slash into every fixture path (`…/tmp//souji-round9-selftest.tam9PI/…`); `canon_path()` = `readlink -m` (`tools/souji-verify.sh:122`, used at `:458`, `:892`) collapses `//`, so the `//`-spelled ledger row fails the `[ "$sp" = "$target" ]` match at `tools/souji-verify.sh:301` (`obsidian=no-matching-ledger-row`) and the fixture `sha256sum` shim's `${!#} = $R9_GATE_TARGET` gate never fires, so the revoked-ledger checks are never reached.
2. Patch. `deliver-c2-O5.patch` = `git -C c diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`, 27 lines, `1 file changed, 8 insertions(+), 2 deletions(-)`, sha256 `eec2866b01cb9e74278729cbf80a9c89b7eeac9e2709eb3fc1b8723c0c265b94`; only `tools/souji-round9-selftest.sh`. `bash -n` clean on both revisions.
3. Counter, candidate:
```
LEG	O5	slash	PASS	base=rc0:selftest: 49 checks, 0 failed	rev=rc0:selftest: 49 checks, 0 failed	rev-slash=rc0:selftest: 49 checks, 0 failed
SUMMARY legs=1 pass=1 fail=0 harm=0 partial=1 rev=e1608b2b4644b9c7c29f6a02c49d9446765b12f1
rc=0
```
4. Counter, red-before at `2d9bca5` (isolated; no other job of mine running):
```
LEG	O5	slash	FAIL	base=rc0:selftest: 49 checks, 0 failed	rev=rc0:selftest: 49 checks, 0 failed	rev-slash=rc1:selftest: 49 checks, 2 failed
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=1
```
5. Q73 consumers. `git -C <clone> grep -l tools/souji-round9-selftest.sh -- tests/fixtures census` → rc0, 56 paths at both revisions. SKILL `## Gate registry` rows naming the helper directly: 0; rows whose self-test command runs it: 3 (`souji-verify`, `souji-vault-verify`, `souji-quarantine`). Paired runs (rc + last digit-bearing line), prereg → candidate:
   - `TMPDIR=<scratch>/tmp` no slash: verify rc0 `ROUND9	16	0` → rc0 `ROUND9	16	0`; vault rc0 `ROUND9	16	0` → rc0 `ROUND9	16	0`; quarantine rc1 `ROUND9	6	22` → rc1 `ROUND9	6	22`.
   - `TMPDIR=<scratch>/tmp/` slash: verify rc1 `ROUND9	14	2` → rc0 `ROUND9	16	0`; vault rc1 `ROUND9	12	4` → rc1 `ROUND9	16	0`; quarantine rc1 `ROUND9	6	22` → rc1 `ROUND9	6	22`.
   - `TMPDIR=/var/tmp` (registry form): verify 0/`16	0` → 0/`16	0`; vault 0/`16	0` → 0/`16	0`; quarantine 0/`28	0` → 0/`28	0`.
6. Q74. Only the kind refusal and the usage refusal exist; unchanged: `bogus <tool>` rc2→rc2, `verify` rc1 with `line 5: 2: tool path required` →rc1 (same message, line 5 unmoved), `:verify <tool>` rc2→rc2, `verify /nonexistent` rc1 with the identical `FAIL R9 nested-stale refuses ancestor: rc=127 …` first line.
7. No re-pin owed: `grep -rn round9 tests/fixtures/r15-preservation-frozen/` → no match; Q71-conformant root (no literal `/var/tmp` template outside the unchanged fallback).

## Findings

1. `tools/souji-vault-verify.sh --selftest` stays rc1 under a slash `TMPDIR` at the candidate on its own harness check, not the helper: `FAIL V9: r4='NOT-VERIFIED(row-incomplete)' want='NOT-VERIFIED(source-equals-vault)'`, identical at prereg. Its `ST_TMP` is built at `tools/souji-vault-verify.sh:1388` from `${TMPDIR:-/tmp}` with the same `//` construction — a sixth slash site, outside the five routed defects and outside this seat's file.
2. `tools/souji-quarantine.sh --selftest` is red (rc4 `live-fleet-mutation-forbidden` on the N cases, 22 checks) whenever `TMPDIR` lies inside `LIVE_FLEET_ROOT` = `dirname` of the tool checkout (`tools/souji-quarantine.sh:168,681`); `TMPDIR=/var/tmp` is 28/0 on both sides. Future runs of that selftest must keep `TMPDIR` outside the checkout's parent.
3. One red-before run issued while my own three-tool matrix was still executing returned `rev-slash=rc127:tools/souji-verify.sh: line 1319: /home/vgpnk/.local/bin/git: No such file or directory` instead of the two-check red. Not reproducible: the isolated re-run printed `49 checks, 2 failed`, and `/home/vgpnk/.local/bin` was identical before and after a standalone slash run. Concurrency artifact of two overlapping selftest batteries; the O5 reading must not be taken while another battery runs.
4. Probe noise, unclaimed: `TMPDIR=/var/tmp/souji-r33-FixO5-probe bash tools/souji-quarantine.sh --selftest` at prereg → `ROUND9	28	0` with rc1 (`FAIL P1 index shows staged deletion (porcelain keeps path)`), versus rc0 at `TMPDIR=/var/tmp`.

No ATTACK: no frozen predicate, item, leg or counter is contested; findings 1-2 are scope notes, verified as base-neutral (`base == candidate` in every row above).

## Deliveries

- `.ufo/waves/round-33/w1/deliver-c2-O5.patch` — `git -C <scratch clone> diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`, one file, `tools/souji-round9-selftest.sh`.
- `.ufo/waves/round-33/w1/deliver-c2-O5.md` — mechanism, both counter readings, the nine-pair Q73 matrix, Q74 refusals, findings, scratch hygiene.
- `.ufo/waves/round-33/w1/SwarmExecutor32.md` — this report.

Tooling: no install or upgrade was made this wave (nothing was needed; pacman untouched). Scratch `/fast/scratch/hyaku/souji-r33/FixO5/` and `/var/tmp/souji-r33-FixO5-probe` removed at close; both clone receipts are copied into `deliver-c2-O5.md`.
