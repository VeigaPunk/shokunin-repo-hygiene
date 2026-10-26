# SwarmCritic17 — C2 kill-rule application (r30 w2, leaf critic)

## Status

STATUS: PASS — the attack ran end to end on committed bytes; the L1's `MISSED` verdict reproduces and is the correct application of the frozen kill rule, while the *reason* it misses is a cross-claim land-order coupling in the frozen design, not a defect of the landed gate; operability is improved.

Answers to the four questions, then evidence.

1. **Is `MISSED` the correct application? Yes.** The frozen target is `reports=86 cne=0 dangling=0 ... fixture=ok redarm=ok regress=same` with exit 0 at two revisions (preregistration.txt:7, "Target after, at the C2 landing commit and the final lane tip"). The frozen v1 counter at 68447af prints `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same` and GATE `rc=1` — one named field is wrong and the required exit code is wrong. The kill rule is absolute (preregistration.txt:7, "Kill rule: any other SUMMARY at the C2 landing commit or the final tip is a miss"). No parsing of the rule admits `dangling=1`.
2. **Is 68447af the C2 landing commit? Yes, on the only reading available before data.** It is the sole commit after the amendments that touches the C2 surface (gate + fixture + red-before), its parent is C1's landing 7b16731, its message is "C2 landing gate …", and the L1's own after-measurement commit aea0525 is titled "C1/C2 after-measurements at their landing commits". Reservation: the frozen text never defines "landing commit" — see Finding 3.
3. **Over-strict or under-strict?** Not over-strict in any way that can inflate a claim: it took the *earliest* commit at which the claim's own surface exists, which is the only choice that cannot be accused of post-hoc relaxation, and it reported the miss rather than the green tip. Not under-strict: it reports the tip's green too, and the tip is green under both readings of the `other=` tension (other=0). Residual gaps are records-level, Findings 5–6.
4. **Operability axis: improved, not harmed.** `reports` 0→86, `cne` 1→0, `dangling` 3→1→0, exit 2→1→0 across base / landing / tip; two of the base's three danglings were template fragments (`census/round-`, `corpus/lessons/round-`) that the change removes, the third resolves through the capture, and 7 previously invisible `LG-SEAT-UNCARRIED` findings surface (the prereg's own probe predicted 7) and are then carried. The REGRESS leg is identical for base and REV (`SELFTEST pass=65 fail=0`, r16 `total=15 failed=0`), so C1's R05/R06 literals are not moved: **calibration is not harmed and coverage is untouched**. The cost is land-order, not instrument quality: the gate is red at any commit that cites a wave path not yet captured, including this round's own C2 landing commit.

## Evidence

All lane paths absolute; receipts in `.ufo/waves/round-30/w2/SwarmCritic17-receipts.txt`. Lane working tree was dirty (`M SKILL.md`, `M corpus/QUALITY.md`, `?? corpus/lessons/round-30.md`) during every run and did not affect any number, because discovery reads the REV tree.

