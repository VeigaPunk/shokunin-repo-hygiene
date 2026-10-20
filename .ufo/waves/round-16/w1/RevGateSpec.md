# Round 16 — C2 landing-gate contract review (r15 D1 / R1 / R4 + rounds 13–15 false positives)

Reviewer: SoujiR16.RevGateSpec (leaf). Source inspection only; no execution of
repository code. Target file reviewed: `tools/souji-census.sh` at
`cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (1784 lines, sha256
`fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`,
`bash -n` rc 0, `shellcheck -S warning` rc 0). Contract under review: the shared
Goal's C2 claim plus the LandingGate item (`.ufo/waves/round-16/w1-spec.json`
`items[0].prompt`). `tools/souji-landing-gate.py` does not exist at cbf688a
(`ls` → `No such file or directory`), so this is a contract review: each pinned
check was re-derived statically over committed bytes at the four named revisions.

Method: `git show <rev>:<path>` bytes into `/var/tmp/souji-r16-RevGateSpec/`,
then `bash -n` (`.sh`) or `ast.parse` (`.py`) only; directory removed at the end.
No lane file other than this report was written.

## 1. Would it have caught D1, R1, R4?

| r15 closure finding | caught by the contract? | check | measured evidence at the named revision |
|---|---|---|---|
| **R1** — `tools/souji-census.sh` landed non-parsing | **yes** | `LG-PARSE-REG` (and, with `--base cc21683`, `LG-PARSE-CHANGED`) | SKILL.md at b410186 cites the path at lines 138 and 167; the regex `tools/<name>.(sh|py)` matches. `bash -n` on b410186 bytes: rc 2, line 1368 `unexpected token '}'` — exactly the closure's site. At cbf688a the same check is clean (rc 0). No other cited path fails at any of r13/r14/r15/r16 (10/15/18/18 cited paths checked). |
| **R4** — frozen pin matches no committed revision | **yes at b410186; at cbf688a there are *two* stale pins, not one** | `LG-FROZEN-PIN` | b410186: `tests/fixtures/r15-preservation-frozen/expected.json` pins `tools/souji-census.sh` at `b51873514d1f…`; the committed bytes are `dab4122c997d…` → 1 finding. At cbf688a: the same pin is still `b5187351…` vs `fed43c71…`, **and** the pin for `tests/fixtures/r15-census-config.py` is `6314d45db6be…` while cbf688a's revised fixture is `9151cde8817d…` → 2 findings. R4's text names only the census pin, so a literal R4 fix leaves the gate red. |
| **D1** — seat-reported known failure not carried | **partly: lesson yes, report/LOG/SKILL no** | `LG-SEAT-UNCARRIED` | `.ufo/waves/round-15/w1/ConfigRepair.md` has 3 matching lines (7, 9, 11); `corpus/lessons/round-15.md` contains none of them (its only ConfigRepair sentence, line 94, says the worker was cancelled and calls the file an "unverified candidate"). So the check is red at b410186 — true positive for the lesson half. But the L1 report lives in the **fleet** repo (`.ufo/reports/round-15/souji.md`; the lane has no `.ufo/reports/` at any of the four revisions), and `--root LANE` + `git archive LANE REV` cannot see it. D1's "the report has none either", and R3's "must reach the L1 report and lesson", are outside the check's reach by construction. |

Simulated gate outcome per revision (pinned predicates, findings = `LG-*` rows
the contract would emit; `checked_*` are the counts the `SUMMARY` line needs):

| revision | `--round` | findings | breakdown | exit |
|---|---|---|---|---|
| `a31642d` (r13 end, **admitted true** per `corpus/lessons/round-13-verifier-spotcheck.md:7`) | 13 | 2 | 2 × `LG-SEAT-UNCARRIED`, **both false** | 1 |
| `cc21683` (r14 end) | 14 | 2 | 2 × `LG-SEAT-UNCARRIED`, **both false** | 1 |
| `b410186` (r15 land) | 15 | 5 | 1 parse + 1 pin + 3 seat, **all true** | 1 |
| `cbf688a` (r16 C1 commit) | 16 | **2** | 2 × `LG-FROZEN-PIN`; `checked_markers=0` (no round-16 wave dir is committed here) | **1, not 0** |

So the "red on historical b410186" half of C2 is exact. The "green at round
end" half is not true at cbf688a and cannot be made true by an R4 fix that
touches only the census pin (G5).

## 2. Findings

Severity is about the gate's fitness as a landing gate, not about the r16 claim
alone. Each patch is minimal text for the contract; the implementation does not
exist yet.

### G1 — HIGH — `LG-SEAT-UNCARRIED` free-text alternatives match ordinary prose, code and tables

The predicate is `every line matching` the pinned alternation, applied to every
`*.md` under the round dir. Two of its alternatives are unbounded free text
(`does[ ]NOT[ ]parse` and `\bsyntax[ ]error\b`, case-insensitive), so they match
any mention of the token, not a failure disclosure. Measured false positives:

- `a31642d` `.ufo/waves/round-13/w1/EvidenceConnection.md:165` — a line inside a fenced shell block (a `bash -n` test in a loop, whose echo message contains the bigram). Not a failure.
- `a31642d` `.ufo/waves/round-13/w1/SourceTimeout.md:78` — a table row documenting `timeout(1)` exit 125 (third cell lists causes). Not a failure.
- `cc21683` `.ufo/waves/round-14/w1/CachePrecedent.md:159` — a bullet describing an intentional mutation test ("mutated to broken code: echo …"). Not a failure.
- `cc21683` `.ufo/waves/round-14/w1/CachePrecedent.md:220` — an exit-code table row for the evidence-cache consumer. Not a failure.

The four lines are reproduced verbatim in the fenced block at the end of this
section. Consequence: the gate is red (exit 1) on round 13, which the non-author
closure admitted, and on round 14 — for text that is documentation or test
design. This is a false-positive rate of 4/7 marker lines over r13–r15.

The same mechanism is structural for round 16: reviewer reports in this round
(`RevScanParse`, `RevengeR15Landing`, this file) necessarily quote r15's parse
fault. Under the unmodified contract every such quote becomes an uncarried
marker that `corpus/lessons/round-16.md` must reproduce verbatim.

Patch P1 (replace the marker sentence):

> LG-SEAT-UNCARRIED — for every `*.md` under `.ufo/waves/round-N/` at REV,
> ignore lines inside ``` fences. A marker is a line whose first non-space
> token, after an optional Markdown heading (`#`…`######`) or bullet (`-`/`*`),
> is `STATUS:` followed by `INCOMPLETE|FAIL|FAILED|BLOCKED|BROKEN`
> (case-insensitive). That line, with heading/bullet decoration stripped and
> internal whitespace collapsed, must occur in `corpus/lessons/round-N.md`.
> Free-text alternatives are not markers.

