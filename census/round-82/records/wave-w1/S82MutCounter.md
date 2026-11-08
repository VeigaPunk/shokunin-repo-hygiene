# S82MutCounter — mutation probe of W1 census/round-82/c1-pointer-counter.py (r82 C1). VERDICT: the frozen C1 claim holds; 8 mutants, 6 killed, 2 survivors (1 MEDIUM coverage gap, 1 equivalent).

Baseline REPRODUCED on lane bytes sha256 cbfdc07c0d5de31f83555747e45f7335bf5584635c7f4665431048880db1875a (= git blob at W1 f5bc4197…): harness `SUMMARY rows=32 mismatches=0 accepted=0 refused_true=0 errors=0` EXIT=0; r78 `items=22 resolved=22` + `forged=12 matched=12 accepted=0`; r77 `items=35 resolved=35` + `forged=7 matched=7 accepted=0`. Controls re-derived red: K-a/K-b 2 accepted (NF-F,NF-G), K-c 2 accepted (NF12c,NF-I) — matches the committed receipts.
Commands (cwd lane): `python3 -B census/round-82/c1-false-row-harness.py --counter <M> --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work <S>/w-<M>`; `python3 -B <M> --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root <fleet> --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv` (r77 pair as frozen).
Mutants (pristine copy byte-identical; one asserted replacement each; full lines in mutants.txt):
M01 drop _owntree_ok branch (:353-356) — KILLED harness mism=2 acc=2 (NF-F,NF-G=MOVED); both regressions green.
M02 _owntree_ok suffix-only both branches — KILLED harness refused_true=1 (TF4).
M03 _capture_ok -> last-component — KILLED harness mism=2 acc=2 (NF12c,NF-I).
M04 drop `token[:kr.start] != "census"` guard (:361) — SURVIVED all 3; EQUIVALENT: :353 already decides every reachable census-token case with the same _capture_ok (pristine/M04 judge agree MOVED/REFUSED on a synthetic census-token axis).
M05 `records/wave-[^/]+/` -> `records/[^/]+/` — KILLED harness acc=1 (NF-H).
M06 suffix -> prefix — KILLED harness refused_true=4 (TF1,TF2,PF-1,TF5); r78 21/22 (L15 REFUSED), r77 34/35 (P31 REFUSED).
M07 own-tree equality -> suffix, _capture_ok kept — SURVIVED all 3; accepts NR6 below (MEDIUM coverage gap).
M08 own-tree equality clause dropped — SURVIVED all 3; EQUIVALENT: tt==tk implies target==token (round digits already equal at :351), so judge returns CAPTURED/MISMATCH at :330-334 before MOVED.
New rows (fixture R5 d1ed98f4…, R6 1f3d82bf… built with the harness's build_fixture; item P04; details newrows.txt):
NR1 `census/round-32/records/wave-./SwarmExecutor08.md` — ACCEPTED (digest matches; `records/wave-[^/]+/` matches "wave-."). False capture, yet NF-C stays a stated limit: no real row grounds a wave-name validity rule (only real `records/wave-*` row is r78 ledger L21 `wave-w1`).
NR2 `…/a2w1/../a2w1/…` — REFUSED, rev_digest None (git cat-file rejects `..` in `rev:path`). NR3 `census/round-32//waves/…` — REFUSED, rev_digest None (cat-file does not normalize; ls-tree does). Both false, refused before any shape rule.
NR4 symlink at `records/wave-z/waves/a2w1/SwarmExecutor08.md` (mode 120000) — REFUSED: `l:5bc93b81…` vs frozen `f:d0693448…`. NR5 `…SwarmExecutor08.md.bak` — REFUSED (basename differs).
NR6 `.ufo/waves/round-32/SwarmExecutor08.md` — REFUSED by pristine, MOVED by M07/M02: own-tree analog of NF12 (`census/round-32/decoy/…`) is absent from the 32 rows. Genuinely false under the frozen rule; coverage gap, not a pristine defect.
Findings: MEDIUM — M07/NR6: a suffix-only own-tree rule passes all three conjuncts; the population has no own-tree flattened/short-suffix decoy (NF-F/NF-G test wrong suffixes, TF4 tests a capture). LOW — `_owntree_ok`'s `tt == tk` clause is unreachable (M08), and the prereg + code comment at :368 claim "_owntree_ok before the basename test" while the bytes run basename at :349 before owntree at :353 (outcome-equivalent, so no verdict change). LOW — NF-C accepted, as the prereg discloses.
Restoration: lane counter sha256 cbfdc07c… before and after; no tracked lane file written; scratch /fast/scratch/hyaku/souji-r82/S82MutCounter removed; `ps` shows no leftover process; no tools installed.
Files written: .ufo/waves/round-82/w1/S82MutCounter.md, .ufo/waves/round-82/w1/S82MutCounter/mutants.txt, .ufo/waves/round-82/w1/S82MutCounter/newrows.txt
