# Round 13 — non-author closure and verifier spot-check

author: hyaku closure (non-author integrator, @m_strong)

Date: 2026-10-20. Reviewer: CloseSoujiR13, freshly dispatched by the orchestrator, not the round author. Read-only reviewer seats: CloseSoujiR13.GateEvidence and CloseSoujiR13.SourceSpotcheck. All lane-relative pointers below resolve at measured delivery `15d95e380ca9ab61495448e3901899bcb276d4b3`, unless another revision is explicitly named.

**Closure: status ok; admitted true.** C1 calibration, C2 operability and C3 coverage improve within their declared, bounded measurements; no harmed axis was found. This is not deletion certification, complete safety coverage, universal no-write proof, or a promotion review. Scores remain legacy-unmapped 7/8/8; no numeric improvement is invented.

## Step-1 conformance

Commands actually executed by this closure (the lane is `/home/vgpnk/Projects/shokunin/souji-shokunin`, fleet `/home/vgpnk/Projects/shokunin`):

```sh
git -C <lane> status --porcelain
git -C <lane> rev-list --count '@{u}..HEAD'
git -C <lane> rev-parse HEAD
git -C <fleet> log --format='%an <%ae> %H %aI' -- .ufo/reports/round-13/souji.md
git -C <lane> log --format='%an <%ae> %H %aI' 31984f473ce4bdab61a99b16cca194b28108cb81..15d95e380ca9ab61495448e3901899bcb276d4b3
git -C <lane> merge-base --is-ancestor <each-cited-commit> HEAD
git -C <lane> diff 31984f473ce4bdab61a99b16cca194b28108cb81 15d95e380ca9ab61495448e3901899bcb276d4b3 -- SCORECARD.md
```

Observed:

- Sole status output: `?? census/operator-sweep-20261019/`. This is explicitly OPERATOR-authored, not lane round debt; its contents were not opened, edited, staged or removed. No uncommitted lane round work. Ahead count `0`; HEAD exactly `15d95e380ca9ab61495448e3901899bcb276d4b3`.
- Fleet report landed as `2f15601e049fab94f7fb40204077eedf31fac070`, `souji-shokunin <souji@shokunin.local>`, 2026-10-20T02:51:59-03:00. Lane ending commit timestamp is 02:49:56-03:00, before the report. All four round commits carry that lane identity.
- All five distinct cited full lane commits resolve and ancestry exits 0: baseline `31984f473ce4bdab61a99b16cca194b28108cb81`, `6ed10a7cd6c7b26f8068dd6e02497e860f9c4317`, `6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`, `23014d40e48e52031939f124ce0ed215ca932c6f`, ending `15d95e380ca9ab61495448e3901899bcb276d4b3`. Short command references resolve to the same commits.
- Report has real work, LOG bindings, measurements, sources/frontier, trend verdicts, and `## SHONEN` with four `[~]` evidence lines. It is not a marker. No `[x]` is written by this closure.
- Dispatched prompt `.ufo/prompts/souji-round-13.md` is committed (`306ea14b78a8d6408762cb000c0a6123d78e1ef7`). A Python literal substitution of fleet `templates/round-prompt.md` fields LANE=souji, ROUND=13, FLEET_ROOT, AXES, and `<souji-repo>`=souji-shokunin followed by `dispatched.startswith(rendered.rstrip('\n'))` returned **True**. Sections 1–5 carry the exact rendered template; campaign addendum follows. The L1 planner mapping is expressly sanctioned by that addendum.
- Committed `w1-dispatch.json` has 32 tasks, policy wave band 32–64, and role histogram: executor 7, scout 4, connector 2, reviewer 8, critic 4, sentinel 2, revenger 2, scribe 3. These match the report. This is verification of persisted dispatch evidence, not a fabricated new dispatch.

Dispatch/termination digest copied from the closure prompt (the mutable live log is not the durable pointer):

```text
2026-10-20T02:09:01-03:00 launch souji round=13 pgid=1489917 driver=hyaku-inline attempt=1
2026-10-20T02:52:19-03:00 complete souji round=13; hyaku-inline attempt=1
```

## Independently re-measured committed inventory

No lane-owned counting script, gate, selftest, fixture, or probe was executed. Python Eval ran `subprocess.run` over plain `git ls-tree`, `git show`, `git diff`, and `git merge-base`; it parsed committed text with `re`/`collections.Counter` and hashed committed blobs with `hashlib.sha256`. The count algorithm was:

```python
paths = git('ls-tree', '-r', '--name-only', revision).splitlines()
knowledge = [p for p in paths if p.startswith('corpus/knowledge/') and p.endswith('.md')]
held = [p for p in knowledge if re.search(r'^## Admission status.*\bHELD\b', git('show', revision+':'+p), re.M)]
admitted = len(knowledge) - len(held)
rows = [[c.strip() for c in line.split('|')[1:-1]]
        for line in git('show', revision+':corpus/SOURCES.md').splitlines()
        if re.match(r'^\|\s*S\d{3,}\s*\|', line)]
tiers = collections.Counter(row[3] for row in rows)
statuses = collections.Counter(row[7] for row in rows)
```

