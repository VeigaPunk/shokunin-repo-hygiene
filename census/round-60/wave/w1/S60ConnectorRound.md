# S60ConnectorRound Report: Sibling-Overlap Scan & Synthesis

**Wave:** `souji-r60-w1`  
**Seat:** `S60ConnectorRound` (Role: `connector`, subagent)  
**Lane Root:** `/home/vgpnk/Projects/shokunin/souji-shokunin`  
**Milestone:** Freeze-record substance binding (C1 calibration) and atomic receipt writing (C2 operability)  
**Read-Only Assertion:** Read-only scan across all sibling lanes in `/home/vgpnk/Projects/shokunin`. Zero sibling code executed; zero production files modified.

---

## 1. Executive Summary

A comprehensive, read-only sibling-overlap scan across all 20 sibling shokunin lanes in `/home/vgpnk/Projects/shokunin` evaluated the existing fleet holdings on:
1. **(a) Freeze-record/preregistration substance binding:** Binding a claim's `Control:` receipt to the declared `Counter` bytes and to a pre-freeze revision.
2. **(b) Atomic receipt writing:** Hardened receipt writing with atomic temp+rename, refusal of overwrite, refusal of dirty worktree, bounded output, and revision/instrument checks.

### Findings Summary
- **No Duplicate Holdings:** Zero sibling lanes duplicate either ground. `preregistration.txt` with claim blocks (`## C<digits>`, `Counter:`, `Control:`, `Population:`, `Base:`) is held exclusively by `souji-shokunin` (35 historic preregistrations). No sibling tool validates that a `Control:` receipt matches the declared Counter blob bytes at freeze or enforces pre-freeze strict ancestry.
- **Complementary Holdings (10 lanes):** 
  - `tameshi-shokunin` enforces `git merge-base --is-ancestor` on control receipts (`receipt-revision-gate.py:172-175`) and binds tool sha256 to git blobs (`receipt-bytes-bind.py:65-75`).
  - `kotodama-shokunin` enforces preflight receipt overwrite refusals and symlink/hardlink refusals (`receipt_guard.py:161-240`).
  - `kaidoku-shokunin` provides the hardened atomic write pattern with `O_CREAT | O_EXCL | O_NOFOLLOW`, `fsync`, `os.replace`, and cleanup (`fetch-carrier.py:260-310`), as well as container freeze checks (`round-84/freeze-precheck.py:68-80`).
  - `chousa-shokunin` provides intra-directory atomic writes with cleanup (`build-spans.py:341-355`) and wave-level digest freeze checking (`freeze-check.py`).
  - `tsukuroi-shokunin` provides an existing `tools/receipt-write.py` tool, but it is unhardened (no atomic rename, no dirty-tree check, no overwrite refusal; direct write).
  - `mori-shokunin` enforces commit order on claim inputs (`mori-freeze-order.py`) and command presence in control receipts (`mori-control-receipt.py`).
  - `kagi-shokunin`, `kama-shokunin`, `kengaku-shokunin`, and `kumitate-shokunin` provide domain-specific freeze or replay audits.
- **Unrelated Holdings (10 lanes):** `audio`, `game-dev-2d`, `game-dev-3d`, `kake`, `kasegi`, `kotoba`, `lore`, `mado`, `revenger`, `tabi` hold no tooling or province ground overlapping either claim.

---

## 2. Exact Grep Commands & Observed Outputs

The scan queried all 20 sibling lanes across their `PROVINCE.md`, `SKILL.md` (present in 18 sibling lanes), and committed `tools/` (769 script files across 8 sibling lanes).

### Query 1: `atomic-write` (`atomic[-_]write`)
- **PROVINCE.md:** `grep -En 'atomic[-_]write' <sibling-lanes>/PROVINCE.md`  
  *Output:* 0 matches (exit 1).
- **SKILL.md:** `grep -En 'atomic[-_]write' <sibling-lanes>/SKILL.md`  
  *Output:* 1 match (exit 0):  
  - `/home/vgpnk/Projects/shokunin/kumitate-shokunin/SKILL.md:402`: `... token-plan probes' catalog + subprocess wiring, atomic-write.mjs's durable publish ...`
