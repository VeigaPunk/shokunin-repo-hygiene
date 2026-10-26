# deliver-src-S225 — proc_pid_fd(5) registry row, rejection row, Gate block

Seat: SwarmScribe39 (wave w1, read-only scribe). Item: open proc_pid_fd(5) live, draft registry row S225,
one rejection row, Gate block entry, validate the row in scratch.
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin; registry read at prereg
2d9bca55a9f042a2c9ed60a797a8069e74c41f46 (`corpus/SOURCES.md`, 254 lines, 147 registry rows, highest S223).
Nothing in the lane was written except this file, `src-S225.html` and `SwarmScribe39.md`; all work executed in
/fast/scratch/hyaku/souji-r33/SourceProcFd/ (removed at the end of the run).

## 1. Fetch receipt

Command (scratch, `export TMPDIR=/fast/scratch/hyaku/souji-r33/SourceProcFd/tmp`):

    curl -sS -o s225.html -w 'http_code=%{http_code} size_download=%{size_download} content_type=%{content_type} url_effective=%{url_effective}\n' \
      -A 'souji-census/1.0 (source registry fetch)' https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html

Output: `http_code=200 size_download=11359 content_type=text/html url_effective=https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html`

- HTTP status: **200**
- Bytes: **11359** (`wc -c`), 11347 characters decoded UTF-8
- sha256: **3a50ddef6f2f3a4f1139dcef3299a5eadf8fc96514df9fcb329a3bffd47ff27e**
- Saved bytes: `.ufo/waves/round-33/w1/src-S225.html` (re-hashed after the copy: same sha256, 11359 bytes)
- Page version: `Linux man-pages 6.19  2026-02-08` (§ COLOPHON), HTML rendering created 2026-09-09
- Sections present (whole page): NAME, DESCRIPTION, SEE ALSO, COLOPHON — nothing else.

## 2. Anchor and located quotes (copied from the bytes of this run)

Anchor: **§ DESCRIPTION paras 1-3** — para 1 the fd entry, para 2 the readlink format for pipes and sockets,
para 3 descriptors with no inode.

| # | Where | Quote (<=25 words, no pipe character) | Words |
|---|---|---|---|
| Q1 | § DESCRIPTION para 2 | `A readlink(2) call on this file returns a string in the format: type:[inode]` | 13 |
| Q2 | § DESCRIPTION para 2 | `For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode.` | 22 |
| Q3 | § DESCRIPTION para 3 | `the entry will be a symbolic link with contents of the form anon_inode:file-type` | 13 |

Each Q was asserted present exactly once, after stripping tags and collapsing whitespace, in the fetched bytes:
`q in norm -> True` for all three.

What the page does **not** say (sweeps over the same bytes): `deleted` 0 matches (no `(deleted)` suffix rule for
an fd target), no statement that repeated slashes are collapsed in the returned string, no statement that the
return is always an absolute pathname. Those would be inference if a row claimed them.

## 3. Row S225 — exact text to append inside `## Registry`, after S223

```
| S225 | proc_pid_fd(5) — https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html | docs | A | the string a readlink of /proc/pid/fd/N yields, which a census case pattern compares; not the permission rule (S096) and not the residue reading | Linux man-pages 6.19, page dated 2026-02-08, HTML rendering created 2026-09-09, fetched 2026-10-26 (http 200, 11 359 bytes, sha256 3a50ddef…ff27e); § DESCRIPTION paras 1-3 | readlink on an fd entry returns the target file; pipes and sockets yield `type:[inode]` and descriptors with no inode yield `anon_inode:[file-type]`, so a comparison against a pathname must branch on non-path targets | mined | 2026-10-26 | 365d | corpus/lessons/round-33.md |
```

Column check: 11 cells — id `S225`; kind `docs`; tier `A` (vendor documentation, not community); scope narrowed
to the returned string and explicitly disjoined from S096 (permission rule); anchor carries the page version,
the fetch receipt digest and the section; teaches states only page text; status `mined`; opened `2026-10-26`;
recheck `365d`; used-by `corpus/lessons/round-33.md` (the C2 sourced citation site in the preregistration).

Ids: highest at prereg is S223; S224 is the POSIX pathname-resolution seat and S226 the Python tempfile seat
(`.ufo/waves/round-33/w1-spec.json`, `make-spec-w2.py`), so S225 and S227 are free. S227 is the rejection id below.

## 4. Rejection row S227 — exact text

Candidate opened live for the same teaching: readlink(2).
`curl -sS -o readlink2.html -w 'http_code=%{http_code} size_download=%{size_download}' https://man7.org/linux/man-pages/man2/readlink.2.html`
→ `http_code=200 size_download=18306`, sha256 `79a58d6cb5e5c8cb789886aa7cf2a03f0c9eafd58e87200f095b172dc3211d93`,
Linux man-pages 6.19, page dated 2026-02-08. (Not persisted in the lane: this item names only `src-S225.html`.)

Sweep over the opened bytes of readlink(2): `type:[` 0 matches, `pipe:[` 0 matches, `anon_inode` 0 matches;
its 10 `proc` hits are the `dirfd`/`AT_FDCWD` prose, the glibc `/proc/self/fd` note, the `st_size` zero caveat and
the SEE ALSO list — the target format itself is only reachable through the sibling page.

