# R41executor03 — C3 candidate fixture (coverage)

Candidate: `.ufo/waves/round-41/w1/R41executor03/r41-refusal-sites.py`
- sha256 `1020e5f28eb34af728a31f5b4e2cc1dc003b274f18cb53c505c12593913e3ed9`, 10166 bytes (`sha256sum`, `wc -c`; euid 1000).
- Python stdlib only, self-contained, 21 probes (P01 P02a P02b P03..P09 P10a P10b P11..P19). Each probe builds its own trigger under a `mkdtemp` inside `--work` and runs the tool. It asserts rc==2 AND the exact stderr token `REFUSAL <CLASS>:`. Probes that touch the file's contents (P17) also assert the hardlinked target is unmodified. euid 0 prints an error on stderr and exits 2 (no skip). The work dir is chmod-restored and removed on exit.
- Trigger notes: a ghost REPO row (ABSENT drift, no git) carries the `--json` probes P10a..P18 and the parse probes. P14 is the only probe that needs git: it runs `git init` in an outside dir and points `root/r/.git` at it.

## Command run (exact)
`cd /fast/scratch/hyaku/souji-r41/R41executor03 && bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41executor03 tests/fixtures/r41-refusal-sites.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor03/r41-refusal-sites.py`

Output (observed, EXIT=0, 22 s):
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 RECORD-MALFORMED killed failing=P01 mapped=P01 rc=1
SITE S02 RECORD-MISSING killed failing=P02a,P02b mapped=P02a,P02b rc=1
SITE S03 RECORD-MALFORMED killed failing=P03 mapped=P03 rc=1
SITE S04 RECORD-MALFORMED killed failing=P04 mapped=P04 rc=1
SITE S05 RECORD-MALFORMED killed failing=P05 mapped=P05 rc=1
SITE S06 RECORD-EMPTY killed failing=P06 mapped=P06 rc=1
SITE S07 RECORD-MALFORMED killed failing=P07 mapped=P07 rc=1
SITE S08 RECORD-MALFORMED killed failing=P08 mapped=P08 rc=1
SITE S09 RECORD-MALFORMED killed failing=P09 mapped=P09 rc=1
SITE S10 JSON-NOT-REGULAR killed failing=P10a,P10b mapped=P10a,P10b rc=1
SITE S11 JSON-NOT-REGULAR killed failing=P11 mapped=P11 rc=1
SITE S12 USAGE killed failing=P12 mapped=P12 rc=1
SITE S13 RECORD-OUTSIDE-ROOT killed failing=P13 mapped=P13 rc=1
SITE S14 RECORD-OUTSIDE-ROOT killed failing=P14 mapped=P14 rc=1
SITE S15 JSON-IS-RECORD killed failing=P15 mapped=P15 rc=1
SITE S16 JSON-INSIDE-MEASURED-TREE killed failing=P16 mapped=P16 rc=1
SITE S17 JSON-HARDLINKED killed failing=P17 mapped=P17 rc=1
SITE S18 JSON-UNWRITABLE killed failing=P18 mapped=P18 rc=1
SITE S19 USAGE killed failing=P19 mapped=P19 rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=1020e5f28eb3
```
Final SUMMARY exit code: 0.

## Sites not reached
None: 19/19 killed, 0 survived, 0 misattributed.

## Notes
- No frozen file was edited; no tool installs. Scratch `/fast/scratch/hyaku/souji-r41/R41executor03` deleted after the run.
- Not exercised: only the score-candidate run above (single run, run once). The one-time run is reproducible but not repeated for flakiness.

## Verdict
Candidate reaches the C3 target in the scratch-clone scoring: PASS (advice, not the L1 measurement).
