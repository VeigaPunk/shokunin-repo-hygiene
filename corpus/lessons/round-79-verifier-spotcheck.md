author: hyaku closure (non-author integrator, @m_zfl)

# souji round 79 — verifier spot-check (non-author closure)

Round: souji lane-round 79. Lane base `e65538e73c7f1a8f7570bc24a2215da8a90043f3`, after
`35b208cc72b014fa5af68101c0561e7974f1fe76` (branch `master`). Report `.ufo/reports/round-79/souji.md`
(fleet repo). Driver digest (copied from `.ufo/watchdog.log`):
`2026-11-07T01:51:21-03:00 launch souji round=79 pgid=304313 driver=hyaku-inline attempt=1`;
`2026-11-07T03:57:09-03:00 complete souji round=79; hyaku-inline attempt=1`.
Written 2026-11-07. This file is the only artifact the closure writes in the lane.

Outcome: status `ok`, **not admitted** (`rejected-honest-stop`). C2 verifies (re-measured); C1 fails
its own frozen kill rule at the after-arm A, as the lane itself reports. No owned axis is harmed.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report filed by lane identity | `git log --format='%an %H %cI' -- .ufo/reports/round-79/souji.md` (fleet) | `souji-shokunin 605b7d18… 03:56:41`, `souji-shokunin 58d1e179… 03:56:32` (second commit only removes one line) | pass; both before `complete` 03:57:09 |
| SHONEN heading, one line per box | read report `## SHONEN` | 4 lines, all `[~]`, each with an evidence pointer | pass |
| cited lane commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> master` over the 14 hashes in the report (base, P, F, W1, W2, A, R1, R2, D, I, domain-trial script, I2, census-after, tip) | `ok` ×14 | pass |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git status --porcelain` | `state branch=master local=35b208cc… remote=35b208cc… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty | pass |
| dispatched prompt carries the template contract | `grep -nE '^## ' .ufo/prompts/souji-round-79.md` | sections 1–5 of `templates/round-prompt.md` + `## 6. Campaign addendum — hyaku` + §7; committed `c208a092` 01:51:16 (before launch) | pass |
| preregistered digests | `sha256sum census/round-79/{c1-signal-counter.py,c1-population.tsv,c2-false-row-harness.py,c2-false-rows.tsv}` | `0d0ec67c…`, `8a34f772…`, `5d5bd236…`, `7c108820…` — equal to the prereg lines | pass |
| chronology P < F < W1/W2 | `git log --format='%h %cI' e65538e7..35b208cc` | P 02:16:09, F 02:16:20, W2 02:16:34, W1 02:16:34 (prereg names drafts in scratch with digests in `records/prefreeze-feasibility.txt`) | pass; freeze-check receipt `SUMMARY claims=2 findings=0` |
| domain-trial grades the filed report | `git show 605b7d18:.ufo/reports/round-79/souji.md \| grep -v '^Final lane hash:' \| sha256sum` | `1ae2b6d6…6ffd`, equal to `report_sha256` in `census/round-79/records/c1-domain-trial.txt` (r78 routed defect 4 closed) | pass |
| gate bytes at tip = W1 | `git show <c>:tools/souji-pre-report-gate.sh \| sha256sum` | base `5f5cb865…`, W1 `ae5022c5…`, R1 `56376fd2…`, R2 `ae5022c5…`, tip `ae5022c5…` | pass (R1 reverted byte-exactly) |

Conformance defects (status-neutral): the A receipt's `command=` line does not record that the counter was
launched with `&`, the condition that decides row s4 (self-disclosed, S79CriticClaims MEDIUM-2); R1 was
committed as a repair before its cause was probed and reverted (self-recorded M2); a wave seat overwrote a
tracked knowledge file before integration (self-recorded M5, restored before landing).

## 2. Claims re-check

### C1 — operability (sourced, S325/S326): evidence-verified, **not verified on its frozen predicate**

The C1 counter executes the lane's pre-report gate, so it was not run here (§Gate standard, Closure
consequence); its committed receipts were re-counted at `35b208cc`:

```
for f in controls/c1-K-a-do-nothing.txt controls/c1-K-b-trap-only.txt controls/c1-K-c-no-kill.txt \
         records/c1-after.txt records/foreground/c1-at-W1-fg-run{1,2,3}.txt records/repair/c1-at-R1-run1.txt; do
  git show 35b208cc:census/round-79/$f | grep -c '^ROW.*match=no'; done
```

