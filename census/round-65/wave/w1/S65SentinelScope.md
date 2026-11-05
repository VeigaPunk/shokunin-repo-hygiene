# S65SentinelScope: round-65 instrument scope and safety audit

Seat: S65SentinelScope (leaf, no subagent dispatch). Lane tip read via `git rev-parse refs/heads/master` = 16da2445088ccca15aa32c66841d878ee57a8706. Writer blob at measured rev 40a371d8 is identical to tip (sha256 be344a7d…). Instrument hashes match the frozen claims: c1-counter.py 6401b35d…, c2-counter.py afd4cb54…, c1-matrix.tsv a521170c…, c2-statements.tsv 0291e1d3….

Deliver dir: `.ufo/waves/round-65/w1/S65SentinelScope/` (receipts, probe scripts, probe outputs). Scratch `/fast/scratch/hyaku/souji-r65/S65SentinelScope/` created, used, and removed.

## Reproductions (post-freeze, independent)

| Claim | Run | Result |
|---|---|---|
| C1 operability | `c1-counter.py --rev 40a371d8 --tool tools/souji-receipt-write.py --work <scratch>/work/c1 --receipt …/c1-sentinel-receipt.txt` | `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`. Every CASE row matches the matrix. Regress both slots `pass=8 fail=0`. Receipt header `instrument_sha256=6401b35d…`. |
| C1 do-nothing control | not run by this seat | out of my assignment |
| C2 calibration | `c2-counter.py --root . --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa… --rev 40a371d8…` | `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0` (…/c2-reproduction.txt) |
| C2 do-nothing | same with `--rev 4a43a4d9` | `findings=2 verdict=FAIL`, `EXIT=1` (…/c2-do-nothing-reproduction.txt) |

Note: `--tsv` must be repo-relative (the counter `git show`s it at `--tsv-rev`); the absolute form exits 2 with `C2-COUNTER-FATAL`. This is a usage pitfall, not a defect.

## Question 1: write scope

Code pointers:
- C1 counter: every write site is under `--work` or the explicit `--receipt`. `build_repo`/`build_case` (c1-counter.py:265-270, 296-299 via `case_dir=work/<letter>/<slot>`), `write_exec` (:459), slot and selftest dirs (:788, :805), `fixture_from_clone` clone to `work/laneref` (:473). The lane is read only via `git -C ROOT show` (:450) and `git clone --shared` (:473, clone source only). `clean_env` sets `GIT_OPTIONAL_LOCKS=0`. The counter refuses `--work` under /tmp, /var/tmp, $TMPDIR, or inside the lane root (main, ~L700).
- Writer (`tools/souji-receipt-write.py`): the only non-selftest writes are the `mkstemp` temp sibling in OUT's directory (:479), `os.link(tmp, out)` (:489), `os.unlink(tmp)`, and the stale sweep glob `<out>.*.tmp` in that same directory (:473-477). `git()` (:80-84) is read-only plumbing with `GIT_OPTIONAL_LOCKS=0`. Selftest writes are under `--work` only.
- Remaining write surface: `--receipt FILE` on the counter and `--out` on the writer are caller-chosen and unconfined. This is by design (records are committed under `census/`), but nothing stops `--receipt` naming a lane path; reviewers should treat that as an operator choice. Severity LOW.

Canary (filesystem before/after): no file was created in the lane, because the bounds forbid lane writes. The canary is the lane's existing metadata:
- Full lane tree snapshot (`find` path/size/mtime/inode/mode, `.git` excluded): 43130 entries before, 43138 after.
- The 8 additions and 1 modification are all in other seats' deliver dirs (`S65CriticClaims/`) or my own deliver dir. Lane source, census, tools, and `.ufo` state are unchanged.
- `.git` depth-2 snapshot before and after: zero differences. `.git/index` is byte-identical in mtime, size, and inode (`263118892`).

Verdict: no instrument call writes the lane. PASS.

## Question 2: secret-shape scan and the r21 privacy boundary

Frame (PROVINCE Round21, QUALITY Q49): the reason output must receive the shared secret-component patterns (`*.env`, `.env`, `.env.*`, `.envrc`, `*credential*`, `*secret*`, `id_*`, `*.pem`), be bounded to 160 bytes, and echo no secret-bearing argv beyond what the reason needs. A filesystem path is not secret-shaped by itself. It becomes secret-shaped when a component matches one of those families.

