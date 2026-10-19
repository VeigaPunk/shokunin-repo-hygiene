# S24 dissent and adjudication — round 9

Status: FINAL snapshot judgment at 2026-10-18T21:13:57-03:00. The initial sections preserve baseline discoveries and their early subtotals; the final reconciliation below supersedes those subtotals and records final installed/candidate replays. Operational safety remains BLOCKED; this record authorizes no live removal.

Axes: calibration, coverage, operability. Fail-closed direction applies: a correct refusal is never scored as a defect. The unit is a reproducible root cause, not every tool/seat reporting it.

## Independent baseline and findings

Frozen tool hashes are in `final-24.json`; fixture-only built-in selftests pass verify 24/24, vault 35/35, quarantine 63/63, census 32/32 (154/154). The green baseline does **not** settle adversarial safety.

- **S24-D1 — confirmed false DELETE:** a pushed directory containing an ignored, never-pushed regular-file descendant gets `SAFE(pushed)`. Porcelain over the directory is empty; quarantine uses `intro-blob=dir-pin-only`, returns `DELETED` rc=0, and removes the unique descendant. Receipt closure over the directory is missing. `tools/souji-quarantine.sh:291-300` binds a file to an introducing blob, but directories only to their pre-move digest: that proves no tampering, not preservation.
- **S24-D2 — confirmed false SAFE only:** both receipt engines say `SAFE(pushed)` after a tracked file is replaced by uncommitted bytes. Quarantine's `dirty-tracked` refusal correctly preserves it. Do not conflate the engine defect with a quarantine deletion defect.
- **S24-D3 — confirmed false DELETE:** a tracked scratch file modified in one local-only commit gets `SAFE(stale)` after its mtime is older than the threshold and the reference sweep is empty. Quarantine rechecks the renamed staged path and deletes it. The unpushed-path veto in PROVINCE.md:34 and SKILL.md:34 must dominate **all** receipt fallbacks, not just `pushed`.

Provisional independent count: **3 root causes; 2 false-DELETE classes, 1 false-SAFE-only class**. Co-reports must be deduplicated against these classes.

## Fresh reproduction, not a historical allegation

The complete fixture generator and captured stdout/stderr are preserved at:

- `/var/tmp/souji-r9-s24.ZRQLD3/judge-battery.py`
- `/var/tmp/souji-r9-s24.ZRQLD3/logs/judge-battery.json`

Run `python3 /var/tmp/souji-r9-s24.ZRQLD3/judge-battery.py` for fresh, independent `mktemp` fixtures on every invocation. Its frozen tool copies are hash-pinned in `final-24.json`. This compact standalone sequence reproduces the same three classes against the canonical tools at invocation time; execute only in fixture repos:

```bash
set -eu
D=$(mktemp -d -p /var/tmp souji-s24-repro.XXXXXX)
T=/home/vgpnk/Projects/shokunin/souji-shokunin/tools
export TMPDIR=/var/tmp GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_OPTIONAL_LOCKS=0 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@local
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@local
mkdir -p "$D/fleet" "$D/home"
export HOME="$D/home" SHOKUNIN_ROOT="$D/fleet" SOUJI_LEDGER="$D/absent.tsv"
export SOUJI_Q_SHOKUNIN_ROOT="$D/fleet" SOUJI_Q_LEDGER="$D/absent.tsv"
newrepo() { R="$D/fleet/$1-shokunin"; git init -q --initial-branch=master "$R"; }
record() {
  git -C "$R" add -A
  tree=$(git -C "$R" write-tree)
  if [ -n "${1:-}" ]; then
    tip=$(printf 'fixture\n' | git -C "$R" commit-tree "$tree" -p "$1")
  else
    tip=$(printf 'fixture\n' | git -C "$R" commit-tree "$tree")
  fi
  git -C "$R" update-ref refs/heads/master "$tip"
}
pushed() {
  git -C "$R" update-ref refs/remotes/origin/master "$tip"
  git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
}
newrepo directory
mkdir -p "$R/bundle"
printf 'pushed\n' > "$R/bundle/kept.txt"
printf 'bundle/never-pushed.bin\n' > "$R/.gitignore"
record; pushed
printf 'unique unpushed bytes\n' > "$R/bundle/never-pushed.bin"
bash "$T/souji-verify.sh" --json "$R/bundle"
git -C "$R" --no-optional-locks status --porcelain -- bundle
bash "$T/souji-quarantine.sh" --hold 0 "$R" bundle
# Expected on the measured bytes: DELETED, including the ignored descendant.
newrepo dirty
printf 'pushed\n' > "$R/note.txt"
record; pushed
printf 'uncommitted replacement\n' > "$R/note.txt"
bash "$T/souji-verify.sh" --json "$R/note.txt"
bash "$T/souji-vault-verify.sh" --fallback --json "$R/note.txt"
bash "$T/souji-quarantine.sh" --hold 0 "$R" note.txt || test "$?" = 3
# Expected: false SAFE from engines, correct NOT-AUTHORIZED from quarantine.
newrepo stale
mkdir -p "$R/.scratch"
printf 'pushed\n' > "$R/.scratch/old.out"
record; pushed
parent=$tip
printf 'local-only committed replacement\n' > "$R/.scratch/old.out"
record "$parent"
touch -d '5 days ago' "$R/.scratch/old.out"
git -C "$R" log --branches --not --remotes --oneline -- .scratch/old.out
bash "$T/souji-verify.sh" --json "$R/.scratch/old.out"
bash "$T/souji-vault-verify.sh" --fallback --json "$R/.scratch/old.out"
bash "$T/souji-quarantine.sh" --hold 0 "$R" .scratch/old.out
# Expected: one unpushed touching commit; nevertheless SAFE(stale), DELETED.
```