This keeps the r15 detection: `ConfigRepair.md:7` is such a heading. It removes
all four measured false positives (none is a status line).

### G2 — HIGH — the carry rule is unsatisfiable for wrapped prose markers

The contract requires the *whole stripped physical line* from the seat file to
appear as a substring of the lesson. `ConfigRepair.md:11` is a wrapped fragment
that begins mid-sentence and ends mid-sentence ("… L1 must either complete the");
`ConfigRepair.md:9` likewise ends with an open parenthesis. A lesson that quotes
the actual sentence fails the substring test; a lesson that copies the fragment
verbatim imports a dangling clause. The only other way to pass is to edit the
seat report after the fact, which is falsification.

Patch P2 (fold into P1): carry at the granularity of the matched marker
(`STATUS:<word>` heading line), not the physical line, or require the seat file's
basename plus the status token. Do not require wrapped prose to be copied.

### G3 — MEDIUM — the L1 report surface D1 names is unreachable from `--root LANE`

Measured: `git ls-tree -r --name-only <rev> -- .ufo/reports/` returns empty at
`a31642d`, `cc21683`, `b410186`, `cbf688a`; the report cited by the closures is
in the fleet repo. `LG-SEAT-UNCARRIED` therefore cannot enforce R3's "the L1
report and lesson". Patch P3:

> add `--report PATH` (optional). When given, every marker must also occur in
> that file. The default stays "no report" and the `SUMMARY` line must report
> `checked_report=0`, so a green run cannot silently claim report coverage.

### G4 — MEDIUM — absent round dir passes (vacuity pinned by the selftest)

