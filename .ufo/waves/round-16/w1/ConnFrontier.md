# ConnFrontier — r16 frontier & province accounting

**Verdict: frontier UNCHANGED (F1–F4). Province surface: no new ground and no
Core/Work-surface change; one boundary clarification is drafted below but is
NOT admitted — gate it on L1 acceptance of C1. C2 is absent at this
checkpoint and is calibration repertoire, not a province surface.**

Read-only accounting over the committed state at `cbf688a` plus in-flight
round artifacts. I ran no census and touched no live repository; acceptance is
L1's, and nothing here promotes an author artifact to an accepted observation.

## 1. Why no frontier row moves

- `git show --stat cbf688a` touches exactly three files:
  `census/round-16/run-matrix.py`, `tests/fixtures/r15-census-config.py`,
  `tools/souji-census.sh`. No `corpus/knowledge/`, `corpus/README.md`,
  `PROVINCE.md` or `SKILL.md` byte changed.
- `corpus/README.md`, `PROVINCE.md` and `corpus/knowledge/` were last committed
  at `b410186` and are clean in the working tree (7 knowledge files: the 5
  admitted entries + `obsidian-ledger.tsv` + HELD K5 — same set as r15).
- The 65-item w1 spec has no item owning a `corpus/knowledge/` entry, and no
  item names `OWN ONLY` on `corpus/README.md` or `PROVINCE.md`; the two items
  mentioning `PROVINCE.md` (`SiblingOverlap`, this one) are report-only
  connectors. So no r16 artifact can satisfy PROVINCE.md:50-51's move-to-Core
  rule (“an admitted `corpus/knowledge/` entry and a SKILL rule”).
- The wave's own surfaces are census-config operability (C1) and landing
  calibration (C2). Neither is an F1–F4 ground.

## 2. Per-row check

### F1 git-native housekeeping vs receipts — UNCHANGED
- Live cursor: `corpus/README.md:46` — “next: does `fetch`/`merge`/`rebase`
  auto-maintenance prune on the fleet's live repos (… 0 prunable, 3 locked
  today)”. The cited numbers are an r12 measurement: `census/round-12/scout-surfaces.md:1-4`
  records 2026-10-19 ~18:45–18:50 at lane HEAD `dcc8b9e`; line 18 shows the
  only lock/`locked=3` row (`game-dev-2d-shokunin`), with
  `maintenance.auto`/`gc.worktreePruneExpire` unset fleet-wide.
- r16 authors no observation harness for git's deleters. The repaired census
  contains no `fetch`/`merge`/`rebase`/`maintenance` invocation, and its own
  selftest asserts `fetch|push|commit|branch|checkout|reset|rebase|prune` are
  absent from non-comment lines (`tools/souji-census.sh:1727-1731`).
- Second-order: the receipt-side census is more usable after C1, but F1's
  question is about git's behavior on live repos. That remains a separate,
  unrun observation. No movement.

### F2 repository size census — UNCHANGED, but the live “next” pointer is stale
- `corpus/README.md:47` still says “next: the /var/tmp write-safety fixture for
  `git repo structure`”. That fixture was acquired and executed in r13:
  `tests/fixtures/r13-repo-structure.sh:2` is the “F2 size-census write-safety
  fixture”, `:107`/`:159-160` hard-code `mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX`,
  and `census/round-13/verification.json` records result `structure-selftest`
  (`bash tests/fixtures/r13-repo-structure.sh --selftest --probe
  tools/souji-repo-structure.sh`) as exit 0, matched true, with PASS cases, at
  measured commit `6f8ee0f`.
- The README contradicts itself: `:64` says the r13 table “supersedes the r12
  F2 row” and `:68` says “bounded structure-census capability acquired; wider
  size attribution remains frontier”; `PROVINCE.md:55-57` agrees (“isolated
  write-safety fixture acquired r13; whole-workspace size attribution and
  unreachable-object census remain frontier”).
- r16 adds no size attribution: the census TSV columns are unchanged
  (`tools/souji-census.sh:24`), and the `cc21683`→`cbf688a` diff has no
  changed (`^[-+]`) line touching `scratch_bytes`, `du -sb`, `repo structure`,
  `count-objects` or the TSV header.