- **tools/:** `grep -rEIn 'atomic[-_]write' <sibling-lanes>/tools/`  
  *Output:* 6 matches (exit 0):  
  - `/home/vgpnk/Projects/shokunin/chousa-shokunin/tools/build-spans.py:341`: `def _atomic_write(dfd: int, name: str, data: bytes) -> None:`
  - `/home/vgpnk/Projects/shokunin/chousa-shokunin/tools/build-spans.py:372`: `_atomic_write(sfd, name.split("/", 1)[1], body.encode("utf-8"))`
  - `/home/vgpnk/Projects/shokunin/chousa-shokunin/tools/build-spans.py:373`: `_atomic_write(ofd, "spans.tsv", manifest)`
  - `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-42/fetch-carrier.py:260`: `def atomic_write(dirpath, name, writer, want_sha):`
  - `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-42/fetch-carrier.py:448`: `atomic_write(icache, want + '.image', ...)`
  - `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-42/fetch-carrier.py:504`: `target, replaced = atomic_write(cache, got + '.bin', ...)`

### Query 2: `rename` (`\brename\b`)
- **PROVINCE.md:** `grep -En 'rename' <sibling-lanes>/PROVINCE.md`  
  *Output:* 8 matches (exit 0):  
  - `kaidoku-shokunin/PROVINCE.md:316,323,325,328,337`: Renamed-copy evidence ID identity analysis (binary disassembly).
  - `kotoba-shokunin/PROVINCE.md:20,42`: Callee-rename-robust OMP surface extractor.
  - `tsukuroi-shokunin/PROVINCE.md:241`: Btrfs scrub status write via `_tmp`-then-rename under `flock`.
- **SKILL.md:** `grep -En 'rename' <sibling-lanes>/SKILL.md`  
  *Output:* 49 matches (exit 0). Examples:  
  - `chousa-shokunin/SKILL.md:102,728`: Matcher rename resilience in research gate witnesses.
  - `kagi-shokunin/SKILL.md:296`: Labeled secret rename tracking.
  - `tsukuroi-shokunin/SKILL.md`: Rename handling in package updates.
- **tools/:** `grep -rEIn 'rename' <sibling-lanes>/tools/`  
  *Output:* 298 matches (exit 0). Examples:  
  - `kaidoku-shokunin/tools/round-42/fetch-carrier.py:263`: `... rename over the final name ...`
  - `tsukuroi-shokunin/tools/check-path-reconciliation.py`: File movement checks.

### Query 3: `fsync` (`\bfsync\b`)
- **PROVINCE.md:** `grep -En 'fsync' <sibling-lanes>/PROVINCE.md`  
  *Output:* 0 matches (exit 1).
- **SKILL.md:** `grep -En 'fsync' <sibling-lanes>/SKILL.md`  
  *Output:* 0 matches (exit 1).
- **tools/:** `grep -rEIn 'fsync' <sibling-lanes>/tools/`  
  *Output:* 16 matches (exit 0):  
  - `kaidoku-shokunin/tools/round-42/fetch-carrier.py:53,263,291`: `os.fsync(fh.fileno())` before `os.replace`.
  - `kotodama-shokunin/tools/gates/provenance-audit.py:424`: `os.fsync(handle.fileno())` in `pin_fixtures()`.
  - `kotodama-shokunin/tools/gates/myth-consistency-gate.py:1076`: `os.fsync(handle.fileno())`.
  - `kotodama-shokunin/tools/gates/lexicon-coverage-audit.py:1460`: `os.fsync(handle.fileno())`.
  - `kotodama-shokunin/tools/gates/costume-era-consistency-gate.py:1498`: `os.fsync(handle.fileno())`.
  - `kotodama-shokunin/tools/gates/phonology-sanity-gate.py:1285`: `os.fsync(handle.fileno())`.
  - *(plus 7 frozen/expected historic copies in kotodama)*.

### Query 4: `preregistration` (`preregistration`)
- **PROVINCE.md:** `grep -En 'preregistration' <sibling-lanes>/PROVINCE.md`  
  *Output:* 2 matches (exit 0):  
  - `kengaku-shokunin/PROVINCE.md:61,161`: Notes fleet process discussion in round 11/12 regarding preregistration/replay gates (referred, not imposed).
