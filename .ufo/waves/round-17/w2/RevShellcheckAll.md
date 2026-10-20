STATUS: DONE — no new `shellcheck -S warning` findings and `bash -n` clean in all 6 changed shell files at ddb7347 (counts AND finding keys equal to 5fa6017); shellcheck dead-code signals expose 17 r17-added lines in never-invoked code (minor) and one masked git status in `jj_keep_novel` (low, optional check).

Seat: RevShellcheckAll (SoujiR17-3.RevShellcheckAll-2) · wave 2 FALSIFY · axis: operability
Revisions: ddb73474433977ff54b015ac3e77669ff2537353 (changed) vs 5fa6017ddcae9f6bd4412df44765f6360cb16294 (base)
Tools: ShellCheck 0.11.0 (/usr/bin/shellcheck, pre-installed), GNU bash 5.3.20(1)-release. Installs/updates: none.
Line numbers below are `git show ddb7347:<path>` lines unless prefixed `base:`.

## Verdict

| claim under attack | verdict |
|---|---|
| r17 introduces no new `shellcheck -S warning` findings in the 6 changed shell files | **holds**: per-file counts equal, and the finding multiset keyed by (code, level, message, source-line text) is identical except one pre-existing SC2034 re-anchored onto an r17 line (F1) |
| `bash -n` clean | **holds**: rc 0 for all 11 files (6 new + 5 base; fixture absent at base) |
| "shellcheck -S warning clean" as a blanket claim for all changed tools | **fails as wording**: `tools/souji-verify.sh` (7) and `tools/souji-vault-verify.sh` (9) return rc=1 at BOTH revisions. Clean (rc 0) only for souji-census.sh, souji-quarantine.sh, vadv54-harness.sh and r17-jj-receipts.sh. Any SCORECARD/QUALITY/LOG draft must say "no new warnings", not "clean" |
| C3 "(b') … dead shadowed sites untouched" | **partial**: see F1. r17 put logic into 3 never-invoked sites and a whitespace edit into 1 redefinition-shadowed site |

## Results (`shellcheck -S warning`, the same invocation as census/round-17/run-matrix.py:208)

| file | base bash -n | new bash -n | base rc / findings | new rc / findings |
|---|---|---|---|---|
| tools/souji-census.sh | 0 | 0 | 0 / 0 | 0 / 0 |
| tools/souji-verify.sh | 0 | 0 | 1 / 7 | 1 / 7 |
| tools/souji-vault-verify.sh | 0 | 0 | 1 / 9 | 1 / 9 |
| tools/souji-quarantine.sh | 0 | 0 | 0 / 0 | 0 / 0 |
| tests/fixtures/r17-jj-receipts.sh | absent | 0 | absent | 0 / 0 |
| tests/vault/vadv54-harness.sh | 0 | 0 | 0 / 0 | 0 / 0 |

tty, `-f gcc` and `-f json1` give identical counts and rc for every file.

Pre-existing warnings, unchanged by r17 (shown at their new lines):
- verify (7):
  - SC2221/SC2222 :131 (`*.env` shadows `.env`)
  - SC2100 ×3 :384:37, :849:17, :849:43: false positives, because `unpushed-branch` literals parse as subtraction
  - SC2034 R_REASON :882:52
  - SC2034 SC_PASS :1001:32 (moved from base:953:9; see F1)
- vault-verify (9):
  - SC2221/SC2222 :122
  - SC2100 ×4 :562:37, :562:63, :1053:17, :1053:43
  - SC2034 FAIL_REASON :907:5, SC_PASS :1207:9, VAULT_HINT :1736:16

Things that could hide a warning (all ruled out):
- **rc files**: no `.shellcheckrc` is tracked at either rev (`git ls-tree <rev> -- .shellcheckrc shellcheckrc tools/.shellcheckrc tests/.shellcheckrc tests/fixtures/.shellcheckrc tests/vault/.shellcheckrc` returns nothing for both revs). `stat` finds no rc file anywhere on shellcheck's search path: lane root, tools/, tests/, tests/fixtures/, tests/vault/, /home/vgpnk/Projects/shokunin, /home/vgpnk/Projects, ~/.shellcheckrc, ~/.config/shellcheckrc, /home, /, /var/tmp, /var.
- **Inline suppressions**: zero `shellcheck` directive lines in any of the 11 files (grep `shellcheck`, no matches). r17 suppressed nothing.

