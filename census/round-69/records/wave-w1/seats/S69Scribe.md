# S69Scribe — round-69 falsification of the C1 battery outcome split and the C2 ambient tuple

Seat: draft author + falsifier. Draft written: `.ufo/waves/round-69/w1/S69Scribe/draft-battery-outcome-split.md`.
All numbers below were re-derived by my own runs of the frozen counter; none is copied from the L1's receipt.

## Verdicts

| item | verdict | evidence |
|---|---|---|
| C1 battery outcome split | **REPRODUCED** | my run: `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, `EXIT=0`; 26 MUTANT lines, every `outcome=` equals the manifest's `expected_outcome`; `grep -c` on L1 receipt = 18/5/2/1 |
| C1 W4 item | **REPRODUCED** | my battery run: 26 `CASE W4` lines, all `base=accept`; honest candidate `CASE W4 expect=refuse base=accept new=refuse new_findings=lane worktree is dirty`; r68 before-arm `grep -c '^CASE W4 .* base=refuse' CAND.txt` = 1 |
| C1 mutant W4 label flips | **REPRODUCED** | r68 records: M-CD-SCRUB / M-CD-NCRAW / M-CD-ROOTREL are the only three with `new_findings=-`; my r69 battery shows the same three |
| C1 do-nothing | **REPRODUCED** | my run: `SUMMARY matrix=47 ... new_forgeries=3 ... EXIT=1`; the 3 forgery rows are exactly W1, W2, W4 |
| C2 clean vs ambient | **REPRODUCED** | my clean and ambient runs: `diff` of `^(CASE\|SUMMARY\|REGRESS\|EXIT=)` = **0** differing lines; both `EXIT=0`, `SUMMARY matrix=47 base_forgeries=3 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 new_echo=0 errors=0 regress=PASS`; my receipt bodies are byte-identical to the L1's `records/c2-{clean,ambient}.txt` bodies |
| C2 selftest | **REPRODUCED (value), NOT COMMITTED (artifact)** | my run: `SELFTEST cases=16 pass=16 fail=0`, `EXIT=0`; 16th check is the main two-row emit check. **No selftest receipt file exists** — `--selftest` returns before `write_receipt` (c1-counter.py:1293-1294 vs 1376/1420), so `--receipt` is ignored and the receipt cannot be produced by the documented invocation |
| C3 coverage table | **REPRODUCED** | `awk -F'\t' 'NR>1{print $5}'` = 12 `mutant` + 2 `limit`; 14 U-rows; my D18/D29 limit run gives both `outcome=survived`, `BATTERY mutants=2 ... survived=2` |

## Findings

**HIGH — D18's limit is not "no honest row exists"; the harness masks the mutant unconditionally.**
`preregistration.txt:100` gives D18's reason as "no optional index-write lock under a held index.lock
— controls/d18-limit-battery.txt". My probe reproduces that (git status rc 0, empty stderr, identical
output with and without the pin). But the deeper reason is mechanical: the counter's `clean_env()`
pins `GIT_OPTIONAL_LOCKS=0` for every git call **and for every writer slot**
(census/round-69/c1-counter.py:334, re-pinned after the scrub tuple; passed to the slot at
c1-counter.py:752). The D18 mutant deletes its own `env["GIT_OPTIONAL_LOCKS"] = "0"`
(census/round-69/battery/D18.py vs tools/souji-receipt-write.py:100) but inherits the counter's pin
from the environment, so **the git environment it hands git is identical to the honest writer's**:
`{"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_NO_REPLACE_OBJECTS": "1",
"GIT_OPTIONAL_LOCKS": "0", ...}` for both, proven by importing each writer under `clean_env()`.
The counter already knows this trap and defeats it for K7 by clearing the pin in the case env
(c1-counter.py:723-729, `GIT_CONFIG_NOSYSTEM: "0"`); no such override exists for D18, so D18 could
**never** be refuted by any row in this harness, contention row or not. Consequence: the D18 limit is
a harness artefact, not a property of the writer, and the entry must say so — the current L1 draft
(corpus/knowledge/battery-outcome-split.md, "What the split does not cover") attributes it to
git's lock behaviour and to a docs gap only.

**MEDIUM — the L1's draft mis-states the D29 limit reason.** The L1 draft says every writer
`ls-files` runs with `-C <toplevel>`, so cwd is already the toplevel and dropping `:(top)` changes
no verdict. The mutant's actual edit is narrower: `census/round-69/battery/D29.py:381` drops `:(top)`
from the **flag-check** `ls-files` only; the other two `ls-files` calls
(`battery/D29.py:119` `ls-files -s -z :(top)` and `:494` `ls-files -v -z :(top)`) keep it. The
reason it is unobservable is therefore that no row reaches a **subdirectory** `--root` for the
flag-check call, not that "every" `ls-files` is unaffected. The prereg's own wording
(preregistration.txt:101-102) is closer but still says "every writer ls-files"; my draft states the
narrower, verified reason.

**MEDIUM — the prereg's instrument list miscounts the manifest.** `preregistration.txt:25` says
"battery-manifest.tsv 27 mutants -> expected outcome"; the file has **26** mutant rows (27 lines
including the header) and the claim body at `preregistration.txt:47` says "26-mutant manifest". The
C1 predicate's own numbers (18/5/2/1 = 26) are right; only the instrument-list line is off by one.
The prompt's own brief likewise says "26 mutants" in one place and "27" in the prereg. Cosmetic,
but a frozen claim file should not carry a count that its own predicate contradicts.

**MEDIUM — `preregistration.txt:40` and `:125` cite a probe path that does not exist.**
Both cite `probe/full-battery-out.txt`; the committed file is
`census/round-69/probes/battery-probe-27-prefix.txt` (and it is a *prefix*: 27 mutants of a
28-member directory, with `BATTERY mutants=27 kills=16 ... survived=3`, and its three survivors are
K7/D10/D29 — pre-fix). The prereg's P5 pointer (`preregistration.txt:41`, `:92`) names
`probe/c2-ambient` for the **r68** before-arm, but `probes/c2-ambient.txt` is the **r69** counter
(matrix=47, `EXIT=0`, regress=PASS); the r68 before-arm is `probes/c2-before-r68-{clean,ambient}.txt`
(matrix=42, `EXIT=1`, regress=FAIL, 6 differing lines — which I reproduce). Both pointers are
wrong; the substance survives at the corrected paths.

**LOW — `probes/c2-{clean,ambient}.txt` carry a stale instrument digest.**
Both name `instrument_sha256=127b06be31ea5b71625cccbb43595b389f7959cdd80a433ffc311eeba6241898`.
The frozen counter is `40757709e5adef00ef86c63fb4b554c03cce80e197747e389d76f58d4c2f5130`, and I
scanned **all 14779 blobs** in the lane: `127b06be...` matches no committed blob, while the frozen
counter's and the writer's digests both matched (control passed). So those two committed probe files
were produced by an instrument revision that exists nowhere in the repository — they are superseded
runs and must not be cited as evidence for the frozen counter.

**LOW — `preregistration.txt:125` claims the probe battery's three survivors were "fixed (K7, D10)"
before the freeze, but the committed coverage table at the freeze records D10 as `forgery` while
the committed probe shows `outcome=survived`.** The freeze-time `records/declared-coverage.tsv`
already says D10 observed=`forgery` (byte-identical to the current file), yet the committed pre-freeze
probe `probes/battery-probe-27-prefix.txt` says `MUTANT D10 outcome=survived`. Both are frozen in
the same commit. The after-arm run does reproduce D10=`forgery` (my run), so the final state is
right; the frozen table simply states the post-fix outcome before the fix is observable in any
committed receipt.

## Commands I ran (all from the lane root, scratch under $HYAKU_SCRATCH/souji-r69/S69Scribe)

```
python3 -B census/round-69/c1-counter.py --root <LANE> --matrix census/round-69/c1-matrix.tsv \
  --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work $S/work-battery \
  --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery
python3 -B census/round-69/c1-counter.py --selftest --root <LANE> --matrix census/round-69/c1-matrix.tsv \
  --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work $S/work-selftest
python3 -B census/round-69/c1-counter.py --root <LANE> --matrix census/round-69/c1-matrix.tsv \
  --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev 893b8ef4e73b3fde45f712df3437a032b1d92d42 \
  --tool tools/souji-receipt-write.py --work $S/work-c2clean            # clean
env -i PATH="$PATH" HOME=$S/amb/home XDG_CONFIG_HOME=$S/amb/xdg GIT_TRACE=1 \
  GIT_TRACE2_EVENT=$S/amb/trace2-event.json GIT_TRACE2_PERF=$S/amb/trace2-perf.txt \
  python3 -B census/round-69/c1-counter.py ... --work $S/work-c2amb      # ambient
python3 -B census/round-69/c1-counter.py --root <LANE> --matrix census/round-69/c1-matrix.tsv \
  --base-rev 3639087917eaeb28719d7603110a6ec22782100e --new-tool $S/base-writer.py --work $S/work-donothing
python3 -B census/round-69/c1-counter.py --root <LANE> --matrix census/round-69/c1-matrix.tsv \
  --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work $S/work-limits \
  --battery-manifest census/round-69/battery-limits.tsv --battery-dir census/round-69/battery
```
Plus: `git show`/`ls-tree`/`cat-file --batch-all-objects` (read-only) for digests and blob scans; a
throwaway `mktemp -d` fixture repo for the index.lock and fsmonitor probes (toplevel asserted before
the first commit); and a python probe importing each writer under the counter's `clean_env()` to
compare the git environments.

## Files I wrote
- `.ufo/waves/round-69/w1/S69Scribe/draft-battery-outcome-split.md` — the knowledge-entry draft
- `.ufo/waves/round-69/w1/S69Scribe.md` — this report

No lane tracked file was edited; no commit, push, stash, reset or checkout was run; no tool was
installed or upgraded (none was needed).

## Out of scope for this seat
The wider-tuple immunity gap (GIT_ATTR_SOURCE / GIT_EXEC_PATH / GIT_TEMPLATE_DIR flipping 100 lines)
is another seat's finding (`.ufo/waves/round-69/w1/S69ExecAmbient.md`); I did not re-measure it and
my draft claims ambient immunity only under the frozen tuple, which is what the predicate asks.
