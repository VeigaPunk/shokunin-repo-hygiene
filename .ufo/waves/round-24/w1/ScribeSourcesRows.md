# ScribeSourcesRows — SOURCES.md append block + lesson Gate lines (souji r24 w1)

Seat: L1Souji24.ScribeSourcesRows (scribe, leaf, read-only on the lane). Lane tip read:
`ce5971c` (base `f9db2181647d91470a724a12d626bd6106805076`). Access date for every source: 2026-10-25.
Scratch: `/var/tmp/souji-r24-ScribeSourcesRows/` (removed before finishing). Tools installed or upgraded: none.

Revision 2 follows the L1 id assignment by document (IRC from L1Souji24): rows S120–S123 only, no
gitrepository-layout row, S123 scoped to § REFS, and `used-by` adds `tools/souji-size-census.py` to S120
and S122. The earlier S124–S127 drafts (git-sparse-checkout, odb/source-packed.c, object-file.c,
gitrepository-layout) are withdrawn; see Finding 2 for the effect on the entry.

## Status

STATUS: PASS. The block holds 4 rows, S120–S123, in the exact 11-column schema, all `mined`, opened
2026-10-25, recheck `on-release`. Each row's anchor names its committed-to-be snapshot under
`census/round-24/sources/`. All 5 snapshots pass `sha256sum -c SHA256SUMS`, and each code snapshot is
byte-identical to the raw tag file this seat fetched. Every Gate quote was located verbatim in the
snapshot bytes. A scratch copy of tip `ce5971c` plus the block validates with exit 0 once the entry
exists.

Landing preconditions:
- The entry `corpus/knowledge/count-objects-linked-worktree-garbage.md` must be committed, otherwise E11 ×4.
- `census/round-24/sources/` must be committed (it is untracked at `ce5971c`), otherwise the anchors do not resolve at the tip.

## Evidence

| check | command | result |
|---|---|---|
| next id | lane registry max at tip | `S119` (119 rows), so the next id is S120 (ScoutCollisionMap E3 agrees) |
| tag pins | `git ls-remote https://github.com/git/git refs/tags/v2.56.0 'refs/tags/v2.56.0^{}'` (same for v2.30.0) | v2.56.0 commit `a018953688f1b10bddf91bff8747068f5f4746a4`; v2.30.0 commit `71ca53e8125e36efbda17293c50027d31681a41f` |
| snapshots | `cd census/round-24/sources && sha256sum -c SHA256SUMS` | 5/5 `OK` |
| snapshot = upstream | digests of the raw files this seat fetched at the tag (`curl -fsS https://raw.githubusercontent.com/git/git/<tag>/<path>`) | `git-v2.56.0-path.c` `f98ba3446d768e3cd9ce8411d5707e35af576a7bd7ad2e7365d26759125d21d2`, `git-v2.30.0-path.c` `7c5b0710780498264d3771ae85b38e679e7ad733028835ccf18cee7d36c62d4a`, `git-v2.56.0-builtin-count-objects.c` `ec13ae40d08741d095fd61faca7ee0d86f0e315d3609f6465224b796d464e03e`, each equal to the upstream bytes, so snapshot line numbers equal upstream line numbers |
| worktree snapshot | `git-worktree.1.txt` sha256 `624821a65c9a30e793ecdc452accc931c222124cb066126deb7e17b3430eb51a`, footer `Git 2.56.0 2026-09-27` | § REFS at L137-146: para 2 at L140, para 4 at L144. The web page (banner `last updated in 2.56.0`) and the adoc at v2.56.0 L299-326 carry the same sentences |
| v2.30.0 agreement | `diff <(sed -n 101,136p v2.30.0) <(sed -n 89,124p v2.56.0)` | identical; the function diff (376-396 against 365-385) shows 3 lines: signature, `different_commondir` source, gitdir source |
| quotes | whitespace-normalised substring test over the snapshots (man hyphenation joined) | all Gate quotes found; max 15 words; no `\|` |
| schema | `awk -F'\|' '{print $2,"NF="NF}'` over the block | S120–S123 each `NF=13` |
| validate, no entry | `scripts/sources-census.sh validate <scratch lane> --today 2026-10-25`, scratch = `git archive ce5971c corpus tools` + block inserted after S119 | exit 1: `E11` S120–S123 for the entry path only. `tools/souji-size-census.py` resolves |
| validate, entry present | the same, with an empty stub at the entry path | exit 0, `ok`, 31 W04: 30 retained plus `S123 duplicate url git-scm.com/docs/git-worktree across scopes`. No E04 |
| census after | `scripts/sources-census.sh census <scratch lane>` | rows 123, tier.A 117, B 5, C 1, mined 100, queued 15, rejected 8 |

## Append block — `corpus/SOURCES.md` `## Registry`, after the S119 row (line 139)

