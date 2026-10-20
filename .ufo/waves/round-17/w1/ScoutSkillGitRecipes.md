STATUS: DONE — static audit of all 12 instruction files: 6 git-write instructions (+1 echo) need a colocated branch, `@{u}` and `branch --show-current`/`--abbrev-ref` are absent, HEAD-as-measured-commit has 0 permissive instructions and 1 under-specified field; 4 adjacent read-side recipes are jj-blind.

Seat `SoujiR17-3.ScoutSkillGitRecipes` · round 17 wave 1 · 2026-10-20 · lane `souji-shokunin` · static, read-only. No file in the lane was written except this report. No `jj` subcommand, no git write, no tool run was executed in the lane or any fleet repo. No installs.

## 1. Verdict per asked category

| asked category | instructions found | verdict |
|---|---|---|
| run a git write (add/commit/mv/rm/push/stash/reset/checkout) | **6 real instructions + 1 echo** (§3) | **fails under colocation** for 5 of 6; 1 (`worktree lock`) is safe |
| resolve `@{u}` | **0 instructions**; 1 **prohibition** (`knowledge/jj-colocation-receipts.md:23`) | holds — no change |
| `branch --show-current` / `--abbrev-ref HEAD` | **0 occurrences** (any form) | holds — no change; and it would return literal `HEAD` here (§2) |
| pin `HEAD` as a measured commit | **0 instructions**; 2 prohibitions (`SKILL.md:210`, `QUALITY.md` Q20); field derivation unstated (§5) | **partial** — one gap to close |

The one sharpest defect is not a stray command but a **criterion that rejects the correct command**: `QUALITY.md:31` Q7's test clause requires the recorded commit to name "the `-c` guard", which a `jj-lane.sh commit` cannot contain. As written, Q7 forces the git path in a colocated lane.

## 2. Observed live state (read-only) — why this matters now

```
$ stat -c '%n %F' .jj .git
/home/vgpnk/Projects/shokunin/souji-shokunin/.jj directory
/home/vgpnk/Projects/shokunin/souji-shokunin/.git directory
$ git -C . rev-parse --abbrev-ref HEAD
HEAD
$ git -C . rev-parse HEAD
5fa6017ddcae9f6bd4412df44765f6360cb16294
$ git -C . rev-parse --verify refs/heads/master
5fa6017ddcae9f6bd4412df44765f6360cb16294
$ git -C . rev-parse --verify refs/remotes/origin/master
5fa6017ddcae9f6bd4412df44765f6360cb16294
$ git -C . symbolic-ref refs/remotes/origin/HEAD
refs/remotes/origin/master
$ git -C . for-each-ref --format='%(refname)' 'refs/jj/keep/*' | wc -l
8
$ git -C . for-each-ref --format='%(refname)' refs/heads refs/tags refs/remotes | wc -l
3
$ git -C . rev-list --count --branches --not --remotes
0
$ git -C . rev-list --count --branches --glob='refs/jj/keep/*' --not --remotes
6
$ git -C . rev-list --count HEAD --branches --not --remotes
0
$ git -C . rev-list --count HEAD --not --all
0
$ for d in kama mado tameshi souji; do ... .jj present ...; done
kama colocated / mado colocated / tameshi colocated / souji colocated
```

Facts that change the reading of every recipe below:

1. **This lane is colocated and HEAD is detached.** `--abbrev-ref HEAD` prints `HEAD`; any branch derivation by that route yields the literal string `HEAD`.
2. **The branch-based unpushed query is blind here.** `--branches --not --remotes` = 0 while adding the keep refs as heads = 6. Those 6 are hidden predecessors/keep-only commits, exactly the conservative-refusal case C3(b) declares.
3. **`--not --all` is vacuous for a keep-only head** (`HEAD --not --all` = 0), so it cannot grant durability (C3(a)).
4. **Three other lanes are already colocated** (kama, mado, tameshi), so souji's *target* repos are not all plain git.

Helper source read for the replacements (`/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh`, v2 per the round-17 contract):

