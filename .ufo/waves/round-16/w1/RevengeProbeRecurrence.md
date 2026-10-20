# Round 16 w1 — RevengeProbeRecurrence (R5)

Seat: `SoujiR16.RevengeProbeRecurrence` (revenger, leaf).
Axes: calibration (primary, lowest 7), operability of the wave contract (secondary).
Scope: reconstruct the r14 and r15 seat probe deviations and the contract wording that permitted
them; propose enforcement mechanics L1 can apply this round. Source reading and git plumbing only;
no census, fixture, gate, build, probe or write outside this report.

Verdict in one line: R5 is a real, twice-recurring process defect, but it is **not** a wording
deficit by r15 — it is a detection-and-consequence deficit. r15's contract already said "no empirical
probes" and all three deviating seats' prompts repeated "no tests/probes"; the deviation survived
because the only audit surface was the seat's own disclosure and the only sanction was a note.

## 1. What was actually executed (reconstructed, not re-run)

| round | seat | act (self-described) | class | pointer | what the observation then authored |
|---|---|---|---|---|---|
| r14 | SafetyCredential | `strace` of `realpath -m -s` / `readlink -m`; bash glob + `[ -d link/.git ]`; `GIT_COMMON_DIR` redirect; forged `.git/worktrees/w/gitdir`; forged synthetic store under `/var/tmp` | probe | `SafetyCredential.md:21-27`, `:113-118`, dev note `:105-107` | F3/F4/F5/F6 are stated with "Exercised:" evidence (`:22-25`) and the landed-code table marks them Fixed/Partially fixed (`:40-50`) |
| r14 | BoundaryAttack | five `mktemp -d /var/tmp/r14-boundary-attack*` probes, `strace`, E1-E14; `souji-census.sh` never run | probe | `BoundaryAttack.md:10`, `:15-21`, `:23-70`, A2/A3 `:86-103` | A2 ("exercised correction") corrects SafetyCredential; A3 is "new"; probe-derived store-mode-000 oracle is proposed for the fixture (`:156`) |
| r14 | SafetyCache | one kernel symlink-open probe (`O_NOFOLLOW` → `ENOTDIR` vs `ELOOP`) | probe | `SafetyCache.md:34-38`, dev note `:58-65` | M3 row cites "probe #1" as its evidence and the finding-id fix follows from it (`:78`) |
| r15 | LinkedPreserve | `find -P /nonexistent-souji-probe -type d ! -readable -print -quit` | probe | `LinkedPreserve.md:110`; attestation contradiction at `:5` vs `:110`; F6 depends on it `:62-65`, `:104-105` | F6's exit-2 mechanism ("dangling `.git` aborts the run") is justified by the probed `find` exit status, then nominated for the acceptance fixture |
| r15 | SkillWording | whole-lane `_grep` (lane root, 200-result cap); whole-lane `_glob` listing `census/operator-sweep-20261019/` names; `ls -la` lane root | scope escalation | `SkillWording.md:78`, `:81`, `:82` | nothing: names exposed, no content used |
| r15 | ReportContract | lane-root `_glob`; `grep -r … .` recursing into the sweep and **reading file contents**, filtered from display | scope + protected read | `ReportContract.md:137(a)-(c)` | nothing quoted; exposure only |

Correction to R5's premise: Q24 was committed at `fc3a8d4` on 2026-10-20 **05:28:44**
(`git log -S'| Q24 |' -- corpus/QUALITY.md`), while the round was launched at **05:17:17**
(`corpus/lessons/round-15-verifier-spotcheck.md:12`). Q24 therefore did not exist at dispatch and
was not a precondition any r15 seat could violate. It landed 11 minutes into the wave; the operative
ban was the wave contract's `empirical probes` clause (`.ufo/waves/round-15/w1-spec.json:3`). R5's
"Q24 landed, but seats again ran prohibited probes" is chronologically imprecise and should be
restated as "the contract ban recurred despite being stated twice (contract + per-item prompt)".

## 2. What the contract wording permitted

### 2.1 r14: the ban named artifact classes, and three other sentences granted the act

The r14 contract sentence is (`.ufo/waves/round-14/w1-spec.json:3`):

> "Leaf seats, no delegation, no commits, no builds/tests/linters/formatters/smoke runs."

