STATUS: DONE — D2 partial: hostile FIFO/socket/hardlink cases degrade per repo, never open, and never hang, but the landed classifier adds two whole-run false-refusal regressions (empty files and translated stat output). There is also a TOCTOU hang and a dot-admin hang.

Seat: SoujiR17-3.SentinelCensusD2-2 · surface: tools/souji-census.sh D2 path at ddb73474433977ff54b015ac3e77669ff2537353 · axis: operability.
Code under test: `git -C <lane> show ddb7347:tools/souji-census.sh` copied to /var/tmp/souji-r17-SentinelCensusD2/tool/tools/ (sha256 688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59, blob 8ad60987b5e8…). Base copy from 5fa6017 for regression checks. Every census run used `timeout 120` or less, on synthetic repos under /var/tmp/souji-r17-SentinelCensusD2/ only. Host versions: git 2.56.0, bash 5.3.20, GNU coreutils stat 9.12. No tools were installed. The scratch directory was deleted after this report.

## Findings

### F1 — MAJOR (operability; regression introduced at ddb7347): a zero-length metadata file is classified as non-regular
- Location: tools/souji-census.sh:549 `kind=$(stat -L -c '%F %h' …)` and :554 `'regular file')`. GNU `%F` prints `regular empty file` for a zero-size file, so the `*)` arm treats it as non-regular. Base 5fa6017 used `[ -f "$path" ]`, which accepts an empty file.
- Observed at ddb7347 (fleet = target repo + benign neighbour):
  - empty `info/attributes` (A7) → rc 0, target row `error`, stderr `git-metadata-unsupported git-metadata-nonregular …/info/attributes`. This is a false degradation.
  - empty `info/attributes` in a linked-worktree admin dir (B7) → rc 0, `error` row.
  - empty `info/exclude` (A8) → **rc 2**, `path-protected: git-metadata-nonregular (…/.git: …/.git/info/exclude)`. Whole run lost.
  - empty `packed-refs` (A9) → **rc 2**, same reason.
  - empty `config` (B5) → **rc 2**, same reason.
  - empty `objects/info/alternates` (B6) → **rc 2**, same reason.
- Base 5fa6017 on A7/A8/A9: rc 0 with no stderr. This is a regression.
- Exploit or trigger path: any `: > .git/info/exclude` or truncation of config or alternates, or an init template that ships empty files. Git itself never writes these files empty: an empty `pack-refs` still writes a 46-byte header (checked). That is why the selftest (49/0) misses it.
- Live exposure: nil at this moment. I ran `stat -c '%s|%F|%h|%n'` over the 8 guarded names in 21 fleet gitdirs plus their worktree admin dirs: 110 files, 0 empty, 0 non-regular, 0 hardlinked.

### F2 — MAJOR (operability; regression): `%F` is gettext-translated, so a non-English message locale refuses the whole fleet
- `LANGUAGE=de LC_ALL=en_US.UTF-8 /usr/bin/stat -c %F <regular>` prints `reguläre Datei`.
- On a fully benign fleet (A11): rc **2**, `path-protected: git-metadata-nonregular (…/t-target/.git: …/.git/config)`. Base 5fa6017 under the same environment: rc 0, both rows `clean`. Every repo's `config` hits the `*)` arm.
- The script never sets LC_ALL or LANG (grep shows only `LC_ALL=C sort` at :1384 and :1519).
- Live exposure: nil today. LANGUAGE is unset, and only C/C.utf8/en_US.utf8/POSIX locales are installed.
- The in-repo convention already handles this: tools/souji-quarantine.sh:159 `export LC_ALL=C`, and q_special_type at :798-800 matches `'regular file'|'regular empty file'|directory`.

**Smallest fix for F1+F2** (two lines): at :549 use `kind=$(LC_ALL=C stat -L -c '%F %h' -- "$path" 2>/dev/null)`, and at :554 use `'regular file'|'regular empty file')`.

I checked this on a patched copy:
- A7, A8, A9, B5, B6, B7 and locale-de all give rc 0 with both rows `clean`.
- A4 (FIFO), A5 (socket), A3b and B1 still give per-repo `error` rows.
- A10 (hardlinked config) and B4 (hardlinked alternates) still give rc 2.
- `bash -n` and `shellcheck -S warning` are clean.
- I did not run the selftest on the copy, because it writes outside my scratch directory. L1 should run `--selftest`.

