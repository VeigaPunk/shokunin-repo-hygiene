## Status
STATUS: PARTIAL — inspected frozen inputs and base surfaces; did not complete a byte-by-byte row ledger or run missed-row falsifiers.

## Evidence
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 9c76c7222a8abff027af42e37f0d160d52526bba:{SCORECARD.md,SKILL.md,SHONEN.md}` — base copies read; revision `9c76c7222a8abff027af42e37f0d160d52526bba`.
- `git -C ... show 2b0171e2071fdc9c16a69bed12b0d040e574d8c8:census/round-34/c1-items.tsv` — frozen item set inspected.
- `git clone -q --no-local ... /fast/scratch/hyaku/souji-r34/MissedRows/c; git -C ... remote remove origin; git -C ... rev-parse --show-toplevel; git -C ... checkout --detach 2b0171e2071fdc9c16a69bed12b0d040e574d8c8` — clone root verified and frozen revision checked out.
- `grep -nE '` command-pattern `|numeric-result-pattern' /fast/scratch/hyaku/souji-r34/MissedRows/SHONEN.md` — only relevant numeric prose found at line 10: `census/round-21/accepted-matrix.json (3/3 sources, each18/18)`; no runnable command there.
- `/proc/loadavg` adjacent to scratch setup/read: `21.32 11.52 5.83 ...`; subsequent clone read: `21.97 12.27 6.20 ...`.

## Findings
1. The frozen contract defines the SCORECARD surface and explicitly named exclusions in `census/round-34/preregistration.txt`, C1. Verbatim: “one item per (argv, statement) pair”. Confidence: high for the clause, incomplete for exhaustiveness of my enumeration.
2. The TSV explicitly identifies line locations and item identities for the frozen 60 rows (`census/round-34/c1-items.tsv`, rows G01–G26 and E01–E34, with stated exclusions/splits). I did not produce the requested row-by-row mapping for every eligible table row; no claim of full enumeration.
3. SHONEN.md contains a numeric evidence reference but no runnable command in that cited bullet (`SHONEN.md:10`); correctly excluded by the runnable-command clause. The file's other listed bullets likewise do not include a runnable command paired with a numeric outcome in the inspected contents.
4. No missed-row falsifier was run. Accordingly, there is no reproduction verdict. This is an execution gap, not evidence that the frozen set has no misses.
5. No LSP device was available in the supplied tool inventory; this is Markdown enumeration, not symbol resolution.

## Attack log
None. No frozen predicate/item change proposed.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-missed-rows.txt` — scoped residual notes; not an exhaustive row ledger.
