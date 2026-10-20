STATUS: DONE — C3 (a′)+(b′) landed in tools/souji-vault-verify.sh only: durable roots = every ref except refs/jj/*, keep-only commits refuse only on blob novelty, dead shadowed sites reverted; selftest 51 → 57 checks, 0 failed.

Seat `SoujiR17-3.VaultJjRoots` · 2026-10-20 · lane base `5fa6017` · writes: `tools/souji-vault-verify.sh` and this report only. No commit, no `jj` on a real repo, no lane tool run against a real directory. No tool was installed or upgraded. Work is on the L1 REVISED C3 contract (supersedes the wave text for C3); my earlier raw-glob/`jj-keep-unpushed` draft was discarded, not layered on.

## 1. Diff summary

`git diff --stat 5fa6017 -- tools/souji-vault-verify.sh` → `1 file changed, 137 insertions(+), 6 deletions(-)`.

- Header: one `r17` paragraph that states exactly the two bounded rules, cites jj source for "keep ref for every commit jj creates", and explicitly records that the repo-root unpushed count is unchanged and branch-based. `usage()` range retargeted `2,52p` → `2,63p` so help still ends at the env-overrides stanza.
- One helper `jj_keep_novel` added at file scope (vault `:414-441`).
- LIVE `try_pushed` (S18 engine, base `:859` → now `:894`): touching revset stays `HEAD --branches --not --remotes` (no glob); novelty result feeds the same refusal, note gains ` jj-keep-novel` only when the keep side contributed; `jjrc=2` (git failure) goes to `pushed=history-unverifiable`.
- LIVE roots site `s18_evaluate_worktree_one` (base `:997-1001` → now `:1051-1055`): `for-each-ref --exclude='refs/jj/' --format='%(objectname)'`.
- LIVE quarantine `second_check` (base `:1140` → now `:1197-1202`): same novelty gate, `SC_EV` gains ` jj-keep-novel`; a git failure fails the check (fail-closed).
- Selftest: git-only fixture (no jj) + J1–J6 replace my provisional V30–V34.

Dead shadowed definitions were REVERTED and verified byte-identical to base (awk-extracted first definitions):

```
DEAD-SITE-UNCHANGED try_pushed (first definition)        # base :412, live redefinition :894
DEAD-SITE-UNCHANGED evaluate_worktree (first definition) # base :517, live redefinition :1259
DEAD-SITE-UNCHANGED evaluate_repo_root (first definition) # base :487, live count restored
$ git diff 5fa6017 -- tools/souji-vault-verify.sh | grep -c 'not --all'
0
```

## 2. Helper body (mirror verbatim in the other two files)

```bash
jj_keep_novel() { # $1 repo, $2 path relative to the repo root
  local repo=$1 rel=$2 c obj known
  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null)" ] || return 1
  if ! known=$(git -C "$repo" rev-list --objects --remotes -- "$rel" 2>/dev/null | cut -d' ' -f1); then
    return 2
  fi
  if ! c=$(git -C "$repo" rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes -- "$rel" 2>/dev/null); then
    return 2
  fi
  while IFS= read -r c; do
    [ -n "$c" ] || continue
    obj=$(git -C "$repo" rev-parse -q --verify "$c:$rel" 2>/dev/null) || continue
    printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0
  done <<< "$c"
  return 1
}
```

Semantics: `0` novel keep-only content for `$rel`; `1` nothing novel, or no `refs/jj/keep/` at all (plain repos run no extra query); `2` git failure. The `known` set is every object `rev-list --objects --remotes -- $rel` reaches for that path (blobs; tree ids cannot collide with a blob id), which is the `{H:<rel>}` set of the contract in one call instead of one `rev-parse` per remote commit.

Caller shape used at both live sites:

```bash
  local jjrc=0 jjrel=${target#"$repo"/}
  jj_keep_novel "$repo" "$jjrel" || jjrc=$?
  if [ "$jjrc" = 2 ]; then NOTES+=("pushed=history-unverifiable"); return 1; fi
  if [ -n "$touching" ] || [ "$jjrc" = 0 ]; then
    if [ "$jjrc" = 0 ]; then
      NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12} jj-keep-novel")
    else
      NOTES+=("pushed=unpushed-commits-touching intro=${intro:0:12}")
    fi
    return 1
  fi
```

## 3. Contract conformance

(a′) `for-each-ref --exclude='refs/jj/'` at the live roots site; every ref except `refs/jj/*` stays a root, so `refs/stash`, `refs/original`, `refs/prefetch/*` keep the base verdict. Git 2.56.0 on this host supports it (verified: with `refs/jj/keep/*` present, the query returned only `refs/heads/master`, `refs/remotes/origin/HEAD`, `refs/remotes/origin/master`, and with `refs/stash` added it is included — see J5 table row).

(b′) blob novelty, not raw glob: the touching revset is base-identical; a keep-only commit refuses only when `C:<rel>` exists and its object is absent from remote-reached objects for that path. Deletions and identical-blob predecessors do not refuse. Whole query gated on `for-each-ref --count=1 refs/jj/keep/`; git failure → caller's `history-unverifiable`/FAIL path. Token on refusal is `jj-keep-novel`.

Repo-root unpushed count reverted to `git log --branches --not --remotes --oneline`; evidence string is base-identical (`unpushed=N dirty=M`, no token).

Header paragraph: no `refs/jj/bookmarks` claim, keep refs described as "one ref for every commit it creates, visible or hidden", with `lib/src/git_backend.rs@v0.45.1:868-871` cited; states the repo-root count is unchanged.

## 4. Selftest

```
$ bash tools/souji-vault-verify.sh --selftest | tail -1
selftest: 57 checks, 0 failed
$ ... | grep -E '^(PASS|FAIL) J'
PASS J1 NOT-VERIFIED(none)          # novel keep-only content refuses, evidence carries jj-keep-novel
PASS J2 VERIFIED(pushed)            # identical blob in remote history (metaedit predecessor) does not refuse
PASS J3 VERIFIED(pushed)            # keep-only phantom deletion does not refuse
PASS J4 NOT-VERIFIED(none)          # absent-worktree head only in refs/jj/keep -> unique=1, refuse
PASS J5 VERIFIED(metadata-prune)    # same head only in refs/stash -> still a root, unique=0, unchanged
PASS J6 plain repo evidence unchanged, no jj token
ROUND9	16	0
```

Base count is 51 by enumeration: the intermediate run that still carried my five provisional V-cases reported `56 checks` (51 + 5), and nothing outside that block was added or removed. The base copy cannot be selftested from `/var/tmp` (it resolves `SCRIPT_DIR` there and `souji-round9-selftest.sh` is absent → `R9 runner missing summary exit=127`), so the base number is stated as enumeration, not as a clean base run.

Fixture is git-only under the selftest's `mktemp -d` with the existing `trap ... EXIT`; no jj process is run:

```bash
  git update-ref refs/jj/keep/jnovel "$jnovel"   # novel nfile content
  git update-ref refs/jj/keep/jsame  "$jsame"    # samefile reverted to the blob j1 already has remotely
  git update-ref refs/jj/keep/jdel   "$jdel"     # deletes delfile
  git update-ref refs/stash          "$jstash"   # head held only by refs/stash
  st_register_worktree "$RJ" wt-jj    "$ST_TMP/wt-jj"    "$jnovel" ""
  st_register_worktree "$RJ" wt-stash "$ST_TMP/wt-stash" "$jstash" ""
```

## 5. Before/after table (git-emulated `refs/jj/keep`, sandbox `/var/tmp/souji-r17-VaultJjRoots/sbx`)

Old = `git show 5fa6017:tools/souji-vault-verify.sh`; new = worktree file; both run with `SHOKUNIN_ROOT=/var/tmp/.../sbx SOUJI_LEDGER=/var/tmp/.../ledger.tsv`.

| target | shape | old | new |
|---|---|---|---|
| `nfile.txt` | keep-only **novel** content | `VERIFIED(pushed)` | `NOT-VERIFIED(none)` — `pushed=unpushed-commits-touching intro=f4352896067f jj-keep-novel` |
| `samefile.txt` | keep-only predecessor with an **identical** blob already in remote history | `VERIFIED(pushed)` | `VERIFIED(pushed)` (unchanged) |
| `delfile.txt` | keep-only **deletion** | `VERIFIED(pushed)` | `VERIFIED(pushed)` (unchanged) |
| `wt-jj` | absent worktree head reachable **only** via `refs/jj/keep/*` | `VERIFIED(metadata-prune)` — false SAFE | `NOT-VERIFIED(none)` — `dir=absent unique=1 … durable-refs-only=yes` |
| `wt-stash` | same shape, head held **only** by `refs/stash` | `VERIFIED(metadata-prune)` | `VERIFIED(metadata-prune)` — `unique=0` (unchanged) |
| repo root `p-shokunin` | root verdict | `NOT-VERIFIED(none)` `unpushed=0 dirty=0` | byte-identical |

Real-jj cross-check (`jj git init --colocate` under the sandbox with `JJ_CONFIG` inside it; 10 `refs/jj/keep/*` refs left by `jj describe`/`jj abandon`):

```
kfile.txt     NOT-SAFE none  pushed=unpushed-commits-touching intro=e480c4f5994c jj-keep-novel; …
wt-keeponly   NOT-SAFE none  dir=absent unique=2 head=53046dc4828c … durable-refs-only=yes
main-shokunin NOT-SAFE none  unpushed=0 dirty=0            # repo-root evidence unchanged
```

## 6. Plain-repo byte identity (no refs anywhere under `refs/jj/`)

Five shapes, full stdout compared after path normalisation:

```
IDENTICAL pf.txt            :: VERIFIED(pushed)
IDENTICAL p2.txt            :: NOT-VERIFIED(none)
IDENTICAL wt-plain          :: VERIFIED(metadata-prune)
IDENTICAL q-plain-shokunin  :: NOT-VERIFIED(unpushed)
IDENTICAL old.out           :: VERIFIED(stale)
```

## 7. Static checks

```
$ bash -n tools/souji-vault-verify.sh          → SYNTAX-OK
$ shellcheck -S warning tools/souji-vault-verify.sh   # warning codes, base vs new
base: 3×SC2034 4×SC2100 1×SC2221 1×SC2222
new : 3×SC2034 4×SC2100 1×SC2221 1×SC2222      # identical set, pre-existing only
```

## 8. Risks / disclosures

1. **git < 2.56** has no `for-each-ref --exclude`: the roots query fails, `R_EVIDENCE="durable-refs-unverifiable"` and the verdict stays NOT-SAFE — fail-closed, but a host-version dependency worth naming in the PROVINCE/SKILL text.
2. `jj_keep_novel` runs only when `refs/jj/keep/` is non-empty and only on the refusal path, but it does one `rev-list --objects --remotes -- <rel>` plus one `rev-list` per refusal in a colocated repo. On a path with very deep remote history this is the most expensive branch of `try_pushed`; no cache was added.
3. Repo-root unpushed stays branch-based by contract: a keep-only commit alone still shows `unpushed=0`. Disclosed in the header, not changed.
4. `jj-keep-novel` evidence wording now diverges from the raw-glob wording I sent sibling `VerifyJjRoots` earlier; I messaged them the exact helper body and caller shape (§2) so the three files can converge on one literal.
5. The 1,877-path over-refusal table in `CriticC3Coverage.md §3.1` is not re-derived here (it needs the four real lanes and I am forbidden from running the tool against them); the novelty gate is exactly the correction that table asked for, but its effect on those lanes must be re-measured by the integrating seat.
6. **Abs-path trap in the shared helper.** `jj_keep_novel` needs a repo-RELATIVE path: `git rev-parse "C:/abs/path"` is invalid revision syntax, fails, and the `|| continue` then reports "not novel" for every keep commit — a silent precision loss that looks like success. Both callers pass `rel=${target#"$repo"/}`; sibling `VerifyJjRoots` hit this in its first draft and confirms the same fix. Keep the `rel` derivation adjacent to the call, not inside the helper, so a future caller cannot pass an absolute path by mistake.

Sandbox `/var/tmp/souji-r17-VaultJjRoots` was removed after the evidence above was captured.