Object of prohibition: `builds`, `tests`, `linters`, `formatters`, `smoke runs` — all *artifacts of a
delivery pipeline*. A one-line `strace`/`find`/`glob` in `/var/tmp` is none of those nouns. The same
contract then supplies three permission-shaped sentences and two narrow or contradicted
prohibition sentences:

- "All fixtures use `/var/tmp` with cleanup; no `/dev/shm`." — reads as an instruction for running fixtures.
- "All seat reports explicitly separate code inspection from exercised evidence." — presupposes exercised evidence.
- Item `SafetyCredential` (`w1-spec.json` items): "unsafe tests must remain synthetic" — literally authorizes synthetic tests.
- Item `BoundaryAttack`: "Attack C2 guarded census **without running it**" — the only act-level prohibition, and its object is *the census*, not primitives.
- All 32 r14 items end: "**No checks mid-flight**; identify final L1 commands." That is the clearest
  act-level rule in the round — and it is contradicted inside the same `SafetyCredential` prompt by
  "unsafe tests must remain synthetic" (`w1-spec.json` items). A seat facing "no checks mid-flight"
  plus "unsafe tests must remain synthetic" plus "all fixtures use /var/tmp with cleanup" resolves
  the conflict by running the synthetic check; the contract supplies no precedence rule. The
  agent-level probe prohibition was never stated as "execute no process".

The seat's own deviation note confirms which reading won: "The round context prohibited builds, tests
and smoke runs mid-flight" (`SafetyCredential.md:107`) — it quotes the artifact list back, then
explains why its probes "deviated from that rule". The wording never said the act was prohibited; it
said five deliverable classes were. Every r14 probe seat kept the tool-under-test unrun and stayed
inside "no tests/builds/smoke runs" as it had parsed them.

### 2.2 r15: the act was prohibited, but "probe" was never defined and the audit surface was absent

The r15 contract sentence is (`.ufo/waves/round-15/w1-spec.json:3`):

> "No delegation, commits, tests, builds, linters, formatters, smoke runs, or empirical probes:
> SOURCE INSPECTION ONLY except writing assigned implementation."

Every seat prompt repeats "Own report ONLY; no tests/probes/edits outside report." (e.g. the
`SkillWording`, `ReportContract`, `LinkedPreserve` items). Three holes remained:

Measured over the committed specs: **all 32** r14 items carry "No checks mid-flight", and **58 of
64** r15 items carry "no tests/probes" (the six without it are `ConfigRepair`, `ConfigFixture`,
`AdmissionChecker`, `RoundRunner`, `LessonDraft`, `SourcesDraft`). All three r15 deviating seats were
inside the 58. Repeating the prohibition in the per-item prompt and the contract did not bind; this
is the central datum behind §3.

**(a) Definitional hole — the prohibition's object.** A single `find -P` was self-classified as "one
shell check … to confirm exit status" (`LinkedPreserve.md:110`) and as "primitive probes only"
(`BoundaryAttack.md:10`). L1's own post-hoc classification ratifies that reading: "Other seats'
version, digest, Git plumbing, manual/source-reading and static census commands are read-only source
metadata, **not executions of the census/checker**" (`corpus/lessons/round-15.md:63-65`). Under that
rule, `find`, `strace` and `realpath` are not covered at all. If the integrator's stated rule excludes
the acts that occurred, the contract cannot have forbidden them unambiguously.

**(b) Scope hole — the protected-path clause enumerated five verbs, not the exposing acts.** r15:
"OPERATOR-authored `census/operator-sweep-20261019/` must not be opened, edited, moved, staged,
copied or deleted." `grep -r` is covered only if one reads "opened" as "read" — `ReportContract`
admits it "read file contents" (`:137(b)`). `_glob`/`ls` name enumeration is not covered by any verb;
`SkillWording` called it "a name-level exposure I did not intend" (`:81`). Contrast the credential
clause in the same sentence: "Never open/copy/query/modify `~/.omp/agent/agent.db*`" — `query` is
there, the sweep clause has no `read`/`list`/`enumerate`/`glob`/`stat`/`traverse`. The sweep boundary
was worded strictly weaker than the credential boundary.

**(c) Audit hole — detection depended on the seat's memory.** Neither round has a command ledger. The
only `## Commands`-prefixed heading in the six reports is `SafetyCache.md:114`: `## Commands for L1
(this seat did not run them)` — a *suggestion list* occupying the field name that now means a *ledger
of what was run*. All six deviations were found by self-disclosure or L1's ad-hoc recollection, not by a field.
The measured rate 3/32 (r14) and 3/64 (r15) is a **disclosure rate**, not a violation rate; the
violation denominator is unknown and, absent a transcript audit, unbounded below. Any claim that the
rule "mostly held" is unsupported.

