STATUS: DONE — S065 quote is verbatim (15 words) and both Wayback stamps reproduce; scope and anchor cells hold, the `teaches` cell overreaches in two clauses.

# Frontier re-open — S065 (GNU Bash manual, The Set Builtin `-m`)

Attacked: the wave-1 Gate record `corpus/lessons/round-18.md:33` and the registry row `corpus/SOURCES.md:83` at tip `5efb519f00075d958c3d1109ef6fcb24c487eb87`. Question: is the recorded quote verbatim, is the anchor right, does the served version line exist, and do the `scope` / `anchor` / `teaches` cells claim more than the source they cite?

## Located anchor (served capture)

- Requested and served stamp: `web/20260930073822/` — captured HTML lines 142, 143, 160 carry that exact stamp; HTTP 200, 27 967 bytes.
- Section heading: `set-live.html:173` `<h4 class="subsection" id="The-Set-Builtin-1"><span>4.3.1 The Set Builtin…` — the only content id on the page. There is **no** `#-m` fragment; the item is the id-less `<dt>` at `set-live.html:266`.
- Quote site: `set-live.html:266-271`
  - `266: <dt><code class="code">-m</code></dt>`
  - `267: <dd><p>Job control is enabled (see <a class="pxref" href="Job-Control.html">Job Control</a>).`
  - `268: All processes run in a separate process group.`
  - `269-270: When a background job completes, the shell prints a line / containing its exit status.`

So the exact locator is § 4.3.1 → `-m` → dd sentences 1-2: `#The-Set-Builtin-1` + `dt -m` (line 266). The row's "§ 4.3.1 -m" points at the right place but cannot deep-link the option.

## Quote check

Recorded: `"Job control is enabled (see Job Control). All processes run in a separate process group."` (`corpus/lessons/round-18.md:33`).

- Verbatim: yes. The served bytes are the two sentences with the `pxref` anchor rendered as its text `Job Control`; the only difference from the HTML is whitespace collapsing at the line break (`:267`→`:268`). Nothing substituted, nothing added.
- `wc -w` = **15** (`printf '%s' 'Job control is enabled (see Job Control). All processes run in a separate process group.' | wc -w` → `15`), matching the lesson's "15 words" and inside the ≤25-word convention.
- Truncation: the third sentence (exit-status line for a completed background job, `:269-270`) is dropped at a sentence boundary without an ellipsis. That sentence is exactly the notification behaviour the scope cell disclaims, so the truncation does not shift meaning toward the row's claim. No misrepresentation; a re-opener should know the quote is "dd sentences 1-2".

## Served version / last-updated line

`set-live.html:20-25` (inside the makeinfo head comment opened at `:20`, closed at `:54`; `<meta name="Generator" content="makeinfo">` at `:41`):

```
20: <!-- This text is a brief description of the features that are present in
21: the Bash shell (version 5.3, 18 May 2025).
23: This is Edition 5.3, last updated 18 May 2025,
24: of The GNU Bash Reference Manual,
25: for Bash, Version 5.3.
```

Calibration note: this line is served bytes but is an HTML comment — it is **invisible in rendered text** (my first render of the capture omitted it entirely). The row's "Edition 5.3 (18 May 2025)" is therefore true and reproducible only by reading the source bytes; a render-only re-open can conclude the claim is unsupported. Edition matches the host interpreter recorded at `census/round-18/c1-matrix-worktree.json` (`bash_version = GNU bash, version 5.3.20(1)-release`), so "Edition 5.3" is the right edition for this lane, not a stale one.

## Access record and companion capture

- Live probe reproduces the row's recorded failure: `curl -sS -m 25 -o /var/tmp/... https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html` → `curl: (28) Connection timed out after 25001 milliseconds`, rc 28. The row's "live gnu.org timed out 2026-10-20 (curl exit 28)" is accurate today.
- Wayback fetch: `http=200 bytes=27967`, sha256 `d510366a59081f7f301e7a723c413b81f7b922e2eec99d7f83b9323ab6606740`.
- Companion "Job Control Basics capture 20260803220758": fetched `http=200 bytes=12769`, sha256 `b193011ef36e663e9ee5e71aae6aab2786e5cf63196cf66aea9cb443dc079e08`; the only 14-digit stamp in the served page is `20260803220758`, so the served capture is the cited one (no nearest-capture redirect).
- Companion edition comment sits at `jc-basics.html:18-21` (same "Edition 5.3, last updated 18 May 2025").

## Cell-by-cell overreach check (`corpus/SOURCES.md:83`)