### F3 — MEDIUM (operability; TOCTOU is a real, exploitable DoS by any concurrent writer to the repo's .git): a FIFO swapped in after the guard's stat hangs the census
- Window: guard_git_files stats the file at :549. The later `git status` at :1115 (and `ls-files | check-attr` at :1078-1085 when filter drivers exist) opens `$GIT_DIR/info/attributes` with a blocking `open(2)`. There is no timeout around any git call (no `timeout` occurs in the script).
- When git reads the file: `git status` reads info/attributes whenever a tracked file is stat-dirty but the same size, because it compares content. Because the census uses `--no-optional-locks`, it never refreshes the index, so such a file stays stat-dirty on every run. Direct check: a FIFO info/attributes on a racily-clean index → `git status` rc 124 (5 s cap), and a same-size touched file → rc 124. A size-changed file gives rc 0, because git does not read attributes in that case. Control: `git check-attr -a` with a FIFO common info/attributes → rc 124 at 10.00 s.
- Race harness: a python loop atomically `rename(2)`s a FIFO or a regular file over info/attributes every 2 ms. The repo has a stat-dirty same-size tracked file. Per-trial cap 20 s.
  - Landed: `SUMMARY trials=10 hang(rc124)=1 soft-error-row=6 measured=3`. The hang trial gave rc 124, t=20.00 s, **0 bytes stdout and 0 bytes stderr**: rows are buffered until the end (:1397 `rows+=`, :1407 print), so one hung repo erases the whole fleet's census. Without an external timeout it never returns.
- Impact: availability only.
  - A writer who also feeds the FIFO only gets git to read attributes they could have written as a regular file anyway. That is the documented non-atomic guard/use residual (header "the guard and the later access are not one atomic operation"), not new.
  - No leftover processes after the timeout kills the run.
- Smallest fix: run the status call at :1115 and the `ls-files | check-attr` pipeline at :1078-1085 as `timeout --kill-after=5 <N> git …`, and map a timeout to the existing `unverifiable` path.
  - Checked on a copy with N=5 (status call only): `SUMMARY trials=12 hang(rc124)=0 soft-error-row=5 measured=7`. Three of those trials returned `status-unverifiable` in about 5.15 s each, instead of hanging.
  - N=60 is a reasonable production value.

### F4 — MEDIUM (operability; existing before this round — the base has the same glob at :768 — but it reaches the D2 surface): dot-named worktree admin dirs escape every admin guard
- Location: :842 `for entry in "$dir"/worktrees/*` (dotglob off, and the script never sets dotglob). Git lists dot-named admin dirs: `git worktree list` showed `wtdot` with admin `.git/worktrees/.wtdot`.
- FIFO at `.git/worktrees/.wtdot/HEAD`: census rc **124 at 30.00 s** with no output, both landed and base. `count_worktrees` (:993, `git worktree list`) blocks on the FIFO. Non-dot control (`wtdot2`): rc 2 in 0.10 s, `git-metadata-nonregular … wtdot2/HEAD`.
- D2-specific case: a FIFO `info/attributes` in the dot admin dir → landed rc 0, main row `clean,wt-dirty`. Git runs in the repo, which breaks the "no git call … runs in it" wording. It is caught only later by worktree_extra_flags. That case is harmless, because git does not read admin info/attributes.
- Trigger: needs a manual rename or a hostile writer. `git worktree add …/.wt` sanitizes the name to `-wt` (observed).
- Smallest fix: `for entry in "$dir"/worktrees/* "$dir"/worktrees/.[!.]* "$dir"/worktrees/..?*; do`. Unmatched patterns stay literal and fall through the existing `[ -d ]` test.
  - Checked on a copy: FIFO HEAD → rc 2 `git-metadata-nonregular (…/.wtdot: …/.wtdot/HEAD)`; FIFO admin info/attributes → rc 0, row `error`.
  - `bash -n` and shellcheck are clean.

### F5 — LOW (the claim is more precise than the behaviour): symlink loops and out-of-gitdir symlinks refuse the whole run, not per repo
- A2 self-loop `attributes -> attributes`: rc 2, `path-protected: symlink-loop (path: …/.git/info/attributes)`.
- A2b pair loop: rc 2, same.
- A3 symlink to a FIFO outside the gitdir: rc 2, `path-protected: git-metadata-symlink (…/.git: …/.git/info/attributes)`.
- Cause: guard_git_links (:906) runs before guard_git_files (:907), and resolve_guarded aborts at hop 41.
- The result is fail-closed and the FIFO is never opened. But the header text (:103-104, "or a symlink resolving to one") holds only for targets inside the gitdir. A3b (`attributes -> ../fifo-in`): rc 0, `error` row. A3c (dangling symlink inside the gitdir): measured `clean`, as documented.
- Smallest fix: change the doc wording to "a symlink resolving to one inside the gitdir; a looping or out-of-gitdir symlink keeps the whole-run symlink-loop/git-metadata-symlink refusal". Making these soft would need to preserve the protected-reach exit 2, so I do not recommend that in this round.

