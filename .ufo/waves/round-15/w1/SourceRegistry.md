# R15 w1 — SourceRegistry (registry census and next free IDs)

Seat: `SoujiR15.SourceRegistry` (scout, leaf). Axes: **calibration**, **operability**.
Certification remains OFF. Receipts remain advisory. Nothing here admits a row, grants a
verdict, or authorizes deletion.

## Evidence separation

- **Read (source inspection):** `corpus/SOURCES.md` — prose lines 3, 5, 7; `## Registry` line 9;
  table header line 11, separator line 12, rows lines 13–52; `## Paths` line 54;
  `## Search log` line 61; `## Leads (unopened)` line 72. Frozen contract
  `/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md` (kaika, 2026-10-19,
  frozen), found from the pointer at `corpus/SOURCES.md:3`; its location matches the one round-12
  planner recorded (`census/round-12/planner.md:10`). Shape, Rules 1–6, and Census block read.
- **Ran:** the contract's own Census block verbatim (read-only `grep`/`awk` counting over
  `corpus/SOURCES.md`) plus a `kind` histogram the block omits, and the same block's `used-by`
  existence check (`[ -e ]` on listed paths; no file contents read). These are counting
  commands over the assigned file, not tool-behavior probes and not a test of the census tool.
- **Disclosed out-of-slice touch (made before the parent's slice reminder; no finding below
  depends on it):** one bounded `grep -m6 '^source:'` over `corpus/knowledge/*.md` headers to
  sanity-check registry back-links, and a 42-line format-precedent read of
  `.ufo/waves/round-14/w1/GateRegistry.md` (lines 1–30 and tail 12). Neither informed any count,
  conclusion or proposed value here.
- **Boundary-contact disclosure (exact calls; not repeated after the reminder).** Three calls
  observed operator-sweep *names* without opening any file inside either sweep directory:
  1. `ls census` (inside a listing command) printed the two operator-sweep directory names; no
     entry was entered.
  2. `find /home/vgpnk/Projects -maxdepth 4 -name 'SOURCES-CONTRACT-v1.md'` descended to the
     `census/<round>` level, stat'd the sweep directory entry, and printed no path from inside.
  3. `find /home/vgpnk -maxdepth 6 -name 'SOURCES-CONTRACT*' -not -path '*/.omp/agent/*'
     -not -path '*operator-sweep*' -not -path '*/.cache/*'` — `-not -path` filters output, not
     traversal: `find` descended into `census/operator-sweep-20261019/`, stat'd entries one
     level inside, and emitted no sweep name.
  No file under either sweep directory was opened, read, copied, or content-queried; no content
  or filename from them appears in this report. All evidence came from `corpus/SOURCES.md` and
  the frozen contract.
- **Not opened:** `~/.omp/agent/agent.db*`, any credential/auth path, and every file under the
  operator-sweep directories. After the parent's boundary reminder all further access was
  confined to this report and explicit known paths.
- **Exercised evidence:** none. No fixture, selftest, census tool, shellcheck, or git
  subcommand was run.
- **Installs/upgrades:** none.

## 1. Exact census (contract command block, run from the lane root)

```
rows: 40
malformed: 0
tier: A=36 B=3 C=1
status: mined=23 queued=15 rejected=2
dupids: (empty)
enum: (empty — no kind/tier/status violations, no tier-inflation)
missing-usedby: (empty)
```

Added histograms (contract block has no `kind` command):

```
kind: docs=31 code=4 community=2 spec=1 book=1 own-work=1
opened: 2026-10-19=33 (S001–S033), 2026-10-20=7 (S034–S040)
recheck: on-release=30, 365d=6, 180d=2, 90d=1, on-change=1
used-by: 8 distinct real paths (5 knowledge `.md` + 3 lessons), 17 rows `—`
```

Status × kind: docs (mined 16, queued 14, rejected 1 = 31); code (mined 4); community
(queued 1 S014, rejected 1 S030); spec (mined 1); book (mined 1); own-work (mined 1 S031).
All counts are observed, not inferred.

## 2. Integrity beyond the contract census

- **Shape holds.** 40 rows, contiguous `S001`–`S040`, no gaps, no duplicates; every row has
  11 cells (AWK `NF=13`), so the table is machine-parseable and no cell smuggles a `|`.
- **status↔used-by invariant holds.** All 23 `mined` rows name at least one existing path; all
  17 `queued`/`rejected` rows are `—`. No mined row is `—`; no queued/rejected row cites a path.
