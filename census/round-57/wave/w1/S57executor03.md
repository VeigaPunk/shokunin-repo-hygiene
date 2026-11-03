# S57executor03 — C1 v6 inline kill-power

Verdict: ATTACK-FOUND (coverage gaps M4 and M5); AGREE on the routed all-findings repair. Axes: calibration and coverage. No frozen implementation, fixture, expected file, or lane configuration edited.

Read preregistration first. Every result below was re-derived this session using the frozen expected TSV, not copied from the pre-freeze receipts. All seven arms built and scored 36 fixture repositories apiece in this seat's scratch. Fixture builder verifies each repository's toplevel before configuration/commits. No lane git mutations, background jobs, delegation, installations, or external state changes.

## Mutation table

| Mutant | Exact edit | Killed by / result | Selftest rc | Exact observed summary |
|---|---|---|---:|---|
| M1 | Replace unclosed-inline `break` with `end_line = n` | F29-PROSE-COMMENT-MENTION only | 1 | `SELFTEST fail cases=36` |
| M2 | Change inline closer search stop from `j > n` to `j > i` | B4-INLINE-NBSP-OPENER; C4-INLINE-CLOSED-COMMENT | 1 | `SELFTEST fail cases=36` |
| M3 | Remove inline recognition, retaining v5 line-start-only block opening | B4-INLINE-NBSP-OPENER; C4-INLINE-CLOSED-COMMENT; no other rows change | 1 | `SELFTEST fail cases=36` |
| M4 | Change inline hidden range from `range(i, end_line + 1)` to `range(i, end_line)` | SURVIVED — coverage gap | 0 | `SELFTEST pass cases=36` |
| M5 | Remove the `after.startswith('>') or after.startswith('->')` special-case branch | SURVIVED — coverage gap | 0 | `SELFTEST pass cases=36` |

M3 interpretation: v5 defines `stripped = ln.rstrip()` and checks `indent <= 3 and stripped.startswith('<!--')`. V6 already uses the equivalent `indent <= 3 and ln.startswith('<!--')`; there is no changed block predicate to regress. The meaningful v5-opener-only regression therefore removes the new inline class. This is the precise tested edit, not a claim that v6 changed the block class. A textual-only substitution to the v5 block predicate would be equivalent, not a behavioral mutation.

M4 concerns the **inline** span's closer line only; block/fence behavior was unchanged.

Contrary to the assignment's anticipated M1 killers, C6 does **not** kill this precise no-closer-to-EOF mutant. Its existing same-line closer is still honored. Observed:

```text
SELFTEST-CASE C6-INLINE-SAME-LINE pass rc=0 want_rc=0 findings=- want_findings=-
```

## Exact failing SELFTEST-CASE lines

M1:

```text
SELFTEST-CASE F29-PROSE-COMMENT-MENTION fail rc=1 want_rc=0 findings=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE want_findings=-
```

M2:

```text
SELFTEST-CASE B4-INLINE-NBSP-OPENER fail rc=0 want_rc=1 findings=- want_findings=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE
SELFTEST-CASE C4-INLINE-CLOSED-COMMENT fail rc=0 want_rc=1 findings=- want_findings=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE
```

M3:

```text
SELFTEST-CASE B4-INLINE-NBSP-OPENER fail rc=0 want_rc=1 findings=- want_findings=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE
SELFTEST-CASE C4-INLINE-CLOSED-COMMENT fail rc=0 want_rc=1 findings=- want_findings=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE
```

## Routed-defect pair independently reproduced

This is a separate mutation from inline M1: remove only the secondary `finding('PAIR-FILING-HIDDEN', ...)` call. Leave the primary finding, counters, and exit behavior intact. Compare the same mutant using the first-finding-only comparator versus the frozen full-list comparator:

| Arm | Outcome | rc | Summary |
|---|---|---:|---|
| PAIR-first: `got_find[:1] == want_find[:1]` | SURVIVE (expected demonstration, not an additional frozen-suite gap) | 0 | `SELFTEST pass cases=36` |
| PAIR-all: `got_find == want_find` | Killed by F24-PAIR-HIDDEN-FILING | 1 | `SELFTEST fail cases=36` |

```text
SELFTEST-CASE F24-PAIR-HIDDEN-FILING pass rc=1 want_rc=1 findings=UNFILED-SOURCES-ANNOTATION want_findings=UNFILED-SOURCES-ANNOTATION,PAIR-FILING-HIDDEN
SELFTEST-CASE F24-PAIR-HIDDEN-FILING fail rc=1 want_rc=1 findings=UNFILED-SOURCES-ANNOTATION want_findings=UNFILED-SOURCES-ANNOTATION,PAIR-FILING-HIDDEN
```

These independently reproduce `records/m1-red-before.txt`: the old assertion misses the missing secondary emission, while the frozen all-findings assertion detects it.

## Commands and durable evidence

Executed foreground command:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57executor03/probe.py
```

The harness set `TMPDIR=/fast/scratch/hyaku/souji-r57/S57executor03` and ran each copied counter with absolute arguments:

```text
python3 -B <scratch>/<arm>/c1-counter.py --selftest --work <scratch>/work-<arm> --expected /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/records/c1-selftest-expected.tsv --builder-sha256 2b8b657b8d86541d4a6f38345cd8d67f1a520603a7cda08f0a5bc3038924633b --expected-sha256 538d902e2f65ddc26bc0c532f4f7de67f89c08020f69151563a982d923d8e105
```

Here `<scratch>` is the TMPDIR above and `<arm>` is M1–M5, PAIR-first, or PAIR-all. Every arm copied `fixtures/` and `records/` alongside its counter so HERE resolves locally. Builder and expected pins were enforced by each run.

Evidence retained under `.ufo/waves/round-57/w1/S57executor03/`:

- `probe.py`: exact runnable harness and mutation definitions.
- `M1.diff` through `M5.diff`, `PAIR-first.diff`, `PAIR-all.diff`: exact counter edits.
- Corresponding `.txt` files: complete stdout/stderr, full actual command, TMPDIR, and EXIT for each arm.
- `results.json`: arm return codes, every failing case, F24 observations, summaries, and mutant source SHA256 values.

Harness exit: 0; observed cleanup line: `SCRATCH_REMOVED=True`. Scratch copies and fixture repos were removed by `finally: shutil.rmtree(S)` before return. Only this advisory report and its exclusive evidence directory were written persistently.

## Risks, limits, and disposition

- M4 is a genuine coverage gap for excluding an inline closer line: none of the frozen expected rows detects that edit. A closer-line-sensitive filing would distinguish the behavior; not added because fixtures are frozen.
- M5 is a genuine coverage gap for deleting the self-closing-form special case: no frozen row kills it. Not repaired in this wave.
- C6 remains a same-line/no-over-hide control, but is not evidence of kill power against this particular M1 edit.
- No claim about HTML renderer correctness or real-lane measurement was tested here. These are mutation/selftest observations only.
- LSP unavailable: no LSP tool was exposed in this seat; inspection used scoped source reads/search. No symbol refactor needed.
- No installs or updates. No blockers. No additional parent gate is required to interpret these receipts; parent owns any integrated claim verification.

Self-evaluation (advisory, not a claim judgment): accuracy 4/5 (M3's requested wording is ambiguous; exact interpretation disclosed), completeness 5/5 (five mutants and both routed-defect arms exercised), clarity 4/5 (full receipt details are longer than the table), actionability 5/5 (exact diffs/commands and surviving gaps named), conciseness 4/5 (evidence repeated selectively for standalone readability); mean 4.4/5. Highest-impact improvement: define M3 as v5-opener-only explicitly in future tasks. Would the user agree? Expected yes on observed results; M3 interpretation remains openly bounded.
