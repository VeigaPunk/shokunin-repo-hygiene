# S66ScoutSources — git documentation source capture for souji round 66 (w1)

Seat: S66ScoutSources (scout). Scope: open the git documentation sources the round-66 C1
env-route rows rest on, mechanically, and deliver raw captures + tag-stripped text + located
quotes with byte offsets. No registry S-ids assigned (the L1 does that). No lane files
touched; every artifact lives under `.ufo/waves/round-66/w1/S66ScoutSources/`.

Milestone: souji r66 (attempt 1) — post-freeze wave, git-environment source capture.

## 1. Deliverables (all under `.ufo/waves/round-66/w1/S66ScoutSources/`)

| file | bytes | sha256 |
|---|---|---|
| `git-environment.html` | 244227 | `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1` |
| `git-environment.txt` | 58863 | `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035` |
| `git-config.html` | 830605 | `37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226` |
| `git-config.txt` | 334668 | `dfc44574996cdf9023e9b61ea37a4aab0fe0c79058b34743d08d5bc788d46054` |
| `quotes.tsv` | 19009 | `fb9cc0d4f8a4df77ec91e96468e9017ca0b350f250a71d489c4e45d287cbfcfc` |
| `recipe.py` | 3287 | `dad463e4111886e8d829a67104f71288d6bd109da96c2f3393d01969770707cd` |
| `locate_quotes.py` | 8868 | `5bac80823dfa9fc7e852fd0dd023c23bae58a1324104e40d78ed35f3e380dd6d` |
| `absences.py` | 4369 | `ac366b10e80fcbe245889a58718746e2ddb96eafb2bca48e2048af71bd09d5b0` |
| `absences.tsv` | 5217 | `9fdc7277a9c50fa1e7b5f03e8012c99a8ed6357aaa6b743a6d338d164e23d9c4` |
| `verify.sh` | 1378 | `144e3b24bf5fc5d0f88b1c89276ce67f0d3a059670f9dccac21bd06a9562b530` |
| `manifest.json` | 3255 | `3123a99d492cd031c4c6cc4f644a043f9ee8b751d26d4941afa098a8b3224364` |
| `upstream-evidence.txt` | 2182 | `411edacb8b84855db29fc6ada79471a6fe4d413ad0f03608098f7e4dee024bea` |
| `git-replace-ref-base-probe.txt` | 1164 | `134ff17cb2caea4f59f1e0c2b54b876c506bac121686fab4305320c98013c690` |
| `config-env-precedence-probe.txt` | 1377 | `6495155d27bdf0f07033fb88e7345499723534c18080b2f917e41a1f6f415ac7` |

## 2. Capture method (mechanical, reproducible, no network needed to re-derive the text)

Fetch (2026-11-05T15:03:48Z, `curl -sSL --max-time 60 -o FILE URL`):

- `https://git-scm.com/docs/git` → HTTP **200**, 244227 bytes → `git-environment.html`
- `https://git-scm.com/docs/git-config` → HTTP **200**, 830605 bytes → `git-config.html`

Both fetches were performed twice; the two captures are byte-identical
(sha256 above matches a second independent fetch).

Tag-strip recipe (`recipe.py`, stdlib `html.parser` only, Python 3.14.8):
skip `<script>`/`<style>` contents; block-level start/end tags → LF, other tags → single
space; whitespace runs collapsed per line; HTML entities unescaped exactly once
(`convert_charrefs=True`); UTF-8, LF endings, exactly one trailing LF.

- `git-environment.txt`: 58863 bytes, 1646 lines, sha256 `624e85ef…f8035`
- `git-config.txt`: 334668 bytes, 7114 lines, sha256 `dfc44574…d46054`

`bash verify.sh` re-strips both captures and confirms the `.txt` files come back
**byte-identical** (deterministic recipe), re-slices every `quotes.tsv` row, and
regenerates the absence table. All steps passed.

Section byte ranges inside the raw HTML (for a reviewer who wants only the section):

- `git-environment.html` → "Environment Variables" section: bytes **180638 – 233881** (53243 bytes)
- `git-config.html` → "ENVIRONMENT" section: bytes **167284 – 170512** (3228 bytes)

