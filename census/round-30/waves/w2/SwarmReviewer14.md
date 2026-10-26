# SwarmReviewer14 — r30-landing-gate-discovery.py vs the frozen D1-D7 contract

Seat: reviewer, souji round 30 attempt 1, wave 2. Read-only seat; scratch `/fast/scratch/hyaku/souji-r30/ReviewDiscoveryFixture/` (receipts copied out, scratch removed). Tooling record: nothing installed or updated this run; used preexisting python3 3.14.8 and git 2.56.0 (operator 2026-10-19 authorization, no pacman transactions).

## Status
STATUS: PASS — the attack ran in full: the fixture executed against the tip gate (7/7 PASS, control FALSE-GREEN-REJECTED, rc 0), the base gate (3/7, REDARM demonstrated directly), a hand-built sloppy-resolver mutant (both D6 trap halves fire), and both prerequisite guards (rc 2, nothing built). One DEFECT-NOT-FATAL found: the fixture docstring attributes to the frozen contract a D6 sentence the frozen preregistration does not contain.

## Evidence

Provenance
- `tests/fixtures/r30-landing-gate-discovery.py` worktree is byte-identical to the tip blob 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8 (`git show <tip>:<fixture> | diff -q` clean); its only commit is 68447af (the C2 landing). `tools/souji-landing-gate.py` is also clean vs tip; `git status --porcelain -- tests/ tools/` empty before and after every run — no lane write.
- Frozen contract, preregistration.txt:7 (opened raw this run): "D6 a `.ufo/waves/round-N/w1/X.md` pointer resolves when census/round-N/waves/w1/X.md is committed and is LG-DANGLING-PTR when it is not". Grep of preregistration.txt and amendments.txt for "pinned against shortcuts" / "same-basename" / "capture directory that exists": the only "same-basename" hit is C1's K2 correction rule (preregistration.txt:5); no D6 shortcut sentence exists anywhere frozen.

Run 1 — fixture vs TIP gate (`tools/souji-landing-gate.py` at 9dcd3676, worktree identical):
```
CASE D1 PASS exit=0 reports=2 status=2 findings=0
CASE D2 PASS exit=2 reports=0 status=0 findings=0
CASE D3 PASS exit=1 reports=1 status=1 findings=1
CASE D4 PASS exit=1 reports=1 status=1 findings=1
CASE D5 PASS exit=1 reports=1 status=1 findings=1
CASE D6 PASS exit=0 reports=1 status=1 findings=0
CASE D7 PASS exit=1 reports=1 status=1 findings=1
CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=D1,D2,D3,D5,D6,D7
cases=7 pass=7 control=FALSE-GREEN-REJECTED
FIXTURE-TIP-RC=0
```

Run 2 — fixture vs BASE gate (blob `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b:tools/souji-landing-gate.py`, 2326 lines, extracted to scratch):
```
CASE D1 FAIL exit=2 reports=0 status=0 findings=0 FAIL(COULD-NOT-EVALUATE printed; exit=2; checked_reports=0 want 2; status_lines=0 want 2)
CASE D2 PASS exit=2 reports=0 status=0 findings=0
CASE D3 PASS exit=1 reports=1 status=1 findings=1
CASE D4 FAIL exit=1 reports=1 status=1 findings=3 FAIL(template token flagged: round-%s; template token flagged: round-{N})
CASE D5 PASS exit=1 reports=1 status=1 findings=3
CASE D6 FAIL exit=1 reports=1 status=1 findings=1 FAIL(mapped: exit=1 want 0; mapped: capture-backed pointer flagged)
CASE D7 FAIL exit=2 reports=0 status=0 findings=0 FAIL(COULD-NOT-EVALUATE printed; exit=2 want 1; checked_reports=0 want 1; missing LG-SEAT-UNCARRIED)
CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=D1,D2,D3,D5,D6,D7
cases=7 pass=3 control=FALSE-GREEN-REJECTED
FIXTURE-BASE-RC=1
```
Corroborates the frozen before-state "Before at base: `reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same`" (preregistration.txt:7): the fixture fails 4/7 at base, i.e. redarm=fail is real, and passes at tip, i.e. fixture=ok is real.

