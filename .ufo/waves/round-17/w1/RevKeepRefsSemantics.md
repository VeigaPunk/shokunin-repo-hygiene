STATUS: DONE — the built (a)/(b) mechanisms are sound and plain-repo-identical, but they have drifted from the declared C3 text in three places; the load-bearing `--exclude` form is unguarded against a silent no-op. Fixture shapes enumerated below.

# RevKeepRefsSemantics — C3(a)/(b) static falsification

Seat: SoujiR17-3.RevKeepRefsSemantics (leaf reviewer). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `5fa6017ddcae9f6bd4412df44765f6360cb16294`, git 2.56.0, bash 5.3.20. No tool installs (nothing needed).

## Snapshot (files were being edited while I reviewed)

Final reviewed bytes:
- `tools/souji-verify.sh` sha256 `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f`, `bash -n` OK at this snapshot.
- `tools/souji-vault-verify.sh` sha256 `bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64`, `bash -n` OK.
- `tools/souji-quarantine.sh` sha256 `24c7cf059f234938a32353b221131c8b6dc71c13468ef967bae733863e131676`, `bash -n` OK.

Mid-flight observations (they no longer reproduce; recorded so the timeline is auditable): an intermediate read had `bash -n tools/souji-verify.sh` failing at `:724` (`syntax error near unexpected token 'fi'`, a dangling `return 1; fi` from a half-applied hunk) and an earlier draft passed the absolute target into a relative-path helper (see G4). Two earlier design drafts were visible and then replaced: (i) three-namespace roots (`refs/heads refs/tags refs/remotes`) and (ii) always-refuse on any keep-only touching commit. Neither is the final build. All conclusions below are against the final snapshot; the Q1/Q2 analysis explicitly distinguishes the drafts.

