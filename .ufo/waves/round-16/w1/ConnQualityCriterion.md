# ConnQualityCriterion — r16 Q25/Q26 criteria draft

Role: connector. Axis in scope: **calibration** (only declared axis for this seat).
Owned file: this report only. `corpus/QUALITY.md` was **not** edited — the rows below are
paste-ready for L1's integration commit.

## Delivered artifact — paste-ready `corpus/QUALITY.md` section

Insert after line 58 (the Q24 row), mirroring the r14/r15 section shape exactly (blank
line, `##` heading, blank line, header row, delimiter, rows):

```markdown
## Round 16 criteria

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q25 | A landing gate is checked at the commit that lands the artifact, not deferred to a later repair: (a) no script cited by a `SKILL.md` registry row may fail to parse; (b) no frozen pin may name bytes that its own record's `measured_commit` does not contain; (c) a seat's known-failure `STATUS:` line must be carried verbatim into the round lesson or report before the artifact is accepted again. (b) is a coherence check, not a behavioral proof: the frozen verdict still needs its own measured run at that revision. The three checks are defined over named revisions and are runnable without the round's new gate tool; the tool is a wrapper, never the criterion. Extends Q17 to frozen pins and Q23 to landing claims; supersedes nothing. | landing evidence, tools, SKILL registry | Parse: every path in the `\| name \| kind \| entry command \|` table of `SKILL.md` must satisfy `git show <rev>:<path> \| bash -n` (or an `ast.parse` equivalent) with exit 0 — at `b410186` the census exits 2 at `line 1368`, at `cbf688ab` all 16 cited scripts exit 0. Pin: every `files` digest in a `*-frozen/expected.json` must equal `sha256sum` of `git show <record.measured_commit>:<path>`, and that path must exist there — r15 pins `b5187351…` while `fc3a8d4` holds `fcff8b05…`, and `tests/fixtures/r15-census-config.py` is absent at `fc3a8d4`. Carry: each `STATUS:` line naming a failure must appear verbatim in the lesson or report — 0 matches at `b410186` for `ConfigRepair.md:7`; the predicate must be exercised on the real `ConfigRepair.md:7–13` text, never a constructed string. `python3 tools/souji-landing-gate.py --rev <rev>` may wrap these; a green wrapper with no registry row does not discharge them. | corpus/lessons/round-15-verifier-spotcheck.md:122 (R1), :124 (R3), :125 (R4); corpus/lessons/round-15.md `## Mistakes` R15-M3 and `### Final disposition` |
| Q26 | The seat probe rule is enforced by transcript audit, not by self-report. Compliance is the agreement between a seat's recorded tool-call transcript and its report's `## Commands` list; a command present in one and absent from the other is the defect, whether or not the seat disclosed it. Voiding is dependency-scoped: an out-of-class **read-only** command voids the findings that use its output; an out-of-class **executing** command voids that seat's evidence; an unreadable transcript, or any class whose input is absent (e.g. no derivable OWNED set), is `unestablished`, never clean; and an exported-transcript audit is a lower bound because rendered arguments truncate, never a proof of absence. Extends Q24; supersedes nothing. | round process, seat evidence | L1, before any acceptance, reads each cited seat's transcript (`history://<id>`, `agent://<id>`) and requires: one `## Commands` section per report (`grep -c '^## Commands$'` = 1); reported commands ⊆ transcript (no unrun claim) and transcript ⊆ reported ∪ the wave's declared read-only class (no omitted probe); every distinct command classified against the wave's allowed list, with each out-of-class line recorded by seat id, class, execute-vs-parse-only and the findings that cite it, then voided at the scope above. Seats outside the round report's citations are not audited; a missing transcript is recorded as `unestablished`. | corpus/lessons/round-15.md R15-M3; corpus/lessons/round-15-verifier-spotcheck.md:126 (R5); corpus/lessons/round-14.md:118; corpus/lessons/round-14-verifier-spotcheck.md:163 (routed defect 4) |
```

Deviations from `corpus/QUALITY.md` conventions, deliberately: the file's rule says a
criterion is *superseded* by a new row that names the row it replaces; Q25/Q26 extend
Q17/Q23/Q24 without rewriting them, so both cells say `supersedes nothing`. Both lesson
cells cite existing lines (`round-15-verifier-spotcheck.md:122,124,125,126`; `round-15.md`
R15-M3; `round-14.md:118`; `round-14-verifier-spotcheck.md:163`) — verified present in
this checkout.

## Evidence (all measured this session; probe-class only)

1. **Table shape.** `corpus/QUALITY.md:52–58` is `## Round 15 criteria` + header
   `| id | criterion | applies-to | test | lesson |` + Q22/Q23/Q24 rows. The file is
   58 lines; no `Round 16 criteria` section exists yet.
