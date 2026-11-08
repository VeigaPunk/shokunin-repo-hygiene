# DRAFT — `corpus/QUALITY.md`, two rows under a new `## Round 84 criteria` heading

Seat: S84Scribe (drafts only; the L1 integrates). Draft file; the L1 appends the block below to `corpus/QUALITY.md`.

> **STATUS: superseded as an integration input.** The L1 landed its own `## Round 84 criteria` section with rows
> **Q154** and **Q155** at `4557fc71`. The landed rows carry the same two criterion sentences this seat was asked
> to draft; the landed Q155 adds the round's own clause-coverage requirement ("the population states which of the
> repair's clauses are load-bearing"), which the L1 measured with its filed-byte mutant battery. This draft is
> kept for the L1 to re-check or extend; where the two differ the **landed text is the lane's**.

## Where it lands

`corpus/QUALITY.md` currently ends with the `## Round 83 criteria` section (rows Q152, Q153). The L1 appends a new
`## Round 84 criteria` section after it, carrying the two rows below with the ids **Q154** and **Q155** (Q153 is
the highest id in the file today). The L1 should verify the next free id at integration time and shift the numbers
if another row has landed.

The table header matches the round-83 section's shape (`| id | criterion | applies to | test | lesson |`).

## Draft block (paste-ready)

---

## Round 84 criteria

