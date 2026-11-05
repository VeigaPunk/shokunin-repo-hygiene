# Seat S67ReviewerC2 — round-67 wave w1 — C2 counter + population attack

Seat scope: attack the frozen C2 instrument pair
(`census/round-67/c2-counter.py` sha `045b47d1ebc1d5df229029fbfdaee12f8d1f6b819a9dc2ba81331b2b12c14916`,
`census/round-67/c2-statements.tsv` sha `8782a21dd9085cf8f0516cc474847cde8a449ef813ddcb68ccdef1bedb433b90`,
both verified byte-exact at the instruments commit `05eb2cee2794e42559c5ba15c3ebfdf7caecfee5` via
`git show | sha256sum`), the mutant recipes `census/round-67/c2-mutate.py`, the frozen controls
(`c2-do-nothing.txt`, `c2-do-nothing-r66.txt`), and the claim semantics in
`census/round-67/preregistration-attempt4.txt`. Read-only on the lane; all measurements ran in
scratch `/fast/scratch/hyaku/souji-r67/S67ReviewerC2/` on a `--shared` clone of the lane repo.

## Verification baseline (findings measured against a green base)

Every freeze-predicate target reproduced exactly in scratch before attacking:

| target | measured |
|---|---|
| frozen counter `--selftest` | `SELFTEST pass cases=17 fail=0`, `EXIT=0`, `STUB-ALWAYS-ZERO REJECTED` |
| frozen counter at pinned state `c13fbb4e` | `FINDING SCOPE-OVERREACH s5` + `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1`, markers `flag=1 inrun=1 env=1 unmerged=1 envcfg=1 envred=1 cdred=0` |
| r66 counter (`ac2157e6…`, r66 population `4576f101`) at pinned state | `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` (matches committed `census/round-67/controls/c2-do-nothing-r66.txt`) |
| do-nothing arm at `045e103` | `FINDING GOVERNED-STATEMENT-UNRESOLVED s5` + `rows=5 findings=1 verdict=FAIL`, `EXIT=1` — byte-equal to the committed control's output lines (`diff` clean after stripping the receipt header) |
| reverted-rule mutant (`c2-mutate.py --mutant reverted-rule`) `--selftest` | `SELFTEST-CASE m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `pass cases=17 fail=1`, `EXIT=1` |
| enum-weakened mutant at pinned state | `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` |

The frozen kill-power targets are genuine, not Iron-Curtain. Findings below attack beyond them.

---

## Findings

### HIGH-1 — Control-uniqueness defect: the claim's base state (36390879) produces the target shape EXACTLY as the pinned state does; the fixed control (045e103) leaves an unrecognized equal-arm

The prereg's kill text (`preregistration-attempt4.txt` lines 79–80) says the only red shape that should
come from a no-work world is `GOVERNED-STATEMENT-UNRESOLVED s5` at the r66 pre-r66-work state, i.e. the
do-nothing control is `--rev 045e103…`. But the claim block ALSO declares
`Base: 3639087917eaeb28719d7603110a6ec22782100e` (line 73), and a no-work arm measured at the BASE
state (also an allowed arm sentence shape) produces:

```
cd /fast/scratch/hyaku/souji-r67/S67ReviewerC2/lane
python3 -B census/round-67/c2-counter.py --root . --tsv census/round-67/c2-statements.tsv \
  --tsv-rev 05eb2cee2794e42559c5ba15c3ebfdf7caecfee5 --rev 3639087917eaeb28719d7603110a6ec22782100e
