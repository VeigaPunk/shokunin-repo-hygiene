# souji round 81 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane round 81, base `b15279bbc3f11ec10fc375a05a08b19cac460d0c`, after `492da800c92d703ce1011b75d219dbb77970a545`
(branch `master`). Report `.ufo/reports/round-81/souji.md` (fleet repo commit `99c5d50ddcca8fca0e78164a482892b1cd4f6ac5`,
author `souji-shokunin`, 06:59:34; committer 07:03:44 after the lane tip's 07:02:14, so the report names a hash that
existed when it was written). Driver digest (`.ufo/watchdog.log`): `2026-11-07T05:55:23-03:00 launch souji round=81
pgid=3536507 driver=hyaku-inline attempt=1`; `2026-11-07T07:04:22-03:00 complete souji round=81; hyaku-inline attempt=1`.

Outcome: status `ok`, **admitted**. C1 verifies (re-measured by me); C2 verifies on its frozen predicate at W2
(re-measured by me) and at the tip bytes R (`89a2ed8c…`, re-measured by me) under the default and `&` launches; the
W2 harm is repaired behind a probe that fails on the earlier bytes; the SHELLOPTS=monitor residual is reproduced by
me at the tip and is a residual against the preregistered stated limit, not a harm against the base. No owned axis is
harmed at `492da800`.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-81/souji.md` | `souji-shokunin 99c5d50ddcca8fca0e78164a482892b1cd4f6ac5` (author 06:59:34, after lane HEAD 492da800 author 07:01:31; committer 07:03:44) | pass |
| `## SHONEN` heading, one line per box | read report; `grep -nE '^\s*- \[[ x~]\]' SHONEN.md` | 4 report lines, all `[~]` with pointers; SHONEN.md has 4 boxes | pass |
| cited commits exist and are ancestors of `master` | `git cat-file -t <h>` + `git merge-base --is-ancestor <h> master` over 13 hashes (base, P, F, W1, W2, A, I, I2, D, R, R receipts, mirror, census-after) | 13/13 `commit anc` | pass |
| lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain \| wc -l` | `branch=master local=remote=492da800… ahead=0 behind=0 tracked=0 untracked=0`; 0 | pass |
| prompt carries the template contract | read `.ufo/prompts/souji-round-81.md` §4/§5/§6 and §2/§2b | report path, sections (incl. Sources & frontier, Trend verdicts, SHONEN), marker rule, commit-then-push, push scope, L0, 1–3 claims on the lowest non-retired axis, Frontier step, L2 minimum, MISSION/AXES | pass |

Observations (status-neutral): P `804f132e` author date 05:54:31 is 52 s before the driver launch line 05:55:23; its
committer date is 06:15:27 and every later commit's author date equals its parent's committer date — the jj
working-copy change-creation timestamp, not a pre-launch commit (same pattern as r80). The r81 preregistration and
census receipts bind `scripts/sources-census.sh` sha256 `3fb72615…64e30`, equal to the script on disk now.

## 2. Claims

Both claims rest on lane-owned instruments (C1 harness + counter, C2 signal counter) and on the tool's selftest and
the r17 fixture. Per PROTOCOL §Gate standard (Closure consequence) I did not treat any lane gate as executed by me;
below, **re-measured** means I ran the committed instrument bytes myself from the lane root against a scratch
`--work` under `/fast/scratch/hyaku/close-souji-r81/` (the instruments refuse `/tmp`), and **evidence-verified** means
I re-read committed receipts and re-hashed the bytes they bind.

Instrument and candidate digests (`git show <c>:<path> \| sha256sum`, first 12 hex):

| object | at F `0b1aeaf1` | at W1/W2 `308bc77b`/`7076ed2d` | at R `ef76a14f` | at tip `492da800` | prereg value | result |
|---|---|---|---|---|---|---|
| `census/round-81/c1-false-row-harness.py` | `292bf75eead7` | same | same | same | `292bf75e…3166d` | frozen |
| `census/round-81/c1-false-rows.tsv` | `3753e4379623` | same | same | same | `3753e437…3dbda` | frozen |
| `census/round-81/c1-pointer-counter.py` | absent | `ca97b984a391` | same | same | W1 receipt binds `ca97b984…` | candidate after F, unchanged to tip |
| `census/round-81/c2-vault-signal-counter.py` | `0756063405a2` | same | same | same | `07560634…47554` | frozen |
| `census/round-81/c2-population.tsv` | `1169dd2bc7fa` | same | same | same | `1169dd2b…48c3b` | frozen |
| `tools/souji-vault-verify.sh` | `5cb0fb13fc9b` (base) | `ba61e9128a49` (W2) | `89a2ed8c3ce0` | `89a2ed8c3ce0` | base blob `5cb0fb13…810bb`, W2 `ba61e912…aa13` | tip = R |

`git show 492da800:tools/souji-vault-verify.sh \| sha256sum` = `89a2ed8c…`; the git blob id at tip is
`51847933eaef…`, equal at R and tip.

### C1 — calibration (lowest owned axis, 7): **verified** (re-measured)

Command I ran (from the lane root, lane = the lane repo, fleet-root = `/home/vgpnk/Projects/shokunin`):
`python3 -B census/round-81/c1-false-row-harness.py --counter census/round-81/c1-pointer-counter.py --lane
/home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work
/fast/scratch/hyaku/close-souji-r81/c1w` → `SUMMARY rows=25 mismatches=0 accepted=0 refused_true=0 errors=0`, `C1_EXIT=0`.
The three rows the r80 counter fails are the ones I saw flip: NF12, NF12c, NF12d now `match=yes` (each `got=REFUSED`),
and the 22 other rows stay `match=yes`.

Evidence-verified receipts (`git show 492da800:census/round-81/<f> \| grep -E '^(rev=\|SUMMARY\|EXIT)'`):
- Before, `controls/c1-K-a-r80-counter.txt` (rev base, counter `90ed9031…`, the r80 counter): `SUMMARY rows=25
  mismatches=3 accepted=3 refused_true=0 errors=0`, `EXIT=1`; the three `match=no` rows are NF12, NF12c, NF12d.
- After, `records/c1-after.txt` (rev `308bc77b`, counter `ca97b984…`): `rows=25 mismatches=0 accepted=0 refused_true=0
  errors=0`, `EXIT=0`; 25 `match=yes` lines.
- Controls red as preregistered: K-b refuse-all `mismatches=3 refused_true=3` `EXIT=1`; K-c without-suffix
  `mismatches=1 accepted=1` `EXIT=1` (the one `match=no` row is NF12c).
- Regressions green: r77 `items=35 resolved=35` + `FORGE-SUMMARY forged=7 matched=7 accepted=0`; r78 `items=22
  resolved=22` + `forged=12 matched=12 accepted=0`; r79 harness (`5d5bd236…`) `rows=9 mismatches=0`; r80 harness
  (`6f22b68a…`) `rows=18 mismatches=0`; all `EXIT=0`.

Reported 3 → 0 equals what I measured. Qualifications carried, none a harm: the suffix binding's only pressure is
NF12c (NF12c/NF12d falseness is stipulated by the L1, S81CriticClaims); mutants M7 and M8 survive; a byte-equal decoy
in the token's own round tree is accepted because the rule never runs there; the prereg's stated-limit example is in
fact refused. All routed to r82 in the lesson `## Routed to round 82` (b).

