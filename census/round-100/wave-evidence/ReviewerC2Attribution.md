# ReviewerC2Attribution — correctness review of the C2 attribution repair

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lane base `a662bb0d7e033cc5ceccd70b52eb234404300845`. HEAD at review: `bf990609` (plan commit only; C2 not committed).
Review object: executor `ExecC2Attribution`'s worktree changes (uncommitted at review time) vs the frozen predicate in `plans/round-100.md` A0.1 C2 (lines 32–47) and Q62 (`corpus/QUALITY.md:152`).

Reproducer dir: `.ufo/waves/round-100/w1/ReviewerC2Attribution/`
Reproducer file: `.ufo/waves/round-100/w1/ReviewerC2Attribution/measured.txt`

## Timing note

At review start the correction block did not exist (entry `wc -l` 76, `grep -c S332` = 0, S075 used-by unchanged, ExecC2Attribution wave dir empty, `git status` clean except `?? census/round-100/`). During review ExecC2Attribution wrote the block to the worktree uncommitted. All verdicts below are measured on current worktree bytes plus HEAD bytes, distinguished explicitly. Committed bytes are what the frozen predicate binds ("both legs measured on committed bytes at the landing tip", `plans/round-100.md:43-44`); no C2 commit has landed yet, so the committed-byte status is the pre-repair baseline — not a pass. The L1 must re-run the pair of greps after the lane commit; this seat's worktree measurements predict the post-commit outcome.

## Per-attack verdicts

### Attack (a): does the correction block quote/attribute field-4 wording to S332 with a located quote (<=25 words) or merely name the row?

**Verdict: not-exists** (for a located <=25-word quoted sentence) — the block exists, names and attributes S332, but carries no located quote from S332's anchor/capture.

Evidence (worktree, `corpus/knowledge/deadline-owned-reaping.md:78-81`, appended after line 76; 5 new lines, `git diff HEAD` shows `+5` lines, 0 deletions in the entry):

```
78: ## Round-100 correction (append-only; S075 field-4 attribution withdrawn)
80: - The in-body "S075 field 4" attribution (in the r98 correction paragraph above, "The reap is now by ownership (S075 field 4/22, S368)") is withdrawn in favour of S332 (kernel emission order). S332 is the Linux kernel `fs/proc/array.c` `do_task_stat()` writer at tag v6.17, captured under census/round-83/srcs/ (SOURCES row S332); the field-4 ppid wording follows from the kernel's emission order, not from the proc_pid_stat(5) man page.
81: - The field-22 starttime attribution to S075 stands (S075 § DESCRIPTION fields 5, 6, 22; field 22 is starttime in clock ticks used for PID identity revalidation). No other attribution in the body changes.
```

Measured grep/awk line (reproducer `measured.txt` section E, same bytes):

```
grep -n "S332" corpus/knowledge/deadline-owned-reaping.md  →  80: ...withdrawn in favour of S332 (kernel emission order)...
awk 'NR==80{print NF}' → 65  (line word count; quoted strings in the line are "S075 field 4" and "The reap is now by ownership (S075 field 4/22, S368)" — both locate the old S075 wording, not an S332 quote)
```

What exists: a proper append-only withdrawal citing S332 by id, file, symbol (`fs/proc/array.c`, `do_task_stat()`), tag (`v6.17`), and capture dir (`census/round-83/srcs/`, `SOURCES row S332`), i.e. a row-name + provenance attribute, matching the frozen predicate's leg-1 instrument (`grep -c 'S332' >= 1`). What does not exist: a <=25-word verbatim located quote from the S332 anchor. The S332 row's own anchor is the concatenation of `do_task_stat()` lines 590–594 (`seq_puts(m, " ("); proc_task_name(m, task, false); ... seq_put_decimal_ll(m, " ", ppid);`) with line numbers and occurrence context (`corpus/SOURCES.md:313`); the correction block copies none of it. The two quoted strings in the block are self-quotation of the old S075 wording for the withdrawal, not S332 ground. Under the seat's attack wording (located quote <=25 words), this leg is the attack's "merely name the row" half. Under the L1 frozen predicate as actually written (leg 1 = `grep -c 'S332' >= 1`), the worktree satisfies leg 1 (worktree `grep -c` = 1, `measured.txt` section B) — the seat flags the predicate/attack gap as a finding, not a predicate failure. L1 decides whether the merit bar is the grep or the quote; the verifier spot-check in r99 (S332 `do_task_stat()`, anchor lines 590–594) is the standard the block falls short of.

