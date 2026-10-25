# ScoutSourcesOpen — round 25 w1 (S124 / S125 open)

Seat: ScoutSourcesOpen (leaf, no dispatch). Lane base read: HEAD 6e4737eab43d8fde1b85eb9f57023d29046705b4.
Wrote nothing in the lane except this report. No SOURCES rows appended.
Host: git 2.56.0-1 (`pacman -Q git`). Tool installs/updates: none.

## Verdict

- **S124 gitrepository-layout(5) § commondir — ACCEPT.** Opened live twice (HTTP 200), byte-identical; the installed 2.56.0 man page and the v2.56.0 tag source agree word-for-word.
- **S125 gitglossary(7) "common directory" — REJECT.** The entry does not exist. There are 0 case-insensitive matches for `common` in the live page, the installed roff, the rendered man text, and `Documentation/glossary-content.adoc` at tag v2.56.0. ScoutSourcedClaimCheck found the same thing independently.
- **Replacement candidate for S125: git-rev-parse(1) `--git-common-dir` + `--path-format`. ACCEPT-ready.** It grounds the exact call the probe makes (`tools/souji-repo-structure.sh:193`: `rev-parse --path-format=absolute --git-common-dir`), which is what C3's `SOUJI-R13-STRUCT-linked-common-dir` case asserts.

## Evidence store

Cite only `/var/tmp/souji-r25-ScoutSourcesOpen/own/`. The scratch root also holds files from another writer (for example `man-*.txt`, `git-rev-parse.html`, `v2.56.0-git.adoc`) that this seat did not produce. Checksums are in `own/SHA256SUMS`.

