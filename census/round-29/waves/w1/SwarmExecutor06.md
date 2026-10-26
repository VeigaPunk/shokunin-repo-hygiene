# SwarmExecutor06 — C2 red-before reproduced and the 152 failures classified

## Status
STATUS: PASS — C2 red-before reproduced byte-for-byte at base (`failed=152 uncovered=14`, rc 1) and every one of the 152 failed r26 manifest records is now classified with a measured ignore rule, size and source-hash verdict; delivery TSV written. One risk for the C2 owner is raised: the `.ufo` source tree has drifted from the r26 manifest for 12 non-failed records, so a naive recapture is byte-exact for the 152 but not for the whole manifest. One counter ATTACK is filed (A-1: dropping the 152 record lines plus the 14 uncovered symlinks scores 0/0/0 under the frozen floor); the L1 owns any stricter-only amendment.

## Evidence

1. Red-before, exactly as specified (lane base 691dd29211c53d0ef94fa072394cb9c8a69fe92e, workspace `souji-shokunin`):
```
$ python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
RC=1
```
Matches the frozen prereg do-nothing control (152/14). r27 and r28 are clean, so the defect is confined to the r26 receipt.

2. Failure kind, recomputed with the counter's own logic over `git ls-tree`/`cat-file` at that rev (script `/var/tmp/souji-r29-C2Classify152/analyze.py`, scratch clone `/var/tmp/souji-r29-C2Classify152/c`):
```
records 1382 unique 1382 malformed lines 0
failed 152
Counter({'absent': 152})
```
Every failure is *absence from the committed tree*; there are zero sha-differs, zero symlink-mode records and zero unparseable manifest lines. The manifest itself is intact and GNU-escaped records all decode (no escaped record is among the 152).

3. Ignore attribution, evaluated in the scratch clone on the path that actually failed to enter git — the committed counterpart `census/round-26/waves/<record>`:
```
$ git -C /var/tmp/souji-r29-C2Classify152/c check-ignore -v --no-index --stdin   # 152 paths
census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:1:fixture/   138
.gitignore:3:__pycache__/                                                                4
census/round-26/waves/assimilation/validate/tests/vault/case-V6/.gitignore:6:/ledger*.tsv 4
census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:2:shims/       2
census/round-26/waves/assimilation/validate/tests/fixtures/case-F7/repo-tree/.scratch/.gitignore:1:* 1
census/round-26/waves/assimilation/validate/tests/fixtures/case-F8/repo-tree/.scratch/.gitignore:1:* 1
census/round-26/waves/assimilation/validate/tests/vault/case-V6/.gitignore:4:/src/        1
census/round-26/waves/assimilation/validate/tests/vault/case-V6/.gitignore:5:/vault/      1
attributed 152  unattributed 0
```
Rule stability between base and tip was checked, not assumed: `git diff --name-only 691dd29..b8cb4b3 -- '*.gitignore'` is empty, and the six consulted ignore files have the same blob at both revs (root `.gitignore` 8538166cdbd6, `fixtures/.gitignore` 8a9cdb6f7ec6, both `.scratch/.gitignore` d6b7ef32c847, `case-V6/.gitignore` 85c7ebdb4805, `vadv-49/.gitignore` 343d0b08b418). The five nested files are present in the clone worktree at the census paths, so the rules were read from real files, not inferred.

4. Source fidelity of the 152 (read-only `stat`/`sha256` over `.ufo/waves/round-26/`):
```
source_exists_yes 152 / 152
source_sha256_matches_manifest_yes 152 / 152
```
All 152 sources exist and are byte-identical to the manifest, so those 152 can be recaptured byte-exactly.

5. Whole-tree recapture check (same sweep, all 1382 records):
```
manifest records 1382  source regular files 1381  source symlinks 17
manifest names absent on disk 1 ['summary.tsv']
disk regular files not in manifest 0
whole-source verify: mismatches 13  (1 missing summary.tsv + 12 hash)
```
The 12 drifting records are listed in Finding 3.

6. Arithmetic cross-check of the receipt: 1245 committed paths under `census/round-26/waves/` at base, minus `manifest.sha256` = 1244; 1382 records − 152 failed = 1230 covered, plus 14 uncovered = 1244. Consistent, and no committed path is double-counted.

