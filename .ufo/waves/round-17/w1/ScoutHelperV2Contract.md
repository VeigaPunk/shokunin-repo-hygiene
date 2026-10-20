STATUS: DONE — jj-lane.sh v2 contract extracted line-exactly from source; no jj/git-write execution performed (per assignment), so runtime display forms are marked [INFERENCE].

# jj-lane.sh v2 — the contract lane docs must cite

Artifact: `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh`
- 711 lines, mode 755, sha256 `3369dc27b4909a9d1c2def774b128fb4a8cb71953ac9b12de4c8519b9024e421`
- HEAD commit `14df5b933128bc04495b7b646672956db3d7ac03` ("jj-lane.sh v2 …"), clean (no worktree diff)
- v1 = `67a3123` (605 insertions / 162 deletions v1→v2)

Method: static reads only. `jj` was never invoked (probe rule), the helper was never run, the selftest was never run. Selftest citations are its *source* (pinned expectations), not observed passes; the "selftest 45/45 (28 cases fail on v1)" claim is quoted from the commit message, not verified here.

Lane state observed (context, not part of the contract): `/home/vgpnk/Projects/shokunin/souji-shokunin/.jj` exists, HEAD is detached at `5fa6017…`, `refs/jj/keep/*` present, jj repo config lives outside the repo at `~/.config/jj/repos/acda0786460d4a89c9c1/config.toml` (`trunk()="master@origin"`, `snapshot.auto-track="none()"`, `user.name="souji-shokunin"`). `lane.branch` is **not** in `.git/config` — so `state` here resolves via `detect_branch` fallback (jj-lane.sh:159-167), not via the recorded mirror.

---

## 1. Deletion / rename admission (jj-lane.sh:523-551)

The only paths that enter a commit are the ones named on the command line. There is no "commit everything" path.

Canonicalization + hard guards, in order:

```
526|    q=$(realpath -m --relative-to=. -- "$p" 2>/dev/null) || { err "bad path: $p"; exit 1; }
527|    case $q in
528|      ''|.|..|../*|/*) err "path escapes the lane root: $p"; exit 1 ;;
529|    esac
530|    case $q in
531|      .git|.git/*|.jj|.jj/*)                err "repo internals are never committable: $p"; exit 1 ;;
532|      .ufo|.ufo/state|.ufo/state/*|.ufo/watchdog.log)
533|        err "driver runtime is never committed by a lane: $p"; exit 1 ;;
534|    esac
```

Four-way classification of each surviving path (:535-549):

| class | test | admitted as |
|---|---|---|
| directory | `[ -d "$q" ]` :535 | `req+=(q)`, `fs_dirs+=(root:"q")` — **no** `--include-ignored` (:536, :563-565) |
| file / symlink (incl. dangling) | `[ -e "$q" ] \|\| [ -L "$q" ]` :537 | `req+=(q)`, `files+=(q)`, `fs_files+=(root-file:"q")`; >10 MiB needs `--allow-large` (:538-542) |
| pending deletion | in branch tip: `git cat-file -e "refs/heads/$branch:$q"` :543 | `req+=(q)`, `fs_req+=(root-file:"q")` — deletion lands |
| anything else | else :547 | `warn: skipping missing path` :548 (non-fatal) |

The deletion arm is the whole v2 addition; its comment is explicit (:544-545): *"Deleted or renamed-away path present in the branch tip: include it so the commit records the deletion."* The oracle is the **branch tip ref**, not the git index and not `@-`. That is safe because `@-` is forced to equal the tip before the commit (see §2).

`req`/`fs_req` are the jj pathspecs; they are the *only* matcher passed to diff and commit:

- `jj diff --summary -- "${fs_req[@]}"` :570
- `jj commit -m "$msg" -- "${fs_req[@]}"` :604

Consequence to document: a **rename/move is landed only when BOTH paths are named**. `mv a b` then naming only `b` lands an ADD of `b` and leaves the `a` deletion in the working copy (see §3). Naming both is exactly what selftest `z24` pins (:662-671):

```
664|  mv "$D/LOG.md" "$D/RENAMED.md"
666|  out=$("$H" commit "$D" --as testlane -m mv -- LOG.md RENAMED.md 2>/dev/null)
668|  ! git -C "$REMOTE" cat-file -e "$BR:LOG.md" 2>/dev/null || return 1
669|  git -C "$REMOTE" cat-file -e "$BR:RENAMED.md"
```

