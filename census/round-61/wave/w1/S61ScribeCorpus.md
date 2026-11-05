# S61ScribeCorpus — round 61 corpus drafts (seat report)

Seat: S61ScribeCorpus (leaf scribe, round 61, wave w1). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lane HEAD observed read-only: `c7228424c3919ecf142bab1aec8181722d86467b`.

Scope: draft corpus text only. No production file, lane index, jj state, fleet file or sibling lane was written. No `git add`/`commit`/`stash`/`checkout`/`jj`. No install, no upgrade, no subagent dispatch. Every sentence below is either observed in a command output listed under "Commands run" or marked `[INFERENCE]` / pending.

## Delivered (absolute paths; delivery dir `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-61/w1/S61ScribeCorpus/`)

| file | content |
|---|---|
| `.../S61ScribeCorpus/sources-rows.md` | two SOURCES rows, S290 (git-log `--diff-filter`, used-by `corpus/knowledge/control-chronology-binding.md`) and S291 (git-update-index `--skip-worktree`, used-by `corpus/knowledge/skip-worktree-concealment.md`); status `queued`; opened 2026-11-05; S290 recheck `180d` as specified, S291 recheck `180d` chosen by this seat (the spec named none). |
| `.../S61ScribeCorpus/knowledge/control-chronology-binding.md` | 56 lines; knowledge entry, house style (`ground:` / `source:` / `verified-at:` / `recheck:` then Claim, What it cannot prove, Decision rule, Round evidence). |
| `.../S61ScribeCorpus/knowledge/skip-worktree-concealment.md` | 58 lines; same shape; writer rule (digest the committed blob, compare worktree to it, never trust `git status`). |
| `.../S61ScribeCorpus/lesson-round-61-skeleton.md` | `## Gate`, `## Mistakes`, `## Named limits` (plus `## Integrated verification`); Mistakes row 1 is the mined r60 mistake (class: unsurfaced rejection-ground finding, self-assessment overreach; evidence: `census/round-60/wave/w1/S60CriticRound/S60CriticRound.md` Finding 1 and `corpus/lessons/round-60-verifier-spotcheck.md`; captured-by: none; fix: Q121). `SPOTCHECK-RESULT` placeholder present. |
| `.../S61ScribeCorpus/quality-q121.md` | `## Round 61 criteria` section with the Q121 row in the Round 56–59 table shape (id, criterion, applies to, check, motivating evidence). Append after the current end of `corpus/QUALITY.md` (last heading there is `## Round 59 criteria`). |
| `.../S61ScribeCorpus/readme-index-row.md` | index row for `knowledge/freeze-record-substance-binding.md`: the F1 row at `corpus/README.md:39` in `## r12 additions` → `### Coverage map`, edited in place (the r26–r40 convention), exact old tail → new tail. |
| `.../S61ScribeCorpus/skill-pointer-fix.md` | one-line fix, `SKILL.md` line 796: `census/round-60/w1/S60ExecFreezeArm/byte-identical.txt` → `census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt` (the new path exists, 3504 bytes). |

Placeholders for the L1 (none may land unfilled): `QUOTE-PLACEHOLDER-1..4` (S290 access record, S290 teaches, S291 access record, S291 bit-goal teaches), `SPOTCHECK-RESULT`, and `L1-FILL` markers in the skeleton (freeze commit id, row 2 of Mistakes, Named limits, Gate status).

## Commands run (exit codes observed)

