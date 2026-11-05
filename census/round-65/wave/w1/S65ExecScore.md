# S65ExecScore: independent reproduction of round-65 scoring (wave w1)

Seat: S65ExecScore (executor). Scope: verification battery from a clean scratch clone. No edits to the lane, no git mutation, no commits.

## Setup and provenance

- Lane tip read via `git rev-parse refs/heads/master`: `16da2445088ccca15aa32c66841d878ee57a8706` (matches the stated chronology tip).
- Lane `git status --porcelain` before the run: clean (0 entries).
- Scratch clone: `git clone --shared` of the lane into `/fast/scratch/hyaku/souji-r65/S65ExecScore/clone`. Asserted `rev-parse --show-toplevel` equals the clone path; clone tip `16da2445...`; clone status clean.
- All counters ran from inside the clone with `--work` under scratch (`.../S65ExecScore/work`, `wst`, `wself`, `regress`); none under /tmp, TMPDIR, or the lane root.
- Working-tree digests in the clone equal the digests at tip for the writer, both counters, the C1 matrix and the C2 population (see `digests.txt`).

## Results (independent reproduction)

| Artifact | Frozen target | Reproduced | Match |
|---|---|---|---|
| `repro-c1.txt` (C1 counter, base 4a43a4d9, rev 40a371d8, from clone) | `matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, EXIT=0 | `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, EXIT=0 | yes |
| `repro-c2.txt` (C2 counter, rev 40a371d8, tsv-rev 2761f0aa) | `rows=4 findings=0 verdict=PASS`, EXIT=0 | `SUMMARY rows=4 findings=0 verdict=PASS rev=40a371d8...`, EXIT=0 | yes |
| `regress-r60.txt` (r60 fixture) | `pass=8 fail=0` | `SUMMARY cases=8 pass=8 fail=0 ...`, EXIT=0 | yes |
| `writer-selftest.txt` | `cases=30 pass=30` | `SELFTEST cases=30 pass=30 fail=0`, EXIT=0 | yes |
| `c1-selftest.txt` | `cases=8 pass=8` | `SELFTEST cases=8 pass=8 fail=0`, EXIT=0 | yes |
| `c2-selftest.txt` | `cases=13 pass=13` | `SELFTEST pass cases=13 fail=0`, EXIT=0 | yes |
| `chronology-sweep.txt` | prod vs tip byte-identical over every `census/round-*/preregistration*.txt` | 34 files, 34 byte-identical, 0 differing (exit codes equal per file) | yes |
| `digests.txt` | pinned writer/counter/matrix/population digests | writer `be344a7d...`, C1 counter `6401b35d...`, C2 counter `afd4cb54...`, C1 matrix `a521170c...`, C2 population `0291e1d3...` (same at 2761f0aa and tip) | yes |

No mismatches were observed. Nothing was reconstructed from the L1's `records/` receipts; these are independent runs.

## Notes and minor observations (not mismatches)

- The C1 and C2 counters each print an `EXIT=` line of their own, and my wrapper appends a second `EXIT=` line, so the captured files show `EXIT=0` twice. The exit code itself is the wrapper's `$?`, which is 0.
- The C1 run reports `regress fixture ... cross-check=match` against the lane clone copy.
- The C1 selftest prints `# control always-refuse failed cases [1, 3] -> ALWAYS-REFUSE-REJECTED` as an expected control line. This is informational, not a failure.
- Chronology sweep: the pre-round production freeze-check (4a43a4d9, sha256 `5794ab27...`) and the tip freeze-check (`7d2cd741...`) produced identical default-mode bytes and identical exit codes on all 34 preregistrations, including `census/round-65/preregistration.txt` (exit 0, identical output). The round-65 freeze-check output is therefore unchanged between the two tools in default mode; the chronology arm (`--chronology`) was not exercised by this sweep, since the task specified default mode.
- Not reproduced by this seat (out of the assigned battery): the do-nothing controls (`controls/c1-do-nothing.txt`, `controls/c2-do-nothing.txt`) and the `--substance` / `--chronology` freeze-check modes.

## Installs

None. No tools were installed or upgraded. Only the lane's own scripts and the host's `git`, `python3`, `sha256sum`, `cmp`, `sed`, `cut`, `ls`, `tail`, `wc`, `grep` were used.

## Process notes

- A backgrounded bash call was passed `ready: null`, which made it run as a service; this had no effect on the outputs. One job-name lookup (`clone-lane`) reported not-found after the job had already exited with status 0; I verified the clone directly.
- Writes: only the deliver directory `.ufo/waves/round-65/w1/S65ExecScore/` and this report file, plus scratch at `/fast/scratch/hyaku/souji-r65/S65ExecScore/`.

## Scratch cleanup

Scratch root `/fast/scratch/hyaku/souji-r65/S65ExecScore/` is removed before yield (all receipts were written directly to the deliver directory before removal).

## Checks the main agent should run

- Compare `repro-c1.txt` SUMMARY and `repro-c2.txt` SUMMARY against the L1's `records/c1-after.txt` and `records/c2-after.txt`; both should agree with this seat's values.
- Optionally rerun the do-nothing controls to confirm `new_forgeries=12` (C1) and `findings=2` (C2) at the same revs.
