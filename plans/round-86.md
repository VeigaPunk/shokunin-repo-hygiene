# Round 86 — amendments to the frozen claims (pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-86/preregistration.txt`
(commit `d77b42589ea77a27e0050e3bdc86ab5450baccd2`, F) and is not edited here: each amendment records what the
round's own artifacts falsified in that wording, and the narrower sentence the round now puts its name to. Numbers
are re-derived on committed bytes by non-author seats and by the L1; records under `census/round-86/records/` and the
wave's reports under `.ufo/waves/round-86/w1/`.

Wave evidence root: `.ufo/waves/round-86/w1/`.

## A0 — instrument corrections, before or during data (not amendments to a claim)

- **A0.1 — the C2 control had no writer beside it, so every row failed closed.** The first before-arm run of
  `census/round-86/c2-k4-counter.py` on `census/round-86/controls/c2-before-base-tool.py` read
  `mismatches=7` with every row `k4rows=['.|stat-cache-concealed']` and the detail
  `the receipt writer is not beside this tool`: `truth_refusal` resolves the writer beside the tool's realpath, and
  the control lives in `census/round-86/controls/`. Fixed before any after-arm byte existed: a byte-identical copy of
  the committed writer (`70bbf1c2…`) sits beside the control, the counter now prints the writer's path and sha256 in
  its header so the binding is visible, and the re-run reads the intended `mismatches=2`
  (`census/round-86/controls/c2-before-base-tool.txt`). The earlier 7-mismatch run is disclosed, not filed.
- **A0.2 — the counter's first row class was wrong.** The first after-arm run classed KF1–KF3
  `index-flag-concealed` because the predicate was `msg.startswith("RECEIPT-")`; the truth class is itself
  `RECEIPT-WORKTREE-STAT-CONCEALED`. Corrected before the filed receipt to the two flag-sweep classes
  (`RECEIPT-GITLINK-CONCEALED`, `RECEIPT-INDEX-*`), so the seven r85 rows keep their r85 class names
  (`records/c2-after.txt` was re-filed after the fix; no claim byte changed).

## A1 — C2: a flagged regular file is refused by the truth check first, so "reported as index-flag-concealed" is narrowed

- **Artifact:** `.ufo/waves/round-86/w1/S86ExecK4.md` § 2(e): an `--assume-unchanged` regular file whose bytes changed
  and whose index stat was rewritten is refused with class `stat-cache-concealed` (`RECEIPT-WORKTREE-STAT-CONCEALED`),
  not `index-flag-concealed`; the flag row fires only for records the byte-truth check passes (a gitlink, an
  unmerged entry, a flagged file whose bytes still match).
- **Frozen wording falsified:** "any record whose tag is not `H` is refused through the writer's own `_flag_refusal`,
  reported as `K4 . index-flag-concealed`".
- **Amended sentence:** *a non-`H` index record is refused through `_truth_refusal` or `_flag_refusal`, whichever
  fires first: a flagged regular file with changed bytes reports `stat-cache-concealed`, a gitlink, an unmerged entry
  or a flagged unchanged file reports `index-flag-concealed` with the writer's own class text.*

## A2 — C2: the sweep sees a concealed gitlink ENTRY, not the commit's movement

- **Artifact:** `.ufo/waves/round-86/w1/S86Critic.md` § C2-b and `.ufo/waves/round-86/w1/S86ExecK4.md` § 3(h):
  `_flag_refusal` classes the entry from the index mode (160000) plus the flag; the sweep never reads the nested
  repository, and the same row fires for a flagged gitlink whose nested HEAD never moved (§ 2(m), § 2(k)).
- **Frozen wording falsified:** the limits sentence "the row proves the flag sweep sees a concealed gitlink commit".
- **Amended sentence:** *KG1 proves the flag sweep reads a gitlink ENTRY carrying a non-`H` flag and classes it
  `RECEIPT-GITLINK-CONCEALED`; it does not prove the sweep reads submodule state, and a flagged gitlink whose nested
  working directory never moved is refused by the same row.*

