# R97ScoutSources — round 97 source re-opening and candidate verdict

Seat: R97ScoutSources (scout, leaf). Lane: souji-shokunin (`/home/vgpnk/Projects/shokunin/souji-shokunin`).
Date: 2026-11-09. Lane base under inspection: `210084b24de1dd1f1fd499f49b0c70744f099f5f`; the round's
instrument commit P1 is `053287d4eea5dc6c0e1aff9c2295cff0f0a2a3d9`.

Write set (this seat): this report and `.ufo/waves/round-97/w1/R97ScoutSources/`. Scratch (deleted at
the end): `/fast/scratch/hyaku/souji-r97/R97ScoutSources/`. No corpus, census, tools or fixture file was
edited; no git/jj state was touched; no commit or push was made.

## Verdict summary

1. **NO-FALSIFICATION of the two claims' counted quantities or predicate sentences.** Every round-97
   source row re-opened live verifies (hash, size, quote occurrence, word count, locator) **except
   S372's word count**, which is a corpus-cell defect, not a claim defect.
2. **DEFECT 1 — S372's anchor cell states 14 words; the quoted sentence has 13** (§3). A corpus-cell
   defect in the row this round added.
3. **DEFECT 2 — the S372 row is malformed: 7 cells, not the contract's 11** (§4). It breaks the
   corpus's own "malformed rows must print 0" census gate (0 at the lane base, 1 at P1) and hides the
   row from the enum and used-by checks.
4. **DEFECT 3 — the C1 claim's A2 mechanism clause describes a reordering the instrument does not
   perform** (§5). The r97 hook **removes** the traceback print from the excepthook/thread channels
   rather than reordering the write before it; the printed traceback is gone, not deferred. The
   sentence's *effect* (the blocking print cannot hold the exit hostage) holds, and no counted
   quantity moves, but the mechanism as written is false of the committed bytes.
5. **One candidate source adjudicated: `write(2)` §ERRORS EAGAIN → ADMIT** (tier A docs), with the
   scope narrowed to what the page says (§6).
6. The `S365/S366/S367` → `S369/S370/S371` supersession chain that the round's knowledge entry relies
   on is verified live and is internally consistent; the r97 rows do **not** inherit the superseded
   rows' over-claims (§2).

## 1. What was re-opened live (all three round sources)

Fetched with `curl -sSL` into the seat scratch dir on 2026-11-09 (HTTP 200 for each), then compared
byte-for-byte and tag-stripped-word-for-tag-stripped-word against the committed captures.

| row | URL | recorded sha256 in row | capture sha256 | live sha256 | live bytes | verdict |
|---|---|---|---|---|---|---|
| S372 | docs.python.org/3/library/sys.monitoring.html | `2b2817933633296ad7c667916d34b9d6f20b5e079a927527dae68ec37d1b3a4c` | `2b281793…` (census/round-97/srcs/monitoring.html) | `2b281793…` | 74653 | **byte-identical to live** |
| S368 | man7.org/linux/man-pages/man2/setsid.2.html | `52cbc1904742df69556104f71d3279f93581756579881c85cee8e37be37c7f30` | `52cbc190…` (census/round-96/srcs/setsid.2.html) | `52cbc190…` | 11555 | **byte-identical to live** |
| S370/S366 (os.set_blocking) | docs.python.org/3/library/os.html | `078e69b12c66fd922353577d209e5a7c2f82a70b1b65eafe64a7910e635427fe` | `078e69b1…` (census/round-96/srcs/os.html) | `984ac6612fe5f556364d42c3ec24f3f3d94ae64a3eb815a0626f994c1ee6b8e4` | 791364 | same size, **1 word differs** (the Sphinx "Last updated on … (04:42 UTC)" → "(08:08 UTC)" footer) |

The S372 row's own `sha256` also equals the **committed blob** at P1:
`git show 053287d4:census/round-97/srcs/monitoring.html | sha256sum` → `2b2817933633296ad7c667916d34b9d6f20b5e079a927527dae68ec37d1b3a4c`
(= the worktree file = the live fetch). The r96 monitoring capture (`cd85fa73…`) is a *different* page
build (footer timestamp `04:42 UTC`); the r97 capture is the `08:08 UTC` build, which is what the live
server serves now. Diffing the tag-stripped text of the r96 capture against the r97/live page gives
exactly one differing token — the timestamp — and the RERAISE quote is unchanged. So the round's
"new capture" is a genuine re-fetch of the same page, and its digest is honest.

