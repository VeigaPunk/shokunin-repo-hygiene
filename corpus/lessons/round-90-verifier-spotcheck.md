author: hyaku closure (non-author integrator, @m_zfl)

# Round 90 verifier spot-check — souji (non-author, hyaku closure)

Lane: `souji-shokunin`. Lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2` (the r89 verifier spot-check
commit); lane HEAD after the round `93c7e6dc07f71cfe9c81d5db40c91a217c535ac0`. `scripts/hyaku/jj-lane.sh state`
reads `branch=master local=93c7e6dc07f71cfe9c81d5db40c91a217c535ac0 remote=93c7e6dc07f71cfe9c81d5db40c91a217c535ac0
ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` is empty and
`git ls-remote origin refs/heads/master` prints the same tip. Report `.ufo/reports/round-90/souji.md` is committed in
the fleet repo by the lane identity (`git log --format='%an %H' -- .ufo/reports/round-90/souji.md` -> `souji-shokunin
36f53d92745b5793a66882edf3a46f9753e614d4`; author 12:13:20 -0300, committer 12:18:10 -0300), on `origin/master`.

Dispatch/complete digest copied from this round's closure prompt (mutable `.ufo/watchdog.log`; the launch and
complete lines are present at lines 3368 and 3377):

`2026-11-08T11:31:05-03:00 launch souji round=90 pgid=2886868 driver=hyaku-inline attempt=1`
`2026-11-08T12:19:22-03:00 complete souji round=90; hyaku-inline attempt=1`

## 1. Step-1 conformance

- **Report identity and path: PASS.** The fleet commit is authored and committed by
  `souji-shokunin <souji@shokunin.local>`; no later sweep. It is not a marker: it names committed instruments,
  receipts, a population, a tool repair, sources and a checkable lane tip.
- **`SHONEN` heading: PASS.** `grep -c '^## SHONEN'` -> 1; four `[~]` lines, each with a resolvable pointer
  (`grep -c '^- \[~\]'` -> 4). `SHONEN.md` is unchanged in the range and carries no `[x]`.
- **Cited lane commits: PASS.** `git merge-base --is-ancestor <h> master` exits 0 for every cited hash:
  `1952c1c7`, `e2a11c73`, `4cb3a06f`, `fd25bfc5`, `8eba0131`, `a711c357`, `47bd575b`, `93c7e6dc`; the base
  `bd760432` and `git log --oneline bd760432..93c7e6dc` list the same eight commits.
- **Lane state: PASS.** `ahead=0`, tracked/untracked 0, clean tree; remote equals local.
- **Report lands last: PASS.** The lane tip's commit time is 12:17:24 -0300 and the report commit's is
  12:18:10 -0300; the report cites the pushed tip `93c7e6dc`. The report's author date (12:13:20) predates the
  A0.7 commit it describes, but the committing event is later, so the filed bytes could and do cite the tip.
- **Prompt contract: PASS.** `.ufo/prompts/souji-round-90.md` starts with a byte-identical rendering of
  `templates/round-prompt.md` (8,566 bytes / 140 lines; substitutions = lane `souji`, round `90`, fleet root,
  lane repo, and the `souji` axes string from `shokunin.conf:76`), followed by hyaku addendum section 6. It
  carries the round-level items (mission/axes, L2 floor, commit-then-push, push scope, L0) and the five
  child-lane items (report path, commit-before-report, `SHONEN` heading, hash citation, lane write scope).
- **Round shape: PASS with one definitional defect.** One v1 wave, 12 seats (3 executor, 2 reviewer, critic,
  mutation-tester, sentinel, connector, scout, scribe, labrat duty on a revenger-role seat). The pushed tree
  carries 12 seat reports and 134 wave files. **Defect (minor):** the report's "attack share 7/12 = 58 %"
  disagrees with the lane's own preregistration ("6/12 = 50 %", which adds sentinel to the addendum's list) and
  with the addendum's four-role list (2 reviewer + critic + mutation-tester + labrat = 5/12 = 42 %); 7/12 is
  the prefile gate's broader `ATTACK_ROLES` set (which also counts connector and revenger). Every count is
  >= 25 %, so no floor is breached; the report should cite one definition.
- **Wave-evidence durability: PASS.** The r89 defect is fixed: `git ls-tree -r master -- .ufo/waves/round-90 |
  wc -l` -> 134 and every `claim-falsification.tsv` artifact path resolves in the pushed tree (18/18).
- **Report accuracy: DEFECT (minor).** The report says `census/round-90/claims.json` is tied to the LOG entry;
  no such path exists — the frozen claims are `.ufo/waves/round-90/claims.json`. The LOG entry itself is present
  (`## Round 90` at `LOG.md:3430`) and covers Claims / Measured / Narrowed / Sources / Wave.
