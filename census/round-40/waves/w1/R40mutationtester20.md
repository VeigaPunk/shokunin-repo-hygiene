# R40mutationtester20 — C2 operability: mutation testing of the L4 docstring↔runtime class/trigger leg

- Seat: mutation-tester (leaf; no subagent dispatch). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- Distinct item 20, named edge case: **the trigger-side of the L4 comparison** — *the observed-class
  channel and the trigger-word match*, i.e. the two halves between the tool's runtime refusal and the
  docstring entry. Concretely two named defects: **F1 class-token tautology** (the trigger word
  `"missing"` is a substring of the class token `RECORD-MISSING`, so the MALFORMED-side check cannot
  fail) and **F2 path-derived class attribution** (r39 `classify()` is a substring scan over
  stdout+stderr, and the tool echoes the record path into that text, so the *path* can set the
  observed class). This is distinct from sibling `R40executor62` (decoder continuation-ownership /
  attachment boundary) and from `R40scout41`/`R40scout53` (the unenumerated frozen list and the
  `ENOTDIR`/`ENAMETOOLONG` omission). I did not re-derive the frozen-list gap; I attacked what the
  leg *measures*.
- Tool installs/upgrades: **none**. `pacman` untouched. Interpreter `Python 3.14.8`, `git 2.56.0`.
- Lane writes: **this report only**. `git status --short` in the lane shows only the untracked
  `census/round-40/` (pre-existing, not mine); `git diff --stat HEAD` is empty; lane HEAD is
  `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`. No lane file, git/jj index, or config was mutated.
- Scratch: `/fast/scratch/hyaku/souji-r40/R40mutationtester20/` (all work), `TMPDIR` set explicitly
  to `<scratch>/tmp` on every child; removed before yield.

## 0. Verdict summary

**C2 operability: NOT falsified as frozen; but the frozen predicate is UNDER-SPECIFIED in a way that
lets a wrong implementation pass. Two concrete defects are measured, one of which (F1) makes the
r40 leg blind to a single-token class swap that the r39 leg already misses.**

| id | defect | measured effect | falsifier status |
|---|---|---|---|
| **F1** | L4's MALFORMED-side trigger word `"missing"` is a substring of the class token `RECORD-MISSING` → the check is **tautological** | mutant **MU-3** (ENOENT reclassified to `RECORD-MISSING`) is **PASSED by L4** in the real committed counter: `LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False` | **surviving mutant of the r39 leg**; killed only by L6's consumer fixture (`L6 FAIL … 9/10`, harm=1). Already named in r39 as F3 (`census/round-39/waves/w1/W1RevC2Harm.md:280`) — I confirm it and add the mutation evidence |
| **F2** | r39 `classify()` is a substring scan over stdout+stderr; the tool echoes the record path into that text, so the **path** can set the observed class | probe path `…/RECORD-MISSING-absent.tsv` → tool raises `RECORD-MALFORMED`, `classify()` returns `RECORD-MISSING` (misread, reproduced on 5 of 6 revisions) | **not recorded in any r39 artifact** (grep over `census/round-39/waves/w1/*.md` and `corpus/lessons/round-39*.md` for a path-derived class returns nothing). r39 recorded only `classify()`'s *token priority* (`W1RevC2Legs.md:313-316`), not its path sensitivity |
| **F3** | continuation-join alone does **not** repair F1 | a join-only r40 leg (`L4-r40a`) still **PASSES** MU-3; only a class-scoped, token-stripped match (`L4-r40b/c`) kills it | **the r40 claim as frozen is reachable but under-specified**: it names the join, not the trigger match |

The frozen preregistration (`census/round-40/preregistration.txt:8`) asks for "all observed
class/trigger pairs in the frozen list" and "Kill if wrapped trigger is missed, or if any observed
class mapping disagrees with runtime behavior". **The kill rule is satisfiable by an r40 leg that
joins continuations but keeps r39's substring trigger match** — i.e. the join is not the
load-bearing part of the fix. Concrete falsifier and measurement plan below.

