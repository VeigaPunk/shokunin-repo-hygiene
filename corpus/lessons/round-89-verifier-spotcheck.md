author: hyaku closure (non-author integrator, @m_zfl)

# Round 89 verifier spot-check — souji (non-author, hyaku closure)

Lane: `souji-shokunin`. Lane base `a2cef94a431dc184e49f980b2664166f081587a4`; lane HEAD after the round
`1786b5527b29f48a6a04b5b11a50528182880761` (remote `refs/heads/master` equals it). Report
`.ufo/reports/round-89/souji.md` committed in the fleet repo by the lane identity
(`git log --format='%an %H' -- .ufo/reports/round-89/souji.md` -> `souji-shokunin
50e8c6bea8af97f8b5e935378059e8081b9c41dd`; author date 10:55:05 -0300, committer date 10:56:14 -0300).

Dispatch/complete digest copied from the closure prompt (mutable `.ufo/watchdog.log`):
`2026-11-08T09:18:13-03:00 launch souji round=89 pgid=1801868 driver=hyaku-inline attempt=1`
`2026-11-08T10:56:38-03:00 complete souji round=89; hyaku-inline attempt=1`

## 1. Step-1 conformance

- **Report identity and path: PASS for identity.** The fleet report commit is authored and committed by
  `souji-shokunin <souji@shokunin.local>`; no later sweep. It is not a marker: the report names real
  committed work (census instruments, tool repair, population, receipts, sources) and a checkable lane tip.
- **`SHONEN` heading: PASS.** One heading, four `[~]` lines, each with a resolvable pointer
  (`grep -c '^## SHONEN'` -> 1; `grep -n '^- \[~\]'` -> 4). `SHONEN.md` carries the same four boxes.
- **Cited lane commits: PASS.** `git merge-base --is-ancestor <h> refs/heads/master` exits 0 for every
  cited hash: `c9329534`, `d8bc7484`, `4854c8d7`, `a3c7cb1f`, `755a46cb`, `4864129b`, `c2ee31a`; the base
  `a2cef94a` and the tip `1786b552` are also ancestors. `git cat-file -e` finds all of them.
- **Lane state: PASS for tracked work.** `scripts/hyaku/jj-lane.sh state` ->
  `branch=master local=1786b552 remote=1786b552 ahead=0 behind=0 head=detached tracked=0 untracked=0`;
  `git status --porcelain` is empty.
- **Prompt contract: PASS.** `.ufo/prompts/souji-round-89.md` starts with a byte-identical rendering of
  `templates/round-prompt.md` (8,566 bytes / 140 lines; substitutions = lane `souji`, round `89`, fleet root,
  lane repo path, the `shokunin.conf` axes string) followed by hyaku addendum section 6. It carries the
  round-level items (mission/axes, L2 floor, commit-then-push, push scope, L0) and the five child-lane items
  (report path, commit-before-report, `SHONEN` heading, hash citation, lane write scope).
- **Round shape: PASS with one role-split defect.** One v1 wave, 12 seats, `w1-results.json` 12/12 settled,
  no dead seat; strict policy attack set (reviewer x2, critic, mutation-tester, labrat) 5/12 = 42% >= 25%;
  connector seats 1 <= 2; residual 0; 12 is inside the 8-16 band. **Defect:** the prompt's minimum split asks
  3 executors and a planner seat; the wave has 2 executors and no planner seat (the L1 holds the planner
  role). Status-neutral.
- **Wave-evidence durability: DEFECT (major, status-neutral).** The report's landed-changes row says
  `4864129b` carries "wave evidence (12 seat reports + receipts + results)", but
  `git ls-tree -r --name-only 4864129b -- .ufo/waves/round-89` lists only `build-spec.py`,
  `claim-falsification.tsv`, `w1-dispatch.json`, `w1-results.json`, `w1-spec.json`, `w1.ready`: the
  `w1/` seat reports and receipts are absent. `.gitignore:1` is `.ufo/waves/`, so
  `git check-ignore -v .ufo/waves/round-89/w1/S89Connector.md` reports the ignore and
  `git status --porcelain --ignored` shows `!! .ufo/waves/round-89/w1/`. The evidence resolves only in the
  local working tree; a clone of the pushed tip cannot see it. Rounds 86, 87 and 88 force-added their wave
  files (`git ls-files .ufo/waves/round-8{6,7,8}` -> 209/280/125 files), so r89 is a regression in evidence
  durability. This is exactly why the pre-file gate passes locally and fails on the pushed bytes (section 2).
