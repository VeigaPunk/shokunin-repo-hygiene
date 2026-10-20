# SrcPythonAst — round-16 source scout

**Verdict: ADMIT one new row (tier A, docs, status `queued`), grounded on the served Python 3.15.0 `ast`
page.** Proposed id **S043**; L1 must renumber (see "Id" below). `corpus/SOURCES.md` was not edited.

Axes named: **coverage** — one primary language-reference page that grounds C2's `.py` parse check, opened
with a same-day served stamp and a fetched-copy hash; **calibration** — the page does *not* literally say
"raises SyntaxError" or "does not execute"; the row states which half is quoted where, and the gate gets a
measured exception surface rather than a one-word claim.

## Open record

| field | value |
|---|---|
| URL | https://docs.python.org/3/library/ast.html (canonical identical) |
| access date | 2026-10-20 |
| served title | `ast — Abstract syntax trees — Python 3.15.0 documentation` |
| served version | Python **3.15.0** documentation (the `/3/` build, not the host's 3.14) |
| last-updated line | `Last updated on Oct 20, 2026 (13:43 UTC).` (fetched copy line 3328) |
| fetched copy | `/tmp/ast315.html`, 362,029 bytes, sha256 `b037b88afd30578f6f9b577c8d9ef6fd344daef7a4bd1375bde12f05e6ce34ce` |
| cross-ref page | https://docs.python.org/3/library/functions.html — same build, `Last updated on Oct 20, 2026 (13:43 UTC).` (line 2735), 330,313 bytes, sha256 `0ee70223b39c189561fbbdc53c62bb8af14394bac9b39d568b622ca4f6f6684f` |
| host interpreter | `Python 3.14.8` |
| version delta | the ast page records `Added in version 3.15: Added the module parameter` — the gate must not pass `module=` on the host |

The fetched copies were removed after hashing; the sha256 pins the bytes as served at access time, not a
stable document identity (a rebuild changes the footer stamp and therefore the hash).

## Located quotes (verbatim, with page locus)

All from the fetched copy at the sha256 above; line numbers are of that copy, the registry anchor uses
section names (builds reflow lines).

**ast page, § ast.parse**
1. `Parse the source into an AST node. Equivalent to compile(source, filename, mode, flags=FLAGS_VALUE, optimize=optimize, module=module), where FLAGS_VALUE is ast.PyCF_ONLY_AST if optimize <= 0 and ast.PyCF_OPTIMIZED_AST otherwise.` (lines 2680–2683)
2. `If source contains a null character (\0), ValueError is raised.` (line 2705)
3. `Note that successfully parsing source code into an AST object doesn’t guarantee that the source code provided is valid Python code that can be executed as the compilation step can raise further SyntaxError exceptions.` (lines 2708–2711)
4. `In particular, ast.parse() won’t do any scoping checks, which the compilation step does.` (lines 2714–2715)
5. `It is possible to crash the Python interpreter with a sufficiently large/complex string due to stack depth limitations in Python’s AST compiler.` (lines 2719–2721)

**ast page, § ast.PyCF_ONLY_AST**
6. `Generates and returns an abstract syntax tree instead of returning a compiled code object.` (lines 3038–3039)

**functions page, § compile**
7. `Compile the source into a code or AST object. Code objects can be executed by exec() or eval().` (lines 589–590)
8. `This function raises SyntaxError if the compiled source is invalid, including a source containing a null character or that cannot be decoded; ValueError if mode or flags is invalid, or if a string source contains surrogate characters; MemoryError or RecursionError if source is too complex to parse or compile, for example an expression with many thousands of nested operators; and OverflowError if source is too large.` (lines 626–633)
9. `If you want to parse Python code into its AST representation, see ast.parse().` (lines 634–635)

## What is grounded, and what is not

- **Grounded literally:** `ast.parse` returns a tree of AST objects built as `compile(..., PyCF_ONLY_AST)`;
  `PyCF_ONLY_AST` returns "an abstract syntax tree instead of … a compiled code object"; parse does no
  scoping checks; success does **not** guarantee the source is compilable or executable; a NUL character
  raises `ValueError`; a sufficiently large/complex string can crash the interpreter.
- **Not literal on the ast page:** the sentence *"raises SyntaxError"* never appears for `ast.parse`. The
  explicit raise table is `compile()`'s (quote 8), reachable only through the documented equivalence (quote 1)
  and the compile page's own cross-link back to `ast.parse` (quote 9). The row must attribute it that way.
- **"Does not execute" is a contract inference, not a quote:** quote 6 says no code object is returned and
  quote 7 says only code objects are executed by `exec()`/`eval()`. `[INFERENCE]` No documented execution
  step exists in the parse call. The docs never write "does not execute". This should be carried as
  inference in the lesson and converted to measurement by the gate fixture (see finding G5).
- **NUL divergence (calibration trap):** ast says NUL → `ValueError` (quote 2); compile says invalid
  source *including* a NUL → `SyntaxError` (quote 8). A gate with `except SyntaxError` only — the shape in
  `census/round-14/cache-demonstration.py:305-307` — would let a NUL-bearing `.py` escape as a traceback
  instead of a red `LG-PARSE-REG` row.
- **Audit event:** `functions.html` says `compile` raises an auditing event; the ast page has zero
  occurrences of "auditing" (`grep -c` → 0). `ast.parse`'s audit behaviour is undocumented on its page;
  immaterial for the gate (no audit hook) and recorded only as an unknown.

## Gate contract this row serves (observed)

`.ufo/waves/round-16/w1-spec.json` item `LandingGate` (prompt): the gate "never executes repository code
(only `bash -n FILE` and Python ast.parse)" and `LG-PARSE-REG` requires that every `.py` cited in `SKILL.md`
and matching `(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.py` "must ast.parse";
`LG-PARSE-CHANGED` applies the same parse to `BASE..REV` changes.

`tools/souji-landing-gate.py` does not exist at HEAD `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (`ls` →
"cannot access"); the above is the dispatch contract, not executed evidence. The r15 analogue for the
underlying defect is `corpus/lessons/round-15-verifier-spotcheck.md:7` ("does not parse") and the parse
checks at `:9`, `:47`, `:55`.

`LG-PARSE-REG` will scan at least these `.py` paths cited in `SKILL.md` (grep at lines 14, 104, 141–150,
210, 214, 221): `tools/souji-cert-evidence.py`, `tools/souji-evidence-cache.py`,
`tools/souji-preservation-evidence.py`, `tests/fixtures/r13-cert-evidence.py`,
`tests/fixtures/r14-evidence-cache.py`, `tests/fixtures/r14-census-boundary.py`,
`tests/fixtures/r15-census-config.py`, `tests/fixtures/r15-preservation-evidence.py`,
`census/round-13/run-verification.py`, `census/round-14/cache-demonstration.py`.
`round-15-verifier-spotcheck.md:47,:55` records `ast.parse` rc 0 for three of them
(`r15-census-config.py`, `tools/souji-preservation-evidence.py`, `tests/fixtures/r15-preservation-evidence.py`)
plus `census/round-15/run-verification.py`, which is not in this list; the remaining seven are unmeasured here.

## Proposed row (existing column shape)

Insert after `corpus/SOURCES.md:54` (S042); line 54 is the last registry row, line 55 blank, `## Paths` at
line 56. Proposed text, cell-for-cell:

| S043 | Python 3.15.0 documentation, `ast` — Abstract syntax trees (`ast.parse`) — https://docs.python.org/3/library/ast.html | docs | A | `ast.parse` as a parse-only `.py` check: returns an AST, never a code object, does no scoping checks, and raises `SyntaxError` for invalid source via the documented `compile()` equivalence and `ValueError` on a NUL character; a successful parse does not prove the file compiles or runs | § ast.parse (ast helpers), § ast.PyCF_ONLY_AST; cross-ref § compile in Built-in Functions (same 3.15.0 build, `If you want to parse Python code into its AST representation, see ast.parse().`); title `ast — Abstract syntax trees — Python 3.15.0 documentation`, served 2026-10-20, footer `Last updated on Oct 20, 2026 (13:43 UTC)`; fetched-copy sha256 `b037b88a…`; host `Python 3.14.8` (3.15 added `module=`) | parsing builds an AST and no code object, so a parse check runs no repository code; it checks grammar only (no scoping checks) and raises `SyntaxError` for invalid source, `ValueError` on NUL; parse success is not compilability | queued | 2026-10-20 | on-release | — |

- **Tier A** — official CPython language reference, primary for the language's own parser contract; the
  installed interpreter is the same implementation family, and the page carries a served version and
  last-updated stamp (Q1).
- **status `queued`, not `mined`** — no committed artifact cites it yet at draft time; a `used-by` naming a
  file that does not exist would repeat the r15 frozen-pin defect. Promotion rule: `mined` when
  `corpus/lessons/round-16.md` (Gate) and `tools/souji-landing-gate.py` both cite it; then set
  `used-by = corpus/lessons/round-16.md`.
- **recheck `on-release`** — same convention as the other docs.python.org row S040.
- **used-by `—`** — target named in the promotion rule above.
- **Rejected alternative:** a second row for `compile()`'s raise table. It would be document inflation (the
  r15 verdict rejected splitting one document's subsections into four rows); the compile sentence is the
  raise table *for the same call* the ast page declares `ast.parse` equivalent to, so it is carried as an
  anchor inside this one row.

**Id:** the registry's next free id really is S043 (`S042` is the max; r15's draft S043–S047 were never
registered — `round-15-verifier-spotcheck.md:80-82` rejects S043–S046 as separate rows and defers S047).
All nine r16 source drafts were told to start at S043, so this number will collide; L1 should renumber in
dispatch order. The row's content is independent of the id.