### C2 — operability: **verified** on its frozen predicate (re-measured at W2 and at R), with the launch-mode ruling

Command I ran for W2: extracted `git show 7076ed2d:tools/souji-vault-verify.sh` to a scratch file (sha256
`ba61e9128a49…`, mode 755) and ran `python3 -B census/round-81/c2-vault-signal-counter.py --tool <that file> --work
/fast/scratch/hyaku/close-souji-r81/c2w2` → `SUMMARY rows=12 mismatches=0 errors=0 orphans=0`, `C2W2_EXIT=0`; 0 rows
`match=no`. For R (the tip bytes): `git show ef76a14f:tools/souji-vault-verify.sh` (sha256 `89a2ed8c3ce0…`) with
`--work …/c2wr` → `SUMMARY rows=12 mismatches=0 errors=0 orphans=0`, `C2R_EXIT=0`. The A commit `cb14eae7` does not
touch the tool (`git diff 7076ed2d cb14eae7 -- tools/souji-vault-verify.sh` empty), so the W2 bytes are the A bytes.

Evidence-verified receipts:
- Before, `controls/c2-K-a-do-nothing.txt` (rev base, tool `5cb0fb13…`): `rows=12 mismatches=8 errors=0 orphans=8`,
  `EXIT=1`. K-b trap-only `mismatches=8 orphans=8`; K-c no-stdin `mismatches=1 orphans=0` (`EXIT=1`; the report's
  "K-c p3 `cli=empty`" matches the one red row).
