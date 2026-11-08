# Round 84 — the false-row population binds five counter clauses (C1 calibration), the vault CLI's signal path freezes the tree before terminating it (C2 operability)

Attempt 1 (`SoujiR84`). Lane base `54709d0db92d9dcd95504a34173c1f6a3fd88ec1` (r83 closed `admitted`; spot-check
`corpus/lessons/round-83-verifier-spotcheck.md`). Frozen claims, instruments and predicates are in
`census/round-84/preregistration.txt`; the wave's amendments are in `plans/round-84.md` (A0-A6) and the pre-file
ledger in `.ufo/waves/round-84/claim-falsification.tsv`.

Staged commits: P `bd2bbb1279dcac9089dc0d4668cba48d88fd444d` (instruments, populations, mutant set, controls, before
receipts, QUALITY heading restore), F `35d87842efd966bfc326eff92fb534ab3e56b79e` (preregistration ALONE), then the
C2 repair + receipts `1f49b3a7824e7f4e65c33358ee24a6afaf8ca50d` and the integration commits that follow.

## Inherited

The r83 spot-check closed round 83 `ok`, **admitted**, with seven routed defects. Answered this round: **D2** (the
`## Round 23 criteria` heading deleted at `802a41e7` — restored in P, the deletion named in LOG), **D3** (the
`b0a5b662…`/`72a405f2…` digest binding — an appended `superseded by` correction in the r84 LOG entry), **D4** (the
"9 seats delivered, 3 skeletons" sentence — corrected in the r84 LOG entry: 12 substantive outputs), **D5** (the
whole-file stat read is now used in every re-check of `cli_kill_tree`, not only the map pass — but see Mistakes M4:
no row exercises it), **D6** (wave seat reports are force-added with the round). D1 (the stale `252 → 255` SOURCES
count) is corrected in the r84 LOG entry as `252 → 256` (256 at r83 tip; 258 after this round's S334/S335).
Not answered: none.

The r83 lesson's r84 list, item by item: the deep-token pair → **TF8/NF-P**; `a2w1/`/`assimilation/` true rows →
**TF9/TF10**; `NF-L`/`NF-L2`/`NF-M` → rows of those ids; `NF-L3` (a token whose first below-round component is not a
wave dir) → **routed** (it needs a new population item, not a row); "ground or delete the census-in-tree branch" →
**routed** (S84Connector F-04: still zero rows; a `census/round-<N>/` token item is needed). The r83 C2 list's
pid-reuse row, parent-before-child row, `termign-fork`/`p5-late-term` rows and a `strace`-robust settle → **routed**
(this round built the late-fork class instead, which is what the r83 evidence pointed at). The carried r81 list
(`_regular` pathspec framing, quarantine intro-blob digest row, fork-tail row, r79 gate re-measurement, check-4 300 s
backstop, r76 K03/K04, status-trusting lane tools, r17 240 s runners) → carried unchanged.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=54709d0d ahead=0 tracked=0 untracked=0`).
`considerthese/` does not exist in this lane; no shokuknow theme taken (`Assimilation: none`).

**Planner seat.** The L1 holds it (`scripts/hyaku/ufo-wave-policy.json` `lanes[]` has no `planner` id); the wave's
planning data-walk rode the connector and the two scouts.

## Gate

Sources opened this round (each opened by fetching/reading it here; ids continue the registry after S333):

- **S334 — `signal(7)` as installed** (man-pages 6.19-1, `/usr/share/man/man7/signal.7.gz`, sha256
  `177f2734…e3b4b`, capture `census/round-84/srcs/signal.7.gz-man-pages`; opened 2026-11-08). Quote, decompressed
  lines 406-407: "SIGSTOP ... cannot be caught, blocked, or ignored." **ADMIT**, `docs`, tier A. It grounds exactly
  the C2 repair's mechanism (a stopped process cannot run a trap); it says nothing about `/proc` reads, pid reuse or
  the tool's walk, and the entry says so. Duplicate-URL check: no other row cites `signal.7`; S075 is
  `proc_pid_stat(5)`, S325 the bash trap node, S326 `timeout.c`, S328 `setsid(1)`.
- **S335 — the lane's own clause-kill receipts** (`census/round-84/records/c1-after.txt`,
  `census/round-84/controls/c1-before-r83-population.txt`; opened 2026-11-08). Quote, the r84 arm's own line:
  "SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5". **ADMIT**, `own-work`, tier A, `mined`.
  It is the only row that speaks to the C1 claim's instrument; it is a receipt, not a rule, and the entry says the
  population proves discrimination on its own rows only.
- **S336 — arXiv 1808.04849, attempted mutation-testing survey** (`https://arxiv.org/abs/1808.04849`, HTTP 200,
  44223 bytes, sha256 `447a1248…971d`; opened 2026-11-08). Quote, the abstract: "To (1) demonstrate the
  implementation of a data science platform built on open-source technology within a large, academic healthcare
  system". **REJECTED**: the id is not the mutation-testing survey it was fetched for — the page is a healthcare
  data-science paper and carries no mutation-testing proposition. **Flip:** a paper source is only reopened when a
  retrievable abstract states the mutation-testing proposition the entry needs (the C1 principle rests on S335).

