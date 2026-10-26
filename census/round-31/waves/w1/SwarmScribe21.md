# SwarmScribe21 — lesson `## Gate` block for round 31

## Status

STATUS: PASS — the `## Gate` block for `corpus/lessons/round-31.md` is drafted at
`.ufo/waves/round-31/w1/deliver-lesson-gate.md`: 4 ADMIT rows (new row S222, the `config/gc.adoc`
fragment through held S063, held S051, the C3 entry as a placeholder), 18 per-entry REJECT rows over
the read-only merge package, 29 located quotes (all 4-25 words, no pipe), a `### SOURCES
touched-row log (old -> new)` skeleton for six rows, an `Assimilation:` line and a
`considerthese/ absent` line. Nothing was integrated and no lane file outside this wave dir was
written; six integration blockers are reported below.

## Evidence

Lane HEAD read-only at `1b81136` (base `9f17a1e`; `git status --porcelain` empty):
`git rev-parse HEAD` -> `1b811368461785040e955f41f9c97e62f61fd67c`; `corpus/lessons/round-31.md`,
`corpus/knowledge/jj-dropped-keep-object-lifetime.md`, `tests/fixtures/r31-jj-object-clock.sh`,
`census/round-31/records/jj-object-clock-run.txt` and `census/round-31/sources/` are absent from
`git ls-tree -r HEAD`.

Live fetches from the tags (scratch under `/fast/scratch/hyaku/souji-r31/SwarmScribe21/`, `TMPDIR`
set inside it; `curl -fsS --max-time 60` exit 0):

```
59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54  r.adoc      (git-reflog.adoc, 5657 B)
0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a  g.adoc      (config/gc.adoc, 7753 B)
0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641  c.md        (jj git-compatibility.md, 12284 B)
```

The three sha256 equal the wave's staged snapshots byte-for-byte (`sha256sum` of
`.ufo/waves/round-31/w1/sources/{git-reflog.adoc,gc.adoc,git-compatibility.md}` printed the same
three digests) and the `deliver-fetch-receipts.tsv` rows (HTTP 200, 2026-10-26T06:21:38Z).
`curl -sS -o /dev/null -w %{http_code} -L https://git-scm.com/docs/git-reflog` -> `200`.

Registry at HEAD (145 rows, max id S221): `grep -c -F` over `git show HEAD:corpus/SOURCES.md` gives
`git-reflog` 0, `reflog expire` 0, `--expire-unreachable` 0, `gc.reflogExpire` 1. Used-by cells read
from HEAD for S002, S051, S054, S063, S117, S220 and copied into the log skeleton unchanged on the
old side.

Merge package read-only: 68 `.md` files under
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/`; `grep -il reflog` returns
11 files and `grep -il unreachable` returns 14; the screened-not-listed line names the eight files in
those sets that are not table rows. `cmp` of each staged file against the lane's
`corpus/knowledge/<same name>`: 10 differ (staged revisions of admitted entries), the rest are new.

Quote check on the drafted block (regex over the delivery): 29 double-quoted spans, every one
4-25 words, none containing a pipe; every table row parses to 5 columns.

## Findings

1. **The entry's reflog URL is not bound to the S222 row.** `census/round-31/c3-counter.py:150-151`
   (L6) fails any `https://` URL in the entry's `## Gate` that is not a substring of a *cited* row's
   source cell; the entry's Gate names `https://git-scm.com/docs/git-reflog`
   (`deliver-entry-jj-dropped-keep-object-lifetime.md`, Gate line for S222) while the drafted S222
   source cell carries only
   `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc`
   (`deliver-sources-rows.md` §1). Fix at integration: add `(served as
   https://git-scm.com/docs/git-reflog)`, the pattern S220's row already uses.
2. **One quoted source has no `S`-id on the entry's `source:` lines.** The entry quotes jj
   `docs/git-compatibility.md:52-53` (step 7 and its Gate, snapshot
   `census/round-31/sources/git-compatibility.md`) but its `source:` lines name only S222, S063,
   S002, S117, S220, S054; held row S051 is that file at that tag (`corpus/SOURCES.md` at HEAD, row
   S051). My Gate admits it as "no new row (cite S051)" and carries the used-by append.
3. **The entry's four `RESULT` spans are placeholders.** `deliver-entry-jj-dropped-keep-object-lifetime.md`
   carries `[PLACEHOLDER RESULT SPANS ...]` and four `RESULT arm=<a> step=<s> ...` spans; L10
   (`census/round-31/c3-counter.py:163-165`) accepts only spans that are whole lines of the record, so
   the count stays at 0 spans-in-record until the L1 substitutes them from
   `census/round-31/records/jj-object-clock-run.txt`. Record and fixture are absent at HEAD.
4. **Snapshot paths in the entry's Gate do not exist at HEAD.** The Gate names
   `census/round-31/sources/git-reflog.adoc`, `gc.adoc`, `git-compatibility.md`, and L4 reads
   `census/round-31/sources/SHA256SUMS` plus `census/round-31/records/fetch-receipts.tsv` at `--rev`;
   the bytes currently exist only as wave deliveries
   (`.ufo/waves/round-31/w1/sources/`, digests verified above) and those two index files are staged
   as `.ufo/waves/round-31/w1/deliver-fetch-receipts.tsv`. They must be committed with the entry.
5. **Landing order matters for the lesson Gate itself.** `corpus/lessons/round-31.md` is a scanned
   pointer source (`tools/souji-landing-gate.py:958-976`, scanned sources; `corpus/lessons/round-%d.md` at :967); the drafted Gate cites
   `census/round-31/sources/*` and `census/round-31/records/jj-object-clock-run.txt`, so landing the
   lesson before those blobs reproduces the round-30 reference-drift mistake
   (`corpus/lessons/round-30.md`, Mistakes row `reference-drift`). Land samples/records first, or in
   the same commit. Absolute package paths are not pointers: the gate rejects paths starting with
   `/` (`_safe_pointer_path`, stable tool).
6. **`S222` is an id reservation, not a fact.** Max registry id at HEAD is S221; the wave rows file
   drafted S222 for git-reflog. If any other wave-1 seat appends a registry row first, the id must be
   re-pointed by document (the row's `source` cell is what binds), and the entry's `source:` line and
   the touched-row log with it.

No path under `/home/vgpnk/Projects/shokuknow` was written, and no pacman or tool install was
performed.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-lesson-gate.md` — the `## Gate` block draft (ADMIT/REJECT table,
  screened sweep, `Assimilation:`, `considerthese/ absent`, touched-row skeleton).
- `.ufo/waves/round-31/w1/SwarmScribe21.md` — this report.
