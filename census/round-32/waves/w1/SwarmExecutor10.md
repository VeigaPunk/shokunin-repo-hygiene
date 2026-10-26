# SwarmExecutor10 — r32 C2 items T09, T10

## Status

STATUS: PASS — both enumerated items now pass the frozen C2 counter at the delivered rev (`items=2 pass=2 fail=0`), with exit code and last line identical to the base run and file work preserved; base-state failures reproduced under the same sandbox.

## Evidence

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; prereg `3ec84fc81b3243429c834a051880b0bcde06291c`; controls `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`. Work done in scratch clone `/fast/scratch/hyaku/souji-r32/C2Pres/c` (origin removed, `rev-parse --show-toplevel` printed the clone before its first commit), patched commit `9b560964da088aba10f78dc7ab35b684b4e587d4`.

Counter (frozen, unmodified), full output:

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py \
    --root /fast/scratch/hyaku/souji-r32/C2Pres/c --rev 9b560964da088aba10f78dc7ab35b684b4e587d4 \
    --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
    --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
    --only T09,T10 --scratch /fast/scratch/hyaku/souji-r32/C2Pres/cnt
ITEM	T09	PASS	base=rc0:W364:selftest: 47/47 passed	sbox=rc0:W365:selftest: 47/47 passed
ITEM	T10	PASS	base=rc0:W60:SELFTEST pass=118 fail=0	sbox=rc0:W61:SELFTEST pass=118 fail=0
SUMMARY items=2 pass=2 fail=0 partial=1 rev=9b560964da088aba10f78dc7ab35b684b4e587d4
COUNTER-RC=0
```

Both patched commands, run once with `TMPDIR` unset and once with `TMPDIR=/fast/scratch/hyaku/souji-r32/C2Pres/tmp`, from the clone root (cwd as the counter uses):

```
T09 [unset] rc=0 last=selftest: 47/47 passed
T10 [unset] rc=0 last=SELFTEST	pass=118	fail=0
T09 [set]   rc=0 last=selftest: 47/47 passed
T10 [set]   rc=0 last=SELFTEST	pass=118	fail=0
```

Base state under the counter's sandbox (`bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm`, `TMPDIR` a scratch dir), base clone `cbase` at `85b61a15`:

```
T09 base-sbox rc=2 last=selftest-unavailable: [Errno 30] Read-only file system: '/var/tmp/souji-r15-preservation-selftest.n74_pls3'
T09 rev-sbox  rc=0 last=selftest: 47/47 passed
T10 base-sbox rc=1 last=PASS	h8-trunc-header-rel
T10 rev-sbox  rc=0 last=SELFTEST	pass=118	fail=0
```

Base T10 stderr tail (`tools/souji-seat-audit.py --selftest` under sandbox):

```
  File "/usr/lib/python3.14/tempfile.py", line 381, in mkdtemp
    _os.mkdir(file, 0o700)
