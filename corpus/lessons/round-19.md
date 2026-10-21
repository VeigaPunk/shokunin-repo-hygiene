# Round 19 — wrap-aware carries, truthful audit shapes, durable revisions, F5 knowledge

Declared claims, in order (baseline `3ab2c81`, the round-18 closure tip):
**C1 calibration** (lowest axis, 7) — the landing gate's carry check is paragraph-aware and
the seat auditor recognizes the shapes the r18 contract actually produced.
**C2 operability** — r13/r14 evidence runners and both count-claims consumers stamp only a
durable 40-hex revision whose tracked measured bytes equal the working tree.
**C3 coverage** — F5 process residue gains its first admitted `corpus/knowledge/` entry from
sources opened this round, with its SKILL rule and README row; list-only, no reap authority.

## Measurements (measured before the report; counting commands in the report)

- **C1 carry.** `python3 tests/fixtures/r19-carry-wrap.py` → `SUMMARY total=4 failed=0
  base_discriminating=2`: the pre-fix gate passes the unmarked cut with exit 0 and rejects
  the wrapped lesson bullet with `LG-SEAT-UNCARRIED`; the changed gate flags the unmarked
  cut and passes the marked, complete and wrapped-bullet cases.
  `python3 tools/souji-landing-gate.py --selftest` → `SELFTEST pass=65 fail=0` (61 before;
  four wrap cases added). The strict branch leaves the five pinned replays `match: True`
  (`census/round-19/gate-replays-r19.json`) and, at `3ab2c81 --round 18`, reports 0 findings
  over 10 carried markers and 175 reports (`census/round-19/gate-r18-strict-fleet.json`).
  A deterministic in-memory invariant probe (`census/round-19/probe-carry-invariants.py`) over 400
  seeded paragraphs reports 562 boundary cuts and 842 mid-line cuts with 0 violations
  (`census/round-19/carry-invariants.txt`): complete paragraphs carry, unmarked first-line cuts
  do not, boundary-marked cuts do, true mid-line cuts do not.
- **C1 audit.** `python3 tools/souji-seat-audit.py --selftest` → `pass=73 fail=0` (66 before).
  `python3 tests/fixtures/r19-seat-audit-shapes.py` → `total=5 failed=0 base_discriminating=2`.
  Re-auditing the committed r18 transcripts with the changed auditor
  (`census/round-19/seat-audit-r18-recheck-w{1,2}.json`): w1 majors 139 → 134, with
  `V-WRITE-SCOPE` 119 → 112, `V-WRITE-RELATIVE` 13 → 12, and the new `V-SIGNAL` 0 → 3;
  w2 majors 92 → 92. The 9 confirmed driver-state reads and the real signal calls remain
  major — the change removes authorized delivery shapes and adds a detection class, it
  does not launder violations.
- **C2.** `python3 tools/souji-rev-pin.py --selftest` → `total=11 failed=0`.
  `python3 tests/fixtures/r19-rev-pin.py` → `total=13 failed=0 base_discriminating=6`.
  `python3 census/round-13/count-claims.py` and `census/round-14/count-claims.py` with the
  default/`HEAD` → exit 2 with the typed refusal; with `3ab2c81` → exit 0 and the same
  inventory. `census/round-13/run-verification.py --round 19` on the dirty lane (captured in
  `census/round-19/c2-smoke.txt`) → exit 2, "tracked measured paths
  differ", no output file.
- **C3.** `python3 census/round-13/count-claims.py <rev>`: admitted 6 at the base and 7 at
  the r19 tip (the preregistered 5 was the r18 prose defect, corrected append-only in
  `.ufo/waves/round-19/preregistration.txt`). Source census: start exit 0 over the base
  bytes (78 rows, sha256 `74c5e01e…`), end exit 0 (85 rows, sha256 `24a411da…`).
- **D2.** `python3 census/round-19/verify-agreement-pin.py --selftest` → 5/0; `--emit` then
  `--check` on `census/round-19/proc-agreement-pinned.json` → exit 0.
- **D5.** `tests/fixtures/r15-census-config.py --tool tools/souji-census.sh` → 20/0;
  `tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` → 29/0.

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| R19-M1 | The C3 before-count was preregistered from prose ("admitted knowledge stays five", r18 README/SCORECARD) instead of the lane's own counter. `census/round-13/count-claims.py b576341` reports **6**: eight `knowledge/*` files minus `.tsv` and one HELD. | `.ufo/waves/round-19/preregistration.txt` Correction; `census/round-19/counts-start.json` | the counting command required before a before→after is written; the r18 prose had no gate | corrected the preregistration append-only and used 6→7; the README r19 section records the historical count defect |
| R19-M2 | The carry fixture resolved its own lane root one directory too high (`tests/` instead of the lane), so the default `--tool` path pointed under `tests/`. | fixture first run: `prerequisite: tool ... is not a file`, with the resolved path under `tests/` because the lane root was one directory too high | the fixture's own prerequisite exit 2 (it failed closed, not silently) | three `dirname` levels; `--tool` resolved against the lane root |
| R19-M3 | The rev-pin fixture expected the base commit to pass the clean-tree case after the sandbox had advanced to a second commit; the guard was right, the expectation was wrong. | `CASE FAIL durable-clean-accept … differ from …` | the fixture's own CASE output | clean/refusal cases use the HEAD revision; the older revision is exercised only with `--no-tree-check` |
| R19-M4 | The auditor fixture demanded three base-arm discriminators, but the private-workdir shape was already allowed at base; only the delivery false major and the missing signal class discriminate. | `CASE FAIL base-vacuity only 2 cases differ` | the base-arm comparison in the fixture | threshold 2, with the workdir and tools-write cases labeled preservation controls |
| R19-M5 | A `.md` preregistration under `.ufo/waves/round-19/` would satisfy the landing gate's prefix scan as a "report", so the carry check could report `checked_reports>=1` with zero seat reports. | gate `check_carry` scans every `*.md` under `.ufo/waves/round-<N>/`; the file was named `preregistration.md` | reading the scan while preparing the pre-submit check (no gate run needed) | renamed to `preregistration.txt`; specs and this lesson re-pointed |