FINDING SCOPE-OVERREACH s5: stable wording: claim redirects_closed needs writer markers cdred; writer blob lacks them
MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=1 envred=1 cdred=0
SUMMARY rows=5 findings=1 verdict=FAIL rev=3639087917eaeb28719d7603110a6ec22782100e
EXIT=1
```

Byte-for-byte the target shape. Mechanism (grep-verified): `SKILL.md` and
`tools/souji-receipt-write.py` are **byte-identical between 36390879 and c13fbb4e**
(`git diff 3639087 c13fbb4e -- SKILL.md tools/souji-receipt-write.py` is empty; the writer sha is
`a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc` at both). The only tree delta
between base and pinned is 113 files added after the base (wave mirrors, lessons, QUALITY, SOURCES,
knowledge entry, records) — none on C2's read surface. `36390879` is `b238ab1d` + one commit, and
`b238ab1d` is downstream of `c13fbb4e` (`git merge-base --is-ancestor c13fbb4e 36390879` → rc 0).

Is this in fact a defect, or by design?

- The prereg's kill text says: "Kill: … the declared counter's selftest below 17/17, a reverted-rule
  mutant selftest that stays green, …" — the kill item list never includes "findings at the base
  state must differ from the pinned state". A work-free wave that measures C2 at the BASE revision
  (`--rev 36390879`, which the claim block names Base) gets `findings=1` with
  `FINDING SCOPE-OVERREACH s5` + `EXIT=1`, i.e. it passes the kill-text and the target text if the
  target's phrase "at the pinned state" is not read strictly as "--rev c13fbb4…".

Where the prereg is explicit, the target AS COMMAND indeed pins `--rev c13fbb4e1b…` exactly; a wave
careless enough to measure C2 at the base would fail the After-line variable-block check (C2's
machine-receipt contract binds the run's own rev line). So this finding is severity MEDIUM (not the
HIGH of a silent cheat path), but it remains a real hole the prereg never closes:

> **MEDIUM-1 (upgraded from the "is that a kill-rule defect?" item):** The prereg's do-nothing arm
> reads `045e103…` but the kill rule never excludes a red at 36390879 that has the same shape as the
> target. A wave (or future operator audit) could cite "C2 findings=1" at base as if the discrimination
> arm had fired; it has, but with the SAME `FINDING SCOPE-OVERREACH s5` ID, so shape-equality with the
> target arm is not a discriminator. The legitimate defense is that the frozen `Base:` field of the
> claim block still points to 36390879 and that the arm is one of the 113 post-base docs commits'
> place (higher levels of the round are what add the record). The kill rule does not say "must be 0
> findings at base"; the tool's own verdict text makes no state assertion beyond the pinned rev.
>
> Repro receipts in `stubs/`; the two states differ only in non-C2 files. The запуск at base is the
> exact `FINDING SCOPE-OVERREACH s5` + `MARKERS … cdred=0` + `EXIT=1` shape.
>
> Fix (r68 or operator): either (a) add to the kill text an explicit item "a red arm measured at the
> BASE revision that carries the same finding id/kind as the target is a control-uniqueness failure
> (the base arm is not a discriminator and must be labeled, not counted)"; or (b) change the frozen
> `Base:` of C2 to `c13fbb4e` (the actual state the counter reads), acknowledging that the base state
> is dead-equivalent for this instrument. Option (b) is the byte-faithful fix but it edits the frozen
> preregistration, which the freeze rule forbids; so the honest fix is (a) in the next lesson record.

### HIGH-2 — REDIRECT_ENUM's source label overstates the capture: `GIT_REPLACE_REF_BASE` is ABSENT from git(1)'s § ENVIRONMENT VARIABLES (0 hits in the S298 capture) and the counter's comment cites exactly the entry text that names its own absent name

`c2-counter.py` lines 110–120 comment: "REDIRECT_ENUM below freezes the class from the committed
S298 capture (git(1) § ENVIRONMENT VARIABLES); its fourth member, `GIT_COMMON_DIR`, is the route the
round-66 W2 probe measured open". At line 127–129:

```python
REDIRECT_ENUM = ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_REPLACE_REF_BASE", "GIT_COMMON_DIR")
```

Sweeps against the committed capture (`census/round-66/sources/git-environment.txt`, sha
`624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035` — the exact sha the r66 lesson's
spotcheck table row S298 binds):

| name | hits in capture | verdict |
|---|---|---|
| `GIT_OBJECT_DIRECTORY` | 2 (entry at line 1081) | PRESENT |
| `GIT_ALTERNATE_OBJECT_DIRECTORIES` | 1 (entry at line 1086) | PRESENT |
| `GIT_COMMON_DIR` (entry at line 1132) | 1 | PRESENT |
| `GIT_REPLACE_REF_BASE` | **0** | **ABSENT from both S298 (git(1)) and S299 (git-config(1))** |

The ABSSENCE is itself the lane's own recorded fact: `census/round-66/sources/absences.tsv` rows 20
and 21 say `GIT_REPLACE_REF_BASE … 0 0 ABSENT not defined in git(1); upstream it is only in
RelNotes/2.6.0.adoc:44 and in the source (refs.c:149 comment, environment.h
GIT_REPLACE_REF_BASE_ENVIRONMENT)`. The r66 SKILL section (line 870 of SKILL.md at c13fbb4e) also
includes `GIT_REPLACE_REF_BASE` in the r66 refusal list — the writer refuses a name the man page does
not document as an environment variable, so the refusal is defense-in-depth against a real C-level
variable, not against a documented git(1) route.

Precise defect: the C2 counter's comment and the module docstring (lines 13–16 and 110–120) say the
enumeration is "frozen from the committed S298 capture". Two of its four names are documented
there, one is documented there but with an entry the comment does not cite, and
`GIT_REPLACE_REF_BASE` is not there at all; its provenance is the r66 landed SKILL refusal list plus
the r66 absences/tsv analysis, both real but neither is "the S298 capture". A future reader auditing
REDIRECT_ENUM against its claimed source will find 3/4 hits and no recorded reason. This does not
change any measured predicate today: REDIRECT_ENUM is exactly the four names the r66 SKILL sentence
refuses-or-leaves-open, and the M5 overreach is measured by the marker set, not by the enum tuple
(the enum is **dead code**: it is assigned at line 127 and never read — `grep -c REDIRECT_ENUM`
counts 3 occurrences, all in the docstring/comment/assignment, and no evaluation path references
the tuple; the marker requirement `("envred", "cdred")` at line 128 of REQUIRED is what the counter
actually uses).

> **MEDIUM-2:** REDIRECT_ENUM is a dead declaration with a provenance-unsafe label. The M5 kill is
> real (the frozen REQUIRED/`redirects_closed` pair drives it), but the tuple's stated source is
> wrong for name #3. Fix in the r67 lesson record: either drop the dead tuple (a r68 counter change;
> a counter change is a claim change — out of scope here) or document provenance properly as
> "3 members from S298; GIT_REPLACE_REF_BASE from the r67-later absences.tsv analysis plus the r66
> landed refusal bytes (c13fbb4e:tools/souji-receipt-write.py:56,296)".

`MEDIUM-2 (subfinding):` the "no fifth name" sweep. Swept the full `§ ENVIRONMENT VARIABLES`
enumerated region of the committed capture (lines 1048–1646): **69 distinct GIT_ variable names** in
the region (count `grep -E '^GIT_[A-Z_]+$' | sort -u`). Individually read the only other
object-affecting booleans — `GIT_NO_REPLACE_OBJECTS` ("ignore replacement refs"), `GIT_NO_LAZY_FETCH`
("not to lazily fetch missing objects"), `GIT_COMMIT_GRAPH_PARANOIA`, `GIT_REF_PARANOIA`,
`GIT_ALLOW_PROTOCOL`, `GIT_DISCOVERY_ACROSS_FILESYSTEM`, and the Windows-only `GIT_REDIRECT_STD[IN |
OUT | ERR]` — none causes git to *resolve objects in a redirected location*, i.e. none widens the
"object-resolving redirect route" class. Command that shows the sweep:

```
awk 'NR>=1048 && NR<=1646' census/round-66/sources/git-environment.txt | grep -E '^GIT_[A-Z_]+$' | sort -u | wc -l   # 69
comm -23 <(awk 'NR>=1048 && NR<=1646' ... | grep -E '^GIT_[A-Z_]+$' | sort -u) \
         <(printf 'GIT_ALTERNATE_OBJECT_DIRECTORIES\nGIT_COMMON_DIR\nGIT_OBJECT_DIRECTORY\nGIT_REPLACE_REF_BASE\n' | sort)
