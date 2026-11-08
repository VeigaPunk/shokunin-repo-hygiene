# Round 83 — the pointer counter binds own-tree moves to real wave shapes (C1 calibration), the vault tool walks the CLI tree once, fork-free (C2 operability)

Attempt 1 (`SoujiR83`). Lane base `1e870403c5d806a5cf9ac93b00da7a928359608f` (r82 closed `admitted`; spot-check
`corpus/lessons/round-82-verifier-spotcheck.md`). Frozen claims, counters and predicates are in
`census/round-83/preregistration.txt`; the wave's amendments are in `plans/round-83.md` (A0-A9) and the pre-file
ledger in `.ufo/waves/round-83/claim-falsification.tsv`.

## Inherited

The r82 spot-check closed round 82 `ok`, **admitted**, with eleven routed defects; the r82 lesson routed seven more.
Answered this round: defect 1 (the S330 candidate never became a row → S330 now exists as `rejected`), defect 2 (the
LOG C2 bullet's "drops the stale `$!`" → corrected in the r83 LOG entry), defect 3 (the missing `51a5e7fa` row in
the r82 report chain → named in the r83 report), defect 5 (C1 own-tree real shapes → C1), defect 8 (C2 tree walk →
C2), defect 9 (the dead `m-` monitor test → C2's launch column), defect 10 (the `termign-fork`/`p5-late-term` rows →
carried), defect 4 (planner seat → documented below). Not answered: defect 6 (the C1 identity clause → proven dead
and deleted, not rowed), defect 7 (the census-in-tree branch → carried), defect 11 (the carried r81 list → carried).

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=1e870403 ahead=0 tracked=0 untracked=0`). No
`considerthese/` directory exists in this lane; no shokuknow theme taken (`Assimilation: none`).

**Planner seat (r82 defect 4), resolved:** `scripts/hyaku/ufo-wave-policy.json` `lanes[]` enumerates scout,
reviewer, labrat, critic, connector, executor, mutation-tester, revenger, simplifier and scribe — there is **no
planner lane id**, so the validator cannot spawn one; the `nativeProfiles.omp-native-v1.planner` object is a different
surface (a profile slot, not a dispatchable item). The L1 holds the canonical planner seat and the wave's planning
data-walk rode scouts, as the prompt permits.

## Gate

- **S332 — Linux kernel `fs/proc/array.c` at tag v6.17, `do_task_stat()`** (URL
  `https://raw.githubusercontent.com/torvalds/linux/v6.17/fs/proc/array.c`, HTTP 200, 23233 bytes, sha256
  `17f2318d…a938`; re-fetched byte-identical; capture `census/round-83/srcs/linux-array.c-v6.17`; opened
  2026-11-08). Quote, lines 590-594 (a concatenation of those five lines): "seq_puts(m, \" (\"); proc_task_name(m,
  task, false); seq_puts(m, \") \"); seq_putc(m, state); seq_put_decimal_ll(m, \" \", ppid);" — and line 612 emits
  `start_time`. **ADMIT**, `code`, tier A. It is a different source from S075 (`proc_pid_stat(5)`): S075 governs
  process identity fields, S332 the kernel's emission order and the unescaped comm. Duplicate-URL check: no other row
  cites the kernel tree or this URL.
- **S331 — the lane's own wave-directory census** (`census/round-83/records/wave-dirs.txt`, committed at
  `1014143d`; working tree at `1e870403`; command in the file header; opened 2026-11-08). Quote, the file's own
  output: "w1/ 65, w2/ 19, assimilation/ 4, records/ 3, residual/ 2, w3/ 1, a2w1/ 1". **ADMIT**, `own-work`, tier A,
  `mined`. Scope narrowed by the source seat to the `.ufo/waves/` tree only (the `census/round-<N>/` capture shapes
  are a different tree); this is the only row that speaks to the C1 rule's shape list.
