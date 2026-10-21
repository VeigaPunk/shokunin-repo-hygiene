STATUS: PASS — For `revision-helper-selftest`, a run with return code 0, the exact positive stdout, and whitespace-only stderr must give `matched: false`. The base gives `matched: true`, so this is a false green that separates base from fix. Required compatibility condition: the real step's passing stderr is exactly zero bytes. This is a source-only analysis: nothing was executed, and no tools were installed.

## Combination analysed

Step: `revision-helper-selftest`, as defined in `census/round-21/run-acceptance.py` `make_steps` (lines 278–279) and frozen in `census/round-21/step-inventory.json` (lines 20–32):
`expected_summary = "SUMMARY total=11 failed=0"`, `pass_pattern = ^CASE\tpass\t`, `pass_count = 11`, kind `summary`.

Synthetic input (stderr/control combination "whitespace-only stderr"):

- returncode `0`
- stdout = 11 lines `CASE\tpass\t<id>\n` followed by `SUMMARY total=11 failed=0\n`
- stderr ∈ { `b"\n"`, `b" "`, `b"\t"`, `b"\r\n"`, `b"\x0b\x0c"`, `b"\xc2\xa0"` (NBSP), `b"\xe3\x80\x80"` (U+3000) }

## Literal expected decision

| vector | stderr bytes | base `matched` (source-inferred) | required changed `matched` |
|---|---|---|---|
| ws-newline | `0a` | true | **false** |
| ws-space | `20` | true | **false** |
| ws-tab | `09` | true | **false** |
| ws-crlf | `0d0a` | true | **false** |
| ws-vt-ff | `0b0c` | true | **false** |
| ws-nbsp | `c2a0` | true | **false** |
| ws-ideographic | `e3 80 80` | true | **false** |
| positive control | (empty) | true | **true** |

All seven whitespace vectors discriminate base from fix. The empty-stderr control has to stay `true` on both.

## Base trace (source-inferred, `run-acceptance.py`)

- Line 353: the input to `failure_lines` is `stdout + "\n" + stderr`. Whitespace contains no `FAIL\t`, `CASE\tFAIL\t` or `CASE\t…\tFAIL` marker, so `failures == []`.
- Line 367: `matched = returncode == 0 and not failures`, which is `True`.
- Lines 372–373: `summary_lines == ["SUMMARY total=11 failed=0"]`, which is `True`. `SUMMARY_RE` only reads stdout.
- Line 389: there are no `INVENTORY\t` lines and the expected auxiliary list is `[]`, which is `True`.
- Lines 400–404: 11 `^CASE\tpass\t` multiline matches equal `pass_count` 11, which is `True`.
- Line 417: `matched = matched and summary_match and pass_match` evaluates to **True**. Stderr is never consulted in the summary branch.
- In contrast, the counter branch (line 445) and the cache-demo branch (line 480) already require `not stderr`. On a decoded `str`, that rejects any non-empty value, including whitespace-only.

## Why whitespace-only must fail (no strip/trim)

1. **Consistency.** The counter and cache branches already treat `"\n"` as a failure. A summary-only `stderr.strip()` would make the same byte string fail in one step kind and pass in another.
2. **Ambiguity of "whitespace."** [INFERENCE from Python stdlib semantics, not opened this round] `str.strip()` removes all characters where `str.isspace()` is true, including NBSP and U+3000. `bytes.strip()` removes only ASCII whitespace. The `ws-nbsp` and `ws-ideographic` vectors therefore get different decisions depending on which strip an implementer picks. A byte-exact empty check has no such ambiguity.
3. **Q41.** Relaxing the oracle to get green is forbidden. If a real positive control emits stray bytes, the fix is to bind those bytes exactly, not to trim them.

## Compatibility requirement (L1 must establish)

All 18 real acceptance steps have to keep matching (preregistration: "retain all18 original real acceptance-step positive controls"). A strict empty-stderr predicate is compatible only if a real passing `tools/souji-rev-pin.py --selftest` run writes exactly zero bytes to stderr, i.e. `stderr_sha256 == e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The same holds for every other summary step.

- That file was not in the named read set, so whether it emits stderr is **unresolved**.
- [INFERENCE] The risk is real. A git-fixture selftest that does not capture child stderr can leak git hints/notices to stderr even on success. With `CHILD_ENV` setting `GIT_CONFIG_GLOBAL=/dev/null`, there is no `init.defaultBranch`, so `git init` may print its default-branch hint, and a detached checkout may print `HEAD is now at …`.
- If L1's changed-implementation acceptance run shows a non-empty stderr on a real summary step, do not weaken the predicate to a strip. Either add an exact per-step `expected_stderr` (literal bytes or sha256) to the step and the frozen inventory, or treat it as a producer defect. Do not silently turn the positive control red.

## Draft repair (for L1; not applied)

This is a single predicate applied to every step kind, which removes the two duplicate `not stderr` checks (clean cutover):

```python
    matched = returncode == 0 and not failures and stderr_bytes == b""
```

Replace line 367 with this, and delete `and not stderr` from lines 445 and 480. `decode_exact` uses `surrogateescape`, so it is lossless, and `stderr_bytes == b""` is equivalent to `not stderr` on the decoded string. The bytes check states that directly.

Draft synthetic-oracle vector (committed fixture, same file used for both base and changed bytes):

```python
REV_HELPER_STEP = {
    "name": "revision-helper-selftest",
    "argv": ["<PYTHON>", "-B", "<ROOT>/tools/souji-rev-pin.py", "--selftest"],
    "expected_summary": "SUMMARY total=11 failed=0",
    "pass_pattern": r"^CASE\tpass\t",
    "pass_count": 11,
}
POSITIVE_STDOUT = (
    "".join("CASE\tpass\tcase-%02d\n" % i for i in range(1, 12))
    + "SUMMARY total=11 failed=0\n"
).encode()
STDERR_WS_VECTORS = (
    ("ws-newline", b"\n", False),
    ("ws-space", b" ", False),
    ("ws-tab", b"\t", False),
    ("ws-crlf", b"\r\n", False),
    ("ws-vt-ff", b"\x0b\x0c", False),
    ("ws-nbsp", b"\xc2\xa0", False),
    ("ws-ideographic", b"\xe3\x80\x80", False),
    ("stderr-empty-control", b"", True),
)
# for name, err, expected in STDERR_WS_VECTORS:
#     got = module.summarize_result(REV_HELPER_STEP, 0, POSITIVE_STDOUT, err, REV, ROOT)["matched"]
#     assert got is expected  (base: True for every row -> 7 base_discriminating)
```

`summarize_result`'s summary branch does not read `revision` or `root`, so placeholders are fine for these two arguments. The fixture does not touch the process scanner, `/proc`, F5 code, or historical TSVs.

## Observed vs inferred vs unresolved

- **Observed (read):** `run-acceptance.py` lines 278–279, 330–333, 346–481 and 640–655; `step-inventory.json` lines 20–32; `AttackRunnerStepResults.md` (summary-stderr HIGH finding); `preregistration.txt`; `corpus/QUALITY.md` Q24/Q41/Q48.
- **Source-inferred:** the base and changed `matched` values in the table above. Nothing was executed.
- **Unresolved:** the actual stderr bytes of the real `revision-helper-selftest` and the other summary steps. `tools/souji-rev-pin.py` was not in the named set. L1's acceptance run decides this.
- No LSP device was available in this harness, and no grep fallback was used. Semantic claims come only from reading the named files. `cache-demonstration.py` was out of scope for this stderr question and was not read.
- No tools were installed or updated.
