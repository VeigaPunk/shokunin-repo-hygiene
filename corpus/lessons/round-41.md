# Round 41 — lesson (souji)

Round: souji round 41, hyaku run 11, attempt 1. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base revision: `7eebc183f2685d1ea9b004b4de22c09a8a4035a7` (the r40 non-author closure spot-check). Frozen instruments commit
`6682b98175b995ee4646ffd1ea6bd8a12cd353dd`; freeze commit `e2a74312af4233963e44e4dbb38838ece07b8bd2` (first commit to add
`census/round-41/preregistration.txt`; no wave file existed before it).
Non-author review read first: `corpus/lessons/round-40-verifier-spotcheck.md` (all four routed defects R40-D-PRUNE, R40-D-C1-BEFORE,
R40-D-FREEZE, R40-D-TOTAL are answered below or by a landed artifact; see `## Mistakes`).

## Gate — sources opened this round

One row, opened on **2026-10-28** by the L1 from the upstream raw URL (the access date is this round's own; the staged package's
dates prove nothing about this lane). Fetched bytes are pinned in `census/round-41/sources/SHA256SUMS`.

| id | url | access date | located quote (<=25 words) | location | admitted for |
|---|---|---|---|---|---|
| S258 | https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c | 2026-10-28 | "prune missing working trees older than <time>" | `builtin/worktree.c` at tag v2.56.0, line 255 (the `N_()` help string of `prune --expire`); the file is 1541 lines, sha256 `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc`; snapshot `census/round-41/sources/git-v2.56.0-builtin-worktree.c` | C1 item I1's sourced leg: it re-pins the builtin half of S009 at v2.56.0 |

Located and checked by hand: `grep -n -F 'prune missing working trees older than <time>'` on the snapshot prints exactly one match,
line 255; line 229 reads `if (should_prune_worktree(the_repository, d->d_name, &reason, &path, expire))`; line 259 reads
`expire = TIME_MAX;`. The v2.55.0 file (snapshot `census/round-41/sources/git-v2.55.0-builtin-worktree.c`, sha256
`2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884`) differs from v2.56.0 in lines 171-266 only at line 229, where the
v2.56.0 call gains `the_repository` as its first argument (`diff <(sed -n 171,266p v2.55.0) <(sed -n 171,266p v2.56.0)`). Seat
`R41scribe04` quoted the v2.56.0 sha256 with two transposed characters (`...c523c1e...` vs the observed `...bd523e1c...`); the figure
above is the one `sha256sum` printed here.

### Assimilation: none — and the r40 reject of staged `fleet-prune-safety-r28.md` is re-decided (R40-D-PRUNE)

No package bytes were appended this round (`/home/vgpnk/Projects/shokuknow` was not read). The round-40 gate rejected the staged
`fleet-prune-safety-r28.md` (staged row S160, git v2.56.0 `worktree.c`) with the reason "the lane already holds git's prune gate
(`worktree.c` appears in 9 rows ...); adopting it again would be a duplicate". The counts below show the reason did not reproduce:
at `bffcc0f660ff36eb8add3f61582748a7af019a5b` two registry rows contain the literal `worktree.c` (S009, S033), one row cites the file
as a source (S009, pinned at v2.55.0, whose own note says the v2.56.0 recheck is pending) and no row cites it at v2.56.0. The item
was therefore a freshness re-pin on held ground, not a duplicate. This round re-decides it as **admit-by-reopening**: the upstream source
was opened directly (S258), the staged package was not adopted, and the staged item stays unadopted. QUALITY Q98 records the rule.

## Corrections to filed round-40 statements

Appended in round 41; the round-40 text is not rewritten. Each CORRECTION line carries the value that the frozen counter
`census/round-41/c1-counter.py` derives at `bffcc0f660ff36eb8add3f61582748a7af019a5b`, the revision the round-40 spot-check measured.
The prose around each line states the scope the derived value covers; the line alone does not (R41reviewer03, M41-4).

