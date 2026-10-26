# SwarmScribe16 — r31 w1: SOURCES rows for C3

## Status

STATUS: PASS — one new registry row (S222, git `Documentation/git-reflog.adoc` at tag v2.56.0)
drafted in the exact 11-column schema, both candidate sources opened this run with ≤25-word
located quotes, `sources-census.sh validate` on a scratch copy of the registry exits 0, and the
second placeholder row (S223) is refused on held-row coverage rather than drafted.

## Evidence

Registry provenance — lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; the file I read is
byte-identical to its blob at that revision (lane HEAD is `1b811368…`, the registry itself is
unmodified by wave 1):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file blob 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc:corpus/SOURCES.md | sha256sum
2488d6314ba6f411f221a445da615a7cec8cf367d78389fad4717ed129165588  -
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain corpus/SOURCES.md
(no output)
```

Registry shape: 145 rows, max id S221, `## Registry` header at line 20, last row at line 166.
S222 is free and unclaimed.

Sources opened this run (scratch download, `TMPDIR` inside scratch):

```
$ curl -sS -o git-reflog.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc
$ curl -sS -o gc.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc
$ curl -sS -o /dev/null -w "%{http_code} %{size_download} %{url_effective}\n" <both urls>
200 5657 https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc
200 7753 https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc
$ wc -l git-reflog.adoc gc.adoc
  161 git-reflog.adoc
  181 gc.adoc
$ sha256sum git-reflog.adoc gc.adoc
59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54  git-reflog.adoc
0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a  gc.adoc
```

Quote verification (whitespace-collapsed substring search on the opened bytes; every quote
≤25 words, no pipe, no double quote — so each can sit inside a Gate span unescaped):

```
git-reflog.adoc words=23 verbatim=True pipe=False dquote=False
git-reflog.adoc words=17 verbatim=True pipe=False dquote=False
git-reflog.adoc words=14 verbatim=True pipe=False dquote=False
git-reflog.adoc words=9  verbatim=True pipe=False dquote=False
gc.adoc         words=14 verbatim=True pipe=False dquote=False
```

Registry sweep backing the adapter/novelty claim (same file, sha256 above):

```
git-reflog              0
reflog expire           0
git reflog              0
--expire-unreachable    0
```

