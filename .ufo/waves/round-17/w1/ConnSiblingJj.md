STATUS: DONE — C3 sibling-overlap scan complete; helper v2 closes six helper-owned hazards, four souji-owned seams remain, one C3(e) premise is stale at base.

# ConnSiblingJj — C3 sibling-overlap scan (hyaku/jj-w1 → souji round 17)

Seat: ConnSiblingJj (connector, leaf). Advisory only; no lane file, helper, or other lane was edited. No `jj` subcommand was run (any repo). No git write. No subagent.
Base: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `5fa6017ddcae9f6bd4412df44765f6360cb16294` (branch master, HEAD detached, `.jj` present).
Fleet root: `/home/vgpnk/Projects/shokunin` @ `df54adf2` shape, **plain git** — `test -d .jj` false, `git for-each-ref refs/jj | wc -l` → `0`.
Tooling: none installed or upgraded (jj 0.45.1 and git 2.56.0 already present; pacman not used).

## 1. What the sibling reports say, and what has since landed

Read non-recursively: the 68 files in `.ufo/waves/hyaku/jj-w1/reports/` were listed; these were read in full or head: `JjAuditSouji`, `JjTrialSouji`, `JjSentinelHelper`, `JjAuditFleetCommit`, `JjTrialFleetRoot`, `JjAuditWatchdog`, `JjAuditClosurePrompt`, `JjCriticProtocol`, `JjCriticRollback`, `JjConnectorProvinces`, `JjAuditInlineSh`, `JjAuditSourcesCensus`, `JjAuditTsukuroi`, `JjTrialKama`, `JjTrialTameshi`, `JjTrialMado`, `JjAuditKama`, `JjAuditMado`, `JjRevengerLaneJjState`.

The wave's write-path work has largely landed upstream. Verified, not assumed:

```
$ git -C /home/vgpnk/Projects/shokunin show --stat --oneline 14df5b9 | head -5
14df5b9 ops(hyaku): jj-lane.sh v2 — fast-forward-only pushes, remote-rewrite stop, rebase without
        --ignore-immutable keeping the --as committer, branch bound at init, canonical paths as
        filesets, .ufo/state + large-file + phantom-deletion + sweep + foreign-identity guards,
        deletions/renames land, realpath lock, single citable 'landed <hash>', push --no-rebase
        for the driver; state falls back to git detection for every lane; selftest 45/45 ...
 scripts/hyaku/inline.sh           |  13 +-
 scripts/hyaku/jj-lane-selftest.sh | 591 ++++++++++++++++++++++++++++++++-----
 scripts/hyaku/jj-lane.sh          | 767 +++++++++++++++++++++++++++++++++++++++--------
$ sha256sum scripts/hyaku/jj-lane.sh
3369dc27b4909a9d1c2def774b128fb4a8cb71953ac9b12de4c8519b9024e421  scripts/hyaku/jj-lane.sh
```

Spot checks inside v2 (read-only): canonical path guard `.git|.jj|.ufo|.ufo/state|.ufo/watchdog.log` then `realpath`; branch-tip deletion admission (`git cat-file -e "refs/heads/$branch:$q"` at `:543-547`, still warns `skipping missing path` only for paths absent from both disk and branch tip, `:548`); phantom-deletion guard comment and refusal at `:618-625`; `--as` allow-list `{lane id, protocol}` near `:490`; lock/err keyed on `realpath`. `b8afbd0` also updated `scripts/hyaku/lane-addendum.md` (§4: never mutating jj/git, branch-ref ancestry, cite `landed`, never `@{u}`/`--abbrev-ref HEAD`) and `scripts/hyaku/closure-prompt.md:23-29,49-57` (same, plus "never `git add`/`git commit`/`git push` or a mutating jj command in the lane").

Lanes have since been re-initialised: `mado/tameshi/kama` repo configs now carry `snapshot.auto-track = "none()"` and their own identities (config-ids `0c6bba43…`, `900fa08b…`, `e3435e31…`; the ids in `JjSentinelHelper` are stale). Keep refs have grown: mado 39, tameshi 27, kama 22; all three HEADs detached.

