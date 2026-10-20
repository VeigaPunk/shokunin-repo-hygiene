# SafetyOperator — round 13 w1 (sentinel, leaf)

Scope: write scopes and git workflow, protection of the operator-authored census, active sibling repos, and the safety of the final validation. I made no edits to the lane or to any other repo. This report is my only write. I read no content from the operator sweep; only `find -printf` metadata and `git status` names. My one runtime probe was a throwaway git+FIFO fixture under `mktemp -d /var/tmp/souji-r13-safetyop.XXXXXX`. Its trap removed it; a residue count afterwards was `0`. I make no claim to independent non-author status. Certification stays OFF.

Axes: calibration (claims match bytes), operability (checks finish and fail closed), coverage (every write path and guard is named).

Tool installs and updates: none.

## Observed baseline (2026-10-20, ~02:15 -0300)

| fact | command | value |
|---|---|---|
| lane top level and HEAD | `git -C <lane> rev-parse --show-toplevel HEAD` | `/home/vgpnk/Projects/shokunin/souji-shokunin`, `31984f47…` |
| upstream | `git -C <lane> status -sb` | `## master...origin/master` (0/0) |
| worktrees, stash, locks | `worktree list --porcelain`; `for-each-ref refs/stash`; `ls .git` | 1 worktree; no stash; no `index.lock`/`gc.pid` |
| maintenance config | `git config --global/--system --get-regexp '^(maintenance\|gc\.)'` | none set (exit 1), so auto-maintenance is at git 2.55.0 defaults |
| fleet repo nesting | `git -C /home/vgpnk/Projects/shokunin check-ignore -v souji-shokunin/` | `.gitignore:1:*-shokunin/`, so the lane is ignored by the fleet repo |
| sweep metadata fingerprint | `find <lane>/census/operator-sweep-20261019 -printf '%P\t%y\t%s\t%T@\t%m\n' \| LC_ALL=C sort \| sha256sum` | `f6a844662f23ec8b0026d3f48bb19d8b27bb137f7ebd57e273c201b8539782b8`; 155 entries; `status -uall` 152 lines; no FIFO, symlink, socket or device files |
| filesystems | `df`, `stat -c %d` | `/var/tmp` btrfs st_dev 31; lane st_dev 57 (same `/dev/mapper/root`, different subvolumes); `/tmp` and `/dev/shm` are tmpfs |
| `/var/tmp` souji residue | `find /var/tmp -maxdepth 1 -name 'souji*' \| wc -l` | 1681, including 11 `souji-r12-*` (2026-10-19 18:45–19:01) and `souji-r13-attackcov-script.SY95q4.sh` (02:14) |

## Findings

### F1 — HIGH (calibration): shared bookkeeping already cites r13 artifacts that do not exist

- **Evidence:**
  - L1 (`SoujiR13`) wrote these files after dispatch. Dispatch was at `w1-dispatch.json` mtime 02:11:33; the writes ran 02:12:39 → 02:13:19. Transcript `history://SoujiR13` lines 135, 139, 143, 147, 163, 167, 201:
    - `corpus/knowledge/git-repo-structure-readonly.md` (new)
    - QUALITY Q17/Q18 (new rows)
    - SOURCES S005/S006 cells
    - PROVINCE F2 "bounded structure probe and isolated write-safety fixture acquired r13"
    - SHONEN marks cut
    - `census/round-13/claims.json`
    - `corpus/lessons/round-13.md`
  - The new entry's line 2 cites `census/round-13/verification.json` and its line 3 cites `bash tests/fixtures/r13-repo-structure.sh --selftest`.
  - PROVINCE cites `tools/souji-repo-structure.sh`.
  - A `test -e` at probe time returned `MISSING` for all three, and for `tests/fixtures/r13-cert-evidence.py` and `tests/fixtures/r13-quarantine-bounds.sh`. Only `tools/souji-cert-evidence.py` existed.
- **Exploit path:** this is the r12 K5 class again (`corpus/lessons/round-12-verifier-spotcheck.md:13`: "Gate claimed a committed fixture that does not exist"). It happens if L1 commits these files before the SizeProbe/EvidenceGate/BoundQuarantine artifacts land, or if a seat's artifact is later abandoned.
- **Impact:** an admitted entry and a PROVINCE "acquired" claim would have no backing bytes. That is fabricated readiness.
- **Smallest remediation:** a closing gate (G3 below) that runs `test -f && ! test -L` on every cited path. Use Q17's own validator once it lands. On any miss, revert the cell and hold the entry.
- **Context:**
  - L1 owns integration, so this is not a seat write-scope breach.
  - The SHONEN marks cut was disputed by ReviewSHONEN; their reply (`history://SoujiR13:203`) conceded the error. I did not re-adjudicate it.

