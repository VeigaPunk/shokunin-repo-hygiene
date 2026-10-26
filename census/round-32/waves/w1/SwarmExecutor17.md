# SwarmExecutor17 — C2Fix27 (r32 w1, items T26 T27)

## Status
STATUS: PASS — both assigned C2 items now run under the bwrap read-only /tmp, /var/tmp, /dev/shm sandbox with a caller TMPDIR (`SUMMARY items=2 pass=2 fail=0`); red-before reproduced at base (T26 sbox rc1, T27 sbox rc98); every other output line, case and exit code unchanged.

## Evidence

Claim scope: C2 (operability) of `census/round-32/records/preregistration.txt`, items T26/T27 of `census/round-32/c2-items.tsv`.
Base `85b61a151923986e7e6b48f7084b9122561b5f3d`; list-rev (prereg) `3ec84fc81b3243429c834a051880b0bcde06291c`; patched scratch commit `e20bacef6da1e14e38f78be170e8766aa652f253` (base + one commit, scratch clone at `/fast/scratch/hyaku/souji-r32/C2Fix27/c`, origin removed, deleted after delivery).

Red-before, base as both --base and --rev (sandboxed run is the patched-vs-base discriminator):

```
python3 -B .../census/round-32/c2-counter.py --root <scratch>/c \
  --rev 85b61a151923986e7e6b48f7084b9122561b5f3d --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T26,T27 --scratch <scratch>/cnt2
ITEM  T26  FAIL  base=rc0:W536:cases=4 pass=4 control=FALSE-GREEN-REJECTED   sbox=rc1:W0:NONE   regress work-dropped
ITEM  T27  FAIL  base=rc0:W735:cases=15 pass=15 control=TAMPER-REJECTED      sbox=rc98:W0:NONE  regress work-dropped
SUMMARY items=2 pass=0 fail=2 partial=1 rev=85b61a151923986e7e6b48f7084b9122561b5f3d
```

After the patch:

```
python3 -B .../census/round-32/c2-counter.py --root <scratch>/c \
  --rev e20bacef6da1e14e38f78be170e8766aa652f253 --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T26,T27 --scratch <scratch>/cnt
ITEM  T26  PASS  base=rc0:W538:cases=4 pass=4 control=FALSE-GREEN-REJECTED   sbox=rc0:W537:cases=4 pass=4 control=FALSE-GREEN-REJECTED
ITEM  T27  PASS  base=rc0:W736:cases=15 pass=15 control=TAMPER-REJECTED      sbox=rc0:W737:cases=15 pass=15 control=TAMPER-REJECTED
SUMMARY items=2 pass=2 fail=0 partial=1 rev=e20bacef6da1e14e38f78be170e8766aa652f253
COUNTER_RC=0
```

Creation counts inside the sandbox are 537/538 and 737/736, i.e. the file work is preserved (contract requires `w1*2 >= w0`), and the last digit-bearing line is byte-identical between base and sandboxed run.

Direct runs of the patched files at `e20bacef`, TMPDIR unset (fallback `${TMPDIR:-/tmp}`) and TMPDIR set to a scratch dir:

```
T26-notmpdir  rc=0  last=cases=4 pass=4 control=FALSE-GREEN-REJECTED
T27-notmpdir  rc=0  last=cases=15 pass=15 control=TAMPER-REJECTED
T26-TMPDIR    rc=0  last=cases=4 pass=4 control=FALSE-GREEN-REJECTED
T27-TMPDIR    rc=0  last=cases=15 pass=15 control=TAMPER-REJECTED
```

Patch on base applies cleanly (`git -C <base worktree> apply --check deliver-C2Fix27.diff`): `APPLY-CHECK=OK`. Delivered whole files are `cmp`-identical to the patched blobs.

## Findings

1. `tests/fixtures/r27-pre-report-gate.sh:7` created its whole per-run tree under a literal host root — pre-patch bytes: `D=$(mktemp -d /var/tmp/souji-r27-pre-report.XXXXXX)` — so the sandboxed run died at rc1 before any case ran (red-before line above). Fixed to `${TMPDIR:-/tmp}`-rooted; all four cases plus the false-green control still run, exit 0, same final line.
2. `tests/fixtures/r28-wave-evidence-capture.sh:51` defaulted its scratch root to a literal host path — pre-patch bytes: `scratch_root=${SOUJI_R29_C2FIXTURE_BASE:-/var/tmp/souji-r29-wave-capture-fixture}` — so `mkdir -p` hit the read-only mount and the fixture took its `|| exit 98` path (red-before rc98, matching the ticket). Fixed to `${TMPDIR:-/tmp}`-rooted; `SOUJI_R29_C2FIXTURE_BASE` still overrides. Header comment at `:11`, which documented the old default, updated to the same expression so the file's documentation does not contradict its code.
3. No other literal `/tmp` `/var/tmp` creation site exists in either file: pre-patch `grep -n -E '/var/tmp|/tmp'` over both files returned exactly lines 7 (r27) and 11, 51 (r28); post-patch the only matches are the TMPDIR-rooted forms. Test-data strings that merely mention paths were not touched — neither file carries any, so the synthetic-transcript caveat did not apply.
4. Behaviour identity held beyond the compared line: r27 still prints `case-*=PASS` + `control=FALSE-GREEN-REJECTED`, r28 still prints `cases=15 pass=15 control=TAMPER-REJECTED` including the committed-bytes cases 7-12 and 15, which build their own scratch git repos under the (now TMPDIR-rooted) run dir.
5. Scratch discipline: all work under `/fast/scratch/hyaku/souji-r32/C2Fix27/` (clone, counter scratch, TMPDIR), origin removed after clone, `rev-parse --show-toplevel` verified before the first commit, throwaway identity set with `git -C` inside scratch only; the directory was deleted after delivery. The counter's own unsandboxed base run left an empty `/var/tmp/souji-r29-wave-capture-fixture` (created by that run, timestamp 05:29); I removed it with `rmdir` after confirming zero entries, and the TMPDIR-unset direct run's empty `/tmp/souji-r29-wave-capture-fixture` likewise. No file outside the lane was written; lane git index/jj untouched; no tool installed, so no install record.

Risks: `${TMPDIR:-/tmp}` deliberately keeps a fallback, so a sandboxed invocation that unsets TMPDIR would still fail — the frozen rule is that the caller passes TMPDIR (the counter does), and the fallback is what keeps the direct TMPDIR-unset run working. `[INFERENCE]` Since the two files now only read TMPDIR, older lanes that set nothing keep their previous `/tmp` behaviour.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-r27-pre-report-gate.sh` (whole patched file, mode 755)
- `.ufo/waves/round-32/w1/deliver-r28-wave-evidence-capture.sh` (whole patched file, mode 755)
- `.ufo/waves/round-32/w1/deliver-C2Fix27.diff` (vs `85b61a151923986e7e6b48f7084b9122561b5f3d`)
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor17.diff` (byte-identical copy of the same diff under the seat-id name used by sibling deliveries; sha256 `6bff1c8237d648170a2f2f29e316b945a500cdc06016fd945e8ea99e5eb94798` for both)
