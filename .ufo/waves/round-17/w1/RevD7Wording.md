STATUS: DONE — D7 confirmed as a carrier/measurement wording elision (facts and every number correct); the r16 report's other Before→after `at <hex>` anchors re-checked, no numeric mismatch, one same-class benign elision at the C1 anchor.

# RevD7Wording — r16 fleet report hex anchors

Scope: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-16/souji.md` (77-line report; commit table at :26-38, Before → after at :42-47, Sources at :49-55) and the artifacts it cites. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (jj-colocated, branch `master`, base `5fa6017`). Read-only; no edits outside this report; no lane/fleet writes.

## 1. D7 core — which commit carries the file, which revision it measured

Command:
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%H -- census/round-16/gate-landing.json
```
Output (one line, so one carrying commit):
```
c46eabf80f4c5b34a6774cd8725a0787306ba754
```

Artifact contents (`census/round-16/gate-landing.json`):
```
{"error": null, "exit": 0, "findings": [],
 "resolved_base": null,
 "resolved_rev": "6ff91f534eece9adde5f667cb7dad400c145351b",
 "summary": {"checked_markers": 30, "checked_pins": 16, "checked_reg": 21,
             "checked_reports": 141, "findings": 0}}
```

Presence/ancestry checks:
```
git merge-base --is-ancestor 6ff91f534e… c46eabf80f…   -> YES
git rev-parse c46eabf^                                  -> 6ff91f534eece9adde5f667cb7dad400c145351b
git cat-file -e 6ff91f5:census/round-16/gate-landing.json
  -> fatal: path 'census/round-16/gate-landing.json' exists on disk, but not in '6ff91f5'   (rc=128)
git cat-file -e c46eabf:census/round-16/gate-landing.json  -> rc=0
git rev-parse c46eabf:census/round-16/gate-landing.json    -> 3577d9fdeffaf52296d181fc12958a8381f835c3
git rev-parse HEAD:census/round-16/gate-landing.json       -> 3577d9fdeffaf52296d181fc12958a8381f835c3  (unchanged since landing)
```
Chain is linear: `cbf688a → 0a70bef → c6207bd → 7a79dc2 → a6ec781 → 163158a → fb23b12 → 4f9a4e8 → 79bbe7a → 6ff91f5 → c46eabf` (each `^` verified).

