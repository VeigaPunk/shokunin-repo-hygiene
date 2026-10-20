# ClaimSeparation — round 15 (souji-r15-w1): C1/C2 causal separability and calibration-lowest obligation

**Seat**: `SoujiR15.ClaimSeparation` (connector, leaf)
**Lane**: `/home/vgpnk/Projects/shokunin/souji-shokunin`
**Judged axes**: operability (C1), calibration (C2; lowest legacy score 7)
**Evidence class**: source and document inspection only. No tests, builds, linters, probes, or fixture runs. Read-only `sha256sum` of tool/fixture bytes. No credential store, `~/.omp/agent`, `census/operator-sweep-20261019/`, or other agents' output was opened. Tool installs or upgrades: none.

**Source state (decisive for the design-only label):** round-15 source has not landed. The installed bytes still match round 14:

| File | sha256 (observed now) | Round-14 recorded (`census/round-14/verification.json`) | Status |
|---|---|---|---|
| `tools/souji-census.sh` | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | same | unchanged; C1 repair absent |
| `tests/fixtures/r14-census-boundary.py` | `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2` | same | unchanged; no benign-config case |
| `tools/souji-evidence-cache.py` | `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6` | same | unchanged |
| `census/round-15/` | only `claims.json` present | — | no C2 checker file exists |

So the C1 repair and the C2 checker are **design-only** in this report. Acceptance requirements are stated below as falsifiable checks.

---

## 1. Axes named

- **Operability (C1).** Round 14's closure (`corpus/lessons/round-14-verifier-spotcheck.md:7,148`) judged operability **harmed**: key-name-only Git config refusals (`tools/souji-census.sh:493–506`) refuse benign repositories and abort the whole census. The namespace gain (baseline 2/12 → changed 12/12) is real but does not offset this. SCORECARD still shows operability 8, "improved r14 C2", and LOG says "normal controls preserved". That wording is contested, not settled.
- **Calibration (C2).** Lowest legacy axis (7, `SCORECARD.md:13`). The round-14 operability claim of "normal controls preserved" was not backed by a benign-config control. The C2 checker must reject that class of overclaim, and must not itself raise the score.

## 2. Causal separability of C1 and C2

### 2.1 Write surfaces are disjoint
- **C1 surface**: `tools/souji-census.sh` only. Relevant sites: `guard_git_config` 493–506 (refusal predicate), its call sites 581, 613, 628, 650, 665, `guard_git_surface` / `list_repos` 922–971 (discovery aborts), `emit_census` 973–995 (only if output semantics change).
- **C2 surface**: a new standalone checker and its own synthetic evidence fixtures. It must not import or execute `tools/souji-census.sh`.
- **Shared, read-only input**: `tests/fixtures/r14-census-boundary.py` (namespace fence). Its digest must stay pinned, or any change must come with fresh paired red/green evidence.

Substrate separation holds. The verdicts are not separable by default, though, so the checker must be graded independently of C1 outcomes (section 4).

### 2.2 Coupling risks that must be closed
- **R-a, self-validation circularity.** If the checker reads its expected case-ID tuple and digests from the same fixture it judges (`EXPECTED_IDS` at `r14-census-boundary.py:45–58`, `BASELINE_SHA` at `:61`), a C1 edit to the fixture can rewrite the expectations the checker tests. The checker must pin the expected IDs, the fixture digest (`e6a984b1…`), and the tool digests in its own file.
- **R-b, weakening through the fixture.** C1 can get benign preservation by relaxing refusals that the namespace fixture expects. The checker must treat any fixture digest change as "weakened or unpaired" unless a new red arm is attached.
- **R-c, `path-protected` vs. `git-config-unsupported`.** The namespace fixture only checks `FINDING = "path-protected"` (`r14-census-boundary.py:43`, `refusal_problems`). Benign-config refusals emit `git-config-unsupported` (`tools/souji-census.sh:506`), which that fixture never looks at. **The current fixture cannot fail on a benign-config regression, with or without C1.** That blind spot is the core calibration gap.

### 2.3 Fixture coverage confirmed
- Repos built by `build_world` (cases 07, 08, 09, 12 and the others) contain no `core.hooksPath`, `core.excludesFile`, `core.attributesFile`, `include.*`, or `filter.*` keys. The only local config written is the bare `GD/config` (`r14-census-boundary.py:221–223`). [grep-verified: no hooksPath/include/filter in the fixture]
- Positive controls are R14C2-07 (`SAFE_FLEET`), R14C2-08 (`SCRATCH_FLEET`), and R14C2-12 (`SYMLINK_FLEET`). None of them is a benign-config control. On the baseline arm, 07 and 08 are exempt from the access rule (`:710–715`).
- The fixture's id-set check runs only when no `--case` filter is given (`:722–727`). A partial run cannot prove the full set.

