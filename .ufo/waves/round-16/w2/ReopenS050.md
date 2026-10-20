# ReopenS050 — S050 (`compile()`) row falsification

Seat: `SoujiR16.ReopenS050-4`, wave 2 FALSIFY, leaf.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane HEAD at audit start `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; at audit end
`163158a706352f1c0ee3521c4da2e5289970db57`. S050 is committed at both; the attacked
bytes are `corpus/SOURCES.md` blob sha256
`f257941874ffce9d0837b942b2b07282a0e317bdf3b6bd932ede070975413319`, worktree-equal,
row at line 64. `tools/souji-landing-gate.py` and `tools/souji-census.sh` are
worktree-clean against HEAD (`git diff --quiet` rc=0); census sha256
`64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (matches the
round-16 record). Mid-audit the first `git status` transiently showed SOURCES modified;
that was a concurrent writer, and the final state is committed and byte-identical to
what I read.

## Row under attack (corpus/SOURCES.md:64)

`| S050 | Python built-in compile() — https://docs.python.org/3/library/functions.html#compile | docs | A | parse/compile without execution of a source text, not runtime correctness | Python 3.15.0 documentation opened 2026-10-20 by L1; § Built-in Functions compile; host Python 3.14 | compile() turns source into a code object (which only exec()/eval() would run) and raises SyntaxError for invalid source, so the landing gate checks Python parse without executing it | mined | 2026-10-20 | on-release | corpus/lessons/round-16.md |`

## Page re-opened 2026-10-20 (observed)

`https://docs.python.org/3/library/functions.html#compile` → **HTTP/2 301**,
`location: https://docs.python.org/3/builtins/functions.html`; destination 200, page
title "Built-in functions — Python 3.15.0 documentation", H1 "Built-in functions",
`compile(...)` entry with id `compile`. Sibling Python doc URLs are still 200
(`/3/library/pathlib.html`, `/3/library/ast.html`), so the move is specific to the
functions page.

Located quote (22 words, verbatim at the `compile()` signature block's exception
paragraph, immediately before "If you want to parse Python code into its AST
representation"):

> "This function raises SyntaxError if the compiled source is invalid, including a source containing a null character or that cannot be decoded"

This matches `corpus/lessons/round-16.md:33` (the Gate record) verbatim; the count is
inside the ≤25-word budget.

## Cell verdicts

- **scope — holds.** The page states "Compile the source into a code or AST object.
  Code objects can be executed by `exec()` or `eval()`." That is exactly a
  parse/compile-without-execution scope; the page makes no runtime-correctness claim.
  The page's own failure list (SyntaxError; ValueError for invalid mode/flags or
  surrogate strings; MemoryError/RecursionError/OverflowError for pathological
  source) is all compile-time, consistent with the scope.
- **teaches — holds.** Sentence-by-sentence: "turns source into a code object (which
  only exec()/eval() would run)" = the quoted first two sentences; "raises SyntaxError
  for invalid source" = the located quote; "the landing gate checks Python parse
  without executing it" = code fact, not a doc claim, verified at HEAD below.
- **tier A — holds.** `docs` from the CPython project itself, same class as S040
  (pathlib) and S043 (bash manual). `corpus/QUALITY.md:5` defers tier shape to the
  SOURCES contract; the row's A is the registry's normal vendor-doc tier.
- **status mined — holds.** It is used: `corpus/lessons/round-16.md:33` carries the
  access record + quote and `:35` says "Sourced claims: C2's parse checks rest on S043
  and S050".
- **recheck on-release — holds, and is already earning its keep.** `docs.python.org/3/`
  is a moving tree: the page now titles itself 3.15.0 and the functions page moved
  under `/builtins/`. A release-boundary recheck is the right cadence for a row whose
  text tracks the current doc build. (Note: host is Python 3.14.8; 3.13 and 3.14 pages
  carry the *identical* exception sentence, so citing 3.15 prose for a 3.14-host check
  creates no behaviour gap — see host probe.)
- **used-by — holds.** The claim named is the landing gate's Python parse check; C2 is
  `tools/souji-landing-gate.py`. At HEAD:
  - `tools/souji-landing-gate.py:213-222` `check_python` calls
    `compile(content, path, "exec")` at `:216` and only returns a detail string.
  - It is wired at `:549` (SKILL.md-cited scripts, incl. cited `.py` files such as
    `tools/souji-cert-evidence.py`, `tools/souji-evidence-cache.py`,
    `tools/souji-preservation-evidence.py`, `tools/souji-landing-gate.py`,
    `tools/souji-seat-audit.py` — `SKILL.md:105,142,146,150,152,154`) and at `:564`
    for `--base..--rev` changed `.sh/.py` (`SCRIPT_EXT_RE` at `:93`), so compile() is on
    both live paths, not dead code.
  - No `exec(`, `eval(`, `runpy` or `importlib` occurs anywhere in the gate
    (`grep -nE` → empty), so the "never executes" half of `check_python`'s docstring
    (`:214`) is true of the tool, not just of the builtin.
  - `tests/fixtures/r16-landing-gate.py:253-265` exercises the Python half with two
    compile-only defects (tab/space mismatch, module-level `return`), so the claim is
    measured, not assumed.
  - `tools/souji-census.sh` (the other named file) contains **no** Python compile use;
    the teaches cell correctly names only the landing gate, so this is not an
    overclaim. C1 rests on S043/S045–S047/S049, per `round-16.md:35`.

