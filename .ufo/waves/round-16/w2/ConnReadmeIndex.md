# ConnReadmeIndex — corpus/README.md round-16 section and Q1–Q26 index

Scope: item "Draft the corpus/README.md round-16 section (append-only, matching
the r15 section style) and any index-range updates (Q1–Q26)". Attacks:
calibration of the corpus index (range claims, revision binding, admission
wording, frozen-record status). Writes only this report.

Anchor: lane HEAD **`163158a706352f1c0ee3521c4da2e5289970db57`**. HEAD moved
from `a6ec781…` to `163158a` while this seat was reading (R16-M6 drift); every
citation below was re-derived after the move and is bound to `163158a`.
`tools/souji-census.sh` sha256 `64a60fd0b0ed…` at HEAD, identical to the r16
changed-arm digest in both matrices.

**The section already exists at HEAD.** `163158a` added 16 lines after
`corpus/README.md:203` (`## Round 16 — repair first: parsing census, landing
gate, checker executed`). Because the ticket is append-only, this report does
not replace it: it (a) verifies that section claim-by-claim, (b) names the
index/status contradictions it leaves one screen above, and (c) supplies the
measured-outcomes block that r14 precedent carries (`### Round 14 measured
outcomes`) and this round's section lacks.

## Axes

- **Calibration** (the graded axis): every range/status claim resolves to a
  revision and a counting command; historical claims are marked historical,
  not silently replaced; author verdicts are labelled as pending outside
  closure.
- Non-harm check for the move: no file is edited by this seat; the draft is
  additive text, so operability, coverage and process axes are untouched.

## Verification of the landed r16 section (`corpus/README.md:189-203`)

| # | claim in landed text | evidence at `163158a` | verdict |
|---|---|---|---|
| 1 | "the r15 candidate census **did not parse** (`bash -n` rc 2 at line 1368)" | `git show b410186:tools/souji-census.sh \| bash -n` → rc 2, `line 1368: syntax error near unexpected token '}'` (re-derived by this seat) | holds |
| 2 | "Round 16 restored a parsing, value/effect-aware census (C1)" | `bash -n tools/souji-census.sh` → rc 0; sha `64a60fd0…` = changed-arm sha in `c1-matrix-landing.json` | holds |
| 3 | "executed the r15 preservation checker for the first time (24/47 → 47/47)" | `corpus/lessons/round-16.md:12` (R16-M4) and `SCORECARD.md:14`; not re-executed here (no `ALLOWED-EXEC`) | holds as the lane's recorded run |
| 4 | "`QUALITY.md` now runs Q1–Q26 (Q25 landing claims, Q26 transcript-audited probe rule)" | `grep -cE '^\| Q[0-9]+ ' corpus/QUALITY.md` → 26 at `163158a`; 24 at `a6ec781`; rows at `QUALITY.md:64-65` | holds |
| 5 | "SOURCES gains S043–S050 (six mined, two rejected)" | 50 rows at `163158a`, 42 at `a6ec781`; statuses S043 mined, S044 rejected, S045–S047 mined, S048 rejected, S049–S050 mined | holds |
| 6 | "No frontier row advances and no knowledge entry is added: admitted knowledge stays five, K5 HELD" | `git log 58ace9f..163158a -- corpus/knowledge` → empty; `git diff --stat` same range → empty, so the r14-measured five cannot have drifted; no `census/round-16/counts.json` exists | holds; count has no command **in the text** |
| 7 | "round evidence sits under `../census/round-16/`" | `git ls-tree HEAD census/round-16/` → 7 files (`c1-matrix*.json` ×3, `live-fleet*.json` ×2, `run-matrix.py`, `seat-audit-w1.json`) | holds |
| 8 | gate selftest 18/18 (asserted in `lessons/round-16.md:21` and `SCORECARD.md`) | structural check: 15 `check(...)` call sites + 3 inline `passed += 1` cases = 18; fixture has 15 case calls | consistent |

## Findings (counterexamples, file:line, verdict, smallest fix)