- **S330 — procps-ng `pgrep(1)` as installed** (procps-ng 4.0.7-1, `/usr/share/man/man1/pgrep.1.gz`, sha256
  `04b59b01…a916`; opened by the r82 Gate 2026-11-07, re-opened 2026-11-08). Quote, decompressed lines 166-167:
  "Only match processes whose parent process ID is listed." **REJECTED** (the r82 spot-check's routed defect 1
  repairs the form: the rejection is now a row): S075 already governs process identity, and `-P` is the mechanism
  the tool proves by running; **flip:** a claim that needs pgrep's own selection semantics (`-a/--list-full`,
  `-o/--oldest`, `-n/--newest`, `-f/--full`) rather than parent attribution. The source seat corrected the first
  draft's flip, which named `NSpid` — a token that appears nowhere in this page (`grep -in nspid` → 0).
- **Within-scope duplicate check before the append:** S330's URL is new (S075 is a different man page); S332's URL
  is new; S331 is `own-work`. `sources-census.sh validate` before the append: 88 lines, `souji ok`, rc 0 (87
  pre-existing `W04` cross-scope duplicate-URL warnings).
- **Spot-check result:** this round's non-author closure spot-checks the three decisions (it is the outside check;
  the lane does not self-attest it).

## Measured

Staged commits in the order the round binds: P `1014143d5cb3ecad23329c8f63cb72328ff30061` (instruments + controls +
real-shape census), F `fbf0ae5e4ac54eec16b9ef5f2439de2a44dfb7b0` (preregistration alone; `git show --name-only` =
one path), post-F correction `51b50c94d0d9a5baf3e6564d1b5dbc48b970053c` (deep-stub hang point after its fan-out),
W1 `bbffe6a0d1221766b76acbf78c649a5783ac9def` (C1 counter + receipts), W2 `9994af61565ec87913152cf1102c61ac9a75b04d`
(C2 tool + receipts), then the integration cleanup (C1 dead-code/comment correction, tool arity guard) and the
regenerated receipts.

- C1 (frozen harness `census/round-83/c1-false-row-harness.py`, 36 rows): K-a (the r82 counter) `mismatches=2
  accepted=0 refused_true=2` EXIT=1, the two refusals TF6 (`w2/`) and TF7 (`w1/`); candidate `mismatches=0
  accepted=0 refused_true=0 errors=0` EXIT=0 at counter sha256 `052c4f3f…` (`records/c1-after.txt`); regressions
  r77 35/35 + 7/7, r78 22/22 + 12/12, r79 9/9, r80 18/18, r81 25/25, r82 32/32.
- C2 (frozen counter `census/round-83/c2-tree-walk-counter.py`, 20 rows): candidate `mismatches=0 errors=0
  orphans=0` EXIT=0 at tool sha256 `b0a5b662…` (`records/c2-after.txt`; deep rows 0.3-0.4 s, 0 survivors, default and
  monitor launches); pgrep invocations 106-108 for the r82 tool and 0 for the candidate (external shim,
  `census/round-83/records/c2-before-pgrep.txt`); selftest 57/0, r17 37/0, probe D 4/4.
- The C2 control is a load-dependent race: five executions of the byte-identical r82 tool through the frozen counter
  give `mismatches` 0, 2, 2, 2, 4 (idle deep rows 1.8/2.0/3.8/4.6 s, `S83Reviewer` F1); the round therefore claims
  no fixed before-count (A5).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | attribution: the wave context named the lane base as the tip at spec-build time (`fbf0ae5e`, which is F) instead of `1e870403` | `S83MutCounter` caveat; `S83Reviewer` F9; prereg line 2 | none — the seat read the prereg and caught it | the report carries the real base; next wave's context builds the base from the prereg, not `rev-parse master` |
