# S62ScoutSources — report (souji round 62, wave 1)

Seat: `S62ScoutSources` (scout, leaf — no subagent dispatch).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, lane base `16fa821fdce00e709d6895ccfc7aaffa465af195`.
Scope: open and verify the two sources the round's C1 claim cites, and draft their registry rows.
Nothing in the lane registry was touched: `corpus/SOURCES.md` at the lane base is byte-identical to
the working copy (verified by `git diff` — empty), and the only files this seat wrote are under
`.ufo/waves/round-62/w1/S62ScoutSources/`.

## 0. Deliverables (absolute paths)

| path | what |
|---|---|
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ScoutSources/report.md` | this report |
| `…/S62ScoutSources/sources-rows.draft.md` | the two drafted registry rows (S292 new; S291 in-place `recheck` change) + the old→new change note |
| `…/S62ScoutSources/gate-block.draft.md` | paste-ready `## Gate` block for `corpus/lessons/round-62.md` |
| `…/S62ScoutSources/captures/ls-files.html` | raw capture, git-ls-files(1), 69017 bytes |
| `…/S62ScoutSources/captures/ls-files.txt` | tag-stripped text version of the same capture |
| `…/S62ScoutSources/captures/update-index.html` | raw capture, git-update-index(1), 84442 bytes |
| `…/S62ScoutSources/captures/update-index.txt` | tag-stripped text version of the same capture |
| `…/S62ScoutSources/captures/SHA256SUMS` | digests of the four capture files (verified with `sha256sum -c`, rc 0) |
| `…/S62ScoutSources/quote-check.txt` | the quote-verification record (verbatim check, word counts, quote digests) |
| `…/S62ScoutSources/check_quotes.py` | the script that produced `quote-check.txt` (exit 0 = all quotes verbatim and ≤25 words) |
| `…/S62ScoutSources/probe-evidence.txt` | the empirical `git ls-files -v` probe record |
| `…/S62ScoutSources/probe_tags.sh` | the script that produced `probe-evidence.txt` (exit 0 = every observed tag letter matched) |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ScoutSources.md` | the trailer report (this file's sibling at the wave level) |

## 1. URLs and access date

Access date for both pages: **2026-11-05** (`ACCESS=$(date -I)` → `2026-11-05`).

| id | URL | HTTP | bytes | sha256 |
|---|---|---|---|---|
| S292 | https://git-scm.com/docs/git-ls-files | 200 | 69017 | `39bbbe6af002214f7ee3075ab4915fc7af05943869a469b89e3393c8cd6f5f08` |
| S291 | https://git-scm.com/docs/git-update-index | 200 | 84442 | `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8` |

Command: `curl -sL -w '%{http_code}' -o <file> <url>` (both reported `200`).
Web-manual revision strings read off the pages: git-ls-files "last updated in 2.55.0";
git-update-index "last updated in 2.52.0". Host git: **2.56.0** (`git --version`).

**SHA256SUMS path:** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ScoutSources/captures/SHA256SUMS`
(contents = the four capture digests; `sha256sum -c SHA256SUMS` → all four `OK`, rc 0.)

## 2. The two located quotes

