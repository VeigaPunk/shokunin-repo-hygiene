# SwarmConnector29 — r32 a2w1 cross-claim and separability check on what landed

## Status

STATUS: PASS — all three seat questions answered from bytes and live runs: (1) C3 moves T18's anchor (+1, verified three
ways), and the separability paragraph missed four more couplings (C2→C2 self, C3→C2 closure, contingent C2→C1 run-callee,
structural C2→C3); (2) C2's patch moves no landed C1 binding (N12/N16/N19 MATCH at tip under v1 and v2; only the entry
script is base-materialized, callees are REV bytes — N16 execs the C2-patched auditor and is output-neutral); (3) C1's
SCORECARD append does not move T03 (fixed-rev read; PASS at tip). Wave-1 mistake classes mapped to r28–r31 lessons; one
bounded move proposed to the L1. Lane untouched (read-only; reports + delivery under `.ufo/waves/round-32/a2w1/`).

## Evidence

Revisions: base 85b61a151923986e7e6b48f7084b9122561b5f3d, C2 98e5203d45b4e419a9e72801733d93303acc7ebd,
C3 a92e1aae91dbf46c2d7eff713932cfc820186970, C1 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93, tip 4e56c48b8fc828f9aba2746e324dc46aa538bdbf.

1. Static closure recompute (fixture's algorithm, `tests/fixtures/r20-input-binding.py:1252-1256,1137-1163`):
   `baseline_mismatches` = 26 (base) → 31 (C2, +5 closure tools C2 patched) → 32 (C3, +1 new knowledge entry) → 32 (C1) → 32 (tip).
   Closure membership: `census/round-13/run-verification.py:107-109` (`corpus/SOURCES.md`, `corpus/knowledge`, `LOG.md`).
   `corpus/SOURCES.md` count-neutral at C3 (already among the 26 at base).
2. Live fixture T18: base prints `... baseline_mismatches=26`; tip prints `... baseline_mismatches=32`.
3. Frozen c2-counter at tip (`python3 -B census/round-32/c2-counter.py … --only T03,T18`):
   `ITEM T03 PASS base=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23 sbox=…identical…`;
   `ITEM T18 FAIL base=…baseline_mismatches=26 sbox=…baseline_mismatches=32 regress`.
4. Frozen c1-counter v1 and v2 at tip over all 44 items: `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9
   withdrawn=17 unbound=6 mismatches=6` (mismatches are the 6 unbound; all bound rows MATCH). Run rows N12, N16, N19 each MATCH.
5. Mechanism bytes: `census/round-32/c1-counter.py:227-231` materializes only `script_of(argv)` from the base blob; REV
   clone supplies every callee. `tools/souji-declared-evidence.py:73-80` reads declarations from the named rev, never the
   worktree. `tools/souji-landing-gate.py:239,1189` reads SKILL/README/SCORECARD via `git ls-tree`/`show` at the named rev.
   `census/round-32/c3-counter.py:150,154` runs coverage/gate tools from the rev-V export.
6. Q65 recurrences: `.gitignore:1` (`.ufo/waves/`); `git cat-file -e 4e56c48:.ufo/waves/round-32/w1/SwarmCritic35.md` rc 128;
   committed citations at `census/round-32/records/amendments.txt:14` and
   `corpus/knowledge/jj-abandoned-object-mtime-clock.md:4` (the latter's sha256 `01cf6dc0…` matches the on-disk file).

## Findings

1. C3→C2 (T18): verified — the new entry moves the anchor +1; SOURCES edit is hash-moving but count-neutral (already mismatched at base).
2. C2→C2 (self), missed by the paragraph: T18's frozen S-equality is unsatisfiable at any rev carrying C2's own fix
   (5 closure tools) — Q58-class (r28 spotcheck d4) preregistration defect.
3. C2→C1 is contingent: base-blob pinning covers the entry script only; landed run bindings survive because their live
   callees are unpatched (N12, N19) or output-neutral under the patch (N16 execs C2-patched `tools/souji-seat-audit.py`).
   Wave-1 SwarmCritic37 demonstrated a C2 rule edit flipping run-bound N35/N36; the landed rows rebind those as record bindings.
4. C2→C3 is structural but output-neutral: L2/L3 execute export-at-V bytes; C2's gate-check hunk is selftest-scratch-only.
5. C1→C2 T03 and C1/C3→T02/T25/T26/T29/T30: no coupling — fixed-rev git reads or synthetic data (verified from bytes; T03 PASS at tip).
6. Recurring mistake classes: Q58 (T18), instrument/gaming (SwarmCritic34 disclosed-not-amended; SwarmCritic35 → A1),
   contract/dishonest-receipt (fake 200 receipt, caught by A1 L17; M1 guard shipped), reference-drift/Q65 (two committed
   citations of gitignored `.ufo/waves/round-32` paths), disposition class not recurring, host-loss class new (attempt-1
   crash; salvage after-records re-derived clean this run).

## Attack log

Not an attack seat; no counter gameability claims filed. Closest attack-shaped observation: T18's frozen predicate admits
no honest passing state at any landed rev — reported as Finding 2 with the byte attribution, and covered by the already-logged
"missed" disposition in `census/round-32/records/amendments.txt`.

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-cross-claim-w2.md` — full cross-claim/separability analysis with the bounded L1 move (carry T18 attribution + final-tip re-measure receipt; append-only correction of the two `.ufo` citations; route C2's disclosed predicate gap to r33).

No installs or upgrades were needed (bwrap/strace already present). Scratch `/fast/scratch/hyaku/souji-r32/SwarmConnector29` removed after copying deliveries.
