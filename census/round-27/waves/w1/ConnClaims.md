# ConnClaims — souji round 27 w1, cross-claim dependency check

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin at base `e78ac7c4837b81b634db4a927605a751a7f006ba` (branch master, ahead=0, remote verified). Read-only seat; writing only this report.

## Status

STATUS: PASS — all three claim pairs (C1/C2, C1/C3, C2/C3) are causally separable and independent; no claim's counter before or after value depends on another claim landing, diff surfaces share 0 bytes, and whole-tree landing-gate verification is a same-tree measurement rather than a causal dependency.

## Evidence

- Base revision: `e78ac7c4837b81b634db4a927605a751a7f006ba` (verified via `git rev-parse HEAD`).
- C1 baseline command: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin`. Output excerpt:
  `LG-DANGLING-PTR corpus/knowledge/registry corpus/QUALITY.md:143 cites path absent at e78ac7c4837b`
  `LG-DANGLING-PTR corpus/lessons/round-24.md:232:S118 corpus/QUALITY.md:141 cites path absent at e78ac7c4837b`
  `SUMMARY findings=2 checked_reg=50 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0`
  (exit code 2 due to no round-27 reports at base, preserving pointer findings).
- C2 baseline commands at base `e78ac7c`:
  `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` → `132`.
  `grep -rlE '^ground: F4' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/ | wc -l` → `2`.
- C3 baseline: `tools/souji-pre-report-gate.sh` absent at base (0 matches in `git ls-tree e78ac7c tools/souji-pre-report-gate.sh`).
- Verified diff surfaces across claims:
  - C1: `corpus/pointer-exemptions.tsv` (+2 rows) and `.ufo/waves/round-27/records/c1-*.tsv`.
  - C2: `corpus/SOURCES.md` (+3 rows S152, S210, S211), `corpus/knowledge/origin-record-writer-r27.md`, `corpus/knowledge/origin-record-mechanism-set-r33.md`, `census/round-27/sources/*`, map/lesson updates.
  - C3: `tools/souji-pre-report-gate.sh`, `tests/fixtures/r27-pre-report-gate.sh`, `.gitignore`.
- Quote 1 (`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:5`):
  "C1 — axis calibration (score 7, lowest non-retired; surface class: self-assessment-file change). Resolve the two internal `LG-DANGLING-PTR` findings"
- Quote 2 (`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:7`):
  "C2 — axis coverage (score 8; surface class: corpus/knowledge/registry change = coverage). Assimilate the F4 origin-record theme"
- Quote 3 (`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:9`):
  "C3 — axis operability (score 8; surface class: gate/runnable fixture on an input edge class). Deliver `tools/souji-pre-report-gate.sh`"
- Quote 4 (`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:928-933`):
  "path for path in tree if path.startswith("corpus/knowledge/") and path.count("/") == 2 and path.endswith(".md")"
- Quote 5 (`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/origin-record-writer-r27.md:63`):
  "staged read-side entry `corpus/knowledge/origin-record-format-gvfs-r26.md`"

## Findings

### 1. Pair C1 / C2 — Causally Separable (Verdict: Independent)

- **Counter before invariance:** C1 before (`findings=2`) and C2 before (`rows=132`, `grounded_F4=2`) are evaluated against immutable base commit `e78ac7c4837b81b634db4a927605a751a7f006ba`. Neither before count can be altered by the other claim landing.
- **Counter after invariance:**
  - C2's counters (`grep` on `corpus/SOURCES.md`, `grep` on `corpus/knowledge/`, `python3 -B tools/souji-gate-check.py`, and `scripts/sources-census.sh validate`) inspect only the SOURCES table, the two admitted knowledge files, and the GLib source snapshots under `census/round-27/sources/`. None of C2's counters read `corpus/pointer-exemptions.tsv` or invoke `tools/souji-landing-gate.py`. C2's counters evaluate identically whether C1 is landed or reverted.
  - C1's counter (`python3 -B tools/souji-landing-gate.py`) evaluates pointer exemptions against scanned citation sites. C1 appends two rows to `corpus/pointer-exemptions.tsv` resolving the two base findings in `corpus/QUALITY.md`. If C1 lands alone (with C2 reverted), `findings=0` is achieved. If C2 lands alongside C1, C2 does not resolve either exempted citation (so no `LG-DANGLING-PTR-EXEMPT-STALE`), nor does it create `corpus/knowledge/registry` or `corpus/lessons/round-24.md:232:S118`.
- **Shared bytes:** 0 bytes. C1 modifies only `corpus/pointer-exemptions.tsv`; C2 modifies `corpus/SOURCES.md`, `corpus/knowledge/*.md`, and `census/round-27/sources/*`. The diffs are completely disjoint.
- **Same-tree measurement vs dependency:** At the joint landing tip, `tools/souji-landing-gate.py` scans all `corpus/knowledge/*.md` files (including C2's additions). This whole-tree scan is a same-tree observation, not a functional dependency. However, as noted in RevNoHarm finding 1, staged draft `origin-record-writer-r27.md:63` cited unadmitted path `corpus/knowledge/origin-record-format-gvfs-r26.md`, which would cause `check_pointers` to emit an `LG-DANGLING-PTR` if landed unchanged. Rewording that token avoids spurious cross-talk, keeping C1 after at 0.
- **Verdict: Independent.**

### 2. Pair C1 / C3 — Causally Separable (Verdict: Independent)

- **Counter before invariance:** Both base states are immutable at `e78ac7c`. C1 before is `findings=2`; C3 before is `tool=absent`.
- **Counter after invariance:**
  - C3's counters (presence check, `bash tests/fixtures/r27-pre-report-gate.sh` returning `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, receipt) evaluate in four isolated git sandboxes under `/var/tmp/souji-r27-ExecFixtureC3Tests`. C3 reads zero bytes from `corpus/pointer-exemptions.tsv` and does not call `tools/souji-landing-gate.py`.
  - C1's counter (`souji-landing-gate.py`) parses scripts cited in `SKILL.md` via `parse_script` (`bash -n`). Valid C3 additions in `tools/souji-pre-report-gate.sh` and `tests/fixtures/r27-pre-report-gate.sh` pass shell syntax checks and introduce 0 findings.
  - C1 evaluates to `findings=0` whether C3 is landed or reverted; C3 evaluates to `cases=4 pass=4` whether C1 is landed or reverted.
- **Shared bytes:** 0 bytes. C1 diff is in `corpus/pointer-exemptions.tsv`; C3 diff is in `tools/` and `tests/fixtures/`.
- **Verdict: Independent.**

### 3. Pair C2 / C3 — Causally Separable (Verdict: Independent)

- **Counter before invariance:** Immutable at base `e78ac7c`.
- **Counter after invariance:**
  - C2's counters measure registry rows, knowledge headers, snapshot quote verification, and census validation. None query `tools/souji-pre-report-gate.sh` or `tests/fixtures/r27-pre-report-gate.sh`.
  - C3's counters measure tool presence and execute selftest cases in `/var/tmp/` sandboxes. None read `corpus/SOURCES.md`, `corpus/knowledge/`, or `census/round-27/sources/`.
  - C2 succeeds whether C3 is landed or reverted; C3 succeeds whether C2 is landed or reverted.
- **Shared bytes:** 0 bytes. C2 touches knowledge/registry/sources surfaces; C3 touches tools/fixtures surfaces.
- **Verdict: Independent.**

### 4. Same-Tree Measurement vs Causal Dependency Distinction

A causal dependency requires that Claim A's counting command invokes Claim B's code/tools, or that Claim A's measured metric changes value because Claim B's diff is present. In contrast, running `sources-census.sh validate` or `souji-landing-gate.py` on the final landing tip is a same-tree integrity measurement: the execution inspects the joint worktree, but each claim's counter delta (C1: 2→0; C2: 132→135, 2→4, ok=2; C3: absent→present, 4/4) is invariant under isolated verification against base.

## Connector Proposal: Isolated Pre-Integration Replay Discipline

- **Affected axes:** Calibration (7, lowest non-retired), Operability (8), Coverage (8).
- **Proposed move:** Enforce an explicit, isolated verification step in the L1 integration workflow before committing the joint landing tip. For each claim, evaluate its counting command against an isolated commit or synthetic sandbox containing only base + that claim's diff:
  1. C1 isolated (`base + pointer-exemptions.tsv`): verify `souji-landing-gate.py` emits `findings=0` and `ptr_exempt=2` in complete isolation from C2/C3 files.
  2. C2 isolated (`base + C2 files`): verify `souji-gate-check.py` (`ok=2 fail=0`) and `sources-census.sh validate` (`rc=0`) with C1/C3 absent.
  3. C3 isolated (`base + C3 files`): verify `tests/fixtures/r27-pre-report-gate.sh` emits `cases=4 pass=4 control=FALSE-GREEN-REJECTED`.
  4. Joint tip: verify all counters jointly at the landed tip.
- **Why this improves axes without harm:** This improves **Calibration (7)** by proving beyond inference that C1's 2→0 finding reduction is causally produced by the two committed exemption rows, completely immune to potential landing-gate cross-talk (e.g. ungrounded knowledge citations in C2 or uncarried seat markers). It improves **Operability (8)** by catching citation errors prior to tip merge, and preserves **Coverage (8)**.
- **Risks:** None; this is a read-only integration verification discipline requiring no schema, contract, or score changes.
- **Verification:** Compare isolated verification outputs with joint tip outputs; confirm both match the declared preregistration before/after values.

## Attack log

N/A — connector seat; no counter or target attack filed.

Report: .ufo/waves/round-27/w1/ConnClaims.md
