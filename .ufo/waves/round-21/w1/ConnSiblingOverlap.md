# ConnSiblingOverlap — Sibling-Overlap Scan Across Round-21 Claims

## Executive Summary & Disposition

STATUS: DONE — Sibling-overlap scan complete across all three preregistered round-21 claims (`C1` calibration, `C2` operability, `C3` coverage) against the five mandated charter files:
- `tameshi-shokunin/PROVINCE.md` (HEAD)
- `kagi-shokunin/PROVINCE.md` (HEAD)
- `mori-shokunin/PROVINCE.md` (HEAD)
- `kama-shokunin/PROVINCE.md` (HEAD)
- `souji-shokunin/PROVINCE.md` (current)

No sibling contests Souji's lane-internal ownership of these three surfaces when strictly bounded to Souji's own receipts, acceptance replay, and tool output. However, adjacent ground is active for each claim: Tameshi owns reusable verification craft; Kagi owns secrets, credential hygiene, and historical exposure; Mori owns host observability, `/tmp` resource runway, and seat terminal liveness; and Kama owns local model endpoints and procfs listener identification.

---

## Claim-by-Claim Adjacency & Overlap Scan

### Claim C1: Seat-audit names implicit fleet-root-namespace reads (`tools/souji-seat-audit.py`)

- **Surface:** Tool invocation auditing (`read`, `grep`, `glob`) across seat transcripts to detect implicit relative path targets resolving at the fleet root cwd (`$SHOKUNIN_ROOT`) outside the lane namespace (`souji-shokunin/.ufo/waves/round-21/preregistration.txt:4-13`).
- **Sibling ownership & contest:**
  - **tameshi-shokunin** owns verification craft and documented gate methods (`tameshi-shokunin/PROVINCE.md:3-5,7-12`), citing `kaidoku-shokunin`'s audit-lane pattern (`PROVINCE.md:10-11`), but explicitly refuses product gate ownership: *"product domains — every lane's gate remains its own; tameshi owns only the reusable craft... Never edits a sibling's gate code"* (`tameshi-shokunin/PROVINCE.md:14-17`). Tameshi does *not* contest Souji's lane-internal seat audit gate.
  - **mori-shokunin** owns passive seat terminal status observation (`mori-shokunin/PROVINCE.md:103-107`) and wave settlement (`mori-shokunin/PROVINCE.md:145-154`), but records in its adjacency matrix that *"souji: Owns artifact cleanup, not process/fleet health. Its province says 'mori-shokunin observes fleet health and reports; souji acts on artifacts'"* (`mori-shokunin/PROVINCE.md:69`). Mori does *not* audit tool invocation parameters or evaluate seat contract compliance.
  - **kagi-shokunin** owns boundary and partition checks over directory breadth (`corpus/scope-gate.sh`, `kagi-shokunin/PROVINCE.md:51`), but does not audit agent transcripts.
  - **kama-shokunin** explicitly refuses anything outside local model serving (`kama-shokunin/PROVINCE.md:40-43`).
  - **souji-shokunin** establishes its own boundary: work surfaces include `$SHOKUNIN_ROOT` (cwd `.`) and `$SHOKUNIN_ROOT/<lane>-shokunin/` (`souji-shokunin/PROVINCE.md:21-22`), but *"Evidence-integrity checking is limited to souji's own receipt/certification fragments; it does not become fleet orchestration or an independent promotion authority"* (`souji-shokunin/PROVINCE.md:95-97`).
- **Pattern Souji should reuse:**
  - From **tameshi-shokunin** (`tameshi-shokunin/PROVINCE.md:3-5`): The discipline of *"fail-closed arms, verdict-line discipline, no-permissiveness audits, before/after proof"*. Specifically, Souji pairs the new `V-READ-ROOT` class with an explicit, independent per-call oracle (`census/round-21/read-root-oracle.tsv`) and base-discriminating synthetic fixtures (`tests/fixtures/r21-read-root.py`) where baseline flags 0 and the target tool flags exact oracle matches.
  - From **mori-shokunin** (`mori-shokunin/PROVINCE.md:103-107,148`): Passive parsing that explicitly accounts for truncation and lower bounds (e.g. truncated paths `…` are treated as lower bounds and not flagged, disclosing limits rather than falsely asserting exactness).