- **SKILL.md:** `grep -En 'preregistration' <sibling-lanes>/SKILL.md`  
  *Output:* 19 matches (exit 0):  
  - `kama-shokunin/SKILL.md:1120,1326,1376,1422,1650,1675`: References to `.ufo/waves/round-N/preregistration.json` (JSON-formatted claim manifests for llama.cpp evaluation).
  - `kengaku-shokunin/SKILL.md:558,944`: References to experimental evaluation preregistration bundles.
  - `mado-shokunin/SKILL.md:2188`: Distinguishes raw truth from retroactive preregistration.
- **tools/:** `grep -rEIn 'preregistration' <sibling-lanes>/tools/`  
  *Output:* 69 matches (exit 0):  
  - `kama-shokunin/tools/round56-prereg-check.py:9,35`: Compares battery roster against `preregistration.json`.
  - `kama-shokunin/tools/round33-claim-audit.py`: Checks claims against preregistration JSON.

### Query 5: `freeze` (`\bfreeze\b`)
- **PROVINCE.md:** `grep -En 'freeze' <sibling-lanes>/PROVINCE.md`  
  *Output:* 45 matches (exit 0). Examples:  
  - `mori-shokunin/PROVINCE.md:132,564`: Core freeze-order verdicts (`tools/mori-freeze-order.py`).
  - `kaidoku-shokunin/PROVINCE.md:70,378,390,432`: Pre-data freeze discipline across firmware extractor rounds.
- **SKILL.md:** `grep -En 'freeze' <sibling-lanes>/SKILL.md`  
  *Output:* 427 matches (exit 0 across chousa, kaidoku, kama, kengaku, kotodama, mori, tsukuroi).
- **tools/:** `grep -rEIn 'freeze' <sibling-lanes>/tools/`  
  *Output:* 3131 matches (exit 0). Examples:  
  - `chousa-shokunin/tools/freeze-check.py`: Wave dispatch/spec/ready freeze gate.
  - `kaidoku-shokunin/tools/round-84/freeze-precheck.py`: Container claim counter-path freeze gate.
  - `mori-shokunin/tools/mori-freeze-order.py`: Claim inputs commit-order freeze gate.

### Query 6: `ancestry` (`ancestry|is-ancestor|merge-base`)
- **PROVINCE.md:** `grep -En 'ancestry|is-ancestor|merge-base' <sibling-lanes>/PROVINCE.md`  
  *Output:* 3 matches (exit 0):  
  - `kama-shokunin/PROVINCE.md:698`: Citation provenance ancestry requirement.
  - `tsukuroi-shokunin/PROVINCE.md:3514`: Master lineage ancestry.
- **SKILL.md:** `grep -En 'ancestry|is-ancestor|merge-base' <sibling-lanes>/SKILL.md`  
  *Output:* 25 matches (exit 0). Examples:  
  - `tameshi-shokunin/SKILL.md:1347`: `git merge-base --is-ancestor` in wave grant durability.
  - `mori-shokunin/SKILL.md:892`: Reachability relation via `git merge-base --is-ancestor`.
  - `tsukuroi-shokunin/SKILL.md:1974,3511`: Local branch ancestry in `tools/_revision.py`.
- **tools/:** `grep -rEIn 'ancestry|is-ancestor|merge-base' <sibling-lanes>/tools/`  
  *Output:* 182 matches (exit 0). Examples:  
  - `tameshi-shokunin/tools/receipt-revision-gate.py:75,173`: `is_ancestor()` enforcing `RECEIPT_CONTROL_NOT_ANCESTOR`.
  - `kaidoku-shokunin/tools/round-30/axis-fit-gate.py:258`: `git merge-base --is-ancestor`.
  - `tsukuroi-shokunin/tools/_revision.py:120`: Ancestry validation helper.

### Query 7: `receipt-writer` (`receipt[-_]write|record[-_]receipt`)
- **PROVINCE.md:** `grep -En 'receipt[-_]write|record[-_]receipt' <sibling-lanes>/PROVINCE.md`  
  *Output:* 0 matches (exit 1).