### I1 — `corpus/lessons/round-40.md` § Assimilation gate: "`worktree.c` appears in 9 rows"

The filed number is wrong by any reading. At bffcc0f the registry has 181 rows; the rows whose text contains the literal `worktree.c`
number two (S009, which cites the file as a v2.55.0 source, and S033, whose cell says "although worktree.c ages by it"); the rows
whose text contains `v2.56.0/worktree.c` number zero. The spot-check's own method (rows that cite the file as a source) gives one.
Re-run:

```
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'worktree\.c'
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'v2\.56\.0/worktree\.c'
```

The source row for the v2.56.0 file is S258 (registry, this round).

CORRECTION I1 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=S258

### I3 — `SCORECARD.md` round-40 C1 row presents `c1-before.txt` and `c1-after-h.txt` as one before→after

The two arms ran over different register files. `census/round-40/records/c1-before.txt` reports `register_cells=6` (register
`census/round-39/cells.tsv`, measured at the frozen base) and `census/round-40/records/c1-after-h.txt` reports `register_cells=3`
(register `census/round-40/cells.tsv`). The register arm of that row is not like-for-like; its item arm (`items=3 open=3` →
`open=0`) is a different, narrower statement. The derivation reads the two receipts' `register_cells=` values only; it does not
prove the cause (the receipts' command headers do, and R41reviewer02 names the register blobs).

```
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*' | head -1
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-after-h.txt | grep -o 'register_cells=[0-9]*' | head -1
```

CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-

### I4 — `LOG.md:1909` (r40 entry): the dead seats' provider error text, and "All wave evidence is captured under `census/round-40/waves/`"

`LOG.md:1909` records two dead seats (`R40w2reviewer01/04`) with the provider error text `Codex error event: Invalid prompt: ...` and
says all wave evidence is captured under `census/round-40/waves/`. Scope of the derived value: the committed bytes under
`census/round-40/waves/` (136 files at bffcc0f, including `w2-results.json`, where both seats have partial outputs and no error
text) contain that text zero times. It does **not** mean the text is unrecorded anywhere: `LOG.md:1909` carries it, so does the fleet
report `.ufo/reports/round-40/souji.md:79`, and the lane at bffcc0f has no other carrier (R41scout03, R41reviewer03). The error
text's origin is the orchestrator's live transcript, which is not a committed receipt; whether the provider message was exactly that is
`[INFERENCE]` from the committed bytes.

```
git ls-tree -r --name-only bffcc0f660ff36eb8add3f61582748a7af019a5b census/round-40/waves/ | while read -r f; do git show "bffcc0f660ff36eb8add3f61582748a7af019a5b:$f" | grep -c 'flagged as potentially'; done | awk '{s+=$1} END{print s+0}'
```

CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-

## Mistakes

### M41-1 — the round-40 claims froze predicates but not the artifacts they named

- **class:** scope (the claim's population and boundary were not in the frozen bytes); facet stale-premise.
- **evidence pointer:** `census/round-40/preregistration.txt` (sha256 `7218101a24a48ce8648e9625c992af1aa972d0e4274f17044e185ac0b3b4758c`,
  first added at `128e412`): C2 "verifies all observed class/trigger pairs in the frozen list" (no list in the file), C3 "the r39 base
  fixture" (no path, no digest), C1 "each anchored item line" (no item table); `grep -n -iE 'sha256|digest'` over the file finds nothing.
  Seat evidence: `corpus/lessons/round-40.md` M40-3..M40-5 and `census/round-40/waves/w1/R40sentinel23.md`.
- **captured-by:** none that runs. QUALITY Q93/Q94/Q95 state the rule in prose, but they were first committed at `994de3b`, a strict
  descendant of `128e412`, so they post-date the freeze they should have caught; no committed command read a preregistration
  (sweep: `grep -n -iE 'freez|frozen|pre-?data|population|preregist' corpus/QUALITY.md` — 27 lines, none runnable;
  `grep -n -iE 'population|digest|sha256|freez' tools/souji-axis-check.py` — no match).
- **fix:** C2's `tools/souji-freeze-check.py` (grammar and 21 cases in `census/round-41/c2-counter.py`). Shown able to fail: the
  frozen controls reject an always-clean stub (2 of 21 cases pass, `controls/c2-control.txt`) and an always-findings stub; the tool
  is absent at the freeze commit (`pass=0`). Limit: the check reads the preregistration's shape, digests and order; it does not read a
  Population file's content, so Q93's probe-byte and Q94's TOTAL-ordering clauses stay with the claim that names them (QUALITY Q99).

### M41-2 — the round-40 dead-seat error text was filed as fact with no committed occurrence

- **class:** attribution (a filed cause with no located source in committed bytes).
- **evidence pointer:** `LOG.md:1909`; zero occurrences under `census/round-40/waves/` (item I4 above); `census/round-40/waves/w2-results.json`
  holds both seats' partial outputs without the text; no `R40w2reviewer01` or `R40w2reviewer04` report file exists in
  `census/round-40/waves/w2/`; the round-40 `w2-run.err` is empty and was never committed. The only committed Codex error text in the lane
  is a different message (`census/round-20/recovery-seat-outcomes.json`).
- **captured-by:** none. `corpus/QUALITY.md:8` ("a quote its location") should have caught it; the landing gate's seat-carry check reads
  only `STATUS:` lines and `## Seat-reported failures` sections, and round 40 has neither, so it was vacuous for that round
  (`python3 -B tools/souji-landing-gate.py --root . --rev bffcc0f660ff36eb8add3f61582748a7af019a5b --round 40` reports `status_lines=0
  carry_heading=0`, per R41scribe09).
- **fix:** the I4 CORRECTION above (append-only). Routed, not fixed: a seat-failure carry rule that reads `census/round-N/waves/*-results.json`.

### M41-3 — a counter that scores the shape of an artifact is fooled by artifacts with the right shape

- **class:** vacuous (a verdict earned by format).
- **evidence pointer:** wave 1. `R41critic01` built eight lessons the frozen C1 counter scored green with the filed statements
  retracted by nobody: a lesson whose prose says "the filed statement stands" (A2), the three lines inside a code fence (A3), malformed or
  indented wrong lines that skip the `junk` check (A5, A7 control), and a registry row that says "NOT OPENED" (A1, A8). `R41critic02` K2/K4/K5:
  a quote-less S258 row and a rewritten S033 row both score `sourced=1`. `R41critic03` and `R41critic04` built C2/C3 candidates that never run
  the tool (a fingerprint table keyed by the fixture's own commit content; fixtures that read the `ZZ-MUTANT` label or the `mut-S<NN>.py` file
  name) and score the target.
- **captured-by:** none; the claim-sizing rule (addendum section 9) names do-nothing controls, and the controls here (absent artifact,
  always-clean stub) pass it, but no control built the honest-shape/dishonest-substance artifact.
- **fix:** none in the frozen counters (the preregistration forbids it). Instead: (1) the landed artifacts are audited by checks outside the
  counters (L1 execution-count shim over the C3 fixture candidates: every candidate invoked the tool 21 times, one per probe;
  `census/round-41/records/shim-audit.txt`); (2) the C2 tool is audited by the wave-2 hidden-case audit (cases the counter does not hold);
  (3) the S258 row's quote and snapshot were re-opened by a second seat in wave 2; (4) QUALITY Q100 records the rule. Whether this closes the
  class is open: a counter that cannot fail on a sniffing artifact stays a named limit (N5, N6).

### M41-4 — a derived value that names no scope reads as a different claim

- **class:** scope (R41reviewer03 F-I4-1/F-I4-2).
- **evidence pointer:** the I4 CORRECTION line carries `occurrences=0`, true under `census/round-40/waves/` and false across the lane (LOG.md:1909
  carries the text).
- **captured-by:** none. **fix:** each CORRECTION block above states its derivation scope in prose; QUALITY Q100 requires it.

## Named limits of the frozen instruments (found in wave 1; none edited, none narrows a target)

- **N1 C1 counter** accepts duplicated lines, lines inside code fences, and prose retracting the correction; it skips malformed lines
  instead of counting them as `junk` (R41critic01 A2-A6).
- **N2 C1 `sourced`** is substring-based: a placeholder row that says "NOT OPENED" and a row inside a code fence pass; a rewritten
  registry row passes (the counter does not check `corpus/SOURCES.md` for append-only) (R41critic01 A1/A8, R41critic02 K2/K4). Compensating
  checks this round: S258's quote and snapshot are re-derived above; the registry change is a pure append (`git diff --stat`); the
  registry census exits 0.
- **N3 C1 `junk`** does not validate the `source=` token of a correct-looking I1 line (R41critic02 K5).
- **N4 C1 I4** derives over `census/round-40/waves/` while the population names LOG.md as the recording file (R41reviewer03).
- **N5 C2** legs and cases do not force the tool to read its input: the real and retro legs check a path string and a count, fixture
  directories are named `cand-<case>`, fixture bytes are deterministic, and the all-target-then-smaller selection rule favours a
  memorising candidate (R41critic03). A tool that drops the `*.ready` branch passes 21/21 (R41critic06).
- **N6 C3** does not require the fixture to execute the tool; the scratch mutant name leaks the site (`mut-S<NN>.py`); `parse_sites`
  discards the trigger column (R41critic04).
- **N7 R1** "killed by the r39/r40 fixture alone" is a docstring promise the code does not enforce; its PRIOR set omits four drift
  fixtures that also pass on the pinned tool (R41critic05 F1, R41critic07).
- **N8 preregistration Targets** are printed prefixes of the counters' SUMMARY lines with a trailing `(exit 0)` no counter prints
  (R41reviewer05 F1); the receipts' `EXIT=` line is the exit evidence.
- **N9 `score-candidate.sh`** takes any dest (path traversal, tracked symlinks written through, a dest naming a counter) and runs
  fixtures unconfined (R41sentinel01 F2-F6). This round used only allowlisted dests and the landing measurements run the lane's
  committed counters, not the scoring clone's.
- **N10 tool defect, routed (not this round's claim):** `tools/souji-worktree-drift.py` follows a leaf symlink named by `--json`
  (R41sentinel01 F1); fixtures must create every `--json` target under their own work directory.
- **N11 pre-existing registry red at the freeze tip:** `python3 -B tools/souji-registry-agreement.py` reports `K1 cited-no-row S146`
  (`corpus/knowledge/origin-record-format-gvfs-r40.md` cites a staged id the lane registry does not hold) (R41critic07).
- **N12 sizing:** each claim is reachable by a partial-work control that passes the full target (C1 by a copied correction plus a fabricated
  row, C2 by a tool that drops one branch, C3 by a fixture that never executes a refusal) (R41critic06). The honest landings are measured
  and audited above; the sizing finding is reported against the claims, not repaired.
- **Routed forward (R41connector02):** M40-12 (the decoder mutant `backslashreplace` survives the r40 fixture), R39-D1/D2 (stale census
  receipt and mismatched receipt-header revision), the count-before-last-append pattern (r38-r40), receipts naming scratch paths, and
  in-place edits of append-only artifacts (r38, r39).

## Wave-2 findings, landing deviation and errata (appended after the C1 landing at 31e4d3e; the CORRECTION lines above are untouched)

Wave 2 (37 seats, `census/round-41/waves/w2/`) re-measured the four landed artifacts and attacked them. The reviewers (`R41w2reviewer01`-`03`, `08`)
reproduced every receipt: C1 `items=3 ... corrected=3 ... sourced=1`, C2 `cases=21 pass=21 fail=0 ... real=ok retro=red`, C3 `killed=19 survived=0`,
R1 `killed=11 survived=0`, and found the preregistration, counters, populations, controls and the pinned tool unchanged since the freeze commit.

### E1 — landing deviation: the C2 tool was hardened after wave-2 attacks (counter, population, predicate and kill rule untouched)

The preregistration (rule 3) says the L1 lands the candidate the frozen counter scores best; it fixes no rule for repairing the winner. At the
first landing (`119c26fa3bbb85e215824de9538bd2eb34e9f874`, `R41executor07` bytes, sha256 `3c3e80ba...`) the frozen counter read 21/21
(`census/round-41/records/c2-after.txt`). `R41w2critic01` (57 crafted preregistrations: 23 false greens, 3 crashes, 4 false findings),
`R41w2executor01` (hidden-case audit, strict 79/83), `R41w2executor02` (CRLF `Round:` fail-open) and `R41w2sentinel01` (caller `GIT_DIR` changes a verdict,
a FIFO `.mailmap` hangs `git log`) showed the tool was not operable on in-grammar input the 21 cases do not hold. The L1 then landed three hardening
commits to `tools/souji-freeze-check.py` only (`383972ce`, `c98fa5f1`, `72e8a0b6`; changes: empty value of any key is `FIELD-EMPTY`; a missing `Round:` line is
`FIELD-MISSING C0 Round`; CRLF/BOM `Round:` tolerated; paths may contain spaces; a NUL in a path no longer crashes; git path quoting off so non-ASCII dispatch
file names are seen; a whitelisted git environment with no `GIT_DIR`, no mailmap, no replace refs). The frozen counter was re-run on the final bytes:
`census/round-41/records/c2-after-hardened.txt` (`cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red`, tool sha256
`8131847b...`, `retro` findings 18 -> 19 because the old-grammar r40 file has no `Round:` line). The hidden-case audit on the final bytes reads strict 80/83
(`census/round-41/records/hidden-audit-hardened.txt`): the three remaining strict "fails" are the deliberate `FIELD-MISSING Round` choice the audit's
expectation did not anticipate. This is reported as a deviation: both measurements stand side by side, and a closure that holds the first landing
as the claim's bytes has the first receipt.

### E2 — corrections to this lesson's own text (R41w2reviewer05, R41w2reviewer06; the reviewers' item tables are in their reports)

- **Q98-Q102** cited in this lesson now exist: they were committed after the lesson (`832b7bbe`), so the text above cited ids that were absent at `31e4d3e`.
  Q102 (hidden-case audit) is new this round and has no earlier mention.
- **M41-1** sweep count: `grep -n -iE 'freez|frozen|pre-?data|population|preregist' corpus/QUALITY.md` prints **25** lines, not 27 (at `bffcc0f` and at `1d41c13`).
  "The tool is absent at the freeze commit": `git cat-file -e e2a7431:tools/souji-freeze-check.py` fails; the receipt `controls/c2-control.txt` records the absence at the
  instruments commit `6682b98`, not at `e2a7431`.
- **M41-2** "the only committed Codex error text in the lane is a different message" is false as written: `git grep -n -E 'Codex error|Invalid prompt' bffcc0f` also returns
  `.ufo/waves/round-21/provider-error-excerpts.json`, `corpus/lessons/round-22.md:187` and copies under `census/round-26/`. The claim that holds: the string `Invalid prompt`
  occurs in committed lane bytes only at `LOG.md:1909`. The fleet report cited as `.ufo/reports/round-40/souji.md:79` is the **fleet-root** path
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md` (tracked in the fleet repo, absent from the lane).
- **M41-3** `R41critic01` built eight candidates of which **seven** (A1-A6, A8) scored green; A7 is the red control. "A registry row that says NOT OPENED" is A1 only
  (A8 is a row inside a code fence). `R41critic02` K5 is the junk-check gap (N3), not a quote-less or rewritten row (K2, K4).
- **N2** "the registry census exits 0" means `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` (exit 0, `census/round-41/records/census-final.txt`);
  `tools/souji-registry-agreement.py` exits 1 at the tip for the pre-existing `K1 cited-no-row S146` (N11).
- **I3** the SCORECARD row is `SCORECARD.md:791` ("C1 evidence-bound closures + strict-descendant register"); its before arm is `c1-before.txt` and its after arm is `c1-after-d.txt`
  (also `register_cells=3` over `census/round-40/cells.tsv`); `c1-after-h.txt` appears at `SCORECARD.md:801` and `:811`. The derived `before=6,after=3` stands. The counter
  hard-codes `c1-after-h.txt` (c1-counter.py:81).
- **Gate, S009**: the "pending recheck for v2.56.0" note sits in S009's used-by file `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:27`, not in the S009 row.
- **I1** "wrong by any reading" overstates: two readings were tried and neither gives 9. Method fragility (R41w2reviewer05 N-a): the literal `v2\.56\.0/worktree\.c`
  matches `S258` only if written without `builtin/`, so the count at the tip is 0 although S258 is a v2.56.0 source row; the derived 0 is a statement about `bffcc0f`.
  The whole-file diff of the two worktree.c tags has 37 hunks; only the :171-266 region differs solely at :229 (R41w2reviewer04 F4).

### Further named limits (wave 2)

- **N13 C2 tool** (landed bytes, after hardening): duplicate keys read first-wins; a malformed `## C` heading is dropped silently; dispatch files named other than `*-dispatch.json` or
  `*.ready` (the lane tracks `*-dispatch-attempts.txt`) are not checked; a symlink Counter reads the link text; a non-UTF-8 path byte is fail-closed
  (R41w2critic01 D4/D7/D9-D11, R41w2critic02). Caller env and a FIFO `.mailmap` were closed by E1.
- **N14 C3 is class-level coverage**: of 29 behavioural (non-label) mutants of the pinned tool, the fixture kills 21 and 8 survive; 17 of the non-equivalent mutants in
  `R41w2mutationtester03` also escape it. P16 does not prove S16 by condition (R41w2critic03 findings 1, 3, 4). The claim's predicate (label rewrite turns exactly the mapped probes red) holds;
  a condition-level reading does not.
- **N15 R1 is not exhaustive**: of 24 further mutants, 15 survive all three drift fixtures (R41w2mutationtester04); a last-position disagreeing TOTAL is killed by r40, r36 and r38-record but never by R1's own cases
  (R41w2critic05).
- **N16 C1 counter**: 28 of 60 single-point mutants of the counter are invisible to all three frozen inputs (R41w2mutationtester05); 15 of 46 edits to the landed lesson/registry leave the target
  met (R41w2mutationtester06): the counter catches every edit to a field it reads and none to prose.
- **N17 fixtures and harness**: the C3 fixture leaves ~26 entries under `--work` after SIGTERM/SIGKILL (R41w2sentinel02, R41w2critic04); `score-candidate.sh` stays unconfined (N9).
- **N18 landing gate**: `python3 -B tools/souji-landing-gate.py --round 41` raised `LG-DANGLING-PTR` for the lesson's pointer to an untracked round-40 file and for QUALITY pointers into
  the ignored `.ufo/waves/round-41/`; the lesson was reworded and the QUALITY pointers repointed to `census/round-41/waves/` (captured at the same commit).
- **N19 axis-harm audit** (R41w2executor03, R41w2executor04): 59 of 61 gate rows identical at base and tip (one flake, `r18-leak-count`); the six r36-r40 drift fixtures unchanged; the only
  harm-shaped difference was the dangling pointer in N18.
