# deliver-quality-rows — corpus/QUALITY.md Q67-Q69 and SKILL.md gate-registry rows, corrected to what landed

Seat SwarmScribe35, round 31 wave 2. Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, preregistration
`1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, lane tip read `2c16d018e40db7c23420a2c3bb546b52957bcc25`
(branch master). Frozen contract and amendments A0-A5 read first. Supersedes the wave-1 draft
`.ufo/waves/round-31/w1/deliver-quality-q67-q69.md` (seat SwarmScribe22), which was written against
`1b81136` and therefore before C2, C3, M1 and amendments A1, A2, A3, A4, A5 landed.

Every count in the check cells below was produced by this seat at the tip; the commands are the ones that
ran, with the tip revision written out, and `<lane>` = `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Raw outputs: `.ufo/waves/round-31/w2/SwarmScribe35.md` ## Evidence.

## Block A — append to corpus/QUALITY.md after line 161 (the Q66 row, end of `## Round 30 criteria`)

Column headers follow the file's own table (`id, criterion, applies to, check, motivating evidence`), not the
wave-1 draft's `applies-to / test / lesson`.

```markdown
## Round 31 criteria

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q67 | A capability cell's count literal is bound only by a row appended after the frozen base bytes (the base bytes must still prefix the file, so an in-place edit binds nothing), and the binding must be honest. A `run:` binding re-runs a command named on the base cell line (the script's basename stem occurs there), with the script taken from the base blob, no shell, no `-c`/`-h`/`--help`/`--version`, the literal absent from the joined argv and carrying at least two integers; it matches only on exit 0 with the literal at digit boundaries in the last digit-bearing line. A `record:` binding names an unchanged record of the row's own round — a `census/round-<K>/` blob, K in that row's round set, no `waves` or `transcripts` component, outside `sources/` and not ending `.py`/`.sh`/`.html`/`.htm`/`.raw`, byte-identical at the base and at the measured revision — whose integers equal the base literal's integers as a multiset; it is a date, never a re-run, and two items may not share one occurrence. A cell that names a command is superseded only by a run row, and a superseding literal has a count shape in both branches (`[word=]N/M`, or two `word=N` fields separated by whitespace or the two bytes backslash-t). Every binding row's reason names the cell occurrence it measures: binding an occurrence to a different occurrence's record that merely prints the same integers is not a binding, and the counter cannot refuse it. An item with no honest observable stays UNBOUND and is counted as a disclosed miss; the target is never reached by substitution, and a green 41/41 is audited item by item rather than accepted. | every count literal in a SCORECARD capability cell and the rows appended for it | `python3 -B tools/souji-capability-cells.py --root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` prints `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` (rc 1, same under the v1 tool): the one UNBOUND is L29 (`SCORECARD.md:170`, `18/18`) whose record states the count as `"matched_command_count": 18`, so the row set is 40 of 41 and the miss is disclosed, not repaired. Red arms `census/round-31/records/controls-a4.tsv` (four shapes v1 accepts and A4 refuses) and `controls.tsv` `C1-junk1` through `C1-junk5`; `controls-amended.tsv` `C1-junk-A2` (v1 `mismatches=0`, A2 `mismatches=1`). Green alone is not proof: a substitution row for L29 naming `census/round-21/final-code-verification.json` prints `bound_record=1 unbound=0 mismatches=0` at rc 0, while its honest record prints `RECORD-MISMATCH` | `corpus/lessons/round-31.md` C1 and amendment A4; `census/round-31/records/c1-after-a4.txt`; substitution arm reproduced in `census/round-31/waves/w2/SwarmScribe35.md` (## Findings 1) |
| Q68 | The landing gate reads the committed record as written. A round's reports are the union of its `.ufo/waves/round-N/` reports and its committed capture `census/round-N/waves/`, an identical relative path counted once, the union read when both exist and could-not-evaluate when neither does. Every `## Seat-reported failures` section of a lesson is read, not only the first, and a heading inside a fenced block is text, not a section boundary. The pointer tokenizer keeps every real missing path as a finding while ignoring ellipsis placeholders, en-dash and hyphen line ranges, `:text` suffixes, `.captured` capture names, printf templates and letters-only prose alternations — with the limit stated as part of the rule: a missing path whose components are all letters and that carries no trailing slash is exempt, so `census/waves` is invisible while `census/waves/` is found. That blind spot is the price of G8 and is disclosed, never silent. Each carry bullet quotes its report's STATUS paragraph and ends in one disposition, `open` or `resolved@<full40>`; the gate's own token accepts seven or more hex characters (`tools/souji-landing-gate.py:113`), so this check refuses anything short of a full 40 and requires the commit to resolve. The oracle that proves the reading is unpredictable: probes are drawn at random per run and printed, because a fixed probe list is a table a gate can copy. | tools/souji-landing-gate.py, its fixtures, and the round records and lessons it scans | `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` prints a `CASE G1` to `CASE G10 PASS` line each and `cases=10 pass=10 control=FALSE-GREEN-REJECTED` (rc 0 at the tip); the same fixture with `--tool <base gate blob>` prints `cases=10 pass=3`, failing exactly G1 G3 G4 G5 G6 G7 G8. `python3 -B census/round-31/c2-counter-v3.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin` prints `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok`; base witness `fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same`. Carry: `python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --round 26 --fleet-root <fleet>` (and 27, 28) prints `findings=0` with no `LG-SEAT-UNCARRIED`, against `census/round-31/records/m1-red-before.txt` (18, 29 and 19 uncarried). Blind-spot witness: a synthetic round-19 lesson citing `census/waves` and `census/waves/` yields one `LG-DANGLING-PTR` for the slashed form only | `corpus/lessons/round-31.md` C2 and amendments A3, A5; `census/round-31/records/c2-after-v3.txt`; `census/round-31/records/m1-after.txt` |
| Q69 | A measured entry states its measurement as record lines, and its fixture must be the thing that measured. At least three backticked spans of the form `RESULT <fields>` are quoted, and every one is a whole line of the run record it cites (exact equality, not a prefix). The record carries both tool versions and both outcomes (`object_present=yes` and `object_present=no`). The fixture is re-run once with a PATH shim that logs jj and git argv and execs the real binaries, so a fixture that prints or cats a record without doing the work is rejected; then twice more with one remover neutered — M1 every `git … reflog expire`, M2 every `git … gc` and `prune`, including the `git gc` that `jj util gc` shells out to. Each mutant must exit 0, print as many `RESULT` lines as the record, differ from it, and carry strictly fewer `object_present=no` lines: removing a remover can only keep an object, so a fixture whose output does not depend on what jj and git actually did fails. The fixture takes its scratch root from `TMPDIR` and refuses with exit 2 when it is unset or resolves inside the lane or the fleet; every jj call names `-R`, every git call `-C`. | corpus/knowledge entries admitted from r31 onward, their run records and fixtures, and the counters that judge them | `python3 -B census/round-31/c3-counter-v3.py --root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` prints `SUMMARY legs=13 fail=0 f1_entries=4` (v1 `legs=11` and v2 `legs=12` also hold), L10 `result_spans=6 not_in_record=[]` and L13 `M1:rc=0,lines=17,differs=True,no=0<4=True M2:rc=0,lines=17,differs=True,no=0<4=True`. Directly: `TMPDIR=<scratch> bash tests/fixtures/r31-jj-object-clock.sh` prints two version lines and 17 `RESULT` lines byte-identical to the record (whole file diff empty); `TMPDIR= bash tests/fixtures/r31-jj-object-clock.sh` exits 2 with `ERROR: TMPDIR is unset or empty; refusing to run` | `corpus/lessons/round-31.md` C3 and amendments A0, A1; `census/round-31/records/jj-object-clock-run.txt`; A1 junk arm in `census/round-31/records/controls-amended.tsv` (v1 fail=0, v2 fail=0, v3 fail=1) |
```

## Block B — append to SKILL.md `## Gate registry`, after the `r30-jj-keep-expiry` row and before `Sources for this skill`

