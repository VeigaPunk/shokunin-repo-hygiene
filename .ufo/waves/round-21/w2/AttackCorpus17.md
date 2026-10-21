# AttackCorpus17 — C1 corpus falsification

**Result: no disagreement found** between the independent labels and the pinned `implicit_root_read` predicate for the 113 read/grep/glob calls in the nine assigned transcripts. **Confidence: high for this static comparison; no runtime behavior was exercised.** The complete row-level oracle is `AttackCorpus17.tsv`.

## Independent labels

Read the frozen preregistration, measurement clarification, and full-corpus-restoration rule before opening the classifier. Labeled all 113 call lines first: **99 OK, 1 FLAG, 13 UNSEEN** (82 read, 31 grep, 0 glob). Export-relative paths and 1-based physical line numbers are used in the TSV.

The sole FLAG is `final/ReopenHistoryReject.txt:54`: `read(.ufo/waves/round-20/final/ReopenHistoryReject.md)` is a visible relative target; lexical resolution from the fleet root is outside the lane. The 13 UNSEEN rows have a cut target/path component or cut call tail, including failed read attempts; they are not treated as OK evidence. Absolute paths remain OK for this class even when outside the lane, as the contract explicitly excludes absolute paths.

## Predicate comparison

Direct source read: `tools/souji-seat-audit.py:377-402`, with its callsite at `:455-458`. `implicit_root_read` selects grep targets by ` @ ` first, then legacy ` in `; a complete grep without either uses `.` while a cut call without a visible target is skipped. It splits semicolon-separated targets, skips a component containing `…`, strips documented read selectors, excludes absolute/tilde paths and case-insensitive URI schemes, then uses normalized lexical containment against the lane root. The callsite applies this to read/grep/glob args without conditioning on the tool status.

For the one visible relative outside-lane target, the predicate returns a target and the caller emits V-READ-ROOT. All complete OK targets are excluded as absolute paths or URIs, and the cut targets are skipped rather than flagged, matching the frozen lower-bound treatment. Error status does not change the pathname classification. No classifier disagreement was observed.

## Bounded gaps

This nine-file sample does not exercise a complete legacy `grep(PATTERN in PATH)` call, a complete grep with no path separator (implicit cwd), a cut pattern with a visible complete ` @ ` target, an uppercase URI scheme, or a `:conflicts` read selector. Those branches were checked in source but are not empirically covered by these transcript calls. LSP was unavailable (`read xd://lsp` returned “No such tool”); grep only located the symbol, and the predicate itself was read directly. No code was executed, and no tests or builds were run.