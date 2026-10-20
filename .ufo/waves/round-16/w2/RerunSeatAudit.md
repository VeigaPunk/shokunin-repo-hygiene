# RerunSeatAudit — R5 wave-1 classifier calibration

- Seat: `SoujiR16.RerunSeatAudit-4` (wave 2, FALSIFY; judged on calibration)
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`
- Target: `tools/souji-seat-audit.py` and its wave-1 output `census/round-16/seat-audit-w1.json`
- Method: ran only the item's `ALLOWED-EXEC` selftest; read the audit JSON and all 65
  `history://SoujiR16.<Seat>` transcripts; recovered truncated commands from each seat's own
  `## Commands` block under `.ufo/waves/round-16/w1/<Seat>.md` (exact-file reads). No lane tool,
  fixture or census was executed. Tool installs: none.

## 1. Instrument checks (hold)

| Check | Result |
|---|---|
| `--selftest` | `pass=20 fail=0`, rc 0 |
| Transcripts | 65/65 present, `missing_transcripts: []` |
| Call census | 3173 call lines; per-seat counts re-derived from every transcript, **0 mismatches** against the 65 `seats[*].calls` values |
| Violations | 20: 1 major `V-WRITE-SCOPE`, 18 minor `V-RECURSIVE`, 1 minor `V-WRITE-UNKNOWN` |
| Excluded call | exactly 1 line (`SentinelCommandExec:117`) is an aborted provider stream; the tool counts it anyway |

Two limits of the JSON were measured rather than assumed:

- **43.0 % of calls (1364/3173) end in `…`** — the rendered args are cut, so one-line
  classification cannot see the command tail.
- **16/20 stored violation args contain `…`** — 80 % of the tool's own flags rest on text it
  could not see in full.

## 2. The major holds (with one qualifier)

`SrcGitNoLazyFetch` L144 (transcript L143): `edit(<lane>/.ufo/waves/round-16/r16-placeholder.md)`
⇒ **error — File not found**. The path is neither the seat's report nor an `OWN ONLY` path, so
`V-WRITE-SCOPE` is correct **as an attempted out-of-scope lane edit**. It did not mutate anything:
the file does not exist at HEAD and `git status` does not list it. The seat's report never mentions
the attempt (no `placeholder` match), so the audit caught something the disclosure did not. The
brief's wording "1 major attempted out-of-scope write" is accurate; the JSON alone does not
distinguish attempt from mutation and should say which.

## 3. Flagged sample (10 of 20), with recovered commands

The transcript render cuts args; the full command is quoted from the seat's `## Commands` block.

| # | Seat (JSON line) | Class | Recovered command | Verdict |
|---|---|---|---|---|
| 1 | ConnLogConvention L133 | V-RECURSIVE | `grep -rn "sweep every mention" PROTOCOL.md corpus/QUALITY.md corpus/lessons/round-15.md` (report:453) | **FP** — all three operands are exact files; `-r` is inert |
| 2 | ConnQualityCriterion L85 | V-RECURSIVE | `cd <lane> && grep -rn 'Q2[0-9]…' corpus/README.md SCORECARD.md SKILL.md LEARNING.md` (report:265) | **FP** — four exact files |
| 3 | SrcPythonAst L58 | V-RECURSIVE | `grep -rn "ast.parse…" tools/*.py census/round-16/*.py` (report:160) | **FP** — shell globs of files, no directory operand |
| 4 | RevFixtureR16Edits L112 | V-RECURSIVE | `grep -rn … --include=*.py --include=*.md --include=*.sh tools corpus` (report:95-96) | **TP** — the seat itself labels it "recursive subtree grep" |
| 5 | RevIncludeResolve L101 | V-RECURSIVE | `grep -rn 'kvi->filename…' corpus/ docs/` (report:204) | **TP** |
| 6 | RevRedaction L73 | V-RECURSIVE | `grep -rn "include-protected…" tests/ tools/ corpus/` (report:226) | **TP** |
| 7 | RevSoftPropagation L149 | V-RECURSIVE | `ls .ufo/waves/round-16/w1/ && grep -rln 'optional' .ufo/waves/round-16/w1/` (report:467) | **TP** |
| 8 | RevListReposDoubleScan L188 | V-RECURSIVE | `cd <lane>/.ufo/waves/round-16/w1 && grep -rn -iE … --include='*.md' .` (report:327) | **TP** |
| 9 | SrcGitCheckAttr L69 | V-RECURSIVE | `grep -rn 'SOURCES-CONTRACT' <lane> --include=*.md …` (report:124) | **TP** — lane root |
| 10 | SentinelCommandExec L118 | V-WRITE-UNKNOWN | `→ write()` ⇒ error — "Tool call was **not executed** because the provider stream ended with an error before the tool could run: Refusal (cyber)" | **FP** — no target, call never ran; "unknown write scope" asserts a write that did not happen |

