# AdmissionRules — round 15, wave 1

Seat: `SoujiR15.AdmissionRules` (connector, leaf). Axes: operability, calibration.
Status: **design-only.** The checker and its fixtures do not exist in the lane at read time:
`tools/souji-preservation-evidence.py`, `tests/fixtures/r15-preservation-evidence.py`,
`tests/fixtures/r15-census-config.py` and `tests/fixtures/r15-preservation-frozen/` are absent
(glob, 2026-10-20). Findings below grade the contract (`w1-dispatch.json:692`, `:686`) and the
canonical rules, not an implementation.

Execution: source inspection only. Read-only `git rev-parse`, `cat-file`, `show | sha256sum`,
`status`, `log` on committed bytes. No tests, probes, builds, or recorded commands run.
Tool installs or updates: **none** (`~/.omp/agent/RULES.md` read; nothing needed).

## 1. Canonical rules cross-checked

Fleet-root `PROTOCOL.md` (`/home/vgpnk/Projects/shokunin/PROTOCOL.md`):

- Verdict map: `0` clean, `1` failed, any other code is `could-not-evaluate` unless declared. L380-384.
- Self-test: isolated fixtures, asserts exit code and a stable finding-id, expected values committed in the owning repo and independent of recomputation. L385-389.
- Two evidences: a gate whose verdict depends on a mutable artifact also ships a **frozen run** over a committed snapshot. `expected.json` **MUST pin the sha256 of every input**. Mismatch is `snapshot_tampered` (exit 2). An unpinned baseline is `unpinned (legacy)`. L390-397.
- A verdict names the revision it grades. L393-394.
- Registry row: eight fields (name, `gate|probe`, entry, verdict map, self-test, pinned path, write scope, owner), in the lane `SKILL.md`. L398-406. Closure grades no gate conformant without the row. L418-421.
- Evidence pointers must resolve at closure, not under `/tmp` or `/dev/shm`. L356-358. Claimed is not re-executed. L361-362. Drift pins count only if persisted in the repo. L370-373.

`PROTOCOL-APPENDIX.md`:

- L44, History pin: a regenerated pin that blesses an edit must die on a commit anchor (`history_pin_unanchored`).
- L45, Frozen inputs: a round-12 `expected.json` pinned only part of the input set, so an edited manifest still read `match`. Every input digest must be pinned.

`corpus/QUALITY.md` (Round 15 criteria):

- Q4 (L28): `/var/tmp` only, with trap.
- Q17 (L41): claimed fixtures resolve to contained regular files at the measured revision.
- Q22 (L56): namespace protection and preservation are separate obligations. A **declared-evidence checker must reject missing, green-only, mismatched or weakened paired controls**. It does not authenticate executions.
- Q23 (L57), Q24 (L58): wording and seat-probe rules.

Round-15 grounding: `corpus/lessons/round-15.md` L9 (R15-M1) and L15 (Gate: "C2 only with actual self-invocation negative controls and pinned frozen evidence"). The file is **untracked** (`git status`: `?? corpus/lessons/round-15.md`). Under PROTOCOL L356-358 it is not evidence until committed, so L1 must commit it before any closure cites it.

Round-14 outside closure (`corpus/lessons/round-14-verifier-spotcheck.md`):

- L104-106: the benign `core.hooksPath` refusal is key-only and aborts the whole census. The twelve namespace cases contain **no benign local-config control**.
- L160: routed defect 1 requires paired baseline/changed benign-config controls and a mixed-fleet case.

## 2. Existing templates to mirror, and where they are weak

| Template | What it does right | Weakness to avoid |
|---|---|---|
| `tests/fixtures/r14-census-boundary.py` | Literal `EXPECTED_IDS` L45-58; baseline identified by digest `BASELINE_SHA` L61, L703-705; red cases must show observed access, L711-715; full id-set check L722-726 | L722 is `if not args.case and ...`: a `--case` subset run can exit 0 with no id-set check. The checker must refuse partial selection for exit 0. `BASELINE_SHA` is `6a000c59` (a31642d), **not** the r15 harm baseline (see F2). |
| `tools/souji-evidence-cache.py` frozen mode | Pins each listed file (`evaluate_frozen` L1099-1204); rejects unknown `expected.json` keys (`_frozen_schema_check` L1063-1096); `frozen-incomplete` for unpinned dependencies L1180-1188 | No residue check: `evaluate_frozen` never enumerates the snapshot directory, so unlisted files are invisible. `expected.json` is self-trust (docstring L199-201: "not self-pinned"). Pins no `measured_commit` and no tool digest. |
| `tools/souji-cert-evidence.py` frozen mode | `_frozen_findings` L789-805; `frozen-incomplete` for any reachable snapshot input not in `expected.json` L913-934; selftest tamper cases L1453-1465 | Same self-trust note (L129-130). Residue not checked in the parts read. |
| `tests/fixtures/r14-cache-frozen/expected.json` | Two pins (L3-4) | Pins are not anchored to a commit. |

