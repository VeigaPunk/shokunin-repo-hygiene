STATUS: DONE — `--all` roots every ref under `refs/` plus `HEAD` (git-rev-list, page stamp "last updated in 2.56.0", opened 2026-10-20), so `refs/jj/keep/*` are roots; this lane measures `--all`=58 vs `--branches --tags --remotes`=52, and the 6-commit gap is exactly the keep-only set.

# SrcGitRevAll — git-rev-list `--all` and the ref-selection family

Question: does `--all` mean all refs in `refs/` plus `HEAD` (hence `refs/jj/*`), and what are the exact
semantics of `--branches`, `--tags`, `--remotes`, `--glob`, `--exclude`?

Sources opened (web, 2026-10-20):
- https://git-scm.com/docs/git-rev-list — title "Git - git-rev-list Documentation"; footer serves
  **"git-rev-list last updated in 2.56.0"**.
- https://git-scm.com/docs/gitrevisions — footer serves **"gitrevisions last updated in 2.56.0"**.
- Corroboration: installed `/usr/share/man/man1/git-rev-list.1.gz`, `git version 2.56.0`
  (`pacman -Q git` → `git 2.56.0-1`), man header `.\" Date: 2026-09-27`. Every option paragraph I quote
  below is byte-identical in the installed roff (`zcat … | sed -n '275,345p'`).

## 1. The verbatim answer

> "Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>."

19 words. Location: § OPTIONS › Commit Limiting › `--all`, anchor
`#Documentation/git-rev-list.txt---all` (HTML id confirmed: `id="Documentation/git-rev-list.txt---all"`).

That is the whole rule. The page **never** names `refs/jj/*` or jj:
`grep -n -iE 'refs/jj|namespace' rev-list.txt` → no match; `refs/stash` appears once, only as a reflog
selector example (`refs/stash@{1}`, line 5189). So "`--all` includes `refs/jj/*`" is the general rule
applied to a ref name that happens to be under `refs/`, **not** a statement git makes about jj.

Corroborating example text on the same page (§ EXAMPLES, 20 words):
> "Print the list of commits authored by you in the past year, on any branch, tag, or other ref."

(the command it heads is `git rev-list --author=you@example.com --since=1.year.ago --all` — "or other ref").

## 2. Exact semantics, verbatim (all under § OPTIONS › Commit Limiting)

| option | verbatim text (page as served 2026-10-20) | words |
|---|---|---|
| `--all` | "Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>." | 19 |
| `--branches[=<pattern>]` | "Pretend as if all the refs in refs/heads are listed on the command line as <commit>." + "If <pattern> is given, limit branches to ones matching given shell glob. If <pattern> lacks ?, *, or [, /* at the end is implied." | 18 + 27 |
| `--tags[=<pattern>]` | "Pretend as if all the refs in refs/tags are listed on the command line as <commit>." + same pattern rule (page writes "If pattern lacks", without "the") | 18 |
| `--remotes[=<pattern>]` | "Pretend as if all the refs in refs/remotes are listed on the command line as <commit>." + "limit remote-tracking branches to ones matching given shell glob" | 18 |
| `--glob=<glob-pattern>` | "Pretend as if all the refs matching shell glob <glob-pattern> are listed on the command line as <commit>." + "Leading refs/, is automatically prepended if missing. If pattern lacks ?, *, or [, /* at the end is implied." (the stray comma after `refs/` is in the page) | 18 + 9 |
| `--exclude=<glob-pattern>` | "Do not include refs matching <glob-pattern> that the next --all, --branches, --tags, --remotes, or --glob would otherwise consider. Repetitions of this option accumulate exclusion patterns up to the next --all, --branches, --tags, --remotes, or --glob option (other options or arguments do not clear accumulated patterns)." | 18 |
| `--exclude` prefix rule | "The patterns given should not begin with refs/heads, refs/tags, or refs/remotes when applied to --branches, --tags, or --remotes, respectively, and they must begin with refs/ when applied to --glob or --all." + "If a trailing /* is intended, it must be given explicitly." | 31 / 11 |
| `--not` | "Reverses the meaning of the ^ prefix (or lack thereof) for all following revision specifiers, up to the next --not." | 20 |
| `--exclude-hidden=(fetch\|receive\|uploadpack)` | "Do not include refs that would be hidden by git-fetch, git-receive-pack or git-upload-pack by consulting the appropriate fetch.hideRefs, receive.hideRefs or uploadpack.hideRefs configuration along with transfer.hideRefs" + "This option affects the next pseudo-ref option --all or --glob and is cleared after processing them." | 31 / 18 |
| `--single-worktree` | "By default, all working trees will be examined by the following options when there are more than one (see git-worktree[1]): --all, --reflog and --indexed-objects." | 24 |

