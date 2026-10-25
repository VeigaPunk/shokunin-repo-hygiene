STATUS: PASS

Seat: AuditSkillShonen (L1Souji22.AuditSkillShonen) — souji round 22, attempt 2, wave 1.
Scope: declared-evidence assertions in `SKILL.md` and `SHONEN.md`, frozen classes A/B/C,
plus the two item-specific checks (a printed command naming a nonexistent tool/evidence
path; a `[x]`/`[~]` box without a resolvable pointer).

Verdict in one line: **0 commands name a nonexistent tool/evidence path; all 4 promotion
boxes carry resolvable pointers; 1 frozen-class-A mismatch (`SKILL.md:37`), 0 class-B,
0 class-C mismatches, and 6 bounded findings (F1-F6).**

Read-only: neither file was edited. Only two files were written — this report and
`.ufo/waves/round-22/attempt2/w1/evidence/AuditSkillShonen.tsv` (121 lines: 1 header + 120
data rows; 11,078 B; sha256 `61366ac18635cc4df627ab0080e54462c84c98785aef50c887d25e5f763a94fd`,
taken after the final edit and quoted for byte identity). No tool was installed or
upgraded (no `uv`, `npm`, `cargo` or pacman transaction was run in this seat). No git/jj
write, no index touch, no cleanup action, no signal.

## 1. Audited revision and byte identity

    $ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 4edb25dfe262515d0da63224bbba71e02e36cba5
    commit
    $ git -C … ls-tree -r --name-only 4edb25dfe262515d0da63224bbba71e02e36cba5 | wc -l
    3545
    $ git -C … cat-file -s 4edb25d:SKILL.md ; cat-file -s 4edb25d:SHONEN.md
    54881
    863

Executed against the frozen base revision `4edb25d` (preregistration base), not against the
worktree. The worktree HEAD is `3216c1998fe04d7e23793ffd4e135bd37c3a11f4`; worktree state was
read only where noted, and it carries three modified `tests/vault/**` files and the new
`attempt2/assimilation/` directory that are not mine and were not audited.

`SKILL.md` = 390 lines, `SHONEN.md` = 12 lines. Worktree bytes equal revision bytes for both
(`sha256` rev vs worktree: `dc79dad96df9…` / `bb4babf93f58…`, equal=yes), so the audit covers
what an agent reads today and what `4edb25d` commits.

## 2. Method (frozen predicates, not redefined)

- **A** — every backticked span that is a repo-relative path ending `.py/.sh/.json/.tsv/.md/.txt`,
  with optional `:<line>` and optional `*`; glob expanded over `git ls-tree -r` at `4edb25d`.
  Checked with `git cat-file -e 4edb25d:<path>` and `git cat-file -s` (non-empty blob).
- **B** — every bare `[0-9a-f]{7,40}` token inside a markdown table cell (cells split on
  *unescaped* `|`; `SKILL.md:222` contains `\|`) whose cell also carries one of
  `commit|rev|revision|measured|at` or `census/round-<N>/`. Checked with
  `git cat-file -e <tok>^{commit}`.
- **C** — every 64-hex token in a cell containing exactly one backticked path, compared to
  `sha256(git cat-file blob 4edb25d:<path>)`. **Zero tokens satisfy the cell predicate**;
  the two 64-hex digests present sit in cells with no backticked path and were verified
  manually instead (§6 F3).
- Skipped tokens are recorded with their exclusion reason so N+S enumerates every candidate
  token the scan saw.

Environment gap: this seat has **no `lsp` device** (`read xd://lsp` → "No such tool"), so
caller/definition checks were done with `git grep`, `git cat-file` and text search over the
committed bytes. This is recorded as a limitation, not as semantic proof.

## 3. Frozen-enum result

    assertions=89 resolved=88 skipped=14 mismatches=1
    class A: 65 occurrences, 64 resolved, 1 mismatch
    class B: 24 occurrences, 24 resolved, 0 mismatch
    class C: 0 occurrences (0 candidates; see §6 F3)

Evidence file (written, then read back):

    $ head -2 .ufo/waves/round-22/attempt2/w1/evidence/AuditSkillShonen.tsv
    file	line	token	class	observed
    SKILL.md	13	SCORECARD.md	A	resolved@4edb25d blob=19812B

The only mismatch row:

    SKILL.md	37	launch-*.json	A	MISMATCH: glob expands over 0 tracked files at 4edb25d (token is a scratch-class pattern, not a claimed artifact)

All 24 class-B tokens resolve (`git cat-file -e <tok>^{commit}` rc=0 at `4edb25d`):
`4800fd7`(×9), `4f48343`(×3), `b576341`(×2), `5efb519`, `b410186`, `a31642d`, `cc21683`,
`6ff91f5`, `79bbe7a`, `5fa6017`, `8513d6ac`, `522dcd76`,
`41553adb139d06511dc386bb3ce4326aebfba675` (the `git show <commit>:path` pipe at `SKILL.md:222`).

## 4. Commands printed by SKILL.md — highest-order defect check

