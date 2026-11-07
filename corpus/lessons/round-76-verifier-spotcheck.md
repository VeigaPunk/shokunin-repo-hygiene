# Round 76 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatch digest (copied from `.ufo/watchdog.log` because the log is mutable):
`2026-11-06T22:02:33-03:00 launch souji round=76 pgid=4163885 driver=hyaku-inline attempt=1`;
`2026-11-06T22:44:12-03:00 complete souji round=76; hyaku-inline attempt=1`.
Lane base `ee59aa4da358d38850ccace194f7cd558ee45ce9`, lane tip `1524bc8160784d030fb7c7122ae266ca77463981`.
The closure authored no round byte and ran no lane gate, counter, tally, probe or selftest (PROTOCOL §Gate
standard, Closure consequence). Gate/counter/tally/probe numbers below are evidence-verified from committed
receipts (`git show 1524bc81:<path> | grep`), with every pinned instrument, population, forged case and gate blob
re-hashed by the closure. Source bytes, quotes and word counts, the b-neg git behaviour, the SOURCES row count, the
tracked state of every attributed `.gitignore`, and the census were re-measured by the closure itself.

## Conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-76/souji.md` | `souji-shokunin <souji@shokunin.local> c2b1474104e03ba19f2528e8f241999217c0d5b9 2026-11-06 22:43:46 -0300`; after the lane tip (22:42:51), before `complete` (22:44:12) | pass |
| `SHONEN` heading, one line per box | read report lines 87-92 | one `## SHONEN` heading, 4 lines, all `[~]`, each with an evidence pointer | pass |
| cited lane commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> master` for the 12 cited full hashes (6c9c2a8e … 1524bc81) plus the base | all `ok`, all 12 round commits authored by `souji-shokunin`; `git log ee59aa4d..master` lists exactly these 12 | pass |
| lane pushed, nothing left over | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git status --porcelain \| wc -l`; `git ls-remote origin refs/heads/master` | `state branch=master local=1524bc81… remote=1524bc81… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain 0 lines; ls-remote `1524bc81…` | pass |
| prompt carries the template contract | `diff <(sed -n 1,140p kimi-shokunin/templates/round-prompt.md) <(sed -n 1,140p .ufo/prompts/souji-round-76.md)` | only `{{LANE}}`/`{{ROUND}}`/`{{FLEET_ROOT}}`/`{{AXES}}` substitutions differ; §1-§5 verbatim, then hyaku addendum §6/§7 and run15 notes; prompt committed `62c3a8a7` before launch | pass |
| chronology P → F → I → W | `git show --name-only --format= <c>` | P `6c9c2a8e` 18 files (no prereg, gate, tally or `.gitignore`); F `2ed6b179` only `preregistration.txt`; I `2c7c1ce6` only `c2-kill-tally.py`; W `e827d2bf` only `.gitignore` + `tools/souji-pre-report-gate.sh` | pass |
| frozen inputs untouched after freeze | `git diff --stat 2ed6b179 master -- census/round-76/{preregistration.txt,controls,c1-evade-counter.py,c1-population.tsv,c2-binding-counter.py,c2-population.tsv,c2-cases}` | empty | pass |
| prereg digests | `git show 1524bc81:<path> \| sha256sum` | c1-evade-counter `618e4f9a…ab0e`, c1-population `937e4a9b…c8f5`, c2-binding-counter `e22f634e…6ca9`, c2-population `c46ea8ff…cb25c`, three c2-cases `dcc28f06…`, `ae80a80f…`, `ac0b1b5c…` — all equal the prereg | pass |
| fleet misroot | `git -C /home/vgpnk/Projects/shokunin status --porcelain` | ` M .scratch/*` (orchestrator) and `?? trail-ids.txt` (pre-existing, not souji's); nothing from this lane | pass |

## Claims

### C1 — operability (pre-report gate ignore-source attribution): **improved** (evidence-verified; attribution inputs re-measured)

- Before: `git show 1524bc81:census/round-76/controls/c1-K-a-do-nothing.txt | grep -E 'match=no|^SUMMARY|^EXIT='` → `match=no` on `f7-selfignore-dir f9-selfignore-nested f10-selfignore-named f14-selfignore-in-tracked-dir`, `SUMMARY rows=30 mismatches=4 errors=0`, `EXIT=1`; `rev=ee59aa4d…`; bound gate `ef3b04e4…356a` = `git show ee59aa4d:tools/souji-pre-report-gate.sh | sha256sum`.
- Controls stay red: K-b blanket `match=no` on `f2 f6 f11 f12`, `mismatches=4`, `EXIT=1`; K-c naive `match=no` on `f11-committed-dir-rule`, `mismatches=1`, `EXIT=1`. Both bound to the frozen counter sha.
- After: `records/c1-after.txt` → 30/30 `match=yes`, `SUMMARY rows=30 mismatches=0 errors=0`, `EXIT=0`, `rev=e827d2bf`; bound gate `18587bd2…23ad` = `git show e827d2bf:tools/souji-pre-report-gate.sh | sha256sum`. `records/wave-repair/c1-at-repair.txt` identical with gate `90bdd8c7…47f3` = `git show 9cbfd296:…` = tip blob.
- Regression conjunct: `c1-regress-r36.txt` `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` EXIT=0; `c1-regress-r27.txt` `cases=4 pass=4 control=FALSE-GREEN-REJECTED` EXIT=0; both instrument digests (`c9d933ec…`, `20763efd…`) equal the tip blobs; repair-time copies identical.
- Domain trial `records/c1-domain-trial.txt`: `check-tip/report/shonen/clean/prereg=PASS`, `EXIT=0`, `rev=27e5e289`, amendment line `18587bd2… -> 90bdd8c7…` (prereg amendment clause honoured). Closure re-check of its attribution line: every source it lists (`.gitignore`, `tests/fixtures/case-F7/repo-tree/.scratch/.gitignore`, `case-F8/…`, `tests/vault/case-V6/.gitignore`, `tests/vault/vadv-49/.gitignore`) is tracked at 27e5e289 (`git cat-file -e 27e5e289:<p>`); `git ls-tree -r --name-only 27e5e289 | wc -l` = 19573 = the receipt's `tracked=`.
- Wave repair evidence: `records/wave-repair/repair-probes.txt` → 8 ROW `match=yes` (fsmonitor W PASS / R FAIL; GIT_EXEC_PATH W EXEC / R NO-EXEC; single-path R FAIL / M09 PASS; nested `.jj` W PASS / R FAIL), `SUMMARY arms=8 as_expected=8`, EXIT=0.
- Spot read of the gate diff (`git diff ee59aa4d 1524bc81 -- tools/souji-pre-report-gate.sh`): tracked set from `ls-tree -r -z --full-tree HEAD`; `check-ignore -v -n -z --stdin` under `core.excludesFile=/dev/null` and `core.fsmonitor=false`; record count and echoed path verified; a path counts declared only when its source is a tracked `.gitignore` in an ancestor directory and the pattern is not a negation. Matches the claim and S320's OUTPUT section.
- Result: matches the report (4 → 0, EXIT 1 → 0, K-b/K-c red, r36 21/21, r27 4/4, trial PASS). Sourced claim on S320 holds (re-opened below).
- Qualifications disclosed by the lane and accepted: frozen rows carry two undeclared paths each, so a refuse-above-one gate (M09) passes the frozen counter (killed only by the repair probe); the fsmonitor forgery of the W candidate was repaired after measurement; the domain trial depends on the W `.gitignore` declaring `/.jj/` (a tracked rule deciding is the rule working).

### C2 — calibration (receipt-bound mutant-kill tally): **improved** (evidence-verified)

- Before: `controls/c2-K-do-nothing-r75.txt` (r75 tally) → `match=no` on `b-swap-x09-gets-m08 b-swap-p1-gets-x09 b-pristine-r74 b-unknown-id b-exit-disagree`, `SUMMARY cases=10 mismatches=5 errors=0`, `EXIT=1`, `rev=ee59aa4d`.
- Blanket reject-all `controls/c2-K-b-blanket-reject-all.txt`: `match=no` on `h-honest h-honest-reordered`, `mismatches=2`, `EXIT=1` (stays red).
- After: `records/c2-after.txt` → 0 `match=no`, `SUMMARY cases=10 mismatches=0 errors=0`, `EXIT=0`, `rev=e827d2bf`; `ROW h-honest … SUMMARY mutants=6 killed=6 survived=0 unread=0 unbound=0 pristine=PASS`. `records/wave-repair/c2-at-repair.txt` identical at `rev=9cbfd296`. `tally-probes.txt` 8/8 (by-name arm: M08 bytes under X09's name rejected by both I and R).
- Result: matches the report (5 → 0, EXIT 1 → 0, blanket red, killed=6).
- Qualifications disclosed and accepted: the binding counter compares exit codes only (S76MutTally K03/K04) and the frozen population is file-name separable (S76CriticClaims); the r76 tally itself binds bytes. Binding names the instrument, it does not prove the run (stated limit). These weaken the instrument's kill power, not the frozen predicate, and are routed to r77.

### Axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 (frozen 30-route counter 4 → 0, controls red, r27/r36 green, domain trial PASS) |
| calibration | improved | C2 (frozen 10-case counter 5 → 0, blanket red, honest killed=6) |
| coverage | unchanged | `git diff ee59aa4d 1524bc81 -- SCORECARD.md`: axis scores unchanged (calibration 7, coverage 8, operability 8); two capability rows added marked `r76 (closure-gated)`, r76 measurements block and r77 plan appended; no row rewritten |

No axis harmed. r75 routed defect 1 closed: `probe-coreworktree-at-r75W.txt` `VERDICT=FORGERY EXIT=1` over gate `620ed97e…` (= `git show 1ad737b4:tools/souji-pre-report-gate.sh | sha256sum`), `-at-r76W.txt` `VERDICT=REFUSED EXIT=0` over `18587bd2…` (pinned in `probe-coreworktree-gates.sha256`).

## Discernment spot-check

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S320 git-check-ignore(1) v2.56.0 | admit (A, mined) | `curl https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-check-ignore.adoc` → HTTP 200, 4159 bytes, sha256 `940177c7…8208`, `cmp` identical to `census/round-76/srcs/git-check-ignore.adoc` | agree | quote "<source> is the pattern's source file, and <linenum> is the line number of the pattern within that source." found at offset 2355 of the whitespace-normalized text, 18 words (≤25); the gate parses exactly the four `-z --verbose` NUL fields the OUTPUT section defines |
| `-n` anchor sentence | reject (over the 25-word bar; paraphrased) | same capture | agree | found at normalized offset 3013, 27 words by `split()` — over the bar, so not quotable; the paraphrase in the knowledge entry is faithful (non-matching records carry empty fields) |
| source-form sentence | reject (over the bar; paraphrased) | same capture | agree | found at offset 2555, 29 words (lane says 29-30) — over the bar |
| S76ExecEvade b-neg "FORGERY HIGH" | reject (seat finding disagreed) | closure fixture: tracked root `.gitignore` `hidden/`, untracked `hidden/.gitignore` `!payload`, `hidden/payload`; `git ls-files -o -i --exclude-standard -z \| git -c core.excludesFile=/dev/null check-ignore -v -n -z --stdin` | agree | both paths attribute to `.gitignore:1:hidden/` (the tracked root rule); `git status --ignored` shows `!! hidden/` — git does not descend, so the negation never applies. This is the declared broad-committed-rule limit (f2/f11 shape), not a forgery of the r76 rule |

New SOURCES row re-opened: S320 (above); its row quote equals the lane's `## Gate` quote and the anchor names OUTPUT, `--verbose`, offset 2355, lines 81-82 (closure `sed -n 78,95p` of the fresh fetch: the quoted clause spans raw lines 81-82 — consistent). Row count `grep -cE '^ {0,3}\| *S[0-9]{3,}' corpus/SOURCES.md`: 242 at `ee59aa4d` → 243 at `1524bc81` (matches the report). S320 cited by `corpus/knowledge/filter-filemode-witness.md` (line 244) and QUALITY Q137.

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, 86 `W04` (duplicate-URL-across-scopes warnings), EXIT=0; equals `census-before.txt` and `census-after.txt` (86 W04 each).

## Trend verdicts

- **expansion: improved** — one new tier-A `mined` row (S320) on ground the lane did not hold (closure: `git show ee59aa4d:corpus/SOURCES.md | grep -c check-ignore` = 0), cited by an admitted knowledge entry and Q137; two capability rows demonstrated running this round (c1-after, c2-after, probes).
- **quality: improved** — wave forgeries (fsmonitor, GIT_EXEC_PATH, unanchored `.jj/`, substring `--selftest`) repaired with W-vs-R receipts that fail on the unrepaired arm (`repair-probes.txt`, `tally-probes.txt` 8/8 each); the r75 probe that could not fail now computes FORGERY/REFUSED; Q137 supersedes Q136's limit clause by a new row. No admitted entry failed its re-check.
- **discernment: improved** — the closure agrees with the gate on the admit (S320) and on all three rejects sampled (two over-bar anchors, b-neg); the lane recorded instrument kill-power gaps instead of re-scoring.

## Routed defects (lane fixes next round)

1. Domain-trial receipt `records/c1-domain-trial.txt` names `command=bash /fast/scratch/…/trial.sh` and binds no digest of that script; the committed `census/round-76/probes/domain-trial.sh` (sha256 `a884ece3…3df1`) is asserted, not bound, to be it. Bind the trial script's digest in the receipt (or run the committed path).
2. The domain trial read the report before its final-hash fill-in (disclosed); the gate's `check-report` verdict therefore grades bytes that differ from the filed report. Run the trial against the filed bytes or record their digest.
3. Kill power of the frozen instruments (S76MutGate M09; S76MutTally K03/K04; filename-separable C2 population) — already routed by the lane as r77 (a)/(b); carry until a successor population/counter lands.
4. S76Sentinel MEDIUM-2 (no timeout; FIFO `.gitignore`/`core.excludesFile` hangs the gate) and r75 routed defect 2 (core.excludesFile arm discrimination) remain open — lane r77 (a).
5. Sibling note (report only, not routed by souji): S76Sentinel LOW-2 — sibling lanes carry an untracked `.jj/.gitignore`; any sibling adopting this gate rule must declare `/.jj/` first.

SHONEN: all four boxes `[~]` with pointers that a non-author can check (SKILL gate rows at `5827817c`, LOG "## Round 76" with a domain trial, seats reproducing prereg commands, PROVINCE/adjacency notes). Promotion is operator-owned; noted for the operator only.
