# S67ConnectorOverlap — round 67 cross-claim and sibling-overlap scan

Seat: S67ConnectorOverlap (connector, leaf, no subagents). Read-only everywhere. Delivered under
`.ufo/waves/round-67/w1/S67ConnectorOverlap/`: `sibling-overlap.md`, `shokuknow-scan.md`, `cross-claim.md`, `report.md`.
No lane file, sibling repo, MANIFEST, `.ufo/state`, fleet template or `~/.local/bin` path was written. No git mutation was run.
No tool was installed or upgraded (no installs to record). Scratch `/fast/scratch/hyaku/souji-r67/S67ConnectorOverlap/` was created and removed.

## Axes named
- Overlap with sibling routes (contest risk for the C1 route).
- Assimilation duty (shokuknow staged themes).
- Claim-to-routed-defect mapping and seat file boundaries (L1 coordination).

## Findings

1. **Sibling overlap, `GIT_COMMON_DIR`.** Eleven-plus tracked sibling files name it. Every hit is a scrub list, a
   poison list or a fresh env. None value-checks it. Nearest analogue: kumitate `scripts/receipt-bind.mjs:101-104`
   (`GIT_ENV_DROP`). kama is prefix-scrub (`tools/report-landing-audit.py:148`). History: kama
   `.ufo/waves/round-21/build/advice/AuditGitEnvSentinel.md:19` (F1 HIGH). No sibling needs souji's refusal design.
   *Contested scope (not absorbed):* a fleet-wide env-scrub helper, and `GIT_NAMESPACE`/`GIT_CEILING_DIRECTORIES`
   (prereg L3): most siblings scrub both, souji does not.
2. **Sibling overlap, other terms.** `RECEIPT-ENV`: no sibling emits it. One term collision (kasegi round-42
   `RECEIPT-ENV-LANDMINE`). `freeze-check --chronology`: souji only. `chousa/tools/freeze-check.py` is a same-named
   tool with no chronology flag. `core.fileMode`: tameshi is the mode-bit owner, and it *forces* exec bits under
   `core.fileMode=false` (`tools/executor-source-pin-measure-v2.py:21-24, 207-210`). Opposite purpose to souji W2.
3. **Shokuknow assimilation.** Verdict (one line): **none matches** (adjacent only: count-objects `different_commondir`
   sweep in `garbage-false-positive-modes-r25.md` §3, a census-side fact). The staged package is stale: pinned to a
   108-row baseline against the lane's 222, and its ids S109–S236 collide with ids the lane already holds (S109 at
   `corpus/SOURCES.md:144`, S236). It cannot be appended as staged. Two entries cite a missing S022.
4. **considerthese.** `souji-shokunin/considerthese/` is absent (`test -d` false). Nothing to list.
5. **Routed items.** R1 (GIT_COMMON_DIR, W1-W3) rides C1. R2 (M4), R2c (M7) and R3 (M5 scope) ride C2, pinned.
   Outside both: K3/K4/K6/K7, L0 360 (git -c trade), M8 wording, the receipt grammar (gating C1's After receipt), Q130.
6. **Gaps and mislabels for L1 (none blocking under the frozen predicate).**
   - R1b: the r66 "route sweep as a frozen enumeration" is narrowed to GIT_COMMON_DIR. L3 carries the rest. State it as
     deferred, not done.
   - R2b: the prereg maps M6 to C2, but the docstring correction sits in `census/round-67/c1-counter.py:76-78` (the C1
     instrument). A label mismatch only.
   - R7: the C1 After receipt is correct only when produced with `--rev <candidate> --receipt` (`c1-counter.py:1004`).
     Hand-assembly would reproduce the r66 chronology failure.
   - [INFERENCE, unmeasured] After C1 lands, the live SKILL s5 sentence would be true for the three names it lists but still
     names only the r66 refusals. C2's pinned verdict is unaffected. Do not edit s5 (L0 362).
7. **File-boundary overlaps (coordination for L1).**
   - **Live lane tree has an uncommitted Q130 row in `corpus/QUALITY.md`** (`git diff --stat`: 1 insertion). S67ScribeEntry's
     rule is no lane edits. Attribute the edit before landing.
   - S300 is named by both S67ScoutSources and S67ScribeEntry. L1 assigns it once.
   - S67ScribeEntry's draft `common-dir-route-receipt-writer.md` duplicates the topic of the r66
     `corpus/knowledge/caller-env-routes-receipt-writer.md` (line 42 already names GIT_COMMON_DIR). Recommend amend or fold.
   - S67ExecWriter's spec lists the frozen `c1-counter.py` and `c1-matrix.tsv`. Confirm its report says read-only.
8. **Spec conflict.** The seat spec gives two report paths: `.../w1/S67ConnectorOverlap/report.md` (the `Report:` trailer,
   inside the seat dir) and `.../w1/S67ConnectorOverlap.md` (outside the seat dir). The hard bound allows only the seat
   dir, so only `report.md` was written. L1 should confirm the intended path.

## Verification performed (read-only; nothing run that mutates)
- `git -C <repo> grep -n -I` over the 19 sibling repos (tracked files), for GIT_COMMON_DIR, RECEIPT-ENV, core.fileMode,
  --chronology and RECEIPT-MEASURED. Results in `sibling-overlap.md`.
- Grep-tool sweeps over sibling working trees and the shokuknow package. Results in `sibling-overlap.md` and `shokuknow-scan.md`.
- Lane reads: `git rev-parse --show-toplevel`, `git log -1`, `git cat-file -e` on instruments commit `05eb2cee`,
  `sha256sum tools/souji-receipt-write.py` (= a8c47d36…97fc), `git diff --stat` (QUALITY Q130 row), greps on
  `census/round-67/c1-counter.py` (docstring lines 60-82; write_receipt line 1004), `c2-counter.py` docstring 1-24,
  `c1-matrix.tsv` rows W1-W3 (refuse/refuse/accept), and the wave spec `w1-spec.json` (10 seats, targets).
- `disk-guard.sh status`: /fast/scratch/hyaku at 49% used, 411.9G free. No heavy pass was run.

## Limits
- Hit lists are the first matches per repo where a cap applied (mori `.scratch` capped at 8). Full counts are not claimed.
- Non-S67 roster peers were not attributed (not in the 10-seat spec).
- The post-landing s5 behaviour is an inference, not measured.