## 3. C1 repair: scope, safe shape, hazards

### 3.1 Current behavior (source-verified)
- `guard_git_config` (`:493–506`) reads **key names only** (`git config --file "$cfg" --no-includes --name-only --list`, `:500`). It lowercases the newline-joined list and matches it against substring globs. It refuses on `core.hookspath`, `core.attributesfile`, `core.excludesfile` regardless of value (`:505`).
- The refusal calls `protected_fail` → exit 2 (`:160–164`). The guard runs during discovery (`list_repos` → `guard_git_surface`, `:964`), before the header is printed (`emit_census` `:979` before `:991`). **One benign repo with a local hooksPath aborts the entire census with no TSV.** Source-verified. Deployment incidence is [INFERENCE], not probed.

### 3.2 Neutralization audit (source-verified; per-command check is to-verify)
- The status call at `:710–712` already overrides `core.fsmonitor=false`, `core.hooksPath=/dev/null`, `core.excludesFile=/dev/null`, `core.attributesFile=/dev/null`. Those keys are therefore **already neutralized for status**, so their local values cannot influence the tool's status output. This is the "already-neutralized" class named in the round-14 routed defect (`round-14-verifier-spotcheck.md:160`).
- Other git calls do not carry those overrides: `worktree list` (`:688`, `:836`), `for-each-ref` (`:694`), `rev-list` (`:698`, `:702`), `rev-parse` (`:859`). None of them reads excludes or attributes. Read-only commands do not run hooks. [INFERENCE, to-verify: per-command audit of every git invocation before the value-aware change lands.]

### 3.3 Keys that must stay refused (fail-closed)
- **`include.*` / `includeif.*`**: the census git calls do not pass `--no-includes`, so git reads included files. Relaxing this without `guard_target` on the resolved include path reopens R14-M3 (`round-14.md:11`). Keep refused unless the include target is resolved and guarded first.
- **`filter.*.clean|smudge|process`**: `status` runs configured clean filters on tracked content, and the tool does not override them. Keep refused.
- **`core.alternateRefsCommand`, `remote.*.promisor`, `extensions.partialClone`, `extensions.worktreeConfig`**: no override exists. Keep refused.
- **`core.worktree`**: already boundary-checked at `:511–520`. Keep that behavior.

### 3.4 Value-aware repair requirements (C1)
1. For `core.hookspath`, `core.excludesfile`, and `core.attributesfile` only, read the **value** (`git config --file "$cfg" --no-includes --get-all …`, inside the gitdir) and run `guard_target` / `protected_reason_input` on it **before any use**. A protected value must still exit 2 with `path-protected`, not a success and not `git-config-unsupported`. This keeps the namespace fence whole.
2. A non-protected value of those three keys is admitted only because the status invocation overrides it. Any new read path must not follow a path it did not guard.
3. Keep all other listed keys on the refuse list in 3.3. Refusal stays fail-closed for any unparseable or ambiguous value.
4. Mixed fleet: a benign repo must not abort unaffected rows. This is a **design decision with output-contract impact**. Options:
   - (a) keep global exit 2 for config refusals: fails the mixed-fleet requirement;
   - (b) per-repo exclusion with a stderr finding and a nonzero exit at the end, so a partial census is never consumed as clean;
   - (c) a new per-row verdict flag: changes the 7-column TSV, which breaks the byte-identical legacy requirement (`SKILL.md:208–216`, selftest).
   Recommendation: keep protected-path refusals as global exit 2 (unchanged namespace fence), and move only unsupported-config to per-repo handling. **Option (b) or (c) changes the output contract; the round-14 lesson requires explicit operator or canonical adjudication for scope changes (`round-14-verifier-spotcheck.md:160`).** [INFERENCE on which option is adopted; the choice is not made in this report.]

## 4. C2 checker: independent preservation-evidence admission

### 4.1 Required behavior (acceptance)
The checker reads a preservation-evidence record and returns admit/reject for the **no-harm** claim only. It must not produce a score, certification, or deletion authority.

Inputs it pins itself (sha256 in its own file):
- tool digests for the baseline (`6a000c59…`, `a31642d`) and the changed arm (the repaired digest, determined only after C1 lands);
- fixture digest `e6a984b1…` or its successor, and the 12-ID tuple;
- benign-control and mixed-fleet control expectations (new fixture, separate digest).

