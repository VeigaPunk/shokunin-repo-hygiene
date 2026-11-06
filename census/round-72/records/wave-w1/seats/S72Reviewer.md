# S72Reviewer — round-72 falsification review (2026-11-06)

Scope: git diff 0bf098dd..2ec8b63 -- census/round-72/ corpus/ SKILL.md; mk-counter.py vs resulting counter.
Method: re-derived every number from committed bytes; live re-runs of all frozen invocations from
/fast/scratch/hyaku/souji-r72/S72Reviewer (removed). No lane tracked file touched.
Note: no LSP server answers in this seat; all checks were direct code reads plus live execution.

## Verdicts

1. mk-counter regen — SOUND. Rebuilt census/round-71 inputs (sha 7e5a694a…, e1a3c00b…, 0d484aa5…,
   identical at 0bf098dd and 23372f36) + mk-counter.py in a scratch lane layout; ran it; outputs cmp
   byte-identical to the candidate commit's census/round-72/c1-counter.py (sha 7578447d…) and
   c1-matrix.tsv (cd8490b4…): "REGEN-EXACT-MATCH", rows=75 base_accept=31 (31 = 19 honest + 7 r71
   forging + 5 FW base_expect=accept; cross-checks honest receipt base_forgeries=12 + base_honest=19).
2. Base expectations — SOUND, circularity declared and bounded. All 70 carried base_expect equal the
   r71 records/c1-after.txt CASE base= verdicts (programmatic check: bad=[]); the 5 FW rows equal the
   probe's base=accept (fw-shapes-probe.txt). Circularity: base_expect are observed verdicts, so they
   bind continuity, not normative correctness — they catch any fixture/counter regression that changes
   base behavior (control (d): r71 counter+Y6 prints base_forgeries=2, EXIT=0 — reproduced live:
   EXIT=0, CASE-identical). Selftest (9a) re-measures the 7 witness rows live against the committed
   base bytes each run; non-vacuous: len(wrows)==len(WITNESS_ROWS) required (c1-counter.py:1747).
   Cannot catch: an expectation wrong since r71. Independent anchors: FW refusal classes (git docs
   S312-S314) and the r60 regress fixture.
3. Counter diff — SOUND. Carried rows unchanged: diff is additive only (CASE_SPECS +5 FW entries;
   _row_env tuple +3 kinds at :1046-1048; inrun_argv/mutate new branches keep the same final raises;
   FIXTURE_REL/FIXTURE_LAST_WANT untouched; only COUNTER_REL updated). base_mismatches counted on
   every path: build error :1211, run error via judge "error" != base_expect :1238-1239; claim gate
   fails closed :1296 (c.get default 1). (9a) really runs witness rows against the base writer
   (evaluate at :1743) and cannot pass vacuously (:1747). (9e) environ restore correct: saved before,
   restored/popped in finally (:1780-1789).
4. Preregistration vs receipts — SOUND, no mismatch. All six frozen sha prefixes reproduce
   (c1-mutants.json cfc40608…, battery SHA256SUMS cfd51315…, battery-manifest 99c9a55f…, harness
   6c7bf41d…, r71-Y6 variant 2e38ca9d…, base writer 118597e0…); tip/base writer b7790001… unchanged.
   6/6 r71 seat mutants reproduce seat files byte-for-byte (occ=1 each); r72-Y6 variant ==
   r72counter+Y6edit; battery members == base writer + one single-occurrence edit each; sha256sum -c
   OK x5. Probe: 10 accept in 35, EXIT=0; probe ts 17:35:27 < freeze commit 17:46:24.
   Controls: (a) 5/6/6, score=6 EXIT=1; (b) CF1 positive FAIL EXIT=2 (variant sha 435f17c4… matches);
   (c) kills=0 survived=5 EXIT=1; (d) EXIT=0 — all match. Claims: C1(i) 11/11+4/4 score=0 EXIT=0;
   C1(ii) base_mismatches=10 EXIT=1; C2(i) BATTERY 5/5 all_match=true EXIT=0; C2(ii) new_honest=19
   base_mismatches=0 EXIT=0 — all reproduced live, CASE/MUTANT/POSITIVE/SUMMARY lines diff-identical
   to the committed receipts. Live kill attribution: each mutant fails exactly its targeting check
   (X6 error gate; X7/X8 pathspec env; X9/X10 member binding; Y1 :1757; Y9 :1761; Y4/Y6/Y10 base
   witness :1746; Z1 :1771) — no accidental kills; all 11 old-strings single-occurrence in r72.
5. SKILL.md r72 rows — SOUND. Row "r72 filter-witness matrix": verdict map matches claim_upheld
   (:1291-1296) + battery_verdict rc (all_match ∧ survived=0 ∧ error=0, base-independent; MUTANT lines
   merely print base_mismatches, :1925); "2 = could not evaluate" matches fatal() EXIT=2 (:1460-1463);
   "(44 checks)" matches SELFTEST cases=44. Row "r72 counter-mutant set" matches harness rc mapping
   (0 = positive PASS ∧ score=0; 2 = invalid/positive-FAIL). Commands reference existing committed
   paths; placeholder style consistent with the r71 rows.

## Findings
- LOW census/round-72/c1-counter.py:1207 — build-error CASE line omits the base_expect= field that
  normal CASE lines print (:1242). Counts correct (:1211); cosmetic asymmetry only.
- LOW (environment, not lane bytes) — one transient mutant-selftest subprocess crash during my
  before-harness rerun (Y4: rc=1, no SELFTEST line → fate=crashed); r71+Y4 then passed 39/39 twice.
  Harness tallies crashes into survived (fails closed), so no number changes; SUMMARY was identical.
- LOW/INFO corpus/knowledge/filter-filemode-witness.md r72 section — "git re-hashes a size-0 index
  entry through its filter on every status read" is mechanistic wording without a cited source; the
  FWw row behavior itself is measured (probe, WM8 battery kill, honest-writer refusal).
- INFO — C1 kills are mutant-set-specific (declared); WM7 fail-open, over-refusal of an honest
  configured-driver repo, smudge-only drivers, non-2.56.0 git stay unmeasured (declared limits).

Residual gaps: control (b) verified against committed bytes + code path, not re-executed; no tool
installs were needed (disk-guard: 408G free on /fast/scratch).

Files written: .ufo/waves/round-72/w1/S72Reviewer.md (this file). No other lane writes.