## Rejected defect interpretations

1. **Different source/vault hashes, both matching the row:** reproduced, but NOT-A-DEFECT under the current contract. The specification verifies four conjuncts, not equality between columns 2 and 4; exports may transform bytes. Identity would require an explicit stronger contract. This case is retained as a semantic risk, not added to the defect numerator.
2. **Visible untracked directory descendant:** quarantine returns `NOT-AUTHORIZED dirty-tracked` rc=3 and preserves the child. This is a passing negative control, not a false DELETE.
3. **Built-in selftests all green:** factual, but not grounds to negate D1/D2/D3. Their assertions omit these conditions.

## Pending adjudication

S17/S18 patch status and co-judge dissent remain pending. The rubric authors are S14/S15/S16 (not S19/S20 as initially assumed); all three drafts have now been read. Independent scorecard measurement confirms two incompatible current numeric fields (calibration 7 vs 6; operability 8 vs 7), one stale-summary root-cause class, and two separate capability-table omissions. S14's 1-class/2-field count and S15/S16's 2-field count do not disagree on facts. No numeric promotion or live removal is authorized by this provisional record.

Additional independent findings at the same frozen tool hashes:

- **S24-D5 — unsafe DELETE containment:** `.ufo-quarantine` is a symlink to an outside-repo fixture directory. The tool follows it for staging and deletion, returns `DELETED` rc=0, and violates physical quarantine containment. Reproduce with `python3 /var/tmp/souji-r9-s24.ZRQLD3/containment-battery.py`, case `D5_quarantine_root_symlink_escape`.
- **S24-D6 — false SAFE, no DELETE:** source==vault ledger row. `souji-verify` says SAFE while the vault engine correctly refuses `source-equals-vault`; quarantine aborts and retains staged bytes. Reproduce with `python3 /var/tmp/souji-r9-s24.ZRQLD3/differential-battery.py`, case `D6_self_referential_ledger`.
- **S24-D7 — false DELETE:** `.usage.md` contains a live reference to `old.out`, but both engines omit hidden files from their stale sweep and quarantine deletes the referenced artifact. Same differential script, case `D7_hidden_live_reference_omitted`.

Independent count is now **6 root causes: 4 unsafe-DELETE classes and 2 false-SAFE-only classes**. This supersedes the early 3-class subtotal above, not any pre-fix observation. Captured transcripts: `/var/tmp/souji-r9-s24.ZRQLD3/logs/{containment,differential}-battery.json`.

Two additional controls must not inflate this count: `--assume-unchanged` and `--skip-worktree` can hide dirt from porcelain, but the file-level introducing-blob second check detects the changed bytes and aborts, retaining them. Also, a valid pushed or stale receipt versus vault's ledger-first mismatch refusal is a benign precedence difference, freshly reproduced in the differential battery. Agreement on a shared false SAFE is still unsafe; disagreement on conservative precedence is not.

## Rubric ruling

S14/S15/S16 are sound prospective bases; prefer S15's explicit 30-row executable ledger with S14's snapshot and independent-oracle obligations. S24 replayed S14's exact 23-case smoke, S16's exact 11 selfchecks, and seven positive/negative S15 scorer tests (all passed). This is calculator/smoke validation, not a completed 30-gate lane assessment. Historical 8/7/8 stays LEGACY-UNMAPPED; all new axis scores are UNRATED.