| file | sha256 | origin |
|---|---|---|
| gitrepository-layout.html | ad7b52fb48738c259c8c9097edafc4ef2cf01248beedf1755c83b99a5fe3c64c | https://git-scm.com/docs/gitrepository-layout, 200, 64401 B |
| gitglossary.html | eb521ce9552c3ffa8606fb4798c0585f124ecb492312cdd0e490e10aeaf0c835 | https://git-scm.com/docs/gitglossary, 200, 109997 B |
| git-rev-parse.html | 9b8f63b653029da49bce87f6b292f099dc8f1b3667a85515c92f66a6f5eb2978 | https://git-scm.com/docs/git-rev-parse, 200, 122331 B |
| git-worktree.html | fa25690b04900cfc1f1b52bb6b23a85d63f8b763477cca71e655434adbfc63d2 | https://git-scm.com/docs/git-worktree, 200, 98918 B |
| git.html | a43b6eff834ea2eb2f4134c7be57a11c8b26d5a9884e5b331f6d5b99ea1a2f0e | https://git-scm.com/docs/git, 200, 244227 B |
| v2.56.0-gitrepository-layout.adoc | 39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439 | raw.githubusercontent.com/git/git/v2.56.0/Documentation/ |
| v2.56.0-glossary-content.adoc | 0635310817aac48a1b2087e957f60be0d95d05834670460143dbde85c8a7be7e | same |
| v2.56.0-git-rev-parse.adoc | 4d8e9aca13f6ea6808272eb44e417687a5cca7d23cf1ed311f25e9fdeb148902 | same |
| v2.56.0-git-worktree.adoc | ee8a368564ace74a07e4a034e080b26fb1c3b35d17ef1fe41dcbfcc5595fe8dc | same |
| gitrepository-layout.5 (roff, from /usr/share/man/man5/*.gz, git 2.56.0-1) | 2cc8adf89615a4e534fe38ffcb889312feadb855c4b4b59bb557c8387969e6fa | installed |
| gitrepository-layout.5.txt (MANWIDTH=100, col -b) | fde5885bd2f6e962fbd8dd662c47afd0134a08556a69856fe38b40f05f5c067d | rendered |
| gitglossary.7 | cbbb45298fb0c2b344faa15576137e019f3d190879ec8fbcf7c86dbdd25db166 | installed |
| gitglossary.7.txt | 8f0b851f5964f7573bfbc1d646db0c87cef60166607da2c8ec17e8ff9d7b45c0 | rendered |
| git-rev-parse.1 | e4bfee5f9f0df8df4fa1ec86b3b34625c2e94ce1f24c47948e856a17e2d1df61 | installed |
| git-rev-parse.1.txt | 80db0dea79d23428099479810678ee30f9d0fbd4b0806f64447d6ec1d9e69074 | rendered |
| git-worktree.1 / .1.txt | 2330c8c8…fa32408 / 22b8ed12…f2318f31 | installed / rendered |

Access record: first open 2026-10-25T12:28:03Z (layout and glossary), second open 2026-10-25T12:29:09Z (all five pages plus the four tag sources). Both opens returned the same sha256 for the layout and glossary pages. Gzipped man pages: `gitrepository-layout.5.gz` 1a22cc41…036a1a and `gitglossary.7.gz` 6dd42527…e3a3, both owned by git 2.56.0-1.

Page footers: gitrepository-layout says "last updated in 2.49.0" (`gitrepository-layout.html:1290`). gitglossary, git-rev-parse, git-worktree and git each say "last updated in 2.56.0".

Agreement check: I stripped HTML tags, roff escapes and link macros, then normalised whitespace. The quoted passages are equal across live HTML, the v2.56.0 adoc, and the installed roff for layout § commondir, rev-parse `--git-common-dir`, and rev-parse `--path-format`. git-worktree § DETAILS differs only by a typographic apostrophe in the HTML (’ vs ').

Empirical sanity check (throwaway repo in `own/wt`, removed afterwards; git 2.56.0):
- `git worktree add ../B` wrote `A/.git/worktrees/B/commondir` = `../..`, and `B/.git` = `gitdir: …/A/.git/worktrees/B`.
- In B, `rev-parse --path-format=absolute --git-dir --git-common-dir` printed `…/A/.git/worktrees/B` and `…/A/.git`.
- In A, both values were `…/A/.git`.

So the relative `commondir` path resolves against the private `$GIT_DIR` to the main repository's `.git`, as S124 states. This is a design probe, not claim data.

## S124 — row candidate (ACCEPT)

Quote (23 words), gitrepository-layout(5) § `commondir`:
> If this file exists, $GIT_COMMON_DIR (see git(1)) will be set to the path specified in this file if it is not explicitly set.

Companion quote, same entry (12 words):
> The repository with commondir is incomplete without the repository pointed by "commondir".

Exact locations of the entry:
- live HTML `gitrepository-layout.html` L2300–2306, anchor `#Documentation/gitrepository-layout.txt-commondir`
- installed roff `gitrepository-layout.5` L364–367
- rendered `gitrepository-layout.5.txt` L208–212
- tag source `v2.56.0-gitrepository-layout.adoc` L268–273

Supporting entry on the same page (no quote needed): `worktrees` says "Each subdirectory contains the working tree-related part of a linked working tree" (roff L377).

| field | value |
|---|---|
| id | S124 |
| source | gitrepository-layout(5) § commondir — https://git-scm.com/docs/gitrepository-layout |
| kind | docs |
| tier | A |
| scope | how a repository's common dir is located: the `commondir` file sets $GIT_COMMON_DIR, with relative paths resolved against $GIT_DIR, at git 2.56.0. Not worktrees/<id> admin files or pruning (S033), not the GIT_COMMON_DIR environment variable itself (S089), and not what rev-parse prints (S125) |
| anchor | § commondir; web manual last updated in 2.49.0, opened 2026-10-25 (HTTP 200, sha256 ad7b52fb…c835); tag v2.56.0 Documentation/gitrepository-layout.adoc L268-273; installed man page git 2.56.0-1 /usr/share/man/man5/gitrepository-layout.5.gz roff L364-367 |
| teaches | if `commondir` exists, $GIT_COMMON_DIR is set to the path in it unless already set; a relative path is relative to $GIT_DIR; the repository is incomplete without the one `commondir` points to |
| status | mined (once the C3 entry lands; otherwise queued) |
| opened | 2026-10-25 |
| recheck | on-release |
| used-by | corpus/knowledge/git-repo-structure-common-dir.md (C3, planned) |

Flip conditions that would make me reject S124:
- a later git release removes or rewords § commondir so it no longer says the file sets $GIT_COMMON_DIR;
- the installed man page diverges from the live page.

Disclosed limit: the page grounds where `commondir` points. It does not itself say "linked worktree → main `.git`". That link comes from git-worktree § DETAILS ("$GIT_COMMON_DIR is set to point back to the main worktree's $GIT_DIR"). S123 already opened that sentence, though its scope names only the private $GIT_DIR. If the entry needs the main-worktree statement, the Scribe should cite S123 with this note rather than widen S124.

## S125 as specified — REJECT (gitglossary(7) "common directory")

Search for `common`, `commondir`, `common dir` and `GIT_COMMON_DIR`, case-insensitive, returned 0 matches in every copy:
- `gitglossary.html` (live, last updated in 2.56.0, sha eb521ce9…c835)
- `gitglossary.7` roff and `gitglossary.7.txt`
- `v2.56.0-glossary-content.adoc` (the glossary's source)

Flip condition: a git release adds a glossary entry for the common directory. Recheck on-release.

## S125 replacement candidate — git-rev-parse(1) (ACCEPT-ready)

Quote 1 (8 words), § OPTIONS `--git-common-dir`:
> Show $GIT_COMMON_DIR if defined, else $GIT_DIR.

Quote 2 (15 words), § OPTIONS `--path-format`:
> If specified as absolute, the paths printed by those options will be absolute and canonical.

Both quotes are located in all three copies:
- live HTML `git-rev-parse.html`: L2917 for `--git-common-dir` (anchor `#Documentation/git-rev-parse.txt---git-common-dir`); L2888 for `--path-format`
- tag source `v2.56.0-git-rev-parse.adoc`: L267–268 for `--git-common-dir`; L246–247 for `--path-format`. `--git-common-dir` appears in the "options modified by `--path-format`" list that starts at L256.
- installed roff `git-rev-parse.1`: L354 for `--git-common-dir`; L336 for `--path-format`. In the rendered text, `--git-common-dir` is at L201–202.

| field | value |
|---|---|
| id | S125 |
| source | git-rev-parse(1) --git-common-dir and --path-format — https://git-scm.com/docs/git-rev-parse |
| kind | docs |
| tier | A |
| scope | what `rev-parse --path-format=absolute --git-common-dir` prints (the structure probe's call) at git 2.56.0. Not --verify or object resolution (S079, S091, S099), not how commondir is set (S124), and not git repo structure output (S005) |
| anchor | § OPTIONS --git-common-dir, --path-format; web manual last updated in 2.56.0, opened 2026-10-25 (HTTP 200, sha256 9b8f63b6…2978); tag v2.56.0 Documentation/git-rev-parse.adoc L246-256, L267-268; installed man page git 2.56.0-1 /usr/share/man/man1/git-rev-parse.1.gz roff L336, L354 |
| teaches | --git-common-dir prints $GIT_COMMON_DIR if defined, else $GIT_DIR; under --path-format=absolute the printed path is absolute and canonical, so a linked worktree's probe value can be compared byte-for-byte with the main repo's resolved git dir |
| status | mined (once the C3 entry lands; otherwise queued) |
| opened | 2026-10-25 |
| recheck | on-release |
| used-by | corpus/knowledge/git-repo-structure-common-dir.md (C3, planned) |

Flip conditions that would make me reject this S125:
- the L1 wants S125 to ground the colocated-vs-plain case instead;
- the Scribe judges a fourth git-rev-parse URL row redundant. Same URL, different scope: precedent S049/S036 and S057/S042.

## Peer candidate (ScoutSourcedClaimCheck)

ScoutSourcedClaimCheck proposes a different S125: git.git `builtin/repo.c` + `ref-filter.c` at v2.56.0, `ref_kind_from_refname` L2970–2997, which classifies `refs/jj/keep/*` as FILTER_REFS_OTHERS. That grounds the other C3 case (`SOUJI-R13-STRUCT-colocated-vs-plain`, references.others.count), not the common-dir case. The two candidates are complementary, not competing. I did not open those blobs, so I cannot verify the peer's line numbers.

Recommendation for the L1:
- S124 = gitrepository-layout § commondir;
- S125 = git-rev-parse `--git-common-dir`;
- the peer's code source becomes S126.

If the frozen "S124/S125" pair must stay at two rows, the L1 chooses which case to source; the other case's entry would then cite S123.

## Addendum (2026-10-25T12:34Z, after peer IRC)

The peer agrees: S124 = layout, S125 = rev-parse, S126 = code. Peer anchors for S126 (not opened by this seat): builtin/repo.c `count_references` L745-778 (others++ L762); ref-filter.c `ref_kind_from_refname` L2970-2997, returning FILTER_REFS_OTHERS at L2996; tag commit a018953688f1.

Id collisions, confirmed with `rg '\bS12[456]\b'` over the lane, excluding round-25 waves:
- **Bare S124** already means a staged-campaign row that maps to lane S109:
  - corpus/lessons/round-22.md L323, L352, L363, L432
  - LOG.md L1507
  - census/round-22/attempt2/quarantine-slice L3 and slice-verdicts.tsv L5
  - census/round-24/records/quarantine-slice L3 and slice-verdicts.tsv L6
  - corpus/lessons/round-24.md L234
  - tests/fixtures/r23-record-agreement.py L172
- **Bare S126** already means the GLib g_file_trash row (staged S126, lane S113) at:
  - round-22.md L324, L354, L360, L432
  - LOG.md L1507
  - both quarantine-slice files L4
  - slice-verdicts r22 L6 and r24 L7
  - round-24.md L170, L235, L238
  - r23-record-agreement.py L172
- **S125** appears only as round-6 seat names (`census/round-6/final-125.json` `"seat"`), a different namespace. No source-row collision.

Consequences for the Scribe and L1:
- Any D5-style disambiguation note must cover S124 as well as S126. The peer flagged S126 only.
- Same-URL, different-scope notes go in the round-25 provenance paragraph:
  - S124 shares its URL with S033 (worktrees/<id> admin files).
  - S125 shares its URL with S079, S091 and S099 (all --verify or object resolution). The peer named only S079.
