# GitSourceBool — Git boolean grammar + promisor/worktreeConfig constraints (source-only scout)

Status: scout report, advisory. No edits/tests/probes/builds. Own file only.
Axes: operability (C1 value-aware repair), calibration (C2 value distinctions must be independently checkable).

## Method and boundary disclosure

Read (source under lane root): `tools/souji-census.sh` (lines 84–90, 119–122, 160–164, 475–491,
493–521, 608–613, 627–628, 645–650, 664–665, 688–713). External primary material (named):
installed `git` 2.55.0 man pages (`git-config(1)`, `git-worktree(1)`, `gitrepository-layout(5)`),
`https://git-scm.com/docs/git-config` (page text last updated 2.56.0; boolean section identical
to 2.55.0), and upstream `git/git` tag **v2.55.0** sources `config.c`, `builtin/config.c`,
`parse.c`, `usage.c`, `setup.c`, `promisor-remote.c` (fetched to `/tmp`, never executed).

Disclosure: one `ls census/` (names only) occurred before the no-query reminder; the operator
sweep directory was not opened, read, copied, moved, staged, or deleted. Targeted greps hit only
known round-14/report/LOG/SCORECARD files. No broad lane-root search was repeated. `git --version`
and man-page dumps are environment/doc reads, not repo probes. No tools installed.

Repair not present at read time: `tools/souji-census.sh:493–521` is still key-only and
`tests/fixtures/r15-census-config.py` does not exist. §§6–7 are **design/acceptance**, not
observed repaired behavior.

## 1. Observed facts in the current tool

- **F1 — value-blind refusal is exactly at the key layer.** `guard_git_config` collects only
  key names (`:500` `git config --file "$cfg" --no-includes --name-only --list`), lowercases the
  whole list (`:503`), and refuses on any case match (`:504–507`). No value is ever read.
  Consequences: `remote.origin.promisor=false`, `extensions.worktreeConfig=false`, a valueless
  `promisor` (true), and `promisor=true` all take the same `git-config-unsupported` path.
  `protected_fail` exits 2 (`:160–164`), so one such repo suppresses the whole census.
  [OBSERVED source; effect on fleet as previously judged in round 14.]
- **F2 — the guard reads `$dir/config` only** (`:495`). Linked-worktree admin dirs contain
  `config.worktree`, not `config`; `guard_git_files` fixed list excludes `config.worktree`
  (`:477`). So per-worktree config is currently unguarded; only the key-only refusal of
  `extensions.worktreeConfig` masks that hole. [OBSERVED]
- **F3 — status neutralizations** (`:709–713`): `-c core.fsmonitor=false
  -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null`.
  These apply only to the `status` call; `worktree list` (`:688`), `for-each-ref` (`:694`),
  `rev-list` (`:698,702`), and `rev-parse` are not covered. [OBSERVED]
- **F4 — global/system config and inherited `GIT_*` are cleared** (`:119–122`). Effective config
  is therefore repo-local (+ per-worktree when the extension is enabled) only. [OBSERVED]

## 2. Boolean value grammar (what Git actually accepts)

Docs: `man git-config` **740–752** (`Values`/`boolean`), mirrored online at `git-config` page
lines 1295–1311. Source: `parse.c:166–191` and `parse.c:20–56`; fatal path `config.c:1292–1299`.

| Config spelling (value part) | Effective boolean | Basis |
|---|---|---|
| `key` with no `=` (NULL value) | **true** | `parse.c:168–169` (`!value → 1`); docs 744–746 |
| `key =` (explicit empty string) | **false** | `parse.c:170–171`; docs 748–749 |
| `true`, `yes`, `on` (any case) | true | `parse.c:172–175` (`strcasecmp`) |
| `false`, `no`, `off` (any case) | false | `parse.c:176–179` |
| `0` / `0k` / `0x0` | false | `parse.c:183–190` integer path, nonzero test |
| any non-zero integer: `1`, `-1`, `+1`, `010`, `0x10`, `1k`, `2M` | **true** | `parse.c:20–56` `strtoimax(…, base 0)` + k/m/g factor; `!!v` |
| anything else (`maybe`, `2x`, overflow, bad suffix) | **invalid** | `git_config_bool` `die()` → exit **128** (`config.c:1292–1297`; `usage.c:82–88`) |

