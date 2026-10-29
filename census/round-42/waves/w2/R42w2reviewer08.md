# R42w2reviewer08 — R1 and the repointed pointers (operability review)

Seat: `R42w2reviewer08` (reviewer, wave 2, round 42). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `bf618f6c5c09d302994871c94903abbea2deb60d`; freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`; tip under
attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`. Read-only in the lane; the only file written is this report.
Scratch: `/fast/scratch/hyaku/souji-r42/R42w2reviewer08/` (deleted before yield; every command below pasted
verbatim from the runs). No tool installed, so the operator tooling directive has no entry.

## Verdict

**The R1 repair (repoint) is sound, byte-exact and live; the frozen R1 predicate was indeed wrong, and the
lesson's M42-2 account is faithful on every checkable point — with one wording defect and one residual gap.**

- The lane copies are byte-identical to the fleet originals (`cmp` silent, sha256 equal, `SHA256SUMS` verified),
  and the fleet originals are unmodified since fleet commit `f47ad6ba8d30`.
- The two repointed lines resolve in **both** gate modes; the four runs at the tip all read `findings=0`.
- The anchors the README row cites (`step 5`, `F3`) exist in the copies and still support the row's figures
  (`references.others.count=15`, `objects.commits.count=55` vs `44`).
- The frozen R1 counter reads `findings=0 deleted=2 rows_added=0 stale=0` at the tip — red **by its letter**, exactly
  as the lesson states, because the landed repair repointed instead of appending three exemption rows.
- **Defect (wording, medium):** the lesson's M42-2 says the three-row predicate "reads green without
  `--fleet-root` and `findings=2` with it". No three-row candidate does that. Spelled as the gate prints the
  findings, the three rows make the exemptions file **malformed** and the gate exits 2 (could-not-evaluate) in
  *both* modes; spelled loader-admissibly, the plain mode reads `findings=4`, not green. The only reading that
  prints `findings=0` is the vacuous one (the counter greps a zeroed `SUMMARY` off a failed run). The lesson
  omits that the "green" is vacuous.
- **Gap (residual, low):** the copies' bytes are pinned only by a `SHA256SUMS` file that **no tool in the lane
  reads**, and no committed receipt records the digest check. The gate checks path *existence*, not bytes.

---

## 1. Byte-for-byte comparison with the fleet originals

```
$ cd /home/vgpnk/Projects/shokunin
$ cmp souji-shokunin/census/round-42/jj-w1-reports/JjAuditSouji.md .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md && echo "IDENTICAL(audit)"
IDENTICAL(audit)
$ cmp souji-shokunin/census/round-42/jj-w1-reports/JjTrialSouji.md .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md && echo "IDENTICAL(trial)"
IDENTICAL(trial)
$ sha256sum souji-shokunin/census/round-42/jj-w1-reports/JjAuditSouji.md souji-shokunin/census/round-42/jj-w1-reports/JjTrialSouji.md
c632531f15398fed37c95033a03e340912dc76c900c72d550379ec4732bdd07c  souji-shokunin/census/round-42/jj-w1-reports/JjAuditSouji.md
ceb6d72870f5306237662837a24c517609abc27eec5826946b4fabf88e5b0775  souji-shokunin/census/round-42/jj-w1-reports/JjTrialSouji.md
$ sha256sum .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
c632531f15398fed37c95033a03e340912dc76c900c72d550379ec4732bdd07c  .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
ceb6d72870f5306237662837a24c517609abc27eec5826946b4fabf88e5b0775  .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
```

`cmp` was silent on both pairs (exit 0), i.e. **byte-identical**.

### The fleet originals' provenance (`git log -1 --format=%H -- <path>`)

```
$ git -C /home/vgpnk/Projects/shokunin log -1 --format='%H %ad %s' -- .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
f47ad6ba8d306f8125597401cb2ce45c1297a593 Sun Oct 25 09:29:03 2026 -0300 repair: restore fleet tree deleted by stray commit 35b91714 (author t <t@t>, 09:21:14 -03)
$ git -C /home/vgpnk/Projects/shokunin log -1 --format='%H %ad %s' -- .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
f47ad6ba8d306f8125597401cb2ce45c1297a593 Sun Oct 25 09:29:03 2026 -0300 repair: restore fleet tree deleted by stray commit 35b91714 (author t <t@t>, 09:21:14 -03)
```

