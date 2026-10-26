# SwarmSimplifier34 — wave 2, round 30 (attempt 1)

## Status

STATUS: PASS — the attack ran: all eight named instruments read at the lane tip and at the frozen prereg
blob, overlap measured mechanically, one behavioural defect proven by witness built from committed format
strings; zero lane bytes edited, zero deletions, zero git/jj mutation.

## Evidence

Read this run (absolute paths under `/home/vgpnk/Projects/shokunin/souji-shokunin/`):

| Surface | Revision / bytes |
|---|---|
| `census/round-30/records/preregistration.txt`, `.../amendments.txt` | working tree at tip |
| `tools/souji-capability-agreement.py` | v1 blob at `d4928ec86b667e3d1ed0adb07fb088e500cf1631` and A3 at `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8` (`git diff d4928ec..9dcd367`) |
| `census/round-30/{c2-counter.py,c2-counter-v2.py,c3-counter.py,c3-counter-v2.py,controls.sh,controls-amended.sh}` | working tree |
| `tools/{souji-coverage-agreement.py,souji-gate-check.py,souji-landing-gate.py,souji-receipt-run.py,souji-rev-pin.py,souji-declared-evidence.py,souji-registry-agreement.py,souji-wave-evidence-capture.sh,souji-verify.spec.md}`, `tests/fixtures/{r28-wave-evidence-capture.sh,r30-landing-gate-discovery.py}`, `census/round-29/*`, `census/round-30/waves/*` | working tree / directory listings |

Measurements (mechanically produced, not estimated): set intersection of non-blank lines — c2 pair 54 shared of
108/149 distinct; c3 pair 33 shared of 120/98; controls pair 18 shared of 68/51; generators 10 (r29↔w1) and
21 (w1↔w2) shared of 121/111/93 lines; `wc -l` for every file cited.

Witness (D1), built from committed format strings only:

```
tools/souji-landing-gate.py:1423  detail = "exit=%d ids=%s paths=%s fleet=%s err=%s" %
census/round-30/c2-counter-v2.py:69  re.sub(r"\terr=.*$", "", l)
result: the CASE line is unchanged  (strip applied? False)
```

`lsp` is **not mounted** in this session (`read xd://lsp` → "No such tool"); caller analysis is text grep and is
reported as literal, not semantic, absence. No tool installed or updated by this seat (nothing to record); no
pacman call; scratch `/fast/scratch/hyaku/souji-r30/SwarmSimplifier34/` created empty and removed.

## Findings

1. **The only round-30 instrument promoted to `tools/` still carries round-30 bytes.**
   `tools/souji-capability-agreement.py:8` — "Each row of `census/round-30/c1-rows.tsv` (at --list-rev) names a
   SCORECARD.md line"; also `:116` (path literal), `:139` and `:229` (regex `^R30-CORRECTION`). A `tools/` home
   was granted before the two round-bound literals were parameterized; next round either forks the file or
   accumulates round-30 history in its docstring.
2. **`census/round-30/c2-counter.py` (v1) has no discriminating power v2 lacks.** v2 runs all four v1 legs and
   drops only the `other=` diagnostic; 54 of v1's 108 distinct lines reappear in v2 under renamed helpers
   (`export` → `clone`). The pair is cost with one benefit only: v1 stays runnable without a `git show`
   extraction.
3. **`census/round-30/c2-counter-v2.py:69` `strip_err` is a no-op** — it demands a tab before `err=`, but the
   CASE detail separator is a space (D1 witness above). The REGRESS-FULL leg therefore compares the free-text
   error tail it documents as dropped; any base/REV pair whose selftest error text differs reports `differs`
   whatever the behavior.
4. **The C3 pair is disjoint, not redundant — the convention is the weight.** 33 shared lines of 120/98: v2 is
   additive (E1-E4), so both files must be run and their two SUMMARY formats reconciled for one claim.
