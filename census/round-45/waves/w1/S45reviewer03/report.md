# S45reviewer03 — Independent historical register identity audit #3 of 66

- Seat: S45reviewer03 (zero-based population index 2)
- Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
- Freeze: 019bccc9ac97f3cec1a1dea574cc2f81f57fc967 (ancestor of HEAD 18e6ec5f1d470afc50992abf8ab4dc5539ad8bd2)
- Derivation base (BASE): 55d7af6f5a22340f7a3de1c386e514ababfaa75f
- Scope: exactly one bounded identity check. No production/fleet writes, no git/jj mutation, no subagent dispatch, no counter freeze bytes amended. No tooling installs were needed (git, awk, python3 already present; pacman transactions remain paused per directive).

## Assigned identity

Population file: census/round-44/c1-population.tsv (sha256 at freeze = 422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c, matches preregistration pin; working-tree copy byte-identical).

Programmatic key ordering (first-occurrence, unique keys): rows=70, unique=66, index 2 = **(line 22, token `c2-after.tsv`, class `mismatch:path-absent`)**, reason filed in population: "not in tree at 55d7af6f5a22340f7a3de1c386e514ababfaa75f".

Register entry (corpus/lessons/round-44.md at freeze, file line 27):

```
CORRECTION-R44 id=R44-03 file=SCORECARD.md line=22 class=mismatch:path-absent stale=c2-after.tsv derived=multi:census/round-24/records/c2-after.tsv;census/round-25/records/c2-after.tsv;census/round-26/records/c2-after.tsv;census/round-27/records/c2-after.tsv;census/round-28/records/c2-after.tsv;census/round-42/waves/w1/R42critic01/k4/c2-after.tsv rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
```

Entry admissibility: column-0 `CORRECTION-R44 ` line; field set exactly {id,file,line,class,stale,derived,rev,scope}; file=SCORECARD.md; rev=BASE; id matches R44-\d{2,}; no fence open on any line before it (awk scan) → it is counted, not fenced/junk. 66 CORRECTION-R44 lines total in the frozen register.

## New counter read

census/round-45/c1-counter.py (sha256 = 46d5fc68497d7d289b43f55f9c808d6da1d309900d357ebc608542436ee34125, matches preregistration pin at freeze and on disk). Relevant rule for this class (source lines 60–66): for `mismatch:path-absent` with a token containing no `/`, take all tree paths at BASE whose basename equals the token, sort; exactly one → that path, more than one → `multi:` + `;`-join, none → `UNHELD`. The counter cross-checks the population against the historical instrument output before scoring (facts equality gate), then compares each filed `derived` against this deterministic expectation.

## Bounded probes executed (exact commands)

1. Population pin and index derivation:
   `git show 019bccc9:.../c1-population.tsv | sha256sum` → 422875…c1e2c; python first-occurrence unique-key ordering → index 2 = (22, c2-after.tsv, mismatch:path-absent).
2. Register read: `git show 019bccc9:corpus/lessons/round-44.md | sed -n '27p'` and `grep -n 'line=22 '` → the R44-03 line quoted above.
3. Independent derivation from BASE blobs (no counter code executed for the value itself):
   `git ls-tree -r --name-only 55d7af6f… | awk -F/ '$NF=="c2-after.tsv"' | LC_ALL=C sort`
   → 6 paths: census/round-24/records/c2-after.tsv; census/round-25/records/c2-after.tsv; census/round-26/records/c2-after.tsv; census/round-27/records/c2-after.tsv; census/round-28/records/c2-after.tsv; census/round-42/waves/w1/R42critic01/k4/c2-after.tsv
   Expected derived = `multi:` + `;`-join = the string in expected-derived.txt; `diff expected-derived.txt filed-derived.txt` → clean (DERIVED-EXACT-MATCH).
4. Historical instrument cross-check (tools/souji-declared-evidence.py blob at BASE, run read-only against the lane with TMPDIR confined to seat scratch):
   `python3 -B instrument.py --root <lane> --rev 55d7af6f… --file SCORECARD.md --format tsv` (rc=1 overall, expected for this audit). Row for line 22:
   `22  c2-after.tsv  A  mismatch:path-absent  not in tree at 55d7af6f…` — exactly the population key and reason; the sibling span `census/round-28/records/c2-before.tsv` is `resolved/present`, and the bare rev token `ed270c42161cd…` is class B resolved.
5. SCORECARD.md line 22 at BASE (`git show 55d7af6f:SCORECARD.md | sed -n '22p'`): the cell names `census/round-28/records/c2-before.tsv`, `c2-after.tsv`, "measured at ed270c42161cd62829783a5e5d2ef4e27089331c" — confirming the stale token is a bare filename used inside a rev-context cell.
6. r42 accounting under Q76: census/round-42/c1-register.tsv (70 rows + header) line 4: `22  c2-after.tsv  resolved  census/round-28/records/c2-after.tsv`. corpus/QUALITY.md criterion Q76 (line 186) requires the before-state to count only mismatches the lane's self-assessment still carries; corpus/lessons/round-44.md:101-105 records the r44 C1 re-derivation as "the same 70-occurrence population as r42, 65 path-bound plus five already scoped/corrected, with zero new unresolved beliefs under Q76". This row is among the already-accounted 70.

