# R41w2reviewer05 — audit of corpus/lessons/round-41.md (CORRECTION I1/I3/I4, Gate)

Seat: R41w2reviewer05 (reviewer, wave 2, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Tip: `1d41c13574db80fdd9a4bde490b712da7ce2a85f`. Lesson bytes: `git show 31e4d3e:corpus/lessons/round-41.md` (= working tree; `git diff HEAD` empty).
Measured-at revision of the CORRECTION lines: `bffcc0f660ff36eb8add3f61582748a7af019a5b` (round-40 bytes).
No file was written outside this report and the seat scratch dir `/fast/scratch/hyaku/souji-r41/R41w2reviewer05/` (deleted before yield). No git mutation. No tool installed or upgraded.

## Verdict

- **Numbers reproduce:** I1 `181 rows / 2 rows / v2.56.0=0`, I3 `register_cells 6 and 3`, I4 `136 files / 0 occurrences`, the S258 quote, line numbers 229/255/259, 1541 lines, both sha256 values, and the 171-266 diff (single hunk at 229) all reproduce from committed bytes.
- **Quoted LOG.md text reproduces** (`LOG.md:1909`, exact substrings).
- **S033 reading reproduces** (cell text exact; S033 is a docs row, not a source citation).
- **Spot-check "counted 1" reproduces** under the stated method (rows citing the file as a source = S009 only).
- **Staged item:** the round-40 rejection quote reproduces verbatim; the staged S160 package is not in any lane commit, so its content is not verifiable from lane bytes (absence only).
- **Three sentences do not reproduce as written** (flags F1–F3 below). Each is a location or attribution error, not a numeric error. Calibration: the figures are right, but two named locations are wrong and one path is ambiguous.

## Flags

- **F1 (I3, attribution — does not reproduce as written).** The lesson says "`SCORECARD.md` round-40 C1 row presents `c1-before.txt` and `c1-after-h.txt` as one before→after." At bffcc0f the row that presents `c1-before.txt` as its before arm is `SCORECARD.md:791` ("C1 evidence-bound closures + strict-descendant register"); its after arm is `c1-after-d.txt`, not `c1-after-h.txt`. `c1-after-h.txt` appears only at `SCORECARD.md:801` (a different row, the fixture counter) and `:811` (narrative). The frozen counter also hard-codes `c1-after-h.txt` (`census/round-41/c1-counter.py:81`). The substance survives: `c1-after-d.txt` also reads `register_cells=3` with `--register census/round-40/cells.tsv`, so the arms still ran over different register files. Correction needed: name `c1-after-d.txt` (SCORECARD:791) and `c1-after-h.txt` (final instrument, SCORECARD:811), or reword.
- **F2 (Gate, S009 note — location wrong).** The Gate says S009 "whose own note says the v2.56.0 recheck is pending." The S009 registry row has no such text: its `recheck` cell is `on-release`, and no `pending`/`v2.56` appears in the row. The note exists in S009's `used-by` file `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:27` ("Treat it as pending recheck (routed to r17)"), which refers to Git 2.56.0. The phrase "pending-recheck note for v2.56.0" that the spot-check quotes at `7eebc18:corpus/lessons/round-40-verifier-spotcheck.md:57` is from the staged S160 package, not from S009. Substance reproduces; the attribution should say "the used-by knowledge file".
- **F3 (I4, path ambiguity).** The lesson cites "the fleet report `.ufo/reports/round-40/souji.md:79`". That path is absent from the lane at bffcc0f (`git show bffcc0f:.ufo/reports/round-40/souji.md` returns "does not exist"). It exists only at the fleet root `/home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md`, where line 79 carries "R40w2reviewer01 and R40w2reviewer04 died with `Codex error event: Invalid prompt: …`". The sentence should say "fleet-root". Content reproduces.

Non-blocking notes (not in the three CORRECTION blocks or Gate, recorded for the calibration reader):
- **N-a (I1 method fragility).** `v2\.56\.0/worktree\.c` is a literal substring. S258 at tip cites `v2.56.0/builtin/worktree.c`, so the same command returns 0 at tip (`grep -c 'v2\.56\.0/worktree\.c'` on tip = 0) although S258 is a v2.56.0 source row. The derived 0 at bffcc0f is correct; the method would miss a v2.56.0 source row added later.
- **N-b (spot-check parenthetical).** `7eebc18:corpus/lessons/round-40-verifier-spotcheck.md:57` says the whole-file grep matches "S033/S058/S232 … as worktrees pages". At bffcc0f S058 and S232 do not contain `worktree.c`; the three matching lines are S009 (`SOURCES.md:38`), S033 (`:62`) and a prose line at `:240`. The spot-check's conclusion (one citing row) stands; its parenthetical is wrong.
- **N-c (counter scope).** `census/round-41/c1-counter.py` derives at the constant `MEASURED = bffcc0f…` (line 46) and does not re-derive at `--rev`. A run at tip therefore re-checks the CORRECTION lines but not the tip's own registry.

## Commands run and output

All `git show`/`git grep` calls are read-only; all run from the lane.

### Sentence-by-sentence

| # | Sentence (lesson line) | Command | Result | Status |
|---|---|---|---|---|
| S1 | "At bffcc0f the registry has 181 rows" (45) | `git show bffcc0f:corpus/SOURCES.md \| grep -E '^\| S[0-9]+ ' \| wc -l` | `181` | PASS |
| S2 | "rows whose text contains the literal `worktree.c` number two (S009, S033)" (46-47) | `… \| grep -E '^\| S[0-9]+ ' \| grep -c 'worktree\.c'` ; `… \| grep -E '^\| S[0-9]+ ' \| grep 'worktree\.c' \| cut -c1-12` | `2` ; `\| S009 \n\| S033` | PASS |
| S3 | "rows whose text contains `v2.56.0/worktree.c` number zero" (47) | `… \| grep -E '^\| S[0-9]+ ' \| grep -c 'v2\.56\.0/worktree\.c'` | `0` | PASS (see N-a) |
| S4 | I1 re-run lines 51-52 (the two commands in the block) | same two commands as S2/S3 | `2`, `0` | PASS |
| S5 | "S009, which cites the file as a v2.55.0 source" (46) | `git show bffcc0f:corpus/SOURCES.md \| grep -E '^\| S009 ' \| awk -F'\|' '{print $3}'` | `git/git source at tag v2.55.0: builtin/gc.c, worktree.c, …` | PASS |
| S6 | "S033, whose cell says 'although worktree.c ages by it'" (46) | `git show bffcc0f:corpus/SOURCES.md \| grep -E '^\| S033 ' \| grep -o 'although worktree\.c ages by it'` | matched exactly | PASS |
| S7 | "The source row for the v2.56.0 file is S258" (55) | `git show 1d41c13:corpus/SOURCES.md \| grep -E '^\| S258 ' \| cut -c1-120` | `\| S258 \| git/git source at tag v2.56.0: builtin/worktree.c — https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c …` | PASS |
| S8 | I1 derived `rows=2,v2.56.0=0` (CORRECTION line, 57) | `python3 -B census/round-41/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin/ --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch /fast/scratch/hyaku/souji-r41/R41w2reviewer05` | `ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes` ; `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` ; `EXIT=0` | PASS (see N-c) |
| S9 | I3 "`c1-before.txt` reports `register_cells=6`" (61) | `git show bffcc0f:census/round-40/records/c1-before.txt \| grep -o 'register_cells=[0-9]*' \| head -1` | `register_cells=6` | PASS |
| S10 | I3 "`c1-after-h.txt` reports `register_cells=3`" (62) | `git show bffcc0f:census/round-40/records/c1-after-h.txt \| grep -o 'register_cells=[0-9]*' \| head -1` | `register_cells=3` | PASS |
| S11 | I3 register files `census/round-39/cells.tsv` and `census/round-40/cells.tsv` (61-62) | `git show bffcc0f:census/round-40/records/c1-before.txt \| head -3` ; `… c1-after-h.txt \| head -3` | before: `--register census/round-39/cells.tsv`, `measured_at 0242085…`; after-h: `--register census/round-40/cells.tsv`, `measured_at dc8bd47…` | PASS |
| S12 | c1-before is "measured at the frozen base" (61) | `git show bffcc0f:corpus/lessons/round-40.md \| sed -n 4p` | `Base revision (frozen in census/round-40/preregistration.txt): 0242085909fb6a4ee041c5443d76316ac6d59d4b` ; c1-before `measured_at` = same hash | PASS |
| S13 | item arm `items=3 open=3` → `open=0` (63-64) | `grep -n 'SUMMARY' ` on both receipts | before `items=3 open=3 …`; after-h `items=3 open=0 …` | PASS |
| S14 | "The register arm … is not like-for-like" / "derivation reads the two receipts' register_cells= values only" (64-65) | `grep -n -E 'c1-before\|c1-after-h\|register_cells' census/round-41/c1-counter.py` | I3 derivation reads only `register_cells=(\d+)` from the two named files (lines 81-85) | PASS |
| S15 | "R41reviewer02 names the register blobs" (65) | `grep -n 'blob' .ufo/waves/round-41/w1/R41reviewer02.md` ; `git rev-parse bffcc0f:census/round-39/cells.tsv bffcc0f:census/round-40/cells.tsv` | reviewer02 lists `6dae3ffb…` and `8e37db34…`; git gives `6dae3ffb0d01c87f7edb7fd9d0d021cf910be7c3`, `8e37db34c0627fde2087554519fd9bcce728c678` | PASS |
| S16 | I3 "the SCORECARD round-40 C1 row presents c1-before.txt and c1-after-h.txt as one before→after" (59-60) | `git show bffcc0f:SCORECARD.md \| sed -n 791p \| awk -F'\|' '{for(i=2;i<=NF;i++) print i": "$i}'`; `grep -n 'c1-after-h' SCORECARD.md` | row 791: before `c1-before.txt`, after `(c1-after-d.txt)`; `c1-after-h` only at lines 801 and 811 | **FAIL — F1** |
| S17 | Substance: register arms ran over different registers (5 of I3) | `git show bffcc0f:census/round-40/records/c1-after-d.txt \| grep -o 'register_cells=[0-9]*'`; header `--register census/round-40/cells.tsv` | `register_cells=3`, register `census/round-40/cells.tsv` | PASS (substance) |
| S18 | I4 "`LOG.md:1909` records two dead seats (`R40w2reviewer01/04`) with the provider error text `Codex error event: Invalid prompt: ...`" (76) | `git show bffcc0f:LOG.md \| sed -n 1909p \| grep -o 'R40w2reviewer01/04.\{0,160\}'` | `… 2 dead seats (R40w2reviewer01/04, provider error \`Codex error event: Invalid prompt: your prompt was flagged as potentially violating our usage policy\`) …` | PASS |
| S19 | "says all wave evidence is captured under `census/round-40/waves/`" (76-77) | `git show bffcc0f:LOG.md \| sed -n 1909p \| grep -o 'All wave evidence[^.]*\.'` | `All wave evidence is captured under \`census/round-40/waves/\`.` | PASS |
| S20 | LOG.md:1909 is in the r40 entry | `git show bffcc0f:LOG.md \| sed -n 1880,1908p \| grep -n '^## '` | headings at 1891 (Round 39) and 1901 (Round 40) | PASS |
| S21 | "`census/round-40/waves/` (136 files at bffcc0f, …)" (78) | `git ls-tree -r --name-only bffcc0f census/round-40/waves/ \| wc -l` | `136` | PASS |
| S22 | "… `w2-results.json` …" exists (78) | `git ls-tree -r --name-only bffcc0f census/round-40/waves/ \| grep w2-results` | `census/round-40/waves/w2-results.json` | PASS |
| S23 | "contain that text zero times" (78) | per-file `grep -c 'flagged as potentially'` summed over the 136 files | `0` (also `Invalid prompt` in waves: `0`) | PASS |
| S24 | "both seats have partial outputs and no error text" (78) | `git show bffcc0f:census/round-40/waves/w2-results.json \| grep -n 'R40w2reviewer0[14]'` ; `… \| grep -n -i error` | seats at lines 8 and 26; first `error` match is line 100 (other seats' output), none in lines 1-99; seat 01 output begins "We need target assignment execution…", seat 04 begins "<think>\nWe found r39 analyzer…" (partial) | PASS |
| S25 | "the lane at bffcc0f has no other carrier" (80) | `git grep -c -F 'Invalid prompt' bffcc0f` ; `git grep -c -F 'Codex error event: Invalid' bffcc0f` ; `git grep -c -F 'flagged as potentially' bffcc0f` | only `LOG.md:1` in each; no other path. Concurs: `.ufo/waves/round-41/w1/R41scout03.md:61` ("Lane @ bffcc0f: only LOG.md:1909 itself") | PASS |
| S26 | "the fleet report `.ufo/reports/round-40/souji.md:79`" carries the text (80) | `git show bffcc0f:.ufo/reports/round-40/souji.md` → does not exist; `sed -n 77,80p /home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md` | lane: absent. fleet root line 79: "- **W2 role mix:** … R40w2reviewer01 and R40w2reviewer04 died with `Codex error event: Invalid prompt: …`" | **FAIL — F3** (path is fleet-root only; content PASS) |
| S27 | I4 derived `occurrences=0` (CORRECTION line 88) | counter command in S8 | `ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes` | PASS |
| G1 | S258 accessed 2026-10-28 (Gate, 17) | `git show 1d41c13:corpus/SOURCES.md \| grep '^\| S258 '` | row text includes "opened 2026-10-28" | PASS |
| G2 | Quote "prune missing working trees older than <time>" located once, line 255 (19-20) | `git show 1d41c13:census/round-41/sources/git-v2.56.0-builtin-worktree.c \| grep -n -F 'prune missing working trees older than <time>'` | `255:  N_("prune missing working trees older than <time>")),` (one match) | PASS |
| G3 | "line 255 (the `N_()` help string of `prune --expire`)" | `… \| sed -n 250,256p` | line 254-255: `OPT_EXPIRY_DATE(0, "expire", &expire, N_("prune missing working trees older than <time>")),` inside `prune()` | PASS |
| G4 | "line 229 reads `if (should_prune_worktree(the_repository, d->d_name, &reason, &path, expire))`" (21) | `… \| sed -n 229p` | exact match | PASS |
| G5 | "line 259 reads `expire = TIME_MAX;`" (21) | `… \| sed -n 259p` | `	expire = TIME_MAX;` | PASS |
| G6 | "the file is 1541 lines" (17) | `… \| wc -l` ; `git ls-tree -l 1d41c13 census/round-41/sources/` ; S258 row "1541 lines" | `1541` | PASS |
| G7 | sha256 `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc` (17) | `git show 1d41c13:…/git-v2.56.0-builtin-worktree.c \| sha256sum` ; `git show 1d41c13:census/round-41/sources/SHA256SUMS` | `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc  -` ; SHA256SUMS line 1 identical | PASS |
| G8 | v2.55.0 sha256 `2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884` (22) | `git show 1d41c13:…/git-v2.55.0-builtin-worktree.c \| sha256sum` ; SHA256SUMS | `2c8e8a8e…e884  -`; matches SHA256SUMS | PASS |
| G9 | v2.55.0 vs v2.56.0 differ in 171-266 only at line 229; v2.56.0 call gains `the_repository` (22-23) | `diff <(… v2.55.0 \| sed -n 171,266p) <(… v2.56.0 \| sed -n 171,266p)` | one hunk `59c59` = file line 229; `should_prune_worktree(d->d_name,…)` → `should_prune_worktree(the_repository, d->d_name,…)` | PASS |
| G10 | "Seat R41scribe04 quoted the v2.56.0 sha256 with two transposed characters (`…c523c1e…` vs observed `…bd523e1c…`)" (24-25) | `grep -n 'af2bd523' .ufo/waves/round-41/w1/R41scribe04.md` ; compare with G7 | scribe04.md:24 `af2bd523c1e89e33…`; observed `af2bd523e1c89e33…`: `e` and `c` swapped at positions 9 and 11 | PASS |
| G11 | "`R41scribe05` quoted correctly" (not claimed; checked for context) | `grep -n 'af2bd523' .ufo/waves/round-41/w1/R41scribe05.md` | lines 10, 45 match the observed hash | context only |
| G12 | Round-40 rejection quote: "the lane already holds git's prune gate (`worktree.c` appears in 9 rows …); adopting it again would be a duplicate" (30-31) | `git show bffcc0f:corpus/lessons/round-40.md \| sed -n 48,50p` | `REJECT — staged entry fleet-prune-safety-r28.md (staged row id S160, git v2.56.0 worktree.c). The lane already holds git's prune gate (worktree.c appears in 9 rows of corpus/SOURCES.md); adopting it again would be a duplicate` | PASS (quote exact) |
| G13 | "staged row S160" / "staged `fleet-prune-safety-r28.md`" stays unadopted (30-35) | `git grep -n '| S160 ' 1d41c13 -- corpus` ; `git grep -n 'fleet-prune-safety' 1d41c13` ; `git log --all -S 'fleet-prune-safety' --oneline` | no S160 row in corpus at tip; the file exists in no lane tree; mentions only in round-31 receipts and round-40 spot-check / lesson; the staged package (`SOURCES.append.md`, outside the lane) is not committed | **UNVERIFIABLE from lane bytes** (absence of adoption PASS; staged content not checkable) |
| G14 | "At bffcc0f two registry rows contain the literal worktree.c (S009, S033), one row cites the file as a source (S009 … whose own note says the v2.56.0 recheck is pending) and no row cites it at v2.56.0" (32-34) | S2/S3/S5 above; `git show bffcc0f:corpus/knowledge/git-auto-maintenance-prunes-worktrees.md \| sed -n 27p` ; `git show bffcc0f:corpus/SOURCES.md \| grep -E '^\| S009 ' \| grep -o -i '.\{0,80\}\(v2\.56\|pending\|recheck\).\{0,80\}'` | counts PASS; S009 row has no "pending"/"v2.56" text (recheck cell = `on-release`); the note is at `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:27`: "Treat it as pending recheck (routed to r17)" | **PARTIAL — F2** (note exists, in the used-by file) |
| G15 | "No package bytes were appended this round" (29) | `git diff --stat 7eebc18 1d41c13 -- corpus/SOURCES.md` ; row counts at 7eebc18 and 1d41c13 | `1 file changed, 4 insertions(+)`; rows 181 → 182; only the S258 row and a note added | PASS |
| G16 | Staged item and "`/home/vgpnk/Projects/shokuknow` was not read" (29) | not checkable from lane bytes | — | UNVERIFIABLE (process claim) |
| G17 | Spot-check "counted 1" (I1 line 47 and Gate 33): spot-check's method (rows that cite the file as a source) gives one | `git show 7eebc18:corpus/lessons/round-40-verifier-spotcheck.md \| sed -n 57p` ; `git show bffcc0f:corpus/SOURCES.md \| grep -n 'worktree\.c'` | spot-check: "1 row, S009, actually cites the file; 0 at v2.56.0". Whole-file grep = 3 lines: `:38` (S009), `:62` (S033), `:240` (prose). Spot-check parenthetical "S033/S058/S232 match" is wrong (S058, S232 do not contain `worktree.c`) — see N-b | PASS (the stated count); N-b |

### Additional verification commands (for the record)

- `git merge-base --is-ancestor bffcc0f 7eebc18` → ancestor (round-40 bytes precede the round-41 base); `git log --oneline bffcc0f..7eebc18 | wc -l` = 1 (the round-40 spot-check commit).
- `git grep -n 'v2\.56\.0/worktree\.c'` on tip vs `git grep -n 'v2\.56\.0/builtin/worktree\.c'` on tip: confirms N-a (the literal misses the builtin path).
- `git ls-tree -r 1d41c13 census/round-41/sources/` — snapshot blobs 77ecd0f… (v2.56.0, 44631 bytes) and d21c43f… (v2.55.0, 42566 bytes); `wc -l` of v2.56.0 = 1541.
- `git status --short` in the lane after every command: empty (no lane mutation).

## Residual risk and verification gaps

- The staged S160 package (`fleet-prune-safety-r28.md`, `SOURCES.append.md`) is outside the committed lane; its contents (and the claim the round-40 reject quotes it) cannot be checked from lane bytes.
- `/home/vgpnk/Projects/shokuknow` was not read (out of scope; the lesson states it was not read).
- The wave-1 seat reports R41scout03/R41reviewer03 are cited for "no other carrier"; R41scout03 was checked (line 61); R41reviewer03 was not re-read.
- The fleet-root report (F3) was checked as a file on the fleet root, not as a git object.
- The frozen counter re-run (S8) re-checks CORRECTION lines only at its constant MEASURED revision (N-c); the row and file values at bffcc0f were re-derived by the shell commands above, not by the counter.

## Recommended corrections (for the lesson owner; not applied by this seat)

1. I3: name the after receipt as `census/round-40/records/c1-after-d.txt` (SCORECARD.md:791) and, if the final-instrument receipt is meant, `c1-after-h.txt` (SCORECARD.md:811); the counter's hard-coded `c1-after-h.txt` (c1-counter.py:81) then needs the same review.
2. Gate, S009 note: cite `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:27`, not the S009 row.
3. I4: state `.ufo/reports/round-40/souji.md:79` is at the fleet root.
4. Optional: note in I1 that the literal `v2.56.0/worktree.c` misses `v2.56.0/builtin/worktree.c` (S258).
