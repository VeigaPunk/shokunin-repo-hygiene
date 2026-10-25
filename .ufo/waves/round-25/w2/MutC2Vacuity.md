# MutC2Vacuity — 8 additional size-census tool mutants vs the C2 12-case fixture (souji r25, wave 2)

Seat: L1Souji25.MutC2Vacuity (mutation-tester, leaf). Attack target: C2 (operability) frozen counter
`python3 -B tests/fixtures/r24-size-census.py --tool <path>` extended to 12 cases
(preregistration.txt:64-76, amendments 1-3; canonical W1 draft `.ufo/waves/round-25/w1/r24-size-census.py`,
sha256 `5bd7e74f...`).

## Status
STATUS: PASS — 8 new clause mutants designed around the six assigned foci, scored against the 12-case
fixture. 7 survive; 1 is killed. Baseline (pristine tool) scores 12/12 rc 0; the stub control is
rejected (`control=FALSE-GREEN-REJECTED`, `lost_found=WRITE-DETECTED`) in every run. All 7 survivors are
non-equivalent: each has a minimal witness where pristine and mutant diverge (witness.out).

## Method (scratch only)
- Scratch `/var/tmp/souji-r25-MutC2Vacuity/` (removed at the end). Lane reads only: tool and fixture
  bytes copied out, verified byte-identical by sha256:
  - tool `tools/souji-size-census.py` = `c5690681b4e86afd4a2a019847c8d18315cea51c2d58d67b3cbc1260143a6eb3`
    (blob `182001db` @ a6d2d15, the lane worktree bytes).
  - 12-case fixture (canonical W1 draft) = `5bd7e74fb7344e2b583858eaeee761272aadc0d3a0a4cfbbec89fd8f68754238`.
    Cross-checked against the lane-committed `tests/fixtures/r24-size-census.py`
    (`9c8a512f...`) — identical verdicts on every mutant (score2.tsv).
- Every mutant built by exact string replacement of the freshly-read baseline bytes, with a per-edit
  occurrence assertion (`== 1`); pristine never edited. Detector per tool:
  `python3 -B <fixture> --tool <tool>`; baseline failure would be inconclusive — baseline passed
  (12/12, rc 0), so no inconclusive verdicts.
- Environment: git 2.56.0, Python 3.14.8. Runs: 9 tools × 2 fixture variants; each full sweep ran
  twice (score.tsv, score2.tsv) with identical verdicts. No git/jj mutations, no lane writes except
  this report; nothing installed.

## Mutants, verdicts, witnesses

| # | Focus (assigned) | Smallest behavior-bearing mutation (baseline line) | 12-case | Failing case | Minimal witness (pristine vs mutant) |
|---|---|---|---|---|---|
| M1 | case-10 stderr wording | `fail_text` frame `exited {rc}:` → `returned rc {rc}:` (:113) | 12/12 SURVIVES | — | bare-empty repo stderr: pristine `...fsck ... exited 0: notice: No default references` vs mutant `...returned rc 0: notice: No default references`; both keep `git failure` + `No default references`, rc 1, no stdout |
| M2 | case-10 stderr wording | failure prefix `git failure:` → `git-error:` in `main()` (:231) | 11/12 KILLED | 10 bare-empty (`git_failure=False`, `no_default_refs=True`) | same bare-empty input; `git failure` substring disappears from stderr |
| M3 | bad bare label | `census.invoked_from=` emitted only when `invoked_from == "bare"` (:212-214) | 12/12 SURVIVES | — | plain main repo: pristine prints `census.invoked_from=main`; mutant omits the line (rc/counts identical) |
| M4 | alternates | drop `census.unreachable_scope=includes-alternates` disclosure line (:217-218) | 12/12 SURVIVES | — | main repo with one alternate: pristine prints `census.unreachable_scope=includes-alternates`; mutant does not (`garbage=0 size_garbage=0 unreachable=3 alternates=1` identical, rc 0) |
| M5 | promisor remote | `remote.*.promisor` refusal drops the value check (`== "true"` → unconditional) (:171-173) | 12/12 SURVIVES | — | plain repo + `remote.origin.promisor=false`: pristine rc 0 census; mutant rc 2 `refused: promisor remote (remote.origin.promisor false)` |
| M6 | common-dir resolution | `census.common_dir=` prints `os.path.dirname(common)` instead of common (:213) | 12/12 SURVIVES | — | plain repo: pristine `census.common_dir=.../repo/.git`; mutant `census.common_dir=.../repo` (worktree root), same counts/rc |
| M7 | stdout counts | `count.<k>=<v>` detail lines dropped (:215) | 12/12 SURVIVES | — | plain repo: pristine emits 8 `count.*` lines; mutant emits none (aggregate `garbage=0 size_garbage=0 unreachable=0 alternates=0` last line identical) |
| M8 | stdout counts | aggregate counts line appended twice (:219-221) | 12/12 SURVIVES | — | plain repo: pristine one final `garbage=0 ... alternates=0` line; mutant two identical final lines (last-line fullmatch unaffected) |