## Observed result

**MATCH.** Filed derived token for R44-03 equals the independently derived expectation byte-for-byte (6-path `multi:` list, LC_ALL=C sort order). The population row, the historical instrument's line-22 output, and the register entry are mutually consistent at BASE. The entry is well-formed and admissible by the new counter's parser rules.

## Zero new factual credit

- This identity was already carried in the r42 register (`22 c2-after.tsv resolved census/round-28/records/c2-after.tsv`); r44 re-derived the same 70 occurrences and r45 only adds an instrument that accepts the filed register. Under Q76 the before-state excludes items the lane's self-assessment already carries, so there is no reduction in outstanding historical facts.
- The claim's own target prints `historical_credit=0`; corpus/lessons/round-45.md:3 states "Historical correction credit is exactly zero (Q76); the prior 70-occurrence population was already accounted for." What changes is measurement capability (0/66 → 66/66 accepted unique registrations with derived-token discrimination), not any SCORECARD fact. Calibration remains label 7; no numeric gain is asserted. This seat confirms that framing for this identity: nothing in this audit converts into a new correction.

## Attack: derivation proves referent, not historical runtime truth

The derivation is sound as a **register-consistency** fact and unsound as **runtime history**:

1. What it proves. At BASE, (a) the literal repo-relative path `c2-after.tsv` is absent, and (b) exactly six files share that basename. That is a static, BASE-indexed same-name census. It identifies a referent *set* for a loosely written bare filename.
2. Anachronism inside the set. The cell's own runtime rev is `ed270c42…` (ancestor of BASE). Probes: `git ls-tree -r --name-only ed270c42… census/round-28/records/` shows `c2-before.tsv` present and `c2-after.tsv` **absent**; the same-name census at that rev returns only 4 paths (rounds 24–27). `git log --diff-filter=A` shows census/round-28/records/c2-after.tsv entered the tree in fec846dd ("round-28: pin after measurements and source recheck receipts"), after the named measurement rev. The sixth member, census/round-42/waves/w1/R42critic01/k4/c2-after.tsv, is a round-42 fixture copy. So ≥2 of the 6 BASE candidates could not have been the r28 runtime referent — the set over-approximates.
3. Under-approximation risk, symmetric. If the true runtime file had a different basename or was uncommitted at BASE, the basename rule would miss it. Token-equality on `multi:` cannot distinguish "author meant census/round-28/records/c2-after.tsv" (as r42 resolved) from "any same-named blob". The `multi:` prefix honestly encodes that ambiguity, but ambiguity is the opposite of runtime identification.
4. Rule-circularity of the match. Filed and expected tokens agree because both are produced by the same deterministic derivation family (counter source lines 60–66 reproduce my independent awk). The match certifies the register was generated by (or faithfully re-enters) the frozen rule — a calibration property of the instrument, not evidence about what existed or was measured in round 28. Genuine runtime anchoring would need an external source (e.g., the r28 record bytes at the measurement rev, or round-28 workflow receipts), which this counter's contract does not consult.
5. Verdict on the attack. The claim text itself stays inside the safe reading: it asserts only "feasible token-bound verifier of the filed register" with historical credit zero. The derivation does not and cannot relabel referent identity as historical runtime truth; had the claim asserted the latter, this identity would be a counterexample.

## Limitations

- Identity-level audit only; the other 65 identities and the 12-case fixture were out of seat scope. The full c1-counter.py was read and its rule reproduced independently, but the integrated counter/fixture run is the planner/integrator's check, not this seat's.
- Historical instrument run used the live working tree as repo root with all reads pinned to BASE via git plumbing; TMPDIR confined to seat scratch. Instrument rc=1 is the expected audit state (mismatches exist population-wide), not a defect signal for line 22.
- The register line was located by grep and verified by `git show` at the freeze; no LSP server applies to this prose/md artifact (no code references to resolve), so no cold-index caveat arises.
- Working tree at HEAD 18e6ec5f contains other seats' in-flight changes (corpus/lessons/round-45.md modified; census/round-45/records untracked); all evidence above was read from the frozen blobs, so those changes do not touch this audit.

## Receipts

- expected-derived.txt, filed-derived.txt, derived-c2.txt, instrument-tsv.txt, scorecard-base.md, instrument.py, commands log: .ufo/waves/round-45/w1/S45reviewer03/ (receipts kept; scratch /fast/scratch/hyaku/souji-r45/S45reviewer03 removed before yield).
- Installs: none.
