## Status
STATUS: PASS — the frozen C2 counter was run over every lane revision that can hold a wave manifest (both commits touching `census/round-2{6,7,8}/waves`, plus the pre-capture boundary, the r28 tip, the lane base and the prereg tip); r26 fails 152/14 from the first commit that commits an r26 manifest onward, r27 and r28 never fail, and the requested escape-deletion experiment shows the two GNU-escaped records contribute 0 of the 152 failures.

## Evidence

Instrument: `census/round-29/c2-counter.py`, blob `4c97d202fcdf0f71c223cfae18ef9f94a1e7e4ac` at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; the file does not exist at any earlier revision (`git rev-parse --verify --quiet <rev>:census/round-29/c2-counter.py` fails for all revs before b8cb4b3), so "run it at that revision" is the frozen instrument at the prereg commit applied with `--rev <historical rev>`. It reads only `git ls-tree`/`cat-file`, never the working tree.

Commits touching the three wave dirs (the mandated set) — exactly two:
```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%H -- census/round-26/waves census/round-27/waves census/round-28/waves
ed270c42161cd62829783a5e5d2ef4e27089331c
765fe8bd602ac679d01e7a0790711485209ab8bd
```

Full tabulation is delivered as `.ufo/waves/round-29/w1/deliver-c2-history.tsv` (9 rows: 7 lane revisions + 2 labelled scratch rows). Key rows:

| rev | manifests | r26 rec/fail/uncovered | r27 rec/fail/uncovered | r28 rec/fail/uncovered | total failed/uncovered | floor_violations | rc |
|---|---|---|---|---|---|---|---|
| 0c96332 (parent of capture) | 0 | – | – | – | 0/0 | 3 | 1 |
| 765fe8b | 2 | 1382/152/14 | 124/0/0 | – | 152/14 | 1 | 1 |
| ed270c4 | 3 | 1382/152/14 | 124/0/0 | 75/0/0 | 152/14 | 0 | 1 |
| de478b4, fec846d, 691dd29 (base), b8cb4b3 (tip) | 3 | 1382/152/14 | 124/0/0 | 75/0/0 | 152/14 | 0 | 1 |

Excerpts at the two anchors:
```
$ python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e   (rc=1)
```
```
$ python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 765fe8bd602ac679d01e7a0790711485209ab8bd
SUMMARY manifests=2 failed=152 uncovered=14 floor_violations=1 rev=765fe8bd602ac679d01e7a0790711485209ab8bd   (rc=1)
```
Base and tip are byte-identical in outcome, so the r26 failure is not a round-29 regression: it arrived with the receipt.

First revision at which r26 failed = 152: `765fe8bd602ac679d01e7a0790711485209ab8bd`, the only commit that changed the r26 wave tree (`git rev-list --count 765fe8b -- census/round-26/waves` → 1; the parent `0c96332` has `census/round-26` without `waves`). The r26 manifest blob `11be6bc1947c1edca5700c94d75a7a1433044909` is identical at 765fe8b, ed270c4, 691dd29 and b8cb4b3, so later commits changed nothing about the r26 bytes.

What 765fe8b changed (`git diff-tree --no-commit-id --name-status -r 765fe8b -- census/round-26/waves`): 1245 files added; `-- census/round-27/waves`: 125 added; whole commit 1398 files, 312638 insertions, 5 deletions; new lane-root `.gitignore`:
```
$ git show 765fe8b -- .gitignore   →   +.ufo/waves/  +census/operator-sweep-*/  +__pycache__/
```
That same commit also added `tools/souji-wave-evidence-capture.sh` (blob `c63a9f0ccf78702cdb44d5d916c40e00e3613503`, unchanged through HEAD). The tool records a disk inventory, not a git inventory — `tools/souji-wave-evidence-capture.sh:9` says `manifest.sha256 - sha256 of every captured regular file (paths as listed`, and `:8` says `Copies <lane>/.ufo/waves/round-<N>/ (byte-exact file contents) into`; the hash set is built at `:157` from `find . -type f` over the copied receipt. Manifest records therefore include files git can never store, and the commit that added the ignore lines skipped them at `git add` time.

