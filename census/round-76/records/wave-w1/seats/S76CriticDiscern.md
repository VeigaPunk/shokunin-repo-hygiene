# S76CriticDiscern — discernment attack, souji round 76 (lane HEAD eef6f30c7be607d7590898da53496408f5fa9545; base ee59aa4d)

I re-derived every number below from committed bytes; full transcript: .ufo/waves/round-76/w1/S76CriticDiscern/evidence.txt

## 1. Routed r75 defects
| item | verdict | evidence |
|---|---|---|
| spot-check 1 probe cannot fail | ADDRESSED | census/round-76/probes/repro-coreworktree.sh:28-33 computes VERDICT and exits 1/0/2; my runs: 620ed97e & 062b6d39 -> `VERDICT=FORGERY EXIT=1`, ef3b04e4 & 18587bd2 -> `VERDICT=REFUSED EXIT=0`. Residual: records/probe-coreworktree-at-r75W.txt binds no gate digest (LOW, F4) |
| spot-check 2 core.excludesFile arm | OPEN | c1-population.tsv new rows are f9/f10/f14/f11/f12 only; f3 still refused by the r75 `hidden` difference block (gate:106-110) before the r76 block runs; Q136 keeps the same limit |
| spot-check 3 domain-trial revision | OPEN (unrecorded) | `git ls-tree -r eef6f30c census/round-76 | grep -i domain` = empty, yet C1 Target makes it a kill conjunct; I reproduced `check-clean=PASS` with blob 18587bd2, EXIT=0, 4.7 s (F3) |
| lesson (a) Y4/Y5 witnesses | OPEN | `git grep -lE 'Y4|Y5|new-slot' ee59aa4..HEAD -- census/round-76` = empty |
| lesson (b) receipt-to-mutant binding | ADDRESSED | my re-run: b-swap-x09-gets-m08 SUMMARY unbound=2 rejected, SUMMARY cases=10 mismatches=0 EXIT=0. Limit real: F5 |
| lesson (c) ls-files branch + refusal class; r27/r36 conjunct | PARTIAL | r27 4/4, r36 21/21 reproduced with the candidate gate bound (18587bd2); no row exercises the new `tracked-file listing failed` branch or refusal order |
| lesson (d) carried set | OPEN | no r76 byte; Q136 still says "the other status-trusting tools stay routed" |
| spot-check 5 stated limit (self-ignoring .gitignore) | ADDRESSED (mechanism) / PARTIAL (corpus) | 30 rows 0 mismatches at W vs 4 [f7 f9 f10 f14] at base; Q136 not superseded (F2) |

Claim re-derivations: C1 30/0 EXIT=0; C2 10/0 EXIT=0, do-nothing 5, blanket 2, h-honest killed=6; r27 4/4; r36 21/21. All match the committed receipts.

## 2. QUALITY literals
- **Q99: literal PASS.** `git rev-parse 2ed6b179^` = 6c9c2a8e (P strictly before F); ee59aa4 ancestor of F; the four Counter/Population digests at F equal the prereg (618e4f9a/937e4a9b, e22f634e/c46ea8ff); Control blobs at F end `EXIT=1`; blobs byte-identical F..tip; no `*-dispatch.json`/`*.ready` under .ufo/waves/round-76; `tools/souji-freeze-check.py --rev 2ed6b179` -> `SUMMARY claims=2 findings=0` EXIT=0 (same at HEAD).
- **Q120: literal PASS on form.** Controls in P (strictly before F) carry command=/rev=/instrument_sha256= plus the tested-instrument digest (gate ef3b04e4; variants 36f06903, 43ebc213, 7d780b60 = committed blobs; r75 tally fdb75c09); expectations come from the frozen population, not the tested bytes. Note r27/r36/domain are Target conjuncts executed at A/W, not the no-work/forgery controls, so they do not breach Q120.
- **Q136 needs a superseding row.** Its first stated limit ("an untracked `.gitignore` that ignores itself … passes") is false for the landed gate (`.jj/` now attributes to `:4:.jj/`), and the S320 mechanism is unregistered. Proposed Q137 (60 words, in evidence.txt): "Supersedes Q136's untracked-.gitignore limit clause (the rest of Q136 stands). Every ignored untracked path's deciding pattern must come from a tracked .gitignore in an ancestor dir (check-ignore -v, core.excludesFile attributed away, S320); otherwise the gate refuses, counting only. Limits: a committed rule broad enough to hide a forged file still passes; .jj/ and .ruff_cache/ pass only because .gitignore names them." S320 row text also in evidence.txt.

## 3. Mission fit
Consistent, with one condition: the rule refuses only *unattributable* hiding; `.jj/` is VCS state, and it now passes because W declared it in the tracked .gitignore — declared policy is exactly what a census can list and quarantine, while a self-ignoring untracked rule cannot be. The tradeoff is real: refusing self-ignore incentivises committing a rule, and any committed rule still passes (f2, f11 both PASS; the lane's own fix is an f11). So the improvement reduces hiding that has no versioned provenance, not hiding. That is the honest limit, not a defect.

## Findings
- **F1 MEDIUM** — S320 is cited by preregistration.txt (C1 block) and gate:111-114, but `grep -rn 'S320' corpus/ SKILL.md SCORECARD.md LOG.md` has no row at HEAD: the claim's citation resolves to nothing. Capture is honest (sha256 940177c7…, 4159 B, byte-identical to upstream v2.56.0); row text supplied.
- **F2 MEDIUM** — QUALITY.md has no row for the r76 rule and Q136's self-ignore limit is now false for the landed gate; Q137 above should land at the report tip (`grep -c '^| Q137' corpus/QUALITY.md` = 0).
- **F3 MEDIUM** — the C1 domain-trial conjunct is unrecorded although reproducible (I ran it); without a committed receipt the kill clause cannot be scored from the round's own bytes.
- **F4 LOW** — records/probe-coreworktree-at-r75W.txt names a scratch gate with no digest; the FORGERY arm is only verifiable at 620ed97e/062b6d39 (my measurement), not at the path it cites.
- **F5 LOW** — C2 binding is header-level: a receipt keeping X15's correct instrument_sha256 with a fabricated consistent body reads `verdict=KILLED` and the tally exits 0 (killed=7/7). This is the prereg's disclosed "binding proves which instrument a receipt names, not that it ran"; it belongs in the row text so "binds every receipt" is not overread.

Commands: `python3 -B census/round-76/c1-evade-counter.py --gate-dir <S>/{w,gb} --work <S>/{c1,c1b}`; `python3 -B census/round-76/c2-binding-counter.py --tally {census/round-76/c2-kill-tally.py, census/round-75/c2-kill-counter.py, census/round-76/controls/variants/tally-K-b-reject-all.py}`; `bash <S>/w/souji-pre-report-gate.sh --lane <lane> --branch master --report <S>/report.md --prereg census/round-76/preregistration.txt`; `bash census/round-76/probes/repro-coreworktree.sh <gate> <S>/pr` x4; `python3 -B tests/fixtures/r36-report-gate.py --work <S>/r36 --gate <S>/w/…`; `env TMPDIR=<S>/r27 bash tests/fixtures/r27-pre-report-gate.sh`; `python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-76/preregistration.txt --rev {2ed6b179,eef6f30c}`; `git check-ignore -v -n -z` on the lane's `.jj/` paths; `curl` of the S320 URL.
Files written: .ufo/waves/round-76/w1/S76CriticDiscern.md (this), .ufo/waves/round-76/w1/S76CriticDiscern/evidence.txt. Lane tracked files untouched; scratch /fast/scratch/hyaku/souji-r76/S76CriticDiscern removed.