- **Report accuracy: DEFECT (minor).** The `Extras` pre-file line says
  `PREFILE-FALSIFICATION: pass claims=2 rows=12 attack_seats=6 findings=0`, while the final ledger has 13
  rows and 7 attack seats. The missing S89Distiller row landed in `1786b552` at 10:55:21, after the report was
  authored at 10:55:05; a gate run over the 12-row ledger and the committed `w1-results.json` (which already
  listed the Distiller as a reviewer-role seat) would have reported `attack-seat-unread`, not a pass. The
  report's seat list likewise omits the Distiller. The lane fixed the ledger after filing; the report's stated
  number is stale, and the report was written before its own last lane commit.
- **Other report-contract defects (status-neutral).** (a) The discernment trend reads
  "mixed -> improved by the honest stop", not one allowed token. (b) The landed-changes row for
  `census/round-89/claims.json` carries `—` in the LOG.md column. (c) `corpus/README.md`'s coverage map and
  frontier stop at r86; the r89 knowledge entry is not indexed (r87/r88 entries were not indexed either).
  (d) The `S351` row title says "Python 3.14" while the capture and the live page are 3.15.2 (disclosed in
  A3; the source cell names the capture title). (e) The capability table row "a malformed-row binding whose
  id is absent from the ledger (measured, not landed)" is a design, not a landed capability; it should not sit
  in the capabilities table. (f) The new "Planned (r90)" block was inserted above the existing "Planned (r89)"
  block.

## 2. Pre-file falsification ledger (addendum section 8, Amendment 59)

Local working tree:

```
python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 89
PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=7 findings=0
EXIT=0
```

Every `claims.json` claim is covered (C1, C2); all seven attack seats are named
(S89Connector, S89Critic, S89Distiller, S89Labrat, S89MutCounter, S89Reviewer, S89Sentinel); every
`falsifies-wording` row names a narrowing: A1 (C1/LD2), A2 (C2 injectivity/window), A0.6 (harness pin). I
adjudicate the rows: the C1 rows are real (the LD2 mechanism is reproduced in S89MutCounter F1, S89Sentinel
3.4, S89Reviewer 1 and S89Simplifier F1) and A1 explicitly says the frozen target is NOT met, so C1 does not
verify; the C2 rows are real (0x85/U+0085 collision, 202-byte window) and A2 narrows the headline while the
enumerated KFF6/KFF7 rule stays intact, so C2 verifies as narrowed. No row is spurious.

On the pushed bytes the same gate fails for durability, not for wording:

```
# fresh clone at 1786b552, report copied to a synthetic fleet root
PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13
EXIT=1        # 13 artifact-missing rows: .ufo/waves/round-89/w1/* are not in the commit
```

The ledger itself is complete and committed; its referenced artifacts are not (section 1). The defect is
named and routed; it does not change the claim verdicts.

## 3. Per-claim re-check

I re-ran both claims from the committed lane bytes. Work roots were empty directories under
`/fast/scratch/hyaku/`, never `/tmp`.

### C1 — calibration 7 (re-measured by this judge; DOES NOT VERIFY)

Command (the frozen one, same counter/mutants/populations, tip harness):

```
python3 -B census/round-89/c1-clause-battery.py \
  --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r89-verify-c1 \
  --only r88,r89 --expect-killed 28
```

Observed (1,695.8 s wall; full log kept at `/fast/scratch/hyaku/souji-r89-verify-c1.log`):

```
# counter sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
# harness sha256=6165eade37f6bfb2d820c8fe5c655831a411695a9f1eddbbd93801a8d36ca63c
# mutants sha256=bc7e6bb1983a19ab6781dba10b3b6c0be9085a7a1ed01d67d8eedec10aeb56ec
# population r88 sha256=b710e368...a68c3 rows=53
# population r89 sha256=04570a64...1e093 rows=57
ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
MUTANT-PAIR m18b-alnum-before pop=r88 killed=no | pop=r89 killed=yes
MUTANT-PAIR m17b-target-keyed pop=r88 killed=no | pop=r89 killed=yes
MUTANT-PAIR m17c-no-malformed pop=r88 killed=no | pop=r89 killed=no
MUTANT-PAIR m18d-first-only pop=r88 killed=no | pop=r89 killed=yes
SUMMARY mutants=16 sets=r88,r89 pristine_r88=ok pristine_r89=ok killed_r88=12 killed_r89=15 killed_total=27
EXIT=1
```