The selftest case list pins "no wave dir passes". Combined with the archive
root, this lets a lane omit its wave reports from the landing commit and still
be green; at cbf688a the check is already vacuous (`checked_markers=0`, because
`.ufo/waves/round-16/` is untracked). For a gate whose single purpose is
disclosure enforcement, silence must not pass. Patch P4: when `--round N` is
given and `.ufo/waves/round-N/` contains no `*.md`, exit 2 (could-not-evaluate);
change the selftest case to expect 2.

### G5 — MEDIUM — C2's "green at round end" is false at cbf688a and R4 is under-specified

Measured at cbf688a (`tests/fixtures/r15-preservation-frozen/expected.json`):

| pin | pinned | actual at cbf688a |
|---|---|---|
| `tools/souji-census.sh` | `b51873514d1f…` | `fed43c710b75…` |
| `tests/fixtures/r15-census-config.py` | `6314d45db6be…` | `9151cde8817d…` (revised by C1 in this same commit) |
| `tests/fixtures/r14-census-boundary.py` | `e6a984b1daf1…` | matches |
| `record_sha256` | `4749ad07…` | matches |

`tests/fixtures/r15-preservation-frozen/README.md` already declares the refresh
procedure (record fields first, then `expected.json`/`record_sha256`). Patch P5:
R4 must name **both** payload pins (census and r15-census-config), then
`record.json`'s `fixture.sha256`, `measured_commit`, `runs.changed.tool.*`,
`namespace_controls.tool.*`, then `expected.json`'s `record_sha256`; and C2's
green target must be a revision at or after that refresh plus the r16 lesson,
not `cbf688a`.

### G6 — MEDIUM — `LG-PARSE-REG` is registry-coverage-dependent; uncited breakage is invisible without `--base`

Only paths *cited in SKILL.md* are parsed. The contract even pins a selftest
case asserting "uncited non-parsing script is NOT flagged without --base", and
the allowed C2 runs name three revisions with no `--base`. A new broken helper
that nobody cites lands green. Measured cost of closing it: 144 `.sh`/`.py`
files under `tools/` + `tests/fixtures/` at cbf688a. Patch P6: add
`LG-PARSE-TREE` over that set (same parse predicate), or make `--base` mandatory
for landing runs and keep the tree scan as the no-base fallback.

### G7 — LOW — `LG-PARSE-CHANGED` predicate is ambiguous

"must parse the same way" can be implemented as "parse status unchanged", under
which a file that was broken before and is broken after passes. Patch P7:
"every `.sh`/`.py` with status A or M in `BASE..REV` must be parse-clean at REV;
a path deleted in REV is not checked."

### G8 — LOW — `LG-FROZEN-PIN` leaves two cases undefined

`record` resolution order is not stated (the r15 record is inside the frozen
dir; a root-first implementation breaks it), and `record_sha256` with a missing
or non-file `record` has no outcome. Patch P8: "`record` resolves relative to
the frozen dir; `record_sha256` with no readable `record` at REV is exit 2."

### G9 — LOW — census line 877–879 would abort the whole run and mislabel it `path-protected`

```sh
    tgt=$(expand_config_path "$val" "$wt") \
      || protected_fail "git-config-unsupported" "$wt" "$key"
```

`protected_fail` exits 2 for the whole run with finding `path-protected`. The
C1 claim says only a protected-namespace reach keeps exit 2 and every other
could-not-evaluate config degrades to one `error` row. Today the path is
unreachable in practice, because `scan_config_file` lines 619–624 apply the same
predicate to the same (globally-isolated; `GIT_CONFIG_GLOBAL=/dev/null` at line
143) config and soft-refuse first. It is defensive dead code with the wrong
semantics if the scan ever narrows. Patch P9: use `cfg_soft "git-config-unsupported"; return 1`.

### G10 — INFO — `bash -n` is not "runs", and the contract already says so

The gate proves parse only. The target file is also structurally dispatchable:
`run_selftest` is defined at 1432, the argument loop starts at 1746, `--selftest`
is invoked at 1765, and `emit_census`/`exit 0` are the last statements (1783–1784),
so there is no r15-style unreachable-dispatch hazard. A parse-clean script with a
missing dispatch would still pass; since the contract forbids executing repo code,
the honest boundary is the claim's own wording ("non-parsing registry script"),
which is correct. No patch.

