# Round 16 · w1 · RevengeInertKeys — why r14/r15 refused `core.alternateRefsCommand` and invalid `remote.*.promisor`, and whether r16's inert reclassification holds

Seat: revenger, leaf. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axes: **operability** (does the refusal/acceptance decision keep the fleet census usable without weakening the
protected-namespace fence), calibration (is the stated reason the reason).
Mode: source/byte review only. No census, fixture, selftest or matrix run by this seat; the only runtime numbers
quoted are read from the committed `census/round-16/c1-matrix.json`. All citations for the changed revision were
re-verified against `git show cbf688a:` bytes (tool sha256 `fed43c71…`); the worktree copy of
`tools/souji-census.sh` diverged from that commit while this review ran (worktree sha256 `f7d0686c…`, diff 69+/41−,
net +28), so line citations name the committed bytes, not the moving worktree. No tools installed or upgraded.

## 1. Short answer

The premise needs one split; the two families did not have the same author or the same claim.

- **r14 (`cc21683`) never called these keys inert.** It refused them by key name as an explicitly declared
  unsupported surface: `cc21683:tools/souji-census.sh:505-506` refuses the whole substring list through
  `protected_fail`, and header `:85-88` says these keys "are refused as unsupported (operability boundary, not full
  normal-config support)". `corpus/lessons/round-14.md:92-95` repeats it as an "Explicit C2 restriction" and adds
  "This is not a claim of unchanged support for every Git configuration." The r14 intent was a boundary policy
  (refuse anything not fully analysed), not an execution/effect finding. The later outside closure judged that
  policy net-harmful (`corpus/lessons/round-14-verifier-spotcheck.md:104-106`, routed at `:158-160`) because the
  refusal is value-blind and aborts the whole fleet (`protected_fail` exits 2 at `cc21683:160-165`; discovery
  guards every child in `list_repos` at `:964`; the TSV header prints only after all rows buffer at `:991`).
- **The "never executed / inert" co-claim is r15's, and it lives in the seat reports and in the r15 candidate
  tool's header — not in the r15 fixture.** The r15 fixture (`b410186:tests/fixtures/r15-census-config.py`)
  simultaneously says `core.alternateRefsCommand` is never consumed (":46-47", "census never runs a consumer") and
  refuses any non-empty value (`:1141-1150`, `case_14`), and classifies invalid promisor booleans as
  "could-not-evaluate" and refuses them (`:29-32`, `:1058-1063`, `case_07`). Those refusals are **stale relative to
  the r15 candidate tool committed in the same revision**: `b410186:tools/souji-census.sh:85-88` says "promisor
  markers are therefore admitted, not refused", `:111-116` says `core.alternateRefsCommand` "are inert ... and are
  not refused", and its `scan_config_file` key table (`:731-756`) has branches only for
  include/includeIf/remote.url/filter/core.worktree — both families fall through unrefused. Nothing executed this
  contradiction: the r15 tool does not parse (`census/round-16/c1-matrix.json`, arm `r15-baseline`: `bash -n` rc 2,
  `line 1368: syntax error near unexpected token '}'`; all 20 fixture cases fail).
- **The refusal therefore outlived its rationale by inertia, not by a judgment that the values were dangerous.**
  The r15 fixture relaxed exactly the families that had a *runtime* neutralizing control (`-c
  core.hooksPath=/dev/null`, `-c core.fsmonitor=false`, boundary-resolved excludes/attributes) and kept refusal
  where the only control was "our command set does not consume it" (alternateRefsCommand) or "git itself will
  fail" (invalid promisor). Fail-closed was treated as cost-free; the r14 closure's whole point is that it is not
  (`round-14-verifier-spotcheck.md:104-106`: "Safety-motivated scope changes ... are not no-trade improvements").
- **r16's reclassification is correct for the measured scope and restores pre-harm operability, not a new
  capability.** Judgment in §4, with the two evidence gaps that keep it from being a durable invariant.

## 2. What each layer actually said