- **SKILL.md:** `grep -En 'receipt[-_]write|record[-_]receipt' <sibling-lanes>/SKILL.md`  
  *Output:* 25 matches (exit 0):  
  - `tsukuroi-shokunin/SKILL.md:4565,4566,4732,4842,4843,4987,4988,5109,5110,5252,5253,5365,5366,5478,5479,5590,5591,5726,5727,5879,5880`: Registration and usage of `tools/receipt-write.py` for raw service probe captures.
  - `kotodama-shokunin/SKILL.md:473`: Registration of `tools/harness/receipt_guard.py` as receipt-write preflight.
  - `kaidoku-shokunin/SKILL.md:1864,1926`: Registration of `record-receipt-audit.py` and `prefile-receipt.py`.
- **tools/:** `grep -rEIn 'receipt[-_]write|record[-_]receipt' <sibling-lanes>/tools/`  
  *Output:* 47 matches (exit 0):  
  - `tsukuroi-shokunin/tools/receipt-write.py:2,12,38`: `receipt-write` companion to `receipt-run.py`.
  - `kotodama-shokunin/tools/harness/receipt_guard_adoption.py`: Static analysis audit of receipt write sites.
  - `kaidoku-shokunin/tools/round-57/record-receipt-audit.py`: Resolves paths named in record sections.
  - `kaidoku-shokunin/tools/round-77/prefile-receipt.py`: Prefile gate wrapper writing execution receipt.

---

## 3. Sibling Overlap Table

