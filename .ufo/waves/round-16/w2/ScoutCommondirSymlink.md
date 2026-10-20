# Scout — symlinked `$GIT_DIR/commondir`: git's resolution vs `tools/souji-census.sh`

Round 16 / wave 2 / FALSIFY. Scope: recon only, source-level. No repo was built, no git command
was run against a fixture, and the census was not executed (probe rule). Every census-behavior
statement below is a static reading of the named file at the bytes under test; the two places that
depend on unexecuted kernel/bash semantics are marked `[INFERENCE]`.

Lane bytes: `tools/souji-census.sh` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`
(1877 lines), identical in the working tree, in `0a70bef`, and at lane HEAD. Lane HEAD moved
during the probe (first observation `a6ec7810…`, later `163158a7…`); `git diff --stat 0a70bef HEAD
-- tools/souji-census.sh` is empty, so the file under review is unchanged by that move.

## Verdict

| Claim | Verdict |
|---|---|
| git follows a symlinked `$GIT_DIR/commondir` and reads the link target's **content** | **holds** — existence is `lstat` (the link itself counts), then `open()` by name follows it |
| census comment "Read a symlinked commondir through its guarded target, as git does" (795, 836, 878) | **holds** for a readable regular target; the bytes read are the bytes git reads |
| census matches git for malformed/broken commondir shapes | **partial** — 5 divergences (D1–D5); all fail-closed, but D1 and D2 abort the whole run |
| C1 summary "only a protected reach exits 2 whole-run" | **partial** as literally stated: D1 (CRLF) and D2 (out-of-gitdir commondir symlink) both exit 2 whole-run without a protected reach. D2 is documented in the tool header (lines 84–86); D1 is not |
| the three `-L "$common"` branches are covered by the scored suites | **fails (gap)** — zero `commondir` occurrences in the r15 fixture; selftest writes only regular `../..\n` files |
| any under-guard (git reads a protected path that census does not guard) via this path | **none found** |

## 1. How git resolves it (observed facts)

All URLs accessed 2026-10-20. Line numbers are for `master`; the identical `get_common_dir_noenv`
block is present in the released `v2.52.0` tag (read at `setup.c` 318–348, same statements).
The host git is 2.56.0 per `corpus/SOURCES.md` row S049 (not re-checked by me).

`get_common_dir_noenv` — https://raw.githubusercontent.com/git/git/master/setup.c (lines 325–343):

- `strbuf_addf(&path, "%s/commondir", gitdir);` — the file is looked up under `$GIT_DIR`.
- `if (file_exists(path.buf)) {` → `if (strbuf_read_file(&data, path.buf, 0) <= 0) die_errno(_("failed to read %s"), path.buf);`
  Quote: `"if (strbuf_read_file(&data, path.buf, 0) <= 0) die_errno"` (13 tokens).
- trailing strip: `"data.buf[data.len - 1] == '\n' || data.buf[data.len - 1] == '\r'"` (14 tokens) —
  a loop that removes **only** trailing LF/CR. No leading or trailing space trim.
- `"if (!is_absolute_path(data.buf)) strbuf_addf(&path, "%s/", gitdir);"` (11 tokens) then
  `"strbuf_add_real_path(sb, path.buf);"` (5 tokens) — relative content is joined to `$GIT_DIR` and
  the result is physicalised.

`file_exists` is **lstat** — https://raw.githubusercontent.com/git/git/master/dir.c (lines 3204–3208):
`"int file_exists(const char *f) { struct stat sb; return lstat(f, &sb) == 0; }"` (17 tokens).
A symlink — including a dangling one — therefore satisfies the predicate.

`strbuf_read_file` opens **by name** — https://raw.githubusercontent.com/git/git/master/strbuf.c
(lines 776–794): `"fd = open(path, O_RDONLY); if (fd < 0) return -1;"` (13 tokens). `open()` follows
the symlink, so git reads the link target's contents. `strbuf_read` returns `-1` when `read()` fails
(strbuf.c 533–549), so a symlink to a directory (open succeeds, read fails EISDIR) `[INFERENCE]`
and a dangling link (open ENOENT) both make git die at setup.c:330. A 0-byte regular file makes
`strbuf_read_file` return `0`, which also satisfies `<= 0` → same die.

`strbuf_add_real_path` dies on an unresolvable path —
https://raw.githubusercontent.com/git/git/master/abspath.c (318–325):
`"strbuf_realpath(&resolved, path, 1);"` (die_on_error=1). In `strbuf_realpath_1` a missing
non-final component with `REALPATH_DIE_ON_ERROR` gives `die_errno("Invalid path '%s'", ...)`
(abspath.c 128–136); the doc comment says `"The directory part of path ... must denote a valid, existing directory"` (13 tokens).

Documentation — https://raw.githubusercontent.com/git/git/master/Documentation/gitrepository-layout.adoc:
`"If this file exists, $GIT_COMMON_DIR ... will be set to the path specified in this file"` (16 tokens)
and `"If the specified path is relative, it is relative to $GIT_DIR."` (13 tokens).

**Answer to the assigned question: yes.** Git follows a symlinked `$GIT_DIR/commondir` and reads the
target's content: `lstat` decides only that the named entry exists (a link counts, even dangling),
`open()` follows the link, and the content is then normalised (trailing CR/LF only), joined to
`$GIT_DIR` if relative, and `realpath()`ed. Failure to open/read is fatal, not "no commondir".

## 2. Census correspondence at HEAD

Three copies of the same block, all preceded by `guard_git_links "$dir"`:

- 766–804 `guard_worktree_registrations` (per linked-worktree admin dir): links at 791, `common=` 793, `-L` 794–797, read 799, leading trim 800, relative join 802, `guard_target` 803.
- 821–857 `guard_git_surface`, `$GIT_DIR` directory: links 830, `common=` 834, `-L` 835–838 (comment 836), read 840, trim 841, join 845, `guard_target` 847.
- 859–897 `guard_git_surface`, gitfile gitdir: links 872, `common=` 876, `-L` 877–880 (comment 878), read 882, trim 883, join 887, `guard_target` 889.

For a symlinked `commondir` whose target is a regular file, `guard_target` (466–470 → `resolve_guarded`
381–460) resolves the link physically, the census `read`s the resolved file, and joins relative
content to `$dir` — the *directory holding the link*, matching git's `$GIT_DIR` rule. So the comment
at 795/836/878 is accurate for this case, and the census is deliberately stricter: it prefix-checks
the link target against the protected roots **before** opening it.

Two structural caveats that narrow what the branch actually does:

1. **The branch is mostly unreachable for out-of-gitdir links.** `guard_git_links` (500–513) refuses
   any symlink in the gitdir that resolves outside it: `case "$resolved" in "$dir"/*) ;; *) protected_fail "git-metadata-symlink"` (511–512). A `commondir` symlink pointing at a shared file outside
   its own gitdir is legal for git but is refused whole-run before 796/837/879 run. So the `-L`
   branch only executes for links that resolve *inside* the same gitdir.
2. **The read is gated on `-f`, not on git's predicate.** `[ -f "$common" ]` (798, 839, 881) is not
   `lstat`-existence + `open`; see D3.

Also: the leading-whitespace trim at 800/841/883 (`target=${target#"${target%%[![:space:]]*}"}`) is
the idiom used for the gitfile `gitdir:` line at 865, but it is **not** git's commondir
normalisation — git trims only trailing CR/LF (see D4).

Attribution: `git log -S'Read a symlinked commondir'` → introduced by `0a70bef` (wave-1 integration);
`git log -S'guard_target git-common-dir'` → occurrence count changes in `48f8945` (r14), `b410186`
(r15) and `cbf688a` (r16 restore), so the behaviour predates wave 2; the "as git does" claim is new
wave-1 text.

## 3. Counterexamples and divergences (static, unexecuted)

**D1 — regular `commondir` with CRLF aborts the whole run (over-refusal; highest operability impact).**
File: `.git/worktrees/wt1/commondir` containing `../..\r\n` — a shape git accepts (setup.c 331–334
strips both CR and LF; common dir becomes the repo root).
Census path: 799 `IFS= read -r c < "$common"` removes the LF only, leaving `../..\r`
`[INFERENCE: bash read removes the delimiter and performs no CR translation; not executed under the
probe rule]`; 800 keeps it; 802 joins to `$admin`; 803 `guard_target` → `resolve_guarded` 396
`*$'\r'*) protected_fail "ambiguous-path" input` → `protected_fail` 200–207 prints
`souji-census: path-protected: ambiguous-path (...)` and `exit 2` — the entire fleet census dies on
one git-valid repository. The same happens through 840/847 (`$GIT_DIR` dir) and 882/889 (gitfile).
This is a new, undocumented contradiction of the C1 contract "only a protected reach exits 2
whole-run; could-not-evaluate → one `error` row".
Smallest fix: mirror git exactly at the three read sites — read the whole file and strip trailing
CR/LF in a loop (`c=$(<"$common")`, then strip `\n`/`\r` from the end) — or, minimally,
`c=${c%$'\r'}` immediately after each `read`, before 803/847/889.

**D2 — commondir symlink leaving its gitdir aborts the whole run (over-refusal; documented r14).**
File: `.git/worktrees/wt1/commondir -> ../../commondir.shared` (git reads it: `lstat` succeeds,
`open` follows). Census: 791 `guard_git_links "$admin"` → 511–512 `git-metadata-symlink` → exit 2
before the commondir branch. Header lines 84–86 state the r14 guard "still refuse[s] the whole run",
so the tool is self-consistent, but the wave-1 summary's "only a protected reach exits 2" is
imprecise for this layout. No protected read either way.
Smallest fix (optional, operability): exempt the literal leaf `commondir` from `guard_git_links`'
inside-gitdir rule and let 796/837/879 do the boundary check — `guard_target` there already refuses
a protected target, and the content is then guarded as in section 2. Keep the rule for every other
metadata symlink.

**D3 — `[ -f ]` vs git's `lstat`+`open` (fidelity gap; observable output unchanged).**
Shapes: dangling symlink (git: `lstat` true → open ENOENT → die, setup.c 328–330); symlink or plain
entry that is a directory (git: open ok, read EISDIR → die `[INFERENCE]`); 0-byte regular file
(git: `strbuf_read_file` returns 0 → `<= 0` → die). Census: `-L` branch resolves, then `[ -f ]`
(798/839/881) is false (or `read` fails and `c=""`), so it silently keeps `$dir` as the common dir
and continues guarding the gitdir's config/alternates. Consequence is bounded: `git rev-parse
--is-inside-work-tree` (1194) dies on the same repo, producing the `error` row, so no fabricated
measurement is emitted — but the guard evaluated the wrong common dir first, and the failure is not
scoped as "could-not-evaluate".
Smallest fix: after the `-L` resolution, when `[ -e "$common" ] || [ -L "$common" ]` and not `-f`,
set `soft=1`/`CFG_SOFT_REASON` (error row for that repo) instead of falling through.

**D4 — leading-whitespace trim is not git behaviour (over-refusal, fail-closed).**
Content `" ../..\n"`: git does not trim the leading space, `is_absolute_path` is false, path becomes
`$GIT_DIR/ ../..`, `strbuf_realpath` dies ("Invalid path"). Census 841 trims to `../..` and guards the
parent — i.e. it follows a path git never follows. With content `" /home/vgpnk/.omp/agent\n"` the
trim turns a git-fatal path into an absolute protected target and exits 2 whole-run, again outside
the "protected reach" definition.
Smallest fix: drop the leading trim at 800/841/883 (keep it at 865 for the `gitdir:` line).

**D5 — multi-line content.** `read -r` consumes only the first line; git keeps embedded newlines
after the trailing strip, so `strbuf_realpath` dies. Census can act on line 1 and guard a common dir
git never uses. No protected read (git cannot open the repo), but the repo is reported differently
(an ordinary row instead of git's fatal). Folded into the D1 fix (read whole file; if LF/CR remain
after the trailing strip, mark the repo error rather than exit 2).

No under-guard was found: every path git can successfully read is resolved by `guard_target` and
prefix-checked before the census opens it; anything git cannot read makes the census's later
`rev-parse` fail and yields `error`.

## 4. Coverage gap

- `grep -c commondir tests/fixtures/r15-census-config.py` → **0**.
- Inline selftest writes only regular files `printf '../..\n' > .../commondir` at 1576 and 1582; the
  only `ln -s` in the whole script is 1795 (unrelated protected-compare fixture). Nothing exercises
  794–797, 835–838, 877–880, or the whitespace/CRLF handling around 799–803/840–847/882–889.
- So the matrix's 38/38 selftest and 20/20 changed-fixture results do not cover the branch the new
  comment claims is "as git does". Add three selftest cases: (a) in-gitdir symlinked commondir to a
  regular file, (b) `../..\r\n` regular file (expect accept, matching git), (c) dangling commondir
  symlink (expect `error` row, not exit 2).

## 5. Sources (accessed 2026-10-20)

| URL | lines | quote (≤25 words) |
|---|---|---|
| https://raw.githubusercontent.com/git/git/master/setup.c | 325–343 | `"if (strbuf_read_file(&data, path.buf, 0) <= 0) die_errno"` |
| https://raw.githubusercontent.com/git/git/master/setup.c | 331–334 | `"data.buf[data.len - 1] == '\n' || data.buf[data.len - 1] == '\r'"` |
| https://raw.githubusercontent.com/git/git/master/setup.c | 337–339 | `"if (!is_absolute_path(data.buf)) strbuf_addf(&path, "%s/", gitdir);"` |
| https://raw.githubusercontent.com/git/git/v2.52.0/setup.c | 318–348 | same block reproduced verbatim in the read window |
| https://raw.githubusercontent.com/git/git/master/dir.c | 3204–3208 | `"int file_exists(const char *f) { struct stat sb; return lstat(f, &sb) == 0; }"` |
| https://raw.githubusercontent.com/git/git/master/strbuf.c | 776–794 | `"fd = open(path, O_RDONLY); if (fd < 0) return -1;"` |
| https://raw.githubusercontent.com/git/git/master/strbuf.c | 533–549 | `"if (got < 0) { ... return -1; }"` |
| https://raw.githubusercontent.com/git/git/master/abspath.c | 318–325 | `"strbuf_realpath(&resolved, path, 1);"` |
| https://raw.githubusercontent.com/git/git/master/abspath.c | 128–136 | `die_errno("Invalid path '%s'", resolved->buf)` |
| https://raw.githubusercontent.com/git/git/master/Documentation/gitrepository-layout.adoc | commondir | `"If this file exists, $GIT_COMMON_DIR ... will be set to the path specified in this file"` |
| https://raw.githubusercontent.com/git/git/master/Documentation/gitrepository-layout.adoc | commondir | `"If the specified path is relative, it is relative to $GIT_DIR."` |

## Confidence and remaining unknowns

- git source facts: **high** (two refs read, exact lines).
- census line-level behaviour: **high** for the branches and predicates; **D1 and the
  directory-target leg of D3 rely on bash `read` and Linux `open(dir)` semantics respectively —
  inference, not execution.** One ALLOWED-EXEC seat should construct the three fixture shapes and
  record the actual exit codes before D1/D2/D3 are treated as measured.
- Not investigated (out of assignment): whether `git worktree add` on any supported platform writes
  CRLF `commondir`; the census's handling of `GIT_COMMON_DIR` env (it unsets all `GIT_*`, so the
  override never reaches its own git calls — a deliberate divergence from a user's environment).
- Lane HEAD advanced from `a6ec7810…` to `163158a7…` during the probe; census bytes unchanged.

STATUS: ok

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && wc -l tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "commondir\|GIT_DIR\|GIT_WORK_TREE\|git -C\|git_cmd\|GIT_CONFIG_COUNT\|GIT_NO_LAZY_FETCH" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '440,540p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '760,900p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '380,462p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '76,170p' tools/souji-census.sh && echo '---1030---' && sed -n '1028,1060p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "commondir\|symlink" tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "protected_reason_inside\|lexical_abs()" tools/souji-census.sh | head -20 && echo --- && sed -n '300,380p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "guard_git_surface\|guard_git_links\|git -C \"\$repo\"" tools/souji-census.sh && echo '---' && sed -n '1140,1215p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '774,812p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'ln -s\|ln --\|symlink' tools/souji-census.sh | head -30 && echo '--- selftest commondir ---' && sed -n '1566,1590p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S04[3-9]\|S050\|commondir" corpus/SOURCES.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S'Read a symlinked commondir' -- tools/souji-census.sh && echo --- && git show 0a70bef:tools/souji-census.sh | sha256sum && git diff --stat 0a70bef HEAD -- tools/souji-census.sh && echo branch && git rev-parse --short HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '500,514p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '819,858p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '516,536p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -3 && git show HEAD:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '170,212p' tools/souji-census.sh && echo '--- fixture commondir ---' && grep -c commondir tests/fixtures/r15-census-config.py; true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S'guard_target git-common-dir' -- tools/souji-census.sh; echo ---; git log --oneline -S'if [ -L "$common" ]' -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^protected_fail()\|^guard_target()\|^resolve_guarded()\|^guard_git_files()\|^guard_git_links()\|^guard_git_surface()\|^guard_worktree_registrations()" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '860,896p' tools/souji-census.sh | nl -ba -v860
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '200,209p' tools/souji-census.sh | nl -ba -v200
curl -sS https://raw.githubusercontent.com/git/git/master/wrapper.c | grep -n "exists\|lstat\|S_ISLNK" ; echo "---setup---"; curl -sS https://raw.githubusercontent.com/git/git/master/setup.c | grep -n "file_exists"
for f in git-compat-util.h wrapper.c path.c cache.h; do echo "== $f"; curl -sS "https://raw.githubusercontent.com/git/git/v2.42.4/$f" | grep -n "file_exists"; done
for f in git-compat-util.h compat/posix.h wrapper.c; do echo "== master $f"; curl -sS "https://raw.githubusercontent.com/git/git/master/$f" | grep -n "file_exists"; done
for f in path.h dir.h environment.h strbuf.h object-file.h repository.h setup.h; do echo "== $f"; curl -sS "https://raw.githubusercontent.com/git/git/master/$f" | grep -n "file_exists"; done
curl -sS https://raw.githubusercontent.com/git/git/master/dir.c | grep -n -A6 "^int file_exists\|^int repo_file_exists"
curl -sS 'https://grep.app/api/search?q=file_exists%28&filter%5Brepo%5D%5B0%5D=git/git' | head -c 3000
curl -sS https://raw.githubusercontent.com/git/git/v2.52.0/setup.c | sed -n '318,348p'
curl -sS https://raw.githubusercontent.com/git/git/master/abspath.c | grep -n -B3 -A25 "char \*strbuf_realpath"
curl -sS https://raw.githubusercontent.com/git/git/master/abspath.c | sed -n '105,212p'
curl -sS https://raw.githubusercontent.com/git/git/master/setup.c | grep -n "commondir\|strbuf_read_file\|strbuf_add_real_path" | sed -n '1,12p'; echo ---; curl -sS https://raw.githubusercontent.com/git/git/master/dir.c | sed -n '3204,3208p'
curl -sS https://raw.githubusercontent.com/git/git/master/strbuf.c | grep -n -A22 "^ssize_t strbuf_read(struct strbuf"
curl -sS https://raw.githubusercontent.com/git/git/master/setup.c | grep -n -A18 "static const char \*read_gitfile_gently" | sed -n '1,30p'
curl -sS https://raw.githubusercontent.com/git/git/master/setup.c | grep -n -B2 -A14 "read_gitfile_gently(const"
curl -sS https://raw.githubusercontent.com/git/git/master/setup.c | grep -n -B2 -A22 "static int read_gitfile_raw"
curl -sS https://raw.githubusercontent.com/git/git/master/setup.c | grep -n -A20 "read_gitfile_raw(struct strbuf"
```

URLs read via the `read` tool (no shell): `.../master/setup.c` (1–300, 300–380), `.../master/gitrepository-layout.adoc`, `.../master/strbuf.c` (774–800), `.../master/abspath.c` (300–345). Directory listing read: `tests/fixtures`. One `web_search`: `git source "int file_exists" "lstat" OR "access" wrapper.c git-compat-util` (used only to locate the definition, which `dir.h`/`dir.c` then confirmed).