Baseline rule already in the census verification plan, which the checker should reuse verbatim: exit 1 on the baseline arm is `expected_red`. Exit 2 on the baseline arm is `could-not-evaluate`, not red (`census/round-14/verification-plan.json` L83). The round-14 closure says the same thing: setup exit 2 is not baseline-red proof (`corpus/lessons/round-14.md` L51-53).

## 3. Findings

**F1 (HIGH, calibration). Green-only and wrong-reason red are not rejected by anything specified.**
- The harm red arm for the benign config is the round-14 installed census. Its refusal is `protected_fail "git-config-unsupported"`, which writes `souji-census: path-protected: git-config-unsupported (<label>: <path>)` to stderr and exits 2 (`tools/souji-census.sh` L160-163, L505-506).
- A red arm must match **exit 2 + stderr regex `^souji-census: path-protected: git-config-unsupported `** on the **named benign case**. Exit 2 alone is not sufficient, and a missing or broken arm must not count as red.
- A green-only record must fail. Required behaviour: no baseline arm, or baseline exit 0 on the benign control, is `could-not-evaluate` (exit 2). Do not map it to clean.

**F2 (HIGH, calibration). Two baselines exist, and the r14 fixture pins the wrong one for C1.**
- r14 namespace red baseline: a31642d, census sha `6a000c59…` (`BASELINE_SHA`, r14 fixture L61). Keep as history.
- r15 harm red baseline: cc2168 (`census/round-15/claims.json` L3). Its `tools/souji-census.sh` blob sha256 is `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` (`git show cc2168…:tools/souji-census.sh | sha256sum`). HEAD is identical.
- Consequence: the r14 fixture's `is_baseline` check (L703) does not recognize `fcff8b05`. The checker's baseline literal must be `fcff8b05…`, pinned separately. Do not reuse `BASELINE_SHA`.
- Other verified digests (HEAD): `tests/fixtures/r14-census-boundary.py` `e6a984b1…`; `tests/fixtures/r14-evidence-cache.py` `95b371ab…`.

**F3 (HIGH, calibration). The dispatched interface has no frozen mode.**
- `w1-dispatch.json:692` specifies `--record FILE --root DIR` and `--selftest` only. PROTOCOL L390-397 makes a verdict over a mutable record a frozen-run obligation. The checker's verdict depends on a record, raw captures and tool bytes, so it is mutable.
- Required: `--frozen DIR` that verifies every `expected.json` pin **before** evaluation, mirroring `souji-evidence-cache.py` `--frozen`.

**F4 (HIGH, calibration). A declared record cannot prove a red run, so raw captures must be re-derived.**
- Q22 says the checker "does not authenticate executions". Taken alone, a hand-edited record with `"verdict": "red"` or parsed fields can flip the outcome.
- Required: the record references **raw per-case stdout and stderr files** for each arm. Each file is sha256-pinned in `expected.json`. The checker recomputes exit code, finding line, row set, and dirty values from those bytes. It never trusts the record's own parsed fields.
- This is the Q20 rule: "digests must be captured with the original observation, never manufactured" (`corpus/QUALITY.md` L49).

**F5 (HIGH, calibration). The expected universe must be literal in the checker, not read from the record.**
- The record can declare its own cases, so a weakened record can shrink the universe. The checker needs a literal case-id tuple, exact expected exit and finding per case, and a duplicate/unknown/zero-case rejection. This is the `FixtureOracles`/`CheckerCases` intent.
- Anti-self-blessing: `expected.json` is the only trust anchor in every existing gate. The checker source must also carry the sha256 of `expected.json` as a literal, so that editing a verdict or a pin changes a reviewed line of source. Follow PROTOCOL-APPENDIX L44 (`pinned_at_commit` names a commit that changed only `expected.json`).

**F6 (MEDIUM, calibration). Residue is unchecked.**
- Neither frozen mode enumerates the snapshot directory (evidence-cache `evaluate_frozen` L1099-1204; cert-evidence reachable-input check L913-934 only). An unlisted raw-capture file or a swapped case file is invisible.
- The residue rule exists only as a proposal (`.ufo/waves/round-14/w1/ProtocolEvidence.md` L110). Require: any file under the snapshot not in `expected.json` `files` is `snapshot_tampered`, exit 2.

