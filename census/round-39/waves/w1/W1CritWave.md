# W1CritWave — wave-shape critique (souji r39 wave 1)

Seat: W1CritWave (critic, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Judged axis: calibration. Scope: the **shape** of `w1-spec.json` / `w1-dispatch.json` against the
binding addendum (`/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md`, run-11 lines) —
seat count and band, role mix and attack share, planner mask, connector count, one batched wave,
prompt distinctness, absolute paths, and whether any item asks a seat to author a lane file the L1
must integrate. No lane bytes were written; this seat ran read-only git and two non-mutating
counter invocations. Scratch `/fast/scratch/hyaku/souji-r39/W1CritWave` was removed on exit (§9).

## 0. Revision pins measured

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3
2201778 round-39: PROVINCE boundary note — two tool contracts repaired, no receipt class, certification OFF
790d16b round-39: C2 — drop unreachable EISDIR from the RECORD-MISSING line (wave-1 W1ExecC2Docstring)
094e531 round-39: C1 — R7 line names the reaped path as $HYAKU_SCRATCH, not a literal scratch root
```

Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
base `ed30b7f5b77939c9073348d810730bc4f355708d`). Rules read: `lane-addendum.md` §6 run-11 block
(64–128 band, 256 ceiling, ≥25 % attack share, few connector seats, one batched wave, planner mask),
`scripts/hyaku/ufo-wave-policy-v2.json` (`waveMinLanes: 64`, `waveMaxLanes: 128`).

## 1. Seat count and band — PASS

```
$ python3 -c "import json,collections; d=json.load(open('.ufo/waves/round-39/w1-spec.json')); ..."
seats=71 role_mix={'connector': 4, 'critic': 8, 'executor': 19, 'mutation-tester': 5, 'revenger': 2,
 'reviewer': 10, 'scout': 8, 'scribe': 10, 'sentinel': 1, 'simplifier': 4}
in_band= True
$ python3 -c "... print('spec items',len(s['items']),'dispatch tasks',len(d['taskCall']['tasks']),
              'registry members',len(d['registry']['members']),'counts',d['counts'])"
spec items 71 dispatch tasks 71 registry members 71 counts {'spawn': 71, 'resume': 0, 'total': 71}
```

71 ∈ [64, 128]; policy `source: config`, `waveMinLanes 64`, `waveMaxLanes 128`, `hardCeiling 256`.
**Verdict: PASS** — one v2 wave inside the band, not padded to the ceiling and not below the floor.

## 2. Attack share — PASS

Attack roles counted as the assignment defines them (reviewer + critic + mutation-tester + sentinel +
revenger) and, separately, as §2 of the addendum defines them (reviewer, critic, mutation-tester,
labrat). The wave carries no labrat, so both counts are identical:

```
attack=26 / 71 = 36.62 %          (threshold ≥ 25 %)
attack= 26 share=36.62%
```

Build/draft roles: executor 19, scribe 10, scout 8, simplifier 4, connector 4. The 26 attack seats
carry 8 critics, 10 reviewers, 5 mutation-testers, 2 revengers, 1 sentinel. Every one of the 26 opens
its `# Task` with a falsification verb, not with build work:

