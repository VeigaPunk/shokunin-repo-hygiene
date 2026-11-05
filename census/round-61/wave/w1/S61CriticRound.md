# S61CriticRound — critique of the round-61 claim plan (not the code)

Seat: S61CriticRound (critic, leaf). Lane: souji (`/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `c7228424`).
Scope: the round's claim plan (`.ufo/waves/round-61/w1-spec.json`, Goal section) attacked for chronology, do-nothing
reachability, kill-rule completeness, axis assignment and preregistration completeness. No production file was edited;
no lane git mutation was run; probes ran in fixture repos under scratch. Receipts: `.ufo/waves/round-61/w1/S61CriticRound/`.

## Verdict

The plan is **not admissible as written**. Its C1 chronology rule, as literally specified, (a) is root-dependent,
(b) is blind to rewrites and delete/re-add at the freeze commit, (c) makes every r60-shaped honest control refuse, and
(d) cannot be scored correctly by its own counter. C2 is a **coverage** claim (fixture expansion over edge classes) declared
as **operability**, which the lane's own `souji-axis-check.py` R2 rejects. Both fixes are small; both must land before the
L1 freezes. Severity: C = blocks freeze; H = wrong result or misattribution if unfixed; M = weakens the falsifier; L = hygiene.

## Findings

### F1 [C] The literal Q120 command walks HEAD, not the freeze; the "orphan non-ancestor" case is not constructible from the freeze walk
- Spec: `git log --diff-filter=A --no-renames --full-history -- <control-receipt-path>` has **no rev**, so it walks the lane's
  checked-out HEAD. That is the "current HEAD" dependence that Q48 forbids (`corpus/QUALITY.md` Q48: "cannot depend on … its current HEAD").
- Evidence (`probe_chrono.py` → `chrono-rule.txt`): the same freeze-born receipt set gives different verdicts depending on the walk root.
  S4 (post-freeze delete + re-add on landing L): walk from L, newest-first → REFUSE; walk from freeze B → ACCEPT (the receipt bytes at B were committed before B; the post-freeze re-add is irrelevant to the frozen blob).
- Why the orphan case fails: `git log <freeze> -- path` lists only ancestors of freeze. A non-ancestor add commit can therefore only be seen from a walk root other than freeze. If the orphan case carries a valid full-40 `rev=`, base already refuses it as `CONTROL-REV-NOT-BEFORE-FREEZE` (`tools/souji-freeze-check.py` L269–271), so it does not count as a chronology discriminator, and the spec's own "base scores new_forgeries=2" would not hold.
- Fix: walk from the freeze commit, never HEAD. Use last-touch (F2 fix). Replace the orphan case with a freeze-walk-constructible shape (S2 / S3 below). Add a matrix case where lane HEAD ≠ freeze (every r60 fixture has HEAD == freeze, so the matrix cannot detect a HEAD-walk; `build-matrix.py` `build_case` ends at freeze).

### F2 [H] The add-commit rule is blind to rewrites: a receipt added green in A and rewritten red in the freeze commit is accepted
- Evidence (`chrono-rule.txt` S2): literal rule → `ACCEPT add=3690f1b1`; blob(A) `4eaac35d` ≠ blob(B) `f7879e4e`. `--diff-filter=A` returns only the first add; a modification at B is never seen. The existing FROZEN-EDITED check (`evaluate`, L336–337) compares freeze vs rev only, never A vs freeze.
- Impact: the frozen (red) bytes were authored at freeze, which is exactly the r60 failure shape, and the claimed arm passes it. The matrix as planned has no rewrite shape, so new_forgeries can be 0 with this hole.
- Fix (verified in `chrono-rule.txt` F''): `last=$(git log -1 --format=%H --no-renames --full-history <freeze> -- <path>)`; refuse `CONTROL-ADDED-NOT-BEFORE-FREEZE` when empty-as-missing, equal to freeze, or not an ancestor. This is "the freeze commit does not itself change the receipt". It accepts S2-pre-freeze rewrites (H2: `ACCEPT`), refuses S1/S2/S3, and accepts the honest shape (H: `ACCEPT`). Add S2 and S3 as frozen matrix rows.

### F3 [H] Delete + re-add at the freeze commit: the freeze_rev ordering pattern accepts the forgery
- Evidence (`chrono-rule.txt` S3): add list newest-first = `e2c99e71 8908b3eb`. Newest pick → REFUSE. `--reverse` oldest pick (the pattern `freeze_rev` uses, `tools/souji-freeze-check.py` L141–144) → **ACCEPT** `8908b3eb`, though the re-add that put the frozen bytes in the freeze commit is the freeze itself.
- Fix: F2's last-touch rule (no ordering choice). If an implementer prefers "exactly one add", it must refuse on ≥2 adds. Never copy `freeze_rev`'s `--reverse`/`ids[0]` into the control check.

### F4 [C] The r60 matrix builder reproduces the r60 failure in fixture form; under the planned rule every honest row is refused
- Evidence: `build-matrix.py` `build_case` (L213–225) sets `freeze_payload = [(PREREG, preb)] + sorted(ctls.items())`, so each control receipt is added by the freeze commit. Rebuilt in scratch (`matrix-r60-rows.txt`; the rebuilt `c1-matrix.tsv` is byte-identical to the committed one): honest-1, honest-2 (both receipts) and honest-3 all → `REFUSE CONTROL-ADDED-NOT-BEFORE-FREEZE` under both literal and F'' rules.
- Consequence: with this matrix, new_honest = 0, so C1's target (`new_honest=3`) is unreachable. The tempting repair (allow `cid == freeze`) reopens r60's failure. The honest repair is to rebuild the matrix with receipts in a commit strictly before the freeze (commit A), which changes the builder, so the r61 matrix is new bytes and must be frozen as such.
- Also required: an honest positive for "legitimate pre-freeze rewrite" (H2) so the rule does not over-refuse.

### F5 [H] C1 is scored on exit codes only: crashes count as refusals, the pinned finding class is not implemented, and base already refuses rev-at-freeze for a different reason
- Evidence: `c1-counter.py` `run_arm` maps exit 0 → accept, exit 1 → refuse (`run_arm`/`main`); `new_ok = new_verdicts == expects` compares verdict only. An uncaught Python exception exits **1** (`python-uncaught-exit.txt`: `EXIT=1`). A candidate that crashes on the two chronology rows scores them as refused. `parse_expected` reads only case/expect/class/ancestor/freeze/prereg/control_rev; `expected.txt` and `c1-matrix.tsv` have no finding-class field, so "per-case EXPECTED FINDING CLASS now pinned" is not implemented anywhere.
- Base already refuses the r60 rev-at-freeze shape: `freezemark` is not FULL40, so `cid=None` → `CONTROL-REV-INVALID` (`tools/souji-freeze-check.py` L266–268). The counter counted that as a chronology kill.
- Fix: refuse-rows require rc == 1 **and** a stdout line `FINDING <claim> <expected-class>`; rc 2 or any traceback never counts. The C2 fixture already does this exactly (`tests/fixtures/r60-receipt-write.py` `rc=... (want 2)`), so copy that discipline.

### F6 [H] The do-nothing arm is mis-specified for r61
- r60 Kill: "the do-nothing arm … `--new-arm plain`, which prints new_forgeries=5". For r61 the plain arm counts every forgery row accepted (7 of 7 with the planned matrix), so it does not test the chronology rule at all. The real do-nothing is the base bytes with `--substance` (c7228424 already contains the substance arm): new_forgeries = number of chronology rows base accepts — 2 for the planned two-row design, 3 once S2 and S3 are added (F2, F3). The plan's text ("base scores new_forgeries=2") is right only for the two-row design; the Kill text is not right for either.
- Fix: pin the do-nothing as `--new-tool <base bytes> --new-arm substance` and pin its printed `new_forgeries=<n>` value (n = chronology rows base accepts, 2 or 3 by matrix) in the prereg.

### F7 [H] C2 is a coverage claim declared as operability; the lane's own instrument refuses it
- Evidence: `AXES.md` coverage = "Fraction of the domain's real surfaces … (repo paths, tools, **edge classes**)". `tools/souji-axis-check.py` R2 maps `fixture-expansion → coverage` only. Machine-block run (`axis-check.txt`, v1): `FLAG C2 R2 surface-class 'fixture-expansion' declared on 'operability'; allowed only on 'coverage'` (exit 1). The C2 surface is two new edge-class cases (concealed-divergence, partial-visibility) in a fixture.
- Precedent: r25 extended the receipt/fixture from 8→12 edge-class cases, declared operability; W2 ruled the surface coverage, and the lesson made C2 unprovable on its declared axis and charged calibration harm (`corpus/lessons/round-25-verifier-spotcheck.md`; `LOG.md` r25 entry). The plan repeats that shape. Q59 says "gate/runnable fixture on an input edge class is an operability surface"; that wording conflicts with the instrument's R2 and with r25, so Q59 cannot be used to defend the label.
- Fix: declare C2 `axis: coverage`, `surface-class: fixture-expansion`, and name the coverage surface (the two edge classes) and its counting command (killed mutants). Note: the coverage score has no re-derivable mapping in `SCORECARD.md` (repeated "score 8 stays" entries), so a coverage move must be stated as a measured count, not a score change.
- With C2 on coverage the round is C1 calibration (lowest axis 7, satisfies R3) + C2 coverage: distinct axes, R1–R3 pass.

### F8 [H] C2's honest half is already met at base; the only discriminating content is fixture and mutant bytes
- Evidence (`c2-mutant-kill-gap.txt`): the **base** honest writer refuses the concealed-divergence repo (`refused: worktree tools/instrument.sh differs from committed bytes at 9a682f57…`, EXIT=2), because `tools/souji-receipt-write.py` L159–174 already compares worktree bytes to `cat-file blob rev:path`. Its publication already uses temp + `os.link` (L244–254), so it already passes partial-visibility in principle. So "honest writer must pass the extended 10-case fixture" requires no tool change.
- Implication: C2 is a test-fixture claim. That supports F7 and means the plan's wording ("honest writer must pass") is not a tool change that could be measured. Do not let the L1 describe C2 as operability work on the writer.

### F9 [H] The partial-visibility kill is timing-dependent; the honest pass can be vacuous
- Evidence (`partial-visibility.txt`, N=40 per arm; a second run gave 6/40): chunked-without-pause mutant seen partial in **5–6/40** trials (≈15 %); the same mutant with a 50 ms pause in **40/40**; honest temp+link **0/40** partial. A plain polling reader therefore does not kill the mutant reliably.
- Vacuity: a reader that never samples OUT passes the honest writer trivially. The continuous reader must also assert it observed a complete OUT at least once.
- Fix: a deterministic handshake, not timing: the mutant writes chunk 1, then blocks until the reader confirms a partial read, then writes chunk 2; the case asserts (a) ≥1 partial observation for the mutant, (b) ≥1 complete observation for honest, (c) never a partial for honest. Pin the mutant bytes by sha256 (see F13).

### F10 [M] The tool under test is bound by worktree, not by the measured revision (Q48)
- `c1-counter.py` L215: `new_tool = … else os.path.join(lane, TOOL_REL)`, i.e. the NEW arm executes the working-tree `tools/souji-freeze-check.py`, while the receipt records `--rev`. The base arm uses `git show <base>:…` (correct). The after receipts show `new-tool=/home/vgpnk/…/tools/souji-freeze-check.py` (r60 `census/round-60/records/c1-after.txt`). The C2 after receipt likewise runs `--tool tools/souji-receipt-write.py` from the worktree. No tool digest is recorded.
- Fix: NEW arm reads `git show REV:tools/…` into `--work`, like BASE; each receipt records `tool_sha256=` of the executed bytes.

### F11 [M] Kill rules are not exact negations; C2 has no mutant-survival clause
- C1 Target: `new_forgeries=0 new_honest=3 stubs=REJECTED`, exit 0. Kill: `new_forgeries>0, new_honest<3, stubs=ACCEPTED, nonzero exit`. The negation of `new_honest=3` is `new_honest≠3`; `<3` misses `>3`. With the r61 positive control, honest rows become 4, so `new_honest=3` is unreachable and the Target must change to 4 (or the positive must be counted separately).
- C2 Target: `pass=8 fail=0`. Kill: `pass<8, fail>0, either control accepted, or nonzero exit`. No clause falsifies "a mutant is killed" at all; `killed_new=2` in the plan has no Kill condition. Fix: one Kill clause per Target conjunct: `either mutant passes the 10-case fixture`, `the r60 fixture kills either mutant`, `honest rc≠0 on any row`, `any row killed by a case other than the named one`.
- Universal clauses: "every forgery refused with its expected class" must be enumerated by the counter (F5), not asserted.

### F12 [H] Do-nothing reachability: C1 and C2 counts can be met without the claimed work
- C1 without chronology work: (i) a candidate that raises on the chronology shapes scores them as refusals (F5); (ii) a HEAD-walk candidate passes the whole matrix because HEAD == freeze in every fixture (F1); (iii) base refuses the r60 rev-at-freeze shape for an unrelated reason (F5). Only the chronology rows discriminate, so C1's measurement rests on those rows alone; each must be pinned to the chronology class, and the rewrite and re-add rows must be added (F2, F3).
- C2 without fixture work: the counts need `killed_new=2`; do-nothing gives 0 (verified: the r60 fixture passes both mutants, `c2-mutant-kill-gap.txt`). The residual route is a fixture case that fails mutants for an unnamed reason. Fix: each killing case name is pinned per mutant; a mutant killed by a different case counts as survived.

### F13 [M] Preregistration completeness (Q99, Q120, Q59, Q70) — what the r60 shape misses and r61 must carry
Required fields for each `## C<n>` block, with the r60 gap in brackets:
1. `Round:`, `Base:` (full-40, strict ancestor of freeze, `c7228424`), `Counter:`, `Population:`, `Control:`, `Target:`, `Kill:` (all present in r60).
2. **`## MACHINE BLOCK … END` with `CLAIM`, `axis:`, `surface-class:`, `enumerate:`** [r60 has none: `souji-axis-check.py census/round-60/preregistration.txt` → `refused: no ## MACHINE BLOCK`, exit 2; Q59 never ran on r60].
3. Population rows with **expected finding class per case** [absent from `c1-matrix.tsv` and `expected.txt`].
4. Control receipts that carry **independent expected rc/findings** alongside observed output (Q120) [r60 receipts record observed EXIT only; r59's `controls.json` had expected values].
5. **Pinned mutant bytes and killing-case mapping** for C2 [no Population for mutants].
6. **Tool-under-test digests** for NEW and BASE arms (F10).
7. **Pinned do-nothing arm and its printed value** (F6).
8. **Feasibility leg (Q70a) and three-run stability (Q70b)** for each counter before freeze [absent].
9. **Stale constants removed**: `c1-counter.py` docstring and `build-matrix.py` say "exactly 8 data rows" and "matrix=8" [hard-coded].
10. **Counter/fixture identity for C2**: the r60 fixture must stay byte-identical (the r60 prereg pins its digest `d5291501…`; the gap demo needs its bytes); the r61 extension is a **new file** (e.g. `tests/fixtures/r61-receipt-write.py`), with its own digest in the prereg.
11. **R4 wording**: `(no --substance)` in C1 text trips R4 (`v2.txt` → `FLAG C1 R4`); add `enumerate:` or reword.
12. Q99 dispatch clause: `.ufo/waves/` is **gitignored** (`.gitignore:1:.ufo/waves/`; `git check-ignore`). `w1-spec.json`, `w1-dispatch.json`, `w1.ready` and any `*-results.json` must not be added at or before freeze (the instrument checks basenames under `.ufo/waves/round-<N>/`). The seat reports under `w1/` need `git add -f` in landing, not earlier.

### F14 [M] No positive real record exists for the real-record arm
- The r61 real-record arm only checks that the candidate refuses r60. A candidate that refuses every prereg carrying a Control line passes it. The only lane record with pre-freeze controls, r59, fails the grammar: base default → `FINDING C0 FIELD-MISSING Round` (EXIT=1); base `--substance` adds `CONTROL-COMMAND-MISMATCH` and `CONTROL-INSTRUMENT-MISSING` (`before.txt` is not an EXIT receipt). So there is no clean real positive.
- Fix: the positive arm is a synthetic Q99-grammatical record whose controls were committed before freeze (the chrono-ancestor control), scored `findings=0` by the candidate and by base. Name it in the prereg as the positive real-record control.

### F15 [M] Plan ordering: the commit sequence has hidden requirements
- The C2 writer refuses a dirty tree (`git status --porcelain`) and an instrument not committed at rev. So the receipts must be produced after the instruments are committed. Sequence the freeze as: **A0** instruments + population + matrix (committed) → run controls at `rev=base` (clean tree) → **A1** receipts → **B** freeze (prereg pins Counter/Population digests of A0's blobs) → **C** tool patch + after receipts. Never regenerate receipts after B; F2's last-touch rule enforces this.
- `git status --porcelain` is blind to `skip-worktree` and `assume-unchanged` (demonstrated: `status-porcelain: []` with a modified tracked instrument, `c2-mutant-kill-gap.txt`). The dirty-tree guard for C1 receipts should compare index to HEAD and worktree to blob.

### F16 [L] C1's axis label is defensible only through the surface class
- C1 calibration is defensible: the r60 report's false "controls committed strictly before the freeze" statement is the overreach the calibration axis is meant to catch (`corpus/lessons/round-60-verifier-spotcheck.md`). But R2 treats `receipt-binding` as neutral and `instrument-acquisition` as operability-only. If the L1 labels C1 `instrument-acquisition` (what adding a finding class to a gate looks like), R2 forces operability and R3 then fails: `v3.txt` → `FLAG - R3 no claim declares the lowest-scoring non-retired axis 'calibration'`. The prereg must name the overreach it catches and state the surface class choice.

### F17 [L] Precedent check the lead asked for
- I did not find a literal "instrument-visibility work mislabeled as calibration" rejection in r56/r57 lessons. Closest documented precedents: r25 (edge-class fixture extension declared operability → coverage; calibration harmed; F7) and r57 (calibration harmed by instrument overreach, not by mislabel). Cite these, not the unlocated phrase.

## Answers to the five questions

1. **Q120 chronology of the planned order.** Yes, it repeats the r60 failure in two places: the matrix builder puts receipts in the freeze commit (F4), and the literal rule cannot see a rewrite or re-add at freeze (F2, F3). The arm **can** see commit A for real r61-shaped history: `git log <freeze> -- <receipt>` lists A (r60 controls resolve to `2670e96a` from `d05a0001`, verified). But the literal command without a rev walks HEAD (F1). The repaired order is in F15.
2. **Do-nothing reachability.** C1 do-nothing (base with `--substance`) gives new_forgeries = number of chronology rows base accepts (2 planned, 3 with S2/S3) and fails the target (verified in logic and by the base-substance refusals on the r60 rows). The counts can still be met without chronology work by exit-1 crashes (F5), HEAD-walk (F1) and wrong-reason refusal (F5). C2 do-nothing gives killed=0 (verified); the residual route is unnamed-kill (F12).
3. **Kill-rule completeness.** Not exact negations (F11). C1 `<3` vs `≠3`; C2 has no mutant-survival clause; the counter enumerates verdict only, not classes (F5).
4. **Axis assignment.** C1 calibration: defensible, but only with the surface named (F16). C2 operability: misattributed; the instrument R2, AXES.md "edge classes", and the r25 precedent all say coverage (F7, F8).
5. **Preregistration completeness.** F13 lists 12 required items; the r60 shape misses at least items 2–9 and 11–12.

## Repaired claim text (minimal, for the L1)

- C1 (calibration, surface `receipt-binding`): the prereg's Counter is `census/round-61/c1-counter.py`; the chronology rule is F'' (last-touch from freeze; refuse if last == freeze or not a strict ancestor; refuse if the path has no touch). Matrix: 4 honest (3 r60 honest + 1 positive H2: pre-freeze rewrite, receipts committed strictly before freeze) + 8 forgeries: kind-only, digest, rev-missing, command-other (base refuses each for its own class); rev-at-freeze kept with expected class `CONTROL-REV-INVALID` (not chronology); three chronology rows that base accepts: S1 freeze-born, S2 rewrite-at-freeze, S3 re-add-at-freeze. The orphan case is dropped (not freeze-walk constructible). At least one row must have lane HEAD ≠ freeze. Do-nothing (pinned): base bytes with `--substance` → `new_forgeries=3` (the three chronology rows; the prereg pins the printed value). Target: new_forgeries=0, new_honest=4, stubs=REJECTED, every refuse row prints `FINDING <claim> <expected class>`, rc 0. Kill: any of `new_forgeries≠0`, `new_honest≠4`, `stubs≠REJECTED`, any row whose printed class differs from expected, any rc≠0. Real-record: base `findings=0` exit 0 on `census/round-60/preregistration.txt@d05a0001` (verified: `real-record-base.txt`); candidate `findings≥2` exit 1 on the same record. Positive real record: a synthetic Q99-grammatical record whose controls were committed before freeze.
- C2 (coverage, surface `fixture-expansion`): new file `tests/fixtures/r61-receipt-write.py` (r60 bytes untouched); 10 cases; `concealed-divergence` and `partial-visibility` with a deterministic handshake (F9); mutant bytes pinned by sha256 and the named killing case per mutant (F11). Target: honest rc 0 with `pass=10 fail=0`; both mutants fail the 10-case fixture on their named case; the r60 fixture passes both mutants (`c2-mutant-kill-gap.txt`, verified). Kill: the negation of each conjunct (F11).

## Limits of this critique

- I did not build a candidate `--substance` implementation or run the lane's `--selftest`; F1–F3 are demonstrated on fixture repos with the rule as specified and its one-line repair, not on the candidate tool.
- The C2 partial-visibility numbers come from a standalone harness that models the reader and mutant, not from the full fixture (which uses timing sleeps). The kill-rate conclusion (timing dependence) is measured; the exact percentages are not stable across runs (5/40 and 6/40 on the chunked-no-pause arm).
- I did not verify the r61 matrix as a frozen matrix (it does not exist yet); F4 is verified on the r60 builder output.
- Q59's wording and R2's vocabulary conflict on gate surfaces; I report that and rely on R2 (the executable instrument) for the axis verdict.

## Tooling

No tools installed or upgraded (python3 stdlib only; git read-only in lane; all mutating git only in scratch fixtures, each checked with `rev-parse --show-toplevel`). No pacman transactions.

## Evidence index

`.ufo/waves/round-61/w1/S61CriticRound/`: `README.txt`, `chrono-rule.txt` (F1–F3), `matrix-r60-rows.txt` (F4), `python-uncaught-exit.txt` (F5), `real-record-base.txt` (real-record arm, verified), `axis-check.txt` + `v1.txt`–`v3.txt` (F7, F16), `partial-visibility.txt` (F9), `c2-mutant-kill-gap.txt` (F8, the r60 fixture passes both mutants), `mutA-worktree-digest.py`, `mutB-chunked-direct.py` (F8/F9 mutants), `probe_chrono.py`, `probe_matrix.py`, `probe_partial.py`.
