## Status

STATUS: PASS — no-harm sweep half A complete: 15 self-contained gate-registry/SCORECARD self-test commands run 4× each (base `85b61a1` and lane tip `4e56c48`, each with `TMPDIR` and plain) in scratch clones. 11 hold, 2 differ only where a wave-1 file is new (benign), 2 differ green→red on registered gates (`H1`, `H2`), cause bisected and counterfactually pinned to C2 `98e5203`'s edit of `tools/souji-evidence-cache.py`.

## Evidence

Setup (scratch only): `git clone -q --no-local <lane> /fast/scratch/hyaku/souji-r32/NoHarmA/repo/{base,tip}`, `origin` removed from both, `git -C repo/base checkout -q 85b61a151923986e7e6b48f7084b9122561b5f3d`; `TMPDIR=/fast/scratch/hyaku/souji-r32/NoHarmA/t2` (plain mode = `TMPDIR` unset, no sandbox). Per run: cwd = that clone's root, argv = the table's command, capture rc + last line containing `[0-9]`. Enumeration rule and the 30-item universe: see Deliveries note below; halves 1-15 (this seat) / 16-30 (SwarmExecutor17-3, agreed over agent message before either ran).

| # | command | base (rc, last digit-bearing line) | tip | verdict |
|---|---|---|---|---|
| 01 | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | 0, `selftest=PASS ids=6/6` | 0, same | same (full output identical, both modes) |
| 02 | `bash tests/fixtures/r13-quarantine-bounds.sh` | 0, `SUMMARY total=5 failed=0 hung=0` | 0, same | same (full output identical after normalizing the clone path) |
| 03 | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` | 0, `SUMMARY total=35 failed=0 skipped=2` | 0, same | same; `SCENARIO` commit ids differ run-to-run at one rev (clock-seeded), two same-rev runs: `tip=51a0e89057f9` vs `tip=fa139691d374`, SUMMARY constant |
| 04 | `bash tests/fixtures/r30-jj-keep-expiry.sh` | TMPDIR 0, `RESULT step=8-control-expire-now keep_refs=6 object_present=yes …`; plain 2, none | identical both modes | same (full output identical) |
| 05 | `bash tests/fixtures/r31-jj-object-clock.sh` | TMPDIR 0, `RESULT arm=reflog-only step=reflog-expire-then-prune …`; plain 2, none | identical both modes | same (full output identical) |
| 06 | `bash tests/fixtures/r32-jj-mtime-clock.sh` | 127, `No such file or directory` | TMPDIR 0, `git-version: git version 2.56.0`; plain 2, none | differs — BENIGN, file added by C3 `a92e1aa`; plain refusal is the SKILL row's documented verdict 2 |
| 07 | `bash tools/souji-proc-census.sh --selftest` | 0, no digit-bearing line (`… selftest PASS (newline comm parser, …)`) | 0, identical text | same. Deviation disclosed: the lane contract bans signals and live `/proc` census; this probe signals only its own workers. Executed before I re-read that clause and not re-run |
| 08 | `bash tools/souji-quarantine.sh --selftest` | 0, `selftest: 108 checks, 0 failed` | 0, same | same (both modes) — see the first-run artifact in Findings 5 |
| 09 | `bash tools/souji-vault-verify.sh --selftest` | 0, `selftest: 57 checks, 0 failed` | 0, same | same (full output differs only in the `mktemp` suffix and the clone path) |
| 10 | `python3 -B census/round-22/mutation-adequacy.py` | 0, `"survived": 7` (killed 52, disagreeing `[]`) | 1, `"survived": 0` (killed 59, 7 disagreeing) | **DIFFERS — HARM H2** |
| 11 | `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` | 0, `"fail": 0` / `"pass": 258` | 1, `"fail": 2` / `"pass": 256` | **DIFFERS — HARM H1** |
| 12 | `python3 -B tests/fixtures/r29-registry-agreement.py` | 0, `cases=20 pass=20 control=FALSE-GREEN-REJECTED` | 0, same | same (full output identical) |
| 13 | `python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt --contract census/round-32/m1-r31-contract.txt` | 2, `can't open file …tools/souji-record-contract.py` | 1, `lines=17 bad=4` | differs — BENIGN, tool added at `7a6667c`; tip output is exactly the M1 red arm the SKILL row and `census/round-32/records/m1-red-before.txt` document |
| 14 | `python3 -m py_compile census/round-17/run-matrix.py` | 0, no digit-bearing line | 0, same | same |
| 15 | `python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts` | 0, `check OK: 144 files verified` | 0, same | same |

