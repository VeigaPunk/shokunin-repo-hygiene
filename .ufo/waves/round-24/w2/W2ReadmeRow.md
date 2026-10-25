# W2ReadmeRow — attack on corpus/README.md § Round 24 (lines 504-532)

Seat: L1Souji24.W2ReadmeRow (read-only). Revision attacked: ca7fc1cb6dd1333096c6f3bdbad304686691d126.
The README is byte-identical at 778747e, ca7fc1c and the current master c3ca7ad (`git diff --quiet 778747e ca7fc1c -- corpus/README.md` → same; `git diff --stat ca7fc1c master -- corpus/README.md` → empty).
Tools installed: none. Scratch: /var/tmp/souji-r24-W2ReadmeRow/ (removed).

## Status

STATUS: PARTIAL. All 13 backticked paths exist at ca7fc1c, and every C1, C2 and C3 refusal or behavior that the section states matches the landed bytes and my probes. Three statements are false: the routed-defect "any recurrence" claim (line 532), the section's own landing condition at the commit that landed it (lines 508-512), and "8 cases fence the envelope" (line 516). Four more are stale or imprecise (lines 506-507, 509, 518, 522-523).

## Evidence

- Path existence (`git ls-tree ca7fc1c -- <p>`; all present): corpus/knowledge/{count-objects-linked-worktree-garbage,git-repo-structure-readonly,repo-size-census-readonly,count-objects-garbage-readings-r25}.md, corpus/lessons/round-23-verifier-spotcheck.md, tools/{souji-size-census.py,souji-coverage-agreement.py,souji-receipt-run.py,souji-repo-structure.sh}, tests/fixtures/{r24-size-census,r24-coverage-agreement,r24-receipt-verify}.py, census/round-24/size-census-lane.txt (blob 4ee86a7e). The other backticked spans are not paths: `.git`, `cmd=`, `tool=`, `verify`, `fsck`, `--lost-found`, the error codes, `ground`, `entries…`, `ground: F2`, `garbage: 1`, `count-objects -v`, `git repo structure`.
- Paths at the landing commit 778747e (`git cat-file -e 778747e:<p>`): every path is present except `census/round-24/size-census-lane.txt` → ABSENT. That file lands only in ca7fc1c (`git show --stat ca7fc1c`: `census/round-24/size-census-lane.txt \| 22`).
- Receipt verification (`python3 -B tools/souji-receipt-run.py verify --root <lane> census/round-24/records/<r>.tsv`): all seven print `verify=ok`. Their counts: c1-after `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`; c1-control-stub `cases=8 pass=4`; c2-after `grounded=6 mapped=6 dangling=0 mismatches=0`; c2-control-base `mismatches=2`; c2-fixture-after `cases=9 pass=9 control=FALSE-GREEN-REJECTED`; c3-after `cases=8 pass=8 refusals=2/2 regress=5/5`; c3-control-base-runner `refusals=0/2`. The five r23 receipts (census/round-23/records/{declared-evidence-after,gate-check-at-first-landing,gate-check-at-lane-base,gate-check-c3,agreement-after}.tsv) each print `verify=ok` at the current tree.
- C2 counter, run by me: `python3 -B tools/souji-coverage-agreement.py --root . --rev <R>` gives `grounded=6 mapped=6 dangling=0 mismatches=0` rc=0 for R = ca7fc1c, 778747e and c3ca7ad.
- Ground lines at ca7fc1c: the F2 entries are git-repo-structure-readonly, repo-size-census-readonly, count-objects-garbage-readings-r25 and count-objects-linked-worktree-garbage. The F4 entries are quarantine-staging-no-copy-r23 and quarantine-origin-record-fields-r24. All four F2 entries are in the line-516 entries cell, and both F4 entries are in the line-42 row. The source IDs cited in that cell (S035–S037, S115–S117, S118–S119) equal each entry's `source:` lines.
- C1 tool probe (tool bytes from ca7fc1c, scratch repos, git 2.56.0):
  - non-repository → rc=2 `refused: not a repository`
  - `--repo r --lost-found` → rc=2 `unknown or missing arguments`
  - a subdirectory → rc=2
  - a linked worktree → rc=0 `garbage=0 size_garbage=0 unreachable=0 alternates=0`, while raw `git -C lnk count-objects -v` prints `garbage: 1` with `warning: garbage found: …/worktrees/lnk/refs`