7. Cross-revision control (same counter, run this seat):
```
0c96332932e66bbaf9cf1c246091d3275a0ab612 (765fe8b~1) SUMMARY manifests=0 failed=0 uncovered=0 floor_violations=3
765fe8bd602ac679d01e7a0790711485209ab8bd            r26 records=1382 failed=152 uncovered=14 floor_violation=0   (SUMMARY manifests=2 ... floor_violations=1)
b8cb4b31ce80e2e3314b88e85d40ea9873180804            r26 records=1382 failed=152 uncovered=14 floor_violation=0   (SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0)
```
`765fe8bd602ac679d01e7a0790711485209ab8bd` (author date 2026-10-25 15:43:53 -0300, committer date 16:01:00 -0300, "round-28: repair pointers, curate F4 primitives, capture wave evidence") is the first revision carrying `census/round-26/waves/manifest.sha256`; its parent is `0c96332932e66bbaf9cf1c246091d3275a0ab612`. This history is a re-commit chain — each commit's committer time equals the next commit's author time (0c96332 c15:43:53 / 765fe8b a15:43:53; 765fe8b c16:01:00 / ed270c4 a16:01:00, c16:04:52; de478b4 a16:04:52) — so revisions are identified by sha and by author date, and `ed270c4` ("round-28: record frozen counters, frontier, and wave results") is the commit that adds the r28 manifest. The `floor_violations` 3→1→0 progression tracks manifest introduction only: the parent has none, 765fe8b adds r26, ed270c4 adds r28. The r26 manifest blob is the same object throughout (`11be6bc1947c1edca5700c94d75a7a1433044909` at base). The 152/14 defect is introduced by the r26 receipt itself and is unchanged through the prereg tip — no wave-1 seat work moved it.

8. Deletion and positive controls against the counter, run this seat in a scratch clone of the lane at b8cb4b3 (throwaway identity configured only via `git -C <scratch> config`; `rev-parse --show-toplevel` printed the scratch clone before the first commit):
```
8b770f2c44a2b1f4a5f77e527cd9c15302f3c126  r26 manifest with its 2 GNU-escaped records deleted
  r26 records=1380 failed=152 uncovered=16 floor_violation=0
  SUMMARY manifests=3 failed=152 uncovered=16 floor_violations=0
a4ca3d968c73d46991201256cd7719f98704e936  one r27 record hash zeroed
  r27 records=124 failed=1 uncovered=0 floor_violation=0
  SUMMARY manifests=3 failed=153 uncovered=14 floor_violations=0
```
Deleting the escaped records leaves `failed` at 152 and only uncovers the two newline-named committed files, so escape decoding contributes zero failures; zeroing a single r27 hash yields `failed=1`, so the sha-diff branch is live and "all 152 are absent, none differ by sha" is not a vacuous result.

## Findings

1. **The 152 are all "not committed", not "wrongly hashed".** `failure=absent` for 152/152 at `census/round-26/waves/manifest.sha256` (rev 691dd29). No record differs by sha and no manifest line is malformed, so the r28 closure's framing ("two malformed newline-path records") understated the defect by 150 records. The two GNU-escaped records (`vadv54-run/r/nl/first\nsecond.md`, `vadv54-run/r/scratch/.scratch/old\nna…`) are not part of the failure set: deleting both from the manifest in a scratch clone leaves `failed=152` and moves `uncovered` 14→16 by uncovering the two newline-named committed files (Evidence 8; the peer seat reproduced the same 1380/152/16 in its own scratch at `def0223`), while zeroing one r27 hash flips `failed=1` — so escape decoding contributes zero failures and the sha-diff branch is live.

2. **148 of 152 are nested-fixture ignore rules carried inside the captured tree, not lane policy.** The receipt contains the validate tool's own test fixtures, including *their* `.gitignore` files, and git honours them when the receipt is added:
   - `assimilation/validate/tests/vault/vadv-49/.gitignore:1:` pattern `fixture/` — 138 records (the whole `fixture/` tree of seven synthetic repos a1,a2,a4,a5,b,c,control);
   - `.../vadv-49/.gitignore:2:` pattern `shims/` — 2 records (`shims/electron43`, `shims/obsidian`);
   - `.../tests/vault/case-V6/.gitignore:6:` pattern `/ledger*.tsv` — 4 records, plus `:4:` `/src/` — 1 (`src/payload.md`) and `:5:` `/vault/` — 1 (`vault/payload.md`);
   - `.../fixtures/case-F7/repo-tree/.scratch/.gitignore:1:` pattern `*` — 1 (`stale-probe-f7.tmp`); same for case-F8 — 1.
   These are the "nested .gitignore neutralised without dropping the file" cases the C2 fix must cover: the ignore files are themselves receipt content and must stay in the manifest while ceasing to exclude their siblings.