Composition of the 152 (committed r26 manifest at 691dd29, records whose path is absent from the committed tree; 0 hash mismatches, 0 symlink records, 0 unparseable records):
- 126 = `.git` internals under `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/fixture/{a1,a2,a4,a5,b,c,control}/.git/` (parent `vadv-49/.gitignore:1:fixture/`);
- 20 = nested-`.gitignore` content: `case-V6` 6 (`case-V6/.gitignore:4,5,6` — `/src/`, `/vault/`, `/ledger*.tsv`) and `vadv-49` 14 (12 under `fixture/`, 2 under `shims/`; `vadv-49/.gitignore:1,2`);
- 4 = `__pycache__/*.pyc` (root `.gitignore:3:__pycache__/`);
- 2 = `.scratch/*.tmp` under `case-F7`/`case-F8` repo-trees (`…/.scratch/.gitignore:1:*`).
All 152 paths still exist untracked in the lane working tree (152/152 `os.path.lexists`), which is why the capture saw them.

Attribution checked against the receipt paths, not the `.ufo` source:
```
$ git -C … check-ignore -v --no-index -- census/round-26/waves/assimilation/validate/tests/vault/case-V6/ledger.tsv
census/round-26/waves/assimilation/validate/tests/vault/case-V6/.gitignore:6:/ledger*.tsv
$ … -- …/vadv-49/fixture/a1/.git/HEAD
census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:1:fixture/
$ … -- …/fixtures/__pycache__/r26-axis-check.cpython-314.pyc
.gitignore:3:__pycache__/
$ … -- …/case-F7/repo-tree/.scratch/stale-probe-f7.tmp
census/round-26/waves/assimilation/validate/tests/fixtures/case-F7/repo-tree/.scratch/.gitignore:1:*
```

Escape experiment (scratch clone, never the lane): `D=$(mktemp -d /var/tmp/souji-r29-HistoryC2Sweep.XXXXXX)`, `git clone -q --no-local` the lane into `$D/c` (`git -C "$D/c" rev-parse --show-toplevel` → `$D/c`), control run at b8cb4b3 reproduced 152/14, then a Python rewrite of `census/round-26/waves/manifest.sha256` dropped the two backslash-prefixed records and committed in scratch (`def022337084e370dffb117acc47d2a10bed6182`):
```
r26 records=1380 failed=152 uncovered=14→16 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=16 floor_violations=0
```
The two escaped records are `./assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md` (manifest `1009b12c…`) and `…/r/scratch/.scratch/old\nname.log` (`ae599d14…`); both are committed (`git ls-tree 691dd29 -- …/vadv54-run/r` shows mode 100644, blobs `65407a80…`, `13281d81…`) and both committed-blob sha256 values equal the manifest records exactly. Deleting the records leaves `failed` at 152 and raises `uncovered` 14→16 (the two committed newline-named files lose their only record), i.e. escape decoding contributes exactly zero failures and is load-bearing for coverage.

Floor arithmetic: committed entries under `census/round-26/waves` at 691dd29 = 1245 (incl. `manifest.sha256`), of which 14 are symlinks (mode 120000) → 1230 regular files = `FLOORS['26']` (`c2-counter.py:23`) and `1382 − 152 = 1230`, so the over-recorded 152 consume exactly the whole floor tolerance and a manifest cannot be made green by also dropping real records.