Reproducer (read-only, lane root):
```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git show 053287d4eea5dc6c0e1aff9c2295cff0f0a2a3d9:census/round-97/srcs/monitoring.html | sha256sum
sha256sum census/round-97/srcs/monitoring.html
curl -sSL https://docs.python.org/3/library/sys.monitoring.html | sha256sum   # -> 2b281793...
```

### Per-row verification table (hash / size / quote / count / locator)

Method for every row: fetch live → HTML-strip tags → `html.unescape` → collapse whitespace → count the
row's quoted sentence's occurrences and its whitespace-token word count → locate the row's named
section by heading position. "occ_cap" = occurrences in the committed capture, "occ_live" = occurrences
in the live fetch.

| row | row sha == capture sha | live bytes == capture bytes | quote words stated → actual | occ_cap / occ_live vs stated | locator names the right section |
|---|---|---|---|---|---|
| S372 (RERAISE) | yes | **yes** | 14 → **13** ✗ | 1 / 1 vs stated 1 ✓ | yes — `id="monitoring-event-RERAISE"` sits under `h2 Events` (page pos 22807) before `h2 Turning events on or off` (43636); the row's "§ Events" is right ✓ |
| S368 (setsid) | yes | yes | 17 → 17 ✓ | 1 / 1 ✓ | yes — quote at tag-stripped pos 665, after `DESCRIPTION` (156) and before `RETURN VALUE` (1059) ✓ |
| S369 (EH) | yes | no (1 footer word) | 4 → 4 ✓ | 1 / 1 ✓ | yes — under `h2 Events` ✓ |
| S370 (set_blocking) | yes | no (1 footer word) | 9 → 9 ✓ | 1 / 1 ✓ | yes — `id="os.set_blocking"` under `h2 File Descriptor Operations` (121044), next h2 `Files and Directories` (254166) ✓ |
| S371 (start_new_session) | yes | no (1 footer word) | 22 → 22 ✓ | 1 / 1 ✓ | yes — first occurrence under `h3 Popen Constructor` (55311), next h3 `Exceptions` (97864) ✓ |
| S365 / S366 / S367 | yes | no (1 footer word) | 4→4, 9→9, 22→22 ✓ | 1/1 each ✓ | yes — same entries as S369/S370/S371 ✓ |
| S360–S364 (base crash rows) | yes | no (1 footer word) | 11→11, 7→7, 15→15, 15→15, 25→25 ✓ | 1/1 (S363 = 2/2 vs stated 2) ✓ | yes — `sys.excepthook` (h1 sys), `threading.excepthook` (h2 Reference), `os._exit` (h2 Process Management), `Popen.returncode` (h2 Popen Objects), atexit intro (h1 atexit) ✓ |

**Cross-check on the counting convention.** Every other row in the registry that carries a
`(N words, occurrence count M)` cell was re-counted the same way: 19 such rows, and 18 of them match
their stated word count and occurrence count exactly (S354–S371). The single exception is S372.
So the corpus's own convention is satisfied by 18/19 rows and broken by exactly the row this round
added.

## 2. Do the rows claim more than the quotes say? (the S365/S366/S367 → S369/S370/S371 chain)

Checked each row's own `teaches` cell against its own quoted sentence:

- **S365** (EH, quote "An exception is handled.") taught that a top-level-handled SystemExit is declared
  *and* that a `finally` does not clear — the second half is not in the quote.
- **S366** (set_blocking) taught that a raw `os.write` on a momentarily non-blocking fd 2 cannot block on
  a full undrained pipe — not in the quote ("Set the blocking mode of the specified file descriptor.").
- **S367** (start_new_session) taught the group-kill consequence — not in the quote.
- **S369 / S370 / S371** each open `supersedes S0NN —` and state exactly what the page does and does not
  say: S369 "the page defines the event as handling; the r96 trade … is measured in plans/round-96.md A1,
  not sourced here"; S370 "the page sets the flag; the full-pipe EAGAIN consequence is write(2) semantics
  (not in the corpus)"; S371 "process groups and the group-kill consequence are NOT stated by this
  sentence and are sourced by S368".

