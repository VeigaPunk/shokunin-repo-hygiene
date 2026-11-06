# S74Sentinel — fail-closed review, tools/souji-pre-report-gate.sh @ ec13ba7fac9085005dca2e69ee12a2933d2c22a5

Commands (lane root; SCRATCH=/fast/scratch/hyaku/souji-r74/S74Sentinel, now removed; gate+writer copies at ec13ba7f in $SCRATCH/gate):
`python3 -B census/round-74/c1-gate-counter.py --gate tools/souji-pre-report-gate.sh --work $SCRATCH/c1`
`bash .ufo/waves/round-74/w1/S74Sentinel/probe-{exec,env,resource,splitstatus}.sh $SCRATCH $SCRATCH/gate`; `python3 -B .../probe-echo.py --scratch $SCRATCH --gate $SCRATCH/gate`
`bash tests/fixtures/r27-pre-report-gate.sh`; `python3 -B tests/fixtures/r36-report-gate.py --work $SCRATCH/w36`

**C1 headline reproduced from committed bytes**: `SUMMARY rows=9 mismatches=0 errors=0` / `EXIT=0` (own run, gate sha256 3162de98…). Fixtures: r27 `cases=4 pass=4 control=FALSE-GREEN-REJECTED`; r36 `SUMMARY cases=21 pass=21 fail=0` + `control=STUB-REJECTED` + `control=VACUOUS-CHECKER-REJECTED`. No pre-existing behaviour regressed.
**C1 predicate (iii) is unevidenced**: `census/round-74/records/c1-domain-trial.txt` does not exist at HEAD 8fe48c86; the string occurs only in `preregistration.txt`. The lane is currently dirty (` M SCORECARD.md SKILL.md corpus/…`), so that trial would FAIL if run now.

## Route table
| input | verdict |
|---|---|
| CWD `subprocess.py` hidden by `.git/info/exclude` | **EXEC + fail-open** (HIGH-1a) |
| planted `tools/__pycache__/souji-receipt-write.cpython-314.pyc` | **EXEC + fail-open** (HIGH-1b) |
| `PYTHONPATH=<dir>/subprocess.py` / `BASH_ENV=<payload>` / PATH-shadowed `python3` | **EXEC + fail-open** |
| repo-local `core.fsmonitor` + `--fsmonitor-valid`, plain edit | **PASS on dirty bytes** (HIGH-2) |
| `importlib/` shadow in CWD; `sitecustomize.py` in CWD; `PYTHONSTARTUP`; `PYTHONINSPECT` | SKIP (frozen `importlib.util`; site runs before `sys.path[0]=''`; non-interactive) |
| `PYTHONHOME=/nonexistent`; `PYTHONSAFEPATH=1`; gate via symlink; writer absent | clean-refuse (`check-clean=FAIL`) |
| `--lane` naming a different clean repo | SKIP — check 4 validates a tree the report does not name |
| tracked FIFO; tracked symlink loop (`a→a`); `--prereg` FIFO | clean-refuse, 0.01 s / 0.13 s |
| tracked 2 GiB sparse file | ok 5.28 s, rss 22.9 MB |
| 200 000-entry index | ok 5.42 s, rss 114.6 MB |
| `--report` FIFO; `--report /dev/zero` | **HANG** (`grep -c` at line 33 opens a reader-less stream; killed at 20 s) |
| status-listed hostile name | ok — porcelain quotes (`" M \"esc\\033[31mred…\""`) |
| stat-forged hostile name | **raw bytes/ESC echoed** (MEDIUM-1) |

