# SwarmScribe26 — LessonGate (r32 w1): draft of the `## Gate` block

## Status

STATUS: PARTIAL — the `## Gate` draft (24 rows: 3 source ADMIT, 1 entry placeholder, 20 per-entry REJECT), the
`### SOURCES touched-row log (old -> new)` skeleton, the `Assimilation:` and `considerthese/` lines and the M1
`## Mistakes` row are delivered, and every source quote was re-fetched from its tag and verified byte-present this
run. The entry ADMIT row and its numbers stay placeholders by construction: at read time the C3 entry, its record
and its fixture had not landed, and `.ufo/waves/round-32/w1/deliver-sources-rows.md` did not exist, so `S223`/`S224`
remain provisional ids.

## Evidence

All lane commands are read-only; scratch under `/fast/scratch/hyaku/souji-r32/SwarmScribe26/` (removed at finish),
`TMPDIR` set there. No write touched `/home/vgpnk/Projects/shokuknow` (read-only `grep`/`awk`/`sed` only).

Frozen inputs read first, at lane tip `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3
7a6667c round-32: controls, amendment A0 (C1 v2: cited evidence, count adjacency) with its controls
3ec84fc round-32: preregistration, frozen counters C1-C3, enumerations, C3 contract, M1 record-contract tool and red-before, start census
85b61a1 round-31 verifier spot-check (integrator, hyaku): non-author admit/reject
```

Source fetch (mine, this run; digests compared with the wave copies and the earlier round snapshots):

```
curl -sS -o gitformat-pack.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc  -> http=200 bytes=27494
curl -sS -o git-gc.adoc         https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc          -> http=200 bytes=6744
curl -sS -o gc-config.adoc      https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc      -> http=200 bytes=7753
ec285ba4…381b  gitformat-pack.adoc      (704 lines)
e3dbc408…ba8c  git-gc.adoc              (187 lines)
0ab75f6f…2f1a  gc-config.adoc           (181 lines)
```

Byte identity: `sha256sum .ufo/waves/round-32/w1/sources/*.adoc` gives `ec285ba4…`, `e3dbc408…`, `0ab75f6f…`,
`474d4147…` — equal to my fetch for the first three; `census/round-31/sources/gc.adoc` and
`census/round-30/sources/git-gc.adoc` carry `0ab75f6f…` and `e3dbc408…` too, so both documents are reproducible
across rounds. Receipt rows: `.ufo/waves/round-32/w1/deliver-fetch-receipts.tsv` (four rows, http 200,
fetched_at 2026-10-26T08:28:0xZ, bytes/sha256 matching).

Quote checks: each of the 10 source quotes and the 20 staged-entry quotes was tested for presence after whitespace
reflow in the named bytes, for a minimal line span, for word count (all 4-25) and for the absence of a literal pipe.
Example (all 30 passed):

```
gitformat-pack.adoc span=659-659    words=14 pipe=False
gitformat-pack.adoc span=674-675    words=14 pipe=False
gitformat-pack.adoc span=351-353    words=20 pipe=False
git-gc.adoc         span=63-64      words=18 pipe=False
gc-config.adoc      span=97-99      words=24 pipe=False
git-grace-period-at-release-r35.md  span=30-31 words=10 pipe=False
repo-size-census-readonly.md        span=44-45 words=14 pipe=False
```

Registry at the preregistration commit `3ec84fc` (`git show 3ec84fc:corpus/SOURCES.md`):
`grep -c '^| S'` -> `146`; max id `S222`; `grep -ci gitformat-pack` -> `0`; `grep -ci mtimes` -> `0`;
`grep -ci cruft` -> `2` (S004's teaches cell, S122's anchor cell); `grep -c 'raw.githubusercontent.com/git/git/v2.56.0/Documentation'`
-> `1` (S222, the git-reflog row). `ground: F1` at base:
`git grep -l '^ground: F1' 3ec84fc -- corpus/knowledge` -> 4 files (the two `git-auto-maintenance-trigger-set*`,
`jj-dropped-keep-object-lifetime`, `jj-keep-ref-expiry`).

Staged-package sweeps (`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge`, 68 files):
`cruft` 0; `mtime|modification time` 6; `pruneExpire` 13; union 19; `unreachable` 14; `loose object(s)` 3.

