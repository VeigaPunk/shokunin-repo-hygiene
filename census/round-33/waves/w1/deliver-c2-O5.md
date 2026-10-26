# C2 leg O5 — tools/souji-round9-selftest.sh scratch root from TMPDIR

Seat: SwarmExecutor32 (leaf). Lane clone: `/fast/scratch/hyaku/souji-r33/FixO5/c`, origin dropped,
`git -C c rev-parse --show-toplevel` = `/fast/scratch/hyaku/souji-r33/FixO5/c` before its first commit.
Prereg commit `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Candidate scratch commit
`e1608b2b4644b9c7c29f6a02c49d9446765b12f1` (throwaway identity `-c user.name=scratch -c user.email=scratch@invalid`).
Base for the counter is `6017a482e7068d5afb7617640198fbb0fe743357` as frozen.

## Why the two false failures happen (mechanism, pruned to one cause)

`tools/souji-round9-selftest.sh:7` built its scratch dir with
`mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX"` and line 14 re-exported the same
`${TMPDIR:-/var/tmp}`. With `TMPDIR` ending in `/` every fixture path therefore carries `//`
(e.g. `.../tmp//souji-round9-selftest.tam9PI/ledger-file/fleet/case-shokunin/source.md`).
The tools under test canonicalise the target with `canon_path()` = `readlink -m`
(`tools/souji-verify.sh:122`, applied at `:458` and `:892`), and POSIX pathname resolution collapses
repeated slashes, so:

- `obsidian` ledger lookup (`tools/souji-verify.sh:301`, `[ "$sp" = "$target" ]`) never matches the
  `//`-spelled row → `obsidian=no-matching-ledger-row`;
- the fixture's `sha256sum` gate shim compares `${!#}` against `$R9_GATE_TARGET`, which is the
  `//` spelling, so the gate never fires and the ledger is never revoked.

Both failing checks are the ledger ones, exactly as the false failures show:

```
FAIL R9 file ledger revocation was reached: rc=0 output=VERDICT	…/tmp//souji-round9-selftest.tam9PI/ledger-file/fleet/case-shokunin/source.md	NOT-SAFE	none	pushed=dirty-or-untracked-content; obsidian=no-matching-ledger-row; stale=not-scratch-type
FAIL R9 directory ledger revocation was reached: rc=0 output=VERDICT	…/tmp//souji-round9-selftest.tam9PI/ledger-directory/fleet/case-shokunin/source	NOT-SAFE	none	pushed=dirty-or-untracked-content; obsidian=no-matching-ledger-row; stale=not-scratch-type
ROUND9	14	2
```

## Patch (one file, `tools/souji-round9-selftest.sh`)

`deliver-c2-O5.patch` (27 lines, sha256 `eec2866b01cb9e74278729cbf80a9c89b7eeac9e2709eb3fc1b8723c0c265b94`) is
`git -C c diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. `--stat`: `1 file changed, 8 insertions(+), 2 deletions(-)`.
Q71 shape: the scratch root is the caller's `TMPDIR` with redundant trailing slashes removed
(`R9_TMPROOT`, a `while` strip, `/${R9_TMPROOT:-/}` guard), the `mktemp -d` template and the exported
`TMPDIR` both use it; nothing else in the file moves (the fallback stays `/var/tmp` as at base, the
`verify|vault|quarantine` kind refusal and the `${2:?tool path required}` usage refusal are untouched).
`TMPDIR=/` still yields the base `//souji-round9-selftest.XXXXXX` template. `bash -n` passes on both
revisions. The delivered file applies to a fresh prereg checkout and reproduces the candidate blob:
`git -C v apply --check <patch>` OK, then `git -C v hash-object tools/souji-round9-selftest.sh` =
`736af5badbd44184edae912f279583f2f2b0c300` = `git -C c rev-parse e1608b2:tools/souji-round9-selftest.sh`.
No other file changed: `git -C c diff --stat` lists only the helper; the r15 frozen set
does not reference the helper (`grep -rn round9 tests/fixtures/r15-preservation-frozen/` → no match), so
no re-pin is owed.

## Receipt — c2-counter, O5 only

Candidate (`--rev e1608b2b4644b9c7c29f6a02c49d9446765b12f1`); command
`python3 -B <lane>/census/round-33/c2-counter.py --root /fast/scratch/hyaku/souji-r33/FixO5/c --rev e1608b2b4644b9c7c29f6a02c49d9446765b12f1 --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/FixO5/cnt --only O5`

```
LEG	O5	slash	PASS	base=rc0:selftest: 49 checks, 0 failed	rev=rc0:selftest: 49 checks, 0 failed	rev-slash=rc0:selftest: 49 checks, 0 failed
SUMMARY legs=1 pass=1 fail=0 harm=0 partial=1 rev=e1608b2b4644b9c7c29f6a02c49d9446765b12f1
rc=0
```

Red-before, same command with `--rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch …/cnt3`, run
with no other job of mine running:

```
LEG	O5	slash	FAIL	base=rc0:selftest: 49 checks, 0 failed	rev=rc0:selftest: 49 checks, 0 failed	rev-slash=rc1:selftest: 49 checks, 2 failed
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=1
```

