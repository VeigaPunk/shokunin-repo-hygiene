# R41executor12 — C2 candidate tools/souji-freeze-check.py

Candidate: `.ufo/waves/round-41/w1/R41executor12/souji-freeze-check.py`
sha256 `67924e50acec17fb16344c05ad30463b367c59a315ae1c120bed706bffe24c95`, 13231 bytes (stdlib only).

## Design
- Reads the prereg blob via `git cat-file blob REV:PATH`; never the work tree. FREEZE-REV = first line of `git log --no-renames --full-history --diff-filter=A --topo-order --reverse REV -- PATH`.
- Exit 2 refusal (stderr `REFUSAL COULD-NOT-EVALUATE: <why>`, empty stdout, no traceback): bad args, `--rev` not full40 lowercase / not a commit, `--root` not a dir or not the repo top level, shallow repo, PATH absent at REV, non-UTF-8 prereg, any git failure, any internal exception.
- Hermetic git: absolute git binary, `git --no-optional-locks --no-pager -C <root> -c protocol.allow=never ...`, env built from scratch (PATH, LC_ALL=C, GIT_CONFIG_NOSYSTEM/GLOBAL/SYSTEM nulled, GIT_OPTIONAL_LOCKS=0, GIT_NO_REPLACE_OBJECTS=1, GIT_TERMINAL_PROMPT=0), stdin closed, only read-only subcommands (cat-file, log, rev-list, rev-parse, merge-base).
- DISPATCH-BEFORE-FREEZE: every `*-dispatch.json`/`*.ready` ever added under `.ufo/waves/round-<N>/` whose add commit is FREEZE-REV or its ancestor (one finding per file, label C0).

## Commands run and output
```
bash census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41executor12 tools/souji-freeze-check.py=<candidate>
```
All 21 `case-*=PASS`; `real ok rc=0 findings=0 summary=(3, 0)`; `retro red rc=1 findings=18 summary=(3, 18)`;
`SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=67924e50acec`
Exit code: 0 (final candidate bytes, as hashed above).

Extra probes against the lane tip e2a74312af4233963e44e4dbb38838ece07b8bd2 (no lane writes):
- `GIT_DIR=/nonexistent GIT_WORK_TREE=/x GIT_INDEX_FILE=/x python3 -B tool --root LANE --prereg census/round-41/preregistration.txt --rev e2a7…` -> `SUMMARY claims=3 findings=0`, rc=0 (inherited GIT_* ignored).
- `--rev abc` -> rc=2 REFUSAL (full40); absent prereg `nope` -> rc=2 REFUSAL; `--root /nonexistent` -> rc=2; missing args -> rc=2 REFUSAL (argparse routed to refusal).

## Verdict
Target SUMMARY reached, exit 0. Not measured by L1; seat score is advice. Scratch `/fast/scratch/hyaku/souji-r41/R41executor12` removed at yield.
Tools installed: none.