## A3 — C1: each new row binds ONE arm of the clause it names, not the whole clause

- **Artifact:** `.ufo/waves/round-86/w1/S86Critic.md` § C1-c: NF-Y's `got` has two components, so only the
  `len(want) < 2` arm of `if len(want) < 2 or len(got) < 2` is exercised (`len(got) < 2` is never reached by any
  pinned row); NF-W's target is a `w[0-9]+/` shape, so the `_capture_ok` suffix rule is exercised only for that shape
  — a counter narrowing `OWNTREE_WAVE` inside the census branch still scores 8/8.
- **Frozen wording falsified:** "this round adds one row per clause … and two frozen mutants that drop exactly those
  clauses" read as clause-level certification.
- **Amended sentence:** *NF-W binds the census-in-tree refusal for a wave-directory target under the token's own
  round, and NF-Y binds the `len(want) < 2` arm of the own-tree short-shape guard; the `len(got) < 2` arm is DEAD
  (measured below), the non-wave shapes under the census root and the rest of the branch's `_capture_ok` surface
  stay unrowed.*
- **Second measurement (this round, `census/round-86/records/a6-len-got.txt`):** a mutant replacing
  `if len(want) < 2 or len(got) < 2:` with `if len(want) < 2:` survives BOTH pinned populations
  (`killed_r85=0 killed_r86=0`, both pristine arms green). It is dead by construction, not merely unrowed: with
  `len(got) < 2` the expression reaches `_capture_ok` (whose `CAPTURE` needs a non-empty remainder, so the target
  needs at least two components) and `OWNTREE_WAVE.match(tt + "/")` followed by `got[1:] == want[1:]` (where
  `want[1:]` is non-empty because `len(want) >= 2`), so no (token, target) pair can flip. The connector's proposed
  `NF-Z` row (S86Connector §5) cannot bind it either: NF-Z's shape is refused by the wave-shape requirement after
  the guard. Disposition: dead clause, deleted or documented as a belt next round, never counted as coverage.

## A4 — C2: the lane's own record-agreement run is not green for K3, and never was

- **Artifact:** `.ufo/waves/round-86/w1/S86ExecK4.md` § 4: on a `--shared` clone at the frozen revision the tool
  reports `MISMATCH K3 corpus/README.md:1017 tally-disagree 3 refused != receipt 0 refused`, byte-identical under the
  base tool and the repaired tool. The cause is a prose misparse of r73's "FX1-FX3 refused" in `corpus/README.md`
  against the r22 tally, not the repair.
- **Frozen wording falsified:** nothing in C2 — the claim is about K4 and record paths. Recorded so no reader takes
  the round as "record-agreement is green"; the K3 row is pre-existing (r85 spot-check D3) and routed, not repaired.
- **Amended sentence:** *the repaired tool's K4 emits no row on the lane's own clean tree (the kill-rule clause); the
  tool's K3 still reports the inherited r73/r22 tally disagreement on `corpus/README.md:1017`, unchanged by this
  round and routed.*

## A5 — C2: the `FLAGFAIL` branch is not the corrupt-index row

- **Artifact:** `.ufo/waves/round-86/w1/S86ExecK4.md` § 2(c): a truncated `.git/index` makes K4's own
  `git status --porcelain` fail first and reports `K4 . status-failed`; the writer's `git ls-files -v` read never
  runs, so the `FLAGFAIL` message is unreachable for an index that is corrupt enough to break status.
- **Frozen wording falsified:** none (the prereg does not claim a corrupt-index row); recorded so the branch is not
  cited as protection.
- **Amended sentence:** *the sweep's read-failure branch fires only when the index is readable enough for K4's status
  read and not for the flag read; a fully corrupt index is refused by the pre-existing `status-failed` row.*

## A6 — C2: the sweep's RULE is the writer's, its LOOP is re-implemented