Still open upstream (verified):
- `PROTOCOL.md` has **zero** `jj`/`jujutsu` matches; `:119-121` and `:230-231` still define closure ancestry as `git merge-base --is-ancestor <hash> HEAD`, and `:177` still excludes only `*/.git/*` from the activity scan. `lane-addendum`/`closure-prompt` say the opposite (branch ref). The "guaranteed delivery channel" is the stale one.
- Fleet-root writers remain jj-blind: `grep -n '\.jj\|jj-lane' scripts/hyaku/fleet-commit.sh scripts/shokunin-watchdog.sh scripts/hyaku/append-closure.py` → no output. Harmless today (fleet root plain, 0 jj refs), blocking if the root is ever colocated (`JjAuditFleetCommit` F3-F5, `JjTrialFleetRoot` F5/F6, `JjAuditWatchdog` F1-F3).

## 2. Adjacency table (the cross-domain line)

Owner codes: **H** = helper/orchestrator (`scripts/hyaku/*`, `PROTOCOL.md`, fleet scripts); **S** = souji (`tools/souji-*`, `SKILL.md`/`PROVINCE.md`, `corpus/knowledge`); **L** = another lane (read-only for souji).

| # | Hazard | Source (report) | Owner | C3 clause | State now / souji obligation |
|---|---|---|---|---|---|
| 1 | Non-fast-forward / sideways push rewrites remote; force-push recovery re-lands cited commits | SentinelHelper F1,F6; CriticRollback F1,F18; CriticProtocol F1 | H | (d) recipe depends | **Closed** by v2 (ff-only, remote-rewrite stop, `--no-rebase` driver push). Cite v2; do not re-fix. |
| 2 | Branch re-detected from `origin/HEAD` after HEAD detaches; lane work pushed to `main` | SentinelHelper F2; CriticRollback F4 | H | — | **Closed** by v2 (branch bound at `init`, `lane.branch`). |
| 3 | Path guard bypassed by `./`, `.ufo`, `.ufo/state`, `./.ufo/state/<f>`; `.ufo/state` unignored in 20/21 lanes | SentinelHelper F3; trials (kama/mado/tameshi) | H (guard) + L (`.gitignore`) | — | **Closed** at commit path by v2 sweep/state guards; per-lane `.gitignore` still lane-owned. |
| 4 | Lock keyed on `basename`; one `jj-push.err` shared by all lanes | SentinelHelper F4 | H | — | **Closed** by v2 (`realpath` key). |
| 5 | `--as` unbound to the lane | SentinelHelper F8 | H | (d) | **Closed** by v2 (`lane id \| protocol`, else exit 1/64). |
| 6 | Helper dropped the deletion half of `git mv`/`git rm`; pure deletion reported success | AuditSouji F1; TrialSouji hazard 1 | H | (d) | **Closed** by v2: branch-tip deletion admitted; phantom deletion refused. The C3(d) "name BOTH paths" recipe is now backed by code (`:543-547`, diff/sweep gates). |
| 7 | `nothing to commit` then `pushed <stale tip>`; `committed` hash orphaned by recovery | SentinelHelper F5,F7; CriticProtocol F1-F4 | H | (d) | **Closed** by v2 (single `landed <hash>`, refuses non-tip base, paths-as-filesets). |
| 8 | Fleet-root writers (`fleet-commit.sh`, `append-closure.py`, watchdog `commit_evidence`) publish the jj WC commit / lose `git add` to an index reset / push empty commits | AuditFleetCommit F3-F5; TrialFleetRoot F5,F6; AuditWatchdog F1-F3 | H | — | **Open, inert**: fleet root has no `.jj` and 0 `refs/jj`. Must stay plain or the writers must be converted; souji must not claim this. |
| 9 | `PROTOCOL.md` still certifies `ancestor of HEAD`, omits `.jj` from activity scan; addendum/closure already use branch-ref | ConnectorProvinces F5 (+ verified) | H | (d) | **Open**; orchestrator edit. Souji recipes must not quote PROTOCOL's HEAD check. |
| 10 | `sources-census.sh` parses jj conflict materialisation (`%%%%%%%` diff lines) as ordinary input; `validate` can print `ok` | AuditSourcesCensus F2 | H (fleet script) | — | Open; no VCS calls, so not a receipt hazard. Adjacent only. |
| 11 | `--not --all` and all-refs roots treat `refs/jj/keep` as durable ⇒ `SAFE(metadata-prune)` for a keep-only head | AuditSouji F3 | **S** | **(a)** | **Worktree partial (2/3)**: `souji-verify.sh:851` and `souji-vault-verify.sh:1039` now use explicit `refs/heads refs/tags refs/remotes`; **`souji-quarantine.sh:1069` is still all-refs**. See §3.5. |
| 12 | Unpushed-touching `--branches --not --remotes` blind to unbookmarked jj commits | AuditSouji F2; ConnectorProvinces F3 (helper bookmarks, so narrow window) | **S** | **(b)** | **Worktree partial (2/3)**: positive-side keep glob in verify `:267/:708/:994` and vault `:443/:896/:1182`; **quarantine `:299/:931/:1251` unchanged**. Pathless repo-root counts also include keeps (verify `:358`, vault `:520`): 6 in this lane, 2 of them empty commits. |
| 13 | Evidence text `durable-refs-only=yes` printed while the roots list includes `refs/jj/keep` | this report (§3.1) | **S** | **(a)** | **Fixed in verify `:856` + vault `:1047`** (roots now filtered, string true); **still false in quarantine `:1077`**. |
| 14 | `rev-parse HEAD` pinned as `measured_commit` in census consumers | AuditSouji F5: `census/round-13/run-verification.py:384,435`, `census/round-14/cache-demonstration.py:166,276` | **S** | — | Open, **not in C1/C3**; detached `@-` may be keep-only. Smallest follow-up: pin `refs/remotes/origin/<branch>`. |
| 15 | Index used as safety oracle (`git mv`/`git rm --cached` quarantine `:518,566`; `ls-files --error-unmatch`; `--no-optional-locks` gaps `verify:322,366`, `vault:488,532`, `census:1000`) | AuditSouji F4,F6 | **S** | (d) | Partially covered: quarantine must commit through the helper with both paths; the index questions remain untrusted. |
| 16 | jj write path bypasses hooks, clean filters, eol, and `info/attributes` | AuditSouji F7 | H (write path) + **S** (read-side guard) | — | Latent (no hooks/attributes today). Knowledge-entry row; C1/D2's non-regular-`info/attributes` refusal is a *read-side* guard and is unaffected. |
| 17 | Empty nested `.git` makes jj see phantom deletions of tracked files; the stub is a **generator artifact**, not a tracked or unignored file | TrialSouji hazard 1; RevPhantomStubScope | **S** (harness bytes/fixture) + H (v2 refusal) | **(e)** | See §3.3 — absent at rest, but HEAD `vadv54-harness.sh` (`966ee19a…`, `:46/47/:176`) recreates it on every run; worktree fix (`b55df92d…`, `:273-281`) makes it transient. C3(e) must pin the harness blob/commit that lands; residue is 4 keep-only commits. |
| 18 | tsukuroi gates accept `--revision HEAD` and certify `@-` (PASS on content the worktree violates) | AuditTsukuroi R1, 15 class-D sites | **L** (tsukuroi) | — | Out of souji's edit scope; carry the *fact* in the knowledge entry, never the fix. |
| 19 | Raw `git commit` inside an already-colocated lane; helper publishes foreign identity | CriticRollback B (live mado: 8 commits ahead, prompt predates the addendum); F6 | **L** (mado/L1) | — | Addendum now bans it; lane/reviewer conformance issue. |
| 20 | `kura` lane / `kura` history owner | — | **none** | — | **No such lane.** `ls /home/vgpnk/Projects/shokunin` (21 lanes), `grep -i kura MANIFEST.json shokunin.conf PROTOCOL.md` (0), `swarm-registry.json` (0), `kimi-shokunin` listing (no lane). Category empty; do not invent an owner. |