- So: no frontier advance; only a stale live pointer. Correcting the pointer is
  a documentation correction, not an r16 capability.

### F3 duplicate verdicts — UNCHANGED
`corpus/README.md:48` makes a `duplicate` receipt class an operator taxonomy
decision. r16's routed defect R7 opens a `rejected` **source-registry** row for
git-status(1); that is a SOURCES status (“source not mined”), not a receipt
class. The vocabularies must not be conflated.

### F4 restorable quarantine — UNCHANGED
`corpus/README.md:49`'s next step is operator-owned (per-item origin records,
`mv --no-copy` staging). The 65-item spec contains no quarantine item, and
`cbf688a` does not touch `tools/souji-quarantine.sh` or
`tests/fixtures/r13-quarantine-bounds.sh`.

## 3. Province surface

### 3.1 Owns / Work surfaces / Refuses — unchanged
C1 narrows *when* the census refuses whole runs; it does not widen what souji
may remove, add a work surface, or add a refused surface. `PROVINCE.md`'s
`## Refuses` rows are untouched (credential content, history rewrite, operator
config, dirty/unpushed lane artifacts).

### 3.2 A defensible boundary clarification — DRAFT ONLY, GATE IT
If (and only if) L1 accepts C1, this paragraph is honest against the committed
header (`tools/souji-census.sh:86-124`), and it contrasts with the r14 policy at
`cc21683:tools/souji-census.sh:85-92` (which refused key presence outright):

> ## Round 16 boundary clarification
>
> At `cbf688a`, among repository-config outcomes only a config-named path
> (include target, `core.excludesFile`, `core.attributesFile`, `core.worktree`)
> that reaches a protected root refuses the whole run (`path-protected`,
> exit 2); usage and malformed-baseline exit 2 are unchanged input errors. A
> config the census cannot evaluate without an unproven path (`~user`,
> `%(prefix)`, include cycle or depth > 10, non-regular or hardlinked include
> target/config.worktree, NUL/unparsable config, invalid
> `extensions.worktreeConfig` boolean) degrades to one `error` row for that
> repository only — exit 0, no git command runs there. A filter driver that an
> attributes source binds to a tracked path skips `status` for that repository
> only (`status-unverifiable`); the driver never runs. `core.hooksPath` and
> `core.fsmonitor` are neutralized on every status; `remote.*.promisor` /
> `extensions.partialClone` are accepted only with `GIT_NO_LAZY_FETCH=1` (an
> invalid promisor boolean still yields `status-unverifiable` from git's own
> status); `core.alternateRefsCommand` is accepted because no census command
> advertises alternate refs. This narrows when the census refuses; it does not
> widen action grounds and is not a sandbox proof for any other git command.
> F1–F4 unchanged.

Do not paste it before acceptance: `census/round-16/c1-matrix.json` is untracked
author output (`changed` arm: r15-config 20/20, r14-namespace 12/12, selftest
rc=0, `bash -n` rc=0, shellcheck warning rc=0; `r15-baseline` `bash -n` rc=2).
Those are the author's numbers, not L1's acceptance.

### 3.3 C2 landing gate is not a province surface
At this checkpoint neither `tools/souji-landing-gate.py` nor
`tests/fixtures/r16-landing-gate.py` exists. If C2 lands, it detects three
named r15 landing defect classes (non-parsing registry script; frozen pin
matching no committed bytes; a seat-reported known failure not carried
verbatim). That is round-process calibration — QUALITY/lesson evidence — not a
fleet hygiene ground, so `PROVINCE.md` Core should not absorb it, and a green
gate is not acceptance (same shape as r13's “an evidence-integrity PASS is not
a safety certificate”, `corpus/README.md:76-78`).

## 4. Contradiction to state explicitly (do not smooth it)

The same config class is **accepted** by the census and **refused** by the F2
probe:

- census: `remote.*.promisor` / `extensions.partialClone` accepted, every git
  call carries `GIT_NO_LAZY_FETCH=1` (`tools/souji-census.sh:101-110`, export at
  `:147`; invalid boolean still degrades to `status-unverifiable`);
- `tools/souji-repo-structure.sh:15-18` and `:197-200`: promisor/partial-clone
  repositories are refused before the walk because `git repo structure` was
  observed lazily fetching three times and growing `.git` 28→40 files.

