## Status

STATUS: PARTIAL — all three doc/code rows (staged S109/S110/S111 → lane S128/S129/S130) re-ground successfully: every cited locator was opened and confirmed byte-exact this run, and the snapshot bytes are identical to the lane's `census/round-26/sources/` copies. Two evidentiary defects are reported as ATTACK-class findings (F4, F5) and one Gate defect (F3) that bear on C2's admit set; no counter or predicate is proposed for change.

## Evidence

**Row S128 (staged S109) — `git-fetch(1)` § OPTIONS.** Fetched `https://git-scm.com/docs/git-fetch` (HTTP 200, 165815 bytes) → `census/round-26/sources/git-fetch.1.txt`, sha256 `78324905ba91b25c288fce5de5f788976be38e88b24815a02692d5ba3af61a5e` — byte-identical to the lane's committed snapshot (`diff` → IDENTICAL; matches `census/round-26/sources/SHA256SUMS`).

Located switch text (HTML `§ OPTIONS`, the `<dd>` shared by the four `<dt>`s `--auto-maintenance` / `--no-auto-maintenance` / `--auto-gc` / `--no-auto-gc`, snapshot lines 3190–3196):

> at the end to perform automatic repository maintenance if needed. This is enabled by default.

(15 words; § OPTIONS, `census/round-26/sources/git-fetch.1.txt` L3194–3196.) The four switches themselves are at L3190–3193 as `<dt>` elements. Cross-checked against the installed manual: `MANWIDTH=200 man 1 git-fetch` prints the same paragraph unhyphenated; host `git version 2.56.0`.

**Row S129 (staged S110) — git.git v2.56.0 call sites.** Fetched `https://raw.githubusercontent.com/git/git/v2.56.0/builtin/{fetch,merge,rebase,am,commit}.c` (all HTTP 200). Each sha256 matches `census/round-26/sources/SHA256SUMS` exactly (`git-builtin-fetch.c` `f14e15eb…`, `git-builtin-merge.c` `b6f5b663…`, `git-builtin-rebase.c` `72b4d351…`, `git-builtin-am.c` `aa5ac1ce…`, `git-builtin-commit.c` `e566f209…`) — i.e. the lane's snapshots are the same bytes I fetched. Whole-tree exhaustiveness check (`git.git v2.56.0` tarball, `grep -rn run_auto_maintenance`): exactly five call sites, all in `builtin/`, plus the definition `run-command.c:1987` / declaration `run-command.h:247`.

| claimed locator | verified line | enclosing function | ≤25-word verbatim quote |
|---|---|---|---|
| `builtin/fetch.c:2926` | 2926 ✔ | `cmd_fetch` (2505) | `run_auto_maintenance(the_repository, verbosity < 0);` |
| `builtin/merge.c:509` | 509 ✔ | `finish` (480) | `run_auto_maintenance(the_repository, verbosity < 0);` |
| `builtin/rebase.c:572` | 572 ✔ | `finish_rebase` (558) | `run_auto_maintenance(the_repository,` |
| `builtin/am.c:1942` | 1942 ✔ | `am_run` (1813) | `run_auto_maintenance(the_repository, state->quiet);` |
| `builtin/commit.c:1965` | 1965 ✔ | `cmd_commit` (1698) | `run_auto_maintenance(the_repository, quiet);` |

Located error-ignoring comments (contiguous, pipe-free; the full sentence is **not** contiguous — see F1):
- `builtin/merge.c:506–507`: `We ignore errors in 'gc --auto', since the`
- `builtin/rebase.c:569–570`: `We ignore errors in 'git maintenance run --auto', since the`

**Row S130 (staged S111) — `builtin/pull.c` fetch spawn.** Fetched `https://raw.githubusercontent.com/git/git/v2.56.0/builtin/pull.c` (HTTP 200, 36060 bytes), sha256 `538aa964818a9e90fc281f555f440e868388a54f1c8be38af0da1e55d52f00d1` — matches `SHA256SUMS`.

`builtin/pull.c:392` (inside `run_fetch`, 388):

> strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);

(4 words; `builtin/pull.c:392`.) `grep -c run_auto_maintenance builtin/pull.c` → **0**: pull has no direct call, so the inheritance is by process spawn — confirmed at runtime below.

**Runtime confirmation of S130's mechanism** (isolated scratch repo, `GIT_TRACE=1`, `git pull -q origin`):

```
trace: run_command: git fetch --update-head-ok -q origin
trace: start_command: /usr/lib/git-core/git fetch --update-head-ok -q origin
trace: run_command: git maintenance run --auto --quiet --no-detach
```

The child `git fetch` runs the maintenance; the parent `git pull` does not.

**Gate / counter state at the tip (read-only runs this round).**
`python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts` → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, exit 0.

