# SwarmScribe22 — r31 w1 draft: QUALITY Q67–Q69 and matching gate-registry rows

## Status

STATUS: PASS — the three criteria are drafted in the exact layout of Q63–Q66 (5 cells, no cell carries a
literal pipe) with runnable checks, the five matching `## Gate registry` rows are drafted in the existing
8-column shape, and every cited path was checked for existence at lane HEAD; the four forward dependencies
and the one gate-versus-preregistration looseness are disclosed rather than silently assumed.

## Evidence

Frozen contract read first: `census/round-31/records/preregistration.txt` (prereg
`1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, controls `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`). Lane
state at read time:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
1b811368461785040e955f41f9c97e62f61fd67c
$ git -C ... log --oneline -4
1b81136 round-31: C1 base output and M1 red-before receipt
ed17ff6 round-31: controls (do-nothing + junk) and stricter amendment A0 (C3 v2 reality leg)
1d45496 round-31: preregistration, frozen counters C1-C3, C1 enumeration, start census
9f17a1e round-30 verifier spot-check (integrator, hyaku): non-author admit/reject
```

Q67 check command exists and its base arm is receipted: `tools/souji-capability-cells.py` exposes
`--root --rev --base --list-rev --scratch --timeout --only` (argparse lines 129–135), exit 0 iff
`mismatches=0`. `census/round-31/records/c1-before.txt:43`:

```
SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
```

Q68 and Q69 arms exist as frozen instruments with their red arms already recorded. `census/round-31/records/controls.tsv`
(rows cited by Q67/Q68's test cells):

```
C2-do-nothing(base)	c2	SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same rev=1d45496a…
C2-junk(stub gate + fake fixture)	c2	SUMMARY fp=0 real=0 cne=0 r26=495 fixture=ok redarm=fail regress=differs rev=4320f030…
C1-junk1(record in waves/)	c1	SUMMARY items=1 bound_run=0 bound_record=0 unbound=0 mismatches=1 partial=1 rev=42c0018f…
C1-junk2(foreign script)	c1	… mismatches=1 … ; C1-junk3(new record) … ; C1-junk4(other integers) … ; C1-junk5(in-place edit) …
C3-junk(sourceless entry + typed record + cat fixture)	c3	… fail=4 … ; c3v2 … fail=5 …
```

(indented rows abbreviated only where the pattern repeats; the file holds each row in full).

Q69's red arm re-tallied by this seat from the committed receipt, per-round block:

```
$ python3 - (count LG-* lines per "## round N:" block in census/round-31/records/m1-red-before.txt)
round 26 UNCARRIED 18 DANGLING 0 total 18
round 27 UNCARRIED 29 DANGLING 0 total 29
round 28 UNCARRIED 19 DANGLING 2 total 21
```

Layout conformance, measured on the committed rows and on the draft: every `| Q6x |` row at
`corpus/QUALITY.md:158-161` splits into 5 cells, and the draft's three rows split into 5 cells; every
registry row including the draft's five splits into 8 cells (`SKILL.md:179-232` header
`name, kind, entry command, verdict map, self-test command, pinned-value path, write scope, owner`).
Existence probe for every path the draft cites — present: `tools/souji-capability-cells.py`,
`tools/souji-landing-gate.py`, `census/round-31/c1-cells.tsv`, `census/round-31/c2-counter.py`,
`census/round-31/c3-counter.py`, `census/round-31/c3-counter-v2.py`, `census/round-31/records/c1-before.txt`,
`census/round-31/records/controls.tsv`, `census/round-31/records/m1-red-before.txt`,
`census/round-31/records/amendments.txt`, `census/round-31/records/preregistration.txt`,
`corpus/lessons/round-26.md`, `-27.md`, `-28.md`, `corpus/QUALITY.md`, `SKILL.md`; absent at `1b81136`:
`tests/fixtures/r31-landing-gate-precision.py`, `tests/fixtures/r31-jj-object-clock.sh`,
`census/round-31/records/jj-object-clock-run.txt`, `corpus/knowledge/jj-dropped-keep-object-lifetime.md`,
`corpus/lessons/round-31.md` (glob `tests/fixtures/r31-*` returned nothing; the rest probed per path).

No scratch directory was created and none removed: no command in this seat needed a clone, fixture run or
download, and no check above executes a counter. No file outside
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/` was written; no git or jj mutation ran.

## Findings

1. **The gate reads only the first carry section, which is why Q68 must say "every section".** Source claim:
   `tools/souji-landing-gate.py:391` — `failures_section_lines` returns lines "Raw lines under
   `## Seat-reported failures` until the next heading." — so an append-only second section (the exact M1 fix
   shape, and the shape `corpus/lessons/round-29.md:90` already uses) is invisible. Quote is verbatim from the
   docstring opened this run; no release of the finding beyond what the source states.