```
$ python3 - <<'EOF'  # first Task line of each attack-role item
reviewer | W1RevC1Forge | Attack C1's instrument by trying to forge a pass. …
reviewer | W1RevC1Register | Attack the C1 register leg. …
reviewer | W1RevC2Legs | Attack C2's six legs. …
reviewer | W1RevC2Doc | Attack C2 L4 (the docstring → behaviour mapping). …
reviewer | W1RevC2Harm | Attack C2 L6 (harm). …
reviewer | W1RevC3Battery | Attack C3's battery. …
reviewer | W1RevC3Fixture | Attack the new fixture's case independence. …
reviewer | W1RevSeparability | Test claim separability. …
reviewer | W1RevFreeze | Compare the frozen prereg against the instruments. …
reviewer | W1RevScope | Audit write scope for the round so far. …
critic | W1CritC1Axis | Criticize C1's axis attribution. …
critic | W1CritC3Axis | Criticize C3's axis and magnitude. …
critic | W1CritSizing | Criticize claim sizing against addendum section 9. …
critic | W1CritDisclosure | Criticize what the claims should disclose. …
critic | W1CritSources | Criticize the sources plan for section 2b. …
critic | W1CritReport | Criticize the report plan. …
critic | W1CritWave | Criticize the wave shape. …
critic | W1CritAssimilation | Criticize the assimilation decision for this round. …
mutation-tester | W1MutC1 | Mutate `census/round-39/c1-counter.py` and score the control. …
mutation-tester | W1MutC2 | Mutate `census/round-39/c2-counter.py` and score its legs. …
mutation-tester | W1MutC3 | Mutate the C3 battery's kill rule and score it. …
mutation-tester | W1MutFixture | Mutate the new fixture to prove the battery depends on its cases. …
mutation-tester | W1MutDriftRules | Hunt for record-parser behaviours the round's four mutants miss. …
sentinel | W1SentInstruments | Security review of the new instruments. …
revenger | W1RevHistory | Reverse-engineer why the r38 spot-check's defect classes recur across rounds. …
revenger | W1RevExitContract | Reverse-engineer the citation tool's intended exit contract from its own artefacts: …
```

**Verdict: PASS** — 36.62 % ≥ 25 %, with 8.6 points of headroom, and all 26 attack seats carry a
falsification task rather than an attack-role label over build work.

## 3. Planner mask — PASS

```
$ python3 -c "... print('planner_present=', 'planner' in roles)"
planner_present= False
$ python3 -c "... print('agent values:',collections.Counter(t['agent'] for t in tasks))"
agent values: Counter({'executor': 19, 'reviewer': 10, 'scribe': 10, 'critic': 8, 'scout': 8,
 'mutation-tester': 5, 'connector': 4, 'simplifier': 4, 'revenger': 2, 'sentinel': 1})
role->agent mismatch: []
$ grep -n "planner" /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs | head -10
263: * Swarm lanes are the ten proposal roles. planner/distiller/labrat/Main are frozen-topology seats
$ wc -c .ufo/waves/round-39/w1-validation.err .ufo/waves/round-39/w1-gen.err
0 .ufo/waves/round-39/w1-validation.err
0 .ufo/waves/round-39/w1-gen.err
```

No item carries role `planner`; every item's `agent` equals its role (role-routed, no model string is
passed anywhere in the payload); the validator emitted zero bytes on stderr. The L1 keeps the
canonical planner seat; the bounded planning walk rides scout/connector items (`W1ConnOverlap`,
`W1ConnCoverage`, `W1ConnDuplicates`, `W1ConnSources`), which is the allowed mapping.
**Verdict: PASS.**

## 4. Connector seats — PASS ("few")

```
connector=4 share=5.63%
```

4 of 71 = 5.63 %, all four read-only cross-surface scans that write only their own report file.
**Verdict: PASS** — a few connector seats, none of them a writer.

## 5. One batched wave — PASS

```
$ ls .ufo/waves/round-39/ | cat
gen-w1-spec.py  w1  w1-dispatch.json  w1-gen.err  w1-spec.json  w1-validation.err  w1.ready  w1.ready.partial
$ cat .ufo/waves/round-39/w1.ready
{"lane":"souji","round":39,"wave":"w1","dispatch":"/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1-dispatch.json","l1":"SoujiR39"}
$ python3 -c "... print('wave keys:', ...)" ; print('n_items:', len(items))
wave keys: souji-r39-w1
n_items: 71
```

Exactly one wave id (`souji-r39-w1`), one spec, one dispatch, one `taskCall` carrying all 71 tasks
(`counts.spawn=71 resume=0`), one `.ready` never rewritten. The co-resident `w1.ready.partial` is
**driver-owned**, not an L1 re-write of the ready file:

```
$ grep -n "ready.partial\|partial" /home/vgpnk/Projects/shokunin/scripts/hyaku/inline-dispatcher.py | head -20
124:def _save_partial(ready, spawned):
128:    os.replace(tmp, ready + '.partial')
273:        os.remove(ready + '.partial')
$ python3 -c "... p=json.load(open('.ufo/waves/round-39/w1.ready.partial')); ..."
entries: 44
keys not in spec: 0 []
value duplication: []
```