```markdown
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S120 | git.git path.c at tag v2.56.0 — https://github.com/git/git/blob/v2.56.0/path.c | code | A | which $GIT_DIR names count-objects -v reports as linked-checkout garbage when the repository has a separate common dir; not the loose or pack scans (S122) and not a ref-backend claim | struct common_dir L89-96; common_list[] L98-124 (info L102, info/sparse-checkout L103, logs L104, logs/HEAD L105, refs L111, gc.pid L120); report_linked_checkout_garbage L365-385; tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4; snapshot census/round-24/sources/git-v2.56.0-path.c sha256 f98ba344…21d2 | in a linked worktree every common_list name not flagged ignore_garbage that exists under the private gitdir is reported as garbage; refs and info are such names, logs and gc.pid are not | mined | 2026-10-25 | on-release | corpus/knowledge/count-objects-linked-worktree-garbage.md, tools/souji-size-census.py |
| S121 | git.git path.c at tag v2.30.0 — https://github.com/git/git/blob/v2.30.0/path.c | code | A | whether the linked-checkout garbage table and sweep already existed at one named earlier tag; not a claim about any release between v2.30.0 and v2.56.0 or before v2.30.0 | struct common_dir L101-108; common_list[] L110-136 (logs L116, logs/HEAD L117, refs L123, gc.pid L132); report_linked_checkout_garbage(void) L376-396; tag v2.30.0 commit 71ca53e8125e36efbda17293c50027d31681a41f; snapshot census/round-24/sources/git-v2.30.0-path.c sha256 7c5b0710…2d4a | at v2.30.0 the table and its flags are byte-identical to v2.56.0 and the sweep differs only in signature and repository access, so the refs trigger is not new in 2.56.0 | mined | 2026-10-25 | on-release | corpus/knowledge/count-objects-linked-worktree-garbage.md |
| S122 | git.git builtin/count-objects.c at tag v2.56.0 — https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c | code | A | when count-objects runs its garbage reporters and how garbage and size-garbage accumulate and print; not which $GIT_DIR names the linked-checkout sweep tests (S120) and not a write-safety claim (S115) | real_report_garbage L41-53; loose_garbage, count_loose, count_cruft L55-82; verbose gate L116-119; loose walk call L121-122; KiB print L151-152; garbage and size-garbage lines L161-162; tag v2.56.0 commit a018953688f1b10bddf91bff8747068f5f4746a4; snapshot census/round-24/sources/git-v2.56.0-builtin-count-objects.c sha256 ec13ae40…e03e | only -v installs the reporter and runs the linked-checkout check; each reported path adds 1 to garbage and its stat size to size_garbage, printed as the floored KiB of the sum | mined | 2026-10-25 | on-release | corpus/knowledge/count-objects-linked-worktree-garbage.md, tools/souji-size-census.py |
| S123 | git-worktree(1) § REFS — https://git-scm.com/docs/git-worktree | docs | A | the per-worktree refs directory of a linked worktree at git 2.56.0 (§ REFS); not lock or prune behaviour (S003), not config.worktree read order (S058), and not whether worktree add creates refs eagerly | § REFS paras 2 and 4; web manual git-worktree last updated in 2.56.0, opened 2026-10-25; installed man page git 2.56.0-1, snapshot census/round-24/sources/git-worktree.1.txt § REFS L137-146 (para 2 L140, para 4 L144) sha256 624821a6…b51a | refs/bisect, refs/worktree and refs/rewritten are not shared, and a linked worktree's copies live at $GIT_COMMON_DIR/worktrees/<id>/refs, so that directory is documented per-worktree structure | mined | 2026-10-25 | on-release | corpus/knowledge/count-objects-linked-worktree-garbage.md |
```

The header and separator lines are copied from `corpus/SOURCES.md:19-20` so the block's shape can be checked. Only the 4 `S12x` lines are to be appended.

### In-place change to log (CORPUS.md SOURCES rule 2)

The entry draft also cites S115 (`ScribeEntry.md:72`), so the lesson must log this change old→new:

- S115 `used-by`: `corpus/knowledge/repo-size-census-readonly.md` → `corpus/knowledge/repo-size-census-readonly.md, corpus/knowledge/count-objects-linked-worktree-garbage.md`

### Proposed `## Paths` line (optional)

- F2 linked-worktree garbage reading — S123 → S120 → S121 → S122: the doc first, for why a linked worktree's private gitdir holds a refs directory; then the reader table that counts it, the earlier tag showing the trigger is old, and last the counters and the `-v` gate.

### Proposed `## Search log` note

- **Round-24 linked-worktree `garbage` sources (2026-10-25).** Question: which primary texts explain why `count-objects -v` reads `garbage: 1` in a linked worktree but `0` against the common dir? Where: raw git/git at tags v2.56.0 and v2.30.0, git-scm.com git-worktree, and the installed git 2.56.0-1 man pages, snapshotted under `census/round-24/sources/`. Identified 4 documents (path.c at two tags, builtin/count-objects.c, git-worktree). Screened 4. Included 4 in 4 rows. The gitrepository-layout snapshot was opened but was not admitted as a row (L1 decision; no entry claim cites it). Stop: each mechanism step the entry states resolves to an opened line.

