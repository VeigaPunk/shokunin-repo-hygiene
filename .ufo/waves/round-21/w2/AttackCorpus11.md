# AttackCorpus11 — C1 implicit-root classifier

**Result: no disagreement in this shard.** Independent labels for the ten assigned committed transcripts are in `AttackCorpus11.tsv` (113 call rows, plus header): **1 FLAG, 101 OK, 11 UNSEEN**. Error-status calls were included. These are labels for the named files only, not a full-corpus result.

## Oracle basis and method

Read the frozen C1 terms in `.ufo/waves/round-21/preregistration.txt`, then `clarification-before-measurement.txt` and the superseding `full-corpus-restoration.txt`, before reading classifier source. The restoration puts all three export directories (`final`, `recovery`, `recovery-final`) back in the raw universe; this assignment covers only its ten enumerated files. Grep located the tool-call records, then raw reads confirmed every selected call line and its literal truncation marker. Labels were completed before the pinned classifier was inspected.

The oracle distinguishes a visible, complete path from an ellipsis-cut target. Absolute paths, `~` paths, and URIs are OK for V-READ-ROOT; relative paths resolve lexically from fleet root `/home/vgpnk/Projects/shokunin` and flag only when outside lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. For grep, a complete call with no explicit path is an implicit fleet-root search; an `@` target is explicit, and historical `in` syntax is supported. The TSV marks cut target/pattern cases UNSEEN, not clean; errors remain attempted calls.

## Comparison with pinned source

Inspected `tools/souji-seat-audit.py` from pinned base `522dcd768ca90afe166532d37d306d3df70aeea5`; no auditor, fixture, or other target code was executed. `implicit_root_read` (lines 377–402) implements the pertinent predicates: `@` takes precedence over legacy `in` (380–384); grep with no separator yields implicit `.` only when args are not ellipsis-cut (385–386); semicolon components are examined independently and components containing `…` are skipped (389–392); read selectors are stripped (393–394); absolute and `~` paths plus case-insensitive URI schemes are excluded (395–397); and lexical normalization tests whether a relative path falls outside the lane (398–401). `audit_seat` calls it for read/grep/glob and records a minor `V-READ-ROOT` when it returns a target (455–458).

- **FLAG — `recovery-final/CorpusAdmission.txt:45`:** `glob(corpus/lessons)` is a complete relative target. From fleet root it resolves outside the lane. The function returns this component, and the caller records the minor finding. This is the one positive discriminator in the shard.
- **OK — 101 rows:** visible complete URI, absolute, or lane-resolving relative targets produce no `V-READ-ROOT`, matching the contract. This includes `final/ReopenGitEnv.txt:98`, whose `souji-shokunin/...` target resolves inside the lane. Absolute targets outside the lane are explicitly excluded from this class.
- **UNSEEN — 11 rows:** 2 cut grep argument/pattern lines in `final/ReopenGitEnv.txt` (76, 82); 8 cut grep lines in `recovery-final/InputR13Fixtures.txt` (53–57, 70, 71, 83); and 1 cut grep target in `recovery/ReceiptAuditor.txt` (59). Source suppresses the first group because the args contain `…`, and skips the cut explicit path components in the latter groups. This agrees with the disclosed lower-bound behavior; the TSV does not treat suppression as proof of a safe target.

## Bounded coverage limits

No assigned line exercises a complete legacy `grep(PATTERN in PATH)` call without `@`, a mixed-case URI scheme, or a relative `..` escape. The implementation branches are present in the inspected source, but those cases are not validated by this corpus shard. No disagreement is claimed for them.

**Verification:** static inspection only. The pinned source locations above were read through `git show` and line-filtered; the corpus was not replayed through the auditor, and no tests or code were run. No tools were installed.