`--type=bool` canonicalizes to lowercase `true`/`false` (docs 751–752;
`builtin/config.c:285–300`).

Doc/source nuance: the docs say “positive numbers” (189–190), but source accepts **negative,
hex, octal and unit-suffixed** integers as true. A hand-rolled shell classifier built from the
doc sentence alone would misclassify `-1`, `0x10`, `010`, `1k`; if it maps “unrecognized” to
false it is **fail-open**. Use Git's own `--type=bool` parser; do not case-match values by hand.

## 3. Query semantics that decide safe admission

- **get vs list (the critical fail-open trap).** `get`/`--get`/`--get-regexp` format every
  matched occurrence with `gently=0` (`builtin/config.c:505–535`) → the first invalid typed
  value dies (128). `list`/`--list` formats with `gently=1`
  (`builtin/config.c:473–481`) → invalid values are **silently omitted**; the man page states
  this at 209–211. Therefore: **never use list mode (with or without `--type`) to decide
  admission**, because an unparseable/hostile value disappears instead of failing.
- **Output/exit contract.** `get`: last value only unless `--all` (`builtin/config.c:630–635`);
  rc 0 = found, rc 1 = absent/no match (docs 66–69), rc 128 = `die` (invalid typed value),
  rc 6 = bad regexp, rc 2/129 = usage. Note `get` without `--all` still *formats every*
  occurrence before printing the last, so an earlier invalid duplicate dies even when the
  effective value is false (fail-closed, but must be reported as an unparseable value, not as
  “key present”).
- **`-z` framing** (docs 221–225; `builtin/config.c:1016–1023`): with `--show-names` or
  `--get-regexp`, records are `key\nvalue\0`. A valueless key back-outs the delimiter
  (`builtin/config.c:409–423`) → record `key\0`; an explicit empty value → `key\n\0`. This is
  the only raw (untyped) framing that distinguishes valueless(true) from empty(false).
- **Scope.** `--file` + `--no-includes` reads exactly that file; includes default **off** when
  a specific file is given (docs 251–254). Repo-local includes remain refused (`:505`). This
  coupling is a correctness precondition: an admitted `include.path` could inject
  `promisor=true` or `worktreeConfig=true` from another file (`config.c:158–174`).
  Value-aware parsing is sound only while `include.*`/`includeIf.*` stay refused.
- **Precedence is per key, not uniform.** Ordinary keys: last value wins (docs 338–340).
  `extensions.worktreeConfig`: last occurrence wins (`setup.c:629–631`, plain assignment per
  callback). `remote.<name>.promisor`: **OR, not last-wins** (see §4).

## 4. Promisor constraints (docs + source)

Docs: `remote.<name>.promisor` “When set to true, this remote will be used to fetch promisor
objects” (5638–5639); `remote.<name>.partialCloneFilter` (5641–5645);
`extensions.partialClone` “value … is the name of the promisor remote”, respected regardless of
`core.repositoryFormatVersion` (2757–2766).

Source facts (`promisor-remote.c`):

1. `remote.<name>.promisor`: callback parses each value with `git_config_bool`; **false returns
   early and never removes** an earlier true; true adds/keeps the remote (132–145). Effective
   semantics = **any true occurrence wins**, across duplicates and across local + worktree
   config. A last-value-only read would wrongly admit `promisor=true` followed by `false`.
2. `remote.<name>.partialCloneFilter`: presence **creates the promisor entry** even without
   `promisor=true` (146–161); the value is required (`git_config_string` → nonbool error).
   Any value, including empty, leaves the entry.
3. `extensions.partialClone=<name>`: adds/creates that promisor entry at init (178–187); the
   value is required and is a **remote name string, not a boolean** (`setup.c:624–628`).
   Presence is the marker; empty string is still a marker (pointer non-NULL).
4. With a non-empty promisor list, missing objects trigger
   `git fetch <remote> --no-tags --no-write-fetch-head --filter=blob:none --stdin` (44–48):
   network, credential-helper, and object-write side effects. This is the hazard a read-only
   census must not admit.

