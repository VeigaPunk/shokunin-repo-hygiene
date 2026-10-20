# BoundaryReviewScratch — round 14, w1

Seat: SoujiR14.BoundaryReviewScratch (reviewer, leaf). Lane: souji-shokunin.
Target: `tools/souji-census.sh` — `.scratch` symlink handling, nonregular
descendants, `newest_mtime` traversal; separation of name metadata from content
reads. Goal: concrete accidental credential access, routed to CensusBoundary.

## Evidence basis

- **Code inspection only.** `tools/souji-census.sh` (827 lines, read in full),
  `AGENTS.md`, `PROVINCE.md`, `~/.omp/agent/RULES.md`. No script was executed and
  no fixture was built, per the seat contract.
- **Exercised evidence: none.** Every behavioural claim below is an inference from
  reading the code, flagged `[INFERENCE]` where it depends on git or find internals.
- **Tools installed or upgraded by this seat: none.** GNU find/du/readlink and git
  are the only tools the script uses; no install was needed for review.
- Credential-store roots are not defined anywhere in the repo. PROVINCE.md:31
  says souji "never reads secret content" and :44 routes credential-shaped
  findings to kagi-shokunin; :32-33 refuses `~/.config/**`. The concrete root list
  is for CensusBoundary to fix. I did not open `~/.omp/agent/` beyond RULES.md.

## Name metadata vs content reads (script as it stands)

| Call | Site | Class | Notes |
|---|---|---|---|
| `readlink -m` (`canon_path`) | L95 | name metadata | Resolves symlinks in the path string; no content read. Canonicalises *into* a symlink target, see F3. |
| `[ -L ]`, `[ -d ]`, `[ -e ]` on `.scratch` | L142-144 | name metadata (lstat/stat) | `-d` follows symlinks, but `-L` is checked first. TOCTOU window between check and `du`; minor. |
| `du -sb -P -- "$d"` | L147 | name metadata | Stat-only, `-P` does not follow symlinks inside `.scratch`. No content read. FIFOs/devices are lstat'd, not opened. |
| `find . -prune ... -o -type f -printf '%T@ %P\0'` | L165-167 | name metadata | `-P` (default) does not descend symlinked dirs; `-type f` excludes symlinks, FIFOs, sockets, devices; `%T@` is taken from lstat. Nothing is opened. |
| awk `secret_path` on `%P` | L168-193 | name metadata | Classifies names only. Output carries mtime + `ok|secret-shaped`, never names or bytes. |
| `git worktree list [--porcelain]` | L109, L235 | git metadata | Reads `.git/worktrees/*` registration files, not work-tree content. |
| `git rev-list --count` / `for-each-ref` | L115-123 | git object/ref metadata | Object DB and refs only; no work-tree file reads. |
| `git -C repo status --porcelain -- .` | L131 | **content read** | For a tracked file whose stat differs from the index (or is racy), git hashes its content to decide modified-or-not. **This is an open()+read of working-tree bytes**, including tracked secret-shaped files. See F1. |
| `git -C wt status --porcelain` on linked worktrees | L231 | **content read** | Same mechanism, in a path taken from `worktree list`. See F2. |
| `git ... status` untracked listing | L131 | name metadata | Untracked files are listed by lstat; git does not read their bytes for status. `[INFERENCE]` for default untracked mode. |

