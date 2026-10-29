# R42executor01 — C2 candidate (minimal diff against the r41 tool)

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42executor01/cand.py
sha256 and bytes: see `sha256sum`/`wc -c` output below (recorded at write time).

Changes against the base tool (structure kept): `parse_claims` returns (claims, extra) and emits KEY-DUPLICATE (one per duplicated key, no first-wins) and HEADING-MALFORMED (`line=<n>`, C0, opens no claim, ends the current block); `HEADER` now requires a space or end of line after `## C<digits>`; `Repo.is_symlink` (git `ls-tree -z`, mode 120000) drives COUNTER-SYMLINK / POPULATION-SYMLINK alone in `check_path_sha`; the dispatch filter matches basename containing `-dispatch` or `.ready`, or ending `-spec.json`/`-results.json`; `main` body moved to `check()`; `--selftest` added. r41 hardening (whitelisted git env, core.quotePath=false, log.mailmap=false, CRLF, spaces, NUL) untouched.

Self-test: 22 cases (21 synthetic repos + unresolved-rev refusal), each repo built under $TMPDIR with `-C`, identity via env, root asserted; runs `check()` in-process, so the tool's own `hashlib.sha256`, `git log --diff-filter` and `git merge-base --is-ancestor` calls execute. Expected digests are literals (not recomputed) so a reversed digest cannot cancel itself. No counter text was read for names (only census/round-42/c2-cases.tsv and the c2-counter.py docstring).

## Commands and output
```
TMPDIR=<scratch> python3 -B cand.py --selftest
SELFTEST cases=22 pass=22 fail=0        (exit 0)

bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42executor01 tools/souji-freeze-check.py=<seat>/cand.py
case-* 37 lines all PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest ok rc=0 summary=(22, 22, 0)
SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=f32b4eba4bbf
exit code 0
```
Verdict: target SUMMARY reached, exit 0. Scratch dir deleted. No tools installed.
sha256: f32b4eba4bbf904de62a080e7e4a32f6830cbd1770237c0fc5ecb630830dd82d  cand.py
bytes: 19728 cand.py