Consequence: C1's shorthand “promisor/partialClone are inert” is true only for
census commands under `GIT_NO_LAZY_FETCH=1`. Any r16 lesson/SKILL/province
wording that generalizes it to tools or to `git repo structure` would be false.

## 5. Affected axes

- **A1 frontier accounting honesty** (primary): the round must be recorded as
  advancing zero frontier rows; the F2 live pointer is currently wrong and
  contradicts committed r13 evidence.
- **A2 province boundary precision** (secondary): the value/effect-aware
  Refused/Degraded/Accepted split is a real boundary refinement, but only
  after acceptance and only scoped to census commands.
- **A3 calibration**: untouched by this move; C2 is L1's to admit.
- **A4 operability**: untouched; I make no claim about C1 beyond citing its
  author matrix.

Harm check: documentation-only, no code, no knowledge entry, no new ground, no
capability claim, no census execution.

## 6. Proposed move (one, bounded)

**Admit the r16 accounting correction, not a frontier claim:**

1. In the r16 README section, state frontier unchanged for all four rows
   (draft A), and keep the province paragraph out of this round's landing until
   C1 is accepted.
2. Replace the stale `corpus/README.md:47` F2 pointer with the remaining
   frontier, citing the already-executed r13 fixture (draft B). This is a
   correction backed by committed evidence, not an r16 advance.
3. Optionally date-stamp F1's r12 numbers at `corpus/README.md:46` (“r12
   measurement, HEAD `dcc8b9e`”) without changing the question.

Draft A (README, appended after the r15 stop section):
```
## Round 16 — repair-first census restoration and landing calibration

r16 repairs operability and calibration; it claims no new ground. No frontier
row (F1–F4) advances: F1's live auto-maintenance exposure run, F2's
whole-workspace size attribution and unreachable-object census, F3's
`duplicate` taxonomy decision and F4's origin-record/staging tool changes
remain the next steps.

- `../tools/souji-census.sh` at `cbf688a` restores a parsing, value/effect-aware
  config guard. Its accepted keys are accepted *for census commands only*;
  `../tools/souji-repo-structure.sh` still refuses promisor/partial-clone
  repositories.
- [only if C2 lands and is measured] `../tools/souji-landing-gate.py`
  mechanically detects three named r15 landing defect classes; a green gate is
  not acceptance and admits no knowledge.
```

Draft B (replacement for `corpus/README.md:47`):
```
- F2 repository size census — next: whole-workspace size attribution and the
  unreachable-object census. The /var/tmp write-safety fixture landed r13
  (`../tests/fixtures/r13-repo-structure.sh`; `structure-selftest` exit 0
  matched in `../census/round-13/verification.json`).
```

## 7. Risks

1. Pasting the province paragraph before C1 acceptance reads as admission of
   the round's own claim; it must stay gated on L1.
2. C1's “promisor/partialClone inert” wording is overbroad across tools; use
   the census-scoped sentence or it contradicts `tools/souji-repo-structure.sh`.
3. Correcting the F2 pointer could be misread as F2 progress; label it a
   correction and cite the r13 measured result.
4. r16's landing diff is otherwise a repair round; keep the doc change to one
   section plus one row to avoid churn.
5. `census/round-16/c1-matrix.json` and the wave spec are untracked; do not
   treat them as accepted evidence or as a substitute for L1's named commands.
6. F1's “0 prunable, 3 locked” is a point-in-time r12 observation, not a
   property of the fleet; it must not be cited as current.

## 8. Verification for L1 (all read-only; I ran these)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --oneline cbf688a
# expect: 3 files (run-matrix.py, r15-census-config.py, souji-census.sh)

git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- corpus/knowledge PROVINCE.md corpus/README.md
# expect: b410186 is newest; cbf688a absent

git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short corpus/README.md PROVINCE.md corpus/knowledge
# expect: empty

grep -nE '^- F[1-4]' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/README.md
grep -n 'bounded structure-census capability acquired' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/README.md   # 68

test -f /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py; echo $?   # 1 at this checkpoint

grep -n 'no forbidden git subcommand' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh   # 1731

grep -n 'promisor' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh   # 15-18, 74-75, 111, 197-200