### F2 — MEDIUM (operability and safety): adding `timeout` to the untracked `mv` can delete live files

- **Evidence:**
  - `tools/souji-quarantine.sh:536` runs `mv -- "$ct" "$qpath"` and `:529` runs `git -C "$crepo" mv`. At probe time, `grep timeout` over the tool found 0 matches, so the Q8 edit has not yet landed.
  - GNU coreutils 9.11 `coreutils.info:8355-8361`: "'mv' falls back on copying as if by 'cp -a', then … it removes the original."
  - This host has different st_dev values on one disk (31 vs 57).
- **Exploit path:** a target sits on a different subvolume or mount from `<repo>/.ufo-quarantine`. `rename(2)` then fails with EXDEV and `mv` copies, then removes. If `timeout` fires during the remove phase, the live source is partly deleted with no hold and no second receipt check. That breaks the assignment's "never delete after timeout".
- **Impact:** partial live data loss. Likelihood is low (it needs a nested mount or subvolume inside a repo); impact is high.
- **Smallest remediation:**
  - Before staging, require `stat -c %d "$(dirname "$ct")"` = `stat -c %d "$(dirname "$qpath")"`. Otherwise return NOT-AUTHORIZED `cross-device`, with no `mv`.
  - A timed-out `git mv` can leave `.git/index.lock`. Report it as STAGE2-FAILED and never remove it automatically.
  - I sent this to `SoujiR13.BoundQuarantine` by peer message.

### F3 — MEDIUM (calibration): the digest helpers can return success without measuring anything

- **Evidence:**
  - `tools/souji-quarantine.sh:184` is `file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1 || true; }`.
  - Probe P5: the same shape under `timeout 3` on a FIFO returned `rc=0 out=[]`.
  - The current callers fail closed only because they compare against a non-empty pin: `:286` (`[ -n "$now_sha" ]`), `:349-350`, and the `:750` `is_hex64`. The `|| continue` at `:795` is dead code, because `file_sha` always returns 0.
  - `dir_digest` at `:186-194`: `xargs -0 -r sha256sum 2>/dev/null | sha256sum` then `return 0`.
- **[INFERENCE] from the code, not executed:** an unreadable file inside the directory drops out of both the pin manifest and the recheck manifest. They still match, so the check reports PASS for bytes it never measured. `find -type f` also skips FIFOs and devices silently instead of refusing them.
- **Exploit path:** if the Q8 patch decides on rc (for example `if file_sha …`) instead of non-empty plus exit 124, a stall turns into a pass. Special files inside a directory stay uncovered.
- **Smallest remediation:**
  - Capture the rc explicitly: `out=$(timeout -k 5 30 sha256sum -- "$f") || rc=$?`, and treat 124/137/non-zero as could-not-evaluate.
  - In `dir_digest`, refuse when `find . -path ./.git -prune -o ! -type f ! -type d -print -quit` is non-empty, and propagate the xargs failure.

### F4 — MEDIUM (Q4): the installed self-tests default their scratch to `/tmp`

- **Evidence (all `${TMPDIR:-/tmp}`):**
  - `tools/souji-quarantine.sh:1247` and `:1519`
  - `tools/souji-verify.sh:1105`
  - `tools/souji-vault-verify.sh:1308`
  - `tools/souji-census.sh:418` and `:516`
  - `tests/runner-23.sh:38`, `runner-27.sh:46`
  - `tests/runner-25.sh:69` goes further and refuses any scratch not under `/tmp`.
- **Exploit path:** L1 runs a whole-tool `--selftest` as a final check with TMPDIR unset. Fixtures land on 16G tmpfs `/tmp`, which violates Q4 and the lane contract ("All fixture writes strictly mktemp under /var/tmp").
- **Smallest remediation:**
  - Every final self-test runs with `TMPDIR=/var/tmp` in a fresh `bash`.
  - Do not run `runner-25.sh` this round; it cannot comply.
  - The new validator already hard-codes `/var/tmp` (`tools/souji-cert-evidence.py:937`, `:1099`).

### F5 — MEDIUM (protecting the operator sweep): git commands that would sweep or remove it

- **Evidence:** fixture probe P3 — `git stash push -u` returned `rc=0 sweep-exists=no`: untracked files leave the worktree until popped.
- **Commands that must not appear in this round:**
  - `git clean` (any flags except `-n`)
  - `git stash -u`/`-a`
  - `git add -A`, `git add .`, `git add census`
  - `git commit -a`
