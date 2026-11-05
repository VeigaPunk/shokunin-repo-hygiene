# S66ScribeEntry — round-66 corpus paperwork (scribe seat)

Lane `souji-shokunin` (`/home/vgpnk/Projects/shokunin/souji-shokunin`), wave `round-66/w1`. Seat type:
scribe (leaf member, no dispatch). Scope: drafts only; NO lane file was edited.

## Files written (all under the seat's own wave dir)

| path | bytes | what it is |
|---|---|---|
| `.ufo/waves/round-66/w1/S66ScribeEntry/knowledge-caller-env-routes.md` | 17267 | draft of `corpus/knowledge/caller-env-routes-receipt-writer.md` |
| `.ufo/waves/round-66/w1/S66ScribeEntry/skill-writer-rule-s5.md` | 6114 | the population row s5 statement + verification (SUPERSEDED by the L1's landing) |
| `.ufo/waves/round-66/w1/S66ScribeEntry/sources-rows-draft.md` | 10973 | three `corpus/SOURCES.md` registry rows + row count before/after |
| `.ufo/waves/round-66/w1/S66ScribeEntry/round-66-lesson-draft.md` | 19418 | draft of `corpus/lessons/round-66.md` (`## Gate` / `## Claims` / `## Mistakes`) |
| `.ufo/waves/round-66/w1/S66ScribeEntry/s5-row.tsv` | 644 | the raw `s5` row extracted from the frozen population (provenance) |
| `.ufo/waves/round-66/w1/S66ScribeEntry.md` | — | this report |

Scratch (host probes, git 2.56.0): `/fast/scratch/hyaku/souji-r66/S66ScribeEntry/probe/` — `rp2`/`rp3`/`rp4`
(replace-ref-base), `routes`/`ig-*` (config and ignore routes), `refs.c` + `refs_v2560.c` (upstream source).

## Numbers this seat measured

**Scout quotes re-sliced independently: 34/34.** Every row of
`.ufo/waves/round-66/w1/S66ScoutSources/quotes.tsv` re-sliced against the delivered `.txt` bytes:
34/34 byte-identical at the stated `byte_offset`, 34/34 `txt_sha256` match, 34/34 ≤25 words, **0 problems**.
The two `.txt` digests: `git-environment.txt` `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035`;
`git-config.txt` `dfc44574996cdf9023e9b61ea37a4aab0fe0c79058b34743d08d5bc788d46054`. The `.html` captures
`534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1` (git(1)) and
`37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226` (git-config(1)) are byte-identical to the
round-64 S295 and round-65 S297 captures already committed in the lane.

**SOURCES.md row count.** `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` →
**220 before**, **223 after** the three drafted rows. Malformed-row check (`NF!=13`) → **0** at HEAD. The
three drafted rows were machine-checked for shape: each has **NF=13**, 11 non-empty cells, no `|` inside a
cell.

**SKILL.md s5.** The s5 `after_pattern` is **167 bytes**. The L1 landed the s5 statement with the writer in
commit `c13fbb4e1b563a78278ddc14316c20252e9a6d8d`; the literal occurs **exactly 1 time** in the SKILL.md blob
at that revision, and per-row occurrence counts are s1 base 1/after 1, s2 base 0/after 1, s3 base 0/after 1,
s4 base 1/after 1, s5 base 1/after 1 — every row resolves to exactly one wording, no `DUPLICATE-LIVE-WORDING`.
This seat's pre-landing draft sentence was checked for the same property (its literal contiguous, zero
collisions with s1–s4) and is recorded for the audit trail, but it is **superseded and must not be pasted**.

**Host probes, git 2.56.0** (all in scratch, git 2.56.0, `/usr/bin/git` sha256
`2912a2a32f408c9b8122e476251b32f4b35f4c3f0c15961686ae87ca456d384c`):

1. `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0=<file>` hides an untracked path
   from `git status --porcelain`; adding `-c core.excludesFile=/dev/null` brings it back. `git config --get
   core.excludesFile` returns the injected path under the injection and `/dev/null` under the `-c` pin — the
   command-line `-c` outranks the injected pair.
2. Legacy `GIT_CONFIG_PARAMETERS="'core.excludesFile=<file>'"` injects the same key on this host and is
   likewise outranked by `-c core.excludesFile=/dev/null`.
