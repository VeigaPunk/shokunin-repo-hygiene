# GrantPython — C1 delivery authorization calibration

## Observed snapshot and method

At the first source read, `git rev-parse HEAD` returned `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. The observed working-byte SHA-256 values were:

| path | SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `78d73d85ba198df6614a47b5d4d9388038da5c74407b475148713bc8958f6269` |
| `tools/souji-rev-pin.py` | `d49efa4e0ee4e9c275e2866dd7b6a20b201a4ac12d2225ca9a0772cfae6578c9` |
| `census/round-13/run-verification.py` | `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc` |
| `census/round-14/run-verification.py` | `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73` |
| `census/round-14/run-targeted.py` | `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2` |
| `census/round-14/cache-demonstration.py` | `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6` |

Review was source-only; no target code, selftest, build, or other check was executed. The requested LSP path was unavailable: `read xd://lsp` returned “No such tool” and listed mounted devices without LSP. Therefore no LSP status/references/definition/diagnostics were available; no grep was used as semantic proof.

## Calibration result

**Assigned discriminator: statically consistent.** The auditor does not grant an unrequested same-stem `.py` merely because it shares the report stem. `audit_seat` defaults `deliveries=()` and adds only that list to the report/OWN ONLY allowlist (`tools/souji-seat-audit.py:285-286, 312-315`); an otherwise unauthorized absolute target is classified `V-WRITE-SCOPE` (`:256-260`). The selftest explicitly expects the unrequested own-stem `.py` write to be major (`:497-503`, especially `:501`).

The exact requested case is accepted by the source logic: `delivery_paths` builds the sibling candidates, parses a line-leading `DELIVER:` or `Write`/`Create`/`Deliver` directive, and appends only a path equal to one of those candidates (`:129-140`). `run` passes those parsed deliveries into `audit_seat` (`:367-376`). Consequently, a directive naming the report's exact `.py` sibling makes that exact path allowed, while other same-stem suffixes remain outside the list (`:257-260`). This is a source-derived behavior assessment, not a fresh execution result.

The round-19 lesson records the historical defect as unconditional allowance of all five same-stem suffixes (`corpus/lessons/round-19-verifier-spotcheck.md:66`). The current observed source instead gates candidate paths on positive item directives; the historical finding is context, not a current-run receipt.

## Low — explicit-positive oracle coverage is missing

The checked-in selftest covers the negative own-stem `.py` case but not the requested-positive branch: its case loop calls `audit_seat` without `deliveries` (`tools/souji-seat-audit.py:509-511`), and the later `run` cases exercise summary and scratch wiring only, with prompts that contain no delivery directive (`:519-551`). Thus the source has the intended positive branch, but the current selftest would not catch a regression in directive parsing or `run`-to-`audit_seat` delivery wiring.

**Concrete oracle addition:** in the existing synthetic `run` spec, give item `S` the prompt `Create /home/u/P/f/lane/.ufo/waves/round-9/w1/S.py` and transcript `→ write(/home/u/P/f/lane/.ufo/waves/round-9/w1/S.py) ⇒ ok`; assert no violation for `S`. Keep the existing `delivery-py-unrequested` case as the negative counterpart. This is a test-coverage finding, not evidence that the current source rejects the explicit directive.

## Residual risk and verification gaps

- The positive directive behavior above is inferred from static control flow only; this lane did not execute a runtime oracle.
- This report adjudicates the assigned C1 own-stem delivery discriminator only. It makes no closure claim about receipt authenticity or the separate C2 measurement-binding claim.
