# Scout — `bash -n` limits: unterminated here-docs, missing `fi` in functions defined after use, `set -n` in sourced files (S043 scope)

Seat: SoujiR16.ScoutBashNLimits-4. Recon only; no lane file edited except this report.
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Shell under test: **GNU bash 5.3.20(1)-release (x86_64-pc-linux-gnu)**.
All URLs accessed **2026-10-20**.

HEAD note: the session opened with HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; the worktree
advanced during the session to `163158a706352f1c0ee3521c4da2e5289970db57` (descendant, the
lesson/SOURCES commit). `tools/souji-census.sh` is the same blob at `0a70bef`, `a6ec7810`,
`163158a7` and in the worktree: `b8442e2ead501ad0ba1f68472e265516040f4aa0`, sha256
`64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`. Every census line number and
claim below therefore holds at both revisions. `tools/souji-landing-gate.py` is likewise unchanged
between the two commits (blob `7d32ba7c…`).

Probe discipline: every behavioural probe below is a `bash -n` invocation fed from stdin via
`printf '%b' … | bash -n` (one file-form check via process substitution, `bash -n <(…)`). No lane
tool was executed, no file was created, nothing was written outside this report. Where a conclusion
needs *runtime* behaviour that `bash -n` cannot exercise, it is marked **[INFERENCE]** and grounded
in the manuals, not measured.

## Question

S043 says `-n` is a parse-only check: "Read commands but do not execute them", detecting syntax
errors only. Three constructs decide how far that claim carries for the round-16 operability story:

1. an unterminated here-document (the r15 "truncated mid-write" failure mode);
2. a missing `fi` inside a function, in particular a function defined after its use;
3. `set -n` in a sourced file.

What does `bash -n` do on each, and what does that mean for `tools/souji-census.sh` at HEAD?

## Short answer

| construct | `bash -n` rc | stderr | rc-only "parses" check | gate's any-stderr check | why |
|---|---|---|---|---|---|
| unterminated here-document at EOF | **0** | warning | **passes (false clean)** | **fails** | EOF is treated as the delimiter with only `warning: here-document … delimited by end-of-file` |
| missing `fi` inside a function defined after use (or never executed) | **2** | syntax error | fails (correct) | fails | `-n` parses every function body regardless of call order or reachability; reports at the body's `}` or at EOF |
| `set -n` in a sourced file | **0** | none | passes (blind) | passes (blind) | `-n` never executes `source`/`.`, so the sourced file is never opened, let alone parsed; the parent's check cannot see it |
| `source`/`.` of a missing file | **0** | none | passes (blind) | passes (blind) | same: the `.` builtin is read, not executed |
| `eval 'if true; then'` | **0** | none | passes (blind) | passes (blind) | the eval string is parsed only when `eval` executes |
| unset variable under `set -u`, `$((1+))`, undefined function call, NUL byte | **0** | none | passes | passes | S043's "not runtime/unset-variable/undefined-function" negatives all reproduce |

S043's claim **holds** on all three constructs; the practical correction is that an unterminated
here-document is not a bash *error* at all, so any checker that tests only `$?` will call a
truncated file clean. The landing gate's `check_bash` already reads stderr (`tools/souji-landing-gate.py:208-209`),
which closes that hole; the C1 matrix records only the rc (`census/round-16/run-matrix.py:110-111,
124`), which does not.

## Findings

### 1. Unterminated here-document: rc 0, warning only

