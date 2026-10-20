# DraftLessonGate — round 16 w1 report

Seat: SoujiR16.DraftLessonGate (scribe, leaf). Judged on: calibration.
Scope: draft the `## Gate` skeleton for `corpus/lessons/round-16.md`. The file itself was NOT written (contract: write only this report). Nothing was measured; every admit/reject below is a conditional rule, not a verdict.

Verified state (read-only):
- `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` resolves and equals `HEAD`.
- `corpus/SOURCES.md` sha256 = `5185720f8dfdf1a9a5e69143e61d1dfe99c3116adc058c7c6768a1217999662d`, the same digest the round-15 closure recorded. Registry is S001–S042, 42 rows.
- `corpus/lessons/round-16.md` does not exist yet.

## Findings for the lead (calibration)

1. **C1 red must be the routed reason, not a parse failure.** The claim cites `r15-baseline b410186 parse fails` as the red arm. A parse error is tool identity, not a behavioral disagreement. The round-15 Gate states "red must come from actual behavioral disagreement, never tool identity," and R15-M1 requires red for the value-blind benign-config reason. The valid red arm is `cc21683` (r14-harm), where the benign `core.hooksPath=/dev/null` refusal occurs. The `b410186` row may be reported only as a conformance defect, never as the C1 red.
2. **C1 is missing a named mixed-fleet control.** The round-15 Gate admits C1 "only with paired benign-config and mixed-fleet preservation plus namespace gains retained." The round-16 measurement list names 20/20 fixture, 12/12 namespace and 38/38 selftest, but no mixed-fleet case ID. Without one, C1 cannot be admitted on the lesson's own rule.
3. **C1 green baseline must be pre-harm.** The 20-ID fixture is preservation evidence only if `a31642d` (pre-harm) is green on the same 20 IDs. The claim states `changed 20/20` but does not state the `a31642d` count. Record both.
4. **C2 "red on b410186, green at round end" is not a calibration proof on its own.** A checker that fails everything also goes red on `b410186`. C2 needs green on controls where the defects are absent (`a31642d`, and the clean repaired state), or the gate's red is unfalsifiable. Round-15 Gate requires "actual self-invocation negative controls."
5. **C2 frozen-pin check is revision-relative.** The R4 pin `b5187351…` matches no committed revision, so the pin-defect check fires at `cc21683` too. Round-end green is meaningful only if the pin is re-recorded with its measured revision (`cbf688ab`) and the gate reads that pin as an independent input. A pin set to the digest of the file under test is self-referential and does not count.
6. **C2 "seat-reported known failure carried verbatim" (defect 3)** should be checked by a text predicate against the seat report. Require the predicate to be tested on `.ufo/waves/round-15/w1/ConfigRepair.md:7-13` text, not only on a constructed string (CriticFixtureOverfit risk).
7. **S043 quote must be opened, not recalled.** The bash `set -n` quote is a slot below. It has not been fetched or verified by this seat. Do not fill it from memory. `set -n` proves a script parses, not that it behaves; scope the row as parse-only, so it cannot be cited as behavioral evidence (the same over-reach R15 criticized).
8. **Census regression watch.** The validate command emits W04 warnings for S035, S036 and S038. A new row must not add a W04 duplicate. A new `gnu.org/software/bash` URL does not duplicate any existing URL, so a new W04 would signal an error in the new row.

## `## Gate` skeleton (for `corpus/lessons/round-16.md`; to be filled by the lead)