- usage `:52-61`, `landed <hash>` is the only citable line `:58`; identity `--as <id>`/`-m` required `:500-503`, `:517`
- refuses non-clone `:76`, the fleet root `:76-80`, non-`.jj` repos `:510`, missing `snapshot.auto-track="none()"` `:519-521`
- path guards `:528-534` (escape, `.git`/`.jj`, `.ufo`/`.ufo/state`/watchdog); 10 MiB cap `:541`
- **admits a missing path present in the branch tip** `:543-545` (this is the v2 deletion/rename fix); else `warn: skipping missing path` `:548`
- commits with `jj commit -m "$msg" -- "${fs_req[@]}"` `:604-605`; parent-must-be-tip guard `:612-616`; changed-path-outside-request guard `:621-637`; **refuses a committed deletion of a path that still exists on disk** `:650-654`; bookmark set `:657`; push `:667` → `jj git push` `:350`, `:695`
- `state` line shape `:181`: `state branch=… local=… remote=… ahead=… behind=… head=attached|detached tracked=… untracked=…`
- the helper contains **no `git commit`/`git add`/`git mv`/`git rm`** (`grep -nE '\bgit\b[^|]*\b(commit|add|mv|rm|push|checkout|reset|stash)\b'` → only comments plus `jj git push/fetch`)

Quarantine note: the helper's driver-runtime guard is `.ufo|.ufo/state|.ufo/state/*|.ufo/watchdog.log` (`:532-534`); the quarantine root `.ufo-quarantine/…` does **not** match, so quarantine paths are committable through the helper.

**Scope rule used below.** `SELF` = this lane (`souji-shokunin`, colocated). `TARGET-jj` = a cleaned repo with `.jj`. `TARGET-plain` = the fleet root or any repo without `.jj` (the helper refuses the fleet root by literal path, `:76-80`). The owning repo of a quarantine is the one place souji writes to a target, so the conditional is mandatory there.

## 3. Instructions that tell an agent to run a git write

### A1 — `SKILL.md:58` (removal flow step 3) · scope TARGET (self/fleet/lane)
> `3. \`git mv\` (or plain \`mv\` for untracked) into \`<repo>/.ufo-quarantine/<utc-date>/...\` — quarantine is a normal commit in the owning repo, made with the guarded form in the Pre-quarantine checklist.`

Why it fails: in `TARGET-jj`, jj ignores the staging area and resets the index on its next mutation, so `git mv` is not a durable staging signal (`knowledge/jj-colocation-receipts.md` §5; JjAuditSouji F4). Nothing in the sentence requires **both sides of the move** in the commit, which is the exact half-landing shape (old path stays in the pushed tree — JjAuditSouji F1, JjTrial). The guarded git form also has no push/landed verification.

Replacement:
> `3. Move into \`<repo>/.ufo-quarantine/<utc-date>/...\` with plain \`mv --\` (never \`git mv\`), then commit on the path that matches the owning repo:`
> `   - \`<repo>/.jj\` exists: \`/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh commit <repo> --as souji -m '<receipt class> <evidence pointer>' -- <old repo-relative path> .ufo-quarantine/<date>/<old path>\` (BOTH paths), then \`jj-lane.sh push <repo>\`; cite only the printed \`landed <hash>\`.`
> `   - no \`.jj\` (fleet root or plain lane): the guarded git form in the Pre-quarantine checklist.`
> `   A helper commit names every changed path; the source may be absent from the worktree only because it is present in \`refs/heads/<branch>\` (jj-lane.sh:543-545).`

### A2 — `SKILL.md:61` (removal flow step 6) · scope TARGET
> `6. Delete from quarantine. \`pushed\` artifacts need no hold beyond the second check.`

Verdict: **implied write, no command named.** In a tracked owning repo the deletion is a second index/history change and is left uncommitted by this step. Not a named git-write instruction, so no quote to replace; if the flow is made explicit, the jj form is a helper commit naming the removed quarantine path (the helper refuses a committed deletion when the path still exists on disk, `:650-654`; a v2 pure deletion lands — `:543`).

### A3 — `SKILL.md:123` (Pre-quarantine checklist) · scope BOTH
> `- [ ] Commit guarded and scoped: \`git -C <repo> add -- <approved paths>\` then \`git -C <repo> -c maintenance.auto=false commit -- <same approved paths>\` — never \`git add -A\` / \`.\``

