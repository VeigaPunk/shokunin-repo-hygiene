# R40w2connector02 — cross-source pattern finder (souji round 40, wave 2, FALSIFY)

Seat: R40w2connector02 (connector, leaf — no subagents). Date: 2026-10-28.
Bytes attacked: the landed instrument commit **128e412b0ced3c243dc27c3dd3332054a611bc2e**
(`census/round-40/{c1-counter.py,c2-counter.py,c3-counter.py,docstring-classes.py}`,
`tests/fixtures/r40-drift-record-branches.py`, `tests/fixtures/r40-docstring-joined.py`), extracted
into a private clone; all counters were run from those extracted bytes, never from the worktree.
Lane touched read-only; no committed file, counter, fixture, preregistration, SCORECARD or LOG edited.

Task: search the OTHER lanes' corpora and lessons for lessons about (a) a docstring/class map read
one line at a time, (b) a register row whose commit is not a strict descendant of its receipt
revision, (c) a mutation counter that scores a detected mutant as survived — report sibling
file:line hits and what this lane could learn, attacking the landed instruments with them.

---

## 0. Environment and method

- Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2connector02/` (clone, fixture repos, counter
  `--scratch`/`--work` dirs). **Removed before this report was finalized; verified absent**
  (`ls /fast/scratch/hyaku/souji-r40/w2/ | grep R40w2connector02` → 0 matches).
- Landed bytes isolated: `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git clone -q --no-hardlinks
  /home/vgpnk/Projects/shokunin/souji-shokunin $B/clone/lane && git -C $B/clone/lane checkout -q --detach
  128e412b0ced3c243dc27c3dd3332054a611bc2e`; `git rev-parse --show-toplevel` asserted equal to the clone.
- No installs. No pacman (host-wide pause honored). Tools used: git, python3 (system).
- Note: the worktree diverged from 128e412b while I worked (the L1 landed 8 follow-up commits; HEAD is
  `549d9ec53a1f5932337ff14438fcd22b0621828d`, 128e412b is its ancestor). Where relevant I state
  landed vs HEAD separately; every verdict below names the bytes it ran.

## 1. Sibling-lane hits (the cross-source deliverable)

### (a) docstring/class map read one line at a time — granularity lessons

- `chousa-shokunin/corpus/lessons/2026-10-16-gate-behavioral-baseline.md:70-73` — "**Line granularity
  vs field granularity**, with chousa numbers. Only 1 of 8 lines contains the volatile token..." and
  `:180-183` — "**A pin's resolution is the pinned surface's granularity.** ... a verify-all pin misses
  a whole class of [changes]". A line-scoped read resolves only what sits on the line; that is exactly
  the r39 one-line docstring read this round replaces, and it says the miss is systematic, not unlucky.
- `game-dev-2d-shokunin/corpus/lessons/r66-rejection-clause-surface.md:30-36` — two channel shapes for
  the same predicate: "(i) **per-LINE** `ERROR:` presence scan over `output.splitlines()` ... (ii)
  **whole-BLOB** substring tests ... Evaluation order in effect: blob clauses → allowlist-gated line
  scan." Neighbouring lane hit the same first-line/per-line vs whole-entry fork and documents which
  shape is allowlist-immune — the same granularity question as first-line vs joined docstring entry.
- `chousa-shokunin/corpus/lessons/round-26.md:30` (R26-M1) — "base gate2383–2387 **materializes every
  line before parsing** ... C1 removes the per-line materialization". Lesson: the parse unit is a
  contract decision, and per-line units got a lane in trouble before.
- `chousa-shokunin/corpus/knowledge/line-binding-r31.md:22` — RFC 5147 line positions vs 1-based gate
  lines: even the "line" unit itself needs a definition pinned in the entry.

### (b) register row whose commit is not a strict descendant of its receipt revision

- `chousa-shokunin/corpus/evidence/round51/receipt-check.py:39-45` — the sibling's receipt gate:
  `RECEIPT_REV_UNKNOWN` (commit not in repo), `RECEIPT_REV_UNLANDED` "**not an ancestor of the tip**",
  `RECEIPT_TOOL_ABSENT`, `RECEIPT_TOOL_MOVED` ("the tool's blob at the tip differs from its blob at
  that revision — the receipt measures code the tip no longer has"). Documented in
  `chousa-shokunin/corpus/QUALITY.md:900-908`, including the named limit: "the header is a convention,
  not a signature — **a receipt can name a revision it did not run at**".
- `audio-shokunin/corpus/lessons/round-101.md:12` (M6, citation lineage drift) — "`git merge-base
  --is-ancestor 5755be5b main` and `... 0cbbb3bb main` both exit 1 ... **A cited commit must be
  reachable from the published branch**, or the evidence must say `branch-scoped`."

### (c) mutation counter that scores a detected mutant as survived — verdict-vocabulary lessons

- `tameshi-shokunin/corpus/knowledge/witness-scoped-kill-verdict.md:12-15` — shmutant's three
  verdicts: "`killed`: 'The suite went red **on its witness**'"; "`accidental`: 'red, but not on its
  witness'"; "`survived` means green" (`:15` and `mutation-score-semantics.md:15`); `:29` —
  "Classification is killed-on-witness iff a full-count red run includes at least one label in the
  pre-registered witness set; accidental iff red/full-count with none; green is survived; **missing
  denominator or nonstandard/unrunnable run is inconclusive**"; `:48` — "a mutant may fail several
  cases, but only a pre-registered match establishes that its intended assertion failed".
- `tameshi-shokunin/corpus/knowledge/mutation-score-semantics.md:16` — "**Inconclusive** — timeout,
  crash before summary, or missing count is not a kill and is excluded". A crash is never 'survived'.
- `tameshi-shokunin/corpus/SOURCES.md:16-17` — S005 (mutmut): "env-clearing tests **produced false
  survivors** (fixed 3.8.0)"; S006 (shmutant) three-verdict discipline. `corpus/README.md:61,617`
  (frontier F2, witness-scoped kill verdicts).

## 2. Attacks on the landed bytes — commands and outputs

### A1 — C1: a token-only forged item CLOSES on the landed bytes — **FALSIFIED** (repaired at HEAD)

Landed binding check (`census/round-40/c1-counter.py:258` @128e412b):
`if not any(evidence_rev.lower() in line.lower() for line in good)` — the pointer is bound per **file**
(some token-satisfying line), not per **line**. The prereg says "each anchored item line must carry a
resolvable, revision-bound evidence pointer"; the landed code closes an item when *any other* good line
in the same file carries the revision. Fixture repo (scratch, identity scoped to the repo,
`rev-parse --show-toplevel` asserted): `src/tool.py` line 1 = bound real line, line 2 = token-only
forged line, register row clean (`mismatches=0 violations=0`):

```
python3 -B $B/clone/lane/census/round-40/c1-counter.py --root $D --rev $R4 \
  --items items-real.tsv --forged forged.tsv --register reg-ok.tsv --scratch $B/c1fix/work
