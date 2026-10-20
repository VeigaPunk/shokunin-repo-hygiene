# ConnSkillRegistry — SKILL.md gate-registry corrections (r16)

Seat: SoujiR16.ConnSkillRegistry (connector, leaf). Judged on: operability.
Scope: draft exact replacement text for the `## Gate registry` table rows and the
`Repeatable fleet census` bullet in `/home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md`
at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (HEAD, 231 lines). **SKILL.md was not edited** —
it is not in this seat's owned files. Every block below is old→new, line-anchored, and
preserves the existing eight-column table shape (`|` × 9 per row).

## Axes (named)

1. **Operability** — can an operator read the row and take the right action, including when a
   repository was not measurable?
2. **Calibration** — does the text avoid presenting non-discriminating or unrun evidence as
   admission evidence?
3. **Contract fidelity** — same columns, same row names, same owner, one physical line per row.
4. **Gate self-consistency** — every newly cited `tools|tests/fixtures|census/round-N` `.sh`/`.py`
   path must exist and parse at the revision where the text lands (LG-MISSING-REG / LG-PARSE-REG),
   otherwise the new text makes the C2 gate red against itself.

## Verified evidence (read-only, at cbf688a)

| fact | evidence |
|---|---|
| Round-16 exit map: `0 census emitted (rows may carry error/status-unverifiable) / header-only diff; 1 selftest or setup failure; 2 usage, malformed baseline, or protected-path refusal; 3 compare drift` | `tools/souji-census.sh:121-124` |
| Degraded config → one `error` row, `return 0`, stderr `config-unsupported` | `tools/souji-census.sh:1086-1092` |
| Bound filter → `status-skipped`, `unverifiable` (dirty 0) | `tools/souji-census.sh:935-943` |
| Whole-run exit 2 propagated for protected reach; non-dir root → exit 1 (setup) | `tools/souji-census.sh:1221,1230-1234`, `:1331-1332` |
| Malformed baseline → exit 2 | `tools/souji-census.sh:1246-1267` |
| Legacy `--selftest` still present; scratch hardcoded `/var/tmp` (so `TMPDIR` is belt-and-braces, not load-bearing) | `tools/souji-census.sh:1437,1740,1784` |
| Fixture r16 revisions (degrade to `error` row exit 0; promisor never refused; `alternateRefsCommand` inert; bound filter skips status only that repo; EACCES errno oracle) | `tests/fixtures/r15-census-config.py:8-33` |
| Fixture IDs `R15CFG-01..20`, `CASE_CLASSES`, `HARM_CASES` (r16 adds 03/07/14) | `tests/fixtures/r15-census-config.py:128-172` |
| `TOOL-KIND` is digest-keyed (a31642d pre-harm, cc21683 r14-harm, else `other`); the case oracle is identical for every arm, never digest-keyed; `--case` is debugging-only | `tests/fixtures/r15-census-config.py:1375-1438` |
| Prerequisite/usage → exit 2 | `tests/fixtures/r15-census-config.py:263-265` |
| Measured arms: changed 20/20 + 12/12 + selftest 38 checks/0 failed/rc 0; pre-harm 8 and 10 failures; r14-harm 16/20 failures on r15-config (4 pass) and selftest 38/0; r15-baseline `bash -n` rc 2 at line 1368, both fixtures fully red | `census/round-16/c1-matrix.json` |
| Live fleet: 23 rows on both arms, rc 0, 0 stderr lines, **identical row sets**, no `error`/`status-unverifiable` rows | `census/round-16/live-fleet.json` |
| Seat reports are committed under `.ufo/waves/` (round-15 `ConfigRepair.md` tracked at b410186) | `git ls-tree b410186 -- .ufo/waves/round-15/w1/`, `git cat-file -e` |
| r15 frozen pin stale at HEAD: `tools/souji-census.sh` expected `b5187351…`, actual `fed43c71…`; `tests/fixtures/r15-census-config.py` expected `6314d45d…`, actual `9151cde8…`; `r14-census-boundary.py` pin and `record_sha256` match | `tests/fixtures/r15-preservation-frozen/expected.json`; `sha256sum`; `c1-matrix.json` `fixtures_sha256` |
| `bash -n tools/souji-census.sh` rc 0; `shellcheck -S warning` rc 0; `ast.parse` ok on the fixture and on `census/round-16/run-matrix.py` | this seat, commands below |
| New C2 files do **not** exist at HEAD (`tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py`) | `ls` returned ENOENT |
| Gate contract (CLI, finding ids, TSV + `SUMMARY`, exit 0/1/2) | `.ufo/waves/round-16/w1-spec.json` items[0], items[1] |