**The r97 material does not inherit the superseded over-claims.** The r97 knowledge entry
`corpus/knowledge/crash-channels-beyond-excepthook.md` (r97 audit section, lines 128-142) cites **S372**
for the latch and states the limits itself: "S369 rules finally/re-raise firing out of the EH entry's
scope and S372 states only that a re-raise fires RERAISE; neither states the ordering the latch relies
on." The preregistration repeats the same limit (`census/round-97/preregistration.txt:79-80`).
The preregistration's C1 wording itself attributes the ordering to an observation, not to S372:
"the EH/RERAISE interleaving (EH, RERAISE, EH, RERAISE on a terminating finally; no RERAISE on a caught
exit) is the shape the predicate relies on, not a documented guarantee".

**Independent check of the disclosed observation (CPython 3.14.8, this host).** I registered RAISE,
EXCEPTION_HANDLED and RERAISE callbacks and recorded the event order for the four relevant shapes:

| shape | event order (frame / id) | distinct exception ids |
|---|---|---|
| x1 module-level `try/finally`, terminating | RAISE(helper) RAISE(<module>) EH(<module>) **RERAISE(<module>)** EH(<module>) **RERAISE(<module>)** RAISE(<module>) | 1 |
| x2 module-level explicit `raise` | RAISE(helper) RAISE(<module>) EH(<module>) **RERAISE(<module>)** EH(<module>) **RERAISE(<module>)** RAISE(<module>) | 1 |
| t1 caught at module level (no `finally`) | RAISE(helper) RAISE(<module>) EH(<module>) | 1 |
| t4 module-level `raise saved` then caught | RAISE(helper) RAISE(<module>) EH(<module>) RAISE(<module>) EH(<module>) — **no RERAISE** | 1 |

