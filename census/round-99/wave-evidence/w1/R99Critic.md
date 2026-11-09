# R99Critic — falsification of C1/C2 wordings against r99 bytes

Lane: souji. Round: 99. Lane base: c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b.
Seat: R99Critic (godspeed; axes: calibration movability, operability wording-to-code, no-harm on hosts).
Scratch: /fast/scratch/hyaku/souji-r99/R99Critic/ (deleted before yield). Reproducers: `.ufo/waves/round-99/w1/R99Critic/reproducers/` (shapes-relabel.tsv, c1-frozen.txt, c1-relabel.txt, c1-r97.txt, c2-results.txt, analyze_t1.py).

## Axes
- calibration (C1 movability): is `shapes=17 mismatched=0` movable by relabelling the frozen file? Is the frozen file hash binding?
- operability (C2 wording-to-code): does 'spawn pid and its ppid-chain descendants only' match the r99 code exactly? Is the counter-descendant case spared? Does it falsify the r98 sentence?
- no-harm: no predicate/byte edits, no host sysctls, scratch only. (No tools installed; none needed.)

## C1 verdicts

Claim C1 sentence 1: "`census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv` prints `SHAPES-SUMMARY shapes=17 mismatched=0` with the r98 hook, kinds read from the frozen file." — **HOLDS.**

Command (exit 0):
`python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes --work $S/c1-frozen`
Observed:
- `FREEZE sha256=8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14`
- `SHAPES-SUMMARY shapes=17 mismatched=0` (q1o/q1q hooked=70, q1i hooked=0; full per-shape table in reproducer c1-frozen.txt)
- EXIT:0
Hook is a byte copy: `diff census/round-99/c1-survivor-search.py census/round-98/c1-survivor-search.py` → identical (sha256 e8ba780a…); r99 declared-shapes.py SHAPES tuple removed, kinds read via load_shapes() (lines 13–27) and printed from the file.

Claim C1 sentence 2: "a relabelled copy of the file (same hook) moves the count, so the frozen file hash is part of the claim." — **HOLDS as measured, NARROWED on binding.**

Relabel attack (q1o=declared, q1q=declared, q1i=crash — the r98 K2 triple), command (exit 1):
`python3 -B …/declared-shapes.py --freeze $S/shapes-relabel.tsv --search …/c1-survivor-search.py --scripts …/shapes --work $S/c1-relabel`
Observed:
- `FREEZE sha256=004356d76d94c54158232f250077c6995b5103b16f34ef4111e4933bc6cc330a` (relabel hash ≠ frozen hash)
- `SHAPES-SUMMARY shapes=17 mismatched=3` + `MISMATCH q1o-save-then-bare-raise.py`, `MISMATCH q1q-caught-then-direct.py`, `MISMATCH q1i-finally-then-catch.py`
- EXIT:1
So relabelling the frozen file **does** move the count (0→3) under the same hook: the M6 movability is closed **iff** the file is the pinned hash `8bc642…`. The runner prints FREEZE sha256 so a relabelled copy is detectable against the pinned value. Reproducer: shapes-relabel.tsv + c1-relabel.txt.

Controls (both mismatched=3, exit 1):
- r97 hook vs frozen file: `SHAPES-SUMMARY shapes=17 mismatched=3` (q1o/q1q hooked=1, q1i hooked=70 — reproducer c1-r97.txt).
- r95 hook vs frozen file: mismatched=3 (t1/t4/q1i MISMATCH, observed in tool output).
- Reverse movability (important narrowing): r97 hook vs **relabelled** file → `SHAPES-SUMMARY shapes=17 mismatched=0`, exit 0. The relabelled file (hash 004356…) makes the r97 (wrong) hook pass. The freeze only binds if the hash is pinned to `8bc642…`; scoring on a relabelled copy with hash 004356… would pass the r97 hook. **The binding is the pinned hash, not the file mechanism** — the claim sentence already says this ("so the frozen file hash is part of the claim"), so it holds, but the reproducer shows the reverse direction explicitly.