Verification method (the lane's round-61 method, unchanged): strip HTML tags with `<[^>]+>`,
`html.unescape`, map U+00A0/U+2009/U+200B/U+2007 to a space, collapse whitespace runs to one
space; a quote is VERBATIM when it is a contiguous substring of the normalized text. Each quote was
checked twice — against the raw capture normalized in memory, and against the tag-stripped text
file — and both must succeed. Script `check_quotes.py` exits 0 only if both checks pass for every
quote and every quote is ≤25 words. Run: `python3 check_quotes.py` → **EXIT=0**
(record: `quote-check.txt`).

### S292 — git-ls-files(1) `-v`

- **Located quote (17 words):**
  `Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1]).`
- **Location:** `Documentation/git-ls-files.txt--v`, OPTIONS section (`h2 id=_options`), the `-v`
  option paragraph. In the capture the paragraph begins at the `<dt … id="Documentation/git-ls-files.txt--v">`
  anchor; in the tag-stripped text the same sentence sits between the `-t` tag list and the `-f`
  paragraph.
- VERBATIM in the raw capture (normalized): **YES** (offset 8351). VERBATIM in the tag-stripped
  text: **YES** (offset 7629). Quote sha256 `addf9d6848340fe6859afb7212c6b6f35d0a9d0fe3fd692affebd26da11bbbc7`.
- Corroborating quotes from the same `-t` status-tag list, also verbatim (5 and 9 words):
  - `tracked file that is skip-worktree` — anchor `Documentation/git-ls-files.txt--t` (tag `S`),
    sha256 `a20da070b4cfa3c9f493d480a93e8045004e046a053135816d39e8b9f311bd0c`
  - `tracked file that is not either unmerged or skip-worktree` — anchor
    `Documentation/git-ls-files.txt--t` (tag `H`), sha256 `46a5276e79bdd6ec9a519a6bcbdd6d476b2706d464b1ed0c85d143111a1e63f9`
- Corroboration on the host: the installed `git-ls-files(1)` man page (git 2.56.0) carries the same
  sentence, with the cross-reference rendered `(see git-update-index(1))` instead of
  `(see git-update-index[1])` — the man page variant is verbatim after the same normalisation
  (1 occurrence). The web quote is the one filed; the man-page difference is only the reference
  style.

### S291 — git-update-index(1) NOTES (re-opened)

- **Located quote (21 words):**
  `This does not work as expected, since Git may still check working tree files against the index when performing certain operations.`
- **Location:** NOTES section (`h2 id=_notes`), anchor `Documentation/git-update-index.txt---notes`.
  Its surrounding paragraph begins "Users often try to use the assume-unchanged and skip-worktree
  bits to tell Git to ignore changes to files that are tracked."
- VERBATIM in the raw capture (normalized): **YES** (offset 25108). VERBATIM in the tag-stripped
  text: **YES** (offset 24386). Quote sha256 `d2b14aa149d71eea22612cf9250a6b8fc6f9a977e86ab4978fa6bb94d1bf0b56`.
- Also verbatim on the host: the installed `git-update-index(1)` man page, 1 occurrence after
  normalisation.

**S291 re-open result: VERBATIM — YES.** The quote reproduces verbatim in the fresh 2026-11-05
re-fetch, in the tag-stripped text of that re-fetch, and in the stored r61 capture
`census/round-61/sources/s291-git-update-index.html`. The fresh re-fetch is **byte-identical** to
the stored capture: sha256 `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8`,
84442 bytes — the same digest the S291 row records (`ecaa637b…43fb8`). The quote's own sha256 is
`d2b14aa149d71eea22612cf9250a6b8fc6f9a977e86ab4978fa6bb94d1bf0b56` in all three.

**No quote failed to reproduce.** All five quotes checked (2 primary + 2 corroborating + the S291
re-open) are verbatim in both the raw capture and the tag-stripped text, and all are ≤25 words.

## 3. Empirical probe — the observed tag letters

Script `probe_tags.sh` (exit 0 = every observed letter matched the expectation); full record in
`probe-evidence.txt`. Run: `sh probe_tags.sh /fast/scratch/hyaku/souji-r62/S62ScoutSources` → **EXIT=0**.
Every fixture repo was created with `mktemp -d -p "$S"` + `git -C "$D" init -q`, every git call names
`-C "$D"`, and `git -C "$D" rev-parse --show-toplevel` was asserted to equal `$D` before the first
commit. The lane was only READ (`git -C <lane> ls-files -v`).

| case | command | observed first byte | rc |
|---|---|---|---|
| baseline, no flags | `git -C "$D" ls-files -v` | `H` for both paths | 0 |
| skip-worktree | `git -C "$D" update-index --skip-worktree tools/counter.py` then `ls-files -v` | **`S`** | 0 |
| assume-unchanged | `git -C "$D" update-index --assume-unchanged tools/instr.sh` then `ls-files -v` | **`h`** (lowercase) | 0 |
| both bits on one path | `update-index --skip-worktree` + `--assume-unchanged` | **`s`** (lowercase `S`) | 0 |
| same paths, `-t` instead of `-v` | `ls-files -t` | `S` and `H` — `-t` does **not** lowercase the assume-unchanged path | 0 |
| unmerged path (merge conflict) | `ls-files -v` | **`M`** (three records, one per stage) | 0 |
| dirty worktree, **no** index flags | `ls-files -v` | `H` for both the modified and the deleted path | 0 |
| forged worktree bytes under both flags | `git -C "$D" status --porcelain` | **empty output** (porcelain silent) | 0 |
| same forged bytes after `update-index --no-skip-worktree` / `--no-assume-unchanged` | `git -C "$D" status --porcelain` | ` M tools/counter.py` / ` M tools/instr.sh` (porcelain now speaks) | 0 |
| outside a repository | `git -C "$S" ls-files -v -z` | fatal, **rc 128** | 128 |

`-z` record layout (`od -c`): `S␣tools/counter.py\0h␣tools/instr.sh\0` — one NUL-terminated record
per path, first byte = tag, second byte = space, then the path. Under `-z` the path is **not**
quoted: a path containing a tab, a space or a double quote appears raw (verified: `H\0tab\tname.txt\0`
and `H␣we ird"na me.txt\0`), so the first byte of each record is always the tag and the path cannot
be confused with the tag.

Lane index at the base, read-only: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -v | wc -l`
→ **17350** entries, and `… | cut -c1 | sort | uniq -c` → **`17350 H`** — i.e. every entry is `H`,
no flagged path. This confirms the claim's stated baseline: a refusal on any non-`H` tag blocks no
honest run on today's lane index.

**Two observations the candidate's frozen rule should be read against** (both are probes, not
manual facts, and neither changes the frozen design):

1. `-t` does not mark the assume-unchanged path (`H`), only `-v` does (`h`). The rule must read
   `-v` records, not `-t` records, or case E (assume-unchanged) would not be caught.
2. The tag alphabet `-v` can produce includes `M` (unmerged) and `S`/`h`/`s` (the two index bits).
   `M` is not a concealment bit — it is an unmerged index entry. Under the frozen rule ("every
   record whose tag is not `H` ⇒ refuse"), a conflicted index is refused with the
   `RECEIPT-INDEX-FLAG-CONCEALED:` class although nothing was concealed. That is the frozen
   behaviour, and a merge-conflicted tree is dirty anyway, so the base dirty check would refuse it
   too; the class name is the only thing at stake, and the frozen 7-case matrix does not include an
   unmerged case.

## 4. The two drafted registry rows

Full text with a cell-by-cell table, the old and new S291 rows, and the old→new change note:
**`sources-rows.draft.md`**. Schema: `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`
(11 columns; contract `SOURCES-CONTRACT-v1`).

**Row 1 — S292 (new row; the L1 appends it after S291):**

```
| S292 | git-ls-files(1) `-v` status tags — https://git-scm.com/docs/git-ls-files | docs | A | index tags shown by git ls-files -v | OPTIONS `-v` and `-t`; anchor id `Documentation/git-ls-files.txt--v`; accessed 2026-11-05 (HTTP 200; 69017 bytes; sha256 39bbbe6a…f5f08; capture census/round-62/sources/s292-git-ls-files.html); web manual "git-ls-files last updated in 2.55.0" | `Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1]).` (17 words) — with `-t`, `H` is a tracked file that is not either unmerged or skip-worktree and `S` is a tracked file that is skip-worktree, so a path carrying either index bit is not tagged `H` | mined | 2026-11-05 | on-release | corpus/knowledge/skip-worktree-concealment.md |
```

**Row 2 — S291 (existing row; only the `recheck` cell changes in place):**

```
| S291 | git-update-index(1) skip-worktree — https://git-scm.com/docs/git-update-index | docs | A | concealed worktree divergence in a receipt instrument: a clean `git status` is not evidence that the worktree file matches its committed blob | NOTES: "This does not work as expected, since Git may still check working tree files against the index when performing certain operations." (accessed 2026-11-05; HTTP 200; sha256 ecaa637b…43fb8; capture census/round-61/sources/s291-git-update-index.html). Same URL as S271 at a different scope (--cacheinfo) | the manual does not guarantee the bit's behaviour, so a silent porcelain status cannot certify concealment-free content; the concealment itself is a round probe on git 2.56.0, not a manual fact | mined | 2026-11-05 | 2026-11-05 | corpus/knowledge/skip-worktree-concealment.md |
```

Change note for the round lesson (contract rule 2: in-place changes are logged old→new):

```
S291 recheck `180d` → `2026-11-05` (re-opened 2026-11-05; the NOTES quote still reproduces
verbatim in the capture and in the re-fetch, which is byte-identical to the stored capture);
status `mined` unchanged; used-by `corpus/knowledge/skip-worktree-concealment.md` unchanged.
```

Constraint checks on both drafted rows:

- **11 columns** — verified by splitting each row on `|`: 11 cells each (`raw '|' count=12`,
  `fields=11`).
- **No `|` inside any cell** — verified: the cell split yields exactly 11 cells and no cell
  contains a `|` (the check prints a finding per offending cell; it printed none).
- **Kind `docs`, tier `A`, scope `index tags shown by git ls-files -v`** — as specified.
- **S292 `used-by` = `corpus/knowledge/skip-worktree-concealment.md`** — as specified, and the path
  exists on disk in the lane (`corpus/knowledge/skip-worktree-concealment.md`), so the census E11
  check passes.
- **S291: status `mined` unchanged, `used-by` unchanged** — as specified. Only `recheck` moves.
- **Gate block format** — `gate-block.draft.md` carries the round-61 Gate's shape: source, URL,
  anchor, access date, located quote with word count, scope, caveat; plus the rejected inference.

**Registry validation (run on a scratch copy, never on the lane).** A scratch lane was built under
the seat's scratch root with exactly these two rows in a `## Registry` table and the
`skip-worktree-concealment.md` file present, then:

- `scripts/sources-census.sh validate --root <scratch> --today 2026-11-05` → `souji ok …`, **rc 0**
  (no E01–E11 finding).
- `scripts/sources-census.sh census --root <scratch>` → `rows 2`, `tier.A 2`, `status.mined 2`,
  `FLEET.missing 0`, **rc 0**.
- `scripts/sources-census.sh overdue --root <scratch> --today 2026-11-05` → prints
  `souji cadence S292 recheck=on-release opened=2026-11-05` and
  `souji overdue S291 0d recheck=2026-11-05 opened=2026-11-05`, **rc 1**.

**The S291 overdue line is a real, measured consequence the L1 must freeze.** The fleet census reads
an ISO-date `recheck` cell as a *due date* and reports the row overdue on or after it; with
`recheck=2026-11-05` and today 2026-11-05, S291 reads as overdue the same day. The same command over
the base row (`recheck=180d`) reports `cadence` and no overdue entry. The alternative reading — S291
was opened 2026-11-05 and is re-opened 2026-11-05, so the 180-day clock has not run and the cell
could stay `180d` — is a one-token edit to the drafted row and is the L1's call. This seat drafts
the row exactly as the seat spec states it (old `180d` → new `2026-11-05`) and does not decide.

## 5. Sanity read of the lane (no registry edits)

`git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 16fa821fdce00e709d6895ccfc7aaffa465af195:SCORECARD.md >/dev/null`
→ **rc 0**. The file resolves at the lane base.
`git -C … show 16fa821fdce00e709d6895ccfc7aaffa465af195:corpus/SOURCES.md | grep -c '^| S29'` → **2**
(S290, S291 — so S292 is the next free id; the committed registry's max id is S291).

## 6. Commands run, with exit codes

| # | command | rc | result |
|---|---|---|---|
| 1 | `curl -sL -w '%{http_code}' -o ls-files.html https://git-scm.com/docs/git-ls-files` | 0 | HTTP 200, 69017 bytes |
| 2 | `curl -sL -w '%{http_code}' -o update-index.html https://git-scm.com/docs/git-update-index` | 0 | HTTP 200, 84442 bytes |
| 3 | `python3 check_quotes.py` | **0** | all 4 quotes verbatim in raw capture AND tag-stripped text; all ≤25 words |
| 4 | `sh probe_tags.sh <scratch>` | **0** | every observed tag letter matched the expectation |
| 5 | `sha256sum -c SHA256SUMS` (in `captures/`) | **0** | 4 files OK |
| 6 | `scripts/sources-census.sh validate --root <scratch> --today 2026-11-05` | **0** | `ok`, no E-finding |
| 7 | `scripts/sources-census.sh census --root <scratch>` | **0** | rows 2, tier.A 2, status.mined 2, missing 0 |
| 8 | `scripts/sources-census.sh overdue --root <scratch> --today 2026-11-05` | **1** | S291 overdue 0d (the consequence named in §4) |
| 9 | `git show 16fa821…:SCORECARD.md >/dev/null` | 0 | resolves at the lane base |
| 10 | `git show 16fa821…:corpus/SOURCES.md \| grep -c '^| S29'` | 0 | 2 (S290, S291) |
| 11 | `git -C <lane> ls-files -v \| wc -l` / `\| cut -c1 \| sort \| uniq -c` | 0 | 17350 entries, 17350 `H` |
| 12 | `git -C "$D" ls-files -v -z` outside a repo | **128** | the failed-read path the candidate refuses on |
| 13 | `python3` row-cell check (11 cells, no `|` inside a cell) | 0 | both rows: 11 cells, no offending cell |

No `git commit`, `git add`, `git push`, `git stash`, `git checkout`, `git reset` or `jj` command was
run in the lane or the fleet repo. The only lane git calls were read-only (`show`, `rev-parse`,
`ls-files`, `log`, `status`, `diff`).

## 7. Named limits

1. **The `-v` tag semantics are a manual fact; the concealment is a probe.** The S292 row sources
   what the letters *mean* (`H` = tracked and neither unmerged nor skip-worktree; `S` = tracked and
   skip-worktree; `-v` lowercases the assume-unchanged tag). It does **not** source that
   `git status --porcelain` stays silent for such a path — that silence is the round-62 probe on
   git 2.56.0 (§3), and the S291 NOTES passage explicitly denies the manual guarantees it. Both
   rows say so in their `teaches` cells.
2. **The probe is version-scoped** (git 2.56.0, host). The tag letters are a git-version fact; the
   manual's `-t` list is version-independent for those three entries, but the lowercase `-v`
   marking was read off the host page "last updated in 2.55.0" and confirmed on the 2.56.0 man page.
3. **The `M` tag is not a concealment bit.** Under the frozen rule, an unmerged index entry is
   refused with the `RECEIPT-INDEX-FLAG-CONCEALED:` class. The frozen 7-case matrix has no unmerged
   case, so this does not affect the frozen predicate, but the class name over-reports there.
4. **`-v` is required, not `-t`.** The probe shows `-t` prints `H` for an assume-unchanged path;
   only `-v` prints the lowercase tag. A candidate that read `-t` would miss matrix row E.
5. **The S291 `recheck` cell value is the L1's freeze.** This seat drafts `180d` → `2026-11-05` as
   the seat spec states; the census then reports the row overdue on the day of the change (§4). The
   alternative (`180d` retained) is a one-token edit.
6. **S292's `used-by` names an entry that currently cites S291 only.** `corpus/knowledge/skip-worktree-concealment.md`
   has `source: S291 — …` in its header. If the L1 admits S292 as `mined` with that `used-by`, the
   entry's `source:` line should also name S292 (the round-61 Q62/K1 rule). That entry edit is the
   L1's, outside this seat's write scope.
7. **The S292 capture path in the drafted row is a planned landing path.**
   `census/round-62/sources/s292-git-ls-files.html` does not exist yet; the bytes are in this
   seat's `captures/` directory and the L1 copies them (and the S291 re-fetch, if it wants a
   round-62 capture of the same page) at landing.
8. **No capture of the man pages was committed.** The man pages were read for corroboration only
   (`man git-ls-files`, `man git-update-index`, git 2.56.0); the filed quotes are the web-page
   wording. The man page's cross-reference style differs (`(1)` vs `[1]`).
9. **Tooling: nothing installed or updated.** No pacman transaction, no `uv tool install`, no
   binary drop-in. The seat needed only `curl`, `python3` (stdlib), `git` 2.56.0, `sha256sum`,
   `od`, and the lane's own `scripts/sources-census.sh`.

## 8. Scratch hygiene

All scratch work lived under `/fast/scratch/hyaku/souji-r62/S62ScoutSources/` (fixture repos,
capture staging, the mini validation lane). Nothing was written under `/tmp`. The scratch tree is
removed at the end of this seat's run; every artefact kept is already copied into the delivery
directory above.
