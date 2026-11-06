# S70Scribe — r70 lesson draft material (seat report)

Read at lane tip `20c117ce160db5c5fc2b88663404b161a8b3c68a` (two commits past the `feb283ee` the
assignment names: `9167e02d` r70 lesson + `tools/souji-pointer-check.py`, `20c117ce` pointer-check
`:line` strip + regenerated r69 receipt + M1 wording). No tool installed. Draft:
`.ufo/waves/round-70/w1/S70Scribe/draft.md`.

Routed-item verdicts (full table with evidence in draft.md §1):
- D1 **closed** (`0d8ce29a`; mirror 71 files, 66/66 live files present, per-file sha256 diffs=0).
- D2 **closed** (mirror carries `…/S69MutTester.logs/selftest-orig.txt` → `SELFTEST cases=16 pass=16 fail=0`, `EXIT=0`).
- D3 **closed** (`SKILL.md:916`; same grep over `e063a2fc:SKILL.md` = 0).
- D4 **partial** (`SCORECARD.md:253` now says "6 differing … lines"; my re-measure = 6 diff markers = 3 changed lines).
- D5 **open** (`grep -c 'XDG\|HOME=\|GIT_TRACE' census/round-69/records/c2-ambient.txt` = 0).
- D6 **pending** (wave in flight; `.ufo/waves/round-70/w1/` holds only `S70Connector/` + registry; `git ls-files .ufo/waves/round-70/` empty).
- (a) **closed** (`PATHSPEC_ENV` 4 vars + `git()` filter; writer case 38; rows `LA…ICD`; `clean_env` drops `PATHSPEC_VARS`). (b) **partial** (`c1-counter.py:394` scrubs template/attr/exec-path/hash; `GIT_QUARANTINE` grep = 0). (c) **closed** (CM1–CM4 `fate=killed`). (d) **open** (`grep -rn D06 census/round-70/` = 0). (e) **closed as rows** (`c1-counter.py:278` `LN4 subdirectory-root-scope-literal-pathspecs` + literal flag/gitlink/absent/unmerged rows; no D29 label). (f) **open** (pointer-check is paths only). (g) **open** (`grep verify` in writer = 0). (h) **open** (`battery_verdict` `:1125-1136` gates obs/survived/error only; `regress=` is printed at `:1535`).
- Sentinel: F-1 **closed** (`:394`); F-2 **closed by scrub, unmeasured**; F-3 **closed** (`verify_members`, `sha256=` per MUTANT, `TAMPER T1 … fate=detected`); F-4 **open** (MUTANT fields are new-slot only); F-5 **open** (`write_receipt` `open(path,"w")`, `:1219`); `command=` absolute paths **open** (`--root .`); S69Scribe D18 artifact **open** (`:395` still pins `GIT_OPTIONAL_LOCKS=0`).

Missing paths (task 4, `git cat-file -e 20c117ce:<path>`), both resolutions tried:
- Dead: `probe/full-battery-out.txt` (r69 lesson M2 cell; prereg `:40`,`:125`), `probe/fsm` (prereg `:38`), `probe/c2-ambient` (prereg `:41`,`:92`) — rc 128 each; `records/c1-candidate.txt` rc 128 at both, but cited only as M7's discarded wrong name.
- Not dead, root-unresolvable shorthand (OK under `census/round-69/`): `controls/d18-limit-battery.txt`, `probes/{battery-probe-27-prefix,c2-ambient,c2-before-r68-clean,c2-before-r68-ambient}.txt`, `records/{c1-after-battery.txt,declared-coverage.tsv}`.

Two draft Mistakes rows (draft.md §2, M4/M5): dead receipt `records/census-after.txt` cited at `corpus/lessons/round-70.md:53` (rc 128, invisible to the new checker because `tools/souji-pointer-check.py:65-68` drops `records/` tokens outside `census/round-*`); untracked `census/round-70/records/pointer-check-r70.txt` cited at `round-70.md:28` (`??` at tip, rc 128).

Findings: HIGH — `corpus/lessons/round-70.md:53` cites a receipt that exists in no commit, and the round's new pointer check cannot see it (`checked=14 missing=1`, the miss being only the untracked file). MEDIUM — `census/round-70/records/pointer-check-r70.txt` is untracked at the tip while `round-70.md:28` cites it as `missing=0` evidence; the tree is dirty (`M SCORECARD.md`) so a writer receipt would refuse. MEDIUM — D4's number is still the two-sided marker count (6, not 3 changed lines) at `SCORECARD.md:253`. LOW — D5, (d), (f), (g), (h), F-4, F-5, absolute `command=`, D18 pin still open. LOW — `corpus/knowledge/pathspec-env-scrub.md` says `:(top)` under literal "matches the literal path `:(top)`"; the committed probe (`probes/lp-ls-files-probe.txt`: `ls-files-out=[] rc=0`) supports "compared as a literal pathname, matches nothing".

Reproduced numbers (mine, not taken from the L1): `c1-after.txt` 59 `CASE`, 15 `new=accept`/44 `new=refuse`; `c2-after.txt` `killed=4 survived=0 tamper=detected score=0`; writer `CASES` = 38; `corpus/SOURCES.md` 226 at `e063a2fc` → 228 at HEAD. No counter/harness run was performed by this seat (read-only receipts and tools only); no lane tracked file touched.

Files written: `.ufo/waves/round-70/w1/S70Scribe/draft.md`, `.ufo/waves/round-70/w1/S70Scribe.md`.
