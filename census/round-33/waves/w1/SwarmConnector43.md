# SwarmConnector43 — sibling-overlap scan (r33 w1)

## Status
STATUS: PASS — sibling-overlap scan complete over 20 sibling `*-shokunin` repos (souji excluded) across
PROVINCE.md / SKILL.md / SCORECARD.md / corpus/QUALITY.md / corpus/knowledge/**.md; 24 located hits,
0 contested scope (all closed historical landings in siblings' own repos). Delivery:
`.ufo/waves/round-33/w1/deliver-sibling-overlap.md`.

## Evidence
- Commands (all read-only, run 2026-10-26 from `/home/vgpnk/Projects/shokunin`): presence sweep over
  20 sibling repos; `grep -rn -i` for TMPDIR / mkdtemp|gettempdir|tempfile / bwrap|bubblewrap /
  scratch(-)root / trailing-slash variants / capability-currency terms across the five file classes.
- Output excerpts (lane, file:line):
  - tameshi `corpus/knowledge/executable-self-assessment.md:7` "A standing capability row says what a
    tool can do and quotes what its command printed."; `:66` "Correct a stale row by appending a new
    statement; never edit or delete the old row."
  - mado `SCORECARD.md:1625` "capability table vs frozen re-demonstration … 1/12 mismatches → 0/12".
  - game-dev-3d `corpus/knowledge/unreal-mcp/gate/run_gate.sh:59` "WORK_ROOT=${GATE_WORKDIR:-${TMPDIR:-/tmp}}";
    `README.md:379` W2 "WORK_ROOT=… (from TMPDIR)" … "the POSIX convention is honoured".
  - mori `SKILL.md:604` "Use an existing private scratch root for selftests; do not let an invalid
    TMPDIR fall back to /tmp."
  - chousa `SKILL.md:162` "strips all trailing slashes for the prefix test only";
    `corpus/knowledge/verification-r16.md:67` "`in_root` now strips all trailing slashes".
  - kama `corpus/QUALITY.md:353` KQ51 "A lane counter removes every temporary directory it creates".
  - tsukuroi `SCORECARD.md:1312` "Re-run `python3 tools/check-self-assessment.py --revision <REV>`
    before treating any count here as current."
  - kotodama `SCORECARD.md:426` "50/50 capability rows exit 0" … "all 50 recorded commands re-executed green".
  - kumitate `corpus/knowledge/mount-order-and-bind-scope.md:9` "mounts fresh `/tmp` and `/run` tmpfs roots".
- Revisions: lane repos at their working-tree HEADs as of 2026-10-26 (read-only; no commits inspected
  beyond grep context). Souji refs from the frozen contract: base `6017a482e7068d5afb7617640198fbb0fe743357`,
  list-rev `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`.
- Tools used: bash coreutils + grep + sed only. No installs, no scratch dir needed (scan is read-only;
  nothing exceeded 50 MB; no clone was required for a grep-level scan).

## Findings
1. **C1-CURRENCY has close doctrine neighbours, none contested** (deliverable §1): tameshi
   `executable-self-assessment.md:7,66` encodes the identical method (capability row = claim with a
   check; stale row corrected only by append); tameshi `SCORECARD.md:2172` round-46/47 restatement
   counter re-runs row commands; mado `SCORECARD.md:1625` (r24 C2, "capability table vs frozen
   re-demonstration", mismatch count → 0) is the same measurement shape as `c1-counter.py`;
   kotodama `SCORECARD.md:426` re-executed all 50 recorded capability commands green; tsukuroi
   `SCORECARD.md:1312` and `corpus/QUALITY.md:873` re-run/resolve capability rows; chousa
   `corpus/QUALITY.md:881,915` and kaidoku `SCORECARD.md:3119-3136` audit capability-row pointers
   and counts. All closed; all in siblings' own tables.
2. **C2-SCRATCH has a landed Q71-identical prior art** (deliverable §2): game-dev-3d gate r104
   (`run_gate.sh:59`, README W0-W2 controls) repaired the same defect class — scratch root from
   `TMPDIR` with `/tmp` default preserved, nonexistent root refused up front. kama KQ51
   (`corpus/QUALITY.md:353`) is the private-TMPDIR hygiene leg; tameshi `guard-kill-closure.md:129`
   and kumitate `mount-order-and-bind-scope.md:9` are bwrap private-/tmp discipline; chousa
   `SKILL.md:162` / `verification-r16.md:67` strip all trailing slashes (root prefix test, not
   TMPDIR — mechanism overlap only); mori `SKILL.md:604` plus four r18/r22 knowledge entries are the
   inverse rule (selftests *require* a repo-local TMPDIR and refuse /tmp fallback).
3. **Non-overlap determinations** (deliverable §2 rows 22-24): audio `SCORECARD.md:873,892` is
   TMPDIR-lock co-tenancy (lock folding), not scratch root; kagi `handler-on-disk-state.md:233-246`
   is TMUX_TMPDIR server isolation; kaidoku `SKILL.md:559` et al. is disk-backed TMPDIR for REA under
   the host `/tmp` quota — the same host condition that motivates souji O1, but a different repair
   surface. None overlap.
4. **Confusion risk, not scope contest** (deliverable §3): tsukuroi's own `child-env-allowlist-r33`
   probe (`tsukuroi-shokunin/SKILL.md:2870,2940,3001,3106`) shares the "r33" number and names TMPDIR
   as a value-channel leak name, but its surface is child-environment allow-listing, not scratch-root
   discipline. Fleet reports should disambiguate "r33" by lane.
5. **Recommendations to the L1** (deliverable §4, reported never absorbed): (a) cite tameshi
   executable-self-assessment as sibling doctrine in the C1 lesson Gate, not as a new mistake class;
   (b) cite game-dev-3d r104 as corroborating prior art in the C2 SKILL error-pattern bullet — it
   does not replace the SOURCES rows the preregistration requires souji to open itself; (c) no
   sibling handoff needed this round.

## Attack log
Not an attack item. No frozen predicate, target, counter, item or leg challenged; the scan found the
frozen scope uncontested.

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-sibling-overlap.md`
- No scratch dir was created (read-only grep-level scan; no clone, no download, nothing over 50 MB).
