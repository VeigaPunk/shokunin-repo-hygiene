# S77MutCounter — r77 w1: C2 counter mutation + forged-ledger falsification
Verdict: 9/10 single-edit mutants survive the five committed controls under the "still red" criterion (only M09 is killed); the frozen counter accepts 6/6 forged ledger rows. K-b/K-c/K-e are aggregate-red only: a per-row forgery passes while EXIT stays 1.
Baseline (pristine must pass): frozen counter sha256 8904de85... (census/round-77/c2-pointer-counter.py), population bbc19ac6..., ledger 011faa0e... reproduces every ITEM/SUMMARY line and EXIT of the five receipts: K-a 0/35; K-b resolved=4 refused=31; K-c resolved=0 refused=4 unresolved=31; K-d mismatched=4 unresolved=31; K-e refused=3 unresolved=32; honest at A: `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` EXIT=0.
Commands: `python3 -B <counter> --root <lane|stubclone> --rev <BASE|A|HEAD> --fleet-root /home/vgpnk/Projects/shokunin [--ledger <variant|honest>]` via `/fast/scratch/hyaku/souji-r77/S77MutCounter/harness.py` (11 instruments x 6 runs, timeout -k 5 1500); K-d control clone built by census/round-77/controls/variants/c2-K-d-stub-build.sh, HEAD dbeba551. Every mutant is one diff hunk with population bytes unchanged.

Mutant table (strict = all control lines identical to receipts; red = all five EXIT=1; honest = ledger at A 35/35):
| mutant | strict | red | honest | verdict | forgery admitted |
| M01 r0-drop | yes | yes | 35/35 | SURVIVED | a population row whose token is not on the cited base line scores (D1: frozen ERROR -> M01 CAPTURED); c2-pointer-counter.py:202 is the only binding and the population sha is printed, never pinned |
| M02 captured-no-digest | yes | yes | 35/35 | SURVIVED | a stub at a '-' (no frozen digest) token resolves CAPTURED (D2: frozen MISMATCH -> M02 CAPTURED); :208 |
| M03 moved-no-compare | no | yes | 35/35 | SURVIVED (receipt differs) | K-e's own 3 rows flip (P04 P09 P31; refused 3->0, resolved=3) yet K-e stays red on 32 unresolved; :228 |
| M04 local-no-prefix | no | yes | 35/35 | SURVIVED (receipt differs) | K-c's own 4 rows flip (P09 P10 P11 P18; refused 4->0, resolved=4) yet K-c stays red on 31 unresolved; :233 |
| M05 fleet-no-ufo | yes | yes | 35/35 | SURVIVED | latent: FLEET for any fleet-root token outside .ufo/; no witness in the frozen population (every '-' FLEET-eligible token already starts .ufo/); :245 |
| M06 token-no-continue | yes | yes | 35/35 | SURVIVED | TOKEN to any existing file, not a continuation (D4: P22->SCORECARD.md, frozen REFUSED, M06 TOKEN); :138 |
| M07 absent-no-history | yes | yes | 35/35 | SURVIVED | latent: ABSENT for history-recoverable bytes; no '-' token has history (only P09-P11/P18, refused earlier by their frozen digests); :254 |
| M08 absent-no-artefact | no | yes | 35/35 | SURVIVED (receipt differs) | reintroduces the pre-P bug the prereg says was fixed; K-b's 6 rows flip (P06 P19 P21 P22 P23 P27; 4/31 -> 10/25) yet K-b stays red; :250 |
| M09 refused-as-resolved | no | NO | 35/35 | KILLED | K-b green: resolved=35 EXIT=0 (ITEM lines still print REFUSED); :257 |
| M10 ignore-unknown | yes | yes | 35/35 | SURVIVED | unknown/duplicate ids silently ignored (D8: honest+P99 frozen EXIT=1 -> M10 EXIT=0, 35/35); :196 |

Forged ledgers the FROZEN counter accepts (one-row ledgers at A; G6 in a clean clone; resolved=5 = 4 R1 captures + the forged row):
| row | counter item | misdesc | severity | why |
| G1 P22 TOKEN census/round-76/c1-evade-counter.py | status=TOKEN | yes | HIGH | corpus/QUALITY.md:150 template is `census/round-<rd>/records/preregistration.txt`; wrong final component, only the prefix is checked |
| G2 P23 TOKEN corpus/lessons/round-3.md | status=TOKEN | yes | LOW-MED | round 3 vs the row's round-29 evidence; rd is unbound so the counter cannot tell |
| G3 P08 FLEET - | status=FLEET | yes | LOW | .ufo/l0-questions.md is not runtime (class doc says runtime); the landed ledger already carries this row |
| G4 P02 QUARANTINED <any quarantine path> | status=QUARANTINED | yes | HIGH | the target is never related to the token; any '-' item resolves with any existing .ufo/quarantine path |
| G5 P08 QUARANTINED <same> | status=QUARANTINED | yes | MED-HIGH | .ufo/l0-questions.md is live under the fleet root; QUARANTINED does not check fleet or history |
| G6 P04 MOVED census/round-02/waves/a2w1/SwarmExecutor08.md | status=MOVED | yes | MED | byte-equal copy (sha256 d0693448... equals the frozen digest) in an unrelated round; MOVED proves bytes, not location |

Findings: HIGH-1 K-b/K-c/K-e redness is aggregate; M03/M04/M08 flip the controls' own forged rows while EXIT stays 1 (only a byte-diff of the frozen SUMMARY literals catches them). HIGH-2 QUARANTINED target is unbound (G4/G5). HIGH-3 R0 is unexercised and the population sha is never asserted (D1). MEDIUM TOKEN prefix-only (G1); MOVED byte-identity-only (G6). LOW FLEET label (G3); unexercised M05/M07/M10 branches.
Caveat: every mutant changes the pinned instrument sha (8904de...), so identity pinning alone kills all ten; this table measures behavioral coverage, not the freeze check.
Files written (seat dir .ufo/waves/round-77/w1/): S77MutCounter.md; S77MutCounter/mutant-matrix.tsv; S77MutCounter/forged-ledger.tsv; S77MutCounter/demos.txt; S77MutCounter/mutants.diff. Scratch removed; no lane tracked file touched, no commit/jj mutation.