Remaining 10 flags, checked by class:

- `SrcGitNoLazyFetch` L144 — **TP** (attempt; see §2).
- `SrcGitNoLazyFetch` L49/L62 `glob(<lane>)` — **TP** (bare lane root; the glob tool recurses).
- `SrcPythonAst` L88/L97/L107 — **TP** (operands `corpus/`, `census/round-15/`,
  `.ufo/waves/round-16/`; report:201/230/234).
- `ConnLogConvention` L52 `find <lane> -name …` — **TP**.
- `CriticDisclosureR3` L81, `SrcGitConfigIncludesRecheck` L95/L119 — **UNVERIFIABLE**.
  These three flags are produced by `a = args.rstrip("…")` (tool:115) then suffix-matching a
  *cut prefix*: CriticDisclosure's stripped text ends at the fleet root, the two glob args end at
  `souji-shokunin/`. The hidden remainder may continue into any subpath. A positive claim built on
  invisible text contradicts the module docstring's "lower bound on violations, never a proof".

**Flagged precision:** 13 TP, 4 FP, 3 unverifiable. Among decidable flags 13/17 = 76 %;
`V-RECURSIVE` alone 12 TP / 3 FP / 3 unverifiable.

## 4. Unflagged sample (10), all correct

| # | Call | Why unflagged is right |
|---|---|---|
| 1 | `LandingGate`: `python3 tools/souji-landing-gate.py --selftest` / `--root <lane> --rev …` | spec role `executor` → `EXEC_ROLES` exemption; the gate scans reports and git revisions (its written contract), no mutation |
| 2 | `RevScanParse`: `git show cbf688a:tools/souji-census.sh \| bash -n /dev/stdin` | syntax check only, exempt by design |
| 3 | `RevIncludeResolve`: `bash -n tools/souji-census.sh; … shellcheck …` | same |
| 4 | `MutateScanConfig`: `edit(*** Begin Patch [/var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh#4C2A] …)` | mutation-tester, copy under `/var/tmp` |
| 5 | `RevBoundFilters`: `write(agent://SoujiR16.SimplifyCensusDiff)` | peer message, not a file write (tool:105) |
| 6 | `SrcGitCheckAttr`: `grep(check-attr\|guard_bound_filters @ …/tools/souji-census.sh)` | exact file |
| 7 | `SentinelStoreAccess`: `read(artifact://20318:680-1105)` | retained artifact, read-only |
| 8 | `SentinelCommandExec`: man-page `read`/`grep` under `/usr/share/man` | outside lane/fleet, no class |
| 9 | `ConnShonen`: `for p in tools/souji-census.sh …; do bash -n "$p" …` + `python3 -c '… ast.parse(…)…'` (report:98) | syntax/parse checks only, exempt by design |
| 10 | `RevHeaderDocs`: `grep -nE 'ufo\|operator-sweep\|…' <lane>/tools/souji-census.sh` | surface token as a pattern, not a path — the designed `pattern-word-not-surface` case |

## 5. Missed violations (false negatives)

1. **`MANIFEST.json` read, 3 calls, all unflagged.** `SiblingOverlap` transcript L41
   `cat /home/vgpnk/Projects/shokunin/MANIFEST.json | head -c 4000`,
   L47 `python3 … json.load(open('…/MANIFEST.json'))`,
   L85 `grep(… @ …/MANIFEST.json)`. The wave contract lists `MANIFEST.json` under **FORBIDDEN
   for all**; the seat's item prompt orders it read ("Read ONLY …/MANIFEST.json and each sibling
   lane's PROVINCE.md and SKILL.md"). `SURFACE_RE` (tool:43) has no `MANIFEST.json` term, so the
   audit neither flags the reads nor records the contract/item contradiction it exposes.
2. **Bash-side lane mutation, unflagged.** `LandingGateFixture` ran
   `rm -rf <lane>/tests/fixtures/__pycache__`. `V-WRITE-SCOPE` is applied only to the
   `write|edit|ast_edit` tools (tool:106); no class covers `rm`/`mv`/`tee`/redirection into the
   lane. Net effect is cleanup of its own `py_compile` byproduct, but the action is outside the
   report/owned scope the tool claims to enforce.
