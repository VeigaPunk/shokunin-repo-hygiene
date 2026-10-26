# SwarmMutationTester36 — r33 w1: C2 frozen-leg mutation probes

## Status
STATUS: PASS — all four assigned mutant kinds were built in scratch, scored with the frozen c2-counter, and dispositioned: 3 killed, 1 survivor recorded as a coverage finding (M3b/O2). Lane bytes untouched; scratch removed.

## Evidence

Revision chain (scratch clone `/fast/scratch/hyaku/souji-r33/MutateC2Counter/c`, cloned `--no-local`, origin removed at once; all scratch commits with throwaway identity `scratch <scratch@invalid>`):
- base `6017a482e7068d5afb7617640198fbb0fe743357` (lane master at the r32 closure spot-check commit)
- list-rev / preregistration `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`
- R (pristine rebuild) `4aa9fb27bd8635791c40f736b0199026ee1a22d7` = 2d9bca55 + the repair diff appended to `census/round-33/records/feasibility.txt` (`tests/fixtures/r15-census-config.py` TMPDIR→`tempfile.gettempdir()` and default-dir mkdtemp; `tools/souji-census.sh` trailing-slash TMPDIR canonicalisation). Pre-image blobs matched the diff headers (`cf74ace`, `a3fb0a8`).
- m1 `e6d93c557275110c368156a52d69d041ef2931d2` = R + literal `/var/tmp` mkdtemp re-introduced (`r15-census-config.py:1545`)
- m2 `be4c81eff08bb9f4580992cfaeba0b004926a330` = R + selftest summary line changed (`souji-census.sh:3013`)
- m3 `6cc30e5f825b5422c96ba9a3c53ae457e919aa76` = R + sandbox-detection false-green probes (`souji-evidence-cache.py` `_selftest`, `r15-census-config.py` `main`)
- m4 `c95ac3d0c604d7731fdbc71af7fae2409dac9194` = R + `--untracked-files=normal`→`all` (`souji-census.sh:1248`)

Detector (frozen, unmodified): `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c2-counter.py --root <clone> --rev <mutant> --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/MutateC2Counter/cnt --only <legs>`; every run with `PATH=/usr/local/bin:/usr/bin:/bin` (Finding 3).

Runs (verbatim LEG/SUMMARY lines; exit code of each counter run in parens):

1. Pristine R, `--only O2,O4` (exit 0):
   ```
   LEG	O2	sandbox-nt	PASS	base=rc0:SUMMARY total=20 failed=0	sbox=rc0:SUMMARY total=20 failed=0
   LEG	O4	slash	PASS	base=rc1:selftest: 69 checks, 7 failed	rev=rc1:selftest: 69 checks, 7 failed	rev-slash=rc1:selftest: 69 checks, 7 failed
   SUMMARY legs=2 pass=2 fail=0 harm=0 partial=1 rev=4aa9fb27bd8635791c40f736b0199026ee1a22d7
   ```
   O2's readings match the frozen receipt exactly. O4's absolute base reading is drifted (Finding 2) but the leg's relative rule holds (all three readings equal).
2. M1, `--only O2` (exit 1):
   ```
   LEG	O2	sandbox-nt	FAIL	base=rc0:SUMMARY total=20 failed=0	sbox=rc2:r15-census-config: cannot create TMPDIR fixture: [Errno 30] Read-only file system: '<TMP>'
   SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=e6d93c557275110c368156a52d69d041ef2931d2
   ```
3. M2, `--only O4` (exit 1):
   ```
   LEG	O4	slash	FAIL	base=rc1:selftest: 69 checks, 7 failed	rev=rc1:selftest: 69 checks, 7 failed (tmpdir canonicalised)	rev-slash=rc1:selftest: 69 checks, 6 failed (tmpdir canonicalised)
   SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=be4c81eff08bb9f4580992cfaeba0b004926a330
   ```
4. M3, `--only O1,O2` (exit 1):
   ```
   LEG	O1	sandbox	FAIL	base=rc0:W302:selftest: 48/48 passed	sbox=rc0:W0:selftest: 48/48 passed
   LEG	O2	sandbox-nt	PASS	base=rc0:SUMMARY total=20 failed=0	sbox=rc0:SUMMARY total=20 failed=0
   SUMMARY legs=2 pass=1 fail=1 harm=0 partial=1 rev=6cc30e5f825b5422c96ba9a3c53ae457e919aa76
   ```
