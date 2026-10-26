# deliver-skill-rows — r33 w1 seat SwarmScribe47

Provenance: base `6017a482e7068d5afb7617640198fbb0fe743357`; preregistration
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Every SKILL.md line reference below is read at the preregistration
commit; every QUALITY.md reference at the current lane worktree (which ends at `Q74`, no `## Round 33 criteria`
section yet). `<L1>` marks a value not read from bytes this run. This file is a draft: it writes no product file.

## (a) two `## Gate registry` rows (SKILL.md)

Placement: append directly after the table's last row, `| r32-c3-counter | …` (line 258 at `2d9bca5`), before the
blank line at 259 and `Sources for this skill:` at 260. Column shape copied from the table header at line 197:
`| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |`.
All exit-code wording is read from the two counters' docstrings at `2d9bca5`; `LANE`, `REV`, `BASE`, `PREREG`, `DIR`
keep the placeholder spelling the existing rows use.

| r33-c1-counter | gate | `python3 -B census/round-33/c1-counter.py --root LANE --rev REV --list-rev PREREG --scratch DIR [--only K01,...]` | 0 `SUMMARY items=24 agree=24 mismatches=0 restated=<n>` (exit 0 iff mismatches=0); 1 any ITEM line that is not `AGREE`, including a `BAD-ROW(...)`, `BAD-CAUSE(...)` or `RUN-FAILED(...)` detail; 2 could-not-evaluate (non-40-hex or unresolvable `--rev`/`--list-rev`, `census/round-33/c1-items.tsv` absent or malformed at `--list-rev`, `SCORECARD.md` absent at either revision or not starting with its `--list-rev` bytes, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, unknown `--only` id, git failure). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; `census/round-33/records/controls.txt` holds the do-nothing red arm `SUMMARY items=24 agree=19 mismatches=5` rc 1 (K04 K05 K16 K17 K18), and `census/round-33/records/feasibility.txt` holds the two scratch-list-rev arms — the junk rows (`65812db`) each `MISMATCH … BAD-CAUSE`, for a substring statement and for a true line with a non-causal commit, so neither binds, and the feasibility leg (`190b4b1`) binding K05 and K18 `AGREE … restated`; both hashes are scratch commits, present only in that receipt | `census/round-33/c1-items.tsv` read at PREREG and never at REV; the `### Round 33 capability currency` rows of `SCORECARD.md` read at REV, each cause commit executed at the cause's parent and at the cause | private `git clone --no-local --no-checkout` per item under `--scratch` (origin removed, detached at REV, `{SCRATCH}` a per-item dir), removed after the run; read-only on `--root` | souji |
| r33-c2-counter | gate | `python3 -B census/round-33/c2-counter.py --root LANE --rev REV --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev PREREG --scratch DIR [--only O1,...]` | 0 `SUMMARY legs=11 pass=5 fail=0 harm=0` (exit 0 iff fail=0 and harm=0); 1 any O leg that is not `PASS`, or any FAILed G guard; 2 could-not-evaluate (non-40-hex or unresolvable `--rev`/`--base`/`--list-rev`, `bwrap` or `strace` absent, `census/round-33/c2-legs.tsv` absent or malformed at `--list-rev`, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, unknown `--only` id, clone failure or clone toplevel mismatch). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; the same command with `--rev` at the preregistration commit (tools identical to base `6017a48`) reads `SUMMARY legs=11 pass=0 fail=5 harm=0` rc 1 in `census/round-33/records/controls.txt`; the feasibility leg in `census/round-33/records/feasibility.txt` (scratch commit `6a409e1`) turns O2 and O4 green while G4 reds on the changed r15 pin (`legs=4 pass=2 fail=0 harm=1 partial=1`), which is the declared Q73 re-pin step, not a pass | `census/round-33/c2-legs.tsv` read at PREREG, leg kinds and per-kind PASS rules in its header: base line equality for every kind, the sandbox leg's half-of-base file-creating syscall count, and the slash leg's equality with the same `TMPDIR` spelled without the trailing slash | two private `git clone --no-local --no-checkout` copies (base, rev) under `--scratch`, `git clean -fdx` before every run, `bwrap` with read-only empty `/tmp`, `/var/tmp`, `/dev/shm`, strace logs in `--scratch`, all removed after the run; read-only on `--root` | souji |

Fields not read from bytes: the C1/C2 landing commits, the tip readings, and the C1 `restated=<n>` value at landing
(`5` is the expected count from the frozen five-item mismatch set, not a measured tip reading) — `<L1>`.

## (b) one `## Error patterns (false-SAFE signatures)` bullet (SKILL.md)

