# ConnSiblingOverlap2 — round 16, wave 2 (FALSIFY): cross-domain re-check R6

**Seat:** connector (leaf). **Declared axis:** calibration. **Read-only:** no lane file
edited; no sibling gate run; no census executed. **Targets named by the assignment:**
tameshi pins and the kumitate round gate, re-read at first 80 lines of `PROVINCE.md` /
`SKILL.md`, then resolved to exact bytes.

**Revisions read (all clean for the files cited):** souji HEAD `163158a706352f1c0ee3521c4da2e5289970db57`
(base `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`); tameshi HEAD `017a2b0c0d1a8fe513e41710416c87b9d6ef9ae9`;
kumitate HEAD `1770305fae20826b39905a8251ddeca6b4957ac4`. souji gate bytes:
`e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`
(`tools/souji-landing-gate.py`, working tree = HEAD).

**HEAD note:** the assignment names `a6ec781` as lane HEAD; at read time HEAD has advanced
to `163158a` ("lesson, sources S043–S050, Q25/Q26, LOG correction and entries, SCORECARD,
SKILL, README"), whose parent is `a6ec781`. The newer commit is what makes S043–S050
committed and the lesson present, so F4/F8 below are stated at `163158a`; the tool itself
last changed at `a6ec781` and its bytes are unchanged since.

## 1. Axes

- **Calibration (judged here):** does the R6 evidence line cite the right owner for each
  rule, at a revision where the citation resolves, without inheriting a sibling's stale
  text?
- **Contract (second-order, improves):** name proximity between souji's "landing gate"
  and kumitate's `round-gate` / `kumitate-round-gate-v1`.
- **Operability (untouched):** no detector behavior is changed by anything proposed.

## 2. Falsification results

| # | Claim under test | Pointer | Verdict | Smallest fix |
|---|---|---|---|---|
| F1 | tameshi's leg count is seven, internally consistent | `tameshi-shokunin/PROVINCE.md:51-55` vs `:28-29` | **fails (sibling-internal)** | tameshi appends `:29 "six" → seven`; souji cites `:49-57` only |
| F2 | `tools/mutate-and-run.sh:84-89` is the six-leg anchor | `tameshi-shokunin/PROVINCE.md:56-57` | **partial (revisionless range)** | append `(at 606716f)` |
| F3 | wave-1's rule "pin mismatch ⇒ could-not-evaluate/SETUP, never a verdict" | `w1/SiblingOverlap.md` §3, runtime bullet | **fails (scope overreach)** | split by shape (below); landed tool already holds |
| F4 | the required scope sentence landed in the tool | `tools/souji-landing-gate.py:16-24` | **partial (not landed)** | one sentence in the Scope paragraph |
| F5 | tameshi's round-gate pin resolves to real, current bytes | `tameshi PROVINCE.md:52-54` | **holds** | none |
| F6 | kumitate owns `round-gate` lane-scoped, not fleet conformance | `kumitate SKILL.md:589,599-605,601,727-731` | **holds** | none |
| F7 | kumitate carries seven gates; `sources-check` entered at `1a8eed5` | `tameshi PROVINCE.md:61-63` | **holds** | none |
| F8 | SOURCES S043–S050 are committed at souji HEAD | `corpus/SOURCES.md` at `163158a` | **holds** | none |

### F1 — tameshi's own province contradicts its round-16 append (fails)

At tameshi HEAD `017a2b0` (`git show HEAD:PROVINCE.md`), line 29 still reads:

> "measured or now governs: **the six recorded mutation legs' gates** as read-only primary
> surfaces"

while the round-16 append at `:51-55` reads "The recorded mutation legs are now **seven**,
not six", naming kumitate `scripts/round-gate.mjs`. The append's own correction list
(`:59-66`; the wave-2 note at `:68-71` addresses a different bullet) corrects lines 8, 35
and 26 only; line 29 is not corrected. Wave 1 cited
`tameshi PROVINCE.md:28-33` as the primary-surface authority without noting this, so a
souji report that copies that citation propagates "six" while the same report's R6 line
says "seven". **Verdict: fails** as an internal-consistency claim; the seven-leg bytes
themselves are correct (`:51-55`). **Smallest fix:** tameshi appends one bullet
`:29 "six" → seven (see :51)`; souji's report cites `:49-57` as the leg-count authority
and does not restate `:29`. Reported, not edited (tameshi `PROVINCE.md:14-17`).

### F2 — `:84-89` is a historical six-leg range (partial)

At tameshi HEAD `017a2b0`, `tools/mutate-and-run.sh` (clean) resolves:

- `:84` = `# expectation:`
- `:85-91` = the seven legs (`js-kimi-census` … `js-round-gate`)
- so `:84-89` = the lead-in plus **five** legs, not six.

The six-leg range resolves only at `606716f`, where `git show 606716f:tools/mutate-and-run.sh`
lines 84-89 are exactly the six legs. The sentence gives the correct current range
(`:85-91`) in the same breath, so a careful reader self-corrects; an unqualified reader at
HEAD does not. **Verdict: partial** — true at a revision, not at HEAD, and tameshi's own
rule is that a reader on a differing revision re-resolves rather than trusts
(`SKILL.md:55-56`). **Smallest fix:** write "`:84-89` at `606716f`".

### F3 — wave-1 over-generalized tameshi's SETUP rule; following it would empty detector 2 (fails)

Wave 1 (`w1/SiblingOverlap.md` §3, "Runtime — pin resolution") required:
"must report a missing repo/rev/blob **or a mismatch** as could-not-evaluate/SETUP, never
as a red/green verdict". That is a misapplication by shape:

- tameshi's SETUP rule is **replay-scoped**: rule 4 under the ledger, "SETUP is not a
  verdict. A missing repo/rev/blob, a pin mismatch, or a refused sub-sweep means *cannot
  verify*" (`SKILL.md:989-992`), immediately followed by rule 5, "The ledger proves the
  instrument, not the gates" (`:993-997`), and the replay mechanics at `:941-948`.
- the **audit/reading shape** classifies instead of refusing: `current` / `stale` /
  `drift` is a reading table (`SKILL.md:1031-1036`), not a SETUP refusal.
- souji's landing gate is the reading shape: its stated defect 2 is "A frozen pin
  matching no committed bytes" (`tools/souji-landing-gate.py:9-11`), which it reports as
  `LG-FROZEN-PIN` (`:399-422`) with exit 1 (`:585`); exit 2 is reserved for
  could-not-evaluate — usage, unknown rev, no `SKILL.md`, missing waves dir, git failure
  (`:31-32`, `:586-588`).

Implemented literally as wave-1 wrote it, a pin mismatch would become exit 2 and the r15
M2 defect would never be reported — the detector would be vacuous on the exact arm it was
built to re-derive. Wave-1's own §1 detector table lists `LG-FROZEN-PIN`, so the two
sections contradict each other. **Verdict: wave-1 bullet fails; the landed tool holds.**
**Smallest fix (text only):** replace the bullet with the shape split — *unresolvable
rev/repo/blob → exit 2 could-not-evaluate; an audited pin that names no committed bytes →
`LG-FROZEN-PIN` finding, exit 1* (tameshi's replay-SETUP rule cited as replay-scoped, not
general).

### F4 — the name-proximity scope sentence did not land (partial)

`grep -c "kumitate\|conformance\|round-gate-v1\|tameshi" tools/souji-landing-gate.py` → **0**
at souji HEAD `163158a`. The header bounds scope at `:16-18` ("landing-claim consistency
and failure-channel carry only. It is NOT a disclosure-enforcement or behavioral-regression
suite") — a real boundary, but not the one at risk: nothing distinguishes this gate from
kumitate's `round-gate.mjs` / contract `kumitate-round-gate-v1`. The lesson carries it no
better: `corpus/lessons/round-16.md` at HEAD has zero occurrences of
`kumitate|conformance|round-gate|tameshi|SETUP|seven|six` and zero `CROSS-DOMAIN` lines.
**Verdict: partial** — wave-1 named the risk, nothing landed. **Smallest fix:** one
sentence in the Scope paragraph: "Not `kumitate-round-gate-v1` and not fleet conformance
(kumitate-shokunin/SKILL.md:727-731); audits souji's own round artifacts only." No re-pin
was observed to be needed: `tests/fixtures/r16-landing-gate.py` carries `pin`/`sha256`
references only for frozen-record subjects, not for the gate's own bytes, and none of the
files read here pins `tools/souji-landing-gate.py`; the gate's bytes are recorded above
for the next reader.

### F5 — the pin resolves, and two lanes independently agree (holds)

Checks against kumitate's object store:

- `git cat-file -t 364f1d5954158ef8844bca4a5fef57b05d2f2ca5` → `commit`
- `git show 364f1d5…:scripts/round-gate.mjs | sha256sum` →
  `f890e277af83a78f2dd265e442c8c5912dc3975a36b18ae1be927022a834d3e9` — identical to
  tameshi's `PROVINCE.md:53-54`
- `git merge-base --is-ancestor 364f1d5… HEAD` → true (kumitate HEAD `1770305`)
- `git show HEAD:scripts/round-gate.mjs | sha256sum` → the same `f890e277…`; worktree
  clean (`git status --porcelain -- scripts/round-gate.mjs` empty)
- kumitate's **own** proxy stanza independently pins the same blob:
  `SCORECARD.md:297` `pin.round-gate=f890e277af83…`

By tameshi's reading table (`SKILL.md:1033`) the pin is `current`, not `stale`, not
`drift`. This is stronger than wave-1's single-sided citation: the R6 line can say the
bytes are dual-pinned and current, not merely "tameshi claims".

### F6 — kumitate's ownership boundary is as wave 1 stated (holds)

`kumitate-shokunin/SKILL.md:601` registry row `round-gate` (entry
`node scripts/round-gate.mjs [--round N] [--reports-dir DIR --main-repo DIR] [--tracked]`
→ `ROUND_GATE:`, self-test `--selftest`); `:589` "All seven are gates"; the seven rows are
`:599-605` (cite-check, surface-probe, round-gate, proxy-check, claims-check, kimi-census,
sources-check). The scope sentence holds verbatim at `:727-731`: it audits "THIS lane's own
round artifacts — a tripwire + integration smoke, not a guarantee", with the fleet-
conformance boundary assigned to the integrator. `kumitate PROVINCE.md:21` still lists
"isolation substrates … git worktrees" as a **queued frontier** row, so git-config/worktree
semantics remain unclaimed and souji must not write that knowledge.

### F7 — seven kumitate gates, `sources-check` at `1a8eed5` (holds)

`git log --all -- scripts/sources-check.mjs` gives three commits, earliest `1a8eed5`
("round-34: sources-registry gate + SOURCES/QUALITY …"). tameshi's correction is accurate.

### F8 — SOURCES S043–S050 at souji HEAD (holds)

Each of S043, S044, S045, S046, S047, S048, S049, S050 is present in
`git show HEAD:corpus/SOURCES.md`. (S043/S048/S050 back the parse checks; S044–S047/S049
back config semantics.)

## 3. R6 — final cross-domain evidence line (corrected, paste-ready)

CROSS-DOMAIN: frozen-pin and round-gate ownership are split, and the two sides now agree on
bytes — tameshi records kumitate `scripts/round-gate.mjs` as its seventh read-only
mutation-leg surface at rev `364f1d5954158ef8844bca4a5fef57b05d2f2ca5` / blob sha256
`f890e277af83a78f2dd265e442c8c5912dc3975a36b18ae1be927022a834d3e9` (tameshi
`PROVINCE.md:51-55`; "not a service run and needed no opt-in", `:56`), kumitate
independently pins the same blob in its own proxy stanza (`pin.round-gate=f890e277…`,
`SCORECARD.md:297`), the pinned revision is an ancestor of kumitate HEAD `1770305`, and the
live blob is byte-identical with a clean worktree, so the pin reads `current` by tameshi's
own table (`SKILL.md:1033`) — while kumitate's instrument remains lane-scoped ("audits THIS
lane's own round artifacts — a tripwire + integration smoke, not a guarantee",
`SKILL.md:727-731`; registry row `:601`), and souji's `tools/souji-landing-gate.py`
(bytes `e7d2439d…` at souji HEAD `163158a`, base `a6ec781`) therefore audits only souji's
own round artifacts, claims neither `kumitate-round-gate-v1` nor fleet conformance, and
splits pin failures by shape: an unresolvable rev/repo/blob is exit 2 could-not-evaluate
(`tools/souji-landing-gate.py:31-32,586-588`), while an audited frozen pin that names no
committed bytes is the `LG-FROZEN-PIN` finding itself (`:399-422`, exit 1 at `:585`) — the
r15 defect it exists to re-derive, not a SETUP refusal (tameshi's SETUP rule is
replay-scoped: `SKILL.md:941-948,989-992`). The leg count is seven, per tameshi
`PROVINCE.md:51-55`; `PROVINCE.md:29` still says "six" and is a sibling-side stale line,
reported to tameshi, not absorbed.

## 4. Proposed move (one, bounded)

**Adopt the shape-split pin rule and the seven-leg authority in the r16 report/lesson
text.** Concretely: (a) replace wave-1's §3 "mismatch ⇒ SETUP" bullet with the two-arm
sentence in F3; (b) cite tameshi `PROVINCE.md:49-57` (not `:28-33`) wherever the report
states the mutation-leg count; (c) add the F4 scope sentence. Text only — no tool behavior,
no census, no gate, no mutation leg, no sibling code touched.

**Affected axes:** calibration improves on attribution (each rule cited at its owner and
scope) and citation resolvability (no unqualified historical line ranges). Contract
improves (name proximity named). Operability unchanged (no detector edit); if (c) is put in
the header instead of only the report, it is a docstring-only change and the gate's own
bytes are not pinned anywhere.

**Why not "keep the gate as is and say nothing":** the landed behavior is already correct,
but the report as drafted would carry a rule that, if implemented, would delete detector 2.
Leaving it would make the round's calibration axis rise on tool behavior while the prose
contradicts it — the exact attribution error C2 exists to catch.

## 5. Risks and second-order effects

- **Fail-closed appearance.** Splitting "mismatch" out of SETUP could read as weakening an
  arm. Mitigation: the exit-2 arm stays for unresolvable repo/rev/blob/git failure, and the
  mismatch arm becomes a *finding* (exit 1), which is strictly more fail-closed than
  "could not evaluate".
- **Cross-lane coupling.** Citing kumitate's `SCORECARD.md:297` makes the R6 line depend on
  a lane-internal stanza; state it as a reading at kumitate HEAD `1770305`, so a later
  re-pin becomes a dated fact, not a drift.
- **Sibling text is moving.** tameshi advances its own round concurrently (HEAD `017a2b0`);
  the pin evidence is object-level (`364f1d5` + blob hash + ancestry) and does not depend on
  tameshi HEAD, but line numbers for `PROVINCE.md:29` are a snapshot — the fix is for
  tameshi's own append, not for souji to assert later.
- **No adoption of the sibling's instrument.** Nothing here proposes adding souji to
  tameshi's ledger; a kill-rate claim would require an opt-in service run with a pinned
  revision (tameshi `PROVINCE.md:56` records the seventh leg as a read-only probe, no
  opt-in), and souji makes none.

## 6. Verification performed

- Pin resolution exercised read-only against the kumitate object store: `cat-file -t`,
  `show <rev>:<path> | sha256sum`, ancestry, HEAD blob hash, worktree cleanliness.
- Line-range claims resolved at the exact revisions named (`git show HEAD:...`,
  `git show 606716f:...`), not trusted from prose.
- Absence claims measured by count (`grep -c` → 0 for the scope words; `CROSS-DOMAIN` count
  0 in the lesson).
- No gate, census, selftest or mutation leg was executed; no file outside this report was
  written; no sibling file was modified.

STATUS: ok

## Commands

```bash
ls -d /home/vgpnk/Projects/shokunin/*/ 2>/dev/null | head -50
for d in tameshi-shokunin kumitate-shokunin; do echo "== $d =="; ls -la /home/vgpnk/Projects/shokunin/$d/PROVINCE.md /home/vgpnk/Projects/shokunin/$d/SKILL.md 2>&1; done
cd /home/vgpnk/Projects/shokunin/kumitate-shokunin && git rev-parse HEAD && git cat-file -t 364f1d5954158ef8844bca4a5fef57b05d2f2ca5 2>&1 && git show 364f1d5954158ef8844bca4a5fef57b05d2f2ca5:scripts/round-gate.mjs 2>/dev/null | sha256sum && git ls-tree -r --name-only 364f1d5954158ef8844bca4a5fef57b05d2f2ca5 -- scripts/ 2>&1
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && sed -n '80,95p' tools/mutate-and-run.sh 2>&1; echo "---rev"; git log --oneline -3 -- tools/mutate-and-run.sh 2>&1
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1 | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w2-spec.json'))
print(json.dumps({k:v for k,v in d.items() if k!='items' and k!='tasks'},indent=1)[:2000])
items=d.get('items') or [t for t in d.get('tasks',[])]
for it in items:
    s=json.dumps(it)
    if 'SiblingOverlap2' in s or 'SiblingOverlap' in s:
        print('===MATCH==='); print(json.dumps(it,indent=1)[:4000])
"
cd /home/vgpnk/Projects/shokunin/kumitate-shokunin && echo "== PROVINCE numbered ==" && cat -n PROVINCE.md | sed -n '8,30p' && echo "== log sources-check ==" && git log --oneline --all -- scripts/sources-check.mjs | tail -5 && echo "== 1a8eed5 ==" && git show --stat --oneline 1a8eed5 2>&1 | head -12 && echo "== round-gate at HEAD vs pin ==" && git show HEAD:scripts/round-gate.mjs | sha256sum && git cat-file -p 364f1d5954158ef8844bca4a5fef57b05d2f2ca5 | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "kumitate\|conformance\|round-gate\|tameshi\|fleet" tools/souji-landing-gate.py | head -30 && echo "== header 1-40 ==" && cat -n tools/souji-landing-gate.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && echo "== PROVINCE numbered 12-60 ==" && cat -n PROVINCE.md | sed -n '12,60p' && echo "== mutate-and-run 78-95 ==" && cat -n tools/mutate-and-run.sh | sed -n '78,95p'
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && grep -n "false anchor\|uncommitted\|git show <rev>\|current\|stale\|drift\|re-pin\|SETUP" SKILL.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== pin resolution code ==" && grep -n "ls-tree\|cat-file\|sha256\|FROZEN_PIN\|LG-FROZEN" tools/souji-landing-gate.py | head -30 && echo "== exit mapping ==" && sed -n '520,600p' tools/souji-landing-gate.py | grep -n "return 2\|exit\|SETUP\|could"
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && echo "== SKILL 150-157 ==" && cat -n SKILL.md | sed -n '150,157p' && echo "== SKILL 939-949 ==" && cat -n SKILL.md | sed -n '939,949p' && echo "== SKILL 1031-1036 ==" && cat -n SKILL.md | sed -n '1031,1036p' && echo "== SKILL 1080-1090 ==" && cat -n SKILL.md | sed -n '1080,1090p'
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && echo "== parent 05a2247^ mutate-and-run 82-92 ==" && git show 05a2247^:tools/mutate-and-run.sh 2>/dev/null | sed -n '82,92p' && echo "== 606716f 84-91 ==" && git show 606716f:tools/mutate-and-run.sh 2>/dev/null | sed -n '84,91p' && echo "== PROVINCE rev ==" && git log --oneline -2 -- PROVINCE.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== grep scope words ==" && grep -c "kumitate\|conformance\|round-gate-v1\|tameshi" tools/souji-landing-gate.py; echo "rc=$?"; echo "== git tree named paths ==" && git ls-tree -r --name-only HEAD -- corpus/lessons .ufo/waves/round-16 corpus/SOURCES.md 2>&1 | head -40 && echo "== SOURCES S043-S050 ==" && grep -n "^| S04[3-9]\|^| S050" corpus/SOURCES.md | cut -c1-220
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && echo "== SKILL 984-1012 ==" && cat -n SKILL.md | sed -n '984,1012p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD -- corpus/lessons corpus/knowledge 2>&1 | tail -20; echo "== w1 landinggate claims =="; grep -n "conformance\|kumitate\|round-gate\|not.*fleet\|SETUP\|mismatch" .ufo/waves/round-16/w1/LandingGate.md | head -25
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "mutation\|kill-rate\|leg\|tameshi\|kumitate" .ufo/waves/round-16/w1/DraftReportSkeleton.md | head -20; echo "== souji PROVINCE round-gate =="; grep -n "round-gate\|kumitate\|tameshi\|conformance\|mutation" PROVINCE.md | head -20
cd /home/vgpnk/Projects/shokunin/kumitate-shokunin && sed -n '595,606p' SKILL.md | cut -c1-140; echo "== round-gate selftest evidence name =="; grep -n "VERDICT: PASS\|selftest" scripts/round-gate.mjs | head -8
cd /home/vgpnk/Projects/shokunin/tameshi-shokunin && echo "== HEAD province 27-32,49-57 ==" && git show HEAD:PROVINCE.md | cat -n | sed -n '27,32p;49,57p' && echo "== dirty? ==" && git status --porcelain -- PROVINCE.md tools/mutate-and-run.sh; echo "== HEAD commit ==" && git rev-parse --short HEAD
cd /home/vgpnk/Projects/shokunin/kumitate-shokunin && echo "== dirty round-gate? ==" && git status --porcelain -- scripts/round-gate.mjs; echo "== HEAD=pin? ==" && [ "$(git show HEAD:scripts/round-gate.mjs | sha256sum | cut -d' ' -f1)" = "f890e277af83a78f2dd265e442c8c5912dc3975a36b18ae1be927022a834d3e9" ] && echo MATCH || echo DIFF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== HEAD lesson greps ==" && git show HEAD:corpus/lessons/round-16.md | grep -n "kumitate\|conformance\|round-gate\|tameshi\|SETUP\|seven\|six" | head -20; echo "== HEAD sources S043-S050 count ==" && git show HEAD:corpus/SOURCES.md | grep -c "^| S0[45][0-9] " ; echo "== HEAD landing-gate identity ==" && git rev-parse --short HEAD && git log --oneline -1 -- tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/kumitate-shokunin && echo "== ancestry ==" && git merge-base --is-ancestor 364f1d5954158ef8844bca4a5fef57b05d2f2ca5 HEAD && echo ANCESTOR || echo NOT-ANCESTOR; echo "== proxy stanza pin ==" && grep -n "pin.round-gate" SCORECARD.md | head -3; echo "== head ==" && git rev-parse --short HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== HEAD log 6 ==" && git log --oneline -6 && echo "== status ==" && git status --porcelain | head -10 && echo "== lesson head ==" && git show HEAD:corpus/lessons/round-16.md | sed -n '1,12p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "Scope\|scope\|not.*fleet\|name proximity\|name-proximity\|conformance" .ufo/waves/round-16/w1/LandingGate.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== 394-422 ==" && cat -n tools/souji-landing-gate.py | sed -n '394,422p' && echo "== exit mapping ==" && grep -n "exit.*= 1\|exit.*= 2\|except" tools/souji-landing-gate.py | head -12 && echo "== lesson crossdomain ==" && git show HEAD:corpus/lessons/round-16.md | grep -c "CROSS-DOMAIN"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for n in 043 044 045 046 047 048 049 050; do git show HEAD:corpus/SOURCES.md | grep -q "^| S$n |" && echo "S$n present" || echo "S$n MISSING"; done; echo "== landing-gate pinned anywhere? =="; grep -rn "souji-landing-gate.py" tests/fixtures/r16-landing-gate.py 2>/dev/null | grep -i "sha\|pin" | head -5; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -l tests/fixtures/r16-landing-gate.py 2>&1; grep -n "sha256\|pin" tests/fixtures/r16-landing-gate.py 2>/dev/null | head -8; echo "== gate bytes =="; sha256sum tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin && echo "== cite-check row ==" && grep -n "^| cite-check" kumitate-shokunin/SKILL.md; echo "== full revs ==" && git -C souji-shokunin rev-parse HEAD && git -C tameshi-shokunin rev-parse HEAD && git -C kumitate-shokunin rev-parse HEAD && git -C souji-shokunin rev-parse a6ec781
```

Tool-level reads (not shell), all exact named paths: `read` on `skill://godspeed`;
`souji-shokunin/.ufo/waves/round-16/` and `.../w1/` directory listings;
`souji-shokunin/.ufo/waves/round-16/w1/SiblingOverlap.md` (full);
`tameshi-shokunin/PROVINCE.md:1-80`, `tameshi-shokunin/SKILL.md:1-80`,
`kumitate-shokunin/PROVINCE.md:1-80`, `kumitate-shokunin/SKILL.md:1-80`; `grep` on
`kumitate-shokunin/SKILL.md` for the gate registry rows. No recursive search, no lane tree
walk, no sibling gate execution, no census, no files outside this report written.
