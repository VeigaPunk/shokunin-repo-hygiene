# SwarmExecutor02 — round 28 w1 — C1(b) Q59 prose-token correction

## Status
STATUS: PASS — `corpus/QUALITY.md:143` (Q59) body phrase `a corpus/knowledge/registry change` reworded to `a knowledge-registry change`; meaning unchanged, the token no longer starts with a scanned root, the `LG-DANGLING-PTR` finding for it is gone on an isolated replay, and the row now contains no path-shaped token except two real existing paths. Working-tree edit only; no commit (L1 integrates).

## Evidence

### 0. Contract read
`/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/records/preregistration.txt:5` (C1): "reword to `knowledge-registry` so the prose no longer reads as a path" — read before any edit.

### 1. Counter at lane base (before)
```
python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 3a2a80d0d18940a5e352ebc526da22a57dad83c4 --round 28 --fleet-root /home/vgpnk/Projects/shokunin
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at 3a2a80d0d189
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at 3a2a80d0d189
SUMMARY	findings=2	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
```
Lane HEAD at edit time was `0c96332932e66bbaf9cf1c246091d3275a0ab612` (work already landed past the prereg base); the two findings are unchanged at that revision.

### 2. Exact before/after line bytes
Before (`0c9633:corpus/QUALITY.md:143`, 791 bytes, sha256 of line `d439c0a6684f979e676f6916dca20afed627309144f27d16936d672594ca5f91`):
```
| Q59 | For each frozen claim, the declared axis must correspond to the actual class of surface the claim changes (a gate/runnable fixture on an input edge class is an operability surface; a corpus/knowledge/registry change is a coverage surface; a self-assessment-file change is a calibration surface). A claim whose axis and surface class are incompatible is a misattribution defect, and the check must be an instrument, not a hand review. | frozen claims; preregistration machine blocks | `python3 tools/souji-axis-check.py --prereg <prereg> --scorecard <scorecard>` exits 0 and prints `flags=0` (R1 axis-owned, R2 surface-class consistency, R3 lowest-axis presence, R4 universal-clause scan) before scoring; the round-26 C3 instrument is the witness | corpus/lessons/round-26.md R26-M1 |
```
After (working tree `corpus/QUALITY.md:143`, 784 bytes, sha256 of line `0c6428241f0133c6149985a504e96920c7f822edaa3926320dd90e15f1d997b5`):
```
| Q59 | For each frozen claim, the declared axis must correspond to the actual class of surface the claim changes (a gate/runnable fixture on an input edge class is an operability surface; a knowledge-registry change is a coverage surface; a self-assessment-file change is a calibration surface). A claim whose axis and surface class are incompatible is a misattribution defect, and the check must be an instrument, not a hand review. | frozen claims; preregistration machine blocks | `python3 tools/souji-axis-check.py --prereg <prereg> --scorecard <scorecard>` exits 0 and prints `flags=0` (R1 axis-owned, R2 surface-class consistency, R3 lowest-axis presence, R4 universal-clause scan) before scoring; the round-26 C3 instrument is the witness | corpus/lessons/round-26.md R26-M1 |
```
Byte accounting (python3 -B over the two line bytes): `delta -7`, `common_prefix_len 191`, `common_suffix_len 583`, `REMOVED 'corpus/knowledge/'`, `ADDED 'knowledge-'`; `pipes 6→6`, `cells 5→5`, trailing bytes `'1 |'` both, no `\|` introduced. Only the single phrase changed; every other byte of the line is identical.

### 3. grep confirmation
```
$ grep -n 'knowledge-registry' corpus/QUALITY.md
143:| Q59 | For each frozen claim, the declared axis must correspond to the actual class of surface the claim changes (a gate/runnable fixture on an input edge class is an operability surface; a knowledge-registry change is a coverage surface; a self-assessment-file change is a calibration surface). …
```
One hit, line 143. `grep -n 'corpus/knowledge/registry' corpus/QUALITY.md` → no hit (exit 1).

### 4. Path-shaped tokens in the row (gate's own grammar)
Applied the gate's own `POINTER_PATH_RE` (`tools/souji-landing-gate.py:141-146`; roots `census|tests|tools|corpus|.ufo/waves|.ufo/quarantine` + `/`) to line 143 and existence-tested each match against the lane root:
- BEFORE: `corpus/knowledge/registry` ABSENT, `tools/souji-axis-check.py` EXISTS, `corpus/lessons/round-26.md` EXISTS.
- AFTER: `tools/souji-axis-check.py` EXISTS, `corpus/lessons/round-26.md` EXISTS. The prose token is gone.
- Non-pointer residue in the row: `gate/runnable` (prose, no scanned root prefix → not matched), `<prereg>`/`<scorecard>` placeholders (not path-shaped). So the row's body and check cells now carry no path-shaped token other than the two real, existing paths.