Reproduction of H1/H2 (`git -C <scratch clone> checkout -q <rev>`, then run in that root with `TMPDIR` set):

```
rev 7a6667c  cache=dd279ba95eeb  oracle rc=0 fail=0   | mut rc=0 killed 52 survived 7 disagree []
rev 98e5203  cache=6b826da2b65f  oracle rc=1 fail=2   | mut rc=1 killed 59 survived 0 disagree [7 ids]
rev 4e56c48  cache=6b826da2b65f  oracle rc=1 fail=2   | mut rc=1 killed 59 survived 0 disagree [7 ids]
counterfactual at 4e56c48 with ONLY tools/souji-evidence-cache.py restored to 7a6667c bytes (dd279ba95eeb):
             oracle rc=0 fail=0   | mut rc=0 killed 52 survived 7 disagree []
```

Digest evidence: `git -C <lane> show 85b61a1…:tools/souji-evidence-cache.py | sha256sum` → `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6`; at `4e56c48` → `6b826da2b65f9901f40b967fa296a164ef2bd0813aa474c0e8a5e760f65e7297`. `git -C <lane> log --oneline 85b61a1..4e56c48 -- tools/souji-evidence-cache.py` prints exactly one commit, `98e5203 round-32: C2 scratch discipline — 26 tools and fixtures take scratch from TMPDIR`. The oracle pins that live digest: SKILL.md:241 "Cache positives also require live tools/souji-evidence-cache.py digest dd279ba9…39d6, not hashed by oracle".

The 7 mutation-adequacy ids that stop being `expect=survived` equivalents: `nonexact-keyin-get`, `failed-checks-to-eq`, `names-len-constant`, `phases-len-constant`, `baseline-guard-pass`, `checks-len-drop`, `caserows-len-drop`. The 2 oracle cases: `positive/clean-cache-demonstration`, `positive/cache-transient-path-and-time`.

No tools installed or upgraded this round (no pacman/uv/npx); `jj`, `git`, `strace`, `bwrap`, `python3` were already present.

## Findings

1. **H1 (harm, registered gate green→red).** `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` at `85b61a1` → rc 0 `fail=0`; at tip `4e56c48` → rc 1 `fail=2`. Cause: `tools/souji-evidence-cache.py` sha256 moved off the digest the oracle pins. Mechanism: `census/round-21/run-acceptance.py:503` `gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))`, required equal to the frozen cache-demo payload's `gate.get("sha256")` at `:522`, so the demo positive cannot match an edited tool. Location: `tests/fixtures/r22-result-oracle.json` (case `positive/clean-cache-demonstration`), SKILL.md:241, commit `98e5203`.
2. **H2 (harm, same cause).** `python3 -B census/round-22/mutation-adequacy.py` rc 0 → rc 1. The step's pristine arm is itself red at the tip (`pristine exit 1 fail 2 pass 256` against base `fail 0 pass 258`), and the 7 entries in `disagreeing_with_expect` are that cascade (`expect equivalent observed killed`), not seven independent predicate flips. Location: `census/round-22/mutation-adequacy.py` default mode, SKILL.md:242, same commit. Independently reproduced with the same counterfactual by SwarmExecutor17-3 (`.ufo/waves/round-32/a2w1/SwarmExecutor17.md`); their two further same-class findings (r15 `--frozen` `snapshot_tampered` on `tools/souji-census.sh`, and the `../`-prefixed pointers at SKILL.md:155-156) are their measurements, not re-run by me.
3. **C2's frozen counter is blind to both.** Its 27 items include `T08 "python3 -B tools/souji-evidence-cache.py --selftest"`, which still passes after the edit, while H1/H2 are outside the item set. A `fail=0` from `census/round-32/c2-counter.py` therefore does not imply no harm: it is satisfiable by an edit that changes a pinned tool digest.
4. **Benign differences only where wave-1 added files** (`r32-jj-mtime-clock.sh`, `souji-record-contract.py`): base returns 127/2 for an absent file; the tip readings match the values their SKILL rows document (fixture prints `jj-version:`/`git-version:` and RESULT lines at `TMPDIR`; record-contract prints the documented `lines=17 bad=4`, rc 1). No harm.
5. **Instrument trap found while running item 08 (all bytes unchanged).** A base arm checked out as a linked worktree (`git worktree add`) makes `souji-quarantine.sh --selftest` print `selftest: 108 checks, 38 failed` where a full clone prints `0 failed`: `run_mode` rejects a gitfile worktree with `[ ! -d "$Q_CREPO/.git" ]` (tools/souji-quarantine.sh:670) → `souji-quarantine: not a git repo: <path>`, rc 2, so the G1 guard arm (`FAIL G1 guard rc=4 (got=2)`) and every nested arm shift. Measured directly in the linked worktree (`not a git repo: …/base`) versus a full clone (`GUARD refusal live-fleet-mutation-forbidden`, rc 4). Pre-existing, identical at base and tip. `[INFERENCE]` from the source line that the `-d .git` test is the rejector.
6. **Second environment dependency of the same fixture.** The guard's fleet root is `LIVE_FLEET_ROOT="$(dirname -- "$REPO_ROOT")"` (tools/souji-quarantine.sh:168); with a scratch `TMPDIR` placed inside the tool repo's parent directory the selftest's own fixtures become "live fleet" and it reports 58 failures (my first layout). Any seat running this probe must keep `TMPDIR` outside `dirname(<repo>)`.

