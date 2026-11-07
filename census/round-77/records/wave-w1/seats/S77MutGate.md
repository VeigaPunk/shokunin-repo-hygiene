# S77MutGate — mutation test: r77 W gate (9b496b08) vs the frozen C1 counter

Baseline re-derived from committed bytes, not from L1 counts:
- W gate blob sha256=28a5135573091a253c69809c4134a3a031da014f7e1bccea5860975d127616be (= census/round-77/records/c1-after.txt:8 bind); counter → `SUMMARY rows=16 mismatches=0 errors=0 hangs=0` EXIT=0 → C1 after-claim CONFIRMED.
- Base gate d4f51563 blob sha256=90bdd8c74e38c525f2ef75b7c22fb95667035515f44724fbd3a2b1addfcc47f3 (= prereg) → `SUMMARY rows=16 mismatches=9 errors=0 hangs=8` EXIT=1, n8 clean=PASS → "9→0, 8→0" CONFIRMED.

17 single-hunk mutants (bash -n clean, diff = 1 hunk each), one fresh --work each, same counter:
| id | edit | SUMMARY | verdict |
|---|---|---|---|
| M01 | drop $GIT_DIR/info/exclude | mism=2 hangs=2 | killed (n3 n10 HANG) |
| M02 | drop $GIT_DIR/info/attributes | mism=1 hangs=1 | killed (n6) |
| M03 | drop core.excludesFile | mism=1 hangs=1 | killed (n4) |
| M04 | drop core.attributesFile | mism=1 hangs=1 | killed (n7) |
| M05 | drop the XDG default | mism=0 hangs=0 | **SURVIVOR** |
| M06 | drop the relative-path join | mism=0 hangs=0 | **SURVIVOR** |
| M07 | `! -f` → `! -e` (info loop) | mism=3 hangs=3 | killed (n3 n6 n10) |
| M08 | drop `-name .gitattributes` | mism=1 hangs=1 | killed (n5) |
| M09 | drop the find | mism=4 hangs=3 | killed (n1 n2 n5, n8 PASS) |
| M10 | find `-print -quit` | mism=0 hangs=0 | **SURVIVOR** |
| M11 | ignore the -1 scan-failure value | mism=0 hangs=0 | **SURVIVOR** |
| M12 | print a different refusal class | mism=9 hangs=0 | killed (all 9 n-rows, class text) |
| M13 | remove `timeout` from status | mism=0 hangs=0 | **SURVIVOR** |
| M14 | gate_timeout=1 | mism=0 hangs=0 | **SURVIVOR** |
| M15 | XDG name fixed to `ignore` for both keys | mism=0 hangs=0 | **SURVIVOR** |
| M16 | find `-maxdepth 1` | mism=4 hangs=3 | killed (n1 n2 n5, n8 PASS) |
| M17 | config check symlink-only (`-L`) | mism=2 hangs=2 | killed (n4 n7) |

Survivors are behavioural losses, not just counter blind spots (probe: fresh fixture, gate run in its own
session, 10 s bound, SIGKILL on the process group; pristine gate refuses in 0.0 s on every extra route).
F1 HIGH — the whole XDG-default branch is unmeasured: M05 green on C1 16/16, r76 30/30, r36 21/21; M15 green on C1 16/16 and r76 30/30. FIFO `$XDG_CONFIG_HOME/git/ignore` → pristine FAIL/RECEIPT-NONREGULAR-SOURCE, M05 HANG; FIFO `.../git/attributes` → pristine refuses, M15 HANG. Killing route: two population rows with an XDG fifo, `XDG_CONFIG_HOME` passed through run_gate (it calls `P.env_clean()` with no extras today).
F2 MEDIUM — relative `core.excludesFile` unmeasured: M06 green on C1 16/16, r76 30/30, r36 21/21; FIFO at `<clone>/xf-rel` with `core.excludesFile=xf-rel` → pristine refuses, M06 HANG. Killing route: relative config value, gate cwd outside the fixture.
F3 MEDIUM — the timeout backstop cannot be observed: M13 (timeout removed) and M14 (gate_timeout=1) are green on 16/16 (M13 also r76 30/30); ROW_TIMEOUT=30 < gate_timeout=300, so no C1 row can see it expire. Killing route: a blocking non-source route (.git/index fifo) with gate_timeout ≤5 s.
F4 LOW — M10 green: only zero/nonzero is checked, never the printed count ("%s exclude/attribute source(s)"). Killing route: a row with two fifo sources asserting the count 2.
F5 LOW — M11 green, and the `|| { echo -1; }` after `find … | wc -l` is dead code: the pipeline's status is wc's (no pipefail), so -1 is reachable only via rev-parse failure.

Files written: `.ufo/waves/round-77/w1/S77MutGate.md`, `.ufo/waves/round-77/w1/S77MutGate/receipts.txt`. Scratch `/fast/scratch/hyaku/souji-r77/S77MutGate` removed.
Commands: `c1-nonreg-counter.py --gate-dir <S>/mutants/<id> --work <S>/work-<id>` · `census/round-76/c1-evade-counter.py --gate-dir … --work …` · `tests/fixtures/r36-report-gate.py --gate … --work …` · `probe_survivors.py` (<S> = the scratch root above).
