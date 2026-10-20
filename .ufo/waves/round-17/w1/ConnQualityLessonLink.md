STATUS: DONE — four candidate mistake rows linked to criteria; one premise falsified (the fixture `.git` stub was never committed and is absent at read time); C3's lane-side fix is only partly on disk and uncommitted.

# ConnQualityLessonLink — mistake→criterion link, round 17 wave 1

Role: connector. Axes named: **operability, calibration, coverage, depth, freshness, adjacency**. Judged on **calibration**. No delegation, no commits, no `jj`, no lane tool run, no live-census run. All citations below are either committed bytes at `HEAD=5fa6017` (`git rev-parse --short HEAD`), or worktree bytes explicitly labelled *worktree-only (uncommitted)*.

Method: read the four candidate mistakes' evidence pointers, resolve each pointer against the object database or the artifact, and for each row state the class, the resolving pointer, what captured it, the smallest fix, and the falsifier. The command list and raw outputs are in §6; every number in the rows below was produced by one of those commands, not inherited from prose.

## 1. Rows (draft for `corpus/lessons/round-17.md` `## Mistakes`)

| id | class | evidence pointer (resolves now) | captured-by | fix | shown able to fail (falsifier) | criterion link |
|---|---|---|---|---|---|---|
| R17-M1 | An auditor verdict was published as a scope violation without reading the flagged call; two classifier shape defects make failed calls look like out-of-scope writes. | `tools/souji-seat-audit.py:68-73` (`write_target`, first-comma split at `:73`); `:76-81` (`rel = target.lstrip("./")` at `:80` drops `.ufo`'s dot). `census/round-16/seat-audit-w2.json` summary `major=3`, `seats_with_major=["ConnReadmeIndex","RerunGateReplayR14"]`: row `line 180` args `.ufo/waves/round-16/w2/ConnReadmeIndex.md`; rows `line 225` args `\| 2 \| stale pin \| …`, `line 226` args `N6 is the exact harm …`. Transcripts: `census/round-16/transcripts/w2/ConnReadmeIndex.txt:179` `→ edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ error · File not found`; `w2/RerunGateReplayR14.txt:224-225` `→ edit(\| 2 \| stale pin …) ⇒ error · Validation failed`, `→ edit(N6 …) ⇒ error · Validation failed`. Published restatement: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-16/souji.md:47` “3 major V-WRITE-SCOPE (all failed edit calls, no bytes written)”. | No mechanism. The r16 non-author closure read the calls (`corpus/lessons/round-16-verifier-spotcheck.md` D4). The 20-case selftest has no relative-`.ufo`-report or prose/malformed-edit case. | Strip only a leading `./` (`target[2:] if target.startswith("./") else target`); when an `edit` argument has no `[path#hash]` form, classify it `V-WRITE-UNKNOWN`/malformed, never `V-WRITE-SCOPE`; add the two shapes to the selftest; commit the transcript manifest (on disk now, 144/144 verify) and a replay `--json` with expected verdict sets. | New selftest cases fail on the old classifier (`--selftest` today is 20/20 with neither shape); replay of `w2` gives `major=0`, replay of `w1` keeps exactly 1 major — `SrcGitNoLazyFetch`, `.ufo/waves/round-16/r16-placeholder.md`, `census/round-16/seat-audit-w1.json` line 144. Note the audit's `line` field is physical (1-based): JSON 225 ↔ the transcript's embedded `224:` call line (same +1 for 180↔179 and 226↔225), so a pointer must quote the call text, not only a number. | Q26 (test clause grows: exact verdict set + FP shapes); Q17 (manifest makes the replay resolve) |
| R17-M2 | A published count was hand-retyped and contradicts the enumeration it summarizes. | `LOG.md:902-903` “flagged 28 uncarried wave-2 STATUS lines”; `corpus/lessons/round-16.md:21` “flagged 28”; the same lesson carries **29** wave-2 bullets at `:58-86` (`sed -n '58,86p' corpus/lessons/round-16.md \| grep -c '^- \`'` → 29); the fleet report gives 29 twice (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-16/souji.md:14` “29 wave-2”, `:45` “`79bbe7a` → 29 LG-SEAT-UNCARRIED”); `census/round-16/gate-landing.json` summary `checked_markers=30`, `findings=0`. The 30th marker is `ConnLogConvention.md:385`, pre-carried at lesson `:43` (peer scout reproduced the predicate; peer evidence, not re-run here). | The r16 closure re-derived it (D3); nothing in the landing gate reads the prose number; the lesson's own bullet block contradicts it. | Append-only LOG correction (28→29) and fix lesson `:21`; carry the measuring command; with D6, commit the gate `--json` at the measurement and quote its `LG-SEAT-UNCARRIED` count instead of retyping. | The count command returns 29 on the same block; a check asserting “prose count == its own block bullet count” fails on 28 and passes on 29. This checks internal consistency only; the historical gate count needs the committed `--json` (D6). | Q10 (numbers match their table) extended to every published count; new Q27(b) |
| R17-M3 | jj keep refs are treated as durable roots, and jj-only heads are excluded from unpushed-touching checks; helper v1 published phantom deletions. | `refs/jj/keep` holds 8 refs; **6 keep-only** (`git rev-list --count <oid> --not --branches --tags --remotes` = 1 for `0254661`, `1e0d8d1`, `41ab059`, `719154d`, `dcc1512`, `dd2e322`), and **4 of those delete both tracked fixture files** (`git diff-tree --no-commit-id --name-status -r` → `D tests/vault/vadv54-run/p/p6repo/one.txt`, `D …/inner/keep.txt`, for `0254661`, `1e0d8d1`, `41ab059`, `719154d`). Root sites at `HEAD=5fa6017`: `tools/souji-verify.sh:351` (`log --oneline "$head" --not --all`) and `:809-813` (`for-each-ref --format='%(objectname)'` roots), `tools/souji-vault-verify.sh:517`, `:997-1001`, `tools/souji-quarantine.sh:1069-1073`; `grep -c 'jj_keep_unpushed\|refs/jj'` over the three tools at HEAD = 0/0/0. Upstream analysis: `.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` F1 `:55-86`, F2 `:88-117`, F3 `:118-131`; `JjTrialSouji.md:76` (nested empty `.git` ⇒ jj phantom deletions; sandbox commit `c31a345`). Helper v2 exists at fleet commit `14df5b9` with a static phantom guard (`scripts/hyaku/jj-lane.sh:618-653`, refuses `D <path>` when the path exists on disk) and a “never anything under refs/jj/” root rule (`:114`). | Nothing in the lane. The census `unpushed` column is branch-based (disclosed); the three receipt tools root at `--not --all`/all refs at HEAD; the jj trial found the class and the keep refs preserve the 4 phantom commits. | Durable roots = `refs/heads`, `refs/tags`, `refs/remotes` only in the three tools; add `--glob=refs/jj/keep/*` heads to every unpushed-touching `log … --branches --not --remotes -- <target>`; keep helper v2's phantom refusal; knowledge entry + recipes. **Status, bound to `HEAD=5fa6017`:** all three tools carry 0 `jj_keep_unpushed|refs/jj` markers (`git show HEAD:<tool> | grep -c` = 0/0/0) and the root sites are still `--not --all` (`verify:351/813`, `vault:517/1001`, `quarantine:1073`); only helper v2 (`14df5b9`) exists. The **worktree is a moving target**: minutes after the HEAD reads, `grep -c 'jj_keep_unpushed\|refs/jj'` returned 10 (verify) / 14 (vault) / 0 (quarantine) — uncommitted sibling edits. Bind no claim to those worktree bytes. | Fixture repo: (i) an absent worktree head held only by a keep ref must be `NOT-SAFE`, never `SAFE(metadata-prune)`; (ii) a keep-only commit touching the target must refuse; (iii) a repo with no `refs/jj/keep/*` must be byte-identical. Helper: v2 refuses the `D` of an on-disk file; v1 committed the 4 phantom rows — the 4 keep commits are the failing witness. v2's selftest claim (45/45; 28 cases fail on v1) is the commit-message claim only; it was **not run here** because `jj` execution is forbidden for this seat. | New Q27(c) (jj-colocated receipts) |
| R17-M4 | A candidate mistake premise was not resolved against the object database: an empty directory cannot be a committed path, and the worktree state changed during the round. | `git log --diff-filter=A -- tests/vault/vadv54-run/p/p6repo/one.txt` → `48a64d8 2026-10-18 … round-4 (amended)`, which adds **29 files** under `tests/vault/vadv54-run` (`git ls-tree -r --name-only 48a64d8`), including only `p6repo/inner/keep.txt` and `p6repo/one.txt` in `p6repo`; **no `.git` entry** (`git ls-tree -r 48a64d8 -- …/p6repo`), `git log --all -- '…/p6repo/.git'` empty, and `one.txt` is byte-identical at `48a64d8` and HEAD (`00508d39…`). `ls -la tests/vault/vadv54-run/p/p6repo` at 2026-10-20T13:33 → `inner/`, `one.txt`; no `.git` (dir mtime `Oct 20 13:33`, state changed during this wave). The hazard is real even though the stub is not committed: `JjTrialSouji.md:76` observed it and verified a directory-pathspec commit ships the deletions, and this lane's keep refs already hold 4 such commits (R17-M3). | None — Q17 is not applied to mistake rows, so the row as written (“committed as part of a run tree”) would itself violate `Q17`. | Rewrite the row: run tree added at `48a64d8` (r4 amended, 29 files); the `.git` stub is untracked, never committed, and absent at read time; prove the hazard from `JjTrialSouji.md:76` + the 4 keep commits; remove any stub before a directory-pathspec commit; bind worktree claims to a timestamp and revision (R16-M6). Smallest mechanical addition: apply Q17 resolution to every `## Mistakes` pointer and reject a path naming an empty directory. | `git ls-tree -r 48a64d8 -- …/p6repo` shows no `.git` ⇒ the row as stated fails; with the stub re-created, helper v2's guard refuses the `D` rows (`:647-653`); with it removed, the guard passes. | Q17 applied to `## Mistakes`; new Q27(a); R16-M6 |

## 2. What the four rows have in common (the link to criteria)

All four are **claims about a repository artifact that were never resolved against the artifact**: a classifier verdict (M1), a number (M2), a durability assumption (M3), a tree membership (M4). The lane already owns the instruments that can resolve each — the seat audit, the landing gate, `git cat-file`, and the census matrix — but Q17/Q25/Q26 are scoped to knowledge entries, landing claims, and seat evidence, not to the round's own `## Mistakes` table. That scoping is the gap.

Proposed criterion row (one row, three clauses; it supersedes nothing):

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q27 | A round's own defect record and instrument output are admitted evidence. (a) Every repository path a `## Mistakes` row names at a revision must resolve (`git cat-file -e <rev>:<path>`); a worktree-only observation is labelled with its read timestamp and revision, and an empty directory can never be a committed path. (b) Every published count is emitted by the command that measured it (a committed `--json`, or the artifact's own enumeration); a prose number that contradicts its own enumeration is a defect. (c) In a jj-colocated repo, receipt roots are durable namespaces only (`refs/heads`, `refs/tags`, `refs/remotes`; never `refs/jj/*`, `refs/stash`, `HEAD`), unpushed-touching checks also seed `--glob=refs/jj/keep/*`, and a commit that deletes a path still present on disk is refused. Extends Q10, Q17 and Q26; plain repos stay byte-identical. | round evidence, seat evidence, receipts | (a) the Q17 resolver over the lesson's mistake table (mutate a pointer to a nonexistent path → one finding); (b) `sed -n '<block>' corpus/lessons/round-17.md \| grep -c '^- \`'` equals the quoted count, plus a committed gate `--json`; (c) fixture repos: keep-only absent head → NOT-SAFE, keep-only touching commit → refuse, plain repo → byte-identical; helper v2's phantom guard on a nested `.git` | this report, R17-M1..M4; `JjAuditSouji.md` F1–F3; `JjTrialSouji.md:76`; `round-16-verifier-spotcheck.md` D3–D4 |

Cheapest wiring (two instruments that already exist, no new dependency):
1. **Seat-audit replay.** `census/round-16/transcripts/` now exists on disk with `MANIFEST.sha256` (144 entries = 65 w1 + 79 w2; `sha256sum -c` rc 0) but **is untracked** (`git ls-files -- census/round-16/transcripts` → 0). Commit it, add the two FP shapes to `--selftest`, and commit the replay `--json` for both waves.
2. **Count emission.** `tools/souji-landing-gate.py` already computes the carry count (`checked_markers` at `:578`, emitted in `--json` at `:621-623`); the missing piece is committing the pre-carry run's `--json` (D6) and quoting it. A one-line selftest pair (block count 29 vs quoted 28) makes the contradiction fail mechanically.

## 3. The one bounded move

**Admit Q27 and make the round's own record the fourth measured arm** — a single read-only “round-record consistency” run that (i) replays both transcript waves with the corrected classifier, (ii) resolves the `## Mistakes` pointers at the landing revision, and (iii) recounts the carry block, all from committed bytes and one committed `--json` pinned by sha256. This is the synthesis of the round's own proposals: C2 supplies the transcript manifest and replay, D6 supplies the pinning discipline, C3 supplies the durable-root fixture, and D3/D4 supply the two failure witnesses. It improves **calibration** (the judged axis) and **depth** (one grounded criterion) and does not touch runtime behavior, so **operability, coverage, freshness, adjacency are unchanged** — no harm. It does not add a knowledge entry or a frontier row, so it cannot inflate coverage.

Risks (stated, not smoothed):
- **Moving target.** `census/round-16/transcripts/` and the lane tools' jj edits appeared *during* this wave (worktree markers moved from 0 to 10/14/0 between two reads minutes apart). Bind every citation to `5fa6017` or to a committed digest; do not treat any worktree `jj_keep_unpushed` edit as evidence.
- **False-SAFE is not yet demonstrated in this lane.** The 6 keep-only commits are hidden predecessors, not absent worktree heads. The durable-root defect is real, but the lane's false-SAFE case needs a worktree registration whose head is keep-only; none was observed here. Do not write “false SAFE observed”.
- **Over-strict Q27(a).** Mistake pointers have many shapes (`path:line`, `rev:path`, ranges); resolve the *path* only, and accept the round's committed wave dir (148 tracked files at `.ufo/waves/round-16`).
- **Transcript text is untrusted seat output.** A replay reads it as data; no execution.
- **Repo bytes.** 144 transcripts ≈ 2.0 MB (`du -sb` = 2,005,183). State the cost where C2 is booked.
- **Reclassification side effect.** Moving the two prose calls to `V-WRITE-UNKNOWN` changes w2 minors (42 → 44) even though majors go 3 → 0. Declare the expected minor count or introduce a non-counting malformed class; do not report “0 findings” ambiguously.

## 4. Verdicts on the candidate rows

| candidate | verdict | basis |
|---|---|---|
| (1) D4 published without re-reading | **holds** | `seat-audit-w2.json` 3 majors; two are prose-split, one is the seat's own report path; transcript calls quoted above; report:47 restates the summary, the closure read the calls |
| (2) LOG 28 vs 29 | **holds** | LOG:902 and lesson:21 say 28; the lesson block has 29 bullets; report:14/:45 say 29 |
| (3) helper-era phantom deletions in `refs/jj/keep` | **holds (materially)** | 6 keep-only commits, 4 with `D` of both files; helper v1 cited; v2 guard exists; lane-side tools unchanged at HEAD |
| (4) empty fixture `.git` “committed” | **fails as stated** | never committed (48a64d8 tree has 2 p6repo blobs, no `.git`; `git log --all` empty); absent at read time (13:33); hazard proven only by trial + keep commits |

## 5. Exact commands and outputs (unrun checks are labelled)

```text
$ git -C <lane> log --diff-filter=A --format='%h %ad %s' -- tests/vault/vadv54-run/p/p6repo/one.txt
48a64d8 Sun Oct 18 15:09:36 2026 -0300 round-4 (amended): obsidian claim withdrawn by operator; ledger-verify tool installed (impl-20, d312263a), CLI findings banked

$ git -C <lane> show --stat 48a64d8 -- tests/vault/vadv54-run | tail -1
     29 files changed, 43 insertions(+)

$ git -C <lane> ls-tree -r 48a64d8 -- tests/vault/vadv54-run/p/p6repo
100644 blob 5fd8799…  tests/vault/vadv54-run/p/p6repo/inner/keep.txt
100644 blob 00508d3…  tests/vault/vadv54-run/p/p6repo/one.txt
$ git -C <lane> log --all --format='%h %s' -- 'tests/vault/vadv54-run/p/p6repo/.git'
(no output)
$ ls -la <lane>/tests/vault/vadv54-run/p/p6repo
drwxr-xr-x … inner
-rw-r--r-- … one.txt            # no .git; dir mtime Oct 20 13:33

$ git -C <lane> for-each-ref refs/jj/keep --format='%(refname) %(objectname:short)'   # 8 refs
$ for each: git rev-list --count <oid> --not --branches --tags --remotes             # 1 for 6 of them
$ git diff-tree --no-commit-id --name-status -r <oid>
D	tests/vault/vadv54-run/p/p6repo/inner/keep.txt
D	tests/vault/vadv54-run/p/p6repo/one.txt
# for 0254661, 1e0d8d1, 41ab059, 719154d

$ git -C <lane> show HEAD:tools/souji-vault-verify.sh | grep -n 'r17 note\|jj_keep_unpushed'   # (none)
$ git -C <lane> show HEAD:tools/souji-verify.sh | grep -c 'jj_keep_unpushed\|refs/jj'          # 0
$ git -C <lane> show HEAD:tools/souji-quarantine.sh | grep -c 'jj_keep_unpushed\|refs/jj'      # 0
$ git -C <lane> show HEAD:tools/souji-vault-verify.sh | sed -n '510,522p'
    if ! uniq=$(git -C "$owner" log --oneline "$head" --not --all 2>/dev/null | wc -l); then

$ sed -n '58,86p' <lane>/corpus/lessons/round-16.md | grep -c '^- `'
29

$ wc -l <lane>/census/round-16/transcripts/MANIFEST.sha256
144
$ (cd <lane>/census/round-16/transcripts && sha256sum -c MANIFEST.sha256); echo rc=$?
… w2/SentinelGateSafety.txt: OK
rc=0
$ git -C <lane> ls-files -- census/round-16/transcripts | wc -l
0                                   # on disk, not committed
$ ls census/round-16/transcripts/w1 | wc -l ; ls census/round-16/transcripts/w2 | wc -l
65
79                                  # 65 + 79 = 144; the assignment's “70 + 77” does not match
$ du -sb census/round-16/transcripts | cut -f1
2005183

$ jq '.summary' <lane>/census/round-16/seat-audit-w2.json
{"calls":4348,"major":3,"minor":42,"seats_audited":79,"seats_with_major":["ConnReadmeIndex","RerunGateReplayR14"]}
$ jq '.summary' <lane>/census/round-16/gate-landing.json
{"checked_markers":30,"checked_pins":16,"checked_reg":21,"checked_reports":141,"findings":0}
```

Transcript calls read at the exact lines quoted in R17-M1 (`:179`, `:224-225`). Not run by this seat: the seat-audit replay, the landing-gate replay, `bash -n`/`shellcheck` on changed bytes, and any `jj` invocation (forbidden). The replay verdicts above are the declared expectations to be measured by the C2 counting command, not observed here.

## 6. Tooling, cleanliness, probe posture

- Tool installs/upgrades: **none**. `pacman` untouched (host-wide pause). No network writes.
- Scratch: one transient check log (`/var/tmp/manifest-check.txt`) was written by the manifest verification and removed (`residue=0`). No other writes outside this report.
- Probe posture: reads/greps on exact named files; `git show|log|ls-tree|ls-files|rev-list|for-each-ref|merge-base|rev-parse` (read-only) on named repos/paths; `sha256sum`, `stat`, `ls -la` on a named directory. No recursive search over the lane, fleet, or a tree. No census/verify/vault/quarantine run. No `jj`.
