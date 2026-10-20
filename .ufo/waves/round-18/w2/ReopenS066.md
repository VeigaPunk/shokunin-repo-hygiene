STATUS: DONE — quote verbatim (21 words, § DESCRIPTION), anchor exact in served HTML and host roff :64-72; one teaches-cell overreach: "empty … pgid" is not taught by kill(2).

# Reopen S066 — kill(2) quote and SOURCES row

Attacked: C1's sourcing. `corpus/lessons/round-18.md:34` (Gate) carries the located quote for S066; `corpus/SOURCES.md:84` @ `5efb519` carries the row's scope / anchor / teaches cells. Nothing built by wave 1 was modified or re-measured.

## 1. Quote — verbatim, counted, anchored

Served page (read of https://man7.org/linux/man-pages/man2/kill.2.html, fetched 2026-10-20), DESCRIPTION, 4th "If" paragraph:

> If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid.

Recorded `corpus/lessons/round-18.md:34` (tip bytes, `git show 5efb519…:corpus/lessons/round-18.md`):

> `- **S066** https://man7.org/linux/man-pages/man2/kill.2.html (man-pages 6.19; \`SrcKill2\`, \`ScribeRowsJobs\`): "If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid." (§ DESCRIPTION, 21 words).`

Character-for-character identical (ASCII `-1`, `-pid`, comma after `-1`, final period). Word count:

```
$ printf '%s\n' 'If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid.' | wc -w
21
```

Matches the recorded "21 words". Second, independent rendering: installed roff, same revision.

```
$ zcat /usr/share/man/man2/kill.2.gz | grep -n 'less than'
66:is less than \-1,
$ zcat /usr/share/man/man2/kill.2.gz | sed -n '55,80p' | nl -ba -v55   # 64-72
64 If / 65 .I pid / 66 is less than \-1, / 67 then / 68 .I sig / 69 is sent to /
70 every process in / 71 the process group whose ID is / 72 .IR \-pid .
```

Concatenated :64-72 is exactly the recorded sentence, nothing more — so "host roff :64-72" is a byte-precise anchor, and `SrcKill2.md:175`'s recorded `71:the process group whose ID is` agrees.

## 2. Served version / last-updated

- Footer: `Linux man-pages 6.19            2026-06-05                        kill(2)`.
- Colophon: `This page was obtained from the tarball man-pages-6.19.tar.gz … on 2026-09-09`; `HTML rendering created 2026-09-09`.
- Host: `.TH kill 2 2026-06-05 "Linux man-pages 6.19"`.
- Lesson records "man-pages 6.19"; SOURCES records "6.19 (2026-06-05)" and "host roff … same revision". Both true. Installed man page and served page are the same revision and date.

## 3. SOURCES.md:84 cells @ 5efb519 (12 cells, verbatim)

| cell | value | check |
|---|---|---|
| scope | `signalling a process group by negative pid; not reaping or pgid reuse` | no overreach — the page does not teach reaping or pgid reuse; the exclusion is correct |
| anchor | `Linux man-pages 6.19 (2026-06-05), opened 2026-10-20; § DESCRIPTION, § ERRORS ESRCH/EPERM; host roff :64-72 same revision` | all four claims verified above; exact |
| teaches | `kill(-pgid, sig) reaches every process in the group, pid 0 means the caller's own group, so an empty or zero pgid must never reach the watchdog's kill` | first two clauses grounded; **"empty" half is not** (see below) |

Anchor detail: the served HTML exposes section anchors only (`#DESCRIPTION`, …), no per-paragraph id, so "§ DESCRIPTION" + the paragraph's opening words is the tightest locator the page permits; the lesson's `(§ DESCRIPTION, 21 words)` is the correct form. The `host roff :64-72` locator is stricter than the HTML one and is exactly right.

## 4. Defects

**D1 (real, teaches cell) — "empty … pgid" is not taught by kill(2).** `pid_t` is an integer; the syscall page cannot describe an empty argument string. What an empty PGID variable does is kill(1)/bash(1) argument parsing, and that page is not cited by this row. The two attributed seats contradict each other on exactly this point:

- `SrcKill2.md:107`: "That `kill -TERM -$pgid` or `kill -- -$pgid` in bash reaches `kill(-pgid, sig)` is kill(1)/bash(1); the syscall page says nothing about argument parsing."
- `ScribeRowsJobs.md:49`: "`kill 0` and an empty PGID both address the caller's own group (S065 limit)."

The landed cell inherited the scribe's unsourced half; the source seat had already excluded it. The grounded part is only `pid 0` (page: "If pid equals 0, then sig is sent to every process in the process group of the calling process."). Sibling rows show the "so …" application shape is conventional (S053, S057, S060), so the *shape* is not overreach; the *content* "empty" is.

**D2 (minor, teaches cell) — "reaches" is stronger than the page's "sent to".** The page's RETURN VALUE qualifies group success: "If signals were sent to a process group, success means that at least one signal was delivered", with EPERM/ESRCH in § ERRORS. SrcKill2's draft anchor cited § RETURN VALUE explicitly; the landed anchor dropped it while the verb was strengthened from "sent to" to "reaches". No landed claim depends on delivery-per-member, so this is wording, not consequence.

**Not defects, recorded for calibration:**
- Scope is *narrower* than `SrcKill2.md:119`'s draft scope (which also claimed the sig-0 probe, group-success return and ESRCH) — under-claim, safe direction; the residual § ERRORS locator in the anchor is cosmetic mismatch, not overreach.
- `ScribeRowsJobs.md:29,36` drafted the kill row as **S065**; the landed registry has it as S066 (S065 is now the bash `-m` row). Content attribution in the lesson holds; only the draft id moved.
- SOURCES rows carry no quotation column, so "verbatim" can only fail at the lesson Gate — it does not.
- No working-tree drift: `git diff --stat 5efb519 -- corpus/SOURCES.md corpus/lessons/round-18.md` → empty.

## 5. Verdict

Quote: **agree** — verbatim, 21 words, § DESCRIPTION, and the host-roff locator is exact. Scope and anchor cells: **agree** — no overreach (scope under-claims if anything). Teaches cell: **partial / disagree** — "empty … pgid" exceeds the cited page by one clause, contradicted within the wave by `SrcKill2.md:107`, and "reaches" drops the RETURN VALUE qualification the source seat had cited.

Smallest fix (one cell, `corpus/SOURCES.md:84`): change `so an empty or zero pgid must never reach the watchdog's kill` → `so a zero or empty PGID must never reach the watchdog's kill, and `kill 0`/empty-argv parsing belongs to kill(1)/bash(1)`; or, minimally, delete `empty or` and leave `a zero pgid must never reach the watchdog's kill`. If "reaches" is kept, restore `§ RETURN VALUE` to the anchor; otherwise write "is sent to". No tool installs; no lane code executed; no clone created; no processes signalled.
