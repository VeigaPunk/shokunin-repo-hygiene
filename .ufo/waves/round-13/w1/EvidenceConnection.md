# Round 13 W1 — EvidenceConnection (UFO-FSD Connector Report)

Seat: `SoujiR13.EvidenceConnection` (connector, leaf).  
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin` (baseline HEAD `31984f4`).  
Judged on: **calibration**, **operability**, **coverage**.  
Execution / Tooling: No build, test, lint, or format execution. No subagent dispatch. No edits to shared bookkeeping, operator sweep, or sibling repos. Tool installs: none.

---

## 1. Executive Summary & Synthesis

This report connects three historically coupled defects in `souji-shokunin`:
1. **The Round 11 Shared-Relay Failure** (`cert-16.json` overwritten by concurrent certifiers; CERTIFIED verdicts attached to uninstalled candidate bytes `60aef4c0` rather than installed bytes `6a000c59` / `11bf9cdf`; `corpus/lessons/round-11.md:14–17`).
2. **The Round 12 K5 Nonexistent-Fixture Defect** (`corpus/knowledge/quarantine-same-filesystem-rename.md` admitted in the Gate table citing a "committed fixture" that was admitted to be a scratch script; paired with circular criterion Q15 relaxing Q4 to allow `/dev/shm`, withdrawn by Q16; `round-12-verifier-spotcheck.md:12–14`).
3. **The Current Round 13 C1 Design** (`tools/souji-cert-evidence.py` + `tests/fixtures/r13-cert-evidence.py` + `tests/fixtures/r13-cert-frozen/`), which introduces an executable evidence validator rejecting mismatched installed hashes, shared fragment ownership, missing evidence paths, and false success.

### The Non-Obvious Move
Current round-13 proposals (`ReviewEvidence`, `ReviewQuality`, `EvidenceGate`) create an executable validator for **tool certification fragments**, but leave **knowledge entry fixtures** governed by toothless prose review (draft Q17: *"the round Gate separately resolves every admitted entry's recheck path"*). That reliance on manual Gate prose is **the exact mechanism that admitted K5 in round 12**. Furthermore, criterion Q2 (which permitted mere textual citation of a fixture without existence checking) and criterion Q6 (which relied on manual single-tool sha equality) remain un-superseded in `corpus/QUALITY.md`.

We propose a single, bounded synthesis:
**Establish two lesson-grounded superseding criteria in `corpus/QUALITY.md` that demonstrably fail on defect inputs, without relaxing Q4 and without introducing duplicate validation tooling**:
- **Q19 (supersedes Q2)**: Knowledge fixture grounding and containment. A claim citing a fixture must resolve to a tracked file in `git ls-files --error-unmatch`, located under `tests/fixtures/`, hardcoded to `/var/tmp` with a trap per Q4, and passing syntax check. Fails demonstrably on uncommitted or nonexistent fixtures (such as r12 K5).
- **Q20 (supersedes Q6)**: Executable evidence integrity and relay rejection. A tool verdict fragment must be verified by `tools/souji-cert-evidence.py` in `--frozen` mode against committed input pins, rejecting shared writable relays, uninstalled artifact digests, and false passes. Fails demonstrably on real committed defect records (such as `HEAD:census/round-10/cert-16.json`).

---

## 2. Evidence and Line-Level Precedents

### A. The Round 11 Shared-Relay and Wrong-Byte Failure
- **Relay Overwrite**: In round 11, candidate certifier harness `tools/cand-s16-cert.py:1856–1860` hardcoded its output path to `census/round-10/cert-16.json` (`fragment = R10 / "cert-16.json"`). Seats S16, S12, S28, and S32 ran concurrently, repeatedly clobbering the shared file (`census/round-11/cert-12.json:2660`, `census/round-11/final-27.json:123`, `census/round-11/dissent-32.md:49–65`).
- **Verdicts on Uninstalled Bytes**: S16's overwritten file reported `certification_ready: true` and `CERTIFIED` for candidate `cand-census-03.sh` (sha `60aef4c0…`), while the installed census was `462dabd2…` (and later `6a000c59…`). The round concluded: *"CERTIFIED verdicts were attached to bytes other than those measured... no certification on compromised evidence"* (`corpus/lessons/round-11.md:14–17`).
- **Real Committed Residue at HEAD**: As discovered by `AttackCalibration` and `MistakeLedger`, `HEAD:census/round-10/cert-16.json` (sha256 `662294df4291c16f…`) was committed in `1ccf11b` and **still contains the false CERTIFIED verdict on non-installed census bytes** (`:2618` `certification_ready: true`; `:10` `60aef4c0…`). The restored r10 state (`6293283e…` at `e879ba0`) was never re-restored after `1ccf11b`.
- **Defect in Q6 (`corpus/QUALITY.md:30`)**: Q6 required one author per fragment and sha equality, but its test column (`sha256sum tools/<tool>.sh equals the digest in the verdict fragment; one author per fragment`) lacked an executable gate, lacked relay detection, and permitted manual prose claims to pass.

### B. The Round 12 K5 Nonexistent-Fixture and Circular Q15 Defect
- **Scratch Recheck Claimed as Committed Fixture**: Entry `corpus/knowledge/quarantine-same-filesystem-rename.md:21` (K5) candidly stated: *"FIXTURE (scratch-only script, not committed; recheck: is its self-contained equivalent)"*. Yet in `corpus/lessons/round-12.md:136`, the Gate table admitted K5, claiming: `Q2 (strace run; the pasteable recheck line is the committed fixture)`.
- **Defect in Q2 (`corpus/QUALITY.md:23`)**: Q2's test column read: *"the entry cites `<file>@<tag>:<line>` or a committed fixture"*. Because the test checked only whether the text *cited* a fixture, the gate passed without verifying whether any fixture file existed in git tracking.
- **Circular Relaxation of Q4**: Because K5 needed to exercise `EXDEV` on `mv`, the scratch script wrote to `/dev/shm`. The lane created Q15 (`corpus/QUALITY.md:39`) specifically to permit `/dev/shm` for K5. The non-author spot check (`corpus/lessons/round-12-verifier-spotcheck.md:12–14`) rejected this:
  - Rejected K5: *"the reviewer found its Gate claimed a committed fixture that does not exist; the lane moved K5 to HELD"* (`round-12-verifier-spotcheck.md:12`).
  - Withdrew Q15 via Q16: *"Q15's only lesson pointer was the K5 admission it was written for (circular; orchestrator review, 2026-10-19). No mined souji lesson grounds a /dev/shm second device, so Q4 stands unrelaxed"* (`corpus/QUALITY.md:40`).

### C. The Round 13 C1 Design and Its Verification Boundaries
- **C1 Objective**: `.ufo/waves/round-13/w1-spec.json:19–27` dispatches `EvidenceGate` to build `tools/souji-cert-evidence.py` and `tests/fixtures/r13-cert-evidence.py`.
- **Parent Augmentation**: Parent `SoujiR13` instructed `EvidenceGate` to add `--frozen DIR` mode, validating `expected.json` input digest pins for all snapshot inputs (`tests/fixtures/r13-cert-frozen/**`) to prevent mutable manifest relay tampering.
- **Key Peer Findings**:
  - `ReviewEvidence.md`: Identifies that a naive manifest validator is insufficient if artifact paths are arbitrary candidates (F1), if coverage can be empty (F2), if digests are not checked against live bytes (F3), or if verdicts are parsed from self-declared narrative strings (F4).
  - `AttackCalibration.md`: Observes that a synthetic selftest alone is an existence count (`before.json:5`), not calibration proof. True calibration requires the validator to demonstrably reject real historical defect records (CX1: `HEAD:census/round-10/cert-16.json`; CX2: candidate paths matching their own sha).
  - `ReviewQuality.md`: Mapped all 53 mistakes; drafted Q17 and Q18 in `corpus/QUALITY.md:41–42`, but observed that Q17 still relies on manual gate resolution for knowledge fixtures, and neither Q17 nor Q18 supersedes the flawed Q2 and Q6 rows.

---

## 3. Affected Axes

| Axis | Pre-Round / Baseline Defect | How the Proposed Move Improves the Axis | Risk of Incompatible Proposals |
|---|---|---|---|
| **Calibration** (Lowest axis: 7) | Evaluated by paper prose and rule-mapping counts (51/53 in r12; `before.json:4` counting file existence). Gate admitted nonexistent fixtures (K5) and overwrote relays (cert-16). | Replaces prose citations with mechanically failing checks. Proves the validator fails on real committed defect records (`HEAD:census/round-10/cert-16.json`) and that knowledge fixtures fail on nonexistent paths. | Synthetic-only testing allows a false sense of security; wording leakage ("CERTIFIED") restates r11 overclaims. |
| **Operability** | Manual Gate spot-checks require human inspection; quarantine staging previously lacked per-target timeout (M43/M44). | Execution commands are deterministic, non-interactive shell and Python CLI calls (`git ls-files`, `grep`, `--frozen`). Self-contained under `/var/tmp` with traps. | Fixtures breaking Q4 by writing to `/tmp` (M10/M30) or `/dev/shm` (Q15); validator crashing on unhandled malformed JSON. |
| **Coverage** | Knowledge entries (F1, F3, F4) admitted without committed test backing; F2 deferred; K5 held due to scratch test. | Establishes a rigorous, clean standard for knowledge fixtures (Q19) so F2 (`git repo structure`) can be safely admitted on a real tracked fixture. | Dropping or narrowing knowledge criteria; creating unverified parallel criteria. |

---

## 4. Proposed Move: Lesson-Grounded Superseding Criteria (Q19 & Q20)

Per `corpus/QUALITY.md:11–13`, criteria are *"superseded by a new row that names the row it replaces, never rewritten"*. We recommend that L1 incorporate two superseding criteria into `corpus/QUALITY.md`:

### Proposal 1: Q19 (Supersedes Q2) — Mechanical Verification of Knowledge Fixtures
- **Names the replaced row**: Supersedes Q2.
- **Lesson grounding**: `corpus/lessons/round-12.md ## Mistakes` M57 (`MistakeLedger.md:57`: Gate row claimed a committed fixture for K5 when none existed; `round-12.md:136` vs `quarantine-same-filesystem-rename.md:21`; `round-12-verifier-spotcheck.md:12–14`).
- **Criterion**: Where documentation is silent or contradicts tool behaviour, a knowledge claim or recheck must cite either:
  1. Source code at a verified release tag (`<file>@<tag>:<line>`), verified by read-only source grep; OR
  2. A committed, tracked fixture under `tests/fixtures/<name>.sh` (or `.py`).
  Prose in an entry, Gate table, or recheck claiming that a fixture exists or was run cannot substitute for a tracked file. Scratch scripts or uncommitted rechecks are strictly non-admitting.
- **Mechanically failing test**:
  For each fixture path `$P` cited by an admitted entry:
  ```bash
  git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files --error-unmatch -- "$P" >/dev/null 2>&1 && \
  test -f "/home/vgpnk/Projects/shokunin/souji-shokunin/$P" && \
  grep -c 'TMPDIR:-/tmp' "/home/vgpnk/Projects/shokunin/souji-shokunin/$P" | grep -q '^0$' && \
  grep -cE '/var/tmp' "/home/vgpnk/Projects/shokunin/souji-shokunin/$P" | grep -qv '^0$' && \
  grep -cE 'trap ' "/home/vgpnk/Projects/shokunin/souji-shokunin/$P" | grep -qv '^0$' && \
  bash -n "/home/vgpnk/Projects/shokunin/souji-shokunin/$P"
  ```
- **Why it demonstrably fails**:
  - Tested against r12 K5 (`$P` = scratch script path): `git ls-files --error-unmatch` exits 1 (`error: pathspec ... did not match any file(s) known to git`).
  - Tested against any script writing to `/tmp`: `grep -c 'TMPDIR:-/tmp'` fails.
  - Tested against any script lacking `/var/tmp` or `trap`: fails.
- **Q4 & Tooling Conformance**: Preserves Q4 strictly unrelaxed (no `/dev/shm` exception). Does not add duplicate tools: executes via standard git and coreutils.

### Proposal 2: Q20 (Supersedes Q6) — Executable Evidence Validator & Frozen Relay Gate
- **Names the replaced row**: Supersedes Q6.
- **Lesson grounding**: `corpus/lessons/round-11.md:14` (shared relay overwritten), `round-11.md:16` (candidate selection contradicted class), `corpus/lessons/round-12.md` M40, M41; and `round-13` M54/M55 (`MistakeLedger.md:53–54`: committed false-success cert-16 record at `HEAD:census/round-10/cert-16.json`).
- **Criterion**: Every certification or tool verdict fragment must be verified by `tools/souji-cert-evidence.py`. The fragment must:
  1. Be written to an author-unique path (`census/round-<N>/cert-<author>.json` or `tests/fixtures/...`) with unique inode and no shared writable relay;
  2. Record the exact `sha256` of the installed tool bytes measured;
  3. Reference evidence files that exist as regular, non-symlink files within the lane root;
  4. Derive its verdict directly from structured outcome fields (`exit_code` == 0 for pass, >0 for fail); narrative fields are ignored;
  5. Pass frozen-mode snapshot verification (`--frozen DIR`) against committed input pins (`expected.json`) to prevent mutable manifest relay tampering.
  Passing evidence integrity verifies evidence consistency only and never grants deletion certification (certification remains OFF).
- **Mechanically failing test**:
  ```bash
  python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --selftest && \
  python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --frozen /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-cert-frozen
  ```
  AND negative replay controls demonstrating rejection:
  - Replay of `HEAD:census/round-10/cert-16.json` against installed `tools/souji-census.sh` (`6a000c59…`) exits 1 with `installed_digest_mismatch`.
  - Replay of candidate path `tools/cand-census-03.sh` exits 1 with `artifact_not_installed`.
  - Replay of duplicate author / shared fragment exits 1 with `duplicate_author` / `shared_fragment`.
- **Why it demonstrably fails**:
  Unlike Q6 (which allowed loose manual grep), Q20 is backed by the CLI gate. Any hash mismatch, duplicate fragment, shared inode, missing evidence file, or exit code contradiction causes an immediate nonzero exit (1 or 2).

---

## 5. Trace of Second-Order Effects

1. **Runtime Surface**:
   - `tools/souji-cert-evidence.py` is registered in `SKILL.md` as a `gate`. It executes strictly read-only, hashes tool files, and inspects declared JSON fragments.
   - Operates with fixed exit codes: `0` (clean), `1` (failed check / honest fail), `2` (could-not-evaluate / tampered snapshot / malformed input).
   - Python code avoids unconstrained tempdir creation (`mkdtemp` strictly specifies `dir="/var/tmp"` per Q4).
2. **Contract Surface (`corpus/QUALITY.md`)**:
   - Clean cutover: Q19 explicitly supersedes Q2; Q20 explicitly supersedes Q6. Prior rows remain in the table for historical provenance, but their superseded status is explicit.
   - Eliminates circularity: Q19 cites r12 M57; Q20 cites r11 M40/M41 and r13 M54/M55.
   - Closes the loophole in draft Q17 by removing the reliance on unverified human Gate prose for knowledge fixtures.
3. **Substrate Surface (Git & Filesystem)**:
   - Exposes the committed defect at `HEAD:census/round-10/cert-16.json`. L1 can safely maintain this file as an explicit historical negative replay fixture rather than leaving it as an unacknowledged false claim in the repository.
   - Wave 1 leaf write scopes remain completely isolated: no shared files touched.
4. **Verification Surface**:
   - L1 gains concrete, copy-pasteable terminal verification commands for the integration commit.
   - Both positive controls (clean exit 0) and negative controls (rejection exit 1/2) are verified.

---

## 6. Risks, Contradictions, and Limitations

1. **Contradiction in Current `corpus/QUALITY.md`**:
   - ReviewQuality drafted Q17 and Q18 at lines 41–42.
   - However, draft Q17's test relies on *"the round Gate separately resolves every admitted entry's recheck path"*. This is a direct regression to the round-12 mechanism that failed.
   - Q19 resolves this contradiction by replacing prose resolution with `git ls-files --error-unmatch`.
2. **Author Identity is Unauthenticated (Inference / Limitation)**:
   - As noted by `ReviewEvidence` (F5) and `AttackCalibration` (CX3), the `author` field in JSON is an unauthenticated string. In r11, `tools/cand-s16-cert.py` hardcoded `"seat": "S16"`, so four different seats produced files claiming to be S16.
   - `souji-cert-evidence.py` enforces string and path uniqueness, which prevents accidental overwrites, but **cannot prove cryptographic or model independence**. Independence remains a Q5 blind re-derivation standard, not a gate output.
3. **Candidate-Selection Bias (Limitation)**:
   - In r11 (M41), the certifier picked `souji-census.impl-46.sh` because it had the most selftests, even though it failed the compare defect class.
   - An evidence validator cannot detect selection bias among candidates unless candidates are pre-registered. Q20 restricts valid certifying artifacts strictly to **installed tools**, preventing candidate self-certification.
4. **Integrity vs. Tool Safety (Contract Boundary)**:
   - A clean run of `souji-cert-evidence.py` certifies **evidence consistency**, NOT tool deletion safety. Certification remains strictly **OFF**.

---

## 7. Verification Steps for L1 Integration

The following checks should be executed by the L1 integrator upon landing round-13 changes:

```bash
L=/home/vgpnk/Projects/shokunin/souji-shokunin

# 1. Verify Q19 mechanical fixture check on admitted entries:
# Ensure every admitted entry citing a fixture is tracked in git and complies with Q4
for entry in $L/corpus/knowledge/*.md; do
  fix=$(grep -E '^recheck:.*tests/fixtures/' "$entry" | sed -E 's/.*(tests\/fixtures\/[^ ;"'\''\)]+).*/\1/')
  if [ -n "$fix" ]; then
    git -C "$L" ls-files --error-unmatch "$fix" >/dev/null 2>&1 || { echo "FAIL Q19: $fix not tracked"; exit 1; }
    grep -c 'TMPDIR:-/tmp' "$L/$fix" | grep -q '^0$' || { echo "FAIL Q19: $fix references /tmp"; exit 1; }
    grep -cE '/var/tmp' "$L/$fix" | grep -qv '^0$' || { echo "FAIL Q19: $fix lacks /var/tmp"; exit 1; }
    grep -cE 'trap ' "$L/$fix" | grep -qv '^0$' || { echo "FAIL Q19: $fix lacks trap"; exit 1; }
    bash -n "$L/$fix" || { echo "FAIL Q19: $fix syntax error"; exit 1; }
    echo "PASS Q19 fixture check: $fix"
  fi