## 3. Decisive evidence

### 3.1 C3(a) is a live false SAFE in the lane today (and the string lies)

`for-each-ref`/`rev-list` with all refs is not hypothetical: souji's own lane holds 8 keep refs, 6 of them keep-only (`git rev-list --count <sha> --not refs/heads/master refs/remotes/origin/master` → `1`), 4 of them deleting the two p6repo files.

```
$ git -C souji-shokunin rev-list --count 0254661427750f47e04f20864c5091cfc74e2e0e --not --all
0                                        # ← current code path ⇒ SAFE(metadata-prune)
$ git -C souji-shokunin rev-list --count 0254661427750f47e04f20864c5091cfc74e2e0e \
      --not --branches --tags --remotes
1                                        # ← durable set ⇒ NOT-SAFE
$ git -C souji-shokunin rev-list --count HEAD --not --branches --tags --remotes    # control
0
```

Implementation constraints measured:
- `--not refs/heads refs/tags refs/remotes` is **fatal** (`rc=128 ambiguous argument 'refs/heads'`); use the option forms `--not --branches --tags --remotes` in `log`/`rev-list`.
- `for-each-ref --format='%(objectname)' refs/heads refs/tags refs/remotes` **does** work as prefixes (3 refs vs 11 all-refs here).
- Base-snapshot sites (`5fa6017`): `souji-verify.sh:351`, `souji-vault-verify.sh:517` (`--not --all`) and `souji-verify.sh:809-813`, `souji-vault-verify.sh:997-1001`, `souji-quarantine.sh:1069-1073` (all-refs roots); all three printed `durable-refs-only=yes` (`verify:817`, `vault:1005`, `quarantine:1077`) while including `refs/jj/keep`. The worktree has since fixed verify and vault; **quarantine still matches the base snapshot** (`:1069/:1077`), so the false attestation and the false-SAFE path remain in that tool — see §3.5.

