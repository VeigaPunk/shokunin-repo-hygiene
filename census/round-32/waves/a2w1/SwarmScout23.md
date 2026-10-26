# SwarmScout23 — C3 entry / S223 source re-open (a2w1)

## Status
STATUS: PASS — all 3 live sources re-fetched (HTTP 200) and byte-identical to SHA256SUMS and to the committed snapshots; 23 of 23 Gate quotes found verbatim at the stated lines; S223 row cells agree with the bytes except one paraphrase (finding 1). Registry-cell and traceability gaps are listed as findings (2-6); none is a quote mismatch. Lane tip at read: 4e56c48b8fc828f9aba2746e324dc46aa538bdbf; landing commit read: a92e1aae91dbf46c2d7eff713932cfc820186970.

## Evidence
Live fetch (curl, TMPDIR scratch under /fast/scratch/hyaku/souji-r32/SwarmScout23, since removed), 2026-10-26:
| URL (…/git/v2.56.0/Documentation/) | HTTP | bytes | sha256 | = SHA256SUMS at a92e1aa | = committed snapshot |
|---|---|---|---|---|---|
| gitformat-pack.adoc | 200 | 27494 | ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b | yes | yes |
| git-gc.adoc | 200 | 6744 | e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c | yes | yes |
| config/gc.adoc | 200 | 7753 | 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a | yes | yes |
(git-repack.adoc, 4th SHA256SUMS line, not fetched live; committed snapshot hash 474d4147… = SHA256SUMS line.) Line counts of live files: 704 / 187 / 181 (wc -l); S223 cell says 704 — ok; S063 cell says 181 lines, 7753 B — ok.

Method: python3 -B script over `git show a92e1aa:corpus/knowledge/jj-abandoned-object-mtime-clock.md` lines 193-226; for each `- S### … lines a-b — "quote" — url — snapshot: …` bullet it whitespace-collapsed the live file's lines a..b and tested containment (FOUND = quote occurs in whole file; LINE-OK = occurs inside the stated range), also searched the minimal line window; word count 4..25 and pipe absence also checked.

Per-quote result (all FOUND, all LINE-OK, all 4-25 words, none with a pipe; actual minimal window = stated range in every case):
| # | id | file | stated lines | words | result |
|---|---|---|---|---|---|
| 1 | S223 | gitformat-pack | 613-614 | 15 | found / line-ok |
| 2 | S223 | gitformat-pack | 631-632 | 20 | found / line-ok |
| 3 | S223 | gitformat-pack | 635-636 | 16 | found / line-ok |
| 4 | S223 | gitformat-pack | 638-640 | 19 | found / line-ok |
| 5 | S223 | gitformat-pack | 655-656 | 19 | found / line-ok |
| 6 | S223 | gitformat-pack | 667-668 | 20 | found / line-ok |
| 7 | S223 | gitformat-pack | 674-675 | 14 | found / line-ok |
| 8 | S223 | gitformat-pack | 682-683 | 17 | found / line-ok |
| 9 | S223 | gitformat-pack | 684-685 | 10 | found / line-ok |
| 10 | S223 | gitformat-pack | 688-689 | 12 | found / line-ok |
| 11 | S223 | gitformat-pack | 351-353 | 20 | found / line-ok |
| 12 | S223 | gitformat-pack | 353-354 | 6 | found / line-ok |
| 13 | S063 | git-gc | 63-64 | 18 | found / line-ok |
| 14 | S063 | git-gc | 64-65 | 5 | found / line-ok |
| 15 | S063 | git-gc | 82-83 | 17 | found / line-ok |
| 16 | S063 | git-gc | 84 | 8 | found / line-ok |
| 17 | S063 | git-gc | 90 | 6 | found / line-ok |
| 18 | S063 | git-gc | 160-161 | 18 | found / line-ok |
| 19 | S002 | config/gc | 86-88 | 18 | found / line-ok |
| 20 | S002 | config/gc | 97 | 11 | found / line-ok |
| 21 | S002 | config/gc | 98-99 | 13 | found / line-ok |
| 22 | S002 | config/gc | 100-102 | 14 | found / line-ok |
| 23 | S002 | config/gc | 102 | 6 | found / line-ok (also occurs at :113, gc.worktreePruneExpire; the cited :102 is the gc.pruneExpire sentence) |
Section labels spot-checked against headings: `== cruft packs` :611, `=== Cruft packs` :653, `== pack-*.mtimes files have the format:` :341; git-gc.adoc `--cruft` :61, `--prune` :81, `--no-prune` :89, NOTES :138; gc.adoc `gc.cruftPacks` :85, `gc.pruneExpire` :96 — all match the bullets' § labels.
Also checked (outside the 23): r31-entry correction quote gc.adoc 144-145 `Interpret their output as object IDs which Git will consider as "recent", regardless of their age.` — found, lines 144-145 ok; "By treating their mtimes as "now"" 145-146 ok; "whether or not to remove an object" 141-143 ok.