| Sibling Lane | Relevant Artifact(s) | Verdict | Ground Held & Scope Analysis |
|:---|:---|:---:|:---|
| **audio-shokunin** | `PROVINCE.md` (mentions proxy receipts) | `none` | Dedicated to audio production (SFX, soundtracks); holds no freeze or receipt writing tools. |
| **chousa-shokunin** | `tools/freeze-check.py`<br>`tools/build-spans.py:341`<br>`tools/parent-lifetime.sh`<br>`tools/receipt-pin.py` | `complementary` | `freeze-check.py` validates wave dispatch/spec/ready sha256 binding to `claims.md`, but does not inspect claim blocks or bind `Control:` receipts to `Counter` bytes. `build-spans.py` implements intra-directory atomic writes with `O_CREAT\|O_EXCL\|O_NOFOLLOW` and cleanup, but for span manifests, not receipts. `parent-lifetime.sh` writes receipts via raw `>` redirection. |
| **game-dev-2d-shokunin** | `PROVINCE.md` | `none` | 2D game development (Godot 4.7.2); holds no freeze or receipt tooling. |
| **game-dev-3d-shokunin** | `PROVINCE.md`, `SKILL.md` (bounded fixture receipts) | `none` | 3D engines; specifies receipt requirements for `verified-here` labels, but has no tools directory or receipt writing tooling. |
| **kagi-shokunin** | `corpus/prefreeze-control.sh`<br>`corpus/release-clock.py` | `complementary` | `prefreeze-control.sh` executes controls on extracted `--base <rev>` trees from a TSV, verifying integer results; does not inspect preregistration claim blocks or provide an atomic receipt writer. |
| **kaidoku-shokunin** | `tools/round-84/freeze-precheck.py`<br>`tools/round-77/prefile-receipt.py`<br>`tools/round-42/fetch-carrier.py:260`<br>`tools/round-57/record-receipt-audit.py` | `complementary` | `round-84/freeze-precheck.py` checks that claim objects name counter paths and pin them in container JSON, but does not check `Control:` receipts. `fetch-carrier.py:260` implements hardened atomic writing with `fsync`, `O_NOFOLLOW`, `os.replace`, and cleanup, but for carrier binary caching. `prefile-receipt.py` writes receipts via standard unhardened `open(..., 'w')`. |
| **kake-shokunin** | `PROVINCE.md`, `SKILL.md` | `none` | Web publishing and documentation; holds no relevant tools. |
| **kama-shokunin** | `tools/prereg-time-check.py`<br>`tools/round56-prereg-check.py`<br>`tools/kama-live-replay.py:179` | `complementary` | `prereg-time-check.py` checks false timestamps in preregistrations against git commit times; `round56-prereg-check.py` compares battery AST against `preregistration.json`. `kama-live-replay.py` replaces archives after fetch. None binds Control receipts or writes receipts atomically. |
| **kasegi-shokunin** | `PROVINCE.md`, `SKILL.md` | `none` | Bounty and security research; holds no receipt writing or freeze tooling. |
| **kengaku-shokunin** | `plans/receipt_consistency_check.py`<br>`PROVINCE.md:827` | `complementary` | Evaluates LLM benchmarks; audits self-consistency of test receipts (`plans/receipt_consistency_check.py`), but does not implement substance binding or atomic receipt writers. |
| **kotoba-shokunin** | `PROVINCE.md:75` (acknowledges souji) | `none` | Prompt and skill craft; explicitly recognizes souji's province over receipt-gated hygiene. Holds no tools directory. |
| **kotodama-shokunin** | `tools/harness/receipt_guard.py`<br>`tools/harness/receipt_guard_adoption.py`<br>`tools/gates/provenance-audit.py:424` | `complementary` | `receipt_guard.py` is the canonical receipt preflight guard: checks `st_nlink == 1`, refuses symlinks (`S_ISLNK`), checks within-repo boundaries, and blocks overwriting committed receipts unless `REFRESH_RECEIPTS=1`. However, it is a preflight validator, not an execution-wrapping atomic writer. `provenance-audit.py` uses tempfile+fsync+rename for fixture regeneration, refusing overwrite if divergent. |
| **kumitate-shokunin** | `SKILL.md:402` (cites `atomic-write.mjs`)<br>`scripts/report-receipt-diff.mjs` | `complementary` | Orchestrator and runtime tooling; governs wave lifecycle and receipt comparison across fleet reports, but provides no lane-level receipt writer or preregistration substance tool. |
| **lore-shokunin** | `PROVINCE.md` (CM-01 through CM-12) | `none` | World bible and consistency ledger; holds no tools directory. |
| **mado-shokunin** | `tools/mado-receipt-citecheck.py` | `none` | Desktop window management; checks receipt citations in documentation; does not write receipts or bind freeze records. |
| **mori-shokunin** | `tools/mori-freeze-order.py`<br>`tools/mori-control-receipt.py`<br>`tools/mori-receipt-complete.py` | `complementary` | `mori-freeze-order.py` checks whether claim inputs predate implementation commits using git topology on `mori-freeze-register-v1` JSON registers. `mori-control-receipt.py` requires control receipts with integer counts to carry a counting command line. Does not parse souji's preregistration format or write receipts atomically. |
| **revenger-shokunin** | `PROVINCE.md`, `SKILL.md` | `none` | Reverse engineering forensics; holds no tools directory. |
| **tabi-shokunin** | `PROVINCE.md`, `SKILL.md` | `none` | Headless browser testing; produces Playwright trace receipts; holds no tools directory. |
| **tameshi-shokunin** | `tools/receipt-revision-gate.py`<br>`tools/receipt-bytes-bind.py`<br>`tools/receipt-commit-bind.py` | `complementary` | Closest verification analogue: `receipt-revision-gate.py:172-175` enforces `RECEIPT_CONTROL_NOT_ANCESTOR` using `git merge-base --is-ancestor` for control receipts. `receipt-bytes-bind.py:65-75` binds recorded `# tool_sha256:` to committed blobs at `# measured_rev:`. However, these are post-hoc evidence checkers over `.ufo/evidence/`, not a pre-registration freeze validator or receipt writer. |
| **tsukuroi-shokunin** | `tools/receipt-write.py:52-67`<br>`tools/receipt-run.py:128-132`<br>`tools/run-receipt.py:103-108` | `complementary` | Shares the tool name `receipt-write.py` (writes captured output into `receipt-run` format via `shared.write_receipt()`). However, its write is unhardened: opens the destination file directly (`with dest.open("wb") as fh:`), lacks atomic rename, lacks dirty-tree check, and does not refuse overwrites. |

---

## 4. Deep-Dive: Committed Tools vs. Round 60 Claims

### 4.1 Claim C1: Freeze-Record Substance Binding
**Check:** Does any committed tool in any lane implement `--substance` binding a claim's `Control:` receipt to the declared `Counter` bytes and to a pre-freeze revision?

