# S68ReviewerCounter — review of the frozen r68 counter edits vs the r67 counter

Scope: read-only review of `census/round-68/c1-counter.py` against `census/round-67/c1-counter.py`, the
writer blob at f70da577 (`sha256 b811ee2a…`, extracted and re-hashed), `census/round-68/c1-matrix.tsv`,
`census/round-68/mutate-writer.py`, `census/round-68/battery/SHA256SUMS`, and the two do-nothing controls.
No lane file was written; no counter/matrix/mutant byte was altered; the full counter battery was NOT run.

## Check 1 — every changed line of the r67→r68 diff: PASS

Full `diff -u` reviewed (367 lines; every hunk accounted for):

| Change | r68 location | Verdict |
|---|---|---|
| scrub tuple gains GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES | c1-counter.py:400-411 (new vars 408-409) | PASS — per-case caller values (W1-W6, PK4/PK7 extras) are applied AFTER the scrub via `clean_env(extra)`; every child env (git_run :415-417, run_slot :727-728, git_show :797-798, run_fixture :831-833) is scrubbed |
| CASE_ORDER adds W4 W5 W6 PK3 PK3h PK4 PK4h PK6 PK6h PK7 PK7h | c1-counter.py:247-251 | PASS — 31 r67 rows + 11 new = 42 = matrix rows |
| CASE_SPECS new entries | c1-counter.py:314-325 | PASS — W4 repo_name=main, cwd_parent, mode_change; W5 cwd_gitdir; W6 honest alias; PK4/PK7 honest pairs; PK6 honest pair |
| mutate() branches for the 6 new env_kinds | c1-counter.py:551-635 | PASS — see per-row states below |
| case_env() branches | c1-counter.py:689-711 | PASS — W4 → `GIT_COMMON_DIR=main/.git` (relative); W5 → `""`; W6 → abs symlink alias; PK3/PK6 → `{}`; PK4 → GIT_CONFIG_GLOBAL; PK7 → GIT_CONFIG_SYSTEM |
| cwd rules | c1-counter.py:859-871 | PASS — cwd_parent → repo parent (W4), cwd_gitdir → repo/.git (W5); W4 instrument re-named `instr.sh` (root-level dual copy exists, :437-445) |
| fixture_from_blob replaces clone-based fixture | c1-counter.py:812-825 | PASS — regress bytes always == `--base-rev` blob (M10 fix); no HEAD drift possible |
| emitted regress header | c1-counter.py:1160 | PASS — now `# regress fixture=<work>/regress/r60-receipt-write.py from 36390879…:tests/fixtures/r60-receipt-write.py (blob)`; both controls show the new line |
| COUNTER_REL r67→r68 | c1-counter.py:217 | PASS — receipt `instrument=` line names the r68 counter |

## Check 2 — per new row: fixture builder/case_env state seen by each slot, and matrix expectation vs writer refusal strings: PASS

Writer refuse() strings confirmed at blob f70da577:tools/souji-receipt-write.py:398 (`lane worktree is
dirty (git status --porcelain non-empty); …`) and :300-309 (`RECEIPT-ENV-COMMONDIR-MISMATCH`, empty value
refused before any git call at :302-303). All 42 matrix rows use only class strings the candidate emits
(RECEIPT-STATE-CHANGED-DURING-RUN :512, RECEIPT-INDEX-FLAG-CONCEALED :150, RECEIPT-INDEX-ENV-SET :334,
RECEIPT-ENV-CONFIG-SET :322, RECEIPT-ENV-REDIRECT-SET :327).

- W4 (matrix:33): both slots see repo `<case>/main` with tracked tools/instr.sh 755→644, a git-dir copy at
  `<case>/main/main` (config fileMode=false) hidden by `.git/info/exclude main/`, caller GIT_COMMON_DIR=`main/.git`,
  writer cwd=`<case>`. Base (a8c47d36: no check, no scrub): git -C root resolves the value to `<root>/main/.git`,
  which does not exist → incidental `not a git repository` refusal (L1 confirmed in control). Candidate: value
  check passes via cwd realpath (:307-309), scrub (:99) keeps git calls on the real repo → dirty → expected class.
- W5 (:34): both see a clean honest repo, caller GIT_COMMON_DIR=`""`, cwd=`repo/.git`; base passes "" to git →
  incidental not-a-git-repository refusal; candidate refuses the empty value outright at :302-303 → expected class.