- **Anything Souji must report rather than absorb:**
  - Fleet-level agent liveness or termination anomalies observed in transcripts route to **mori-shokunin** (`mori-shokunin/PROVINCE.md:6-10,103-107; souji-shokunin/PROVINCE.md:50-52`).
  - Any raw credential strings or tokens observed in transcripts route to **kagi-shokunin** (`kagi-shokunin/PROVINCE.md:5,48; souji-shokunin/PROVINCE.md:36-37,55-56`).
  - Souji must *not* absorb general fleet transcript auditing or promotion authority: `tools/souji-seat-audit.py` evaluates Souji's own seat contract compliance only (`souji-shokunin/PROVINCE.md:95-97`). Reusable transcript auditing patterns must be reported to **tameshi-shokunin** (`tameshi-shokunin/PROVINCE.md:14-17`).

---

### Claim C2: Scratch-clone replay runner (`census/round-21/run-acceptance.py`)

- **Surface:** Non-author replayable acceptance runner verifying 18 fixed commands from an arbitrary local Git clone/bare mirror without requiring `SRC == lane path` or `SRC HEAD == rev` (`souji-shokunin/.ufo/waves/round-21/preregistration.txt:15-19`).
- **Sibling ownership & contest:**
  - **tameshi-shokunin** owns verification-fixture craft: *"hermetic suites, mutation testing, fail-closed arms... before/after proof"* (`tameshi-shokunin/PROVINCE.md:3-5`). Tameshi refuses individual lane gate ownership (`PROVINCE.md:14-15`), so it does not contest Souji's runner, but governs the reusable methodology.
  - **mori-shokunin** owns host runway observation (`SURFACE disk` and `SURFACE cgroup` monitoring `$ROOT` and `/tmp`; `mori-shokunin/PROVINCE.md:26,94`). Crucially, Mori's FR9 explicitly warns: *"scratch paths and unreconstructable fingerprints are not durable evidence; retain a reproducible fixture generator and digest before making replay claims"* (`mori-shokunin/PROVINCE.md:52`). A runner that creates scratch clones in `/tmp` interacts directly with Mori's monitored runway.
  - **kama-shokunin** maintains lane-owned fixtures using ephemeral execution with strict teardown (`kama-shokunin/PROVINCE.md:73-76: "graceful teardown with returncode 0, ownership-gated port closure... Fake-server controls run only /tmp fakes on ephemeral loopback ports"`).
  - **kagi-shokunin** exercises isolated scratch environments (`corpus/surface-census.sh --verbs` on scratch overrides; `corpus/op-ref-probe.sh --dotenv-bytes` under `env -i` with scratch HOME/XDG; `kagi-shokunin/PROVINCE.md:46,49`) and records lone-clone behavior (`claim-ledger.sh: lone clone prints FLEET-ABSENT`; `PROVINCE.md:52`).
  - **souji-shokunin** owns hygiene surfaces including `.scratch/` and dead worktree metadata (`souji-shokunin/PROVINCE.md:10-13`), refuses Git history rewrites (`PROVINCE.md:34`), refuses touching dirty/unpushed work (`PROVINCE.md:40`), and limits evidence checking to its own receipts (`PROVINCE.md:95-97`).
- **Pattern Souji should reuse:**
  - From **tameshi-shokunin** (`tameshi-shokunin/PROVINCE.md:3-5`): Hermetic fixture isolation. Acquiring a private clone with `git clone --quiet --no-local --no-checkout` and checking out a detached revision guarantees that ambient untracked files, branch pointers, and dirty working trees cannot leak into the test run.
  - From **mori-shokunin** (`mori-shokunin/PROVINCE.md:52`): Adhering to FR9 by pinning evidence to durable git commit SHAs (`--rev FULL40`) rather than ephemeral scratch paths.
  - From **kama-shokunin** (`kama-shokunin/PROVINCE.md:73-76`) & **kagi-shokunin** (`kagi-shokunin/PROVINCE.md:46,49`): Guaranteed ephemeral cleanup. Any temporary clone created in `/tmp` must be strictly cleaned up on all exit paths (success, mismatch, refusal, exception) so no dead worktrees drain Mori's `/tmp` disk runway.
- **Anything Souji must report rather than absorb:**
  - Souji must *not* claim general fleet replay runner or workspace orchestration authority (`souji-shokunin/PROVINCE.md:95-97,105-106`).
  - Host disk or memory runway pressure encountered during scratch cloning routes to **mori-shokunin** (`mori-shokunin/PROVINCE.md:26`).
  - The general method of non-author scratch-clone replay runners should be reported to **tameshi-shokunin** (`tameshi-shokunin/PROVINCE.md:14-17`) for fleet-wide verification craft admission once demonstrated across two independent lanes.

---

### Claim C3: Process-census reason-field redaction (`tools/souji-proc-census.sh`)