ITEM I-REAL CLOSED
FORGED I-FORGED CLOSED (must stay OPEN) CLOSED
REGISTER cells=1 mismatches=0 commit_rows=1 commit_hashes=1 violations=0 ok
SUMMARY items=1 open=0 forged=1 forged_open=0 forged_closed=1 ... register_mismatches=0 register_violations=0 ...
EXIT1=1
```

Exit 1 is driven **solely** by `forged_closed=1`: the prereg kill condition "Kill if the forged line
closes" is met on the landed bytes (the round's own forged control set happens to live in a separate
file — `census/round-40/c1-forged.tsv` — so its receipt never exercised this shape).
At HEAD (549d9ec5, after 994de3b+dc8bd47) the same probe gives
`FORGED I-FORGED OPEN EVIDENCE-NOT-BOUND` — repaired; a fully-formatted forgery (line carries
`` `evidence/ev.md` `` + rev) is still OPEN `EVIDENCE-DISAGREES expected=['subcases=21']` because HEAD
also binds the evidence **content**. LANDED: FALSIFIED. HEAD: repaired (verified).

### A2 — C1: evidence is existence-only on the landed bytes; a decoy pointer closes — **FALSIFIED** (repaired at HEAD)

Landed `c1-counter.py:256-258` reads the evidence path only via `git_show(...) is None`. Item with
`evidence=decoy/other.md@R1` where `decoy/other.md` = "placeholder bytes, nothing to do with any
census item", closing line = tokens + rev:

```
python3 -B .../c1-counter.py --root $D --rev $R4 --items items-decoy.tsv --register reg-ok.tsv
ITEM I-DECOY CLOSED
REGISTER cells=1 mismatches=0 ... violations=0 ok
EXIT2=0
```

An item closes citing "evidence" whose content was never read. The lane's own r37 reconciler is
stricter (`tools/souji-citation-reconcile.py:287`: receipt must appear **backticked** on the line) —
the new counter was looser than the lane's older tool. At HEAD the same probe gives
`ITEM I-DECOY OPEN EVIDENCE-NOT-BOUND`, and content disagreement gives `EVIDENCE-DISAGREES`.
LANDED: FALSIFIED. HEAD: repaired (verified, including the fully-formatted forgery probe).

### A3 — C1 register strict-descendant leg — **SAFE** (on landed bytes; unchanged at HEAD)

```
run 3 (commit older than receipt_rev): REGISTER RR-BACK BACKWARDS commit-not-descendant ... violations=1, EXIT=1
run 4 (commit == receipt_rev):        REGISTER RR-EQ  BACKWARDS commit-equals-receipt_rev ... violations=1, EXIT=1
run 5 (no commit cell):               REGISTER RR-NC  BACKWARDS no-commit ... violations=1, EXIT=1
```

Landed `c1-counter.py:215-227` implements strict descendant = resolves, ≠ receipt_rev, and
`merge-base --is-ancestor receipt_rev commit`; every not-strict shape I could construct is rejected.
Residual (named limit, mirrors `chousa QUALITY.md:906`): the leg cannot tell whether the register was
actually produced at `receipt_rev` — a convention, not a signature. SAFE.

### A4 — C2: the landed counter cannot run from its own landed bytes — **FALSIFIED** (fixed by 8a5fbdb)

```
$ git clone … && git -C clone/lane checkout -q --detach 128e412b…
$ cd clone/lane && python3 -B census/round-40/c2-counter.py --root … --rev 128e412b… --base-rev 0242085… --scratch …
Traceback (most recent call last):
  File ".../census/round-40/c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
