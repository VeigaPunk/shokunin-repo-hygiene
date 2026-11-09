# R99ExecC1 — C1 freeze-file build

Params: /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/c1-survivor-search.py
Params: /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/shapes.tsv
Params: /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/declared-shapes.py
Verdict: implemented; frozen file gives mismatched=0, relabelled copy moves count to 3, r97 hook against
frozen file gives mismatched=3
Tooling: none installed (python3 system); no sysctls touched.

## Files delivered (lane paths, absolute)
- /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/c1-survivor-search.py — byte copy of
  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-98/c1-survivor-search.py
  (sha256 e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1 both sides).
- /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/shapes.tsv — header
  `name<TAB>kind<TAB>plain<TAB>comment` + 17 rows, names and kinds verbatim from the r98 SHAPES tuple.
  sha256 8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14.
- /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/declared-shapes.py — copy of the r98
  runner with the SHAPES tuple removed; kinds are read from --freeze only. Contract points:
  (a) missing/one of required args → argparse error, rc 2 (verified below: rc=2 with `--freeze` etc absent).
  (b) prints `FREEZE sha256=<hex>` of the freeze file before running.
  (c) prints one `SHAPE <name> kind=<kind> plain=.. hooked=.. ok|MISMATCH` per row plus
      `SHAPES-SUMMARY shapes=N mismatched=M` (exit 0 iff mismatched=0, else 1).
  (d) prints `MISMATCH <name>` lines naming each mismatched row. Unknown kind raises ValueError.

## Run 1 — frozen file, r98 hook (as specified in the ticket)
Command (exit 0):
```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/declared-shapes.py --freeze /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/shapes.tsv --search /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/c1-survivor-search.py --scripts /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-98/shapes --work /fast/scratch/hyaku/souji-r99/R99ExecC1/w-frozen
```
Output:
```
FREEZE sha256=8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14
...
SHAPE q1o-save-then-bare-raise.py kind=crash plain=1 hooked=70 ok
SHAPE q1q-caught-then-direct.py kind=crash plain=1 hooked=70 ok
SHAPE q1i-finally-then-catch.py kind=declared plain=0 hooked=0 ok
SHAPES-SUMMARY shapes=17 mismatched=0
```
rc=0. All 17 rows ok.

Missing-arg check: same command with no `--freeze`/`--search`/`--scripts`/`--work` → argparse
`error: the following arguments are required: --freeze, --search, --scripts, --work`, rc=2.

## Run 2 — relabelled copy in scratch (Q173 movability attack)
Built /fast/scratch/hyaku/souji-r99/R99ExecC1/shapes-relabelled.tsv from shapes.tsv by flipping
q1o→declared, q1q→declared, q1i→crash (sha256 004356d76d94c54158232f250077c6995b5103b16f34ef4111e4933bc6cc330a),
then the same command with that --freeze (rc=1):
```
FREEZE sha256=004356d76d94c54158232f250077c6995b5103b16f34ef4111e4933bc6cc330a
SHAPE q1o-save-then-bare-raise.py kind=declared plain=1 hooked=70 MISMATCH
SHAPE q1q-caught-then-direct.py kind=declared plain=1 hooked=70 MISMATCH
SHAPE q1i-finally-then-catch.py kind=crash plain=0 hooked=0 MISMATCH
SHAPES-SUMMARY shapes=17 mismatched=3
MISMATCH q1o-save-then-bare-raise.py
MISMATCH q1q-caught-then-direct.py
MISMATCH q1i-finally-then-catch.py
```
The count moves 0 → 3 under relabelling with the same hook; the FREEZE hash differs, so the
relabelled file cannot masquerade as the frozen one (M6).

## Run 3 — r97 hook (census/round-98/controls/c1-r97-search.py) against shapes.tsv (rc=1)
```
FREEZE sha256=8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14
SHAPE q1o-save-then-bare-raise.py kind=crash plain=1 hooked=1 MISMATCH
SHAPE q1q-caught-then-direct.py kind=crash plain=1 hooked=1 MISMATCH
SHAPE q1i-finally-then-catch.py kind=declared plain=0 hooked=70 MISMATCH
SHAPES-SUMMARY shapes=17 mismatched=3
MISMATCH q1o-save-then-bare-raise.py
MISMATCH q1q-caught-then-direct.py
MISMATCH q1i-finally-then-catch.py
```
The three rows are exactly the r97/r98 hook difference (bare raise-saved, caught-then-direct,
finally-then-catch), matching the r98 declared-shapes.expected reasoning quoted in the r98 module docstring.

## Findings
1. First relabel script run folded the header line into the row dict and produced a 17-row file
   whose header row kind-cell was `kind`, causing runner `SHAPE name missing`, rc=2 — a scratch-side
   script bug, not a runner defect. Fixed by splitting header explicitly (see Run 2). The runner
   already fails loudly (rc 2, stderr) on a structurally broken freeze file rather than silently
   scoring it.
2. The runner depends only on the hook's `HOOK` attribute from the --search file, exactly as r98;
   the declared-shapes.expected per-shape reasoning was preserved in the shapes.tsv comment column
   (header contract `name<TAB>kind<TAB>plain<TAB>comment`; plain values left empty as descriptive,
   not used by the verdict).

Scratch: /fast/scratch/hyaku/souji-r99/R99ExecC1/ deleted before yield.
Tests: three runs above; no builds/lints run (editing wave).