```markdown
| souji-capability-cells | gate | `python3 -B tools/souji-capability-cells.py --root LANE --rev REV --base BASE --list-rev PREREG [--only L01,...]` | 0 `unbound=0 mismatches=0` over `items=41`; 1 any `ITEM` line whose verdict is `UNBOUND`, `RUN-MISMATCH`, `RECORD-MISMATCH` or `BAD-ROW`; 2 could-not-evaluate (non-40-hex or unresolvable revision, enumeration absent at PREREG, git failure). `--only` also prints `partial=1` and is diagnostic, never a pass | no embedded selftest; red arms `C1-do-nothing(base)` (`unbound=22 mismatches=34`) and `C1-junk1` through `C1-junk5` in `census/round-31/records/controls.tsv`, `C1-junk-A2(non-count literal)` in `controls-amended.tsv`, four A4 shapes in `controls-a4.tsv`; green 41/41 is not reached at r31 (L29 honest miss, `unbound=1 mismatches=1`) and is reachable by a substitution binding the counter cannot refuse, so a green run is audited, never accepted | enumeration `census/round-31/c1-cells.tsv` read at PREREG, 41 items at base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; `SCORECARD.md` base bytes must prefix REV | one private `git clone --no-local` per run under `--scratch`, origin removed, deleted on exit; executes only the bound script from the base blob, never a shell; never the lane worktree | souji |
| r31-landing-gate-precision | gate | `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool PATH` | 0 a `CASE G1` to `CASE G10 PASS` line each and last line `cases=N pass=N control=FALSE-GREEN-REJECTED`, N at least 10; 1 any `FAIL` case or an accepted always-zero control; 2 missing prerequisite (tool absent, no git, TMPDIR unset or resolving inside the lane or the fleet root) | same default invocation; red arm is the base tool blob, which prints `cases=10 pass=3` and fails exactly G1 G3 G4 G5 G6 G7 G8 while G2 G9 G10 stay green (this is the C2 counter's REDARM leg) | cases G1 to G10 frozen in `census/round-31/records/preregistration.txt` C2; G8 is the contract's prose-alternation case and carries the letters-only blind spot | synthetic rounds under `$TMPDIR` only, removed in `finally`; never writes in a lane checkout | souji |
| r31-jj-object-clock | probe | `TMPDIR=<scratch> bash tests/fixtures/r31-jj-object-clock.sh` | 0 prints a `jj-version:` line, a `git-version:` line and 17 `RESULT arm=… step=… keep_refs=N target_keep=… reflog_hits=N object_present=yes-or-no` lines; 2 refused (TMPDIR unset, empty, not a directory, or resolving inside the souji lane or the fleet root) or interrupted | no self-test; the judging instruments are the C3 counter's legs L8 (record shape), L9 (two replays equal the record), L12 (jj and git argv logged through a shim) and L13 (remover subtraction, M1 reflog expire and M2 gc/prune) | `census/round-31/records/jj-object-clock-run.txt` (17 RESULT lines, jj 0.45.1, git 2.56.0, recorded at the C3 landing commit and re-run byte-identical at the tip) | jj-colocated scratch repositories under `$TMPDIR`, every jj call `-R`, every git call `-C`; never a lane | souji |
```