## 3. Checked, no defect found

- `LG-PARSE-REG` at `a31642d`, `cc21683`, `cbf688a`: 0 findings (10/15/18 cited paths). No false positives.
- `LG-MISSING-REG`: 0 findings at all four revisions; every cited path exists.
- `LG-PARSE-CHANGED` over `a31642d..cc21683` (10 scripts), `b410186..cbf688a` (3), `cc21683..cbf688a` (8): 0 false positives; fires exactly on `tools/souji-census.sh` in `cc21683..b410186`.
- `LG-FROZEN-PIN` at `a31642d` (7 pins) and `cc21683` (9 pins): 0 findings. Path resolution "frozen dir first, else root" is exercised correctly by all three fixtures (`r13-cert-frozen` is dir-relative, `r14-cache-frozen` is dir-relative, `r15-preservation-frozen` is root-relative).
- `git archive` distortion: no `.gitattributes` exists at any of the four revisions (measured), so no `export-ignore` file can be dropped from the snapshot.
- Census C1 mechanism vs claim (source inspection): protected reach exits 2 at 1086 (`guard_path`), config-unsupported emits exactly one `error` row at 1088–1092, bound filter drivers skip status for one repo only at 939–943 and 907–934, and `core.hooksPath`/`core.fsmonitor` are overridden on every status at 947–949 with `GIT_NO_LAZY_FETCH=1` at 147. The header at 84–120 states the same contract. One nit only: a worktree record containing a newline/tab/CR refuses the whole run as `ambiguous-path` (1048–1050), which is a path-shaped refusal, not a namespace reach; negligible.

Residual risk: this review could not execute the gate (it does not exist), so the
`SUMMARY` counts above are re-derived from the pinned predicates, not printed by
the tool. Two IDs can fire for one defect at b410186 (`LG-PARSE-REG` and
`LG-PARSE-CHANGED` for the census path); L1 should expect 6 rows for the
`--base cc21683 --round 15` run, not 5.

## 4. Gate-hygiene note for this file

The four historical false-positive lines are quoted verbatim below for evidence.
They are round-13/round-14 files, so no `--round 16` run scans them — but these
quotes are inside *this* file, which a `--round 16` run does scan. Measured with
the pinned predicate, this report contains **6** marker-matching lines: the 4
quotes below plus 2 lines of the `## Commands` block that reproduce the marker
regex itself (lines 307 and 364 of this file). Under the contract **as written**
all 6 are `LG-SEAT-UNCARRIED` findings that `corpus/lessons/round-16.md` would
have to reproduce verbatim. That is the intended demonstration of G1/G2: a gate
whose own contract text and evidence command cannot be green. Patch P1 (skip
fenced blocks, status-anchored markers) makes all 6 exempt. No line of this
report carries a status heading.

```text
a31642d .ufo/waves/round-13/w1/EvidenceConnection.md:165
    bash -n "$L/$fix" || { echo "FAIL Q19: $fix syntax error"; exit 1; }

a31642d .ufo/waves/round-13/w1/SourceTimeout.md:78
| **125** | The `timeout` utility itself failed | Syntax error, unrecognized argument, bad duration |

cc21683 .ufo/waves/round-14/w1/CachePrecedent.md:159
  `tools/probe.sh` is mutated to broken code: `echo "syntax error"; exit 1`.

cc21683 .ufo/waves/round-14/w1/CachePrecedent.md:220
     - `2`: Malformed / could-not-evaluate (syntax error, missing file, symlink, path traversal, non-regular file, protected path).
```

STATUS: review complete — no blocking defect in this deliverable; C2's contract needs P1–P9 applied (G1–G6 are pre-adoption blockers) and cannot be green at cbf688a as written.

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; echo "---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3; echo "---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t cbf688ab2ab28e38103e5a9417ca525b5f2ed423
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/ | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- .ufo/waves/round-16/ | cat; echo "=== round-13 ==="; git ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- .ufo/waves/round-13/ | cat; echo "=== round-14 ==="; git ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- .ufo/waves/round-14/ | cat; echo "=== round-15 ==="; git ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- .ufo/waves/round-15/ | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-landing-gate.py 2>&1; echo "---"; git status --porcelain | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/ .ufo/waves/round-16/w1/ 2>&1 | cat; echo "=== census/round-16 ==="; ls -la census/round-16/ | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && cat corpus/lessons/round-15-verifier-spotcheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,p+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,p+f'[{i}]')
    else:
        if isinstance(o,str) and ('landing' in o.lower() or 'LandingGate' in str(p)):
            print(p,'=',o[:3000]); print('---')