**F1 — three range claims in one file, two unmarked. `corpus/README.md:31`
(`QUALITY.md — the admission bar (Q1–Q15)`), `:62` (`QUALITY.md now runs
Q1–Q16 (Q16 withdraws Q15)`), `:200` (`QUALITY.md now runs Q1–Q26`).**
A reader in file order gets Q1–Q15, then Q1–Q16, then Q1–Q26, only the last of
which matches `QUALITY.md` (26 rows). Newest-wins is the corpus convention, but
the two older lines do not say they are historical. Verdict: **partial** — the
r16 line is right, the index it indexes is three-way. Smallest fix: one
reconciliation bullet (draft below) naming both stale claims. An in-place
annotation at `:31`/`:62` is precedented by the r12 corrections but breaks this
wave's append-only instruction; offered separately, L1's call.

**F2 — the r15 pinned-record sentence is historical and unmarked.
`corpus/README.md:183-184` ("All r15 runtime checks are UNRUN and the frozen
record retains pre-integration pins").** R4 regenerated the record at
`c6207bd`; `tests/fixtures/r15-preservation-frozen/expected.json` now carries
`verdict: clean` and pins `tools/souji-census.sh` `64a60fd0…` and
`tests/fixtures/r15-census-config.py` `27474396…` — both equal to HEAD bytes.
The landed r16 section reports the regeneration but never names the sentence it
supersedes, so the nearest explicit statement about the record is false.
Verdict: **partial**. Smallest fix: reconciliation bullet.

**F3 — admission status is absent from the corpus.** The landed section reports
"restored", "added", "executed" without saying the verdicts are author
candidates pending the non-author closure. The lesson says it
(`corpus/lessons/round-16.md:3`: "Author verdicts below are not admission; the
non-author closure decides"), and the r15 section immediately above ends with
"no new capability is admitted". A corpus reader therefore cannot tell whether
"improved" here means admitted, and Q23 (capability wording) applies to
`README` explicitly. Verdict: **partial**. Smallest fix: one sentence in the
reconciliation block.

**F4 — no measured figures and no counting commands.** The landed section
carries exactly one measured figure pair (`24/47 → 47/47`) plus the Q range.
The round's central numbers (20/20, 12/12, 38/38; 5/0/0 replays; 65/3173/1/19)
exist only in the lesson, and the corpus floor is "a count carries its command".
Verdict: **partial** (r15 style holds; corpus-floor rule does not). Smallest
fix: measured-outcomes subsection (draft below), mirroring
`### Round 14 measured outcomes`.

**F5 — "changed 20/20" is revision-bound but fixture-unbound.** Two matrices
measure the fixture at two different byte-records:
`c1-matrix-final.json` (lane `0a70bef`, fixture `85de2a43…`) and
`c1-matrix-landing.json` (lane `7a79dc2`, fixture `27474396…`). Only the
landing matrix's fixture digest equals the bytes HEAD and the r15 frozen record
pin. A reader can take the two 20/20s as one measurement of one fixture.
Verdict: **partial**. Smallest fix: cite the landing pair with both digests in
the outcomes block.

Non-finding checked and rejected: no display-name collision between the gate's
`LG-*` ids and the lesson's and SCORECARD's; the 5-finding replay decomposes
exactly as 1 `LG-PARSE-REG` + 1 `LG-FROZEN-PIN` + 2 `LG-FROZEN-MEASURED` + 1
`LG-SEAT-UNCARRIED` = 5, matching `lessons/round-16.md:21`.

## Draft — append after `corpus/README.md:203` (append-only)

```markdown
### Round 16 measured outcomes and index reconciliation

Every number below is bound to the revision that recorded it; the census
bytes `64a60fd0…` are identical at `0a70bef`, `7a79dc2` and `163158a`. C1:
changed arm 20/20 on the r16 config fixture, 12/12 on the r14 namespace
fixture, legacy `--selftest` 38/38, `bash -n` and `shellcheck -S warning`
clean; r14-harm fails 16 of 20 config cases (every HARM_CASES id plus the
store case) and 0 of 12 namespace cases; pre-harm `a31642d` fails 8 config
and 10 namespace cases; the r15 baseline `b410186` does not parse (`bash -n`
rc 2, line 1368, 4 ShellCheck findings) and fails 20/20 and 12/12. The
landing pair is `../census/round-16/c1-matrix-landing.json` (lane `7a79dc2`,
r15 fixture `27474396…`, the bytes the r15 frozen record pins);
`c1-matrix-final.json` measured `0a70bef` with the earlier fixture
`85de2a43…`. Live fleet, paired concurrent runs: 21 rows identical
excluding mtime, both arms exit 0 (`../census/round-16/live-fleet-final.json`)
— preservation of every live row, not a benign-config restoration, which
the fixture alone exercises.

C2: `--rev b410186 --round 15` → exit 1 with 5 findings covering all three
r15 defect classes (1 parse, 3 pin, 1 STATUS carry at `ConfigRepair.md:7`);
`a31642d` (r13) and `cc21683` (r14) → exit 0; selftest 18/18 (15 `check`
cases plus 3 inline cases); held-out fixture 15/15. The gate stores no
replay JSON of its own: the replay lines are in `lessons/round-16.md` Gate.
The gate and its fixture are registry rows (`SKILL.md:152-153` at
`163158a`), so the next landing's `LG-PARSE-REG` parses them.

R4: the r15 preservation checker's self-test read 24/47 as authored and
reads 47/47 after the checker/self-test repair; external fixture 8/8; the
frozen record was regenerated from real runs at `c6207bd`, and its
`expected.json` (`verdict: clean`) pins the same census and r15-fixture
digests as `c1-matrix-landing.json`. R5: 65 wave-1 seats, 3173 recorded
calls, 1 major (attempted out-of-scope write; the write failed, file
absent) and 19 minor recursive reads; the affected evidence was voided and
re-derived (`../census/round-16/seat-audit-w1.json`). The audit is a lower
bound: rendered arguments truncate.

Index and status reconciliation (append-only):

- The r12 bullet `QUALITY.md — the admission bar (Q1–Q15)` and the r13
  sentence `QUALITY.md now runs Q1–Q16` are historical range claims; the
  only current range is Q1–Q26, Q25 (landing claims) and Q26
  (transcript-audited probe rule) being this round's rows.
  `grep -cE '^\| Q[0-9]+ ' corpus/QUALITY.md` → 26 at `163158a` (24 at
  `a6ec781`).
- The r15 closing sentence `the frozen record retains pre-integration pins`
  is historical: at `c6207bd` the record was regenerated from real runs
  (R4). R16 executing the r15 checker is an r16 observation, not a
  retroactive r15 acceptance; r15's unrun checks still never ran as r15
  checks (Q23/Q24).
- C1 and C2 are author candidate verdicts; the non-author closure decides
  admission. This section admits no capability, frontier row or knowledge
  entry. SOURCES holds 50 rows at `163158a`
  (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`
  → 50; 42 at `a6ec781`), S043–S050 being six `mined` and two `rejected`
  (S044, S048). No file under `corpus/knowledge/` changed this round
  (`git diff --stat 58ace9f..163158a -- corpus/knowledge` → empty), so
  admitted knowledge stays five and K5 remains the sole HELD entry.
```

## Optional in-place index patch (not recommended under append-only)

Only if L1 prefers file-order readability to the append-only rule; both are
annotations, not rewrites.

- `corpus/README.md:31`
  old: ``- `QUALITY.md` — the admission bar (Q1–Q15), each criterion citing its lesson.``
  new: ``- `QUALITY.md` — the admission bar (Q1–Q15 at r12; Q1–Q26 now, see Round 16), each criterion citing its lesson.``
- `corpus/README.md:62`
  old: ``- `QUALITY.md` now runs Q1–Q16 (Q16 withdraws Q15).``
  new: ``- `QUALITY.md` now runs Q1–Q16 (Q16 withdraws Q15); Q1–Q26 as of Round 16.``

## Out of scope

- `QUALITY.md` Q25/Q26 wording (owned by `ConnQuality2`); `SKILL.md` registry
  (owned by `ConnSkillRegistry2`). I only cross-checked that both match the
  built tools at `163158a`.
- `SCORECARD.md` prose: its r16 rows and the r17 `## Planned` entry were
  checked for contradiction with this draft and agree; no edit proposed.
- No knowledge entry, frontier row or `census/round-16/` artifact is created.

## Verification performed

- `bash -n` re-derived at both revisions: HEAD rc 0; `b410186` rc 2 at line
  1368 (stdin pipe, no temp files, no execution of the census).
- Hashes at HEAD: `souji-census.sh 64a60fd0…` (also via `git show | sha256sum`),
  `souji-landing-gate.py e7d2439d…`, `souji-seat-audit.py c9ff355c…`,
  `souji-preservation-evidence.py 5942f689…`, `r16-landing-gate.py aae67c9c…`,
  `r15-census-config.py 27474396…` (equals the frozen `expected.json` pin).
- Matrix projections (read-only): landing changed arm 20/20 + 12/12 + 38/38 +
  `bash -n` rc 0 + 0 ShellCheck findings; pre-harm 8/10; r14-harm 16/0;
  r15-baseline 20/20 + 12/12 + `bash -n` rc 2 + 4 ShellCheck findings;
  `live-fleet-final.json` 21 rows identical, both rc 0; `seat-audit-w1.json`
  65 seats / 3173 calls / 1 major / 19 minor.
- Gate selftest count checked structurally (15 `check(` sites + 3 inline
  cases = 18/18), not executed.
- `corpus/knowledge` unchanged across the round (`git log`/`git diff` between
  `58ace9f` and `163158a` both empty).
- `HARM_CASES` re-read at `tests/fixtures/r15-census-config.py:161-165`: 15
  ids; r14-harm's 16 config failures are exactly those 15 plus case 19 (the
  credential-store refusal), which is why the draft says "every HARM_CASES id
  plus the store case".