### 3.2 C3(b): the keep glob is only correct on the positive side (silent-zero trap)

```
$ git -C souji-shokunin log --format=%H HEAD --branches --not --remotes -- tests/vault/vadv54-run/p/p6repo/one.txt
(0 lines)                                # today
$ ... --branches --glob=refs/jj/keep/* --not --remotes -- <same path>
4 lines: 0254661427, 1e0d8d1644, 719154dc9d, 41ab059d7d
$ ... --branches --not --remotes --glob=refs/jj/keep/* -- <same path>
(0 lines)                                # ← glob after --not is negated: silently inert
```

Plain-repo control (`/home/vgpnk/Projects/shokunin`, no `refs/jj`), same command shape on `PROTOCOL.md`: baseline 0, keep-glob 0 — byte-identical rows, as C3(b) requires. Untouched path in the lane (`tools/souji-verify.sh`): 0 — no spurious refusal.

Ordering is the whole move: a plausible-looking edit that appends the glob after `--not --remotes` passes review, runs clean, and enforces nothing.

### 3.3 C3(e): the stub is absent at rest but is *regenerated* by committed bytes

```
$ stat -c '%F' souji-shokunin/tests/vault/vadv54-run/p/p6repo/.git
stat: cannot stat ...: No such file or directory
$ ls -A  tests/vault/vadv54-run/p/p6repo
inner  one.txt
$ git show HEAD:tests/vault/vadv54-harness.sh | sha256sum
966ee19a4d33467f3ae2673c5649b4a62c0b9d15c4556501bdb9fd427ac0f3a4
$ sha256sum tests/vault/vadv54-harness.sh          # worktree, uncommitted ' M'
b55df92d5eb8589a0696cd9004eea6364033c59852012fd677834450349e42fa
$ git ls-tree -r --name-only HEAD -- tests/vault/vadv-49/fixture | wc -l
0
```

