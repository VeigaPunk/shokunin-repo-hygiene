# R41executor01 — C3 candidate fixture

Candidate: `.ufo/waves/round-41/w1/R41executor01/r41-refusal-sites.py`
sha256 `8bf040106df7efdb20673dc39d1f60565163ff9415a5ad3e5e7c0f3153770167`, 6859 bytes. Python stdlib only; euid 0 -> stderr message, exit 2.

Design: 21 table-driven probes (one small function each). Each builds its trigger in its own dir under a `mkdtemp` inside `--work`, runs
`python3 -B TOOL --root --record ...`, and passes only if rc==2 AND stderr contains `REFUSAL <CLASS>:`. Cleanup restores dir modes then rmtree.
Triggers per c3-sites.tsv: ENOENT, chmod 000 (P02a), self-symlink loop (P02b), dir record, dup row, junk line, comments only, three TOTAL mismatches
(each only one field wrong), FIFO no reader / directory / /dev/null as --json, --root a file, `../sibling` row, `.git` file -> outside git-init'd repo,
--json == record, --json under a git-init'd repo in root, hardlinked outside file, 0555 outside dir, `--timeout 0`.

Command run (uid 1000):
`bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41executor01 tests/fixtures/r41-refusal-sites.py=<candidate>`

Output: `PRISTINE ok rc=0 probes=21 ...`, all 19 `SITE Sxx ... killed failing==mapped` (S02 P02a,P02b; S10 P10a,P10b).
SUMMARY (verbatim): `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=8bf040106df7`
Exit code: 0.

Unreachable sites: none. Limits: P02a/P18 are skipped-by-refusal under uid 0 (exit 2, by design); P11 opens /dev/null for write (no truncate), outside --work but writes nothing.
Scratch `/fast/scratch/hyaku/souji-r41/R41executor01` deleted. No tools installed. Verdict: target met.
