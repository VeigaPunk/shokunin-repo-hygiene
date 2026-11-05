# S66ExecWriter — souji round 66 candidate writer (wave w1)

Verdict: candidate built, frozen C1 counter passes on the candidate, selftest passes 33/33, CANDIDATE-READY written.
No edits to tools/, census/, or any frozen file. Integration (copy to tools/, commit) is for L1.

## Artifacts (under .ufo/waves/round-66/w1/S66ExecWriter/)
- candidate/souji-receipt-write.py — candidate bytes, 1478 lines (base 1374).
- candidate/SHA256SUMS — `a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc  souji-receipt-write.py` (sha256sum -c: OK).
- candidate/c1-run.txt — frozen C1 counter stdout at the candidate commit; EXIT=0.
- candidate/selftest.txt — `python3 -B souji-receipt-write.py --selftest --work DIR` on the candidate; SELFTEST cases=33 pass=33 fail=0, rc 0.
- candidate/notes.md — changes by line, refusal classes and raise sites.
- CANDIDATE-READY — the sha256 above (written last).

## Build
- Scratch clone: /fast/scratch/hyaku/souji-r66/S66ExecWriter/clone (`git clone --shared`, checkout 045e103478fa4a7eff77db2cab5b9e2f26959a0a).
- Candidate commit in the clone: **6ec59b3aa5f07c95aa77b73a46a8bf750d356b48** (identity S66Seat, `-C` explicit). Candidate bytes equal the committed blob.
- Frozen counter run: `python3 -B census/round-66/c1-counter.py --root CLONE --matrix census/round-66/c1-matrix.tsv --base-rev 045e103478fa4a7eff77db2cab5b9e2f26959a0a --rev 6ec59b3aa5f07c95aa77b73a46a8bf750d356b48 --tool tools/souji-receipt-write.py --work /fast/scratch/hyaku/souji-r66/S66ExecWriter/work/c1`.
  Frozen counter and matrix were read only.

## Measured results
- C1 target line: `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`. Matches the frozen target.
- Base forgeries (8): E1, E2, E3, E4, E5, E6, MOD2, MOD3. Base honest 5; new honest 5.
- New refusal classes: E1/E2 RECEIPT-ENV-CONFIG-SET; E3 lane worktree is dirty; E4/E5/E6 RECEIPT-ENV-REDIRECT-SET; MOD2/MOD3 RECEIPT-STATE-CHANGED-DURING-RUN.
- Regress arm: base=PASS, new=PASS (both `SUMMARY cases=8 pass=8 fail=0`).
- Selftest: 33 cases (30 base + 3 new: case_31 env-config, case_32 env-redirect with GIT_INDEX_FILE value not echoed, case_33 setuid in-run flip). All 33 pass.

## Scope of changes (the six required items)
1. Env gate before the GIT_INDEX_FILE gate, before any git call: RECEIPT-ENV-CONFIG-SET (lines 293) and RECEIPT-ENV-REDIRECT-SET (line 298), presence-based, names only.
2. GIT_INDEX_FILE gate: block shape kept (line 304, refuse 305–306); message names the variable, value not echoed.
3. git() helper: GIT_DIR/GIT_WORK_TREE scrub and GIT_OPTIONAL_LOCKS kept; added `-c core.excludesFile=<devnull>`, GIT_CONFIG_GLOBAL=devnull, GIT_CONFIG_NOSYSTEM=1, GIT_NO_REPLACE_OBJECTS=1. All 11 receipt-path git calls go through git(); the only other `subprocess` git calls are in the selftest fixture harness.
4. _snapshot_entry mode mask 0o777 → 0o7777 (line 176); oct() format kept, so _delta_label still reports `mode`.
5. Docstring: round-65 "round 66 routes" wording replaced at line 49 and a round-66 paragraph added (lines 54–60); other lines unchanged.
6. Selftest: 3 new cases (31–33), no existing case changed.

## Named limits (not changed; per preregistration)
- Ignore routes (.git/info/exclude, tracked .gitignore, repo-local core.excludesFile) remain outside C1; the docstring says so.
- Presence-based env refusal (L3): an empty value still refuses; by design.

## Tooling / host
- No tools installed or upgraded. No pacman transactions. No sysctl changes. No writes outside the wave dir and the scratch dir.
- Writer selftest and counter both ran from the clone/work dirs under /fast/scratch/hyaku/souji-r66/S66ExecWriter/.

## Checks for L1 to run at integration
- Copy candidate/souji-receipt-write.py to tools/ at the integration commit and confirm sha256 a8c47d36…97fc.
- Re-run the frozen C1 counter at the landed revision (its tool slot will then be the landed commit), expecting the SUMMARY line above.
- Run `python3 -B tools/souji-receipt-write.py --selftest --work DIR` on the landed bytes (expect 33/33).
- C2 counter / M-ENV kill check are not owned by this seat; the candidate does not touch SKILL.md.
