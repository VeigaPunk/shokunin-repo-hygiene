STATUS: DONE — S068 quote is faithful (22 words, token-identical; one rendered sentence space normalized); the S068 SOURCES row's teaches cell overreaches on the census half.

# Attacked claim

The S068 record at tip 5efb519: the located quote in `corpus/lessons/round-18.md:36` (round-18 Gate, "Sources opened this round") and the S068 row in `corpus/SOURCES.md:86` (scope · anchor · teaches). Source URL: https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html, opened 2026-10-20.

# Observed facts

## F1 — quote is verbatim (agree)

Located anchor: § DESCRIPTION, field `(22) starttime` (HTML section `#DESCRIPTION`; host roff `/usr/share/man/man5/proc_pid_stat.5.gz:227-232`).

Served text (raw HTML, field 22, `/var/tmp/souji-r18w2-ReopenS068-procstat.html`, bytes at `jiffies` index 9989):

```
Before Linux 2.6, this value was expressed in
jiffies.  Since Linux 2.6, the value is expressed in
clock ticks (divide by <i>sysconf(_SC_CLK_TCK)</i>).
```

Recorded quote (`corpus/lessons/round-18.md:36`): "Before Linux 2.6, this value was expressed in jiffies. Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))." (field 22 starttime, 22 words).

