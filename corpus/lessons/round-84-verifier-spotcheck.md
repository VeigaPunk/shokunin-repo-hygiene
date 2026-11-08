# souji round 84 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane round 84, base `54709d0db92d9dcd95504a34173c1f6a3fd88ec1`, after
`a8e88b9c53e111ce6e9d09de50d1515d6032587a` (branch `master`, `local=remote`, `ahead=0`, `head=detached`,
`tracked=0 untracked=0`). Report `.ufo/reports/round-84/souji.md` (fleet repo commit `04a40609` by
`souji-shokunin`, after lane tip). Driver digest (`.ufo/watchdog.log`, mutable — pointer at closure):
`2026-11-08T03:01:34-03:00 launch souji round=84 pgid=1918461 driver=hyaku-inline attempt=1`;
`2026-11-08T04:26:13-03:00 complete souji round=84; hyaku-inline attempt=1`.

Outcome: status `ok`, **admitted**. C1 and C2 both verify — I re-measured both before→after arms myself on the
committed bytes (commands and outputs below). No owned axis is harmed. One SETUP defect in the pre-file ledger
gate is named (status-neutral: the wave artifacts themselves were read and adjudicated by hand). The
`falsifies-wording` rows all name amendments A1–A10 in `plans/round-84.md`; two non-author seats (S84Reviewer,
S84ExecC1) independently reproduced the filed numbers, and my probe confirms the over-specification rows are
real rather than defensive.

## 1. Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-84/souji.md` | `souji-shokunin 04a40609…` | pass |
| `## SHONEN` heading, one line per box | `grep -A5 '^## SHONEN' <report>` | 1 heading, 4 lines all `[~]` with resolvable pointers | pass |
| cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <h> master` over `bd2bbb12…`, `35d87842…`, `1f49b3a7…`, `4557fc71…`, `56a95d62…`, `a8e88b9c…` | 6/6 ancestor | pass |
| lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `branch=master local=a8e88b9c remote=a8e88b9c ahead=0 behind=0 head=detached tracked=0 untracked=0`; empty | pass |
| prompt carries template contract | read `.ufo/prompts/souji-round-84.md` | §1 MISSION/AXES binding, §2 1–3 claims + lowest axis + separability, §2b frontier + frozen census, §3 L2 floor, §4 report contract + SHONEN, §5 commit/push scope, §6 hyaku addendum (run 15: 8–16 seats, ≥25 % attack, ≤2 connectors) | pass |
| marker vs report | report names 6 round commits, receipts + before→after tables | real report | pass |
| L2 floor and attack share | `.ufo/waves/round-84/w1-spec.json`, `w1-results.json` | 12 seats (band 8–16), executor×3 scribe scout×2 connector reviewer critic mutation-tester×2 sentinel; attack 5/12 = 42 % ≥ 25 %; connectors 1 ≤ 2; 12/12 substantive | pass |
| prereg F is alone | `git show --name-only 35d87842…` | `census/round-84/preregistration.txt` only | pass |

Status-neutral defects (named, not status predicates):

- **D1 — pre-file ledger gate returns SETUP, not the ledger verdict.** `python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 84` exits 2 with `FINDING claims-missing …/.ufo/waves/round-84/claims.json` (`PREFILE-FALSIFICATION: SETUP findings=1`). No `claims.json` exists anywhere under `.ufo/waves/round-84/`; the lane instead kept the ledger `.ufo/waves/round-84/claim-falsification.tsv` (13 rows over C1/C2, every `falsifies-wording` row naming `plans/round-84.md` A1–A10) and `census/round-84/preregistration.txt` as the frozen claims. I read the ledger by hand against the lane's own rule (every claim covered, every attack-role seat's artifact read, every falsifying row naming a narrowing) and adjudicated each row against `plans/round-84.md` A0–A10 myself — the ledger satisfies the addendum §8 substance; only the machine gate's input surface (`claims.json`) is absent. That absence is a conformance defect in the round's form, not a false claim.
- **D2 — kill rule cannot distinguish row mismatch from harness error.** Battery line 118: `killed = rc != 0 or mism > 0 or errs > 0`; a harness error (rc≠0) with `mism=0` counts as killed. Observed: no kill in the 5/5 was an error (every mutant `errors=0`, each with a real `match=no` row — see §2), so the ambiguity is not load-bearing this round, and S84Reviewer recorded the same point (F6). Disclose it in the harness header if the battery is reused.
- **D3 — wave substrate note.** S84ExecEvade and S84MutTool scored `RefC2` bytes `a810acaf…` (a mid-write copy carrying the M2 `|| continue` defect); the filed bytes `030fa10d…` were re-scored by the L1 (22/0/0/0) and re-mutated (A5, lesson M5). The ledger names which bytes each finding attacked — reconciled, not unreconciled.
- **D4 — S84Critic report file stayed a skeleton.** Its findings live in its final output (`agent://S84Critic`) and the ledger (A8/A9); the file is tracked. The ledger cites the transcript, not the file — a durability gap, named.