104 backticked command spans (`bash`, `python3`, `python3 -B`, `TMPDIR=… bash`, `git`, …).
They name **48 distinct repo artifact paths**: 12 under `tools/`, 26 under `tests/fixtures/`,
10 under `census/`. For each:

    $ git -C … cat-file -e 4edb25d:<path>      # rc=0 for all 48
    $ git -C … cat-file -s 4edb25d:<path>      # smallest 1033 B (tests/fixtures/r21-read-render-edges.py); 0 zero-byte blobs

**No printed command names a tool or evidence path that does not exist.** The only
non-resolving path-shaped tokens in command position are argument *placeholders*
(`<path>`, `<repo>`, `<rev>`, `<lane>`, `<owner-id>`, `<rel>`, `<qpath>`, `PATH`, `DIR`,
`REV`, `LANE`) and git ref patterns (`refs/jj`, `refs/heads/<b>`) — none is a named path.
The four placeholder *baseline artifacts* at `SKILL.md:216/217/219/220` are a bounded
operability issue, not this class: see F2.

## 5. SHONEN.md boxes

Four boxes, all `[~]`, none `[x]`, so no box claims an achieved state. Each carries a
resolvable pointer (all checked at `4edb25d`, content checked, not just existence):

| line | box | pointer resolution |
|---|---|---|
| 5-6 | SKILL.md contains decision tables, error patterns, checklists, cited sources | `SKILL.md` (54,881 B) has `## Decision tables`, `## Error patterns`, `## Checklists`, `## Gate registry`; `corpus/SOURCES.md` (79,306 B) has exactly one row each for S100/S101/S102/S103; `corpus/lessons/round-21.md` (26,647 B) has `## Gate` |
| 7-8 | one end-to-end domain task logged in LOG.md | `LOG.md` = 1467 lines; **line 362** = `## 2026-10-19 — operator sweep (execution): root-wide receipts + home-wide cache/tmp cleanup`; the claimed 96-artifact `pushed` removal is stated at lines 368-371 (`Removed — fleet root, receipt pushed (96 artifacts)`; `96/96 SAFE(pushed)`) |
| 9-10 | instructions executable without oral context | `census/round-21/run-acceptance.py` (35,326 B); `accepted-matrix.json` (3258 B) → `scenarios=3 replayed=3 summaries_equal=true`, every record `matched_command_count=18`; `remote-source-after.json` (505,583 B) → `expected_command_count=18 matched_command_count=18 all_matched=true` — the `3/3 sources, each18/18` claim is supported |
| 11-12 | no cross-domain bleed | `PROVINCE.md` (10,088 B) has `### Round21 privacy boundary`; `.ufo/waves/round-21/w1/ConnSiblingOverlap.md` (17,396 B) exists; `corpus/lessons/round-21.md` has `### Boundaries and teaching` |

**No `[x]`/`[~]` box lacks a resolvable pointer.** Observation (not a defect against the
pointer rule): the range `S100-S103` at line 6 includes S102, which `SKILL.md` does not cite
(`grep -o 'S[0-9]\{3\}' SKILL.md | sort -u` → S035 S036 S037 S040 S062 S064 S067 S068 S075
S076 S082 S086 S088 S100 S101 S103 S104 S105); S102 exists as a source row, so the pointer
resolves, but the range overstates what SKILL cites.

## 6. Defect list (bounded, by severity)

