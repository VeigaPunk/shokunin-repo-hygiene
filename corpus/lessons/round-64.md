# Round 64 — honest stop: no preregistration frozen, no claim admitted

Base `ae2f4ece2c936ecd8c4260632ad7330c84f7882d` (lane master at round start, clean, pushed). Wave: one v1 wave of
12 seats, `.ufo/waves/round-64/w1/` (dispatched via the inline handoff, spawned 2026-11-05 08:06:31). Outcome:
**both declared claims are NOT admitted and NOT frozen.** The production writer, `SKILL.md`, `tools/` and the
knowledge entries are unchanged this round. Frontier rows S295 and S296 landed. Mistakes M1–M7 are mined below.

## Claim

Declared intent (wave context, dispatched before any seat ran; no predicate frozen):

- **C1, operability.** In-run content snapshot under `--allow-dirty`, a `GIT_INDEX_FILE` refusal, and toplevel
  (`:(top)`-scoped) index reads for `tools/souji-receipt-write.py`. Candidate: sha256 `46a9388b…619a63b`
  (`.ufo/waves/round-64/w1/S64ExecWriter/souji-receipt-write.py`, selftest 26/26 in the seat run).
- **C2, calibration (lowest owned axis, score 7).** Three SKILL.md statements about the writer's enforced scope
  agree with the writer bytes in both directions.

Not admitted, for these reasons (each a Mistake below): the C1 frozen matrix has an unresolved row (N4: the design reviewer and the counter's fixture disagree on base reachability, M1);
the candidate and counters were executed by seats before any predicate existed (M2); the counter's receipt
header is mangled (M3); and the C2 kind-only and decoy controls cite revisions that exist only in a seat's
scratch clone (M4). Candidate scores are diagnostic only and are not admission evidence.

## Gate

Sources opened 2026-11-05 by the scout seat `S64ScoutSources`; captures committed at `census/round-64/sources/`
(`quote-check.txt` lists every offset and its slice assertion).

- **S295 admit** — git(1) `GIT_INDEX_FILE`, https://git-scm.com/docs/git, § ENVIRONMENT VARIABLES › The Git
  Repository › GIT_INDEX_FILE; accessed 2026-11-05; HTTP 200 (244227 bytes; sha256 `534c674f…f9d1`). Located quote
  (17 words, byte-contiguous): `This environment variable specifies an alternate index file. If not specified, the
  default of $GIT_DIR/index is used.` Proof: `census/round-64/sources/s295-located-quote.txt` offset 113; slice
  `[113:230]` equals the quote (assertion PASSED); second carrier `s295-git-man.txt` offset 30767 (PASSED). Scope:
  what the variable names. Not a rule about what a consumer must do with it.
- **S296 admit** — gitglossary(7) PATHSEC magic word `top`, https://git-scm.com/docs/gitglossary, § PATHSEC magic
  words, entry `top`; accessed 2026-11-05; HTTP 200 (109997 bytes; sha256 `216bc0df…f0129`). Located quote (18
  words, byte-contiguous): `The magic word top (magic signature: /) makes the pattern match from the root of the
  working tree`. Proof: `s296-located-quote.txt` offset 43; slice `[43:140]` equals the quote (PASSED); second
  carrier `s296-gitglossary-man.txt` offset 15869 (PASSED). Scope: the magic word's meaning only.
- **Named limit on S296 — the literal `:(top)` is not on the page.** `grep -rn -- ':(top)'` over the git v2.56.0
  tree exits 1 (0 hits), and 0 hits over 60 fetched git-scm.com command pages. The page states the word and the
  long-form rule as separate sentences. Composing them is the reader's step. The binding is code:
  `pathspec.c` v2.56.0 line 106 `{PATHSPEC_FROMTOP,'/',"top"}` and `parse_long_magic()` line 333 (copy at
  `census/round-64/sources/git-2.56.0-pathspec.c`). A dedicated code-kind row is routed to round 65; this round
  keeps the binding as a named limit on S296.
- **Rejected inference (discernment sample, recorded not admitted).** "GIT_INDEX_FILE must be refused or scrubbed
  by any consumer that reads an index." Rejected: S295 states only what the variable does; a consumer's duty is
  not on the page. Flip: a git(1) or gitglossary(7) sentence that assigns that duty to tools.
- **Rejected inference.** "`:(top)` is printed on the git-scm.com page." Rejected: the literal is absent (see the
  named limit above). Flip: the literal appearing in a fetched page's bytes at a revision the lane can cite.
- **D1 correction (round-63 S294 offsets) — see `corpus/lessons/round-63.md`, appended section.** The scout's
  mechanical proof: the S294 quote sits at committed-capture raw offset 109094 (`.html`) and committed-text offset
  31190 (`.txt`). The round-63 values 31053 and 109019 are wrong; the 13-word sentence is not byte-contiguous in
  either capture (a source line-wrap sits between "commit in" and "another"), so only a whitespace-tolerant
  first-word offset is well-defined.
- **D2 (S294 `used-by` duplicate)** — old `corpus/lessons/round-63.md, corpus/lessons/round-63.md` → new
  `corpus/lessons/round-63.md`. Cited set unchanged. Logged here as the required old→new record.
- **Frontier step.** S295 and S296 are opened this round and cited by this lesson (sourced-claim duty). The
  C1 claim's evidence trail rests on them. Id S293 remains a hole (drafted and ruled out in round 63); S295/S296
  continue after S294.
- **Assimilation: none.** `considerthese/` does not exist in this lane (`ls` exit 2). The connector seat
  `S64ConnectorOverlap` read `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` read-only; no theme was
  adopted this round.
- **Non-author spot-check:** pending for S295, S296 and this lesson's diagnostic numbers (`## Gate` is not
  admitted as claim evidence).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | frozen-matrix row realizability disputed: N4 (subdirectory `--root`, skip-worktree forgery outside the subtree) is reported unreachable at base by the design reviewer (its `cat-file rev:rel` reads `rel` repo-root-relative, so a subtree `--root` fails "absent at" first; H1), but the counter's own N4 fixture (`census/round-64/c1-counter.py`, which places instrument copies in the subtree) gives `base=accept`. The provisional 8/3 count therefore has an unresolved row and is not claimed as 7. The freeze cannot proceed until one fixture is probed against the other | `.ufo/waves/round-64/w1/S64ReviewerDesign.md` H1; `census/round-64/controls/c1-do-nothing.txt` (`N4 … base=accept`); `.ufo/waves/round-64/w1/S64CriticClaims.md` | none — the M1 probe duty (r63 routed fix 2) existed, but the wave wrote the provisional count before any fixture was probed against both writers | disagreement routed round 65; N4 is not frozen; the chosen fixture must be probed in both shapes and both results committed |
