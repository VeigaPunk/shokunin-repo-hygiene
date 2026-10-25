# souji round 25 — draft SOURCES rows S124/S125 (ScribeSources-2, wave 1; file sources-rows-2.md)

Draft only. The L1 integrates it into `corpus/SOURCES.md`; this draft does not edit that file.
Lane commit at drafting: 6e4737eab43d8fde1b85eb9f57023d29046705b4 (master).
This seat opened every cited page live on 2026-10-25 between 12:28Z and 12:33Z (HTTP 200). Each fetched file is sha256-identical to ScoutSourcesOpen's copy (`.ufo/waves/round-25/w1/ScoutSourcesOpen.md` § Evidence), as listed in the table below.

| copy | sha256 |
|---|---|
| gitrepository-layout.html (web) | ad7b52fb48738c259c8c9097edafc4ef2cf01248beedf1755c83b99a5fe3c64c |
| git-worktree.html (web) | fa25690b04900cfc1f1b52bb6b23a85d63f8b763477cca71e655434adbfc63d2 |
| git.html (web) | a43b6eff834ea2eb2f4134c7be57a11c8b26d5a9884e5b331f6d5b99ea1a2f0e |
| gitglossary.html (web) | eb521ce9552c3ffa8606fb4798c0585f124ecb492312cdd0e490e10aeaf0c835 |
| git-rev-parse.html (web) | 9b8f63b653029da49bce87f6b292f099dc8f1b3667a85515c92f66a6f5eb2978 |
| v2.56.0 Documentation/gitrepository-layout.adoc | 39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439 |
| v2.56.0 Documentation/git-worktree.adoc | ee8a368564ace74a07e4a034e080b26fb1c3b35d17ef1fe41dcbfcc5595fe8dc |
| v2.56.0 Documentation/git.adoc | 050c5330f1a231be22bee3db27c7ef90d8ba22bb7bd6c72c8bab462f6f0a1f79 |
| v2.56.0 Documentation/glossary-content.adoc | 0635310817aac48a1b2087e957f60be0d95d05834670460143dbde85c8a7be7e |
| v2.56.0 Documentation/git-rev-parse.adoc | 4d8e9aca13f6ea6808272eb44e417687a5cca7d23cf1ed311f25e9fdeb148902 |

Revision pins:
- Tag: git/git tag v2.56.0, peeled commit a018953688f1b10bddf91bff8747068f5f4746a4, read with `git ls-remote https://github.com/git/git 'refs/tags/v2.56.0^{}'`.
- Installed man pages: git 2.56.0-1, page footer `Git 2.56.0 2026-09-27`. The rendered line numbers below come from `MANWIDTH=80 man -P cat <sec> <page>` piped to `col -b`. ScoutSourcesOpen used `MANWIDTH=200`, so its man line numbers differ from these; the text is the same.

## Rows (11 columns, append after S123)

```
| S124 | gitrepository-layout(5) § commondir — https://git-scm.com/docs/gitrepository-layout | docs | A | the $GIT_DIR/commondir file as the source of $GIT_COMMON_DIR when that variable is not set explicitly, and the incompleteness of a repository carrying it; not that linked worktrees carry the file (S125), not which names are shared (S120 common_list), not environment precedence (S089), not worktrees/<id>/gitdir or locked (S033) | § commondir; web manual gitrepository-layout last updated in 2.49.0 (2.49.1 → 2.56.0 no changes), opened 2026-10-25; tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4 Documentation/gitrepository-layout.adoc L268-273 sha256 39ce8d13…9439; installed man page git 2.56.0-1 gitrepository-layout(5) rendered at MANWIDTH=80 L236-240 | a commondir file sets $GIT_COMMON_DIR to the path it names (relative paths resolve against $GIT_DIR) unless the variable is already set, and a repository carrying commondir is incomplete without the repository that file names | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md, corpus/lessons/round-25.md |
| S125 | git-worktree(1) § DETAILS $GIT_COMMON_DIR clause — https://git-scm.com/docs/git-worktree | docs | A | that within a linked worktree $GIT_COMMON_DIR points back to the main worktree's $GIT_DIR; only that clause, not the private $GIT_DIR clause of the same sentence (S123), not where the setting is stored (the page says a .git file; the commondir mechanism is S124), not lock or prune behaviour (S003) | § DETAILS, sentence beginning Within a linked worktree, $GIT_COMMON_DIR clause; web manual git-worktree last updated in 2.56.0, opened 2026-10-25; tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4 Documentation/git-worktree.adoc L374-378 (clause L376-377) sha256 ee8a3685…fe8dc; installed man page git 2.56.0-1 git-worktree(1) rendered at MANWIDTH=80 L329-333 | a linked worktree's common dir is the main worktree's $GIT_DIR, so a common-dir reading taken from a linked worktree should equal the main repository's resolved git dir | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md, corpus/lessons/round-25.md |
```

