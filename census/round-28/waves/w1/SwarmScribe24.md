# Souji round 28 — round report DRAFT (attempt 1, wave w1)

Scribe seat `SwarmScribe24` (UFO-FSD). This file contains (A) the drafted round report per the orchestrator's section order, and (B) this seat's scoped findings.

> Landing note: the orchestrator asked for the draft at `census/round-28/records/report-draft.md`. This seat is read-only outside `.ufo/waves/round-28/w1/`, so the draft is delivered here for the L1 (the only integrator/committer) to land at that path verbatim, replacing the `[AFTER]` markers with measured values at wave end.

---

# Souji round 28 — attempt 1 (v2 wave w1)

## Work performed

Declared claims (distinct axes; at least one on the lowest non-retired axis = calibration 7): **C1 calibration (7)** — correct the stale Q57/Q59 composite-site citations the frozen landing-gate counter reports at base; **C2 coverage (8)** — assimilate the F4 origin-record-primitives theme from `/home/vgpnk/Projects/shokuknow/merge/souji/`; **C3 operability (8)** — resolve the routed `.ufo/waves` evidence-leftover defect with a new instrument + runnable fixture. One v2 wave (build + attack together), 64 seats spawned (`w1-dispatch.json` counts spawn=64 resume=0 total=64), attempt 1.

- **C1**: landing-gate findings `2 → 0`, no exemption rows. (a) Q57 cell (QUALITY.md:141) enumerated-site syntax forms pseudo-path token `corpus/lessons/round-24.md:232:S118`; refactor site list into committed `census/round-28/q57-sites.txt` and point the cell's second mapping argument at committed authority `census/round-24/records/slice-verdicts.tsv` (the uncommittable `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` copy is dropped from the command). (b) Q59 criterion-body token (QUALITY.md:143) `corpus/knowledge/registry` reworded to `knowledge-registry`.
- **C2**: admit `corpus/knowledge/origin-record-exclusivity-r28.md` (re-grounded this round from POSIX.1-2024 `open()`) and `corpus/knowledge/origin-record-durability-r28.md` (re-grounded from POSIX.1-2024 `fsync()`); each carries a `## Gate` section with ≥1 admit and ≥1 reject from the staged set; each cites an appended SOURCES row opened this round (S212 = open(), S213 = rename(), S214 = fsync(); status=mined, used-by exactly the admitted entries, 11-column fleet census schema). Dispose the routed staged S119 zh-Hans `git-fetch(1)` edition: decision-time snapshot fetch today, sha256 pin, ≤25-word quote; ADMIT → append S215 (used-by `corpus/knowledge/git-auto-maintenance-trigger-set.md`); REJECT → keep staged (reason + flip in the lesson Gate). Re-run the F4 source recheck (verify r27 GLib snapshot digests still match committed `census/round-27/sources/SHA256SUMS`).
- **C3**: deliver `tools/souji-wave-evidence-capture.sh` (byte-exact copy + `manifest.sha256` + `summary.tsv`; bounded, read-only over source, verifies manifest, refuses special files/escaping) with fixture `tests/fixtures/r28-wave-evidence-capture.sh` (positive + tamper-negative controls); run for rounds 26 and 27 (and 28 at round end); add `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/` to lane `.gitignore`; after capture, revert tracked r26 wave modifications to HEAD (bytes preserved in capture).

## Landed changes

At draft time the wave is mid-flight; the only lane commit past the frozen base is the freeze commit:

- `0c96332932e66bbaf9cf1c246091d3275a0ab612` "round-28: frozen preregistration + before receipts + do-nothing controls" (11 files, +342): `census/round-28/records/preregistration.txt`, before receipts `c1/c2/c3-before.tsv`, controls `c1/c2/c3-control.tsv`, `axis-check-before.txt`, assimilation proofs `records/assimilation/reg-ids` (135), `staged-ids` (134), `collisions` (27).
- On disk, uncommitted at draft time: `.gitignore` (three required patterns), `census/round-28/q57-sites.txt` (4 site lines), `census/round-28/c1-counter.sh`, `census/round-28/records/c1-run-base.tsv`.
- Wave dir `souji-shokunin/.ufo/waves/round-28/w1/` already holds dispatch spec/registry, `snapshots/{open,rename,fsync}.html` (decision-time fetches for S212–S214), draft entry files, `slice-verdicts.tsv`, `quarantine-slice.tsv`, `r26-leftovers-inventory.tsv`.
- Claim deltas land at wave end by the L1 [AFTER].