Semantic reading (each clause is the quoted text, nothing added):

- `--all` = `{refs/**}` ∪ `{HEAD}`. Since `refs/jj/keep/<oid>` is under `refs/`, it is in the set.
  `HEAD` is a member only because the sentence adds it explicitly — it is not under `refs/`
  (gitrevisions § Specifying Revisions › `<refname>` resolves `$GIT_DIR/<refname>` first, and lists
  HEAD, FETCH_HEAD, ORIG_HEAD, MERGE_HEAD, REBASE_HEAD, REVERT_HEAD, CHERRY_PICK_HEAD, BISECT_HEAD,
  AUTO_MERGE there; then "otherwise, refs/<refname> if it exists;").
- `--branches`/`--tags`/`--remotes` = exactly `refs/heads`, `refs/tags`, `refs/remotes`. No other
  namespace is named. A `<pattern>` without `?*[` gets `/*` appended, i.e. it is a prefix match.
- `--glob` = shell-glob over refs, with `refs/` prepended when missing (so `--glob=jj/keep/*` and
  `--glob=refs/jj/keep/*` are the same request).
- `--exclude` is **positional**: it prunes only the *next* pseudo-option, and repeated `--exclude`
  accumulate until that option. For `--glob`/`--all` the pattern must start with `refs/`; the trailing
  `/*` is **not** implied for `--exclude` (unlike the pseudo-options).
- `--not` applies to what follows it, and pseudo-options are "listed on the command line as
  <commit>", so `--not --branches --tags --remotes` subtracts those three sets.
- `--all` does **not** include reflog objects (`--reflog` is separate), alternate-repository ref tips
  (`--alternate-refs` is separate), or objects no ref reaches. Refs hidden by `transfer.hideRefs` /
  `*.hideRefs` are still included by plain `--all`; only `--exclude-hidden` consults them.
- Multi-worktree: `--all` examines **all working trees** by default (per the `--single-worktree`
  sentence), so per-worktree refs of sibling worktrees are in the set too, unless `--single-worktree`.

## 3. Observed on the live lane (read-only git verbs only; no jj, no writes)

Repo: `/home/vgpnk/Projects/shokunin/souji-shokunin` (jj-colocated, branch master, base 5fa6017).

```
$ git -C $R for-each-ref --format='%(refname)' | cut -d/ -f1-2 | sort -u
refs/heads
refs/jj
refs/remotes
$ git -C $R for-each-ref --format='%(refname)' 'refs/jj/keep/*' | wc -l
8
$ git -C $R for-each-ref --format='%(refname)' | grep -Ev '^refs/(heads|tags|remotes)/'
refs/jj/keep/0254661427750f47e04f20864c5091cfc74e2e0e
refs/jj/keep/1e0d8d1644cf18a0e02189bc27b33a5a6b55474c
refs/jj/keep/41ab059d7dd5c3465bb84d7049a87756cdc19926
refs/jj/keep/5fa6017ddcae9f6bd4412df44765f6360cb16294
refs/jj/keep/719154dc9d15ea25a0204ba12c35493526d6c1ed
refs/jj/keep/c46eabf80f4c5b34a6774cd8725a0787306ba754
refs/jj/keep/dcc1512e2a4f4db48de025081485223ac8ee8246
refs/jj/keep/dd2e3226864c182165c8c725b1d0ff3fbc3a37e1
```
(no `refs/stash`, no `refs/notes`, no `refs/bisect`; `.git/worktrees` does not exist, so the
`--single-worktree` widening does not bite this repo — `stat` → No such file or directory)

```
all=58                     git rev-list --count --all
trio=52                    git rev-list --count --branches --tags --remotes
heads=52                   git rev-list --count --branches
jjglob=58                  git rev-list --count --glob=refs/jj/keep/*
head_only=52               git rev-list --count HEAD
unique_beyond_trio=6       git rev-list --all --not --branches --tags --remotes | wc -l
keep_only_unique=6         git rev-list --glob=refs/jj/keep/* --not --branches --tags --remotes | wc -l
```

