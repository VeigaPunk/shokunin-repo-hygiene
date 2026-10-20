STATUS: DONE — Gate quote is verbatim (22 words on both served versions) and its anchor locates; the S067 row's teaches cell overreaches by one clause ("only the direct child"), and its anchor cell omits the section that documents the run() kill.

# ReopenS067 — round 18, wave 2 (falsify C2 calibration; re-open of source S067)

Axis attacked: calibration — does the authority chain (lesson Gate quote → SOURCES row → taught claim) say exactly what the served page says, and nothing more?

## 1. Attacked claim

1. `corpus/lessons/round-18.md` Gate line for S067 records the quote `"If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess."` as verbatim from https://docs.python.org/3/library/subprocess.html, `(§ Popen, 22 words)`, served as "Python 3.15.0 docs, last updated Oct 20, 2026".
2. `corpus/SOURCES.md@5efb519` row S067 (line 85) cells scope / anchor / teaches are within what the page states.

## 2. Access record (observed 2026-10-20, this host)

| URL | served title | footer / last-updated line |
|---|---|---|
| https://docs.python.org/3/library/subprocess.html | `subprocess — Subprocess management — Python 3.15.0 documentation` | `Last updated on Oct 20, 2026 (20:57 UTC).` |
| https://docs.python.org/3.14/library/subprocess.html | `subprocess — Subprocess management — Python 3.14.8 documentation` | `Last updated on Oct 20, 2026 (20:36 UTC).` |

Host interpreter: `python3 --version` → `Python 3.14.8` (`/usr/bin/python3`) — so the row's "/3.14/ lines for host Python 3.14.8" names a real version, and the /3.14/ page self-identifies as 3.14.8.

Footer drift worth recording: wave 1's `SrcPySubprocess.md` recorded 19:47 UTC (/3/) and 19:51 UTC (/3.14/); the same URLs now serve 20:57 and 20:36 UTC. The docs regenerate intra-day, so only the date is stable — the row quotes the date only, which is the robust choice.

## 3. Quote check — verbatim

Extraction method: fetched each page to `/var/tmp/`, located the enclosing `<p>` of the sentence (markup `<em>start_new_session</em>`, `<code>…setsid()…</code>`), removed tags, unescaped entities, collapsed whitespace, then substring-compared the lesson quote.

```
pysub.html   TITLE: subprocess — Subprocess management — Python 3.15.0 documentation
 norm para: If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess.
 exact: True | words para: 22 | words quote: 22

pysub314.html TITLE: subprocess — Subprocess management — Python 3.14.8 documentation
 norm para: If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess.
 exact: True | words para: 22 | words quote: 22
```

`printf '%s\n' '<quote>' | wc -w` → `22`. The paragraph is exactly one sentence — no elision, no dropped trailing period, lowercase "true" preserved as served.

## 4. Located anchor (what the lesson's "§ Popen" resolves to)

- Enclosing `<section id="popen-constructor">`, heading rendered `Popen Constructor¶`; enclosing class entry `<dt … id="subprocess.Popen">` (anchor `#subprocess.Popen`). There is **no per-parameter anchor** — the parameter paragraphs live only in the constructor section.
- Position in that section: immediately after the `restore_signals` paragraph (`Changed in version 3.2: restore_signals was added.`) and immediately before `Availability: POSIX` + `Changed in version 3.2: start_new_session was added.`, which is in turn followed by the `process_group` paragraph.
- Usable URL anchor: https://docs.python.org/3/library/subprocess.html#popen-constructor (or `#subprocess.Popen`).
- The lesson's `(§ Popen, 22 words)` is shorthand for `§ Popen Constructor`; a reader searching "Popen" lands on the class entry and the sentence is one paragraph below `restore_signals`. Locatable, not the literal heading text — a labeling nit, not a wrong location.

## 5. SOURCES@5efb519 row S067 (line 85) — cell-by-cell

Exact cells (`git show 5efb519f00075d958c3d1109ef6fcb24c487eb87:corpus/SOURCES.md`, line 85):

- **scope**: `start_new_session and what a timeout does to the child; not descendant reaping`
  - First clause matches the anchored content. The exclusion is explicit.
- **anchor**: `Python 3.15.0 docs (footer "Last updated on Oct 20, 2026"), /3.14/ lines for host Python 3.14.8, opened 2026-10-20; § Popen start_new_session, § Popen.communicate timeout`
  - Version, footer date, and 3.14/host-version claims all verified true.
  - The `§ Popen start_new_session` anchor is right.
  - The `§ Popen.communicate timeout` anchor is right for the "not killed" half: the sentence `The child process is not killed if the timeout expires, so in order to cleanup properly a well-behaved application should kill the child process and finish communication:` is in the `Popen.communicate` entry (`#subprocess.Popen.communicate`, inside section `popen-objects`).
  - **Defect: the anchor does not name where `run(timeout)` is documented.** The taught claim `run(timeout) kills …` rests on a different paragraph: `A timeout may be specified in seconds, it is internally passed on to Popen.communicate(). If the timeout expires, the child process will be killed and waited for.` — that paragraph sits under `subprocess.run` in section `using-the-subprocess-module`, not under `Popen.communicate`. Following the row's own anchors, a reader finds the opposite-sounding "not killed" sentence and no kill sentence.
  - `"/3.14/ lines"` names no line numbers — dangling but not false.
