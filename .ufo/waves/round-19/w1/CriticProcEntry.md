STATUS: DONE — C3 is a modest knowledge synthesis, but its current scope overstates enumeration; keep Core observation-only and reconcile the province boundary.

# Findings

**Strongest objection — coverage is described more broadly than the implementation can observe.** The entry says the tool emits a row per own-UID process meeting the residue predicates (`corpus/knowledge/process-residue-observations.md:35-44`), but the scan explicitly excludes itself and any process whose observed parent chain reaches it (`tools/souji-proc-census.sh:135-144,314-334`). It also silently drops processes when `/proc/<pid>/status` cannot be read, treats an unreadable cwd as empty, ignores cmdline read errors, skips unreadable fd links, and drops rows when the UID/starttime recheck fails (`tools/souji-proc-census.sh:147-157,230-276,340-355,370-377`). This matters especially because the entry itself notes ptrace access checks for cwd, fd and wchan (`process-residue-observations.md:15-22`). Thus even among same-UID processes, “one row per” is not exhaustive: a residue held by an inaccessible process or the census's own descendant tree can be omitted, and an empty output is not evidence of absence. The existing non-atomic and PID-namespace limits (`process-residue-observations.md:84-91`) do not disclose these intentional/skipped cases. This is the coverage blocker; it is fixable by narrowing the claim and naming the omissions, without widening the tool.

**Knowledge versus copy.** The entry is not merely a copy of S067–S069: S067 concerns subprocess timeout/session behavior and is not used by the entry; S068/S069 were narrowed/rechecked as S075/S076; and S082–S085 add proc-page descriptions of cwd/fd/wchan/status and access checks (`corpus/SOURCES.md:87-89,95-96,102-105`). The useful synthesis is the explicit divide between what the exe man page documents and what cwd/fd fixture cases observe (`process-residue-observations.md:26-31`), plus the distinction between row context and action/liveness proof. However, the field/column/precedence inventory mostly repeats the tool and Q32/Q33, while the counter disagreement is already in the r18 lesson (entry `:35-63`; `corpus/QUALITY.md:81-83`; `corpus/lessons/round-18.md:31-32`). Treat this as a sourced, scope-specific reference—not a new detection capability, independent validation, or proof that the census is complete. With the missing observation limit made explicit, it qualifies as a knowledge entry rather than a bare paraphrase.

**Core boundary.** The README promotion is properly narrow: it says “Core for the observation surface,” and keeps the reap ruling in the r19 Frontier (`corpus/README.md:274,279-281`). The entry denies reap authority and sends other-UID/host-health findings out of scope (`process-residue-observations.md:79-91`); PROVINCE routes host liveness/resource findings to mori (`PROVINCE.md:43-52`). So this does not overclaim reaping authority or mori's liveness evidence if “mori” remains an ownership/routing boundary, not a claim that this entry measured or verified mori's work. Do not promote all of F5: reap remains operator-owned, and cross-UID/host liveness remains outside this observation surface. One current inconsistency must be reconciled before the promotion is treated as canonical: `PROVINCE.md:61-78` still says F5 has no knowledge entry and is frontier, which is false in this worktree. Smallest safe map change: mark only the own-UID, list-only observation surface Core (admission still pending); keep reap frontier/operator-owned and other-UID/host liveness adjacent/routed to mori.

**Exact limits the entry must contain.** The first sentence below is missing and is required by the code's omission behavior. The other sentences preserve or sharpen limits already present at `process-residue-observations.md:26-31,79-91`:

> The census omits itself and processes whose observed parent chain reaches it; unreadable per-process `/proc` fields and PID/UID/starttime recheck failures are skipped, so an empty result does not prove that no eligible residue exists among all current-UID processes.
>
> The scan is non-atomic and sees only processes exposed through its `/proc` view and current UID; it is not a cross-UID or host-wide liveness census, and routing findings to mori does not mean mori's liveness was measured here.
>
> A row is a nomination, not a removal receipt or kill/reap authorization; any action requires operator approval, fresh `(pid, starttime, boot_id)` verification at act time, and a LOG record.
>
> `proc_pid_exe(5)` documents the deleted annotation for exe only; applying suffix checks to cwd/fd is a fixture-supported inference, not a statement in those man pages.
>
> A listed link does not prove the target's bytes are unrecoverable or any artifact safe to delete; PID-namespace differences remain unmeasured.

**Next-round falsifiers.** Reopen S082–S085 at their recorded anchors and revise any claim whose documented scope has drifted. Re-run the named P1–P19 fixture (`tests/fixtures/r18-proc-census.sh:4-21`): missing P1/P2/P9 positives, false P3/P10/P12/P13 rows, wrong P11 identity, P18/P19 precedence, secret leakage in P6/P14–P16, or any P7 signal syscall falsifies the corresponding claim. Add a same-UID access-denied case and a controlled census-descendant residue case: if either is omitted without an incomplete/limited-result indication, it falsifies any renewed claim of complete own-UID coverage. A stable, independently verified PID-set mismatch under a comparable two-window scan falsifies the corresponding agreement observation; a match still cannot establish absence of a shared bug, as the entry already acknowledges (`:67-75`).

**Impacted axes:** coverage (primary: completeness boundary and what the new entry actually adds); calibration/provenance (secondary: keeping documented facts distinct from fixture observations). No claim is made here about executing the entry's recheck commands.

# Evidence

- Worktree entry: `corpus/knowledge/process-residue-observations.md:15-31,35-63,67-91`.
- Implementation omission behavior: `tools/souji-proc-census.sh:135-157,230-276,314-377`.
- Existing fixture cases: `tests/fixtures/r18-proc-census.sh:4-21`; the listed P1–P19 cases do not cover denied per-process reads or the census's own descendant exclusion.
- New and rechecked source rows: `corpus/SOURCES.md:95-96,102-105`; S067–S069 are at `:87-89`.
- Prior counterexample and calibrated historical scope: `corpus/lessons/round-18.md:31-32`; Q32/Q33 at `corpus/QUALITY.md:81-83`.
- Boundary statements: `corpus/README.md:274,279-281`; `PROVINCE.md:43-52,61-78`.

# Commands run

No shell commands, tests, fixture, census, git/jj operation, install, or network request were run. Review was static via repository reads/search only.

# Contract compliance

Wrote only this scoped report. No subagents, scratch files, forbidden paths, or tools/tests/census/corpus edits were used.