# souji round 80 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane round 80, base `f80f9368a8a20679438b1dffd72d0faab0ccf194`, after `5865301b20b1d8ee9751c157e944b06999e9a70e`
(branch `master`). Report `.ufo/reports/round-80/souji.md` (fleet repo commit `3cd299a0`, author `souji-shokunin`).
Driver digest (`.ufo/watchdog.log`): `2026-11-07T04:02:15-03:00 launch souji round=80 pgid=231481
driver=hyaku-inline attempt=1`; `2026-11-07T05:49:30-03:00 complete souji round=80; hyaku-inline attempt=1`.

Outcome: status `ok`, **admitted**. C1 verifies (evidence-verified); C2 verifies on its frozen predicate at
the measured candidate W2 and on the shipped tip bytes (evidence-verified); the harm the wave found at W2 is
repaired before the after commit behind probes that fail on the earlier bytes, and no owned axis is harmed at
`5865301b`. The ruling on that harm is in §2 (C2).

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-80/souji.md` | `souji-shokunin 3cd299a018635622df8e5d068da7c24c82982aaa` (05:48:22, after lane tip 05:46:55) | pass |
| `## SHONEN` heading, one line per box | read report | 4 lines, all `[~]`, each with a pointer | pass |
| cited commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit}` + `git merge-base --is-ancestor <h> refs/heads/master` over the 18 cited hashes (base, P, F, W1, W2, A, I, D, R, R receipts, D2, R2, R2 receipts, D3, R3, R3 receipts, mirror, census-after) | 18/18 `exists anc` | pass |
| lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `branch=master local=remote=5865301b… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty | pass |
| prompt carries the template contract | `diff templates/round-prompt.md <(sed -n 1,140p .ufo/prompts/souji-round-80.md)` | only placeholder substitutions (`{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}`, `{{AXES}}`); §6 hyaku addendum follows | pass |
| commit identity | `git log --format='%an <%ae>' f80f9368..5865301b` | 17/17 `souji-shokunin <souji@shokunin.local>` | pass |

Observations (status-neutral): P `515d57c8` carries author date 04:01:20, 55 s before the driver launch line;
its committer date is 04:27:19 and every later commit's author date equals its parent's committer date — the
jj working-copy change-creation timestamp, not a pre-launch commit. The dispatched prompt is committed under the
lane identity (`7d8081a6`), as r79's was (`c208a092`): driver behaviour, not lane debt.

## 2. Claims

Both claims rest on lane-owned instruments (C1 harness + counter, C2 signal counter, r13/r17 fixtures, the tool's
selftest). Per PROTOCOL §Gate standard (Closure consequence) I did not execute them: every number below is
**evidence-verified** from committed receipts, with instrument and candidate bytes re-hashed from the commits
myself. Nothing was re-run.

Instrument and candidate digests (`git show <c>:<path> | sha256sum`):

| object | at freeze / candidate | at tip `5865301b` | prereg / receipt value | result |
|---|---|---|---|---|
| `census/round-80/c1-false-row-harness.py` | F `6f22b68a…e6c7` | `6f22b68a…e6c7` | prereg `6f22b68a…e6c7` | frozen |
| `census/round-80/c1-false-rows.tsv` | F `5cce4146…15be` | same | prereg same | frozen |
| `census/round-80/c1-pointer-counter.py` | absent at F; W1 `90ed9031…69f1` | `90ed9031…69f1` | regress receipts bind `90ed9031…` | candidate after F, unchanged to tip |
| `census/round-80/c2-signal-counter.py` | F `32cf0c72…b966` | same | prereg and all C2 counter receipts | frozen |
| `census/round-80/c2-population.tsv` | F `ca5e2387…9025` | same | prereg same | frozen |
| `tools/souji-quarantine.sh` | base `e2f2d083…9e4d`; W2 `67ec160b…7181` | `23a43fbb…8572` (= R3 `4a499e9a`) | K-a base sha, A receipts `67ec160b…`, `repair3/selftest-at-R3.txt` binds `23a43fbb…` | W2 measured, R3 = tip |

### C1 — calibration: **verified** (evidence-verified)

