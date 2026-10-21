# AttackCorpus20 — independent C1 classifier attack

**Result:** The independent TSV contains 112 raw call occurrences from the nine assigned transcript exports: 104 `OK`, 8 `UNSEEN`, and 0 `FLAG`. I found no static disagreement with `implicit_root_read` on the classifiable calls. This is a source comparison, not an executed classifier result.

## Independent label set

`AttackCorpus20.tsv` was labeled before opening the classifier implementation, using the frozen C1 contract, `clarification-before-measurement.txt`, and the superseding `full-corpus-restoration.txt`. It preserves the requested export-directory identity and 1-based physical line numbers. All three exports in the restoration rule are represented in the assignment's nine-file subset; recovery entries were included despite the earlier clarification's superseded exclusion.

The 8 `UNSEEN` calls are exactly:

- `final/ReopenTimeout.txt:41,42` — web.archive URL target cut with `…`.
- `recovery-final/GrantTraversal.txt:62` — visible `@` target is cut (`/home/vg…`); `:69` — grep argument/pattern is cut before a target is recoverable.
- `recovery/ReceiptSpec.txt:63-66` — each visible `@` target is cut (`/home…`).

The other 104 have complete absolute or URI targets. None resolves as an implicit fleet-root target. Error-status calls remain included as attempts: `recovery/GrantPython.txt:46,64`, `recovery/ReceiptManifest.txt:89`, and `recovery/ReceiptSpec.txt:80`.

## Predicate comparison

Inspected `tools/souji-seat-audit.py:377-402` (`implicit_root_read`) and its call site at `:455-458`, plus `CALL_RE`/`LINE_NO_RE` at `:81,89` and `:409-415`. Static comparison against each TSV row:

Pinned source identity: the inspected file matched `522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-seat-audit.py` by SHA-256 (`e1298b9348f42406af59be885dcfac146c8939c8d389fd2109532b9fe397687c`).

- The `read` selector removal and `grep` delimiter order agree with C1: `@` is preferred, then legacy ` in `, then omitted-path grep is treated as `.` unless the args are cut.
- Splitting `;` components, skipping a component containing `…`, handling URI schemes case-insensitively, exempting absolute and `~` paths, and lexically normalizing relative paths agree with the frozen contract.
- For these 112 calls, every complete component is absolute or a URI; the eight cut cases are not guessed. Thus the independent outcomes are 104 `OK` and 8 `UNSEEN`, with no expected `FLAG`; the predicate presents no discrepancy on this subset.

**Evidence limitation:** `xd://lsp` was unavailable (`No such tool: xd://lsp`), so the source review used literal `grep`/`read`; it is not semantic LSP proof. I did not execute the classifier, run tests/builds, or inspect earlier oracle label files. No tools were installed or updated.