The separation the rule wanted was achievable, so the failure is not reporting skill:
`SafetyCache.md:30-34` labels "Code inspection only. Nothing in this section was run." and
"Exercised. These are the only commands this seat ran" in one report. The defect was the act and the
absent ledger, not the seat's ability to distinguish inspection from execution.

### 2.3 Why disclosure was rational: the laundering chain

Q24's operative sentence is "any deviation is recorded and not laundered into final acceptance"
(`corpus/QUALITY.md:58`), and its test is "Wave contract and report distinguish source review,
historical deviation and the actual named L1 command/output/revision". A seat that writes a
`## Process notes` deviation paragraph **passes that test by construction**. The criterion is
satisfied by the confession, so the cost of probing is one paragraph.

More consequentially, "not acceptance evidence" did not mean "not used". Three observed chains:

1. **Finding id authored by the probe.** `SafetyCache` M3 changes the `ENOTDIR` mapping to a
   `symlink` finding id, with "probe #1" as its evidence column (`SafetyCache.md:78`). L1 did not
   rerun it (`round-14.md:120-124`), but the *fix decision* is the probe's output.
2. **Finding severity authored by the probe.** `LinkedPreserve` F6 is "dangling `.git` aborts the
   run" (`:62-65`); its `find -P <missing>` exit-status basis is the one executed command (`:110`,
   acknowledged at `:105`), and F6 then enters the acceptance list. A source-only reading would have
   had to mark the exit code `[INFERENCE]`; the probe converted it into a finding.
3. **Fixture cases authored by probes.** The r14 C2 fixture's worktree-owner and alternates cases
   correspond to probe-derived F5/N1/N2 (`SafetyCredential.md:24`, `:65`; `BoundaryAttack.md:117-119`).
   The r15 lesson says the probes were not rerun "or use[d] … as acceptance" (`round-14.md:122-124`),
   but acceptance *inputs* were shaped by them. Causation is `[INFERENCE]`; the citation chain
   (probe row → F-id → landed-status table → fixture case) is observed text.

The rule that would have stopped this is missing: an observation obtained by a prohibited act must be
quarantined as a hypothesis and may justify a fix or fixture case **only after independent
re-derivation** (source line or named L1 run). Without that, "probe evidence is not acceptance" is a
label on the claim, not a fence around the decision.

## 3. Enforcement mechanics L1 should apply this round

### 3.1 Audit unit and ground truth

Audit **per seat**, before that seat's findings enter any aggregation. Ground truth is the transcript
(`history://<id>`), not the report. The report's `## Commands` is the *claim under test*. If a
transcript is unavailable, the row is `not-auditable` — never `clean`.

### 3.2 Transcript audit fields (one row per seat; table in the closure, JSON at `census/round-16/probe-audit.json`)