- **teaches**: `start_new_session makes the child call setsid(); communicate(timeout) kills nothing and run(timeout) kills only the direct child — so a fixture must kill its session itself, the leak class behind 44 of the 58 orphans`
  - `start_new_session makes the child call setsid()` — supported.
  - `communicate(timeout) kills nothing` — supported by the verbatim "The child process is not killed if the timeout expires".
  - **Defect: `run(timeout) kills only the direct child` overreaches.** The page says only "the child process will be killed and waited for". It never speaks about descendants or process groups: full-text counts on the served /3/ page — `descendant` 0, `grandchild` 0, `process group` 0 (prose), `setsid` 2 (the quoted paragraph plus a cross-reference). "only" asserts descendant survival, which is exactly what the row's own scope cell excludes ("not descendant reaping"). The wave-1 report it cites says the same in as many words: "nothing on the page extends 'killed' to the child's own children" (`SrcPySubprocess.md` § 2). The predecessor draft row was also careful: "not a claim about process-group kill semantics, which the page does not state" (`ScribeRowsPy.md:26`).
  - Internal precedent for the correct pattern: row S070 (line 88) has the same shape of scope exclusion ("not a read-side block test") and its teaches cell honors it — "the read side has no such answer". S067 instead asserts the excluded thing.
  - `44 of the 58 orphans` is consistent with the lesson's R18-M2 (44 from r15-census-config + 14 from an uncommitted r17 copy = 58), but it is this round's measurement, not something this source teaches; the cell's "so a fixture must kill its session itself" is a sound cross-source inference (S065/S066/S067) presented with "so".

## 6. Verdict

**AGREE on the attack against the recorded quote: it is verbatim.** Exact single-sentence match on both the /3/ (3.15.0) and /3.14/ (3.14.8) pages; `wc -w` = 22; served version and footer date match the lesson; the anchor resolves to `popen-constructor` (`Popen Constructor`) and the paragraph's neighbourhood is as described.

**PARTIAL on the S067 row as written.** Scope is honest, the two named anchors locate, but (a) the teaches cell claims a descendant fact the page never states and its own scope excludes, and (b) the anchor cell omits `§ subprocess.run timeout`, the only place the "run kills the child" half is documented. Both are inference/bookkeeping defects, not fabricated quotations: the page is silent, not contrary.

## 7. Smallest fix

In the S067 row only (no change to the lesson Gate quote line):

- teaches: replace `run(timeout) kills only the direct child` with `run(timeout) kills the child process it started and waits for it (the page names that one child and says nothing about descendants)`.
- anchor: add `§ subprocess.run timeout` (and, optionally, write `§ Popen Constructor` instead of `§ Popen`) so the run-kill sentence has a citable location.

## 8. Commands run (all read-only; no lane code executed)

```
curl -sS https://docs.python.org/3/library/subprocess.html      -o /var/tmp/pysub.html
curl -sS https://docs.python.org/3.14/library/subprocess.html   -o /var/tmp/pysub314.html
python3 - <<'EOF' … # locate enclosing <p>, de-mark, compare quote, count words, map sections
EOF
printf '%s\n' '<quote>' | wc -w                      # → 22
grep -c -i "descendant\|grandchild" pysub.html pysub314.html   # → 0 and 0
python3 --version                                    # → Python 3.14.8
git -C <lane> show 5efb519…:corpus/SOURCES.md        # S067 at line 85, S070 at line 88
git -C <lane> show 5efb519…:corpus/lessons/round-18.md
git -C <lane> show 5efb519…:.ufo/waves/round-18/w1/SrcPySubprocess.md
git -C <lane> show 5efb519…:.ufo/waves/round-18/w1/ScribeRowsPy.md
```

Tooling: no installs or upgrades (nothing needed); `curl` + host `python3` 3.14.8 parsing only `/var/tmp` copies of the two pages; lane files read via read-only `git show` on named paths. No census/verify/quarantine tool run, no signals, no clone.

## 9. Remaining unknowns

- The `/3.14/` line numbers quoted inside `SrcPySubprocess.md` (:507-508, :726-728, etc.) were not independently reproduced (no text-browser line numbering used this round); the landed row cites no line numbers, so the Gate quote is unaffected.
- Whether the census fixture actually issues the session-wide kill (C1's code claim) is outside this source question and was not checked here.

Confidence: high on the verbatim/version/anchor facts (direct observation of both served pages); high on the overreach finding (absence established by full-text count and by wave 1's own wording); medium-high on the "smallest fix" phrasing preference only.