walk(d)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l; echo "---"; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
it=[i for i in d['items'] if i.get('name')=='LandingGate'][0]
print(it['prompt'])
print('=== OWNED/keys ===', list(it.keys()))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
it=[i for i in d['items'] if i.get('name')=='LandingGate'][0]
open('/var/tmp/lg-item.txt','w').write(it['prompt'])
print(len(it['prompt']))
EOF
echo "==="; wc -l /var/tmp/lg-item.txt
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
s=open('/var/tmp/lg-item.txt').read()
line=s.splitlines()[11]
import textwrap
print(textwrap.fill(line, 120))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -30 | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186 cbf688a; do echo "== $r =="; git ls-tree -r --name-only $r -- tests/fixtures/ | grep -F 'frozen' || echo "(no frozen dirs)"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186 cbf688a; do for f in r13-cert-frozen r14-cache-frozen r15-preservation-frozen; do echo "===== $r:$f/expected.json ====="; git show $r:tests/fixtures/$f/expected.json 2>&1 | head -60; done; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186 cbf688a; do echo "===== $r ====="; git show $r:SKILL.md 2>&1 | grep -nE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' | sed 's/\(.\{200\}\).*/\1.../' | cat; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in cbf688a b410186; do echo "== $r =="; for f in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json; do printf '%s  ' "$f"; git show $r:$f 2>/dev/null | sha256sum | cut -d' ' -f1; done; done
mkdir -p /var/tmp/souji-r16-RevGateSpec && cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import subprocess,re,os,ast,json
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'
revs={'r13-end a31642d':'a31642d','r14-end cc21683':'cc21683','r15-land b410186':'b410186','r16 cbf688a':'cbf688a'}
pat=re.compile(r'(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.(?:sh|py)')
def show(rev,path):
    p=subprocess.run(['git','-C',LANE,'show',f'{rev}:{path}'],capture_output=True)
    return p.stdout if p.returncode==0 else None
for label,rev in revs.items():
    skill=show(rev,'SKILL.md').decode()
    cited=sorted(set(m.group(0) for m in pat.finditer(skill)))
    print(f'== {label} ({rev}) cited={len(cited)}')
    for c in cited:
        data=show(rev,c)
        if data is None:
            print(f'  LG-MISSING-REG  {c}')
            continue
        if c.endswith('.py'):
            try: ast.parse(data.decode()); status='parse-ok'
            except SyntaxError as e: status=f'PARSE-FAIL {e.lineno}: {e.msg}'
        else:
            open('/var/tmp/souji-r16-RevGateSpec/x.sh','wb').write(data)
            p=subprocess.run(['bash','-n','/var/tmp/souji-r16-RevGateSpec/x.sh'],capture_output=True,text=True)
            status='parse-ok' if p.returncode==0 else f'PARSE-FAIL({p.returncode}) {p.stderr.strip().splitlines()[:2]}'
        if status!='parse-ok': print(f'  LG-PARSE-REG    {c}  {status}')
    print('  -- clean otherwise')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import subprocess,re
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'
MR=re.compile(r'(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b')
rounds={13:'a31642d',14:'cc21683',15:'b410186'}
def show(rev,path):
    p=subprocess.run(['git','-C',LANE,'show',f'{rev}:{path}'],capture_output=True)
    return p.stdout.decode() if p.returncode==0 else None
for r,rev in rounds.items():
    ls=subprocess.run(['git','-C',LANE,'ls-tree','-r','--name-only',rev,'--',f'.ufo/waves/round-{r}/'],capture_output=True,text=True).stdout.split()
    md=[p for p in ls if p.endswith('.md')]
    lesson=show(rev,f'corpus/lessons/round-{r}.md')
    print(f'== round {r} rev {rev}: {len(md)} seat .md; lesson present={lesson is not None}')
    if lesson is None:
        continue
    hits=0
    for p in md:
        body=show(rev,p)
        for ln in body.splitlines():
            s=ln.strip()
            if s and MR.search(s):
                hits+=1
                carried = s in lesson
                print(f'  {"CARRIED " if carried else "UNCARRIED"} {p}: {s[:110]}')
    print(f'  markers={hits}')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import subprocess,json,hashlib,re
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'
revs={'r13-end':'a31642d','r14-end':'cc21683','r15-land':'b410186','r16':'cbf688a'}
def ls(rev,path):
    return subprocess.run(['git','-C',LANE,'ls-tree','-r','--name-only',rev,'--',path],capture_output=True,text=True).stdout.split()