## 2. Claims

Both claims rest on lane-owned instruments. Per PROTOCOL §Gate standard (Closure consequence) I executed no
sibling gate: **re-measured** means I ran the committed counter bytes myself from the lane root against a
scratch dir under `census/round-84/closure-tmp` (the instruments refuse `/tmp`); **evidence-verified** means I
re-read committed receipts and re-hashed the bytes they bind.

### C1 — calibration (lowest owned non-retired axis, 7): **verified** (re-measured, both ends, plus a mutant)

```
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
  --work census/round-84/closure-tmp --only r84 --expect-killed 5
```
Observed (my run, 65 s): `ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0`; `m6 killed=yes mismatches=1 errors=0`, `m7 killed=yes mismatches=1 errors=0`, `m8 killed=yes mismatches=2 errors=0`, `m9 killed=yes mismatches=4 errors=0`, `m10 killed=yes mismatches=0 errors=40 exit=1`; `SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5`, `EXIT=0` — matches the filed receipt `census/round-84/records/c1-after.txt` (`m10 mismatches=1 errors=0`).

Before, same battery on the r83 population:
```
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
  --work census/round-84/closure-tmp --only r83
```
Observed (my run, 93 s): `ARM pristine pop=r83 rows=36 mismatches=0 errors=0 exit=0`; all five `MUTANT … killed=no mismatches=0 errors=0 exit=0`; `SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0`, `EXIT=0` — byte-identical to `census/round-84/controls/c1-before-r83-population.txt`. Pins re-derived: counter `052c4f3f…`, harness `51b30dbd…`, mutants `b71cf3d8…`, r84 population `4795f009…` (44), r83 `c9a6d58c…` (36); `git diff bd2bbb12..a8e88b9c -- <instruments>` empty (frozen).

Kill attribution (via S84Reviewer §3, corroborated by `census/round-84/records/c1-m9-rows.txt`): m6↔NF-L, m7↔NF-L2, m8↔TF9+TF10, m9↔TF8+TF9+TF10+NF-P (`refused_true=3 accepted=1`), m10↔NF-M — every kill a genuine row mismatch, none a harness error.

Mutation probe of the round's own wording (the ledger's A8 row: "the 44 rows are not minimal"): the 40-row subset (36 old + NF-L, NF-L2, NF-M, TF9) already kills 5/5, so NF-Q and three others are non-minimal. It is **reconciled**, not unreconciled: the filed claim certifies five named clauses on the 44-row population, not minimality of the population, and `plans/round-84.md` A10 carries the over-specification as a stated limit.

### C2 — operability (8): **verified** (evidence-verified on filed bytes; both arms re-read, not re-executed)

Filed tool `tools/souji-vault-verify.sh` sha256 `030fa10d…ef41d` — matches `census/round-84/records/c2-after.txt` header. Re-read of both receipts:

- After (`c2-after.txt`): `SUMMARY rows=22 mismatches=0 errors=0 orphans=0`, `C2-AFTER-EXIT=0`; l1/l2 `survivors=0 secs=0.7/0.6`, 20 other rows all `match=yes`.
- Before (`c2-before-r83-tool.txt`, control `72a405f2…`): `SUMMARY rows=22 mismatches=2 errors=0 orphans=2`, `C2-BEFORE-EXIT=1`; l1/l2 `survivors=1 match=no`.
- Clause mutants on filed bytes (`c2-mutants-on-filed.txt`): STOP→TERM killed (1 mismatch), no-KILL-sweep killed (2), single-pass survives (22/22), first-line re-check survives (22/22) — the last two are the unrowed belts A1/A2, stated as limits, not measured clauses.

