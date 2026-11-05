# S61ScoutSources — souji round 61, wave 1

Seat: scout (leaf; no subagent dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Date: 2026-11-05. Host git: `git version 2.56.0`.

## What I delivered

Everything below lives in my delivery dir only
(`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-61/w1/S61ScoutSources/`).
No production file (`tools/`, `tests/`, `census/`, `corpus/`, `SKILL.md`, `SCORECARD.md`, `LOG.md`)
was created, edited or deleted; no `git commit`/`add`/`push`/`stash`/`checkout`/`jj` was run anywhere;
only read-only git (`log`, `show`, `rev-parse`) in the lane and mutating git inside throwaway fixture
repos under my scratch.

| file | bytes | sha256 |
|---|---|---|
| `s290-git-log.html` | 375834 | `f206647fba42b627f46d29993490fbb585adedaa5d27b9ed575f50ef9002f69b` |
| `s291-git-update-index.html` | 84442 | `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8` |
| `source-metadata.tsv` | 461 | `08a7f16ac4994fce22b408dde63028906012fcd60d76f89d186f43d0410a04d0` |
| `s290-located-quote.txt` | 1365 | `b65fb1db62af804c802520aef5a09340540e78cc354c99d041068507773649da` |
| `s291-located-quote.txt` | 2075 | `7940c9442bac7b9261ee0923befb0b2f0c63dd4ae7b51956e7f56d3d072411c2` |
| `quote-check.txt` | 6045 | `0849f9b570325bee36b1eebd7beec96cd19788cb6780c945130fde2588b29b6f` |
| `s288-recheck.txt` | 2751 | `6c3d646476775b7ce7d46b05d6f0c04892afb90e0c5fbd9d69b2af280d1cbc48` |
| `sources-rows.md` | 4535 | `9c35d6c947d92dd465bd007250db1d459cf104db507ae4634be3043188ceb846` |
| `probe-evidence.txt` | 878 | `c03c8cf41355b07ae5a871c4b7f4bf1af281a531c21b93222aba48c30c2c5ce4` |
| `check_quotes.py` | 4473 | `a59d3ddf8c36896aa88997fe3c5e2580e30b8fd8b8d245a3863fc15883982609` |
| `SHA256SUMS` | 855 | — (digests of the ten files above) |

## Commands run and observed outputs

### 1. Capture (both fetches, in one batch, into scratch)

```
curl -sSL -w '%{http_code} %{size_download}\n' -o $S/s290-git-log.html          https://git-scm.com/docs/git-log
  -> 200 375834
curl -sSL -w '%{http_code} %{size_download}\n' -o $S/s291-git-update-index.html https://git-scm.com/docs/git-update-index
  -> 200 84442
```
Both HTTP 200, no error. Digests as tabled above. Page versions read out of the captures'
"Latest version" banner: `git-log last updated in 2.56.0`; `git-update-index last updated in
2.52.0` (the version list shows `2.53.0 -> 2.56.0 no changes`).

### 2. Quote extraction and verbatim verification

`check_quotes.py` strips tags (`re.sub(r'<[^>]+>','',raw)`), decodes entities
(`html.unescape`), maps U+00A0/U+2009/U+200B/U+2007 to space, collapses whitespace runs to one
space, then tests each quote with `str.find()`. The captures themselves were never modified; all
normalisation happened in memory over the scratch copies.

`python3 check_quotes.py` -> **EXIT=0**; `quote-check.txt` ends with:

```
SUMMARY: all quotes verbatim = YES
SUMMARY: all quotes <= 25 words = YES
```
9 quotes checked, every one `VERBATIM: YES` with a non-negative normalised offset.

### 3. S288 re-open of the lane's committed capture

`census/round-60/sources/s288-python-os-replace.html` is the exact filename (the dir also holds
`s110-rename2-reopen.html`, `s214-fsync2-reopen.html`, `s251-git-merge-base.html`,
`s251-located-quote.txt`, `s288-located-quote.txt`, `SHA256SUMS`).

```
sha256sum census/round-60/sources/s288-python-os-replace.html
  ece1ab71f281f72bbaaa318f6e376adeceed40466f086861eb1edfbb79f68079
git show HEAD:census/round-60/sources/s288-python-os-replace.html | sha256sum
  ece1ab71f281f72bbaaa318f6e376adeceed40466f086861eb1edfbb79f68079
```
Recorded digests found:
- `corpus/lessons/round-60.md:22` (r60 lesson `## Gate`, S288 admit bullet) — `ece1ab71…`, 791358 bytes, access date 2026-11-04. **Present.**
- `census/round-60/sources/SHA256SUMS:4` — `ece1ab71…`. **Present.**
- `corpus/SOURCES.md` S288 row — records URL, access date, `HTTP 200, 791358 bytes, capture
  census/round-60/sources/s288-python-os-replace.html` but **no sha256 cell**. The digest is
  absent from that row only.

**Drift: NONE.** Today’s on-disk digest equals the committed blob digest equals both recorded
digests; byte count 791358 unchanged. `s288-located-quote.txt` also re-hashed identically
(`86dbb07d448038ad648fc0b30710e35f5f763dbac8bdcae7ba5ea41e53fc3aa7` on disk and in
`git show HEAD:`), and that file is **not** listed in `census/round-60/sources/SHA256SUMS`
(which lists only the four `.html` captures) — first time its digest is recorded. Full detail in
`s288-recheck.txt`.

## The two located quotes

### S290 — git-log(1) `--diff-filter` (grounds the C1 add-commit resolution)

- heading: **OPTIONS -> DIFF FORMATTING** (`h2 id=_diff_formatting`); option entry
  `--diff-filter=[(A|C|D|M|R|T|U|X|B)...[*]]`
- anchor id: `Documentation/git-log.txt---diff-filterACDMRTUXB`
- quote (15 words): `Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)`
- corroborating, same anchor (16 words): `Also, these upper-case letters can be downcased to exclude. E.g. --diff-filter=ad excludes added and deleted paths.`
- corroborating, DESCRIPTION (`h2 id=_description`) (14 words): `Various other options and paths parameters can be used to further limit the result.`

### S291 — git-update-index(1) `--skip-worktree` (grounds the C2 concealed-divergence case)

- heading: **OPTIONS** (`h2 id=_options`), entry `--skip-worktree` / `--no-skip-worktree`
- anchor id: `Documentation/git-update-index.txt---skip-worktree`
- quote (22 words): `the object names recorded for the paths are not updated. Instead, these options set and unset the "skip-worktree" bit for the paths.`
- alternate, section **SKIP-WORKTREE BIT** (`h2 id=_skip_worktree_bit`) (14 words):
  `treat the file as unchanged when it is not present in the working directory`
- corroborating, same section (18 words): `Note that not all git commands will pay attention to this bit, and some only partially support it.`
- corroborating, same section (15 words): `Git commands will also avoid treating the lack of such files as an intentional deletion`
- corroborating, same section (12 words): `Although this bit looks similar to assume-unchanged bit, its goal is different.`
- **limit caveat**, section **NOTES** (`h2 id=_notes`) (21 words):
  `This does not work as expected, since Git may still check working tree files against the index when performing certain operations.`

### Named limits / rejected inferences (must travel with the rows)

1. **S290 does not say "the commit that ADDED the path".** The page documents `--diff-filter` as a
   per-commit diff filter over the letters A/C/D/M/R/T/U/X/B. It does not state that a log filtered
   with `--diff-filter=A` names the creating commit, and it does not document `--full-history`,
   `--no-renames`, or the strict-ancestor test. That composition is the r61 C1 arm’s construction
   and is established by probe, not by this page.
2. **S291 does not say a content change is hidden from `git status`.** The manual’s NOTES section
   explicitly warns the bit "does not work as expected". The concealment effect measured below is a
   round observation on git 2.56.0, not a sourced guarantee, and it is version-scoped.
3. **S291 shares its URL with the existing S271 row** (`corpus/SOURCES.md:231`, git-update-index(1),
   opened 2026-11-01, `USING --CACHEINFO` scope). S291 is a different scope on the same page, which
   the registry convention permits (cf. S036/S049/S079/S091/S099 sharing git(1)); the row text
   should say so rather than let it read as a duplicate. Observed while re-opening: the r48 record
   says the page served **84442 bytes** on 2026-11-01, and today’s S291 capture is **also 84442
   bytes** — the page is byte-count stable across the four days, though no digest was kept in r48
   (only the located-quote text file `census/round-48/sources/s271-git-update-index-located-quote.txt`,
   sha256 `af4e199d2d5aaac5cbc84e9ce86cd1275adece7df3355d66e13e8a3bbdfd60b4`), so byte-identity with
   the r48 fetch cannot be asserted. The r48 located quote
   `--cacheinfo is useful when the object is in the database but the file isn't available locally.`
   is present in today’s capture at normalised offset 12420, with the page’s typographic apostrophe
   (`isn’t`) where the r48 record transcribed a straight one — a transcription artefact of that
   record, not a change on the page.
4. **Both S290 and S291 are free registry ids** — the committed registry holds 213 rows with max id
   S289, and `grep 'S29[01]' corpus/SOURCES.md` finds nothing, so the scribe’s S290/S291 rows do
   not collide.
5. The r60 wave’s scratch numbering once used "S290 merge-base / S291 os.replace"
   (`.ufo/waves/round-60/w1/S60ScribeEntry.md:34`); that scratch numbering was superseded and never
   entered the registry, so S290/S291 are free.

## Probe evidence (`probe-evidence.txt`) — round observations, not sourced facts

Fixture repos were created with `D=$(mktemp -d -p "$S") && git -C "$D" init -q` and every later git
call named `-C "$D"`; `git -C "$D" rev-parse --show-toplevel` was asserted equal to `$D` before the
first commit, and a throwaway identity (`user.email t@t`, `user.name t`) was used only there.

**Probe A — `--diff-filter=A` resolves the add commit** (git 2.56.0): a file `c/receipt.txt`
committed three times (`A` add, `B`/`C` modify). `git log --oneline -- c/receipt.txt` lists all
three; `git log --diff-filter=A --no-renames --full-history --format='%H %s' -- c/receipt.txt`
lists **only** the add commit, and `git merge-base --is-ancestor <add> HEAD` exits 0.

**Probe B — skip-worktree conceals a worktree divergence** (git 2.56.0): tracked `inst.txt`
committed, then modified in the worktree.

```
status --porcelain BEFORE --skip-worktree: [ M inst.txt]
status --porcelain AFTER  --skip-worktree: []
git diff --name-only:                      []
git diff-index --name-only HEAD:           []
git ls-files -v inst.txt:                  [S inst.txt]
worktree blob (git hash-object):           b5dc6b85...
committed blob (git rev-parse HEAD:...):   4b48deed...
```
So the worktree bytes differ from the committed blob while `git status --porcelain` is silent —
the exact shape the C2 `concealed-divergence` case needs. The `S` flag from `git ls-files -v` marks
the skip-worktree bit.

## Registry rows

`sources-rows.md` in my delivery dir carries the two 11-column rows in the lane’s
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`
shape, with the scribe’s four `QUOTE-PLACEHOLDER-<n>` markers filled in from these captures, and
the NOTE caveat the L1 must carry into the lesson’s `## Gate`.

**L1 action required (out of my write scope):** move the two captures from my delivery dir to
`census/round-61/sources/s290-git-log.html` and `census/round-61/sources/s291-git-update-index.html`
(the scribe’s rows already cite those paths), extend `census/round-61/sources/SHA256SUMS` with both
digests, insert the two rows after the S289 row in `corpus/SOURCES.md`, and record the S290/S291
access records and located quotes in `corpus/lessons/round-61.md` `## Gate`.

## Tooling

No installs, no upgrades, no pacman transaction, no network package fetch. Everything used was
already present: `curl`, `git 2.56.0`, `python3` (stdlib `re`, `html`, `hashlib`, `subprocess`
free), `sha256sum`, `stat`. The `html.parser` module was available but a `re`-based tag strip was
sufficient and was applied only in memory over scratch copies.

## Scratch

Scratch root `/fast/scratch/hyaku/souji-r61/S61ScoutSources/` (fixture repos, the checker, the
scratch copies) was removed after the deliverables were copied into the delivery dir and
re-verified byte-for-byte. No scratch artifact remains outside the delivery dir.

## Remaining unknowns

- Whether the L1 lands the two rows as `mined`/`queued` and which knowledge file the `used-by`
  cells point at (`corpus/knowledge/control-chronology-binding.md` and
  `corpus/knowledge/skip-worktree-concealment.md` are the scribe’s drafts; neither file existed in
  the lane at my read time).
- Whether the C1 arm’s `CONTROL-ADDED-NOT-BEFORE-FREEZE` class name and the C2 case names
  `concealed-divergence` / `partial-visibility` match the executor’s frozen matrix; that is the
  L1’s and the executors’ seam, not mine.