44 of 71 items are filled so far, every key is a spec item, no seat name is mapped twice, and the
values (`W1ExecC2Repro-5`, `W1ExecC3Fixture-3`) are the harness's collision suffixes on agent names,
not duplicate spawns of one item. **Verdict: PASS** — one batched wave, mid-fill, no duplicate writer
recorded.

## 6. Distinct prompts — PASS

```
dup prompts: 0
dup names: 0
pairs jaccard>0.6: 0 []
missing trailer: 0
trailer path dups: []
trailer != expected: []
```

No two items share a prompt, no two share a task body above 0.6 Jaccard on 4+ character tokens, and
each of the 71 items renders a unique `Report: .ufo/waves/round-39/w1/<ItemName>.md` trailer.
**Verdict: PASS** — no padding by duplication, and no two seats can collide on one report path.

## 7. No item asks a seat to author a lane file the L1 must integrate — PASS

```
$ python3 -c "... scan task bodies for write verbs co-occurring with production paths ..."
### W1ExecConsumers
    `tests/fixtures/r36-worktree-drift.py`, `tests/fixtures/r38-drift-write-envelope.py`,
### W1ScribeGate
    170 -> 170+k). Do not write into `corpus/SOURCES.md`; the L1 appends.
$ python3 -c "... scan task bodies for 'git commit|git add|git push|jj <verb>' ..."
(no output)
```