| M2 | chronology: the candidate writer and counters were executed by seats (selftest 26/26; r60/r62/r63 regress; sentinel re-run; five mutation kills) before any preregistration existed. Same class as round-63 M2 | `.ufo/waves/round-64/w1/S64ExecWriter/selftest.txt`; `.ufo/waves/round-64/w1/S64MutKill/kills.txt`; `.ufo/waves/round-64/w1/S64SentinelScope.md` | none — `tools/souji-freeze-check.py --chronology` (S64ExecFreeze) is a candidate, not landed, so nothing enforces "scored after freeze" | pre-freeze runs are diagnostic only. The chronology arm is routed round 65 and must land before the next freeze |
| M3 | counter receipt header mangled: the C1 counter's `command=` line abspath-joined every argv token, flags included (for example `/home/vgpnk/Projects/shokunin/--root`), so the do-nothing receipt cannot be re-run as written | `.ufo/waves/round-64/w1/S64ExecCounterC1/controls/c1-do-nothing.txt` line 4; `census/round-64/c1-counter.py` `main()` command builder | none — `freeze-check --substance` only requires that `command=` mention the counter path, which the mangled line does | command builder changed to join argv as invoked; C1 do-nothing regenerated under `census/round-64/controls/` |
| M4 | C2 kind-only, positive-synthetic and decoy control receipts cite revisions (`ee7fbe5a…`, `769d9b2c…`, `e9ac1fcd…`) that exist only in a seat's scratch clone, not in the lane history, so no chronology check can bind them | `.ufo/waves/round-64/w1/S64ExecCounterC2/controls/revs.txt`; `c2-kind-only-forgery.txt` header | none — the freeze check reads only the named Control file, which passes | those receipts are disclosed as out-of-lane evidence. Routed round 65: build every control in the lane as a commit strictly before the freeze |
| M5 | N2 fixture false-realizable: an EMPTY untracked directory produces a row whose base and candidate outcomes differ from the frozen expectation (reviewer H2). A symlink inside an untracked directory is also unhandled by the frozen design (reviewer, "H-if-followed") | `.ufo/waves/round-64/w1/S64ReviewerDesign.md` H2 and symlink item | none — the wave design was written before the reviewer's fixture probe | routed round 65: non-empty directory fixture; explicit symlink rule (record name, never follow) |
| M6 | registry teaches cell overclaimed: a draft S296 row said the page documents the long form `:(top)`. The scout's named limit disproved it (0 hits on the page and in the tree) | `.ufo/waves/round-64/w1/S64ScoutSources.md`; `corpus/SOURCES.md` S296 row | the scout's exhaustive grep (caught before the append) | the row's teaches cell now states only what the page says; the `:(top)` composition is named as the reader's step |
| M7 | round-63 quote-location error recurrence (round-63 M4 class): the S294 offsets recorded in `corpus/lessons/round-63.md` were not mechanically verified and are wrong (31053/109019 versus 31190/109094) | `.ufo/waves/round-64/w1/S64ScoutSources.md` (D1); `corpus/lessons/round-63-verifier-spotcheck.md` §5 D1 | the round-63 closure spot-check (outside the lane) | appended correction in `corpus/lessons/round-63.md`; the original text is not rewritten |

