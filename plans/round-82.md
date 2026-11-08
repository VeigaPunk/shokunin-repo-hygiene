# Round 82 — amendments to the frozen claims (Amendment 59, pre-file falsification)

Written after wave `w1` settled and before the round report was filed. The frozen wording lives in
`census/round-82/preregistration.txt` and is not edited here: each amendment below records what the
wave's own adversarial artifacts falsified in that wording, and the narrower sentence the round now
puts its name to. The **numbers** are unchanged: every frozen predicate was re-derived on committed
bytes by non-author seats and by the L1 (`census/round-82/records/c1-after.txt`,
`c2-after.txt`, `c2-after-monitor.txt`; re-derivations in `.ufo/waves/round-82/w1/S82ExecC1.md`,
`S82Connector.md` §0, `S82Sentinel.md`, `S82MutTool.md`, `S82Connector2.md`, `S82MutCounter.md`).

Wave evidence root: `.ufo/waves/round-82/w1/`.

## A1 — C1: the own-tree binding runs AFTER the last-component test, not before

- **Artifact:** `.ufo/waves/round-82/w1/S82Reviewer.md` (LOW "wording/code"), independently
  `.ufo/waves/round-82/w1/S82MutCounter.md` (LOW, M08).
- **Frozen wording falsified:** "the `_owntree_ok` check runs BEFORE the basename test" (prereg
  `## C1` Grounding; repeated in the W1 code comment at `census/round-82/c1-pointer-counter.py:368`).
- **Enforced property:** the last-component equality test runs first (`c1-pointer-counter.py:349`);
  `_owntree_ok` runs at `:353`, after it and before the location-class tests. The two orders decide
  every frozen row and every regression row identically (`refused_true=0`, `mismatches=0`).
- **Amended sentence:** *the own-tree binding runs after the last-component equality test and before
  the location-class tests; the order is outcome-equivalent on the 32-row population and the five
  regression suites, and no row isolates it.*

## A2 — C1: the own-tree rule binds an identity path and one capture shape, not "the own round tree"

- **Artifact:** `.ufo/waves/round-82/w1/S82Connector2.md` F1 (MEDIUM), re-derived by the L1
  (`_owntree_ok` truth table, this round's log).
- **Frozen wording falsified:** "the token's own round tree is bound by the same subtree+full-suffix
  rule". `CAPTURE` accepts `waves/|wave/|records/wave-<w>/` only, and the lane's real wave
  directories are `w1` (65), `w2` (19), `w3`, `a2w1`, `records/` — **none** named `waves/` or `wave/`.
  A genuine own-tree move `.ufo/waves/round-32/a2w1/X` → `.ufo/waves/round-32/w1/X` is therefore
  REFUSED, while the harness-planted `.ufo/waves/round-32/waves/a2w1/X` is kept. r81 accepted both.
- **Enforced property:** the own-tree binding keeps the token's identity path and a
  `waves/|wave/|records/wave-<w>/` capture shape, and refuses every other own-tree location,
  including the lane's real `wN/` directories.
- **Amended sentence:** *the own-tree binding refuses the NF-F/NF-G decoys and keeps TF4's capture
  shape; it also refuses a genuine own-tree move into a real `wN/` wave directory, a narrowing of
  r81's acceptance that no true row in the population exercises (stated limit; routed to round 83
  with the ground it needs — a real own-tree move row).*

## A3 — C1: the census-in-tree full-suffix branch is dead code for this population

- **Artifact:** `.ufo/waves/round-82/w1/S82CriticClaims.md` (MEDIUM), independently
  `.ufo/waves/round-82/w1/S82Connector.md` F2 (MEDIUM).