```
$ printf '%b' 'cat <<EOF\nhello\n' | bash -n
bash: line 2: warning: here-document at line 1 delimited by end-of-file (wanted `EOF')
rc=0
```

The same warning appears for a file argument (process substitution, so the warning is prefixed with
the path rather than `bash:`):

```
$ bash -n <(printf 'cat <<EOF\nx\n')
/dev/fd/63: line 2: warning: here-document at line 1 delimited by end-of-file (wanted `EOF')
rc=0
```

That is exactly the shape the gate's `check_bash` captures: `proc.returncode == 0` but
`err.strip()` non-empty → finding `bash -n rc=0 but stderr: <path>: line N: warning: here-document …`
(`tools/souji-landing-gate.py:201-210`). `tests/fixtures/r16-landing-gate.py:267-278` pins this class
("bash -n exits 0 but warns on stderr; the gate must treat stderr as a finding").

More probes in the same class:

| id | input shape | rc | stderr |
|---|---|---|---|
| E11 | complete top-level code, then `cat <<EOF`, then body to EOF | 0 | warning |
| H1 | terminator line `EOF ` (trailing space — not a match) | 0 | warning |
| H2 | terminator line `\tEOF` under `<<EOF` (leading tab — not a match) | 0 | warning |
| H3 | `<<-EOF` with tab-indented body and terminator | 0 | — (valid) |
| H8 | uniformly CRLF file, opener `<<EOF` and terminator `EOF\r\n` | 0 | — (the `\r` belongs to the delimiter word on both the opener and terminator lines, so they match) |
| E5 | unterminated here-doc **inside** `f() { … }` | **2** | warning + `syntax error: unexpected end of file from '{' command on line 1` |
| H5 | unterminated here-doc inside `$( … )` | **2** | warning + `unexpected EOF while looking for matching ')'` |
| E14 | `if true; then` + `cat <<EOF` + body `fi` (no terminator) | **2** | warning + `unexpected end of file from 'if' command on line 1` |

So the truncation is caught only when it also leaves a construct open (`{`, `(`, `if`). A file cut
at top level inside a here-document passes with rc 0. The same applies to a truncation that happens
at a **command boundary** — `bash -n` cannot know the intended file was longer; only a byte pin
(e.g. `LG-FROZEN-PIN`) can detect that.

Verdict: S043 holds ("syntax errors only" — bash classifies this as a warning, not an error). As an
operability signal, `bash -n` rc alone is **partial**: the gate's any-stderr rule is required; the
C1 matrix's rc-only record is not equivalent.

### 2. Missing `fi` inside a function defined after use: rc 2, caught regardless of order/reachability

Call before definition, with a missing `fi` inside the body:

```
$ printf '%b' 'main\nmain() {\n  if true; then\n    echo hi\n}\n' | bash -n
bash: line 5: syntax error near unexpected token `}'
bash: line 5: `}'
rc=2
```

The diagnostic points at the function body's closing brace, **not** at the call site, and the
definition's position after the call changes nothing. Variants:

| id | input shape | rc | stderr names |
|---|---|---|---|
| E3 | top-level `main` then `main() { if … }` (no `fi`) | 2 | `unexpected token '}'` at the body's `}` |
| E31 | `exit 0` before the same malformed definition | 2 | `unexpected token '}'` |
| H7 | two functions, second never called and malformed | 2 | `unexpected token '}'` |
| H6 | malformed function with no closing `}` at all | 2 | `unexpected end of file from 'if' command` |
| E35 | one-line `f() { if true; then echo x; }` | 2 | `unexpected token '}'` |
| E34 | missing `fi` inside `( if … )` | 2 | `unexpected token ')'` |
| E2 | top-level missing `fi` (no function) | 2 | `unexpected end of file from 'if' command on line 1` |
| E16 | top-level missing `done` | 2 | `unexpected end of file from 'for' command on line 1` |
| E23 | two nested unclosed constructs (`if`, `for`) | 2 | one error only: `unexpected end of file from 'for' command on line 3` (innermost opener named) |

Order and reachability do not matter to `-n`: the parser walks the whole input and parses each
function definition as it reaches it, so a body that a run might never reach is still checked.
Conversely, the call itself is not checked: a call to a function that is defined later (valid body)
is rc 0 (E4), and a call to a function that never exists is rc 0 (E33, even under `set -u`) — this
is S043's "undefined-function checking" limit.

**Real lane instance (r15 baseline).** `git show b410186:tools/souji-census.sh` fails `bash -n` with
rc 2 at line 1368:

```
bash: line 1368: syntax error near unexpected token `}'
bash: line 1368: `}'
```

The cause is inside `list_repos()`: the outer `if` opened at line 1324
(`if [ "$INCLUDE_ROOT" = 1 ] && … ; then`) never gets its `fi`; only the inner `if` is closed at
line 1334, and `shopt -s nullglob` starts at line 1335 while the outer `if` is still open. The
parser reaches the function's `}` at line 1368 and reports there. HEAD closes both: the inner `fi`
is at line 1271 and the outer `fi` at line 1272 (verified with `cat -A`); `bash -n` on the HEAD
census is rc 0 with empty stderr. This is exactly the construct in the assignment, and it shows
`bash -n` catches a missing `fi` inside a function whose error only manifests at the body's closing
brace.

