# S80Scribe — r80 w1: corpus text drafts (scribe)

Verdict: DONE — three drafts delivered; every number re-derived from committed receipts; one new probe (M3).
Touched surfaces: `.ufo/waves/round-80/w1/S80Scribe/` only. No lane tracked file written; no git mutation.

## Files written (all under .ufo/waves/round-80/w1/S80Scribe/)
- `knowledge-section.md` — 25 lines, "A session front for tools that use `$(...)` everywhere (r80, souji-quarantine.sh)".
- `quality-rows.md` — Q144, Q145 in the 5-column `| id | criterion | applies to | check | motivating evidence |` shape.
- `capability-row.md` — "signal-safe quarantine dry-run", `r80 (closure-gated)`.
- `probe-forking-setsid.txt` — probe receipt for M3.

## Re-derived from committed bytes (receipts re-read; counters NOT re-run — executor seats own that, and a concurrent heavy run disturbs the 5 s settle)
- `census/round-80/records/c1-after.txt`: `SUMMARY rows=18 mismatches=0 accepted=0 errors=0`, EXIT=0; NF6b/NF8/NF10 `got=REFUSED`.
- `census/round-80/records/c2-after.txt`: `SUMMARY rows=15 mismatches=0 errors=0 orphans=0`, EXIT=0; worst row `secs=3.9`.
- Controls: `c2-K-a-do-nothing.txt`, `c2-K-b-trap-only.txt`, `c2-K-c-no-session-kill.txt` each `mismatches=12 ... orphans=12`; p1-p3 `match=yes` in all three.
- Regressions: r13 `SUMMARY total=5 failed=0 hung=0`; selftest `selftest: 108 checks, 0 failed` (committed 100755) vs `81 checks, 51 failed` (0644 copy); r17 `total=35 failed=0 skipped=2`; trial `TRIAL identical=yes`, `result_lines_base=3 result_lines_cand=3`.
- Tool bytes: `git show 836dac3e:tools/souji-quarantine.sh` = 2010 lines (base f80f9368 = 1935), 243 `$(` (242 outside comments); `q_proc_sid` parses field 6 after `${st##*) }`; `for pass in 1..8`; `exit $((128+$2))`.

## Findings on landed bytes (L1 already integrated a variant at 60c7f50e)
- MEDIUM-1 `corpus/knowledge/gate-signal-handling.md:67-68` quotes S328 truncated at "process group leader." and drops "Otherwise, it executes a program in the current process." — the clause that carries "setsid execs in place". My draft quotes the full sentence (decompressed line 37).
- MEDIUM-2 `:73` "repeats until none is left (at most 8 passes)" overstates the code: `q_kill_session` returns 0 after pass 8 without re-checking (836dac3e:194-207), and the front prints `RECEIPT-QUARANTINE-SIGNALED` regardless (:222-232). The SIGNAL line is not evidence of a kill; the survivor census is.
- MEDIUM-3 `:81-84` limits omit the exec-in-place precondition. The front never checks `$!` is a session leader; under job control the `&` job IS a process-group leader, setsid forks, `wait` returns at once, the EXIT trap deletes the worker TMPDIR, and the tool exits 0 with no verdict. Probe: rc=0 in 140 ms, 0 output lines, worker dead on `mktemp: ... No such file or directory`. Not covered by the 15 rows (all job-control off); `bash -m` itself not exercisable here (pty unavailable: "no job control in this shell").
- LOW-4 `:63-64` "INT was held until the child ended" — K-a shows only `exited=n ... secs=5.0 tmpleft=1` at the settle; the rest is inferred from S325, not observed.
- LOW-5 `:57` title differs from the seat spec ("capture children in `$(...)`" vs "use `$(...)` everywhere"); my draft uses the spec title.

## Commands that decide the above
- `git show 836dac3e:tools/souji-quarantine.sh | wc -l` → 2010; `git show f80f9368:tools/souji-quarantine.sh | wc -l` → 1935.
- `grep -n gate_run tools/souji-pre-report-gate.sh` → 12 call sites (388-line gate), the r79 contrast in the draft.
- `PATH=$S/bin:$PATH bash $S/td/cand/tools/souji-quarantine.sh --dry-run <lane> <lane>/PROVINCE.md` → rc=0, 0 lines, 140 ms (baseline without the wrapper: rc=0, 9 lines, 6.54 s).
- `zcat census/round-80/srcs/setsid.1.gz-util-linux-2.42.4 | sed -n '30,45p'` → line 37 confirmed.
- Scratch `/fast/scratch/hyaku/souji-r80/S80Scribe` removed; `ps -eo pid,args | grep S80Scribe` → none. Disk guard at start: /fast/scratch/hyaku 49% used, 411.0G free.

## Out of scope / not done
- No counter re-run, no lane edit, no judge, no commit; C1/C2 falsification by execution belongs to the executor seats.