Regressions evidence-verified (not executed — the lane's gate): selftest 57 checks 0 failed (`c2-regress-selftest.txt`), r17 `total=37 failed=0 skipped=0` (`c2-regress-r17.txt`), probe D `arms=4 failed=0`. The `cli_kill_tree` freeze-before-signal shape (SIGSTOP map pass + second pass + SIGKILL sweep with starttime re-check, every stat read whole-file) is in the filed bytes at `030fa10d`.

### SCORECARD and axes

`git diff 54709d0d a8e88b9c -- SCORECARD.md` appends only (Round 84 measurements table + capability rows + planned r85); no axis score changed (calibration 7, coverage 8, operability 8 — no reproducible 0–10 mapping, verdict + counting command instead of a number). `git diff --quiet 54709d0d a8e88b9c -- PROVINCE.md` true. The C2 diff is confined to `cli_kill_tree` in `tools/souji-vault-verify.sh`.

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1 re-measured: r84 44-row population `mismatches=0` pristine green and `killed_r84=5` while the r83 36-row population leaves 0/5 (same counter `052c4f3f…`, same battery, same mutants). The instrument now discriminates the five clauses it certifies; it is not minimal (A8) and does not certify the whole rule (A10) — both stated. |
| operability | improved | C2 evidence-verified: filed bytes `030fa10d…` give 22/0/0/0 with l1/l2 `survivors=0`; the r83 bytes `72a405f2…` give 2/2 orphans on exactly l1/l2. The freeze (STOP before any trappable signal) and the KILL sweep are the measured clauses; the second map pass and the whole-file re-check are unrowed belts (A1/A2), stated as limits. |
| coverage | unchanged | no coverage claim; `PROVINCE.md` unchanged; three SOURCES rows appended but no new surface class entered the corpus — the round's gain is instrument power and one tool path, not breadth. |

The other three axes carry no claim and show no harm: `depth` gains `corpus/knowledge/own-tree-pointer-binding.md` r84 section and `corpus/knowledge/gate-signal-handling.md` r84 section; `freshness` is exercised (r83 36-row regression green on the filed counter); `adjacency` is unchanged (connector records sibling overlap, nothing absorbed).

## 3. Discernment spot-check

`corpus/lessons/round-84.md` `## Gate` logs three decisions: two admits (S334, S335) and one reject (S336).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S334 — `signal(7)` as installed (man-pages 6.19-1) | admit (`docs`, tier A, `mined`) | `/usr/share/man/man7/signal.7.gz` → `zcat | sed -n '405,408p'`: "The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored." (quote "SIGSTOP ... cannot be caught, blocked, or ignored.", 6 words, located at decompressed lines 406-407); capture `census/round-84/srcs/signal.7.gz-man-pages` sha256 `177f2734…e3b4b` matches the lesson's hash | agree | quote is verbatim, located, ≤25 words; it grounds exactly the C2 mechanism (a STOPPED pid cannot trap or fork) and the entry states it says nothing about `/proc` reads or pid reuse — the scope split is honest, not the duplicate-of-an-existing-ground failure |
| S336 — arXiv 1808.04849, attempted mutation-testing survey | reject (row exists as `rejected` with reason + flip) | `curl -sL https://arxiv.org/abs/1808.04849` → HTTP 200, 44223 bytes; abstract: "Objective: To (1) demonstrate the implementation of a data science platform built on open-source technology within a large, academic healthcare system…" — title "A Scalable Data Science Platform for Healthcare and Precision Medicine Research" | agree | the id is not the mutation-testing survey it was fetched for; carries no mutation-testing proposition, so it cannot ground the C1 principle (which rests on S335). The flip (a retrievable abstract stating the needed proposition) is grounded in what the page actually contains. Correct rejection of a wrong-id fetch. |
| S335 — the lane's own clause-kill receipts | admit (`own-work`, tier A, `mined`) | `census/round-84/records/c1-after.txt` → "SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5" verbatim; `census/round-84/controls/c1-before-r83-population.txt` → "SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0" | agree | the quote is the receipt's own line; a receipt is the only row that speaks to the C1 instrument, and the entry states it proves discrimination on its own rows only — not a rule. Legitimate `own-work` tier-A row. |
| newly written `corpus/SOURCES.md` row — S334's quote cell | ≤25-word located quote | as above (decompressed lines 406-407; quoted text 6 words, 22 with "The signals … and" paraphrase — within the 25-word bound as cited) | agree | the cell quotes the page, names the line range and the capture path; resolves. |

Sources census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, 87 pre-existing `W04` cross-scope
duplicate-URL lines, `EXIT=0`. Rows `256 → 259` (`grep -cE '^\| *S[0-9]{3,}' corpus/SOURCES.md` = 259; the diff
adds exactly S334–S336, 0 removed).

## 4. Trend verdicts

- **expansion: unchanged** — I agree. The registry gains three rows (one rejected) and the knowledge base two
  sections on ground the coverage map already holds; `PROVINCE.md` unchanged and no `## Frontier` row advanced.
  The round's gain is instrument power and one tool path, not breadth, and the report says exactly that.
- **quality: improved** — I agree. The population that certifies the pointer counter now kills five clause-blind
  mutants it previously passed (0/5 → 5/5, both pristine arms green — re-measured by me); the vault tool's
  signal path leaves no survivor on the two late-fork rows the r83 bytes left one each, inside the same settle,
  with selftest 57/0, r17 37/0/0 and probe D 4/0 on the filed bytes (evidence-verified). Two clauses of the
  repair are unrowed and are stated as such (A1/A2) rather than claimed.
- **discernment: improved** — I agree. The wave falsified parts of the round's own wording before filing (A1 the
  second map pass, A2 the whole-file re-check, A5 the substrate of two seats' findings, A7 NF-Q's missing kill,
  A8 the non-minimal population, A9 the claim's subject at F, A10 the two unbound clauses), the ledger carries
  13 rows over 2 claims and every attack seat, and the round's do-nothing arms (36-row population, r83 tool
  bytes) are committed receipts rather than assertions. The sentinel's census-in-census finding — a wrong-file
  resolution both populations certified green — is the round's most valuable result, and it is filed as a
  narrowing (A10), not smoothed over. The three Gate decisions I re-opened all agree.

