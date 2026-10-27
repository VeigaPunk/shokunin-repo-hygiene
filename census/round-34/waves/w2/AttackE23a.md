# AttackE23a — r34 w2 adversarial falsification of W1's E23a finding

Target: C1 item E23a (`SCORECARD.md:304`, r29 C2 committed-bytes receipts, v1 arm). Seat: SwarmCritic17.
Read-only; no frozen artifact, lane file, or git ref touched. Bounded probes only.

## Status

REPRODUCED AND CONFIRMED — W1's mismatch is real, its cause analysis is correct, and its proposed
argv-correction restatement (pinned at `b8620071…`) is valid under every frozen rule I could
exercise: cause, argv, exit, statement, line-identity, and Q76. I independently re-executed all
three load-bearing measurements (parent / cause / pin) and ran the frozen judge's acceptance
logic against W1's exact row text using the counter's own code. No honest rule-conforming route
was missed; the only alternatives are either already named by W1 (pin `1dc67850…`) or invalid
under the frozen branches (source-verified). The defect is not a measurement artifact
(manifests counts are git-tree-deterministic) and not unreachable under another frozen clause
(E23a is squarely in the frozen surface; no Q76 binding exists).

## Evidence

- Frozen row: `census/round-34/c1-items.tsv:67` (list rev `2b0171e2…`, file identical at freeze
  rev `2b591924…` — `git diff` empty):
  `E23a  SCORECARD.md:304  0  SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0
  census/round-29/c2-counter.py  {REV}  python3 -B census/round-29/c2-counter.py --root . --rev {REV}`
- Base do-nothing record `census/round-34/records/controls-c1-do-nothing.txt`:
  `ITEM E23a MISMATCH original rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8
  failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=11.24`
  (file header pins base `9c76c72…`; list diff `2b591924…` vs `2b0171e2…` = 0 lines).
- W1 deliverable `.ufo/waves/round-34/w1/deliver-c1-E23a.md` — MISMATCH reading, Q76 sweep,
  cause `de874ee8…`, parent `1dc67850…`, proposed row, frozen-counter AGREE probe (scratch
  commit `511323e3…`).