| M2 | vacuous fixture: the `deep` stub wrote its hang mark BEFORE spawning its children, so a fast correct walk read survivors (16/24) on `d24-monitor-group` while a slow r82 walk passed the same row | reference run `d24-monitor-group survivors=16`; correction `51b50c94` | the L1's own reference run — the do-nothing control alone never showed it (A0) | stub fans out first, mark last; control re-run red for the same reason (`mismatches=4`); disclosed as A0 |
| M3 | unvacuous guard: `${20}` in bash is `${2}` + `0`, so the "starttime" check compared the current ppid with the pass ppid; when the DFS killed a parent first, its children were re-parented and skipped (7-20 of 24 survivors) | debug dumps `DBGC s20=48246753 s0=36505100`, `DBGMISS got=14870 want=41590020`; two rows passing/failing alternately | none — found by instrumenting the walk after two flaky rows | `${20}` for every positional above 9; assert a field's meaning on one known pid before trusting a guard |
| M4 | stale binding: the C2 after-receipts named `tools/souji-vault-verify.sh.new`, a path that never landed, and a seat read the pre-integration draft's red receipts as if they were the filed bytes | `S83Reviewer` F6; `S83Scribe` F-1 | S83Scribe F-1 and S83Reviewer F6 (both re-derived by the L1) | receipts regenerated against `tools/souji-vault-verify.sh` and its digest; the round lands receipts only from the landing path |
| M5 | false comment: the r82 code comment "the order carries: owntree/PF-1 before the last-component basename test" contradicts `judge()` (basename first, owntree second) and was carried into the new counter | `S83Connector` §3.1; `census/round-83/c1-pointer-counter.py` (corrected comment) | S83Connector (a wave seat) — the r82 A1 correction never reached the code comment | comment corrected to state the real order; the C1 receipt regenerated on the final bytes |
| M6 | unrowed safety code: the starttime re-check and the as-discovered kill order are in the tool but no frozen row separates them (m1/m7/m8 mutants survive 20/20) | `S83MutTool` m1/m7/m8; `S83CriticClaims` C2 | S83MutTool (the round's own mutation seat) | A6 narrows the claim to the measured delta; pid-reuse and parent-before-child rows routed to r84 |
| M7 | form: the prereg is prose, not the r80-r82 key-line shape, so `tools/souji-freeze-check.py` reports 13 `FIELD-MISSING` and verifies nothing; the population pins and receipt digests carry the binding instead | `S83Reviewer` F4 | S83Reviewer (the round's own reviewer) | A9 records it; r84's prereg restores the key lines |
| M8 | plan drift: the lane waited ~20 minutes on the dispatcher host gate while 192 foreign `while True: pass` processes held load1 ≈ 250 (a seat's `load_stable` probe, not this lane's) | `.ufo/state/inline-dispatcher.log` `host-defer` lines; Main's reap message | Main (operator session) reaped them after the L1 reported the count | no lane action; reported, not routed |

## Wave

One v1 wave, 12 seats, policy `scripts/hyaku/ufo-wave-policy.json` (band 8-16): 3 executor, 1 scribe, 2 scout,
1 connector, 1 reviewer, 1 critic, 2 mutation-tester, 1 sentinel. Attack seats 6/12 (50 %, over the 25 % floor).
Spawned 02:06:37 after a host-gate deferral; 9 seats delivered substantive reports, **3 seats left a skeleton only**
(S83ExecC2, S83Sentinel, S83ScoutDirs) and are reported dead-in-effect; C2 was independently re-derived by
S83ExecC1's sibling work, S83MutTool, S83ExecEvade, S83CriticClaims and S83Reviewer, so no conjunct lost its check.

| seat | verdict |
|---|---|
| S83ExecC1 | candidate byte-identical to the landed counter (`2d163a6e…` then), 36/36 + 5 regressions green; synthetic probes of `_owntree_ok` (TF6/TF7/TF4/assimilation/records-wave true; NF-J/NF-K/decoy false) |
| S83ExecEvade | 36 evasion runs: candidate/control exit within settle, 0 survivors, empty TMPDIR across fast-exit, TERM-ignoring, setsid, 24-child fan-out, 3-deep chain, `a) (b` comm, double-fork; r82 baseline spends 26 pgrep forks and 2.99-3.83 s on fan24 (F-2 margin) |
| S83MutCounter | 8 mutants: m1 (drop `wN/`), m2 (shapes only), m3 (basename only), m4 (own-tree dropped) killed by TF6/TF7/NF-J; **m5 identity clause equivalent/dead; m6 digest, m7 round-equality, m8 `records/` survive** → NF-L/NF-L2/NF-M/NF-L3 rows named |
| S83MutTool | 8 mutants of `cli_kill_tree`: starttime re-check, `ps` map, private-file order and others survive 20/20; the candidate variant it tested passed 20/0/0/0 at 0.9-1.0 s |
| S83Reviewer | chronology holds (P < F < correction < W1 < W2, F touches one path); C1 K-a reproducible; **F1 high: the C2 control is green on an idle host (0,2,2,2,4 over five runs)**; F2 the pgrep shim is not the counter's; F3 the `${20}` unbound-variable abort; F4 the freeze-check form; F6 the `.new` path; F7 `records/wave-<anything>`; F8 late forks |
| S83CriticClaims | C1: two cheaper rules meet the target (shape-lean, basename-only), the six-shape list is over-specified, three alternates dead, identity dead, NF-K mislabelled; C2: the safety clauses are unrowed and the control is not reproducible |
| S83Connector | C1/C2 STRICTLY SEPARABLE (no shared file, counter, population or command); sibling overlap: `tools/souji-proc-census.sh:136-160` already parses ppid/starttime (fields[1]/fields[19]) for the prose census; wording table (unrowed wave shapes, dead identity, contradictory comment, pgrep shim, `SOUJI_*` scrub) |
| S83ScoutSources | S332 admit (anchor corrected to a named line concatenation + the unescaped-comm branch), S331 admit (scope narrowed to `.ufo/waves/`), S330 admit as rejected (flip corrected off `NSpid`); comm-newline hazard noted (F-6) |
| S83Scribe | drafts for both knowledge sections, Q152/Q153, the three SOURCES rows; measured the pgrep topology (N+2 nodes; 108 = 6×2 + 4×3 + 2×2 + 2×14 + 2×26) and caught the stale `.new` receipts (F-1) |
| S83ExecC2 | skeleton only — no verdict (its candidate `98b0ca80…`, 1893 lines, was the bytes MutTool/Evade attacked) |
| S83Sentinel | skeleton only — no verdict |
| S83ScoutDirs | skeleton only — no verdict |

## Repairs after the wave (not the claim's measurements)

- C1 cleanup (after the first score, before filing): the three dead capture alternates and the unreachable `tt ==
  tk` disjunct removed from the own-tree branch, the contradictory r82 comment corrected. Re-measured on the final
  bytes: 36/0/0/0 and all six regressions green (`records/c1-after.txt`, counter sha256 `052c4f3f…`).
- C2 arity guard (after the first score, before filing): `[ "$#" -ge 20 ] || continue` in the `/proc` pass and
  before each TERM and KILL, so a short stat line cannot abort the trap handler under `set -euo pipefail`
  (S83Reviewer F3; observed `v2-int-pid` `survivors=2` on the pre-integration draft). Re-measured on the final
  bytes (`b0a5b662…`): 20/0/0/0, selftest 57/0, r17 37/0, probe D 4/4.
- Both repairs are disclosed in `plans/round-83.md` A1-A3/A9; the receipts cited in the report are the regenerated
  ones, and the older receipts are superseded in place (no receipt is edited to hide a red run).

## Routed to round 84

1. C1 deep-token pair (kept `…/w2/sub/X`, refused flattened `…/w2/X`) and the NF-L/NF-L2/NF-M/NF-L3 rows the
   mutants named; true rows for `a2w1/` and `assimilation/`; ground or delete the census-in-tree branch.
2. C2 pid-reuse row, parent-before-child row, `termign-fork`, `p5-late-term`; a `strace`-robust settle; the
   comm-newline skip as a hostile-CLI row.
3. Prereg form: the r80-r82 key-line shape (`Round:/Base:/Counter:/Population:/Control:/Target:/Kill:`) so
   `souji-freeze-check.py` verifies the round.
4. Carried unchanged from the r81 list: `_regular` pathspec framing, the quarantine intro-blob digest row, the
   fork-tail row, the r79 gate re-measurement, the check-4 300 s backstop, r76 K03/K04, status-trusting lane tools,
   r17 240 s runners.
