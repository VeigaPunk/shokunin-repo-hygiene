STATUS: DONE — C1 scope attack complete: the per-repo watchdog is the right layer, but the proposed contract has two fixable defects that keep the fleet hangable, and three disclosures are mandatory.

# Critic — C1 scope (is a per-repo watchdog a real fix?)

Seat: CriticC1Scope. Base b576341. Axis judged: operability. All line numbers are
tools/souji-census.sh at b576341.

## Verdict

**Partial / holds-with-corrections.** A per-repo bound is a *real* fix for the
claim as stated ("no single repository can hang the fleet census"), not symptom
suppression — but only because the claim is a liveness claim. The root cause
(adversarial or concurrent mutation of repo metadata making *some* open(2)
block) is outside the tool's authority: git performs opens the census cannot
pre-approve, and every check-then-open guard is itself inside the race window.
Nothing the tool does can *prevent* the block; it can only bound the blast
radius. Suppression would be: swallowing the hang silently, or bounding and
reporting the repo as measured. The contract does neither — the timed-out repo
gets an `error` row (zeros explicitly marked non-measurement, same convention as
the existing degraded rows at :1266/:1281) plus a distinct stderr marker. The
symptom stays visible; the *harm* (fleet hang) is removed. That is the correct
layer for an operability claim.

But the fix as specified does **not** yet close the class. Two defects below
are counterexamples that leave the fleet hangable under the exact same shim
L1 already built.

## The class, precisely

Class to close: *any blocking syscall anywhere in the per-repo attempt* —
including bash builtins (`read < fifo` blocks identically to `open`), external
commands (git, tr, find, du), and pipelines. Blocking opens reachable today:

- `tr -d '\000' < "$cfg"` at :695 and `git config --file "$cfg"` at :698/:701 —
  inside `scan_config_file`, run for **every include.target** the recursion
  visits (:714-718). A raced include path blocks here.
- `IFS= read -r line < "$file"` — gitfile_admin :820, commondir reads
  :880/:923/:965, alternates :505/:515 — all plain blocking opens by the shell.
- Every git subprocess: config is parsed on *every* git command, so a raced
  include/config FIFO blocks `rev-parse`, `worktree list`, `ls-files`,
  `check-attr`, `status`, `rev-list`, `for-each-ref` — not just `status`.
  Direct local proof: census/round-18/leaked-procs-before-1631.txt lines
  2,4,6,22,24,26,28,30 show `/usr/bin/git ... rev-parse --is-inside-work-tree`
  blocked for hours on `r-inc-fifo` fixtures — `rev-parse` never opens
  info/attributes; the blocked open is in config/include parsing.

## Alternative comparison

| Alternative | Closes the class? | Cost | Verdict |
|---|---|---|---|
| Bound each git call with `timeout` | **No.** Misses every non-git blocking point: `tr < cfg` :695, `read < file` :820, `find`/`du` (:1162/:1144) on a hung FS, `mapfile` on a FIFO'd pipe source. Also fails the budget: `guard_bound_filters` + `worktree_extra_flags` + measurement issue ≥10 git calls per repo (:1069,:1085,:1090,:1000,:1006,:1010,:1014,:1027,:1122,:1253), each N×bound, and an adversary can re-block on every call — N hangs per repo, not one. Exit-code ambiguity (child's own 124/137 vs timeout's) needs a marker anyway. | Looks simpler; actually requires wrapping a moving target set of call sites | Reject |
| `O_NONBLOCK` open-check before git | **No.** TOCTOU is the attack itself: the shim swaps *after* the check, exactly as it already swaps after `stat -L` at :555. An O_NONBLOCK probe is just another check in the same race window; holding the FIFO open O_RDWR doesn't help (git's own open then succeeds but read(2) blocks forever on a writer-less, reader-held pipe). | ~free, buys nothing | Reject |
| Private attributes via `core.attributesFile` | **No, dead on arrival.** (a) git reads `$GIT_DIR/info/attributes` *unconditionally* — `core.attributesFile` only *replaces the per-user file*, it does not stop the info/attributes read. Local proof: `count_dirty` already passes `-c core.attributesFile="$at"` at :1124 (and `/dev/null` is the sanctioned empty value), yet the r17 d2-fifo repro still blocks in `status`. (b) Producing the "private copy" is itself a blocking open of the very file being attacked. (c) It covers only one of many unconditional opens — the observed rev-parse block is in config parsing, untouched by this knob. | Non-functional | Reject |
| Refuse repos whose metadata changed guard→use | **No.** Detection ≠ prevention: re-stat narrows the window, never closes it — the swap lands between the re-stat and git's internal open, same as it lands between :555 and the open today. Also harms calibration: a repo under legitimate concurrent churn (a `git gc` mid-census rewriting packed-refs/index) flaps between "refused" and measured across runs. | Cheap to add, adds a finding class, closes nothing | Reject as fix; OPTIONAL as a diagnostic finding, adds nothing to the invariant |
| Private `.git` copy / mount namespace | Heavy, still racy (the copy reads the raced files), and a namespace/remount strains "never writes" at :9. | Worst | Reject |
| **Per-repo process group + watchdog (proposed)** | **Yes — the only option that covers the whole class** (builtins, pipelines, subprocesses, guard *and* measurement, present and future blocking points). Group SIGTERM+SIGKILL reaches everything in the region. | Medium complexity; correctness hinges on reap semantics (D2 below) | **Keep, with corrections** |