All severities (`-S style`): error/warning/info/style totals per file are unchanged, except quarantine info 21 → 20. One SC2329 is gone (`s18_evaluate_worktree_one` gained selftest callers at :1725 and :1731). Code histogram base → new: SC2015 6/6, SC2016 2/2, SC2034 5/5, SC2094 4/4, SC2100 7/7, SC2126 2/2, SC2153 8/8, SC2221 2/2, SC2222 2/2, SC2329 54 → 53. The new fixture has 0 findings at every severity.

## Findings

### F1 — minor (maintainability; no runtime effect): 17 r17-added lines are in never-invoked code, in 3 divergent shapes, breaking a byte-identity that held at base

**Lead.** The only key change at warning level is in verify. SC2034 "SC_PASS appears unused" moved from base:953:9 to :1001:32. shellcheck anchors SC2034 on the last assignment, and the last `SC_PASS=0` is now the r17 line `if [ "$krc" != 1 ]; then SC_PASS=0; …`.

Intersecting the r17 hunks (`git diff -U0 5fa6017 ddb7347`) with the functions shellcheck reports as SC2329 "never invoked" at ddb7347 gives:

| file | r17 lines | never-invoked function | why it can never run |
|---|---|---|---|
| tools/souji-verify.sh | 985, 1000–1001 | `second_check()` 976–1004 | It is inside `if [ "$S18_KIND" = quarantine ]` (895–1005). `S18_KIND=verify` is set unconditionally at :526, the only assignment. No caller in the file, and `SC_PASS` has no reader (SC2034). |
| tools/souji-vault-verify.sh | 1192, 1204–1206, 1208 | `second_check()` 1183–1212 | Same guard (1102–1213). `S18_KIND=vault` at :728 is the only assignment. No caller, no `SC_PASS` reader. |
| tools/souji-vault-verify.sh | 453 (one **blank line** inserted) | `try_pushed()` 450–474 | Redefined at top level at :894, before the main flow at :1751. This is a redefinition-shadowed site. |
| tools/souji-quarantine.sh | 1015–1022 (`jj_keep_novel` check) | `try_pushed()` 994–1032 | No call site in the file: only the definition matches `try_pushed\b`. Zero dynamic dispatch (`declare -f`, `typeset -f`, `export -f`, `"$fn"`, `try_$`, `eval`: no matches). Quarantine takes receipts from the souji-verify.sh child (`VERIFY_BIN`, :176). |

The census has 1 SC2329 function and no r17 hunk inside it.

**Drift.** Extract each tool's `if [ "$S18_KIND" = quarantine ]; then … fi` block:
- At base, verify and vault-verify were **byte-identical**: 109 lines each, sha256 prefix `a27a9b029e6361c4` (`cmp` identical).
- At ddb7347 they differ: verify has 111 lines (`6575a84d46e7a4bd`), vault-verify has 112 lines (`30a4b24a3f7f3258`).

So the same head-history `jj_keep_novel` gate now exists in three shapes:
- **live quarantine** (:1339–1342): `else local kn=0; jj_keep_novel … || kn=$?; if [ "$kn" -ne 1 ]; then SC_PASS=0; …`
- **dead verify** (:1000–1001): `krc=0; jj_keep_novel … || krc=$?; if [ "$krc" != 1 ]; then SC_PASS=0; …` (unconditional, after the git-log test)
- **dead vault-verify** (:1204–1208): `touching=$(…) || touching=x; jj_keep_novel … || jjrc=$?; if [ -n "$touching" ] || [ "$jjrc" != 1 ]; then …; if [ "$jjrc" = 0 ]; then SC_EV="$SC_EV jj-keep-novel"; fi`

The whole inlined S18 layer, minus the `S18_KIND` line, already differed between verify and vault-verify at base (8 changed lines). The quarantine-only block was the one sub-block that was byte-identical.

