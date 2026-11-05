# S61SentinelScope — safety and scope audit, souji round 61 wave w1

Scope: report only. No production file, seat file, lane Git state or host state was changed.
Baseline: lane HEAD = `c7228424c3919ecf142bab1aec8181722d86467b` (round-60 verifier spot-check commit, committed 2026-11-04T21:38:48-03:00).
Audit time: 2026-11-05, about 04:39 local. Wave spec written 04:36.

## Verdict
- Write scope: PASS, with two non-seat writes to explain (findings 1b, 1c).
- Frozen bytes: PASS. Production paths are byte-identical to the base commit.
- Q117 headers: no receipts exist yet, so nothing is missing. Two scratch sidecars would fail the header rule if promoted (finding 3).
- Secrets: FALSE POSITIVES ONLY. No credential material found; three files match the `op://` alternation, which is the literal text of the scan pattern in the spec (finding 4).
- pacman: PASS for the host log and process table. No pacman transaction in the wave window (finding 5).

## 1. Write scope
1a. Seat dirs under `.ufo/waves/round-61/w1/` at audit time: `S61ExecC2Fixture`, `S61ExecRealRecord`, `S61ReviewerC2`, `S61ScoutSources`, `S61ScribeCorpus`. All are empty (0 files). Command: `find <dir> -type f | wc -l`.
  `S61SentinelScope/` was created by this seat (empty until this file was written).
1a'. Scratch `/fast/scratch/hyaku/souji-r61/` holds 13 seat dirs; every file is inside its own seat dir. Counts: S61ConnSibling 5, S61ExecRealRecord 3, S61MutationCounter 7, S61ScoutSources 32, all other seat dirs 0.
1b. Wave-root files written 04:36–04:37 by the orchestrator, not by a seat: `round-61/make-spec.py`, `w1-spec.json`, `w1-dispatch.json`, `w1.ready`, `w1.ready.dispatched`, and `w1/swarm-registry.json` (mode 0600). Expected for dispatch, but they sit beside seat dirs, so the L1 should confirm the orchestrator owns them.
1c. `/tmp` entries newer than the spec: `/tmp/r61-run-out.json` (47772 B) and `/tmp/r61-run-err.txt` (0 B), both created 04:36:56 in the same second. Likely orchestrator run output, not a seat write. The L1 should confirm. Nothing in these files was read beyond size and mtime.
1d. `/tmp/alma.log` (2.6 MB, still growing at 04:39) is written by live processes `alma` (PIDs 3769363 and 3769372, owner vgpnk). That process is not a round-61 seat. It is host-level and out of this wave's scope. Under the 50 MB `/tmp` rule it is within limits. Noted, not attributed to a seat.
1e. Lane root: `find . -maxdepth 1 -newer .ufo/waves/round-61/w1-spec.json` returned nothing. Fleet root top level: nothing newer than the spec. `~/.local/bin`: nothing newer than the spec.
1f. `git -C <lane> status --porcelain` returned empty. Caveat: `.ufo/waves/` is gitignored (`.gitignore:1`), so this command cannot see wave-dir drift. Finding 1a–1e covers that gap.

## 2. Frozen bytes
2a. `git diff --stat c7228424c3919ecf142bab1aec8181722d86467b -- tools tests census corpus SKILL.md SCORECARD.md LOG.md`: empty, exit 0.
2b. `git rev-parse HEAD` = base commit. `git merge-base --is-ancestor <base> HEAD` succeeded. `git log <base>..HEAD -- <prod paths>`: no commits.
2c. `git ls-files -v` flag histogram: 17092 `H`, zero `S` (skip-worktree) and zero lowercase (assume-unchanged). No hidden modifications are possible through the index.
2d. Production files newer than the spec (`find tools tests census corpus SKILL.md SCORECARD.md LOG.md -newer w1-spec.json`, excluding `__pycache__`): none.
2e. Ignored production-path entries are pre-existing: `tools/__pycache__` mtime 2026-11-04 15:52, `census/operator-sweep-20261019` mtime 2026-10-19, plus older `census/round-*/__pycache__` and `tests/fixtures` scratch files. None is newer than the spec.
2f. Mutant base copies in `/fast/scratch/hyaku/souji-r61/S61MutationCounter/base/` are byte-identical (`cmp`) to the base commit blobs: `tools/souji-freeze-check.py`, `tools/souji-receipt-write.py`, and `tests/fixtures/r60-receipt-write.py`.

