# S75ExecEvade — falsification of C1 gate (W 1ad737b) ignore-source rule

Gate blob: `git show 1ad737b:tools/souji-pre-report-gate.sh` sha256=620ed97e… (matches lane file).
Frozen C1 counter re-run: `SUMMARY rows=25 mismatches=0 errors=0` (reproduced).
Verdict: C1 claims survive; 1 new finding (HIGH) on a vector the r74 probe routed differently.

## Route table (gate rc / check-clean / label)

| route | rc | clean | verdict |
|---|---|---|---|
| a XDG_CONFIG_HOME/git/ignore hides new.txt | 1 | FAIL (pinned status lists 1) | NOT FORGERY — caller env reaches status too; gate doesn't scrub HOME/XDG but pinned status also hides it, and FAIL is still FAIL. Direct: `XDG_CONFIG_HOME=… git ls-files --exclude-standard` lists new.txt. |
| a2 HOME/.gitconfig core.excludesFile | 1 | FAIL (pinned status) | NOT FORGERY. Without HOME env, `git config --get core.excludesFile`=empty: default user gitconfig already had no rule in this container; with HOME env status empty + `--exclude-standard` lists new.txt (unmasked). Gate relies on nothing here. |
| a2-honest (committed rule) | 0 | PASS | correct |
| a3 GIT_CONFIG_GLOBAL via env | 1 | FAIL (`?? new.txt`) | NOT FORGERY — gate unsets it (gate.sh:4), file visible |
| b info/exclude + committed sub/.gitignore | 1 | FAIL RECEIPT-UNTRACKED-LOCAL-EXCLUDE | correct (sub committed rule doesn't cover root) |
| c committed `!new.txt` + exclude `new.txt` | 1 | FAIL (`?? new.txt`) | NOT FORGERY — .gitignore negation makes file visible to status |
| c2 committed `new.txt` + exclude `!new.txt` | 0 | PASS | NOT FORGERY/over-refusal: file *is* ignored under both listings (standard={new.txt}, perdir={new.txt}; `check-ignore` → `.gitignore:1`); local negation loses to committed rule — committed policy wins, legitimately PASS |
| d untracked sub/.gitignore in tracked dir | 1 | FAIL (`?? sub/.gitignore`) | NOT FORGERY: untracked .gitignore itself is status-visible (outer status catches it before r75 rule). Stated f7 limit only covers dirs whose .gitignore is *inside* the untracked dir |
| d2 untracked sub/.gitignore, no-match pattern | 1 | FAIL (`?? sub/.gitignore`) | NOT FORGERY, same reason |
| e tracked .gitignore + skip-worktree rule | 1 | FAIL RECEIPT-WORKTREE-STAT-CONCEALED | NOT FORGERY — r74 truth check catches it (not the r75 rule, but killed) |
| f exclude `newdir/` + committed `*.txt` | 0 | PASS | NOT FORGERY: under `--exclude-per-directory` the same set is listed (perdir walks *.txt inside untracked dir per git: a `*.txt` pattern matches files anywhere including entries `ls-files -o` reports), so standard==perdir, hidden=∅ → PASS correctly. Committed rule genuinely covers the file |
| f2 honest committed dir rule | 0 | PASS | correct |
| g unreadable sub/ (chmod 000) | 1 | FAIL (`Permission denied`) | NOT FORGERY: gate fails closed (outer git status errors) |
| g-honest | 0 | PASS | correct |
| h GIT_DIR env → other repo | 1 | FAIL RECEIPT-UNTRACKED-LOCAL-EXCLUDE | NOT FORGERY — gate unsets GIT_DIR (gate.sh:4) |
| **h2 core.worktree → pristine clone + exclude+new file** | **0** | **PASS** | **FORGERY (HIGH)** — see below |
| i1 newline in name, exclude | 1 | FAIL (`?? "new\nline.txt"`) | NOT FORGERY: newline splits .gitignore lines so the rule never matched; visible to status |
| i1h newline, committed | 1 | FAIL | NOT OVER-REFUSAL: same reason, no match → FAIL right |
| i2 non-UTF8 name, exclude | 1 | FAIL RECEIPT-UNTRACKED-LOCAL-EXCLUDE | correct |
| i2h non-UTF8, committed | 0 | PASS | correct |
| ctl-clean / ctl-committed | 0 | PASS | correct |

## FINDING HIGH-1 (FORGERY): core.worktree redirection hides untracked files from the r75 rule

Gate consults `git -C $lane status` and `git -C $lane ls-files` (both with `-c core.fsmonitor=false`
only for r75 probe? r75 `_ignored()` adds `-c core.fsmonitor=false` but no override of core.worktree).
With `core.worktree=<pristine clone>` set in the *repo config* (read by caller-env-clean git: repo config
is not caller env and is not scrubbed), both invocations act on the pristine tree:
`status` → empty (rc PASS), `ls-files --exclude-standard` and `--exclude-per-directory` → both empty on
pristine/ → `hidden = ∅` → PASS, while `new.txt` exists untracked (and hidden by info/exclude) in the
real worktree. Observed: `check-clean=PASS rc=0`, `status --porcelain` in clone → empty,
`clone/new.txt` exists, `pristine/new.txt` absent. r74's `l-core-worktree` route modified a *tracked*
file (truth-check row), so its FAIL verdict didn't cover the untracked-hide shape; counter population
has no untracked variant of it. The r75 subtraction inherits the blindness: its inputs are both
redirected identically, so their difference never sees the real tree.
Repro: `.ufo/waves/round-75/w1/S75ExecEvade-h2-coreworktree.sh` → prints `check-clean=PASS` with
untracked new.txt in the real tree (`rc=1` overall only from unrelated check-tip=FAIL in the minimal repro).
Fix direction: read core.worktree (or pass `--git-dir/--work-tree` + `-c core.worktree=` override) so both
enumerations run against the real worktree; or refuse when `git config core.worktree` is set.

## Notes
- No HANG anywhere. No OVER-REFUSAL: every PASS-labeled fixture had a genuinely committed covering rule
  (f, c2 verified set-by-set with `ls-files -z --others --ignored` and `check-ignore -v`).
- Quirk observed: `git ls-files --others --ignored` under a `*.txt`-style rule lists *tracked* `.txt`
  files too (they are matched by the pattern as paths); the subtraction is symmetric so it cancels —
  benign here, but brittle if rule shapes ever diverge between the two enumerations.
- Commands: `python3 evade.py` (probes a–i + honest twins, 2s), frozen
  `c1-evade-counter.py --gate-dir … --work …` → `SUMMARY rows=25 mismatches=0 errors=0` (5s),
  repro script above. Driver and receipts: scratch `/fast/scratch/hyaku/souji-r75/S75ExecEvade/` (evade.py,
  work/, gate/, c1/). Files written: `.ufo/waves/round-75/w1/S75ExecEvade.md` (this),
  `.ufo/waves/round-75/w1/S75ExecEvade-h2-coreworktree.sh`.
- No tool installs needed (git/python3/bash present). Scratch removed before yield.
