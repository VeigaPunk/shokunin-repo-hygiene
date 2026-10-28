# R40w2critic06 — attack on the r40 C3 crash-probe repair

Role: critic (falsify). Landed revision attacked: `128e412b0ced3c243dc27c3dd3332054a611bc2e`.
Base revision named: `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
All committed bytes were read with `git -C <lane> show 128e412:PATH`. No commits, pushes, or
mutating git/jj commands were run. Installs: none (no pacman, no uv, no npm). Python: system
`/usr/bin/python3` 3.14.8.

## Verdict

**FALSIFIED** (on the crash probe's own contract, `census/round-40/c3-counter.py:99-102`, `:18-19`).

- The repair reads the crash marker from STDERR only (`c3-counter.py:115`). That is correct for
  the fixture as landed, but it does not establish "the fixture did not crash":
  - **V1** a fixture that catches an internal exception per case and prints the traceback to STDOUT
    is scored `killed=True` for a tool that writes no branch defect at all (stray byte on tool
    stdout). The landed counter manufactures a kill.
  - **V2** a fixture that exits 1 after its SUMMARY with a plain message (no traceback header) is
    scored `killed=True` for every mutant. The probe checks only the traceback header, not a crash.
  - **V3** a fixture that prints SUMMARY with fail>0 and then raises is scored `killed=False`,
    `crash=True`. A detected mutant is therefore masked as survived. This is fail-closed, but it is
    a masked kill and the battery SUMMARY does not count it separately.
  - **V4** a traceback on STDOUT alone, with a real kill, is still scored killed. The stdout marker
    is ignored, which is correct for a real kill, but the docstring's "no traceback" wording is not
    what the code checks.
- Independent defect in the committed bytes: the failing-case attribution the repair promises is
  dead. `c3-counter.py:116-117` filters on `l.endswith("FAIL")`, but a FAIL line carries a
  ` rc=... out=...` suffix, so `failing=` is always `-` at the landed revision (Attack A below).
  The uncommitted working-tree copy of the same file fixes this (`=FAIL` in the first token), so the
  lane's working tree and the landed bytes disagree (see Attack A).
- Independent contract defect: `--base-rev` is validated (`c3-counter.py:133`) but never used to
  read content. The base fixture is read from `args.rev` (`c3-counter.py:146`). "Every mutant must
  survive the r39 base fixture" is therefore measured at the candidate revision, not at the named
  base (Attack C).
- Independent harm: `score()` runs the mutant with no timeout (`c3-counter.py:103-107`). A
  non-terminating tool hangs the counter with no verdict (Attack D).

For the **landed fixture** itself (`tests/fixtures/r40-drift-record-branches.py`), the declared
mutant verdicts are correct: M15-M18 are each killed by a genuine failing case, base_killed=0, and a
stray-byte tool gives NO-SUMMARY (not killed). The falsifier needs a fixture shape the landed
fixture does not have (V1/V2/V3). The probe is the evidence for that.

## What was attacked (file:line, committed bytes at 128e412)

| Item | Location |
|---|---|
| Repair docstring (STDERR-only marker) | `census/round-40/c3-counter.py:22-27`, `:97-102` |
| Kill contract docstring ("no traceback and exit 1") | `census/round-40/c3-counter.py:17-19` |
| SUMMARY parse (last `SUMMARY cases=` line on stdout) | `c3-counter.py:108-114` |
| Crash marker (stderr only) | `c3-counter.py:115` |
| Failing-case attribution (dead at R) | `c3-counter.py:116-117` |
| Kill predicate `rc==1 and fails>0 and not crash` | `c3-counter.py:118` |
| Subprocess with no timeout | `c3-counter.py:103-107` |
| `--base-rev` validated only | `c3-counter.py:133` |
| Base fixture read from `args.rev` | `c3-counter.py:146` |
| Skip guard anchor in tool | `tools/souji-worktree-drift.py:370` |
| Fixture decode with `text=True` (tool output) | `tests/fixtures/r40-drift-record-branches.py:85` |
| Fixture SUMMARY print / exit | `tests/fixtures/r40-drift-record-branches.py:145`, `:150` |

## Probe

Reproducible driver (committed in the lane's w2 directory, reads all bytes via `git show`):
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w2/R40w2critic06-probe.py`