3. **126 of 152 sit inside nested `.git/` directories of the captured fixture repos and could never be added even with `-f`.** Composition: 98 `.git/hooks/*.sample`, 7 `.git/config`, 7 `.git/info/exclude`, 7 `.git/HEAD`, 7 `.git/description`. They are currently excluded by the enclosing `fixture/` rule, so a fix that only neutralises `.gitignore` rules will still not make them committable; either the capture tool must account for them as explicitly-excluded, or the receipt must stop embedding fixture `.git` internals. This is the concrete case behind the "accounted as excluded, never silently dropped" requirement in the prereg.

4. **4 of 152 are the lane's own root rule `__pycache__/`** (`.gitignore:3:`): `assimilation/validate/tools/__pycache__/*.pyc` (3) and `assimilation/validate/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` (1). This is the "root-ignored name" case: the name is excluded by the repo's own policy, so the receipt must record it as excluded rather than dropping it.

5. **Source tree still exists; the 152 have not drifted, but the whole r26 source has.** `.ufo/waves/round-26/` holds 1381 regular files and 17 symlinks, and the 152 sources hash-match 152/152. However 12 manifest records' sources no longer match the manifest:
   - `w1/CritAmendNeed.md`, `w1/ExecLandingCheck.md`, `w1/LabGitVersion.md`, `w1/ScribeQ58Note.md`, `w1/SimpCounterCheck.md`, `w1/landing-check.md`, `w1/q58-note.md`, `w1/report-draft.md`, `w1/results-count.py`, `w1/shonen-lines.md`, `w1/verify-loop.sh` — mtime 2026-10-25T15:53:30, and the current bytes equal `HEAD` (b8cb4b3), i.e. the rewritten bytes were committed under `.ufo/`;
   - `w1/ScribeGateDraft.md` — mtime 2026-10-25T20:45:43 and dirty vs `HEAD`; `HEAD` still holds the manifest-matching bytes.
   For all 12 the committed census copy still matches the manifest (`census-ok`), so the frozen counter is unaffected — the census receipt is the only byte-faithful copy. A "recapture" driven from today's `.ufo` would silently re-hash those 12 records (and add `summary.tsv`); the C2 owner must decide that supersession explicitly instead of letting the copy decide it. Provenance of the 15:53 rewrite is [INFERENCE] not established here — I only measured that the pre-commit `.ufo` bytes already differed from the r26 manifest.

6. **The 14 uncovered are exactly the receipt's 14 committed symlinks, with no `symlinks.tsv` at base.** `git ls-tree` shows mode `120000` for `assimilation/validate/tests/vault/mock-cli/obsidian-cli`, `.../obsidian-cli-inspector`, `.../vadv-51/fixture/vault/x2-note.txt`, seven under `.../vadv54-run/q/`, `.../vadv54-run/p/alias-dotdot-target.md`, `.../p/alias-link.md`, `.../tools/impl-21.sh`, `.../tools/impl-39.sh`, `.../tools/souji-census.impl-40.sh`; `census/round-26/waves/symlinks.tsv` does not exist at 691dd29, so none can be covered. Source-side, 17 symlinks exist under `.ufo/waves/round-26/` including one absolute target (`.../vadv-51/fixture/vault/x2-note.txt` → `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/vadv-51/fixture/src/x2-note.txt`), which matters for the capture tool's link-target verbatim handling.

7. **Secret-shaped names: none by basename.** Sweep over the 152 recorded basenames for `vault token secret key credential passw id_rsa .pem .env oauth auth .ssh .aws .netrc cookie session kdbx keystore` gives 0 hits. The only hit is the directory component `vault` (146 paths under `assimilation/validate/tests/vault/`), a test-fixture directory name, and the name-level credential carriers `.git/config` (7) and `.git/info/exclude` (7) — both inside the ignored `fixture/` subtree of synthetic repos. No contents were read; kagi owns content scans.

8. **Attribution trap worth recording for anyone re-deriving this list.** Running `git check-ignore -v --no-index` on the *source* path `.ufo/waves/round-26/<record>` collapses all 152 to `.gitignore:1:.ufo/waves/` (measured, same clone). That rule is the intentional reason the evidence lives in a census receipt at all, not the reason the receipt is incomplete; git also does not descend into an excluded parent while collecting deeper rules. The classification above therefore uses the census path, and both computations are stated so the choice is inspectable.

9. **Delivery rows are independently re-checkable.** 152 data rows, 8 columns, 152 unique paths, all `failure=absent`, all `source_exists=yes`, all `source_sha256_matches=yes`; four randomly sampled rows were re-run as single `git check-ignore -v --no-index` calls in the clone and returned the same rule as the TSV. TSV sha256: `b06d04cff6b674ef5c1451bf4b72c82f0d4f07b4ba9e301c35d72076b3d0af52`.

## Attack log

