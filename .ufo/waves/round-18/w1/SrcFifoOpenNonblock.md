STATUS: DONE — open(2) at man7.org (man-pages 6.19, 2026-02-08) opened 2026-10-20; the ENXIO no-reader clause is located verbatim; draft row below; one boundary the C1 lesson must respect.

# Source item — open(2) ENXIO, writer-side no-reader probe

## Exact fetch record

- URL fetched: `https://man7.org/linux/man-pages/man2/open.2.html` (read natively; served 2026-10-20).
- Served version/last-updated line (page footer): `Linux man-pages 6.19            2026-02-08                        open(2)`.
- Colophon as served: "This page was obtained from the tarball man-pages-6.19.tar.gz fetched from ... on 2026-09-09"; "HTML rendering created 2026-09-09".
- Section anchors used: § ERRORS (first `ENXIO` entry), § O_NONBLOCK, § NOTES › FIFOs.

## Located quote (verbatim, 20 words)

> O_NONBLOCK | O_WRONLY is set, the named file is a FIFO, and no process has the FIFO open for reading.

- Anchor: § ERRORS, first `ENXIO` entry; man-pages 6.19 (2026-02-08), as served 2026-10-20; rendered lines 683–684.
- `printf '%s\n' '<quote>' | wc -w` → `20`.

Supporting lines, same revision (not part of the quote):
- § O_NONBLOCK (:331–350): "Neither the open() nor any subsequent I/O operations ... will cause the calling process to wait"; but "this flag has no effect for regular files and block devices".
- § NOTES › FIFOs (:888–891): "Opening the read or write end of a FIFO blocks until the other end is also opened".
- § ERRORS other `ENXIO` entries (:686–689): missing device special file; UNIX domain socket.

## Draft SOURCES.md row

Draft id `S064` — next free id at b576341; L1 renumbers if another wave-1 seat claims it. Registry cell contract taken from the header row of `corpus/SOURCES.md` (`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`).

| S064 | open(2) — https://man7.org/linux/man-pages/man2/open.2.html | docs | A | ENXIO as the deterministic no-reader answer for a nonblocking write-side open of a FIFO; not a read-side block test, a type classifier, or a race-free probe | Linux man-pages 6.19, page date 2026-02-08, HTML rendering 2026-09-09, opened 2026-10-20; § ERRORS first ENXIO clause (:683-684), § O_NONBLOCK (:331-355), § NOTES FIFOs (:888-891) | a nonblocking write open of a reader-less FIFO fails ENXIO immediately instead of blocking; the same errno also means a missing device node or a UNIX socket, and a read open has no symmetric failure | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md |

Row-shape notes:
- Shares open(2)'s URL with S062's anchor mention ("open(2) § O_NONBLOCK same revision") under a different scope, exactly as S057/S042 and S059/S045 share a URL across scopes; S062 grounds the blocking read open, this row grounds the ENXIO write-side answer. S062 itself is not changed.
- The `teaches` cell is prose because a literal `|` cannot sit unescaped in a pipe-table cell; the verbatim quote above is the record for the round-18 Gate line, matching the round-17 provenance pattern ("URL, access record and a ≤25-word located quote for each are in corpus/lessons/round-17.md Gate").
- `used-by` names `corpus/lessons/round-18.md`, which **does not exist at b576341** (read → "not found"). L1 must create it in the same round or LG-DANGLING-PTR will flag this row at the round tip.
- Recheck `on-release`: content tracks man-pages releases, like S062.

## What it teaches for souji r18 (C1)

1. **The fixture's no-reader check is exactly this clause.** `tests/fixtures/r17-census-hygiene.py:328-334` `unblock_fifos()` does `os.open(str(p), os.O_WRONLY | os.O_NONBLOCK)` and closes on success. ENXIO is the documented failure branch: no reader is attached, so the open cannot block; success means a reader was waiting and is now released. That is why cleanup cannot itself leave a second blocked process.
2. **The read side has no symmetric errno.** `open(2)` gives ENXIO only for `O_NONBLOCK | O_WRONLY`; § NOTES › FIFOs says any FIFO open blocks until the other end opens. So a `git` read-side open of `$GIT_DIR/info/attributes` cannot be made to fail fast by flags, which is why C1's bound must be an external process-group watchdog — not an open flag and not an errno check.
3. **ENXIO alone is not a metadata classifier.** The same errno covers a missing device special file and a UNIX domain socket (:686–689). A probe must establish the inode type first (the stat probe `guard_git_files` already performs at `tools/souji-census.sh:551-577`) or it will misread a socket/device as a reader-less FIFO.
4. **Nonblocking success is a snapshot.** A reader may close immediately after a successful probe, so "not ENXIO" means a reader existed at that instant. Adequate for fixture cleanup; not a durable production property.

