# S70MutWriter — r70 mutation probe: writer pathspec scrub vs frozen C1 + writer case 38

Lane read-only HEAD during runs: 20c117ce160db5c5fc2b88663404b161a8b3c68a; tip writer sha256
118597e0b537d104a54ac5206f038a364905f65ff8267725457d06ff8952e71f (= 93a051b bytes);
counter/matrix sha256 3f684c3e… / 1607e4f8… (equal to freeze 0243af04). No installs; git 2.56.0.

C1 (cwd = lane root): python3 -B census/round-70/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333 --new-tool /fast/scratch/hyaku/souji-r70/S70MutWriter/<F> --work /fast/scratch/hyaku/souji-r70/S70MutWriter/c1-<id>
ST: TMPDIR=/fast/scratch/hyaku/souji-r70/S70MutWriter/wst-<id> python3 -B /fast/scratch/hyaku/souji-r70/S70MutWriter/<F> --selftest --work /fast/scratch/hyaku/souji-r70/S70MutWriter/wst-<id>

Baseline (pristine tip): SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS, EXIT=0 → detector green on pristine bytes; killed mutants below are real.

| id | edit (tools/souji-receipt-write.py) | C1 nf/nh/cm | EXIT | case 38 | verdict |
| W1 | :105 tuple loses GIT_LITERAL_PATHSPECS | 4/15/5 | 1 | PASS 38/38 | killed by C1 (LD,LN4,LG1,LA9 forged; LU1 class); survives case 38 |
| W2 | :105 tuple loses GIT_GLOB_PATHSPECS | 0/14/0 | 1 | PASS 38/38 | killed by C1 (GA over-refused); survives case 38 |
| W3 | :105 tuple loses GIT_NOGLOB_PATHSPECS | 0/15/0 | 0 | PASS 38/38 | SURVIVED both |
| W4 | :105 tuple loses GIT_ICASE_PATHSPECS | 0/14/0 | 1 | PASS 38/38 | killed by C1 (ICA over-refused); survives case 38 |
| W5 | :111 drop `and k not in PATHSPEC_ENV` | 4/13/5 | 1 | FAIL (LITERAL skip-worktree rc=0) | killed both; C1 equals do-nothing control exactly |
| W6 | scrub only first ls-files call (:393; :402 in the mutant), removed from git() | 0/12/2 | 1 | FAIL (LITERAL honest rc=2 STATE-CHANGED) | killed both (LA,GA,ICA over-refused; LU1,LG1 class) |
| W7 | scrub applied to every call except status (`"status" in args`) | 0/15/0 | 0 | PASS 38/38 | SURVIVED both |

Every row: base_forgeries=4 base_honest=13 new_echo=0 errors=0 regress=PASS; nf=new_forgeries, nh=new_honest, cm=class_mismatches. W3/W7 outputs byte-identical to baseline except slot/header lines.
Base-writer case-38 probe (base blob e063a2fc + tip PATHSPEC_ENV tuple :105, case_38 function :1499, CASES entry :1565): SELFTEST cases=38 pass=37 fail=1 — "GIT_LITERAL_PATHSPECS=1 skip-worktree rc=0"; tip control 38/38 pass ⇒ case 38 can fail and fails on pre-change bytes.
Claim check: C1's frozen SUMMARY/EXIT reproduce on pristine bytes; every substantive single edit (W1,W2,W4,W5,W6) is killed by the frozen matrix, so C1's numbered claim is not falsified. C2 not touched by this seat.

Findings
- HIGH (incident, fleet repo /home/vgpnk/Projects/shokunin, not the lane): my probe's `mktemp -p "$S" probe.st` lacked XXXXXX; mktemp failed, `git -C ""` fell back to cwd (fleet root) and `git add -A && git commit -m seed` ran there. Result: commit cff0b4cbe684ce702bca2a126b579d602f0cd6ae (parent 02a592827f1f740999357862d2e3024de1ff0e44, author p <p@x>, 2026-11-06 16:05:54 -0300) added .scratch/run15-state.json (M), versions.html (A), w4lines.txt (A), +235/−79. It is now an ancestor of main/master (log: cff0b4cb seed → cfe0e4cc → 1fe72c80). Content intact; no deletions. I ran no recovery (mutating git forbidden to me); orchestrator decision required (e.g. keep, or rewrite cff0b4cb out of fleet history). Root cause: missing mktemp template + git -C "" semantics.
- MEDIUM: writer case 38 loops `for var in PATHSPEC_ENV` — the same constant the writer scrubs with. Removing one variable removes its own test: W1/W2/W4 keep 38/38 while C1 kills them; W3 leaves the scrub list with both detectors green. Selftest is not independent of the implementation constant it validates (dual of C2's mutation rationale).
- LOW: W3 (NOGLOB scrub removed) survives both detectors = honest limit, not a claim gap: matrix NGA/NGD pass either way and my probe (probe-status-noglob.txt) shows `ls-files -v -z ':(top)'` is identical under NOGLOB/under none, so the variable is verdict-inert on this surface; only the prose "every writer git call" is unobserved for NOGLOB.
- LOW: W7 (scrub omitted for status) survives both = honest limit: `git status --porcelain` takes no pathspec and my probe shows identical status bytes under all four variables; the claim sentence "every writer git call" is broader than any observable consequence.

Files written under .ufo/waves/round-70/w1/S70MutWriter/: S70MutWriter.md (this report), mutants.diff,
probe-status-noglob.txt, c1-baseline.txt, c1-W1.txt…c1-W7.txt, st-W1.txt…st-W4.txt, st-W5.txt,
st-W5c.txt, st-W6.txt, st-W6c.txt, st-W7.txt, st-base38.txt, st-tip.txt (22 files). Scratch
/fast/scratch/hyaku/souji-r70/S70MutWriter removed after copying; lane untouched.
