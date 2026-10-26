# SwarmScout19 — C3 source re-open (hash, status, bytes, quote verbatim)

## Status
STATUS: PARTIAL — all 3 sources re-fetched live byte-identical to the committed snapshots and receipts (HTTP 200, bytes, sha256 equal); 8 of 9 Gate quotes and all 5 inline body quotes + 6 RESULT spans are verbatim at (or inside) their stated lines; 1 Gate quote has a wrong line anchor and wrong section label, 1 body claim overstates its source, and several line-numbered git-gc.adoc quotes sit outside the Gate/snapshot set.

## Evidence
Lane tip read: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` = 2c16d018e40db7c23420a2c3bb546b52957bcc25. Fetch time 2026-10-26 07:28:23 GMT (curl, raw.githubusercontent.com, `-sS`, no redirect).

| URL (tag) | HTTP | bytes live | sha256 live | = SHA256SUMS | = fetch-receipts.tsv (200, 5657/7753/12284) | = git blob at tip |
|---|---|---|---|---|---|---|
| git v2.56.0 Documentation/git-reflog.adoc | 200 | 5657 | 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54 | yes | yes | yes |
| git v2.56.0 Documentation/config/gc.adoc | 200 | 7753 | 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a | yes | yes | yes |
| jj v0.45.1 docs/git-compatibility.md | 200 | 12284 | 0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641 | yes | yes | yes |

`cd census/round-31/sources && sha256sum -c SHA256SUMS` -> three `OK`. Worktree entry file sha256 equals the tip blob (2dfba384…1087100). The committed receipt `fetched_at` is 2026-10-26T06:21:38Z (all three rows); tag content is immutable so a later re-fetch matching proves the receipts honest on these three, not that the L1's own fetch happened (A1 disclosure stands).

Also re-fetched (not asked, needed for the body quotes): git v2.56.0 Documentation/git-gc.adoc (200, 6744 B, sha e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c, `cmp` identical to census/round-30/sources/git-gc.adoc); jj v0.45.1 lib/src/git_backend.rs (200, 102068 B, sha 95147270…c86c69 = round-30 capture = S054 row); cli/src/commands/util/gc.rs (200, 2235 B, sha 9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b = entry step 7); cli/tests/cli-reference@.md.snap (200, sha b3306943…333554, `cmp` identical to round-30 capture). Rendered https://git-scm.com/docs/git-reflog (200) carries the same text for 5 of 5 reflog quotes (page footer "last updated in 2.51.1").

### Gate quotes (entry `## Gate`, lines 210-218), script-checked against snapshot bytes with whitespace collapsed
| # | file | stated | tight range | words | pipe | verbatim |
|---|---|---|---|---|---|---|
| 1 | git-reflog.adoc | 66-68 | 66-68 | 23 | no | yes |
| 2 | git-reflog.adoc | 115-116 | 115-116 | 6 | no | yes |
| 3 | git-reflog.adoc | 119-121 | 120-121 | 11 | no | yes (stated range wider) |
| 4 | git-reflog.adoc | 113-115 | 114-115 | 10 | no | yes (wider) |
| 5 | git-reflog.adoc | 122-124 | 122-124 | 10 | no | yes |
| 6 | gc.adoc | 115-119 | 117-118 | 11 | no | yes (wider) |
| 7 | gc.adoc | 124-128 | 127-128 | 14 | no | yes (wider) |
| 8 | gc.adoc | 96-97 | 97 | 11 | no | yes |
| 9 | git-compatibility.md | 52 | 52-53 | 16 | no | **text verbatim, line anchor wrong: quote spans 52-53, not "line 52"** |

S222 row (SOURCES.md:167): `161 lines` = `wc -l` 161; `:19` is the `git reflog expire` SYNOPSIS line; `:66-70` DESCRIPTION, `:111-117` --expire, `:119-127` --expire-unreachable all match the printed lines; 5657 B / sha / HTTP 200 match; the paraphrase cell (`all`/`never` sentinels, 90/30 defaults) matches lines 111-127. Row id S222 appears once; S221 precedes it.

Body (lines 13-137) double-quoted spans, all 5 found verbatim: "and anything else in the refs/* namespace" (git-gc.adoc:146); "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other" (git_backend.rs:900); "may reference commits in branches that were later amended or rewound" (git-gc.adoc:145-146); "along with everything reachable from it" (git-gc.adoc:160-161); "It should be safe to run `git gc` in the Git repo" (git-compatibility.md:52-53, inside the cited 52-54). Unquoted cites checked: git-gc.adoc:16-20 and :81-87 and :141-151 exact; gc.adoc:96-105, :115-132, :140-147 exact; git_backend.rs:970-987 has `.arg("--git-dir=.")` and `format!("--prune=@{} +0000", ...)`; util/gc.rs:44-66 is `cmd_util_gc`; cli-reference snap :3793 and :3799-3805 exact. The six `RESULT ` spans in Roles 1-4 are whole lines of census/round-31/records/jj-object-clock-run.txt (sha 085b87c7…207e5, 17 `RESULT ` lines) — all 6 `True`.