- Commit chain (`git rev-list --parents`, read-only): `02aea48 → 7b16731 (C1) → 68447af (C2) → aea0525 (capture + after-measurements) → 76c94eb → 936efc8 → 9dcd367`. Only 68447af touches `tools/souji-landing-gate.py` + `tests/fixtures/r30-landing-gate-discovery.py` after the amendments.
- Frozen v1 at 68447af (my run, `python3 -B census/round-30/c2-counter.py --root <lane> --rev 68447af… --base 9420341… --fleet-root /home/vgpnk/Projects/shokunin`): byte-identical to `census/round-30/records/c2-after-v1.txt`, 8 lines, rc=1: `GATE rc=1 reports=86 cne=0 dangling=1 other=7` / `SUMMARY … dangling=1 other=7 …`.
- Frozen v1 at the tip (9dcd367): `GATE rc=0 reports=86 cne=0 dangling=0 other=0`, `SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same`, rc=0 — the frozen literal, exit 0.
- The one dangling, at 68447af, gate rc=1: `LG-DANGLING-PTR	.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv	SCORECARD.md:322 cites path absent at 68447afef62e`; exactly 1 such line (`grep -c`). SCORECARD.md:322 at that rev is a 1301-byte C1 measurement line; the pointer is inside it. `git cat-file -e 68447af:census/round-30/waves/w1/deliver-c1-literal-history.tsv` → rc=128 ("exists on disk, but not in"); same path at aea0525 → rc=0. `tools/pointer-exemptions.tsv` does not exist at 68447af, so no exemption could have applied.
- Ambiguity arm: frozen v1 at aea0525 → `SUMMARY reports=86 cne=0 dangling=0 other=7 … regress=same`, rc=0 under v1's exit test. So the landing-commit definition alone decides between miss and met (and only under a lenient reading of `other=`; see Finding 2).
- A1 (v2) at 68447af: `BIND rc=1 … dangling=1 fail`, `REGRESS-FULL tools/souji-landing-gate.py rc=0/0 lines=66/66 differs`, `SUMMARY-V2 … bind=fail … regress_full=differs`, rc=1. At the tip: `bind=ok … regress_full=differs`, rc=1. Byte-identical to `census/round-30/records/c2-after-v2.txt` at the landing commit.
- `regress_full` cause, controlled on the two 66-line selftests: 2 differing lines, both `CASE` lines whose only change is an `err=` tail ("… under .ufo/waves/round-18/ or census/round-18/waves/ …"). Character before `err=` is a space (`fleet=[] err=`); `c2-counter-v2.py:69` strips on `\terr=.*$`. Stripping on `\s+err=.*$` makes the outputs equal; the tab-anchored strip does not.
- Frozen-counter hygiene: `census/round-30/c2-counter.py` sha256 prefix `6cd15db9ce0f5555` at d4928ec, 02aea48, 68447af and 9dcd367 — the frozen instrument was never edited after freeze. `c2-counter-v2.py` prefix `31a78084a48ab560` at 02aea48 and tip.
- Reproducibility of the frozen BEFORE line: base gate run today against the live lane still prints `checked_reports=0` and `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-29/ at 9420341d9a81` (rc=2, dangling=3) even though the live `.ufo/waves/round-29/` holds 86 `.md` files — discovery reads the REV tree (`check_carry`: `p for p in tree if p.startswith(wave_prefix)`), so the counter is revision-deterministic, not run-order-dependent.

Quotes (bytes opened this run, ≤25 words, no pipe characters):
- `census/round-30/records/preregistration.txt:7` — "Kill rule: any other SUMMARY at the C2 landing commit or the final tip is a miss".
- `census/round-30/records/preregistration.txt:13` — "Causal separability: each counter is evaluable at its own landing commit without the others".
- `tools/souji-landing-gate.py:485-486` — "When both are committed the wave dir alone is read, so no report is ever counted twice".
- `census/round-30/c2-counter-v2.py:113` — "bind = reports == expected == 86 and ufo_md == 0 and cnef == 0 and dangling == 0".

## Findings

