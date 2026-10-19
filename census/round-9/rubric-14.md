# Round 9 — S14 independent scorecard rubric

Seat: S14. Rubric version: `S14-r9-v1`. Axes: **calibration, operability, coverage**.
Independent draft: no round-9 peer findings were used. This seat changes only this file; the parent owns integration into SCORECARD.md and LOG.md.

## Measured snapshot and verdicts

Measured at `2026-10-18T23:49:25Z`, lane HEAD `14916c075c7de4b905d92c472e6312026d12d44a`. The following hashes were unchanged before and after the fixture smoke:

```text
7c0039a528a2a760622ce9d9b69427e2ee695a993b7acca72968fc048cfd2378  SCORECARD.md
a91049c96e5fba7c3db83df288a261717156c3834532e54d712ed0c555e350c4  tools/souji-verify.sh
53f92421b254426c7e4882c1da9cfaa444bddde7ff90ee30afcd48fa229328b1  tools/souji-vault-verify.sh
5780ad751aa49d1bb587690154cab98ab6aa71b4def518673c2f383301c51c4f  tools/souji-quarantine.sh
11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381  tools/souji-census.sh
```

- **Confirmed tool defects: 0 in this seat's limited smoke**, not proof of absence. Fresh fixture checks: **23 PASS / 0 FAIL**. All four installed tools also pass `bash -n`.
- **Confirmed current-score contradictions: 1 class / 2 fields.** Calibration is 7 in SCORECARD.md:14 but 6 at :45; operability is 8 at :15 but 7 at :45. Coverage agrees at 8. This is a stale-summary documentation defect, not a false-SAFE tool finding.
- **Separate evidence gaps, not extra contradictions:** all three axis rows use report labels rather than commit IDs in their measured-commit cells (`r3 report`, `r5 report`, `r4 report`). None supplies a reproducible evidence-to-0–10 mapping. A file count or a successful task alone does not derive an 8.
- **Current-scorecard calibration consistency: NOT-MET.** Operability is partially reverified by the smoke; comprehensive operability and coverage scores are **NOT-EVALUATED** under this new rubric. This seat does not assign replacement numbers or certify round-9 admission.
- **Rubric verdict: candidate for parent adoption.** Fix the summary, identify measurement snapshots, then evaluate the frozen checklist below. Preserve useful historical evidence instead of declaring historical claims false merely because live state has changed.

Basis: fleet `AXES.md:25–55,75–83`; lane `PROVINCE.md:6–36`; `AGENTS.md:3–18`; current tool interfaces. LOG.md:219–265 records rejected rounds despite useful completed work; LOG.md:267–290 records the later fixture capability. Capability acquisition and round admission must remain separate.

## Counting and evidence rules

Every checklist item is `P` (all required observations pass), `F` (a fresh observation contradicts the requirement), or `U` (not executed, invalid environment, or insufficient evidence). Each axis has a fixed denominator of ten, with one point per item:

```text
P + F + U = 10
score = P                 only when U = 0
score = NOT-EVALUATED     when U > 0; publish the bound [P, P + U]
```

Do not turn missing evidence into a measured zero, count a refusal as a safety bug, or award partial credit for an uncompleted compound requirement. A clean fail-closed refusal can satisfy a safety negative control while leaving a claimed positive capability unproved. Preserve the underlying counts alongside the coarse integer score; a verified raw improvement need not cross a score boundary.

Freeze item definitions, case IDs, mandatory variants, expected outcomes and denominator **before** running. New attack classes extend a versioned matrix; do not silently remove hard cases or adjust weights after seeing results. Compare before/after on the common frozen matrix and report newly added classes separately. A rubric change is not evidence that the tools improved.

Each scored observation needs: item/case ID; expected result and independent oracle; exact replay command; fixture recipe under `mktemp -d -p /var/tmp`; UTC measurement time; full lane HEAD and exact tool hashes; exit code; parseable output; asserted filesystem/index/preservation end state; and evidence path. Record dirty/uncommitted tool bytes by hash, not HEAD alone. A report label is acceptable as a pointer only when its measurement snapshot is explicitly resolvable.

A finding register uses `CONFIRMED-OPEN`, `CONFIRMED-FIXED` (fresh rerun on the final hashes), `NOT-REPRODUCED`, or `TEST-INVALID`. Static suspicion, old scratch output, judge votes and missing artifacts do not establish a current defect. Track environment failures separately; a quota failure without unsafe authorization is not a false SAFE/DELETE.

## Non-compensable admission gates

Scores describe evidence quality; they never authorize removal. There is no average of the three axes and no pass-rate override for a safety failure.