S13 is **not recommended as-is**, despite a mechanically reproducible scorer (six independent fixture-commit tests passed). Its safety override sets calibration=0 even when an audit accurately discovers and discloses a pre-existing tool defect; fleet AXES.md defines calibration as self-assessment quality, not tool correctness. Its coverage credit for every exercised failing case measures exploration, whereas S14/S15/S16 require governed positive/negative surface controls. Its `closed=true` ledger can emit `MEASURED` with a BLOCKED mandatory cell (fresh fixture test: calibration=9, other axes=10), while the other drafts leave unknown axes unrated. These are substantive alternative metric choices, not runtime tool defects or extra current-scorecard contradictions. Keep exploration counts separate and apply a deployment veto without erasing calibration evidence.

## Dirty-file interpretation dissent

S12's early `pushed-dirty-file` observation and S09's corpus oracle treat SAFE as a receipt-only fact because quarantine blocks the mutation. S23 and S24 instead count the engines' SAFE as a **false SAFE removal-verdict defect**: the tools advertise removal verdicts, PROVINCE.md:34 / AGENTS.md:10 veto dirty work touching the artifact, and the round explicitly treats false SAFE as material. Both sides agree on all observed bytes and on quarantine's correct refusal. Count one engine root cause, zero unsafe-delete cases for this variant; never call quarantine's refusal a failure. This dispute must remain visible rather than silently disappearing into a majority vote.

## Fresh peer-replay findings

S24 executed the durable embedded S03, S04, S05 (both variants), S06, S07 and S11 recipes, S10's full 40-case corpus, and S09's full 40-artifact generator with a real tab-target delete. All used the same frozen baseline tools; captures are `/var/tmp/souji-r9-s24.ZRQLD3/logs/`. Repetitions do not multiply defect classes.

- S03: Git disappearance after worktree discovery becomes SAFE(metadata-prune), even though the fixture branch retains an unpushed commit. Turkish `LANG=tr_TR` with a genuinely compiled locale bypasses ID_* refusal on an empty aged directory. Both freshly reproduced.
- S04: NUL is silently erased from list paths and exact receipt pins; both invalid rows delete the alias target. One parser root cause, two contract-violation scenarios. A valid prefix followed by malformed input can delete before exit 2, but no all-or-nothing contract exists; do not count that as another unsafe-authorization defect.
- S05: missing/rewound default origin refs during hold still permit DELETE when a backup ref keeps the broad any-remote query empty. These two manifestations are one lost-default-ref-predicate cause, not two. Bytes remain in the backup fixture ref; the violation is current receipt authority, not unrecoverable loss.
- S06: stale and pushed ancestors delete dirty/unpushed nested repositories. Map these to the stale-directory and pushed-directory closure classes, not an extra general nested-repo bug. Both supposedly read-only verifiers also replace fixture `.git/index`, proven by hash changes plus strace; this is a separate write-contract defect, not a false-SAFE count.
- S07: after an atomic header-only ledger replacement, eight in-flight verifier calls still report SAFE and four quarantine calls DELETE. Fresh calls refuse. One receipt-generation/revocation class across three surfaces; independent vault copies survive, so do not claim unrecoverable loss. Safe coordination with concurrent writers needs a generation/locking protocol; a fingerprint check alone does not prove arbitrary race freedom.
- S09: a filename `tab<TAB>SAFE<TAB>stale<TAB>payload.dat` has no receipt and both JSON verifiers correctly refuse it, yet quarantine parses the echoed raw TSV path as authority, returns SAFE(stale) twice and actually DELETEs it. This is a distinct engine-output framing defect, not the list-file NUL erasure. A three-column directory ledger row also yields core SAFE despite missing mandatory vault digest; vault refuses and actual quarantine aborts while retaining bytes.
- S10: full outcome vector matches: 40 cases, seven A/B differences (five unsafe directional, two benign), 13 unsafe deletions, zero harness errors. Fresh/externally referenced children of aged directories and detached-HEAD omissions reproduce. Source/vault overlap was additionally reconstructed with **no helper-created spare copy**: both verifiers still SAFE, quarantine retains the sole staged copy on abort.
- S11: the exact shell proof freshly reproduced unique detached-commit loss after a false SAFE metadata-prune recommendation, native fixture prune and fixture-only GC. It also reproduced dirty linked-worktree DELETE under a non-`*-shokunin` owner, ambiguous registration overwrite, tab-corrupted internal owner metadata, and main gitfile-root misclassification. Missing/malformed object/ref cases join the already-counted Git-error-to-zero class. Quarantine itself skips metadata-prune; it does not execute prune/GC. Locked-registration SAFE is recorded as a policy mismatch (native Git preserves the lock), not another strict code/data-loss class.