`git show 5865301b:census/round-80/<receipt> | grep -E '^(rev=|instrument_sha256=|SUMMARY|FORGE-SUMMARY|EXIT)'`:

- Before, `controls/c1-K-a-r79-counter.txt` (rev base): `SUMMARY rows=18 mismatches=3 accepted=3 errors=0`, `EXIT=1`;
  the three `match=no` rows are `NF6b` (QUARANTINED), `NF8` (TOKEN), `NF10` (MOVED) — 15 of 18 `match=yes`.
- After, `records/c1-after.txt` (counter `90ed9031…`): `SUMMARY rows=18 mismatches=0 accepted=0 errors=0`, `EXIT=0`;
  18/18 rows `match=yes`.
- Controls red as preregistered: K-b refuse-all 18/18 on the harness but `controls/c1-K-b-refuse-all-regress-r78.txt`
  `SUMMARY items=22 resolved=3 … refused=19`, `EXIT=1`; K-c ablations without-regular / -capture-root / -whole each
  `mismatches=1 accepted=1`, `EXIT=1`.
- Regressions green: r78 `items=22 resolved=22` + `forged=12 matched=12 accepted=0`; r77 `items=35 resolved=35` +
  `forged=7 matched=7 accepted=0`; r79 harness (`5d5bd236…`) `rows=9 mismatches=0 accepted=0`; all `EXIT=0`.
- Reported 3 → 0 equals the receipts. Qualifications disclosed and accepted: the frozen set kills 3 of 9 rule
  mutants (mode arm unseen); NF12 decoy under `census/round-<N>/` and NF14 still accepted; the 100644/100755
  whitelist is grounded by S294, which the counter docstring does not cite. All routed by the lane to r81.

### C2 — operability: **verified** (evidence-verified), with a ruling on the W2 harm

- Before, `controls/c2-K-a-do-nothing.txt` (rev base, tool `e2f2d083…`): `SUMMARY rows=15 mismatches=12 errors=0
  orphans=12`, `EXIT=1`. K-b trap-only and K-c no-session-kill: `mismatches=12 orphans=12`, `EXIT=1` each.
- After at A (rev W2 `836dac3e`, tool `67ec160b…`): `records/c2-after.txt` `SUMMARY rows=15 mismatches=0 errors=0
  orphans=0`, `EXIT=0`; `c2-regress-r13.txt` `total=5 failed=0 hung=0`; `c2-regress-r17.txt` `total=35 failed=0
  skipped=2`; `c2-domain-trial.txt` three `DRY-RUN-PASS` RESULT lines, `TRIAL identical=yes`, `EXIT=0`.
- Selftest conjunct ruling: `c2-regress-selftest.txt` (a `git show` copy at `/fast/scratch/.../td/cand/`) reads
  `selftest: 81 checks, 51 failed`; `c2-regress-selftest-committed-mode.txt` (the committed file, `bash
  tools/souji-quarantine.sh --selftest`) reads `108 checks, 0 failed`. The base copy fails identically
  (`diagnosis/selftest-base-mode0644-copy.txt` 81/51; non-author S80ExecC2 reproduced it from the true base blob
  `e2f2d083`, `wave-w1/seats/S80ExecC2.md:42-44`). The 81/51 reading cannot distinguish base from candidate, so it is
  an instrument-context failure, not a candidate measurement; the frozen command run on the candidate as shipped
  reads 108/0. Kill rule not triggered (agrees with S80Reviewer and S80CriticClaims item 13).
- Domain trial: v1 compared two empty outputs (vacuous), v2 ran the arms from different locations; v3 is symmetric
  and is shown able to fail (`diagnosis/domain-trial-v3-refuses-empty.txt` `TRIAL identical=no`, `EXIT=1`). The
  predicate was not changed; the probe was. Accepted.
- **Harm at W2.** `records/repair/front-launch-modes-at-W2.txt` (instrument `ac78ee91…`): `ARM monitor-p1 ok=n rc=0
  signal_line=n verdict=-`, `SUMMARY arms=3 failed=3`, `EXIT=1` — under job control the W2 tool exits 0 with no
  verdict where the base answers; this contradicts the claim's own "with no signal its dry-run verdicts and exit
  codes are unchanged". It is outside the frozen rows, found by three non-author seats.