- **Frozen wording falsified:** the C1 paragraph's attribution of PF-1/NF-F/NF-G/NF-H to the
  full-suffix branch ("the census-subtree `_capture_ok` … runs before the last-component test;
  basename is a necessary, not sufficient condition", and the chronology line "the census branch
  keeps `_capture_ok` before the last-component test (PF-1/NF-F/NF-G/M8)"). No frozen row has a
  token under `census/`, so `c1-pointer-counter.py:365-371` never fires; replacing it with
  `elif False:` leaves `rows=32 mismatches=0 accepted=0 refused_true=0 errors=0` EXIT=0 and both
  regressions green (S82Connector F2).
- **Enforced property:** the C1 delta is delivered by `_owntree_ok` alone; PF-1's MOVED verdict is
  decided by the pre-existing `_capture_ok`, so its "shape-true" label does not discriminate.
- **Amended sentence:** *on this population the own-tree branch alone moves the counter from 2
  accepted to 0; the census-in-tree branch changes no verdict and is carried as ungrounded
  hardening (routed: ground it with a real row or delete it).*

## A4 — C1: the K-b control is the r81 counter, not a purpose-built variant (the seat's stronger conclusion is rejected)

- **Artifact:** `.ufo/waves/round-82/w1/S82Connector.md` F1 (MEDIUM).
- **Frozen wording:** "the controls stay red: K-b owntree-dropped
  (`controls/variants/c1-K-b-owntree-dropped.py`; `controls/c1-K-b-owntree-dropped.txt`: mismatches=2
  accepted=2, EXIT=1)". Its docstring's "accepted=3" is wrong (the receipt says 2) — a LOW wording
  defect the round adopts.
- **Adopted (provenance):** the variant's code is byte-identical to
  `census/round-81/c1-pointer-counter.py` (two module-docstring lines differ), so the round has one
  purpose-built C1 variant, not two.
- **Rejected (the seat's conclusion):** F1 also claims "the mutant that would isolate the round's own
  new rule is absent". That is false: the round's only new load-bearing code is the `_owntree_ok`
  branch, and removing it *yields* the r81 counter (the census-in-tree branch it also carries is dead
  code, A3) — so K-b is exactly the own-tree-removal mutant and its 2 accepted rows are the isolation
  it is accused of not providing. Provenance is thinner than the prereg implies; isolation is intact.
- **Amended sentence:** *the controls that stay red are K-a (the r81 counter, 2 accepted), K-b (the
  same bytes under the round's variant name — the own-tree-removal mutant, 2 accepted) and K-c
  (suffix→last-component, 2 accepted); only K-c is a purpose-built variant.*

## A5 — C1: the population cannot discriminate the identity clause

- **Artifact:** `.ufo/waves/round-82/w1/S82MutCounter.md` (MEDIUM, M07/NR6; LOW, M08).
- **Frozen wording falsified:** that the own-tree branch is *bound by* the subtree-plus-suffix rule
  in the strong sense the claim implies: a suffix-only own-tree variant (M07) passes all three
  committed conjuncts, and the identity disjunct is unreachable-by-verdict (M08). The 32-row
  population holds no own-tree flattened/short-suffix decoy; NR6 (`.ufo/waves/round-32/X`) is refused
  by the frozen counter but moved by M07.
- **Enforced property:** the committed rule is strong enough for the frozen rows; the extra strength
  over a suffix-only rule is unmeasured.
- **Amended sentence:** *the counter refuses NF-F/NF-G/NF-H on the frozen rows; the population cannot
  separate the identity clause from a suffix-only rule, so the identity disjunct is carried as
  unproven extra strength (routed: an own-tree flat-decoy row).*

## A6 — C2: the empty-`CLI_PID` window orphans the subtree while reporting "stopped it" — repaired in W3

- **Artifact:** `.ufo/waves/round-82/w1/S82Sentinel.md` F-1 (MEDIUM); code re-read by the L1.
- **Frozen wording falsified:** "*kills the CLI subtree* and answers a caller's signal under job
  control". W2 replaced base's `local pid=${CLI_PID:-${!:-}}` with `local pid=${CLI_PID:-}`
  (`tools/souji-vault-verify.sh:245`), so a signal that arrives between `timeout … &` (:290) and
  `CLI_PID=$!` (:291) leaves `pid` empty: no tree kill, no group kill, no `wait` — the handler prints
  `souji-vault-verify: SIG<name> ... stopped it, no verdict` and exits 143 with the CLI subtree alive.
  Measured A/B on the committed bytes: base 0/150 iterations orphaned, W2 1/150 (Sentinel `bigab4.py`);
  a slowed fork dispatches the pending TERM in that window 110/120 times; on the real tool the window
  spans 4.07 ms. The prereg's stated rationale for the removal ("`$!` … is never the timeout pid
  here") is false: `:290` is the tool's only background launch, so `$!` **is** the timeout pid there.
  The prereg's stated limits exclude "the windows before the traps arm and after `wait`"; this window
  is after the traps arm and before `wait`, so it is not excluded.
- **Repair landed (W3, `records/repair-w3/`):** R1 restores the base expression
  `local pid=${CLI_PID:-${!:-}}`; the frozen 16-row counter, the selftest, the r17 fixture and probe D
  are re-run on the repaired bytes.
- **Amended sentence:** *on the frozen 16-row population the tool kills the CLI subtree and its
  job-controlled grandchild under both launches; the empty-`CLI_PID` window that W2 opened is closed
  by repair R1 before filing, and the frozen rows do not exercise that window either way.*

## A7 — C2: the m1/m2 rows are not monitor rows; the monitor evidence is the whole-counter launch

- **Artifact:** `.ufo/waves/round-82/w1/S82MutTool.md` (MEDIUM); L1 re-read of
  `census/round-82/c2-vault-signal-counter.py:217` (`rid.startswith("m-")`).
- **Frozen wording falsified:** "`m1/m2` run with `SHELLOPTS=monitor` in the tool's environment (the
  tool's bash adopts job control …)" (prereg C2 Labels; repeated in `SKILL.md:954` and `QUALITY.md`
  Q149). The branch tests `m-`, the row ids are `m1-monitor-term-fork` / `m2-monitor-hup-fork`, so it
  never fires: under the default launch m1/m2 duplicate v7/v8 and carry no monitor.
- **Enforced property:** the launch-mode matrix is the counter's own two launches — `:216` inherits
  the caller's environment, so `env SHELLOPTS=monitor python3 …` puts job control into **every** row's
  tool environment. That is what `records/c2-after-monitor.txt` measures.
- **Amended sentence:** *the 16 rows are green under both the counter's launches; the monitor launch
  sets job control for all rows through the inherited environment, and the m1/m2 row labels do not
  add a monitor of their own — the `m-` prefix test in the counter is dead code (routed).*

## A8 — C2: the tree walk's cost and its pid-reuse window are stated limits

- **Artifacts:** `.ufo/waves/round-82/w1/S82Sentinel.md` F-2 and F-3 (MEDIUM),
  `.ufo/waves/round-82/w1/S82Connector2.md` F3 (LOW).
- **Falsified implication:** that `cli_kill_tree` kills "the whole subtree" in bounded time and
  touches only descendants. Measured: one `pgrep -P` per tree node, each a full `/proc` scan
  (0.53–0.80 s/call at 4–5 k processes, 2.15 s at 7.3 k); signal→exit 5.74 s at 12 descendants,
  9.64 s at 24 — past the counter's 5 s settle; and the snapshot→KILL gap reaches 6.11 s, so a
  recycled pid in the snapshot can be KILLed.
- **Enforced property:** the frozen rows use a stub with at most one grandchild, and no row measures
  the walk's cost or a pid-reuse collision.
- **Amended sentence:** *on the frozen rows (≤1 grandchild) the tree kill is load-bearing and
  bounded; the walk costs one `/proc` scan per node (≥12 descendants exceeds the 5 s settle) and a
  recycled pid in the snapshot can be KILLed — stated limits, routed to round 83 with the seat's
  verified remediation (one fork-free `/proc` ppid map, kill-as-discovered).*

## A9 — C2: "before = 4" is the modal value of a noisy control, and the receipt reproduces only untraced

- **Artifacts:** `.ufo/waves/round-82/w1/S82Connector2.md` F4 (LOW),
  `.ufo/waves/round-82/w1/S82Connector.md` F6 (LOW).
- **Falsified implication:** that the do-nothing baseline is a fixed 4. Five runs of the frozen K-a
  command on byte-identical base bytes gave `mismatches=1,2,4,4,4`, the surviving row moving between
  v7/v8/m1/m2. Under `strace -f -e trace=openat` the C2 receipt itself reads `mismatches=12
  orphans=11` (the trace pushes the tool past the 5 s settle).
- **Enforced property:** the candidate was 16/0/0/0 in 3/3 monitor runs and 1/1 default; the base is
  red in 5/5 runs but not always on the same rows.
- **Amended sentence:** *the before-state is "red in 5 of 5 runs, modal 4 mismatches / 4 orphans";
  the after-state is 0 in every run; every C2 receipt is untraced.*