**Admission rule (design).** Admit only when all three hold: (a) `extensions.partialClone` is
absent; (b) no `remote.*.partialCloneFilter` occurrence; (c) every `remote.*.promisor`
occurrence is false (not merely the last one). Refuse on any true, any filter, any extension
marker. Invalid boolean / valueless filter / any unparseable result → could-not-evaluate.

**Current hole [OBSERVED source; INFERENCE effect].** Pattern `:505` matches
`remote.*.promisor` but **not** `remote.*.partialClonefilter`. A filter-only config therefore
passes the guard while source creates a promisor remote — fail-open — whereas the benign
`promisor=false` config is refused. The repair must close the filter marker to keep a no-trade
claim.

## 5. worktreeConfig constraints

Docs: `git-config` 2833–2861; `git-worktree` 252–276 and 316–317; `git-config` FILES 326–328.
Source: `setup.c:597–635` (v0 extension handler), `629–631` (bool, last-wins), `761–763`
(flag read from `$GIT_COMMON_DIR/config`), `787–793` (when enabled, read
`$gitdir/config.worktree` for core.bare/core.worktree); `config.c:1563–1569, 1588–1599`
(read order and gate).

- Same boolean grammar; **valueless = true**, empty = false, invalid → `git_config_bool` dies
  during repo setup. [OBSERVED source]
- **false/absent is inert**: Git reads `config.worktree` only when the flag is true
  (`config.c:1593–1595`; `setup.c:787`). A physical `config.worktree` is ignored. So admitting
  `false` is safe and is the required C1 preservation case.
- **true is effective and highest precedence**: settings in `config.worktree` override every
  other file (docs 2836–2838). Any unsafe key there (hooksPath, filters, includes, promisor)
  is live. It is per-worktree: `$GIT_COMMON_DIR/config.worktree` for the main worktree;
  `$GIT_COMMON_DIR/worktrees/<id>/config.worktree` for linked ones (`config.c:1565`).
- The flag itself is read **only** from the common config (`setup.c:761–763`); a
  `config.worktree` cannot enable/disable it.
- `worktreeConfig` is honoured even when `core.repositoryFormatVersion` is 0
  (`setup.c:601–603` comment; docs 2860–2861). Do not gate on format version.
- With true, the `core.worktree`/`core.bare` special case is gone; values in `config.worktree`
  are per-worktree and must be boundary-checked there too (`git-worktree` 264–271).
- **Access hole:** `guard_git_config` never reads `config.worktree`, and `guard_git_files:477`
  does not include it. Minimal safe repair: admit false/absent, keep true refused (header must
  state why). Full repair: if true is admitted, guard `$GIT_DIR/config.worktree` with the same
  value-aware rules, boundary-check it before read, and reject symlink/non-regular/hardlinked
  forms. [OBSERVED current source; design]

## 6. Design guidance for the repair (design-only; no repaired source exists)

All queries stay on `git config --file "$cfg" --no-includes -z` so they read exactly the
inspected file, never includes, never the environment.

1. Promisor values:
   `git config --file "$cfg" --no-includes -z --type=bool --all --show-names --regexp '^remote\..*\.promisor$'`
   - rc 1 → no key; rc 0 → any `true` record → refuse; all `false` → continue; rc 128 →
     could-not-evaluate (invalid boolean); any other rc → could-not-evaluate.
   - `--all` is mandatory (OR semantics). Plain `--get` prints only the last value and would
     fail-open on true-then-false. `list`-mode is forbidden (silent omission, §3).
2. Promisor-filter markers:
   `… -z --all --show-names --regexp '^remote\..*\.partialclonefilter$'` (no `--type`).
   Any record → refuse (value required; valueless is a Git config error).
3. Partial-clone extension: `… -z --get extensions.partialClone`.
   rc 0 (any value, even empty) → refuse; rc 1 → absent; else could-not-evaluate.
4. Worktree extension: `… -z --type=bool --get extensions.worktreeConfig`.
   rc 1 → absent(false); `false` → admit and do not read `config.worktree`; `true` → refuse
   under minimal repair, or guard `config.worktree` first; rc 128 → could-not-evaluate.
   Do not use `--list`; do not use shell case for the value.
5. Distinguish failure causes: a malformed file is `git-config-unparsed`; a valid but invalid
   boolean is an unparseable/unsupported value. Keeping separate reasons preserves the
   calibration signal the C2 checker needs.