## Block A — replace `SKILL.md:138` (souji-census row)

OLD (verbatim):

```markdown
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv]` | 0 clean; 3 failed differential comparison; 1 failed selftest or could-not-evaluate setup (legacy debt); 2 could-not-evaluate usage/malformed baseline/protected or unsupported Git path (`path-protected`) | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | caller comparison is unpinned; no pinned complete legacy selftest id set | read-only census; compare capture and isolated selftest under `/var/tmp` | souji |
```

NEW (verbatim, one physical line):

```markdown
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--include-root] [--compare PREV.tsv]` | 0 census emitted — including per-repository degraded rows (`error`, `status-unverifiable`) — or header-only diff; 1 failed selftest or setup failure (missing `git`/`du`, root not a directory); 2 could-not-evaluate usage, malformed baseline, or protected-path refusal (`path-protected`); 3 differential comparison drift | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | caller comparison is unpinned; no pinned legacy selftest id set; code 0 does not certify rows — read each row's `verdict_flags` | read-only census; compare capture and isolated selftest under `/var/tmp` | souji |
```

Why: three factual defects in the old cell — (a) "0 clean" is false for degraded repositories
(one `error` row, exit 0), (b) "1 … could-not-evaluate setup" omits that code 1 also covers
setup failures such as a non-directory root, (c) "protected or unsupported Git path" names a
class the census no longer has: every Git-path refusal is `path-protected`, and no
"unsupported Git" code 2 exists (those are `souji-repo-structure` codes 3/4 at line 142).

## Block B — replace `SKILL.md:148` (r15-census-config row)

OLD (verbatim):

```markdown
| r15-census-config | gate | `python3 tests/fixtures/r15-census-config.py --tool PATH` | 0 clean; 1 failed case/id-set; 2 could-not-evaluate prerequisite/trace/usage | same full default invocation over isolated synthetic HOME; selected tool supplies pre-harm, harmed or changed arm | fixture literal EXPECTED_IDS and per-case fixed exits/findings/row expectations | isolated `/var/tmp`; no real store or live fleet probe | souji |
```

NEW (verbatim, one physical line):

```markdown
| r15-census-config | gate | `python3 tests/fixtures/r15-census-config.py --tool PATH` | 0 clean; 1 failed case/id-set; 2 could-not-evaluate prerequisite/trace/usage | same full default invocation over an isolated synthetic HOME; `--tool` selects the arm (a31642d pre-harm and cc21683 r14-harm are labelled by digest only; the oracle is identical for every arm and no verdict is digest-keyed; `--case ID` is debugging-only and never admission) | fixture literal EXPECTED_IDS R15CFG-01..20, CASE_CLASSES and HARM_CASES; per-case fixed exits/findings/row expectations; r16 oracles 03 config degrade (exit 0, `error` row), 07 invalid promisor boolean, 14 attribute-bound filter skips status; `--json` records observed_exit/observed_finding | isolated `/var/tmp`; no real store or live fleet probe | souji |
```

Why: the old wording says the arm is "pre-harm, harmed or changed" with no r16 revision, and
nothing tells a reader that r15-baseline is a *conformance* red (it does not parse), not a
behavioral red, or that the legacy `--selftest` is non-discriminating (it passes 38/0 on
cc21683 in `c1-matrix.json`). The row is also the binding point for the C2 checker, which needs
`--json`.

## Block C — append two rows after `SKILL.md:150` (last row of the table)

