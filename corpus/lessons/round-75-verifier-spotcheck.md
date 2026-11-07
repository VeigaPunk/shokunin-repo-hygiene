# Round 75 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatch digest (copied from `.ufo/watchdog.log` because the log is mutable):
`2026-11-06T21:19:27-03:00 launch souji round=75 pgid=51262 driver=hyaku-inline attempt=1`;
`2026-11-06T21:58:55-03:00 complete souji round=75; hyaku-inline attempt=1`.
Lane base `52d3f07d08422689464598f8be7e2c957fcf0805`, lane tip `a4554ca19f991f24a58077fc43c787c19750d413`.
The closure authored no round byte and ran no lane gate, counter or selftest (PROTOCOL §Gate standard,
Closure consequence). Gate/counter/selftest numbers below are evidence-verified from committed receipts
(`git show a4554ca1:<path> | grep`), with every pinned instrument, population and gate digest re-hashed by the
closure. The ignore-listing difference, source bytes, quotes, SOURCES row count and census were re-measured by
the closure itself.

## Conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-75/souji.md` | `souji-shokunin <souji@shokunin.local> f2fe13d274feba77ae6d91e7ecdecbf19055ae08 2026-11-06 21:58:25 -0300`; after the lane tip (21:57:41), before `complete` (21:58:55) | pass |
| `SHONEN` heading, one line per box | read report lines 81-86 | one `## SHONEN` heading, 4 lines, all `[~]`, each with an evidence pointer | pass |
| cited lane commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> master` for 7ba5217d be599cbb f6ec0d71 1ad737b4 5d10e09e 3564e925 c8dabbd7 a4554ca1 (full hashes) | all 8 `ok`, all authored by `souji-shokunin`; `git log 52d3f07d..master` lists exactly these 8 | pass |
| lane pushed, nothing left over | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `state branch=master local=a4554ca1… remote=a4554ca1… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; ls-remote `a4554ca1…` | pass |
| prompt carries the template contract | `diff <(head -140 .ufo/prompts/souji-round-75.md) kimi-shokunin/templates/round-prompt.md` | only `{{LANE}}`/`{{ROUND}}`/`{{FLEET_ROOT}}`/`{{AXES}}` substitutions differ; §1-§5 verbatim, then hyaku addendum §6/§7 and run15 notes | pass |
| chronology P → F → I → W | `git show --name-only --format= <c>` | P `7ba5217d` 20 files (no prereg, gate or candidate); F `be599cbb` only `preregistration.txt`; I `f6ec0d71` only `census/round-75/c1-counter.py`; W `1ad737b4` only `tools/souji-pre-report-gate.sh` (+18) | pass |
| frozen inputs untouched after freeze | `git diff --stat be599cbb a4554ca1 -- census/round-75/{preregistration.txt,controls,c1-evade-counter.py,c1-population.tsv,c2-kill-counter.py,c2-mutants.json}` | empty | pass |
| prereg digests | `git show 7ba5217d:<path> \| sha256sum` | c1-evade-counter `9ed4a97b…9a17`, c1-population `85257260…0343`, c2-kill-counter `fdb75c09…1c35`, c2-mutants `612e89e2…b533` — all equal the prereg | pass |
| fleet misroot | `git -C /home/vgpnk/Projects/shokunin status --porcelain` | `.scratch/*` (orchestrator) and `?? trail-ids.txt`, none souji's | pass |

## Claims

### C1 — operability (pre-report gate ignore-source rule): **improved** (evidence-verified; ignore listing re-measured)