`python3 -B tests/fixtures/r23-locator-heading.py --entries <both entries> --snapshot-dir census/round-26/sources` → `entries=2 locators=0 locators_bad=0` (see F3).

**Fixture replica (own scratch copy, campaign fixture read-only, never executed in `shokuknow`).** I copied `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh` into my scratch and patched **only** the two `mktemp -d` scratch roots (diff shows 3 changed lines: 1 comment + 2 paths) so nothing was written outside `/var/tmp/souji-r26-ScoutRegroundDocs/`. Result: all 7 cases PASS, matching the campaign's recorded evidence (`git_version=git version 2.56.0`).

**Isolation test (setup commit's own trigger suppressed via `-c maintenance.auto=false`, so only the command under test can prune).** Stale registration aged 4 months, `before=2` worktree registrations:

| command under test | registrations after | `git maintenance run --auto` spawned |
|---|---|---|
| `git merge -q --no-edit topic` | **1** (pruned) | 1 |
| `git rebase -q topic` (default merge backend) | **2** (no prune) | **0** |
| `git fetch -q <remote>` | **1** (pruned) | 1 |

## Findings

1. **All three staged row locators are exact.** `git-fetch(1)` § OPTIONS carries the four switches; the five `run_auto_maintenance` call sites sit at precisely `fetch.c:2926`, `merge.c:509`, `rebase.c:572`, `am.c:1942`, `commit.c:1965`; `pull.c:392` carries the `strvec_pushl` fetch spawn, and `pull.c` has zero direct `run_auto_maintenance` calls. The whole-tree grep shows these five are the *only* call sites in v2.56.0, so S129's scope cell ("the set of porcelain commands that call `run_auto_maintenance` at tag v2.56.0") is accurate. Confidence: high.

2. **S129's snapshot set is incomplete for its own scope.** S129's scope cell names the *set* of porcelain commands calling `run_auto_maintenance`, but the row's anchor lists only `builtin/fetch.c, builtin/merge.c, builtin/rebase.c, builtin/am.c, builtin/commit.c` — `builtin/pull.c` is not among them (it is covered separately by S130, so this is consistent), and `builtin/commit.c`/`builtin/am.c` *are* included. No defect; recorded because the exhaustiveness claim is what F4 rests on.

3. **The landed Gates carry no `§ <NAME>` locator, so Q54 is vacuous on both admitted entries.** `tests/fixtures/r23-locator-heading.py` reports `locators=0` for both entries — the Gate blocks name snapshots and carry plain-language locators (`OPTIONS`, `lines 506-509`, `line 2926`) but no `§ NAME` token, so the Q54 heading-resolution check has nothing to resolve. C2's kill rule requires "every snapshot § locator resolves to a heading line"; as landed, that rule is unexercised. This is fixable and I verified the fix works: a probe entry whose Gate line reads `— S128 § OPTIONS — … snapshot: census/round-26/sources/git-fetch.1.txt` yields `entries=1 locators=1 locators_bad=0`, because the snapshot has a real heading (`<h2 id="_options">OPTIONS</h2>`, L2995). Location: `corpus/knowledge/git-auto-maintenance-trigger-set.md` L74–75, `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` L99–100.

4. **Two entry-body quotes are not verbatim against the snapshots they cite.** (a) `git-auto-maintenance-trigger-set.md` L22–24 quotes "Run git maintenance run --auto at the end to perform automatic repository maintenance if needed. This is enabled by default." — this string is **not** a contiguous substring of `git-fetch.1.txt`: the HTML interleaves `<span class='synopsis'><code>git</code> <code>maintenance</code> <code>run</code> <code>--auto</code></span>`, so only the 15-word tail is contiguous. (b) `git-auto-maintenance-trigger-set.md` L30–35 quotes the merge/rebase comments as the single strings "We ignore errors in 'gc --auto', since the user should see them." and "We ignore errors in 'git maintenance run --auto', since the user should see them." — in the C sources the comment wraps across two lines, so the squashed source reads `… since the * user should see them. …` (a `*` continuation intervenes); the quoted sentences are reconstructions, not verbatim spans. A Gate quote of either form would fail the gate-check's `check4-quote-absent-from-snapshot`; the landed Gates avoided this by quoting different, contiguous spans. Fixable by adopting the located quotes in the Evidence table.

5. **The landed Gates' quote lines are not tied to a row id and one does not evidence its row's claim.** `git-auto-maintenance-trigger-set.md` L75 quotes `struct child_process cmd = CHILD_PROCESS_INIT;` from `git-builtin-pull.c lines 390-391`; that line is generic boilerplate and does not evidence S130's claim (the fetch spawn at `pull.c:392`). The S130 row's claim-bearing span is the `strvec_pushl` line, which cannot be carried as a single Gate quote: the gate-check's quote regex `"([^"]{2,400})"` splits it into `strvec_pushl(&cmd.args, ` / `, ` / `, NULL);` because it contains embedded double quotes. A pipe-free, quote-free alternative for S130 is available and verified findable in the snapshot: `strvec_pushl(&cmd.args,` — or the entry can cite `pull.c:392` in prose with the row id and keep the Gate quote on the `--update-head-ok` switch.

6. **`git rebase` in the campaign fixture's topology does not reach any `run_auto_maintenance` call site; the fixture's `rebase` case prune is caused by the case's own setup commit.** In the fixture's `rebase` case the sequence is `checkout -B topic other` → `git commit -qm topic` → `checkout master` → `git rebase -q topic`. Step-by-step trace of that exact sequence: the **`git commit -qm topic`** step spawns `git maintenance run --auto` and takes the count 2 → 1; the subsequent **`git rebase -q topic`** step spawns **zero** maintenance runs and leaves the count at 1. Source reason: `git rebase`'s default backend is the merge backend, and `builtin/rebase.c:765–766` skips `finish_rebase()` for it ("merge backend cleans up after itself"); the sequencer's commit path uses in-process `commit_tree_extended` (`sequencer.c:1687`), so `builtin/commit.c:1965` is not reached either. Isolation test confirms: with the setup commit's trigger suppressed, `git rebase -q topic` leaves 2 registrations and spawns 0 maintenance runs, while `git merge -q --no-edit topic` prunes to 1 with 1 maintenance run. Location: fixture `lanes/souji/round2/fixtures/r23-trigger-prune.sh` L157–164; `builtin/rebase.c:765–766`; `sequencer.c:1687`. Consequence for C2's admit set: `git-auto-maintenance-trigger-set-r23.md` L17–19 (claim 1) attributes the `rebase` case's 2 → 1 to "under `git rebase`", and L56–60 attributes reachability to `builtin/rebase.c:572`; the measurement it cites (S131) does not isolate `git rebase` from the setup commit, and in the default merge backend `git rebase` reaches neither `rebase.c:572` nor `commit.c:1965`. The `merge` case is *not* affected: `merge.c:509` is reached on the fast-forward path too (`merge.c:1690` calls `finish()`), which the isolation test confirms (merge prunes to 1 with 1 maintenance run).

7. **The campaign fixture's `pull` case never runs `git pull`.** `lanes/souji/round2/fixtures/r23-trigger-prune.sh` L144–147 implements `pull)` as `git remote add origin "$rem"` + `git fetch -q origin` — a *fetch*, with no `git pull` anywhere in the file (`grep -n pull` returns only the label, the header comment, and the `run_case pull` line). So S131's "pull" row measures the fetch trigger, while `git-auto-maintenance-trigger-set-r23.md` L19–21 claims "under `git pull`" the count goes 2 → 1 and L25–27 explains it via S130's spawn mechanism. The *mechanism* is nonetheless real and I confirmed it at runtime (`git pull` → child `git fetch --update-head-ok` → `git maintenance run --auto`), so the defect is in the evidence-to-claim link, not in S130 or in git's behaviour.

8. **The fixture's `merge` case contradicts its own comment.** L149 says "A real, non-fast-forward merge so the merge actually updates HEAD", but the case's topology makes `master` an ancestor of `topic` (measured: `git merge-base --is-ancestor master topic` → true), so the merge is a **fast-forward**. This does not break the merge case — `merge.c:509` is on the fast-forward path as well — but the comment's stated rationale is wrong.

9. **`corpus/lessons/round-26.md` Gate lacks the per-row located quotes the prereg requires.** C2 states "Every cited source is re-opened THIS round by the lane (new access date, <=25-word located quote in the lesson Gate, snapshot bytes under `census/round-26/sources/`)". The r26 lesson Gate (L5–18) names S128–S132 in prose but carries **no** per-row quote and **no** per-row access date; the r25 precedent does (`corpus/lessons/round-25.md` L33–36: "Quote (23 words): …" per row, "accessed 2026-10-25"). The r25 convention also counts 3 `Quote (` occurrences; the r26 lesson has 0. Location: `corpus/lessons/round-26.md` `## Gate`.

10. **Snapshot bytes are already in the lane and match mine exactly.** `census/round-26/sources/` holds `git-fetch.1.txt`, `git-builtin-{fetch,merge,rebase,am,commit,pull}.c` and a `SHA256SUMS`; every sha256 equals my independently fetched bytes. The L1 therefore needs no new copy for the doc/code rows — only the delivery-file naming reconciliation below.

11. **Delivery-file naming must reconcile before the L1 copies.** The prereg's S129 anchor and the entries' Gates cite `census/round-26/sources/git-builtin-{fetch,merge,rebase,am,commit}.c` and `git-builtin-pull.c` (per-file), whereas this seat's delivery instruction names `git-builtin-v2560.txt` and `git-pull-c.txt`. Both sets are in my scratch and are byte-identical where they overlap (`git-pull-c.txt` ≡ `git-builtin-pull.c`, sha256 `538aa964…`; `git-fetch.1.txt` ≡ the lane's, `78324905…`); `git-builtin-v2560.txt` is the five call-site files concatenated with per-file headers (sha256 `a2b85ed2…`) and is **not** interchangeable with the per-file names in the Gate `snapshot:` paths, because the gate-check resolves the named path literally. Recommendation to the L1: copy the per-file names the registry and Gates cite (already present and verified), and treat `git-builtin-v2560.txt` as a convenience bundle only.

