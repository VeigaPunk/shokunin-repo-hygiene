# souji round 85 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane round 85, base `705fa1385c4ccec23811cfa57104046ec6587258` (r84 closed `admitted`), after
`aa2b9ccf5ec3b70a023b9e315482e261690262a7` (branch `master`, `local=remote`, `ahead=0`, `head=detached`,
`tracked=0 untracked=0`). Report `.ufo/reports/round-85/souji.md` (fleet repo commit `dc7fe33d` by
`souji-shokunin`, after lane tip). Driver digest (`.ufo/watchdog.log`, mutable — pointer at closure):
`2026-11-08T04:33:04-03:00 launch souji round=85 pgid=1687441 driver=hyaku-inline attempt=1`;
`2026-11-08T05:31:03-03:00 complete souji round=85; hyaku-inline attempt=1`.

Outcome: status `ok`, **admitted**. C1 and C2 both verify — I re-measured both before→after arms myself on the
committed bytes (commands and outputs below; C1 150 s, C2 7-row counter both arms). No owned axis is harmed.
The pre-file ledger passes clean (`pass claims=2 rows=14 attack_seats=6 findings=0`, exit 0 — the two r84
ledger-gate defects are fixed). One registry-count discrepancy between the report (259→260) and the committed
bytes (259→263) is named as a status-neutral defect; it does not bar admission because the frontier section's
substance (counting command + census receipts + rows by tier) resolves and the lesson states 259→263 correctly.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-85/souji.md` | `souji-shokunin dc7fe33d…` | pass |
| `## SHONEN` heading, one line per box | `grep -n '^## SHONEN' .ufo/reports/round-85/souji.md` | 1 heading (line 163), 4 lines all `[~]` with resolvable pointers | pass |
| cited commits exist and are ancestors of `master` | `git -C souji-shokunin merge-base --is-ancestor <h> master` over `5bd5a0ce…`, `43c630eb…`, `1ed32fe4…`, `5d3dd78d…`, `13b34b28…`, `1d4b515b…`, `ec7c5732…`, `aa2b9ccf…`, `aa2b9ccf` itself | 9/9 ancestor | pass |
| lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state souji-shokunin`; `git -C souji-shokunin status --porcelain` | `branch=master local=aa2b9ccf remote=aa2b9ccf ahead=0 behind=0 head=detached tracked=0 untracked=0`; empty | pass |
| prompt carries template contract | read `.ufo/prompts/souji-round-85.md` | §1 MISSION/AXES binding, §2 1–3 claims + lowest axis + separability, §2b frontier + frozen census, §3 L2 floor, §4 report contract + SHONEN, §5 commit/push scope + L0, §6 hyaku addendum (run 15: 8–16 seats, ≥25 % attack, ≤2 connectors) | pass |
| marker vs report | report names 10 round commits, per-claim before→after tables with commands, receipts, trends, SHONEN | real report | pass |
| L2 floor and attack share | `.ufo/waves/round-85/w1-spec.json`, `w1-results.json` (committed at `aa2b9ccf`) | 12 seats (band 8–16), executor×3 scribe scout×2 connector reviewer critic mutation-tester×2 sentinel; attack 5/12 = 42 % ≥ 25 %; connectors 1 ≤ 2; 12/12 substantive outputs | pass |
| prereg F is alone | `git show --name-only 43c630eb…` | `census/round-85/preregistration.txt` only | pass |
| pre-file falsification | `python3 scripts/hyaku/prefile-falsification.py --lane souji --round 85` | `PREFILE-FALSIFICATION: pass claims=2 rows=14 attack_seats=6 findings=0`, exit 0 | pass |

Status-neutral defects (named, not status predicates):

- **D1 — report's registry-count line contradicts the committed bytes (259→260 vs 259→263).** The report says
  "Registry `259 → 260`" (twice: Work-performed bullet and Sources & frontier) and "one new registry row (S337)"
  in expansion, but `git show 705fa138:corpus/SOURCES.md | grep -cE` = 259 and `grep -cE '^\| *S[0-9]{3,}'`
  at `aa2b9ccf` = 263: the round added **four** rows in two commits — S337 (`5d3dd78d`, via commit `5d3dd78d`
  "…sources…"), then S338 (rejected) + S339 + S340 (`2bd0149c`). The lesson `## Gate` states "Registry
  `259 → 263`: four rows added, one rejected, zero removed" correctly; the report's claim is the stale one.
  The discrepancy is a conformance defect in the report line only: the frontier section's counting command and
  census receipts resolve, no row is missing, and the expansion verdict (`unchanged`, ground already covered)
  matches either count. Fix next round: the report's registry line must be re-derived from the same grep at
  file time (A5-class evidence binding; see §5 routed defects).
