# SOURCES.md registry rows — round 66 (draft for the L1)

Shape copied from the last three rows of `corpus/SOURCES.md` (S295, S296, S297), column order exactly:

`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`

11 columns ⇒ `NF==13` (the census check `awk -F'|' … NF!=13` must print 0). No `|` inside any cell.
The L1 assigns the real S-ids (the contract says the id is `S` + 3 or more digits, the next unused, never
reused); the three rows below are placeholders `NEW-SID-1..3`.

## Row count, before and after

Census command (CORPUS.md § SOURCES.md, "Census — run from the lane root"):

```sh
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
```

- **BEFORE: 220** (measured this seat, at lane HEAD `045e103478fa4a7eff77db2cab5b9e2f26959a0a`, 2026-11-05).
- **AFTER (3 new rows appended): 223**.
- Malformed-row check after the append must print `0`:
  `awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md`.
- Duplicate-id check must print nothing (the L1 picks ids that are unused).

## The three rows

Paste-ready. `NEW-SID-1..3` are the L1's to number; the text is complete otherwise.

| NEW-SID-1 | git(1) ENVIRONMENT VARIABLES — GIT_OBJECT_DIRECTORY and GIT_ALTERNATE_OBJECT_DIRECTORIES — https://git-scm.com/docs/git | docs | A | the object-store redirect routes a caller can inject into a receipt writer's git reads: which directories the object database and the object search path are taken from | § ENVIRONMENT VARIABLES › GIT_OBJECT_DIRECTORY (locator offset 30732) and › GIT_ALTERNATE_OBJECT_DIRECTORIES (locator offset 30937); accessed 2026-11-05; HTTP 200; 244227 bytes; sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`; capture `census/round-66/sources/git-environment.html`; tag-stripped text `census/round-66/sources/git-environment.txt` sha256 `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`; located quotes `census/round-66/sources/git-environment.txt` offset 30753 ("If the object storage directory is specified via this", 9 words) and offset 31092 ("specifies a \":\" separated (on Windows \";\" separated) list", 9 words) — slice assertions PASSED (re-sliced independently by S66ScribeEntry) | `GIT_OBJECT_DIRECTORY` names the directory the object database is created under, "otherwise the default $GIT_DIR/objects directory is used"; `GIT_ALTERNATE_OBJECT_DIRECTORIES` names a list of directories "which can be used to search for Git objects", so a caller-set value decides where an object lookup is answered from — the two redirects C1 rows E4 and E5 refuse; the page does not say the objects found there are the repository's own | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md |
| NEW-SID-2 | git(1) ENVIRONMENT VARIABLES — GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM and GIT_NO_REPLACE_OBJECTS — https://git-scm.com/docs/git | docs | A | the global-config-file route and the documented replace-ref read switch: which config file git reads, and how to make git ignore replacement refs | § ENVIRONMENT VARIABLES › GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM (locator offset 40065) and › GIT_NO_REPLACE_OBJECTS (locator offset 46311); accessed 2026-11-05; HTTP 200; 244227 bytes; sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`; capture `census/round-66/sources/git-environment.html`; tag-stripped text `census/round-66/sources/git-environment.txt` sha256 `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`; located quotes `census/round-66/sources/git-environment.txt` offset 40302 ("will not be read. Likewise, if GIT_CONFIG_GLOBAL is set, neither", 10 words), offset 40535 ("Whether to skip reading settings from the system-wide", 8 words) and offset 46334 ("Setting and exporting this environment variable tells Git to", 9 words) — slice assertions PASSED (re-sliced independently by S66ScribeEntry) | setting `GIT_CONFIG_GLOBAL` makes git read that file instead of `$HOME/.gitconfig` or `$XDG_CONFIG_HOME/git/config`, and the same block states it "Can be set to /dev/null to skip reading configuration files of the respective level" — the pin the receipt writer applies; `GIT_CONFIG_NOSYSTEM` skips the system-wide config, which the page ties to "a predictable environment for a picky script"; `GIT_NO_REPLACE_OBJECTS` tells git to "ignore replacement refs and do not replace Git objects", the read the writer neutralises with `GIT_NO_REPLACE_OBJECTS=1` — the page does not tie that variable to the `GIT_REPLACE_REF_BASE` namespace shift | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md |
| NEW-SID-3 | git-config(1) § ENVIRONMENT and § CONFIGURATION — GIT_CONFIG_COUNT/GIT_CONFIG_KEY_<n>/GIT_CONFIG_VALUE_<n>, the `-c` precedence, and core.excludesFile — https://git-scm.com/docs/git-config | docs | A | the runtime-config injection route and the key that decides which paths a status read does not show: how environment pairs enter a git process's configuration, and what outranks them | § ENVIRONMENT › GIT_CONFIG_COUNT/GIT_CONFIG_KEY_<n>/GIT_CONFIG_VALUE_<n> (locator offset 20861) and the `-c` precedence sentence of the same block; § CONFIGURATION › core.excludesFile (locator offset 102897); accessed 2026-11-05; HTTP 200; 830605 bytes; sha256 `37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226`; capture `census/round-66/sources/git-config.html`; tag-stripped text `census/round-66/sources/git-config.txt` sha256 `dfc44574996cdf9023e9b61ea37a4aab0fe0c79058b34743d08d5bc788d46054`; located quotes `census/round-66/sources/git-config.txt` offset 20918 ("If GIT_CONFIG_COUNT is set to a positive number, all environment pairs", 11 words), offset 21340 ("in configuration files, but will be overridden by any explicit options", 11 words), offset 21411 ("passed via git -c .", 5 words), offset 102915 ("Specifies the pathname to the file that contains patterns to", 10 words) and offset 103037 ("to .gitignore (per-directory) and .git/info/exclude .", 6 words) — slice assertions PASSED (re-sliced independently by S66ScribeEntry) | the environment pairs are "added to the process's runtime configuration" — the injection C1 rows E1 and E2 exercise — and the same block states they "will be overridden by any explicit options passed via git -c", so a command-line `-c core.excludesFile=<null device>` outranks an injected `core.excludesFile` (measured on git 2.56.0); `core.excludesFile` names the file whose patterns describe "paths that are not meant to be tracked, in addition to .gitignore (per-directory) and .git/info/exclude", the key that decides what a status read does not show — the page does not assign any duty to a reader of that status | mined | 2026-11-05 | on-release | corpus/knowledge/caller-env-routes-receipt-writer.md |

