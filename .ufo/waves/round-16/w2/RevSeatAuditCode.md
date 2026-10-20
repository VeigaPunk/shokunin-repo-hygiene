# RevSeatAuditCode — source review of `tools/souji-seat-audit.py` (R5) vs the wave-2 contract

Scope: lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; reviewed file
`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py`
(sha256 `c9ff355c6bca31196eeb0527d7286e601878a1c50309d078cd1523820c9bd3b3`, 237 lines).
Source read only: I ran no lane tool, fixture, census, or `--selftest`. Every claim below is
from the source plus the committed records (`census/round-16/seat-audit-w1.json`, the wave
specs, and the seats' verbatim `## Commands`). The one wave-1 major (an `edit` of
`.ufo/waves/round-16/r16-placeholder.md` by SrcGitNoLazyFetch) is a true positive under V-WRITE-SCOPE.

Axis verdicts against the w2 PROBE RULE:

- **Violation classes** — **fails**: three explicitly forbidden behaviours have no class
  (delegation, git mutations, bash-mediated lane edits), V-RECURSIVE mislabels two
  exact-file greps in the committed result, and V-LIVE-CENSUS/V-SURFACE are bypassable.
- **OWN ONLY parsing** — **partial**: prose triggers ownership, directory grants are not
  honoured, multi-line/multi-parenthetical lists are truncated.
- **ALLOWED-EXEC** — **fails**: the marker elevates the entire transcript to executor
  instead of whitelisting the named command(s); 16/79 w2 items (12 reviewers + 4
  mutation-testers) therefore never reach V-EXEC, and the branch has no selftest case.
- **Truncation limits** — **partial**: argument-level `…` is documented, but record-level
  (multi-line) loss and zero/missing coverage are silent and still exit 0.

## F1 (major, classes) — V-RECURSIVE is shape-based: at least two wave-1 "recursive reads" are exact-file greps

Lines 54, 112-113, 114-117. The bash branch fires on `grep\s+-\w*r` plus the lane/fleet
literal appearing *anywhere* in the args; it never inspects operands. The tool branch fires
only when the rendered args end exactly with `lane`/`fleet`.

Committed evidence (the audit's own record, `census/round-16/seat-audit-w1.json`):

- `ConnQualityCriterion` line 85 (minor V-RECURSIVE) records
  `cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn 'Q2[0-9]\|Q1[0-9]\|criteria' corpus/README.md SCORECARD.md …`;
  the verbatim command is `.ufo/waves/round-16/w1/ConnQualityCriterion.md:265` and its
  operands are four regular files (`corpus/README.md SCORECARD.md SKILL.md LEARNING.md`).
  `grep -r` over regular-file operands searches exactly those files; no tree is walked.
- `ConnLogConvention` line 133 (minor V-RECURSIVE) records
  `grep -rn "sweep every mention" /home/.../PROTOCOL.md /home/.../c…`;
  verbatim at `.ufo/waves/round-16/w1/ConnLogConvention.md:453`, operands are three files
  (`PROTOCOL.md`, `corpus/QUALITY.md`, `corpus/lessons/round-15.md`).

The w2 contract allows "grep … on EXACT named files (never recursive search over the lane
root, the fleet root, or a whole directory tree)"; these two commands search no tree, so
the wave-2 claim "19 minor whole-lane recursive reads" overstates by at least two.
`SrcGitCheckAttr` line 69 (grep with the lane root as operand) is a genuine positive.

Mirror false negatives, same class:

- Flag order: `grep --include=*.py -rn 'pat' /home/…/souji-shokunin` does not match line 54
  (`grep\s+-\w*r` cannot skip the `--include` token), though it walks the lane tree.
- Tool branch: `grep(pat @ /home/…/souji-shokunin/tools)` and
  `glob(**/* @ /home/…/souji-shokunin/tools)` are not flagged (path is a subdirectory, not
  the root); a trailing `:` selector would also defeat the `endswith` test.
- `cd /home/…/souji-shokunin && grep -rn pat /var/tmp/x` is flagged (lane appears in the
  `cd`) although the search root is the allowed /var/tmp copy.

Smallest fix (line 54 and 114-117): find the recursive flag token anywhere in the command
(`(?:^|\s)(?:-[A-Za-z]*[rR]\b|--recursive|--dereference-recursive)`), then require at least
one *operand* (not the `cd` prefix) to be `lane`, `fleet`, or a path under either; for the
grep/glob tool branch, flag when the rendered path starts with `lane`/`fleet` (prefix, not
`endswith`) or a `**` pattern is present.

