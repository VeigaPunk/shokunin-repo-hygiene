# S86ExecC1 — C1 independent re-derivation (souji round 86)

Scope: re-derived both C1 arms end-to-end on the committed bytes, independently of the L1. No lane file modified; all scratch under `/fast/scratch/hyaku/souji-r86/S86ExecC1/` (deleted before yield, receipts copied into `.ufo/waves/round-86/w1/S86ExecC1/`). No tool installed; used system python3 only.

Frozen bytes exercised (sha256):
- census/round-86/c1-pointer-counter.py `8278ea4d41d0975b748419ba79de44d3eefc924d8f415071660def83f9fba1f3`
- census/round-86/c1-false-row-harness.py `2dac2e818c65bb9cd8a8361899b78cc33ddb91b9ba216d27e5b0f821804bc9d9`
- census/round-86/c1-mutants.json `6f055edea73e5b22d870cb1e85100251cf7ba47486519ed448582b1b9c6471a6`
- r85 population `1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42` (47 rows); r86 population `79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561` (49 rows); r84 `4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f` (44 rows). Verified: parsed rows r86[:47]==r85, r85[:44]==r84 (byte-level prefix, header comment lines excluded since they are `#`-prefixed and not counted).

Verdict: C1 claim reproduces exactly. Pristine arms green on both populations; r86 kills all eight mutants; r85 control kills six and leaves c7/m14 alive. One deviation from the seat spec found in §3 (battery FATAL exit code is 1, not 2).

## 1. Battery arms (verbatim)

Command A: `python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py --work <scratch/w_r85r86b> --only r85,r86 --expect-killed 14`
Full byte-for-byte output saved at `.ufo/waves/round-86/w1/S86ExecC1/battery-r85-r86.txt` (35 lines). Verbatim:

```
ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0
ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0
MUTANT m6-digest-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m6-digest-blind pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m6-digest-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m7-round-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m7-round-blind pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m7-round-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m8-w-only-shapes pop=r85 killed=yes mismatches=2 errors=0 exit=1
MUTANT m8-w-only-shapes pop=r86 killed=yes mismatches=2 errors=0 exit=1
MUTANT-PAIR m8-w-only-shapes pop=r85 killed=yes mismatches=2 errors=0 exit=1 | pop=r86 killed=yes mismatches=2 errors=0 exit=1
MUTANT m9-basename-only pop=r85 killed=yes mismatches=4 errors=0 exit=1
MUTANT m9-basename-only pop=r86 killed=yes mismatches=4 errors=0 exit=1
MUTANT-PAIR m9-basename-only pop=r85 killed=yes mismatches=4 errors=0 exit=1 | pop=r86 killed=yes mismatches=4 errors=0 exit=1
MUTANT m10-records-as-wave pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m10-records-as-wave pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m10-records-as-wave pop=r85 killed=yes mismatches=1 errors=0 exit=1 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m11-class-enum pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m11-class-enum pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m11-class-enum pop=r85 killed=yes mismatches=1 errors=0 exit=1 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT c7-census-in-tree pop=r85 killed=no mismatches=0 errors=0 exit=0
MUTANT c7-census-in-tree pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR c7-census-in-tree pop=r85 killed=no mismatches=0 errors=0 exit=0 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m14-short-shape pop=r85 killed=no mismatches=0 errors=0 exit=0
MUTANT m14-short-shape pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m14-short-shape pop=r85 killed=no mismatches=0 errors=0 exit=0 | pop=r86 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14
EXIT=0
```

Command B (control): same with `--only r85 --expect-killed 6`. Saved at `.ufo/waves/round-86/w1/S86ExecC1/battery-r85-only.txt`. Verbatim:

```
ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0
MUTANT m6-digest-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m6-digest-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m7-round-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m7-round-blind pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m8-w-only-shapes pop=r85 killed=yes mismatches=2 errors=0 exit=1
MUTANT-PAIR m8-w-only-shapes pop=r85 killed=yes mismatches=2 errors=0 exit=1
MUTANT m9-basename-only pop=r85 killed=yes mismatches=4 errors=0 exit=1
MUTANT-PAIR m9-basename-only pop=r85 killed=yes mismatches=4 errors=0 exit=1
MUTANT m10-records-as-wave pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m10-records-as-wave pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT m11-class-enum pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m11-class-enum pop=r85 killed=yes mismatches=1 errors=0 exit=1
MUTANT c7-census-in-tree pop=r85 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR c7-census-in-tree pop=r85 killed=no mismatches=0 errors=0 exit=0
MUTANT m14-short-shape pop=r85 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR m14-short-shape pop=r85 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=8 sets=r85 pristine_r85=ok killed_r85=6 killed_total=6
EXIT=0
```

