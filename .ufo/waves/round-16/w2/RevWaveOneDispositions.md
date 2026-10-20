# RevWaveOneDispositions — round 16 w2 (reviewer, calibration)

Target: every wave-1 report under `.ufo/waves/round-16/w1/` whose STATUS line is non-ok,
dispositioned against lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Mode: source-only at HEAD (committed blobs via `git show`/`cat-file`, `sha256sum`,
`bash -n`/`compile()` not needed here). No census, fixture, gate, selftest, matrix, audit
or lane file was executed or edited; this report is the only write.

## 0. Selection rule, and why it had to be chosen deliberately

63 `*.md` reports. 52 carry a column-0 `STATUS:` line; one more (`SrcGitCheckAttr.md:113`)
carries a bolded `**STATUS:` line; 10 carry no STATUS line at all (`LandingGate`, `PlanWalk`,
`RevBoundFilters`, `RevHeaderDocs`, `RevIncludeResolve`, `RevMatrixRunner`, `RevSoftPropagation`,
`ScoutAltRefsConsumers`, `SimplifyCensusDiff`, `SrcPythonAst`).

A literal reading of the contract (`STATUS: FAIL|INCOMPLETE|BLOCKED|PARTIAL`) selects **zero**
reports: no wave-1 seat used the failure vocabulary, even where it declared a live defect.
The substantive reading — a STATUS line that asserts an open defect, failure, refusal or
blocked state in a round-16 deliverable — selects **21** reports. That gap is itself the main
finding (§2 F1), because the landing gate's marker set is the literal vocabulary.

Measured gate consequence (committed bytes at HEAD, regex read from
`tools/souji-landing-gate.py:62-78` and applied by hand): the round-16 wave-1 corpus produces
exactly **two** vocabulary markers, `ConnLogConvention.md:221` and `:385`, both 4-space-indented
quotations of r15 `ConfigRepair.md:7` (the gate's own selftest string). Both are carried by
`corpus/lessons/round-16.md:43,58`, so a `--round 16` run at a revision containing that lesson
would report `checked_markers=2`, `findings=0` — while none of the 21 defect lines below is
visible to it. "Green at round end" is therefore reachable without any of these dispositions.

## 1. The 21 non-ok STATUS lines

Verdicts: **fixed** = HEAD code/fixture removes the reported failure; **partial** = some
sub-items fixed; **open** = survives at HEAD. Line numbers are HEAD unless a revision is named.

### 1.1 ConnFrontier.md:242 — partial
> STATUS: no check in this seat failed. Known state: no frontier row advances; the F2 live pointer contradicts committed r13 evidence; C2 is not present at this checkpoint (`tools/souji-landing-gate.py` absent) and `census/round-16/c1-matrix.json` is untracked author output, not acceptance.

C2 presence and the untracked-artifact facts are fixed: `tools/souji-landing-gate.py` and
`census/round-16/c1-matrix.json` are both in `git ls-tree HEAD`. The F2 pointer is **not**
fixed: `corpus/README.md:47` still reads "next: the /var/tmp write-safety fixture for
`git repo structure`", which r13 already acquired (`tests/fixtures/r13-repo-structure.sh:2`,
`:107`). Minimal fix: replace that pointer with the next capability (whole-workspace size
attribution, per `PROVINCE.md:55-57`).

### 1.2 CriticFixtureOverfit.md:49 — partial
> STATUS: findings advisory. The 05 and 20 oracle fixes are genuine, not fitted. The 03, 07, 12 and 14 row semantics are grounded in pre-harm a31642d, git docs and Q22, but 03 and 14 also pin stderr tokens minted by cbf688a (Q11), and 07 depends on an unsourced Git-version behavior. Static analysis says all 13 HARM_CASES fail on r14-harm (not executed). HARM_CASES omits 18 and 20, which also fail on harm. tools/souji-preservation-evidence.py still holds the r15 class table and was not migrated. Known failure: none of this seat's conclusions were confirmed by a run.

Fixed: `HARM_CASES` now includes `R15CFG-18` and `R15CFG-20`
(`tests/fixtures/r15-census-config.py:161-165`); the paired-evidence class table is migrated —
`tools/souji-preservation-evidence.py:323-357` puts 03 in `CONFIG_SAFETY_IDS`
("could-not-evaluate config: per-repo error row (degrade)"), 07 in `CONFIG_BENIGN_IDS`,
14 in `SAFETY`, and carries 18/20; the fixture now has the mixed-degrade fleet
(`:556-565`) and the precedence repo (`:468-472`); the run-based evidence exists at
`c6207bd`/`c1-matrix-final.json`. Open: 07's git-version dependence is still unsourced
(no SOURCES row pins which command parses `remote.*.promisor`), and the two stderr tokens
(`config-unsupported`, `status-skipped`) pinned by 03/14 are still absent from the documented
contract: `SKILL.md:139` documents the row flags only, and `corpus/QUALITY.md` mentions neither.
Minimal fixes: (a) add one clause to `SKILL.md:139` naming the two diagnostics; (b) either cite
the promisor-parse behaviour or relax 07's oracle to "not refused; row present; dirty accurate
or `status-unverifiable`".

### 1.3 CriticGateVacuity.md:140 — fixed
> STATUS: gate file absent at review time — findings are against the pinned contract only; the held-out replays A1/A2 are predictions from the regex applied to committed bytes, not gate runs.

Gate exists at HEAD and its selftest covers the predictions: fenced-block and table-row
exclusion plus STATUS anchoring (`tools/souji-landing-gate.py:62-78`, `:273-289`) removes the
A1/A2 false positives (r13 `EvidenceConnection.md:165`/`SourceTimeout.md:78`, r14
`CachePrecedent.md:159,220` are code/table/recipe lines, none STATUS-anchored); A8
(missing wave dir → exit 2) is `check_carry`'s `EvalError`; A9/A10 are
`LG-FROZEN-PIN`/`LG-FROZEN-MEASURED` and the value-binding cross-check (`:457-500`);
A3/A4 are covered by the channel and vocabulary (`**STATUS:` tolerated at `:71`;
`fails`/`unrun`/`red` in `FAILURE_STATUS_WORDS` at `:72-78`), and the selftest exercises
`bold-status`, `uncarried-marker` and `open-admitted` (`:883-923`); A5 (prose-only
`SyntaxError: invalid syntax`) is deliberately **not** covered — the prose net was dropped
for the 42-line false-positive reason stated at `:63-70`. A11/A12 are
`check_python` (`compile()`, `:213-221`) and `check_bash` (any stderr, `:192-211`). Open, and
already declared a tradeoff: F3 (substring carry = transcription, not disclosure) — the gate
still accepts pasted lines. Minimal fix: one contract sentence in the gate header stating the
carry is transcription and naming the pasted-appendix route as out of scope.