This reproduces exactly the interleaving the preregistration discloses ("EH, RERAISE, EH, RERAISE on a
terminating finally; no RERAISE on a caught exit"), and the RERAISE fires **for the same exception
object** (one distinct id per shape) — which is the property the latch's `_SOUJI_ELIG[id(exc)]` keying
depends on. The preregistration's stated limit (i) — "A module-level `finally` whose exception is caught
by the enclosing `except` (elig_fin_then_caught) keeps the mark by the same latch (it stays errored)" —
also holds on this host: a module-level `try/finally` nested inside a `try/except SystemExit` produces
RAISE, RAISE, EH, RERAISE, EH, RERAISE, EH (a RERAISE *is* present), so the pending candidate is
cancelled and the mark survives. Run under the committed r97 hook that shape exits **70** with the
crash marker `SOUJI-R97-CRASH SystemExit first raised in raiser() of the main script` — i.e. errored, as
the preregistration states. No falsification.

## 3. DEFECT 1 — S372's anchor cell states 14 words; the quoted sentence has 13

**Exact defective text** (`corpus/SOURCES.md:311`, the `anchor` cell of row S372):

> § Events, the `sys.monitoring.events.RERAISE` entry: "An exception is re-raised, for example at the end of a finally block." (14 words, occurrence count 1)

**Measured**: the quoted sentence as it appears in the whitespace-normalized tag-stripped text of both
the committed capture and the live page is **13** whitespace-separated tokens, and it occurs **exactly
once** (the stated occurrence count is correct). Token count: `An(1) exception(2) is(3) re-raised,(4)
for(5) example(6) at(7) the(8) end(9) of(10) a(11) finally(12) block.(13)`. `wc -w` on the quoted
string returns 13.

Reproducer:
```
python3 -c 'q="An exception is re-raised, for example at the end of a finally block."; print(len(q.split()))'   # 13
```
and, from the corpus root, the row's own count cell versus the same count applied to the 18 sibling
rows with the same cell form (18/18 match; S372 is the sole mismatch — see §1).

**Scope of the defect**: the sentence and its occurrence count are right; only the stated word count is
off by one. This is a **corpus-cell defect**, not a falsification of a C1 or C2 claim sentence: the
preregistration quotes the same 13-word sentence (line 29-30) and does not state a word count for it,
and the count appears nowhere in either claim. The corpus is append-only per `SOURCES-CONTRACT-v1`
rule 2 (`anchor` is immutable; a correction is a new row whose `teaches` opens `supersedes S0NN —`),
so this must be routed to the L1 as an amendment, not edited in place. The L1's options: a superseding
row S373 that corrects the count, or (if the L1 judges a same-round row's anchor cell fixable within
the round) a logged correction. I do not edit `corpus/` — that is the L1's integration call.

## 4. DEFECT 2 — the S372 row is malformed: 7 cells, not the contract's 11

`corpus/SOURCES.md:311` (S372) has **8 pipe characters → NF=9**, where every other registry row has
NF=13 (11 columns). The row ends after its `teaches` cell; the `status`, `opened`, `recheck` and
`used-by` cells are **absent**, and the used-by path was appended into the `teaches` cell as prose
("Used-by: corpus/knowledge/crash-channels-beyond-excepthook.md") instead of occupying the `used-by`
column.

Measured consequences, using the contract's own census commands
(`SOURCES-CONTRACT-v1.md` §Census, copied verbatim at `census/round-12/sources-census.sh:5-16`):

| census command | lane base `210084b2` | at P1 `053287d4` (HEAD) | expected |
|---|---|---|---|
| malformed rows (`NF!=13`) | **0** | **1** (S372) | 0 |
| status histogram | `mined=247 queued=14 rejected=32` | `mined=247 queued=14 rejected=32` **plus one row with an empty status** | no empty bucket |
| tier histogram | `A=280 B=10 C=3` | `A=281 B=10 C=3` | — |
| enum-violation check (`NF==13` only) | silent | **silent** — the row is skipped because its NF≠13 | must print nothing |
| mined-used-by path existence (`NF==13` only) | — | **skipped for S372** — its used-by path is never checked | must print nothing |

Reproducer (lane root):
```
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md   # -> 1
git show 210084b24de1dd1f1fd499f49b0c70744f099f5f:corpus/SOURCES.md | awk -F'|' '/^\|S[0-9]{3}\|/ && NF!=13 {n++} END{print n+0}'   # -> 0
```

Both defects were introduced by **P1**, the round's own instrument commit: the lane base has a clean
registry (0 malformed rows, no empty-status bucket) and the P1 tree does not. The row's own `source`
cell is otherwise accurate (URL, HTTP 200, capture path, sha256, "Python 3.15 documentation", opened
2026-11-09 all verify), and the row's `scope` cell is honest and correctly bounded
("the EH/RERAISE interleaving on a terminating finally is NOT stated by this page and is an observation
on CPython 3.14.8, not a sourced claim").

**Neither defect falsifies a claim sentence.** C1's counted quantity (declared-exit shapes the hook turns
into 70: before 2, after 0, over the 14-shape table) and C2's (conforming arms of 20, before 20 with
survivors 1/2, after 20 with survivors=0) are unaffected by a registry cell's word count and by a
malformed row: the shape receipts in `census/round-97/controls/shapes-r97.txt` (mismatched=0),
`shapes-r95.txt`/`shapes-r96.txt` (mismatched=2 each) and the r97 commit's own instrumentation are
independent of `corpus/SOURCES.md`'s shape. I therefore report these as **DEFECTs for the L1 to
amend in `plans/round-97.md`**, not as claim falsifications.

## 5. DEFECT 3 — the C1 claim's A2 clause describes a reordering the instrument does not perform

**The exact claim sentence** (`census/round-97/preregistration.txt:33-35`, C1 CLAIM):

> reorders the excepthook/thread crash channels to write before the traceback print (A2), and restores fd 2's blocking mode in the no-free-tool-id fallback (A3).

**What the committed bytes do.** In the r96 hook the two channels *print* and then crash
(`census/round-96/c1-survivor-search.py:117-120` calls `sys.__excepthook__(t, v, tb)`; `:130-133` calls
`threading.__excepthook__(a)`; both then call `_souji_crash`). In the r97 hook
(`census/round-97/c1-survivor-search.py:133-136` and `:147-150`) **neither print call survives** — each
body is a single `_souji_crash(...)` call, and `_souji_crash` ends in `_SOUJI_EXIT(@RC@)` i.e.
`os._exit(70)` (`:115-131`), so control never returns to any print. The traceback is **not reordered
after the marker write; it is gone.**

**Measured**, same script, same hook bytes, host CPython 3.14.8:

| hook | rc | traceback printed | stderr |
|---|---|---|---|
| r96 | 70 | **yes** | `Traceback (most recent call last): … RuntimeError: boom\nSOUJI-R96-CRASH uncaught RuntimeError\n` |
| r97 | 70 | **no** | `SOUJI-R97-CRASH uncaught RuntimeError\n` |