- **Settlement record: NOTE (minor).** The driver's final `w1-results.json` (committed at `47bd575b`) has all 12
  `results[]` entries with `output: null` and the note "orchestrator kernel restarted mid-wave; seat output was
  delivered to the orchestrator session but not retained — read the seat report file in the wave dir". "All 12
  seats settled" is true at the report-file level (12 committed reports), which the report's A0.7 disclosure
  partly covers; it does not say the driver retained no seat output. No seat output is invented: the reports
  under `.ufo/waves/round-90/w1/` are the evidence and they resolve.

## 2. Pre-file falsification ledger (addendum section 8, Amendment 59)

```
python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 90
PREFILE-FALSIFICATION: pass claims=2 rows=18 attack_seats=7 findings=0
EXIT=0
```

Both `C1`/`C2` from the frozen `claims.json` are covered; all seven attack seats are named (S90Connector,
S90Critic, S90ExecC1, S90ExecC2, S90ExecC3, S90Labrat, S90MutCounter, S90Reviewer, S90Reviewer2,
S90ScoutSources, S90Scribe, S90Sentinel); every one of the 18 artifact paths resolves in the pushed tree. Six
rows are `falsifies-wording`, every one names a narrowing. I adjudicate them:

| row | real? | reconciled? |
|---|---|---|
| C1 `S90Critic` — the battery does not print its own hash; a stub printing the target SUMMARY scores with zero runs (A5b) | real (the battery's own sha appears only in the prereg pin `e7265335…`; a stub would pass the literal predicate) | yes: the narrowing makes the pinned bytes + committed receipt the evidence; I re-ran the harness myself and the pins agree |
| C2 `S90Reviewer2` `c2-edge-probe` — a 201-byte stderr cut inside U+0085's encoding renders the surviving byte `\x85` (A4) | real (receipt shows `count_x85=1 count_u0085=0` for 101p+C285+98s) | yes: A4 adds the boundary clause; the clause is stated, not measured, and the boundary row is routed |
| C2 `S90Reviewer2` `c2-variant-doublebackslash-fixture` — a doubled-backslash spelling passes 12/12 (A1) | real (I re-ran the fixture on the committed variant, sha `5ec2e925…`, and reproduced 12/12) | yes: A1 names the brute-force probe as the injectivity evidence and routes the missing conjuncts |
| C2 `S90Reviewer2` `c2-variant-newline-fixture` — a raw newline in the detail passes 12/12 (A4) | real (committed receipt: the variant scores 12/12) | yes: recorded as an instrument gap; the filed tool's detail is one physical line |
| C2 `S90Sentinel` H1 — a one-token U+0085 backslash doubling survives the kill rule (A1) | real (same class as the variant above; H1 is HIGH and the seat did not repair the committed fixture) | yes: identical to A1's narrowing |
| C2 `S90Critic` — the fixture does not test the dead-code half (A5c) | real (a keep-`_one_line` tool scores 12/12) | yes: the deletion is measured by `grep`+AST load, the prereg's second evidence; I confirmed both |

No row is spurious and none is unreconciled. The C2 claim therefore verifies only under the A1/A4/A5 narrowings;
the report states exactly that. The C1 row narrows evidence quality, not any number.

## 3. Per-claim re-check

Work roots were empty directories under `/fast/scratch/hyaku/`, never `/tmp`. The committed lane bytes were
read-only; the only files I wrote are the scratch logs and this spot-check.

### C1 — calibration 7 (delta re-measured; tally evidence-verified; VERIFIES)

Pins re-derived from committed bytes:

- `diff census/round-89/c1-false-rows.tsv census/round-90/c1-false-rows.tsv` is exactly the appended `LD2b` line
  (`ZZ9<TAB>ABSENT`, 2 columns); both files' sha256 match the battery's PINS (`04570a64…`, `d64d7695…`).
- The counter is byte-identical to the frozen r87 counter, sha256 `fd0a8e24…`; the r90 mutant FILE differs from
  r89 only in its top-level `note` — `json` equality of the 16 `members` lists is `True` (A5a's narrowing).
- `grep -c 'ZZ9' census/round-77/c2-pointer-ledger.tsv` -> 0; `m17c`'s `old` is exactly the
  `len(r) < 3 or r[0] in ledger` line and its `new` drops the length guard.

Targeted reproduction of the claim's delta with the committed r90 harness (four arms; the harness sha256 matches
its pin `c3664747…`, fixture revs print as in the receipt):

```
pristine counter / r89 population : rows=57 mismatches=0 ... exit=0
pristine counter / r90 population : rows=58 mismatches=0 ... exit=0
m17c-mutated     / r89 population : rows=57 mismatches=0 ... exit=0   (survives)
m17c-mutated     / r90 population : rows=58 mismatches=1 ... exit=1   (killed)
  sole mismatch: ROW LD2b where=ledger item=ZZ9 expect=LEDGER-REFUSED/1 got=- match=no
```

So the do-nothing control is green on r89 and m17c is alive there; on r90 the ONLY failing row under m17c is
LD2b. That reproduces the claimed mechanism and the `killed_r89=15 → killed_r90=16` step (the r89 15-kill tally
is inherited unchanged from the r89 closure, same counter and mutant bytes). The full 16-mutant
`killed_total=31` is evidence-verified from `census/round-90/records/c1-after.txt`, which matches the report and
the prereg cell for cell; the battery's own sha is externally pinned in F (`e7265335…`) but not self-printed
(A5b). **Verdict: C1 verifies; calibration `improved`.**

### C2 — operability 8 (re-measured; VERIFIES as narrowed)

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-90/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r90-verify-c2
CASE KFF9 tool=pass before=fail ; CASE KFF10 tool=pass before=fail ; all other cases pass on both arms
SUMMARY cases=12 tool_pass=12 before_pass=10        FIXTURE_EXIT=0
```

Do-nothing control (the r89 bytes as BOTH arms): `SUMMARY cases=12 tool_pass=10 before_pass=10`, KFF9/KFF10
fail on both arms, `EXIT=1` — identical to `census/round-90/records/prefreeze-c2-control.txt`. The r87 12-row K4
regression on the filed tool re-read `SUMMARY rows=12 mismatches=0 errors=0`, `EXIT=0` (writer `70bbf1c2…`).
Tool, before-arm, fixture and harness hashes all match the report (`d095b52f…`, `f6fce6d1…`, `d4417213…`).

Independent escape probe (my own script, importing the committed tool): `_escape_text(_decode_record(b"\x85"))`
= `\x85`, `_escape_text("\u0085")` = `\u0085`, the literal twins print doubled backslashes, the pair is distinct,
and a 10-character single/pair sweep has zero collisions. `grep -c 'def _one_line('` -> 0, no `_one_line(` call
remains, and `ast.parse` loads the module. The r89 base tool's `o == 0x85` branch printed the character as
`\x85`, so the collision C2 repairs is real at the base bytes.

The narrowings are real: the doubled-backslash variant (committed at
`.ufo/waves/round-90/w1/S90Reviewer2/receipts/variant-doublebackslash-tool.py`, sha `5ec2e925…`) passes the r90
fixture 12/12, so the fixture does not certify the word "injective"; the edge probe shows a window cut inside
U+0085's encoding renders `\x85`; a raw newline in the detail passes 12/12; a keep-`_one_line` tool passes 12/12.
The report and plan A1/A4/A5 name each of these rather than widening the claim. **Verdict: C2 verifies under its
narrowings; operability `improved`.**

### Axis-harm check

`git diff bd760432 93c7e6dc -- SCORECARD.md` is additive (the r90 measurement block, two capability rows, the
r91 planned block, and the r89 "Planned (r90)" block relabelled historical); no axis score changed. `SKILL.md`
and `PROVINCE.md` are untouched; `corpus/SOURCES.md` has one insertion and zero deletions; `corpus/QUALITY.md`,
`corpus/README.md`, the knowledge entry and the lesson are additive; `tools/souji-record-agreement.py` is the
only code repair (+10/−21). No file outside the lane changed and no other lane was touched. No owned axis was
harmed.

## 4. Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | C1 binds the last unrowed clause of the r89 mutant set through an absent-id population row; the delta is re-measured and the m17c kill is LD2b-only |
| operability | improved | C2's public path reads 12/12 vs 10/10 (re-measured), the r87 K4 counter stays green, and the dead escape-first helper is gone (grep + AST) |
| depth | unchanged | SKILL.md is untouched; no new decision table or error pattern this round |
| coverage | unchanged | PROVINCE.md is untouched; the knowledge entry is a frontier note, not a new surface |
| freshness | unchanged | no drift re-verification claim this round; the S353 source is new, not stale-held |
| adjacency | unchanged | the connector's sibling scan found no contested scope (S90Connector §3); no cross-domain absorption |

## 5. Discernment spot-check (`corpus/lessons/round-90.md` `## Gate`)

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin
souji` -> `souji ok`, `EXIT=0`, W04 warnings only. Rows `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
corpus/SOURCES.md` -> 275 at tip, 274 at base `bd760432`; the SOURCES diff is one inserted row, no touched rows.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S353 Unicode UAX #14, § NL: Next Line (the round's admit) | admit, tier A `docs`, `mined` | live `https://www.unicode.org/reports/tr14/` -> HTTP 200, 226,166 bytes, sha256 `296df533…c7c0`, byte-identical to `census/round-90/srcs/tr14.html`; quote at capture lines 2878-2879, occurrence count 1 | agree | the 18-word quote "The NL class acts like BK in all respects (there is a mandatory break after any NEL character)." is present once; the class-table row `0085 / NEXT LINE (NEL)` is at 2873-2876; U+0085 = NL grounds the byte/character rule C2 rests on, and the row scopes itself to that section |
| UAX #13, Unicode Newline Guidelines (the round's reject sample, not filed) | reject (supersession tombstone) | live `https://www.unicode.org/reports/tr13/` -> HTTP 200, 6,348 bytes, sha256 `bfa7f97b…7c78`, byte-identical to `census/round-90/srcs/tr13.html`; 25-word quote found once | agree | the page only says the material moved into the Core Specification from Version 4.0; the archived `tr13-9.html` (opened by S90ScoutSources) treats CR/LF/CRLF/NEL alike on input, the opposite of the distinction this cell needs, so a reject with a flip condition is the right gate call |
| S353's registry quote (`corpus/SOURCES.md:292`) | ≤25 words? | the row's quoted sentence and the capture above | agree | 18 words, occurrence 1, `status=mined`, `used-by=corpus/knowledge/nel-byte-character-pair.md` (exists), `verified-at` 2026-11-08, `recheck` 365d; the row quotes the section and capture lines, not the convention-dependent offset |

The spot-check agrees with both sampled gate decisions; the lesson's `## Mistakes` carries three rows with
evidence and fixes (wave-evidence durability, pre-freeze after-data, S352 label), none of which I found unfixed.

## 6. Trend verdicts

- **expansion: improved.** `SOURCES.md` 274 -> 275 rows with one new tier-A `mined` row (S353) and a new
  admitted knowledge entry (`corpus/knowledge/nel-byte-character-pair.md`) whose `source:` cites S353, S348 and
  S351; the frontier map gains the r87-r90 rows, and two capability rows enter the table with passing r90
  demonstrations.
- **quality: improved.** The filed tool separates the byte/character pair through the public path (12/12 vs the
  r89 tool's 10/12, re-measured), the r87 12-row K4 counter stays green (re-measured), the dead helper is
  deleted and the module loads, Q165 adds the "measurement must discriminate" criterion, and no admitted entry
  was found false and left unmarked. The instrument gaps the wave found are narrowed and routed, not hidden.
- **discernment: improved.** The round's own wave falsified six sentences — one C1 evidence sentence, four C2
  sentence clauses plus the injectivity certification — and the lane narrowed each in `plans/round-90.md`
  A1/A4/A5 before filing rather than defending them; the S353 offset slip and quote word count were corrected
  before the row landed; my sampled gate decisions both agree. The r89 design-only capability row still sits in
  the r89 capability table (prose calls it superseded), a record-hygiene defect carried below, not a
  discernment regression.

## 7. Routed defects for r91

1. **Wrong claims path in the report (minor).** `census/round-90/claims.json` does not exist; the frozen claims
   are `.ufo/waves/round-90/claims.json`. Correct the citation in the r91 report's errata or a new report line.
2. **Attack-share arithmetic (minor).** The report's 7/12 conflicts with the preregistration's 6/12 and the
   addendum's 5/12; cite one definition (all are >= 25 %).
3. **Settlement-record disclosure (minor).** State that the driver's `w1-results.json` retained no seat outputs
   (`output: null`, kernel restart) and that the 12 committed seat reports are the settlement evidence.
4. **r89 capability row (carried from the r89 spot-check).** "a malformed-row binding whose id is absent from
   the ledger (measured, not landed)" still sits in the r89 capability table; AXES.md says a capability without
   a passing demonstration does not enter the table. The r90 prose calls it superseded by the landed row —
   remove or annotate the row itself.
5. **Carry the narrowed instrument work.** KFF9/KFF10 doubled-spelling conjuncts (`count(bs*2+"u0085")==0`,
   `count(bs*2+"x85")==0`), the raw-window boundary row, the "one physical line" row, a fixture row for the
   `_one_line` deletion, and the battery self-pin (A5b), all already in `### Planned (r91)`.

## 8. Closure verdict

Both declared claims verify (C1 by a re-measured delta plus the committed 16-mutant receipt, C2 by a re-measured
public path under its recorded narrowings); no owned axis is harmed; the three learning trends are `improved`.
The routed defects above are record-accuracy items and do not bar admission.