- **Do not document "stub removed" as durable.** At HEAD `tests/vault/vadv54-harness.sh` recreates it unconditionally with the run tree (`:46` `WORK=`, `:47` `rm -rf "$WORK"`, `:176` `mkdir -p "$P/p6repo/.git" …`). The current worktree snapshot keeps it only around the P6 case (`:277` `mkdir -- "$P/p6repo/.git"`, `:279` EXIT-trap `rmdir`, `:280` `run_tool`, `:281` `rmdir` with a non-empty refusal warning). That transient shape must land, and C3(e) must pin the harness blob/commit that lands — not the directory's absence today. `b55df92d…` is a **review-time snapshot** (the harness was edited three times during review); the pinned sha and P6 line range must be re-taken after the final edit at landing, and the report's acceptance row should cite the landed blob, never this snapshot.
- The 7 `tests/vault/vadv-49/fixture/{control,a1,a2,a4,a5,b,c}/.git` dirs are safe **because `git ls-files` has zero tracked paths beneath them**, not because of `tests/vault/vadv-49/.gitignore:1:fixture/`: jj's reserved-name skip runs before the ignore matcher, so an ignore rule cannot rescue a tracked subtree. Do not repeat the ignore-rule explanation.
- The phantom-deletion hazard is otherwise **historical**: 4 keep-only commits each delete `p6repo/{one.txt,inner/keep.txt}`; the other 2 keep-only refs change 0 files. After C3(b), receipts over those two paths become `NOT-SAFE` until jj drops the keep refs — disclose this pair explicitly.
- A round-17 regression fixture must **synthesise** `refs/jj/keep` and a nested `.git` in a `/var/tmp` repo; one that runs the live harness inherits the transient window in §5.

### 3.4 Sibling contradiction to resolve in the knowledge entry

`JjAuditSouji` F2 says `--branches --not --remotes` misses unpushed jj work; `JjConnectorProvinces` F3 shows the helper always bookmarks before push, so the query is correct under the helper and the earlier "use `--all`" advice **overcounts by 5:1**. C3's split is the correct third position and should be stated as such: `--branches --not --remotes` stays the unpushed semantics (census unchanged), keep refs are added **only** to the path-touching refuse checks, and `--all` is never used for either.

### 3.5 Delta since the first evidence run (worktree, uncommitted)

The tools moved while this report was being written (reviewer notice, then re-read). The committed base is still `5fa6017`; every change below is a working-tree ` M`, so acceptance must cite the landed commit, not these bytes.

| tool | sha256 (worktree) | C3(a) durable roots | C3(b) keep touching | jj selftest |
|---|---|---|---|---|
| `souji-verify.sh` | `8434313…` | fixed `:851` | fixed `:267,:708,:994` | J1, J1b, J2, J3 (`:1314-1317`) |
| `souji-vault-verify.sh` | `745fedb…` | fixed `:1039` | fixed `:443,:896,:1182` | **none** (`update-ref refs/jj` count 0) |
| `souji-quarantine.sh` | `df40751…` | **not fixed `:1069`** | **not fixed `:299,:931,:1251`** | none |

Measured consequences on the current worktree:

- **Pathless repo-root counts now include keeps and were not disclosed that way.** `git log --branches --glob=refs/jj/keep/* --not --remotes --oneline | wc -l` → `6` (old form → `0`). Of those 6, **2 are empty commits changing 0 files** (`dcc1512`, `dd2e322`) and 4 delete the two p6repo paths. Verify's J3 deliberately pins this for a repo-root receipt; the C3 disclosure ("hidden rewritten predecessors that touched the target") does not cover a pathless count or an empty commit. Decide explicitly: either disclose "any keep ref, even an empty commit, refuses a repo-root receipt", or scope keep inclusion to path-scoped checks (then J3 changes).
- **The glob-ordering trap is behaviourally pinned in verify**: with the glob after `--not`, J1 would see `0` touching commits and expect SAFE, so J1 fails. It is not pinned in vault (no jj cases) or quarantine (no implementation).
- **Quarantine still attests `durable-refs-only=yes` while including keeps** (`:1069/:1077`), so the live false-SAFE in §3.1 is still reachable through the quarantine receipt path.
- Plain-repo short-circuits are present (`jj_has_keep` / `for-each-ref refs/jj/keep/ | grep -q .`), so no non-jj repo pays a second log; the plain control in §3.2 still holds.

