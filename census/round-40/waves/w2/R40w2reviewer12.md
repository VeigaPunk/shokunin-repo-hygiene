# R40w2reviewer12 — operability review

## Attack and verdict
Attacked correctness defects in `census/round-40/c1-counter.py`, `c2-counter.py`, `c3-counter.py`, and `docstring-classes.py`: exit handling, exceptional input paths, initialization, regex scope, and scratch-path handling. **SAFE (no actionable defect found in scope)** for the C2 exercised path; no C1/C3 full counter invocation was performed, so their runtime behavior remains unverified here. No concrete source-level defect was established from the read.

## Evidence

First read frozen claims from `census/round-40/preregistration.txt` (unchanged). The landed commit stat command was:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e
```

It reported the commit `round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery`, including all four reviewed files.

Help/interface command, with real output:

```sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c2-counter.py --help
```

```text
usage: c2-counter.py [-h] --root ROOT --rev REV --base-rev BASE_REV
                     [--defect-base-rev DEFECT_BASE_REV] [--scratch SCRATCH]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --rev REV
  --base-rev BASE_REV
  --defect-base-rev DEFECT_BASE_REV
                        the revision where the unresolvable --rev defect was
                        live (the r39 base); the round's own --base-rev is the
                        r39 tip, where that defect is already repaired, so the
                        discriminating arm needs the defect revision
  --scratch SCRATCH
```

The landed counter was run against the current lane HEAD and frozen base, with an explicitly supplied scratch root:

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer12; L=/home/vgpnk/Projects/shokunin/souji-shokunin; R=$(git -C "$L" rev-parse HEAD); B=0242085909fb6a4ee041c5443d76316ac6d59d4b; printf 'rev=%s base=%s\\n' "$R" "$B"; python3 "$L/census/round-40/c2-counter.py" --root "$L" --rev "$R" --base-rev "$B" --scratch "$S"
```

Real output:

```text
rev=549d9ec53a1f5932337ff14438fcd22b0621828d base=0242085909fb6a4ee041c5443d76316ac6d59d4b
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```

Reviewed source ranges: C1 lines 90–362; C2 lines 72–370; C3 lines 96–211; `docstring-classes.py` lines 1–96. In particular, C1's `run` uses a `finally` cleanup around the scratch directory and returns refusal code 2 on the shown parse/register error paths; C2 similarly cleans scratch in `finally` and returns 2 for caught `ValueError`/`OSError`; C3 cleans scratch in `finally` and uses explicit return codes for refusal, pristine failure, and mutation results. The C2 landed execution's complete seven-leg success output is evidence for that exercised path, not proof against all odd inputs.

No LSP device was available in the provided tool inventory, so no semantic LSP references/diagnostics checks were possible. No tools were installed. Scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer12` was removed (verified by `test ! -e`).

## Residual risk / verification gaps
C1 and C3 counters were read but not run; C1/C3 edge-case behavior, including unusual malformed inputs and custom scratch paths, remains unverified. The executed C2 command used lane HEAD `549d9ec53a1f5932337ff14438fcd22b0621828d`, while requested instrument commit is `128e412b0ced3c243dc27c3dd3332054a611bc2e`; therefore this is not evidence of exact byte identity at the requested commit. No concrete file:line defect identified.