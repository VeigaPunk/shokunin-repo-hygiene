STATUS: DONE — S070 quote is verbatim at 20 words, anchor and served version match; row scope/anchor clean, teaches within bounds but owes one precision note.

# Reopen S070 — open(2) ENXIO: quote, anchor, version, row calibration

**Attacks:** C2 calibration's source record S070 as landed at `5efb519f00075d958c3d1109ef6fcb24c487eb87` — the quote in `corpus/lessons/round-18.md:38` (under `## Gate`, "Sources opened this round") and the row at `corpus/SOURCES.md:88` (scope, anchor, teaches). Question: verbatim or not, and do the cells overreach?

## Fetch record

- URL fetched: `https://man7.org/linux/man-pages/man2/open.2.html` → HTTP 200, no redirect (`url_effective` identical), fetched **2026-10-20T21:19:58Z**; 76,506 bytes; `sha256 d665489cadb85624d98fae03a8d8d06209030f32735cff8aeba949ad8491c789`.
- Served version/last-updated line (rendered `<pre>` line 1028): `Linux man-pages 6.19            2026-02-08                        open(2)`.
- COLOPHON: "This page was obtained from the tarball man-pages-6.19.tar.gz fetched … on 2026-09-09"; HTML rendering created 2026-09-09. This matches the row's `Linux man-pages 6.19 (2026-02-08)` exactly.

## Quote verification

- **Located anchor:** `§ ERRORS`, the **first of three ENXIO entries** — rendered pre-text lines **646–647** (next two ENXIO entries at 649 and 652; the native-markdown read showed them at 683–684). The claimed "first ENXIO entry" is exact.
- Rendered text (hard-wrapped in the page):
```
       ENXIO  O_NONBLOCK | O_WRONLY is set, the named file is a FIFO, and
              no process has the FIFO open for reading.
```
- Whitespace-normalized paragraph is exactly `ENXIO ` + the recorded quote; the recorded quote is a **verbatim substring** after unwrapping. The leading error label `ENXIO` is correctly omitted and the section is named, so nothing is lost.
- `wc -w` on the recorded quote = **20** (the `|` counts as a whitespace token; 19 if it were stripped). Both the lesson's "(§ ERRORS ENXIO, 20 words)" and the row are therefore counting the same way.
- Lesson quote vs page sentence: string equality **True**. Lesson quote vs SOURCES row: identical text.
- `§ O_NONBLOCK` anchor exists and backs "at once": "When possible, the file is opened in nonblocking mode. Neither the open() nor any subsequent I/O operations on the file descriptor which is returned will cause the calling process to wait." (pre 300–304), and "For the handling of FIFOs (named pipes), see also fifo(7)." (pre 321).

## Row cells (`corpus/SOURCES.md:88`)

| cell | content | assessment |
|---|---|---|
| scope | nonblocking write-open of a reader-less FIFO; not a read-side block test | **Accurate, no overreach.** It states exactly the source's reach and disclaims the read side. |
| anchor | Linux man-pages 6.19 (2026-02-08), opened 2026-10-20; § ERRORS first ENXIO entry, § O_NONBLOCK | **Accurate and locatable.** Both anchors exist; "first ENXIO entry" is verified; § O_NONBLOCK supplies the no-wait half of "at once" and explicitly delegates FIFO specifics to fifo(7) (already row S062). |
| teaches | O_WRONLY with O_NONBLOCK on a FIFO nobody reads fails ENXIO at once, so a fixture can prove no blocked reader remains; the read side has no such answer | **Within bounds under a broad reading; one precision note below.** First clause and "at once" are sourced. "The read side has no such answer" holds: a nonblocking read-open succeeds whether or not a writer exists (no ENXIO analogue), and a blocking read-open is a block test the scope already excludes. |

## The one residual (precision, not a defect)

The fixture's stalled process is a reader blocked **inside `open(O_RDONLY)`**, not in `read(2)`:

- `tools/souji-census.sh:2345` replaces `.git/info/attributes` with a FIFO, `:2349` `exec "$real_git" -C "$repo" "$@"` runs `git status`, and git's attribute open is `open_nofollow(path, O_RDONLY)` / `open(path, O_RDONLY)` (S064, attr.c:702-705). With no writer, the kernel blocks inside `open`.
- The ENXIO entry's condition is "no process has the FIFO open for reading". A process still inside `open` has not completed it, and **open(2) does not say** whether an in-progress opener counts. So the doc alone does not quite prove "no blocked reader remains".
- The claim is nevertheless true on Linux: `fs/pipe.c` `fifo_open` does `pipe->readers++` (line 1250) **before** `wait_for_partner(pipe, &pipe->w_counter)` (line 1259), and the `FMODE_WRITE` path returns `-ENXIO` only when `!pipe->readers` (lines 1271–1272). The probe therefore detects — and would even release — a reader blocked in open. Kernel source fetched 2026-10-20T21:20:11Z, HTTP 200, `sha256 547e3034b4588c67b34a31334a3a6abc0b79b929cc87aad0decd34e22b7b90b6`.
- Net: the fixture's assertion is sound and discriminating (a surviving opener makes the probe succeed, and the fixture reports "still has a reader"); only the attribution is loose. The row credits open(2) with a fact that lives in the kernel implementation.

## Verdict

**AGREE** with the record's factual core, with one precision caveat. The quote is verbatim (20 words), the anchor is the correct first ENXIO entry plus a real § O_NONBLOCK, the served revision matches the recorded man-pages 6.19 (2026-02-08), and the scope cell does not overreach. The teaches cell is operationally correct but closes "no blocked reader remains" on kernel behavior the cited page does not state; that is inference-grade closure presented as one sourced claim, not a quote or anchor error and not a defect in the fixture.

**Smallest fix:** append to the teaches cell "(kernel `fs/pipe.c` `fifo_open` counts an in-progress opener in `pipe->readers` before it waits, and write-open returns ENXIO only when `readers` is zero; open(2) does not state this)" and add that file at the host kernel revision as a companion source next to S062 — or, if no companion row is wanted, narrow the clause to "prove no process holds the FIFO open for reading".

## Provenance / bounds

- No lane file changed; only this report written. No `ALLOWED-EXEC` on this item, so no fixture, census, or gate was run; no process signalled; no `jj` run.
- Tool installs/upgrades: none (not needed).
- All commands were reads, exact-path greps, sha256sum, one HTTP GET of the source page and the kernel `fs/pipe.c`, and read-only `git show` at `5efb519…`.
