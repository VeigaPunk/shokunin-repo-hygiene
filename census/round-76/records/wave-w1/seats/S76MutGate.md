# S76MutGate — mutation test of the r76 C1 gate block (souji r76 w1, falsification seat)

Baseline first (byte truth): gate+writer at e827d2b (gate blob 7a8eec51, same blob at 113b0072) → `python3 -B census/round-76/c1-evade-counter.py --gate-dir /fast/scratch/hyaku/souji-r76/S76MutGate/base --work .../work-base` = `SUMMARY rows=30 mismatches=0 errors=0`, EXIT=0; gate sha256 18587bd2ff103f8ee136a3b6e59e96039f3202e06c688a8ecb7c8f4bf76623ad, writer 70bbf1c2…. Candidate block spans tools/souji-pre-report-gate.sh:111-144.
17 single-edit mutants (build_mutants.py; every anchor asserted to occur exactly once; writer bytes unchanged in each gate dir); each run: `python3 -B census/round-76/c1-evade-counter.py --gate-dir <scratch>/mut/<ID> --work <fresh>`.

| id | edit (line in @e827d2b gate) | SUMMARY / EXIT | verdict |
|---|---|---|---|
| M01 | L138 drop `src in tracked and` | mism=4 / 1 (f7 f9 f10 f14 PASS) | killed |
| M02 | L138 drop `basename(src)==b".gitignore"` | mism=0 / 0 | SURVIVOR LOW-2 |
| M03 | L139 drop `(d=="" or path.startswith(d+"/"))` | mism=0 / 0 | SURVIVOR LOW-2 |
| M04 | L138 drop `not pat.startswith(b"!")` | mism=0 / 0 | SURVIVOR LOW-3 |
| M05 | L125 drop `-c core.excludesFile=/dev/null` | mism=0 / 0 | SURVIVOR LOW-4 |
| M06 | L125 drop `-n` | mism=0 / 0 | SURVIVOR LOW-4 |
| M07 | L128 accept any check-ignore rc | mism=0 / 0 | SURVIVOR LOW-5 |
| M08 | L134-136 skip echoed-path check | mism=0 / 0 | SURVIVOR LOW-3 |
| M09 | L141 `if undeclared:` → `> 1` | mism=0 / 0 | SURVIVOR **HIGH-1** |
| M10 | L116 `--cached` → `--others` | mism=8 / 1 (f2 f6 f7 f9 f10 f11 f12 f14) | killed |
| M11 | L122 `--exclude-standard` → `--exclude-per-directory=.gitignore` | mism=0 / 0 | SURVIVOR LOW-6 |
| M12 | L144 `sys.exit(1)` → `sys.exit(0)` on undeclared | mism=4 / 1 (f7 f9 f10 f14) | killed |
| M13 | L128 drop `len(rec) != 4*len(ign)+1` | mism=0 / 0 | SURVIVOR LOW-3 |
| M14 | delete block 111-144 (control) | mism=4 / 1 (f7 f9 f10 f14) | killed |
| M15 | L137 `d = os.path.dirname(src)` → `d = b""` | mism=0 / 0 | SURVIVOR LOW-2 |
| M16 | L138 invert `not pat.startswith(b"!")` | mism=4 / 1 (f2 f6 f11 f12) | killed |
| M17 | L121 `tracked = set()` | mism=4 / 1 (f2 f6 f11 f12) | killed |

**HIGH-1 (M09 survives; threshold is unmeasured).** Every route the new block actually decides carries exactly 2 undeclared paths — `UNDECLARED-IGNORE: 2` for f7/f9/f10/f14 on my re-built fixtures (probe3) — so `>1` is indistinguishable from `>0` on the frozen 30-row population, and both regression conjuncts stay green on M09: `SUMMARY cases=21 pass=21 fail=0` (r36) and `cases=4 pass=4` (r27). Divergence proven on two fixtures (pristine FAIL, M09 check-clean=PASS): K1 `pl/.gitignore` = `/.gitignore` alone (1 undeclared, pristine `UNDECLARED-IGNORE: 1`); K2 tracked root rule `cache/.gitignore` + untracked `cache/.gitignore` = `*.bin` + untracked `cache/x.bin` → 1 undeclared with a real hidden payload (`check-ignore`: `cache/.gitignore|1|*.bin|cache/x.bin`). Proposed killing route: add K1 and K2 to census/round-76/c1-population.tsv with expect=FAIL.
**LOW-2 (M02, M03, M15).** Equivalent: with core.excludesFile attributed away, check-ignore sources are per-directory `.gitignore` files or `$GIT_DIR/info/exclude` (gitignore(5)); nothing under `.git` can be indexed (`git add -f .git/info/probe3` → rc 0, index unchanged), so `src in tracked` already implies `.gitignore`; and a per-dir `.gitignore` only decides paths beneath it (eqprobe: `a/.gitignore|1|*.log|a/x.log`, `b/x.log` unmatched). Predicates unreachable, not wrong.
**LOW-3 (M04, M08, M13).** Equivalent on all constructible inputs: a path whose last match is a `!` pattern is not ignored (eqprobe: keep.txt shown as `|2|!keep.txt|keep.txt`, absent from `ls-files --ignored`); `check-ignore --stdin` echoes its input verbatim (incl. the space path probe); NUL records are always 4·N+1 when git exits 0/1.
**LOW-4 (M05, M06).** Message-only: route f3 (repo core.excludesFile) is already refused by the writer's pinned status (`souji-receipt-write.py:159` pins `core.excludesFile=/dev/null`) — pristine and M05/M06/M09/M11 all print `pinned git status … lists 1 record(s)` on the counter's own f3 fixture; unmatched-without-`-n` paths can therefore never reach the verdict. The counter cannot tell whether `/dev/null` attribution or `-n` exists.
**LOW-5 (M07).** Unreachable: the gate builds the check-ignore argv itself (`--stdin` only), so rc≥2 with a well-formed 4N record set cannot be produced by any route.
**LOW-6 (M11).** Provable equivalence after the earlier layer: `hidden = std − perdir = ∅` implies std ⊆ perdir, and perdir ⊆ std, so `ign` is the identical set.
Verdict: the block's core protection IS measured (M01/M12/M14/M16/M17 killed; f7's relabel is what kills four of them) but the population's four forgery routes all carry two undeclared paths, leaving one HIGH sensitivity gap (M09) that the counter, r36 and r27 all fail to see. No lane byte was modified (only scratch copies); no tool installed.

Files written: .ufo/waves/round-76/w1/S76MutGate.md, .ufo/waves/round-76/w1/S76MutGate/receipts.txt (mutant table, SUMMARY lines, probe outputs, r36/r27 lines). Scratch /fast/scratch/hyaku/souji-r76/S76MutGate removed after copying receipts.
