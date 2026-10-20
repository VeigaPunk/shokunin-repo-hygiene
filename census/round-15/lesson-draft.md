# Round 15 lesson draft (LessonDraft seat, unintegrated)

Status: DRAFT for L1 integration. Not admitted. Not an author `[x]` mark. No QUALITY, SOURCES, LOG, SCORECARD or SHONEN edit is made by this file. Sources: source inspection of `corpus/lessons/round-14-verifier-spotcheck.md`, `corpus/lessons/round-14.md`, `corpus/QUALITY.md` (Q20/Q21 rows), and `tools/souji-census.sh` at the lane working tree read by this seat. No command, census run, fixture, selftest, gate, or probe was executed by this seat.

Baseline cited by the round-15 claims: `cc2168325768d5356a82c039dcdf787377c55784` (`census/round-15/claims.json`).

## Outside disagreement (round-14, reported verbatim)

The non-author closure `corpus/lessons/round-14-verifier-spotcheck.md` is the source of record. Its verdict is `Status: ok; admitted: false; verdict: rejected-harmed.` It admits C1 within declared-byte scope and rejects C2's net admission. Verbatim disagreement rows:

- Line 117: `| C2 as an axis improvement with no harm | ADMIT within tested cases; expose restrictions for closure | before/after census source, especially after 493–506, 710–712, 964, 973–995 | disagree with net admission | Namespace cases pass, but benign key values are also refused and can suppress the whole fleet output. |`
- Line 148: `| operability | harmed | C2 namespace protection improves, but key-only benign-config refusal contracts prior census support and aborts all rows |`
- Line 106: `The twelve committed namespace cases do not include a benign local-config preservation control.`
- Line 105–106: `[INFERENCE, not an executed fixture] an otherwise supported benign-config repository consequently changes from usable census to exit 2/no TSV. No deployment incidence was probed.`
- Line 160 (routed item 1): `repair benign-config support without weakening protected-namespace refusal. Begin with value/effect-aware treatment of already-neutralized hooks settings. Add paired baseline/changed benign-config controls and a mixed-fleet case showing a harmless local setting cannot suppress unaffected rows.`
- Line 161 (routed item 2): `Tested-case improvement and honest restrictions do not prove no harm to the previous supported domain.`
- Line 162 (routed item 3): `consistently describe the demonstrated C1 consumer as the actual attempt_reuse decision on synthetic records. The full migrated dispatch and positive real-evidence retention were not run.`
- Line 163 (routed item 4): `enforce the disclosed prohibition on mid-flight seat empirical probes. SafetyCredential/BoundaryAttack/SafetyCache reports are not acceptance evidence.`
- Line 164 (routed item 5): `known external-input commands require fresh observation when claimed as a new execution, not cache-based relabelling.`

Author verdicts being disputed (`corpus/lessons/round-14.md`, `## Final measured gate decisions` and `Author verdicts:`, lines 79, 110–111): C2 "ADMIT within the tested namespace cases" and "operability improved within declared cases". The closure's operability verdict is harmed; the author's is not accepted.

### Source reopened by this seat (inspection only, working tree)

- `tools/souji-census.sh:493–506` `guard_git_config`: key-name-only match. Line 503 lowercases keys; line 505 matches `*core.hookspath*` among other patterns; line 506 calls `protected_fail "git-config-unsupported"` regardless of value. Confirmed.
- `tools/souji-census.sh:710–712` `count_dirty`: the tool's own `git status` invocation passes `-c core.hooksPath=/dev/null`. Confirmed: the tool already neutralizes this key for its own status call.
- `tools/souji-census.sh:964` calls `guard_git_surface` inside `list_repos`; `:979` calls `list_repos "$root"`; `:991` prints `$HEADER`. Discovery precedes the header. Confirmed.
- `tools/souji-census.sh:160–163` `protected_fail`: `exit 2`. In `emit_census` (`:982–986`) an rc of 2 exits the whole run. Confirmed.