Admission requires **all** of:
1. **Paired red arm.** Baseline arm exits **1** with `SUMMARY … failed>0` and per-case `CASE` lines containing access or contract evidence. An exit 2 (setup/could-not-evaluate) is not red proof. This matches the round-14 rule (`LOG.md:656–662`, attempt-1 exit-2 fixture setup not counted).
2. **Green arm.** Changed arm exits 0 with every expected ID PASS, same fixture digest as the red arm.
3. **Namespace controls.** R14C2-07, 08, and 12 PASS on the changed arm and are present in both arms.
4. **Benign-config controls (new).** At least one repo with a local `core.hooksPath` (and one each with `core.excludesFile` / `core.attributesFile`) whose changed-arm row is emitted and equals the oracle row, plus a mixed fleet in which one benign repo sits beside unaffected rows and all unaffected rows still emit. Baseline arm is recorded for contrast.
5. **Non-weakening.** Changed-arm expected exit and finding per protected case are unchanged from the pinned tuple. Fixture digest is unchanged, or a new paired red arm is attached.
6. **Recomputed verdict.** The checker re-derives pass/fail from raw `CASE`/`SUMMARY` lines. It does not trust a stored `matched` or `status` field.

Reject classes (nonzero exit, stable finding IDs):
- `green-only`: changed arm without a paired red arm.
- `red-not-red`: baseline failure caused by exit 2 or missing access evidence.
- `weakened`: changed-arm expectation or fixture digest differs from the pinned tuple, without a new red arm.
- `benign-control-missing`: no benign-config arm (blocks any no-harm claim).
- `mixed-fleet-missing`: unaffected rows suppressed or absent.
- `self-graded`: verdict fields supplied by the evidence rather than recomputed.

### 4.2 Independence from C1 (the core calibration requirement)
The checker must fail **without any C1 repair being wrong**, and it must fail **when C1 is absent**. Required replays, all on synthetic or historical bytes, read-only:

| Replay | Input | Required checker result | Shows |
|---|---|---|---|
| **R1, historical falsifier** | `census/round-14/verification.json` (measured 552cae4; baseline 2/12, changed 12/12, no benign arm) | **REJECT** `benign-control-missing` for no-harm admission | Reproduces the outside closure's verdict independent of any C1 fix. |
| R2 green-only | changed-arm record only, all PASS | REJECT `green-only` | Green alone is insufficient. |
| R3 weakened | changed arm with one protected expectation edited, or fixture digest changed without a red arm | REJECT `weakened` | Expectations cannot be quietly changed. |
| R4 setup-as-red | baseline arm exit 2 with `could-not-evaluate` text | REJECT `red-not-red` | Setup failure cannot stand in for red. |
| R5 C1 absent | round-14 tool digest as "changed" plus a synthetic benign arm showing exit 2 | REJECT `benign-control-missing` and/or `mixed-fleet-missing` | Checker fails when the repair is absent, even with all namespace cases green. |
| R6 self-admission | repaired tool with no benign or mixed-fleet arm | REJECT | The C1 author cannot admit C1 by namespace green alone. |
| P1 positive control | synthetic paired record meeting all six conditions | ADMIT (no-harm, bounded to fixture cases) | Admission path exists and is not vacuous. |

R1 is the decisive calibration test: the checker must reproduce the round-14 closure's rejection from committed bytes. If it admits R1, the checker is not calibrated.

### 4.3 Calibration-lowest obligation
- Calibration stays at **7, delta 0**. The checker's admit/reject output is gate evidence (like `souji-cert-evidence.py`), not a score. Any SCORECARD change needs outside closure.
- The round-14 wording "normal controls preserved" (SCORECARD operability row; LOG round-14 entry) must not be repeated. Until a paired benign arm passes, operability stays **contested**, not 8 "improved". [Contradiction stated explicitly: SCORECARD operability 8 vs. closure "harmed". Do not smooth it.]
- The checker must describe itself as bounded to its fixture cases: no historical execution proof, no deletion authority, no universal race-free or hardlink/mount coverage (matches `SKILL.md:195–216`).
- Self-tests write only under `/var/tmp`, use synthetic bytes, and never read the real store.

## 5. Exact acceptance needed (for L1 and for the seats that implement)