## 1. Subject bytes, controls, and fixtures (all committed, all hashed)

Subject: `tools/souji-worktree-drift.py` at the r40 base revision
`0242085909fb6a4ee041c5443d76316ac6d59d4b` — sha256
`e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` (identical at lane tip
`be4cb61`, so the tool did not move in r39's post-verifier commit).

Control: committed `census/round-39/c2-counter.py` at the same revision — sha256
`732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11`.

r39 base bytes for the counter's `--base-rev` arm: `tools/souji-worktree-drift.py` at
`ed30b7f5b77939c9073348d810730bc4f355708d` — sha256
`14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194`.

Scratch git fixture (`/fast/scratch/hyaku/souji-r40/R40mutationtester20/fixture2`), built by
`git archive` of the lane at `ed30b7f5` (base) then `git archive` of `0242085`'s `tools tests
census` (pristine candidate); each mutant is an **independent branch** off the pristine candidate so
no two mutations compound. Every `git` command used `-C <fixture root>` and
`git rev-parse --show-toplevel` was asserted to equal that root before every commit.

```
BASE=c9da85dfd899a977d3b64e0ff8ea623f32e4833a   (r39 base bytes)
PRIS=09c4b74dbf0387d5eb9c0b78d3dbea21bb493621   (pristine r39 tip bytes)
MU1=6dbcb007506649d0a45626ac3ba8466051a8f1b2   (docstring rewrap)
MU2=805e52b684fcaf0ab4a8483d19cd3b3585ab8594   (ELOOP -> RECORD-MALFORMED)
MU3=f8608ef6af47c9cfaca9c9c4d673f06104cb5194   (ENOENT -> RECORD-MISSING)
MU4=5535a660bf782b25576c8ad0713bdf71babb0226   (inverted pair: both lines name both keywords)
```

Mutated `tools/souji-worktree-drift.py` sha256 per branch:

```
MU1 0b431f022185aca33bba118d53e811329e947ed03cb4bd4834b5c79a99ca9404
MU2 299892f9e697026e1a62c62ffc3a7b75bbdfa5bbbfe24906d66af0c3ef4f4fb0
MU3 7643dd229c0bc2675bcb8b8329873b0399359038a56b2cc8571cebc1159729ed
MU4 f0a098c5fa0061f25eed8c8ad1f213eee8fe5539fbf75d46e26f392db479297f
```

Mutations are one-token edits to the scratch copy only:
- MU-1: `RECORD-MISSING         EACCES or ELOOP opening the record path: the path` / continuation
  line rewritten so `EACCES or ELOOP` lands **only on the continuation line** (the r40 subject).
- MU-2: `if exc.errno == errno.ENOENT:` → `if exc.errno in (errno.ENOENT, errno.ELOOP):`.
- MU-3: `raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)` → `…RECORD-MISSING…`
  in the ENOENT branch.
- MU-4: both class lines name both keywords (`EACCES or ELOOP or a missing path` /
  `a missing (ENOENT) or EACCES or non-regular record path`).

## 2. Commands actually run (all in scratch; no lane write)

```text
read /home/vgpnk/.omp/agent/RULES.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
git -C <lane> rev-parse --show-toplevel ; git -C <lane> log --oneline -15 ; git -C <lane> status --short
git -C <lane> show 0242085:tools/souji-worktree-drift.py | sha256sum      # e48ed08e6728…
git -C <lane> show 0242085:census/round-39/c2-counter.py    | sha256sum  # 732b1e425a6d…
git -C <lane> show ed30b7f5:tools/souji-worktree-drift.py  | sha256sum   # 14e9c0f77d7e…
git -C <lane> archive ed30b7f5 | tar -x -C <fixture2>      # base bytes
git -C <lane> archive 0242085 tools tests census | tar -x -C <fixture2>   # pristine candidate
git -C <fixture2> init -q . ; git add -A ; git commit -m "…"   # per branch, toplevel asserted first
python3 -B <scratch>/battery.py ; python3 -B <scratch>/mutants.py ; python3 -B <scratch>/mutants2.py
python3 -B <scratch>/r40leg.py ; python3 -B <scratch>/isolate.py ; python3 -B <scratch>/final.py
TMPDIR=<scratch>/tmp python3 -B <scratch>/subjects/c2-counter-r39.py \
    --root <fixture2> --rev <REV> --base-rev <BASE> --scratch <scratch>/csN
