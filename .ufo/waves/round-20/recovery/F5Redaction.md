# F5 redaction review

**STATUS: OPEN.** The observed record supports only a bounded redaction statement, not a secret-free read or universal output-redaction guarantee. An argv-derived path escaping through `reason` remains an inference, not an observed leak; the existing record explicitly says no private-value probe was made or authorized. This review did not execute the census or fixture, inspect private data, or establish a runtime leak.

**Observed bytes:** repository `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; the working `corpus/knowledge/process-residue-observations.md` SHA-256 was `5031c5cbebe1dd9907299e30550c6fec1e53177d5d8742a8fd889cf001a29f34` (reader snapshot `#1CF8`). The correction itself records the baseline and the three bound implementation/fixture digests at lines 104–115; those are documentary provenance, not fresh execution evidence.

## Counterexample and evidence

- `corpus/knowledge/process-residue-observations.md:55–59` says the census reads `cmdline`, does not read `environ`, and that secret-shaped argv is redacted before printing. The no-`environ` boundary does not imply secret-free input: the same entry says raw cmdline/argv is read before printing-time redaction at lines 124–125.
- Lines 38–44 describe an argv-derived missing-scratch-path trigger and expose `reason` as an output column. Lines 124–127 say `reason` has separate sanitation from `cmd` and explicitly leave a credential-shaped argv-derived path escaping through `reason` as **[INFERENCE]**. Thus a concrete adversarial fixture is an absent scratch path whose argv component contains a synthetic credential-shaped canary; if the path-derived reason retains it, `cmd` redaction alone will not prevent the canary appearing in the serialized row. Nothing read here shows that this actually happens.
- `corpus/lessons/round-19-verifier-spotcheck.md:104` is historical corroboration of the same inference and likewise records that no payload was constructed and no value inspected; it is not fresh test evidence.

**Smallest safe oracle change:** add one deterministic fixture case with a non-secret, synthetic credential-shaped canary embedded in the argv path that triggers the missing-scratch-path reason. Assert the canary is absent from the complete serialized output—especially both `reason` and `cmd`—while the expected reason remains useful. Do not use a live/private value. Until that field-level oracle exists, scope the existing prose at `process-residue-observations.md:58` to the tested fake patterns and state alongside it that raw `cmdline` is read, no `environ` read is only a narrower boundary, and `reason` redaction is unverified.

**Impacted axis:** calibration only—the available evidence cannot calibrate a claim of secret-free input or universal redaction across output fields. This is an unverified channel, not a demonstrated defect or authorization for a live probe.
Report: `.ufo/waves/round-20/recovery/F5Redaction.md`