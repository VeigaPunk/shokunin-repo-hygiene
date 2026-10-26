# SwarmExecutor07 — r31 w1 C2 fixture (landing-gate precision G1-G10)

## Status

STATUS: PASS — the frozen C2 fixture is written to the preregistration contract, the base tool at 9f17a1ef reproduces exactly the required REDARM pattern (FAIL G1 G3 G4 G5 G6 G7 G8, PASS G2 G9 G10), the always-zero control is rejected, the refusal paths fire, and a scratch-only probe carrying only the contract's reading rules scores `cases=10 pass=10`.

## Evidence

E1 — fixture run against the BASE tool (contract REDARM). Base commit 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; tool bytes extracted with `git show 9f17a1ef...:tools/souji-landing-gate.py` (sha256 ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056). Fixture sha256 fdae16132b48233a6cf2df0e6342fe8b448e1a3b63598380365c1fc1d897ecac.

    $ TMPDIR=/fast/scratch/hyaku/souji-r31/C2Fixture/tmp \
        python3 -B .ufo/waves/round-31/w1/deliver-r31-landing-gate-precision.py \
        --tool /fast/scratch/hyaku/souji-r31/C2Fixture/base-gate.py
    CASE G1 FAIL exit=0 reports=1 status=1 findings=0 dangling=0 uncarried=0 FAIL(g1: checked_reports=1 want 2 (union); g1: LG-SEAT-UNCARRIED count=0 want 1; g1: LG-SEAT-UNCARRIED does not name w1/B.md)
    CASE G2 PASS exit=0 reports=1 status=1 findings=0 dangling=0 uncarried=0
    CASE G3 FAIL exit=1 reports=2 status=2 findings=1 dangling=0 uncarried=1 FAIL(g3: LG-SEAT-UNCARRIED count=1 want 0 (second section unseen?))
    CASE G4 FAIL exit=1 reports=1 status=1 findings=1 dangling=1 uncarried=0 FAIL(g4: LG-DANGLING-PTR count=1 want 0: census/round-18/...seat-audit...json)
    CASE G5 FAIL exit=1 reports=1 status=1 findings=1 dangling=1 uncarried=0 FAIL(g5: LG-DANGLING-PTR count=1 want 0: tools/x.py:274–277)
    CASE G6 FAIL exit=1 reports=1 status=1 findings=3 dangling=3 uncarried=0 FAIL(g6: LG-DANGLING-PTR count=3 want 0: .ufo/waves/round-31/v/.gitattributes | census/round-31/waves/v/.gitignore | census/round-31/waves/v/.gitignore:fixture/)
    CASE G7 FAIL exit=1 reports=1 status=1 findings=2 dangling=2 uncarried=0 FAIL(g7: LG-DANGLING-PTR count=2 want 0: census/round-%d/waves/ | corpus/lessons/round-%02d.md)
    CASE G8 FAIL exit=1 reports=1 status=1 findings=3 dangling=3 uncarried=0 FAIL(g8: LG-DANGLING-PTR count=3 want 0: corpus/authority | tools/kill/killpg | tools/tests/census/corpus)
    CASE G9 PASS exit=1 reports=1 status=1 findings=6 dangling=6 uncarried=0
    CASE G10 PASS exit=1 reports=1 status=1 findings=1 dangling=0 uncarried=1
    CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=G1,G2,G9,G10
    cases=10 pass=3 control=FALSE-GREEN-REJECTED
    $ echo $?
    1

