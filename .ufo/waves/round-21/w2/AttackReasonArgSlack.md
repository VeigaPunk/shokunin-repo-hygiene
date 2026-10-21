# C3 attack: `xox[baprs]-` token in an argv-derived path

**Result: bounded static no-leak for this token class.** For a path that contains the exact lower-case `xox[baprs]-` pattern recognized by the script, the argv parser marks the source path secret and the reason formatter emits `[REDACTED]` in place of the whole path. The bound is 160 bytes. This is a source trace only; no census, fixture, selftest, or other project code was run, and no live `/proc` or historical census data was inspected.

## Pinned source and evidence chain

The checked-out files match the requested integrated revision: `tools/souji-proc-census.sh` SHA-256 is `3bc403440d67e2e8a096f52e3953cfb32a5a415c8e032d91d386c95f792fafb5` both from `git show 522dcd768ca90afe166532d37d306d3df70aeea5:tools/souji-proc-census.sh` and the named working file; the fixture likewise matches at `46a60e32c86301c8a4bb70bc83a04591749c6466c33cc5ef112a4f5d885add39`.

1. `redact_secrets` replaces any matched `xox[baprs]-[[:alnum:]_.-]+` token with `[REDACTED]` (script lines 238–240). `redact_command` applies that same function to command text and slices it to 160 bytes (244–248).
2. For each argv item, `read_argv_stream` separately saves its control-sanitized form, calls `redact_secrets` on the raw item, and sets `secret=1` when the result differs (263–268). With the fixture’s `.../missing/xoxb-SOUJIR21FAKE34567` candidate, the xox pattern changes the item, so `secret` is 1. The raw absolute candidate is still used for gone-path classification (270–281), but its secret provenance is stored in `PROC_GONE_SECRET` at 277–278.
3. `format_reason` replaces the whole path with `[REDACTED]` when that provenance flag is set, then applies `redact_secrets` once more and truncates the result to 160 bytes (250–255). Thus the argv path does not rely solely on token-substring replacement in the reason.
4. The census loop passes both the selected path and `PROC_GONE_SECRET` to `format_reason` and assigns its result to `reason` (384–388). The final row uses that formatted value as `safe_reason` and emits it directly in the reason column (403–415). The command column is separately redacted through `redact_command` (403–405).
5. `--reason-only argv` uses the same `read_argv_stream` and `format_reason` functions, prints only `REDACTED_REASON` plus a newline, then exits before the normal census branch (709–731). It does not print the raw `CMD_RAW` value. This is the fixture path, not an observed run.

The related `fd` reason path does not carry argv provenance, but `format_reason` still runs the xox regex over the full `fd-path-gone:<path>` value (253–254); its residual path is also length-bounded. That is not needed for the argv finding and does not establish broader coverage.

## Fixture and baseline extraction

`tests/fixtures/r21-reason-canary.sh` supplies the xoxb fake token in both argv and fd cases (lines 54–66). Its marker is `SOUJIR21FAKE34567`, so the fixture’s leak predicate checks that the canary value itself is absent from output (91–94, 99–112). It also checks output length, one-line formatting, the reason prefix, and no stderr (105–112). Static application to the argv case predicts a reason of `argv-path-gone:[REDACTED]\n`; this is not a test result.

The baseline argv parser is not a handwritten lookalike: the fixture reads the supplied `--base` source (line 20), regex-extracts the exact bodies of `path_under_prefix`, `top_level_scratch_gone`, `sanitize_field`, and `read_process_argv` (23–29), then inserts those bodies verbatim into `base_code` (30–45). Only the proc-path input is redirected to the synthetic temporary `cmdline` file; the fixture documents this substitution at 21–22 and creates no directory at its candidate prefix (46–49). The wrapper’s baseline reason serialization applies the extracted `sanitize_field` and emits the original `argv-path-gone:` field (32–37), matching the baseline census behavior in the supplied `6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh` source: the selected argv path was sanitized and prefixed, not redacted in the reason. Therefore this xox canary is expected to remain in the baseline reason, while the integrated parser/formatter closes it.

**Provenance limitation:** the fixture requires `--base` but reads whatever path the caller supplies; it does not itself validate that those bytes came from commit `6ff3413bba9c8430c3b0bc4d2052e21d0407183f` (14–20). The extracted bodies are exact relative to that input, but exact historical-baseline identity depends on the caller supplying the named commit’s source. This is an explicit fixture boundary, not evidence that the supplied invocation used the wrong source.

## Bounds and confidence

This finding is limited to contiguous lowercase tokens matching the existing xox regex in an argv item selected as a gone scratch path. It does not certify unknown/encoded token forms, arbitrary argv context, every output field, or untested runtime behavior. Confidence is high for the bounded source-level trace, with no runtime verification. No LSP device was exposed in this seat’s tool inventory; no grep-based semantic claim was used.