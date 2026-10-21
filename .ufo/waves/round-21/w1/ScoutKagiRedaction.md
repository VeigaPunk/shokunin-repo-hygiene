# Kagi redaction findings — Souji C3

## Conclusion

Kagi documents secret-shaped detection patterns for its **transcript-at-rest scan**, but no reason-field-specific rule requiring Souji C3 to reuse those patterns. Treat the list as evidence of Kagi's local scanner contract, not a mandatory/general redaction specification for `tools/souji-proc-census.sh`. Do not adopt `the-janitor refs`' output behavior as a redactor: Kagi documents a concrete leakage case.

## Source evidence

- `corpus/knowledge/transcript-hygiene.md:49-62` defines two scanner classes: **HIT** patterns for material-shaped strings (including `op://`, key/token prefixes, and session-token names), and **WARN** patterns for credential-language field names. WARN covers request text discussing credentials and is not itself a secret-material verdict. At `:92-97`, its `--classify` path reports counts/classification and never matched text; this is a transcript-scan output contract, not a reason-field transformation rule.
- `corpus/knowledge/transcript-hygiene.md:28-37` scopes the scanner to text-bearing columns in the durable OpenCode database. Its bounds at `:119-131` say it catches only shapes it is told about, that high-entropy strings without a known prefix pass, and that this scanner's minimum prefix set should be extended rather than silently shrunk. That bounded, surface-specific detection set does not establish a complete redaction policy for argv/fd paths.
- `corpus/knowledge/op-ref-consumption.md:56-57` gives a direct counterexample to treating `refs` as safe redaction: `K=op://V/I/F` is echoed verbatim with trailing text, while a quoted reference is misreported as a non-reference even though `op run` resolves it. The decision table at `:199-200` says not to paste the output unless every key is a ref, and explains that plain values are not masked.

## C3 relevance and bounded finding

The named C3 target is `tools/souji-proc-census.sh`'s `argv-path-gone` / `fd-path-gone` reason field and its synthetic canary case in `tests/fixtures/r21-reason-canary.sh`. **[INFERENCE]** Kagi's cited rules concern scanning persisted transcript fields and inventorying dotenv values, not constructing a process-census reason from argv/fd paths. I found no C3-specific must-follow or must-not-absorb ruling in the permitted Kagi docs. A bounded reason not to absorb the Kagi pattern array wholesale is that its HIT/WARN split is tailored to transcript text, and its own stated limit excludes unknown high-entropy material; a Kagi-specific `refs` implementation also has the documented trailing-text leak above.

Accordingly, the Kagi material does not call for relaxing or replacing the frozen Souji C3 contract. Its most relevant cross-surface lesson is not to mistake a known-pattern scanner or inventory output for general-purpose redaction.

## Confidence and remaining unknowns

- **High** that Kagi defines the quoted, domain-local HIT/WARN taxonomy and warns against trusting `refs` as redaction.
- **Moderate** on the negative finding that no separate Kagi policy addresses Souji's reason field: this review was limited to `PROVINCE.md`, `SKILL.md`, and the three permitted knowledge files (`transcript-hygiene.md`, `credential-isolation.md`, `op-ref-consumption.md`); no Kagi implementation or other knowledge entry was inspected. No LSP device was exposed for this documentation-only review.
- No tools/tests, live process data, or credential/vault files were accessed; no tools were installed.