Narrowings / residue (not falsifying C1):
1. Schema is lax: an 18-row file (extra duplicate a1 row) prints `shapes=18 mismatched=0`, exit 0 — the runner validates header and 4-col rows (unknown kind raises ValueError, good) but never asserts N=17 or uniqueness. A 17-vs-18 count is visible in the SUMMARY line, so a careful reader notices; a count-only check could be fooled by a 9-row 0-mismatch subset (e.g. dropping all three hard rows and asserting mismatched=0 is satisfiable with shapes=14). Smallest safe correction: L1 (or a future runner) — reasoned note for the report, not an edit (predicates frozen; no seat edits in place).
2. The `plain` column is empty in every row and unused by the runner (predicate is kind-driven: declared ⇒ plain==hooked, crash ⇒ hooked==70); the `comment` column is unparsed prose. Hash still pins these bytes, but they carry no predicate weight.
3. t4 comment reads "terminating finally/re-raise (last stamp RR)" while kind=declared; the F3 freeze note in declared-shapes.expected is the recorded rationale (q1i pinned declared; t1/t4/q1i declare). Comment is the only RST-visible tension; it is prose under the hash, not a predicate error (measured hooked=0=plain=0).

## C2 verdicts

Claim C2 sentence 1: "the r99 arms counter reaps only the recorded spawn pid and its ppid-chain descendants" (wording-to-code). — **HOLDS (code matches the sentence exactly).**

Static diff `census/round-98/c2-setup-arms.py` → `census/round-99/c2-setup-arms.py` (the only semantic change; sibling R99ExecC2 still editing — hash drifted 60a8c226…→03e8a99e… during my runs, semantic diff stable):
- DELETED: `elif _is_descendant(pid, os.getpid()): pass` + branch-(c) comment (r98 lines 189–191). Grep of r99 shows no `_is_descendant(pid, os.getpid())` in _reap_owned (only `os.getpid()` in exclude sets / S13 path).
- r99 _reap_owned kills iff pid==spawn_pid with starttime match, else iff `_is_descendant(pid, spawn_pid)` (ppid-chain walk, S075 field 4, fields 4/22). Docstring: "a counter-descendant carrier that is not a spawn-chain member is NEVER killed (r98 branch (c) removed)". Survivors rule updated to the same spawn-chain predicate.
- The compat `_reap_by_identity(ident, exclude)` delegates to `_reap_owned(..., None)` whose comment branch `continue`s (never kill on argv alone) — no hidden argv kill path.

Claim C2 sentence 2: "a planted counter-descendant carrier outside the spawn chain survives (cross-arm probe)". — **HOLDS** (clean run; storm runs confounded — see honesty note).