The values match the report and `records/c1-after.txt` cell for cell: fifteen of sixteen killed on r89,
`m17c-no-malformed` survives, the frozen target `12/16/28 EXIT 0` is **NOT MET**. The three new bindings
behave as claimed (`NF6h` -> `m18b`, `LD1b` -> `m17b`, `NF6i` -> `m18d`, each killed on r89 and alive on
r88); `LD2` binds nothing (`m17c` survives on both). The before arm is the r88 column of the same run and
agrees with `controls/c1-before.txt` (12 killed, four survivors, EXIT 0). Pins re-derived from committed
bytes: counter `fd0a8e24...` is byte-identical at r87 `77ccef7c`; items `ce80195d...`; the r89 population is
the r88 53 data rows byte-for-byte in order plus NF6h/NF6i/LD1b/LD2 (verified by comparing the data rows).
The prereg harness pin `c75cd946...` is stale against the filed `6165eade...` (A0.6, landed after F); the
before receipt's header still prints the old pin. **Verdict: C1 does not verify; calibration `unprovable`.**

### C2 — operability 8 (re-measured by this judge; VERIFIES as narrowed)

After arm (1.29 s):

```
python3 -B tests/fixtures/r89-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-89/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r89-verify-c2
CASE KFF6 tool=pass before=fail ; CASE KFF8 tool=pass before=fail ; all ten tool=pass
SUMMARY cases=10 tool_pass=10 before_pass=8 ; EXIT=0
```

Before arm (same fixture, the r88 tool bytes `4042218f...` as BOTH arms): `SUMMARY cases=10 tool_pass=8
before_pass=8`, KFF6 and KFF8 fail, `EXIT=1`. Tool `f6fce6d1...`, before bytes `4042218f...`, fixture
`a9b03141...` all match the receipt headers and the report. The r87 12-row K4 regression on the filed tool
(`census/round-87/c2-k4-counter.py`, 3.71 s) reads `SUMMARY rows=12 mismatches=0 errors=0`, `EXIT=0`, writer
`70bbf1c2...`, every row `match=yes`. The narrowing is real: `S89ExecC2` section 6 measures raw `0x85` and
UTF-8 NEL as the same `\x85` cell on r89 (r88 kept them distinct), and the raw window is 202 bytes
(head-100 + three-byte U+2026 + tail-99), not 200. The frozen enumerated rule (KFF6/KFF7 + KFF8 head) is
met. **Verdict: C2 verifies under its narrowings; operability `improved`; the 0x85/NEL collision is routed
to r90.**

## 4. Axis-harm check

`git -C souji-shokunin diff a2cef94a 1786b552 -- SCORECARD.md` is additive: r89 measurements, two capability
rows, the r90 planned block; the paragraph "No owned axis score changed (calibration 7, coverage 8,
operability 8 ...)" holds. `SKILL.md`/`PROVINCE.md` are untouched; `QUALITY.md` gains Q164; `SOURCES.md`
gains S351; `tools/souji-record-agreement.py` is the only code repair (31 added lines, one replaced line).
No owned axis was harmed. Two record defects are named, not harm: the design-only capability row and the
r90/r89 planned-block order.

## 5. Discernment spot-check (`corpus/lessons/round-89.md` `## Gate`)

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` -> `souji ok`, `EXIT=0`, with the S351 duplicate-URL W04 (the expected
scope-narrowing line); W04 count 88 before -> 89 after. Rows
`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` -> 274 at tip, 273 at base
`a2cef94a`. `git diff a2cef94a 1786b552 -- corpus/SOURCES.md` adds only S351.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S351 Python `codecs` Error Handlers, `surrogateescape` (the round's admit) | admit (A, `mined`) | live `https://docs.python.org/3/library/codecs.html#error-handlers` -> HTTP 200, 181,610 bytes, sha256 `62a3d3da...fea6f` = the capture; quote located at the `surrogateescape` table cell | agree | the 13-word quote "On decoding, replace byte with individual surrogate code ranging from U+DC80 to U+DCFF." is present once (normalized offset 12,540; the lane's stripper reads 12,792) and the page title is "Python 3.15.2 documentation"; the row is a scope-narrowing row on the held codecs URL (S253/S256 own `replace`), and `used-by` `corpus/knowledge/decode-escape-order.md` exists |
| S352 Python `base64` `b64encode`/`validate` (the round's reject sample) | reject, not filed | live `https://docs.python.org/3/library/base64.html` -> HTTP 200, 79,712 bytes, sha256 `4b7d1eef...49db` = the r89 capture; S349's 15-word quote present once | agree | the scope is exactly S349's standing reject (encoding mechanics, not a record-format rule; S348 carries the enforceable one-line property), and S349's flip condition is unchanged; re-filing the same page would add registry weight, so recording the reject in the Gate rather than as a duplicate row is the correct curatorial call |

The S351 row's <=25-word quote (the Gate's 13-word sentence) is verbatim in the capture and in the live
fetch; the capture is byte-identical to the live page. The row's "3.14" title against the 3.15.2 capture is
disclosed in A3 and is the only wording defect in the row.