All git-semantics experiments ran in throwaway repos under `/var/tmp/souji-r17-RevKeepRefsSemantics/` with `LC_ALL=C GIT_LITERAL_PATHSPECS=1` (the tools' env). No census/verify/vault/quarantine run against any real path; no real repo mutated.

## The built design (as of the final snapshot)

(a) Durable roots — `for-each-ref --exclude='refs/jj/' --format='%(objectname)'`:
`tools/souji-verify.sh:854`, `tools/souji-vault-verify.sh:1061`, `tools/souji-quarantine.sh:1155`. Roots are **every ref except `refs/jj/*`** — `refs/stash`, `refs/original`, `refs/notes/*`, `refs/bisect/*`, `refs/worktree/*` stay roots. HEAD is never a root because `for-each-ref` never lists HEAD. Result feeds `rev-list --count "$head" --not "${roots[@]}" --` (`verify :858`, `vault :1065`, `quarantine :1159`); `uniq==0` ⇒ SAFE(metadata-prune).

(b) Keep-only work — `jj_keep_novel` (`verify :241-259`, `vault :433-449`, `quarantine :977-991`):
1. probe: any `refs/jj/keep/*` ref, else return 1 (plain repos run nothing new);
2. `keep = rev-list --glob=refs/jj/keep/* --not --branches --tags --remotes -- <rel>` — glob is a *positive* head, before `--not`; a git failure ⇒ 2;
3. `known = rev-list --objects --remotes -- <rel>` object ids;
4. for each keep commit, `rev-parse -q --verify "$c:<rel>"`; if that blob/tree id is absent from `known` ⇒ 0 (refuse); deletions (path absent in the keep commit) and identical-content predecessors do not refuse;
5. callers: `verify :719` (live `try_pushed` `:694`, via `evaluate_artifact` `:428`), `vault :914` (live `try_pushed` `:894`), `quarantine :341` and `:1341` (live second checks; `quarantine`'s `try_pushed` `:995` has no caller).

Live/shadowed map (the files still define the guard generation twice; last definition wins):

| file | function | shadowed copy | live copy |
|---|---|---|---|
| verify | `try_pushed` | `:258` (unpatched r6 body) | `:694` (novelty `:719`) |
| verify | `evaluate_worktree` | `:371` (option-group `:389`; formerly `--not --all`) | `:1047` → `s18_evaluate_worktree_one` `:832` (roots `:854`) |
| verify | `evaluate_repo_root` | — | `:357` (branch-only, see G1c) |
| vault | `try_pushed` | `:450` (old body) | `:894` (novelty `:914`) |
| vault | `evaluate_worktree` | `:537` (option-group `:556`) | `:1237` → `s18_evaluate_worktree_one` `:1018` (roots `:1061`) |
| vault | `evaluate_repo_root` | — | `:535` (branch-only) |
| quarantine | roots | — | `s18_evaluate_worktree_one` (roots `:1155`) |
| quarantine | second checks | — | `s18_second_check` `:341`, wrapper `:1341` |
| quarantine | `try_pushed` | — | `:995` (**no caller**) |

## Q1 — can `--branches --tags --remotes` (or the built minus-jj roots) turn a NOT-SAFE verdict SAFE on a plain repo?

**Correctly implemented: no, and the final build is monotone. Mis-implemented: yes, catastrophically — three distinct shapes, each measured.**

Monotonicity. `uniq = |anc(head) \ anc(R)|`. The built `R' = R \ refs/jj` is a subset of today's all-refs `R`, so `anc(R') ⊆ anc(R)` and `uniq' ≥ uniq`; SAFE fires only at `uniq==0`, so roots can only *lose* SAFE. Measured (repo with `refs/heads/main` only, keep ref holding commit K off-branch): `rev-list --count K --not <all objectnames>` = **0** (today's false SAFE(metadata-prune)), `--not <all objectnames minus refs/jj>` = **1** (NOT-SAFE). For the positive side (the drafts' `--branches --glob` form), adding roots can only grow the count.

Mis-shapes that produce false SAFE:

1. **Bare namespace wildcards in rev position are pathspecs, not refs.** `rev-list --count HEAD` = 2; `rev-list --count HEAD --not 'refs/tags/*'` = **0** in a repo with **no tags at all** (git disambiguates the unresolvable wildcard as a pathspec; `GIT_LITERAL_PATHSPECS=1` makes it literal; nothing matches; the walk is empty). `--glob='refs/tags/*'` on the same repo = 2 (correct no-op). `git rev-parse --verify 'refs/heads/*'` → `fatal: Needed a single revision`. If used as roots this makes **every** absent-worktree head `uniq=0` ⇒ SAFE(metadata-prune) everywhere.
2. **Bare namespace names** (`--not refs/heads refs/tags refs/remotes`) → `fatal: ambiguous argument 'refs/heads'` (128) — degrades everything to `worktree-ancestry-unverifiable` (NOT-SAFE but kills metadata-prune).
3. **`--glob` after `--not` is negated** (`--not` reverses "all following revision specifiers", git-rev-list(1) man 274-279). Measured with a local-only branch commit c3 touching `f` plus `refs/jj/keep/<c3>` (bookmark+keep sharing a sha — the ordinary jj-colocated shape): base `log --format=%H HEAD --branches --not --remotes -- f` = 3 lines; `… --not --remotes --glob='refs/jj/keep/*' -- f` = **0** lines ⇒ `touching` empty ⇒ SAFE(pushed) certified for local-only work. Correct order (`--branches --glob=… --not --remotes`) = 3 lines.

Sound forms: `--not --branches --tags --remotes` (option-group negation works: `rev-list --count HEAD --not --branches` = 0 when HEAD is on a branch) or the objectname list from an explicit `for-each-ref`; the keep glob strictly before `--not`, single-quoted. The final build uses the `--exclude` form for (a) and a separate helper for (b), so neither trap is present.

## Q2 — does dropping HEAD from roots change plain-repo verdicts?

**In the final build: no — nothing changes.** `for-each-ref` never lists HEAD (verified attached and detached: output was only `refs/heads/main`, and with a stash, `refs/heads/main refs/stash`), so the *live* absent-worktree path never used HEAD as a root, before or after. The built minus-jj roots keep `refs/stash` a root, so a stash-held registration head still earns SAFE(metadata-prune) (measured 0 unique) — plain-repo verdicts are byte-identical.

Two corrections to the plausible reading of C3(a):
- The declared text ("durable roots are refs/heads, refs/tags, refs/remotes only — never refs/jj/*, refs/stash or HEAD") describes a **three-namespace draft**, not the build. That draft was measured to change plain-repo verdicts: stash-held absent head → all-refs roots 0 (SAFE) vs three-namespace roots **2** (NOT-SAFE); same for `refs/notes`/`refs/bisect`/`refs/worktree`. The final minus-jj form avoids that. Keep the build, fix the claim (G1a).
- The detached-HEAD flip I measured (`--not --all` = 0 vs option-group = 1) exists only in the shadowed legacy `--not --all` copies, which the build already rewrote (`verify :389`, `vault :556`) and which are unreachable. Do not revive them.

## Q3 — does an unmatched `--glob=refs/jj/keep/*` error on repos with no such refs?

**No.** Measured: `log --oneline --branches --glob='refs/jj/keep/*' --not --remotes` and the `rev-list --count` form are byte-identical to the glob-less commands, exit 0, in a repo with no `refs/jj` at all; an empty `.git/refs/jj/keep/` directory is the same; an unborn repo returns empty, exit 0 (its HEAD is gated by `cat-file -e "$head^{commit}"` first). Docs: `--glob=<pattern>` = "pretend as if all the refs matching … are listed"; zero matches add nothing (git-rev-list(1) man 337-343).

Quoting is the only hazard: unquoted, a cwd containing a decoy `refs/jj/keep/<file>` expands the pattern to paths (`fatal: ambiguous argument`, conservative → history-unverifiable), and with an exported `BASHOPTS` carrying `nullglob` the argument disappears entirely (a child bash saw `nullglob on`), silently disabling (b) while plain-repo checks still pass. All three helpers quote `"--glob=refs/jj/keep/*"`; keep it that way and pin it (K17).

## Findings

**G1 (high, contract drift) — the built rules are better than the declared C3 text, but they are not the declared text; three divergences must be reconciled by L1.**

a) **Roots.** C3(a): "refs/heads, refs/tags, refs/remotes only — never refs/jj/*, refs/stash or HEAD." Build (`verify :854`, `vault :1061`, `quarantine :1155`): every ref except `refs/jj/*`; stash/original/notes/bisect/worktree stay roots; HEAD is not listed by `for-each-ref` at all. Consequence: the declared claim would have changed plain-repo verdicts (measured stash case 0→2); the build does not. Recommend amending C3(a) to "every ref except refs/jj/* (HEAD is never a for-each-ref root)" — that also makes the in-file headers (`verify :61-77`, `vault :44-58`, `quarantine :116-124`) correct as written.

