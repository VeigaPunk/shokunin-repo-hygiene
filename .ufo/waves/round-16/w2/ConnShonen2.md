# ConnShonen2 — SHONEN.md boxes mapped to final r16 evidence (HEAD)

Measured at lane HEAD `163158a706352f1c0ee3521c4da2e5289970db57` (2026-10-20). The wave
contract named `a6ec781`; L1 landed `163158a` (round-16 lesson, SOURCES S043–S050, QUALITY
Q25/Q26, LOG entries, SCORECARD, SKILL registry, README) while this seat was reading. Every
pointer below resolves at `163158a`. `SHONEN.md` itself is unchanged since `6ed10a7` (r13):
its four pointers are stale, none false.

Axes: **calibration** (pointer currency and claim strength). Operability and coverage are
untouched — this is a docs/pointer mapping, no lane file edited. No box moves to `[x]`:
r16 is a verification round, certification is OFF and K5 is HELD; all four stay `[~]`.

I ran no tool, fixture or gate (no `ALLOWED-EXEC` in this item). Every r16 pass/fail number
below is a *recorded* value read from committed evidence, not a check re-run by this seat.

## Box map

| # | box (SHONEN as landed) | verdict | current pointer resolves? | r16 evidence at `163158a` | smallest fix |
|---|---|---|---|---|---|
| 1 | SKILL.md contains real decision tables, error patterns, checklists, cited sources | holds | yes, but r13-only | `SKILL.md:42` Decision tables (5-row classify table), `:74` Error patterns, `:109` Checklists, `:126` Gate registry (18 rows; new r16 rows `:152` souji-landing-gate, `:153` r16-landing-gate, `:154` souji-seat-audit; `:149`/`:150` updated); `corpus/SOURCES.md:9` r16 provenance, `:57-64` S043–S050 (6 mined, S044/S048 rejected); `corpus/lessons/round-16.md`; `corpus/QUALITY.md:64-65` Q25/Q26 | add the r16 registry rows/source ids to the pointer; no box change |
| 2 | At least one end-to-end domain task executed and logged in LOG.md | holds | yes | `LOG.md:362` heading, section `362-438`; `:368` “**Removed — fleet root, receipt `pushed` (96 artifacts).**”; `:375` hold (>25 min) + second check; receipts tracked at `census/operator-sweep-20261018/approval-list.tsv`, `resume-verdicts.tsv`. r16 LOG entries `:817`/`:836` record verification work, not a domain removal | cite the section range + receipts; do not add the r16 entries |
| 3 | Instructions executable by an agent without oral context | holds, one misread risk | yes | `SKILL.md:109-124` two checklists, `:126-155` each registry row carries entry command + verdict map + self-test + pinned path, `:176-197` repository-structure census; `census/round-13/verification.json` `results[name=structure-selftest]` → `exit_code 0`, `matched true`, stdout `selftest=PASS ids=5/5`, `measured_commit 6ed10a7`; `census/round-16/run-matrix.py` header usage, refuses overwrite; r16 executes `census/round-16/c1-matrix-final.json` and `c1-matrix-landing.json` | add the r16 registry commands + run-matrix; annotate the fixture header (F1) |
| 4 | No cross-domain bleed (PROVINCE.md still accurate) | holds (inherited, not re-derived) | yes | `PROVINCE.md:6` Owns, `:19` Work surfaces, `:26` Refuses, `:47-71` Core/Frontier/Adjacent, `:72-81` Round 13 refinement, `:82-93` Round 14 clarification; `.ufo/waves/round-13/w1/Overlap.md` (tracked at HEAD; §4 cross-domain matrix, §5 sibling-absence checks); `corpus/lessons/round-16.md:22` rejects “any deletion certification; K5 re-admission”, `:75` “Certification stays OFF; K5 stays HELD” | pointer stays on PROVINCE + Overlap; optional one-sentence Round 16 clarification (F3) |

## Proposed SHONEN.md body (exact; `[~]` + pointer only)

```markdown
# souji-shokunin — Promotion checklist

Promotion to shokunin requires all of:

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
  SKILL.md Decision tables, Error patterns, Checklists and Gate registry (incl. souji-landing-gate, r16-landing-gate, souji-seat-audit); corpus/SOURCES.md (S043–S050 registry rows); corpus/lessons/round-16.md
- [~] At least one end-to-end domain task executed and logged in LOG.md
  LOG.md:362-438 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed; census/operator-sweep-20261018/approval-list.tsv, resume-verdicts.tsv)
- [~] Instructions executable by an agent without oral context
  SKILL.md Checklists, Gate registry entry/verdict/self-test columns and Repository structure census; tests/fixtures/r13-repo-structure.sh with recorded 5/5 PASS in census/round-13/verification.json; census/round-16/run-matrix.py
- [~] No cross-domain bleed (PROVINCE.md still accurate)
  PROVINCE.md Core / Frontier / Adjacent, Round 13 boundary refinement, Round 14 boundary clarification; .ufo/waves/round-13/w1/Overlap.md; corpus/lessons/round-16.md Gate (Rejected) and Residuals
```