## 3. `quotes.tsv` — located quotes

Format (TSV, header row):
`source, quote, byte_offset, txt_sha256, access_date_utc, http_status, line_no, section, block_offset, block_text`

`quote` is always one verbatim line of the `.txt` (byte-identical to the slice at
`byte_offset`, no trailing newline, ≤25 words). `block_text` is the surrounding
definitional block, verbatim, with LF encoded as the two characters `\n`.

**34 rows. Every row was verified by re-slicing the `.txt` at the recorded byte offset and
byte-comparing (`locate_quotes.py --verify` → `verify: 34 rows, all offsets re-sliced and
byte-compared OK`).**

`.txt` sha256 anchors:
- `git-environment.txt` → `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`
- `git-config.txt` → `dfc44574996cdf9023e9b61ea37a4aab0fe0c79058b34743d08d5bc788d46054`

### 3.1 Requested quotes — where each one actually lives

| requested item | located? | source | byte offset(s) in `.txt` |
|---|---|---|---|
| GIT_CONFIG_COUNT / GIT_CONFIG_KEY_ / GIT_CONFIG_VALUE_ definition | YES | git-config | 20861, 20878, 20897, 20918 (def block 20861) |
| GIT_CONFIG_GLOBAL | YES | git-environment **and** git-config | 40065 (env), 20561 (config) |
| GIT_CONFIG_NOSYSTEM | YES | git-environment **and** git-config | 40515 (env), 20716 (config) |
| GIT_OBJECT_DIRECTORY | YES | git-environment | 30732 |
| GIT_ALTERNATE_OBJECT_DIRECTORIES | YES | git-environment | 30937 |
| GIT_REPLACE_REF_BASE | **ABSENT from both man pages** | — | see §4 |
| GIT_NO_REPLACE_OBJECTS | YES | git-environment | 46311 |
| core.excludesFile (git-config) | YES | git-config | 102897 |
| git-config statement on the precedence of command-line `-c` | YES (three places) | git-config | 21340/21358/21411 (ENVIRONMENT), 18472 (FILES read order), 19414 (SCOPES → "the -c option"), 6930/6948 in git-environment (the `-c` option itself) |

Verbatim text of the load-bearing ones (from the `.txt`, LF as line breaks):

- GIT_CONFIG_COUNT family (git-config.txt, ENVIRONMENT, block 776–786):
  `If GIT_CONFIG_COUNT is set to a positive number, all environment pairs` /
  `GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be` /
  `added to the process's runtime configuration. The config pairs are` /
  `zero-indexed. Any missing key or value is treated as an error. An empty` /
  `GIT_CONFIG_COUNT is treated the same as GIT_CONFIG_COUNT=0, namely no` /
  `pairs are processed. These environment variables will override values` /
  `in configuration files, but will be overridden by any explicit options` /
  `passed via git -c .`
- GIT_CONFIG_GLOBAL / GIT_CONFIG_SYSTEM (git-environment.txt, 1281–1289):
  `Take the configuration from the given files instead from global or` /
  `system-level configuration files. If GIT_CONFIG_SYSTEM is set, the` /
  `system config file defined at build time (usually /etc/gitconfig )` /
  `will not be read. Likewise, if GIT_CONFIG_GLOBAL is set, neither` /
  `$HOME/.gitconfig nor $XDG_CONFIG_HOME/git/config will be read. Can` /
  `be set to /dev/null to skip reading configuration files of the` /
  `respective level.`
- GIT_CONFIG_NOSYSTEM (git-environment.txt, 1290–1296):
  `Whether to skip reading settings from the system-wide` /
  `$ ( prefix ) /etc/gitconfig file. This Boolean environment variable can` / …
- GIT_OBJECT_DIRECTORY (git-environment.txt, 1081–1085):
  `If the object storage directory is specified via this` /
  `environment variable then the sha1 directories are created` /
  `underneath - otherwise the default $GIT_DIR/objects` / `directory is used.`
- GIT_ALTERNATE_OBJECT_DIRECTORIES (git-environment.txt, 1086–1096):
  `specifies a ":" separated (on Windows ";" separated) list` / … /
  `objects. New objects will not be written to these directories.`