### F6 — LOW (over-refusal, fail-safe): an admin-dir info/attributes degrades a repo that git never reads it from
- B1 (hardlink, worktree inside the fleet root), B2 (FIFO, worktree outside the root), B3 (hardlink, outside) all give rc 0, main row `error`, and one stderr `git-metadata-unsupported … worktrees/<name>/info/attributes`.
- Linked worktrees read the common `info/`, not the admin one: `git check-attr -a base.txt` in the B2 worktree with the FIFO admin file → rc 0, 0.00 s.
- No fix required. Note it in the doc if exactness matters.

### F7 — LOW (scaling): linear, does not hang, all-or-nothing output
- FIFO-attributes repos (empty template, `cp -a`):
  - N=10: rc 0, 0.75 s.
  - N=100: rc 0, 6.37 s.
  - N=1000: rc 0, 62.91 s.
  - At each N, rows = error rows = stderr diagnostics = N, with 0 other stderr lines.
- About 63 ms per bad repo, compared with 124 ms per benign repo (benign N=100: 12.44 s, all `no-remote`). D2 does not amplify the cost.
- N=10000: rc **124 at 120.00 s, 0 bytes stdout, 0 bytes stderr**. The list_repos guard pre-pass alone (about 31 ms per repo) runs past 120 s, and rows and diagnostics are only emitted later.
- Not relevant for 22 repos. Same buffering cause as F3.

## Holds (observed, landed ddb7347)
| case | rc | target row | stderr |
|---|---|---|---|
| A0 benign | 0 | clean | — |
| A1 info/attributes is a directory | 0 | clean | — |
| A3b symlink → FIFO inside gitdir | 0 | error | `git-metadata-unsupported git-metadata-nonregular …/info/attributes` |
| A3c dangling symlink inside gitdir | 0 | clean | — |
| A4 FIFO | 0 | error | `… git-metadata-nonregular …/info/attributes` |
| A5 AF_UNIX socket | 0 | error | `… git-metadata-nonregular …/info/attributes` |
| B1/B3 hardlinked admin info/attributes (worktree in/out of root) | 0 | error | `… git-metadata-hardlink …/worktrees/<n>/info/attributes` |
| B2 FIFO admin info/attributes | 0 | error | `… git-metadata-nonregular …/worktrees/B2/info/attributes` |
| B4 FIFO admin attrs + hardlinked common alternates | 2 | — | `path-protected: git-metadata-hardlink (…/.git: …/objects/info/alternates)` |
| A10 hardlinked attrs + hardlinked config | 2 | — | `path-protected: git-metadata-hardlink (…/.git: …/.git/config)` |

- In every rc 0 row above, the neighbour repo `z-benign` stays `clean`, and there is exactly one stderr line per degraded repo.
- Never-open witness (B8, FIFO attributes): a writer-side `O_WRONLY|O_NONBLOCK` probe polled every 0.5 ms during the run → `tries=974 reader_opens_seen=0`. The census run took 0.25 s, rc 0.
- Base 5fa6017 on A4/A5: rc 2 whole run. D2's improvement holds for these cases.
- Round-1 A6/A6c were mis-built: I hardlinked `info/exclude` itself, which correctly gives rc 2 on exclude. B1/B3 replace them.

## Verdict
D2 is **partial** on operability.
- Holds: per-repo degradation for FIFO, socket, symlink to FIFO inside the gitdir, and hardlinks in the repo gitdir and in admin dirs; never opened; never hangs on static content; the exit-2 neighbours keep refusing.
- Fails: F1 and F2 are regressions introduced at ddb7347 that turn benign shapes (an empty file, a German message locale) into whole-run rc 2.
- Fails: F3 (TOCTOU) and F4 (dot-admin bypass) still allow an unbounded hang with total loss of output.

Fix order: F1+F2 (2 lines) → F3 (timeout on status and check-attr) → F4 (1 line) → F5 doc wording.

## Commands run (abridged; full outputs quoted above)
- `git -C <lane> show ddb7347:tools/souji-census.sh` (sed ranges 90-200, 399-660, 812-1130, 1200-1420); `git diff 5fa6017 ddb7347 -- tools/souji-census.sh`; `git show ddb7347:tools/souji-quarantine.sh | sed -n 790,815p`.
- `/usr/bin/stat -c '%F'` probes, including the `LANGUAGE=de` translation check; the live fleet `stat` over the exact named metadata files (110 files).
- `/var/tmp/souji-r17-SentinelCensusD2/harness.sh` (A0–A11), `harness2.sh` (B1–B8, witness, git-reads-admin check), `race.sh` (TRIALS=10 landed; TRIALS=12 patched), `scale.sh 10 100 1000` and `scale.sh 10000`, the dot-admin script.
  - Every census invocation was `timeout ≤120 <copy> --root <synthetic fleet>`.
- `bash -n` and `shellcheck -S warning` on the patched copy: clean.