- **D2 — wave seat report files are not tracked (gitignored).** `.gitignore:1:.ufo/waves/` ignores the whole
  directory; `aa2b9ccf` force-adds only `claims.json`, `claim-falsification.tsv`, `w1-results.json`,
  `w1.ready`, `build-spec.py`, `w1-spec.json`, `w1-dispatch.json`, `w1-plan.err`. The 12 seat report files
  (`.ufo/waves/round-85/w1/S85*.md`) are on disk but **untracked** (`git ls-files` shows no `w1/S85*` path;
  `git status --porcelain` is empty only because the ignore hides them). The ledger cites them by path
  (`w1/S85ExecC1.md` etc.) as its evidence. Every verdict I re-checked resolves on disk at closure, so this is
  a durability gap, not an admission bar — the same class as r84 D4, now systematic across the wave. Routed f
  or r86: force-add seat reports (or a per-round exception) so the ledger's citations are durable.
- **D3 — inherited record-agreement disagreement, resolved this round.** The report names the pre-existing K3
  mismatch (`corpus/README.md:1017 3 refused != receipt 0 refused`) present at the base commit; my C2
  regression run reproduces it (see §2). It is routed to r86 as a record-agreement row, not this round's scope.

## 2. Claims

Both claims rest on lane-owned instruments. Per PROTOCOL §Gate standard (Closure consequence) I executed no
sibling gate: **re-measured** means I ran the committed counter bytes myself from the lane root against a
scratch dir under `/fast/scratch/hyaku/closure-souji-r85/` (the instruments refuse `/tmp`); **evidence-
verified** means I re-read committed receipts and re-hashed the bytes they bind. Both claims are re-measured,
both ends.

### C1 — calibration (lowest owned non-retired axis, 7): **verified** (re-measured, both ends)

```
python3 -B census/round-85/c1-clause-battery.py --counter census/round-85/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/closure-souji-r85/c1r85 --only r85 --expect-killed 6
python3 -B census/round-85/c1-clause-battery.py --counter census/round-85/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/closure-souji-r85/c1r84 --only r84 --expect-killed 5
```
Observed (my runs, 150 s total): after — `ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0`,
`m11-class-enum killed=yes mismatches=1 errors=0`, `SUMMARY mutants=6 sets=r85 pristine_r85=ok killed_r85=6`,
`EXIT=0`; before — `ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0`,
`m11-class-enum killed=no mismatches=0 errors=0 exit=0`, `SUMMARY … killed_r84=5`, `EXIT=0` — both match the
filed receipts `census/round-85/records/c1-after.txt` and `census/round-85/controls/c1-before-r84-population.txt`
byte for byte. Pins re-derived: counter `91b4ffde…` (552 lines), harness `d49aeb32…`, mutants `bb788c0e…`,
r85 population `1468236c…` (47 rows = 48 lines incl. header comment; 44 r84 rows byte-for-byte prefix,
`diff` empty), r84 population `4795f009…` (44), `c1-items.tsv` `d9a2ad8c…` (3 items). The 47-row population
adds NF-R + TF11 + NF-S (unknown ledger class, `NF-S … BOGUS … REFUSED` at `c1-false-rows.tsv:48`); the
kill of `m11-class-enum` comes from NF-S's genuine mismatch (`errors=0`), so no kill came from an error —
r84 D2 is answered (the battery now prints `mismatches` and `errors` separately per mutant; all six kills have
`errors=0`, and the pristine arms are 0/0).

