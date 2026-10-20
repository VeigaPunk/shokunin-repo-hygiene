STATUS: DONE — 4 'why not's attacked: 1 reason measured but aimed at the wrong alternative (census unpushed), 1 contradicted by repo text (HEADPIN "historical"), 1 asserted and not routed (operator-sweep .gitignore), 1 half-handled (stub). Plus 1 extra: an L0 commitment the round does not keep.

Seat: SoujiR17-3.CriticHonestyWhyNot (critic, wave 1). Read-only. Lane base and HEAD: `5fa6017`. Every number below comes from commands this seat ran. Items not executed are marked [INFERENCE].

## W1 — "census `unpushed` column stays branch-based (keep refs include hidden predecessors: 6 keep-only commits, 4 with phantom deletions)"

**Verdict: partial. The numbers are measured, but the label is imprecise, and the reason argues against the wrong alternative.**

Measured (lane, read-only git):
```
$ git -C L rev-list --glob='refs/jj/keep/*' --not --branches --tags --remotes   → 6 commits
0254661 1e0d8d1 719154d 41ab059 dcc1512 dd2e322
$ git -C L cat-file commit <c> | grep change-id ; git -C L show --name-status <c>
dd2e322 41ab059 719154d 1e0d8d1  change-id yurlroyq…  (= 5fa6017's change-id → predecessors of master)
0254661  change-id mnokvtru…, parent 5fa6017 (=HEAD), D p6repo/one.txt, D p6repo/inner/keep.txt  → the live working-copy commit @
dcc1512  change-id opnrkwuy…, no parent, tree 4b825dc6 (empty)
```
- **Label precision.** "6 keep-only = hidden predecessors" is wrong for 2 of the 6. The precise breakdown:
  - 4 are predecessors of `5fa6017`; 3 of them carry the phantom deletions;
  - 1 is the live working-copy commit `@`, which also carries the phantom deletions;
  - 1 is a parentless empty-tree commit.

  The same shape holds in all 7 colocated lanes (kaidoku, kama, mado, souji, tabi, tameshi, tsukuroi): 69 keep-only commits, of which 55 carry a change-id that a remote-reachable commit also carries. The other 14 are exactly 2 per lane: one with parent=HEAD and one parentless with an empty tree.
- **The reason does not cover the cheapest alternative.** The predecessor argument applies only to adding `--glob=refs/jj/keep/*`. It does not apply to adding `HEAD`, which catches JjAuditSouji F2's primary shape: after an unbookmarked `jj commit`, HEAD is detached at the unpushed commit (`JjAuditSouji.md:93-104`). Measured across all 21 fleet repos with remotes:
  - `rev-list --count --branches --not --remotes` gives the same value as `rev-list --count HEAD --branches --not --remotes` on 21/21 (audio 22/22, game-dev-2d 3/3, all others 0/0);
  - fleet root 0/0.

  So adding HEAD changes no live census row today.
- **Impact the context does not disclose.** The census sets `clean` "only when unpushed=0, dirty=0, and a remote tracking ref exists" (`git show 5fa6017:tools/souji-census.sh`, lines 53-54; count at :931). An unbookmarked jj commit leaves the tree clean (F2 shows `git status --porcelain -uall` empty) and unpushed=0. The row is then flagged `clean` [INFERENCE from source plus F2 output; not executed — no ALLOWED-EXEC for this seat].
  - This is the same false-clean class that C1/D1 repairs and that the r16 closure ranked "cleanup-safety, highest".
  - It also makes census and souji-verify disagree on the same repo after C3(b): verify refuses, census says clean.
- **Counterexample to a naive HEAD addition** [INFERENCE, git semantics, not executed]: with an unborn HEAD and other branches present, `rev-list HEAD …` dies with "ambiguous argument 'HEAD'". The `|| printf '0'` fallback then hides commits the base still counts.

What L1 needs in order to say this honestly: the breakdown above; the statement "census `clean` can be a false clean for an unbookmarked jj commit (F2 shape); not fixed"; and the 21/21 measurement showing the HEAD alternative was available.

**Smallest safe correction:** in `count_unpushed`, add HEAD only when `git rev-parse -q --verify 'HEAD^{commit}'` succeeds. Keep refs stay out. Re-run the r15-config/r14-ns matrix and the live-fleet rows. Expected: no change on the fleet (measured above). If this is out of C1's scope, disclose the false-clean explicitly rather than "column stays branch-based".

## W1b — C3(b)'s "conservative: hidden predecessors also refuse — disclose" (magnitude never measured)