**F1 — MEDIUM (calibration): `SKILL.md:37` is the only frozen-class-A mismatch.**
Token: `` `launch-*.json` `` inside the `stale` receipt row ("scratch type as the tool
classifies: `.scratch/`, `*.out`, `*.log`, `launch-*.json`, `*-draft.*`"). Executed:
glob expansion over tracked files at `4edb25d` yields 0 hits. The token is a *classifier
pattern*, not an artifact claim, so this is a false positive of the frozen predicate, not a
false claim in the prose: `*.out`, `*.log` and `*-draft.*` escape class A only because those
extensions are not in the enum. A scanner implementing the frozen predicate verbatim (the
same predicate C1's counter uses) will report this as a mismatch.

**F2 — MEDIUM (operability): four printed commands carry their baseline artifact as a
bracketed placeholder, so the command cannot be executed as printed.** Verbatim:

    SKILL.md:216  python3 tests/fixtures/r21-read-root.py --tool tools/souji-seat-audit.py --base-tool <6ff3413-auditor-file>
    SKILL.md:217  bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base <6ff3413-proc-file>
    SKILL.md:219  python3 tests/fixtures/r21-replay-boundaries.py --tool census/round-21/run-acceptance.py --base-tool <8513d6ac-runner-file>
    SKILL.md:220  python3 tests/fixtures/r21-source-head.py --tool census/round-21/run-acceptance.py --base-tool <522dcd76-runner-file>

The prefixes resolve (`git cat-file -e 6ff3413^{commit}`, `8513d6ac^{commit}`,
`522dcd76^{commit}` → rc=0), and the artifact path is inferable from the sibling `--tool`
argument, so this is not the "nonexistent path" class. But only one extraction command is
committed: `git show 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh`
is the **only** `git show` in `corpus/README.md` (`git show 4edb25d:corpus/README.md |
grep -n "git show"` → 1 hit, line 344). No committed extraction recipe exists for the
auditor file or the two runner files. This weakens `SHONEN.md:9`'s claim in letter.

**F3 — MEDIUM (calibration): the two pinned SHA-256 claims cannot be bound by class C, yet
they are true.** `SKILL.md:216` and `:217` place the digest in a cell with **no** backticked
path (the path lives in the command cell), so class C cannot fire. Manual derivation:

    $ git cat-file blob 4edb25d:…  # via 6ff3413
    sha256(6ff3413:tools/souji-seat-audit.py)    = b2fa68e2e98dae9d046c11775737337fb99b0db94fb5042017e4c8a56fc83389   (matches)
    sha256(6ff3413:tools/souji-proc-census.sh)   = 37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64   (matches)

So the digests resolve; the *declaration* is unre-derivable from the cell alone. (The raw
cell text glues the label to the digest — `SHA25637c3316a…` — which a hex-run scanner must
split before it can even see the 64-char token.)

**F4 — LOW (calibration): an elided digest is recorded and verified but outside every class.**
`SKILL.md:222` states "live `tools/souji-evidence-cache.py` digest `dd279ba9…39d6`".
Executed: `sha256(4edb25d:tools/souji-evidence-cache.py)` =
`dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6` — matches both elided
ends. An elided 8+4 token is not 64-hex (class C) and its cell has no revision-context word
(class B), so it is counted as skipped, i.e. the strongest-looking pin on that row is
unclassifiable under the frozen enum.

**F5 — LOW/MEDIUM (durability): `SKILL.md:114`'s quarantine destination exists only as an
untracked empty directory — the stated quarantine has no committed receipt.**
Executed: `find .ufo/quarantine -type f | wc -l` → **0**; `-type d | wc -l` → 8;
`git ls-files .ufo/quarantine | wc -l` → **0** (and `git check-ignore` reports no ignore
rule). The prose "The r16 stub `tests/vault/vadv54-run/p/p6repo/.git` is quarantined at
`.ufo/quarantine/round-17/…/dot-git-empty-stub`" therefore holds for the working tree only,
while `SKILL.md:58` step 3 requires committing both paths. An empty `.git` stub directory
cannot be represented by a git commit, so this artifact class is outside the lane's
committed-receipt model; the prose should say so rather than imply a committed move.

**F6 — LOW (scope clarity): two prose revision tokens have no repo qualifier.**
`SKILL.md:230` labels `e20f4fa` "(fleet commit …)" (correct: lane rc=128, fleet-root rc=0),
but `SKILL.md:231`'s `a1b44b1` says only "already removed by a1b44b1" — in the lane repo
`git cat-file -e a1b44b1^{commit}` → rc=128, and it resolves only in
`/home/vgpnk/Projects/shokunin` (rc=0). Line 90's `b2f2efa` is correctly qualified
("fleet-root commits like"). Both are prose, so class B does not see them; a reader checking
in the lane repo gets a false alarm.

Not defects (checked and cleared): `.ufo/state/`, `.ufo/watchdog.log` and `scripts/` at
`SKILL.md:69-70` are fleet-root-relative and all three exist there; the tool/symbol pointers
`s18_evaluate_worktree_one` and `jj_keep_novel` exist in the three named receipt tools
(`git grep -c` at `4edb25d` → 2/2/4 and 2/3/7 hits).

## 7. Axes

- calibration: 88/89 frozen-enum assertions resolve; the one mismatch is a predicate
  over-capture (F1) and the two digests (F3) are true but unbound. No axis harmed.
- operability: every printed tool/fixture path exists and is non-empty; four baseline
  placeholders (F2) are the only print-and-run gap.
- coverage: 89 enum assertions + 14 recorded skips + 48 command paths + 17 pointer tokens
  enumerated; nothing narrowed.

## 8. Residual risk and verification gaps

- Single revision. Everything is measured at `4edb25d`. Worktree-only declarations were not
  audited, except F5, where the worktree is the only place the claim can be checked.
- Existence is not semantics. "Path exists" says nothing about whether the artifact supports
  the claim in its cell. Only five content claims were spot-verified: the two
  pinned base-tool digests (F3), the elided evidence-cache digest (F4), and the two r21
  matrices (`3/3` and `18/18`).
- No printed command was executed; this audit is read-only and does not claim any gate runs.
- Prose revision tokens are outside class B by the frozen cell predicate; the five prose
  tokens (b410186 ×2, b2f2efa, e20f4fa, a1b44b1) were resolved manually (`b410186` lane
  rc=0; the fleet tokens in the fleet repo only).
- Two genuine revision pins are excluded by the frozen context-word rule and recorded as
  skips, not mismatches: `5fa6017` at `SKILL.md:194` and the 40-hex baseline
  `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` at `SKILL.md:214` (`--baseline` is not in the
  keyword list). Both resolve rc=0. If the C1 scanner shares this predicate it under-counts
  the same way.
- No `lsp` server is mounted in this seat, so no semantic caller/definition proof exists for
  the symbol pointers; those checks are text/`git grep` level.
- Tool inventory: no installs, no upgrades, nothing recorded because nothing changed.
