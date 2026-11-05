# S62ScoutSources — drafted SOURCES registry rows (round 62)

Access date for every row below: **2026-11-05** (git-scm.com served both pages with HTTP 200).

Lane schema (11 columns, `corpus/SOURCES.md` `## Registry` header):
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`

Contract: `SOURCES-CONTRACT-v1` (`/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`)
rule 1 (a row needs URL + access date + a <=25-word located quote grounding `teaches`),
rule 2 (append-only; only `status`, `recheck`, `used-by` change in place, logged old->new in the round lesson).

No `|` appears inside any cell of either drafted row (checked, see report.md §4).

---

## Row 1 — S292 (NEW row; the L1 appends it after the S291 row)

```
| S292 | git-ls-files(1) `-v` status tags — https://git-scm.com/docs/git-ls-files | docs | A | index tags shown by git ls-files -v | OPTIONS `-v` and `-t`; anchor id `Documentation/git-ls-files.txt--v`; accessed 2026-11-05 (HTTP 200; 69017 bytes; sha256 39bbbe6a…f5f08; capture census/round-62/sources/s292-git-ls-files.html); web manual "git-ls-files last updated in 2.55.0" | `Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1]).` (17 words) — with `-t`, `H` is a tracked file that is not either unmerged or skip-worktree and `S` is a tracked file that is skip-worktree, so a path carrying either index bit is not tagged `H` | mined | 2026-11-05 | on-release | corpus/knowledge/skip-worktree-concealment.md |
```

Cell-by-cell:

| # | cell | value |
|---|---|---|
| 1 | id | `S292` (next unused id: the committed registry's max id is S291; `grep '^| S29' corpus/SOURCES.md` → S290, S291 only) |
| 2 | source | `git-ls-files(1) `-v` status tags — https://git-scm.com/docs/git-ls-files` |
| 3 | kind | `docs` (contract enum; the census validator E05 accepts it) |
| 4 | tier | `A` (official git manual, primary for the scope) |
| 5 | scope | `index tags shown by git ls-files -v` |
| 6 | anchor | OPTIONS `-v` and `-t`; anchor id `Documentation/git-ls-files.txt--v`; accessed 2026-11-05 (HTTP 200; 69017 bytes; sha256 `39bbbe6a…f5f08`; capture `census/round-62/sources/s292-git-ls-files.html`); web manual "git-ls-files last updated in 2.55.0" |
| 7 | teaches | the located 17-word quote + what the `-t` tag list says `H` and `S` mean |
| 8 | status | `mined` (cited by `corpus/knowledge/skip-worktree-concealment.md`; the file exists on disk — the census E11 check passes) |
| 9 | opened | `2026-11-05` |
| 10 | recheck | `on-release` (54 of the lane's 67 `git-scm.com` rows use `on-release`; the tag list is git-version-scoped) |
| 11 | used-by | `corpus/knowledge/skip-worktree-concealment.md` |

The S292 row's `used-by` is the path named by the seat spec. The knowledge entry at
`corpus/knowledge/skip-worktree-concealment.md` currently cites **S291** in its `source:` line
and mentions `git ls-files -v` in its `Consequence` section. If the L1 admits S292 as `mined`,
that entry's `source:` line should also name S292 (the r61 lesson's Q62/K1 rule: an admitted
entry's `source:` must cite the row its `used-by` names). This is the L1's edit, not this seat's.

---

## Row 2 — S291 (EXISTING row; in-place `recheck` cell change only)

Old row (committed, `corpus/SOURCES.md:251`, lane base 16fa821fdce00e709d6895ccfc7aaffa465af195),
trimmed to the cells that matter:

```
| S291 | git-update-index(1) skip-worktree — https://git-scm.com/docs/git-update-index | docs | A | concealed worktree divergence in a receipt instrument: a clean `git status` is not evidence that the worktree file matches its committed blob | NOTES: "This does not work as expected, since Git may still check working tree files against the index when performing certain operations." (accessed 2026-11-05; HTTP 200; sha256 ecaa637b…43fb8; capture census/round-61/sources/s291-git-update-index.html). Same URL as S271 at a different scope (--cacheinfo) | the manual does not guarantee the bit's behaviour, so a silent porcelain status cannot certify concealment-free content; the concealment itself is a round probe on git 2.56.0, not a manual fact | mined | 2026-11-05 | 180d | corpus/knowledge/skip-worktree-concealment.md |
```

New row (identical except the `recheck` cell, which moves `180d` → `2026-11-05`):

```
| S291 | git-update-index(1) skip-worktree — https://git-scm.com/docs/git-update-index | docs | A | concealed worktree divergence in a receipt instrument: a clean `git status` is not evidence that the worktree file matches its committed blob | NOTES: "This does not work as expected, since Git may still check working tree files against the index when performing certain operations." (accessed 2026-11-05; HTTP 200; sha256 ecaa637b…43fb8; capture census/round-61/sources/s291-git-update-index.html). Same URL as S271 at a different scope (--cacheinfo) | the manual does not guarantee the bit's behaviour, so a silent porcelain status cannot certify concealment-free content; the concealment itself is a round probe on git 2.56.0, not a manual fact | mined | 2026-11-05 | 2026-11-05 | corpus/knowledge/skip-worktree-concealment.md |
```

Change note to log old -> new in the round lesson (`corpus/lessons/round-62.md`, contract rule 2):

```
S291 recheck `180d` → `2026-11-05` (re-opened 2026-11-05; the NOTES quote still reproduces
verbatim in the capture and in the re-fetch, which is byte-identical to the stored capture);
status `mined` unchanged; used-by `corpus/knowledge/skip-worktree-concealment.md` unchanged.
```

**Measured consequence of the new recheck value, for the L1 to freeze.** The fleet census
(`scripts/sources-census.sh overdue`) reads an ISO-date `recheck` cell as a *due date* and reports
the row overdue on or after it. With `recheck=2026-11-05` and today 2026-11-05, the row is
reported overdue on the same day:

```
souji	overdue	S291 0d recheck=2026-11-05 opened=2026-11-05
```

(`scripts/sources-census.sh overdue --root <scratch> --today 2026-11-05`, exit 1; the same command
over the base row, `recheck=180d`, reports `cadence` and no overdue entry.) The alternative
reading — the row was opened on 2026-11-05 and is re-opened on 2026-11-05, so the 180-day clock has
not run and the cell could stay `180d` — is a one-token edit to the drafted row above and is left
to the L1, which owns the freeze. This seat does not decide it.

**Status / used-by.** Both cells are unchanged, as the seat spec requires: `status` stays `mined`,
`used-by` stays `corpus/knowledge/skip-worktree-concealment.md`. Neither cell is rewritten.

**Where the captures land.** The two captures this seat produced are in
`.ufo/waves/round-62/w1/S62ScoutSources/captures/` (`ls-files.html`, `update-index.html`, plus
tag-stripped `ls-files.txt` and `update-index.txt`, plus `SHA256SUMS`). The L1 copies them to
`census/round-62/sources/` and names them in the registry rows; the S292 row above already names
`census/round-62/sources/s292-git-ls-files.html`, and the S291 row keeps the r61 capture path
`census/round-61/sources/s291-git-update-index.html`, whose sha256 is unchanged
(`ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8`).