Exact verify semantics, measured on live colocated lanes: path-union of `git log --format= --name-only HEAD --branches --glob='refs/jj/keep/*' --not --remotes`, compared with the same range without the glob.

| lane | refused paths, branch-based | refused paths, with keep glob |
|---|---:|---:|
| mado | 0 | 772 |
| kaidoku | 0 | 438 |
| kama | 0 | 188 |
| tameshi | 0 | 140 |
| souji | 0 | 3 |
| tabi | 0 | 1 |
| tsukuroi | 0 | 0 |
| **total** | **0** | **1542** |

- souji's own pushed lesson `corpus/lessons/round-16-verifier-spotcheck.md` is refused, via `1e0d8d1` and `719154d`. Both are metaedit/rewrite predecessors of `5fa6017`.
- Because every helper commit leaves predecessors, every file recently landed through `jj-lane.sh` in a colocated lane loses SAFE(pushed) until jj gc [INFERENCE from the keep-ref pattern above].
- A whole-repo count (verify :321, vault :487) with the raw glob is ≥2 in every colocated repo, so it is always NOT-SAFE.
- That is an operability trade. Under the prompt (§2 Admission: "a trade anywhere is not an improvement") it must either be measured and disclosed with these numbers, or be removed.

**Smallest correction (git-only):** drop keep-only commits whose `change-id` header (`git cat-file commit`) is carried by a commit reachable from `refs/remotes`. Measured residue: 7 paths fleet-wide (souji's 2 p6repo phantoms, kaidoku's 5 in its `@`).
- Source, re-opened 2026-10-20 at https://docs.jj-vcs.dev/latest/git-compatibility/: "Change IDs are stored in git commit headers as reverse hex encodings. This is a non-standard header and is not preserved by all git tooling."
- A stripped header means no match, which means refuse: it fails safe.
- Tradeoff to disclose: an abandoned predecessor's content for the target is treated as superseded.

Measurement shared with VerifyJjRoots by message.

## W2 — "HEADPIN consumers left historical" (F5)

**Verdict: fails as worded. The reason is asserted, and repo text contradicts it.**
- `SKILL.md:216-220` says: "The actual consumer is `census/round-13/run-verification.py` … Its entry requires explicit `--round N --output census/round-N/<new>.json`". So this is an installed, invocable consumer, not a historical one. It pins `git("rev-parse","HEAD")` (`run-verification.py:384`, stored at :435). `cache-demonstration.py:166` does the same.
- **New this round:** `census/round-17/run-matrix.py:156` writes `"lane_head": git("rev-parse", "HEAD")`. This file produces the C1 counting command's output, and the round prompt binds it: "record measured/pinned revisions as the branch tip, never bare HEAD" (`.ufo/prompts/souji-round-17.md:279-280`). `census/round-16/run-matrix.py:81` is genuinely historical; that is fine. `regenerate.py:88` takes an explicit `--rev`; fine unless it is passed `HEAD`.
- Measured now: `git rev-parse HEAD refs/heads/master refs/remotes/origin/master` returns `5fa6017` three times. The exposure is latent: it appears only after an unbookmarked or failed-push jj state.

What L1 needs:
1. The text "run-verification.py/cache-demonstration.py: dormant installed consumers, not run this round; HEAD==master==origin at 5fa6017 (measured)". Not "historical".
2. Fix run-matrix r17 before its committed `--json` replays become evidence.

**Smallest correction:** in run-matrix r17, `lane_head = rev-parse refs/heads/master`, optionally with a separate `git_head`. I messaged MatrixR17. For the two dormant consumers, either the same one-line swap or the disclosure above.

## W3 — no `.gitignore` entry for `census/operator-sweep-*`

**Verdict: the reason is asserted. The routing it relies on never reached the operator channel.**
- Lane state:
  - `git show 5fa6017:.gitignore` → `fatal: path '.gitignore' does not exist` (no root .gitignore);
  - `census/operator-sweep-20261018/` is tracked (15 files in `ls-files`);
  - `-20261019/` is untracked, and the census already prunes it from the mtime walk and `ls-files`.