- **Surface:** Sanitizing gone-path candidates drawn from secret-bearing argv elements, applying regex redaction patterns, bounding reason length to 160 bytes, and adding a `/proc`-free entry point (`--reason-only argv|fd`) in `tools/souji-proc-census.sh` (`souji-shokunin/.ufo/waves/round-21/preregistration.txt:21-26`).
- **Sibling ownership & contest:**
  - **kagi-shokunin** OWNS secrets, vault ops, and credential hygiene evidence (`kagi-shokunin/PROVINCE.md:3,5`). Kagi explicitly defines the adjacency boundary in `PROVINCE.md:67`: *"Adjacent — report, don't absorb: ... chousa, kasegi and kumitate run their own secret-shaped tripwires over their outputs (hygiene filters, not vault ops); kama refuses to hold credentials for authenticated health checks and would route that need here through L0... kagi owns runtime auth and credential custody"*. Kagi confirms that lane-local redaction of emitted strings is an *output hygiene filter*, not vault ops or secret-scanner ownership.
  - **souji-shokunin** explicitly refuses credentials, secrets, tokens, vault refs (→ kagi) (`souji-shokunin/PROVINCE.md:36-37,55-56,101-104`). Furthermore, Souji's charter explicitly acknowledges the limits of its scanner: *"The Refuses policy is not proof that the scanner avoids all raw private values: it reads raw same-uid argv, and its reason column sanitizes control bytes but does not apply the cmd canary redactor to path text. The current source-level defect and unknown historical exposure are explicitly held for operator/Kagi, not an authorization for Souji to inspect private snapshots or live processes. See the souji | round-20 F5 reason-field L0 request and the final correction in corpus/knowledge/process-residue-observations.md"* (`souji-shokunin/PROVINCE.md:163-169`).
  - **mori-shokunin** owns fleet/host observability and refuses credential material (`mori-shokunin/PROVINCE.md:15`). Mori employs MESSAGE-free journal logging (`mori-shokunin/PROVINCE.md:24,44: "No raw MESSAGE is emitted"`) and minimizes retained evidence (`PROVINCE.md:125-131`). Mori's adjacency matrix confirms Souji acts only on artifact cleanup, not fleet health (`PROVINCE.md:69`).
  - **kama-shokunin** decodes procfs for child-owned loopback listeners (`kama-shokunin/PROVINCE.md:82-88`), but refuses auth/credentials (`PROVINCE.md:40`).
  - **tameshi-shokunin** owns verification craft (`tameshi-shokunin/PROVINCE.md:3-5`), including canary fixtures.
- **Pattern Souji should reuse:**
  - From **kagi-shokunin** (`kagi-shokunin/PROVINCE.md:48-50,67`): Output hygiene tripwire discipline. Reason redaction must be treated strictly as an output hygiene filter over Souji's own emitted TSV columns, never as a general secret scanner. Fixtures must use synthetic fabricated canaries only, never real credentials (`kagi-shokunin/PROVINCE.md:49; souji-shokunin/.ufo/waves/round-21/preregistration.txt:25`).
  - From **mori-shokunin** (`mori-shokunin/PROVINCE.md:24,44,125-131`): Evidence minimization and defensive field bounds. The 160-byte upper bound on the `reason` field mirrors Mori's policy of bounding logged fields and suppressing unbounded raw message strings.
  - From **kama-shokunin** (`kama-shokunin/PROVINCE.md:73-76,82-88`) & **tameshi-shokunin** (`tameshi-shokunin/PROVINCE.md:3-5`): Decoupled unit testing. By adding the `--reason-only` entry point that operates on stdin (`preregistration.txt:24`), Souji decouples reason-redaction verification from live `/proc` inspection, creating a hermetic, repeatable test arm.
- **Anything Souji must report rather than absorb:**
  - **CRITICAL:** Any historical credential exposure or leaked secret values in historical census logs must be reported to **kagi-shokunin** and the operator (`kagi-shokunin/PROVINCE.md:5-6,67; souji-shokunin/PROVINCE.md:36-37,84-85,166-169`).
  - Souji must *not* claim to be a secret scanner, credential auditor, or vault authority (`souji-shokunin/PROVINCE.md:36-37,101-104; kagi-shokunin/PROVINCE.md:3,67`).
  - Souji must *not* claim process liveness, kill authority, or inspection of other uids (which belong to **mori-shokunin** and the operator; `souji-shokunin/PROVINCE.md:50-52,141-143,153-157; mori-shokunin/PROVINCE.md:3-10,69`).
  - Redaction in `tools/souji-proc-census.sh` must be documented as an internal output-hygiene filter on its own emitted rows, while secret patterns, vault ops, and exposure assessments remain Kagi/operator territory.

---

## Connector Synthesis: Non-Obvious Move

### Evidence