- C1 fixture digest: tests/fixtures/r24-size-census.py has sha256 373ef1f0… at both 1efe406 and ca7fc1c, so it was not edited after the controls. The tool's sha256 at 778747e and at ca7fc1c is 09bb8e0d…, which equals `tool_sha256=` in size-census-lane.txt.
- C3 verify probe: in a copy of c2-after.tsv I changed `cmd=python3 -B tools/…` to `./tools/…`. `verify` then printed `RECEIPT-TOOL-NOT-IN-ARGV` rc=2; the unmodified copy printed `verify=ok`. `durable_rev` (tools/souji-receipt-run.py:137-141) restricts durable refs to `refs/heads refs/tags refs/remotes`.
- Mutation probe (Finding 1): a scratch repo holding corpus/README.md and corpus/knowledge from ca7fc1c, with only `` `knowledge/git-repo-structure-readonly.md` (S035–S037); `` removed from line 516. Running the ca7fc1c C2 tool on it gave `grounded=6 mapped=6 dangling=0 mismatches=0` rc=0. Line 516 then names three knowledge entries while its status cell still says "read side (three entries" plus the new r24 entry.

## Findings

1. **FALSE: line 532.** Quote: "C2's `MISSING-FROM-MAP` now counts any recurrence as a mismatch." The tool counts an entry as mapped if *any* F<k> row names it (`mapped_by_k.setdefault(k, set()).update(names)`, tools/souji-coverage-agreement.py:114). It never reads status prose. The routed defect (corpus/lessons/round-23-verifier-spotcheck.md:41, "reconcile the current map table with its own “read side now holds three” prose") is a disagreement between the current table and prose. The mutation probe drops an F2 entry from the current r24 row and still scores `mismatches=0`, because the superseded r13 row at line 68 still names that entry. Entries with no `ground:` line are also invisible (fixture case 8 `ungrounded-entry` expects 0 by design). The true statement is narrower: "an F<k>-grounded entry named in no F<k> map row is a mismatch."
2. **FALSE at landing: lines 508-512, the section's own landing condition.** Quote (lines 511-512): "otherwise its cells name only the files present at that commit." The row landed in 778747e and names `../census/round-24/size-census-lane.txt`, which is ABSENT at 778747e; it first appears in ca7fc1c. The path exists at ca7fc1c, so this task's ls-tree check passes there, but the stated rule was broken by the landing commit and no correction was appended. C2 cannot see this, because `DANGLING-MAP-PATH` only checks spans ending `knowledge/<name>` (tools/souji-coverage-agreement.py:31). So c2-after's `dangling=0` at 778747e does not mean every map path resolved. Secondary point: the fixture named as co-landing (`../tests/fixtures/r24-size-census.py`) was committed in 1efe406, not in 778747e. "Lands only in the same commit as" holds only if read as "present at".
3. **FALSE / overclaim: line 516, status cell.** Quote: "The 8 frozen fixture cases fence the no-write envelope". Only cases 1-6 compare a manifest across the tool run (tests/fixtures/r24-size-census.py:139-238). Case 7 (`detector`, :241-251) runs `git fsck --lost-found` directly to prove the manifest can see a write. Case 8 (`control`, :254-259) scores a stub emitter. The cell also omits the envelope limits named in amendment 1:12-13, "a tool that restores directory mtimes after a write is invisible to this manifest", and atime/ctime are excluded. The work tree is not manifested: the manifest root is the common git dir (fixture :5-6), plus the alternate's objects dir in case 5 only. Accurate wording: "cases 1-6 assert the common-git-dir manifest unchanged; case 7 proves the detector; case 8 rejects a stub".
4. **STALE / incomplete: line 518, C3 row status.** It lists only the two frozen `verify` refusals. Amendment 1 made the symmetry literal, and those landed bytes are absent from the README: `run` refuses `TOOL-NOT-IN-ARGV` and `TOOL-PATH-REDACTED` (tools/souji-receipt-run.py:179,181); `verify` adds `RECEIPT-COMMAND-REFUSED` (:305) and an unparsable `cmd=` → `RECEIPT-MALFORMED` (:302); `cmd=` redacts per argv element; and the COUNTS_RE widening lets round-24 counts lines carry receipts. The two codes stated and "the five r23 receipts must still verify" are true (c3-after `refusals=2/2 regress=5/5`; my re-verify shows 5/5 `verify=ok`). The row is titled "verify/run symmetry" but describes only the verify half.
5. **IMPRECISE: lines 522-523, Frontier (r24).** Quote: "under the same `.git` manifest envelope the r24 fixture uses". The r24 fixture roots its manifest at the resolved *common* git dir (fixture docstring :5-6). The cited entry draws exactly this distinction in its r24 note: corpus/knowledge/git-repo-structure-readonly.md last paragraph, "the fixture's manifest is rooted at `--absolute-git-dir`, so from a linked worktree it would not see writes to the shared object store". In a linked worktree `.git` is a file, so "`.git` manifest" reproduces the ambiguity the entry warns about. The rest of the bullet holds: the :233-234 reference is the r17 colocated/plain precondition, and the r13 result is bounded per that entry.
6. **INCOMPLETE: lines 506-507.** Quote: "this table supersedes the F2 rows at :40 (r12 map) and :68 (Round 13)". A third map row carries the F2 ground token: line 217 (ground cell "F2 caveat, disclosed only: colocated repos inflate structure counts", inside the r17 table whose header cells are `ground`, `status`, `entries / runnable evidence`), and C2's `GROUND_TOKEN` reads it as F2. The section neither supersedes nor mentions it. This is harmless for C2 (that row has no knowledge path), but the list of F2 rows is not exhaustive.
7. **OFF-BY-ONE: line 509.** Quote: "the r17 convention at :205-211". Line 205 is the `## Round 17` heading, the landing-condition sentence starts on line 208 ("Landing"), and it ends on line 212 ("frontier."). The correct range is :208-212.