### 1.4 CriticNamespaceWeakening.md:5 — fixed
> STATUS: Source review identifies a definite soft-refusal precedence defect and multiple newly exposed access paths; runtime outcomes are [INFERENCE], not measured failures. C1's namespace-retention claim is not established by the supplied matrix.

All four defects are addressed at HEAD. (1) Soft no longer pre-empts a protected reach:
`scan_config_file` sets `soft=1` and continues (`tools/souji-census.sh:603-606`, `:640-665`),
and `guard_git_surface` collects `soft=1` until after every metadata guard (`:792`, `:821-856`,
`:870-899`); the precedence shape is fixtured (`r-tilde-then-store`,
`tests/fixtures/r15-census-config.py:468-472`, case_02 `:1118-1119`). (2) Relative-include
origin is the spelled path (`scan_config_file` `$4`, `:641-648`). (3) Index readers are
neutralized by `GIT_CONFIG_COUNT` (`:162-163`) and the fixture adds `s-fsm-filter`
(`:405-411`, case_08 `:1215`). (4) `ls-files`/`check-attr` now carry status's pathspec
exclusions (`:1002-1007`). Residual hardlink/XDG notes are declared in the header
(`:125-128`).

### 1.5 CriticNoHarmPreharm.md:14 — open (1 of 8 fixables landed)
> STATUS: residual contraction exists and needs operator scope adjudication. Fixable defects: A1, A2, A3, A4, B1, B2, C2, E2. Tradeoffs the operator must rule on: A7, C1, D1, E1. Policy-mandated, no correction: E3.

Only C2 (unmodellable config values) is fixed (`guard_config_path` returns 3,
`tools/souji-census.sh:535-560`; callers degrade `:641-670`). Still whole-run exits at HEAD:
A1 symlink-out-of-gitdir (`:512`), A2 hardlink metadata (`:529`), A3 alternates
symlink/quoted/depth (`:475-491`), A4 unreadable gitdir dir (`:503-506`); B1 fleet-child
symlink still skipped (`:1287`); B2 symlinked `.git` still dropped after guarding
(`:1290-1293`); E2 `--ignore-submodules=all` still on every status (`:1037`). The C1 claim
"only a protected reach exits 2" is false for each. Minimal fix: the report's own
§"Smallest safe corrections" 1-3 (soft-degrade those classes; resolve B1/B2 with
`guard_target` and emit a row); E2 needs a gitlink flag (`status-unverifiable` when the index
has mode 160000). Both are scope decisions L1 owns, but the claim text must be narrowed until
they land.

### 1.6 MutateDirtyFilters.md:5 — fixed
> STATUS: SURVIVED M02 — disabling the HOME/.config/git default passes both allowed detectors. Seven of eight mutants were killed; zero probes were inconclusive. This is a coverage finding, not permission to weaken C1.

M02 (`base=${XDG_CONFIG_HOME:-/dev/null}`) now fails: the fixture creates
`$HOME/.config/git/ignore` and repo `r-xdg-default` expected `CLEAN`
(`tests/fixtures/r15-census-config.py:598-606`, `:1163`). The mutant forces
`-c core.excludesFile=/dev/null`, so `xdg-hidden.txt` counts dirty and case_04 fails.

### 1.7 MutateScanConfig.md:2 — partial (m2 open)
> STATUS: Probe complete: 8 single-line mutants; 5 killed, 3 survived (m2, m4, m6: fixture gaps); 0 inconclusive. Every pristine and restored detector run passed. m8 included an observed, bounded FIFO timeout. Scratch restored exactly, then deleted.

m4 killed by `r-inc-tilde-store` (`tests/fixtures/r15-census-config.py:466`, case_02
`:1118`); m6 killed by `r-inc-twice` (`:445-450`, case_01 `:1104`). **m2 survives**: removing
the `CFG_STACK` equality check (`tools/souji-census.sh:613-615`) still yields a soft
`git-include-depth` row, and `soft_repo` (`:1079`) accepts any `config-unsupported`
detail — the fixture still contains no `git-include-cycle` assertion. Minimal fix: in
`case_03`, assert that `r-inc-cycle`'s stderr carries `git-include-cycle` (the census already
emits `CFG_SOFT_REASON`, `:579-584`).

### 1.8 RevengeFrozenPin.md:202 — fixed; one doc residual
> STATUS: `b5187351…` is unattested — no committed blob, no odb object, no reproducible transcript; frozen verdict `clean` is unreachable at `b410186` and the pin is still unrepaired at `cbf688ab`.

Fixed at HEAD: `expected.json` pins `tools/souji-census.sh = 64a60fd0…`,
`tests/fixtures/r15-census-config.py = 27474396…`, `tests/fixtures/r14-census-boundary.py =
e6a984b1…`, and all three equal the HEAD blobs I hashed. `record.json:7` sets
`measured_commit = c6207bd`, and `git cat-file blob c6207bd:tools/souji-census.sh` hashes to
`64a60fd0…` (value-binding holds); every arm's `commit`/`sha256` pair matches
(`record.json:92-93`, `:225-226`, `:353-354`, `:481-482`); `record_sha256` equals the record's
actual digest (`173db777…`); transcripts now print absolute tool paths
(`record.json:82`, `:471`); the laundering recipe is superseded by
`tests/fixtures/r15-preservation-frozen/regenerate.py`. Residual (D5 documentation): the frozen
`README.md:7-21` still declares "These pins were authored before the C1 repair… correctly
yields `snapshot_tampered`… until the integrator refreshes" and instructs a digest-only refresh
(steps 1-2), contradicting the record it now ships with. Minimal fix: replace
`README.md:7-21` with "re-measure via `regenerate.py`; never rewrite digests without
re-capturing each arm's stdout".

