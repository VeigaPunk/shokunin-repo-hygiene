# BoundaryReviewRoot — C2 root / ancestor / symlink input protection and ordering

Seat: SoujiR14.BoundaryReviewRoot (reviewer, leaf)
Target: /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
Snapshot reviewed: `souji-census.sh#5156` (827 lines, read in full)
Axes: calibration, operability

## Evidence class

- Code inspection only. Every finding below is from reading the file. Line numbers are the snapshot above.
- Exercised evidence: **none**. No census run, no selftest, no shell execution, no probe of any protected path. No real `~/.omp/agent` access.
- Tools installed or upgraded: none (review needed none).

## Verdict

C2 is not implemented in the snapshot. `tools/souji-census.sh` contains no credential-store guard of any kind. A text search for `HOME`, `omp`, `protected`, `credential` and `alias` in the script returns only the secret-name regex (L175), a fixture string (L543), and the comment at L40. The script never reads `$HOME`.

Consequence on the current file: `--root`, `SHOKUNIN_ROOT`, `--compare`, child symlinks, and `git worktree list` paths all reach `stat`, glob, `find`, `git status`, and content reads without any refusal. A root equal to, inside, or above `~/.omp/agent` is enumerated.

Required ordering (spec, w1-spec.json item CensusBoundary): lexical guard first, then canonical resolution, then directory stat/enumeration/content access. The current file violates that order at every input entry point.

## Protected set (assumption to confirm at L1)

This review assumes the credential-store tree is `$HOME/.omp/agent`. Basis: the lane and wave instructions forbid opening `~/.omp/agent` except RULES.md and skills, and the SafetyCredential spec names that tree. PROVINCE.md L30-31 assigns credentials to kagi-shokunin and says souji never reads secret content. L1 must confirm the exact set, including whether a passwd-derived home is also protected (see F11).

## Ordering map (current file)

| Stage | Line(s) | Input touched | Guard before access? |
|---|---|---|---|
| Arg parse, `--root` / `--compare` values stored | 797-814 | raw string | no validation |
| `SHOKUNIN_ROOT` default | 83 | env string | no |
| Selftest dispatch | 816 | none | n/a |
| Compare dispatch | 821-824 | `COMPARE` | no |
| Compare file `[ -f ]` stat + full read | 365, 367, 385 (called from 416) | compare path | **no** — runs before any root check |
| Root canonicalise (`readlink -m`) | 345 via 95 | root path | **no** |
| Root `[ -d ]` stat | 346 | root path | **no** |
| Child glob + `[ -d ]` / `[ -d .git ]` follow symlinks | 324, 325, 333 | root children | **no** |
| Child canonicalise | 245 via 95 | child path | **no** |
| `cd` + `find` names and mtimes | 165 | repo path | **no** |
| `git status` / `rev-list` / `worktree list` | 109, 115-123, 131, 235, 253 | repo `.git` | **no** |
| Worktree path canonicalise + `[ ! -d ]` + `git status` | 225, 227, 231 | `.git/worktrees/*/gitdir` values | **no** |
| `.scratch` `[ -e ]` before `[ -L ]` | 142-143 | `.scratch` symlink | stat through symlink before refusal |
| Temp file in `${TMPDIR:-/tmp}` | 418 | env path | **no** |

## Findings (ordered by severity)

### F1 — BLOCKING — no guard exists (L1-L827, whole file)
No lexical or canonical check against the protected set exists anywhere. Every C2 requirement is unmet: root refusal, ancestor refusal, alias refusal, compare refusal, and stable protected-path finding with exit 2.
Fix: add a guard function, called before any FS access on every external input path (see F2-F8).

### F2 — HIGH — root reaches stat and enumeration before any check (L344-353, L316-341)
Order today: `canon_path` (L345) → `[ -d ]` (L346) → `list_repos` globs children (L320-340). The guard must run on the raw string first, then on the canonical result, and both must run before L345's canonicalisation is trusted. Refuse equal, descendant, and ancestor roots, and every alias (canonical equality or prefix).
Note: `--include-root` at L320 also stats `$root/.git` before any check.

### F3 — HIGH — canonicalisation fails open (L95)
`canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }` falls back to the raw lexical string when `readlink` fails. A guard that compares "the canonical result" would then compare the attacker-supplied string, which is the path being checked for aliasing. Fix: on failure return an error and refuse with exit 2 (could-not-evaluate, fail closed). Callers at L225, L245, L345 currently ignore failure.