Shadow probe (A1, a finding not a claim, evidence-verified): `census/round-85/records/a1-c7-shadow.txt` —
`ARM pristine pop=r84 rows=44`, `ARM pristine pop=r85 rows=47`, `MUTANT c7-census-in-tree-drop killed=no`
on both, `SUMMARY … killed_r84=0 killed_r85=0`. Read with S85Scribe's reachability evidence (`.ufo/waves/
round-85/w1/S85Scribe.md` F1), the verdict "reachable and unbound" (not shadowed) is the correct reading and
the round withdrew its own first sentence (A1). Killed-count honesty: the claim certifies six kills on the
47-row population, not the whole rule (A4: five more guards unbound, S85MutCounter; A7: instrument notes stay
byte-stable).

### C2 — operability (8): **verified** (re-measured, both ends)

Filed tool `tools/souji-record-agreement.py` sha256 `0ade0751…` — matches `census/round-85/records/c2-after.txt`
header. The base control `census/round-85/controls/c2-K-a-base-tool.py` `ec5b809d…` is byte-identical to the
pre-round blob (the K4 diff is confined to `truth_refusal` + one `K4 . stat-cache-concealed` row at lines
171–424; the control's `grep` shows no `truth_refusal`).

```
python3 -B census/round-85/c2-k4-counter.py --tool tools/souji-record-agreement.py \
  --work /fast/scratch/hyaku/closure-souji-r85/c2after
python3 -B census/round-85/c2-k4-counter.py --tool census/round-85/controls/c2-K-a-base-tool.py \
  --work /fast/scratch/hyaku/closure-souji-r85/c2before
