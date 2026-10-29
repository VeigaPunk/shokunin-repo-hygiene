# R42w2executor02 — execution-count and anti-sniffing audit (C3 fixture, C2 tool)

Tip under attack: 3105a63b23481fccf7df58e74d14a6681e0ea0c8 (working tree). Nothing in the lane was written; scratch deleted. Receipts are in `.ufo/waves/round-42/w2/R42w2executor02/` (paths below relative to that directory).

## Commands actually run
1. `TMPDIR=<scratch>/a python3 -B .ufo/waves/round-42/audit-candidates.py c3 tests/fixtures/r42-drift-conditions.py --scratch <scratch>/a` -> 
   `wrapper run rc=0 cases=13 fail=0 invocations=13` / `AUDIT c3 findings=0`
2. Own C3 shim: `PATH=<shim>:$PATH TMPDIR=<work> python3 -B tests/fixtures/r42-drift-conditions.py --tool c3-wrap.py --work <work>`; c3-wrap.py runs the real pinned tool as a subprocess and appends one JSON line (argv, cwd, rc, seconds, stdout/stderr head) per invocation to `c3-tool-calls.jsonl`; a PATH `git` shim logs the first argv word of every git call (`c3-git-subcommands.log`). Fixture output (`c3-run.txt`): 13 PASS, `SUMMARY cases=13 pass=13 fail=0`.
3. Own C2 shim, direct: `env PATH=shimA:$PATH PYTHONPATH=<py> TMPDIR=<t1> python3 -B tools/souji-freeze-check.py --selftest` -> `SELFTEST cases=31 pass=31 fail=0`, rc=0. shimA/git logs `<tag> <argv>` (tag T = the call carries GIT_NO_REPLACE_OBJECTS=1, i.e. the tool's own `Repo.run`; tag S = the selftest's fixture-building git calls). `sitecustomize.py` wraps `hashlib.sha256` to log each call. (First attempt logged nothing: the tool whitelists its env, so a `$GITLOG` variable never reached the shim; shims were rebuilt with hard-coded log paths. That attempt is discarded.)
4. Counter with the same shim: `env PATH=shimB:$PATH TMPDIR=<t2> python3 -B census/round-42/c2-counter.py --root <lane> --rev 3105a63b… --scratch <sc>` -> `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb` (receipts `c2-counter-git-calls.log`, 3867 calls).

## C3 table: case -> invocations -> argument shapes (every case exactly 1 tool invocation; 13 total; fixture runs 17 `git init` + the tool itself issues 18 `git --no-optional-locks …` calls)
| case | invocations | args shape | rc / observed |
|---|---|---|---|
| default-timeout-outlasts-a-blocked-git | 1 | --root R --record REC --skip-unrecorded (no --timeout) | rc1, 40.13 s, `DRIFT UNREACHABLE t list-timeout` |
| fifo-record-is-refused-not-blocked | 1 | --root --record --skip-unrecorded | rc2, `REFUSAL RECORD-MALFORMED` |
| gitdir-sibling-prefix-is-outside | 1 | same | rc2, `REFUSAL RECORD-OUTSIDE-ROOT … s gitdir` |
| invalid-utf8-in-record-becomes-replacement-char | 1 | + `--json O/o.json` | rc1, `DRIFT ABSENT a\ufffdb` |
| list-nonzero-rc-is-reported-unreachable | 1 | --root --record --skip-unrecorded | rc1, `UNREACHABLE:list-rc=128` |
| list-timeout-is-reported-unreachable | 1 | + `--timeout 1` | rc1, 2.12 s, `UNREACHABLE:list-timeout` |
| longer-old-json-is-truncated-on-write | 1 | + `--json O/old.json` | rc0, SUMMARY only |
| record-option-is-required | 1 | `--root R` only | rc2, argparse usage |
| root-option-is-required | 1 | `--record REC` only | rc2, argparse usage |
| root-sibling-prefix-is-outside | 1 | --root --record --skip-unrecorded | rc2, `RECORD-OUTSIDE-ROOT ../root2` |
| symlinked-child-is-not-discovered | 1 | --root --record (no --skip-unrecorded) | rc1, `DRIFT UNRECORDED u2` |
| timeout-of-one-is-accepted | 1 | + `--timeout 1` | rc1, `DRIFT ABSENT a` |
| two-digit-regs-are-read-whole | 1 | --root --record --skip-unrecorded | rc1, `REGS-CHANGED r record=10 live=1` |

Cases that never invoke the tool: none. Every case's observed stdout/stderr token matches the case name's claimed behaviour (see `c3-tool-calls.jsonl`). No case takes more than one invocation, so no case is invoked with a second argument set to compare (a single-observation design is a possible weakness for flakiness, not for sniffing). The fixture passes a *wrapper path* as --tool and still goes green, so it neither hashes nor reads tool bytes (also audit-candidates.py static scan: findings=0).

## C2 call profile (git subprocess calls by subcommand; T = tool-side, S = selftest scaffolding)
| artifact | calls by kind | suspicious? |
|---|---|---|
| `--selftest` (31 cases) | T: cat-file blob 166, ls-tree 54, rev-parse 59, `log --diff-filter=A` (freeze) 29, `log --diff-filter=A --name-only` (dispatch) 29, `merge-base --is-ancestor` 32 (=369 tool calls). S: add 64, commit 64, commit-tree 31, init 31, rev-parse 94 (=284). sha256 calls: 54 | no |
| counter, 37-case run + real/retro/retro_clean + selftest + 3 patch legs | T: cat-file blob 764, ls-tree 240, rev-parse 287, `log --diff-filter=A` 125, `…--name-only` 124, merge-base 112 (=1652 tool calls, of which 369 are the unpatched selftest). S: add 505, commit 505, commit-tree 124, init 232, rev-parse 841, checkout 6, cat-file -e 1, show 1. Stub tools (control_clean/control_findings) issue 0 tool-side git calls | no |

Answers: yes, the selftest really runs `log --diff-filter=A` (58 calls: 29 freeze + 29 dispatch), `merge-base --is-ancestor` (32), `cat-file blob` (166), `ls-tree` symlink checks (54) and SHA-256 hashing (54 calls). The 29 freeze-log calls = 31 cases minus the two rc2 cases (rev-unresolved, prereg-absent), which stop before the log, consistent with the case table. All git calls run through the whitelisted-env `Repo.run` (no S-tagged call carries `core.quotePath`). The patch legs' targets (hashlib.sha256, `--diff-filter=A`, `merge-base`) are all exercised by the unpatched selftest, so P1/P2/P3 intercept real calls (the python-level patch means the shim does not log the patched legs; their rc != 0 is from the counter's own output, patches=3/3).

## Verdict
No case/exercise gap and no sniffing signature found. C3: 13/13 cases invoke the tool exactly once with distinct, behaviour-relevant args; fixture survives a path-changing wrapper. C2: self-test is a genuine exerciser of digest, freeze-detection, ancestry, symlink and blob code; counter's 37 cases reproduce the same call kinds at ~4.5x volume. Observations only (not defects): C3 cases are single-shot (no repeat); `default-timeout-outlasts-a-blocked-git` costs 40 s wall (it dominates the fixture's ~45 s).