### F4 — HIGH — `--compare` is loaded before the root guard and read in full (L416, L365-385)
`emit_compare` calls `load_census "$COMPARE"` (L416) before `emit_census` (L419). `load_census` does `[ -f "$file" ]` (L365), which follows symlinks, and then reads the file (L367, L385). The header gate (L370-372) limits echo to lines starting with the exact header, but the read itself is content access. `/dev/stdin` redirected from a store file also resolves through `readlink -m` to the store path; the guard must canonicalise before L365. (Behaviour on `/dev/stdin` is [INFERENCE] from `/proc/self/fd` semantics; not exercised.)
Fix: guard `COMPARE` lexically and canonically before L365, and before the root guard only if the root guard also runs first. Refuse with exit 2 and the protected-path finding.

### F5 — HIGH — child symlinks reach census (L324-341, L245, L165)
`list_repos` tests `-d` (follows symlinks) at L325 and `-d "${d%/}/.git"` at L333. A child symlink into the store passes both, is canonicalised at L245, and is then walked by `find` (L165) and `git` (L109-137). The spec requires "skip symlink repo roots".
Fix: skip any child where `[ -L "$d" ]` before `-d`, and re-check the canonical repo against the protected set in `census_one` before any git, find, or du call.

### F6 — HIGH — worktree registrations are unguarded directory stats and git reads (L216-240, L235, L225-231)
`worktree_extra_flags` takes each `worktree <path>` from `git worktree list --porcelain` (L235). That path is read from `.git/worktrees/*/gitdir`, which is repo-controlled metadata. It is canonicalised (L225), then `[ ! -d "$path" ]` stats it (L227), then `count_dirty` runs `git -C "$path" status` (L231). A registration pointing into the store therefore gets a directory stat and an index/status read.
Fix: guard each worktree path lexically and canonically before L227 and L231. Refuse (set a flag or finding) and do not run `count_dirty` on it. The `git worktree list` call itself (L109, L235) runs in the repo, so it is covered by the Git seat's `commondir` review, not here.

### F7 — MEDIUM — `.scratch` symlink is stat'd through before refusal (L142-143)
`[ ! -e "$d" ] && [ ! -L "$d" ]` at L142 calls `-e`, which follows a symlink into the store and stats its target before `[ -L ]` at L143 refuses it. Fix: test `[ -L "$d" ]` first and return 0 before any `-e`/`-d` call.
Note: `du -sb -P` (L147) does not follow the top-level symlink; the `-L` refusal is the real protection, so reordering is the fix.

### F8 — MEDIUM — temp file written under `$TMPDIR` on compare path (L418-421) and selftest fixtures under `$TMPDIR` (L516)
`emit_compare` writes census output to `mktemp "${TMPDIR:-/tmp}/..."`. `TMPDIR` is environment-controlled. If it points into the protected tree, the census writes into the store, contradicting the header claim "never writes outside a --selftest mktemp" (L4-6). The selftest at L516 has the same `TMPDIR` dependency.
Fix: avoid the temp file on compare (buffer in a variable or compare in-process), or refuse a `TMPDIR` that overlaps the protected set before writing.

### F9 — MEDIUM — lexical normalisation and relative inputs unspecified
The guard must normalise the raw string before comparing: collapse `//`, `/./`, trailing `/`, and resolve `..` lexically. Relative `--root`/`--compare` values must be made absolute against `$PWD` first. The current file has no normalisation. `readlink -m` handles normalisation only after the FS is touched, which is too late for the lexical pass.

### F10 — MEDIUM — no stable protected-path finding; wrong exit codes today (L93, L346)
Existing failures use `usage_err` (exit 2, L93) or `root is not a directory` (exit 1, L346). The spec requires a stable protected-path finding with exit 2. Proposed shape (for CensusBoundary to adopt or amend): `souji-census: protected-path refused: kind=root|ancestor|alias|compare|worktree` on stderr, exit 2, no protected path echoed (PROVINCE L31: cite paths/modes only; here do not echo the protected path at all).

### F11 — MEDIUM (operability) — guard must not trust `$HOME` alone
A poisoned `HOME` would move the protected set. Recommend protected set = union of `$HOME/.omp/agent` and the passwd-home `/.omp/agent` (lookup via `getent passwd "$(id -u)"`), each checked lexically and canonically. Tests use synthetic HOME for isolation; the passwd-home entry keeps the real store refused even under a synthetic HOME in an operator run.
Residual: bind mounts and hard links cannot be detected by path. `stat -c %d:%i` on the protected root would catch them but is a stat of the protected root itself. This is an L1 decision (metadata-only, not enumeration), not a blocker.