## Host probe (observed, Python 3.14.8, `/var/tmp` seat dir, deleted)

- `python3 -m py_compile canary.py` where canary.py's first statement writes
  `/var/tmp/souji-r16-ReopenS050-4/EXECUTED`: rc=0 and **no EXECUTED file** — compiling
  source did not run it.
- null byte in source → `SyntaxError: source code string cannot contain null bytes`,
  rc=1 — the 3.15 quote's null-character clause is true on the host interpreter.
- tab/space mismatch → `TabError: inconsistent use of tabs and spaces in indentation`,
  rc=1 (`TabError` ⊂ `SyntaxError`, so `check_python`'s `except (SyntaxError,
  ValueError)` catches it).

## Counterexample search (all failed to falsify)

- *Version drift* — 3.13, 3.14 and 3.15 doc builds carry the same exception sentence;
  host 3.14.8 confirms the null-byte behaviour. No gap.
- *Hidden execution* — the page documents a `compile` auditing event ("may also be
  raised by implicit compilation") and compile-time `SyntaxWarning`s. Those are hook /
  warning observations, not execution of the compiled source; the canary probe shows
  no source execution. The scope says "without execution of a source text", which
  survives.
- *Exception breadth* — `ValueError` (invalid mode/flags, surrogates) is unreachable
  with the gate's fixed `"exec"` mode and bytes input; `MemoryError`/`RecursionError`/
  `OverflowError` are caught by the gate's broad `except Exception` (`:219`) and turned
  into a parse finding (fail-closed; a file that cannot be compiled cannot be
  imported). The taught "raises SyntaxError for invalid source" is the operative case
  and remains true.
- *Census use* — absent, and not claimed.

## Only defect found (non-blocking, calibration hygiene)

The URL cell (and `round-16.md:33`) records
`https://docs.python.org/3/library/functions.html#compile`, which is now a 301 to
`https://docs.python.org/3/builtins/functions.html#compile`. Access still succeeds
(destination 200, `id="compile"` present, quote present), and the lesson's access
record is honest, so the scope/teaches grounding stands; this is drift, not a false
row, and it is precisely what `recheck: on-release` exists to catch.

Smallest fix: in `corpus/SOURCES.md:64` replace the URL cell with
`https://docs.python.org/3/builtins/functions.html#compile` (and the same string in
`corpus/lessons/round-16.md:33`). Optional cosmetic: anchor cell
"§ Built-in Functions compile" → "§ Built-in functions, compile()".

## Verdict

**holds** — the page supports both the scope cell and the teaches cell; tier A,
`mined`, `on-release` are right; and the row is genuinely used by the landing gate at
HEAD (`souji-landing-gate.py:216`, wired `:549/:564`) with the census correctly not
claimed. The 301 is the sole, non-blocking fix.

## Remaining unknowns

