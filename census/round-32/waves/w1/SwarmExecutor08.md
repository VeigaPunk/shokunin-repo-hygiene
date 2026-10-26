# SwarmExecutor08 — r32 w1, C2 operability, items T03 T04 T05 T06

## Status

STATUS: PASS — the three named tools now derive their selftest scratch from the caller's TMPDIR; under the frozen C2 counter all four items PASS (`SUMMARY items=4 pass=4 fail=0`), where 3 of 4 FAILED at base with the same instrument.

## Evidence

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg/controls head at clone time `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`, `--list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`. Scratch clone `/fast/scratch/hyaku/souji-r32/C2Decl/r.Hisg5X/c` (origin removed, `rev-parse --show-toplevel` = the clone), patch committed there as `5f0b4bf7fa3f0a3181bc2db3080c5e640f6dcc71`. The three files are byte-identical between base and that clone's parent (`git diff --stat 85b61a1 -- tools/souji-declared-evidence.py tools/souji-gate-check.py tools/souji-rev-pin.py` → empty), so the delivered diff is exactly this patch.

### Red-before (same counter, `--rev <base>`)

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py --root <clone> \
    --rev 85b61a151923986e7e6b48f7084b9122561b5f3d --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
    --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T03,T04,T05,T06 --scratch <scratch>/cnt-red
ITEM	T03	PASS	base=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23	sbox=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23
ITEM	T04	FAIL	base=rc0:W86:selftest=8/8	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
ITEM	T05	FAIL	base=rc0:W20:selftest=9/9	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
ITEM	T06	FAIL	base=rc0:W110:SUMMARY total=11 failed=0	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
SUMMARY items=4 pass=1 fail=3 partial=1 rev=85b61a151923986e7e6b48f7084b9122561b5f3d
rc=1
```

### Green (patched)

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py --root <clone> \
    --rev 5f0b4bf7fa3f0a3181bc2db3080c5e640f6dcc71 --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
    --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T03,T04,T05,T06 --scratch <scratch>/cnt
ITEM	T03	PASS	base=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23	sbox=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23
ITEM	T04	PASS	base=rc0:W87:selftest=8/8	sbox=rc0:W88:selftest=8/8
ITEM	T05	PASS	base=rc0:W20:selftest=9/9	sbox=rc0:W21:selftest=9/9
ITEM	T06	PASS	base=rc0:W110:SUMMARY total=11 failed=0	sbox=rc0:W111:SUMMARY total=11 failed=0
SUMMARY items=4 pass=4 fail=0 partial=1 rev=5f0b4bf7fa3f0a3181bc2db3080c5e640f6dcc71
rc=0
```

### Every patched command, TMPDIR unset and TMPDIR set (patched clone, rc + last digit-bearing line)

```
T03 tmp=unset rc=1 last=[assertions=252 resolved=229 skipped=401 mismatches=23]
T04 tmp=unset rc=0 last=[selftest=8/8]
T05 tmp=unset rc=0 last=[selftest=9/9]
T06 tmp=unset rc=0 last=[SUMMARY total=11 failed=0]
T03 tmp=set   rc=1 last=[assertions=252 resolved=229 skipped=401 mismatches=23]
T04 tmp=set   rc=0 last=[selftest=8/8]
T05 tmp=set   rc=0 last=[selftest=9/9]
T06 tmp=set   rc=0 last=[SUMMARY total=11 failed=0]
```

Identical to the base-run readings (base column above), so no output line, case or exit code moved.

### TMPDIR actually used (patched clone, `strace -f -e trace=mkdir,mkdirat`)

```
$ TMPDIR=<scratch>/probe strace -f -qq -o probe.log -e trace=mkdir,mkdirat python3 -B tools/souji-gate-check.py --selftest
selftest=9/9
$ grep -c <scratch>/probe probe.log        # 15
670882 mkdir("/fast/scratch/hyaku/souji-r32/C2Decl/probe/souji-gate-check-xv_072a7", 0700) = 0
670882 mkdir(".../probe/souji-gate-check-xv_072a7/corpus", 0777) = 0
670882 mkdir(".../probe/souji-gate-check-xv_072a7/census", 0777) = 0
$ ls -A <scratch>/probe | wc -l           # 0  (fixture root created under TMPDIR and removed)
```

Negative control: `TMPDIR=<scratch>/ro` (mode 500) → `rc=0` for both selftests, because Python's `tempfile` skips an unusable candidate and falls back to `/tmp` (Finding 4). The counter's TMPDIR is always a fresh writable dir under `--scratch`, so this does not affect the target.

No leftover dirs: `ls -d /tmp/souji-declared-evidence-* /tmp/souji-gate-check-* /tmp/souji-rev-pin-selftest-*` → no match (rc 2); the TMPDIR-unset runs wrote only small self-cleaned fixtures to `/tmp`.

Delivered diff applies to a clean base checkout: `git -C <fresh clone at 85b61a1> apply --check` on `deliver-SwarmExecutor08.diff` → rc 0, `3 files changed, 7 insertions(+), 4 deletions(-)`.