| id | criterion | applies to | test | lesson |
|---|---|---|---|---|
| Q154 | A population is judged by what its rows kill: every clause the rule enforces carries a false row and every real shape a true row. A clause with no row is invisible to the population, so the population certifies a rule it does not discriminate. The judge is a mutation battery over the rule's own counter: each single-edit mutant that drops one clause must go red on the population, and the same battery on the previous population must leave it green (otherwise the delta is vacuous). The population carries one FALSE row per clause (a real copy whose bytes differ from the token's frozen digest; a byte-equal copy in another round's tree; a token flattened one component; a non-wave directory under the own tree; a real wave prefix that drops the token's suffix) and one TRUE row per real shape the rule names (a deep token under a real `w2/`, and the lane's real `a2w1/` and `assimilation/` wave directories). A rule that names a shape no row exercises is prose, not calibration. Limits it states: a population proves discrimination on its own rows, not the rule's correctness on the world; the false rows are byte-equal copies of the token's byte source by construction, so they test location binding, not content identity; the mutants are hand-written single edits, not a generated battery; a kill is a non-zero harness exit, which cannot distinguish a row mismatch from a harness error; the populations are sha256-pinned, so editing a row kills the claim rather than changing it. | pointer-resolution counters and any calibration population (r84 own-tree binding) | the r84 clause battery over the pinned 44-row population: pristine `rows=44 mismatches=0`, all five frozen mutants killed (`killed_r84=5`, EXIT 0), with the per-mutant killing rows named (NF-L; NF-L2; TF9+TF10; TF8+TF9+TF10+NF-P; NF-M); the same battery on the r83 36-row population leaves all five green (`killed_r83=0`, EXIT 0) — `census/round-84/records/c1-after.txt`, `census/round-84/controls/c1-before-r83-population.txt`, `census/round-84/c1-mutants.json`; the row detail in `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-per-mutant-rows.txt` | corpus/lessons/round-83.md `## Routed to round 84` item 1 (the C1 deep-token pair and the NF-L/NF-L2/NF-M/NF-L3 rows the mutants named; true rows for `a2w1/` and `assimilation/`); corpus/QUALITY.md Q152; plans/round-83.md A2 (the basename-only rule scored 36/36 on the r83 population) |
| Q155 | A signal-path repair names the descendant it could not see and the pass that now sees it. A repair that closes a late-fork escape states the escape's shape (a CLI that traps the caller's signal and forks a child after the map pass, leaving the tool's process group), says why one pass cannot see it (the child was never in the map, and a `setsid` also leaves the group), names the pass that now covers it (a second fork-free map pass over the frozen tree) and the mechanism that removes the trap from the path (SIGSTOP each descendant before any trappable signal reaches it — a stopped process can neither run a trap nor fork — then SIGKILL the frozen set). The repair's own instrumentation is checked the same way: the identity re-read before each signal is guarded on the CONTENT of the stat file, not on the exit status of the read that fetched it, because `IFS= read -r -d ''` returns non-zero at EOF even though it read the whole file (the bash manual's `read` node: "The exit status is zero, unless end-of-file is encountered"), so a status guard skips EVERY descendant and disables the freeze outright; the opposite shape, a first-line read, skips only a descendant whose `comm` carries a newline (r83 spot-check D5). The two error modes are opposite and both silent, so a repair states which one its bytes have. Limits it states: a child forked after the second pass is not seen; `/proc` is not an atomic snapshot, so a child whose parent died in the read→STOP window is not a descendant any pass could see; pidfd is not used (bash only), so the STOP→KILL pair widens the pid-reuse window; a child that reparents before the second map is missed; a descendant that left the tree before the walk is never found. | signal-path repairs over a descendant tree (the vault CLI's abort path) | the frozen 22-row population with the late-fork rows: `SUMMARY rows=22 mismatches=0 errors=0 orphans=0` with both late rows at `survivors=0 tmpleft=0` inside the 5 s settle, against the r83 control at `mismatches=2` with one survivor each — `census/round-84/records/c2-reference-prefreeze.txt`, `.ufo/waves/round-84/w1/S84ExecC2/c2-after-receipt.txt`, `census/round-84/controls/c2-before-r83-tool.txt`; the `latefork` stub bytes in `census/round-84/c2-late-fork-counter.py` (`STUBS["latefork"]`); the guard defect, the measured read shapes and the minimal reproducer in `.ufo/waves/round-84/w1/S84Scribe/receipts/d5-read-shapes.txt`, `repro-read-d-status.sh` and `c2-refc2-current-bytes-FAILING.txt` | corpus/lessons/round-83.md `## Routed to round 84` item 2; corpus/lessons/round-83-verifier-spotcheck.md D5 (the whole-file stat read was scoped to the map pass only); corpus/QUALITY.md Q153 |

## Grounding map for the L1

| row | grounded in |
|---|---|
| Q154's five false rows and three true rows | `census/round-84/c1-false-rows.tsv` (TF8, TF9, TF10, NF-P, NF-L, NF-L2, NF-M, NF-Q) |
| Q154's kill numbers and the before arm | `census/round-84/records/c1-after.txt`; `census/round-84/controls/c1-before-r83-population.txt`; re-measured in `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-battery-r84.txt` and `c1-before-r83.txt` |
| Q154's per-mutant killing rows | `.ufo/waves/round-84/w1/S84Scribe/receipts/c1-per-mutant-rows.txt` |
| Q154's "shape no row exercises is prose" | `corpus/QUALITY.md` Q152; `plans/round-83.md` A2 |
| Q154's "byte-equal by construction / hand-written mutants / kill is a non-zero exit / sha256-pinned" | `census/round-84/preregistration.txt` C1 "Stated limits (frozen)"; `census/round-84/c1-false-row-harness.py` `POP_PINS`; `census/round-84/c1-clause-battery.py` |
| Q155's escape shape, why one pass cannot see it, the second pass, the freeze mechanism | `census/round-84/preregistration.txt` C2 stated wording; `census/round-84/c2-late-fork-counter.py` `STUBS["latefork"]`; `.ufo/waves/round-84/w1/S84ExecC2/cli_kill_tree.diff` |
| Q155's measured rows and the r83 control | `census/round-84/records/c2-reference-prefreeze.txt`; `.ufo/waves/round-84/w1/S84ExecC2/c2-after-receipt.txt`; `census/round-84/controls/c2-before-r83-tool.txt` |
| Q155's `read -d ''` guard defect and the reproducer | `.ufo/waves/round-84/w1/S84Scribe/receipts/repro-read-d-status.sh` + `.out`; `c2-refc2-current-bytes-FAILING.txt`; `c2-fix-candidate.txt` |
| Q155's limits | `census/round-84/preregistration.txt` C2 "Stated limits (frozen)" |
| the lesson pointers | `corpus/lessons/round-83.md` `## Routed to round 84` items 1 and 2; `corpus/lessons/round-83-verifier-spotcheck.md` D5 |