## Findings
1. **Wrong line anchor and wrong section label on the jj Gate quote** (entry line 218). It says "§ Git-specific behaviours, section Garbage collection line 52". Bytes: no heading "Git-specific" exists (`grep -n -i 'Git-specific'` = no match); the bullet `* **Garbage collection: Yes.**` sits under `## Supported features` (git-compatibility.md:11); the quoted sentence wraps lines 52-53 ("…in the Git" / "repo, but it's not tested,"). A reader following the stated "line 52" cannot find the full quote on one line. Harms: calibration (a verified-looking quote with a bad anchor), coverage only marginally.
2. **Body step 2 overstates its source** (entry lines 29-30): "a keep ref survives only when `new_heads.contains(&id)` (git_backend.rs:925)". Bytes at :925: `if new_heads.contains(&id) && name_good {`, and :939-945 keep any non-head ref whose loose-ref mtime is newer than `keep_newer` (`if mtime > keep_newer { ... continue; }`). So "only when" is false (name_good condition and the mtime gate; the entry's own S054 registry cell cites 939-945). Also the function runs only inside gc (S054 row `:1558-1564`), which the step does not say. Harms: calibration; mechanism text feeding F1 receipt rules.
3. **Line-numbered git-gc.adoc quotes are outside the Gate and the cited snapshot set.** Body steps 1, 3, 4, 5, 6 cite git-gc.adoc:16-20, :81-87, :141-151, :160-161 (and quote three spans) but `## Gate` only holds config-fragment quotes from gc.adoc plus three snapshots; git-gc.adoc is not in census/round-31/sources/ and S063's cell has no raw-file line anchors ("web manual … opened 2026-10-20; § NOTES first paragraph"). The numbers are right — I re-fetched v2.56.0 git-gc.adoc and it is byte-identical to census/round-30/sources/git-gc.adoc — but the entry does not name that capture, so the stated lines are not checkable from the entry alone. Harms: calibration/operability of the Gate contract ("the three snapshots named below").
4. **Gate quote source ids incomplete:** the jj compat quote (Gate line 218) carries no `[S051]`; the registry row for that file exists (S051, SOURCES.md:72) — traceability gap only.
5. **Stale draft text** at entry line 1: `(placeholder id: the L1 renumbers by document)` remains though the row is landed as S222. Harms: calibration (minor).
6. **Wide ranges are not mismatches** (Gate #3, #4, #6, #7 state ranges that contain the quote plus 1-2 neighbouring lines). Reported for completeness; not counted as defects.
7. **Receipts scope:** fetch-receipts.tsv has only the 3 snapshot rows; the entry's other "opened this run" bytes (gc.rs sha 9c4d…, git_backend.rs sha) have no receipt row in the lane — I found both hashes correct live, so the claims hold, but they are attested only in prose.

No finding contradicts the three snapshot hashes, statuses, byte counts, the S222 row's line ranges, or the 5 body quotes; no Gate quote exceeds 25 words (max 23) or contains a pipe.

## Attack log
- Re-fetch 3 snapshot URLs live, headers, bytes, sha: all equal (committed + receipts + git blob).
- `sha256sum -c` on committed SHA256SUMS: OK x3.
- Script check (whitespace-collapsed substring, searched tight line range, word count, pipe) over all 9 Gate quotes: 8 clean, #9 anchor wrong.
- Script check over all double-quoted body spans vs 7 sources: 5/5 verbatim.
- Opened git-gc.adoc, git_backend.rs, util/gc.rs, cli-reference snap live; compared to round-30 captures: identical.
- Read git_backend.rs:896-988 whole: found finding 2.
- Rendered page git-scm.com/docs/git-reflog vs quotes: 5/5 present.
- RESULT spans vs record: 6/6; record sha equals the entry's.
- S222 uniqueness and adjacency: 1 row, after S221.
- Not attempted: the fixture, counters c3-counter*.py (other seats), Observed-section semantics.

## Deliveries
- This report only. Scratch dir /fast/scratch/hyaku/souji-r31/w2-SwarmScout19/ removed after writing. Tooling installed: none.