`setsid(1)` was re-opened for this round and turned out to be **S328 already** (r80); no duplicate row was written
and the C2 section cites S328. Within-scope duplicate check before the append: none of the three URLs or paths is in
the registry twice. Census before the append: `souji ok`, EXIT 0 (88 lines incl. 87 `W04`); after: see the report.

## Measured

- **C1 (calibration).** Population `census/round-84/c1-false-rows.tsv` sha256 `4795f009…f6f` (44 rows = the r83 36
  byte-for-byte + TF8, TF9, TF10, NF-P, NF-L, NF-L2, NF-M, NF-Q at fixture R7); harness
  `census/round-84/c1-false-row-harness.py`; battery `census/round-84/c1-clause-battery.py`; five mutants
  `census/round-84/c1-mutants.json`. After: `ARM pristine pop=r84 rows=44 mismatches=0 errors=0`, every mutant
  `killed=yes`, `SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5`, EXIT 0
  (`census/round-84/records/c1-after.txt`). Before (same counter, same battery, same mutants, 36-row population):
  pristine `36/0`, all five `killed=no`, `SUMMARY ... killed_r83=0`, EXIT 0
  (`census/round-84/controls/c1-before-r83-population.txt`). Per-mutant killing rows: m6↔NF-L, m7↔NF-L2,
  m8↔TF9+TF10, m9↔TF8+TF9+TF10+NF-P (`refused_true=3 accepted=1`, `census/round-84/records/c1-m9-rows.txt`),
  m10↔NF-M. The counter is byte-identical to r83's (`052c4f3f…`): the round moved the instrument, not the rule.
- **C2 (operability).** Population `census/round-84/c2-population.tsv` sha256 `31422477…ec58` (22 rows = the r83 20
  unchanged + `l1-late-setsid-pid` default launch + `l2-late-setsid-group` job-control launch); counter
  `census/round-84/c2-late-fork-counter.py`. Filed tool `tools/souji-vault-verify.sh` sha256
  `030fa10d5b7d312c4bc2ef759495c124616b9130f6cd0a52da7be2bdbb6ef41d`. After: `rows=22 mismatches=0 errors=0
  orphans=0`, l1 0.7 s / l2 0.6 s, 0 survivors, EXIT 0 (`census/round-84/records/c2-after.txt`). Before: the r83 tool
  bytes (control `census/round-84/controls/c2-K-a-r83-tool.sh`, `72a405f2…`) `rows=22 mismatches=2 errors=0
  orphans=2`, one surviving `setsid sleep 600` per late row, EXIT 1
  (`census/round-84/controls/c2-before-r83-tool.txt`). Regressions on the filed bytes: selftest 57/0, r17
  `total=37 failed=0 skipped=0`, probe D `arms=4 failed=0`. Clause mutants of the filed bytes: `kill -STOP`→`kill
  -TERM` killed (1 mismatch), no-KILL-sweep killed (2), single-pass **survives** (22/22), first-line re-check
  **survives** (22/22) — `census/round-84/records/c2-mutants-on-filed.txt`.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | vacuous fixture: the first `latefork` stub ran `while :; do sleep 1; done`, so bash deferred its trap past the tool's 0.1 s KILL sweep; the before arm read `survivors=0` on both late rows for the r83 tool (a false green) | first `census/round-84/controls/c2-before-r83-tool.txt` run | the before arm itself (it contradicted the r83 evidence that the class escapes) | stub busy-loops on the `:` builtin so the trap runs when the signal lands; disclosed as A0.1, no candidate had scored |
