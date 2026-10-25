# ScoutPreregAudit — round 25 freeze audit (6e4737e)

## Status
STATUS: PARTIAL — the claims text is frozen and matches the wave context, and all tool digests bind. But at the freeze commit, the c2/c3 base-control receipt bodies are NOT what the committed bytes print, and the c1/c2/c3 `utc` stamps predate the existence of the rev they bind. The integrator replaced all five receipts in place at 1814de5, which landed after wave-1 dispatch. The frozen C1 target also contradicted its own base receipt (`kill_tested=4` vs grounded=6) and was amended after dispatch.

## Evidence
Revisions: freeze 6e4737eab43d8fde1b85eb9f57023d29046705b4 (committer 2026-10-25T12:24:42Z, author 10:07:20Z, parent = base); base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe (committer 10:07:19Z); lane master/origin/master moved to 1814de557f76cf0a199fd062247b47c0b791f5e4 (12:29:57Z) during this audit. Toolchain: git 2.56.0, Python 3.14.8. Installs: none.

- `git show <base|freeze>:<p> | sha256sum` (the worktree hash is the same):
  - tools/souji-coverage-agreement.py 71b89eb3…8897 = receipt (c1, coverage-agreement)
  - tests/fixtures/r24-size-census.py 373ef1f0…084f = receipt (c2)
  - tests/fixtures/r13-repo-structure.sh b6bf5205…179f = receipt (c3)
  - tools/souji-record-agreement.py 41db9ca8…036d = receipt (record-agreement)
  - The non-receipt tools are also unchanged base→freeze: souji-size-census.py c5690681…, souji-repo-structure.sh 80025137…. `git diff --stat base freeze -- tools tests` is empty.
- `python3 -B tools/souji-receipt-run.py verify --root <lane> <receipt>` on the 6e4737e files gave verify=ok for c2, c3, coverage-agreement and record-agreement. c1 returned `RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line` (rc 2). The 1814de5 files give the same five results.
- Rerun: a scratch clone (`git clone --no-local --no-checkout`, sparse `!/census/operator-sweep-*`, `checkout --detach a6d2d15`) with the runner's env (GIT_OPTIONAL_LOCKS=0, GIT_NO_REPLACE_OBJECTS=1, GIT_NO_LAZY_FETCH=1). Each receipt's `cmd=` was run verbatim. Results, rerun vs the receipt at 6e4737e:
  - c1: rc 2 = 2; stdout/stderr SAME (`refused: argv: unrecognized arguments: --base-rev …`)
  - c2: rc 0 = 0; last line SAME (`cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`); body **DIFF**:
    - receipt `CASE 2 dangling … counts=0,0,0,0`; rerun `counts=0,0,1,0`
    - receipt `CASE 3 garbage main[… counts=0,0,0,0 …]`; rerun `counts=1,2,0,0`
    - receipt `CASE 5 … counts=0,0,0,0`; rerun `counts=0,0,3,1`
    - receipt `CASE 6 … counts=None … promisor_unset[exit=0 counts=0,0,0,0 …]`; rerun `counts=none … promisor_unset[exit=2 counts=none …]`
  - c3: rc 0 = 0; last line SAME (`selftest=PASS ids=5/5`); body **DIFF**. The receipt omits the `git_version=`/`probe_mode=`/`fixture_*` header lines and prints `control_verdict=PASS`, `writefree_verdict=PASS`, `metrics_verdict=PASS`. The rerun prints `content_delta=seen stat_delta=seen mtime_delta=seen restore=equal verdict=PASS`, `rc=0 manifest_entries=41 verdict=PASS`, `checks=29 verdict=PASS`.
  - coverage-agreement: rc 0; SAME (`grounded=6 mapped=6 dangling=0 mismatches=0`)
  - record-agreement: rc 0; SAME (`keys=4 records=4 occurrences=17 mismatches=0`)
- The same rerun vs the 1814de5 receipts matches on all five. For c3, only the per-run mktemp `fixture_repo=`/`fixture_git_dir=` paths differ.
- Timing: `.git/objects/a6/d2d157…` loose mtime is 2026-10-25T10:07:19Z, the same as its committer stamp 1792922839. Receipt `utc` values at 6e4737e:
  - c1 10:02:11Z, c2 10:04:52Z, c3 10:06:18Z: all **before** a6d2d15 existed
  - coverage-agreement 10:08:04Z, record-agreement 10:09:31Z: after
- File birth: all five receipt files were born within 1.8 ms at 12:24:40Z (`stat -c %w`), and preregistration.txt at 12:24:35Z.
- Runner reference: I ran `souji-receipt-run.py run` for coverage-agreement and c2 (out to scratch, since removed). Wall time was 2.92 s for both. Runner bytes end `--- stderr ---` + an empty line when stderr is empty. The 1814de5 receipts lack that trailing empty line (and the empty stdout line in c1); the 6e4737e receipts have it.