The S09, S10 and S11 mismatch counts have different case universes and compared surfaces. They must never be added as if they were one global contradiction numerator. Each is reported with its denominator in the final JSON.

## Count reconciliation

The final JSON baseline register J01–J23 is a **freshly reproduced S24 union**, not a sum of peer totals or an exhaustive domain claim: **23 runtime root/invariant classes = 12 unsafe-DELETE classes (including containment/authority), 8 false-SAFE-only classes, 1 unsafe metadata-prune recommendation leading to fixture commit loss, and 2 additional read-only/input-validation contract classes.** Interacting causes do not double-count a deletion occurrence (for example detached-directory case S10-135). J05 moved from false-SAFE-only to destructive after S24 freshly reproduced S18's act-time vault-to-quarantine symlink alias: the only staged copy is deleted. It remains the same preservation-independence root, not an extra bug.

S22's narrower earlier union has 14 classes; its ledger self/descendant/ancestor variants are correctly grouped under one independence invariant, which S24 adopts as J05 rather than inflating two roots from S10-D06/D07. S24's additional fresh NUL/list, tab/output, ledger-revocation, unavailable-scope and worktree identity/ambiguity replays explain the broader total. This is a measurement-scope difference, not contradictory observations. Lock-policy SAFE, census newline inventory flags, and main gitfile-root census omission stay separately qualified and are not added to the strict safety-root total.

S22's empty-census comparison is also independently reproduced: a zero-byte prior TSV plus empty current root returns a successful header-only diff despite the required-header contract. It is J14, a measurement/input-validation defect, not an unsafe deletion or an extra scorecard contradiction.

## Final installed S17 snapshot

Exact final hashes are in `final-24.json` (`4baa8d95…`, `ea43bb0f…`, `f6f8516c…`, unchanged census `11bf9cdf…`, required selftest helper `dd7c636e…`). S24 froze all five files in an isolated fixture lane, ran the real expanded suites **40/40 + 51/51 + 91/91 + 32/32 = 214/214**, and replayed broader attack universes against those same bytes.

- S05 origin rollback and missing-origin variants now ABORT rc=3, retaining staged copies.
- S07's scheduled atomic ledger revocation now produces 8 in-flight NOT-SAFE, 8 fresh NOT-SAFE and 4 quarantine ABORTED with all four staged copies retained. Positive stable-ledger controls still work. This is bounded schedule closure, not proof against ABA or the final check-to-delete race.
- S17's new regression tests also demonstrate checked Git errors, locale refusal, read-only index preservation and NUL-list refusal. Nested-repository variants of directory closure now refuse, but general directory closure remains unsafe.
- The complete S10 replay still has **13 unsafe DELETE cases**, 7 A/B verdict differences (5 unsafe directional, 2 benign), 24 cases with an unsafe SAFE, and no harness error.
- The fresh S09 generator still actually deletes the no-receipt tab-spliced target. Its three-surface differences remain **8/40**; three are layered refusals, five are unsafe authority differences.
- The exact S11 shell proof again loses the unique detached commit after acting on false metadata-prune plus fixture-only GC, and actually DELETEs the dirty linked worktree. Ambiguous registrations and gitfile-root false SAFE also remain. Query-error variants now refuse; tab-owner W19 fails closed through checked query errors, without claiming the internal representation was repaired.

**Current final-byte lower bound: 16 confirmed open root/invariant classes**: J01–J08, J12, J14, J15, J17, J19, J20, J22, J23. This is 9 destructive classes, 5 false-SAFE-only classes, 1 unsafe metadata-prune recommendation and 1 input-validation contract class. J09/J10/J11/J13/J16/J18 have demonstrated repairs on the registered cases; J21's demonstrated exploit is now blocked. Neither list asserts exhaustive closure of untested variants.

## S18 candidate — useful but not promotable as-is

All three suffix wrappers **and** `souji-guard.r9-s18.sh` were frozen as one complete package; canonical-name adapter copies preserve identical bytes and include the required suffixed child engine. S24 independently reproduced:

- S18's own battery: baseline **9/37**, 28 unsafe outcomes; candidate **37/37**, zero unsafe outcomes in that battery; all 122 inherited candidate checks pass.
- Broader S10 corpus on the candidate: **2 actual unsafe directory deletions** (133 assume-unchanged, 134 skip-worktree) and 3 unsafe SAFE cases (the file variant aborts and retains bytes). No harness errors; A/B verdict mismatch count 0 does not establish safety.
- S04's two NUL row variants still actually DELETE on S18. S17 correctly fixes this boundary; do not regress it by replacing wrappers wholesale.
- S07's atomic-revocation schedule still yields 8 in-flight SAFE and 4 DELETE on S18, with independent vault copies surviving. S17 fixes that demonstrated schedule; a late-loaded S18 override must not remove the generation checks.
- S11 W16/W17 still produce false metadata SAFE; R05 still produces false pushed SAFE for a main gitfile root. W19 and dirty worktree W20 correctly refuse on the candidate.

