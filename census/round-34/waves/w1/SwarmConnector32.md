## Status
STATUS: PASS — scoped sibling overlap scan completed; overlap disclosures only.

## Evidence
- Read frozen contract first: `census/round-34/preregistration.txt` at frozen `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; C1 calibration and C2 operability are separate claims (lines 13-25, 75-88, 117-132). Counter docstrings and frozen item/leg files also read.
- Search: case-insensitive regex `bwrap|bubblewrap|strace|work witness|sandbox|load-stable|private bind|gate registry|restatement|row agreement` across sibling `PROVINCE.md`, `SKILL.md`, `SCORECARD.md`, `corpus/QUALITY.md`, and `corpus/knowledge/*.md`; `souji-shokunin` excluded. Search output surfaced relevant matches in Chousa, Kagi, and Tameshi; scope and selected anchors are recorded in delivery below. Search was broad enough to include unrelated fleet scratch/prompt hits in an initial root search; those are excluded from findings.
- Revision evidence: preregistration hash anchor `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` as specified in task; sibling files were read from current local checkouts (no sibling revision pin was supplied).

## Findings
1. **Chousa, direct conceptual overlap / distinct unit.** `chousa-shokunin/SKILL.md:89-93` has numeric command measurement rows; `chousa-shokunin/SCORECARD.md:2428` says the gate registry agrees with its checked tree. Quote from opened bytes: “the lane's own gate registry now agrees with the committed tree” (SCORECARD.md:2428). Report scope distinction: tree/entry-point membership is not Souji's per-row measured-output agreement.
2. **Kagi, registry + isolation boundary precedent.** `kagi-shokunin/SKILL.md:694-718` includes gate registry and explicitly limits scratch fixture evidence; `:780-782` distinguishes author-side measurement from independent admission/hostile-program sandboxing. Quote: “a scratch fixture is not a live-host pass.” (`SKILL.md:718`). Report scope distinction: do not treat as evidence for Souji's concrete bwrap/strace legs.
3. **Tameshi, direct sandboxed-probe overlap / different subject.** `tameshi-shokunin/corpus/knowledge/guard-kill-closure.md:129` describes bwrap probes and limits their boundary; `hermetic-env-differential.md:25-29` documents fresh bwrap scratch and limits; `regression-tally-completeness.md:42,68` documents a sandboxed selftest. Quote: “The envelope is a sandbox for the probes, not a proof of containment for the tools under test.” (`guard-kill-closure.md:129`). This does not demonstrate Souji's /var/tmp private bind, work witness, or load-stable anchor.
4. **Kumitate, adjacent rather than equivalent.** `tameshi-shokunin/corpus/knowledge/mutation-case-kumitate-round-gate.md:21-23,145-147` reports strace observation and treats bwrap confinement as a next step, not an already-executed matching witness.
5. **Kagi boundary disclosure.** `kagi-shokunin/SKILL.md:303` says its text guard is not a sandbox; this is a negative boundary, not a Souji implementation proof.

## Attack log
None. No reproduced state against either frozen claim.

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-sibling-overlap.md` — overlap findings and contested scope.