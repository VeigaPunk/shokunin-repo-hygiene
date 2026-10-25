# ScoutSourcedClaimCheck — C3 sourced-claim plan (S124/S125)

Seat `L1Souji25.ScoutSourcedClaimCheck-2`, read-only scout. Lane tip 6e4737eab43d8fde1b85eb9f57023d29046705b4
(SOURCES.md last changed at 315422ba; sha256 59befea6…7de). Staged package
`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` sha256 1510052e…7d6 (shokuknow HEAD 8b94c5c1, read only).
Host git 2.56.0-1. Opened 2026-10-25T12:29Z. No installs. Scratch `/var/tmp/souji-r25-ScoutSourcedClaimCheck/` removed.

## Status

STATUS: PARTIAL — the collision check is clean against the lane registry, and no renumbering is legal or needed. But S124 and S125 both collide numerically with staged campaign rows (different documents). The bare tokens `S124`/`S125` already mean those staged rows in six committed lane files. The planned S125 source (gitglossary "common directory") does not exist at git 2.56.0. Replacement rows are given in (c).

## Evidence

Collision check (the 0-3-space row grammar from CORPUS.md §Maintained parser note):

```sh
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' $F | grep -oE 'S[0-9]+' | sort -u
comm -12 staged.ids lane.ids ; comm -12 proposed.ids staged.ids ; comm -12 proposed.ids lane.ids
```

