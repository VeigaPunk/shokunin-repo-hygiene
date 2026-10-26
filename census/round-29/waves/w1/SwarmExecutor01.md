# SwarmExecutor01 — C1 instrument fixture (r29 w1)

## Status
STATUS: PASS — runnable fixture for `tools/souji-registry-agreement.py` builds 12 scratch-repo cases, passes 12/12 against the committed tool, rejects the always-zero emitter control, and goes red (9/12) against a scratch copy with the entry→row reverse check deleted.

## Evidence
Tool untouched: `sha256sum tools/souji-registry-agreement.py` = `51131fe74faa95a1488ad6957d90b272a22c52171c257d9b97bb27c305b09801`; `git status --porcelain tools/` empty. Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, prereg `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

1. Base measurement of the instrument (context for the fixture's expectations):
```
$ python3 -B tools/souji-registry-agreement.py --root . --rev 691dd29... --list-rev b8cb4b3...
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
... (4 more K1) ...
K2 uncorrected LOG.md:1758
K2 uncorrected SCORECARD.md:23
K2 uncorrected corpus/lessons/round-28.md:22
K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29...
rc=1
```
Also observed: at base without `--list-rev` the instrument returns `rc=2 COULD-NOT-EVALUATE stale list <rev>:census/round-29/stale-statements.tsv unreadable` (the TSV lives only in the prereg commit), so the fixture always passes `--list-rev <full40>`.

2. Fixture against the committed tool (delivery path, scratch repos under `/var/tmp/souji-r29-C1Fixture/`):
```
$ cd /var/tmp && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-r29-registry-agreement-fixture.py
cases=12 pass=12 control=FALSE-GREEN-REJECTED
rc=0
```

3. Red-before, scratch copy with the reverse check deleted (`/var/tmp/souji-r29-C1Fixture/red-before/broken-tool.py`, the `for i in sorted(ids):` block in `k1` replaced by `del ids`):
```
$ python3 -B .../deliver-r29-registry-agreement-fixture.py --tool /var/tmp/souji-r29-C1Fixture/red-before/broken-tool.py
FAIL cited-not-in-used-by: rc=0 summary=(0, 0, 0) lines=[] stderr=
FAIL cited-no-row: rc=0 summary=(0, 0, 0) lines=[] stderr=
FAIL indent-4-ignored: rc=0 summary=(0, 0, 0) lines=[] stderr=
cases=12 pass=9 control=FALSE-GREEN-REJECTED
rc=1
```

4. Fixture file: 291 lines, `python3 -B -c "ast.parse(...)"` → `ast-ok`; sha256 `eea7388922b1d98bdd40e6156bed9e7c2d0b7b6d066f4c77adcbe4cf065ad062`.

5. Scratch `/var/tmp/souji-r29-C1Fixture/` removed; no `__pycache__` created (all runs `python3 -B`). No tool installs or upgrades were made; host `pacman` untouched.

## Findings
1. Case semantics implemented as exact verdict-line sets + exit code + `SUMMARY k1/k2/mismatches`, each case a fresh `git init` repo with a single commit and the stale list committed under `census/round-29/stale-statements.tsv`, supplied via `--list-rev <rev> --stale-list <path>` (every `git` call is `-C <scratch repo>`; identity configured per scratch repo only).
2. The instrument has no `--tool` option and must not gain one; `--tool` is the fixture's own flag selecting the binary under test. The control therefore runs this fixture as a child with `--tool <always-zero emitter>` (`--no-control` stops recursion) and demands rc≠0 plus a `FAIL` line for every case that expects a nonzero verdict (`NEGATIVES` = 11 of 12; only `consistent` is emitter-satisfiable). A fixture bug that let the emitter through prints `CONTROL FALSE GREEN tolerated by: …` and exits 1.
3. Case 6 is non-vacuous in both directions: a 3-space row whose `used-by` file names its id yields 0 mismatches, but if the row were ignored the entry's `source: S008` would surface as `cited-no-row`. Case 7 pins the 4-space (indented-code) boundary: the ignored row's nonexistent `used-by` path must NOT be reported, while its citer must produce exactly `K1 cited-no-row`.
4. Case 12 pins K2 marker ordering: a `R29-CORRECTION LOG.md:3` line placed before line 3 must not satisfy the append-only rule (`lines[ln:]`), so the verdict stays `uncorrected`.
5. Case 11 pins the rev gate: `deadbeef` exits 2 with `COULD-NOT-EVALUATE` on stderr and no `SUMMARY` on stdout.
6. `indent-4-ignored` failing under the broken copy is expected collateral: the ignored row's citer can only be caught by the reverse check, so deleting that check also blinds the grammar-boundary case. The reverse check is exercised directly by cases 4 and 5.
7. Landability notice: `git check-ignore -v` reports `.gitignore:1:.ufo/waves/` for the delivery file, so round-29 wave bytes are untracked and exist on disk only until the L1 copies/lands them. Unrelated: `git status --porcelain` also shows `M .ufo/waves/round-26/w1/ScribeGateDraft.md` (tracked from an earlier round), a sibling's change I did not touch.

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-r29-registry-agreement-fixture.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmExecutor01.md` (this report)
