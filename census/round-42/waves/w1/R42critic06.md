# R42critic06 — attack on the round-42 preregistration and controls as a package

Seat: R42critic06 (critic). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Freeze afe17f416eec04dcf3f480b580a8f928de61d19d, instruments b7408095543579ac71b33ecf7b80b0cb8ef45036, base bf618f6c5c09d302994871c94903abbea2deb60d.
Read-only: no frozen file, counter, population, control, tool or tracked file was edited. Attack artifacts are copied into this seat directory (`attacks/`); every candidate was scored in a scratch clone by `census/round-42/score-candidate.sh`. Scratch `/fast/scratch/hyaku/souji-r42/R42critic06/` removed before yield. No tool installed or upgraded.

## 1. Commands run and observed output

Freeze check (the required command):
```
$ python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-42/preregistration.txt --rev afe17f416eec04dcf3f480b580a8f928de61d19d
SUMMARY claims=3 findings=0          EXIT=0
```

Frozen digests, re-derived (`sha256sum`): c1-counter 0ab07cd3…dcd46aa ✓, c1-items b2601340…8a39 ✓, c2-counter fa44392d…5ac1 ✓, c2-cases 148b7b87…4511 ✓, c3-counter bf0ebf4f…585d76 ✓, c3-mutants 2f6f8df3…4ab205 ✓, r1-counter f2dcbd06…11cc1bb ✓, pinned tool b2a603cf…3ab3e34dc6 ✓ (all match the prereg).