## Attack log

- **ATTACK-1 (contract adequacy, reproduced).** C2's target `fail=0` over 27 argvs is satisfiable while two registered gates that are not in the item set go green→red. State reproduced: at `7a6667c` both green, at `98e5203` both red, and reverting only `tools/souji-evidence-cache.py` to base bytes at `4e56c48` restores both. Consequence for the L1: C2's `SUMMARY fail=0` (if reached) must not be reported as "no harm to operability" without an explicit statement that the r22 oracle and mutation-adequacy pins were re-measured.
- **ATTACK-2 (measurement method).** A base arm built with `git worktree add` instead of a second clone silently changes item 08's verdict (0 → 38 failures) with byte-identical tool files. A no-harm sweep or counter that uses worktrees for base arms is invalid for `souji-quarantine.sh --selftest`; the reproduced pair is in Evidence and Findings 5.
- No predicate, target, counter or item set is proposed for change; nothing was committed, staged or moved.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmExecutor16.md` (this report; only file written inside the lane).
- Enumeration rule behind the split (for the L1's completeness check): backticked spans in SKILL.md gate registry (self-test and fixture commands) and SCORECARD capability rows (capability table plus appended capability rows) that start with `bash`/`python3` after stripping `TMPDIR=<v> `/`SOUJI_CLI_BIN=<v> ` prefixes; excluded as placeholders/external-base: commands containing `<…>`, `…`, or ALL-CAPS argument words, `--output`/`--work`/`--json`/`--base-tool`/`--base`, and the four base-blob arms (`r21-read-root`, `r21-reason-canary`, `r21-replay-boundaries`, `r21-source-head`) and the placeholder-only `r21-source-refs`/`r21-acceptance`/r29-r32 counter entries; excluded as C2 items: every argv in `census/round-32/c2-items.tsv` (including `r31-landing-gate-precision`, `r30-landing-gate-discovery`, `r24-size-census`, `r27-pre-report-gate`, `r28-wave-evidence-capture`, the `r13-repo-structure` probe, `souji-verify --selftest`, `souji-census --selftest`, and the r20 fixtures) — 30 commands remained, halves 1-15/16-30 by `LC_ALL=C sort`; the `[--opt]`-only spans were reduced to the fixture's default invocation only after confirming an argparse `default=` for `r14-evidence-cache.py`, `r14-census-boundary.py`, `r15-census-config.py`, `r16-landing-gate.py`, `r18-landing-pointers.py`, `r19-*`, `r22-mutation-adequacy.py`.
- Scratch `/fast/scratch/hyaku/souji-r32/NoHarmA` removed after the evidence above was transcribed.