1. **C1 source**: `guard_git_config` value-aware for `hookspath`/`excludesfile`/`attributesfile` only; other listed keys still refused; protected values → `path-protected` exit 2 before any access; no change to `:511–520`.
2. **C1 audit**: per-command statement for every git call in section 3.2, recorded as observed by source inspection, labelled `to-verify` until executed.
3. **C1 mixed fleet**: a decided option from 3.4(4), with the output contract stated. If the TSV or exit codes change, adjudication is required before admission.
4. **C1 fixture**: benign-config cases added to a **separate** fixture (not `r14-census-boundary.py`); namespace fixture digest unchanged or re-paired with fresh red evidence.
5. **C2 checker**: standalone file; pins its own tuple and digests; recomputes verdicts; reject classes in 4.1; replays R1–R6 and P1 in its self-test using synthetic bytes under `/var/tmp`.
6. **Non-author closure**: R1 result must be reproduced by a non-author reader before any calibration movement.
7. **Documentation**: SCORECARD/LOG wording for operability must say "contested" until items 1–4 pass in measured evidence.

## 6. Risks and contradictions (explicit)

- **Operability: SCORECARD 8 vs. round-14 closure "harmed".** Both are on record. Not reconcilable by source alone; the benign arm decides it.
- **Namespace fence cannot see benign regressions.** Demonstrated by source (`:43`, `:506`, `refusal_problems`). This is the calibration gap, independent of C1.
- **Mixed-fleet fix changes output contract.** Per-repo handling is required by the mixed-fleet requirement, but it changes TSV or exit behavior. Needs adjudication, not silent change.
- **Neutralized-key relaxation depends on the status override staying intact.** If a future change removes `-c core.hooksPath=/dev/null` (`:711`), the relaxation becomes unsafe. The checker should pin the status invocation text, or the benign arm should fail when that override is removed.
- **Round-14 closure's R14-M4-class risk (fallthrough).** Gate-level green did not prove caller enforcement in round 14. The same risk applies here: a value-aware guard that returns early on success could skip the protected-value check. The R5/R6 replays and the protected-value test in 3.4(1) address this.

## 7. Unrun checks (for L1 to execute after all seats land)

- `sha256sum` on every file named in the acceptance list, against the pinned tuple.
- `bash -n tools/souji-census.sh` and `shellcheck -S warning tools/souji-census.sh`.
- `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (legacy 38/38 expected).
- `TMPDIR=/var/tmp python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-census.baseline.sh` (expect exit 1) and `--tool tools/souji-census.sh` (expect exit 0), unchanged.
- The new benign and mixed-fleet fixture, paired red/green, with the baseline arm required to show benign refusal (exit 2) or per-row loss.
- `python3 -m py_compile` and `--selftest` for the C2 checker; replays R1–R6 and P1 from section 4.2.
- R1 replay against `census/round-14/verification.json` (read-only).

## 8. Files consulted (read-only)

`.ufo/waves/round-15/w1-spec.json` (ClaimSeparation entry); `.ufo/waves/round-15/w1-dispatch.json`; `census/round-15/claims.json`; `AGENTS.md`; `SKILL.md:182–216`; `SCORECARD.md:9–47`; `LOG.md:618–724` (round-14 entries); `corpus/lessons/round-14.md`; `corpus/lessons/round-14-verifier-spotcheck.md`; `tools/souji-census.sh` (lines 2–103, 155–165, 272–470, 493–520, 552–580, 610–670, 687–720, 836–859, 921–996, 1009–1022, 1144–1200, 1530–1539); `tests/fixtures/r14-census-boundary.py` (lines 1–63, 124–230, 320–420, 544–735); `census/round-14/verification.json` (header and `checks`/`consumer` only). Not opened: `census/operator-sweep-20261019/`, `~/.omp/agent`, any credential or auth file.

[Checksums and line references are source inspection only; no run was executed by this seat.]

## 9. Boundary disclosure (correction to section 8)

- Violation, disclosed: one recursive glob `{tools,tests,census,corpus}/**/*` was run during source discovery. Its output listed file **names** under `census/`, including entries under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `classification-final.json`, `census-before.tsv`). No file content under that directory was read, copied, queried, or modified. Section 8's statement that the operator sweep was "not opened" is accurate for content only; the names were enumerated.
- Other calls: one non-recursive root listing `souji-shokunin/*`; one recursive glob limited to `.ufo/**/*`; explicit-path reads and greps only; one `sha256sum` over four named files plus `ls` of `tests/fixtures` and `.ufo/waves/round-15/w1`. No git commands, no runtime probes, no tests, no fixture runs.
- No further queries of `census/` or any recursive lane-root search will be made by this seat. Findings in sections 1–7 rely only on explicit tool, fixture, census round-14/15 and corpus paths; they are unaffected by the enumerated names.