Findings:

- **F4 (MEDIUM) writer echoes the caller's env value unscrubbed.** `RECEIPT-INDEX-ENV-SET` prints `repr(os.environ['GIT_INDEX_FILE'])` verbatim (writer ~L276-278). Probe (`probe-secret-echo-output.txt`): with `GIT_INDEX_FILE` set to a 300-character path containing `id_rsa_secret_credential`, the writer emits a 497-byte stderr. Nothing is scrubbed or bounded at the writer. The value is a path, not a secret today, but the writer applies none of the Q49 patterns to it.
- **F5 (LOW) the 160 bound is the counter's, not the writer's, and it is per-stream characters.** `one_line(text, limit=160)` (c1-counter.py) caps each slot's stderr at 160 characters, so a `# detail` line carries two excerpts. Measured `# detail` lengths in `c1-sentinel-receipt.txt`: max 417 characters (N3 and P13). Q49 says "whole reason bounded to 160 bytes". The counter's bound does not match that wording.
- **Path persistence.** The excerpts keep a path prefix in committed records (e.g. `…/work/c1/N3/new/repo/.git/a...`). None of the frozen rows carries a secret-shaped component, so the frozen receipts contain none. The mechanism is still unscrubbed.
- **Raw argv.** The writer's refusal text does not echo argv (`--command` parse failure prints only `No closing quotation`, no token; probe-secret-echo-output). The wrapped argv does appear in OUT as `command=shlex.join(argv)` (writer ~L464), by design and only on accept. The counter's receipt `command=` line contains only paths, the rev, and the tool.

Verdict: NOT CLEAN for the r21 boundary at the writer. The counter's receipts are clean for this matrix.

Suggested named-limit wording:
- Writer, preferred: "RECEIPT-INDEX-ENV-SET names the variable only; its value is never echoed." Changing the refusal to name the variable and not its value removes the path from every reason, and fits the r21 boundary without a secret-pattern filter.
- Counter, if the value must stay: "Each slot's stderr is excerpted to its first 160 characters; the two excerpts together are bounded to 320 characters; excerpts are not scrubbed against the shared secret patterns; path prefixes may remain." Stated as a named limit, not as the Q49 bound.

## Question 3: host hygiene

- No instrument calls `sysctl`, `pacman`, `/proc`, `db.lck`, `os.system`, `shell=True`, `os.kill`, or `killpg`. Grep over both counters and the writer (`grep -nE`). The writer's only signal handlers (`signal.signal`, :1366-1367) are installed in its own process and only re-raise to its own exit path. `proc.kill()` (:419, :422) targets only the writer's own wrapped child. The counter's child processes are its own (`subprocess.run` timeouts 120/180/300/900s, no kill of foreign pids). The pacman pause is not observed or followed; no instrument touches pacman state.
- A sibling C1 counter process (`ReviewerC2`) was visible in `ps`. It is not mine; I did not signal it.
- Installs: none. No tools installed or upgraded by this seat.

**F1 (HIGH) caller-set git config defeats the untracked dirty check (not in frozen matrix).** The writer's `git()` (:80-84) scrubs only `GIT_DIR` and `GIT_WORK_TREE`. It refuses `GIT_INDEX_FILE` (r64) but passes `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, and `HOME`/XDG through. Probes (`probe-env-config.sh`, `probe-replace-excludes.sh`, outputs in `probe-env-output.txt`):

- Ordering: `-c status.showUntrackedFiles=all` WINS over `GIT_CONFIG_COUNT` injecting `status.showUntrackedFiles=no` and over `GIT_CONFIG_PARAMETERS` injecting the same key. Liveness: a plain `git status` under the injection is empty, so the injection is live. The writer refuses (`lane worktree is dirty`). So the `-c` override holds for this key.
- Bypass: the same route with `core.excludesFile` (injected by `GIT_CONFIG_COUNT`) makes an untracked file ignored. Plain status is empty and the writer ACCEPTS, rc 0, OUT written. Control without injection refuses. This is the class the writer's r65 C1 header claims closed ("so operator config cannot hide untracked entries"). It is not closed. The frozen V1 row covers the `showUntrackedFiles` key only, so the frozen claim passes while the header's general sentence is false.
- Independent confirmation: S65ScribeEntry measured the same residual with env, repo-local, and tracked `.gitignore` routes (accept in base and new). Received by message; recorded here as corroboration.

