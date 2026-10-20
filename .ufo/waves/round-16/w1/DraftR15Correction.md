# DraftR15Correction — r15 census understatement correction drafts

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Scope: draft append-only correction texts for r15 understatements of the non-parsing census. No lane file was edited; this report is the only write.

## Measured facts (observed this seat)

| revision | check | result |
|---|---|---|
| a31642d | `git show a31642d:tools/souji-census.sh \| bash -n` | exit 0 |
| cc21683 | same | exit 0 |
| b410186 (r15 landing) | same | exit 2: `syntax error near unexpected token '}'` at line 1368 |
| b410186 | `git show b410186:tools/souji-census.sh \| shellcheck -S error -` | exit 1: SC1046 (line 1324, unmatched `if`), SC1047/SC1072 (line 1368, `}`), SC1073 |
| cbf688a (HEAD) | same as bash -n | exit 0 (syntax only; no behavioral claim from this seat) |

- b410186 script: 1995 lines; cbf688a script: 1784 lines.
- `git diff --stat b410186 cbf688a -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md tools/souji-census.sh`: only `tools/souji-census.sh` changed. SKILL.md, SCORECARD.md, round-15.md and LOG.md are byte-identical between b410186 and cbf688a (sha256 matched for SKILL.md, SCORECARD.md, round-15.md).
- Adjacent artifacts parse at both revisions (`ast.parse` only): `tools/souji-preservation-evidence.py`, `tests/fixtures/r15-census-config.py`.
- Lane convention: corrections are appended, never rewritten. Prior forms: SCORECARD `Correction (r12 post-review, 2026-10-19):` and `Correction (r13):` paragraphs placed directly after the axes table; SKILL/lesson corrections as appended sections; LOG corrections as new `## <date> — …` entries ("Corrections to earlier claims are new entries, never rewrites", LOG line 31).

## Understatements found

1. **SCORECARD.md line 15 (operability row)**: "candidate repair … landed without red-before/green-after execution", "Numeric delta 0". Understated: the landed census did not parse. "Delta 0" means legacy-unmapped, not unchanged.
2. **SKILL.md line 138 (census verdict-map row)**: lists codes with no parse-failure row. Exit 2 is defined as usage / malformed baseline / path-protected; bash exits 2 on the r15 syntax error, so a parse failure would be misread as a caller error.
3. **SKILL.md line 167 (Known surfaces, "Repeatable fleet census")**: presents the census as repeatable with no r15 caveat. At b410186 it was not runnable.
4. **corpus/lessons/round-15.md lines 95–96 and C1 row lines 98–100**: "unverified candidate" / "unprovable; NOT admitted" omits the measured blocking defect (non-parsing, exit 2; shellcheck exit 1).
5. Adjacent (same class, not named in the assignment but should be appended in the same sweep): **SKILL.md lines 226–231** ("lands an unverified value/effect-aware candidate") and **LOG.md lines 778–787** ("Landed source candidates: tools/souji-census.sh …").

Verdict on the r15 C1 "unprovable; NOT admitted" disposition: still correct. The correction adds a measured defect; it does not upgrade any claim.

## Draft A — SCORECARD.md (insert directly after the axes table, before the `Correction (r12 post-review …)` paragraph at line 17)

```
Correction (r16 sweep, 2026-10-20): the r15 operability row above is
understated. At the r15 landing commit b410186, `tools/souji-census.sh` did
not parse: `git show b410186:tools/souji-census.sh | bash -n` exits 2
(syntax error near unexpected token `}`, line 1368), and
`shellcheck -S error` exits 1 (SC1046/SC1047). The predecessors a31642d and
cc21683 and the later restoration cbf688a pass `bash -n` (exit 0). "Numeric
delta 0" means legacy-unmapped, not unchanged: at b410186 the census was a
measured non-operable artifact. The cbf688a parse result is a syntax fact
only; no r15 behavioral acceptance is claimed by this note. R14
rejected-harmed debt stays OPEN. Details: `corpus/lessons/round-15.md`
(appended correction section) and the 2026-10-20 round-16 correction entry in
LOG.md.
```

## Draft B — SKILL.md (insert as an indented continuation under "Known surfaces", after line 168)

```
  Correction (r16 sweep, 2026-10-20): the "Repeatable" wording above and the
  `souji-census` row in the gate registry (line 138) predate the r15 landing
  audit. At b410186 `tools/souji-census.sh` failed `bash -n` (exit 2, line
  1368) and `shellcheck -S error` (exit 1); a script that does not parse cannot
  yield a valid census. Exit 2 in the verdict map denotes usage, malformed
  baseline or protected path; a shell parse failure also exits 2 and must not
  be read as a caller error. At cbf688a the script passes `bash -n` (exit 0);
  that is a syntax fact only. Historical lines are unchanged.
```

## Draft C — SKILL.md (append directly after line 231, end of the round-14/15 section)

```
Correction (r16 sweep, 2026-10-20): "lands an unverified value/effect-aware
candidate" above understates the r15 landing. The b410186 census failed
`bash -n` (exit 2, line 1368) and `shellcheck -S error` (exit 1), so it was
not runnable at its landing revision. cbf688a restores parse (`bash -n` exit
0). No r15 or r16 behavioral pass is implied by this note.
```

## Draft D — corpus/lessons/round-15.md (append a new section at end of file, after line 146)