## 5. Routed defects (lane fixes next round)

1. **D1 — `claims.json` surface.** The pre-file falsification gate expects `.ufo/waves/round-84/claims.json`
   (frozen claims keyed C1..C9) and returns SETUP without it. Freeze that file next round (or record its
   absence and the ledger-by-hand check in the prereg), so the gate can pass mechanically.
2. **D2 — killed-by-error ambiguity.** The battery's kill rule (`rc≠0` OR mismatch OR error) cannot tell a
   row mismatch from a harness error. This round it did not bite (every kill `errors=0`), but the battery
   should record per-mutant `errors` separately from `mismatches` in the kill verdict, or a harness crash reads
   as a kill.
3. **C1 (carried, the lane's own r85 list):** `NF-L3` (first below-round component not a wave dir), a
   `census/round-<N>/`-token row to bind the census-in-census clause the sentinel showed unbound (A10) or
   delete the dead census-in-tree branch, a last-component row (`…/erratum-evidence-RENAMED.txt`), rows for the
   token-on-line / unknown-class refusals (S84MutCounter survivors).
4. **C2 (carried, the lane's own r85 list):** a row exercising the second map pass (a child forked in the
   read→STOP window), a comm-with-newline row for the whole-file re-check (r83 D5), a pid-reuse row, a
   parent-before-child row, `termign-fork`/`p5-late-term`, a `strace`-robust settle.
5. **Wave discipline (carried):** the reference implementation must not be edited while seats are scoring it; a
   reference copy belongs in a seat-owned path with a frozen hash (M5/A5).

SHONEN: all four boxes stay `[~]` with resolvable pointers (SKILL gate registry rows, `corpus/SOURCES.md`
S334/S335, `corpus/lessons/round-84.md` `## Gate`, LOG.md r84 entry, `git diff … -- PROVINCE.md` empty).
Boxes 1–4 look checkable by a non-author from those pointers; promotion is operator-owned and I write no `[x]`.