python3 -B <scratch>/counter-patchA.py | counter-patchB.py | counter-patchC.py | counter-patchD.py  (same CLI)
```

The four patched counters are **scratch copies** of the committed r39 counter with one minimal change
each; they are measurement instruments for the r40 leg design, not lane artifacts:
- **patchA** — L4 trigger match scoped to the class body:
  `def _body(e): return e[len(e.split()[0]):].lower() if e else ""`, then
  `"enoent" in _body(new_classes.get(missing,""))` and `"eacces" in _body(new_classes.get(locked,""))`.
  This is exactly the proposal already on record at `census/round-39/waves/w1/W1RevC2Doc.md:219`
  (`dc[cls][len(cls):].lower()`).
- **patchB** — patchA **plus** `classify()` parsing the `REFUSAL <CLASS>:` prefix before the
  substring fallback.
- **patchC** — unmodified r39 counter, but the two probe paths are renamed to carry a class token
  (`RECORD-MISSING-absent.tsv`, `RECORD-MISSING-record-probe.tsv`) — the F2 experiment.
- **patchD** — patchB **plus** the contaminated probe paths — the F2-experiment control.

## 3. The runtime side: observed classes, and F2 (path-derived attribution)

Probe battery against the committed pristine bytes (fixture PRIS), 12 probes, each a fresh
`--record` path under `<scratch>/probe*/`, `--root` a plain directory:

```
ENOENT                           raised=RECORD-MALFORMED     classify=RECORD-MALFORMED
EACCES                           raised=RECORD-MISSING       classify=RECORD-MISSING
ELOOP                            raised=RECORD-MISSING       classify=RECORD-MISSING
NONREG_DIR                       raised=RECORD-MALFORMED     classify=RECORD-MALFORMED
NONREG_FIFO                      raised=RECORD-MALFORMED     classify=RECORD-MALFORMED
ENOTDIR                          raised=RECORD-MISSING       classify=RECORD-MISSING
ENAMETOOLONG                     raised=RECORD-MISSING       classify=RECORD-MISSING
RECORD-EMPTY                     raised=RECORD-EMPTY         classify=RECORD-EMPTY
RECORD-OUTSIDE-ROOT              raised=RECORD-OUTSIDE-ROOT  classify=RECORD-OUTSIDE-ROOT
ENOENT|path-has-RECORD-MISSING   raised=RECORD-MALFORMED     classify=RECORD-MISSING   <<< MISREAD
ENOENT|path-has-RECORD-MALFORMED raised=RECORD-MALFORMED     classify=RECORD-MALFORMED
EACCES|path-has-RECORD-MALFORMED raised=RECORD-MISSING       classify=RECORD-MISSING
```

**F2 is measured and reproducible.** The drift tool's refusal message embeds the record path:

```
REFUSAL RECORD-MALFORMED: <scratch>/probe4/RECORD-MISSING-absent.tsv is not a regular file
```

r39's `classify()` (`census/round-39/c2-counter.py:127-131`) scans that whole string for the first
token in `("RECORD-MISSING","RECORD-MALFORMED","RECORD-EMPTY","RECORD-OUTSIDE-ROOT")`. The path's own
`RECORD-MISSING` substring wins, so the observed class for a **malformed** record is reported as
**`RECORD-MISSING`**. Reproduced on 5 of 6 revisions (all except MU-3, where the tool really does
raise `RECORD-MISSING`, so the misread becomes invisible).

Consequence measured end-to-end with the **real committed counter** (patchC, only the probe paths
changed):

```
counter-patchC --rev=PRIS rc=0 | SUMMARY legs=6 pass=6 fail=0 harm=0
   LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
