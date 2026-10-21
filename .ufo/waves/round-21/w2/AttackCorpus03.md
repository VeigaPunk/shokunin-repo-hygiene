# AttackCorpus03 — C1 classifier review

**STATUS: COMPLETE.** Fresh independent labels are in `AttackCorpus03.tsv` for the assigned committed source `census/round-20/transcripts/recovery/OracleAcceptance.txt` (`recovery/OracleAcceptance.txt` in the TSV). It contains 132 read/grep/glob call rows: 103 `OK`, 29 `UNSEEN`, 0 `FLAG`. Error results at lines 47, 48, 160, 161, and 371 remain attempts; their status did not determine their label. No earlier oracle label file was read.

## Observed facts

- I read the frozen C1 contract, `clarification-before-measurement.txt`, and `full-corpus-restoration.txt` before classifying. I wrote the TSV before reading `tools/souji-seat-audit.py`.
- The independently classifiable targets in this transcript are absolute paths or `skill://`, `agent://`, and `history://` URIs. None is a relative target resolving outside the lane. The 29 `UNSEEN` calls have a truncated target component or selector (`…`); the TSV names the cut for each. There is no complete relative target, no grep call without a visible `@`/legacy `in` path, and no legacy `grep(PATTERN in PATH)` example in this transcript.
- I read `implicit_root_read` at `tools/souji-seat-audit.py:377-402` and its call site at `:455-458` (source snapshot tag `7F8F`). No target code was executed. The available tool inventory exposes no `lsp` device; the grep lookup only located the definition, and the predicate comparison below is from direct source reading, not grep output.

## Predicate comparison

- **Grep path selection:** `" @ "` is checked first and split from the right; the legacy `" in "` form is the next branch. With neither separator, complete args resolve to `.` and args containing `…` are left unclassified. This matches the specified precedence and implicit-root behavior. For a cut pattern with a complete visible `@` target, this branch still selects the target; truncation in the pattern alone does not suppress classification.
- **Multiple paths and cuts:** The function splits `;`-separated targets, trims components, and skips empty or visibly truncated components. A cut component is therefore not guessed, while complete sibling components are still judged as required by the per-component rule. In this transcript each visible complete sibling is itself absolute, so none creates a flag.
- **Read selectors:** Before path classification, `read` removes a trailing `:raw`, `:img`, `:conflicts`, numeric/range selector, or supported comma/repeated-colon selector suffix. This includes the documented `:conflicts` form and leaves the visible path for the root check.
- **Absolute/URI exclusions:** Paths starting `/` or `~` are excluded, and the URI-scheme regex is case-insensitive. Both agree with C1. Other relative components are joined to the fleet root, normalized lexically, and checked against the normalized lane root; `..` escapes are therefore handled without resolving symlinks, as specified.
- **Severity/call site:** A non-`None` result is reported as `V-READ-ROOT` with minor severity; the existing exit-status logic is not changed by this class.

## Result and limits

No disagreement is observed between the independently classifiable rows and the reviewed predicates: all complete visible targets are excluded by the absolute/URI rules, and truncated components are skipped. Thus this transcript produces no known positive against which precision/recall of the new class can be measured; the 29 `UNSEEN` entries are explicitly not treated as negatives. This is a bounded, non-falsifying result, not evidence that the relative-path or implicit-grep positive cases work. The fallback's legacy `" in "` parsing also remains unexercised here; the sample supplies no evidence about pattern text containing that delimiter.

No builds, tests, linters, formatters, or target-code execution were performed. No tools were installed.