### 2.1 r14 `cc21683` — declared unsupported surface

| Evidence | Text / effect |
|---|---|
| `cc21683:tools/souji-census.sh:85-88` | lists include/includeIf, filters, hooksPath, attributes/excludes, `core.alternateRefsCommand`, `remote.*.promisor`, `extensions.partialClone`, worktreeConfig: "refused as unsupported (operability boundary, not full normal-config support)" |
| `:505-506` | one unanchored lowercase `case "$keys"` substring list → `protected_fail "git-config-unsupported"`; the value is never read |
| `:160-165` | `protected_fail` prints `path-protected` and `exit 2` |
| `:964`, `:986`, `:991` | discovery guards each child before rows; `rc=2` re-exits 2; the header is printed only after all rows buffer, so one refused repo yields no TSV |
| `corpus/lessons/round-14.md:92-95` | "Explicit C2 restrictions: repositories with ... alternateRefsCommand, promisor/partial clone ... refuse as unsupported. This is not a claim of unchanged support for every Git configuration." |
| `corpus/lessons/round-14-verifier-spotcheck.md:104-106` | value-blind key refusal of a harmless `core.hooksPath=/dev/null` contracts prior support and aborts all rows; net operability **harmed** |

Consequence: r14's own record is honest about the refusal but wrong about its cost. It is *not* evidence that these
two keys are dangerous to execute; it is evidence that r14 would not analyse their effect.

### 2.2 r15 seats — non-execution established, controls differ

- `GitSourceHooks.md:16` — "`core.hooksPath` is **execution-inert for every command the census runs on a fleet
  repo except `git status`**, and that one invocation already forces `-c core.hooksPath=/dev/null`." Its §4 table
  audits all fleet call sites; the alternateRefsCommand row (`:96-97`) is explicitly "[INFERENCE] from its documented
  'advertising alternate tips' scope; **it remains refused anyway**". `:157` records the durable residual: a future
  git could add a hook to a read-only command; only a uniform wrapper/audit mitigates it.
- `PromisorSafe.md:40` — at r14 the census exported `GIT_OPTIONAL_LOCKS`, `GIT_CONFIG_*`, `GIT_TERMINAL_PROMPT` but
  **not** `GIT_NO_LAZY_FETCH`; "any of these reading a missing tree or blob can trigger `git fetch ...`. That is a
  network and write path inside a 'read-only census'." `:28` (F1 acceptance) — value-aware parse suggested; "Any
  other exit (e.g. 128 on an invalid boolean) = could-not-evaluate or refuse, **never clean**." `:30` (F2) — "do
  **NOT** make `extensions.partialClone=false` benign"; `:63` — `promisor=maybe` → "could-not-evaluate or refused,
  never clean".
- `SpecialConfig.md:27-29` (SC-3) — "every config or special-file refusal aborts the whole fleet as
  `path-protected`"; "**Why this is false provenance:** a non-namespace unsupported config is reported as
  `path-protected`, i.e. as if it had reached the store." `:73` (SC-9) — export `GIT_NO_LAZY_FETCH=1`;
  "Promisor values can then be preserved by effect rather than refused by key."
- `RunnerLimits.md:12` — "Several census git reads fail open or fail to zero"; `:67` (F9) — "census exit 0 does not
  mean a complete census"; `:94` — timeout → could-not-evaluate, never pass.

So the seats supplied exactly the two ideas r16 uses: a call-set audit for alternateRefsCommand, and an env-level
no-lazy-fetch control for promisor. They did **not** supply a reason to keep the refusal.

### 2.3 r15 fixture `b410186` — refusal retained, and contradicted

