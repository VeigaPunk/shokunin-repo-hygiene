# ScribeSourcesRows — C3 registry append block (S115–S119)

STATUS: PASS — five rows drafted in the registry's exact 11-column order and validated in a scratch
mirror: `sources-census.sh validate` exits 0 with **0 E-findings** and the pre-existing **30
W04** warnings unchanged, rows 114 → 119. S115–S117 are unconditional; S118/S119 are admitted on
ScoutCommunity's confirmation (both pages HTTP 200, 2026-10-25). One path conflict needs the L1's
decision (Finding 1); nothing here is appended — `corpus/SOURCES.md` is untouched.

Lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (read at 2026-10-25T08:20Z; `git status
--porcelain` = 14 paths). Registry at base: 114 rows, max id S114, 0 E-findings, 30 W04
(`ScoutRegistryCensus.md` E1, re-read this run).

## Deliverable — append inside `## Registry`, not at end of file

The rows go **after the S114 row and before the blank line that precedes `## Paths`**. Appending at
EOF places them under `## Paths` and the census reports `E12 row outside Registry section` for each
(measured, see Evidence row 4). Column order copied from the header line
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`.

### Block A — unconditional (C3's three rows, S115–S117)

```markdown
| S115 | git-count-objects(1) — https://git-scm.com/docs/git-count-objects | docs | A | the -v field set at git 2.56.0, including the garbage and size-garbage file counts and alternate paths; not the reachable-graph statistics git repo structure reports (S035) and not a write-safety or concurrency claim | § OPTIONS -v/--verbose field list; web manual last updated 2.51.1 (2.51.2 → 2.56.0 no changes), opened 2026-10-25; installed man page git 2.56.0-1 /usr/share/man/man1/git-count-objects.1.gz | garbage counts files neither valid loose objects nor valid packs; size-garbage is their KiB; alternate lists other object databases; no write side effect documented | mined | 2026-10-25 | on-release | corpus/knowledge/repo-size-census-readonly.md |
| S116 | git-fsck(1) — https://git-scm.com/docs/git-fsck | docs | A | fsck's option boundary for a reachability census: which options print and which one writes; not the gc reachability rule of S063 and not a completeness or concurrency claim | § OPTIONS --unreachable, --dangling/--no-dangling, --no-reflogs, --lost-found, and the <object> default head set; web manual last updated 2.53.0 (2.54.0 → 2.56.0 no changes), opened 2026-10-25; installed man page git 2.56.0-1 /usr/share/man/man1/git-fsck.1.gz | --unreachable prints objects unreachable from any reference node; --lost-found writes dangling objects into .git/lost-found/commit/ or .git/lost-found/other/; default heads include index and reflogs | mined | 2026-10-25 | on-release | corpus/knowledge/repo-size-census-readonly.md |
| S117 | git-prune(1) — https://git-scm.com/docs/git-prune | docs | A | prune's own deletion scope (unpacked unreachable objects only; packed objects remain), dry run and expiry, plus its advice to prefer git gc; not the grace periods of S002 and not a recommendation to prune | § DESCRIPTION, § OPTIONS -n/--dry-run and --expire; web manual last updated 2.43.0 (2.43.1 → 2.56.0 no changes), opened 2026-10-25; installed man page git 2.56.0-1 /usr/share/man/man1/git-prune.1.gz | prune removes unpacked objects unreachable from the given heads, leaves packed ones, offers -n dry-run, and --expire bounds loose-object age | mined | 2026-10-25 | on-release | corpus/knowledge/repo-size-census-readonly.md |
```

### Block B — conditional on ScoutCommunity's confirmation (S118, S119, tier B)

ScoutCommunity (`w1/ScoutCommunity.md` Finding 1/2, `STATUS: PASS`) confirms both pages exist and
are reachable on 2026-10-25, so the condition is **satisfied**; append Block B in the same edit.

```markdown
| S118 | Git のガベージコレクションについて (Qiita, koseki) — https://qiita.com/koseki/items/f1af58f1ec1693f0536a | community | B | the gc.auto 6700 loose-object threshold as a Japanese practitioner restates it from git 1.9.2 config help; the page never glosses the count-objects garbage field | § 設定 gc.auto (6700); datePublished 2015-06-13, quotes git help config v1.9.2; opened live 2026-10-25 (HTTP 200) | restates the gc.auto default of 6700 loose objects, quoting git 1.9.2 config help; a page about gc thresholds, not the garbage field | mined | 2026-10-25 | 180d | corpus/knowledge/count-objects-garbage-semantics-r24.md |
| S119 | Git 仓库瘦身全攻略 (CSDN, weixin_33940469) — https://bbs.csdn.net/weixin_33940469/article/details/100327798 | community | B | a Chinese count-objects -vH field table that glosses garbage as files Git cannot recognise while mislabelling the unit as size, and restates a 6700 threshold; not the field's authority | § 2.1 count-objects 与 du field table; publishTime 2026-09-19 05:45, opened live 2026-10-25 (HTTP 200), body paywalled after the table | glosses garbage as the files Git cannot recognise, with a unit error on size; restates a 6700 loose-object auto-gc threshold | mined | 2026-10-25 | 180d | corpus/knowledge/count-objects-garbage-semantics-r24.md |
```

If the L1 instead lands entry 2 at the wave item's filename, replace the two Block B `used-by`
cells with `corpus/knowledge/count-objects-garbage-readings-r25.md` — see Finding 1. Never name both
paths in one cell: `E11` fails on whichever file does not exist.

### `source:` ids the two drafted entries cite (row-citation proof)

| entry draft | `source:` lines it carries | rows that must exist |
|---|---|---|
| `w1/ScribeEntryRepoSize.md` (→ `corpus/knowledge/repo-size-census-readonly.md`) | `S115` git-count-objects, `S116` git-fsck, `S117` git-prune | Block A, all three |
| `w1/ScribeEntryGarbage.md` (→ path per Finding 1) | `S118` qiita JA, `S119` csdn ZH | Block B, both |

Every one of S115–S119 is cited by an admitted entry and every cited id resolves in the appended
registry (`Evidence` row 6); no row in either block is uncited, so nothing here needs dropping.

## Evidence

All commands read-only. Scratch: `/var/tmp/souji-r23-ScribeSourcesRows/` (removed before yield).

1. **Registry shape and the column order copied.**
   `sed -n '95,140p' corpus/SOURCES.md` → header `| id | source | kind | tier | scope | anchor |
   teaches | status | opened | recheck | used-by |`; 11 cells per row; style sampled from S001–S004
   (installed-man-page anchors) and S110–S114 (snapshot anchors, `mined | 2026-10-25 | 180d`).
   `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `114`;
   `grep -oE '^\| S[0-9]{3,}' … | sort | tail -3` → `S112 S113 S114`.
