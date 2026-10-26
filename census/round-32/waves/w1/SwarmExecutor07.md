# SwarmExecutor07 — r32 w1 C2 operability (T01, T02, T29, T30)

## Status
STATUS: PASS — `tools/souji-landing-gate.py` and the two gate-running fixtures create all scratch through tempfile, so the parse snapshot (`:1182`) and the `--selftest` root (`:1499`) honour the caller's TMPDIR; all four C2 items PASS under bwrap with `/tmp`, `/var/tmp`, `/dev/shm` read-only, exit code and last digit-bearing line identical to base, file-creating syscalls not dropped.

## Evidence

Contract sentence (frozen), `census/round-32/records/preregistration.txt:9`: "its parse snapshot and selftest still write under `/var/tmp` ignoring `TMPDIR` (`tools/souji-landing-gate.py:1182` and `:1499`)".

Scratch clone `/fast/scratch/hyaku/souji-r32/C2Gate/c` (origin removed; `rev-parse --show-toplevel` printed it), patch committed as scratch rev `81d271867f6a4e40ad42ae43aa30f60d233171dd` on lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; item list at `--list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` (unchanged, prereg). Scratch removed after delivery.

Counter (verbatim, run this wave):
```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py --root /fast/scratch/hyaku/souji-r32/C2Gate/c --rev 81d271867f6a4e40ad42ae43aa30f60d233171dd --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T01,T02,T29,T30 --scratch /fast/scratch/hyaku/souji-r32/C2Gate/cnt
ITEM	T01	PASS	base=rc0:W8306:SELFTEST pass=65 fail=0	sbox=rc0:W8312:SELFTEST pass=65 fail=0	
ITEM	T02	PASS	base=rc0:W25:SUMMARY findings=0 checked_reg=65 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=18 status_lines=75 carry_heading=1 checked_reports=114	sbox=rc0:W26:SUMMARY findings=0 checked_reg=65 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=18 status_lines=75 carry_heading=1 checked_reports=114	
ITEM	T29	PASS	base=rc0:W689:cases=7 pass=7 control=FALSE-GREEN-REJECTED	sbox=rc0:W697:cases=7 pass=7 control=FALSE-GREEN-REJECTED	
ITEM	T30	PASS	base=rc0:W875:cases=10 pass=10 control=FALSE-GREEN-REJECTED	sbox=rc0:W885:cases=10 pass=10 control=FALSE-GREEN-REJECTED	
SUMMARY items=4 pass=4 fail=0 partial=1 rev=81d271867f6a4e40ad42ae43aa30f60d233171dd
```

Patched commands, TMPDIR set to `/fast/scratch/hyaku/souji-r32/C2Gate/tmp`, then TMPDIR unset (rc, last line):
```
T01-norm	rc=0	SELFTEST	pass=65	fail=0
T02-norm	rc=0	SUMMARY	findings=0	checked_reg=65	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=75	carry_heading=1	checked_reports=114
T29-norm	rc=0	cases=7 pass=7 control=FALSE-GREEN-REJECTED
T30-norm	rc=0	cases=10 pass=10 control=FALSE-GREEN-REJECTED
T01-unset	rc=0	SELFTEST	pass=65	fail=0
T02-unset	rc=0	SUMMARY	findings=0	checked_reg=65	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=75	carry_heading=1	checked_reports=114
T29-unset	rc=2	cases=0 pass=0 control=FALSE-GREEN-ACCEPTED
T30-unset	rc=2	cases=0 pass=0 control=FALSE-GREEN-ACCEPTED
PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)
```
The two `-unset` rc=2 lines are the fixtures' pre-existing documented prerequisite (`r30-landing-gate-discovery.py:36`, `r31-landing-gate-precision.py:53`), not a change: those fixtures already required TMPDIR before the patch. The gate itself (`T01`, `T02`) falls back to Python's default temp root when TMPDIR is unset, rc 0 and the same last line.

Delivered bytes are the committed blobs (`git hash-object` on each delivery equals `HEAD:<path>`):
```
tools/souji-landing-gate.py                 10069f5cd22e64c52cb2392d56e7a6abd8ebaed6
tests/fixtures/r30-landing-gate-discovery.py 53e8e80c85119162702dd81a07b8db641c33e7f1
tests/fixtures/r31-landing-gate-precision.py 13b551d933b8c5c0a3ef2b1b464262e3effa42e2
```

Diff scope: `git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- <the three files>` = 10 lines in the gate, 5+5 in the fixtures; nothing else touched, worktree clean after the commit.

## Findings

1. **Fixed, T01/T02.** `tools/souji-landing-gate.py:1182` `snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-")` and `:1499` `top = tempfile.mkdtemp(prefix="souji-landing-gate-selftest-")` — the `dir="/var/tmp"` keyword is gone, so both roots resolve through tempfile/TMPDIR. No other filesystem root is hard-coded; no shell guard of the `/var/tmp/<prefix>.*` kind exists in this file (sweep: `grep -n 'tmp\|TMP' tools/souji-landing-gate.py` yields only `:25`, `:1182`, `:1366`, `:1499`).
2. **Doc claims in the same three files corrected** (no behaviour, no output line changes): gate docstring `:24-26` now reads "tempfile.mkdtemp() snapshot (honouring the caller's TMPDIR)"; selftest section comment `:1367-1368` no longer names `/var/tmp`; `tests/fixtures/r30-landing-gate-discovery.py:42-45` and `tests/fixtures/r31-landing-gate-precision.py:59-62` no longer assert the gate "pins its parse-snapshot directory to /var/tmp".
3. **Work not dropped** (the counter's second predicate): sbox creations ≥ base in every item — T01 8312/8306, T02 26/25, T29 697/689, T30 885/875 (threshold `w1*2 >= w0`). No `work-dropped` flag on any row.
4. **Out-of-scope stale claim, for the L1**: `SKILL.md:200` (souji-landing-gate registry row, isolation cell) still says "private /var/tmp removed". That sentence is false against the patched gate. I did not edit it — my item names only the three files above — so the row needs an L1 (or wave-2) update in the same landing commit, otherwise the registry row contradicts the tool.
5. **Test data left alone, as instructed**: `tests/fixtures/r31-landing-gate-precision.py:300` carries a synthetic `.gitignore` body `"/tmp/\n"`; it is fixture data, creates nothing, and was not touched.
6. **Historical copies out of scope**: `census/round-26/waves/assimilation/validate/tools/souji-landing-gate.py:1022,1339`, `census/round-30/waves/w1/deliver-souji-landing-gate.py:1070,1387` and `census/round-31/waves/w1/deliver-souji-landing-gate.py:1174,1491` retain the literal; they are census artefacts, not live lane tools (not in the C2 item set), and I did not touch them.

Environment: no installs, no pacman transaction, no tool upgrade; `python3 -B` throughout (no `__pycache__`); lane worktree only read; no git/jj mutation in the lane; scratch `/fast/scratch/hyaku/souji-r32/C2Gate` removed after delivery. Unrun: the full 27-item C2 `fail=0` (other seats' items) and the landing-commit/tip measurements — the L1 owns those.

## Deliveries
- `.ufo/waves/round-32/w1/deliver-souji-landing-gate.py`
- `.ufo/waves/round-32/w1/deliver-r30-landing-gate-discovery.py`
- `.ufo/waves/round-32/w1/deliver-r31-landing-gate-precision.py`
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor07.diff`