- **Impact:** irreversible loss of 152 operator-authored files, or committing them.
- **Smallest remediation:** guards G1 and G6 below. On any fingerprint change, stop and report; never "restore" it.

### F6 — MEDIUM (git workflow): the SKILL commit line fails for new files, and `fleet-commit.sh` is the wrong tool

- **Evidence:**
  - `SKILL.md:115` gives `git -C <repo> -c maintenance.auto=false commit -- <approved paths>`.
  - Probe P1: `commit -- <untracked>` fails with `error: pathspec 'new' did not match any file(s) known to git`, `rc=1`.
  - Probe P2: `add -- <path>` then `commit -- <path>` returned `rc=0`, and the sibling untracked directory stayed untracked (`sweep-tracked=0`).
  - Round 13 adds at least 8 new files.
  - L1 read `scripts/hyaku/fleet-commit.sh` (`history://SoujiR13:130`). That script works on the fleet repo (`:12`, `:39 cd "$FLEET"`), commits without `-c maintenance.auto=false` (`:53`), and pushes (`:63`). Lane paths are ignored there (fleet `.gitignore:1`).
- **Exploit path:** L1 tries the SKILL line, hits the failure, and improvises with `add -A`. Or L1 routes through `fleet-commit.sh`, which runs auto-maintenance and pushes the fleet repo.
- **Smallest remediation:** commit with G5: an explicit `add --` followed by `commit --` with the same path array, the guard flag and the lane identity. Record the remediation of `SKILL.md:115` in r13 bookkeeping (L1's scope, not mine).

### F7 — LOW-MEDIUM (operability and calibration): the omp shell's builtins shadow coreutils

- **Evidence:**
  - In the persistent harness shell, `type mv timeout sha256sum find rm` reports `shell builtin`.
  - `mv --version` prints `mv 0.8.0`, and `timeout --version` prints a usage error.
  - In a fresh `bash -c`: `/usr/bin/timeout` is `GNU coreutils 9.11` and `/usr/bin/mv` is GNU.
  - The builtins are not exported, so the scripts themselves get GNU tools.
- **Exploit path:** a guard typed inline in the harness, such as `timeout 30 sha256sum F` or a recorded tool version, measures a different implementation from the one the tool uses. The evidence then misstates the tool version, which breaks Q1.
- **Remediation:** run every final check as `bash -c '…'` or `bash <script>`, and record versions via `/usr/bin/<tool> --version`.

### F8 — LOW (operability): the quarantine self-test can fail while other seats are still writing

- **Evidence:** `tools/souji-quarantine.sh:1316` and `:1490-1494` compare the live lane's `status --porcelain | grep -c .` before and after (H3).
- **Exploit path:** a seat or L1 creates a file in a new tracked directory during the self-test. H3 fails falsely, or a retry hides a real failure.
- **Remediation:** run final checks only after every w1 seat has landed (all seats are no-commit leaves). Re-check the porcelain count right before and after the self-test.

### F9 — INFO (sibling repos): status snapshot; nothing for souji to touch

- **Evidence:** read-only status across 21 `*-shokunin` repos; all are 0/0 against upstream.
  - `tabi-shokunin`: 6 `M`, 2 `??`, with an active `TabiR13.*` wave.
  - `game-dev-2d-shokunin`: 3 linked worktrees, all `locked souji r5: pinned…`.
  - `kotodama-shokunin`: linked worktree `.scratch/ca02-wt-r34` with no `locked` line.
  - `game-dev-3d-shokunin` and `lore-shokunin`: 1 untracked file each.
- **Risk:**
  - Running the C3 probe or any quarantine/receipt flow against a live sibling this round reads a moving tree; that applies to tabi above all.
  - AGENTS.md:10 forbids touching an artifact whose owning lane has dirty work.
  - Any commit inside kotodama could auto-prune its unlocked registration (round-12 M51). That is their lane's problem: report it, do not act on it.
- **Remediation:** final checks target `/var/tmp` fixtures only. Do not use `--repo` on any sibling.

### F10 — LOW (Q4 hygiene): `/var/tmp` residue

- **Evidence:** 1681 `souji*` entries, including 11 `souji-r12-*` despite trap cleanup, and one r13 file already: `souji-r13-attackcov-script.SY95q4.sh`.
- **Why it was left behind:** to-verify; a killed run or a trap gap are possible causes.
- **Action:** cleaning this up would be a deletion outside lane scope, so do not do it. Gate only on no new `souji-r13-*` residue after the final checks (G4).

### F11 — INFO (calibration limit of the C1 validator)

- **Evidence:** `tools/souji-cert-evidence.py:39-42`, `:67-70`, `:140-144`. It resolves against `--root`, uses O_NOFOLLOW/O_NONBLOCK with an fstat regular-file check, works in `/var/tmp` mkdtemp, and states its limits.
- **Limitation, [INFERENCE] (I did not read the author-uniqueness logic):** the `author` field is self-declared. The validator can catch duplicate fragment paths and duplicate author strings, not who actually wrote the bytes. A relay that writes two fragments under two names passes.
- **Remediation:** state this in the C1 claim. Bind each fragment path to its seat (one fragment per `.ufo/waves/round-13/<wave>/<Seat>.*`). Run it as `python3 -I` so `PYTHONPATH` or a `sitecustomize` cannot inject code.

## Guard commands for L1, in order, after every seat has landed

Run each in a fresh `bash -c`, not in the harness shell (F7). `L=/home/vgpnk/Projects/shokunin/souji-shokunin`.

```bash
# G0 right repo, clean git state
git -C "$L" rev-parse --show-toplevel                        # == $L
test ! -e "$L/.git/index.lock" && git -C "$L" stash list | wc -l   # 0

# G1 operator sweep untouched (metadata only; no content read)
find "$L/census/operator-sweep-20261019" -printf '%P\t%y\t%s\t%T@\t%m\n' | LC_ALL=C sort | sha256sum
#   == f6a844662f23ec8b0026d3f48bb19d8b27bb137f7ebd57e273c201b8539782b8 ; on mismatch STOP
git -C "$L" status --porcelain -uall -- census/operator-sweep-20261019 | wc -l   # 152

# G2 residue baseline
before=$(find /var/tmp -maxdepth 1 -name 'souji-r13-*' | wc -l)

# G3 every path the bookkeeping cites exists as a regular, non-symlink file (F1)
for p in tools/souji-cert-evidence.py tests/fixtures/r13-cert-evidence.py \
         tools/souji-quarantine.sh tests/fixtures/r13-quarantine-bounds.sh \
         tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh \
         census/round-13/verification.json corpus/knowledge/git-repo-structure-readonly.md; do
  [ -f "$L/$p" ] && [ ! -L "$L/$p" ] && echo "ok $p" || echo "MISSING $p"; done

# G4 bounded self-tests, /var/tmp only (F4), GNU tools (F7); then residue
TMPDIR=/var/tmp /usr/bin/timeout -k 10 900 bash "$L/tools/souji-quarantine.sh" --selftest; echo rc=$?
TMPDIR=/var/tmp /usr/bin/timeout -k 10 300 python3 -I "$L/tools/souji-cert-evidence.py" --selftest; echo rc=$?
shellcheck -S warning "$L/tools/souji-quarantine.sh"; echo rc=$?
after=$(find /var/tmp -maxdepth 1 -name 'souji-r13-*' | wc -l); echo "residue $before -> $after"   # no increase
#   (the r13 fixtures/probes have their own commands in census/round-13/final-checks.md once written)

# G5 guarded, path-limited lane commit (F5/F6); PATHS = approved landed r13 set, never a directory glob over census/
PATHS=( ... )                                                  # explicit files only
git -C "$L" add -- "${PATHS[@]}"
git -C "$L" -c maintenance.auto=false -c user.name=souji-shokunin -c user.email=souji@shokunin.local \
    commit -m "<msg>" -- "${PATHS[@]}"

# G6 post-commit: only approved paths, sweep still untracked and unchanged
git -C "$L" show --name-only --format= HEAD | grep -c '^census/operator-sweep-20261019/'   # 0
git -C "$L" show --name-only --format= HEAD | grep -vxF -f <(printf '%s\n' "${PATHS[@]}") | wc -l   # 0
#   re-run G1 (same sha256, 152)
```

Never run:
- `git clean`, `git stash -u/-a`, `git add -A/./census`, `git commit -a`
- `scripts/hyaku/fleet-commit.sh` for lane paths
- `tests/runner-25.sh`
- any souji probe or tool with `--repo`/`--root` aimed at a live sibling
- any `--hold`/non-dry-run quarantine against a live path

## Limitations

- Every observation is from ~02:15 and the seats are still writing, so the tool state (Q8 not yet landed) and the missing-artifact list will change. G3 and G4 must be re-run on the final bytes.
- F3's unreadable-file behaviour and F11's author limit are inferred from the code, not executed.
- I did not review the correctness of BoundQuarantine, EvidenceGate or SizeProbe beyond the cited lines.
- The cause of the r12 `/var/tmp` residue is to-verify.
- `git repo structure --format=lines` worked on my throwaway fixture (P8, rc 0). I make no read-only claim about the live repos.