## Attack log

**ATTACK-1 (C2 / S131 / entry `git-auto-maintenance-trigger-set-r23.md` claim 1, L17–19, L56–60).** The admitted `rebase` measurement is not isolated: the fixture's `rebase` case prunes the stale registration during its own setup `git commit -qm topic` (commit.c:1965), and the `git rebase -q topic` that follows spawns **zero** `git maintenance run --auto` and prunes nothing. Isolation test: `git rebase -q topic` → 2 registrations remain, 0 maintenance runs; `git merge -q --no-edit topic` → 1 registration, 1 maintenance run. Source: `builtin/rebase.c:765–766` skips `finish_rebase()` for the merge backend; `sequencer.c:1687` commits in-process, so `commit.c:1965` is not reached either. Effect on the round's sourced claim: S131's `rebase` row does not establish that `git rebase` prunes, and S129's `rebase.c:572` call site is not on the default `git rebase` path at all — it is reached only by `git rebase --apply` (measured: 1 maintenance run), which is not what the fixture runs. The r23 entry's own caveat (L56–60: "a rebase that is a no-op does not reach the call site") is consistent with my measurement but contradicts the PASS it cites. Reported as an attack on the evidence-to-claim link; **no counter, target or case set is proposed for change** — the frozen predicates are untouched, and the L1 decides the remedy.