5. M4, `--only O4,G6` (exit 1):
   ```
   LEG	O4	slash	FAIL	base=rc1:selftest: 69 checks, 6 failed	rev=rc1:selftest: 69 checks, 8 failed	rev-slash=rc1:selftest: 69 checks, 2 failed
   LEG	G6	guard	FAIL	base=rc0:SUMMARY total=29 failed=0	rev=rc1:SUMMARY total=29 failed=1
   SUMMARY legs=2 pass=0 fail=1 harm=1 partial=1 rev=c95ac3d0c604d7731fdbc71af7fae2409dac9194
   ```
6. Direct (unstraced) selftests for attribution, run in the scratch clone:
   - base `6017a482`, no strace: `selftest: 69 checks, 0 failed` (65s) — matches the frozen receipts.
   - base `6017a482`, under the counter's exact strace wrapper (`strace -f -qq -e trace=mkdir,mkdirat,creat,open,openat,openat2`): 7 FAILs, all in the watchdog/timeout cluster (Finding 2); `selftest: 69 checks, 7 failed` (211s).
   - m4, no strace: exactly 2 FAILs, both flip-caused — `FAIL dirty count=3 want 2` and `FAIL showUntrackedFiles=no: dirty=3 want 2`; every watchdog check PASS; `selftest: 69 checks, 2 failed` (48s).

## Findings