Consequence stated by the closure and consistent with this source read: one key-matched repository aborts the run before any row is printed. This is source-inferred; it is not an executed fixture here.

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| R15-M1 | operability: value-blind refusal of a benign local Git config key suppresses the whole fleet census | `tools/souji-census.sh:493–506` (key-name match at 505, refusal at 506); `:964`, `:979–991`, `:160–163`; `corpus/lessons/round-14-verifier-spotcheck.md` lines 104–106, 117, 148 | none in round-14: the 12 namespace cases contain no benign local-config control (spotcheck line 106) | Value/effect-aware handling of already-neutralized keys (`core.hooksPath`, which `:711` already overrides), with refusal retained for effect-bearing keys; paired benign-config controls and a mixed-fleet control. See Q22. |
| R15-M2 | calibration: a green namespace-only result was admitted as net no-harm to the previously supported surface | `corpus/lessons/round-14.md` Gate C2 row and `Author verdicts`; spotcheck lines 102, 117, 148 | the round-14 closure (non-author) rejected the net admission; the author's own gate did not | A no-harm or net-improvement admission needs independent paired preservation evidence for the previously supported surface, not only the newly protected cases. See Q22. |
| R15-M3 | wording: the C1 consumer demonstration was described more broadly than its executed scope | `corpus/lessons/round-14.md` line 89 (synthetic records through `attempt_reuse`; full migrated `run()`/`--retry-failed` not demonstrated); spotcheck line 162 | round-14 closure, routed item 3 | Each consumer claim names its input kind (synthetic or real) and its path; a synthetic decision is never described as a full dispatch. See Q23. |
| R15-M4 | process: seats executed empirical probes mid-flight despite the prohibition | `corpus/lessons/round-14.md` lines 120–126 (SafetyCredential, BoundaryAttack, SafetyCache); spotcheck line 163 | round-14 closure, routed item 4 | Seats perform no execution, probe, fixture or gate run; only the L1 acceptance run yields execution evidence; disclosed deviations are recorded and are not acceptance evidence. See Q23. |
| R15-M5 | label drift: an observation at an older revision was restated as a fresh execution at a later revision | spotcheck line 164 (routed item 5); the `48f8945` source-anchor observation vs. later revision | round-14 closure, routed item 5 | Keep the original measurement revision and label. A later revision's unexecuted source reading is labelled as inspection, not execution. See Q23. |

## Gate — candidate criteria for round 15 (final decisions bound to L1's measured evidence)

| candidate | draft decision | required before admission | limit |
|---|---|---|---|
| C1 operability repair of value-blind Git config refusal (R15-M1) | pending evidence; cannot be admitted on source reading | paired baseline/changed benign-config row, mixed-fleet row showing unaffected repositories still emitted, and protected-namespace rows still refused, all at committed revisions | effect-bearing keys (`include`, `includeIf`, `filter.*`, `core.attributesFile`, `core.excludesFile`, `core.alternateRefsCommand`, `promisor`, `extensions.partialClone`, `extensions.worktreeConfig`) stay refused unless value/effect-aware evidence proves neutralization; broader narrowing needs operator/canonical scope-change adjudication, not a no-harm admission |
| C2 calibration: independent preservation-evidence admission checker (R15-M2) | admit only if the checker itself rejects green-only, weakened or missing preservation evidence and its own paired red/green and namespace controls pass | checker rejects a fixture with only green outputs, with a weakened expected value, and with a missing benign control; accepts the paired set | checker is not a deletion or certification authority |
| No certification, deletion authority, or universal race-free claim | REJECT (unchanged) | none | — |

## Q22 — preserve supported configuration effects; no trade-off admission (draft criterion text for QUALITY, not written here)

A census change that refuses, narrows, or re-scopes a configuration the previous tool supported is admitted as no-harm only when committed paired baseline/changed controls show unchanged output for benign values of the same key or surface, and a mixed-fleet control shows that unaffected repositories are still emitted in the same run. Keys whose value can alter reads keep refusal unless value/effect-aware evidence shows neutralization. Any remaining narrowing is an explicit operator or canonical scope-change adjudication; it is never recorded as a no-trade improvement. Namespace-only green cases, authored capability rows, and disclosed restrictions do not satisfy this criterion.

- Test (required observables): paired baseline/changed run of the census fixture on synthetic repositories only, with (a) a benign-config row, (b) a mixed-fleet row, (c) a protected-namespace row; compare exit code and TSV row set per row; baseline must be red for the protection row and unchanged for the preservation rows.
- Applies to: census.
- Lesson pointer: `corpus/lessons/round-15.md` `## Mistakes` R15-M1, R15-M2.

## Q23 — real-consumer wording is synthetic-only unless observed; no in-flight empirical probes (draft text, not written here)

A capability or consumer claim names the input kind and the path executed. Synthetic records through a real decision function are described as synthetic-only consumer decisions. A full migrated dispatch on real evidence is claimed only after a committed real observation at a named revision. Seats perform no empirical probe in flight (no command execution, tool run, fixture run, or gate run); only L1's acceptance run produces execution evidence; any disclosed seat probe is recorded as a process deviation and is not acceptance evidence. Each observation keeps the revision and label at which it was measured; a later-revision source reading is labelled as inspection.

- Test (required observables): the round manifest records each claimed consumer as (path, input-kind synthetic|real, measured revision, exit status). A claim with input-kind synthetic may not be phrased as full dispatch. Seat reports list every deviation. The concrete checker is the round's admission-checker output, which L1 integrates; this draft does not assume its name or location.
- Applies to: round evidence, admission.
- Lesson pointer: `corpus/lessons/round-15.md` `## Mistakes` R15-M3, R15-M4, R15-M5.

## Notes for L1 integration

- Q22/Q23 numbering is provisional: `corpus/QUALITY.md` currently ends at Q21; no Q22/Q23 row exists at the baseline in this seat's read. L1 assigns final numbers.
- The R15 mistake IDs and the lesson file `corpus/lessons/round-15.md` are not created here.
- Verification not run by this seat: census selftest, `tests/fixtures/*`, ShellCheck, sources-census validate, any paired run. All remain L1 acceptance items.
- Tool installs or updates by this seat: none.