- **Artifact:** `.ufo/waves/round-86/w1/S86Connector.md` §4: the writer inlines its `ls-files -v -z :(top)` loop in
  `write_receipt` and exposes no reusable function, so K4's bootstrap re-implements that loop while calling the
  writer's own `git()` and `_flag_refusal()`. K4 also does not call `_witness_refusal` (filter/attribute drivers) or
  `_content_snapshot`.
- **Frozen wording falsified:** "it runs the same index-flag sweep the receipt writer runs before a receipt" read as
  one implementation.
- **Amended sentence:** *K4 re-runs the writer's flag RULE — the same command, the same `tag != H` test, the same
  `_flag_refusal` call and the same pinned `git()` environment — with the loop re-implemented in K4's bootstrap
  because the writer inlines it; the writer's `_witness_refusal` and `_content_snapshot` are not run and remain
  unmeasured by K4.*

## A7 — C2: the writer's stderr truncation hides the cause, and is routed

- **Artifact:** `.ufo/waves/round-86/w1/S86ExecK4.md` §2(b) and `S86Connector.md` §5: when the writer's embedded
  sweep raises (`AttributeError: _flag_refusal`), the parent's no-verdict message truncates the stderr to its first
  200 characters, so the operator sees `Traceback (most recent call last):` and not the exception.
- **Frozen wording falsified:** none (the claim does not cover diagnostics); recorded because the fail-closed
  message is the reader's only handle.
- **Amended sentence:** *the fail-closed message keeps the writer's first 200 stderr characters, which can cut the
  exception line; the truncation is routed to r87 (`stderr.strip()[-200:]` or the last line first), not repaired in
  this round's claims.*

## A8 — C1: NF-W binds the census-in-tree branch's PRESENCE, not its suffix test (which is dead)

- **Artifact:** `.ufo/waves/round-86/w1/S86MutCounter.md` § 5.1 and § 5.2: the single edit `x3-c7-shape-only`
  (branch kept, `not _capture_ok(...)` replaced by a capture-prefix shape test) survives both pinned populations
  (`killed_r85=0 killed_r86=0`) and agrees with the filed predicate on all 504 census path pairs the own-tree branch
  accepts; the reasoning is a two-case proof — whenever the branch is reached, `_capture_ok` is either already True
  (both predicates False) or the target's below-round path starts with a wave directory, which `CAPTURE` cannot match
  (both predicates True). The same seat's `x5-m14-guard-want-only` and this round's L1 probe
  (`census/round-86/records/a6-len-got.txt`) independently show the guard's `len(got) < 2` half is dead.
- **Frozen wording falsified:** "NF-W binds the census-in-tree refusal for a wave-directory target under the token's
  own round" read as binding the branch's suffix rule (A3's first narrowed sentence names the branch, but the branch's
  message names a suffix test the row does not exercise).
- **Amended sentence:** *NF-W binds the presence of the census-in-tree branch — its enforced rule is "an own-tree
  wave-directory shape under a census token is refused", which is what the branch decides on every input that reaches
  it — and it does not bind the branch's `_capture_ok` suffix test, which is dead on the reachable set (a code
  decision for r87, not a row).*

## A9 — C2: the record names the paths the writer lists, and the writer lists at most five

- **Artifact:** `.ufo/waves/round-86/w1/S86ExecEvade.md` § C2: six same-size stat-cache forgeries give
  `RECEIPT-WORKTREE-STAT-CONCEALED: 6 tracked path(s) … (f1-aaa.txt, …, f5-eee.txt …)` — one physical line, the
  escape holds, and the sixth path appears nowhere in the record. `_truth_refusal` caps its `names` list at five
  (`sorted(bad)[:5]` plus `…`).
- **Frozen wording falsified:** "so one K4 record stays one physical line and still names the path" — it names the
  first five paths and a count.
- **Amended sentence:** *a newline or tab in a path is C-escaped, so one K4 record stays one physical line and every
  path the writer's message lists (at most five, then an ellipsis and the count) is recoverable; a sixth forged path
  is counted but not named, the r85-carried five-path cap (F7/R86-4), unchanged and routed.*

