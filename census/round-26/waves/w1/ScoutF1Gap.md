# ScoutF1Gap — F1 frontier map, r26 C2 expansion grounding

## Status

STATUS: PARTIAL — the gap list is delivered in full and the F1 remaining-open-items
enumeration is delivered, but two of the three gap-closing evidence claims in the
C2 admit set are **confounded** (the prunable registration is already gone before
the measured command runs), and the round's own numerator is already stale at
tip. Both are attack-grade findings, not defects in the frozen counters.

Seat: read-only scout (leaf member, no dispatch). Scope: read the two base F1
corpus files in full, list verbatim every deferral sentence for the
fetch/merge/rebase/pull trigger set, enumerate F1's remaining open items per
PROVINCE + README, and ground the C2 expansion claim.

## Evidence

All commands read-only. Lane tip `d6c13b0`; prereg base `0eca7c8`; frozen
amendment-1 commit `89e0fce`. Host `git version 2.56.0`, Linux x86_64.
Tooling: no install, no upgrade, no pacman transaction (nothing needed).

### E1 — the two base F1 files are unchanged base→tip (the deferrals still stand)

```
$ git -C souji-shokunin diff --stat 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd HEAD \
    -- corpus/knowledge/git-auto-maintenance-prunes-worktrees.md \
       corpus/knowledge/git-grace-periods-and-expire-to.md
(empty)
$ git rev-parse HEAD:corpus/knowledge/git-auto-maintenance-prunes-worktrees.md \
    0eca7c8:corpus/knowledge/git-auto-maintenance-prunes-worktrees.md \
    HEAD:corpus/knowledge/git-grace-periods-and-expire-to.md \
    0eca7c8:corpus/knowledge/git-grace-periods-and-expire-to.md
5e081957d9840ff97c91f7c86004df1168964d82
5e081957d9840ff97c91f7c86004df1168964d82
138660c39927757dcca936d9026996d0e2b29e22
138660c39927757dcca936d9026996d0e2b29e22
```

### E2 — the deferral gap list (verbatim, byte-verified against the opened files)

Quotes are ≤25 words, contain no literal or escaped `|`, and were verified
present in the cited line with `python3 -B` (substring + word count + pipe check).
File A = `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`;
file B = `corpus/knowledge/git-grace-periods-and-expire-to.md`.

| # | Location | Verbatim quote | Words | Defers what |
|---|---|---|---|---|
| D1 | A:8 | "A successful `git commit` can trigger worktree-prune as a side effect on Git 2.55.0:" | 14 | The claim is scoped to `commit` only; the other trigger commands are not claimed. |
| D2 | A:25 | "A search of the cached Git 2.55 sources found one direct `run_auto_maintenance` call each in `builtin/am.c:1942`, `fetch.c:2885`, `merge.c:509` and `rebase.c:572` at v2.55.0" | 22 | Names `am`/`fetch`/`merge`/`rebase` as call sites — the trigger set, unmeasured. |
| D3 | A:25 | "these are call sites only — whether each prunes was not fixture-run, and other trigger paths are not excluded." | 19 | **The central deferral**: the four commands are call-site-only, not behaviourally run. |
| D4 | A:25 | "Manual `git gc` also calls worktree-prune at `builtin/gc.c:1042-1044@v2.55.0`; this was read in code only, not separately reproduced" | 17 | A second, unmeasured trigger path (manual `git gc`), code-read only. |
| D5 | A:25 | "Local config (`maintenance.auto`, strategy/task enablement, and the auto threshold) can alter the behavior." | 13 | The behaviour is config-dependent, so no measurement transfers blindly. |
| D6 | A:27 | "this entry was verified on 2.55.0 and has not been re-verified on 2.56.0. Treat it as pending recheck (routed to r17), not as re-confirmed." | 24 | Version staleness: the whole entry is 2.55.0-only, on a 2.56.0 host. |
| D7 | A:16 | "The fixture corroborates the tagged source; it does not replace it." | 11 | The r12 fixture is corroboration, not the admission basis. |
| D8 | A:19 | "The pruning step itself is the seat's report, not re-observed." | 10 | The r12 incident's prune is seat-reported, not re-observed. |
| D9 | B:37 | "this entry was verified on 2.55.0 and has not been re-verified on 2.56.0. Treat it as pending recheck (routed to r17), not as re-confirmed." | 24 | Same version staleness, second base entry. |
| D10 | B:18 | "Changing that hold is an operator/SKILL decision; this entry records facts only." | 12 | The expiry values are recorded, not acted on; no hold change is claimed. |
| D11 | B:21 | "The fixture demonstrates deletion of that orphaned commit under forced expiry; it does not simulate concurrent-writer corruption." | 17 | Concurrent-writer corruption is not simulated — an explicit non-establishment. |
| D12 | B:15 | "`--prune=now` ignores object age and “increases the risk of corruption if another process is writing to the repository concurrently”" | 20 | `--prune=now` is a documented corruption risk, not a safe default. |