Totals: killed=1 (M2 by case 10), survived=7, inconclusive=0. Both fixture drafts agree.

## Findings
1. **Case 10 (bare-empty) pins the `git failure` prefix, not the failure frame.** M2 dies because the
   `git failure` substring vanishes; M1 survives because only the frame wording changes while git's
   `notice: No default references` passes through verbatim. The frozen predicate (`'git failure' in
   stderr`, `'No default references' in stderr`, rc 1, no counts line) therefore constrains the prefix
   string and the verbatim git stderr, but nothing else in the failure report. Tool :113/:231.
2. **The bare label is pinned only positively.** Case 9 requires `census.invoked_from=bare`; no case
   asserts `=main` or `=linked`. M3 (label line missing for main/linked) survives — consistent with W1
   survivors M3 (always `bare`) and m19 (linked labelled main), but a distinct clause: the emission
   condition itself. Tool :212-214.
3. **Alternates reporting is pinned only through `alternates=1`.** Case 5 asserts `counts[3]==1` and
   manifest unchanged; nothing asserts the `census.unreachable_scope=includes-alternates` line, so M4
   (dropping it) survives. The earlier dict-collapse variant (count via `dict(fields)`) was killed by
   case 5 — `alternate:` values are paths, not counts, so `int()` raised ValueError (exit 1, traceback)
   — recorded as a design dead-end, not a survivor. Tool :217-218.
4. **The promisor-remote clause is unreachable in the fixture** — W1 finding 3 (m14) reproduced from the
   opposite side: M5 keeps the clause but breaks its value semantics, and still passes, because case 8's
   clone always carries `remote.origin.promisor=true` or (after unset) a `.promisor` pack; case 12 has
   no remote. A `remote.*.promisor=false` repo (legitimately disabled promisor) is censused by pristine
   and refused by M5 — the distinguishing input. Tool :171-173.
5. **`census.common_dir=` is unverified output.** M6 reports a wrong common dir (worktree root) and
   still passes 12/12; the fixture's manifest is computed over the fixture's own `rev-parse` common dir,
   and no predicate reads the tool's `census.common_dir` line. Tool :213.
6. **The aggregate counts line is the only stdout contract the fixture enforces.** M7 (all `count.*`
   detail lines dropped) and M8 (aggregate line duplicated) both survive: `has_counts` searches any line
   and the per-case parse `fullmatch`es only the last line. No uniqueness, no count line
   presence/count assertions. Tool :215, :219-221.

## Attack log
- A1 M1 wording-frame rewording → SURVIVES (verified via witness; case 10 still PASS).
- A2 M2 prefix rewording → KILLED by case 10 (only kill; proves the wording check discriminates).
- A3 M3 label emission conditional → SURVIVES (witness: main repo label line absent).
- A4 M4 alternates-scope line drop → SURVIVES (witness: line absent with alternate present).
- A5 M5 promisor value semantics broken → SURVIVES (witness: `promisor=false` refused).
- A6 M6 wrong census.common_dir → SURVIVES (witness: root printed for .git).
- A7 M7 count.* detail lines dropped → SURVIVES (witness: no count.* lines).
- A8 M8 duplicated aggregate line → SURVIVES (witness: two final counts lines).
- Baseline runs: 12/12 rc 0 on both fixture variants; control flags correct on every run; no baseline
  failure → no inconclusive verdicts.

## Restoration evidence
Lane untouched: `tools/souji-size-census.py`, `w1/r24-size-census.py`, `tests/fixtures/r24-size-census.py`
sha256 unchanged after all runs (final integrity check). Scratch baseline `baseline.py` re-hashed
`c5690681...` after the sweep (identical to the lane tool). Mutant hashes before scoring are recorded in
the table (generation step): M1 `ed51b95e...`, M2 `c9ef0cbe...`, M3 `a30fb7c5...`, M4 `66ac3b19...`,
M5 `d87e3b51...`, M6 `050e2207...`, M7 `2370bf5f...`, M8 `5b6dc2f9...`. Scratch
`/var/tmp/souji-r25-MutC2Vacuity/` removed at the end.

## Bound note
All 7 survivors are coverage findings for the frozen C2 case set — the claim's predicate, case set and
target are unchanged; admission belongs to L1. The commit identical is as-is; no candidate case or gate
is proposed inside this report (case set is frozen).
