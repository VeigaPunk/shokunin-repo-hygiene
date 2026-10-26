# SwarmExecutor30 — r33 w1, C2 leg O3

## Status

STATUS: PASS — the scoped repair is complete: `tests/fixtures/r15-preservation-frozen/regenerate.py` takes its scratch root from `TMPDIR` (two changed lines, no other file touched), red-before reproduces the base `OSError` and the patched tree gets past it, Q73/Q74 receipts green. **The frozen leg itself still reads FAIL at the C2 landing commit** for a cause outside the five repaired files (`tests/fixtures/r14-census-boundary.py` + the checker's `NAMESPACE_SHA256` literal), reproduced in §4 and routed to the L1 — my file is not that blocker.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `6017a482e7068d5afb7617640198fbb0fe743357`, prereg/list-rev `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Scratch `/fast/scratch/hyaku/souji-r33/FixO3` (`TMPDIR=/fast/scratch/hyaku/souji-r33/FixO3/tmp`), clones made with `git clone -q --no-local … ; git remote remove origin`, throwaway identity only for scratch commits. No tool installed or upgraded this run.

### 1. The patch (delivery `deliver-c2-O3.patch`)

```
$ git -C /fast/scratch/hyaku/souji-r33/FixO3/c diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2
 tests/fixtures/r15-preservation-frozen/regenerate.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```
```diff
-private /var/tmp directory (removed afterwards). The fixtures run from the
+private TMPDIR directory (removed afterwards). The fixtures run from the
-    scratch = Path(tempfile.mkdtemp(prefix="souji-r16-repin.", dir="/var/tmp"))
+    scratch = Path(tempfile.mkdtemp(prefix="souji-r16-repin."))
```
Scratch commit `32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2` (parent 2d9bca). `git apply --check` on a pristine 2d9bca work tree: `APPLIES CLEANLY AT BASE`. `git diff --name-only 2d9bca 32f48f9` prints only that one path. Q71: Python `tempfile` without `dir=` (→ `TMPDIR`); the file passes no `env=` to any child, so children already inherit the caller's `TMPDIR`; nothing else changes.

**Already integrated:** the L1 landed these exact bytes in lane commit `a7c35c24bdd8bae5cff9766ace02a81915756701` ("round-33: C2 scratch-discipline repairs O1-O5 …"). `git show a7c35c2:tests/fixtures/r15-preservation-frozen/regenerate.py` compares byte-identical (`cmp`) with `git show 32f48f9:…`, both sha256 `e2428676d1e8a0bbd885e624482cd3af6e0a80f3ceee87285ee67f5edaaf4d78`.

### 2. Red-before — frozen O3 leg at 2d9bca (unrepaired)

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c2-counter.py \
    --root /fast/scratch/hyaku/souji-r33/FixO3/c --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/FixO3/cnt --only O3
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean	sbox=rc1:OSError: [Errno 30] Read-only file system: '<TMP>'
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
(exit 1)
```

### 3. After — frozen O3 leg at the O3 commit, measured alone

```
$ python3 -B …/c2-counter.py --root /fast/scratch/hyaku/souji-r33/FixO3/c \
    --rev 32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2 --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/FixO3/cnt --only O3
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean	sbox=rc1:regenerate: tests/fixtures/r15-census-config.py on <HEX> could not evaluate (rc=2)
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2
(exit 1)
```

The repair works — the run now gets past `mkdtemp` into the arms — and then dies in its own **child**: `regenerate.py` runs `tests/fixtures/r15-census-config.py` once per arm, and at a tree that has only O3 that fixture still creates `dir="/var/tmp"` (O2's file), exits 2 under the sandbox, and `regenerate.py` converts that into `could not evaluate (rc=2)`. An `--only O3` reading on an O3-only tree therefore cannot PASS; see finding 2. This is why the C2 landing commit carries all five repairs.

### 4. Landing reading — frozen O3 leg at the C2 landing commit `a7c35c2`

The L1 landed my bytes in `a7c35c24bdd8bae5cff9766ace02a81915756701`; the leg was measured on a clone of that commit (`/fast/scratch/hyaku/souji-r33/FixO3/land`):

```
$ python3 -B …/c2-counter.py --root /fast/scratch/hyaku/souji-r33/FixO3/land \
    --rev a7c35c24bdd8bae5cff9766ace02a81915756701 --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/FixO3/cnt --only O3
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean	sbox=rc1:regenerate: tests/fixtures/r14-census-boundary.py on <HEX> could not evaluate (rc=2)
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=a7c35c24bdd8bae5cff9766ace02a81915756701
(exit 1)
```

All five repairs are present and the run still fails — now in `regenerate.py`'s **namespace arm**, which runs `tests/fixtures/r14-census-boundary.py`, a file outside the five repaired files and itself still literal-`/var/tmp` (`:691 mkdtemp(… dir="/var/tmp")`, `:368 "TMPDIR": "/var/tmp"`). Isolated under the counter's exact sandbox at the landing commit:

```
$ bwrap --dev-bind / / --ro-bind <empty 555> /tmp --ro-bind <empty 555> /var/tmp --ro-bind <empty 555> /dev/shm \
    --chdir <land> python3 -B tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
rc=2  r14-census-boundary: cannot create /var/tmp fixture: [Errno 30] Read-only file system: '/var/tmp/r14-census-boundary.q0jqfc4_'
$ same command, plain
rc=0  SUMMARY	total=12	failed=0
```

Reachability probe (**scratch only, NOT delivered, NOT mine**): landing tree plus a Q71-shaped scratch-root change to `r14-census-boundary.py` alone (`423bcd52b960762752afb37bd19caa235996a49c`) still fails, now at the checker's literal pin:

```
LEG	O3	sandbox-nt	FAIL	base=rc0:… verdict=clean	sbox=rc3:finding pinned-mismatch: namespace_fixture.sha256=<HEX> is not the pinned r14 digest <HEX>
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=423bcd52b960762752afb37bd19caa235996a49c
$ (ns clone) python3 -B tools/souji-preservation-evidence.py --selftest
selftest-unavailable: …/tests/fixtures/r14-census-boundary.py missing or differs from the pinned r14 digest
```

`tools/souji-preservation-evidence.py:307 NAMESPACE_SHA256 = e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2` equals both the landing file's sha256 and `expected.json files["tests/fixtures/r14-census-boundary.py"]`. So O3's PASS needs r14's scratch root **and** that literal **and** the r15 re-pin: wider than the prereg's five files. That is the L1's decision; the repair in my file is complete and is not the blocker.

### 5. Sandbox margin (why readings can read FAIL without a defect)

`regenerate.py` caps every arm at `timeout 300`. The sandboxed child fixture at the landing commit measured **254 s** (`bwrap … python3 -B tests/fixtures/r15-census-config.py --tool tools/souji-census.sh` → rc0 `SUMMARY total=20 failed=0`, load average 31-51), and two attempts at load ~60 returned `could not evaluate (rc=124)`; one earlier invocation printed the *base* line as `could not evaluate (rc=124)` (`base=rc1`). Contention cannot turn a FAIL into a PASS, but it can hide an honest PASS.

### 6. Q73 — consumers, pins, registered gates

- `git grep -l tests/fixtures/r15-preservation-frozen/regenerate.py <REV> -- tests/fixtures census` → rc 0 at both `2d9bca` and `32f48f9`, the same 17 paths at both revisions: ten `census/round-16/transcripts/…` files, `census/round-18/final-verification-4800fd7.json`, `census/round-26/waves/assimilation/validate/corpus/lessons/round-16.md`, the assimilation copy `census/round-26/waves/assimilation/validate/tests/fixtures/r15-preservation-frozen/regenerate.py`, `census/round-26/waves/manifest.sha256`, `census/round-32/records/a2-repairs.txt`, `census/round-33/c2-legs.tsv`, `census/round-33/preregistration.txt`, and the file itself. All are historical evidence, the assimilation snapshot, or this round's frozen item text.
- No executable consumer: `grep -rn "regenerate.py" --include=*.py --include=*.sh tools tests` (excluding the file) → no match. `grep -c regenerate` in `tests/fixtures/r15-preservation-frozen/expected.json` and `record.json` → `0` and `0`.
- No byte pin of this file: `expected.json`'s `files` map is `['tests/fixtures/r14-census-boundary.py', 'tests/fixtures/r15-census-config.py', 'tools/souji-census.sh']`. `census/round-26/waves/manifest.sha256:119` pins the **assimilation copy** `./assimilation/validate/tests/fixtures/r15-preservation-frozen/regenerate.py` = `f34fadb9…`, which equals that copy's own sha256 and (coincidentally) the pre-patch live file's sha256 (`git show 2d9bca…:…/regenerate.py | sha256sum` = `f34fadb9…`); the copy is untouched, the live path is not pinned. **O3 needs no re-pin** (unlike O2/O4, which move the r15 frozen pin).
- Registered gate rows naming it — `SKILL.md:215` (`souji-preservation-evidence`, names `regenerate.py --rev <rev>`) and `SKILL.md:216` (`r15-preservation-evidence`); both line numbers hold at `2d9bca`, at `32f48f9` and at the landing commit `a7c35c2`. Run in the same clone at each revision:

| command | rev 2d9bca | rev 32f48f9 | rev a7c35c2 |
|---|---|---|---|
| `python3 -B tools/souji-preservation-evidence.py --selftest` (row 215) | rc0 `selftest: 47/47 passed` | rc0 `selftest: 47/47 passed` | — |
| `python3 -B tests/fixtures/r15-preservation-evidence.py` (row 216) | rc0 `fixture: 8/8 checks passed` | rc0 `fixture: 8/8 checks passed` | — |
| `python3 -B tools/souji-preservation-evidence.py --root . --frozen tests/fixtures/r15-preservation-frozen` (G4) | rc0 `frozen_files: 3` | rc0 `frozen_files: 3` | — |

### 7. Q74 — write-scope / refusal guard

`regenerate.py` has no write-scope guard and no refusal that depends on its scratch root: it writes only fixed paths in its own directory (`HERE/record.json`, `HERE/expected.json`), takes no `--out`/target, and its refusals are `2` (usage/binding/tool failure, before scratch creation) and `3` (non-clean verdict without `--allow-nonclean`). The patch's two lines sit outside both branches. Base refusal inputs at both revisions:

```
rev 2d9bca5 argv=[]             rc=2 regenerate.py: error: the following arguments are required: --rev
rev 2d9bca5 argv=[--rev a31642d] rc=2 regenerate: tools/souji-census.sh differs between a31642d14006 and the worktree
rev 32f48f9 argv=[]             rc=2 regenerate.py: error: the following arguments are required: --rev
rev 32f48f9 argv=[--rev a31642d] rc=2 regenerate: tools/souji-census.sh differs between a31642d14006 and the worktree
```

`TMPDIR` inside a git work tree is not refused at base either (no such refusal exists), so moving the scratch root neither adds nor drops a refusal. Exit 3 has no base input at base (the record's verdict is `clean`), so nothing about it can regress.

## Findings

1. **C2 leg O3 is unreachable at the C2 landing commit — blocker, outside my file.** `regenerate.py` unconditionally runs its namespace arm (`run_arm(NS_FIXTURE, …)`, `NS_FIXTURE = "tests/fixtures/r14-census-boundary.py"`), and that fixture creates scratch under the literal `/var/tmp` (`tests/fixtures/r14-census-boundary.py:691`, also `:368 "TMPDIR": "/var/tmp"`), so it exits 2 under the leg's sandbox. Reproduced at `a7c35c2` (all five repairs): `sbox=rc1:regenerate: tests/fixtures/r14-census-boundary.py on <HEX> could not evaluate (rc=2)`; isolated under the same bwrap: `rc=2 r14-census-boundary: cannot create /var/tmp fixture: [Errno 30] Read-only file system: '/var/tmp/r14-census-boundary.q0jqfc4_'`, plain `rc=0 SUMMARY total=12 failed=0`. A Q71-shaped change to that fixture alone still fails — `sbox=rc3:finding pinned-mismatch: namespace_fixture.sha256=… is not the pinned r14 digest`, because `tools/souji-preservation-evidence.py:307 NAMESPACE_SHA256` and `expected.json files["tests/fixtures/r14-census-boundary.py"]` both pin its bytes. Reaching PASS needs r14's scratch root + that literal + the r15 re-pin: wider than the prereg's five files. Decision belongs to the L1.
2. **O3 also depends on O2, by construction.** `regenerate.py` runs `tests/fixtures/r15-census-config.py` once per arm; on an O3-only tree that fixture still creates `dir="/var/tmp"` and the leg reads `could not evaluate (rc=2)` from the child (evidence §3) even though the O3 repair has already succeeded. The landing commit carries O2, so this coupling does not bite there; an `--only O3` reading on an O3-only tree must not be read as a defect of this patch.
3. **The leg's PASS margin is tight under the sandbox and load-sensitive.** `regenerate.py` caps every arm at `timeout 300`; the sandboxed child fixture at the landing commit measures **254 s** for one run (`bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm … python3 -B tests/fixtures/r15-census-config.py --tool tools/souji-census.sh` → rc0 `SUMMARY total=20 failed=0`, at load average 31-51). Two attempts at load ~60 produced `could not evaluate (rc=124)` (the arm cap), and one earlier invocation produced the *base* line itself as `could not evaluate (rc=124)` (`base=rc1`). Contention cannot turn a FAIL into a PASS, but it can hide an honest PASS; final readings should be taken on a quiet host (the fleet sat at load 57-92 on 32 cores throughout this seat).
4. **No consumer or pin moves with my file** (evidence §6), so O3 contributes no Q73 re-pin step; the r15 frozen pin covers `r15-census-config.py`, `r14-census-boundary.py` and `tools/souji-census.sh`, i.e. O2's, O4's and r14's bytes, not mine.
5. **Observed, not mine to fix:** the lane worktree outside my clones has moved past the preregistration (tip `a7c35c2` plus uncommitted `SKILL.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/lessons/round-33.md`, `census/round-33/sources/`), and registry row numbers are revision-bound (215/216 at `2d9bca`, `32f48f9` and `a7c35c2`; one line lower in the live worktree). Every receipt here cites the revision it was taken at. Also observed and left alone: `/var/tmp` holds live `r15-census-config.*` scratch trees from other seats (mtimes 14:03-15:34, several written while this seat ran) plus `souji-r16-repin.k2v8iy3h`; attribution is not decidable from outside, and deleting them could break a running sibling, so they were not touched. My own scratch tree `/fast/scratch/hyaku/souji-r33/FixO3` was removed (mode-000 fixture dirs needed a `chmod -R u+rwX` first); the seat left no scratch behind.

## Attack log

**ATTACK (reproduced state, no rule change proposed): C2's O3 leg cannot reach its frozen predicate at the C2 landing commit.** State: `census/round-33/c2-counter.py --only O3` at `a7c35c24bdd8bae5cff9766ace02a81915756701` prints `LEG O3 sandbox-nt FAIL … sbox=rc1:regenerate: tests/fixtures/r14-census-boundary.py on <HEX> could not evaluate (rc=2)` — the failure is in a file the preregistration does not list among the five repaired tools/fixtures, reached unconditionally from the repaired script. Adding that file's Q71 repair to a scratch tree still reads `sbox=rc3:finding pinned-mismatch: namespace_fixture.sha256=…`, because the checker's literal `NAMESPACE_SHA256` (line 307) and `expected.json` pin the same bytes. So under the frozen legs the O3 leg is unreachable by any repair confined to the declared surface; the round's own Q70 reachability leg was never executed for O3 after repairs (feasibility.txt ran only O2 and O4). Receipts: §2-§4 above and `deliver-c2-O3.md`.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-c2-O3.patch` — the diff at `2d9bca → 32f48f9`, one file, two lines; applies cleanly at base.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-c2-O3.md` — full receipts (command, output, revision) for the change, red-before, after, Q73 and Q74, plus the risks restated here.
- this report.