D3 is the sentence the C2 admit set exists to close. D2/D3 are the trigger-set
gap; D4/D5/D6/D9 are the transfer limits; D7/D8/D10/D11/D12 are the scope limits
that survive the expansion and are stated as such in the new entries.

### E3 — C2's admitted evidence: the two new entries close D3, and their own wording is accurate about it

`corpus/knowledge/git-auto-maintenance-trigger-set.md` (new, `ground: F1`, tracked
at HEAD) states at its "What this does NOT establish" block that the behavioural
gap "for those three commands is closed by the sibling entry
`corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` (S131), not here."
Verified: `git grep -l '^ground: F1' HEAD -- corpus/knowledge/` returns exactly 2
files, matching C2 K1 = 2.

Both new entries' `recheck:` lines and the base entries' `recheck:` lines still
pass on the live host:

```
$ v=$(git --version | awk '{print $3}')   # 2.56.0
$ curl -fsSL https://raw.githubusercontent.com/git/git/v$v/builtin/gc.c \
    | grep -cE 'strategy = geometric_strategy;|"3\.months\.ago"'      # -> 2  (base A expects 2)
$ MANWIDTH=2000 man git-gc | grep -oE '2\.weeks\.ago|3\.months\.ago|defaults to (90|30) days|default is (60|15) days' | sort -u
2.weeks.ago
3.months.ago
default is 15 days
default is 60 days
defaults to 30 days
defaults to 90 days          (base B recheck passes, 6 values)
```

### E4 — the trigger set is closed over the whole v2.56.0 tree (not just the five probed builtins)

Full `git clone --depth 1 --branch v2.56.0` into scratch; exhaustive grep of
every `.c`/`.h` in the tag:

```
$ grep -rn 'run_auto_maintenance' --include='*.c' --include='*.h' . | grep -v Documentation
./builtin/am.c:1942:  run_auto_maintenance(the_repository, state->quiet);
./builtin/commit.c:1965:  run_auto_maintenance(the_repository, quiet);
./builtin/fetch.c:2926:  run_auto_maintenance(the_repository, verbosity < 0);
./builtin/merge.c:509:  run_auto_maintenance(the_repository, verbosity < 0);
./builtin/rebase.c:572:  run_auto_maintenance(the_repository,
./run-command.c:1987:int run_auto_maintenance(struct repository *r, int quiet)   [definition]
./run-command.h:247:                                                        [declaration]
```

Exactly five call sites; `builtin/pull.c` has none (verified: 0 matches).
**Entry A's "exactly five of the candidate builtins" is closed and correct** — the
word "candidate" is the only slack, and the tag-wide search closes it. This
upholds S129's claim.

`git pull` reaches the trigger by process spawn, not by its own call site:

```
builtin/pull.c:392:  strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);
```

Three **other** builtins spawn a child `git fetch` and therefore inherit the
trigger the same way `pull` does — none is named in either new entry:
`builtin/remote.c:1717` (`git remote update`), `builtin/remote.c:104`
(`git remote add -f`), `builtin/submodule--helper.c:2530`
(`git submodule update --remote`). The last is inside `fetch_in_submodule`, and
`builtin/gc.c:899` spawns `git fetch` from the `prefetch` maintenance task.
Entry A claims the trigger set is "a named, per-command set" and gives the
census its "denominator" — the denominator is wider than the five plus `pull`.

