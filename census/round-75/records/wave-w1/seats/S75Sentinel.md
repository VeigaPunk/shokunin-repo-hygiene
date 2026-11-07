# S75Sentinel — W gate 1ad737b4 fail-closed / security review (r75 w1)

Verdict: the new block is fail-closed on every reachable error path and matches its frozen predicate on the 25 rows; it introduces no new exec or hang surface. Two equal-privilege bypasses it does not close: repo-local core.worktree (untracked payload -> check-clean=PASS) and the declared self-ignoring-.gitignore limit. Every claim number re-derived from committed blobs.

## Claim re-derivation (gate+writer copied from git; frozen invocation, cwd=lane root)
- base 52d3f07d gate sha 062b6d39: SUMMARY rows=25 mismatches=2 errors=0 rc=1 (f-info-exclude, f5-info-exclude-dir) — matches K-a.
- W 1ad737b4 gate sha 620ed97e (= c1-after receipt): SUMMARY rows=25 mismatches=0 errors=0 rc=0 — matches.
- K-b blanket variant sha e0d2e149: SUMMARY rows=25 mismatches=3 errors=0 rc=1 (f2,f6,f7) — matches; stays red.
- Novel coverage is info/exclude only: f3-repo-excludesfile already FAIL at base (writer pins core.excludesFile=/dev/null; writer sha identical base and W).
- Lane ignore delta (committed 5d10e09e): std=per=25993 then 26032 (seats writing), hidden=0; `.jj/.gitignore:1:/*` self-ignores.

## Route table (fresh fixtures; gate blob 620ed97e; log .ufo/waves/round-75/w1/S75Sentinel/probes.log)
| probe | verdict |
|---|---|
| info/exclude file and dir | clean-refuse (RECEIPT-UNTRACKED-LOCAL-EXCLUDE 1) |
| committed .gitignore *.pyc | ok (PASS) |
| HOME/XDG global ignore *.swp | clean-refuse via pre-existing pinned status (base gate identical) |
| GIT_CONFIG_GLOBAL / COUNT+KEY+VALUE / PARAMETERS | SKIP (scrubbed before first git call; file visible -> refuse) |
| repo core.excludesFile | clean-refuse (pinned status; already FAIL at base) |
| core.worktree=<pristine copy> + untracked payload | forged PASS (rc=0) — F1 |
| PATH shim logging argv / shim exit-0 for ls-files | EXEC / forged PASS — F3 |
| alias.ls-files=!cmd; core.hooksPath; core.fsmonitor=<script> | SKIP (builtin wins; no hooks; block pins fsmonitor off, hook runs only unpinned = pre-existing) |
| git rc!=0 for --others; safe.directory | clean-refuse ("ignored-file listing failed"; safe.directory not testable without chown, same rc path) |
| ANSI+newline filename under info/exclude | ok (count only; 0 ESC bytes; no injected check line) |
| untracked self-ignoring .gitignore payload | ok (declared limit) |
| info/exclude dir + non-self-ignoring .gitignore | clean-refuse (1: the .gitignore itself) |
| FIFO .gitignore inside committed-ignored dir | ok (not opened; gate PASS) |
| 200k ignored files + depth-2000 chain | ok (gate 0.87 s / 82 MB / PASS; depth 2000, pathlen 4068) |
| root or plain-dir FIFO .gitignore | HANG (rc=124; base gate 124 too; no timeout anywhere) |
| status.showUntrackedFiles=no; core.excludesFile=dir | clean-refuse (cmdline -uall wins; status fatal) |

## Findings
- MEDIUM F1 (pre-existing, inherited by W): `git -C lane` honours repo-local core.worktree, so both new listings and the status describe a substituted worktree; a lane with an untracked payload reads check-clean=PASS (W gate rc=0; base gate rc=0). Same privilege as the info/exclude route the round models. Smallest fix: `--work-tree="$lane"` on every gate/writer git call (tested: then status prints `?? payload.txt`); `-c core.worktree=` does not override (tested).
- LOW F2: the declared limit is broader than "the .jj/.ruff_cache shape": any untracked self-ignoring .gitignore anywhere hides arbitrary content (probe M PASS). Claim accurate; the block cannot be a seat trust boundary.
- LOW F3: the new subprocess resolves `git` via PATH (4 ls-files calls logged); a shim exiting 0 for ls-files yields PASS. Nil delta (python3 and the parent git are PATH-resolved too).
- LOW F4: HOME/XDG global excludes over-refuse an untracked swap file, but the base gate already refuses it (pinned status); no W regression.
- INFO F5: FIFO .gitignore at the root or in a plain dir wedges the gate forever (no timeout); base identical; block adds no hang.
- Observation: at read time worktree gate sha ef3b04e4 (9+/1-) != 620ed97e and the lane carried M corpus/SOURCES.md, M corpus/knowledge/filter-filemode-witness.md: the domain trial is not reproducible from the worktree; bind the committed blob.
Files: .ufo/waves/round-75/w1/S75Sentinel.md; .ufo/waves/round-75/w1/S75Sentinel/{probes.log,probe-core.sh,probe2.sh,probe3.sh,probe4.sh}. Tooling: none installed.
