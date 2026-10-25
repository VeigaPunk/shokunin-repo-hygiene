author: hyaku closure (non-author integrator, @m_strong)

# Round 14 — non-author closure and verifier spot-check

## Decision

**Status: ok; admitted: false; verdict: rejected-harmed.** This is a substantive, committed report, not a marker. C1 verifies within declared-byte/synthetic-consumer scope. C2's namespace improvement verifies, but its disclosed value-blind Git-configuration refusals contract existing operability. Honest disclosure does not satisfy the protocol's no-trade admission rule. No lane-authored file or SHONEN box is changed by this closure.

Reviewed before `a31642d14006830ec62edf40b0354c3699728c4a` and after `69c1604474494fc2746e091fd545c5d283c02cba`. Read-only auxiliary reviews: `CloseSoujiR14.SoujiR14GateEvidence` (reviewer, C1) and `CloseSoujiR14.SoujiR14ConfigNoHarm` (critic, C2). This integrator owns the verdict; neither seat executes the lane's gates.

## Step-1 conformance

Commands executed from the fleet-root session, using the absolute repository paths:

```sh
git -C /home/vgpnk/Projects/shokunin log --format='%an %H' -- .ufo/reports/round-14/souji.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-list --count '@{u}..HEAD'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
```

Observed:

```text
souji-shokunin 1e0aaa31c96a277ee54bb855a1b0ca585ad9e3df
?? census/operator-sweep-20261019/
0
69c1604474494fc2746e091fd545c5d283c02cba
```

The sole untracked directory is operator-authored by explicit assignment; it was not opened, copied, modified, staged or deleted. There was no uncommitted lane round work at review start. The report has all six required sections in order and four author `[~]` SHONEN lines matching the four checklist boxes. It names real source, evidence, LOG bindings and committed work.

For each of `a31642d14006830ec62edf40b0354c3699728c4a`, `48f8945780adeb259cff0ef7dd9b7efbf1544ec7`, `552cae4204b3ab818419ad8adbfef3a4da29a3e0`, `42d0b7b177b05889589009d94314cb3d7231ac25`, and `69c1604474494fc2746e091fd545c5d283c02cba`, executed `git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor <hash> HEAD`: all exited 0. The four round commits carry `souji-shokunin <souji@shokunin.local>`. Their final commit timestamp is 2026-10-20T05:02:35-03:00; the lane-authored report commit is 05:04:43-03:00, after lane work. The checked upstream-ahead count was zero.

The dispatched prompt was read completely. Its mission binding, distinct 1–3 claims, lowest-axis rule, frontier step, batched L2 floor, report/SHONEN/hash requirements, lane write scope, commit-before-report, push scope and L0 channel are present. A plain committed-text comparison after substituting fleet root/lane/round found **template sections 2–5 exact: true**. The round's frozen campaign addendum allows 32–64-seat waves; `w1-dispatch.json` records 32 spawn/0 resume, policy waveMinLanes 32/waveMaxLanes 64. The report accounts for the L1 planner mapping. Later campaign wave sizes are not applied retroactively. Disclosed seat mid-flight empirical probes are historical process defects, not independent acceptance evidence; they remain routed below.

Dispatch/completion digest copied from the closure assignment (the mutable watchdog was not treated as immutable proof):

```text
2026-10-20T03:45:29-03:00 launch souji round=14 pgid=2183055 driver=hyaku-inline attempt=1
2026-10-20T05:05:41-03:00 complete souji round=14; hyaku-inline attempt=1
```

## Independent measurements over committed bytes

These are fresh plain measurements, not executions of a sibling's gate. In Python Eval, used `subprocess.check_output(['git','-C',repo,'show',rev+':'+path])` for bytes and `git ls-tree -r --name-only <rev>` for committed paths. Parsed source rows with `re.match(r'^\|\s*S\d{3,}\s*\|', line)` and `line.split('|')[1:-1]`; counted tiers/statuses with `collections.Counter`. Counted Markdown knowledge files, separating the file containing `HELD`, and capability-table rows between `## Capabilities` and `## Planned`. Commands operate on the exact before/after hashes above; no lane Python was imported or executed.