Table header (`corpus/SOURCES.md:17`): `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.

1. **scope — holds.** "what `set -m` changes for background jobs in a script; not notice/tty behaviour". Narrower than the quoted sentence ("All processes") and correct for the use: `tools/souji-census.sh:1478-1481` is `set -m` → `"$@" > … 2> … &` → `worker=$!` → `set +m`, a non-interactive script backgrounding one repository job. The exclusion is coherent: the quote stops before the -m entry's notification sentence, and the tool restores `set +m` before it waits (`:1481`), so the notification path is off by the time the job state changes. No overreach.
2. **anchor — holds, two precision nits.** Live-timeout, Wayback stamp, edition, § number and companion stamp all reproduce (above). Nits, not overreach: (a) "Edition 5.3 (18 May 2025)" comes from a head **comment**, `set-live.html:23`; (b) no `#-m` anchor exists, only `#The-Set-Builtin-1` at `:173`.
3. **teaches — overreaches in two clauses.** Cell: "with job control enabled every job runs in its own process group, which is what lets the census watchdog signal one repository's whole tree and nothing else".
   - "every job runs in its own process group": **neither cited page says this.** The `-m` sentence's subject is "processes", not jobs; the companion capture never states per-job group creation — its whole § 7.1 vocabulary is "The shell associates a job with each pipeline", "each process has a process group ID", "Processes that have the same process group ID are said to be part of the same process group" (normalized `jc.txt`, § 7.1). The per-job statement is the correct reading of bash's implementation and matches the code, but it is a step past the row's stated evidence. The row's own `anchor` cell cannot support it.
   - "one repository's whole tree": an absolute the mechanism does not give. The signal is `kill -TERM/-KILL -- "-$pgid"` (`tools/souji-census.sh:1495,1497`), i.e. group membership, and a child that calls `setsid()`/`setpgid()` leaves that group. The tool itself demonstrates the escape: its watchdog is launched as `setsid bash -c '…'` (`:1482`) precisely so it is outside the worker's group and survives the group kill it issues. Group kill reaches the job's processes **that stay in the group**; "whole tree" is false for any repo command that detaches.
   - "and nothing else" holds: `kill -- -pgid` addresses only that group, and the setsid watchdog is outside it.
   - Code attribution is otherwise right: the group does come from `set -m` (not from `setsid`); `setsid` at `:1482` belongs to the watchdog, and the parent's own fallback kills `-- -"$worker"` (`:1547,1578,1580`), so "the watchdog" is the primary but not the only signaller. `setsid` availability is a hard requirement (`:2617`).

Boundary note for C1 (not S065's claim): the r18 fixture asserts the timeout line by membership — `expected not in run.stderr.splitlines()` (`tests/fixtures/r18-census-bounded.py:809-810`) — so a stray `-m` job-status line on census stderr would not fail B1-B8. The B-cases therefore do not test the "stderr is exactly `souji-census: repo-timeout <N>s <repo>`" wording; they test that the line is present. I did not run any census, so this is [INFERENCE] from the fixture source, not an observed failure.

## Verdict

- Quote verbatim + word count + anchor section + access record: **AGREE** — byte-for-byte after whitespace/link normalization, 15 words, both captures reproduce at the cited stamps, live failure reproduces (curl 28).
- Row `scope`: **agree** (no overreach).
- Row `anchor`: **agree**, two precision nits (edition line is a head comment; no `#-m`); neither changes the claim.
- Row `teaches`: **DISAGREE in part** — "every job runs in its own process group" exceeds both cited pages, and "whole tree" is not guaranteed by group membership (measured escape is demonstrated by the tool's own `setsid` watchdog at `tools/souji-census.sh:1482`). Keep the row; fix the cell. This does not affect C1's own wording, which says "its own process group" and "the group survives SIGKILL", not "whole tree".

## Smallest fix

Rewrite the `teaches` cell of `corpus/SOURCES.md:83` to the quote's own terms, e.g.:

> with job control enabled a background job's processes run in a process group separate from the shell's, so the census can TERM/KILL one repository's group as a unit (`kill -- -$worker`); a child that creates its own session or group (`setsid`) is outside it

and, in the `anchor` cell only, add "(edition line in page head comment)" so a render-only re-opener can reproduce it. `corpus/lessons/round-18.md:33` needs no change: the quote, the `§ 4.3.1 -m` locator, and "15 words" are all exact.

## Method / compliance

No lane file was edited; only this report. No clone was created (nothing needed execution). No `jj`, no git write, no census/verify/vault/quarantine run, no process signalled, no tool installed. Commands used: `git -C <lane> show 5efb519:<path>` on named paths, `grep`/`awk` on named files, `curl` GETs of the two Wayback captures into `/var/tmp/souji-r18w2-ReopenS065/`, `sha256sum`, `wc -c`, `wc -w`, `python3` text normalization of the two saved captures (read-only analysis, no writes outside /var/tmp).