## Findings
**HIGH-1 — the gate's check-4 python child is code-injectable, and injection makes it lie.** `gate-w.sh:45` runs `python3 -B - …` with no `-I`/`-P`, so `sys.path[0]=''` (the caller's CWD) and the writer's `import subprocess` resolves from there. A gitignored/`exclude`d `subprocess.py` ending `sys.exit(0)` yields `truth=""` → `check-clean=PASS`, `exit=0`, on a lane whose `hash-object` (75a69bc3…) ≠ index oid (d075eae2…). The real lane's `.gitignore` already carries `__pycache__/`, so a planted pyc beside the lane's own writer needs no worktree evidence at all. Evidence: `raw/eA-out.txt`, `raw/eB-out.txt`, `raw/eC-out.txt`, `raw/v1-out.txt`, `raw/v2-out.txt`. **Remediation**: `python3 -I -B` (isolated mode ignores PYTHON* and drops the CWD from `sys.path`).
**HIGH-2 — a plain dirty lane passes check 4.** Gate line 43 reads `git … status` with no config pinning; the writer pins `-c core.fsmonitor=false` (`souji-receipt-write.py:159`). With repo-local `core.fsmonitor=<hook printing "/">` + `git update-index --fsmonitor-valid a.txt`, the gate sees `0` status lines and proceeds, while `_truth_refusal` sees ` M a.txt`, puts it in `listed`, **skips it** (`souji-receipt-write.py:283`), finds `bad` empty and returns `None` → `check-clean=PASS`, `EXIT=0`, with worktree 61742046… vs index d075eae2…. Reproduced under the counter's own env (`HOME`/`GIT_*` scrubbed, `GIT_CONFIG_GLOBAL=/dev/null`). Evidence: `raw/ss2-out.txt`. This is the writer's own r62 `case_16_fsmonitor_silenced` threat, re-opened by the wrapper. **Remediation**: pin `-c core.fsmonitor=false -c core.checkStat=default -c core.trustctime=true` on gate line 43, and make `_truth_refusal` return a refusal when `listed` is non-empty.
**MEDIUM-1 — no-echo (D30: "no refusal message prints a caller value", census/round-68/…/S68ScoutDeclared/summary.md:46).** `_truth_refusal` interpolates raw path bytes (`os.fsdecode(p)`, writer:309) and `gate-w.sh:56` prints them with `%s`; a tracked name `inj\ncheck-clean=PASS\n<ESC>[2Jz.txt` makes the gate's merged stderr contain a line reading exactly `check-clean=PASS` plus a raw ESC. Impact bounded: `c1-gate-counter.py:190` reads stdout only and takes the **first** match, so the frozen instrument cannot be flipped; receipts/terminals and any `grep -c` consumer can. **Remediation**: print the count only, or C-quote the names (`_cquote`, writer:227).
**MEDIUM-2 — `--report` is unbounded.** `-s` is false for a FIFO/`/dev/zero`, then `grep -c` blocks forever (`gate-w.sh:33`). Fail-closed gates must not hang on caller input.
**LOW** — (a) `2>&1` at line 43 turns a git warning into `check-clean=FAIL` on an honest tree (`warning: could not open directory 'sub/': Permission denied`, rc 0); (b) a missing/oddly-located writer yields a raw Python traceback instead of a named refusal, and no r27/r36 case covers it; (c) `PATH`, `BASH_ENV` and `python3` are unpinned while 27 `GIT_*` vars are scrubbed — an inconsistent threat model; (d) `--lane` is caller-trusted, so check 4 can be pointed at a different tree.
**ok** — FIFO/symlink-loop/2 GiB/200k paths neither hang nor exhaust (≤115 MB); the `.git/config`-hidden index flags `--skip-worktree` are still caught by the hash, so HIGH-2 is specific to the two-status-reader split.

Files written: `.ufo/waves/round-74/w1/S74Sentinel.md`, `S74Sentinel/{mkfixture.py,probe-exec.sh,probe-env.sh,probe-resource.sh,probe-echo.py,probe-splitstatus.sh}`, `S74Sentinel/raw/{e0,eA,eB,eC,v1..v7,r5,r6,r7,ss2}-*.txt`, `S74Sentinel/raw/gate-w.sh`. No tool installs; scratch removed; no lane tracked file touched.
