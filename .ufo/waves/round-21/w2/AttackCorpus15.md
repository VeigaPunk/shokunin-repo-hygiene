# AttackCorpus15 — C1 full-call attack

## Observed facts

- Labeled the nine assigned committed r20 transcripts against the frozen C1 contract in `.ufo/waves/round-21/preregistration.txt`, then applied the later corpus corrections in `.ufo/waves/round-21/clarification-before-measurement.txt` and `.ufo/waves/round-21/full-corpus-restoration.txt`. No earlier oracle-label files were read.
- The independent TSV at `.ufo/waves/round-21/w2/AttackCorpus15.tsv` contains all 113 read/grep/glob call rows in the assigned files: **99 OK, 14 UNSEEN, 0 FLAG**. Failed calls are included as attempts.
- The 14 UNSEEN rows have cut target components or no complete visible target: `recovery-final/ConsumerSkill.txt` lines 48, 49, 66; `recovery-final/F5Enumeration.txt` lines 43, 75, 79, 87; `recovery-final/SourceRefs.txt` lines 40, 48; `recovery/ErrataCarry.txt` line 47; and `recovery/InputDemo.txt` lines 52, 53, 68, 69. All remaining visible complete targets are absolute paths or URI targets; none is a complete relative filesystem target resolving outside the lane.
- The classifier was read from pinned base `522dcd768ca90afe166532d37d306d3df70aeea5`, `tools/souji-seat-audit.py`. Its `implicit_root_read` definition is at line 377; `audit_seat` invokes it at line 456. A read-only `git grep -n implicit_root_read 522dcd768ca90afe166532d37d306d3df70aeea5 -- tools/souji-seat-audit.py` returned those locations. The command output did not separately expose an exit code. No target code, builds, tests, or classifier execution were run.

## Static comparison

The predicates in `implicit_root_read` match the frozen C1 rules exercised by the visible calls:

1. For `grep`, it gives ` @ ` precedence over the legacy ` in ` renderer; if neither is present, a complete argument uses the implicit `.` target, while an argument containing the cut marker is not flagged.
2. It splits semicolon-delimited targets, ignores empty or clipped components, and returns a violation if any complete component resolves outside the lane.
3. For `read`, it strips the documented trailing selectors, including numeric/range/comma selectors and `raw`, `img`, and `conflicts`, before path classification.
4. Absolute and `~` targets are exempt. URI schemes are matched case-insensitively. Other complete relative targets are joined to the fleet root and normalized before the lane-boundary comparison.
5. Call status is not an input to this predicate, so error-status attempts remain in scope.

**No disagreement was found on the adjudicable rows.** The 14 UNSEEN rows are skipped by the pinned predicate and therefore produce no violation, consistent with the frozen lower-bound rule; the classifier does not emit a separate UNSEEN result. No complete visible target in this corpus subset should produce `V-READ-ROOT`.

## Limits and confidence

- High confidence in the 113 visible call identities and their classifications under the stated oracle; the 14 clipped targets remain unknown and were not treated as clean evidence.
- This is the assigned nine-file attack only, not a remeasurement of the complete 192-file raw universe.
- The LSP device is unavailable in this session. `git grep` was used only to locate the pinned symbol; conclusions above come from reading the pinned function body, not from grep as semantic proof.
