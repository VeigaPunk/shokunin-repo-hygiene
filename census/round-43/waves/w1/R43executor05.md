# R43executor05 — C3 tool candidate

- Candidate: `.ufo/waves/round-43/w1/R43executor05/candidate.py`
- SHA-256: `e24619364e030a76572b323dd0cd06ec9d4f74ca4c8c964bc328c42b16c0d0a5`
- Behavior: lstat of absolute `--json` path runs at the start of `run`, before root/record guards. Existing final-component symlinks are refused as `JSON-TARGET-SYMLINK`; missing leaves remain creatable and non-symlink path handling retains existing resolution.
- Anchors command: Python AST-read `c3-counter.py` MUTANTS+EQUIV and counted candidate bytes. Output: `anchors 22 all_unique True`; each of S03,S11,S12,S13,S17,S22,S25,S33,S34,S35,S43,S44,S53,S58,S63,S73,B3,B4,E5,E7,E9,H4 printed count `1`.
- `python3 -B tests/fixtures/r42-drift-conditions.py --tool <candidate> --work <existing scratch dir>`: `SUMMARY cases=13 pass=13 fail=0`, `EXIT=0`.
- `python3 -B tests/fixtures/r38-drift-write-envelope.py --tool <candidate> --work <existing scratch dir>`: `SUMMARY cases=12 pass=11 fail=1`, `EXIT=1`. The sole failure is `case-json-symlink-resolved=FAIL rc=2 resolved_written=False`, whose expected behavior conflicts directly with N10 refusal. All other cases, including docstring enum, pass. Initial attempt with nonexistent work dirs also failed; rerun used existing directories.
- Direct scratch symlink probe (link target absent): stderr `REFUSAL JSON-TARGET-SYMLINK: /fast/scratch/hyaku/souji-r43/R43executor05/probe/out.json names a symlink`; exit `2`.
- Verdict: candidate implements the requested N10 behavior and all 22 anchors remain unique. The legacy r38 symlink-resolution assertion is incompatible; the nine-fixture green criterion cannot be fully met without updating that obsolete expectation in the fixture (outside this assignment).
- No tools installed or updated.