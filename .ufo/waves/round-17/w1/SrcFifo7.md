STATUS: DONE — fifo(7)/open(2) ground the D2 blocking-open hazard for a FIFO; the "hardlinked" half is not stated by either page.

# SrcFifo7 — fifo(7)/open(2) source opening for S0?? (D2)

## Sources actually opened (access date 2026-10-20)

- https://man7.org/linux/man-pages/man7/fifo.7.html — fetched 2026-10-20, served HTML. Version/"last updated" line the page serves: page footer `Linux man-pages 6.19            2026-02-08                        fifo(7)`; COLOPHON: tarball `man-pages-6.19.tar.gz` fetched 2026-09-09; HTML rendering created 2026-09-09.
- https://man7.org/linux/man-pages/man2/open.2.html — fetched 2026-10-20, served HTML. Footer `Linux man-pages 6.19            2026-02-08                        open(2)`; same COLOPHON (tarball fetched 2026-09-09).
- Host cross-check: `man-pages 6.19-1` (pacman), `/usr/share/man/man7/fifo.7.gz` `.TH fifo 7 2026-02-08 "Linux man-pages 6.19"` and `/usr/share/man/man2/open.2.gz` `.TH open 2 2026-02-08 "Linux man-pages 6.19"` — the installed vendor page is the same revision as the served page, so the quote is pinned to a package too.

No tool was installed or upgraded.

## (1) Verbatim quote that answers the question

**fifo(7) § DESCRIPTION** (11 words, verbatim):

> Normally, opening the FIFO blocks until the other end is opened also.

Roff source (host 6.19-1) confirms the sentence across wrapped lines: `zcat /usr/share/man/man7/fifo.7.gz | sed -n '22,34p'` → `Normally,` / `opening the FIFO blocks` / `until the other end is opened also.`

Supporting verbatim, same section (15 words): "The FIFO must be opened on both ends (reading and writing) before data can be passed."

**open(2) § DESCRIPTION › `O_NONBLOCK` or `O_NDELAY`** (22 words, verbatim; roff 545-549):

> Neither the open() nor any subsequent I/O operations on the file descriptor which is returned will cause the calling process to wait.

**Answer to the question.** A blocking read-open of a FIFO with no writer never returns: `open(path, O_RDONLY)` waits for the other end. So if `$GIT_DIR/info/attributes` is a FIFO, any guard routine that opens it "to check it", and any git command whose attribute lookup reads it, wedges the per-repository census indefinitely — the failure is a hang, not an error row. D2's rule (classify the path first, refuse it, and issue no git call that could read it) is exactly the liveness consequence: to keep the run finite you must not perform a blocking read-open at all. A timeout would bound the hang but still spends the timeout per repository and still lets git start; refusing before any open is the only shape that preserves the one-line-per-repo contract.

Note the type boundary: these pages establish the blocking hazard for **FIFO special files**. They do not claim every non-regular type blocks — fifo(7) says nonblocking write-only open fails `ENXIO`, and open(2) `O_DIRECTORY` exists "to avoid denial-of-service problems if opendir(3) is called on a FIFO or tape device". The broader "non-regular" refusal is safe, but only the FIFO case is grounded here as a hang.

## (2) Drafted row — exact 11-column order, no `|` inside any cell

Next unused id is S051 (registry currently ends at S050); `S0??` left for L1 to number.

| S0?? | fifo(7) and open(2), Linux man-pages — https://man7.org/linux/man-pages/man7/fifo.7.html and https://man7.org/linux/man-pages/man2/open.2.html | docs | A | blocking-open liveness of a FIFO special file in a repository metadata path; not Git behavior and not hardlink policy | fifo(7) § DESCRIPTION "Normally, opening the FIFO blocks until the other end is opened also."; open(2) § DESCRIPTION O_NONBLOCK; Linux man-pages 6.19, .TH date 2026-02-08, HTML rendered 2026-09-09 | a FIFO read-open blocks until a writer opens it, so a guard that opens a non-regular metadata path before checking its type can hang forever; type-check and refuse without opening | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |

Status evidence: D2 is a lane change this round, so `mined` is the intended state, and the round's Gate must carry the URL/date/quote for the row anyway. **Caveat for L1:** `corpus/lessons/round-17.md` does not exist yet (`stat` → No such file or directory) and the registry census fails a `mined` row whose `used-by` path is absent. If that lesson is not landed with this row cited, write the row `queued` with `used-by` `—`; flip to `mined` when the lesson exists. No knowledge entry currently exists for this fact, so the lesson is the only honest `used-by`.

Scope honesty: the row does not ground "hardlinked". Keep the row's `teaches` to the FIFO case; a second source is needed to justify refusing a hardlinked regular file.

## (3) Contradiction check against the context's claim text