**F7 (MEDIUM, operability). Partial selection can go green.**
- `r14-census-boundary.py` L722: the id-set check is skipped when `--case` is used. Apply the same pattern to the r15 fixture and it becomes a green subset gate.
- Required: no `--case` filter in the checker or the r15 fixture for an exit-0 path. A subset invocation is exit 2 usage.

**F8 (HIGH, operability). Freeze timing and the drift rule.**
- The changed-arm `tools/souji-census.sh` does not exist until `ConfigRepair` lands. The frozen pin for that arm can only be written after the final commit. Any later byte change makes it stale.
- Required: `expected.json` pins `measured_commit` (40 hex) and the candidate sha256. Drift rule: a digest change without re-derivation is `could-not-evaluate`, never pass (same as `census/round-14/verification-plan.json` L82, L156, and the round-14 quality proposal L251).
- Order: L1 freezes last, after all seats land. Frozen expectation must be generated from the committed bytes at the pinned commit.

**F9 (MEDIUM, operability). Mixed-fleet control must not accept header-only success.**
- `emit_census` runs discovery (L973-975) before printing the header. A zero-row output with a header is a plausible false green.
- Changed-arm pass requires: exit 0, row set equal to the pinned repo set, and pinned dirty values for dirty repos. Zero rows is a failure.
- Baseline: exit 2, no TSV rows for the whole census. This matches the round-14 closure L104-106.

**F10 (MEDIUM, operability). Registry row shape and write scope.**
- The lane `SKILL.md` table (L127-140) holds all rows. Add two: the checker gate and the external fixture gate, like `r14-census-boundary` (L140).
- Pinned path: `tests/fixtures/r15-preservation-frozen/expected.json`. Write scope: `tests/fixtures/r15-*`, `tools/souji-preservation-evidence.py`, isolated `/var/tmp`. Owner: souji.
- Verdict map for the checker (recommended, to be declared in the row):
  - `0` clean: every paired control discriminates and the changed arm meets the namespace and mixed-fleet expectations.
  - `1` failed: honest evidence in which the changed arm fails a control, or a namespace control regresses.
  - `2` could-not-evaluate: missing or green-only arm, non-discriminating baseline, wrong-reason red, malformed input, tampered pin, unlisted file, partial case set, zero cases, duplicate or unknown ids, JSON type confusion (bool-as-int, string exit), path outside root or through a symlink.
- Non-discriminating baseline (benign control green on baseline): exit 2, not 1. A green baseline means the control proves nothing, so it cannot grade the repair.

**F11 (MEDIUM, operability). Pointers must be committed.**
- `corpus/lessons/round-15.md` is untracked and `corpus/QUALITY.md` is modified (`git status`). The Q22-Q24 rows and the lesson are not closure evidence until committed. L1 commits them with the round.

**F12 (LOW, calibration). A stale round-15 frozen reference.**
- `.ufo/waves/round-13/w1/ReviewGateStandard.md` L83 proposes an `expected.json` shaped after `.ufo/waves/round-15/frozen/r15-pre-003400/expected.json`. That directory is absent, and no other file references it. Do not treat it as a pin.

## 4. Frozen expectation needs (exact)

`tests/fixtures/r15-preservation-frozen/expected.json`, schema `souji-preservation-evidence-expected-v1`. Reject unknown keys, as `souji-evidence-cache.py` already does.

Required keys:
- `record`: path to the declared paired-evidence JSON (pinned).
- `verdict`: `clean` | `failed` | `could-not-evaluate`.
- `measured_commit`: 40-hex commit the candidate bytes were measured at.
- `pinned_at_commit`: commit that changed only `expected.json` (anchor; PROTOCOL-APPENDIX L44).
- `baseline_sha256`: `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` (r14-installed, cc2168 blob).
- `candidate_sha256`: sha256 of the repaired `tools/souji-census.sh` at `measured_commit`. Filled last (F8).
- `files`: sha256 for every snapshot input: `record.json`, `tests/fixtures/r15-census-config.py`, each raw stdout and stderr capture for each arm, and the checker's own expected case-id digest.

Literals that belong in the checker source, not in `expected.json` (F5): the case-id tuple, exact exit and finding per case, the namespace set `R14C2-01..12`, the benign and mixed-fleet case ids, and the `expected.json` sha256 anchor.