1. A fresh independently justified **false SAFE or false DELETE blocks the affected tool/claim** at that snapshot. One failing safety case is enough; 99 passing cases do not cancel it. Any forbidden live mutation, secret-content access, driver-state access or GUI/config side effect is also a hard stop.
2. After a fix, rerun the exact reproducer, the affected class variants, the standard permitted regression suite, and the integrated receipt-engine-to-quarantine path. Pin final bytes. Finding and fixing a defect can improve calibration; it is not evidence that no defect existed.
3. `NOT-SAFE`, `NOT-AUTHORIZED`, `ABORTED`, engine error, unknown evidence and unsupported inputs are fail-closed outcomes, **not safety defects**. A missing positive capability may make its operability item unproved, but must not be inflated into an unsafe-authorization finding.
4. Fixture success does not open live gates. Operator approval, quarantine, hold and act-time re-verification still apply. `SAFE` is a receipt verdict, not permission to skip those steps; `clean` in a census is not a removal receipt.
5. Admit a round only when its declared 1–3 causally separable, distinct-axis claims verify, no axis is harmed, and no safety gate remains open. Unknown/no-evidence is not `unharmed`. Do not rewrite a failed round into a success because the parent completed deliverables later.

## Calibration — ten reproducible evidence obligations

- **K01 Scope and axes:** every current claim maps to an owned axis or an explicitly bounded capability, with scope and rejected/out-of-scope work recorded.
- **K02 Numerical derivation:** every numeric axis score is reproducible from this versioned ten-item ledger; older scores are explicitly historical/unmapped, not carried forward as newly measured.
- **K03 Snapshot identity:** every observation resolves to commit plus actual tool hashes, measurement time and exact context; historical and current assertions are distinguished.
- **K04 Ground truth:** each counted defect has a fresh recipe and independent expected outcome; confirmed, fixed, not-reproduced and test-invalid counts reconcile.
- **K05 Count integrity:** raw rows reconcile to totals; unique case IDs and unique defect classes are both reported; multiple seats reproducing one bug do not become multiple bugs.
- **K06 Closure discipline:** every open finding has a disposition; every fixed finding has a rerun on the final integration bytes. Unresolved defects remain visible.
- **K07 Internal consistency:** the axis table, saturation summary, planned/current claims and capability ledger do not make conflicting present-tense assertions. Historical observations are labelled as such.
- **K08 Uncertainty and dissent:** untested/blocked cases and legitimate judge disagreement are visible; neither a majority vote nor tool-to-tool agreement substitutes for the oracle.
- **K09 Honest boundary:** denied candidates, missing external approval and live-work exclusions are reported without manufacturing an eligible artifact or claiming a live run from a fixture.
- **K10 Comparable axis verdicts:** improved/unharmed/harmed/unknown is supported by before/after observations on the same matrix, including regressions outside the claimed axis.

## Operability — ten executable obligations

- **O01 Installation:** all four installed entrypoints exist, pass shell syntax checks, and match the final recorded bytes; test prerequisites are checked explicitly.
- **O02 Regression suite:** every applicable standard selftest/regression suite passes on the deliverable. Harnesses must themselves obey this round's fixture-only, headless, no-protected-access envelope. Quota/scope-invalid runs are U, not green.
- **O03 Output contract:** exact verdict tokens, target identity, record cardinality/order and documented exit codes are machine-checked for normal, batch and malformed input; unknown/error cannot be parsed as SAFE.
- **O04 Receipt engine:** pushed and stale happy paths work; local-only/unknown-ref, live-reference and freshness controls refuse; checks are exercised through real subprocess calls.
- **O05 Preservation verification:** an independent source/vault pair works; missing/mismatched/incomplete/self-dependent preservation refuses; advisory CLI behavior cannot create a receipt or a GUI/config side effect.
- **O06 Census and comparison:** repetition is deterministic on frozen fixtures; expected rows/flags reconcile; identical compare is header-only/exit 0; real changes are detected; malformed/partial input cannot masquerade as a clean comparison.
- **O07 Dry run:** authorized and refused cases produce the correct dry-run result while preserving source bytes, metadata, index, refs and quarantine absence. Dry-run success is not a promise that a future second check will pass.
- **O08 Integrated lifecycle:** each claimed receipt class executes stage→hold→second check→delete on fixture success; tampering/revoked evidence aborts and retains the staged object. Assert end state and preservation survival, not merely a DELETED string.
- **O09 Containment and recovery:** live guard, repo boundaries, symlinked ancestors, collisions, interruption and failure paths cannot escape the fixture or destroy the sole copy. Any temporary output also stays under `/var/tmp`.
- **O10 Operator handoff:** runbooks have tested commands, correct named gate owners, explicit authorization context and recovery steps; no live mutation is implied by a capability demonstration or by a census flag.