## Lesson Gate lines — `corpus/lessons/round-24.md` `## Gate` → `### Opened sources (2026-10-25)`

- **S120 mined** — https://github.com/git/git/blob/v2.56.0/path.c#L89-L124 and #L365-L385, tag v2.56.0 (commit a018953688f1b10bddf91bff8747068f5f4746a4), accessed 2026-10-25, snapshot `census/round-24/sources/git-v2.56.0-path.c`. Located quote (L90): "Not considered garbage for report_linked_checkout_garbage". Second quote (L111): `{ 0, 1, 1, "refs" },`. Early return (L371-372): "if (!r->different_commondir) return;".
- **S121 mined** — https://github.com/git/git/blob/v2.30.0/path.c#L101-L136 and #L376-L396, tag v2.30.0 (commit 71ca53e8125e36efbda17293c50027d31681a41f), accessed 2026-10-25, snapshot `census/round-24/sources/git-v2.30.0-path.c`. Located quote (L102): "Not considered garbage for report_linked_checkout_garbage". `{ 0, 1, 1, "refs" },` is at L123. The struct and list are byte-identical to v2.56.0 L89-124.
- **S122 mined** — https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c#L116-L119, tag v2.56.0, accessed 2026-10-25, snapshot `census/round-24/sources/git-v2.56.0-builtin-count-objects.c`. Located quote (L116-118): "if (verbose) { report_garbage = real_report_garbage; report_linked_checkout_garbage(the_repository);". Counters (L49-52): "if (!stat(path, &st)) size_garbage += st.st_size; warning("%s: %s", desc, path); garbage++;". Unit (L152): "(unsigned long)(size_garbage / 1024));".
- **S123 mined** — https://git-scm.com/docs/git-worktree, § REFS, page last updated in 2.56.0, accessed 2026-10-25; installed man page git 2.56.0-1, snapshot `census/round-24/sources/git-worktree.1.txt` L140 and L144. Located quote (§ REFS para 2, L140): "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared." Second quote (§ REFS para 4, L144): "worktrees/bar/refs/bisect/bad are the same as $GIT_COMMON_DIR/worktrees/foo/HEAD and $GIT_COMMON_DIR/worktrees/bar/refs/bisect/bad."

Registry line for the lesson: `119 → 123` rows (`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`).
`validate` exits 0 once the entry is committed, with 31 `W04` warnings (30 retained plus S123) and no `E` finding.

## Findings

1. **Ids follow the L1 assignment by document.** S120 = path.c@v2.56.0, S121 = path.c@v2.30.0, S122 = count-objects.c@v2.56.0, S123 = git-worktree. These match ScribeEntry's placeholders S120–S123 (`ScribeEntry.md:54-57`). No staged shokuknow id is kept; staged S120–S123 name other documents.
2. **The entry draft still cites three ids that now have no row.** `ScribeEntry.md` cites S124 (git-sparse-checkout, item 4), S125 (odb/source-packed.c, item 5) and S126 (object-file.c, item 5) at `:69-71`, `:113-114`, `:124-131`. Under this assignment those ids would dangle, or would later bind to unrelated documents. Before landing, each must either be removed from the entry or get an L1-assigned row. The bytes were re-opened this round with matching digests: adoc `7952d0dc…9ede`, `bfb57f4c…ec4a`, `e011ce18…6708`; rev-1 row text is available on request. Without them, item 4's sparse-checkout storage claim and item 5's scan-scope claims rest only on probe runs (ProbeLinkedModes, ProbeGarbageKinds) and S115.
3. **`tools/souji-size-census.py` names no source id.** Its docstring (L8-10) states the common-dir rule ("`--git-dir=<common>` does not") but cites neither S120 nor S122. E11 passes because the path exists. For the `used-by` cell to be literally true, a docstring line such as `Sources: S120 path.c@v2.56.0 report_linked_checkout_garbage; S122 count-objects.c@v2.56.0 L116-119` would close the gap. That is the executor's file; this seat did not edit it.
4. **Snapshots are untracked at `ce5971c`.** `git status` shows `?? census/round-24/sources/`. The anchors cite these paths, so they must land in the same commit as the rows or earlier.
5. **Entry locator off by one (carried from rev 1).** `ScribeEntry.md` item 7 cites "S122 `:48-50`". At v2.56.0, `builtin/count-objects.c:48` is blank; the code is L49-50, or L49-52 with the counter.
6. **S123 scope excludes eager creation.** § REFS documents where per-worktree refs live. Neither git-worktree nor the layout page says `worktree add` creates an empty `refs/` (ScoutWorktreeDoc Finding 6). That stays a probe fact.

## Out of scope / not done

- No lane file was edited apart from this report. The S115 `used-by` change is drafted, not applied.
- The rev-1 rows S124–S127 are withdrawn per the L1; no gitrepository-layout row is drafted.
