STATUS: DONE — wave-1 gap confirmed: census git status/check-attr open `/etc/gitattributes`; the r18 watchdog does bound the resulting FIFO hang (12.413 s / 3 repos at `--repo-timeout 2`), and a one-line `GIT_ATTR_NOSYSTEM=1` mutant removes the open with B1–B8 8/0 and selftest 62/0.

# ProbeGitAttrNosystem — `GIT_ATTR_NOSYSTEM` gap in `tools/souji-census.sh`

Attacked claim: C1 operability + wave-1 gap “census lacks `GIT_ATTR_NOSYSTEM=1`”.
Worktree: `/var/tmp/souji-r18w2-ProbeGitAttrNosystem/lane` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`.
Host: git 2.56.0, strace 7.2, kernel 7.2.11-arch1-1. No tools installed (strace/git/`unshare` already present).
`/etc/gitattributes` does not exist on this host (latent gap, not a live effect).

## Findings (observed)

**F1 — the file is really opened.** The exact census status argv (`tools/souji-census.sh:1165-1172`: `--no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null status --porcelain …`) run under the census env (`:189-200`) on a synthetic repo:

```
openat(AT_FDCWD, "a.txt", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/etc/gitattributes", O_RDONLY) = -1 ENOENT
openat(AT_FDCWD, "/dev/null", O_RDONLY) = 4
openat(AT_FDCWD, ".gitattributes", O_RDONLY|O_NOFOLLOW) = -1 ENOENT
openat(AT_FDCWD, ".git/info/attributes", O_RDONLY) = -1 ENOENT
```

Same for the guard lookup `guard_bound_filters` (`:1128-1135`, `git … check-attr -z --stdin filter`):
`openat(AT_FDCWD, "/etc/gitattributes", O_RDONLY) = -1 ENOENT`.
Re-running both with `GIT_ATTR_NOSYSTEM=1` removes the `/etc/gitattributes` open (only the in-tree `.gitattributes` remains).
The env block has `GIT_CONFIG_NOSYSTEM=1` but no `GIT_ATTR_NOSYSTEM` (`:189-191`); `-c core.attributesFile=…` overrides only the *global* file — it does not suppress the system one, as the trace order shows. So `GIT_CONFIG_NOSYSTEM` is not a substitute.

**F2 — FIFO hang is bounded by r18, at full-bound cost per repo.** With `/etc/gitattributes` a FIFO (ephemeral private mount namespace over `/etc`, host untouched):
- direct status, census argv: hung → killed by `timeout 4`, rc 124; with `GIT_ATTR_NOSYSTEM=1`: rc 0.
- `souji-census.sh --root fleet3 --repo-timeout 2`: rc 0, 4 s, row `<repo>\t0\t0\t0\t0\t\terror`, stderr `souji-census: repo-timeout 2s <repo>`.
- 3-repo fleet, `--repo-timeout 2`: **12.413 s**, 3 × `repo-timeout 2s`, 3 `error` rows, rc 0; no leftover census/git from my run.
So C1’s bound holds, but every repo whose status performs an attribute lookup pays the full bound (2 s bound + 2 s TERM/KILL grace ≈ 4.1 s/repo here; at the default 600 s that is ≈602 s/repo, sequential ⇒ a host-level FIFO stalls a whole fleet at ~10 min/repo). A root-owned `/etc` FIFO is not repo-reachable, so this is operator robustness, not a repo attack.

**F3 — no operator workaround.** The script clears every inherited `GIT_*` (`:187`, `compgen -v GIT_`), which includes `GIT_ATTR_NOSYSTEM`. Census invoked with `GIT_ATTR_NOSYSTEM=1` in the environment still timed out on the FIFO (rc 0, 4 s, same diagnostic). The fix must be in-script.

**F4 — host attrs can bind a repo-configured filter, but the guard stays symmetric.**
Regular `/etc/gitattributes` = `* filter=evil`, repo config `filter.evil.clean` writes a marker: direct status with the census argv ran the driver (marker 3 lines); census emitted `status-skipped: filter-driver-bound`, dirty `unverifiable`, marker absent. Reason: `check-attr` reads the same stack, so the fail-closed guard sees the binding. After the fix both sides are blind consistently (mutant measured dirty=1, marker absent). Host attrs therefore degrade a measurement to `status-unverifiable`, they do not execute a driver under census today.

**F5 — the system file is followed as a symlink; in-tree attrs are not.** `/etc/gitattributes → /var/tmp/…/attrs-target` (`*.c text eol=crlf`), `check-attr` returned `a.c\0text\0set\0`, i.e. the target’s content was parsed; strace shows `openat("/etc/gitattributes", O_RDONLY) = 3` (no `O_NOFOLLOW`), versus `openat(".gitattributes", O_RDONLY|O_NOFOLLOW)`. `/etc` is not in `PROTECTED_HOME_ROOTS` (`:263`, `:330-373`), so a root-planted symlink into a protected root would be read unguarded — root-only defense-in-depth gap, not repo-escapable.

**F6 — no test pins the knob.** `tests/fixtures/r18-census-bounded.py:160-180` (`setup_env`, `GIT_CONFIG_NOSYSTEM` at :172) and `:350-365` (census env, :363) omit it; `tests/fixtures/r17-census-hygiene.py:105-108` `GIT_ENV` omits it; the 62-check selftest asserts no exported env. B4 covers a work-tree `.gitattributes` FIFO (`r18-census-bounded.py:920-1000`), not the system file.

**F7 — silent count change not demonstrated.** `*.txt text eol=crlf` in `/etc/gitattributes` did not change `git status --porcelain` (dirty 1 with and without) or the census dirty count; I do **not** claim count corruption. The demonstrated measurement effect is only the fail-closed `status-unverifiable` (F4).

## Verdict

**Partial.** The C1 boundedness claim holds under a hostile system attributes file (F2), and there is no repo-level code execution (F4). But the wave-1 gap is real: census opens a host-global attribute file it neither models nor can override (`-c core.attributesFile` cannot suppress it), pays the full per-repo bound when that path is a FIFO, and blocks the only operator-level mitigation by clearing inherited `GIT_*` (F1–F3, F6).

## Smallest fix (verified on a `/var/tmp` mutant, not the lane)

1. One line at `tools/souji-census.sh:191`:
   `export GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 GIT_ATTR_NOSYSTEM=1`
2. Header note next to the `:149-151` env discipline sentence (“global/system config cleared”) that the system attributes file is disabled too.
3. Pin it with a fixture assertion (unprivileged fixtures cannot create `/etc/gitattributes`, so assert the env instead): extend the B-series shim (`r18-census-bounded.py`, `R18_REAL_GIT` wrapper) to log `$GIT_ATTR_NOSYSTEM` and require `1` on every census git call; optionally add `GIT_ATTR_NOSYSTEM` to `r17-census-hygiene.py:105` `GIT_ENV`.

Mutant = original + that line: sha256 `eb916efc…f077f8` (original `5efb519:tools/souji-census.sh` = `7e6a92d4…0bcd`), `bash -n` OK.
- `r18-census-bounded.py --census <mutant>`: `SUMMARY total=8 failed=0` (B1–B8 all PASS).
- `<mutant> --selftest`: `selftest: 62 checks, 0 failed`, rc 0.
- FIFO `/etc/gitattributes`, 3-repo fleet, `--repo-timeout 2`: base 12 413 ms / 3 timeout rows / 3 `error`; mutant 647 ms / `dirty=1` on all 3 / stderr 0 bytes; strace of the mutant shows **no** `/etc/gitattributes` open.
- In-tree `.gitattributes` binding `filter=evil` still yields `status-skipped: filter-driver-bound` and no driver run; regular `/etc` binding after the fix yields dirty=1 with no driver run.

## Exact commands (all under `/var/tmp/souji-r18w2-ProbeGitAttrNosystem`)

```
git clone --quiet --no-local <lane> lane && git -C lane checkout --quiet --detach 5efb519…
env -i PATH=/usr/bin:/bin HOME=… GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 GIT_NO_LAZY_FETCH=1 \
  GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false \
  GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null \
  strace -f -qq -e trace=openat,open,stat,newfstatat -o trace-A.txt \
  git -C synth --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null \
    -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null \
    status --porcelain --ignore-submodules=all --untracked-files=normal -- .   # rerun with GIT_ATTR_NOSYSTEM=1 → trace-B.txt
sudo unshare --mount --propagation private bash ns-test.sh   # tmpfs over /etc inside the namespace only
sudo unshare --mount --propagation private bash ns-test3.sh  # mutant under FIFO / filter / in-tree attrs
sudo unshare --mount --propagation private bash ns-test4.sh  # 3-repo bounded cost
python3 tests/fixtures/r18-census-bounded.py --census <mutant>
```

Workspace and clone deleted after the run; outputs above are quoted verbatim from the transcript.
