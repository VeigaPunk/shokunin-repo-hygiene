# SwarmExecutor03 — C2 instrument v2 (wave-evidence capture over committed bytes)

## Status

STATUS: PASS — v2 capture tool delivered; the r26 receipt recaptured with it verifies over COMMITTED bytes: frozen counter `failed=152 uncovered=14` → `failed=0 uncovered=0`, `r26 records=1255` (floor 1230), counter rc 1 → 0. Every old exit code and the read-only/no-network/no-git-mutation promises are kept. Two residual notes (F5, F6) and one mandated behaviour change (F3) are listed below; none blocks the C2 target.

## Evidence

**E1 — red before (read-only, lane).** The routed defect is `corpus/lessons/round-28-verifier-spotcheck.md:114`: "add a nested-`.gitignore` case to `tests/fixtures/r28-wave-evidence-capture.sh`" (same item: capture must verify "against what git will commit").

```
$ python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
rc=1
```
Same line at prereg tip `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, rc 1. No lane writes.

**E2 — recapture + frozen counter in a scratch clone** (tool bytes = the delivered file, sha256 `3db37453e0fdbd253e9f8abaff970c88995eeaeb18bcbd2df42ca9a712397374`).

```
$ D=$(mktemp -d /var/tmp/souji-r29-C2ToolV2.XXXXXX)
$ git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c2"
$ git -C "$D/c2" config user.email r29@scratch.invalid ; ... user.name "r29 scratch"
$ cp -a /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26 "$D/c2/.ufo/waves/round-26"
$ cp <delivery> "$D/c2/tools/souji-wave-evidence-capture.sh"
$ bash "$D/c2/tools/souji-wave-evidence-capture.sh" "$D/c2" 26
captured+verified: $D/c2/.ufo/waves/round-26 -> $D/c2/census/round-26/waves
records=1255 renames=5 excluded=11 symlinks=17
rc=0
$ git -C "$D/c2" add -A -- census/round-26 && git -C "$D/c2" commit -q -m "r29 C2 scratch: r26 recaptured by v2 tool"
rev=86e370d87da4e48ef8dec25de0e4f2558fff0a66
$ bash "$D/c2/tools/souji-wave-evidence-capture.sh" "$D/c2" 26 --verify --rev 86e370d87da4e48ef8dec25de0e4f2558fff0a66
verify-rev rev=86e370d87da4e48ef8dec25de0e4f2558fff0a66 records=1255 failed=0 uncovered=0
rc=0
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/c2-counter.py --root "$D/c2" \
    --rev 86e370d87da4e48ef8dec25de0e4f2558fff0a66
r26 records=1255 failed=0 uncovered=0 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=86e370d87da4e48ef8dec25de0e4f2558fff0a66
rc=0
```
Scratch clone was created with `git -C "$D/c" rev-parse --show-toplevel` → `/var/tmp/souji-r29-C2ToolV2.lgPgUL/c`; identity configured only with `git -C <scratch> config`; every git call named `-C`; scratch removed at the end.

**E3 — committed-byte invariants of that receipt** (`86e370d8`).

```
$ git -C c2 ls-tree -r --name-only 86e370d8 -- census/round-26/waves | grep -cE '\.(gitignore|gitattributes)\.captured$'
5
$ git -C c2 ls-tree -r --name-only 86e370d8 -- census/round-26/waves | grep -cE '(^|/)(\.gitignore|\.gitattributes)$'
0
$ git -C c2 ls-tree -r 86e370d8 -- census/round-26/waves | grep -c '^120000'
17                      # symlinks.tsv rows: 17
$ cut -f3 census/round-26/waves/excluded.tsv | sort | uniq -c
   7 git-dir            # 7 refused .git trees, each one digest row
   4 ignored            # 4 __pycache__/*.pyc