- My executed probes (lane root, read-only; the tool reads only via `git ls-tree`/`cat-file`,
  `census/round-29/c2-counter.py:24-97`):
  1. `--rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38` (cause's parent) →
     `r26 records=1381 … r28 records=75 … SUMMARY manifests=3 failed=0 uncovered=0
     floor_violations=0 rev=1dc67850…`, RC=0 — original predicate HOLDS at parent.
  2. `--rev de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` (cause) → adds
     `r29 records=131 failed=0 uncovered=0 floor_violation=0`,
     `SUMMARY manifests=4 failed=0 uncovered=0 floor_violations=0 rev=de874ee8…`, RC=0 —
     predicate FAILS at cause (manifests 3→4 in one commit). Reproduces W1 byte-for-byte.
  3. `--rev b86200714069022954a3b498cf697d894119b45e` (W1's pin) →
     `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b8620071…`, RC=0 —
     proposed statement's last digit-bearing line verified live.
- Line identity: `git show 2b0171e2…:SCORECARD.md | sed -n 304p` ==
  `git show de874ee8…:SCORECARD.md | sed -n 304p` (cmp: identical, 700 chars); the text is
  absent at `de874ee8^` (`1dc67850…`, grep -cF = 0; parent's SCORECARD has 297 lines, no C2
  row) and absent at `b8620071…` (row born later at `de874ee8`; `b8620071` is an ancestor of
  `de874ee8` — the row's own "measured at" rev predates its landing, as measurements do).
- Ancestry: `git merge-base --is-ancestor de874ee8… 2b0171e2…` = true (cause in list ancestry);
  `git cat-file -p de874ee8…` shows exactly one parent (`1dc67850…`).
- Cause stat: `git show --stat de874ee8…` — `SCORECARD.md | 21 +` and
  `census/round-29/waves/manifest.sha256 | 131 ++` in the same commit. Value-drift closure:
  `git log --follow -- census/round-29/c2-counter.py` lists exactly one commit, its creation
  `b8cb4b31…` — no later commit can re-break the statement.
- Q76 sweep (reproduced): `git grep -n 'SCORECARD.md:304' 9c76c72… -- .` hits only
  `census/round-30/waves/w1/SwarmRevenger34.md:37` and `deliver-cross-claim.md:46` (prose
  about a *different* row, `SCORECARD.md:314`) and the r33 enumeration
  `deliver-c1-enumeration-misses.md:36` (the item's source). No correction/supersession/binding
  row exists at base; Q76 does not apply.
- Tip drift attribution (source-verified): at `9c76c72…` the census tree holds 8 manifests
  (`ls-tree`: r26…r33, each `waves/manifest.sha256`). The r33 manifest (89 records, added by
  `d65a5c43…` "round-33: final-tip receipt … (89 records)") does not list
  `census/round-33/waves/w1-results.json`, which `af7fd250…` added (1 file, 296 lines) →
  exactly `manifests=8 … uncovered=1` at tip. W1's mechanism is right (it did not name
  `d65a5c43…` as the manifest author — immaterial).
- Judge-logic verification (executed): `/fast/scratch/hyaku/souji-r34/E23a/verify_row.py`
  imports the frozen `census/round-34/c1-counter.py` and applies its own functions to W1's
  exact row text: `load_restatements` → 1 row, 7 cells; where/kind match; exit `0` well-formed;
  run cell backticked and names `c2-counter.py` (the basename rule,
  `c1-counter.py:267-268`); statement backticked; cause full-40 and ancestor of list rev;
  reason non-empty; cause parent = `1dc67850…`; line text (from list rev) absent at parent /
  present at cause (`c1-counter.py:293-296` branch); original predicate fails at cause;
  `collapse(last_digit_line(probe-3 output)) == collapse(statement)` → ALL CHECKS PASS.
- Frozen instrument intact: `python3 -B census/round-34/c1-counter.py --selftest` →
  `SELFTEST pass always-zero rejected RESULTS:0 rejected foreign argv rejected`, RC=0.
- Negative control: a tip-pinned restatement cannot false-green — the tool exits 1 at tip
  (do-nothing record), so `exit_ok` fails regardless of statement (`c1-counter.py:320-321`);
  and a `holds()=None` run is rejected, not accepted (`is not False` at `c1-counter.py:297`).

## Findings

1. The alleged defect is REAL. Row 304 was born stale: `de874ee8…` authored the row and added
   r29's own `waves/manifest.sha256` in the same commit, moving the measured quantity 3→4.
   Independent re-execution matches W1 byte-for-byte at parent and cause.
2. W1's correction is RULE-VALID, not merely plausible. Every frozen acceptance condition in the
   argv-correction branch (`c1-counter.py:283-300`) plus the statement/exit binding
   (`:311-322`) was verified — most by live execution, the row-format parsing by the counter's
   own functions on W1's verbatim text. W1's committed AGREE probe (`511323e3…`) is consistent
   with all of this.
3. No honest route was missed. Alternatives examined and closed:
   - `rrun="same"` restatement: impossible — the only commit touching
     `census/round-29/c2-counter.py` is its creation `b8cb4b31…`, at which the original argv
     still HOLDS (manifests=3 there), failing the "stops at cause" requirement.
   - Pin at `1dc67850…` (last rev where the claim held): equally valid, and W1 explicitly
     documented it as an alternative (measured rc 0 there, probe 1 above).
   - Exclusion as historical/argv-dup: E23a is enumerated in the frozen list itself; the r33
     deliverable shows the r33 counter excluded E23 by *its own* section clause, which the r34
     surface definition overrides; the argv is the item's own, not a dup of an r33 K-item's
     restated pair.
4. Not a measurement artifact. `manifests`/`uncovered` are pure functions of the committed
   tree; host load at the relevant runs (5.87–13.12 per W1, 11.24 do-nothing) cannot move them,
   and the do-nothing line matches my independent tip attribution exactly.
5. Not unreachable under another frozen clause. Q76 sweep is empty for the cell; the item's
   line, files, and argv all conform to the frozen list columns.
6. The pin is honest, not a fig leaf. `b8620071…` is the row's own "measured at
   `b86200714069022954a3b498cf697d894119b45e`" revision and the r33 enumeration's measured rev
   for this exact arm (r33 deliverable row E23, "YES" column). That the row's text did not yet
   exist at that rev is inherent — the measurement predates the landing commit — and the
   restated row states plainly it is a revision-scoped historical measurement, quarantining the
   later `manifests=8 … uncovered=1` drift (r33 manifest `d65a5c43…` vs `w1-results.json`
   `af7fd250…`) from the claim.
7. Immaterial W1 omissions (no correction needed): the r33-manifest author `d65a5c43…` is
   unnamed in the drift narrative; and the do-nothing record's list-rev header reads the freeze
   rev `2b591924…` while the assignment/W1 use `2b0171e2…` — the two are byte-identical for
   `census/round-34/c1-items.tsv` (verified), so the readings agree.

## Attack log

- Falsify parent-absence claim: first attempt printed `297` — an artifact of running the grep
  in parallel before its pattern file existed (empty pattern matches every line; the parent's
  SCORECARD has exactly 297 lines). Sequential re-run: `grep -cF` = 0 at `de874ee8^`, 0 at
  `b8620071…`. W1's claim stands.
- Falsify Q76: reproduced W1's sweep independently; same three hits, none a binding row.
- Break the proposal with a tip-pinned row: closed by exit code (rc 1 at tip) — no false AGREE.
- Break the proposal via `holds()=None` gaming: the frozen branch rejects `None`
  (`is not False`), and my probe-2 run is clean rc 0, so `holds=False` deterministically.
- Full-clone judge reproduction: attempted a packed standalone clone; `git repack -a` on a
  `--shared` clone did not localize alternate objects and the follow-up gc pruned the needed
  revs. Aborted (also to respect the <50 MB scratch ceiling) and replaced with function-level
  verification: the frozen counter module's own `load_restatements`/`collapse`/`last_digit_line`/
  `FULL` applied to W1's verbatim row text, plus live execution of every underlying git
  predicate. Scratch footprint now 1 MB.
- Negative control script: tip-pinned truthful statement still MISMATCH (rc≠exit); recorded
  above.

## Deliveries

- This report: `.ufo/waves/round-34/w2/AttackE23a.md`.
- Seat summary: `.ufo/waves/round-34/w2/SwarmCritic17.md`.
- Scratch (1 MB): `/fast/scratch/hyaku/souji-r34/E23a/verify_row.py` (harness) — probe outputs
  quoted verbatim above; no fixtures, no lane clones retained.
- No lane, frozen, or other-repository files modified; no commits, no subagent dispatch.