Comparison (script, `/var/tmp`): tag-stripped + whitespace-collapsed served text == recorded quote, **word-order-identical: True**; **words: 22** both; `printf '%s' "<quote>" | wc -w` → `22` (cap in the Gate header is ≤25 words). The only byte-level difference is the roff sentence space: raw HTML has `jiffies.  Since` (two spaces, `repr` confirmed), the lesson normalizes it to one. No word or punctuation differs. The quote occurs exactly once in the page (the phrase "this value was expressed in jiffies" is unique to field 22; field 18's "Before Linux 2.6, this was a scaled value…" is a different sentence).

Served version / last-updated line (page footer):

```
Linux man-pages 6.19            2026-02-08               proc_pid_stat(5)
```

COLOPHON: "This page was obtained from the tarball man-pages-6.19.tar.gz fetched from … on 2026-09-09"; "HTML rendering created 2026-09-09". `mirrors.edge.kernel.org/pub/linux/docs/man-pages/` lists `man-pages-6.19.tar.gz` as newest (6.17, 6.18, 6.19), so the served page is not stale as of 2026-10-20. Host: `pacman -Q man-pages` → `man-pages 6.19-1`; host roff fields (5) pgrp / (6) session / (22) starttime carry the same labels and the same field-22 sentences.

## F2 — scope cell (holds; one nit)

`corpus/SOURCES.md:86` scope: "field order and units of pgrp, session and starttime; not boot-epoch or atomicity". The page numbers all fields and gives starttime's units (clock ticks, divide by sysconf(_SC_CLK_TCK)); pgrp/session are plain IDs with no units, so "units of pgrp, session" is a loose compound — nit only, no false claim about the source. "not boot-epoch" is correct (btime is in `/proc/stat`, not this page); "not … atomicity" is correct (the page says nothing about read atomicity).

## F3 — anchor cell (holds, every cell verified)

"Linux man-pages 6.19 (2026-02-08), opened 2026-10-20; § DESCRIPTION fields (5) pgrp, (6) session, (22) starttime; host man-pages 6.19-1" — version/date match the served footer; the three field labels match exactly (`(5) pgrp %d`, `(6) session %d`, `(22) starttime %llu`); `pacman -Q man-pages` → 6.19-1; host roff labels identical.

## F4 — teaches cell (overreach: session misattributed as the census's identity binder)

Cell: "starttime is clock ticks since boot (divide by sysconf(_SC_CLK_TCK)); session is field 6 — the key the fixtures use to kill a whole session and the proc census uses as an identity binder".

- "starttime is clock ticks since boot (divide by sysconf(_SC_CLK_TCK))" — supported by field 22 (the "since boot" half is the field's first sentence, "The time the process started after system boot."; the recorded quote covers the units half — the field-level anchor covers both).
- "session is field 6" — supported (`(6) session %d`).
- "…the key the fixtures use to kill a whole session" — supported:
  - `tests/fixtures/r15-census-config.py:282-288` (`fields[3] == str(session_id)` → SIGKILL each member, then `os.killpg`);
  - `tests/fixtures/r17-census-hygiene.py:159-162` (comment: "state/ppid/pgrp/session are fields 0–3");
  - `tests/fixtures/r18-census-bounded.py:415-417,448-456` (snapshot `"session": fields[3]`; comment "pgrp is field 5 and session is field 6"; kill sweep).
- "…and the proc census uses as an identity binder" — **false for the proc census**: `tools/souji-proc-census.sh:125` stores `PROC_SID=${fields[3]}` and `:354` prints it as the `sid` column, but the only PID-reuse identity check compares **starttime**: `:305` snapshots `… "$PROC_SID" "$PROC_STARTTICKS"`, `:314` takes the last token, `:316` `[[ $PROC_STARTTICKS == "$snapshot_start" ]] || continue`; `:321` age also uses `PROC_STARTTICKS`. `PROC_SID` is never compared anywhere in the tool (grep: only :125, :305, :354).
- The actual (session, starttime) pair identity check lives in the matrix runner, not the census: `census/round-18/run-matrix.py:71-82` returns `(fields[3], fields[19])`; `:115`/`:122` kill only if `info == (session_id, start_time)`.

So the row attributes to the proc census a use it does not have, while omitting starttime's real identity role there — the exact class of authority-row inaccuracy C2 is calibrated against (though it affects no measured number; severity low).

# Verdict

- **Agree** on the S068 quote: verbatim in words and punctuation, 22/22 words, located at § DESCRIPTION field 22 starttime; the sole difference is the rendered double sentence space after "jiffies." normalized to one space; served version 6.19 dated 2026-02-08 (not stale; host 6.19-1).
- **Agree** on the scope and anchor cells (with the units-of-IDs nit).
- **Disagree** with the teaches cell's census clause: "the proc census uses [session] as an identity binder" is not what `tools/souji-proc-census.sh` does — starttime is the reuse binder, session is an emitted column; the pair check belongs to `census/round-18/run-matrix.py`.

# Smallest fix

In `corpus/SOURCES.md:86`, replace the whole teaches cell

> starttime is clock ticks since boot (divide by sysconf(_SC_CLK_TCK)); session is field 6 — the key the fixtures use to kill a whole session and the proc census uses as an identity binder

with

> starttime is clock ticks since boot (divide by sysconf(_SC_CLK_TCK)) and the proc census's PID-reuse identity binder (age base); session is field 6 — the key the fixtures use to kill a whole session, emitted by the census as the sid column

No other cell needs a change. (If the author meant the pair check in the runner, name `census/round-18/run-matrix.py`, not "the proc census"; either way the census clause as written is false.)

# Exact commands (all read-only; no lane writes; no processes started; no tool installs)

```
read https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html      # field (22) starttime block + COLOPHON/footer
curl -sS -o /var/tmp/souji-r18w2-ReopenS068-procstat.html https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
                                                                    # http=200 bytes=20647; repr at idx 9989: 'jiffies.  Since Linux 2.'
python3 -c '<tag-strip compare>'                                    # word-order-identical: True; words 22; equal on words
printf '%s' '<quote>' | wc -w                                       # 22
curl -sS https://mirrors.edge.kernel.org/pub/linux/docs/man-pages/ | grep -o -E 'man-pages-[0-9.]+\.tar\.gz' | sort -uV | tail -3
                                                                    # man-pages-6.17 / 6.18 / 6.19.tar.gz
pacman -Q man-pages                                                 # man-pages 6.19-1
zcat /usr/share/man/man5/proc_pid_stat.5.gz | grep -n -A2 -E '^\.RI \((5|6|22)\)'
                                                                    # (5) pgrp :104-105; (6) session :107-108; (22) starttime :227-232
git -C <lane> show 5efb519…:corpus/lessons/round-18.md | grep -n 'Before Linux 2.6'
                                                                    # :36 (S068 entry)
git -C <lane> show 5efb519…:corpus/SOURCES.md | sed -n '86p'        # S068 row
git -C <lane> show 5efb519…:tools/souji-proc-census.sh | grep -n -E 'PROC_SID|PROC_STARTTICKS|snapshot_start|identity fields'
                                                                    # :104,:125,:305,:314,:316,:321,:354
git -C <lane> show 5efb519…:census/round-18/run-matrix.py | grep -n -E 'def process_info|fields\[3\]|fields\[19\]|info != \(session_id, start_time\)'
                                                                    # :71,:82,:115,:122
```

Tool installs/updates: none (no channel touched).
