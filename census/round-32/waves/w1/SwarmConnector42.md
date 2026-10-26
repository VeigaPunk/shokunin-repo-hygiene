# SwarmConnector42 — r32 w1 cross-claim pattern report

## Status
STATUS: PASS — read-only cross-claim review completed; deliverable `deliver-cross-claim.md` written; no counters executed, no lane bytes modified, no scratch created.

## Evidence
- Lane state (read-only): base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg `3ec84fc81b3243429c834a051880b0bcde06291c`, controls `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; `git status --porcelain -uno` empty (worktree clean at controls commit).
- Bytes opened: `census/round-32/records/preregistration.txt`, `c1-counter.py`, `c1-counter-v2.py`, `c1-enumerate.py`, `c2-counter.py`, `c3-counter.py`, `c3-contract.txt`, `c1-items.tsv`, `c2-items.tsv`, `records/controls.tsv`, `records/amendments.txt` (A0), `records/m1-red-before.txt`, `m1-r31-contract.txt`, `tools/souji-record-contract.py`, `tools/souji-declared-evidence.py`, `tools/souji-landing-gate.py`, `tests/fixtures/r17-jj-receipts.sh`, `tests/fixtures/r31-jj-object-clock.sh`, `SCORECARD.md` (raw lines 147-176, 313-315, 354-355, 422-424), `corpus/lessons/round-28.md`, `round-29.md`, `round-30.md`, `round-31.md` (## Mistakes).

## Findings
1. **C2→C1 coupling (F1):** C1 `run:` bindings execute the base-blob script inside a REV clone whose sibling files are REV bytes. N35–N42 share T30's exact argv (fixture + `souji-landing-gate.py`), N12 consumes `souji-verify.sh` (T15), N22–N24 share T27. C2's invariants pin only the REV-fixture+REV-tool combo, not C1's base-fixture+REV-tool combo. Prereg's causal-separability sentence holds only for self-contained scripts.
2. **C1 duplicate hazard (F2):** binding rows are unnamespaced; a same-shaped row for the same id+line appended later (next round's supersession block, or a wave-2 correction) flips the item to `BAD-ROW(duplicate)`; `withdrawn` appended over a binding also duplicates → no post-landing repair path exists.
3. **C2×SCORECARD immune (F3):** T03 reads the declaration via git blob at `--rev` (base); landing-gate family reads only committed bytes; C1's appended rows cannot perturb C2 anchors.
4. **C3 fixture hygiene (F4):** r31 fixture already honours TMPDIR (guard + `mktemp -d "$TMPDIR/..."`); the new r32 fixture is outside C2's frozen enumeration and C3 replays are not sandboxed, so its scratch discipline is enforced by nothing mechanical — grep gate at delivery.
5. **M1×L14 parity (F5):** `contract_bad()` and the M1 tool are equivalent for the frozen contract (exact key order, set membership); divergences: wildcard `*`/`#` members (tool only) and malformed-contract behaviour (tool exit 2 vs counter flags). L14 does not invoke the tool; D1 value-set violations are caught identically, dangling-citation D1 is caught by neither.
6. **Recurring classes (F6):** vacuous target reaches (r29–r31) → C2's creation floor permits halving work; record-outside-contract/scope (r30) → C3 L10 does not guard prose claims, only backticked RESULT spans; landing/carry → safe here because C1 payload paths are blob-checked.
7. **C1 binding-channel budget (F7):** N15–N17 (line 168), N20–N21 (line 313), N22–N24 (line 314) have no A0(a)-eligible cited census path and no script stem — only `withdrawn` remains, saturating the cap of 8 exactly; N19/N43/N06–N11 are borderline. Plan must validate binding budget before committing rows.

## Attack log
None filed (connector seat; no counter defect reproduced). Structural advisories F2/F1 are design notes, not attacks.

## Deliveries
- `.ufo/waves/round-32/w1/deliver-cross-claim.md` (cross-claim findings F1–F7, evidence quotes, recommendations).