Verdict F1: HIGH. Probe: `probe-env-config.sh` / `probe-replace-excludes.sh`. Smallest remediation: in `git()` set `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, and `HOME`-independent, plus refuse (same posture as GIT_INDEX_FILE) any `GIT_CONFIG_COUNT`/`GIT_CONFIG_PARAMETERS`/`GIT_CONFIG_KEY_*` presence. Pin `-c core.excludesFile=/dev/null`. Alternatively reword the header to the key-only claim and record the ignore-source route as a named limit.

**F2 (MEDIUM) repo-local `.git/info/exclude` hides untracked content with no env involved.** Probe `p7-info-exclude`: plain status `[]`, writer `rc=0` accept. Requires write access to the lane `.git`. Same remediation family as F1 (pin the ignore sources, or refuse when `.git/info/exclude` names a dirty path).

**F3 (MEDIUM, requires `--allow-dirty` and `refs/replace` write) the instrument digest can be substituted.** Probe `p6b-replace-allowdirty`: committed instrument X, `refs/replace/X → Y`, worktree holds Y, `--allow-dirty` → writer `rc=0`, receipt `instrument_sha256=aea35bbe…` (Y's digest), while the committed blob is `8f513b9f…` (X). The worktree-vs-committed check (`cat-file blob`, :373-388) reads through replacement objects, so it compares against Y and passes. Without `--allow-dirty` the dirty tree refuses, so the attack needs the caller-accepted-dirty baseline. Remediation: `GIT_NO_REPLACE_OBJECTS=1` in `git()`, or `git --no-replace-objects` on the cat-file/ls-tree reads.

## Question 4: fixture identity

- C1 counter: fixture commits use repo-local `user.name=C1 Counter` and `user.email=c1-counter@invalid` (`git config` in `build_repo`, c1-counter.py ~L268-279 region). Those writes go only to `<fixture>/.git/config`; the lane config and global config are never touched by the counter. Toplevel is asserted equal to the fixture dir before the first commit.
- C2 counter: read-only `git show`; no fixture or config writes.
- Writer selftest fixtures use `GIT_ID` repo-local identity (`s60execrecorder@example.invalid`), also not global.
- **F6 (LOW) host global config is inherited.** `clean_env` does not set `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`. Host `~/.config/git/config` (keys seen: `rerere.enabled`, `commit.verbose`, `credential.https://github.com.helper`, `diff.*`, `init.defaultbranch`, `user.*`) applies to fixture git calls. No `core.hooksPath` is set, so no hook execution was observed. Remediation: isolate in `clean_env` (same as F1).

## Summary

| ID | Severity | Item | Status |
|---|---|---|---|
| F1 | HIGH | Caller-set GIT_CONFIG_* (core.excludesFile) defeats dirty check; not in frozen matrix | probe reproduced, control refuses |
| F2 | MEDIUM | `.git/info/exclude` hides untracked content (repo-local) | probe reproduced |
| F3 | MEDIUM | refs/replace on instrument blob + --allow-dirty substitutes digest | probe reproduced |
| F4 | MEDIUM | RECEIPT-INDEX-ENV-SET echoes env value unscrubbed (secret-shape pattern not applied) | probe reproduced |
| F5 | LOW | counter excerpt bound is per-stream characters (max 417/line), not Q49 "160 bytes whole reason" | measured |
| F6 | LOW | fixtures inherit host global git config (no GIT_CONFIG_GLOBAL isolation) | code + config read |
| F7 | LOW | `--receipt`/`--out` unconfined (by design; note) | code |

Frozen-claim status: C1 and C2 reproduce exactly. F1 to F3 are outside the frozen predicates and do not change C1's frozen counts (new_forgeries=0 holds because the frozen V1 row tests only the `showUntrackedFiles` key). F4 and F5 bear on the r21 privacy wording, not on the matrix. Operator/S65ScribeEntry: F1 should be recorded as a finding, not a named limit, because the writer header states the general claim.

Installs: none. Scratch removed. Deliver: `.ufo/waves/round-65/w1/S65SentinelScope/`.
