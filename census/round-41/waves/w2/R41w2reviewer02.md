# R41w2reviewer02 — independent re-measure of C2 (operability)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f
Judged on: operability · Role: reviewer (read-only; no lane, tracked-file or census writes)
Scratch used: /fast/scratch/hyaku/souji-r41/R41w2reviewer02 (deleted before yield)
Copied receipt: .ufo/waves/round-41/w2/R41w2reviewer02/c2-tip-counter.out

## 1. Counter re-measure

Commands (exit codes observed):

    python3 -B census/round-41/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 119c26fa3bbb85e215824de9538bd2eb34e9f874 --scratch /fast/scratch/hyaku/souji-r41/R41w2reviewer02   -> EXIT=0
    python3 -B census/round-41/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch /fast/scratch/hyaku/souji-r41/R41w2reviewer02   -> EXIT=0

Both runs print the same 21 `case-*=PASS` lines, then:

    real ok rc=0 findings=0 summary=(3, 0)
    retro red rc=1 findings=18 summary=(3, 18)
    SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8

This matches the Target line in census/round-41/preregistration.txt (C2) and the SUMMARY/real/retro lines in records/c2-after.txt (diffed: identical).

Disagreement with the brief: records/c2-after.txt does NOT contain the 21 `case-*=PASS` lines (`grep -c '^case-'` = 0; file is 6 lines: header, `$` command line, real, retro, SUMMARY, EXIT=0). The case list is only visible by re-running the counter. The receipt is therefore a summary, not the per-case evidence.

Frozen digests (sha256sum at tip): c2-counter.py = 85ffe263…1e11 (matches prereg); c2-cases.tsv = 4854335a…75c6 (matches prereg). Consistency check: the 21-row c2-cases.tsv agrees with the counter's CASES table on every case's exit code and finding multiset (19 CASES + 2 refusal rows; mismatches=[]). The counter never reads the TSV, so this agreement is by convention, not enforced.

Controls: controls/c2-control.txt ends `EXIT=1` (red, as CONTROL-NOT-RED requires); it reports `pass=2 fail=19` for the do-nothing case.

Tool identity: tools/souji-freeze-check.py sha256 3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b at both 119c26f and 1d41c13 (unchanged between the two revs; the only file changed in that span among the C2 set is records/c2-after.txt).

## 2. Hand run of the landed tool

    python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-41/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f
    SUMMARY claims=3 findings=0            EXIT=0

    python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-40/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f
    FINDING C1 FIELD-MISSING Base|Control|Counter|Kill|Population|Target   (x3 claims, 18 lines total)
    SUMMARY claims=3 findings=18           EXIT=1

Also run at 119c26f over the round-41 prereg: SUMMARY claims=3 findings=0 EXIT=0. The r40 result is deterministic (3 runs, identical md5 c61e9eb1…).

Plausibility of the r40 result: the 18 findings are correct for the bytes they read. census/round-40/preregistration.txt has 0 `Round:` lines and 0 `Base|Counter|Population|Control|Target|Kill:` key lines (its predicates are prose, `## C1 — …` headers and `Predicate:/Control:/Kill` wording), so every claim is FIELD-MISSING on every key. This is a grammar-absence result, not a freeze result.

## 3. Operability probes (all run by hand, lane tip)

    --rev 119c26f (short)                  REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id   EXIT=2
    --rev ffff…ffff (unresolved)           REFUSAL … does not resolve to a commit                              EXIT=2
    --prereg census/round-41/nope.txt      REFUSAL … is absent at 1d41c13…                                     EXIT=2
    --root <nonexistent dir>               REFUSAL … is not a directory                                        EXIT=2
    --root <non-git dir>                   REFUSAL … --rev … does not resolve to a commit in <dir>             EXIT=2
    no arguments                           argparse usage, exit 2
    run from cwd=/ with relative prereg    SUMMARY claims=3 findings=0 EXIT=0

Refusals are clean (no traceback) and distinct from findings (exit 1). The tool reads the prereg blob at --rev, not the work tree.

## 4. Findings (ranked)