**ATTACK-2 (C2 / S131 `pull` row / entry `git-auto-maintenance-trigger-set-r23.md` L19–21, L25–27).** The fixture's `pull` case runs `git fetch -q origin`, never `git pull` (`grep -n pull` on the fixture yields only the label, header comment and `run_case` line). S131's "pull" row therefore measures the fetch trigger, so the entry's "under `git pull` the count goes 2 → 1" is not what S131 shows. The underlying mechanism (S130) is independently confirmed at runtime, so the claim is true but the cited receipt does not evidence it. Same reporting discipline: reported, not silently repaired.

**ATTACK-3 (C2 kill rule, both entries' Gates).** Q54 is vacuous as landed (`locators=0`): the Gate blocks name snapshots but carry no `§ <NAME>` locator, so the frozen requirement "every snapshot § locator resolves to a heading line" is unexercised, and the landed quotes are not row-attributed (one of them — `struct child_process cmd = CHILD_PROCESS_INIT;` — does not evidence S130's claim). A verified fix exists and is within the frozen rule's intent: a `§ OPTIONS` locator resolves against the snapshot (`locators=1 locators_bad=0`), and pipe-free/quote-free located spans for every row are listed in the Evidence table above.

**ATTACK-4 (C2 admit-set completeness).** Two of the three doc/code rows' content is correct, but the row-scoped quotes carried in the entry bodies are reconstructions rather than verbatim spans (Finding 4). If the lesson Gate is to carry the prereg-required ≤25-word located quotes, they must be the contiguous spans I located, not the entry's current renderings.

## Scope / bounds honoured

Read-only on the lane: no `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv` of anything I did not create, no signals. Only file written inside the lane is this report. Nothing under `/home/vgpnk/Projects/shokunin/.scratch/`, `.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, the fleet `scripts/`/`templates/`, any sibling lane repo, or the lane's `jj`/git index was touched. `/home/vgpnk/Projects/shokuknow` was read only; the campaign fixture was **copied** into my scratch and executed there (scratch paths patched), never run in place. All scratch lived under `/var/tmp/souji-r26-ScoutRegroundDocs/` and was removed at the end except the three delivery files. No credentials, no live `/proc` census, no `census/operator-sweep-*` contents, no `.scratch/` contents. No tools installed (none needed). No `agent://all` used.

**Deliverables** in `/var/tmp/souji-r26-ScoutRegroundDocs/`: `git-fetch.1.txt` (165815 B, `78324905…`), `git-builtin-v2560.txt` (328457 B, `a2b85ed2…`), `git-pull-c.txt` (36060 B, `538aa964…`); plus the registry-citing per-file set `git-builtin-{fetch,merge,rebase,am,commit,pull}.c`, each sha256-equal to the lane's `SHA256SUMS`.
