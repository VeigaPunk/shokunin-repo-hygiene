# R41executor06 — C3 candidate (coverage)

Candidate: `.ufo/waves/round-41/w1/R41executor06/r41-refusal-sites.py` (destination `tests/fixtures/r41-refusal-sites.py`)
- sha256 `86659db9b037e5864dff0b7dcefe64b3bc600295fd36c98c9afbfa3c1490b966`, 11321 bytes. Stdlib only, uid 1000.

## Commands and output
```
bash census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41executor06 \
  tests/fixtures/r41-refusal-sites.py=<abs>/.ufo/waves/round-41/w1/R41executor06/r41-refusal-sites.py
```
Output (exit 0):
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01..S19: all `killed`, failing set == mapped set (S02 P02a,P02b; S10 P10a,P10b; others one probe each), mutant rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=86659db9b037
EXIT=0
```
Hermeticity check: ran the fixture directly against the pinned tool with `GIT_DIR=/nonexistent GIT_WORK_TREE=/x` exported:
`SUMMARY probes=21 pass=21 fail=0`, rc=0; `--work` dir was empty afterwards (scratch tree removed in `finally`, chmod-000/0555 entries restored first).

## Design
- Each probe builds its own tree under `<work>/r41-refusal.*/<PID>/{root,out}`, runs the tool with a whitelisted env (PATH, HOME/TMPDIR=work, LC_ALL=C, GIT_CONFIG_NOSYSTEM/GLOBAL/SYSTEM neutralised, GIT_TERMINAL_PROMPT=0), 60 s timeout, stdin /dev/null.
- Assertion: rc == 2 AND exactly one stderr line starting `REFUSAL ` containing `REFUSAL <CLASS>:`.
- Triggers: ENOENT; chmod 000 (EACCES); symlink loop (ELOOP); directory record; duplicate row; garbage line; comment-only; three TOTAL mismatches each isolating one field; FIFO (ENXIO) and directory (EISDIR) as --json; /dev/null as --json (S_ISCHR checked first); --root a file; row `../sibling`; in-root `.git` file to a real outside gitdir (git init under work); --json == --record; --json under a measured git repo; two-link outside file; 0555 dir; --timeout 0.
- euid 0: prints error on stderr, exit 2 (no skip). Exit 1 when any probe fails (counter requires rc=1 on mutants).

## Unreached sites
None: 19/19 killed. No defect found in frozen files.

## Verdict
Target met: `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`, exit 0. Scratch `/fast/scratch/hyaku/souji-r41/R41executor06` to be removed on yield.