Here `git(*args)` means checked, captured `subprocess.run(['git','-C',lane,*args], text=True)`. Both exact revisions were read, not the lane's emitted counts:

| Inventory | Before 31984f4 | After 15d95e3 | Comparison with report |
|---|---:|---:|---|
| knowledge Markdown files | 5 | 6 | distinguishes existence from admission |
| HELD entries | 1 | 1 | K5 `quarantine-same-filesystem-rename.md` remains excluded |
| admitted knowledge | 4 | 5 | agrees |
| F2 bounded structure entry | 0 | 1 | agrees |
| declared-evidence gate file | 0 | 1 | agrees; inventory alone is not capability proof |
| source rows | 33 | 37 | agrees |
| A / B / C | 29 / 3 / 1 | 33 / 3 / 1 | agrees |
| mined / queued / rejected | 16 / 15 / 2 | 20 / 15 / 2 | agrees |

Old source-row byte comparisons found **0** changed existing rows; added IDs are exactly S034–S037. K5's committed file is unchanged. `git diff 6f8ee0f 15d95e3 -- tools/ tests/fixtures/` was empty; `git diff 6ed10a7 15d95e3 -- tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh` was empty. The measured executable/fixture revisions therefore still apply at delivery.

## Per-claim committed-evidence re-check

Per PROTOCOL Gate standard, these are **evidence-verified**, not gates independently re-executed. Closure parsed `git show 15d95e3:census/round-13/verification.json`, extracted each result's exit/expected exit/matched/actual measured_commit/stdout, and hashed each listed installed tool's committed bytes against `installed_sha256`. All **six** tool digest comparisons returned True. GateEvidence separately checked all **seven** frozen input digests against `tests/fixtures/r13-cert-frozen/expected.json`; all match. Registry rows are present in SKILL.md:118–137, including verdict maps, isolated self-invocation commands, expected-value locations, write scope and owner.

| Claim | Before → after, verified evidence | Verdict |
|---|---|---|
| C1 calibration | Gate absent→present re-measured. At 6f8ee0f, embedded `selftest: 36/36 passed`, external `fixture: 5/5 checks passed`, exit 0. Frozen observation at 6ed10a7: clean, fragments=2, pass=2, findings=0, frozen_files=7. Historical wrong-byte replay: `artifact-digest-mismatch`, exit 2; candidate replay: `artifact-candidate`, exit 2, both at 6ed10a7. Installed census digest `6a000c59…` is distinct from candidate `60aef4c0…`. | **improved**, declared consistency only |
| C2 operability | Corrected identical fixture at 6f8ee0f: baseline tool digest `141c0fd…` equals baseline committed tool; `SUMMARY total=5 failed=4 hung=2`, exit 1. Delivered tool `df407511…`: `SUMMARY total=5 failed=0 hung=0`, exit 0. Cases discriminate FIFO target/descendant refusal, delayed untracked move and file digest, plus a working regular-file control. | **improved**, demonstrated five-case bounds/diagnostics only |
| C3 coverage | Admitted knowledge 4→5 and F2 0→1 independently re-measured. Structure evidence at 6ed10a7: `selftest=PASS ids=5/5`, exit 0, Git 2.55.0. It includes detector controls, persistent-manifest equality, exact synthetic metrics, invalid-repository and partial/promisor-config refusal; probe and fixture are unchanged at delivery. | **improved**, bounded F2 slice only |

Regression observations at 6f8ee0f are committed: verify/vault/quarantine/census `40/51/91/36 checks, 0 failed`; warning-level ShellCheck exit 0. Closure read these outputs; it did not run these checks. `verification-attempt-1.json` retains the first failing pass. The retained frozen/replay observations name 6ed10a7 individually. The later cert-evidence change repairs only the selftest finding-id regex to accept `_`; it does not alter production frozen/replay verdict logic. External frozen-clean/frozen-tampered checks also ran at 6f8ee0f. Evidence timestamp 05:45:21Z lies after measured 6f8ee0f (05:44:18Z), before shipping commits (05:48:55Z and 05:49:56Z).

C2 does **not** establish all bound sites or all safety classes. No committed case demonstrates actual cross-device refusal, a stalled tracked `git mv`, directory digest, find/receipt-engine/special-scan timeout, or index-lock residue. Source inspection shows guards but is not an empirical acquisition of those cases. The report already excludes comprehensive safety certification; its broader implementation descriptions must not be read as extra measured capabilities. The independent reviewer supports C2's bounded improvement, not those unexercised extensions.

## Discernment spot-check and reopened sources