| M2 | unvacuous guard: `{ IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null \|\| continue` — `read` returns 1 at EOF, so the STOP/KILL re-checks skipped every pid and the freeze stopped nothing (d24-monitor-group 24 survivors, l1 2, l2 1; SUMMARY mismatches=5) | `census/round-84/records/c2-after-integration.txt` first run | the frozen population (it went red on the rows the repair is for) | the map pass's shape: read with no `\|\|`, then `[ -n "$now" ] \|\| continue`; re-run 22/0/0/0 |
| M3 | falsified wording: the repair's second map pass carries no row — a single-pass mutant scores 22/22 green because the CLI is frozen in pass 1 and never forks | `census/round-84/records/c2-mutants-on-filed.txt` (M2 survives); S84Connector F-03 | the round's own filed-byte mutant battery and the connector | A1: the claim names the freeze and the KILL sweep as load-bearing and the second pass as an unrowed belt; row design routed |
| M4 | falsified wording: the whole-file stat re-check (the r83 D5 fix) carries no row — its first-line variant scores 22/22 green because no frozen row has a comm with a newline | `census/round-84/records/c2-mutants-on-filed.txt` (M4 survives) | the same battery | A2: stated as a limit and as the D5 answer, not as a measured clause; a comm-newline row is routed |
| M5 | stale substrate: two seats (S84ExecEvade, S84MutTool) scored `RefC2` sha256 `a810acaf…` while the L1 was rewriting the reference; that copy carried the M2 `\|\| continue` defect, so their survivor counts (5 mismatches, 26 survivors on the fan-out shape) describe bytes no one filed | `S84ExecEvade.md` §"Bytes under test", `S84MutTool.md` §"Candidate provenance", S84Reviewer F1/F4 | S84Reviewer's chronology finding (RefC2's hash moved mid-review) and A0.2 | the filed bytes `030fa10d…` were re-scored by the L1 (22/0/0/0) and re-mutated; the ledger records which bytes each finding attacked |
| M7 | overclaim: the knowledge section and Q154 wrote a universal criterion ("one false row per clause the rule enforces") while the population bound five of the counter's eight MOVED-refusal clauses — the census-in-census clause is unbound by both pinned populations and a dropped-clause mutant resolves a wrong file while both stay green | `S84Sentinel.md` F1/F2, its `c1_clause_coverage.py` (8 clause mutants × 2 populations); `c1_wrong_file_demo.py` | S84Sentinel (its per-clause battery, not the frozen five) | A10 narrows the criterion to the clauses the population claims and states the unbound two; the `census/round-<N>/`-token row is routed to r85 |
| M6 | claim sizing: the first `m9` edit (`got[-1:] == want[-1:]`, no length guard) was already killed by the r83 population (NF-J), so it was not an unbound clause | first `census/round-84/controls/c1-before-r83-population.txt` run (`killed_r83=1`) | the before arm (the design required 0/5) | m9 replaced by the r83 critic's A2 rule (`len(got)==2 and got[1]==want[-1]`), which the r83 population leaves green; A0.3 |

## Wave

One v1 wave, 12 seats, policy `scripts/hyaku/ufo-wave-policy.json` (band 8-16): executor×3, scribe, scout×2,
connector, reviewer, critic, mutation-tester×2, sentinel. Attack seats 5/12 (42 %, over the 25 % floor);
connectors 1 (≤2). Seat verdicts and the falsification ledger are in `.ufo/waves/round-84/claim-falsification.tsv`
and the seat reports (force-added with the round, r83 D6).