Supplementary arm C `--only r86 --expect-killed 8` also ran: `SUMMARY mutants=8 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8`, EXIT=0 (saved at `.ufo/waves/round-86/w1/S86ExecC1/battery-r86-only.txt`).

Each of the eight `old` texts occurs exactly once in the filed counter (verified before the runs); no BATTERY-FATAL invalid arm.

## 2. Branch derivation from `judge()` (census/round-86/c1-pointer-counter.py)

Prereq (all MOVED): line 376-400 pass: frozen digest present, target digest equals frozen, basename equal, same round (lines 397-404). Line numbers below are the filed r86 file.

### NF-W → c7 (census-in-tree branch, lines 417-425)

Row: `NF-W fixture R9 r85 I85R MOVED census/round-84/w1/c1-after.txt REFUSED`. Item I85R token `census/round-84/records/c1-after.txt`.
- Line 405 own-tree test: `target[:tr.start(0)] == token[:kr.start(0)]` is `'census' == 'census'` true, but `_owntree_ok` (line 368-371) returns **True** via the wave-directory disjunct: `OWNTREE_WAVE` (line 351) matches `w1/`, and `got[1:] == want[1:]` (`['c1-after.txt'] == ['c1-after.txt']`). So line 405 does NOT refuse.
- Line 410 passes (prefix is `'census'`, in the allowed pair).
- Line 413 skipped (token prefix IS `'census'`).
- Line 417 guard: `target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" and not _capture_ok(...)`. `_capture_ok` (340-348) is **False**: CAPTURE regex (337) only accepts `waves/|wave/|records/wave-<w>/`, and the target suffix is `w1/...`. Hence `not _capture_ok` is True → line 425 `why = "census-in-tree target is not a wave capture keeping the token's full path suffix"` → REFUSED. This is the sole refusal.
- Under c7 (`elif False:  # c7: the census-in-tree branch is dropped`, c1-mutants.json) lines 417-425 are skipped entirely; control reaches line 469 `return cls, ""` = MOVED = accepted → mismatch → harness exit 1 → killed=yes.

### NF-Y → m14 (own-tree short-shape guard, line 366)

Row: `NF-Y fixture R9 r86 I86S MOVED census/round-83/waves/c1-pointer-counter.py REFUSED`. Item I86S token `census/round-83/c1-pointer-counter.py` — one component below its round.
- Line 405: prefixes equal (`'census'`), `_owntree_ok` (354-371): `want = ['c1-pointer-counter.py']` (len 1), `got = ['waves','c1-pointer-counter.py']` (len 2) → line 366 `if len(want) < 2 or len(got) < 2:` fires → returns False → line 409 why = "own-round-tree target …" → REFUSED. This guard is the sole refusal: under m14 the line becomes `if False:`, `_owntree_ok` then reaches line 368 `_capture_ok` = **True** (CAPTURE matches `waves/`, suffix equals token last component) → `_owntree_ok` True → line 405 passes; line 417 does not fire because `_capture_ok` is True; falls to line 469 MOVED → accepted → killed=yes.

### Why the r85 47 rows cannot kill them

c7: lines 417-425 need (target prefix `census`, token prefix `census`, `_owntree_ok` True, `_capture_ok` False). Every r85 MOVED row with a census token is one of the three I85R rows, and none satisfies all four:
- NF-R (`records/copy/`): prefix pair census/census but `_owntree_ok` False (no wave-dir match, no CAPTURE match) → refused at line 405, never reaches 417.
- TF11 (`waves/`): `_capture_ok` True → line 417's `not _capture_ok` False → decides MOVED correctly, no refusal to lose.
- Every other r85 MOVED row's token is `.ufo/...` (P04/P07) so `token[:kr.start(0)] != "census"`, or L02 whose token `census/operator-sweep-20261019` has `kr is None` (no `round-<N>`) so `elif kr` guards at 405/413/417 never evaluate. NF-W is the first row with `_owntree_ok` True via the `w1/` wave shape while the shape is not a CAPTURE shape.

m14: the counts were enumerated over all r85 MOVED rows. Token bodies below their round: P04 `['a2w1','SwarmExecutor08.md']` (2), P07 `['w1','S61ExecRealRecord','erratum-evidence.txt']` (3), I85R `['records','c1-after.txt']` (2), I85C (2). The guard fires on exactly the rows whose target `got` is < 2 (NF-K `.ufo/waves/round-32/SwarmExecutor08.md`), but the guard is not the sole refusal there: with the guard dropped, `_capture_ok` and `OWNTREE_WAVE` both still fail, `_owntree_ok` stays False, NF-K stays REFUSED. No r85 row has a `< 2` side with `_capture_ok` True. I86S (token `census/round-83/c1-pointer-counter.py`, 1 component) first appears in the r86 item population and has no r85 row. So dropping the guard changes no r85 outcome.

