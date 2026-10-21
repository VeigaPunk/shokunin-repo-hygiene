# GrantText — C1 calibration review

## Major finding — delivery parser treats a negated directive prefix as permission

**STATUS: OPEN.** An item can mention the exact same-stem `.txt` artifact in a line whose trailing prose explicitly denies authorization, yet the parser grants that artifact. A successful write to it then avoids the required `V-WRITE-SCOPE` major. This contradicts the C1 requirement that a negative prose filename mention is not permission and leaves the unrequested-`.txt` case falsifiable by a concrete counterexample.

**Source evidence:** `tools/souji-seat-audit.py:139-143`. `delivery_paths()` matches a line beginning with `Write <absolute-path>` and checks only that the captured path is a candidate sibling. The regex accepts whitespace after that path, and the function does not inspect the remainder of the line for a denial. `tools/souji-seat-audit.py:597-598`'s `incidental-not-grant` oracle covers an `Inspect <path>` line, not a candidate path followed by explicit negation.

**Counterexample / oracle change:** For a seat whose report path is `R.md`, supply this item-prompt line:

```text
Write R.txt — NOT AUTHORIZED; the filename is shown only as a negative example.
```

Then record `→ write(R.txt) ⇒ ok`. Expect a major `V-WRITE-SCOPE`: the line is a denial, not an authorization. Add this as a grant-parser oracle case (with the concrete absolute sibling path); keep the existing positive exact-path directive case allowed. A narrow fix is to recognize only a complete, unambiguous positive directive form, rather than accepting a directive-looking prefix and ignoring trailing prose.

## Observation and verification boundary

- Observed HEAD: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`.
- The auditor was worktree-modified during this review. The first fingerprint call recorded SHA-256 `9ac0c6e08aad430e964a6ced088409e300e93705ea048be09af1479bdb26eabd`; after the bounded source reads, a fingerprint call recorded `98034593ea4480922ad46e944bc62ea0b10365a016275c029664e9135f1d2c07`. The finding cites the later-observed parser at lines 139–143; I did not wait or poll for further edits.
- This is static source analysis only. No target code, fixture, test, or runtime was executed; no historical execution receipt is claimed.
- No `lsp` device/status route was available in this seat's tool inventory. Literal grep fallback supplied line locations only; the finding is based on the displayed parser logic, not grep as semantic proof.
- No tool was installed or updated.