## 3. Q117 receipt headers (rev=/instrument=/instrument_sha256=/command=)
3a. Search: `grep -rIlE '^(rev|instrument|instrument_sha256|command)='` over the scratch tree and the round-61 wave tree. Hits: only the two tool copies in `S61MutationCounter/base/` (`souji-receipt-write.py` and `r60-receipt-write.py`). Those are source code, not receipts.
3b. Missing headers: none in any receipt, because no receipt exists yet in the wave dirs.
3c. Sidecars that would fail the rule if promoted: `/fast/scratch/hyaku/souji-r61/S61ScoutSources/s290-meta.txt` ("200 375834") and `s291-meta.txt` ("200 84442"). These are HTTP-fetch metadata (status and byte count) with no Q117 headers. Recommendation: the L1 must not deliver them as receipts. The two `.html` bodies next to them are web-fetch captures and are untrusted content.

## 4. Secrets
4a. Command: `grep -rInE '(op://|AKIA[0-9A-Z]{16}|xox[baprs]-|BEGIN [A-Z ]*PRIVATE KEY)' round-61/`. Exit 0 with hits, so the spec's own "must print nothing" condition is not met as written.
4b. Hit paths (no match content printed):
  - `.ufo/waves/round-61/make-spec.py` (line 366, the scan instruction)
  - `.ufo/waves/round-61/w1-spec.json` (line 55, the seat prompt)
  - `.ufo/waves/round-61/w1-dispatch.json` (line 171, the seat task)
4c. Per-pattern counts (`-c`) for `AKIA`, `xox[baprs]-`, and `BEGIN … PRIVATE KEY`: zero in every file. The only hit is the `op://` alternation, and the output of `grep -oE "op://.{0,4}"` shows only `op://|AKI`, i.e. the pattern text. No vault reference or credential value is present.
4d. Conclusion: false positives caused by the scan pattern appearing in the spec itself. Fix in the scanner: exclude `make-spec.py`, `w1-spec.json`, and `w1-dispatch.json`, or scan only seat delivery dirs.

## 5. pacman
5a. `/var/log/pacman.log` mtime 2026-11-04 17:33. Last entries: `2026-11-04T17:33:59-0300 [ALPM] installed anydesk-bin (8.1.0-2)`. No entry dated 2026-11-05, so no transaction ran after the wave started at 04:36.
5b. `/var/lib/pacman/db.lck` does not exist. `pgrep -a pacman` returned nothing (exit 1). `ps` for pacman/yay/paru/aur returned nothing (exit 1 for those patterns; only unrelated `dirmngr` and open-design processes listed).
5c. No wave file mentions `pacman -S`.
5d. Limit: this checks the host pacman log and process table only. Non-pacman installs (`uv tool`, `npx`, binaries in `~/.local/bin`) are not covered. `~/.local/bin` shows nothing newer than the spec. `uv` tool directories were not checked.

## 6. Other observations (low)
6a. `.ufo/waves/round-35/w1/` contains an ignored file with a malformed name (`ithdrawn (class ...`, looks like a shell-quoting artifact from an older round). Pre-existing, not round-61. Not touched.
6b. The spec's wave scan command is itself the only `op://` source. Recommend the scanner's pattern list live outside the scanned tree.

## Commands run (read-only)
- `find .ufo/waves/round-61 -newer SCORECARD.md -type f` and `find ... -printf` (mtimes, sizes)
- `git -C <lane> status --porcelain`, `git status --porcelain --ignored=matching`, `git diff --stat <base> -- <prod paths>`, `git ls-files -v`, `git rev-parse HEAD`, `git merge-base --is-ancestor`, `git log <base>..HEAD -- <prod paths>`, `git show <base>:<path> | cmp -`, `git ls-tree -r --name-only <base>`
- `grep -rInE` (secret scan), `grep -rIncE` per pattern, `grep -oE`, `grep -rIlE` (receipt headers)
- `ls`, `stat`, `cat`, `head`, `wc`, `cmp`, `lsof /tmp/alma.log`, `pgrep`, `ps`, `tail /var/log/pacman.log`
- Python `json.load` of `w1-spec.json` (read only)

No tool was installed. No files were written outside this seat's delivery file.