Checker self-test negative controls (each asserts exact exit and finding-id set):
1. Green-only record (no baseline arm): exit 2.
2. Baseline benign arm exit 0 (non-discriminating): exit 2.
3. Baseline exit 2 with a different reason than `git-config-unsupported`: exit 2.
4. Changed benign arm exit 2: exit 1 (honest failed repair).
5. Namespace case mismatch: exit 1. Missing namespace id: exit 2.
6. Duplicate, unknown or zero-case ids: exit 2.
7. Header-only changed mixed-fleet output: exit 1.
8. Raw-capture byte flip: exit 2, `snapshot_tampered`.
9. Unlisted file in snapshot directory: exit 2, `snapshot_tampered`.
10. `expected.json` verdict or pin edited without anchor update: exit 2, `snapshot_tampered`.
11. Record `candidate_sha256` differs from pin: exit 2.
12. Baseline digest set to `6a000c59…` (a31642d): exit 2.
13. `--case` subset: exit 2 usage.
14. Symlink, hardlink, or path outside `--root`: exit 2.
15. JSON `true` as exit code, or a string exit: exit 2.
16. Record's `command` string is never executed: spy check (no subprocess call).

## 5. Acceptance for L1 (named, not run here)

Run after all seats finish, under `TMPDIR=/var/tmp`:
- `python3 tools/souji-preservation-evidence.py --selftest; echo rc=$?` → `0`, last line `selftest: N/N passed`. Do not pin N in the registry row.
- `python3 tests/fixtures/r15-preservation-evidence.py; echo rc=$?` → `0`.
- `python3 tools/souji-preservation-evidence.py --frozen tests/fixtures/r15-preservation-frozen; echo rc=$?` → `0`, `clean`.
- Independent digest re-derivation: `sha256sum -c` over every `files` entry, run by L1 outside the gate.
- Pin binding: `git show <measured_commit>:tools/souji-census.sh | sha256sum` equals `candidate_sha256`; `git show cc2168325768d5356a82c039dcdf787377c55784:tools/souji-census.sh | sha256sum` equals `baseline_sha256`.
- Paired controls on the same committed fixture: `python3 tests/fixtures/r15-census-config.py --tool <cc2168 copy in /var/tmp>` expects exit 1 with the benign ids failing for the routed reason; `--tool <repaired copy>` expects exit 0 with 12/12 namespace and mixed-fleet rows. Use the verification plan rule: baseline exit 1 is expected red; baseline exit 2 is could-not-evaluate.
- Tamper: flip one byte in a copy under `/var/tmp` → exit 2, `snapshot_tampered`. Committed fixture unchanged: `git status --porcelain -- tests/fixtures/r15-preservation-frozen` is empty.
- Q4 check: `grep -c 'TMPDIR:-/tmp' tools/souji-preservation-evidence.py tests/fixtures/r15-*.py` → `0`.

## 6. Limits and unrun checks

- No check was run. The checker, fixtures and frozen snapshot do not exist, so every acceptance line above is unrun.
- F1-F12 are source-grounded. The benign-config harm path is grounded in committed `tools/souji-census.sh` source plus the round-14 closure's recorded observation. It is not re-observed here.
- Digests were computed read-only from committed bytes. Sibling seats' reports were not read.
- No pacman action, no install, no host-service change.

## 7. Routed to SoujiR15

Material items already sent: F2 (baseline literal must be `fcff8b05…`, not `BASELINE_SHA`), F3 (dispatched interface lacks `--frozen`), F5 (checker-source anchor for `expected.json`), F7 (no `--case` subset for exit 0).
## 8. No-query boundary disclosure

Authoritative boundary (from SoujiR15 IRC): explicit known paths only; no whole-lane or census recursive glob/search; no runtime probes.

Violations during this seat, disclosed (not repeated after notice):
- `_glob` on the lane root (non-recursive listing) and `_glob` `**/*` over the lane root with `gitignore: false`. Its output listed filenames under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `.hold.json`, `results/`). Filenames only. No file in that directory was opened, read, copied, or queried.
- `_glob` `**/PROTOCOL*` over the lane root, and a `_glob` `{tools,tests,census/round-15,census/round-14,.ufo/waves/round-15}/**/*{preserv,admi,checker,baseline,frozen}*` search. The second returned entries from outside the lane (a `mori-shokunin` path). Nothing was opened from it.
- `_grep` of `(?i)admission|preservation|two-evidence|frozen|checker` over the lane root. Its output included round-13 and round-14 report and fixture paths. No operator-sweep paths matched.

Limitation: any finding that relied on a recursive listing was cross-checked by reading the explicit file. Only explicit files (`PROTOCOL.md` L343-423, `PROTOCOL-APPENDIX.md` L35-53, tools/tests paths, `census/round-14/*`, `corpus/*`, `.ufo/waves/round-15/*` JSON) were read for content. No runtime probe or test was run. The only shell commands were read-only `git rev-parse`, `cat-file`, `show | sha256sum`, `status`, and `log` on committed bytes.