**Impact.**
- There is no behavior change and no false SAFE.
- The verify 45/0 and vault 57/0 selftests cannot exercise these lines, so they must not be cited as C3 coverage.
- The next sync of the inlined guard now has three candidate shapes to choose from.
- If "dead shadowed sites" in C3 (b') covers the guarded or uncalled copies, the claim fails. If it means only redefinition-shadowed functions, it fails only on the whitespace line vault-verify:453. [INFERENCE: the claim's intended scope is not stated in the assignment.]

**Smallest fix (boring).** Drop the dead-site hunks:
- verify `@@ -940 +985 @@` and `@@ -954,0 +1000,2 @@`
- vault-verify `@@ -402,0 +453 @@`, `@@ -1128 +1192 @@`, `@@ -1140 +1204,3 @@` and `@@ -1141,0 +1208 @@`
- quarantine `@@ -936,0 +1015,8 @@`

This restores verify ≡ vault-verify for the quarantine block (sha prefix `a27a9b02…`). If L1 wants the dead copies to mirror live logic instead, paste the live quarantine `else` form byte-for-byte into both dead copies (one shape, not three), and correct the C3 wording either way.

### F2 — low (optional check SC2312, not exercised): `jj_keep_novel` treats a failed `git for-each-ref` as "nothing novel"

The function is byte-identical in all three tools: verify:241–256, vault-verify:433–448, quarantine:977–992. Its first line is:

```bash
[ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null)" ] || return 1
```

(verify:243, vault-verify:435, quarantine:979). SC2312 (`-o all`) flags it because the substitution discards git's exit status. A failing `for-each-ref` produces empty output and `return 1`. That contradicts the function's own contract: "Returns 0 novel, 1 nothing novel … and 2 when git itself failed, so the caller keeps its existing history-unverifiable path" (vault-verify:430–432; same wording ends at verify:240). The failure direction is fail-open (keep commits are ignored).

The risk is low on the live path. verify:719 and vault-verify:914 call it only after `git log … HEAD --branches --not --remotes` has succeeded (verify:710), so refs were just readable. [INFERENCE: I found no realistic case where for-each-ref fails alone. Not exercised: ALLOWED-EXEC does not cover running tool code.]

Smallest fix (same single query for plain repos):

```bash
local repo=$1 rel=$2 c obj known keep
keep=$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null) || return 2
[ -n "$keep" ] || return 1
```

## Triaged non-findings (optional checks on r17 lines)

- **census SC2310 delta** (`-o all`). The keys appear "added" at :864, :907, :925, :949, :967 (`guard_git_files … || soft=1`) only because the line text changed. Base had SC2310 at the same five sites (base:790, :831, :849, :873, :891, `… || exit 2`), so errexit was already off inside the guard. `guard_git_files` (:542–579) does not rely on errexit:
  - a stat failure is handled explicitly (:549, `continue`)
  - every refusal calls `protected_fail`, which runs `exit 2` (:556, :564, :573)
  - an `exit` inside an `||` operand still ends the run

  So `|| soft=1` can only see the info/attributes soft returns (:560–562 and :569–571). No weakening of D2 "other guards keep exit 2".
- **quarantine SC2312 at :548 and :573** (`emit CMD … "$(q_jj_commit_recipe …)"`): `q_jj_commit_recipe` (:245) only calls `printf`, so nothing meaningful is masked. The verify:1293 and quarantine :1694–1733 SC2312/SC2310 hits are selftest-only. All three receipt tools run under `set -euo pipefail` (verify:78, vault-verify:64, quarantine:158). The `jj_keep_novel … || rc=$?` SC2310 sites capture rc on purpose.
- **vadv54-harness.sh P6 stub change** (lines 173 and 270–283): `mkdir` stub, then `trap 'rmdir …' EXIT`, run, `rmdir`, `trap - EXIT`. It is the only `trap` in the file at either rev, so nothing is clobbered. `dir_digest` prunes `./.git`, so P6_DIG does not depend on the stub. Lint-clean at every severity.
- **Optional-check totals** (`-S style -o all`):

  | file | base | new |
  |---|---|---|
  | census | 1230 | 1336 |
  | verify | 1134 | 1229 |
  | vault-verify | 1405 | 1493 |
  | quarantine | 1487 | 1669 |
  | harness | 514 | 516 |
  | fixture | — | 620 |

  The added keys are almost entirely SC2250 (prefer braces) and SC2292 (prefer `[[ ]]`), which match the existing style. Every SC2310/SC2312 on r17 lines in the four tools was reviewed: F2 plus the items above.