| Measurement | Before | After | Comparison with report |
|---|---:|---:|---|
| `tools/souji-evidence-cache.py` committed presence | 0 | 1 | agrees |
| `tests/fixtures/r14-evidence-cache.py` presence | 0 | 1 | agrees |
| `tests/fixtures/r14-census-boundary.py` presence | 0 | 1 | agrees |
| source rows | 37 | 40 | agrees |
| tier A/B/C | 33/3/1 | 36/3/1 | agrees; three A additions |
| mined/queued/rejected | 20/15/2 | 23/15/2 | agrees |
| admitted/HELD Markdown knowledge entries | 5/1 | 5/1 | agrees |
| SCORECARD capability rows | 9 | 11 | two authored additions; C2 not independently admitted as no-harm |
| config-guard definitions (`^guard_git_config\(\)`) | 0 | 1 | new support restriction, not a preservation proof |
| literal `git-config-unsupported` occurrences in census source | 0 | 2 | independently confirms new refusal implementation |

All S001–S037 full registry row bytes are unchanged. All existing `corpus/knowledge/` bytes are unchanged. No new knowledge/coverage-map ground is inferred from three source rows or two authored capability rows.

Also executed:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff a31642d14006830ec62edf40b0354c3699728c4a 69c1604474494fc2746e091fd545c5d283c02cba -- SCORECARD.md
```

The diff preserves legacy scores calibration 7, operability 8, coverage 8 and zero numeric deltas, names both new capabilities, and discloses restrictions. Unchanged numbers do not establish unchanged operational support.

### C1 — calibration: improved, bounded claim verified

**Evidence-verified, not gate-reexecuted.** Parsed the two committed JSON manifests with `json.loads(git show <after>:census/round-14/<file>)`; parsed the consumer's nested `stdout` JSON and counted `checks` values. The observed committed record is:

- `verification-attempt-1.json`, measured at `48f8945780adeb259cff0ef7dd9b7efbf1544ec7`: cache selftest exit 0, `48/48 passed`; external fixture exit 0, `22/22 checks passed`; frozen run exit 0, `reusable`, one declared dependency, **two pinned input files**. Consumer: 33 assertions, 32 true, sole failed assertion `migrated_caller_refuses_stale`; gate exit 1 but retained source true.
- `verification.json`, measured at `552cae4204b3ab818419ad8adbfef3a4da29a3e0`: consumer exit 0, 33 assertions/33 true/no failed checks. Baseline authentic retention returns stale green without producer execution; migrated `attempt_reuse` returns no retained source with exit 1/`dependency-digest-mismatch` and `reason=gate-refused`. Default historical-runner invocation exits 2 before the matrix; no historical JSON is rewritten.
- Direct SHA-256 over the final committed gate is `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6`, matching S039 and recorded execution. Gate, external fixture and expected snapshot bytes are unchanged from 48f8945 to the reviewed after hash. The consumer and boundary fixture/tool are unchanged from 552cae4 to after. Historical r13 `verification.json` bytes are identical before/after.

Independently SHA-256-hashed both frozen inputs named in committed `expected.json`:

```text
dependency.txt 875598b6f830e010b5fc1c6db42528ef127423623e1af60d276be6527623366a match=true
record.json 67221a338ef4ada7505d26a41cc634fcbabb1e6b64e8ef47138e7b766871df41 match=true
expected verdict: reusable
```

`SKILL.md:138–139` supplies the gate/fixture registry fields, 0/1/2 map, self-invocation, pinned path, isolated write scope and owner. `_emit:1209–1211` disclaims historical execution proof. The consumer red→green is tied to an unchanged demonstration and the actual decision-function fix, not a weaker expectation.

**Limit:** the migrated full `run()`/`--retry-failed` dispatch was not demonstrated end-to-end; the real `attempt_reuse` function was exercised on synthetic records. Every historical r13 record is legacy and refused; no positive production retention is demonstrated. Source inspection supports the wiring, not an unobserved production run. This is enough for the report's bounded eligibility/decision claim, not universal consumer or provenance certification.

### C2 — namespace cases improve; net operability harmed

**Evidence-verified, not gate-reexecuted.** Counted `^CASE\t` rows and tab-separated PASS/FAIL in committed `verification.json` stdout:

```text
baseline tool a31642d: 12 cases; PASS=2 FAIL=10; SUMMARY total=12 failed=10; exit=1
changed tool 552cae4: 12 cases; PASS=12 FAIL=0; SUMMARY total=12 failed=0; exit=0
legacy census selftest: 38 checks, 0 failed; exit=0
warning-level ShellCheck: exit=0
```

The baseline trace contains actual synthetic forbidden-access observations, not just missing finding strings. R14C2-07/08 pass both versions. Installed census SHA-256 at the after hash is `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`, identical to the recorded changed tool. Baseline digest is `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`, also matching the record. Initial exit-2 fixture-setup failures remain in attempt-1 and are not counted as baseline red proof. Ordinary/linked/compare preservation is real but finite.

**No-harm judgment: reject.** Baseline `tools/souji-census.sh:12–18` scans every immediate main repo and `count_dirty:127–137` uses normal Git status without a key-presence ban. After `guard_git_config:493–506` reads key names only, lowercases them, and refuses `core.hooksPath` regardless of its value. A harmless repository-local `core.hooksPath=/dev/null` therefore meets the new refusal predicate; the tool's own status invocation at `710–712` forces exactly that safe value. This is not limited to a credential-store destination. `list_repos:964` calls the guard; `emit_census:979` performs discovery before printing the header at 991. `protected_fail:160–164` exits 2, so one such repository aborts the whole census, including unaffected peers.

The key-only refusal and propagation are directly established from committed source. **[INFERENCE, not an executed fixture]** an otherwise supported benign-config repository consequently changes from usable census to exit 2/no TSV. No deployment incidence was probed. The twelve committed namespace cases do not include a benign local-config preservation control. Broader includes/filters/attributes/excludes/promisor/worktreeConfig restrictions are honestly disclosed, but a narrowed tested claim cannot erase this older supported-surface contraction. Safety-motivated scope changes can be considered by the operator; they are not no-trade improvements under the current protocol.

## Discernment spot-check and source reopening

Samples are from `corpus/lessons/round-14.md`, `## Gate` / Final measured gate decisions. Sources were reopened independently; no sibling gate was run.