python3 -c "import json;d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/verification.json'));print([ (r['name'],r['exit_code'],r['matched']) for r in d['results'] if r['name']=='structure-selftest'], d['measured_commit'])"
# expect: [('structure-selftest', 0, True)] 6f8ee0f...

python3 -c "import json;d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix.json'));print({a:{f:(v.get('total'),v.get('failed'),v.get('rc')) for f,v in x.items()} for a,x in d['arms'].items()})"
# changed: r14-namespace (12,0,0), r15-config (20,0,0); r15-baseline bash_n rc=2
```

STATUS: no check in this seat failed. Known state: no frontier row advances; the F2 live pointer contradicts committed r13 evidence; C2 is not present at this checkpoint (`tools/souji-landing-gate.py` absent) and `census/round-16/c1-matrix.json` is untracked author output, not acceptance.

## Commands

Every shell command run by this seat, verbatim (heredoc bodies included; `read`-tool calls are not shell commands and are omitted):

```
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1; echo ---; ls /home/vgpnk/Projects/shokunin/souji-shokunin/census/ 2>&1 | tail -20

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
"

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    print(it.get('id'),'|',it.get('kind'),'|',it.get('owner'),'|',str(it.get('title'))[:110])
" 2>&1 | head -60

cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls census/round-16/ && echo --- && cat census/round-16/*.json 2>/dev/null | head -40

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
print(json.dumps(d['items'][0], indent=1)[:1500])
print('N items', len(d['items']))
print(json.dumps(d.get('context'))[:800])
"

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    p=it['prompt']
    import re
    m=re.search(r'OWN ONLY[^\n]*', p)
    print(it['name'],'|',it['role'],'|',(m.group(0)[:150] if m else ''))
"

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    if it['name']=='ConnFrontier':
        print(it['prompt'])
"

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -8 && echo --- && git status --short | head -20 && echo --- && ls corpus/knowledge/ && echo --- && ls corpus/lessons/ | tail -6 && echo --- && ls tools/ | head -40

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix.json'))
print(json.dumps({k:(list(v) if isinstance(v,dict) else v) for k,v in d.items()}, indent=1)[:1200])
" 2>&1 | head -40; echo ---; grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md; grep -oE '^\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | tail -6

cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/lessons/ && echo --- && git show --stat --oneline cbf688a | head -20 && echo --- && ls -la tools/souji-landing-gate.py tools/souji-census.sh tools/souji-preservation-evidence.py 2>&1 && echo --- && grep -nE '^## Q|^### Q' QUALITY.md | tail -8

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-15/end-sources.json'))
print(type(d)); print(json.dumps(d)[:600])
" 2>&1; echo ---; grep -nE '^\|[[:space:]]*S04[0-3]' corpus/SOURCES.md

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
ctx=d['context']
print('context has frontier:', 'frontier' in ctx.lower(), '| f2:', 'f2' in ctx.lower())
for it in d['items']:
    if it['name']=='DraftSkillSection':
        print('---DraftSkillSection---'); print(it['prompt'][:2500])
EOF

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix.json'))
for arm,a in d['arms'].items():
    out={}
    for fx,v in a.items():
        if isinstance(v,dict) and 'total' in v: out[fx]=f"{v.get('passed',v.get('total')-v.get('failed',0))}/{v['total']} failed={v.get('failed')} rc={v.get('rc')}"
        elif isinstance(v,dict) and 'rc' in v: out[fx]=f"rc={v['rc']}"
    print(arm, out)
EOF

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 -- corpus/knowledge PROVINCE.md corpus/README.md && echo --- && git status --short corpus/README.md PROVINCE.md corpus/knowledge && echo "(empty=clean)" && echo --- && grep -nE '^## Frontier|^- F[1-4]' corpus/README.md

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE 'Refused|Degraded|Accepted|status-unverifiable|exit 2|exit code' | head -40

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '44,130p'

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^## |^### ' QUALITY.md | tail -12; echo ---; grep -nE '^## |^### ' SKILL.md | head -30

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE 'maintenance|prune|GIT_NO_LAZY_FETCH|worktree list|repack|gc ' | head -20; echo ---; ls tests/fixtures/ | grep -iE 'r16|structure|quarantine|dupe|size' ; echo ---; git show --stat --oneline b410186 | head -12

cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/*.md && echo --- && grep -nE '^## Q|^### Q|^\*\*Q' corpus/QUALITY.md 2>/dev/null | tail -10

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '1680,1760p'

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'Q2[0-9]' corpus/QUALITY.md | head -20; echo ---; git show cbf688a:tools/souji-census.sh | grep -nE 'no forbidden git subcommand|selftest: .* checks'

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '/var/tmp|mktemp' tests/fixtures/r13-repo-structure.sh | head -8; echo ---; python3 - <<'EOF'
import json
d=json.load(open('census/round-13/verification.json'))
s=json.dumps(d)
import re
for m in re.finditer(r'[^"]*structure[^"]*', s):
    print(m.group(0)[:200])
EOF

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'prunable|locked|maintenance|fetch|merge|rebase' census/round-12/scout-surfaces.md | head -20; echo ---; sed -n '1,12p' census/round-12/scout-surfaces.md

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-13/verification.json'))
print(list(d))
for k,v in d.items():
    s=json.dumps(v)
    if 'structure' in s.lower():
        print('KEY',k, s[:900])
EOF

cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,30p' tests/fixtures/r13-repo-structure.sh; echo ...; sed -n '100,120p' tests/fixtures/r13-repo-structure.sh

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-13/verification.json'))
for r in d['results']:
    n=r.get('name','')
    if 'struct' in n or 'structure' in n.lower():
        print(n, '| exit', r.get('exit_code'), '| matched', r.get('matched'), '| cmd', ' '.join(r.get('command',[]))[:120])
EOF

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | grep -nE 'count-objects|repo structure|status --porcelain|rev-list|worktree list' | head; echo ---; grep -nE 'promisor|partialClone|partial-clone' tools/souji-repo-structure.sh | head -12

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688a:tools/souji-census.sh | sed -n '1,43p'

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'Refused \(exit 2|Degraded to one|Accepted: any|Exit codes|no forbidden git subcommand|^#   repo  worktrees' tools/souji-census.sh; echo ---; git diff cc21683 cbf688a -- tools/souji-census.sh | grep -E '^[-+].*(scratch_bytes|repo structure|count-objects|du -sb|worktrees  unpushed)' | head

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^### Round 15 final operator stop|^## Round 15|^## Round 14|^## Round 13|^- \*\*Frontier|F1 git-native|F2 repository|F3 duplicate|F4 restorable' PROVINCE.md corpus/README.md

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^## Round 13 current coverage|^## Round 14|^## Round 15|^### Round 15 final operator stop' corpus/README.md; echo ---; grep -nE '^## Round 1[34]' PROVINCE.md; echo ---; ls tests/fixtures/ | grep -iE 'r16' ; echo "(none above = absent)"; echo ---; grep -nE 'GIT_NO_LAZY_FETCH=1$|^export GIT_NO_LAZY_FETCH' tools/souji-census.sh

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'bounded structure-census capability acquired' corpus/README.md; echo ---; python3 - <<'EOF'
import json
d=json.load(open('census/round-13/verification.json'))
print('measured_commit', d['measured_commit'])
print('recorded_at', d['recorded_at'])
for r in d['results']:
    if r.get('name')=='structure-selftest':
        print(json.dumps(r)[:700])
print('scope', json.dumps(d.get('scope'))[:400])
EOF

cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '86,124p' tools/souji-census.sh

cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | grep -nE 'hooksPath|fsmonitor|promisor|alternateRefsCommand|Refused|Degraded|Accepted' | head -20; echo ---; git show cc21683:tools/souji-census.sh | sed -n '78,100p'

cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '\bmerge\b|\bmaintenance\b' tools/souji-census.sh | head; echo "rc=$?"; echo ---; sed -n '1727,1734p' tools/souji-census.sh

cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '14,19p' tools/souji-repo-structure.sh; echo ...; sed -n '196,200p' tools/souji-repo-structure.sh

cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    p=it['prompt']
    for kw in ('corpus/knowledge','PROVINCE.md','corpus/README.md','F1','F2','F3','F4'):
        if kw in p and kw in ('corpus/knowledge','PROVINCE.md','corpus/README.md'):
            print(it['name'],'mentions',kw)
EOF
```