## Coverage — ten mandatory surface families

Coverage means governed domain surface, not number of seats, repetitions, deleted files or bytes. A family passes only when its preregistered supported variants and applicable negative controls are verified. Intrinsically forbidden variants are refusal-only; an otherwise positive-capability family cannot pass by refusing everything. These are minimum families, not a claim of exhaustive security coverage.

- **C01 Ordinary artifacts:** files and directories, tracked/untracked/ignored states, repository roots and nested repository boundaries; correct artifact-vs-metadata classification.
- **C02 Git preservation:** remote-default resolution, no/ambiguous refs, later local edits, staged/unstaged changes, detached/alternate refs and git-command errors; account for the current bytes, not introduction ancestry alone.
- **C03 Stale scratch:** every documented scratch family, old/young/boundary/future mtimes, live references, self/census/quarantine exclusions, directories containing newer or referenced children, and unreadable scans.
- **C04 File ledgers:** valid independent pair; missing/changed sides; incomplete, duplicate, relative, CRLF/no-EOL and malformed rows; self/symlink/hardlink dependence; no requirement to read secret-shaped payloads.
- **C05 Directory ledgers:** deterministic complete manifests, empty directories/metadata policy, nested vault copies, symlinks/special nodes, traversal/hash errors and repository-history preservation rather than only working-tree bytes.
- **C06 Worktree metadata:** present/absent, clean/dirty, named/detached, pushed/unpushed/unique, pinned/locked registrations, missing objects and failed git probes; preserve metadata-only semantics.
- **C07 Paths and execution context:** canonical/lexical paths, relative paths, outside-repo targets, symlinked ancestors, unusual separators/control characters, option-like names, git pathspec magic and inherited git environment.
- **C08 Census inventory:** main/root/linked/bare/malformed/hidden/symlink repo shapes; dirty/worktree/no-remote/error states; deterministic compare, duplicate/truncated rows and path-sanitization collisions.
- **C09 Quarantine transition:** every claimed receipt and list pin, dry-run, staging collisions/failures, hold-boundary mutation, receipt revocation, index/ref changes, second-check failure and post-check race assumptions.
- **C10 Protected boundaries:** secrets, operator config, driver runtime, live lane products and GUI launchers have explicit exclusion/refusal coverage. Audit guards/instrumentation without opening protected payloads or creating/touching forbidden driver-state paths.

Report both `covered families / 10` and the expanded case matrix with untested variants. A shrinking candidate set or all candidates being legitimately refused is not reduced scope coverage, but also does not prove a newly runnable deletion capability.

## Differential and contradiction audit rules

Normalize tools only over a shared, documented contract: canonical artifact identity, exact verdict and receipt, consistent fixture/root/ledger/time context, final hashes. Preserve raw output. Do not search for the substring `SAFE` inside `NOT-SAFE`, or trust a summary without per-target/end-state assertions.

`tools/souji-verify.sh` tries pushed before ledger for ordinary artifacts; the vault tool checks a matching ledger first and may terminate with a ledger mismatch. That intentional precedence difference, differing reason text, two-line versus JSON output, or one tool refusing while another has an independently valid receipt is **not automatically a contradiction or defect**. Adjudicate each against independently established preservation/safety ground truth. Agreement between two implementations can reproduce a shared bug.

Count contradictions by `(current assertion key, measurement scope/snapshot)` and report affected fields separately. Current-vs-current incompatible scores count; historical-vs-live drift, missing evidence, externally blocked work and duplicate reports do not. A historical hash still matching its cited measurement commit is not a broken current-tool hash claim unless it is presented as current.

For the measured SCORECARD.md, the tally is one stale-summary class, two contradictory fields, three snapshot-label gaps, and three numerically underived rows. Do not sum those overlapping documentation observations into nine tool defects.

## Fresh reproduction A — scorecard contradiction counts

Run from the lane root. This only reads SCORECARD.md:

```bash
python3 - <<'PY'
import json, pathlib, re
s = pathlib.Path('SCORECARD.md').read_text()
rows = {m[0]: int(m[1]) for m in re.findall(r'^\| (coverage|calibration|operability) \| (\d+) \|', s, re.M)}
bottom = re.search(r'Coverage (\d+),\s*operability (\d+), calibration (\d+)', s)
summary = dict(zip(('coverage', 'operability', 'calibration'), map(int, bottom.groups())))
differences = [{'axis': a, 'table': rows[a], 'summary': summary[a]} for a in sorted(rows) if rows[a] != summary[a]]
cells = [re.split(r'(?<!\\)\|', x)[1:-1] for x in s.splitlines() if re.match(r'^\| (coverage|calibration|operability) \|', x)]
measured = {x[0].strip(): x[4].strip() for x in cells}
print(json.dumps({'contradictions': differences, 'fields': len(differences), 'classes': int(bool(differences)), 'measured_commit_cells': measured}, indent=2))
PY
```

