# S68Sentinel — round-68 counter & fixture security/scope audit (read-only) — 2026-11-05

Full audit (write-path table, clean_env table, sha256 results, classified findings):
.ufo/waves/round-68/w1/S68Sentinel/sentinel.md

Verdicts: Item 1 writes contained PASS · Item 2 no-/tmp + W4/W5/PK6 containment PASS (exception: caller-named --receipt unvalidated, by design) · Item 3 clean_env frozen-tuple PASS, gaps named · Item 4 frozen bytes + chronology PASS · Item 5 W5/W6/alias-symlink PASS · Item 6 findings below.

Findings:
- MEDIUM-1 c1-counter.py:400-413 (vs 431-624): HOME/XDG_CONFIG_HOME unscrubbed — counter's own fixture-build git calls (init 431, add 455, commit 458, update-index 471/504/599/622, hash-object 591, read-tree 596, write-tree 603, commit-tree 608, update-ref 616) still read ambient on-disk global/system git config; ambient core.hooksPath/core.fsmonitor can execute and mutate fixture bytes, steering C1/C2 verdicts with zero frozen-byte changes. Writer children protected by writer's own NOSYSTEM/GLOBAL=nulldev pins. Smallest remediation: clean_env sets GIT_CONFIG_GLOBAL=os.devnull + GIT_CONFIG_NOSYSTEM=1 (behavior-neutral; identity/dates pinned repo-locally 437-438/454, env 607-611).
- LOW-1 400-413: GIT_TRACE*/GIT_TRACE2* unscrubbed; path-valued trace = git-appended writes outside --work (verdict-neutral). Strip GIT_TRACE-prefixed keys.
- LOW-2 170-173, 189-191 vs 812-825/1145-1146: stale docstring claims a lane `git clone --shared` regress arm; r68 code reads the fixture from the --base-rev blob, no clone exists (grep: docstring-only). Drift overstates writes; frozen file, report-only.
- LOW-3 400-413, 1100-1102: GIT_DISCOVERY_ACROSS_FILESYSTEM unscrubbed; --work checked only against --root, not any enclosing foreign work tree (cwd-sensitive W4 863 / W5 864-866).
- INFO-1: f70da577… is a commit (`git cat-file -t`), preregistration calls it "blob"; commands unaffected (--rev semantics, git_show rev:path 817/1125).
- INFO-2: --receipt (1082, 980, 1170-1177) caller-named, unvalidated; receipt embeds absolute argv (1171-1172) — operator paths in lane receipts (privacy).
- INFO-3: probes/ and records/ under census/round-68 are empty, untracked, status-clean; freeze binds tracked bytes.

Key evidence: sha256 working tree = ab3ac5c7… / bb56e69a… / 23e19b8e… ✓; SHA256SUMS content = candidate b811ee2a… + 14 mutants, and all 14 reproduce byte-identically from candidate writer bytes via frozen mutate-writer.py (diff EMPTY, "BATTERY-DERIVATION-MATCH"); `git diff --stat 8b393b19… -- census/round-68` EMPTY; `git status --porcelain census/round-68` clean; worktree writer == commit f70da577 writer == b811ee2a…; f70da577 is the last commit touching the writer (r67 landing); 8e4e84cc and 485e370d are ancestors of 8b393b19 (merge-base --is-ancestor); W6 alias symlink target = realpath(fixture repo/.git) under --work (555-556), never the lane's; PK6 objects/refs/replace written only inside the scratch fixture (git -C repo, 591-624).

Commands: read-only git (cat-file, show, diff --stat, ls-files, status --porcelain, log, merge-base --is-ancestor, check-ignore), sha256sum, mutate-writer derivation into scratch, disk-guard status (green: /fast/scratch/hyaku 50%, 405.8G free). No counter run, no lane write, no git mutation.

Files written: .ufo/waves/round-68/w1/S68Sentinel/sentinel.md; .ufo/waves/round-68/w1/S68Sentinel.md; scratch /fast/scratch/hyaku/souji-r68/S68Sentinel (deleted before yield). No tool installs.
