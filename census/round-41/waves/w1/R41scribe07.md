# R41scribe07 — draft QUALITY row Q99 (scribe, round 41 wave 1)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `e2a74312af4233963e44e4dbb38838ece07b8bd2` (freeze commit, `git rev-parse HEAD`).
Draft: `.ufo/waves/round-41/w1/R41scribe07/Q99.md` (one table row, intended for a new `### Round 41 criteria` table in `corpus/QUALITY.md`). No tracked file was edited. No scratch dir was created. No git mutation was run. No candidate was scored (`score-candidate.sh` covers c1/c2/c3/r1 only; Q99 is a criterion row, not a claim counter).

## Inputs read

- `corpus/QUALITY.md` table grammar: `| id | criterion | applies to | check | motivating evidence |` (round-40 table, line 234); rows Q89-Q97 at lines 236-248.
- `corpus/lessons/round-40.md` `## Mistakes`: M40-3 (line 105), M40-4 (line 112), M40-5 (line 119).
- `census/round-41/preregistration.txt`: `Round: 41`; three claim blocks C1/C2/C3 each carrying Base, Counter+sha256, Population+sha256, Control, Target, Kill; R1 block is not a `## C<n>` claim.
- `census/round-41/c2-counter.py`: the freeze-check protocol and finding classes (lines 1-30).

## Commands run and observed output

1. `sha256sum census/round-41/c2-counter.py census/round-41/c2-cases.tsv census/round-41/c1-counter.py census/round-41/c1-items.tsv` — digests `85ffe263…1e11`, `4854335a…c6`, `8860dc7a…63`, `2d2a548e…6a`. All four equal the preregistration's stated sha256 values.
2. `sha256sum census/round-41/c3-counter.py census/round-41/c3-sites.tsv census/round-41/r1-counter.py` — `9ef99e8f…1537ca`, `be363c0d…2764ea`, `8352eed4…556`. All equal the preregistration.
3. `git merge-base --is-ancestor 7eebc183f2685d1ea9b004b4de22c09a8a4035a7 e2a74312af4233963e44e4dbb38838ece07b8bd2` — exit 0 (Base is a strict ancestor; `!=` test also passed).
4. `git log --oneline --diff-filter=A -- census/round-41/preregistration.txt` — `e2a7431` (freeze commit adds the file).
5. `git ls-tree` of the seven frozen counter/population blobs at `e2a7431` vs `6682b98175b995ee4646ffd1ea6bd8a12cd353dd` (instruments commit) — `cmp` reports identical, 7 entries.
6. `for f in census/round-41/controls/{c1,c2,c3,r1}-control.txt; tail` — last non-blank line `EXIT=1` in all four (red, nonzero, per the C2 `CONTROL-NOT-RED` clause).
7. `grep -cE '^(Base|Counter|Population|Control|Target|Kill):' census/round-40/preregistration.txt` — `0`. The round-40 preregistration has `## C1/C2/C3` headers and no column-0 key line, so the frozen C2 retro case (`retro=red`) is consistent with its text; the tool was not run.
8. `grep -c '^| Q99 |' .ufo/waves/round-41/w1/R41scribe07/Q99.md` — `1`.
9. `grep -n '^### M40-[345]' corpus/lessons/round-40.md` — lines 105, 112, 119 (the three lesson headings cited).
10. `grep -n 'Q98\|Q99' corpus/QUALITY.md …` — no match: Q98 is absent at the tip; Q97 is followed directly by nothing in its table, and Q99 is unassigned.
11. `ls -la tools/souji-freeze-check.py`; `git ls-files --error-unmatch tools/souji-freeze-check.py` — `No such file or directory`; `pathspec … did not match any file(s) known to git`. The C2 tool is absent at the tip.

Not run: `python3 -B tools/souji-freeze-check.py …` (the tool does not exist; running it would be an unrun check, not a pass).

## Q99 draft (summary)

A claim is frozen only when its `## C<n>` block carries column-0 `Base:` (full40, strict ancestor of the freeze commit), `Counter:` and `Population:` (path + `sha256=`, digest equal at the freeze commit; population at least header + one item), `Control:` (committed receipt whose last non-blank line is `EXIT=<n>`, n nonzero), and non-empty `Target:` and `Kill:`; the counter and population stay byte-identical to the report tip; no dispatch/ready file under `.ufo/waves/round-<N>/` predates the freeze. Check: the protocol in `census/round-41/c2-counter.py`. Lesson: M40-3, M40-4, M40-5.

## Calibration notes (what the row does and does not claim)

- The row does not claim `tools/souji-freeze-check.py` exists. Observed: it is absent at `e2a7431` (command 11). The row says it is specified by protocol and not landed.
- Evidence pointers are verified: digests (commands 1-2), Base ancestry (3), freeze commit (4), instrument/freeze blob identity (5), red controls (6), round-40 lacks key lines (7), lesson headings (9).
- Grounding gap: M40-3..M40-5 do not name a Control receipt. The red-Control clause is therefore grounded in the r41 preregistration's own `Do-nothing control` lines, and the row's lesson column says so rather than attributing it to M40-3..5.
- Overlap: Q93 (freeze before scoring, content list) and Q95 (population committed before dispatch) cover content; Q99 is the structural block check. Q99 supersedes neither; no row is rewritten.
- Id gap: the table jumps Q97 → Q99. Q98 is not filled here; the L1 decides the id.
- Round-40's `census/round-40/preregistration.txt` carries zero key lines, so the frozen C2 `retro=red` case is consistent with the row. This is observed by grep, not by the tool.

## Verdict

- Q99 draft: WRITTEN (`.ufo/waves/round-41/w1/R41scribe07/Q99.md`), its evidence pointers verified by the commands above.
- Q99 check (the protocol): NOT RUN, tool absent at the tip. The row therefore is not claimed as enforced; it is a draft criterion pending C2's landed tool.
- Tooling: no install or update performed by this seat.
- No candidate scored; no scratch dir created; no lane, fleet, or tracked file written.
