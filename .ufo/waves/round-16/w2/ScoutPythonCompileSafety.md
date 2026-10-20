# Scout — Python `compile()` safety (execution, limits, memory, warnings)

Round 16, wave 2 (FALSIFY). Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`,
HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`. Recon only: nothing was installed,
no lane file was modified except this report, and no command outside the probe rule ran.

Question: does Python `compile()` execute code (including `__future__` imports and
encoding declarations), and what do its recursion, memory and warning behaviours mean
for the one lane call site, related back to `tools/souji-census.sh` at HEAD?

## Verdict table

| Axis | Verdict | What decides it |
|---|---|---|
| Executes source code / imports | **holds** | `compile()` returns a code object; only `exec()`/`eval()` run it (S1) |
| `__future__` statement | **holds** | compile-time directive, no import, no user code (S7) |
| Encoding declaration | **holds** | bytes are decoded per PEP 263 first/second line; no code runs (S6) |
| Recursion / nesting limits | **holds** | bounded by lexer `MAXLEVEL` and parser `MAXSTACK` → `SyntaxError` or `MemoryError`, both caught (S8–S11) |
| Memory | **partial** | documented `MemoryError`/`OverflowError` are caught, but the blob read before `compile()` is unbounded (S1) |
| Warnings | **FAILS** | ambient `PYTHONWARNINGS`/`-W error` can turn a `SyntaxWarning` into a `SyntaxError` finding; the gate does not pin warning state (S2, S3, S4) |
| Caller flags inherited | **holds now, latent** | `dont_inherit` defaults to false; gate has no `from __future__` today (S1) |
| Audit hook | **holds, host caveat** | `compile` audit event; a host hook may abort or run host code (S1, S12) |

