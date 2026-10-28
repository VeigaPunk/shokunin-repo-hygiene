# R41w2reviewer01 — C1 calibration re-measurement (wave 2, reviewer)

Seat: R41w2reviewer01 · Role: reviewer · Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Lane tip: 1d41c13574db80fdd9a4bde490b712da7ce2a85f (clean `git status --porcelain`). L1 landing: 31e4d3e758bb903808a9270018d7e5be99ce38a4.
Scope: read-only. No clone, no fixture, no mutating git/jj. Scratch `/fast/scratch/hyaku/souji-r41/R41w2reviewer01` (deleted before yield).

## 1. Counter re-run (committed counter, committed revision)

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 31e4d3e758bb903808a9270018d7e5be99ce38a4 --scratch /fast/scratch/hyaku/souji-r41/R41w2reviewer01
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
EXIT=0

$ ... c1-counter.py --root ... --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch ...
(identical four lines, EXIT=0)
```

Result: target `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` met at both revisions. The counter's own derived values match the three CORRECTION lines at `corpus/lessons/round-41.md` (lines 57, 72, 88 at tip).

## 2. Recorded receipt comparison

`census/round-41/records/c1-after.txt` (committed at 31e4d3e) carries the same header command (`--rev 31e4d3e…`), the same three ITEM lines and the same SUMMARY line, `EXIT=0`. Identical to the live re-run in §1.

## 3. Source census validate

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji ; echo EXIT=$?
(52 lines `souji W04 Sxxx duplicate url … across scopes`, then)
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

- Exit code 0. W04 count = 52 (`grep -c W04` over the output). Registry rows: 182 at the working tree, tip and 31e4d3e (`grep -cE '^\| S[0-9]+ '`); 181 at bffcc0f, +S258.
- `census/round-41/records/census-before.txt` vs live output: `diff` shows only one difference — the receipt's trailing `exit 0` line. The 52 W04 lines and the `ok` line are byte-identical.

## 4. CORRECTION-prose audit (counter checks shape only; prose checked here against bytes)

### I1 — `corpus/lessons/round-40.md:49`, "`worktree.c` appears in 9 rows"
- Filed text verified verbatim at bffcc0f (`git show bffcc0f:corpus/lessons/round-40.md | sed -n 49p` region: "`worktree.c` appears in 9 rows of `corpus/SOURCES.md`").
- Derivations re-run at bffcc0f: rows in `corpus/SOURCES.md` (`^| S[0-9]+ `) = 181; rows containing `worktree.c` = 2 (S009, S033); rows containing `v2.56.0/worktree.c` = 0. S033 cell quote "although worktree.c ages by it" verified. S009 cites v2.55.0 `worktree.c`.
- Other readings I tried to find a 9: `worktree` case-insensitive rows = 26; `worktree.*prune|prune.*worktree` = 14; `git worktree` = 5; `builtin/worktree` = 0; `v2.5` ∩ worktree rows = 5. None gives 9.
- **Verdict on the number: truthful.** **Overstatement:** the prose says "wrong by any reading"; the lesson enumerates two readings. No reading I tried gives 9, but the universal is not demonstrated in the lesson. Minor.
- S258 sourced leg: row present at 31e4d3e (`grep -c '^| S258 '` = 1), tier A, opened 2026-10-28, cells name `v2.56.0` and `worktree.c` (counter `sourced=1`). Snapshot `census/round-41/sources/git-v2.56.0-builtin-worktree.c`: 1541 lines; sha256 `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc` (matches SHA256SUMS line 1); quote `prune missing working trees older than <time>` at line 255 (single match, `grep -n -F`); line 229 is the `should_prune_worktree(the_repository, …)` call; line 259 `expire = TIME_MAX;`. `diff` of lines 171–266, v2.55.0 vs v2.56.0: one differing line (59 in the window, i.e. file line 229), exactly as the lesson states.

### I3 — `SCORECARD.md` r40 C1 row, "like-for-like" claim
- Filed row at bffcc0f: `SCORECARD.md:791`. Its before cell cites `census/round-40/records/c1-before.txt` (`register_cells=6`). **Its after cell cites `census/round-40/records/c1-after-d.txt`**, not `c1-after-h.txt` (`register_cells=3`); the row's receipt cell also reads `c1-after-d.txt`.
- The CORRECTION prose says the SCORECARD row "presents `c1-before.txt` and `c1-after-h.txt` as one before→after". **That receipt name is wrong for the filed row.** `c1-after-h.txt` is named by the lesson, by the counter (`derive` reads `c1-after-h.txt`), and by reviewer02 F1, but not by SCORECARD:791 (grep for `c1-after-h` in SCORECARD.md returns only lines 801 and 811, which are unrelated rows).
- Substance verified: `c1-after-d.txt` at bffcc0f carries `register_cells=3` and header `--register census/round-40/cells.tsv` at rev 549d9ec; `c1-before.txt` carries `--register census/round-39/cells.tsv` at rev 0242085. The two arms ran over different register files; the derived value `before=6,after=3` is correct either way; the item arm (`open=3`→`open=0`) is as stated.
- **Verdict: the derived value and the like-for-like finding are truthful; the correction block misnames the after-receipt of the filed row.** Counter did not detect it (shape-only, as the task states).

### I4 — `LOG.md:1909` (r40 Swarm bullet): dead-seat error text; "All wave evidence is captured under `census/round-40/waves/`"
- Verified at bffcc0f: LOG.md:1909 contains `Codex error event: Invalid prompt: your prompt was flagged as potentially violating our usage policy` and the sentence `All wave evidence is captured under \`census/round-40/waves/\`.`
- `census/round-40/waves/` = 136 tracked files at bffcc0f (`git ls-tree -r --name-only` count). Per-file grep for `flagged as potentially`: zero matches in every file.
- Whole-tree search at bffcc0f (`git grep -n -I 'Invalid prompt'`, `'flagged as potentially'`): only LOG.md:1909. So "the lane at bffcc0f has no other carrier" holds for the error text.
- `.ufo/reports/round-40/souji.md:79` (tracked in the fleet repo; `git ls-files --error-unmatch` ok) carries the same error text (W2 role-mix bullet). Verified.
- `w2-results.json`: R40w2reviewer01 and R40w2reviewer04 outputs are partial (`We need target assignment execution…`; `<think>…`), no error text. Verified.
- Prose scope statement and the "[INFERENCE]" label on origin are appropriate. **Verdict: truthful as scoped.**

