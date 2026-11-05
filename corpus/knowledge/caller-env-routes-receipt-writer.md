source: S298 — git(1) § ENVIRONMENT VARIABLES (https://git-scm.com/docs/git; accessed 2026-11-05; HTTP 200); S299 — git-config(1) § ENVIRONMENT, § FILES, § SCOPES, core.excludesFile (https://git-scm.com/docs/git-config; accessed 2026-11-05; HTTP 200). Quotes and offsets: `corpus/lessons/round-66.md` Gate and `census/round-66/sources/quotes.tsv`.
verified-at: c13fbb4e1b563a78278ddc14316c20252e9a6d8d (the landed revision of `tools/souji-receipt-write.py`, sha256 a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc)
recheck: `python3 -B census/round-66/c1-counter.py --root LANE --matrix census/round-66/c1-matrix.tsv --base-rev 045e103478fa4a7eff77db2cab5b9e2f26959a0a --rev <full40> --tool tools/souji-receipt-write.py --work DIR` must print `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS` and `EXIT=0`; the E1-E6, MOD2 and MOD3 rows inside it are the re-verification point for this entry

# A receipt writer's clean-tree check must not be steerable by caller-injected git environment

ground: F4-adjacent — receipt hygiene: the receipt writer decides "clean" by reading git, so any environment that changes what git reads changes the verdict (extends `knowledge/untracked-visibility-concealment.md`, which covers the `status.showUntrackedFiles` key, and `knowledge/skip-worktree-concealment.md`, which covers the index flags)

## Claim

A receipt writer that trusts git's reads can be blinded or redirected without touching any tracked byte, through environment variables that git itself honours:

- `GIT_CONFIG_COUNT` with `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`, and the legacy `GIT_CONFIG_PARAMETERS` form, inject `core.excludesFile`. A file listed there is hidden from `git status` (revenger P1, P2).
- `GIT_CONFIG_GLOBAL` replaces the global config file, so a crafted global file injects the same excludes route (revenger P3a). Pointing it at the null device with `GIT_CONFIG_NOSYSTEM=1` stops the hiding (revenger P3b).
- `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` change which object store git reads. A redirect to an empty directory breaks reads (revenger P4-ctl), so the redirect is observable, but a redirect to a complete copy is indistinguishable from honest use (P4), which is why presence must be refused rather than content tested.
- `GIT_REPLACE_REF_BASE` changes the replace-ref namespace. With a trailing slash, a forged replace ref is honoured (revenger P6c, output `FORGED`). Without the trailing slash, git aborts with `BUG: refs.c:1908` (P6a, rc -6).

Source support: `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>` and `GIT_CONFIG_VALUE_<n>` are defined on git-config(1) (S299, quote at offset 20918, 11 words). A command-line `-c` overrides these pairs (S299, offset 21376; revenger P7). `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM` are defined on git(1) (S298, offset 40302). `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` are defined on git(1) (S298, offset 30753 and 31092). `GIT_NO_REPLACE_OBJECTS` is defined on git(1) (S298, offset 46334; revenger P8 confirms it restores the original view). **Not on either page:** `GIT_CONFIG_PARAMETERS` and `GIT_REPLACE_REF_BASE`. Both are upstream internals, so their behaviour rests on the revenger probes and not on a docs sentence. The absences table is `census/round-66/sources/absences.tsv`.

## Rule (round 66, C1)

The receipt writer:

1. refuses, before any git call, the presence of `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, or any `GIT_CONFIG_KEY_*` / `GIT_CONFIG_VALUE_*` name, with `RECEIPT-ENV-CONFIG-SET`;
2. refuses, before any git call, the presence of `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` or `GIT_REPLACE_REF_BASE`, with `RECEIPT-ENV-REDIRECT-SET`;
3. prints variable names only, never values (the round-65 sentinel F4 defect is redacted in the same change);
4. pins, on every git call, `GIT_CONFIG_GLOBAL` and `core.excludesFile` to the null device, and sets `GIT_CONFIG_NOSYSTEM=1` and `GIT_NO_REPLACE_OBJECTS=1`;
5. records the full permission bits (`st_mode & 0o7777`, setuid, setgid and sticky included) in the in-run snapshot mode byte.

`GIT_CONFIG_GLOBAL` is repointed, not refused. The frozen matrix expects its class to be the dirty check, because the excluded file then shows up as untracked (row E3). Item 4 is also what makes the repoint hold.

Falsifiable form: `census/round-66/c1-matrix.tsv` rows E1-E6, MOD2 and MOD3. On the base writer (`045e103478fa4a7eff77db2cab5b9e2f26959a0a`) eight of them are forgeries (E1, E2, E3, E4, E5, MOD2, MOD3 and E6; E6 is accepted there only after the trailing-slash repair). On the landed candidate, zero are. Five honest rows (A, B, T4, V2, SY1) still accept.

## Measured

- Base (`045e1034`): `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=8 new_honest=5 class_mismatches=8 regress=PASS`, `EXIT=1` (do-nothing control, `census/round-66/controls/c1-do-nothing.txt`).
- Landed (`c13fbb4e`): `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0` (`census/round-66/records/c1-after.txt`).
- Writer selftest on the landed bytes: `cases=33 pass=33` (`census/round-66/records/writer-selftest.txt`).

## Named limits (not claimed)

- **`GIT_COMMON_DIR` is an open route on the landed candidate** (measured, round 66 L1 W2). Pointing it at a copy of `.git` whose config sets `core.fileMode=false` hides a tracked 755→644 change from the clean-tree check, and the writer accepts without `--allow-dirty` (rc 0 on base and on the candidate). The same effect follows from setting `core.fileMode=false` in the repository's own config (same config read). This is not in the six frozen names. Routed to round 67 as a separate claim.
- **Ignore routes** (`.git/info/exclude`, a tracked `.gitignore`, a repository-local `core.excludesFile`) still hide untracked content from the dirty check. They are outside C1 by design.
- **Other git-resolution names** (`GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, `GIT_CONFIG_SYSTEM`) are neither refused nor separately pinned. `GIT_CONFIG_SYSTEM` is inert once `GIT_CONFIG_NOSYSTEM=1` is pinned (sentinel LOW-3).
- **Honest-run refusal cost (trade, operator to rule).** git sets `GIT_CONFIG_PARAMETERS` in the environment of children that run under `git -c`. A writer launched that way is now refused with `RECEIPT-ENV-CONFIG-SET` (measured: base rc 0, candidate rc 2). A host whose global config excludes files would also see those files as dirty after the pin (round-66 L2; not measured on this host, which has no global excludes).
- **Setuid and sticky bits are invisible before the run** on a tracked file: git's porcelain does not track them, and the start-of-run check has no snapshot. The in-run snapshot now records them. Setgid has no matrix row, so it is unmeasured.
- **Redirect presence is refused even when harmless.** `GIT_ALTERNATE_OBJECT_DIRECTORIES` set to an empty directory is harmless on this host (revenger P5), so the row's class rests on presence, not on an observed forgery of that shape.
- **M-ENV kill power is one mutant.** Four of the eight C1 mutants survive the frozen matrix (K3, K4, K6, K7): the `core.excludesFile` and `GIT_CONFIG_GLOBAL` pins are mutually redundant for E3, and the replace and system-config pins need fixtures no row creates (`.ufo/waves/round-66/w1/S66MutKill/report.md`).

## Frontier

This entry is F4-adjacent receipt hygiene and does not promote any frontier row. It adds no coverage-map ground to `corpus/README.md`. The round-66 SCORECARD row records it as a capability, not as a frontier move.
