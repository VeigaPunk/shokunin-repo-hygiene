## Round 41 boundary note (freeze-check instrument, refusal-site coverage)

Round 41 adds one souji-owned instrument, `tools/souji-freeze-check.py` (C2), and two
fixtures for the existing `tools/souji-worktree-drift.py` (C3 `tests/fixtures/r41-refusal-sites.py`,
R1 `tests/fixtures/r41-drift-record-order.py`). It adds no receipt class, no deletion verdict and no
deletion authority; no `## Owns`, `## Refuses` or `## Adjacency` row changes. Certification stays OFF
and K5 HELD. The C1 CORRECTION lines are lesson and SOURCES content, not a boundary change.

`tools/souji-freeze-check.py` is instrumentation for this lane's own preregistrations. It reads
`census/<round>/preregistration.txt` as the blob at a full 40-hex `--rev`, checks the freeze fields and
the sha256 pins of souji's own counters and populations, and prints `FINDING` and `SUMMARY` lines. It
reads git objects only and is read-only on `--root`. It is not fleet orchestration: it dispatches,
locks and starts nothing, and it does not replace kumitate's round gate or any kumitate marker
check. It is not a protocol gate: no souji-freeze-check reference exists outside this lane, so no
fleet addendum, template, script or sibling SKILL invokes it, and this round does not edit the fleet
addendum's prose freeze rule. It has no authority over other lanes: a `--root` argument is a read
target, and a `FINDING` is advice to this lane's L1, not a verdict on any other lane. The same reading
as the Round 13 and Round 14 wording applies: evidence-integrity checking is limited to souji's own
fragments and does not become fleet orchestration or a promotion authority.

Limit: the round-40 file, read as the retro case, is red through grammar findings only (18
`FIELD-MISSING`; that file predates the `## C<n>` key grammar). Freeze-class findings are exercised by
the synthetic cases in `census/round-41/c2-cases.tsv`, not by the retro file.

One overlap is named, not absorbed. `DISPATCH-BEFORE-FREEZE` reads souji's own
`.ufo/waves/round-N/` markers (`*-dispatch.json` and `*.ready`) and flags any marker added at or
before the freeze commit. It re-derives a marker-ordering rule rather than citing kumitate's
definition, and the two differ: kumitate's `kumitate-shokunin/scripts/plan-before-ready.sh:12-13`
takes the oldest top-level `*.ready`, falling back to a top-level `*-dispatch.json` only when no
`.ready` ever existed; souji's check matches either kind at any depth. Kumitate owns the wave-marker
definition. Souji's check is a local ordering probe over souji's own waves and is not the fleet
definition. Route any change to the marker rule to kumitate.

The refusal-site battery covers the existing `tools/souji-worktree-drift.py`, whose refusal classes
are already souji's Owns line for dead worktree metadata and the Round 39 note above. It reaches all
19 refusal sites with 21 probes and adds no code path and no class to that tool. The R1 fixture adds
mutant kills for the same pinned tool; the TOTAL repair it guards landed before the freeze (`e9dc38d`).

Adjacent, reported and not absorbed (same-name instruments in other lanes; none is souji's):

- `kasegi-shokunin/corpus/instruments/freeze-check.py`: replays each claim's `counter_cmd` at a base
  tree and emits `FC-*` ids, over kasegi's claims-v2 JSON. It is prior art for replay-at-base and is
  not a duplicate of souji's prereg grammar.
- `mori-shokunin/tools/mori-freeze-order.py`: checks that frozen claim inputs predate their
  implementation commits (`mori-freeze-order-v1`). It overlaps the freeze-before-data idea; the
  register and its order rule belong to mori.
- `chousa-shokunin/tools/freeze-check.py` (round 61): a pre-ready check of claims, dispatch, spec and
  ready files, wired into chousa's SKILL row for `freeze-check`. Its dispatch and ready checks are
  closer to `DISPATCH-BEFORE-FREEZE` than kasegi's or mori's tools are. It is chousa's gate.

Two other lanes ship a tool named `freeze-check` (kasegi and chousa). Kengaku's files (70 by a
`-F "freeze-check --double-read"` grep) cite that command, and none is defined under kengaku's `tools/`
or `scripts/`. Souji's instrument keeps the souji prefix (`souji-freeze-check.py`). No lane should add
an unqualified `freeze-check` tool.

Sources: `census/round-41/preregistration.txt` (frozen C1, C2, C3, R1 blocks); `census/round-41/records/`
receipts at the landed commits; `.ufo/waves/round-41/w2/R41w2scribe05.md` (evidence and commands).
