# ReceiptSpec — C1 consumed-spec byte fingerprint

## Finding — repeated-path drift can replace the spec receipt bytes

**Severity: Major for the C1 receipt contract; conditional on a same-path alias and a change between reads.** In `tools/souji-seat-audit.py:357–362`, `consume()` reads bytes and assigns them to `input_bytes[str(path.resolve())]` without checking whether that resolved path was consumed before. The spec is parsed from the first `consume(spec_path)` result at line 366. Later, each transcript is consumed at approximately lines 387–390. If `spec_path` is also the transcript path `tdir / (name + ".txt")`, the second `consume()` overwrites the first bytes stored under the same path key. The end check at lines 401–404 compares the current file only with that last stored value, and lines 410–411 fingerprint only the surviving dictionary value. Thus a changed-and-still-present second version passes the check and is reported as the spec digest even though `json.loads` parsed the first version. This contradicts the preregistered requirement that repeated input reads detect drift and that the receipt bind the actual spec bytes consumed.

**Concrete counterexample/oracle change:** add a deterministic selftest with `spec_path == tdir / "S.txt"` and a valid first-read JSON spec naming item `S`. Control `Path.read_bytes` for that one resolved path to return the spec bytes on the first read, distinct transcript bytes on the second read, and those transcript bytes again on the final recheck. Assert `run()` raises `ValueError` and produces no receipt; the current implementation instead overwrites the first bytes and can return the second digest. The minimal production guard is for `consume()` to reject a second read of an already-seen resolved path when its bytes differ, rather than overwrite the saved bytes.

## Static evidence and limits

There is no JSON reserialization in the ordinary spec path: `run()` parses `consume(spec_path).decode("utf-8")` directly (line 366), while `input_sha256` hashes the raw `bytes` retained by `consume()` (lines 357–362, 410–411). For distinct, stable paths this does fingerprint the exact bytes parsed. The defect is that the path-keyed cache silently replaces those bytes on a repeated path read, defeating that property for the counterexample above.

The existing `selftest()` does not assert any `input_sha256` value: its `run()` checks cover summary/transcript behavior (lines 536–540) and grant classifications (around lines 595–605). Add the exact-byte receipt oracle above; do not treat the existing grant cases as evidence for spec fingerprint fidelity.

**STATUS: OPEN.** Source inspection identifies a concrete route to a false spec receipt and a falsifiable deterministic oracle, but no test or runtime execution was performed in this read-only review. No output from target code is claimed.

## Observed source snapshot

At the first bounded source read, the observed repository `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline). Working-file SHA-256 values captured in that read batch:

| Path | SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `9ac0c6e08aad430e964a6ced088409e300e93705ea048be09af1479bdb26eabd` |
| `tools/souji-rev-pin.py` | `d49efa4e0ee4e9c275e2866dd7b6a20b201a4ac12d2225ca9a0772cfae6578c9` |
| `census/round-13/run-verification.py` | `a10d66ca6728f641fb4144c7fcfb2996ff1940fd7c6e2f69e30230073a9116e8` |
| `census/round-14/run-verification.py` | `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502` |
| `census/round-14/run-targeted.py` | `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895` |
| `census/round-14/cache-demonstration.py` | `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213b` |

No LSP device/server was available in the exposed tool inventory; conclusions above are from bounded source reads, not grep as semantic proof. All review work was static. No builds, tests, linters, formatters, smokes, or target-code execution were run; no tools were installed or updated.
