# S62ScoutSources — trailer report (round 62, wave 1)

Full report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ScoutSources/report.md`.

## Sources opened (access date 2026-11-05, both HTTP 200)

| id | URL | bytes | sha256 |
|---|---|---|---|
| S292 | https://git-scm.com/docs/git-ls-files | 69017 | `39bbbe6af002214f7ee3075ab4915fc7af05943869a469b89e3393c8cd6f5f08` |
| S291 | https://git-scm.com/docs/git-update-index | 84442 | `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8` |

- **S292 located quote (17 words, verbatim in the raw capture AND the tag-stripped text):**
  `Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1]).`
  Location: `Documentation/git-ls-files.txt--v`, OPTIONS (`h2 id=_options`).
  Corroborating (also verbatim): `tracked file that is skip-worktree` and
  `tracked file that is not either unmerged or skip-worktree`, both under
  `Documentation/git-ls-files.txt--t`.
- **S291 located quote (21 words, verbatim):**
  `This does not work as expected, since Git may still check working tree files against the index when performing certain operations.`
  Location: `Documentation/git-update-index.txt---notes` (NOTES, `h2 id=_notes`).
- **S291 re-open result: VERBATIM YES.** The fresh re-fetch is byte-identical to the stored r61
  capture (same sha256 `ecaa637b…43fb8`, 84442 bytes), and the quote's own sha256 is
  `d2b14aa149d71eea22612cf9250a6b8fc6f9a977e86ab4978fa6bb94d1bf0b56` in both. **No quote failed to
  reproduce.**

## Deliverables (all under `.ufo/waves/round-62/w1/S62ScoutSources/`)

`report.md` · `sources-rows.draft.md` (the two drafted rows + the old→new change note) ·
`gate-block.draft.md` (paste-ready `## Gate`) · `captures/` (2 raw HTML + 2 tag-stripped text +
`SHA256SUMS`) · `quote-check.txt` + `check_quotes.py` · `probe-evidence.txt` + `probe_tags.sh`.

## Drafted registry rows (L1 appends / edits; this seat touched no lane file)

- **S292 (new row, 11 columns, kind `docs`, tier `A`, scope `index tags shown by git ls-files -v`,
  used-by `corpus/knowledge/skip-worktree-concealment.md`, status `mined`, opened 2026-11-05,
  recheck `on-release`)** — the full row text is in `sources-rows.draft.md`.
- **S291 (existing row; ONLY the `recheck` cell changes in place):** `180d` → `2026-11-05`.
  Status `mined` and used-by unchanged. Change note for `corpus/lessons/round-62.md` is in
  `sources-rows.draft.md`.

Both rows validate clean on a scratch copy:
`scripts/sources-census.sh validate --root <scratch> --today 2026-11-05` → `ok`, rc 0;
`census` → rows 2, tier.A 2, status.mined 2, missing 0, rc 0.

## Empirical probe (git 2.56.0, `probe_tags.sh` exit 0)

`ls-files -v` first byte: skip-worktree → **`S`**; assume-unchanged → **`h`** (lowercase); both bits
→ **`s`**; unmerged → **`M`**; dirty-but-unflagged → `H`. `-t` alone prints `H` for the
assume-unchanged path — only `-v` lowercases it. Forged worktree bytes under the flags leave
`git status --porcelain` **empty**; clearing the flags makes porcelain speak. `-z` records are
`TAG␣path\0` with the path unquoted. `git ls-files -v -z` outside a repo exits **128**.
Lane index at the base (read-only): **17350 entries, 17350 `H`** — a refusal on any non-`H` tag
blocks no honest run on today's lane.

## Named limits (full list in report.md §7)

1. The `-v`/`-t` tag semantics are manual facts; the porcelain silence under a flagged path is a
   round probe on git 2.56.0, not a documented guarantee (S291 NOTES denies the guarantee).
2. `M` (unmerged) is not a concealment bit but the frozen rule refuses it with the
   `RECEIPT-INDEX-FLAG-CONCEALED:` class; no frozen matrix case covers it.
3. The candidate must read `-v` records, not `-t` records, or matrix row E is missed.
4. **The L1 must freeze the S291 `recheck` value.** As drafted (`2026-11-05`), the census reports
   the row `overdue 0d` on the day of the change (`overdue --root <scratch> --today 2026-11-05`,
   rc 1). The base value `180d` reports `cadence` and no overdue entry. Keeping `180d` is a
   one-token edit.
5. S292's `used-by` entry currently cites S291 in its `source:` line; if the L1 admits S292 as
   `mined`, that entry's `source:` should also name S292 (L1's edit).
6. `census/round-62/sources/s292-git-ls-files.html` does not exist yet — the L1 copies the capture
   bytes at landing.
7. Tooling: nothing installed or updated; no pacman transaction.
