# Round 85 — the false-row population binds the counter's class-enum guard (C1 calibration), record-agreement K4 re-derives tracked bytes instead of trusting `git status` (C2 operability)

Attempt 1 (`SoujiR85`). Lane base `705fa1385c4ccec23811cfa57104046ec6587258` (r84 closed `admitted`; spot-check
`corpus/lessons/round-84-verifier-spotcheck.md`). Frozen claims, instruments and predicates are in
`census/round-85/preregistration.txt`; the wave's amendments are in `plans/round-85.md` (A0-A3) and the pre-file
ledger in `.ufo/waves/round-85/claim-falsification.tsv`.

Staged commits: P `5bd5a0ce5ab012c7a87b394290d1ac5843c9a7f7` (instruments, populations, mutants, controls, before
receipts), F `43c630eb3983f5b5b51f8b46dd9e64899427378b` (preregistration ALONE), wave artifacts `1ed32fe4`, then the
C2 repair, the after receipts and the integration commits that follow.

## Inherited

The r84 spot-check closed round 84 `ok`, **admitted**, with two status-neutral defects (D1 the pre-file gate wants
`.ufo/waves/round-N/claims.json`, absent since r84; D2 the clause battery's kill rule cannot separate a row mismatch
from a harness error) and the routed r85 list. Answered this round: **D1** — `.ufo/waves/round-85/claims.json` is
frozen with the two claims, so the gate can read a claims file instead of returning SETUP (the ledger itself is still
authored against the wave's artifacts, which the gate does not read). **D2** — the C1 battery prints `mismatches`
and `errors` separately on every `MUTANT-PAIR` line and the round reads them separately; no kill this round came from
an error. Not answered: none.

The r84 `## Routed to round 85` list, item by item: "a FALSE row whose token is a `census/round-<N>/` path with a
frozen digest" → **built** (NF-R, on item I85R) and it **falsified the routed premise**: the branch is shadowed, not
unbound (A1); "NF-L3 (a token whose first below-round component is not a wave dir)" → **not built**, carried (the
r85 population needed the census-token item first, and NF-L3 needs a population item whose token contains such a
path); "the census-in-tree branch (ground it with a `census/round-<N>/` token item or delete it)" → **answered:
delete** (A1, measured); "a row for the token-on-line / unknown-class refusals" → **unknown-class built** (NF-S,
the claim); token-on-line **not built** (a row whose token is not on its base line makes the pristine arm red by
construction, so it cannot be a population row); C2 list (second map pass, comm-with-newline, pid-reuse,
parent-before-child, termign-fork, strace settle) → **carried**, none built this round.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=705fa138 ahead=0 tracked=0 untracked=0`).
`considerthese/` does not exist in this lane; no shokuknow theme taken (`Assimilation: none`).

**Planner seat.** The L1 holds it (`scripts/hyaku/ufo-wave-policy.json` `lanes[]` has no `planner` id); the wave's
planning data-walk rode the connector and the two scouts.

## Gate

Sources opened this round (each opened by fetching/reading it here; ids continue the registry after S336):

- **S337 — PIT (pitest.org), the tool's own documentation** (`https://pitest.org/`, HTTP 200, 12023 bytes, sha256
  `b0c7e050…10cc`; capture `census/round-85/srcs/pitest-org.html`; opened 2026-11-08). Quote, the "Mutation testing"
  section: "mutation testing is the gold standard against which all other types of coverage are measured".
  **ADMIT**, `docs`, tier B (a tool vendor's documentation is a strong secondary, not a spec), `mined`. It grounds
  exactly the C1 principle — a suite is judged by the mutants it kills, so a population is judged by the mutants it
  kills, not by the rows it carries. Duplicate-URL check: no other row cites `pitest.org`.
- **S315 (racy-git), S316 (git-hash-object), S317 (gitformat-index), S335 (own-work clause-kill receipts) were
  re-opened this round** for the C2/C1 ground. Their cells are unchanged: no `status`, `recheck` or `used-by` edit,
  and S317's `used-by` already names the entry the r85 section extends. The C2 section quotes S317's index-entry
  field list ("32-bit mtime seconds … this is stat(2) data") from the installed `gitformat-index(5)` (git 2.56.0),
  and S315's racy-git sentence ("Git can incorrectly think files in the working tree are unmodified even though they
  actually are") is the class K4 now refuses rather than trusts.

- **S338 — git-status(1) as installed** (git 2.56.0-1, capture `.ufo/waves/round-85/w1/S85ScoutSources/
  git-status.1.gz`, roff line 40; opened 2026-11-08 by S85ScoutSources and re-read here). Quote: "paths that have
  differences between the working tree and the index file". **REJECTED** — the sentence restates ground S317 (the
  index entry's stat data) and S315 (the stat shortcut) already carry; a third row on one comparison is registry
  weight, not knowledge. **Flip:** a scoped teaching the existing rows do not carry (the porcelain format's own
  contract, or its background-refresh behaviour).
- **S339 — gitformat-index(5) as installed** (git 2.56.0-1, capture `…/S85ScoutSources/gitformat-index.5.gz`, roff
  line 172; opened 2026-11-08). Quote: "Hash checksum over the content of the index file before this checksum."
  **ADMIT**, `docs`, tier A, `mined` — it grounds why the C2 fixture's forgery must re-checksum the index and why an
  index rewrite is a whole-file act.
- **S340 — "Practical Mutation Testing at Scale", arXiv:2102.11378** (`https://arxiv.org/abs/2102.11378`, HTTP 200,
  43870 bytes, sha256 `38551f5c…cc2f8`; capture `…/S85ScoutSources/arxiv-2102.11378-abs.html`; opened 2026-11-08).
  Quote, abstract: "Mutation analysis assesses a test suite's adequacy by measuring its ability to detect small
  artificial faults, systematically seeded into the tested program." **ADMIT**, `paper`, tier B, `mined` — the
  paper-backed form of S337's vendor sentence, and the quote the C1 criterion actually needs.

Census before the appends: `souji ok`, EXIT 0 (`census/round-85/records/sources-census-before.txt`); after them:
`souji ok`, EXIT 0 (`…-after.txt`), 87 pre-existing `W04` cross-scope duplicate-URL lines plus the first attempt's
`E09` (the S338 flip text sat in the `recheck` cell instead of `teaches`) — corrected before the green run, which is
M5 below. Registry `259 → 263` (`grep -cE '^\| *S[0-9]{3,}' corpus/SOURCES.md`): four rows added, one rejected,
zero removed.

## Measured

- **C1 (calibration).** Population `census/round-85/c1-false-rows.tsv` sha256 `1468236c…8d42` (47 rows = the r84 44
  byte-for-byte in order, plus NF-R and TF11 at fixture R8 and NF-S at R8). Counter
  `census/round-85/c1-pointer-counter.py` sha256 `91b4ffde…7304` (r84's resolution rules byte-for-byte; the only
  change is one added POPS entry for the r85 item population `census/round-85/c1-items.tsv` sha256 `d9a2ad8c…5114`,
  required because the counter refuses an unpinned population). Battery after, `--only r85 --expect-killed 6`:
  `ARM pristine pop=r85 rows=47 mismatches=0 errors=0`, six `MUTANT-PAIR … killed=yes`, `SUMMARY mutants=6 sets=r85
  pristine_r85=ok killed_r85=6`, EXIT 0 (`census/round-85/records/c1-after.txt`). Before (do-nothing, same counter,
  same battery, same six mutants, r84 44-row population): `killed_r84=5`, `m11-class-enum killed=no`, EXIT 0
  (`census/round-85/controls/c1-before-r84-population.txt`). Shadow probe (`probes/c7-shadow.json`, one mutant,
  `--only r84,r85 --expect-killed 0`): `killed_r84=0 killed_r85=0` with both pristine arms green
  (`census/round-85/records/a1-c7-shadow.txt`) — A1.
- **C2 (operability).** Filed tool `tools/souji-record-agreement.py` sha256 `ed1ada73…d382` (K4 change only:
  `truth_refusal` + one `bad()` call; 30 insertions). Counter `census/round-85/c2-k4-counter.py` sha256
  `0a7b801d…9648` (7 frozen rows over a hermetic synthetic repository). After: `SUMMARY rows=7 mismatches=0
  errors=0`, the three forged rows `k4=1 named=yes`, EXIT 0 (`census/round-85/records/c2-after.txt`). Before: the
  base blob `ec5b809d…8d32c` `SUMMARY rows=7 mismatches=3 errors=0`, KF1/KF2/KF3 `k4=0 match=no`, EXIT 1
  (`census/round-85/controls/c2-before-base-tool.txt`).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | survivor/leak: the C2 counter's `reset()` did not rebuild the index, so a forged stat entry survived `git reset --hard` and the NEXT row read the previous row's forgery red (`k4=1 named=no` on KF2/KF3) | first `census/round-85/controls/c2-before-base-tool.txt` run; the counter printed `k4rows=['a.txt|uncommitted-path']` on KF2 and `['ln|…']` on KF3, naming the wrong row's path | the counter's own per-row `k4rows` diagnostics (added after the first run) | `reset()` deletes `.git/index` before the reset, so every tracked path is checked out again; re-run reads `mismatches=3` with the three forgeries missed — the frozen before (A0.1) |
| M2 | substrate (the r84 M5 class repeating): the C2 counter was edited after two seats had scored it — the m5 mutant made it die with `KeyError` because the `named` predicate indexed `FORGED` for honest rows | `.ufo/waves/round-85/w1/S85MutK4.md` § m5, which prints the traceback and the counter sha it ran (`ae482f07…`) | S85MutK4's report (its sha line is what makes the edit visible) | fixed pre-file (`0a7b801d…`) and both arms re-run on the filed bytes; A0.4 binds every seat finding to the counter sha it attacked |
| M3 | number-drift: the r85 row pin declared 48 rows for a 48-line file that holds 47 rows (one header comment) | harness/battery `FATAL: population is not 48 well-formed rows` before any score | the pin check in `c1-false-row-harness.py` / `c1-clause-battery.py` | pin corrected to 47 before data; the sha256 never changed (A0.2) |
| M5 | reference-drift: the first S338 row put the rejection's flip condition in the `recheck` column, which the census reads as a cadence (`E09 recheck=…`) | `census/round-85/records/sources-census-after.txt` first run, `E09` on S338 | the source census (E09 is the rule's own detector) | the reason and flip moved into `teaches` (`REJECTED: …; flip: …`) and `recheck` set to `180d`; census re-run green |
| M4 | stale-premise: the round's first C1 target ("bind the census-in-tree clause with a census-token row") was not bindable — the clause is shadowed, so no row can kill it | the first r85 battery arm: `m11-census-in-tree killed=no` on BOTH populations | the before arm itself (a target that cannot move) and the shadow probe `records/a1-c7-shadow.txt` | retargeted to the class-enum guard before F; the measurement kept as A1, and Q156 added so the next round tests shadow-vs-unbound before naming a clause unbound |

## Wave

One v1 wave, 12 seats, policy `scripts/hyaku/ufo-wave-policy.json` (band 8-16): executor×3, scribe, scout×2,
connector, reviewer, critic, mutation-tester×2, sentinel. Attack seats 5/12 (42 %, over the 25 % floor);
connectors 1 (≤2). Seat verdicts and the falsification ledger are in `.ufo/waves/round-85/claim-falsification.tsv`
and the seat reports (force-added with the round).
