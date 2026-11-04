# S59Scribe — round-59 source rows: S286 mined, S287 rejected, with executable row-draft checks

## Behavior and axes

Axes: located-quote fidelity; distinct-scope separation on a shared URL; record
accuracy of the source citations; executability of the delivered drafts; absence
of production mutation.

Read before source work: `census/round-59/preregistration.txt` (frozen at
`19f44552378d333f401ff2f0864c4e8b9c59ab1f`), the executed controls committed at
`74455b7209e04a2375c2084738a7b6fea59bf6d5` (`before.txt`, `c1-counter.py`,
`controls.py`, `controls.json`, `controls-run.txt`), `corpus/lessons/round-59.md`
and `corpus/lessons/round-58-verifier-spotcheck.md`.

This is lane-dispatched source work with executable checks on the drafts. It is
**not** independent non-author judgment, not admission, and not a statement that
the lane's gate implementation is correct.

## What was delivered

Two SOURCES row drafts, both citing one officially opened document with
distinct scopes:

- **S286 (draft, tier A, status mined)** — scope: *public child-process
  return-code assertions in the assessment gate selftest*. Located quote (17
  words, within the 25-word ceiling): `Exit status of the child process.
  Typically, an exit status of 0 indicates that it ran successfully.` Grounds:
  `CompletedProcess.returncode` is a child exit status distinct from captured
  stdout, so a selftest asserting only printed findings cannot establish child
  success.
- **S287 (draft, tier A, status rejected)** — scope: *rejected inference that
  check=False itself asserts the child's success*. Located quote (19 words):
  `If check is true, and the process exits with a non-zero exit code, a
  CalledProcessError exception will be raised.` The documented exception is
  conditioned on check being true, and the `run()` signature on the same page
  defaults `check=False`, so the default asserts no exit status. Flip: compare
  `CompletedProcess.returncode` against an independently persisted expected rc.
  **The official document is not rejected; the inference drawn from it is.**

Source: `https://docs.python.org/3/library/subprocess.html`, accessed
2026-11-04, Python 3.15.2 documentation, curl -sSL HTTP 200 (no redirect),
208648 bytes, sha256
`31f573c59a215fbad7e12dd81b41715f38b600eed240b84b9a42bd4e4a1685b1`. Opened
twice by independent paths: a curl capture and the session's URL reader, both
returning the same 3.15.2 text containing both quoted sentences. Capture line
spans: S286 at 362–363, S287 at 301–302 of the capture.

## Gate draft and lesson draft

`gate-draft.md` — admit/reject decisions, the executable substance, the
explicit list of what was not established, and the inherited-debt list.
`lesson-draft.md` — Gate continuation wording for the round-59 lesson, the
**r58 late-control mistake carried forward verbatim** (control commitment after
predicate freeze cannot establish prefreeze discrimination; r59's controls were
executed and committed at `74455b72` *before* the declaration at `19f44552`),
the two existing mistake rows, a proposed third row on uncounted quote lengths,
and the preserved-debts paragraph.

## Executable substance

`verify-quotes.py` (stdlib only, read-only over the capture and the rows file)
checks each draft row: quote verbatim in the tag-stripped, entity-decoded,
whitespace-collapsed capture; word count at or below 25; anchor label present
on the page; exactly one shared URL across both rows; distinct scopes.

Honest arm — `SUMMARY checks=2 findings=0`, exit 0.

Four negative controls, each rejected with a named finding:

| control | mutation | observed |
|---|---|---|
| corrupt-quote | S286 quote reworded | rc=1 `FINDING QUOTE-NOT-VERBATIM S286` |
| over-long-quote | S286 quote replaced by 30 words | rc=1 `FINDING QUOTE-TOO-LONG S286 words=30` |
| same-scope | S287 scope set equal to S286's | rc=1 `FINDING SCOPES-NOT-DISTINCT …` |
| different-url | S287 URL changed to `os.html` | rc=1 `FINDING URLS-DIFFER …` |

The fleet sources census was run read-only in three configurations and never
wrote: over the live lane working tree (exit 0, only W04 for S286/S287), over
an isolated scratch lane copy carrying **this seat's** draft rows (exit 0, lane
`ok`, only the W04 lines), and over that same fixture with S287's scope set
equal to S286's to confirm the census semantics (rejected rows stay out of the
E04 arm; flipping S287 to `mined` does raise
`E04 S287 duplicate url … within scope …`).

## Findings reported to L1 (not applied by this seat)

1. **S287 word count.** The round-59 lesson in the lane working tree records
   the S287 located quote as 23 words. The quoted sentence is **19**
   whitespace-separated words; the counted token list is in `quotes.txt`. The
   quote itself is verbatim and correct — only the stated length is wrong. Same
   defect class as r57's S279 quote-2 (recorded 17, later established 19). A
   proposed third mistake row covering this is in `lesson-draft.md`.
2. **S287 scope wording.** The working-tree row's scope cell reads "rejected
   inference that capturing stdout with the default check setting proves child
   success" while its `teaches` cell states the check=False point. This seat's
   assigned scope is "rejected inference that check=False itself asserts
   success"; the draft uses that wording. Either wording keeps the two scopes
   distinct from S286, so the W04/E04 classification is unchanged.