This is the commit the repointed rows cite (`fleet commit f47ad6ba8d30`). Corroboration that the pinned bytes are
the fleet's own, and that the fleet tree was not edited afterwards:

```
$ git -C /home/vgpnk/Projects/shokunin show f47ad6ba8d30...:.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md | sha256sum
c632531f15398fed37c95033a03e340912dc76c900c72d550379ec4732bdd07c  -
$ git -C /home/vgpnk/Projects/shokunin show f47ad6ba8d30...:.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md | sha256sum
ceb6d72870f5306237662837a24c517609abc27eec5826946b4fabf88e5b0775  -
$ git -C /home/vgpnk/Projects/shokunin log --oneline f47ad6ba8d30..HEAD -- .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
(empty — unchanged since)
$ git -C /home/vgpnk/Projects/shokunin status --porcelain -- .ufo/waves/hyaku/jj-w1/reports/
(empty — worktree clean)
$ git -C /home/vgpnk/Projects/shokunin diff --stat f47ad6ba8d30 -- .ufo/waves/hyaku/jj-w1/reports/
(empty — identical)
```

The fleet originals also survive the stray-delete/restore history intact: their bytes at `7d0c7605` (the original
study commit) equal the bytes at `f47ad6ba8d30` and equal the lane copies —
`git show 7d0c7605:.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md | sha256sum` →
`c632531f…`, `JjTrialSouji.md` → `ceb6d728…`. (At the stray commit `35b91714` the path is absent —
`fatal: path '…' exists on disk, but not in '35b91714'` — which is why `f47ad6ba` exists at all.)

### The lane copies are committed at the tip, not just present in the worktree

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r 3105a63b23481fccf7df58e74d14a6681e0ea0c8 -- census/round-42/jj-w1-reports/
100644 blob c0bbf687e07ecde2b5e06cafeaa161f1ad831880	census/round-42/jj-w1-reports/JjAuditSouji.md
100644 blob 363d8ae310c4c3962972f8d64e2e1a4470b24d79	census/round-42/jj-w1-reports/JjTrialSouji.md
100644 blob 174d1193297a9eb61c7648b7d119fb8c51ff4c46	census/round-42/jj-w1-reports/SHA256SUMS
$ git show 3105a63...:census/round-42/jj-w1-reports/JjAuditSouji.md | sha256sum
c632531f15398fed37c95033a03e340912dc76c900c72d550379ec4732bdd07c  -
$ git show 3105a63...:census/round-42/jj-w1-reports/JjTrialSouji.md | sha256sum
ceb6d72870f5306237662837a24c517609abc27eec5826946b4fabf88e5b0775  -
```

(Committed blob `363d8ae3…` → content sha256 `ceb6d728…`, confirmed via `git cat-file -p 363d8ae3… | sha256sum`.)

> **Observation, not a defect.** One earlier invocation of `git -C souji-shokunin show 3105a63…:census/round-42/jj-w1-reports/JjTrialSouji.md`
> printed `fatal: path '…' does not exist in '3105a63…'`. That was **not reproducible**: the same command run
> 30× in a loop succeeded every time, `ls-tree` lists the blob, `git cat-file -p` yields the expected bytes, and
> the lane's `.git/objects/pack/` shows two packs rewritten at 22:28 (a concurrent repack by another seat's
> tooling, `.git/objects` mtime 22:03, `.git/index` 22:06). It is a transient read during a concurrent repack,
> not a defect in the landed tree. Recorded because a reviewer who hits it once would wrongly suspect the copy.

### SHA256SUMS confirmed

```
$ cat /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/jj-w1-reports/SHA256SUMS
c632531f15398fed37c95033a03e340912dc76c900c72d550379ec4732bdd07c  JjAuditSouji.md
ceb6d72870f5306237662837a24c517609abc27eec5826946b4fabf88e5b0775  JjTrialSouji.md
```

Verified in **both** directories (lane copies, and the fleet originals themselves):

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/jj-w1-reports && sha256sum -c /fast/scratch/hyaku/souji-r42/R42w2reviewer08/SHA256SUMS
JjAuditSouji.md: OK
JjTrialSouji.md: OK
$ cd /home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports && sha256sum -c /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/jj-w1-reports/SHA256SUMS
JjAuditSouji.md: OK
JjTrialSouji.md: OK
```

