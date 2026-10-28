# R41w2executor02 — differential audit of six C2 candidates (R41executor07..12)

Lane tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f; landed tool `tools/souji-freeze-check.py` is byte-identical to
`w1/R41executor07/souji-freeze-check.py` (`cmp` printed `same`).

## Verdict
**Landed 07 has one real defect (D1, fail-open on CRLF/CR `Round:` line); everything else is stylistic or shared.**
Claim C2 (the counter) still passes 21/21; the defect lies outside the counter's 21 cases (none uses CRLF).
Not a harm to the counter, but it is a hidden-case failure of the tool's operability: a CRLF-saved prereg silently
skips the DISPATCH-BEFORE-FREEZE check and reports clean (exit 0).

## Evidence pointers (all under `.ufo/waves/round-41/w2/R41w2executor02/`)
- `diff-audit.py` — 121-scenario battery (random names, CRLF, spaces, Round missing, merged-branch freeze, same-commit dispatch, ...), runs all six candidates, compares (exit, finding-class multiset, crash).
- `battery-6-candidates.txt` — full output; `raw-6-candidates.json` — per-tool stdout/stderr per scenario (scratch path replaced by SCRATCH).
- `battery-landed-vs-patched.txt` — same battery, landed vs my one-line patch (`souji-freeze-check.patched.py`).

## Commands actually run
```
cd /fast/scratch/hyaku/souji-r41/R41w2executor02 && TMPDIR=$PWD python3 -B .../w2/R41w2executor02/diff-audit.py $PWD/run2
  -> TOTAL scenarios=121 disagree=22   (first run, 104 scenarios + 1 build-fail: disagree=16; 17 scenarios added in run 2)
python3 -B .../R41executor{07,08,11}/souji-freeze-check.py --root $D --prereg prereg-{lf,crlf}.txt --rev $H   (hand repro, below)
bash census/round-41/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=<patched>
  -> SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=01d27f05a69f
python3 -B census/round-41/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch <scratch>
  -> SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
battery with TOOLS={landed, patched}  -> TOTAL scenarios=121 disagree=4  (exactly the 4 D1 scenarios, nothing else changed)
```

## Where 07 is the odd one out

### D1 (defect, real): `Round:` line with CR defeats the dispatch check — 07 alone reports clean
Cause: `ROUND = re.compile(r"^Round:[ \t]*(\d+)[ \t]*$", re.M)`; `$` in re.M matches only before `\n`, so `Round: 41\r\n`
and a bare-CR file never match, `dispatch_findings` returns `[]`. Claim parsing uses `splitlines()` so the rest of the
prereg is read correctly: the tool says `claims=N findings=0` — silently wrong, not refused.
Scenarios (07 rc=0 `[]`; 08,09,10,11,12 rc=1 `C0 DISPATCH-BEFORE-FREEZE`): `s99_round_crlf_dispatch_before`, `s113_round_crlf_only_no_dispatch` (same-commit dispatch), `s115_mixed_crlf_round_line_only` (only the Round line has CR). `s114_round_bare_cr_line`: 07 and 08 miss, 11 finds (09,10,12 say NO-CLAIMS).
Minimal repro (transcript):
```
D: base commit; commit 2 adds .ufo/waves/round-41/w1-dispatch.json; commit 3 ("freeze") adds census files + prereg
prereg-lf.txt   (Round: 41\n ...)  07 -> FINDING C0 DISPATCH-BEFORE-FREEZE ... ; SUMMARY claims=1 findings=1 ; exit=1
prereg-crlf.txt (Round: 41\r\n ..) 07 -> SUMMARY claims=1 findings=0 ; exit=0     08, 11 -> FINDING C0 DISPATCH-BEFORE-FREEZE, exit=1
```
Fix (tested, `souji-freeze-check.patched.py`, one line): `m = ROUND.search(text.replace("\r\n", "\n").replace("\r", "\n"))`.
C2 counter still 21/21 with it; 121-scenario battery differs from landed only on the four D1 scenarios.
Hole in the counter: c2-counter.py has no CRLF case, so the mutation "ROUND regex without `\r`" passes the counter.