S20's limited S09-corpus PASS and S18's 37/37 are accurate within their stated universes, not contradictory to these wider failures. Current installed S17 and S18 each repair useful but incomplete subsets; **neither receives a clean deployment certificate**. Integration must compose the repairs, add direct current-byte checks that ignore index concealment flags, fix worktree identity/ambiguity and remaining corpus classes, and replay both case universes on the final complete wrapper/engine/helper identities.

## Merged-rubric dissent — arithmetic is valid, metric choice remains

S19's `rubric-final.md` (sha256 `36f3322a7f31b76e12add5c64d94d3d103f78ea93e6c1eeff8567479ffb9b18f`) chooses S13; S21 concurs. S24 read the exact merged artifact and replayed its calculator with six fresh committed-evidence fixture tests, all passing. Its stronger provenance binding is valuable; this is not an implementation/arithmetic defect.

S19 explicitly labels coverage as exploration, makes MEASURED structural rather than operational, and prohibits new publication from incomplete evidence. Those qualifications resolve overclaim risk but do not change S24's axis-semantics dissent: a safety override still turns an otherwise honest calibration assessment into zero, and explored failing surfaces are not the same metric as safely governed fleet coverage. Prefer S13's committed-evidence interface **with** S15/S14's independent safety veto and unknown/bounds publication policy; keep raw calibration quality visible. If the parent chooses the merged convention, document it as a new evidence metric, not a numerical improvement over legacy AXES scores. Pin required helper/guard dependencies in the runtime evidence as well as the four entrypoints.

All three current axis scores remain **UNRATED / LEGACY-UNMAPPED**. The two conflicting current score fields (one stale-summary class) and two capability-row omissions are unchanged. No rubric choice repairs runtime safety or retroactively admits r6/r7.

## Durable supplemental probes and limits

The complete peer recipes are retained in S03/S04/S05/S06/S07/S10/S11 JSON and `seat-09-generator.py`; those source recipes, not old disposable output paths, are the durable replay inputs. The early standalone block above covers S24's first three classes. This fresh standalone command covers the unavailable-reference-scope and empty-census cases without requiring retained fixtures:

```bash
python3 - <<'PY'
from pathlib import Path
import json, os, subprocess, tempfile, time
b=Path(tempfile.mkdtemp(prefix='souji-s24-extra-',dir='/var/tmp'))
t=Path('/home/vgpnk/Projects/shokunin/souji-shokunin/tools')
p=b/'old.out'; p.write_text('synthetic aged artifact\n'); old=time.time()-5*86400; os.utime(p,(old,old))
e=dict(os.environ,TMPDIR='/var/tmp',SHOKUNIN_ROOT=str(b/'missing-root'),SOUJI_LEDGER=str(b/'missing-ledger.tsv'),GIT_OPTIONAL_LOCKS='0')
for n in ('souji-verify.sh','souji-vault-verify.sh'):
    a=['bash',str(t/n),'--json']+(['--fallback'] if 'vault' in n else [])+[str(p)]
    r=subprocess.run(a,env=e,text=True,capture_output=True,timeout=30)
    print(json.dumps({'tool':n,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}))
(b/'empty-root').mkdir(); (b/'empty.tsv').write_text('')
r=subprocess.run(['bash',str(t/'souji-census.sh'),'--root',str(b/'empty-root'),'--compare',str(b/'empty.tsv')],env=e,text=True,capture_output=True,timeout=30)
print(json.dumps({'tool':'census-empty-compare','exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}))
PY
```

No live candidate was attacked or moved. Tool selftests ran only from copied fixture lanes; inherited suites do create synthetic secret/protected-name sentinels inside their own fixtures, so their green results are regression observations, **not proof of strict no-protected-name-access harness conformance**. S22/S23/S21's stricter decision not to execute those suites is a legitimate methodological distinction. All independent destructive attack fixtures use ordinary payload names (or empty/absent name-refusal probes), no live secret content, driver state or watchdog logs. All required background work has completed.

**Final round ruling:** bounded differential audit and prospective rubric work are useful; clean fail-closed hardening is NOT-MET. Keep live removal unauthorized, preserve the dissent, and do not admit the round as fully clean while the final-byte unsafe authorizations remain.