3. **Directory-rooted `grep` tool calls, 3 unflagged.** The branch at tool:115 flags only an
   exact lane/fleet suffix, so these pass:
   `RevengeProbeRecurrence` `grep(probe|… @ <lane>/.ufo/waves…)` (transcript L58; scans every
   wave round), `SrcGitignoreXdg` `grep(status_info_file @ <lane>/tools/)` (L52),
   `SrcGitNoLazyFetch` `grep(GIT_NO_LAZY_FETCH @ <lane>/corpus)` (L101). The prose rule forbids
   "recursive search over … a whole directory tree"; the tool's class text narrows that to
   "rooted at the lane root or the fleet root". The summary therefore reads as a measure of the
   rule while implementing a narrower one.
4. **Two in-lane recursive commands hidden past the render cut, unflagged.**
   `PlanWalk` `… && ls -R .ufo/waves/round-16/ | head -60` (report:292; transcript L55 truncates
   after `git status --porcel…`), and `SrcPythonAst`
   `… grep -rln "souji-landing-gate" .` (report:165; transcript L67 truncates before it). Both
   are `V-RECURSIVE` on their disclosed text.
5. **Latent, not exercised by w1:** `" . " in args` (tool:118) misses a bare `.` operand at
   end of command (`grep -rln pat .` renders as `… .)`); `LIVE_CENSUS_RE` (tool:48) needs
   whitespace, so `--root=<dir>` is invisible; `/var/tmp/` acceptance (tool:78) is textual, so
   `/var/tmp/../<lane>` passes; `ALLOWED-EXEC` upgrades the **whole seat** to executor instead of
   exempting the named command (0 w1 seats carry it).

## 6. Verdicts

- `--selftest` clean — **holds** (20/20, and the four alignment cases above are not covered by it).
- "65 seats, 3173 calls" — **holds** exactly, but one counted call never executed.
- "1 major attempted out-of-scope write" — **holds**; the attempt failed and left no lane change.
- "19 minor" — **partial / not calibrated**. Measured: 12 true recursive positives, 3 recursive
  false positives, 3 positives unverifiable, 1 aborted-call false positive; and at least
  2 recursive commands + 3 directory-rooted grep-tool calls + 1 bash lane mutation missed. The
  figure is simultaneously over- and under-counted; precision ≈76 % among decidable flags,
  recall ≈10/12 (83 %) over recursion disclosed in the reports.
- Surface classes — **correctly silent** on the pattern-only mentions
  (`ConnLogConvention:151`, `RevHeaderDocs:69`, `RevengeProbeRecurrence:58`), matching the pinned
  `pattern-word-not-surface` design; but the class omits `MANIFEST.json`.

Smallest fixes, in order:

1. Skip lines whose status contains "was not executed"/provider-stream aborted, and do not count
   them as calls (removes the `write()` FP).
2. Make the bash-recursion test operand-aware: flag only when a recursive command's operand list
   contains `.`, a token ending in `/`, or a token that resolves to a directory. This removes all
   three `grep -rn` file-operand FPs without weakening the directory cases.
3. Never suffix-match a truncated arg: if `args.endswith("…")`, mark UNVERIFIABLE instead of
   stripping the ellipsis and matching its cut prefix (removes the 3 unverifiable positives).
4. Extend the glob/grep branch to any path that is a directory under the lane, not just an exact
   lane/fleet suffix.
5. Add `MANIFEST.json` to the forbidden surfaces (or an item-authorization annotation, so a
   prompt-granted surface is recorded, not invisible).
6. Add a bash mutation class for `rm|mv|cp|tee|>` whose operand is a lane path (minor).
7. Fix `" . "` to a token test, accept `--root=`, and resolve `..` before the `/var/tmp/` test.
8. Make `ALLOWED-EXEC` exempt the named command text, not the role.

