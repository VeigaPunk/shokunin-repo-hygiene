# ExecC2Attribution — C2 attribution correction (round 100)

## Completed edits

1. `corpus/knowledge/deadline-owned-reaping.md`: appended at end (after line 76)
   `## Round-100 correction (append-only; S075 field-4 attribution withdrawn)` — cites S332
   (kernel emission order, `fs/proc/array.c` `do_task_stat()` v6.17) for the field-4 ppid wording,
   withdraws the in-body "S075 field 4" attribution in favour of S332, states the field-22
   starttime attribution to S075 stands. Append-only; no filed byte rewritten.

2. `corpus/SOURCES.md`: S075 used-by cell now ends
   `..., corpus/knowledge/gate-signal-handling.md, corpus/knowledge/deadline-owned-reaping.md`.
   No other cell changed, no row added/removed, no other row touched. No new SOURCES row.

## Commands run (cwd /home/vgpnk/Projects/shokunin/souji-shokunin, exit codes observed)

- Baseline before edit: `grep -c 'S332' corpus/knowledge/deadline-owned-reaping.md` -> `0`;
  `awk -F'|' '/^\|[[:space:]]*S075[[:space:]]*\|/ {print $12}' corpus/SOURCES.md` ->
  ` corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md, corpus/knowledge/gate-signal-handling.md `

- Post-edit verification (frozen predicate, in seat spec):
  - `grep -c 'S332' corpus/knowledge/deadline-owned-reaping.md` -> prints `1` (exit 0). So >= 1 holds.
  - `awk -F'|' '/^\|[[:space:]]*S075[[:space:]]*\|/ {print $12}' corpus/SOURCES.md` -> prints
    ` corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md, corpus/knowledge/gate-signal-handling.md, corpus/knowledge/deadline-owned-reaping.md `
    — contains `deadline-owned-reaping.md`. Holds.
  - `git diff --stat` -> `corpus/SOURCES.md | 2 +-`, `corpus/knowledge/deadline-owned-reaping.md | 5 +++++`
    (2 files, 6 insertions, 1 deletion — the single deletion is the replaced S075 row line).
    `git diff -- corpus/SOURCES.md` shows only the S075 row's used-by cell changed.

- Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
  - Exit code: `0` (captured via `EXIT=$?`).
  - Last line: `souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`
  - Preceding lines are pre-existing `W04 ... duplicate url` warnings only; none reference the new
    edit (e.g. no S075 used-by/format error, no S332 issue).

## Findings

None. Both predicate legs pass on the working-tree bytes, the diff is scoped to the two routed
defect-2 changes, and the census validates clean (exit 0).

## Scratch / ownership

- Scratch dir `/fast/scratch/hyaku/souji-r100/ExecC2Attribution/` removed before yielding
  (`rm -rf -- /fast/scratch/hyaku/souji-r100/ExecC2Attribution/`, verified absent).
- Owned/report dir `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-100/w1/ExecC2Attribution/`
  contains no files (no reproducer artifacts needed; predicate outputs recorded above).
- No tools installed/updated; no git/jj mutation; no other paths touched.

Report: .ufo/waves/round-100/w1/ExecC2Attribution.md
