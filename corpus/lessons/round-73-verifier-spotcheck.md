# Round 73 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatch digest (copied from `.ufo/watchdog.log` because the log is mutable):
`2026-11-06T18:54:32-03:00 launch souji round=73 pgid=1281462 driver=hyaku-inline attempt=1`;
`2026-11-06T20:22:44-03:00 lane-dead-no-report souji round=73` (attempt 1 ended without a landed report);
`2026-11-06T20:22:46-03:00 launch souji round=73 pgid=1590628 driver=hyaku-inline attempt=2`;
`2026-11-06T20:29:02-03:00 complete souji round=73; hyaku-inline attempt=2`.
Lane base `a789486d8d5d5e0f91145ad70282956f2cb6fda0`, lane tip `d8380f6d04dbda5f3c8ac804eb3149466f9b256b`.
The closure authored no round byte and ran no lane gate, counter or selftest (PROTOCOL §Gate standard,
Closure consequence): every counter/selftest number below is evidence-verified from committed receipts; source
fetches, row counts and the census were re-run by the closure.

## Conformance

| check | command | result |
|---|---|---|
| report landed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an %H %ad' -- .ufo/reports/round-73/souji.md` | `souji-shokunin 949d113b7195cba1e53772eadc4210dc55244557`, 20:28:30 -0300: after the last lane commit (20:27:40), before `complete` (20:29:02) |
| `SHONEN` heading, one line per box | read report §SHONEN | 4 `[~]` lines, each with a pointer; no `[x]` |
| cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <h> master` for 23ecd070 1eac307f aaacba33 b84ff90b 312e8f29 4534dd17 35192856 d8380f6d | all 8 ok |
| lane pushed, clean | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git status --porcelain` | `local=remote=d8380f6d… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty; `ls-remote origin refs/heads/master` = d8380f6d |
| authorship | `git log --format='%h %an <%ae> %cI' a789486d..d8380f6d` | all 8 commits `souji-shokunin <souji@shokunin.local>` |
| freeze chronology | same log | F 19:05:11 < I 19:08:11 < K 19:08:50 < W 19:11:58 < A 19:12:39; wave dispatched 19:15:33 (after A); repair 4534dd17 20:27:15 |
| prompt carries the template contract | `grep -n '^## ' .ufo/prompts/souji-round-73.md` | §1 MISSION/AXES … §5 commit/push scope, §6 hyaku addendum, §7 scratch discipline present |
| owned-axis scores | `git diff a789486d d8380f6d -- SCORECARD.md` | additions only: two r73 capability rows, r73/r74 plan bullets, r73 measurement table; calibration 7, coverage 8, operability 8 unchanged |

Not a marker report: real commits, receipts and claims.

## Claims

C1 (operability) — evidence-verified against frozen predicate (prereg lines 57-72):

| conjunct | command (all `git show d8380f6d:census/round-73/<f> \| grep -E '^(SUMMARY\|EXIT=\|SELFTEST)'`) | observed |
|---|---|---|
| (i) after | `records/c1-after.txt` | `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`; header binds `new=b84ff90b…:tools/souji-receipt-write.py` |
| (ii) do-nothing | `controls/c1-K-a-do-nothing.txt` | `new_forgeries=3 … class_mismatches=3`, `EXIT=1` |
| (iii) blanket / forger | `controls/c1-K-b-blanket-refusal.txt`, `controls/c1-K-c-forger.txt` | `new_honest=0 class_mismatches=59 regress=FAIL` `EXIT=1`; `new_forgeries=15` `EXIT=1` |
| (iv) writer selftest | `records/writer-selftest.txt` | `SELFTEST cases=44 pass=44 fail=0`, `EXIT=0` |
| in-round repair | `records/wave-repair/selftest-writer.txt`, `selftest-M01.txt`, `selftest-M05.txt`, `c1-main-arm-wave-writer.txt` | 45/45 EXIT=0; M01 and M05 each `pass=44 fail=1` EXIT=1; repaired writer main arm SUMMARY identical to c1-after, EXIT=0 |

Reported before→after (`new_forgeries` 3 → 0, `new_honest` 21/21, EXIT 1 → 0) matches. **operability: improved.**

C2 (calibration) — evidence-verified against frozen predicate (prereg lines 100-111):

| conjunct | command | observed |
|---|---|---|
| (i) D1..D5 | `for k in 1 2 3 4 5; do git show d8380f6d:census/round-73/records/c2-after-D$k.txt \| grep -cE '^SUMMARY .*base_unwitnessed=1( \|$)'; done` | `1 1 1 1 1`; edited rows FWr, FWi, FWp, FWs, FC3 each `base=accept … base_witness=no` |
| before | `controls/c2-before-r72-D1..D5.txt` SUMMARY/EXIT | each `matrix=75 base_forgeries=12 base_mismatches=0`, `EXIT=0` (0 of 5 detected) |
| (ii) positive control | `controls/c1-K-a-do-nothing.txt` | `base_unwitnessed=0 base_forgeries=15` |
| (iii) counter selftest | `records/counter-selftest.txt` | `SELFTEST cases=52 pass=52 fail=0`, `EXIT=0` |

Reported 0 → 5 of 5 matches. The lane's own qualification stands and is not a harm: the witness is tree-global
(FWw/FC1/FC2 defanged still `base_witness=yes`, S73ExecC2), so Q133's per-row wording overstates the instrument.
**calibration: improved.** **coverage: unchanged** (no coverage claim; score 8 kept).

No owned axis harmed. Both claims verified; neither is exploratory.

## Discernment spot-check (`corpus/lessons/round-73.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S315 racy-git.adoc v2.56.0 | admit (A, mined) | `curl https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/technical/racy-git.adoc` → HTTP 200, 9121 B, sha256 `f661ed2d…b84ad` (equals SOURCES row) | agree | primary git documentation at a pinned tag; the 16-word quote is present verbatim and is exactly the failure C1 guards (status as a stat-cache verdict) |
| S316 git-hash-object(1) `--no-filters` | admit (A, mined) | `curl -L https://git-scm.com/docs/git-hash-object` → HTTP 200, sha256 `b7e8f953…eb798` (equals row) | agree | official man page; 22-word quote present verbatim after tag-strip; grounds hashing *with* filters so FXc (autocrlf) is not over-refused |
| racy-git sentence at offset 3374 | reject (over cap) | `census/round-73/srcs/racy-git.txt` offset 3374 to the next `. ` | agree | the sentence "the cached stat information … is now different" counts 26 words (`python3` split), over the 25-word cap; the admitted 16-word sentence carries the same point |

