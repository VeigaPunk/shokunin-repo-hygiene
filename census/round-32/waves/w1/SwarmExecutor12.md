# SwarmExecutor12 — r32 w1, C2 item T12 (tools/souji-census.sh)

## Status

STATUS: PASS — `tools/souji-census.sh` now roots census and selftest scratch at `${TMPDIR:-/tmp}` (six literal `/var/tmp` sites plus two child-env overrides), its `/var/tmp/souji-census-now.*` guards now match the TMPDIR-rooted dir with the same strictness, and the frozen C2 counter passes T12 (`fail=0`): base rc0 and sandbox rc0 with identical last digit-bearing line `selftest: 69 checks, 0 failed`. Lane left untouched (HEAD still `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`); no tool installs were needed.

## Evidence

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; prereg `3ec84fc81b3243429c834a051880b0bcde06291c`; scratch commit under test `7503490243600a4c4e9087a212577911167b567f` (scratch clone `/fast/scratch/hyaku/souji-r32/C2Census/r.HR76Pc/c`, branch `r32-c2-census` off base, origin removed).

1. Frozen counter, exact command:

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py \
  --root /fast/scratch/hyaku/souji-r32/C2Census/r.HR76Pc/c \
  --rev 7503490243600a4c4e9087a212577911167b567f \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only T12 --scratch /fast/scratch/hyaku/souji-r32/C2Census/cnt
```

Full output (counter exit 0):

```
ITEM	T12	PASS	base=rc0:W5108:selftest: 69 checks, 0 failed	sbox=rc0:W5479:selftest: 69 checks, 0 failed	
SUMMARY items=1 pass=1 fail=0 partial=1 rev=7503490243600a4c4e9087a212577911167b567f
```

(`sbox` runs under `bwrap` with /tmp, /var/tmp and /dev/shm read-only and TMPDIR a scratch dir; W is the strace creation count.)

2. Patched command with TMPDIR set to `/fast/scratch/hyaku/souji-r32/C2Census/tmp`:

```
rc=0
PASS fixtures under mktemp (/fast/scratch/hyaku/souji-r32/C2Census/tmp/souji-census-selftest.8elp1s)
selftest: 69 checks, 0 failed
```

3. Patched command with TMPDIR unset (`env -u TMPDIR`):

```
rc=0
PASS fixtures under mktemp (/tmp/souji-census-selftest.YcQVnx)
selftest: 69 checks, 0 failed
```

Post-run `ls -d /tmp/souji-census-selftest.*` → `leftover-count=0` (trap cleanup intact); no stderr in either run.

4. `bash -n tools/souji-census.sh` → `SYNTAX-OK`; `grep` sweep for `/var/tmp|/tmp` outside `${TMPDIR:-/tmp}` in the patched file → no hits (comments included). Diff: 1 file, 11 insertions, 10 deletions.

5. Lane read-only check: `git rev-parse HEAD` → `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; `git status --porcelain` → `?? census/round-32/measure.sh` (pre-existing, not mine).

## Findings

1. Base wrote every census/selftest temp root under a literal `/var/tmp`: `tools/souji-census.sh:308` and `:1878` (`CENSUS_TMP=$(mktemp -d /var/tmp/souji-census-now.XXXXXX)`), `:2008` (`ST_TMP=$(mktemp -d /var/tmp/souji-census-selftest.XXXXXX)`). Both now use the template `"${TMPDIR:-/tmp}/…"`, so the caller's scratch root wins and an unset TMPDIR keeps the ordinary `/tmp` default.
2. Guards that recognise the tool's own temp dir were literal-path too and would have stopped matching after the move: `st_worker_tmpdir` at base `:1989` (`/var/tmp/souji-census-now.*/*`) and the SIGTERM/SIGKILL cleanup cases at base `:2905` and `:2969` (`/var/tmp/souji-census-now.*`). Each now matches `"${TMPDIR:-/tmp}"/souji-census-now.*` (and the `/*` suffix in `st_worker_tmpdir`), i.e. the same anchored prefix-plus-glob strictness, just rooted at the caller's TMPDIR; a path outside that root still falls to `return 1` / no cleanup.
3. Child envs at base `:2281` and `:2292` forced `TMPDIR=/var/tmp` on the protected-boundary children; both now pass `TMPDIR="${TMPDIR:-/tmp}"`, i.e. the caller's root. The two assertions (`protected root refused before access`, `protected compare alias refused`) still pass in the 69/0 run.
4. Doc text at base `:10` (`writes only temporary census output under /var/tmp`) and `:80` (`Builds fixture fleets under /var/tmp`) now state `${TMPDIR:-/tmp}`. Comments only; no output or exit code changes.
5. Untouched: no remaining hard-coded temp root anywhere in the file; no test-data string was altered; each command's output lines, cases and exit codes are unchanged (counter compares base vs sandbox and both are `rc0` + the same last line; selftest count unchanged at 69 checks, 0 failed).
6. Observation, no action taken: `/var/tmp/souji-census-now.r8wOm1` and `/var/tmp/souji-census-selftest.OIPDTD` were live (mtime 05:33:36, partial fixture contents, holder is not this seat) during my check, so they belong to a concurrently running seat's unpatched base run; I left them in place. This seat's own runs cleaned up after themselves.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-souji-census.sh` — patched file whole (as committed at `7503490243600a4c4e9087a212577911167b567f`).
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor12.diff` — `git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- tools/souji-census.sh` (uses the lane's mnemonic `c/`…`w/` prefixes; applies with `git apply -p1`).

Scratch `/fast/scratch/hyaku/souji-r32/C2Census` and the throwaway `/fast/scratch/r32census-base.sh` were removed after the deliveries were copied.