Per keep ref, commits not reachable from the durable trio (`rev-list --count <ref> --not --branches --tags --remotes`):
`1` for six refs; `0` for `refs/jj/keep/5fa6017…` (the base commit) and `refs/jj/keep/c46eabf…`.
This matches the context's "6 keep-only commits in this lane" exactly, and the 6 = 58 − 52 arithmetic.

Decisive pair, on keep-only commit `0254661427750f47e04f20864c5091cfc74e2e0e`:
```
not_all=0     git rev-list --count 0254661 --not --all
not_trio=1    git rev-list --count 0254661 --not --branches --tags --remotes
```
At `tools/souji-verify.sh:351` the code is
`uniq=$(git -C "$owner" log --oneline "$head" --not --all …)` and `uniq = 0` returns
`SAFE` / `metadata-prune`. So a worktree head held only by a jj keep ref is scored SAFE *because*
`--all` roots `refs/jj/keep/*` — exactly the C3(a) defect, now measured rather than argued.
With the durable trio the same head scores 1 unique and does not reach SAFE.

`--exclude` order and scope, measured (`rc` all 0, empty stderr):
```
52   git rev-list --count --exclude=refs/jj/keep/* --all      # exclude BEFORE the pseudo-option: applies
58   git rev-list --count --all --exclude=refs/jj/keep/*      # exclude AFTER: does not apply
58   git rev-list --count --exclude=HEAD --all                # accepted, no effect: HEAD survives
52   git rev-list --count --exclude='refs/*' --all            # refs/ pruned; HEAD alone roots 52
 0   git rev-list --count HEAD --not --branches --tags --remotes
```
So `--all --exclude=refs/jj/keep/*` is **not** a substitute for a durable root set: it cannot drop HEAD
(the page requires `refs/`-prefixed patterns for `--all`; HEAD is added by the `--all` sentence itself),
and the exclusion is silently positional.

Empty-namespace behaviour (the C3(b) "plain repos byte-identical" precondition):
```
 0  rc=0   git rev-list --count --glob=refs/nosuch/*                 # absent namespace: empty set, no error
52  rc=0   git rev-list --count HEAD --not --glob=refs/nosuch/*      # contributes nothing to --not
```

## 4. Contradiction check (item 3 of the ticket)

**No statement on either page contradicts the context's claim text.** Specifically not contradicted:
`--all` is broader than the durable trio (it is); `refs/jj/*` are in it (they are, by the `refs/` rule);
`--branches`/`--remotes` are `refs/heads`/`refs/remotes` (they are); `--glob=refs/jj/keep/*` is a legal,
additive root (it is). The page's own text *demonstrates* the hazard the claim names.

Two statements that **qualify** the premise "`--all` means all refs in refs/ plus HEAD" without
contradicting it — quote them wherever C3(a) is restated, because both cut the same way (wider, not
narrower):

1. "By default, all working trees will be examined by the following options when there are more than
   one (see git-worktree[1]): --all, --reflog and --indexed-objects." — in a multi-worktree repo
   `--all` also roots sibling worktrees' per-worktree refs, so it is a superset of "this worktree's
   `refs/` + HEAD". This lane has no `.git/worktrees`, so nothing here depends on it.
2. "This option affects the next pseudo-ref option --all or --glob and is cleared after processing
   them." (`--exclude-hidden`) — proves plain `--all` does **not** consult `fetch.hideRefs` /
   `transfer.hideRefs`: even refs hidden from transfer are counted as roots.

Explicit limits of what these pages establish (do not over-claim):
- Neither page says anything about `refs/jj/*`, jj, or any non-git tool.
- Neither page documents `git for-each-ref` patterns. The half of C3(a) that says an **all-refs
  `for-each-ref` roots list** must be narrowed (`tools/souji-verify.sh:809-813` runs
  `git for-each-ref --format='%(objectname)'` with no patterns, then
  `rev-list --count "$head" --not "${roots[@]}"`) is **not grounded by these two pages**. It is
  grounded instead by substituting the rev-list pseudo-options, which this row does pin.

## 5. Drafted SOURCES row (registry column order; L1 numbers it — next unused id is S051: 50 rows, max S050)