6. Update the boundary header (`:86–90`) to describe **effective-value** tests and the
   residual refusal effects (true/filter/extension/true-worktree), not key presence.

## 7. Exact acceptance needed (fixture absent; design-only)

Same command on r14 baseline source and repaired tool. Baseline must be red where value-blind
refusal harmed; repaired must be green; unsafe cases must stay red; namespace cases unchanged.

| Case | Config (repo-local) | r14 | repaired |
|---|---|---|---|
| A false promisor | `remote.origin.promisor = false` | exit 2 | exit 0, row emitted |
| B true promisor | `= true` | exit 2 | exit 2 |
| C valueless promisor | `promisor` (no `=`) | exit 2 | exit 2 (true) |
| D empty promisor | `promisor =` | exit 2 | exit 0 (false) |
| E invalid promisor | `= maybe` | exit 2 | exit 2, distinct/unparseable finding |
| F duplicate | `= true` then `= false` | exit 2 | exit 2 (OR; not last-wins) |
| G filter only | `partialCloneFilter = blob:none` | possibly exit 0 | exit 2 (closes hole) |
| H partialClone | `extensions.partialClone = origin` | exit 2 | exit 2 |
| I worktree false | `extensions.worktreeConfig = false` | exit 2 | exit 0 |
| J worktree valueless | `worktreeConfig` no `=` | exit 2 | exit 2 (true) |
| K worktree true, clean | `= true`, clean `config.worktree` | exit 2 | exit 2 (minimal) |
| L worktree true, unsafe | `= true`, `config.worktree` has `core.hooksPath`/filter/promisor | exit 2 | exit 2 |
| M worktree false, unsafe file | `= false` + unsafe `config.worktree` | exit 2 | exit 0 (inert) — strongest no-harm control |
| N mixed fleet | benign false + unsafe true + normal | exit 2 | exit 2 fleet-wide; safe-only fleet emits all rows |
| O namespace retention | r14 fixture’s 12 cases | pass | pass unchanged |

Exact case IDs/row assertions belong to ConfigFixture; this is required coverage, not an
interface. G’s baseline cell is deliberately marked “possibly exit 0”: it is a **source-derived**
fail-open expectation, not an executed baseline, and must not be recorded as runtime evidence.

## 8. Unrun checks, limits, unknowns

- **No execution**: no `git config` value query, fixture, census, shell probe, build, lint, or
  formatter was run. All rc/output claims are doc- or source-derived.
- Exit 128 for an invalid typed value is from `die()` (`usage.c:82–88`), not observed.
- Source cited is v2.55.0 (installed git is 2.55.0); the online doc page is 2.56.0 but its
  boolean wording matches. No 2.56.0 source was inspected.
- `EXTENSION` handling for `worktreeConfig`/`partialClone` at repository-format version 0 is
  source-derived (`setup.c:597–635`), not exercised.
- Repair source absent at read time; §§6–7 are advisory acceptance and may conflict with
  ConfigRepair’s chosen query primitives. ConfigFixture must not encode my case table as
  runtime evidence.

## Sources

- `tools/souji-census.sh` lines cited inline (lane root).
- `/usr/share/man/man1/git-config.1.gz` (git 2.55.0), decompressed lines 40–69, 183–232,
  251–258, 320–340, 735–752, 2098–2113, 2757–2766, 2833–2861, 5638–5645.
- `/usr/share/man/man1/git-worktree.1.gz` (2.55.0), lines 252–276, 316–317.
- `/usr/share/man/man5/gitrepository-layout.5.gz` (2.55.0), repository-format/extension rules.
- `https://git-scm.com/docs/git-config` (2.56.0 text): boolean 1295–1311; anchors
  `#Documentation/git-config.txt-boolean`, `…-remoteltnamegtpromisor`,
  `…-extensionsworktreeconfig`.
- Upstream `git/git` v2.55.0: `config.c` 158–174, 1292–1299, 1555–1569, 1588–1599;
  `builtin/config.c` 285–300, 409–423, 473–481, 505–535, 630–635, 1016–1023;
  `parse.c` 20–56, 166–191; `usage.c` 82–88; `setup.c` 597–635, 753–793;
  `promisor-remote.c` 44–48, 127–161, 178–187.