**[INFERENCE] Runtime asymmetry.** A plain run parses a function body when it reaches the
definition; if an earlier command exits (explicit `exit`, or `set -e` on a failing call before the
definition), the runtime may never notice the malformed body, while `bash -n` rejects the file.
Conversely, for b410186 the malformed `list_repos` is top-level and reached before any dispatch, so
a run would abort with the same line-1368 error; the static verdict matches runtime there. The
manual describes the shell's read/parse/execute cycle per command ("The following is a brief
description of the shell's operation when it reads and executes a command"; `-t` is documented as
"Exit after reading and executing one command"), which is the basis for the inference. For this
lane the asymmetry runs in the safe direction: the static check is stricter, and the census defines
all functions before its first top-level call (dispatch only after line 1858).

Verdict: **holds** — `bash -n` detects a missing `fi` inside a function defined after use; no
counterexample found. The limit is only that it cannot tell whether the malformed body would have
been executed.

### 3. `set -n` in a sourced file: invisible to `bash -n`

`bash -n` does not execute the `.`/`source` builtin, so it never opens the sourced file:

```
$ printf '%b' '. /nonexistent/nope-xyz.sh\n' | bash -n        # rc=0, no stderr
$ printf '%b' 'source /nonexistent/nope-xyz.sh\n' | bash -n   # rc=0, no stderr
```

A nonexistent path is the strongest proof: if bash had attempted to read it, it would have errored.
The same holds for `set -n` placed in the parent (never executed, so no effect on the parse) and for
content behind `.`:

| id | input shape | rc | stderr |
|---|---|---|---|
| E6 | `.` a nonexistent file | 0 | — |
| E7 | `source` a nonexistent file | 0 | — |
| E10 | `set -n` then `echo after` | 0 | — |
| E17 | `set -n`, `. ./does-not-exist.sh`, `echo after` | 0 | — |
| E22 | `set -n` then a missing-`fi` `if` | **2** | syntax error — `set -n` does not suppress parsing of the file being checked |
| E32 | `. ./lib.sh` then `echo ok` | 0 | — |

Consequences:

- A syntax error in a sourced helper is **not** part of the parent's `bash -n` verdict. The landing
  gate only parses each cited `.sh` blob separately (`CITED_PATH_RE` at
  `tools/souji-landing-gate.py:58-60`, applied at 539-551; `parse_script` at 224-231), so a sourced
  helper that is neither cited nor changed in the rev is unchecked. The census has no `source`/`.`
  (see below), so it has no such blind path in the current lane.
- `set -n` in a sourced file is accepted silently by `bash -n`; whether it is a defect depends on
  runtime. **[INFERENCE]** POSIX and the bash manual both say `-n` means commands are read but not
  executed; the bash manual says the `.` command "reads and execute[s] commands … in the current
  shell context", and POSIX says the dot utility executes commands "in the current environment".
  A sourced file that runs `set -n` therefore turns off execution for the rest of that shell,
  including the caller's remaining commands: a runtime smoke run can exit 0 having executed nothing
  after that point. `bash -n` cannot see this because it never executes the source. No lane instance
  was found: the census has no `set -n`/`noexec` and no `source`/`.`, and the gate fixtures are
  Python.
- The same non-traversal applies to `eval` (E8: rc 0) and to any runtime-generated code.