Both rows are `mined` only if the C3 entry `corpus/knowledge/git-repo-structure-common-dir.md` lands and cites them (prereg C3 lands it in the same commit as the README map row). If the entry does not land, write `queued` and set `used-by` to `corpus/lessons/round-25.md` only.

### Alternate S125 rows (the L1 picks one; swap the whole row)

Alternate 1 is ScoutSourcesOpen's recommended replacement: git(1) GIT_COMMON_DIR. The scope is narrowed here because S089 already anchors this variable (S089's teaches: "GIT_COMMON_DIR and GIT_INDEX_FILE redirect their respective stores").

```
| S125 | git(1) GIT_COMMON_DIR worktree split — https://git-scm.com/docs/git | docs | A | the split between non-worktree files read from $GIT_COMMON_DIR and worktree-specific files such as HEAD and index read from $GIT_DIR; not the repository-selection redirect itself (S089), not lock suppression (S036), not lazy fetch (S049), not how a linked worktree sets the variable | § ENVIRONMENT VARIABLES GIT_COMMON_DIR; web manual git last updated in 2.56.0, opened 2026-10-25; tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4 Documentation/git.adoc L580-586 sha256 050c5330…1f79; installed man page git 2.56.0-1 git(1) rendered at MANWIDTH=80 L1044-1050 | once $GIT_COMMON_DIR is set, non-worktree files normally in $GIT_DIR come from it while worktree-specific files such as HEAD and index stay in $GIT_DIR, so one worktree's state spans two directories | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md, corpus/lessons/round-25.md |
```

Alternate 2 is the briefed document, gitglossary(7), scoped to its `worktree` entry. The briefed `common directory` entry does not exist.

```
| S125 | gitglossary(7) § worktree — https://git-scm.com/docs/gitglossary | docs | A | the glossary's split of one worktree's repository metadata into a shared part and a per-worktree part; not a definition of the common directory (the page has no such entry), not where either part is stored, and not the per-worktree ref list (its per-worktree ref entry names only HEAD and refs/bisect/, narrower than S123 § REFS) | § worktree entry; web manual gitglossary last updated in 2.56.0 (2026-09-28), opened 2026-10-25; tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4 Documentation/glossary-content.adoc L771-778 sha256 06353108…e7be; installed man page git 2.56.0-1 gitglossary(7) rendered at MANWIDTH=80 L676-682 | most of a worktree's repository metadata is shared among the repository's worktrees while the index, HEAD, pseudorefs such as MERGE_HEAD, per-worktree refs and the per-worktree config file are kept per worktree | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md, corpus/lessons/round-25.md |
```

Why the primary S125 is the git-worktree clause:
- It is the only opened sentence that grounds C3's measured equality, `probe.git_common_dir == A's resolved git dir` for `--repo B` (ScoutSourcesOpen attack A2).
- S124 alone grounds only the commondir pointer; it never mentions linked worktrees.
- Overlap check: S123 anchors the same sentence, but its scope and teaches cover only the private-$GIT_DIR clause. Alternate 1 overlaps S089's anchor in the same way. Alternate 2 overlaps no row, but it names no directory, so it cannot ground either C3 case.

### Gate material (for `corpus/lessons/round-25.md` `## Gate`)

Quotes are copied from bytes opened this run. Each is at most 25 words and contains no pipe. Every quote was matched after whitespace normalisation against the web text and the v2.56.0 adoc. The man copies were also matched where noted (hyphenation joined, `git(1)` for `git[1]`).

- **SOURCES S124**: https://git-scm.com/docs/gitrepository-layout, § commondir, accessed 2026-10-25.
  - Adoc L269-271, also in the man text: "If this file exists, $GIT_COMMON_DIR (see git[1]) will be set to the path specified in this file if it is not explicitly set." (23 words)
  - Incompleteness clause, adoc L272-273, also in the man text: "The repository with commondir is incomplete without the repository pointed by "commondir"." (12 words)
- **SOURCES S125 (primary)**: https://git-scm.com/docs/git-worktree, § DETAILS, adoc L376-377, accessed 2026-10-25. The web page and man page use U+2019 in `worktree’s`; the adoc uses an ASCII apostrophe.
  - "$GIT_COMMON_DIR is set to point back to the main worktree’s $GIT_DIR (e.g. /path/main/.git)." (13 words)
- **Alternate 1**: https://git-scm.com/docs/git, § ENVIRONMENT VARIABLES GIT_COMMON_DIR, adoc L581-584.
  - "non-worktree files that are normally in $GIT_DIR will be taken from this path instead. Worktree-specific files such as HEAD or index are taken from $GIT_DIR." (25 words)
