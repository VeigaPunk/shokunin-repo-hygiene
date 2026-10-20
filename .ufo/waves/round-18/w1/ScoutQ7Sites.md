STATUS: DONE — R4 sweep at b576341: two in-scope prescriptive sites (QUALITY Q7; the auto-maintenance knowledge "Lane link"), both narrowable to plain repos; no other raw `git commit`/`git add` prescription in the five scopes.

# R4 sweep — places prescribing raw `git commit`/`git add` for lane or jj-colocated commits

Seat: SoujiR18.ScoutQ7Sites-5 (leaf, calibration axis). Read-only prose sweep at
`b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (short `b576341`; `git rev-parse --short HEAD` → `b576341`).

Lane colocation is observed, not assumed: `stat -c '%F %n' .jj .git` → `directory .jj` / `directory .git`.
So the lane's own commits are in scope of the jj-colocated rule.

Scopes swept whole: `corpus/QUALITY.md`, `SKILL.md`, `PROVINCE.md`, `corpus/README.md`,
`corpus/knowledge/*.md` (5 files).

## F1 — HIT (prescriptive): `corpus/QUALITY.md:31` (Q7)

Verbatim (line body; table row):

> | Q7 | Every lane or hygiene commit: (a) runs `git -C <repo> rev-parse --show-toplevel` and confirms the intended repo first; (b) stages only named paths (`commit -- <paths>`), never `add -A` or `.`; (c) runs with `-c maintenance.auto=false` so git's own pruning cannot ride along. | commits | the commit command recorded in LOG names its pathspec and the `-c` guard; `git show --stat --format= <hash>` lists only approved paths | LOG.md:381 (`git add -A` swept live outputs into e20f4fa); round-12 M51 (auto-maintenance prunes worktree metadata on commit); round-12 M53 (silent `cd` failure committed in the fleet root) |

Conflict, three ways:
1. The criterion binds "Every lane or hygiene commit". The lane itself is `.jj`-colocated
   (above), and `SKILL.md:129` says the opposite for that case: "a refusal … is a stop,
   never a git fallback, never a raw `git commit` under colocation". `SKILL.md:128` routes
   the lane's commit through `jj-lane.sh commit <lane> --as souji -m … -- <paths>`.
2. Clause (c) forces the raw-git reading even though the row never spells the `git` prefix:
   `-c maintenance.auto=false` is a git-commit flag. The helper invocation cannot carry it,
   and the helper does not add it either (`grep -n 'maintenance.auto' scripts/hyaku/jj-lane.sh`
   → no match). So Q7's own test — "the commit command recorded in LOG names its pathspec
   and the `-c` guard" — is unsatisfiable for a colocated lane commit.
3. (b)'s "stages only named paths" is the `git add` half of the plain-repo recipe
   (`SKILL.md:130`), while under colocation `corpus/knowledge/jj-colocation-receipts.md:99`
   says "No `git add` before a jj call (§5)"; `:52` records that
   `git add -- <paths> && git commit -- <paths>` "cannot coexist with interleaved jj calls".

Already routed by the admitted outside closure, and this sweep agrees with it:
`corpus/lessons/round-17-verifier-spotcheck.md:152` ("`corpus/QUALITY.md` Q7 still prescribes
`commit -- <paths>` with `-c maintenance.auto=false` for 'every lane or hygiene commit' …
Narrow Q7 to plain repos") and `:106` ("The knowledge entry §5 agrees. `QUALITY.md` Q7 still
says every lane commit uses `commit -- <paths>` (R4).").

### Narrowable? YES — clause by clause

- (a) `git -C <repo> rev-parse --show-toplevel`: keep **universal**. The right-repo check
  applies to both routes (`SKILL.md:126` keeps it above the route split); the helper also
  needs the correct repo. Nothing here is raw-git-specific.
- (b) split in two. "never `add -A` or `.`" is **universal** (`SKILL.md:127` repeats it for
  both routes). "stages only named paths (`commit -- <paths>`)" is **plain-repo mechanics**;
  the colocated analogue is the helper's exact `-- <paths>` (`SKILL.md:129`) plus the
  no-`git add`-before-jj rule (`jj-colocation-receipts.md:99`).
- (c) `-c maintenance.auto=false`: **plain-repo only**. It is a raw git flag; the helper is
  fleet-owned and carries no such token, so a colocated commit can neither pass nor record it.
- test column: split by repo kind. Plain repo: recorded command names its pathspec and the
  `-c` guard (unchanged). Repo with `.jj`: recorded helper call cites the helper's
  `landed <hash>` line (`SKILL.md:129`), with no `-c` requirement.
- lesson column: **unchanged**. All three lessons survive for plain repos, and M51's ground
  truth is itself about plain git — `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:8`
  says "A successful `git commit` …" and `SKILL.md:91` already qualifies it as "a plain
  `git commit`".

### Smallest fix (advisory; R4 owner is the executor seat, not this scout)

`corpus/QUALITY.md:11-13` fixes the form: "a criterion is superseded by a new row that names
the row it replaces, never rewritten." Append one row after Q28, leaving Q7 byte-identical:

> | Q29 | Supersedes Q7's (b)/(c) and its test for jj-colocated repositories; (a) and the never-`add -A`/`.` rule stay universal. A lane or hygiene commit in a repo with `.jj` is made only through that lane's helper naming exact paths (`SKILL.md:128-129`); `git add` is not run before a jj call and the helper is fleet-owned, so no `-c maintenance.auto=false` is required of or recorded for it. A plain repo (no `.jj`) still uses named `git add` then `-c maintenance.auto=false commit -- <paths>` (`SKILL.md:130`). | commits | a colocated commit record names the helper call and its `landed <hash>`; a plain-repo commit record names its pathspec and the `-c` guard; `git show --stat --format= <hash>` lists only approved paths | LOG.md:381; round-12 M51, M53; R4 in corpus/lessons/round-17-verifier-spotcheck.md |

Rationale for striking Q7's test for `.jj`: it cannot be satisfied there by any compliant
commit, so a landing check that enforced it would either fail every colocated round or
silently exempt the lane — both are calibration losses.

## F2 — HIT (prescriptive in form, descriptive in intent): `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:22`

Verbatim (whole line):

> SKILL removal-flow step 3 makes quarantine a normal owning-repo commit (`SKILL.md:40-47`); its Pre-quarantine checklist already guards the scoped commit with `git -C <repo> -c maintenance.auto=false commit -- <approved paths>` and pins registrations with `git worktree lock --reason` (`SKILL.md:94-100`). …

Conflict: it asserts, without a repo-kind qualifier, that "the scoped commit" is guarded by
the raw `git -C <repo> -c maintenance.auto=false commit` form. After `SKILL.md:127-130` that
is true only of the plain-repo branch (`:130`); a repo with `.jj` uses the owning lane's
helper (`:129`), which takes no `-c` flag.

Also stale, same line (adjacent calibration defect, Q2 class): the two cited ranges no longer
hold the cited content. At b576341, `SKILL.md:40-47` is the receipt taxonomy / classify table
(step 3 of the removal flow is `SKILL.md:58`), and `SKILL.md:94-100` falls inside the
"Git deletes without a receipt" bullet (starts `:91`) and the following "Unbounded staging"
bullet (starts `:98`), not the checklist (the Pre-quarantine checklist is `SKILL.md:122-132`).

Narrowable? YES. Rewrite the clause as: "its Pre-quarantine checklist guards a **plain-repo**
commit with `git -C <repo> -c maintenance.auto=false commit -- <approved paths>`
(`SKILL.md:130`); a jj-colocated repo commits through the owning lane's helper
(`SKILL.md:129`) and carries no `-c` flag", and repoint both line references
(step 3 → `:58`; checklist → `:122-132`). Severity is lower than F1: it reports how the
checklist works rather than instructing the lane to run the command, but it is the same
un-narrowed raw-git claim and lives inside an admitted knowledge entry.

## Non-hits, scanned and cleared (no prescription of raw git for lane/colocated commits)

| site | text | why not a hit |
|---|---|---|
| `SKILL.md:91` | "a plain `git commit` spawns `git maintenance run --auto`" | descriptive hazard note; already says "plain", i.e. already narrow |
| `SKILL.md:127` | "never `git add -A` / `.`" | prohibition, universal; no raw-commit instruction |
| `SKILL.md:128` | lane route: `jj-lane.sh commit <lane> --as souji … -- <paths>` | the superseding authority itself |
| `SKILL.md:129` | "never a raw `git commit` under colocation" | explicit prohibition; agrees with the fix |
| `SKILL.md:130` | plain repo: `git add -- <rel> <qpath>` then `-c maintenance.auto=false commit -- <rel> <qpath>` | already scoped "plain repo (no `.jj`)" |
| `SKILL.md:58` | "commit BOTH paths … by the Pre-quarantine commit route" | route-neutral by reference |
| `corpus/knowledge/jj-colocation-receipts.md:50-52` | observations: `git add` + `jj commit`/`jj describe` interactions; the raw pair "cannot coexist" | failure evidence against raw git, not a prescription |
| `corpus/knowledge/jj-colocation-receipts.md:99` | "No `git add` before a jj call (§5)" | prohibition; consistent with the helper route |
| `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:8` | "A successful `git commit` can trigger worktree-prune …" | mechanism claim, not a lane instruction |
| `corpus/README.md:210` | landing condition: section lands "only in the same commit as …" | co-landing requirement; route-neutral |
| `corpus/README.md:217-222` | colocation disclosure; `git rev-list`/`for-each-ref` reads | read-only measurements, no commit route |
| `PROVINCE.md:27,29` | "git index is not a signal"; "plain git repo" definition | descriptive |
| `PROVINCE.md:118-120` | "commits stay operator/helper-owned" | consistent with the helper route; no command |
| `corpus/QUALITY.md:72` (Q28) | applies-to includes "lane commits under jj colocation"; exact-file-path rule only | helper-compatible; precedent for a repo-kind-scoped row |
| `corpus/QUALITY.md:37,41,64` (Q13/Q17/Q25) | `git show`, committed-file resolution, landing checks | read-only/lifecycle checks; no commit/add recipe |

`corpus/README.md` and `PROVINCE.md` contain no `git add` / `git commit` invocation anywhere
(`grep -n 'git ' corpus/README.md PROVINCE.md` listed only read-only commands, `git mv`,
`worktree prune`, and prose).

## Adjacent observations for L1 (not R4 hits, no fix proposed)

- `LOG.md:496,652,676,766,814` record raw `git -c maintenance.auto=false commit -- <same
  named paths>` for r12/r14/r15 lane work. These are historical records in rounds that
  predate the r17 helper route, not prescriptions; no edit is implied.
- `grep -n 'jj-lane' LOG.md` → no matches. The LOG carries no helper-commit record, so Q7's
  test ("the commit command recorded in LOG names … the `-c` guard") has no colocated
  instance that could pass, which is additional evidence beyond the prose contradiction.
- Q28 (`corpus/QUALITY.md:72`) already demonstrates the accepted shape for scoping by repo
  kind inside one row's applies-to column; Q29 as drafted uses the same shape.

## Commands run (exact, with the decisive outputs)

```
git -C … rev-parse --short HEAD                         → b576341
stat -c '%F %n' .jj .git                                → directory .jj / directory .git
grep -rnE 'git add|git commit|commit -a|add -A|git stage|git -C [^ ]+ add' \
  PROVINCE.md SKILL.md corpus/README.md corpus/QUALITY.md corpus/knowledge/*.md
  → SKILL.md:91,127,129,130; corpus/QUALITY.md:31;
    corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:8,22;
    corpus/knowledge/jj-colocation-receipts.md:50,51,52,99   (no PROVINCE/README hits)
grep -n 'commit' PROVINCE.md corpus/README.md corpus/QUALITY.md
  → PROVINCE/README: descriptive only; QUALITY: Q7 at :31, lifecycle rows elsewhere
grep -n '^| Q' corpus/QUALITY.md | cut -c1-60            → Q1..Q28 (Q7 at line 31, Q28 last)
grep -n 'maintenance.auto\|git commit\|git -C' scripts/hyaku/jj-lane.sh
  → no maintenance.auto match; line 4 "Replaces git commit/push for shokunin lane repos"
grep -n 'Q7' corpus/lessons/*.md SKILL.md PROVINCE.md corpus/README.md
  → corpus/lessons/round-17-verifier-spotcheck.md:106,152; round-12.md:41,104,113,115
grep -n 'jj-lane\|landed [0-9a-f]\{7\}\|helper commit' LOG.md → no matches
```

All commands were read-only grep/stat/read on named files; no probe, no fixture, no jj, no git
write. No tool installs.

## Verdict

R4 **holds** as routed: exactly one in-scope *prescription* (`corpus/QUALITY.md:31` Q7)
plus one un-narrowed restatement inside an admitted knowledge entry
(`corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:22`). Both are **narrowable to
plain repos** without weakening the three lessons that ground them. Smallest fix: a
superseding Q29 naming Q7 (quality file's own supersession rule), and a plain-repo qualifier
plus re-pointed SKILL line refs in the knowledge sentence.

## Remaining unknowns

- Whether a helper-driven `jj commit` can trip git auto-maintenance through jj's git backend
  (push/fetch paths) was not measured and is outside R4's prose question; the helper carries
  no `maintenance.auto` token, so Q7(c) is at least not recorded for it.
- LOG does not name the command that landed r17's `ddb7347`/`4f48343`, so Q7's compliance in
  the colocated regime cannot be reconstructed from LOG alone.