## Findings
1. The r26 wave receipt was born failing. First failing revision `765fe8b` (author 2026-10-25T15:43:53-03:00, committer 16:01:00-03:00 — this lane's history is a re-commit chain in which each commit's committer time equals the next commit's author time); every later revision, including the r29 lane base `691dd29` and prereg tip `b8cb4b3`, reports `r26 records=1382 failed=152 uncovered=14 floor_violation=0` and rc=1. Location: `census/round-26/waves/manifest.sha256` (blob `11be6bc1…`), unchanged since introduction.
2. Cause is instrument design, not byte drift: `tools/souji-wave-evidence-capture.sh:157` builds the manifest from `find . -type f` over the copied receipt, so untracked/untrackable names enter the record set, while the receipt is committed through git's ignore-aware index. Location: `tools/souji-wave-evidence-capture.sh:8-12`, `:157`, `:185-189`.
3. The commit that introduced the receipt also introduced the ignore rules that make 6 of its own records uncommittable: root `.gitignore` lines `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/` were added in `765fe8b` together with the 1245-file r26 capture. Location: `.gitignore:1-3`, `git show 765fe8b -- .gitignore`.
4. Two distinct commit-blocking mechanisms, both reproduced: 126 `.git/` internals are uncommittable because their parent directory is ignored by `vadv-49/.gitignore:1:fixture/` (git never descends, so the embedded-repo rule is not even reached); 20 are ignored by case-local `.gitignore` files that were themselves copied into the receipt and committed (`case-V6/.gitignore:2,3,6`, `vadv-49/.gitignore:1,2`); 4 by the root `__pycache__/`; 2 by `…/.scratch/.gitignore:1:*`. All 152 are "absent", none hash-mismatched.
5. The 14 uncovered are exactly the committed symlinks under `census/round-26/waves/assimilation/validate/{tests,tools}/` (e.g. `vault/mock-cli/obsidian-cli`, `vadv54-run/q/led-chain.tsv`, `tools/impl-21.sh`), mode 120000, and `census/round-26/waves/symlinks.tsv` has never existed in lane history (`git log --all -- 'census/round-26/waves/symlinks.tsv'` → empty), so nothing can account for them. The capture tool copies symlinks but hashes only regular files (`:157`), which is why no such file was ever produced.
6. Escape decoding is correct and irrelevant to the 152: both backslash-prefixed records verify against committed blobs; deleting them keeps `failed=152` and pushes `uncovered` to 16. The counter's `esc = l.startswith('\\')` branch (`c2-counter.py:53`) parses GNU-format records as intended.
7. Instrument property at historical revisions (not a defect at the frozen target): the floor arm `missing = [r for r in FLOORS if … not in mans]` (`c2-counter.py:95`) is revision-blind, so `765fe8b` reports `floor_violations=1` merely because the r28 manifest did not exist yet; at `691dd29`/`b8cb4b3` it is 0 and the prereg target is unaffected. Recorded, no amendment proposed (contract frozen).
8. Calibration cross-check, corrected: `FLOORS['26']=1230` equals the committed regular-file count under `census/round-26/waves` at base (1244 non-manifest entries − 14 symlinks), and `FLOORS['27']=124` / `FLOORS['28']=75` equal theirs (125−1, 76−1), so the floors are derivable from committed bytes. The record-level slack for *recorded* content is zero (`1382 − 152 = 1230`, and the comparison is `<`, so equality passes). My earlier "zero slack" reading was nonetheless wrong at tree level: `uncovered` is computed over the committed tree, so the 14 committed symlinks — which no record can ever cover, since a record whose tree entry is mode 120000 is scored failed — can simply be deleted. See finding 11.
9. Sibling deliverable reconciled, no conflict: `.ufo/waves/round-29/w1/deliver-c2-152-classification.tsv` (mtime 21:39:48) is receipt-side and re-derives the same split with a finer granularity — their `vadv-49/.gitignore:1:fixture/` 138 = my 126 `.git` internals + 12 non-`.git` fixture files, plus `shims/` 2, `case-V6` 6 (`:4,5,6`), root `__pycache__/` 4, `.scratch` 1+1, total 152. An earlier revision of that file (read earlier in this seat's run, before its 21:39:48 mtime) carried the source-side `.gitignore:1:.ufo/waves/` collapse, which I flagged to `SwarmExecutor06-2`; the delivered revision no longer carries it, and my independent `check-ignore` sweep above matches it line for line. Nothing under `census/` was changed by me.

10. Pre-existing tracked modification in the r26 capture source, not mine: `git -C <lane> status --porcelain` reported exactly one entry before and after this seat's run — ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` (mtime 20:45:43, `git diff --stat` = 2 insertions, 1 deletion; the changed lines record inbound-coordination text and state that the round-26 Gate case set stays frozen at S128–S132). Because `census/round-26/waves/` was captured from `.ufo/waves/round-26/`, that source tree is no longer byte-identical to the committed receipt for this one path, and a recapture will pick up the edited bytes. Flagged for the integration owner; I did not touch the file.
11. ATTACK reproduced (filed by `SwarmExecutor06-2` as A-1; it falsifies my finding 8 wording, so I measured it myself). Scratch clone at b8cb4b3: (a) Python-drop the 152 absent record lines from `census/round-26/waves/manifest.sha256`, (b) `git rm` the 14 committed symlinks no record covers, commit `270d04e505628aea53b196c3996ef18b3a40d665` → `r26 records=1230 failed=0 uncovered=0 floor_violation=0`, `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`, rc 0. 166 evidence paths disappear (152 phantom records plus 14 real committed symlinks) while the frozen C2 target reads green, because the floor comparison is `<` and `uncovered` is computed over the committed tree.
12. Amendment calibration for A-1 (scratch instrumentation copies only; lane counter untouched). The satisfiable correct receipt is: records for every committed regular file, plus `symlinks.tsv` (itself recorded), 1231 records → at `251bfad6f938bf2aac2ab6de3d46c750a2b644c7` on base b8cb4b3 the unmodified counter returns `r26 records=1231 failed=0 uncovered=0 floor_violation=0`, `SUMMARY … failed=0 uncovered=0 floor_violations=0`, rc 0. Max feasible r26 records is therefore 1231 (1230 committed regular files + `symlinks.tsv`); a record whose tree entry is a symlink is scored failed, so 1382 is unreachable. Measured floor variants: `FLOORS['26']=1382` leaves the base verdict untouched (152/14, rc 1) as reported, but scores that correct receipt `floor_violation=1` rc 1 — it kills the C2 target instead of hardening it; `FLOORS['26']=1231` leaves base at 152/14 rc 1, keeps the correct fix green (rc 0), and turns A-1 red (`records=1230 floor_violation=1`, rc 1). Residual hole that no records floor can close: the correct receipt with the 14 symlinks deleted (`e80eb5d8bbf00366f5e319ee44071d049d8373a9`) is still green at 1231 (`records=1231 failed=0 uncovered=0`), because `uncovered` only sees paths that still exist; catching that needs a frozen committed-path-set or symlink-count check, i.e. a predicate change the contract forbids mid-round. Practically, A-1 is visible in the landing diff (152 manifest lines plus 14 tracked symlinks deleted), so a reviewer catches what the counter cannot. Risk noted for the r26 recapture: 5 of the 14 symlink targets are absolute `/home/vgpnk/…` paths, so a literal `symlinks.tsv` would commit host paths into the lane (precedent: `de478b4` removed a runtime path token from calibration evidence).

Other committed receipts: no. The counter enumerates only `census/round-<N>/waves/manifest.sha256`, and the committed tree at HEAD contains exactly three such manifests (`git ls-tree -r --name-only HEAD` → r26, r27, r28), so other receipt families (`census/round-29/records/*`, `census/round-2x/*.tsv`, `.ufo/waves/*`, tool receipts) are outside its surface entirely and cannot make it fail. Within the surface, the r27 (124 records / 125 committed entries) and r28 (75 / 76) manifests pass `failed=0 uncovered=0 floor_violation=0` at every revision where they exist — 765fe8b through b8cb4b3 — and that pass is not vacuous: zeroing one r27 record hash in the scratch clone (`11f603eca3eecc6efc5d2ef222d946a685c81de9`) makes the same counter report `r27 records=124 failed=1`, `SUMMARY failed=153`. Only the r26 receipt fails, and it fails for the whole life of the receipt rather than at any later commit.

## Deliveries
- `.ufo/waves/round-29/w1/deliver-c2-history.tsv` (history sweep table, 7 lane revisions + 2 labelled scratch rows, provenance header lines).
- `.ufo/waves/round-29/w1/SwarmExecutor14.md` (this report).

Scratch `/var/tmp/souji-r29-HistoryC2Sweep/` and `/var/tmp/souji-r29-HistoryC2Sweep.IQApjE/` removed after the runs; no lane bytes, index, jj state or external path touched; no tool installed. Unrun: none — every number above comes from a command executed in this run.