Statements that hold, for the record:
- line 507: F4 row :42 names both F4-grounded entries.
- line 516 C1 behavior: common-dir read, `fsck --unreachable --no-reflogs --no-progress` with no `--lost-found`, alternates counted from `alternate:` lines, and exit-2 refusals for `--lost-found`, promisor/partialClone and non-repositories (tool :125-170, :189-202, plus my probe).
- line 516: "three entries, r13/r23"; "one lane-bound measurement, no fleet figure" (size-census-lane.txt header).
- line 517: C2 row matches the tool's table rule (:77-78) and both mismatch classes.
- line 527: F1, F3 and F4 are unchanged; r24 touched only two F2 knowledge files (`git diff --stat a65fac9 ca7fc1c -- corpus/knowledge`).
- line 530: routed-defect pointer :41 and its quoted prose.
- line 531: "names every F2 entry in its entries column" (4 of 4).

## Attack log

| attack | command | result |
|---|---|---|
| paths exist at ca7fc1c | `git ls-tree ca7fc1c -- <13 paths>` | survives |
| paths exist at landing commit | `git cat-file -e 778747e:<p>` | falsified (size-census-lane.txt ABSENT) → F2 |
| C1 refusal claims | tool probe: nonrepo/`--lost-found`/subdir | survives (rc=2 each) |
| C1 linked discount | tool on linked vs raw `count-objects -v` | survives (0 vs `garbage: 1`) |
| "8 cases fence envelope" | read fixture cases 1-8 | falsified (6 of 8) → F3 |
| C3 refusal codes | verify on mutated cmd= copy; grep codes | survives; row stale vs amendment → F4 |
| r23 regression | verify 5 r23 receipts | survives 5/5 |
| C2 at tip | run tool at ca7fc1c/778747e/c3ca7ad | survives (mismatches=0) |
| "any recurrence" counted | drop F2 entry from r24 row, rerun C2 | falsified (mismatches=0) → F1 |
| F4 "both" entries | `ground:` lines at ca7fc1c | survives (2 of 2 at :42) |
| line references :40 :42 :68 :205-211 :233-234 :41 | read lines at ca7fc1c | :205-211 off by one → F7; rest survive |
| F1/F3/F4 unchanged | `git diff --stat a65fac9 ca7fc1c -- corpus/knowledge` | survives |
