# SwarmExecutor09 — r32 w1 C2 items T07 T08 (operability)

## Status
STATUS: PASS — both assigned items (`T07 tools/souji-cert-evidence.py`, `T08 tools/souji-evidence-cache.py`) honour the caller's `TMPDIR` after a two-site patch each; the frozen C2 counter reports `items=2 pass=2 fail=0` for them, selftest stdout and exit codes are byte-identical to base modulo the scratch path, and no other lane file is touched.

## Evidence

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; scratch clone `/fast/scratch/hyaku/souji-r32/C2Cert/c` (clone of the lane, `origin` removed, `git -C … rev-parse --show-toplevel` printed the clone), patched commit `3f6a069bf07e7e1b41f6f55e8f89eb99aea12f2a` on top of `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.

### 1. Red-before: base tools under a read-only /tmp,/var/tmp,/dev/shm sandbox
Clone `/fast/scratch/hyaku/souji-r32/C2Cert/base` at base; run inside `bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm`, `TMPDIR` a fresh writable dir:

```
BASE-UNDER-SANDBOX tools/souji-cert-evidence.py rc=1
  err: Traceback (most recent call last): … File "…/souji-cert-evidence.py", line 1156, in selftest
       base = Path(tempfile.mkdtemp(prefix="souji-r13-cert-selftest.", dir="/var/tmp"))
       OSError: [Errno 30] Read-only file system: '/var/tmp/souji-r13-cert-selftest.2drkzmet'
BASE-UNDER-SANDBOX tools/souji-evidence-cache.py rc=2
  out-last: selftest-unavailable: [Errno 30] Read-only file system: '/var/tmp/souji-r14-cache-selftest.7433p8ax'
```

Both base tools asked `/var/tmp` for scratch, exactly as the C2 rationale states.

### 2. Frozen C2 counter over my items (v1 counter, unmodified)
```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py \
  --root /fast/scratch/hyaku/souji-r32/C2Cert/c --rev 3f6a069bf07e7e1b41f6f55e8f89eb99aea12f2a \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
  --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only T07,T08 --scratch /fast/scratch/hyaku/souji-r32/C2Cert/cnt
```
```
ITEM	T07	PASS	base=rc0:W275:selftest: 36/36 passed	sbox=rc0:W276:selftest: 36/36 passed	
ITEM	T08	PASS	base=rc0:W302:selftest: 48/48 passed	sbox=rc0:W303:selftest: 48/48 passed	
SUMMARY items=2 pass=2 fail=0 partial=1 rev=3f6a069bf07e7e1b41f6f55e8f89eb99aea12f2a
```
`rc=0`. Work criterion is not dodged: sandbox file creations exceed base (W276/W275, W303/W302), because the scratch tree now lands inside the traced clone-relative TMPDIR.

### 3. Same commands with TMPDIR set and with TMPDIR unset (patched rev)
```
TMPDIR-set   tools/souji-cert-evidence.py  rc=0 last=selftest: 36/36 passed
TMPDIR-unset tools/souji-cert-evidence.py  rc=0 last=selftest: 36/36 passed
TMPDIR-set   tools/souji-evidence-cache.py rc=0 last=selftest: 48/48 passed
TMPDIR-unset tools/souji-evidence-cache.py rc=0 last=selftest: 48/48 passed
```
Residue after the four runs: `ls -d /tmp/souji-r1[34]-*` → `0`; `ls -d $TMPDIR/souji-r1[34]-*` → `0` (every tree removed in its `finally`).

### 4. Output identity base vs rev (TMPDIR set, paths normalised to `<T>`)
```
tools/souji-cert-evidence.py base-rc=0 rev-rc=0 base-lines=37 rev-lines=37   stdout-identical-modulo-scratch
tools/souji-evidence-cache.py base-rc=0 rev-rc=0 base-lines=1 rev-lines=1   stdout-identical-modulo-scratch
```

### 5. Patch scope
`git -C /fast/scratch/hyaku/souji-r32/C2Cert/c show --stat HEAD` → `2 files changed, 18 insertions(+), 15 deletions(-)`; `git status --porcelain` empty. Delivered files are copies of the committed rev:
```
816e8555…f921  .ufo/waves/round-32/w1/deliver-souji-cert-evidence.py
6b826da2…e7297 .ufo/waves/round-32/w1/deliver-souji-evidence-cache.py
```

Tooling: no install or upgrade this wave (nothing needed; no pacman transaction run).

## Findings

1. **T07 root cause** — `tools/souji-cert-evidence.py:994` (`"TMPDIR": "/var/tmp"` in `_selftest_env`, pinned for every child invocation) and `:1156` (`tempfile.mkdtemp(prefix="souji-r13-cert-selftest.", dir="/var/tmp")`). Fixed: child env now forwards the caller's `TMPDIR` only when it is set (`:990-998`), selftest root is `tempfile.mkdtemp(prefix=…)` with no `dir=` (`:1158`).
2. **T08 root cause** — `tools/souji-evidence-cache.py:1295` (`mkdtemp(…, dir="/var/tmp")`) and `:1311` (`"TMPDIR": "/var/tmp"` in the child env). Fixed the same way (`:1295`, `:1308-1315`); `HOME` stays the fixture-local `home` under the scratch base, never `/var/tmp`.
3. **Retained, deliberately unchanged** — `tools/souji-cert-evidence.py:1158` sits outside any `except OSError` (unlike `tools/souji-evidence-cache.py:1294-1298`), so an unusable `TMPDIR` still ends in an uncaught `OSError` traceback with exit 1 instead of the documented exit 2. Changing that would alter an exit code outside the frozen fix rule, so I left it; it is a candidate for a later round with its own contract.
4. **Doc-only edits, no output change** — `tools/souji-cert-evidence.py:132-137` and `:1494` (help text) and `tools/souji-evidence-cache.py:32-35` now say the selftest builds under the caller's `TMPDIR`; `/var/tmp` mentions that are behavioural examples (`tools/souji-evidence-cache.py:144`, `:379`) are untouched, and no output line, case or exit code moved (Evidence 4).
5. **Non-claims kept out** — `tests/fixtures/r13-cert-evidence.py:8-9,36,112` and `tests/fixtures/r14-evidence-cache.py:18,154,166` own their own `/var/tmp` scratch but are outside the C2 set (rule: r20–r31 only) and are not my items; I did not edit them.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-souji-cert-evidence.py` (whole patched file)
- `.ufo/waves/round-32/w1/deliver-souji-evidence-cache.py` (whole patched file)
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor09.diff` (`git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- tools/souji-cert-evidence.py tools/souji-evidence-cache.py`)

Scratch `/fast/scratch/hyaku/souji-r32/C2Cert` removed after the copies were verified; nothing in the lane working tree, index, jj state or any sibling repo was written.