| Item | Lane decision | Reopened source | Agree/disagree | Reason |
|---|---|---|---|---|
| C1 declared-dependency eligibility / migrated stale decision | ADMIT within declared-byte scope | committed gate `_evaluate_dependencies:929–930`, `_emit:1209–1211`; both verification manifests and corrected consumer source | agree, bounded | Pins match and the recorded actual decision changes red→green; no authentication or complete-dependency inference is implied. |
| Historical execution/authors/complete dependencies | REJECT | `_emit:1211`; frozen record/expected input; manifest limitations | agree | Matching declared bytes cannot establish a past execution, authenticated author, or omitted dependency set. |
| Universal race-free protection / deletion certification | REJECT | tool boundary header `72–99`, PROVINCE `82–93`, synthetic case output | agree | Finite namespace tests and explicit hardlink/mount/race residuals cannot certify deletion; certification remains OFF. |
| C2 as an axis improvement with no harm | ADMIT within tested cases; expose restrictions for closure | before/after census source, especially after `493–506`, `710–712`, `964`, `973–995` | disagree with net admission | Namespace cases pass, but benign key values are also refused and can suppress the whole fleet output. |
| S038 correction | ADMIT new row, retain history | installed `/usr/share/info/coreutils.info.gz`, decompressed with Python `gzip.open(...,'rt')` | agree | Lines 15319–15320 contain the KILL quote; 15365 contains timeout exit 124. Historical S034 is superseded, not rewritten. |

New source-row quote checks, reopened 2026-10-20:

- **S038:** installed vendor source lines 15319–15320: “Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal.” Twelve whitespace-delimited words. Line 15365: `124 if COMMAND times out, and '--preserve-status' is not specified`. The lesson's new locator is correct.
- **S039:** `tools/souji-evidence-cache.py:930`: “Measure every declared dependency in sorted order.” Seven words; exact code quote and pinned digest agree. Implementation evidence is not execution evidence.
- **S040:** reopened https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve using the static reader; served Python 3.15.0 documentation says, under Path.resolve, “Make the path absolute, resolving any symlinks.” Seven words. Its introduction separately describes pure paths as computational without I/O. This supports the narrow pre-access ordering rationale, not a sandbox proof.

