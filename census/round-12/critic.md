# r12 critic — adversarial review of the declared claims

Author: W2RoundSouji-8.R12Critic (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12Critic`; this committed copy is the durable form). 2026-10-19.

## Ranked findings

### CRITICAL — C2 is not causally separable from C1 or C3
**Rule:** `AXES.md:27–34` requires each claim to be verifiable without the others. SOURCES contract v1 §3 keeps admission criteria in `corpus/QUALITY.md`.

**Counterexample / evidence:** C1 creates `QUALITY.md`, which C2 needs to admit entries. The declared K1 plan also requires S031, the C3 fixture’s own-work source. Thus C2 cannot be verified with C1 and C3 absent. Coverage has another prerequisite: `LEARNING.md:30` requires each new entry to cite a coverage-map row, but the current `corpus/README.md` has no `## Frontier`.

**Smallest safe correction:** Before these claims, seed generic QUALITY criteria from existing lessons and the coverage-map rows as unclaimed prerequisites. Let C1 add mistake-specific criteria. Make K1 rely on reopened Git sources, not S031; keep the fixture row optional or outside K1’s admission evidence.

**Axes:** Calibration, coverage, operability.

### HIGH — C1’s completeness check can self-grade
**Rule:** `LEARNING.md:37–45, 54–64` requires outside spot-checking, criteria grounded in lessons, and a Gate section. Calibration is about assessment matching observed repo state (`AXES.md:15`).

**Counterexample / evidence:** C1’s author supplies both the mistake classes and the `captured-by` criteria. A count or “every class has a criterion” check cannot detect omitted classes or permissive criteria. The current snapshot has no `corpus/lessons/round-12.md`. Also, `corpus/README.md:17–18` says every round lesson has a Gate, while STATE §5 reports the earlier lessons lack one.

**Smallest safe correction:** Fix the class inventory to the identified historical evidence—rederive it from the append-only LOG and prior lessons—and have a named non-author audit the rows against the actual SKILL/tools/fixtures. In `## Gate`, list candidates, admissions and rejections with reasons; have that reviewer reopen and judge at least one real admit and one real reject, recording `agree`/`disagree` and reasons. For C1’s exhaustive claim, the reviewer must check the inventory, not just sample two rows. Correct the README’s blanket statement without rewriting historical lessons.

**Axes:** Calibration.

### HIGH — The new fixture can pass without demonstrating pruning, and its scratch path is not fenced
**Rule:** The round’s fixture rule requires work only under `/var/tmp`; PROTOCOL §Gate standard requires a falsifiable verdict.

**Counterexample / evidence:** `tests/fixtures/r12-maintenance-guard.sh:35` uses `${TMPDIR:-/var/tmp}`, so an invocation with `TMPDIR=/tmp` or another location can write outside the required scratch root **[INFERENCE from the script’s path expansion]**. At lines 115–123 it checks only `after == expect`, not the printed `before`. Therefore, if the positive case begins at 1 and remains at 1, it can report PASS without pruning **[INFERENCE from the comparison]**. The captured result (`tests/results/r12-maintenance-guard.txt:10–14`) reports `before=2` in its run, but the script does not enforce that precondition.

**Smallest safe correction:** Hard-code `/var/tmp/souji-r12-XXXXXX`; fail closed unless every case starts with exactly two registrations and ends at its expected count. Record the runtime Git version in the script’s output. The positive case currently sets `maintenance.autoDetach=false`; Git v2.55.0 `run-command.c:1964–1985` shows that this changes foreground/background execution, not whether auto-maintenance runs. Label it as the synchronous reproduction, or add a bounded check of the default detached case.

**Axes:** Operability, calibration.

### HIGH — C3 is a Git fact until the checklist makes it operational; it is not yet a registered gate
**Rule:** `AXES.md:12–13` defines operability by runnable artifacts and executable checklists. PROTOCOL §Gate standard (`:362–389, :400–406`) requires a gate’s self-test and registry row in its registry home.

**Counterexample / evidence:** The fixture and captured output support the Git behavior, but current `SKILL.md:44, 87–90` still describes an ordinary quarantine commit and has no maintenance or pathspec guard row. The script returns failure on mismatches, but has no self-test invocation or SKILL registry row. As it stands, the finding is knowledge; it becomes an operability move only when the workflow is usable from SKILL.

**Smallest safe correction:** Add concise, executable pre-quarantine rows: disable auto-maintenance for that commit, stage only approved paths, and preserve intentionally pinned registrations with `git worktree lock`. If retaining the fail-capable script as a gate, add its self-test invocation, stable expected finding ID, verdict map, pinned-value path, write scope, owner, and registry row. Do not label a fail-capable script a probe.

**Axes:** Operability.

### MEDIUM — C2’s five-entry count is not coverage evidence by itself
**Rule:** SOURCES contract v1 §§1, 4 (`:45–48, :56–58`) requires each new row to be opened in-round and recorded in the lesson Gate; expansion counts admitted entries on uncovered coverage-map ground, not source-row or file counts. `LEARNING.md:30` requires each entry to cite its coverage-map row.

**Counterexample / evidence:** ART rows are leads, not reopened evidence. In the current corpus snapshot, the planned SOURCES file, QUALITY file, and Frontier map are absent. Counting five entries or five `source:` headers would not establish that their sources were opened, mined, or on uncovered ground.

**Smallest safe correction:** Reopen each relied-on source in this round and record the required URL, access date, and short located quote in `## Gate`; ensure each entry’s source resolves to a mined row and each entry cites a prior coverage-map row. The integrator must land those map rows before the expansion claim is measured.

**Axes:** Coverage, calibration.

### MEDIUM — Round records would preserve stale and contradictory state
**Rule:** `AXES.md:27–30` requires before→after evidence in `SCORECARD.md` and `LOG.md`.

**Counterexample / evidence:** `LOG.md:349–360` records that the operator cancelled the 12-round goal and names re-certification as the next task; STATE §6 proposes a different r12 claim set. The current `SCORECARD.md:26–40` still plans through r5, and `:48–53` says receipts are advisory until r10 even though LOG r11 says certification was still withheld for evidence-integrity failures.

**Smallest safe correction:** Record the newly assigned r12 claims as an explicit amendment in the round log, update Planned and the measured axis rows, and keep tool certification OFF unless the r11 evidence-integrity issue is actually resolved. The operator-sweep incident (`LOG.md:379–384`) also makes an explicit-path commit check essential; do not use `git add -A`.

**Axes:** Calibration, operability.

## C3 live-repo commit risk

The read-only command `GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin worktree list --porcelain` showed two registrations—the main checkout and the `kaika/round` checkout—with neither marked `prunable`. No matching maintenance/worktree configuration was returned by the read-only `git config --show-origin --get-regexp` checks on the repo and lane. **No registration that could currently be pruned was observed.**

Git is nevertheless enabled for auto-maintenance by default in v2.55.0 (`run-command.c:1964–1985`); the pruning task and lock/expiry behavior are in [`builtin/gc.c`](https://github.com/git/git/blob/v2.55.0/builtin/gc.c#L379-L430) and [`worktree.c`](https://github.com/git/git/blob/v2.55.0/worktree.c#L949-L1008). The existing fixture result reports the positive and control cases; I did not rerun it.

For the round commit, use a one-shot guard and explicit paths, e.g. stage only reviewed paths, then `git -C <lane-worktree> -c maintenance.auto=false commit --only -- <same-explicit-pathspecs>`. `git worktree lock` protects a specific registration; it is not needed for the two live registrations observed here.

**Runner risk:** No generic fixture auto-discovery was found in the `tests/` search sweep; existing references are to explicit fixture cases. No runner regression is evidenced in this snapshot.

## Claim verdicts

- **C1 — holds-if-fixed.** Appropriate lowest-axis target, but requires an independently audited inventory and a compliant Gate.
- **C2 — falsified as declared.** It depends on C1’s QUALITY file and C3’s fixture source, violating causal separability; the coverage map is also a prerequisite.
- **C3 — holds-if-fixed.** The recorded behavior is supported, but the fixture can false-pass or escape the required scratch root, and the operational checklist/gate wiring is absent in the reviewed snapshot.