```

**E4 — legacy receipts are byte-compatible** (v1 manifests written by the uutils `sha256sum` path).

```
bash tool "$D/c" 27 --verify            -> verified ... records=124        rc=0
bash tool "$D/c" 27 --verify --rev R    -> verify-rev records=124 failed=0 uncovered=0
bash tool "$D/c" 28 --verify            -> verified ... records=75         rc=0
bash tool "$D/c" 28 --verify --rev R    -> verify-rev records=75  failed=0 uncovered=0
```

**E5 — feature harness (scratch, 43 assertions, 43 pass).** Covers: nested `.gitignore`+`.gitattributes` renamed and *their subtree kept* after neutralisation; root-ignored `__pycache__/*.pyc` and `*.log` excluded with reason `ignored`; `.git` FILE and `.git` DIR not copied, reason `git-dir`, `.git` file digest = sha256 of its bytes; symlink verbatim + bare `symlinks.tsv` col1; manifest holds summary/renames/excluded/symlinks and no symlink record; exactly one escaped record, named `nl/first\nsecond.md`; manifest names LC_ALL=C sorted; empty dir preserved; clean rev verify `failed=0 uncovered=0`; tamper ladder `1 0` → `2 0` → `2 1` → `2 2` (stray file, unaccounted symlink) → `3 1` (symlink row added, manifest now stale) → `0 1` (row flushed, wrong target ⇒ symlink uncovered again); rename collision refused rc 3; non-repo lane still captures and writes no accounting TSV; `--rev` without `--verify` rc 1, short rev rc 1, unknown rev rc 1.

**E6 — legacy fixture unchanged.** `bash tests/fixtures/r28-wave-evidence-capture.sh` against the v2 tool → `cases=6 pass=6 control=TAMPER-REJECTED`, rc 0 (rc 1/2/3/4 paths and the tamper control all still fire; case 6's captured-files count stays 0 because empty accounting TSVs are not written).

**E7 — delivery integrity.** `bash -n` clean; 649 lines; sha256 `3db37453e0fdbd253e9f8abaff970c88995eeaeb18bcbd2df42ca9a712397374` (identical in the run copy and the delivery file).

**E8 — peer confirmation (not executed by me).** SwarmExecutor04-2 reports its 12-case fixture green on these exact bytes (`md5 d00c545fcd2be2aecf93319e1f4a7c7f`): `cases=12 pass=12 control=TAMPER-REJECTED` exit 0, base tool red-before `pass=6` exit 1; case 11 shows untampered `failed=0` then tampered `failed=1 uncovered=0`.

## Findings

1. **Required surface (a)–(g) implemented.** (a) receipt stays `census/round-N/waves/`; (b) rename rule + `renames.tsv` — script:467 (stored name), 517, 521; (c) ignore predicate on the DEST path after the receipt is cleared — `make_ignorer` script:197-216 (literal `git check-ignore --no-index -q --` at 206, never `git add`), `.git` refusal `git-dir` script:452-463, ignored-exclusion at 475-482; (d) symlinks verbatim + `symlinks.tsv` script:498, 525; (e) GNU manifest with `./rel`, LC_ALL=C byte sort, escaped records, all accounting TSVs included — `gnu_line`/`manifest_bytes` script:296-306; (f) `--verify --rev` over ls-tree/cat-file with python3 hashing and `failed`/`uncovered` accounting — `verify_rev` script:576-625, rc 4 at 625; plain `--verify` still checks the disk copy `verify_disk` script:567-572; (g) exit codes 0/1/2/3/4/5 preserved.
2. **r26 arithmetic reconciles exactly.** Source has 1381 regular files (`find -type f` prints 1383 *lines* because two names contain a newline: `vadv54-run/r/nl/first\nsecond.md`, `vadv54-run/r/scratch/.scratch/old\nname.log`). 130 are excluded (126 files inside 7 `.git` trees, 4 `__pycache__/*.pyc`), 1251 copied, + 4 accounting TSVs = **1255 records**. Old receipt held 1382 records of which 152 were absent from git. Decomposition (the r28 closure's own `git check-ignore -v` attribution, `corpus/lessons/round-28-verifier-spotcheck.md` "Cause:"): `fixture/` 138 = 126 `.git` internals + 12 real fixture files, `__pycache__/` 4, `case-V6 /ledger*.tsv` 4, `shims/` 2, `case-F7`/`case-F8 .scratch/` 2, `case-V6 /src/`+`/vault/` 2 — sum 152. In v2 those 22 non-`.git`, non-pycache files are committed (they exist only because copied nested rules no longer apply), while the 126 `.git` internals become digest rows and the 4 `.pyc` become `ignored` rows.
3. **Behaviour change to log at supersession:** `.git` trees are no longer copied (mandate (c)), so the re-captured r26 receipt drops the 126 `.git` internals that the old receipt carried on disk, recording each tree as one `excluded.tsv` row with a subtree digest (construction documented in the script header, `tree_digest` script:218-237). The superseded r26 receipt is what the r28 closure found uncommittable; the L1 should say this plainly in the supersession note.
4. **Doc gap (no functional effect):** the header's exit-3 summary lists special file / path escape / nested src-dst / name collision but the ignore-predicate failure path also exits 3 (`make_ignorer` script:210-212). Bytes were frozen after peer validation, so the fix is left to the L1 rather than re-cut here.
5. **Residual gap:** `check_ignore_neutralised` script:538-541 rejects a *regular* file named `.gitignore`/`.gitattributes` in a verified receipt, but a *symlink* of that name in a receipt this tool did not write would pass `--verify`. Capture can never produce one (the rename rule covers symlinks too), so this only affects foreign receipts.
6. **Ignore-decision environment:** the check is the literal `check-ignore --no-index`, so a global `core.excludesFile` would participate. On this host `git config --get core.excludesFile` is empty and `~/.config/git/ignore` is absent, so the r26 decisions came from the lane's own `.gitignore` chain only (only `__pycache__/` matched, 4 files). A lane with a global exclude could therefore exclude more than its own rules say; that is the honest reading of "the lane's rules" as measured.
7. **Floor margin:** r26 sits 25 records above the frozen floor (1255 vs 1230) because 126 formerly-recorded `.git` internals are now accounted rather than recorded. A future round whose evidence is `.git`-heavy would compress that margin; the counter, not the tool, owns the floor.
8. **No lane mutation.** Only writes in the lane: this report and the delivery file under `.ufo/waves/round-29/w1/` (both gitignored paths). `git status --porcelain` in the lane shows one pre-existing entry that is not mine: ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`. No `git add/commit/push/stash/checkout/reset`, no jj mutation, no `rm`/`mv` outside `/var/tmp/souji-r29-C2ToolV2.*` (removed), no signals, no network, no tool installs (nothing to record for the 2026-10-19 tooling directive).

## Deliveries

- `.ufo/waves/round-29/w1/deliver-souji-wave-evidence-capture.sh` — final path `tools/souji-wave-evidence-capture.sh`; 649 lines; sha256 `3db37453e0fdbd253e9f8abaff970c88995eeaeb18bcbd2df42ca9a712397374`; `bash -n` clean.