`souji-quarantine` moves therefore must pass `-- <old> <new>`; `z24` is the only pinned rename case and it names both sides.

Sweep guards after the commit (:609-656) also accept a move in either representation: the `R`/`C` arm parses all three git/jj summary shapes and validates **both** sides against `req` (:633-645); an unparseable rename line is a hard refusal, not a guess (:643).

## 2. Phantom-deletion refusal (jj-lane.sh:617-656)

```
617|  # 2. Every changed path falls under the requested paths; .ufo/state never.
618|  # 3. Phantom deletion: refuse a committed deletion of a file that still
619|  #    exists on disk (a nested empty .git dir makes jj see deletions).
...
630|  while IFS= read -r line; do
...
649|    case $line in
650|      D\ *)
651|        if [ -e "$cpath" ] || [ -L "$cpath" ]; then
652|          err "commit would delete $cpath but it exists on disk (nested repo?) — refusing"
653|          exit 1
654|        fi ;;
655|    esac
656|  done < <("$JJ_BIN" --ignore-working-copy diff --summary -r "$hash" 2>/dev/null)
```

Exact semantics:

- It inspects the **commit's own delta** (`-r "$hash"` :656), not the working copy.
- A `D` entry is legal only if the path is absent from disk (`-e` *and* `-L` false, :651); a symlink counts as present.
- The refusal fires **after** `jj commit` (:602-605) and after `hash=$(jj_ids '@-' …)` (:606), but **before** `bookmark set` (:658). Therefore: bookmark stays put (:609 comment), exit 1, no `landed`, nothing pushed. The just-created commit is left as `@-` in the local jj repo; the next helper run sees `@- != tip` and re-anchors an empty `@` onto the tip (:584-594), abandoning it.
- Trigger class: a nested `.git` (even empty) makes jj report deletions for files still on disk. Selftest `z7` (:418-427) builds `tests/vadv54-run/p/p6repo/.git`, then requires `commit … -- tests/vadv54-run` to fail **and** `one.txt` to survive at the remote tip (:424-425). This is C3(e)'s stub, and the guard is the reason a phantom deletion can never land.
- It is a last-resort guard, not a substitute for admission: a named path that exists is admitted as an add/modify, so a `D` line only appears through jj's own view (nested repo, stale snapshot).

## 3. `git mv`-staged rename, only the destination named

Observed from the helper code path: destination `b` exists on disk → admitted via :537-542 as `root-file:"b"`. The source `a` is never named, so it never enters `req`/`fs_req` and is never a jj matcher. `jj commit … -- root-file:"b"` (:604) therefore records only `b`. The commit's delta is `A b` (the parent still has `a`), so the sweep passes — `path_ok b` ok, no `D` line to trigger :651 — the bookmark moves (:658) and the push runs. **The result is a half-applied move: `b` added, `a` still present at the branch tip, the `a` deletion left uncommitted in `@`. No warning is emitted.**

