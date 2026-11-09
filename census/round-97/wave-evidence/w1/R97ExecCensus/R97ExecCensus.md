# R97ExecCensus — mutant census: r97 search vs frozen r96 search (r93 population)

Seat: R97ExecCensus (leaf). Lane: souji-shokunin, base 210084b. Instruments read-only (census/round-97, census/round-96, census/round-93, census/round-87).
Command shape for both runs: `--counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --jobs 5`, no `--ids`. Run (a) r97 then (b) r96, sequentially.

Hashes printed by the searches:
- r97 search sha256=b8efc240a7fb7aa02ce62cddf3c95501b5f85975278ee88cc32667a3c7af1345
- r96 search sha256=33c4bf63a68de4a0f9544373a5a361c0d1ca755ed06736383abd54406d892774
- counter fd0a8e24..., harness 1868a570..., population d6439f65... (identical in both runs)

## 1. SEARCH-SUMMARY lines

(a) r97: `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`
    `SEARCH-SUMMARY generated=278 ambiguous=9 uncompiled=0 hung=1 scored=268 errored=53 killed=139 survived=76`
(b) r96: `SEARCH-SUMMARY generated=278 ambiguous=9 uncompiled=0 hung=1 scored=268 errored=53 killed=139 survived=76`

Logs: `.ufo/waves/round-97/w1/R97ExecCensus/r97-search.log`, `.../r96-search.log`.

## 2. Difference table (verdicts)

Ids compared: 278 generated, identical id sets.
Differing verdicts between (a) and (b): **0 ids** (none crash, none non-crash).
Verdict tallies, both runs: yes=139, no=76, errored=53, skip:ambiguous=9, skip:hung=1.
SEARCH-line rc tallies, both runs: rc=1 x192 (139 killed=yes + 53 errored), rc=0 x76 (survived). No SEARCH-line rc=70 or negative.

Because the verdict diff is empty, no crash-reason attribution is needed to explain a verdict change. Crash reasons were inspected only to characterise output, below.

## 3. Crash-reason observations (harness.out, not verdict-changing)

- r97 work trees: 269 harness.out retained; 30 contain `SOUJI-R97-CRASH` reasons (924 mentions in total): uncaught RuntimeError/KeyError/ValueError/IndexError, SystemExit in main, os._exit(1).
- r96 work trees: 269 harness.out; the r96 hook writes its marker in fewer places (112 `SOUJI-R96-CRASH` mentions) and the rest of the errored rows carry a Python `Traceback` (812 mentions) in the detail field.
- Per-row (got, rc, match) tuples: 17,697 rows compared across 269 mutant files: **0 differing**. All rows with rc=70 in r97 also have rc=70 in r96. The 66 negative row rc values (`-9`, in m0277) appear in both runs.
- Differences are confined to the `detail=` text (crash-first ordering, A2 — the r97 hook writes its marker before the traceback print; r96 prints the traceback first). Tag-only diff of harness.out: the sed-normalised diff still differs in the counter path line (work-r97 vs work-r96 path) and in traceback vs marker detail text.

## 4. Survivor-set diff

`survivors-r97.json` and `survivors-r96.json` (both emitted with --emit into this seat dir): 76 records each, **byte-identical** (`diff` empty). Set equality of ids: True.

## 5. r96-host shape table (`declared-shapes.py --search census/round-96/c1-survivor-search.py`)

```
SHAPE a1-sys-exit-helper.py     kind=declared plain=3 hooked=3 ok
SHAPE a5-exit-builtin.py        kind=declared plain=3 hooked=3 ok
SHAPE a5b-quit-builtin.py       kind=declared plain=3 hooked=3 ok
SHAPE a4-caught-then-return.py  kind=declared plain=3 hooked=3 ok
SHAPE a12-module-raise.py       kind=declared plain=3 hooked=3 ok
SHAPE v1-module-raise.py        kind=declared plain=3 hooked=3 ok
SHAPE v3-func-args-pattern.py   kind=crash    plain=3 hooked=70 ok
SHAPE w1-init-helper.py         kind=crash    plain=3 hooked=70 ok
SHAPE w2-main-raise-helper.py   kind=crash    plain=3 hooked=70 ok
SHAPE a3b-try-finally-sysexit.py kind=crash   plain=3 hooked=70 ok
SHAPE t1-catch-module-falloff.py kind=declared plain=0 hooked=0 ok
SHAPE t4-reraise-at-module.py   kind=declared plain=0 hooked=0 ok
SHAPE x1-module-finally-term.py kind=crash    plain=1 hooked=1 MISMATCH
SHAPE x2-module-reraise-term.py kind=crash    plain=1 hooked=1 MISMATCH
SHAPES-SUMMARY shapes=14 mismatched=2
EXIT=1
```
Quoted: `SHAPES-SUMMARY shapes=14 mismatched=2`. Log: `.ufo/waves/round-97/w1/R97ExecCensus/r96-shapes.log`. This matches the prereg control (x1/x2 at 1, wrongly declared; the A1 trade).

## 6. Falsification check

- Non-crash verdict differences: none. The claim that "a differing non-crash id would falsify the census" is not triggered.
- `killed 139, survived 76`: reproduced in both runs.
- `errored 53`: reproduced in r97 (53). **The r96 search also returns errored=53 on this population, not the 48 the census expected.**

FALSIFIES-NUMBER: the expectation "errored 53 vs 48 = the five new fixtures" (the r96 search errored count on the r93 population being 48, so that the r97-only errored rows are the five new fixtures). Measured: frozen r96 search errored=53 on the same population, identical per-id verdicts to r97. Reproducer: `.ufo/waves/round-97/w1/R97ExecCensus/r96-search.log` (SEARCH-SUMMARY line). The five-new-fixtures attribution of the 53 vs 48 gap is therefore not reproduced; the errored count does not move between the r96 and r97 search on this population.

No FALSIFIES-WORDING. The C1 wording "the r97 sentinel/rule changes no verdict of a non-crash mutant" holds on this population: 0 verdict changes across 278 generated mutants.

## Verdict

C1 no-harm check (r97 sentinel/rule vs r96 on generated mutants of the frozen r87 counter, r93 population): **verdict-neutral on all 278 generated ids** (0 differing verdicts, 0 differing survivor records). One numeric expectation (r96 errored=48) is falsified (measured 53) — recorded as FALSIFIES-NUMBER above. Shape table on the r96 host: mismatched=2 as the prereg control predicts.

## Tooling

No tool installed or upgraded. Used only the existing lane `python3` and `bash`.

## Scratch

Scratch `/fast/scratch/hyaku/souji-r97/R97ExecCensus/` removed after copying receipts. Receipts (text only) in `.ufo/waves/round-97/w1/R97ExecCensus/receipts/`.
