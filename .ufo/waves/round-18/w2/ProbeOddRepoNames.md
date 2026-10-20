STATUS: PARTIAL — emitted TSV rows are byte-exact and parseable, but TAB/LF/CR repository basenames are silently dropped (never run, never bounded, no row) and an LF in `--root`/`--compare` is truncated instead of refused, so the C1 "every repository ... runs" clause does not hold for the odd names the attack names.

# Attacked claim (C1 operability, TSV integrity of repo names)

`tools/souji-census.sh` @ `5efb519f00075d958c3d1109ef6fcb24c487eb87` (tool sha256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`, identical to `git cat-file blob 5efb519:tools/souji-census.sh`): every repository (list-phase guards and `census_one`) runs in its own process group under `--repo-timeout N`; a timeout emits `<repo>\t0\t0\t0\t0\t\terror` plus stderr `souji-census: repo-timeout <N>s <repo>`; others measured; exit 0; protected refusal still exit 2. Specific ask: repo dirs named with a TAB, an LF and a leading dash, one hanging (writer-less FIFO `.gitignore`), under `--repo-timeout 3`; check the error row and stderr line are sanitized and parseable.

Fixtures built under `/var/tmp/souji-r18w2-ProbeOddRepoNames/work3` in a clone at 5efb519; `git` on PATH was a logging shim (records pgid + argv, then execs `/usr/bin/git`), so per-repo execution and process groups are observable. Host: git 2.56.0, bash 5.3.20. Nothing installed or upgraded; no pacman used.

## Observed — leading-dash name (hanging) and a normal neighbour

`bash tools/souji-census.sh --root /var/tmp/.../fleetA --repo-timeout 3` (children: `normal`, `tab<TAB>repo`, `new<LF>line`, `cr<CR>repo`, `-dashrepo` with FIFO `.gitignore`):

```
rc=0  wall_ms=5518  stdout_lines=3
repo<TAB>worktrees<TAB>unpushed<TAB>dirty<TAB>scratch_bytes<TAB>mtime_iso<TAB>verdict_flags
/var/tmp/.../fleetA/-dashrepo<TAB>0<TAB>0<TAB>0<TAB>0<TAB><TAB>error
/var/tmp/.../fleetA/normal<TAB>1<TAB>0<TAB>0<TAB>0<TAB>2026-10-20T18:21:33-03:00<TAB>clean
stderr: souji-census: repo-timeout 3s /var/tmp/.../fleetA/-dashrepo
awk -F'\t' NF!=7: 0 of 3 lines; non-souji stderr lines: 0
```

Byte checks: the dash row is `cmp`-identical to `printf '%s\t0\t0\t0\t0\t\terror\n' <repo>` (ROW-BYTE-EXACT yes); stderr is `cmp`-identical to `printf 'souji-census: repo-timeout 3s %s\n' <repo>` (STDERR-BYTE-EXACT yes). Matches the claimed row and message exactly (`tools/souji-census.sh:1693`, `:1709`; stderr `:1678`, `:1707`).

The guard phase (preflight loop) is bounded too: with the shim sleeping only on the guard's `git config --file .../-dashrepo/.git/config --list`, `--repo-timeout 3` gave rc=0, wall 5410 ms, the same byte-exact row/stderr, and `normal` still `clean`; zero leftover processes referenced the fixture afterwards. Shim log shows guard and census calls for the dash repo in two distinct pgids (2560733 vs 2563141; normal: 2562059 vs 2617036) in the main run — one process group per repo per phase, as claimed.

## Observed — TAB / LF / CR names are silently dropped

Same fleet: the TAB, LF and CR children each got **0 git invocations** (grep count in the shim log: `tab<TAB>repo` 0, `new<LF>line` 0, `cr<CR>repo` 0; dash 12, normal 13). They produce **no row and no stderr**. A fleet whose only child is `only<TAB>tab` returned rc=0, **header-only stdout**, 0-byte stderr, 63 ms.

Cause: `tools/souji-census.sh:1412-1414` — `case "$base" in *$'\n'*|*$'\t'*|*$'\r'*) continue ;;` runs before `GUARD_CANDIDATES+=` (`:1416`) and before `REPOS+=` (`:1431`), so such children never enter the guard loop or `census_one`. The mechanism the round-18 change added (`run_repo_with_watchdog`, guard loop at `:1665-1689`, `census_one` at `:1691-1715`) is never reached for them. The contract header (`:19-23`, `:25-57`, `:63-65`) does not mention this exclusion, and no diagnostic is printed, so a hanging or ordinary repo with such a name is invisible with exit 0.

Consequence for the ask: for the TAB and LF names there is **no error row and no `repo-timeout` line to sanitize** — `sanitize_field` (`:1031-1037`) is not exercised on the repo-timeout path by any TAB/LF path, because TAB in a `--root` is refused (below) and such children are dropped. The sanitize/parseability claim is only testable (and holds) for the dash name.

## Observed — TAB in `--root` refused; LF in `--root`/`--compare` truncated

* `--root /var/tmp/.../root<TAB>withtab` → rc=2, 0 stdout bytes, one stderr line: `souji-census: path-protected: ambiguous-path (input: /var/tmp/.../root^Iwithtab)` — protected refusal still exit 2 (`resolve_guarded:461`, `guard_path:522-526`). Holds.
* `--root $'/var/tmp/.../A\nB'` (that directory **exists** and contains repo `inB`) → rc=0, 383 ms, stderr empty, single row `repo=[/var/tmp/.../A/inA]` — i.e. the tool silently censused the sibling directory `A`, not the requested newline-named root. `--root $'/var/tmp/.../A\n'` likewise censused `A` (rc=0). `--compare $'base.tsv\njunk'` was accepted and compared against `base.tsv` (rc=0, diff header only).
* Cause: `lexical_abs` (`:278-295`) splits with `local IFS=/; read -r -a parts <<< "$p"` (`:286`); `read` stops at the first LF, so everything after an LF is discarded before the `*$'\n'*|*$'\t'*|*$'\r'* → ambiguous-path` refusal at `:461` ever sees it. Isolated reproduction of the exact idiom: `parts=6` for the newline path, result `/var/tmp/.../work3/A`; the same input with a TAB keeps `parts=7` and the TAB (which is why TAB/CR are refused and LF is not).

## Verdict

* TSV integrity of rows that are emitted: **holds** — 7 columns, no control characters, exact error row, exact stderr line, neighbours measured, exit 0, no leftovers; dash-named repos are guarded and censused in their own process groups.
* C1 'every repository (list-phase guards and census_one) runs in its own process group under `--repo-timeout`': **fails** for basenames containing TAB, LF or CR — they are dropped before any guard/process group, with no row, no diagnostic, exit 0. The claim's sanitization clause is vacuous for those names.
* 'protected refusal still exit 2': holds for TAB input; LF input bypasses the intended `ambiguous-path` refusal because `lexical_abs` truncates first (exit 1 'root is not a directory' on a nonexistent prefix, or silent census of the wrong directory, exit 0, when the prefix exists).
* Overall: **partial**.

## Smallest fix

1. `:1414` — keep the TSV-safe drop but make it observable: `printf 'souji-census: skipped-ambiguous-name %s\n' "$(sanitize_field "$d")" >&2` and add one contract sentence at `:19-23`. Do not emit a sanitized row: sanitization can map two distinct names to one key, which would then fail the `--compare` duplicate-repo check (`:1779`). A row requires control-character escaping (e.g. `\t` → `\\t`), not replacement.
2. `resolve_guarded` — test `$raw` for `*$'\n'*|*$'\t'*|*$'\r'*` and `protected_fail "ambiguous-path" input "$raw"` **before** the `lexical_abs` call at `:449/:453`, so `--root`/`--compare` with an LF exits 2 exactly like TAB does today; harden `lexical_abs:286` against line-based `read` (reject LF there too) so no internal caller can be silently truncated.

Cleanup: probe clone and all `/var/tmp/souji-r18w2-ProbeOddRepoNames` fixtures removed after the runs; no process from them remains; nothing was signalled that this seat did not start.