- **Rejected format holds.** S030 and S032 read `REJECTED: <reason>; flip: <what would change it>`.
- **Supersession is by new row, not edited status.** Exactly three correction rows open
  `teaches` with `supersedes S0NN —`: S035→S005, S036→S006, S038→S034. The superseded rows keep
  their original status (S005/S006 `queued`, S034 `mined`) because contract rule 2 permits only
  `status`/`recheck`/`used-by` changes and defines no "superseded" status. Round 15 must not
  "fix" those statuses; that would be an append-only violation.
- **URL reuse is narrow and intentional.** 37 rows carry a URL, 34 distinct; the three repeated
  URLs are exactly the supersession pairs (git-repo, git, timeout). A new row may reuse a URL
  only with a distinct `scope` cell, and only a correction carries the `supersedes` prefix.
- **Anchor pinning is near-uniform.** Every row names a revision, version, tag, host version or
  access date. Weaker legacy cells: S024/S025 give only major.minor (`Coreutils 9.12`, host
  `9.11`) and S029 gives a year only (`online edition (2016)`). These satisfy "version or
  publication date" but are weaker than the examples; do not copy them in new rows.
- **`source` cell deviations (do not use as precedent).** The contract allows a repo path or
  command instead of URL/DOI only for `own-work`. S026 is `docs` with only an installed man-page
  path; S039 is `code` with only a repo path. Round-15 C1 rows are `docs`; each must carry its
  canonical `https://git-scm.com/docs/…` URL (or the pinned source URL).
- **`recheck` is a cadence, not a closed enum.** `on-change` (S039) and `365d` are observed and
  admissible; `on-release` is the norm for git docs.

## 3. Next free IDs (determinate without operator sweep)

- Maximum existing id is **S040**; the id rule is `S` + 3 digits, "the next unused; never
  reused". The strings `S041` and every `S0NN` ≥ S041 do **not** occur anywhere in
  `corpus/SOURCES.md` (checked over the table, `## Paths`, `## Search log`, `## Leads`).
- Therefore the next free id is **S041**, then S042, S043, … assigned in the order rows are
  finalized. Observed from the registry table alone; no operator-sweep path was read and none is
  needed to establish this.
- If the round-15 draft lands **N** new rows they occupy **S041–S040+N** with no gaps and no
  reuse. A correction takes the next id; it never reuses the id of the row it corrects.
- **Collision risk:** `census/round-15/sources-draft.md` is a proposal file, not the registry.
  Any "S041" written there is a proposed allocation. Only the integrator writing
  `corpus/SOURCES.md` assigns ids, and must re-run this census immediately before editing rather
  than trust numbers copied from the draft or from this report.

## 4. Coverage for C1 (operability)

Observed: the registry contains **no `git-config(1)` row** and **no `git-status(1)` row**; no
row's `source` or `scope` mentions git-config, includes, `hooksPath`, boolean value parsing, or
status porcelain/ignored semantics. Round-13's search log (line 67) records git-status as
"corroborating existing-source context, not new rows" — that is precedent that an opened
document need not become a row, not coverage.

Near-miss rows and why they do not cover C1 (observed from their `scope`/`teaches` cells):

| row | its scoped claim | why it does not cover Git config semantics |
|---|---|---|
| S006, S036 | `git(1)` optional-lock suppression only | `teaches` explicitly disclaims mandatory writes and object fetching; no config-key parsing |
| S033 | `gitrepository-layout(5)` `worktrees/<id>` lock and gitdir for lock/prune | its anchor mentions `config.worktree` at :395, but scope is lock/prune; round-12's negative search log excluded `config.worktree` as a pruning input, so using it for `extensions.worktreeConfig` would exceed the `scope` cell |
| S009 | tagged `gc.c`/`worktree.c`/`run-command.c`/`commit.c` maintenance execution | what auto-maintenance deletes, not how config values are resolved |
| S001–S004, S010, S011 | maintenance/gc/worktree/repack behavior | adjacent housekeeping, no config-include or hook semantics |

No row covers `core.hooksPath`, `include.path`/`includeIf.*`, `--no-includes`,
`core.attributesFile`, `core.excludesFile`, `core.alternateRefsCommand`, `filter.*`,
`remote.*.promisor`, `extensions.worktreeConfig`, or boolean parsing. Inference drawn from that
absence: S041+ are genuinely **new** primary rows, not re-scopes of existing rows, and each needs
its own round-15 Gate record (URL, access date, ≤25-word located quote) per contract rule 1.
A row may not be written from the repo's existing prose or from another seat's report.

