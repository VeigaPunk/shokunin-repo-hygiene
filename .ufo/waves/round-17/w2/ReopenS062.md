STATUS: DONE — S062 (fifo(7)/open(2)) re-opened independently on 2026-10-20: the primary quote is verbatim at the anchor it names and is 12 words (wave-1 says 11); version line 6.19 / 2026-02-08 reproduced exactly; tier/scope/opened/recheck hold; `teaches` disagrees on three clauses (blocking qualifier dropped, "non-regular" is broader than the page, "hang forever" ignores the interruptible wait); `status mined` fails the sources census at ddb7347 because its `used-by` file does not exist; the row's id is S062, not the wave-1 prose's S051 (already allocated to jj git-compatibility).

# ReopenS062 — `fifo(7)`/`open(2)` re-opened independently (round 17, W2 FALSIFY)

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, landed tip `ddb7347`. Wave-1 draft under test:
`.ufo/waves/round-17/w1/SrcFifo7.md`, sha256 `fd5fdea25190b5793f67467650fa6c3fd698c5708733a9005a80b18a0c400e7d`, 9,489 bytes.
`git cat-file -e ddb7347:.ufo/waves/round-17/w1/SrcFifo7.md` → `fatal: path ... exists on disk, but not in 'ddb7347'`, so the draft is untracked review material, not landed evidence. No `jj`, no lane tool, no git write; the only file written is this report. No tool installed or upgraded.

## 1. What was served, and the version lines the pages carry

Both pages are served by man7.org as renderings of the man-pages tarball, and both are stamped today (2026-10-20):

| page | footer the page serves | COLOPHON | host package |
|---|---|---|---|
| `https://man7.org/linux/man-pages/man7/fifo.7.html` | `Linux man-pages 6.19            2026-02-08                        fifo(7)` | tarball `man-pages-6.19.tar.gz` fetched 2026-09-09; HTML rendering created 2026-09-09 | `man-pages 6.19-1`; `zcat /usr/share/man/man7/fifo.7.gz \| grep '^\.TH'` → `.TH fifo 7 2026-02-08 "Linux man-pages 6.19"` |
| `https://man7.org/linux/man-pages/man2/open.2.html` | `Linux man-pages 6.19            2026-02-08                        open(2)` | same tarball/rendering dates | `zcat /usr/share/man/man2/open.2.gz \| grep '^\.TH'` → `.TH open 2 2026-02-08 "Linux man-pages 6.19"` |

The draft's version cell ("Linux man-pages 6.19, `.TH` date 2026-02-08, HTML rendered 2026-09-09") **agrees exactly** with the served page. The ".TH" wording is not printed by the HTML — the footer is generated from it — and I confirmed the `.TH` line from the host roff, so no overclaim. `on-release` is also current-checkable: the kernel.org mirror index lists `man-pages-6.19.tar.gz  25-Aug-2026` as the newest tarball, so 6.19 is the release the recheck is keyed to.

## 2. Quote verification (the assigned check)

**Primary quote — VERBATIM, anchor correct, 12 words.**

> Normally, opening the FIFO blocks until the other end is opened also.

Served page, § DESCRIPTION, third paragraph (HTML line-wrapped as `Normally, opening the FIFO blocks until the other end is / opened also.`); de-wrapping gives the sentence character-for-character, including `Normally,` with its comma and `also.` with its period. The host roff confirms the same sentence split across lines 28-31 of `/usr/share/man/man7/fifo.7.gz`. Word count is **12**, not the draft's "11 words" (`Normally,` / opening / the / FIFO / blocks / until / the / other / end / is / opened / also.). Still far under the 25-word cap.

Anchor: the draft names "fifo(7) § DESCRIPTION". That is where the sentence lives; the page's HTML exposes no finer anchor than `#DESCRIPTION`, and the sentence is the last of three DESCRIPTION paragraphs (it follows the "kernel maintains exactly one pipe object" and "must be opened on both ends" sentences). Anchor **agrees**; "third paragraph of DESCRIPTION" is the tightest available locator.

**Supporting quotes — all verbatim, two counts off by one.**