2. **Dimension (a), parse.** `SKILL.md:134–150` is the registry table
   (`| name | kind | entry command | …`), 15 rows citing 16 distinct `tools/`/`tests/`
   scripts. At `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`: 8 `bash -n` → rc 0, 8
   `ast.parse` → rc 0, i.e. 16/16 parse. At `b410186`: `git show b410186:tools/souji-census.sh | bash -n`
   → `line 1368: syntax error near unexpected token '}'`, rc 2. `bash -n` on a synthetic
   stdin line printed nothing and exited 0, so the check is parse-only (no execution, no
   writes) — safe to run on historical bytes.
3. **Dimension (b), pins — two independent defects, not one.**
   - `tests/fixtures/r15-preservation-frozen/expected.json` pins
     `tools/souji-census.sh` = `b5187351…`. Digest per revision touching that path:
     `cbf688ab fed43c71`, `b410186 dab4122c`, `552cae4 fcff8b05`, `48f8945 fd234148`,
     `43d5754 6a000c59`, `b5db5cf 11bf9cdf`. The pin matches **none**.
   - `record.json` declares `measured_commit = fc3a8d49…` and
     `runs.changed.tool = {commit: fc3a8d49…, sha256: b5187351…}`. But the census bytes at
     `fc3a8d4` hash to `fcff8b05…`, and `tests/fixtures/r15-census-config.py` **does not
     exist at `fc3a8d4`** (`git show` → "exists on disk, but not in 'fc3a8d4'").
     `tools/souji-preservation-evidence.py:215–218` states `measured_commit` is
     "format-checked, never resolved against git history", so the commit↔digest pair is
     never cross-checked by the existing checker. This is why Q25(b) is worded as
     *pin = bytes at the record's own declared revision*, not the weaker r15 R4 wording
     "no committed revision has": a lazy re-pin to any historical digest would satisfy R4
     while still being false against `measured_commit`.
4. **Dimension (c), carry.** `.ufo/waves/round-15/w1/ConfigRepair.md:7` is
   `## STATUS: INCOMPLETE — file has an unresolved syntax error`; line 11 is "The file in
   tree does NOT parse." At `b410186`, `grep -ciE 'does not parse|do not ship|syntax error'`
   over `LOG.md`, `SKILL.md`, `SCORECARD.md`, `corpus/lessons/round-15.md` →
   `0 0 0 0`. `round-15.md` `### Final disposition` instead calls the file an
   "**unverified candidate**".
5. **Q26 grounding.** `round-15-verifier-spotcheck.md:126` (R5): "Q24 landed, but seats
   again ran prohibited probes or queries … Enforce it, don't just record it."
   `round-14-verifier-spotcheck.md:163` (defect 4) is the same rule one round earlier.
   The r16 wave contract already requires a closing `## Commands` section, so Q26
   formalizes existing machinery rather than adding a new seat burden.

## Affected axes

- **calibration: improves.** Both rows convert prose obligations into assertions that
  resolve against a named revision's bytes or a recorded transcript, so a non-author can
  falsify them without trusting a new tool. The r15 class (criteria landed, enforcement
  never ran) becomes detectable at the landing commit.
- **operability, coverage, depth, freshness, adjacency: no change.** The checks are
  read-only (`git show`, `bash -n`, `ast.parse`, transcript reads); nothing executes the
  census; no knowledge entry, source row or score moves.

