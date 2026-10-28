# R41executor02 — C3 candidate report

Candidate: `.ufo/waves/round-41/w1/R41executor02/r41-refusal-sites.py`
sha256 `bf403b2b5a75b72030847d44cdbc0fde3a7e2afff7f8d255c35cbbb7657b72c9`, 9714 bytes (`sha256sum`, `wc -c`).

## Command run (uid 1000, non-root)
```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41executor02 \
  tests/fixtures/r41-refusal-sites.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor02/r41-refusal-sites.py
```
Output (exit 0):
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01..S19 each "killed", failing set == mapped set (S02: P02a,P02b; S10: P10a,P10b; all others single probe), rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=bf403b2b5a75
EXIT=0
```
(All 19 SITE lines were printed `killed`; summarised here.)

## Design
- One function per probe id (P01 P02a P02b P03..P19), docstring names site S0x and trigger recipe.
- Each probe builds its trigger in `--work/r41-<ID>/{root,outside}` (recreated per run, removed after, perms restored), runs the tool with a minimal env (PATH, TMPDIR=probe dir), asserts rc==2 AND a stderr line starting with `REFUSAL <CLASS>:`.
- uid 0: prints error to stderr, exit 2 (not exercised; ran as uid 1000).
- P14 uses a hand-built bare gitdir (HEAD/objects/refs) outside root referenced by a `.git` file; no git invocation by the fixture. P16 writes nothing in the tool-pass path (refused before write). Stdlib only, no network.

## Sites not reached
None: 19/19 killed, 0 survived, 0 misattributed. Verdict: PASS (target SUMMARY met, exit 0). Scratch dir deleted. No tools installed.