- Repairs to the after commit, each behind a probe that fails first:
  D→R: `front-launch-modes` 3/3 fail at W2 → `repair/front-launch-modes-at-R.txt` `arms=3 failed=0`;
  D2→R2: `repair/front-worker-death-at-R.txt` `arms=2 failed=2` (`front_rc=137 survivors=5`; `tmpdir-missing rc=2
  (base tool: 1)`) → `repair3/front-worker-death-at-R3.txt` `failed=0`;
  D3→R3: `repair2/front-comm-newline-at-R2.txt` `arms=1 failed=1 survivors=1` → `repair3/front-comm-newline-at-R3.txt`
  `failed=0`.
  At R3 (= tip tool bytes `23a43fbb…`): frozen counter `repair3/c2-at-R3.txt` and `repair3/c2-monitor-at-R3.txt`
  `rows=15 mismatches=0 errors=0 orphans=0` (`instrument_sha256=32cf0c72…`, the frozen counter), r13 5/0/0, r17
  35/0/2, selftest `108 checks, 0 failed` binding `23a43fbb…`, domain trial identical.
- Ruling. Grading is against the after commit `5865301b`: there the frozen instrument reproduces the full
  predicate on the shipped bytes (12 → 0 mismatches, 12 → 0 orphans, regressions green), and the W2 harm no
  longer reproduces under the probe that exposed it. No owned axis is harmed at the after commit. This follows
  the r77/r78 closures, which admitted wave-found defects repaired behind failing-first probes with the frozen
  counter re-run at the repair. The repaired bytes were not attacked by a wave, so routed defect 1 below requires
  r81 to freeze the post-wave rows and re-measure the repaired front under a fresh freeze, as the lane already
  plans (SCORECARD "r81 (planned)").
- Spot read of the repair (`git diff 836dac3e 5865301b -- tools/souji-quarantine.sh`): `set +m` before the
  setsid launch, worker refuses unless `PPID` is its front, nested branch requires `q_proc_runs_self`, post-wait
  `trap '' TERM INT HUP`, session sweep when the worker itself died, `q_proc_sid` reads the whole stat file and
  strips through the last `) ` (field index 3 after state = session). This is consistent with the receipts.

### SCORECARD and axes

`git diff f80f9368 5865301b -- SCORECARD.md`: appends only (r80 done row, r81 planned, Round 80 measurements table,
two `(closure-gated)` capability rows); no axis score changed (calibration 7, coverage 8, operability 8).
`PROVINCE.md` unchanged (`git diff --quiet` true).

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1 evidence-verified: 3 → 0 accepted false rows on the frozen harness, controls red, regressions green |
| operability | improved | C2 evidence-verified at W2 and at the tip bytes (12 → 0 mismatches and orphans); W2 job-control harm repaired before the after commit behind failing-first probes |
| coverage | unchanged | no coverage claim; PROVINCE unchanged |

Re-measured by me: the digest table, receipt SUMMARY/EXIT lines, the `match=` row counts, SOURCES row counts, and
the sources census. Evidence-verified only: every lane-owned counter, probe, fixture and selftest result.

## 3. Discernment spot-check

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S328 setsid(1) as installed | admit (A, mined) | `pacman -Qo /usr/share/man/man1/setsid.1.gz` → util-linux 2.42.4-1; `sha256sum` `614ae07f…7385243` = row and capture `census/round-80/srcs/setsid.1.gz-util-linux-2.42.4`; `zcat … \| sed -n 37p` | agree | Gate quote "The command calls fork(2) if already a process group leader. Otherwise, it executes a program in the current process." (19 words) is verbatim on line 37 and grounds the exec-in-place front/worker design |
| S327 git-ls-tree(1) as installed | admit (A, mined) | owner git 2.56.0-1; sha256 `c0e10ef5…1a7e86` = row and capture; `zcat … \| sed -n '204p;251,256p'` | agree | line 204 is the default format verbatim; "The type of the object (commit, blob or tree)" (9 words) spans roff lines 252-255; supports "a range member may be a tree", while the mode whitelist rests on S294, as the Gate states |
| draft S329 proc_pid_stat(5) as installed | reject (within-scope duplicate) | owner man-pages 6.19-1, sha256 `d2b5d09d…cc002b51` (= Gate), lines 107-108 "(6) session %d / The session ID of the process."; SOURCES rows S068/S075 | agree | S068's scope is "field order and units of pgrp, session and starttime" on the same page and S075 supersedes it with the same field 6; a second row would duplicate scope (CORPUS rule 2); citing S075 (not S068) is right |

