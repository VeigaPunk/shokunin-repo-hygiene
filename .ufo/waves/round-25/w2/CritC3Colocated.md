# CritC3Colocated — attack on C3's colocated/plain predicate (souji r25 w2)

Seat: `L1Souji25.CritC3Colocated` (critic, leaf, read-only). Lane HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd`; worktree carries the W1 integration (live `tests/fixtures/r13-repo-structure.sh` is byte-identical to the W1 draft, `cmp` = IDENTICAL). No installs, no lane/lane-state mutations; scratch `/var/tmp/souji-r25-CritC3Colocated/` removed before finish. Re-ran only the bounded counter/probes in isolated scratch.

## STATUS: PASS (predicate confirmed, correctly bounded, non-vacuous; simulation is a faithful stand-in for the ref-count effect, and the real-jj shape is verified against a real jj repo)

## 1. Predicate confirmed: metric lines only, `references.others.count` strictly greater (observed 2 vs 0)

Implementation (`tests/fixtures/r13-repo-structure.sh`, colocated block lines 779-848):

- **probe.* excluded**: `grep -E '^(references|objects)\.'` on each probe output (lines 813-814); a `cmp -s` of the two sorted metric files is a hard gate (`metrics-identical`, line 817-819).
- **others strictly greater**: `parse_metrics` then `((10#$CP_COLO_OTHERS > 10#$CP_PLAIN_OTHERS))` (lines 826-831). The 2-vs-0 is the **observed instance**, not a hardcoded oracle: setup adds exactly two keep refs — `refs/jj/keep/$CP_HEAD` and `refs/jj/keep/$CP_HIDDEN` (lines 788-793) — so `others_plain=0 others_colocated=2`; the requirement itself is strict `>`, which is drift-robust.
- **rc=0 + metric difference both asserted**: `plain_rc`/`colocated_rc` must be 0 (805-806), stderr empty (807-808), gitdir manifests unchanged before/after (809-812), and the metric sets must differ.

Frozen spec verbatim (amendment 3 §3): "compare ONLY the metric lines (drop probe.*), and require `references.others.count` greater in the keep-ref clone; a do-nothing emit must not reach PASS, and the case must assert rc=0 plus the metric difference." Implementation satisfies it point-for-point.

Re-run (frozen counter, committed probe): `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` →
`id=SOUJI-R13-STRUCT-colocated-vs-plain … plain_rc=0 colocated_rc=0 others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS`, final `selftest=PASS ids=7/7` rc=0. Matches the W1 receipt (ExecC3 evidence line).

## 2. A change only to output path cannot pass — verified by mutants

Mutants (wrappers around the committed probe, run as `--probe <mutant>` in scratch):

| mutant | behaviour vs real probe | colocated case result |
|---|---|---|
| `m-path-fixed` | emits identical/static metrics for both clones, only `probe.*` path lines differ | **FAIL** `metrics-identical; others.count colocated=0 not> plain=0` |
| `m-noop` | `exit 0`, no output | **FAIL** `plain-no-metrics; colocated-no-metrics; metrics-identical; others.count unparsed` |
| `m-zero` | rewrites `references.others.count=0` in both | **FAIL** `others.count colocated=0 not> plain=0` |
| `m-one` | rewrites `references.others.count=1` in both | **FAIL** `others.count colocated=1 not> plain=1` |
| `m-stderr` | adds a stderr line | **FAIL** `plain-stderr-nonempty; colocated-stderr-nonempty` |
| `m-path` | rewrites only `probe.*` path lines, real metrics intact | colocated case **PASS** (probe.* ignored by design); whole suite **FAIL** via other cases pinning probe fields |

Conclusions:
- A **pure path-only difference can never produce PASS** (`m-path-fixed` fails: identical metrics → `metrics-identical` + `others not >`). A do-nothing emit fails (m-noop). The "path-only false green" hole is closed.
- `m-path` shows probe.* lines are *invisible* to this case by design (correct: clone paths always differ, a whole-output compare is vacuous — this is exactly scout Attack 3, resolved by amendment 3). The case only ever sees real metric content; path edits can neither cause nor mask a PASS.
- Whole-suite path fakes are additionally caught elsewhere (`object-metrics` requires `repo structure --format=lines` in `probe.command`; `linked-common-dir` pins `probe.git_dir`/`probe.repo_root`).

## 3. `refs/jj/keep/*` simulation: real jj colocation vs ref-count effect

The simulation does **not** run jj; it demonstrates the **ref-count effect** in the true jj namespace. I verified the real shape two ways:

- **This lane is a real jj-colocated repo (jj 0.45.1, per operator directive)**. `git -C souji-shokunin for-each-ref --format='%(refname)'` → 474 × `refs/jj/keep/<oid>`, 2 `remotes/origin`, 5 heads, **no other `refs/jj/*` category**. Raw baseline `git -c maintenance.auto=false repo structure --format=lines` on the lane → `references.others.count=474`, `references.branches.count=5`, rc=0. **1:1**: real colocation's entire git-ref contribution is `refs/jj/keep/*`, and `others` counts exactly that.
- **Scratch real jj repo** (`jj git init --colocate`, jj 0.45.1, 3 described commits + intermediate working-copy commits, isolated `$HOME`): refs = 9 × `refs/jj/keep/<oid>`, nothing else; probe `references.others.count=9`, `objects.commits.count=9`, rc=0, stderr empty.

So the premise "a jj-colocated repository carries `refs/jj/keep/*` refs that keep otherwise hidden commits reachable" is *verified against real jj*, and the simulation's two keep refs reproduce the exact mechanism (hidden commit kept alive by a keep ref → `others` +1, `commits` +1). What the simulation does not exercise — jj's `.jj/repo/store`, op log, bookmark export to `refs/heads`, its own gc/ref maintenance — is explicitly disclosed in fixture LIMITS (lines 137-143: "real jj-managed repositories … not exercised … the keep-ref simulation only proves that extra [refs] …") and the knowledge entry `## What this does NOT establish` ("Real jj-managed repositories: keep refs are simulated; jj's own ref writes, op log and `.jj/` store are not exercised"). The claim records a **precondition** ("a colocated figure is not interchangeable with a plain baseline"), not a proof of full jj behaviour — appropriately honest, and the causal content of the precondition is confirmed true.

## 4. Scope bounds — appropriate, with recorded residuals

- Bounded well: two `--no-hardlinks` clones of one synthetic repo; deterministic ref setup; rc/stderr/manifest checks; metrics-only differential; strict-greater oracle; red arms receipted pre-data (W1 ExecC3 m1-m5: noop, common-write, private-write, common-misreport, others-zero — all FAIL the draft, four of them false-green on the OLD committed fixture). Non-vacuity controls verified (m-noop, m-zero, m-one all FAIL).
- Residuals (disclosed, not defects):
  1. **Black-box trust**: the fixture parses the probe's stdout; a *lying* emitter printing clone-position-dependent values (e.g. plain `others=0`, colocated `others=1`) with no real refs would pass. Inherent to a counter-style fixture; the red arms bound real tool defects, not adversarial emitters (scout Attack 3 parity).
  2. **Upstream key contract**: `git repo structure` is EXPERIMENTAL and its lines key set is an upstream contract (`tools/souji-repo-structure.sh:36-42`); `others` classification is upstream-defined. A future git reclassifying keep refs would change observed values but the strict-greater oracle adapts; it cannot be pinned to 2/0 forever.
  3. **Baseline-mode tally not pinned**: prereg pins `ids=7/7` for `--probe`; amendment 3 leaves baseline unspecified (observed `ids=6/6`). Informational.
  4. `differing_keys=8` is reported but not asserted; stable across two independent runs.

## Attack log

- A1 (frozen wording "byte-comparison"): whole-output comparison is vacuous (paths always differ) — closed by amendment 3 (metrics-only + strict greater). Confirmed implemented and effective.
- A2 (do-nothing false green): killed — m-noop FAILs via no-metrics + metrics-identical.
- A3 (path-only false green): killed — m-path-fixed FAILs; path lines are excluded, not compared.
- A4 (real-jj fidelity): simulation = faithful ref-count stand-in; verified against real jj (lane 474↔474; scratch 9↔9). Full jj internals not claimed, explicitly NOT-establish.
- A5 (emitter trust): residual limitation only, already recorded by W1 scout; no predicate change proposed.

Evidence pointers: fixture lines 779-848; amendment 3 §3; ExecC3 receipt line (others 0/2, differing_keys=8); `git -C … for-each-ref` category counts; raw `git repo structure` on lane (others=474, rc=0); scratch jj repo probe (others=9, rc=0); mutant table above. All commands re-run this wave in `/var/tmp/souji-r25-CritC3Colocated/` (removed); no production writes.