3. `GIT_CONFIG_GLOBAL=<crafted global config>` hides the excluded path; `GIT_CONFIG_GLOBAL=/dev/null
   GIT_CONFIG_NOSYSTEM=1` brings it back.
4. **`GIT_REPLACE_REF_BASE` without a trailing slash makes git ABORT**, not misbehave quietly:
   `git status --porcelain` and `git for-each-ref` exit **134** with
   `BUG: refs.c:1908: ref pattern must end in a trailing slash when trimming`. With the trailing slash the
   namespace really moves: with `refs/replace-forged-r66/<real-oid>` pointing at another blob,
   `git cat-file -p HEAD:a.txt` prints the **forged** content, and `GIT_NO_REPLACE_OBJECTS=1` restores the real
   content. `git show-ref`, `git rev-parse --git-dir` and `git ls-files -v` are unaffected by the crash.
5. Ignore routes on git 2.56.0: under `.git/info/exclude`, a tracked `.gitignore` and a repository-local
   `core.excludesFile`, the excluded path is absent from `git status --porcelain` in all three cases.
   `-c core.excludesFile=/dev/null` restores it **only** for the repository-local `core.excludesFile` route —
   the `.git/info/exclude` and tracked-`.gitignore` routes survive the `-c` pin, because neither is the
   `core.excludesFile` key. This sharpens the frozen named limit L1.

**Two of the six refused variables have NO manual anchor at 2.56.0.** `GIT_REPLACE_REF_BASE` and
`GIT_CONFIG_PARAMETERS`: 0 hits in the captured git(1)/git-config(1) pages, 0 in the installed
`git(1)`/`git-config(1)`/`git-replace(1)` man pages, and 0 in upstream `Documentation/git.txt`,
`git-config.txt` and `git-replace.txt` at tag v2.56.0. Their only upstream prose is `refs.c`
(`NAMESPACE_REPLACE`), `environment.h` (`#define GIT_REPLACE_REF_BASE_ENVIRONMENT`, `#define
CONFIG_DATA_ENVIRONMENT`), `config.h` (the `GIT_CONFIG_PARAMETERS` value format) and
`Documentation/RelNotes/2.6.0.adoc`. So rows E2 and E6 can only be grounded on upstream SOURCE — a `docs`
row for them would be false. Digests this seat obtained: `refs.c` at tag v2.56.0
(`a018953688f1b10bddf91bff8747068f5f4746a4`) sha256
`c0e5406b2d198ff26a9da541c85363a48e39fa6c012bc7e82569c7f60298460b`; the same file at the scout's pinned
commit `0ffa3e35c7c82ab8d0de226149fb03b3f7674d05` (post-tag) sha256
`50d953415b73d3eeaa1280ecaadcb350a8faa294f3b5337979c12ceef2d3932c`.

**Round-66 chronology, re-read from the frozen artefacts.** `8410a97e` → `4576f101` is a **2-file** diff
(`census/round-66/c1-counter.py`, 1 line; `census/round-66/c2-mutate.py`, +78): the one changed line is the
E6 fixture's `GIT_REPLACE_REF_BASE` value, `refs/replace-forged-r66` → `refs/replace-forged-r66/`. The
frozen counter's digest equals the preregistration's pin (`273d6fc9ad1f8b1f8091e58439be9e5a8d844e8e0812ddd5c9b50b58585f1490`,
re-measured at HEAD and at `4576f101`). `8410a97e` is an ancestor of the control commit `4864c01f`, and the
control receipt's own `instrument_sha256=` header is the **repaired** digest — so the control was taken
against the repaired instrument, as the preregistration states. Base-writer blob at `045e1034…` sha256
`6be46a05358aa8f3fc97402ffbeeda05ba010efbef568693b1f3ca40b0ef6cf0`, equal to the `src=` recorded in the
control receipt.

**Preregistration bytes.** Attempt-1 blob at `5d17a5de` and at HEAD are byte-identical (sha256
`becb21ba78b5688c6fb0869be0a681e12336d24a418b6fa0f54431d5e61298bc`) — the in-place append was fully
restored. The attempt-2 blob at `02cc6609` and at HEAD are byte-identical (sha256
`400d3dfe9078c65163aaefd8acbef1ccb18ffb2361352bab71b5d8f8e68fd90e`). `git diff 01bc1e16^ 01bc1e16 --
census/round-66/preregistration.txt` shows the append: **+8/−1**; `git show a81280e1 --stat` shows the
restore: **+1/−8**.

## Findings

