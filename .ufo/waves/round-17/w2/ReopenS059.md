STATUS: DONE — S059 re-opened 2026-10-20: primary quote is verbatim, 18 words, at the named :69-71 anchor; tier/kind/status/opened/recheck agree; `teaches` DISAGREES (the page does name `git status`, in examples); `scope` needs one clarifying clause; the draft's duplicate-URL warning has no lane-side emitter.

# ReopenS059 — gitattributes(5), `$GIT_DIR/info/attributes` precedence

Scope: independent re-open of the S059 row drafted in `.ufo/waves/round-17/w1/SrcGitRepoLayoutAttrs.md` (single source: https://git-scm.com/docs/gitattributes). Page-level only; no claim about git's C reader. Advisory; L1 integrates.

## Source opened

| Item | Observed |
|---|---|
| URL | https://git-scm.com/docs/gitattributes |
| Opened | 2026-10-20 (this seat, direct fetch) |
| Version line served | `Latest version ▾ gitattributes last updated in 2.56.0`; menu entry `2.56.0 … 2026-09-28` (next: 2.55.0, 2026-06-29) |
| Pinned text used for line anchors | `Documentation/gitattributes.adoc` at tag `v2.56.0` (raw fetch succeeded; content matches the served page) |

The draft's version line — `web manual "gitattributes last updated in 2.56.0" (2.56.0 dated 2026-09-28), opened 2026-10-20` — is exactly what the page served. **Agree.**

## Primary quote audit

Drafted quote:

> When deciding what attributes are assigned to a path, Git consults `$GIT_DIR/info/attributes` file (which has the highest precedence)

Served page, same sentence continues:

> When deciding what attributes are assigned to a path, Git consults `$GIT_DIR/info/attributes` file (which has the highest precedence), `.gitattributes` file in the same directory as the path in question, and its parent directories up to the toplevel of the work tree (the further the directory that contains `.gitattributes` is from the path in question, the lower its precedence). Finally global and system-wide files are considered (they have the lowest precedence).

- **Verbatim:** holds. Every character through the closing parenthesis matches the served page (inline code markup only). The quote stops mid-sentence after a parenthetical; the omitted `, .gitattributes file …` does not change its meaning.
- **Presentation defect (minor):** the truncation is unmarked. A reader can take the closing paren for the sentence end. Smallest fix: append ` …` (or say "first clause of") — the full sentence is too long for the ≤25-word cap, so ellipsis is the correct form.
- **Length:** 18 words. Command: `printf '%s\n' 'When deciding what attributes are assigned to a path, Git consults \`$GIT_DIR/info/attributes\` file (which has the highest precedence)' | wc -w` → `18`. ≤25. Holds.
- **Anchor:** § DESCRIPTION of `Documentation/gitattributes.adoc` at `v2.56.0`, lines **69-71**. Independent grep of the tag-pinned adoc returned matches at `*69` (`When deciding what attributes are assigned to a path, Git`) and `*70` (`consults \`$GIT_DIR/info/attributes\` file (which has the highest`), with `precedence), .gitattributes file…` at `71`. The draft's `:69-71` is correct. Holds.

### Corroborating locators — all verified

| Draft claim | Verified at v2.56.0 adoc | Served page |
|---|---|---|
| EXAMPLES "Finally it examines `$GIT_DIR/info/attributes`." | `:1341` (`3. Finally it examines … This file is used to override the in-tree settings.`) | present, verbatim |
| EFFECTS "Currently, the following operations are attributes-aware." | sentence spans `:119-120` (governing sentence starts `:118`) | present, verbatim |
| NOTES symlink sentence | `:1304-1306` | present, verbatim |
| `check-attr` named as value reader | `:112`, `:113`; SEE ALSO `:1358` | present |
| `git status` only in end-of-line example | `:263`, `:267` | present, verbatim |

No statement about `git status` exists outside `:263`/`:267` (grep `git status` over the adoc: only those two hits). The draft's body already said this; see the `teaches` verdict, where the cell contradicts it.

## Cell verdicts

| Cell | Drafted value (abbreviated) | Verdict | Corrected text / basis |
|---|---|---|---|
| `source` (URL) | gitattributes(5) — https://git-scm.com/docs/gitattributes | **agree** | — |
| `kind` | docs | **agree** | Official Git manual page. |
| `tier` | A | **agree** | First-party git documentation; same URL is already tier A as S045 (`corpus/SOURCES.md:59` at ddb7347). The census's tier rule only flags `A`+`community` (`census/round-12/sources-census.sh:14`); no inflation here. Caveat: the `SOURCES-CONTRACT-v1` text is not present under `corpus/` (listing: README.md, SOURCES.md, QUALITY.md), so this verdict rests on precedent + first-party status, not on the contract's own wording. |
| `scope` | "that attribute lookup consults `$GIT_DIR/info/attributes` with the highest precedence; not which commands read attributes" | **agree, needs one clarifying clause** | The positive half is exact page text. The negative half is defensible only as "not an enumeration": the page *does* name consumers — `git check-attr` at :112-113 and SEE ALSO :1358, and `git status` in its end-of-line example at :263/:267. Corrected cell: **"that attribute lookup consults `$GIT_DIR/info/attributes` with the highest precedence; not an enumeration of which commands trigger attribute lookup (`git check-attr` is named at :112-113 and :1358; `git status` appears only in an example at :263, :267)"** |
| `anchor` | "gitattributes last updated in 2.56.0" (2026-09-28), opened 2026-10-20; DESCRIPTION :69-71; EXAMPLES :1341; NOTES :1304-1306; EFFECTS :119-120 | **agree; add the locators the corrected teaches cites** | Every listed locator checks out. Corrected cell: **"web manual \"gitattributes last updated in 2.56.0\" (2.56.0 dated 2026-09-28), opened 2026-10-20; § DESCRIPTION `Documentation/gitattributes.adoc:69-71` at tag v2.56.0; § EXAMPLES :263, :267, :1341; § NOTES :1304-1306; § EFFECTS :119-120; `check-attr` named :112-113, § SEE ALSO :1358"** |
| `teaches` | "Git consults … so any attribute lookup reads a repo-local file souji does not control; the page names no status invocation and its symlink rule covers only a worktree `.gitattributes`" | **DISAGREE** | Two clauses fail. (1) **"the page names no status invocation" is false**: the page names `git status` at `:263` (`$ git status        # Show files that will be normalized`) and `:267` ("If any files that should not be normalized show up in *git status*"). What is absent is a *doctrinal statement* that status performs attribute lookup — not the naming. S045 already words this correctly at `corpus/SOURCES.md:59`: "does not state a status invocation"; the draft strengthened it into a falsity. (2) **"any attribute lookup reads"** overstates the page's verb: the page says Git *consults* the file when deciding attributes; it never says the file is opened unconditionally (an absent file is not discussed) and never uses "read". "souji does not control" is a project inference, not page text. The symlink clause holds (:1304-1306 is scoped to "a `.gitattributes` file in the working tree"). Corrected cell: **"Git consults `$GIT_DIR/info/attributes` (highest precedence) when deciding a path's attributes, so the file is a repo-local input to attribute decisions; the page names `git check-attr` as a value reader (:112-113, SEE ALSO :1358) and mentions `git status` only in an end-of-line example (:263, :267) — it never states that status reads attributes; its symlink rule covers only a worktree `.gitattributes` (:1304-1306), and it states no file-type or link-count condition for the `info/attributes` file"** |
| `status` | mined | **agree, conditional on landing order** | `mined` is valid once `corpus/lessons/round-17.md` exists and cites the row for the doc-stated half. If the row is pasted before the lesson, use the draft's `queued` variant: the used-by census literally tests `[ -e "$p" ]` (`census/round-12/sources-census.sh:15-16`) and would print `missing: corpus/lessons/round-17.md`. Do not paste `mined`+lesson path while the path is absent. |
| `opened` | 2026-10-20 | **agree** | Opened independently today. |
| `recheck` | on-release | **agree** | Versioned web manual, latest 2.56.0; matches S045/S049/S050. |
| `used-by` | corpus/lessons/round-17.md | **agree as target; existence required** | Same census condition as `status`; the path must exist in the lane at paste time or the queued variant applies. |

## Contradiction check against the draft's claim text

Claim under audit: `$GIT_DIR/info/attributes` "is read by git for attribute lookup (so any status/check-attr call may open it)."

- Part 1 ("read by git for attribute lookup") — **holds at page level**, via the § DESCRIPTION quote.
- Part 2 ("any status call may open it") — **not stated**. `check-attr` is a named consumer (:112-113, :1358); `status` appears only in an example (:263, :267). The page's § EFFECTS list ("Currently, the following operations are attributes-aware", :118-120) enumerates *operations whose behavior attributes change* and contains no `git status` subsection — a counter-reading of the list as closed, not of the example. Keep the status path labelled inference, exactly as the draft's body already does.
- **File-type silence:** the only symlink statement on this page is :1304-1306, scoped to a worktree `.gitattributes`. Grep for `symbolic|symlink|hardlink|hard link|regular file|link count` over the adoc returns that single block. On the layout page the only symlink hit is `HEAD` (:136-137); the `info/attributes` entry (:228-230) states no write, regular-file or link-count requirement. So D2's refusal of a hardlinked/non-regular `info/attributes` is **stricter than documentation**, as the draft says. That disclosure should survive integration.

## Draft side claim that fails: the duplicate-URL warning

The draft's "Expected registry side effect" asserts the fleet census will warn `souji W04 S0?? duplicate url git-scm.com/docs/gitattributes across scopes`, exit 0, "of the class it already emits for S035/S036/S038/S049".

Observed:

- `git -C <lane> show ddb7347:tools/souji-census.sh | grep -n -i -E 'duplicate url|W04|SOURCES\.md'` → **exit 1, no output**. The main census contains no sources-registry handling at all (case-insensitive `SOURCES\.md|sources|registry|W04` also returns nothing).
- The lane's documented sources census, `census/round-12/sources-census.sh` (named at `corpus/README.md:32`), checks **duplicate IDs** (`:11-12`), enum/tier (`:14`), and mined used-by existence (`:15-16`). It has **no URL check and no `W04` code**.
- `git -C <lane> diff --stat ddb7347 -- corpus/SOURCES.md corpus/QUALITY.md corpus/README.md tools/souji-census.sh tools/souji-landing-gate.py census/round-12/sources-census.sh` → no output, so the greps above are the landed bytes.
- Duplicate URLs already coexist without any warning: S034/S038 (coreutils timeout) and S036/S049 (git(1)), `corpus/SOURCES.md:48,52,49,63` at ddb7347.

Verdict: the paragraph is **unverified from lane evidence**; if a fleet-level tool outside this lane emits it, the row must name that tool's path and line. Smallest fix: **delete the paragraph** — a second gitattributes row with a distinct scope follows the S034/S038 and S036/S049 precedent, and no lane census objects. Keep only the true half: the used-by existence check forces the `queued`→`mined` flip with the lesson.

## Optional second row (gitrepository-layout) — spot-check

- Version line served: `gitrepository-layout last updated in 2.49.0` with `2.49.1 → 2.56.0 no changes`, 2.49.0 dated 2025-03-14. Draft matches.
- `info/attributes` quote at `:228-230` matches verbatim, including `See also: linkgit:gitattributes[5]` on `:230`.
- **Anchor defect:** § `info` is at `:194-197` ("Additional information about the repository is recorded in this directory…"), not inside the draft's `:216-230`. Corrected optional-row anchor: **"§ info `Documentation/gitrepository-layout.adoc:194-197`, § info/attributes :228-230 at tag v2.56.0"**.
- Omission worth one clause (page-stated, :196-197): the `info` directory is ignored when `$GIT_COMMON_DIR` is set and `$GIT_COMMON_DIR/info` is used instead — relevant if the row is ever used to reason about linked worktrees. Not an overclaim; optional.

## Commands run and observed output

1. `read .ufo/waves/round-17/w1/SrcGitRepoLayoutAttrs.md` — full draft.
2. `read https://git-scm.com/docs/gitattributes` (+ `:301-1468`) — served version block and full page. Version line as recorded above; DESCRIPTION, EFFECTS, NOTES, EXAMPLES, SEE ALSO read verbatim.
3. `grep` over `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitattributes.adoc`:
   - pattern `deciding what attributes are assigned|does not follow symbolic links|Finally it examines|operations are attributes-aware|consults` → hits at `*69`, `*70`, `*120`, `*1304`, `*1341`.
   - pattern `check-attr` → `*112`, `*113`, `*1358`.
   - pattern `symbolic|symlink|hardlink|hard link|regular file|link count` → `*1304` only.
   - pattern `git status|attributes-aware|Certain operations` → `*118`, `*119`, `*120`, `*263`, `*267`.
4. `read https://git-scm.com/docs/gitrepository-layout` and `grep` its v2.56.0 adoc for `info/attributes|symbolic|hard ?link|regular file|Defines which attributes` → `*228-230`; symlink only `HEAD` `*136-137`; `grep '^info::|Additional information about the repository'` → `*194-197`.
5. `read corpus/SOURCES.md:1-60` and `:64-98`; `git show ddb7347:corpus/SOURCES.md | grep -n -E '^\| S0(34|35|36|38|41|42|43|44|45|46|47|49|50) '` → S045 at `:59`, S034 `:48`, S035 `:49`, S036 `:50`, S038 `:52`, S049 `:63`.
6. `grep` case-insensitive `duplicate|dupe` and `SOURCES\.md|sources|W04|registry` in `tools/souji-census.sh` (working tree) → only `compare file: duplicate repo` at `:1465`; second pattern no matches. Repeated against `git show ddb7347:tools/souji-census.sh` → **no output, exit 1**.
7. `grep` `duplicate|W0[0-9]|used-by|used_by|mined` in `census/round-12/sources-census.sh` → duplicate IDs `:11-12`, enum/tier `:14`, mined used-by `:15-16`.
8. `grep` `duplicate url|W04|SOURCES\.md` in `tools/souji-landing-gate.py` and `tools/souji-preservation-evidence.py` → no matches.
9. `git -C <lane> diff --stat ddb7347 -- corpus/SOURCES.md corpus/QUALITY.md corpus/README.md tools/souji-census.sh tools/souji-landing-gate.py census/round-12/sources-census.sh` → **no output** (working tree equals landing for every cited file).
10. `printf '%s\n' '<quote>' | wc -w` → `18`.

No git writes; no `jj`; no seat/verify/vault/quarantine tool executed; no network writes; no installs or upgrades; no `/var/tmp` work.

## Remaining unknowns

- `SOURCES-CONTRACT-v1` text was not found under `corpus/`; the tier-A verdict uses same-URL precedent and first-party status. If L1 holds the contract elsewhere, check its tier wording.
- Whether a fleet-level census outside this lane emits a duplicate-URL `W04` warning. Not reproducible from the two lane censuses; the draft's exact message template remains unsupported here.
- Git's C-level attribute reader (`attr.c` / `read_attr_from_file`) was not opened; file-type behavior for `$GIT_DIR/info/attributes` remains a doc-level silence, as scoped.
- Whether any given `git status` invocation reaches the attribute machinery: not stated by this page; the status path stays inference.

## Bottom line

The quote and every locator hold; the row's `tier`, `kind`, `status` (with landing order), `opened`, `recheck`, `used-by` agree. The **smallest fix** is one sentence: replace the `teaches` cell's "the page names no status invocation" with "mentions `git status` only in an end-of-line example (:263, :267), never as a stated consumer", change "reads" to "consults", and add the corresponding locators to `anchor` and the clarifying clause to `scope`. Delete the duplicate-URL warning paragraph or name its emitter. No code change is implied by the documentation.