### Why the r84 44 rows cannot kill them

r84 rows are a strict prefix of r85 (verified above, 44/44 rows identical in order) and contain no I85R row at all (42 of the 44 are P04/P07/L02 rows). Both clauses are therefore even less reachable: no census-token row (kills c7 impossible, same four-condition argument), and the only MOVED tokens are P04 (2 below round) and P07 (3 below round); the NF-K short-got row exists but still fails independently of the guard as shown above.

## 3. Pin attacks (one byte changed in a copy; lane bytes untouched)

Changed exactly one byte (last byte of the file, `...X\n` replacing `...<\n>`) in a scratch copy of `census/round-86/c1-false-rows.tsv` (sha256 became `d8b74303…`) and separately in a scratch copy of `census/round-86/c1-items.tsv` (sha256 became `ad1bf5ee…`). Tampered copies and raw stderr receipts saved under `.ufo/waves/round-86/w1/S86ExecC1/pinr/`.

- Harness (`c1-false-row-harness.py --population <tampered false-rows>`), guards POP_PINS at harness lines 94-97, sha check at line 295-298:
  `C1-HARNESS-FATAL: population sha256 d8b7430338f29d5123f2ab1bca964ac1fd411d90692bfc6a525467e222af7261 is not a pinned population (1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42, 4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f, 79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561, c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb)` — **exit 2**.
- Counter (`c1-pointer-counter.py --population <tampered items>`), guards POPS at counter lines 124-141, sha check at counter lines 501-506:
  `C2-COUNTER-FATAL: population sha256 ad1bf5eec7a664dd8456cfeb28a6f33852e1211c2a7ac51ba3b08bded85a1121 is not pinned` — **exit 2**. Same FATAL for the tampered false-rows copy (`d8b74303…`), exit 2.
- Battery (scratch copy of `c1-clause-battery.py` + tampered `c1-false-rows.tsv` at its pinned path, guards PINS at battery lines 44-51, sha check at battery lines 59-62):
  `BATTERY-FATAL: r86 population sha256 d8b7430338f29d5123f2ab1bca964ac1fd411d90692bfc6a525467e222af7261 is not the pin 79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561` — **exit 1, not 2**.

DEVIATION / finding: the seat spec states all three refuse with "FATAL, exit 2 in each case", and the preregistration (battery docstring line 27) claims battery "2 on usage, a pin mismatch, an edit that does not apply exactly once". Measured: the battery's pin-mismatch path raises `SystemExit("BATTERY-FATAL: …")` via `raise SystemExit` at battery line 62 inside `run()`, which exits 1. The `return 2` paths (battery lines 90, 93, 103, 114, 122) cover --work/--only/pristine checks only. The refusal still happens before any mutant is scored, so it is fail-closed, but the exit code disagrees with both the docstring and the frozen claim text. L1 should either correct the docstring/preregistration to "1" for the battery pin path or change line 62 to `print(...); return 2`. Recorded as a defect in the frozen text, not in the instrument's fail-closed property.

## 4. r85 → r86 counter diff (classification)

`diff -u census/round-85/c1-pointer-counter.py census/round-86/c1-pointer-counter.py` saved at `.ufo/waves/round-86/w1/S86ExecC1/diff-r85-r86-counter.txt`. Exactly 2 hunks:
- Hunk 1 (`@@ -1,5 +1,14 @@`): module docstring only — renames successor lines, adds the r86 paragraph naming I86S, the POPS entry, the short-shape guard, and the I85R census-in-tree reachability note.
- Hunk 2 (`@@ -124,6 +133,11 @@`): POPS table only — adds the two comment lines and one entry: `"5abf3b01…9dade2": ("r86", "705fa1385c4ccec23811cfa57104046ec6587258", 4)`.

No resolution rule, guard, branch, or message changed — every line after the docstring is byte-identical except the added POPS entry. `c1-ledger.tsv` is byte-identical between rounds (sha256 `7cbb28c9…`, verified with diff).

## Files landed

- `.ufo/waves/round-86/w1/S86ExecC1.md` (this report; sibling file — the seat dir is a directory of the same prefix name, the report path is a separate file)
- `.ufo/waves/round-86/w1/S86ExecC1/battery-r85-r86.txt`, `battery-r85-only.txt`, `battery-r86-only.txt`, `diff-r85-r86-counter.txt`, `pinr/` (tampered copies + stderr/exit receipts for the three pin attacks)

Tooling recorded: no tool installed or upgraded (§authorization); only system `python3 -B`, `git` (read / fixture-clone only through the harness), and `diff`/`sha256sum` were used. Scratch `/fast/scratch/hyaku/souji-r86/S86ExecC1/` removed before yield.
