# R41connector01 — sibling-overlap scan (read-only)

Seat: connector (leaf, no dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, freeze `e2a74312af4233963e44e4dbb38838ece07b8bd2`.
Scope: classify the three new round-41 surfaces against souji's `PROVINCE.md` (Owns / Refuses / Adjacency / Adjacent) and grep sibling lanes read-only for overlap.
Nothing was edited, committed, or scored. Scratch dir `/fast/scratch/hyaku/souji-r41/R41connector01` was created empty and removed (`rm -rf`, observed `scratch-removed`).

## 0. What exists to classify

The three surfaces are not committed at the freeze commit. Candidates sit in other seats' wave dirs:

| Surface | Committed at e2a7431? | Candidate paths (sha256, full) |
|---|---|---|
| C2 `tools/souji-freeze-check.py` | no | `.ufo/waves/round-41/w1/R41executor07/souji-freeze-check.py` `3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b` (215 lines); `R41executor08/` `9cc2f0eee1a60fc004d1ee0abfb1c9885daf0c5f4487267a0864ea57d22ff0c0` (230); `R41executor09/` `e0bec95b77a08c7cab1d45a7c4d4d1fa7f1f15e5191d95bdde15fbe39661f7ba` (233) |
| C3 `tests/fixtures/r41-refusal-sites.py` | no | `R41executor01/` `8bf040106df7efdb20673dc39d1f60565163ff9415a5ad3e5e7c0f3153770167` (215); `R41executor02/` `bf403b2b5a75b72030847d44cdbc0fde3a7e2afff7f8d255c35cbbb7657b72c9` (287); `R41executor03/` `1020e5f28eb34af728a31f5b4e2cc1dc003b274f18cb53c505c12593913e3ed9` (299); `R41executor04/` `f32022e28fe2293af44d7fee1cb73f9a39221fbcc534022b78d77a8c96551978` (91); `R41executor05/` `841d8562e40972669a25d15adff280f6ed591e471a027d36f8b480edd7f390da` (360); `R41executor06/` `86659db9b037e5864dff0b7dcefe64b3bc600295fd36c98c9afbfa3c1490b966` (306) |
| R1 (not a claim) `tests/fixtures/r41-drift-record-order.py` | no | `R41executor13/` `a2880a91410611c7ed8bd6c472957f88745e3c61d9044e1ba3ff53386a47d234` (170) |
| C1 CORRECTION lines in `corpus/lessons/round-41.md` | no | none found |

Commands and output:

```
$ git -C .../souji-shokunin cat-file -e e2a74312af4233963e44e4dbb38838ece07b8bd2:corpus/lessons/round-41.md
fatal: path 'corpus/lessons/round-41.md' does not exist in 'e2a74312af4233963e44e4dbb38838ece07b8bd2'
$ grep -rIn 'CORRECTION' .ufo/waves/round-41        -> (no output)
$ find .ufo/waves/round-41 -path '*round-41*' \( -name 'souji-freeze-check.py' -o -name 'r41-refusal-sites.py' -o -name 'r41-drift-record-order.py' \)
  -> 10 paths (listed above)
```

Note: the `tools/`, `tests/fixtures/` and `corpus/lessons/` paths named in the spec do not exist yet. The overlap findings below are judged on the candidates and on the frozen preregistration grammar, not on landed bytes.

## 1. Province check (PROVINCE.md)

- **Adjacency** (`PROVINCE.md:50-57`): mori (health/liveness), tsukuroi (host repair), kagi (credentials). Adjacent (report, don't absorb): kumitate (`:80-81`, task-worktree locks), chousa (`:82-83`, research method and source hierarchy), credential-bearing history to kagi (`:84-86`).
- **Refuses** (`:32-47`): history rewrite, credentials, operator config, dirty/unpushed artifacts, live work products, signalling unrelated processes.
- The drift tool's refusal classes are souji's own Owns: "dead worktree *metadata* (`git worktree prune` …)" (`:11-12`). The round-39 boundary note (`PROVINCE.md:276-289`) already fixed the drift tool's record-class contract as souji's.

## 2. Surface verdicts

### C2 — `tools/souji-freeze-check.py` (preregistration freeze checker)

Verdict: **stays in souji's province; two overlaps to route, one adjacency to name. No sibling reads a souji preregistration.**

- Reads only souji's own preregistration grammar (`## C<n>` blocks, `Base/Counter/Population/Control/Target/Kill`), with `census/round-40/preregistration.txt` as retro input. Province fit: Owns "Dry-run censuses"/gates over own evidence (`PROVINCE.md:17`), and round-14 boundary wording that local checks "serve souji's own evidence fragments" (`:101-105`).
- **Overlap 1 — kumitate dispatch-marker rule (route to L1).** Candidate C0 finding `DISPATCH-BEFORE-FREEZE` re-derives the marker definition in `kumitate-shokunin/scripts/plan-before-ready.sh:12-13` ("oldest commit that ADDS a top-level `.ufo/waves/round-R/*.ready`, fallback `*-dispatch.json`"). Kumitate owns dispatch and wave markers; `plan-before-ready` is referenced in 13 kumitate files (`grep -rIl -F plan-before-ready kumitate-shokunin` excluding `.ufo/.git/.jj`). Recommendation: keep the check (it is souji's freeze rule) but cite kumitate's marker definition in the freeze-check docstring rather than forking the rule.
- **Overlap 2 — same-name "freeze-check" family across the fleet (name only, different surface).**
  - `kasegi-shokunin/corpus/instruments/freeze-check.py` (394 lines): replays each claim's `counter_cmd` at a base tree, FC-* finding ids, `--selftest` cases=27; SKILL.md:1153. Different input (claims-v2 JSON, not a prereg). Not a duplicate; it is prior art for the replay-at-base idea that C2's grammar does not do.
  - `mori-shokunin/tools/mori-freeze-order.py`: "Check whether frozen claim inputs predate their implementation commits" (mori SKILL row r18 freeze-order). Overlaps the freeze-before-data concept of `DISPATCH-BEFORE-FREEZE`. Mori's PROVINCE owns watchdog/liveness/settlement reads, not preregistration grammar, so this is a concept overlap only.
  - `kengaku-shokunin` evidence logs (27 files) cite a `freeze-check --double-read` command (e.g. `corpus/evidence/attrib-r22-opencode-trials.log:8,46,71`). No definition found under kengaku `tools/` or `scripts/` (`grep -rIl -E 'def .*freeze|freeze-check\b' kengaku-shokunin/tools kengaku-shokunin/scripts` → no output). Home of that command unknown; not located.
  - Recommendation: the name `freeze-check` is now used by at least three lanes. Consider the souji-prefixed name (already used: `souji-freeze-check.py`) and do not add a fourth generic name.
- **Adjacency:** none of the candidates reads `kumitate` round-gate or `tabi` `check-round-contract.mjs`; grep for `preregistration|freeze` in those files returned only the `plan-before-ready.sh` lines (`:37,45,139,261,467,637`).

### C3 — `tests/fixtures/r41-refusal-sites.py` (refusal-site battery for `tools/souji-worktree-drift.py`)

Verdict: **stays in souji's province; no sibling overlap in code or record grammar.**

- Subject tool is souji's: `tools/souji-worktree-drift.py` (docstring `REPO<TAB>name<TAB>regs=N<TAB>prunable=N` / `TOTAL<TAB>...` grammar, lines 24-25, 88-89), documented in `PROVINCE.md:276-289` (round 39) and on the Owns line for dead worktree metadata.
- Record grammar producers: zero in sibling lanes. Commands and output: `grep -rIl -F 'REPO\tregs=' <sibling>` over all `*-shokunin` lanes (excluding `.git`, `.jj`, `.ufo`) and fleet-root top-level files → **0 files** (`fleet-root-top files=0`, no sibling lines printed). `grep -rIl -E 'TOTAL repos=|RECORD-MALFORMED|RECORD-OUTSIDE-ROOT|JSON-NOT-REGULAR'` across siblings and fleet root → only souji `.ufo/reports` and `MANIFEST.json` hits.
- Adjacency (lock semantics): `souji-worktree-drift.py` contains 12 lines matching `lock`. Kumitate owns live task-worktree locks (`PROVINCE.md:80-81`). Kumitate's isolation note `kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:16` cross-references souji's `git-auto-maintenance-prunes-worktrees.md` as "linked worktrees pruned by maintenance, which this entry does not…". Read-only cross-reference; no code overlap. The C3 battery probes refusal classes only and does not test lock behaviour, so the adjacency is documented, not claimed.
- `tameshi-shokunin/plans/round-7-record-draft.md:188` contains prose "worktree-drift immunity" only; no tool.

### C1 — CORRECTION lines in `corpus/lessons/round-41.md` and tier-A row for git v2.56.0 `worktree.c`

Verdict: **stays in souji's province (its own lessons and SOURCES admission); route the source-hierarchy method to chousa as already stated in PROVINCE.md:82-83.** Two in-lane issues to flag.

- Basis confirmed: `git show e2a7431:corpus/lessons/round-40.md` contains "`worktree.c` appears in 9 rows" at line 49 (grep output `49: … (worktree.c appears in 9 rows of`). This is the I1 statement C1 corrects.
- Source-table state: `corpus/SOURCES.md` max row is `S257` (`grep -o '^| S[0-9]*' … | sort -V | tail -1` → `| S257`); zero existing `| S258 ` rows, so `S258` is the next free id within souji's table.
- **In-lane overlap (flag):** `corpus/SOURCES.md` already has 9 lines mentioning `worktree.c`; the closest is `S009` (git/git v2.55.0 `builtin/gc.c, worktree.c, run-command.c, builtin/commit.c`, `SOURCES.md:38`). A v2.56.0 `worktree.c` row would be a second code-tier row on the same file under a different tag. The r40 precedent (S251 duplicate-url warning, `SOURCES.md` round-40 provenance) shows the census tolerates this as a warning, not a finding; L1 should state the scope difference in the row's `scope` cell.
- **Cross-lane id note:** `S258` also appears in sibling lanes as their own ids: `kumitate-shokunin/.ufo/waves/round-59/build/.../staged-ids:134` and `chousa-shokunin/.ufo/waves/round-45/w1/ConnectSiblings.md:22` (kotodama's `SOURCES.md` list). Lane-local ids; no collision inside souji, but any cross-lane citation must carry the lane prefix.
- Method adjacency: `PROVINCE.md:82-83` says chousa owns the method; souji's SOURCES "applies it and does not restate it". The new row must follow `SOURCES-CONTRACT-v1` (cited in `SOURCES.md:3`), not a chousa restatement.

### R1 (not a claim) — `tests/fixtures/r41-drift-record-order.py`
Stays in souji (same tool as C3). No sibling overlap found.

## 3. Counts (commands run, read-only)

Excluded `.git`, `.jj`, and `.ufo` in the count loops unless stated.

| Term | Sibling lanes with hits (file counts) | Verdict |
|---|---|---|
| `freeze-check` | kake 1, kasegi 10, kengaku 27 (logs), kotodama 1, lore 1, mori 1 | name family, see §2 C2 |
| `worktree-drift` | tameshi 1 (prose) | none |
| `plan-before-ready` | kumitate 13 | route (C2 overlap 1) |
| `DISPATCH-BEFORE-FREEZE` | 0 (outside round-41) | candidate-only |
| `REPO\tregs=` record grammar | 0 | none |
| `git-auto-maintenance-prunes` | kumitate 1 | adjacency, read-only |
| `r41-refusal-sites` | 0 (outside `.ufo/waves/round-41`) | candidate-only |

Command shape (one per term): `for d in *-shokunin; do grep -rIl --exclude-dir=.git --exclude-dir=.jj --exclude-dir=.ufo -F -e "$t" "$d" | wc -l; done`. Single-hit checks by `grep -rIn -F` listed in §2.

## 4. Verdict

- C2 (`souji-freeze-check.py`): stays in souji; route the dispatch-marker definition to kumitate (cite, don't fork), and avoid a fourth generic `freeze-check` name in the fleet.
- C3 (`r41-refusal-sites.py`): stays in souji; no overlap in code or grammar; lock-semantics adjacency to kumitate is documented only.
- C1 (CORRECTION lines and tier-A row): stays in souji; flag the `worktree.c` scope overlap with existing `S009` and the lane-local `S258` id for L1.
- No sibling owns any of the three surfaces. Two overlaps need a decision by L1 (C2 marker rule; C1 row scope). Nothing here changes a frozen counter or population.

Verification not run by this seat: no candidate was scored (`score-candidate.sh` is out of scope for connector); no tool installs; no git or jj mutation in any repo.

## 5. Evidence pointers

- `PROVINCE.md:11-12, 17, 32-47, 50-57, 80-86, 101-105, 276-289`
- `census/round-41/preregistration.txt` C2/C3/C1 blocks (frozen)
- `census/round-41/c2-counter.py` grammar (lines 1-30, class list)
- `kumitate-shokunin/scripts/plan-before-ready.sh:3,12-13,37,45,139,261,467,637`
- `kasegi-shokunin/corpus/instruments/freeze-check.py:1-30`; `kasegi-shokunin/SKILL.md:1153`
- `mori-shokunin/tools/mori-freeze-order.py:1-3`; `mori-shokunin/SKILL.md:179`
- `kengaku-shokunin/corpus/evidence/attrib-r22-opencode-trials.log:8,46,71`
- `souji-shokunin/tools/souji-worktree-drift.py:24-25,48-50,88-89,164-178`
- `kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:16`
- `corpus/SOURCES.md:3,38,39` (`S009`, `S010`) and the max row `S257`
- `git show e2a7431:corpus/lessons/round-40.md:49` ("worktree.c appears in 9 rows")
- Candidate digests as in §0.