| receipt | ROW match=no | rows with survivors>0 | SUMMARY / EXIT |
|---|---|---|---|
| K-a do-nothing (base) | 10 | 10 | `rows=11 mismatches=10 errors=0 orphans=10` EXIT=1 |
| K-b trap-only | 10 | 10 | mismatches=10 orphans=10 EXIT=1 (red, as preregistered) |
| K-c no-kill | 10 | 10 | mismatches=10 orphans=10 EXIT=1 (red) |
| **A** `records/c1-after.txt` (W1) | **1** (s4 INT: `exited=n … survivors=3 tmpleft=2 secs=5.0`) | 1 | `rows=11 mismatches=1 errors=0 orphans=1` **EXIT=1** |
| R1 run1 (reverted) | 1 | 1 | mismatches=1 EXIT=1 |
| foreground run1/2/3 (W1, post-measurement) | 0/0/0 | 0/0/0 | `mismatches=0 orphans=0` EXIT=0 ×3 |

Regression conjuncts (re-counted): r78 `rows=17 mismatches=0 hangs=0`, r77 `rows=16 mismatches=0`, r76
`rows=30 mismatches=0`, r36 `cases=21 pass=21 fail=0`, r27 EXIT=0 — all green. Domain trial: ARM1 PASS on
gitsource/tip/clean with no check-signal line; ARM2 real SIGTERM `rc=143 survivors=0`, `amendment=none`.

The prereg Kill line reads "any mismatch, error or orphan on the 11 rows"; A has one of each kind that
counts. The Stated limits name SIGKILL and short `$(...)` forks, not a signal ignored on entry. **The kill
rule fires: C1 does not verify.** The foreground runs are a re-run under a launch the prereg did not name;
they are diagnosis, not the claim.

Diagnosis independently confirmed (plain bash, not the lane's gate or probe): a script that starts
`bash -c 'trap -p INT; trap "echo caught" INT; trap -p INT; grep SigIgn /proc/self/status' &` prints
`trap -- '' SIGINT` twice and `SigIgn: 0000000001000006` (SIGINT bit set; the trap is refused); the same
command in the foreground prints `trap -- 'echo caught' SIGINT`, `SigIgn: 0000000001000000`
(bash 5.3.20). This agrees with S325's second anchor (decompressed `bash.info` lines 3942-3943, re-read
below) and supports the lane's reading that s4 is an instrument launch artefact. That is why operability is
graded `unprovable-but-better` below rather than `unchanged`; it does not turn a fired kill rule into a pass.

### C2 — calibration: **re-measured, verified**

Run by the closure from the lane checkout (the harness is a counter over committed bytes, not a registered
gate; its fixture lives in the work dir; `git status --porcelain` stayed empty afterwards):

```
python3 -B census/round-79/c2-false-row-harness.py --counter census/round-79/c2-pointer-counter.py \
  --lane $PWD --fleet-root /home/vgpnk/Projects/shokunin --work /fast/scratch/hyaku/closure-souji-r79/<d>
```

| counter | observed | reported |
|---|---|---|
| `census/round-79/c2-pointer-counter.py` (after) | `SUMMARY rows=9 mismatches=0 accepted=0 errors=0`, EXIT=0; NF1–NF5 `got=REFUSED` | same (`records/c2-after.txt`) |
| `census/round-78/c2-pointer-counter.py` (K-a, before) | `SUMMARY rows=9 mismatches=5 accepted=5 errors=0`, EXIT=1; NF1/NF2/NF5 `got=TOKEN`, NF3 `got=MOVED`, NF4 `got=QUARANTINED` | same (`controls/c2-K-a-r78-counter.txt`) |

Controls and regressions evidence-verified by re-counting receipts: K-b refuse-all 9/9 on the harness but
`items=22 resolved=3` EXIT=1 on the r78 regression (red, as preregistered); ablations range 2, nextline 1,
moved 1, quarantine 1 accepted, all EXIT=1; regressions r78 `items=22 resolved=22` EXIT=0, r77 `items=35
resolved=35` EXIT=0. Every C2 kill condition is clear. Qualification carried from the lane's wave: NF6a/NF6b/
NF8/NF10 still accepted and 8 of 13 rule mutants survive the frozen population (routed).

### Owned axes