```
| S051 | git-rev-list(1), ref-selection pseudo-options — https://git-scm.com/docs/git-rev-list | docs | A | which refs `--all` and the durable-ref options root, and how `--glob`/`--exclude` narrow them, on Git 2.56.0; not for-each-ref pattern semantics | web manual "git-rev-list last updated in 2.56.0", opened 2026-10-20; installed git 2.56.0-1 roff (Date: 2026-09-27) agrees verbatim; § OPTIONS › Commit Limiting: --all, --branches, --tags, --remotes, --glob, --exclude, --exclude-hidden, --single-worktree, --not; § EXAMPLES (`--all`) | `--all` roots every ref under refs/ plus HEAD, so refs/jj/keep/* are roots; --branches, --tags, --remotes root exactly refs/heads, refs/tags, refs/remotes; --glob prepends refs/; --exclude prunes only refs/ names, only for the next pseudo-option, and cannot drop HEAD | mined | 2026-10-20 | on-release | corpus/knowledge/jj-colocation-receipts.md |
```

Landing precondition (frozen census, CORPUS.md § Census): "mined rows whose used-by paths do not exist —
must print nothing". `corpus/knowledge/jj-colocation-receipts.md` does **not** exist yet
(`ls -l` → No such file or directory). Append this row as `mined` only once C3(c) lands that entry; if
the entry slips, flip `status` to `queued` and `used-by` to `—` (or point `used-by` at
`corpus/lessons/round-17.md` once that exists). No `|` in any cell; 11 columns + 2 framing pipes = NF 13.

Gate block for the round lesson, ready to paste:

```
S051 — https://git-scm.com/docs/git-rev-list — opened 2026-10-20
stamp: "git-rev-list last updated in 2.56.0"; installed git 2.56.0-1 (man Date: 2026-09-27) verbatim
quote (19 words, § OPTIONS › Commit Limiting › --all, #Documentation/git-rev-list.txt---all):
  "Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>."
```

Optional second row (gitrevisions) — **recommendation: do not add**; record it in the search log as
corroborating context, the way the registry already treats git-status and mv. Draft if L1 disagrees:

```
| S052 | gitrevisions(7), refname disambiguation — https://git-scm.com/docs/gitrevisions | docs | A | revision-name resolution order for bare refnames on Git 2.56.0 | web manual "gitrevisions last updated in 2.56.0", opened 2026-10-20; § Specifying Revisions › <refname> | resolution tries $GIT_DIR/<refname> (HEAD and the other *_HEAD files) before refs/<refname>, so HEAD is not under refs/ while refs/jj/keep/<oid> resolves through refs/ | queued | 2026-10-20 | on-release | — |
```

Search-log line for the bounded search (rule 5):

```
- Round-17 ref-selection reading (2026-10-20). Question: what does `--all` root, and how do
  --branches/--tags/--remotes/--glob/--exclude narrow it, for the jj durable-root rule? Where:
  git-rev-list(1) and gitrevisions(7) web manuals (both "last updated in 2.56.0"), installed git
  2.56.0-1 roff, plus read-only rev-list measurements on the souji lane. Identified 2 documents,
  screened 2; included 1 row (S051); excluded gitrevisions from rows as corroborating context.
  Stop: the option family and its ordering/prefix rules were located and matched by measurement;
  for-each-ref pattern semantics remain unopened.
```

## 6. Verdict and smallest fix

**Verdict: holds** for the premise (`--all` = `refs/**` ∪ `HEAD`, includes `refs/jj/*`) and for the
C3(a) hazard; **partial** for the whole C3(a) sentence, because its `for-each-ref` half needs
git-for-each-ref(1), which nobody opened.

Smallest doc-grounded fix (all revisions of it stay inside rev-list, one manual):

1. `tools/souji-verify.sh:351` — replace `--not --all` with `--not --branches --tags --remotes`.
   Measured: keep-only head scores `0` (→ SAFE/metadata-prune) under `--not --all`, `1` under the trio.
2. `tools/souji-verify.sh:809-813` — replace the unfiltered `for-each-ref` roots array plus
   `rev-list --count "$head" --not "${roots[@]}"` with the single
   `rev-list --count "$head" --not --branches --tags --remotes --`. Same idiom, and it removes the
   dependency on the undocumented-for-this-question for-each-ref patterns. In this lane that is the
   difference between 58 and 52 roots.