**Answer to the question posed:** carrying commit = **`c46eabf`** (the only commit in the path's history); measured revision = **`6ff91f5`** (`resolved_rev`, `resolved_base` null), which is `c46eabf`'s first parent and does **not** contain the path.

**Verdict on report:38 — partial (wording, not fact).** The row is
`| c46eabf | census/round-16/gate-landing.json (gate at 6ff91f5) | LOG:886 |`.
In a commit table whose first column is a commit, `(gate at 6ff91f5)` can be read as "the gate artifact is at 6ff91f5" — false, the path is absent there (rc=128 above). The intended reading "the gate ran over 6ff91f5" is true, and every number in the sentence is exact: `findings=0, checked_reg=21, checked_pins=16, checked_markers=30, checked_reports=141` match the artifact field-for-field. This is a precision defect, not an overclaim; the r16 verifier reached the same reading (`corpus/lessons/round-16-verifier-spotcheck.md:144`: "D7, minor wording … file lands at `c46eabf` and records a run over `6ff91f5` blobs").

## 2. Corrected sentence — paste-ready for the r17 lesson

Prose form (recommended; names both roles explicitly):

> `census/round-16/gate-landing.json` was carried by `c46eabf` (the only commit in the path's history) and records a round-16 gate run whose `resolved_rev` is `6ff91f5` — the *measured* revision, one commit before the carrier, where the path itself is absent (`git cat-file -e 6ff91f5:census/round-16/gate-landing.json` exits 128). The run: findings 0, checked_reg 21, checked_pins 16, checked_markers 30, checked_reports 141, `resolved_base` null.

Table-row form, if the r17 lesson keeps the commit table:

> `| c46eabf | adds census/round-16/gate-landing.json: artifact of a --rev 6ff91f5 --round 16 run (resolved_rev 6ff91f5, resolved_base null; findings 0, reg 21, pins 16, markers 30, reports 141). 6ff91f5 is the measured revision and does not contain the path; c46eabf carries it | LOG:886 |`

Companion correction for the same elision at the C1 anchor (report:44), where `c1-matrix-final.json` is carried by `7a79dc2` but measures `0a70bef`:

> `census/round-16/c1-matrix-final.json` was carried by `7a79dc2`; it records a run that measured `0a70bef` (`changed` and `lane_head`, `arms.changed.rev` = `0a70beff3bec…`), whose `tools/souji-census.sh` sha256 is `64a60fd0b0ed…`, unchanged to HEAD. The landing rerun measured `7a79dc2` under fixture bytes `27474396…`; the `0a70bef` run used `85de2a43…` (fixture changed at `c6207bd`). Per-case verdicts are identical across the two runs; only ephemeral strace pids, temp paths, and stack addresses differ.

## 3. Every other `(... at <hex>)` in the Before→after section — same method

Method per phrase: (a) `git log --format=%H -- <path>` / `--diff-filter=A` for the carrier; (b) the artifact's own recorded revision field for the measurement; (c) presence test for any path attributed to that revision.

| report line | phrase | carrier (git) | measured revision / evidence | verdict |
|---|---|---|---|---|
| :38 | `gate-landing.json` (gate at `6ff91f5`) | `c46eabf` (sole log entry) | `resolved_rev` `6ff91f5`; path absent at `6ff91f5` (rc=128) | **partial** — carrier elided (D7) |
| :14 | "gate at `6ff91f5` → 0 uncarried" | n/a (run, no file) | run over `6ff91f5`; 0 uncarried corroborated by artifact `findings: []` | holds as a run anchor (same idiom, harmless) |
| :44 | "At `0a70bef` (… `c1-matrix-final.json`)" | `7a79dc2` (`--diff-filter=A` on the JSON) | `changed=0a70bef`, `lane_head=0a70bef3bec…`, `arms.changed.rev=0a70beff3bec…`; census sha `64a60fd0…` at `0a70bef` = HEAD = worktree | holds as a measurement anchor; carrier differs (`7a79dc2`) — same elision shape, benign in prose |
| :45 | "re-run at `fb23b12` after the vacuity fix" | `fb23b12` modifies `tests/fixtures/r16-landing-gate.py` (numstat `7 4`, 11 changed lines) | fixture at `fb23b12` has 14 `case(` calls + 1 vacuity-stub row = 15 result rows (same 15 at pre-fix `7a79dc2`); diff changes `evaluate(stub_proc, 1` → `0` | holds (structural: `SUMMARY total=15`); 15/15 itself prose-only, no committed stdout |
| :45 | "before carry, `79bbe7a` → 29 LG-SEAT-UNCARRIED" | n/a (gate rev) | `6ff91f5^ = 79bbe7a` (verified); 29 matches `corpus/lessons/round-16.md:14` ("12 wave-1, 29 wave-2") | holds (ordering + count consistent); no committed JSON for the arm |
| :46 | "`--frozen` clean (measured `c6207bd`)" | record carried/regenerated at `7a79dc2` (`git log -- …/record.json` → `7a79dc2`, `b410186`) | `record.json.measured_commit = c6207bdac2e0ef52c1da5fbc87dce5d94065972e`; `verdict: clean`; `c6207bd` ancestor of `7a79dc2` | **holds exactly** — the model wording ("measured") |
| :45 | counts `findings=0, reg=21, pins=16, markers=30, reports=141` | `c46eabf` | artifact summary exact match | holds |
| :51 | "End (at `c46eabf`, SOURCES sha256 `b0683473…`)" | `c46eabf` | `git show c46eabf:corpus/SOURCES.md \| sha256sum` = `b06834735866a1bd18a7d5e2bda7d578716b59543e0305ba65ce93f8ab2c45a4` (= HEAD = worktree) | holds exactly |
| :53 | "after wave-2 reopens (`4f9a4e8`)" | `4f9a4e8` | commit subject names "SOURCES S044/S045"; stat touches `corpus/SOURCES.md`, `SCORECARD.md`, `corpus/lessons/round-16.md` | holds |

**Mismatches found: none numeric.** One wording defect (`:38`, carrier elided) and one same-class but harmless elision (`:44`, prose measurement anchor whose carrier is `7a79dc2`). Every count, sha256, revision role, and ancestry claim in the section resolves against a committed artifact.

## 4. Supporting checks (C1 matrix identity claim, report:44)

`c1-matrix-final.json` (`changed=0a70bef`, `lane_head=0a70bef`) vs `c1-matrix-landing.json` (`changed=HEAD`, `lane_head=7a79dc2`):

- Fixture bytes differ between runs: r15-config `85de2a43e904…` (final, at `0a70bef`) vs `27474396808f33…` (landing, at `7a79dc2`). Fixture chain: `b410186 6314d45d… → cbf688a 9151cde8… → 0a70bef 85de2a43… → c6207bd 27474396… → HEAD 27474396…`.
- Verdict equality (all four arms × both suites = 8 suite comparisons, 128 case verdicts): equal. `changed` 20/20 + 12/12 PASS; `pre-harm` 12 PASS/8 FAIL + 2 PASS/10 FAIL; `r14-harm` 4/20 + 12/12; `r15-baseline` 0/20 + 0/12.
- After normalizing `/var/tmp/<dir>`, `0x…` stack addresses and 5+-digit pids, residual diffs = 2: `changed./rev` (`0a70bef` vs `7a79dc2` by construction) and one truncated trailing pid in `R14C2-04.detail`. So "identical" is true at verdict level; the report does not disclose that the two runs used *different fixture bytes*, which is the informative part.

## 5. Residual risks / evidence gaps (advisory, not D7)

1. **LOG binding is section-level only.** The table preamble (`souji.md:24`) defines `LOG:886` as the "round 16 wave-2 corrections" entry; `LOG.md:886` is that header (`## 2026-10-20 — round 16 wave-2 corrections…`). But `grep -n "gate-landing" LOG.md` → empty and `grep -n "6ff91f5\|c46eabf\|79bbe7a" LOG.md` → empty. The LOG never names the artifact or its counts, so the binding evidences the *change set*, not the gate result. Holds at the granularity the table declares; weakest link if a later round reads LOG as the artifact's ledger.
2. **Five of six gate arms are prose-only.** Only the `6ff91f5` run has a committed JSON (`gate-landing.json`). The `b410186`/15 (5 findings), `a31642d`/13 (0), `cc21683`/14 (0) and `79bbe7a` (29) numbers have no committed replay; this seat could not re-derive them (running the gate is outside the probe set). D6-class, already routed.
3. **`24/47` before-number** in report:46 is prose-only per `round-16-verifier-spotcheck.md:67`; unaffected by D7, noted for the same evidence class.

## 6. Calibration

D7 is real but **minor**: the compact parenthetical conflates *carrier* with *measured revision* in the one place (`:38`) where the first table column is itself a commit, so the misreading "the file is at 6ff91f5" is available and false (rc=128). It is not an overclaim — every figure reproduces from the artifact — and the corpus already uses "gate at `<rev>`" for a *run* elsewhere unambiguously (`corpus/lessons/round-16.md:56`, "flagged by the gate at `79bbe7a` before carry"). The smallest fix is therefore wording, not new evidence: name the carrier and the `resolved_rev`, as drafted in §2. The r17 lesson must not carry the bare `(gate at <hex>)` form, and should apply the same two-role wording to the C1 anchor at `:44` (`7a79dc2` carries, `0a70bef` measured) for consistency.

## 7. Tooling

No installs or upgrades. Commands used, all in the allowed set: `git -C <repo> log/show/rev-parse/cat-file/merge-base` (read-only), `sha256sum`, `grep`/`awk`/`wc` on exact named files, `python3` JSON reads of named artifacts (no tool execution, no lane tool run). No writes outside this report.
