# W2SrcCountWt — re-open S122 (count-objects.c@v2.56.0) and S123 (git-worktree § REFS/§ DETAILS)

## Status
STATUS: PARTIAL — every S122 and S123 line number and quote survives against live bytes and snapshots; two attacks land: S123's anchor does not cover the § DETAILS quote the entry hangs on it, and S123's teaches cell plus entry item 4 hold only on the files ref backend.

## Evidence
Revisions: lane `master` = c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface; artifacts landed at 778747e (`git diff --stat 778747e master -- corpus/SOURCES.md corpus/knowledge/count-objects-linked-worktree-garbage.md census/round-24/sources/` → empty). Working tree carries an uncommitted edit to the entry (S121 source line, a GIT_COMMON_DIR precondition in item 7); it touches no S122/S123 citation. Host `git version 2.56.0`, `pacman -Q git` → `git 2.56.0-1`. Scratch `/var/tmp/souji-r24-W2SrcCountWt/` (removed at end). No tools installed.

| check | command | result |
|---|---|---|
| S122 live bytes | `curl -sSfL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/count-objects.c`; `cmp` vs snapshot | `IDENTICAL`; both sha256 `ec13ae40d087…e03e` = SHA256SUMS = row cell |
| S122 tag | `git ls-remote https://github.com/git/git 'refs/tags/v2.56.0^{}'` | `a018953688f1b10bddf91bff8747068f5f4746a4` = row cell |
| S122 URL | `curl -w %{http_code} https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c` | `200` |
| S123 live page | `curl -sSfL https://git-scm.com/docs/git-worktree` (98918 B), tags stripped, whitespace collapsed | `last updated in 2.56.0`; L140 quote count 1; L170 quote count 1; L144 sentence count 1 |
| S123 REFS paragraphing | live HTML `<div class="paragraph">` inside `id="_refs"` | 5 paragraphs; para 2 starts `In general, all pseudo refs`, para 4 starts `For example, main-worktree/HEAD` — same as snapshot L138/140/142/144/146 |
| S123 snapshot vs installed man | `MANWIDTH=100000 man -P cat git-worktree \| col -b`, `expand`, trailing-space strip, `diff` vs snapshot | only L1 and L277 differ (header/footer padding); body identical; man page owned by `git 2.56.0-1`; snapshot sha256 `624821a6…b51a` = row cell |
| ref-backend probe | `/var/tmp` repos `git init --ref-format={files,reftable}`, `worktree add --detach`, `update-ref refs/worktree/k HEAD`, `count-objects -v` in the linked worktree | files: private dir holds `refs/worktree/k`, `garbage: 2`; reftable: private dir holds `refs/heads` + `reftable/…ref`, no `refs/worktree`, `garbage: 1` |
| id collisions at tip | `git show master:corpus/SOURCES.md` ids ∩ `.ufo/waves/round-24/assimilation/staged-ids` | 15: S109–S123 (freeze record: 11) |

Line-by-line, S122 (snapshot = live bytes):

| cite (row/entry) | line | verbatim bytes | verdict |
|---|---|---|---|
| real_report_garbage L41-53 | 41 | `static void real_report_garbage(unsigned seen_bits, const char *path)` … L53 `}` | survives |
| entry item 6 "line 50", task 49-52 | 49-52 | `if (!stat(path, &st))` / `size_garbage += st.st_size;` / `warning("%s: %s", desc, path);` / `garbage++;` | survives (stat is L49, add L50) |
| loose_garbage/count_loose/count_cruft L55-82 | 55, 61, 77, 82 | `static void loose_garbage(const char *path)` … `static int count_cruft(` … `}` | survives |
| verbose gate L116-119 | 116-119 | `if (verbose) {` / `report_garbage = real_report_garbage;` / `report_linked_checkout_garbage(the_repository);` / `}` | survives |
| Gate ADMIT line 118 | 118 | `report_linked_checkout_garbage(the_repository);` | survives, verbatim |
| loose walk L121-122 | 121-122 | `for_each_loose_file_in_source(the_repository->objects->sources,` / `count_loose, count_cruft, NULL, NULL);` | survives |
| KiB print L151-152; Gate ADMIT line 152 | 151-152 | `strbuf_addf(&garbage_buf, "%lu",` / `(unsigned long)(size_garbage / 1024));` | survives, verbatim |
| entry "unless -H" | 105, 142-145 | `OPT_BOOL('H', "human-readable", &human_readable,` ; `strbuf_humanise_bytes(&garbage_buf, size_garbage);` | survives |
| garbage lines L161-162 | 161-162 | `printf("garbage: %lu\n", garbage);` / `printf("size-garbage: %s\n", garbage_buf.buf);` | survives |