```markdown
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--base REV]` | 0 no findings; 1 findings (`LG-*`); 2 could-not-evaluate usage, unknown rev, absent SKILL.md, or git failure | `python3 tools/souji-landing-gate.py --selftest`; external fixture below | pinned finding ids LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-SEAT-UNCARRIED; committed `tests/fixtures/*-frozen/expected.json` `files`/record digests at REV; `SUMMARY` coverage counts are part of the verdict (zero `checked_markers` is not evidence) | read-only `git archive REV` into a private `/var/tmp` snapshot; synthetic repos in selftest; never executes repository code (`bash -n`, `ast.parse` only) | souji |
| r16-landing-gate | gate | `python3 tests/fixtures/r16-landing-gate.py [--tool PATH]` | 0 clean; 1 failed case or failed vacuity control; 2 could-not-evaluate missing prerequisite/usage | same default self-invocation fixture | fixture literal case ids; historical replay pins (b410186 must yield LG-PARSE-REG for `tools/souji-census.sh`, LG-FROZEN-PIN, LG-SEAT-UNCARRIED for `.ufo/waves/round-15/w1/ConfigRepair.md`); held-out synthetic cases | isolated `/var/tmp`; reads the lane at named revisions; no real store or live fleet probe | souji |
```

Order matches the existing tool→fixture pairing (`souji-preservation-evidence` then
`r15-preservation-evidence` at lines 149-150).

## Block D — replace `SKILL.md:167-168` (bullet)

OLD (verbatim):

```markdown
- Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`
  (r6; per-repo worktrees/unpushed/dirty/scratch/mtime/flags).
```

NEW:

```markdown
- Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`
  (r6; r16 value/effect-aware config guard) — per-repo
  worktrees/unpushed/dirty/scratch/mtime/flags. Code 0 is not a fleet-wide
  clean bill: read the flags (`error` = config could not be evaluated, and the
  numeric fields are `0` placeholders, not measurements; `status-unverifiable`
  = status was skipped or failed, so `dirty` is unknown). Code 2 is a
  whole-run refusal (usage, malformed baseline, protected path); a degraded
  repository never changes the exit code.