- **Alternate 2**: https://git-scm.com/docs/gitglossary, § worktree, adoc L774-776, also in the man text.
  - "repository metadata, most of which are shared among other worktrees of a single repository, and some of which are maintained separately per worktree" (23 words)

Write the ids as `SOURCES S124` / `SOURCES S125` in the lesson, entry and README. The bare id `S124` already carries other meanings in `corpus/lessons/round-22.md` (L323, L352, L363, L432) and `corpus/lessons/round-24.md` (L234). ScoutSourcesOpen finding 4 reports this; it is the same class as prereg D5's bare-"S123" problem.

### Used-by / status change log (rule 2)

No existing row's `status`, `recheck` or `used-by` changes for S124/S125.

There is one conditional case. If the landed C3 entry also cites S123 (git-worktree § REFS / private $GIT_DIR) or S089 (git(1) GIT_COMMON_DIR) in its `source:` lines, that row's `used-by` gains the entry, and the lesson logs the change old→new:
- S123 used-by: `corpus/knowledge/count-objects-linked-worktree-garbage.md` → `corpus/knowledge/count-objects-linked-worktree-garbage.md, corpus/knowledge/git-repo-structure-common-dir.md`
- S089 used-by: `corpus/lessons/round-20.md` → `corpus/lessons/round-20.md, corpus/knowledge/git-repo-structure-common-dir.md`

## Paths

Suggested new bullet. Append it; the existing F2 bullet stays unchanged.

- F2 linked-worktree envelope — S123 → S125 → S124 → S120: what a linked worktree keeps privately (its own $GIT_DIR and per-worktree refs); then where its common dir points (the main worktree's $GIT_DIR); then the commondir file that supplies that pointer, and why the private gitdir is incomplete without it; last, the tagged reader table of common-dir names that count-objects sweeps under a private gitdir.

## Search log

- **Round-25 common-dir envelope sources (2026-10-25).**
  - Question: which primary texts ground C3's linked-worktree envelope? Two facts are needed: a linked worktree's gitdir resolves to a common git dir equal to the main repository's git dir, and that pointer comes from a file without which the private gitdir is incomplete.
  - Query: on git-scm.com, gitrepository-layout § commondir; gitglossary, looking for a `common directory` or `COMMON_DIR` entry, else § worktree; git § ENVIRONMENT VARIABLES GIT_COMMON_DIR; git-worktree § DETAILS; git-rev-parse `--git-common-dir`.
  - Where: the live web manuals (HTTP 200); raw git/git at tag v2.56.0 (`Documentation/*.adoc`, peeled commit a0189536…); the installed git 2.56.0-1 man pages. The three copies agree on every quoted passage. The bytes are sha256-identical to ScoutSourcesOpen's independent fetches.
  - Date: 2026-10-25.
  - Counts: identified 5 documents, screened 5, included 2 as new rows, excluded 3 from new rows.
    - Included: S124 (gitrepository-layout § commondir) and S125 (git-worktree § DETAILS, $GIT_COMMON_DIR clause only).
    - Excluded, git(1) GIT_COMMON_DIR: S089 already anchors this variable. It is kept as a drafted alternate row with a narrower scope.
    - Excluded, gitglossary: the briefed entry does not exist, and the `worktree` entry names no directory. It is kept as a drafted alternate row.
    - Excluded, git-rev-parse `--git-common-dir` ("Show $GIT_COMMON_DIR if defined, else $GIT_DIR.", adoc L267-268): the page is already registered (S079/S091/S099, other scopes). It is the exact call the probe makes (`tools/souji-repo-structure.sh:193`) and is a lead for a later scoped row, outside the frozen S124/S125 frame.
  - Negative claim, with its sweep: gitglossary has no `common directory` or `COMMON_DIR` entry. `grep -ci common` returns 0 on the v2.56.0 `glossary-content.adoc`, on the rendered web text and on the rendered installed page.
  - Other observations:
    - The glossary's `per-worktree ref` entry (adoc L496-500) names only HEAD and `refs/bisect/`. That is narrower than git-worktree § REFS (S123).
    - git-worktree § DETAILS says the two settings "are made in a .git file". ScoutSourcesOpen's host run shows `commondir: ../..` under the private gitdir, so S125's scope excludes the storage mechanism and leaves it to S124.
    - The gitrepository-layout web page is stamped "last updated in 2.49.0". Its 2.56.0 equivalence rests on the v2.56.0 adoc and the installed page.
  - Stop rationale: both C3 facts resolve to a located primary sentence at a pinned revision. No claim is made about which files a git command writes, or about reference counts in jj-colocated repositories; C3's second case is measured by the fixture, not sourced.