- GIT_NO_REPLACE_OBJECTS (git-environment.txt, 1413–1415):
  `Setting and exporting this environment variable tells Git to` /
  `ignore replacement refs and do not replace Git objects.`
- core.excludesFile (git-config.txt, 2469–2475):
  `Specifies the pathname to the file that contains patterns to` /
  `describe paths that are not meant to be tracked, in addition` /
  `to .gitignore (per-directory) and .git/info/exclude .` /
  `Defaults to $XDG_CONFIG_HOME/git/ignore .` / …
- `-c` precedence in git-config(1):
  - ENVIRONMENT (lines 784–786): `… These environment variables will override values` /
    `in configuration files, but will be overridden by any explicit options` /
    `passed via git -c .`
  - FILES (724–726): `The files are read in the order given above, with last value found taking` /
    `precedence over values read earlier. When multiple values are taken then all` /
    `values of a key from all files will be used.`
  - SCOPES (746–749): the `command` scope is `GIT_CONFIG_{COUNT,KEY,VALUE} environment variables (see ENVIRONMENT` /
    `below)` / `the -c option`
  - git(1) itself (400–402): `-c <name>=<value>` / `Pass a configuration parameter to the command. The value` /
    `given will override values from configuration files.`

### 3.2 Machine-readable absence table (`absences.tsv`, 24 rows)

Generated by `absences.py`; each row gives the needle's count in the tag-stripped text and
in the tag-stripped raw HTML, so an ABSENT is a measured zero, not a judgement.

| needle | git-environment | git-config |
|---|---|---|
| GIT_CONFIG_COUNT | **0 ABSENT** | 4 present |
| GIT_CONFIG_KEY_ | **0 ABSENT** | 2 present |
| GIT_CONFIG_VALUE_ | **0 ABSENT** | 2 present |
| GIT_CONFIG_PARAMETERS | **0 ABSENT** | **0 ABSENT** |
| GIT_CONFIG_GLOBAL | 2 present | 1 present |
| GIT_CONFIG_NOSYSTEM | 1 present | 1 present |
| GIT_CONFIG_SYSTEM | 2 present | 1 present |
| GIT_OBJECT_DIRECTORY | 2 present | 0 ABSENT |
| GIT_ALTERNATE_OBJECT_DIRECTORIES | 1 present | 0 ABSENT |
| GIT_REPLACE_REF_BASE | **0 ABSENT** | **0 ABSENT** |
| GIT_NO_REPLACE_OBJECTS | 2 present | 0 ABSENT |
| core.excludesFile | 0 ABSENT | 1 present |

## 4. GIT_REPLACE_REF_BASE — the sentence is absent from both man pages

Requested quote: **the GIT_REPLACE_REF_BASE definition. It does not exist in git(1) or
git-config(1).** Measured, not paraphrased:

- `git-environment.txt`: 0 occurrences; `git-environment.html` (tag-stripped): 0.
- `git-config.txt`: 0 occurrences; `git-config.html` (tag-stripped): 0.
- Same for every published version tried: `https://git-scm.com/docs/git/2.20.0`,
  `/2.30.0`, `/2.39.0`, `/2.40.0`, `/2.43.1`, `/2.50.0`, `/2.13.7` → all HTTP 200, all
  0 occurrences. `https://git-scm.com/docs/git-replace` and `/git-replace/2.20.0`,
  `/2.30.0`, `/2.43.1`, `/2.50.0` → all HTTP 200, all 0 occurrences.

Where the variable *is* defined upstream (`upstream-evidence.txt`, from a scratch
read-only sparse clone of `https://github.com/git/git.git` @ `0ffa3e35c7c82ab8d0de226149fb03b3f7674d05`):

- `Documentation/RelNotes/2.6.0.adoc:44-46` — the only prose definition in the whole tree:
  `An environment variable GIT_REPLACE_REF_BASE tells Git to look into` /
  `refs hierarchy other than refs/replace/ for the object replacement` / `data.`
