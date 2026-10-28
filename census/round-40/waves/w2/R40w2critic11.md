# R40w2critic11 — attack on M40-1 ("the r39 C3 scoring contract scored a detected mutant as SURVIVED; r40 does not")

Seat: R40w2critic11 (critic, wave 2, falsify). Judged on: calibration.
Target bytes: landed instrument commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`
(lesson `corpus/lessons/round-40.md` at that commit). The lane HEAD has since moved
(`556c24a`, `6ded124`, `8a5fbdb`); the lesson's measurement receipt (`census/round-40/records/c3-after.txt`)
says it was measured at `8a5fbdb`. Both revisions are checked below.
Base revision: `0242085909fb6a4ee041c5443d76316ac6d59d4b`.

## Verdict: FALSIFIED

M40-1's diagnosis (the r39 kill test reads the fixture's combined streams, so an echoed tool traceback
masks a detection) is REPRODUCED for one mutant class. Its evidence claim is FALSIFIED:

1. The lesson says the r40 battery's four mutants (M15-M18) are `killed=no` under the r39 contract and
   `killed=yes` under the r40 contract, and that `census/round-40/records/c3-after.txt` reproduces this.
   FALSE. Under the r39 contract M15-M18 are `killed=yes` (table below). `c3-after.txt` contains only r40
   contract output, never the r39 contract.
2. The only mutant that flips between the two contracts is a tool-crash mutant (`TOTOL`, the seat's
   `totol` defect). Its r40-contract kill comes from the tool traceback on **every** case (`fails=8` on the
   r40 fixture), not from a branch case. At the landed commit the counter's failing-case list is empty
   for every kill (`failing=-`), so the lesson's "prints the failing case names so a kill is attributable"
   is FALSE at `128e412`. It was fixed later at `8a5fbdb`, which is not the commit the lesson cites.
3. The lesson says the criterion was right and only the stream read was wrong. The standing rule
   (`census/round-38/preregistration.txt:189-194`) says "no `Traceback` on either stream". The landed r40
   counter changed that predicate to stderr only (`census/round-40/c3-counter.py:115`). That is a contract
   change, not a repair of the implementation.
4. A detected mutant that makes the fixture abort without its own SUMMARY is still scored SURVIVED by
   both contracts (probe B below). So "the r40 contract does not score a detected mutant as SURVIVED" is
   false as a general statement.

What is SAFE: the r40 contract is not vacuous. Its survived path is reachable (M13r39 under the r40
fixture: `killed=no`), so the instrument can fail in principle. The mined mistake's pointers are also wrong
(item 6 below).

## Attack surface (file:line at 128e412)

| # | Attacked claim / code | Location |
|---|---|---|
| A1 | lesson: r39 contract "scores a detected mutant as SURVIVED" | `census/round-39/c3-counter.py:101-102` (`crash = ... in (proc.stdout + proc.stderr)`) |
| A2 | r39 fixture echoes tool output into its own stdout | `tests/fixtures/r39-drift-record-rules.py:76`, `:79-80`, `:103-104`, `:133` (print to stdout) |
| A3 | lesson: r40 contract reads the fixture's stderr only; "prints the failing case names" | `census/round-40/c3-counter.py:115` (crash), `:116-117` (failing list), `:118` (killed), `:22-27` (docstring) |
| A4 | r40 fixture echoes tool output the same way | `tests/fixtures/r40-drift-record-branches.py:87`, `:90-91`, `:142` |
| A5 | lesson "shown able to fail" evidence and pointer | `corpus/lessons/round-40.md` (128e412) `:55` (pointer), `:67` ("criterion was right"), `:71-73` ("Shown able to fail", K1/K2) |
| A6 | standing kill rule the lesson says is unchanged | `census/round-38/preregistration.txt:189` (A5 heading), `:194` ("no `Traceback` on either stream") |
| A7 | receipt cited as K1/K2 evidence | `census/round-40/records/c3-after.txt` (measured at `8a5fbdb`; lines 4-7 are r40-contract output only) |
| A8 | cited wave-1 finding path | lesson cites `census/round-40/waves/w1/R40reviewer18.md` (does not exist); the file is `.ufo/waves/round-40/w1/R40reviewer18.md` (F1 at `:28`, the `totol` mutant at `:46`) |

## Commands and real output

Setup (no lane write; every file under the seat scratch, which is deleted at the end):
`S=/fast/scratch/hyaku/souji-r40/w2/R40w2critic11`, `L=/home/vgpnk/Projects/shokunin/souji-shokunin`,
`C=128e412b0ced3c243dc27c3dd3332054a611bc2e`. Byte check: `git -C $L show $C:<path>` was extracted with
`git show` and hashed. `census/round-40/c3-counter.py` at `$C` sha256 `7bdde9f6b205...`; the worktree
copy differs only in the failing-list predicate (lines 116-117, the later `8a5fbdb` fix).

### R1 — dual-contract reproduction of M40-1 (the re-runnable check; script in the appendix)

Command:
`python3 -B $S/repro.py $L $C $S/repro-run/landed`
(the script loads the r39 and r40 counters from `git show $C:...`, builds each mutant from
`git show $C:tools/souji-worktree-drift.py`, and calls each counter's own `score()`.)

Output (real, `repro-landed.out`):
```
TOTOL  fixture=r40  r39-contract killed=no  [rc=1 fails=8 crash=True]  r40-contract killed=yes [rc=1 fails=8 crash=False failing=-]
TOTOL  fixture=r39  r39-contract killed=no  [rc=1 fails=4 crash=True]  r40-contract killed=yes [rc=1 fails=4 crash=False failing=-]
M13    fixture=r40  r39-contract killed=no  [rc=0 fails=0 crash=False]  r40-contract killed=no  [rc=0 fails=0 crash=False failing=-]
M13    fixture=r39  r39-contract killed=yes [rc=1 fails=1 crash=False]  r40-contract killed=yes [rc=1 fails=1 crash=False failing=-]
M15    fixture=r40  r39-contract killed=yes [rc=1 fails=1 crash=False]  r40-contract killed=yes [rc=1 fails=1 crash=False failing=-]
M15    fixture=r39  r39-contract killed=no  [rc=0 fails=0 crash=False]  r40-contract killed=no  [rc=0 fails=0 crash=False failing=-]
M16    fixture=r40  r39-contract killed=yes [rc=1 fails=4 crash=False]  r40-contract killed=yes [rc=1 fails=4 crash=False failing=-]
M16    fixture=r39  r39-contract killed=no  [rc=0 fails=0 crash=False]  r40-contract killed=no  [rc=0 fails=0 crash=False failing=-]
M17    fixture=r40  r39-contract killed=yes [rc=1 fails=1 crash=False]  r40-contract killed=yes [rc=1 fails=1 crash=False failing=-]
M17    fixture=r39  r39-contract killed=no  [rc=0 fails=0 crash=False]  r40-contract killed=no  [rc=0 fails=0 crash=False failing=-]
M18    fixture=r40  r39-contract killed=yes [rc=1 fails=1 crash=False]  r40-contract killed=yes [rc=1 fails=1 crash=False failing=-]
M18    fixture=r39  r39-contract killed=no  [rc=0 fails=0 crash=False]  r40-contract killed=no  [rc=0 fails=0 crash=False failing=-]
```

Reading:
- `TOTOL` (the seat's `if total is not None:` → `if totol is not None:`, anchor count 1): the r39
  contract says `killed=no` with `crash=True`; the r40 contract says `killed=yes`. The M40-1 flip is
  reproduced for this mutant, on both fixtures.
- `M15`-`M18` (the r40 battery): the r39 contract says `killed=yes`, the same as the r40 contract. The
  lesson's "killed=no under the r39 contract" for these four mutants is FALSE. Their kills are not
  affected by the laundering path at all, since no traceback is produced.
- `M13` on the r40 fixture: `killed=no` under both contracts. This is the reachable survived path
  (the r40 fixture has no outside-root case, and the r39 fixture kills it). So the contract can return
  SURVIVED. The lesson's "shown able to fail" is not supported by this probe, but the contract is
  not vacuous.

### R2 — the echo site for TOTOL (where the r39 contract's crash probe fires)

Command: `python3 -B tests/fixtures/r39-drift-record-rules.py --tool $S/mut/TOTOL.py --work $S/work/probe2`
(landed bytes). Real output (`drive2.out`, a grep of the fixture's STDOUT):
```
(a) r39 fixture on TOTOL rc=1
(a) STDOUT line with Traceback: case-good=FAIL rc=1 want=0 missing=['SUMMARY', 'record_repos=2'] out='Traceback (most recent call last):   File ".../mut/TOTOL.py", line 451, in <module>     sys.exit(main(sys.argv[1:])) '
(a) STDOUT line with Traceback: case-total-before-rows=FAIL rc=1 want=0 missing=['SUMMARY', 'record_repos=2'] out='Traceback (most recent call last): ...'
(a) STDOUT line with Traceback: case-crlf=FAIL rc=1 out='Traceback (most recent call last): ...'
(a) STDOUT line with Traceback: case-outside-root=FAIL rc=1 want=2 missing=['RECORD-OUTSIDE-ROOT'] out='Traceback (most recent call last): ...'
(a) fixture stderr has Traceback: False
(a) SUMMARY: ['SUMMARY cases=7 pass=3 fail=4']
```
So the tool traceback is echoed into the fixture's stdout at `r39-drift-record-rules.py:79-80` and printed at `:133`.
The fixture's own stderr is clean, which is why the r40 stderr-only probe sees no crash.
(`SUMMARY cases=7` here, not 9, because the r39 fixture has 7 cases; `fail=4` matches the lesson.)

### R3 — the landed counter's kill attribution (`failing=` field)

Command: extracts `census/round-40/c3-counter.py` at `$C` into `$S/c3-landed.py` and runs
`python3 -B $S/c3-landed.py --root $L --rev $C --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/cli-landed`
Real output (`cli-landed.out`):
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
```
Cause: `census/round-40/c3-counter.py:116-117` filters on `l.endswith("FAIL")`, but a FAIL line ends with
the detail text, so the list is always empty. The same command at `8a5fbdb` (bytes equal to the lane HEAD copy,
sha256 `444af2692c5e...`) prints `failing=total-conflicting-second`, `failing=good,total-duplicate-identical,...`
and so on, which matches `census/round-40/records/c3-after.txt`. So the landed counter misses the attribution
the lesson claims; the later revision has it.