### E5 — ATTACK: two of the three "all four commands prune" claims are confounded

The admitted measurement is the campaign's own-work fixture
`lanes/souji/round2/fixtures/r23-trigger-prune.sh` (sha256
`11c136aa71066733d50d226d344df9125401780aa81836f8ca9ca68a9997e65a`, re-grounded
byte-for-byte by this lane, as S131). Its `pull` case is **not** `git pull`:

```
$ grep -n 'pull' r23-trigger-prune.sh
3:# `git pull` auto-maintenance actually PRUNE a worktree registration?
12:#   The `commit` path is proven (r12 fixture). For fetch/merge/rebase/pull the
144:    pull)
195:run_case pull           1 pull

$ sed -n '144,147p' r23-trigger-prune.sh
    pull)
      g "$repo" remote add origin "$rem"
      g "$repo" fetch -q origin
      ;;
```

The `pull` case runs `git fetch`, not `git pull` — so it re-measures the `fetch`
path, and the `pull` claim in the new entry
`corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` ("under `git pull`",
"The `git pull` result is the expected consequence of S130: pull spawns
`fetch`") rests on the code argument plus a fixture row that never invoked
`pull`. My own isolated run does confirm the *behaviour* (see E6), so the claim
is true — but the cited evidence does not witness it.

Worse, the `merge` and `rebase` cases each perform a `git commit` **inside the
case, before the measured command**, with the registration already aged:

```
merge)   g "$repo" checkout -q -B topic other; printf 'topic\n' >"$repo/topic.txt";
         g "$repo" add topic.txt; g "$repo" commit -qm topic;      # <-- commit
         g "$repo" checkout -q master; g "$repo" merge -q --no-edit topic
rebase)  ... g "$repo" commit -qm topic;                          # <-- commit
         g "$repo" checkout -q master; g "$repo" rebase -q topic
```

`git commit` is itself one of the five trigger commands (E4), and the base entry
A:8 records that the commit path prunes. So in the `merge` and `rebase` cases
the prunable registration may already be gone before `merge`/`rebase` runs —
the case does not discriminate *which* command pruned. My replication
(scratch `/var/tmp/souji-r26-ScoutF1Gap/exp`, git 2.56.0, `maintenance.autoDetach=false`,
index aged to 4 months, fixture's exact command sequence):

```
FIXTURE-MERGE   before=2  after_commit=1  after_merge=1
FIXTURE-REBASE  before=2  after_commit=1  after_rebase=1
```

The count drops **at the intervening `commit`**, not at the merge/rebase. The
fixture's own `expect=1` for these two cases is therefore satisfied by the
commit, and the merge/rebase trigger is not isolated. This is the r25 mistake
class "a committed witness cited for more than it runs" (round-25 lesson
R24-M19 / `W2Rejects` F14) recurring in r26 on a new entry.

Isolating the merge and rebase commands (topic commit made **before** the
registration is aged, so no commit happens inside the measured window):

```
MERGE-ONLY   before=2  after=1
REBASE-ONLY  before=2  after=1
```

So `merge` and `rebase` **do** prune on their own — the claim is true, but the
cited fixture does not witness it, and the fixture as written cannot distinguish
the trigger. The C2 claim's kill rule does not test this, so it is not a
counter failure; it is a coverage-weakness in the admitted entry's own
"MEASURED" claim.

`git am` — the fifth call site (E4) — has **no** behavioural case at all:

```
$ grep -rniE '\bgit am\b|SOUJI-.*-am\b|case=am\b' lanes/souji/ merge/souji/knowledge/   # empty
$ grep -n 'run_case ' r23-trigger-prune.sh
run_case fetch          1 fetch
run_case fetch-auto-off 2 fetch-auto-off
run_case pull           1 pull
run_case merge          1 merge
run_case rebase         1 rebase
run_case locked         2 locked
run_case fresh          2 fresh
```

So the newly named trigger set has five commands; the fixture covers four of
them (`fetch`, `merge`, `rebase`, `pull`-as-fetch), and `am` is named but never
measured. Entry A names `am.c:1942` in the trigger set; entry B's claim title
says "`fetch`, `merge`, `rebase` and `pull` auto-maintenance all prune" — `am` is
in the set but out of the measurement, and nothing says so.

### E6 — the behaviours are nonetheless real (independent measurement, scratch only)

Same scratch harness, `GIT_CONFIG_GLOBAL=/dev/null`, `maintenance.autoDetach=false`,
index aged 4 months, working directory removed (the base entry's mechanism):

```
REAL-PULL   before=2  after=1     (real `git pull`, not a fetch)
```

So `git pull` prunes. Note the *mechanism* differs from the fixture's story:
`git pull` ran `git fetch` internally (E4) and the prune came from the spawned
fetch — which is exactly the S130 argument the entry makes, and also exactly what
the fixture's `pull` case actually executed.

### E7 — ATTACK: the round's own numerator is already stale at the tip

The r26 lesson states, at `corpus/lessons/round-26.md:32-35`:

> "The r25 "0 prunable, 3 locked" fleet census is history: S132 re-checks to
> **5 registrations, 0 prunable, 0 locked** even at `--expire=now`. The
> fleet is *currently* unexposed"

and `corpus/README.md:46` (tip) says the remaining F1 open items are
"keep-ref expiry unmeasured, fleet exposure numerator re-census".

Live read-only measurement of the **fleet root** at 2026-10-25 14:46, git 2.56.0:

```
$ git -C /home/vgpnk/Projects/shokunin worktree list --porcelain | grep -cE '^worktree |^locked |^prunable '
$ git -C /home/vgpnk/Projects/shokunin worktree list --porcelain | grep -c '^worktree '   # 5
$ git -C /home/vgpnk/Projects/shokunin worktree list --porcelain | grep -c '^locked'       # 0
$ git -C /home/vgpnk/Projects/shokunin worktree list --porcelain | grep -c '^prunable '    # 4
```

Four of the five fleet-root registrations are **prunable right now**, all with
the same reason ("gitdir file points to non-existent location"), and the
automatic prune path would take them:

```
$ git -C /home/vgpnk/Projects/shokunin worktree prune --dry-run
Removing worktrees/s3-nonauthor64: gitdir file points to non-existent location
Removing worktrees/root-closure-null-round: gitdir file points to non-existent location
Removing worktrees/s3-ready66: gitdir file points to non-existent location
Removing worktrees/native-mutation-proof: gitdir file points to non-existent location
$ git -C /home/vgpnk/Projects/shokunin worktree prune --dry-run --expire=now     # same 4
$ git -C /home/vgpnk/Projects/shokunin worktree prune --dry-run --expire=3.months.ago   # (no output)
$ git -C /home/vgpnk/Projects/shokunin worktree list --porcelain | grep -c '^worktree '  # still 5 (dry-run did not mutate)
```

The four prunable registrations are `native-mutation-proof`,
`root-closure-null-round`, `s3-nonauthor64`, `s3-ready66` — all hyaku wave
worktrees whose working directories are gone. Their admin `index` mtimes are
2026-10-21 (4 days old), which is why the **3.months.ago** auto threshold still
shields them but `--expire=now` and the default manual prune do not.

Why this contradicts S132: S132's own evidence file
(`lanes/souji/round2/evidence/r23-worktree-census.out`, sha256 `1ac71c4f…`) says
the four hyaku registrations had `gitdir_target_exists=yes` and index mtimes of
2026-10-21, and reported "no output — none prunable" at all three expiries.
Today the targets are gone:

```
$ for p in /fast/scratch/hyaku/{native-mutation-proof,root-closure-null-round,s3-nonauthor64,s3-ready66}/.git; do printf '%s exists=' "$p"; [ -e "$p" ] && echo YES || echo NO; done
/fast/scratch/hyaku/native-mutation-proof/.git exists=NO
/fast/scratch/hyaku/root-closure-null-round/.git exists=NO
/fast/scratch/hyaku/s3-nonauthor64/.git exists=NO
/fast/scratch/hyaku/s3-ready66/.git exists=NO
```

So the direction of the drift is exactly the F1 mechanism: the working
directories were removed, which turns four registrations from "live" to
"prunable" with **no receipt and no souji involvement**. The S132 row's claim
cell — "the fleet repo has 5 registrations, 0 prunable and 0 locked … so the
round-12 '0 prunable, 3 locked' figure is stale" — is true as a 2026-10-23
reading and **false as a statement about the fleet now**. It is dated in its
locator ("2026-10-23") but the lesson's prose at :32-35 upgrades it to the
present tense ("The fleet is *currently* unexposed") and the README next-step
line still says "fleet exposure numerator re-census".

Fleet-wide (all 22 repos, same command shape as the r12 census at
`census/round-12/scout-surfaces.md:41`):

```
repos=22 registrations=32 locked=3 prunable=5
```

against the r12 baseline printed in the same file, "22 repositories, 52 worktree
registrations, 3 locked, 0 prunable". So the fleet numerator has moved twice
over: registrations 52 → 32, and prunable 0 → 5. The lane's own census tool
(`tools/souji-census.sh`) counts worktree *lines* (`count_worktrees`, via
`git worktree list | grep -c .`) and has no prunable/locked column at all
(`grep -c prunable tools/souji-census.sh` → 0), so the lane cannot re-derive this
numerator from its own instrument — it must be re-censused read-only, and the
S132 number is a 2-day-old snapshot of a moving quantity.

### E8 — F1 remaining open items, per PROVINCE + README (the delivered enumeration)

**PROVINCE.md** (`souji-shokunin/PROVINCE.md`):
- `:63-65` — F1 is a **Frontier** row: "F1 git-native housekeeping vs receipts —
  git's own deleters (`maintenance --auto` worktree-prune, gc/reflog grace
  periods) acting on surfaces souji gates." A frontier row moves to Core only
  with an admitted `corpus/knowledge/` entry **and** a SKILL rule
  (`PROVINCE.md:61-62`).
- `:131-132` — "F1 as a whole stays frontier; how long jj keeps a
  `refs/jj/keep/*` ref remains unmeasured."
- `:120` — keep refs are "never durable receipt roots".

**corpus/README.md**:
- `:39` (tip) — coverage-map row now lists four F1 entries (two base + two new).
- `:46` (tip) — the F1 next-step: "the trigger set and the measured prune are now
  held (round-26 entries `knowledge/git-auto-maintenance-trigger-set{,-r23}.md`,
  S128-S132); remaining: keep-ref expiry unmeasured, fleet exposure numerator
  re-census."
- `:216` — F1-jj row: "F1 itself stays frontier; keep-ref expiry unmeasured".
- `:228-231` — r17 Frontier: keep-ref expiry measurement "— unrun"; the
  conservative-refusal cost "stays disclosed, not narrowed".

**corpus/lessons/round-26.md** residuals: `:68` R-r26-1 (maintenance
strategy/task scope unmeasured), `:72` R-r26-2 (two staged rows un-cited),
`:76` R-r26-3 (keep-ref expiry still not measured — and it points at
`git-auto-maintenance-trigger-set.md` for the claim boundary, but that file
contains **no** keep-ref content: `grep -cE 'keep-ref|refs/jj' corpus/knowledge/git-auto-maintenance-trigger-set.md`
→ 0. The real keep-ref source is `corpus/knowledge/jj-colocation-receipts.md:108`:
"Keep-ref lifetime. The docs read do not state it." — a dangling cross-ref).

**Enumerated remaining F1 open items:**

1. **Keep-ref expiry** — unmeasured (PROVINCE:131-132; README:46, :216, :228-231;
   round-26 R-r26-3). Source of truth: `jj-colocation-receipts.md:108` says the
   docs do not state it. Cross-ref in R-r26-3 is dangling (see above).
2. **Fleet exposure numerator re-census** — README:46. Now demonstrably stale
   (E7): fleet root is 5 registrations / 0 locked / **4 prunable**; fleet-wide
   32 registrations / 3 locked / 5 prunable.
3. **`git maintenance run` strategy/task scope** — round-26 R-r26-1. Verified
   still open at v2.56.0: `builtin/gc.c:1502-1530` `geometric_strategy` carries
   six tasks, and `TASK_WORKTREE_PRUNE` is `SCHEDULED | MANUAL, SCHEDULE_WEEKLY`
   (`:1524-1527`) — i.e. the weekly-schedule test inside `if (opts->schedule)`
   is what excludes it from an `--auto` run only because the MANUAL type admits
   it (`:718-720` `maintenance_task_worktree_prune` runs it whenever
   `cfg.prune_worktrees_expire` is set). Which tasks run under which strategy is
   not measured.
4. **`git am` trigger** — named at `builtin/am.c:1942` (E4) but never
   behaviourally measured anywhere, lane or campaign (E5).
5. **`git remote update` / `git remote add -f` / `git submodule update --remote`**
   — spawn a child `git fetch` and inherit the trigger (E4), but are named in
   neither new entry and are not in the fixture.
6. **Manual `git gc` prune path** — D4 says it was "read in code only, not
   separately reproduced"; still un-reproduced at tip.
7. **Concurrent-writer corruption under `--prune=now`** — D11/B:21, still not
   simulated.
8. **Base entries still carry the 2.55.0-only recheck** (D6, D9). Both `recheck:`
   commands still pass on 2.56.0 (E3), so the *stale-verification* note can be
   discharged by a re-verification — but that has not been done, and `git
   worktree prune --expire` defaults differ by path: `builtin/worktree.c:259`
   (`prune`) and `:1144` (`list`) both default `expire = TIME_MAX`, while the
   automatic task passes `cfg->prune_worktrees_expire` = `3.months.ago`
   (`gc.c:144`). A manual `git worktree prune` with no `--expire` therefore
   prunes the four fleet-root registrations (E7) while the automatic path
   currently does not.

## Findings

1. **Gap list delivered (E2).** D3 — "these are call sites only — whether each
   prunes was not fixture-run, and other trigger paths are not excluded." — is
   the single sentence the C2 admit set exists to close, at
   `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:25`. Eleven further
   deferral/limit sentences (D1-D2, D4-D12) are listed verbatim with locations
   in E2. The C2 expansion claim is grounded: entry A closes the trigger-set
   half (D2), entry B the behavioural half (D3), and both new entries' own
   "What this does NOT establish" blocks carry the surviving limits forward.

2. **The trigger set is closed over the whole v2.56.0 tag** (E4): exactly five
   `run_auto_maintenance` call sites (`am`, `commit`, `fetch`, `merge`,
   `rebase`), `pull` has none. Entry A's "exactly five of the candidate
   builtins" is correct and the candidate set is provably complete.

3. **ATTACK — the `pull` case in the admitted fixture never runs `git pull`**
   (E5). `fixtures/r23-trigger-prune.sh:144-146` runs `git remote add origin`
   then `git fetch -q origin`. The evidence row
   `id=SOUJI-R23-TRIGGER-pull case=pull before=2 after=1` therefore witnesses the
   *fetch* path a second time. The entry's `git pull` claim is true (E6: real
   `git pull` prunes, 2→1, measured independently in scratch) but the cited
   witness does not support it.

4. **ATTACK — the `merge` and `rebase` cases are confounded by an intervening
   `git commit`** (E5). The count drops at the commit, not at the measured
   command (`after_commit=1, after_merge=1`). `git commit` is itself a trigger
   command. Isolated measurement confirms merge and rebase do prune on their own
   (2→1 each), so the *claim* holds but the *fixture* cannot discriminate the
   trigger — the r24-M19 "witness cited for more than it runs" class recurring.

5. **ATTACK — `git am` is in the named trigger set but has no behavioural case**
   (E5): no `am` case in the fixture, none anywhere in the campaign corpus.

6. **ATTACK — the round's fleet numerator is stale at the tip** (E7). The fleet
   root is 5 registrations / 0 locked / **4 prunable** right now (default manual
   prune and `--expire=now` both list all four); fleet-wide 32 registrations /
   3 locked / 5 prunable vs the r12 baseline 52 / 3 / 0. The lesson's
   present-tense "The fleet is *currently* unexposed"
   (`corpus/lessons/round-26.md:32-35`) is false as written; S132's row is a
   2026-10-23 snapshot whose locator says so but whose prose does not.

7. **The trigger set's denominator is wider than five + `pull`** (E4).
   `git remote update` (`builtin/remote.c:1717`), `git remote add -f`
   (`builtin/remote.c:104`) and `git submodule update --remote`
   (`builtin/submodule--helper.c:2530`) each spawn a child `git fetch` and
   inherit the trigger exactly as `pull` does. Entry A's "denominator" framing
   (entry A, "Lane link and consequence") does not carry them.

8. **`git am`/`git remote *`/`git submodule update` are the two concrete named
   gaps in the denominator** — with E5's `am` gap this is the same gap the base
   entry flagged at A:25 ("other trigger paths are not excluded"), still not
   excluded after the expansion.

9. **R-r26-3's cross-reference is dangling** (E8): the lesson points at
   `git-auto-maintenance-trigger-set.md` for the keep-ref claim boundary; that
   file has zero keep-ref content. The keep-ref boundary lives at
   `corpus/knowledge/jj-colocation-receipts.md:108`.

10. **The lane cannot re-derive the F1 numerator with its own instrument**
    (E7): `tools/souji-census.sh` counts worktree lines and has no
    prunable/locked column; the exposure census is a separate read-only pass
    whose output the lane does not currently hold.

11. **The base entries' `recheck:` lines still pass on the live host** (E3) —
    both the `gc.c` grep (expect 2) and the `git-gc` man grep (6 values). The
    2.55.0-only verification note (D6, D9) is dischargeable but undischarged.

## Attack log

- **A1 (C2 evidence, coverage axis) — the admitted fixture's `pull` case does
  not run `git pull`.** `fixtures/r23-trigger-prune.sh:144-146` runs
  `git remote add origin "$rem"; g "$repo" fetch -q origin`. The claim in
  `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` ("under `git pull`",
  "pull spawns `fetch`") is therefore not witnessed by the row it cites
  (`id=SOUJI-R23-TRIGGER-pull`). The behaviour is nonetheless true — measured
  independently here (real `git pull`, 2→1, scratch only). The preregistration's
  C2 counters do not test this, so it is not a counter failure; the entry's
  "MEASURED" claim is over-stated relative to its witness.

- **A2 (C2 evidence, coverage axis) — the admitted fixture's `merge` and
  `rebase` cases are confounded by an intervening `git commit`.** The commit
  precedes the measured command in both cases and is itself a trigger command;
  the count reaches 1 at the commit (`after_commit=1 after_merge=1`). The
  prunable registration may be gone before `merge`/`rebase` is reached, so the
  case cannot attribute the prune to `merge`/`rebase`. Isolate the merge or
  rebase by ageing the registration **after** the topic commit. The behaviour is
  true in isolation (2→1 each, measured here). Same defect class as
  `corpus/lessons/round-24.md` R24-M19.

- **A3 (C2 registry/lesson, calibration axis) — the round's own fleet numerator
  is stale at the tip, and the lesson asserts it in the present tense.** Live
  read-only measurement 2026-10-25 14:46: fleet root 5 registrations / 0 locked /
  **4 prunable** (default manual prune and `--expire=now` both list all four;
  `--expire=3.months.ago` lists none, because the admin index mtimes are
  2026-10-21); fleet-wide 22 repos / 32 registrations / 3 locked / 5 prunable,
  against the r12 baseline of 22 / 52 / 3 / 0 at
  `census/round-12/scout-surfaces.md:41`. `corpus/lessons/round-26.md:32-35`
  says "The fleet is *currently* unexposed" — false as written. The S132 row's
  claim cell ("0 prunable and 0 locked … the round-12 figure is stale") is a
  2026-10-23 reading whose locator is dated but whose lesson prose is not.
  README:46 already names "fleet exposure numerator re-census" as remaining.

- **A4 (C2 admit set, coverage axis) — the trigger-set denominator excludes
  three commands that inherit the trigger.** `builtin/remote.c:1717`
  (`git remote update`), `builtin/remote.c:104` (`git remote add -f`),
  `builtin/submodule--helper.c:2530` (`git submodule update --remote`) each
  spawn a child `git fetch` and reach `run_auto_maintenance` by process spawn,
  the mechanism entry A documents for `pull`. Entry A calls the trigger set "a
  named, per-command set" and gives the census its "denominator"; the
  denominator as named is incomplete.

- **A5 (C2 admit set, coverage axis) — `git am` is named as a trigger and
  never measured.** `builtin/am.c:1942` is one of the five call sites
  (tag-wide search, E4). No `am` case exists in the admitted fixture, and none
  exists anywhere in the campaign corpus (`grep -rniE '\bgit am\b|case=am\b'` →
  empty). Entry A names it; entry B does not measure it and does not say so.

- **A6 (cross-reference, calibration axis) — round-26 R-r26-3 points at a file
  with no keep-ref content.** `corpus/lessons/round-26.md:76-79` says "See
  `git-auto-maintenance-trigger-set.md` for the claim boundary";
  `grep -cE 'keep-ref|refs/jj' corpus/knowledge/git-auto-maintenance-trigger-set.md`
  → 0. The keep-ref boundary is `corpus/knowledge/jj-colocation-receipts.md:108`.

- **A7 (scope, not a defect) — the F1 frontier is still frontier.** Two more
  admitted entries do not move F1 to Core: PROVINCE.md:61-65 requires an
  admitted entry **and** a SKILL rule, and `SKILL.md:101` still cites only the
  base entry `git-auto-maintenance-prunes-worktrees.md` — the two new entries
  are not cited by SKILL.md. F1 stays frontier by the lane's own rule; the
  remaining open items are the eight enumerated in E8.

## Notes / limits

- No counter, predicate, target or case set is proposed for change here. A1-A6
  are reported as attacks on the *evidence quality and currency* of the C2
  admit set, per the preregistration's "if you believe a counter is wrong or
  gameable, report it as an ATTACK" rule. Nothing in the frozen counters
  (C1/C2/C3 K1-K4) was exercised against data by this seat.
- No file outside `.ufo/waves/round-26/w1/ScoutF1Gap.md` was written. No
  `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no signals.
  The lane's tracked files are unchanged (`git status --porcelain` on
  `corpus/ tools/ tests/ SKILL.md PROVINCE.md` → no tracked modifications).
  The pre-existing untracked `tests/fixtures/__pycache__/` and
  `tools/__pycache__/` were present before this seat and were not created or
  modified by it (this seat ran every Python invocation with `python3 -B`).
- Fleet-root commands were strictly read-only (`worktree list --porcelain`,
  `worktree prune --dry-run`, `worktree list` counts). The `--dry-run` prune
  mutated nothing: registration count was 5 before and after, and all four
  `.git/worktrees/` admin directories are still present
  (`native-mutation-proof`, `root-closure-null-round`, `s3-nonauthor64`,
  `s3-ready66`). No `git worktree prune` (mutating form) was ever run anywhere.
- `/home/vgpnk/Projects/shokuknow` was read only: two corpus files and the
  fixture/evidence bytes under `lanes/souji/round2/`. Nothing was written,
  committed, fetched or pushed there, and no campaign tool was run there. The
  scratch experiments are my own scripts under
  `/var/tmp/souji-r26-ScoutF1Gap/exp/`, not the campaign's fixture.
- `considerthese/` is absent in this lane (one report line, per the r26
  preregistration's ASSIMILATION section).
- Scratch removed on completion: `/var/tmp/souji-r26-ScoutF1Gap/`.