```

## Block E — second-order stale prose, `SKILL.md:226-231` (recommended)

The paragraph still tells the operator that r15 landed "an unverified value/effect-aware
candidate" with "No r15 … preservation … claimed". Left unchanged, it contradicts the
corrected row and hides that the current bytes pass the fixture. Replace the six lines:

OLD (verbatim):

```markdown
R14's blanket local-configuration refusal was rejected as harmed by the
outside closure. R15 lands an unverified value/effect-aware candidate:
intended behavior and remaining unsupported forms are in the current tool
header, not demonstrated guarantees. No r15 benign/mixed-fleet preservation,
namespace retention, ShellCheck or selftest pass is claimed. Exact unrun
acceptance and frozen re-pin requirements: `corpus/lessons/round-15.md`.
```

NEW:

```markdown
R14's blanket local-configuration refusal was rejected as harmed by the
outside closure. R16 replaces it with a value/effect-aware guard: repository
config is classified per key and value, not by key presence, and the accepted,
degraded and whole-run-refused classes are stated in the tool header at the
landing revision. A protected-namespace reach still refuses the whole run
(exit 2); a repository whose config cannot be evaluated becomes one `error`
row (exit 0; no git command runs there); a filter driver bound by an
attributes source skips status for that repository only
(`status-unverifiable`) and never runs. Code 0 does not certify the rows it
emits. The measured arm matrix for the current bytes is
`census/round-16/c1-matrix.json` (counting command
`python3 census/round-16/run-matrix.py --changed <rev> --output <new.json>`);
the round record and any unrun acceptance checks are in
`corpus/lessons/round-16.md`.
```

## Block F — one sentence in the gate-map preamble (optional, recommended)

Insert after `SKILL.md:131` ("…their historical fallback is not Q4-conformant.") and before the
blank line preceding the table:

```markdown
A probe's code 0 means it ran and produced data; code 0 does not certify that
data. `souji-census` in particular emits per-repository `error` and
`status-unverifiable` rows and still exits 0 — read the row flags, not the
exit code.
```

No table row or column changes.

## Landing order and cross-surface risks

1. **Atomic landing (blocking).** Block C cites `tools/souji-landing-gate.py` and
   `tests/fixtures/r16-landing-gate.py`. Both are absent at HEAD. `LG-MISSING-REG` fires on any
   registry-cited path absent at REV, so landing SKILL.md before those files makes the new gate
   red on the landing commit itself. Blocks A–F and both new files must be one commit.
2. **Self-application.** Once cited, the gate parses itself, the fixture, `tools/souji-census.sh`
   and `tests/fixtures/r15-census-config.py` via `bash -n`/`ast.parse`. All four currently parse
   (this seat: `bash -n` rc 0, `shellcheck -S warning` rc 0, `ast.parse` ok), so the new text does
   not add a red. `census/round-16/run-matrix.py` is cited by Block E and also parses; if L1 wants
   no round-specific counting command in SKILL, delete only that parenthesis — the rest of Block E
   does not depend on it.
3. **Coverage vacuity in the landing gate.** `LG-SEAT-UNCARRIED` reads `.ufo/waves/round-N/*.md`
   from committed bytes. The round-16 seat report checked here
   (`.ufo/waves/round-16/w1/DraftSkillSection.md`) is untracked at HEAD, so a round-end gate run
   before the reports are committed would check zero markers and pass vacuously. The
   `SUMMARY … checked_markers=C` field is the guard; the row text says so.
4. **Frozen-pin independence.** `LG-FROZEN-PIN` verifies `tests/fixtures/*-frozen/expected.json`
   against committed bytes at REV. A digest recomputed from the file under test is
   self-referential and must not be recorded as a pin (agrees with `DraftLessonGate.md` finding
   5); the r16 row's pinned-value cell therefore names finding ids and the historical replay,
   not a digest.
5. **Do not promote the census to a gate.** It remains a probe: exit 0 is data, and Blocks A/D/F
   say so explicitly. No row's `kind` or `owner` cell changes.
6. **Do not cite the live fleet as repair evidence.** `live-fleet.json` is a no-regression
   observation (23 identical rows, both arms, rc 0, zero stderr) on a fleet with no hostile
   config; it does not discriminate the r14 value-blind defect. The discriminating mixed-fleet
   controls are `R15CFG-16`/`R15CFG-17` in the fixture (`c1-matrix.json`: 16/20 r14-harm failures,
   0/20 changed).
7. **`error` rows are literal zeros.** `census_one` prints `%s\t0\t0\t0\t0\t\terror`
   (`tools/souji-census.sh:1090`). Any SKILL wording that only says "degraded" without saying
   "placeholders, not measurements" invites a summing or sorting reader to under-count. Blocks A,
   D and F carry that sentence; `DraftSkillSection.md` carries the long form.
8. **`TMPDIR` is inert for the census selftest** (scratch is hardcoded `/var/tmp` at
   `tools/souji-census.sh:1437`). Keep the prefix so the row matches the preamble convention, but
   do not read it as evidence that TMPDIR is honored.
9. **`--case ID` never admits.** The fixture help says "debugging only, never for admission"
   (`tests/fixtures/r15-census-config.py:1384-1386`); Block B states it so a green single case is
   not quotable as a gate pass.
10. **C2 end-green is blocked on R4, not on this text.** At HEAD the r15 frozen pin still records
    the pre-r16 bytes for two files (`b5187351…` vs actual `fed43c71…` for
    `tools/souji-census.sh`; `6314d45d…` vs actual `9151cde8…` for
    `tests/fixtures/r15-census-config.py`). `LG-FROZEN-PIN` therefore fires at `cbf688a` until the
    pin is re-recorded with its measured revision. Block C's row describes the pin as an input
    and must not be read as evidence that it is green; a re-pin computed from the file under test
    is self-referential (risk 4).

## Not verified by this seat

- No fixture, gate, or census run (connector probe rule; executors/L1 own those). The counts in
  Block B's rationale are read from `census/round-16/c1-matrix.json` as the lane's recorded
  measurement, not re-executed.
- No real-fleet `error` row exists in `live-fleet.json`; the degrade path is evidenced by code
  and by fixture case `R15CFG-03` (`obs=0`, `config-unsupported:git-config-unparsed` in the
  matrix), not by an observed fleet row.
- The stale-pin row is a byte comparison; the gate's `LG-FROZEN-PIN` emission was not observed
  because `tools/souji-landing-gate.py` does not exist yet.
- The C2 files were absent when this report was written; Blocks C/D/E are text that must be
  reconciled with the landed gate if its CLI diverges from the spec pin.

## Tooling

No installs or upgrades. `bash -n`, `shellcheck` (present), `python3` stdlib used only.

STATUS: draft complete; SKILL.md unedited; no fixture/gate/census execution by this seat; the
two C2 files are absent at HEAD, so Block C must land atomically with them.

## Commands

```bash
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ 2>&1; echo ---; ls /home/vgpnk/Projects/shokunin/souji-shokunin/tools/ 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -6 && echo --- && git rev-parse HEAD && echo --- && ls *.md && echo --- && wc -l SKILL.md 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls census/round-16/ 2>&1 && echo --- && ls tests/fixtures/ | head -40 && echo --- && ls tools/souji-landing-gate.py 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "Gate registry\|Repeatable fleet census\|r15-census-config\|^Sources for this skill\|^## " SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "exit 2\|exit 3\|exit 1\|exit 0" tools/souji-census.sh | sed -n '1,120p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "Baseline discrimination" -A 40 tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16 && python3 -c "
import json,sys
for f in ('w1-spec.json','w1-dispatch.json'):
    d=json.load(open(f))
    s=json.dumps(d)
    print(f, type(d).__name__, len(s))
    print('landing-gate occurrences:', s.count('landing-gate'), '| landing_gate:', s.count('landing_gate'))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16 && python3 - <<'EOF'
import json
d=json.load(open('w1-spec.json'))
def walk(o,path=""):
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,f"{path}.{k}")
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,f"{path}[{i}]")
    elif isinstance(o,str) and 'landing-gate' in o:
        print("==",path)
        print(o[:3000])
walk(d)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16 && python3 - <<'EOF'
import json
d=json.load(open('w1-spec.json'))
for i in (0,1):
    print(f"=========== items[{i}] name={d['items'][i].get('name')}")
    print(d['items'][i]['prompt'])
    print()
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1; echo ---; grep -n "set -n\|Bash" corpus/SOURCES.md | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "TOOL-KIND\|r15-baseline\|pre-harm\|r14-harm\|def main\|add_argument" tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && tail -30 corpus/SOURCES.md && echo --- && grep -c "^| S" corpus/SOURCES.md && grep -n "^| S04" corpus/SOURCES.md | tail -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '125,170p' SKILL.md | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "config-unsupported\|status-skipped\|unsupported" tools/souji-census.sh | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w1/ 2>&1; echo ---; ls .ufo/waves/round-15/w1/ 2>&1 | head; echo ---; grep -n "TMPDIR\|mktemp -d" tools/souji-census.sh | sed -n '1,25p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat b410186..HEAD && echo --- && sed -n '930,950p;1215,1240p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import ast,sys
p='tests/fixtures/r15-census-config.py'
ast.parse(open(p,'rb').read(), filename=p); print('ast.parse ok', p)
" ; git diff --stat -- SKILL.md; git rev-parse HEAD:SKILL.md; sha256sum SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '214,231p' SKILL.md | cat -n && echo === && bash -n tools/souji-census.sh && echo "bash -n: ok" && shellcheck -S warning tools/souji-census.sh; echo "shellcheck rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import ast
for p in ('census/round-16/run-matrix.py',):
    ast.parse(open(p,'rb').read(), filename=p); print('ast.parse ok', p)
" && ls -l census/round-16/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print(type(d).__name__, list(d)[:12])
print(json.dumps(d, indent=1)[:2500])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print('lane_head', d['lane_head']); print('changed', d['changed']); print('fixtures_dirty', d['fixtures_dirty']); print('git_version', d['git_version']); print('fixtures', d['fixtures_sha256'])
print()
for name,arm in d['arms'].items():
    print('ARM', name, 'bash_n', arm.get('bash_n'))
    for fx in ('r15-config','r14-namespace'):
        s=arm.get(fx) or {}
        print('  ',fx,'rc=',s.get('rc'),'total=',s.get('total'),'failed=',s.get('failed'))
    st=arm.get('selftest') or {}
    print('   selftest', st if not isinstance(st,dict) else {k:st.get(k) for k in ('rc','total','failed','summary')})
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && head -c 2200 census/round-16/live-fleet.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,collections
d=json.load(open('census/round-16/live-fleet.json'))
print('root',d['root'],'observed',d['observed'])
for name,arm in d['arms'].items():
    flags=collections.Counter()
    for r in arm['rows']:
        for f in r[6].split(',') if r[6] else []:
            flags[f]+=1
    print(name, arm.get('rev'), arm.get('result'), 'rows',arm.get('row_count'), 'stderr',arm.get('stderr_lines'), dict(flags))
    print('   stderr_sample', arm.get('stderr_sample') or arm.get('stderr_tail') or '')
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,collections
d=json.load(open('census/round-16/live-fleet.json'))
for name,arm in d['arms'].items():
    lens=collections.Counter(len(r) for r in arm['rows'])
    print(name, arm.get('rev'), arm.get('result'), 'rows',arm.get('row_count'),'len',dict(lens),'stderr_lines',arm.get('stderr_lines'))
    print('  keys', list(arm))
    flags=collections.Counter()
    for r in arm['rows']:
        if len(r)>=7:
            for f in (r[6].split(',') if r[6] else []): flags[f]+=1
    print('  flags',dict(flags))
    st=arm.get('stderr_lines_detail') or arm.get('stderr')
    if st: print('  stderr',st[:5])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/live-fleet.json'))
a=d['arms']['r14-harm']['rows']; b=d['arms']['changed']['rows']
print('first row', a[0])
sa={tuple(r[:5])+ (r[5],) for r in a}; sb=set(map(tuple,b))
print('equal sets:', sa==sb, 'only r14:', sorted(sa-sb), 'only changed:', sorted(sb-sa))
print('changed rows with error/status:', [r for r in b if 'error' in r[5] or 'status-unverifiable' in r[5]])
print('r14 rows with error:', [r for r in a if 'error' in r[5]])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree b410186 -- .ufo/waves/round-15/w1/ | head -5; echo "rc=$?"; echo ---; git ls-tree HEAD -- .ufo/waves/round-15/w1/ConfigRepair.md; echo ---; git cat-file -e b410186:.ufo/waves/round-15/w1/ConfigRepair.md && echo "tracked at b410186" || echo "NOT tracked at b410186"; git cat-file -e HEAD:.ufo/waves/round-16/w1/DraftSkillSection.md && echo "r16 draft tracked at HEAD" || echo "r16 draft untracked at HEAD"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' SKILL.md | sort -u
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for n,a in d['arms'].items():
    print('==',n)
    print(json.dumps(a.get('selftest'), indent=1)[:700])
    print('  shellcheck', json.dumps(a.get('shellcheck'))[:300])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^def die\|def die(" -A 4 tests/fixtures/r15-census-config.py && grep -n "def main" -B2 tests/fixtures/r14-census-boundary.py | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^# Exit codes\|^#   0 census emitted\|^#   2 usage\|^#   3 compare drift\|root is not a directory\|census failed for" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "r14-census-boundary\|souji-repo-structure" SKILL.md | head -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-preservation-frozen/record.json && git ls-tree b410186 -- tests/fixtures/r15-preservation-frozen/ && git ls-tree HEAD -- tests/fixtures/r15-preservation-frozen/
```

Reads (file tool, not shell): `skill://godspeed`; `SKILL.md:100-231`, `:125-140`;
`tools/souji-census.sh:1-80`, `:84-200`, `:1060-1100`;
`tests/fixtures/r15-census-config.py:1-90`, `:128-230`, `:1360-1450`;
`census/round-16/run-matrix.py:1-70`; `.ufo/waves/round-16/w1/DraftSkillSection.md`;
`.ufo/waves/round-16/w1/DraftLessonGate.md`;
`.ufo/waves/round-16/w1-spec.json` (`.items[0].prompt`, `.items[1].prompt`).
