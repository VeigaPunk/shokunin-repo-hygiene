# S86Reviewer findings (round 86)
Independent re-derivation of C1 and C2 on committed bytes; chronology and instrument binding.

## C2 (operability 8) — RE-DERIVED PASS
Commands (cwd census/round-86):
- after: `python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py --work /fast/scratch/hyaku/souji-r86/S86Reviewer/c2a` → EXIT 0, `SUMMARY rows=9 mismatches=0 errors=0`; KG1 `k4=1 named=yes ...index-flag-concealed`, KG2 `k4=1 named=yes ...stat-cache-concealed`.
- before: `--tool census/round-86/controls/c2-before-base-tool.py --work .../c2b` → EXIT 1, `SUMMARY rows=9 mismatches=2 errors=0`; KG1 `k4=0 named=no match=no`, KG2 `k4=1 named=no match=no detail=''`.
My stdout matches `records/c2-after.txt` and `controls/c2-before-base-tool.txt` except the `# fixture clone=` path line.

## Digests (sha256sum vs receipt headers) — ALL MATCH
tools/souji-record-agreement.py 4cc3b945…468df; controls/c2-before-base-tool.py 0ade0751…fb7; tools/souji-receipt-write.py 70bbf1c2…bcd; census/round-86/c2-k4-counter.py 6438c014…827; c1-pointer-counter.py 8278ea4d…1f3; c1-false-row-harness.py 2dac2e81…9d9; c1-mutants.json 6f055ede…47a6; c1-false-rows.tsv (r86) 79db70f6…561; (r85) 1468236c…042; c1-items.tsv 5abf3b01…dade2; r83 c9a6d58c…02eb; r84 4795f009…6f6f. No r85 receipt-binding defect class present in r86 headers.

## C1 counter diff (r85→r86) — AS CLAIMED
`diff census/round-85/c1-pointer-counter.py census/round-86/c1-pointer-counter.py` = docstring change + ONE POPS entry (`"5abf3b01…"` → `("r86","705fa138…",4)`) with its comment block. No guard/branch/message change. `cmp census/round-85/c1-ledger.tsv census/round-86/c1-ledger.tsv` → LEDGER-IDENTICAL.

## C1 battery — r85 arm RE-DERIVED PASS
`--only r85 --expect-killed 6` → EXIT 0, output byte-identical to `controls/c1-before-r85-population.txt` (`diff` clean): pristine 47/0/0, m6–m11 killed=yes, c7 and m14 killed=no, `SUMMARY mutants=8 sets=r85 pristine_r85=ok killed_r85=6 killed_total=6`.
Prereg "EXIT=0" wording for C1: the battery itself prints no trailing `EXIT=0` line (grep '^EXIT=' = 0 in both C1 receipts) — the battery's process exit code is 0 as counted. Conventions match across rounds; requirement verified by exit code 0.

## C1 both-arm — RE-DERIVED PASS
- `--only r85,r86 --expect-killed 14` → EXIT 0 (232.9s), `diff` vs `records/c1-after.txt` clean (BOTH-EXACT-MATCH): pristine r85 47/0/0 and r86 49/0/0, m6–m11 killed=yes on both pops, c7-census-in-tree and m14-short-shape killed=no on r85 / killed=yes on r86, `SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14`. An earlier copy was SIGTERMed at 207s leaving a clean 13-line strict prefix of the filed receipt; the clean re-run above is the counted one.

## Chronology — PASS (with author/commiter nuance)
- P 47602fa6 committer 2026-11-08T05:47:12-03:00 (author 05:35:06); 12 files: instruments, controls, both before receipts; no records/.
- F d77b4258 committer 05:47:18 (author 05:47:12); `git show --name-only` = preregistration.txt ALONE.
- C2 repair 2acbbfc8 committer 05:47:25 (author 05:47:18); tools/souji-record-agreement.py only, AFTER F.
- After receipts (records/c1-after.txt, records/c2-after.txt) are UNCOMMITTED (`?? census/round-86/records/`, not in any commit — `git show 2acbbfc8:records/c2-after.txt` fatal: path does not exist). Disk mtimes: c2-after.txt 05:47:33 (after C2 repair 05:47:25 — consistent), c1-after.txt 05:53:01 (tree touched by a sibling seat re-measuring in the same lanes). The claim requires after receipts measured on filed bytes; my independent re-derivation (above) confirms byte equality of the receipt *contents*, so content cannot be stale relative to filed bytes regardless of the in-tree file mtime.

## Verdict
Both claims re-derived on committed bytes with the exact counting commands; every receipt header digest verified against sha256sum; counter diff is one POPS entry plus docstring; ledgers byte-identical; F-alone and repair-after-F verified. No defects found. Residual risk: after receipts remain uncommitted in-tree (integration owner stamps/commits them); the SIGTERM-killed first both-arm copy was a local scheduling artifact, not an instrument signal.
