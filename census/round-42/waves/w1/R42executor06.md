# R42executor06 — C2 candidate tools/souji-freeze-check.py

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42executor06/souji-freeze-check.py
Bytes: 18550 (r41 base tool: 10397). sha256: 9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6

Changes over r41: HEADER now `## C<digits>` + space/EOL; BADHEAD regex -> HEADING-MALFORMED (line=<n>, closes the open block, opens none);
parse_claims returns per-claim duplicate-key sets -> KEY-DUPLICATE per key (dup keys then not evaluated, no FIELD-MISSING/EMPTY for them);
check_path_sha runs `git ls-tree -z --full-tree FREEZE -- normpath(path)` after the blob exists and emits COUNTER-/POPULATION-SYMLINK (mode 120000), no digest compare;
dispatch name test widened (`-dispatch`, `.ready` substrings; `-spec.json`, `-results.json` suffixes); r41 whitelisted env/quotePath/mailmap/NUL handling untouched.
`--selftest`: 31 in-process cases (calls main() over synthetic repos built under tempfile.mkdtemp() i.e. $TMPDIR; every git call names -C, identity via env,
fixture digests are literals so a patched sha256 cannot agree with itself; tool's own subprocess.run git log --diff-filter / merge-base paths exercised); no special-casing of counter names.

Commands run (seat scratch /fast/scratch/hyaku/souji-r42/R42executor06, TMPDIR passed explicitly):
1. `TMPDIR=... python3 -B souji-freeze-check.py --selftest` -> `SELFTEST cases=31 pass=31 fail=0`, rc=0
2. `bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42executor06 tools/souji-freeze-check.py=<candidate>`; final run output (rc=0):
   - all 37 `case-*=PASS`; `real ok rc=0 findings=0 summary=(3, 0)`; `retro red rc=1 findings=19`; `retro_clean ok rc=0 findings=0`; `selftest ok rc=0 summary=(31, 31, 0)`
   - `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb`
   - exit code 0 (target met exactly)
Decisions where the spec was silent: a malformed heading ends the preceding claim block (like any `## ` line); duplicate keys are reported only (first-wins reading dropped); symlink check normalises path with posixpath.normpath so `./c.py` cannot dodge it.
Limits: symlinked parent directories are not detected (git cannot traverse them -> path reads as MISSING); sed/golf not applied beyond docstring condensing (size is dominated by the 31-case self-test).
Tools installed: none. Counter CASES/SITECUSTOMIZE not read. Verdict: PASS at target.
