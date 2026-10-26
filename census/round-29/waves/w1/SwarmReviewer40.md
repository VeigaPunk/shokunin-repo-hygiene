# SwarmReviewer40 — C2 base counter re-derivation (independent) + hostile-name robustness

STATUS: PARTIAL — my own verifier over an independently exported byte set reproduces the frozen
counter exactly per round (r26 1382/152/14, r27 124/0/0, r28 75/0/0) and the frozen counter never
traces back on hostile names (space, tab, newline, backslash, CR, non-UTF-8 file and directory
names, symlink/empty/dir manifests, bad revs). Partial because the frozen instrument has three
reach defects found by testing, and the naive r26 recapture required by C2 is unsafe today: the
receipt cannot detect a path-permuted copy, its GNU-only unescape false-fails the `\r` escape that
this host's own `sha256sum` emits, and the capture tool reports `--verify` green while 12 r26 wave
source files differ from the receipt (one of them currently dirty).

## Evidence

Base rev for everything below: `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (verified with
`git -C <lane> rev-parse`), branch master, tip `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

1. Export (does not use the frozen counter's acquisition path):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive 691dd29... \
  census/round-26/waves census/round-27/waves census/round-28/waves | tar -x -C /var/tmp/souji-r29-ReDeriveC2/
```
Exported path set equals `git ls-tree -r -z` exactly (r26 1247 blobs, r27 125, r28 76).
`git cat-file -p HEAD:.gitattributes` shows no `export-ignore`/`text`/`eol`/`filter` rule, so
archive bytes are blob bytes; and 1230 of the 1382 r26 records hash-match, which proves no
conversion happened. (Line-based `ls-tree -r | wc -l` reports 1245 for r26, two short: two record
names contain an embedded newline.)

2. My verifier (`/var/tmp/souji-r29-ReDeriveC2/verify.py`, own parser: GNU/uutils prefix `\`,
`\\`/`\n`/`\r` escapes, records `hash  name`, `./` stripped, uncovered = regular file or symlink
under the waves dir with no record and no `symlinks.tsv` waiver):

```
r26 records=1382 malformed=0 failed=152 uncovered=14
r27 records=124 malformed=0 failed=0 uncovered=0
r28 records=75 malformed=0 failed=0 uncovered=0
TOTAL failed=152 uncovered=14        rc=1
```

3. Frozen counter, same rev, same host, run exactly as enumerated by the prereg:

```
python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 691dd29...
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29...
```
rc 1, as the prereg declares ("Before at base: `manifests=3 failed=152 uncovered=14
floor_violations=0`, rc 1", preregistration.txt:7). No discrepancy of any kind per round.

4. Cause of the 152 (all 152 are absence, zero hash mismatches, zero malformed lines, zero
duplicate record names):

```
git -C <lane> check-ignore --no-index --stdin   # 152 paths piped in
-> rc 0, 152 lines out (all ignored)
```
All 152 also still exist on the lane disk (152/152 `os.path.exists`). Families: 140
`assimilation/validate/tests/vault/vadv-49/...`, 6 `.../case-V6/...`, 4 `__pycache__/*.pyc`,
2 fixture `.scratch/stale-probe-f{7,8}.tmp`. So the r26 manifest was generated from disk bytes that
git can never commit — exactly the capture defect C2 repairs (nested .gitignore / ignored names).

5. Cause of the 14 uncovered: they are exactly the 14 committed symlinks; no unrecorded regular
file exists (the only non-record regular file is `manifest.sha256`, excluded by name), no
`.gitkeep` anywhere under the three waves dirs, `summary.tsv` is recorded in all three manifests,
no record contains `..`. There is no `symlinks.tsv` in any round at base, so the 14 links have no
waiver. Two records are GNU-escaped (embedded newline) and both hash-match, so escape decoding is
right: `./assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md` and `.../r/scratch/.scratch/old\nname.log`.

6. Hostile-name robustness of the frozen counter (scratch repos created with `git -C <D> init -q`,
`git -C <D> rev-parse --show-toplevel` printed `$D` before the first commit):

| shape in `census/round-26/waves/` | frozen counter | rc | traceback |
|---|---|---|---|
| space, tab, newline, backslash, 0xFF/0xFD/0xFC/0xFE file names + non-UTF-8 symlink with matching `symlinks.tsv` + uncovered non-UTF-8 file + stray symlink | records=8 failed=1 uncovered=4 | 1 | none |
| non-UTF-8 directory `dir\xff sub/` holding `f\xfe.txt`, raw-byte record | records=1 failed=0 uncovered=0 | 1 (floors only) | none |
| `manifest.sha256` as a symlink / empty / a directory / CRLF records | records=0 failed=1 uncovered=2, floor_violations=3 | 1 | none |
| short rev `abc123` | `COULD-NOT-EVALUATE rev must be a full 40-hex revision` | 1 | none |
| 40-hex rev absent from the repo | `COULD-NOT-EVALUATE git ls-tree ... fatal: not a tree object` | 1 | none |
| repo with no manifest at all | `SUMMARY manifests=0 failed=0 uncovered=0 floor_violations=3` | 1 | none |

My verifier gave identical counts on the first and last rows. rc was always 1 (never 2, never a
traceback), matching the assignment's requirement.

7. `r26 --verify` is green against the live source while the source has drifted:

```
bash tools/souji-wave-evidence-capture.sh <lane> 26 --verify   -> rc 0 "captured+verified"
```
but 12 recorded r26 wave files differ between the live `.ufo/waves/round-26/w1/` and the receipt:
`CritAmendNeed.md ExecLandingCheck.md LabGitVersion.md ScribeGateDraft.md ScribeQ58Note.md
SimpCounterCheck.md landing-check.md q58-note.md report-draft.md results-count.py shonen-lines.md
verify-loop.sh`. For 11 of them HEAD bytes already differ from the receipt (later committed
edits, worktree clean); `ScribeGateDraft.md` has HEAD == receipt (`8f25ae21...`) but the worktree
is dirty (`a7f30602...`, mtime today 20:45, `git status` shows `M`), i.e. an uncommitted draft edit
to a file the r26 manifest records at line 1335.

## Findings

1. **`--verify` cannot detect source drift (capture tool, `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-wave-evidence-capture.sh:182`).** The source-vs-receipt comparison is inside `if [[ $verify_only -eq 0 ]]`, so verify mode only checks the receipt's internal self-consistency. Evidence: item 7 — rc 0 for r26 today with 12 drifted files. The header (lines 18-20) states "the file-hash set is compared against the source tree" as part of the receipt's re-verification; that sentence is false for `--verify`. C2's fix should move that comparison under `--verify` (it would then legitimately fail r26 until the recapture).
2. **Source-vs-receipt comparison is tautological and permutation-blind (`...capture.sh:184-191`).** In capture mode the receipt was just copied from the source, and the check compares sorted hash *values* only (`awk '{print $1}'`), so a receipt whose paths hold each other's bytes still compares equal. It cannot fail for the reason it exists.
3. **The frozen counter cannot detect a permuted receipt (attack, see below).** Demonstrated with the real counter: post-fix-clean r26 (records 1231), clean r27 (124), and r28 with `w1.ready` and `w1.ready.dispatched` contents swapped and the manifest regenerated → `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`, rc 0, while `census/round-28/waves/w1.ready` no longer equals committed `.ufo/waves/round-28/w1.ready` (`e631acbc...`). The predicate "verify over committed bytes" therefore only buys receipt self-consistency, not receipt-to-source fidelity; `.ufo/waves/` is tracked (90 blobs under `round-26/w1` alone), so a path-set comparison against the committed source is available to whichever claim wants it.
4. **GNU-only unescape false-fails this host's `\r` escape (`census/round-29/c2-counter.py:25-26`, `re.sub(r'\\([\\n])', ...)`).** `sha256sum --version` here is uutils 0.8.0; it escapes `\\`, `\n` **and** `\r` (leaves `\x01`, ESC, DEL, VT, BS raw — probed one name per call). End-to-end through the real capture tool (scratch lane, round-98): the manifest line is `\87428fc5...  ./w1/cr\rname.md`, the file's sha256 is exactly `87428fc5...`, and the frozen counter reports `r98 records=5 failed=1 uncovered=1` — the same file counted both as a failed record and as uncovered. Zero such records exist at base (grep `\\r`: 0 in all three manifests), so the base numbers stand; the defect bites any future receipt with a CR-bearing name, which is producible on this host by the lane's own tool.
5. **`symlinks.tsv` counts as uncovered unless the manifest records it (`census/round-29/c2-counter.py:80-88`).** It is a regular file under the waves dir and only `manifest.sha256` is excluded by name. The C2 recapture must therefore add `./symlinks.tsv` to the r26 manifest, not only create the ledger; with it, my post-fix simulation lands records 1231/124/75 and all zeros (rc 0). Without it, uncovered stays 1 and C2 cannot reach its target.
6. **Zero floor margin for r26.** FLOORS r26 = 1230 = 1382 − 152. A correct recapture lands at 1231 (1230 files + `symlinks.tsv`); any further legitimate exclusion or a decision to stop recording `summary.tsv` drops below the floor and produces a false red. Not gameable in the loosening direction, but brittle; worth logging with the supersession rather than silently absorbing.
8. **`.ufo/waves/` is ignored (`.gitignore:1`), so r29 wave deliveries do not appear in `git status`.** `git check-ignore -v .ufo/waves/round-29/w1/SwarmReviewer40.md` returns `.gitignore:1:.ufo/waves/`; no r29 wave file is tracked at tip and no r28 wave file is either, while r26/r27/r28 census receipts are tracked. Landing r29 evidence therefore needs `git add -f` (or an equivalent explicit add) or the round closes with no committed wave inputs.

7. **The r26 recapture is unsafe while `.ufo/waves/round-26/w1/ScribeGateDraft.md` is dirty.** Recapture copies disk bytes, so the new r26 receipt would contain uncommitted content with no commit to point at, and would also silently absorb 11 files whose committed bytes changed after the original capture. The prereg already commits to logging the supersession (preregistration.txt:7, "The re-captured r26 receipt supersedes the committed one"); the log should name the 12 files and the recapture should run only on a clean `git status -- .ufo/waves/round-26/`.

## Attack log

- **A1 — permutation laundering of a receipt (gameable predicate).** Scratch repo `/var/tmp/souji-r29-ReDeriveC2.s.*`: r26 rebuilt as the C2 post-fix state (ignored records dropped, `symlinks.tsv` written and recorded → 1231 records), r27 unchanged (124), r28 with two recorded files' contents swapped and manifest regenerated (75). Frozen counter at `fb049bb...`: `r26 records=1231 failed=0 uncovered=0 floor_violation=0 / r27 ... / r28 ...` and `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`, **rc 0**. The C2 zeros are reachable, but also reachable by a receipt that no longer matches the committed source in path↔content assignment. Per the contract I am not proposing a predicate change; this is reported so the L1 can decide whether the claim needs the stricter source-tree comparison.
- **A2 — self-waiving symlink ledger.** `uncovered` accepts any `symlinks.tsv` line whose col2 equals the committed link blob, with no check that the target exists, normalizes inside the tree, or is not `/dev/null`. r26 already contains `vadv54-run/q/led-devnull.tsv -> /dev/null`, a dangling `led-dangling.tsv -> missing.tsv`, and absolute-path links into the lane worktree, so the ledger waives exactly the shapes an auditor would want flagged. Frozen by contract; reported as gameability, not as a request to change the counter.
- **A3 — escape-set narrowness (see finding 4).** The same unescape rule is used by my independent verifier, so the false red is not an artifact of one implementation: it is a property of decoding uutils output as GNU output.
- Checks that did **not** break the counter: record names containing `..` (key lookup only, no filesystem traversal — 0 at base); duplicate record names (none at base; dict-keyed, so a duplicate cannot flip a failing path to pass); manifest paths outside `census/` (not enumerated); round-28 `summary.tsv` presence (recorded in all three); empty/absent manifests (floor catches).

## Residual risk and verification gaps

- I did not score C1 or C3 and did not re-run them; C2's after-state cannot be measured until the L1 lands a capture-tool rewrite plus the r26 r29 receipts — my r26 "post-fix" numbers (1231/124/75, zeros) are a `[INFERENCE]`-grade simulation in scratch, not a measurement of the lane.
- My verifier mirrors the frozen counter's escape set by design; the `\r` result above was confirmed against the real capture tool and the raw sha256 of the file, not by reading the counter's code path twice.
- `.ufo/waves/round-26/w1/ScribeGateDraft.md` was already dirty when I started; I did not touch it. No lane file other than this report was written by me; no git/jj mutation, no signals, no tool installs. Scratch under `/var/tmp/souji-r29-ReDeriveC2*` was removed after this report was written.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmReviewer40.md` (this report). No other delivery file named for this item.