- After at A, `records/c2-after.txt` (rev `7076ed2d`, tool `ba61e912…`): `rows=12 mismatches=0 errors=0 orphans=0`,
  `EXIT=0`. Selftest `records/c2-regress-selftest.txt` binds the tool `ba61e912…` and reads `selftest: 57 checks, 0
  failed`; r17 `records/c2-regress-r17.txt` `SUMMARY total=37 failed=0 skipped=0`; domain trial `TRIAL identical=yes
  targets=3 verdicts=3/3`.
- At R, `records/repair/c2-at-R.txt` (rev `ef76a14f`, tool `89a2ed8c…`): `rows=12 mismatches=0 errors=0 orphans=0`;
  `repair/selftest-at-R.txt` binds `89a2ed8c…` `57 checks, 0 failed`; `repair/r17-at-R.txt` `total=37 failed=0
  skipped=0`; `repair/domain-trial-at-R.txt` identical 3/3.
- Harm at W2 repaired: `records/repair/tmpdir-in-vault-at-W2-run{1,2,3}.txt` each `SUMMARY arms=4 failed=3`,
  `EXIT=1` (the three `ok=n` arms are TMPDIR equal to / inside / an ancestor of the vault; the `during=` field shows
  `souji-vault-cli.XXXXXX` under the vault); `tmpdir-in-vault-at-base.txt` `arms=4 failed=0`; at R
  `tmpdir-in-vault-at-R-run{1,2,3}.txt` each `arms=4 failed=0`, `EXIT=0`. Probe D `398e568c` precedes R `ef76a14f`.
  Spot read of `git diff 7076ed2d ef76a14f -- tools/souji-vault-verify.sh`: adds `cli_tmp_ok` (readlink -m of
  TMPDIR and each vault directory/hint; refuses when either is a path prefix of the other) and runs the call in the
  foreground when it fails — consistent with the receipts.

**Launch-mode ruling.** I re-ran the frozen counter at the tip bytes under `SHELLOPTS=monitor`
(`SHELLOPTS=monitor python3 -B census/round-81/c2-vault-signal-counter.py --tool <R bytes> --work …/c2wrm`) →
`SUMMARY rows=12 mismatches=2 errors=0 orphans=2`, `EXIT=1`; the two `match=no` rows are v7-term-pid-fork and
v8-hup-group-fork, each `survivors=1`. This is the same residual the lane recorded at W2
(`records/launch/c2-at-W2-monitor.txt`, also `mismatches=2 orphans=2` on v7/v8) and independently found
(S81ExecC2 HIGH). The preregistration names launch mode as a stated limit, and the same counter on the base bytes
under the same launch leaves 8 mismatches and 8 orphans (`records/launch/c2-K-a-base-monitor.txt`), so the candidate
is strictly better than base in that mode and the frozen predicate (default launch) is green. I rule this a
disclosed residual, not a harm: routed to r82 as a descendant-tree kill, as the lane routed it. No receipt shows the
monitor launch at R; my run is the first measurement of the tip bytes in that mode, and it matches W2's.

Unmeasured branches (M3/M05 of the lesson, S81MutTool): the KILL fallback and the post-call `trap - TERM INT HUP`
reset have no frozen row; a pid-only kill scores the same as the group kill on every row (S326). Disclosed, routed.

### SCORECARD and axes