Three do-nothing control receipts plus the R1 control, re-run in my scratch (`--scratch` my own dir, never L1's):

| control | my observed line | receipt in controls/ | match |
|---|---|---|---|
| C1 A no register | `SUMMARY items=70 population=ok registered=0 class_ok=0 unresolved=5 corrected=0 junk=0 rewritten=0 new_mismatches=0` rc=1 | same | yes |
| C1 B forged register (score-candidate) | `SUMMARY items=70 population=ok registered=70 class_ok=42 unresolved=5 corrected=0 junk=0 rewritten=0 new_mismatches=0` | same | yes |
| C2 A r41 tool | `SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red retro_clean=ok selftest=FAIL patches=0/3` | same | yes |
| C2 B always-green selftest | `… real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=6e1c564a94b5` | same | yes |
| C3 A no fixture | `SUMMARY mutants=13 killed=0 survived=13 pristine=FAIL prior=8/8 … equiv_killed=0 anchors=ok` | same | yes |
| C3 B always-pass stub | `SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok` | same | yes |
| C3 C byte-sniffer | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=6 anchors=ok` | same | yes |
| R1 control | `SUMMARY findings=3 deleted=0 rows_added=0 stale=0` rc=1 | same | yes |

Predicate numbers: `python3 -B tools/souji-declared-evidence.py --root <lane> --rev bf618f6… --file SCORECARD.md` → `assertions=474 resolved=404 skipped=780 mismatches=70` (matches C1 Predicate).

Landing gate scope (R1): `python3 -B tools/souji-landing-gate.py --root <lane> --rev afe17f… --round 41` (no fleet root) → three `LG-DANGLING-PTR` rows: `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` and `…/JjTrialSouji.md` (cited from corpus/README.md:217), `.ufo/waves/hyaku/jj-w1/reports/` (corpus/knowledge/jj-colocation-receipts.md:148); `SUMMARY findings=3`.

Prior fixtures × 19 condition mutants (`attacks/prior_vs_mutants.py`, reuses the frozen counter's MUTANTS/EQUIV/PRIOR tables read-only): 152 of 152 runs completed with rc 1 or 0, a SUMMARY line, and no traceback and no timeout; every one is a clean NOT-KILL. (The script's own `KILLS` tally is a bug — `"NOT-KILL".endswith("KILL")` — and is disregarded; the per-line classes are the evidence.)

Repository facts:
- `git ls-files .ufo/waves/round-41 .ufo/waves/round-42 | wc -l` → `0`; `git check-ignore` → `.gitignore:1:.ufo/waves/`.
- `git log --diff-filter=A --name-only afe17f -- .ufo/waves/round-41 .ufo/waves/round-42` → empty.
- `git ls-tree bf618f6… corpus/lessons/round-42.md` → empty (the lesson file does not exist at base).
- `git show --stat afe17f`: adds c2-cases.tsv, preregistration.txt, controls/c2-control.txt, c3-control.txt, r1-control.txt, and **modifies** controls/c1-control.txt (the C1 receipt went from `registered=62 class_ok=34` to `registered=70 class_ok=42` in the freeze commit).

## 2. Attacks built and scored (score-candidate.sh, cheapest form of each)

| # | candidate (artifact) | scored SUMMARY (verbatim) | verdict |
|---|---|---|---|
| A1 | C2 env-marker selftest: r41 tool + `--selftest` that exits 1 when `SOUJI_R42_PATCH` is set (`attacks/freeze-check-envcheat.py`, `attacks/make_c2_cheat.py`) | `SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3` | patches leg reached with zero digest/freeze/ancestry logic; overall target still missed (13 new cases fail) |
| A2 | C3 byte-presence fixture: asserts 13 pinned condition lines are present in `--tool` text, never runs the tool (`attacks/byte-presence-fixture.py`) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13` | **full C3 Target reached** |
| A3 | C3 cheapest partial: two argparse probes (`attacks/cheap-fixture.py`) | `SUMMARY mutants=13 killed=1 survived=12 pristine=FAIL … cases=2` | rejected (as designed) |
| A4 | C1 partial: register labels all 70 items `unresolved`, no lesson (`attacks/mk.py`) | `SUMMARY items=70 population=ok registered=70 class_ok=5 unresolved=5 corrected=0 junk=0 …` | rejected; shows class_ok measures rule conformance |
| A5 | R1 repair: the three exact pointer paths appended as exemption rows (`attacks/pointer-exemptions.tsv`) | `SUMMARY findings=0 deleted=0 rows_added=3 stale=0` (`score-candidate.sh r1`) | R1 Target feasible with the intended fix |

Note on A2 provenance: the 13 fragments were typed from the frozen population descriptions (c3-mutants.tsv) and the pinned tool text; the fixture never reads the counter. The counter's own EQUIV control is the only defence against this shape, and it only fires if a fixture also touches the six equivalent lines.

## 3. Equivalence and kill-logic checks (read, not run)

- EQUIV correctness (`tools/souji-worktree-drift.py`): B3 (line 141) and B4 (line 277) call `set_blocking` only after an `fstat` S_ISREG check on the same fd, so a regular file never sees O_NONBLOCK effects: equivalent. E5/E7/E9 (lines 292, 301, 318, 342): `measured[0]` is `root_real` and every gitdir/repo entry is refused unless inside root_real, so the JSON guard on `[root_real]` is equivalent. H4 (line 320 `if args.json:`): `""` and `None` are both falsy: equivalent. No defect found in the EQUIV set.
- Survival is non-vacuous: the 152 prior-fixture runs above show no crash or timeout masquerading as survival.
- C3 `killed()` (c3-counter.py:151-153) requires rc 1, fail>0 and no traceback; a 300 s timeout returns 124 (line 146) and counts as survived. Not exploited by any run above.

## 4. Findings

Severity: **admission** = changes whether a candidate can be admitted by the frozen counter; **named limit** = report and lesson must carry it; **cosmetic** = wording or count only.

| item | finding | severity | proposed handling (named limit; frozen files unchanged) |
|---|---|---|---|
| C3 Predicate vs counter | Predicate says the fixture "observes tool behaviour rather than bytes". Counter enforces this only through EQUIV (c3-counter.py:92-103, 151-153). A fixture that asserts the 13 mutated lines are present (A2) reaches the full Target with pristine=ok and equiv_killed=0. | **admission** | L1 pre-landing audit of `tests/fixtures/r42-drift-conditions.py`: reject any fixture that reads `--tool` as text (`open(a.tool`, `read_text`, `in src`) or never invokes it via `subprocess`. Record in lesson as a named limit that the counter cannot distinguish behaviour from line presence. |
| C2 patches leg | `p_rc not in (0,124)` (c2-counter.py:410) accepts any non-zero exit, including tracebacks and an env-keyed exit. A1 reaches patches=3/3 with selftest=ok. The three patches also match literal argv shapes (`--diff-filter=A`, `merge-base`, `hashlib.sha256`), so a correct tool written differently is not exercised [INFERENCE: not built]. | named limit (admission only if the L1 shim audit misses an env-keyed exit) | L1 audit greps candidate tool for `SOUJI_R42_PATCH`, `sitecustomize`, `sys.modules`, `os.environ`; name the argv-shape dependence in the lesson. |
| C2 Population `c2-cases.tsv` | Pinned by sha (148b7b87…) but never read by c2-counter.py (`grep` finds no reference). The 37 cases are the in-code CASES tuple (c2-counter.py:212-254). The TSV currently mirrors CASES exactly, but drift is unmeasured. | named limit | Name the Population as documentary; no counter reads it. |
| C2 DISPATCH-BEFORE-FREEZE | `.ufo/waves/` is gitignored (.gitignore:1) and has no tracked file and no history in r41 or r42. The dispatch leg of `real` and `retro_clean` can never fire on committed bytes; the widened names are exercised only in synthetic repos. Clause "before any wave file exists" is not re-derivable from committed bytes. | named limit | Name in lesson: the dispatch rule is a synthetic-only guarantee in this lane; any wave-freeze claim rests on the L1's own record, not on the tool. |
| C2 Predicate vs Target | Target omits `tool_sha=…` printed by SUMMARY (cosmetic). Predicate says "21 r41 cases retained": counter has 19 r41 rows + the two `two_unresolved` cases (c2-counter.py:277-282), consistent but unstated. | cosmetic | State the 19+2 split in the lesson. |
| C1 kill rule vs Target | `met` (c1-counter.py:247-249) tests `corrected == unresolved` and `class_ok == 70`, not `unresolved == 5`. The literal 5 is only checked textually. Derivation is frozen at BASE, so K=5 holds in practice (A4 class_ok=5 confirms). | cosmetic | Name: K=5 is a property of the frozen base, not enforced by the verdict. |
| C1 calibration meaning | `class_ok` measures agreement with the counter's own rules R1-R4 (c1-counter.py:25-34), not whether those rules are correct. A candidate that derives the register from the counter's `derive` would also reach 70. | named limit | Lesson states calibration = rule conformance; the "true" count of 65/5 is a definition, not a measurement. L1 audit must reject candidates that import the counter. |
| C1 separability | Prereg rule 6 says C1 touches SCORECARD-side records only. C1 also requires `census/round-42/c1-register.tsv` and `corpus/lessons/round-42.md` (c1-counter.py:57-58); the lesson does not exist at base. `new_mismatches` runs the declared-evidence tool at REV, which resolves tokens only via `git ls-tree`/`cat-file` (tools/souji-declared-evidence.py:13, 66). Any round-42 SCORECARD row that cites a gitignored `.ufo/waves/…` seat report turns C1 red though C1 is not at fault. | named limit (coupling to other claims' SCORECARD rows and lesson text) | L1 cites only committed paths in SCORECARD additions this round; C1 landed in the same jj commit as the lesson; name the coupling. |
| C1 overlapping writer | `junk` (c1-counter.py:216-233) counts any `CORRECTION-DE` text in the round lesson, which the scribes also write. The prereg's "No overlapping writers" conflicts with the append requirement. | named limit | Scribe lesson text must not contain `CORRECTION-DE`; the L1 greps before landing. |
| C1 wording | "append one line to corpus/lessons/round-42.md" creates the file (absent at base). Rule "every Counter … is the blob at its adding commit" is false for c1-counter.py (added 410316c, edited b740809; frozen blob is b740809's). The freeze check enforces blob-at-freeze only. Prereg says "five control receipts are added by the freeze commit"; four receipts exist and c1-control.txt was modified, not added. | cosmetic | Correct the wording in the round lesson. |
| R1 feasibility | Three exact-path exemption rows give `findings=0 deleted=0 rows_added=3 stale=0` (A5). Exemptions match exact paths (landing-gate:1049-1055), so no prefix broadening. | none (verified) | none |
| R1 limits | Reason text unchecked. An exemption silences that path for every future source. `deleted` counts whole files (corpus/knowledge/jj-colocation-receipts.md), not "the entry" as the prereg says. R1 scans SCORECARD.md, corpus/README.md, corpus/knowledge/*.md and round-41 LOG sections at REV, so other seats' edits there can turn R1 red. | named limit (+ cosmetic wording) | Name the path-level scope and the coupling; keep the other seats out of README and knowledge files this round. |
| separability (3) | C1 and R1 are coupled through SCORECARD reads at REV (see above). R1 does not read round-42 lessons (check_pointers sources use round-41, landing-gate:1078-1087), so C1's lesson edit cannot change R1. C2 and C3 touch disjoint files and their legs do not read each other's artifacts. | named limit | Report the C1/R1 SCORECARD coupling in the round lesson. |
| universal clauses (4) | Every Kill and Predicate universal is enumerated by a counter leg except: C2 "exits non-zero when … patched" (3 fixed patches only, see above) and C1 "no mismatch on a line added this round" (enumerated as lines > base count; rewrites caught by `rewritten`). "over the landed lane tip" is not printable by any counter; it is context, not a verdict field. | cosmetic (context phrase) / named limit (C2) | Name the 3-patch scope; state the phrase is context. |
| freeze check run | Freeze check on the prereg is green at afe17f (claims=3 findings=0), but the dispatch leg is inert (above). | named limit | As C2 dispatch row. |

## 5. Verdict

- Admission-changing defect: **one** (C3 byte-presence fixture, A2). Frozen counter cannot be changed; handling is an L1 pre-landing audit of the candidate fixture plus a named limit. Without that audit, C3 would be admitted on a fixture that never runs the tool.
- Controls: all eight do-nothing and partial controls reproduce their receipts exactly and none reaches its Target. The partial-work attacks A1, A3, A4 fail their targets; A2 does not.
- Named limits: C2 patches leg (env-keyed exit accepted), C2 population unread, C2 dispatch leg inert in this lane, C1 calibration = rule conformance, C1/R1 SCORECARD coupling, C1 lesson overlap, R1 path-level scope.
- Cosmetic: C1 `unresolved=5` not in verdict, prereg wording on "adding commit" and "five receipts", C2 Target omits tool_sha.
- Verified (no defect): C3 EQUIV set (six behaviour-equivalent mutants), C3 survival non-vacuity (152 clean runs), R1 Target feasibility, all eight control receipts reproduce.

Commands for the L1 to run once after landing (not run by me as verification): `bash census/round-42/score-candidate.sh c3 <scratch> tests/fixtures/r42-drift-conditions.py=<landed fixture>` plus a grep of that fixture for `open(` / `read_text` on `--tool`.
