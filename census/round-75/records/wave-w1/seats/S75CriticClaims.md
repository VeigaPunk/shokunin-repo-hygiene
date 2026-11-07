# S75CriticClaims — r75 C1/C2 falsification (critic, w1)
Reviewed P 7ba5217d, F be599cbb, I f6ec0d71, W 1ad737b4, A 5d10e09e (tip). Numbers re-derived from committed bytes; receipts in .ufo/waves/round-75/w1/S75CriticClaims/.

## Verdicts
1. C1 labels — QUALIFIED. Both relabels are load-bearing for the 0 and both rows already read the r75 label at Base: f2 PASS (controls/c1-K-a:27), n-filemode FAIL (my route: `pinned git status ... lists 1 record(s)`, the writer's core.fileMode pin). The 2->0 delta is exactly the two info/exclude rows (c1-K-a:25,42; records/c1-after:25,36). The rulings are frozen (prereg:27-30), not post-hoc, but the target's 0 is label-defined, not behaviour-defined.
2. C1 core.excludesFile — FALLS as attribution. f3 FAILs at Base already through the writer's `-c core.excludesFile=/dev/null` pin (tools/souji-receipt-write.py:159-161) before the new block; my f3 detail is `byte truth: pinned git status ... lists 1 record(s)`, never RECEIPT-UNTRACKED-LOCAL-EXCLUDE. A gate refusing only info/exclude meets all 25 rows; the block's live arm is info/exclude alone (gate:98).
3. C1 population — FALLS (HIGH). Clean core.worktree redirect (symlinks preserved, index refreshed): --lane carries secret.txt hidden by its own info/exclude while git resolves the worktree to a copy; Base and W both print `check-clean=PASS` rc=0 (redirect-base.txt, redirect-W.txt). The l-core-worktree row fails only on a copytree artifact (`detail-clean:  T ln`, evade-probe.py:397-403), so the row does not test the redirect. In-flight patch (worktree gate sha256 ef3b04e4) prints `RECEIPT-WORKTREE-REDIRECTED` and keeps 25 rows 0/0 — smallest safe correction; amendment per prereg:22-24.
4. C1 omitted shapes — HOLDS. XDG global ignore FAIL (writer pin), `git add -f` staged FAIL (`A build/x.pyc`), untracked subdir .gitignore FAIL (`?? d2/.gitignore`); committed-subdir .gitignore PASS is the f2 policy. Lane differential standard-perdir = 0 over 26052 ignored paths (lane-differential.txt).
5. Sourcing S318/S319 — HOLDS. The code implements the documented composition (git-ls-files.adoc:127-134,326-340; gitignore.adoc:37-59,147-150), gate:98; it does not merely cite.
6. C2 numbers — HOLDS. My runs: pristine 64/64 EXIT=0; X09 1, P1 1, M08 1, M14 1, M15 2, M17 2; kill SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS EXIT=0 (kill-tally.txt). Mutant shas equal records/variants/r75-* byte for byte; apply-edit applies once.
7. C2 X09 detector — HOLDS/QUALIFIED. It drives evaluate()/row_scope through the patched tree_divergence in both slots (counter:2037-2053); a witness ignoring divergences fails (9a) and the r75 per-row check (2015-2021). It is a scoping unit test, not a real-fixture probe; wrong-paths scoping is uncovered.
8. C2 P1/do-nothing — HOLDS. P1 killed only by the r75 per-row check (`new-slot unwitnessed=['AS2','FC2','FM2']`); X15 alone survives (fail=0, prereg:47-49); do-nothing r74 killed=4 survived=2 EXIT=1 (do-nothing-tally.txt); blanket pristine=FAIL EXIT=1.
9. Universal clauses — QUALIFIED. prereg:4-5 receipt-substance has no counter (four r75 controls comply on inspection); prereg:37-38 "no evaluate()/verdict change" is diff-only (two selftest hunks, counter:2015-2053); the domain trial has no committed receipt at A (target clause unmeasured until the report tip; predicate reproduced 0).

## Commands
c1: python3 -B census/round-75/c1-evade-counter.py --gate-dir <gate@rev> --work <scratch> -> base 2/25 EXIT=1, W 0/25 EXIT=0, K-b 3 EXIT=1, patched 0/25 EXIT=0.
c2: python3 -B <counter> --selftest --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --work <dir> (8 runs); c2-kill-counter.py --pristine/--mutant (both tallies); apply-edit.py --set {c2-mutants|c2-survivors} --id <ID>.
freeze: python3 -B tools/souji-freeze-check.py --root . --prereg census/round-75/preregistration.txt --rev be599cbb --substance --chronology -> claims=2 findings=0 EXIT=0.

## Findings
HIGH C1: clean core.worktree redirect passes check-clean at Base and W with info/exclude-hidden lane content; l-core-worktree fails for a symlink artifact, not the redirect. Fix: worktree==lane refusal (in-flight, amendment both digests).
MEDIUM C1: core.excludesFile is claimed as candidate scope but is closed upstream by the writer pin; no separability (an info/exclude-only gate meets the target).
MEDIUM C1: f2 PASS is a load-bearing policy ruling; a .gitignore committed at the tip hides new content and passes (my committed-subdir test PASS); not listed among the stated limits (only f7).
LOW C1: domain trial has no committed receipt at A; predicate reproduced (differential 0).
LOW C2: r75 counter bytes are not hash-bound in the frozen prereg (authored at I after F); A receipts bind instrument_sha256=90a3c7b2; diff is exactly the two checks.
LOW: prereg:4-5 receipt-substance clause has no counter.

Files (seat dir): S75CriticClaims.md; S75CriticClaims/{c1-base,c1-W,c1-Kb,c1-patched,lane-differential,redirect-base,redirect-W,redirect-patched,kill-tally,do-nothing-tally}.txt, out-{pristine,X09,X15,P1,M08,M14,M15,M17}.txt, out-r74p.txt, out-r74-{X09,P1,M08,M14,M15,M17}.txt.
