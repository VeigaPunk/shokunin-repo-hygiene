# R41executor04 — C3 candidate report

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor04/r41-refusal-sites.py
sha256 f32022e28fe2293af44d7fee1cb73f9a39221fbcc534022b78d77a8c96551978, 3725 bytes. Stdlib only, no network, writes only under a mkdtemp dir inside --work (removed in finally; chmod restored first). euid 0 -> stderr message, exit 2.

Design: one shared scratch fleet per run (empty-ish root, outside record/json files); 21 probes each invoke `python3 -B TOOL --root R --record REC --skip-unrecorded [extra]` and assert rc==2 AND `REFUSAL <CLASS>:` in stderr. Triggers per c3-sites.tsv (ENOENT, chmod 000, ELOOP symlink, dir record, dup, junk, comments-only, TOTAL repos/regs/prunable, FIFO, dir, /dev/null json, file as root, ../sib, .git file -> outside gitdir (hand-built minimal gitdir, no git init), json==record, json under root, hardlink, chmod 500 dir, --timeout 0). No git writes, no jj.

Command run (cwd /fast/scratch/hyaku/souji-r41/R41executor04):
bash census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41executor04 tests/fixtures/r41-refusal-sites.py=<candidate>
Output: PRISTINE ok rc=0 probes=21; SITE S01..S19 all `killed` with failing == mapped (S02 P02a,P02b; S10 P10a,P10b).
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2
Exit code: 0. Wall time 19.6 s.

Unreachable sites: none. Tooling installed: none. Scratch dir deleted.
Verdict: target met on first run (seat score is advice; L1 measures).
