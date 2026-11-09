# R95ExecC1 — C1 re-derivation on committed bytes (after arm, r94 do-nothing control, forgery controls)

Verdict: NO-FALSIFICATION (C1). No C2 work in this seat. Lane HEAD 59fd7be0 (F); P1 d79bc3fe and P2 48c5efe9 in history.

## 1. Pins (sha256 measured on lane bytes)

| file | pin in prereg / P1-P2 | measured | match |
|---|---|---|---|
| census/round-95/c1-survivor-search.py | 6066508fa4b113f5… | 6066508fa4b113f5e7d9d269e4e3516c104d0e5cc9236cc5e4c6aa8a0d649740 | yes |
| census/round-95/c1-targets.json | fb40bf4e046c0748… | fb40bf4e046c074845ec00c587173b49c7a095a6236cb188880a2183d7ba5b8e | yes |
| census/round-95/c1-control-r94-rule.py | fb90b3873232900d… | fb90b3873232900def423a33aa9945dabec9c6a9c453e59f94a814d3b887a26f | yes |
| census/round-95/c1-forgery-controls.py | 753083b70ca9075c… | 753083b70ca9075c15d6bcf21be717e46046f78637def9395f27a4f7f25ef0b2 | yes |
| census/round-93/c1-false-row-harness.py | 1868a570… | 1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4 | yes |
| census/round-93/c1-false-rows.tsv | d6439f65… | d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e | yes |
| census/round-87/c1-pointer-counter.py | fd0a8e24… | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | yes |
| census/round-94/c1-survivor-search.py (frozen r94) | 97b8defa… | 97b8defa5c3c007cc10814483fe6dae6fe0f0a0bdb066b0f14169561b9f374ae | yes |

Not checked: the forgery-variant sha256s (FA 612140a6…, FB 3b766d1f…, FC 5a84f7a4…) are printed by the runner and recorded in forgery-receipt.txt; I did not compare them against a P2 receipt line. Lane cleanliness (git status) was not checked.

## 2. Hunk inventory: r94 → r95 search

Source: `diff -u census/round-94/c1-survivor-search.py census/round-95/c1-survivor-search.py`, saved as r94-r95-unified.diff (230 lines, 7 hunks):

- H1 @@ -1,21 +1,30 @@ — module docstring. Class: docstring.
- H2 @@ -37,6 +46,7 @@ — `+import re`. Class: rule (support for rc extraction).
- H3 @@ -55,24 +65,117 @@, part — HAND += five tuples (h-sysexit, h-atexit, h-thread, h-osexit, h-sigkill). Class: HAND.
- H4 same hunk, part — HOOK: r94 excepthook-only f-string replaced by a template with @RC@ placeholder; adds _souji_crash (writes `SOUJI-R95-CRASH <why>` then os._exit(70)), excepthook, unraisablehook, threading.excepthook, os._exit replacement, sys.monitoring RAISE callback (ids 3–5), atexit callback registered first. Class: HOOK.
- H5 same hunk, part — CHECK script (modes excepthook, sysexit, atexit, thread, osexit, argparse) and CHECKS tuple. Class: CHECK.
- H6 @@ -111,10 +214,12 @@ — verdict(): ROW rc extracted with `-?\d+`; errored if harness rc==70 or rc<0 or any ROW rc==70 or rc<0. Class: rule.
- H7 @@ -206,16 +311,25 @@ — main() precondition: runs each CHECKS mode with 60 s timeout, fatal on mismatch, prints the check line. Class: precondition.

UNEXPECTED: none. score() is not touched by any hunk. main() changes only in the precondition block.

Hand-tuple check (hand-check.txt): the five extra tuples in the control wrapper are byte-identical to the five r95 HAND tuples (membership verified programmatically). r94 HAND length 5, r95 HAND length 10.

## 3. Do-nothing control (frozen r94 rule via wrapper, --jobs 5)

Wrapper census/round-95/c1-control-r94-rule.py loads the frozen r94 search and the r95 search by path, takes the five r95 HAND tuples, asserts five, sets `r94.HAND = r94.HAND + extra`, then calls `sys.exit(r94.main(sys.argv[1:]))`. The only mutation in the wrapper is that HAND line. HOOK, verdict(), score() and main() are the frozen r94 bytes (sha256 97b8defa…). The wrapper's sha256 fb90b387… matches the prereg.

Receipt: control-receipt.txt (wall 125.69 s):
- `# crash-sentinel rc=70 check=pass` — r94's own one-line precondition. It is not the seven-mode check.
- SEARCH h-sysexit killed=yes, h-osexit killed=yes, h-sigkill killed=yes; h-atexit killed=no, h-thread killed=no; a491c22 killed=yes, h-ok-admits-one killed=yes, h-crash-late killed=errored, h-crash-index killed=errored, a127c26 killed=no.
- `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=2 killed=5 survived=3`, EXIT 0.

