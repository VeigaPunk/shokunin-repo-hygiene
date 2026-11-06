# S71MutWriter — r71 writer mutation probe (claim C1 + selftest cases 39/40)

Control (re-derivation): C1 with `--new-tool` = `git show a1db6c8…:tools/souji-receipt-write.py`
(sha256 56b6be0331d2590909984733524436ce70dd5dc699c26d7599821c956fc85207) prints
SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0
new_echo=0 errors=0 regress=PASS, EXIT=0 — the frozen C1 predicate reproduces exactly.

| id | single edit in tools/souji-receipt-write.py @a1db6c8 | C1 SUMMARY (new_forgeries/new_honest/class_mismatches) EXIT | case 39 / 40 | verdict |
|---|---|---|---|---|
| W1 | :124 drop "GIT_ATTR_SOURCE" from git() scrub tuple | 0/19/2, EXIT=1 | FAIL / ok | killed by C1 (AS1,AS2: rc=2 but class unreadable `new_findings=-`) + case 39 |
| W2 | :132 drop `-c core.fileMode=true` pin | 2/19/2, EXIT=1 | ok / FAIL | killed by C1 (FM1,FM2 now `accept`) + case 40 (`pre-run mode flip rc=0`) |
| W3 | :449-451 delete pre-run `_filter_drivers` refusal | 0/19/0, EXIT=0 | ok / ok (full 40/40) | SURVIVED |
| W4 | :559-561 delete post-run `_filter_drivers` refusal | 0/19/0, EXIT=0 | ok / ok (full 40/40) | SURVIVED |
| W5 | :155 `("clean","process")` → `("clean",)` | 0/19/0, EXIT=0 | ok / ok (full 40/40) | SURVIVED |
| W6 | :153 stop excluding attribute value `set` | 0/19/0, EXIT=0 | ok / ok (full 40/40) | SURVIVED |
| W7 | :148-149 `check-attr` failure → `return []` (fail-open) | 0/19/0, EXIT=0 | ok / ok (full 40/40) | SURVIVED |
| W8 | :147 `check-attr --cached` (index-only attributes) | 0/19/0, EXIT=0 | ok / ok (full 40/40) | SURVIVED |
| base | base bytes 118597e0… + cases 39/40 + CASES entries + FILTER_CLASS | n/a | FAIL / FAIL | cases 39/40 shown able to fail (both rc=0, receipt written) |

Findings
- HIGH (W8, instrument coverage): the only load-bearing detail of the filter witness is that `check-attr` reads the WORKTREE attribute file; nothing pins it. Probe (probes.txt, probe_w8.py): worktree-only `.gitattributes` = `".gitattributes filter=empty\ntracked.txt filter=sed\n"` with `filter.empty.clean="cat >/dev/null"`, `filter.sed.clean="sed s/dirty/clean/"`, `tracked.txt` forged `dirty\n` → `git status --porcelain` empty; candidate rc=2 RECEIPT-FILTER-DRIVER-SET / no out; W8 rc=0 and a 184-byte receipt written. C1's route list (repo config, info/attributes, committed .gitattributes, GIT_ATTR_SOURCE) omits this route and Named limits do not exclude it; candidate bytes are correct, the instruments are not. Not a falsification of the frozen predicate, a gap in what it establishes.
- MEDIUM (W3): pre-run refusal deletion is invisible — both gates refuse FC1/FC2/FC3, so either can be removed. Probe: identical poisoned fixture, wrapped `/bin/sh -c "printf ran > marker"` → candidate command_ran=False, W3 command_ran=True (rc=2 both): the wrapped command's side effects execute on a tree the writer refuses.
- MEDIUM→declared limit (W4): post-run refusal deletion survives; prereg "Named limits" declares no in-run driver-creation row, so mutant survival is a declared limit, but the post-run code path is now verified by nothing.
- LOW→declared limit (W5): process-driver row absence is declared; case 39 configures only a clean driver, so `process` is untested in code and matrix alike.
- LOW (W6): probe shows git applies no filter for a valueless `filter` attribute (check-attr "set", status ` M`), so the `b"set"` guard only changes the refusal class; no row covers valueless attributes.
- LOW (W7): the documented "refuses (exit 2) when the reads themselves fail" is untested; a quick reachability probe found none (chmod 000 .gitattributes → check-attr rc=0 "unspecified", status dirty), so severity is bounded.

Commands (from /home/vgpnk/Projects/shokunin/souji-shokunin, TMPDIR/--work under /fast/scratch/hyaku/souji-r71/S71MutWriter):
`python3 -B census/round-71/c1-counter.py --root … --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1… --new-tool <mut>/Wn.py --work <scratch>/c1/Wn` (W1-W8 + candidate control; 25-32 s each)
`python3 -B <mut>/Wn.py --selftest --work <scratch>/wst/Wn` (full 40-case suite) and run_cases.py (cases 39/40 only)
`python3 -B mut/BASE+39+40.py --selftest` cases 39/40 via run_cases.py.

Files written: .ufo/waves/round-71/w1/S71MutWriter.md; .ufo/waves/round-71/w1/S71MutWriter/{W1..W8, BASE+39+40}.py,
{W1..W8,cand}.out, base3940.out, wst/*.out, probes.txt, build_mutants.py, probe_w3.py, probe_w6.py, probe_w8.py, run_cases.py.
No lane tracked file, MANIFEST, .ufo/state, sibling repo or PATH dir was touched; no git/jj mutation was run.