`git diff e65538e7 35b208cc -- SCORECARD.md`: adds the r79 "done" line, r80 planned line, the Round 79
measurements table, and two capability rows marked "closure-gated"; no score cell changed ("No owned axis
score changed (calibration 7, coverage 8, operability 8)").

| axis | verdict | reason |
|---|---|---|
| operability | unprovable-but-better | frozen predicate red at A (1 mismatch, 1 orphan); 10 → 1 under the frozen counter even at A, 10 → 0 in the foreground, regressions all green, gate bytes at tip = W1; the residual row is reproduced as a launch artefact by plain bash above |
| calibration | improved | C2 re-measured 5 → 0 accepted false rows, controls red, regressions green |
| coverage | unchanged | two tier-A rows added; no coverage claim, score unchanged |

## 3. Discernment spot-check

Source: `corpus/lessons/round-79.md` `## Gate`. Census:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ `souji ok …/corpus/SOURCES.md`, EXIT=0; 87 W04 lines, equal to the lane's census-before and census-after
receipts (87 each). Rows `grep -cE '^ {0,3}\| *S[0-9]{3,}' corpus/SOURCES.md`: 247 at base → 249 at tip.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S325 GNU Bash 5.3 manual, node Signals (installed) | admit (A, mined) | `pacman -Qo /usr/share/info/bash.info.gz` → bash 5.3.20-1; `sha256sum` → `cde1a336…588f` (matches row); `zcat … \| sed -n '3262p;3281,3283p;3942,3943p'` | agree | lines 3281-3283 carry "it will not execute the trap until the command completes. If Bash is waiting for an asynchronous command via the 'wait' builtin"; 3262 "When job control is not in effect, asynchronous commands ignore 'SIGINT'"; 3942-3943 the second anchor; scope matches what C1 and M2 use |
| S326 coreutils `src/timeout.c` at v9.12 | admit (A, mined) | `curl https://raw.githubusercontent.com/coreutils/coreutils/v9.12/src/timeout.c` → HTTP 200, 21183 bytes, sha256 `bf1f0d99…2cc9` (matches row); `sed -n 567,572p` | agree | line 567 "Ensure we're in our own group so all subprocesses can be killed." (12 words, ≤25) then `if (!foreground) setpgid (0, 0);` — exactly the cited quote; the tag matches the host's coreutils 9.12 |
| gnu.org bash Signals page and coreutils timeout-invocation page | reject (unreachable) | `curl -m 40 https://www.gnu.org/software/bash/manual/html_node/Signals.html` → exit 28, http 000; `curl -m 30 …/coreutils/manual/html_node/timeout-invocation.html` → exit 28 | agree | still unreachable from this host; nothing was opened, so nothing to admit; the installed info file carries the same node |
| bminor/bash `doc/bashref.texi` mirror path | reject (404) | `curl https://raw.githubusercontent.com/bminor/bash/master/doc/bashref.texi` → HTTP 404, 14 bytes | agree | a guessed path, not a source |

SOURCES row re-open: S326 (newly written, `corpus/SOURCES.md` line 285): quote "Ensure we're in our own
group so all subprocesses can be killed." is 12 words and present verbatim at line 567 of the re-fetched
file. Spot-check result: 2 admits, 2 rejects re-opened, 4/4 agree.

## 4. Trend verdicts

- **expansion: improved** — S325/S326 (tier A, mined) on ground the lane did not hold, both re-opened with
  matching digests; new `corpus/knowledge/gate-signal-handling.md`, QUALITY Q142/Q143; census ok, 247 → 249 rows.
- **quality: unprovable-but-better** — C2's instrument now refuses five false rows it accepted (re-measured);
  C1's gate change is real (regressions green, foreground 0 orphans, domain-trial SIGTERM arm 0 survivors)
  but its frozen measurement is red, and a misdiagnosed repair was committed and reverted. No single count
  carries the net.
- **discernment: improved** — the lane reported its own kill rule as fired rather than re-running until
  green, reverted R1 byte-exactly, and recorded M1–M6; its source decisions agree 4/4 under re-open, and its
  launch-artefact diagnosis reproduces in plain bash.

## 5. Routed defects (lane fixes next round)

1. Every counter receipt records its launch disposition (foreground/background; inherited `SigIgn`) on a
   column-0 line, and the C1 counter successor resets inherited signal dispositions for the gate it starts or
   refuses to run when SIGINT is ignored on entry (lesson M2/M3; route (a)).
2. Re-measure C1 under a freshly frozen successor counter before any operability score or "signal-safe gate
   children" capability row is counted; until then the SCORECARD capability row stays closure-gated and
   unearned (this closure does not admit it).
3. State in the prereg Stated limits any launch condition the instrument depends on; a limit discovered after
   A is a disclosure, never an amendment.
4. Diagnose before repairing: no repair commit without a probe that can fail on the hypothesised cause (M2, R1).
5. Wave seats write only under their seat directory; the integrator checks `git status` before integration
   (M5) — keep the guard that caught it.
6. C2 survivors: NF6b, NF8, NF10 and detectors DM01/DM07/DM11 (S79MutCounter), plus the prose-declaration
   limit NF6a (route (d)).
7. Carried: check-4 300 s backstop row; r76 K03/K04; status-trusting lane tools (route (b)/(c)).