3. Do **not** implement the narrowing as `--all --exclude=refs/jj/*`: HEAD survives every `--exclude`
   and the exclusion is positional (measured 52 / 58 / 58 above).
4. C3(b)'s `--glob=refs/jj/keep/*` addition is safe on plain repos: an absent namespace yields an
   empty set with rc 0 (`--glob=refs/nosuch/*` → 0, rc 0), and the explicit trailing `/*` is correct
   because `--exclude`, unlike the pseudo-options, does not imply it.

Disclose with the change: narrowing `--all` to the trio also drops `refs/notes`, `refs/stash`,
`refs/bisect/*` and sibling-worktree per-worktree refs from the root set, so a commit held only by one
of those flips from SAFE to NOT-SAFE. That is the conservative direction and is what the claim intends.
Also disclose: `--all` never included reflog objects, so reflog-only commits were already counted as
unique (conservative) before this change.

## 7. Commands actually run (and what they returned)

```
curl -fsS --max-time 60 -o /var/tmp/rev-list.html https://git-scm.com/docs/git-rev-list   → 254766 bytes
curl -fsS --max-time 60 -o /var/tmp/gitrevisions.html https://git-scm.com/docs/gitrevisions → 74654 bytes
python3 (strip tags on <div id="content">) → rev-list.txt 99760 chars, gitrevisions.txt 35232 chars
grep -oE 'git-(rev-list|revisions) last updated in [0-9.]+' → "git-rev-list last updated in 2.56.0",
                                                              "gitrevisions last updated in 2.56.0"
grep -n '^Commit Limiting' rev-list.txt → 3306; grep -n -iE 'refs/jj|namespace' → no match
sed -n '3460,3600p' rev-list.txt → the --not/--all/--branches/--tags/--remotes/--glob/--exclude/
                                   --exclude-hidden text quoted above
sed -n '2085,2270p' gitrevisions.txt → the <refname> resolution ladder quoted above
git --version → git version 2.56.0 ; pacman -Q git → git 2.56.0-1
zcat /usr/share/man/man1/git-rev-list.1.gz | sed -n '275,345p' → identical wording; header Date: 2026-09-27
sed -n '340,360p;800,820p' tools/souji-verify.sh → --not --all at :351; all-refs for-each-ref roots at :809-813
git -C <lane> for-each-ref --format='%(refname)' [refs/jj | 'refs/jj/keep/*'] → 8 keep refs, no other
                                   non-durable namespace
git -C <lane> rev-list --count … → all=58 trio=52 heads=52 jjglob=58 HEAD=52; --all∖trio=6; keep∖trio=6
git -C <lane> rev-list --count 0254661… --not --all → 0 ; --not --branches --tags --remotes → 1
git -C <lane> rev-list --count --exclude=refs/jj/keep/* --all → 52 ; --all --exclude=… → 58 ;
              --exclude=HEAD --all → 58 (rc 0, empty stderr) ; --exclude='refs/*' --all → 52
git -C <lane> rev-list --count --glob=refs/nosuch/* → 0 rc 0 ; HEAD --not --glob=refs/nosuch/* → 52 rc 0
git -C <lane> rev-parse --git-path worktrees → .git/worktrees ; stat → No such file or directory
awk over corpus/SOURCES.md → 50 rows, max S050; ls corpus/knowledge/jj-colocation-receipts.md → absent
```

No tool installed or upgraded this round; no pacman transaction attempted (host-wide pause respected);
nothing needed. No jj subcommand was run; no git write was run; the only file written is this report.

## 8. Remaining unknowns (for L1 to route)

1. `git-for-each-ref(1)` pattern semantics (prefix match vs literal) — unopened; blocks grounding the
   `for-each-ref` phrasing of C3(a) and blocks any fix that keeps a roots array instead of pseudo-options.
2. Whether `--branches`/`--tags`/`--remotes` are accepted with zero matching refs on the oldest git the
   fleet supports — measured here rc 0 with empty `refs/tags`, but only on 2.56.0.
3. The jj side (when jj drops `refs/jj/keep/*`, whether keep refs are per-operation or per-repo) — not
   a git question; belongs to SrcJjKeepRefs / the jj documentation rows.
4. Sibling seat `ScribeSourcesRows.md` sits in this same report directory; I did not read it (probe
   rule). If it drafts a row for the same page, keep one and fold the other's quote into the Gate.