2. **Sources opened this run (2026-10-25), live and installed.**
   `curl -sS https://git-scm.com/docs/git-{count-objects,fsck,prune}` → HTTP 200; version banners
   `last updated in 2.51.1` / `2.51.2 → 2.56.0 no changes`; `last updated in 2.53.0` / `2.54.0 →
   2.56.0 no changes`; `last updated in 2.43.0` / `2.43.1 → 2.56.0 no changes`.
   `pacman -Q git` → `git 2.56.0-1`; `man -w git-count-objects git-fsck git-prune` → the three
   `/usr/share/man/man1/git-*.1.gz` paths named in the anchors; `man git-count-objects | col -bx`,
   `man git-fsck | col -bx`, `man git-prune | col -bx` → full text read (field list, `--lost-found`
   path pattern, prune DESCRIPTION/OPTIONS).
   `git count-objects -v` in the lane (read-only, no write side effect documented or observed) →
   `count: 5051 / size: 35828 / in-pack: 1544 / packs: 3 / size-pack: 8791 / prune-packable: 0 /
   garbage: 0 / size-garbage: 0` — the field list is live on this host. No `alternate` line here
   because no alternate is configured; the page's own wording is what the row teaches.
3. **Community pages (Block B's condition).**
   `curl -sS -o /dev/null -w 'http=%{http_code}' <url>` → `http=200` for both, twice.
   `grep -oE '"datePublished":"[^"]*"'` (qiita) → `2015-06-13T18:52:41.000+09:00`;
   `grep -oE '"publishTime":"[^"]*"'` (csdn) → `2026-09-19 05:45:09`.
   Verbatim spans located in the fetched bytes: `gc.auto (6700)`, `The default value is 6700.
   Setting this to 0 disables it.` (qiita § 設定); `无法被 Git 识别的垃圾文件大小` (csdn § 2.1
   field table, `garbage` row) and the paywall marker `最低 0.47元/天 开通会员,解锁全文` after that
   table. `grep -c 'count-objects'` on the qiita text → `0`, which is why S118's scope says the page
   never glosses the field.
4. **Scratch validation — the append block as bytes, both variants.**
   Mirror = copy of `corpus/SOURCES.md` with the block inserted before `## Paths`, plus empty stubs
   for every `used-by` path in the file, then
   `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root <mirror> <mirror>/souji-shokunin`:
   ```
   3-row variant : exit=0  E=0  W=30  rows=117
   5-row variant : exit=0  E=0  W=30  rows=119
   ```
   Control that the insert position matters: the same rows appended at EOF instead →
   `E12 S115 row outside Registry section`, `E12 S116 …`, `E12 S117 …` (exit 1). This is why the
   Deliverable says "inside `## Registry`".
5. **Cell-shape checks (programmatic, over the block's bytes).**
   `cols=11` for S115–S119; `teaches_words` = 24 / 22 / 20 / 22 / 20 (all ≤25); `pipe_in_cells=no`
   and `escaped_pipe=no` for every row; `status=mined`; `opened=2026-10-25`; `recheck=on-release`
   (A rows) and `180d` (B rows) — both accepted by the validator's `E09` branch (`NNd` or symbolic
   `^[A-Za-z][A-Za-z0-9 _-]*$`).
6. **Row-citation cross-check.**
   `grep -hE '^source: S[0-9]+' w1/ScribeEntryRepoSize.md w1/ScribeEntryGarbage.md` → S115, S116,
   S117, S118, S119; each resolves exactly once in the appended mirror registry
   (`resolves=1`) and each row's `used-by` cell names the entry draft that cites it.
7. **No new census findings.** W04 count is 30 before and after in both variants; no W04/E-line
   names S115–S119. `ConnSiblingSources.md` E1/E2 independently found no other lane holding any of
   the five URLs, so no `supersedes S0NN —` prefix is warranted (a supersede clause would be false).
8. Tooling: **no installs and no upgrades** this run (nothing was missing: `curl`, `git 2.56.0-1`,
   `gawk`, the three man pages were all present).

## Findings

1. **Entry-2 path conflict, frozen counter vs wave item — needs the L1, not me.** The frozen C3
   counter (`preregistration.txt` § C3) names `corpus/knowledge/count-objects-garbage-semantics-r24.md`
   as `--entries`; the wave item and `ScribeEntryGarbage.md`'s deliverable line name
   `corpus/knowledge/count-objects-garbage-readings-r25.md`. Landing only the item's name leaves the
   counter pointing at a missing file (`entry-missing`) and C3 fails with the contract unamended.
   My Block B `used-by` cells therefore name the **prereg-frozen** path; the alternate cell value is
   given in the Deliverable. I did not edit the counter. Locations:
   `preregistration.txt` § C3 counter line; `w1-spec.json` item `ScribeEntryGarbage`;
   `ScribeEntryGarbage.md` Finding 1 (same conflict, same recommendation).
2. **Landing order is load-bearing: rows cannot land before the entries exist.** `E11` tests
   `[ -e "$dir/$used-by" ]` (`scripts/sources-census.sh:562-569`), so appending the rows while the
   two entry files are still absent makes the census exit 1 with five `E11` lines. Measured: the
   5-row mirror without entry stubs → `E=5`, all mine. The rows, the entries and the census run must
   be one landing. Location: `scripts/sources-census.sh:562-569`.
3. **S119 must not repeat the ZH unit error.** `ScribeEntryGarbage.md` Finding 2 requires the
   registry `teaches` cell to avoid repeating "garbage is a size". The S119 cell reports the page's
   own gloss *and* its unit error in one clause ("glosses garbage as the files Git cannot recognise,
   with a unit error on size"), so a reader cannot lift "size" as the field's meaning. The authority
   for the count-vs-size split is S115's `teaches`. Locations: `w1/ScribeEntryGarbage.md` Finding 2;
   Block B row S119; Block A row S115.
4. **S118 cannot carry a field reading, and the row says so.** `count-objects` and `size-garbage`
   occur zero times in the qiita page; its only ASCII `garbage` is inside the quoted "light-weight
   garbage collection" sentence. The S118 scope cell states the page never glosses the field, so the
   row cannot be misread as community authority on it. Locations: Block B row S118;
   `ScoutCommunity.md` Finding 1.
5. **Scope cells name their in-lane neighbour, per `ConnSiblingSources.md`.** S115 names S035, S116
   names S063, S117 names S002; S005/S006 are historical and not re-cited. `ConnSiblingSources.md`
   E1/E2/E5 confirm none of the three git-scm pages exists as a row in souji or any other lane, so
   these are first rows and no supersede clause is used. Location: `w1/ConnSiblingSources.md` Status
   and E5.
6. **`ConnSiblingSources.md` E7 contains a misattribution (reported, not repaired).** E7 asserts
   "Souji already carries `git-worktree` (S003) *and* `…/git-worktree/2.56.0` (S230) with no warning
   between them". Souji's registry holds no S230 (`grep -c 'S230' corpus/SOURCES.md` → `0`), no
   `git-worktree/2.56.0` row (`grep -c` → `0`), and no id above S199; the fleet's only S230 rows are
   kotodama's `corpus/SOURCES.md:259` (a linguistics book) and mori's `:236` (Python reference), and
   neither is a git-worktree row. The W04/E04 conclusion E7 supports still holds on the mechanism
   alone (`scripts/sources-census.sh:641-653`), so no row here depends on the false example. Location:
   `w1/ConnSiblingSources.md` E7.
7. **`S134` (staged own-work garbage census) gets no row, by design.** Entry 2 rejects it
   (`ScribeEntryGarbage.md` Gate REJECT 1: evidence outside this repo), and my blocks stop at S119 —
   so the registry grows by exactly the five documents that are cited, and the staged `S134` figure
   never enters this lane's provenance. Location: `w1/ScribeEntryGarbage.md` Gate; this report's
   Deliverable (no S120).

## Attack log

Not an attack item; no counter, predicate, target or key set was proposed for change, and
`corpus/SOURCES.md` was not edited. One calibration observation, filed without proposing a change:
C3's frozen target is `rows 114 -> >=117`, which the three unconditional rows satisfy exactly, so
Block B's two rows are claim-neutral — they raise coverage without moving the counter past its
already-reached target. If the round wants the community half to count, the counter would have to
name `>=119`; I did not propose that, and the frozen target stands.

## Out of scope / not done

- `corpus/SOURCES.md` itself (the L1 applies the block); `census/round-23/` (does not exist yet;
  the entry Gate snapshots are the L1's to write); `tools/souji-gate-check.py` (entry-side predicate,
  executed by `ScribeEntryGarbage` in its own scratch, not re-run here).
- No fleet census: `git count-objects -v` was run once against this lane only, and no size figure
  from it is claimed by any row.
- Scratch `/var/tmp/souji-r23-ScribeSourcesRows/` removed before yield.