Placement: end of that section, directly after the `r32` jj-mtime bullet's last line (line 158,
`that no prune reaching the object has completed — never that a deletion was proved absent.`) and before the
paragraph beginning `The repository-content bound is not a kernel/filesystem sandbox:` at line 160.

- **A trailing slash in `TMPDIR` makes a string comparison miss a kernel-canonical path** (r33, C2; S224, S225 `<L1>`): repeated slashes collapse to one in pathname resolution (S224 `<L1>`), but a shell `case` pattern and a ledger row comparison are byte comparisons, and `readlink -- /proc/<pid>/fd/1` also prints the file under the kernel's single separators (S225 `<L1>`). With `TMPDIR=/s/` the census pattern `"${TMPDIR:-/tmp}"/souji-census-now.*/*` is `/s//souji-census-now.*/*` and never matches, and `mktemp -d "${TMPDIR}/…"` hands back a `//`-spelled scratch path whose ledger rows stop matching the canonical spelling: with `TMPDIR` ending in `/` `bash tools/souji-census.sh --selftest` prints `selftest: 69 checks, 10 failed` and `bash tools/souji-verify.sh --selftest` prints `selftest: 49 checks, 2 failed` (the two `FAIL R9 … ledger revocation was reached` checks), each `0 failed` under the same `TMPDIR` written without the trailing slash. The failing-check count moves with the run — 10 in `feasibility.txt:168`, 12 in `controls.txt`, 13 in this seat's re-run at the same base bytes — so quote the exit code and the `failed` verdict, never the count, as the stable observation. Canonicalise the caller's `TMPDIR` once at entry — strip trailing slashes, keep `/` — never widen a skip or normalise only one side of one comparison. Recheck: `python3 -B census/round-33/c2-counter.py --root . --rev <full40> --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch <dir> --only O4,O5`.

Source rows: `corpus/SOURCES.md` at `2d9bca5` ends at `S223`, and `corpus/lessons/round-32.md` already prints the id
`S224` for the git-gc candidate — the two ids this bullet cites were not readable as rows, hence `<L1>` (see the
report's findings; an id collision the L1 must settle).

The `10 failed` figure is read in `census/round-33/records/feasibility.txt:168`; the frozen counters' do-nothing run in
`census/round-33/records/controls.txt` prints `12 failed` for the same leg at the same base bytes, and this seat's
re-run at `6017a48` printed `13 failed` — the failing-check count moves while the rc-1 verdict and the `69 checks`
total hold. The slash PASS rule compares rc and last line between the rev no-slash and rev slash runs, both of which
the repair must make `0 failed`, so the moving count sits only on the red side and changes no target.

## (c) one QUALITY.md criterion row

Placement: a new section at the end of `corpus/QUALITY.md` (the file ends at `Q74` inside `## Round 32 criteria`),
using the section's column shape `| id | criterion | applies to | check | motivating evidence |`.

```markdown
## Round 33 criteria

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q75 | A capability row's stated outcome is re-run at the round tip, and a drifted row is corrected only append-only, with an executed cause. Every SCORECARD.md row that names a runnable command and an outcome is one item; the item's command runs at the measured revision in a private clone with a `TMPDIR` scratch, and the row binds only if the run's exit and its stated outcome both hold. A row that no longer holds is restated in a new appended section — never edited in place, and the pre-existing bytes must still prefix the file — as `<line>`, exit, `same` or a corrected argv, one complete digit-bearing output line, a full-40 cause commit and a reason; the cause is executed, because value drift needs the original outcome to hold at the cause's parent and fail at the cause, while an argv correction needs the cause to have written the row and the row's own command to fail there. A restatement whose cause does not survive that execution is a `BAD-CAUSE` mismatch, not a narrative, and the append-only prefix is checked, not asserted. | SCORECARD.md capability rows; round counters | `python3 -B census/round-33/c1-counter.py --root LANE --rev REV --list-rev PREREG --scratch DIR` prints `mismatches=0` at the landing commit and at the tip; the do-nothing arm at base reads `mismatches=5` over 24 items and both junk arms print `BAD-CAUSE`, so a target of 0 is neither free nor unreachable | `corpus/lessons/round-33.md` `<L1>` (not landed at write time, so the lesson quote is a placeholder for the L1); `census/round-33/records/controls.txt` (do-nothing `mismatches=5`); `census/round-33/records/feasibility.txt` (K05 value drift at `ddb7347`, K18 argv correction at `07f83e6`) |
```

Fields not read from bytes: the lesson row text and its line pointer — `corpus/lessons/round-33.md` does not exist at
base, at the prereg commit, or in the worktree at write time — `<L1>`.
