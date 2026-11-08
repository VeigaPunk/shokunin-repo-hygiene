# Round 87 — two clauses r86 measured reachable and unrowed get their rows, and a third candidate is measured already bound (C1 calibration); K4 reads NUL status records, names its writer delegation and keeps the exception line (C2 operability)

Attempt 1 (`SoujiR87`). Lane base `5e288bb3152328f371325d0bf4fee7309d629991` (r86 closed `admitted`; spot-check
`corpus/lessons/round-86-verifier-spotcheck.md`, its five routed defects 5–10 and the status-neutral list D1–D3).
Frozen claims, instruments, predicates and kill rules are in `census/round-87/preregistration.txt`; the wave's
amendments are in `plans/round-87.md`; the pre-file ledger in `.ufo/waves/round-87/claim-falsification.tsv`.

Staged commits: P `77ccef7c5de2ad015f28da70fd58e1156c0f5b73` (instruments, populations, mutants, controls, both before
receipts), F `6ed2d368dc416f6409ac181e0ea45e23da82f89e` (preregistration ALONE), the C2 repair
`6e502c5c05fd3ca4193883921ef0c9b79a7d36a7`, then the after receipts and the integration commits that follow.

## Inherited

The r86 spot-check closed round 86 `ok`, **admitted**, with five routed defects (5 battery pin-exit/docstring drift,
6 dead arms/effective narrowing, 7 carried population gaps, 8 inherited K3 tally row plus the r83/r84 C2 list, 9
citation-precision nits, 10 lesson-vs-plans count mismatch). Answered this round: **7 (partly)** — the two r85-measured
survivors m12 and m16 now have rows, and the third candidate (the `_capture_ok` suffix comparison) was measured and
found ALREADY bound by NF12c, so it was not given a row; m17 (duplicate ledger id), the `_whole` before-byte half and
the `len(want) <= len(have)` half stay carried, and item 7's remaining clauses are named in the prereg's limits.
**8 (partly)** — the inherited K3 row is re-measured on the round tip (`census/round-87/records/c2-real-lane.txt`: the
only mismatch is `K3 corpus/README.md:1017 tally-disagree 3 refused != receipt 0 refused`, and K4 emits no row).
**5** — the C1 battery's pin path and the harness's rev-label list are the only mechanical edits to the r86
instruments, and the round's reviewer re-derives both diffs; the r86 battery's pin-exit/docstring drift itself is not
repaired this round (the r87 battery inherits the r86 docstring, and the claim cites EXIT 2 only for the
edit-does-not-apply-once path, which holds). **6, 9, 10** — routed forward.

No inherited lane leftovers at start (`jj-lane.sh state`: `local=remote=5e288bb3 ahead=0`). `considerthese/` does not
exist in this lane; no shokuknow package was taken (`Assimilation: none`).

**Planner seat.** The L1 holds it (`scripts/hyaku/ufo-wave-policy.json` `lanes[]` has no `planner` id); the wave's
planning data-walk rode the connector and the two scouts.

## Gate

Sources opened this round (each read here; ids continue the registry after S345):

- **S346 — git-status(1) as installed** (git 2.56.0-1, `/usr/share/man/man1/git-status.1.gz`, capture
  `census/round-87/srcs/git-status.1` sha256 `52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95`,
  opened 2026-11-08). Quote, OPTIONS `-z`, roff line 698: "filenames containing special characters are not specially
  formatted; no quoting or backslash-escaping is performed". **ADMIT**, `docs`, tier A, `mined` — it grounds C2's KN3
  decision rule: the line form hands a parser git's quoted spelling, the NUL form hands it the bytes.
- **S347 — git-grep(1) as installed** (same git, `/usr/share/man/man1/git-grep.1.gz`, capture
  `census/round-87/srcs/git-grep.1` sha256 `52603128b427d0cd8d2bfdc10790958a9d34b8762abc3a3d870504ac3b5b14a6`,
  opened 2026-11-08). Quote, OPTIONS `-F`, roff line 212: "Use fixed strings for patterns (don't interpret pattern as
  a regex)." **ADMIT**, `docs`, tier A, `mined` — `_declared` searches for *paths* containing `.` and `/`; under a
  regex reading the same pattern would match declarations the row never names.
- **Rejected — git-config(1) `core.quotePath`** (same git, opened 2026-11-08). The page names where the quoting rule is
  configured, while S346 already carries the rule for the stream this lane parses. **REJECTED** as a duplicate scope;
  **flip:** a round that must decide which quoting rule a *caller's* config selects.

Census before the appends: `souji ok`, EXIT 0 (`census/round-87/records/sources-census-before.txt`, 88 lines: 87
pre-existing W04 cross-scope duplicate-URL warnings and the ok line); after them: `souji ok`, EXIT 0
(`…-after.txt`), no `E0x` finding. Registry `268 → 270` (`grep -cE '^\| *S[0-9]{3,}' corpus/SOURCES.md`): two rows
added, one rejected, zero removed. Both admitted rows are cited by
`corpus/knowledge/machine-parsed-path-spelling.md`.

## Measured

