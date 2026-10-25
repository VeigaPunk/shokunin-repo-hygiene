# SwarmExecutor15 — Exec-C3Gitignore (round 28 w1)

## Status
STATUS: PASS — .gitignore created with exactly the three frozen patterns; after SwarmExecutor14's r26+r27 capture checkpoint, the 11 tracked r26 wave files were reverted to HEAD; frozen counter `git status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'` = 0; wave directories still exist on disk; receipt manifests `census/round-26/waves/manifest.sha256` and `census/round-27/waves/manifest.sha256` exist and are non-empty.

## Evidence
Before (start of wave, HEAD 0c96332932e66bbaf9cf1c246091d3275a0ab612, freeze parent 3a2a80d):
```
$ git -C <lane> status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'
169
$ git -C <lane> status --porcelain=v1 --untracked-files=all | wc -l
327
```
(tracked-modified under `.ufo/waves/round-26/w1/`: exactly the 11 files: CritAmendNeed.md, ExecLandingCheck.md, LabGitVersion.md, ScribeQ58Note.md, SimpCounterCheck.md, landing-check.md, q58-note.md, report-draft.md, results-count.py, shonen-lines.md, verify-loop.sh).

After .gitignore creation (50 bytes; od confirms exactly `.ufo/waves/\n`, `census/operator-sweep-*/\n`, `__pycache__/\n`):
```
$ git -C <lane> check-ignore -v .ufo/waves/round-27/w1/ConnClaims.md census/operator-sweep-20261019/chunks/chunk-00 tools/__pycache__/
.gitignore:1:.ufo/waves/ .ufo/waves/round-27/w1/ConnClaims.md
.gitignore:2:census/operator-sweep-*/ census/operator-sweep-20261019/chunks/chunk-00
.gitignore:3:__pycache__/ tools/__pycache__/
$ git -C <lane> status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'
11
```

After capture checkpoint (SwarmExecutor14 confirmed r26+r27 captures done; `test -s census/round-26/waves/manifest.sha256 && test -s census/round-27/waves/manifest.sha256` true) and revert of the 11 files via `git -C <lane> show master:<path> > <path>`:
```
$ git -C <lane> status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'
0
$ for d in .ufo/waves/round-26/w1 .ufo/waves/round-27 .ufo/waves/round-28 .ufo/waves/round-28/w1; do [ -d "$d" ] && echo "OK $d" || echo "MISSING $d"; done
OK .ufo/waves/round-26/w1
OK .ufo/waves/round-27
OK .ufo/waves/round-28
OK .ufo/waves/round-28/w1
$ (sha256 of `git show master:<path>` vs on-disk file for all 11) → match=11/11
```
No other paths were touched; no wave files deleted; no git/jj mutation (reverts are working-tree only). No tool installs performed (RULES.md read; none needed).

## Findings
1. Lane had no root `.gitignore` at wave start (tracked .gitignore files exist only under results/, tests/, and r26 assimilation fixture trees); the three patterns were added as a new file. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.gitignore`.
2. Frozen C3 counter baseline in preregistration.txt was 163 dirty `.ufo/waves` paths at 3a2a80d; observed 169 at wave start (HEAD 0c96332) — delta is round-28 wave files (w1-dispatch.json, w1.ready, swarm-registry.json) added since freeze; irrelevant to the 0-at-tip target.
3. SwarmExecutor14 reported a r26 manifest quirk: 2 entries with newline filenames (from the vadv54-run fixture tree, e.g. `first\nsecond.md`). Not in my scope; flagged for the C3 receipt reviewers (Rev-C3Receipts) to judge against the tool's special-file handling.
4. After .gitignore, untracked `.ufo/waves` files no longer appear in porcelain; only the 11 tracked-modified r26 w1 files remained, and they are now reverted — wave dirs left intact on disk, so no evidence is lost (bytes preserved in census/round-26/waves/).

## Attack log
None from this seat. (Pre-warning: gitignore does not un-track already-tracked legacy wave files; round-26's 11 historical tracked files remain tracked. If later rounds want zero tracked wave files, a one-time `git rm --cached` would be needed by the integrator — not performed, per scope.)