Reproducer: `.ufo/waves/round-100/w1/ReviewerC2Attribution/measured.txt` (sections B, E).

### Attack (b): does the entry's front-matter `source:` now cite S332 (Q62 bidirectional leg 1) or only the body text?

**Verdict: not-exists** (front-matter does not cite S332) — S332 is cited only in the body correction block.

Evidence (worktree, `corpus/knowledge/deadline-owned-reaping.md:3`):

```
3:source: S367 (Python `subprocess`, the `start_new_session` parameter; that the child calls setsid()); S368 (Linux man-pages `setsid(2)` DESCRIPTION; that the new session is a new process group); scored against census/round-96/c2-forgery-probe.py and census/round-96/c2-setup-arms.py at round 96.
verified-at: S367 page opened 2026-11-09 ...(S367/S368 only; no S332)
```

Measured grep/awk lines (reproducer `measured.txt` section C):

```
awk 'NR==3' corpus/knowledge/deadline-owned-reaping.md | grep -c "S332"  →  0
awk 'NR==3' corpus/knowledge/deadline-owned-reaping.md | grep -o "S367|S368|S332" | sort | uniq -c  →  1 S367, 1 S368, 0 S332
grep -n "S332" corpus/knowledge/deadline-owned-reaping.md  →  80 only (body line, not line 3)
```

Q62 (`corpus/QUALITY.md:152`) binds both directions: "every S-id an entry's front-matter `source:` lines cite must be a row that lists that entry in `used-by`" (K1) and every row's `used-by` path "must ... name that row id" (K2). Consequences:

- Live, worktree: S332 never enters the front-matter `source:` line, so K1 is not engaged by S332 at all. The body-only cite keeps K1 clean (no front-matter cite needing a used-by backlink) but leaves the calibration repair incomplete under Q62's own bidirectional reading: the entry's dependency on S332 is prose, not a citable `source:` attribution. S075's used-by gain (attack c) has the same asymmetry in reverse: S075 names the entry, and the entry *does* cite S075 in body line 65 ("S075 field 4/22") and line 81, but not in front-matter either — front-matter cites S367/S368 only. So the worktree repair creates body-level mutual naming (entry body ↔ S075 used-by: both name each other at body level) but zero front-matter-level leg-1 for either S075 or S332. The frozen predicate's leg 1 (`grep -c 'S332'` over the whole entry file) is deliberately body-blind, so the predicate passes on worktree bytes while Q62's front-matter bar does not. Measured status: Q62 K1 failure does NOT exist (no front-matter S332 cite to fail it), but Q62-grade attribution (front-matter cite + used-by name) also does NOT exist for S332 — body-only is the attack's "only the body text" half, confirmed.
- Committed bytes (HEAD): leg 1 = 0, leg 2 = 0 (`git show HEAD:... | grep -c` = 0/0, reproducer sections A) — the pre-repair baseline, exactly as the plan's "Before at base: leg 1 prints 0, leg 2 prints 0" (`plans/round-100.md:44-45`) predicts. This is not a regression; it is the unlanded state.

Reproducer: `.ufo/waves/round-100/w1/ReviewerC2Attribution/measured.txt` (sections A, B, C).

### Attack (c): is S075's used-by the only row changed (git diff)?

**Verdict: exists** — the only SOURCES.md row touched is S075, and only its used-by cell.

Evidence (worktree, `git diff HEAD`):

```
git diff HEAD --stat  →  corpus/SOURCES.md 2 +- (1 line changed), corpus/knowledge/deadline-owned-reaping.md 5 +++++
git diff HEAD -- corpus/SOURCES.md | grep "^[+-]|"  →  2 lines: -| S075 | ... ; +| S075 | ...
git diff HEAD -- corpus/SOURCES.md  hunk @@ -107,7 +107,7 @@  →  single hunk, line 110 only
```

Measured diff line (`corpus/SOURCES.md:110`, worktree), used-by tail:

```
... | corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md, corpus/knowledge/gate-signal-handling.md, corpus/knowledge/deadline-owned-reaping.md |
```