Line and id anchors in this block are absent on purpose except `LOG.md:362-438`: SKILL,
SOURCES, QUALITY, PROVINCE and the lesson are still editable by wave-2 integration, so
section names and stable ids are used instead of line numbers. The measured line map is in
the table above (`163158a` only).

## Falsification notes

**F1 — box 3: the fixture an agent opens first denies its own recorded run.**
`tests/fixtures/r13-repo-structure.sh:4-7` says `STATUS: authored, NOT EXECUTED by this
seat … not an observed PASS`, while `census/round-13/verification.json`
(`results[name=structure-selftest]`) records exit 0, `matched: true`, `selftest=PASS
ids=5/5` at `measured_commit 6ed10a7`. The header is seat-scoped and historically true, not
a lie; but box 3 is exactly “without oral context”, and the first file read says the
evidence is a design target. Smallest fix: append one header line —
`# Recorded integrator run: census/round-13/verification.json (structure-selftest; exit 0; 5/5; measured_commit 6ed10a7).`
Verdict for the box: holds; the pointer already carries the run, so this is a readability
repair, not a claim correction.

**F2 — box 2: pointer line is a heading, and r16 must not be used to inflate it.**
`LOG.md:362` is the section heading; the section ends at `:438` (next heading `:439`). The
parenthetical matches `:368` (96 artifacts) and `:375` (hold + second check). r16 adds LOG
entries at `:817` (r15 parse correction) and `:836` (census/gate/checker/audit), but neither
is an end-to-end *domain* removal; citing them would overstate the box. Keep the sweep as
the sole evidence and widen the pointer to the range plus the two tracked receipt files.

**F3 — box 4: “still accurate” is inherited, not re-derived in r16.**
`PROVINCE.md` has no Round 15/16 section, and r16 added two gates
(`tools/souji-landing-gate.py`, `tools/souji-seat-audit.py`) with no province paragraph.
Nothing in r16 contradicts the existing text: the r13 sentence (`PROVINCE.md:72-81`) already
bounds evidence-integrity checking as “not fleet orchestration or an independent promotion
authority”, the landing gate reads committed blobs and only runs `bash -n`/`compile()` in
`/var/tmp` (`SKILL.md:152`), and the wave-1 audit read only souji's own exported transcripts
(`census/round-16/seat-audit-w1.json`; lesson `:70`). The r13 sibling sweep (`Overlap.md`
§5) was not re-run in r16. Verdict: holds. Optional strengthening for L1, only if the box is
to cite r16 rather than r13:
`## Round 16 boundary clarification` — “Landing-gate findings are consistency findings about this lane's own landing claims and never execute or certify repository behavior; the seat-transcript audit covers souji's own exported wave seats only and is a lower bound, not fleet-wide compliance or promotion authority.”

**F4 — HEAD moved mid-wave; do not copy pointers measured at `a6ec781`.**
At `a6ec781`, `corpus/lessons/round-16.md`, `census/round-16/c1-matrix-landing.json`, the
SOURCES S043–S050 paragraph, Q25/Q26, the LOG r16 entries, the SKILL registry rows and the
SCORECARD r16 rows were absent or uncommitted. The SHONEN draft above uses only paths and
ids that resolve at `163158a`; any wave-2 item that measured `a6ec781` bytes must re-pin.