b) **Refusal rule.** C3(b): "a commit only jj holds that touches the target refuses (conservative: hidden rewritten predecessors that touched the target also refuse — disclose)." Build: refuse only when the keep-only commit's object at the path is **novel** relative to every object reachable from `--remotes -- <rel>`; deletions and identical-content predecessors do not refuse (measured: novel blob rc=0, identical-content rc=1, deletion rc=1). This is the right precision call (it removes the phantom-deletion/`vadv54` false refusals), but it contradicts both the claim text and the census disclosure. Amend C3(b)/census text; do not "fix" the code toward the older text.

c) **Repo-root unpushed term.** C3(b) names the repo-root checks (`verify :321`, `vault :487`) as also seeding keep heads. Build: every `evaluate_repo_root` is branch-only (`verify :359-361`, `vault :537-539`; `quarantine` has no `evaluate_repo_root`). No verdict effect (repo roots are unconditional NOT-SAFE; only `unpushed=`/receipt changes), but the enumerated claim line is unimplemented. Either add the term (cheap, evidence-only) or drop it from the claim.

**G2 (medium) — the `--exclude` form is load-bearing and silently fails when wrong.** `for-each-ref --exclude='refs/jj/'` excludes `refs/jj/keep/*` from the default all-refs listing (measured: heads+stash returned, jj keep excluded; boundary respected — `refs/jjx/y` survives). `--exclude='refs/jj/*'` (the obvious-looking "glob" spelling) excludes **nothing** (5 vs 4 objectnames) and exits 0 — a one-character cleanup would silently restore the r16 false SAFE(metadata-prune) with no diagnostic. Docs describe `--exclude` only for use "up to the next --all/--branches/--tags/--remotes/--glob"; the default-listing behaviour is real but not promised by that sentence, so it must be pinned behaviorally (J4/J5 do) and statically (K19).

