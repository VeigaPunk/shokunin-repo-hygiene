# RevengeAttrGuardIntent — why `info/attributes` entered `guard_git_files`, and what the exit-2 channel meant

STATUS: DONE — the `info/attributes` guard is a multi-seat r15 safety requirement (highest-precedence
attributes source read by `check-attr`/`status`; FIFO hang; hardlink alias into the store); its
*whole-run* blast radius is an artifact of list membership in a loop that calls `protected_fail`, not
a separately reviewed decision. r16's 0a70bef restored it after cbf688a's rewrite silently dropped
it (RevBoundFilters D2). Per-repo degrade (D2, r17) preserves the original safety goal exactly,
because the repo is skipped before any git call; it does not relax the alias refusal.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `5fa6017ddcae9f6bd4412df44765f6360cb16294`
(`census` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`). Source
inspection and read-only git only; no census/fixture execution, no writes but this report.

**Line numbers are pinned to the committed blob `5fa6017:tools/souji-census.sh`.** The worktree
drifted while this report was being written: `M tools/souji-census.sh`, sha256 `3efa9190…`, 1906
lines (committed: 1877), mtime `2026-10-20 13:42:10 -0300` — a sibling executor is landing D1/D2.
Every citation below was re-checked against `git show 5fa6017:…`; live-worktree line numbers must
not be used to contradict them.

## 1. Reconstructed contract of the guard (what "safety" means here)

`guard_git_files` (`tools/souji-census.sh:519-535`) is a **stat-only, pre-git screen** of files git
opens directly from the gitdir. Its own comment states one goal (`:517-518`): "a FIFO/device/socket
is refused rather than opened or waited on." The second goal is stated elsewhere, not in the
function: a hardlink is a path-invisible alias into the protected store, and `nlink > 1` refusal is
the documented residual mitigation for aliases (r14 `BoundaryReviewGit.md:46`, quoted as the
authority by `AttributesSafe.md:25`; the trace oracle cannot see a hardlink read —
`AttributesSafe.md:33-36`).

So the goal is not "the operator sees a loud failure". It is two invariants:

- **S1** — the census (and the git it runs) never *opens* a non-regular metadata file (a FIFO open
  blocks; a device read is unbounded).
- **S2** — the census never *reads* a hardlinked metadata file, because a path boundary cannot
  distinguish it from an alias into the protected store.

The *channel* used to enforce S1/S2 is borrowed: the loop calls `protected_fail`
(`:200-208`), which prints the namespace finding `PROTECTED_FINDING='path-protected'` (`:197`) and
exits 2 for the whole run. Nothing in the function distinguishes a namespace reach from a
file-kind/alias failure.

## 2. Evidence chain

| When | Revision | What happened | Evidence |
|---|---|---|---|
| r14 | `cc21683` | `info/attributes` **absent** from the fixed list; recorded as an acknowledged residual, "no change requested this round" | `.ufo/waves/round-14/w1/BoundaryReviewGit.md:46` (P3, residual hardlink gaps) |
| r15 u1 | `b410186` | `info/attributes` **and** `info/sparse-checkout` added, in a rewrite that also made include-target kind failures whole-run | `git show b410186:tools/souji-census.sh \| sed -n '520,524p'`; include: `:676`, `:681` |
| r15 u2 | `b410186` | Header states the class policy: "Whole-run exit 2 is reserved for protected-path reaches, ambiguous targets, non-regular include targets, hardlinked config files, and git metadata that fails the integrity checks." | `git show b410186:tools/souji-census.sh \| sed -n '106,111p'` |
| r15 u3 | `b410186` | A High finding had already rejected that policy as **false provenance** and asked for per-row `error` + its own stderr finding, naming `git-metadata-nonregular`/`-unreadable` | `.ufo/waves/round-15/w1/SpecialConfig.md:27-34` (SC-3) |
| r15 u4 | `b410186` | No wave 2 existed (`status: skipped-by-operator-wrapup`, `dispatched_seats: 0`); the round was operator-stopped and never accepted; the census **does not parse** (`syntax error near unexpected token '}'`, line 1368; sha256 `dab4122c…`) | `.ufo/waves/round-15/w2-skipped.json`; commit subject "acceptance unrun"; re-verified below |
| r16 c1 | `cbf688a` | Census rebuilt from the r14 bytes (only 54 lines differ from `cc21683`; 299 added) and the fixed list is exactly r14's seven names — both r15 additions **silently lost** | `git diff --stat cc21683 cbf688a -- tools/souji-census.sh`; `git diff cc21683 cbf688a -- tools/souji-census.sh \| grep -c info/attributes` → `0` |
| r16 w1 | `RevBoundFilters` | D2 MEDIUM: `info/attributes` is read by the guard's own `check-attr` and by `status` but never type/nlink-screened; symlink covered, FIFO and hardlink not; "minimal patch (one word at 505)" | `.ufo/waves/round-16/w1/RevBoundFilters.md:98-135` (patch `:127-129`; fixture gap `:131-134`) |
| r16 c2 | `0a70bef` | Guard re-added — one-word hunk, **no exit-semantics discussion** in the diff or commit body | `git show 0a70bef -- tools/souji-census.sh` hunk: `- for rel in … info/exclude objects/…` → `+ … info/exclude info/attributes objects/…` |
| r16 w2 | `RevCensusScanFinal` | S5: the guard calls `protected_fail` → whole fleet abort for `nlink>1`, "nothing protected is involved"; counterexample `cp -al`; supplies the exact `cfg_soft` patch and the `guard_config_file_kind` precedent | `.ufo/waves/round-16/w2/RevCensusScanFinal.md:132-159` |
| r16 w2 | `CriticC1NoHarm2` | A2: "fixable: per-repo `error` row. No git runs in that repo, so this is strictly safe"; names `info/attributes` as the one **new** whole-run trigger vs r14 | `.ufo/waves/round-16/w2/CriticC1NoHarm2.md:17`, `:26`, `:75-76`, `:138`, `:150` |
| r16 w2 | `RevCensusStatusFinal` | residual 1: `.git/info/attributes` *is* nlink-screened while other attribute targets are not — inconsistent; suggests `return 3` | `.ufo/waves/round-16/w2/RevCensusStatusFinal.md:322-326` |
| r16 close | `5fa6017` | Verifier classifies it as "the same metadata-guard class as r14's hardlinked `config`/`HEAD` guards … a safety guard, not a value-blind config refusal"; routes **D2**: "Degrade it per repo (patch in `RevCensusScanFinal.md` S5), or keep it explicitly under the L0 ruling" | `corpus/lessons/round-16-verifier-spotcheck.md:49`, `:135`; disclosed in `corpus/lessons/round-16.md:59`, `SCORECARD.md:46` |

None of the three commits carries a body (`git log -1 --format='%B'` = subject only), so no commit
cites a rationale. The chain above is reconstructed from the seat reports and headers the commits
landed.

## 3. Why it was added — two distinct reasons

**r15 (`b410186`) — six seats, one implementation list, two concerns (precedence + file kind).** The attribute source is
`$GIT_DIR/info/attributes`, which `gitattributes(5)` gives the **highest precedence** and which
`core.attributesFile=/dev/null` cannot neutralize; `check-attr` and `status` both open it. The
guard's job is to decide whether a `filter` driver is bound, so the file that decides the answer was
the one file unscreened. Seats:

- `AttributesSafe.md:22-26` (F3, "MEDIUM operability, safe to fix"): add `info/attributes`;
  acceptance P-F (`:66`) requires "the repaired guard to refuse with a stable finding".
- `RelativePaths.md:58-61` (F6): add it; `status` reads it.
- `SpecialConfig.md:36-43` (SC-4, Medium): FIFO in `.git/info/attributes` hangs `count_dirty`;
  correction "fold the checks into the single walk".
- `PlanWalk.md:118-120` (G3, OBSERVED): the fixed list misses `info/sparse-checkout`,
  `info/attributes`, …; a FIFO can hang `status` before any finding.
- `MetadataFlow.md:112`, `:128`, `:226-228`: the T4 read matrix and the FIFO/hardlink residual.
- `ConfigRepair.md:23`: the change is a one-line list entry ("added `info/attributes`,
  `info/sparse-checkout`").

No seat in this list discusses the fleet-wide blast radius of that element. The *only* seat that
discusses exit semantics for the class argues **against** it (SC-3 above).

**r16 (`0a70bef`) — coverage restoration, not a new safety decision.** `cbf688a` rebuilt the census
from the r14 baseline and the guard list reverted to r14's seven names. `RevBoundFilters` D2
observed that the "any attributes source" claim would be false and that a FIFO at the
highest-precedence source would hang the census. The fix was the one-word insertion; the exit code
came with the loop.

## 4. Intended, or artifact of reusing `protected_fail`?

**Both, at different layers — and the layer that matters for D2 is the artifact.**

- **Class layer: intended.** The r15 header (`b410186:106-111`) deliberately reserves whole-run
  exit 2 for "git metadata that fails the integrity checks", and the r15 code matched it: include
  targets that were non-regular or hardlinked also used `protected_fail` (`:676`, `:681`). So for
  the seven r14-era fixed names, whole-run refusal is a stated policy, not an accident.
- **Element layer: artifact.** `info/attributes` is one name in a `for rel in …` list whose body
  unconditionally calls `protected_fail`. Adding a name changes no decision point. Corroborating
  facts:
  1. The requesting seats asked for "refuse", "add to the list", "fold into the walk" — never for a
     fleet abort (`AttributesSafe.md:26`, `:66`; `RelativePaths.md:61`).
  2. The emitted finding is `path-protected` (`:197`), i.e. the element reports a protected-namespace
     reach although no protected path is involved. SC-3 names exactly this "false provenance" as
     the reason to split the channel.
  3. The class policy that would justify it was written in the same repair, was never executed
     (`b410186` does not parse; `bash -n` rc 2 at line 1368), never got a wave-2 review
     (`w2-skipped.json`), and was never accepted (commit subject: "acceptance unrun").
  4. At r16 the sibling class was **moved the other way**: include-target and `config.worktree`
     kind failures are now soft (`guard_config_file_kind`, `:587-596`, called at `:647` and `:704`).
     Whole-run refusal for `info/attributes` is therefore an outlier against the r16 tool's own
     precedent — the precedent S5 cites.

`[INFERENCE]` The likely historical cause is that r15's repair was assembled from candidate
outputs (`ConfigRepair.md:23`) rather than designed against the exit contract; the element then
travelled with the list through a rewrite, a re-add, and a landing that happened ~47 minutes after
the re-add (`0a70bef` 11:40:42 → `c46eabf` 12:27:07), with wave-2 catching the blast radius only in
the closing minutes (wording fix at `4f9a4e8` 12:25:19, contraction left open — `round-16.md:59`).

## 5. Did any reviewer argue for per-repo degrade?

Yes — argued at r15, then re-derived independently at r16 wave 2 and by the closing verifier:

| Seat / source | Scope it argued for | Exact text |
|---|---|---|
| r15 `SpecialConfig.md:27-34` (SC-3, **High**) | the whole class incl. `git-metadata-nonregular`/`-unreadable` and `git-config-unparsed` | "Keep `exit 2` plus `path-protected` only for namespace reach… Route config-unsupported, nonregular, unreadable and unparsed cases to a per-row flag… Give these cases their own stderr finding, e.g. `config-unsupported`." |
| r15 `FiltersSafe.md:68-71` (F5, adjacent class) | config-selection refusals | "The refusal is not a path-safety event" → recommends per-row |
| r16 `RevCensusScanFinal.md:132-159` (S5) | the whole `guard_git_files` list | "keep the alias protection, drop the fleet abort"; patch: `cfg_soft "git-metadata-hardlink"; return 1` and call sites `|| soft=1`; cites `guard_config_file_kind:594` |
| r16 `CriticC1NoHarm2.md:75-76,138,150` (A2) | the whole class, and `info/attributes` as the regression vs r14 | "per-repo `error` row. No git runs in that repo, so this is strictly safe." / "A separate code change would remove the one regression against r14: take `info/attributes` out of L521, or route it through the per-repo soft path." |
| r16 `RevCensusStatusFinal.md:322-326` | attribute/excludes target nlink | "return 3 when `> 1`" |
| r16 verifier `round-16-verifier-spotcheck.md:135` | `info/attributes` only | "Degrade it per repo (patch in `RevCensusScanFinal.md` S5), or keep it explicitly under the L0 ruling." |

SC-3 was never integrated (r15 had no wave 2; landing stopped) and was not carried into the r15
lesson (`corpus/lessons/round-15.md` mentions attributes only as "local attributes/excludes
fidelity", `:116`). It was re-derived independently in r16, not inherited.

## 6. Does D2's per-repo degrade preserve the original safety goal?

**Yes — it preserves S1 and S2 exactly, and is strictly safer than computing the row.**

Mechanism at `5fa6017`:

1. `guard_git_files` is reached from `guard_git_surface` (`:821`) at `:831`/`:849`/`:873`
   (main dir, commondir, gitfile gitdir) and at `:790` (linked-worktree admin, inside
   `guard_worktree_registrations`).
2. `census_one` (`:1174-1181`) calls `guard_git_surface` **before** every measurement call
   (`:1201-1207`: `count_worktrees`, `count_unpushed`, `count_dirty`, `scratch_bytes`,
   `worktree_extra_flags`). On a soft return it prints the zeroed `error` row and returns —
   **no git command runs for that repository**.
3. The guard path's only git invocations are `git config --file … --no-includes` (`:618`, `:621`,
   `:671`), which open the named config file only and never read attributes. The attribute-reading
   calls (`ls-files`/`check-attr` `:1002-1008`, `status` `:1035-1037`) are all inside `count_dirty`
   and are therefore skipped.
4. The guard's own probes are `[ -f ]`, `[ -e ]`, `[ ! -d ]`, `stat -L -c %h` — stat only. A FIFO is
   stat'ed, never opened; a hardlink is stat'ed, never read.

Therefore: a hardlinked or non-regular `info/attributes` still *refuses the repo* (S2 alias
mitigation and S1 no-open are enforced by not measuring), and the file is never opened by the
census or by git. Nothing about the protected-namespace refusal changes: a resolved protected reach
elsewhere in the same repo still exits 2, because a soft finding never stops the scan
(`HEAD:93-96`, and `:605`) and `guard_config_path` still exits 2 on a protected hit.

What is *lost*, and must be disclosed rather than hidden:

- That repository becomes unmeasured (`error`, exit 0). This is a contraction against pre-harm
  `a31642d`, which measured it; D2 shrinks the contraction from fleet-wide to one row, it does not
  remove it (the verifier's ledger already classifies it as a disclosed residual,
  `round-16-verifier-spotcheck.md:49`).
- The failure is no longer loud to a consumer that reads only the exit code. That is the same trade
  the r16 config path already made and documents (`HEAD:97-100`), and the stderr diagnostic
  `git-metadata-unsupported <reason> <path>` (D2's wording) restores the loud channel on stderr.

Implementation caveats that determine whether step 2 actually holds:

- **C1 — keep the strong form.** D2's "no git call that could read that file" should be "no git call
  runs for that repo". The existing early return already gives the strong form; deciding per
  subcommand which calls "could read" attributes is the exact fragile reasoning that produced D2
  (`check-attr`, `status`, and `ls-files` with attribute pathspecs; `git config` does not).
- **C2 — diagnostic first-wins.** `cfg_soft` keeps only the first reason (`:580-583`). A commondir
  metadata soft can be masked by an earlier config soft from the main dir. Emit the
  `git-metadata-unsupported` line at the guard site (stderr) rather than relying on
  `CFG_SOFT_REASON`, or give it priority.
- **C3 — linked worktree / commondir ownership.** A hit while guarding a linked admin (`:790`) or a
  shared commondir must degrade the *owning repo's* row (i.e. `guard_worktree_registrations` returns
  1 and `worktree_extra_flags` is skipped). The plumbing supports this (`:855`, `:897`), but the
  fixture must include a linked worktree whose shared `info/attributes` is the hostile file —
  otherwise the test cannot distinguish "row degraded" from "worktree row never measured".
- **C4 — scope boundary.** `git-metadata-unavailable` (`stat` failure, `:526`) is outside D2's
  declared scope ("hardlinked or non-regular") and stays whole-run. A symlink resolving outside the
  gitdir is refused earlier by `guard_git_links` (whole-run); that is a boundary reach and should
  stay.

## 7. Divergences from the last-known-good intent (advisory)

- **V1 — false provenance (pre-existing, fixed for this element by D2).** Every `git-metadata-*`
  failure is printed as `path-protected` (`:197`, `:529-532`) though nothing protected is involved.
  The r15 High finding SC-3 made this the primary reason to split the channel. D2's distinct
  `git-metadata-unsupported` diagnostic is the first correct split.
- **V2 — `info/sparse-checkout` was part of the r15 intent and is now absent.** The r15 list was
  nine names (`b410186:522-524`); `cbf688a` dropped both additions; D2 restored only
  `info/attributes`. `grep -n sparse tools/souji-census.sh` at `5fa6017` returns **nothing**, and no
  r16 report or the SCORECARD notices the second loss (`SCORECARD.md:46` names only
  `info/attributes`). `PlanWalk.md:118-120` (G3) and `MetadataFlow.md:128` name
  `info/sparse-checkout` for the same FIFO-hang class (`status` reads it when sparse checkout is
  enabled). This is an unclaimed residual of the same class, not part of D2's declared scope.
- **V3 — the r15 header's class policy is not applied uniformly even in r16.** Include-target and
  `config.worktree` kind failures are soft (`:587-596`, `:647`, `:704`), fixed metadata is whole-run. D2
  moves `info/attributes` to the majority r16 behavior; the remaining seven stay loud by the r17
  claim, so a `cp -al` fleet still aborts (RevCensusScanFinal S5's counterexample survives for
  `config`/`HEAD`/`index`). That is a deliberate scope choice, but it should be stated in the
  round's no-harm ledger rather than left implicit.

## 8. Verdict

- **Why r15 added it: holds.** Six seats, vendor precedence, FIFO hang, hardlink alias residual.
- **Why r16 re-added it: holds.** RevBoundFilters D2; the r16 rewrite had silently dropped the r15
  guard, and the "any attributes source" claim would have been false.
- **Whole-run refusal: class-intended, element-artifact.** It was the list's inherited channel; no
  seat or commit weighed the fleet-wide consequence for this name, and the one seat that examined
  the channel (SC-3, High) rejected it as false provenance. The author's class policy was never
  executed, reviewed in a wave 2, or accepted.
- **Per-repo degrade argued before D2: yes**, at r15 (SC-3, and F5 for the adjacent config class),
  three times at r16 wave 2 (S5, CriticC1NoHarm2, RevCensusStatusFinal residual 1), and once by the
  closing verifier (routed D2).
- **D2 preserves the safety goal: holds**, on S1/S2, because the repo is skipped before any git call
  and the guard is stat-only. It does not relax the alias refusal; it converts a fleet abort into a
  named per-repo refusal. Conditions C1–C4 above must hold, and the fixture must prove "no git ran"
  (a configured clean-filter sentinel plus a short timeout discriminates a skipped repo from a
  measured one).

**Smallest fix (for the executor, if the above is accepted):** implement D2 as S5's patch shape
(`cfg_soft`/`return 1` for `rel = info/attributes` only; call sites `|| soft=1`), print
`git-metadata-unsupported <reason> <path>` at the guard site, keep `census_one`'s early return
unchanged, and add one fixture case with a linked-worktree commondir and a bound-filter sentinel.
Leave `info/sparse-checkout` out of this change only if the round records it as an open residual
(V2); otherwise it is the same one-line addition under the same class.

## 9. Commands run (exact) and observed output

All commands below ran while the worktree still equalled `5fa6017` (census sha256 `64a60fd0…`);
reproduce the `tools/souji-census.sh` reads against `git show 5fa6017:tools/souji-census.sh`
because the worktree has since been modified (see the drift notice above).

```text
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -S'info/attributes' --format='%h %ad %s' -- tools/souji-census.sh
0a70bef 2026-10-20 round-16: integrate wave-1 review fixes into census, config fixture and matrix runner (C1)
cbf688a 2026-10-20 round-16: restore parsing value/effect-aware census; execute and repair config fixture (C1)
b410186 2026-10-20 round-15: land operator-stopped config repair candidates; acceptance unrun

$ git show b410186:tools/souji-census.sh | sed -n '520,524p'
guard_git_files() { # $1 resolved gitdir
  local dir=$1 rel path nlink
  for rel in config HEAD index packed-refs commondir \
      info/exclude info/attributes info/sparse-checkout \
      objects/info/alternates; do

$ sed -n '521p' tools/souji-census.sh   # HEAD
  for rel in config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates; do

$ git diff --stat cc21683 cbf688a -- tools/souji-census.sh
 tools/souji-census.sh | 353 ++++++++++++++++++++++++++++++++++++++++++--------
 1 file changed, 299 insertions(+), 54 deletions(-)
$ git diff cc21683 cbf688a -- tools/souji-census.sh | grep -c 'info/attributes'
0

$ git show b410186:tools/souji-census.sh | sha256sum
dab4122c997db9b921e036ec8e2adf4c0e4743d8722ba9b2a28739bda9397810  -
$ git show b410186:tools/souji-census.sh | bash -n /dev/stdin
/dev/stdin: line 1368: syntax error near unexpected token `}'
/dev/stdin: line 1368: `}'
rc=2
$ bash -n tools/souji-census.sh ; echo rc=$?      # HEAD
rc=0
$ sha256sum tools/souji-census.sh
64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c  tools/souji-census.sh
$ git show c46eabf:tools/souji-census.sh | sha256sum
64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c  -

$ git show b410186:tools/souji-census.sh | grep -n 'Whole-run exit 2 is reserved\|safe fleets keep every row'
108:#   forms) mark only that repo's row `error`; safe fleets keep every row.
109:#   Whole-run exit 2 is reserved for protected-path reaches, ambiguous
$ git show b410186:tools/souji-census.sh | sed -n '106,111p'
#   Config conditions that leave a repo unusable (unparsed file, include
#   cycle or depth over git's 10, scan budget exceeded, unsupported value
#   forms) mark only that repo's row `error`; safe fleets keep every row.
#   Whole-run exit 2 is reserved for protected-path reaches, ambiguous
#   targets, non-regular include targets, hardlinked config files, and git
#   metadata that fails the integrity checks.

$ grep -n 'check-attr\|status --porcelain\|ls-files -z' tools/souji-census.sh
35:#   dirty           `git status --porcelain` line count on the main work tree
58:#                     own `git status --porcelain` is non-empty.
982:# Neither ls-files nor check-attr runs a driver.
1000:  # Same pathspec exclusions as status, so check-attr never reads an
1003:      ls-files -z --cached -- . ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
1008:      check-attr -z --stdin filter 2>/dev/null)
1037:      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
$ grep -n 'count_dirty()' tools/souji-census.sh
1021:count_dirty() { # $1 repo; exit 2 on a protected reach
$ grep -n 'guard_git_files' tools/souji-census.sh
519:guard_git_files() { # $1 resolved gitdir
790:            guard_git_files "$admin" || exit 2
831:    guard_git_files "$dir" || exit 2
849:        guard_git_files "$dir" || exit 2
873:    guard_git_files "$dir" || exit 2
891:        guard_git_files "$dir" || exit 2
$ sed -n '1174,1181p' tools/souji-census.sh
census_one() { # $1 repo-dir
  local repo
  repo=$(guard_path repo "$1") || exit 2
  if ! guard_git_surface "$repo"; then
    printf 'souji-census: config-unsupported: %s (%s)\n' \
      "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$repo")" >&2
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
$ grep -n 'sparse' tools/souji-census.sh
(no output; exit 1)

$ git log --format='%h %ad %s' --date=iso -8
5fa6017 2026-10-20 12:29:50 -0300 round-16 verifier spot-check (integrator, hyaku): non-author admit/reject
c46eabf 2026-10-20 12:27:07 -0300 round-16: landing gate evidence at 6ff91f5 (findings=0, 30 markers, 141 reports)
6ff91f5 2026-10-20 12:26:56 -0300 round-16: carry wave-2 STATUS lines; dead-seat authorship and wave-2 audit in Process
79bbe7a 2026-10-20 12:25:28 -0300 round-16: final wave-2 seat reports
4f9a4e8 2026-10-20 12:25:19 -0300 round-16: wave-2 honesty corrections (lesson, SCORECARD, QUALITY Q25/Q26, SOURCES S044/S045, LOG append); wave-2 seat audit
fb23b12 2026-10-20 12:21:18 -0300 round-16: wave-2 reports; gate fixture vacuity fix; knowledge freshness notes (host git 2.56.0)
163158a 2026-10-20 12:03:21 -0300 round-16: lesson, sources S043-S050, Q25/Q26, LOG correction and entries, SCORECARD, SKILL, README
a6ec781 2026-10-20 11:59:22 -0300 round-16: narrow the gate's failure channel to contract STATUS vocabulary; audit honors ALLOWED-EXEC (C2, R5)
# 0a70bef (11:40:42) and cbf688a (11:13:47) are older ancestors; their timestamps from `log -1`.
$ git log -1 --format='%H%n%ad%n%an%n%n%B' 0a70bef   # cbf688a, b410186 likewise
(empty body; subject only)

$ zcat /usr/share/man/man5/gitattributes.5.gz | grep -n -A3 'highest precedence'
109: When deciding what attributes are assigned to a path, Git consults $GIT_DIR/info/attributes
     file (which has the highest precedence), .gitattributes file in the same directory …
     [rendered line 109 continues past this point; the precedence clause is complete here]
$ git --version
git version 2.56.0
```

Non-shell reads: exact-file `read`/`grep` over the r14/r15/r16 wave reports and lessons named in
§2/§5, `SCORECARD.md:15,46`, `corpus/lessons/round-15.md:9,116`, and the r17 `w1-spec.json`
(item `RevengeAttrGuardIntent`, plus `CensusD1D2`, `ScoutAttrGuardFlow`, `RevD2Static`,
`SentinelFifoHostile`, `CriticC1Harm` for the declared D2 shape).

Conduct: no census/fixture/gate run, no `jj`, no git write, no network write, no recursive search
over the lane or fleet root, nothing under `census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`
or `MANIFEST.json` opened. Tool installs/updates: **none** (no install was needed; `git 2.56.0`,
`bash` and the installed gitattributes(5) page sufficed. ShellCheck was **not** run and is not
claimed here).

## 10. Confidence

- Chronology and code facts (**high**): every citation was read in the blob or file named, and the
  two digests plus both parse states were re-derived here.
- "Class-intended, element-artifact" (**high** for the artifact half — no document decides the
  element's blast radius and the channel is inherited; **medium** for the class half, because the
  only statement of class intent is the r15 header of a revision that never parsed or ran).
- Safety-preservation verdict (**high** for S1/S2 under the existing soft early-return; conditional
  on C1–C3 being implemented as described).
