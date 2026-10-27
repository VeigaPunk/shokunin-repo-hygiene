# SwarmCritic21 — Round 34 W2 seat report (AttackE26)

## Status

Seat assignment: adversarially falsify the W1 finding for AttackE26 / C1 item E26
(`census/round-34/c1-items.tsv:71`, cell `SCORECARD.md:345`). Method: read-only source/revision
inspection plus bounded, lane-read-only gate probes (scratch `/fast/scratch/hyaku/souji-r34/E26/`,
< 2 MB; per-rev gate bytes via `git show`; TMPDIR confined to scratch).

**Corrected final status (post-dispatch peer challenge by `SoujiR34a2`, verified against frozen
bytes at list rev `2b0171e…`):**
1. W1's *mismatch* finding is **confirmed** — E26 is a real, deterministic value-drift mismatch
   (stated `dangling=1 other=7` vs observed `dangling=0 other=0` at base; three agreeing readings
   at loads 10.36/35.17/52.05; landing-rev value reproduces byte-for-byte today → not an artifact,
   not fleet-root live-state drift; 13-commit gate bisect attributes the drift to content commits
   `aea0525…` (dangling 1→0) and `936efc8…` (other 7→0), not to the r31 gate change).
2. My first-pass "honest route open via `same`-cause `aea0525…`" is **REVOKED** — the peer is
   right: the frozen judge's `same` branch requires the cause to touch an item file
   (`census/round-30/c2-counter.py` only), and `aea0525` touches none → BAD-ROW. Worse, the
   same-branch is structurally dead for E26: the sole ancestry commit touching that file is its
   creation `d4928ec`, whose parent lacks the counter (`holds`=None → BAD-CAUSE).
3. **New blockade found while verifying:** amendment A1(c) requires a restated statement to EQUAL
   the run's collapsed last digit-bearing line at the measured rev, but `c2-counter.py:117` prints
   `rev={a.rev}` there — the measured commit's own hash, which a row inside that commit cannot
   contain. So even an argv-correction restatement with the unmodified argv is
   self-referentially impossible at the landing reading. `RESULTS:` binding cannot substitute
   (no `RESULT ` lines emitted).
4. **Only engine-accepted route is dishonest** (pipe the counter through sed to strip the
   ` rev=<hash>` stamp; cause `393b011…` verified: wrote the exact row line, parent `f732978…`
   lacks it, original argv fails at the cause). It falsifies the verbatim-quote/provenance
   requirement; the canonical judge must reject it.
5. **Net:** E26 is honestly unrestateable under frozen bytes → C1's `items=60 agree=60` target is
   unreachable through E26 by honest means. Reported for judgment-level ruling (as with the E25
   seat), not amendment (post-data freeze).

## Evidence

- Frozen row (`c1-items.tsv:71`): exit 0; statement `reports=86 cne=0 dangling=1 other=7
  fixture=ok redarm=ok regress=same`; `files`=`census/round-30/c2-counter.py`; cell unique to E26;
  SCORECARD.md byte-identical base↔list-rev.
- Frozen judge `c1-counter.py` @ list rev: `same` branch file-touch check
  (`BAD-ROW(cause touches none of the item files)`) + parent/cause hold check; argv-correction
  branch (corrected argv must name a row file; cause wrote the row's exact line; ORIGINAL argv
  must fail at the cause); A1(c) exact `collapse(last_digit_line) == quoted` check; `RESULTS:`
  branch needs ≥1 `RESULT ` line.
- `git log --oneline 2b0171e -- census/round-30/c2-counter.py` → `d4928ec` only (creation;
  absent at `d4928ec^`); `--all` extras `12b3439`/`14f93e7` are non-ancestor orphan duplicates.
- c2-counter.py:116-117: SUMMARY ends `… regress=<same|differs> rev={a.rev}`.
- Line authorship: exact line-345 text absent at `f732978…`, present at `393b011a8221259abe6825fc3b637fcdc1b0e1eb` and onward (`393b011^`=`f732978506f3fa8ef32d4af1b4ee5bc962603aaf`).
- Probes (`/fast/scratch/hyaku/souji-r34/E26/out-*.txt`): gate findings 8@68447af → 7@aea0525 →
  0@936efc8 → 0@52ebd48/8024b54 → 1@98e5203 → 0@9c76c72; original statement fails at `393b011`.

## Findings

1. W1 mismatch confirmed; correction route **closed** (two independent blockades, both
   engine-verified). Peer challenge upheld and generalized.
2. **Cross-item hazard:** A1(c)+`rev=` binding blocks honest restatements of every rev-printing
   item (E23a, E23b, E24, E27, E29, E31, E32, E33 per W1 q76 receipt; E28 prints no rev).
3. **Engine hole:** frozen argv-correction branch never re-runs the corrected argv at the cause
   and does not refuse pipes/metacharacters → output manipulation is engine-acceptible;
   `r34-c1-junk.py` (A4/A5) does not cover it. Fixable defect for a future freeze.
4. Process: no stricter amendment possible post-data; E26 needs a judgment-level ruling as a
   frozen instrument/statement-binding defect (same disposition class as E25).
5. First-pass sub-findings retained: r34 appended rows must not cite uncaptured
   `.ufo/waves/round-34/…` paths (gate scans SCORECARD citations); the cell is "at the C2 landing
   commit"-pinned (arguably the preregistration's historical-exclusion class — moot, list frozen).

## Attack log

- Read frozen row, preregistration + amendment log, W1 receipts, committed controls/r30 record,
  counter/gate/judge source; executed 13-commit read-only gate bisect; verified Blockade 1
  (file-touch + d4928ec-only lineage) and Blockade 2 (rev= self-print + exact binding); verified
  the dishonest pipe route's engine mechanics and its cause; replied to `SoujiR34a2`.
- No lane/fleet-root file modified; no commits; no subagent dispatch; scratch < 2 MB (< 50 MB
  ceiling); nothing written to PATH dirs.

## Deliveries

- `souji-shokunin/.ufo/waves/round-34/w2/AttackE26.md` — full target report (corrected status).
- `souji-shokunin/.ufo/waves/round-34/w2/SwarmCritic21.md` — this seat report.
- Probe artifacts: `/fast/scratch/hyaku/souji-r34/E26/`.
