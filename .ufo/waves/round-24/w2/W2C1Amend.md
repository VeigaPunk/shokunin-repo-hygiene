# W2C1Amend — attack on amendment discipline (souji r24 w2, FALSIFY)

## Status
STATUS: FAIL — the claim "every change stricter, sanity runs not claim data" is falsified on three points: (1) the control-timing remedy weakens frozen "after-data" to "after-receipt"; (2) the case-6 input substitution lets a tool that ignores `extensions.partialClone` score 8/8 (shown with a mutant); (3) the C3 "sanity" run used the exact landing runner bytes, and a C1 lane-tool 8/8 run that predates the controls is not disclosed. These survive: commit order (no after-receipt before the amendment commit), the C1 fixture's per-case predicates (all supersets of the frozen ones; C=8, no case dropped), and C2's kill rule.

## Evidence
Revisions: lane base a65fac9; prereg f9db218; instruments+amendment 1efe406; control ce5971c; after-state 778747e; after-receipts ca7fc1c. `git rev-parse master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (wave-1 reports commit, one past ca7fc1c). Host: git 2.56.0, Python 3.14.8.

- `git log --format='%h A=%ad C=%cd' a65fac9..master` gives committer times 1efe406 06:29:29, ce5971c 06:29:45, 778747e 06:33:39, ca7fc1c 06:34:57, c3ca7ad 06:35:24 (-0300). Author dates are change-creation times (1efe406 A=06:14:49).
- Receipt `utc=` fields: controls 09:29:39Z, 09:29:40Z and 09:29:41Z (after the amendment commit at 09:29:29Z, before ce5971c). After-receipts 09:34:44Z–09:34:49Z (after 778747e, before ca7fc1c).
- `git log -- <file>`: the prereg was touched only by f9db218, and the amendment and all three fixtures only by 1efe406. Appending holds, and no counter was edited after the controls ran.
- Fixture bytes: `sha256(w1/r24-size-census.py)` = 1efe406 = 778747e = `373ef1f0…84f`. The same equality holds for the C2 and C3 fixtures and for the C2 tool.
- Working-tree mtimes: the prereg was last written 06:14:44 and the amendment 06:28:32. `w1/ExecSizeCensusFixture.md` was written 06:28:39 and `w1/ExecReceiptFixture.md` 06:29:05.
- `git show 778747e:tools/souji-receipt-run.py | sha256sum` → `9df0738cdfd969fc0c75ea858f5c2392d34dbf4bb78911916637e146850d82ff`. At 1efe406 the same command gives `e13d0c83…` (the base runner).
- Mutant run in `/var/tmp/souji-r24-W2C1Amend/`. I copied the 778747e tool and deleted lines 152–158 (the `extensions.partialClone` refusal). `python3 -B fixture.py --tool mut-noext.py` printed `CASE 6 refusal PASS … partial_clone[exit=2 …] promisor_unset[exit=2 …]` and then `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit=0.
- Frozen-literal arm: a repo with `core.repositoryformatversion=1` and `extensions.partialclone=origin`, no promisor key and no `.promisor` pack. Landing tool: `refused: partial-clone repository (extensions.partialClone=origin)` exit=2. Mutant: `garbage=0 size_garbage=0 unreachable=0 alternates=0` exit=0.
- C2 per-entry check: `git grep '^ground: '` at a65fac9 finds 4 grounded entries (r25, quarantine-origin-r24, quarantine-staging-r23, repo-size-census). At 778747e all 4 are present with the same F<k>, plus 2 more (6 ≥ 4).
- `git show 1efe406:tests/fixtures/r24-receipt-verify.py | grep -c -E 'COMMAND-REFUSED|RECEIPT-MALFORMED|TOOL-PATH-REDACTED'` → `0`.
- Scratch removed (`ls: cannot access '/var/tmp/souji-r24-W2C1Amend'`). No tools installed.

## Findings
1. **Remedy weakens a frozen condition (not stricter).**
   - prereg.txt:64: "NOT print the target line; its receipt is committed before any after-data."
   - amendment-1.txt:8: "before data); they are committed before any after-receipt, as the remedy CritPrereg names."
   - After-receipts are a subset of after-data, so the amendment replaced the frozen bar with a weaker one, inside a document whose line 3 says "Every change below is stricter than the frozen text".
   - After-data did exist before ce5971c (findings 3 and 4). Axis: calibration.