Command for the later revision (re-runs the receipt):
`python3 -B <(git -C $L show 8a5fbdbddaab24c5ba43fc6a133499efb405f214:census/round-40/c3-counter.py) --root $L --rev 8a5fbdbddaab24c5ba43fc6a133499efb405f214 --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/cli-8a5`
Output: the four `MUTANT ... killed=yes ... failing=<names>` lines and
`SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e`
(identical to `census/round-40/records/c3-after.txt`; exit 0).

### R4 — a detected mutant that aborts the fixture (probe B)

Mutant: the tool writes an undecodable byte to stdout before parsing the record. The anchor
`    rows, total = parse_record(args.record)\n` is unique in the landed tool; the mutant inserts
`    sys.stdout.buffer.write(b"\xff\n")` before it. Command: fixtures run on the mutant
(`python3 -B <fixture> --tool <mutant> --work <dir>`). Real output (`drive2.out`):
```
(b) r40 fixture on RAWBYTE: rc=1 SUMMARY=[] stderr_tail=["UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"]
(b) r39 fixture on RAWBYTE: rc=1 SUMMARY=[] stderr_tail=["UnicodeDecodeError: ..."]
(b) r39-contract on r40 fixture: killed=no (NO-SUMMARY rc=1)
(b) r40-contract on r40 fixture: killed=no (NO-SUMMARY rc=1)
```
The fixture's own `subprocess.run(..., text=True)` raises before its SUMMARY (`r40-drift-record-branches.py:82-85`).
Both contracts score this as SURVIVED. The mutant is detected (the fixture never completes), so "the r40 contract does
not score a detected mutant as SURVIVED" is false in general. This path is the "fixture has no own failure summary"
rule and is arguably correct by design, but the lesson does not state it. The tool emits raw bytes only in this
constructed mutant; the landed tool decodes record text with `replace` (`tools/souji-worktree-drift.py:147`). The
record reader's replace decode is inferred from the decode sites (147, 190, 197, 304), not exercised; the real tool is not shown to emit raw bytes.

