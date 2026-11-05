# S64ScoutSources — round 64 C1 source frontier (scout seat)

Deliverables (all under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-64/w1/S64ScoutSources/`):

```
captures/s295-git-page.html         244227  534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1
captures/s295-git-page.txt           69917  e7a0a9360b6f66c1c92f0cc9bcde1b3098b4a30ecae6465a3000c843cf51e213
captures/s295-located-quote.txt        231  07fa8baa7327d3b8ade1f92c4423e1e73433a927510651f1c2c5bce09a3ffff3
captures/s295-git-man.txt            62275  51e31eaa2e2e4cb07feb9af8c6a0d19e1e54498e2fb61005c2bf839a8146c33b
captures/s296-gitglossary.html      109997  216bc0df7f50dc17d331ea2a9873daf65a08a2afddd797f73a300cc2e15f0129
captures/s296-gitglossary.txt        35712  d8cb27328dd194ce8d63ae2fdb4621cae6c4a65107ac07193ce3ddfddd71ee6a
captures/s296-located-quote.txt        208  cba509a55a940bd6401c6f61dde1f772bfa1b53fec2d9ec6a03c6cc99987366c
captures/s296-gitglossary-man.txt   30296  10b8988bd93230e8bf295d7a06994a79ec7bd891d1e1a69690cfe75fb83a2e6d
probes/probe-log.txt                    (P1..P14, commands + outputs + exit codes)
probes/git-2.56.0-pathspec.c        23341  5f839150bbbf4806...   (pathspec_magic[] + parse_long_magic())
probes/git-2.56.0-glossary-content.adoc 33357  0635310817aac48a...
quote-check.txt                        (15660 bytes; every offset asserted mechanically)
rows/SOURCES-rows-draft.md             (the two rows + shape validation + named limits)
```

Scratch root `/fast/scratch/hyaku/souji-r64/S64ScoutSources/` holds the working copies and the
`registry-test/` scratch registry copy; it is removed on exit. Every artifact needed is copied
into the delivery directory above.

**Answering model:** `minimax-code/MiniMax-M3.1-Flash` (this seat's model, per the workstation
context in the assignment).

---

## 1. git(1) — GIT_INDEX_FILE, Environment Variables section

Fetch: `curl -sSL -o git.1.html -w 'HTTP=%{http_code} BYTES=%{size_download}' https://git-scm.com/docs/git`
→ `HTTP=200 BYTES=244227` (exit 0). sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`.

The entry lives in **§ ENVIRONMENT VARIABLES › The Git Repository** (the `<h2 id="_environment_variables">`
heading is at raw offset 180742; the `GIT_INDEX_FILE` `<dt>` carries anchor
`Documentation/git.txt-GITINDEXFILE` at raw offset 183681).

**Located quote (17 words, ≤ 25):**

> `This environment variable specifies an alternate index file. If not specified, the default of $GIT_DIR/index is used.`

**Mechanical offset proof.** The git(1) *web* page renders this entry with markup between the
words, so the sentence is **not** byte-contiguous in the raw web bytes. I cut the entry's own
HTML element out of the **same fetched bytes** (by its anchor id), stripped tags → nothing,
unescaped entities, collapsed whitespace runs, and the result is byte-contiguous:

```
s295-located-quote.txt   offset=113  line=1  contiguous=True  sha256 07fa8baa7327d3b8ade1f92c4423e1e73433a927510651f1c2c5bce09a3ffff3
PROOF: assert capture[113:230] == quote_bytes  -> PASSED
slice = b'This environment variable specifies an alternate index file. If not specified, the default of $GIT_DIR/index is used.'
```

**Independent second carrier.** The installed man page (`git 2.56.0-1`, package owner confirmed by
`pacman -Qo /usr/share/man/man1/git.1.gz` → `git 2.56.0-1`) carries the identical sentence
verbatim; rendered (`MANWIDTH=200 man 1 git`) it is **byte-contiguous**:

```
s295-git-man.txt         offset=30767  line=865  contiguous=True
PROOF: assert capture[30767:30884] == quote_bytes  -> PASSED
```

This is the M4/D1 lesson applied mechanically — the offset is not a recorded number, it is a
sliced assertion that passes.

## 2. The `:(top)` pathspec magic — which page documents it

**The literal string `:(top)` appears on NO git-scm.com page and in NO git source file.**

```
grep -rn -- ':(top)' <git v2.56.0 source tree>          -> exit 1, 0 hits (whole tree)
grep -c ':(top)' over 60 fetched git-scm.com pages       -> 0 hits on every page
```

Pages fetched for the sweep: `git`, `git-add`, `git-checkout`, `git-ls-files`, `git-status`,
`git-diff`, `git-log`, `git-grep`, `git-restore`, `git-clean`, `git-mv`, `git-rm`, `git-stash`,
`git-worktree`, `git-submodule`, `git-rev-parse`, `git-update-index`, `git-branch`, `git-cherry`,
`git-describe`, `git-show`, `git-blame`, `git-reflog`, `git-remote`, `git-fetch`, `git-push`,
`git-pull`, `git-clone`, `git-init`, `git-config`, `git-reset`, `git-revert`, `git-rebase`,
`git-merge`, `git-bisect`, `git-sparse-checkout`, `git-ls-tree`, `git-archive`,
`git-count-objects`, `git-gc`, `git-prune`, `git-repack`, `git-fsck`, `git-verify-pack`,
`git-update-ref`, `git-tag`, `git-format-patch`, `git-send-email`, `git-request-pull`,
`git-http-backend`, `git-daemon`, `git-shell`, `git-upload-pack`, `git-receive-pack`,
`git-update-server-info`, `git-difftool`, `git-mergetool`, `git-bugreport`, `git-credential*`,
`git-lfs`.

The only long-form magic literal on any of them is `:(glob)` and `:(literal)`, both in **git(1)**
§ OPTIONS `--glob-pathspecs` / `--noglob-pathspecs` (`captures/s295-git-page.html` raw offsets
104195 and 104668). **That is the page that documents the long-form spelling convention** — and it
documents it with `glob`/`literal`, not with `top`.

**The page that documents the `top` magic word is gitglossary(7) § PATHSEC** (fetched
`HTTP=200 BYTES=109997`, sha256 `216bc0df7f50dc17d331ea2a9873daf65a08a2afddd797f73a300cc2e15f0129`),
entry `top` (anchor `Documentation/gitglossary.txt-top`).

**Located quote (18 words, ≤ 25):**

> `The magic word top (magic signature: /) makes the pattern match from the root of the working tree`

**Mechanical offset proof:**

```
s296-located-quote.txt   offset=43  line=1  contiguous=True  sha256 cba509a55a940bd6401c6f61dde1f772bfa1b53fec2d9ec6a03c6cc99987366c
PROOF: assert capture[43:140] == quote_bytes  -> PASSED
slice = b'The magic word top (magic signature: /) makes the pattern match from the root of the working tree'
```

Independent second carrier: the installed man page git 2.56.0-1 renders the **full 29-word**
sentence byte-contiguously at offset 15869, line 231 (`assert capture[15869:16033] == quote_bytes`
→ PASSED). The 29-word full sentence is over the 25-word registry limit, so the row's quote cell
carries the 18-word prefix (same entry, same first-word offset); the full sentence is recorded in
`quote-check.txt`.

**Supporting secondary quote** (the long-form rule that makes `:(top)` a legal spelling) — 25 words:

> `the leading colon : is followed by an open parenthesis (, a comma-separated list of zero or more "magic words", and a close parentheses )`

offset 15510, line 225 in `captures/s296-gitglossary-man.txt`; `assert capture[15510:15647] == quote_bytes` → PASSED.

**What actually binds the spelling (a CODE fact, not a page fact).** git v2.56.0 `pathspec.c`:

```
line 106:  { PATHSPEC_FROMTOP,  '/', "top" },
line 333:  static const char *parse_long_magic(...)   — matches each long-form word against
           pathspec_magic[i].name; line 378: die("Invalid pathspec magic '%.*s' in '%s'", ...)
```

So `:(top)` parses **because** `top` is in git's magic table, and the PATHSEC page is what says
what the magic word *means*. The L1 must decide whether to add the `pathspec.c` binding as a
third row (tier A, `code`) or keep it as a named limit on S296. Copy delivered:
`probes/git-2.56.0-pathspec.c`.

## 3. GIT_INDEX_FILE probe on git 2.56.0

Fixture: `D=$(mktemp -d -p "$S") && git -C "$D" init -q`; committed `secret.txt` + `tools/counter.py`;
`git -C "$D" rev-parse --show-toplevel` printed the fixture path exactly, before the first commit.
Full transcript with exit codes: `probes/probe-log.txt`.

**The read goes to the alternate copy** (the assignment's required shape):

```
P2  cp "$D/.git/index" "$D/alt-index"                                   exit=0
P4  GIT_INDEX_FILE="$D/alt-index" git -C "$D" update-index --skip-worktree tools/counter.py   exit=0
P5  git -C "$D" ls-files -v -z          ->  H secret.txt / H tools/counter.py     exit=0   (main index unchanged)
P6  GIT_INDEX_FILE="$D/alt-index" git -C "$D" ls-files -v -z  ->  H secret.txt / S tools/counter.py   exit=0
P7  sha256sum .git/index alt-index      -> dfc8e2fb…  vs  6517bef7…   (the two index files differ)
```

**The N3 shape (flag in the REAL index, `GIT_INDEX_FILE` pointing at a flag-free copy):**

```
P8  real index                          ->  H secret.txt / S tools/counter.py
    GIT_INDEX_FILE=flagfree-index       ->  H secret.txt / H tools/counter.py     (the S is INVISIBLE)
```

This is the forgery the candidate's `RECEIPT-INDEX-ENV-SET:` refusal must catch, and it shows the
refusal must be a **refusal, not a scrub**: scrubbing `GIT_INDEX_FILE` would restore the real
index and silently change the caller's index view.

**Two more measured behaviours the page does not document:**

```
P13  GIT_INDEX_FILE=<nonexistent> git ls-files -v -z   -> 0 bytes stdout, exit 0   (a SILENT EMPTY index)
P14  GIT_INDEX_FILE=<empty file> git ls-files -v -z    -> fatal: index file smaller than expected, exit 128
```

P13 matters to the design: a caller-set `GIT_INDEX_FILE` pointing at a nonexistent path makes the
base writer's flag loop see **zero records** — the concealment check passes vacuously.

## 4. D1 re-location — the round-63 S294 quote offsets (true values, mechanically proven)

Committed capture: `census/round-63/sources/s294-git-fast-import.html`
(171432 bytes, sha256 `4830e69c…d72e9`) and `.txt` (66048 bytes, sha256 `6e7c0fb3…9ba8b`).

Recorded in `corpus/lessons/round-63.md` `## Gate`: *"offset 31053 of the tag-stripped text, raw
offset 109019"*.

**True raw byte offset of the first matched word `A gitlink`:**

```
offset = 109094   (line 3598)
PROOF : assert raw[109094:109103] == b'A gitlink'  -> PASSED
slice : b'A gitlink'
the recorded 109019 lands on: b'rget.</p>\n</li>\n<li>\n<p><span '   <- the tail of the 120000 symlink line
```

**True offset in the committed tag-stripped `.txt` (the very file the Gate cites):**

```
offset = 31190   (line 796)
PROOF : assert txt[31190:31199] == b'A gitlink'  -> PASSED
the recorded 31053 lands on: b'ant. \n 100755 or 755 : A normal, but exe'   <- the 100755 mode line
delta: 31190 - 31053 = 137
```

**The 13-word sentence is NOT byte-contiguous in EITHER capture** — a source line-wrap sits between
`commit in` and `another` (`raw[109094:109174]` = `b'A gitlink, … a commit in\nanother repository. …'`;
`find(full_quote_bytes)` = -1 in both files). So only a **whitespace-tolerant first-word offset**
is well-defined, and that is what the recorded numbers must be.

**The four tag-strip normalizations, measured on the committed `.html` (the D1 measure):**

| normalization | first-word offset | full quote contiguous |
|---|---|---|
| naive strip (tag → nothing, raw bytes kept) | 54935 | no |
| newline → space | 54935 | yes |
| collapse-newlines (` \n ` → `\n`) | 34462 | no |
| collapse-whitespace (all `\s+` → ` `) | 31600 | yes |

**None of the four reproduces 31053, and none reproduces 109019.** The recorded numbers are
unreproducible from the committed capture by any of the four normalizations.

**Provenance of the error.** The r63 seat-local capture
(`.ufo/waves/round-63/w1/S63ScoutSources/captures/s294-git-fast-import.{html,txt}`) is
**byte-identical** to the committed census capture (both sha256 `4830e69c…` / `6e7c0fb3…`). The
offsets were therefore wrong against the very bytes the seat measured — the defect is in the
measurement, not in a later re-copy.

**The correction entry the L1 must land** (append-only in `corpus/lessons/round-63.md`, naming the
text it supersedes — the lesson text is NOT to be rewritten):

> supersedes: *"offset 31053 of the tag-stripped text, raw offset 109019"*
> corrected: tag-stripped `.txt` offset **31190** (line 796); raw `.html` offset **109094**
> (line 3598), the first matched word `A gitlink`; the 13-word sentence is not byte-contiguous in
> either capture (a source line-wrap sits between `commit in` and `another`), so only a
> whitespace-tolerant first-word offset is well-defined; none of the four tag-strip normalizations
> reproduces 31053 (54935 / 54935 / 34462 / 31600) nor 109019.

**D2 (the duplicate `used-by` cell), logged old → new.** A scan of every row's `used-by` cell found
**exactly one** duplicated path:

```
awk -F'|' '...{split($12,a,","); delete seen; for(...){if(g in seen) print "DUP in row "$2": "g; seen[g]=1}}' corpus/SOURCES.md
  -> DUP in row  S294 : corpus/lessons/round-63.md
```

```
row S294
old (as committed at ae2f4ece) : corpus/lessons/round-63.md, corpus/lessons/round-63.md
new                            : corpus/lessons/round-63.md
effect                         : the repeated path is removed; the row's cited set is unchanged
note                          : corpus/lessons/round-63.md must also CITE S294 for the K1 used-by-no-cite
                                  check to pass — verified: grep -c 'S294' corpus/lessons/round-63.md -> 2
```

## 5. Registry rows drafted (S295, S296)

Full text, named limits and the shape validation are in
`rows/SOURCES-rows-draft.md`. Id state read read-only from `corpus/SOURCES.md`: 217 rows, highest
id **S294**, `S293` is a hole (drafted in r63, ruled out of integration), so the **next free id is
S295**. The row text:

```
| S295 | git(1) GIT_INDEX_FILE — https://git-scm.com/docs/git | docs | A | what a caller-set GIT_INDEX_FILE does to every index read a git process makes: it names an alternate index file instead of the repository's own, so a reader that ignores the variable reads a different index than the repository's | § ENVIRONMENT VARIABLES › The Git Repository › GIT_INDEX_FILE (anchor `Documentation/git.txt-GITINDEXFILE`); accessed 2026-11-05; HTTP 200; sha256 534c674f…f9d1; capture census/round-64/sources/s295-git-page.html; located quote census/round-64/sources/s295-located-quote.txt | `This environment variable specifies an alternate index file. If not specified, the default of $GIT_DIR/index is used.` (17 words); the page does not say a tool must refuse or scrub a caller-set value, nor how a relative value is resolved, nor that an alternate index can omit entries the real index carries | mined | 2026-11-05 | on-release | corpus/lessons/round-64.md |
| S296 | gitglossary(7) PATHSEC magic word `top` — https://git-scm.com/docs/gitglossary | docs | A | the pathspec magic word `top`, whose long form `:(top)` makes a pattern match from the root of the working tree even when the command runs from inside a subdirectory — the documented basis for observing the whole index rather than one subtree | § PATHSEC magic words, entry `top` (anchor `Documentation/gitglossary.txt-top`); accessed 2026-11-05; HTTP 200; sha256 216bc0df…f0129; capture census/round-64/sources/s296-gitglossary.html; located quote census/round-64/sources/s296-located-quote.txt | `The magic word top (magic signature: /) makes the pattern match from the root of the working tree` (18 words); the page does not print the literal `:(top)` spelling, nor say that `git ls-files` honours it, nor that the long form accepts a comma-separated magic-word list | mined | 2026-11-05 | on-release | corpus/lessons/round-64.md |
```

Both quotes: ≤ 25 words (17 and 18), located by a mechanically asserted raw byte offset, no `|`
inside any cell, page's own words.

Shape validation run **on a scratch copy of the registry** (never on the lane):

```
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {print NR": "NF}'   -> (no output)  EXIT 0
duplicate ids                                                                     -> (no output)  EXIT 0
kind/tier/status enum violations                                                 -> (no output)  EXIT 0
pipe inside any cell                                                             -> (no output)  EXIT 0
tier histogram -> A=209 B=7 C=3   (217 base rows + 2 new = 219)                     EXIT 0
```

**Integration facts the L1 must handle**

1. `corpus/lessons/round-64.md` **does not exist yet**, and both rows name it in `used-by`.
   `tools/souji-registry-agreement.py`'s K1 check requires every `used-by` path to exist at the
   measured revision **and** to name the row id. Until the L1 creates the round-64 lesson and cites
   `S295`/`S296` in it, K1 reports `used-by-missing` / `used-by-no-cite` for both new rows. Round 63
   hit exactly this; the same ordering applies.
2. `S293` stays a hole (S292 → S294 → S295 → S296). Not a new defect — the registry already has
   that shape at S292 → S294 — but the round-64 provenance paragraph should say S293 was skipped.
3. A **duplicate-url warning is expected, not a finding**: `git(1)` is already carried by S006,
   S036, S049, S125, S236, S237, S275 and `gitglossary` by S127; both new rows are under a
   **distinct scope** from every existing row on the same URL (the census reports W04 for this,
   as it did for S251/S239/S244).
4. `S127` (gitglossary) is a **rejected tier-C** row under a different scope (the common-directory
   candidate). S296 is tier A, mined, PATHSEC `top`. No conflict; the lesson should say so.

## 6. Named limits of each source

**git(1) § ENVIRONMENT VARIABLES › GIT_INDEX_FILE (S295).** The page documents only the one
sentence the row quotes. It does **not** document: that a tool should refuse or scrub a
caller-set value; how a **relative** value is resolved (absolute values only were probed); that an
alternate index can omit entries the real index carries (probe P8, a probe fact); that a
nonexistent `GIT_INDEX_FILE` yields a silent empty index (probe P13) or an empty file is fatal
(probe P14, exit 128); that the variable is inherited by child processes (ordinary POSIX
environment inheritance, not a git(1) statement); anything about `git ls-files`, porcelain status
or receipt writers. The `GIT_DIR` precedence sentence that mentions `GIT_INDEX_FILE` is a
precedence statement about a *different* variable, not a rule about the index file's own path.

**gitglossary(7) § PATHSEC magic word `top` (S296).** The page documents the magic word `top`
and the long-form syntax. It does **not** document: the **literal string `:(top)`** (verified
absent from the whole git v2.56.0 tree and from 60 fetched git-scm.com pages — the page prints
the magic word `top` and the magic signature `/`, and the long-form rule is a *separate*
sentence; composing them to `:(top)` is the reader's move); that `git ls-files` honours `:(top)`;
that `:(top)` with an empty pattern means "the whole index" (probe P11; the page's "a pathspec
with only a colon means there is no pathspec" is a different rule); the **implementation binding**
of `top` to the long form (git's `pathspec.c` `pathspec_magic[]` + `parse_long_magic()`, a code
fact — the L1 decides whether to make it a third row); that `:(top)` output paths are cwd-relative
and carry `../` prefixes from a subdirectory (probe P10).

**Other named limits of this seat's work.** Probes ran on one host (Arch linux 7.2.11-arch1-1, git
2.56.0 / package `git 2.56.0-1`); `core.fsmonitor` was not consulted and no fsmonitor daemon is
configured here. The `GIT_INDEX_FILE` probes used absolute paths only. The `:(top)` probes used a
two-file fixture; interaction with sparse checkout, submodules or worktrees was **not** probed. The
`:(top)` sweep covered the pages listed in §2 and the v2.56.0 tree, not every git-scm.com page nor
other git releases. The installed man captures are **rendered** output (`MANWIDTH=200 man …`), not
roff source, so their offsets are offsets into the rendered text. The git-scm.com pages were
fetched once each; the sha256 of the served bytes is the reproducible artifact. **The committed
round-63 `s294-git-fast-import.txt` could not be reproduced byte-for-byte from any tag-strip recipe
I tried** (16 combinations of script/style removal, comment removal, tag replacement, entity
handling, whitespace collapsing and blank-line collapsing; closest 66005 bytes vs the committed
66048), so all D1 offsets are reported against the committed bytes as committed and were verified by
slicing those bytes. No registry row was written to `corpus/SOURCES.md` and no capture was written
to `census/`; the L1 owns both. I did not test the C1 candidate writer bytes.

## 7. What this constrains for the C1 candidate (design input, not a ruling)

- The `GIT_INDEX_FILE` refusal must be an **env refusal**, not a scrub: probe P8 shows that a
  flag-free alternate index makes a skip-worktree flag invisible, and scrubbing would change the
  caller's index view (the page does not document a relative-value resolution rule, so a scrub
  cannot even be reasoned about from the source).
- Probe P13 is new information for the matrix: a caller-set `GIT_INDEX_FILE` naming a
  **nonexistent** file makes `ls-files -v -z` print **0 bytes and exit 0**, so the base writer's
  flag loop sees zero records and the concealment check passes vacuously. The N3 fixture as
  specified (a flag-free *copy*) is the stronger shape; a nonexistent-path variant is a second
  case the L1 may want to add.
- The `:(top)` scope fix must run `git ls-files` **from the real toplevel** and read the whole
  index: probe P9 shows `git -C <subdir> ls-files` sees only that subtree, probe P11 shows
  `:(top)` with an empty pattern from the toplevel lists every entry, and probe P10 shows that
  running `:(top)` **from a subdirectory** reaches the whole index but renders the paths with
  `../` prefixes — so `:(top)` alone is not a substitute for resolving the toplevel. Probe P12
  shows `:(top)**` lists everything and `:(top)/**` lists **nothing**.

## 8. L1 decisions requested

1. Append S295 and S296 as drafted, or renumber (S293 is free if the L1 prefers to close the
   hole — but S295/S296 are what the round prompt assigns).
2. Decide whether `pathspec.c`'s magic-table binding becomes a third registry row (tier A,
   `code`) or stays a named limit on S296.
3. Create `corpus/lessons/round-64.md` and cite S295/S296 in it, or the K1 check fires on both
   new rows.
4. Land the D1 correction entry and the D2 old→new `used-by` normalization as specified in §4.
5. Copy the eight capture files into `census/round-64/sources/` under the names in
   `rows/SOURCES-rows-draft.md`.

No blockers. Nothing outside my delivery directory and my scratch root was written.