2. **Case 6 input substitution: a frozen-literal failure passes 8/8 (coverage regression in the counter, not in the tool).**
   - The frozen text names the key form. prereg.txt:38: "promisor/partialClone repo". prereg.txt:55: "partialClone repo -> exit 2".
   - amendment-1.txt:19 makes the arm "a real `git clone --filter=blob:none` (remote.origin.promisor=true and". On git 2.56.0 that clone carries no `extensions.partialClone` (`w1/ExecSizeCensusFixture.md:73`: "git 2.56.0 writes no `extensions.partialClone` key on a partial clone").
   - The fixture's setup accepts either key (`r24-size-census.py:227-230`), but no arm carries `extensions.partialClone`. The mutant that drops that refusal scores 8/8 (Evidence).
   - The landing tool does refuse that repo, so C1's tool is unharmed. But the counter's 8/8 no longer certifies the frozen "partialClone" refusal. No case was dropped and no expected value lowered; the input class was swapped. Axis: coverage.
3. **The C3 "sanity" run was the after-measurement on landing bytes, taken before the controls.**
   - The disclosure (amendment-1.txt:5) says "C3 fixture (base runner 6/8 refusals=0/2; patched runner" … "8/8 refusals=2/2" and calls these runs "not claim evidence".
   - `w1/ExecReceiptFixture.md:81` records the lane working-tree runner as `9df0738cdfd969fc0c75ea858f5c2392d34dbf4bb78911916637e146850d82ff` → `cases=8 pass=8 refusals=2/2 regress=5/5`. That digest equals `778747e:tools/souji-receipt-run.py`. Fixture `f8c4c391…` is unchanged, so c3-after.tsv reproduces this run byte for byte.
   - The amendment's "Pinned target line" (amendment-1.txt:37) and the "Symmetry made literal" clauses (amendment-1.txt:39) were therefore written with the landing result already observed. Pinning a target you have already met is stricter only on paper. The disclosure does not say the "patched runner" was the landing runner. Axes: calibration, operability.
4. **An undisclosed C1 after-run on the claimed surface predates the amendment commit and the controls.**
   - `w1/ExecSizeCensusFixture.md:39` reports a run on the lane tool: "--tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-size-census.py; echo exit=$?` (L1-integrated lane tool, read-only use)". The same line records "`cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit 0".
   - The report file was written at 06:28:39, before the amendment commit (06:29:29) and the stub control (09:29:40Z).
   - The amendment discloses only the C2 and C3 runs. The scored lane tool is not byte-identical to the landed one (the 778747e tool, `09bb8e0d…`, rewrote 65 lines vs 1efe406 `7ad5cc76…`), so this is a pre-control C1 after-data point, not the receipt itself. [INFERENCE] The digest of the scored lane-tool bytes was not recorded by that seat.
5. **The C1 kill-rule letter was crossed in a stricter direction (a tradeoff for the judge, not a loosening).**
   - prereg.txt:69 rule: "no case is dropped or re-specified after any seat has scored."
   - Wave-1 seats scored mutants and reference tools on earlier fixture revisions before cases 3–6 were re-specified. `w1/ExecSizeCensusFixture.md:85`: "Before amendment 1, a zero `size_garbage` passed case 3". `w1/CritC1Control.md:30-37` lists six cheaters reaching 8/8.
   - CritC1Control A5 flagged the condition itself. Every re-specification tightened its case. Whether "scored" covers instrument-validation runs is ambiguous; the strict letter is breached.
6. **The COUNTS_RE widening is an admitted loosening listed under "every change stricter".**
   - amendment-1.txt:42: "Separate widening (not a C3 clause): verify's COUNTS_RE also accepts the round-24 counts lines".
   - `778747e:tools/souji-receipt-run.py:63-71` adds `cases=\d+ pass=\d+` and four more alternatives.
   - It cannot flip a C3 case: the fixture's tiny-counter prints an `assertions=` line that the base regex already matched. Every round-24 receipt verifies only because of it, and it landed in the same commit as the claim work. The amendment's header claim is false as written for this bullet. Axis: calibration.
