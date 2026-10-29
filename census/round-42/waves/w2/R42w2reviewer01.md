# R42w2reviewer01 — re-measure C1 and fact-check the round-42 lesson's Gate and Corrections

Seat: R42w2reviewer01 (wave 2, role reviewer, judged on calibration). Lane tip read: `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (the lane's HEAD; `git status --porcelain` empty at read time). Base: `bf618f6c5c09d302994871c94903abbea2deb60d`.
Receipts (committed-in-seat, citable): `.ufo/waves/round-42/w2/R42w2reviewer01/receipts/`, probes `.ufo/waves/round-42/w2/R42w2reviewer01/probe/`. Scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer01` removed before yield. No git or jj mutation; nothing written outside the seat directory; no tools installed or upgraded.

## Verdict

- **C1 target reproduces at the tip.** `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, exit 0.
- **The tip differs from `c1-after.txt` (measured at `34e33a6`) only by bookkeeping appends.** The SCORECARD appended 26 lines and no base line changed; the 70 declared-evidence mismatches are the identical set. The 16 new SCORECARD assertions all resolve.
- **Most Gate and Corrections values reproduce.** The five CORRECTION-DE derived values, the line 14/92 digest provenance, the S259 quote and live bytes, the SOURCES 182→183 and W04 52 figures, and the rejection-ground numbers all check out.
- **Not reproduced or overstated (details in the table):**
  1. The SCORECARD:697 sentence lists **six** receipts, not five; three mismatch, and the lesson's "the other two … were not checked" is contradicted by three headers I read that match.
  2. The "three of nine planned items done as written" count does not follow from the lesson's own bullets (they name five landed sub-items).
  3. The fixture digest `42259756` is the r24 fixture at `1efe406`; the fixture has changed since (base digest `65d2d681`), which the lesson does not say.
  4. The "26 prunable registrations" phrase is not in the staged entry (it reads "26 registrations across 10 lane repos").
  5. The live fleet now shows 30 registrations across 29 repos (prunable still 0), not the 27/26 the lesson cites; the lesson cites a dated census, so this is a recency note, not a falsification of the cited figure.
- **Out-of-scope observation on C3 (not a Gate/Corrections claim):** the C3 counter at the same tip gave `old_killed=1` on one run and `old_killed=0` on two others. This is the N-C3b timing limit the lesson already names; the first run's exit was lost to a pipe, and the summary line is quoted verbatim below.

## Commands run (exact) and observed output

C1 at the tip (`receipts/c1-tip.txt`):
```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch /fast/scratch/hyaku/souji-r42/R42w2reviewer01
SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0
EXIT=0
```

Declared-evidence instrument (`receipts/declared-evidence-counts.txt`; exit 1 is the instrument's mismatch exit, not an error):
```
$ python3 -B tools/souji-declared-evidence.py --root <lane> --rev bf618f6c5c09d302994871c94903abbea2deb60d --file SCORECARD.md --format counts
assertions=474 resolved=404 skipped=780 mismatches=70
$ ... --rev 34e33a662cd0d6931e5aa006bd90364e7852c0d5 ...
assertions=474 resolved=404 skipped=780 mismatches=70
$ ... --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 ...
assertions=490 resolved=420 skipped=810 mismatches=70
```
(My first base attempt used a mistyped base hash and returned `revision does not resolve`; the correct base spelling was then run and is the row above.)

Tip-versus-receipt diff (`git diff --stat 34e33a6 3105a63`): `LOG.md +12`, `SCORECARD.md +26`, `census/round-42/records/c1-after.txt +4`, `corpus/lessons/round-42.md` one line (N-adj wording). `git diff bf618f6..3105a63 -- SCORECARD.md | grep -c '^-[^-]'` = 0 (pure append). Mismatch sets compared by (line, token, class): base 70 and tip 70, identical. The c1-after receipt header says it was measured before the SCORECARD/LOG rows were appended.

Register/population: `c1-register.tsv` has 71 lines (header + 70); `awk -F'\t'` class counts: `65 resolved`, `5 unresolved`. Items at lines 14, 68 (×2), 92, 175 are the five unresolved rows (`c1-items.tsv`).

Probes of the lesson's junk leg (`receipts/c1-lesson-probes.txt`, each a copy of the tip lesson with one line appended, scored through `score-candidate.sh c1`):
```
base-lesson  junk=0
dup          junk=1   (second CORRECTION-DE line=14)
fenced       junk=1   (CORRECTION-DE inside a code fence)
retract      junk=0   (prose: "The correction recorded above for line 14 is withdrawn …")
malformed    junk=1   (rev=deadbeef)
prose-marker junk=1   (prose line containing the marker)
```

Freeze check (`receipts/freeze-check-prereg.txt`, `freeze-check-selftest.txt`): `SUMMARY claims=3 findings=0` (exit 0) on `census/round-42/preregistration.txt` at `afe17f4`; `SELFTEST cases=31 pass=31 fail=0` (exit 0).

Landing gate, both modes at the tip (`receipts/gate-tip-both-modes.txt`): `findings=0` plain and with `--fleet-root`, both exit 0. R1 counter (`receipts/r1-tip.txt`): `SUMMARY findings=0 deleted=2 rows_added=0 stale=0`, exit 1 (red by its letter, as the lesson says).

S259 (`receipts/s259-live-sha256.txt`): `curl -sS -o live-site.html -w %{http_code} https://docs.python.org/3/library/site.html` → `http_code=200`; `sha256sum` `620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a`, identical to `census/round-42/sources/SHA256SUMS`. Title: `site — Site-specific configuration hook — Python 3.15.2 documentation`.