def blob(rev,path):
    p=subprocess.run(['git','-C',LANE,'show',f'{rev}:{path}'],capture_output=True)
    return p.stdout if p.returncode==0 else None
for label,rev in revs.items():
    print(f'== {label} ({rev})')
    frozen=[p for p in ls(rev,'tests/fixtures/') if re.search(r'tests/fixtures/[^/]+-frozen/expected\.json$',p)]
    for exp in frozen:
        d=json.loads(blob(rev,exp))
        fdir=exp.rsplit('/',1)[0]
        pins=0; bad=0
        for rel,want in d.get('files',{}).items():
            pins+=1
            data=blob(rev,f'{fdir}/{rel}')
            if data is None: data=blob(rev,rel)
            got=hashlib.sha256(data).hexdigest() if data is not None else None
            if got!=want:
                bad+=1; print(f'   LG-FROZEN-PIN {exp} -> {rel}: pinned={want[:12]} got={(got or "MISSING")[:12]}')
        rs=d.get('record_sha256')
        if rs:
            rec=d.get('record'); data=blob(rev,f'{fdir}/{rec}') if rec else None
            got=hashlib.sha256(data).hexdigest() if data else None
            if got!=rs: print(f'   LG-FROZEN-PIN {exp} record {rec}: pinned={rs[:12]} got={(got or "MISSING")[:12]}')
        print(f'   {exp}: pins={pins} bad={bad}')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:corpus/lessons/round-15.md | grep -nEi 'configrepair|parse|syntax|incomplete|status' | head -30; echo "=== README r15 frozen ==="; git show cbf688a:tests/fixtures/r15-preservation-frozen/README.md; echo "=== record.json ==="; git show cbf688a:tests/fixtures/r15-preservation-frozen/record.json | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import subprocess,re
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'
MR=re.compile(r'(?i)\bSTATUS:\s*(?:INCOMPLETE|FAIL(?:ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b')
def show(rev,p):
    r=subprocess.run(['git','-C',LANE,'show',f'{rev}:{p}'],capture_output=True)
    return r.stdout.decode() if r.returncode==0 else None