Verdict: **holds as a scope limit** (S043's "parse-only" already implies it); it is the sharpest
operability caveat because both a static rc-only check and a runtime smoke test can pass vacuously.

### 4. S043's other negatives, measured

| id | construct | rc | conclusion |
|---|---|---|---|
| E30 | `set -u` then `echo "$never_defined"` | 0 | unset variables are not checked |
| E9 | `echo $((1+))` | 0 | arithmetic is not evaluated |
| E33 | `set -u` then undefined function call | 0 | functions are not resolved |
| E4 / E26 | call before a valid definition | 0 | call order is not a syntax property |
| E24 | NUL byte in the file (`echo ok\0junk`) | 0 | NUL is tolerated |
| E23 | two independent unclosed constructs | 2 | only the first reported error; parsing stops |

This confirms the S043 row's scope cell: `-n` is a parse-only check, not a runtime, unset-variable,
or undefined-function check.

## Documentation grounding (all accessed 2026-10-20; ≤25-word quotes)

1. **GNU Bash 5.3 manual, §4.3.1 The Set Builtin** — live
   `https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html` timed out during this
   recon (same outage S043 records); Wayback capture
   `https://web.archive.org/web/20260930073822/https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html`:
   > “Read commands but do not execute them. This may be used to check a script for syntax errors.”
   (18 words). Relation: this is the exact parse-only rule the probes reproduce; the page says
   nothing about here-document EOF handling, so the warning-only rc 0 is implementation behaviour,
   not a documented error. `-t` on the same page — “Exit after reading and executing one command.”
   (7 words) — shows the read/execute unit is one command, which grounds the runtime asymmetry
   [INFERENCE] above.

2. **POSIX.1-2017 `sh`, `set`** —
   `https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#set` (lines 3279-3280):
   > “The shell shall read commands but does not execute them; this can be used to check for shell
   > script syntax errors.” (21 words). Relation: normative confirmation of parse-only; again no
   here-document EOF semantics. A `bash -n` of the census therefore proves only syntax, never that
   its 20/20, 12/12, and 38/38 runtime results would occur.

3. **GNU Bash manual, §4.1 Bourne Shell Builtins** — live page timed out; Wayback capture
   `https://web.archive.org/web/20261002183420/https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html`:
   > “The `.` command reads and execute commands from the *filename* argument in the current shell
   > context.” (17 words); and for `eval`, “Bash then reads and executes this command” (7 words).
   Relation: sourced/eval text is parsed only when executed, matching E6/E8; under `-n` neither
   executes, so neither file nor string is parsed.

4. **POSIX.1-2017 dot utility**, same page (lines 2447-2452):
   > “The shell shall execute commands from the *file* in the current environment.” (12 words).
   Relation: supports the [INFERENCE] that a `set -n` executed inside a sourced file disables the
   caller's remaining commands (the sourced file runs in the caller's environment).

5. **GNU Bash manual, §3.1.1 Shell Operation** — live page timed out; Wayback capture
   `https://web.archive.org/web/20261015175550/https://www.gnu.org/software/bash/manual/html_node/Shell-Operation.html`:
   > “The following is a brief description of the shell’s operation when it reads and executes a
   > command.” (17 words). Relation: the cycle is described per command, which is why a runtime exit
   can leave a later malformed function unparsed while `bash -n` still sees it [INFERENCE].

## Relation to `tools/souji-census.sh` at HEAD

Observed on the exact HEAD blob (`b8442e2e…`, sha256 `64a60fd0…`; worktree identical):

- `bash -n tools/souji-census.sh` → **rc 0, stderr empty** (run against the worktree file; its blob
  `b8442e2e…` is identical at the opening HEAD `a6ec7810`, the moved HEAD `163158a7`, and `0a70bef`,
  so the result applies to all three). The census parses cleanly at HEAD.
- The census contains **no `bash -n` invocation at all** (grep for `bash -n` yields nothing; the
  only `bash` occurrences are the shebang at line 1 and the comment at line 7). It contains no
  `source`/`.` builtin, no `eval`, no `set -n`/`noexec`; no here-documents (only here-strings
  `<<<` at lines 221, 324, 1473); no `function` keyword; `set -euo pipefail` at line 139. Its first
  top-level call to a shell function is `run_selftest` at line 1858 (dispatch; `guard_path` at 1865),
  after every function definition; the only earlier top-level commands are assignments,
  `set`/`unset`/`export`, and external-command substitutions (plus one `while` loop), none of which
  calls a shell function, so the undefined-function blind spot (E4) is not exercised.
- Therefore none of the three limits weakens the census's *own* execution: there is no unparsed
  code path (no source/eval), no here-doc to truncate, and the one missing-`fi` risk is exactly
  what `bash -n` catches. The census's operability evidence remains the executed matrix
  (changed 20/20, r14 namespace 12/12, legacy selftest 38/38), not its parse status.
