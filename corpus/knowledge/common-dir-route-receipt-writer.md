source: S300 — git setup.c / environment.c / git(1) § ENVIRONMENT VARIABLES at tag v2.56.0 (https://raw.githubusercontent.com/git/git/v2.56.0/setup.c; https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git.adoc; accessed 2026-11-05; HTTP 200 on fetch — capture and quotes in `census/round-67/wave/w1/S67ScoutSources/`); S298 — git(1) § ENVIRONMENT VARIABLES (https://git-scm.com/docs/git; accessed 2026-11-05; HTTP 200)
verified-at: f70da577eb1e1624cc63ab8fd0468565927d9b6a (the landed revision of `tools/souji-receipt-write.py`, sha256 b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725; host git 2.56.0)
recheck: `env -u GIT_COMMON_DIR -u GIT_NO_REPLACE_OBJECTS python3 -B census/round-67/c1-counter.py --root LANE --matrix census/round-67/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev <full40> --tool tools/souji-receipt-write.py --work DIR` must print `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS` and `EXIT=0`; rows W1-W3 inside it are the re-verification point for this entry

# A caller-injected GIT_COMMON_DIR must be value-checked, not presence-refused

ground: F4-adjacent — receipt hygiene: the receipt writer decides "clean" by reading git through the repository's common directory. A caller-set `GIT_COMMON_DIR` picks that directory, so it can point the dirty check at a copy whose config hides a change. Extends `knowledge/caller-env-routes-receipt-writer.md` (round 66), which refuses the config and object-redirect names by presence and names this route as open.

## Claim

`GIT_COMMON_DIR` is the environment route the round-66 writer left open (round-66 W2, `census/round-66/probes/w2-w3-env-probe.txt`). Git honours it as the repository's common directory:

- In `setup.c`, `get_common_dir()` takes `getenv(GIT_COMMON_DIR_ENVIRONMENT)` and uses that value as given, ahead of the on-disk `commondir` file (S300, `setup.c`, quote: `const char *git_env_common_dir = getenv(GIT_COMMON_DIR_ENVIRONMENT); if (git_env_common_dir) { strbuf_addstr(sb, git_env_common_dir); return 1; }`, 13 words, whitespace-normalized match in the capture).
- The documented contract is the same: "If this variable is set to a path, non-worktree files that are normally in $GIT_DIR will be taken from this path instead." (S300 / S298, git(1) § ENVIRONMENT VARIABLES, 22 words, normalized match).
- The repository struct then binds the value, so later reads follow it (S300, `setup.c` `apply_gitdir_and_environment`, `.commondir = getenv_safe(...)`).

Consequence measured at the round-67 base (`census/round-67/controls/c1-do-nothing.txt`): a copy of the repository's `.git` whose config carries `core.fileMode=false`, pointed to by `GIT_COMMON_DIR`, hides a tracked 755→644 change from the writer's dirty check. The base writer then writes a receipt over the hidden change (rows W1, W2 accept on base).

## Rule (round 67, C1)

The receipt writer:

1. resolves the repository's own common directory with `git rev-parse --git-common-dir` under `-C <root>`, with `GIT_COMMON_DIR`, `GIT_DIR` and `GIT_WORK_TREE` scrubbed and the round-66 pins kept;
2. when `GIT_COMMON_DIR` is set at all (an empty value included), canonicalizes both the caller's value and git's resolved path with `os.path.realpath` and refuses with `RECEIPT-ENV-COMMONDIR-MISMATCH` if they differ or the resolution fails. It prints the variable name only, never the value (the r65 sentinel redaction rule);
3. accepts an equal value without change (row W3). A harmless, already-neutralized value must keep working (the Q22 value/effect-aware rule);
4. removes `GIT_COMMON_DIR` from the environment of every git call the writer makes, next to the round-66 scrubbed names.

The check is value-aware where round 66's presence refusals were not. A presence refusal would abort every run that sets the variable to the true value.

## Named limits (not claimed)

- **Relative values with the writer's cwd different from the root (measured, candidate fails closed).** The writer compares `realpath(value)` against cwd-relative resolution with the root-relative git output. Probe: `cd` to a parent of the repository, `GIT_COMMON_DIR=.git`. Base accepts (rc 0). Candidate refuses with `RECEIPT-ENV-COMMONDIR-MISMATCH` (rc 2), although git itself, run with `-C <repo>`, resolves `.git` to the repository (`git -C <repo> rev-parse --git-common-dir` prints `.git`). Git resolves the relative value against `-C`, the root. The round-67 prereg text said "the same rule git applies", which is true only for git's own `-C` calls. The candidate can refuse an honest run here, but it never accepts a redirect that git would honour, so this is a fail-closed trade. Operator ruling pending (L0 line in `.ufo/l0-questions.md`, round 67).
- **Submodule contexts.** git's `worktree.c` (`submodule_uses_worktrees`) reads the submodule common dir with `get_common_dir_noenv` and comments "The env would be set for the superproject" (S300, `worktree.c`, 13 words). The writer's check reads only the root's own common dir; a submodule root is not separately measured.
- **Start-of-run only.** The value is read once at writer start. A change made during the wrapped command is outside the check (the same scope as the r62 index-flag check).
- **Not covered:** `GIT_NAMESPACE` and `GIT_CEILING_DIRECTORIES` (S300: `GIT_NAMESPACE` is read from the caller env, `environment.c` `get_git_namespace`; `GIT_CEILING_DIRECTORIES` is read-only in git, `setup.c`). Neither is refused or pinned by round 67 (the named L3 limit).
- **The counter itself.** `c1-counter.py`'s `clean_env()` does not scrub `GIT_COMMON_DIR` from the operator's shell, so a run with that variable set in the shell measures a different instrument. The operator run procedure is `env -u GIT_COMMON_DIR -u GIT_NO_REPLACE_OBJECTS`, and the next frozen counter adds the scrub (sentinel M1, `S67SentinelScope/scope.md`).

## What round 67 does not claim

- Ignore routes and repository-local config keys: a repository-local `core.excludesFile` is closed by the writer's `-c core.excludesFile=<devnull>` pin on every call (revenger PK3, `S67MutKill/k67-decision.md`). That closure is a proposed fixture row, not a frozen row this round, so the round-66 named limit L1 wording that it stays open is not corrected here (the prereg is frozen).
- A repository-local `core.fileMode` or a caller-named global or system config with a non-excludes key: pinned away by `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` on every call (proposed fixtures PK4/PK7). Not frozen rows this round.

Correction (round 71, 2026-11-06; the line above is not edited): the r67 sentence that a repository-local `core.fileMode` is "pinned away by `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` on every call" is false. Those pins reach only the global and system scopes; repository-local `core.fileMode=false` hid a pre-run and an in-run mode flip from the round-start writer (`census/round-71/controls/c1-do-nothing.txt` rows FM1/FM2, base=accept). Closed by the r71 `-c core.fileMode=true` pin (`census/round-71/records/c1-after.txt`; `knowledge/filter-filemode-witness.md`, S308).
