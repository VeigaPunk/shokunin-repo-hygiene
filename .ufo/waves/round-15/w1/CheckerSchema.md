# CheckerSchema — round 15 C2 preservation-evidence checker (design-only)

Seat: `SoujiR15.CheckerSchema`. Axes: calibration (C2, lowest legacy axis 7), operability (guarded by C1 non-regression). Scope: schema, exit map, parsing/type rules, identity bindings, acceptance. Source inspection only.

## Status

- **Design-only.** `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` are absent (`git status`: only `.ufo/waves/round-15/`, `census/round-15/claims.json`, `census/operator-sweep-20261019/` untracked; `ls tools | grep -i preserv` empty). Nothing below is observed runtime behavior.
- No tests, probes, builds, or edits. No recorded command executed. No credential, auth, `~/.omp`, or operator-sweep path opened.
- Tooling: none installed or upgraded. `RULES.md` not needed since no install was performed.
- Owned output: this report only.

## Evidence read (exact pointers)

- `.ufo/waves/round-15/w1-spec.json` item `AdmissionChecker`: interface `--record FILE --root DIR`, `--selftest`; outer `0 clean / 1 failed honest evidence / 2 could-not-evaluate malformed-tampered`; pinned literal ids; no command execution.
- `corpus/lessons/round-14-verifier-spotcheck.md` L92–106 and L117, L148, L160: round-14 C2 rejected-harmed. Key-only `core.hooksPath` refusal (value-blind) aborts the whole census (exit 2, no TSV). Routed defect 1 requires paired baseline/changed benign-config controls plus a mixed-fleet case. Their absence is the gap this checker must close.
- `tools/souji-census.sh` L160–163 `protected_fail`: stderr is `souji-census: path-protected: <reason> (<label>: <path>)`, exit 2. L493–506 `guard_git_config`: lowercases all key names joined by newlines, then glob-matches substrings (`*core.hookspath*`, `*include.*`, …). Value-blind. L711 runs git with `-c core.hooksPath=/dev/null`, so the tool's own safe value trips its own guard.
- `tests/fixtures/r14-census-boundary.py` L46–57 `EXPECTED_IDS` (R14C2-01..12). `refusal_problems` (≈L480–502) asserts `FINDING in res.err` only, i.e. the substring `path-protected`, not the reason. No benign or mixed-fleet case exists. Output is `CASE\t<id>\tPASS|FAIL\t<free text>` plus `SUMMARY\ttotal=N\tfailed=M` (L716–728). `id-set` is checked only when `--case` is absent, and emits a pseudo-row `CASE\tid-set\tFAIL`. Baseline exemption at L712 for R14C2-07/08.
- `tools/souji-evidence-cache.py` L30–110 exit contract and record schema; L852–909 `_validate_record` (`isinstance(matched,bool)`, bool rejected as exit int); L764 `_reject_duplicate_keys`; L641 `_open_regular_beneath` (O_NOFOLLOW fd walk, fstat regular, nlink 1, same device); L1063 `_frozen_schema_check`; L1099 `evaluate_frozen` pinned snapshot. Reuse these patterns; do not reimplement looser ones.
- `SKILL.md` L127–140 registry table: no row yet for `souji-preservation-evidence`. Required row (see Acceptance).
- `census/round-14/verification.json`: runner-authored record fields `matched`, `expected_exit`, `exit_code`, inline `stdout`, `installed_sha256`. Checker must recompute, not trust, these.

## Findings (severity order)

**F1 critical — baseline semantics are underspecified; blanket "baseline must fail" is wrong.**
The spec says "baseline actual benign-control failures and changed green". Read literally, that is coherent only per case. Baseline = round-14 tool at `cc2168325768d5356a82c039dcdf787377c55784` (`claims.json`). That tool already contains the r14 namespace guard, so R14C2-01..12 are likely green on baseline. Only the benign and mixed-fleet controls are red there. The a31642d baseline (10/12 red) is not the r15 baseline. A checker requiring "baseline fails every case" would reject a correct record, and one that accepts any baseline failure would admit a non-discriminating control.
Acceptance: a per-case expectation table pinned as literals in the fixture.