Why it fails: it is the **only** commit recipe, so a colocated owning repo (kama, mado, tameshi, or this lane) gets the wrong path; `<approved paths>` does not say "both sides of a move"; `git add` before a jj call is exactly what §5 of the jj entry forbids.

Replacement (three items, keep the plain-git line verbatim for its scope):
> `- [ ] Right repo: \`git -C <repo> rev-parse --show-toplevel\` prints the owning repo (never trust \`cd\`); for a colocated repo also require \`jj-lane.sh state <repo>\` to report the expected \`branch=\`.`
> `- [ ] Colocated owning repo (\`<repo>/.jj\` exists): \`jj-lane.sh commit <repo> --as souji -m '<receipt class + evidence pointer>' -- <approved paths>\` naming every changed path, both sides of a move; then \`jj-lane.sh push <repo>\`; cite only \`landed <hash>\`. No \`git add\` before or after a jj call.`
> `- [ ] Plain owning repo (no \`.jj\`, including the fleet root): \`git -C <repo> add -- <approved paths>\` then \`git -C <repo> -c maintenance.auto=false commit -- <same approved paths>\` — never \`git add -A\` / \`.\``

### A4 — `AGENTS.md:20` (operating rules) · scope SELF
> `- Commit as \`souji-shokunin <souji@shokunin.local>\`.`

Why it fails: it names an identity but no path, and in this lane a raw `git commit` lands on a detached HEAD without moving `refs/heads/master`; the commit then exists only as a jj-imported head (keep-ref-held at worst), invisible to `--branches --not --remotes` (§2, measured 0 vs 6). The helper refuses to sweep such a stranded sibling (`working copy has changes on a non-tip base; refusing to sweep or strand work`, `:584-586`) and its push preflight rejects a foreign author/committer in the push range (`:216-230`), so a wrong-identity raw commit blocks the next push.

Replacement:
> `- Commit through the lane helper: \`jj-lane.sh commit <lane> --as souji -m '<message>' -- <paths>\`. It stamps author AND committer \`souji-shokunin <souji@shokunin.local>\`, and the same identity is the push gate. A raw \`git commit\` in this colocated lane is not a landing path.`

### A5 — `corpus/QUALITY.md:31` Q7 · scope BOTH
> `| Q7 | Every lane or hygiene commit: (a) runs \`git -C <repo> rev-parse --show-toplevel\` and confirms the intended repo first; (b) stages only named paths (\`commit -- <paths>\`), never \`add -A\` or \`.\`; (c) runs with \`-c maintenance.auto=false\` so git's own pruning cannot ride along. | commits | the commit command recorded in LOG names its pathspec and the \`-c\` guard; \`git show --stat --format= <hash>\` lists only approved paths | … |`

Why it fails: (c) is asserted for **every** lane commit, but a helper commit runs `jj commit` and never enters git's `builtin/commit.c`, so the `-c` guard has no meaning there; worse, the **test** makes "names … the `-c` guard" a pass condition, so the correct helper command cannot pass Q7. (b) is weaker than the helper's enforcement and omits "both sides of a move".

Replacement (criterion text + test):
> `| Q7 | Every lane or hygiene commit: (a) confirms the intended repo first (\`git -C <repo> rev-parse --show-toplevel\`; for a colocated lane also \`jj-lane.sh state <repo>\`); (b) stages only named paths — \`jj-lane.sh commit … -- <paths>\` in a \`.jj\` repo, \`commit -- <paths>\` in a plain repo, never \`add -A\` or \`.\`; (c) on the git path, runs with \`-c maintenance.auto=false\` (a helper commit runs \`jj commit\` and cannot carry that guard). | commits | the commit command recorded in LOG names its pathspec and, on the git path, the \`-c\` guard; \`git show --stat --format= <hash>\` lists only approved paths | … |`

Note (a)'s `rev-parse --show-toplevel` is read-only and stays correct under jj — no change there.

### A6 — `PROVINCE.md:11-13` (Owns, lane-repo hygiene) · scope TARGET-jj / TARGET-plain
> `  \`.scratch/\`, dead worktree *metadata* (\`git worktree prune\` after the commits are proven pushed or empty), duplicate configs, stale generated output with no live references.`

