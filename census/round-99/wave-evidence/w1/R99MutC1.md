# R99MutC1 — mutation test of the r99 C1 runner (`census/round-99/declared-shapes.py`)

Detector (per seat spec): the `SHAPES-SUMMARY` line (plus exit code) — does the mutation move it?
Pristine baseline first: failure would be inconclusive. Baseline passed.

## Inputs / restoration evidence

| artifact | sha256 |
|---|---|
| `census/round-99/declared-shapes.py` (lane, `c94d678`) | `7f6a0816c34eec167016253b7f3d82fedf14aa408c5fab98cc60f3e5d0711816` |
| pristine scratch copy (before/after identical) | `7f6a0816c34eec167016253b7f3d82fedf14aa408c5fab98cc60f3e5d0711816` |
| `census/round-99/c1-survivor-search.py` (r98 hook) | `e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1` |
| `census/round-99/shapes.tsv` (frozen) | `8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14` |
| relabelled freeze (all kinds flipped) | `ff006ddcb3a10d82e5945740824d23c22e36b8b16607ca50d3c0e17507d60792` |
| 18-row freeze (appended `zz-missing.py` declared) | `ec26a3a3448521f1bec5659b8ba9fe148e689262d27b54b43d2d075bb46a9671` |

The pristine lane file was never edited (mutants lived only under scratch
`/fast/scratch/hyaku/souji-r99/R99MutC1/`, deleted after this report — the directory
is gone with it; the lane hash above is the after-state). No lane file, no git state
was touched: `git status` in the lane shows only the pre-existing untracked
`census/round-99/` tree written by the executor seats.

## Commands (all from scratch dir; `--work` under scratch, never `/tmp`)

Common args: `--freeze <f> --search …/round-99/c1-survivor-search.py
--scripts …/round-98/shapes --work <scratch>/w-*` with `python3 -B` (3.14, system).

**Baseline P0** — `python3 -B pristine.py --freeze …/round-99/shapes.tsv …` → exit `0`
- `FREEZE sha256=8bc642c4…a14`
- `SHAPES-SUMMARY shapes=17 mismatched=0`

**M1–M5 vs frozen file** — exit codes and summary lines:

| mutant | exit | `SHAPES-SUMMARY` |
|---|---|---|
| M1 drop `MISMATCH` rows | 0 | `shapes=17 mismatched=0` |
| M2 hard-coded kinds | 0 | `shapes=17 mismatched=0` |
| M3 ignore freeze file | 1 | `shapes=17 mismatched=8` |
| M4 invert declared comparison | 1 | `shapes=17 mismatched=9` |
| M5 accept missing shape | 0 | `shapes=17 mismatched=0` |

(M3 lists the 8 crash shapes as `MISMATCH` because it labels everything `declared`;
M4 lists the 9 declared shapes as `MISMATCH` — the exact complements. The
`grep -c '^SHAPE'` = 18 counts are 17 shapes + the summary line itself.)

**Discriminating probes:**

- **P2 pristine + relabelled freeze** → exit `1`,
  `FREEZE sha256=ff006ddc…792`, `SHAPES-SUMMARY shapes=17 mismatched=17`.
  (All 17 kinds flipped, so all 17 mismatch — label source confirmed live.)
- **P1 M2 + relabelled freeze** → exit `0`,
  `FREEZE sha256=ff006ddc…792` (digest still printed — it hashes the file
  regardless), `SHAPES-SUMMARY shapes=17 mismatched=0`.
  The hard-coded tuple provably never reads the file: the same relabelling that
  moves the pristine count by 17 leaves M2 at 0.
- **M3 + 18-row freeze** → exit `1`, `SHAPES-SUMMARY shapes=17 mismatched=8`
  (shape count stays 17: the extra row is silently ignored).
- **M5 + 18-row freeze** → exit `0`, `SHAPES-SUMMARY shapes=17 mismatched=0`,
  zero rows mention `zz-missing`.
- **Control: pristine + 18-row freeze** → exit `2`, stderr
  `SHAPE zz-missing.py missing`, and no `SHAPES-SUMMARY` line at all.
