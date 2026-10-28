# R41w2executor01 — hidden-case audit of tools/souji-freeze-check.py (C2 operability)

Verdict: **C2 landed tool is NOT hidden-case clean.** Two strict-tier defects (both silently drop `DISPATCH-BEFORE-FREEZE`, a false-clean on the exact failure the tool exists to catch), four literal-tier silent-pass defects, two ambiguous-tier divergences. The frozen counter's 21 cases are unaffected (it passes 21/21 on tip; none of the defects is in its population). The harness itself is shown able to fail (memoriser 20/83, always-clean stub 17/83) and able to pass (a two-line patched candidate 83/83), so the red result is the tool's, not the harness's.

## Artifacts (all under /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w2/R41w2executor01/)
- `hidden-audit.py` (sha256 5bcdf76b9d150b69ab4500acc8005f5faf08fdae4a8c0b2301e9fe140f0ef479): 92 scenarios per run. 84 hand-specified (strict 75 incl. 3 raw-prereg and 6 refusal cases, literal 4, ambig 5) + 8 fuzz scenarios of 5-9 claims. Per-run random: root dir, prereg path, instrument paths, commit messages (decoys such as "early dispatch"/"freeze" + random hex), salts in every file, claim numbers, CRLF/LF, defect combination. Oracle is the in-file `oracle()` written from the c2-counter.py grammar docstring; no code shared with the tool; every hand scenario's literal expectation is cross-checked against the oracle (harness aborts on disagreement, so a harness error cannot masquerade as a tool failure).
- `receipts/`: `landed-seed20261028.txt`, `landed-seeds-2-7-strict-fails.txt`, `fixed-candidate-seed20261028.txt`, `fixed-candidate-c2-score.txt`, `tr4-seed20261028.txt`, `stub-clean-seed20261028.txt`.
- `freeze-check-fixed-candidate.py` (sha256 6cb6a8b4…3095c): landed tool + two one-line changes (candidate only, not landed).
- Scratch /fast/scratch/hyaku/souji-r41/R41w2executor01 deleted. Nothing written to tests/, tools/, census/, corpus/ or any tracked file.

## Commands actually run
```
python3 -B .../hidden-audit.py --seed 20261028                       # landed tool = git show 1d41c135…:tools/souji-freeze-check.py (sha256 3c3e80ba…340b)
python3 -B .../hidden-audit.py --seed 2..7                           # six more seeds, landed tool
python3 -B .../hidden-audit.py --seed 20261028 --tool .../w1/R41critic03/tr4-fingerprint-table.py
python3 -B .../hidden-audit.py --seed 20261028 --tool census/round-41/controls/c2-stub-clean.py
python3 -B .../hidden-audit.py --seed 20261028 --tool .../freeze-check-fixed-candidate.py
bash census/round-41/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=.../freeze-check-fixed-candidate.py
python3 -B census/round-41/c2-counter.py --root <lane> --rev 1d41c135… --scratch <scratch>
```
Tip tool blob 1d41c135 == 119c26fa blob (same sha256 3c3e80ba…).

## Results (seed 20261028; verbatim SUMMARY lines)
```
landed         SUMMARY scenarios=92 strict=79/83 literal=0/4 ambig=3/5 seed=20261028 tool_sha256=3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b   (rc=1)
fixed-candidate SUMMARY scenarios=92 strict=83/83 literal=0/4 ambig=3/5 ... tool_sha256=6cb6a8b44a62e235fa5678813809ebe4ca255f3e7d4cabee0daeee95cea3095c           (rc=0)
tr4 memoriser  SUMMARY scenarios=92 strict=20/83 literal=0/4 ambig=3/5 ...                                                                                        (rc=1)
always-clean   SUMMARY scenarios=92 strict=17/83 literal=0/4 ambig=3/5 ...                                                                                        (rc=1)
fixed candidate under frozen counter: SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=6cb6a8b44a62
landed under frozen counter:          SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
```
Landed tool, seeds 2-7 (strict pass of 83): 78, 78, 76, 77, 75, 78 (`landed-seeds-2-7-strict-fails.txt`). In every seed every strict failure is one of: `crlf-defects-and-early-dispatch`, `dispatch-non-ascii-file-name`, `dispatch-non-ascii-directory`, or a `fuzz-*-crlf` scenario that carried early dispatch files. No LF fuzz scenario ever failed; no strict failure of any other class in any of 7 seeds. 72 of the 75 hand-specified strict scenarios (all grammar, digest, ancestry, edit, directory, empty-population, control, refusal, merge, rename, symlink/space/relative-root cases) pass in all 7 seeds.

