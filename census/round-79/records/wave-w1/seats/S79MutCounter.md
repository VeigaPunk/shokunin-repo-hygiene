# S79MutCounter — r79 C2 counter falsification (seat S79MutCounter)

Verdict: the frozen C2 numbers reproduce exactly; the counter's claimed coverage does not hold. 13 single-change mutants of its four r79 rules and their helpers: 5 killed, 8 survived. The pristine counter still ACCEPTS 2 false QUARANTINED rows, 1 false range row and 1 contract-satisfying MOVED row I built; a 5th (a `fleet:` range) is accepted only with a staged fleet root.

## Reproduced (counter = 17009fa1:census/round-79/c2-pointer-counter.py sha256=f597909b2bd4c06bd435c284b580deacdd82c5cfe335c1c8ba578ab9fe5ed703 = lane HEAD bytes; git diff W2..HEAD empty)
command=python3 -B census/round-79/c2-false-row-harness.py --counter census/round-79/c2-pointer-counter.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work <S>/base/h1
  `SUMMARY rows=9 mismatches=0 accepted=0 errors=0` EXIT=0 and `# fixture rev=6436db6a8ea2d9d0deea6f57cbc160fafa4c6c23` (the frozen fixture rev).
command=python3 -B census/round-79/c2-pointer-counter.py --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv
  `SUMMARY items=22 resolved=22 ...` / `FORGE-SUMMARY forged=12 matched=12 accepted=0` EXIT=0; r77 set: `items=35 resolved=35` / `forged=7 matched=7 accepted=0` EXIT=0.

## Mutants (one hunk each, anchor-count==1; sources <S>/mut/M01..M13.py, diff .ufo/waves/round-79/w1/S79MutCounter/mutants.diff; per-mutant output .../probes.txt)
M01 range set-test -> "any member of the expansion": SURVIVED (9/9, 22/22, 35/35)
M02 range span bound (hi<lo | hi-lo>999) -> False: SURVIVED (no population range spans >999)
M03 range zero-pad width -> 0: SURVIVED (no zero-padded range token in either population)
M04 wrapped continuation -> run.startswith(rest): KILLED by NF5 (mismatches=1 accepted=1)
M05 wrapped clause deleted: KILLED by r78 (resolved=21 refused=1, L13 LOG.md:2308)
M06 no-round MOVED refusal deleted: KILLED by NF3
M07 MOVED round equality -> prefix match: SURVIVED
M08 QUARANTINED _declared call deleted: KILLED by NF4
M09 _declared token-in-line -> "any line names the target": SURVIVED
M10 AUTHORITY -> ("LOG.md",): KILLED by r78 L06 and r77 P14 (resolved 21/22, 34/35)
M11 range duplicate-count guard deleted: SURVIVED
M12 AUTHORITY += README.md: SURVIVED
M13 _declared grep at HEAD instead of --rev: SURVIVED
Kill ratio 5/13. Detector rows the frozen set lacks (kills the survivors, pristine refuses each): DM01 P19 TOKEN D1;D2;D3;D4;D9 -> REFUSED / M01 TOKEN; DM07 P04 MOVED corpus/round-321/decoy/SwarmExecutor08.md -> REFUSED / MOVED; DM11 P19 D5 listed twice -> REFUSED / TOKEN; NF6c L06 .../ghost-stub -> REFUSED / M09 QUARANTINED; NF6d .../readme-stub -> REFUSED / M12 QUARANTINED; NF6e .../late-stub at rev 0c0554d2 -> REFUSED / M13 QUARANTINED.

## False rows the pristine counter ACCEPTS (fixture fx.GcYKJM REV1 1700f276 / REV2 0c0554d2 / REV3 62054b7a / REV4 1a7ca607; rows in .../fixture.txt)
NF6a L06 QUARANTINED `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/denied-stub` -> got=QUARANTINED; the only line naming it says "we will NOT declare .../denied-stub for tests/vault/vadv54-run/p/p6repo/.git" (control: same row at REV1 -> REFUSED). LOW — exercised the prereg's stated limit (declaration bound to text, not bytes), here a refusal sentence.
NF6b L06 QUARANTINED `.../other-stub` -> got=QUARANTINED; the line names `.../other-stub.bak` and `.../p6repo/.gitignore-p6repo`, so token and target both match as SUBSTRINGS of different paths (control at REV2 -> REFUSED). MEDIUM.
NF8 P19 TOKEN all five `census/round-73/records/c2-after-D1..D5.txt` with D3.txt a DIRECTORY -> got=TOKEN (rev_digest tree is non-None; the expansion test compares names, not bytes). LOW.
NF10 P04 MOVED `corpus/round-32/decoy/SwarmExecutor08.md` (byte-equal copy, unrelated subtree) -> got=MOVED (G6 basename + same round only). LOW, contract-satisfying.
NF9 P19 range satisfied entirely by `fleet:` members -> got=TOKEN with a staged fleet root, REFUSED under the real fleet root (/home/vgpnk/Projects/shokunin has no census/). LOW, latent.

## Findings
HIGH none. MEDIUM: NF6b substring binding (rule intent broken without any false prose); the frozen population has no detector for M01/M07/M09/M11/M12/M13 and never exercises M02/M03's helpers, so 8/13 real weakenings pass. LOW: NF6a, NF8, NF10, NF9.
Files written: .ufo/waves/round-79/w1/S79MutCounter.md; .ufo/waves/round-79/w1/S79MutCounter/{baseline.txt,mutants.tsv,mutants.diff,probes.txt,fixture.txt}. No tool installed; scratch removed; no lane file written.