ModuleNotFoundError: No module named 'docstring_classes'
EXIT_LANDED_BYTES=1
```

The landed tree ships `docstring-classes.py` (hyphen, `git ls-tree 128e412b census/round-40/`);
`import docstring_classes` cannot resolve. Providing a hand-renamed copy in scratch, the counter then
fails three legs at the landed rev:

```
LEG L1 FAIL new rc=2 class=True old rc=2 class=True     # discriminator assumes the REV-UNRESOLVED
LEG L2 FAIL new rc=2 class=True old rc=2 class=True     #   defect is live at base 0242085 — it is not
LEG L5 FAIL new=None old(one-line)=None                 # run_fixture (c2-counter.py:178) appends --work;
EXIT_C2_PATCHED=1                                       #   the fixture rejects it: "error: unrecognized
                                                        #   arguments: --work …" exit 2 → no SUMMARY
SUMMARY legs=7 pass=4 fail=3 harm=0
```

So the landed bytes can produce neither a run nor the claimed `legs=7 pass=7` receipt; the receipts in
`census/round-40/records/c2-after-d.txt` were measured at `--rev 549d9ec5` (post-landing bytes), not at
the landed instrument commit. The join itself is real (L4 PASS with
`missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']`, L4b PASS — sibling lesson (a) was correctly
applied). At HEAD the counter runs and gives `SUMMARY legs=7 pass=7 fail=0 harm=0`, exit 0 (verified),
matching the receipt. LANDED: FALSIFIED. HEAD: repaired (verified).

