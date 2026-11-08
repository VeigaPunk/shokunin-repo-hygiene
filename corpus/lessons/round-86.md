# Round 86 — two clauses r85 measured reachable and unrowed get their rows (C1 calibration); record-agreement K4 carries the writer's index-flag sweep and keeps record paths on one line (C2 operability)

Attempt 1 (`SoujiR86`). Lane base `89d02c907d40cc09fedc9d420cf9509df685e143` (r85 closed `admitted`; spot-check
`corpus/lessons/round-85-verifier-spotcheck.md`, its three status-neutral defects D1-D3 and the routed R86-1..R86-4
list). Frozen claims, instruments, predicates and kill rules are in `census/round-86/preregistration.txt`; the wave's
amendments are in `plans/round-86.md` (A0-A5) and the pre-file ledger in
`.ufo/waves/round-86/claim-falsification.tsv`.

Staged commits: P `47602fa690d19bd320fc0053fbeed46a1270ff09` (instruments, populations, mutants, controls, both before
receipts), F `d77b42589ea77a27e0050e3bdc86ab5450baccd2` (preregistration ALONE), the C2 repair
`2acbbfc80ac91e1b65cf5dae7287209fed9c7c86`, then the wave artifacts, the after receipts and the integration commits.

## Inherited

The r85 spot-check closed round 85 `ok`, **admitted**, with three status-neutral defects and a routed list. Answered
this round:

- **R86-1 (D1, the report's registry count)** — the r86 report's registry count is derived from the same
  `grep -cE '^\| *S[0-9]{3,}\|' corpus/SOURCES.md` at file time (263 → 268), not from a draft census.
- **R86-2 (D2, wave seat reports gitignored)** — the r86 wave's seat reports are force-added in the wave-evidence
  commit, so the falsification ledger's artifact column names durable paths.
- **R86-3 (A1/A4 carried: ground it or delete it)** — answered **ground**: NF-W and NF-Y are the two rows, and
  nothing was deleted. The rest of the r85 survivor list (m12, m16, m17, the `len(got) < 2` arm, the basename
  clause) stays carried, with the basename clause now classified shadowed-for-verdict rather than unbound.
- **R86-4 (A2/A3/F7 carried)** — the five-path naming cap is unchanged (S86ExecEvade measured it, see the wave);
  the r83/r84 C2 carried list (pid-reuse, parent-before-child, termign-fork/p5-late-term, strace settle) is carried
  again; the inherited K3 tally row is routed with its cause (A4).

No inherited lane leftovers at start (`jj-lane.sh state` at start: `local=remote=89d02c90 ahead=0 tracked=0
untracked=0`). `considerthese/` does not exist in this lane; no shokuknow theme taken (`Assimilation: none`).

**Planner seat.** The L1 holds it (`scripts/hyaku/ufo-wave-policy.json` `lanes[]` has no `planner` id); the wave's
planning data-walk rode the connector and the two scouts.

## Gate

Sources opened this round (each fetched/read here; ids continue the registry after S340):

- **S341 — git-ls-files(1) as installed** (git 2.56.0-1, `/usr/share/man/man1/git-ls-files.1.gz`, capture
  `census/round-86/srcs/git-ls-files.1.gz` sha256 `153d58dd…`, opened 2026-11-08). Quote, OPTIONS `-t`, rendered
  line 119: "tracked file that is not either unmerged or skip-worktree". **ADMIT**, `docs`, tier A, `mined` — it
  grounds the sweep's decision rule: a non-`H` tag names exactly the entries a status comparison cannot be trusted
  for. Duplicate-URL check: no other row cites `git-ls-files`.
- **S342 — git-update-index(1) as installed** (capture `census/round-86/srcs/git-update-index.1.gz` sha256
  `27e70864…`, opened 2026-11-08). Quote, "Skip-worktree bit" section, rendered lines 325-326: "Tell git to avoid
  writing the file to the working directory when reasonably possible, and treat the file as unchanged when it is
  not". **ADMIT**, `docs`, tier A, `mined` — the flag's own contract is to treat the path as unchanged, so a change
  behind it is invisible to every status read.
- **S343 — gitsubmodules(7) as installed** (capture `census/round-86/srcs/gitsubmodules.7.gz` sha256 `607d08e2…`,
  opened 2026-11-08). Quote, first section, rendered lines 26-27: "The gitlink entry contains the object name of the
  commit that the superproject expects the submodule’s working directory to be at." **ADMIT**, `docs`, tier A,
  `mined` — a gitlink's recorded content is a commit id, not bytes, so no hash of the worktree can decide it.
- **S344 — the same git-ls-files page, `--stage`** (opened 2026-11-08). Quote, rendered lines 51-52: "Show staged
  contents' mode bits, object name and stage number in the output." **REJECTED** — the mode/object-name half
  restates S317 (the index entry's stat and object fields) and S327 (each tree entry carries its mode and type), and
  the stage number is a detail this lane's receipts already exclude. **Flip:** a scoped teaching about the unmerged
  stage triples and resolve-undo, which neither row carries.

Re-opened unchanged for the round's ground: S315 (racy-git), S316 (git-hash-object), S317 (gitformat-index), S339
(the index file's trailing checksum), S335/S337/S340 (clause-kill receipts and mutation adequacy).

Census before the appends: `souji ok`, EXIT 0 (`census/round-86/records/sources-census-before.txt`, 88 lines: 87
pre-existing W04 cross-scope duplicate-URL warnings and the ok line); after them: `souji ok`, EXIT 0
(`…-after.txt`), no `E0x` finding. Registry `263 → 268` (`grep -cE '^\| *S[0-9]{3,}\|' corpus/SOURCES.md`): five
rows added, one rejected, zero removed.

## Measured

- **C1 (calibration).** Population `census/round-86/c1-false-rows.tsv` sha256 `79db70f6…` (49 rows = the r85 47
  byte-for-byte in order plus NF-W and NF-Y at the new fixture revision R9); item population
  `census/round-86/c1-items.tsv` sha256 `5abf3b01…` (the r85 three items byte-for-byte plus I86S, base 705fa138);
  mutants `census/round-86/c1-mutants.json` (the r85 six byte-identical plus `c7-census-in-tree` and
  `m14-short-shape`). After, `--only r85,r86 --expect-killed 14`: `ARM pristine pop=r85 rows=47 mismatches=0
  errors=0`, `ARM pristine pop=r86 rows=49 mismatches=0 errors=0`, eight `killed=yes` on r86,
  `SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14`, exit 0
  (`census/round-86/records/c1-after.txt`). Before, the do-nothing control `--only r85 --expect-killed 6`:
  `killed_r85=6`, `c7` and `m14` `killed=no`, exit 0 (`census/round-86/controls/c1-before-r85-population.txt`). The
  r86 counter differs from r85's by one POPS entry plus its docstring (reviewer-verified diff).
- **C2 (operability).** Tool `tools/souji-record-agreement.py` sha256 `cf875367…` (the wave repair `f5e196a2` closes the sentinel's config-view route; the first repair commit `2acbbfc8` measured `4cc3b945…` and every 9-row number is identical on both) (before: the lane-base bytes
  `0ade0751…`, copied at `census/round-86/controls/c2-before-base-tool.py` with a byte-identical copy of the writer
  beside it, `70bbf1c2…`). After: `SUMMARY rows=9 mismatches=0 errors=0`, KG1
  `k4rows=['.|index-flag-concealed']`, KG2 `named=yes`, the seven r85 rows unchanged, exit 0
  (`census/round-86/records/c2-after.txt`). Before: `SUMMARY rows=9 mismatches=2 errors=0`, KG1 `k4=0` (no row at
  all), KG2 `named=no`, exit 1 (`census/round-86/controls/c2-before-base-tool.txt`).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | control-binding: the C2 before-arm control had no writer beside it, so `truth_refusal` failed closed and all 9 rows flagged (7 mismatches, not 2) | the first probe run's own detail: `the receipt writer is not beside this tool (…/census/round-86/controls/souji-receipt-write.py)` | the receipt's per-row `detail=` field, which is why the counter prints one | byte-identical writer copy beside the control (`70bbf1c2…`) plus a `# writer path=/sha256=` header in the counter so the binding is visible; re-run reads the intended 2 (A0.1) |
| M2 | instrument-class drift: the first after-arm classed KF1-KF3 `index-flag-concealed` because the predicate was `msg.startswith("RECEIPT-")`, and the truth class is itself `RECEIPT-WORKTREE-STAT-CONCEALED` | the first after run's `k4rows=['.|index-flag-concealed']` on rows whose r85 class was `stat-cache-concealed` | the counter's own `k4rows` column, compared against the r85 receipt | predicate narrowed to the two flag-sweep classes and the after receipt re-filed (A0.2) |
| M3 | wording overreach: the prereg's limit said the sweep "sees a concealed gitlink commit"; it reads an entry (mode 160000 + flag) and never submodule state — the same row fires when the nested HEAD never moved | `.ufo/waves/round-86/w1/S86Critic.md` C2-b; `S86ExecK4.md` §3(h)/§2(m) | the critic's wording attack plus the executor's no-movement control | A2 narrows the sentence to "reads a gitlink ENTRY carrying a non-`H` flag" |
| M4 | coverage overclaim: C1's "one row per clause … drops exactly those clauses" read as clause-level certification, but NF-Y exercises only the `len(want) < 2` arm and NF-W only a `w[0-9]+` shape — two strictly weaker counters score 8/8 | `.ufo/waves/round-86/w1/S86Critic.md` C1-c (want-only guard; w-shape-narrowed census branch) | the critic's weaker-rule construction, which the battery can score | A3 narrows the certified surface to the two arms/states the rows actually exercise |
| M5 | branch citation: the writer's `FLAGFAIL` message is not reachable for a corrupt index — K4's own `git status` read fails first and reports `status-failed` | `.ufo/waves/round-86/w1/S86ExecK4.md` §2(c) | the executor's corrupt-index probe | A5 records the branch's real reach; no claim cites it |
| M7 | inherited-precondition gap: the C2 repair routed its flag sweep through the writer's `git()` helper and inherited the writer's implementation but not the writer's preconditions — the writer refuses `GIT_CONFIG_*`/`GIT_INDEX_FILE` at its own entry point, which the `exec()`-the-source bootstrap never reaches, so a caller environment (or a repo-local `core.sparseCheckout`) made `ls-files -v` report `H` for a skip-worktree gitlink and K4 returned a CLEAN verdict on the class the repair exists to catch | `.ufo/waves/round-86/w1/S86Sentinel.md` §2 (probes I1/F5/K1/L1); the frozen counter's `ENV` strips `GIT_*`, so it could not see it | the sentinel's config-view table and its env-route probe, which the L1 re-ran as `census/round-86/records/c2-env-route.txt` | repaired in-round (A11): `git_env()` strips `GIT_INDEX_FILE`/`GIT_OBJECT_DIRECTORY`/`GIT_ALTERNATE_OBJECT_DIRECTORIES`/`GIT_REPLACE_REF_BASE`, the child subprocess gets that environment, and the sweep pins `core.sparseCheckout=false`; `k4_rows_with_env` 0 → 1 on the KG1 class |
| M6 | instrument-docstring drift: the battery's own docstring says a pin mismatch is "2 on usage, a pin mismatch, an edit that does not apply exactly once", but the pin-mismatch path raises `SystemExit("BATTERY-FATAL: …")` and exits 1 (the mutant-edit path does `return 2`) | `.ufo/waves/round-86/w1/S86ExecC1.md` §3, receipt `S86ExecC1/pinr/` | the executor's one-byte pin attack, which recorded the actual exit code instead of the claimed one | left as filed (the C1 receipts bind the battery's bytes, and changing them now would break the binding the round's own A5 rule requires); the claim's kill rule names EXIT 2 only for the mutant-edit path, which holds. Routed to r87: fix the exit code and the docstring together and re-file the receipts |

## Wave

One v1 wave, 11 seats, policy `scripts/hyaku/ufo-wave-policy.json` (band 8-16): executor×3, mutation-tester, scribe,
scout×2, connector, reviewer, critic, sentinel. Attack seats 4/11 (36 %, over the 25 % floor); connectors 1 (≤2).
Seat verdicts and the falsification ledger are in `.ufo/waves/round-86/claim-falsification.tsv` and the seat reports
(force-added with the round).