The r97 code comment itself still describes the intent it does not implement — `# r97 (A2): crash FIRST
on the raw write, then print` (`:134-135`) — and the r97 knowledge entry repeats it:
`corpus/knowledge/crash-channels-beyond-excepthook.md:137-139` says `_souji_excepthook`/`_souji_thread`
"now call the raw signal-safe `_souji_crash` **before the traceback print**". There is no traceback print
left on those channels to be before.

**Scope of the defect — what does and does not move.**
- The *effect* the clause names still holds, and holds a fortiori: the blocking `TextIOWrapper` print
  cannot hold the exit hostage on a full undrained pipe, because on those two channels there is no
  print at all. The r96 limit that motivated A2 is genuinely repaired.
- **No counted quantity moves.** C1's counted quantity is "declared-exit shapes the hook turns into 70
  (x1/x2): before 2 false-declares under the r96 hook, after 0" — a function of the shape table's exit
  codes, not of whether stderr carries a traceback. The search's kill rule reads stdout `ROW` lines and
  the returncode only (`c1-survivor-search.py:22`); stderr is never read. The ten-target summary and
  the 14-shape summary are unaffected.
- The `unraisable` channel is outside the clause's scope and still prints (`c1-survivor-search.py:141`
  `u.print_exception()`), so the corpus's r96 limit (1) about that channel is neither claimed to be
  fixed nor fixed.
- The loss is **undisclosed**: the r96 knowledge entry documents the traceback print as observed
  behavior of those channels (`:113`: "the excepthook and thread channels print their traceback through
  the blocking TextIOWrapper before the crash path"), and the r97 audit section describes only a
  reordering — it does not say the print was removed.

**Verdict**: this is a **wording defect in the C1 CLAIM sentence**, not a falsification of C1's count
or predicate. It is recorded here so the L1 can amend `plans/round-97.md` per Amendment 59 (a narrowing
amendment or an honest stop, never a silent repair). The L1's choice of wording: either restate the
clause as "removes the traceback print from the excepthook/thread channels so no blocking print can
hold the exit hostage", or restore the print *after* the crash write (impossible as written, since
`_souji_crash` exits — it would need the print moved into `_souji_crash` after the write and before
`os._exit`, or the exit deferred). A reviewer should also note that the *loss of the printed traceback
on those channels* is itself a diagnostic regression worth a sentence in the entry.

Reproducer: `.ufo/waves/round-97/w1/R97ScoutSources/r97scout-hook-order.txt` (the two-hook stderr
comparison, the r96/r97 source excerpts, and the print-call inventory).

## 6. Candidate source — `write(2)` §ERRORS (EAGAIN): ADMIT, tier A docs

The task asked for one more candidate on reaping a timed-out fixture's grandchildren or on non-blocking
writes. I screened two candidates on the reaping side and one on the non-blocking-write side, and
adjudicate the non-blocking-write one.

### Screened, not adjudicated (recorded for the L1's search log)

- `proc_pid_cmdline(5)` (man7.org, HTTP 200, 7918 bytes, sha256
  `1fc6816805fa28c1fe015700e7c40efc21d9bbc032e02c35a447004075a91f15`) — the file the r97 counter's
  `_reap_by_identity` reads (`/proc/<pid>/cmdline`, split on NUL). The corpus has **no** row for this
  page (`grep -c "proc_pid_cmdline" corpus/SOURCES.md` → 0), while it has rows for the sibling
  `/proc/pid/*` pages (stat, exe, cwd, fd, wchan, status). The page's own text names the failure mode
  that matters for an argv-identity key: "This read-only file holds the complete command line for the
  process, **unless the process is a zombie**. In the latter case, there is nothing in this file: that
  is, a read on this file will return 0 characters." I verified that on this host: an unreaped zombie
  child reads `/proc/<pid>/cmdline` as **0 bytes** (state `Z`), so an argv-identity scan silently misses
  a zombie grandchild. This is a real, citable gap — but it is a *second* candidate and the corpus
  already has two rejected `pipe(7)` rows for a neighbouring scope, so a new proc-row admission should
  be a separate decision with its own scope discipline (and PROVINCE forbids the lane from signalling
  inherited or unrelated processes, so a `proc_pid_cmdline` row must not be read as a licence to kill by
  argv). **Left to the L1 as a lead, not adjudicated here.**
