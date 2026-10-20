# Round 15 — source-only mutation plan

## Axes and evidence boundary

- **Operability (C1):** preserve benign configured repositories and every unaffected mixed-fleet row, without losing the protected-namespace boundary.
- **Calibration (C2):** admit only complete, identity-bound paired preservation evidence; green-only evidence must not support a no-harm claim.
- Source inspection only. No mutant, fixture, checker, test, probe, build, or separate runtime was executed. No certification/deletion authority is claimed.
- Inspected source snapshots: `tools/souji-census.sh` (`EAEA`) and `tests/fixtures/r14-census-boundary.py` (`2C61`); claim definitions are `census/round-15/claims.json:3-13`.
- At inspection, inventory contained none of `tests/fixtures/r15-census-config.py`, `tools/souji-preservation-evidence.py`, `tests/fixtures/r15-preservation-evidence.py`, or `census/round-15/run-verification.py`. Their oracles below are **design-only acceptance requirements**, grounded in `.ufo/waves/round-15/w1-spec.json:19,28,37`, not claims about implemented checks. No future case ID or output is invented.

## Four prospective mutants

### M1 — reintroduce the value-blind hooks key ban

**Smallest behavior-bearing defect:** after the repair, make any `core.hooksPath` declaration take the unsupported-config refusal, irrespective of its value/effective override. The existing defect is already visible at `tools/souji-census.sh:493-507`, especially the `*core.hookspath*` alternative at line 505. Status already supplies `-c core.hooksPath=/dev/null` at lines 710-712.

**Expected detector — design-only:** the fixed hooks-preservation case in `tests/fixtures/r15-census-config.py --tool PATH`. Use a synthetic ordinary repository with `core.hooksPath=/dev/null` (or a harmless fixture-owned hooks directory); demand exit 0 and the complete expected seven-column census row, including fixture-controlled counts/flags. The hypothetical mutant takes the refusal instead, so that positive-case exit/row assertion must fail. A case requiring only absence of hook execution cannot detect this operability regression.

**Exact acceptance still needed:** a literal hooks-positive case ID in the fixture's fixed inventory; the same fixture bytes/expectations must expose the round-14 baseline `cc2168325768d5356a82c039dcdf787377c55784` as red and repaired bytes as green. Baseline-red must specifically include the benign hooks control, not merely an unrelated failed case. Since the currently inspected source already has the ban, it is not a pristine repaired control from which a mutation kill can be claimed.

**Output / verdict:** no runtime output; **NOT RUN — design-only, no killed/survived result**.

### M2 — strip the external-path namespace guard

**Smallest behavior-bearing defect:** in `guard_path`, replace `resolved=$(resolve_guarded "$2" 0 1) || exit 2` with `resolved=$2` (`tools/souji-census.sh:413-416`). Leave the internal-target guards intact. This single-line bypass affects both the initial root check at line 1527 and the census root resolution at line 975; deleting only the initial check would leave the later guard and would not exercise the intended defect.

**Exact existing detector:** `tests/fixtures/r14-census-boundary.py --tool PATH --case R14C2-01`. `case_01` passes the synthetic protected root to `--root` (lines 544-545). `refusal_problems` requires exit 2, `path-protected` on stderr, empty stdout, no canary, and no spy/strace access (lines 480-502). In particular, `trace_access(..., allow_root_stat=False, ...)` rejects even a stat of that root (lines 423-469, 497-499). The bypass permits the subsequent `[ -d "$root" ]` before refusal (`souji-census.sh:975-976`), so **[INFERENCE]** this access oracle will fail even if a later guard still refuses. The fixture reports a detected failure as `CASE\tR14C2-01\tFAIL\t...` and exits 1 (lines 716-729); these are source-defined output forms, not observed output.

**Full acceptance:** unchanged full fixture, literal `R14C2-01` through `R14C2-12`, all 12 passing on repaired pristine/restored bytes. Its positive controls must also stay green; root-refusal alone is not preservation evidence. Source lines 45-58 pin the inventory; lines 674, 722-729 enforce the default complete run. The fixture requires working strace and non-root execution (lines 678-679, 695-701); an unavailable detector is inconclusive, not a kill.

**Output / verdict:** no runtime output; **NOT RUN — source-backed expected kill, not an empirical kill**.

### M3 — drop an unaffected mixed-fleet row

**Smallest behavior-bearing defect:** remove the `+` from `rows+=("$row")`, yielding `rows=("$row")` (`tools/souji-census.sh:980-984`). This replaces the accumulated array for each successfully measured repository. The final emission at lines 991-994 then preserves only the last row. Single-repository cases remain insensitive to this defect.