## A10 — C1: the population leaves the round comparison's leading-zero case and the wave-dir domain unbound

- **Artifact:** `.ufo/waves/round-86/w1/S86ExecEvade.md` § C1: `mut-intround` (`tr.group(1) != kr.group(1)` ->
  `int(...) != int(...)`) scores `rows=49 mismatches=0` — not killed — while the counter resolves the false row
  `.ufo/waves/round-032/w2/…` as MOVED; and a `w0/` copy is accepted because `w[0-9]+` includes `0`, with no row
  pinning the domain either way.
- **Frozen wording falsified:** nothing in C1's sentence (the eight frozen mutants stay killed and the limits already
  say the population proves discrimination on its own rows); recorded because the calibration verdict would otherwise
  read as "the rule's round comparison and wave-dir domain are certified".
- **Amended sentence:** *the r86 population certifies the eight named mutants and the two new rows' clauses; it does
  not bind the round comparison's leading-zero case (an `int()`-normalising counter is green on all 49 rows) or the
  wave-directory domain (`w0/` is accepted), both routed to r87 as rows (`NX3`, and a `w0/` decision).*

## A11 — C2: the sweep read the writer's config view, so an environment or repo config could hide the tag (repaired in-round)

- **Artifact:** `.ufo/waves/round-86/w1/S86Sentinel.md` §2 (probes I1, F5, K1, L1) and the L1 re-probe
  `census/round-86/records/c2-env-route.txt`: `git ls-files -v` renders a skip-worktree entry as `H` whenever
  `core.sparseCheckout` is on. The tool's own `git()` strips `GIT_CONFIG_*` and pins six keys; the writer's `git()`
  (used by the r86 sweep) strips `GIT_DIR`/`GIT_WORK_TREE`/`GIT_COMMON_DIR`/`GIT_ATTR_SOURCE`/pathspec variables only
  and pins nothing about sparse checkout. So with `GIT_CONFIG_PARAMETERS="'core.sparseCheckout=true'"` (or
  `GIT_CONFIG_COUNT`, or the repository's own `core.sparseCheckout=true`) the sweep sees tag `H` for a skip-worktree
  gitlink, `_truth_refusal` skips `160000` anyway, and K4 returned a CLEAN verdict for the KG1 class — a fail-open on
  exactly the class the repair adds. The frozen 9-row counter cannot see it: its own `ENV` strips every `GIT_*`.
- **Frozen wording falsified:** "any record whose tag is not `H` is refused" is true of the code and false of the
  read: the tag a caller can choose is not the tag the index holds.
- **Repair (landed, tool sha256 `cf875367…`):** `git_env()` is factored out and its `ENV_ROUTES` now also excludes
  `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` and `GIT_REPLACE_REF_BASE`; the
  embedded writer subprocess runs with that same environment; and the sweep pins `core.sparseCheckout=false`, which
  wins over both the caller's environment and the repository's config (measured: `S` tag under
  `GIT_CONFIG_PARAMETERS` and under a repo-local `core.sparseCheckout=true`). Re-probe
  `census/round-86/records/c2-env-route.txt`: base tool `k4_rows_with_env=0` (no sweep at all), filed tool
  `k4_rows_with_env=1` naming `nest` as `RECEIPT-GITLINK-CONCEALED`.
- **Amended sentence:** *the sweep reads the index through the tool's own pinned environment and with
  `core.sparseCheckout=false`, so a caller's `GIT_CONFIG_*` environment, a caller's index/object-store redirection or
  a repository-local sparse-checkout setting cannot turn a non-`H` record into `H`; the frozen 9-row counter does not
  exercise that route (its own env strips `GIT_*`), so the route is measured by probe, not by a frozen row, and
  `core.sparseCheckout` arriving through a host-level config file outside `GIT_CONFIG_GLOBAL` remains out of scope.*