## 5. Row-shape checklist for S041+

- 11 cells, one line per row, no `|` in any cell; `id` = S041… contiguously.
- `kind` from the enum: `docs` for git documentation, `code` for git/git source, `own-work`
  only for the lane's own re-runnable gate output; `community` is never tier A.
- `tier` scoped to `scope`, never global: A for official docs/source, B for secondary, C for
  leads only.
- `anchor` = exact section + revision (installed version/man page, commit/tag, or ISO access
  date). Never a bare homepage, and not a year alone.
- `teaches` one grounded learner benefit (observed rows run 17–39 words); a correction opens
  `supersedes S0NN —`; a rejection reads `REJECTED: …; flip: …`.
- `status` starts `queued` unless a same-round knowledge entry or lesson cites it; do not
  pre-mark `mined`, since `mined` requires a real `used-by` path.
- `opened` = `2026-10-20` (ISO); `recheck` = ISO date or cadence (`on-release` for git docs,
  `on-change` acceptable for a local-artifact assertion as in S039).
- `used-by` = `—` at creation unless a same-round entry cites it, then the exact repo-relative
  path.

## 6. Append-only and provenance obligations at integration

- Only `status`, `recheck` and `used-by` may change in place, each logged old→new in the
  round-15 lesson Gate (rule 2). `source`, `kind`, `tier`, `scope`, `anchor`, `teaches`, `opened`
  are immutable; a correction is a new row.
- Add a **Round-15 provenance** paragraph after line 7, following the round-13/round-14 pattern
  (naming which ids were opened on 2026-10-20 and where their quotes/access records live —
  expected `corpus/lessons/round-15.md` Gate). Do not rewrite the sentences at lines 3, 5, 7.
- Update `## Paths` only if a new row joins a study sequence. F1–F4 reference no config row, so
  a Git-config path, if added, needs its own ordered line and a stated reason for the order.
- `## Search log` needs one entry for the round-15 opening: question, where searched, date,
  identified/screened/included/excluded counts, exclusion reasons, stop rationale — including
  documents read only as corroboration.
- `## Leads (unopened)` must not absorb a row's topic: a lead is not evidence and never a row;
  opening a lead this round removes it from Leads.

## 7. Calibration and scorecard boundary

- Row count is not progress. Contract rule 4 counts expansion by **admitted knowledge entries**
  whose `source:` cites a `mined` row on uncovered coverage-map ground, not by registry rows.
  40 → 40+N rows must produce no score delta by itself; an uncited new row is `queued`, not
  expansion.
- The census above is shape evidence only. A green census does not admit a row, does not prove
  a quote, and must not stand in for the round-15 Gate.
- Next-id determination is bookkeeping, not preservation evidence; it must not be cited by the
  C2 admission checker in place of paired red/green evidence.

## 8. Residual unknowns

- The round-15 sources draft was not present at read time, so **N** (new-row count) is unknown.
  S041 remains the next free id under any N.
- `SOURCES-CONTRACT-v1` delegates admission to `corpus/QUALITY.md`, which was not read (out of
  slice); this report makes no admission claim and no tier judgment on unopened sources.
- Whether a proposed doc duplicates an existing row's exact `scope` can only be judged from the
  draft; current duplication risk is low because no config/status row exists, but each proposal
  must be checked against the S006/S036/S033 scope cells.
- The round-14 Gate quotes in `corpus/lessons/round-14.md` were not re-opened (out of slice);
  the file exists and the registry's `used-by` pointers pass the existence check.

## 9. Risks and blockers

- **ID collision across seats (risk).** Any other seat writing "S041" into a draft is proposing,
  not allocating. Only the `corpus/SOURCES.md` writer assigns, at merge time.
- **Shape regression (risk).** Copying S026/S039's path-only `source` or S029's year-only anchor
  would fail the contract's `source`/`anchor` requirements or weaken provenance.
- **Append-only violation (risk).** Rewriting a historical `teaches` (for example retagging S034
  as superseded) breaks rule 2; the correction row is the only mechanism.
- **No blocker.** Registry state and the next id are fully determinate from the assigned file.

Report: .ufo/waves/round-15/w1/SourceRegistry.md
