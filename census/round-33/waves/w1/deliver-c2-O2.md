# C2 leg O2 — tests/fixtures/r15-census-config.py scratch root from TMPDIR

Seat SwarmExecutor29, r33 w1. Parent 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; base 6017a482e7068d5afb7617640198fbb0fe743357.
Scratch clone /fast/scratch/hyaku/souji-r33/FixO2/c, repair commit 5bfcc3308b4506976c59b2483402cd9e73b26780 (one file).

Patch: `deliver-c2-O2.patch` (verbatim `git -C <clone> diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`), 1 file, 5 hunks,
7 insertions / 7 deletions. Applies clean to 2d9bca5 (`git apply --check` OK in a second clone; the post-apply blob
sha256 equals the candidate blob 62e310ca71f1e5fe3e37ad44b70fa9348f52fc8dc2d9b46c6c48cd0df2a81d27; base blob
790024c9e03d605b87571d3f7307770d4e0b6690ff508d1e24780fa462ecb82e). Note the diff carries the lane's
`diff.mnemonicprefix=true` prefixes (`c/`/`w/`); `git apply` (default -p1) handles them.

## What changed (Q71: scratch root only)

1. `run_tool` child env `"TMPDIR": "/var/tmp"` -> `tempfile.gettempdir()` (the caller's TMPDIR, never a literal root).
2. `main` `tempfile.mkdtemp(prefix="r15-census-config.", dir="/var/tmp")` -> `tempfile.mkdtemp(prefix="r15-census-config.")`.
3. The die message follows the root: `cannot create /var/tmp fixture: {exc}` -> `cannot create fixture scratch in {tempfile.gettempdir()}: {exc}`.
4. Docstring truth: `synthetic HOME under /var/tmp` -> `under its `$TMPDIR` scratch directory`; `Q4 parity: scratch is
   /var/tmp only` -> `Q4 parity: scratch is `$TMPDIR` only`. Every other `/var/tmp` mention in the file: none left
   (`grep -n 'var/tmp' tests/fixtures/r15-census-config.py` -> rc1, no match).
Removal scope unchanged: `cleanup()` rmtree's only the fresh mkdtemp child (`SCRATCH`), never TMPDIR itself.

```diff
diff --git c/tests/fixtures/r15-census-config.py w/tests/fixtures/r15-census-config.py
index cf74ace..ff27dda 100755
--- c/tests/fixtures/r15-census-config.py
+++ w/tests/fixtures/r15-census-config.py
@@ -71,9 +71,9 @@ Semantics pinned here (SoujiR15.ConfigRepair lock, reviewer reports):
     path-protected: <reason>` on stderr, no stdout rows (rows print only
     after every repo is measured).
 
-The fixture builds a synthetic HOME under /var/tmp whose agent store
-(<home>/.omp/agent) is mode 000 and contains a canary string. Every tool
-invocation runs under `strace -f` with PATH spies for
+The fixture builds a synthetic HOME under its `$TMPDIR` scratch directory
+whose agent store (<home>/.omp/agent) is mode 000 and contains a canary
+string. Every tool invocation runs under `strace -f` with PATH spies for
 find/du/git/cat/head/tail/readlink/stat/realpath logging cwd, argv and
 selected GIT_* environment values. Two independent access checks run on
 every invocation:
@@ -102,7 +102,7 @@ TOOL-KIND records which arm ran. CASE detail and the --json record carry
 observed_exit/observed_finding per case (last invocation) for the C2
 paired-preservation checker.
 
-Q4 parity: scratch is /var/tmp only and removed in a finally block.
+Q4 parity: scratch is `$TMPDIR` only and removed in a finally block.
 No /dev/shm, no real credential path, no live census.
 """
 
@@ -825,7 +825,7 @@ def run_tool(args: list[str], extra_env: dict[str, str] | None = None) -> Result
     env = {
         "PATH": f"{SPYDIR}:/usr/local/bin:/usr/bin:/bin",
         "HOME": str(HOME),
-        "TMPDIR": "/var/tmp",
+        "TMPDIR": tempfile.gettempdir(),
         "LC_ALL": "C",
         "GIT_CONFIG_GLOBAL": "/dev/null",
         "GIT_CONFIG_SYSTEM": "/dev/null",
@@ -1542,9 +1542,9 @@ def main(argv: list[str]) -> int:
         die(f"tool not readable: {TOOL}: {exc}")
 
     try:
-        SCRATCH = Path(tempfile.mkdtemp(prefix="r15-census-config.", dir="/var/tmp"))
+        SCRATCH = Path(tempfile.mkdtemp(prefix="r15-census-config."))
     except OSError as exc:
-        die(f"cannot create /var/tmp fixture: {exc}")
+        die(f"cannot create fixture scratch in {tempfile.gettempdir()}: {exc}")
     records: list[dict] = []
     try:
         try:
```

## C2 counter — candidate (this is the leg's own reading)

```
$ python3 -B census/round-33/c2-counter.py --root /fast/scratch/hyaku/souji-r33/FixO2/c \
    --rev 5bfcc3308b4506976c59b2483402cd9e73b26780 --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/FixO2/cnt-rc2 --only O2,G6
LEG	O2	sandbox-nt	PASS	base=rc0:SUMMARY total=20 failed=0	sbox=rc0:SUMMARY total=20 failed=0
LEG	G6	guard	PASS	base=rc0:SUMMARY total=29 failed=0	rev=rc0:SUMMARY total=29 failed=0
SUMMARY legs=2 pass=1 fail=0 harm=0 partial=1 rev=5bfcc3308b4506976c59b2483402cd9e73b26780
candidate rc=0
```
An earlier identical invocation (scratch `cnt`, output piped through `tee`, so its shell rc was tee's) printed the
same three lines verbatim. `--only O2,G6` cannot reach the frozen full-set target (`legs=11 pass=5 fail=0 harm=0`);
displayed pass/fail count only the O legs run.

## C2 counter — red-before (2d9bca5, the frozen list-rev bytes)

```
$ python3 -B census/round-33/c2-counter.py --root .../FixO2/c --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --base 6017a48... --list-rev 2d9bca5... --scratch .../FixO2/cnt-red --only O2,G6
LEG	O2	sandbox-nt	FAIL	base=rc0:SUMMARY total=20 failed=0	sbox=rc2:r15-census-config: cannot create /var/tmp fixture: [Errno 30] Read-only file system: '<TMP>'
LEG	G6	guard	PASS	base=rc0:SUMMARY total=29 failed=0	rev=rc0:SUMMARY total=29 failed=0
SUMMARY legs=2 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
```
(rc not captured separately: the command was piped through `tee`. The counter returns 0 iff fail=0 and harm=0 —
c2-counter.py:203 — and a fail=0/harm=0 partial run was observed returning rc=0, a harm=1 run rc=1.)

## Q73 — consumers and registered gate

Consumer set (`git -C <clone> grep -l tests/fixtures/r15-census-config.py -- tests/fixtures census`), identical at
2d9bca5 and at 5bfcc33 (135 paths, `diff` empty). Live consumers: `tests/fixtures/r15-preservation-evidence.py`,
`tests/fixtures/r15-preservation-frozen/{expected.json,record.json,regenerate.py}`; the rest are historical round
transcripts/records plus this round's frozen docs (`census/round-33/*`), which only mention the path.

SKILL `## Gate registry` rows naming the fixture: SKILL.md:211 (`r15-census-config | gate | `python3
tests/fixtures/r15-census-config.py --tool PATH``) and SKILL.md:213 (r17-census-matrix, which names "r15" only).
Row 211's command executed in scratch clones, plain, `TMPDIR` a scratch dir:

```
base 6017a482e706: rc=0, last line  SUMMARY	total=20	failed=0   (TOOL-KIND other)
rev  5bfcc3308b45: rc=0, last line  SUMMARY	total=20	failed=0   (TOOL-KIND other)
```

Frozen-pin guards (`--only G4,G5`, candidate):

```
LEG	G4	guard	FAIL	base=rc0:frozen_files: 3	rev=rc2:finding snapshot_tampered: 'tests/fixtures/r15-census-config.py': pinned=<HEX> observed=<HEX>
LEG	G5	guard	PASS	base=rc0:fixture: 8/8 checks passed	rev=rc0:fixture: 8/8 checks passed
SUMMARY legs=2 pass=0 fail=0 harm=1 partial=1 rev=5bfcc3308b4506976c59b2483402cd9e73b26780
rc=1
```
G4 red is the declared Q73 step: the r15 frozen pin must be regenerated by its own `regenerate.py` as its own commit
(L1's re-pin; the C2 landing commit is that re-pin). G5 green. `census/round-33/c2-legs.tsv` G4 is therefore red at
this repair commit by design, not hidden.

## Q74 — refusals (no write-scope guard existed over the scratch root)

The fixture's only guards are usage/unknown-case/root-user/tool-unreadable; none protected `/var/tmp`, and none takes
a write target, so Q74's added `TMPDIR`-inside-a-work-tree refusal has no antecedent. Every base refusal still fires
with the same code and message at the candidate (uid 1000):

| input | base 6017a48 | candidate 5bfcc33 |
|---|---|---|
| `--tool /nonexistent/tool.sh` | rc2 `r15-census-config: tool not readable: /nonexistent/tool.sh` | rc2 same |
| `--case R15CFG-99` | rc2 `r15-census-config: unknown case id: R15CFG-99` | rc2 same |
| `--bogus-flag` | rc2 `usage: r15-census-config.py ... error: unrecognized arguments: --bogus-flag` | rc2 same |

The `refusing to run as root` refusal is not exercisable at uid 1000 — untested, not claimed. Scratch removal cannot
reach a caller tree: `cleanup()` (`tests/fixtures/r15-census-config.py:1487-1494`) chmods the store and rmtree's
`SCRATCH`, the fresh mkdtemp child only.

## Q71 receipts

```
$ TMPDIR=/fast/scratch/hyaku/souji-r33/FixO2/run-tmp/probe/ python3 -B -c 'import tempfile; print("gettempdir:", tempfile.gettempdir()); print("mkdtemp:", tempfile.mkdtemp(prefix="probe."))'
gettempdir: /fast/scratch/hyaku/souji-r33/FixO2/run-tmp/probe
mkdtemp: /fast/scratch/hyaku/souji-r33/FixO2/run-tmp/probe/probe.kvk2o7bs
```
A trailing slash on TMPDIR is normalized, so the child env never carries a doubled slash.

Leftover sweep after all candidate runs (base-revision runs inside the counter still create `/var/tmp/...` transiently
and remove it: two such dirs seen live at 14:51/14:52 during the last run were gone afterwards):

```
$ ls -d /tmp/r15-census-config.* /var/tmp/r15-census-config.* 2>/dev/null
/var/tmp/r15-census-config.3tk6qehq   mtime 14:06:08  ~11.6 MB
/var/tmp/r15-census-config.psjsbayp   mtime 14:15:33  ~10.6 MB
/var/tmp/r15-census-config.xec8q0wl   mtime 14:03:28  ~10.0 MB
```
These three have frozen mtimes from before/around this seat's runs and belong to runs that died without their
`finally` (a counter timeout kill skips `cleanup()`). Ownership is indeterminate and they are outside this seat's
write scope, so they were left in place — flagged, not removed.

## Tooling

None installed or changed this wave (no pacman/uv/npx use; the host-wide pacman pause was respected).

## Notes for the L1

- SKILL.md:211's last cell still reads `isolated `/var/tmp`; no real store or live fleet probe`, which this repair
  makes false (the isolation root is now the caller's TMPDIR). Proposed doc-only edit, left out of the patch because
  the item scoped it to the fixture: `isolated `$TMPDIR`; no real store or live fleet probe`. No leg measures it.
- No C1 item runs this fixture (`census/round-33/c1-items.tsv` files column never names it), so the repair cannot move
  a C1 row; K07/K08 use `tools/souji-census.sh` and `tools/souji-verify.sh`, untouched here.