### R5 — the lesson's evidence pointers

- `census/round-40/waves/w1/R40reviewer18.md` does not exist (`ls: cannot access ... No such file or directory`).
  The file is `.ufo/waves/round-40/w1/R40reviewer18.md`; its F1 (`:28`) and `totol` mutant (`:46`) match the
  lesson's description.
- `census/round-40/records/c3-after.txt` says `measured_at: 8a5fbdb…`, not the landed commit, and has no r39-contract
  column, so it cannot show the "killed=no under the r39 contract" half of the K1/K2 pair.

## Residual notes (not separate falsifiers)

- The r40 contract changed the standing A5 predicate ("no `Traceback` on either stream",
  `census/round-38/preregistration.txt:194`) to "stderr only". A tool crash now counts as a kill
  (`TOTOL` fails all 8 cases). The battery's base check (`base_killed`) would still reject a crash mutant that the
  r39 base also kills, so the M15-M18 battery result is not inflated by this; but the lesson's "the criterion was
  right" is not accurate.
- The C3 kill attribution is not enforced by the code: `killed = rc==1 and fails>0 and not crash`
  (`c3-counter.py:118`) does not require the failing set to contain a branch case. That was true at 128e412 and
  remains true at 8a5fbdb.
- Scope: I did not attack C1 or C2 here (other seats). Attack of C3 mutants M15-M18 themselves: each is killed by its
  branch case on the r40 fixture (`failing=` at 8a5fbdb) and survives the r39 base (`base_killed=0`), as the receipt says.