**F2 critical — namespace 12/12 cannot prove the refusal reason.**
`refusal_problems` accepts any exit 2 with the substring `path-protected`. A tool refusing with the wrong reason (for example a benign-config refusal reported under a protected-namespace reason) passes those cases. The r14 fixture is a frozen input for r15 and cannot be edited to add a structured reason field. Disclose this as a residual limitation. The checker must not claim reason-specific namespace proof from R14C2-01..06/10/11.

**F3 critical — the benign-control arms must exist and be pinned.**
Required new literal IDs (names are proposals; values must be pinned in the fixture and agreed with `CheckerCases`):
- B1 local `core.hooksPath=/dev/null` repo, changed exit 0 with one census row.
- B2 other benign local keys (for example `core.autocrlf`, `user.name`), changed exit 0 with a row.
- M1 mixed fleet: one benign-config repo plus one normal repo, changed exit 0 with both rows; baseline exit 2 with zero rows (proves the abort).
- Baseline arm: B1, B2, M1 must show observed exit 2 with the finding `git-config-unsupported`.
Benign-control and mixed-fleet arms must also keep a protected-namespace refusal in the same run, so the repair cannot pass by disabling the guard.

**F4 critical — "actual" failure is not checkable from free text.**
The r14 CASE detail is free text (`exit=2 want 0`). A fabricated `FAIL` line is indistinguishable from an observed one. The r15 config fixture must emit structured observation fields per CASE, for example `observed_exit=<int>` and `observed_finding=<reason>`, matched by an exact grammar. The checker must require those for B1/B2/M1 baseline arms and reject detail that lacks them (exit 2). Without this, no checker can satisfy "baseline actual benign-control failures" against a record it cannot independently tie to the run.

**F5 high — strict CASE/SUMMARY grammar.**
- Split on `\n` exactly. Do not use `str.splitlines()` (splits on `\x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029`, enabling injected lines). Reject `\r`, NUL, and other C0 controls in stdout.
- Digits: `[0-9]` only, canonical (no `+`, sign, leading zeros, or whitespace). Python `\d` matches Unicode digits and must not be used.
- Exactly one `SUMMARY` line, and it is the final line. Absent, duplicated, or non-final → exit 2 (truncation or tampering).
- Parse each `CASE` row with `split('\t', 3)`. Status token exactly `PASS` or `FAIL`.
- `CASE\tid-set\t...` is not a case ID. Treat it as a failed pseudo-row, not a case; count it in neither the universe nor `total`.
- `SUMMARY.total` must equal the number of case rows, and `SUMMARY.failed` must equal the FAIL count. Mismatch → exit 2.

**F6 high — JSON types (bool-as-int, exit strings, floats, non-finite, duplicates).**
- `type(x) is int`; reject `bool` (Python `True == 1` and `isinstance(True, int)`). Applies to `exit_code`, `expected_exit`, counts, `stdout_bytes`.
- Exit values must be `int` in 0..255. Reject `"0"`, `0.0`, `null`.
- `json.loads(..., parse_constant=<raise>)` to reject `NaN`, `Infinity`, `-Infinity`. Default json accepts them.
- `object_pairs_hook=_reject_duplicate_keys` (pattern at L764).
- Catch `RecursionError` and `ValueError` → exit 2.
- Enforce `MAX_JSON_BYTES` (16 MiB pattern L283). Reject UTF-8 BOM and invalid UTF-8 → exit 2.
- Recompute `matched` from `exit_code` against the pinned expectation. A declared `matched` that disagrees → exit 2 (`verdict-false-pass` precedent, L899–908).

**F7 high — null and empty maps (vacuity).**
- `results: null`, `cases: null`, `stdout: null`, `case: null` → exit 2.
- `cases: {}` or `[]` → exit 2 (zero-case vacuity; the cache gate treats an empty map as unbound, L171).
- A record-declared expected id set shorter than the pinned universe → exit 1 (weakened, see F12). The record cannot narrow the universe; the checker ignores it except as a cross-check.
- Unknown case ID (not in the pinned universe) → exit 2.
- Duplicate case ID → exit 2.

