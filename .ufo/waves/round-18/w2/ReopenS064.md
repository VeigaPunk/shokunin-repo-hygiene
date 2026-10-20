STATUS: DONE — S064 quote is verbatim (token-exact, 13 words) and its teaches claim is true at tag v2.56.0; two anchor-cell nits, no overreach, no retraction.

# Reopen S064 — git attr.c at v2.56.0

## Attacked claim
`corpus/lessons/round-18.md` Gate S064 quote is verbatim from
`raw.githubusercontent.com/git/git/v2.56.0/attr.c`, anchored at attr.c:702-705 with fstat at
:712-718; the `corpus/SOURCES.md` S064 row (scope / anchor / teaches) does not overreach.

Pinned revision read: `git -C <lane> show 5efb519f00075d958c3d1109ef6fcb24c487eb87:corpus/{SOURCES.md,lessons/round-18.md}`
(HEAD == 5efb519f00075d958c3d1109ef6fcb24c487eb87; tracked tree clean). SOURCES row at line 82,
lesson quote at line 32.

## Served version / last-updated
- `curl -sS -D /var/tmp/s064-hdr.txt -o /var/tmp/s064-attr.c https://raw.githubusercontent.com/git/git/v2.56.0/attr.c`
  → `HTTP/2 200`, `content-length: 35118`, `etag: "a520a41ea80bc1a637c2848a9a51fd4996f967796dd2421643c947f69fbba8b0"`,
  `date: Tue, 20 Oct 2026 21:17:35 GMT`, `cache-control: max-age=300`.
  **raw.githubusercontent serves no version or Last-Modified line** (HEAD request repeats: only
  etag/date/content-length); the version identity therefore rests on the tag URL, which I pinned:
- `git ls-remote https://github.com/git/git refs/tags/v2.56.0 'refs/tags/v2.56.0^{}'`
  → tag object `2478544319491bbd2a42cc57a83e3d2f4730a280`, peeled commit `a018953688f1b10bddf91bff8747068f5f4746a4`.
  API `git/tags/2478544…`: `tag v2.56.0`, tagger `2026-09-28T04:20:13Z`, object type commit.
- Digest identity: served file `sha256 c5d49ce3f01cc99c79997426c0d06687a231a1f97a68e1b9b21f520d8bc300f1`,
  byte-identical (`cmp` IDENTICAL; same sha256) to (a) the raw URL at the peeled commit
  `…/a0189536…/attr.c` and (b) `attr.c` inside `codeload.github.com/git/git/tar.gz/refs/tags/v2.56.0`.
  So the tag URL served the tag's bytes, not a later branch.
- Last commit touching `attr.c` reachable from v2.56.0 (`api.github.com/repos/git/git/commits?path=attr.c&sha=v2.56.0&per_page=1`):
  `e49c0e898a540577c42ee3693368a273534dc9eb`, committer date `2026-07-06T22:50:19Z`,
  subject `Merge branch 'ps/setup-drop-global-state'`.
- `git --version` → `git version 2.56.0`: the row's "tag v2.56.0 = host git 2.56.0" is accurate.

## Located anchor and quote
Source lines, verbatim (leading tabs shown as `\t`):
```
702: \tif (flags & READ_ATTR_NOFOLLOW)
703: \t\tfd = open_nofollow(path, O_RDONLY);
704: \telse
705: \t\tfd = open(path, O_RDONLY);
```
- Normalization check (strip leading whitespace per line, join with one space) equals the lesson
  string **exactly** (`normalized == quote: True`). Wording and punctuation are token-identical,
  nothing elided; only the 4-line layout is collapsed to one line, which the `:702-705` anchor
  discloses. Quote is verbatim at token level, not byte level (no newline/tab retention).
- `printf '%s' '<quote>' | wc -w` → **13**, matching the lesson's "(attr.c:702-705, 13 words)".
- fstat: `712: if (fstat(fd, &st)) {`, failure block ends `716: }`; `717-718` are the
  `ATTR_MAX_FILE_SIZE` check, not fstat. The lesson's "fstat follows at :712-718" is 2 lines wide:
  exact span is **:712-716**. Nit only; fstat does follow the open at :712.

## SOURCES.md S064 row (5efb519, line 82) — cells
Scope: "how git opens $GIT_DIR/info/attributes and .gitattributes; not which commands consult
attributes" — accurate and self-limiting; teaches says nothing about `.gitattributes` (under-claim,
not overreach) and does not collide with S045 (line 63: gitattributes docs, filter-driver scope).