## Findings for the gate implementer (advisory; L1 integrates)

- **G1 — catch surface.** Catch `SyntaxError` **and** `ValueError` (NUL, quote 2), plus a decode error from
  reading (a `UnicodeDecodeError` is a `ValueError`). Quote 8 additionally documents `MemoryError`,
  `RecursionError`, `OverflowError` for the compile path; `[INFERENCE]` `ast.parse` propagates them, since the
  ast page documents neither. Simplest total form: `except (SyntaxError, ValueError, MemoryError,
  RecursionError, OverflowError)` around the parse, mapping every catch to `LG-PARSE-REG`.
- **G2 — read strictly.** The r14 precedent reads text as UTF-8
  (`census/round-14/quality-proposal.json:451`: `open(p, encoding="utf-8").read()`). A non-UTF-8 `.py`
  raises before `ast.parse`; a gate that catches only parse errors exits with a traceback instead of a
  finding. Read bytes and decode with an explicit failure → red row.
- **G3 — size bound.** Quote 5 says the interpreter can *crash*, not merely raise, on a sufficiently
  large/complex string; no `except` clause covers that. Bound the file size or record a bounded skip, and
  say so in the gate's output.
- **G4 — host version.** Do not pass `module=` (3.15-only); default `mode='exec'`, `optimize=-1` and
  `feature_version=None` are the documented defaults and suffice.