**F5 — box 1: “cited sources” is a registry pointer, not a live-fetch claim.**
S043's grounding is a Wayback capture plus the installed `bash(1)` (`corpus/lessons/
round-16.md` Seat-reported failures, `SrcBashSetN` open); S044/S048 are rejected rows kept
for curation. `SKILL.md` inline citations remain S035–S037/S040 and Q18/Q20/Q21/Q23;
S043–S050 are cited by the lesson and the registry. The proposed line says “S043–S050
registry rows” to keep that distinction explicit.

## What was not verified here

The landing gate was not run by this seat against `163158a`; a self-landing replay (does the
gate pass on the commit that landed it?) is outside this item and remains unverified. No
fixture, selftest or census was executed.

STATUS: ok

## Commands

```
ls /home/vgpnk/Projects/shokunin/souji-shokunin/ 2>&1 | head -50
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -12
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^#' SKILL.md && echo '--- files ---' && ls -la corpus/lessons/ 2>&1 && echo '--- fixtures ---' && ls tests/fixtures/ 2>&1 && echo '--- census13 ---' && ls census/round-13/ 2>&1 && echo '--- census16 ---' && ls census/round-16/ 2>&1
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain=v1 && echo '--- SHONEN at HEAD ---' && git show HEAD:SHONEN.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== LOG.md 355-375 ===' && sed -n '355,375p' LOG.md && echo '=== SOURCES head ===' && sed -n '1,20p' corpus/SOURCES.md && echo '=== SOURCES tail ids ===' && grep -oE '^\| ?S[0-9]+' corpus/SOURCES.md | tail -12
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== PROVINCE ===' && sed -n '1,60p' PROVINCE.md && echo '=== Overlap ===' && ls -la .ufo/waves/round-13/w1/ 2>&1 && echo '=== r13 verification ===' && python3 -c "import json;d=json.load(open('census/round-13/verification.json'));print(type(d));print(list(d)[:20] if isinstance(d,dict) else len(d))"
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== HEAD LOG 358-368 ===' && git show HEAD:LOG.md | sed -n '358,368p' && echo '=== HEAD SOURCES last ids ===' && git show HEAD:corpus/SOURCES.md | grep -oE '^\| ?S[0-9]+' | tail -5 && echo '=== HEAD SOURCES r16 line? ===' && git show HEAD:corpus/SOURCES.md | grep -n 'Round-16' || echo no-r16-para && echo '=== HEAD LOG tail ===' && git show HEAD:LOG.md | tail -12
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,80p' corpus/lessons/round-16.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '125,240p' SKILL.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w2/ && echo '=== spec ===' && cat .ufo/waves/round-16/w2-spec.json | head -c 4000
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SKILL r16 refs ===' && grep -n 'r16\|landing-gate\|seat-audit\|repeatable fleet census\|Repeatable fleet census' SKILL.md; echo '=== .ufo tracked? ===' && git ls-tree -r --name-only HEAD .ufo | head -5; echo '=== check-ignore ===' && git check-ignore -v .ufo/waves/round-13/w1/Overlap.md || echo not-ignored; echo '=== ls Overlap at HEAD ===' && git cat-file -e HEAD:.ufo/waves/round-13/w1/Overlap.md 2>&1 && echo tracked || echo absent-at-head
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,80p' SCORECARD.md && echo '=== LOG sweep extent ===' && sed -n '362,430p' LOG.md | grep -n '^## '
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== HEAD census16 ===' && git ls-tree -r --name-only HEAD census/round-16/ && echo '=== HEAD r16 tools/fixtures ===' && git ls-tree -r --name-only HEAD tools/ | grep -E 'landing|seat|preservation|census' && echo '=== HEAD r16 fixtures ===' && git ls-tree -r --name-only HEAD tests/fixtures/ | grep -E 'r16|r15-preservation'
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SHONEN in lesson ===' && grep -n 'SHONEN\|promotion' corpus/lessons/round-16.md; echo '=== LOG headings after 362 ===' && awk 'NR>=362 && /^## /{print NR": "$0}' LOG.md | head -10; echo '=== PROVINCE tail ===' && sed -n '60,140p' PROVINCE.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SHONEN history ===' && git log --oneline -- SHONEN.md | head -5 && echo '=== census operator-sweep tracked ===' && git ls-tree -r --name-only HEAD census/ | grep -i 'operator-sweep' | head -6; echo '=== run-matrix help ===' && head -40 census/round-16/run-matrix.py
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SKILL checklists ===' && sed -n '108,124p' SKILL.md && echo '=== worktree LOG r16 ===' && grep -n 'round 16\|round-16' LOG.md | head -10
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== HEAD SCORECARD round-16 refs ===' && git show HEAD:SCORECARD.md | grep -n 'round-16\|landing-gate\|seat-audit' | head -20; echo '=== HEAD has lesson? ===' && (git cat-file -e HEAD:corpus/lessons/round-16.md && echo yes || echo NO); echo '=== HEAD c1-matrix-landing? ===' && (git cat-file -e HEAD:census/round-16/c1-matrix-landing.json && echo yes || echo NO); echo '=== worktree LOG 362 ===' && sed -n '362p' LOG.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && head -25 tests/fixtures/r13-repo-structure.sh && echo '=== landing gate usage ===' && grep -n 'Usage\|--root\|--rev\|--round' tools/souji-landing-gate.py | head -15 && echo '=== seat audit usage ===' && grep -n 'Usage\|--' tools/souji-seat-audit.py | head -12
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -4 && echo '=== status ===' && git status --porcelain && echo '=== ls-tree lesson ===' && git ls-tree HEAD corpus/lessons/ && echo '=== ls-tree landing json ===' && git ls-tree HEAD census/round-16/
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SKILL r16 ===' && grep -n 'r16\|landing-gate\|seat-audit\|value/effect\|Repeatable fleet census' SKILL.md; echo '=== SOURCES r16 ===' && grep -n 'Round-16\|^| S04[3-9]\|^| S050' corpus/SOURCES.md | cut -c1-160; echo '=== QUALITY Q25/Q26 ===' && grep -n 'Q25\|Q26' corpus/QUALITY.md | head
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== LOG r16 headings ===' && grep -n '^## 2026-10-20 — round 16' LOG.md; echo '=== LOG 362 ===' && sed -n '362p' LOG.md; echo '=== next heading after 362 ===' && awk 'NR>362 && /^## /{print NR": "$0; exit}' LOG.md; echo '=== lesson status lines ===' && grep -n '^STATUS:' corpus/lessons/round-16.md | head; echo '=== lesson size ===' && wc -l corpus/lessons/round-16.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('census/round-13/verification.json'))
for r in d['results']:
    s=json.dumps(r)
    if 'repo-structure' in s:
        print(json.dumps({k:r[k] for k in r if k in ('gate','command','exit','verdict','summary','id','name')}, indent=0)[:800])