Grounding that the staged state is irrelevant: jj ignores the git index — "The staging area will be ignored. For example, `jj diff` will show a diff from the Git HEAD to the working copy." and "Jujutsu will ignore Git's staging area." (https://docs.jj-vcs.dev/latest/git-compatibility/). So `git mv` buys nothing; the helper's unit is the disk state + the named pathspec. The staged index entry is not a guard either: staged-entry refusal exists only at **first colocation** (:415-418, selftest `z25` :673-680), never in `commit`.

[INFERENCE] With only `b` named, the pre-commit `jj diff --summary` may render the pair as `A b` or as `R a => b` depending on jj's copy detection; this changes nothing observable, because that diff is used only for the emptiness test (:570-578) and the commit itself is pathspec-limited to `b`. The committed delta cannot contain `a`.

To land the move in one commit: name both (`-- a b`). `a` is admitted by :543-546 (in tip, absent on disk), `b` by :537; `jj commit -- root-file:"a" root-file:"b"` records `D a` + `A b` (or `R a => b`; both accepted, §1), and the `D` guard passes because `a` is gone from disk. A second call naming `a` also works after the fact (admitted as a deletion), but it produces two commits and a window in which both paths exist.

## 4. What `warn: skipping missing path` now means (:547-548)

Emitted only when the canonicalized path is **not** a directory, **not** an existing file/symlink, **and not present in the branch tip**. It now means exactly one thing: *"this name is unknown — it is not a pending deletion, not a live path, and not a typo-free path in this branch"*. It is dropped from the commit set.

What it deliberately no longer means (v1 contrast, `git show 67a3123:scripts/hyaku/jj-lane.sh` :193-196):

```
193|    if [ -e "$p" ] || git ls-files --error-unmatch -- "$p" >/dev/null 2>&1; then
196|      echo "warn: skipping missing path $p" >&2
```

v1's oracle was disk-exists **or** index membership, so a missing path could be shrugged off even when it was a real pending deletion. v2 splits that case out: a genuine deletion never warns (it is admitted at :543). Operational reading for lanes: if you name a path you just deleted and get this warning, the path was **already** gone from `refs/heads/<branch>` (an earlier commit landed the deletion) or never existed there — verify with `git cat-file -e refs/heads/<branch>:<path>`, and do not expect the helper to invent a deletion.

Non-fatal by design. If *every* named path warns: `nothing to commit (no such paths)` and exit 0 (:551). Two other stderr-only warnings must not be confused with it: init's `warn: could not untrack <path>` (:462) and post-commit `warn: jj refused to track (ignored or over size limit), not committed: <paths>` (:662-666).

## 5. Output lines (:21-22, :57-60, :232-260)

- `landed <hash>` — **the only citable line**. Printed on **stdout** only after `git ls-remote origin refs/heads/<branch>` returns a tip equal to the local tip (:236-245) and, when this run's commit was given, after proving it is an ancestor of that tip (:246). Normal case :258.
- `rewritten <old> -> <new>` — printed **before** `landed` only when push recovery rebased this run's commit so the old hash is no longer an ancestor of the remote tip; the new hash is found by change id (`heads(::bookmarks(b) & change_id(cid))`, :246-253). The pair is `<old> <new>`, and `new` need not equal the landed tip when later commits sit on top — cite only `landed`. Selftest `g2` pins precisely that: `$RW` non-empty, `$PH = remote_tip`, `$RW` an ancestor of `$PH` (:209-211).
- `nothing to commit` (:576-577) and `nothing to commit (no such paths)` (:551) print **no hash**, exit 0. Selftest `z21` asserts the output contains no 40-hex, `landed`, `pushed` or `committed` (:634-636).
- `state branch=<b> local=<40h> remote=<40h> ahead=<n> behind=<n> head=<attached\|detached> tracked=<n> untracked=<n>` (:179). `head=` is the only detached-HEAD signal lanes should read; there is no `@{u}`.
- Everything else (`err "…"`, warnings, jj failure excerpts) goes to **stderr** (:69-70 `err()`).

## 6. Exit codes

Global (:9-11, :57, :62): `0` ok / nothing to do · `1` failure · `3` committed but push failed (commit kept) · `64` usage. `jj not found` is `1` (:40); the fleet root is not a lane, `1` (:98-104).

| subcommand | 0 | 1 | 3 | 64 |
|---|---|---|---|---|
| `init <lane> <id>` | colocated + config written, ends by printing `state` | any prerequisite failure (not a clone, detached non-tip :404, merge/rebase in progress :407-414, unmerged index :413, staged index :415-418, init changed the index :490-499) | — | bad lane id (:372), wrong argc (:371) |
| `commit … -- <paths>` | `landed` (or `nothing to commit`) :670 | every guard: bad/escaping path :526-534, oversized file :540-542, `jj file track`/`diff`/`metaedit`/`commit` failure :561-605, non-tip parent :584-594, parent≠tip sweep :612-616, path outside request :628, phantom deletion :652, bookmark set :658-659 | `do_push` failed after the bookmark moved (:669) — **the commit is kept locally** | wrong argc/no paths/no `-m` (:507), bad `--as` (:508) |
| `push [--no-rebase] <lane>` | `landed` :698 / :702 | not a clone, not colocated, no branch/identity recorded (:684-690) | preflight, push, or `report_landed` failure (:694, :696, :697, :701) | no dir / usage (:683) |
| `state <lane>` | one state line, exit 0 | not a clone, no branch, refs not 40-hex (:168-172) | — | argc ≠ 1 (:156) |

Exit 3 is the operationally important one: **do not re-commit** — the commit exists and the bookmark points at it; run `push` again. `--no-rebase` (:692-698) is the driver's durability push: fast-forward only, no fetch, no rebase, so a moved remote is exit 3 with no recovery (that is what `inline.sh` `verify` treats as "not landed", inline.sh:121-125). Plain `push` retries at most 3 times and recovers **only** on stale-lease/moved-remote errors (:349-363); hooks, permissions, tracking, conflicts and content rejections are fatal on the first attempt (:359-360).

Pushes are never forced (`git push --remote origin --bookmark "$b"`, no `--force`, :350/:695) and preflight refuses anything but a fast-forward (:210-214) or a push range containing a foreign author/committer (:215-228), which is why *every* lane VCS write must go through the helper (`--as <lane-id>` or `protocol`, :516-517).

## 7. `.ufo` path rules — can `.ufo/waves/round-17/…` be committed? **Yes.**

Both case arms, verbatim:

```
530|    case $q in
531|      .git|.git/*|.jj|.jj/*)                err "repo internals are never committable: $p"; exit 1 ;;
532|      .ufo|.ufo/state|.ufo/state/*|.ufo/watchdog.log)
533|        err "driver runtime is never committed by a lane: $p"; exit 1 ;;
534|    esac
```

```
620|  path_ok() { # <path> — every changed path must lie under a requested path
621|    local cp=$1 rp2
622|    case $cp in .ufo/state|.ufo/state/*)
623|      err "commit would touch .ufo/state: $cp"; exit 1 ;;
624|    esac
```

The `.ufo` pattern is **exact**, not `.ufo/*`. Refused: the directory `.ufo` itself, `.ufo/state`, anything under `.ufo/state/`, and `.ufo/watchdog.log`. Admitted: every other `.ufo/...` path, including `.ufo/waves/round-17/w1/ScoutHelperV2Contract.md`. A changed `.ufo/state` path is also refused at sweep time (:622-624), so it cannot slip in through a broad directory name.

Observed evidence in this lane repo (`souji-shokunin`): `git ls-files -- .ufo` → **288 tracked paths**, including `.ufo/waves/round-13/w1/*.md` and `.ufo/waves/round-13/w1-dispatch.json`; `git ls-files -- .ufo/state .ufo/watchdog.log` → **0**; no root `.gitignore` exists and `.git/info/exclude` has no active patterns. So `.ufo/waves/**` is already a committed artifact namespace, and `.ufo/state` is not.

Two rules that must accompany this in docs:

1. `./` is refused, but as an escape, not as `.ufo`: `realpath -m --relative-to=. -- ./` → `.` → :528 `path escapes the lane root`. `realpath -m` also resolves `..` and symlinks, so `.ufo/waves/../state/x` and a `.ufo/waves` symlink pointing into `.ufo/state` both canonicalize to the refused `.ufo/state/...`.
2. Named **files** are tracked with `--include-ignored` (:556-561); named **directories** are tracked without it (:563-565, comment :556-558), so a lane-level ignore pattern can suppress a whole-directory name but never a named file. Name report files (or an unignored directory) — never rely on `--include-ignored` for a directory.

Correction the docs need: the header bullet at :28 (`` `.ufo`, `.ufo/state`, `.git` and `.jj` are never committable``) reads as if all of `.ufo` is refused; the code refuses only the four exact classes above. Selftest `z4` (:383-395) pins `.ufo`, `.ufo/state`, `.ufo/state/run.json` and `./` — it never tests `.ufo/waves`, so it does not contradict admission.

---

## Copy-paste recipe block for SKILL.md / PROVINCE.md

```text
Lane VCS writes go through scripts/hyaku/jj-lane.sh only (never git add/commit/push):
  jj-lane.sh commit <lane> --as <id> -m "<msg>" -- <path>...     # id = lane id or protocol
  jj-lane.sh push <lane>                                          # ff-only, lease-recovery
  jj-lane.sh state <lane>                                         # pure git; head=attached|detached
Cite ONLY the `landed <hash>` line. `rewritten <old> -> <new>` is informational and precedes
`landed` after recovery; `nothing to commit` prints no hash.
Name EVERY path that must change. A move/quarantine needs BOTH paths -- <old> <new>; naming only
the destination lands the add and leaves the old path (and its deletion) behind. A deleted path
is admitted when it is still in refs/heads/<branch>; `warn: skipping missing path` means the name
is neither on disk nor in the branch tip (already deleted, or a typo) and is dropped.
Refused always: `.git`, `.jj`, `.ufo` itself, `.ufo/state`, `.ufo/state/*`, `.ufo/watchdog.log`.
`.ufo/waves/<round>/...` IS committable. Files >10 MiB need --allow-large. Name files, not
directories, when an ignore rule might cover them.
Exit 0 = done/nothing; 1 = nothing moved; 3 = commit kept, push failed (retry `push`, never
re-commit); 64 = usage. Never leave your own `jj commit`/raw `git commit` under the tip, and
never rely on `@{u}` or HEAD -- read `head=`/`ahead=` from `state`.
```

Coverage note for C3(d): `SKILL.md` and `PROVINCE.md` currently contain **zero** `jj` mentions (grep over both exact files, case-sensitive: no matches). The recipes are absent, not stale — they must be added whole, and this block is the contract they must match. The driver already assumes it: `inline.sh:32-37` (state is pure git over `refs/heads`/`origin`, never `@{u}`), `inline.sh:121-125` (`push --no-rebase`; failure = "not landed"), `inline.sh:126` (warns on leftover uncommitted changes — exactly the half-move residue of §3).

## Commands run (all read-only)

- `read` whole `scripts/hyaku/jj-lane.sh` + ranged reads :18-64, :150-230, :230-262, :300-560, :560-672, :673-711; `grep -n` numbered ranges :505-560, :610-672, :230-262, :18-64, :150-230, :340-366, :560-610, :636-680
- `sha256sum`/`stat`/`wc -l` on the helper → digest and 711 lines above
- `git -C /home/vgpnk/Projects/shokunin log/diff/status/show` — helper lineage (`67a3123` → `14df5b9`), v1 :193-196, clean worktree
- `grep -n 'staged entries|could not untrack|detached'` → :404, :413, :417, :462, :582
- `read` selftest ranges :1-73, :74-120, :193-212, :370-430, :636-680; `grep` for `phantom|rename|.ufo|landed|deletion`
- `git -C …/souji-shokunin ls-files -- .ufo | wc -l` → 288; `ls-files -- .ufo/state .ufo/watchdog.log | wc -l` → 0; `read .git/info/exclude`; `config --file .git/config --list`; `read .jj/repo/config-id` + external `~/.config/jj/repos/acda0786460d4a89c9c1/config.toml`; `for-each-ref refs/jj`; `symbolic-ref -q HEAD` → empty (detached)
- `read` https://docs.jj-vcs.dev/latest/git-compatibility/ (staging-area ignored; colocated import/export on every command)
- No installs or upgrades; no `jj` invocation; no writes outside this report path.

## Verdict and smallest fix

- Contract as coded: **holds** (all seven questions answered at exact lines above; deletion admission :543-546, phantom refusal :649-654, additive-only `git mv` half-move, warning semantics :547-548, `landed`/`rewritten` :246-258, exit table :57/:62/:669/:694-702, `.ufo` arms :530-534 / :622-624).
- Documentation gap: **fails** — no jj recipe in `SKILL.md`/`PROVINCE.md`; and the helper header at :28 overstates the `.ufo` refusal (a reader would wrongly conclude `.ufo/waves/round-17/...` is refused, while 288 such paths are already tracked).
- Smallest fix: paste the recipe block above into `SKILL.md` (one pointer line in `PROVINCE.md` if it indexes skills), and reword `jj-lane.sh:28` to `` `* .ufo` itself, `.ufo/state/**`, `.ufo/watchdog.log`, `.git`, `.jj` are never committable (`.ufo/waves/**` is)` ``. No code change is required for the contract itself.

## Remaining unknowns

- [INFERENCE] jj's pre-commit diff rendering of a filesystem rename (`A b` vs `R a => b`) — unobservable without executing jj; harmless either way (§3).
- Not observed: whether `jj file track --include-ignored -- root-file:"a"` succeeds for a path deleted from disk but present in the tip. Selftest `z23`/`z24` are written to require exactly that outcome (:652-671), but I did not run them; the code path assumes success and aborts with exit 1 otherwise (:559-561).
- Not observed: the selftest's 45/45 claim, and which of the 28 v1 failures are the rename/phantom cases (commit message only).
- Out of scope: C1/C2/C3(a,b) counting claims; only §7 and the doc gap touch C3(d)/(e), and my lane-state notes are context, not a verdict on colocation correctness.