New SOURCES row re-opened: S316 (above); quote 22 words ≤ 25, located OPTIONS `--no-filters`. Row count
`grep -cE '^ {0,3}\| *S[0-9]{3,}' corpus/SOURCES.md` at a789486d → d8380f6d: 237 → 239 (matches report).
Census `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`: `souji ok`, 86 W04, no
other finding, EXIT=0 (matches report).

## Trend verdicts

- **expansion: improved** — S315/S316 tier-A rows on new ground (index stat cache, hash-object conversion), knowledge
  `filter-filemode-witness.md` r73 section, two SCORECARD capability rows, a new refused forgery class.
- **quality: improved** — writer mutants M01/M05 went from surviving to killed in-round, shown by committed
  `selftest-M01.txt`/`selftest-M05.txt` (fail=1, EXIT=1) and the repaired 45/45 selftest.
- **discernment: unchanged** — all three gate decisions sampled are correct, but Q133 was written with a per-row
  wording the lane's own instrument meets on 12 of 15 rows, and 5 of 12 seats (incl. S73CriticDiscern) left no
  verdict. Agrees with the lane's self-grade.

## Routed defects (lane fixes next round)

1. Q133 overstates the counter (per-row vs tree-global witness): append a superseding QUALITY row or land the
   row-specific witness (lesson M2, S73ExecC2).
2. Counter survivors M08 (fail-open witness read), M14, M15, M17 and writer survivor M03 remain unkilled.
3. The lane's own gates trusting `git status` (`tools/souji-pre-report-gate.sh:36-37`, `tools/souji-verify.sh`,
   `tools/souji-vault-verify.sh`, `tools/cand-*-verify.sh`, `tools/souji-record-agreement.py`; S73Connector HIGH).
4. `base_forgeries` is not witness-gated.
5. `corpus/lessons/round-73.md` opens "Attempt 1" although attempt 2 finished and filed the round; the report
   states its pointer-check gives `missing=4` on the lesson (not re-run here) — tidy so it exits 0.
6. Wave evidence: `w1-results.json` empty and five seats delivered no report (lesson M4) — seat findings must land
   in files before the L1 ends.