## 5. Commands run (all read-only)

- `python3 -B …/census/round-41/c1-counter.py --root … --rev 31e4d3e…` and `--rev 1d41c13…` (both `--scratch` under the seat scratch dir): EXIT=0, target met.
- `cat census/round-41/records/c1-after.txt`, `cat census/round-41/records/census-before.txt`.
- `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` (exit 0, output diffed against census-before.txt).
- `git show <bffcc0f|1d41c13|31e4d3e>:<path>` for corpus/lessons/round-40.md, corpus/SOURCES.md, SCORECARD.md, LOG.md, census/round-40/records/{c1-before,c1-after-d,c1-after-h}.txt, census/round-40/waves/w2-results.json; `git ls-tree -r --name-only bffcc0f census/round-40/waves/` (136); `git grep -n -I` for `Invalid prompt`, `flagged as potentially`, `Codex error event`, `worktree\.c`; `git log` for the round-40 spot-check path.
- `sha256sum` and `sed`/`diff` over `census/round-41/sources/*.c`; `grep -n -F` for the S258 quote.
- Fleet `.ufo/reports/round-40/souji.md` lines 77–81 read.
- No tools installed or upgraded.

## 6. Verdict

- **Counter (calibration C1, shape):** MET at 31e4d3e and at the tip, matching `records/c1-after.txt`; validate exit 0, output identical to `census-before.txt` apart from its appended `exit 0` line.
- **Correction truthfulness:** I1 and I4 truthful in substance and scope. I3 derives the right values but **misnames the filed SCORECARD row's after-receipt** (`c1-after-d.txt`, not `c1-after-h.txt`). I1 says "wrong by any reading" without enumerating readings (none I tried gives 9).
- **Recommendation before admission:** an append-only fix to the I3 line (or a note in the lesson) naming `c1-after-d.txt` as the SCORECARD after-receipt and `c1-after-h.txt` as the receipt the counter reads; and narrowing the I1 "any reading" wording. Neither changes the derived values or the counter target. Whether the I3 misnaming is an admission blocker is the main agent's call; I judge C1 verified on the counter and on substance, with one citation defect open.
- No axis harmed by the C1 landing as measured here.
