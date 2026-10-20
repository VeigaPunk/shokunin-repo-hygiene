STATUS: DONE — both pages opened 2026-10-20; "attribute lookup consults `$GIT_DIR/info/attributes`" is doc-stated (18-word verbatim quote located); "any status call may open it" is not stated by either page; one SOURCES row drafted.

# SrcGitRepoLayoutAttrs — r17 W1 source seat

Question: is `$GIT_DIR/info/attributes` read by git for attribute lookup, so that any status/check-attr call may open it?

## Sources opened (access date 2026-10-20)

| URL | version / "last updated" line served | pinned revision used for line anchors |
|---|---|---|
| https://git-scm.com/docs/gitrepository-layout | `gitrepository-layout last updated in 2.49.0`; version menu line `2.49.1 → 2.56.0 no changes`; 2.49.0 entry dated 2025-03-14 | `Documentation/gitrepository-layout.adoc` at tag v2.56.0 (unchanged since 2.49.0 per the page's own menu) |
| https://git-scm.com/docs/gitattributes | `gitattributes last updated in 2.56.0`; 2.56.0 entry dated 2026-09-28 | `Documentation/gitattributes.adoc` at tag v2.56.0 |

## 1. Verbatim answer — stated

> "When deciding what attributes are assigned to a path, Git consults `$GIT_DIR/info/attributes` file (which has the highest precedence)"

Anchor: gitattributes(5), § DESCRIPTION, `Documentation/gitattributes.adoc:69-71` at tag v2.56.0 (web page served "last updated in 2.56.0", opened 2026-10-20). 18 words, verbatim, unparaphrased.

Corroborating statements, also verbatim and located:

- gitattributes(5), § EXAMPLES, `:1341`: "Finally it examines `$GIT_DIR/info/attributes`." (4 words) — the worked precedence walk-through names it as the last, overriding source.
- gitrepository-layout(5), § `info/attributes`, `Documentation/gitrepository-layout.adoc:228-230`: "`info/attributes` — Defines which attributes to assign to a path, similar to per-directory `.gitattributes` files." That entry states what the file is (a per-path attribute source inside the repository's `info` directory) but does not itself use the word "read".

What the pages do **not** state: no sentence on either page names `git status` as a command that reads attributes. The only status mentions in gitattributes are example lines — `:263` "`$ git status        # Show files that will be normalized`" and `:267` "If any files that should not be normalized show up in 'git status'". `git check-attr` is named as an attribute consumer at `:112-113` and in SEE ALSO at `:1358`.

Verdict on the two halves of the question:

- "read by git for attribute lookup" — **holds**, on the § DESCRIPTION quote above.
- "so any status/check-attr call may open it" — **partial**: `check-attr` is a named consumer (`:1358`); for `status` the pages offer only the end-of-line example at `:263`/`:267`, never a doctrinal statement. Treat the status path as inference-from-example, not as a quoted claim.

## 2. Drafted SOURCES row (paste as one row; L1 numbers the id)

Column order copied from `corpus/SOURCES.md` header: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.

| S0?? | gitattributes(5) — https://git-scm.com/docs/gitattributes | docs | A | that attribute lookup consults `$GIT_DIR/info/attributes` with the highest precedence; not which commands read attributes | web manual "gitattributes last updated in 2.56.0" (2.56.0 dated 2026-09-28), opened 2026-10-20; § DESCRIPTION `Documentation/gitattributes.adoc:69-71` at tag v2.56.0; § EXAMPLES :1341; § NOTES :1304-1306; § EFFECTS :119-120 | Git consults `$GIT_DIR/info/attributes` (highest precedence) when deciding a path's attributes, so any attribute lookup reads a repo-local file souji does not control; the page names no status invocation and its symlink rule covers only a worktree `.gitattributes` | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |

Why `mined`: it grounds D2 this round — the guard exists because attribute lookup is the read path to a repo-local metadata file, which is exactly what D2 refuses to let a git call reach in a degraded repository.

Landing ordering, so the census stays green: the row's `used-by` path `corpus/lessons/round-17.md` does not exist until L1 writes the round lesson. The SOURCES census check "mined rows whose used-by paths do not exist — must print nothing" will print `missing: corpus/lessons/round-17.md` until then. If L1 pastes the row before the lesson lands, paste this variant instead and flip it (status `queued`→`mined`, used-by `—`→path) in the same commit as the lesson:

| S0?? | gitattributes(5) — https://git-scm.com/docs/gitattributes | docs | A | that attribute lookup consults `$GIT_DIR/info/attributes` with the highest precedence; not which commands read attributes | web manual "gitattributes last updated in 2.56.0" (2.56.0 dated 2026-09-28), opened 2026-10-20; § DESCRIPTION `Documentation/gitattributes.adoc:69-71` at tag v2.56.0; § EXAMPLES :1341; § NOTES :1304-1306; § EFFECTS :119-120 | Git consults `$GIT_DIR/info/attributes` (highest precedence) when deciding a path's attributes, so any attribute lookup reads a repo-local file souji does not control; the page names no status invocation and its symlink rule covers only a worktree `.gitattributes` | queued | 2026-10-20 | on-release | — |

Expected registry side effect (not a failure): this URL is already S045's, so the fleet census will add a warning of the class it already emits for S035/S036/S038/S049 — `souji W04 S0?? duplicate url git-scm.com/docs/gitattributes across scopes` — with exit 0. The precedent is four standing rows, so no avoidance is needed; a distinct `scope` and `teaches` is what keeps it honest.

Optional second row, **not** required by the question and skippable: gitrepository-layout(5) would add the layout side (`info` is repository-local metadata; `info/attributes` defines per-path attributes). S033 already registers that URL for `worktrees/<id>` admin files, so a second row is only worth it if L1 wants the `info/attributes` definition anchored in the registry itself:

| S0?? | gitrepository-layout(5) — https://git-scm.com/docs/gitrepository-layout | docs | A | `$GIT_DIR/info` is per-repository metadata and `info/attributes` defines per-path attributes there | web manual "gitrepository-layout last updated in 2.49.0" with "2.49.1 → 2.56.0 no changes", opened 2026-10-20; § info, § info/attributes `Documentation/gitrepository-layout.adoc:216-230` at tag v2.56.0 | per-repository metadata lives in `$GIT_DIR/info` and `info/attributes` defines attributes for paths, so the file is per-repo state, not global config; the entry states no write or file-type requirement | queued | 2026-10-20 | on-release | — |

## 3. Contradiction check against the context claim text

Claim text checked: that `$GIT_DIR/info/attributes` "is read by git for attribute lookup (so any status/check-attr call may open it)."

**No statement on either page contradicts it.** The two nearest statements, quoted so L1 can see the boundary rather than take my word:

1. gitattributes(5), § NOTES, `Documentation/gitattributes.adoc:1304-1306`:
   > "Git does not follow symbolic links when accessing a `.gitattributes` file in the working tree."
   This is scoped to a **worktree** `.gitattributes`. It is not a statement about `$GIT_DIR/info/attributes`, so it neither contradicts the claim nor licenses treating a symlinked `info/attributes` as already safe. It must not be cited as if it protected the `$GIT_DIR` file.

2. gitattributes(5), § EFFECTS, `:119-120`:
   > "Currently, the following operations are attributes-aware."
   The enumerated subsections (`:122` Checking-out and checking-in, Generating diff text, Performing a three-way merge, Checking whitespace errors, Creating an archive, Packing objects, Viewing files in GUI tools) contain no `git status` section. Read as a closed list this would argue against "any status call may open it". It is not closed in that sense — the page's own end-of-line example runs `git status` to observe normalization (`:263`, `:267`) — so the list is of operations whose behavior attributes *change*, not of commands that read attributes. Report this as the only counter-reading on either page, and keep the status path labelled as inference.

Neither page states any regular-file, link-count or file-type requirement for `$GIT_DIR/info/attributes`; the repo-layout entry (`:228-230`) and the gitattributes precedence rule are silent on file type. So D2's refusal of a hardlinked or non-regular `info/attributes` is **stricter than the documentation** — a defensive choice, and it should be disclosed as one, in the same style as S045's filter-driver choice. The documentation supports "the file is the read path"; it does not support "this file shape is unsupported by git".

## Commands run and observed output

1. `read https://git-scm.com/docs/gitrepository-layout` (583 rendered lines) → version block: `gitrepository-layout last updated in 2.49.0`; `2.49.1 → 2.56.0 no changes`; 2.49.0 dated *2025-03-14*. § `info` reads: "Additional information about the repository is recorded in this directory." § `info/attributes` reads: "Defines which attributes to assign to a path, similar to per-directory `.gitattributes` files."
2. `read https://git-scm.com/docs/gitattributes` (1468 rendered lines) → version block: `gitattributes last updated in 2.56.0`; 2.56.0 dated *2026-09-28*. § DESCRIPTION contains the consulted-first sentence; § NOTES contains the symlink sentence.
3. `grep` over `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitattributes.adoc` for `deciding what attributes are assigned|does not follow symbolic links|Finally it examines|attributes-aware` → hits at `:69`, `:120`, `:1304`, `:1341` (output quoted above; `:69-71` is the three-line wrap of the 18-word sentence).
4. `grep` over `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitrepository-layout.adoc` for `info/attributes|Defines which attributes` → hits at `:221` (`info/exclude`), `:228-230` (`info/attributes`).
5. `grep` over the same gitattributes adoc for `status|check-attr` → `check-attr` at `:112-113`, `:1358`; `status` only as example lines `:263`, `:267` and as filter-protocol status words (`:438`, `:539-664`, `:1149-1151`). Zero `status` entries under § EFFECTS.
6. `grep` over the repo-layout adoc for `attributes|symlink|symbolic` → `:137` (HEAD may be "a symbolic link"), `:228-230` (`info/attributes`). Zero file-type or link-count statements about `info/attributes`.

Word count of the primary quote: 18 (`When` 1, `deciding` 2, `what` 3, `attributes` 4, `are` 5, `assigned` 6, `to` 7, `a` 8, `path` 9, `Git` 10, `consults` 11, `$GIT_DIR/info/attributes` 12, `file` 13, `which` 14, `has` 15, `the` 16, `highest` 17, `precedence` 18).

## Verdict and smallest fix

- Question part 1 ("read by git for attribute lookup"): **holds**, quoted and located.
- Question part 2 ("any status call may open it"): **partial** — `check-attr` is a named consumer, `status` is only an example; do not quote the page for status.
- Smallest fix for D2's write-up: cite this row for "attribute lookup consults `$GIT_DIR/info/attributes`", and state separately that refusing a hardlinked/non-regular one is souji's stricter defensive choice (neither page constrains file type). One sentence of disclosure, no code change implied by the docs.

## Remaining unknowns (not opened this round)

- Source-level read path: whether git's attribute reader opens `$GIT_DIR/info/attributes` with `O_NOFOLLOW` or how it behaves on a non-regular file. Both named pages are silent; establishing it needs `attr.c`/`read_attr_from_file` at the tag, which was outside this question's two sources.
- Whether a given `git status` invocation reaches the attribute machinery on every stat state. git-status(1) is already a rejected row (S044) for a different reason; it was not re-opened here, and no page sentence in the two named sources states it.

## Probe-rule and tooling record

- Files read in the lane: `corpus/SOURCES.md` (registry header, rows, Paths, Search log, Leads), `corpus/lessons/round-16-verifier-spotcheck.md` (both named in the assignment/context), plus the report-directory listing to confirm the write target. No other lane file opened; no recursive search over the lane, fleet root or any tree; no repo tool executed; no git command needed; no commit.
- Web reads only (no writes): the two assigned git-scm.com pages and the two tag-pinned raw adoc files used solely to fix line anchors for the same text.
- Tool installs/updates: none.