Why it fails: `git worktree prune` is a git-metadata write and is fine in a colocated repo (jj does not manage linked worktrees), but "proven pushed" is not specified and the tools' current test (`--not --all`) counts `refs/jj/keep` as durable (C3(a), JjAuditSouji F3: `HEAD --not --all` empty for a keep-only head). An absent registration whose head is keep-only would be pruned on a vacuous proof.

Replacement:
> `  \`.scratch/\`, dead worktree *metadata* (\`git worktree prune\` only after the registration head is reachable from a durable root — \`refs/heads\`, \`refs/tags\`, \`refs/remotes\` — never \`--not --all\` and never \`refs/jj/*\`; a keep-only head is NOT-SAFE), duplicate configs, stale generated output with no live references.`

### A7 — `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:22` (echo) · scope BOTH
> `SKILL removal-flow step 3 makes quarantine a normal owning-repo commit (\`SKILL.md:40-47\`); its Pre-quarantine checklist already guards the scoped commit with \`git -C <repo> -c maintenance.auto=false commit -- <approved paths>\` and pins registrations with \`git worktree lock --reason\` (\`SKILL.md:94-100\`).`

Verdict: descriptive echo of A3, but it is the corpus entry an agent will follow, and its line references are **stale**: the removal flow is `SKILL.md:54-61` (step 3 at `:58`), the checklist is `:118-124`. Replacement text:
> `SKILL removal-flow step 3 makes quarantine a normal owning-repo commit (\`SKILL.md:58\`): colocated repos commit through \`jj-lane.sh commit … -- <old> <new>\`, plain repos through the guarded \`git -C <repo> -c maintenance.auto=false commit -- <approved paths>\` (\`SKILL.md:123\`); registrations are pinned with \`git worktree lock --reason\` (\`SKILL.md:124\`). The \`-c\` guard applies to the git path only — a helper commit runs \`jj commit\` and never enters git's auto-maintenance path.`

### A8 — safe git writes, keep (no change)
- `SKILL.md:124` — `git -C <repo> worktree lock --reason "<why>" <worktree-path>`: git-metadata write, jj-independent, and it is the mitigation the auto-maintenance entry relies on. Keep.
- `SKILL.md:122` — `git -C <repo> rev-parse --show-toplevel`: read-only; correct under jj.
- `SKILL.md:91-97` and `knowledge/quarantine-same-filesystem-rename.md:45` — **descriptions** of `git commit`/`git mv`, not instructions (`:45` also carries stale tool lines: installed `git mv` is `:518`, `git rm --cached` `:566`, per JjAuditSouji §2). No recipe to change; the second is a citation drift only.

## 4. `@{u}` — 0 instructions