- The three limits do bound the **claims others make about the census**:
  - `bash -n` rc 0 at r15-baseline was **not** the case: b410186 is rc 2 at line 1368 (missing
    `fi` in `list_repos`, lines 1324-1335; see Finding 2). HEAD's repair (lines 1271-1272) is what
    makes the rc-0 claim true. This is the construct the assignment names, and the real instance
    confirms both the detection and the diagnostic location.
  - The landing gate's `check_bash` (`tools/souji-landing-gate.py:192-210`; `bash -n` at line 202;
    any-stderr rule at 208-209) is the gate's only `bash -n` consumer, and it is stricter than a
    rc check: a truncated here-doc yields a finding there even though rc is 0. Fixture case 4
    (`tests/fixtures/r16-landing-gate.py:267-278`) pins that rule. The gate's remaining blind spots
    are the sourced/eval/`set -n` class (Finding 3) and boundary-aligned truncation (Finding 1);
    neither is present in the census.
  - The C1 matrix records `bash_n.rc` and the first two stderr lines but prints/compares only the
    rc (`census/round-16/run-matrix.py:110-111`, line 124). In
    `census/round-16/c1-matrix-final.json`, changed/pre-harm/r14-harm have `rc 0, stderr []`, and
    r15-baseline has `rc 2` with the line-1368 syntax error. For the current four arms this is
    harmless, but the metric would call a here-doc-truncated arm clean. **Smallest fix:** in
    `run-matrix.py` after line 111, treat non-empty `err` as a parse failure (mirror
    `check_bash`'s rc-0-but-stderr finding), or rename the reported field to `bash -n rc` so the
    C1 claim is not confused with the gate's stricter `bash -n` semantics.
- Dialect caveat: the gate parses every cited `.sh` with `bash -n` regardless of shebang. The
  census is `#!/usr/bin/env bash` (line 1), so it is unaffected; a cited `#!/bin/sh` script using
  non-bash syntax could be rejected (or bash-only syntax accepted but fail under dash). No current
  instance in this lane's cited set.

## Verdict

- S043 **holds** on all three constructs. The only practical divergence is that an unterminated
  here-document is a warning with rc 0, so "bash -n clean" is false as a *quality* statement if
  measured by rc alone; the landing gate's any-stderr rule is the correct closure, and the C1
  matrix's rc-only record is the weaker claim.
- Missing `fi` in a function defined after use is reliably detected (rc 2), independent of call
  order and reachability; the r15 baseline b410186 is a real instance, and HEAD is clean.
- `set -n` in a sourced file is outside `bash -n` (the file is never opened) and can silently
  no-op a runtime smoke test [INFERENCE]; the census has no such path.
- For `tools/souji-census.sh` at HEAD, operability is unaffected: parse-clean, no dynamic code
  paths, and the one static-check-relevant defect class is fixed. Confidence: high on observed rc
  and stderr (bash 5.3.20, primary docs); the runtime `set -n` and early-exit consequences are
  inference and labelled.

## Remaining unknowns

- Runtime caller-suppression by a sourced `set -n`, and the early-exit-before-definition case, were
  not executed (probe rule: only `bash -n`). They are inferred from the POSIX/bash manual text
  above; the static facts (file never opened; rc 0; no diagnostic) are measured.
- Live gnu.org pages timed out during this recon; the quotes are from Wayback captures whose
  content matches the installed `bash(1)` text as recorded by S043. Bash source-level confirmation
  (`parse_and_execute`/`reader_loop` noexec handling) was attempted via the Debian sources and
  GitHub mirrors; the raw endpoints returned 404, so the verdict rests on docs + probes.

STATUS: ok

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n "S043" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
grep -n 'bash -n\|BASH_ENV\|noexec\|shellcheck\|py_compile\|syntax' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tools/souji-census.sh | wc -l; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-census.sh
grep -n 'S043\|here-document\|heredoc\|set -n\|sourced' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md
grep -n 'bash\|/bin/sh\|GIT_CONFIG\|GIT_NO_LAZY\|set -[a-z]*n\|\.sh' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n '^[a-zA-Z_][a-zA-Z0-9_]*()' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
t(){ n=$1; s=$2; o=$(printf '%b' "$s" | bash -n 2>&1); r=$?; printf '%s|rc=%d|%s\n' "$n" "$r" "$o"; }
t E1-unterminated-heredoc 'cat <<EOF\nhello\n'
t E2-missing-fi-top 'if true; then\necho x\n'
t E3-missing-fi-fn-defined 'main\nmain() {\n  if true; then\n    echo hi\n}\n'
t E4-call-before-def 'main\nmain() { echo hi; }\n'
t E5-unterminated-heredoc-in-fn 'f() {\ncat <<EOF\nin body\n}\nf\n'
t E6-source-missing-file '. /nonexistent/nope-xyz.sh\n'
t E7-source-word-missing 'source /nonexistent/nope-xyz.sh\n'
t E8-eval-syntax 'eval "if true; then"\n'
t E9-arith 'echo $((1+))\n'
t E10-set-n-in-file 'set -n\necho after\n'
t(){ n=$1; s=$2; o=$(printf '%b' "$s" | bash -n 2>&1); r=$?; printf '%s|rc=%d|%s\n' "$n" "$r" "$o"; }
t E11-truncated-in-heredoc 'echo ok\ncat <<EOF\ntruncated body\n'
t E12-heredoc-warning-terminated 'cat <<EOF\nx\nEOF\n'
t E13-heredoc-delim-quoted-missing "cat <<'EOF'\nx\n"
t E14-missing-fi-in-heredoc 'if true; then\ncat <<EOF\nfi\n'
t E15-fi-inside-heredoc-terminated 'if true; then\ncat <<EOF\nfi\nEOF\nfi\n'
t E16-missing-done-loop 'for i in 1 2; do\necho $i\n'
t E17-set-n-sourced 'set -n\n. ./does-not-exist.sh\necho after\n'
t E18-bash-env-probe 'echo body\n'
printf 'E19-BASH_ENV-nonexistent|'; o=$(BASH_ENV=/nonexistent/be.sh bash -n -c 'true' 2>&1); r=$?; printf 'rc=%d|%s\n' "$r" "$o"
printf 'E20-BASH_ENV-nonexistent-stdin|'; o=$(printf 'true\n' | BASH_ENV=/nonexistent/be.sh bash -n 2>&1); r=$?; printf 'rc=%d|%s\n' "$r" "$o"
printf 'E21-ENV-nonexistent-stdin|'; o=$(printf 'true\n' | ENV=/nonexistent/en.sh bash -n 2>&1); r=$?; printf 'rc=%d|%s\n' "$r" "$o"
grep -n 'bash\|parse\|compile\|syntax' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py
grep -n 'bash -n\|shellcheck\|py_compile\|bash' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py
f=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; o=$(bash -n "$f" 2>&1); echo "HEAD census bash-n rc=$? stderr=${o:-<empty>}"; grep -nE '(^|[;&|()][[:space:]]*)(source|\.)([[:space:]]|$)' "$f" || echo "no source/dot builtin"; grep -nE '(^|[;&|()][[:space:]]*)eval([[:space:]]|$)' "$f" || echo "no eval"; grep -nE 'set [+-][a-zA-Z]*n|noexec' "$f" || echo "no set -n/noexec"
grep -n 'heredoc\|here-doc\|EOF\|warning' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py | head -40
bash --version | sed -n '1p'; t(){ n=$1; s=$2; o=$(printf '%b' "$s" | bash -n 2>&1); r=$?; printf '%s|rc=%d|%s\n' "$n" "$r" "$o"; }
t E22-set-n-plus-missing-fi 'set -n\nif true; then\necho x\n'
t E23-two-errors 'if true; then\necho a\nfor x in y; do\necho b\n'
t E24-nul-byte 'echo ok\0junk\n'
t E25-fi-inside-terminated-heredoc 'if true; then\ncat <<EOF\nfi\nEOF\n'
t E26-call-before-def-valid 'main\nmain() { if true; then echo hi; fi; }\n'
t E27-unreachable-bad-branch 'if false; then\nif true; then\necho x\nfi\n'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | nl -ba | awk 'NR>=1350 && NR<=1372'; echo '--- callers of that function name ---'; git show b410186:tools/souji-census.sh | grep -n 'emit_compare\|load_census\|field_at' | head -20
t(){ n=$1; s=$2; o=$(printf '%b' "$s" | bash -n 2>&1); r=$?; printf '%s|rc=%d|%s\n' "$n" "$r" "$o"; }
t H1-terminator-trailing-space 'cat <<EOF\nbody\nEOF \n'
t H2-terminator-leading-tab 'cat <<EOF\nbody\n\tEOF\n'
t H3-dash-terminator-tab 'cat <<-EOF\n\tbody\n\tEOF\n'
t H4-heredoc-in-cmdsubst 'x=$(cat <<EOF\nbody\nEOF\n)\n'
t H5-unterminated-in-cmdsubst 'x=$(cat <<EOF\nbody\n'
t H6-fi-before-brace-missing-eof 'f() {\n  if true; then\n    echo x\n'
t H7-two-functions-second-broken 'a() { echo a; }\nb() {\n  if true; then\n    echo b\n}\na\nb\n'
t H8-crlf-terminator 'cat <<EOF\r\nbody\r\nEOF\r\n'
f=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; echo "heredocs:"; grep -n '<<' "$f" || echo none; echo "function-keyword:"; grep -n '^function ' "$f" || echo none; echo "file-bash-n:"; printf 'cat <<EOF\nx\n' > /dev/null 2>&1; bash -n <(printf 'cat <<EOF\nx\n') 2>&1; echo "procsub rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | bash -n 2>&1 | head -5; echo "r15-baseline bash-n rc=${PIPESTATUS[1]}"
grep -n 'souji-census' /home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md | head -12
curl -s -o /dev/null -w 'evalstring-data-http=%{http_code}\n' https://sources.debian.org/data/main/b/bash/5.3-4/evalstring.c; curl -s https://sources.debian.org/data/main/b/bash/5.3-4/evalstring.c | grep -n 'noexec' | head -5; echo "pipe done"
t(){ n=$1; s=$2; o=$(printf '%b' "$s" | bash -n 2>&1); r=$?; printf '%s|rc=%d|%s\n' "$n" "$r" "$o"; }
t E30-unset-var 'set -u\necho "$never_defined"\n'
t E31-missing-fi-after-exit 'exit 0\nf() {\n  if true; then\n    echo hi\n}\n'
t E32-valid-source-line '. ./lib.sh\necho ok\n'
t E33-undefined-fn-with-set-u 'set -u\nnot_a_function 2>/dev/null\n'
t E34-missing-fi-in-subshell '( if true; then echo x; )\n'
t E35-missing-fi-one-line 'f() { if true; then echo x; }\nf\n'
f=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; grep -n 'set -euo pipefail' "$f"; grep -n '<<<' "$f"; grep -n 'bash -n' "$f" || echo 'no bash -n in census'; sed -n '134,146p' "$f"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | nl -ba | awk 'NR>=1325 && NR<=1350'; echo '--- HEAD list_repos ---'; nl -ba tools/souji-census.sh | awk 'NR>=1257 && NR<=1272'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | nl -ba | awk 'NR>=1308 && NR<=1338'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def check_bash\|"bash", "-n"\|if err:\|def parse_script\|path.endswith\|LG-PARSE-REG' tools/souji-landing-gate.py; echo '--- matrix ---'; grep -n 'bash", "-n"\|bash_n' census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -4; echo '--- ancestry ---'; git merge-base --is-ancestor 163158a7 HEAD && echo '163158a7-ancestor-of-HEAD'; git rev-parse HEAD; git diff --stat a6ec7810 HEAD -- tools/souji-census.sh tools/souji-landing-gate.py | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | awk 'NR==1324 || NR==1334 || NR==1335 || NR==1368' | cat -A | cut -c1-100; echo '--- HEAD 1271-1272 ---'; awk 'NR==1271 || NR==1272' tools/souji-census.sh | cat -A
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^# --- main\|run_selftest; fi\|^emit_census\|^  emit_compare\|guard_path root' tools/souji-census.sh; nl -ba tools/souji-census.sh | awk 'NR>=1854 && NR<=1868'
f=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; echo '--- broad source/dot ---'; grep -nE '(^|[^[:alnum:]_./-])(source|\.)([[:space:]]|$)' "$f" || echo 'none'; echo '--- broad eval ---'; grep -nE '(^|[^[:alnum:]_])eval([[:space:]]|$)' "$f" || echo 'none'; echo '--- noexec ---'; grep -n 'noexec' "$f" || echo 'none'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse 0a70bef:tools/souji-census.sh a6ec7810:tools/souji-census.sh 163158a7:tools/souji-census.sh; git hash-object tools/souji-census.sh tools/souji-landing-gate.py; git rev-parse 163158a7:tools/souji-landing-gate.py
f=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ScoutBashNLimits.md; wc -l "$f"; grep -n '^STATUS:' "$f"; tail -c 40 "$f" | cat -A; echo; stat -c '%s bytes' "$f"
```