### 5. Isolated replay proving the finding is removed by this line alone
Scratch `/var/tmp/souji-r28-SwarmExecutor02/replay` (`git init`, `git -C "$D" rev-parse --show-toplevel` → `/var/tmp/souji-r28-SwarmExecutor02/replay` verified before first commit) = `git archive` of lane `0c9633` (commit `62e36dca`), then **only** line 143 replaced from the working tree (asserted no other index assigned) → commit `9aaa94fa`.
```
--rev 62e36dca (pre-fix):  LG-DANGLING-PTR corpus/knowledge/registry  corpus/QUALITY.md:143 ; SUMMARY findings=3
--rev 9aaa94fa (post-fix): (no corpus/QUALITY.md:143 row)                        ; SUMMARY findings=2
```
The one-finding drop is exactly the Q59 pointer. The residual scratch findings are not caused by this edit: `corpus/lessons/round-24.md:232:S118` (C1(a) seat's item, still open in the working tree) and `LG-FROZEN-MEASURED tests/fixtures/r15-preservation-frozen/expected.json measured_commit '005f3d37…' does not resolve` — a replay artifact of the fresh `git init` having no history (absent from the lane-base run above).

### 6. Blast radius
- `git diff -U0 -- corpus/QUALITY.md` shows two single-line hunks: `@@ -141 +141 @@` (C1(a) seat, not touched by me) and `@@ -143 +143 @@` (mine).
- `grep -rn 'knowledge/registry|Q59' tests/ tools/` → no hits: no fixture or instrument asserts the old phrase. `tools/souji-axis-check.py` derives surface class from the prereg `surface-class:` line (`SURFACE_AXIS`), not from QUALITY prose, so R2 is unaffected.
- Remaining occurrences of the old phrase are frozen/append-only records only (`census/round-27/records/preregistration.txt:7`, `census/round-28/records/preregistration.txt:7`, `census/round-28/records/log-entry-draft.md:5`, prior `.ufo/waves/round-2[67]/…` reports); deliberately not rewritten.

## Findings
1. **F1 — Q59 body token corrected, no other pseudo-path in the row.** `corpus/QUALITY.md:143`: `a corpus/knowledge/registry change` → `a knowledge-registry change`; row's only remaining path-shaped tokens are `tools/souji-axis-check.py` and `corpus/lessons/round-26.md`, both existing at `0c9633`.
2. **F2 — residual gate finding is the sibling item, not mine.** `corpus/QUALITY.md:141` still cites `corpus/lessons/round-24.md:232:S118` (C1(a)); the lane gate will report `findings=1` for C1 until that seat's refactor lands. Location: `corpus/QUALITY.md:141`.
3. **F3 — frozen records keep the old wording by design.** The phrase survives in `census/round-27/records/preregistration.txt:7`, `census/round-28/records/preregistration.txt:7` and prior wave reports; these are historical evidence and must not be edited to make a counter look clean.
4. **F4 — meaning preserved, no silent criterion change.** The surface-class taxonomy in Q59 (`operability` / `coverage` / `calibration`) and its instrument witness (`tools/souji-axis-check.py`, `flags=0`) are untouched; only the noun phrase spelling changed. Location: `corpus/QUALITY.md:143`.
5. **F5 — instrument not weakened.** No gate grammar, exemption file, or fixture was touched; `corpus/pointer-exemptions.tsv` untouched (the frozen claim forbids exemptions, and none was used). Location: `tools/souji-landing-gate.py:141-146` (read-only reference), `corpus/pointer-exemptions.tsv` (unmodified).

## Attack log
- **A1 (counter gameability, reported not exploited)** — `LG-DANGLING-PTR` on a prose token is clearable by rewording, so the counter measures token hygiene, not citation validity. This is the sanctioned C1(b) fix and the meaning is unchanged, but a future round could "fix" a real broken citation the same way. Discriminator already available: the fix must leave a real path where a citation is intended (here no citation is intended, and the row's remaining paths all resolve). Location: `corpus/QUALITY.md:143`, counter `tools/souji-landing-gate.py:141-146`.

## Notes
- No commits, no `git add`, no `jj` mutation, no deletes/moves; single file edited in the working tree (`corpus/QUALITY.md`), plus this report.
- No tool installs or upgrades this wave.
- Scratch `/var/tmp/souji-r28-SwarmExecutor02` removed after the runs.
- Parent should re-run at the landing tip: `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --round 28 --fleet-root /home/vgpnk/Projects/shokunin` and expect the `corpus/knowledge/registry` row absent (C1 passes only when C1(a) also lands).