3. **S286/S287 already exist as uncommitted working-tree rows.** At the time of
   this seat's read, `git status --porcelain` in the lane showed
   ` M corpus/QUALITY.md`, ` M corpus/SOURCES.md`, `?? corpus/lessons/round-59.md`
   — L1's round-59 edits, containing S286/S287 and Q119/Q120. They are absent
   from `HEAD` (`git show HEAD:corpus/SOURCES.md | grep -c 'S28[67]'` → 0). The
   ids were therefore already taken in the working tree; the drafts here refine
   those rows rather than claiming fresh ids. **No id was reserved by this seat
   and no registry byte was changed.**

## Gates, touched surfaces, out-of-scope legs

- Exercised: two independent opens of one official URL; located-quote
  extraction, verbatim check and word counting against the captured bytes; a
  row-draft checker with an honest arm and four killed negative controls; the
  fleet sources census in three read-only configurations (live lane, isolated
  scratch copy with these drafts, and a mutated-scope fixture); the lane-local
  SOURCES shape census; working-tree status reads.
- Findings: both located quotes are verbatim, 17 and 19 words, inside the
  25-word ceiling, at capture spans 362–363 and 301–302; the two drafts pass
  the fleet census with only the expected W04; two record discrepancies in the
  working-tree lesson and row are reported above.
- Unrun: the r59 assessment gate (no `assessment-gate.py` existed in
  `census/round-59/` at this seat's read — that directory held `before.txt`,
  `c1-counter.py`, `controls-run.txt`, `controls.json`, `controls.py`,
  `population.tsv`, `preregistration.txt`, `sources-before.txt`); the frozen
  counter; the pre-freeze controls; the `c1-counter.py --selftest` mode; every
  build, lint and formatter; the non-author outside verification; any mutation
  battery against lane code; canonical Rust judgment.
- Touched: this report and the eight artifacts in
  `.ufo/waves/round-59/w1/S59Scribe/` only, plus own scratch, which was
  removed at the end. No production edit, no fleet or sibling edit, no commit,
  push, branch or jj mutation, no tool install or package transaction, no
  service, no runtime dispatch, no task dispatch.
- Known limits: the located quotes are documented API semantics, not evidence
  about any souji implementation; the row-draft checker validates the drafts
  only, not the lane gate; W04 is a warning class and the census exit code
  does not distinguish it from a clean lane.

## Inherited debts — unchanged

Visibility-parser second-opener / code-span / escape / link / TAB and scale
defects; recorder dirty-tree and overwrite; capture row-set meta-test;
historical receipt bindings; diagnostic escaping; receipt-confinement
atomicity and resource-intake bounds. Certification OFF; K5 HELD; r46
mass-id-drift hold retained; prior r56/r57 rejected-harmed and r58
rejected-honest-stop admissions unchanged. This seat closed none of these and
opened none.

## Tools

No tool was installed or updated. No pacman transaction was attempted; the
host guard for this wave pauses all pacman transactions, and none was needed.
Python 3.14.8 (pre-installed) and `curl`/`gawk`/`bash` (pre-installed) were
the only executables used; no `uv`/`npx`/official-binary install was required
and none was performed. `/home/vgpnk/.omp/agent/RULES.md` was read before any
tooling step.

## Self-assessment (not a gate)

Accuracy 4: both quotes located twice over, counted by command against pinned
bytes, and the drafts census-validated in isolation. Completeness 4: both
assigned rows delivered with located quotes, date, exact URL and capture
evidence, plus Gate and lesson drafts; the two record discrepancies are
reported rather than applied because the target files are L1's. Clarity 4:
decisions, executed checks and unrun checks are separated. Actionability 4:
rows are paste-ready and the checker is re-runnable. Conciseness 3: receipts
are long by design. Overall 3.8. Highest-impact improvement: have the lesson's
word counts produced by the counting command rather than written by hand, which
is the one defect this seat actually found in the record.

## Artifact paths (relative to /home/vgpnk/Projects/shokunin/souji-shokunin)

- `.ufo/waves/round-59/w1/S59Scribe.md` — this report
- `.ufo/waves/round-59/w1/S59Scribe/sources-rows-draft.md` — the two row drafts with rationale
- `.ufo/waves/round-59/w1/S59Scribe/gate-draft.md` — Gate admit/reject draft
- `.ufo/waves/round-59/w1/S59Scribe/lesson-draft.md` — lesson draft incl. the r58 late-control mistake
- `.ufo/waves/round-59/w1/S59Scribe/rows.tsv` — machine-checkable row file
- `.ufo/waves/round-59/w1/S59Scribe/verify-quotes.py` — row-draft checker with negative controls
- `.ufo/waves/round-59/w1/S59Scribe/quotes.txt` — located-quote receipt (counts, token lists, line spans)
- `.ufo/waves/round-59/w1/S59Scribe/receipts.txt` — exact commands and observed outputs
- `.ufo/waves/round-59/w1/S59Scribe/subprocess.html` — the captured source page

Report: .ufo/waves/round-59/w1/S59Scribe.md