**Findings by Candidate:**
1. **`chousa-shokunin/tools/freeze-check.py` (lines 35–60):**
   - Implements `CLAIMS_NONEMPTY`, `CONTEXT_DIGEST`, `DIGEST_STRAY`, `CONTEXT_SPEC_EQ`, `NAMES`, `BODY_RENDER`, `READY_DISPATCH`, `READY_IDENT`.
   - *Distinction:* Validates that the wave spec and dispatch payloads carry the SHA-256 of `claims.md`. Does not inspect claim blocks (`## C1`), does not read `preregistration.txt`, and does not bind `Control:` receipts.
2. **`kaidoku-shokunin/tools/round-84/freeze-precheck.py` (lines 68–80):**
   - Checks `CLAIM_NO_COUNTER_PATH`, `COUNTER_BLOB_ABSENT`, `COUNTER_PATH_NOT_PINNED`, `COUNTER_PIN_MISMATCH`.
   - *Distinction:* Checks that JSON claim objects name a counter script path and that the container JSON pins the counter blob at `--rev`. Does not validate `Control:` receipts or check pre-freeze ancestry.
3. **`tameshi-shokunin/tools/receipt-revision-gate.py` (lines 172–175):**
   - Validates `RECEIPT_CONTROL_NOT_ANCESTOR` via `is_ancestor(lane, full, certified)`.
   - *Distinction:* Verifies that revisions mentioned inside an existing receipt file are ancestors of a certified commit. Does not parse preregistration files, does not check that `instrument=` matches `Counter:`, and does not check that `instrument_sha256=` matches the Counter blob at freeze.
4. **`mori-shokunin/tools/mori-freeze-order.py` (lines 171–230):**
   - Checks whether frozen inputs in `mori-freeze-register-v1` predate implementation commits using `diff-tree`.
   - *Distinction:* Operates on a dedicated JSON register format, checking commit chronology, not receipt contents or counter blob digests.

**Verdict:** **NO committed sibling tool implements the substance check.** Ground is held exclusively by `souji-shokunin`.

---

### 4.2 Claim C2: Hardened Atomic Receipt Writing
**Check:** Does any committed tool in any lane implement a hardened receipt writer (`tools/souji-receipt-write.py` contract: atomic temp+rename, refuse overwrite, refuse dirty tree, bounded output, rev/instrument checks)?

**Findings by Candidate:**
1. **`tsukuroi-shokunin/tools/receipt-write.py` (lines 52–67) & `receipt-run.py` (lines 128–132):**
   - `write_receipt` implementation:
     ```python
     def write_receipt(path: str, blob: bytes) -> None:
         dest = Path(path)
         dest.parent.mkdir(parents=True, exist_ok=True)
         with dest.open("wb") as fh:
             fh.write(blob)
     ```
   - *Distinction:* Direct file write (`dest.open("wb")`). Lacks atomic rename; will clobber pre-existing files without warning; does not check worktree cleanliness (`git status`); does not enforce output byte bounds; does not validate git revisions or instrument blobs.
2. **`kotodama-shokunin/tools/harness/receipt_guard.py` (lines 161–240):**
   - Enforces preflight safety: verifies target is a singly-linked regular file (`info.st_nlink == 1`), refuses symlink targets (`stat.S_ISLNK(info.st_mode)`), checks destination is inside the repository root (`candidate.relative_to(root)`), and refuses overwriting committed receipts without `REFRESH_RECEIPTS=1`.
   - *Distinction:* A validation guard, not a writer. It does not execute commands, does not write files, does not enforce byte bounds, and does not check dirty worktrees.
3. **`kaidoku-shokunin/tools/round-42/fetch-carrier.py` (lines 260–310):**
   - `atomic_write` implementation:
     ```python
     cand = os.path.join(dirpath, '.%s.tmp-%d-%s' % (name, os.getpid(), os.urandom(6).hex()))
     fd = os.open(cand, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
     with os.fdopen(fd, 'wb') as fh:
         writer(fh)
         fh.flush()
         os.fsync(fh.fileno())
     os.replace(tmp, final)
     ```
   - *Distinction:* Written specifically for caching downloaded binary carriers (firmware images). Does not record command execution, exit codes, git revisions, or enforce worktree cleanliness.
4. **`chousa-shokunin/tools/build-spans.py` (lines 341–355):**
   - `_atomic_write` using `dir_fd`, `O_CREAT | O_EXCL | O_NOFOLLOW`, `os.replace`, and cleanup on exception.
   - *Distinction:* Written for internal cache manifest publishing; does not record subprocess execution receipts.