```

The leg "verifies" the wrong class entry and still passes. Under the r39 idiom this is masked by F1
(the tautology), but under a *scoped* match the same contamination flips the verdict the other way
(measured, §5): `join+scoped+r39class` on the contaminated probe → **FAIL** (a false failure caused
by the path, not by the tool). Only `join+scoped+REFUSALparse` → **PASS**.

Note the ordering dependency: patchC's `missing=RECORD-MISSING` also means the leg's `old_maps`
arm (which reads the r39 base bytes) is comparing a *different* class than intended. r39 recorded
`classify()`'s token priority (`W1RevC2Legs.md:313-316`) but not that the counter's own probe path
is inside the scanned text.

## 4. The docstring side: F1 — the trigger match is tautological

Committed pristine bytes, r39 `docstring_classes` (first line per class):

```
RECORD-MISSING   -> 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path'
RECORD-MALFORMED -> 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
```

Continuation-joined (the r40 subject):

```
RECORD-MISSING   -> 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
RECORD-MALFORMED -> 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line that does not match the schema, a duplicated name, or a TOTAL row that disagrees'
```

The r39 L4 predicate is
`missing in new_classes and "missing" in new_classes.get(missing,"").lower() and locked in new_classes and "EACCES" in new_classes.get(locked,"")`.
When the observed class for a **missing** path is `RECORD-MISSING`, the second conjunct
`"missing" in …` is satisfied **by the class token itself**:

```
PRIS   ENOENT probe -> REFUSAL prefix=RECORD-MALFORMED   r39 classify=RECORD-MALFORMED
       RECORD-MISSING entry = 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path …'
       r39 idiom  : 'missing' in entry -> True   <-- satisfied by the CLASS TOKEN
       scoped     : 'missing' in body  -> False