- W6 (:35): both see clean repo + `<case>/alias-git` symlink → repo/.git; base accepts (env value is a valid
  alias); candidate realpath-equal check passes → accept ✓.
- PK3/PK3h (:36-37): repo-local config `core.excludesFile=<case>/excl-local.txt` naming tools/hidden.txt (defect
  variant writes the untracked file); candidate `-c core.excludesFile=<devnull>` pin (writer :105-106) keeps
  hidden.txt visible → dirty; honest variant clean → accept.
- PK4/PK4h (:38-39): caller GIT_CONFIG_GLOBAL=<case>/global-mode.gitconfig (`fileMode=false`), fixture filemode
  unset; GIT_CONFIG_GLOBAL=devnull pin (writer :102) → mode change visible → dirty; honest → accept.
- PK6/PK6h (:40-41): repository refs/replace/<HEAD> → forged replacement commit; index+worktree carry the same
  forged bytes; GIT_NO_REPLACE_OBJECTS=1 pin (writer :104) → read tree differs from forged worktree → dirty;
  honest (no replace ref) → accept.
- PK7/PK7h (:42-43): caller GIT_CONFIG_SYSTEM=<case>/system-mode.gitconfig (`fileMode=false`); GIT_CONFIG_NOSYSTEM=1
  pin (writer :103) → dirty; honest → accept.

Statically, all 14 battery mutants (battery/SHA256SUMS: candidate b811ee2a… + 14 lines) are refuted by specific
rows: K1→E1/E2, K2→E4/E5/E6, K3→PK3, K4→PK4 (also E3), K5→MOD2, K6→PK6, K7→PK7, K8→N3/P13, M-CD-CALL→W2 (accept
→ forgery) and W1 (wrong class), M-CD-EMPTY→W5 (realpath("")==cwd==repo/.git passes the dropped-empty check →
accept), M-CD-NCABS/M-CD-NCRAW→W6 (alias symlink compared non-canonically → refuse on an honest row),
M-CD-ROOTREL→W4 (resolves value against root → commondir-mismatch class, not "lane worktree is dirty"),
M-CD-SCRUB→W4 (caller value leaks into git() → unresolvable path → wrong-class refusal; the do-nothing control's
base W4 stderr empirically confirms this resolution semantics: `fatal: not a git repository`).

## Check 3 — verdict logic: PASS (2 LOW)

- No EXIT=0-with-error-rows path: any `new=error` row (build failure c1-counter.py:854-857, or judge "error"
  :740-741) sets `all_new_match=False` (:857, :897) AND either a class_mismatch (refuse rows, :890-891) or
  new_honest<n_accept (accept rows, :893-894); `claim_upheld` (:923-926) requires all of new_forgeries=0,
  new_honest==n_accept, class_mismatches=0, regress==PASS, all_new_match; exit is `0 if claim_upheld(res) else 1`
  (:1167). Fatal paths print EXIT=2 (:961-964).
- Crash mapped to refuse: impossible. judge returns "refuse" only for rc==2 with no out file (:739-740); a writer
  crash (rc 1 / traceback), timeout (124), or kill maps to "error" (:741) → error row → excluded by the frozen
  predicate's zero-`new=error` clause (and the claim itself is killed, not upheld). A counter crash (uncaught
  non-CaseError, e.g. OSError in build_case) exits 1 without EXIT=/SUMMARY lines — environmental only (run_slot
  contains all subprocess errors), hits the candidate arm equally, and is caught by the kill rule.
- LOW — F1 substring class match: findings_for matches the expected class as a raw substring of writer stderr
  (c1-counter.py:744-747); an incidental refusal whose text contains a class token would count as a class match.
  No collision exists today (tokens are RECEIPT-* branded except "lane worktree is dirty", unique to writer:398).
  Repro: none current — latent.
- LOW — F2 docstring mechanism narrative for W4 ("git -C <root> resolves it against the ROOT (main/main/.git,
  the poison)", c1-counter.py:8-13) misstates the resolved path (`<root>/main/.git` doesn't exist; the copy
  occupies `<case>/main/main`), so an M-CD-SCRUB mutant is refuted by an unresolvable-repository class, not by
  the poison config hiding the mode change. Verdict-integrity unaffected (class mismatch still flips
  class_mismatches); documented behavior confirmed by control evidence.