Run 3 — prerequisite, TMPDIR unset:
```
PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)
cases=0 pass=0 control=FALSE-GREEN-ACCEPTED
PREREQ-UNSET-RC=2
```

Run 4 — prerequisite guard, TMPDIR inside a git checkout (simulated entirely in scratch: a fresh git repo containing copies of the fixture and the tip gate, TMPDIR a subdir of that repo):
```
PREREQ FAIL TMPDIR .../guard-sim/tmp is inside the tool git checkout .../guard-sim
PREREQ FAIL TMPDIR .../guard-sim/tmp is inside the fixture git checkout .../guard-sim
cases=0 pass=0 control=FALSE-GREEN-ACCEPTED
GUARD-SIM-RC=2
GUARD-SIM-TMP-RESIDUE: (empty — nothing was built before the guard fired)
```

Run 5 — mutant gate (tip gate with sloppy capture resolution inserted after the exact-capture check: a `.ufo/waves/round-N/...` pointer also resolves when any committed path starts with the capture directory, or when any committed `census/round-*` path carries the pointer's basename):
```
CASE D1 PASS exit=0 reports=2 status=2 findings=0
CASE D2 PASS exit=2 reports=0 status=0 findings=0
CASE D3 PASS exit=1 reports=1 status=1 findings=1
CASE D4 PASS exit=1 reports=1 status=1 findings=1
CASE D5 PASS exit=1 reports=1 status=1 findings=1
CASE D6 FAIL exit=0 reports=1 status=1 findings=0 FAIL(mapped-missing: exit=0 want 1; mapped-missing: uncaptured pointer not flagged; mapped-dir: exit=0 want 1; mapped-dir: capture-directory-only resolution)
CASE D7 PASS exit=1 reports=1 status=1 findings=1
CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=D1,D2,D3,D5,D6,D7
cases=7 pass=6 control=FALSE-GREEN-REJECTED
FIXTURE-MUTANT-RC=1
```

Per-case contract mapping (fixture line numbers from the tip blob)
- D1 — world :215-222 (commits `census/round-30/waves/w1/SeatA.md` and `w2/SeatB.md`, no `.ufo/waves/round-30/`), judge :322-331 (no CNE, rc!=2, checked_reports=2, status_lines=2, findings=0). Tests the frozen sentence exactly, over the recursive w1/w2 layout, and adds status/findings pins. Wrong gates caught: capture-ignorer (CNE — the base run demonstrates), non-parser of STATUS (status_lines=0), w1-only reader (1!=2), spurious finder (findings!=0), the control (0!=2).
- D2 — world :223-225, judge :332-337 (CNE, rc==2, checked_reports=0). The fixture's expectations match the gate's real error path: the gate always prints its SUMMARY (tools/souji-landing-gate.py:1200-1201, fragment "status_lines=%d\tcarry_heading=%d\tchecked_reports=%d") and prints "COULD-NOT-EVALUATE\t%s" to stderr with exit 2 (gate:1215, :2345-2347).
- D3 — world :226-237 (same relative report path in both dirs; the capture copy carries no STATUS line), judge :338-348 (rc==1, checked_reports=1, status_lines=1, LG-SEAT-UNCARRIED). status_lines=1 proves the .ufo bytes were read (the capture copy has none); checked_reports=1 proves no double count — the gate's dedup rule is "the wave dir alone is read, so no report is ever counted twice" (gate:486). A capture-ignoring gate passes D3 (the base run demonstrates: D3 PASS at base) and is caught by D1; the frozen D3 sentence is about .ufo-read plus no-double-count, and the judge pins both.
- D4 — world :238-253, judge :349-354 (no LG-DANGLING-PTR row containing `round-%s`, `round-<N>`, `round-{N}`). Substring needles are more sensitive than the frozen full-token wording, not less. Gate side: template tokens are skipped as non-pointers (gate:877-880, "TEMPLATE_POINTER_RE.search(part)").
- D5 — same world, judge :355-359 (rc==1; the real dangling `census/round-29/does-not-exist.md` in the SAME file must be flagged). The same-file co-location defeats file-level suppression: a gate that suppresses pointers in template-bearing files passes D4 only by failing D5.
- D6 — worlds :254-290, judge :360-376: `mapped` (resolve; rc==0; no flag), `mapped-missing` :266 (same-basename capture of the EVALUATED round committed — a round-agnostic mapping must not resolve), `mapped-dir` :279 (capture directory exists without the pointed-at file — directory-only resolution must not resolve). The gate binds the mapping to the pointer's own round number (gate:913-916, `return "census/%s/waves%s" % (match.group(1), match.group(2) or "")` off `CAPTURE_POINTER_RE = re.compile(r"^\.ufo/waves/(round-\d+)(/.*)?$")` gate:155), and `tree_paths` holds every parent directory of committed files (gate:955-960), so directory-only resolution is a real, distinguishable failure mode. Frozen text pins only resolve/not-resolve; the two trap worlds are fixture-authored (Finding 1) and demonstrably effective (Run 5).
- D7 — world :291-296, judge :377-385 (rc==1, checked_reports=1, LG-SEAT-UNCARRIED for the capture-only uncarried `STATUS: FAIL`).
- Control — :412-418: a stub printing one clean zero SUMMARY ("SUMMARY\tfindings=0\tchecked_reg=0" fragment, :414) run through the same seven judges; fails 6/7 (D4 passes trivially — the frozen text requires only >=1 failure). Output format matches the frozen spec: `CASE <id> PASS|FAIL` lines with a detail suffix, a CONTROL line, last line `cases=7 pass=M control=FALSE-GREEN-REJECTED` (:544-547), N=7 >= 7, and "return 0 if (passed == len(CASES) and rejected) else 1" (:548); rc 2 on missing prerequisite (observed, Runs 3-4).

$TMPDIR discipline
- Builds only under $TMPDIR: "tempfile.mkdtemp(prefix=\"r30-discovery-fixture-\", dir=os.path.realpath(os.environ[\"TMPDIR\"]))" (:494-495); repos under `<scratch>/repos`, control stub under `<scratch>`, git identity pinned by git_env (:66-88) with REPO_SELECTING variables scrubbed (:46-53); `finally: shutil.rmtree(scratch, ignore_errors=True)` (:549-550). After Runs 1, 2 and 5 the scratch root held only my two gate copies — zero fixture residue.
- Guards verified empirically: unset TMPDIR → rc 2 before any build (Run 3); TMPDIR inside a git checkout → both labels flagged, rc 2, zero residue in the would-be TMPDIR (Run 4, simulated in scratch, never against the lane).
- The gate under test writes its own parse snapshot under /var/tmp — "tempfile.mkdtemp(prefix=\"souji-landing-gate-\", dir=\"/var/tmp\")" (gate:1070), removed in evaluate's finally — tool behavior, disclosed in the fixture docstring :31-33. Two /var/tmp dirs observed mid-run belonged to concurrent peers and were gone on re-stat; none was created by my runs. No lane write occurred.

## Findings
1. DEFECT-NOT-FATAL (provenance) — tests/fixtures/r30-landing-gate-discovery.py:21-24 presents "Both halves are pinned against shortcuts: a same-basename capture of the evaluated round does not resolve it" as part of the block headed "Frozen contract (census/round-30/records/preregistration.txt, C2 paragraph)". preregistration.txt:7 (read raw this run) ends D6 at "...LG-DANGLING-PTR when it is not."; amendments.txt contains no such sentence (grep: no match). The two trap worlds (:266, :279) are fixture-authored strictness committed at the C2 landing, never logged as an amendment. Stricter-only — no frozen predicate, target or counter is relaxed — but the docstring misquotes the frozen contract; the L1 should either have the docstring corrected (docstring-only change) or log the extra halves as fixture-authored strictness.
2. DEFECT-NOT-FATAL (robustness) — run_gate :181-191 launches the gate with the ambient environment ("proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)", :188 — no env=), while the fixture scrubs REPO_SELECTING for its own git calls (:46-53). Harmless today because the gate pins GIT_ENV for every internal git call (gate:210, :249, :691) and GIT_ENV strips the repo-selecting variables (gate:190-211) — but the fixture's isolation guarantee rests on the gate's own hygiene, not its own; a future gate regression there could misjudge the fixture silently.
3. Observation (prereg accuracy; no fixture change needed) — the frozen problem statement says the gate "reports template tokens (`round-%s`, `round-<N>`) and capture-mapped `.ufo/waves/round-N/` pointers as dangling" (preregistration.txt:7); at base only `round-%s` and `round-{N}` are flagged (Run 2: findings=3 = both tokens plus the real dangling pointer) — `round-<N>` is never a pointer candidate because the tokenizer drops tokens containing `<`, `>`, `*` (base-gate.py:829, "or any(char in raw for char in \"<>*\")"). D4 requires all three unflagged, which is stricter than base behavior and satisfied at tip. No defect in the fixture; the prereg's problem statement is half-accurate on `round-<N>`.
4. Observation (residual gap) — D1's judge pins rc!=2 but not rc==0 (:325); a hypothetical gate exiting nonzero without CNE and with correct counts would pass D1. rc==0 is pinned only in D6's mapped half (:365). The frozen contract does not state D1's exit code, so this is contract-faithful; residual risk only.

## Attack log
1. Fixture vs tip gate (9dcd3676) — HOLDS: 7/7 PASS, control FALSE-GREEN-REJECTED, rc 0; output format and exit-code semantics match the frozen fixture contract.
2. Fixture vs base gate (9420341d) — HOLDS (REDARM demonstrated directly): base fails D1 (CNE — it reads only .ufo/waves), D4 (flags `round-%s` and `round-{N}`), D6 (capture-backed pointer flagged), D7 (CNE); passes D2, D3, D5. Base's D3 pass confirms D3 alone cannot catch a capture-ignorer — D1 supplies that discrimination; the case SET satisfies the frozen contract.
3. Always-zero-emitter control — HOLDS: fails D1,D2,D3,D5,D6,D7 (passes D4 trivially); rejected as the frozen text requires.
4. Sloppy-resolver mutant (basename-across-rounds plus directory-only capture resolution) — HOLDS: exactly D6 fails, both trap halves fire ("mapped-missing: uncaptured pointer not flagged", "mapped-dir: capture-directory-only resolution"); every other case and the control unaffected. The fixture catches both D6 shortcuts its docstring claims to pin.
5. $TMPDIR discipline (unset, inside-checkout, residue) — HOLDS: rc 2 before any build in both guard paths, zero residue, builds strictly under mkdtemp(dir=realpath(TMPDIR)), scratch self-cleaned, no lane write.
6. Docstring provenance — DEFECT-NOT-FATAL (Finding 1).
7. Per-case wrong-gate analysis — no wrong gate found that passes the case set; residual: Finding 4's rc gap on D1 (contract-faithful).

## Deliveries
- .ufo/waves/round-30/w2/SwarmReviewer14.md — this report.
- .ufo/waves/round-30/w2/SwarmReviewer14-run-tip.txt — Run 1 receipt.
- .ufo/waves/round-30/w2/SwarmReviewer14-run-base.txt — Run 2 receipt.
- .ufo/waves/round-30/w2/SwarmReviewer14-run-mutant.txt — Run 5 receipt.
- .ufo/waves/round-30/w2/SwarmReviewer14-run-prereq.txt — Runs 3-4 receipts.

Report: .ufo/waves/round-30/w2/SwarmReviewer14.md