| Item | Lane decision | Re-opened source | Outside judgment | Reason |
|---|---|---|---|---|
| F2 `git-repo-structure-readonly.md` | admit bounded entry | [git-repo COMMANDS / structure](https://git-scm.com/docs/git-repo); committed entry, fixture, verification.json and AttackCoverage.md | **agree** | Primary documentation describes reachable-object statistics, and unchanged committed fixture evidence supports persistent state equality on its normal synthetic repository. Version/scope limits and the observed partial-clone counterexample are explicit. |
| Structure size means recoverable disk space | reject | Same git-repo structure section; [Git v2.55.0 repo.c](https://raw.githubusercontent.com/git/git/v2.55.0/builtin/repo.c) | **agree** | Ref-rooted reachable-object statistics do not establish reclaimable filesystem space, per-artifact preservation, or removal permission. |
| C1 PASS grants deletion certification | reject | SKILL.md:12–16, QUALITY Q18, verification.json and frozen/replay evidence | **agree** | Consistency cannot prove command execution, authenticated independent identity, complete safety-class coverage, or safe deletion. Certification remains OFF. |
| Re-admit K5 / revive Q15 | reject / hold | K5 Admission status HELD; QUALITY Q16/Q17; prior non-author round-12 spotcheck | **agree** | Missing committed cross-device fixture and withdrawn circular exception remain unresolved. No new integrity gate turns that held entry into admitted knowledge. |

Freshly reopened S035 quote (main reviewer and source reviewer), web manual 2.56.0, COMMANDS / structure / `table`: **“This format may change and is not intended for machine parsing.”** Exact match, **11 words**, ≤25. This supports its narrowly scoped teaches text, not universal stability/no-write claims. Source reviewer also reopened S036's optional-lock quote and tagged S037's `refs_for_each_ref` call at repo.c:744, plus skipped object-info reads at 798–801 and final zero return at 930.

S034 installed quote was independently reopened using `zcat /usr/share/info/coreutils.info.gz` through Python subprocess, then numbered `splitlines()` output. Exact text is at **15319–15320**: “Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal.” The words are accurate; the stored line numbers are not (routed below). Timeout exit 124 is at **15365**.

Required census actually executed by this closure:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```

Exit **0**, complete observed stdout:

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

W04 notices are advisory append-only correction duplicates, not validation failures.

## Axis and trend verdicts

| Axis | Verdict | Evidence / boundary |
|---|---|---|
| calibration | improved | C1 scoped discrimination and explicit withdrawal of historical installed-tool certification authority |
| operability | improved | C2 identical-fixture red/green, retained regressions; no broad deletion-safety certificate |
| coverage | improved | C3 one sourced admitted F2 entry and demonstrated bounded probe |
| depth | unchanged | unworked; no contrary admitted-domain claim found in spot reads |
| freshness | unchanged | no independent stale-knowledge sweep claimed |
| adjacency | unchanged | PROVINCE retains sibling/operator boundaries; F2 metrics and local fragment checks do not take fleet orchestration or removal authority |

- **Expansion: improved.** One new admitted knowledge entry on formerly uncovered F2 ground, source trio S035–S037 mined, coverage-map and PROVINCE bounded core refinement; not four rows counted as knowledge.
- **Quality: unchanged.** Corrected source overclaims and improved operations are real, but no separate existing admitted-entry freshness/supersession sweep is claimed. K5 stays visibly held rather than false admission.
- **Discernment: improved.** Outside sampling agrees on admits and rejects; prior K5 disagreement is mined as R13-M1/Q17 and executable missing-evidence rejection. Q18 separates integrity/safety; Q19 replaces spelling-count enforcement with behavior. Lane-dispatched seats are not treated as outside reviewers.

## Routed findings and review adjudication

1. **Souji next round — citation correction, status-neutral:** S034's immutable anchor in `corpus/SOURCES.md:44` and the located quote in `corpus/lessons/round-13.md:42` give 15316–15317 and exit-status 15349. Actual quote is **15319–15320**, exit 124 **15365**; 15349 is verbose diagnostics. Append a source correction row superseding S034 (do not rewrite immutable cells) and a named lesson erratum. Quote content/timeout fact is correct; this does not invalidate bounded claim outcomes.
2. **Souji next round — keep C2's evidence scope explicit:** cross-device refusal and the unexercised bound/residue sites listed above are implementation-only observations, not this round's demonstrated capability. When revisited, distinguish them with isolated committed cases or retain explicit unproved labels. K5 remains held, certification OFF. This is a limitation/routing item, not a demand to expand the admitted five-case claim retroactively.
3. **Retention caveat, not a current claim failure:** the runner's retained-green selection does not itself compare tool digests before retaining an old observation. This closure checked unchanged files and the sole production-irrelevant parser delta directly. Actual per-result revisions plus the report's explicit retained-run disclosure are authoritative; top-level measured_commit must not erase them.

Reviewer proposals adjudicated: S037 `add_tree_entries:146` is an interior call-site anchor within the named function, not a false function-definition claim. A fixture author's “not executed by this seat” header is compatible with a subsequent main-agent run; unchanged committed fixture identity binds its observed result without requiring it in an installed-tool-only digest map. Stating delimited output does not promise universal no-writes is a valid bounded reading, not an unsupported assertion of universal write safety. The claimed absent K5 HELD marker was withdrawn: it exists at line 51. These are not routed defects.

SHONEN remains four author `[~]` marks. This closure does not certify every box as fully independently checked: in particular, it did not re-review the historical live end-to-end task or execute operational instructions. Promotion remains operator-owned. No operator/cross-domain mutation, promotion, mint or L0 question was made. Tool installs/updates: **none**.
