# deliver-docs-review — SwarmReviewer22 (r31 w2)

Scope: C3 documentation edits, `git diff 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc 2c16d018e40db7c23420a2c3bb546b52957bcc25 -- corpus/README.md PROVINCE.md SKILL.md corpus/SOURCES.md`. All four files are touched only by the C3 landing commit `1baf4da02b71b012ee2426ea7c309496c0c3aca0`, so the diff is the tip state. Full report: `.ufo/waves/round-31/w2/SwarmReviewer22.md`.

## Verdicts per assigned check

| Check | Verdict | Evidence |
|---|---|---|
| README: F1 map row is the only in-place change, rest append-only | PASS | 2 hunks (`:39` row, `:642-700` append); row cell-diff: entries cell only, status cell byte-identical; r12 creation (`d7266c5`) and r28/r29/r30 in-place map-row history (`765fe8b`/`1dc6785`/`76c94eb`) verified |
| PROVINCE boundary note claims nothing beyond the entry | PASS | Note `:213-236`; `:60` Core line, `:208` r30 gap quote verbatim, five prior entries, holders = record arms, `1baf4da` touches no `tools/` path |
| SKILL keep-ref bullet: packed-ref caveat + `6 to 2` per r30 record and wave-2 corrections | PASS | Record `jj-keep-expiry-run.txt:4-5` (`keep_refs=6` → `keep_refs=2`, `target_keep=no`); corrections `jj-keep-ref-expiry.md:127`; packedness mechanism `git_backend.rs:939-945` (capture hash re-fetched byte-identical) |
| SKILL error-pattern bullet matches the record | PASS | Every holder claim is a record RESULT line; citations S054/S222/S063 match the entry's claims 2-4; fixture header and `:50` `reflog_hits` definition verified |
| S222 schema + five used-by appends match the entry's `source:` lines | PASS | S222 `:167`: 11 columns, no pipe in any cell, opened 2026-10-26, mined, on-release, used-by the entry; anchor verified against snapshot AND live re-fetch (sha256 `59e7f0f1…`, 161 lines, 5657 B); five appends used-by-cell-only, set = entry's six `source:` lines = counter L6 `cited` |
| `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | PASS | rc=0, "ok", 33 pre-existing W04 duplicate-URL warnings only |

## Independent re-derivations (attacks)

- Live re-fetch of all five cited source bytes + `Documentation/git-gc.adoc`: every sha256 byte-identical to the entry's/S222's claims (`59e7f0f1…`, `0ab75f6f…`, `0fb71f99…`, `95147270…`, `9c4d6a37…`). No fabricated snapshot.
- Fixture `tests/fixtures/r31-jj-object-clock.sh` re-run in seat scratch (`TMPDIR=/fast/scratch/hyaku/souji-r31/w2-DocsReview/tmp`): rc=0, 17 RESULT lines byte-identical to `census/round-31/records/jj-object-clock-run.txt` (sha256 `085b87c7…` matches the entry). "deterministic across runs" independently confirmed; agrees with landing receipts L9 (`replays=[(0, 17, True), (0, 17, True)]`) and L12 (`results_equal=True`).
- All 9 entry Gate quotes + all `git_backend.rs`/`gc.rs`/`git-gc.adoc` line anchors verified accurate.

## Findings for the L1 (none touches a frozen target or a counter)

1. [low / coverage] `corpus/README.md:657` — "a third `jj util gc --expire=now`" is an off-by-one: the op-abandon step's util gc is the arm's second (fixture `assigned_steps`; solo total 2; descendant's third is where B goes).
2. [low / coverage] `SKILL.md:116` + `PROVINCE.md:225-228` — the receipt-grade recipes name two of the entry's three required conditions; the entry (`jj-dropped-keep-object-lifetime.md:148-149`) also requires the keep-ref state ("cannot name all three — the prune date, the reflog state and the keep-ref state — has not"). Absence check self-protects, but the recipe under-specifies the entry's auditability demand.
3. [low / coverage] Entry claims 1/3/4/5/6 cite `git-gc.adoc` main-document line ranges (`:16-20`, `:81-87`, `:141-146`, `:144-146`, `:148-151`, `:160-161`) whose bytes are unsnapshotted, absent from `census/round-31/records/fetch-receipts.tsv`, and not in the verified-at disclosure ("three snapshots and the jj source"); S063's row anchor still records only the web manual "§ NOTES first paragraph". Anchors verified accurate live — content real, disclosure missing.
4. [low / coverage] Entry claim 7's `cli/src/commands/util/gc.rs` opening (disclosed inline, sha256 verified live) has "no registry row yet" — no row, no fetch receipt, no Gate quote; the frozen preregistration's frontier step says "curate SOURCES.md rows opened this round".
5. [nit / coverage] Entry role 1 (`:95`) "reads the same except for the ref count" — the two record lines are identical in every field; only the step name differs.
6. [nit / coverage] README's "`jj-version: jj 0.45.1`" truncates the record's version line (`jj 0.45.1-7c41cdeb…`).
7. [reminder / coverage] `census/round-31/records/census-end.txt` (named by the frozen preregistration's frontier step beside `census-start.txt`) is absent at tip — presumably a round-close artifact; flagged so it is not forgotten.