- **G5 — prove non-execution by fixture, not by doc.** `tests/fixtures/r16-landing-gate.py` (owned by
  `LandingGateFixture`) should cite, in a synthetic `SKILL.md` world, a side-effecting `.py` whose module
  body writes a marker, then assert the marker is absent after the `--rev` run. This turns the
  `[INFERENCE]` in "does not execute" into measured evidence and directly discharges the gate's
  "never executes repository code" claim.
- **G6 — scope honesty.** The parse check proves *parses*, not *compiles* and not *runs* (quotes 3–4). Gate
  text and the round lesson should not upgrade `LG-PARSE-REG` into an operability proof; the r15 defect it
  catches was exactly "does not parse".

## Remaining unknowns

- `ast.parse`'s raise surface for `MemoryError`/`RecursionError`/`OverflowError` is not documented on the ast
  page; only `compile()`'s table names them — inheritance unverified (no parse executed in this seat).
- `UnicodeDecodeError` is a `ValueError` subclass (`[INFERENCE]` from the exception hierarchy; not quoted
  here) — worth one assertion in the gate's selftest.
- The 3.15.0 doc build can change after 2026-10-20; the sha256 + last-updated line are the recheck handle,
  and `recheck: on-release` is the registry signal.
- Python 3.14's ast documentation was not opened; only the 3.15 delta (`module=` added) is grounded from
  this page.