- Before: `git show a4554ca1:census/round-75/controls/c1-K-a-do-nothing.txt | grep -E 'match=no|^SUMMARY|^EXIT='` → `ROW f-info-exclude expect=FAIL clean=PASS rc=0 match=no`, `ROW f5-info-exclude-dir … match=no`, `SUMMARY rows=25 mismatches=2 errors=0`, `EXIT=1`; `rev=52d3f07d…`, bound gate `062b6d39…d341` = `git show 52d3f07d:tools/souji-pre-report-gate.sh | sha256sum`.
- Blanket control K-b: `SUMMARY rows=25 mismatches=3 errors=0`, `EXIT=1` (stays red, as frozen).
- After: `records/c1-after.txt` → 25/25 `match=yes`, `SUMMARY rows=25 mismatches=0 errors=0`, `EXIT=0`; bound gate `620ed97e…2b96` = `git show 1ad737b4:tools/souji-pre-report-gate.sh | sha256sum`. `records/wave-repair/c1-at-repair.txt` identical. The r74 imported rows keep their FAILs (kill clause not triggered).
- Domain trial `records/c1-domain-trial.txt`: `check-tip/report/shonen/clean/prereg=PASS`, `EXIT=0`, `rev=c8dabbd7`; amendment line names W blob `620ed97e…` → repaired blob `ef3b04e4…356a`, which equals `git show 3564e925:tools/souji-pre-report-gate.sh | sha256sum` and the tip's gate. The prereg's amendment clause is honoured (r74 routed defect 1 closed).
- Closure re-measurement on the live lane: `git --no-optional-locks ls-files -o -i --exclude-standard | wc -l` = 26152 and `… --exclude-per-directory=.gitignore | wc -l` = 26152 (difference 0; the receipt's 26133 at c8dabbd7 predates later ignored bytes); `git rev-parse --show-toplevel` = the lane; no `info/exclude` patterns, no `core.excludesFile`.
- Result: matches the report (2 → 0, EXIT 1 → 0, K-b red, trial PASS). Sourced claim: S318/S319 re-fetched by the closure (below) and support the set difference.
- Qualifications already disclosed by the lane and accepted: f3 (core.excludesFile) was refused at base by the writer's pinned status, so only the info/exclude arm moved; the stated limit f7 (self-ignoring `.gitignore`) is labelled PASS in the prereg.

### C2 — calibration (witness-counter second detectors): **improved** (evidence-verified)

- Before: `controls/c2-K-do-nothing-r74.txt` → `SUMMARY mutants=6 killed=4 survived=2 unread=0 pristine=PASS`, `EXIT=1`. Blanket `c2-K-blanket-pristine-red.txt` → `pristine=FAIL`, `EXIT=1`.
- After: `records/c2-after.txt` → `MUTANT X09|P1|M08|M14 fail=1 … KILLED`, `M15|M17 fail=2 … KILLED`, `PRISTINE fail=0 exit=0 verdict=PASS`, `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS`, `EXIT=0`; instrument sha `fdb75c09…` = prereg.
- Pristine selftest `records/c2-after-pristine-selftest.txt`: `instrument_sha256=90a3c7b2…` = `git show f6ec0d71:census/round-75/c1-counter.py | sha256sum`; `SELFTEST cases=64 pass=64 fail=0`, `EXIT=0`.
- Result: matches the report (4 → 6 of 6). Lane-disclosed survivors (Y4/Y5, selftest-block mutants, UNREAD boundary unreceipted) routed to r76.

### Axis harm

- `git diff 52d3f07d a4554ca1 -- SCORECARD.md`: 13 insertions, 0 deletions — two r75 capability rows, r75 done / r76 planned lines, `### Round 75 measurements`. No score changed: calibration 7, coverage 8, operability 8.
- Spot reads: QUALITY Q136 (line 352) supersedes only Q135's ignored-files limit clause; SKILL rows 937-938 register both r75 instruments; LOG `## Round 75` at line 2995; lesson `## Mistakes` M1-M6; knowledge `filter-filemode-witness.md` +58 lines.

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1, 2 → 0 mismatches, K-b red, domain trial PASS on the repaired gate with a recorded amendment |
| calibration | improved | C2, 4 → 6 of 6 killed, pristine 64/64, blanket red |
| coverage | unchanged | not claimed; SCORECARD score unchanged |

## Discernment spot-check (`corpus/lessons/round-75.md` `## Gate`)

Fetch: `curl -sS https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/{gitignore,git-ls-files}.adoc` → HTTP 200, 9535 bytes sha256 `338221577b4f…5e71` and 12123 bytes sha256 `56af3aad88df…a74b`, both equal to the rows. Quotes located in the whitespace-normalised text with Python `str.find`.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S318 gitignore(5) v2.56.0, anchor "Patterns read from exclude sources that are outside the working tree, such as $GIT_COMMON_DIR/info/exclude and core.excludesFile" | admit (A, mined) | gitignore.adoc fetch above; found at normalised offset 3807, 16 words | agree | Verbatim at the cited offset, ≤25 words. It names both local sources as outside the working tree, which is exactly the premise that makes them unversioned and therefore a lane change. Primary doc at a pinned tag: tier A is right. |
| S319 git-ls-files(1) v2.56.0, anchor "give `--exclude-per-directory=.gitignore`, and then specify: 1. … core.excludesfile … 2. The `$GIT_COMMON_DIR/info/exclude` file." | admit (A, mined) | git-ls-files.adoc fetch above; found at normalised offset 11458, 24 words | agree | Verbatim, 24 words (≤25). It states that `--exclude-per-directory` alone omits the two local sources, which is the set difference the gate computes. |
| first S318 anchor "Patterns which are specific to a particular repository but which do not need to be shared with other related repositories" | reject (anchor) | same gitignore.adoc fetch; text found (normalised offset 1650), 20 words; the sentence continues "… should go into the `$GIT_COMMON_DIR/info/exclude` file" | agree | Real text, but the clause naming info/exclude lies after the quote, so the anchor cannot ground the claim. Replacing it before landing was right. |
| S318 27-word anchor "Patterns which should be version-controlled …" | reject (anchor) | same fetch; found, 27 words | agree | Over the 25-word bar. |

- SOURCES rows: `git diff 52d3f07d a4554ca1 -- corpus/SOURCES.md` adds exactly S318 and S319, no removed or changed row; row count `grep -cE '^ {0,3}\| *S[0-9]{3,}'` 240 → 242. S318's row quote (line 277) is the 16-word anchor verified above.
- Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 86 `W04` (duplicate-URL warnings, unchanged from the committed before/after receipts), `EXIT=0`.

## Trend verdicts

- **expansion: improved.** Two new tier-A `mined` rows (S318, S319) on ground the lane did not hold — which exclude sources are versioned policy, and how ls-files composes them — cited by `filter-filemode-witness.md` r75; the gate gained an ignore-source rule and a work-tree check; two capability rows.
- **quality: improved.** Q136 narrows Q135 by superseding only its limit clause. The core.worktree forgery and the r36 fixture regression were repaired in-round with W-vs-R receipts (`coreworktree-W.txt` `check-clean=PASS` → `coreworktree-R.txt` `check-clean=FAIL … RECEIPT-WORKTREE-REDIRECTED`; r36 `18/21` at W → `21/21` amended at base and at repair). No admitted entry failed its re-check here.
- **discernment: improved.** The non-author spot-check agrees with the gate on both admits and both rejects; the lane replaced two under-reaching anchors on a seat's falsification, ruled the r74 probe's mislabels in its prereg, and disclosed its own over-strong prereg description (M6) and the core.excludesFile attribution.

## Routed defects (lane fixes next round)

1. **Probe that cannot fail.** `census/round-75/records/wave-repair/probes/repro-coreworktree.sh:20` prints a static legend `gate rc=$? (0+check-clean=PASS … = FORGERY)` and the receipt ends `EXIT=0` for both W and R; the verdict is read off `check-clean` by eye. Emit a computed `FORGERY|REFUSED` line and a nonzero exit on forgery, or register it as a probe (PROTOCOL §Gate standard).
2. **C1 core.excludesFile arm undiscriminated.** Row f3 FAILed at base because the receipt writer pins `-c core.excludesFile=/dev/null`, so no frozen row shows the new rule is the one refusing that source. Add a row that separates the two.
3. **Domain-trial revision.** The trial ran at `c8dabbd7`, not the cited tip; disclosed, and the tip only adds the receipt (`git diff --stat c8dabbd7 a4554ca1` = 1 file). Keep stating the measured revision.
4. **Lesson routed items (a)-(d)** stay on the queue: Y4/Y5 post-only and base-aliased witnesses; the kill tally's EXIT=2 / `fail=0 EXIT=1` classes and receipt-to-mutant binding (S75MutCounter M1/M2, S75Reviewer O2); the gate's ls-files failure branch and refusal class (S75MutGate F3/F4); other status-trusting lane tools, nine sibling gates, writer M03.
5. **Stated limit.** A self-ignoring untracked `.gitignore` (f7, the `.jj/` shape) and broad committed rules still hide content; prereg's "committed .gitignore rules only" was wrong (M6). Keep the limit on the queue until a row fixes it.