Instrumented cross-arm probe (R98Sentinel probe + 1 Hz liveness monitor), vs r99 counter:
- `CARRIERS-FOUND 3` (counter-descendants via a different arm's fixture; ancestry confirmed ppid-chain reaches counter but never the T1 spawn pid)
- monitor: carriers reparented `ppid=other-fixture → ppid=counter (2005191)` via PR_SET_CHILD_SUBREAPER, state S throughout
- `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0`, `CROSS-ARM-RESULT … killed=no` (×3), `CROSS-ARM-SUMMARY label=r99i counter_exit=1 carriers=3 signalled=0 signalled_pids=none`, EXIT:0. Full table in c2-results.txt.
So the branch-(c) removal is effective: the R98Sentinel FINDING-4 case is now spared.

Claim C2 sentence 3: "a foreign decoy survives (decoy test)". — **HOLDS.**
Decoy test vs r99 counter: `DECOY-PLANTED n=86 dead=0 alive=86 counter_exit=0`, `DECOY-SUMMARY verdict=spared`, `ARMS-SUMMARY arms=20 conform=20`, EXIT:0.

Claim C2 sentence 4: "the r98 CM8 argv-only mutant is still killed by the decoy test". — **HOLDS.**
Decoy test vs census/round-98/c2-cm8-mutant.py (argv-only reap, `# CM8 forgery: ownership check removed`): `DECOY-PLANTED n=85 dead=84 alive=1 counter_exit=0`, `DECOY-SUMMARY verdict=killed`, EXIT:1. The predicate still discriminates.

Claim C2 sentence 5 (implicit): does this falsify the r98 claim sentence? — The **r98** sentence ("reaps ONLY (a) spawn pid or (b) ppid-chain descendants") **was falsified by r98 code** (branch (c) widened it: `_is_descendant(pid, os.getpid())` killed any counter-descendant carrier; R98Sentinel cross_arm_probe reached a P1-arm carrier by T1's reap; recorded in r98 spotcheck, sentence flagged "does not verify as written"). That fingerprint is now gone from r99 code, so the falsification does not carry forward: the r99 sentence matches the r99 code. **Verdict on the r98 sentence: falsified (by r98 bytes, already found); verdict on the r99 sentence: holds.**

## New finding: r99 under-reaps the T1 escapee (the cost of removing branch (c))

The PIPHOLDER fixture forks a setsid child then its parent exits at once. After the parent exits, the escapee's ppid chain no longer reaches the T1 probe (spawn pid): it reparents to the subreaper (counter) or systemd. My decoy-r99 run proves it:
- `T1.out`: `--survivors 0 planted-killed 0--` — the reap killed nothing (the only token-carrying spawn-chain candidate is the probe itself, excluded).
- **Live escapee sighted**: pid 3686187, ppid 1525 (`/usr/lib/systemd/systemd --user`), session 3686187, state S, argv `fixture-pipe-holder.py … --work …/decoy-r99/arms/T1/positive`. It was still alive long after the counter exited (I killed it myself with pkill for cleanup; its liveness at that point is the evidence).
- `conform=20` is therefore partly **vacuous**: survivors counts only spawn-chain members, and the escapee is not one, so survivors=0 trivially; the conform byte cannot witness the reap. The r99 counter REAPS NOTHING on T1. If the r99 claim sentence promises the escapee is reaped ("reaps only the recorded spawn pid and its ppid-chain descendants" read as including the T1 grandchild), that sub-sentence is **falsified in the under-reaping direction**: the escapee is spared, not reaped. The build-spec anticipated this ("otherwise it is NOT killed (report that as an open limit … do not invent a rule)"). This is a tradeoff the canonical judge must weigh: the sentence is now exactly true (code=wording) but the counter no longer reaps the escaped grandchild it exists to reap — operability was bought by removal, not by ownership record (escapee pid+starttime never recorded). Smallest safe correction (for L1, not edited here): either narrow the claim sentence to name the open limit ("T1 escapee unreachable once its parent exits") or fix the reap predicate to record the escapee (e.g. probe-reported grandchild pid+starttime) in a later round. Severity: MEDIUM — the decoy predicate (the binding C2 witness) is unaffected, and sparing a foreign decoy is prioritised over reaping the escapee, but "operability 8" now rests on a reap that kills only the probe itself.

## Honesty / methodology (unrun ≠ passed)

- Cross-run contamination: 3 of my 4 cross-arm runs coincide with sibling seats running decoy storms concurrently. Evidence: T1 probe `exit=-15` (SIGTERM; no SIGTERM sender exists in either counter — only SIGKILL killpg sweeps) in runs cross-r99, xr98, and the first r99 run; carrier transitions `S → Z (ppid=counter)` with T1.out `--planted-killed 0--` — i.e. the carriers were zombie-killed environmentally, not by either counter's T1 reap. I do **not** rely on those storm runs for any verdict. The clean verdicts: r99i run (T1 exit=2, signalled=0) for sparing; the committed R98Sentinel receipt (`label=r98 … signalled=3`, counter_exit=1) for the r98 control direction. A finding must beat an opinion; the spared verdict is anchored in the clean run's monitor log plus the static diff.
- The r99 c2-setup-arms.py hash drifted mid-wave (60a8c226… → 03e8a99e…); the semantic diff vs r98 (branch-(c) deletion + comment updates) was re-verified at both hashes. My decoy/cross-arm runs straddle the edit; L1 should note the hash at freeze.
- No claim byte / predicate was edited by this seat (read-only git only; files created: this report + reproducers dir + instrumented probe copy in scratch).
- Pre-existing host pollution (not mine): decoy sleepers from sibling seats (R99ExecC2, R99MutC2) observed in ps; I pkill'd only my own escapee's token path.

## Smallest safe corrections (for L1)

1. C1: no change required (sentence holds). Optional hardening: assert N=17/unique in the runner or note the count line as load-bearing in the report.
2. C2: decide whether the under-reap is acceptable: either caption the claim sentence with the escapee-unreachability limit or schedule a round that records the escapee identity at spawn. Do not re-add branch (c) without naming it in the sentence.

## L0 questions
None. Tooling: no installs; none needed.

Report: .ufo/waves/round-99/w1/R99Critic.md