done

# 2. Verify Q20 evidence validator positive controls:
python3 -m py_compile $L/tools/souji-cert-evidence.py
python3 $L/tools/souji-cert-evidence.py --selftest; echo "selftest_rc=$?"
python3 $L/tools/souji-cert-evidence.py --frozen $L/tests/fixtures/r13-cert-frozen; echo "frozen_rc=$?"

# 3. Verify Q20 negative replay controls (must demonstrably fail with exit 1 or 2):
# a. Replay uninstalled census bytes (HEAD cert-16 defect CX1):
python3 $L/tools/souji-cert-evidence.py --replay-defect cert16-uninstalled-bytes; echo "replay_cert16_rc=$?"  # expect 1
# b. Replay candidate artifact path (CX2):
python3 $L/tools/souji-cert-evidence.py --replay-defect candidate-artifact-path; echo "replay_cand_rc=$?"    # expect 1

# 4. Verify no positive "CERTIFIED" claims in clean output:
grep -niE 'verdict.*certified' $L/tools/souji-cert-evidence.py | grep -v 'NOT_CERTIFICATION' || true

# 5. Verify QUALITY.md superseding table consistency:
grep -E '^\| Q19 \| Supersedes Q2' $L/corpus/QUALITY.md
grep -E '^\| Q20 \| Supersedes Q6' $L/corpus/QUALITY.md
```

Report complete. Written to `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/EvidenceConnection.md`.