- `refs.c:149` (source comment): `GIT_REPLACE_REF_BASE environment variable. This` …
- `environment.h:25`: `#define GIT_REPLACE_REF_BASE_ENVIRONMENT "GIT_REPLACE_REF_BASE"`
- `common-init.c:44-47`: `replace_ref_base = getenv(GIT_REPLACE_REF_BASE_ENVIRONMENT);` …

A whole-tree grep of upstream `Documentation/` for `GIT_REPLACE_REF_BASE` returns exactly
one hit — `RelNotes/2.6.0.adoc:44`. The variable is undocumented in every man page.

**Host git probe** (`git-replace-ref-base-probe.txt`, host git 2.56.0, fresh scratch repo):
- `GIT_REPLACE_REF_BASE=refs/replace-forged-r66/` (trailing slash) → `git log --oneline` rc=0, normal output.
- `GIT_REPLACE_REF_BASE=refs/replace-forged-r66` (**no** trailing slash) → git **aborts**:
  `BUG: refs.c:1908: ref pattern must end in a trailing slash when trimming` (rc=-6/SIGABRT).
- `GIT_NO_REPLACE_OBJECTS=1` → rc=0.

This is directly relevant to the frozen C1 row E6: the frozen counter's E6 fixture value is
`"refs/replace-forged-r66/"` (with trailing slash), which is the *accepted* form. The
frozen preregistration already records that an earlier instrument commit carried a
`GIT_REPLACE_REF_BASE` value that made git abort and measured the git crash instead of the
writer; this probe reproduces and localises that failure mode, and confirms the frozen
value is the safe one.

## 5. GIT_CONFIG_PARAMETERS — also absent from both man pages