## Commands run (outputs condensed; full outputs in this seat's transcript)

1. Extraction into /var/tmp/souji-r17-RevShellcheckAll/{new,base}/:

   ```bash
   git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <rev>:<path> > /var/tmp/souji-r17-RevShellcheckAll/<side>/<basename>
   ```

   The first attempt used `git show --output=`, which does not apply to blob display: it wrote 0-byte files, so I re-extracted with a redirect. `wc -l`:

   | side | census | verify | vault-verify | quarantine | fixture | harness |
   |---|---|---|---|---|---|---|
   | new | 2065 | 1419 | 1763 | 1839 | 769 | 555 |
   | base | 1877 | 1316 | 1632 | 1677 | ABSENT (new in r17) | 547 |

   sha256 of the new copies:
   - census `688ff8ad…`
   - verify `92743004…`
   - vault-verify `bbca35a1…`
   - quarantine `24c7cf05…`
   - fixture `6792df99…`
   - harness `b55df92d…`
2. `bash -n <f>`: rc 0 ×11.
3. `shellcheck -S warning <f>` (plus `-f gcc`, `-f json1`): the table above.
4. Key diff (code | level | message without "on line N" | trimmed source line) at `-S warning`: identical for census, vault-verify, quarantine and harness. verify differs only on the SC_PASS line (base `SC_PASS=0; SC_EV="$SC_EV head-history=FAIL"` → new `if [ "$krc" != 1 ]; then SC_PASS=0; …; fi`).
5. `shellcheck -S style <f>` with the same key diff: one removal (quarantine SC2329 `s18_evaluate_worktree_one`), otherwise identical.
6. `shellcheck -S style -o all <f>` with the key diff: the totals above.
7. `git diff --unified=0 5fa6017 ddb7347 -- tools/souji-{verify,vault-verify,quarantine}.sh | grep '^@@'`: hunks mapped onto the SC2329 extents (F1 table). Quarantine-only blocks were extracted by awk and compared with `cmp` and `diff` (F1 shas).
8. Static reachability: read and grep on the extracted copies (`S18_KIND`, `SC_PASS`, `second_check`, `try_pushed\b`, dispatch patterns). `stat` on the rc-file candidates listed above: none exist. `git ls-tree` for tracked rc files: none.

## Residual risk / verification gaps

- **Pipefail membership pipe** (`printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0`, at verify:253, vault-verify:445, quarantine:989). It runs under `set -o pipefail`. If `$known` is larger than the pipe buffer and grep matches early, printf gets SIGPIPE (rc 141), the pipeline fails and the function returns 0 ("novel"). That would be a spurious, fail-closed refusal of an identical-content predecessor in large histories, against C3 (b')'s "identical-content predecessors do not refuse". [INFERENCE] Not shellcheck-detectable and not exercised. It belongs to the SIGPIPE-pattern sentinel lane.
- **Masked commit lookup**: `obj=$(git rev-parse -q --verify "$c:$rel") || continue` (verify:252 and the mirrored lines) treats any git failure, not only "path absent", as a deletion. [INFERENCE] Not exercised.
- Results are pinned to ShellCheck 0.11.0. The other C1 matrix arms (a31642d, cc21683) were not linted by this seat: out of scope.
- I did not execute any tool or fixture code (ALLOWED-EXEC is limited to `git show`, `bash -n` and shellcheck). The F1 reachability argument is static: hard-coded `S18_KIND`, no call sites, no dynamic dispatch.
- Scratch /var/tmp/souji-r17-RevShellcheckAll/ is deleted after writing this report.