This matches the prereg control line exactly.

## 4. After arm (r95 search on committed bytes, --jobs 5) — matches the predicate

Receipt: after-receipt.txt (wall 65.91 s). Work trees were in scratch and are deleted.

- Check line: `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2` — identical to the prereg.
- `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1` — identical to the prereg.
- SEARCH lines: h-sysexit, h-atexit, h-thread, h-osexit, h-sigkill, h-crash-late, h-crash-index killed=errored; h-ok-admits-one and a491c22-<-to-<= killed=yes; a127c26-True-to-False killed=no.
- EXIT 0.

## 5. Per-target ROW table (after arm; each harness.out has 66 ROW lines)

Mapping m0000–m0009 to targets: the h-* ids come from the mutated counter's comments (m0002–m0009). m0000 differs from the frozen counter at line 127 (`True`→`False`, the a127c26 edit). m0001 differs at line 491 (`<`→`<=`, the a491c22 edit). Both line numbers match the SEARCH lines.

| target | ROW | rc distribution | match=no | SOUJI-R95-CRASH stderr seen in harness.out | verdict |
|---|---|---|---|---|---|
| a127c26-True-to-False (m0000) | 66 | rc=0 ×5, rc=1 ×61 | 0 | none | no (survived) |
| a491c22-<-to-<= (m0001) | 66 | rc=0 ×4, rc=1 ×62 | 1 | none | yes (killed) |
| h-ok-admits-one (m0002) | 66 | rc=0 ×9, rc=1 ×57 | 1 | none | yes (killed) |
| h-crash-late (m0003) | 66 | rc=70 ×66 | — | none | errored |
| h-crash-index (m0004) | 66 | rc=0 ×4, rc=1 ×61, rc=70 ×1 | — | none | errored |
| h-sysexit (m0005) | 66 | rc=70 ×66 | — | 56 × `SOUJI-R95-CRASH SystemExit first raised in main() of the main script` | errored |
| h-atexit (m0006) | 66 | rc=70 ×66 | — | none | errored |
| h-thread (m0007) | 66 | rc=70 ×66 | — | none | errored |
| h-osexit (m0008) | 66 | rc=70 ×66 | — | 56 × `SOUJI-R95-CRASH os._exit(1)` | errored |
| h-sigkill (m0009) | 66 | rc=-9 ×66 | — | none | errored |

- The two killed=yes targets (a491c22, h-ok-admits-one) and the survivor (a127c26) have no rc=70 and no negative rc row.
- h-crash-index has one rc=70 row among 66; the crash fires on the one ledger-bearing row, and the "any ROW rc=70" leg makes it errored.
- Why h-atexit, h-thread and h-crash-late have no SOUJI-R95-CRASH text in harness.out is not established from these files. The harness keeps the counter's stderr only on some rows. [INFERENCE] the sentinel's stderr write happens after the harness's copy point for these channels. I did not test this.

## 6. Forgery controls (FA/FB/FC, --jobs 5)

Receipt: forgery-receipt.txt (wall 162.26 s). Search used: 6066508f… (the r95 search).

- FA (verdict never returns yes): `errored=9 killed=0 survived=1`.
- FB (no sentinel on PYTHONPATH): `errored=1 killed=6 survived=3`.
- FC (rule without the negative-rc leg): `errored=6 killed=3 survived=1`. Here h-sigkill is `killed=yes` because its rows are rc=-9 and are not counted as errors. The other sentinel channels still error.
- `C1-FORGERY-SUMMARY forgeries=3 refused=3`, EXIT 0.

All three differ from the predicate's `errored=7 killed=2 survived=1`, so all three are refused. Each fails in a different way: FA kills nothing, FB loses the sentinel, FC loses the signal leg.

## 7. Falsification verdict

NO-FALSIFICATION.

What I tried:
- Re-ran the after arm on committed bytes. The check line, SEARCH-SUMMARY and EXIT match the prereg predicate.
- Re-ran the do-nothing control. The frozen r94 rule gives errored=2 killed=5 survived=3 on the r95 targets, as stated.
- Re-ran FA/FB/FC. All three are refused 3/3.
- Verified the eight sha256 pins in §1 against the prereg and the P1 values.
- Classified every hunk of the r94→r95 diff (§2). No unexpected change, and score() is byte-identical.
- Read all ten harness.out files and counted ROW rc values (§5). The semantic kills have no rc=70 or negative rc row.

Limits:
- The prereg's "crash-channel fixtures" claim is checked on these ten targets only, as stated.
- I did not test the stderr-capture question in §5 beyond reading the files.
- Setup and scratch: scratch under /fast/scratch/hyaku/souji-r95/R95ExecC1 was deleted. No git or jj mutation, no sudo, no background process left running. No tool installed.