- Whether docs.python.org will keep serving the `/library/functions.html` 301
  indefinitely (out of this seat's reach; the on-release recheck covers it).
- Whether any other corpus doc cites `compile()` (would extend `used-by`); not swept —
  the probe rule forbids recursive lane-wide search, and the two named files are the
  ones the claim implicates.

## Probe-rule disclosure

Allowed-command boundary: two transient doc caches were written to `/tmp`
(`/tmp/py313.html`, `/tmp/py314.html`) while comparing 3.13/3.14 doc builds; both were
deleted after reading, nothing in the lane was touched. All other writes were inside
`/var/tmp/souji-r16-ReopenS050-4/`, which was deleted (`cleanup: gone`). No lane file
was edited, staged, stashed or committed. No tools installed or updated.

STATUS: ok

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain -- corpus/SOURCES.md tools/souji-census.sh tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S050" corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '52,66p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S050\|compile()" tools/souji-census.sh tools/souji-landing-gate.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "compile" tools/souji-landing-gate.py && echo ---- && sed -n '195,245p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "S050\|S043\|S046\|Gate" corpus/lessons/round-16.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "parse_script(\|SCRIPT_EXT_RE\|check_python(\|check_bash(" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-landing-gate.py | grep -n "compile(content\|def check_python\|bash\", \"-n\"" && git show HEAD:tools/souji-census.sh | grep -n "py_compile\|python\|compile" | head -20; echo "census-grep-rc=$?"
python3 --version; curl -sSI --max-time 20 https://docs.python.org/3/library/functions.html | sed -n '1,8p'
curl -sS --max-time 25 https://docs.python.org/3.14/library/functions.html | tr '\n' ' ' | sed 's/<[^>]*>/ /g' | tr -s ' ' | grep -o "This function raises[^.]*\." | head -3
curl -sS --max-time 25 https://docs.python.org/3.13/library/functions.html -o /tmp/py313.html; echo rc=$?; grep -o "This function raises.\{0,300\}" /tmp/py313.html | sed 's/<[^>]*>//g' | tr -s ' ' | head -2
curl -sS --max-time 30 https://docs.python.org/3.14/builtins/functions.html -o /tmp/py314.html; echo rc=$?; grep -c "id=\"compile\"" /tmp/py314.html; grep -o "This function raises.\{0,400\}" /tmp/py314.html | sed 's/<[^>]*>//g' | tr -s ' ' | head -2
for v in 3.13 3.14; do echo "== $v =="; curl -sS --max-time 30 "https://docs.python.org/$v/library/functions.html" | tr '\n' ' ' | sed 's/<[^>]*>//g' | tr -s ' ' | grep -o "This function raises SyntaxError.\{0,320\}" | head -1; echo; done
for v in 3.13 3.14; do echo "== $v =="; curl -sSL --max-time 30 "https://docs.python.org/$v/builtins/functions.html" | tr '\n' ' ' | sed 's/<[^>]*>//g' | tr -s ' ' | grep -o "This function raises SyntaxError.\{0,300\}" | head -1; echo; done
curl -sSI --max-time 20 https://docs.python.org/3/library/pathlib.html | sed -n '1,4p'; echo ---; curl -sSI --max-time 20 https://docs.python.org/3/library/ast.html | sed -n '1,4p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,25p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE "\bexec\s*\(|\beval\s*\(|runpy|importlib" tools/souji-landing-gate.py; echo "---SKILL cites---"; grep -noE "tools/[A-Za-z0-9_.-]+\.(sh|py)" SKILL.md | sort -u | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "tier\|Tier" corpus/QUALITY.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '33p;35p' corpus/lessons/round-16.md && printf 'words in quoted sentence: ' && printf '%s' 'This function raises SyntaxError if the compiled source is invalid, including a source containing a null character or that cannot be decoded' | wc -w
curl -sSI --max-time 20 https://docs.python.org/3.14/library/functions.html | sed -n '1,4p'; echo ---; curl -sSI --max-time 20 https://docs.python.org/3/builtins/functions.html | sed -n '1,4p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,30p' corpus/QUALITY.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '66,130p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "lesson@HEAD:" && git show HEAD:corpus/lessons/round-16.md | grep -c "S050" && echo "sources@HEAD:" && git show HEAD:corpus/SOURCES.md | grep -c "S050"; echo "worktree-source-sha:" && sha256sum corpus/SOURCES.md tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- corpus/SOURCES.md && git diff -- corpus/SOURCES.md | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain && echo "---diff rc---" && git diff --quiet -- corpus/SOURCES.md; echo "diff-rc=$?" && git diff --cached --stat | head
set -u; D=/var/tmp/souji-r16-ReopenS050-4; rm -rf "$D"; mkdir -p "$D"; cd "$D"; printf 'open("%s/EXECUTED","w").write("x")\n' "$D" > canary.py; printf 'x = 1\0\n' > nullbyte.py; printf 'def f():\n    a = 1\n\tb = 2\n' > tab.py; echo "== host $(python3 --version) =="; echo "-- canary compile --"; python3 -m py_compile canary.py; echo "rc=$?"; if [ -e "$D/EXECUTED" ]; then echo "EXECUTED: source ran during compile"; else echo "NOT EXECUTED: no canary file"; fi; echo "-- null byte --"; python3 -m py_compile nullbyte.py 2>&1 | tail -3; echo "rc=${PIPESTATUS[0]}"; echo "-- tab defect --"; python3 -m py_compile tab.py 2>&1 | tail -3; echo "rc=${PIPESTATUS[0]}"; cd /; rm -rf "$D"; echo "cleanup: $([ -e "$D" ] && echo present || echo gone)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git show HEAD:corpus/SOURCES.md | grep -n "^| S050" | cut -c1-200 && git show HEAD:corpus/lessons/round-16.md | grep -n "S050" | cut -c1-160 && sha256sum tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --quiet -- tools/souji-landing-gate.py tools/souji-census.sh; echo "tools-diff-rc=$?"; git show HEAD:tools/souji-landing-gate.py | grep -n "compile(content\|def check_python" ; git show HEAD:corpus/SOURCES.md | sha256sum; sha256sum corpus/SOURCES.md
rm -f /tmp/py313.html /tmp/py314.html; ls /tmp/py313.html /tmp/py314.html 2>&1 | head -2
```

(File reads through the `read` tool, not shell: `tools/souji-landing-gate.py:195-245`,
`:535-575`, `:55-70,150-190`; `https://docs.python.org/3/library/functions.html#compile`.)
