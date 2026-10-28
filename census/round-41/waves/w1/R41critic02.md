# R41critic02 — attack on C1 append-only and sourced checks

Seat: R41critic02 (critic, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, tip e2a7431 (freeze). Counter: census/round-41/c1-counter.py (sha256 8860dc7a…, unmodified). Scoring only via census/round-41/score-candidate.sh into scratch /fast/scratch/hyaku/souji-r41/R41critic02 (removed before yield). Candidates copied to .ufo/waves/round-41/w1/R41critic02/candidates/.

## Question

1. Can a candidate pass `rewritten=0` while altering a filed line?
2. Can `sourced=1` be met by a row that does not quote its source?

## Verdict

- **Q1, the three filed item files (round-40.md, SCORECARD.md, LOG.md): no false green found.** Byte-prefix check `tip.startswith(base)` holds. An in-place edit of the filed sentence (K3a) and an edit of the heading with the anchor kept (K3b) both score `rewritten=1` and exit 1. All three files end in LF (checked: `git show bffcc0f:<file> | tail -c1` = `\n`), so the only append-only bypass (extending a final unterminated line) does not exist.
- **Q1, filed registry rows (corpus/SOURCES.md): FALSE GREEN.** `rewritten` never reads SOURCES.md. A candidate that rewrites an existing filed row (S033, opened 2026-10-19, status queued) and cites it passes `rewritten=0 sourced=1` and exits 0 (K4). The frozen counter docstring (`c1-counter.py:29-30`) says the *three* files are append-only; the registry is not covered.
- **Q2, sourced=1 from a row with no quote: FALSE GREEN.** A fabricated S258 row whose grounding-quote column (`teaches`, cells[6]) is `-` satisfies the counter and exits 0 (K2). `sourced()` (`c1-counter.py:96-107`) reads only cells[1] (source) and cells[5] (anchor), and checks `tier==A`, `status==mined`, `opened==2026-10-28`, and that `v2.56.0` and `worktree.c` appear in those two cells. It never reads the quote column, and it reads the candidate's own SOURCES.md at `--rev` (`:97`), so the candidate supplies its own evidence. This literally meets the frozen predicate text ("cites a tier-A mined registry row opened 2026-10-28 for git v2.56.0 worktree.c"), but it violates the corpus rule that every row carries a ≤25-word located quote (round-40 Gate header; M40-7 cites CORPUS.md SOURCES rule 1). The lane's own census validator also accepts it (see §4).
- **Junk check: FALSE GREEN (additional, found while probing sourced).** The junk loop (`c1-counter.py:155-163`) compares file/filed/derived/rev but never `group(6)` (source). A CORRECTION line for I1 whose source is unresolved (`S999`) or `-` is counted neither as corrected nor as junk; it yields `junk=0` (K5a, K5b, exit 0). The kill rule is "any junk line".

No frozen file was edited. Named limits for the L1 (not edits): (a) sourced must require the quote column; (b) sourced must require the row id to be new relative to MEASURED, and SOURCES.md must be prefix-checked against MEASURED; (c) junk must validate `source=` for I1.

## 1. Counter facts relied on (committed, unmodified)

| fact | location |
|---|---|
| MEASURED = bffcc0f…, items pinned by sha256 2d2a548e… | c1-counter.py:46-48 |
| derive reads MEASURED only (constant mismatch flags) | :71-93 |
| sourced(): registry read at `--rev`, cells[1]+cells[5] substring test, tier/status/date tests | :96-107 (blob at :104, predicate :105-106) |
| intact = anchor in tip and `tip.startswith(base)` for the item file only | :136-143 |
| I1 sourced gating on the CORRECTION line's `source=` | :147-151 |
| junk loop: no check of group(6) | :155-163 |
| target | :166-167 |
| registry column order (verified against HEAD rows S009, S033, S257): cells[0]=id, [1]=source, [2]=kind, [3]=tier, [4]=scope, [5]=anchor, [6]=teaches (quote), [7]=status, [8]=opened, [9]=recheck, [10]=used-by | corpus/SOURCES.md header `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |` at HEAD |
| no HEAD row passes the sourced predicate (awk over HEAD rows with tier A, mined, 2026-10-28, `v2.56.0` and `worktree.c`): zero rows | `git show HEAD:corpus/SOURCES.md \| awk ...` (empty output) |

## 2. Sweep (commands actually run; all via score-candidate.sh unless noted)

Invocation form: `bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41critic02 <dest>=<src> ...` with `TMPDIR=/fast/scratch/hyaku/souji-r41/R41critic02`.

Candidate sources (scratch; copies in .ufo/waves/round-41/w1/R41critic02/candidates/):
- `lesson-valid.md`: three CORRECTION lines carrying the counter's own derived values (`rows=2,v2.56.0=0`, `before=6,after=3`, `occurrences=0`), rev=bffcc0f…; I1 `source=S258`; I3/I4 `source=-`.
- `sources-S258.md`: HEAD SOURCES.md + one appended row after S257: `| S258 | git v2.56.0 builtin/worktree.c — https://github.com/git/git/blob/v2.56.0/builtin/worktree.c | code | A | git 2.56.0 linked-worktree prune gate | builtin/worktree.c at tag v2.56.0 | - | mined | 2026-10-28 | on-release | corpus/lessons/round-41.md |` (teaches/quote cell = `-`).
- `round-40-filed.md`: line 49 changed `appears in 9 rows` → `appears in 2 rows` (anchor removed).
- `round-40-headline.md`: line 1 heading changed; anchor line kept.
- `sources-S033.md`: HEAD SOURCES.md with the filed S033 row replaced (source now cites v2.56.0 worktree.c, status queued→mined, opened 2026-10-19→2026-10-28).
- `lesson-S033.md`: as lesson-valid but I1 `source=S033`.
- `lesson-bogus-S999.md` / `lesson-bogus-dash.md`: lesson-valid plus an extra I1 line with `source=S999` / `source=-`.

Results (verbatim SUMMARY lines):

| run | candidate | SUMMARY | exit |
|---|---|---|---|
| K0 | no candidate (do-nothing) | `SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0` | 1 |
| K1 | lesson-valid, HEAD registry | `SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0` | 1 |
| K2 | lesson-valid + sources-S258 | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | **0 (FALSE GREEN)** |
| K3a | K2 + round-40 filed line edited (anchor removed) | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=1 sourced=1` | 1 (caught; I1 `intact=NO`) |
| K3b | K2 + round-40 heading edited (anchor kept) | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=1 sourced=1` | 1 (caught; I1 `intact=NO`) |
| K4 | lesson-S033 + sources-S033 (filed S033 rewritten) | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | **0 (FALSE GREEN)** |
| K4-control | lesson-S033, HEAD registry | `SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0` | 1 |
| K5a | lesson-bogus-S999 + sources-S258 | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | **0 (junk line passes)** |
| K5b | lesson-bogus-dash + sources-S258 | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | **0 (junk line passes)** |

Run-error disclosure: my first K4 scoring paired the S033 registry with lesson-valid (`source=S258`), which gave `sourced=0` and exit 1. That was a mis-built candidate, not evidence; it is superseded by the K4 rerun with lesson-S033 and the K4-control above. The control shows the green in K4 comes from the S033 rewrite, not the lesson.

Per-item lines for K2 (for the record): `ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes`, `ITEM I3 ... corrections=1 intact=yes`, `ITEM I4 ... corrections=1 intact=yes`.

## 3. Interpretation

- K2 meets the frozen target text exactly (`corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, exit 0) with a row that has no quote and no snapshot. A candidate can therefore satisfy calibration's sourced leg by inventing a registry row. The frozen target does not catch that.
- K4 shows the registry is unprotected: a filed row (S033, used by other rows, with its original opened date and status) can be rewritten and then cited.
- K5a/K5b show the junk leg is not enforced for I1 source tokens.
- Negative results: in-place edits to the three filed item files are caught (K3a/K3b). I did not find a way to alter those files with rewritten=0.
- I did not build an honest candidate with a real worktree.c v2.56.0 quote; the attacks above do not need one. An honest green is still the L1's measurement to make.

## 4. Lane validator cross-check (read-only)

I committed the K2 candidate in a scratch clone (`git clone --shared` of the lane, `git -C <clone> rev-parse --show-toplevel` asserted equal before commit, identity via GIT_AUTHOR_*/GIT_COMMITTER_* env only) and ran the existing registry validator:

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin <K2 clone>` → `k2clone ok .../corpus/SOURCES.md` with W04 lines only; EXIT=0.
- Same command on the lane: `souji-shokunin ok .../souji-shokunin/corpus/SOURCES.md`; EXIT=0.

So the existing census validator also does not reject a quote-less row (it reports W04 duplicate-url warnings only).

## 5. Lane and host hygiene

- Lane: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` = empty (0 lines) after the sweep. No lane write. score-candidate.sh clones and removes its own scratch.
- Only git writes: one `git commit` in my scratch clone /fast/scratch/hyaku/souji-r41/R41critic02/k2clone (rev-parse toplevel asserted; identity env only). No git config, no lane commit.
- Tools installed: none. Used installed git 2.56.0 and the lane's existing scripts only.
- Scratch: all work under /fast/scratch/hyaku/souji-r41/R41critic02; removed at yield (rm -rf of that directory only). One scratch file was briefly written to the shared /fast/scratch/hyaku/souji-r41/ root and moved into my directory before any use.

## 6. Pointers

- Counter: census/round-41/c1-counter.py (committed at e2a7431; read-only here).
- Population: census/round-41/c1-items.tsv; control: census/round-41/controls/c1-control.txt, c1-junk-round-41.md.
- Registry: corpus/SOURCES.md at HEAD e2a7431 (S033 row, S257 row, header).
- Candidates (seat copies): .ufo/waves/round-41/w1/R41critic02/candidates/{lesson-valid,lesson-bogus-S999,lesson-bogus-dash,lesson-S033,sources-S258,sources-S033,round-40-filed,round-40-headline}.md
- Predicate text: census/round-41/preregistration.txt §C1 (Target/Kill/Predicate).

## 7. Calls for the L1

1. Treat K2 and K4 as named limits of the frozen C1 counter, not as passes. A landed candidate that writes a quote-less S258 would score the target.
2. Any landed C1 lesson should be checked against the corpus rule (≤25-word quote in the row's teaches cell, verbatim in the cited snapshot) by a non-counter check before measurement, and the registry should be prefix-checked against MEASURED with `git diff`, outside the counter.
3. The junk leg should validate `source=` for I1 lines (K5a/K5b).
