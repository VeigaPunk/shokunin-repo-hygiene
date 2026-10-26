# r33 C2 leg O3 — `tests/fixtures/r15-preservation-frozen/regenerate.py` scratch root from `TMPDIR`

Seat `SwarmExecutor30`, wave w1 (v1 policy). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `6017a482e7068d5afb7617640198fbb0fe743357`, prereg/list-rev `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`.
All runs by this seat on 2026-10-26, host load average 57-92 (32 cores, fleet storming) — see Risks.

## Change (one file, two lines)

Patch: `deliver-c2-O3.patch` (sha256 `608407672ccca44361f505f96cce90900949513c521ecb4a6867104f3f49da96`).

```
$ git -C /fast/scratch/hyaku/souji-r33/FixO3/c diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2
diff --git a/tests/fixtures/r15-preservation-frozen/regenerate.py b/tests/fixtures/r15-preservation-frozen/regenerate.py
index f990de9..68906f2 100755
--- a/tests/fixtures/r15-preservation-frozen/regenerate.py
+++ b/tests/fixtures/r15-preservation-frozen/regenerate.py
@@ -12,7 +12,7 @@ runs printed:
   namespace_controls <REV>  tools/souji-census.sh under tests/fixtures/r14-census-boundary.py
 
 Each tool is extracted with `git show <rev>:tools/souji-census.sh` into a
-private /var/tmp directory (removed afterwards). The fixtures run from the
+private TMPDIR directory (removed afterwards). The fixtures run from the
 lane checkout and must equal their bytes at <REV>; the installed tool must too.
@@ -135,7 +135,7 @@ def main() -> int:
             print(f"regenerate: {rel} differs between {rev[:12]} and the worktree",
                   file=sys.stderr)
             return 2
-    scratch = Path(tempfile.mkdtemp(prefix="souji-r16-repin.", dir="/var/tmp"))
+    scratch = Path(tempfile.mkdtemp(prefix="souji-r16-repin."))
     try:
```
Files touched: `tests/fixtures/r15-preservation-frozen/regenerate.py` only (`git diff --name-only` between the two commits prints exactly that one path). No other file was edited for any reason.

Q71 shape: `tempfile.mkdtemp` with no `dir=` takes `TMPDIR` (`tempfile.gettempdir()`); the docstring moves with the code. Child processes: the file passes no `env=` to any `subprocess.run`, so every child (the two fixtures, `git`, the checker) inherits the caller's `TMPDIR` already — nothing to change (`grep -n "env=" regenerate.py` → no match). After the patch `grep -n "var/tmp\|/tmp\|mkdtemp" <file>` → the only hits are `tempfile` import/use and no literal root.

```
$ git -C <clone> apply --check deliver-c2-O3.patch   # on a pristine 2d9bca work tree
APPLIES CLEANLY AT BASE
$ git -C <worktree> diff --stat
 tests/fixtures/r15-preservation-frozen/regenerate.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

## Red-before — frozen counter at 2d9bca (unrepaired)

```
$ export TMPDIR=/fast/scratch/hyaku/souji-r33/FixO3/tmp
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c2-counter.py \
    --root /fast/scratch/hyaku/souji-r33/FixO3/c --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/FixO3/cnt --only O3
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean	sbox=rc1:OSError: [Errno 30] Read-only file system: '<TMP>'
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
(exit 1)
```

The red-before failure is the base defect: the sandboxed run dies in the script's own `mkdtemp(dir="/var/tmp")` (`OSError`, `read-only file system`) before any fixture runs.

## After — frozen counter at the O3 repair commit, measured alone

Scratch commit `32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2` (parent 2d9bca, throwaway identity, `--no-local` clone with `origin` removed).

```
$ python3 -B .../c2-counter.py \
    --root /fast/scratch/hyaku/souji-r33/FixO3/c --rev 32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2 \
    --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/FixO3/cnt --only O3
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean	sbox=rc1:regenerate: tests/fixtures/r15-census-config.py on <HEX> could not evaluate (rc=2)
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2
(exit 1)
```

Read this line carefully: the O3 repair itself worked — the run got past `mkdtemp` and into the arms — and the sandboxed run then died in its **child**: `regenerate.py` runs `tests/fixtures/r15-census-config.py` for every arm (`run_arm`), and that fixture at base is itself still on `mkdtemp(..., dir="/var/tmp")` (that is O2's file, not mine). Under the sandbox it exits 2 at its own scratch creation, so `regenerate.py` raises `could not evaluate (rc=2)` and returns 1. Isolated `--only O3` therefore cannot PASS on an O3-only tree; the landing commit carries O2, and the next section measures it there — where the leg meets a **second, wider** blocker (`tests/fixtures/r14-census-boundary.py`) that the five declared repairs do not cover.

## Landing measurement — the C2 landing commit `a7c35c2` (all five repairs; the L1's, not mine)

The L1 landed the O3 bytes itself in `a7c35c24bdd8bae5cff9766ace02a81915756701` (verified identical above), so the frozen leg was measured against that commit (clone `/fast/scratch/hyaku/souji-r33/FixO3/land` at `a7c35c2`, `origin` removed):

```
$ python3 -B .../c2-counter.py --root /fast/scratch/hyaku/souji-r33/FixO3/land \
    --rev a7c35c24bdd8bae5cff9766ace02a81915756701 --base 6017a482e7068d5afb7617640198fbb0fe743357 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/FixO3/cnt --only O3
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean	sbox=rc1:regenerate: tests/fixtures/r14-census-boundary.py on <HEX> could not evaluate (rc=2)
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=a7c35c24bdd8bae5cff9766ace02a81915756701
(exit 1)
```

With all five repairs present, `regenerate.py` gets past its own scratch root **and** past the three tool arms, then dies in its **namespace arm**, which runs `tests/fixtures/r14-census-boundary.py` — a file outside the five repaired files and itself still on a literal `/var/tmp`:

```
$ sed -n '691p;368p' tests/fixtures/r14-census-boundary.py     # at a7c35c2
        SCRATCH = Path(tempfile.mkdtemp(prefix="r14-census-boundary.", dir="/var/tmp"))
        "TMPDIR": "/var/tmp",