**G3 (medium) — claim/audit site lists still point at shadowed copies and superseded mechanisms** (`verify :234`/`:351`, `vault :517`, and the old `--branches --not --remotes` shape). A grep-based D6/regenerate assertion can pass on the dead copy while the live path is wrong — this is exactly what I caught mid-flight in vault, where the first patch landed on the shadowed `try_pushed`/`evaluate_worktree` while the live `try_pushed`/`s18_evaluate_worktree_one` still had the old shapes. Any evidence must be behavioral plus a definition-aware static assert (K19); a bare grep is not proof.

**G4 (medium-low, SAFE-ward edge) — relative-path derivation is unguarded.** `verify :718` `rel=${target#"$repo"/}` and `vault :913` `jjrel=${target#"$repo"/}` silently leave an absolute path when `$repo` is not an exact prefix of the canonicalized target (e.g. the repo reached through a symlinked path: `find_repo_for` returns `git rev-parse --show-toplevel`, target is `canon_path`'d). The helper then cannot resolve `$c:<abs>`, returns 1 ("not novel"), and a keep-only novel blob is **allowed** — the only SAFE-ward path I found in the build. `quarantine :1017` shows the pattern that avoids it (`[ "$jjrel" != "$target" ]`), but it *skips* the check, which is the same outcome. Smallest fix: in `jj_keep_novel`, if `$2` is absolute (`case "$2" in /*) return 2;; esac`) so the caller takes `history-unverifiable`; do the same in the two callers that currently pass a possibly-absolute rel. (Quarantine's dead `try_pushed :995` is guarded; verify's live one is not.)

**G5 (low) — per-keep-commit `grep -Fxq` subprocess.** `jj_keep_novel` spawns one `printf | grep` per keep commit per artifact (`verify :255`, `vault :447`). This lane already shows 6 keep-only commits; a long-lived jj lane can carry hundreds, and `try_pushed` runs for every artifact. Correctness unaffected; if profiling shows it, batch with `grep -Fxf <(printf '%s\n' "$keep_objs")` or an associative array.

**G6 (info) — `--exclude`/novelty are new, so the r16 census disclosure no longer describes the build.** The context's census note ("keep refs include hidden predecessors … 4 with phantom deletions → disclosed, not changed") was written for the always-refuse draft; under the novelty rule those four phantom-deletion predecessors do **not** refuse. The census column itself stays branch-based (out of my scope), but the sentence tying it to (b) needs the same amendment as G1b.

## Verified non-issues (falsifiers that came back negative)

- Minus-jj roots are a subset of today's roots ⇒ monotone; the r16 jj-keep-only-head bug is fixed (0 → 1 unique).
- `for-each-ref --exclude='refs/jj/'` boundary is component-wise: `refs/jjx/y` survives; only `refs/jj/…` is removed. Trailing-slash form required (G2).
- `for-each-ref` never emits HEAD (attached or detached), so the HEAD clause in C3(a) was already true in every live path.
- Unmatched `--glob` is a no-op, exit 0 (Q3), including an empty `.git/refs/jj/keep/` and an unborn repo.
- `--not` negates option groups (`--branches --tags --remotes`) and the `--glob` option; ordering is positional (Q1).
- Positive rev roots are never history-simplified away: merge amended TREESAME for the path, keep commit S as the only positive root → `log --format=%H --glob='refs/jj/keep/*' --not --remotes -- f` still lists S (`--full-history` adds nothing). So a keep-only commit with a novel blob always surfaces.
- Non-commit roots are tolerated: annotated tag objects peel (`rev-list --count S --not <tagobj>` = 0); a blob in the negative root list is a no-op, exit 0; a keep ref pointing at a blob does not break `rev-list --glob` (exit 0).
- A keep ref pointing at a pushed commit changes nothing (2 vs 2).
- Novelty helper end-to-end on a scratch repo: novel blob → 0, identical-content predecessor → 1, deletion → 1, no keep refs → 1, absolute path mis-passed → 1 (i.e. the G4 silent-allow).
- Empty `"${roots[@]}"` under `set -u` is fine on bash 5.3; `--not --` counts all reachable (conservative).
- `set -euo pipefail` is active in all three tools; the helpers' `|| return 2` paths do catch git failures (and callers map 2 → history-unverifiable).

## Fixture shapes the suite must cover

Existing coverage in the build: verify `J1`–`J5` (`:1347-1351`) pins novel (J1), identical-content-on-a-side-remote (J2), deletion (J3), keep-only absent head (J4), stash-held absent head (J5); quarantine `JJ0`–`JJ7` (`:1693-1732`) pins the helper units, the flow token, and the stash/keep-root split; vault has an equivalent `J1`-style case. Missing shapes (add to `st_case`/`st_register_worktree`, `verify :1140` writes arbitrary HEAD+commondir, so only `git update-ref refs/jj/keep/<sha>` / `git stash` are new setup verbs):

1. **K01 plain, no refs/jj, absent reg head = origin tip** (F4): SAFE(metadata-prune) `unique=0`, byte-identical evidence.
2. **K02 plain, local-only branch commit touching target** (pushed artifact): NOT-SAFE(unpushed-commits-touching), no `jj-keep-novel`.
3. **K03 plain, fully pushed artifact**: SAFE(pushed), identical evidence; asserts no keep token leaks into plain repos.
4. **K04 stash-held absent head**: SAFE(metadata-prune) — pins that minus-jj keeps stash as a root (a three-namespace regression turns this NOT-SAFE).
5. **K05 notes/worktree-held absent head**: SAFE(metadata-prune), same purpose.
6. **K06 detached-HEAD-only absent head**: NOT-SAFE(none) both before and after; discriminates a wildcard-pathspec root bug (which yields SAFE).
7. **K07 keep-only absent head**: NOT-SAFE(none) `durable-refs-only=yes` (existing J4).
8. **K08 keep ref + head on a branch**: SAFE(metadata-prune) — keep refs are not roots of trust.
9. **K09 keep ref at a commit reachable from origin**: absent head = that commit → SAFE (remote root); pushed artifact untouched by it → SAFE(pushed).
10. **K10 keep-only novel blob touching target**: NOT-SAFE with `jj-keep-novel` (existing J1).
11. **K11 keep-only identical-content predecessor** (equal to a blob on any remote ref): SAFE(pushed), no token (existing J2).
12. **K12 keep-only deletion of the target**: SAFE(pushed), no token (existing J3) — the phantom-deletion case.
13. **K13 keep-only commit not touching the target**: pushed artifact on another path SAFE(pushed).
14. **K14 keep ref pointing at a blob/tree**: exit 0, verdict unchanged, no crash.
15. **K15 keep ref sharing a local-only branch commit's sha**: refused by the base `touching` query (branch positive), no novelty needed — pins that the helper does not *replace* the branch check.
16. **K16 keep refs absent**: evidence byte-identical to pre-r17 for every fixture (no token, no receipt change).
17. **K17 decoy cwd / `BASHOPTS` nullglob**: run from a cwd containing `refs/jj/keep/<file>`, and once with an exported BASHOPTS including `nullglob`; K10/K11 must be unchanged (proves the single-quoted `--glob=` survives).
18. **K18 empty repo / owner with no heads/tags/remotes**: roots empty → NOT-SAFE(none), exit 0, no crash.
19. **K19 definition-aware static assert** (not a bare grep): the *last* definition of `evaluate_worktree`/`s18_evaluate_worktree_one`/`try_pushed`/`evaluate_repo_root` in all three tools contains (i) no `--not --all`, (ii) no bare `refs/heads`/`refs/tags`/`refs/remotes` rev argument, (iii) no `--glob` after a `--not`, (iv) no `--exclude='refs/jj/*'` (mis-form), and (v) `for-each-ref` roots always carry `--exclude='refs/jj/'`.
20. **K20 quarantine parity**: replay K01–K15 through `souji-quarantine.sh`'s live second-check/flow (JJ0–JJ7 already cover most; K04/K05/K06 and K15 are the gaps).
21. **K21 symlinked-repo path** (G4): invoke with the lane root reached through a symlink; a keep-only novel blob must still refuse (or degrade to history-unverifiable), not SAFE.

## Smallest fixes

1. Amend C3 text (and the census sentence, G6) to the built rules: roots = every ref except `refs/jj/*`; (b) = novel-blob refusal, deletions/identical-content excluded; drop or implement the repo-root keep term (G1a–c).
2. `verify :718` / `vault :913` / `quarantine :1017`: treat a failed prefix-strip as unverifiable — guard the absolute case inside `jj_keep_novel`: `case "$2" in /*) return 2;; esac` (G4).
3. Add K05/K06/K13/K14/K15/K17/K19/K21 to the selftests; keep J1–J5/`JJ0–JJ7` as-is (G2/G3).
4. Optional: batch the per-keep `grep` (G5).

## Commands run (verbatim, trimmed output)

Under `W=/var/tmp/souji-r17-RevKeepRefsSemantics`, `LC_ALL=C GIT_LITERAL_PATHSPECS=1`, scratch repos built with `git init`; `git --version` → `git version 2.56.0`.

```
# roots: keep-only head (t3)
git rev-list --count "$K" --not $(git for-each-ref --format='%(objectname)')                                   -> 0   (old false SAFE)
git rev-list --count "$K" --not $(git for-each-ref --format='%(objectname)' --exclude='refs/jj/')             -> 1   (minus-jj)
git rev-list --count "$K" --not $(git for-each-ref --format='%(objectname)' refs/heads refs/tags refs/remotes) -> 1   (three-namespace draft)

# bare wildcard is a pathspec (t5: HEAD=D child of A, no tags)
git rev-list --count HEAD                              -> 2
git rev-list --count HEAD --not 'refs/tags/*'          -> 0   exit=0
git rev-list --count HEAD --not --glob='refs/tags/*'   -> 2   exit=0
git rev-parse --verify 'refs/heads/*'                  -> fatal: Needed a single revision (128)
git rev-list --count HEAD --not refs/heads             -> fatal: ambiguous argument 'refs/heads' (128)
git rev-list --count HEAD --not --branches --tags --remotes -- -> 0 ; … --not (trailing) -> 3

# --exclude form (t1: refs/heads/main, refs/jj/keep/K, refs/stash, refs/jjx/y)
git for-each-ref --format='%(refname)' --exclude='refs/jj/'      -> refs/heads/main refs/jjx/y refs/stash (+remotes)
git for-each-ref --format='%(refname)' --exclude='refs/jj/*'     -> refs/jj/keep/K still present
git for-each-ref --exclude='refs/jj/*' --format='%(objectname)'  -> 5 objectnames
git for-each-ref --exclude='refs/jj/'  --format='%(objectname)'  -> 4 objectnames

# --glob placement (t1: c3 local-only touches f, refs/jj/keep/<c3>)
git log --format=%H HEAD --branches --not --remotes -- f                          -> 3
git log --format=%H HEAD --branches --not --remotes --glob='refs/jj/keep/*' -- f  -> 0   (false pass)
git log --format=%H HEAD --branches --glob='refs/jj/keep/*' --not --remotes -- f  -> 3

# unmatched glob / empty namespace / unborn
… --glob='refs/jj/keep/*' --not --remotes  (no refs/jj, empty .git/refs/jj/keep, unborn) -> identical / empty, exit 0

# stash and detached HEAD (t7, t5)
git rev-list --count "$ST" --not $(git for-each-ref --format='%(objectname)')                     -> 0
git rev-list --count "$ST" --not $(git for-each-ref --format='%(objectname)' --exclude='refs/jj/') -> 0   (stash stays a root)
git for-each-ref --format='%(refname)'                    -> refs/heads/main refs/stash   (HEAD not listed)
git rev-list --count HEAD --not --all                     -> 0   (legacy/dead form only)
git rev-list --count HEAD --not $(… three namespaces)     -> 1   (draft only)

# history simplification (t6): keep commit S merged, merge amended TREESAME to first parent
git log --format='%H %s' -- f                                     -> only M
git log --format=%H --glob='refs/jj/keep/*' --not --remotes -- f  -> S and M (positive roots never simplified away)

# novelty helper replica (tools/souji-verify.sh:241-259), scratch t/n
jj_keep_novel "$PWD" d/n.txt          (novel keep blob)       -> 0
…                                     (keep-only deletion)    -> 1
…                                     (identical to pushed)   -> 1
…                                     (no refs/jj/keep)       -> 1
…                                     ($PWD/d/n.txt absolute) -> 1   (G4 silent allow)

# tag/blob roots
git rev-list --count "$S" --not "$(git rev-parse refs/tags/ann)" -> 0  (annotated tag peels)
git rev-list --count HEAD --not <list incl lightweight blob tag> -> 0  exit=0
```

Doc citations from `/usr/share/man/man1/git-rev-list.1.gz`: `--not` reverses meaning "for all following revision specifiers, up to the next --not" (man 274-279); `--all` includes "all the refs in `refs/`, along with HEAD" (282-287); `--glob=<glob-pattern>` "pretend as if all the refs matching … are listed" (337-343); `--exclude` applies "up to the next --all/--branches/--tags/--remotes/--glob" (360-367).

Snapshot/identity: `git -C <lane> rev-parse HEAD` → `5fa6017…`; `sha256sum tools/{souji-verify,souji-vault-verify,souji-quarantine}.sh` at final read → `9274300…/bbca35a…/24c7cf0…`; `bash -n` → OK for all three; `git diff --stat HEAD -- tools/` showed verify/vault/quarantine plus census/seat-audit/landing-gate modified.

## Residual risk / verification gaps

- No tool was run against a real directory (prohibited) and no selftest was executed; every verdict mapping is code-reading plus scratch-repo measurement of the underlying git commands. K01–K21 and the built-in J/JJ cases are unrun here.
- The files changed repeatedly during review (three design revisions observed); findings G1–G5 are pinned to the sha256 snapshot above. Re-read the live definitions before integrating.
- `--exclude` default-listing semantics is measured on git 2.56.0 only; the man page does not promise it. A git upgrade could change it silently — K19 plus a behaviour case is the guard.
- Census `unpushed` column and the r16 disclosure text were not exercised (separate seats); G1b/G6 must land there too.
- Performance: `rev-list --objects --remotes -- rel` plus one `grep` per keep commit per artifact; measure on the jj lane before calling C3 sealed.
- `refs/replace/*` rewrites traversal globally regardless of roots; not exercised.
- Both tool files carry two generations; every future edit must target the live copy (G3).