```

This is the r39-recorded F3 (`census/round-39/waves/w1/W1RevC2Harm.md:153,280`: "`'missing'` in
line.lower(): True (satisfied only by the class token)"; "L4's `new_maps=True` is vacuous for the
MALFORMED side"). My contribution is the **mutation consequence**, which no committed r39 artifact
records.

## 5. Mutation results: what each leg variant kills

Leg variants, all evaluated on the **same** probe set and the **same** bytes:

| variant | analyzer | trigger match | observed class from |
|---|---|---|---|
| `L4-r39` | one line per class (r39 `docstring_classes`) | case-insensitive substring over the whole entry | r39 `classify()` scan |
| `L4-r40a` | join continuations | **r39 substring match** | r39 `classify()` scan |
| `L4-r40b` | join continuations | class-scoped, token-stripped, word-boundary | r39 `classify()` scan |
| `L4-r40c` | join continuations | class-scoped, token-stripped, word-boundary | `REFUSAL <CLASS>:` prefix parse |

Verdicts (probe set in parentheses):

```
PRISTINE  r39-2probe(ENOENT,EACCES)  L4-r39=PASS  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
PRISTINE  r39+ELOOP                  L4-r39=PASS  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
PRISTINE  extended-5(+NONREG,ENOTDIR)L4-r39=FAIL  L4-r40a=FAIL  L4-r40b=FAIL  L4-r40c=FAIL
MU1       r39-2probe                 L4-r39=FAIL  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
MU1       r39+ELOOP                  L4-r39=FAIL  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
MU2       r39-2probe                 L4-r39=PASS  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
MU2       r39+ELOOP                  L4-r39=FAIL  L4-r40a=FAIL  L4-r40b=FAIL  L4-r40c=FAIL
MU3       r39-2probe                 L4-r39=PASS  L4-r40a=PASS  L4-r40b=FAIL  L4-r40c=FAIL
MU3       r39+ELOOP                  L4-r39=PASS  L4-r40a=PASS  L4-r40b=FAIL  L4-r40c=FAIL
MU4       r39-2probe                 L4-r39=PASS  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
MU4       r39+ELOOP                  L4-r39=PASS  L4-r40a=PASS  L4-r40b=PASS  L4-r40c=PASS
```

Reading:

- **MU-1 (the r40 subject) is the discriminator that works.** The r39 one-line analyzer misses the
  wrapped trigger (`new_maps=False`), every joining analyzer detects it. This is the prereg's
  "synthetic wrapped-trigger probe is detected while the r39 one-line analyzer misses it" — **the
  join is a real and necessary capability**, and MU-1 is a concrete instance of it.
- **MU-3 is the falsifier of the join-only reading.** A join-only r40 leg (`L4-r40a`) **PASSES** a
  mutant whose observed class mapping is inverted (ENOENT now raises `RECORD-MISSING` while the
  docstring says `RECORD-MALFORMED` is "a missing (ENOENT)"). The prereg's kill rule — "Kill if …
  any observed class mapping disagrees with runtime behavior" — is therefore **not reachable** by a
  join-only leg. Only a class-scoped, token-stripped match (`L4-r40b`/`L4-r40c`) kills MU-3.
- **MU-2 (ELOOP → `RECORD-MALFORMED`) is killed only by adding the ELOOP probe.** With the r39
  two-probe set every variant passes it; with `ELOOP` added every variant fails it. So the frozen
  list's *membership* (which probes) is load-bearing, not just the analyzer's join.
- **MU-4 (inverted pair, both lines name both keywords) survives every variant**, including the
  scoped ones. A per-class directional check cannot see it; only a **bijective** check can — the
  trigger word must not also appear in the *other* class's entry. Measured:

```
C. bijective leg (isolate.py)
  PRIS   directional=PASS  bijective=PASS
  MU3    directional=FAIL  bijective=FAIL
  MU4    directional=PASS  bijective=FAIL
        ENOENT  observed=RECORD-MALFORMED  names=True  other-classes-holding-trigger=['RECORD-MISSING']
        EACCES  observed=RECORD-MISSING    names=True  other-classes-holding-trigger=['RECORD-MALFORMED']
```

  This is r39's recorded DIVERGENCE D4 (`census/round-39/waves/w1/W1RevFreeze.md:193`: "an inverted
  pair naming both keywords passes"), which I reproduce as a mutant rather than a reading.

## 6. The real committed counter, all five revisions

Committed `census/round-39/c2-counter.py` bytes, real CLI, scratch fixture:

```
counter=c2-counter-r39 (committed r39 bytes)
  PRIS rc=0 | SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728
      LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
  MU1   rc=1 | SUMMARY legs=6 pass=5 fail=1 harm=0
      LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
  MU2   rc=0 | SUMMARY legs=6 pass=6 fail=0 harm=0      <-- ELOOP mutant SURVIVES the whole counter
      LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
  MU3   rc=1 | SUMMARY legs=6 pass=5 fail=1 harm=1
      LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False  <-- L4 BLIND
      LEG L6  FAIL r38-drift-record=9/10(base 10/10)                                          <-- caught by L6, not L4
  MU4   rc=0 | SUMMARY legs=6 pass=6 fail=0 harm=0      <-- inverted pair SURVIVES the whole counter
      LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False

counter=counter-patchA (r39 + class-scoped trigger match)
  PRIS rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS … new_maps=True old_maps=False
  MU1   rc=1 | pass=5 fail=1 harm=0 | LEG L4 FAIL … new_maps=False old_maps=False
  MU2   rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS … new_maps=True old_maps=False
  MU3   rc=1 | pass=4 fail=2 harm=1 | LEG L4 FAIL missing=RECORD-MISSING locked=RECORD-MISSING new_maps=False old_maps=False  <-- KILLED
  MU4   rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS …                                          <-- still survives