## Before → after measurements

Frozen counters (preregistration.txt MACHINE BLOCK), base values from `census/round-28/records/*-before.tsv` at lane base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`:

| Claim | Counter (frozen) | Before (base) | After (tip) |
|---|---|---|---|
| C1 | `python3 -B tools/souji-landing-gate.py --root <lane> --rev <full40> --round 28 --fleet-root <fleet>` → SUMMARY `findings=N` | findings=2 (checked_reg=52; c1_rc=2); findings: LG-DANGLING-PTR corpus/knowledge/registry ← QUALITY.md:143; corpus/lessons/round-24.md:232:S118 ← QUALITY.md:141 | findings=0 [AFTER] |
| C2 | `grep -cE '^ground: F4' corpus/knowledge/*.md` | 4 | 6 [AFTER] |
| C2 | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` | 135 | 138 [AFTER] (S119 row, if appended, not counted) |
| C2 | `python3 -B tools/souji-gate-check.py` | — (target entries gate ok=2, fail=0) | ok=2 [AFTER] |
| C2 | `sources-census.sh validate` | — | exit 0 [AFTER] |
| C2 | `python3 -B tools/souji-coverage-agreement.py --root . --rev <tip>` | — | grounded/mapped=6/6, dangling=0, mismatches=0 [AFTER] |
| C3 | `git status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'` | 163 | 0 [AFTER] |
| C3 | `test -s census/round-26/waves/manifest.sha256 && test -s census/round-27/waves/manifest.sha256` | manifests 26/27 absent | present and non-empty [AFTER] |
| C3 | `bash tests/fixtures/r28-wave-evidence-capture.sh` | — | cases=6 pass=6 control=TAMPER-REJECTED, rc 0 [AFTER] |
| axes | `souji-axis-check.py` (R1–R4) | claims=3 flags=0, rc 0 (`axis-check-before.txt`) | flags=0 [AFTER] |

Controls: `c1/c2/c3-control.tsv` reproduce the before values byte-identically (do-nothing controls). Kill rules (frozen): C1 — any remaining finding or an exemption row used to clear one fails; C2 — gate/census nonzero, map mismatch, or used-by citing an unadmitted entry fails; C3 — any remaining dirty `.ufo/waves` path, missing/non-verifying manifest for a claimed round, or unreported control fails.

## Sources & frontier

- `corpus/SOURCES.md` holds 135 rows at base (last id S211). This round appends **S212 open()**, **S213 rename()**, **S214 fsync()** — POSIX.1-2024 (IEEE Std 1003.1-2024, pubs.opengroup.org/onlinepubs/9799919799/functions/{open,rename,fsync}.html), status=mined, used-by exactly the two admitted F4 entries, 11-column fleet census schema (header at SOURCES.md:20). Decision-time snapshots for the three pages are already fetched into `.ufo/waves/round-28/w1/snapshots/`.
- Staged **S119 zh-Hans git-fetch(1) edition** (`merge/souji/SOURCES.append.md` line 17: git-scm zh_HANS-CN, opened 2026-10-23, used-by `git-auto-maintenance-trigger-set.md`) — routing decision pending decision-time pin [AFTER].
- Frontier: F4 chain S022→S152→S210→S211 (writer/mechanism) gains the two POSIX primitive entries (exclusivity O_EXCL+rename, durability fsync); staged entry front matter confirms re-grounding this round: "ground: F4 — restorable quarantine (the two POSIX guarantees a per-item origin record needs: exclusive creation and atomic publication)" (`origin-record-exclusivity-r28.md:6`) and "ground: F4 — restorable quarantine (the durability guarantee a published origin record needs, and the limit on what any guarantee can promise)" (`origin-record-durability-r28.md:5`). F4 source recheck vs `census/round-27/sources/SHA256SUMS` [AFTER].

## Trend verdicts

- **expansion — improved:** two added F4 knowledge entries on new-ground; registry 135→138. (Measured [AFTER].)
- **quality — improved:** stale self-assessment citations (Q57/Q59) corrected; C3 instrument + 6-case fixture; r27 stance carried over ("both entries re-grounded against SHA-256 and Git-blob-verified GLib 2.84.0 snapshots"). (Measured [AFTER].)
- **discernment — improved:** S119 decision-time disposition closes the r27 "remains rejected pending a decision-time pinned snapshot" gap. (Measured [AFTER].)

## SHONEN

- [~] SKILL.md decision tables / gate registry — frozen counters (landing-gate, gate-check, coverage-agreement, axis-check) are instrumented and receipt-bound (`c1-counter.sh`).
- [~] At least one end-to-end domain task executed and logged — C3 capture for rounds 26/27 and fixture 6/6 [AFTER]; `LOG.md` entry at round end.
- [~] Instructions executable by an agent without oral context — `tools/souji-wave-evidence-capture.sh` + `tests/fixtures/r28-wave-evidence-capture.sh` [AFTER].
- [~] No cross-domain bleed — C2 scoped to F4 origin-record primitives; hard bound respected (only lane-repo writes; merger source read-only); `PROVINCE.md` unchanged.

**Stale-lane:** not stale — local HEAD `0c96332932e66bbaf9cf1c246091d3275a0ab612` equals remote `refs/heads/master` (verified `git ls-remote`), ahead=0; no other lane mission open.

**Tool installs:** none (no installs/updates by this seat; pacman guard respected).

---

# Seat report — SwarmScribe24

## Status
STATUS: PASS — assigned deliverable (round-report draft with base facts, `[AFTER]` placeholders, all required sections) produced and written to this seat's report dir; read-only posture held; no tools installed; no scratch created.

## Evidence
- Read frozen contract: `census/round-28/records/preregistration.txt` (24 lines; claims C1/C2/C3, machine-block counters, kill rules).
- Read base receipts: `c1-before.tsv` (findings=2, checked_reg=52, c1_rc=2), `c2-before.tsv` (grounded_f4=4, rows=135), `c3-before.tsv` (dirty_waves=163, manifests_26/27=absent), `axis-check-before.txt` (claims=3 flags=0 rc=0); controls `c1/c2/c3-control.tsv` identical.
- Lane git: `git -C <lane> status --short --branch` (detached HEAD, 12 M / 35 ?? at first read); `rev-parse HEAD` = `0c96332932e66bbaf9cf1c246091d3275a0ab612`; `show --stat 0c96332` (11 files, +342); `ls-remote origin refs/heads/master` = `0c96332932e66bbaf9cf1c246091d3275a0ab612`; `log 3a2a80d..HEAD` = freeze commit only.
- SOURCES: header 11 cols at `corpus/SOURCES.md:20`; last row S211; S119 row exists in lane (CSDN count-objects) and staged zh-Hans git-fetch edition in `merge/souji/SOURCES.append.md` (line 17).
- Staged F4 entries present in merger: `merge/souji/knowledge/corpus/knowledge/origin-record-exclusivity-r28.md`, `origin-record-durability-r28.md` (G gate sections, ground F4).
- Current C3 counter run (read-only, exact frozen command): `git status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'` → **11** (tracked-modified wave paths only); `.gitignore` on disk (untracked) already carries the three patterns.

## Findings
1. **Lane moved past the frozen base.** HEAD is `0c96332` (freeze commit: preregistration + before receipts + controls + assimilation IDs), not `3a2a80d`; remote matches, so lane is not stale. The before receipts' measured values are fixed at `3a2a80d`.
2. **C3 counter base (163) vs mid-wave reading (11); `.gitignore` effect.** The base 163 included untracked wave paths. The on-disk `.gitignore` (three patterns from C3, uncommitted at draft time) already suppresses untracked `.ufo/waves/` paths from porcelain, so the mid-wave counter reads 11 (tracked r26 wave mods only). The tip target 0 therefore measures tracked-mod residuals plus any non-ignored untracked paths; untracked leftovers remain on disk but are hidden once ignore rules land. Capture must preserve bytes before the revert; this is an observation on measurement timing, not a counter defect (the counter and claim text are frozen and unchanged).
3. **Controls reproduce before values byte-identically** (`c1/c2/c3-control.tsv` = before receipts), so the do-nothing control is clean.
4. **Assimilation prerequisites are in place:** staged F4 entries exist with `## Gate` sections and F4 ground; SOURCES has 135 rows ending at S211 (so S212–S214 are free); w1 snapshots for open/rename/fsync already fetched.
5. **No tools installed/updated; no scratch used; no lane mutation** (no git add/commit/push/stash/checkout/reset, no jj, no rm/mv, no signals).

## Attack log
None — no frozen counter/predicate/target/case set is believed wrong or gameable; no amendments proposed.