Command (scratch was `/fast/scratch/hyaku/souji-r40/w2/R40w2critic06`, passed explicitly):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w2/R40w2critic06-probe.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic06/probe
```

Real output (exit 0):

```
fixture                        tool                 killed detail (committed counter score())
landed                         pristine             False  rc=0 fails=0 crash=False failing=-
landed                         stray_stdout_byte    False  NO-SUMMARY rc=1
landed                         M15                  True   rc=1 fails=1 crash=False failing=-
landed                         M16                  True   rc=1 fails=4 crash=False failing=-
landed                         M17                  True   rc=1 fails=1 crash=False failing=-
landed                         M18                  True   rc=1 fails=1 crash=False failing=-
V1_stdout_tb_caught_as_fail    pristine             False  rc=0 fails=0 crash=False failing=-
V1_stdout_tb_caught_as_fail    stray_stdout_byte    True   rc=1 fails=8 crash=False failing=-
V1_stdout_tb_caught_as_fail    M15                  True   rc=1 fails=1 crash=False failing=-
V1_stdout_tb_caught_as_fail    M16                  True   rc=1 fails=4 crash=False failing=-
V1_stdout_tb_caught_as_fail    M17                  True   rc=1 fails=1 crash=False failing=-
V1_stdout_tb_caught_as_fail    M18                  True   rc=1 fails=1 crash=False failing=-
V2_nontb_abort_after_summary   pristine             False  rc=0 fails=0 crash=False failing=-
V2_nontb_abort_after_summary   stray_stdout_byte    False  NO-SUMMARY rc=1
V2_nontb_abort_after_summary   M15                  True   rc=1 fails=1 crash=False failing=-
V2_nontb_abort_after_summary   M16                  True   rc=1 fails=4 crash=False failing=-
V2_nontb_abort_after_summary   M17                  True   rc=1 fails=1 crash=False failing=-
V2_nontb_abort_after_summary   M18                  True   rc=1 fails=1 crash=False failing=-
V3_tb_after_summary            pristine             False  rc=0 fails=0 crash=False failing=-
V3_tb_after_summary            stray_stdout_byte    False  NO-SUMMARY rc=1
V3_tb_after_summary            M15                  False  rc=1 fails=1 crash=True failing=-
V3_tb_after_summary            M16                  False  rc=1 fails=4 crash=True failing=-
V3_tb_after_summary            M17                  False  rc=1 fails=1 crash=True failing=-
V3_tb_after_summary            M18                  False  rc=1 fails=1 crash=True failing=-
V4_tb_header_stdout_only       pristine             False  rc=0 fails=0 crash=False failing=-
V4_tb_header_stdout_only       stray_stdout_byte    False  NO-SUMMARY rc=1
V4_tb_header_stdout_only       M15                  True   rc=1 fails=1 crash=False failing=-
V4_tb_header_stdout_only       M16                  True   rc=1 fails=4 crash=False failing=-
V4_tb_header_stdout_only       M17                  True   rc=1 fails=1 crash=False failing=-
V4_tb_header_stdout_only       M18                  True   rc=1 fails=1 crash=False failing=-
```

Variant definitions (single edits to the committed fixture; the probe asserts each anchor occurs once):
- V1: `run_record` wrapped; any exception is `traceback.print_exc(file=sys.stdout)` and counted as FAIL.
- V2: after the SUMMARY print, `if failed: sys.exit("fixture aborted after summary")`.
- V3: after the SUMMARY print, `if failed: raise RuntimeError(...)`.
- V4: after the SUMMARY print, `print("Traceback (most recent call last):", file=sys.stdout)`.
- stray_stdout_byte tool: `import sys as _g; _g.stdout.buffer.write(b"\xff\n")` prepended to the pristine tool. It is not a declared mutant; it exercises the decode path.

## Attack A — failing-case attribution at 128e412 (FALSIFIED, dead predicate)

Command:
```
python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2critic06/c3-counter-landed.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic06
```
(the file is `git show 128e412:census/round-40/c3-counter.py`; the same bytes are in the probe as `c3-counter-committed.py`)

Real output (exit 0):
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
```