Newly written row re-opened: `S328` (`corpus/SOURCES.md:287`). Its Gate quote is 19 words and verbatim. The row's
`anchor` cell quotes the full three-sentence DESCRIPTION passage (27 words): that is an anchor cell, not the
≤25-word Gate quote, so CORPUS rule 1 holds. Its `teaches` cell still names S068 (P text, append-only); the
knowledge entry and the tool cite S075.

Sources census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ `souji	ok	…/corpus/SOURCES.md`, 87 `W04` lines (all cross-scope duplicate URLs, same as before), `EXIT=0`.
Row count `grep -cE '^ {0,3}\| *S[0-9]{3,}' corpus/SOURCES.md`: base 249 → tip 251, equal to the report.

## 4. Trend verdicts

- **expansion: improved** — `corpus/knowledge/gate-signal-handling.md` gains the r80 section (session front for
  `$(...)`-heavy tools) with `source: S325, S326, S328, S075`, S328 a new mined tier-A row; S327 a new mined tier-A
  row grounding C1; QUALITY Q144/Q145; two capability rows demonstrated running (`c2-after.txt`, `c2-at-R3.txt`).
- **quality: improved** — the knowledge entry's stale S068 citation is superseded by S075 (registry K1 at I 8 →
  tip 7, back to base, `records/registry-agreement-*.txt`); the S328 quote in the knowledge entry is corrected
  with its Otherwise clause; the W2 harm and two further wave defects are repaired behind failing-first probes
  with the frozen counter green at the repair. No admitted entry fails its re-check.
- **discernment: improved** — the spot-check agrees with the gate on two admits and one reject; mistake M1 (lossy
  copy replay) became QUALITY Q145; defective receipts (81/51 selftest, v1/v2 trials, racy v1 probe) are kept as
  diagnosis rather than replaced.

## 5. Routed defects (lane fixes next round)

1. Freeze the post-wave quarantine rows (job-control launch, spoofed session, worker killed, TMPDIR missing,
   newline comm) as a successor population and re-measure the R3 front under a fresh freeze with a wave
   attack. The R/R2/R3 bytes have only author measurements.
2. `census/round-80/records/diagnosis/selftest-base-mode0644-copy.txt` binds `67ec160b…` (the candidate) in its
   `instrument_sha256`/`# bind` lines while executing `td/base/souji-quarantine.sh`: `rec.sh` must bind the bytes it
   actually executed (S80ExecC2 MEDIUM); for copies it should also record the executed file's mode.
3. `records/registry-agreement-at-I.txt` measures `--rev 79fcc73d` (R2 receipts), not I `60c7f50e`; the report and
   lesson call it "at I". Label it with the measured revision. The `rev=` line in all three registry receipts is
   the recording commit `24274475`, not the measured one.
4. The registry-agreement tool is red at base and at tip (`k1=7 k2=1`, `EXIT=1`; `K2 rewrote-not-appended
   SCORECARD.md`). Pre-existing and unchanged by r80; route a correction or a recorded accepted-red rationale.
5. `census-after.txt` and `census-before.txt` bind `census/round-80/rec.sh` as `instrument=` rather than
   `scripts/sources-census.sh`. Bind the census script's digest.
6. C1 qualifications carried: NF12/NF14, mode-arm detector rows, the counter docstring citing S294.
7. S328 `teaches` cell names S068 (superseded by S075). This is append-only P text: record the correction
   through a successor row or a lesson note, not an in-place edit.

SHONEN: all four boxes are `[~]` with resolvable pointers (SKILL gate rows for C1/C2, LOG `## Round 80` domain
trial at `c2-domain-trial.txt` and `repair3/domain-trial-at-R3.txt`, wave seat reproductions, PROVINCE unchanged).
They look checkable by a non-author; promotion is operator-owned.