(The same sentence reads both ways: the slash condition is the only difference. `partial=1` is the
`--only O5` label the counter prints; the full eleven-leg reading is the L1's run.)

## Receipt — Q73 consumers, base vs candidate

`git -C <clone> grep -l tools/souji-round9-selftest.sh -- tests/fixtures census`: 56 paths at
`2d9bca5` and 56 at `e1608b2` (identical; rc 0 both). SKILL `## Gate registry` rows naming the helper
directly: 0. Rows whose *self-test command* executes it through the tool: `souji-verify`,
`souji-vault-verify`, `souji-quarantine` (3). Their registry form is `TMPDIR=/var/tmp bash tools/<tool> --selftest`
(vault adds `SOUJI_CLI_BIN=/bin/false`).

All nine pairs run from `/fast/scratch/hyaku/souji-r33/FixO5/{b=prereg,c=commit}`, printing `rc` and the
last digit-bearing line:

| TMPDIR | tool | prereg `2d9bca5` | candidate `e1608b2` |
|---|---|---|---|
| `<scratch>/tmp` (no slash) | souji-verify | rc0 `ROUND9	16	0` | rc0 `ROUND9	16	0` |
| `<scratch>/tmp` (no slash) | souji-vault-verify | rc0 `ROUND9	16	0` | rc0 `ROUND9	16	0` |
| `<scratch>/tmp` (no slash) | souji-quarantine | rc1 `ROUND9	6	22` | rc1 `ROUND9	6	22` |
| `<scratch>/tmp/` (slash) | souji-verify | rc1 `ROUND9	14	2` | rc0 `ROUND9	16	0` |
| `<scratch>/tmp/` (slash) | souji-vault-verify | rc1 `ROUND9	12	4` | rc1 `ROUND9	16	0` |
| `<scratch>/tmp/` (slash) | souji-quarantine | rc1 `ROUND9	6	22` | rc1 `ROUND9	6	22` |
| `/var/tmp` (registry form) | souji-verify | rc0 `ROUND9	16	0` | rc0 `ROUND9	16	0` |
| `/var/tmp` (registry form) | souji-vault-verify | rc0 `ROUND9	16	0` | rc0 `ROUND9	16	0` |
| `/var/tmp` (registry form) | souji-quarantine | rc0 `ROUND9	28	0` | rc0 `ROUND9	28	0` |

Read: every no-slash row is byte-identical between base and candidate (the O5 requirement), the registry
form is green on both sides for all three, and the slash rows the helper owns move from red to green
(verify 14/2 → 16/0, vault 12/4 → 16/0). The two rc1 slash rows that stay red are *not* the helper
(see findings 1 and 2).

## Receipt — Q74 refusals

The helper's only guards are the kind refusal and the usage refusal; both are unchanged (same rc, same
message, same line number — the patch does not shift line 5):

| argv | prereg | candidate |
|---|---|---|
| `bogus tools/souji-verify.sh` | rc2 | rc2 |
| `verify` | rc1 (`line 5: 2: tool path required`) | rc1 (same message) |
| `:verify tools/souji-verify.sh` | rc2 | rc2 |
| `verify /nonexistent` | rc1, `FAIL R9 nested-stale refuses ancestor: rc=127 …` | rc1, identical first line |

No write-scope guard existed to keep: the helper writes only inside its `mktemp -d` root and removes it
on `EXIT`; the patch does not widen that root (it strips slashes off the same caller root).

## Findings (for the L1; none is in my file's scope)

1. `tools/souji-vault-verify.sh --selftest` with a trailing-slash `TMPDIR` still exits 1 at the
   candidate, on its *own* harness check, not on the shared helper:
   `FAIL V9: r4='NOT-VERIFIED(row-incomplete)' want='NOT-VERIFIED(source-equals-vault)'`
   (identical line at base). Its `ST_TMP` is built at `tools/souji-vault-verify.sh:1388` from
   `${TMPDIR:-/tmp}` with the same `//` construction; this is a sixth slash site outside the five
   routed defects and outside my write scope.
2. `tools/souji-quarantine.sh --selftest` is red (rc4 `live-fleet-mutation-forbidden` for the N cases,
   22 checks) whenever its `TMPDIR` sits inside `LIVE_FLEET_ROOT` = `dirname` of the tool's checkout
   (`tools/souji-quarantine.sh:168,681`). My first matrix put `TMPDIR` at `<scratch>/tmp`, i.e. under
   the clone's parent → 6/22 on both sides; `TMPDIR=/var/tmp` → 28/0 on both sides. Any future run of
   that selftest must keep `TMPDIR` outside the checkout's parent.
3. One `c2-counter --only O5` red-before run, issued while my own three-tool matrix was still executing,
   returned `rev-slash=rc127:tools/souji-verify.sh: line 1319: /home/vgpnk/.local/bin/git: No such file or directory`
   instead of the expected two-check red. It did not reproduce: the isolated re-run above printed
   `49 checks, 2 failed`, and `/home/vgpnk/.local/bin` was byte-identical before and after a standalone
   slash run (`diff` of `ls -la`, empty). Recorded as a concurrency artifact of two overlapping selftest
   batteries, not as a counter defect — but the O5 reading is not safe to take while another battery runs.
4. Probe noise, not a leg: `TMPDIR=/var/tmp/souji-r33-FixO5-probe bash tools/souji-quarantine.sh --selftest`
   at prereg gave `ROUND9	28	0` with rc1 (`FAIL P1 index shows staged deletion (porcelain keeps path)`),
   while `TMPDIR=/var/tmp` gave rc0. Not measured, not claimed.

## Scratch hygiene

All work under `/fast/scratch/hyaku/souji-r33/FixO5/` (`c` clone, `b` prereg checkout cloned from `c`,
`tmp`, `out`, `cnt`, `cnt2`, `cnt3`); no `origin` remote in either clone; every git call named `-C <clone>`.
`/var/tmp/souji-r33-FixO5-probe` was created by me for finding 4. Both trees are removed before this seat
finishes (`rm -rf /fast/scratch/hyaku/souji-r33/FixO5 /var/tmp/souji-r33-FixO5-probe`); nothing in the lane
or the fleet was deleted, moved or classified.
