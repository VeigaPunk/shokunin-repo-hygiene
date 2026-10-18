# gate-runbook-17 — souji-shokunin round 8 (seat S17, runbook drafter)

Drafted: 2026-10-18 18:38-03:00. Fragment pair: this file +
`census/round-8/seat-17.json`. Every command marked **TESTED** was executed
read-only on the live fleet today by S17 with the observed output recorded
below. Every command marked **EXECUTE-THEN** is gated and must not run before
its gate-open condition holds. Souji seats never run `git fetch/push/commit/
branch` on live repos; pushes below belong to the owning lane or the operator.

## 0. Current blocker scoreboard (all measured 2026-10-18 18:28–18:38 -03:00)

| Class | Blocker | Observed now | Gate-open condition |
|---|---|---|---|
| A — 96 approval rows | operator sign-off pending | 96/96 `SAFE pushed` in dry-run; gate1/gate2 fails = 0 | operator names `census/round-3/operator-approval-list.tsv` as approved (LOG.md entry or directive) |
| B — gd2d pins | branches unpushed | wt-r98/99/100 `unique_vs_remotes=1` each; all 3 locked; dirs present; main ahead 5 | gd2d lane pushes; per-branch unpushed → 0; checkout dirs retired |
| C — kotodama | lane unpushed + dirty | 53 unpushed commits, 9 dirty paths, `.scratch` 41G growing | lane pushes (→0) + clean (→0) + stable byte count + classification pass re-derived |
| D — lane remote | origin 404 | `git ls-remote origin HEAD` → "Repository not found" (TESTED) | operator creates `VeigaPunk/shokunin-repo-hygiene`; push lands; `unpushed_total` → 0 |
| E — lore `.scratch` | 3 gates fail | gate1 PASS (0 unpushed-touching); gate2 FAIL (`??` non-empty); gate3 FAIL (mtime age 0.77d < 1d; live citation LOG.md:3529–3530) | all three gates pass together (see §5) |