Observed: calibration `7 vs 6`, operability `8 vs 7`; `fields=2`, `classes=1`; measured cells `coverage=r3 report`, `calibration=r5 report`, `operability=r4 report`. Escaped pipes in the coverage counting command are excluded from column splitting.

## Fresh reproduction B — limited fixture smoke, not full certification

Executed successfully at the hashes above using Python 3.14.7 and Git 2.55.0. The fresh fixture was `/var/tmp/souji-r9-s14.XvLVaU` and was removed by `finally`. No live candidate, remote service, secret-shaped fixture, forbidden driver-state path or GUI is used. No git fetch/push/commit/branch is run; fixture history is built by plumbing. This is **16 receipt checks + 3 census checks + 4 quarantine checks = 23**, not the full rubric denominator and not 23 independent security classes. Standard selftests were not executed by this seat.

The following complete replay prints its per-case results and cleans only its own fixture. Recheck/pin tool hashes when replaying after a patch; success on different bytes is a new observation.

```bash
fixture=$(mktemp -d -p /var/tmp souji-r9-s14.XXXXXX) && TMPDIR=/var/tmp S14_FIXTURE="$fixture" python3 - <<'PY'
import hashlib, json, os, pathlib, shutil, subprocess
base=pathlib.Path(os.environ['S14_FIXTURE']); lane=pathlib.Path.cwd(); repo=base/'fleet'/'probe-shokunin'; vault=base/'vault'
env=os.environ.copy(); env.update(TMPDIR='/var/tmp',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_OPTIONAL_LOCKS='0',GIT_AUTHOR_NAME='S14 fixture',GIT_AUTHOR_EMAIL='s14@example.invalid',GIT_COMMITTER_NAME='S14 fixture',GIT_COMMITTER_EMAIL='s14@example.invalid')
for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_NAMESPACE','SOUJI_QUARANTINE_ALLOW_LIVE','SOUJI_Q_TEST_HOOK','SOUJI_Q_SELFTEST_ACTIVE'):
    env.pop(k,None)
checks=[]
def call(args, stdin=None, extra=None):
    return subprocess.run(list(map(str,args)), input=stdin, text=True,capture_output=True,env=env| (extra or {}),timeout=30)
def check(name, ok, detail=''):
    checks.append({'case':name,'pass':bool(ok),'detail':detail}); assert ok,(name,detail)
def git(*args, stdin=None):
    p=call(['git','-C',repo,*args],stdin=stdin); assert p.returncode==0,p.stderr; return p.stdout.strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    repo.mkdir(parents=True); vault.mkdir(); (base/'home').mkdir(); env['HOME']=str(base/'home')
    git('init','-q','--initial-branch=master')
    pushed=repo/'pushed.txt'; pushed.write_text('preserved pushed bytes\n')
    git('add','--','pushed.txt'); tree=git('write-tree'); head=git('commit-tree',tree,stdin='fixture\n')
    git('update-ref','refs/heads/master',head); git('update-ref','refs/remotes/origin/master',head); git('symbolic-ref','refs/remotes/origin/HEAD','refs/remotes/origin/master')
    (repo/'.scratch').mkdir(); aged=repo/'.scratch'/'aged.out'; aged.write_text('old neutral payload\n'); os.utime(aged,(1,1))
    linked=repo/'.scratch'/'linked.out'; linked.write_text('old referenced payload\n'); os.utime(linked,(1,1))
    (repo/'notes.md').write_text('linked.out is still used\n')
    young=repo/'.scratch'/'young.out'; young.write_text('new neutral payload\n')
    plain=repo/'ordinary.txt'; plain.write_text('unreceipted payload\n')
    source=repo/'preserved.md'; source.write_text('independent preservation\n'); copy=vault/'preserved.md'; copy.write_bytes(source.read_bytes())
    bad=repo/'mismatch.md'; bad.write_text('current source bytes\n'); badcopy=vault/'mismatch.md'; badcopy.write_text('earlier source bytes\n')
    ledger=base/'ledger.tsv'; ledger.write_text('source_path\tsource_sha256\tvault_path\tvault_sha256\n'+f'{source}\t{sha(source)}\t{copy}\t{sha(copy)}\n'+f'{bad}\t{sha(badcopy)}\t{badcopy}\t{sha(badcopy)}\n')
    ctx={'SHOKUNIN_ROOT':str(base/'fleet'),'SOUJI_LEDGER':str(ledger)}
    cases=[('pushed',pushed,'SAFE','pushed'),('preserved',source,'SAFE','moved-to-obsidian'),('aged',aged,'SAFE','stale'),('referenced',linked,'NOT-SAFE',None),('young',young,'NOT-SAFE',None),('no_receipt',plain,'NOT-SAFE',None),('missing',repo/'missing.txt','NOT-SAFE',None),('source_mismatch',bad,'NOT-SAFE',None)]
    for tool in ('souji-verify.sh','souji-vault-verify.sh'):
        for name,target,want,receipt in cases:
            args=['bash',lane/'tools'/tool,'--json']; args+=['--fallback'] if tool=='souji-vault-verify.sh' else []
            p=call([*args,'--',target],extra=ctx); d=json.loads(p.stdout)
            check(tool+':'+name,p.returncode==0 and d['verdict']==want and (receipt is None or d['receipt']==receipt),d['verdict']+'('+d['receipt']+')')
    cargs=['bash',lane/'tools'/'souji-census.sh','--root',base/'fleet']
    one=call(cargs); two=call(cargs)
    check('census:repeat',one.returncode==two.returncode==0 and one.stdout==two.stdout)
    baseline=base/'baseline.tsv'; baseline.write_text(one.stdout)
    same=call([*cargs,'--compare',baseline]); check('census:compare_same',same.returncode==0 and len(same.stdout.splitlines())==1)
    added=repo/'added.txt'; added.write_text('new untracked file\n')
    delta=call([*cargs,'--compare',baseline]); check('census:compare_delta',delta.returncode==3 and '\tdirty\t' in delta.stdout)
    qctx={'SOUJI_Q_SHOKUNIN_ROOT':str(base/'fleet'),'SOUJI_Q_LEDGER':str(ledger),'SOUJI_VERIFY_BIN':str(lane/'tools'/'souji-verify.sh')}
    qargs=['bash',lane/'tools'/'souji-quarantine.sh','--hold','0']
    before=sha(repo/'.git'/'index'); before_bytes=pushed.read_bytes()
    dry=call([*qargs,'--dry-run',repo,pushed],extra=qctx)
    check('quarantine:dry_run',dry.returncode==0 and '\tDRY-RUN-PASS\tpushed\t' in dry.stdout and pushed.read_bytes()==before_bytes and sha(repo/'.git'/'index')==before and not (repo/'.ufo-quarantine').exists())
    refused=call([*qargs,repo,plain],extra=qctx)
    check('quarantine:no_receipt',refused.returncode==3 and '\tNOT-AUTHORIZED\t' in refused.stdout and plain.read_text()=='unreceipted payload\n')
    removed=call([*qargs,repo,pushed],extra=qctx)
    check('quarantine:full_flow',removed.returncode==0 and '\tDELETED\tpushed\t' in removed.stdout and not pushed.exists() and not (repo/'.ufo-quarantine').exists() and git('cat-file','blob',head+':pushed.txt')=='preserved pushed bytes')
    hook=base/'tamper.sh'; hook.write_text('#!/usr/bin/env bash\nprintf tampered >> "$1"\n')
    aborted=call([*qargs,repo,aged],extra=qctx|{'SOUJI_Q_SELFTEST_ACTIVE':'1','SOUJI_Q_TEST_HOOK':str(hook)})
    staged=list((repo/'.ufo-quarantine').glob('*/.scratch/aged.out'))
    check('quarantine:tamper_abort',aborted.returncode==3 and '\tABORTED\tstale\t' in aborted.stdout and len(staged)==1 and staged[0].read_text().endswith('tampered'))
    print(json.dumps({'fixture':str(base),'checks':checks,'passed':len(checks),'failed':0,'tool_defects_confirmed':0,'scope':'limited smoke, not an exhaustive adversarial audit'},indent=2))
finally:
    shutil.rmtree(base)
PY
```

## Parent integration actions

1. Reconcile the two summary scores with the axis table; do not invent a different score while doing so.
2. Give existing numeric rows an explicit historical/unmapped status or derive them using an adopted, frozen rubric. Record real commit/hash context and keep the old task observations.
3. Add demonstrated census/quarantine capabilities to the current repertoire with their actual first-working evidence; do not treat their absence from the old table as a new runtime defect.
4. Combine independent round-9 attack findings by unique class, rerun on integrated final bytes, and evaluate the complete safety gates before admitting claims. This seat's 23 green smoke checks cannot discharge that obligation.