No statement on either page contradicts D2's **conclusion** (refuse before reading; keep the run finite). Both pages support the blocking hazard. Three statements narrow the **wording**:

1. fifo(7) § DESCRIPTION — the closest thing to a contradiction of "must never be read":

   > A process can open a FIFO in nonblocking mode. In this case, opening for read-only succeeds even if no one has opened on the write side yet.

   So "must never be read" is stronger than the source: a *nonblocking* read-only open does succeed without a writer. The defensible claim is "must never be opened **in blocking mode** by a path with no writer/timeout", not "a FIFO can never be read". D2's actual mechanism (no open at all) is still correct and simpler; only the justification text should say "blocking open" rather than "read".

2. fifo(7) § DESCRIPTION — qualifies blocking semantics but does not contradict refusal:

   > Under Linux, opening a FIFO for read and write will succeed both in blocking and nonblocking mode.

   An `O_RDWR` open would also not hang; the census has no reason to use one, so refusal remains the right policy.

3. open(2) § DESCRIPTION › `O_PATH` — shows a non-data inspection path exists:

   > The file itself is not opened, and other file operations (e.g., read(2), write(2), fchmod(2), fchown(2), fgetxattr(2), ioctl(2), mmap(2)) fail with the error EBADF.

   `O_PATH` is an alternative safe inspection technique; it does not contradict refusing, but it means "never read" is a chosen policy, not a physical necessity.

**Hardlink gap (not stated).** Neither page mentions hardlinks. `open(2)` treats a hardlink to a regular file as a regular file (`O_DIRECTORY` fails, ordinary read succeeds), so a hardlink cannot hang the guard by the mechanism quoted. The context's "hardlinked ... info/attributes" refusal therefore has **no support on these pages**; it needs an aliasing/scope argument (a hardlink lets repository metadata name content outside the repository) or its own source. Also note a type test cannot catch it: a hardlinked regular file is `S_ISREG`, so D2 needs an explicit `st_nlink > 1` branch separate from `!S_ISREG`, or the fixture will show a functional hole.

## Smallest fixes (advisory)

1. Land S051 as drafted; if `corpus/lessons/round-17.md` is not written this round, use `queued` + `used-by` `—` instead of `mined`.
2. In the D2 ground text, say "blocking read-open" rather than "must never be read"; the page supports the former exactly and the latter only as a policy choice.
3. Keep the hardlink refusal, but justify it as an aliasing test (`st_nlink > 1` on a regular file) and do not attribute it to fifo(7)/open(2).
4. Fixture: a FIFO at `$GIT_DIR/info/attributes` with no writer, run under a wall-clock timeout, must produce the `git-metadata-unsupported fifo <path>` stderr diagnostic and an `error` row with exit 0; a blocking implementation would hang and the timeout proves the red-before state.

## Commands run (with observed output)

```
$ man-pages 6.19-1                      # pacman -Q man-pages
$ zcat /usr/share/man/man7/fifo.7.gz | grep -n -i 'block\|both ends\|nonblocking'
25:The FIFO must be opened on both ends (reading and writing)
28:opening the FIFO blocks
31:A process can open a FIFO in nonblocking mode.
42:both in blocking and nonblocking mode.
$ zcat /usr/share/man/man7/fifo.7.gz | sed -n '22,34p'
The kernel maintains exactly one pipe object for each
FIFO special file that is opened by at least one process.
The FIFO must be opened on both ends (reading and writing)
before data can be passed.
Normally,
opening the FIFO blocks
until the other end is opened also.
A process can open a FIFO in nonblocking mode.
In this case,
opening for read-only succeeds
even if no one has opened on the write side yet
$ zcat /usr/share/man/man2/open.2.gz | grep -n -A4 'nonblocking mode'
545:When possible, the file is opened in nonblocking mode.
546-Neither the
547-.BR open ()
548-nor any subsequent I/O operations on the file descriptor which is
549-returned will cause the calling process to wait.
$ zcat /usr/share/man/man7/fifo.7.gz | grep -n '^\.TH'
6:.TH fifo 7 2026-02-08 "Linux man-pages 6.19"
$ zcat /usr/share/man/man2/open.2.gz | grep -n '^\.TH'
7:.TH open 2 2026-02-08 "Linux man-pages 6.19"
$ stat -c '%n %F %s' .../corpus/lessons/round-17.md .../.ufo/waves/round-17/w1
stat: cannot stat '.../corpus/lessons/round-17.md': No such file or directory (os error 2)
.../.ufo/waves/round-17/w1 directory 38
```

Verdict: **holds** for the blocking-open rationale of D2; **partial** for the claim as worded — the nonblocking-open statement narrows "must never be read", and the hardlink branch is not stated by either page.
