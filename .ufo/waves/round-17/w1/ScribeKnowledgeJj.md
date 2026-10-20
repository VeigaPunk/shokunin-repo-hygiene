STATUS: DONE — jj-colocation knowledge entry written as a candidate; sources opened, lane observations cited, nothing re-run.

# ScribeKnowledgeJj — round 17, wave 1 (C3(c))

## Behavior
Wrote `corpus/knowledge/jj-colocation-receipts.md` (new, `candidate — pending round-17 gate`). It covers: colocation default and import/export; detached HEAD (`@-` as [INFERENCE]); `refs/jj/keep/*` (observed; retention beyond "prevent GC" not documented); unbookmarked commits invisible to `--branches --not --remotes`; `--all` subtracting keep-ref heads (derived, [INFERENCE] with observed output); index ignored by jj; `snapshot.auto-track="none()"`; nested `.git` phantom deletions (observed only); helper commits naming both paths of a move; `measured_commit`=HEAD pins; untested git gc under jj; hooks/attributes not honored by jj writes.

## Gates
- Q1: `verified-at` names jj 0.45.1-7c41cdeb and git 2.56.0; host `git --version` = 2.56.0 (run). jj was not run (seat rule). `recheck:` line gives the commands.
- Q2: git and jj doc claims cite URL + ≤25-word quote; observations cite report file:line; helper claims cite `scripts/hyaku/jj-lane.sh:544-549, :618-619` (read, not executed). No committed fixture exists for the observations — flagged in Limits as a gate decision.
- Q3: three failure cases with locations (JjAuditSouji F1 :55-86, F3 :118-130; JjTrialSouji hazard 1 :76).
- Q4: recheck instructs `mktemp -d /var/tmp/...` plus trap; no /tmp, no live path.
- Q7: the operating rules repeat the pathspec and `-c maintenance.auto=false` guard.
- `## Source rows to number` lists 7 jj/git docs rows and 3 own-work rows, all `S0??`. The only `S0??` placeholders in the entry are in that list.

## Touched surfaces
- Created: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/jj-colocation-receipts.md`
- Created: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w1/ScribeKnowledgeJj.md` (this report)
- Not touched: SKILL.md, PROVINCE.md, tools, census, LOG.md, SOURCES.md, QUALITY.md (read only), any repository state, any git or jj write.

## Sources opened (2026-10-20)
- https://docs.jj-vcs.dev/latest/git-compatibility/ (requested jj-vcs.github.io host redirected to docs.jj-vcs.dev; page meta names docs.jj-vcs.dev as canonical)
- https://docs.jj-vcs.dev/latest/working-copy/
- https://docs.jj-vcs.dev/latest/bookmarks/
- https://docs.jj-vcs.dev/latest/config/ (grep of the full page for auto-track and colocate)
- https://docs.jj-vcs.dev/latest/git-comparison/
- https://docs.jj-vcs.dev/latest/technical/concurrency/
- https://git-scm.com/docs/git-rev-list (`--all`, `--branches`, `--tags`, `--remotes`, `--glob`; page last updated 2.56.0)
- Lane reports: JjAuditSouji.md, JjTrialSouji.md (read, line-cited)
- Existing knowledge entries for shape: git-grace-periods-and-expire-to.md, git-auto-maintenance-prunes-worktrees.md; corpus/QUALITY.md; corpus/SOURCES.md (row shape)
- `scripts/hyaku/jj-lane.sh` via grep on exact file (read only)

## Commands run
- `git --version` → `git version 2.56.0`
- `ls corpus/knowledge/` (listing only)
- No `jj` invocation. No git write. No test or fixture run.

## Tooling
No install or upgrade. Installed/updated: nothing. Host git 2.56.0 was already present.

## Out-of-scope items
- The census `unpushed` column stays branch-based; disclosed in the entry, not changed (per contract).
- The `--glob=refs/jj/keep/*` recipe is proposed, not landed. The round-17 executors own the tool change.
- The helper v2 behavior is claimed by the lane contract; the entry states that the source read matches it, and that the helper was not executed.

## Findings (advisory)
1. Keep-only heads make `log HEAD --not --all` vacuous, because `--all` includes the keep refs and HEAD. This is stronger than "keep refs are not durable roots". The entry marks the mechanism `[INFERENCE]` and cites the observed output (JjAuditSouji F3). L1 may want the gate to verify it with a /var/tmp fixture before admission.
2. Retention of hidden or abandoned predecessors under `refs/jj/keep/*` is not documented in the pages read; the entry states this as a limit. Do not promote it to a sourced claim without a jj source or doc row.
3. The nested-`.git` phantom-deletion behaviour is observed only (JjTrial hazard 1). The nearest documented analogue (submodules) is labelled as an analogue.
4. jj docs for colocation say "Git tools … can have trouble with conflicted files"; not relevant to the receipt surface, so left out.

## Verdict
Holds for coverage of C3(c). The entry is complete for the requested section list. Source-row numbering and the admission decision belong to L1 and the round-17 gate.

## Checks for the main agent to run (not run by this seat)
- `shellcheck`/`bash -n`: not applicable (knowledge entry, no script).
- Q2/Q4 re-check: `grep -c '/var/tmp' corpus/knowledge/jj-colocation-receipts.md` only if the gate requires it; the entry contains no `/tmp` path other than the `/var/tmp` scratch note.
- L1 to number the `S0??` rows in `## Source rows to number` and to resolve the `source:` front-matter line.