## 4. Proposed move (one, bounded)

**Finish the single ref-set vocabulary in `tools/souji-quarantine.sh` and make the same predicate executable in all three tools' selftests.**

1. Durable set: verify (`:851`) and vault (`:1039`) already use explicit `refs/heads refs/tags refs/remotes`. Apply the identical replacement to **quarantine `:1069`** (`for-each-ref` all-refs) and its `rev-list --not "${roots[@]}"` twin; `durable-refs-only=yes` at `:1077` becomes true only then.
2. Ephemeral set: verify (`:267/:708/:994`) and vault (`:443/:896/:1182`) already put `--glob='refs/jj/keep/*'` on the positive side. Apply it to **quarantine `:299/:931/:1251`**, before `--not --remotes`. Then settle the pathless case once (`verify :358`, `vault :520`, `quarantine :1105`): either scope keep inclusion to path-scoped checks, or keep J3's broad form and disclose "any keep ref, including an empty commit, refuses a repo-root receipt" — the current disclosure names only predecessors that touched the target.
3. Selftest parity: verify's J1/J1b/J2/J3 (`:1314-1317`) pin keep-touching refusal, the untouched-path SAFE, the keep-only durable-root refusal, and the pathless refusal; J1 also fails if the glob is moved after `--not`. **Vault has zero jj cases and quarantine has none** — mirror J1-J3 into both selftests, plus one empty-keep case for the pathless decision.
4. Record in `corpus/knowledge/jj-colocation-receipts.md` (exists, well sourced): the p6repo pair as the known-refused set under keep-touching (4 keeps, 2 empty keeps for the pathless count); C3(e)'s **durable generator** (`tests/vault/vadv54-harness.sh` blob at HEAD `966ee19a…`, transient-stub shape `b55df92d…`, re-pinned at landing), never "stub removed"; and the reserved-name-skip-before-ignore order (vadv-49 is safe only because 0 tracked paths lie beneath `fixture/`).