- **M1 + relabelled freeze** (mismatches induced) → exit `1`,
  `SHAPES-SUMMARY shapes=17 mismatched=17`, but `MISMATCH`-prefixed rows = 0
  (the 17 per-shape `… MISMATCH` suffixes remain).

## Verdicts (detector = `SHAPES-SUMMARY` line + exit code)

- **M1 (drop `MISMATCH` recap rows) — KILLED** under the detector (summary still
  reads `mismatched=17` / exit 1 when mismatches exist). **Equivalent w.r.t. the
  detector**: the recap rows are redundant with the per-shape suffixes and the
  summary count; only a consumer scraping `^MISMATCH <name>` recap rows would see
  a difference. No finding.
- **M2 (kinds from a hard-coded tuple) — NOT killed by the summary line alone**
  (`mismatched=0`, exit 0, identical to pristine). **This is the intended M6
  finding, not an equivalent mutant**: P1 proves the mutation is observationally
  invisible to the summary detector — the very vulnerability C1 exists to remove.
  It is caught only by the surrounding claim apparatus (the relabelled-copy probe
  and the `FREEZE` hash), not by the summary line. No summary-line predicate
  would be a valid regression test for M6.
- **M3 (ignore the freeze file, enumerate the scripts dir) — KILLED**
  (`mismatched=8`, exit 1): the 8 crash shapes are relabelled `declared` by the
  mutant, so the summary moves even with no mismatch anywhere else in the system.
- **M4 (invert the declared comparison `==` → `!=`) — KILLED**
  (`mismatched=9`, exit 1): exactly the 9 declared shapes flip. The comparison is
  load-bearing in the summary.
- **M5 (accept a missing shape with `continue`) — NOT killed by the summary line
  alone** (`mismatched=0`, exit 0, identical to pristine). **Not equivalent**: the
  pristine control (exit 2, `SHAPE zz-missing.py missing`, no summary line)
  differs observably — a missing shape under M5 is silently dropped while the
  shape count stays at 17. The summary detector is blind to it because `total`
  is only incremented for present shapes; the missing-shape guard (`return 2`)
  is the load-bearing behavior, and it is exercised through the exit code and
  stderr, not the summary line. **Finding F1** (reproducer: M5 + 18-row freeze
  above; pristine control in the same section).

## Findings

- **F1 (coverage, M5):** the declared-exit shape table's completeness is enforced
  by an early `return 2` outside the summary detector. A one-edit mutation that
  silently skips missing shapes yields `SHAPES-SUMMARY shapes=17 mismatched=0`
  with exit 0. If any downstream gate keys only on the summary line, a deleted
  shape file passes undetected. The lane's existing behaviour is correct
  (control run proves exit 2 + stderr); the gap is that the summary line, the
  claimed C1 detector, does not cover it. Suggested cover (L1 decision, not
  applied): also assert `total == len(shapes)` before printing the summary, or
  count skipped shapes into the summary. Reproducer:
  `M5-accept-missing-shape.py` + `shapes-18row.tsv` under scratch (command above),
  vs `pristine.py` + `shapes-18row.tsv` (exit 2).
- **F2 (calibration note, M2):** the summary line cannot distinguish "kinds read
  from the frozen file" from "kinds hard-coded in the runner" — M2 is
  indistinguishable from pristine under the detector in every run above. The C1
  claim is therefore only as strong as its relabelled-copy probe + `FREEZE`
  hash; the summary line alone is not evidence for the M6 property. (The claim
  text already pairs them; this records the measured dependency.)

## Mutant definitions (each exactly one edit to the pristine runner)

- M1: delete the trailing `for name in bad: print(f"MISMATCH {name}")` block.
- M2: replace `shapes = load_shapes(ns.freeze)` with the 17 `(name, kind)` pairs
  copied verbatim from `shapes.tsv`.
- M3: replace `shapes = load_shapes(ns.freeze)` with
  `[(f, "declared") for f in sorted(os.listdir(ns.scripts)) if f.endswith(".py")]`.
- M4: `plain.returncode == hooked.returncode` → `!=`.
- M5: missing-shape branch `print(...); return 2` → `continue`.

Tooling: only system `python3` (no installs, no pacman, no sysctl changes).