```markdown
## Gate

Admission requires measured evidence, not the existence of these criteria.

### Decisions

| claim | decision | admit only if (all) | reject if (any) | measured evidence |
|---|---|---|---|---|
| C1 operability | PENDING: admit / reject | (a) `bash -n`, `shellcheck -S warning` clean at `cbf688ab`; (b) red = `cc21683` on the benign `core.hooksPath=/dev/null` case (routed reason, not parse); (c) green = `a31642d` and `cbf688ab` on the same 20 IDs; (d) named mixed-fleet case green at `cbf688ab`; (e) r14 namespace 12/12 and selftest 38/38 retained; (f) protected-namespace reach still exit 2 | any routed-reason red not observed; any pre-harm ID red at HEAD; mixed-fleet case missing or red; namespace or selftest regression; red sourced from parse error | `<run-matrix.py output path>`, `<digest>` |
| C2 calibration | PENDING: admit / reject | (a) gate red on `b410186` for R1–R3 defects; (b) gate green on `a31642d` and on the repaired HEAD, with no false positive; (c) frozen pin re-recorded with measured revision `cbf688ab` and read as an independent input; (d) seat-report predicate tested on `ConfigRepair.md:7-13` verbatim text; (e) `bash -n` clean on the gate and fixtures | gate green on a known-bad control; pin is self-referential; any defect in R1–R3 unobserved; gate parse fails | `<gate output path>`, `<digest>` |

Unrun checks have not passed. Measured `changed` counts are the author's claim until L1 reruns them.

### Opened sources and registry decisions

- **S043**, `<bash manual URL, to be opened>`, opened `<YYYY-MM-DD>` by L1 at revision `<tag or version as served>`. Quote (≤25 words, located line): `“<verbatim quote from opened page>”` (line `<n>`). Scope: `set -n` checks syntax only; it does not establish runtime behavior. Grounds C2 defect 1 (non-parsing registry script).
- No other row opened unless L1 opens it and records it here.

Registry: new rows absent→mined, tier A within scope, used-by this lesson. S001–S042 unchanged, including immutable correction rows and their status/recheck/used-by cells.

### Process and conformance (filled by lead)

- Seat no-probe rule (R5): `<per-seat command audit, verbatim>`.
- Cross-domain evidence line (R6): `<line>`.
- Carried seat failures verbatim (R3): `ConfigRepair.md:7-13` quoted in full.
- `rejected` row for git-status(1) (R7): `<row or reason not added>`.
```

## Change-log format (old→new), for every registry row touched

One line per touched row; immutable cells keep their original text in the `old` column.

```text
S0xx | field: status | old: <value> | new: <value> | reason: <one sentence> | evidence: <lesson path>:<line>
S0xx | field: recheck | old: <value> | new: <value> | reason: <one sentence> | evidence: <lesson path>:<line>
S0xx | field: used-by | old: <value> | new: <value> | reason: <one sentence> | evidence: <lesson path>:<line>
S043 | field: status | old: (absent) | new: mined | reason: new row, opened this round | evidence: corpus/lessons/round-16.md Gate
```

Row-level changes must be stated, not inferred. A row whose cells do not change is not listed.

## Census before/after command block

Run by L1 (not by this seat). Start: before any edit to `corpus/SOURCES.md`. End: after all edits. Both runs must exit 0.

```bash
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
# expected before (round-15 end): 42 rows, A/B/C 38/3/1, mined/queued/rejected 25/15/2, digest 5185720f…
# expected stdout before:
#   souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
#   souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
#   souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
#   souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
# after: add S043 (and any further new rows); expect 43+ rows and the same three W04 lines unless a new row duplicates a URL.
```

Note: the `scripts/sources-census.sh` path is a fleet script. This seat did not run it, per the probe rule.

## Commands

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify cbf688ab2ab28e38103e5a9417ca525b5f2ed423^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify HEAD
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%H %s' -3 -- corpus/SOURCES.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%H %s' -3 -- corpus/lessons/round-15.md
```

Read-only file reads (not shell): `corpus/lessons/round-15-verifier-spotcheck.md`, `corpus/lessons/round-15.md`, `corpus/SOURCES.md`, `.ufo/waves/round-15/w1/ConfigRepair.md`, `corpus/lessons` (directory), `skill://godspeed`.

Tool installs/updates: none.

STATUS: skeleton only. No C1 or C2 decision is made; the lead must run the measurements and open S043 before the `## Gate` is final. Census not run by this seat.