**Expected detector — design-only:** the fixed mixed-fleet case in `tests/fixtures/r15-census-config.py --tool PATH`, containing at least one benign configured repository and one unaffected ordinary repository. Require exact equality of emitted repository identities to the independently fixed expected set, one row per identity, no duplicates/extras, and the expected per-repository fields. For a two-repository case, one surviving data row must fail even when exit remains 0, the TSV header is correct, and that surviving row is individually valid. Do not derive the expected repository set from returned rows.

**Exact acceptance still needed:** a pinned mixed-fleet case ID, explicit expected identities/cardinality, and field assertions in source. The preservation checker must require that case in both sides of the same fixed case set; omitting the mixed-fleet case from evidence must not be accepted. Existing r14 positive validation selects one named row and validates its fields (`r14-census-boundary.py:505-529`); it does not establish this new multi-repository property.

**Output / verdict:** no runtime output; **NOT RUN — design-only, no killed/survived result**.

### M4 — accept a green-only preservation record

**Smallest behavior-bearing defect — design-only:** remove the check that the baseline actually failed the designated benign-preservation controls, while leaving all structural, identity/digest, changed-green, and namespace checks intact. This isolates the paired-red requirement rather than relying on an unrelated malformed-record rejection. The implementation point cannot be named until `tools/souji-preservation-evidence.py` exists.

**Exact required external oracle:** invoke the checker with its contracted `--record FILE --root DIR` interface on a wholly synthetic, well-formed record whose baseline and changed outcomes are both green, with consistent stdout/exit/case identities, required digests, installed-tool binding, and namespace controls 12/12. The record must fail admission despite satisfying those other conditions. Under the contracted exit meanings (`w1-spec.json:28`), an honest complete record that fails the required baseline-red condition should return **1**, not 0; a missing/malformed/tampered baseline is a separate **2** control. A valid paired-red/green positive record must still return 0. These are required classifications, not observed implementation behavior.

**Exact acceptance still needed:** `tests/fixtures/r15-preservation-evidence.py` must self-invoke the checker on a pinned green-only negative case and assert rejection; mutant return 0 must make that detector fail. Do not let a negative record fail earlier because its digest, case inventory, capture, or namespace result is missing/mismatched. Also pin missing-baseline, weakened-case-set, and namespace-control rejection cases, so passing a single green-only control cannot substitute for the full C2 contract. Checker `--selftest` must reflect failed negative controls rather than merely parsing their records. Never execute command strings contained in records.

**Output / verdict:** no runtime output; **NOT RUN — design-only, no killed/survived result**.

## Unrun acceptance and restoration evidence

For L1 only, after the owning implementations land: freeze the detector bytes, literal case IDs, and expected outcomes; establish repaired pristine green; apply each defect separately in an isolated scratch copy; run the identical bounded detector on pristine/mutant/exactly restored bytes. A failing pristine control is **inconclusive**, even though the separate historical round-14 control is intentionally red. Count a kill only when the targeted behavioral assertion changes, not merely when a stale provenance digest rejects a mutant. Record each subject's actual digest truthfully without weakening binding checks. Missing-tool/setup/timeout failures are not kills. A surviving mutant is a coverage finding, never permission to relax the contract.

This seat wrote **only this report**. No source/scratch mutation was made, so restoration was unnecessary. Before/mutant/after SHA-256 values and runtime outputs were **not collected**; byte-equivalence is not asserted, including against concurrent owner changes. Read snapshot tags above are source references, not cryptographic restoration evidence. No tool installation or update was performed.

## Query-boundary disclosure

Before SoujiR15's explicit no-whole-root-query reminder, this seat made two overbroad discovery calls:

1. `read` with `path="/home/vgpnk/Projects/shokunin/souji-shokunin"`; the directory listing exposed the name/metadata of `census/operator-sweep-20261019/`, not its file contents.
2. `glob` with `path="/home/vgpnk/Projects/shokunin/souji-shokunin/**/AGENTS.md;/home/vgpnk/Projects/shokunin/souji-shokunin/*;/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-15/*"`, `hidden=true`, `gitignore=false`, `limit=120`. The recursive filename query could traverse the operator-sweep subtree; no sweep file appeared among returned matches. That lack of matches does **not** establish that its directory entries were unqueried.

No sweep file was explicitly opened, copied, edited, moved, staged, or deleted by this seat. No sweep content is used as evidence here. These discovery calls exceeded the clarified query boundary; they were not repeated. Subsequent source discovery was limited to explicit tool/fixture files and round-15 evidence paths. No runtime probe or test was run.