1. **Second-Order Substrate Contradiction between C2 Replay and Mori/Souji F5:**
   - Under C2, `census/round-21/run-acceptance.py` creates a temporary scratch clone under a temporary directory (`git clone --quiet --no-local --no-checkout` into a private temp dir; `preregistration.txt:17`).
   - Mori observes `/tmp` disk runway (`mori-shokunin/PROVINCE.md:26: "default df -P targets $ROOT and /tmp"`).
   - Furthermore, Mori's FR9 explicitly rules: *"scratch paths and unreconstructable fingerprints are not durable evidence; retain a reproducible fixture generator and digest before making replay claims"* (`mori-shokunin/PROVINCE.md:52`).
   - If an acceptance replay invocation is aborted, fails, or completes without deterministic scratch cleanup, it leaves abandoned git repositories and vanished scratch file descriptors in `/tmp`.
   - Souji's own F5 process residue census explicitly scans `/tmp` for residue: *"current-uid deleted cwd links (any location) or vanished scratch argv/fd paths under /var/tmp, /tmp, /dev/shm, listed by tools/souji-proc-census.sh"* (`souji-shokunin/PROVINCE.md:73-75`).
   - Therefore, a naive C2 runner implementation that leaves disposable clone directories in `/tmp` would directly create the exact F5 process residue that C3 and Souji's charter nominate for cleanup, and would degrade the host disk runway monitored by Mori.

2. **Decoupled Verification Synthesis across C2 and C3:**
   - C3 introduces `--reason-only` to achieve a `/proc`-free entry point that exits before any `/proc` or `boot_id` read (`preregistration.txt:24`).
   - C2 acceptance testing runs 18 fixed steps that must not access live `/proc` or touch literal lane paths (`preregistration.txt:17,22`).
   - Reusing Kama's lifecycle containment pattern (`kama-shokunin/PROVINCE.md:73-76`) establishes clean teardown of `/tmp` resources.

### Affected Axes

- **C2 Operability:** Non-author replays succeed cleanly from arbitrary repositories without leaving host residue.
- **C1 Calibration:** Replay output records durable commit SHAs (`--rev FULL40`) and exact step summaries without embedding ephemeral scratch paths into durable JSON records (adhering to Mori FR9).
- **C3 Coverage / Adjacency:** Avoids self-generating F5 scratch residue in `/tmp` that would trigger Souji's own process census or consume Mori's monitored `/tmp` runway.

### Proposed Move

L1 should ensure that `census/round-21/run-acceptance.py` encapsulates its scratch clone acquisition in a strict **ephemeral lifecycle context manager** (`tempfile.TemporaryDirectory` with fail-safe `shutil.rmtree` teardown):
1. **Zero-Residue Guarantee:** On all execution branches (normal exit 0, mismatch exit 1, refusal exit 2, and unhandled exceptions/signals), the temporary clone directory under `/tmp` is guaranteed to be deleted immediately upon exit.
2. **Durable Citation Binding (Mori FR9):** In the generated acceptance output JSON, the `root` metadata must record the durable requested revision (`args.rev`) and the original source path (`args.root`), while strictly omitting or redacting ephemeral temporary directory paths from recorded output fields.
3. **Pre-execution Lane-Path and Secret Refusal:** Refuse literal lane paths in step programs (as required by C2 contract) and refuse any output path inside the disposable scratch clone or measured directories.

### Risks & Mitigations

- *Risk:* Premature deletion of the scratch clone before the external acceptance JSON is fully written.
  - *Mitigation:* Ensure the external output JSON is atomically written to `args.output` before exiting the temporary clone context manager.
- *Risk:* Permission or lock issues preventing deletion on Windows or NFS mounts.
  - *Mitigation:* The runner runs on Linux (Arch Linux host `7.2.11-arch1-1`); `git clone --no-checkout` leaves no active processes or background daemons holding locks.

### Verification

1. Replay `census/round-21/run-acceptance.py --root . --rev <REV> --output /tmp/test-out.json` across scenarios S1, S2, and S3.
2. Verify exit 0, `all_matched 18/18`, and that no `/tmp/tmp*` or `/tmp/souji-*` directories remain after the command completes (`ls -d /tmp/*souji* 2>/dev/null` returns empty).
3. Verify `git status` in the source repository remains clean (`SRC digest/status before == after`).

---

## Tooling Directive & Process Compliance

- **Tooling Record:** No tools were installed, updated, or removed.
- **VCS & Execution Bounds:** Leaf member. No subagents dispatched (`task` not called). No VCS mutations performed. No target code executed. No live `/proc` or protected directories opened.
- **File Bounds:** Only the mandated named charter files were read; only this scoped report path was written.