## The upstream-source row the L1 may want as a fourth row (NOT one of the three above)

`GIT_REPLACE_REF_BASE` and `GIT_CONFIG_PARAMETERS` appear in NO manual page at 2.56.0. Measured this seat:
`grep -c` over the captured `git-environment.html` and `git-config.txt` → 0 for each variable; over the
installed man pages `git-replace(1)`, `git-config(1)`, `git(1)` → 0 for each; over upstream
`Documentation/git.txt`, `Documentation/git-config.txt`, `Documentation/git-replace.txt` at tag v2.56.0 → 0
for each. The only upstream prose is source and a release note:

- `refs.c` (upstream git/git, `NAMESPACE_REPLACE`): "this one can be changed by the GIT_REPLACE_REF_BASE
  environment variable."
- `environment.h`: `#define GIT_REPLACE_REF_BASE_ENVIRONMENT "GIT_REPLACE_REF_BASE"`,
  `#define CONFIG_DATA_ENVIRONMENT "GIT_CONFIG_PARAMETERS"`.
- `config.h`: the `GIT_CONFIG_PARAMETERS` value format — "a space-separated list of quoted \"'<key>'='<value>'\" pairs".
- `Documentation/RelNotes/2.6.0.adoc`: "An environment variable GIT_REPLACE_REF_BASE tells Git to look into
  refs hierarchy other than refs/replace/ for the object replacement data."

Captures and digests this seat obtained (the scout seat holds the same upstream evidence in
`.ufo/waves/round-66/w1/S66ScoutSources/upstream-evidence.txt`):

| upstream file | commit | sha256 |
|---|---|---|
| `refs.c` (tag v2.56.0) | `v2.56.0` = `a018953688f1b10bddf91bff8747068f5f4746a4` | `c0e5406b2d198ff26a9da541c85363a48e39fa6c012bc7e82569c7f60298460b` |
| `refs.c` (scout's pinned commit `0ffa3e35c7c82ab8d0de226149fb03b3f7674d05`, "The 15th batch", 2026-11-04) | same tree, post-tag | `50d953415b73d3eeaa1280ecaadcb350a8faa294f3b5337979c12ceef2d3932c` |

If the L1 files this as a row, the `kind` is `code`, tier A, and the scope must be the two UNDOCUMENTED
variables only (a `docs` row for them would be false). The L1 decides whether to file it as a fourth row or
to fold the upstream quotes into the knowledge entry's Gate only; the row count note above then becomes
223 or 224.

## Notes for the L1

- **`used-by` must exist at the revision.** The census check (`awk … NF==13 … s=="mined" … [ -e "$p" ]`) prints
  `missing: <path>` for a mined row whose `used-by` path is absent. `corpus/knowledge/caller-env-routes-receipt-writer.md`
  does not exist yet: it exists as the DRAFT at
  `.ufo/waves/round-66/w1/S66ScribeEntry/knowledge-caller-env-routes.md`. Either land the knowledge entry
  in the same commit as the registry rows, or set these rows' status to `queued` until it lands (a `queued`
  row is not checked for a live `used-by`). The registry rows and the knowledge entry must land together
  (the round-65 M6 lesson: the `used-by` cell and the entry's `source:` line are one binding, both
  directions).
- **`kind` must be one of** `spec|docs|paper|code|tool|dataset|talk|book|community|own-work` — `docs` for
  these three. **`tier`** must be `A|B|C` — `A` (official documentation, authoritative for these scopes).
  **`status`** must be `queued|mined|rejected` — `mined` once the entry cites the row. **`opened`** is an
  ISO date (2026-11-05). **`recheck`** is an ISO date or a cadence (`on-release`, matching S295/S296/S297).
- **Neighbour rows.** S237 already carries git(1)'s `GIT_CONFIG_NOSYSTEM`, S238 already carries git-config(1)'s
  `GIT_CONFIG_COUNT`, S047 carries `core.excludesFile`'s default LOCATION from gitignore(5), S295 carries
  git(1)'s `GIT_INDEX_FILE` and S049 git(1)'s `GIT_NO_LAZY_FETCH`. The three rows above take scopes those
  rows do not hold; the git(1)/git-config(1) URLs are shared with S006/S036/S049/S089/S125/S237/S238/S275/
  S295/S297, so a duplicate-url census warning (W04) is expected and is not a finding (the round-65 lesson
  records the same for S291/S295/S296).
- **No new row is needed for `GIT_CONFIG_NOSYSTEM`** (S237) or `GIT_CONFIG_COUNT` (S238) — the new rows
  cite them in `teaches`/`scope` only as context, and the knowledge entry's `source:` line may cite S237
  and S238 alongside the three new ids.