1. **[Coverage finding — survivor] The `sandbox-nt` kind has no work attestation.** `census/round-33/c2-legs.tsv:8` (at 2d9bca55): "sandbox-nt  as sandbox, but without the strace wrapper and without the creation-count condition". The counter's sandbox-nt acceptance is `census/round-33/c2-counter.py:174` (at 2d9bca55): `ok = rc1 == rc0 and s1 == s0 and s0 != "NONE"` — no witness term. Observed: a tool that probes `/var/tmp` writability and, on `OSError`, prints its base success line and exits 0 without doing its work PASSES O2 (M3b: `sbox=rc0:SUMMARY total=20 failed=0`, no work done). The sibling `sandbox` kind catches the identical trick on O1 via its creation-count term — `census/round-33/c2-counter.py:178`: `ok = rc1 == rc0 and s1 == s0 and s0 != "NONE" and w1 * 2 >= w0` (M3a: rc and line both matched, killed purely by `W0` vs `W302`). O3 shares O2's kind, so the same false green is available there by construction `[INFERENCE: same kind, not separately executed]`. Reported against the frozen claim; no rule change proposed (amendments are the L1's alone).
2. **[Environment drift] The counter's strace wrapper currently flips 7 census-selftest checks at base.** Direct base selftest without strace: `selftest: 69 checks, 0 failed` (65s). Same commit under the counter's exact strace wrapper: `FAIL watchdog neighbour neighbour-a fields=0/0/error`, `FAIL watchdog neighbour neighbour-b fields=0/0/error`, `FAIL watchdog wall time 13629ms (want < 6000ms)`, `FAIL timed-out FIFO nonblocking open did not return ENXIO (rc=2)`, `FAIL timed-out Git process remains (pid=)`, `FAIL parent SIGKILL cleanup rc=0 launcher=0 census=319273 git= watchdog= tmp=`, `FAIL SIGTERM-ignored run rc=0 flags=clean wall=4130ms` — `selftest: 69 checks, 7 failed` (211s, 3.2x slower). The frozen receipts (L1, earlier today) show `base=rc0:selftest: 69 checks, 0 failed` under the same wrapper, so the wrapper alone is not the cause; current host load (100+ background jobs, dozens of live sibling seats) is the plausible amplifier `[INFERENCE]`. The failed-count also fluctuates between counter runs (pristine 7/7/7; M2 run 7/7/6; M4 run 6/8/2), so the slash legs' equality conditions are load-fragile right now: a C2 landing/tip reading taken under this load could flip O4/O5 spuriously even for a no-op rev. Location: `tools/souji-census.sh` selftest watchdog/timeout checks (watchdog wall-time bound, timed-out-process reaping, SIGKILL/SIGTERM cleanup cluster); wrapper at `census/round-33/c2-counter.py` `run()` (`strace -f -qq`).
3. **[Environment drift] A transient `~/.local/bin/git` entry poisoned the first baseline run.** `tests/fixtures/r15-census-config.py:427` (at 2d9bca55): `found = shutil.which(name)` resolved `git` to `/home/vgpnk/.local/bin/git`, whose exec failed: `r15-census-config: setup command failed (2): /home/vgpnk/.local/bin/git -c maintenance.auto=false -C <TMP> update-ref refs/remotes/origin/master <HEX>: /usr/bin/python3: can't open file '/home/vgpnk/.local/bin/git': [Errno 2] No such file or directory`. That file is absent now (`which -a git` → `/usr/bin/git` only); the caller PATH carries a dozen agent-tooling dirs ahead of `/usr/bin`, so counter readings are caller-PATH-sensitive. All scoring runs above used `PATH=/usr/local/bin:/usr/bin:/bin`. The same drift also explained the first run's `O4 base=rc1:selftest: 69 checks, 6 failed` (fixture setup failures), distinct from Finding 2's strace cluster.
4. **[Stability confirmation] Three base readings reproduce the frozen receipts exactly**: O1 `base=rc0:W302:selftest: 48/48 passed`; O2 `base=rc0:SUMMARY total=20 failed=0`; G6 `base=rc0:SUMMARY total=29 failed=0`. G6's clean base makes M4's harm attribution unambiguous (base `failed=0` → rev `failed=1`).
5. **[Process] One scratch-branching slip, self-caught and corrected**: m2 was first committed on a branch that had inherited M1's hunk; rebuilt from R and verified single-line (`git diff 4aa9fb27..be4c81ef` = one line in `tools/souji-census.sh`). The scored m2 is the rebuilt `be4c81ef`. No other slips.

## Attack log

| mutant | rev | expected | observed | verdict |
|---|---|---|---|---|
| M1: literal `/var/tmp` mkdtemp re-introduced (`tests/fixtures/r15-census-config.py:1545` at base: `SCRATCH = Path(tempfile.mkdtemp(prefix="r15-census-config.", dir="/var/tmp"))`) | `e6d93c557275110c368156a52d69d041ef2931d2` | O2 FAIL | O2 FAIL — sandboxed run dies `rc2` `[Errno 30] Read-only file system` vs base `rc0` | killed |
| M2: TMPDIR canonicalisation kept but no-slash selftest line changed (`tools/souji-census.sh:3013` at base: `st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"`) | `be4c81eff08bb9f4580992cfaeba0b004926a330` | O4 FAIL | O4 FAIL — rev no-slash line carries the appended suffix, ≠ base line (the slash rule's rev==base condition) | killed |
| M3a: sandbox-detection false green in `tools/souji-evidence-cache.py` `_selftest` (probe `mkdtemp(dir="/var/tmp")` at `souji-evidence-cache.py:1295`; on `OSError` print the base line `selftest: 48/48 passed`, exit 0, no work) | `6cc30e5f825b5422c96ba9a3c53ae457e919aa76` | O1 catches it via the strace creation condition | O1 FAIL — `sbox=rc0:W0` vs `base=rc0:W302`: rc and line both matched; killed purely by `w1 * 2 >= w0` | killed |
| M3b: same false green in `tests/fixtures/r15-census-config.py` `main` (on `OSError` print `SUMMARY	total=20	failed=0`, exit 0, no work) | `6cc30e5f825b5422c96ba9a3c53ae457e919aa76` | O2 does NOT catch it (no creation condition) | O2 PASS — `sbox=rc0:SUMMARY total=20 failed=0` with no work done | **SURVIVED — coverage finding (Finding 1)** |
| M4: guard harm — pinned `--untracked-files=normal` dropped (`tools/souji-census.sh:1248` at base: `--untracked-files=normal -- .`), breaking `tests/fixtures/r17-census-hygiene.py` case_04's absolute expectation (`r17-census-hygiene.py:751`: `"r-suf-all": ("1", "0", "1", "dirty"),`; comment `r17-census-hygiene.py:737-739`: "the pinned `normal` mode must collapse it to one") | `c95ac3d0c604d7731fdbc71af7fae2409dac9194` | G6 FAIL counted as harm | G6 FAIL — base `rc0:SUMMARY total=29 failed=0` → rev `rc1:SUMMARY total=29 failed=1`; summary `harm=1`; O4 collateral FAIL (direct run names the two flip-caused selftest failures) | killed |

## Deliveries
- `.ufo/waves/round-33/w1/SwarmMutationTester36.md` — this report (the only lane file I wrote).
- No tool installs or upgrades performed (operator directive 2026-10-19): the task used the pre-present `bwrap`, `strace`, `python3 3.14.8`, `git 2.56.0`.
- Scratch `/fast/scratch/hyaku/souji-r33/MutateC2Counter/` removed after the receipts above were copied; post-cleanup listing of `/fast/scratch/hyaku/souji-r33/` shows only sibling dirs (`FixO3`, `FixO4`, `L1`, `c1.lock`) — untouched.
- Lane state: no `git`/`jj` mutation in the lane (the clone was `--no-local` read-only source; origin removed in the clone only); lane HEAD observed at `a7c35c24bdd8bae5cff9766ace02a81915756701` with 5 pre-existing porcelain entries, none mine; frozen census files verified unchanged since 2d9bca55 (`git diff --stat 2d9bca55 -- census/round-33/c2-counter.py census/round-33/c2-legs.tsv census/round-33/preregistration.txt` empty).
- Leaf member: no subagents dispatched.
