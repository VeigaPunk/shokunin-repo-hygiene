# S60ExecRecorderFix — round 60, wave 1, seat report (C2 fixture)

Seat: executor, leaf. Scope: build and run the C2 8-case receipt-writer fixture; score the base
recorder and the S60ExecRecorder candidate. No production files touched; no git mutations outside
throwaway fixture repos; no subagents spawned; no tools installed (python3 3.14.8 and git 2.56.0
already present; RULES.md read; pacman paused — nothing filed).

## Delivered (absolute paths)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecRecorderFix/r60-receipt-write.py
  (candidate for tests/fixtures/r60-receipt-write.py; sha256
  d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecRecorderFix/base-run.txt
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecRecorderFix/new-run.txt

## Commands run (exact)
1. `python3 -B r60-receipt-write.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/record-receipt.sh --work /fast/scratch/hyaku/souji-r60/S60ExecRecorderFix/work-base` → exit 1 (expected: base is not the hardened writer)
2. `python3 -B r60-receipt-write.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ExecRecorder/souji-receipt-write.py --work /fast/scratch/hyaku/souji-r60/S60ExecRecorderFix/work-new` → exit 0
Full stdout/stderr and exit codes are verbatim in base-run.txt / new-run.txt. Scratch work dirs were
removed after the run files were written into the delivery dir.

## Observed results
Candidate (S60ExecRecorder/souji-receipt-write.py, flag form):
`SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, fixture exit 0.

Base (census/round-57/record-receipt.sh, positional form):
`SUMMARY cases=8 pass=4 fail=4 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, fixture exit 1.
- Base PASSES: case 3 atomic-in-flight, case 4 kill-residue, case 6 rev-short, case 7 instrument-absent.
- Base FAILS: case 1 (receipt lacks the `command=` field the hardened contract adds), case 2
  (clobbers pre-existing OUT, rc=0), case 5 (execs `--max-bytes` as the wrapped command, rc=127 —
  honest unbounded behaviour), case 8 (no dirty-tree check).

## Calibration finding: frozen C2 claim "base = 3/8" is falsified — measured 4/8
The base recorder captures the wrapped command via `OUTPUT=$(...)` in memory and writes OUT only
afterwards. That makes it atomic-in-effect (case 3) and kill-clean (case 4: SIGKILL of its process
group leaves neither OUT nor any temp). It fails case 1 solely because the hardened contract adds
`command=`. The frozen 3/8 most plausibly assumed the base writes OUT non-atomically in flight
and/or counted case 1 as a pass. The claim understates the base by exactly one case (case 4);
the hardened writer's real deltas over base are: overwrite refusal, dirty-tree refusal, output
bound, `command=` field, and kill-safe temp discipline (base has no temp at all to leak).

## Fixture design decisions (so reviewers can attack them)
- Two invocation forms, `--style auto` (default): `*.sh` → positional
  `TOOL LANE REV INSTR OUT -- CMD...` (base-compatible); otherwise flag form
  `TOOL --root LANE --rev REV --instrument INSTR --out OUT -- CMD...` (candidate contract).
  Override with `--style positional|options`.
- `--max-bytes 65536` is passed ONLY on case 5 (the bound is that case's subject), between OUT and
  `--`: the candidate parses it there; the positional base execs it as the command, showing honest
  unbounded behaviour. An earlier uniform-every-case variant corrupted the base's argv on all 8
  cases (rc=127 everywhere) and masked cases 3/4 — measured 2/8 {6,7}; rejected as unfaithful.
  S60MutMutation independently reproduced that 2/8 before the fix.
- Digest definition: `instrument_sha256` = sha256 of the committed instrument BYTES at rev
  (`git show REV:INSTR`), identical to the base's `git show | sha256sum` by construction. The
  candidate's digest method (`git cat-file blob`) was stated by its author and NOT re-measured here.
- `command=` accepted as exact space-join or any form whose shlex.split equals the wrapped argv.
  The candidate's emission form (shlex.join) was stated by its author and NOT inspected here;
  case 1 passed on the candidate, so its `command=` line matched the accepted forms.
- Kill case uses `start_new_session=True` + `os.killpg` at ~0.4s against a 1s command, then a 0.3s
  settle before the residue check. In-flight check at ~0.3s.
- Controls: always-write stub must fail {2,4,5,6,7,8}; always-refuse stub must fail case 1.
  Measured: always-write failed all 8; always-refuse failed {1,3}. Fixture exit 0 iff 8/8 and both
  rejected — a pure refuser cannot reach exit 0 (it fails case 1).
- Independence/re-runnability: fresh throwaway repo per case under `<work>/case-<n>/`, wiped at
  start; `git -C D init -q -b main`, toplevel asserted == D before first commit, throwaway identity
  repo-local only; all later git calls name `-C`. Fixture writes only under `--work`.

## Named limits
- Case 5's base "fail" is via argv misparse (rc=127), not a measured unbounded write; the predicate
  (exit 2 ∧ OUT absent) is what fails, and the detail line records the mechanism.
- Cases 3/4 are wall-clock (0.3s/0.4s vs a 1s command); extreme load could flake them. Not observed.
- For a tool that refuses before doing anything, case 4 can pass vacuously (tool exited before the
  kill); the always-refuse control's required case-1 failure keeps such a tool from reaching exit 0.
- Style auto keys on the `.sh` extension; a flag-form shell tool or positional Python tool would
  need an explicit `--style`.
- The fixture scores behaviour only (exit codes, bytes, presence/absence); it does not judge
  receipt prose quality.
- Candidate was scored from the sibling delivery dir (read-only use); if L1 integrates a different
  candidate revision, re-run for a fresh new-run.txt.

## Peer coordination
- S60ExecRecorder: CLI contract locked (flag form, receipt order, digest bytes, refusal set, exit
  semantics); their candidate measured 8/8.
- S60MutMutation: case-2 self-contradiction they caught was fixed; frozen fixture hash and both
  measured scores sent so their pristine/mutant/restored triplets use these bytes.