## Findings

1. All three selftests pinned their fixture root to a literal `/var/tmp`, so any caller whose scratch root is elsewhere (the operator `/fast/scratch/hyaku` discipline) either leaked into `/var/tmp` or, under a read-only `/var/tmp`, died before running a case. Locations at base: `tools/souji-declared-evidence.py:265` ``base = tempfile.mkdtemp(prefix="souji-declared-evidence-", dir="/var/tmp")``, `tools/souji-gate-check.py:231` ``base = tempfile.mkdtemp(prefix="souji-gate-check-", dir="/var/tmp")``, `tools/souji-rev-pin.py:253` ``top = tempfile.mkdtemp(prefix="souji-rev-pin-selftest-", dir="/var/tmp")``.
2. Fix: `dir=` dropped in those three calls, so `tempfile` resolves the root through `TMPDIR`; each site carries a one-line comment stating the invariant. Nothing else changed — no case, name, output line, ordering or exit code, and no non-selftest code path (T03, the only item that touches the audit path, reads identically `assertions=252 resolved=229 skipped=401 mismatches=23` rc 1 before and after).
3. `tools/souji-declared-evidence.py:18` documented the old behaviour — base text ``Exit 0 iff M == 0.  Read-only: git plumbing only, scratch under /var/tmp.`` — now ``scratch under $TMPDIR.``. It is a docstring, not printed by any counted command; `--root`/`--rev` output is unaffected.
4. Limit, observed not hidden: with `TMPDIR` pointing at a non-writable directory the selftests still exit 0, because Python's `tempfile` falls back to `/tmp` when no candidate is usable. That is stdlib semantics and outside this item's fix rule ("drop the hard-coded dir="); under the counter the caller always supplies a writable TMPDIR, and under bwrap a `/tmp` fallback would surface as the same EROFS the items used to show, i.e. it cannot produce a silent pass in the sandbox.
5. `SCORECARD.md:171` still says of this tool, verbatim `read-only, git plumbing only, /var/tmp scratch;` — after this patch that sentence is false. `SCORECARD.md` is not in this seat's write scope; the L1 owns it (and the prereg's landing-text discipline / sentence-to-record sweep). Only this one SCORECARD row mentions `/var/tmp` for these three tools; `tools/souji-gate-check.py` and `tools/souji-rev-pin.py` rows (`SCORECARD.md:32,167,388`) carry no scratch-location sentence.
6. The counter's BASE clone still runs the base blob, which creates and removes its fixture dir under `/var/tmp`; after the red-before and green runs no `souji-declared-evidence-`/`souji-gate-check-`/`souji-rev-pin-selftest-` directory remains (`/var/tmp` holds only unrelated older `souji-r23-*` files this seat did not touch).
7. Write scope held: only `tools/souji-declared-evidence.py`, `tools/souji-gate-check.py`, `tools/souji-rev-pin.py` inside the scratch clone (committed `5f0b4bf`), plus this report and the delivery files under `.ufo/waves/round-32/w1/`. No lane git/jj mutation, no `rm`/`mv` of anything this seat did not create (the only `mv` renamed the three whole-file deliveries this seat copied into `w1/`), nothing touched under `/home/vgpnk/Projects/shokunin` outside `souji-shokunin/`, no network command, no tool installs (no new tool version to record).

## Attack log

Not an attack seat; no counter predicate is claimed wrong here. The nearest attackable observation is Finding 4 (stdout/green comparison is unaffected, but a future item whose fixture root can fall back to `/tmp` would pass outside the sandbox while failing inside it — recorded as a limit, not reproduced as a counter defect).

## Deliveries

All under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/`:

| file | sha256 | note |
|---|---|---|
| `deliver-souji-declared-evidence.py` | `a332491607129195f59d289b431cc29fb4c8dc21e10859d552700697a3b09831` | whole file at `5f0b4bf`, equals `git cat-file blob 5f0b4bf:tools/souji-declared-evidence.py` |
| `deliver-souji-gate-check.py` | `ea268127618b765af6c1dd22735c7dbff068dbb0b2dfbefc78be4df7a7e08b06` | whole file at `5f0b4bf` |
| `deliver-souji-rev-pin.py` | `e41c74d08874d8f6a7f195364682ed78424c346d4c1ce95b117eab535130072a` | whole file at `5f0b4bf` |
| `deliver-SwarmExecutor08.diff` | `3e308566466bb72ddf385bfb27f491468698811327c9f551c97cdfe220da7835` | `git -C <clone> -c diff.mnemonicPrefix=false diff --src-prefix=a/ --dst-prefix=b/ 85b61a151923986e7e6b48f7084b9122561b5f3d -- tools/souji-declared-evidence.py tools/souji-gate-check.py tools/souji-rev-pin.py` |

Checks the L1 should run after integration: the frozen C2 counter with the full item set at the integrated tip (`--rev <tip>`), and the same four-item `--only` lane for C2's own record.