E2 — per-world rows (same base tool, same scratch; a debug import of the fixture's own `build_world`/`run_gate`), showing the findings named by the contract and nothing extra:

    g1  SUMMARY findings=0 checked_reports=1 status_lines=1
    g2  SUMMARY findings=0 checked_reports=1 checked_markers=1 carry_heading=1
    g3  LG-SEAT-UNCARRIED  .ufo/waves/round-31/w1/Y.md  line 3: STATUS: FAIL - synthetic carry y.
    g4  LG-DANGLING-PTR    census/round-18/...seat-audit...json
    g5  LG-DANGLING-PTR    tools/x.py:274–277
    g6  LG-DANGLING-PTR    .ufo/waves/round-31/v/.gitattributes | census/round-31/waves/v/.gitignore | census/round-31/waves/v/.gitignore:fixture/
    g7  LG-DANGLING-PTR    census/round-%d/waves/ | corpus/lessons/round-%02d.md
    g8  LG-DANGLING-PTR    corpus/authority | tools/kill/killpg | tools/tests/census/corpus
    g9  LG-DANGLING-PTR    .ufo/waves/round-31/w1/missing.md | census/round-3/garbage-census.out | census/round-31/waves/w1/missing.md | corpus/knowledge/missing.md:12–14 | tools/__pycache__/ | tools/missing.py   (findings=6)
    g10 LG-SEAT-UNCARRIED  .ufo/waves/round-31/w1/Z.md  line 3: STATUS: FAIL - synthetic carry z.

E3 — refusal contract (unset / inside lane / inside fleet), exit 2 each, nothing created:

    PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)
    PREREQ FAIL TMPDIR /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo is inside the lane root /home/vgpnk/Projects/shokunin/souji-shokunin
    PREREQ FAIL TMPDIR /home/vgpnk/Projects/shokunin/.scratch is inside the fleet root /home/vgpnk/Projects/shokunin

E4 — satisfiability (scratch-only probe, NOT a delivery, NOT a claim): a copy of the base tool in /fast/scratch/hyaku/souji-r31/C2Fixture/probe-gate.py carrying only the contract's reading rules (union + dedupe of the two report trees, every carry section, ellipsis/printf/`:text`/en-dash/`.captured`/prose token rules, real dangling pointers kept) gives `CASE G1..G10 PASS` for all ten and `cases=10 pass=10 control=FALSE-GREEN-REJECTED`, exit 0. The probe was deleted with the scratch tree.

Versions: Python 3.14.8, git 2.56.0. No tool was installed or upgraded this run (no pacman; nothing else needed).

## Findings

1. Base report discovery is wave-tree-first, capture only as fallback: in g1 the `.ufo/waves/round-31/w1/A.md` blob suppresses `census/round-31/waves/w1/B.md` entirely (`checked_reports=1`, zero findings). Locator: tools/souji-landing-gate.py:467-479 at 9f17a1ef.
2. Base carry scan stops at the next heading, so only the first `## Seat-reported failures` section is read: g3 leaves report Y uncarried. Locator: tools/souji-landing-gate.py:389-400 (`failures_section_lines`) at 9f17a1ef.
3. Base pointer tokenizer false positives, each reproduced by its own world: ASCII `...` placeholder (g4), en-dash line range `tools/x.py:274–277` (g5), `.captured`/`:text` composite (g6, three tokens), printf templates `%d`/`%02d` (g7, two tokens), prose slash alternations (g8, three tokens). Locator: tools/souji-landing-gate.py:832-905 (`_trim_pointer_token`, `_pointer_paths`) at 9f17a1ef.
4. Precision is preserved on the same base tool: g9 still reports all six real dangling pointers (including `corpus/knowledge/missing.md:12–14` with its line spec and `tools/__pycache__/` with its trailing slash), and g10 still reports exactly one uncarried failure (Z). Any suppression broad enough to green g4-g8 while losing one of the g9/g10 rows fails the fixture.
5. The case set is achievable: E4 shows 10/10 with contract-shaped reading rules, so a C2 tool that keeps base precision can pass; the fixture is not an unreachable target.
6. C2Gate's /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-souji-landing-gate.py did not exist when this seat finished, so the fixture has not been run against that delivery. E4 is a scratch probe only; C2Gate's file is the tool of record.
7. Fixture boundary checks: it creates only git repos under `$TMPDIR` (private mkdtemp, removed in `finally`), never writes in the lane, never runs lane scripts, and passes no `--fleet-root`. The gate's own `/var/tmp` parse snapshot is the tool's behaviour.

Risks (for the L1): (a) the fixture hardcodes the contract's lanes roots (`LANE_ROOT`, `FLEET_ROOT`) for the TMPDIR refusal; if the lane relocates, those constants move with the contract. (b) G2 requires byte-identical dedupe of `w1/A.md`; a union tool that reads capture bytes when both exist still passes because the fixture writes identical bytes. (c) G1/G2 assert `checked_reports`, which a future gate must keep in SUMMARY.

## Deliveries

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-r31-landing-gate-precision.py (sha256 fdae1613…) — frozen fixture for integration verbatim at tests/fixtures/r31-landing-gate-precision.py.
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-c2-fixture-red-before.txt — base-tool REDARM transcript.
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/SwarmExecutor07.md — this report.