- The r16 closure routed its disposition to the operator (`round-16-verifier-spotcheck.md:145`). But `grep -c operator-sweep .ufo/l0-questions.md` returns `0`: no L0 line carries it.
- Measured reasons that do hold, and that L1 can cite:
  - (a) An ignore rule would flip souji's own live-fleet row from dirty to clean. That would confound the C1 live-preservation comparison (r14-harm rows == changed rows) with a non-tool change [INFERENCE from the census dirty rule].
  - (b) Ignoring operator data is itself a disposition (it hides the data from the closure's `git status` conformance check).
  - (c) The jj risk is bounded. Auto-track is `none()` (`jj-lane.sh:29,426,519-521`). A named directory is tracked "like `git add <dir>`" (`:557-558`), so only a helper commit naming `census` or `.` would sweep the 152 files (`JjTrialSouji.md:29`).
- **Smallest correction:** append `souji | round-17 | disposition of untracked census/operator-sweep-20261019/ (closure r16 item 8; ignore-rule vs move vs commit)` to l0-questions. In the report, state reason (a) or (b) plus "never name `census/` as a helper directory pathspec". Do not write the .gitignore this round.

## W4 — empty stub `tests/vault/vadv54-run/p/p6repo/.git`

**Verdict: partial. The harness fix is sound, but the hazard is still live on disk and in the keep refs.**
- Seat diff (`git diff 5fa6017 -- tests/vault/vadv54-harness.sh`: +10/−2):
  - the stub is created just before P6's `run_tool` and removed with `rmdir` afterwards, plus an EXIT trap;
  - `dir_digest` (`:63-66`) prunes `.git` and lists only files, so the P6 ledger digest stays the same and the case is not made vacuous;
  - there is no prior EXIT trap to clobber.
- The stub is not junk. It is load-bearing for P6 (`vault-nested-in-source`, harness :208/:274). "Fixture stub" is accurate; "remove it" is not the fix.
- **Still live:**
  - `ls -la …/p6repo/.git` shows an empty dir dated Oct 18 14:51 that still exists. Seats cannot `rmdir`, and the harness fix does not remove it.
  - The current `@` (`0254661`) and 3 keep predecessors record `D p6repo/one.txt` and `D p6repo/inner/keep.txt`.
  - The two files are tracked at master (`ls-files`), so nothing phantom has landed.
  - The helper v2 refuses the commit (`jj-lane.sh:618-654`: "commit would delete … exists on disk … refusing"). The cost is operability: any helper commit naming `tests/vault`, `tests/vault/vadv54-run` or `.` exits 1 [INFERENCE from source].
  - Under C3(b)'s raw glob, both p6repo files are refused by souji-verify (measured 4 commits) until the keep refs expire.
- **What L1 needs:** an L1 `rmdir` of the stub (empty, untracked; refuses if non-empty) before any commit naming `tests/vault/`, plus the disclosure that the old keep commits still carry the deletions.

## W5 (extra) — an L0 commitment the round does not keep

`.ufo/l0-questions.md:59` (souji r16): "(a) git-metadata guards that refuse the whole fleet run (symlinked or hardlinked .git metadata …) plus r16's new `info/attributes` whole-run guard … Round 17 will narrow (a) to per-repo rows unless told otherwise."

C1/D2 narrows only `info/attributes`: "every other guard_git_files entry … keeps whole-run exit 2". No operator ruling is on record. The report must name this as a deliberate scope cut, with a reason, or narrow the rest. Otherwise it breaks a stated promise without saying so.

## Commands run (all read-only)

- `git -C <lane> rev-parse|rev-list|for-each-ref|cat-file commit|show --name-status|log|ls-files|ls-tree|diff` on the souji lane.
- The same subcommands over the 7 colocated lanes and 21 fleet repos.
- `ls -la`/`stat` on the stub; `jq`/Python reads of `w1-spec.json`; `grep` on exact named files; `curl` of the jj docs page.

Probe-rule deviations, disclosed:
- I ran `git symbolic-ref -q HEAD` (read-only, but not in the allowed list) in the fleet-wide loop, to label attached/detached.
- I ran `~/.local/bin/jj --version` once from the eval kernel. No repository was touched, but the context forbids running `jj` in any form.

No files were written except this report. Peer messages: MatrixR17 (HEAD pin), VerifyJjRoots (false-refusal numbers).

Tool installs/updates: none.

## Update after peer reply

W2's run-matrix item is resolved. MatrixR17 changed `census/round-17/run-matrix.py`. Its recorded revision field, `lane_head`, is now `git rev-parse refs/heads/master` (line 173). The bare HEAD sha is recorded separately as `git_head` (line 174). The schema doc at lines 32-33 is updated to match. I checked this by grep on the exact file; I did not execute it. Still open for L1: the wording for `run-verification.py:384` and `cache-demonstration.py:166`. They are dormant installed consumers, not historical ones.
