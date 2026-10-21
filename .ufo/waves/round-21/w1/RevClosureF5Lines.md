# r20 closure F5 source check

## Finding — F5 statement confirmed

The `closure.notes` F5 statement in `census/round-21/r20-closure-excerpt.json` is accurate for pinned source `544c8358039a07e8b45e6db72312da5c8d965275:tools/souji-proc-census.sh`.

- `sanitize_field` only replaces C0/DEL control characters with spaces (`tools/souji-proc-census.sh:188-189`). For argv-path reasons, the scanner calls it on `PROC_GONE_PATH` then assigns `argv-path-gone:$SAFE_FIELD` (`346-349`); for fd-path reasons it calls it on `PROC_FD_GONE_PATH` then assigns `fd-path-gone:$SAFE_FIELD` (`350-355`).
- The output path runs `redact_command "$CMD_RAW"` and assigns `row_cmd` (`364-366`), then sanitizes `reason` only (`367-368`). The output prints `safe_reason` and `row_cmd` as the ninth and tenth fields (`375-377`).
- Therefore `argv-path-gone` and `fd-path-gone` values receive control-character sanitization but none of the secret-matching redactions applied to `cmd`. This verifies the excerpt's distinction, not a claim that the reason is the full argv: those reason values are the selected gone-path strings.

## Command redaction coverage absent from reason

All `redact_command` content patterns in the pinned source:

1. Authorization bearer value: case-insensitive `Authorization:` + optional whitespace + case-insensitive `Bearer` + whitespace + a non-whitespace value (`196-198`).
2. Inline token option: case-insensitive `--token=VALUE`, where the value runs to whitespace (`200-202`).
3. GitHub-style token: `ghp_` followed by one or more alphanumerics, `_`, or `-` (`204-206`).
4. `sk-` credential: `sk-` followed by one or more alphanumerics, `_`, `.`, or `-` (`208-210`).
5. Password assignment: case-insensitive `password=VALUE`, value through whitespace (`212-214`).
6. URL user-info: a scheme matching `[[:alpha:]][[:alnum:].+-]*://`, then non-whitespace/non-`/`/non-`@` bytes through `@` (`216-218`).
7. AWS-style access key: literal uppercase `AKIA` followed by exactly 16 characters from `[0-9A-Z]` (`220-222`).
8. Slack-style token: literal lowercase `xox` + one of `baprs` + `-` + one or more alphanumerics, `_`, `.`, or `-` (`223-225`).

These are applied to the joined command string. Separately, `read_process_argv` handles the argv-element shape `--token=VALUE` through the inline pattern above, and handles a standalone `--token` element followed by a next argv element by replacing that next element with `[REDACTED]`; the standalone option comparison is case-insensitive (`249-255`). Neither shape receives any token-specific treatment in the reason path. The next-argument behavior is based on the flag being exactly `--token` ignoring case; it is not a general `--secret VALUE` rule.

`redact_command` also converts C0/DEL controls to spaces (`194`) and truncates the resulting command to 160 bytes (`226-227`); the reason sanitizer does not provide either secret-pattern redaction or that command-length bound.

## Evidence and gaps

Pinned-source inspection commands executed:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 544c8358039a07e8b45e6db72312da5c8d965275:tools/souji-proc-census.sh`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -E 'SAFE_FIELD=|value=\$\{value//|while \[\[ \$value =~|replacement=\$\{BASH_REMATCH|AKIA|xox|REDACTED_CMD=|redact_next|arg,,.*--token|CMD_RAW\+=' 544c8358039a07e8b45e6db72312da5c8d965275 -- tools/souji-proc-census.sh`

The first returned the pinned script; the second returned the matching rule/branch lines cited above. The tools did not expose shell exit codes, so none are asserted. No tests, selftest, or target code were executed. `xd://lsp` was not mounted in this session, so no LSP status/references/definition/diagnostics were available; this was a source-only verification, and no semantic caller claim is made beyond the displayed source paths.