## Check 4 — do-nothing controls: PASS

`sha256sum census/round-68/c1-counter.py` → `ab3ac5c78a623c145e768ffb0c233e9f65a892a78431de44790187da3fdb37f0`
== `instrument_sha256=` in both controls; `rev=3639087917eaeb28719d7603110a6ec22782100e` in both — correct for a
--new-tool (do-nothing) run; grammar: `measured = ns.rev if ns.rev else ns.base_rev` (c1-counter.py:1176-1177),
and --new-tool mode sets no --rev. Both slots sha256=a8c47d36… (base writer), matrix sha bb56e69a…, regress
blob-sourced. `c1-do-nothing.txt`: …

- SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=2 new_honest=11 class_mismatches=4 regress=PASS; EXIT=1.
- new_forgeries=2 = W1+W2 accepts — exactly the statically predicted rows (base writer has no COMMONDIR check and
  its git() does not scrub GIT_COMMON_DIR); class_mismatches=4 = W1, W2, W4, W5 (W4/W5 wrong-class "not a git
  repository" refusals, L1 confirmed verbatim in the control detail lines). base_honest=11 = the 11 accept rows.
- `c2-do-nothing-ambient.txt`: byte-identical header hashes and CASE/SUMMARY/REGRESS/EXIT lines under the ambient
  env; `diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' c1-do-nothing.txt) <(… c2-do-nothing-ambient.txt) | grep -c '^[<>]'` → 0.
  The do-nothing arm is flip-free, as the scrub design predicts for the candidate arm.

## Check 5 — selftest (single allowed run): PASS

`python3 -B census/round-68/c1-counter.py --selftest --root /home/vgpnk/Projects/shokunin/souji-shokunin
--matrix census/round-68/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e
--work /fast/scratch/hyaku/souji-r68/S68ReviewerCounter/selftest-work` (run from the lane root) printed
`SELFTEST cases=8 pass=8 fail=0` / `EXIT=0`, matching the frozen census/round-68/controls/r68-selftest.txt.
(First attempt with a nonexistent --work dir printed `C1-COUNTER-FATAL: work directory does not exist`, EXIT=2 —
expected guard behavior, work dir must pre-exist.)

## C1-predicate satisfaction question (acceptance criterion)

Can the C1 predicate as frozen be satisfied by any writer that does not implement the writer's protections? **No.**
The candidate arm pins the exact SUMMARY (new_forgeries=0 ∧ class_mismatches=0 ∧ new_honest=11 ∧ regress=PASS,
c1-counter.py:923-926): zero forgeries requires refusing each of the 29 forgery rows, class_mismatches=0 requires
the refusal text to name the row's exact class (each class identifies the specific protection that fired — dirty,
state-changed, flag-concealed, env-gates, commondir-mismatch), and new_honest=11 forces acceptance of programs the
protections deliberately allow. A writer without a protection either accepts its forgery row (new_forgeries>0),
refuses with the wrong class (class_mismatches>0), or over-refuses honest rows (new_honest<11) — none satisfy the
SUMMARY. The battery arm independently pins every protection's load-bearing status: each of the 14 single-edit
mutants must flip to EXIT=1, so a protection present but non-load-bearing (its row discharged by another
mechanism) makes its mutant survive at EXIT=0 → kill. No writer lacking the protections meets both arms.

## Residual risk / verification gaps

- base=error rows do not enter any count (evaluate :894-897 only counts accepts/refuse-verdicts), but the C1
  predicate pins the full SUMMARY string (base_forgeries=2 base_honest=11), so a silent base error cannot pass.
- The mutant-battery exit codes and the candidate SUMMARY are not re-measured here (full counter run forbidden by
  my seat spec); the verdicts above are static source analysis corroborated by the four committed control
  artifacts, and must be confirmed by the assigned battery/ambient seats.
- No LSP server is available for this seat's session; all caller/definition checks above are text+hash level
  against frozen bytes (git show + sha256sum), never against worktree state.
- Tooling authorization: no tools were installed or upgraded this session; no pacman/uv/npm actions taken.

## Files written under the seat directory

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68ReviewerCounter/review.md (this file)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68ReviewerCounter.md (registry copy of this report)

Scratch (/fast/scratch/hyaku/souji-r68/S68ReviewerCounter: counter.diff, writer-candidate.py, writer-base.py,
selftest-work/) deleted before yield.