1. **Verdict correct (HOLDS).** 68447af + `dangling=1` + `rc=1` vs a frozen target naming `dangling=0` and exit 0; the kill rule admits no other outcome. The L1's reading is what the contract requires and must not be softened to "met at tip".
2. **The miss is cross-claim, and the frozen text does not say so.** The sole dangling is `SCORECARD.md:322`, a line C1 landed at 7b16731; the capture that resolves it lands two commits later at aea0525. The frozen claim `preregistration.txt:13` says each counter is *evaluable* at its own landing commit — true, it runs and prints deterministically — but it does not say the *target is satisfiable* there, and it is not: removing that one C1 line alone would print `dangling=0`. Additionally, under wave-1's strict reading of the `other=` tension (`deliver-cross-claim.md` §7: `other` must return to 0), `other=7` fails too, at 68447af and at aea0525, and is cleared only by the r29 carry at 936efc8. Either reading leaves C2's landing commit red. Suggest recording the miss under this attribution so operability is not scored down for a bookkeeping ordering artifact.
3. **"C2 landing commit" is undefined in the frozen text.** 68447af → miss; aea0525 → `dangling=0` (met under v1's exit test). The L1 chose the stricter of the two, which is the only defensible choice after data, but the ambiguity should be closed in the next preregistration (e.g. the commit named in the claim's after-measurement record, or the literal required at every commit from landing to tip). Not changeable this round.
4. **A1 as shipped cannot reach its own target at any revision.** `c2-counter-v2.py:69` strips `\terr=`; the selftest separates with a space, so the exempted `err=` tails are never stripped and `regress_full=differs` at 68447af *and* at the tip (rc=1 both). The underlying gate reword is the only difference and v1's REGRESS is `same`, so this is an instrument defect, not a gate regression. Smallest safe correction: `\s+err=` (stricter-only in effect: it removes a false red), logged; do not cite A1's target as met until it prints.
5. **A1's `bind` tests more than the amendment declares.** `c2-counter-v2.py:113` conjoins `dangling == 0`, so at 68447af it prints `bind=fail` although the binding is intact (`reports=86 expected=86 ufo_md=0 cne=0`). A1's BIND text (reports==86, no committed `.ufo` `.md`, private clone) does not include dangling. Mislabels a good binding as broken; keep the field but stop folding dangling into it.
6. **Records gap in the L1's own after-measurements.** `census/round-30/records/c2-after-v1.txt` and `c2-after-v2.txt` contain only the 68447af run; the tip half of the frozen target ("and the final lane tip") exists only in a wave-2 seat delivery (`.ufo/waves/round-30/w2/deliver-c2-rerun.txt`). My reruns reproduce both halves, but the round's committed receipt set should carry both before the w2 capture lands.
7. **Design note for r31, not a defect here.** `check_carry` prefers the wave dir when both are committed (`tools/souji-landing-gate.py:485-486`), i.e. the gitignored, force-addable source outranks the committed capture. Fixture D3 freezes this precedence, so it must not move this round; next round the capture should win when both exist.

## Attack log

- L1 C2 `MISSED` verdict at 68447af — **HOLDS**. Reproduced byte-identical; `dangling=1` and `rc=1` against a literal naming `dangling=0` and exit 0.
- 68447af is the C2 landing commit — **HOLDS**, with the reservation that the frozen text does not define the term (Finding 3).
- L1's cause attribution ("C1 SCORECARD block cited a wave path not yet captured, resolved at the capture commit") — **HOLDS**. One dangling line, `SCORECARD.md:322`; absent at 68447af (cat-file rc=128), present at aea0525 (rc=0), and dangling returns to 0 there.
- L1's v2 diagnosis ("err-stripping regex expects a tab where the selftest prints a space") — **HOLDS**. Character before `err=` is a space; `\s+err=` equalises the outputs, `\terr=` does not; r16 fixture identical throughout.
- Implicit reading that the tip is green — **HOLDS**. `dangling=0 other=0`, rc=0, and the frozen literal printed at 9dcd367.
- Alternative reading "landing commit = aea0525 ⇒ met" — **BROKEN as a rescue**. `dangling=0` there, but `other=7` fails wave-1's strict `other=` reading and the definition is post-data; both moves would relax the frozen text.
- A1 v2 target as printed — **BROKEN** at 68447af and at the tip (`regress_full=differs`, rc=1). Instrument defect, not a gate regression.
- Operability axis harmed by the landed gate — **REFUTED** (improved: reports 0→86, cne 1→0, dangling 3→1→0, exit 2→1→0, template false positives gone, 7 real uncarried findings surfaced, REGRESS same).
- Calibration harmed by the landed gate — **REFUTED**. `SELFTEST pass=65 fail=0` and r16 `total=15 failed=0` identical base vs REV; no selftest case added.
- Gate determinism under a dirty lane — **HOLDS**. Discovery and pointer scan read the REV tree; base line `reports=0 cne=1 dangling=3` still reproduces with 86 `.md` live in `.ufo/waves/round-29/`.

## Deliveries

- `.ufo/waves/round-30/w2/SwarmCritic17.md` (this report)
- `.ufo/waves/round-30/w2/SwarmCritic17-receipts.txt` (provenance, commit graph, R1–R8 raw runs, verdicts)

No file in the lane was modified; scratch `/fast/scratch/hyaku/souji-r30/SwarmCritic17` removed after the receipts were written. No tool installed or updated (git 2.56.0, python 3.14.8, jj 0.45.1 already present; no pacman transaction).
