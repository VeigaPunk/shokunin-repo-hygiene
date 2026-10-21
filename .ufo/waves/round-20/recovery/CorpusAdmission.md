# CorpusAdmission — source-quality calibration

## Scope and observed state

Fresh, read-only source review of the named round-20 authority, lesson, source registry, and its specifically cited existing knowledge entry. The preregistration declares C1 calibration and C2 operability, with no C3/coverage claim (`.ufo/waves/round-20/preregistration.txt:1-3`; `corpus/lessons/round-20.md:5-10`). I did not execute source code, reopen public pages, run a corpus validator, or make an admission decision. This is author-side advice, not non-author closure.

The declared baseline is `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (preregistration line 1). I did not independently verify current HEAD. Working-byte SHA-256 values for the files read are recorded below; no commit or runtime result is inferred.

## Evidence and explicit discrepancy

The source-decision accounting is internally consistent: `corpus/lessons/round-20.md:27-35` records S089 admitted, S090 explicitly rejected, and S091-S093 admitted (four admitted, one rejected); lines 45-61 add S094 as a scoped locator correction and state the combined total as six pages, five admitted, one rejected. The registry has the matching current-round rows at `corpus/SOURCES.md:109-114`. The lesson also explicitly preserves the distinct historical fact that round 19 had no explicit reject catalogue and does not backdate S032 or invent a rejected S079-S088 row (`round-20.md:37-39`). This is a good boundary: a correction/exclusion is not silently relabelled as a source rejection.

There is, however, a terminology mismatch in the no-expansion account. `corpus/SOURCES.md:140` says the combined source search implies “no knowledge growth,” while the already-existing `corpus/knowledge/process-residue-observations.md` has a substantive, explicitly round-20 precision correction at lines 101-133: it replaces the earlier read/enumeration wording, cites S086-S088, adds implementation digests and narrows the claimed read set, skipped-data scope, and redaction limits. The round-20 lesson more narrowly says the source decisions are not a new coverage-map entry (`round-20.md:25`) and the prior F5 core is retained rather than a new coverage claim (`round-20.md:130`).

This is not evidence of a new knowledge *path* or a new coverage claim; it is evidence that an existing knowledge entry was updated. Thus “zero new knowledge entries/coverage expansion” can be true while literal “no knowledge growth” is too broad. Keep that distinction explicit rather than scoring the source additions as knowledge expansion. `corpus/QUALITY.md:3-14` applies its bar to both source rows and knowledge entries, but does not define these as interchangeable denominators.

**STATUS: OPEN** — reconcile the broad “no knowledge growth” wording with the round-20 correction to an existing knowledge entry. This is a bounded source-accounting/calibration issue; it does not by itself overturn the correctly separated five-admit/one-reject source tally, establish new coverage, or close either C1 or C2.

## Affected axes

- **C1 calibration:** improve by distinguishing source decisions, newly admitted knowledge paths, existing-entry corrections, and coverage claims in the oracle/report. Do not treat a new source row as a new knowledge entry.
- **C2 operability:** no change proposed or needed; this move is reporting/oracle classification only and preserves the full-ID and complete-input requirements.
- **Coverage:** no new coverage claim is supported by this evidence.

## One bounded proposed move

Add one independent **existing-entry correction** counterexample to the source/knowledge accounting oracle, using the round-20 precision correction in `corpus/knowledge/process-residue-observations.md:101-133`: require separate results for (1) current-round source decisions (expected S089-S094: five admitted, one rejected), (2) newly added knowledge paths, (3) existing knowledge paths whose bytes/content were corrected, and (4) coverage claims. Replace the undifferentiated “no knowledge growth” wording with the measured distinctions. The correction must register as an existing-entry update, not as a new knowledge path or coverage increment; S090 remains the actual current-round rejection, and the S086-S088 teaching corrections must not be relabelled as round-20 source rejects.

This is one narrow oracle/reporting change: it preserves the source admission policy, historic rows, C1/C2 tests, and the declared no-coverage scope while making the learning-trend classification falsifiable.

## Risks and verification boundary

The phrase “no knowledge growth” may have been intended to mean no new entry or coverage expansion; the proposed wording change makes that intended scope explicit rather than alleging a substantive new-coverage claim. Conversely, counting every precision correction as a new knowledge entry would overstate expansion, so the oracle must track existing-path edits separately. No source page was re-opened by this seat; quoted-source accuracy remains the round lesson's recorded observation, not a fresh external-source check. No build, test, lint, smoke, or target-code execution was performed or authorized here. A non-author reviewer/integrator must adjudicate any disposition.

## Observed working-byte identities

Declared baseline: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (from the preregistration; current HEAD not independently checked).

Evidence files read:

- `.ufo/waves/round-20/preregistration.txt` — `1c138e71c868fdadc9fde6bca60fdb0cc94d61e2d2a4990115885d956286a9cd`
- `corpus/lessons/round-20.md` — `b69815a46b1ef6f5abaf31c86ce0108d50fd9bf854d4562b8cc447a90e90a7e0`
- `corpus/lessons/round-19-verifier-spotcheck.md` — `bbfa0ddde5c0782f77fc710f77c2a331f93b9cd1b37ac28f05803a719e11d708`
- `corpus/QUALITY.md` — `f93e535c2e6c99f74d55fb89100fcb979fd54428e486309958bf5884c66cc4e4`
- `corpus/SOURCES.md` — `199c06c9a57e692d010bda0578ae9f8a47bbe6fe2ef34bdbc802996e3b95a500`
- `corpus/knowledge/process-residue-observations.md` — `5031c5cbebe1dd9907299e30550c6fec1e53177d5d8742a8fd889cf001a29f34`

Inspected C1/C2 source files (working-byte SHA-256): `tools/souji-seat-audit.py` `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6`; `tools/souji-rev-pin.py` `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d`; `census/round-13/run-verification.py` `385133127c65b09a718c7bc68b5f43a8aebffc9b9602d0578eca0a5093d346eb`; `census/round-14/run-verification.py` `34371fa99a0aafffc25780963f83de354c21a11660855a1d4feb2ed419c2e4d6`; `census/round-14/run-targeted.py` `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2`; `census/round-14/cache-demonstration.py` `df9209ac21169087bb8c4f114608d17124ad4b092a318a65c88f9aea48b98697`.

No tools were installed or updated.