Affected axes: **coverage** (quarantine joins the predicate; vault/quarantine get the selftest pins verify already has), **calibration** (quarantine's false attestation removed; the pathless empty-keep effect becomes a stated rule instead of an accident; the three tools stop disagreeing on the same target), **operability** untouched by (a)/(b) except the intended conservative `SAFE → NOT-SAFE`, and the pathless decision is the one place a narrower rule avoids blanket repo-root refusals. C3(e) stays a bytes-pinned correction, not a directory claim.

## 5. Risks / second-order effects

- The two live fixture paths (`tests/vault/vadv54-run/p/p6repo/one.txt`, `inner/keep.txt`) are **already refused by verify and vault** in the worktree but still certifiable by quarantine — the three tools disagree on the same target today. Disclose; do not delete keep refs (a git write, and it would only accelerate GC of the same commits); do not special-case paths.
- Pathless keep inflation is broader than the C3 disclosure: 2 of this lane's 6 keep-only commits are empty (0 changed files), yet they make `unpushed>0` for a repo-root receipt. Either state that rule or scope keeps to path-scoped checks; leaving J3 pinning a rule the docs describe more narrowly is a calibration defect.
- Transient-window race (RevPhantomStubScope §5): while the P6 case runs (≤ `timeout 30`) the stub exists; a concurrent jj snapshot in the lane would see `D` rows for the two tracked files, and a directory-pathspec commit could ship them. The harness is manual and not wired to any gate; a file-exact helper commit never ships them. Landing the transient shape is necessary but not sufficient — keep the window short and keep the harness out of gate/runner chains.
- A plain repo with a detached HEAD whose commit is held only by HEAD flips `SAFE(metadata-prune) → NOT-SAFE` under (a). That is the intended durable-refs rule; pin it deliberately in the fixture rather than discovering it in a round.
- Keep refs are time-limited (jj GC grace). A fixture that reads the live lane would be flaky in both directions; synthesised refs are mandatory.
- The glob must be quoted in shell (`'refs/jj/keep/*'` / `"--glob=…"`) and placed before `--not`; `shellcheck` will not catch the ordering error. Verify's J1 does catch it behaviourally; vault and quarantine have no equivalent case, so a misordered copy there is silent.
- Do not extend the keep glob to the census `unpushed` column: C3 explicitly keeps it branch-based, and doing so would inflate it 6→? in this lane alone.
- Fleet-root colocation is the other large conditional risk, but it is H-owned and inert at 0 jj refs; souji's C3 must not absorb it into its verification claim.

## 6. Verification (all read-only; exact commands and observed outputs)

The line cites in items 1-6 are the **committed base `5fa6017` snapshot** on which this seat's first run was made; current worktree sites and hashes are in §3.5. Items 4-5 were re-checked after the worktree moved.

Run and observed during this seat:
1. `git -C souji-shokunin for-each-ref --format='%(refname)' refs/jj/keep` → 8; `git rev-list --count <sha> --not refs/heads/master refs/remotes/origin/master` → 6×`1`, 2×`0`.
2. `git rev-list --count 0254661… --not --all` → `0`; `--not --branches --tags --remotes` → `1`.
3. `git log --format=%H HEAD --branches --glob=refs/jj/keep/* --not --remotes -- tests/…/one.txt` → 4 lines; the same with the glob after `--not` → 0; `tools/souji-verify.sh` → 0; fleet-root control → 0.
4. `grep -n 'durable-refs-only'` → verify:817, vault:1005, quarantine:1077; `grep -n 'scans'`-adjacent reads confirm `--not --all` at verify:351, vault:517.
5. `git -C /home/vgpnk/Projects/shokunin for-each-ref refs/jj | wc -l` → 0; `test -d .jj` → false; `grep -n '\.jj|jj-lane' fleet-commit.sh shokunin-watchdog.sh append-closure.py` → nothing.
6. `grep -n -i 'jujutsu|jj' PROTOCOL.md` → no matches; `:119-121`, `:177`, `:230-231` read verbatim.
7. `git check-ignore -v tests/vault/vadv-49/fixture/control/.git` → `tests/vault/vadv-49/.gitignore:1:fixture/`; `git ls-tree -r --name-only HEAD -- tests/vault/vadv-49/fixture | wc -l` → `0`; `stat tests/vault/vadv54-run/p/p6repo/.git` → ENOENT; `git show HEAD:tests/vault/vadv54-harness.sh | sha256sum` → `966ee19a…` (`:46/47/:176` recreates the stub); `sha256sum tests/vault/vadv54-harness.sh` → `b55df92d…` with `git status --porcelain` = ` M` (`:273-281` transient stub).
8. `sha256sum scripts/hyaku/jj-lane.sh` → `3369dc27…`; `git log --oneline -1 14df5b9` → v2 message; helper source reads at `:543-548`, `:618-625`, `:~490`.
9. Lane configs: `cat .jj/repo/config-id` → `0c6bba…`, `900fa0…`, `e3435e…`; corresponding `~/.config/jj/repos/<id>/config.toml` each contain `auto-track = "none()"` and the lane identity.

After the executor's edit, the acceptance run is the round's own command (`census/round-17/run-matrix.py --changed <rev|WORKTREE>` over `r17-census-hygiene.py`, `r15-config`, `r14-namespace` and `--selftest`) plus a vault/quarantine selftest; expect `changed` to show the new (a)/(b) rows and no row movement for the plain-repo control.
