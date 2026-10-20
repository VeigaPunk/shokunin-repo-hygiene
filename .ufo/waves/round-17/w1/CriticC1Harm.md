STATUS: DONE — C1 attacked statically. The approach is sound, but there are 7 ways the implementation can fail and the draft fixture does not catch them. 13 fixture cases are required and a 12-row no-harm ledger follows.

# CriticC1Harm — round 17 wave 1: attack on C1 (D1 `--untracked-files=normal`, D2 per-repo `info/attributes` degrade)

Axis judged: **operability**. Safety is noted wherever an operability "gain" could lose a guard.
Bytes reviewed: `tools/souji-census.sh` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`. This equals `git show 5fa6017:tools/souji-census.sh`, so the working tree is still unmodified r16. Reference arms were read with `git show a31642d|cc21683:tools/souji-census.sh`. The draft fixture `tests/fixtures/r17-census-hygiene.py` was read as it stood, untracked, during this review (cases R17-01..11).
Method: static only. No item carries `ALLOWED-EXEC`, so no census, copy or fixture was run. Git behaviour was checked against git `master` sources (`path.c`, `attr.c`, `builtin/commit.c`, `dir.c`).

## 1. Why the r16 guard exists (provenance)

`git log -S'info/attributes' -- tools/souji-census.sh` gives three commits:
- `b410186`: added to `guard_git_files` together with `info/sparse-checkout`.
- `cbf688a`: removed again.
- `0a70bef`: re-added alone, at `:521`.

The rationale is `.ufo/waves/round-15/w1/AttributesSafe.md` F3/R3 (:22-26): "`$GIT_DIR/info/attributes` … `status` reads it … an `nlink > 1` hardlink to a store file is not refused". F5 (:33-36) adds that the strace oracle **cannot see** a hardlink read, because the open names the repo path, not the store. P-F (:66) therefore labels the hardlink case "contract-level only".

The round-16 closure (`round-16-verifier-spotcheck.md:49`) classes this guard as a safety guard re-landed against cc21683. D2 routes it to a per-repo degrade, following the precedent `RevCensusScanFinal.md` S5 (:132-157).

**Corollary that bounds D2's real benefit.**
- Benign mass hardlinking (`cp -al`, `rsync --link-dest`, dedup tools) also hardlinks `config`, `HEAD` and `info/exclude`. Those stay whole-run exit 2 under C1.
- So the degrade changes the outcome only when `info/attributes` is the *only* hardlinked metadata. In practice that is a deliberate manual share, or exactly the attack shape R3 targeted.
- D2 does not weaken safety *if and only if* no process opens the file (§3 H-A). It does reduce salience: a loud whole-run `path-protected: git-metadata-hardlink` becomes an exit-0 `error` row plus one stderr line.
- That is a tradeoff to disclose, not a defect.

## 2. Live-fleet exposure (measured, read-only)

I ran `git config --file <repo>/.git/config --list`, filtered to `status.*|include*|extensions.worktreeconfig|core.untrackedcache`, plus `lstat` of `.git/info/attributes`, `.git/config.worktree` and `.git/worktrees/`, over the 21 repos in `census/round-16/live-fleet-final.json` (root `/home/vgpnk/Projects/shokunin`).

Result for all 21 repos:
- `status.*` keys: none
- `include*` keys: none
- `config.worktree`: none
- `info/attributes`: none

Global and system config are inert, because the census exports `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null` (`:153`).

⇒ **Prediction: C1 changes zero live rows.** A live diff between r16 and changed on any non-drift field is itself a falsifier. Likely causes:
- a wrong mode, e.g. bare `-u` means `all`; lore's collapsed `.scratch/` (dirty 1) or kaidoku (105) would grow;
- a sticky degrade flag.

Run both arms back-to-back, because lanes mutate the fleet.

## 3. Counterexamples (ordered by severity)

### H-A — the degrade must not skip later guards (safety; would violate the declared exit-2 invariant)

Evidence:
- `guard_git_files` loops `config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates` (`:521`). `objects/info/alternates` comes **after** `info/attributes`.
- In `guard_git_surface`, `guard_git_files` (`:831`, `:873`) runs **before**:
  - `guard_git_config` (`:832`, `:874`): protected `include.path` / `core.*File` / `core.worktree`;
  - the commondir chain (`:834-853`, `:876-895`): commondir `guard_git_files`, `guard_git_config`, `guard_wt_config`;
  - `guard_alternates` (`:854`, `:896`): protected alternates targets;
  - `guard_worktree_registrations` (`:855`, `:897`).
- `guard_alternates_file` only tests `[ -f "$alt" ] || return 0` (`:482`). A FIFO or hardlinked `objects/info/alternates` is therefore caught **only** by `guard_git_files`.

Counterexample: suppose the implementation returns early, either from `guard_git_files` at `info/attributes` or from `guard_git_surface` on the soft result. Then any of these refusals becomes exit 0 with an `error` row:
- a hardlinked or FIFO `objects/info/alternates`;
- a protected include;
- a protected alternates target;
- a protected commondir;
- a hardlinked commondir `config`;
- a protected `worktrees/*/gitdir`.

This contradicts C1's declared "every other guard_git_files entry … and every protected-namespace refusal keeps whole-run exit 2".

Draft fixture coverage: only R17-10, a hardlinked `config` in the same repo with nothing else wrong. It cannot catch any of these.

Smallest correction: the S5 shape. Record the soft result, then **continue the loop** with `cfg_soft "git-metadata-…"; soft=1` instead of `return`. Return 1 only after the loop. Each caller then does `|| soft=1`, so every later guard still runs, as the `:818-820` comment already promises.

### H-B — a call site left at `|| exit 2` produces a silent, unlabelled exit 2

Evidence:
- Today every non-zero exit from `guard_git_files` comes from `protected_fail`, which prints `path-protected:` (`:200-207`).
- Once `guard_git_files` returns 1 for the soft case, any call site still written `guard_git_files … || exit 2` exits 2 with **no finding line**.
- The five sites are `:790`, `:831`, `:849`, `:873` and `:891`.
- `:790` (registered linked-worktree admin, inside `guard_worktree_registrations`) is easy to miss. It runs in the main shell during `list_repos` (`:1266/1269/1299`), so a silent exit 2 kills the whole fleet run.

Draft fixture coverage: `d2_fleet` only mutates `b/.git/info/attributes`, i.e. site `:831`. Sites `:790`, `:849`, `:873` and `:891` are untested.

Smallest correction: convert all five sites. The fixture needs one case per site (see §4 F-5..F-8).

### H-C — a sticky soft state degrades the neighbours

Evidence:
- `list_repos` calls `guard_git_surface "$d" || true` in the **main shell** for every repo (`:1299`) before any row is computed.
- `census_one` runs later in `row=$(census_one …)` subshells (`:1317`) that inherit main-shell globals.
- Only `CFG_SOFT_REASON` is reset per repo (`:823`).
- `CFG_WT_ENABLED` is global. It is set by `guard_git_config` (`:721`) and consumed by `guard_wt_config` (`:698`) and `guard_worktree_registrations` (`:792`).

Counterexamples:
- (i) A new flag (e.g. `META_SOFT=1`) that is not reset in `guard_git_surface` turns every repo after the pre-scan into `error`, including `a`, which sorts **before** `b`.
- (ii) An early return that skips `guard_git_config` in repo B leaves the previous repo's `CFG_WT_ENABLED` in place. If A had `extensions.worktreeConfig=false` and B has it `true` with a `config.worktree` `include.path` into the store, B's `config.worktree` is never scanned, and exit 2 becomes exit 0.

Draft coverage: (i) is covered by `degraded_fleet_problems`: `a`/`c` must not be `error`, plus a byte-identity re-run with `b` removed (`:346-386`). (ii) is not covered.

### H-D — the degraded row hides real dirt and unpushed commits; `--compare` invents deltas (operability; S6 still open)

Evidence:
- The error row is `repo\t0\t0\t0\t0\t\terror` (`:1180`): worktrees, unpushed, dirty and scratch are all the placeholder `0`.
- `emit_compare` still computes numeric deltas for `worktrees|unpushed|dirty|scratch_bytes` (`:1465`). This is the unfixed `RevCensusScanFinal.md` S6.

Counterexample: repo `b` has 3 dirty files and 2 unpushed commits, plus a hardlinked `info/attributes`.

| arm | row / compare output |
|---|---|
| a31642d, cc21683 | `… 2 3 … dirty,unpushed` |
| r16 | no rows (exit 2) |
| changed | `b 0 0 0 0  error` |

Against an a31642d- or cc21683-era baseline, `--compare` prints `dirty 3 0 -3` and `unpushed 2 0 -2`. That reads as a cleanup that never happened.

- No false `clean`: `error` sets `has_problem` (`:1236`). This is safe for consumers that read the flags column.
- Unsafe for numeric consumers: this output is **newly reachable** for this input class under C1 (r16 exited 2).

Smallest correction: within the round, the fixture asserts `b`'s flags are exactly `error` (no `clean`) **while `b` carries real dirt and unpushed commits**. The draft `b` is pristine, so it cannot show what is hidden. The ledger discloses the compare delta. Fix S6 (`chg=unmeasured` when either side's flags contain `error`), or state it as an open residual.

### H-E — FIFO hang becomes reachable in `showUntrackedFiles=no` repos (operability regression for a narrow class)

Evidence:
- Under `-uno`, git skips the untracked walk entirely, so no `.gitignore` is opened.
- In `normal` mode git reads the `.gitignore` of every directory it walks: `dir.c` `add_patterns` does `open(fname, O_RDONLY)` / `open_nofollow` (`:1165-1167`). That is a blocking open on a FIFO; `O_NOFOLLOW` does not help.
- The census has no timeout around `git status` (no `timeout` anywhere in `souji-census.sh`).

Counterexample: a repo with `status.showUntrackedFiles=no` and a FIFO named `.gitignore` in any walked directory, including an untracked one.

| arm | outcome |
|---|---|
| r16, a31642d | exit 0 with a false-clean row |
| changed | `git status` blocks forever; the whole census never finishes |

The class is pre-existing for every default-mode repo, so this is not a new kind of hazard. It is newly reachable for `-uno` repos.

Smallest correction: disclose it in the ledger and pin it in the fixture with the 60 s cap, expected `rc 124` on changed and r16-default. Optional: wrap the `count_dirty` status in `timeout -k`, giving `unverifiable`. That is outside C1's declared scope.

### H-F — `normal` changes counts for `showUntrackedFiles=all` repos (an intended normalization, but it is a diff)

Evidence: a31642d (`:131`), cc21683 (`:712`) and r16 (`:1037`) all pass no mode, so repo config wins. Under `all`, every file in an untracked directory is a separate line. Changed collapses each such directory to one line.

Effects:
- The dirty flag is unchanged: under both `all` and `normal`, any untracked non-ignored content gives ≥1 line.
- Counts drop.
- A baseline taken by any earlier arm makes `--compare` report drift (exit 3) on such repos once.
- The header (`:35-37`) says the count is "default untracked mode … matching souji-verify". Once the mode is pinned, that wording should say "`--untracked-files=normal` regardless of `status.showUntrackedFiles`".
- souji-verify's receipt-evidence `status` calls (`souji-verify.sh:322`, `:366`, `:820`; vault `:518`, `:562`, `:1038`; quarantine `:1080`) still honor config, and they also honor global config: verify does not set `GIT_CONFIG_GLOBAL` (only `unset GIT_DIR …` at `:64`).
- So "matching souji-verify" becomes false for `-uno` repos. This is a duplicate-authority wording defect only.
- Verdicts are unaffected. The SAFE-deciding status already pins `--untracked-files=all --ignored=matching` (`verify:658`, `vault:876`, `quarantine:919`). Present worktrees and repo roots are always `NOT-SAFE` (`verify:324-328`, `:372-374`, `:793`).

Draft coverage: R17-04 pins `all` == `normal` == 1. Good.

### H-G — a mode typo silently reintroduces the defect or expands counts

- `--untracked-files` takes an optional argument. Bare `-u` means `all`.
- `--untracked-files normal` (space instead of `=`) parses as mode `all` plus a pathspec `normal`.
- Placing the flag after `--` (`:1037`) makes it a literal pathspec, so `-uno` is honored again.

R17-01 and R17-04 catch all three only when both run on changed. The live-fleet identity in §2 is the cheap second net.

### Residual false-clean vectors that D1 does NOT fix

Disclose these so C1 does not read as "no false clean":
- an unreadable untracked directory: `open_cached_dir` fails, the directory is treated as empty and hidden;
- `assume-unchanged` / `skip-worktree` index bits;
- `info/exclude` or `.gitignore` `*`;
- `--ignore-submodules=all` (inherited).

All of these are identical across the four arms.

### Over-degrade to disclose (not harm vs r16)

- `info/` is a **common** path: git `path.c:102` `{ 0, 1, 1, "info" }`, with only `info/sparse-checkout` per-worktree (`:103`).
- So git never reads `worktrees/<id>/info/attributes`. The guards at `:790` and `:873` (linked admin dirs) degrade for a file git does not open.
- At `:790` the degraded row is the **main** repo M, because the check sits inside M's `guard_worktree_registrations`. M's own dirt and unpushed commits are then hidden as `0` (H-D).
- vs r16 this is an improvement (exit 2 → one row); vs a31642d it is a contraction.
- Smallest correction (optional): check `info/attributes` only in the resolved common dir. Keep the admin-dir check for the other entries.

### Duplicate and mislabelled diagnostics (minor operability)

If the new diagnostic is printed inside `guard_git_*`, it fires once in the `list_repos` pre-scan (`:1266`, `:1269`, `:1299`) and again in `census_one` (`:1177`), so at least twice per repo.

`census_one` also prints `config-unsupported: ${CFG_SOFT_REASON:-git-config-unsupported}` (`:1178`). If the degrade does not set `CFG_SOFT_REASON`, stderr wrongly blames config.

The fixture should pin the exact count and wording:
- `git-metadata-unsupported <reason> <path>` exactly once, or an explicitly documented N;
- no `git-config-unsupported` for this cause;
- the path passed through `sanitize_field`.

## 4. Falsification cases the fixture MUST include

Existing draft ids are kept. "red" means the arm must FAIL the case's changed expectation; that is what proves the case discriminates. Every invocation keeps the per-run cap (draft `timeout=60`, `:233-238`), so a hanging reference arm yields `rc 124` for that case only, not a lost 900 s matrix arm (`run-matrix.py:37-43`).

| id | setup | changed expect | r16 5fa6017 | r14 cc21683 | pre-harm a31642d | covers |
|---|---|---|---|---|---|---|
| R17-01..03 (draft) | `-uno` local / include / `config.worktree` + untracked file | dirty ≥1, no `clean` | red (false clean) | 01 red; 02/03 refused value-blind (exit 2), record | red | D1 |
| R17-04 (draft) | `all` vs none, 3-file untracked dir | both dirty=1 | red (3) | red (3) | red (3) | H-F, H-G |
| **F-1** new | `-uno` set in a **linked worktree's** `config.worktree` (`extensions.worktreeConfig=true`), untracked file in that worktree, main clean | main row has `wt-dirty`, not `clean` | red | record | red | D1 via `worktree_extra_flags:1162` |
| **F-2** new | boolean forms `false`, `0` and `off` | dirty ≥1 each | red | record | red | D1 parse breadth |
| **F-3** new (preserve) | `status.showUntrackedFiles=bogus` | `status-unverifiable` on **all** arms. git dies in config (`commit.c:1512` `return error(…)`) before the `-u` arg is parsed; [INFERENCE: dies, not a warning — the case verifies it] | same | same | same | no harm |
| **F-4** new | `-uno` + FIFO `.gitignore` in an untracked dir | pinned: `rc 124` (disclosed hang), **or** `unverifiable` if a timeout fix lands | exit 0, false clean | record | exit 0, false clean | H-E |
| R17-07..09 (draft) | `b` info/attributes hardlink / FIFO / symlink→FIFO, neighbours `a`,`c` | `b` = `error`, a/c byte-identical, no `git -C b` | red (exit 2) | red (measured or hang) | red | D2 |
| **F-5** new | info/attributes hardlink in the **commondir** of a linked worktree discovered as a root (`.git` file, `:891`) | that row `error`, exit 0, diagnostic present | red | record | red | H-B |
| **F-6** new | hardlink in a linked worktree's **own admin dir** (`:873`) | `error` row, exit 0 (over-degrade disclosed) | red | record | record | H-B |
| **F-7** new | hardlink in a **registered** worktree admin of main M (`:790`) | M = `error`, exit 0, **not a silent exit 2** (stderr non-empty, names reason) | red | record | record | H-B |
| **F-8** new | `.git` dir with `commondir` → other gitdir whose info/attributes is FIFO (`:849`) | `error`, exit 0, run completes | red | record (may hang) | record (may hang) | H-B |
| **F-9** new (refuse) | same repo: info/attributes hardlink **plus** each of: (a) `objects/info/alternates` FIFO; (b) `include.path` → store; (c) alternates line → store; (d) commondir `config` hardlinked; (e) `worktrees/x/gitdir` → protected; (f) `extensions.worktreeConfig=true` + `config.worktree` include → store, with an earlier-sorted repo having `worktreeConfig=false` | exit 2, `path-protected`, empty stdout, for **each** sub-case | exit 2 | per sub-case | per sub-case | H-A, H-C(ii) |
| **F-10** new | D2 `b` carries 3 dirty files + 2 unpushed commits; then `--compare` against a baseline row `b 1 2 3 0 … dirty,unpushed` | row flags exactly `error`; compare output recorded and disclosed (`-3`/`-2`), or `unmeasured` if S6 lands | exit 2 | measured | measured | H-D |
| **F-11** new (oracle liveness) | FIFO info/attributes **with a tracked file made stat-dirty**, so an unguarded status must consult attributes | changed: completes, `error` | exit 2 | **must hang → rc 124** | **must hang → rc 124** | proves R17-08's oracle is live [INFERENCE: attributes are read only when a tracked file is hashed — the red arms verify it] |
| **F-12** new (oracle liveness, hardlink) | R17-07 plus an inotify `IN_OPEN` watch on the partner inode (Python `ctypes` `inotify_init1`/`inotify_add_watch`; no install needed; watches are per-inode, so this closes AttributesSafe F5's blind spot) plus a stat-dirty tracked file | zero `IN_OPEN` on the inode during the run | n/a (exit 2) | ≥1 `IN_OPEN` (red control) | ≥1 `IN_OPEN` | D2 never-opened, non-vacuous |
| **F-13** new | stderr shape for R17-07 | `git-metadata-unsupported` exactly the pinned number of times; no `git-config-unsupported`; repo path sanitized | — | — | — | diagnostics |

Spy oracle note (draft `:346-386`): "no `git -C <bad>`" must match on **both** the spelled and the `realpath` form of `b`. The census passes guarded or resolved paths (`guard_path`, `:1176`), and `/var/tmp` symlinks would make a spelled-only match vacuous.

## 5. No-harm ledger L1 must report

| # | input class | a31642d | cc21683 | r16 5fa6017 | changed | verdict to report |
|---|---|---|---|---|---|---|
| L-1 | no `status.*` key (whole live fleet, §2) | rows | rows | rows | byte-identical to r16 | preserve; live identity required |
| L-2 | `-uno` (local/include/worktree) + untracked | false clean | local: false clean; include/wt: exit 2 | false clean | dirty | improved on all arms |
| L-3 | `all` + untracked dirs | N per file | N per file | N per file | 1 per dir | **count change** (flag same); one-time compare drift (exit 3); header wording |
| L-4 | `-uno` + FIFO `.gitignore` | exit 0 false clean | — | exit 0 false clean | **hang** (no timeout) | **contraction, disclosed** (pre-existing class newly reachable) |
| L-5 | invalid `status.showUntrackedFiles` | unverifiable | — | unverifiable | unverifiable | preserve (F-3 verifies) |
| L-6 | info/attributes hardlink, benign | measured row, **reads inode** | measured row, reads inode | **whole run exit 2** | `b` error, rest measured, exit 0 | improved vs r16; **per-repo contraction vs a31642d/cc21683** (measured → `error`, dirt and unpushed shown as 0) — safety-motivated, not no-harm |
| L-7 | info/attributes FIFO | hang if hashed (F-11) | same | exit 2 | `b` error, exit 0 | improved vs all |
| L-8 | info/attributes in linked admin dir (git never reads it) | measured | measured | exit 2 | that row, or **main M**, `error` | improved vs r16; over-degrade vs a31642d (disclose) |
| L-9 | any other `guard_git_files` entry, or protected reach, same repo as L-6/7 | varies | exit 2 | exit 2 | **must stay exit 2** (F-9) | invariant; any exit 0 = reject |
| L-10 | `--compare` across a degraded row | — | — | n/a | invented `-N` deltas (S6) | **disclose** (newly reachable for this class) |
| L-11 | salience of the attack-shaped hardlink | silent read | silent read | loud whole-run refusal | quiet `error` row + stderr | tradeoff: safety holds iff F-12 shows zero opens |
| L-12 | sibling tools' evidence `status` | — | — | config-honoring | unchanged | duplicate-authority wording (H-F); verdict paths already pinned (`verify:658` etc.) |

Judge note: L-4, L-6 (vs pre-harm), L-8 and L-10 are real contractions or new reachability. They may be admitted only as disclosed tradeoffs. L-9 is the hard reject line: any F-9 sub-case at exit 0 means C1 harms safety.

## 6. Smallest safe correction set (for CensusD1D2)

1. `count_dirty` `:1037`: add `--untracked-files=normal` before `--`. Write `=normal`, never bare `-u` and never a space-separated value. Update header `:35-37` to "`--untracked-files=normal` regardless of `status.showUntrackedFiles`".
2. `guard_git_files`, `info/attributes` entry only: `cfg_soft "git-metadata-hardlink|git-metadata-nonregular"; soft=1; continue`. Return 1 after the loop. All other entries keep `protected_fail`.
3. Sites `:790`, `:831`, `:849`, `:873`, `:891`: `|| soft=1`. No `return` in `guard_git_surface` until every guard has run.
4. Print the `git-metadata-unsupported` diagnostic once, from `census_one`, using `CFG_SOFT_REASON` and the sanitized path. Do not also print `config-unsupported` for this reason.
5. Optional: check `info/attributes` only in the resolved common dir (git `path.c:102`). Optional: S6 `unmeasured`.

## Commands run (all read-only)

- `git -C …/souji-shokunin log -S'info/attributes' --format='%h %ad %s' --date=short -- tools/souji-census.sh` → `0a70bef`, `cbf688a`, `b410186` (all 2026-10-20).
- `git show {b410186,cbf688a,0a70bef} -- tools/souji-census.sh | grep -C3 info/attributes` → add (with `info/sparse-checkout`), remove, re-add alone.
- `git show {a31642d,cc21683}:tools/souji-census.sh | grep -nE 'for rel in|status --porcelain|attributesFile=|untracked'` → a31642d `:131` status with no mode and no `guard_git_files` list; cc21683 `:477` list without info/attributes, `:712` status with no mode.
- `grep -nE 'timeout|subprocess' census/round-16/run-matrix.py` → `run(..., timeout=900)` returns 124.
- `grep -nE 'status (--porcelain…)|untracked-files…'` over `souji-verify.sh`, `souji-vault-verify.sh` and `souji-quarantine.sh` → line numbers cited in H-F.
- `sha256sum tools/souji-census.sh` and `git show 5fa6017:tools/souji-census.sh | sha256sum` → both `64a60fd0…7c`.
- `git status --porcelain=v1 -- tools tests/fixtures census/round-17` → census unmodified; `r17-census-hygiene.py` and `census/round-17/` untracked.
- Python: `git config --file <repo>/.git/config --list` (filtered keys only) plus `os.lstat` over the 21 live-fleet repos → no `status.*`, include, `config.worktree` or info/attributes anywhere.
- `curl` of git `master` `path.c`, `attr.c`, `builtin/commit.c`, `dir.c` (source reading) → `path.c:102-103`, `attr.c` `read_attr_from_file` blocking `open`, `commit.c:1225`/`:1512`, `dir.c:1165-1167`.
- Reads: `souji-census.sh:479-563`, `:563-703`, `:769-913`, `:935-1083`, `:1124-1330`; `round-16-verifier-spotcheck.md`; `RevCensusScanFinal.md`; `AttributesSafe.md` (grep); `r15-census-config.py` (grep and `:990-1018`); `r17-census-hygiene.py` (grep and `:470-603`).

Tool installs or updates: none.