### 1.9 RevengeInertKeys.md:245 — partial
> STATUS: r16 fixture docstring still carries the pre-r16 refusal rules at `tests/fixtures/r15-census-config.py:46-47,61-62` (superseded by `:13-14` but not reconciled); the `alternateRefsCommand` inertness proof is fixture-vacuous for the documented alternate-advertisement trigger (no fixture repo has `objects/info/alternates`) and unguarded by the selftest source audit (`tools/souji-census.sh:1729-1731`).

The source-audit half is fixed: `tools/souji-census.sh:1822` extends the forbidden-invocation
regex with `^[^#]*--alternate-refs`. The docstring half is **not** fixed: HEAD
`tests/fixtures/r15-census-config.py:46-47` still says "invalid booleans refuse fail-closed as
could-not-evaluate" and `:61-62` says "any non-empty command value refuses", while `:19-22`
says promisor is never refused and `alternateRefsCommand` is inert for any value. The fixture
still has no `objects/info/alternates` repo (grep of the HEAD fixture: no match), so the
sentinel remains non-discriminating. Minimal fix: rewrite the two bullets to the r16 rule (keep
the sentinel as a negative control, say so); the alternate-store repo is optional and would
need a benign alternates target the boundary guard admits.

### 1.10 RevFixtureR16Edits.md:237 — partial (T2 open)
> STATUS: review complete (source inspection, no execution). No blocking defect found in the fixture's oracle logic; F1/F2/T1/T2 should land before C1's "for that repo only" and "driver never runs" claims are accepted, and F4 must be re-pinned or retired.

F1 fixed (`f.bin` rewritten after the commit, `tests/fixtures/r15-census-config.py:527-537`,
the rewrite at `:535`); F2 fixed (`FL_MIXED_DEGRADE`, `:556-565`, asserted in case_03
`:1125-1145`); F3 fixed (`soft_problems` now pins the mtime cell, `:1054-1072`, assert at
`:1072`); F4 fixed (repin, §1.8); T1 fixed
(`wait`/`pipefail`/stride → `return 1` fail-closed, `tools/souji-census.sh:1009-1011`); T3
fixed (`status_info_file` returns 3, `:942-952`). **T2 open**: `run_selftest` (`:1522`) still
exercises none of `scan_config_file`, `status_info_file` or `guard_bound_filters` — a scan of
`tools/souji-census.sh:1522-1825` finds no such reference. Minimal fix: three selftest cases
over existing `mktemp` fixtures (benign include chain, one degrade config, one unbound-driver
repo).

### 1.11 RevGateSpec.md:226 — partial (P3, P6 open)
> STATUS: review complete — no blocking defect in this deliverable; C2's contract needs P1–P9 applied (G1–G6 are pre-adoption blockers) and cannot be green at cbf688a as written.

Applied at HEAD: P1/P2 (G1/G2 — STATUS-anchored marker, fences/tables skipped,
`tools/souji-landing-gate.py:62-78`), P4 (G4 — empty wave dir → `EvalError`/exit 2,
`:313-314`), P5 (G5 — R4 repin plus `LG-FROZEN-MEASURED`, `:457-500`), P7 (G7 —
`--diff-filter=AM` parsed at REV, `:555-566`, the flag at `:557`), P8 (G8 — `ROOT_PREFIXES`, record-relative
resolution and `record_sha256`-without-record finding, `:87-89`, `:431-434`), P9 (G9 — config
paths now `cfg_soft`, census `:641-670`). **Not applied**: P3 (G3) — no `--report` argument
(`argparse` at `:984-989` has `--root/--rev/--round/--base/--json/--selftest` only), so R3's
"the L1 report" surface is still unenforced; P6 (G6) — no `LG-PARSE-TREE`, so an uncited new
non-parsing helper lands green without `--base`. Minimal fixes: add `--report` and emit
`checked_report=0|1`; add the tree scan or make `--base` mandatory for landing runs.

### 1.12 RevRedaction.md:214 — partial (F1, F3 open)
> STATUS: no defect found that breaks either fixture oracle; three real but narrow issues

F2 fixed (`guard_config_path` returns 3 for non-protected resolve failures,
`tools/souji-census.sh:535-560`; callers degrade). **F1 open**: `protected_fail` still redacts
only when `protected_reason_inside` normalizes to a protected path
(`tools/souji-census.sh:200-207`), and `resolve_guarded` still prints the raw input for
`ambiguous-path` (`:386`, `:396`), so `--root "$HOME/.omp/agent/.."` echoes the store path.
**F3 open**: `load_census` (`:1339`) still validates only columns 2-5 and non-empty repo names
(`:1374-1390` unchanged by `0a70bef`), so `--compare` echoes baseline content unfiltered.
Minimal fixes: add the textual reach predicate the report supplies and OR it into
`protected_fail`; guard/sanitize `mtime_iso`/`verdict_flags` on load.

### 1.13 RevR14NamespaceRetention.md:253 — partial (F3 open, F4 fixed)
> STATUS: no defect found that changes any of the 12 case outcomes at cbf688a. F1 is the only r16-introduced path that converts a namespace refusal into a soft `error` row, and it requires an unevaluable config the fixture never creates (medium, exit-code/finding fidelity only, no store read).

F1 fixed (soft findings no longer stop the scan; all hard guards run first,
`tools/souji-census.sh:603-606`, `:792`, `:821-856`, `:870-899`; precedence fixtured at
`tests/fixtures/r15-census-config.py:468-472`). F2 fixed (`status_info_file` returns 3 and
`count_dirty` degrades, `tools/souji-census.sh:942-952`, `:1021-1026`). F4 fixed (the
`config-unsupported` diagnostic is now printed for a soft worktree, `:1157-1159`). **F3 open**:
`PROTECTED_HOME_ROOTS+=("$pi/agent")` still appends the raw absolute `PI_CONFIG_DIR` form
(`tools/souji-census.sh:269`), unnormalized. Minimal fix: wrap in `lexical_abs` at `:269` and
`:296`.