```
## Correction (r16 sweep, 2026-10-20)

Lines 95–96 ("committed as an **unverified candidate**, not a working repair")
and the C1 row (lines 98–100) understate the landed census. At the landing
commit b410186, `git show b410186:tools/souji-census.sh | bash -n` exited 2
with a syntax error near `}` at line 1368; `shellcheck -S error` exited 1 with
SC1046/SC1047 at lines 1324 and 1368. Predecessors a31642d and cc21683 pass
`bash -n` (exit 0); restoration cbf688a passes `bash -n` (exit 0).

The C1 verdict "unprovable; NOT admitted" remains correct. Its missing-evidence
column omitted a measured blocking defect: the landed artifact could not be
executed. The C2 checker and fixture parse at b410186 (`ast.parse`); that is a
syntax check only and does not change the C2 verdict. The original text above
is preserved unchanged.
```

## Draft E — LOG.md (append as a new entry at end of file, after line 815)

```
## 2026-10-20 — round 16 correction sweep: r15 census landing did not parse

Corrections (new entry; prior entries not rewritten) to the round-15 landing
entry (lines 770–787, "Landed source candidates: tools/souji-census.sh …") and
to the SCORECARD operability row, SKILL.md census row (line 138), SKILL.md
"Repeatable" line (167), SKILL.md lines 226–231, and round-15 lesson lines
95–100.

Measured: `git show b410186:tools/souji-census.sh | bash -n` exit 2 (line
1368); `shellcheck -S error` exit 1 (SC1046/SC1047). a31642d, cc21683 and
cbf688a pass `bash -n` (exit 0). The census therefore was not operable at
b410186; "numeric delta 0" means legacy-unmapped, not unchanged.

No census execution was run for this entry. Verdicts unchanged: r15 C1
unadmitted; C2 unadmitted; R14 rejected-harmed debt OPEN; certification OFF;
K5 HELD.
```

## Notes for the integrator

- Insert Draft A after the SCORECARD table (after line 15), before line 17.
- Insert Draft B after SKILL.md line 168 (inside the Known-surfaces list, as a continuation of the census bullet). Draft B is a correction for lines 138 and 167 together; the line-138 row itself stays unchanged.
- Append Draft C after SKILL.md line 231 and Draft D at the end of corpus/lessons/round-15.md.
- Append Draft E as the last entry of LOG.md.
- Line numbers refer to the files at cbf688a (HEAD for this seat); these four files are byte-identical to b410186, so the numbers also apply at the landing revision.
- The cbf688a parse result is a syntax check only. The r16 C1 fixture counts and any shellcheck-clean claim at cbf688a are the round's claims for the integrator to verify, not facts established here.

## Install / update record

None. No tool was installed or updated by this seat.

## Scope and boundary record

- Only this report was written. No lane file, historical file, operator sweep path, credential store or sibling repo was opened or modified.
- `tools/souji-census.sh` was not executed on any directory; only `bash -n` and `shellcheck` were run against `git show` output.

STATUS: drafts complete; no failed check. Integrator must append drafts A–E and verify the placement (line numbers) before applying.

## Commands

Shell commands run by this seat, verbatim:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -15 && echo --- && for r in a31642d cc21683 b410186 cbf688ab2ab28e38103e5a9417ca525b5f2ed423; do printf '%s: ' "$r"; git show "$r:tools/souji-census.sh" 2>&1 | bash -n 2>&1; echo "exit=$?"; done
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md | head -n 20 && echo --- && git diff --stat b410186 cbf688a -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md tools/souji-census.sh && echo --- && git show b410186 --stat --format='%H %s' | head -n 30 && echo --- && git show b410186:tools/souji-census.sh | wc -l && git show cbf688a:tools/souji-census.sh | wc -l && echo --- && git show b410186:SKILL.md | bash -c 'cat >/dev/null' ; git diff b410186 -- SKILL.md | head -n 5; git show b410186:SCORECARD.md | sha256sum; git show cbf688a:SCORECARD.md | sha256sum; git show b410186:corpus/lessons/round-15.md | sha256sum; git show cbf688a:corpus/lessons/round-15.md | sha256sum; git show b410186:SKILL.md | sha256sum; git show cbf688a:SKILL.md | sha256sum
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | bash -n; echo "b410186 exit=$?"; git show a31642d:tools/souji-census.sh | bash -n; echo "a31642d exit=$?"; git show b410186:tools/souji-census.sh | shellcheck -S error - ; echo "shellcheck b410186 exit=$?"; git show cc21683:tools/souji-census.sh | bash -n; echo "cc21683 exit=$?"; git show cbf688a:tools/souji-census.sh | bash -n; echo "cbf688a exit=$?"
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in tools/souji-preservation-evidence.py tests/fixtures/r15-census-config.py; do for r in b410186 cbf688a; do printf '%s@%s: ' "$f" "$r"; git show "$r:$f" | python3 -c 'import ast,sys; ast.parse(sys.stdin.read()); print("ast ok")' 2>&1 | tail -n 1; done; done; git show b410186:tests/fixtures/r15-census-config.py >/dev/null && echo fixture-present-b410186; git show b410186 --stat --format= -- tools/souji-census.sh tests | tail -n 3
```

Read/grep tool calls (exact named files only, read-only): `SKILL.md` lines 120–190 and 192–231; `SCORECARD.md` full; `corpus/lessons/round-15.md` lines 1–66, 80–110, 110–146; `LOG.md` lines 1–300, 300–420, 700–815; `_grep` for `Correction \(r|non-parsing|does not parse|did not parse|parse fails|b410186|unverified candidate` over the four named files.