counter=counter-patchB (patchA + REFUSAL-prefix class parse)
  PRIS rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING
  MU1   rc=1 | pass=5 fail=1 harm=0 | LEG L4 FAIL …
  MU2   rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS …
  MU3   rc=1 | pass=4 fail=2 harm=1 | LEG L4 FAIL missing=RECORD-MISSING … new_maps=False        <-- KILLED
  MU4   rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS …                                          <-- still survives

counter=counter-patchC (r39 idiom, class token in the probe path)
  PRIS rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
                                                                                              <-- verifies the WRONG class, passes

counter=counter-patchD (patchB + class token in the probe path)
  PRIS rc=0 | pass=6 fail=0 harm=0 | LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
                                                                                              <-- contamination neutralised
  MU3   rc=1 | pass=4 fail=2 harm=1 | LEG L4 FAIL missing=RECORD-MISSING … new_maps=False
```

**MU-2 and MU-4 survive the entire committed r39 counter** (`rc=0`, `pass=6 fail=0 harm=0`). That is
the pre-existing r39 gap (harm mutant S1 and DIVERGENCE D4), not new — but it sets the bar the r40
leg must clear, and it means the r40 leg's kill rule must cover **both** the probe-set membership
(MU-2 needs the ELOOP probe) and the bijectivity of the mapping (MU-4 needs a cross-class
exclusion), in addition to the continuation join (MU-1) and the trigger scoping (MU-3).

## 7. A structural hazard in reusing the r39 `new_ok and not old_ok` shape

The r39 L4 verdict is `new_ok and not old_ok` — a **difference** between the candidate's and the
base's docstring maps. That shape requires the base to be *worse*. Measured on the same byte pairs
with only the `--rev`/`--base-rev` labels swapped:

```
--rev=PRIS --base-rev=MU1  -> LEG L4 PASS  new_maps=True  old_maps=False
--rev=MU1  --base-rev=PRIS -> LEG L4 FAIL  new_maps=False old_maps=True
--rev=PRIS --base-rev=PRIS  -> LEG L4 FAIL  new_maps=True  old_maps=True
```

The leg's verdict flips with the *labels*, not with the bytes. For the r40 claim this matters: a
pristine candidate and a wrapped candidate (MU-1) both satisfy "the class is documented", but only
MU-1 satisfies "the base did not document it". An r40 leg that reuses `new_ok and not old_ok` will
therefore need a *synthetic* base whose docstring lacks the trigger, not the r39 base revision — the
prereg's phrase "a synthetic wrapped-trigger probe" is doing exactly this work, and it must be
synthetic in the **docstring**, not only in the file layout.

## 8. Bounded measurement plan for the r40 leg (concrete, executable)

At the candidate revision, the r40 C2 leg must satisfy **all** of the following, or the frozen kill
rule is not reachable:

1. **Join** continuation lines into one class entry — *necessary* (kills MU-1 blind) but not
   *sufficient*.
2. **Scope** the trigger match to the class body, class token stripped, word-boundary matched
   (`dc[cls][len(cls):]`, already on record at `W1RevC2Doc.md:219`) — otherwise the MALFORMED-side
   check is a tautology and MU-3 survives (kills MU-3).
3. **Derive** the observed class from the tool's `REFUSAL <CLASS>:` prefix, not from a substring
   scan of stdout+stderr — otherwise the probe path can set the class (kills F2 / patchC).
4. **Probe every trigger in the frozen list**, including `ELOOP` and the non-regular case — otherwise
   MU-2 survives (kills MU-2).
5. **Check bijectivity**: a trigger word must not appear in the *other* class's entry — otherwise
   MU-4 survives (kills MU-4).
6. **Use a synthetic docstring base** for the `not old_ok` arm, or replace the differential shape
   with an absolute predicate — otherwise the verdict depends on revision labelling (§7).

Acceptance for the r40 leg, as mutants on the committed bytes (all five already built and hashed
above):

| mutant | must be killed by the r40 leg | killed by |
|---|---|---|
| MU-1 wrapped trigger | YES | join (any variant) |
| MU-2 ELOOP → MALFORMED | YES | ELOOP probe in the frozen list |
| MU-3 ENOENT → MISSING | YES | class-scoped trigger match |
| MU-4 inverted pair | YES | bijective cross-class exclusion |
| pristine | MUST PASS | — |
| r39 base bytes | MUST FAIL | — |

## 9. Claims I did **not** test, and limits

- **I did not execute an r40 counter.** No r40 candidate bytes exist in the lane
  (`census/round-40/` contains only `preregistration.txt`; the lane has no r40 counter or fixture).
  Every "r40 leg" verdict above is a verdict of **my scratch prototype** on **committed r39 bytes**,
  labelled `L4-r40a/b/c`. These are measurements of what the leg *shape* does, not of any candidate.
- **I did not verify the frozen list's membership.** The prereg does not enumerate it
  (`census/round-40/preregistration.txt:8` says "the frozen list" only). I show which probe sets
  kill which mutants; I do not decide the list.
- `ENOTDIR` and `ENAMETOOLONG` raise `RECORD-MISSING` and occur nowhere in the docstring, so the
  pristine bytes **FAIL** any leg that requires those triggers to be named
  (`extended-5`/`extended-6` → FAIL on PRISTINE). This is r39's recorded F2
  (`census/round-39/waves/w1/W1RevC2Harm.md:172`) and is also `R40scout41`'s edge; I reproduce it as
  a probe-set measurement and draw no separate claim from it.
- The r39 counter's other legs (L1, L2, L3, L5, L6) are outside C2 and I did not attack them; L6's
  contribution to MU-3 is noted because it is the only place MU-3 currently dies.
- All measurements are on this host (Linux, `Python 3.14.8`, `git 2.56.0`, uid 1000 non-root, so
  the mode-000 EACCES probe behaves as intended). The EACCES probe depends on the file being
  unreadable by the running uid; a root run would change it.

## 10. Restoration / cleanliness evidence

- The lane was never written: `git -C <lane> status --short` → `?? census/round-40/` only (that
  directory is the pre-existing untracked preregistration, not mine); `git -C <lane> diff --stat HEAD`
  → empty; lane HEAD unchanged at `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`.
- All mutations were applied to copies under `<scratch>/subjects`, `<scratch>/work`,
  `<scratch>/tmp` and to branches of the scratch fixture repo. The pristine subject bytes were
  re-hashed after every mutation batch:
  `pristine drift-base.py sha256 after all mutations = e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`
  `= before` (printed `equal = True`).
- The scratch fixture is disposable by construction (it is a scratch repo under
  `/fast/scratch/hyaku/souji-r40/R40mutationtester20/`), and the whole scratch tree was removed
  before yield.

## 11. Verdict

**C2 operability: the frozen claim is not falsified, but it is under-specified, and the join it
names is not the load-bearing part of the fix.** A join-only r40 leg — exactly the change the
preregistration describes — passes a single-token class swap (MU-3) whose observed class mapping
disagrees with runtime behaviour, which is the prereg's own kill condition. The mutation evidence
also shows that MU-2 (ELOOP) and MU-4 (inverted pair) survive the entire committed r39 counter, so
the r40 leg must add probe-set coverage and cross-class bijectivity, not only the continuation join.

The concrete falsifier for the r40 leg is: **apply MU-3 to the committed tool bytes, run the r40
counter, and require `LEG L4` (or its r40 equivalent) to FAIL. Any r40 leg that PASSES MU-3
satisfies the join sentence but not the kill sentence, and is therefore not the leg the
preregistration froze.** The patchA/patchB measurement shows the repair is two lines in the
counter's own helpers and kills MU-3 while keeping pristine green (`pass=6 fail=0 harm=0`).
