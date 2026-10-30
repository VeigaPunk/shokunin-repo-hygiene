# S44executor33 — absolute-link output-envelope probe

Axes: calibration / operability / coverage. This scoped check targets coverage of the r44 leaf-link refusal contract; it does not assess admission.

## Evidence

- Registration: `census/round-44/preregistration.txt` lines 22–28 names C3, base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`, and the frozen C3 target. Freeze candidate is `d314fd6e85d62565344fa6c4b102f52f62297884`.
- Contract/fixture: `tests/fixtures/r44-drift-symlink-refusal.py` lines 4–9 documents `--json OUT` final-component symlink refusal as rc 2 with `JSON-TARGET-SYMLINK`, disallows resolving/writing through it, while parent symlinks still resolve and regular output remains valid. Lines 109–179 define six isolated cases. The runner builds a synthetic git repo and record, then invokes the actual tool using `--root`, `--record`, `--timeout 30`, `--json`.
- Tool: `tools/souji-worktree-drift.py` lines 239–281 opens output without following symlink components; lines 451–466 show CLI and refusal rc contract.
- Exact bounded command:
  `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r44-drift-symlink-refusal.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r44/S44executor33`
- Exact observed stdout:
  ```
  case-dangling-symlink-refused=PASS
  case-outside-symlink-refused=PASS
  case-subdir-symlink-refused=PASS
  case-symlink-dir-refused=PASS
  case-regular-json-written=PASS
  case-parent-symlink-ok=PASS
  SUMMARY cases=6 pass=6 fail=0
  ```
- Read-only source comparison commands: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`; `rev-parse HEAD` → `d314fd6e85d62565344fa6c4b102f52f62297884`; `rev-parse --verify 55d7af6f5a22340f7a3de1c386e514ababfaa75f^{commit}` → `55d7af6f5a22340f7a3de1c386e514ababfaa75f`. `git show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:tools/souji-worktree-drift.py | sha256sum` → `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`; candidate `sha256sum tools/souji-worktree-drift.py` → `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`. The bytes differ, so this probe establishes candidate behavior only, not the before/after base-arm delta.

## Findings and limits

All six fixture assertions passed against the actual frozen candidate, including each absolute output leaf symlink case; no unintended target creation/write was detected by the fixture, and both positive cases wrote JSON successfully. Thus the frozen cutover affects this case as implemented: candidate enforces the documented leaf-symlink refusal while retaining the regular-leaf and symlinked-parent success paths. The base blob's differing digest alone is not a behavioral comparison: no base-arm fixture execution was performed, and no direct before/after result is claimed. This is the assigned fixture's six-case bounded probe, not whole-suite validation. No tools installed or updated.