OSError: [Errno 30] Read-only file system: '/var/tmp/tmpvk7z1bv6'
```

Positive proof the creations are now TMPDIR-rooted (strace `mkdir,mkdirat,openat` counted per the counter's rule, `TMPDIR=/fast/scratch/hyaku/souji-r32/C2Pres/probe`, patched rev):

```
tools/souji-preservation-evidence.py rc=0 created=365 under_TMPDIR=365 forbidden=[]
tools/souji-seat-audit.py            rc=0 created=61  under_TMPDIR=61  forbidden=[]
```

`forbidden` is any creation path starting `/var/tmp`, `/tmp/` or `/dev/shm` — none. Base-state claim: `census/round-32/c2-items.tsv` header, rule sentence, "whose code creates scratch under a literal /tmp or /var/tmp"; preregistration C2 paragraph, "tools and fixtures create scratch under a literal /var/tmp or /tmp whatever TMPDIR says".

`--help` output byte-identical to base for both files (`HELP-IDENTICAL` for each), so no non-selftest surface moved. Clone working tree clean after the run (`git -C … status --porcelain` empty).

## Findings

1. **T09 defect at base, fixed.** `tools/souji-preservation-evidence.py:1956` (`tempfile.mkdtemp(prefix="souji-r15-preservation-selftest.", dir="/var/tmp")`) and its child env at `:1976` (`"TMPDIR": "/var/tmp"`). Sandboxed, the mkdtemp fails and the selftest degrades to `selftest-unavailable` exit 2. Fix: `mkdtemp(prefix=…)` with no `dir` (tempfile honours `TMPDIR`), and the child env now gets `os.environ.get("TMPDIR") or str(base)` — the caller's root when set, otherwise this selftest's own tree, never a shared `/var/tmp`. The `except OSError` → exit 2 path, every case, and `selftest: 47/47 passed` are unchanged.
2. **T10 defect at base, fixed.** `tools/souji-seat-audit.py:667`, `:680`, `:702` used `tempfile.TemporaryDirectory(dir="/var/tmp")`; the first block aborts the selftest (`OSError` above), so the base run printed only the parser cases and exited 1 with no `SELFTEST` summary. Fix: `tempfile.TemporaryDirectory()` in all three (same call sites, same bodies). `SELFTEST	pass=118	fail=0` matches base exactly.
3. **Stale docstring at `tools/souji-preservation-evidence.py:32`** said the selftest "builds isolated synthetic roots under `/var/tmp`". Reworded to the caller's `TMPDIR`. No CLI output depends on the module docstring (`argparse` uses the short `description=`), confirmed by the identical `--help` comparison.
4. **Deliberately unchanged (out of C2's creation rule).** `tools/souji-seat-audit.py` keeps every `/var/tmp` string that is contract or test data and creates no files: `LIVE_CENSUS_RE` `:90`, `ABS_RE` `:128`, the `scratch_path()` declaration regex `:204`/`:208`, the legacy `CLONES:` regex `:217`, `seat_scratch` and the synthetic transcript rows `:537–:654`. Likewise `tools/souji-preservation-evidence.py:1841` `_arm(tool_path="/var/tmp/tool.sh")` is declared-record data only (`_arm` builds dicts; no filesystem call).
5. **Residual risk, not fixed here (outside the frozen item set).** `scratch_path()` at `tools/souji-seat-audit.py:203-209` accepts a seat scratch declaration only as `/var/tmp/souji-r<N>[w<slot>]-<Name>`, and `LIVE_CENSUS_RE` at `:90` treats any census `--root` outside `/var/tmp` as major. Under this round's operator directive (scratch and clones under `/fast/scratch/hyaku/souji-r32/<Seat>/`) a seat's declared scratch grants nothing and its own scratch writes are reported `V-WRITE-SCOPE` major. No enumerated C2 item exercises it (T10 runs `--selftest` only), so changing it would alter a pinned contract inside a claim this seat does not own; flagged for wave 2 / L1. `[INFERENCE]` for the false-major consequence — I did not run the auditor against a `/fast/scratch` transcript.
6. **Counter observation, not an attack.** `normalize()` maps both `/var/tmp/...` and `TMPDIR`-rooted paths to `<TMP>`, so an ITEM PASS alone cannot show which root was used. That is why the strace creation census in Evidence is included; it is not a defect in the frozen predicate, which measures exit code, last line and work volume as registered.

## Attack log

No attack filed: I found no counter or predicate to be gameable within the frozen C2 rule, and my items are repairs, not falsifiers. Finding 6 records the one place where a PASS is weaker than it looks, with the compensating measurement reproduced above.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-souji-preservation-evidence.py` — whole patched file, 2655 lines, sha256 `0b6c4904ec5de95b51e02c2a31e3ac40086fdd5117ced1d0f835d899c035f2f9`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-souji-seat-audit.py` — whole patched file, 801 lines, sha256 `e6fca3e176c85a0dc2e1295dfed52c563a035cbe759611efe558ba4d1ae953cd`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-SwarmExecutor10.diff` — `git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- tools/souji-preservation-evidence.py tools/souji-seat-audit.py`, 68 lines, sha256 `fc72d19fcbcbcbd7ad3dd17478f2621bee5488ccb53c1e8c2d7c824eed90c236`

Both delivered binaries are byte-identical to the files the counter measured (`cmp` OK on each). Scratch `/fast/scratch/hyaku/souji-r32/C2Pres` removed after copying. No pacman, no tool installs, no lane git or jj mutation, no write outside my report and the three delivery files.