```
Observed (my runs): after — `SUMMARY rows=7 mismatches=0 errors=0`, KF1/KF2/KF3 `k4=1 named=yes`, honest rows
KH1/KH2/KU1/KU2 unchanged, `EXIT=0`; before — `SUMMARY rows=7 mismatches=3 errors=0`, KF1/KF2/KF3 `k4=0
match=no`, `EXIT=1` — matching `c2-after.txt` / `c2-before-base-tool.txt`. Counter `0a7b801d…` matches both
receipt headers. The two Sentinel HIGH escapes (realpath + `-I`, pinned status config) are closed by
`ec7c5732` (re-stamped `c2-after.txt` header + `plans/round-85.md` A6). Limits stated, not claimed: the
gitlink/flag-sweep escape (A2, S85ExecK4) and the five-path naming cap (F7) remain.

Real-lane regression: `tools/souji-record-agreement.py --root . --rev 43c630eb` runs; the only K3/K4 finding
is the inherited `corpus/README.md:1017 3 refused != receipt 0 refused` (report names it; pre-existing at base).

### SCORECARD and axes

`git diff 705fa138 aa2b9ccf -- SCORECARD.md` appends only (Round 85 measurements table + two capability rows
+ planned r86); no axis score changed (calibration 7, coverage 8, operability 8 — no reproducible 0–10 mapping,
verdict + counting command instead of a number, which the lane states rather than fabricates).
`git diff 705fa138 aa2b9ccf -- PROVINCE.md` empty (0 lines).

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1 re-measured: r85 47-row population `mismatches=0` pristine green and `killed_r85=6` while the same battery on the r84 44-row population leaves `m11-class-enum` alive (`killed_r84=5`, same counter `91b4ffde…`, same battery, same mutants). The instrument now discriminates the class-enum guard it previously passed. |
| operability | improved | C2 re-measured: filed bytes `0ade0751…` refuse the three stat-cache forgeries (`mismatches=0`, KF1–KF3 `k4=1 named=yes`) that the base blob `ec5b809d…` misses (`mismatches=3`, `k4=0 match=no`); honest rows unchanged on both. |
| coverage | unchanged | no coverage claim; `PROVINCE.md` unchanged; four SOURCES rows appended but no new surface class entered the corpus — the round's gain is instrument power and one tool path, not breadth. |

The other three axes carry no claim and show no harm: `depth` gains Q156/Q157 plus two r85 knowledge sections;
`freshness` is exercised (r83 36-row regression green in `census/round-85/records/c1-regress-r83.txt`);
`adjacency` unchanged (A2's gitlink escape is routed inside the lane, nothing absorbed).

### Pre-file falsification ledger (addendum §8, Amendment 59)

`python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 85` →
`PREFILE-FALSIFICATION: pass claims=2 rows=14 attack_seats=6 findings=0`, exit 0. I read the ledger
(`.ufo/waves/round-85/claim-falsification.tsv`) by hand against the lane's rule: 14 rows over both claims
and all six attack seats (S85ExecC1, S85ExecEvade, S85ExecK4, S85Reviewer, S85Critic, S85MutCounter,
S85MutK4, S85Sentinel — the attack-role set), and all five `falsifies-wording` rows (S85ExecEvade,
S85Scribe, S85Sentinel on C1; S85ExecK4, S85Sentinel on C2) name `plans/round-85.md` as the narrowing, each
tied to an amendment A1/A2/A4/A5/A6/A7 (C1: census-in-tree deciding not shadowed, reachable/unbound F1/F4,
LOCAL-POLICY/FLEET/ABSENT unbound; C2: gitlink escape, Sentinel HIGH escapes). Each naming amendment exists
(`grep -c '^## A' plans/round-85.md` = 9: A0, A1, A2, A3, A0.4, A4, A5, A6, A7). No failing row exists; no
row is real-and-unreconciled — every narrowing is a stated limit or an in-round correction (A6 both escapes
repaired in `ec7c5732`, A5 both receipts re-filed on committed bytes in `1d4b515b`/`1ff0eb58`). The r84
`claims-missing` SETUP defect is fixed: `claims.json` is committed at `aa2b9ccf` (2 claims, Wording/instrument/
counter/target each).

## 3. Discernment spot-check

`corpus/lessons/round-85.md` `## Gate` logs five decisions: three admits (S337, S339, S340) and two rejects
(S336 carried unchanged? no — S338 rejected; plus S336 is the prior round's row, not this round's), with S315/
S316/S317/S335 re-opened unchanged. Sampling ≥1 admit and ≥1 reject, I re-opened four items by their recorded
sources; S337's quote check passed after decoding the HTML (raw grep of the capture misses it because
`<strong>` tags interrupt the phrase).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S337 — PIT (pitest.org), tool's own documentation | admit (`docs`, tier B, `mined`) | capture `census/round-85/srcs/pitest-org.html`: sha256 `b0c7e050…` matches, 12023 bytes; the exact quoted text sits at lines 137–138 ("…mutation testing is the **gold standard** against which all other types of coverage are measured.", tags stripped; the lesson names the "Mutation testing" section, and the page's `What` section carries it verbatim) | agree | quote is verbatim (14 words, ≤25), located, and grounds exactly the C1 criterion (a suite judged by kills — confirmed by S340's abstract). The "paragraph on statement coverage" anchor is imprecise (the sentence lives in the `What` section, not the statement-coverage paragraph) — named as a minor anchoring slip, not worth disputing the admit; S340 carries the criterion more sharply than S337 does, and the lesson says so. |
| S339 — gitformat-index(5) as installed (git 2.56.0-1) | admit (`docs`, tier A, `mined`) | capture `.ufo/waves/round-85/w1/S85ScoutSources/gitformat-index.5.gz` → `zgrep -n` line 172: "Hash checksum over the content of the index file before this checksum." (12 words; trace in `…/quote-receipt.txt` Q2) | agree | quote is verbatim and located (roff line 172); it grounds exactly the C2 fixture's must-re-checksum claim (a forged entry is a whole-file rewrite). Scope split vs S317 (per-entry stat fields) is stated and honest. |
| S338 — git-status(1) as installed (git 2.56.0-1) | reject (row kept: `REJECTED: …; flip: …`) | capture `.ufo/waves/round-85/w1/S85ScoutSources/git-status.1.gz` → `zgrep -c` the DESCRIPTION sentence "paths that have differences between the working tree and the index file" at roff line 40 | agree | quote is verbatim (12 words) and located; the rejection is correct because the sentence restates S317 (index stat data) + S315 (racy-git stat shortcut) already held for this lane — the flip (a scoped teaching the rows do not carry: porcelain format contract or background-refresh behaviour) is grounded in what the page actually contains. Right call; wrong-cell (E09 `recheck`) corrected in-round (M5). |
| S340 — "Practical Mutation Testing at Scale", arXiv:2102.11378 | admit (`paper`, tier B, `mined`) | capture `.ufo/waves/round-85/w1/S85ScoutSources/arxiv-2102.11378-abs.html` → `grep -c "Mutation analysis assesses a test suite"` = 4 (abs+fulltext copies) | agree | abstract quote is verbatim (22 words, ≤25), located (byte offset 2386), and is the paper-backed form of S337's vendor sentence — the quote the C1 criterion actually needs. |
| newly written `corpus/SOURCES.md` row — S337's quote cell | ≤25-word located quote | as above (capture lines 137–138; quoted text "mutation testing is the gold standard against which all other types of coverage are measured", 14 words) | agree | the cell quotes the page, names the section, and the capture hash resolves. |

Sources census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 87 pre-existing `W04` cross-scope
duplicate-URL lines, `EXIT=0` (matches `census/round-85/records/sources-census-after.txt` exactly). Rows
`259 → 263` (`grep -cE '^\| *S[0-9]{3,}' corpus/SOURCES.md` = 263; base = 259).

The report's `259 → 260` line (D1 above) is reconciled by the above: the shipped delta is S337+S338+S339+S340.
My spot-check verdicts agree with the lesson's `## Gate` on all four rows; the report's undercount does not
make the registry wrong — the review agrees with the recorded Gate decisions rather than the report's count
sentence.

## 4. Trend verdicts

- **expansion: unchanged** — I agree. Four rows are appended (three admits, one reject) and two knowledge
  sections land on ground the coverage map already holds; `PROVINCE.md` unchanged and no `## Frontier` row
  promoted to Core. The round's gain is instrument power and one tool path, not breadth, and the report says
  exactly that (subject to D1's count).
- **quality: improved** — I agree. The population that certifies the pointer counter now kills the class-enum
  mutant it left green (`killed_r84=5 → killed_r85=6`, both pristine arms green — re-measured by me), and the
  lane's audit tool no longer certifies a tree it has not measured (three stat-cache forgeries missed →
  refused, honest rows unchanged on both arms). Two clauses of the C2 repair are unrowed (A2 gitlink escape,
  five-path cap) and are stated as limits, not claimed.
- **discernment: improved** — I agree. The wave falsified the round's own framing before filing — the census-
  in-tree clause first read as shadowed, withdrawn as reachable and unbound (A1; S85Scribe F1/F4); the basename
  clause first read as bound on a mutant that crashed (Q133), corrected on the second run; the C1 target
  retargeted before F (A0.3); the C2 counter caught dying on an over-refusal (A0.4/M2); a gitlink concealment
  named (A2) and two receipts naming unobtainable bytes re-filed on committed bytes (A5) — and the round
  withdrew or corrected each time rather than defending them. A5/Q156/Q157 were added so the next round tests
  reachability and status-trust before naming a clause. All three (four) Gate decisions I re-opened agree,
  including one rejection.

## 5. Routed defects (lane must fix next round)

- **R86-1 (D1).** The report's Sources & frontier / expansion lines state registry `259 → 260` / "one new
  registry row (S337)" while the committed delta is 259 → 263 (S337+S338+S339+S340). Re-derive the count line
  from the same `grep -cE` at file time; a number carried from a draft census is a conformance defect (CORPUS.md
  "a count carries its command", applied to reports). The lesson's number is correct; the report's is not.
- **R86-2 (D2).** Wave seat reports (`.ufo/waves/round-85/w1/S85*.md`) are gitignored and untracked; the
  falsification ledger cites them as evidence without durability. Force-add seat reports (or a per-round
  exception) in the wave commit.
- **R86-3 (A1/A4 carried).** The r84 routed item "ground it or delete it" answered "ground it": NF-W and the
  48-row population are routed to r86; NF-L3, the token-on-line row (pristine-red by construction), and the
  five unbound guards (m12/m14/m16/m17 + dead m15) are carried. Nothing was deleted this round.
- **R86-4 (A2/A3/F7 carried).** The gitlink/flag-sweep escape, stage-0/intent-to-add rows, the five-path
  naming cap, the inherited K3 disagreement, and the r83/r84 C2 carried list (pid-reuse, parent-before-child,
  termign-fork/p5-late-term, strace settle) remain.

## 6. Verdict

`CLOSURE souji r85 status=ok admitted=true` — every claim verifies, no axis harmed, the ledger passes, the
gate spot-check agrees with the lesson, the census is green. Defects D1–D3 are status-neutral and routed in §5.
Promotion is operator-owned; the SHONEN boxes remain `[~]` (lane-asserted, verifier pending) and this spot-check
does not check them — noted for the operator: on the evidence above the boxes look checkable by a non-author.