```
$ grep -nE '@\{u\}' SKILL.md PROVINCE.md AGENTS.md corpus/QUALITY.md corpus/README.md corpus/knowledge/*.md
corpus/knowledge/jj-colocation-receipts.md:23: … any check that resolves `@{u}`, reads `symbolic-ref HEAD`, or assumes HEAD sits on a branch is wrong in a colocated lane.
```
The only hit is a **prohibition**. Verdict holds; no replacement needed. (The historical `@{u}` use is in `tests/fixtures/case-F3/make-fixture.sh:193`, outside this seat's file scope, per JjAuditSouji §F8.)

## 5. `branch --show-current` / `--abbrev-ref HEAD` — 0 occurrences

```
$ grep -nE 'show-current|abbrev-ref' <the same 12 files>
(no output; count=0)
```
Verdict holds. Positive forms already in use are correct: `jj-lane.sh state <dir>` prints `branch=`/`local=`/`remote=`/`head=`, and `git rev-parse --verify refs/heads/<branch>` (`jj-lane.sh:170`, `:555`) is the durable-tip form. This matters because `--abbrev-ref HEAD` returns the literal string `HEAD` in this lane (§2), so any future addition must not use it.

## 6. HEAD as a measured commit — 0 instructions, 2 prohibitions, 1 under-specified field

Occurrences of `HEAD` in decisions (20 lines; only these bear on measurement):
- `SKILL.md:210` — `Preserve the original declared revision: no fallback to a file-level revision or current HEAD.` (prohibition; correct)
- `QUALITY.md` Q20 — `retention preserves the original declared measured revision` (prohibition by implication; correct)
- `knowledge/jj-colocation-receipts.md:68-70, :93` — §9 `Evidence that records HEAD` + rule 6 `Do not pin \`HEAD\` in evidence` (prohibition; **candidate**, not installed behaviour)
- `SKILL.md:35` (`refs/remotes/origin/HEAD`) and `QUALITY.md:36` (detached worktree HEAD) are read-side/other, not measurement pins.

**The gap**: the positive derivation of `measured_commit` is nowhere stated. `SKILL.md:202-206` only says the record "declares … its own `measured_commit`", and Q25(b) only checks that the record "holds the bytes the record pins". With no positive rule, the two named consumers pinned HEAD — `census/round-13/run-verification.py:384` (`git rev-parse HEAD`) and `census/round-14/cache-demonstration.py:166` (`git rev-parse --verify HEAD`), cited from JjAuditSouji F5/§4.1 (not re-opened by this seat; those files are outside the static file list).

Smallest fix (one clause in two places):
- `SKILL.md:208-210` → `Derive a new record's \`measured_commit\` from the branch tip — \`git -C <lane> rev-parse --verify refs/heads/<branch>\`, recorded with the branch name; for a pushed observation use the helper's \`landed <hash>\`. \`git rev-parse HEAD\` is forbidden: in a colocated lane HEAD is detached \`@-\` (measured: \`--abbrev-ref HEAD\` → \`HEAD\`).`
- `QUALITY.md` Q25(b) test → add `and \`measured_commit\` must be reachable from \`refs/heads\`, \`refs/tags\` or \`refs/remotes\` (a keep-only or detached commit is not a measurement anchor)`.

## 7. Adjacent read-side recipes (not one of the four categories, same defect class)

These decide SAFE/NOT-SAFE; they are read-only, but under colocation they are the false-clean surface. Listed for the integrator, not as asked-category findings.

| file:line | quote (abridged) | jj defect | replacement |
|---|---|---|---|
| `SKILL.md:35` | ``AND no unpushed commit touches the path (`git log --branches --not --remotes --oneline -- <path>` empty …)`` | measured in this lane: 0 without keep heads, **6** with them | `git log --format=%H HEAD --branches --glob='refs/jj/keep/*' --not --remotes -- <path>` empty; keep-only heads and hidden predecessors refuse (disclose) — aligns with C3(b) and `jj-colocation-receipts.md` rule 5 |
| `SKILL.md:77-78` | `` `git log --branches --not --remotes --oneline` in the owning repo is non-empty `` | same query, same blindness | same command as `:35` |
| `SKILL.md:113` | ``(`git log --not --remotes --oneline -- <path>` empty)`` | **weaker than `:35`** (no `--branches`, no explicit positive rev; starts at HEAD) | make it identical to `:35`; a checklist must not be laxer than the receipt it guards |
| `PROVINCE.md:11` | "commits are proven pushed" | reserved-roots proof unspecified; today's tools use `--not --all` | durable-root proof (see A6) |
| `SKILL.md:89-90` | `` `git worktree list` + `git log <wt-sha> --oneline | head` — … commits not on any branch is NOT-SAFE `` | safe direction (keep-only looks "not on a branch" → NOT-SAFE) | none |
| `QUALITY.md` Q12 | `git fsck --unreachable --no-reflogs | wc -l` before/after | keep refs make jj-held commits *reachable*, so fsck residue under-reports jj-held work | keep as residue accounting; never as a safety signal (already implied by "recoverable only until `gc.pruneExpire`") |

`SKILL.md:35`'s default-ref resolution is jj-correct as written: existing refs only, `refs/remotes/origin/HEAD` (present here → `refs/remotes/origin/master`), no fetch, no local branch. No change needed beyond the keep-glob clause.

## 8. Coverage and method

Files read in full or in every decision-bearing range (12; line counts at read time):

| file | lines | instructions found |
|---|---|---|
| `SKILL.md` | 240 | A1 :58, A2 :61 (implied), A3 :123, A8 :124 |
| `PROVINCE.md` | 93 | A6 :11-13 |
| `AGENTS.md` | 20 | A4 :20 |
| `corpus/QUALITY.md` | 65 | A5 :31; §6 Q20/Q25 |
| `corpus/README.md` | 203 | none (46 `fetch/merge/rebase` are research questions, not recipes) |
| `knowledge/git-auto-maintenance-prunes-worktrees.md` | 27 | A7 :22 (echo) |
| `knowledge/git-grace-periods-and-expire-to.md` | 37 | none |
| `knowledge/git-repo-structure-readonly.md` | 46 | none (read-only probe) |
| `knowledge/dupe-finders-detect-then-act.md` | 40 | none |
| `knowledge/quarantine-same-filesystem-rename.md` | 58 | A8 (description only, :45) |
| `knowledge/trash-spec-restorable-quarantine.md` | 39 | none |
| `knowledge/jj-colocation-receipts.md` | 124 | prohibitions :23, :93; rule 5 :96-97; landed mid-session (13:35), covered |

Sweeps and counts (the negative carries its sweep):

```
grep -inE 'git[[:space:]-]+(add|commit|mv|rm|push|stash|reset|checkout|switch)\b' <12 files>   → 11 lines (incl. 5 in jj-colocation-receipts)
grep -nE '@\{u\}' <12 files>                                                                   → 1 (prohibition)
grep -nE 'show-current|abbrev-ref' <12 files>                                                   → 0
grep -nE '\bHEAD\b' <12 files>                                                                  → 20 (2 prohibitions, 1 remote-HEAD resolution, rest prose/reports)
grep -n 'measured_commit' <12 files>                                                            → 3 (SKILL:202, Q25, jj-colocation:23)
grep -nE '\bgit\b[^|]*\b(commit|add|mv|rm|push|checkout|reset|stash)\b' scripts/hyaku/jj-lane.sh → comments + `jj git push/fetch` only
```

Not done, by contract: no `jj` at all; no git write; no execution of `souji-census.sh`, `souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh` or any copy against a real directory; no read of `census/operator-sweep-20261019/`; no credential content. The helper's behaviour above is **source-read, not executed**. Installations/upgrades: none.

## 9. Smallest fix list (ordered by risk removed per line)

1. `SKILL.md:123` — add the colocated branch and the both-sides-of-a-move rule (A3). This is the commit an agent actually runs.
2. `SKILL.md:58` — replace `git mv` with plain `mv` + helper commit naming both paths (A1).
3. `QUALITY.md:31` Q7 — conditional (b)/(c) and stop requiring the `-c` guard of a helper commit (A5). Without this, the admission bar rejects the correct command.
4. `AGENTS.md:20` — restate the identity rule as the helper invocation (A4).
5. `PROVINCE.md:11-13` — durable-root proof for `worktree prune` (A6).
6. `SKILL.md:113` — make the pre-removal check identical to the `:35` receipt, keep glob included (§7).
7. `SKILL.md:208-210` + Q25(b) — name the positive `measured_commit` derivation (§6).
8. `knowledge/git-auto-maintenance-prunes-worktrees.md:22` — update command and stale line refs (A7).
9. If C3(b) lands the tool change, update `SKILL.md:35` and `:77-78` prose in the same commit; otherwise the prose (which wins only until the tools change, `SKILL.md:28`) will contradict installed behaviour.

## 10. Remaining unknowns (not established by this seat)

1. **Whether `jj git push` refreshes `refs/remotes/origin/<branch>`.** The helper reads that ref (`:170`, `:395`, "fetch first") but I did not execute a push; if it lags, `pushed` receipts in this lane stay conservative (`pushed-unverifiable`), never false-SAFE — a direction, not a measured fact.
2. `jj-colocation-receipts.md:64` cites the helper's deletion admission at `:544-549`; the `cat-file` test is at `:543-546` (v2). Its §8 also keeps the **v1** observation ("warned skipping missing path") next to the v2 source, which can read as "v2 still drops a named source path". Behaviourally harmless (§8's rule is "name both"), but the wording should say v1-was, v2-admits.
3. The same entry's `## Source rows to number` uses `S0??` placeholders (7 rows): unnumbered rows cannot be admitted against `corpus/SOURCES.md` row identity, and `corpus/README.md` has no index row for the entry yet. Entry status is `candidate`.
4. Helper v2's `jj commit -m … -- <fileset terms>` path and the `state` output were read, not run; no empirical claim about a live commit is made here.