```

Isolated under the counter's exact sandbox (`--dev-bind / / --ro-bind <empty 555> /tmp --ro-bind <empty 555> /var/tmp --ro-bind <empty 555> /dev/shm`, `TMPDIR` a scratch dir), at `a7c35c2`:

```
$ cd /fast/scratch/hyaku/souji-r33/FixO3/land
$ env TMPDIR=…/tmp3 bwrap --dev-bind / / --ro-bind …/empty /tmp --ro-bind …/empty /var/tmp \
    --ro-bind …/empty /dev/shm --chdir . python3 -B tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
ns sandbox rc=2 elapsed=0s
r14-census-boundary: cannot create /var/tmp fixture: [Errno 30] Read-only file system: '/var/tmp/r14-census-boundary.q0jqfc4_'
$ (same command, plain, no bwrap)
rc=0
SUMMARY	total=12	failed=0
```

So the O3 leg is **not reachable at the C2 landing commit** as the legs are frozen: `regenerate.py` always executes the namespace arm, and that arm's fixture cannot create its scratch under the leg's sandbox. This holds for any tree that has the five declared repairs.

Reachability probe (scratch clone `/fast/scratch/hyaku/souji-r33/FixO3/ns`, **measurement only, NOT delivered, NOT a repair of mine**): the landing tree plus a Q71-shaped scratch-root change to `r14-census-boundary.py` alone (5 lines: two docstring phrases, `"TMPDIR": tempfile.gettempdir()`, `mkdtemp` without `dir=`, the `die` text), commit `423bcd52b960762752afb37bd19caa235996a49c`:

```
LEG	O3	sandbox-nt	FAIL	base=rc0:regenerated at <HEX>: … verdict=clean	sbox=rc3:finding pinned-mismatch: namespace_fixture.sha256=<HEX> is not the pinned r14 digest <HEX>
SUMMARY legs=1 pass=0 fail=1 harm=0 partial=1 rev=423bcd52b960762752afb37bd19caa235996a49c
```

The namespace arm now completes, and `regenerate.py`'s own evaluation (the checker, `--record` mode) rejects the new record because the checker holds a **literal** digest of that fixture: `tools/souji-preservation-evidence.py:307 NAMESPACE_SHA256 = "e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2"`, which is also `expected.json`'s `files["tests/fixtures/r14-census-boundary.py"]` (`sha256sum` of the live file at `a7c35c2` = `e6a984b1…`). The checker's own selftest refuses a changed fixture:

```
$ cd /fast/scratch/hyaku/souji-r33/FixO3/ns && python3 -B tools/souji-preservation-evidence.py --selftest
selftest-unavailable: /fast/scratch/hyaku/souji-r33/FixO3/ns/tests/fixtures/r14-census-boundary.py missing or differs from the pinned r14 digest
```

Conclusion for the L1 (not a proposal, a reproduced state): making O3's frozen leg PASS requires the r14 fixture's scratch root **and** the checker's `NAMESPACE_SHA256` literal **and** the r15 frozen re-pin — a surface wider than the preregistration's five files, and wider than my item. My file's repair is complete and is not the blocker.

## Prerequisite stack (earlier measurement attempt; superseded by the landing reading above)

`/fast/scratch/hyaku/souji-r33/FixO3/stack`, made from the O3 commit plus the O2 repair exactly as the L1 recorded it in `census/round-33/records/feasibility.txt` ("### repair diff", the `r15-census-config.py` hunks), commit `58058d7779672a0c2f13bf45f616dae0ccf2857f`:

- the O3 part of the stack is byte-identical to the delivered patch (`cmp` of `git diff 2d9bca 58058d7 -- tests/fixtures/r15-preservation-frozen/regenerate.py` against `deliver-c2-O3.patch` → equal; both sha256 `608407672c…`);
- two attempts at the leg on it read `sbox=rc1:regenerate: tests/fixtures/r15-census-config.py on <HEX> could not evaluate (rc=124)` — the child fixture exceeded `regenerate.py`'s per-arm `timeout 300` under load average ~60 (a load artefact, not a scratch failure; superseded by the landing-commit reading, which reached the namespace arm at load 18).

## Q73 — consumers, pins, registered gates

Consumer sweep (`git grep -l`, run at both revisions; rc 0 both times, same 17 paths both times):

```
$ git -C <clone> grep -l tests/fixtures/r15-preservation-frozen/regenerate.py <REV> -- tests/fixtures census
<REV>:census/round-16/transcripts/w1/PreservationRepin.txt
<REV>:census/round-16/transcripts/w2/ConnSkillRegistry2.txt
<REV>:census/round-16/transcripts/w2/CriticFixtureRound2.txt
<REV>:census/round-16/transcripts/w2/DraftMistakesFinal.txt
<REV>:census/round-16/transcripts/w2/RerunCheckerFixture.txt
<REV>:census/round-16/transcripts/w2/RerunCheckerSelftest.txt
<REV>:census/round-16/transcripts/w2/RerunFrozen.txt
<REV>:census/round-16/transcripts/w2/RevCheckerDiff.txt
<REV>:census/round-16/transcripts/w2/RevGateFrozenRules.txt
<REV>:census/round-16/transcripts/w2/RevRegenerate.txt
<REV>:census/round-18/final-verification-4800fd7.json
<REV>:census/round-26/waves/assimilation/validate/corpus/lessons/round-16.md
<REV>:census/round-26/waves/assimilation/validate/tests/fixtures/r15-preservation-frozen/regenerate.py
<REV>:census/round-26/waves/manifest.sha256
<REV>:census/round-32/records/a2-repairs.txt
<REV>:census/round-33/c2-legs.tsv
<REV>:census/round-33/preregistration.txt
<REV>:tests/fixtures/r15-preservation-frozen/regenerate.py
```

(REV = `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` and `32f48f958c7c0b5406c1fab50524bf5e7d9d3ba2`; the only difference between the two outputs is the revision prefix. A looser `git grep -l "regenerate\.py"` returns the same set plus `census/round-16/.../CriticR4Laundering.txt`, `CriticSeparability2.txt`, `census/round-26/.../round-16-verifier-spotcheck.md`, `round-17.md`, `census/round-33/records/feasibility.txt`.)

Every hit is historical transcript, historical record, the assimilation snapshot, this round's own frozen item text, or the file itself. **No executable consumer reads, runs or pins this file:**
- `grep -rn "regenerate.py" --include=*.py --include=*.sh tools tests` (excluding the file itself) → no match.
- `grep -c regenerate tests/fixtures/r15-preservation-frozen/expected.json …/record.json` → `0` / `0`.
- The r15 frozen pin names three files and not this one: `python3 -B -c "…json.load(expected.json)['files']"` → `['tests/fixtures/r14-census-boundary.py', 'tests/fixtures/r15-census-config.py', 'tools/souji-census.sh']`.
- `census/round-26/waves/manifest.sha256:119` pins `./assimilation/validate/tests/fixtures/r15-preservation-frozen/regenerate.py` with `f34fadb988c186cfe88b1b5226a31369339b5002c3d0f8ca6231732d9df6943b`, which is that copy's own sha256 (`sha256sum` of the copy = `f34fadb9…`). That digest is also the **pre-patch** sha256 of the live file (`git show 2d9bca…:tests/fixtures/r15-preservation-frozen/regenerate.py | sha256sum` = `f34fadb9…`); after the patch the live file is `e2428676d1e8a0bbd885e624482cd3af6e0a80f3ceee87285ee67f5edaaf4d78`. The manifest row names the assimilation copy, which is untouched, so the row still verifies against its own committed bytes at every revision; it is not a pin of the live path.
- `census/round-18/final-verification-4800fd7.json` mentions the path inside a recorded command transcript only.

Q73 consequence: **no re-pin is required for O3** (unlike O2/O4, whose byte changes move the frozen pin).

Registered gate rows naming the fixture (SKILL.md:215, SKILL.md:216), run at both revisions in the same clone (`git checkout -qf --detach <REV>`):

| command (SKILL.md row) | rev 2d9bca5 | rev 32f48f9 |
|---|---|---|
| `python3 -B tools/souji-preservation-evidence.py --selftest` (row 215) | rc=0 `selftest: 47/47 passed` | rc=0 `selftest: 47/47 passed` |
| `python3 -B tests/fixtures/r15-preservation-evidence.py` (row 216) | rc=0 `fixture: 8/8 checks passed` | rc=0 `fixture: 8/8 checks passed` |
| `python3 -B tools/souji-preservation-evidence.py --root . --frozen tests/fixtures/r15-preservation-frozen` (counter guard G4) | rc=0 `frozen_files: 3` | rc=0 `frozen_files: 3` |

## Q74 — write-scope / refusal guard

`regenerate.py` has no write-scope guard and no refusal that depends on its scratch root:
- its writes are fixed paths inside its own directory (`HERE/record.json`, `HERE/expected.json`); it takes no `--out`/target argument, so there is no caller-controlled write target and no root-vs-target refusal to keep.
- its only refusals are `return 2` (usage/binding/tool failure, before any scratch creation) and `return 3` (non-clean verdict without `--allow-nonclean`); neither tests the scratch root, and the patch's two changed lines are the docstring and the `mkdtemp` call — outside both branches.

Base refusal inputs run at both revisions (rc and last line identical, both fire before scratch creation):

```
rev 2d9bca5: argv=[] rc=2 last=[regenerate.py: error: the following arguments are required: --rev]
rev 2d9bca5: argv=[--rev a31642d] rc=2 last=[regenerate: tools/souji-census.sh differs between a31642d14006 and the worktree]
rev 32f48f9: argv=[] rc=2 last=[regenerate.py: error: the following arguments are required: --rev]
rev 32f48f9: argv=[--rev a31642d] rc=2 last=[regenerate: tools/souji-census.sh differs between a31642d14006 and the worktree]
```

Exit 3 has no base input at base (the record's verdict is `clean`, so the refusal never fires at 2d9bca), so nothing about it can regress; the sandboxed runs above exercise the non-refusal path end to end. `TMPDIR` pointing inside a git work tree is not refused at base either — the script has no such refusal — so moving the scratch root neither adds nor drops one.

## Risks

1. **The O3 leg is unreachable at the landing commit, for a cause outside the repair set.** At `a7c35c2` the sandboxed run dies in `regenerate.py`'s namespace arm: `tests/fixtures/r14-census-boundary.py` (not one of the five repaired files) still creates scratch under the literal `/var/tmp` and exits 2 under the leg's sandbox (isolated: rc=2 `cannot create /var/tmp fixture: [Errno 30] Read-only file system`; plain: rc=0 `SUMMARY total=12 failed=0`). A Q71-shaped change to that fixture alone is not enough either: the checker holds `NAMESPACE_SHA256` (`tools/souji-preservation-evidence.py:307`) and `expected.json` pins the same digest, so that tree reads `sbox=rc3:finding pinned-mismatch: namespace_fixture.sha256=…`. O3's PASS therefore needs the r14 scratch root, the checker literal and the r15 re-pin — wider than the prereg's five files. The L1 owns that decision; my file's repair is not the blocker.
2. **O3 also depends on O2.** `regenerate.py` runs `tests/fixtures/r15-census-config.py` as its child for every arm; an `--only O3` reading on a tree without O2's repair fails in that child (rc=2). The C2 landing commit carries O2, so this coupling does not bite at the landing commit.
3. **Host load turns readings into timeouts.** `regenerate.py` caps each arm at `timeout 300`; under load average 57-92 the sandboxed child fixture exceeds it and the leg prints `could not evaluate (rc=124)` (two landing/stack attempts). One earlier invocation also produced a base line of `could not evaluate (rc=124)` (`base=rc1`) instead of the normal rc0 line — a FAIL produced by contention, not by the code. This cannot make a FAIL pass, but it can hide an honest PASS; final readings should be taken on a quiet host.
4. The patch is two lines in one file and changes no output on an unconstrained host: the base plain run at 2d9bca (unpatched tree) still prints `regenerated at <HEX>: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean`, and the same plain line is the reference the sandboxed run must equal.