## What it does NOT establish

- **Not that git ever opens nonblocking.** The clause describes the opener's own flags; it says nothing about how `git status` opens `info/attributes`, so it cannot ground "git would fail rather than hang".
- **No read-side "no writer" test.** `O_RDONLY | O_NONBLOCK` returns immediately whether or not a writer exists; no ENXIO analogue for a writer-less FIFO read open is documented.
- **Not about regular files or block devices.** § O_NONBLOCK (:344–350) says the flag "has no effect for regular files and block devices", so it says nothing about the regular/hardlinked `info/attributes` arm.
- **Not a bound on an already-blocked process, and not the C1 fix.** The watchdog, not ENXIO, bounds a `git` already stuck in `open(2)`.
- **Not a claim about kernel FIFO buffer limits.** The `ENOMEM` FIFO-buffer clause (:664–667) and pipe(7) limits are separate and are not grounded by this quote.
- **Not validation of the fixture's errno handling.** `unblock_fifos()` catches every `OSError`, so ENXIO, EACCES and EINTR are conflated; the page locates ENXIO, it does not prove the fixture distinguishes it.

## Verdict

- Source item: **holds**. The ENXIO sentence exists verbatim at the served revision with the stated meaning; the version line is present and quotable.
- "This grounds the C1 no-reader check": **holds for fixture-side release/detection only**; **fails** if extended to "the census can detect the blocked read open" or "ENXIO fixes the hang".

## Smallest fix

Add the row at the next free id (S064 if unclaimed) with `used-by corpus/lessons/round-18.md` created in the same round; put the verbatim quote plus § ERRORS anchor and `wc -w` 20 in the round-18 Gate record; in C1's lesson text, cite this row only for the fixture-side `O_WRONLY | O_NONBLOCK` probe and keep the process-group watchdog as the hang bound; never write that ENXIO detects a blocked read open.

## Exact commands run and outputs

1. `read https://man7.org/linux/man-pages/man2/open.2.html` — served `open(2) - Linux manual page`; footer `Linux man-pages 6.19            2026-02-08                        open(2)`; colophon tarball `man-pages-6.19.tar.gz` fetched 2026-09-09, rendering 2026-09-09.
2. `grep 'ENXIO|O_NONBLOCK|FIFO' artifact://89126` — hit `683|ENXIO  O_NONBLOCK | O_WRONLY is set, the named file is a FIFO, and`, `684| no process has the FIFO open for reading.`; also `331|O_NONBLOCK or O_NDELAY`, `888|FIFOs`, `889|Opening the read or write end of a FIFO blocks until the other end`.
3. `printf '%s\n' 'O_NONBLOCK | O_WRONLY is set, the named file is a FIFO, and no process has the FIFO open for reading.' | wc -w` → `20`.
4. `grep 'fifo|O_NONBLOCK|Nonblock|reader|block' tests/fixtures/r17-census-hygiene.py` — `331|fd = os.open(str(p), os.O_WRONLY | os.O_NONBLOCK)`, `332|except OSError:`, `328|def unblock_fifos()`.
5. `grep 'fifo|O_NONBLOCK|Nonblock|reader|block' tests/fixtures/r15-census-config.py` — `496|repo = init_repo(UNSAFE / "r-inc-fifo", ...)`, `497|os.mkfifo(repo / "fifo.inc")` (read-side include target, no nonblocking option).
6. `read tools/souji-census.sh:539-603` — `guard_git_files` stat-only probe at :551-577; comment "a FIFO or device is classified here, never touched by open(2)".
7. `read corpus/lessons/round-18.md:1-30` — not found.
8. `read corpus/SOURCES.md:44-113` — row contract and S051–S063; S062 already cites open(2) § O_NONBLOCK; no S064 exists.

Tool installs/updates: none.
