# LessonDraft — round 15 scoped findings

Seat: SoujiR15.LessonDraft (leaf, source inspection only). Owned write: `census/round-15/lesson-draft.md` (created; it did not exist). No other shared write.

## Boundary disclosure (no-query reminder)

- Violation: one `_glob` call with path `/home/vgpnk/Projects/shokunin/souji-shokunin` (whole lane root, `gitignore: false`, `hidden: true`, `limit: 200`) enumerated filenames under `census/operator-sweep-20261019/`, including `results/kotodama-chunk-*.tsv|.err`, `.hold.json`, `stage-hold-delete.sh`, `second-check.py`, `quarantine-mtimes-t0.tsv`, `tmp-kept.tsv`, `tmp-removed.tsv`, `kagi-routing-*.txt`, `lore-scratch-verdicts.tsv`, `kotodama-children-sizes.tsv`. The call ran before the reminder; it is not repeated.
- Limitation: only the directory listing names were returned. No operator-sweep file was opened, read, copied, queried, edited, moved, staged or deleted. Neither the draft nor this report relies on any operator-sweep name or content.
- All later reads were explicit files (`corpus/lessons/*`, `corpus/QUALITY.md`, `SKILL.md`/`LOG.md` via grep, `tools/souji-census.sh` line ranges, `.ufo/waves/round-15/*.json`, `census/round-15/claims.json`). No runtime probe or test was run.

## Behavior

- Drafted the round-15 lesson candidates from the non-author round-14 closure `corpus/lessons/round-14-verifier-spotcheck.md`: five mistakes (R15-M1 to R15-M5), candidate Gate rows, and draft criterion text for Q22 (preserved supported configuration effects; no trade-off admission) and Q23 (synthetic-only real-consumer wording; no in-flight empirical probes).
- Verbatim outside disagreement is quoted with line numbers (spotcheck lines 102, 105–106, 117, 148, 160–164).
- Q22/Q23 numbering is provisional for L1.

## Gates

- Not run by this seat, by instruction: no census, selftest, fixture, gate, ShellCheck, sources-census validation, or paired run.
- Source inspection performed on `tools/souji-census.sh` (working tree read by this seat): `:493–506` key-name refusal (`:505` matches `*core.hookspath*`; `:506` refuses), `:710–712` tool's own status call forces `core.hooksPath=/dev/null`, `:964` guard call in `list_repos`, `:979–991` discovery precedes header, `:160–163` `protected_fail` exits 2. All consistent with the closure's cited lines.

## Touched surfaces

- `census/round-15/lesson-draft.md` (new, owned).
- `.ufo/waves/round-15/w1/LessonDraft.md` (this report).
- Not touched: QUALITY, SOURCES, LOG, SCORECARD, SHONEN, SKILL, sibling files, `census/operator-sweep-20261019/`, any credential or auth file, `~/.omp/agent/agent.db*`.

## Out of scope

- Admission, deletion or certification decisions; QUALITY row authoring; the round's C1 code repair; a real-consumer observation.

## Findings

1. Round-14 C2 was admitted as no-harm by the author while the non-author closure rejected net admission (spotcheck line 117). The author's `operability improved within declared cases` is not accepted (spotcheck line 148). Q22 addresses this.
2. Source-inspected: the key-only refusal at `tools/souji-census.sh:505–506` is value-blind; `:711` already neutralizes `core.hooksPath` for the tool's own status call, so a value/effect-aware repair is plausible. Not demonstrated by execution.
3. The round-14 consumer wording (`corpus/lessons/round-14.md` line 89) is synthetic-record scope. Q23 requires the input kind to be named.
4. The round-14 seats' mid-flight probes (`corpus/lessons/round-14.md` lines 120–126) are recorded as deviations and are not acceptance evidence. Q23 prohibits repetition.

## Artifact paths

- `census/round-15/lesson-draft.md`
- `.ufo/waves/round-15/w1/LessonDraft.md`

## Unrun checks for L1

- Census selftest and paired benign-config/mixed-fleet runs (C1 evidence).
- Checker red/green controls (C2 evidence).
- ShellCheck and `scripts/sources-census.sh validate` if any source row changes.
- Confirm final Q22/Q23 numbers and R15 IDs during integration.

## Tool installs or updates

None.
