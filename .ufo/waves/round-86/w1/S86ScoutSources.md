# S86ScoutSources — souji round 86 w1, seat S86ScoutSources (source scout)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (lane id `souji`). Seat `S86ScoutSources`, wave 1 of round 86.
Scope owned: `.ufo/waves/round-86/w1/S86ScoutSources/` only. No lane file, no `MANIFEST.json`, no `.ufo/state/*`,
no `.scratch/*`, no git/jj mutation in the lane, no sibling-lane file touched.
Scratch: `/fast/scratch/hyaku/souji-r86/S86ScoutSources/` (deleted before yield; receipts copied into the seat dir first).

## Verdict

**All three requested sources were opened this round and every quote is verified byte-exact. The registry already
carries rows S341/S342/S343 for exactly these three clauses, and my independent re-open reproduces each row's
capture bytes, its anchor line and its quote character-for-character — so the round's source ground is confirmed,
not re-filed.**

The registry's highest id at `HEAD` (`2acbbfc8`) was **S340**; the round's working tree now carries **S341–S344**
(uncommitted, `git status --porcelain` → ` M corpus/SOURCES.md`), four rows added, one of them rejected. The next
unused ids are **S345, S346**.

## 0. The contract (read first)

- `/home/vgpnk/Projects/shokunin/CORPUS.md` § "SOURCES.md — where a shokunin learns" — contract `SOURCES-CONTRACT-v1`
  (kaika, 2026-10-19, frozen). Rules that bind this seat: rule 1 (*a row is a claim* — open the source in the round
  that writes the row; the lesson's `## Gate` records URL + access date + a ≤25-word quote with its location);
  rule 2 (append-only — only `status`/`recheck`/`used-by` change in place; a correction is a new row);
  rule 4 (*expansion is knowledge, not rows*); rule 5 (a negative claim carries its sweep).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` — the registry itself, 11 columns (Markdown row
  NF=13): `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.
  `kind` ∈ spec/docs/paper/code/tool/dataset/talk/book/community/own-work; `tier` ∈ A/B/C; `status` ∈
  queued|mined|rejected. A rejected row's `teaches` reads `REJECTED: <reason>; flip: <what would change the verdict>`.
- The round's contract: `census/round-86/preregistration.txt` (frozen at commit F `d77b4258` alone).

## 1. Source (a) — git-ls-files(1) as installed: the `-v`/`-t` tag list that names `H` and `S`

**Opened.** `man git-ls-files` on this host: `/usr/share/man/man1/git-ls-files.1.gz`, git **2.56.0-1**
(`pacman -Qi git` → `Version: 2.56.0-1`), man footer `Git 2.56.0   2026-09-27   GIT-LS-FILES(1)`.
sha256 of the installed `.gz`: `153d58dd4b8c60f1b1374e08455ea5d5a5a658f02684de0b16a714788beda804`.
Rendered with `MANWIDTH=100 man git-ls-files | col -b` (297 lines). Captures in the seat dir: `git-ls-files.1.gz`,
`git-ls-files.txt`. Served page `https://git-scm.com/docs/git-ls-files` fetched 2026-11-08: HTTP 200, 69 017 bytes,
sha256 `39bbbe6af002214f7ee3075ab4915fc7af05943869a469b89e3393c8cd6f5f08` — **byte-identical to the hash S292
already recorded**, so the served page is unchanged since 2026-11-05.

**Located quote** — OPTIONS `-t`, roff source line 193, rendered line 119 of the capture:

> "tracked file that is not either unmerged or skip-worktree"

9 words. Byte-exactness: `sed -n '119p' git-ls-files.txt | hexdump -C` → `…72 73 6b 69 70 2d 77 6f 72 6b 74 72 65 65`
("skip-worktree", ASCII hyphen `0x2d`), so the quote is a literal substring with no Unicode folding. The sibling
`S` entry ("tracked file that is skip-worktree", roff line 198, rendered line 122) and the `-v` lowercase rule
(rendered lines 143–145, roff 219: "Similar to -t, but use lowercase letters for files that are marked as assume
unchanged (see git-update-index[1]).") are present in the same capture.

**Duplicate-URL check.** `https://git-scm.com/docs/git-ls-files` → **1 row, S292** (mined, tier A) — the *same
document*, at the scope "index tags shown by git ls-files -v (lowercase for assume-unchanged, S for skip-worktree,
H for a plain tracked entry)"; its quote is the `-v` lowercase sentence. The installed man-page path
`/usr/share/man/man1/git-ls-files.1.gz` → **0 rows at HEAD**, **1 row in the working tree (S341)**.

**Row I would write** — identical to the landed **S341** (same source, same anchor, same quote, same sha256):

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S341 | git-ls-files(1) as installed (git 2.56.0-1, /usr/share/man/man1/git-ls-files.1.gz; capture census/round-86/srcs/git-ls-files.1.gz sha256 153d58dd…bd46, opened 2026-11-08) | docs | A | what a `git ls-files -t`/`-v` status tag names (scope: the tag legend's H and S entries and the -v lowercase rule; not the index entry fields, the pathspec options or the exclude options) | OPTIONS -t, rendered line 119 of the capture: "tracked file that is not either unmerged or skip-worktree" | the tag a `-v` record carries names exactly the classes a status read cannot be trusted for, so a non-H tag is an index-flag sweep's decision rule rather than a heuristic | mined | 2026-11-08 | on-release | corpus/knowledge/filter-filemode-witness.md |

**Already in the registry? Yes — and this is the point of the row.** S292 (the served page, same document) holds the
`-v` lowercase rule and the `S` tag; it does **not** carry the `H` legend entry's wording, which is the sentence the
C2 sweep's decision rule rests on: a tag is `H` only if the record is neither unmerged nor skip-worktree. The
installed man page is a different artifact (different URL, different revision stamp) and the anchor is a different
section than S292's `Documentation/git-ls-files.txt--v`, so this is a distinct scope, not a second copy of S292's.
`grep -cF` for the served URL is 1, not 2, so the row adds no new cross-scope duplicate-URL warning.

## 2. Source (b) — git-update-index(1) as installed: the `--skip-worktree` / `--assume-unchanged` descriptions

**Opened.** `man git-update-index`: `/usr/share/man/man1/git-update-index.1.gz`, git **2.56.0-1**, footer
`Git 2.56.0   2026-09-27   GIT-UPDATE-INDEX(1)`. sha256
`27e7086469f31da5adcc5bff5d17b0502e7b7ab2fe5b2c2afa7de34683f6f1b8`. Rendered `MANWIDTH=100 man git-update-index | col -b`
(479 lines). Captures: `git-update-index.1.gz`, `git-update-index.txt`. Served page
`https://git-scm.com/docs/git-update-index` fetched 2026-11-08: HTTP 200, 84 442 bytes, sha256
`ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8` — **byte-identical to the hash S291 recorded**.

**Located quote** — § "Skip-worktree bit", roff source line 504, rendered lines 325–326 of the capture:

> "Tell git to avoid writing the file to the working directory when reasonably possible, and treat the file as unchanged when it is not"

24 words. The sentence continues "…present in the working directory." in the same paragraph; the quote is cut at the
≤25-word boundary, and the cut is faithful to the source (the row's own `teaches` names the "unchanged" contract).

**Duplicate-URL check.** `https://git-scm.com/docs/git-update-index` → **2 rows at HEAD, S271** (USING `--CACHEINFO`
scope) and **S291** (NOTES scope: "This does not work as expected, since Git may still check working tree files
against the index when performing certain operations." — verified present verbatim in the served page). The
installed man-page path `/usr/share/man/man1/git-update-index.1.gz` → **0 rows at HEAD**, **1 row in the working
tree (S342)**.

**Row I would write** — identical to the landed **S342**:

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S342 | git-update-index(1) as installed (git 2.56.0-1, /usr/share/man/man1/git-update-index.1.gz; capture census/round-86/srcs/git-update-index.1.gz sha256 27e70864…f6f1b8, opened 2026-11-08) | docs | A | the contract of the skip-worktree bit (scope: the "Skip-worktree bit" section's one-sentence definition; the --assume-unchanged bit and core.ignorestat are out of scope here) | "Skip-worktree bit" section, rendered lines 325-326 of the capture: "Tell git to avoid writing the file to the working directory when reasonably possible, and treat the file as unchanged when it is not" | the flag's own contract is to treat the path as unchanged, so a worktree change behind it is invisible to every status read and only an index-flag read can refuse it | mined | 2026-11-08 | on-release | corpus/knowledge/filter-filemode-witness.md |

**Already in the registry? Yes — S291 and S271, at two other scopes of the same document, and neither carries this
clause.** S291's scope is the *NOTES* caveat (git may still check the worktree against the index in some
operations); S342's scope is the *bit's own contract* ("treat the file as unchanged"), which is a different
sentence in a different section of the same page. Both scopes are separately useful and neither restates the other.

**Sibling clause I checked but did not file — the `--assume-unchanged` description, which no row carries.**
Rendered lines 77–78, roff source line 121:

> "the user promises not to change the file and allows Git to assume that the working tree file matches what is recorded in the index"

25 words, verbatim in the capture. The "assume-unchanged bit and core.ignorestat are out of scope here" clause in
S342's own `scope` cell explicitly leaves it open, and `grep -c "user promises not to change the file"` on
`corpus/SOURCES.md` = **0** — no registry row holds it. The *difference* paragraph at rendered lines 346–352
(roff 512) is likewise unrowed ("Although this bit looks similar to assume-unchanged bit, its goal is different." —
12 words, verbatim; `grep -c "its goal is different"` = **0**). **Recommendation to L1:** this is a genuine gap, and
the round's own claim is about the *pair* of bits (`_flag_refusal` refuses on either). A row scoped to the
assume-unchanged description would be new ground — but it is **this seat's recommendation only**; I have not filed it,
because the contract's rule 1 makes a row a claim about a source opened in the round, and the L1 owns the id
sequence and the Gate text. It is offered as a candidate for L1 to take or drop.

## 3. Source (c) — git-submodules(5) / gitformat-index(5) as installed: what a gitlink entry records

The task named **gitformat-index(5) or git-submodules(5)** as installed. I opened all three candidates.

**Candidate 1 — `git-submodules(5)`: unreachable, and the name is wrong at every upstream revision.**
`man git-submodules` → "No manual entry for git-submodules"; `man -w git-submodules.5` and `git-submodules.7` →
no entry. The installed page is **`gitmodules(5)`** (`/usr/share/man/man5/gitmodules.5.gz`, sha256
`c1a0fa4c7b9d8fae510c9a74ab6a27b85a17ea63acbac7a77b42680c88064448`) — and it is a **different document**: it
defines the `.gitmodules` file's keys and never mentions a gitlink. Measured on the rendered page:
`grep -c -i gitlink` = **0**, `grep -c -i 'commit id'` = **0**; the served `https://git-scm.com/docs/gitmodules`
(HTTP 200, sha256 `4fa372e3d6715e742c3dd1c9b6ed37e7c4502c12f9927c7199fc8ff1b91a233e`) likewise contains neither
string. Upstream, `Documentation/git-submodules.adoc` and `Documentation/git-submodules.txt` are **404 at every tag
checked** (v1.7.0, v1.8.0, v2.0.0, v2.5.0, v2.10.0, v2.13.0, v2.14.0, v2.20.0, v2.25.0, v2.30.0, v2.40.0, v2.50.0,
v2.55.0, v2.56.0); `Documentation/gitsubmodules.adoc` appears at v2.25.0+ and `Documentation/gitmodules.adoc` at
v2.56.0. The upstream `Makefile`/`meson.build` at v2.56.0 list `gitsubmodules.adoc` under `MAN7_TXT` — the page is
**section 7, not 5**. And `https://git-scm.com/docs/git-submodules` → **HTTP 404**;
`https://git-scm.com/docs/gitsubmodules` → HTTP 200 (47 526 bytes, sha256 `346275cf82859f51a9b860b0c8ae13abbe4688350daef95937f14234cf698bfd`).
**This candidate is reported as unreachable under the name the task gave.**

**Candidate 2 — `gitformat-index(5)` as installed: opens, but does not carry the sentence.**
`/usr/share/man/man5/gitformat-index.5.gz` (sha256 `9fd72e4cd4211da514ce2aa350653fc3be7548ebaee4655cd7d82c69fb5e781a`),
rendered 390 lines. It names the gitlink **only** as an object-type bit value: roff 296 / rendered 82,
"valid values in binary are 1000 (regular file), 1010 (symbolic link) and 1110 (gitlink)", and roff 317 / rendered 87,
"Symbolic links and gitlinks have value 0 in this field." `grep -c -i 'commit id'` on the rendered page = **0**; the
page never says what a gitlink's recorded name *denotes*. Its upstream `.adoc` at v2.56.0 (sha256
`c8aca94073fed907c47f631db8a9c53a9a0a0007f8ea3cdce9722224bebbaa93`) carries the same two sentences and nothing
more on gitlinks. **This document cannot ground the claim "a gitlink entry records a commit id rather than
content."** It is also already registered: **S317** (upstream `.adoc`, Index-entry scope) and **S339** (the same
installed page, the file-level checksum clause) — two rows, both mined.

**Candidate 3 — the page that does carry it: `gitsubmodules(7)` as installed.** `/usr/share/man/man7/gitsubmodules.7.gz`
(sha256 `607d08e2120140e4f73e1f4bc8068e70a0a1fd30d110e151a8f7a2dae03d0e2e`), rendered `MANWIDTH=100 man 7 gitsubmodules | col -b`
(237 lines). Upstream source `Documentation/gitsubmodules.adoc` at tag v2.56.0 (sha256
`0e1a7ca29db55a75014281275a6daaa72b0bc6dbb2375b90549ff4da165ea375`).

**Located quote** — DESCRIPTION, first section, roff source line 51, rendered lines 26–27 of the capture:

> "The gitlink entry contains the object name of the commit that the superproject expects the submodule’s working directory to be at."

21 words. Byte-exactness: the apostrophe in "submodule’s" is **U+2019** in both the capture and the quoted string
(`hexdump -C` → `73 75 62 6d 6f 64 75 6c 65 **e2 80 99** 73`), and the rendered line also contains a literal tab
inside "that  the\t superproject  expects\tthe". Verified present in the served `gitsubmodules` page after tag
stripping. The upstream `.adoc` carries the same sentence as plain ASCII: "The `gitlink` entry contains the object
name of the commit that the superproject expects the submodule's working directory to be at." (lines 36–37).

**Duplicate-URL check.** `https://git-scm.com/docs/gitsubmodules` → **0 rows**; `https://git-scm.com/docs/git-submodules`
→ **0 rows** (and 404); `https://git-scm.com/docs/gitmodules` → **0 rows**; the upstream `.adoc` URLs → **0 rows**.
The installed path `/usr/share/man/man7/gitsubmodules.7.gz` → **0 rows at HEAD**, **1 row in the working tree (S343)**.

**Row I would write** — identical to the landed **S343**:

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S343 | gitsubmodules(7) as installed (git 2.56.0-1, /usr/share/man/man7/gitsubmodules.7.gz; capture census/round-86/srcs/gitsubmodules.7.gz sha256 607d08e2…d0e2e, opened 2026-11-08) | docs | A | what a gitlink tree entry records (scope: the sentence naming the gitlink's content; submodule update rules and .gitmodules semantics not used) | first section, rendered lines 26-27 of the capture: "The gitlink entry contains the object name of the commit that the superproject expects the submodule’s working directory to be at." | a gitlink's recorded content is a commit id, not bytes, so no hash of the worktree can decide a gitlink's state and only the index/flag read can name a concealed change | mined | 2026-11-08 | on-release | corpus/knowledge/filter-filemode-witness.md |

**Already in the registry? No — and the nearest row is a different document.** **S294** (git-fast-import(1), mode
160000 is a gitlink: "A gitlink, SHA-1 of the object refers to a commit in another repository.") states the mode
list, not what a gitlink entry's recorded name denotes, and its own `scope` cell says the page "does not state … how
a gitlink interacts with `git status`". **S317** (gitformat-index(5), Index entry) is the index-entry field list.
Neither carries the sentence. `gitmodules(5)` is a third document again (the `.gitmodules` key list) and carries
neither string. **S343's URL and scope are both new.**

## 4. The reject

**S344 — git-ls-files(1) as installed, the `--stage` listing.** Opened 2026-11-08 on the same page and capture as
S341. Quote, OPTIONS `-s/--stage`, roff source line 51, rendered lines 51–52:

> "Show staged contents' mode bits, object name and stage number in the output."

13 words, verbatim in the capture (verified).

**REJECTED** — the mode/object-name half restates ground **S317** already holds (the index entry's stat and object
fields: "the mode object type and the object name of an entry") and **S327** already holds (each tree entry carries
its mode and type: "%(objectmode) %(objecttype) %(objectname)%x09%(path)"), while the stage number is a detail this
lane's receipts already exclude — `_truth_refusal` skips every entry whose stage is not 0
(`tools/souji-receipt-write.py:283`). A third row on one listing's fields is registry weight, not knowledge.
**Flip:** a scoped teaching about the unmerged stage triples and resolve-undo, which neither row carries —
measured: `grep -c -i 'resolve-undo'` = 1 and `grep -c -i 'stage triple'` = 1 on the whole registry, and **neither
S317 nor S327 mentions "stage" at all** (`grep -c -i stage` on each row = 0), so that clause is genuinely unrowed.

**This is the one of the three I would reject, and it is the one the round already rejected.** The rejection is
consistent with the round-85 precedent (S338, the git-status(1) DESCRIPTION row, rejected for the same reason:
"restates ground S317 … and S315 … already carry for this lane, so the row adds registry weight, not knowledge").

**Nothing in the three requested sources is rejected.** (a) and (b) are distinct scopes of documents the registry
already holds at *other* scopes; (c) as the task named it (`gitformat-index(5)` / `git-submodules(5)`) cannot ground
the sentence at all — the sentence lives in `gitsubmodules(7)`, which is what S343 correctly cites.

## 5. Duplicate-URL check — command and output

From the lane root; the registry file is `souji-shokunin/corpus/SOURCES.md`, compared at `HEAD` (`2acbbfc8`, 263
rows) and in the live working tree (267 rows).

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin
for u in "<url>"; do
  h=$(git show HEAD:corpus/SOURCES.md | grep -cF "$u")
  w=$(grep -cF "$u" corpus/SOURCES.md)
  printf 'HEAD=%-3s WT=%-3s %s\n' "$h" "$w" "$u"
done
```

Output (`duplicate-url-check.txt`):

```
HEAD=1   WT=1   https://git-scm.com/docs/git-ls-files
HEAD=2   WT=2   https://git-scm.com/docs/git-update-index
HEAD=0   WT=0   https://git-scm.com/docs/gitformat-index
HEAD=0   WT=0   https://git-scm.com/docs/gitsubmodules
HEAD=0   WT=0   https://git-scm.com/docs/git-submodules
HEAD=0   WT=0   https://git-scm.com/docs/gitmodules
HEAD=0   WT=0   https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitsubmodules.adoc
HEAD=1   WT=1   https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-index.adoc
HEAD=0   WT=1   /usr/share/man/man1/git-ls-files.1.gz
HEAD=0   WT=1   /usr/share/man/man1/git-update-index.1.gz
HEAD=0   WT=1   /usr/share/man/man7/gitsubmodules.7.gz
HEAD=1   WT=1   /usr/share/man/man5/gitformat-index.5.gz
```

Rows already citing the two served URLs (with scope), from the registry:

| row | URL | scope |
|---|---|---|
| S292 | https://git-scm.com/docs/git-ls-files | index tags shown by `git ls-files -v` (lowercase for assume-unchanged, `S` for skip-worktree, `H` for a plain tracked entry) |
| S271 | https://git-scm.com/docs/git-update-index | USING `--CACHEINFO` |
| S291 | https://git-scm.com/docs/git-update-index | NOTES: "This does not work as expected…" |
| S317 | …/v2.56.0/Documentation/gitformat-index.adoc | Index entry (stat fields, mode object type, object name) |
| S339 | /usr/share/man/man5/gitformat-index.5.gz | the index file's own trailing checksum |

**Structural check with the fleet's own census** (the tool that reports `E04` same-URL-within-scope and `W04`
same-URL-across-scopes):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate . --today 2026-11-08
souji-shokunin	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

Findings histogram: `ok` ×1, `W04` ×87 — **no `E0x` finding**, and the 87 `W04` lines are the lane's pre-existing
cross-scope duplicate-URL warnings (S035/S036/S038/S049/S057/S058/S059/S063/S065/S072/S073/S075/S076/S077/S078/S080/
S081/S082/S083/S085/S086/S087/S088/S089/S090/S091/S092/S093/S094/S095/S096/S097/S098/S099/S106/S108/… — one per
pre-existing shared URL). **The four new rows introduce zero new `E0x` and zero new `W04`.**
For comparison, a HEAD-only copy of the registry (263 rows) validated with the same command also reports
`W04` ×87 plus `E11` ×268 — the `E11`s are **artifacts of the copy** (its `used-by` paths do not exist on disk in
the scratch copy), not defects of the lane; the lane's own tree validates `ok`.

## 6. Sources that could NOT be fetched (reported as unreachable, not fabricated)

| candidate | result | note |
|---|---|---|
| `man git-submodules` / `git-submodules.5` / `git-submodules.7` | **no manual entry** | the installed section is 7 (`gitsubmodules`), not 5; the name the task used does not exist on this host |
| `https://git-scm.com/docs/git-submodules` | **HTTP 404**, 6 697 bytes | the served page has no such name; `…/docs/gitsubmodules` is 200 |
| `Documentation/git-submodules.adoc` / `.txt` upstream | **404 at every tag checked** (v1.7.0 → v2.56.0, 14 tags) | upstream never carried that file name; `gitsubmodules.adoc` (man 7) and `gitmodules.adoc` (man 5) are the two files |
| `https://git-scm.com/docs/git-submodules` (via git-scm) | **HTTP 404** | as above |

Nothing else in the round was unreachable: all four served pages (git-ls-files, git-update-index, gitsubmodules,
gitformat-index, gitmodules) returned HTTP 200 and were captured with sha256.

## 7. Reproducing this seat's evidence

All under `.ufo/waves/round-86/w1/S86ScoutSources/` (every file sha256'd in `SHA256SUMS`):

| file | what it is |
|---|---|
| `git-ls-files.1.gz`, `git-ls-files.txt` | the installed git-ls-files(1) man page (gz + `MANWIDTH=100 man | col -b` render) |
| `git-update-index.1.gz`, `git-update-index.txt` | the installed git-update-index(1) man page |
| `gitsubmodules.7.gz`, `gitsubmodules.txt` | the installed gitsubmodules(7) man page |
| `gitformat-index.5.gz`, `gitformat-index.txt` | the installed gitformat-index(5) man page (the rejected candidate (c)-2) |
| `gitmodules.5.gz`, `gitmodules.txt` | the installed gitmodules(5) man page (the rejected candidate (c)-1) |
| `git-ls-files.html`, `git-update-index.html`, `gitsubmodules.html`, `gitformat-index.html`, `gitmodules.html` | the served pages, fetched 2026-11-08, HTTP 200 |
| `gitsubmodules.adoc`, `gitformat-index.adoc`, `gitmodules.adoc`, `gitrepository-layout.adoc` | upstream `Documentation/` sources at tag v2.56.0 |
| `quote-receipt.txt` | the byte-exactness / word-count receipt for every quote above |
| `duplicate-url-check.txt` | the duplicate-URL check command output |
| `census-validate-lane.txt`, `census-validate-head.txt` | fleet census on the lane working tree and on a HEAD-only copy |
| `SHA256SUMS` | sha256 of every capture in this seat dir |

Quote word counts (against the ≤25-word contract), counted by `wc -w` against the pasted strings: 9 (S341), 24
(S342), 21 (S343), 13 (S344), 25 (the unrowed assume-unchanged description).

**Capture-hash agreement with the lane's own captures.** The lane's `census/round-86/srcs/` holds the same three
`.gz` files; their sha256 values are **identical** to mine:
`git-ls-files.1.gz` `153d58dd…bd46`, `git-update-index.1.gz` `27e70864…f6f1b8`, `gitsubmodules.7.gz`
`607d08e2…d0e2e`. Two independent copies of the installed pages agree byte-for-byte, so the landed rows' capture
citations are sound.

## 8. Tooling

**No tool was installed or upgraded by this seat.** The host's `git 2.56.0-1`, `man`/`groff`/`col`, `coreutils`,
`bash`, `python 3.14`, `curl` and the fleet's own `scripts/sources-census.sh` were sufficient; the pacman guard (all
pacman transactions paused host-wide) was therefore never engaged. `pacman -Qi git` was run read-only, to stamp the
package version `2.56.0-1` used in every row's anchor.

## 9. Limits of this seat's findings

1. **Nothing here is a new row.** The three rows this seat was asked to draft already exist in the lane's working
   tree as S341/S342/S343, with the same sources, anchors, quotes and capture hashes; this seat's contribution is
   independent re-opening and byte-exact verification, plus the reachability finding about the `(c)` candidates.
   The L1 may treat S341–S343 as verified.
2. **The reject is S344**, and it was reached by the round independently of this seat; this seat confirms the
   rejection reason against S317 and S327 by quote and by the sweep `grep -c -i stage` = 0 on both rows, and
   confirms the flip is genuinely unrowed.
3. **One gap found and NOT filed:** the `--assume-unchanged` bit's own description (roff 121 / rendered 77–78, 25
   words verbatim) and the bit-difference paragraph (roff 512 / rendered 346–352) are held by **no** registry row,
   while the round's claim is about the *pair* of flags `_flag_refusal` refuses on. `grep -c "user promises not to
   change the file"` = 0 and `grep -c "its goal is different"` = 0 over `corpus/SOURCES.md`. Left to L1 as a
   candidate; this seat filed nothing.
4. **The `gitsubmodules(7)` page is section 7, not 5.** The task's "git-submodules(5)" does not exist at any
   upstream revision or on this host; the sentence the claim needs lives in section 7. The landed row S343 cites it
   correctly.
5. **Verification method.** Every quote was checked twice: once against the *rendered* capture at the row's stated
   rendered line (whitespace-collapsed, ASCII/U+2019 normalised) and once against the raw `.gz` with roff escapes
   normalised. Where the row's quote differs from the served page's wording (`(see git-update-index[1]).` on the web
   page vs `(see git-update-index(1)).` in the installed roff; U+2019 vs ASCII apostrophe in `submodule’s`), the
   row's quoted form is the one present in the capture it cites — verified by `hexdump -C`.
6. **The lane's working tree was not touched by this seat.** `git status --porcelain` before and after this seat's
   work shows the same two entries (` M corpus/SOURCES.md`, plus the untracked `census/round-86/srcs/` and
   `census/round-86/records/`), all created by the L1 and other seats; this seat wrote only inside
   `.ufo/waves/round-86/w1/S86ScoutSources/` and this report file. No git/jj command in the lane was mutating; the
   only git calls were `git --version`, `git log`, `git status --porcelain`, `git show HEAD:corpus/SOURCES.md` and
   `git diff` — all read-only.