## Gate

### Sources opened this round (URL · access 2026-10-21 · located quote ≤25 words)

- **S079** https://git-scm.com/docs/git-rev-parse (last updated 2.56.0), § OPTIONS `--verify`:
  "Verify that exactly one parameter is provided, and that it can be turned into a raw
  20-byte SHA-1" (20 words). The page does not claim durable reachability or a worktree
  match; the helper adds both. The 20-byte wording predates SHA-256 repositories.
- **S080** https://git-scm.com/docs/git-for-each-ref (last updated 2.54.0), § OPTIONS
  `<pattern>...`: "If one or more <pattern> parameters are given, only refs are shown that
  match against at least one pattern" (19 words). Selecting `refs/heads refs/tags
  refs/remotes` excludes `refs/jj` by construction; `%(*objectname)` peels annotated tags.
- **S081** https://git-scm.com/docs/git-diff, § OPTIONS `--quiet`: "Disable all output of
  the program. Implies `--exit-code`." (8 words). Exit 1 therefore means "tracked measured
  paths differ", never clean.
- **S082** https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html (man-pages 6.19,
  2026-02-08), § DESCRIPTION: "This is a symbolic link to the current working directory of
  the process." (15 words). No `(deleted)` suffix is documented here.
- **S083** https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html, § DESCRIPTION: "a
  subdirectory containing one entry for each file which the process has open" (17 words);
  pipes and sockets read `type:[inode]`, not a pathname.
- **S084** https://man7.org/linux/man-pages/man5/proc_pid_wchan.5.html, § DESCRIPTION:
  "The symbolic name corresponding to the location in the kernel where the process is
  sleeping." (15 words); access is ptrace-gated.
- **S085** https://man7.org/linux/man-pages/man5/proc_pid_status.5.html, § DESCRIPTION:
  "Provides much of the information in /proc/pid/stat and /proc/pid/statm in a format
  that's easier for humans to parse." (23 words).
- Rechecked, not changed: **S075** proc_pid_stat(5) field 6 "The session ID of the
  process." (6 words) and field 22 starttime tick units; **S076** proc_pid_exe(5) "If the
  pathname has been unlinked, the symbolic link will contain the string ' (deleted)'
  appended to the original pathname." (20 words). The cwd/fd suffix rule remains
  fixture-carried, not documented.

### Registry changes (old → new)

S079–S085: absent → opened 2026-10-21, tier A, status `mined`, recheck `on-release`,
used-by `corpus/lessons/round-19.md` (S082–S085 additionally
`corpus/knowledge/process-residue-observations.md`). No existing row's immutable cells
changed; S075/S076 were re-opened and keep their status. Counts 78 → 85 rows (A 74 → 81,
B 3, C 1; mined 59 → 66, queued 15, rejected 4, malformed 0).

### Acceptance

All named structural acceptance is rerun by `python3 census/round-19/run-acceptance.py
--rev <r19 tip> --output census/round-19/final-verification-<short>.json`; the record carries
each command, expected and observed exit, parsed self-test tallies and the changed-file
digests. L1 runs it once after the round commit; a red command is reported, not re-rolled.

## Residuals (open)

- **Wave evidence is appended below after dispatch**: this file's `## Seat-reported failures`
  section is the last section so wave lines append without rewriting committed bytes.
- **Carry scope.** The strict branch applies only when the gate scans a round ≥ 18; the
  historical round-16 landing record keeps its 0 findings by design. The seven wrapped
  quotes there are known and are not retro-corrected.
- **Audit scope.** Private clone workdirs whose slot name differs from
  `/var/tmp/souji-r<N>-<Seat>/` remain `V-WRITE-SCOPE` majors; the r18 adjudication already
  read those calls as authorized. The allow-list stays exact; the residual is disclosed,
  not laundered. The auditor still cannot see a signal hidden past a rendered truncation.
- **C2 contraction.** A run that measures uncommitted work now refuses; the caller must
  commit first or measure a named commit. This is the intended trade and is reported as
  such. `cache-demonstration.py` returns blocked (exit 2) while the harness paths are
  dirty; after the round commit it must return 0 and that receipt is in the final record.
- **D1.** The closure-owed receipt binding a cited revision is produced at the r19 commit
  and committed in the round's second commit (the report may cite only that receipt).
- **D3.** The gate's 61-case baseline is receipt-backed (`census/round-18/final-verification-4800fd7.json`);
  the old 33 baseline stays labeled static.
- **F5 reap.** The 58 listed fixture orphans remain unreaped; the entry grants no reap
  authority and the operator L0 line stays open.

## Seat-reported failures

Round 19 seat failure-channel lines, appended after the waves return (each quoted verbatim
with its disposition).