Each source is cited with URL, a quote of at most 25 words, and access date 2026-10-20.
Documentation fetched is Python 3.15.0 (S050's document); CPython source is the 3.14 branch;
the host interpreter is Python 3.14 per `corpus/SOURCES.md` row S050.

## Sources

S1. <https://docs.python.org/3/library/functions.html#compile> (accessed 2026-10-20).
    - "Compile the source into a code or AST object. Code objects can be executed by exec() or eval()."
    - "including a source containing a null character or that cannot be decoded"
    - "MemoryError or RecursionError if source is too complex to parse or compile, for example an expression with many thousands of nested operators"
    - "OverflowError if source is too large"
    - "Raises an auditing event compile with arguments source and filename."
    - "The filename argument should give the file from which the code was read"
    - "the code is compiled with the same flags that affect the code that is calling compile()"
    - "The optional argument module specifies the module name."

S2. <https://docs.python.org/3/library/warnings.html#warning-filter> (accessed 2026-10-20).
    - SyntaxWarning: "typically emitted when compiling Python source code, and hence may not be suppressed by runtime filters"
    - action `error`: "turn matching warnings into exceptions"
    - "The warnings filter is initialized by -W options passed to the Python interpreter command line and the PYTHONWARNINGS environment variable."

S3. <https://docs.python.org/3/whatsnew/3.12.html> (accessed 2026-10-20).
    - "A backslash-character pair that is not a valid escape sequence now generates a SyntaxWarning, instead of DeprecationWarning."
    - Same section: "In a future Python version, SyntaxError will eventually be raised, instead of SyntaxWarning."

S4. CPython 3.14 `Parser/tokenizer/helpers.c` (accessed 2026-10-20).
    - `_PyTokenizer_warn_invalid_escape_sequence` calls `PyErr_WarnExplicitObject(PyExc_SyntaxWarning, ...)`
      (line 149) and on error: "Replace the SyntaxWarning exception with a SyntaxError to get a more accurate error report" (lines 153–162).
    - `_PyTokenizer_parser_warn` (lines 220–247) returns 0 when `!tok->report_warnings`, and on a warning
      raised as an exception clears it and calls `_PyTokenizer_syntaxerror`.
    - `_PyTokenizer_check_coding_spec` (line 456): "Check whether the line contains a coding spec."

S5. <https://docs.python.org/3/reference/lexical_analysis.html#encoding-declarations> (accessed 2026-10-20).
    - "If no encoding declaration is found, the default encoding is UTF-8."
    - "this comment is processed as an encoding declaration"

S6. <https://peps.python.org/pep-0263/> (accessed 2026-10-20).
    - "If the encoding is unknown to Python, an error is raised during compilation."

S7. <https://docs.python.org/3/reference/simple_stmts.html#future-statements> (accessed 2026-10-20).
    - "A future statement is recognized and treated specially at compile time"

S8. CPython 3.14 `Parser/lexer/lexer.c` (accessed 2026-10-20).
    - line 1260: `if (tok->level >= MAXLEVEL)` → `_PyTokenizer_syntaxerror(tok, "too many nested parentheses")`
    - lines 539–541: `if (tok->indent+1 >= MAXINDENT) { tok->done = E_TOODEEP; }`

S9. CPython 3.14 `Parser/parser.c` (accessed 2026-10-20).
    - lines 11–18: `#define MAXSTACK 6000` in the default build (4000 in one debug-build variant, 1000 under
  `Py_DEBUG`)
    - line 985: `if (p->level++ == MAXSTACK || _Py_ReachedRecursionLimitWithMargin(PyThreadState_Get(), 1))`

S10. CPython 3.14 `Parser/pegen_errors.c` (accessed 2026-10-20), lines 409–414:
    - `_Pypegen_stack_overflow` sets `PyExc_MemoryError`, `"Parser stack overflowed - Python source too complex to parse"`.

S11. <https://docs.python.org/3/library/ast.html#ast.parse> (accessed 2026-10-20).
    - "It is possible to crash the Python interpreter with a sufficiently large/complex string"
    - "due to stack depth limitations in Python’s AST compiler."
    - "successfully parsing source code into an AST object doesn’t guarantee that the source code provided is valid Python code"
    - `ast.parse` on a null character raises `ValueError`, not the `SyntaxError` `compile()` raises (S1).

S12. <https://docs.python.org/3/library/sys.html#sys.addaudithook> (accessed 2026-10-20).
    - "Hooks can then log the event, raise an exception to abort the operation, or terminate the process entirely."

## The only `compile()` call site in the lane at HEAD

`grep -rn "compile(" tools/souji-landing-gate.py tools/souji-census.sh` finds one built-in call:
`tools/souji-landing-gate.py:216`. (The `re.compile(` occurrences in the same file are regex
compilation, a different API.) A follow-up scan of the named lane Python tools — the five `tools/*.py`
gates, `tests/fixtures/r16-landing-gate.py`, `census/round-16/run-matrix.py`, and the two r15
fixture/regenerator scripts — found no other built-in `compile(` call (only comments mention it).

- `parse_script` (lines 223–231) dispatch: `.sh` → `check_bash`, everything else (`.py`) → `check_python`.
- `check_python` (lines 213–221) is exactly:
  ```
  def check_python(path, content):
      """compile() only — never executes. Return detail on failure, else None."""
      try:
          compile(content, path, "exec")
      except (SyntaxError, ValueError) as exc:
          return "%s: %s" % (type(exc).__name__, str(exc).splitlines()[0][:200])
      except Exception as exc:  # e.g. TypeError on undecodable bytes
          return "%s: %s" % (type(exc).__name__, exc)
  ```
- `content` is **bytes**: `blob_at_path` (lines 150–159) returns `subprocess.run([... "cat-file", "blob", ...]).stdout`.
  So the PEP 263 bytes path is the live one, not the `str` path.
- `path` is only passed as `filename` (diagnostic attribution); per S1 the filename is not read.
- Scope: cited registry scripts matching `CITED_PATH_RE` (lines 58–60, `tools|tests/fixtures|census/round-<n>`),
  plus `.py`/`.sh` files changed in `BASE..REV` when `--base` is supplied (lines 553–566). Without `--base`,
  only `SKILL.md`-cited scripts are compile-checked.

## Axis detail

### 1. Does `compile()` execute code? — holds (no)

- S1 is explicit: the object is *executed by* `exec()`/`eval()`; `compile()` itself only produces it.
- `__future__` is not an import at compile time: S7 calls it a compile-time directive; it changes compiler
  flags/code generation only. No `__import__`, no attribute lookup, no user callable is reachable from the
  compiler for a source string.
- Encoding declarations are consumed by the tokenizer to *decode* bytes (S4 `check_coding_spec`, S5); decoding
  runs no source code.
- The filename is not opened (S1: it "should give the file from which the code was read"; it is metadata for
  diagnostics). The gate already read the bytes from git, so no second read exists.
- The lane call site contains no `exec`, `eval`, `importlib` or `__import__`; the only `re.compile(` instances
  are regex compilation, a different API.
- The precise statement is therefore: **no audited source executes**; `compile()` can still run *host-installed*
  code — an audit hook on the `compile` event (S1, S12) and a replaced `warnings.showwarning`. The gate
  installs neither.

Verdict: **holds**.

### 2. Recursion / nesting limits — holds, bounded and caught

Documented outcomes for over-complex source are `MemoryError` or `RecursionError` (S1). CPython 3.14 does not
recurse until the C stack dies on ordinary deep nesting; it trips explicit guards first:

- lexer: `MAXLEVEL` → `SyntaxError: too many nested parentheses` (S8); indentation depth `MAXINDENT` → `E_TOODEEP`
  (also a `SyntaxError` family error);
- parser: `MAXSTACK 6000` and `_Py_ReachedRecursionLimitWithMargin` (S9) → `_Pypegen_stack_overflow`, which is
  **`MemoryError`** with text `"Parser stack overflowed - Python source too complex to parse"` (S10).

The gate catches `SyntaxError` explicitly (line 217) and every other documented class — `MemoryError`,
`RecursionError` (a `RuntimeError`), `OverflowError` (an `ArithmeticError`), and a promoted `SyntaxWarning`
(an `Exception`) — through `except Exception` (line 219). So for compile-to-code, the parser limits degrade to a
finding, not a crash. The one documented crash path that remains is the warning at S11: a sufficiently
large/complex string can crash the interpreter through AST-compiler stack depth. That warning is attached to
`ast.parse`, and the 3.14 parser guards above are the mitigation; reaching it through `compile()` is
**[INFERENCE] unlikely in 3.14 and untested here** (probe rule forbids executing crafted inputs).

Note for calibration: the gate's use of `compile()` rather than `ast.parse()` is materially correct. S11 says a
successful AST parse does not imply the source compiles, and gives the example `return 42`: a valid Return node
that cannot be compiled alone. `compile()` rejects a module-level return; the held-out fixture exercises exactly
that shape with `tools/returns.py` (`"x = 1\nreturn 0\n"`), expecting `LG-PARSE-REG` (fixture lines 258–265).

Verdict: **holds**.

### 3. Memory — partial

- S1 names `MemoryError`/`RecursionError` for over-complex source and `OverflowError` for too-large source;
  all are caught by the gate (above).
- But the gate buffers the whole blob before compiling: `blob_at_path` returns complete `stdout` bytes
  (lines 150–159), then `compile()` builds a decoded string, AST and code object. Peak memory is a multiple of
  the blob, with no size cap anywhere in `parse_script`/`check_python`.
- On lane-sized scripts (largest audited file: the 1005-line gate itself) this is irrelevant. If the gate were
  ever pointed at a multi-hundred-MB blob, the documented outcome is `MemoryError` (reported as a parse finding,
  which is misleading but not wrong: such a file cannot be imported either). Whether Linux kills the process
  for OOM before CPython's allocation fails is **[INFERENCE]**, not documented.
- The blast radius is bounded by git: only blobs already committed in the lane are read, and the gate never
  fetches (its git calls are local `cat-file`/`ls-tree`/`diff`).

Verdict: **partial** — safe for the lane's own scripts, would need a size cap for untrusted blobs.

Smallest fix (only if the gate is ever pointed outside the lane): in `check_python`, before `compile()`, refuse
oversized input, e.g. `if len(content) > 16 * 1024 * 1024: return "source-too-large: %d bytes" % len(content)`.
Advisory; not required at r16.

### 4. Warnings — FAILS (documented environment input changes the verdict)

This is the one substantive counterexample against the gate's calibration:

1. `SyntaxWarning` is emitted *while compiling* (S2), and the `error` action turns matching warnings into
   exceptions (S2). The filter table is initialized from `-W`/`PYTHONWARNINGS` (S2).
2. On the warning-as-error path, CPython's tokenizer **converts the warning into `SyntaxError`** — quote from
   S4: "Replace the SyntaxWarning exception with a SyntaxError to get a more accurate error report"; the
   generic `_PyTokenizer_parser_warn` does the same.
3. The gate does not touch warnings state: `grep -c "warnings\|PYTHONWARNINGS"` over
   `tools/souji-landing-gate.py` is **0**. The fixture's `Gate.run` also inherits the environment
   (`subprocess.run(...)` without `env=`, `tests/fixtures/r16-landing-gate.py:154`).

Concrete case (mechanism grounded; **not executed** under the probe rule): a cited `tools/x.py` containing a
non-raw regex such as `PATTERN = re.compile("\d+")`.
- Default filters: S3 makes `"\d"` a `SyntaxWarning`; it is printed to stderr and `compile()` succeeds → no finding.
- `PYTHONWARNINGS=error` (or `-W error`): the same bytes raise `SyntaxError: "\d" is an invalid escape sequence`
  via S4 → `check_python` returns a detail → `LG-PARSE-REG`/`LG-PARSE-CHANGED` finding.

So the same commit can be clean or failing depending only on the caller's environment. At this HEAD no current
audited file triggers it: a non-raw `\d`/`\s`/`\w` scan over the three `.py` files changed at HEAD
(`tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py`, `tools/souji-seat-audit.py`) found none
(grep exit 1), and the fixture has no warning case at all. The defect is latent, not currently red.

Verdict: **fails** the "same bytes → same verdict" property under a documented environment variable.

Smallest fixes, in order of risk:
1. Pin the environment in the invocation contract: run the gate with `PYTHONWARNINGS=` cleared (or
   `-W default`), and say so in the CLI docs/lesson replay command. Zero code change, no false-negative risk.
2. In `check_python`, `import warnings` and wrap the call:
   `with warnings.catch_warnings(): warnings.simplefilter("ignore"); compile(...)`.
   S2's caveat ("may not be suppressed by runtime filters") means this must be verified on the host before it is
   claimed; a filter installed before the call is expected to apply to `PyErr_WarnExplicitObject`, but that is
   **[INFERENCE]** until run.

Do not "fix" this by catching `Warning` and returning clean: a promoted warning aborts the compile, so later
syntax errors in the same file would never be seen — that would trade a false positive for a false negative.

### 5. Encoding declarations — holds; one wrong comment

- `compile(bytes)` decodes per PEP 263: a `coding[=:]` comment on line 1 or 2 selects the codec, otherwise
  UTF-8 (S4, S5, S6); a UTF-8 BOM is ignored rather than an error (S5).
- Unknown codec → "an error is raised during compilation" (S6); undecodable bytes and null characters →
  `SyntaxError` (S1). The gate's first `except` catches both.
- The `str`-source variant is not used: `content` is always git blob bytes.
- **Defect (minor, comment only):** `tools/souji-landing-gate.py:219` says
  `# e.g. TypeError on undecodable bytes`. Undecodable bytes raise `SyntaxError` (S1's own quoted sentence
  says "cannot be decoded" under `SyntaxError`), and `TypeError` is raised only for a source that is neither
  `str`, `bytes` nor an AST — impossible here. The broad `except Exception` is still justified, but for the
  resource classes: `MemoryError`/`RecursionError`/`OverflowError` (S1) and a promoted `SyntaxWarning` (S4).

Smallest fix: replace that comment with
`# e.g. MemoryError/RecursionError/OverflowError for over-complex input`.

### 6. Caller-flag inheritance — holds now, latent

S1: with `flags=0` and `dont_inherit=False` (the call's defaults), "the code is compiled with the same flags
that affect the code that is calling compile()". The gate has no `from __future__` import
(`grep -c "^from __future__"` = 0), so today the check is a clean default-grammar parse. If a future import
is ever added to the gate (e.g. `annotations`), every audited `.py` would silently be compiled under it,
which can hide a real "this file only works with the future flag" difference.

Verdict: **holds now, latent**.

Smallest fix: `compile(content, path, "exec", dont_inherit=True)` — the audited file's own
`from __future__` lines are still honoured (they are part of its source), while the gate's own flags stop
leaking in.

### 7. Audit hook — holds, host caveat

S1: `compile()` raises the `compile` audit event with `source` and `filename`; S12: a hook may "abort the
operation" by raising. The gate adds no hook and installs no `sitecustomize`, so under a stock interpreter
nothing here executes. A host that installs a raising hook would make every Python parse check fail (caught
as an arbitrary exception, reported with the hook's type) — honest failure, environment-dependent, not a lane
defect. No action.

## Relation to `tools/souji-census.sh` at HEAD

- Bytes confirmed identical to the wave statement: `sha256sum tools/souji-census.sh` =
  `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`; `bash -n` exits 0.
- The census contains **no Python at all**: `grep -n "python\|py_" tools/souji-census.sh` exits 1 with no
  output. `compile()` therefore has no role in C1; S050 cannot ground any census claim, and every statement
  about census parsing rests on S043 (`bash -n`) alone.
- The landing gate reaches `tools/souji-census.sh` through `check_bash` (`.sh` branch, lines 190–210), i.e.
  `bash -n` in a `/var/tmp` snapshot. The r15 replay finding `LG-PARSE-REG tools/souji-census.sh` is S043's
  mechanism, not `compile()`.
- The compile path *does* reach census Python support scripts when they are `SKILL.md`-cited
  (`CITED_PATH_RE`, lines 58–60, admits `census/round-<n>/…py`; `SKILL.md` cites e.g.
  `census/round-13/run-verification.py` line 216 and `census/round-14/cache-demonstration.py` line 220) or when
  `--base` makes them "changed". The `.py` files changed in `HEAD~1..HEAD` are
  `tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py`, `tools/souji-seat-audit.py`.
- Consequence for calibration: the warnings-environment finding cannot make the census red. It can make a
  `.py` evidence script red only under a non-default warning filter, and no current lane file triggers it.
  Separately, without `--base` the gate never sees uncited changed `.py` files; the r15 replay command in
  `corpus/lessons/round-16.md:21` omits `--base`, so only the cited census shell script was parse-checked there.
  If L1 wants changed-Python coverage on the landing, the replay should carry `--base <baseline>` (the CLI already
  supports it and the fixture covers the id).

## Observed vs inference vs gaps

Observed (file/line or source above):
- one `compile()` call site; bytes input; no `warnings`/`__future__` in the gate;
- documented exception classes and CPython's `SyntaxWarning`→`SyntaxError` conversion path;
- parser/lexer limits and the `MemoryError` stack-overflow handler;
- census has no Python and parses under `bash -n`;
- fixture covers module-level `return` but no warning/encoding/resource-limit case.

Inference (not executed, probe rule):
- the `PYTHONWARNINGS=error` counterexample's exact end-to-end gate output (the pieces are documented and read
  in CPython source, but no crafted run was made);
- that `warnings.simplefilter("ignore")` suppresses the compile-time warning on this host;
- OOM-killer vs `MemoryError` ordering for a huge blob;
- reachability of the S11 interpreter-crash path through `compile()` in 3.14.

Gaps / not answered here:
- Whether the host's `python3` is exactly 3.14.0 or another 3.14.x patch (SOURCES S050 says 3.14; no interpreter
  probe was run).
- The numeric `MAXLEVEL` value (definition not located in the files fetched; the guard and its message are
  confirmed at S8, the constant's value is not).
- Constant folding of literal expressions inside `compile()` was not verified against CPython source in this
  pass (`Python/ast_opt.c` fetch returned no match for the patterns tried); it remains **[INFERENCE]** that it
  is compiler-internal and never runs user code.

## Tooling

No installs or upgrades. Nothing was written outside this report and no temporary directory was created.

STATUS: ok

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; grep -n "S050\|S043\|compile()" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
grep -rn "compile(" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh 2>&1; echo ---; grep -n "compile\|ast\|py_compile" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py
grep -n "check_python\|py_compile\|read_bytes\|read_text\|compile_check\|def .*python\|\.py\b" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py | head -60
grep -n "def blob_at_path" -A 25 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py; echo ===; grep -n "python\|py_" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh | head; echo ===; grep -n "warnings\|PYTHONWARNINGS\|-W " /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py
grep -n "S050\|compile" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md | head -30; echo ===; grep -n "null\|\\x00\|escape\|Warning\|nested\|deep" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py | head -20; echo ===; grep -n "BAD_PY\|GOOD_PY" -A 4 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py | head -30
grep -n "def emit\|LG-PARSE\|print(\|stdout" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py | head -25
grep -n "\.py\b\|python3 tools\|run-matrix" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md | head -20; echo ===; grep -n "CITED\|cites\|registry" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py | head -20
grep -n "os.environ\|sys.executable\|subprocess.run" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py | head -20; echo ===; grep -n "module-level return\|return\b" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh tools/souji-landing-gate.py && bash -n tools/souji-census.sh && echo "bash-n-rc=$?"
grep -n "coding\|x00\|null\|deep\|Warning\|nested" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py | head -15; echo ===; grep -n "python\|PYTHON" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py | head -15
grep -n "\.py\b" /home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md | head -20; echo ===; git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --name-only --diff-filter=AM a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae~1 a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae 2>/dev/null | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def check_python" -A 10 tools/souji-landing-gate.py; echo ===; grep -cn "^from __future__\|^import warnings\|warnings\." tools/souji-landing-gate.py; echo ===; grep -n "python\|py_" tools/souji-census.sh; echo "census-python-grep-rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nP '(?<!r)"[^"]*\\[dDsSwW.]' tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py tools/souji-seat-audit.py; echo "nonraw-escape-rc=$?"; echo ===; grep -n "return 42\|return 1\b" tests/fixtures/r16-landing-gate.py | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "module-level\|MODULE\|^BAD\|^GOOD\|top_level\|return" tests/fixtures/r16-landing-gate.py | head -25
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nP '(?<![.\w])compile\(' tools/souji-cert-evidence.py tools/souji-evidence-cache.py tools/souji-preservation-evidence.py tools/souji-seat-audit.py tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py census/round-16/run-matrix.py tests/fixtures/r15-census-config.py tests/fixtures/r15-preservation-frozen/regenerate.py; echo "builtin-compile-rc=$?"
```