| seat | verdict |
|---|---|
| S84ExecC1 | derived all eight new rows branch-by-branch from `judge()`; reproduced 44/0 + 5/5 and the 36/0 r83 regression; no finding |
| S84ExecC2 | built the freeze candidate (`a33038e9…`), 22/0/0/0 with l1/l2 green; did not close the D5 re-reads (connector F-02) — the L1 integrated them |
| S84ExecEvade | 14-cell evasion matrix on `a810acaf…` (M5): survivors on the late rows, the re-fork shape, the fan-out+late shape, and a daemonizing CLI that exits before the signal; no signal outside its own descendant set, no TMPDIR leak |
| S84Connector | C1/C2 **strictly separable** (no shared file, counter, population, command or receipt); F-01 the `start_of` reset in `RefC2`, F-02 the D5 re-reads in the seat candidate, F-03 the unrowed second pass, F-04 the dead census-in-tree branch |
| S84Reviewer | independently verified both claims on the committed bytes (C1 36/0 + 44/0 + 5/5 + 0/5; C2 control 2/2 and candidate green), confirmed P/F chronology and that F is the prereg alone; F1/F4 the mid-write RefC2 hash |
| S84MutCounter | extended the mutant set past the frozen five (see its report for the survivors it adds to the r85 route list) |
| S84MutTool | clause mutants of `a810acaf…` (M5); its per-clause table is re-derived on the filed bytes by `census/round-84/records/c2-mutants-on-filed.txt` |
| S84ScoutDirs | real-shape census against the R7 fixture; the census-in-tree branch is still ungrounded |
| S84ScoutSources | S334 admitted, S336 rejected, S335 the own-work receipt row — its drafts were superseded by the rows the L1 filed (S334-S336) and its report is force-added |
| S84Scribe | knowledge drafts (both sections), the two QUALITY rows, and an independent reproducer for the `read -d ''` guard defect |
| S84Critic | wording falsification of both claims: C1 a 40-row subset kills the same 5/5 (A8), NF-Q kills none of the five (A7), a MOVED verdict is location+digest equality not lineage; C2 the claim's subject is the repair commit's bytes, not the bytes at F (A9), the root is never STOPped and a child whose parent dies in the window is skipped; interim output at `agent://S84Critic`, report file is a skeleton |
| S84Sentinel | adversarial kill scope and clause coverage: F1/F2 two counter clauses unbound by both populations (a census-in-census mutant resolves a wrong file, green on both — A10); F6 the comm-with-newline leak, FIXED in the filed bytes `030fa10d` (still open in `a33038e9`/`a810acaf`); F7 the abort path's group kill can signal a process that joined the CLI's group (pre-existing since r83, routed); F9 with TMPDIR inside the vault the tool installs no trap (pre-existing r81 foreground fallback, routed); canary under pid churn never signalled |

## Routed to round 85

- **C1:** a FALSE row whose token is a `census/round-<N>/` path with a frozen digest (binds the census-in-census clause the sentinel showed unbound, and grounds or replaces the dead census-in-tree branch), a last-component row (`…/erratum-evidence-RENAMED.txt`), `NF-L3` (a token whose first below-round component is not a wave directory), the census-in-tree branch
  (ground it with a `census/round-<N>/` token item or delete it — carried since r83), and a row for the
  token-on-line / unknown-class refusals (S84MutCounter survivors).
- **C2:** a row that exercises the second map pass (a child forked in the read→STOP window; needs a stub whose fork
  is observable without racing the walk), a comm-with-newline row for the whole-file re-check (r83 D5), a pid-reuse
  row, a parent-before-child row, `termign-fork`/`p5-late-term` (r83 list), and a `strace`-robust settle.
- **Wave discipline:** the reference implementation must not be edited while seats are scoring it; a reference copy
  belongs in a seat-owned path with a frozen hash (M5).