PY
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== lesson headings ===' && grep -n '^## \|^### ' corpus/lessons/round-16.md; echo '=== PROVINCE boundary lines ===' && grep -n '^## ' PROVINCE.md; echo '=== SHONEN refs elsewhere ===' && grep -rn 'SHONEN' MINT.md SKILL.md AGENTS.md PROVINCE.md 2>/dev/null | head
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
d=json.load(open('census/round-13/verification.json'))
for r in d['results']:
    if r.get('name')=='structure-selftest':
        print(json.dumps(r, indent=1)[:1200])
PY
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== SKILL decision table rows ===' && sed -n '42,73p' SKILL.md | grep -c '^|'; echo '=== Overlap verdict ===' && grep -n 'no sibling\|0 hits\|bleed\|Sweep' .ufo/waves/round-13/w1/Overlap.md | head -8; echo '=== HEAD now ===' && git rev-parse --short HEAD && git status --porcelain | head
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '362,438p' LOG.md | grep -n '96\|second\|hold\|removed\|Removed\|quarantin' | head -20; echo '=== PROVINCE total ===' && wc -l PROVINCE.md; echo '=== SKILL citations ===' && grep -oE 'S0[0-9]{2}|Q[0-9]{2}' SKILL.md | sort -u | tr '\n' ' '
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== registry-cited paths that do not exist ===' && grep -oE '(tools|tests)/[A-Za-z0-9._/-]+\.(sh|py)' SKILL.md | sort -u | while read -r p; do [ -e "$p" ] || echo "MISSING $p"; done; echo '=== w2 dir ===' && ls -la .ufo/waves/round-16/w2/ | head; echo '=== ConnShonen2 exists? ===' && ls .ufo/waves/round-16/w2/ConnShonen2.md 2>&1
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,8p' tests/fixtures/r13-repo-structure.sh | cat -n; echo '=== PROVINCE 82-93 ===' && sed -n '82,93p' PROVINCE.md; echo '=== HEAD ===' && git rev-parse --short HEAD
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## ' SKILL.md && echo '--- 40-44 ---' && sed -n '40,44p' SKILL.md && echo '--- 71-76 ---' && sed -n '71,76p' SKILL.md && echo '--- 124-128 ---' && sed -n '124,128p' SKILL.md && git rev-parse --short HEAD
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w2/ConnShonen2.md && sed -n '1,12p' .ufo/waves/round-16/w2/ConnShonen2.md && echo '...' && grep -n 'STATUS:' .ufo/waves/round-16/w2/ConnShonen2.md && git rev-parse --short HEAD && git status --porcelain | head -5
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## ' .ufo/waves/round-16/w2/ConnShonen2.md && tail -6 .ufo/waves/round-16/w2/ConnShonen2.md
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=126 && NR<156 && /^\| [a-z0-9-]+ \|/ {n++; print NR": "$0}' SKILL.md | cut -c1-60; echo "count=$(awk 'NR>=126 && NR<156 && /^\| [a-z0-9-]+ \|/ {n++} END{print n}' SKILL.md)"
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '42,73p' SKILL.md | cat -n | sed -n '1,32p'
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- SKILL 155-156 ---' && sed -n '155,156p' SKILL.md | cut -c1-60; echo '--- LOG 368/375 ---' && sed -n '368p;375p' LOG.md | cut -c1-100; echo '--- lesson 22/75 ---' && sed -n '22p;75p' corpus/lessons/round-16.md | cut -c1-120; echo '--- HEAD ---' && git rev-parse --short HEAD && wc -l .ufo/waves/round-16/w2/ConnShonen2.md
```