Same counter with the lane's uncommitted working-tree bytes (`git diff` shows only
`c3-counter.py:116-117` changed; `git -C <lane> diff 128e412 -- census/round-40/c3-counter.py`):
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
```
The committed bytes therefore print `failing=-` for every mutant. The attribution the repair
promises ("prints the failing case names so a kill is attributable") does not function at the landed
revision. Note that HEAD of the lane is now `549d9ec` and `128e412` is its ancestor; the working-tree
edit is uncommitted and is not what the landed revision contains.

## Attack B — the crash probe on V1/V2/V3/V4 (FALSIFIED, see probe table)

Reasoning per variant:
- V1 (stdout traceback, per-case catch): `score()` tests only stderr for the marker (`c3-counter.py:115`),
  so a stdout traceback is invisible. `fails=8` comes from the caught exception, so `killed=True`
  for a non-branch tool defect. A fixture-internal crash is credited as detection. Counter contract
  violated (`c3-counter.py:18-19` requires "no traceback").
- V2 (no-traceback abort after SUMMARY): `killed=True`. The only crash discriminator is the traceback
  header. Any non-traceback nonzero exit after a failing SUMMARY is a kill.
- V3 (traceback after SUMMARY): `killed=False crash=True`. The detected mutant is reported as survived.
  Fail-closed, and it masks a detection; the battery SUMMARY (`c3-counter.py:202-204`) does not count
  fixture crashes separately from survivors.
- V4 (stdout traceback header, real kill): `killed=True`. Correct for a real kill, but it shows the
  docstring's "no traceback" is not the enforced predicate.

Landed fixture (no V1-V4 shape): the stray-byte tool gives `NO-SUMMARY`, so the landed counter does
not manufacture a kill from tool output. The declared mutants M15-M18 are killed by genuine failing
cases on the landed fixture.

## Attack C — `--base-rev` is never read (FALSIFIED, contract)

Command:
```
python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2critic06/c3-counter-landed.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --base-rev ccbb1326204bbf21034820430e9923cb96ef4c17 --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic06
```
Real output (exit 0): `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e`
(`ccbb1326` is the repository root commit, which predates the r39 fixture; the run succeeded anyway).
A bogus unresolvable revision is refused (`REFUSAL COULD-NOT-EVALUATE: --base-rev 000...001 does not resolve`, exit 2),
so `--base-rev` is checked for resolution and then discarded. The base fixture is read from `--rev`
(`c3-counter.py:146`).

## Attack D — no timeout on the mutant run (FALSIFIED, harm: no verdict)

Command:
```
timeout 25 python3 -B -c "import importlib.util; spec=importlib.util.spec_from_file_location('c3','<scratch>/c3-counter-landed.py'); c3=importlib.util.module_from_spec(spec); spec.loader.exec_module(c3); print(c3.score('<scratch>/fx-landed.py','<scratch>/hang/hang_tool.py','<scratch>/hang'))"
```
where `hang_tool.py` is `import time\ntime.sleep(100000)`. Output: `scoring hanging tool ...` then exit 124 (the
timeout killed it at 25 s; `score()` never returned). The counter has no per-mutant timeout
(`c3-counter.py:103-107`); the fixture's `--timeout 30` bounds only git calls inside the tool.

## Attack E — precondition checks (SAFE)

- The landed fixture and tool match the committed revision (both read via `git show`; the working
  tree differs only in `census/round-40/c2-counter.py` and `c3-counter.py:116-117`).
- Pristine passes (`rc=0 fails=0`), declared mutant anchors each occur exactly once (`count==1`
  path is exercised by the full run), and M15-M18 kill on their designated cases.
- A stdout traceback alongside a real kill (V4) does not mask the kill: killed=True.

## Re-run and cleanup

- Re-run: the three commands above (Attack A, B via the probe, C) and Attack D with `timeout 25`.
- Scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2critic06` was removed (`rm -rf` run; `ls` reports
  "No such file or directory").
- No edits to counters, fixtures, preregistration, SCORECARD.md, LOG.md, corpus/, or committed files.
  The probe and this report are the only files written, both under the lane's `.ufo/waves/round-40/w2/`.