## Proposed move (one bounded proposal)

**Decouple the criterion from the gate tool.** Q25's test is an equation over
`git show <rev>:<path>` bytes that a person can run with coreutils + bash; the round's
new `tools/souji-landing-gate.py` is demoted from "the test" to "an independently admitted
wrapper" whose own acceptance is *reproducing red at `b410186` and green at the landing
revision*. This is a compatible synthesis of C2's tool, R4's re-pin and R5's enforcement:
all three become instances of one primitive — **an assertion must resolve against a named
revision's bytes or a recorded transcript, never against prose**. If Q25 instead names the
unlanded tool as its test, Q25 inherits the tool's admission and repeats the r15 failure
mode where the criterion exists and its enforcement never runs; the tool also currently
does not exist at `cbf688ab` (`ls tools/souji-landing-gate.py` → absent). The asymmetry is
itself evidence for the move: Q26's wrapper already exists untracked
(`tools/souji-seat-audit.py`), Q25's does not, and neither criterion should inherit its
tool's admission.

Second-order effects traced:

- **R4's repair is constrained.** Swapping `b5187351` → `fed43c71` while leaving
  `measured_commit: fc3a8d4` is still red under Q25(b) (census at `fc3a8d4` is
  `fcff8b05`; the r15 fixture is absent there). The re-pin must move `measured_commit`
  to a revision that contains all three pinned paths with matching digests.
- **R3's repair becomes mandatory text, not disclosure.** `ConfigRepair.md:7` must appear
  verbatim in the r16 lesson before `tools/souji-census.sh` is accepted again; the r15
  "unverified candidate" phrasing cannot be the carrier.
- **Self-application.** If the gate tool is added to the `SKILL.md` registry, Q25(a) makes
  it subject to `bash -n`/`ast.parse` — cheap self-consistency, not circularity.
- **Bookkeeping collision (Q10).** `corpus/README.md:31` still says "Q1–Q15" and
  `:154–155` says "Q22–Q24"; Q25/Q26 cannot land alone or Q10's closing test fails. The
  integration commit must move both lines to Q1–Q26 / Q22–Q26.
- **Source registry.** SOURCES.md currently ends at S042; C2's GNU Bash `set -n` row is
  not yet in the checkout. Q25 must **not** cite an S-number until that row lands —
  citing it now would repeat the r12-K5 nonexistent-fixture defect Q17 exists to stop.

## Reconciliation with sibling round-16 drafts (read-only)