**F8 high — truncated stdout.**
- Record must declare `stdout_bytes` (int) and `stdout_sha256` (64 lowercase hex). Checker recomputes both over the recorded stdout bytes. Mismatch → exit 2.
- `truncated: true` or any truthy non-bool → exit 2.
- Stdout length equal to a capture cap → exit 2 (cannot prove completeness).
- Missing final `SUMMARY` → exit 2 (F5).

**F9 high — identity bindings.**
- Fixture digest identical across baseline and changed arms, and equal to the digest measured under `--root`.
- Case-ID sequence identical across arms (stable identities).
- Installed tool digest measured by the checker under `--root` at `tools/souji-census.sh`; compare to the record's declared digest. Mismatch → exit 2 (tampered).
- Baseline digest pinned as a literal in the fixture. From r14 recorded evidence the r14 installed census digest is `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` (`census/round-14/verification.json`). The r15 baseline `cc21683` tool digest is **[INFERENCE]** equal to that: L1 must confirm with `git show cc2168325768d5356a82c039dcdf787377c55784:tools/souji-census.sh | sha256sum`.
- `measured_commit` and `baseline_commit` each 40 lowercase hex. `baseline_commit` must equal the pinned `cc21683…`; any other value → exit 2.
- Both arms must declare the same `measured_commit`, or the record is mixed → exit 2.

**F10 high — path safety.**
- All record paths are relative canonical POSIX keys (no leading `/`, no `..`, no `.`, no empty component, no backslash, no whitespace edge, no control chars). Absolute or non-canonical → exit 2.
- Resolve only through the r14 fd walk (`_open_regular_beneath`): O_NOFOLLOW per component, fstat regular, nlink 1, same device. Symlink or hardlink → exit 2.
- `--root` and every resolved path refused lexically first if inside `~/.omp`, the credential store, or `census/operator-sweep-20261019/` (protected-tree list pattern L407). The checker never opens the operator sweep.
- **Design decision required:** the baseline tool snapshot lives under `/var/tmp` (runner extracts it), outside `--root`. Options: (a) the runner copies baseline bytes into `--root/evidence/` before recording, and the checker only reads under root; (b) allow a single declared `/var/tmp` path with the same no-follow checks plus digest pin. Option (a) is preferred because it keeps containment total.

**F11 medium — outer exit map (honest, closed).**

| Exit | Meaning | Examples |
|---|---|---|
| 0 | Clean: all arms present, bound, exact universe, baseline discriminates per pinned table, changed passes | B1/B2/M1 baseline exit 2 + `git-config-unsupported`, changed exit 0; R14C2-01..12 changed 12/12 PASS |
| 1 | Well-formed, bound, honest evidence that fails admission | changed red on a pinned case; baseline does not reproduce benign refusal (non-discriminating); green-only (no baseline arm); namespace < 12/12; missing an expected ID in an otherwise valid record |
| 2 | Could-not-evaluate: malformed, tampered, unsafe, or internal | bad JSON/types/F5–F10 rules; digest mismatch; truncated; null/empty map; zero case; unknown or duplicate ID; unsafe path; internal exception (caught, reported `internal-error`) |

Argparse usage errors → 2. `--selftest` failure → 1 (r14 precedent, L1 selftest `return 0 if failures==0 else 1`). Selftest tooling must not emit exit 0 when any negative control is unverified.

**F12 medium — weakened and green-only detection (discriminating controls).**
- Green-only (record has only a changed arm, or baseline arm copied from changed) → 1.
- Baseline PASS on B1/B2/M1 → 1 (non-discriminating).
- Changed FAIL on any pinned case → 1.
- Expected universe edited in the record (declared IDs ≠ pinned) → 1 if the record is otherwise valid, 2 if the declared set is malformed.
- Fixture bytes changed between arms or from the pinned digest → 2 (tampered).

**F13 medium — selftest negative controls (each asserts exact exit and finding id).**
Minimum: valid pair → 0; green-only → 1; baseline-green-on-benign → 1; changed-red-on-benign → 1; namespace 11/12 → 1; missing B1 → 1; `exit_code: true` → 2; `exit_code: "0"` → 2; `exit_code: 0.0` → 2; `NaN` → 2; duplicate key → 2; `results: null` → 2; `cases: {}` → 2; unknown ID → 2; duplicate ID → 2; truncated (no SUMMARY) → 2; `\u2028` injected line → 2; Unicode digit in SUMMARY → 2; `../` and absolute path → 2; symlink record → 2; digest mismatch → 2; `id-set` pseudo-row → 2; `--record` missing → 2; oversized (>16 MiB) → 2. Each control must fail when its guard is removed (discriminating).

