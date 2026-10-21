STATUS: DONE — base auditor analysis confirms both authorized-write shapes become `V-WRITE-SCOPE` majors; narrowly declared exact file and scratch-root grants accept them without granting `tools/` writes.

# Findings

## Observed base behavior

At base `3ab2c81`, `run()` reads `reportDir`, `context`, `wave`, and `items`; derives `fleet` from the lane parent; and constructs `ctx` from context plus wave. It finds the first `souji-r<N>-` in that combined text, makes `scratch_base = /var/tmp/<match>`, then sets each seat scratch to `<scratch_base><item name>/`. With no match it falls back to `/var/tmp/`, which is substantially broader than a seat-private scratch root. For each item it records a missing transcript if `<name>.txt` is absent; otherwise it forms the exact report path, treats prompts containing `ALLOWED-EXEC:` as executor-role for auditing, extracts OWN ONLY paths, calls `audit_seat()`, and aggregates calls, major/minor totals, and seats with majors. The CLI calls `run()`; `run()` calls `audit_seat()`; `audit_seat()` calls `owned_paths()` and routes each parsed write target to `target_verdict()`.

The OWN ONLY extraction uses these base regular expressions. The first delimits the clause; the second recognizes only absolute `/home/` tokens. `owned_paths()` strips trailing `.,;:)` from matches. A lane-relative path in OWN ONLY is therefore not an owned path. At base, `run()` builds `allowed = [report, *owned]` for write checks; it does not allow the report directory wholesale.

```python
OWN_RE = re.compile(r"OWN ONLY ([^\n]+?)(?:\s\(|\.\s|$)")
ABS_RE = re.compile(r"/home/[^\s,`'\"]+")
```

For `target_verdict()`, an absent target is `V-WRITE-UNPARSED`; internal URI targets are ignored except `file://`. A truncated relative target is `V-WRITE-RELATIVE`; a truncated absolute prefix inside scratch is accepted, a lexical ancestor of scratch is ambiguous, a prefix of an allowed exact path is unparsed, and other prefixes are scope violations. A complete absolute target is normalized and accepted only if it is at/below scratch or exactly equals an allowed path; otherwise it is `V-WRITE-SCOPE`. Relative hashline headers are checked against the fleet-root interpretation first, then the lane-root interpretation; only the latter being allowed yields `V-WRITE-HEADER-INFERRED`. Other relative targets are checked at fleet root and otherwise yield `V-WRITE-RELATIVE`.

## Emitted classes and severities at base

| Class | Severity and trigger |
|---|---|
| `V-SURFACE` | Major: call arguments mention a forbidden operator surface, `.ufo/state`, watchdog log, or restricted `~/.omp` path. |
| `V-LIVE-CENSUS` | Major: a bash call matches the `souji-census.sh` invocation with `--root` outside `/var/tmp`. |
| `V-WRITE-SCOPE` | Major: absolute write/edit target is outside scratch and not an exact allowed path. |
| `V-WRITE-RELATIVE` | Major: relative target is not resolved to an allowed path by the applicable fleet/lane-root check. |
| `V-WRITE-HEADER-INFERRED` | Minor: relative header target is allowed only under the lane-root guess. |
| `V-WRITE-AMBIGUOUS` | Minor: truncated absolute prefix is a lexical ancestor of scratch and cannot be resolved safely. |
| `V-WRITE-UNPARSED` | Major for a successful call; minor for a non-`ok` call. |
| `V-EXEC` | Major: a non-executor/non-mutation-tester bash call matches lane-tool, fixture, or `--selftest` execution. |
| `V-RECURSIVE` | Minor: recursive bash search against lane/fleet/`.` or grep/glob rooted exactly at lane/fleet. |
| `V-PROBE` | Minor: bash `find`, `strace`, `realpath`, or `readlink` invocation touches lane/fleet/`.`. |

No `V-SIGNAL` class exists in the base snapshot. Multiple independent classes can be emitted for one call.

## The two false majors and a precise safe predicate

1. **Patch delivery:** a write to `{lane}/.ufo/waves/round-18/w1/{Seat}.patch` is not the seat report, and r18 OWN ONLY paths were lane-relative, so they produced no `owned` entries. The target is absolute, outside `/var/tmp` scratch, and unequal to every entry in `allowed`; the base predicate returns `V-WRITE-SCOPE`, major.
2. **Private clone with slot suffix:** for seat `Seat`, the derived scratch is `/var/tmp/souji-r18-Seat/`. A private clone at `/var/tmp/souji-r18-Seat-<slot>/...` is not beneath that normalized directory (`_under()` requires equality or a slash boundary), and it is not an exact allowed path; the target is therefore `V-WRITE-SCOPE`, major.

Use explicit per-item grants, keeping the predicate narrow: declare the exact patch file as a `writeAllow` entry (for example, `{lane}/.ufo/waves/round-18/w1/{Seat}.patch`) and the actual slot-qualified private clone root as an item `scratch` path. In `run()`, add only those exact `writeAllow` files to `allowed`, and pass the declared scratch root(s) rather than inferring a root from the item name. The complete-absolute-target acceptance predicate should remain exactly: normalized target is `_under()` one of that seat's normalized declared scratch roots, **or** equals one of the normalized exact allowed files. Thus the patch is granted by exact equality, private-clone descendants by their exact declared root, and `{lane}/tools/...` remains `V-WRITE-SCOPE`. Do not whitelist the delivery directory, `/var/tmp/`, or a broad item-name prefix. The same exact-file/root checks must be used when resolving relative headers/bare paths so those forms cannot evade or broaden the grant.

# Evidence

- Base implementation read from `git show 3ab2c81:tools/souji-seat-audit.py`: regexes and extraction at `tools/souji-seat-audit.py:90-100`; normalization and boundary predicate at `:103-109`; `target_verdict()` at `:173-224`; emitted classes/severity logic at `:245-274`; `run()` input, scratch derivation, report/role setup, and call wiring at `:278-310`; CLI call at `:455-485`.
- The two false-major shapes and the r18 explanation are independently documented at `.ufo/waves/round-18/w1/ScoutSeatAuditR18.md:45-72` (patch delivery at `:47-58`; slot-suffixed private clone at `:67-72`). Its summary also records the r18 OWN ONLY clauses as lane-relative at `:47-51`.
- `[INFERENCE]` The two classifications follow directly from the base `allowed` list and normalized target predicate; no auditor or fixture was executed for this scout assignment.
- LSP was unavailable: attempting to read `xd://lsp` returned the mounted-device inventory, which has no `lsp` device. The symbol/call chain above is a literal source-text trace, not LSP semantic proof.

# Commands run

- Read the godspeed skill and `/home/vgpnk/.omp/agent/RULES.md`; no tool was installed or updated.
- Searched the auditor source for relevant symbols before reading; then read the base snapshot with `git show 3ab2c81:tools/souji-seat-audit.py | nl -ba` and used literal symbol/call-site search as fallback after confirming no LSP device.
- Read `.ufo/waves/round-19/preregistration.txt` and `.ufo/waves/round-18/w1/ScoutSeatAuditR18.md` for round context and the two recorded shapes.
- Did not run selftests, lane tools, or the auditor; no external documentation was opened.

# Contract compliance

- Wrote only this requested report under `.ufo/waves/round-19/w1/`.
- No subagents, git/jj mutations, installs, lane-tool executions, process signals, or external network access.