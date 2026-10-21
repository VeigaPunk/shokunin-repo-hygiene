# SimpRedactHelper — source-only proposal

Axes: C3 secret-pattern coverage; byte-for-byte cmd compatibility; separate whole-field bounds; minimum implementation weight.

## Finding and preserved contract

Candidate: extract the existing ordered pattern loop from `redact_command` into one unbounded helper, then bound cmd and reason in their respective wrappers. Keep `sanitize_field` control-only: it also serves boot_id and wchan, so changing its contract would widen scope. Retain the eight regexes, order, replacement spaces, and case handling exactly. Do not truncate before redaction. No implementation edits or deletions made.

Exact proposed replacement function text (replace the existing `sanitize_field`/`redact_command` section with this section):

```bash
sanitize_field() {
  SAFE_FIELD=${1//[$'\001'-$'\037'$'\177']/ }
}

redact_secrets() {
  local value=$1 replacement
  value=${value//[$'\001'-$'\037'$'\177']/ }

  while [[ $value =~ ([Aa][Uu][Tt][Hh][Oo][Rr][Ii][Zz][Aa][Tt][Ii][Oo][Nn]:[[:space:]]*[Bb][Ee][Aa][Rr][Ee][Rr][[:space:]]+)[^[:space:]]+ ]]; do
    replacement=${BASH_REMATCH[1]%%:*}': [REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ (--[Tt][Oo][Kk][Ee][Nn]=)[^[:space:]]+ ]]; do
    replacement=${BASH_REMATCH[1]}' [REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ (ghp_)[[:alnum:]_-]+ ]]; do
    replacement=${BASH_REMATCH[1]}'[REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ (sk-)[[:alnum:]_.-]+ ]]; do
    replacement=${BASH_REMATCH[1]}'[REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ ([Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]=)[^[:space:]]+ ]]; do
    replacement=${BASH_REMATCH[1]}' [REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ ([[:alpha:]][[:alnum:].+-]*://)[^/@[:space:]]*@ ]]; do
    replacement=${BASH_REMATCH[1]}'[REDACTED] @'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ AKIA[0-9A-Z]{16} ]]; do
    value=${value/"${BASH_REMATCH[0]}"/'[REDACTED]'}
  done
  while [[ $value =~ xox[baprs]-[[:alnum:]_.-]+ ]]; do
    value=${value/"${BASH_REMATCH[0]}"/'[REDACTED]'}
  done
  REDACTED_FIELD=$value
}

redact_command() {
  redact_secrets "$1"
  # Bash substring slicing is byte-based because LC_ALL=C is fixed above.
  REDACTED_CMD=${REDACTED_FIELD:0:160}
}

redact_reason() {
  redact_secrets "$1"
  # Bound the complete reason, including argv-path-gone: or fd-path-gone:.
  REDACTED_REASON=${REDACTED_FIELD:0:160}
}
```

Exact intended census emission call-site substitution:

```bash
    redact_reason "$reason"
    safe_reason=$REDACTED_REASON
```

This replaces only the final `sanitize_field "$reason"` / `safe_reason=$SAFE_FIELD` pair. The new synthetic reason-only entry point must use this same wrapper on the fully constructed reason, not print a separately sanitized path. The earlier path sanitization can remain to minimize integration change; its control replacement is idempotent. Cmd and reason each own their length slice, even though both limits are currently 160. No configurable-bound framework or second pattern list is needed.

## Coverage boundary / counterexample

The helper extraction alone is NOT all of C3. Frozen r2 requires argv provenance handling before path extraction loses context. Synthetic example: NUL-delimited `worker`, `--token`, `/tmp/nonexistent-fake-secret/file`. The candidate path has no matching secret-pattern syntax after extraction; merely passing `argv-path-gone:/tmp/nonexistent-fake-secret/file` through this helper leaves the fabricated secret raw. Likewise `--password=/tmp/nonexistent-fake-secret/file` loses its password marker when only its value becomes the gone path. The argv reader must classify the original element and the argument following `--token`, retaining the classification for the selected candidate, then construct `argv-path-gone:[REDACTED]` for a secret-bearing candidate. Do not try to fix this by adding generic path matching or by changing cmd's historical regexes. Such changes would risk cmd byte compatibility and non-secret path fidelity.

[INFERENCE] Cmd byte compatibility follows statically because control normalization, all eight sequential transformations and final 160-byte slice are unchanged; the extraction adds only an intermediate shell variable, with no command substitution, subprocess, newline stripping or output. This is not an executed equivalence result. The extra global `REDACTED_FIELD` is the small tradeoff, matching the existing output-variable convention; callers copy the result immediately. No added arbitrary truncation parameter or output-variable indirection is required.

## Evidence and limits

- Read frozen oracle: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-21/preregistration.txt`, especially C3 r1–r5 and the synthetic-only restriction.
- Read required godspeed skill.
- Executed source retrieval only: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 544c8358039a07e8b45e6db72312da5c8d965275:tools/souji-proc-census.sh`. Tool returned the committed script; its result did not expose a numeric exit code. No target script, test, formatter, build, live census or /proc read was executed.
- Source inspected: `sanitize_field`, `redact_command`, `read_process_argv`, and census reason construction/final sanitation; all from the named committed file.
- No dead-function deletion or absence-of-callers claim; no LSP semantic proof is asserted. Both existing functions have visible callers in the retrieved source and are retained. The candidate removes duplicate future pattern authority, not an allegedly unreachable function.
- No scratch copy needed for this no-edit proposal. No production or VCS writes performed; only this authorized report was written. Shared-tree byte identity was not measured and is not claimed.
- No tool installations or upgrades.
- Unexecuted integrator acceptance: synthetic C3 canary fixture, including split-token/path-context cases, control and non-secret paths, every inherited cmd pattern and full-field 160-byte boundaries. Do not execute the prohibited live selftest or r18 fixture.

Stop point: further consolidation of `sanitize_field` into secret redaction would alter unrelated field contracts; sharing the cmd bound or expanding its regexes would risk the required byte compatibility. This proposal deliberately stops before either change.