The added tail `, corpus/knowledge/deadline-owned-reaping.md` is the sole content change on the line; all other cells (id, source, kind, tier, scope, anchor, teaches, status, opened, recheck) are byte-identical (the +/- pair differs only in the used-by tail — verified by the full diff, which shows one line pair, no other +/- lines). No new SOURCES row: `wc -l corpus/SOURCES.md` = 468 before and after (`git diff` shows no added row line; row count unchanged). Note the previously measured 3 matches for `deadline-owned-reaping` in SOURCES.md are the S367/S368/S371 rows' teaches cells mentioning the entry in prose ("grounds the process-group hal...", r96-era), not the S075 row — S075 had 0 until this worktree edit (reproducer section D: `-`/`+` both `| S075 |`). Committed bytes: `git diff a662bb0d..HEAD --name-only` = `plans/round-100.md` only, and `git show HEAD:corpus/SOURCES.md` S075 row = pre-repair bytes (no entry) — so committed-byte isolation holds trivially at HEAD; the worktree isolation (S075-only) is what ExecC2Attribution must land, and it is exactly what is on disk.

Reproducer: `.ufo/waves/round-100/w1/ReviewerC2Attribution/measured.txt` (sections D, F).

## Findings

**F1 (attack a, located-quote gap).** The correction block attributes field-4 to S332 by name/provenance (line 80: file, symbol, tag, capture dir, row id) but quotes no S332 sentence <=25 words and cites no S332 anchor line numbers (590–594) or occurrence count — the standard S332's own row carries (`corpus/SOURCES.md:313`) and r99's verifier used for S332 ("the kernel procfs writer", round-83 Gate). The block satisfies the frozen predicate's leg-1 grep but not the seat's located-quote attack. Severity: calibration-nit, not a predicate failure under the L1's grep instrument; L1 to decide whether to require the quote before landing. Reproducer: `measured.txt` section E; block at `corpus/knowledge/deadline-owned-reaping.md:80`.

**F2 (attack b, front-matter gap).** `source:` (line 3) still cites only S367/S368; S332 appears only in body line 80. Under Q62 (`corpus/QUALITY.md:152`), a body-only cite is not bidirectional evidence: K1 (front-matter cite → row names entry) never engages for S332, and K2 (row names entry → entry's `source:` cites row) is broken in the S075 direction too (S075 used-by names the entry, entry front-matter names S367/S368 only). The frozen predicate (whole-file `grep -c`) cannot distinguish this from a front-matter cite. Severity: the routed defect's "correct by new entry/row" intent is only half-met at the Q62 grade; the L1's frozen grep passes but the attribution remains prose. Reproducer: `measured.txt` section C; front-matter at `corpus/knowledge/deadline-owned-reaping.md:3-4`.

**F3 (timing/state, no defect).** All legs verified on worktree bytes; committed bytes (HEAD `bf990609`) still show 0/0. If the L1 lands ExecC2Attribution's exact worktree bytes, the committed-byte predicate becomes 1/1 by construction (same greps, `measured.txt` sections B+C predict it). Re-verify at the landing tip before claiming C2. No action beyond the L1's normal commit-time measurement.

## Commands run (all from `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only git)

- `git -C ... rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`; `git log --oneline -5` → HEAD `bf990609`, base `a662bb0d`; `git status --short` → initially clean except `?? census/round-100/`, later ` M corpus/SOURCES.md; M corpus/knowledge/deadline-owned-reaping.md`.
- `grep -c 'S332' corpus/knowledge/deadline-owned-reaping.md` → 0 at start, 1 after ExecC2 writes (exit 0 both; count is the measurement).
- `awk '/^\| S075 /' corpus/SOURCES.md | grep -c 'deadline-owned-reaping'` → 0 at start, 1 after; `git show HEAD:corpus/SOURCES.md | awk ...` → 0 (committed baseline).
- `awk 'NR==3' ...deadline-owned-reaping.md | grep -c 'S332'` → 0 (front-matter never updated).
- `git diff HEAD` → SOURCES.md 1-line (S075 used-by tail only) + entry +5 lines append-only; `git diff a662bb0d..HEAD --name-only` → `plans/round-100.md` (committed C2 = none).
- `sed -n '78,81p' ...deadline-owned-reaping.md`; `awk 'NR==80{print NF}'` → 65; `awk 'NR>=78' ... | grep -o '\"[^\"]*\"'` → `"S075 field 4"`, `"The reap is now by ownership (S075 field 4/22, S368)"` (no S332 verbatim quote).
- Reproducer capture: combined greps/awk/diffs → `.ufo/waves/round-100/w1/ReviewerC2Attribution/measured.txt` (exit 0).

Scratch `/fast/scratch/hyaku/souji-r100/ReviewerC2Attribution/` was created at start and is empty (mkdir only, no large files); it is removed before yield (own defect if left). No tool installs were needed; no `model` passed anywhere; no git mutations by this seat.

No predicate was edited by this seat. F1/F2 are findings for the L1; the committed-byte predicate remains 0/0 until the L1 lands the worktree bytes.