## Corrections applied to the wave-1 draft

1. **Level.** Q68 and Q69 now state the amended counters: C2's `shift` leg is the v3 random-probe oracle
   (A5), not the v1 static list; Q69 is the v3 `legs=13` target with v1 and v2 still required. The wave-1
   draft stopped at v1/v2 for C3 and at v1 for C2, so its check cells described targets that no longer
   certify.
2. **Q67 gained A2 and A4.** The wave-1 row had neither the count shape rule (A2) nor A4(a) run-only
   supersession of a command-bearing cell, A4(b) record-kind exclusions, A4(c) base-blob execution and A4(d)
   no shared occurrence.
3. **Q67 gained the honest-miss rule.** The wave-1 row asserted `unbound=0 mismatches=0` as the reading. The
   landed state is `unbound=1 mismatches=1`, which is honest: L29's record restates the count as
   `"matched_command_count": 18`. The row now says a disclosed miss is a valid outcome and that substitution
   is not, and it warns that the counter cannot tell the two apart (reproduced below).
4. **Q67's target wording.** The frozen target is unchanged (`unbound=0 mismatches=0`); only the reading is
   corrected, to `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` with rc 1, at both the landing
   commit `24f343c8ffc820c0f89b4252cbdc94ab9a673aab` and the tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`,
   under v1 and A2+A4 alike.
5. **Q68 gained the letters-only limit as text.** Wave-1 mentioned "extension-less prose alternations" as a
   tokenizer win without stating that the win costs a real missing letters-only path. A3 disclosed the cost;
   the row now carries it, and the witness pair `census/waves` / `census/waves/` was run against the real
   gate this round.
6. **Q68 gained the disposition rule** (one `open` or `resolved@<full40>` per carry bullet, full 40 that
   resolves, gate token only seven or more hex) and **the fence rule**, both of which the wave-1 draft left in Q69's
   or nowhere's scope. The carry-disposition rule belongs with the tool that reads carries; Q69 is now the
   measured-entry criterion only.
7. **Q69 gained L12 and L13.** Wave-1 had the shim idea without the remover subtraction; A1 landed L13 after
   wave-1 was written. The row now requires M1 and M2 mutants with the shape it actually checks (exit 0, same
   line count, differs, strictly fewer `object_present=no`).
8. **Q69's span rule made exact.** The counter collects backticked spans matching RESULT followed by a space
   and at least one further character, then requires each to equal a whole record line; a bare mention of the
   word RESULT in prose is therefore not a span and is not counted (the entry carries six such spans, not
   seven). The row states the form instead of "every backticked `RESULT ` span", which would have been false
   about the tool.
9. **Table headers and live paths.** Wave-1 used `applies-to / test / lesson`; the file uses
   `applies to / check / motivating evidence`. Wave-1's forward-path caveat is resolved for all three rows:
   `tests/fixtures/r31-landing-gate-precision.py`, `tests/fixtures/r31-jj-object-clock.sh`,
   `census/round-31/records/jj-object-clock-run.txt`, `corpus/knowledge/jj-dropped-keep-object-lifetime.md`
   and `corpus/QUALITY.md` are committed at `2c16d01`. `corpus/lessons/round-31.md` is not — see below.
10. **Block B narrowed to the three assigned rows.** Wave-1 drafted five, including `r31-c2-counter` and
    `r31-c3-counter` rows pinned to v1/v2 targets. Those two are stale in the same way as correction 1 and are
    not redrafted here (outside this seat's assignment); the integration owner must either update them to v3
    (C2 `shift=ok` with random probes, C3 `legs=13`) or drop them.

## Dependencies the integration must resolve

1. **`corpus/lessons/round-31.md` is absent at the tip.** `git cat-file -e
   2c16d018e40db7c23420a2c3bb546b52957bcc25:corpus/lessons/round-31.md` fails; no untracked lesson exists in
   the working tree either. All three motivating-evidence cells cite it as assigned. Under Q65 the commit that
   lands these rows must be at or after the lesson commit, so Block A lands with or after the lesson; if the
   lesson's headings differ from the r30 shape (`## Gate`, `## Findings`, `## Seat-reported failures`,
   `## Mistakes`, `## Receipts`, `## Residuals`, `## Wave`), the citations must name the real headings
   (`grep -n '^## ' corpus/lessons/round-31.md`).
2. **The wave-2 report citation** in Q67's evidence cell points at the captured copy
   `census/round-31/waves/w2/SwarmScribe35.md`. That path exists only after this round's wave-2 capture lands;
   before that, cite `.ufo/waves/round-31/w2/SwarmScribe35.md` or drop the parenthetical.
3. **Q67's green state does not exist at r31.** The block must not be read as saying C1 passed: the counter
   exits 1 with one honest miss, and the frozen target is missed by one item. The row says so.
4. **No tool version claim.** This seat installed, upgraded and removed nothing; no package transaction ran.