- **Distinct reds — do not conflate.** `DraftLessonGate.md:13` is right that C1's red must be
  the routed benign-config reason at `cc21683`, never the `b410186` parse failure ("red must come
  from actual behavioral disagreement, never tool identity", `round-15.md` `## Gate`). Q25(a)'s
  `b410186` parse red is a **landing** red (R1), a different gate from C1's behavioral arm. Q25's
  applies-to is `landing evidence, tools, SKILL registry`, deliberately disjoint from Q22's
  `census, no-harm evidence`; neither row may be used as the other's red.
- **Pin coherence vs pin independence.** `DraftLessonGate.md:17` warns that a pin re-set to the
  digest of the file under test is self-referential and does not count. Agreed, and the rows above
  encode both halves: Q25(b) only requires the pin to *cohere* with the record's declared
  `measured_commit`; C2 still must produce a frozen verdict from an independent input with its
  measured revision, and Q25(b) explicitly says it is "a coherence check, not a behavioral proof".
  A pin that is merely overwritten with `fed43c71…` while `measured_commit` stays `fc3a8d4` fails
  Q25(b) because the r15 fixture is absent at `fc3a8d4`.
- **Carry predicate anti-overfit.** `DraftLessonGate.md:18` requires the defect-3 predicate to be
  tested on the real `ConfigRepair.md:7–13` text, not a constructed string. Folded into Q25's test
  cell. The planned lesson slot `DraftLessonGate.md:49` ("`ConfigRepair.md:7-13` quoted in full")
  satisfies the carry check as written, since it contains the `STATUS:` line.
- **Probe audit already has a slot.** `DraftLessonGate.md:47` reserves
  "Seat no-probe rule (R5): `<per-seat command audit, verbatim>`". Q26 defines what fills it: the
  per-seat command set from the transcript, not the report's self-description.
- **Enforcement wrapper exists for Q26, not Q25.** `tools/souji-seat-audit.py` (untracked,
  created during this wave; `ast.parse` rc 0) already implements R5 from exported
  transcripts with named classes (`V-SURFACE`, `V-LIVE-CENSUS`, `V-WRITE-SCOPE`,
  `V-EXEC`, `V-RECURSIVE`) and exit 0/1/2. Q26 adopts its shape, its major/minor split
  supplies the dependency-scoped voiding, and its declared truncation limit is written into
  the criterion. It is not committed at `cbf688ab`, so it is not yet evidence of
  enforcement; if it lands and is registry-cited, Q25(a) applies to it.
- **Live Q26 case in this wave.** `CriticDisclosureR3.md:123,130` self-reports command 6,
  `git -C /home/vgpnk/Projects/shokunin log … -- .ufo/reports/round-15/souji.md`: fleet-root
  `-C`, which the round-16 probe rule does not list (it lists lane-root `git -C`). It is
  read-only. Under Q26 that is not a severity judgment and not a confession to be credited: the
  transcript carries the command either way, and the findings that use its output are voided.
  This shows Q26 has teeth on day one and that disclosure is not the enforcement mechanism.
- **Scope of the name.** `SiblingOverlap.md:16,43–44` places `tools/souji-landing-gate.py` one
  noun from kumitate's `round-gate.mjs`. Q25 audits souji's **own** artifacts; it is not fleet
  conformance and must not be written up as such. Q25(b) adopts tameshi's committed-bytes pin
  vocabulary (`SiblingOverlap.md:17`, "a pin on uncommitted bytes is a false anchor") rather than
  inventing a taxonomy.
- **S043 does not exist yet.** `DraftLessonGate.md:19,40` correctly leaves the GNU Bash `set -n`
  row as an unfilled slot. Q25's lesson cell therefore cites only existing lesson lines; adding
  `S0xx` before the row lands would repeat the nonexistent-evidence defect behind Q17.

## Risks / contradictions (stated, not smoothed)

- **Measured contradiction with C2's "green at round end":** at the current HEAD
  `cbf688ab`, Q25(b) is **RED** — pin `b5187351…` matches no committed revision and
  `measured_commit: fc3a8d4` lacks one pinned path. Q25 cannot be shown green at
  `cbf688ab`; only a commit that edits `expected.json`/`record.json` can make it green.
  L1 must not mark Q25 green against the pre-re-pin revision.
- **Q26 is implementable, but only as a lower bound.** `tools/souji-seat-audit.py`
  (untracked, created during this wave) already reads exported transcripts
  (`→ tool(args…) ⇒ status`) and pins V-SURFACE / V-LIVE-CENSUS / V-WRITE-SCOPE /
  V-EXEC / V-RECURSIVE with exit 0/1/2. Its own docstring states that the rendered
  transcript truncates long arguments, so a clean run is not proof of absence; Q26 adopts
  that limit. Its OWNED extraction matches `OWN ONLY (...)` in the item prompt only:
  3 of 65 r16 items carry that phrase, while ownership is stated in the shared context.
  For the other 62 the write-scope class has no input and must be reported
  `unestablished`, not flagged and not passed. A transcript export is still required —
  the tool reads no transcript store directly — so Q26's enforcement remains L1's
  export + audit, not a self-report.
- **Read-only vs executing must be defined by the wave, not argued per seat.** The split
  that Q26's voiding depends on must come from the wave contract's explicit
  forbidden-execution list (this round: running the census or any copy on a real
  directory, anything touching the operator sweep, `~/.omp`, `.ufo/state`, fleet scripts).
  A seat must not reclassify a forbidden execution as "read-only" because it used a
  `--dry-run` flag or suppressed output; `--dry-run` still executes the tool.
- **Carry-check gameability.** Requiring "a `STATUS:` line" verbatim could be satisfied
  by a benign `STATUS:` line; the row restricts it to a line naming a failure. The
  failure-token list should live in the wave contract, not be invented per seat.
- **Scope limit of (a).** Only registry-cited scripts are checked; a broken non-cited
  helper passes. This is deliberate (Q23: capability wording matches the exercised
  boundary) and is stated so Q25 is not read as "every script parses".
- **Pin-binding interpretation.** Q25(b) requires the pin to match `measured_commit`'s
  bytes. A future record that legitimately measures working-tree files rather than a
  commit must declare the landing revision as `measured_commit` or it will be red. That
  is the intended tightening; the alternative (no commit binding) is exactly r15's hole.

## Verification (read-only; for L1's acceptance, not run as acceptance here)

1. `git -C <lane> show b410186:tools/souji-census.sh | bash -n; echo $?` → stderr
   `line 1368: syntax error near unexpected token '}'`, `2`.
2. `git -C <lane> show cbf688ab:tools/souji-census.sh | bash -n; echo $?` → `0`.
3. Registry parse sweep at the landing revision → 16/16 rc 0 (observed at `cbf688ab`).
4. `git -C <lane> show fc3a8d4:tools/souji-census.sh | sha256sum` →
   `fcff8b05…` ≠ pinned `b5187351…`; `git cat-file -e fc3a8d4:tests/fixtures/r15-census-config.py` → absent.
5. `for f in LOG.md SKILL.md SCORECARD.md corpus/lessons/round-15.md; do git -C <lane> show b410186:$f | grep -ciE 'does not parse|do not ship|syntax error'; done`
   → `0 0 0 0`.
6. Per r16 report: `grep -c '^## Commands$'` → `1`; L1 compares that list against
   `history://<id>` for every seat the round report cites.

STATUS: draft complete and paste-ready; `corpus/QUALITY.md` intentionally not edited
(owned-file bound). Known failure carried: Q25(b) is red at HEAD `cbf688ab` until the r15
frozen pin and `measured_commit` are re-bound. Tool installs/updates: none.

## Commands

```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/ 2>/dev/null | head -50
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md 2>/dev/null; echo "---"; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ 2>/dev/null
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15-verifier-spotcheck.md 2>/dev/null; echo "==="; ls /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/
awk 'NR>=43 && NR<=58' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md | cat -A | head -0; echo "==="; awk 'NR>=43 && NR<=58 {print NR": "$0}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tools/ | head -40; echo "=== landing gate?"; ls -la tools/souji-landing-gate.py 2>&1; echo "=== git status"; git status --porcelain | head -20; echo "=== HEAD"; git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for f in ['.ufo/waves/round-16/w1-spec.json','.ufo/waves/round-16/w1-dispatch.json']:
    d=json.load(open(f))
    s=json.dumps(d)
    print(f, len(s))
" ; echo "==="; python3 - <<'EOF'
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1-spec.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            walk(v,p+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o):
            walk(v,p+f'[{i}]')
    else:
        if isinstance(o,str) and 'ConnQualityCriterion' in o:
            print(p, '->', o[:400].replace('\n',' | '))
walk(d)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
it=d['items'][34]
for k,v in it.items():
    print(f'--- {k}:')
    print(v)
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-dispatch.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
s=json.dumps(d)
i=s.find('ConnQualityCriterion')
print(s[max(0,i-2500):i+1500])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in d['items']:
    p = it.get('prompt','')
    if 'QUALITY.md' in p:
        print('###', it['name'], '| keys:', list(it))
        print(p[:900])
        print()
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^\*\*R[1-7]|^## Routed defects|^## Decision|^## Conformance|D1, disclosure' corpus/lessons/round-15-verifier-spotcheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-preservation-frozen/expected.json 2>/dev/null | head -40; echo "=== exists in worktree?"; ls -la tests/fixtures/r15-preservation-frozen/ 2>&1 | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "HEAD digest:"; git show HEAD:tools/souji-census.sh | sha256sum; echo "=== revs touching census tool:"; git log --all --format='%H %ad %s' --date=short -- tools/souji-census.sh | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn 'Q2[0-9]\|Q1[0-9]\|criteria' corpus/README.md SCORECARD.md SKILL.md LEARNING.md 2>/dev/null | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in $(git log --all --format=%H -- tools/souji-census.sh); do printf '%s ' "$r"; git show $r:tools/souji-census.sh | sha256sum | cut -d' ' -f1; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=130 && NR<=175 {print NR": "$0}' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^\|\s*S0(4[0-9]|5[0-9])\s*\|' corpus/SOURCES.md | cut -c1-400; echo "=== bash/set -n mentions"; grep -nE 'set -n|GNU Bash|bash\.man|gnu\.org/software/bash' corpus/SOURCES.md | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/ 2>/dev/null; echo "=== matrix head"; python3 -c "
import json; d=json.load(open('census/round-16/c1-matrix.json')); print(json.dumps(d, indent=1)[:1200])" 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^- |^[0-9]+\. \*\*R[1-7]' corpus/lessons/round-15-verifier-spotcheck.md | sed -n '1,40p'; echo "=== R lines"; grep -nE 'R[1-7],|R1,|R3,|R4,|R5,' corpus/lessons/round-15-verifier-spotcheck.md | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re, pathlib
txt = pathlib.Path('SKILL.md').read_text().splitlines()
rows = [l for l in txt[133:150] if l.startswith('|') and not l.startswith('|---') and 'name' not in l.split('|')[1]]
paths = []
for r in rows:
    for p in re.findall(r'(?:tools|tests)/[A-Za-z0-9._/-]+\.(?:sh|py)', r):
        if p not in paths: paths.append(p)
print(len(rows), 'registry rows;', len(paths), 'distinct cited paths')
for p in paths: print(p, pathlib.Path(p).exists())
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in tools/souji-verify.sh tools/souji-vault-verify.sh tools/souji-census.sh tools/souji-quarantine.sh tests/fixtures/r12-maintenance-guard.sh tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh tests/fixtures/r13-quarantine-bounds.sh; do bash -n "$p" 2>&1; printf '%s rc=%s\n' "$p" "$?"; done; for p in tools/souji-cert-evidence.py tests/fixtures/r13-cert-evidence.py tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py; do python3 -c 'import ast,sys; ast.parse(open(sys.argv[1],"rb").read())' "$p" 2>&1; printf '%s rc=%s\n' "$p" "$?"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- b410186 census parse:"; git show b410186:tools/souji-census.sh | bash -n; echo "rc=$?"; echo "--- HEAD census parse:"; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | bash -n; echo "rc=$?"; echo "--- noexec demo:"; printf 'echo SHOULD_NOT_RUN\n' | bash -n; echo "rc=$? (no output above = parse only)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'));print(list(d));print(json.dumps(d,indent=1)[:900])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'revision|measured|snapshot_tampered|expected\.json|sha256' tools/souji-preservation-evidence.py | head -25
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py; do printf '%s @fc3a8d4: ' "$p"; git show fc3a8d49b52de26bef74418da96611aae34b958d:$p | sha256sum | cut -d' ' -f1; done; echo "--- pinned:"; python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/expected.json'));print(json.dumps(d['files'],indent=1))"; echo "--- measured_commit:"; python3 -c "import json;print(json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))['measured_commit'])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=7 && NR<=13 {print NR": "$0}' .ufo/waves/round-15/w1/ConfigRepair.md 2>/dev/null; echo "=== carried at b410186?"; for f in LOG.md SKILL.md SCORECARD.md corpus/lessons/round-15.md; do printf '%s: ' "$f"; git show b410186:$f 2>/dev/null | grep -ciE 'does not parse|do not ship|syntax error' ; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py; do printf '%s @b410186: ' "$p"; git show b410186:$p 2>/dev/null | sha256sum | cut -d' ' -f1; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=65 && NR<=95 {print NR": "$0}' tools/souji-preservation-evidence.py; echo "=== 210-222"; awk 'NR>=208 && NR<=222 {print NR": "$0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print('measured_commit:',d['measured_commit'])
print('fixture:',d['fixture'])
print('namespace_fixture:',d['namespace_fixture'])
for k,v in d['runs'].items():
    print(k,'tool=',v.get('tool'),'exit=',v.get('exit_code'))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^## Process deviations' corpus/lessons/round-14.md; grep -nE 'defect 4|Routed defects|defect 3' corpus/lessons/round-14-verifier-spotcheck.md | cut -c1-180; echo "=== QUALITY tail"; awk 'NR>=52 {print NR": "$0}' corpus/QUALITY.md | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=158 && NR<=172 {print NR": "$0}' corpus/lessons/round-14-verifier-spotcheck.md | cut -c1-240
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^#{2,3} ' corpus/lessons/round-14.md; echo "=== deviations mentions"; grep -niE 'deviation' corpus/lessons/round-14.md | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re
p='.ufo/waves/round-16/w1/ConnQualityCriterion.md'
lines=open(p).read().splitlines()
for i,l in enumerate(lines,1):
    if l.startswith('| Q2') or l.startswith('| id |') or l.startswith('|---'):
        # count unescaped pipes
        n=len(re.findall(r'(?<!\\)\|', l))
        print(i, 'unescaped_pipes=',n, l[:60])
EOF
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ConnQualityCriterion.md; echo "=== fleet root stray?"; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>/dev/null; ls /home/vgpnk/Projects/shokunin/.ufo/waves/round-16/w1/ConnQualityCriterion.md 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -nE 'Q2[5-9]|landing gate|landing-gate|probe rule|## Commands|transcript' DraftLessonGate.md CriticDisclosureR3.md SiblingOverlap.md DraftR15Correction.md 2>/dev/null | cut -c1-220
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && head -40 DraftLessonGate.md; echo "=== SIBLING"; head -30 SiblingOverlap.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && awk 'NR>=118 && NR<=140 {print NR": "$0}' CriticDisclosureR3.md | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && awk 'NR>=38 && NR<=52 {print NR": "$0}' DraftLessonGate.md | cut -c1-300
cd /home/vgpnk/Projects/shokunin/souji-shokunin && head -40 tools/souji-seat-audit.py; echo "=== ast"; python3 -c 'import ast;ast.parse(open("tools/souji-seat-audit.py","rb").read());print("parse ok")'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
keys=set()
for it in d['items']: keys.update(it)
print('item keys:',sorted(keys))
print('items with owned:',sum(1 for it in d['items'] if 'owned' in it))
print('top-level:',sorted(d))
EOF
echo "=== tool owned handling"; grep -nE 'owned|OWNED|report' tools/souji-seat-audit.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=45 && NR<=60 {print NR": "$0}' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
d=json.load(open('.ufo/waves/round-16/w1-spec.json'))
n_only=n_owned=0
for it in d['items']:
    p=it.get('prompt','')
    if 'OWN ONLY' in p: n_only+=1
    if re.search(r'\bOWNED\b',p): n_owned+=1
print('items:',len(d['items']),'with OWN ONLY:',n_only,'with OWNED:',n_owned)
print('context has OWNED:', 'OWNED' in d.get('context',''))
print('context has OWN ONLY:', 'OWN ONLY' in d.get('context',''))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re
p='.ufo/waves/round-16/w1/ConnQualityCriterion.md'
L=open(p).read().splitlines()
print('lines',len(L),'fences',sum(1 for l in L if l.startswith('```')),'fence_balanced',sum(1 for l in L if l.startswith('```'))%2==0)
for i,l in enumerate(L,1):
    if l.startswith('| Q2') or l.startswith('| id |'):
        print(i,'pipes',len(re.findall(r'(?<!\\)\|',l)))
print('headings:',[l for l in L if l.startswith('## ')])
EOF
echo "=== QUALITY untouched"; git diff --stat -- corpus/QUALITY.md; git status --porcelain corpus/QUALITY.md; echo "(empty above = untouched)"
```