A simpler implementation of the same mechanism — `timeout -k 2 N setsid bash -c '…'` — cannot wrap `census_one` (a shell function; would need re-exec) and, critically, `timeout(1)` blocks in waitpid after its own kill, so it inherits defect D2. The hand-rolled `set -m` watchdog in the contract is the right shape; `timeout` is not a strict improvement.

## Fixable defects in the proposed fix

**D1 — The bound does not cover the listing phase; the fleet still hangs before any `census_one` runs.**
`list_repos` performs opening work unbounded, outside the per-repo region the
contract wraps: `guard_git_surface` at :1352/:1355/:1385 (→ `scan_config_file` →
`tr < "$cfg"` :695 and `git config --file` :698, plus commondir/alternates
`read` builtins :880/:923/:965/:505) and `guard_git_pointer` at :1381
(→ `gitfile_admin` `read < "$g"` :820, :943). The same shim that swaps
info/attributes on the `status` call can swap an include target or the `.git`
file on the *listing* pass — `emit_census` (:1400) blocks inside `list_repos`
before the bounded row loop starts, and L1's reproducer stands.
*Smallest safe correction:* bound the whole per-repo attempt — either run
`list_repos` itself inside the same watchdog mechanism (one bound, distinct
stderr `souji-census: list-timeout`, exit 1 on expiry), or strip `list_repos`
to lstat/glob only and move every open into the bounded `census_one` (the
gitfile `continue` at :1381 needs its guard deferred into a bounded helper —
its exit-2 protected semantics survive because `census_one` already exits 2
through `emit_census` :1407).

**D2 — Unbounded reap reintroduces the hang and violates "the watchdog never outlives its repo."**
After SIGKILL, a child in uninterruptible sleep (dead FUSE/NFS mount under the
repo — exactly the failure shape this fleet guards against, see the deleted-/var/tmp
residue this round is about) cannot die; a plain `wait`/`wait -n` on the region
blocks forever → the watchdog outlives the bound, `emit_census` blocks on the
`wait`, outer `timeout 15` → rc 124 again, neighbours' rows lost. The bound
kills the *blocker* but the run still hangs on the *reap*.
*Smallest safe correction:* bound the reap — after KILL, poll `kill -0`/`wait -n`
for a short grace (a few seconds), then stop waiting regardless, emit the error
row, and continue. The leftover D-state/zombie process is residue: disclosed
(see below) and detectable by the new C3 proc census — a clean cross-claim
handoff. Note `timeout(1)` has the identical waitpid-after-kill hole, so it
cannot replace this mechanism.

**D3 — Classification and capture details that silently corrupt semantics if done the easy way.**
- Timeout must be detected by a **watchdog-set marker**, never by exit status:
  a `census_one` that dies at 124/137 for its own reasons (OOM-KILL, nested
  timeout) must not be labeled `repo-timeout`, and a timed-out region's 143/137
  must not be misread as a generic failure (contract requires exit 0 for
  timeouts vs exit 1 for other nonzero).