## 6. Trend verdicts

- **expansion: improved.** `SOURCES.md` 273 -> 274 (`grep -cE` above), S351 admitted `mined`, one new
  admitted knowledge entry (`corpus/knowledge/decode-escape-order.md`) whose `source:` cites S351 and S348,
  and the C1 population/mutant sets grow 53->57 rows and 12->16 members on ground the r88 corpus did not
  hold. The README coverage-map gap is a routed defect, not a counterweight to the admitted entry.
- **quality: improved.** Q164 records the raw-first/surrogateescape rule; C2 is 10/10 after vs 8/10 before
  through the public path (re-measured), with the r87 12-row counter unchanged (`rows=12 mismatches=0
  errors=0`); no admitted entry was found false and left unmarked. The 0x85/NEL collision and the C1 miss are
  recorded in A1/A2, the lesson and the SCORECARD and carried to r90.
- **discernment: improved.** The spot-check agrees with both sampled gate decisions (S351 admit, S352
  reject), re-opened against the live pages and the committed captures; and the round's own wave falsified
  its C1 target and its C2 headline and the lane filed the honest values ("C1 ... NOT MET", headline
  narrowed) instead of defending or re-scoring them. The report's "mixed -> improved" wording is a report
  defect, not a different verdict.

## 7. Routed defects (lane to fix in round 90)

1. **Commit the wave evidence (major).** `git add -f` (or fix `.gitignore`) the 12 seat reports and their
   receipts under `.ufo/waves/round-89/w1/`, and stop writing "12 seat reports" in a commit message whose tree
   does not contain them. The prefile ledger's artifacts must resolve from the pushed lane, not only from the
   local working tree.
2. **File the report after the ledger is final.** The reported pre-file number (12 rows / 6 attack seats) is
   stale against the final 13/7 and the report was written before `1786b552`; re-run the gate immediately
   before filing and quote its actual output.
3. **C1 calibration:** bind `m17c` with the measured `LD2b` row (`ZZ9\tABSENT`, an id absent from the frozen
   ledger) and re-measure the 16/28 target; the LD2 row design is already falsified (M1).
4. **C2 operability:** spell U+0085 as `\u0085` in `_escape_text` (or add KFF9) so the r89 repair does not
   collide on the byte/NEL pair that r88 kept distinct; add the limit to Q164's text if it is not expressed
   as the KFF6/KFF7 pair only.
5. **`corpus/README.md` coverage map/frontier:** index `decode-escape-order.md` (and the r87/r88 entries) and
   add the r89 frontier section; the map stops at r86.
6. **Capability table:** move the "malformed-row binding (measured, not landed)" row to planned; the
   capabilities table admits only demonstrations that ran and landed.
7. **Role split:** dispatch the prompt's third executor and a planner seat, or record the L1-planner waiver
   explicitly in the round plan.
8. **Trend token:** use exactly one of `improved | harmed | unchanged | unprovable-but-better` for each trend
   in the report (discernment currently reads "mixed -> improved").
9. **Landed-changes LOG column:** tie `census/round-89/claims.json` to the round-89 LOG entry instead of `—`.
10. **S351 version title:** name the capture's 3.15.2 (or both 3.14 and 3.15.2) in the row title; A3's note
    is a disclosure, not the row's own statement.
11. **SCORECARD order:** move the r90 planned block below the existing r89 planned block (or mark r89
    superseded) so the section reads in round order.

## 8. Reproducibility notes

Both counting commands were re-run by this judge from the committed bytes; the C1 battery took 1,695.8 s and
the C2 fixture 1.29 s (after) / 1.29 s (before); the r87 12-row K4 regression took 3.71 s. All work roots were
empty directories under `/fast/scratch/hyaku/` (never `/tmp`). Pins re-derived from committed bytes: counter
`fd0a8e24...`, r89 population `04570a64...`, mutants `bc7e6bb1...`, harness `6165eade...` (tip; the prereg's
`c75cd946...` is the A0.6 stale pin), tool `f6fce6d1...`, before tool `4042218f...`, fixture `a9b03141...`.
The pushed-tip prefile failure was reproduced from a fresh clone of `1786b552` with a synthetic fleet root:
`PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13`, `EXIT=1` (13
`artifact-missing` rows, no `claim-uncovered`/`narrowing-missing` rows).