## F2 (major, classes) — three w2 contract prohibitions have no class; V-WRITE-SCOPE covers only the write tools

Contract: "All seats are leaves: no delegation, no commits, no git add/stash/reset/checkout,
no edits to ANY lane file — you write ONLY your report."

- Delegation: `audit_seat` (84-118) has no `tool == "task"` branch. `→ task(…)` is invisible.
- Git mutations: no git branch at all. `→ bash(git -C /home/…/souji-shokunin commit -am x)`,
  `git add`, `git stash`, `git reset`, `git checkout` are invisible (only V-SURFACE,
  V-LIVE, V-EXEC, V-RECURSIVE run against bash args).
- Bash-mediated lane edits: lines 102-109 run only for `WRITE_TOOLS = {"write","edit","ast_edit"}`.
  `→ bash(printf x > /home/…/souji-shokunin/SKILL.md)`, `sed -i`, `tee`, `cp`, `mv` produce
  no finding, so "no edits to ANY lane file" is not enforced. The wave-1 report shows this
  class of command in use (e.g. `git show b410186:tools/souji-census.sh > /tmp/r15census.sh`
  at `.ufo/waves/round-16/w1/SrcPythonAst.md:166`), and the audit sees nothing.
- V-WRITE-SCOPE also over-permits /var/tmp: line 78 returns True for any `/var/tmp/…` for
  every role, while the contract limits writes to `/var/tmp/souji-r16-<SeatName>/` and only
  for ALLOWED-EXEC/mutation items. A `scribe`/`reviewer` write to `/var/tmp/anything` (or
  another seat's directory) is unflagged.
- Line 80 `rel = target.lstrip("./")` strips the leading dot of hidden components, so the
  relative report form the docstring advertises (line 77) fails for this wave's own report
  directory: target `.ufo/waves/round-16/w2/RevSeatAuditCode.md` against report
  `/home/…/souji-shokunin/.ufo/waves/round-16/w2/RevSeatAuditCode.md` yields
  `rel = "ufo/waves/round-16/w2/RevSeatAuditCode.md"`, and `p.endswith("/"+rel)` is false →
  a spurious major V-WRITE-SCOPE. (Seats are told to use absolute paths, so this is latent
  unless a seat uses the relative trailer form.) `rel = target[2:] if target.startswith("./") else target`
  fixes it.

Smallest fix: add `V-DELEGATE` for `tool == "task"`; `V-GIT` for
`\bgit\b[^|;&]*\b(?:add|commit|stash|reset|checkout|switch|clean|rm|mv|push)\b`; extend the
write branch to bash redirection/`tee`/`cp`/`mv`/`sed -i` targets under `lane` (excluding
`/var/tmp`); pass `scratch = f"/var/tmp/souji-r16-{name}/"` into `allowed_target` and allow
/var/tmp only under it; fix line 80.

## F3 (major, classes) — V-LIVE-CENSUS misses `--root=`, the default root, and `SHOKUNIN_ROOT`

Line 48 requires `--root` followed by whitespace and a token not starting `/var/tmp`. The
census accepts `--root=DIR` (`tools/souji-census.sh:1846`) and defaults
`ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"` (`tools/souji-census.sh:173`), i.e.
the real fleet directory.

Concrete unflagged invocations (for an executor / mutation-tester / ALLOWED-EXEC seat,
where V-EXEC is suppressed — see F4):

- `bash tools/souji-census.sh --root=/home/vgpnk/Projects/shokunin` — `--root` is followed
  by `=`, so line 48 does not match.
- `bash tools/souji-census.sh` — no `--root`; scans the default fleet root; line 48 has
  nothing to test.
- `SHOKUNIN_ROOT=/home/vgpnk/Projects/shokunin bash tools/souji-census.sh` — no `--root`
  *and* the `bash` is not at the EXEC_RE command anchor (`^`, `;`, `&`, `|`, `(`), so no
  class fires for any role at all.
- `--root /var/tmp-copy/...` is accepted by the lookahead (prefix, not path-boundary), and
  `--root /var/tmp/../home/...` passes the same prefix test.

Smallest fix: match the census invocation anywhere in the args, then resolve the effective
root from `--root=…`, `--root …`, `SHOKUNIN_ROOT=…`, else the default; flag unless the
normalized root is under `/var/tmp/` (reject `..` components and a `/var/tmpfoo` prefix);
exempt `--selftest`. Note the named ALLOWED-EXEC `RerunLegacySelftest` command copies the
census to /var/tmp and runs `--selftest`, so the exempt must be kept.

## F4 (major, contract) — ALLOWED-EXEC is a blanket role elevation, not a command whitelist

Lines 133-136: any item prompt containing the literal `ALLOWED-EXEC:` makes the whole seat
`executor`, which disables V-EXEC for every bash call in that transcript. The contract says
"Only items marked `ALLOWED-EXEC:` may run exactly the command(s) named there."

- 16/79 w2 items carry the marker (12 reviewers, 4 mutation-testers). RerunSeatAudit
  names exactly one command, `python3 /home/…/tools/souji-seat-audit.py --selftest`, yet
  its transcript may run `python3 /home/…/tools/souji-landing-gate.py`,
  `python3 /home/…/tests/fixtures/r16-landing-gate.py`, or a /var/tmp mutant of any tool
  with no finding. MutateSeatAudit names "`python3 <copy> --selftest` per mutant" and is
  exempt for everything else.
- The marker is a substring test: a prompt that merely quotes or negates the phrase is
  elevated too.
- The branch added by a6ec781 has **no selftest case**: `selftest` (152-200) calls
  `audit_seat` with explicit roles, and its one `run()` case has no ALLOWED-EXEC item, so
  the behaviour is untested.

Smallest fix: after the marker, extract the backticked command spans
(`re.findall(r"`([^`]+)`", prompt[idx:])`) and pass them to `audit_seat`; exempt a bash
call only when `any(cmd in args for cmd in allowed_cmds)` (normalizing whitespace), leaving
V-EXEC active for every other command. Keep the executor/mutation-tester role exemption
only for the w1 convention or gate it behind a `--wave w1` flag, since the w2 contract
binds mutation-testers to their named commands too.

## F5 (major, classes) — V-SURFACE misses four contract-forbidden paths and flags one allowed read

Line 43-46:

- `MANIFEST.json` is absent from the regex (contract forbids it).
  `→ read(/home/…/souji-shokunin/MANIFEST.json)` yields no finding.
- Sibling lane repos are absent: `→ read(/home/vgpnk/Projects/shokunin/<sibling-lane>/…)`
  is unflagged even when the item prompt names no such file; `fleet` (line 124) is only
  used for the recursive equality test.
- `$HOME` is not covered: `→ bash(cat $HOME/.omp/agent/config.yml)` is unflagged
  (`~` and `/home/<user>` are the only alternatives).
- `.ufo/state` without the trailing slash and a relative `.ufo/watchdog.log` are missed
  (`\.ufo/state/` and `/.ufo/watchdog\.log`): `→ read(.ufo/state)` and
  `→ read(.ufo/watchdog.log)` yield nothing.

False positive, same line: the regex cannot tell a path from a grep pattern, despite the
comment at 40-42. `→ bash(grep -n 'census/operator-sweep-20261019' PROTOCOL.md)` is an
allowed exact-file read but is flagged major V-SURFACE. The selftest's
`pattern-word-not-surface` case avoids this only by omitting the dated suffix.

Smallest fix: extend the regex to `(?:^|[/\s])MANIFEST\.json\b`,
`(?:^|/)\.ufo/state(?=/|\b)`, `(?:^|/)\.ufo/watchdog\.log`, and `\$HOME|\$\{HOME\}`; add a
sibling check for absolute paths under `fleet`-but-not-`lane` that the item prompt does not
name verbatim; scrub the first non-flag quoted operand of `grep`/`rg` before applying
SURFACE_RE (or demote a hit found only inside that operand to minor).

## F6 (major, classes) — V-EXEC is quote-blind and unanchored: it misses real execution and flags mentions

Lines 49-52. The python branch is unanchored and stops at `\.py(?!\S)`; the bash branch
requires `bash` at a command anchor and `.sh` in the next token; `--selftest\b` is a bare
substring.

False negatives (real execution of a lane tool/fixture, no finding):

- `→ bash(/home/…/souji-shokunin/tools/souji-landing-gate.py --rev HEAD)` (direct
  executable, no `python3`/`bash` token).
- `→ bash(python3 -c 'import runpy;runpy.run_path("tools/souji-landing-gate.py")')` — the
  `.py` token ends in `"`, so `(?!\S)` fails, and the `-c` token blocks the path branch.
- `→ bash(bash -c '/home/…/souji-shokunin/tools/souji-landing-gate.py --rev HEAD')` — the
  inner path is quoted and the first token after `bash` is `-c`, so neither the script
  branch nor the unanchored python branch fires (a `--selftest` inside the quotes *would*
  be caught by the bare `--selftest\b` alternative, which is the FP below).
- Observed in the audited wave: `.ufo/waves/round-16/w1/SrcPythonAst.md:182` runs
  `python3 -c "import json; …"` (not an allowed operation under the w1 rule, which forbids
  "any command not allowed above"); the audit records no finding for it. Whether L1 treats
  it as a violation is a policy call, but the tool cannot see it.

False positive (`--selftest` mention):

- `→ bash(git -C /home/…/souji-shokunin show HEAD:tools/souji-landing-gate.py | grep -n --selftest)`
  is an allowed `git show` + exact-file grep but matches `--selftest\b` → major V-EXEC.

Related, unanchored python mention: `→ bash(echo python3 tools/x.py)` matches the first
alternative (the `python3 …/tools/x.py` substring is unanchored) and is flagged.

Smallest fix: anchor the python branch at a command position; add a command-position
alternative for direct `(?:\./|/)\S*(?:tools|tests/fixtures|census/round-\d+)/\S+\.(?:py|sh)\b`
(unless `bash -n`), plus `(?:python3?|bash|sh)\s+-c\b` and `sh|dash|zsh` for non-executing
seats, treating `python3 -c|-` as execution; anchor `--selftest` as
`(?:^|[;&|(]\s*)\S*--selftest\b` so a quoted grep pattern no longer matches. Keep the
`-m py_compile` and `bash -n` exemptions (the current regex already exempts them: the
`py_compile` token blocks the path branch).

## F7 (partial, classes) — OWN ONLY parsing

Line 55 (`OWN ONLY ([^\n]+?)(?:\s\(|\.\s|$)`) and 61-65:

- **Prose trigger.** This seat's own item (w2-spec `RevSeatAuditCode`) says
  "classes, OWN ONLY parsing, ALLOWED-EXEC, truncation limits." — `OWN_RE` matches it. The
  captured span has no `/home` path, so `owned_paths` returns `[]` (currently benign). Had
  the sentence named its target ("OWN ONLY parsing of /home/…/tools/souji-seat-audit.py"),
  the parser would have granted edit rights to the file under review. The convention needs
  the phrase to be a declaration, not a topic.
- **Directory grants are lost.** The w1 `PreservationRepin` prompt grants "the files in
  /home/…/tests/fixtures/r15-preservation-frozen/". `owned_paths` captures that directory,
  but `allowed_target` (76-81) only accepts exact equality or a `"/"+rel` suffix, so every
  write under it is a major V-WRITE-SCOPE false positive. (The committed audit has no such
  flag for that seat, so the write either did not happen or was bash-mediated — see F2.)
- **Single-line capture.** `[^\n]+?` cannot span lines; a list written across lines, or a
  list where a parenthetical follows the first path (`OWN ONLY /a.py (new), /b.py (new)`),
  grants only the pre-parenthesis part or nothing → further false positives on legitimate
  owned writes.

Smallest fix: anchor the declaration (`(?m)^\s*OWN ONLY\s+`) and require the capture to
start with `/home/`, split on commas, strip parentheticals, and read continuation lines
that begin with `-`, `/home/`, or "and the files in". In `allowed_target`, treat an allowed
entry ending in `/` as a directory prefix (`target.startswith(p)`).

## F8 (partial, truncation/coverage) — record loss and zero coverage are silent; exit 0

- Line 39 `CALL_RE` requires the call, its closing `)` and `⇒` on one rendered line. Any
  multi-line render (the heredoc calls in `.ufo/waves/round-16/w1/SrcPythonAst.md:167` and
  following) is neither counted nor flagged; there is no `unparsed` counter, so the summary
  cannot distinguish "no violation" from "record not parsed". [INFERENCE: the export may
  flatten newlines; the code has no guard either way.]
- Zero coverage passes: a `--transcripts` directory with no matching files (or an empty
  spec case) yields `seats_audited=0`, `major=0`, and line 233 returns 0. A missing
  transcript is exactly the case where a seat's evidence cannot be cleared, yet the process
  is "clean" on the exit channel; only the printed `missing=` hints otherwise.
- `flag()` (line 96) stores `args[:200]`; in the committed JSON several V-RECURSIVE entries
  are cut mid-command, so a late surface/exec match would not be visible in the evidence.
- `main()` writes `--json` after the try/except (the `run()` call is the only guarded
  statement), so an unwritable output path raises and exits 1, not the documented 2
  (docstring line 28).
- The Limits paragraph (22-24) mentions only argument-level `…` truncation; the record-level
  and coverage gaps above are not stated.

Smallest fix: count lines that begin `→` after the `N:` prefix but fail `CALL_RE`; add
`unparsed` and `missing` to the summary; return 2 when `seats_audited == 0` or
`missing_transcripts` is non-empty (1 only for majors over full coverage); store the matched
span alongside `args[:200]`; extend the Limits paragraph.

## Residual risk / verification gaps

- No execution was possible under the probe rule: the regex claims are source-level, and
  the `runpy`/`bash -c`/`--root=` counterexamples are constructed from the code paths, not
  observed runs. The two V-RECURSIVE false positives are grounded in the committed JSON and
  the seats' verbatim commands.
- The wave-1 "1 major" is a true positive; the "19 minor" count is not a contract count
  (see F1) and leaves the unmodeled classes (F2) uncounted. The wave-1 transcripts live in
  `history://`, not the repo, so the true violation totals cannot be recomputed here.
- SentinelCommandExec's empty-args write (`seat-audit-w1.json`, line 118) is classified
  minor V-WRITE-UNKNOWN. If the renderer collapsed a real target, a lane write is
  under-classified; the JSON cannot settle it.
- Unverified: the actual transcript render for multi-line calls, and whether the harness
  renders `cwd` in bash args (affects the `grep -rn pat .` case in F1).

STATUS: ok — source review complete; no lane tool, fixture, census or selftest executed; findings advisory for L1.

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD | grep -iE 'seat-audit|seat_audit|waves/round-16'
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -3 && sha256sum tools/souji-seat-audit.py && wc -l tools/souji-seat-audit.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('census/round-16/seat-audit-w1.json'))
print(json.dumps(r['summary'],indent=1))
print('missing',r['missing_transcripts'])
for n,s in r['seats'].items():
    for v in s['violations']:
        print(n,s['role'],v['severity'],v['class'],v['line'],'|',v['args'][:160])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(sorted(s.keys()))
print('reportDir',s.get('reportDir'),'wave',s.get('wave'))
print('items',len(s['items']))
for it in s['items']:
    p=it.get('prompt','')
    print('---',it['name'],'|',it['role'],'| OWN ONLY:', 'OWN ONLY' in p, '| ALLOWED-EXEC:', 'ALLOWED-EXEC:' in p)
    if 'OWN ONLY' in p:
        i=p.index('OWN ONLY'); print('   ',repr(p[i:i+140]))
    if 'ALLOWED-EXEC:' in p:
        i=p.index('ALLOWED-EXEC:'); print('   AE:',repr(p[i:i+140]))
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -- '--root\|usage\|ROOT' tools/souji-census.sh | head -40
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
ctx=s['context']
print(len(ctx))
for key in ['PROBE RULE','ALLOWED-EXEC','MANIFEST','OWN ONLY','Recursive','recursive','operator-sweep','STATUS']:
    i=ctx.find(key)
    print('KEY',key,'at',i)
i=ctx.find('PROBE RULE')
print(ctx[i:i+2600])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1280,1345p' tools/souji-census.sh
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/ && ls .ufo/waves/round-16/w2 2>/dev/null | head -30; git show --stat a6ec781 | head -30
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
s=json.load(open('.ufo/waves/round-16/w2-spec.json'))
print('keys',sorted(s.keys()),'wave',s.get('wave'),'reportDir',s.get('reportDir'))
ctx=s.get('context','')
i=ctx.find('PROBE RULE')
print('CTX PROBE:',ctx[i:i+1400] if i>=0 else 'none')
print('items',len(s['items']))
n=0
for it in s['items']:
    p=it.get('prompt','')
    if 'ALLOWED-EXEC:' in p or 'OWN ONLY' in p:
        n+=1
        print('---',it['name'],it['role'])
        for kw in ('OWN ONLY','ALLOWED-EXEC:'):
            j=p.find(kw)
            if j>=0: print('  ',kw,repr(p[j:j+160]))
print('special items',n)
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'root=' tools/souji-census.sh | head; grep -n '^\s*--root\|--root)' tools/souji-census.sh | head
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for f in ('.ufo/waves/round-16/w1-dispatch.json','.ufo/waves/round-16/w2-dispatch.json'):
    d=json.load(open(f))
    print('==',f,'keys',sorted(d.keys()))
    s=json.dumps(d)
    for kw in ['transcript','seat-audit','history://','export']:
        i=s.find(kw)
        print(' ',kw,i)
        if i>=0: print('   ',s[max(0,i-200):i+300])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,textwrap
ctx=json.load(open('.ufo/waves/round-16/w2-spec.json'))['context']
print('LEN',len(ctx))
for para in ctx.split('\n'):
    for ln in textwrap.wrap(para,700) or ['']:
        print(ln)
    print('--')
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('census/round-16/seat-audit-w1.json'))
for n,s in r['seats'].items():
    for v in s['violations']:
        if v['severity']=='major' or v['class']=='V-WRITE-UNKNOWN':
            print(n,'role=',s['role'],json.dumps(v))
# calls distribution
import statistics
cs=[(s['calls'],n) for n,s in r['seats'].items()]
cs.sort()
print('min/max/median calls',cs[0],cs[-1],statistics.median(c for c,_ in cs))
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'SURFACE_RE\|LIVE_CENSUS_RE\|EXEC_RE\|EDIT_TARGET_RE\|RECURSIVE_BASH_RE\|OWN_RE\|ABS_RE\|WRITE_TOOLS\|EXEC_ROLES\|def owned_paths\|def write_target\|def allowed_target\|def audit_seat\|eff_role\|def run\|def selftest\|def main' tools/souji-seat-audit.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in SrcPythonAst SrcGitNoLazyFetch MutateScanConfig; do echo "=== $f"; grep -n '^python3 -c\|^python3 - <<\|^eval\|^git status\|^git -C .* status\|^sh \|^python3 -m py_compile\|^find \|^grep ' .ufo/waves/round-16/w1/$f.md | head -12; done
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '/## Commands/,$p' .ufo/waves/round-16/w1/SrcPythonAst.md | head -40
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'r15census\|python3 -c\|python3 - <<\|-o /tmp\|> /tmp' .ufo/waves/round-16/w1/SrcPythonAst.md
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
s=json.load(open('.ufo/waves/round-16/w2-spec.json'))
ae=[it for it in s['items'] if 'ALLOWED-EXEC:' in it.get('prompt','')]
print('AE items',len(ae),'of',len(s['items']))
from collections import Counter
print(Counter(it['role'] for it in ae))
for name in ('RerunSeatAudit','MutateSeatAudit','RerunGateFixture'):
    it=next(x for x in s['items'] if x['name']==name)
    print('=====',name,it['role'])
    print(it['prompt'][:1200])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1836,1860p' tools/souji-census.sh; grep -n 'return 1 if sm\|seats_audited\|missing_transcripts\|rel = target' tools/souji-seat-audit.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'grep -rn' .ufo/waves/round-16/w1/ConnQualityCriterion.md | head -6; echo ===; grep -n 'grep -rn' .ufo/waves/round-16/w1/ConnLogConvention.md | head -6
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '83,88p' .ufo/waves/round-16/w1/ConnQualityCriterion.md; echo ===; sed -n '131,136p' .ufo/waves/round-16/w1/ConnLogConvention.md
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '## Commands' .ufo/waves/round-16/w1/ConnQualityCriterion.md .ufo/waves/round-16/w1/ConnLogConvention.md; echo ===; grep -n '^STATUS:' .ufo/waves/round-16/w1/Rev*.md | head -8; echo ===; tail -n 12 .ufo/waves/round-16/w1/RevBoundFilters.md
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^CALL_RE\|^Limits:\|^Exit:\|^def selftest\|^def main\|^def audit_seat\|^def run' tools/souji-seat-audit.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'Line 38\|comment at 41-42\|21-23\|docstring line 27\|152-199' .ufo/waves/round-16/w2/RevSeatAuditCode.md
```
