---
source: S291 — git-update-index(1) `--skip-worktree` (https://git-scm.com/docs/git-update-index; accessed 2026-11-05) for the index-flag route this entry extends; NEW-SID-1/2/3 (see `corpus/SOURCES.md`, ids assigned by the L1) — git(1) § ENVIRONMENT VARIABLES (https://git-scm.com/docs/git; accessed 2026-11-05) and git-config(1) (https://git-scm.com/docs/git-config; accessed 2026-11-05) for the config and object-redirect routes; located quotes with byte offsets in `census/round-66/sources/` (L1 copy of `.ufo/waves/round-66/w1/S66ScoutSources/quotes.tsv`)
verified-at: c13fbb4e1b563a78278ddc14316c20252e9a6d8d (the round-66 candidate writer's landing revision; the base `045e103478fa4a7eff77db2cab5b9e2f26959a0a` carries the round-65 writer and is NOT this claim's revision)
recheck: `python3 -B census/round-66/c1-counter.py --root LANE --matrix census/round-66/c1-matrix.tsv --base-rev 045e103478fa4a7eff77db2cab5b9e2f26959a0a --rev c13fbb4e1b563a78278ddc14316c20252e9a6d8d --tool tools/souji-receipt-write.py --work DIR` must print `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS` and `EXIT=0`; the E1–E6, MOD2, MOD3 and SY3 rows inside it are the re-verification point for this entry

# A receipt writer's status and object reads must not be steerable by caller-injected environment routes

ground: F4-adjacent — receipt hygiene: the receipt writer's status and object reads are the surfaces a caller steers (`corpus/knowledge/skip-worktree-concealment.md` closed the index-flag route to the same guarantee; `corpus/knowledge/untracked-visibility-concealment.md` closed one config KEY)

## Claim

A receipt writer that reads the repository through `git` can be steered by the CALLER's environment, with no
change to any tracked byte. Two route families reach it:

- **Caller-injected config.** `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_<n>`/`GIT_CONFIG_VALUE_<n>` and the legacy
  `GIT_CONFIG_PARAMETERS` add config pairs to the process's runtime configuration, so a caller can inject
  `core.excludesFile` and make an untracked path INVISIBLE to `git status --porcelain`. `GIT_CONFIG_GLOBAL`
  names the global config file instead of `$HOME/.gitconfig`/`$XDG_CONFIG_HOME/git/config`.
- **Caller-injected object redirects.** `GIT_OBJECT_DIRECTORY` repoints the primary object store,
  `GIT_ALTERNATE_OBJECT_DIRECTORIES` adds search directories for object lookups, and `GIT_REPLACE_REF_BASE`
  moves the replacement-ref namespace away from `refs/replace/`.

A receipt writer that honours these routes can write a receipt over a tree it did not measure, or over a
forged object it read from a substituted store.

## Rule (round 66, C1 rows E1–E6)

The writer refuses the PRESENCE of those routes before it makes any git call, and pins the config routes it
still honours to the null device:

- `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_KEY_*`, `GIT_CONFIG_VALUE_*` present →
  refuse with `RECEIPT-ENV-CONFIG-SET`.
- `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE` present →
  refuse with `RECEIPT-ENV-REDIRECT-SET`.
- On every git call the writer also sets `GIT_CONFIG_GLOBAL` to the null device, `GIT_CONFIG_NOSYSTEM=1`,
  `GIT_NO_REPLACE_OBJECTS=1`, and pins `-c core.excludesFile=<null device>`, so a config route that reaches
  the child process anyway cannot hide an untracked path.
- The in-run snapshot records `st_mode & 0o7777`, not `& 0o777`: setuid, setgid and sticky are recorded, so a
  permission-bit flip under `--allow-dirty` refuses with `RECEIPT-STATE-CHANGED-DURING-RUN` (rows MOD2, MOD3).
- A same-content symlink retarget refuses with `RECEIPT-STATE-CHANGED-DURING-RUN` (row SY3): the snapshot
  records the symlink's TARGET STRING, so a retarget to a byte-identical copy still changes the recorded string.

Falsifiable form: with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0=<file>`
naming a file that excludes `tools/hidden.txt`, the base writer (round-66 base `045e103478fa4a7eff77db2cab5b9e2f26959a0a`)
writes a receipt (exit 0) and the landed writer refuses with `RECEIPT-ENV-CONFIG-SET` (exit 2). Under
`GIT_REPLACE_REF_BASE=refs/replace-forged-r66/` the base writer accepts (exit 0) and the landed writer refuses
with `RECEIPT-ENV-REDIRECT-SET`. Under `GIT_CONFIG_GLOBAL=<crafted global config>` the base writer accepts
and the landed writer refuses with `lane worktree is dirty` (the null-device repoint makes the excluded path
show up untracked). The honest rows A, B, T4, V2 and SY1 must still accept: the refusal is key- and
variable-scoped, not a blanket refusal of any `GIT_*` in the environment.

## Measured (round 66, C1 counter)

- Frozen 28-row matrix, `census/round-66/records/c1-after.txt` at `c13fbb4e…`: `SUMMARY matrix=28
  base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`.
  The do-nothing arm `census/round-66/controls/c1-do-nothing.txt` prints `new_forgeries=8 … class_mismatches=8`,
  `EXIT=1`.
- The base writer at the round base reads the injected routes: the do-nothing receipt shows rows E1, E2, E3,
  E4, E5, E6, MOD2 and MOD3 as `base=accept` (the eight base forgeries) and SY3 as `base=refuse` (the row
  kills a read-through-symlink-hasher mutant class, not a base forgery).
- C2 at the same revision (`census/round-66/records/c2-after.txt`): `MARKERS flag=1 inrun=1 env=1 unmerged=1
  envcfg=1 envred=1`, `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` — the SKILL.md statement s5 and the
  writer's two new refusal classes agree.
- The M-ENV kill (`census/round-66/records/c2-mutant-m-env.txt`): the round-66 counter on the mutant prints
  `FINDING SCOPE-OVERREACH s2: … claim closed_full needs writer markers env; writer blob lacks them` and
  `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1`; the round-65 counter on the SAME mutant at the same
  SKILL.md prints `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0`. That is the round-65 M10 repair,
  demonstrated.

## Host probes (this seat, git 2.56.0, scratch `S66ScribeEntry/probe/`)

- `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` and legacy `GIT_CONFIG_PARAMETERS` both inject
  `core.excludesFile` into `git status --porcelain` on this host: the excluded path disappears from the
  porcelain output with the injection, and reappears with `-c core.excludesFile=/dev/null` on the same
  command line. `git config --get core.excludesFile` returns the injected path under the injection and
  `/dev/null` under `-c core.excludesFile=/dev/null` — the command-line `-c` outranks the injected pair.
- `GIT_CONFIG_GLOBAL=<crafted>` hides the excluded path; `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`
  brings it back.
- `GIT_REPLACE_REF_BASE` without a trailing slash makes git ABORT, not misbehave quietly: `git status
  --porcelain` and `git for-each-ref` exit 134 with `BUG: refs.c:1908: ref pattern must end in a trailing
  slash when trimming` (git 2.56.0). With the trailing slash the namespace moves and the read is forged:
  with `refs/replace-forged-r66/<real-oid>` pointing at a different blob, `git cat-file -p HEAD:a.txt` prints
  the forged content; `GIT_NO_REPLACE_OBJECTS=1` restores the real content.

## Named limits (frozen with round 66; none claimed as passes)

- **Ignore routes stay outside C1.** `.git/info/exclude`, a tracked `.gitignore` and a repository-local
  `core.excludesFile` in `.git/config` still hide untracked content from the writer's status reads on BOTH
  slots: the dirty check is a status check, and ignored content is outside it by design. Measured on git
  2.56.0: the excluded path is absent from `git status --porcelain` under all three routes, and `-c
  core.excludesFile=/dev/null` restores it ONLY for the repository-local `core.excludesFile` route (the
  `.git/info/exclude` and tracked-`.gitignore` routes survive the `-c` pin, because neither is the
  `core.excludesFile` key).
- **C1's pins change behaviour for honest lanes.** `GIT_CONFIG_GLOBAL` to the null device,
  `GIT_CONFIG_NOSYSTEM=1` and `-c core.excludesFile=<null device>` make a host-global or repository-local
  excludes file ineffective, so a file that was hidden becomes untracked and counts as dirty. The frozen
  honest rows A, B, T4, V2 and SY1 do not exercise that route.
- **Presence, not content.** C1 refuses the PRESENCE of the six named variables; a caller that sets one to
  an empty string is still refused, and a caller that sets one to a harmless value is still refused.
- **C2 is lexical.** The C2 counter reads a refusal needle as live only when it occurs on an uncommented
  line carrying `refuse(` or a `return` whose value begins with a string literal. A needle on a dead line
  (behind `if False:`) or inside a one-line docstring that also carries `refuse(` still reads live.
  Reachability is the C1 matrix's job, not C2's.
- **One mutant, not a battery.** The C2 kill-power result is one number from one mutant recipe
  (`census/round-66/c2-mutate.py`, M-ENV), not a mutation rate.
- **`GIT_CONFIG_PARAMETERS` and `GIT_REPLACE_REF_BASE` have no manual anchor.** Neither variable appears in
  the git(1) or git-config(1) pages at 2.56.0 (`grep -c` over the captured pages: 0 for each), nor in the
  installed man pages, nor in upstream `Documentation/git.txt`, `git-config.txt` or `git-replace.txt` at tag
  v2.56.0 (0 for each). Their only upstream prose is the git 2.6.0 release note (`Documentation/RelNotes/
  2.6.0.adoc`: "An environment variable GIT_REPLACE_REF_BASE tells Git to look into refs hierarchy other than
  refs/replace/ for the object replacement data.") and the source constants in `environment.h` and
  `config.h`; the routes are therefore grounded on upstream SOURCE, not on a manual page.

## Gate

opened: 2026-11-05 — two pages fetched live this round (`https://git-scm.com/docs/git`, HTTP 200, 244227
bytes, sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`; `https://git-scm.com/docs/git-config`,
HTTP 200, 830605 bytes, sha256 `37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226`). The
capture and the located-quote proof are the scout seat's (`.ufo/waves/round-66/w1/S66ScoutSources/`:
`git-environment.html`, `git-environment.txt` sha256 `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`,
`git-config.html`, `git-config.txt` sha256 `dfc44574996cdf9023e9b61ea37a4aab0fe0c79058b34743d08d5bc788d46054`,
`recipe.py`, `quotes.tsv`, `upstream-evidence.txt`, `verify.sh`); the L1 copies them to `census/round-66/sources/`
under the names the registry rows' anchor cells name. This seat independently re-sliced ALL 34 rows of
`quotes.tsv` against the delivered `.txt` bytes: 34/34 byte-identical at the stated offset, 34/34 sha256
match, every quote ≤25 words.

- ADMIT (NEW-SID-1, git(1) § ENVIRONMENT VARIABLES) — `GIT_OBJECT_DIRECTORY` (locator offset 30732,
  quote "If the object storage directory is specified via this" at offset 30753, 9 words) and
  `GIT_ALTERNATE_OBJECT_DIRECTORIES` (locator offset 30937, quote "specifies a \":\" separated (on Windows
  \";\" separated) list" at offset 31092, 9 words); accessed 2026-11-05; HTTP 200. Reason: the page states
  that the variable names the object-storage directory and that the alternates variable names a list of
  directories "which can be used to search for Git objects" — exactly the two reads a receipt writer makes
  and the two routes E4 and E5 exercise. Flip: the page no longer documents the variables, or the located
  quote stops being byte-contiguous in the named capture.
- ADMIT (NEW-SID-2, git(1) § ENVIRONMENT VARIABLES) — `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` (locator offset
  40065, quote "will not be read. Likewise, if GIT_CONFIG_GLOBAL is set, neither" at offset 40302, 10 words;
  the null-device sentence at the same block: "Can be set to /dev/null to skip reading configuration files of
  the respective level.") and `GIT_NO_REPLACE_OBJECTS` (locator offset 46311, quote "Setting and exporting this
  environment variable tells Git to" at offset 46334, 9 words). Reason: the first states that setting
  `GIT_CONFIG_GLOBAL` replaces the global config file and that `/dev/null` skips it — the pin the writer
  applies; the second states the documented way to make git ignore replacement refs, the read the writer
  neutralises with `GIT_NO_REPLACE_OBJECTS=1`. Flip: the page stops documenting either variable or its
  `/dev/null` behaviour.
- ADMIT (NEW-SID-3, git-config(1) § ENVIRONMENT / § CONFIGURATION) — `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_<n>`/
  `GIT_CONFIG_VALUE_<n>` (locator offset 20861, quote "If GIT_CONFIG_COUNT is set to a positive number, all
  environment pairs" at offset 20918, 11 words) with the precedence sentence (quote "in configuration files,
  but will be overridden by any explicit options" at offset 21340, 11 words, followed by "passed via git -c ."
  at offset 21411, 5 words); and `core.excludesFile` (locator offset 102897, quote "Specifies the pathname to
  the file that contains patterns to" at offset 102915, 10 words, and "to .gitignore (per-directory) and
  .git/info/exclude ." at offset 103037, 6 words); accessed 2026-11-05; HTTP 200. Reason: the page states
  that the environment pairs "will be added to the process's runtime configuration" — the injection E1/E2
  exercise — and that they are "overridden by any explicit options passed via git -c", which is why the
  writer's `-c core.excludesFile=<null device>` pin beats an injected pair (measured on this host). The
  `core.excludesFile` quote states the key that decides which paths status does not show, the key E1–E3
  inject. Flip: the page stops documenting the variable or the `-c` precedence.
- ADMIT (upstream source, not a manual page) — git/git at tag v2.56.0: `refs.c` (NAMESPACE_REPLACE comment:
  "this one can be changed by the GIT_REPLACE_REF_BASE environment variable"), `environment.h`
  (`#define GIT_REPLACE_REF_BASE_ENVIRONMENT "GIT_REPLACE_REF_BASE"`, `#define
  CONFIG_DATA_ENVIRONMENT "GIT_CONFIG_PARAMETERS"`), `config.h` (the `GIT_CONFIG_PARAMETERS` format comment:
  "a space-separated list of quoted \"'<key>'='<value>'\" pairs"), and `Documentation/RelNotes/2.6.0.adoc`
  ("An environment variable GIT_REPLACE_REF_BASE tells Git to look into refs hierarchy other than
  refs/replace/ for the object replacement data."). Reason: these two variables are absent from every
  manual page at 2.56.0 (0 hits in the captured pages, the installed man pages and the three upstream
  `Documentation/*.txt` files), so the E2 and E6 routes can only be grounded on upstream source. The row is
  `kind: code`, tier A, scoped to the two UNDOCUMENTED variables only. Flip: the variables appear in a
  shipped manual page, which would replace this row with a docs row.
- REJECT (do not admit) — "a receipt writer must refuse these environment variables": the pages assign no duty
  to any consumer; the refusal is this lane's design decision. Flip: a git(1)/git-config(1) sentence that
  assigns that duty to tools that gate on git's reads.
- REJECT (do not admit) — "`GIT_CONFIG_GLOBAL` to the null device makes git ignore every global config": the
  page says the global-level config files are not read and that `/dev/null` skips that level; it does not say
  the repository-local or system config is skipped, and `GIT_CONFIG_NOSYSTEM=1` is a separate variable. Flip:
  a sentence stating the system and local levels are skipped too.
- REJECT (do not admit) — "`GIT_NO_REPLACE_OBJECTS=1` also disables the replace-ref namespace shift": the
  variable's documented effect is that git ignores replacement refs and does not replace Git objects; the
  namespace base is a separate variable with separate upstream prose. Flip: a sentence stating the two are
  equivalent.
- **Neighbour rows.** S237 already carries git(1)'s `GIT_CONFIG_NOSYSTEM` and S238 already carries
  git-config(1)'s `GIT_CONFIG_COUNT`; the new rows take the scopes those rows do NOT hold (the object-store
  and replace-ref routes; the global-config-file route and the documented null-device skip; the `-c`
  precedence and the `core.excludesFile` key). A duplicate-url census warning (W04) is expected, exactly as
  for S291/S295/S296 and S251/S239/S244; it is not a finding.
- Non-author closure: sample the ADMIT quotes' byte-offset assertions against the committed capture; sample
  the two upstream-source quotes against the pinned tag; and sample one REJECT flip against the page bytes.

## What this does not prove

- The claim is about six environment variables on one git version's reads. It is NOT a statement that a receipt
  writer is immune to operator configuration in general: the measured ignore routes (.git/info/exclude, a
  tracked .gitignore) say the opposite.
- The counter proves the writer's behaviour on the frozen matrix, not that the writer's env gate is
  unreachable: the gate is lexical and a dead refusal line would still read live to C2.
- Bytes are not execution: the receipts cited here are the round's committed receipts plus this seat's
  independent re-slicing of the scout's captures; neither proves that the command that produced them was the
  one described.