Conclusion: the only **content** reads in the script are the two `git status`
calls. Everything else is name, stat, or git-internal metadata. The header's
claim (L4, L39-40: "never reads secret-shaped files", "File contents are never
opened") is accurate for `newest_mtime` and `du`, and false for `git status`.

## Findings (ordered by severity)

### F1 — HIGH (content read, contract violation): `count_dirty` hashes tracked secret-shaped files

- Site: `count_dirty`, L131-132:
  `git --no-optional-locks status --porcelain -- . ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log'`
- Only `.ufo/state` and `.ufo/watchdog.log` are pathspec-excluded. A tracked
  `.env`, `credentials.json`, `id_ed25519`, `*.pem`, etc. is not. If its stat
  info drifts (touch, editor save, checkout, `mtime` change), git reads it and
  computes its blob hash. That is an accidental content read of a secret-shaped
  file, and it happens on every census run where the stat is stale.
- Output is unaffected (no bytes printed), so the selftest "secret file contents
  absent" check (L683-688) cannot detect it. The selftest checks output only. The
  calibration gap is that the contract claim is untested.
- `[INFERENCE]` git refreshes and hashes only pathspec-matched entries; the
  exclude-pathspec pattern is therefore a plausible way to keep secret-shaped
  paths out of the hash. L1 must verify with a spy or `strace -e openat` on a
  fixture (not run by this seat).
- Recommended fix (C2 owns): (a) exclude secret-shaped tracked pathspecs from the
  main `status` call with `:(exclude,glob)**/.env*` etc. mirroring `secret_comp`;
  (b) enumerate tracked secret-shaped paths with `git ls-files -z` (index only,
  no hashing) and set a flag (e.g. `secret-shaped`, already defined) plus drop
  `clean`, so the census does not report a false clean; (c) keep secret-shaped
  *untracked* names counted by name only (`git ls-files --others -z`). A tracked
  secret file that is modified is then reported as unverified rather than read.
- Severity note: real but bounded. It needs a tracked secret-shaped file and a
  stat drift. The contract breach is unconditional in principle.

### F2 — HIGH (boundary): linked-worktree paths reach `git status` unchecked

- Site: `worktree_extra_flags`, L216-240. `path` comes from `git worktree list --porcelain`
  (a file under `.git/worktrees/*/gitdir`); it is canonicalised only for the
  "is this the main tree?" comparison (L225-226). It is then passed straight to
  `count_dirty` (L231) with only `[ -d "$path" ]` (L227, follows symlinks).
- A registration pointing at a credential-store directory, or through a symlink
  into one, causes `git -C <cred-dir> status` (content read per F1 and name
  enumeration). If the target is not itself a git repo, git walks up and may
  status an enclosing repo, including `$HOME` if it is a repo.
- Fix: canonicalise `path` and refuse credential-store overlap before `count_dirty`;
  record `wt-refused` (new flag, or existing `error`) and do not call git there.

### F3 — MEDIUM (boundary, contract): repo-root symlinks are followed

- Site: `list_repos` L324-335 (`"$root"/*/` glob, `[ -d "$d" ]`,
  `[ -d "${d%/}/.git" ]`) and `census_one` L245 (`canon_path`). A child of the
  root that is a symlink to a directory with a `.git` directory is accepted; its
  canonical target is then used for every git and find call.
- The round-14 contract says "never follow repo-root or .scratch symlinks into
  credential store." The current code does follow repo-root symlinks.
- Fix: in `list_repos`, skip (or flag) any `"$root"/<child>` that is `-L`; compare
  canonical targets against credential roots before any git or find call.

### F4 — MEDIUM (operability, not access): symlinked `.scratch` is silent

- Site: `scratch_bytes` L142-143 returns `0` for a symlink and `newest_mtime`
  (L165-167) never descends it or counts it (`-type f`, `-P`). The access behaviour
  is correct: nothing is followed or read.
- But the census gives no flag for it, so a `.scratch -> <anywhere>` link is
  invisible in the verdict. An operator cannot tell a symlinked `.scratch` (possibly
  pointing into credential store) from an absent one.
- Fix: emit a flag (`scratch-symlink`) and do not call `du` or `find` through it.
  Keep the existing zero-byte behaviour.
- `[INFERENCE]` `-L` on `.scratch` followed by `du` is a short TOCTOU window; the
  flag fix removes the reliance on the check ordering.

### F5 — LOW (calibration): credential classification is name-component only and incomplete

- Site: `secret_comp` L170-178 and `secret_path` L179-183. Matches `.envrc`,
  `*.env`, `.env.*`, names containing `credential|secret`, `id_*`, `*.pem`.
- Not matched: `.netrc`, `.npmrc`, `.pypirc`, `.git-credentials` (only via
  `credential`), files under `.ssh/`, `.gnupg/`, `.aws/`, `.kube/`, `.docker/`,
  `.config/gh/`, `.password-store/`. Those files' mtimes are counted into
  `mtime_iso` and are not flagged. This is name metadata only; no bytes are read,
  so it is calibration, not access.
- Fix: add directory-component rules (`.ssh .gnupg .aws .kube .docker .password-store`)
  and file rules (`.netrc .npmrc .pypirc`), and treat a match as excluded from the
  max as now.

### F6 — LOW (confirmed safe, recorded for L1): nonregular descendants and symlinks inside the tree

- `find` is `-P` by default and filters with `-type f` before `-printf`. FIFOs,
  sockets, devices and symlinks are neither opened nor stat-followed.
- `du -P` does not follow symlinks inside `.scratch`.
- Untracked FIFO/socket in the tree: git lists it as untracked from lstat;
  `[INFERENCE]` git does not open it for `status`. Tracked-to-FIFO type change:
  `[INFERENCE]` git's `ie_match_stat` classifies it as a type change before any
  data read. Both are L1 spy checks, not verified here.
- No finding. Recorded because the seat was asked to distinguish these cases.

### Not a finding

- `canon_path` (`readlink -m`) resolves path strings only. It reads symlink
  targets (metadata) and does not open them.
- `git rev-list` and `for-each-ref` read object/ref metadata only.

## Concrete credential access (the target's question)

One concrete accidental content read exists: **F1** (`git status` hashing tracked
secret-shaped files on stat drift). The second content path is **F2** (git status in
an unchecked linked-worktree path, which can land in the credential store). Neither
prints bytes. Both break the "never reads" contract.

Notified CensusBoundary (SoujiR14.CensusBoundary) with F1-F4 summaries.

## Final L1 commands (not run by this seat)

Run after all round-14 seats land, in this order, from the lane root:

1. `bash -n tools/souji-census.sh` — syntax only.
2. `tools/souji-census.sh --selftest` — must exit 0 after C2 edits.
3. `tests/fixtures/r14-census-boundary.py` (C2 fixture) — must include:
   a. `.scratch -> <synthetic cred root>` symlink: no `du`/`find` call through it;
      `scratch-symlink` flag present.
   b. repo-root symlink to a dir with `.git`: refused before any git call.
   c. linked worktree registered at a synthetic cred root: refused before `status`.
   d. tracked `*.env` with stat drift: command spy or `strace -f -e trace=openat`
      shows no open of that file during `status`; row reports `secret-shaped`, not
      `clean`.
4. Spot-check F1 mechanism on a synthetic repo in `/var/tmp` (only if L1 chooses,
   with `strace -e openat`): confirm the pathspec-exclude keeps the tracked
   secret file out of `git status` opens. This is the `[INFERENCE]` in F1.
5. `shellcheck tools/souji-census.sh` if available (not installed by this seat).

Cleanup: all fixtures under `/var/tmp` must be removed by the harness; none were
created by this seat.

## Residual risk / verification gaps

- F1 pathspec-exclude behaviour and F6 FIFO/type-change behaviour are git
  internals and are unverified here (`[INFERENCE]`).
- Credential-store root list is not defined in the repo; C2 must choose it.
- Selftest cannot detect content reads (it checks output only). Only a spy or
  `strace` check can.

## C2 re-review (static parse of landed tools/souji-census.sh, sha256 2cf44ee9…, 1458 lines)

Code inspection only. Nothing executed; no fixture, selftest, strace, or census run by this seat.
Lines are from the landed file at the read above; re-verify after any further edit.

| Finding | C2 status | Evidence (landed file) |
|---|---|---|
| F1 HIGH: `git status` hashes tracked secret-shaped files on stat drift | **NOT FIXED — disclosed only.** Header L6-9, L45-46 now says `git status` may read/hash tracked content. Pathspec excludes are unchanged in substance: only `.ufo/state`, `.ufo/watchdog.log`, and `census/operator-sweep-*`. No tracked secret-shaped exclusion and no `git ls-files` path. | `count_dirty` L625-640 |
| F2 HIGH: linked-worktree paths reach `git status` unchecked | **FIXED.** Path is rejected on `\n`/`\t`/`\r` (L730), resolved by `guard_target worktree` (L732, refuses protected prefixes, follows symlinks), skipped when a `.git` symlink or missing `.git` (L738-748, no git call), and passed through `guard_git_surface` before `count_dirty` (L749-750). | `worktree_extra_flags` L720-759 |
| F3 MED: repo-root symlinks followed | **FIXED.** Symlink children skipped at L871 after a lexical protected check (L867); a symlink `.git` is guarded and not emitted (L874-877); include-root is gated on a non-symlink raw root (L844). | `list_repos` L840-890 |
| F4 MED: symlinked `.scratch` silent | **Access half FIXED; visibility half NOT FIXED.** `-L` is tested before `-e` (L644), so no stat/du through the link. No `scratch-symlink` flag exists, and fixture R14C2-08 expects rc 0 with `scratch_bytes` 0 and no flag, so the silence is now encoded as expected behaviour. | `scratch_bytes` L642-655 |
| F5 LOW: name-only credential classes incomplete | Not expanded (L1 decision per CensusBoundary.md:164-166). Accepted as residual. | `secret_comp` L674-682 unchanged |
| F6 (confirmed safe): nonregular and symlink descendants | Still safe. `find -P` (L667) with `-type f` before `-printf` (L671); `du -P` (L649). Operator-sweep prune added at L668-670. | `newest_mtime` L661-716 |

New, LOW (operability): `count_dirty` and `newest_mtime` silently exclude `census/operator-sweep-*` from the dirty count and mtime max, with no flag. This is deliberate, but an operator cannot see that a dirty tree was excluded. Suggest an `operator-sweep-excluded` note or accept it in the header.

Contract tension (for L1): PROVINCE.md:31 still says souji "never reads secret content", and AGENTS.md:10 says "never touch credentials." The landed header now says the opposite for `git status`. The tool no longer lies, but the province invariant is unreconciled. This is the open decision: exclude tracked secret-shaped pathspecs (and report them via `git ls-files` as `secret-shaped` without `clean`), or amend PROVINCE.md to accept the read.

Not re-read by this seat: guard helpers L396-520, `census_one` body L762-838 beyond the guard calls, `emit_census`/`emit_compare` L892-1002. Not verified: pathspec glob semantics for `:(exclude,glob)census/operator-sweep-*` (single level, nested form covers deeper) `[INFERENCE]`.

Final L1 checks for these findings (not run here):
1. `strace -f -e trace=openat -o /var/tmp/… tools/souji-census.sh --root <synthetic>` with a tracked `.env` whose mtime is touched: confirm whether `git status` opens it (F1 is open until this is shown either way).
2. Fixture R14C2-08 plus a new case: `.scratch -> <synthetic store>` must still produce no `du`/`find` path through the link, and should emit a flag if the decision is to add one.
3. Worktree registration at a synthetic store path: confirm refusal before any `git -C` line in the spy log (F2).
4. Repo-root symlink child to a synthetic repo: confirm it is absent from rows and the spy log (F3).

## L1 disposition (C2 pin ec79adbc…, 1462 lines; supersedes 2cf44ee9…, 1458)

Pin changed by four lines. Cited sites re-located by grep (code inspection only): count_dirty pathspecs L635-638, scratch_bytes `-L` L648, worktree_extra_flags guard L736/L753, list_repos symlink skip L875, registration guard L514-520. No regression at any cited site. Full L1 read of the new file not repeated here.

- F1 (HIGH, tracked secret-shaped content read by `git status`): **accepted as disclosed residual** per L1. Header states status may hash tracked content. No general credential-class pathspecs this round. Open follow-up: PROVINCE.md:31 "never reads secret content" remains unreconciled with this behaviour; this seat does not close it.
- F2 (HIGH, worktree paths): fixed (unchanged).
- F3 (MED, repo-root symlinks): fixed (unchanged).
- F4 (MED, symlinked `.scratch`): access fixed; **visibility accepted as legacy** per L1. Silent 0 with no flag; R14C2-08 encodes it deliberately.
- Operator-sweep exclusion from dirty and mtime: **silent by design** per L1 (LOW, accepted).
- F5 (LOW), F6 (safe): unchanged.

Still unverified by this seat: pathspec glob semantics (`[INFERENCE]`), and the F1 strace check, which L1 must run if the disclosure decision is revisited.