**Verdict:** **NO committed sibling tool implements the hardened atomic receipt writer.** Ground is unoccupied across the fleet.

---

## 5. Design Decision to Copy from a Sibling

### Selected Decision
**Adopt the Intra-Directory O_EXCL + fsync + os.replace Atomic Pattern with Symlink/Hardlink Pre-Check** from `kaidoku-shokunin/tools/round-42/fetch-carrier.py:260-310` and `kotodama-shokunin/tools/harness/receipt_guard.py:195-202`.

### Specification of the Pattern for `tools/souji-receipt-write.py`
1. **Intra-Directory Temporary Sibling (Prevents `EXDEV`):**
   - Do NOT use standard `/tmp` or an arbitrary `tempfile.NamedTemporaryFile()` default. Placing the temporary file in `/tmp` when `OUT` is located on a different mount (e.g. `/fast/scratch` or a separate workspace drive) causes `os.replace()` to fail with `OSError: [Errno 18] Invalid cross-device link` (`EXDEV`).
   - Derive the temporary file path strictly within the destination directory:
     ```python
     out_dir = os.path.dirname(os.path.abspath(out_path))
     os.makedirs(out_dir, exist_ok=True)
     tmp_name = f".{os.path.basename(out_path)}.tmp-{os.getpid()}-{secrets.token_hex(6)}"
     tmp_path = os.path.join(out_dir, tmp_name)
     ```
2. **Symlink and Overwrite Refusal via `lstat` (`kotodama` pattern):**
   - Before creating any temporary file or executing the probe command, inspect `OUT` with `os.lstat()`:
     ```python
     try:
         st = os.lstat(out_path)
         # If it exists (even as a broken symlink), refuse overwrite
         sys.stderr.write(f"refused: output path already exists: {out_path}\n")
         return 2
     except FileNotFoundError:
         pass
     ```
   - This prevents TOCTOU exploits where an attacker plants a symlink to an out-of-scope file (e.g. `/etc/passwd` or repository configs) that `os.replace()` would otherwise overwrite.
3. **Safe Creation, Flush, Durability, and Atomic Rename (`kaidoku` pattern):**
   - Create with exclusive flags: `os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)`.
   - Flush userspace buffers and synchronize kernel disk buffers: `fh.flush(); os.fsync(fh.fileno())`.
   - Perform atomic replacement: `os.replace(tmp_path, out_path)`.
   - Ensure clean removal of `tmp_path` in a `finally:` block (and via signal handlers) if any exception or interrupt occurs prior to successful rename.

---

## 6. UFO-FSD Connector Synthesis: One Non-Obvious Move

### Context & Conflict Analysis
- **Declared Axes in Round 60:** **Calibration (C1)** and **Operability (C2)**.
- **Contract Boundary:**
  - C1 extends `tools/souji-freeze-check.py` with `--substance` to inspect a claim's `Control:` receipt blob at `FREEZE`. It requires finding classes: `CONTROL-INSTRUMENT-MISSING`, `CONTROL-INSTRUMENT-MISMATCH`, `CONTROL-REV-MISSING`, `CONTROL-REV-INVALID`, `CONTROL-REV-NOT-BEFORE-FREEZE`, `CONTROL-COMMAND-MISSING`, `CONTROL-COMMAND-MISMATCH`.
  - C2 creates `tools/souji-receipt-write.py` to record commands and output into a receipt file carrying `instrument=`, `instrument_sha256=`, `rev=`, `command=`, output, and `EXIT=<rc>`.
- **The Latent Contradiction / Vulnerability:**
  If `souji-receipt-write.py` simply echoes command output into the receipt body without strict structural framing, commands whose stdout legitimately contains lines matching `instrument=...` or `rev=...` (such as self-testing checkers or git logging commands) will introduce ambiguous key lines. Conversely, if `souji-freeze-check.py --substance` scans the entire receipt blob using an unanchored regex or whole-file line search, a forged control receipt can embed fake `instrument=` and `rev=` lines inside stdout while executing a completely different command, fooling the substance check.

### Proposed Move: Strict Four-Line Header Fencing with Normalized Relative-Path Binding
Synthesize the C1 validator contract and the C2 writer contract into a mutually reinforcing, non-circular protocol:

1. **In `tools/souji-receipt-write.py` (C2):**
   - Write exactly a four-line header at column 0 before any command output:
     ```text
     instrument=<repo-relative-path>
     instrument_sha256=<64-hex>
     rev=<40-hex>
     command=<shlex-quoted-command>
     ```
   - Normalize the instrument path: Convert `--instrument` to a canonical repo-relative path (`os.path.relpath(path, root)`), rejecting absolute or traversing paths (`..`).
   - Single-line command constraint: Shlex-quote the command or join argv elements such that `command=` is guaranteed to occupy exactly one line, preventing multiline injection into the header block.
2. **In `tools/souji-freeze-check.py --substance` (C1):**
   - Parse the `Control:` receipt blob by extracting header fields strictly from the top of the file up to the first non-header line or output delimiter.
   - Enforce **strict ancestry** using `rev != freeze and repo.is_ancestor(rev, freeze)` (derived from `tameshi-shokunin/tools/receipt-revision-gate.py:155,173`), preventing the subtle cheat where `merge-base --is-ancestor` returns True when `rev == freeze`.
   - Match `command=` against the declared `Counter:` path using token boundary recognition (e.g. `path in shlex.split(cmd_line)`) rather than loose substring matching, preventing substring false positives (e.g. matching `tools/foo.py` against `tools/foo.py.bak`).

### Trace of Second-Order Effects
- **Runtime Surface:** Zero impact on tool runtime overhead; header parsing is $O(1)$ over the first four lines. Intra-directory atomic write eliminates `EXDEV` failures on scratch mounts.
- **Contract Surface:** Resolves the grammar ambiguity between `record-receipt.sh` (which omitted `command=`) and `souji-freeze-check.py` without requiring secondary schema files.
- **Substrate Surface:** Hardened against cross-device links and symlink tampering on Linux, Windows/MSYS, and BSD filesystems.
- **Verification Surface:** Falsification test suites (such as `S60ReviewerFreeze` and `S60ReviewerRecorder`) can deterministically test header truncation and command parsing without brittle line-number assumptions.

### Affected Axes
- **Calibration (C1):** **Improved.** Eliminates false-positive passes where stdout mimics header metadata; guarantees that control receipts are strictly pre-freeze.
- **Operability (C2):** **Improved.** Hardens the receipt writer against disk-full errors, partial writes, symlink hijacking, and `EXDEV` cross-mount crashes.
- **Depth / Adjacency:** **Improved.** Bridges the gap between git object inspection and runtime filesystem guarantees without encroaching on sibling provinces.
- **Harmed Axes:** **None.** Both claims remain causally separable; C1's matrix can be scored without running C2, and C2's fixture can be verified independently.

### Risks & Mitigations
- **Risk:** Commands that emit ANSI escapes, binary data, or huge stdout could exceed memory limits.
  *Mitigation:* C2's `--max-bytes` parameter (default 256 KiB) terminates read and unlinks the temporary file before rename.
- **Risk:** Clock skew or rebasing changing commit timestamps.
  *Mitigation:* Pre-freeze validation relies strictly on git graph ancestry (`merge-base --is-ancestor`), not commit timestamps or mtimes.

### Verification Plan
1. **C1 Matrix Verification:** Execute `python3 -B c1-counter.py` on the 8-case matrix:
   - 3 honest accept cases pass.
   - 5 forgery refuse cases (`CONTROL-INSTRUMENT-MISSING`, `CONTROL-INSTRUMENT-MISMATCH`, `CONTROL-REV-MISSING`, `CONTROL-REV-NOT-BEFORE-FREEZE`, `CONTROL-COMMAND-MISMATCH`) fail with exact named findings.
2. **C2 Fixture Verification:** Execute `python3 -B r60-receipt-write.py --tool tools/souji-receipt-write.py --work <scratch>`:
   - All 8 fixture cases (clean write, overwrite refusal, in-flight atomicity, kill residue, output bound, short rev, absent instrument, dirty tree) pass.
3. **Cross-Check:** Run `souji-freeze-check.py --substance` against a control receipt generated directly by `souji-receipt-write.py` to confirm end-to-end acceptance.