### A5 — C3: landed kills are unattributable (`failing=-`) despite the docstring's repair claim — **FALSIFIED** (fixed by 8a5fbdb)

Landed `c3-counter.py:116-117` @128e412b parses failing cases with
`... if l.startswith("case-") and l.endswith("FAIL")`, but the landed fixture prints
`case-%s=%s%s ... " " + detail` (`tests/fixtures/r40-drift-record-branches.py:142`) — a FAIL line
always ends with its detail, never with "FAIL", so the list is always empty. Real battery run at the
landed rev:

```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- base:rc=0 fails=0
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
EXIT_C3=0
```

Four kills, zero named cases — the landed docstring promises "prints the failing case names, so a kill
is attributable to the branch case that covers it". At HEAD the parse is fixed and my M16 probe
reports `failing=skip-suppresses`. Battery verdict itself: **SAFE** (4/4 killed, pristine ok,
base_killed=0, cases=8). Attribution claim on landed bytes: FALSIFIED.

### A6 — C3: a detected mutant is scored SURVIVED via the stderr channel — **FALSIFIED, still live at HEAD** (the surviving falsifier)

Landed and HEAD `c3-counter.py:115,118` (HEAD bytes verified identical here):
`crash = "Traceback (most recent call last)" in proc.stderr`; `killed = rc==1 and fails>0 and not crash`.
Crash detection is a marker string on the fixture's **stderr channel**, not an actual fixture-crash
test. A fixture that detects the mutant (own `SUMMARY`, `rc=1`, `fail=1`) and forwards captured child
diagnostics to its own stderr — a normal fixture design — flips the verdict:

```
fixture stdout: case-skip-suppresses=FAIL tool_rc=1
                SUMMARY cases=1 pass=0 fail=1        (fixture exit 1, stderr carries the echoed
                                                      "Traceback (most recent call last):" marker)
LANDED score() on DETECTED M16 mutant: killed=False detail='rc=1 fails=1 crash=True failing=-'
HEAD   score() on DETECTED M16 mutant: killed=False detail='rc=1 fails=1 crash=True failing=skip-suppresses'
```

A red-on-witness run with its own failure summary is scored `survived` (the SUMMARY's
`survived=len(results)-killed` bucket, `c3-counter.py:202-203`) — exactly the defect class the landed
docstring claims the r39→r40 repair removed ("a genuinely detected mutant was scored SURVIVED"), and
exactly sibling lesson (c): tameshi's discipline is `survived` = green, red-not-on-witness =
accidental, unrunnable/crash = **inconclusive**, never a false survivor. The r39 variant laundered the
marker through stdout; the r40 fix moved the blind spot to stderr instead of closing it.
**FALSIFIED at 128e412b and still live at 549d9ec5.**

## 3. Verdicts

| Attack | Bytes | Verdict | Key evidence |
|---|---|---|---|
| A1 C1 forged token-only line closes | 128e412b | **FALSIFIED** (prereg kill condition met) | `FORGED I-FORGED CLOSED (must stay OPEN)`, clean register, exit 1 solely from forged_closed=1 |
| A2 C1 decoy evidence pointer closes | 128e412b | **FALSIFIED** (predicate sentence; content never read) | `ITEM I-DECOY CLOSED`, exit 0 |
| A1/A2 same probes at HEAD 549d9ec5 | 549d9ec5 | SAFE (repaired: path backtick + EVIDENCE-DISAGREES) | `OPEN EVIDENCE-NOT-BOUND` / `OPEN EVIDENCE-DISAGREES` |
| A3 C1 register strict-descendant | 128e412b | SAFE | BACKWARDS × 3 (not-descendant / equals / no-commit), violations=1, exit 1 |
| A4 C2 operability | 128e412b | **FALSIFIED** (cannot import; L1/L2/L5 fail with workaround; L5 passes `--work` the fixture rejects) | `ModuleNotFoundError: No module named 'docstring_classes'`; `SUMMARY legs=7 pass=4 fail=3` |
| A4' C2 at HEAD | 549d9ec5 | SAFE (receipt `legs=7 pass=7` reproduces) | exit 0, SUMMARY legs=7 pass=7 |
| A5 C3 kill attribution | 128e412b | **FALSIFIED** (dead `endswith("FAIL")` parse → `failing=-` on all 4 kills) | battery output `failing=-` ×4; fixed at HEAD (`failing=skip-suppresses`) |
| A5' C3 battery kill conditions | 128e412b | SAFE | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`, exit 0 |
| A6 C3 detected-mutant-scored-survived | 128e412b **and HEAD** | **FALSIFIED (live at both)** | `score()` → `killed=False detail='rc=1 fails=1 crash=True'` on a detected mutant |