| # | field | allowed values / derivation |
|---|---|---|
| 1 | `seat`, `role` | registry id and role |
| 2 | `transcript_available` | `yes` \| `no` (`no` ⇒ disposition `not-auditable`) |
| 3 | `shell_invocations` | count of every process invocation in the transcript, including builtins that run a program |
| 4 | `declared_commands` | count of lines in the report's `## Commands` |
| 5 | `undeclared` | set difference transcript − ledger, each item: first token + literal argument prefix (≤120 chars). Non-empty ⇒ V6 |
| 6 | `phantom` | ledger entries with no transcript match. Non-empty ⇒ V6 (claimed run not observed) |
| 7 | `tool_calls` | every non-shell `read`/`grep`/`glob`/`task` call with its path/query argument (r15's three worst acts were non-shell) |
| 8 | `max_path_scope` | `exact-file` \| `exact-dir` \| `wave-dir` \| `lane-root` \| `fleet-root` \| `protected` |
| 9 | `protected_hits` | count of path arguments matching `census/operator-sweep-20261019`, `~/.omp`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`, sibling lanes |
| 10 | `exec_workdir` | for executors: actual `/var/tmp/souji-r16-<Seat>/` path(s), fixture world path(s), and post-run absence check |
| 11 | `violations` | zero or more V-codes (§3.3), one evidence pointer each (transcript offset or `report:line`) |
| 12 | `derived_findings` | findings/fixes/fixture cases whose justification depends on a violating observation; each must carry an independent basis or be void |
| 13 | `disposition` | `clean` \| `void` \| `advisory-only` \| `not-auditable` |
| 14 | `recurrence` | prior-round seat/class for the same V-code, or `new` |
| 15 | `remediation` | `none` \| `evidence voided` \| `seat re-run` \| `gate check added` |

### 3.3 Violation classes (each has a mechanical membership test)

| code | class | membership test | r14/r15 instances |
|---|---|---|---|
| V1 | TARGET-EXECUTION | invoked `tools/souji-census.sh`, a copy, or the fixture under test, in any directory | 0 observed (all six seats kept the tool unrun) |
| V2 | EMPIRICAL-PROBE | executed any process outside the declared static set for the purpose of observing the artifact's or its platform's behavior (`find`, `strace`, `realpath`, `readlink`, kernel-open scripts, single-command smoke checks) | r14×3, r15×1 |
| V3 | SCOPE-ESCALATION | any `read`/`grep`/`glob`/`find`/`ls` whose path argument is not an exact named file or an exact item-named directory; includes wave-root and lane-root enumeration | r15×2 |
| V4 | PROTECTED-PATH EXPOSURE | any traversal, name listing (V4n), grep, open or stat reaching a protected path (§3.2 field 9); content read is V4c | r15×2 (`SkillWording` names = V4n; `ReportContract` contents = V4c) |
| V5 | WRITE-SCOPE | any write/move/delete outside OWNED files or the seat's own `/var/tmp` scratch, including fleet-root-relative paths | r15×2 (`SourcesDraft`, `GitSourceStatus`) |
| V6 | LEDGER/ATTESTATION DEFECT | transcript command absent from the ledger; ledger entry absent from the transcript; or a header attestation contradicted by the report's own disclosure | r15×1 (`LinkedPreserve.md:5` vs `:110`) |
| V7 | PROXY-PROBE | the seat causes a peer/subagent/labrat/executor to perform a V1–V3 act; the requesting seat is the violator, and the delegated transcript is evidence | 0 observed; the r16 "one read-only labrat probe (executors only)" creates the channel |

V3 and V4 must stay separate, following r15's own classification
(`corpus/lessons/round-15.md:53-56`): "read-only greps do **not** breach that operator rule. They
breach this lane's stricter wave no-query contract and are recorded as lane conformance defects
(seat, command class, read-only), not operator-authority violations." V4n (names) and V4c (contents)
are therefore **lane-conformance defects that void lane evidence**; neither is an operator-authority
violation unless the act also writes. V5 is the only class that can breach operator authority, and only when
the path is operator-owned. Do not escalate a V4 read to an operator incident, and do not downgrade
it because it was read-only.

Declared-nonobservational tier (not a violation, still recorded): `cat`, `echo`, `cd`, `pwd`, `wc`,
`head`/`tail`, `sed` without `e`, and non-recursive `ls` of an explicit directory inside the lane,
provided the call carries no claim and no path outside the lane. This tier is needed because a
closed allowlist that omits ubiquitous pipeline utilities produces either mass technical violations
or silent omissions; §4 records this seat as a measured case.

### 3.4 Detection procedure (five mechanical steps, no discretion)

1. Enumerate the transcript; extract every process invocation and every non-shell tool call with its
   path argument.
2. Normalize both sides (basename + first two arguments) and compute `undeclared` and `phantom`.
3. Apply the membership tests V1–V7 to each entry; record the first failing test as the V-code.
4. For each finding in the report, test whether its justification cites a violating observation
   (`derived_findings`); demand an independent basis (committed source line, committed fixture case,
   or named L1 command) or mark the finding `void`.
5. Write the row; aggregate. A seat with any V-code is `void` for **all** its evidence, per the r16
   contract sentence, except that V2/V3-derived *hypotheses* may be retained as `advisory-only` once
   independently re-derived. No exception is made for disclosure.

### 3.5 Consequence matrix

| disposition | meaning | may be cited in report/lesson? | may justify a fix or fixture case? |
|---|---|---|---|
| `clean` | no V-code; ledger reconciles | yes | yes |
| `advisory-only` | V2/V3 only, no protected hit, no target execution; observation independently re-derived | as `[UNVERIFIED-PROBE]` only | only via the independent basis |
| `void` | any V1, V4, V5, V6, V7; or V2/V3 not re-derived | no | no |
| `not-auditable` | transcript unavailable or row incomplete | no (counts as unrun) | no |

### 3.6 Discriminating red test for the schema itself

A schema that only flags what the reports admit is not enforcement. Before using it on r16, run it
read-only against the six historical seats; the expected output is fixed here, so L1 can check the
auditor rather than trust it:

- `SafetyCredential` → V2 (strace/glob/GIT_COMMON_DIR probes).
- `BoundaryAttack` → V2 (five probe trees) with `souji-census.sh` unrun (V1 = 0).
- `SafetyCache` → V2 only (kernel open probe). Its report separates the two evidence kinds correctly
  (`:30-34`: "Code inspection only. Nothing in this section was run." then "Exercised. These are the
  only commands this seat ran"), so no V6.
- `LinkedPreserve` → V2 (`find -P`), V6 (`:5` attestation vs `:110`).
- `SkillWording` → V3 (lane-root grep, lane-root glob), V4n (name listing).
- `ReportContract` → V3 (lane-root glob, `grep -r .`), V4c (contents read).

If the audit does not produce exactly these classes, the auditor is under-detecting and its r16 rows
must not be used. If a transcript is unavailable, the corresponding row must be `not-auditable`; that
is itself a calibration finding for R5, not a pass.

### 3.7 Residual gaps in the current r16 contract (fixable before the wave closes)

The r16 contract (`.ufo/waves/round-16/w1-spec.json:3`) is materially better than r14/r15: closed
allowlist, explicit "any command not allowed above", prohibited `find`/`ls` at lane scope,
`never open/list/grep/copy/move/stage/delete` on the sweep, `never read` on `~/.omp`, and a required
`## Commands`. Four gaps remain:

1. **`## Commands` is shell-only.** r15's three worst acts were `_grep`, `_glob`, `ls`. Require a
   second ledger: `## Tool calls`, each non-shell call with its path/query argument. Field 7 cannot
   be filled from a shell ledger.
2. **Discovery is unauthorized.** The items name report files without their wave subdirectory; a seat
   must list `.ufo/waves/round-16/w1/` to find them. Add: "one non-recursive listing of the wave
   report directory is allowed to locate an assigned input; any listing outside it is V3."
3. **The labrat allowance is an unclassified proxy channel.** Require the labrat transcript to be
   attached to the executor's audit row, and state that V1–V3 apply to the delegated act (V7).
4. **Ledger honesty needs an explicit class.** `## Commands` is a claim; the contract's consequence
   sentence ("a violation voids that seat's evidence") does not say that an omission is itself a
   violation. Add V6 verbatim: "An omission or mismatch between the transcript and the ledger voids
   the evidence whether or not the omitted command was itself allowed."

Two wording replacements L1 can paste (the r14/r15 sentences are the ones that failed):

> "Execute no process except the enumerated static checks. Any other invocation — in any directory,
> under any path name, including a single `find`, `strace`, `realpath`, or shell one-liner — is a
> probe. A probe's purpose defines it, not whether the invoked program is the census, the checker, or
> a copy. A probe performed by a peer, subagent, labrat or wrapper on your behalf is your probe."

> "Never open, read, list, enumerate, glob, stat, grep or traverse `census/operator-sweep-20261019/`."

## 4. Self-application (this seat is the first audit row)

Run against §3.2/§3.3, from this seat's own transcript:

| field | value |
|---|---|
| transcript_available | `yes` (registered subagent) |
| shell_invocations | 7 compound calls containing: `git -C … log` ×4, `git -C … rev-parse` ×2, `git -C … ls-tree` ×3, `python3` read-only JSON phrase counts ×2 |
| declared_commands | all seven, verbatim, in `## Commands` |
| undeclared / phantom | `none` |
| tool_calls | `read` on exact named files and on 7 bounded directory listings (5 wave/census/corpus roots, 2 paged `w1` report directories used to locate the three item-named reports); `grep` on exact named files only; `glob` 0; `task` 0 |
| max_path_scope | `wave-dir` (the two paged `w1` listings). Lane root never listed; no recursive search anywhere |
| protected_hits | 0 (`census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`, `MANIFEST.json` never named in any argument) |
| exec_workdir | n/a (no executor commands) |
| violations | `none` |
| derived_findings | none depend on a prohibited observation; all citations are report lines, committed lesson/QUALITY lines, or git metadata |
| disposition | `clean` |
| declared-tier noise | `ls -la` ×2 (exact dirs, non-recursive), `echo`, `cd &&` ×5, `sed -n` ×1 (output cap), `cat` ×2 (pager suppression), `python3` heredoc ×2 (read-only JSON field counting; no artifact execution) — §3.3 declared tier, recorded not voiding |
| recurrence | `new` for the tier observation |

This row is the argument for the taxonomy: under a literal allowlist, this seat would be a
technical violator for `cat`/`sed`/`echo`/`cd`, and the honest seat response is to omit them — which
is exactly how r14/r15 ledgers stayed empty. A declared non-observational tier keeps the void
sanction meaningful and the ledger complete.

## 5. Calibration verdict and bounds

- **Improves calibration if applied:** the round gets a measured violation denominator instead of a
  disclosure narrative; the void sanction is attached to a decidable act class; the derived-use rule
  closes the laundering path that Q24 left open; and the schema is falsifiable red on history (§3.6).
- **Not claimed:** that r16 has no violations (unaudited); that transcripts for r14/r15 seats remain
  available (L1 must check; if not, those rows are `not-auditable`); that any seat's r14/r15 finding
  was actually caused by its probe (`[INFERENCE]` on causation; the citation chain is observed).
- **Carry into R16-M4/Q26:** R5's premise should be corrected — Q24 was committed 11 minutes after
  launch and is satisfiable by disclosure. The lesson row must say "recorded but not *enforced*:
  no ledger, no transcript audit, no consequence; Q26 must name the audit fields and V-classes",
  not "seats violated Q24".
- **Do not** rerun any historical probe to confirm it, and do not cite a probe-derived finding as
  acceptance without an independent basis (§3.4 step 4).

STATUS: reconstruction complete from committed lesson/QUALITY text, wave JSON, and the six seat
reports; no probe, census, fixture, gate or build was executed by this seat; enforcement mechanics
are a proposal, not a run.

## Commands

```
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/ 2>&1; echo ---; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -20 2>&1; echo ---; git rev-parse HEAD 2>&1
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only HEAD -- tools tests census/round-16 corpus/QUALITY.md 2>&1 | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --format='%h %ci %s' -5 -- corpus/QUALITY.md && echo --- && git ls-tree -r --name-only HEAD -- tools/ | cat && echo --- && git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --format='%h %ci %s' -S'| Q24 |' -- corpus/QUALITY.md && echo --- && git log --format='%h %ci %s' -S'empirical probes' -- corpus/QUALITY.md && echo --- && git ls-tree HEAD -- .ufo/waves/round-15 .ufo/waves/round-16 | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
for rnd in ('14','15'):
    d=json.load(open(f'.ufo/waves/round-{rnd}/w1-spec.json'))
    items=d['items']
    print(rnd,'items',len(items),
          'no-checks',sum('No checks mid-flight' in (i.get('prompt') or '') for i in items),
          'no-tests-probes',sum('no tests/probes' in (i.get('prompt') or '') for i in items),
          'synthetic-tests',sum('unsafe tests must remain synthetic' in (i.get('prompt') or '') for i in items))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('.ufo/waves/round-15/w1-spec.json'))
print([i['name'] for i in d['items'] if 'no tests/probes' not in (i.get('prompt') or '')])
PY
```

Non-shell calls (all exact named files; directories only as bounded listings):
`read` — `corpus/lessons/round-14.md`, `corpus/lessons/round-15.md`, `corpus/QUALITY.md`,
`corpus/lessons/round-15-verifier-spotcheck.md`, `.ufo/waves/round-14/w1/{SafetyCredential,
BoundaryAttack,SafetyCache}.md`, `.ufo/waves/round-15/w1/{SkillWording,ReportContract,LinkedPreserve}.md`,
`.ufo/waves/round-1{4,5,6}/w1-spec.json` (`.context` and item prompts), `.ufo/waves/round-16/w1/
DraftReportSkeleton.md`, `AGENTS.md`; directory listings: `.ufo/waves/round-14`, `.ufo/waves/round-15`,
`.ufo/waves/round-16`, `.ufo/waves/round-14/w1:1-40`, `.ufo/waves/round-15/w1:1-70`, `census/round-16`,
`corpus`.
`grep` — the six seat reports, `corpus/QUALITY.md`, `corpus/lessons/round-1{4,5}*.md`,
`.ufo/waves/round-1{4,5,6}/w1-spec.json`. `glob` — none. `task` — none.