```

An absent-claim carries its sweep: **no fifth object-resolution-redirect name is documented in the
committed capture's env region** (the counter's own comment about GIT_COMMON_DIR's entry text
"If this variable is set to a path" matches capture line 1133). The M5 enumeration claim, as
*enumeration*, is sound; only the "frozen from S298" label for name #3 is wrong.

### MEDIUM-3 — The M4 case is non-vacuous for the specific `returncode`-line shape but a reverted rule can pass with emission-adjacent shapes that are NOT `refuse(` or `return <literal>` lines; the case's discrimination is inherited from the `return` substring, not from refusals

The ONLY mechanism that makes the `m10-s5-assertion-line-not-live` case discriminate is the reverted
rule's `"return" in raw` matching the substring `return` inside `r.returncode`. This was then (r66)
and remains now a token-collision, and the case's shape choice does not get around the underlying
class: the reverted rule reads BOTH needles live on any line containing the substring `return` under
any other construct that also mentions the substring. The frozen stub uses two
`if r.returncode != 2 or "<needle>" not in r.stderr:` lines. Two shapes I built in scratch produce
the same flip and are NOT the frozen fixture shape:

- `shape-A-returncode-conjunction.py` — `if r.returncode != 2 and "RECEIPT-ENV-CONFIG-SET" and "RECEIPT-ENV-REDIRECT-SET" and False:` → repaired去找 findings=1, reverted findings=0 (flip).
- `shape-B-assert-all-on-one-line.py` — `assert "RECEIPT-ENV-CONFIG-SET" in r.stderr and "RECEIPT-ENV-REDIRECT-SET" in r.stderr and r.returncode == 2` → same flip.

These confirm the frozen case is not a one-shape-only guard and that a mutant-shaped writer can still
use several sentence forms — i.e., the repair's discrimination is HOSTED by the substring "return",
not by "a refusal line". Severity: the case is non-vacuous and any reverted-rule-counter mutant
still fails `--selftest` as long as the frozen stub's exact bytes are used; the point for the record
is that the M4 fix covers the *reverted-rule recipe*, not the *rule class*. A different revert of the
repair — for example adding `"returncode"` into RETURN_LITERAL or replacing
`RETURN_LITERAL.search(raw)` with a token that matches `r.returncode` — would not be caught by the
case (it is a different mutant recipe; the frozen "reverted-rule" recipe is the only one declared).

> **MEDIUM-3:** The M4 repair kills the specific reverted-rule recipe; a *class* of reverted rules
> that also match `r.returncode` un-patches the guard without being caught by the recipe. The frozen
> mutant-recipe commit (c2-mutate.py) names exactly one revert shape, so killing it is enough for the
> frozen prereg, but the guard is rule-shape-specific, not rule-class-specific, and the docstring's
> "the reverted round-65 rule … reads them live and produces findings=0" phrasing generalizes one
> revert to the whole revert family. That generalization is a named-limit-quality remark, not a
> predicate failure today.

A stub the case CANNOT see structurally (all tested by direct import of the frozen counter bytes in
scratch): placing both needles in

- an all-comments block (repaired findings=1, correct — no line is live),
- a top-level assignment `NAME = "RECEIPT-ENV-CONFIG-SET … "` (both rules read this DEAD: findings=1
  under both — the sentinel is a needle on a line with `refuse(`/`return`/`returncode`, and plain
  assignment lines with a needle literal are dead in both. This stub is the ENEMY of the M4 case:
  a reverted-rule-counter passing with a dropped refusal in an assignment literal would NOT be caught
  here even though it is dropped, meaning the case's kill only binds the specific recipe, not the
  general "dead-token mutant" class — that class is killed by the four other dead-token cases, not
  by this one).
- a `print(...)`-only emitter (repaired findings=1, reverted also findings=1: both rules refuse the
  line — a print is not a refusal-line emission path, so the case does not discriminate print-only
  refusals; both counters write findings=1, i.e. a writer stub that emits with print() only
  would score findings under the repaired rule while a real writer that emits only with print()
  exists as a limit not covered by either counter — a writer-side limit, not a C2 claim defect).

An exhaustive summary of the stub-shape sweep is in `stubs/PROBE.txt`; the stubs
(`case-frozen-assertion-lines.py`, `shape-A-returncode-conjunction.py`,
`shape-B-assert-all-on-one-line.py`, `reverted-rule-inline.py` — the mutant counter bytes used for
comparison) are delivered inside `stubs/`.

### MEDIUM-4 — Scope check binds markers, not reachability: confirmed, and the shape `cdred live-lexical but refusal unreachable` is trivially constructible; the two instruments jointly close only the specific refusal-line class, and the class gap remains

Counter docstring named-limit sentence (lines 76–80 approx.) already owns this. Constructible
scratch stub (delivered as part of `stubs/…` — not committed here because the point is already a
frozen named limit):

```
def _dead_route(p):
    if False:
        refuse("RECEIPT-ENV-COMMONDIR-MISMATCH: " + p)
```

The frozen `live_markers()` rule (`refuse(` on a non-comment line) reads the needle live even though
the written refusal never executes. The C1 behavioral matrix closes the equivalent WRITER-BEHAVIOR
gap only for the SPECIFIC behavior the matrix exercises — W1/W2 use the writer's REAL refusal
machinery (the measured writer commits, not a stub), so a fake dead-branch cdred in a candidate
byte would put the needle in an unreachable refuse site but the writer's W1/W2 refusals would run
on the OTHER route refusals; a candidate that only adds a dead-branch `refuse("RECEIPT-ENV-…COMMONDIR-MISMATCH…")`
while wiring its real GIT_COMMON_DIR check to a pass-through would pass C2 and FAIL C1 (W1/W2 ask the
real env check to refuse). Conversely, a candidate that adds the live refusal and reuses the correct
mechanism but puts ONLY a dead-branch needle for a different marker would pass W1/W2 and fail C2 —
so the two instruments jointly cover the class (the writer's real check + the needle-bound lexical
check) only under their separate scopes; each alone leaves its own gap and the pair does not overlap.
Joint coverage verdict: **the pair covers the class as long as the same bytes are measured by both
counters (which C1's `--tool tools/souji-receipt-write.py` and C2's `--rev` bind as the same
candidate). No additional gap remains beyond the frozen named limits if both arms run on the same
bytes; a gap remains if C2's steward rewrites the M5 stance without re-running C1 on the final
landing.**

### LOW-1 — The prereg's C2 "Before arm" citation of the r66 counter commit id is a BLOB sha, not the counter's digest commit — the instrument line binds the byte digest; no defect, just a naming mismatch for future auditors

The frozen text names the r66 counter as "the round-66 frozen counter (census/round-66/c2-counter.py
sha256=ac2157e606…)". `git cat-file -t ac2157e6…` → `fatal: Not a valid object name` in the lane
clone, because the sha the prereg quotes is the counter file's SHA-256 DIGEST, verified equal with
`sha256sum census/round-66/c2-counter.py` → `ac2157e6060e95e0d21e760b0b1a0edf8efeaed8181e121a2f86a623b9e25c67`.
Also confirmed by `census/round-66/records/c2-selftest.txt`-style committed receipt: the token carries
`instrument_sha256=ac2157e6…25c67` (its own sha). Read it as a digest; the counter's *commit* path
is `4576f101: census/round-66/c2-counter.py`. No finding, just a causal note so auditors do not misread.
Included because the seat target asked for an explicit absent-claim carry-its-sweep discipline; this
item's sweep found a labeling convention, not a defect.

### LOW-2 — The other two long-documented no-work discriminator shapes (base wording + env_closed path) are silent on the equal-tree base-vs-pinned; both have been excluded above; a residual shape exists only for the specific fingerprint byte-diff between the 113 post-base doc commits (not covered by C2 and outside its claim)

Closing note for the HIGH-1/MEDIUM-1 investigation: with the base wording pattern in place
(`S5_PAT` in both slots) the stable-wording mechanism automatically routes the s5 row to
`redirects_closed`, which is why the two byte-identical states produce byte-identical counter output.
Every OTHER population mechanism (GOVERNED-STATEMENT-UNRESOLVED at `045e103`) reads a DIFFERENT
false-tree state (`SKILL.md` there does not carry S5_PAT yet, verified `grep -c S5_PAT`-style by the
r67 counter showing envcfg=0 / envred=0 markers for the r66-writer at `045e103`), so the do-nothing
control is not merely a different finding ID but a fundamentally different tree, fully red on that
other shape. Every claim of the "no-work cannot meet the target shape" kind holds for 045e103; only
36390879, the base state, is an unrecognized second red-with-target-shape arm. Residual risk: none
that a no-work wave can claim C2 as a pass, because wave reporting binds candidate run receipts to
the pinned rev string (machine-receipted at records time; the C2 prereg receipt structure requires
it), but the red-at-base ambiguity is one the next round should close explicitly.

---

## Anchors (s4 note correction M7, s5 note)

**s4 is present at 36390879 and at c13fbb4e (grep count 1 at both):**

```
$ git grep -c 'an unmerged index entry is refused with `RECEIPT-INDEX-UNMERGED`' 36390879 -- SKILL.md
3639087917eaeb28719d7603110a6ec22782100e:SKILL.md:1
$ git grep -c 'an unmerged index entry is refused with `RECEIPT-INDEX-UNMERGED`' c13fbb4e -- SKILL.md
c13fbb4e1b563a78278ddc14316c20252e9a6d8d:SKILL.md:1
```

Full sentence at `SKILL.md:839` at both revisions (the r62-writer paragraph ending
"…and an unmerged index entry is refused with `RECEIPT-INDEX-UNMERGED`").

**The r66 population's note is factually wrong.**(`4576f101…:census/round-66/c2-statements.tsv`,
line 5, note cell): reads
"stable wording covering the r62 named-limit unmerged clause; **absent from SKILL.md at base
(GOVERNED-STATEMENT-UNRESOLVED feeds the do-nothing red), added with the r65 landing**".
Two clauses falsified by the grep above: (a) "absent from SKILL.md at base" is false — count 1 at
36390879; (b) "added with the r65 landing" is unsupported — the sentence lives in the base-commit
SKILL.md (Round-62 section paragraph at line 839) and was not added by r65. The r67 population's own
note (`05eb2cee…:census/round-67/c2-statements.tsv`, s4 note cell) states the correction
explicitly ("r67 correction of the r66 population's note (round-66 M7): the r66 note claimed this
sentence is absent from base SKILL.md, but the base SKILL.md carries it (grep count 1 at
36390879…, SKILL.md Round-62 section)"). **The correction is accurate**: the cell-level claims in the
frozen r67 population's s4 note match the lane bytes, and the operational consequence the r66 note
foreshadowed (the do-nothing red at that arm arising from an s4 UNRESOLVED finding) does not exist —
the frozen r67 do-nothing control is red via s5 GOVERNED-STATEMENT-UNRESOLVED only, and s4 resolves
on both slots of the pinned state, exactly as the r67 population's corrected note claims.

**s5 note (the "Note (not machine-checked)" cell):** the sentence text stays the frozen r66 bytes and
the scope fix "lives in the claim token, not a rewording" — verified against the population bytes
(base_pattern == after_pattern at s5) and against the counter's evaluate() stable-wording mechanism.

---

## C1 corroboration measured by this seat (bounds: read-only, run against the candidate writer at the PINNED commit c13fbb4e in a scratch fixture, not the future candidate)

The candidate writer bytes at `c13fbb4e` (the J-r66 landing) reproduce the r66 behavior:
equal-value `GIT_COMMON_DIR` accepted (`RECORD … rc=0`), mismatching and empty values
mistakenly-passthrough — the r66-named-limit known gap. I did NOT run the C1 counter; the
wave's executor seat will. This check was a C2-adjacent Corroboration that the *pinned* bytes still
carry the cdred-dead marker set the C2 counter reads (`cdred=0`) so the C2 claim's measurement of
`cdred=0` was not a counter artifact.

## Tooling authorization record

No tools installed or upgraded this seat (work used existing `python3` 3.x, `git` 2.5x, `sha256sum`,
`diff`, `grep`). No pacman operation. No network probes. No git mutation anywhere, including fixures;
fixture creation used a plain `git init` in a `mktemp -d -p /fast/scratch/hyaku/souji-r67/S67ReviewerC2/`
directory with `-C "$D"` on every later call, and fixture commits used `-c user.name=… -c user.email=…`
throwaway identities inside the fixture only (`rev-parse --show-toplevel` equality verified before
the first commit).

## Scratch cleanup

Per the wave contract: `/fast/scratch/hyaku/souji-r67/S67ReviewerC2/` contents were copied into
`.ufo/waves/round-67/w1/S67ReviewerC2/stubs/` (probe stubs + PROBE.txt) before cleanup; the scratch
root itself is removed at seat completion (`trap 'rm -rf -- "$S"' EXIT` was set; a final
`rm -rf -- /fast/scratch/hyaku/souji-r67/S67ReviewerC2` runs after the last evidence copy).
The `--shared` lane clone and the W2 fixture under it are discarded — no unique bytes were produced
inside them (the fixture held no unique data: every byte there derives from the c13fbb4e commit via
`git show`, reproducible from the lane at any time).