`git diff b15279bb 492da800 -- SCORECARD.md`: appends only (r81 done row, r82 planned, Round 81 measurements table,
two `(closure-gated)` capability rows); no axis score changed (calibration 7, coverage 8, operability 8).
`PROVINCE.md` unchanged (`git diff --quiet` true).

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1 re-measured: 3 → 0 accepted false rows on the frozen 25-row harness, controls red, r77/r78/r79/r80 regressions green |
| operability | improved | C2 re-measured at W2 and at the tip bytes: 8 → 0 mismatches and 8 → 0 orphans; W2 vault-path write repaired behind a failing-first probe; monitor-mode residual is better than base and disclosed |
| coverage | unchanged | no coverage claim; PROVINCE unchanged; one SOURCES row added (S329) is a source, not a province area |

Re-measured by me: the C1 harness (25 rows), the C2 counter at W2 and at R (12 rows each), the C2 counter at R under
`SHELLOPTS=monitor`, SOURCES row counts, the sources census, all instrument/candidate digests, receipt SUMMARY/EXIT
and `match=`/`match=no` lines, the tool diff. Evidence-verified only: the tool's selftest, the r17 fixture, the
domain trial, the registry-agreement tool, and every lane-owned probe other than the two counters.

## 3. Discernment spot-check

