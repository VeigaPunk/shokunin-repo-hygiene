## Status
STATUS: PASS — scoped cross-claim analysis and delivery completed; no C1/C2 counter run is claimed.

## Evidence

- Read frozen contract first at `census/round-34/preregistration.txt` (`2b0171e2071fdc9c16a69bed12b0d040e574d8c8`), then both counter docstrings and `c1-items.tsv` / `c2-legs.tsv` at the freeze. C1 counter lines 4–8: “runs the item argv from the clone root”. C2 legs lines 34–40 specify W1/W2/W3/W4/N3/N4 argv.
- Direct C1 argv/files intersection with C2 target paths: G01 and G07 list `tools/souji-census.sh`. Source trace: `tools/souji-preservation-evidence.py:1906-1923` reads and pin-checks r14 fixture in G02 selftest; `tests/fixtures/r15-preservation-evidence.py:147-159` copies the actual r15 config and r14 namespace fixtures; `census/round-21/run-acceptance.py:301-353,671-688` runs its inventory, including the evidence-cache demo at 338–343. Therefore G17a/G17b have transitive runtime coupling to `tools/souji-evidence-cache.py`; G15/G16 only call runner functions with synthetic inputs, and G18 consumes fixed oracle data without running child commands.
- C2 guards: `census/round-34/c2-counter.py:207-229`. G2 gets changed path names and checks its allowlist. G5 comment quote: “Per-commit path-disjointness across the two claim namespaces.” Its actual C1 path set is only SCORECARD.md/SKILL.md and its C2 set only c2-legs.tsv/c2-counter.py. Neither guard reads doc contents; C2 leg argv contains no SCORECARD/SKILL path. Preregistration lines 117–118 says: “C1 is verifiable without C2 (its items run no r34 file) and C2 without C1 (its legs run no SCORECARD/SKILL row)”.
- Commit command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline 9c76c7222a8abff027af42e37f0d160d52526bba..2b0171e2071fdc9c16a69bed12b0d040e574d8c8` → `2b0171e`, `73f029e`, `2b59192`. The follow-up `git show --name-only --format="%h %s" <range>` output showed 2b0171e changes c2-counter; 73f029e changes c2-counter, preregistration, r34-c1-junk; 2b59192 changes both C1 and C2 counters/items/legs plus preregistration, both r34 fixtures and census-start/closure-sweep. No listed commit changes SCORECARD.md or SKILL.md.

## Findings

1. G01/G07 output can move if `tools/souji-census.sh` changes while their SKILL rows stay unchanged. G17a/G17b may move if the evidence-cache tool changes through the acceptance runner; G02/G03 may move if their consumed r14/r15 fixture bytes change. The frozen C2 scope says “C2 touches only: census/round-34/c2-*, tests/fixtures/r34-*”; thus these shared-path edits are not allowed C2 work. G6 also pins the r14 fixture. For transitive G02/G03/G17a/G17b dependencies, C1 item file sets do not declare the shared tool/fixture causes, so the frozen cause rule would not permit restatement if such a cause occurred. This is latent coupling, not a measured output change.
2. No C2 guard or leg reads SCORECARD.md/SKILL.md contents. G2 and G5 do inspect those path names in diffs/commit paths, so a C1 doc-only restatement changes guard inputs, but does not alter C2 measurement; a separate C1 commit is allowed by G2 and does not intersect G5's C2 paths.
3. **ATTACK (reproduced source-state): G5's implementation is narrower than the preregistered complete C1/C2-file-set wording.** Commit `2b59192`, present in the enumerated `base..freeze` ancestry, touches `census/round-34/c1-counter.py` and `c1-items.tsv` together with `c2-counter.py` and `c2-legs.tsv`. But G5 tests C1 paths only against SCORECARD.md/SKILL.md, so that mixed commit is not detected by its configured intersection. The L1's planned separate landing commits can honor the implemented check, but that does not establish full-file-set disjointness. No frozen counter or predicate was changed.

## Attack log

- G5 scope gap: reproduced with the committed `2b59192` name-only listing and the G5 sets at `c2-counter.py:220-229`. Contradiction: preregistration says “per-commit disjointness of the C1 and C2 file sets”; implementation omits C1 counter/items from the checked C1 set.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-cross-claim.txt` — full separability evidence, bounded move, risks, and attack details.
- `.ufo/waves/round-34/w1/SwarmConnector30.md` — this scoped report.