Round-level: the landed instrument commit 128e412b does not support its own C1/C2 claims (A1, A2, A4);
the receipts in `census/round-40/records/` are measured at 549d9ec5, not at the landed instrument
commit, so no receipt certifies the landed bytes. The L1's post-landing commits (8a5fbdb, 994de3b,
42e18ed, dc8bd47) repair A1/A2/A4/A5. A6 remains open at HEAD.

## 4. What the lane could learn (cross-source moves)

1. **A6 (from tameshi's verdict vocabulary, `witness-scoped-kill-verdict.md:12-15,29` and
   `mutation-score-semantics.md:16`):** classify the fixture run, not a channel string — `survived`
   only when green with a full count; red-with-own-summary = killed (on the failing cases it names);
   crash/NO-SUMMARY/BAD-SUMMARY = a separate `inconclusive` bucket, never folded into `survived`
   (`c3-counter.py:202` counts `survived=len(results)-killed`). Concretely: crash should be detected
   by outcome (no/bad SUMMARY, or non-{0,1} exit), not by `"Traceback" in stderr`; and a detected kill
   must not be downgraded by any stderr content. This is the one falsifier still live at HEAD.
2. **A1/A2 (from chousa's receipt gate, `receipt-check.py:39-45`, and its QUALITY limit):** bind
   pointers per line and by content+digest, not per file and by existence — the r37 reconciler already
   required the backticked path (`:287`); the new counter initially lagged the lane's own older tool.
   HEAD now matches the reconciler's discipline; keep the per-line reading explicit in the contract.
3. **(a) granularity (from `gate-behavioral-baseline.md:180` "a pin's resolution is the pinned
   surface's granularity" and game-dev-2d `r66`:30-36):** the landed docstring-classes `_entries`
   (`docstring-classes.py:43-66`) is still a line heuristic (indent+blank-line rules), not the PEP 257
   logical-line join its docstring claims; a whitespace-only line splits an entry and any indented
   prose glues into the preceding class. Fine for the frozen pairs (L4 re-derives them at runtime),
   but the module docstring over-claims the mechanism — worth one honest sentence.
4. **Evidence chain (from audio `round-101.md:12` M6):** receipts should name and be re-runnable at
   the bytes they certify. `records/*-after-*.txt` name `--rev 549d9ec5` while the round's landed
   instrument commit is 128e412b — after this wave the two coincide only because the L1 re-landed the
   instruments; the landed-commit receipts (e.g. `c2-after.txt` if any at 128e412b) would have shown
   the ModuleNotFoundError honestly.

## 5. Second-order effects and risks of the proposed move

- Splitting `survived` into survived/inconclusive changes the SUMMARY line shape; any consumer regex
  (`records/` parsers, the round receipt greps) must be updated in the same commit — the SUMMARY is
  the receipt's parse surface.
- Outcome-based crash detection must still fail the round on inconclusive runs (exit 1), or a broken
  fixture could pass vacuously; keep `killed_n == len(results)` with inconclusive counted as not-killed.
- Tightening the crash rule may retroactively change recorded C3 receipts' `survived` counts; re-run
  the battery at the pinned rev before rewriting any recorded numbers (append-only corrections only).

## 6. Scratch

`/fast/scratch/hyaku/souji-r40/w2/R40w2connector02/` — **removed**, verified absent before this
report was written. No other writes outside this report file.