- staged ids (134): S109 S110 … S242. This is the contiguous range S109–S242, every id present.
- lane ids (123): S001 S002 … S123. This is the contiguous range S001–S123, with no gaps (the gap scan printed nothing).
- `comm -12 staged lane` → S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 (15 ids, matching the round-24 lesson's "post-append collisions 15").
- `comm -12 {S124,S125} staged` → `S124`, `S125`.
- `comm -12 {S124,S125} lane` → (empty).
- Lane health: duplicate ids none, malformed rows (NF!=13) 0, 4+-space-indented S rows none in either file. Lane max id is S123, so the next unused id is S124.

What the staged rows S124/S125 are (SOURCES.append.md:22-23):
- staged S124 = "souji round-2 probe noreplace_probe.py", own-work. This is already adopted as lane **S109** (round-22.md L323: "campaign S124→S109").
- staged S125 = "statx(2) — Linux man-pages 6.19", scope mount-id uniqueness. It was never adopted. Lane S114 is statx(2) with a different scope. Staged knowledge `quarantine-origin-record-fields-r23.md:3` cites `source: S125`.

Bare `S124` already in committed lane files (`rg -n -w 'S12[45]'`, excluding .ufo and operator-sweep):
`census/round-22/attempt2/slice-verdicts.tsv:5`, `census/round-22/attempt2/quarantine-slice:3`,
`census/round-24/records/slice-verdicts.tsv:6`, `census/round-24/records/quarantine-slice:3`,
`tests/fixtures/r23-record-agreement.py:172`, `corpus/lessons/round-24.md:234`, `corpus/lessons/round-22.md:352,363`.
Every one of these means the staged own-work row. Bare `S125` has no lane hits outside census/round-6 seat names (`"seat": "S125"`, which are not source ids).

Sources opened this run (all live 200 OK or installed git 2.56.0-1):

| doc | revision | located text (≤25 words, verbatim) |
|---|---|---|
| gitrepository-layout(5) § commondir, installed roff L364-367; round-24 text snapshot `census/round-24/sources/gitrepository-layout.5.txt` L130-131 (sha256 41439c3f…c490, matches SHA256SUMS); web page "last updated in 2.49.0", html sha256 ad7b52fb…e2c, same sentence | git 2.56.0-1 | "If this file exists, $GIT_COMMON_DIR (see git(1)) will be set to the path specified in this file if it is not explicitly set." |
| same § | same | "The repository with commondir is incomplete without the repository pointed by "commondir"." |
| same page § objects, installed col-b L41 | same | "This directory is ignored if $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/objects" will be used instead." |
| git-rev-parse(1) § --git-common-dir, roff L354-360; web "last updated in 2.56.0" | 2.56.0 | "Show $GIT_COMMON_DIR if defined, else $GIT_DIR." |
| git-repo(1) § structure, roff L115; web "last updated in 2.56.0" | 2.56.0 | "Reference counts categorized by type" |
| builtin/repo.c @v2.56.0 (raw, sha256 b915126b…487be, 996 lines), L762 inside `case FILTER_REFS_OTHERS:` | tag commit a018953688f1b10bddf91bff8747068f5f4746a4 (`git ls-remote` peeled) | "stats->others++;" ; L692 "print_keyvalue("references.others.count", key_delim," |
| ref-filter.c @v2.56.0 (raw, sha256 9dae1123…0480), `ref_kind_from_refname` L2970-2997 | same tag | "{ "refs/heads/" , FILTER_REFS_BRANCHES }," … L2996 "return FILTER_REFS_OTHERS;" |
| gitglossary(7) | installed 2.56.0 and web "last updated in 2.56.0" (html sha256 eb521ce9…835) | **absent**: `rg -c -i common` gives 0 on both the installed page and the live page |

Behaviour run (scratch, git 2.56.0, committed probe `tools/souji-repo-structure.sh`):
- Setup: A is a repo with one commit; B was created with `git -C A worktree add ../B`. Then `git -C B rev-parse --path-format=absolute --git-common-dir` → `…/A/.git`; `--absolute-git-dir` → `…/A/.git/worktrees/B`; `A/.git/worktrees/B/commondir` = `../..`.
- `bash tools/souji-repo-structure.sh --repo B` → `probe.status=ok`, `probe.git_dir=…/A/.git/worktrees/B`, `probe.git_common_dir=…/A/.git`. The probe takes this value from `rev-parse --git-common-dir` (tools/souji-repo-structure.sh L193).
- `git clone --no-local A P`, and the same for C, then `update-ref refs/jj/keep/<oid> HEAD` in C. In `repo structure --format=lines`, P shows `references.others.count=0` and C shows `references.others.count=1`. The other three counts are identical: branches=1, tags=0, remotes=3.

## Findings

1. **(a) Collision result.** S124 and S125 do not collide with lane rows: `comm -12 proposed lane` is empty, and the lane is contiguous S001–S123. They **do** collide with staged campaign ids S124 and S125, and both pairs name different documents (staged S124 is the noreplace probe, already lane S109; staged S125 is statx mount-id). This collision cannot be avoided. The staged range covers S109–S242, so any lane id up to S242 collides. Round-22 M21 said the same: "the overlap is unavoidable for any lane id below the campaign's maximum" (`corpus/lessons/round-22.md` L429-430).
2. **(b) Renumbering: not needed and not legal.** CORPUS.md §SOURCES.md says `id`: "`S` + 3 or more digits, the next unused; never reused". The next unused lane id is S124. Skipping to S243 would break "the next unused", and round-22 M16 says "the lane's next free id the only legal one" (round-22.md L319-320). Nothing was renumbered. The disambiguator is a by-document map, the same one rounds 22 and 24 used.
3. **ATTACK: bare `S124` is about to become ambiguous inside the lane.** This is the same defect class as D5 (bare S123). Once lane S124 is appended as a git document, the eight bare-`S124` sites listed under Evidence (slice-verdicts.tsv r22/r24, quarantine-slice r22/r24, `tests/fixtures/r23-record-agreement.py:172`, round-22.md L352/L363, round-24.md L234) will read as the new row. The round lesson needs a disambiguation note alongside D5's: "pre-r25 bare S124 = staged own-work noreplace probe = lane S109". The by-document map should gain two rows: staged S124 → lane S109, and staged S125 → (not adopted; lane S114 is statx under a different scope). `r23-record-agreement.py:172` is fixture data keyed on staged ids. It does not need to change, but the lesson should state it.
4. **ATTACK: the planned S125 source is ungroundable.** The ScoutSourcesOpen item (w1-spec) names "git-glossary(7) … entry `common directory` / `COMMON_DIR`". No such entry exists in the installed 2.56.0 page or in the live page ("last updated in 2.56.0"); both return 0 matches for `common`. Rule 1 ("A row is a claim. Write it only after opening the source") cannot be met for that row. I messaged `L1Souji25.ScoutSourcesOpen` and `L1Souji25.ScribeSources`.
5. **Coverage gap in the planned pair.** C3 has two halves: the linked common dir, and colocated versus plain. Both planned candidates (layout and glossary) ground only the first half. The second half (`references.others.count` rises with `refs/jj/keep/*`) needs the ref classifier. That classifier is in git source (builtin/repo.c + ref-filter.c @v2.56.0), not in any manual: git-repo(1) says only "Reference counts categorized by type". The existing S037 is repo.c at **v2.55.0**, scoped to refs-rooted object accounting. The existing S054 is jj keep-ref creation and removal. Neither covers the classification.
6. **S124 shares its URL with S033.** S033 is gitrepository-layout, scoped to `worktrees/<id>` admin files, status `queued`, used-by `—`. Sharing a URL under a different scope has precedent: S049/S036, S057/S042, S059/S045, all noted in the SOURCES provenance paragraphs. The round-25 provenance paragraph must say so. S033's cells stay unchanged; no in-place change is needed.
7. **Contract checks for the proposed rows.** Both rows have 11 cells and no `|` in any cell. Kinds are `docs` and `code` (both in the enum). Tier A is correct: official docs for the page scope, and tag-pinned source for the code scope. Neither row is `community`, so there is no tier inflation. Anchors give a section or lines plus a revision. Each `teaches` cell states a page or code fact, not lane policy (S096 precedent). `opened` is 2026-10-25, this round. `status: mined` is valid **only if** `corpus/knowledge/git-repo-structure-common-dir.md` lands in the same commit; otherwise the frozen census "mined rows whose used-by paths do not exist" fails. If the entry slips, the rows must be `queued` with used-by `—`.
8. **`used-by` semantics (contract).** "repo-relative paths of the knowledge entries or lessons citing the row". The proposed rows list only the entry. A side observation outside C3: S120 and S122 list `tools/souji-size-census.py` in used-by. That path is neither a knowledge entry nor a lesson, so the existing cell deviates from the contract wording. Nothing in C3 depends on it. [INFERENCE] The census only checks that the path exists, so it passes.
9. **Snapshot paths.** The S124 text snapshot already exists and is committed at round 24 (`census/round-24/sources/gitrepository-layout.5.txt`, sha matches SHA256SUMS), so it can be cited. The S125 code snapshots do not exist yet. The suggested paths `census/round-25/sources/git-v2.56.0-builtin-repo.c` and `census/round-25/sources/git-v2.56.0-ref-filter.c`, with the sha256 above, must be written by the integrator (not by me) before the anchors cite them.

### (c) Exact rows to carry (proposal; integrator appends; ScribeSources owns the draft)

```
| S124 | gitrepository-layout(5) § commondir — https://git-scm.com/docs/gitrepository-layout | docs | A | how a linked worktree's private $GIT_DIR resolves its common dir through the commondir file at git 2.56.0; shares S033's URL under a different scope (not the worktrees/<id> admin files of S033) and not the per-worktree refs of S123 | § commondir, § objects; web manual gitrepository-layout last updated in 2.49.0, opened 2026-10-25; installed man page git 2.56.0-1 roff L364-367; text snapshot census/round-24/sources/gitrepository-layout.5.txt L130-131 sha256 41439c3f…c490 | a commondir file sets $GIT_COMMON_DIR, objects, refs and config are then read from the common dir instead of $GIT_DIR, and a gitdir with commondir is incomplete without the repository it names | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md |
| S125 | git.git builtin/repo.c and ref-filter.c at tag v2.56.0 — https://github.com/git/git/blob/v2.56.0/builtin/repo.c (also ref-filter.c) | code | A | which refs git repo structure counts under references.others at git 2.56.0; not refs-rooted object accounting (S037, v2.55.0) and not keep-ref creation or removal (S054) | builtin/repo.c struct ref_stats L318-323, references.*.count print L686-693, count_references L745-778 (switch L751, others L762), refs_for_each_ref L794; ref-filter.c ref_kind_from_refname L2970-2997 (return FILTER_REFS_OTHERS L2996); tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4; snapshots census/round-25/sources/git-v2.56.0-builtin-repo.c sha256 b915126b…487be, census/round-25/sources/git-v2.56.0-ref-filter.c sha256 9dae1123…0480 | a ref outside refs/heads/, refs/remotes/ and refs/tags/ that is not HEAD, a pseudoref or a root ref is counted as references.others, so refs/jj/keep/* refs raise references.others.count | mined | 2026-10-25 | on-release | corpus/knowledge/git-repo-structure-common-dir.md |
```

The C3 entry's `source:` lines, in the shape of `count-objects-linked-worktree-garbage.md` L1-5:

```
source: S124 — https://git-scm.com/docs/gitrepository-layout — § commondir, § objects — git 2.56.0 (installed man page 2.56.0-1 roff L364-367; web "last updated in 2.49.0"); snapshot census/round-24/sources/gitrepository-layout.5.txt
source: S125 — https://github.com/git/git/blob/v2.56.0/builtin/repo.c — line 745-778 (count_references), line 686-693 (references.*.count); ref-filter.c line 2970-2997 (ref_kind_from_refname) — tag commit a018953688f1; snapshots census/round-25/sources/git-v2.56.0-builtin-repo.c, git-v2.56.0-ref-filter.c
source: S123 — https://git-scm.com/docs/git-worktree — § DETAILS (private $GIT_DIR) — existing row, cited not duplicated
source: S054 — jj v0.45.1 git_backend.rs — refs/jj/keep/* creation — existing row, cited not duplicated
```

Gate quotes for the lesson are the ≤25-word quotes in the Evidence table: the commondir sentence and the incomplete-without sentence for S124; L762 `stats->others++;` plus L2996 `return FILTER_REFS_OTHERS;` for S125.

Optional alternative row, not proposed: git-rev-parse(1) § --git-common-dir. Quote: "Show $GIT_COMMON_DIR if defined, else $GIT_DIR." This is the exact interface the probe calls at L193, and it would share its URL with S079 under a different scope. Using it as S125 would leave the colocated/plain half without a source (Finding 5), so I list it only for a possible S126.

## Addendum (12:34Z) — reconciled with ScoutSourcesOpen (`.ufo/waves/round-25/w1/ScoutSourcesOpen.md`)

ScoutSourcesOpen independently rejected S125-as-gitglossary and proposes three rows: S124 is gitrepository-layout § commondir, S125 is git-rev-parse(1) § --git-common-dir together with § --path-format, and S126 is the code row from (c) above. I agree. It sources every C3 case and it is not a re-specification: the prereg says the entry cites "S124/S125", and citing S126 as well goes beyond that text without dropping anything. The L1 decides whether a third row is allowed. With only two rows, the colocated/plain case has no source (Finding 5).

- **Collision check for S126.** S126 is not a lane row (0 hits). It is in the staged package: staged S126 is GLib `g_file_trash()` (SOURCES.append.md:24), which is already adopted as lane **S113** ("S126→S113", round-22.md L324). Renumbering is still not needed or legal, because S126 would be the next unused id after S125.
- **Bare-`S126` hazard (extends Finding 3).** Ten committed lane sites mean the staged gtk row: `tests/fixtures/r23-record-agreement.py:172`, `census/round-22/attempt2/slice-verdicts.tsv:6`, `census/round-22/attempt2/quarantine-slice:4`, `census/round-24/records/slice-verdicts.tsv:7`, `census/round-24/records/quarantine-slice:4`, round-22.md L354/L360, round-24.md L235/L238, and LOG.md L1507 (the last is a map line and already qualified). The disambiguation note should cover bare S124 (staged noreplace probe, lane S109) and bare S126 (staged gtk trash, lane S113).
- **S124 teaches narrowed** to fit ScoutSourcesOpen's limit. The commondir section never says "linked worktree", and the main-repo-`.git` sentence belongs to S123 § DETAILS. In the row in (c), replace the scope opener "how a linked worktree's private $GIT_DIR resolves its common dir through the commondir file at git 2.56.0" with "what a commondir file in a $GIT_DIR sets and what a gitdir carrying one depends on, at git 2.56.0". `teaches` is unchanged because it states page facts only. The entry must cite S123 for "linked worktree gitdir is private, under the main repository".
- **S126:** the code row from (c), renumbered from S125 to S126 in this proposal only. Nothing is appended.
- **S125 (rev-parse):** I did not open `--path-format` this run. I opened `--git-common-dir` (roff L354-360, web "last updated in 2.56.0"). S079 shares this URL with scope `--verify`, so the provenance paragraph must note the different scope.

## Attack log

- A1 (Finding 3): bare-S124 ambiguity across 8 committed lane sites after the append. Falsified if every pre-r25 bare `S124` were already qualified as staged. They are not (see the rg hits).
- A2 (Finding 4): the S125-as-gitglossary plan rests on a nonexistent entry. Falsified by any match for `common dir`, `commondir` or `GIT_COMMON_DIR` in gitglossary 2.56.0. There are 0 matches, local and live.
- A3 (Finding 5): the planned pair leaves C3's colocated/plain half unsourced. Falsified if S037 or S054 grounded the references.others classification. Neither does: S037 is v2.55.0 object accounting and S054 is keep-ref lifecycle.
- A4 (Finding 7): `mined` with a used-by entry that lands in a later commit breaks the frozen census. This is a landing-order precondition, not a defect yet.