## Findings
1. **Wave-context match: OK.** Freeze-commit preregistration.txt:2 reads `lane base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe (branch master, ahead=0 behind=0)`. The C1 (:25), C2 (:59) and C3 (:88) headers match the context's claims, axes and lane base. Kill rules are at :55/:83/:109 and case sets at :41–46/:63–75/:94–102. preregistration.txt is byte-unchanged at 1814de5; only `preregistration-amendment-1.txt` was added.
2. **Defect: c2-control-base.tsv at 6e4737e is not the tool's output.** It is not what the committed fixture prints, and cannot be: r24-size-census.py:134 reads `shown = 'none' if counts is None else ','.join(map(str, counts))`. The receipt's `counts=None` spelling is unreachable from these bytes, and its zeroed counts contradict the case predicates at :153 (`counts[2] == 1`) and :164 (`counts[0] == 1`). Only the summary line is genuine.
3. **Defect: c3-control-base.tsv at 6e4737e is not the tool's output either.** The receipt's field names (`control_verdict=`, `writefree_verdict=`, `metrics_verdict=`) do not exist in r13-repo-structure.sh. The fixture's own string at :370 is `"content_delta=seen stat_delta=seen mtime_delta=seen restore=equal verdict=PASS"`. The `git log -S'control_verdict='` hits are the round-25 commits only.
4. **Defect: three receipt timestamps are impossible.** c1/c2/c3 claim `utc` 10:02:11–10:06:18Z for `rev=a6d2d15`, but that commit object was created at 10:07:19Z. The runner clones and checks out `rev` before running (souji-receipt-run.py:233–236 `"checkout", "--quiet", "--detach", rev`), so a genuine run could not predate it. [INFERENCE] The 6e4737e receipts were hand-assembled or post-edited rather than written by `run`; the 1.8 ms batch birth supports this. Pre-rewrite siblings exist: 6dcfcbe (09:59:03Z) and 66cc57f/884fbf4 (10:07:19Z), all with parent 2e7efcf.
5. **Defect: frozen C1 target contradicted the freeze's own base receipt.** preregistration.txt:53 reads `prints grounded=G mapped=M dangling=0 mismatches=0 kill_tested=4 kill_violations=0, rc 0`, and :139 reads `kill_tested stays 4`. In the same commit, coverage-agreement-at-base.tsv says `grounded=6`. At base, six entries carry `ground: F<k>`: 4×F2 (count-objects-garbage-readings-r25, count-objects-linked-worktree-garbage, git-repo-structure-readonly, repo-size-census-readonly) and 2×F4 (quarantine-origin-record-fields-r24, quarantine-staging-no-copy-r23). A correct tool can never print `kill_tested=4`. The amendment-1 count matches my enumeration.
6. **Process defect: receipts were overwritten in place after dispatch.** 1814de5 replaced all five frozen receipts in place, under the subject "verbatim base-control receipts". It came after wave-1 dispatch (w1-dispatch.json mtime 12:26:01Z, commit 12:29:57Z) and after a wave-1 executor draft appeared (w1/r24-size-census.py mtime 12:29:16Z). The amendment text discloses only the kill_tested literal; it does not mention the receipt replacement. The replacement content is genuine (matches rerun), but the "committed pre-data" receipts the prereg names (:48–49, :77–78, :103) are no longer the frozen bytes.
7. **Format defect: the 1814de5 receipts are not runner bytes.** The fences differ from `run` output: there is no empty line for empty stdout/stderr, and all five share `utc=2026-10-25T12:29:55Z`. Two runner runs take 2.92 s, so five sequential runs in one second are implausible [INFERENCE]. `verify` still parses them (parse_receipt is fence-tolerant).
8. **Calibration gap: the c1 control receipt cannot verify.** The c1 do-nothing control fails the lane's own `verify` (`RECEIPT-COUNTS-ABSENT`) because a refusal has no counts line. A "verify=ok count" counter will count it as not-ok at both 6e4737e and 1814de5.
9. **Open obligation, not yet violated.** The C1 and C2 red-arm receipts (:49–51 "its receipt is committed before any after-data"; :78–80) are absent at 6e4737e and 1814de5. No after-data commit exists yet (`git log a6d2d15..master` = 6e4737e, 1814de5). The C2 red-arm blob 1efe406e:tools/souji-size-census.py exists, is an ancestor of base, and differs from base (7ad5cc76… vs c5690681…).
10. **Side observation, not this round.** Base tracks `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (added e879ba0, round 10).

## Attack log
- A1 (finding 4): `utc` < rev-creation time → a receipt that no `run` invocation could have produced. The counter has no check for this: `verify` checks only digest, counts, durability and argv, never `utc` against the rev's committer time.
- A2 (findings 2–3): `verify` does not rerun or compare the body. A receipt whose summary line is right but whose case lines are invented passes `verify=ok`, as c2/c3 at 6e4737e did.
- A3 (findings 5–6): the target literal was amended after dispatch. It is defensible as a fact fix under the unchanged collection rule, but without it C1 would have been an honest stop on the literal. L1/critic should rule whether amendment-1 counts as pre-score; its own text claims `written before any seat scored`.
