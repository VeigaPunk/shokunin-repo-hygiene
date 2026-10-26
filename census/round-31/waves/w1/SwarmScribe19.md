## Status

STATUS: PASS — M1 (round-27 seat-failure carry) is delivered as one append-only section with 29 bullets, one per committed failure paragraph; a scratch-clone replay shows the base gate moving from `29 LG-SEAT-UNCARRIED carry_heading=0` to `0 LG-SEAT-UNCARRIED carry_heading=1`, and a control that deletes one bullet re-fails with exactly that report named.

## Evidence

Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; lane HEAD while working `1b811368461785040e955f41f9c97e62f61fd67c`. All gate runs used the lane's own `tools/souji-landing-gate.py`. Scratch: `/fast/scratch/hyaku/souji-r31/SwarmScribe19/r.AfTj0S/c`, cloned with `--no-local` and `remote remove origin` (`remote -v` printed nothing; toplevel printed that clone).

Red-before, lane base (no `--fleet-root`, run in the lane, read-only):
```
python3 -B tools/souji-landing-gate.py --root <lane> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --round 27
SUMMARY findings=32 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=0 checked_reports=94
```
`cut -f1 | sort | uniq -c` → `3 LG-DANGLING-PTR`, `29 LG-SEAT-UNCARRIED`. Same at lane HEAD `1b811368`, so the defect is live.

Red-before, scratch clone at `1b811368` (`--fleet-root /home/vgpnk/Projects/shokunin`): `findings=29 … checked_markers=29 … carry_heading=0`, rc 1.

Green after, scratch commit `ea07520ee2622c54a463b207159823d04383e01e` (lesson grew 41 → 82 lines, append only):
```
SUMMARY findings=0 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94
```
rc 0. Without `--fleet-root`: `3 LG-DANGLING-PTR`, the same three `.ufo/waves/hyaku/...` pointers already at lane HEAD — the appended section added none.

Load-bearing control, scratch commit `44935719f47e2d00944d27bbcccbf345b11cd3cb` (one bullet removed): rc 1, `LG-SEAT-UNCARRIED census/round-27/waves/w1/ScribeLOG.md line 2 …`, `findings=1`; clone reset to `ea07520e` afterwards.

Disposition checks run this run: `sha256(git cat-file -p e78ac7c:tools/souji-landing-gate.py)` = `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd` (equals `c1-before.tsv` `gate_sha256`); `python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`; `git ls-tree -r --name-only HEAD | grep -c __pycache__` → `5`; gate at HEAD with `--fleet-root` for round 27 → zero `LG-DANGLING-PTR`. Tooling: none installed or upgraded (bash, git, python3 only); scratch directory removed after the delivery was written.

## Findings

1. **Round-27's carry gap is open at the tip, not historical.** `corpus/lessons/round-27.md` (41 lines, no `## Seat-reported failures`) versus 29 committed STATUS failure paragraphs under `census/round-27/waves/`; the base gate reports the identical `findings=29 carry_heading=0` at `9f17a1ef` and at `1b811368`. The delivery fixes exactly this by append.
2. **The preregistration's round-27 numbers do not reproduce as written.** `census/round-31/records/preregistration.txt` states "round 27 29 LG-SEAT-UNCARRIED + 2 dangling"; measured at lane base without `--fleet-root` there are `3 LG-DANGLING-PTR`, and with `--fleet-root` there are `0`. The 29 uncarried reproduce exactly. Reported, not an attack: no predicate or target is affected.
3. **The tracked-`__pycache__` defect the two round-27 seats reported is still live.** `git ls-tree -r --name-only HEAD | grep __pycache__` lists 5 blobs, including `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (the path `ExecPycacheFix.md:2` and `LabGitIgnoreProbe.md:4` name). Both entries are carried `open` on that basis.
4. **The installed round-27 pre-report gate still carries the false-PASS vectors its reviewer demonstrated.** `tools/souji-pre-report-gate.sh:4` unsets a git env list without `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0`; `:34` uses `status --porcelain=v1 --untracked-files=all` (ignored files invisible); `:31` still tests `grep -c '^## SHONEN'` (prefix match). The read-only breach is fixed (`GIT_OPTIONAL_LOCKS=0`, `git --no-optional-locks`), so `RevC3Gate.md:4` is carried `open`, not `resolved@`.
5. **Disposition split: 16 `resolved@<commit>` (8 at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`, 8 at `c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0`) and 13 `open`.** Two entries are report-level and were delivered only in the fleet report (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/souji.md:11`), which is not a lane commit, so `CritReportContract.md:5` and `ScribeReport.md:2` stay `open` rather than borrowing a resolution they cannot name.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-m1-carry-r27.md` — the verbatim append block (`## Seat-reported failures`, 29 bullets; bytes identical, sha256 `3fe34851daaa1c9552133c1ee8700a6d98cd5b02520170e67d3e9414edd8cc9a`, to the block proven green), its receipts, and the per-entry disposition basis table.
- `.ufo/waves/round-31/w1/SwarmScribe19.md` — this report.