Requested indirectly (C1 row E2 uses `GIT_CONFIG_PARAMETERS`). Measured 0 occurrences in
both `.txt` and both tag-stripped `.html` captures. Upstream it exists only as an internal
propagation channel: `environment.h:20` `#define CONFIG_DATA_ENVIRONMENT "GIT_CONFIG_PARAMETERS"`,
`config.h:192-199` (`git_config_append_parameter`, "Append a config option to the buffer
that can be exported via the GIT_CONFIG_PARAMETERS environment variable"), and
`Documentation/RelNotes/2.31.0.adoc:129` ("the way GIT_CONFIG_PARAMETERS encodes
variable/value pairs has been tweaked to make it more robust").

**Host git probe** (`config-env-precedence-probe.txt`, host git 2.56.0):
- `GIT_CONFIG_PARAMETERS="'core.excludesFile=/tmp/xx'"` → `git config --get core.excludesFile` → `/tmp/xx` (rc=0). The host honours it.
- `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0=/tmp/xx` → `/tmp/xx` (rc=0). The host honours it.
- `git -c core.excludesFile=/tmp/yy config --get core.excludesFile` **with** `GIT_CONFIG_COUNT=1 …` → `/tmp/yy` (rc=0). `-c` wins over the env pair, exactly as git-config(1) ENVIRONMENT states.
- `GIT_CONFIG_NOSYSTEM=1` alone → `git config --get core.excludesFile` rc=1 (no value; the system/global level contributed nothing).

So the two env routes the C1 matrix names are both live on the host git even though one
of them (`GIT_CONFIG_PARAMETERS`) has no prose definition in the man pages.

## 6. The C1 matrix rows this capture underwrites

From `census/round-66/c1-counter.py` (read-only) the E-rows and the env vars they ride on:

- E1 `env-config-count-excludes` → `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_0` / `GIT_CONFIG_VALUE_0` — definition located in git-config(1) ENVIRONMENT, offsets 20861 / 20878 / 20897.
- E2 `env-config-parameters-excludes` → `GIT_CONFIG_PARAMETERS` — **no man-page definition**; semantics confirmed only by host probe (§5).
- E3 `env-config-global-excludes` → `GIT_CONFIG_GLOBAL` — definition located in git(1) 1281–1289 (offset 40065) and git-config(1) 768–771 (offset 20561); the `/dev/null` skip idiom is documented in git(1) line 1288 (`be set to /dev/null to skip reading configuration files of the`).
- E4 `env-object-dir-redirect` → `GIT_OBJECT_DIRECTORY` — git(1) 1081–1085, offset 30732.
- E5 `env-alternates-redirect` → `GIT_ALTERNATE_OBJECT_DIRECTORIES` — git(1) 1086–1096, offset 30937.
- E6 `env-replace-ref-base` → `GIT_REPLACE_REF_BASE` — **no man-page definition**; only the 2.6.0 release note (§4).

Also relevant to the frozen limit (L2): `core.excludesFile` is defined in git-config(1) at
offset 102897 with default `$XDG_CONFIG_HOME/git/ignore` — so the writer's
`-c core.excludesFile=<null device>` pin changes the documented default, and the
`GIT_CONFIG_GLOBAL`→null-device pin plus `GIT_CONFIG_NOSYSTEM=1` are exactly the two
documented "skip this level" mechanisms (git(1) 1288 and 1290).

## 7. Confidence and remaining unknowns

- **High confidence** (directly measured, re-verifiable offline): every quote and offset in
  `quotes.tsv`; every ABSENT in `absences.tsv`; the two `.txt` sha256 anchors; the HTTP
  statuses (200) and access date (2026-11-05T15:03:48Z); the section byte ranges.
- **High confidence** (upstream tree grep + host probe): `GIT_REPLACE_REF_BASE` and
  `GIT_CONFIG_PARAMETERS` have no prose definition in git(1) or git-config(1) in any
  published version checked; the only upstream prose for the first is `RelNotes/2.6.0.adoc:44`.
- **Unknown / out of scope here**: whether the L1's registry wants an explicit *absence*
  citation for `GIT_REPLACE_REF_BASE` in the C1 write-up, or the release note + `refs.c`
  comment to stand as the citation. I did not assign S-ids.
- **Unknown**: whether the round-66 writer's own refusal messages quote any of these
  definitions verbatim — that is the executor's and the reviewer's check, not mine.

## 8. Tooling / host notes

- No package was installed or upgraded. `curl 8.23.0 (x86_64-pc-linux-gnu) libcurl/8.23.0
  OpenSSL/3.6.5` (system) and `Python 3.14.8` (system) were already present and were used
  as-is. No `pacman`/`uv`/`npm` transaction was performed, so the host-wide pacman pause was
  not touched.
- No sysctl was changed. No `bwrap`/sandbox was needed; nothing in this seat required
  `user.max_user_namespaces`.
- Scratch only: `/fast/scratch/hyaku/souji-r66/S66ScoutSources/` (raw captures, the
  upstream sparse clone, the probe repo). No `/tmp` file over 50 MB was used; the upstream
  clone is `--depth 1 --filter=blob:none --sparse` (8.1 MB of Documentation checked out).
- The lane repo was never mutated: `git rev-parse --show-toplevel` in
  `/home/vgpnk/Projects/shokunin/souji-shokunin` prints that directory, and
  `git status --porcelain` is empty apart from this seat's untracked wave dir
  (`.ufo/waves/` is gitignored via `.gitignore:1`). At the time this seat wrote its
  report the lane HEAD was the frozen attempt-2 freeze commit
  `02cc660965e027c6c6390604e50702bb06377b2e`; the L1 has since landed
  `c13fbb4e` ("round-66: writer rejects caller-injected GIT_CONFIG_* and object-redirect
  env routes; full mode bits; SKILL/QUALITY r66 rows", touching `SKILL.md`,
  `corpus/QUALITY.md`, `tools/souji-receipt-write.py`). This seat's captures were taken
  from the upstream documentation, not from the lane, so the L1's commit does not affect
  any byte of this seat's deliverables; `bash verify.sh` was re-run after that landing and
  still reports both `.txt` files byte-identical on re-strip and 34/34 quote rows
  re-sliced OK.

## 9. Re-verification commands

```
cd .ufo/waves/round-66/w1/S66ScoutSources
bash verify.sh
```

Expected output: both `.txt` files byte-identical on re-strip; `verify: 34 rows, all
offsets re-sliced and byte-compared OK`; `wrote …/absences.tsv (24 rows)`.

Report: .ufo/waves/round-66/w1/S66ScoutSources.md