M1 evidence read (not re-executed this run): `census/round-32/records/m1-red-before.txt` holds
`BAD 16..19 arm=reflog-only outside descendant|solo`, `lines=17 bad=4`, `exit=1`; the r31 record
`census/round-31/records/jj-object-clock-run.txt` has 19 lines, 17 `RESULT`, four of them `arm=reflog-only`
(lines 16-19); `census/round-31/records/preregistration.txt:20` carries the literal
`arm=<solo|descendant> step=<name> keep_refs=<n> target_keep=<yes|no> reflog_hits=<n> object_present=<yes|no>`.

`ls considerthese` -> `No such file or directory` (2026-10-26).

## Findings

1. **The two-row plan leaves two raw doc URLs without a carrier under C3 L6.** L6 requires every https URL printed in
   the entry's `## Gate` to appear in the source cell of a *cited* row (`census/round-32/c3-counter.py:24-25`,
   implementation `:232`: `cellurls = " ".join(rows[i][2] for i in cited …)`). The wave-1 anchors quote
   `config/gc.adoc:97-99` and `git-repack.adoc:76-77` (`.ufo/waves/round-32/w1/deliver-c3-anchor-lines.md`), but no
   held row's source cell carries either raw URL — `S002`/`S063` are `https://git-scm.com/docs/git-gc` and `S004` is
   `https://git-scm.com/docs/git-repack` — and the row draft enumerates only `S223` (gitformat-pack) and `S224`
   (git-gc). My Gate therefore admits the `config/gc.adoc` fragment conditionally: own row if the entry's Gate prints
   the URL, otherwise the quote moves to the body and `S063` keeps only the reachability rule. The same applies to
   `git-repack.adoc`, noted in the `S224` flip.

2. **The base registry is not cruft-free in prose.** `corpus/SOURCES.md:25` at `3ec84fc` (S004) teaches
   `--cruft -d --expire-to` and its anchor cell names `Documentation/git-repack.adoc at tag v2.56.0`, while its source
   cell is the git-scm page. The new `S223` is still a distinct row (0 rows on `gitformat-pack`, 0 on `.mtimes`,
   and S004 states no per-object clock), but a reader can mistake S004 for the cruft ground; the Gate's `S223` row
   says so in its reason cell.

3. **No staged entry can ground the object clock or the cruft arm.** 68 files, `cruft` 0, `mtimes` 0,
   `gc.cruftPacks` 0; the 19 files hit by `mtime|pruneExpire` are worktree-registration, fleet-config or vendor
   material, and the 20th row (`repo-size-census-readonly.md`) states the loose/packed expiry split but is an older
   revision of an admitted entry (`cmp` against `corpus/knowledge/repo-size-census-readonly.md` -> exit 1).
   Locations: each row of the Gate table carries its own file:line.

4. **The staged package cannot be appended as-is.** 38 of its 134 ids collide with the lane's S001-S222
   (S109-S132, S152, S210-S222) and 10 of its 68 paths already exist in `corpus/knowledge/` with different bytes
   — `.ufo/waves/round-32/w1/deliver-assim-sweep.md` §§ 2, 5 (peer seat's sweep; I independently reproduced the
   `repo-size-census-readonly.md` path-collision `cmp` result). My Gate records assimilation as none.

5. **Ids are provisional.** `.ufo/waves/round-32/w1/deliver-sources-rows.md` was absent when read (wave still
   running), so `S223`/`S224` follow the item's placeholder order; the Gate's opening paragraph tells the L1 to
   re-point at landing, and the touched-row log names no new id as a touched row.

6. **The M1 row's "shown able to fail" evidence is a committed receipt, not a rerun.** `lines=17 bad=4`, `exit=1`
   is read from `census/round-32/records/m1-red-before.txt`; I did not execute `tools/souji-record-contract.py`
   this run, and the row attributes the count to that file, not to this seat. The r31 contract literal at
   `census/round-31/records/preregistration.txt:20` was opened and quoted inside the row.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-lesson-gate.md` — the `## Gate` block (24 rows), `Screened and not listed`
  paragraph, `Assimilation:` line, `considerthese/` line, `### SOURCES touched-row log (old -> new)` skeleton and
  the `## Mistakes` M1 row.
