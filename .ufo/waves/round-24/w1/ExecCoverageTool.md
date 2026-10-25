# ExecCoverageTool — r24 w1, C2 tool draft

## Status
STATUS: PASS — the draft follows the frozen C2 CLI, counts line, mismatch classes and exit codes. It is stdlib-only, 160 lines, and reads committed bytes only. The control preview at base gives `mismatches=2` with exit 1.

## Evidence
Delivery: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/w1/souji-coverage-agreement.py`
sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`, 160 lines. Host: git 2.56.0, Python 3.14.8.

Control preview (lane READ-ONLY, cwd /var/tmp):
```
$ python3 -B .ufo/waves/round-24/w1/souji-coverage-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev a65fac98964b445758e94c805728c9a19d302ff8
MISMATCH	MISSING-FROM-MAP	corpus/knowledge/count-objects-garbage-readings-r25.md	ground=F2 map_rows_F2=3
MISMATCH	MISSING-FROM-MAP	corpus/knowledge/repo-size-census-readonly.md	ground=F2 map_rows_F2=3
grounded=4 mapped=2 dangling=0 mismatches=2
exit=1
```
At lane commit f9db2181647d91470a724a12d626bd6106805076 the output is byte-identical (same 2 rows, same counts, exit 1).

Hand cross-check at base: `grep -nE '^ground:'` over `git show <base>:corpus/knowledge/*.md` returns 4 lines: F2 count-objects-garbage-readings-r25.md:5, F4 quarantine-origin-record-fields-r24.md:7, F4 quarantine-staging-no-copy-r23.md:6, F2 repo-size-census-readonly.md:6. Both F4 entries are named in the entries cell of README.md:41. Three rows carry the F2 token: README.md:40 (entries `—`), :68 (entries `knowledge/git-repo-structure-readonly.md` plus tool and fixture paths) and :216 ("F2 caveat", entries are lane-report paths). None of their entries cells names either F2 entry, which matches the tool's output.

Refusals (all exit 2, message on stderr): `--rev a65fac9`, `--rev HEAD`, `--rev 0000…0000` (40-hex, not a commit), a 41-character rev, `--root /var/tmp` (not a repository), a missing `--rev`, and an extra `--lost-found` argument. An uppercase 40-hex base rev is accepted and gives identical counts.

Synthetic falsifier (scratch `/var/tmp/souji-r24-ExecCoverageTool/`, removed; the final `ls -d` reports "No such file or directory"):
- c1 → `grounded=4 mapped=1 dangling=1 mismatches=4`, exit 1. It covers:
  - a `../knowledge/a.md` span in an `F2-sub` row (mapped);
  - an escaped `\|` in the status cell (columns not shifted);
  - `knowledge/gone.md` written twice in one cell (dangling counted once);
  - `b.md` named only under an `F31` row and in prose without backticks (MISSING);
  - a table whose `entries` header is the 2nd cell (not a map, so F6 and F7 are MISSING);
  - a `ground:` line after the `# ` heading (ignored);
  - `ground:F5` with no space (counted);
  - an `ENTRIES / evidence` header (matched case-insensitively).
- c1 re-run after deleting `a.md` and appending a map row in the working tree: byte-identical output, so the working tree is not read.
- c2: d.md's F5 is unmapped → mismatches=1, exit 1. Once every ground is mapped, c3 gives `grounded=4 mapped=4 dangling=0 mismatches=0`, exit 0.

No tools installed. No `__pycache__` was created under w1.

## Findings
1. Base control: X=2, and both mismatches are F2. The C2 after-state therefore needs `count-objects-garbage-readings-r25.md` and `repo-size-census-readonly.md` in the entries cell of an F2 row. Today README.md:68 names them only in its status cell, which the tool does not read. C1's new F2 entry must be added there too (preregistration lines 120-121). For the kill rule, grounded(base) is 4.
2. Lane state, not mine: `tools/souji-coverage-agreement.py` exists untracked in the lane (mtime 06:22:22 -0300, sha256 `629fbd4a…`). It is an intermediate copy of this draft and differs at line 25 only: it has `[0-9a-f]{40}` where the final draft has `[0-9a-fA-F]{40}`. The L1 should re-copy the w1 file. I did not touch the lane copy.
3. Interpretation chosen, flagged here: an entry counts as mapped only when its basename equals the `<name>` of a backticked `knowledge/<name>` span in an F<k> row's entries cell. The contract text is looser (preregistration.txt:82-84): "whose basename appears in NO entries-column cell". At base both readings give X=2, because neither F2 basename appears anywhere in an F2 entries cell.
4. Per-entry semantics: an entry with several `ground:` lines is mapped only when every F<k> is mapped, and each unmapped k is its own MISMATCH row. DANGLING is counted once per README line and name.
5. Strict token: `F2.`, `F2:`, `**F2**` and `F2,` do not carry the token, so such a row is not an F2 row. This follows "F<k> followed by a space, `-`, or end of cell".

6. Cross-run with the fixture seat: `python3 -B .ufo/waves/round-24/w1/r24-coverage-agreement.py --tool .ufo/waves/round-24/w1/souji-coverage-agreement.py` (cwd /var/tmp) printed `cases=9 pass=9 control=FALSE-GREEN-REJECTED`, exit 0, and left no `/var/tmp/souji-r24-coverage-*` behind. The always-zero control failed all 9 cases.

## Attack log
- A1 (calibration limit, not gameable toward a false 0 on the classes above): "mapped" is a membership test only. An F2 row whose status cell says "not admitted" still maps an entry listed in its entries cell. C2 measures agreement between map and entries, not status truthfulness.
- A2 (narrowing risk): a row's ground cell rewritten from `F2 …` to `**F2** …` would leave that row with no F2 token. The result is more MISSING rows, never fewer, so the change cannot reach 0 by hiding rows. Deleting a `ground:` line would lower X, but the kill rule grounded(tip) ≥ grounded(base)=4 catches that.
- A3 (the fixture seat should test): an always-zero emitter is rejected by any case with X>0. The synthetic c1 shape above (mismatches=4) is a cheap discriminating case.