| quote as used by wave 1 | served page | word count |
|---|---|---|
| "The FIFO must be opened on both ends (reading and writing) before data can be passed." | § DESCRIPTION, second paragraph — exact | 16 (draft says 15) |
| open(2) "Neither the open() nor any subsequent I/O operations on the file descriptor which is returned will cause the calling process to wait." | § DESCRIPTION › `O_NONBLOCK` or `O_NDELAY` — exact | 22 (draft says 22 ✓) |
| "A process can open a FIFO in nonblocking mode." | § DESCRIPTION, fourth paragraph — exact | 9 |
| "Under Linux, opening a FIFO for read and write will succeed both in blocking and nonblocking mode." | § DESCRIPTION, fifth paragraph — exact | exact |
| open(2) `O_PATH`: "The file itself is not opened, and other file operations (e.g., read(2), write(2), fchmod(2), fchown(2), fgetxattr(2), ioctl(2), mmap(2)) fail with the error EBADF." | § DESCRIPTION › `O_PATH` — exact | exact |
| open(2) `O_DIRECTORY`: "to avoid denial-of-service problems if opendir(3) is called on a FIFO or tape device" | § DESCRIPTION › `O_DIRECTORY` — exact | exact |

One quoting nuance the row should not inherit: the open(2) sentence is quoted without its lead-in in the same paragraph, "When possible, the file is opened in nonblocking mode." Dropping it is harmless for a FIFO (the hedge applies to regular files and block devices, which the page's next paragraph names), but a row that quotes only the second sentence is quoting a sentence that begins mid-argument.

## 3. Per-cell verdict on the drafted row

The drafted row (11 cells, `|`-free) is structurally valid: 11 columns is exactly `NF=13` for `awk -F'|'`, the `kind` enum accepts `docs`, and the tier/status enums accept `A`/`mined` (`census/round-12/sources-census.sh:1-9`).

| cell | verdict | basis / corrected text |
|---|---|---|
| `id` | **DISAGREE (prose only)** | The row cell says `S0??`, which is fine, but the draft's prose says "Next unused id is S051 (registry currently ends at S050)". S051 is already the round's jj git-compatibility source (`.ufo/waves/round-17/w2/ReopenS051.md` header, "S051 ... docs.jj-vcs.dev/latest/git-compatibility/"); S052/S054/S056/S057/S059 are likewise taken by sibling rows. This item is **S062**. |
| `source` | **PARTIAL** | One URL per row is the S001–S050 convention; S009 lists several *files of one repository* under a single URL, and corroborating documents live in `anchor` (S038, S042, S049). Two distinct documents' URLs in `source` has no precedent. Corrected: `fifo(7), Linux man-pages — https://man7.org/linux/man-pages/man7/fifo.7.html`, with the open(2) URL moved to `anchor`. |
| `kind` | **AGREE** | `docs` — a man page. Enum-valid. |
| `tier` | **AGREE** | `A`. man7.org serves the man-pages project's own tarball (COLOPHON states the provenance and the fetch date); it is the canonical upstream text for these interfaces, not a community write-up. The census inflation rule (`tier A + kind community`) does not fire. |
| `scope` | **AGREE, one clause worth adding** | The page is not about Git and not about hardlinks, and the cell says so — that exclusion is the honest part. "in a repository metadata path" is the lane's application, which is how S049/S045 scope cells are framed. Optional hardening: say "FIFO special file only" and "read-write open is Linux-specific (POSIX undefined)" — both are page statements (see § DESCRIPTION paragraphs 4-5) and they fence the exact overreaches the `teaches` cell commits. |
| `anchor` | **AGREE** | Section names are right: fifo(7) § DESCRIPTION; open(2) § DESCRIPTION `O_NONBLOCK`. Version/date/rendering strings reproduce the served page. Corrected form only tightens the fifo locator to "third paragraph" and adds `§ ERRORS EINTR` (see next section). |
| `teaches` | **DISAGREE** | Three clauses claim more than the page states — detailed in §4. |
| `status` | **DISAGREE as drafted** | `mined` requires the `used-by` path to exist (`census/round-12/sources-census.sh` "mined rows whose used-by paths do not exist — must print nothing"). `git ls-tree ddb7347 corpus/lessons/` lists `round-1 … round-16`; there is no `round-17.md`. As landed today the row prints `missing: corpus/lessons/round-17.md`. Either `queued` + `—` now, or `mined` + `corpus/lessons/round-17.md` only in a commit that also creates that lesson and cites the row — the wave-1 caveat is correct and I confirm it independently. |
| `opened` | **AGREE** | 2026-10-20; both pages served today with today's access. |
| `recheck` | **AGREE** | `on-release`; 6.19 is the current tarball (mirror index 2026-08-25), so the recheck key is live and unambiguous. |
| `used-by` | **DEPENDS on `status`** | `corpus/lessons/round-17.md` does not exist at ddb7347. It is a legitimate target *only* for the FIFO half of D2; the hardlink half is not taught by these pages (see §5), so a lesson that cites S062 for both halves would over-attribute. |

## 4. The `teaches` overreach, clause by clause

Drafted cell: *"a FIFO read-open blocks until a writer opens it, so a guard that opens a non-regular metadata path before checking its type can hang forever; type-check and refuse without opening"*.

1. **"a FIFO read-open blocks until a writer opens it" — over-broad.** The page's very next paragraph contradicts the unqualified form: *"A process can open a FIFO in nonblocking mode. In this case, opening for read-only succeeds even if no one has opened on the write side yet …"*, and the paragraph after that says *"Under Linux, opening a FIFO for read and write will succeed both in blocking and nonblocking mode."* So the true statement is about a **blocking, one-direction** open. Corrected: "a blocking open of a FIFO waits until the other end is opened (a nonblocking read-only open succeeds with no writer, and an `O_RDWR` open does not wait)".
2. **"a non-regular metadata path" — broader than the page.** fifo(7) is titled and scoped to the FIFO special file; it says nothing about sockets, character or block devices, or non-regular files as a class. The census's own doc block is broader than the source it cites (`tools/souji-census.sh:104-114` "a hardlinked or non-regular (FIFO/socket/device, or a symlink resolving to one)"), which is a defensible defensive guard but is not this page's teaching. Corrected: keep "FIFO special file" in the cell and let the code's wider class stand on its own (it is a policy choice, not a sourced fact).
3. **"can hang forever" — not unconditional.** It hangs only while no other end opens *and no signal arrives*. open(2) § ERRORS names exactly this wait as interruptible: *"EINTR  While blocked waiting to complete an open of a slow device (e.g., a FIFO; see fifo(7)), the call was interrupted by a signal handler; see signal(7)."* The honest phrasing is "blocks indefinitely until the other end is opened or the open is interrupted"; "forever" also obscures why a `SIGINT` cannot be relied on in a batch census (no handler, no tty).
4. **"type-check and refuse without opening" — this is lane policy, and it is what the code does.** It is not a claim the page makes, but registry `teaches` cells routinely carry the lane consequence (S045, S046, S049), so keeping it is conventional. It is also literally true of the implementation (§6): the type probe is `stat(2)`, which does not open.

## 5. The hardlink half is ungrounded (confirmed)

Neither page contains a hardlink statement. The full fifo(7) text has no `hardlink`/`hard link` token; open(2)'s only link-related text is symlink following (`O_EXCL`, `O_NOFOLLOW`, `ELOOP`), `link(2)` used to build an atomic lockfile under `O_EXCL` (which merely *reads a link count with stat(2)*), and unlink-vs-descriptor semantics. So:

- The census's comment gives the right reason **for the code** — `tools/souji-census.sh:631-633`: "a FIFO would block status forever; a hardlink can alias into a store" — an **aliasing** argument, not a FIFO argument.
- A hardlinked regular file is `S_ISREG`, so the type probe cannot catch it; the code has a separate `nlink > 1` branch (`:558-565`) and the fixture asserts it (`:1927`, `:1968-1976`). That split is correct.
- The source row must therefore say "not hardlink policy" (as the draft's scope already does) and must not support the hardlink branch. If L1 wants the hardlink half sourced, S059 (`gitattributes(5)`, `$GIT_DIR/info/attributes`) is the adjacency — but it does not state aliasing either, so an explicit "policy, not sourced" label is the honest option.

## 6. How D2 actually consumes the source at ddb7347 (does the teaching match the code?)

- `guard_git_files()` — `tools/souji-census.sh:542`; loop over `config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates` at `:544`.
- The probe is **before** any open: `if ! kind=$(stat -L -c '%F %h' -- "$path" 2>/dev/null); then continue; fi` at `:549`. `stat(2)` does not open the file, so a FIFO at that path cannot block here. This is the exact shape the `teaches` cell should describe. (Comment nit: `:547` calls it an "lstat-resolved type probe", but `-L` dereferences; the behaviour matches the intended "a symlink resolving to one" test at `:104-105`, so the comment, not the code, is off.)
- `regular file` + `nlink > 1` + `info/attributes` → `meta_soft "git-metadata-hardlink"` (`:558-562`); every other non-regular type at `info/attributes` → `meta_soft "git-metadata-nonregular"` (`:567-571`); all other guarded entries keep `protected_fail` (whole-run exit 2), and the loop continues (`:562-572`, `:574-577`).
- `emit_soft_diag()` (`:648`) prints exactly `souji-census: git-metadata-unsupported <reason> <path>` to stderr, and the config soft line only when no metadata reason exists or a config reason also exists — matching the landed contract text.
- Fixture: `mkfifo "$RF/.git/info/attributes"` at `:1936`; assertions at `:1983-1989` require the repo's flag to be `error` ("(no hang)") and stderr to carry `git-metadata-unsupported git-metadata-nonregular .../info/attributes`.
- **Red-before bound:** the FIFO selftest invocation itself is unbounded (`:1958-1962`, no `timeout`). The bound comes from the harness: `census/round-17/run-matrix.py:89-108` runs each command with a timeout and kills the process group on expiry (`:91` names "on a hostile fifo"), and `:212` runs `--selftest` under `timeout=600`. A blocking implementation would therefore surface as a missing `selftest: N checks` line rather than as a green run — the case is valid *through the matrix*, but a bare `tools/souji-census.sh --selftest` on a host with the regression would hang. Smallest fix: wrap that one invocation in `timeout 20` and let exit 124 fail the case.
- **Residual the page cannot close:** the doc block itself admits "the guard and the later access are not one atomic operation" (`:144-145` region). The page grounds the hazard, not atomicity; a path swapped to a FIFO between the probe and `git status` still blocks. No source row can fix that; it belongs in the lesson's residual list.

## 7. Corrected row (full, 11 cells, no `|` inside any cell)

| S062 | fifo(7), Linux man-pages — https://man7.org/linux/man-pages/man7/fifo.7.html | docs | A | blocking-open liveness of a FIFO special file only, Linux; not sockets or devices, not hardlink policy, not Git behavior, and read-write open on a FIFO is Linux-specific with POSIX leaving it undefined | fifo(7) § DESCRIPTION third paragraph "Normally, opening the FIFO blocks until the other end is opened also.", with the next paragraph for the nonblocking and read-write exceptions; open(2) § DESCRIPTION O_NONBLOCK and § ERRORS EINTR at https://man7.org/linux/man-pages/man2/open.2.html; Linux man-pages 6.19, page date 2026-02-08, HTML rendered 2026-09-09, current tarball man-pages-6.19.tar.gz dated 2026-08-25 on the kernel.org mirror | a blocking open of a FIFO waits until the other end is opened, a nonblocking read-only open succeeds with no writer, and the wait is interrupted by a signal; so a guard that opens such a path before classifying it blocks instead of failing, and the census classifies with stat(2) and refuses without open(2) | queued | 2026-10-20 | on-release | — |

Flip rule: if `corpus/lessons/round-17.md` lands in the same commit and cites this row for the FIFO half of D2, change `queued` → `mined` and `—` → `corpus/lessons/round-17.md`. Do not cite it for the hardlink branch.

## 8. Smallest fixes (advisory)

1. Set the id to **S062**; the wave-1 prose's "next unused id is S051" collides with the round's jj git-compatibility row.
2. Keep `source` to the fifo(7) URL; put the open(2) URL and `§ ERRORS EINTR` in `anchor`.
3. Rewrite `teaches` per §4: add "blocking", keep the subject to FIFO (not "non-regular"), and replace "hang forever" with "waits until the other end opens (interruptible by a signal)".
4. `status queued` + `used-by —` unless the round-17 lesson lands in the same commit; `mined` is census-invalid at ddb7347 (`round-17.md` absent).
5. Correct the two word counts (12, not 11; 16, not 15) if they are reused in the lesson Gate; both still satisfy ≤25.
6. Optional: bound the FIFO selftest invocation with `timeout` so the red-before state fails instead of hanging outside the matrix harness.

## 9. Remaining unknowns

- Whether L1 will land `corpus/lessons/round-17.md` and cite S062 for the FIFO half only — the `status`/`used-by` verdict is conditional on that commit.
- The hardlink half has no source in either page; if the round wants a sourced hardlink refusal it needs a different row (S059 is adjacent but also silent on aliasing).
- Whether the census's wider class (socket, device, symlink-to-those) should get its own source row; this page does not cover it, and the code's broad `*` branch is currently policy-only.

Verdict: **partial** — quote, anchor, version line, tier, scope, opened and recheck hold; `teaches` overstates three clauses; `status`/`used-by` are census-invalid at ddb7347; the row id is S062, not S051.

## 10. Commands run (verbatim, with observed output)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
d7e648d5a1931e6dbacfd5be0587547afee15de3
$ git -C ... ls-tree --name-only ddb73474433977ff54b015ac3e77669ff2537353 corpus/
corpus/QUALITY.md  corpus/README.md  corpus/SOURCES.md  corpus/knowledge  corpus/lessons
$ git -C ... ls-tree --name-only ddb7347... corpus/lessons/
round-1.md ... round-16.md   (no round-17.md)
$ git -C ... show ddb7347...:corpus/SOURCES.md | grep -n '^| S0' | tail -8
S043 ... S050   (last id S050)
$ sha256sum .ufo/waves/round-17/w1/SrcFifo7.md
fd5fdea25190b5793f67467650fa6c3fd698c5708733a9005a80b18a0c400e7d  .ufo/waves/round-17/w1/SrcFifo7.md
$ stat -c '%s bytes' .ufo/waves/round-17/w1/SrcFifo7.md
9489 bytes
$ git -C ... cat-file -e ddb7347....ufo/waves/round-17/w1/SrcFifo7.md
fatal: path '.ufo/waves/round-17/w1/SrcFifo7.md' exists on disk, but not in 'ddb73474433977ff54b015ac3e77669ff2537353'
$ pacman -Q man-pages
man-pages 6.19-1
$ zcat /usr/share/man/man7/fifo.7.gz | grep -n '^\.TH'
6:.TH fifo 7 2026-02-08 "Linux man-pages 6.19"
$ zcat /usr/share/man/man2/open.2.gz | grep -n '^\.TH'
7:.TH open 2 2026-02-08 "Linux man-pages 6.19"
$ zcat /usr/share/man/man7/fifo.7.gz | sed -n '22,34p'
The kernel maintains exactly one pipe object for each
FIFO special file that is opened by at least one process.
The FIFO must be opened on both ends (reading and writing)
before data can be passed.
Normally,
opening the FIFO blocks
until the other end is opened also.
.P
A process can open a FIFO in nonblocking mode.
In this case,
opening for read-only succeeds
even if no one has opened on the write side yet
$ python3 - <<'EOF'   # word counts
primary fifo: 12 words, 69 chars
support fifo: 16 words, 85 chars
open nonblock: 22 words, 133 chars
fifo nonblock: 9 words, 46 chars
open eintr: 26 words, 148 chars   (trimmed form used above is 24)
EOF
$ git -C ... show ddb7347...:tools/souji-census.sh | grep -n 'guard_git_files()\|stat -L -c .%F %h\|FIFO would block\|emit_soft_diag()\|mkfifo\|FIFO info/attributes: error row'
542:guard_git_files() { # $1 resolved gitdir
549:    if ! kind=$(stat -L -c '%F %h' -- "$path" 2>/dev/null); then continue; fi
632:# FIFO would block status forever; a hardlink can alias into a store), so
648:emit_soft_diag() { # $1 repo label; prints every stored soft finding (stderr)
1936:  mkfifo "$RF/.git/info/attributes"
1983:  if [ "$v" = "error" ]; then st_ok "FIFO info/attributes: error row (no hang)"
$ git -C ... show ddb7347...:census/round-17/run-matrix.py | grep -n 'timeout'
89:def run(cmd: list[str], timeout: int = 900)
91:# (e.g. on a hostile fifo); kill the whole group on timeout, not just the
212:            rc, so, se = run(["bash", str(tool), "--selftest"], timeout=600)
$ git -C ... show ddb7347...:census/round-12/sources-census.sh | sed -n '1,14p'
(mined rows whose used-by paths do not exist — must print nothing; runs `[ -e "$p" ] || echo "missing: $p"`)
```

Web reads (no network writes): the two man7.org pages above (fifo.7 and open.2, full DESCRIPTION and ERRORS), and `https://mirrors.edge.kernel.org/pub/linux/docs/man-pages/` for the current tarball date. Peer reports read by exact name: `.ufo/waves/round-17/w1/SrcFifo7.md`, `.ufo/waves/round-16/w2/ReopenS045.md` (shape precedent), and the headers of `.ufo/waves/round-17/w2/ReopenS051.md`, `ReopenS052.md`, `ReopenS054.md`, `ReopenS056.md`, `ReopenS057.md`, `ReopenS059.md` (id allocation).