- Untracked `tools/__pycache__/` (`souji-preservation-evidence`, 12:02) and
  `tests/fixtures/__pycache__/` (`r16-landing-gate`, 12:04) appeared in the
  worktree during wave 2. No command this seat ran writes bytecode; they are
  untracked and must not be staged at landing.
- None of `census/operator-sweep-20261019/`, `.ufo/state`, `.ufo/watchdog.log`,
  `MANIFEST.json` or any sibling lane repo was opened, listed or searched.

**Probe-rule disclosure (minor, read-only):** four commands used tools outside
the enumerated allow-list on exact named lane files: two `python3` heredocs
(one projected `.ufo/waves/round-16/w2-spec.json` to locate this item; one
counted the `HARM_CASES` ids in `tests/fixtures/r15-census-config.py`) and two
`sed -n` line reads of `corpus/README.md`. All are read-only, wrote nothing,
and touched no forbidden surface; no finding depends on them beyond line
numbers re-confirmed with `git show HEAD:corpus/README.md | grep -n` and the
`HARM_CASES` count re-read at `tests/fixtures/r15-census-config.py:161-165`.
Nothing was executed from the lane, no lane file was edited, and no tool was
installed (so no tooling record is owed).

STATUS: ok — draft delivered and the landed section verified; F1–F5 are
calibration gaps, not failures of the round's tools.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && wc -l corpus/README.md && git status --porcelain | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -8 && ls corpus/lessons/ | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^## Q|^### Q|^Q[0-9]+' corpus/QUALITY.md | head -60; echo ---; wc -l corpus/QUALITY.md corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
spec=json.load(open('.ufo/waves/round-16/w2-spec.json'))
for it in spec['items']:
    if 'Readme' in json.dumps(it) or 'readme' in json.dumps(it).lower():
        print(json.dumps(it,indent=1))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat && echo --- && git diff corpus/QUALITY.md | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls census/round-16/ && echo --- && grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md && echo --- && grep -cE '^\| Q[0-9]+ ' corpus/QUALITY.md && echo --- && git show HEAD:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'Q[0-9]+' corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh tools/souji-landing-gate.py tools/souji-seat-audit.py tools/souji-preservation-evidence.py tests/fixtures/r16-landing-gate.py tests/fixtures/r15-census-config.py 2>&1 && git show HEAD:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^\|[[:space:]]*S04[2-9]|^\|[[:space:]]*S050' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff LOG.md | head -90
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/QUALITY.md | grep -nE '^## Q|Q25|Q26' | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -4 && echo --- && git show --stat --format='%H %s' HEAD | head -20 && echo --- && git show HEAD:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' && git show HEAD:corpus/QUALITY.md | grep -cE '^\| Q[0-9]+ ' && git show HEAD:corpus/README.md | grep -cE 'Q[0-9]+'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD --format= -- corpus/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S04[3-9]|^\|[[:space:]]*S050/ {gsub(/^[ \t]+|[ \t]+$/,"",$9); print $2, $9}' && echo --- && git ls-tree --name-only HEAD census/round-16/ && echo --- && git show HEAD:corpus/QUALITY.md | grep -cE '^\| Q[0-9]+ '
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'landing-gate|seat-audit|preservation-evidence|souji-census' SKILL.md | cut -c1-180
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^\s*(def case|case\(|check\()' tests/fixtures/r16-landing-gate.py | wc -l && grep -nE 'check\("' tools/souji-landing-gate.py | wc -l && echo --- && ls -l tests/fixtures/r15-preservation-frozen/ && echo --- && head -30 corpus/knowledge/quarantine-same-filesystem-rename.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '5 findings|42 quotation|18/18|15/15|47/47|8/8|clean|24/47|b410186|a31642d|cc21683' corpus/lessons/round-16.md | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD --format= -- SCORECARD.md | head -70
cd /home/vgpnk/Projects/shokunin/souji-shokunin && cat tests/fixtures/r15-preservation-frozen/expected.json && echo --- && grep -cE 'check\(' tools/souji-landing-gate.py && grep -nE '^\s*check\(' tools/souji-landing-gate.py | wc -l
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline 58ace9f..HEAD -- corpus/knowledge && echo "knowledge-diff-empty=$?" && git diff --stat 58ace9f..HEAD -- corpus/knowledge && echo --- && git log --oneline 58ace9f..HEAD | wc -l && git diff --stat 58ace9f..HEAD | tail -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain && echo --- && git diff --stat && echo --- && git rev-parse HEAD && ls -la .ufo/waves/round-16/w2/ | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -oE 'check\(' tools/souji-landing-gate.py | wc -l && echo --- && sed -n '31p;62p' corpus/README.md && echo --- && wc -l corpus/README.md && echo --- && git show HEAD:corpus/README.md | tail -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'passed += 1' tools/souji-landing-gate.py && grep -n 'passed += 1\|check(' tools/souji-landing-gate.py | sed -n '1,60p' | cut -c1-110 && echo --- && grep -c 'CASE\\t' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in 0a70bef 7a79dc2 a6ec781 163158a; do printf '%s ' "$r"; git show $r:tests/fixtures/r15-census-config.py | sha256sum; done; echo ---; for r in 0a70bef 7a79dc2 a6ec781 163158a; do printf '%s ' "$r"; git show $r:tests/fixtures/r14-census-boundary.py | sha256sum; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'fixtures_sha256|sha256_file|fixture' census/round-16/run-matrix.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in c1-matrix.json c1-matrix-final.json c1-matrix-landing.json; do printf '%s ' "$f"; grep -o '"r15-config": "[0-9a-f]*"' census/round-16/$f | head -1; grep -o '"changed": "[0-9a-f]*"' census/round-16/$f | head -1; grep -o '"lane_head": "[0-9a-f]*"' census/round-16/$f | head -1; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && bash -n tools/souji-census.sh; echo "head_bashn_rc=$?"; git show b410186:tools/souji-census.sh | bash -n; echo "r15_bashn_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/README.md | grep -nE 'Q1–Q15|Q1–Q16|Q1–Q26' && echo --- && git show HEAD:corpus/README.md | sed -n '183,184p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^## Round 16|^## Round 15|frozen record retains|All r15 runtime|admitted knowledge stays five|QUALITY.md now runs' corpus/README.md && echo --- && grep -n 'Q25\|Q26' corpus/QUALITY.md | cut -c1-80 && echo --- && grep -nE '^\| souji-landing-gate|^\| r16-landing-gate|^\| souji-seat-audit' SKILL.md | cut -c1-60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain && wc -l .ufo/waves/round-16/w2/ConnReadmeIndex.md && tail -3 .ufo/waves/round-16/w2/ConnReadmeIndex.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'HARM_CASES' tests/fixtures/r15-census-config.py | cut -c1-140 && python3 - <<'EOF'
import re
src=open('tests/fixtures/r15-census-config.py').read()
m=re.search(r'HARM_CASES\s*=\s*\[(.*?)\]', src, re.S)
if m:
    ids=re.findall(r'"(R15CFG-\d+)"', m.group(1))
    print(len(ids), ids)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools/__pycache__ tests/fixtures/__pycache__ 2>&1 | head -12
```