| Evidence | Text |
|---|---|
| `:13` | "Semantics pinned here (SoujiR15.ConfigRepair lock, reviewer reports)" |
| `:29-32` | "invalid booleans refuse fail-closed as could-not-evaluate" |
| `:46-47` | "empty value is benign; any non-empty command value refuses (**census never runs a consumer**)" |
| `:83-84` | pre-harm arm: "safe cases PASS; the **new refusal controls** FAIL where the guard did not exist yet" |
| `:1058-1063` | `case_07` expects `unsafe_repo(... ("git-config-unsupported","git-config-unparsed"))` → exit 2 + `path-protected` |
| `:1141-1150` | `case_14` refuses `r-altrefs-cmd`, `r-altrefs-exit`, `r-altrefs-bare` with `git-config-unsupported` |
| `b410186:tools/souji-census.sh:85-88`, `:111-116`, `:151` | tool admits promisor markers, treats alternateRefsCommand as inert and not refused, exports `GIT_NO_LAZY_FETCH=1` |
| `b410186:tools/souji-census.sh:161-165` | `soft_fail` is per-repo (sets `CFG_SOFT_REASON`, returns 1), matching its header's per-row `error` promise — the fixture's whole-run exit-2 expectation does not match this either |

That is a three-way inconsistency at one revision: fixture says refuse, tool header says admit, tool guard admits
(and would soft-degrade, not exit 2). The fixture's `case_07` was written as a *safety control to be added*, while
the landed candidate had already removed the key refusal. The r15 closure could not see it: the tool's parse
failure short-circuits every case (`c1-matrix.json` arm `r15-baseline`, 0/20).

### 2.4 r16 `cbf688a` — the reclassification as landed