The committed `SHA256SUMS` blob at the tip is byte-identical to the worktree file
(`git show 3105a63…:census/round-42/jj-w1-reports/SHA256SUMS` → the same two lines, `cat -A` shows plain
`\n` endings, no CRLF).

## 2. The exact two repointed lines

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff bf618f6c5c09d302994871c94903abbea2deb60d 3105a63b23481fccf7df58e74d14a6681e0ea0c8 -- corpus/README.md corpus/knowledge/jj-colocation-receipts.md
```

The repoint is two hunks, one per file (the README hunk also carries the round-42 frontier block; the two
**repointed** lines are the `F2` table row and the `Lane reports` paragraph):

`corpus/README.md:217` (F2 row) — **base**:

```
| F2 caveat, disclosed only: colocated repos inflate structure counts versus a plain clone (`references.others.count` 15 from `refs/jj/keep/*`; `objects.commits.count` 55 vs 44, sandbox) — no F2 capability claimed | observed, not claimed | `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` step 5; `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` F3 |
```

`corpus/README.md:217` (F2 row) — **tip**:

```
| F2 caveat, disclosed only: colocated repos inflate structure counts versus a plain clone (`references.others.count` 15 from `refs/jj/keep/*`; `objects.commits.count` 55 vs 44, sandbox) — no F2 capability claimed | observed, not claimed | `../census/round-42/jj-w1-reports/JjTrialSouji.md` step 5; `../census/round-42/jj-w1-reports/JjAuditSouji.md` F3 (r42 repoint, R41-D-LG-DANGLING: byte-exact copies of the fleet-repo reports, sha256 in `../census/round-42/jj-w1-reports/SHA256SUMS`; fleet repo, hyaku jj-w1 reports directory, at fleet commit f47ad6ba8d30) |
```

`corpus/knowledge/jj-colocation-receipts.md:148` — **base**:

```
Lane reports (cited inline by file and line, not S-rows): JjAuditSouji.md (fleet repo `.ufo/waves/hyaku/jj-w1/reports/`), JjTrialSouji.md (same), fixture outputs `census/round-17/jj-receipts-{base5fa6017,4f48343}.txt`.
```

`corpus/knowledge/jj-colocation-receipts.md:148` — **tip**:

```
Lane reports (cited inline by file and line, not S-rows): JjAuditSouji.md (byte-exact lane copy `census/round-42/jj-w1-reports/`; original in the fleet repo, hyaku jj-w1 reports directory, fleet commit f47ad6ba8d30), JjTrialSouji.md (same), fixture outputs `census/round-17/jj-receipts-{base5fa6017,4f48343}.txt`.
```

The gate's `--base` leg confirms no other file changed in the round that touches these paths: the diff for
`corpus/pointer-exemptions.tsv` is empty (no rows appended, no rows removed — the repoint is *not* an exemption
repair).

## 3. The cited steps still exist in the copies and still support the row

The README row cites `step 5` in `JjTrialSouji.md` and `F3` in `JjAuditSouji.md`. Both anchors exist in the
**lane copies** (and, since the copies are byte-identical, in the fleet originals):

```
$ grep -n '^### F3' JjAuditSouji.md
118:### F3 — HIGH: `--not --all` and all-ref roots treat `refs/jj/keep` as durable
$ grep -n '^## Step 5' JjTrialSouji.md
53:## Step 5 — lane's own git-touching checks (300 s timeout each)
```

The row's own numbers are still carried by the cited step (`JjTrialSouji.md:57`, `:61`):

```
| `tools/souji-repo-structure.sh --repo <r>` | exit 0 | exit 0 | PASS but **inflated**: `references.others.count=15` (refs/jj/keep/*), `objects.commits.count=55` vs 44 |
- The 15 extra refs are `refs/jj/keep/<sha>` — jj pins every intermediate working-copy/rebase commit. Any tool that counts "all refs" or unreachable objects sees them; `git rev-list --all` = 55 vs `--branches` = 44.
```

`F3` (`JjAuditSouji.md:118-130`) is the "`--not --all` / all-ref roots treat `refs/jj/keep` as durable" finding,
i.e. exactly the subject of the F2 caveat row. Both anchors are live in the copies: `JjTrialSouji.md:76` still
describes the `refs/jj/keep/*` inflation (hazard 2).

## 4. The landing gate at the tip, four runs (QUALITY Q103: mode named per block)

Mode flags are echoed in each block header, per Q103.

**(a) `--round 41`, no `--fleet-root`**
```
$ python3 -B tools/souji-landing-gate.py --root . --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --round 41
SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
rc=0
```
**(b) `--round 41`, with `--fleet-root /home/vgpnk/Projects/shokunin`**
```
$ python3 -B tools/souji-landing-gate.py --root . --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --round 41 --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
rc=0
```
**(c) `--round 42`, no `--fleet-root`**
```
$ python3 -B tools/souji-landing-gate.py --root . --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --round 42
SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=1	carry_heading=0	checked_reports=80
rc=0
```
**(d) `--round 42`, with `--fleet-root /home/vgpnk/Projects/shokunin`**
```
$ python3 -B tools/souji-landing-gate.py --root . --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --round 42 --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=1	carry_heading=0	checked_reports=80
rc=0
```

All four are green. The `--base` leg (changed-scripts, `bf618f6…`→tip) is also clean:
`--round 41 --base` → `findings=0 … checked_changed=329 …`; `--round 42 --base` → `findings=0 … checked_changed=329 …`.

**The same four runs at the base, for the contrast the lesson quotes** (both modes, mode flags shown):

```
$ python3 -B tools/souji-landing-gate.py --root . --rev bf618f6c5c09d302994871c94903abbea2deb60d --round 41
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at bf618f6c5c09
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at bf618f6c5c09
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at bf618f6c5c09
SUMMARY	findings=3	checked_reg=107	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
rc=1
$ python3 -B tools/souji-landing-gate.py --root . --rev bf618f6c5c09d302994871c94903abbea2deb60d --round 41 --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=0	checked_reg=107	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
rc=0
```

This reproduces the lesson's M42-2 evidence pointer exactly: `findings=3` without `--fleet-root`, `findings=0` with
it, at the base. The three finding paths and their source lines are identical to the ones the lesson quotes.

**The gate at the receipt's revision** (`51f204fb7c633b691a3ca9cd8c0bf025f6e0a093`, the rev named in
`census/round-42/records/gate-both-modes.txt`) also reads green in both modes, with the receipt's counts
(`checked_reg=107`, `checked_reports=165`) reproduced:
```
--round 41                 → SUMMARY findings=0 checked_reg=107 … checked_reports=165
--round 41 --fleet-root …  → SUMMARY findings=0 checked_reg=107 … checked_reports=165
```
So the committed receipt `census/round-42/records/gate-both-modes.txt` is faithful, and the tip (two commits
later) is still green in both modes.

### Liveness: the repointed citation is actually checked, not merely quiet

Deleting the copies in a scratch clone makes the gate go red in **both** modes — the repointed pointer is
enforced, not a silent no-op:

```
# LIVENESS A: the two .md copies deleted (SHA256SUMS kept), commit c93001f97ae2b039d1ae0437381464a0f705d57c
--- plain
LG-DANGLING-PTR	census/round-42/jj-w1-reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at c93001f97ae2
LG-DANGLING-PTR	census/round-42/jj-w1-reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at c93001f97ae2
SUMMARY	findings=2	…
--- fleet
LG-DANGLING-PTR	census/round-42/jj-w1-reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at c93001f97ae2
LG-DANGLING-PTR	census/round-42/jj-w1-reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at c93001f97ae2
SUMMARY	findings=2	…

# LIVENESS B: the whole directory deleted, commit 97402db819d85ed7f4a58634f599f4c51a5c6fb6
--- plain
LG-DANGLING-PTR	census/round-42/jj-w1-reports/	SKILL.md:292 cites path absent at 97402db819d8
LG-DANGLING-PTR	census/round-42/jj-w1-reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at 97402db819d8
LG-DANGLING-PTR	census/round-42/jj-w1-reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at 97402db819d8
LG-DANGLING-PTR	census/round-42/jj-w1-reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at 97402db819d8
LG-DANGLING-PTR	census/round-42/jj-w1-reports/SHA256SUMS	corpus/README.md:217 cites path absent at 97402db819d8
SUMMARY	findings=5	…
--- fleet
(same five findings)
```

Note the third pointer surface the repair inherits: `SKILL.md:292` (the `r42-r1-counter` gate row) also cites
`census/round-42/jj-w1-reports/`, so the SKILL row is bound to the copies too. That is consistent, but it means
the copy directory is now load-bearing for the SKILL registry row as well — a detail worth keeping in mind if
the copies are ever pruned.

## 5. The frozen R1 counter at the tip, and its output against its docstring

```
$ python3 -B census/round-42/r1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch /fast/scratch/hyaku/souji-r42/R42w2reviewer08
SUMMARY findings=0 deleted=2 rows_added=0 stale=0
rc=1
```

Against `census/round-42/r1-counter.py`'s own docstring (`Target: SUMMARY findings=0 deleted=0 rows_added=3
stale=0 (exit 0)`), field by field:

| field | docstring meaning | tip value | why |
|---|---|---|---|
| `findings` | the gate's own `findings=` at REV, run `--root LANE --rev REV --round 41` with **NO** `--fleet-root` | `0` | the repointed pointers resolve in-tree; the gate is green without `--fleet-root` (run (a) above) |
| `deleted` | deleted lines between BASE and REV in `corpus/README.md`, the jj-colocation entry and `corpus/pointer-exemptions.tsv` | `2` | `git diff --numstat base tip` = `12 1 corpus/README.md` and `1 1 corpus/knowledge/jj-colocation-receipts.md`; the two repointed lines each count one deletion. The counter's `deleted` leg is an *append-only* proxy, and the repoint is by construction an edit of two existing lines. |
| `rows_added` | data rows appended to `corpus/pointer-exemptions.tsv` between BASE and REV | `0` | the repair appended no exemption rows — `git diff --numstat base tip -- corpus/pointer-exemptions.tsv` is empty; the file still holds its 4 committed rows |
| `stale` | `LG-DANGLING-PTR-EXEMPT-STALE` findings printed by the same run | `0` | no exemption rows exist to go stale |

So the counter is **red by its letter** — `deleted=2` (≠0) and `rows_added=0` (≠3) — while the substantive gate
finding (`findings=0`) is green. That is precisely what the lesson's M42-2 states ("The frozen R1 counter reads
`findings=0 deleted=2 rows_added=0 stale=0` = **red by its letter**"), and R1 is not a claim, so a red R1 is
reported, not narrowed. **The lesson's number is exactly reproduced.**

## 6. Was the frozen R1 predicate (three exemption rows) wrong? — applied in a scratch clone, both modes

Scratch clone `/fast/scratch/hyaku/souji-r42/R42w2reviewer08/exp.4O3qpg`, `git rev-parse --show-toplevel` asserted
equal to the clone before the first commit, identity passed only through `GIT_AUTHOR_*`/`GIT_COMMITTER_*`.

**Baseline (no repair, base rev), both modes** — reproduces §4's base reading: plain `findings=3` (exit 1),
fleet `findings=0` (exit 0).

**EXPERIMENT A — the three rows spelled exactly as the gate prints the findings** (the literal reading of the
frozen predicate: "one row per dangling pointer", the pointer string being the finding's path column):

```
../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	<reason>
../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	<reason>
.ufo/waves/hyaku/jj-w1/reports/	<reason>
```
commit `388f80bc925bdb55cf359020b4570a60a0f5ccd3`:
```
--- plain
SUMMARY	findings=0	checked_reg=0	checked_changed=0	checked_pins=0	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	corpus/pointer-exemptions.tsv:5 malformed exemption row (expected unique path<TAB>reason)
gate_rc=2
--- fleet
SUMMARY	findings=0	checked_reg=0	checked_changed=0	checked_pins=0	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	corpus/pointer-exemptions.tsv:5 malformed exemption row (expected unique path<TAB>reason)
gate_rc=2
--- frozen r1-counter at exp A commit
SUMMARY findings=0 deleted=0 rows_added=3 stale=0
counter_rc=0
```

This is the decisive result. The three rows **as the gate prints them** are not loader-admissible
(`tools/souji-landing-gate.py:1030` `load_pointer_exemptions` requires `fields[0].startswith(POINTER_ROOTS)` and
`_safe_pointer_path`; the two `../`-collapsed paths have a `..` component and no POINTER_ROOTS prefix). The
loader raises, the gate exits **2** in **both** modes with a *zeroed* `SUMMARY findings=0 checked_*=0` on stdout,
and `r1-counter.py` — which greps `^SUMMARY\tfindings=(\d+)` and never inspects the gate's exit code — reads
`findings=0` and **exits 0**. So the frozen predicate's target is reachable only *vacuously*: the counter's green
is a could-not-evaluate run wearing a green hat.

**EXPERIMENT B — the three rows spelled loader-admissibly** (fleet-relative `.ufo/waves/hyaku/jj-w1/reports/…`,
which is the only spelling the loader accepts for those paths), commit `576bd7eab001d91bcd9e83d1771c77d91cae7e72`:
```
--- plain
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at 576bd7eab001
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at 576bd7eab001
LG-DANGLING-PTR-EXEMPT-STALE	.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	exemption does not suppress an unresolved pointer or dangling measured_commit at 576bd7eab001
LG-DANGLING-PTR-EXEMPT-STALE	.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	exemption does not suppress an unresolved pointer or dangling measured_commit at 576bd7eab001
SUMMARY	findings=4	…
gate_rc=1
--- fleet
LG-DANGLING-PTR-EXEMPT-STALE	.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	…
LG-DANGLING-PTR-EXEMPT-STALE	.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	…
SUMMARY	findings=2	…
gate_rc=1
--- frozen r1-counter at exp B commit
SUMMARY findings=4 deleted=0 rows_added=3 stale=2
counter_rc=1
```

**EXPERIMENT C — three admissible rows pointing at the landed copies** (commit
`0d3e5ea0053da6cc5461d61f5d9eb391f4286779`): plain `findings=3`, all three `LG-DANGLING-PTR-EXEMPT-STALE`
(the copies resolve in-tree, so the rows suppress nothing and every row is stale); counter
`findings=3 deleted=2 rows_added=3 stale=3`, rc=1.

### Conclusion on the predicate

**The frozen R1 predicate was indeed wrong — and it is wrong for a reason the lesson only half states.**

1. The **honest** predicate is unreachable. There is no three-row exemptions file that suppresses the two
   `corpus/README.md:217` findings: the loader will not accept the pointer form the gate prints, and any
   admissible spelling does not string-equal the normalized pointer the gate yields. Experiment B shows the
   plain mode still reads `findings=4` (2 dangling + 2 stale) even with the loader's own preferred spelling.
2. The **stated** target is reachable only vacuously. Experiment A: gate exit 2, counter exit 0. This is the
   defect `R42scout03` already named in wave 1 (`census/round-42/waves/w1/R42scout03.md:7`, `:60`, `:80`):
   *"the pass is vacuous: the gate never evaluates (exit 2, malformed exemption row) and the r1-counter reads the
   gate's zeroed SUMMARY without checking the gate's exit status."* My Experiment A reproduces that byte for byte
   on an independent clone.
3. The **landed repair** (repoint to in-tree byte-exact copies) is the correct avoidance: it reads `findings=0` in
   both modes at the tip, with no exemption rows to go stale, and with the pointer still enforced (LIVENESS A/B).

**Is the lesson's M42-2 account faithful?** Faithful on the diagnosis (wrong predicate; the landed repair trades
nothing and reads green in both modes), faithful on the numbers it quotes (`findings=3` vs `0` at the base;
`findings=0 deleted=2 rows_added=0 stale=0` at the tip), faithful on the mechanism it names (staleness is a set
difference at `tools/souji-landing-gate.py:1267-1275`, `pointer_exemptions - used_exemptions`; the reason column is
never read). **One wording defect:**

> **M42-2 states:** *"R42scout03 measured the frozen R1 repair (three `corpus/pointer-exemptions.tsv` rows):
> green without `--fleet-root` and `findings=2` (`LG-DANGLING-PTR-EXEMPT-STALE`) with it, because staleness is a
> set difference…"*

The two halves of that sentence cannot both be true of one three-row candidate, and neither half is the honest
reading:

- "green without `--fleet-root`" is the **vacuous** `findings=0` of Experiment A — a run that exited 2 and
  evaluated nothing (`checked_reg=0 … checked_reports=0`). The lesson does not say so; a reader who takes the
  sentence at face value believes a three-row exemptions file yields a green plain-mode gate, which is false:
  with the loader-admissible spelling the plain mode reads `findings=4` (Experiment B), and with the finding's own
  spelling the gate cannot evaluate at all (Experiment A).
- "`findings=2` with it" is Experiment B's *fleet-mode* reading of the loader-admissible spelling, not of the
  three rows "as the gate prints them". The lesson fuses two different candidate spellings into one sentence.

The lesson's **conclusion** (the frozen predicate was wrong; the landed repair reads green in both modes) is
correct and independently reproduced. The **evidence sentence** should read something like: *"the three-row
candidate spelled as the gate prints the findings is loader-malformed, so the gate exits 2 in both modes and the
counter's `findings=0` is vacuous; spelled admissibly the plain mode reads `findings=4` and the fleet-root mode
`findings=2`."* Since `corpus/lessons/round-42.md` is a landed artifact and this seat is read-only, this is
reported, not edited.

The same claim is repeated in the landed `SKILL.md:292` (`r42-r1-counter` row): *"three exemption rows read green
without `--fleet-root` and `findings=2` (`LG-DANGLING-PTR-EXEMPT-STALE`) with it"* — same defect, same
correction. Also `census/round-42/preregistration.txt`'s R1 target (`SUMMARY findings=0 deleted=0 rows_added=3
stale=0`) is unreachable in an honest evaluation; the preregistration is frozen and is not amended, which the
lesson's M42-5 erratum convention covers.

## 7. Residual gap: the copies' *bytes* are pinned by a file nothing reads

`SHA256SUMS` is the only thing that pins the copies' content, and:

```
$ grep -rn 'jj-w1-reports' --include='*.py' --include='*.sh' .   (excluding waves/)
(no output)
$ grep -rn 'SHA256SUMS' --include='*.py' --include='*.sh' . | grep -v '/waves/'   → only census/round-29..32 sources/SHA256SUMS
(no consumer of census/round-42/jj-w1-reports/SHA256SUMS)
```

and no committed receipt records the digest check (`grep -rn 'c632531f\|ceb6d728' --include='*.txt' --include='*.md' --include='*.tsv' .`
outside wave-1 reports → no output). The gate checks **path existence**, not bytes: LIVENESS C corrupted
`JjTrialSouji.md` in a clone (`printf 'x\n' >>`) and the gate stayed green in both modes
(`SUMMARY findings=0 …` at commit `f27d27943fb622f14fd0f32b1e6a5dde7bf1b64f`, plain and fleet), while the file's
sha256 changed to `d96b519e4b50c92eada6fb623378c6d66fc11640cda282822228b6185e3c7818`.

So "byte-exact copies" is true **today** (verified above, by hand, against both the lane and the fleet), but it is
enforced by nothing in the lane: a future edit to either copy, or to the fleet original, would leave every gate
green while the README's "byte-exact" claim silently became false. Severity low (the claim is currently true and
the digests are published), but it is the one thing in this repair that no instrument re-checks.

## 8. Verification gaps and residual risk

- **Not run:** the landing gate at the tip with `--json`; the C1/C2/C3 counters and their controls (out of this
  seat's scope — R1 only); `git fsck` on the fleet repo (not needed for the byte claim, which rests on
  `sha256sum`); the fleet repo's own gate (`--round 41` there is a different lane).
- **Transient noted:** one unreproducible `git show` failure during a concurrent repack (§1). 30 consecutive
  successful reads after it; `ls-tree` and `cat-file` agree with the committed blob.
- **Frozen instruments not edited:** `census/round-42/r1-counter.py` (no gate-exit check), `tools/souji-landing-gate.py`
  (`load_pointer_exemptions` grammar; `pointer_exemptions - used_exemptions` staleness),
  `census/round-42/preregistration.txt`, `census/round-42/controls/r1-control.txt`. The three defects above are
  **reported as findings for the L1**, exactly as preregistration rule 1 requires; none was edited.
- **Cross-lane consistency:** `census/round-42/records/gate-both-modes.txt` is committed at the tip
  (`100644 blob 55cba6f6…`) and its contents are reproduced by my runs at its own rev (`51f204fb…`) and hold at
  the tip.

## 9. Exact commands run (all from the fleet root `/home/vgpnk/Projects/shokunin` unless noted)

```bash
# §1 byte identity
cmp souji-shokunin/census/round-42/jj-w1-reports/JjAuditSouji.md .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
cmp souji-shokunin/census/round-42/jj-w1-reports/JjTrialSouji.md .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
sha256sum <both lanes' copies> <both fleet originals>
cat souji-shokunin/census/round-42/jj-w1-reports/SHA256SUMS
sha256sum -c <SHA256SUMS>            # run in the lane copies dir and in the fleet reports dir
git -C /home/vgpnk/Projects/shokunin log -1 --format='%H %ad %s' -- .ufo/waves/hyaku/jj-w1/reports/Jj{Audit,Trial}Souji.md
git -C /home/vgpnk/Projects/shokunin show f47ad6ba8d30…:.ufo/waves/hyaku/jj-w1/reports/Jj{Audit,Trial}Souji.md | sha256sum
git -C /home/vgpnk/Projects/shokunin show 7d0c7605:.ufo/waves/hyaku/jj-w1/reports/Jj{Audit,Trial}Souji.md | sha256sum
git -C /home/vgpnk/Projects/shokunin log --oneline f47ad6ba8d30..HEAD -- .ufo/waves/hyaku/jj-w1/reports/Jj{Audit,Trial}Souji.md
git -C /home/vgpnk/Projects/shokunin status --porcelain -- .ufo/waves/hyaku/jj-w1/reports/
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r 3105a63… -- census/round-42/jj-w1-reports/
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63…:census/round-42/jj-w1-reports/{JjAuditSouji.md,JjTrialSouji.md,SHA256SUMS}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -p 363d8ae3… | sha256sum

# §2 the two repointed lines
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff bf618f6… 3105a63… -- corpus/README.md corpus/knowledge/jj-colocation-receipts.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat bf618f6… 3105a63… -- corpus/pointer-exemptions.tsv corpus/README.md corpus/knowledge/jj-colocation-receipts.md

# §3 anchors
grep -n '^### F3' census/round-42/jj-w1-reports/JjAuditSouji.md
grep -n '^## Step 5' census/round-42/jj-w1-reports/JjTrialSouji.md
sed -n '53,80p' census/round-42/jj-w1-reports/JjTrialSouji.md

# §4 four gate runs at the tip + base contrast + receipt rev + --base leg
python3 -B tools/souji-landing-gate.py --root . --rev <TIP> --round 41 [--fleet-root /home/vgpnk/Projects/shokunin]
python3 -B tools/souji-landing-gate.py --root . --rev <TIP> --round 42 [--fleet-root /home/vgpnk/Projects/shokunin]
python3 -B tools/souji-landing-gate.py --root . --rev <TIP> --base bf618f6… --round 41|42
python3 -B tools/souji-landing-gate.py --root . --rev bf618f6… --round 41 [--fleet-root /home/vgpnk/Projects/shokunin]
python3 -B tools/souji-landing-gate.py --root . --rev 51f204fb… --round 41 [--fleet-root /home/vgpnk/Projects/shokunin]

# §5 the frozen counter at the tip
python3 -B census/round-42/r1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63… --scratch /fast/scratch/hyaku/souji-r42/R42w2reviewer08

# §6 predicate experiments (scratch clones under /fast/scratch/hyaku/souji-r42/R42w2reviewer08/)
#   exp.sh: baseline, EXP A (rows as printed), EXP B (loader-admissible rows)
#   exp2.sh: VARIANT C (rows citing the landed copies), LIVENESS A/B/C
# each clone: git init; git remote add origin <lane>; git fetch origin <rev>; git checkout; toplevel asserted == clone;
#   identity only via GIT_AUTHOR_*/GIT_COMMITTER_*; no git commit outside the clone; no jj anywhere.

# §7 consumers of the digests
grep -rn 'jj-w1-reports' --include='*.py' --include='*.sh' . | grep -v '/waves/'
grep -rn 'c632531f\|ceb6d728' --include='*.txt' --include='*.md' --include='*.tsv' . | grep -v '/waves/w1/'
```

Scratch directory `/fast/scratch/hyaku/souji-r42/R42w2reviewer08/` (two clones, the two experiment scripts, the
extracted `SHA256SUMS`) was removed after the runs; nothing outside it and this report was written.

Report: `.ufo/waves/round-42/w2/R42w2reviewer08.md`