Scratch-copy validation — mirror built from `cp -a corpus`, S222 appended after S221, the one
non-corpus used-by target (`tools/souji-size-census.py`) copied so held rows' E11 checks resolve;
`diff -u` against the lane registry shows exactly one added line:

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file /fast/scratch/hyaku/souji-r31/SwarmScribe16/lane/corpus/SOURCES.md --today 2026-10-26
file	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/fast/scratch/hyaku/souji-r31/SwarmScribe16/lane/corpus/SOURCES.md
exit=0
```

37 output lines = 36 `W04` + the `ok` line; zero lines matching `\tE[0-9]{2}\t`; no line names
S222. The same 36 warnings and exit 0 are produced by the unmodified registry in the same mirror
(warning sets `diff`-identical), so the row adds no finding of any class. The run was repeated after
the served URL was added to S222's source cell: identical 37 lines, exit 0.

L6 expression of `census/round-31/c3-counter.py:150-152` simulated over the entry draft and the
mirror (no counter run — the entry is not at a revision):

```
cited ['S002', 'S054', 'S063', 'S117', 'S220', 'S222']
missing []
gate_urls ['https://git-scm.com/docs/git-gc', 'https://git-scm.com/docs/git-reflog']
url_unbound []
```

## Findings

1. **S222 drafted and validated** — `deliver-sources-rows.md` §1. Row appended after S221
   (registry line 166): kind `docs` (validator enum `spec|docs|paper|code|tool|dataset|talk|book|community|own-work`),
   tier `A` (git's own `Documentation/` at the release tag), status `mined`, opened 2026-10-26,
   recheck `on-release`, used-by `corpus/knowledge/jj-dropped-keep-object-lifetime.md`; NF=13, no
   pipe inside any cell. Anchor cell carries the five line ranges, HTTP status, byte count and
   sha256 of the bytes opened.

2. **S223 refused on held coverage, not drafted** — location `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md:23`
   (row S002, `git-gc(1)`). S002's anchor names `§ CONFIGURATION gc.reflogExpire, gc.reflogExpireUnreachable`
   and its teaches cell states `reflog 90 days (30 if unreachable)`, i.e. both keys and both
   default ages are already held. The page was still opened to test drift: `gc.adoc:115-122`
   (gc.reflogExpire) and `:124-132` (gc.reflogExpireUnreachable) restate the same 90/30-day
   defaults, so a v2.56.0 row would re-teach S002. [INFERENCE], secondary and not decisive: the
   rendered form of `config/gc.adoc` is included in the `git-config(1)` page served at
   https://git-scm.com/docs/git-config, a URL S042 holds (S057 at another scope), so a served-URL
   row would also collide on URL.

3. **S222 is novel in the registry** — the four-string sweep above returns 0 for each; no held row
   states the `git reflog expire` subcommand contract. The scope cell says so explicitly and
   defers gc reachability to S063 and prune's own scope to S117.

4. **Validation ran against a mirror whose used-by target is a placeholder** — the C3 entry did not
   exist when the mirror was built (03:24): `corpus/knowledge/` held only `jj-colocation-receipts.md`
   and `jj-keep-ref-expiry.md`, and `.ufo/waves/round-31/w1/` held no `deliver-entry-*`. The
   one-line placeholder at `corpus/knowledge/jj-dropped-keep-object-lifetime.md` exists only in
   scratch so E11 can pass; L11 of `census/round-31/c3-counter.py` re-runs the same validator on
   the exported registry after the entry lands, which is the real gate for this row.

5. **used-by deltas now rest on observed citations** — the wave-1 entry draft landed after my first
   check: `.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md:1-6` carries six
   `source:` lines naming S222, S063, S002, S117, S220 and S054, so `deliver-sources-rows.md` §5
   lists the concrete old → new for all five held ones. The entry is still not committed to
   `corpus/knowledge/`, so the L1 should trim the list if the integrated `source:` set differs.

6. **Independent corroboration of the two snapshots** — the sibling delivery
   `.ufo/waves/round-31/w1/deliver-c3-anchor-lines.md` records the same byte counts and sha256 for
   both files (5657 / `59e7f0f1…`; 7753 / `0ab75f6f…`), fetched separately, which cross-checks the
   provenance in S222's anchor cell.

7. **No other registry cell moved** — the only diff between the copied registry and the lane
   registry is the S222 line; S002/S063/S054/S117/S220 used-by edits belong to the L1, not to this
   read-only seat.

8. **The source cell carries the served URL so the entry's Gate URLs stay bound (L6)** — the entry
   draft's Gate cites `https://git-scm.com/docs/git-reflog` for S222, while
   `census/round-31/c3-counter.py:150-152` requires every `https://` URL in the Gate to occur in the
   source cell of a cited row. S222's source cell therefore reads
   `…/Documentation/git-reflog.adoc (served as https://git-scm.com/docs/git-reflog)`, mirroring
   S220's raw/served pair; the served URL is second, so `url_of()` still keys duplicate checks on the
   raw URL and the row stays unique (no E04/W04 names S222). Local simulation of the L6 expression
   over the draft and the mirrored registry prints `gate_urls ['https://git-scm.com/docs/git-gc',
   'https://git-scm.com/docs/git-reflog']` and `url_unbound []`. This is a simulation of the
   counter's expression, not a counter run: the entry is not at a revision yet.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-sources-rows.md` (S222 row, S223 refusal with S002's cells, five
  located quotes, validation transcript, used-by deltas)
- `.ufo/waves/round-31/w1/SwarmScribe16.md` (this report)

No tooling installed (guard respected: no pacman); tools used: `curl`, `sha256sum`, `python3 -B`,
`git` read-only. Scratch `/fast/scratch/hyaku/souji-r31/SwarmScribe16/` removed after the delivery
landed.
