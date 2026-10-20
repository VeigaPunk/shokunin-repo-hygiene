STATUS: DONE — R2, R3, and R4 remain confirmed at b5763415cc67ecff1e8fe56c58c39a6fb106d7a3

Axis: calibration (7).

## Scope and pin

`git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` returned `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`. `git diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- LOG.md SKILL.md SCORECARD.md corpus/QUALITY.md census/round-17/live-fleet.json` produced no output; the checked working-tree sources match the pinned revision. The separately checked round-17 closure and lesson files are present at that revision and had no diff from it.

LSP was unavailable: `read xd://lsp` returned `No such tool: xd://lsp` and the mounted-device list had no LSP device. Therefore no LSP status, references, definitions, or diagnostics could be requested. I used direct source reads and exact-literal Git queries below; no grep result is presented as semantic proof. No tests or build checks were run; no tools were installed.

## Moderate — R2: missing replay-record citation (confirmed)

**Evidence:** `LOG.md:916` and `SKILL.md:163,165` cite `census/round-17/gate-replays-ddb7347.json`. The pinned tree has no such path. The requested history command, `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --all --oneline -- census/round-17/gate-replays-ddb7347.json`, returned no output. `git ls-tree -r --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- census/round-17/gate-replays-ddb7347.json` also returned no output; `git cat-file -e b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:census/round-17/gate-replays-ddb7347.json` returned `fatal: path 'census/round-17/gate-replays-ddb7347.json' does not exist in 'b5763415cc67ecff1e8fe56c58c39a6fb106d7a3'` (exit 128).

The alternative committed file is `census/round-17/gate-replays-4f48343.json`. Its `replays.r16-precarry` entry resolves `79bbe7a`, has `exit: 1`, `finding_count: 29`, `checked_markers: 30`, and `match: true`. This substantiates 29 uncarried findings among 30 markers for the 4f48343 replay; it does not substantiate a ddb7347-named record. The round-17 closure independently routes this correction at `corpus/lessons/round-17-verifier-spotcheck.md:150`.

**Verdict:** The R2 pointer defect remains. The count is supported by the committed 4f48343 replay, with the replay identity stated accurately.

**Exact append-only LOG correction text:**

```markdown
## 2026-10-20 — round 17 correction: r16-precarry replay pointer

Correction to the round-16 count correction above (LOG.md:916) and the r17 gate registry pointers (SKILL.md:163,165), found by the round-17 non-author closure (corpus/lessons/round-17-verifier-spotcheck.md:150, R2). `census/round-17/gate-replays-ddb7347.json` is not present at `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`: `git ls-tree -r --name-only` returns no path, `git cat-file -e` reports that the path does not exist, and `git log --all --oneline -- census/round-17/gate-replays-ddb7347.json` returns no commits. The committed record is `census/round-17/gate-replays-4f48343.json`; its `replays.r16-precarry` entry resolves `79bbe7a`, exits 1 with 29 findings and 30 checked markers, and has `match: true`. Thus the 29-of-30 count is supported by the 4f48343 replay, not by a ddb7347 record. The old ddb7347 path is withdrawn; the registry pointers at SKILL.md:163 and :165 should name `census/round-17/gate-replays-4f48343.json`.
```

**Smallest companion fix:** change the record token on `SKILL.md:163` and `SKILL.md:165` from `gate-replays-ddb7347.json` to `gate-replays-4f48343.json`.

## Low — R3: operability count includes the JSON header (confirmed)

**Evidence:** `SCORECARD.md:15` says `live fleet paired rows identical (22 repos)`. In `census/round-17/live-fleet.json`, both arms have a 22-element `rows` array; element 0 is the column header (`repo`, `worktrees`, `unpushed`, `dirty`, `scratch_bytes`, `mtime_iso`, `verdict_flags`), leaving 21 repository rows. The round-17 closure confirms this at `corpus/lessons/round-17-verifier-spotcheck.md:67`.

**Exact queries and outputs:**

- `read census/round-17/live-fleet.json?q=.arms%20%7C%20map%28.rows%20%7C%20length%29` → `[22,22]` (includes header).
- `read census/round-17/live-fleet.json?q=.arms%20%7C%20map%28.rows%20%7C%20length%20-%201%29` → `[21,21]` (repository rows).
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n '22 repos' b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- SCORECARD.md` → `SCORECARD.md:15: ... live fleet paired rows identical (22 repos) ...`.

**Verdict:** R3 remains a one-repository overcount in the SCORECARD prose; the paired live-fleet rows themselves agree.

**Exact smallest correction:** replace `live fleet paired rows identical (22 repos)` with `live fleet paired rows identical (21 repos)` in `SCORECARD.md:15`.

## Moderate — R4: Q7's raw-Git rule conflicts with the repo-kind commit route (confirmed)

**Evidence:** `corpus/QUALITY.md:31` Q7 applies the `git rev-parse`, named-path `git commit`, and `-c maintenance.auto=false` recipe to “Every lane or hygiene commit.” The rule at `corpus/QUALITY.md:11-14` explicitly requires supersession by a new row naming the replaced criterion, not rewriting Q7. In contrast, pinned `SKILL.md:127-130` selects the commit route by repository kind: jj-colocated repositories use the owning lane's helper, while only plain repositories use the raw-Git add/commit sequence. `corpus/lessons/round-17.md:16` (R17-M3) records the nested-`.git` phantom-deletion failure that motivates the distinction; existing Q28 at `corpus/QUALITY.md:72` supplies the r17 jj-receipts fixture and J6 plain-repo byte-identity control. The closure routes this at `corpus/lessons/round-17-verifier-spotcheck.md:152`.

**Verdict:** R4 remains. Q7's universal scope contradicts the repo-kind-specific contract. Preserve Q7 and add a new superseding criterion.

**Exact proposed row** (next ID, Q29, under a new Round 18 criteria table):

```markdown
| Q29 | Supersedes Q7's scope for jj-colocated repositories: Q7's raw-Git root check, named-path staging/commit, and `-c maintenance.auto=false` recipe applies only to plain Git repositories. A jj-colocated repository uses the owning lane's `scripts/hyaku/jj-lane.sh` commit helper with `--as <owner-id>` and explicit paths; never fall back to raw `git commit` under colocation. Q7 remains applicable to plain Git repositories. | commits | For a plain repository, retain Q7's root/pathspec/maintenance checks. For a jj-colocated commit, verify the owning-lane helper with `--as <owner-id>` and explicit paths; retain `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` J6 plain-repo byte-identity control. | corpus/lessons/round-17.md R17-M3 |
```

## Residual verification gaps

This was a source/evidence review only. LSP-backed semantic checks were unavailable, and no runtime tests were run. All three requested closure findings are nevertheless present in the pinned files and committed evidence cited above.