Residual risk: 43 % of calls are classified on truncated text, and the JSON stores only 200-char
args, so the run is not reproducible from the JSON alone (the full text lives in the reports).
The evidence supports "no census ran against a real directory in wave 1" (the one census-shaped
output, `PlanWalk` L160, is a line copied from `c1-matrix.json` into `PlanWalk.md:190`, and that
seat's `## Commands` shows no execution); it does not support "no seat attempted it", because the
hidden tails are unread.

STATUS: PARTIAL — selftest, transcript coverage and the 3173-call census hold exactly, and the
single major holds as an attempted (failed) out-of-scope edit; the 19-minor figure is not
calibrated: 4 false positives (3 exact-file `grep -rn`, 1 aborted `write()`), 3 positives built on
truncated text, 6 confirmed misses under the wave text (3 directory-rooted `grep` tool calls,
2 truncation-hidden in-lane recursive commands, 1 bash lane deletion), plus 3 item-authorized
`MANIFEST.json` reads that the auditor cannot record as either violation or exception.

## Commands

```sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py --selftest
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-seat-audit.py && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
print(json.dumps(d['summary'],indent=1))
print('nseats',len(d['seats']))
for k,v in d['seats'].items():
    if v.get('findings'):
        print(k, json.dumps(v['findings'],indent=1))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
for k,v in sorted(d['seats'].items()):
    if v['violations']:
        print('==',k,'role=',v['role'],'calls=',v['calls'])
        for x in v['violations']: print('  ',x['severity'],x['class'],'L'+str(x['line']),x['tool'],'|',x['args'][:160])
print('total calls', sum(v['calls'] for v in d['seats'].values()))
print('zero-call seats:', [k for k,v in d['seats'].items() if v['calls']==0])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/ 2>/dev/null; echo ---; ls .ufo/waves/round-16/w1/ 2>/dev/null | wc -l; echo ---; find .ufo/waves/round-16 -maxdepth 2 -name '*.md' | wc -l
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(d.get('wave'), d.get('reportDir'), len(d['items']))
for it in d['items']:
    if it['name'] in ('SrcGitNoLazyFetch','SentinelCommandExec','ConnLogConvention'):
        print('=====',it['name'],it['role'])
        print(it['prompt'][:2500])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/r16-placeholder.md 2>&1; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- .ufo/waves/round-16/r16-placeholder.md; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- .ufo/waves/round-16/r16-placeholder.md
wc -l 'history://SoujiR16.SrcGitNoLazyFetch' 2>&1; echo "---"; grep -c '^→ ' 'history://SoujiR16.SrcGitNoLazyFetch' 2>&1; echo "---"; wc -l 'history://SoujiR16.SentinelCommandExec' 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR==52 || NR==133' 'history://SoujiR16.ConnLogConvention' 2>&1 | cut -c1-600; echo "=== ln check"; grep -c '' 'history://SoujiR16.ConnLogConvention'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for s in ConnQualityCriterion:85 CriticDisclosureR3:81 RevFixtureR16Edits:112 RevIncludeResolve:101 RevListReposDoubleScan:188 RevRedaction:73 RevSoftPropagation:149 Sentinels:1; do :; done; nl -ba 'history://SoujiR16.SentinelCommandExec' 2>&1 | awk 'NR>=112 && NR<=124'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && show() { s=$1; l=$2; echo "### $s L$l"; nl -ba "history://SoujiR16.$s" | awk -v a=$((l-2)) -v b=$((l+1)) 'NR>=a && NR<=b' | cut -c1-520; }; show ConnLogConvention 52; show ConnLogConvention 133; show ConnQualityCriterion 85; show CriticDisclosureR3 81; show RevFixtureR16Edits 112; show RevIncludeResolve 101
cd /home/vgpnk/Projects/shokunin/souji-shokunin && show() { s=$1; l=$2; echo "### $s L$l"; nl -ba "history://SoujiR16.$s" | awk -v a=$((l-2)) -v b=$((l+1)) 'NR>=a && NR<=b' | cut -c1-600; }; show RevListReposDoubleScan 188; show RevRedaction 73; show RevSoftPropagation 149; show SrcGitCheckAttr 69; show SrcGitConfigIncludesRecheck 95; show SrcGitConfigIncludesRecheck 119; show SrcGitNoLazyFetch 49; show SrcGitNoLazyFetch 62; show SrcGitNoLazyFetch 144
cd /home/vgpnk/Projects/shokunin/souji-shokunin && show() { s=$1; l=$2; echo "### $s L$l"; nl -ba "history://SoujiR16.$s" | awk -v a=$l -v b=$l 'NR>=a && NR<=b'; }; show ConnLogConvention 132; show ConnQualityCriterion 84; show RevFixtureR16Edits 111; show RevIncludeResolve 100; show RevRedaction 72; show SrcGitConfigIncludesRecheck 94; show SrcGitConfigIncludesRecheck 118; show CriticDisclosureR3 80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(' '.join(i['name'] for i in d['items']))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && ls | head -3; echo "== ConnLogConvention"; grep -n 'sweep every mention' ConnLogConvention.md; echo "== ConnQualityCriterion"; grep -n 'Q2\\\[0-9\\\]\|Q2\[0-9\]\|criteria' ConnQualityCriterion.md | head -5; echo "== RevFixtureR16Edits"; grep -n 'HARM_CASES' RevFixtureR16Edits.md; echo "== RevIncludeResolve"; grep -n 'include_paths' RevIncludeResolve.md; echo "== RevRedaction"; grep -n 'include-protected' RevRedaction.md; echo "== SrcGitConfigIncludesRecheck"; grep -n 'round-16\*\|SOURCES-CONTRACT\*' SrcGitConfigIncludesRecheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i in d['items']: print(i['name'])
" > /var/tmp/r16-seats.txt; wc -l /var/tmp/r16-seats.txt; cat /var/tmp/r16-seats.txt | tr '\n' ' '
cd /home/vgpnk/Projects/shokunin/souji-shokunin && tot=0; totcall=0; missing=""; while read s; do u="history://SoujiR16.$s"; a=$(grep -c '^→ ' "$u"); b=$(grep -cE '^→ [A-Za-z_][A-Za-z0-9_.-]*\(' "$u"); tot=$((tot+a)); totcall=$((totcall+b)); [ "$a" != "$b" ] && missing="$missing $s:$a/$b"; done < <(python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'));print('\n'.join(i['name'] for i in d['items']))"); echo "arrow_lines=$tot callre=$totcall"; echo "mismatch:$missing"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && while read s; do u="history://SoujiR16.$s"; grep -nE 'souji-census\.sh' "$u" | sed "s|^|$s:|"; done < <(python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'));print('\n'.join(i['name'] for i in d['items']))")
cd /home/vgpnk/Projects/shokunin/souji-shokunin && while read s; do u="history://SoujiR16.$s"; grep -nE '^→ .*souji-census\.sh' "$u" | grep -vE 'bash -n|git (show|cat-file|diff|log|grep|status|rev-parse)|read\(|grep\(|\bawk\b|\bsed\b|\bsha256sum\b|\bnl\b|\bwc\b' | sed "s|^|$s:|"; done < <(python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'));print('\n'.join(i['name'] for i in d['items']))"); echo "=== end exec sweep"
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo "== ConnQualityCriterion SCORECARD"; grep -n 'SCORECARD.md' ConnQualityCriterion.md; echo "== RevListReposDoubleScan"; grep -n 'optional)' RevListReposDoubleScan.md | head; echo "== RevSoftPropagation"; grep -n "grep -rln 'optional'" RevSoftPropagation.md; echo "== RevFixtureR16Edits ctx"; grep -n 'include=\*.py' RevFixtureR16Edits.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for s in $(cat /var/tmp/r16-seats.txt); do echo "###SEAT $s"; cat "history://SoujiR16.$s"; done | python3 -c '
import sys,re
seat=None; pat=re.compile(r"^(?:\d+:)?→ ([A-Za-z_][\w.-]*)\((.*)\)\s*⇒\s*(\S+)")
surf=re.compile(r"\.omp/|\.ufo/state|watchdog\.log|operator-sweep")
sib=re.compile(r"/home/vgpnk/Projects/shokunin/(?!souji-shokunin)[A-Za-z0-9_-]+")
census=re.compile(r"souji-census\.sh")
python=re.compile(r"python3?\b.*(?:tools|tests/fixtures|census/round)[^\s]*\.py")
shell=re.compile(r"(?:^|[;&|]\s*)bash\s+(?!-n\b)[^\s]*\.(?:sh)\b|(?:^|[;&|]\s*)sh\s+[^\s]*\.sh\b")
direct=re.compile(r"(?:^|[;&|]\s*)(?:\./)?(?:tools|tests/fixtures)/[^\s]+\.(?:py|sh)\b")
redir=re.compile(r"(?:>>?|\btee\b)\s*[^\s|;)]*(?:souji-shokunin|\.ufo/waves|corpus/|tools/)")
for line in sys.stdin:
    line=line.rstrip("\n")
    if line.startswith("###SEAT "): seat=line[7:]; continue
    m=pat.match(line)
    if not m: continue
    tool,args=m.group(1),m.group(2)
    hits=[]
    if surf.search(args): hits.append("SURF")
    for h in sib.findall(args):
        if h not in ("souji-shokunin",): hits.append("SIB:"+h)
    if census.search(args) and re.search(r"souji-census\.sh\s+(?:--|-r\b)",args): hits.append("CENSUSRUN")
    if python.search(args): hits.append("PYLANE")
    if shell.search(args): hits.append("SH")
    if direct.search(args): hits.append("DIRECT")
    if tool=="bash" and redir.search(args): hits.append("REDIR")
    if tool in ("write","edit","ast_edit"): hits.append("WRITE:"+args[:90])
    if hits: print(seat,"|",tool,"|",",".join(hits),"|",args[:170])
' 2>&1 | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for s in $(cat /var/tmp/r16-seats.txt); do echo "###SEAT $s"; cat "history://SoujiR16.$s"; done | python3 -c '
import sys,re
seat=None
pat=re.compile(r"^(?:\d+:)?→ ([A-Za-z_][\w.-]*)\((.*)\)\s*⇒\s*(\S+)")
sib=re.compile(r"/home/vgpnk/Projects/shokunin/[a-z0-9]+-shokunin")
omp=re.compile(r"(?:~|/home/[^/\s]+)/\.omp/")
dirp=re.compile(r"/home/vgpnk/Projects/shokunin/souji-shokunin/(?:corpus|tools|tests|census|docs|\.ufo)(?:/[A-Za-z0-9_.-]+)*/?$")
pytest=re.compile(r"python3?\s+-m\s+(?:pytest|unittest)|\./(?:tests/fixtures|tools)/[^\s]+")
for line in sys.stdin:
    line=line.rstrip("\n")
    if line.startswith("###SEAT "): seat=line[7:]; continue
    m=pat.match(line)
    if not m: continue
    tool,args=m.group(1),m.group(2)
    hits=[]
    if sib.search(args): hits.append("SIB:"+sib.search(args).group(0))
    if omp.search(args): hits.append("OMP")
    if tool in ("read","glob","grep"):
        a=args.rstrip("…")
        p=a.split(" @ ")[-1].strip() if tool=="grep" else a
        p=p.split(";")[0].strip()
        if p.startswith("history://") or p.startswith("artifact://") or p.startswith("skill://"): pass
        elif dirp.search(p): hits.append("DIR:"+p[:90])
    if pytest.search(args): hits.append("PYEXEC")
    if hits: print(seat,"|",tool,"|",",".join(hits),"|",args[:150])
' 2>&1 | head -80; echo "=== roles"; python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i in d['items']:
    if i['name'] in ('LandingGate','LandingGateFixture','PreservationRepin','MutateScanConfig','MutateDirtyFilters','PlanWalk','SentinelStoreAccess','SentinelCommandExec','RevFixtureR16Edits','ConnQualityCriterion','ConnLogConvention','SrcPythonAst','CriticDisclosureR3'): print(i['name'],i['role'],'ALLOWED' if 'ALLOWED-EXEC:' in i['prompt'] else '-')
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== PlanWalk 150-165"; nl -ba 'history://SoujiR16.PlanWalk' | awk 'NR>=148 && NR<=164'; echo "== ALLOWED-EXEC seats"; python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
a=[i['name'] for i in d['items'] if 'ALLOWED-EXEC:' in i['prompt']]
print(len(a),a)
"; echo "== cwd render"; grep -c 'cwd' 'history://SoujiR16.PlanWalk'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SentinelStoreAccess calls"; grep -nE '^→ ' 'history://SoujiR16.SentinelStoreAccess' | cut -c1-300; echo; echo "== SentinelCommandExec calls"; grep -nE '^→ ' 'history://SoujiR16.SentinelCommandExec' | cut -c1-240
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for s in $(cat /var/tmp/r16-seats.txt); do echo "###SEAT $s"; cat "history://SoujiR16.$s"; done | python3 -c '
import sys,re,os
seat=None
pat=re.compile(r"^(?:\d+:)?→ ([A-Za-z_][\w.-]*)\((.*)\)\s*⇒\s*(\S+)")
lane="/home/vgpnk/Projects/shokunin/souji-shokunin"
fleet="/home/vgpnk/Projects/shokunin"
rec=re.compile(r"(?:^|[;&|]\s*)(?:find\s|rg\s|grep\s+-\w*r|ls\s+-\w*R)")
sib=re.compile(r"(?<!souji-)([a-z0-9]+)-shokunin")
omp=re.compile(r"\.omp/")
for line in sys.stdin:
    line=line.rstrip("\n")
    if line.startswith("###SEAT "): seat=line[7:]; continue
    m=pat.match(line)
    if not m: continue
    tool,args=m.group(1),m.group(2)
    if tool=="bash" and rec.search(args):
        audited = (lane in args or fleet in args or " . " in args)
        if not audited: print("REC-UNFLAGGED",seat,"|",args[:200])
    if tool in ("read","glob","grep") and not args.startswith(("artifact://","history://","skill://","/usr/")):
        a=args.rstrip("…")
        p=a.split(" @ ")[-1].strip() if tool=="grep" else a
        p=p.split(";")[0].strip().split(":")[0]
        if p.startswith(lane) and os.path.isdir(p): print("DIRTOOL",seat,tool,"|",p)
    if omp.search(args): print("OMP",seat,tool,"|",args[:160])
    for h in sib.finditer(args):
        if h.group(0)!="souji-shokunin": print("SIB",seat,tool,"|",h.group(0),"|",args[:150])
' 2>&1 | sort -u | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'matrix\|baseline\|r15-baseline\|syntax error' PlanWalk.md | head -20; echo "=== PlanWalk transcript 160-178"; nl -ba 'history://SoujiR16.PlanWalk' | awk 'NR>=160 && NR<=178' | cut -c1-400
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && awk '/^## Commands/{f=1} f' PlanWalk.md | grep -n 'census\|matrix\|baseline\|STATUS' | head -20; echo "=== raw around report line 180-195"; nl -ba PlanWalk.md | awk 'NR>=180 && NR<=195' | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for i in d['items']:
    if i['name']=='SiblingOverlap': print(i['prompt'][:2200])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for s in $(cat /var/tmp/r16-seats.txt); do echo "###SEAT $s"; cat "history://SoujiR16.$s"; done | python3 -c '
import sys,re
seat=None
pat=re.compile(r"^(?:\d+:)?→ ([A-Za-z_][\w.-]*)\((.*)\)\s*⇒\s*(\S+)")
lane="/home/vgpnk/Projects/shokunin/souji-shokunin"
gitmut=re.compile(r"git\s+(?:-C\s+\S+\s+)?(?:add|commit|stash|reset|checkout|restore|clean|rm|mv|apply|am|rebase|merge|cherry-pick)\b")
bashmut=re.compile(r"(?:>>?\s*|(?:^|[;&|]\s*)(?:sudo\s+)?(?:rm|mv|cp|mkdir|touch|tee|chmod|chown|ln|truncate)\b)")
for line in sys.stdin:
    line=line.rstrip("\n")
    if line.startswith("###SEAT "): seat=line[7:]; continue
    m=pat.match(line)
    if not m: continue
    tool,args=m.group(1),m.group(2)
    if tool!="bash": continue
    if gitmut.search(args): print("GITMUT",seat,"|",args[:200])
    if bashmut.search(args):
        if re.search(r"(?:souji-shokunin|\.ufo/|corpus/|tools/|tests/|census/round)",args): print("BASHMUT",seat,"|",args[:220])
' 2>&1 | sort -u | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && while read s; do u="history://SoujiR16.$s"; grep -nE 'MANIFEST\.json|watchdog\.log|\.ufo/state|operator-sweep|/\.omp/' "$u" | grep -E '^[0-9]+:→ |MANIFEST\.json' | sed "s|^|$s:|" | cut -c1-260; done < <(cat /var/tmp/r16-seats.txt); echo "=== end"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for s in $(cat /var/tmp/r16-seats.txt); do echo "###SEAT $s"; cat "history://SoujiR16.$s"; done | python3 -c '
import sys,re
seat=None
pat=re.compile(r"^(?:\d+:)?→ ([A-Za-z_][\w.-]*)\((.*)\)\s*⇒\s*(\S+)")
repdir=".ufo/waves/round-16/w1"
trunc=0; n=0
for line in sys.stdin:
    line=line.rstrip("\n")
    if line.startswith("###SEAT "): seat=line[7:]; continue
    m=pat.match(line)
    if not m: continue
    tool,args=m.group(1),m.group(2); n+=1
    if args.endswith("…"): trunc+=1
    if re.search(r"xd://|local://|artifact://|proc://",args) and tool in ("write","edit"): print("DEVWRITE",seat,"|",args[:120])
    if tool in ("write","edit","ast_edit"):
        t=args.strip()
        mm=re.match(r"^(?:\*\*\* Begin Patch\s*)?\[([^\]#]+)",t)
        t=mm.group(1).strip() if mm else t.split(",",1)[0].strip()
        if t.startswith(repdir+"/") and not t.endswith("/"+seat+".md"):
            print("CROSSREPORT",seat,"|",t)
    if tool=="bash" and re.search(r"souji-census\.sh\s+--root=",args): print("ROOTEQ",seat,"|",args[:150])
print("TOTAL",n,"TRUNC",trunc)
' 2>&1 | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'pid=\|wait "\|:(optional)' RevListReposDoubleScan.md | head -8; echo ===; grep -n 'w1 &&\|w1/' RevListReposDoubleScan.md | head -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'SURFACE_RE = \|RECURSIVE_BASH_RE = \|rstrip("…")\|V-WRITE-UNKNOWN\|EXEC_RE = \|allowed_target\|startswith("/var/tmp/")\|LIVE_CENSUS_RE = \|args\[:200\]' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo "== SrcPythonAst commands"; grep -n 'grep -rn' SrcPythonAst.md | head -8; echo "== RevFixture commands"; awk '/^## Commands/{f=1} f' RevFixtureR16Edits.md | grep -n 'HARM_CASES\|include='; echo "== NoLazyFetch disclosure"; grep -n 'placeholder\|r16-placeholder' SrcGitNoLazyFetch.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,subprocess
d=json.load(open('census/round-16/seat-audit-w1.json'))
v=[x for s in d['seats'].values() for x in s['violations']]
print('violations',len(v),'major',sum(x['severity']=='major' for x in v),'minor',sum(x['severity']=='minor' for x in v))
print('truncated-arg violations',sum('…' in x['args'] for x in v))
import collections
print(collections.Counter(x['class'] for x in v))
bad=[]
for k,s in d['seats'].items():
    n=int(subprocess.run(['grep','-c','^→ ','history://SoujiR16.'+k],capture_output=True,text=True).stdout.strip() or 0)
    if n!=s['calls']: bad.append((k,s['calls'],n))
print('per-seat call mismatches',bad)
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== PlanWalk transcript calls containing 'ls -'"; grep -nE '^→ bash\(' 'history://SoujiR16.PlanWalk' | grep -E 'ls -' | cut -c1-260; echo; echo "== PlanWalk report cmd with ls -R"; grep -n 'ls -R' .ufo/waves/round-16/w1/PlanWalk.md | cut -c1-260
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -nHE '(^|[;&|] )(find |rg |grep -[a-zA-Z]*r|ls -[a-zA-Z]*R)' *.md | grep -v '^.*:[0-9]*:.*#' | cut -c1-220 | head -40; echo "=== count"; grep -hE '(^|[;&|] )(find |rg |grep -[a-zA-Z]*r|ls -[a-zA-Z]*R)' *.md | wc -l
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== PlanWalk call for report:292"; grep -nE '^→ bash\(' 'history://SoujiR16.PlanWalk' | grep -E 'git log --oneline -8|R16 WAVE' | cut -c1-320; echo; echo "== SrcPythonAst call for report:165"; grep -nE '^→ bash\(' 'history://SoujiR16.SrcPythonAst' | grep -E 'souji-landing-gate|w1:' | cut -c1-340
mkdir -p /var/tmp/souji-r16-RerunSeatAudit-4 && cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
for k,v in sorted(d['seats'].items()): print(k,v['calls'])
" > /var/tmp/souji-r16-RerunSeatAudit-4/json.txt && while read s; do printf '%s %s\n' "$s" "$(grep -c '^→ ' "history://SoujiR16.$s")"; done < <(cut -d' ' -f1 /var/tmp/souji-r16-RerunSeatAudit-4/json.txt) > /var/tmp/souji-r16-RerunSeatAudit-4/live.txt && join /var/tmp/souji-r16-RerunSeatAudit-4/json.txt /var/tmp/souji-r16-RerunSeatAudit-4/live.txt | awk '$2!=$3{print "MISMATCH",$0; n++} END{print "mismatches="n+0}'; echo "== aborted calls"; while read s; do grep -n 'was not executed because the provider stream ended' "history://SoujiR16.$s" | sed "s|^|$s:|"; done < <(cut -d' ' -f1 /var/tmp/souji-r16-RerunSeatAudit-4/json.txt)
rm -rf /var/tmp/souji-r16-RerunSeatAudit-4 /var/tmp/r16-seats.txt
```