- `prctl(2)` `PR_SET_CHILD_SUBREAPER` — fetched (HTTP 200, 26266 bytes, sha256
  `ef698f6c5aab0224e9bf238ea1820160797c15d0adcee8b37fcaac7297866810`). A subreaper would let the
  counter *adopt* orphaned grandchildren, but it changes the lane's process topology and PROVINCE
  constrains the lane to signalling only workers it spawned. **Not adjudicated; recorded as a
  non-candidate.**

### The adjudicated candidate

- **URL**: https://man7.org/linux/man-pages/man2/write.2.html
- **Accessed**: 2026-11-09, HTTP 200, 23203 bytes, sha256
  `82dd6ad3e998940915d9a9dc92d42afdb64ccb75121d350ae5ee42279d684ccc` (captured to the seat scratch
  dir; man-pages 6.19 per COLOPHON; the host's installed `man-pages 6.19-1` carries the same clause).
- **Located quote (25 words, §ERRORS → the first `EAGAIN` entry)**:
  > "The file descriptor fd refers to a file other than a socket and has been marked nonblocking ( O_NONBLOCK ), and the write would block."
  Occurrence count in the whitespace-normalized tag-stripped capture: **1** (the `EAGAIN or EWOULDBLOCK`
  variant for sockets is a different clause and is deliberately out of scope).
  Rendering note: the man-pages HTML renders the parentheses with inner spaces (`( O_NONBLOCK )`), the
  installed roff renders `(O_NONBLOCK)` and uses U+2010 in "non‐blocking"; the quote above is the
  HTML-capture rendering, matching how S368's and S372's quotes are taken from the capture.
- **Verdict: ADMIT**, tier A, kind `docs`, scope limited to *the errno a non-socket write returns when
  the write would block*, i.e. the `EAGAIN` clause only — not the socket `EAGAIN/EWOULDBLOCK` clause, not
  `ENOSPC`, not `EPIPE`/`SIGPIPE`, and not any statement about pipe capacity.
- **Reason (admission)**:
  1. **It fills a gap the corpus itself names.** S370's `teaches` cell says in so many words: "the
     full-pipe EAGAIN consequence is write(2) semantics (**not in the corpus**)". The round's C1 wording
     and the r97 knowledge entry both rest on the crash marker being dropped rather than blocking on a
     full undrained pipe, and that consequence has no source row today — S370 explicitly leaves it
     unsourced. A `write(2)` row is the missing ground.
  2. **It is exactly the mechanism the r97 instrument relies on, and the mechanism is measurable on this
     host.** Measured here: with fd 2 set non-blocking, filling the pipe raises `EAGAIN`
     (`BlockingIOError`) at 65536 bytes, and a subsequent write also fails `EAGAIN` (errno 11) rather
     than blocking. So `os.write` on a momentarily non-blocking fd 2 returns/raises instead of blocking —
     the behavior the r97 crash path depends on.
  3. **It does not widen the claims.** The page does not say a pipe's buffer is 64 KiB, does not say what
     "non-blocking" does to a pipe beyond the errno, and does not mention Python. It cannot be used to
     support "the marker write never blocks" as a blanket statement — only the errno clause.
  4. **Contract compliance (rule 1)**: URL + access date + a ≤25-word located quote with its location,
     all present; the page is tier A (primary man-pages, same revision family as the corpus's existing
     `kill(2)`, `open(2)`, `setsid(2)` rows); a rejection is *not* appropriate because the page is
     authoritative for this scope and does not overreach when scoped as above.
  5. **Duplicate-URL check**: the fleet census flags a repeated URL+scope (E04) unless `teaches` opens
     `supersedes S0NN —`. `man7.org/.../man2/write.2.html` appears **nowhere** in `corpus/SOURCES.md`
     today (verified: no `man2/write` URL in the registry), so a new row is not a duplicate-URL
     collision. It is also not in the `pipe(7)` rejected pair's URL space.
  6. **PROVINCE fit**: this is a documented-OS-semantics source of the same family as the corpus's
     existing rows for the lane's own census/watchdog/proc tooling; it grants no deletion authority,
     touches no credential material, and adds no new work surface. QUALITY's Q2 (docs vs. behaviour) is
     satisfied because the installed behaviour was measured and agrees (EAGAIN on a full non-blocking
     pipe, errno 11).
- **Flip condition** (for the L1's row): flip to `rejected` if a later man-pages revision drops or
  rewords the `EAGAIN` clause for non-socket descriptors, or if the lane's use of it turns into a
  claim about *pipe capacity* (which is `pipe(7)`'s clause, and `pipe(7)` already carries two rejected
  rows here — a new `pipe(7)` row would need its own scope and would inherit that rejection history).
  Flip to a narrower scope if the row is cited for anything beyond the errno clause.
- **Suggested row skeleton for the L1** (not written by this seat — `corpus/` is frozen for the wave
  and only the L1 integrates corpus changes):

  | id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
  |---|---|---|---|---|---|---|---|---|---|---|
  | S373 | write(2) — https://man7.org/linux/man-pages/man2/write.2.html (HTTP 200, 23203 bytes, sha256 82dd6ad3…, man-pages 6.19, opened 2026-11-09) | docs | A | the errno a write to a non-socket fd marked O_NONBLOCK returns when the write would block; not the socket EAGAIN/EWOULDBLOCK clause, not ENOSPC/EPIPE, not pipe capacity | § ERRORS, the first `EAGAIN` entry: "The file descriptor fd refers to a file other than a socket and has been marked nonblocking ( O_NONBLOCK ), and the write would block." (25 words, occurrence count 1) | grounds S370's unsourced half: on a momentarily non-blocking fd a write that would block fails with EAGAIN instead of blocking, which is why the crash marker is best-effort and the exit code is the verdict (measured on 3.14.8: errno 11 at a 65536-byte pipe) | queued → mined when cited | 2026-11-09 | 365d | corpus/knowledge/crash-channels-beyond-excepthook.md |

## 7. What this seat tried that did NOT produce a finding (negative sweep)

- `grep -c "cmdline" corpus/SOURCES.md` → 1 (only the unrelated S263 Python command-line row): the
  `/proc/pid/cmdline` page has no corpus row (recorded as a lead, §6).
- `grep -c "write(2)" corpus/SOURCES.md` → 1 (S370's prose mention): no row cites the page.
- No corpus row anywhere cites `man7.org/.../man2/write.2.html`, so no duplicate-URL collision.
- The `pipe(7)` rows S243/S246 are both `rejected` for the *open-time block* scope; neither covers the
  pipe-capacity/EAGAIN clause, so they do not already ground what S370 leaves open — but they are
  rejected rows in that URL's space, which is why I did not nominate a `pipe(7)` row.
- Re-derivation of the r97 hook's event ordering on CPython 3.14.8 (§2) — consistent with the
  preregistration's disclosed interleaving; no deviation found.
- The r96→r97 supersession chain S365–S371 (§2) — consistent; the r97 material does not inherit the
  superseded rows' over-claims.

## 8. Tools, versions, installs

No tool was installed, upgraded or removed (the tooling directive's install channel was not needed;
`curl`, `python3` 3.14.8, `awk`, `grep`, `git` read-only plumbing and `man` were sufficient). No
network fetch reached anything outside `docs.python.org` and `man7.org`, and every fetched byte landed
in the seat scratch dir, which was deleted before this report was written. No git/jj write operation
was performed; `git show`/`git log` were read-only.

## 9. Evidence paths

- Report: `.ufo/waves/round-97/w1/R97ScoutSources.md` (this file).
- Seat dir: `.ufo/waves/round-97/w1/R97ScoutSources/` — holds the text receipts copied out of scratch
  before cleanup:
  - `r97scout-row-verification.tsv` — the per-row hash/size/quote/count/locator table of §1.
  - `r97scout-defects.txt` — the two defect reproducers of §3 and §4 with their command output.
  - `r97scout-candidate-write2.txt` — the candidate's fetch metadata, located quote, occurrence count,
    and the host EAGAIN measurement.
  - `r97scout-rera-order.tsv` — the CPython 3.14.8 event-order measurement of §2 (the four shape
    scripts plus `elig_fin_then_caught`, and the committed r97 hook's exit-70 runs on the two crash
    channels and on that shape).
  - `r97scout-hook-order.txt` — the r96-vs-r97 hook stderr comparison behind DEFECT 3 (r96 prints a
    traceback, r97 prints only the crash marker), the r96/r97 source excerpts of the two channels, and
    the print-call inventory.
- Scratch (deleted): `/fast/scratch/hyaku/souji-r97/R97ScoutSources/`.