Anchor: "read_attr_from_file :699-718, bootstrap_attr_stack :940-948".
- `read_attr_from_file` is defined at **693-733**; :699 is `int lineno = 0;`, i.e. the window
  starts 6 lines *after* the signature and lands mid-struct-decl. It does contain open (:702-705)
  and fstat (:712), so no line number is false — but a reader landing at :699 sees no function
  name. Precision nit; smallest fix `:693-721` (or `:702-712`).
- `bootstrap_attr_stack :940-948` is exactly the info frame (`/* info frame */` through `}`). Correct.
  Missing from the cell: `915: unsigned flags = READ_ATTR_MACRO_OK;` — the line that decides the
  branch for info/attributes. With only :940-948 plus the quote, the branch is not derivable.

Teaches: "info/attributes is opened with a plain blocking open(path, O_RDONLY) and fstat runs only
after it, so a FIFO there blocks git inside open(2) before any type check — no pre-open guard in git".
- Confirmed branch: `bootstrap_attr_stack` sets `flags = READ_ATTR_MACRO_OK` (:915; no
  READ_ATTR_NOFOLLOW) and passes flags unchanged to `read_attr_from_file(git_path_info_attributes(), flags)`
  (:941-942) → else branch `705: fd = open(path, O_RDONLY);`. No `O_NONBLOCK`, no pre-open stat.
- Ordering confirmed: `711: fp = xfdopen(fd, "r")` (no type check) → `712: fstat` →
  `717: st.st_size >= ATTR_MAX_FILE_SIZE`. The only fifo/type-relevant calls in attr.c are the
  post-open fstat at :712 and the lstat at :1277, which is `builtin_object_mode_attr` on the
  *queried path*, not on the attributes file. attr.c has no pre-open guard for the attributes file.
- "no pre-open guard in git" tested tree-wide on the v2.56.0 tarball: `git_path_info_attributes`
  occurs only at `attr.c:896` (GIT_PATH_FUNC definition) and `attr.c:942` (the sole call);
  `INFOATTRIBUTES_FILE` is `environment.h:28 "info/attributes"`; `read_attr_from_file`'s five call
  sites are all in attr.c (855, 857, 926, 932, 942); `grep -rn "lstat(.*attr|stat(.*attr" --include=*.c`
  → no matches. The universal is supported for this tag, so it is not overreach — though the source
  is one file, so "in attr.c" would be the tighter phrasing (digest pin keeps it checkable).
- Tier A as implementation source at a named upstream tag matches the S054 precedent; row is unique
  (71 source rows, one S064 at line 82).

## Commands run (all read-only)
```
curl -sS -D /var/tmp/s064-hdr.txt -o /var/tmp/s064-attr.c https://raw.githubusercontent.com/git/git/v2.56.0/attr.c
curl -sS -o /var/tmp/s064-attr-peeled.c https://raw.githubusercontent.com/git/git/a0189536…/attr.c
curl -sSL -o /var/tmp/s064-git.tar.gz https://codeload.github.com/git/git/tar.gz/refs/tags/v2.56.0
git ls-remote https://github.com/git/git refs/tags/v2.56.0 'refs/tags/v2.56.0^{}'
git -C <lane> show 5efb519f00075d958c3d1109ef6fcb24c487eb87:corpus/SOURCES.md
git -C <lane> show 5efb519f00075d958c3d1109ef6fcb24c487eb87:corpus/lessons/round-18.md
sha256sum /var/tmp/s064-attr.c /var/tmp/s064-attr-peeled.c /var/tmp/s064-src/attr.c
grep -rn "git_path_info_attributes|INFOATTRIBUTES_FILE|read_attr_from_file" --include='*.c' --include='*.h' /var/tmp/s064-src
```
No lane file was written except this report; nothing was installed (no tool/version change to record);
the /var/tmp tarball and extraction tree were deleted after the checks.

## Verdict
**Agree — holds.** Quote is verbatim (13 words, no elision), :702-705 and :712 are the right lines,
and the row's teaches claim is true at tag v2.56.0 including the tree-wide "no pre-open guard".
No cell overreaches; scope is properly narrow and disjoint from S045.

Smallest fix (cosmetic, one cell + one span): SOURCES.md S064 anchor `read_attr_from_file :699-718`
→ `:693-721; flags=READ_ATTR_MACRO_OK :915`; lesson `fstat follows at :712-718` → `:712-716`.