7. **The C3 symmetry clauses have no counter.** The C3 fixture contains no `COMMAND-REFUSED`, `RECEIPT-MALFORMED` or `TOOL-PATH-REDACTED` (count 0). Those amendment clauses add requirements on paper that `cases=8 pass=8` does not certify. Axis: operability (claim overreach).
8. **Survives: the C1 fixture against the frozen case text, case by case.**
   - Case 1: all four counts 0, exit 0, manifest unchanged (`:143`).
   - Case 2: `counts[2]==1`, no delta, no lost-found (`:153`).
   - Case 3: garbage=1 plus size_garbage=2, two arms (`:164-175`).
   - Case 4: garbage=0, witness==1 read after the tool (`:185-190`).
   - Case 5: alternates=1 plus both manifests (`:207`).
   - Case 6: three exit-2 arms (`:234`).
   - Case 7: delta plus `lost-found/other/<oid>` (`:250`).
   - Case 8: stub over `CASES[1:5]` = cases 2–5 (`:258`).
   - The manifest is a superset of the frozen one (directories added, `mtime_ns`). The last line and exit rule match prereg:44-45. The precondition exit 2 cannot produce exit 0. One soft spot: `run()` turns setup exceptions into FAIL, so a stub "fails" case 8 on a setup crash. Receipts show real discrimination (`stub_failed=dangling,garbage,alternates` with counts lines).
9. **Survives: C2.**
   - The per-entry kill rule adds to the count rule; both pass (4 base entries kept, same F<k>; 6 ≥ 4).
   - The backticked `knowledge/<name>` mapping is narrower than "basename appears". It is neutral on the observed data: at base, the two missing basenames occur only in the F2 status cell (`a65fac9:corpus/README.md:68`) and in prose (`:478`, `:480`), never in an entries cell. The frozen-literal base is therefore also 2, matching `c2-control-base.tsv`.
   - The C2 tool bytes (`71b89eb3…`) are unchanged from the wave-1 draft through 778747e.
10. **Survives: order.** No after-receipt was created or committed before 1efe406. The control receipts were produced 10–12 s after the amendment commit and committed before the after-state. One more pre-control item exists: `census/round-24/records/r13-repo-structure-recheck-git2.56.0.out` (mtime 06:22, committed in 778747e). It is an r13 re-verification output, not a C1–C3 counter, so it is out of claim scope.

## Attack log
| # | attack | executed | result | class |
|---|---|---|---|---|
| A1 | dropped case or loosened expected value in C1 fixture | read fixture `:139-264` against prereg:47-60 | none found; all predicates supersets | survives |
| A2 | after-receipt before amendment commit | git log committer dates plus receipt `utc=` | order clean | survives |
| A3 | amendment text vs frozen text, word-level | prereg:64 vs amendment:8 | after-data narrowed to after-receipt | fixable defect (disclosure) |
| A4 | frozen-literal partialClone repo vs amended case 6 | mutant `mut-noext` through fixture plus literal repo | mutant 8/8; literal repo censused exit 0 | tradeoff (counter coverage) |
| A5 | sanity run = landing bytes? | sha256 of 778747e runner vs ExecReceiptFixture:81 | identical `9df0738c…` | disclosure understated |
| A6 | undisclosed pre-control C1 run | ExecSizeCensusFixture:39 plus mtimes | lane-tool 8/8 at 06:28:39 | disclosure omission |
| A7 | C2 kill rule bypass by re-grounding | `git grep '^ground: '` base vs tip | all base entries kept | survives |
| A8 | C2 mapping reinterpretation inflates control | base README occurrences of the 2 missing basenames | neutral; frozen-literal also 2 | survives |
| A9 | symmetry clauses counted? | grep of C3 fixture for codes | 0 hits | claim overreach |

Smallest safe corrections. None of these touches a counter, because post-data counter edits are barred.
- Record findings 1, 3, 4, 6 and 7 as deviations in the scorecard and lesson.
- Make the C1 verdict say that the `extensions.partialClone`-only refusal is not pinned by the counter, and preregister that arm for r25.
- Make the C3 verdict say "two named residuals verified; symmetry clauses (COMMAND-REFUSED, MALFORMED, run TOOL-PATH-REDACTED) unverified by the counter".
- Strike the word "stricter" from the COUNTS_RE bullet by an amendment-2 note or scorecard text; the frozen files stay unchanged.

Tool installs: none.
