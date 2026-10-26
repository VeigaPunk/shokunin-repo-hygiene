# SwarmScribe39 — S225 proc_pid_fd(5) registry row (round 33, w1)

## Status
STATUS: PASS — proc_pid_fd(5) opened live (HTTP 200, 11 359 bytes, sha256 `3a50ddef…ff27e`, bytes saved), row S225 drafted in the 11-column registry shape with three located quotes, one rejection row S227 (readlink(2), opened, swept, rejected), Gate block entry written, and both rows validated in a scratch mirror of the lane registry: `file ok`, exit 0, 0 E-codes, the single new W04 being S225's shared URL.

## Evidence

Revision read: prereg `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (`corpus/SOURCES.md` 254 lines, 147 registry rows, highest id S223); lane working tree at `fef88f2159f6380a4d1360f73365b3d595973a37`, `git status --porcelain` empty.

Fetch (scratch `TMPDIR=/fast/scratch/hyaku/souji-r33/SourceProcFd/tmp`):

```
curl -sS -o s225.html -w 'http_code=%{http_code} size_download=%{size_download} content_type=%{content_type} url_effective=%{url_effective}\n' \
  -A 'souji-census/1.0 (source registry fetch)' https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html
http_code=200 size_download=11359 content_type=text/html url_effective=https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html
sha256  3a50ddef6f2f3a4f1139dcef3299a5eadf8fc96514df9fcb329a3bffd47ff27e
```

Page version `Linux man-pages 6.19  2026-02-08` (COLOPHON), rendering created 2026-09-09. Sections: NAME, DESCRIPTION, SEE ALSO, COLOPHON only.

Quote verification, tags stripped and whitespace collapsed over the fetched bytes:

```
13 True A readlink(2) call on this file returns a string in the format: type:[inode]
13 True the entry will be a symbolic link with contents of the form anon_inode:file-type
22 True For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode.
6  True proc(5), proc_pid_cwd(5), proc_pid_exe(5), proc_pid_fd(5), proc_pid_root(5), namespaces(7)   # rejection candidate, readlink(2) SEE ALSO
```

Registry validation in scratch (mirror = lane `corpus/` + `tools/souji-size-census.py`, rows inserted after `| S223 `, 149 rows):

```
$ scripts/sources-census.sh validate --file mirror/corpus/SOURCES.md --today 2026-10-26     # before the lesson lands
file	E11	S225 missing used-by corpus/lessons/round-33.md
$ ... same, with corpus/lessons/round-33.md present
file	ok	/fast/scratch/hyaku/souji-r33/SourceProcFd/mirror/corpus/SOURCES.md
exit=0   W04=37   E=0
$ ... --file <lane>/corpus/SOURCES.md   # baseline, unchanged lane registry
36 W04 lines, exit 0
```

37 = 36 pre-existing + `W04 S225 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes`; S227 adds no diagnostic.

Readlink probe, my scratch tree, no lane tool or lane process touched:

```
argv target: /fast/scratch/hyaku/souji-r33/SourceProcFd/probe/a//worker.out
readlink    : /fast/scratch/hyaku/souji-r33/SourceProcFd/probe/a/worker.out
pipe fd1    : pipe:[166194168]
```

## Findings

1. **The URL is already carried four times.** `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md:104, :107, :116, :117` — S083 (fd entries and non-path link contents), S086 (supersedes S083's teaches), S095/S096 (permission rule). S225's scope is the returned string itself (`type:[inode]`, `anon_inode:[file-type]`) and is disjoint from S096; the machine signal is the one new W04. L1 chooses row-versus-fold: the round-32 Gate precedent (`corpus/lessons/round-32.md:25`, "NOT APPENDED as a row; ADMIT as source through `S063`") would fold the anon_inode sentence into S086 instead of adding S225. The draft row is delivered either way.
2. **The page states no `(deleted)` suffix for an fd target.** Sweep over the fetched bytes: `deleted` 0 matches. A residue row that cites proc_pid_fd(5) for a deletion marker would be grounding on nothing; the F5 limit recorded for S082–S085 stands unchanged.
3. **The page states no slash normalisation.** It gives the format and the non-path targets only. With the measured return (double slash of the `open` argument absent from the readlink output), the O4 mechanism needs both S224 (POSIX pathname resolution of repeated slashes) and this row; proc_pid_fd(5) alone would be a false ground for it. [INFERENCE] the trailing-slash mismatch itself: literal pattern `//souji-census-now.*/*` at `tools/souji-census.sh:1990` cannot match a one-slash path; the same shape repeats at `:2906` and `:2970`, which is why the base reading counted ten false failures rather than two.
4. **Landing order matters for the used-by cell.** `corpus/lessons/round-33.md` does not exist at the prereg commit, so the row alone makes `validate` red with exactly `E11 S225 missing used-by corpus/lessons/round-33.md` — the reading delivered as run A. Landing the lesson and the row in one commit keeps validate clean; the row must not point at a lesson that never lands.
5. **Rejection candidate is clean but empty on this teaching.** `readlink(2)` (HTTP 200, 18 306 bytes, sha256 `79a58d6c…11d93`) sweeps to `type:[` 0, `pipe:[` 0, `anon_inode` 0 and sends the reader to `proc_pid_fd(5)` in SEE ALSO; its only adjacent remark is the `/proc` magic-symlink `st_size` zero caveat, which is a sizing note, not the returned string.
6. **Id allocation.** Highest id at prereg is S223; S224 (POSIX pathname resolution) and S226 (Python tempfile) are taken by sibling seats in `.ufo/waves/round-33/w1-spec.json` and `make-spec-w2.py`; S225 and the rejection id S227 are free at this wave.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-src-S225.md` — fetch receipt, anchor, quotes, row S225, rejection row S227, Gate block entry, validation receipts, measurement, limits.
- `.ufo/waves/round-33/w1/src-S225.html` — the fetched bytes (11 359 bytes, sha256 `3a50ddef6f2f3a4f1139dcef3299a5eadf8fc96514df9fcb329a3bffd47ff27e`); not committed by me.
- `.ufo/waves/round-33/w1/SwarmScribe39.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r33/SourceProcFd` removed at the end of the run; no tool was installed or upgraded (no pacman transaction, no `uv`/`npx` install), so there is no install to record.