**F14 medium — registry and frozen pins.**
- `SKILL.md` table needs a row: name `souji-preservation-evidence`, kind gate, command `python3 tools/souji-preservation-evidence.py --root DIR --record PATH`, verdict map per F11, self-test `python3 tools/souji-preservation-evidence.py --selftest`, pinned literal ids in fixture, write scope isolated `/var/tmp`, owner souji. (Not in this seat's ownership; route to L1/ScorecardDraft.)
- Frozen expected input for the record: `tests/fixtures/r15-preservation-evidence/expected.json` pins each input file digest, mirroring `r14-cache-frozen/expected.json`.

**F15 limit — the checker validates declarations, not execution.**
It cannot prove the runs happened, since it must not execute recorded commands. It proves internal consistency, digest binding to measured bytes, and that the record cannot narrow the universe. The measured L1 run is the only execution evidence. Disclose this in the report and in SCORECARD prose. Do not describe the checker as certifying operability.

## Acceptance needed (exact)

1. Pinned literal universe: namespace `R14C2-01..12` plus `B1`, `B2`, `M1` (agreed IDs with `CheckerCases`), with a per-ID expectation table (baseline outcome, changed outcome, required structured fields).
2. Structured observation fields from the r15 config fixture (F4). Checker rejects detail lacking them for baseline benign arms.
3. Baseline digest and commit pinned: `cc2168325768d5356a82c039dcdf787377c55784`; tool digest verified by L1 with `git show`.
4. Parser and JSON rules F5/F6/F8 implemented and covered by F13 negative controls, each removable to show discrimination.
5. Exit map F11 implemented exactly; no path yields 0 unless every F9/F10 check passes.
6. SKILL.md registry row (F14).
7. L1 final acceptance: run checker `--selftest`, the r15 fixture on baseline and changed arms, and `shellcheck` only if shell changes. No run by this seat.

## Unrun checks and verification gaps

- No runtime check executed; all statements are source reads or design.
- `fcff8b05…` as cc21683 baseline digest is an inference from r14 recorded evidence. Not verified.
- Whether the r14 fixture's `path-protected` substring check can pass for a wrong reason is inferred from source (L480–502), not observed.
- Whether benign local keys (B2) are actually refused today is inferred from `guard_git_config` substring logic, not observed. The round-14 closure already states this as `[INFERENCE, not an executed fixture]`.

## Messages sent

- `SoujiR15.AdmissionChecker` (owner): schema summary, per-case table, parser/type rules, exit map, report path.
- `SoujiR15.CheckerCases`: structured observation requirement (F4) and namespace reason limitation (F2).

## No-query boundary disclosure

Violations of the operator no-query boundary by this seat, disclosed and not repeated:

1. Whole-lane recursive glob (first `_glob` call, root `/home/vgpnk/Projects/shokunin/souji-shokunin`, `hidden=true`, `gitignore=false`, limit 200). Its listing printed names under `census/operator-sweep-20261019/`. Names only; no file contents were opened.
2. Whole-lane recursive grep (`grep -rln -i 'preservation\|admission\|bool-as-int\|red/green\|paired' --include=* .`, run from the lane root). This necessarily traversed `census/operator-sweep-20261019/`. Matches were truncated by `head -50`, so whether any operator-sweep file matched is unknown; no matched content from that path was printed or used.
3. Directory listings `ls -la census` and `ls -la` on lane subdirectories, which show operator-sweep directory names.

Limitation: my conclusions do not rely on any operator-sweep content. Output used came from `tools/`, `tests/fixtures/`, `census/round-13..15` paths, `corpus/lessons/`, `SCORECARD.md`, `.ufo/waves/round-15/w1-spec.json`, and `census/round-15/claims.json`. No further whole-root or recursive queries were run after the operator reminder.