Landed-tool table (non-PASS rows; every other row of the 92 is PASS, see receipts/landed-seed20261028.txt):
| tier | scenario | exit got/want | missing / extra (claim,class) |
|---|---|---|---|
| strict | crlf-defects-and-early-dispatch | 1/1 | missing C0 DISPATCH-BEFORE-FREEZE |
| strict | dispatch-non-ascii-file-name | 0/1 | missing C0 DISPATCH-BEFORE-FREEZE (tool exits CLEAN) |
| strict | dispatch-non-ascii-directory | 0/1 | missing C0 DISPATCH-BEFORE-FREEZE (tool exits CLEAN) |
| strict | fuzz-1-9claims-crlf | 1/1 | missing 2x C0 DISPATCH-BEFORE-FREEZE |
| literal | literal-base-blank (`Base:` empty) | 0/1 | missing C1 BASE-UNRESOLVED |
| literal | literal-counter-blank | 0/1 | missing C1 COUNTER-MISSING |
| literal | literal-population-blank | 0/1 | missing C1 POPULATION-MISSING |
| literal | literal-control-blank | 0/1 | missing C1 CONTROL-MISSING |
| ambig | ambig-counter-path-with-space | 1/0 | extra C1 COUNTER-MISSING, C1 POPULATION-MISSING |
| ambig | ambig-sha256-uppercase-hex | 1/0 | extra C1 COUNTER-DIGEST |
Passing ambig rows: counter-without-sha256 (COUNTER-DIGEST), counter-added-after-freeze (COUNTER-MISSING only), prereg-path-with-glob-chars (clean).

## Root causes (reproduced, not inferred)
1. **CRLF Round line (strict).** `ROUND = re.compile(r"^Round:[ \t]*(\d+)[ \t]*$", re.M)`; direct check: `ROUND.search("Round: 41\n…")` matches, `ROUND.search("Round: 41\r\n…")` → `None`. `$` in MULTILINE mode stops before `\n`, leaving `\r`. `dispatch_findings` returns `[]` at `if not m` → DISPATCH-BEFORE-FREEZE never runs for any CRLF prereg; exit code and SUMMARY say clean. (Everything else in a CRLF prereg parses correctly: `splitlines()` handles key lines; scenario `crlf-clean` passes.) The real r41 preregistration has 0 CR bytes, so the landed lane is not hit today.
2. **Non-ASCII dispatch names (strict).** `git log --name-only` quotes such paths (observed output: `".ufo/waves/round-9/\303\251-dispatch.json"`, including the quote characters); `base.endswith("-dispatch.json")` / `.endswith(".ready")` then see a trailing `"`. A dispatch or ready file with any non-ASCII byte in its name or in a parent directory is invisible; tool exits 0.
Candidate fix (not landed): `[ \t\r]*$` in ROUND, `-c core.quotepath=false` (or `-z`) on the dispatch `git log`. With these two edits the audit goes 83/83 strict and the frozen counter still reads 21/21. Names containing tab, `"` or `\` would still be quoted under quotepath=false; `--name-only -z` is the complete fix.
3. **Blank value of a present key (literal tier).** `if f.get("Base")`, `if f.get("Counter")`, `if f.get("Population")`, `if f.get("Control")` skip a key line with an empty value, so `Base:` / `Counter:` / `Population:` / `Control:` with nothing after the colon produce no finding at all. Target/Kill blank is caught (FIELD-EMPTY); the other four are not, and the documented classes (BASE-UNRESOLVED "not a full40 that resolves", *-MISSING "no blob at FREEZE-REV") read literally cover them. Grammar silent on blank values, hence literal tier, not strict.
4. **Ambiguous tier.** `PATH_SHA = ^(\S+)\s+sha256=<lowercase 64 hex>$`: a repo path containing a space, or an uppercase-hex digest, falls to the fallback branch and is reported COUNTER-MISSING/POPULATION-MISSING (space) or COUNTER-DIGEST (uppercase) although the file exists and its digest is right. Grammar text says `<repo path>` and `<64 hex>` without restriction.

## What the frozen counter could not see (why these are hidden)
c2-cases.tsv has fixed LF fixtures, ASCII names, canonical `census/round-41/…` paths and one dispatch file per case, so a tool memorising path strings or commit subjects passes it (R41critic03's finding) and a CRLF/non-ASCII/blank-value defect is outside its population. The hidden audit randomises all of those per run; the tr4 memoriser (fingerprint table keyed to the counter's fixtures) falls to 20/83 and the always-clean stub to 17/83, their passes are scenarios whose correct answer is clean (tr4 also passes 4 refusals that fall out of its rev/prereg existence checks).

## Limits of this audit
- Oracle expectation for the literal and ambig tiers is my reading of the docstring, flagged as such; only strict-tier results are claimed as defects of the tool against its documented grammar.
- Not covered: pathspec edge cases beyond `[`/`*` in the prereg path (ambig scenario passes), duplicate key lines, `Round:` lines with trailing text, BOM-prefixed preregs, very large histories, concurrent writers.
- `rev` given as a branch/tag name is documented as refused (FULL40) and was only tested with abbreviated and unknown 40-hex ids.
- Tools installed: none.