1. **The L1 landed the s5 statement before this seat's draft reached it** (`c13fbb4e…`, with the writer and
   the QUALITY rows, in one commit). The landed bullet carries the s5 literal byte-exactly and the C2 after
   receipt is green (`findings=0`, `EXIT=0`, `envcfg=1 envred=1`). **This seat's drafted sentence must not
   be pasted**; the draft file records it as superseded. The only actionable consequence is for the lesson:
   the s5 statement's scope is the env routes only, and the L1's landing correctly puts the ignore routes,
   the empty-value refusal and the lexical C2 read in a separate "Named limits, not claimed:" bullet.
2. **`GIT_REPLACE_REF_BASE` and `GIT_CONFIG_PARAMETERS` have no manual anchor at git 2.56.0** (0 hits in
   every manual page and every upstream `Documentation/*.txt` at the tag). The two rows E2 and E6 rest on
   upstream SOURCE, not on documentation. The drafted `sources-rows-draft.md` therefore offers the fourth
   `kind: code` row as the L1's call (row count 223 or 224), and the drafted knowledge entry's Gate records
   the upstream quotes with their file/line provenance.
3. **The E6 fixture value was a hard git abort, not a subtle misread.** Measured: exit **134** with
   `BUG: refs.c:1908: ref pattern must end in a trailing slash when trimming` on `git status --porcelain` and
   `git for-each-ref` for the un-slashed value. The frozen repair (one character) is confirmed by the
   `8410a97e → 4576f101` diff, and the control receipt's `instrument_sha256` header shows the control ran
   against the repaired counter. No control, candidate or after receipt was taken against the crashing value.
4. **The frozen named limit L1 is slightly under-specified about the ignore routes.** Measured: the
   `-c core.excludesFile=<null device>` pin defeats a repository-local `core.excludesFile` but NOT
   `.git/info/exclude` and NOT a tracked `.gitignore`, because neither is the `core.excludesFile` key. The
   knowledge draft states this precisely; the L1 may want the lesson's named-limit text to say it.
5. **The M-ENV kill is demonstrated, not asserted.** `census/round-66/records/c2-mutant-m-env.txt`: the
   round-66 counter on the mutant gives `FINDING SCOPE-OVERREACH s2: … needs writer markers env` and
   `findings=1`, `EXIT=1`; the round-65 counter on the SAME mutant at the same SKILL.md gives `rows=4
   findings=0 verdict=PASS`, `EXIT=0`. That is exactly the round-65 M10 repair the round set out to make.
6. **The registry rows and the knowledge entry are still unlanded** (`corpus/SOURCES.md` at 220 rows; no
   `corpus/knowledge/caller-env-routes-receipt-writer.md`). They must land in ONE commit: the `used-by`
   cell of a `mined` row must name a path that exists at that revision, and the entry's `source:` line must
   name the row (the round-65 M6 lesson). Until then the three rows should be `queued`, not `mined`.

## Out of scope / not done by this seat

- No lane file was edited: `tools/`, `census/`, `corpus/`, `SKILL.md`, `QUALITY.md`, `SCORECARD.md`, `LOG.md`,
  `MANIFEST.json`, `.ufo/state/` and every sibling repo are untouched. `git status --porcelain` at the end
  showed only the L1's own untracked `census/round-66/records/` — this seat added nothing to the lane tree.
- No git/jj mutating command was run in the lane or anywhere else. The only git commands used were
  read-only (`show`, `log`, `diff`, `rev-parse`, `merge-base --is-ancestor`, `status --porcelain`,
  `ls-tree`, `cat-file`). The scratch probes used `git init`/`git add`/`git commit` inside this seat's own
  scratch directory only.
- No counter, gate, selftest or formatter was run: those are the L1's. This seat's numbers are the four
  draft files' contents, the scout-quote re-slicing, the host git probes, and the byte/checksum readings
  quoted above.
- No tool was installed or upgraded this round (no `pacman`, `uv`, `npx` or binary install), so there is no
  tool/version/channel entry to record. The host's git 2.56.0 was used as found.
- No sysctl was read or written; no host state was changed.

## Boundary note

This seat's drafts are drafts. The L1 owns the final wording, the S-ids, the landing order, and the
`## Gate` / `## Claims` / `## Mistakes` text of `corpus/lessons/round-66.md`. Every numeric result quoted
above is either re-measured by this seat or copied from a committed lane receipt, with the command named.