### 1.14 RevScanParse.md:206 — fixed
> STATUS: no defect in the `scan_config_file` key/subsection/variable split; RSP-1 (High) is a real filter-execution bypass in the same `--list -z` record idiom, RSP-2 (Medium) is a `worktreeConfig` state-model defect, RSP-3 (Low) is a declared-shape contract mismatch. No check was executed against a real repository.

RSP-1 fixed with the supplied patch shape: `case "$rec" in *$'\n'*) [ -n "${rec#*$'\n'}" ] ||
continue ;; esac` (`tools/souji-census.sh:990-992`). RSP-2 fixed: the grant is read only at
depth 0 (`:669`) and `guard_wt_config` saves/restores it (`:696-710`). RSP-3 fixed: control
characters return 3 and degrade (`:542-560`, callers `:640-670`). Coverage gap persists (no
trailing-newline filter value in the fixture) but the bypass is closed.

### 1.15 RevStatusInfoFile.md:213 — partial (F3, F4, F5 open)
> STATUS: review complete. F1 (MEDIUM, row accuracy) and F6 are fixed in the live worktree; F2 (MEDIUM, whole-run abort on non-protected unresolvable values) is fixed in the live worktree but untested by the fixture; F3/F4/F5 remain live in both cbf688a and the worktree. No execution was possible under the probe rule, so every git-behaviour claim above is source/doc-grounded, not observed.

F1 fixed (`rc`-aware read, set-but-empty → `/dev/null`, `tools/souji-census.sh:942-947`);
F2 fixed (rc 3 path, `:535-560`, `:640-670`); F6 fixed (`:(optional)` stripped, missing target →
XDG, `:652`, `:947-954`). **F3 open** (per-occurrence refusal; no last-wins map — grep for
`CFG_VAL` returns nothing, and the "last-wins" sentence remains at `:602`); **F4 open**
(excludes/attributes scan base is still `${dir%/*}`, `:652`); **F5 open** (`[ -z "${HOME:-}" ]`
at `:962`, relative XDG → `/dev/null` at `:965-968`). Minimal fixes are the report's three
diffs. Note: F2 is still fixture-untested — no case uses a multi-line or looping excludes value.

### 1.16 ScoutGitHostVersion.md:124 — open
> STATUS: no host version/doc gap; item premise "installed 2.55" is false - installed is git 2.56.0 (pacman 2.56.0-1), matching served 2.56.0 docs.

Not fixed at HEAD: `corpus/SOURCES.md:56` (S042) still says "installed 2.55.0 corresponding
sections via SoujiR15.SourcesDraft", and `:49`/`:50` (S035/S036) say "installed 2.55.0 manual".
Three independent seats measured git 2.56.0 and the installed man-page header
(`Source: Git 2.56.0`, `Date: 2026-09-27`). Minimal fix: change S042's anchor cell to
"installed 2.56.0" (and record the host version in the round-16 lesson Gate), or mark the
2.55.0 anchors as authored-before-upgrade.

### 1.17 SentinelCommandExec.md:91 — fixed (F3 informational, open)
> STATUS: F1 is open; I inferred it from the docs and did not run it. As a result, the C1 statement that "hooksPath/fsmonitor … are inert" does not hold for repos that define a filter key. F2 is a low-severity fail-open. No tool installs or updates.

F1 fixed exactly as proposed: `export GIT_CONFIG_COUNT=2 … core.fsmonitor=false …
core.hooksPath=/dev/null` after the `GIT_*` purge (`tools/souji-census.sh:162-163`), plus the
sentinel repo `s-fsm-filter` (`tests/fixtures/r15-census-config.py:405-411`, case_08 `:1215`).
F2 fixed: `pipefail` + `wait "$pid" || return 1` + stride check (`:1009-1011`). F3 (the
`rev-list … || printf '0'` fallback, `:927`, `:931`) is outside the STATUS text and still open.

### 1.18 SrcBashSetN.md:129 — resolved by landing
> STATUS: live gnu.org unreachable from this host on 2026-10-20 (curl exit 28, 12-25 s timeouts, both schemes); quote from Wayback capture 20260930073822, edition line from capture 20260927102039, installed GNU Bash 5.3 man page corroborates. `tools/souji-landing-gate.py` and `scripts/sources-census.sh` are absent at read time.

The gate-absence half is moot (gate tracked at HEAD); S043 exists with the Wayback anchor and
the L1 offline corroboration (`corpus/SOURCES.md:57`). The live-page failure is an environment
fact, not a lane defect, and the row does not depend on it. No counterexample.

### 1.19 SrcGitConfigIncludesRecheck.md:295 — open
> STATUS: source re-check complete and S042 still supports its mined claim; no probe was run by this seat. Two claim-level discrepancies recorded for L1: (1) S042's anchor says installed 2.55.0 but the installed man pages declare Git 2.56.0 (TH 2026-09-27); (2) C1's "only a protected-namespace reach keeps whole-run exit 2" is contradicted by `usage_err` and by non-namespace `protected_fail` classes (`ambiguous-path`, `unresolved-path`, `symlink-loop`, `git-metadata-symlink`, `special-path`, `hardlinked-compare`, `load_census` bad baseline).

Both open. (1) is the S042 anchor (§1.16). (2) is a live claim defect: `protected_fail`
still fires at these non-namespace sites at HEAD — `tools/souji-census.sh:386`, `:396`,
`:432`, `:436`, `:442`, `:475`, `:480`, `:487`, `:503`, `:506`, `:512`, `:526`, `:529`,
`:532`, `:700`, `:719`, `:866`, `:1137`, `:1345` (19 sites: `ambiguous-path`,
`unresolved-path`, `symlink-loop`, `git-alternates-*`, `git-metadata-*`, `special-path`) —
plus `usage_err` (`:187`) for CLI/baseline errors. Namespace reaches (`:403`, `:416`, `:422`,
`:427`, `:548`, `:556`, `:1284`) are correctly not counted. Minimal fix: narrow the claim to
"for repository config, only a protected-namespace reach exits 2; structural git-metadata
guards, compare-mode refusals and CLI usage errors also exit 2", or land
CriticNoHarmPreharm A1-A4.