The only write-verb hit is the *negative* instruction in `W1ScribeGate` ("the L1 appends"), and the
only other hit is a fixture list being read. Every builder item exercises bytes already in the lane
(`W1ExecC3Fixture` runs the fixture, `W1ExecC2Docstring` derives the docstring map, `W1ExecConsumers`
runs six consumer fixtures); scribes draft text into their own report and the L1 lands it. No item
names a mutating git or jj command. The shared context states the bound explicitly ("You are
advisory: the L1 integrates").
**Verdict: PASS** — the wave is advisory throughout; the L1 is the only writer.

## 8. Every item names absolute paths — PASS on prose, **FAIL on three runnable lines**

All 71 items name the lane root absolutely at least once:

```
items with lane abs path: 71 / 71
```

The failure is narrower and mechanical: three items hand a seat a **verbatim command** whose script
or fixture path is CWD-relative while the seat's cwd is the fleet root. Measured, not inferred:

```
$ cd /home/vgpnk/Projects/shokunin && python3 -B census/round-39/c1-counter.py --root . \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv \
    --register census/round-39/cells.tsv
python3: can't open file '/home/vgpnk/Projects/shokunin/census/round-39/c1-counter.py': [Errno 2] No such file or directory
FLEET_ROOT_RC=2

$ cd /home/vgpnk/Projects/shokunin && python3 -B tests/fixtures/r39-drift-record-rules.py \
    --tool tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r39/W1CritWave
python3: can't open file '/home/vgpnk/Projects/shokunin/tests/fixtures/r39-drift-record-rules.py': [Errno 2] No such file or directory
RC=2

$ cd /home/vgpnk/Projects/shokunin && python3 -B .../census/round-39/c1-counter.py --root . --rev ed30b7f... \
    --items .../c1-items.tsv --register .../cells.tsv
REFUSAL COULD-NOT-EVALUATE: --rev ed30b7f5b77939c9073348d810730bc4f355708d does not resolve to a commit
```

Same bytes, run from the lane root, are correct:

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c1-counter.py --root . \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv \
    --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1CritWave
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

The relative form is worse than a clean refusal for the C3 counter, because `--fixture` is opened
CWD-relative (`census/round-39/c3-counter.py:123  candidate_src = open(args.fixture, ...)`) and is
not guarded, so an absolute `--root` plus the item's relative `--fixture` raises an **uncaught
traceback** — the exact shape the r38 A5 kill contract treats as a broken battery, not as a kill:

```
$ cd /home/vgpnk/Projects/shokunin && python3 -B .../census/round-39/c3-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev ed30b7f... --base-rev ed30b7f... \
    --fixture tests/fixtures/r38-drift-record.py --scratch /fast/scratch/hyaku/souji-r39/W1CritWave
    candidate_src = open(args.fixture, encoding="utf-8").read()
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/r38-drift-record.py'
RC=1
```

**Impact measured, and it is contained this wave:** all three affected seats repaired the paths
themselves before running —

```
$ grep -n "cd /home\|--root" .ufo/waves/round-39/w1/W1ExecC1Base.md | head -3
73:$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
75:$ TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecC1Base python3 -B census/round-39/c1-counter.py \
76:    --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d \
$ grep -n "cd /home\|--root" .ufo/waves/round-39/w1/W1ExecC3Baseline.md | head -2
17:python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
$ grep -n "cd /home\|--root" .ufo/waves/round-39/w1/W1ExecC3Fixture.md | head -2
23:cd /home/vgpnk/Projects/shokunin/souji-shokunin
```

so no false finding was scored in this wave. The defect is nevertheless live in the frozen spec and
re-fires on every weaker seat.

**Verdict: FAIL (calibration), 3 items named** — `W1ExecC1Base`, `W1ExecC3Baseline`,
`W1ExecC3Fixture` (and, same class but repaired by a `cd`, `W1ExecC2Docstring`'s
`git show <rev>:tools/souji-worktree-drift.py` line, which lacks `-C <lane>`).

**Smallest safe correction** (no predicate, receipt or counter score changes):
1. In the spec text, prefix the three command lines with the absolute lane path —
   `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py --root
   /home/vgpnk/Projects/shokunin/souji-shokunin ...` and the same for `c3-counter.py` and the
   fixture run; add `-C /home/vgpnk/Projects/shokunin/souji-shokunin` to the `git show` line.
2. In `census/round-39/c3-counter.py`, resolve `--fixture`/`--base-fixture`/`--tool` against
   `--root` (or refuse with `REFUSAL COULD-NOT-EVALUATE: fixture absent` + exit 2) instead of
   letting `open()` raise, so the documented exit-2 contract holds for its own inputs.

## 9. Adjacent findings (named, not scored by this seat)

1. **Register arm has no builder seat.** C1's frozen predicate needs
   `register_cells>=6` and `commit_distinct>=2`, and its counter takes
   `--register census/round-39/cells.tsv` — a path that is **absent and untracked**:

   ```
   $ ls -la census/round-39/cells.tsv
   ls: cannot access 'census/round-39/cells.tsv': No such file or directory
   $ git ls-files census/round-39/ | cat
   census/round-39/c1-counter.py
   census/round-39/c1-items.tsv
   census/round-39/c2-counter.py
   census/round-39/c3-counter.py
   census/round-39/preregistration.txt
   census/round-39/records/c1-before.txt
   census/round-39/records/c2-before.txt
   census/round-39/records/c3-before.txt
   ```

   The control receipt shows the counter tolerating this (`register_cells=0`), so the base arm
   reproduces — but the *landing* arm cannot reach `register_cells>=6` until the L1 lands the file.
   The generator for it is untracked too (`census/round-39/make-cells.py`, not in `git ls-files`),
   and its own docstring says the six anchored lines must be copied by the L1 into
   `SCORECARD.md`, `LOG.md` and `corpus/QUALITY.md`. No item names `cells.tsv`, `REG-01..REG-06` or
   `cells-lines.md` as work: `grep` over the 71 tasks returns only `W1ExecC1Base` (as an input path)
   and `W1ConnDuplicates` (as a search surface). Consequence: the arm the round exists to close —
   the r38 limit "all ten rows carry `commit == receipt_rev`" — has attack coverage
   (`W1RevC1Register`, `W1MutC1`) but no build/verify seat, and only a critic would notice it
   missing. Correction: one line in the C1 context saying the L1 lands `cells.tsv` plus the six
   anchored lines at the landing revision, or one executor item that runs
   `make-cells.py --write` in scratch and prints the counter's `REGISTER` line.
2. **Stale seat count in the generator.** `gen-w1-spec.py:2` says 72 seats; the spec emits 71:

   ```
   $ grep -n "72\b" .ufo/waves/round-39/gen-w1-spec.py | head
   2:"""Generate the r39 wave-1 spec: one v2 wave (72 seats) carrying build and attack items.
   spec items 71 dispatch tasks 71 registry members 71 counts {'spawn': 71, 'resume': 0, 'total': 71}
   ```

   This is the R13 class the round itself polices (a lane byte stating a value the repo contradicts).
   Correction: `72` → `71` (or drop the parenthetical).
3. **Axis label outside the axis table.** 4 items carry axis `adjacency`
   (`W1RevScope`, `W1ScoutOverlap`, `W1ConnOverlap`, `W1SentInstruments`) while `SCORECARD.md`'s
   `## Axes` table scores exactly three (`coverage 8`, `calibration 7`, `operability 8`);
   `adjacency` exists in this lane only as a trend-row label (`corpus/lessons/round-38-verifier-spotcheck.md:106
   | adjacency | unchanged |`). Not a violation — the label is the lane's own vocabulary — but an item
   tagged with an unscored axis can never move a score, so no report line should read those four
   items as an axis move.
4. **`/var/tmp` hardcoded in the C3 instrument.** `census/round-39/c3-counter.py:81` calls
   `child_env("/var/tmp")` in `resolves()`, which overrides `TMPDIR` and ignores `--scratch`
   (addendum §7.4 class: a counter that writes to a reaper-swept root regardless of `--work`).
   `c1-counter.py:203`, `c2-counter.py:172` and `c3-counter.py:120` fall back to `/var/tmp` only
   when neither `--scratch` nor `TMPDIR` is set, which is the acceptable shape. In remit of
   `W1ExecScratch`; named here because it is inside the instrument C1/C3 predicates are scored with.
5. **The 72 files this wave produces are gitignored; the L1 must name them individually to land
   them.** `.gitignore:1` is `.ufo/waves/`, and neither the previous round's nor this one's wave
   evidence is tracked:

   ```
   $ head -5 .gitignore
   .ufo/waves/
   census/operator-sweep-*/
   __pycache__/
   $ git check-ignore -v .ufo/waves/round-39/w1/W1CritWave.md
   .gitignore:1:.ufo/waves/	.ufo/waves/round-39/w1/W1CritWave.md
   $ git ls-files .ufo/waves/round-38 | wc -l
   0
   $ git ls-files .ufo/waves/round-39 | wc -l
   0
   $ git ls-files .ufo/waves | wc -l
   3026
   ```

   3026 older wave files are tracked (added before the ignore rule); r38 and r39 have none. The
   lane helper can still land them, but only when each path is named as a **file**:

   ```
   $ sed -n '654,666p' /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh
     # Record tracking for named paths. --include-ignored (which also admits files
     # over snapshot.max-new-file-size) applies only to named FILES; a named
     # directory is tracked like `git add <dir>`, so ignored content stays out.
     ...
     "$JJ_BIN" --config "$AUTOTRACK_OFF" file track --include-ignored -- "${fs_files[@]}"
   ```

   [INFERENCE from that source, not from a run — this seat may not run the helper] naming the
   directory `.ufo/waves/round-39` tracks nothing, `jj diff --summary -- root:"…"` is then empty and
   the helper prints `nothing to commit`; naming `…/w1-spec.json`, `…/w1-dispatch.json`,
   `…/w1/swarm-registry.json` and the 71 seat reports as files lands them. Consequence for this
   wave: the L1's wave-evidence commit is the one step where the round's own R4 routed defect
   ("untracked wave evidence") recurs, and r38's zero tracked files show it did recur last round.
   Correction: name the files, and add one line to the round report stating the tracked count
   (`git ls-tree -r --name-only <landing> -- .ufo/waves/round-39 | wc -l`) so the claim is measured
   rather than asserted.

## Verdict table

| check | rule source | measured | verdict |
|---|---|---|---|
| seat count in 64–128 band | addendum run-11, policy v2 | 71 | PASS |
| attack share ≥ 25 % | addendum run-11 | 26/71 = 36.62 % | PASS |
| planner mask (no `planner` seat) | orchestrator ruling 2026-10-19 | 0 planner; L1 holds it; validator stderr empty | PASS |
| few connector seats | addendum run-11 | 4/71 = 5.63 % | PASS |
| one batched wave | addendum §2 | 1 spec, 1 dispatch, 1 `taskCall`/71 tasks, 1 `.ready` | PASS |
| distinct prompts | addendum §2 | 0 exact dups, 0 pairs > 0.6 Jaccard, 71 unique trailers | PASS |
| no seat authors a lane file the L1 integrates | addendum §3/§4 | 0 write-to-production items; `W1ScribeGate` defers to the L1; 0 mutating-git verbs | PASS |
| every item names absolute paths | addendum §2 seat-path rule | 71/71 name the lane root; **3 runnable lines fail from cwd** | **FAIL** — `W1ExecC1Base`, `W1ExecC3Baseline`, `W1ExecC3Fixture` |
| *(adjacent, not an assigned check)* wave evidence can be landed | addendum §2/§4 | `.ufo/waves/` ignored; r38 and r39 both 0 tracked files; helper force-tracks only named files | WARN — L1 must name each wave file, not the directory |

**Overall:** the wave shape is sound — band, attack share, planner mask, connector count, single
batch, and prompt distinctness all pass with margin, and no seat is positioned to write a lane file
the L1 must integrate. The one calibration defect is mechanical and cheap: three items ship
CWD-relative commands that fail from the seat's own starting directory, absorbed this wave only
because the three seats repaired them by hand; the C3 counter compounds it by raising an uncaught
`FileNotFoundError` on a relative `--fixture` where its docstring promises exit 2. Three further
findings sit outside the shape check but land in the same integration step: the register arm has no
build seat, `gen-w1-spec.py:2` claims 72 seats for a 71-seat wave, and every file this wave produces
is gitignored, so the L1's evidence commit must name the files one by one or the round reproduces
the R4 defect it claims to close.

## 10. Scratch

`/fast/scratch/hyaku/souji-r39/W1CritWave` was used as `--scratch` for two counter invocations and
removed at the end of this seat; `ls` after removal is empty (verified below), so no tree is left on
disk by this seat.

```
$ rm -rf /fast/scratch/hyaku/souji-r39/W1CritWave && ls -d /fast/scratch/hyaku/souji-r39/W1CritWave 2>&1
ls: cannot access '/fast/scratch/hyaku/souji-r39/W1CritWave': No such file or directory
```

No tool was installed or upgraded by this seat. No lane bytes, fleet bytes or receipts were written;
the only file this seat wrote is this report.

## 11. Command index (every command this seat ran)

Structural reads (no output quoted above unless noted):

```
$ ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/ ; ls -la .../census/round-39/
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
$ read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt
$ cat /home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md
$ cat /home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json
$ ls /home/vgpnk/Projects/shokunin/scripts/hyaku/
$ cat .ufo/waves/round-39/w1.ready ; cat .ufo/waves/round-39/w1.ready.partial
$ wc -c .ufo/waves/round-39/w1-validation.err .ufo/waves/round-39/w1-gen.err
$ grep -n "ready.partial\|partial" /home/vgpnk/Projects/shokunin/scripts/hyaku/inline-dispatcher.py
$ grep -n "planner" /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs
$ sed -n '8,22p' /home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md
$ sed -n '1,20p' .ufo/waves/round-39/w1/W1ExecC1Base.md ; sed -n '1,12p' .ufo/waves/round-39/w1/W1ExecRegistry.md
$ head -30 census/round-39/make-cells.py ; head -3 census/round-39/c1-items.tsv
$ read census/round-39/c3-counter.py:58-92 ; read census/round-39/c3-counter.py:104-150
$ ls -la census/round-39/records/ ; cat census/round-39/records/c1-before.txt
```

Machine checks (JSON analyses over `w1-spec.json` / `w1-dispatch.json`, run with `python3 -c` or
`python3 - <<'EOF'` from `/home/vgpnk/Projects/shokunin/souji-shokunin`): spec keys and item count;
role counter + attack share + planner + connector + duplicate names/prompts; dispatch
`policy`/`counts`/`registry`; per-item absolute-path presence; write-verb × production-path scan;
mutating-git/jj verb scan; runnable-line relative-path scan; `--root .` scan; `agent` vs `role`
mapping; `Report:` trailer uniqueness; pairwise prompt Jaccard; partial-file mapping (44 entries, 0
keys outside the spec, 0 duplicated values); `.ufo/reports/` write-target scan; adjacency item list.

Targeted probes (quoted in full in the sections above):

```
$ cd /home/vgpnk/Projects/shokunin && python3 -B census/round-39/c1-counter.py --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c1-counter.py --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1CritWave
$ cd /home/vgpnk/Projects/shokunin && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d --items /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv --register /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/cells.tsv
$ cd /home/vgpnk/Projects/shokunin && python3 -B tests/fixtures/r39-drift-record-rules.py --tool tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r39/W1CritWave
$ cd /home/vgpnk/Projects/shokunin && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --fixture tests/fixtures/r38-drift-record.py --scratch /fast/scratch/hyaku/souji-r39/W1CritWave
$ ls -la census/round-39/cells.tsv ; git ls-files census/round-39/
$ grep -n "cells.tsv" .ufo/waves/round-39/gen-w1-spec.py
$ grep -n "72\b" .ufo/waves/round-39/gen-w1-spec.py
$ grep -rn "adjacency" --include="*.md" /home/vgpnk/Projects/shokunin/souji-shokunin | grep -v "^./.ufo/waves"
$ grep -n "adjacency" corpus/lessons/round-38*.md
$ grep -n "mkdtemp\|/var/tmp\|/tmp" census/round-39/c1-counter.py census/round-39/c2-counter.py census/round-39/c3-counter.py
$ grep -n "add_argument" census/round-39/c1-counter.py census/round-39/c3-counter.py
$ grep -n "fixture\|root" census/round-39/c3-counter.py
$ grep -n "cd /home\|--root\|No such file\|can't open" .ufo/waves/round-39/w1/W1ExecC3Baseline.md
$ grep -n "cd /home\|--root\|No such file\|can't open" .ufo/waves/round-39/w1/W1ExecC3Fixture.md
$ grep -n "cd /home\|--root\|No such file\|can't open" .ufo/waves/round-39/w1/W1ExecC2Docstring.md
$ grep -n "\-\-root\|cd /home\|python3 -B" .ufo/waves/round-39/w1/W1ExecC1Base.md
$ rm -rf /fast/scratch/hyaku/souji-r39/W1CritWave && ls -d /fast/scratch/hyaku/souji-r39/W1CritWave
$ wc -l .ufo/waves/round-39/w1/W1CritWave.md ; git status --porcelain .ufo/waves/round-39/w1/W1CritWave.md
$ git -C /home/vgpnk/Projects/shokunin status --porcelain | grep -i "critwave\|W1CritWave"
$ head -5 .gitignore
$ git check-ignore -v .ufo/waves/round-39/w1/W1CritWave.md
$ git ls-files .ufo/waves/round-38 | wc -l ; git ls-files .ufo/waves/round-39 | wc -l ; git ls-files .ufo/waves | wc -l
$ sed -n '630,730p' /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh
$ sed -n '654,666p' /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh
$ cat census/round-39/c1-items.tsv
```

Two commands failed for environmental reasons and are reported as such, not as findings:
`cat scripts/hyaku/ufo-wave-policy-v2.json` from the lane (the policy lives in the fleet root, read
there instead), and `sed -n '1,40p' AXES.md` (no `AXES.md` at the lane root; the axis table is
`SCORECARD.md`'s `## Axes`). `grep -rln "planner mask"` over `scripts/hyaku` and `docs` returned
nothing — the planner rule is in `lane-addendum.md` §2, quoted in §3 above.