- The private temp-file stdout in the contract is **load-bearing, keep it**:
  `row=$(census_one ...)` at :1403 would still hang forever on a leaked
  setsid-escapee grandchild holding the capture pipe open — the pipe closes
  only when *all* writers die, and the group kill cannot reach an escaped
  session. Same for stderr inheritance by the watchdog/region.
- Validate the temp file contains exactly one well-formed row before adopting
  it: a region killed mid-`printf` (:1338) or a leaked writer appends a partial
  row, which would corrupt the TSV shape load_census depends on.
- Watchdog orphans: if `emit_census` exits early (exit 2 on a later repo, or a
  signal), a still-sleeping watchdog `sleep N` is orphaned residue — precisely
  what the C3 census then counts against the lane. Reap outstanding watchdogs
  on every exit path, or have the watchdog poll its parent's liveness.
- `set -m` in the non-interactive script may emit job-status notices on the
  script's stderr around each killed job; harmless but noisy — an
  implementation detail to verify, not a blocker.

## Mandatory disclosures for the report/LOG

1. **The bound converts hang → not-measured.** The `error` row's numeric fields
   are placeholders, not measurements (same contract as the existing degraded
   rows at :1266/:1281). In the TSV the timed-out row is *indistinguishable*
   from a guard-soft `error` row — only the stderr `repo-timeout` marker
   differentiates. A `--compare` run sees a flapping `error`↔measured diff that
   means "the bound fired", not "the repo changed". This tradeoff must be
   stated, not implied.
2. **The bound is per-repo; the fleet worst case is Σ bounds, not one bound.**
   N adversarial/slow repos serialize to N×600 s at the default — the run can
   still take hours. The claim is "no *single* repo hangs the fleet"; slowness
   at just-under-bound per repo is an accepted residual, not a hang.
3. **Two residues the bound cannot remove:** a setsid-escapee grandchild and a
   post-KILL uninterruptible child remain blocked processes after the run
   (the second is *new* residue the watchdog itself can create). Both are
   exactly what the C3 proc census is for — disclose that C1 bounds the
   *census's* liveness, not the process table's cleanliness.
4. **Guard reads are themselves in the race window.** Every `stat -L`/`read`/`tr`
   the guards perform (:555,:695,:820) can be the blocking open under an
   adversary that swaps after the check; the bound, not the guard, is what makes
   this safe. The fix's story must not claim the guards now prevent the opens.

## What would make this symptom suppression (it currently isn't)

- Emitting the error row without the stderr marker (silences the conversion).
- Labeling a timeout by exit status (mislabels real failures — see D3).
- Reaping unboundedly (converts "hang in the open" to "hang in the wait" — D2).
- Bounding only `census_one` while leaving listing-phase opens unbounded (D1).

## Smallest safe correction (summary)

Keep the proposed mechanism; extend the bounded region to cover all per-repo
opening work including `list_repos`'s guard calls (D1); bound the post-KILL
reap with a grace then give up waiting (D2); classify timeouts by watchdog
marker and validate the temp-file row (D3); disclose the hang→not-measured
conversion, the Σ-bound worst case, and the two residual blocked-process
classes. With those, the claim "no single repository can hang the fleet census"
holds for the full open(2)-anywhere class, and the only alternatives that come
cheaper all fail to close it.

## Evidence commands run

- `read` tools/souji-census.sh :1-133, :539-603, :679-703, :1080-1341,
  :1394-1433 — located every open(2) surface and the emit_census row loop.
- `grep` census_one|emit_census|timeout|set -m|killpg and git -C|git config|
  include\.path and read -r|< "\$ — enumerated all git calls, config-include
  recursion, and shell-builtin file reads.
- `read` census/round-18/leaked-procs-before-1631.txt :1-43 — observed blocked
  `git rev-parse` (config/include open, not attributes) and `git status`
  children under fixture census runs, ppid 1497 harness still alive.
- `read` tests/fixtures listing — confirmed fixture harness files named in the
  goal exist (r15-census-config.py, r17-census-hygiene.py).

No tools installed; no commands run against the live fleet; no writes outside
this report.