S223 row (`git show a92e1aa:corpus/SOURCES.md | grep S223`, SOURCES.md:168), cell vs bytes: URL/tag ok; HTTP 200, 27494 B, sha256 ok; `:341-358` mtimes table (table is 341-358 ok, ith-value lines 351-353 ok); `:611-616`, `:629-642`, `:653-675`, `:682-689` ok; row quote "A cruft pack eliminates … per-object mtimes" (:655-656) ok (19 words); "only objects within the grace period become traversal tips" matches :667-668 step 1; S004 is git-repack(1) (`--cruft-expiration` carve-out ok).

Cell-level diff base 85b61a1 -> a92e1aa of corpus/SOURCES.md (python split on ` | `): S002 changed only cell 10 (used-by) +`corpus/knowledge/jj-abandoned-object-mtime-clock.md`; S051 changed only cell 10 (used-by) +`corpus/knowledge/jj-dropped-keep-object-lifetime.md`; S063 changed cell 5 (anchor) and cell 10 (used-by) +`…jj-abandoned-object-mtime-clock.md`; S223 added as new line 168. No other row changed.

## Findings
1. S223 cell `:12-14 SYNOPSIS pack-*.{pack,idx,rev,mtimes}` is a paraphrase: bytes at 12-14 are three separate lines `pack-*.{pack,idx}`, `pack-*.rev`, `pack-*.mtimes` (gitformat-pack.adoc:12-14). Lines right; the brace string does not occur in the file. Low.
2. Stale text: entry `source: S223 … (placeholder id: the L1 renumbers by document)` (entry line 1) and the Gate intro `The gitformat-pack row is a placeholder id for the L1 to renumber` (entry ~line 198) — S223 is the landed id (SOURCES.md:168); the statement is no longer true. The r31 entry got an append-only supersession for the same phrase; the r32 entry has none yet.
3. S002 quotes 19-23 are bytes of Documentation/config/gc.adoc at v2.56.0, but S002's registry cell still reads `git 2.55.0 … installed man page git 2.55.0-1`; its §-cell lists `gc.reflogExpire…gc.worktreePruneExpire`, not `gc.cruftPacks` or `gc.pruneExpire` and not config/gc.adoc. Only S002's used-by changed. The 2.56.0 provenance of S002-attributed quotes is carried only by the entry's own `source: S002` line, not the row. Same for S063 quotes 13-17 (`§ OPTIONS --cruft/--prune/--no-prune` of git-gc.adoc): S063's cell anchors only `§ NOTES first paragraph` and the config/gc.adoc lines 96-147; quote 18 (NOTES :160-161) is inside NOTES but is the numbered list, not the first paragraph.
4. S063 cell `config/gc.adoc lines 96-147` names pruneExpire, reflogExpire, reflogExpireUnreachable, but 96-147 also spans gc.worktreePruneExpire (107-113) and gc.recentObjectsHook (140-153, cut at 147). It excludes `gc.cruftPacks` (85-88), which quote 19 cites under S002. Range is a superset, not wrong; it is the r31 correction's own text (`gc.recentObjectsHook (gc.adoc:140-147)`).
5. Old->new logging: no round-32 lesson exists at a92e1aa or at tip 4e56c48 (`git ls-tree master corpus/lessons | grep round-32` empty), so the S002/S063 used-by old->new additions and the S223 append are not yet logged anywhere I could read (grep `used-by|old → new|S223` over census/round-32, corpus/README.md, PROVINCE.md, SKILL.md at a92e1aa: no hits). What IS logged at a92e1aa, in `corpus/knowledge/jj-dropped-keep-object-lifetime.md` `## Round 32 corrections`: S051 used-by now names that entry (prose, no old string); S063 new anchor cell text (full new text, old text only as the superseded clause `scopes the page to § NOTES first paragraph`). The r31 convention (corpus/lessons/round-31.md:56) is a `| S063 | used-by | old | new | reason |` table row — L1 must write that for S002, S051, S063 (used-by) and S063 (anchor cell), plus S223 new row. Pending, not a mismatch.
6. The entry's `source: S002` / `S063` lines give URL `https://git-scm.com/docs/git-gc` while the bytes quoted are the raw adoc at the v2.56.0 tag (config/gc.adoc is a fragment included by git-gc.adoc:136 per the entry); the Gate bullets pair that URL with the snapshot path, so a reader re-fetching the URL gets rendered HTML, not the snapshot lines. The `recheck:` command does fetch the raw tag files and expect the three hashes — good.
No quote mismatch, no wrong line range, no missing source found.

## Deliveries
None (report only). Scratch /fast/scratch/hyaku/souji-r32/SwarmScout23 removed. No installs; tools used: curl, sha256sum, python3 -B, git read-only.
