# Draft — corpus/lessons/round-90.md `## Mistakes` (souji r90, seat S90Scribe)

Target: `corpus/lessons/round-90.md`, a NEW file (the lane has `corpus/lessons/round-89.md` as the newest; there
is no `round-90.md` yet — `ls corpus/lessons/` ends at `round-89.md` and `round-89-verifier-spotcheck.md`).

**Format** — copied from the r89 file's own `## Mistakes` table (`corpus/lessons/round-89.md:57-65`): a five-column
Markdown table `| # | class | evidence pointer | captured-by | fix |`, one row per mistake.

**Numbering caveat for the L1:** this seat's draft numbers the row **M1** (the only mistake this seat drafts).
If the L1 lands other mistakes in the same file first, renumber so the `QUALITY.md` Q165 row's lesson pointer
(`corpus/lessons/round-90.md M1`) still resolves — `corpus/QUALITY.md:16-18` requires a lesson pointer "of the form
`round-12 M<nn>`" to resolve to the row with that id in the file's `## Mistakes`.

## Status: the L1 has already landed an M1 covering this defect

While this seat was drafting, the L1 landed `corpus/lessons/round-90.md` with its own M1 row for exactly this
defect. **This seat's draft and the L1's landed row are the same mistake.** The comparison, cell by cell:

| cell | the L1's landed M1 (in `corpus/lessons/round-90.md`) | this seat's draft | verdict |
|---|---|---|---|
| class | "wave evidence left gitignored: the r89 commit message said '12 seat reports' but `.ufo/waves/` is gitignored, so a clone of the pushed tip could not resolve the pre-file ledger's artifacts (13 `artifact-missing` rows)" | "wave evidence left gitignored: the round's 12 seat reports and their receipts were never committed, so the pushed tip could not resolve the pre-file ledger's artifacts — the ledger itself is committed and complete, but every path it names is absent from the tree, and the landed-changes row claimed 'wave evidence (12 seat reports + receipts + results)' for a commit whose tree contains none of them" | **the landed one is tighter.** It names the count (13 `artifact-missing` rows) in the class cell itself. This seat's version buries the count in the evidence-pointer cell, where a reader scanning the table does not see it. |
| evidence pointer | "`corpus/lessons/round-89-verifier-spotcheck.md` §1 and §2; `git ls-tree -r 4864129b -- .ufo/waves/round-89` lists only six files" | "`corpus/lessons/round-89-verifier-spotcheck.md` §1 'Wave-evidence durability: DEFECT (major, status-neutral)' and §7 item 1; `.gitignore:1` is `.ufo/waves/`; `git ls-tree -r --name-only 4864129b -- .ufo/waves/round-89` lists only `build-spec.py`, `claim-falsification.tsv`, `claims.json`, `w1-dispatch.json`, `w1-results.json`, `w1-spec.json`, `w1.ready`; `git check-ignore -v …` reports the ignore and `git status --porcelain --ignored` shows `!! .ufo/waves/round-89/w1/`; r86/r87/r88 force-added their wave files (209/280/125 files), so r89 is a regression" | **the landed one is correct where this seat's draft was WRONG.** The landed row cites `4864129b`, where the tree holds **six** files — this seat measured that: `git ls-tree -r --name-only 4864129b -- .ufo/waves/round-89` → 6 files, and `claims.json` was added LATER, at `c2ee31ae` (7 files at the closure tip `1786b552`). This seat's draft listed seven files under the `4864129b` citation — **a seven-for-six slip of its own.** The landed row gets it right. |
| captured-by | "the pre-file gate's artifact-existence check — it passed on the local tree and failed on the pushed bytes, which is the only place it counts" | "the pre-file gate's artifact-existence check (`scripts/hyaku/prefile-falsification.py`, `resolve_artifact` -> the `artifact-missing` finding at the ledger row): it resolves each ledger artifact against the wave directory and reports `artifact-missing` when the path does not exist under any permitted base. On the local working tree the gate reads `PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=7 findings=0`, EXIT 0 … On the pushed bytes it reads `PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13`, EXIT 1, all 13 rows `artifact-missing`" | the landed one is **sharper in substance** ("which is the only place it counts" is the rule; this seat's draft states the rule only implicitly). This seat's draft carries the **exact commands and outputs**, which the landed row does not — see "The defect reproduced" below, which is this seat's contribution to keep. |
| fix | "every r90 wave file is named explicitly to `jj-lane.sh` (`jj file track --include-ignored`), and the round checks `git ls-tree -r <tip> -- .ufo/waves/round-90` lists the seat reports before filing (plans/round-90.md A0.6)" | "commit the wave evidence: `git add -f` the round's seat reports and their receipts under `.ufo/waves/round-<N>/w1/` (or un-ignore that path in the lane's own `.gitignore`), so the ledger's artifacts resolve from the pushed lane and not only from the local working tree; and stop writing 'N seat reports' in a commit message whose tree does not contain them." | **the landed one is correct for THIS lane and this seat's is wrong.** The lane is jj-colocated: `scripts/hyaku/jj-lane.sh` is the only writer (`jj-lane.sh commit <lane-dir> --as <id> -m <message> -- <path>...`), and its `file track` call carries `--include-ignored` precisely so an ignored path can be named explicitly. This seat's `git add -f` suggestion names a command the lane does not use. The landed fix also adds a **pre-filing check** (`git ls-tree -r <tip> -- .ufo/waves/round-90` must list the seat reports), which is stronger than "commit it" — it makes the check a gate. |

**Recommendation to the L1: keep the landed M1 as it is.** It is more accurate than this seat's draft on three of the
four cells (the six-file count, the jj-colocated fix, the sharpness of the captured-by rule). The one thing this
seat's draft adds that the landed row lacks is the **exact reproduction** below — the commands and their verbatim
outputs, including the fresh-clone run on the pushed bytes. **If the L1 wants the reproducer in the lesson, the
"## The defect reproduced" section below is the paste-ready text; if not, this seat's report carries it either way.**

**One correction this seat must carry forward: the landed row's own fix rests on the L1's `plans/round-90.md` A0.6,
which this seat checked** — `jj-lane.sh` carries `--include-ignored` on its `file track` call
(`scripts/hyaku/jj-lane.sh:654-658`: "`# Record tracking for named paths. --include-ignored (which also admits files
…`"), so naming the wave files explicitly to the helper is the supported route, and `.ufo/waves/…` is not on the
helper's never-committable list (`.ufo`, `.ufo/state`, `.ufo/state/*`, `.ufo/watchdog.log` — `jj-lane.sh:513`). The
fix route is sound.

## The table (this seat's draft, for comparison only — the L1's landed M1 supersedes it)

````markdown
## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | wave evidence left gitignored: the round's 12 seat reports and their receipts were never committed, so the pushed tip could not resolve the pre-file ledger's artifacts — the ledger itself is committed and complete, but every path it names is absent from the tree, and the round's landed-changes row claimed "wave evidence (12 seat reports + receipts + results)" for a commit whose tree contains none of them | `corpus/lessons/round-89-verifier-spotcheck.md` §1 "Wave-evidence durability: DEFECT (major, status-neutral)" and §7 item 1; `.gitignore:1` is `.ufo/waves/`; `git ls-tree -r --name-only 4864129b -- .ufo/waves/round-89` lists only `build-spec.py`, `claim-falsification.tsv`, `claims.json`, `w1-dispatch.json`, `w1-results.json`, `w1-spec.json`, `w1.ready`; `git check-ignore -v .ufo/waves/round-89/w1/S89Connector.md` reports the ignore and `git status --porcelain --ignored` shows `!! .ufo/waves/round-89/w1/`; r86/r87/r88 force-added their wave files (`git ls-files .ufo/waves/round-8{6,7,8}` -> 209/280/125 files), so r89 is a regression | the pre-file gate's artifact-existence check (`scripts/hyaku/prefile-falsification.py`, `resolve_artifact` -> the `artifact-missing` finding at the ledger row): it resolves each ledger artifact against the wave directory and reports `artifact-missing` when the path does not exist under any permitted base. On the local working tree the gate reads `PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=7 findings=0`, EXIT 0 — the files are on disk. On the pushed bytes it reads `PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13`, EXIT 1, all 13 rows `artifact-missing` | commit the wave evidence: `git add -f` the round's seat reports and their receipts under `.ufo/waves/round-<N>/w1/` (or un-ignore that path in the lane's own `.gitignore`), so the ledger's artifacts resolve from the pushed lane and not only from the local working tree; and stop writing "N seat reports" in a commit message whose tree does not contain them. The gate is the check that catches this — a lane that passes it locally has proved only that the files are on the local disk |
````

## The defect reproduced (commands + exact output), so the row is a reproducer and not an opinion

All commands run from the fleet root `/home/vgpnk/Projects/shokunin` or the lane; read-only git only; the clone is
a scratch fixture under `/fast/scratch/hyaku/souji-r90/S90Scribe/clone/`.

**1 — the wave files exist on disk but are gitignored.**

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
ls .ufo/waves/round-89/w1/*.md | wc -l          # 12  (the 12 seat reports, on disk)
git ls-files .ufo/waves/round-89/w1/ | wc -l     # 0   (none tracked)
git check-ignore -v .ufo/waves/round-89/w1/S89MutCounter.md
```

Output:

```
.gitignore:1:.ufo/waves/	.ufo/waves/round-89/w1/S89MutCounter.md
```

**2 — the pre-file gate PASSES locally.**

```
cd /home/vgpnk/Projects/shokunin
python3 scripts/hyaku/prefile-falsification.py --lane souji --round 89 --fleet /home/vgpnk/Projects/shokunin
```

Output:

```
PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=7 findings=0
EXIT=0
```

**3 — the same gate FAILS on the pushed bytes (a fresh clone of the r89 closure tip `1786b552`).**

```
S=/fast/scratch/hyaku/souji-r90/S90Scribe
mkdir -p "$S/clone"
git clone --quiet --no-local --shared /home/vgpnk/Projects/shokunin/souji-shokunin "$S/clone/souji-shokunin"
git -C "$S/clone/souji-shokunin" checkout --quiet 1786b5527b29f48a6a04b5b11a50528182880761
mkdir -p "$S/clone/fleet"
cp -r "$S/clone/souji-shokunin" "$S/clone/fleet/souji-shokunin"
mkdir -p "$S/clone/fleet/.ufo/reports/round-89"
cp /home/vgpnk/Projects/shokunin/.ufo/reports/round-89/souji.md "$S/clone/fleet/.ufo/reports/round-89/souji.md"
cd /home/vgpnk/Projects/shokunin
python3 scripts/hyaku/prefile-falsification.py --lane souji --round 89 --fleet "$S/clone/fleet"
```

Output (verbatim; 13 findings, all `artifact-missing`):

```
FINDING artifact-missing line 2 artifact=.ufo/waves/round-89/w1/S89MutCounter.md does not exist
FINDING artifact-missing line 3 artifact=.ufo/waves/round-89/w1/S89Sentinel.md does not exist
FINDING artifact-missing line 4 artifact=.ufo/waves/round-89/w1/S89Reviewer.md does not exist
FINDING artifact-missing line 5 artifact=.ufo/waves/round-89/w1/S89Simplifier.md does not exist
FINDING artifact-missing line 6 artifact=.ufo/waves/round-89/w1/S89ExecC2.md does not exist
FINDING artifact-missing line 7 artifact=.ufo/waves/round-89/w1/S89Critic.md does not exist
FINDING artifact-missing line 8 artifact=.ufo/waves/round-89/w1/S89Scribe.md does not exist
FINDING artifact-missing line 9 artifact=.ufo/waves/round-89/w1/S89Reviewer.md does not exist
FINDING artifact-missing line 10 artifact=.ufo/waves/round-89/w1/S89Critic.md does not exist
FINDING artifact-missing line 11 artifact=.ufo/waves/round-89/w1/S89Sentinel.md does not exist
FINDING artifact-missing line 12 artifact=.ufo/waves/round-89/w1/S89Labrat.md does not exist
FINDING artifact-missing line 13 artifact=.ufo/waves/round-89/w1/S89Connector.md does not exist
FINDING artifact-missing line 14 artifact=.ufo/waves/round-89/w1/S89Distiller.md does not exist
PREFILE-FALSIFICATION: FAIL claims=2 rows=13 attack_seats=7 findings=13
EXIT=1
```

**4 — the tree at that tip really does lack the seat reports.**

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git ls-tree -r --name-only 1786b5527b29f48a6a04b5b11a50528182880761 -- .ufo/waves/round-89
```

Output:

```
.ufo/waves/round-89/build-spec.py
.ufo/waves/round-89/claim-falsification.tsv
.ufo/waves/round-89/claims.json
.ufo/waves/round-89/w1-dispatch.json
.ufo/waves/round-89/w1-results.json
.ufo/waves/round-89/w1-spec.json
.ufo/waves/round-89/w1.ready
```

(The ledger `claim-falsification.tsv` and `claims.json` ARE committed; the twelve `w1/` seat reports and their
receipts are not. The clone confirms it: `ls .ufo/waves/round-89/w1/` in the clone → "No such file or directory".)

**The same defect is LIVE in r90 — this is the part the L1 must act on.** At lane tip `fd25bfc5`:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
ls .ufo/waves/round-90/w1/*.md | wc -l          # 12  (on disk)
git ls-files .ufo/waves/round-90/w1/ | wc -l     # 0   (none tracked)
git check-ignore -v .ufo/waves/round-90/w1/S90Scribe.md
```

Output:

```
.gitignore:1:.ufo/waves/	.ufo/waves/round-90/w1/S90Scribe.md
```

`.ufo/waves/round-90/` currently has exactly ONE tracked file (`git ls-files .ufo/waves/round-90` →
`.ufo/waves/round-90/build-spec.py`), so **if r90 lands the way r89 landed, r90's pre-file gate will also pass
locally and fail on the pushed bytes.** This seat's own report file (`.ufo/waves/round-90/w1/S90Scribe.md`) is
inside the ignored path and is therefore **not** durable until the L1 force-adds it. The lane already owns a tool
for the durable copy: `tools/souji-wave-evidence-capture.sh <lane-abs> <round-N>` copies the wave tree into
`census/round-<N>/waves/` with a `manifest.sha256` and re-verifies it — that is the receipt-style route (the lane
used it for rounds 26-45 and 66). The `git add -f` route is what rounds 86/87/88 did and what the r89 spot-check
asked for.

## Is this a HIGH finding (a no-work control that passes the target)? — NO, and the distinction matters

The brief says: "A no-work control that passes the target is a HIGH finding: say so." This is **not** that case,
and the row above says so explicitly rather than borrowing the severity:

- The pre-file gate's **control** is the r89 round itself, and it **FAILED** on the pushed bytes
  (`findings=13`, EXIT 1). The defect is a failure of the round's own control, caught and named.
- The gate's **local** pass (`findings=0`, EXIT 0) is **not** a no-work control that reaches the target: it is the
  gate run against the working tree, where the files DO exist. It proves the ledger is complete and every artifact
  is present **on this host** — it proves nothing about the pushed bytes, and the lane's own closing judge already
  recorded exactly that distinction ("the same gate fails for durability, not for wording", spot-check §2).
- No claim wording is falsified by this: the r89 spot-check says the ledger's rows are real and the claim verdicts
  are unchanged ("The defect is named and routed; it does not change the claim verdicts"). It is a **durability**
  defect in the round's bookkeeping, which is why it belongs in `## Mistakes` and not in the round's narrowing
  amendments.

## What this seat did NOT check

- Whether the L1 will land the r89 wave evidence (the `git add -f` of round 89's twelve seat reports). This seat
  did not commit anything, so the r89 defect is still open as of lane tip `fd25bfc5`.
- Whether the lane's `.gitignore` will be changed (the fix column names both routes; the L1 picks one).
- The r89 closure report's own accuracy beyond the wave-evidence claim quoted here; this seat did not re-verify
  the spot-check's other ten routed defects.