**Sweep for mistakes (run at round end):** `grep -c 'closed in round 62 by C1' SKILL.md` → 1 (round-62 R1 overreach still
at base; routed, not edited). `grep -c 'a flag set, or a file edited, while the wrapped command runs is not checked' SKILL.md`
→ 1 (the in-run gap is still stated open at base, which is true for the base writer). Both are base-bytes facts, not regressions.

## Named limits (carried as observed; none claimed)

- **Untracked-visibility blindness (MEDIUM, sentinel S64-F1; reproduced by the writer seat).** An operator-injected
  `status.showUntrackedFiles=no` hides untracked files from every porcelain check, and the writer accepts. The base
  writer has the same hole. Not applied this round: it is outside the three frozen deltas, and `--untracked-files=all`
  would newly refuse honest runs that the base accepts. Routed round 65 with its own predicate and regress rows.
- **Allow-dirty content (round-63 F1, HIGH).** The candidate's content snapshot addresses in-run appends to dirty files and new files in
  untracked directories (seat rows N1, N2). Its handling of symlinks inside untracked directories is not frozen and is
  routed (M5).
- **`GIT_INDEX_FILE` edge cases (probe P13/P14 in the scout log).** A nonexistent path makes `ls-files -v -z` print nothing and
  exit 0, so the base flag loop passes vacuously. An empty file is fatal (exit 128). A relative path was not probed.
- **`:(top)` binding is code, not page (S296 named limit).** Probes covered `git ls-files` from a subdirectory; sparse
  checkout, submodules and worktrees were not probed.
- **Pre-freeze diagnostic runs** (M2) are not admission evidence for any claim.
- **C2 population is three SKILL.md sentences.** A kind-only forger editing only `corpus/knowledge/` is outside it by design
  (round-63 M3 rationale). Green and decoy controls exist only as out-of-lane revisions (M4).
- **Axis tie-break and MACHINE BLOCK (operator L0 open).** `.ufo/l0-questions.md` lines 324–325 and 335–336. Routed
  around; not answered.
- **Planner seat (round-63 spot-check D3).** The validator refuses a planner role; the L1 holds the planner seat. Recorded
  again this round; an explicit operator L0 line is appended.

## Routed to round 65

1. Re-declare C1's matrix with probed realizability: N4 re-shaped to a base-reachable case or dropped with a named limit
   (M1); N2 with a non-empty directory (M5); a symlink-in-untracked row with the record-name rule; the P13
   nonexistent-index row (named limit above).
2. Build every control in the lane as a commit strictly before the freeze; regenerate C1 and C2 receipts from the fixed
   command builder (M3, M4). Keep the stub rejections (accept, refuse, message-without-token) as first-class rows.
3. Land `tools/souji-freeze-check.py --chronology` with its historical sweep before the next freeze (M2). The candidate
   is `.ufo/waves/round-64/w1/S64ExecFreeze/souji-freeze-check.py`; its default output must stay byte-identical.
4. C2: add a green/decoy control and a row-presence pin; cover the s3 unmerged clause; the after-patterns are the counter
   literals `S2_AFTER` and `S3_AFTER` (`census/round-64/c2-counter.py`).
5. Untracked visibility (named limit above) as its own claim with a do-nothing control.
6. Carried from round 62 and 63: R1 (SKILL.md:830 overreach), R3 (knowledge-entry `verified-at` refresh), the operator L0 lines,
   and the round-63 spot-check D3 (planner seat).
7. A code-kind registry row for pathspec.c `parse_long_magic` (S296 named limit), tier A, if the operator accepts code rows.

## Integrated verification

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` at round end: exit 0 is required; the
  before/after counts are in the report.
- Freeze checker: not run this round (no preregistration). The next freeze must run `--substance` and `--chronology`.