### F12 — LOW — documentation drift in the header
- L9 names `tools/souji-census.impl-33.sh`; the file is `tools/souji-census.sh`.
- L4-6 "never writes outside a --selftest mktemp" is contradicted by L418.
- L89 `usage` prints lines 2-68 via `sed`; adding the refusal flag/finding text will need the range updated.

### F13 — NOTE — selftest cannot prove C2 as written
`run_selftest` (L511-792) has no protected-path case and no command spy. The required fixture `tests/fixtures/r14-census-boundary.py` must:
- use synthetic HOME under `/var/tmp` only (never real `$HOME`);
- put a `PATH` shim in front of `git`, `find`, `du`, `readlink`, `date` that logs each invocation, and assert zero invocations that touch a protected path before refusal;
- cover direct, descendant, ancestor, alias (symlink root, symlink child, symlink `.scratch`, symlink worktree gitdir), and compare-path cases, each expecting exit 2 and the stable finding;
- clean up `/var/tmp` on exit.

### F14 — NOTE (cross-seat) — `GIT_*` override list is incomplete (L71)
L71 unsets `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE` but not `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, or `GIT_ALTERNATE_OBJECT_DIRECTORIES`. Route to BoundaryReviewGit; listed here only so the ordering fix is not limited to paths.

## Required ordering for the C2 implementation (for CensusBoundary)

1. Parse args (L797-814) — record raw `--root`, `--compare`.
2. Lexical pass on each raw input (no FS): absolutise against `$PWD`, normalise, compare against protected set strings and their ancestors/descendants.
3. Canonical pass (`readlink -m`, fail closed): compare canonical result against protected set; refuse aliases.
4. Only then: `[ -d ]`, `[ -f ]`, glob, `find`, `git`, `du`, `mktemp`, content read.
5. Per child and per worktree path: repeat 2-3 before any git/find/du; skip symlinks before `-d`/`-e`.
6. Selftest/fixture cases per F13.

## Final L1 commands (not run by this seat)

- `bash -n /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh --selftest` (selftest must be extended per F13 first)
- `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py` (synthetic HOME under /var/tmp only)
- Static: `grep -n 'omp\|HOME\|getent\|protected' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` — expect guard hits before the first FS call in each entry point
- Do not run the census against the real `$HOME` for C2 verification; use `env HOME=/var/tmp/<fixture>`

## Residual risk / verification gaps

- The guard does not exist yet; every finding above is against the current snapshot. Re-read after CensusBoundary lands; line numbers will shift.
- `/dev/stdin` behaviour and `readlink -m` on `/proc/self/fd` are [INFERENCE] from documented semantics, not exercised.
- Bind-mount and hard-link aliases are not detectable by path (F11).
- Source row S038 (timeout docs correction): not applicable to this seat; left to the SourceTimeout scout.

## Review of landed bytes 2cf44ee9… (tools/souji-census.sh, tests/fixtures/r14-census-boundary.py)

Scope: static read only. No runs, no builds, no protected-path access. sha256 of the script matches the pin `2cf44ee986641dc2de3a25f2b9524e4a10e718f36afd2e5338d2c65251ece849` (1458 lines). Fixture sha256 `d712ac790e241c1b0bed429e86d3a680d51fbd5073ed7660d511326a8c78fd1d`.
Tools: none installed or upgraded. `/usr/bin/strace` is present (read-only check).

### Improved since snapshot 5156 (verified by reading)
- `main` guards `--root` and `--compare` (L1446-1447) before `command -v git/du` and before any stat.
- `..` input is refused (L322-324); symlink targets are folded one hop at a time (L353-369).
- `canon_path` fail-open is gone; unresolved and looping links fail closed.
- `list_repos` skips symlink children and guards child names before `-d` (L857-872). `.git` symlinks are not rows.
- `.scratch` tests `-L` first (L644).
- Git gitdir, commondir, alternates, and worktree registrations are guarded; `git status` is run with `core.fsmonitor=false` and `core.hooksPath=/dev/null`.

### F-A BLOCKING: fail-open when a guard refusal happens inside `$(...)`
Bash clears `-e` in command substitutions (bash(1), Command Substitution; non-POSIX default). `emit_census` calls `census_one` as `if row=$(census_one "$repo")` (L901). A refusal inside that subshell therefore does not stop the flow; the captured value is empty and execution continues. The refusing `exit 2` only ends the innermost `resolve_guarded` subshell, and the enclosing `$(guard_target …)` returns 0.
Affected sites: census_one L764 (`repo=$(guard_path …)`); guard_git_surface L529, L544, L566, L581 (`dir=$(guard_target …)`); worktree_extra_flags L732 (`cpath=$(guard_target …)`); guard_target L392 and guard_path L383 (`resolved=$(resolve_guarded …)`); emit_compare/emit_census root capture L894, L1005.
Reachable path (a): gitfile root with commondir into the store (fixture R14C2-06 `commondir` variant, `--include-root`). list_repos L848-850 guards only the gitfile target and adds the root. census_one L765 → guard_git_surface L566-586: `dir=$(guard_target git-common-dir …)` refuses silently and leaves `dir=""`. L777 `git rev-parse` then reads the store's GD. Expected result: rc 0 with a row (not rc 2). [INFERENCE from the errexit rule; L1 must confirm with R14C2-06.]
Reachable path (b): linked worktree whose admin `commondir` is an absolute store path. list_repos never inspects `worktrees/*/commondir` (guard_worktree_registrations checks only the `gitdir` target). worktree_extra_flags L749 `guard_git_surface "$cpath"` passes silently, and L750 `count_dirty` runs `git status` against the store. [INFERENCE]
Fix: every refusal-bearing capture uses an explicit status (`dir=$(guard_target …) || return 2`; guard functions return non-zero on refusal; callers `|| exit 2`). Do not depend on errexit. Static invariant for the fixture or L1: `grep -nE '=\$\(guard_|=\$\(resolve_guarded' tools/souji-census.sh` must return nothing. `shopt -s inherit_errexit` (bash ≥ 4.4) is a partial mitigation only; prefer explicit status.

### F-B HIGH: lstat of the store parent before refusal
`resolve_guarded` (L318-379) has no upfront lexical check on the normalized input. For `--root …/home/.omp/agent` it runs `[ -L "$candidate" ]` on `…/home/.omp` (L353) before the store is refused at L350. The store's parent is metadata-only, but the lane contract requires lexical refusal before any stat. Fix: (1) run `protected_component_reason` and `path_overlaps` on the normalized input before the loop (direct inputs then cost zero stats); (2) before any `[ -L ]` on a candidate, refuse if `candidate + remaining lexical suffix` contains a protected component pair or lies inside a root (covers aliases, where the suffix is the link target).

### F-C Fixture oracle blind spot
`run_tool` traces only `execve,open,openat,getdents64` (L317). `lstat`/`newfstatat`/`statx`/`readlink`/`access` are invisible, so F-B cannot be detected, and R14C2-01..04 would pass on the stat. Widen the filter to include `newfstatat,statx,readlink,readlinkat,access,faccessat`, keeping the STORE filter. Expect R14C2-01..04 to FAIL until F-B is fixed; that is the correct red.
Coverage gaps to add as cases: (i) linked-worktree `commondir` alias into the store (path (b)); (ii) a repo containing `census/operator-sweep-*/` with a file, asserting no `getdents64`/`openat` under it. The `count_dirty` pathspec excludes (L629-634) are not proven to stop git from walking the directory. [INFERENCE; needs strace.]

### F-D Medium/low
- A FIFO at `worktrees/*/HEAD`, `worktrees/*/commondir`, or `worktrees/*/gitdir` is not refused (guard_git_files covers only top-level names, guard_git_links covers only symlinks). `read <` or `git` can hang. Operability, not credential access.
- `PI_CODING_AGENT_DIR=$HOME` (or `.`) adds a root that refuses every HOME-internal path, including the default fleet root. Fail closed, but document and reject roots equal to or above `$HOME`.
- Header L75-77 says `<home>/${PI_CONFIG_DIR:-.omp}/agent`; code adds that root only when `PI_CONFIG_DIR` is set (the default is covered by the `.omp/agent` component pair). Doc drift only.
- `guard_git_config` matches `*include.*` as a substring of the lowercased key list, so unrelated keys trigger `git-config-unsupported`. Over-refusal, fail closed.

### Verdict on 2cf44ee9
Not ready to close C2. Root and compare ordering is improved, but F-A lets a refusal pass silently on reachable gitfile/commondir and worktree-commondir inputs, and F-B/F-C mean the fixture cannot show the stat ordering the lane requires. Re-review after F-A and F-B land.

### L1 commands (not run by this seat)
- `bash --version`
- `grep -nE '=\$\(guard_|=\$\(resolve_guarded' tools/souji-census.sh` (expect empty after F-A)
- `python3 -B tests/fixtures/r14-census-boundary.py --case R14C2-06` (expect FAIL on commondir before F-A fix)
- `python3 -B tests/fixtures/r14-census-boundary.py --case R14C2-01` (expect FAIL on stat before F-B fix)
- After fixes: full `python3 -B tests/fixtures/r14-census-boundary.py` and `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`

## Re-review of final bytes 034a518e… (tools/souji-census.sh 1515 lines) and a118225b… (fixture 679 lines)

Scope: static read only. No runs, no builds, no protected-path access. Pins verified with sha256sum and wc -l.
Tools: none installed or upgraded.

### N1 (fail-open inside command substitution): CONFIRMED FIXED
Every refusal-bearing capture is `|| exit 2` (grep of `=$(guard_|=$(resolve_guarded|=$(gitfile_admin|=$(worktree_extra_flags` shows only the two seed probes at L241 and L256 unwrapped, by design with `2>/dev/null`). `census_one` exit 2 propagates through `if row=$(census_one …)` to `emit_census` rc check. Guard-function exits inside `list_repos` run in the main shell and are intended.
Minor: `guard_git_surface` calls at L807 and L823 are unwrapped. They exit internally, so behaviour is correct; make explicit for the invariant.

### N4 (stat before refusal): CONFIRMED FIXED for alias and store-descendant inputs
Lookahead at L368-372 folds candidate plus remaining suffix lexically and refuses before `[ -L "$candidate" ]` at L373. For `--root …/.omp/agent/…` the refusal happens at candidate `.omp` before its lstat. Symlink-root aliases are refused when the walk folds the target. [INFERENCE for the alias case; not exercised.]

### Residual R1 (medium): ancestor inputs still stat before refusal
`--root ~`, `--root ~/.omp`, and `--root /` are not caught by the lookahead, because it refuses only descendants or equals. The final predicate at L393-396 runs after the walk, so each ancestor candidate is lstat'd at L373 first. Fix: before the loop when final=1, run `protected_reason_input "$lex"` on the lexical input. `path_overlaps` refuses ancestors. Do not apply the pre-check to gitfile-internal targets without thought: allow=1 targets are physical and should keep the post-walk check only.

### Residual R2 (medium, L1 decision): seed probe stats the store parent
L256 `resolve_guarded "$lex/.omp"` lstat's `~/.omp` on every invocation, including real-HOME runs. This is metadata of the store parent and runs before any input. Options: (a) drop the probe and document the relocated-`~/.omp` residual; (b) keep it and state it in the header, with an explicit oracle for the parent. The fixture cannot see it today (see R3c).

### Residual R3 (fixture oracle holes, medium)
- (a) `trace_access` L408-409 exempts every `readlink(` line, so a readlink of a store child is invisible. Remove the exemption or check readlink paths under AGENT.
- (b) L422 counts stat-family tokens only when `agent + "/"` appears. A stat of AGENT itself is exempt in refusal cases (R14C2-01). Keep the exemption for the positive control R14C2-08 only.
- (c) Ancestor stats (`HOME`, `~/.omp`) are not matched by L417 (`agent not in line`). R14C2-03 can pass while stat'ing HOME. Add a parent/ancestor set for refusal cases.
- The trace filter `%file,getdents64,execve` (L361) now covers the stat family, which closes the earlier F-C blind spot. The hit classifier is the remaining gap.

### R14C2-06 commondir (expected rc 2)
Static reading: L598-606 and L634-641 guard the commondir target with `|| exit 2`, so a store target refuses explicitly. [INFERENCE] Confirm with `--case R14C2-06`; not run here.

### Verdict on 034a518e
N1 closed. N4 closed for aliases; open for ancestors (R1) and the probe decision (R2). The fixture cannot yet serve as the red/green oracle (R3). Not ready to close C2 until R1 and R3 are resolved. R2 is an L1 decision.

### L1 commands (not run by this seat)
- `bash --version`
- `grep -nE '=\$\(guard_|=\$\(resolve_guarded|=\$\(gitfile_admin|=\$\(worktree_extra_flags' tools/souji-census.sh` (expect only L241, L256)
- `python3 -B tests/fixtures/r14-census-boundary.py --case R14C2-06`
- `python3 -B tests/fixtures/r14-census-boundary.py --case R14C2-03` (expect a PASS only after R1 and R3c)
- After fixes: full `python3 -B tests/fixtures/r14-census-boundary.py` and `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`

## Re-review of final bytes 1533 e2a1d502… (tools/souji-census.sh) and 726 fda498d0… (fixture)

Scope: static read of targeted regions; not every line re-read. No runs, no builds, no protected-path access. Pins verified with sha256sum and wc -l.
Tools: none installed or upgraded.

### R1 (ancestor inputs stat before refusal): CLOSED
`resolve_guarded` runs `protected_reason_input "$lex"` on the lexical input at L358 when final=1, before the walk and before any lstat. Seed probes (final=0) are unaffected.

### R2 (startup stat of the store parent): ACCEPTED as an L1 decision
Disclosed in the header (L93-95): startup resolves each home's `.omp` parent to seed a relocated-store root. The fixture cannot see it: `trace_access` (L454) requires the substring "agent", and `…/home/.omp` does not contain it. "Parent stat only, no content" is therefore asserted by comment, not by the oracle. Low.

### R3a (readlink oracle): CLOSED
Fixture L438-446 matches the readlink path argument against AGENT and its descendants.

### R3b (bare root stat in refusal cases): CLOSED
`refusal_problems` calls `trace_access(..., allow_root_stat=False)` (L489), so a stat of AGENT itself is flagged in refusal cases.

### R3c (lenient mode scope): NOT AS CLAIMED. Medium
The IRC says lenient root-stat mode is used only for the scratch positive. The code does not do that: `positive_problems` calls `trace_access(res.trace)` with the default `allow_root_stat=True` at L528, and it serves cases 07, 08, 09 (including the home-store variant at L604), and 12. A bare store-root stat in any positive case is invisible.
Fix: `trace = trace_access(res.trace, allow_root_stat=scratch)`.

### Glob-follow (tool L933): CLOSED
The fleet loop is now `for d in "$root"/*; do` (no trailing slash), so bash does not stat-follow a fleet symlink there.
Residual, low-medium: `for reg in "$dir"/worktrees/*/gitdir; do` (L557) matches through repo-controlled entries under `.git/worktrees`. bash may stat-follow a symlinked intermediate entry [INFERENCE; not exercised]. Fix: iterate `"$dir"/worktrees/*`, skip `[ -L ]` entries before checking `"$w/gitdir"`.

### Oracle blind spot (medium): path-string matching only
`trace_access` matches the path text in each strace line. A kernel-followed symlink (for example `alias-child -> LEAK` in R14C2-12, or a worktree symlink) appears under the fleet path, so a stat or open that resolves into the store is never flagged. R14C2-12 therefore cannot fail on symlink-following.
Fix: for stat, open, readlink, and getdents lines, `os.path.realpath` the path argument (links still exist after the run) and test it under AGENT. Apply the same check to execve argv paths.

### /proc compare special path (L1003-1004): acceptable
`load_census` runs the `/proc`, `/dev/fd`, `/dev/stdin` refusal after `guard_path` (which walks symlinks lstat-only). The walk stays outside the store.

### Unreadable gitdir (L458-462): fail-closed, operability cost. Low
`find -P "$dir" -type d ! -readable -print -quit` walks the whole guarded gitdir with no `-maxdepth` on every repo before git. An unreadable subdirectory in `objects/` refuses the repo. Document the refusal and consider bounding the walk.

### Verdict on 1533 / 726
R1 closed. R2 accepted by L1 decision. R3 partially closed: R3a and R3b closed; R3c is misapplied and the realpath oracle is missing. C2 not ready to close until R3c is fixed and the realpath check lands.

### L1 commands (not run by this seat)
- `sha256sum tools/souji-census.sh tests/fixtures/r14-census-boundary.py`
- `grep -nE 'allow_root_stat' tests/fixtures/r14-census-boundary.py` (expect `scratch` passed at L528 once fixed)
- `grep -nE 'worktrees/\*/gitdir' tools/souji-census.sh` (expect none once fixed)
- `python3 -B tests/fixtures/r14-census-boundary.py --case R14C2-12`
- `python3 -B tests/fixtures/r14-census-boundary.py` (full, after fixes), then `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`