S123 quotes (snapshot `census/round-24/sources/git-worktree.1.txt`):

| quote (entry Gate) | snapshot line | live page | verdict |
|---|---|---|---|
| "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared." | 140 (§ REFS para 2) | present, once | survives |
| "Within a linked worktree, $GIT_DIR is set to point to this private directory" | 170 (§ DETAILS, header L167) | present, once | survives as a quote; see Finding 3 |

## Findings
1. **S122 survives in full.** Snapshot `census/round-24/sources/git-v2.56.0-builtin-count-objects.c` is byte-identical to live raw at tag v2.56.0 (peel `a018953688f1…`). Every range in the row's anchor cell (L41-53, L55-82, L116-119, L121-122, L151-152, L161-162) and every entry cite (line 118, line 50, line 151-152, line 41-53, line 116-119) lands on the named code. Both Gate quotes match verbatim. Teaches cell ("each reported path adds 1 to garbage and its stat size to size_garbage, printed as the floored KiB of the sum") matches L49-52 and L152. Nuance, not a defect: L46-47 `if (!desc) return;` means a path whose seen_bits map to no message (`PACKDIR_FILE_PACK\|PACKDIR_FILE_IDX`, L35-37) is neither warned nor counted; "reported" in the row has to mean "passed the desc check". — `census/round-24/sources/git-v2.56.0-builtin-count-objects.c` L35-53.
2. **S123 quotes, line numbers, version and hash survive.** § REFS is L137-146 with para 2 at L140 and para 4 at L144, as the row says. Live paragraphing matches (5 paragraphs). The page reads "last updated in 2.56.0". The snapshot body equals the installed git 2.56.0-1 man page. — `corpus/SOURCES.md` L143 anchor cell "snapshot census/round-24/sources/git-worktree.1.txt § REFS L137-146 (para 2 L140, para 4 L144)".
3. **ATTACK — S123's anchor does not cover the § DETAILS quote attributed to it.** The entry's source line reads "S123 — https://git-scm.com/docs/git-worktree — § REFS, § DETAILS" (`corpus/knowledge/count-objects-linked-worktree-garbage.md` L4). Its Gate ADMITs the § DETAILS sentence at snapshot L170 (entry L138), and item 3 cites "(S123 § DETAILS, § REFS)" (entry L35). But the S123 row's title is "git-worktree(1) § REFS", its scope cell scopes it to "the per-worktree refs directory of a linked worktree at git 2.56.0 (§ REFS)", and its anchor cell lists only "§ REFS paras 2 and 4 … L137-146". L170 is outside that span. The only rows anchoring § DETAILS are S003 (git 2.55.0, opened 2026-10-19, scope "git 2.55.0 worktree lock, prune and porcelain list") and S058 (scope "`extensions.worktreeConfig` read order only"). Neither row's scope covers "$GIT_DIR points to the private directory". So the § DETAILS claim has no row whose anchor and scope both cover it. The preregistration itself names the source as "git-worktree DETAILS" (`.ufo/waves/round-24/preregistration.txt` L72), not § REFS. The quote is true in live and snapshot bytes; this is a provenance-cell gap, not a falsified fact.
4. **Scope vs S003/S058: distinct by declaration, overlapping by section.** All three rows share the URL `https://git-scm.com/docs/git-worktree`. Declared scopes do not overlap: S003 covers lock/prune/`-n -v --expire`/porcelain `-z` at 2.55.0 (`corpus/SOURCES.md` L23). S058 covers "`extensions.worktreeConfig` read order only" (L78). S123 covers per-worktree refs (§ REFS) and excludes both by name: "not lock or prune behaviour (S003), not config.worktree read order (S058)" (L143). The overlap is at section level only: S003 and S058 both anchor § DETAILS, and the entry uses S123 for a § DETAILS sentence (Finding 3). If S123's anchor were widened to § DETAILS L170, its scope would still be topically distinct from both.
5. **ATTACK — S123's teaches cell and entry item 4 are files-backend-only, and the scope never says so.** S123 teaches: "a linked worktree's copies live at $GIT_COMMON_DIR/worktrees/<id>/refs". Para 4 states a ref-name equivalence ("worktrees/bar/refs/bisect/bad are the same as $GIT_COMMON_DIR/worktrees/foo/HEAD and $GIT_COMMON_DIR/worktrees/bar/refs/bisect/bad", snapshot L144). Para 5 adds "To access refs, it’s best not to look inside $GIT_DIR directly." (L146). The /var/tmp probe on git 2.56.0 shows the difference. On a `--ref-format=reftable` repository, a linked worktree's `refs/worktree/k` is stored under `worktrees/<id>/reftable/`, not under `refs/`, and `count-objects -v` reads `garbage: 1`. On the files backend the same steps read `garbage: 2`. So the entry's item 4 bullet "a `refs/worktree/*` ref reads `garbage: 2`" (entry L49) and its "contributes 2 or 3" (item 7) hold only on the files backend. The entry never mentions a backend: `grep -n 'reftable\|ref backend\|ref-format'` returns no hit, and "What this does NOT establish" has no such limit. The `refs` trigger in item 3 survives on both backends (reftable still creates the private `refs` directory, reading `garbage: 1`). The census rule in item 7 is unaffected. [INFERENCE: refs/bisect and logs/refs/* behave the same way under reftable; only refs/worktree was probed.]
6. **Note (owned by W2Collisions) — the new id collisions are not recorded.** Lane ids S120–S123 now also collide with staged ids S120–S123. The collision count at the tip is 15 (S109–S123), against "collisions 11" at freeze (`preregistration.txt` L130). W1 asked for this: "Mint lane ids, re-point citations by document as in r22 … and record the new collision count." (`.ufo/waves/round-24/w1/ReviewQualityBar.md` L59). A `git grep` at 778747e finds no updated count. `census/round-24/records/quarantine-slice` L2 (" S123   `payload-absent`") names the register's S123 with no in-file header. Only the sibling `slice-verdicts.tsv` header disambiguates it ("ids below are campaign register ids … NOT lane registry ids").

## Attack log
- A1 S122 snapshot ≠ live bytes → cmp IDENTICAL, sha equal → **survives**.
- A2 S122 tag commit wrong → ls-remote peel equals row → **survives**.
- A3 S122 line ranges/quotes drift (118, 49-52, 151-152, 41-53, 55-82, 116-119, 121-122, 161-162) → all land on named code verbatim → **survives**.
- A4 S123 quotes absent live or misplaced in snapshot → both present once live; L140 and L170 in snapshot; para 2/4 indices correct live and in snapshot → **survives**.
- A5 S123 snapshot ≠ installed 2.56.0 man page → body identical (header/footer padding only) → **survives**.
- A6 S123 anchor covers every S123 use → § DETAILS L170 is outside L137-146 and outside the row's § REFS scope → **lands** (Finding 3).
- A7 S123 scope distinct from S003/S058 → declared scopes are disjoint; overlap only at § DETAILS section level → **survives with a caveat** (Finding 4).
- A8 S123 teaches and entry item 4 hold for any ref backend → reftable reads `garbage: 1` with no private `refs/worktree` → **lands** (Finding 5).