ATTACK A-1 — the frozen C2 counter scores PASS on a receipt that deletes the evidence it is supposed to guard. Measured this seat in a scratch clone of the lane at b8cb4b3: (a) drop the 152 failed record lines from `census/round-26/waves/manifest.sha256`, (b) `git rm` the 14 committed symlinks that no record covers, commit `b5ae0c5963ad525f1e0de6773a7429bbdcfbb9f9`, then run the frozen counter:
```
r26 records=1230 failed=0 uncovered=0 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0  rev=b5ae0c5963ad525f1e0de6773a7429bbdcfbb9f9   rc 0
```
Mechanism: `FLOORS['26'] = 1230` in `census/round-29/c2-counter.py:23` equals exactly the record count that survives dropping the 152 failures (1382 − 152 = 1230) and the check is `len(recs) < FLOORS.get(rn, 1)`, so equality passes; `uncovered` is computed over the committed tree, so deleting the 14 uncovered symlinks empties it. The prereg junk control enumerates "drop the failing records only -> uncovered 14 (fails)" but not that drop plus the symlink deletion. A receipt that lost 166 of its evidence paths would therefore score 0/0/0.
Stricter-only remedy probes (scratch copies of the counter only; the lane counter and its floors were not modified):
- `FLOORS['26']=1382` (my first probe) trips the deletion mutation — `r26 records=1230 failed=0 uncovered=0 floor_violation=1`, rc 1 — and leaves the base verdict at `1382/152/14/0`. **Retracted as an amendment**: a record whose committed tree entry is mode `120000` is scored failed by the counter's record loop, so symlinks can never be records, and 126 of the 152 failing paths sit inside nested `.git/` directories git refuses to index, so 1382 records are unreachable for any receipt that keeps that evidence out of `.git`. The peer seat's minimal correct receipt (records for the 1230 committed regular files plus `symlinks.tsv`, commit `251bfad6f938bf2aac2ab6de3d46c750a2b644c7`) lands at `records=1231` and is red under a 1382 floor.
- `FLOORS['26']=1231` is the strictest value the peer could prove satisfiable: minimal correct receipt green, base unchanged at `152/14/0`, and A-1's deletion rev red at `records=1230 floor_violation=1`. It is not merely a count: at 1231 the record set is forced to be exactly the 1230 committed regular files plus `symlinks.tsv` — `uncovered` requires every committed regular file to be recorded, `symlinks.tsv` is one of them, and a record that survives without its file scores failed while a fabricated record for an absent path also scores failed, so there is no compensating move. What the floor cannot express is the absence of evidence for paths that never entered the tree: the 152 phantom record lines are simply gone, and that drop is only invisible when bundled with the `symlinks.tsv` addition — both halves show in the landing diff.
- Residual hole no records floor closes: the peer's `e80eb5d8bbf00366f5e319ee44071d049d8373a9` — an otherwise correct 1231-record receipt whose 14 committed symlinks are deleted while their `symlinks.tsv` rows remain — stays green at floor 1231, because `uncovered` only sees paths that still exist. The remaining A-1 surface is therefore exactly "symlink rows without symlink targets", which needs a committed-path-set or symlink-existence predicate the contract forbids mid-round.
- My earlier "equivalent superset rule" (new r26 record set ⊇ the 1382 records at 691dd29) is satisfiable only if every record path becomes a committed regular file, so it inherits the same 126-`.git` obstruction; it closes A-1, not the symlink-deletion residual.
Calibration measured this seat at base: `census/round-26/waves` holds 1245 committed paths = 1231 regular (including `manifest.sha256`) + 14 symlinks, i.e. 1230 record-eligible files; 5 of the 14 symlink targets are absolute (4 lane-absolute `/home/vgpnk/…` and one `/dev/null`), so a literal `symlinks.tsv` would commit host paths into the lane — precedent `de478b4` ("remove runtime path token from calibration evidence"). With the terminal receipt design still open, I recommend no specific floor; choosing and logging any amendment is the L1's.
Scope note: this is a scoring hole, not an undetectable one — exploiting it in the lane would show as 152 manifest lines plus 14 tracked symlinks removed in the C2 landing diff. I did not change the counter, its predicate or its floors.

## Deliveries
- `.ufo/waves/round-29/w1/deliver-c2-152-classification.tsv` — 152 rows (path, manifest sha256, failure, ignore rule, size, source existence, source sha256, match) plus summaries by ignore rule, by top-level directory (`assimilation` 152), by captured fixture area, totals, and the name-only secret sweep.
- `.ufo/waves/round-29/w1/SwarmExecutor06.md` — this report.

Scratch `/var/tmp/souji-r29-C2Classify152/` removed after use; no lane file outside the two paths above was written, no git/jj mutation, no network. No tools installed or upgraded this seat.