```
| S227 | readlink(2) — https://man7.org/linux/man-pages/man2/readlink.2.html | docs | A | the readlink syscall's buffer and truncation contract only; not the /proc/pid/fd link contents | Linux man-pages 6.19, page dated 2026-02-08, fetched 2026-10-26 (http 200, 18 306 bytes, sha256 79a58d6c…11d93); § DESCRIPTION, § SEE ALSO | REJECTED for S225's teaching: the page defers the fd link contents to proc_pid_fd(5) in SEE ALSO and states no target format (swept the opened bytes: `type:[` 0, `pipe:[` 0, `anon_inode` 0 matches); flip: readlink(2) states the fd target format itself | rejected | 2026-10-26 | 365d | corpus/lessons/round-33.md |
```

Rejection quote, § SEE ALSO: `proc(5), proc_pid_cwd(5), proc_pid_exe(5), proc_pid_fd(5), proc_pid_root(5), namespaces(7)` (6 words, verbatim).

## 5. Gate block entry for `corpus/lessons/round-33.md` § Gate

Table row in the round-32 Gate shape (Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip):

| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |
|---|---|---|---|---|
| `S225` proc_pid_fd(5) — what readlink of `/proc/pid/fd/N` returns | ADMIT (new row; scope restricted to the returned string) | https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html — http 200, 11 359 bytes, sha256 `3a50ddef…ff27e`, content-type text/html, fetched 2026-10-26; Linux man-pages 6.19, page dated 2026-02-08, rendering created 2026-09-09; snapshot `.ufo/waves/round-33/w1/src-S225.html` | § DESCRIPTION para 2 — "A readlink(2) call on this file returns a string in the format: type:[inode]"; para 3 — "the entry will be a symbolic link with contents of the form anon_inode:file-type" | Grounds the C2 mechanism the SKILL error-pattern bullet states: the value a census case pattern compares is a pathname only for open files; pipes, sockets and descriptors with no inode carry `type:[inode]` and `anon_inode:[file-type]`, so the pattern must branch. Registered against S083/S086 (same page, entry and link-content scope) and S096 (permission rule) — see finding 1. Flip: a case pattern that never compares a readlink value needs no row. |
| `S227` readlink(2) | REJECT (registry row kept as rejected) | https://man7.org/linux/man-pages/man2/readlink.2.html — http 200, 18 306 bytes, sha256 `79a58d6c…11d93`, fetched 2026-10-26 | § SEE ALSO — "proc(5), proc_pid_cwd(5), proc_pid_exe(5), proc_pid_fd(5), proc_pid_root(5), namespaces(7)"; sweep: `type:[` 0, `pipe:[` 0, `anon_inode` 0 | The page states the syscall's buffer/truncation contract and sends the reader to proc_pid_fd(5) for the link contents; it cannot ground the comparison. Flip: readlink(2) states the fd target format itself. |

## 6. Registry validation in scratch (executed)

Scratch mirror: `/fast/scratch/hyaku/souji-r33/SourceProcFd/mirror/` = `corpus/` copied from the lane plus
`tools/souji-size-census.py` (the only used-by path outside `corpus/`) ; both rows inserted after `| S223 `.
Registry row count after insertion: 149.

A — before the round-33 lesson lands (expected single E11 on S225's used-by):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file mirror/corpus/SOURCES.md --today 2026-10-26 | grep -v $'\tW04\t'
file	E11	S225 missing used-by corpus/lessons/round-33.md
A_exit=1
```

B — with `corpus/lessons/round-33.md` present (placeholder for the check only):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file mirror/corpus/SOURCES.md --today 2026-10-26 | grep -v $'\tW04\t'
file	ok	/fast/scratch/hyaku/souji-r33/SourceProcFd/mirror/corpus/SOURCES.md
B_exit=0
W04=[37] E=[0]
```

Baseline for comparison, the lane registry at prereg, unchanged (read-only run, no mirror):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md --today 2026-10-26 | grep -c W04
36
```

So the only new diagnostic my two rows add is one warning, `W04 S225 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes`
(37 = 36 + 1); S227 adds none (its URL is new); no E-code is attributable to either row once the lesson exists.

## 7. Scratch measurement filed for the lesson (mine, not page text)

Because the O4/O5 legs turn on a TMPDIR with a trailing slash and the census case pattern at
`tools/souji-census.sh:1986-1994` compares `readlink -- "/proc/$1/fd/1"` (line 1988) against the pattern
`"${TMPDIR:-/tmp}"/souji-census-now.*/*` (line 1990), I probed the return value in my own scratch tree
(no lane tool run, no lane process touched):

```
argv target: /fast/scratch/hyaku/souji-r33/SourceProcFd/probe/a//worker.out
readlink    : /fast/scratch/hyaku/souji-r33/SourceProcFd/probe/a/worker.out
pipe fd1    : pipe:[166194168]
```

The doubled slash of the open argument is absent from the returned string, and a pipe fd returns `pipe:[inode]` as
the page documents. This is a measurement of this host, **not** a claim of the page: proc_pid_fd(5) states the
format and nothing about slash normalisation. [INFERENCE] from the measurement plus the code: with `TMPDIR`
ending in `/`, the literal pattern `//souji-census-now.*/*` cannot match a returned path carrying one slash, so
`st_worker_tmpdir` returns 1 — the same two-line shape repeats for the cleanup comparison at
`tools/souji-census.sh:2906` and `:2970`. The O4 defect therefore needs both legs — S224 (POSIX pathname
resolution of repeated slashes) for what the kernel resolved, and S225 for what a comparison may see.

## 8. Limits

- The page is a rendering of man-pages 6.19 (2026-02-08); nothing here speaks for later man-pages or for a kernel
  whose readlink differs.
- One page, one anchor; no second source corroborates the anon_inode wording in this submission.
- The rejection row's bytes were not saved in the lane (item names only `src-S225.html`); only its digest, size
  and quote are recorded. L1 may persist them if the rejected row is kept.
- Row insertion order and the S224 seat's row are L1's: if S224 lands first, S225 appends after it and no id moves.