- **C1 (calibration).** Population `census/round-87/c1-false-rows.tsv` sha256 `b066fa0f…` (51 rows = the r86 49
  byte-for-byte, in order, plus TQ1 and NE1; the prefix audit is `census/round-87/records/c1-prefix-audit.txt`);
  items `c1-items.tsv` sha256 `ce80195d…` (the r86 four byte-for-byte plus I87E, base 705fa138); mutants
  `c1-mutants.json` sha256 `9368b342…` (the r86 eight byte-for-byte plus m12-token-on-line and m16-nf6b-punct).
  After, `--only r86,r87 --expect-killed 18`: `ARM pristine pop=r86 rows=49 mismatches=0 errors=0` and
  `ARM pristine pop=r87 rows=51 mismatches=0 errors=0`, ten `killed=yes` on r87,
  `SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18`, EXIT 0
  (`census/round-87/records/c1-after.txt`). Before, the do-nothing control `--only r86 --expect-killed 8`:
  eight `killed=yes`, `m12-token-on-line killed=no`, `m16-nf6b-punct killed=no`, `killed_r86=8`, EXIT 0
  (`census/round-87/controls/c1-before.txt`).
- **C1 negative result.** `c8-capture-suffix` (the `_capture_ok` suffix comparison) is killed by the existing r86 row
  NF12c on the 49-row population (`census/round-87/records/c1-c8-measured.txt`, `rows=49 mismatches=1`), so the
  planned NF-Z row was removed before the freeze. Q162 records the rule.
- **C2 (operability).** Tool before `census/round-87/controls/c2-before-base-tool.py` sha256 `cf875367…` with its
  byte-identical writer `70bbf1c2…` beside it; after `tools/souji-record-agreement.py` sha256 `0ad9e3bf…`. After:
  `SUMMARY rows=12 mismatches=0 errors=0`, KN1/KN2/KN3 `named=yes`, KN2's header `writer_sha=70bbf1c2a92e
  appended_sha=1b8ecf328ed3`, the nine r86 rows unchanged, EXIT 0 (`census/round-87/records/c2-after.txt`). Before:
  `SUMMARY rows=12 mismatches=3 errors=0`, KN1/KN2/KN3 `named=no`, EXIT 1 (`census/round-87/controls/c2-before.txt`).
  Real lane at `6e502c5c`: K4 emits no row; the only mismatch is the inherited K3 tally row
  (`census/round-87/records/c2-real-lane.txt`).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | padding risk: the round planned a third row (NF-Z) for a clause an existing row already bound | `census/round-87/records/c1-c8-measured.txt` (`rows=49 mismatches=1`, killer NF12c) | the Q162 rule (score the candidate mutant before adding the row) and the mutant-first measurement it requires | the row and its mutant were removed before the freeze; the negative result is filed and the prereg records it (A0.1) |
| M2 | chronology: both after arms were first run while the freeze was being written | `census/round-87/controls/prefreeze/`, F committer time 06:47:35 vs run times 06:47:19 (C1) and the same minute (C2) | the freeze-before-scoring rule (r63 M2) and the commit timestamps it leaves | pre-freeze runs kept as disclosure, not filed as evidence; the receipts were re-run after F (A0.2) |
| M3 | instrument defect caught before the receipts were treated as data: the KN3 row compared `(record, class)` while the status characters live in the detail cell, so a correct record scored `named=no` | `plans/round-87.md` A0.4; counter sha256 `4e2b7c06…` | the row-by-row reading of the first after receipt (one mismatch with the record present) | the row compares all three cells exactly; both arms were re-filed on the corrected counter bytes |
| M4 | validator fact: the wave policy's `SWARM_ROLES` has no `labrat`, so the planned dead-arm probe would have been refused at dispatch | `~/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs:265`; `plan --spec` error `unknown_role` | the validator's own refusal, which fires before any seat spawns | the item moved to `S87Simplifier` (permitted role) with the same hypothesis; recorded as A0.3 |
| M5 | fixture-path citation class: the r86 knowledge entry cites `census/round-84/w1/...` and `census/round-83/waves/...`, which are harness-fixture paths and read as dangling lane pointers | `tools/souji-landing-gate.py` at `6ed2d368` (three LG-DANGLING-PTR findings on those paths) | the landing gate's pointer check | an append-only correction section was added to `corpus/knowledge/own-tree-pointer-binding.md` naming them fixture-only |
| M6 | repair-harm caught by the wave: the first `-z` status arm read the stream in text mode, so a path that is not valid UTF-8 raised `UnicodeDecodeError` and the tool emitted no counts line and no K4 row — a genuine uncommitted change became invisible, strictly worse than the quoted spelling it replaced; two lesser shapes (CR translated to LF, a rename source admitted as a status record by a content test) rode the same read | `.ufo/waves/round-87/w1/S87ExecC2.md` HIGH-1/MEDIUM-1/MEDIUM-2; `census/round-87/controls/c2-byte-arm-before.txt` (`rows=3 mismatches=3`, KB1 `counts=no`) | the wave's own adversarial read of the repair, plus the byte-arm probe it forced (`census/round-87/c2-byte-arm.py`) | the status arm now runs `git_bytes()` and decodes at the record boundary with `backslashreplace`, skips a rename's second field by the `R`/`C` status letters, and keeps a CR as CR; `census/round-87/records/c2-byte-arm-after.txt` reads `rows=3 mismatches=0` (commit `578cbf2c`, plans/round-87.md A1) |
| M7 | limits incompleteness: the prereg's stated limits named three unrowed halves and left four more (the token-on-line basename granularity, the `_whole` after-byte lookahead, `_regular`'s symlink leg, `token_ok`'s hyphen marker) unnamed — a reader would have taken the named list for the complete one | `.ufo/waves/round-87/w1/S87MutCounter.md` §4/§6 (p2, p3, p7, p8 all `killed=no` on both populations, each with a differential probe; p6 `bool(want)` measured dead over 161,472 pairs) | the mutation-tester's probe set — a limits list is a claim about the *complement* and needs the same single-edit sweep as the rows | the four survivors are named in `plans/round-87.md` A4 and carried to r88 with their binding-row designs; p6 is retired as dead |
