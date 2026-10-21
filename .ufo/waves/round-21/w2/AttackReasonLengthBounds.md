# AttackReasonLengthBounds — C3 reason length sink

## Scope and method

Attacked pinned integrated source `522dcd768ca90afe166532d37d306d3df70aeea5`, specifically long ordinary argv/fd reason values, the placement of the 160-byte cut, and the canary fixture's baseline extraction. Compared the fixture's extracted baseline helpers with `6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh`.

This is a source-only trace, not an executed test. I did not run either script, inspect live `/proc`, or inspect historical snapshots.

## Production sink trace: bounded for the assigned ordinary-path class

- `LC_ALL=C` is exported at script line 13, so Bash substring slicing uses bytes; the nearby comment at line 246 also states this for the command sink.
- `format_reason` at lines 250–255 first replaces a provenance-marked argv path with `[REDACTED]` (252), then calls `redact_secrets` on the **complete** `kind-path-gone:path` string (253), and only then slices `REDACTED_FIELD` to 160 bytes (254). `redact_secrets` first substitutes control bytes (209), then applies the secret-pattern loops (211–240). Thus neither the kind prefix nor an unmasked suffix can escape the 160-byte bound; regex masking is not applied only to a pre-truncated prefix.
- The argv census path calls `format_reason argv ...` at lines 384–387; fd calls `format_reason fd ...` at lines 389–394. The `/proc`-free dispatch at lines 711–732 calls the same `read_argv_stream` and `format_reason` functions (713–715, 728), and emits only `REDACTED_REASON` plus newline (730). Census emission places that same reason string in the TSV row (413–415).
- For the fixture's ordinary bound input (fixture lines 81–83), let `P` be its generated prefix (`/var/tmp/souji-r21-canary-` plus 12 hex bytes: 38 ASCII bytes). The path is `P + '/' + 400*z`, 439 bytes. No listed redaction pattern matches the `z` suffix. Before slicing, the complete argv reason is 15 + 439 = 454 bytes; the fd reason is 13 + 439 = 452 bytes. The production slice therefore retains exactly the first 160 bytes of each complete reason, including the kind prefix. This is the same byte operation the fixture expects at line 83: `(mode + '-path-gone:' + path).encode()[:160] + b'\n'`. The reason is bounded; the path tail is intentionally not preserved.
- In the fixture's plain and controls cases (76–80), the selected non-secret path is formatted without secret-pattern substitutions; control bytes become spaces through `redact_secrets` as expected. The fd dispatch strips one trailing input newline at lines 718–719 before prefix selection and formatting; argv uses NUL-separated input through `read_argv_stream`.

**Static result for the assigned production sink:** no length-bound or truncate-before-mask divergence found. This is a source-derived result, not an observed fixture pass.

## Baseline extraction and wrapper fidelity

Fixture lines 21–29 extract four functions from `--base` using their literal function headers and the first subsequent column-zero closing brace. In the actual pinned baseline source, the extracted spans are:

- `path_under_prefix`: baseline lines 160–167
- `top_level_scratch_gone`: 168–186
- `sanitize_field`: 188–190
- `read_process_argv`: 230–257

Each span runs from the function header through its function-closing `}`; none has an intervening column-zero `}`. The fixture therefore uses exact source bodies for these four helpers, not rewritten helper lookalikes. The only substituted input root is the fixture's temporary `cmdline` file read by the unchanged `read_process_argv` body (fixture comment at 21–22; driver at 30–45).

The baseline driver does synthesize the small reason-emission wrapper rather than extracting `census()`. That wrapper is output-equivalent for these inputs to baseline census lines 345–368: the baseline sanitizes the selected path, prefixes `argv-path-gone:` or `fd-path-gone:`, and sanitizes the reason again; the wrapper sanitizes the path and prints the same ASCII prefix and field. The baseline has no reason redaction or 160-byte reason slice. For the ASCII canary values in this fixture, that means the marker survives in every selected path.

Two harness limitations remain visible in source:

1. The fixture reads whatever file is passed as `--base` (line 20); it does not itself attest that the file came from commit `6ff3413...`. The extraction is exact for the baseline file inspected here, but revision identity depends on the caller supplying that file.
2. Although the constructed cases imply 19 baseline leaks (8 pattern canaries in each of argv/fd plus 3 argv provenance cases; fixture lines 54–73), the fixture does not enforce that every one leaks. It accumulates `base_leaks` at lines 93–94; `--baseline-only` checks only return codes at 95–97; normal mode's final guard at line 117 requires merely `base_leaks != 0`. Thus a partial baseline extraction/regression where some expected baseline canaries stop leaking can still pass the aggregate baseline guard. The fixture prints per-case `base_leak` values (112) and the aggregate (116), but does not assert the preregistered “every argv/fd canary leaks” condition.

## Coverage boundary

The fixture separates long ordinary-path bound cases (81–83) from secret-pattern cases (54–66); it does not combine a long path with a secret marker at/near byte 160. Production source order establishes mask-before-slice, but the fixture has no direct regression case for a boundary-adjacent secret marker. This is a test-coverage limitation, not evidence of a production leak in the assigned ordinary-path class.

## Conclusion and confidence

**No static counterexample found for long ordinary argv/fd paths:** the complete kind-prefixed reason is redacted/sanitized first and then byte-sliced to at most 160 bytes. The fixture's expected bound expression includes the kind prefix and agrees with that source path. **Baseline helper extraction is exact** for the four named helpers in the inspected `6ff3413` source; the reason-emission wrapper is synthesized but equivalent for these canaries. Confidence: high for the inspected source control flow; no runtime behavior was measured.