# SwarmCritic17 — r34 w2 seat report (AttackE23a: C1 item E23a)

Scoped adversarial falsification of W1's E23a finding. Full detail in `AttackE23a.md`; this is the
seat-scoped summary. Read-only; frozen artifacts untouched; no subagent dispatch.

## Status

CONFIRMED — W1's E23a mismatch is real and its proposed restatement is rule-valid. I
independently re-executed the three load-bearing measurements and applied the frozen judge's own
acceptance logic to W1's verbatim row text. The defect is not a measurement artifact and not
unreachable under another frozen clause; no honest route was missed.

## Evidence

- Frozen row `census/round-34/c1-items.tsv:67` (list rev `2b0171e2…`): E23a = `SCORECARD.md:304`,
  exit 0, statement `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`,
  argv `python3 -B census/round-29/c2-counter.py --root . --rev {REV}`.
- Do-nothing record `census/round-34/records/controls-c1-do-nothing.txt`: E23a MISMATCH,
  rc 1 vs 0, `last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c72…`.
- My probes (executed, lane root, read-only):
  1. parent `1dc67850…` → `manifests=3 …` RC 0 — original predicate holds.
  2. cause `de874ee8…` → adds `r29 records=131`, `SUMMARY manifests=4 …` RC 0 — predicate fails;
     `git show --stat` confirms SCORECARD.md (+21) and r29 `waves/manifest.sha256` (+131) in one
     commit; line 304 byte-identical at list rev and cause, absent at parent and at `b8620071…`.
  3. pin `b8620071…` → `manifests=3 …` RC 0 — proposed statement verified live.
- Judge logic (executed via the counter's own functions on W1's exact row text,
  `/fast/scratch/hyaku/souji-r34/E23a/verify_row.py`): 7 cells, where/kind match, argv names
  `c2-counter.py`, cause full-40 + ancestor of list rev, line-identity absent@parent/present@cause,
  original predicate fails at cause, `collapse(last_digit_line) == collapse(statement)` — all pass.
- Q76 sweep reproduced: no binding row for the cell at base. Tool drift closed:
  `c2-counter.py` has exactly one commit (`b8cb4b31…`, creation). Counter selftest RC=0.
- Tip drift attribution (source-verified): 8 manifests r26–r33 at tip; r33 manifest (89 records,
  `d65a5c43…`) omits `w1-results.json` (`af7fd250…`) → `uncovered=1`. Matches do-nothing exactly.

## Findings

1. Real defect: row born stale at `de874ee8…` (manifests 3→4 within the authoring commit).
2. Correction valid under frozen cause/argv/exit/statement/Q76 rules — verified by live probes
   and by the frozen judge's own parsing/binding functions.
3. No missed honest route: `same`-run restatement impossible (only tool commit leaves claim
   holding at cause); tip-pinned row honestly rejected (rc 1 at tip → no false green); pin
   `1dc67850…` equally valid and already documented by W1.
4. Pin `b8620071…` is the row's own "measured at" rev and the r33 enumeration's measured rev for
   this arm — a faithful historical scope, not a fig leaf.
5. Immaterial W1 omissions: r33-manifest author `d65a5c43…` unnamed; do-nothing list-rev header
   names the byte-identical freeze rev `2b591924…`. No correction required.

## Attack log

- Falsify "absent at parent": initial parallel-shell grep artifact (`297` = empty pattern vs
  297-line parent file); sequential re-run = 0 matches. W1 stands.
- Q76 sweep, ancestry, parentage, line-identity: all independently re-run; all match W1.
- Full-clone judge reproduction aborted (repack/gc pruned revs on the shared clone; ceiling
  discipline); replaced by function-level verification with the frozen module plus live
  execution of every underlying predicate.
- Negative control: tip-pinned truthful statement still MISMATCHes on exit code.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE23a.md` (full report), this summary.
- Scratch: `/fast/scratch/hyaku/souji-r34/E23a/verify_row.py` (1 MB total).
- Nothing else written; no lane/frozen/other-repo mutation.