- Census header `tools/souji-census.sh:101-109`: "Accepted: any core.hooksPath/core.fsmonitor value ... any
  `remote.*.promisor` or `extensions.partialClone` value (every git call carries `GIT_NO_LAZY_FETCH=1`; an invalid
  promisor boolean fails git's own status, giving status-unverifiable as before round 14), any
  `core.alternateRefsCommand` (consumed only when advertising alternate refs, which no census command does)".
- Env control `:145-149`: `export GIT_NO_LAZY_FETCH=1` after the `GIT_*` purge and next to
  `GIT_OPTIONAL_LOCKS/GIT_TERMINAL_PROMPT`.
- Guard `:640-646`: both families have no `case` branch — comment: "Inert for the census, any value ..." — so the
  scan falls through after parsing every key exactly (no substring `case`).
- Degradation path `:555-560`, `:1085-1093`: `cfg_soft` is per-repo; `census_one` emits one
  `repo 0 0 0 0 "" error` row plus `souji-census: config-unsupported: <reason> (<repo>)` and returns before any
  `git -C repo` call; exit stays 0.
- Status degradation `:1135-1137`: a failed status becomes `dirty=0` + `status-unverifiable` (never clean).
- Fixture `:13-26`: "remote.*.promisor values are never refused (07 ... pre-harm status-unverifiable row) and
  core.alternateRefsCommand (any value, 12) is inert for the census and must give accurate rows."
- Fixture `case_07` `:1135-1141` expects `("1","0","0","status-unverifiable")`; `case_12` `:1202-1213` expects
  `CLEAN` for empty/plain plus `single_positive` for cmd/exit/bare; `INERT_SENTINELS` `:842` includes
  `("altrefs","SENT_AR")` and `positive_problems` asserts it on every positive case (`:927`), so "the altrefs
  sentinel must never fire" is actually enforced, not prose.

Measured matrix (`census/round-16/c1-matrix.json`, read-only; not re-run by this seat):

| arm | rev | `bash -n` | shellcheck | r15 config | r14 namespace | selftest |
|---|---|---|---|---|---|---|
| changed | cbf688a | 0 | 0 findings | **20/20**, exit 0 | 12/12 | 38/38 |
| pre-harm | a31642d | 0 | 0 | 12/20 (R15CFG-07 **PASS**, 12 **PASS**) | 2/12 | 36/36 |
| r14-harm | cc21683 | 0 | 0 | 4/20; 07 and 12 **FAIL — exit 2, `path-protected:git-config-unsupported`** | 12/12 | 38/38 |
| r15-baseline | b410186 | **2** (line 1368) | 1 rc, 4 findings | 0/20 | 0/12 | rc 2 |

The two reclassified cases are explicitly *restitution* rows: pre-harm passes them too (`observed_exit=0`,
`observed_finding=none`), and only the r14 key-name arm is red.

## 3. Why the refusal persisted (intent trace)

1. r14 copied the whole non-default config surface into one refusal list to keep the namespace guarantee simple;
   the list was never a per-key effect claim (`cc21683:85-88`, `round-14.md:92-95`).
2. The r15 fixture started from that list verbatim (its docstring `:4-9` is the same key set) and relaxed only
   families whose neutralization could be *stated as a call-site override* (`:22-28` hooks/fsmonitor/attrs/excludes)
   or *observed as a pre-harm row* (valid promisor spellings, `:29-34`). For alternateRefsCommand the only control
   is negative — "census never runs a consumer" — so the fixture refused the command-bearing values to keep the
   property structural. For invalid promisor the fixture took PromisorSafe F1's "could-not-evaluate" wording and
   turned it into the r14 whole-run refusal, which is also the `path-protected` false provenance SpecialConfig
   SC-3 independently flagged.
3. The r15 candidate tool had *already* moved to the effect-based policy (header `:85-88`, `:111-116`; guard
   `:731-756`), but it did not parse, so the fixture never reconciled with it and the closure never measured the
   disagreement. r16 is the first revision where the two artifacts state the same rule.

## 4. Judgment on the r16 reclassification

### 4.1 `core.alternateRefsCommand` — accept, **confidence high for the current command set, medium as a durable invariant**

- Correct: the documented consumer is alternate-ref *advertisement*; the audited census calls
  (`git config --file`, `worktree list`, `for-each-ref refs/remotes`, `rev-list --count`, `status --porcelain`,
  `rev-parse --is-inside-work-tree`) advertise nothing (`GitSourceHooks.md:16`, call-site table §4, alternateRefs
  row `:96-97`). The value is a shell string that is never executed; refusing it aborted the fleet for a key that
  cannot run.
- The claim is now falsifiable: `SENT_AR` is asserted on every positive case (`fixture:842`, `:927`), and the
  matrix shows r14-harm red vs pre-harm/changed green. That is the right shape for an "inert" claim.
- Limits, and they matter for six-month maintainability:
  1. **No fixture repo has `objects/info/alternates`** (all repos are `init_repo`, `fixture:314-325`; no alternates
     setup anywhere). In a repo with no alternate there is nothing to advertise, so the sentinel cannot distinguish
     "no consumer exists" from "a consumer had nothing to do"; its green is consistent with a consumer path being
     present. The only evidence that no consumer runs is the `GitSourceHooks` call-set audit, `[INFERENCE]`. The
     fixture should add one repo with an alternate object store plus `alternateRefsCommand` and the same sentinel.
  2. **No structural guard protects the audit.** The selftest source audit (`census:1727-1732`) only forbids
     `fetch|push|commit|branch|checkout|reset|rebase|prune`. A future `rev-list --alternate-refs`, `upload-pack` or
     any advertising call would silently arm an attacker-controlled shell command, and nothing in the suite would
     go red. `GitSourceHooks.md:113` recommended the uniform override/audit; r16 adopted neither. Minimum durable
     fix: extend the selftest regex to `--alternate-refs` and any advertisement command, and name that invariant in
     the header.
- Not a new capability: the pre-harm arm already passed this family; r16 restores it (`c1-matrix.json`).

### 4.2 invalid `remote.*.promisor` — accept, **confidence high for operability, medium for the safety argument**

- Correct where it matters: the r14 shape was the worst of both — whole-fleet exit 2, no row, and a
  `path-protected` label for a repo that never reached the store (SC-3's false provenance). r16 runs git, lets
  the invalid boolean kill the command git itself parses, and maps the failure to `status-unverifiable` with exit
  0. Matrix: changed and pre-harm both produce `("1","0","0","status-unverifiable")`; r14-harm produces exit 2.
- It satisfies PromisorSafe F1's "never clean" **by outcome, not by census-level evaluation**: r16 deliberately
  does not read the boolean. That is defensible because the bad value is self-defeating (git dies when it parses
  it) and because `GIT_NO_LAZY_FETCH=1` + `GIT_TERMINAL_PROMPT=0` remove the fetch path for the good values; but
  the guarantee is now "git fails somewhere the census maps honestly", which is the weaker class RunnerLimits F3
  already found violated elsewhere.
- Residual exposure introduced by the reclassification: r14 refused these repos, so no git ran in them; r16 runs
  the full counter set. `count_worktrees` (`census:850-854`) and `count_unpushed` (`:856-868`) still fail open to
  `0` (`|| printf '0'`, `grep -c . || true`). A failed `worktrees` read is upgraded to `wt=0` plus the `error`
  flag (`census:1127`), but a failed `unpushed` read is not: if a promisor-induced failure lands on `rev-list`
  while remotes exist and `status` happens to succeed, `unpushed=0` would be a false zero with no `error` flag.
  This is pre-existing (RunnerLimits F3) and not demonstrated reachable for a boolean-parse failure, but it is the
  exact reason F1 asked for a *census-level* classification instead of an abstention. State it as a residual, not a
  measured defect.

### 4.3 `extensions.partialClone` — the r16 change overrides `PromisorSafe.md:30` (F2) and is acceptable only because of the env pin

F2 said do not make `=false` benign because git names a promisor remote "false" and would fetch on missing
objects. r16 accepts every value (`census:105-108`; fixture `case_09` `:1159-1167` expects `false`/empty/`origin` CLEAN) and
relies on `GIT_NO_LAZY_FETCH=1` to cut the fetch. The fixture asserts the env on **every observed git call**
(`spy_git_env`, `:812-822`; `make_spy` logs `ENV\<TAB>GIT_NO_LAZY_FETCH\<TAB>$value` on each invocation, `:328-341`;
`case_08` `lazy_fetch=True`), so the control is measured, not assumed. This is a legitimate replacement of a
value-blind refusal by a stronger runtime control — but it is *conditional*: remove the export and F2's objection
becomes correct again (the fixture would go red, which is the right coupling). Note also that this family, like
promisor, is only exercised on complete repos; an incomplete repo is not in the fixture.

### 4.4 What the r16 matrix does not prove

- No incomplete promisor/partial-clone repo (missing blob/tree) exists in the fixture. `PromisorSafe` F3's required
  case — "a repo with `partialCloneFilter` only and a missing blob must not emit a clean row and must not produce a
  git fetch trace" — is not in the r16 matrix. The fetch path is closed by the global env, so the risk is low, but
  the row-fidelity claim for that input is `[INFERENCE]`.
- No repo combines `objects/info/alternates` with `core.alternateRefsCommand`.
- `case_07`'s comment says "no other row is suppressed", but `single_positive` runs `--root <UNSAFE>/<name>
  --include-root` (one repo, `fixture:1043-1051`); the mixed-fleet non-suppression property is not what that case
  measures. The property itself is covered by the other fleet cases, so this is a comment overstatement, not a
  missing control.

## 5. Calibration defects to reconcile before acceptance

1. **`tests/fixtures/r15-census-config.py:46-47` and `:61-62` still state the pre-r16 rules** ("invalid booleans
   refuse fail-closed as could-not-evaluate"; "any non-empty command value refuses"). The supersession sentence at
   `:13-14` ("supersede the bullets below where they conflict") makes the file self-consistent on a careful read,
   but the bullet list is what a maintainer skims, and it now codifies behavior the fixture asserts against. This
   is the same class as R15-M1/R3 (a stale declaration surviving the landing). Reconcile the bullets to the case
   code; do not rely on the precedence sentence.
2. The r15 fixture's refusal expectations were not merely conservative — they encoded the *opposite policy* from the
   tool landed in the same commit (`b410186` fixture `:29-32`, `:46-47`, `:1058-1063`, `:1141-1150` vs tool
   `:85-88`, `:111-116`, `:731-756`). r16's fixture revision is the reconciliation. Recording this as "r16 reversed
   an r15 safety judgment" would be wrong; there was no operative r15 judgment to reverse.
3. `promisor`/`partialClone`/`altrefs` remain single-input classes (complete repo, no alternates). If L1 wants the
   reclassification to be an admitted capability rather than a restitution row, add the missing-object and
   alternates fixtures named in §4.4.

## 6. Operability verdict

The reclassification is the correct operability move on the r14 closure's own terms: it removes whole-run exit 2
and false `path-protected` provenance for two families that cannot reach a protected path, restores the pre-harm
row for invalid promisor, and adds the missing `GIT_NO_LAZY_FETCH` control that r14 never had. Namespace refusals
and the exit-2 shape are retained (`c1-matrix.json`: r14 namespace 12/12; r15 cases 02/11/17/19 still assert the
protected shape per `fixture:13-17`). It does not weaken the fence; it repairs over-refusal.

It is restitution plus one genuine safety addition (the env pin), not a new capability. The two evidence gaps in
§4.4 and the doc contradiction in §5.1 should be closed before any "inert for all inputs" wording is admitted.

STATUS: r16 fixture docstring still carries the pre-r16 refusal rules at `tests/fixtures/r15-census-config.py:46-47,61-62` (superseded by `:13-14` but not reconciled); the `alternateRefsCommand` inertness proof is fixture-vacuous for the documented alternate-advertisement trigger (no fixture repo has `objects/info/alternates`) and unguarded by the selftest source audit (`tools/souji-census.sh:1729-1731`).

Process disclosure: after the report was first written I corrected two line anchors (`:12-26`→`:13-26`,
`:1135-1143`→`:1135-1141`) with a `python3` in-place rewrite of my own report file instead of the `edit` tool.
That command is listed verbatim in §Commands. No other file was touched, and the rewrite changed only those two
substrings (verified by re-reading the affected lines).

## Commands

Shell commands run by this seat, in order (verbatim; `read`/`grep` tool calls used only the exact paths cited
above and are not shell commands):

```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/ 2>&1 | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -8 && echo ---- && git rev-parse HEAD && echo ---- && ls tests/fixtures/ | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-15/ 2>&1 && echo ---- && ls .ufo/waves/round-15/w1/ 2>&1 | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show --stat cc21683 --oneline | head -40 && echo ===== && git show --stat b410186 --oneline | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E 'alternaterefscommand|promisor|partialclone|hookspath|fsmonitor' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | grep -n -i -E 'alternaterefscommand|promisor|partialclone|hookspath|fsmonitor'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | sed -n '480,535p' | cat -n | sed 's/^/  /'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-census-config.py | grep -n -i -E 'alternaterefs|promisor|partialclone|hookspath|fsmonitor' | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E 'alternaterefs|promisor|partialclone|hookspath|fsmonitor' tests/fixtures/r15-census-config.py | head -100
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-census-config.py | sed -n '1080,1160p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,sys
d=json.load(open('census/round-16/c1-matrix.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print('lane_head',d['lane_head'],'git',d['git_version'])
print('fixtures_sha256',d['fixtures_sha256'])
for a in d['arms']:
    print('ARM',a.get('arm') or a.get('name'), {k:a[k] for k in a if k in ('rev','tool_sha256','exit','summary','cases_passed','cases_total','status')})
print('changed keys', list(d['changed'])[:10] if isinstance(d['changed'],dict) else type(d['changed']))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print('arms type', type(d['arms']), list(d['arms'])[:10] if isinstance(d['arms'],dict) else d['arms'][:2])
print('changed type', type(d['changed']))
if isinstance(d['arms'],dict):
    for k,v in d['arms'].items():
        print(k, json.dumps(v)[:400])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
ch=d['changed']
print('changed keys:', list(ch))
cfg=ch['r15-config']
print('cfg keys:', list(cfg)[:20])
for cid in ('R15CFG-07','R15CFG-12','R15CFG-14'):
    c=cfg.get('cases',{}).get(cid)
    print(cid, json.dumps(c)[:1200] if c else 'ABSENT')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print('changed rev:', d['changed'])
for arm in ('changed','pre-harm','r14-harm','r15-baseline'):
    a=d['arms'][arm]
    print('==ARM',arm,'keys',list(a))
    rc=a.get('r15-config',{})
    if isinstance(rc,dict):
        print(' r15-config keys', list(rc))
        cases=rc.get('cases',{})
        for cid in ('R15CFG-07','R15CFG-12','R15CFG-14'):
            c=cases.get(cid)
            print(' ',cid, json.dumps(c)[:900] if c else 'ABSENT')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm in ('changed','pre-harm','r14-harm','r15-baseline'):
    a=d['arms'][arm]
    cfg=a['r15-config']
    print('==',arm,'rev',a.get('rev'),'sha256',str(a.get('sha256'))[:16],'bash_n',a['bash_n'],'sc',str(a.get('shellcheck_warning'))[:80])
    print('   cfg total',cfg['total'],'failed',cfg['failed'],'rc',cfg['rc'])
    print('   ns',a['r14-namespace'].get('total'),a['r14-namespace'].get('failed'),'selftest',str(a['selftest'])[:200])
    fails=[k for k,v in cfg['cases'].items() if v['verdict']!='PASS']
    print('   cfg fails:',fails)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-census-config.py | sed -n '1000,1085p' | cat -n
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- b410186 setup ---' && git show b410186:tests/fixtures/r15-census-config.py | sed -n '485,505p' | cat -n && echo '--- HEAD setup ---' && sed -n '509,530p' tests/fixtures/r15-census-config.py | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E 'inert|never.executed|never runs|no consumer|alternaterefs|promisor' corpus/lessons/round-14.md corpus/lessons/round-15.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'SENT_AR|sentinel_problems|lazy_fetch|EXEC_SENTINELS|def positive_problems|def single_positive|def unsafe_repo|def refusal_problems' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'cfg_soft|CFG_WT_ENABLED|cfg_skip|config-unsupported|status-unverifiable|status-skipped' tools/souji-census.sh | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'return 1' tools/souji-census.sh | head -40 && echo ---- && grep -n 'guard_git_surface\|guard_git_files()\|guard_git_links()' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | grep -n -i -E 'NO_LAZY_FETCH|promisor|partialclone|alternaterefs|type=bool|get-regexp' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | grep -n -E 'git-config-unsupported|git-config-unparsed|scan_config|guard_git_config|CFG_WT|inert|Inert' | head -40 && echo '---- header 80-120 ----' && git show b410186:tools/souji-census.sh | sed -n '80,120p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | sed -n '700,790p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -A18 '^count_unpushed()\|^count_worktrees()' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'forbidden|subcommand|audit|hook-inert|alternate|fetch|sha256|GIT_NO_LAZY_FETCH' tools/souji-census.sh | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^export GIT_NO_LAZY_FETCH|GIT_NO_LAZY_FETCH' tools/souji-census.sh && echo ---- && grep -n -E 'Explicit C2 restrictions|alternateRefsCommand|promisor' corpus/lessons/round-14.md && echo ---- && grep -n -E 'alternateRefs|promisor|inert|never' corpus/lessons/round-15.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'def spy_git_env|GIT_NO_LAZY_FETCH|def make_spy|SPY|spy' tests/fixtures/r15-census-config.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-census-config.py | grep -n -E 'def case_07|def case_14|def case_12|could-not-evaluate|never runs a consumer|any non-empty'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '806,830p' tests/fixtures/r15-census-config.py | cat -n && echo '--- b410186 case_12/14 ---' && git show b410186:tests/fixtures/r15-census-config.py | sed -n '1125,1150p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'def init_repo|alternates|missing|prune|--objects|blob' tests/fixtures/r15-census-config.py | head -40 && echo ---- && sed -n '300,326p' tests/fixtures/r15-census-config.py | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'def case_07|def case_12|Round-16 revisions|remote\.\*\.promisor values are never|alternateRefsCommand \(any value' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | grep -n -E 'refused as unsupported|declares include|core.alternaterefscommand|protected_fail "git-config-unsupported"' | head -10 && echo ---- && sed -n '1725,1735p' tools/souji-census.sh | cat -n && echo ---- && sed -n '88,98p' corpus/lessons/round-14.md | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-15/w1 && grep -n -E 'execution-inert|remains refused anyway|future git version|never executed|inert' GitSourceHooks.md | head -20 && echo ---- && grep -n -E 'Any other exit|could-not-evaluate|GIT_NO_LAZY_FETCH is the write-free|unmitigated|do NOT make' PromisorSafe.md | head -20 && echo ---- && grep -n -E 'preserved by effect|aborts the whole fleet|false provenance|GIT_NO_LAZY_FETCH=1' SpecialConfig.md | head -20 && echo ---- && grep -n -E 'fail-open|fail to zero|exit 0 does not mean|124 or 137' RunnerLimits.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | grep -n -E '^protected_fail\(\)|^list_repos\(\)|^emit_census\(\)|guard_git_surface "\$repo"|if \[ "\$rc" = 2 \]' | head -12 && echo ---- && git show cc21683:tools/souji-census.sh | sed -n '155,170p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1135,1145p;1202,1214p' tests/fixtures/r15-census-config.py | cat -n && echo '---- b410186 tool contradiction ----' && git show b410186:tools/souji-census.sh | sed -n '84,90p;111,116p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | sed -n '955,995p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-census-config.py | sed -n '80,92p' | cat -n && echo '---- soft_fail ----' && git show b410186:tools/souji-census.sh | grep -n -A6 '^soft_fail()'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'invalid booleans|any non-empty|any value,|never refused|supersede the bullets' tests/fixtures/r15-census-config.py | head -12 && echo ---- && sed -n '12,27p' tests/fixtures/r15-census-config.py | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def case_09' tests/fixtures/r15-census-config.py && grep -n 'def case_08' tests/fixtures/r15-census-config.py && sed -n '1,8p' .ufo/waves/round-16/w1/RevengeInertKeys.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re,io
p='.ufo/waves/round-16/w1/RevengeInertKeys.md'
s=open(p,encoding='utf-8').read()
s=s.replace('Fixture `:12-26`:','Fixture `:13-26`:')
s=s.replace('`case_07` `:1135-1143`','`case_07` `:1135-1141`')
open(p,'w',encoding='utf-8').write(s)
print('ok')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh tests/fixtures/r15-census-config.py && echo ---- && git show cbf688a:tools/souji-census.sh | sha256sum && git show cbf688a:tests/fixtures/r15-census-config.py | sha256sum && echo ---- && git diff --stat cbf688a -- tools/souji-census.sh tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -n -E 'Accepted: any|export GIT_NO_LAZY_FETCH|Inert for the census|^cfg_soft\(\)|config-unsupported: %s|status-unverifiable\)|^count_worktrees\(\)|^count_unpushed\(\)|forbidden git subcommand|fetch\|push\|commit' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a -- tools/souji-census.sh | grep -E '^[-+].*(promisor|alternaterefs|alternateRefs|NO_LAZY|inert|Inert)' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '638,650p' | cat -n && echo ---- && git show cbf688a:tools/souji-census.sh | wc -l && echo ---- && git diff cbf688a -- tools/souji-census.sh | grep -c '^+'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c '^```' .ufo/waves/round-16/w1/RevengeInertKeys.md && tail -3 .ufo/waves/round-16/w1/RevengeInertKeys.md && wc -l .ufo/waves/round-16/w1/RevengeInertKeys.md
```
