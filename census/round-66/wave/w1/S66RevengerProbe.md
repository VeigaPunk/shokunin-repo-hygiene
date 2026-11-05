# S66RevengerProbe — host git env-route probes (round 66, wave 1)

Host: git 2.56.0, Python 3.14.8. Raw lines: `.ufo/waves/round-66/w1/S66RevengerProbe/probe.txt`.
Scope: read-only probes against throwaway repos created under `/fast/scratch/hyaku/souji-r66/S66RevengerProbe/` (removed after run). No host config, sysctl, lane, or sibling repo touched. No installs. Every probe re-run once; reruns agree with first runs.

## Results

| Probe | Env / argv | rc | Observed effect |
|---|---|---|---|
| P1 | `GIT_CONFIG_COUNT=1`, `KEY_0=core.excludesFile`, `VALUE_0=<excludes.txt>` (names `hidden.txt`); `status --porcelain` | 0 | **Hidden**: porcelain empty. Control without the env shows `?? hidden.txt`. Rerun identical. |
| P2 | `GIT_CONFIG_PARAMETERS="'core.excludesFile=<excludes.txt>'"` | 0 | **Hidden** (empty porcelain). Rerun identical. |
| P3a | `GIT_CONFIG_GLOBAL=<global.gitconfig with excludesFile>` | 0 | **Hidden** (empty porcelain). |
| P3b | `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` (same repo) | 0 | **Stops hiding**: `?? hidden.txt`. Rerun identical. This is the E3 repoint working. |
| P4 | `GIT_OBJECT_DIRECTORY=<copy of .git/objects>`; `cat-file -t HEAD` | 0 | Succeeds, prints `commit`. Rerun identical. The copy is complete, so it does not distinguish. |
| P4-ctl | `GIT_OBJECT_DIRECTORY=<empty dir>`; `cat-file -t HEAD` | 128 | Fails: `fatal: git cat-file: could not get object info`. Proves the redirect is honoured. |
| P5 | `GIT_ALTERNATE_OBJECT_DIRECTORIES=<empty dir>`; `cat-file -t HEAD` | 0 | Succeeds, `commit`. Local objects satisfy the read, so an empty alternate is harmless here. Rerun identical. |
| P6a | `GIT_REPLACE_REF_BASE=refs/replace-forged-r66` (no trailing slash) | **-6 (SIGABRT)** | Aborts: `BUG: refs.c:1908: ref pattern must end in a trailing slash when trimming`. Matches the instrument-commit note. |
| P6b | `GIT_REPLACE_REF_BASE=refs/replace-forged-r66/` (trailing slash) | 0 | Succeeds, `commit`. Rerun identical. |
| P6c | trailing-slash base + `refs/replace-forged-r66/<HEAD>` -> forged commit; `cat-file -p HEAD` | 0 | **Forged replace honoured**: output shows `FORGED`. |
| P7 | env `GIT_CONFIG_COUNT` hiding file AND argv `-c core.excludesFile=/dev/null` | 0 | **Command-line `-c` wins**: `?? hidden.txt` shown. Rerun identical. |
| P8 | replace ref `refs/replace/<HEAD>` -> forged commit; `cat-file -p HEAD` | 0 | Plain read shows `FORGED`. With `GIT_NO_REPLACE_OBJECTS=1` (rc 0) shows the original message `base`. Rerun identical. |
| P9 (4644) | `os.chmod(0o4644)`; `os.stat & 0o777` vs `& 0o7777` | 0 | `&0o777=0o644`, `&0o7777=0o4644`. The low-bits view hides setuid. |
| P9 (1644) | `os.chmod(0o1644)` | 0 | `&0o777=0o644`, `&0o7777=0o1644`. Sticky hidden by low-bits mask. |
| P9 (2644) | `os.chmod(0o2644)` | 0 | `&0o777=0o644`, `&0o7777=0o2644`. Setgid hidden by low-bits mask. |
| P9 (0644) | `os.chmod(0o644)` | 0 | Identical under both masks (control). |

## Findings for the C1 design

1. **E1 and E2 are real routes.** Both the `GIT_CONFIG_COUNT` pair and the legacy quoted `GIT_CONFIG_PARAMETERS` form hide an untracked file from `status`. The writer must refuse presence of both; it cannot rely on value shape.
2. **E3 repoint works as designed.** Pointing `GIT_CONFIG_GLOBAL` at `/dev/null` with `GIT_CONFIG_NOSYSTEM=1` removes the hiding. Being a pin, it must be applied on every git call, and the env refusal (as the matrix states) still applies to the caller-set variable.
3. **E4 (object-dir redirect) and the control.** A redirect to an empty dir breaks reads, so the redirect is observable. A redirect to a full copy is indistinguishable from honest, which is why the writer must refuse presence rather than test content.
4. **E5 is harmless on this host** (P5 passes with an empty alternate). The row's `refuse` class therefore rests on presence, not on an observed forgery effect of this specific shape. [INFERENCE for alternates that point at real objects; not measured here.]
5. **E6 has two sides.** The no-slash form aborts git with SIGABRT (rc -6); the slash form forges (P6c). The writer's refusal of the variable's presence is needed; the abort alone is not a defence.
6. **Command-line `-c` overrides env-injected config (P7).** A writer pin `-c core.excludesFile=<null>` on every call therefore takes precedence over a caller `GIT_CONFIG_COUNT` injection. This supports the frozen design, but the env refusal is still needed for the other routes (GIT_CONFIG_GLOBAL/PARAMETERS, replace/object routes).
7. **P8 confirms `GIT_NO_REPLACE_OBJECTS=1` restores the original view**, so pinning it on every call defeats forged replace refs in the default namespace. It does not defeat the custom base in P6c unless the variable is also refused; that is why E6 needs presence refusal.
8. **MOD2/MOD3 mask gap confirmed (P9).** Snapshotting `st_mode & 0o777` loses setuid/setgid/sticky; `& 0o7777` keeps them. A flip 644 -> 4644 is invisible to the low-bits snapshot, matching the MOD2 row's stated base behaviour.

## Confidence
High for P1-P3, P6, P7, P8, P9: each observed twice with identical outcome. Medium-high for P4/P5: the redirect is shown by the control (P4-ctl), but P4 and P5 alone do not prove a forgery. Git version is the single host dependence; these results are not claimed for other git versions.

## Tools / installs
None. No packages installed; no host state changed. Scratch removed after the run.