1. `mkdir -p` scratch and delivery dir; `ls corpus/knowledge`, `tail`/`grep` of `corpus/SOURCES.md` (rows S260–S289, status vocabulary `mined`/`queued`/`rejected`); `grep -n` of `SKILL.md` line 796; — all rc 0.
2. `sed`/`cat` of `corpus/knowledge/freeze-record-substance-binding.md`, `git-strict-descendant-relation-r40.md`, `quarantine-restore-path-reoccupied.md` (house style); `sed` of `corpus/QUALITY.md` Round 59 table header; `sed`/`grep` of `corpus/README.md` — rc 0.
3. `ls census/round-60/wave/w1/S60CriticRound`, `sed -n 1,30p` / `grep -n` of `S60CriticRound.md` (Finding 1 at line 44 `### 1. Q120 chronology ... VIOLATES`); `sed` of `corpus/lessons/round-60-verifier-spotcheck.md` — rc 0.
4. `git --version` → `git version 2.56.0`. `MANWIDTH=100 man git-log` / `man git-update-index` / `man git-status` read for the `--diff-filter` and `--skip-worktree` wording — rc 0 (the installed man pages; no web fetch was made by this seat).
5. `git -C <lane> rev-parse HEAD` → `c7228424c3919ecf142bab1aec8181722d86467b`; `git -C <lane> cat-file -p 2670e96a…` → present (rc 0), used only to confirm the r60 freeze commit exists.
6. `grep`/`sed` of `tools/souji-freeze-check.py` `freeze_rev` (lines ~141–145): `git log --diff-filter=A --no-renames --full-history --reverse --format=%H rev -- prereg`, first full id taken (used as observed base fact in the knowledge entry).
7. Validation (rc 0): `awk -F'|'` cell count over the two S290/S291 rows → 11 cells each, matching S289's 11 cells; `wc -l` of knowledge entries → 56 and 58 (both under 60); `grep -o QUOTE-PLACEHOLDER-[0-9]` inventory → 1..4 present; `ls -la` of `census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt` → exists, 3504 bytes; `grep -n 'SPOTCHECK-RESULT'` → 2 hits in the skeleton.
8. Stale-path sweep `grep -rn "round-60/w1/" corpus SKILL.md … census` (rc 0): hits in `SKILL.md:796` (fixed by this seat's draft, not applied) and in `corpus/lessons/round-60-verifier-spotcheck.md:234–236` (the non-author closure's own text; out of scope, see limits).

No check that exercises the freeze checker, the receipt writer or any fixture was run, because the C1/C2 implementation is the L1's and no candidate tool bytes exist in this seat's delivery. No test passed or failed on this seat's files.

## Findings (scoped)

1. The two knowledge entries state only what the sources and the base bytes show. Their measured results are not stated; each points to `census/round-61/` for the landed evidence. The r61 real-record numbers (base EXIT=0 findings=0; candidate EXIT=1 with ≥2 `CONTROL-ADDED-NOT-BEFORE-FREEZE`) appear only as the arm's acceptance target, not as observed.
2. `freeze_rev` in base `tools/souji-freeze-check.py` already resolves the oldest add with the same `--diff-filter=A --no-renames --full-history` set the C1 rule needs. The C1 rule should reuse it or state why not. The re-added-path choice is a real design decision left open in the entry, marked `[INFERENCE]`.
3. The skip-worktree status-silence reading is not in the S291 manual text (the manual speaks to absence and deletion, and to assume-unchanged's different goal). The entry marks it `[INFERENCE]` and makes the writer compare bytes, so the claim does not depend on it.
4. `README.md` does not index `knowledge/freeze-record-substance-binding.md` at all (grep: no match). The proposed row is an in-place append to the F1 cell, following the in-place convention.

## Named limits

- **Quotes unverified.** None of the four quote placeholders is filled. The S290/S291 rows and knowledge `source:` lines cite URLs and access dates that this seat did NOT fetch from the web; the claims rest on the installed man pages (git 2.56.0). The scout's captures must confirm the wording, or the rows stay `queued`. `queued` rows must not be cited as admitted until then.
- **`--no-renames` wording is outside S290's scope.** Flagged `[INFERENCE]` in the knowledge entry, not sourced.
- **Planned evidence paths.** `census/round-61/…` does not exist yet; the knowledge entries and the Q121 evidence cite it generically. The L1 must confirm landed names before landing.
- **`corpus/lessons/round-60-verifier-spotcheck.md:234–236`** carries the same broken r60 path the SKILL fix repairs, and the closure text itself says "Correct the path". That file belongs to the non-author closure and is not edited by this seat; the L1 decides.
- **Recheck for S291** (`180d`) is this seat's choice, not a spec value.
- **Index for r61 entries** is not drafted; the README note says index them only after they land.
- **Q121 check** names a `corpus/lessons/round-61.md` file that will exist only after the L1 writes it.
- **Knowledge lines** are 56 and 58; the cap is "under 60", which both meet.

## Out of scope (not done)

- No candidate `tools/souji-freeze-check.py` or `tools/souji-receipt-write.py`; no fixture (C1/C2 are the L1's).
- No edit to `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*`, `corpus/knowledge/*` — all were drafted into the delivery dir for the L1.
- No web capture (scout's job); no fleet-repo or sibling-lane access.

## Tooling

No install or update. `git 2.56.0` was already on the host and used read-only. Scratch `/fast/scratch/hyaku/souji-r61/S61ScribeCorpus/` was created empty and removed; it held no receipts.