The round lesson `corpus/lessons/round-81.md` `## Gate` logs one admit (S329) and no reject row: the only
rejection-shaped decisions are the within-scope duplicate check on S325 before the S329 append, and the r81
registry-agreement section's decision not to repair K1 S146 / K2. I sampled the admit, the duplicate check, and the
S146 non-repair.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S329 admit (A, mined) — GNU Bash 5.3 Lists of Commands | admit | `pacman -Qo /usr/share/info/bash.info.gz` → bash 5.3.20-1; `sha256sum` = `cde1a336…105588f`, equal to `census/round-79/srcs/bash.info.gz-5.3`; `zcat … \| sed -n 738,770p` vs `git show 492da800:census/round-81/srcs/bash.info-5.3-Lists.txt` | agree | the excerpt is byte-equal to decompressed lines 738-770; the Gate quote "the standard input for asynchronous commands, in the absence of any explicit redirections, is redirected from ‘/dev/null’" is verbatim across lines 758-760 and is 17 words by `wc -w` on the quoted span (the Gate's own count; the SOURCES cell carries the same span). It grounds C2's `<&0`, and the K-c no-stdin control turns p3 red (`cli=empty`), so the source is load-bearing |
| within-scope duplicate check: S325 (node 3.7.6 Signals) vs the Lists node | reject S325 as a duplicate of S329 (i.e. S329 is not a duplicate) | `grep -n '^| S325 ' corpus/SOURCES.md` scope cell; S325's excerpt is `census/round-79/srcs/bash.info-5.3-Signals.txt` lines 3243-3290 | agree | S325's scope is trap deferral during a foreground command, the `wait` interrupt, and SIGINT/SIGQUIT in asynchronous commands; S329's scope is the `&` paragraph's stdin rule. Different nodes, different claims; CORPUS rule 2 not violated |
| K1 S146 `cited-no-row` left red (registry agreement) | reject adding an S146 row / rewriting the entry | `sed -n 1,4p corpus/knowledge/origin-record-format-gvfs-r40.md`; `grep -c '^| S146 ' corpus/SOURCES.md` → 0 | agree | the token sits in provenance prose ("staged id S146", the shokuknow package id the entry was re-pointed from), not in a `source:` citation; the entry's real source is S254. Adding a row would fabricate a source; rewriting append-only text to hide the token would game the instrument. Accepted-red with a stated reason is the right call |

Newly written row re-opened: `S329` (`corpus/SOURCES.md:288`). Its Gate quote is 17 words (≤25) and verbatim. The
row has 11 `|`-separated cells, matching the other rows (the M1 pipe defect was fixed before P; the census E01 check
is what caught it). Its `teaches`/scope cell names the job-control precondition ("when job control is off"), which
S81ScoutSources asked for (F3); the scope cell carries it.

Sources census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 87 `W04` lines (all cross-scope duplicate
URLs, unchanged from r80), `EXIT=0`; the script's sha256 `3fb72615…64e30` equals the digest bound in
`records/census-before.txt` and `records/census-after.txt`. Row count `grep -cE '^ {0,3}\| *S[0-9]{3,}'
corpus/SOURCES.md`: base `b15279bb` 251 → tip `492da800` 252, equal to the report. The five used-by-only touches
(S062, S110, S251, S298, S321) each cite a knowledge file that does cite the row (spot-checked S062 and S321 in
`corpus/knowledge/git-discovery-sources.md` lines 34-35, S110 in `quarantine-restore-path-reoccupied.md` line 2,
S251 in `control-chronology-binding.md` and `freeze-record-substance-binding.md`, S298 in
`replace-ref-receipt-writer.md`).

## 4. Trend verdicts

- **expansion: improved** — one mined tier-A row (S329) on ground the lane did not hold (asynchronous-command
  stdin), a knowledge section on the async-job pattern for a single bounded call (`corpus/knowledge/
  gate-signal-handling.md` r81 section, `source:` cites S329), QUALITY Q146/Q147, two closure-gated capability rows
  demonstrated running (`c1-after.txt`, `c2-after.txt`, `repair/c2-at-R.txt`), and a reusable vault signal counter
  plus a vault-rail probe.
- **quality: unprovable-but-better** — the lane's own verdict, and I agree. The vault tool no longer leaves its CLI
  running on a caller's signal under the default launch (8 → 0 orphan rows at W2 and at R, re-measured), five
  registry used-by cells now match their citations (K1 7 → 1, evidence-verified), and a wave-found rail harm was
  repaired behind a failing-first probe. But C2 is launch-dependent (2 orphan rows under `SHELLOPTS=monitor`,
  reproduced by me at the tip), two kill branches are unmeasured, K1 S146 and K2 remain accepted-red, and C1's
  discriminating rows are L1-built. No single counter carries the net; the operator rules.
- **discernment: improved** — the spot-check agrees with the gate on the admit and on both rejection-shaped
  decisions; the lane found M4 itself before the wave reported it, kept the defective first parse as a diagnosis
  that fails (`diagnosis-m2-first-parse-at-base.txt` `mismatches=12`, `EXIT=1`), applied five non-author corrections,
  disclosed that a pid-only kill scores the same, and refused to repair probe-less LOWs without a failing probe.
  Defect: the `## Gate` section logs no reject row, so there was no reject decision to sample; the closest decisions
  were the duplicate check and the S146 non-repair, both of which I agree with.

## 5. Routed defects (lane fixes next round)

1. `corpus/lessons/round-81.md` `## Gate` carries an admit but no reject row; LEARNING.md asks the section to record
   candidates considered, admitted, and rejected with reasons. Next round's lesson should log at least one reject
   (a real candidate source or entry considered and turned down), so a non-author has a reject to spot-check.
2. C2 launch-mode row and descendant-tree kill (lesson M4, S81ExecC2 HIGH): freeze a `SHELLOPTS=monitor` row and kill
   by descendant tree before the CLI can leave timeout's group; my re-run at the tip reproduces `mismatches=2
   orphans=2` on v7/v8.
3. C2 missing rows: `v9-term-ignoring-cli` (KILL fallback) and `p5-late-term` (trap reset) — both branches survive
   the frozen rows (S81MutTool M03/M05); probe D's two missing arms (inside-vault subdir, hint root); the stale `$!`
   fallback; other terminating signals leaking the private file.
4. C1: a decoy in the token's own round tree (NF-F/NF-G/PF-4, S81MutCounter MEDIUM), a killer row for M8
   (`census/round-<N>/records/<non-wave>/`), and the partial-suffix instance of the stated limit (PF-1).
5. V1: the r80 front's monitor-mode settle tail (S81ExecV1 MEDIUM, 1 in 7); `tests/fixtures/r17-jj-receipts.sh` 240 s
   runners (S81Connector).
6. Carried: the `_regular` pathspec, the quarantine intro-blob digest row, the fork-tail row, the r79 gate
   re-measurement, the check-4 300 s backstop row, r76 K03/K04, the status-trusting lane tools.

SHONEN: all four boxes are `[~]` with resolvable pointers (SKILL gate rows for C1/C2 at `f6f699de`/`398e568c`, LOG
`## Round 81` domain trial at `census/round-81/records/c2-domain-trial.txt` and `records/repair/domain-trial-at-R.txt`,
wave seat reproductions under `.ufo/waves/round-81/w1/`, PROVINCE unchanged). They look checkable by a non-author;
promotion is operator-owned.