5. **E1/E2 create a second authority for a rule the shared tool already owns, less strictly.**
   `tools/souji-coverage-agreement.py:34` `FRONT_GROUND = re.compile(r"^ground:\s*F([0-9]+)")` reads `F1` out of
   `ground: F1-jj`, and `GROUND_TOKEN` likewise accepts the `F1-jj` map row; `c3-counter-v2.py`'s E2 docstring
   holds the opposite intent: "(the plain F1 row; the `F1-jj` edge-class row does not satisfy it)". A seat that
   reuses the shared tool alone reopens the bug A2 closed.
6. **E3 hand-rolls a receipt the lane already ships.** `c3-counter-v2.py:61-64` clones at REV, replays a fixture
   and compares lines; `tools/souji-receipt-run.py:4` — "A counter run is only evidence if the bytes that
   produced it are pinned." Fifth copy of clone+run+compare in this lane.
7. **`controls-amended.sh` has no C3 arm and no A2 discriminator** (it defines `c3()` and calls it only for the
   do-nothing base); the A2 cheat states survive only inside wave-1/wave-2 seat receipts. Both controls files
   share an 18-line prologue and r29 ships the identical quartet.
8. **Wave-spec generation is re-derived every round**: `census/round-29/waves/make-spec.py` 121, `census/round-30/waves/make-spec-w1.py` 111,
   `.ufo/waves/round-30/make-spec-w2.py` 93 — 325 lines, near-orthogonal text, all three living inside evidence
   capture directories. This is the largest removable weight and it is not on the named-instrument list.

## Attack log

| Attacked item | Verdict |
|---|---|
| `tools/souji-capability-agreement.py` as a `tools/` resident (v1 blob vs A3) | DEFECT-NOT-FATAL — right home, two unparameterized round literals (F1) |
| v1 → v2 sibling convention for frozen counters | BROKEN — v1 subsumed, 54/108 lines duplicated, no extra discriminating leg (F2) |
| `c2-counter-v2.py` REGRESS-FULL leg | BROKEN — `strip_err` can never match, proven (F3) |
| `c2-counter-v2.py` BIND leg counting the capture with `ls-tree` instead of the manifest | HOLDS — independence is required; manifest.sha256 has 86 members, and trusting it would make the check circular |
| C3 v1+v2 pair | DEFECT-NOT-FATAL — legs disjoint, so the pair is necessary under the convention (F4) |
| C3 L2/L3/L9 (delegation to coverage-agreement, gate-check, sources-census.sh) | HOLDS — 3 of 9 legs are calls, not reimplementations |
| C3 E1/E2 vs `souji-coverage-agreement.py` | DEFECT-NOT-FATAL — strict copy shadowing a lax shared authority (F5) |
| C3 E3 vs `souji-receipt-run.py` | DEFECT-NOT-FATAL — duplicate primitive (F6) |
| `controls.sh` + `controls-amended.sh` | DEFECT-NOT-FATAL — missing C3/A2 arms, duplicated prologue (F7) |
| Wave-spec generators (r29 + r30 w1 + w2) | BROKEN as a pattern — 325 lines, four instances (F8) |
| Extracting the shared clone/normalize helper into `tools/lib` | REJECTED by me — it would break the frozen-counter invariant (runnable from its own revision alone) and let a later lib edit silently change what a re-run measures; keeping the duplication is the cheaper side of this trade |
| C1 K2 vs `souji-declared-evidence.py` class A; C3 L6 vs `souji-registry-agreement.py` K1; L5 vs gate-check check3 | RECORDED, not proposed — merging each moves an enumerated set, so each needs its own round |

Axes unharmed: no lane byte was written outside my two wave-2 files; calibration (7), operability (8) and
coverage (8) surfaces are untouched by this seat, and each proposal is scoped to round 31.

## Deliveries

- `.ufo/waves/round-30/w2/deliver-instrument-sprawl.md` — full inventory (reusable / one-round / consolidate),
  the measured duplication table, proposals P1-P6 for round 31, the explicit stop condition (keep the four
  clone helpers duplicated), and defects D1-D3.

Report path (relative to the lane): `.ufo/waves/round-30/w2/SwarmSimplifier34.md`.
