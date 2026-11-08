# souji round 82 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane round 82, base `488956c45166ed6edc21567e8588a8134413949e`, after `44e074018b2acb89f6143195d34c5c90237e8655`
(branch `master`, `local=remote`, `ahead=0`). Report `.ufo/reports/round-82/souji.md` (fleet repo commit
`3c44e8d0d4e5f2f16e5d3c11cdd3459510780c7a`, author `souji-shokunin`). Driver digest (`.ufo/watchdog.log`):
`2026-11-07T22:59:00-03:00 launch souji round=82 pgid=3437660 driver=hyaku-inline attempt=1`;
`2026-11-08T01:16:28-03:00 complete souji round=82; hyaku-inline attempt=1` (attempts 1–3 of 2026-11-07 07:13–07:17 are
the same round's dead launches, no commit — nothing inherited: `jj-lane.sh state` at start equals the base).

Outcome: status `ok`, **admitted**. C1 verifies (re-measured by me on the tip bytes, with the r81 before-control and
the K-b ablation re-run); C2 verifies on its frozen predicate at the tip bytes under **both** launches (re-measured by
me), with the base before-control reproduced in both launches; the W2 harm is closed by R1 and the filed bytes pass.
No owned axis is harmed.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by the lane identity | `git log --format='%an %H' -- .ufo/reports/round-82/souji.md` | `souji-shokunin 3c44e8d0d4e5f2f16e5d3c11cdd3459510780c7a`; commit touches only that path (184 insertions) | pass |
| `## SHONEN` heading, one line per box | read report; `grep -n '^## SHONEN'` | line 143; 4 lines, all `[~]` with resolvable pointers; `SHONEN.md` holds the same 4 boxes | pass |
| cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <h> master` over 10 hashes (P `1cb7c7d1`, F `d302b4f3`, F2 `28fd32c0`, F3 `1ec433c6`, W1 `f5bc4197`, W2 `73110f6f`, A `9881676a`, wave `7dc3c726`, W3 `c5c3f087`, tip `44e07401`) | 10/10 ancestor; every round commit authored `souji-shokunin <souji@shokunin.local>` | pass |
| lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `branch=master local=remote=44e07401… ahead=0 behind=0 head=detached tracked=0 untracked=0`; empty | pass |
| prompt carries the template contract | read `.ufo/prompts/souji-round-82.md` | §1 MISSION/AXES binding, §2 1–3 claims + lowest non-retired axis + causal separability, §2b frontier step + frozen census command, §3 L2 floor ≥8 + role split, §4 report contract + marker rule + SHONEN/commit-hash rules, §5 commit-then-push + push scope + L0, §6 hyaku addendum — matches `templates/round-prompt.md` | pass |
| marker vs report | report names real work, 10 resolvable commits, evidence pointers | not a marker | pass |

Status-neutral observations (named, not defects on the status):

- The report's commit chain omits `51a5e7fa` (`round-82: freeze receipt and lesson M1/M2`, the commit that carries
  `records/freeze-check-at-P.txt`), and the **Landed changes** table has no row for it. The freeze-check receipt is
  cited by lesson M1 and by the SCORECARD addendum, so the evidence resolves; the chain is incomplete.
- The dispatch prompt §3 requires a `planner` seat. The wave has none, and the report's justification ("validator
  forbids a `planner` seat") is not visible in `scripts/hyaku/ufo-wave-policy.json` (which defines a `planner` role
  under `nativeProfiles`). Unverified; routed.
- Attack share: the report's 8/14 = 57 % uses the falsification tool's wider `ATTACK_ROLES` (which counts sentinel and
  connector); the run-15 map enumerates reviewer/critic/mutation-tester/labrat only, giving 5/14 = 36 %. Both clear
  the 25 % floor; the label, not the floor, is at stake.
- The dead seat `S82ExecC2` is reported dead (87-byte stub), not back-filled, and C2 lost no conjunct: three other
  seats re-derived it and I re-derived it again below.

## 2. Claims

Both claims rest on lane-owned instruments and on the tool's own selftest/r17/probe set. Per PROTOCOL §Gate standard
(Closure consequence) I executed no sibling gate: **re-measured** below means I ran the committed counter bytes
myself from the lane root against scratch dirs under `/home/vgpnk/Projects/shokunin/.scratch/` (the instruments refuse
`/tmp`); **evidence-verified** means I re-read committed receipts and re-hashed the bytes they bind.

Instrument and candidate digests (`sha256sum`; the receipt's own binding in parentheses):

| object | at base `488956c4` | at W1/W2 `f5bc4197`/`73110f6f` | at tip `44e07401` | receipt binding | result |
|---|---|---|---|---|---|
| `census/round-82/c1-false-row-harness.py` | absent | `a45a9022…ff73` | `a45a9022…ff73` | `a45a9022…` | frozen |
| `census/round-82/c1-false-rows.tsv` | absent | `c7d4a1ef…2ebd82` | same | `c7d4a1ef…` | frozen |
| `census/round-82/c1-pointer-counter.py` | absent | `cbfdc07c…db1875a` | same | `cbfdc07c…` | candidate, unchanged to tip |
| `census/round-82/c1-false-row-harness.py` of r81 used for the regression | `292bf75e…3166d` | same | same | `292bf75e…` | frozen |
| `census/round-82/c2-vault-signal-counter.py` | absent | `d1a43e08…81d0df` | same | `d1a43e08…` | frozen |
| `census/round-82/c2-population.tsv` | absent | `09628eec…42ca6f` | same | `09628eec…` | frozen |
| `tools/souji-vault-verify.sh` | `89a2ed8c…32e16` (base) | `556ad94a…10c032` (W2) | `dd6d440e…5855e1a` (R1) | W2 receipts bind `556ad94a…`, R1 receipts bind `dd6d440e…` | tip = R1; `git show c5c3f087:tools/souji-vault-verify.sh \| sha256sum` = `dd6d440e…`, so R1's digest-bound working-tree measurement resolves at the pushed commit |

### C1 — calibration (lowest owned non-retired axis, 7): **verified** (re-measured)

Command I ran from the lane root:

```
python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin \
  --work /home/vgpnk/Projects/shokunin/.scratch/souji82-c1
```

Observed: `SUMMARY rows=32 mismatches=0 accepted=0 refused_true=0 errors=0`, `EXIT=0`. All 32 rows `match=yes`; the
four own-tree/full-suffix decoys `NF-F`, `NF-G`, `NF-H`, `NF-I` each `got=REFUSED rc=1`; `PF-1`, `TF4`, `TF5`
`got=MOVED`. That is the reported after, byte-for-byte in its summary line.

Before, same harness with the frozen r81 counter (`census/round-81/c1-pointer-counter.py`): `SUMMARY rows=32
mismatches=2 accepted=2 refused_true=0 errors=0`, `EXIT=1`, and the two `match=no` rows are exactly `NF-F` and `NF-G`
(each `got=MOVED`). Delta delivered by the new rule, reproduced.

Ablation: the same harness with `census/round-82/controls/variants/c1-K-b-owntree-dropped.py` → `rows=32 mismatches=2
accepted=2`. I read the code diff (`diff <(git show 488956c4:census/round-81/c1-pointer-counter.py)
census/round-82/controls/variants/c1-K-b-owntree-dropped.py`): the K-b variant differs from the r81 counter in line 2
(docstring) only, and the r82 counter adds `_owntree_ok` plus two `elif` branches. The second branch (census-in-tree
full suffix) cannot fire on this population (no token under `census/`), so K-b is the exact ablation of the round's
own-tree rule *as this population exercises it*; A4's reconciliation of S82Connector F1 holds. Caveat, not a defect:
K-a and K-b are the same measurement (`accepted=2` both), so they are one control run twice, not two independent
controls.

Regression spot re-run by me: `python3 -B census/round-81/c1-false-row-harness.py --counter
census/round-82/c1-pointer-counter.py …` → `SUMMARY rows=25 mismatches=0 accepted=0 refused_true=0 errors=0`, `EXIT=0`,
equal to `records/c1-regress-r81-harness.txt`. The other four regression receipts were evidence-verified only
(`r78 items=22 resolved=22` + `forged=12 matched=12 accepted=0`; `r77 items=35 resolved=35` + `forged=7 matched=7
accepted=0`; r79 `rows=9 mismatches=0`; r80 `rows=18 mismatches=0`).

Limits carried as stated limits, not defects: the own-tree rule refuses a genuine move into the lane's real `wN/`
directories (`CAPTURE` accepts only `waves/|wave/|records/wave-<w>/`; the lane's trees are `w1` 65, `w2` 19, `w3`,
`a2w1`); the identity disjunct is inseparable from a suffix-only rule on this population; the census-in-tree branch is
dead; `NF-C` remains accepted. Q150/Q151 record the two criteria the wave mined.

### C2 — operability (8): **verified** (re-measured at the tip bytes, both launches, with the base before-control)

Command I ran at the tip bytes (`tools/souji-vault-verify.sh`, `dd6d440e…`):

```
python3 -B census/round-82/c2-vault-signal-counter.py --tool tools/souji-vault-verify.sh \
  --work /home/vgpnk/Projects/shokunin/.scratch/souji82-c2        # and the same under env SHELLOPTS=monitor
```

Observed default: `SUMMARY rows=16 mismatches=0 errors=0 orphans=0`, `EXIT=0`. Observed monitor:
`SUMMARY rows=16 mismatches=0 errors=0 orphans=0`, `EXIT=0`. 0 rows `match=no` in either run.

Before-controls I re-ran on the base bytes (`git show 488956c4:tools/souji-vault-verify.sh`, sha256 `89a2ed8c…`):
monitor launch → `rows=16 mismatches=4 errors=0 orphans=4`, `EXIT=1`, the four `match=no` rows being
`v7-term-pid-fork`, `v8-hup-group-fork`, `m1-monitor-term-fork`, `m2-monitor-hup-fork`, each `survivors=1`; default
launch → `rows=16 mismatches=0 errors=0 orphans=0`. That is the report's before (including its bounded-baseline
reading of the default launch) reproduced by me, and it confirms the counter's red is the job-control launch, not a
tool defect at base.

Harm and repair: W2 replaced `local pid=${CLI_PID:-${!:-}}` with `local pid=${CLI_PID:-}`; R1 restores it. The R1
receipts (`census/round-82/records/repair-w3/`) bind `tool_sha256=dd6d440e…` and state the executed bytes equal the
tool at `c5c3f087`, which I confirmed. My two runs above are the tip bytes, i.e. the repaired file as pushed.

Evidence-verified only: `selftest: 57 checks, 0 failed`; r17 `SUMMARY total=37 failed=0 skipped=0`; probe D `arms=6
failed=0`; C2 controls K-b `mismatches=12 orphans=12` and K-c (p3). I did not execute the tool's own selftest: it is
the lane's gate, not mine to run (§Gate standard).

### SCORECARD and axes

`git diff 488956c4 44e07401 -- SCORECARD.md`: appends only (r82 done row replacing the planned row, the Round 82
measurements table, the post-wave addendum). `git diff --quiet 488956c4 44e07401 -- PROVINCE.md` is true — unchanged.
No axis score changed (coverage 8, calibration 7, operability 8 at both ends).

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1 re-measured: the frozen 32-row harness accepts 2 false rows (NF-F, NF-G) on the r81 counter and 0 on the r82 counter, `refused_true=0`, with the r81/r78/r77/r79/r80 regressions green (r81 re-run by me) |
| operability | improved | C2 re-measured at the tip bytes: base leaves 4 rows with orphans under `SHELLOPTS=monitor` (v7/v8/m1/m2), the filed tool leaves 0 under both launches; the W2 empty-`CLI_PID` window is closed by R1 and the repair is bound by digest to `c5c3f087` |
| coverage | unchanged | no coverage claim this round; `PROVINCE.md` unchanged; zero SOURCES rows added |

Re-measured by me: the C1 harness against the r82 counter, the r81 counter and the K-b variant; the r81 regression
harness; the C2 counter at the tip bytes under both launches and at the base bytes under both launches; the row/tier
counts, the sources census, all instrument digests, and every receipt SUMMARY/`match=` line. Evidence-verified only:
the tool's selftest, r17, probe D, the C2 K-b/K-c controls, the four C1 regression receipts other than r81, the
registry-agreement tool.

## 3. Discernment spot-check

`corpus/lessons/round-82.md` `## Gate` logs **one reject and no admit**: the only candidate considered is S330
(procps-ng pgrep(1)), rejected as a duplicate of S075's ground, and nothing was admitted because no row was opened
this round. That absence is itself the finding; I sampled the reject plus the nearest available admit (r81's S329).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S330 candidate — procps-ng pgrep(1), parent lookup (`cli_kill_tree`'s mechanism) | reject as a SOURCES row | `zcat /usr/share/man/man1/pgrep.1.gz` → `-P, --parent ppid`: "Only match processes whose parent process ID is listed."; `grep '^| S075 ' corpus/SOURCES.md` → proc_pid_stat(5), scope pgrp/session IDs and starttime | agree on the decision, disagree on the form | the only new proposition is the `-P` parent lookup, which the tool itself demonstrates by running, and S075 already governs the process-identity ground, so a second row adds no expansion (CORPUS rule 4). But the round prompt §2b.1 says "Rejections stay as rows with reason and flip"; `grep -c REJECTED corpus/SOURCES.md` = 22 (unchanged), highest id = S329, so S330 exists nowhere in the registry — the reject lives only in lesson prose. Routed |
| S329 admit (r81; the nearest admit — r82 has none) — GNU Bash 5.3 Lists of Commands | admit | `zcat /usr/share/info/bash.info.gz \| sed -n '755,762p'` → "When job control is not active, the standard input for asynchronous commands, in the absence of any explicit redirections, is redirected from ‘/dev/null’." at decompressed lines 757-760 | agree | the quote is verbatim, located, and 17 words (≤25); the row's scope names the job-control precondition and the citation grounds r81 C2's `<&0`. Load-bearing for r81, not for this round's claims |
| newly written `corpus/SOURCES.md` row | none written (252 → 252) | `grep -cE '^\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md` = 252; `git diff 488956c4 44e07401 -- corpus/SOURCES.md` empty | n/a — defect recorded | the frontier step wrote no row and left its one rejected candidate unrowed; nearest newest row S329 checked instead (same as above) |

Sources census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 87 `W04` cross-scope duplicate-URL lines
(pre-existing), `EXIT=0`. Row count `252` at base and at tip, equal to the report.

## 4. Trend verdicts

- **expansion: unchanged** — no row added (252 → 252), no new `corpus/knowledge/` entry (the corpus diff is
  `QUALITY.md` +4, `knowledge/gate-signal-handling.md` +30 inside an existing entry, and the round lesson), no
  capability row entered. The round deepens two existing instruments; the one candidate was a deliberate
  non-expansion. I agree with the lane's verdict.
- **quality: improved** — Q150 supersedes Q148's order clause and Q149's row clause and Q151 adds the real-shape
  criterion; the `gate-signal-handling.md` r82 section replaces the `$!`-drop decision with the measured window, the
  repair and four new limits; six frozen sentences were amended to the property the counters enforce with the
  falsifying artifact cited (`plans/round-82.md` A1–A9). The harm this round introduced is closed on the filed bytes
  (my re-measurement above). I agree.
- **discernment: improved** — the wave falsified six sentences of the round's own wording and all six were narrowed
  before filing rather than defended; a seat's MEDIUM that would have retracted a landed control was re-derived and
  rejected on the bytes (lesson M6, A4); the dead seat is reported dead; the S330 reject was adjudicated by a second
  seat and I agree with the substance. Form defects (no admit in this round's Gate; the reject unrowed) are routed and
  do not overturn the decisions. I agree.

## 5. Routed defects (lane fixes next round)

1. **Registry form — the rejected candidate never became a row.** Open `S330` as a `rejected` row with the reason and
   flip already written in the lesson `## Gate`, or get an operator ruling that refusals may stay in prose (§2b.1
   says they stay as rows).
2. **LOG.md append-only correction.** The Round 82 entry's first C2 bullet says the tool "drops the stale `$!`" while
   R1 restored `${CLI_PID:-${!:-}}`; append a correction entry (or an explicit supersession in the bullet) naming that
   sentence, since the filed bytes do not drop the fallback.
3. **Report bookkeeping.** `51a5e7fa` (freeze receipt + lesson M1/M2) is in the lane history but missing from the
   report's commit chain and the Landed changes table; make the chain complete or name the omission.
4. **Wave shape.** Prompt §3's planner seat is absent and the "validator forbids it" justification does not resolve in
   `scripts/hyaku/ufo-wave-policy.json` (which defines a `planner` role). Document the real rule or seat one.
5. **C1 own-tree real shape** (the lane's own route 1, Q151): extend `CAPTURE` to the lane's real `wN/` directories and
   row a kept real move beside a refused `decoy/` sibling.
6. **C1 identity clause** (route 2): a flattened/short-suffix own-tree decoy so the population can separate the identity
   disjunct from a suffix-only rule.
7. **C1 census-in-tree branch** (route 3): ground it with a real token-under-`census` row or delete it.
8. **C2 tree walk** (route 4): one fork-free `/proc` ppid-map pass with kill-as-discovered, closing F-2 (per-node
   `pgrep -P` cost) and F-3 (snapshot→KILL reuse window) together.
9. **C2 counter** (route 5): the dead `rid.startswith("m-")` test at `census/round-82/c2-vault-signal-counter.py:217`
   should become a row property or be deleted; settle under `strace`; guard `pgrep`.
10. **C2 rows** (route 6): `termign-fork` (tree KILL × forked CLI) and the reproduced `p5-late-term` row.
11. **Carried, unchanged** (r81 spot-check §5 item 6): `_regular` pathspec framing, quarantine intro-blob digest row,
    fork-tail row, r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, status-trusting lane tools, r17 240 s
    runners.

SHONEN: all four boxes are `[~]` with resolvable pointers (SKILL gate registry rows for both r82 instruments at
`SKILL.md:952-955`, LOG `## Round 82`, `census/round-82/preregistration.txt` + `plans/round-82.md`, PROVINCE
unchanged). Box 2's pointer is the r82 instrument receipts, not a new end-to-end domain task — the historical sweep
remains `LOG.md:362` — so I do not upgrade the mark. They look checkable by a non-author; promotion is
operator-owned.