Recommended execution order: D first (a live origin re-opens the `pushed`
receipt for souji's own 13 local-only commits — fleet-wide reaudit trigger
from r7), then A (independent of D — the 96 rows verify against the FLEET
root's `origin/master`, which already exists), then B, C, E.

---

## 1. Class A — 96 approval rows awaiting operator

Row source: `census/round-3/operator-approval-list.tsv` (97 lines = header +
96 rows; columns `path size_bytes intro_commit sha256 source evidence` — only
`path`, `source`, `evidence` are populated; key every step on `path`).

**Who:** operator signs off; souji **parent** stages; a **non-author blind
seat** verifies; operator gives final OK before any delete.

### Step A0 — quarantine dry-run (read-only, runnable any time) — TESTED

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
tail -n +2 census/round-3/operator-approval-list.tsv | cut -f1 \
  | while IFS= read -r p; do bash tools/souji-verify.sh "$p"; done
```

Observed 2026-10-18: `rows=96`, tally `96 SAFE/pushed`, zero `NOT-SAFE`
(each line `VERDICT <abs-path> SAFE pushed intro=b2f2efae7549
ref=refs/remotes/origin/master ancestor=yes`). Tool selftest green
(`--selftest` exit 0; fixture-mutating selftests only). An absent path
fails closed: `NOT-SAFE unreachable missing path` (TESTED on
`/tmp/s17-absent-probe-xyz`) — if any row was already removed by other
means, the dry-run flags it instead of skipping silently. **ABORT** the
gate-open flow if any row returns `NOT-SAFE`.

### Step A0b — gate1/gate2 re-derivation (read-only) — TESTED

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
tail -n +2 census/round-3/operator-approval-list.tsv | cut -f1 \
  | while IFS= read -r p; do
      rel="${p#/home/vgpnk/Projects/shokunin/}"
      g1=$(git -C /home/vgpnk/Projects/shokunin log --branches --not --remotes \
            --oneline -- "$rel" | wc -l)
      g2=$(git -C /home/vgpnk/Projects/shokunin status --porcelain=v1 \
            --untracked-files=all -- "$rel" | wc -l)
      [ "$g1" -ne 0 ] || [ "$g2" -ne 0 ] && echo "FAIL $g1/$g2 $rel"
    done
```

Observed: `total=96 gate_fails=0`. Must print nothing at execution time.

### Step A1 — staging (only after operator sign-off; parent executes)

```bash
cd /home/vgpnk/Projects/shokunin
Q=".ufo-quarantine/$(date -u +%Y-%m-%dT%H%M%SZ)"
mkdir -p "$Q"
tail -n +2 souji-shokunin/census/round-3/operator-approval-list.tsv | cut -f1 \
  | while IFS= read -r p; do
      [ -e "$p" ] || { echo "SKIP absent: $p" >> "$Q/staging.log"; continue; }
      rel="${p#/home/vgpnk/Projects/shokunin/}"
      sha256sum "$p" >> "$Q/pre-staging-sha256.txt"
      mv -v -- "$p" "$Q/$(printf %s "$rel" | tr / __)" >> "$Q/staging.log" 2>&1
    done
```

Plain `mv` per the r7 parent template (records the rel→quarantine mapping in
`staging.log`; tracked rows will show as `D` in fleet-root status — that is
expected and is the operator's commit, not souji's; no `git mv`, no `git
commit` by seats).

### Step A2 — hold

Hold window = until the next souji round's gate re-check, ≥24h. Nothing
reads, moves, or deletes inside `$Q`.

### Step A3 — second receipt check (next round; parent + blind seat)

```bash
cd /home/vgpnk/Projects/shokunin
cd "$Q" || exit 1
awk '{print $1}' pre-staging-sha256.txt | sort > /tmp/a.$$
find . -type f ! -name pre-staging-sha256.txt ! -name staging.log \
  -exec sha256sum {} + | awk '{print $1}' | sort > /tmp/b.$$
diff /tmp/a.$$ /tmp/b.$$ && echo SECOND-CHECK-OK
rm -f /tmp/a.$$ /tmp/b.$$
```

Re-run Step A0 too: every original path must now return
`NOT-SAFE unreachable missing path` (the fail-closed post-staging state).

### Step A4 — delete (only after SECOND-CHECK-OK **and** operator final OK)

```bash
rm -rf -- "$Q"     # never rm outside .ufo-quarantine/
```

Parent records the deletion in LOG.md with the receipt evidence. The fleet
root commit of the deletions belongs to the operator.

---

## 2. Class B — gd2d pins (wt-r98 / wt-r99 / wt-r100)

**Who:** gd2d lane owner (or operator) pushes and retires the three checkout
dirs; souji parent verifies receipts, unlocks, prunes metadata; blind seat
re-verifies.

### Step B1 — the lane pushes (gate-open act; NOT a souji command)

```bash
git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin \
  push origin main wt-r98 wt-r99 wt-r100
```

### Step B2 — souji verifies the push (read-only; no fetch)

```bash
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
for b in main wt-r98 wt-r99 wt-r100; do
  echo "$b local=$(git rev-parse --short "$b") remote=$(git ls-remote origin "refs/heads/$b" | cut -c1-8)"
done
# PROCEED only when local == remote for all four.
# Observed pre-gate (18:33): wt-r98/99/100 unique_vs_remotes=1 each;
# main_ahead=5 — all four must reach 0 unique:
for b in wt-r98 wt-r99 wt-r100; do
  echo "$b unique=$(git rev-list --count "$b" --not --remotes)"
done
```

### Step B3 — checkout dirs retired (lane owns the work products)

```bash
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
for w in game-dev-2d-shokunin-wt-r98 game-dev-2d-shokunin-wt-r99 game-dev-2d-shokunin-wt-r100; do
  [ -d "$w" ] || continue
  [ -z "$(git -C "$w" status --porcelain)" ] || { echo "ABORT dirty $w"; break; }
  git worktree unlock "$w"
  git worktree remove "$w"
done
```

Any dirty checkout → ABORT (lane work lives there).

### Step B4 — souji receipt check on the registrations, then metadata prune

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
for w in game-dev-2d-shokunin-wt-r98 game-dev-2d-shokunin-wt-r99 game-dev-2d-shokunin-wt-r100; do
  bash tools/souji-verify.sh --json "/home/vgpnk/Projects/shokunin/$w"
done
# expect three × SAFE with receipt=metadata-prune (dir absent + unique=0)
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
git worktree prune -v
git worktree list          # expect main + /var/tmp/r102-S1 only (5 → 2 lines)
ls .git/worktrees/         # expect r102-S1 only
```

`/var/tmp/r102-S1` (detached, round-102 seat worktree) is out of this
class's scope — leave it unless its own round retires it.

---

## 3. Class C — kotodama awaiting push

**Who:** kotodama lane pushes and cleans its own tree; souji parent re-checks
gates; operator sign-off before ANY `.scratch` action (41G live tree).

### Step C1 — gate-open re-check (read-only; executed by souji parent after the kotodama lane reports push+clean)

```bash
cd /home/vgpnk/Projects/shokunin/kotodama-shokunin
echo "unpushed=$(git log --branches --not --remotes --oneline | wc -l)"   # must be 0 (observed 18:34: 53)
echo "dirty=$(git status --porcelain | wc -l)"                            # must be 0 (observed 18:34: 9)
du -sb .scratch; sleep 300; du -sb .scratch   # byte counts must be identical (observed: 41G and growing ~2.3MB/s historically)
```

### Step C2 — classification pass re-derived

Re-derive the per-file classification from the r6 handoff
(`census/round-6/kotodama-scratch-handoff.md`) against the then-current
tree — do not act on the r6 snapshot's numbers. Every removal candidate
needs its own receipt via:

```bash
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh \
  --json <kotodama-path>   # per target; only SAFE rows go on a ticket list
```

Then the same staging → hold → second-check → operator-OK → delete flow as
§1 Steps A1–A4, rooted at `kotodama-shokunin/.ufo-quarantine/`. If any gate
or the stability probe fails: hands off (r6/r7 standing verdict
NOT-SAFE/hands-off remains in force).

---

## 4. Class D — lane-remote creation (souji origin 404)

**Who:** OPERATOR only (PROVINCE.md: "Publishing, vault approval, remote
creation — operator-owned"). No souji seat runs the push.

### Step D1 — operator creates the repo

Create EMPTY repo `VeigaPunk/shokunin-repo-hygiene` on GitHub (no README, no
license — the local history is the source of truth). The `origin` URL is
already configured in the lane; do not re-add it.

### Step D2 — verify existence, then push (operator or delegated session under operator sign-off, recorded in LOG.md)

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
GIT_TERMINAL_PROMPT=0 git ls-remote origin HEAD   # TESTED 18:31: "remote: Repository not found." — must succeed after creation
git push -u origin master                          # 13 local-only commits land (observed 18:31: unpushed_total=13)
```

### Step D3 — verify receipts are now establishable

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git log --branches --not --remotes --oneline | wc -l   # expect 0
git branch -r                                           # expect origin/HEAD -> origin/master, origin/master
git ls-remote origin refs/heads/master                  # must equal git rev-parse --short master
```

### Step D4 — fleet-wide reaudit (r7 trigger 1)

With souji's `refs/remotes` non-empty, re-run gate1+gate3 on every lane
candidate class (tools/, tests/vault, census archive candidates) and re-run
the §1 Step A0 dry-run. The r7 finding "every pushed receipt inside the lane
repo is unverifiable" retires the moment Step D3 holds.

---

## 5. Class E — lore `.scratch` re-check conditions

Observed 18:33–18:36: `.scratch` 272K, dir mtime `2026-10-18 00:03:50
-0300`; gate1 PASS vacuously (`unpushed_touching_lines=0`); gate2 FAIL
(`?? .scratch/V02/...` non-empty); gate3 FAIL (age 0.77d < 1d; live
citations at `LOG.md:3529–3530`); lore has 3 unpushed commits incl.
`6cec83a` whose .gitignore rules cover only
`.ufo/waves/**/*-scratch/` and `baseline-tree/` — **proven NOT lane-root
.scratch**: `git check-ignore -v .scratch/V02/.../README.md` → exit 1
(TESTED). Stale-eligible (mtime ≥1d) no earlier than **2026-10-19 00:03:50
-03:00**, and only if the dir is not touched again.

**Who:** lore lane retires/answers the gates; souji parent re-checks all
three together; quarantine-first staging; operator final OK.

### Step E1 — three-gate re-check (read-only; all must pass in ONE sitting)

```bash
cd /home/vgpnk/Projects/shokunin/lore-shokunin
stat -c '%y' .scratch                                                   # G3a: >= 2026-10-19 00:03:50 -0300, unchanged since
git log --branches --not --remotes --oneline -- .scratch | wc -l        # G1: must be 0
git status --porcelain=v1 --untracked-files=all -- .scratch | wc -l     # G2: must be 0
grep -rn --exclude-dir=.git -e 'lane-root .scratch' -e '\.scratch/V02' \
  LOG.md *.md 2>/dev/null                                               # G3b: must print nothing (citation retired/pushed by a lore round)
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh \
  --stale-days 1 --json .scratch                                        # G3c: expect SAFE receipt=stale
```

G2 path to zero: the lore lane must actually delete or move the `.scratch`
contents (ignore rules will NOT hide them — see check-ignore proof above),
in its own round, with its tree clean and pushed.

### Step E2 — quarantine-first execution (souji parent, only when E1 is all-green)

Same flow as §1 Steps A1–A4 rooted at `lore-shokunin/.ufo-quarantine/`:
stage (`mv`), hold ≥24h / one round, hash-compared second check, operator
final OK, delete, LOG.md entry. Any gate red at re-check time → the ticket
dies; re-derive from scratch next round (fail-closed, per AGENTS.md).

---

## 6. Standing refusals (every class, every seat)

- No souji seat runs `git fetch/push/commit/branch` on live repos — pushes
  in §2/§4 are written for the owning lane/operator. `ls-remote` and
  `rev-list` are the only remote-facing reads.
- Any NEW quarantine runner tool proves itself on `mktemp` fixtures
  (`--selftest` + a scripted runner scenario) before touching anything real.
- Never read secret-shaped files, `.ufo/state/`, `.ufo/watchdog.log`.
- Uncertain at any step → verdict `NOT-SAFE`, stop, record in LOG.md.