F1 (medium, operability) — DISPATCH-BEFORE-FREEZE is blind to the real wave files.
- .gitignore:1 ignores `.ufo/waves/`. `git check-ignore -v` confirms `.ufo/waves/round-41/w1-dispatch.json` and `w1.ready` are ignored.
- On disk: w1-dispatch.json, w1.ready, w2-dispatch.json, w2.ready (4 files). `git log --all -- .ufo/waves/round-41` returns nothing. The tool's dispatch_findings() uses `git log --name-only -- <tree>`, so it can never see these files.
- Result: the round-41 real leg reports findings=0 partly by vacuity for this check. The tool's own docstring says "a `*-dispatch.json` or `*.ready` file under the prereg's own directory tree", which the implementation does not honour for untracked files. The counter's dispatch-before-freeze case commits its synthetic file, so the counter never tests the ignored-file path either.
- mtimes (observed): freeze e2a74312 at 18:55:17; w1-dispatch.json 18:58:04, w1.ready 18:58:09 (after freeze); w2-dispatch.json and w2.ready 20:13:43 (after freeze). The ordering happens to be correct, but the tool cannot prove it.

F2 (low–medium, C2 predicate wording) — the retro leg does not exercise the freeze checks.
- The C2 predicate says the tool "reads census/round-40/preregistration.txt red", and the frozen mistake to mine is the r40 pre-data-freeze failure (M40-3..5). The retro red is produced only by FIELD-MISSING, because the r40 file has no Round line and no key lines. No freeze-ordering or FROZEN-EDITED finding is exercised on a real r40 artifact. The retro leg (`len(findings) >= 3`) would pass for any tool that reports missing keys.
- Read as a claim: "the tool is red on r40" is true; "the tool would have caught the r40 freeze failure" is not demonstrated by this leg. Recorded as a named limit, not a defect in the bytes.

F3 (low, evidence) — records/c2-after.txt lacks the case list (see §1). Re-running the counter is the only way to see per-case results.

F4 (info) — c2-cases.tsv (the frozen Population) is not read by the counter; agreement is by convention (checked by hand/script above, 0 mismatches).

## 5. Verdict

- C2 measured target: REPRODUCED. At 119c26f and at tip, the counter gives `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red`, exit 0, matching the frozen Target line. The frozen digests match.
- Operability of tools/souji-freeze-check.py on the real prereg: plausible. Refusals are clean and distinct; reading from the blob works; output is deterministic; the round-41 prereg is clean for the reasons its grammar can see.
- Operability caveat (F1): one of the four freeze rules (dispatch-before-freeze) cannot see the ignored wave tree, so the tool's "clean" on round-41 does not prove that rule. This is not a counter failure (the case list is what the frozen counter checks), but it is a real gap between the tool's stated contract and its behaviour, and it should be a named limit in the round lesson.
- Disagreement with the brief: the receipt lacks the case list (F3); the r40 retro is red by grammar absence (F2), not by the freeze defects it is meant to mirror.
- Recommendation for the L1: keep the C2 measurement as is (it is the frozen instrument); record F1 and F2 as named limits; do not patch the frozen counter or amend the claim.

## 6. Commands run (complete list)

1. counter at 119c26f and at 1d41c13 (2 runs, exit 0 each)
2. cat census/round-41/records/c2-after.txt; grep -c '^case-' (=0)
3. diff of SUMMARY/real/retro lines: receipt vs tip run (identical)
4. sha256sum of counter, cases.tsv, tool at 1d41c13 and 119c26f
5. freeze-check over census/round-41/preregistration.txt and census/round-40/preregistration.txt at 1d41c13; and at 119c26f
6. refusal probes (short rev, unresolved rev, absent prereg, missing root, non-git root, no args), cwd=/ run, 3x determinism run
7. git log --diff-filter=A for census/round-41/preregistration.txt (freeze e2a74312) and census/round-40/preregistration.txt (128e412)
8. git check-ignore -v on wave files; git ls-files .ufo (3026 tracked, none under round-41); git log --all -- .ufo/waves/round-41 (empty)
9. grep of Round:/key lines in round-40 prereg (0 and 0)
10. python3 TSV-vs-CASES comparison (21 rows, 19 CASES + 2 refusal rows, 0 mismatches)
11. stat mtimes of the 4 wave files
12. copied c2-tip.out to the seat dir; removed scratch dir

No mutating git or jj command was run. No file in tests/, tools/, census/, corpus/, SKILL.md or any tracked file was written.