Interpreter-flag probe (sitecustomize on PYTHONPATH, host `Python 3.14.8`):
```
python3 -B            SITECUSTOMIZE_RAN
python3 -B -s         SITECUSTOMIZE_RAN
python3 -B -P         SITECUSTOMIZE_RAN
python3 -B -I         (no import)
python3 -B -E         (no import)
python3 -B -S         (no import)
```

Fleet prune, read-only (`git worktree list --porcelain` and `git worktree prune --dry-run -v` per repo; `receipts/fleet-live-prune-dryrun.txt`): 29 repos, 30 registrations, `prunable=0` in every repo.

Sources census (read-only validate): `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0; `W04` lines 52; `grep -c '^| S[0-9]' corpus/SOURCES.md` = 183. `git diff bf618f6..3105a63 -- corpus/SOURCES.md` adds only the `S259` row.

C3 counter at the tip (out of scope, observed):
```
run 1 (pipe to tail, exit not captured):  SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=1 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
run 2 (receipts/c3-tip-run2.txt, TRUE_EXIT=0): SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
```
Run 1 is in-session output only (not a file receipt); the target requires `old_killed=0`.

## Statement table

Legend: R = reproduced; NR = not reproduced; P = partly; U = unverifiable by me.

| # | statement (lesson / artifact) | command or source | reproduced? |
|---|---|---|---|
| 1 | C1 target `items=70 … new_mismatches=0` at the tip | C1 counter, `receipts/c1-tip.txt` | R |
| 2 | `c1-after.txt` value at `34e33a6` | `census/round-42/records/c1-after.txt` (same SUMMARY line) | R |
| 3 | Tip differs from `34e33a6` only by bookkeeping | `git diff --stat 34e33a6 3105a63` (LOG, SCORECARD +26, c1-after +4, lesson 1 line) | R (the lesson's "tip differs" framing is not stated in it; the diff is the answer) |
| 4 | Declared-evidence base `474/404/780/70` | declared-evidence `--rev bf618f6…` | R |
| 5 | Declared-evidence tip has 16 more assertions, all resolved, 70 mismatches unchanged | declared-evidence `--rev 3105a63…` → `490/420/810/70`; base vs tip mismatch sets identical | R |
| 6 | Base SCORECARD has 839 lines | `git show bf618f6…:SCORECARD.md \| wc -l` | R |
| 7 | 65 items resolve, 5 unresolved | register `awk` class count | R |
| 8 | Five unresolved items are lines 14, 68 (×2), 92, 175 | `c1-items.tsv` and register rows | R |
| 9 | R42scribe01–05 each read 13 rows, 65 agree, 0 disagree | `waves/w1/R42scribe0{1..5}.md` (`agree=13 disagree=0 cannot-tell=0`) | R (read from reports, not re-run) |
| 10 | R42reviewer01 re-derived all 70, 0 register disagreements | `waves/w1/R42reviewer01.md:25,94,101`; the counter's `class_ok=70` re-derives the same | P (seat claim read, not independently re-run; counter agrees) |
| 11 | CORRECTION-DE line=14 `derived=rev-unresolved` | counter `corrected=5 junk=0`; `git cat-file -e 65817d0d^{commit}` → `fatal`, rc 128 | R |
| 12 | 65817d0d = first 8 hex of sha256 of a `tools/souji-declared-evidence.py` blob; full `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` | `git log --all -- tools/souji-declared-evidence.py` + `sha256sum` per blob: matches `4a6ee90a` and `eb2b393d` | R |
| 13 | "The SCORECARD cell was not wrong about the tool" | base line 14 reads `tool_sha256 65817d0d…, rev 9301d98c…` (cell text reproduced; "not wrong" is interpretation) | P (the cell text is confirmed; the judgement is the lesson's) |
| 14 | CORRECTION-DE line=68 token `42259756…` `derived=sha256=bb506469…` | counter `corrected=5`; `sha256sum` of base tool = `bb506469be860f99…` | R |
| 15 | `42259756…` = sha256 of `tests/fixtures/r24-coverage-agreement.py` at `1efe406` | `git show 1efe406…:tests/fixtures/r24-coverage-agreement.py \| sha256sum` = `42259756a06538a5…` | R |
| 16 | "The cell text was true when written" (fixture digest) — implies the fixture is otherwise current | fixture at **base** sha256 = `65d2d681813f5c09…`, not `42259756` | NR (the fixture changed after `1efe406`; the cell's fixture digest is also stale at base and the lesson does not say so) |
| 17 | CORRECTION-DE line=68 token `71b89eb3…` = sha256 of tool at `1efe406` | `git show 1efe406…:tools/souji-coverage-agreement.py \| sha256sum` = `71b89eb3c7ce4179…` | R |
| 18 | First `bb506469…` revision is `604cd441` | `git log --reverse -- tools/souji-coverage-agreement.py` + per-blob sha: `604cd441` is the first with `bb506469` | R |
| 19 | CORRECTION-DE line=92 `09bb8e0d` `derived=rev-unresolved` | counter; `git cat-file -t 09bb8e0d` → `fatal` | R |
| 20 | `09bb8e0d` = sha256 prefix of `tools/souji-size-census.py` at `778747eb`, full `09bb8e0d9906b0df…` | `git show 778747eb…:tools/souji-size-census.py \| sha256sum` = `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` | R |
| 21 | "fleet pickaxe finds no commit" for `09bb8e0d` | `git -C /home/vgpnk/Projects/shokunin log --all --oneline -S 09bb8e0d` → empty. (The lane's own pickaxe finds `34e33a6`, `6ad4d67`, `7407f09`, which are round-42 commits quoting the token; not a revision.) | R (fleet root); the lane-level hits are unmentioned by the lesson |
| 22 | Current worktree tool hashes differently; "tool changed after r24" | base `tools/souji-size-census.py` sha `c5690681…`; `git log` commits `1efe406`, `778747e`, `315422b` (2026-10-25 06:58 > 778747e 06:33) | R |
| 23 | CORRECTION-DE line=175 `c2-after.tsv` `derived=path-absent` | counter; `git ls-tree -r --name-only bf618…` | R |
| 24 | `c2-after.tsv` matches five committed paths `census/round-24..28/records/c2-after.tsv` | `git ls-tree` grep (five paths) | R |
| 25 | Nearest "Round N" heading above line 175 is Round 23; the Capabilities table is under it | base SCORECARD heading scan: `97: ### Round 23 measurements`, `143: ## Capabilities` | R |
| 26 | Heading-context rule selects no path, so the value is `path-absent` | counter output `unresolved` for line 175 (the rule itself read in `c1-counter.py` `derive()`) | R |
| 27 | Scoped prose for lines 14, 68, 92, 175 (the cell means which artifact) | base lines 14, 68, 92, 175 read | R (interpretation; the artifacts named exist) |
| 28 | SCORECARD:697 sentence: `78ea25a9…` is a commit | `git cat-file -t 78ea25a9…` → commit | R |
| 29 | Receipt headers: `c2-after4.txt` and `c3-after3.txt` say `6949319e`; `a7-counter-fixes.txt` says `9b443200` | `git show bf618f6…:census/round-38/records/<f> \| head -1` | R |
| 30 | "three of the five receipts that sentence lists" | the sentence lists **six**: `c1-after5`, `c1-vacuity4`, `c2-after4`, `c3-after3`, `consumers-after4`, `a7-counter-fixes`; three mismatch | NR (count is six, not five) |
| 31 | "The other two receipts of the list were not checked this round" | headers of `c1-after5`, `c1-vacuity4`, `consumers-after4` read `78ea25a9…` (match); I read them now | NR (they were checkable and match) |
| 32 | "The numbers in those receipts match their cells" | `c2-after4` SUMMARY = cell (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3`); `c3-after3` = cell (`cases=10 pass=10 fail=0`, `mutants=4 killed=4 survived=0`); `a7` numbers not checked | P |
| 33 | SCORECARD:839 quoted filed text | `git show bf618…:SCORECARD.md \| sed -n 839p` contains `r42: calibration: a counter that reads correction prose and rejects fenced, duplicate and retracting lines (N1-N4)` (markdown bold stripped in the quote) | R |
| 34 | "no counter in r42 reads correction prose" (what the lesson means by "no counter reads prose meaning") | probe `retract` → `junk=0`; the C1 junk leg reads only lines containing `CORRECTION-DE` | R |
| 35 | "Three planned items out of nine were done as written" | lesson's own bullets name landed sub-items: N13 dup keys, heading malformed, dispatch names (3); N14 condition mutants, M40-12 (2) = 5 named as landed; calibration not done; hidden-case audit not frozen; R39-D1/D2 and N10 not done | NR (the count does not follow from the bullets; granularity is not stated) |
| 36 | S259 URL live bytes equal the snapshot | `curl` 200, `sha256sum` `620581fe…` | R |
| 37 | S259 title "Python 3.15.2 documentation" | live `<title>` | R |
| 38 | Quote "an attempt is made to import a module named sitecustomize, which can perform arbitrary site-specific customizations" at snapshot lines 418–419 | `sed -n 417,420p` on snapshot; live text (tags stripped, whitespace normalised) contains the quote | R |
| 39 | `-S` suppression sentence at snapshot lines 227–228 | `sed -n 226,229p`: `automatically imported … The automatic import can be suppressed using the interpreter's -S option` (line 227 start, 228 end) | R |
| 40 | `-I` effect "not stated on this page" | live page `grep -c -- "-I"` = 0 and no "isolated mode" | R |
| 41 | Host Python 3.14.8 | `python3 -V` | R |
| 42 | sitecustomize reaches `-B`, `-s`, `-P`; does not reach `-I`, `-E`, `-S` children (Q105 caveat) | flag probe above | R |
| 43 | Snapshot sha256 in SHA256SUMS matches | `sha256sum census/round-42/sources/python-3-library-site.html` | R |
| 44 | S259 row fields: tier A, mined, recheck on-release, used-by the lesson | `corpus/SOURCES.md` row 213 | R |
| 45 | Registry 182 → 183 rows; start census `rows=182`, `W04=52` | `records/census-before.txt`; table row count 183 | R |
| 46 | Census validate exit 0 and W04 = 52 at the end | `scripts/sources-census.sh validate … souji` exit 0; `W04` lines 52 | R |
| 47 | No older SOURCES row changed | `git diff bf618f6..3105a63 -- corpus/SOURCES.md` adds only S259 | R |
| 48 | R42scribe06 and R42sentinel02 re-opened the live page at `620581fe…` | `waves/w1/R42scribe06.md:19-25`, `waves/w1/R42sentinel02.md:53` | R (read from reports; my own live fetch matches) |
| 49 | Rejection ground: staged entry `fleet-prune-safety-r28.md` says "26 prunable registrations", run 2026-10-24 | staged file at `shokuknow/merge/souji/knowledge/corpus/knowledge/fleet-prune-safety-r28.md` (sha `d8b71cf4…`): "26 registrations across 10 lane repos", run 2026-10-24; literal "26 prunable" count = 0 | P (the figure reproduces; the quoted phrase is the lesson's paraphrase, not a verbatim quote) |
| 50 | Staged conclusion "every prunable registration is safe to prune" | staged title, case-insensitive grep = 1 | R |
| 51 | Lane entry `fleet-prune-numerator-r35.md`: "27 registrations across 26 repositories, 0 prunable" from the 2026-10-28 census | `corpus/knowledge/fleet-prune-numerator-r35.md`; `records/prune-census.tsv` `TOTAL repos=26 regs=27 prunable=0`; file sha `8b37041a…` matches the entry | R (as a dated record) |
| 52 | The population is "empty" (0 prunable) | live dry-run, 29 repos: `prunable=0` everywhere | R for prunable; the live registrations differ (30 in 29 repos vs 27 in 26) — recency note, not a falsification of the cited dated figure |
| 53 | "worktree.c appears in 9 rows" was falsified (I1) | `git show bffcc0f…:corpus/SOURCES.md \| grep -cF worktree.c` → 3 lines, 2 of them registry table rows (S009, S033); the third is a note line | R |
| 54 | Registry had 181 rows at `bffcc0f`; 0 rows cite `v2.56.0/worktree.c` | `grep -c '^| S[0-9]'` = 181; `grep -F v2.56.0/worktree.c` = 0 | R |
| 55 | `considerthese/` does not exist in the lane | `ls -d considerthese` → not found | R |
| 56 | R1 repoint and both-mode gate `findings=0` (named in the Corrections context) | `receipts/gate-tip-both-modes.txt` | R |

## Notes for the L1

- Items 16, 30, 31, 35 and 49 are the lesson-text fixes that a reader would act on. Items 30/31 are the most material (a receipt count and a "not checked" claim the artifacts contradict). These are append-only lesson corrections, not edits to any frozen file.
- The C1 counter cannot see any of items 16, 30, 31, 35 or 49: they are prose, and the frozen counter reads only `CORRECTION-DE` lines and the register. This matches the lesson's own named limit N-C1a (shape vs substance).
- The C3 nondeterminism (run 1 `old_killed=1`) is a fact about the frozen counter at this tip, reported for N-C3b; I did not edit or re-score anything.
