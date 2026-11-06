# S72ExecC2 — C2 coverage falsification (souji r72, wave w1)

Verdict: **C2 (i) and (ii) REPRODUCED from committed bytes; no HIGH/MEDIUM finding.** All runs from
`/home/vgpnk/Projects/shokunin/souji-shokunin`, scratch `/fast/scratch/hyaku/souji-r72/S72ExecC2`.

## Decisive lines (my runs)
- `BATTERY mutants=5 kills=5 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0 all_match=true` / `EXIT=0` (bat.rc=0) → C2(i) holds.
- `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0` → C2(ii) holds; new_honest 19 == matrix accept rows 19.
- Before control (r71 counter, r71 matrix, same 5 members): `BATTERY mutants=5 kills=0 ... survived=5 error=0 all_match=false` / `EXIT=1` (before.rc=1) → control (c) holds.
- Per-mutant forgery rows (parsed from CASE lines): WM3→FWr, WM4→FWi, WM5→FWp, WM6→FWs, WM8→FWw — exactly one forged row each, honest=0/echo=0/errors=0; matches the probe's one-member-per-shape map.
- FW rows in main arm: `base=accept new=refuse` with class `RECEIPT-FILTER-DRIVER-SET` for all five (class_mismatches=0 over 75 rows).

## Commands (exact)
- `python3 -B census/round-72/c1-counter.py --root <lane> --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1… --work <S>/bat --battery-manifest census/round-72/battery-manifest.tsv --battery-dir census/round-72/battery --receipt <S>/bat.txt`
- `… --rev 0bf098dd… --tool tools/souji-receipt-write.py --work <S>/main --receipt <S>/main.txt`
- `python3 -B census/round-71/c1-counter.py … --matrix census/round-71/c1-matrix.tsv --work <S>/before --battery-manifest census/round-72/battery-manifest.tsv --battery-dir census/round-72/battery`
- `python3 -B census/round-72/probes/fw-shapes-probe.py --work <S>/probe <base-writer> <lane-writer> WM3..WM8`
- `sha256sum -c SHA256SUMS` in `census/round-72/battery` → 5×OK; rebuilt members with a scratch copy of `make-battery.py` → `cmp` IDENTICAL 5/5, manifest + SHA256SUMS IDENTICAL.
- Regenerated counter+matrix with a scratch copy of `mk-counter.py` → both byte-identical (counter sha 7578447d…, rows=75, base_accept=31).

## Evidence
- Probe: 35/35 PROBE lines identical to `probes/fw-shapes-probe.txt` after renaming my writer files (10 accept / 25 refuse / 0 error); base writer accepts all five shapes, lane-base writer refuses all five, each member accepts exactly its own shape.
- Receipt diffs vs L1: `records/c2-after-battery.txt` 5 changed lines, `records/c2-honest-writer.txt` 11, `controls/c2-before-r71-battery.txt` 5 — all header (`rev/instrument/instrument_sha256/command`), slot/regress path lines, and my added `# receipt=` trailer. Instrument sha256 7578447d… (r72) / 7e5a694a… (r71) match on both sides.
- Matrix provenance: 70 carried rows byte-identical in cols 1-3 to `census/round-71/c1-matrix.tsv`; `base_expect` equals the r71 `c1-after.txt` `CASE … base=` value for all 70; exactly FWr FWi FWp FWw FWs appended; cross-tab accept|accept 19, refuse|accept 12, refuse|refuse 44 (base accepts 31 = base_forgeries 12 + base_honest 19).
- Frozen inputs unchanged since freeze 23372f36: preregistration, c1-mutants.json, battery-manifest, SHA256SUMS, all five members, make-battery.py, probe .py/.txt, control (c), r71 harness/counter/matrix all SAME; writer at lane base and tree = b7790001…244d.
- Hashes: manifest 99c9a55f…204e, SHA256SUMS cfd51315…0437, mutants cfc40608…a754 — match the preregistration.

## Findings
- LOW: `probes/fw-shapes-probe.txt` ends with `EXIT=0`, which the probe script never prints (runner-appended); the artifact is not literally reproduced by the documented command alone.
- LOW: the frozen probe names its reference writers `base-8b9345b1.py` / `tip-0bf098dd.py`, files that exist nowhere; they are bound only by the sha256 tags in the header (118597e0 / b7790001), which I reproduced by `git show` at those revisions.
- WM7 remains unmeasured as declared (manifest has 5 members, no WM7); not a miss.

## Files written
`.ufo/waves/round-72/w1/S72ExecC2.md`, `.ufo/waves/round-72/w1/S72ExecC2/{bat.out,main.out,before.out,probe.out,probe.norm,rebuild-cmp.txt,rebuild-make-battery.out}`. No tool installs; no lane tracked file touched.