2. **The gate's carry token is looser than the frozen disposition wording.** `tools/souji-landing-gate.py:111`
   accepts `resolved@` followed by 7 or more hex characters, while the preregistration requires a full 40:
   `census/round-31/records/preregistration.txt:22` — "with a disposition per entry (`open` or
   `resolved@<full40>`)". Q69 therefore carries its own full-40 check; the gate alone would pass a short
   token. Recorded as a disclosed limit, not an amendment (amendment authority is the L1's).

3. **Q67's "never a file grep happened to match" clause is already instrumented by five committed controls.**
   `census/round-31/records/controls.tsv` rows `C1-junk1`–`C1-junk5` reject, one each, a record placed under
   `waves/`, a foreign script, a record rewritten in the current round, a record carrying other integers and
   an in-place cell edit — the five shapes the clause names. The counter's own text fixes the record rule:
   `tools/souji-capability-cells.py:29` — "it is the same blob at --base and REV".

4. **A `record:` binding dates a literal, it does not re-measure it.** The frozen target accepts
   `record:` bindings whose integer multiset equals the base literal's, so a cell bound only by `record:` is
   the row's own round measurement restated. Q67 states this explicitly so such a cell is never cited as a
   current re-run; only `run:` bindings re-execute a command.

5. **Four of Q68/Q69's test cells and three registry rows cite paths absent at `1b81136`** (absent-path list
   in Evidence): `tests/fixtures/r31-landing-gate-precision.py`, the C3 fixture/run/entry, and
   `corpus/lessons/round-31.md`. Their wave drafts already exist in this directory as
   `deliver-r31-landing-gate-precision.py`, `deliver-r31-jj-object-clock.sh`,
   `deliver-jj-object-clock-run.txt` and `deliver-entry-jj-dropped-keep-object-lifetime.md` (directory listing
   opened this run), so only their integration at the final paths is missing. Under Q65 a landed row may cite only committed paths, so Block A and Block B
   must land at or after the C2, C3 and lesson commits, or the affected cells must be trimmed to committed
   paths at that commit. The L1 decides; this seat does not.

6. **Q68's union clause is what makes the C2 target measurable, and the dedupe half is not proven by the
   target alone.** `r26=495` is 466 force-added reports plus 29 capture-only reports
   (`census/round-31/c2-counter.py` docstring), so 495 shows the union but not the identical-relative-path
   dedupe; that half rests on fixture case G2, which the REDARM requires to pass on the base tool too. Q68
   names the fixture as the instrument for it rather than the scalar.

7. **Interaction with rounds 15, 19, 23, 24, 25 is a consequence, not a scope expansion.**
   `census/round-31/records/preregistration.txt:22` routes their mid-file carry sections as residual "unless
   C2 lands first". C2 is a claim that lands, after which the multi-section reading exposes those rounds'
   uncarried lines to the same gate; Q69 states that the round then carries them, instead of pre-declaring
   those rounds clean.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-quality-q67-q69.md` — Block A (three `## Round 31 criteria` rows) and
  Block B (five `## Gate registry` rows: `souji-capability-cells`, `r31-c2-counter`,
  `r31-c3-counter (A0 v2 stricter)`, `r31-landing-gate-precision`, `souji-landing-gate v2`), plus the
  dependency/limit notes the integrator must read before appending.