### 1.20 SrcGitNoLazyFetch.md:69 — open
> STATUS: no behavioural probe was executed (Q24/R5-compliant); the git binary version is unverified and the 2.55.0→2.56.0 installed-docs discrepancy is reported, not resolved.

Not fixed: no host git version is recorded in `corpus/SOURCES.md` or the lesson draft's Gate
section, and SOURCES is unchanged. Minimal fix: one cell recording the host version (the same
patch as §1.16).

### 1.21 SrcGitCheckAttr.md:113 — resolved (evidence voided, source re-derived)
> **STATUS: PROBE RULE breach self-disclosed — one whole-lane recursive grep was run (`grep -rn 'SOURCES-CONTRACT' /home/vgpnk/Projects/shokunin/souji-shokunin --include=*.md --include=*.sh --include=*.py`), which the round-16 PROBE RULE forbids; per contract this voids this seat's evidence unless L1 re-derives it. The grep traversed the lane, so it may have opened files under `census/operator-sweep-20261019/`; no line from that path appeared in the output and nothing from that directory was quoted, copied or used.**

Dispositioned by L1 at `a6ec781`: the R5 audit's independent finding is
`census/round-16/seat-audit-w1.json` (19 minor whole-lane reads), S046 was re-derived by L1,
and the lesson carries the disclosure (`corpus/lessons/round-16.md:47`). No open lane defect.
This line is invisible to the gate (`PROBE` is not in `FAILURE_STATUS_WORDS`), which is §2 F1
in one example.

## 2. Cross-cutting findings (the calibration payload)

### F1 — HIGH — the landing gate's failure channel has zero recall on this round's own disclosures
Measured on committed wave-1 bytes: 21 substantive non-ok STATUS lines, 0 using the vocabulary
at `tools/souji-landing-gate.py:72-78`; the only two vocabulary markers in the corpus are
4-space-indented quotations of the r15 seat line in `ConnLogConvention.md:221,385`, both
carried by the lesson. So `checked_markers` counts self-quotations and the 21 defect lines are
outside the channel — while `corpus/lessons/round-16.md:39-51` claims the section holds "every
failure-channel STATUS line and every non-ok STATUS line that reports a defect". It lists 12
lines and covers 10 of the 21 (CriticNoHarmPreharm, MutateDirtyFilters, MutateScanConfig,
SentinelCommandExec, CriticNamespaceWeakening, RevengeFrozenPin, RevengeInertKeys,
SrcGitCheckAttr, SrcBashSetN, CriticGateVacuity). Missing 11: `ConnFrontier.md:242`,
`CriticFixtureOverfit.md:49`, `RevFixtureR16Edits.md:237`, `RevGateSpec.md:226`,
`RevRedaction.md:214`, `RevR14NamespaceRetention.md:253`, `RevScanParse.md:206`,
`RevStatusInfoFile.md:213`, `ScoutGitHostVersion.md:124`,
`SrcGitConfigIncludesRecheck.md:295`, `SrcGitNoLazyFetch.md:69`. Two of those
(`RevScanParse`, `RevR14NamespaceRetention`) are fully fixed and need only a disposition line;
the other nine carry at least one open item from §1.
Minimal fix (precision-preserving): add `LG-SEAT-STATUSVOCAB` — a STATUS line whose value's
first token is neither benign (`ok`, `none`, `no`) nor a failure token is a finding; and add
the eleven missing lines to the lesson's section with `resolved@`/`open`. The measured
42-line false-positive set was non-STATUS prose, so a STATUS-only format check cannot
re-introduce it.

### F2 — MEDIUM — the gate treats indented code blocks as markers
`seat_failure_lines` toggles only on lines starting with a fence
(`tools/souji-landing-gate.py:273-289`), so a 4-space-indented quotation is parsed as a
STATUS line (`STATUS_PREFIX_RE` tolerates arbitrary leading whitespace, `:71`). The contract
says "on a line starting `STATUS:`". Minimal fix: require the raw line to match
`^(#{1,6}[ \t]+)?([-*][ \t]+)?STATUS` (no general `\s*`), which also drops the two
self-quotation markers in `ConnLogConvention.md`.

### F3 — MEDIUM — the frozen-pin check cannot see the r15 D5 splice
`check_frozen_pins` verifies `files[]` against `measured_commit` blobs and `record_sha256`
against the record (`tools/souji-landing-gate.py:388-500`), but never verifies the record's own
transcripts: `stdout_sha256` is unchecked and the `TOOL <path> sha256=<hex>` token inside
`runs.*.stdout` is never compared to the pin. The HEAD record is honest, but a digest-only
re-pin that keeps the authored transcript (RevengeFrozenPin D5) would still be green.
Minimal fix: for each arm, assert `sha256(stdout) == stdout_sha256` and that the transcript's
`TOOL` digest equals the pinned `files[<tool>]`; pure bytes, no execution.

### F4 — MEDIUM — C1's refusal claim is still overbroad
See §1.19: 19 of the 26 `protected_fail` sites are non-namespace, plus `usage_err`. The wave-2 context
sentence ("only a protected reach exits 2 whole-run") repeats the overbreadth. Minimal fix:
one claim sentence, or land CriticNoHarmPreharm A1-A4/B1/B2.

### F5 — LOW — auditability gap: 10 reports carry no STATUS line
`LandingGate`, `PlanWalk`, `RevBoundFilters`, `RevHeaderDocs`, `RevIncludeResolve`,
`RevMatrixRunner`, `RevSoftPropagation`, `ScoutAltRefsConsumers`, `SimplifyCensusDiff`,
`SrcPythonAst`. The w2 contract already requires `STATUS: ok` when there is no failure; the
wave-1 contract only said "any known failure on a line starting `STATUS:`", so these are not
violations — but they are indistinguishable from an unreported failure, and the gate has no
check for it. Minimal fix: add `LG-SEAT-NOSTATUS` (a report with zero STATUS lines → finding)
for every `--round N` that has reports.