Executed the required fleet source validator:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```

Exit **0**, observed stdout:

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

W04 notices are advisory correction-URL duplicates, not failed validation. Corpus shape is conformant on this check; round admission is separately rejected for the operational trade.

## Per-axis and trend verdicts

| Axis | Verdict | Evidence / limit |
|---|---|---|
| calibration | improved | C1 bounded eligibility, preserved original revisions, actual decision-function red→green; limits disclosed |
| operability | harmed | C2 namespace protection improves, but key-only benign-config refusal contracts prior census support and aborts all rows |
| coverage | unchanged | admitted knowledge 5→5, HELD 1→1, unchanged knowledge bytes/map ground; do not use this corpus metric to cancel operational support loss |
| depth | unchanged | no new independently claimed technical-knowledge entry |
| freshness | unchanged | no separate admitted-entry freshness sweep; correction source independently reopened |
| adjacency | unchanged | PROVINCE preserves kagi/operator/kumitate boundaries; no operational authority absorbed |

- **Expansion: improved.** C1 adds a demonstrated repertoire capability even though no new coverage-map knowledge is added. Authored C2 capability-row presence is not counted as independent no-harm admission.
- **Quality: unchanged.** Existing admitted knowledge bytes are unchanged, no re-verification/supersession sweep is claimed, K5 remains visibly HELD. The operational trade is charged explicitly above, not hidden by this corpus-quality verdict.
- **Discernment: unchanged.** Outside sampling agrees on bounded C1 and the broad-proof/certification rejects; prior retention/citation findings become grounded R14-M1/M2/M4, Q20/Q21 and an accurate erratum. However, the current C2 net-admission disagreement remains to be learned; the author's improved trend is not accepted wholesale. The new disagreement is routed for the next lesson, not silently resolved by disclosure.

## Routed defects and review adjudication

1. **Souji next round, admission-blocking operational trade:** repair benign-config support without weakening protected-namespace refusal. Begin with value/effect-aware treatment of already-neutralized hooks settings. Add paired baseline/changed benign-config controls and a mixed-fleet case showing a harmless local setting cannot suppress unaffected rows. If broader safe configurations remain intentionally unsupported, obtain explicit operator/canonical scope-change adjudication; do not call that a no-harm improvement.
2. **Souji next round, learning:** mine this outside disagreement into the next lesson and a grounded preservation/admission criterion. Tested-case improvement and honest restrictions do not prove no harm to the previous supported domain. Retain this closure as outside evidence, not an author `[x]` mark.
3. **Souji next round, wording/evidence boundary:** consistently describe the demonstrated C1 consumer as the actual `attempt_reuse` decision on synthetic records. The full migrated dispatch and positive real-evidence retention were not run. Broader capability wording needs a separate real dispatch observation; no historical output overwrite is authorized.
4. **Souji next round, process:** enforce the disclosed prohibition on mid-flight seat empirical probes. SafetyCredential/BoundaryAttack/SafetyCache reports are not acceptance evidence. Preserve their disclosed deviation history; do not rerun to confirm those observations.
5. **Retained original observations:** the auxiliary reviewer noted that the targeted pass did not rerun the externally dependent source-anchor probe at the later revision. This closure does not relabel that original 48f8945 observation as a fresh execution. End-source validation was separately rerun by the lane, and this closure independently reopened the installed quote. Keep original measurement labels; known external-input commands require fresh observation when claimed as a new execution, not cache-based relabelling.

The prior S034 citation defect is corrected by S038/erratum; the prior retention caveat has the bounded C1 fix. R13's unexercised quarantine sites, hardlink/mount/race residuals, K5 HELD and certification OFF remain explicit limits, not newly failed promises.

SHONEN is **not** certified fully checkable by this closure: the historical live end-to-end task and every operational instruction were not independently re-reviewed/executed. Promotion and any `[x]` change remain operator-owned. No promotion, mint, sibling edit, real credential-store probe, credential/auth-file access or separate omp process occurred. Tool installs/updates: **none**.