### Minor 07-vs-others (not defects; fail-closed or grammar-ambiguous)
- `s61_counter_sha_upper`: 07,10 flag COUNTER-DIGEST for an uppercase-hex digest, 08,11,12 accept, 09 FIELD-MISSING. 07's detail text ("has no sha256=<64 hex>") is misleading since the hex is 64 long (grammar says lowercase regex only).
- `s64_counter_extra_tokens` (`... sha256=<hex> (frozen)`): 07,10 COUNTER-DIGEST, 08,11 accept, 09,12 FIELD-MISSING.
- `s07_space_in_paths`: 07 reports COUNTER-MISSING for `census dir/my counter.py` (uses first token); 09,12 FIELD-MISSING. Paths with spaces are outside the grammar; 07's message names the wrong path.
- `s100_round_text_not_number` (`Round: 41 (r41)`): 08 only flags; 07 ignores Round line. Grammar says digits only.
- `s107_unicode_linesep_in_value`: 07 and 08 use `str.splitlines()` so U+2028 inside a value starts a phantom line (`\x0c## C9` → phantom claim C9 with 5 FIELD-MISSING); 09-12 use `split("\n")`. Fail-closed false positive, exotic.
- `s34_prereg_dotslash`, `s58_base_tag_annotated`, `s45_key_nospace`, `s72_counter_dotslash`, `s77_pop_cr_only_lines`, `s85_control_with_comment_tokens`, `s69_counter_path_traversal`, `s37_prereg_latin1`, `s105_shallow_clone_rev`: 07 agrees with the majority; the odd ones are 08 (refuses `./prereg.txt`, false BASE-NOT-ANCESTOR on annotated-tag Base, **crashes with BrokenPipeError traceback on `../etc/passwd` counter path**), 09 (no-space key, `./` path, CR-only lines, control comment), 12 (refuses latin-1 prereg and shallow clone with rc=2 — arguably correct for shallow).
- `s120_population_utf8_nbsp_only_line`: 07,10,11,12 POPULATION-EMPTY; 08,09 count NBSP as an item.
- `s39_header_variants`: 10,11 additionally report the first claim from the `## C1a` interleave; 07,08,09,12 agree.

## Shared blind spots (all six agree; not 07-specific, candidate gaps vs the "freeze before data" rule)
- `s23_prereg_edited_after_freeze`: a claim added to the prereg after freeze → clean (prereg's own post-freeze edits are never compared with freeze). `s86_control_edited_after_freeze`: control blob changed to `EXIT=0` after freeze → clean (only Counter/Population get FROZEN-EDITED). Both consistent with the documented class list.
- `s49_duplicate_key_second_bad`: duplicate `Base:` — first wins, second (unresolvable) ignored silently.
- `s97_round_leading_zero` (`Round: 041`): looks for `round-041/`, so a real `round-41` dispatch is not found; clean.
- `s111_freeze_is_merge_commit_adding_prereg`: prereg first added by a merge commit itself → all six refuse (rc=2, "no commit adds"), because `git log --diff-filter=A` shows no diff for merges. Safe (refusal), but the merged-branch case where the merge adds the prereg is unevaluable.
- Merged-branch cases that behave sensibly in all six: `s17`,`s18`,`s19`,`s20`,`s109`,`s110` (dispatch only flagged when it is an ancestor of freeze), `s112`.

## Agreement summary
121 scenarios, 99 unanimous, 22 disagreements (list in `battery-6-candidates.txt`). Same-commit dispatch (`s12`,`s13`), dispatch-before-freeze (`s11`,`s16`,`s94`,`s96`,`s98`), Round missing (`s09`,`s10`), CRLF prereg without dispatch (`s03`,`s06`), random names (`s02`,`s116`), clean cases: unanimous and correct.
Tooling installed: none. Scratch `/fast/scratch/hyaku/souji-r41/R41w2executor02` deleted after receipts were copied.