- No `ast.parse` execution in this seat (probe rule); behavior claims are documentation-only except the
  lane's own precedent at `census/round-14/cache-demonstration.py:305-312`, which catches `SyntaxError` and
  then separately calls `compile()` — i.e. the lane already treats parsing and execution as two steps.

## Commands

```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/tools/ 2>&1 | head -40; echo ---; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/ 2>&1 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "ast.parse\|py_compile\|SyntaxError" tools/*.py census/round-16/*.py 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tools/ | grep -iE 'landing|gate|census' ; echo '--- round16:'; ls census/round-16/ 2>&1; echo '--- git:'; git -C . rev-parse HEAD; git -C . status --porcelain tools/ census/round-16/ | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "py\b\|\.py\|parse\|ast\." census/round-16/run-matrix.py | head -40; echo '--- cert:'; sed -n '220,250p' tools/cand-s16-cert.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' census/round-16/run-matrix.py; echo '...'; wc -l census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "parse\|SyntaxError\|registry" corpus/lessons/round-15-verifier-spotcheck.md | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/ 2>&1; echo '--- w1:'; ls .ufo/waves/round-16/w1/ 2>&1 | head -40; echo '--- gate mentions:'; grep -rln "souji-landing-gate" .ufo/waves/round-16/ corpus/ 2>/dev/null | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh > /tmp/r15census.sh 2>/dev/null; wc -l /tmp/r15census.sh; python3 --version; git rev-parse --short=7 b410186 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 2>/dev/null; sed -n '40,60p' corpus/lessons/round-15-verifier-spotcheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,p+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,p+f'[{i}]')
    else:
        s=str(o)
        if 'landing-gate' in s or 'parse' in s.lower():
            print(p, '=>', s[:600])
EOF
cd /tmp && curl -fsS https://docs.python.org/3/library/ast.html -o /tmp/ast315.html && grep -n "execut\|PyCF_ONLY_AST\|SyntaxError" /tmp/ast315.html | sed 's/<[^>]*>//g' | head -40; echo '--- last updated:'; grep -o "Last updated on [^<]*" /tmp/ast315.html | head -3; grep -o 'This page is licensed[^<]*' /tmp/ast315.html | head -1
cd /tmp && sed -n '3034,3060p' /tmp/ast315.html | sed 's/<[^>]*>//g'; echo '======'; sed -n '2678,2720p' /tmp/ast315.html | sed 's/<[^>]*>//g'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'));print(json.dumps(d,indent=1)[:3000])"
cd /tmp && curl -fsS https://docs.python.org/3/library/functions.html -o /tmp/fn315.html && python3 - <<'EOF'
import re,html
s=open('/tmp/fn315.html',encoding='utf-8').read()
i=s.find('id="compile"')
seg=s[i:i+9000]
txt=re.sub(r'<[^>]+>','',seg)
print(html.unescape(txt)[:3000])
EOF
echo '--- last updated:'; grep -o "Last updated on [^<]*" /tmp/fn315.html | head -1; grep -o "<title>[^<]*" /tmp/fn315.html
cd /tmp && curl -fsSL https://docs.python.org/3/library/functions.html -o /tmp/fn315.html && grep -o "Last updated on [^<]*" /tmp/fn315.html | head -1; grep -o "<title>[^<]*" /tmp/fn315.html; python3 - <<'EOF'
import re,html
s=open('/tmp/fn315.html',encoding='utf-8').read()
i=s.find('id="compile"')
seg=s[i:i+12000]
txt=html.unescape(re.sub(r'<[^>]+>','',seg))
print(re.sub(r'\n{3,}','\n\n',txt)[:2600])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "S043\|S044\|S045\|S046\|S047" corpus/ census/round-15/ .ufo/waves/round-16/ 2>/dev/null | head -20; echo '--- max S:'; grep -o "S0[0-9][0-9]" corpus/SOURCES.md | sort -u | tail -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
tasks=d.get('tasks') or d.get('items') or []
print(type(tasks), len(tasks) if hasattr(tasks,'__len__') else '')
def prompts(o):
    out=[]
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='prompt' and isinstance(v,str): out.append(v)
            else: out.extend(prompts(v))
    elif isinstance(o,list):
        for v in o: out.extend(prompts(v))
    return out
ps=prompts(d)
print('prompts:',len(ps))
for p in ps:
    m=re.findall(r'S0\d\d',p)
    if m: print('NUM', sorted(set(m)), p.splitlines()[0][:80], '||', [l for l in p.splitlines() if re.search(r'S0\d\d',l)][:3])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-landing-gate.py 2>&1; python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d:
    p=it.get('prompt','') if isinstance(it,dict) else ''
    if 'landing' in p.lower() or 'GateSpec' in str(it.get('name','')):
        print('===',it.get('name'),'\n',p[:1500],'\n')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "ast.parse\|py_compile" corpus/lessons/round-14*.md corpus/lessons/round-15*.md census/round-1*/ 2>/dev/null | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "tier\|admi\|Tier A\|primary" corpus/QUALITY.md | head -30; echo '--- shape:'; grep -n "^| id |" corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '18,40p' census/round-14/cache-demonstration.py; echo '---305:'; sed -n '298,318p' census/round-14/cache-demonstration.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^| S04[0-2]" corpus/SOURCES.md; echo '--- table end:'; grep -n "^## Paths\|^$" corpus/SOURCES.md | sed -n '1,12p'; echo '--- QUALITY 1-28:'; sed -n '1,28p' corpus/QUALITY.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "SOURCES-CONTRACT" corpus/ PROTOCOL.md 2>/dev/null | head; echo '---'; ls corpus/ | head -20; echo '--- tier defs:'; grep -n "Tier A\|tier A\|^| A" corpus/*.md | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i,it in enumerate(d):
    if isinstance(it,dict):
        n=it.get('name') or it.get('id') or list(it)[:2]
        print(i, n)
print('keys of first dict:', list(d[0]))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
t=d['tasks']
print(list(d))
for i,it in enumerate(t):
    print(i, {k:v for k,v in it.items() if k!='prompt'})
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(list(d))
t=d.get('items')
print(type(t), len(t) if t else 0)
if isinstance(t,list):
    for i,it in enumerate(t):
        if isinstance(it,dict):
            print(i, it.get('name') or it.get('id') or it.get('role'), '|', (it.get('prompt') or '')[:60].replace('\n',' '))
        else:
            print(i, type(it), str(it)[:80])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    if it.get('name') in ('LandingGate','LandingGateFixture'):
        print('#####',it['name'],'#####')
        print(it['prompt'])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
it=[x for x in d['items'] if x.get('name')=='LandingGate'][0]
p=it['prompt']
i=p.find('OWN ONLY')
print(p[i:])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
it=[x for x in d['items'] if x.get('name')=='LandingGate'][0]
p=it['prompt']
print('len',len(p)); print(repr(p[-200:]))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
p=[x for x in d['items'] if x.get('name')=='LandingGate'][0]['prompt']
i=p.find('LG-PARSE-CHANGED')
print(p[i:])
EOF
cd /tmp && python3 - <<'EOF'
import re,html
s=open('/tmp/fn315.html',encoding='utf-8').read()
t=html.unescape(re.sub(r'<[^>]+>','',s))
i=t.find('This function raises')
print(re.sub(r'\s+',' ',t[i:i+600]))
EOF
cd /tmp && python3 - <<'EOF'
import re,html
s=open('/tmp/fn315.html',encoding='utf-8').read()
t=html.unescape(re.sub(r'<[^>]+>','',s))
i=t.find('Raises an auditing event compile')
print(re.sub(r'\s+',' ',t[i:i+500]))
EOF
sha256sum /tmp/ast315.html /tmp/fn315.html; wc -c /tmp/ast315.html /tmp/fn315.html
cd /tmp && grep -c "auditing" /tmp/ast315.html; python3 - <<'EOF'
import re,html
s=open('/tmp/ast315.html',encoding='utf-8').read()
t=html.unescape(re.sub(r'<[^>]+>','',s))
i=t.find('It is possible to crash')
print(re.sub(r'\s+',' ',t[i:i+320]))
EOF
cd /tmp && grep -n "null character\|FLAGS_VALUE\|won.t do any scoping\|successfully parsing\|PyCF_ONLY_AST instead\|instead of returning\|Last updated on" /tmp/ast315.html | sed 's/<[^>]*>//g' | head -20; echo '=== functions:'; grep -n "raises SyntaxError if the compiled source\|see ast.parse\|instead of returning" /tmp/fn315.html | sed 's/<[^>]*>//g' | head -10
cd /tmp && sed -n '2706,2716p' /tmp/ast315.html | sed 's/<[^>]*>//g'; echo '=== fns:'; grep -n "SyntaxError if the compiled\|see .*ast.parse\|Last updated on" /tmp/fn315.html | sed 's/<[^>]*>//g' | head
cd /tmp && grep -n "This function raises\|many thousands\|see <a class=\"reference internal\" href=\"ast.html\"\|ast.parse()" /tmp/fn315.html | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.py' SKILL.md | head -20
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/; echo '--- ast 2718-2724:'; sed -n '2718,2724p' /tmp/ast315.html | sed 's/<[^>]*>//g'; echo '--- fns 612-616:'; sed -n '612,616p' /tmp/fn315.html | sed 's/<[^>]*>//g'
cd /tmp && grep -n "Compile the source into a code or AST object\|Code objects can be executed" /tmp/fn315.html | sed 's/<[^>]*>//g'; echo '--- ast 2704-2716 numbered:'; awk 'NR>=2704 && NR<=2716 {printf "%d:%s\n", NR, $0}' /tmp/ast315.html | sed 's/<[^>]*>//g'; echo '--- ast 3036-3040:'; awk 'NR>=3036 && NR<=3040 {printf "%d:%s\n", NR, $0}' /tmp/ast315.html | sed 's/<[^>]*>//g'
cd /tmp && awk 'NR>=626 && NR<=636 {printf "%d:%s\n", NR, $0}' /tmp/fn315.html | sed 's/<[^>]*>//g'; echo '--- fns 589-591:'; awk 'NR>=589 && NR<=591 {printf "%d:%s\n", NR, $0}' /tmp/fn315.html | sed 's/<[^>]*>//g'; echo '--- ast 2679-2684:'; awk 'NR>=2679 && NR<=2684 {printf "%d:%s\n", NR, $0}' /tmp/ast315.html | sed 's/<[^>]*>//g'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain corpus/SOURCES.md; echo "rc=$?"; echo '--- row block:'; sed -n '/## Proposed row/,/^## Findings/p' .ufo/waves/round-16/w1/SrcPythonAst.md | head -30; rm -f /tmp/ast315.html /tmp/fn315.html /tmp/r15census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
p='.ufo/waves/round-16/w1/SrcPythonAst.md'
lines=open(p,encoding='utf-8').read().splitlines()
for n,l in enumerate(lines,1):
    if l.startswith('| S043 |'):
        cells=[c.strip() for c in l.strip().strip('|').split('|')]
        print('line',n,'cells',len(cells))
        for i,c in enumerate(cells,1): print(i,repr(c[:80]))
print('lines',len(lines))
print('ends with Commands fence:', lines[-1]=='```')
EOF
```
