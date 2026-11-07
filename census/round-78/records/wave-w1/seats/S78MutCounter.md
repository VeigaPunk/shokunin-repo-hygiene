# S78MutCounter — r78 C2 counter: mutation test of its new rules (falsification)

Verdict: every frozen C2 number re-derives at A 319109b0ddc836c6cf3364fdde3ab99796f21f32; the frozen artifacts kill 6/10 mutants, while M02/M04/M07/M09 survive every frozen forgery and control and die only to new rows; the pristine counter accepts 5 false ledger rows (NF1–NF5). No HIGH. Lane HEAD moved to bbd199da07dc6ce40ac428cdfd2321a6630442f4 (L1 integration) with the four C2 artifacts byte-identical to A; this seat wrote nothing in the lane.

Re-derived: base pointer check missing=22 is set-identical to the 22 population rows; missing=19 at 87d4561 and A. A: SUMMARY items=22 resolved=22 unresolved=0 refused=0 mismatched=0 errors=0 / FORGE-SUMMARY forged=12 matched=12 accepted=0 / EXIT=0. r77: items=35 resolved=35 / forged=7 matched=7 accepted=0 / EXIT=0. Base: prefreeze resolved=0 unresolved=22 with forged=12 matched=12; K-a 0/22; K-b 19/3; K-c (c2-forge-legacy.py) forged=7 matched=0 accepted=7 EXIT=1; K-d FATAL EXIT=2; K-e r77 status=MOVED, r78 status=REFUSED EXIT=0. Counter sha256 9a6a34fd…, population 7c04cdaf…, ledger b0e92fd7…, forge b52dcd84… all match at A and HEAD.

cmd: cd LANE && python3 -B $S/pristine/c2-pointer-counter.py --root LANE --rev A --fleet-root FLEET --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv

Mutant table (mutants/*.py, mutants.diff; A = r78 pop+ledger+forge, B = r77 set, g6 = adapted probes/g6-collision.sh; F = frozen forgery set, C = frozen control, P = new scratch probe; A/B cells = resolved/matched, accepted=0 unless shown)
| mutant | change | A | B | g6 | killed by |
|---|---|---|---|---|---|
| M01 | MOVED round-<N> check removed | 22/22, 12 match | 35/35, 7 match | P04=MOVED | C K-e |
| M02 | MOVED last-component check removed | 22/22, 12 match | 35/35, 7 match | P04=REFUSED | P FP2 (P04=MOVED) |
| M03 | QUARANTINED dirname check removed | accepted=1 (LF02) | accepted=2 (F03,F05) | REFUSED | F |
| M04 | QUARANTINED fleet refusal removed | 22/22, 12 match | 35/35, 7 match | REFUSED | P FP8 (L16=QUARANTINED) |
| M05 | TOKEN next-line accepts any rest | 22/22, 12 match | accepted=3 (F01,F02,F06) | REFUSED | F |
| M06 | TOKEN template r<N> check dropped | 22/22, 12 match | accepted=2 (F02,F06) | REFUSED | F |
| M07 | template literal-equality check removed | 22/22, 12 match | 35/35, 7 match | REFUSED | P LP2 (P22=TOKEN) |
| M08 | population sha256 pin bypassed | 22/22, 12 match | 35/35, 7 match | REFUSED | C K-d (EXIT=1 errors=1, not FATAL EXIT=2) |
| M09 | forge matched==forged -> accepted==0 | 22/22, 12 match | 35/35, 7 match | REFUSED | P LP3 (EXIT=0 on expect=MISMATCH/got=REFUSED) |
| M10 | forge row judged with ledger row | matched=0 accepted=12 | matched=0 accepted=7 | REFUSED | F |

Frozen artifacts alone kill 6/10: M03, M05, M06, M10 by forgeries; M01 by K-e; M08 by K-d. COVERAGE FINDING (MEDIUM): M02/M04/M07/M09 are invisible to every frozen artifact — no frozen forgery exercises the MOVED basename binding, the QUARANTINED fleet refusal, the template literal check independent of r<N>, or an expect=MISMATCH row; each needed a row outside both frozen sets.

Accepted false ledger rows (false-rows.tsv; NF1 on lane bytes at A; NF2–NF5 on scratch clone rev 6f44938f0d6369a26ef516c10029c711145f6acc; none in either frozen set):
- MEDIUM NF1 P19 TOKEN census/round-73/records/c2-after-D1.txt -> got=TOKEN accepted=1 (lane A): one of the five named receipts resolves the item; D2–D5 need not exist.
- MEDIUM NF2 P19 TOKEN census/round-73/records/c2-after-D9.txt -> got=TOKEN: '..' checks stem/suffix/digit only (:181-191), never the D1..D5 span.
- MEDIUM NF3 L02 MOVED census/round-02/operator-sweep-20261019 -> got=MOVED: token has no round-<N>, so a byte-equal copy at an arbitrary directory passes (:222-226); G6 fixed only round-named tokens.
- LOW NF4 L06 QUARANTINED .ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/NOT-THE-STUB -> got=QUARANTINED: leaf name/bytes unbound (:237-246; real leaf dot-git-empty-stub).
- LOW NF5 L13 TOKEN census/round-49/sources/s272-python-open-l -> got=TOKEN: any prefix of the wrapped continuation resolves (:178).

file:line evidence: census/round-78/c2-pointer-counter.py:216-226 (MOVED), :237-246 (QUARANTINED), :146-156 (_template_ok), :178 (next-line), :181-191 (range), :295-299 (pin), :345/:353 (forge).

Files written under .ufo/waves/round-78/w1/S78MutCounter/: S78MutCounter.md, mutants.tsv, mutants.diff, matrix-at-A.tsv, controls-at-base.tsv, probes-raw-1.tsv, probes-raw-2.tsv, g6-mutants.tsv, false-rows.tsv, repro.txt, g6-mutant.sh, and mutants/M01-moved-round-binding-removed.py, mutants/M02-moved-basename-binding-removed.py, mutants/M03-quarantine-dirname-binding-removed.py, mutants/M04-quarantine-fleet-check-removed.py, mutants/M05-token-nextline-any-rest.py, mutants/M06-token-template-rN-dropped.py, mutants/M07-template-literal-check-removed.py, mutants/M08-population-pin-bypassed.py, mutants/M09-forge-match-replaced-by-accepted-zero.py, mutants/M10-forge-judged-with-ledger-row.py.