## Scratch

Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2critic11/` (drive.py, drive2.py, repro.py, copies of landed
bytes, mutants, work dirs) was REMOVED before yield: `rm -rf` ran and the path no longer exists (verified).
No lane file was written, no git mutation was run, no tool was installed.

## Appendix — `repro.py` (re-runnable; `python3 -B repro.py LANE REV SCRATCH`)

```python
#!/usr/bin/env python3
"""Re-runnable M40-1 check. usage: python3 -B repro.py LANE REV SCRATCH
Reads the committed bytes at REV with `git show` (no lane file is written), loads the committed r39 and
r40 C3 counters, and scores the same mutant bytes under each counter's own score() for each fixture."""
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
LANE, REV, S = sys.argv[1:4]
os.makedirs(S, exist_ok=True)


def show(path):
    data = subprocess.run(["git", "-C", LANE, "show", REV + ":" + path],
                          stdout=subprocess.PIPE, check=True).stdout
    dst = os.path.join(S, path.replace("/", "__"))
    with open(dst, "wb") as handle:
        handle.write(data)
    return dst


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


r39 = load("r39c3", show("census/round-39/c3-counter.py"))
r40 = load("r40c3", show("census/round-40/c3-counter.py"))
tool = show("tools/souji-worktree-drift.py")
fix40 = show("tests/fixtures/r40-drift-record-branches.py")
fix39 = show("tests/fixtures/r39-drift-record-rules.py")
src = open(tool, encoding="utf-8").read()
mutants = [("TOTOL", "    if total is not None:\n", "    if totol is not None:\n"),
           ("M13", r39.MUTANTS[2][1], r39.MUTANTS[2][2])] + list(r40.MUTANTS)
work = os.path.join(S, "work")
os.makedirs(work, exist_ok=True)
for mid, old, new in mutants:
    assert src.count(old) == 1, (mid, src.count(old))
    path = os.path.join(S, mid + ".py")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(src.replace(old, new))
    os.chmod(path, 0o755)
    k1, d1, _ = r39.score(fix40, path, work)
    k2, d2, _ = r40.score(fix40, path, work)
    k3, d3, _ = r39.score(fix39, path, work)
    k4, d4, _ = r40.score(fix39, path, work)
    print("%-6s fixture=r40  r39-contract killed=%-3s [%s]  r40-contract killed=%-3s [%s]" % (
        mid, "yes" if k1 else "no", d1, "yes" if k2 else "no", d2))
    print("%-6s fixture=r39  r39-contract killed=%-3s [%s]  r40-contract killed=%-3s [%s]" % (
        mid, "yes" if k3 else "no", d3, "yes" if k4 else "no", d4))
```

## Verdicts

- M40-1 diagnosis (laundering of a tool traceback through the fixture echo): REPRODUCED for `TOTOL` (R1, R2).
- M40-1 evidence ("the r40 battery's four mutants are killed=no under r39 and killed=yes under r40",
  "c3-after.txt reproduces it", "prints the failing case names" at 128e412): FALSIFIED (R1, R3, R5).
- "The fix can fail": SAFE on the survived path (R1 M13 under the r40 fixture), but not demonstrated by the lesson's
  own evidence.
- Residual: detected-by-fixture-abort is scored SURVIVED by both contracts (R4), and the A5 predicate changed (A6).