### F6 — LOW — two documented-contract tokens are still undocumented
`config-unsupported` and `status-skipped` are pinned by the fixture oracles
(`tests/fixtures/r15-census-config.py:1051`, `:1298-1299`) but absent from `SKILL.md:139` and
`corpus/QUALITY.md`. Minimal fix: name them in the census registry row's semantics cell.

## 3. Second bucket — STATUS lines that declare an unrun requirement, not a seat failure

- `DraftLessonMistakes.md:44` "STATUS: no failing check. … Items the L1 acceptance must still run: the landing-gate red/green run (not present), the frozen re-pin, and the fixture red/green run." — all three now exist at HEAD (gate + its selftest/replays, `c6207bd` repin, `c1-matrix-final.json`; the landing rerun `c1-matrix-landing.json` is still untracked). **fixed**.
- `DraftSkillSection.md:67` "STATUS: draft complete; … no real-fleet `error` row observed." — still true: `census/round-16/live-fleet-final.json` has 21 rows, both arms rc=0, zero `error` rows, and its own `note` says the live fleet held no r14-refused key. **open but disclosed**; the lesson must not claim a measured live error row.
- `CriticDisclosureR3.md:119` and `RevengeR15Landing.md:202` — "no known failure in this seat's own output. One probe-rule deviation, disclosed below." / "no blocker. One read-only command outside the enumerated allow-list…". Both are process disclosures with no deliverable failure; the R5 audit independently found 19 minor whole-lane reads and voided affected findings. **no counterexample**.

## 4. Residual risk and verification gaps

- Every disposition above is from committed bytes at HEAD; nothing was re-executed. Where a
  seat's claim is about git runtime behaviour (F1/F2/F3/F4 of §1.5, §1.2's 07), I can only
  confirm code shape, not behaviour.
- `--frozen` "clean" is L1's c6207bd claim; I verified value-binding of every pin and the
  record digest, not the checker's verdict.
- `census/round-16/c1-matrix-landing.json` is untracked at HEAD (`git status`), so the landing
  measurement is not yet committed evidence; `c1-matrix-final.json` is tracked.
- The gate would also not detect §1.21 or any §1 line; that is F1, not a rendering issue.

STATUS: ok — 21 non-ok wave-1 STATUS lines dispositioned (6 fixed, 9 partial, 4 open, 2 resolved by landing), 6 cross-cutting findings with minimal patches; no check I ran failed; no lane file edited.

## Commands

Every shell command run, in order, verbatim:

```sh
ls -1 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && for f in *.md; do line=$(grep -n '^STATUS:' "$f" | tail -1); if [ -n "$line" ]; then printf '%s\t%s\n' "$f" "$line"; else printf '%s\t(NO STATUS)\n' "$f"; fi; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -nE '^STATUS: *(FAIL|INCOMPLETE|BLOCKED|PARTIAL|ok)' *.md | cat; echo "---- counts ----"; grep -lE '^STATUS: *(FAIL|INCOMPLETE|BLOCKED|PARTIAL)' *.md | wc -l
ls -1 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ ; echo ---; ls -1 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16 && python3 -c "
import json
d=json.load(open('w1-spec.json'))
print(json.dumps(d,indent=1)[:6000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16 && python3 -c "
import json
d=json.load(open('w2-spec.json'))
print(json.dumps(d,indent=1)[:6000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && wc -l ConnFrontier.md CriticFixtureOverfit.md CriticGateVacuity.md CriticNamespaceWeakening.md CriticNoHarmPreharm.md MutateDirtyFilters.md MutateScanConfig.md RevengeFrozenPin.md RevengeInertKeys.md RevGateSpec.md RevRedaction.md RevR14NamespaceRetention.md RevScanParse.md RevStatusInfoFile.md SentinelCommandExec.md SrcBashSetN.md RevFixtureR16Edits.md ScoutGitHostVersion.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD | grep -E 'round-16|preservation|SOURCES|lessons/round-1[56]' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD | grep -E '^(tools|tests|corpus|skill)' | cat; echo '--- status ---'; git status --porcelain | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n 'GIT_CONFIG_COUNT\|GIT_CONFIG_KEY\|GIT_CONFIG_VALUE\|core.fsmonitor\|core.hooksPath\|GIT_NO_LAZY_FETCH' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== expected.json HEAD ==='; git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json; echo '=== record identity ==='; git show HEAD:tests/fixtures/r15-preservation-frozen/record.json | grep -nE 'measured_commit|sha256|"commit"|"path"' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- log ---'; git log --oneline -8 | cat; echo '--- HEAD blob digests ---'; for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json tests/fixtures/r15-preservation-frozen/expected.json; do printf '%s  %s\n' "$(git cat-file blob HEAD:$p | sha256sum | cut -d' ' -f1)" "$p"; done; echo '--- census digest per commit ---'; for r in c6207bd 7a79dc2 a6ec781 0a70bef; do printf '%s  %s\n' "$(git cat-file blob $r:tools/souji-census.sh 2>/dev/null | sha256sum | cut -d' ' -f1)" "$r"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '1,70p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat cbf688a 0a70bef -- tools/souji-census.sh tests/fixtures/r15-census-config.py census/round-16/run-matrix.py | cat; echo '=== census diff (0a70bef) ==='; git diff cbf688a 0a70bef -- tools/souji-census.sh | head -200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a 0a70bef -- tests/fixtures/r15-census-config.py | head -260
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && for f in RevGateSpec.md RevStatusInfoFile.md RevScanParse.md RevRedaction.md RevR14NamespaceRetention.md; do echo "================ $f"; grep -nE '^(#|##|###|STATUS:)|^\*\*[A-Z][0-9]|^- \*\*[A-Z][0-9]|^\| ?[A-Z][0-9]' "$f" | head -60; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'git-include-cycle\|include-cycle\|r-inc-cycle\|xdg-default\|r-inc-twice\|r-inc-tilde-store\|r-tilde-then-store\|s-fsm-filter' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py; git show HEAD:tools/souji-landing-gate.py | grep -n 'LG-\|STATUS\|FAIL\|INCOMPLETE\|BLOCKED\|PARTIAL\|Seat-reported\|phrase\|quotation' | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | grep -n 'report\|checked_report\|PARSE-TREE\|no-md\|empty\|absent\|could-not-evaluate\|record\b\|measured_commit\|frozen dir\|relative' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | sed -n '300,360p;455,500p;553,600p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '600,720p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n 'protected_fail\|usage_err' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '940,1000p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '790,900p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1000,1050p' | cat -n; echo '=== last-wins map? ==='; git show HEAD:tools/souji-census.sh | grep -n 'CFG_VAL\|last-wins' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '1,120p' RevengeInertKeys.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== HEAD census alternate refs / selftest audit ==='; git show HEAD:tools/souji-census.sh | grep -n 'alternate-refs\|alternates\|source audit\|forbid' | cat; echo '=== fixture alternates ==='; git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'alternates' | cat; echo '=== census diff excludes ==='; git diff cbf688a 0a70bef -- tools/souji-census.sh | grep -n 'exclude).ufo\|check-attr\|ls-files' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n -B2 -A18 'fixture-vacuous\|1729-1731\|selftest source audit\|§3\|## 3' RevengeInertKeys.md | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== when was --alternate-refs audit added ==='; git log -S'--alternate-refs' --oneline -- tools/souji-census.sh | cat; echo '=== 0a70bef audit hunk ==='; git diff cbf688a 0a70bef -- tools/souji-census.sh | grep -n -B6 -A6 'alternate-refs' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '1,114p' CriticNoHarmPreharm.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n 'if \[ -L "\$d" \]\|ignore-submodules\|GIT_CONFIG_GLOBAL\|git-metadata-hardlink' | cat; echo '=== ConnFrontier F2 ==='; cd .ufo/waves/round-16/w1 && grep -n -B4 -A20 'F2' ConnFrontier.md | head -70
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '1,71p' CriticFixtureOverfit.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-preservation-evidence.py | grep -n 'CONFIG_HARM_FAILS\|CONFIG_REFUSAL\|CONFIG_BENIGN\|CONFIG_SAFETY\|REFUSAL_CASES\|"03"\|"07"\|"14"\|r16\|R16' | head -40; echo '=== preserve harm pins 18/20 ==='; git show HEAD:tools/souji-preservation-evidence.py | grep -n -A4 '18\|20' | grep -n 'preserve\|PASS\|FAIL' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -nE '^(#|##|###)|^\| ?[A-Z][0-9]|^### [A-Z][0-9]' RevFixtureR16Edits.md | head -50; echo '=== status ==='; sed -n '230,344p' RevFixtureR16Edits.md | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '100,147p' SrcBashSetN.md; echo '=== ScoutGitHostVersion tail ==='; sed -n '95,140p' ScoutGitHostVersion.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '53,140p' RevRedaction.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SOURCES 2.55/2.56 ==='; grep -n '2\.55\|2\.56' corpus/SOURCES.md | head -20; echo '=== S042 row ==='; grep -n 'S042' corpus/SOURCES.md | head; echo '=== README:47 ==='; sed -n '44,50p' corpus/README.md; echo '=== protected_fail HEAD ==='; git show HEAD:tools/souji-census.sh | sed -n '200,235p' | cat -n; echo '=== text predicate? ==='; git show HEAD:tools/souji-census.sh | grep -n 'protected_text_reaches\|protected_reason_inside' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '1,60p' CriticGateVacuity.md; echo '=== A1/A2 predictions ==='; grep -n -A16 'A1\b\|A2\b' CriticGateVacuity.md | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== frozen README ==='; git show HEAD:tests/fixtures/r15-preservation-frozen/README.md | cat -n | head -40; echo '=== rev-list fallback ==='; git show HEAD:tools/souji-census.sh | grep -n 'rev-list --count\||| printf' | head -10; echo '=== wt-dirty ==='; git show HEAD:tools/souji-census.sh | grep -n 'wt-dirty' | head; echo '=== preserve ids ==='; git show HEAD:tools/souji-preservation-evidence.py | sed -n '320,360p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | sed -n '62,105p' | cat -n; echo '=== parse_script ==='; git show HEAD:tools/souji-landing-gate.py | grep -n -A25 'def parse_script' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== wt flags ==='; git show HEAD:tools/souji-census.sh | sed -n '1125,1175p' | cat -n; echo '=== check_python / check_bash ==='; git show HEAD:tools/souji-landing-gate.py | grep -n -A14 'def check_python\|def check_bash' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && n_md=$(ls *.md | wc -l); n_status=$(grep -l '^STATUS:' *.md | wc -l); echo "md=$n_md status=$n_status"; echo '--- no STATUS files ---'; for f in *.md; do grep -q '^STATUS:' "$f" || echo "$f"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== r14 boundary fixture r-fsm/r-filter coverage ==='; git show HEAD:tests/fixtures/r14-census-boundary.py | grep -n 'fsmonitor\|filter\.' | head -10; echo '=== lesson draft STATUS carry ==='; grep -n 'Seat-reported failures' corpus/lessons/round-16.md 2>/dev/null | head -3; grep -c 'resolved@\|open' corpus/lessons/round-16.md 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== R14NS status ==='; sed -n '250,260p' .ufo/waves/round-16/w1/RevR14NamespaceRetention.md; echo '=== selftest config coverage ==='; git show HEAD:tools/souji-census.sh | awk 'NR>=1590 && NR<=1830' | grep -n 'scan_config\|excludesFile\|attributesFile\|filter\.\|config-unsupported\|status-skipped' | head -20; echo '=== S043 ==='; grep -n '^| S043' corpus/SOURCES.md | head -2; echo '=== gate --report? ==='; git show HEAD:tools/souji-landing-gate.py | grep -n 'add_argument' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/live-fleet-final.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
print(json.dumps(d,indent=1)[:1800])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/live-fleet-final.json'))
print('arms',list(d['arms']))
print('note:',d['note'])
print('not_run:',d['not_run'])
print('identical:',d['rows_identical_excluding_mtime'])
for k,a in d['arms'].items():
    print(k, a['rev'][:7], a['tool_sha256'][:12], a['result'], 'rows',a['row_count'], 'stderr',a['stderr_lines'])
    errs=[r for r in a['rows'] if r[-1]=='error' or 'error' in r[-1]]
    print('  error rows:',errs[:3])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== seat_failure_lines ==='; git show HEAD:tools/souji-landing-gate.py | sed -n '273,300p'; echo '=== stdout_sha256 / TOOL token in gate ==='; git show HEAD:tools/souji-landing-gate.py | grep -n 'stdout\|TOOL' | head -20; echo '=== census hardlink residual header ==='; git show HEAD:tools/souji-census.sh | grep -n 'hardlink\|residual' | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== first token of each STATUS value ==='; grep -h '^STATUS:' *.md | sed -E 's/^STATUS:[[:space:]]*//' | awk '{print $1}' | sort | uniq -c | sort -rn; echo '=== lines matching gate failure vocabulary ==='; grep -inE '^[#*[:space:]]*STATUS[*[:space:]]*[:—][[:space:]]*(incomplete|fail|failed|fails|failing|failure|blocked|broken|partial|harmed|red|unrun|error|regression|known)\b' *.md | cat; echo '=== count ==='; grep -icE '^[#*[:space:]]*STATUS[*[:space:]]*[:—][[:space:]]*(incomplete|fail|failed|fails|failing|failure|blocked|broken|partial|harmed|red|unrun|error|regression|known)\b' *.md | awk -F: '{s+=$2} END {print s}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '210,232p;378,392p' ConnLogConvention.md | cat -n; echo '=== fence parity check ==='; awk 'NR<=221 && /^```/ {n++} END {print "fences before 221:", n}' ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'STATUS: INCOMPLETE' corpus/lessons/round-16.md | head; echo '=== failures section sample ==='; sed -n '39,80p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== STATUS anywhere, not column 0 ==='; grep -nE '(^|[^A-Za-z_-])STATUS[[:space:]]*:' *.md | grep -vE '^[^:]+:[0-9]+:STATUS' | cut -c1-220 | head -20; echo '=== SrcGitCheckAttr line ==='; sed -n '110,118p' SrcGitCheckAttr.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a 0a70bef -- tools/souji-census.sh | grep -n -B3 -A8 'relocat\|\.omp parent\|seed' | head -50; echo '=== HEAD seed code ==='; git show HEAD:tools/souji-census.sh | grep -n -A12 'seed' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '283,310p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '246,300p' | cat -n; echo '=== PI_CONFIG_DIR refs ==='; git show HEAD:tools/souji-census.sh | grep -n 'PI_CONFIG_DIR' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status-skipped\|config-unsupported' SKILL.md corpus/QUALITY.md | head -10; echo '=== SKILL registry rows for gate/audit ==='; grep -n 'souji-landing-gate\|souji-seat-audit\|souji-census' SKILL.md | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- gate ---'; git show HEAD:tools/souji-landing-gate.py | grep -n 'diff-filter\|^FAILURE_STATUS_WORDS\|^    }$\|^)$\|^STATUS_PREFIX_RE\|def seat_failure_lines\|raise EvalError("no .md' | head -12; echo '--- fixture ---'; git show HEAD:tests/fixtures/r15-census-config.py | grep -n '^SOFT_FINDING\|status-skipped\|^def soft_repo\|^def soft_problems\|FL_MIXED_DEGRADE =\|^HARM_CASES' | head -12; echo '--- census ---'; git show HEAD:tools/souji-census.sh | grep -n 'CFG_SOFT_REASON keep\|case "\$rec" in\|PROTECTED_HOME_ROOTS+=("\$pi/agent")\|^status_info_file()\|^load_census()\|status-skipped: filter\|^guard_bound_filters()' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- census symbols ---'; git show HEAD:tools/souji-census.sh | grep -n '^guard_git_surface()\|^guard_worktree_registrations()\|^count_dirty()\|^guard_config_path()\|^protected_fail()\|^guard_path()\|^run_selftest()\|soft=1$\|soft=0 || return\|XDG_CONFIG_HOME\|HOME:-\|:(optional)\|config-unsupported: %s (%s)\|^cfg_soft()' | head -40; echo '--- fixture ---'; git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'fields\[5:\]\|^def case_0[1348]\|^def soft_problems\|^def soft_repo\|^def positive_problems' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'bin changed\|dat changed\|^def case_02\|^def case_04\|mixed-degrade\|r-xdg-default' | head -14; echo '--- census ---'; git show HEAD:tools/souji-census.sh | grep -n '^guard_wt_config()\|git-include-cycle\|-L "\$d/.git"\|-L "\$g"' | head -10; echo '--- gate check_frozen def ---'; git show HEAD:tools/souji-landing-gate.py | grep -n '^def check_frozen_pins\|^def check_carry\|^def is_failure_line' | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1255,1300p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2 && grep -n '62-80\|72-80\|1007\|1235\|791-799\|859-863\|891-895\|1069-1082\|598-601\|527-536\|555-563\|1069-1074\|1590-1830\|944-950\|560-566\|1286-1298\|791-863\|1022-1026\|1157-1160\|989-992\|666\|699-710\|535-541\|944-947\|660, `:947-951\|656\|955\|1069\|1194-1210\|1000-1016' RevWaveOneDispositions.md | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '860,870p;1278,1290p' | cat -n; echo '--- non-namespace protected_fail sites ---'; git show HEAD:tools/souji-census.sh | grep -nE 'protected_fail "(ambiguous-path|unresolved-path|symlink-loop|git-metadata-[a-z]+|git-alternates-[a-z]+|special-path|hardlinked-compare)"' | cat
```

Non-shell reads (no command): `read` of `RevengeFrozenPin.md`, `SentinelCommandExec.md`,
`RevGateSpec.md:39-226`, `RevScanParse.md:82-210`, `RevR14NamespaceRetention.md:85-160,182-232`,
`artifact://32163:raw:3-3` (w1 spec context).