for rev,paths in [('a31642d',['.ufo/waves/round-13/w1/EvidenceConnection.md','.ufo/waves/round-13/w1/SourceTimeout.md']),
                  ('cc21683',['.ufo/waves/round-14/w1/CachePrecedent.md']),
                  ('b410186',['.ufo/waves/round-15/w1/ConfigRepair.md'])]:
    for p in paths:
        body=show(rev,p)
        lines=body.splitlines()
        infence=False
        for i,ln in enumerate(lines,1):
            f=ln.lstrip().startswith('```')
            if MR.search(ln.strip()):
                print(f'{rev} {p}:{i} fence={ "IN" if infence else "OUT"} | {ln[:150]}')
            if f: infence = not infence
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE '^(function )?[a-zA-Z_][a-zA-Z0-9_]*\(\)|^main |^main\(\)|^run_selftest|^usage|^exit|^[[:space:]]*main "\$@"' | head -60; echo "=== tail ==="; git show cbf688a:tools/souji-census.sh | tail -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '1084,1170p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '1218,1260p'; echo "=== cfg_soft ==="; git show cbf688a:tools/souji-census.sh | sed -n '540,600p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE 'hookspath|fsmonitor|alternaterefscommand|promisor|partialclone|include\.path|includeif' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '935,962p'; echo "=== guard_bound_filters ==="; git show cbf688a:tools/souji-census.sh | sed -n '907,935p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '630,660p'; echo "=== guard_path ==="; git show cbf688a:tools/souji-census.sh | sed -n '184,200p;441,460p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186 cbf688a; do echo "== $r =="; git show $r:.gitattributes 2>&1 | head -20; done; echo "=== r16 lesson present? ==="; git cat-file -e cbf688a:corpus/lessons/round-16.md 2>&1; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import subprocess,ast
LANE='/home/vgpnk/Projects/shokunin/souji-shokunin'
def sh(args): return subprocess.run(args,capture_output=True,text=True)
for base,rev,label in [('a31642d','cc21683','r14 (a31642d..cc21683)'),('cc21683','b410186','r15 (cc21683..b410186)'),('cc21683','cbf688a','r15+r16 (cc21683..cbf688a)'),('b410186','cbf688a','r16 (b410186..cbf688a)')]:
    out=sh(['git','-C',LANE,'diff','--name-status',f'{base}..{rev}']).stdout.splitlines()
    files=[l.split('\t')[-1] for l in out if l.split('\t')[0] in ('A','M')]
    files=[f for f in files if f.endswith(('.sh','.py'))]
    print(f'== {label}: {len(files)} changed scripts')
    for f in files:
        p=subprocess.run(['git','-C',LANE,'show',f'{rev}:{f}'],capture_output=True)
        if p.returncode!=0: print('   DELETED-at-rev',f); continue
        if f.endswith('.py'):
            try: ast.parse(p.stdout.decode()); ok=True
            except SyntaxError: ok=False
        else:
            open('/var/tmp/souji-r16-RevGateSpec/y.sh','wb').write(p.stdout)
            ok=subprocess.run(['bash','-n','/var/tmp/souji-r16-RevGateSpec/y.sh'],capture_output=True).returncode==0
        if not ok: print('   LG-PARSE-CHANGED',f)
    print('   (clean otherwise)')
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- r13 EvidenceConnection 158-168 ---"; git show a31642d:.ufo/waves/round-13/w1/EvidenceConnection.md | sed -n '158,168p'; echo "--- r13 SourceTimeout 73-80 ---"; git show a31642d:.ufo/waves/round-13/w1/SourceTimeout.md | sed -n '73,80p'; echo "--- r14 CachePrecedent 154-162 ---"; git show cc21683:.ufo/waves/round-14/w1/CachePrecedent.md | sed -n '154,162p'; echo "--- r14 CachePrecedent 216-222 ---"; git show cc21683:.ufo/waves/round-14/w1/CachePrecedent.md | sed -n '216,222p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cbf688a -- corpus/lessons/ | cat; echo "=== r15 lesson lines 88-98 ==="; git show b410186:corpus/lessons/round-15.md | sed -n '88,98p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '763,840p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '874,935p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE 'excludesfile|attributesfile|expand_config_path|PROTECTED_FINDING=' | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '579,630p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE 'GIT_CONFIG|GIT_NO_LAZY_FETCH|export GIT|-c core\.' | cat; echo "=== guard_git_config ==="; git show cbf688a:tools/souji-census.sh | sed -n '669,690p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '1039,1084p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '60,150p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- r13 spotcheck decision ---"; git show cbf688a:corpus/lessons/round-13-verifier-spotcheck.md | sed -n '1,20p'; echo "--- r14 spotcheck decision ---"; git show cbf688a:corpus/lessons/round-14-verifier-spotcheck.md | sed -n '1,16p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import ast;ast.parse(open('census/round-16/run-matrix.py').read());print('run-matrix.py ast ok')"; python3 -c "import ast;ast.parse(open('tests/fixtures/r15-census-config.py').read());print('r15-census-config.py ast ok')"; bash -n tools/souji-census.sh && echo "census bash -n ok"; shellcheck -S warning tools/souji-census.sh >/dev/null 2>&1; echo "shellcheck rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in a31642d cc21683 b410186 cbf688a; do echo "== $r =="; git ls-tree -r --name-only $r -- .ufo/reports/ | cat; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE '^while \[ "\$#" -gt 0 \]|^if \[ "\$SELFTEST" = 1 \]|^\[ -n "\$ROOT" \]|^guard_path root|^emit_census$|^exit 0$|^run_selftest\(\)|^emit_compare$|^  emit_compare$' | cat; echo "--- 875-882 ---"; git show cbf688a:tools/souji-census.sh | sed -n '875,882p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cbf688a -- tools/ tests/fixtures/ | grep -cE '\.(sh|py)$'
```
