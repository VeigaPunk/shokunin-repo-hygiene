# R41executor08 — C2 candidate tools/souji-freeze-check.py

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor08/souji-freeze-check.py
sha256 9cc2f0eee1a60fc004d1ee0abfb1c9885daf0c5f4487267a0864ea57d22ff0c0, 9558 bytes (`sha256sum`, `wc -c`).

## Design
- Reads the prereg blob at --rev via a persistent `git cat-file --batch` (never the work tree). Three git processes total: that batch (rev commit check, prereg blob, base commits, counter/population/control blobs at FREEZE-REV and at --rev), one `git log --full-history --no-renames --diff-filter=A --name-only` over PATH plus `.ufo/waves/round-<N>/` (gives FREEZE-REV = oldest add of PATH, and dispatch-file adds), one `git rev-list FREEZE` (ancestor set for BASE-NOT-ANCESTOR and DISPATCH-BEFORE-FREEZE).
- FROZEN-EDITED compares blob oids at --rev vs FREEZE-REV. A missing key line yields only FIELD-MISSING (downstream checks for that key skipped).
- Exit 2 + `REFUSAL COULD-NOT-EVALUATE: ...` on stderr for non-full40/unresolved --rev, absent PATH, no add commit. Stdlib only, no network, read-only (no writes into --root).
- Unspecified edges I chose: blank Base -> BASE-UNRESOLVED; Counter/Population value with no parsable `sha256=<64hex>` -> *-DIGEST; blank path -> *-MISSING; Round line absent -> dispatch check skipped.
- No tool installs.

## Command and output
```
cd /fast/scratch/hyaku/souji-r41/R41executor08 && bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41executor08 tools/souji-freeze-check.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor08/souji-freeze-check.py
```
All 21 `case-*=PASS` lines, then:
```
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=9cc2f0eee1a6
EXIT=0
```
Wall time of the whole scoring run: 9.67 s (21 cases + 42 stub-case runs + 2 real legs).

## Verdict
Target SUMMARY reached, exit 0, on the first scoring run. Scratch dir deleted. Not run: other counters; no edits to any tracked file.
