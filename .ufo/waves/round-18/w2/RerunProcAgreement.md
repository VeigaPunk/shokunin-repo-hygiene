STATUS: DONE — two live pairs were captured; the current 65 = 65 claim did not reproduce, and the census predicates are not equivalent.

# Attacked claim: C3 — “live 65 = 65”

Axes: live count fidelity; repeatability under process churn; equivalence of the census and blind-counter predicates.

## Findings

1. **P2 — The claimed live equality was not reproduced in these runs.** On the same boot (`3e7084f4-7046-4957-a8a2-c00542a3b469`), the two sequential pairs reported:

   | Invocation | `souji-proc-census.sh` rows (cwd / argv / fd) | `leak-count.py` total (cwd / argv / fd) |
   |---|---:|---:|
   | 1 | 93 (67 / 18 / 8) | 88 (58 / 20 / 10) |
   | 2 | 81 (58 / 13 / 10) | 83 (58 / 15 / 10) |

   The counter’s family totals were `other=30, r15-census-config=44, r17-census-hygiene=14` in pair 1 and `other=25, r15-census-config=44, r17-census-hygiene=14` in pair 2. The emitted PID sets changed between the repeated scans. For example, counter-only PID `1319616` was present in pair 1’s counter output but not its preceding census output; census-only PID `1143942` was present in pair 1’s census output but not its following counter output. In pair 2, census-only PID `1029257` and counter-only PID `1434684` likewise show non-identical sequential observations. These are not atomic snapshots: live processes were starting and exiting during the scans, so the changed PIDs and counts are consistent with churn. The observation does not establish that the earlier recorded snapshot was fabricated, but it does not reproduce 65 = 65 now.

2. **P2 — `cwd-deleted` bypasses the configured scratch-prefix predicate.** `tools/souji-proc-census.sh:326-327` labels any cwd ending in ` (deleted)` as `cwd-deleted`; this branch does not test `PREFIXES`. The CLI describes `--prefix` as the scratch-path prefix to inspect (`tools/souji-proc-census.sh:7,24-26`). By contrast, the blind counter checks the cwd path against its scratch prefixes before counting it (`census/round-18/leak-count.py:101-111`). Thus a deleted cwd outside the selected prefixes can be emitted by the census but excluded by the counter. This is a real predicate mismatch, although the observed unmatched PIDs above are not evidence that any particular one had a non-scratch cwd. **Smallest fix:** remove the deleted suffix and require the cwd path to be under one configured `PREFIXES` boundary before assigning `cwd-deleted`.

3. **P2 — The argv predicates also do not define identical sets.** Census argument extraction only considers an argument beginning with `/` or matching `--*=/*` (`tools/souji-proc-census.sh:214-228`). The counter searches for scratch-path substrings within each argument and trims trailing punctuation (`census/round-18/leak-count.py:20-22,53-65`). Therefore a path embedded in a differently shaped argument can satisfy the counter but not the census. This means exact PID-set agreement cannot be inferred from two sequential aggregate totals, even with less churn. **Smallest fix:** specify one intended argv-path grammar and make both independent scanners apply that same inclusion rule; retain raw per-run PID/reason evidence when claiming equality.

## Exact commands and observed outputs

Ran these commands back-to-back twice, with `set -e`:

```sh
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-18/leak-count.py
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-18/leak-count.py
```

All four commands completed successfully. Census output in both runs had the same boot ID above. Counter JSON returned `total=88`, reasons `cwd-deleted=58, argv-path-gone=20, fd-path-gone=10` on the first invocation and `total=83`, reasons `cwd-deleted=58, argv-path-gone=15, fd-path-gone=10` on the second.

## Verdict

**C3 live `65 = 65`: not reproduced by this live sample.** The repeated scans changed due to process churn, and the two tools have demonstrably different inclusion predicates, so this sample cannot establish exact census/counter agreement. The current values are observations, not a stable live-count invariant.

## Residual risk and verification gaps

- `/proc` enumeration and the two programs’ scans are non-atomic; process churn alone can change membership between consecutive invocations.
- `xd://lsp` was requested, but no LSP device is mounted/available in this session. No LSP semantic requests were possible; no grep output was used as semantic proof.
- No process was signaled, no `/proc/*/environ` was read, and no tools were installed.