# CritPrereg — falsifying the round-24 preregistration

Seat: `L1Souji24.CritPrereg` (critic, read-only). Target: `.ufo/waves/round-24/preregistration.txt`
at lane commit `f9db2181647d91470a724a12d626bd6106805076` (base `a65fac98964b445758e94c805728c9a19d302ff8`).
Contract: `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-24.md` §2, §9, §10; `/home/vgpnk/Projects/shokunin/AXES.md`.

## Status

STATUS: PARTIAL. No defect would invalidate the round yet. No counter receipt exists
(`census/round-24/records/` holds only `quarantine-slice`, `slice-verdicts.tsv` and an r13 recheck),
so every correction below can still land before data. I executed four counterexamples:

- C1's no-write manifest misses a transient `fsck --lost-found` write.
- C1's case 4 accepts a hard-coded linked-worktree discount.
- C3's case a cannot tell the durable-ref predicate from an all-refs mutant.
- The draft `verify` accepts receipts whose argv `run` refuses, so "verify/run symmetry" is
  broader than what the counter checks.

C2's do-nothing base value is `mismatches=2`, so the do-nothing control cannot reach the target.
It is reachable as 0 only by a counter bug that matches a basename anywhere in a row instead of in
the entries cell. One axis-legality question goes to the judge: is README a self-assessment surface?

## Evidence

All scratch work was under `/var/tmp/souji-r24-CritPrereg/` (since removed), with git 2.56.0,
`GIT_CONFIG_GLOBAL=/dev/null`.

1. **C2 base oracle.** This is my own implementation of the frozen predicate, not the lane tool.
   Command: `python3 -B c2oracle.py /home/vgpnk/Projects/shokunin/souji-shokunin a65fac98964b445758e94c805728c9a19d302ff8`
   ```
   grounded {'count-objects-garbage-readings-r25.md': 'F2', 'quarantine-origin-record-fields-r24.md': 'F4', 'quarantine-staging-no-copy-r23.md': 'F4', 'repo-size-census-readonly.md': 'F2'}
   MISSING-FROM-MAP count-objects-garbage-readings-r25.md
   MISSING-FROM-MAP repo-size-census-readonly.md
   basename-only-outside-entries-cell [('count-objects-garbage-readings-r25.md', [68]), ('repo-size-census-readonly.md', [68])]
   grounded=4 dangling=0 mismatches=2
   ```
   The five map tables are at README lines 36, 66, 214, 238 and 272, with 17 data rows. At base,
   12 of the `.md` files in `corpus/knowledge/` exist and only 4 carry a `ground:` line.
2. **CE1: transient write.** On a dangling-blob repo I ran `git fsck --lost-found`, which wrote one
   file to `other/`, then `rm -rf .git/lost-found`. I compared manifests of regular files
   (path, type, mode, size, mtime, sha256):
   `regular-file manifest: IDENTICAL after write+cleanup` and `dir mtimes: DIFFER` (on `.git` itself).
3. **CE2: linked worktree plus junk.** With `objects/pack/junk` in the common dir:
   `raw main: garbage: 1`, `raw linked: garbage: 2`, `common-dir: garbage: 1`.
4. **CE3: refs/jj-only commit versus dangling commit.**
   `ad154afb durable(heads|tags|remotes)=0 allrefs=1` (held only by `refs/jj/keep/x`) and
   `1a7e991f durable(heads|tags|remotes)=0 allrefs=0` (dangling).
5. **CE4: draft verify against run.** Draft is `.ufo/waves/round-24/w1/souji-receipt-run.py`, sha256
   prefix `cbe96d734e54aa6c`. Each crafted receipt had a true digest and a body of
   `entries=1 ok=1 fail=0`:
   - `cmd=git -C /elsewhere show tools/t.py` gave `verify=ok`, rc=0. Run's response to the same
     argv: `GIT-DIRECTED-COMMAND … rc=2`.
   - `cmd=git fsck --lost-found tools/t.py` gave `verify=ok`, rc=0.
   - `cmd=python3 tools/other.py tools/t.py` gave `verify=ok`, rc=0, with `tool=` passed only as a
     data argument.
6. **r23 regression receipts.** I read the five `census/round-23/records/*.tsv` at base. Every `rev=`
   is contained by `refs/heads/master` and `refs/remotes/origin/master`. Every `tool=` is the script
   argv element directly after `python3` or `python3 -B`. Neither new refusal (a, b) would refuse a
   regression receipt.
7. **Freeze tree.** `git ls-tree -r --name-only f9db218… -- .ufo/waves/round-24 census/round-24` lists
   only `assimilation/{collisions,quarantine-slice,reg-ids,staged-ids}`, `census-start.txt` and
   `preregistration.txt`. No control receipt was committed at freeze.

## Findings

1. **C1/C2 coupling: not a separability defect, but an identity hole through C2's count-based kill
   rule.** AXES.md:30–31 says: "Claims must be **causally separable** — each verifiable without the
   others having landed".
   - C2 reaches 0 without C1: map the two base entries (Evidence 1).
   - C1's counter reads no map.
   - So separability holds. The disclosed coupling (prereg:120, "C1's new F2 entry must also appear
     in the coverage map for C2's after-state to stay 0") is negative interference only.

   The defect is prereg:91: "Kill rule: grounded(tip) < grounded(base) -> C2 fails (no entry may be
   deleted or un-grounded to reach 0)".
   - **Counterexample:** C1 lands a new `ground: F2` entry (grounded goes from 4 to 5), and someone
     strips `ground:` from `repo-size-census-readonly.md` (5 back to 4). The kill rule passes and one
     MISSING mismatch vanishes by un-grounding, the exact act the parenthesis forbids.
   - Impacted axis: calibration.
   - **Smallest correction:** make the kill rule set-based. C2 fails if any entry grounded at base is
     absent at tip, or carries a different `F<k>`. Label: `pre-data-legal` (it would-invalidate after
     any seat scores C2).
2. **C2's counter grades itself, and the fixture that guards it has no frozen cases.**
   prereg:93: "an always-zero emitter must fail it." No case set is frozen, and passing the fixture is
   not part of C2's verdict.
   - **Counterexample:** a tool that matches a basename anywhere in an F2 row reads base
     `mismatches=0`, because README:68's status cell names both basenames: "**r23: the read side now
     holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`,
     `count-objects-garbage-readings-r25.md`)". The do-nothing control would then meet the target.
     This is the r23 spot-check's routed "table vs prose" defect.
   - The draft `tools/souji-coverage-agreement.py` reads `entries` from cell index 2 (lines 78 and
     101), so it would not trip this. Nothing frozen prevents a regression.
   - **Correction:** freeze fixture cases:
     - a basename only in the status cell gives MISSING;
     - an `F2` row does not satisfy an `F21` entry;
     - a dangling path;
     - a clean map;
     - the always-zero emitter is rejected.
   - Also make fixture exit 0 a C2 verification condition, and commit the base-control receipt
     (expected `mismatches=2` per Evidence 1). Label: `pre-data-legal`.
3. **C2 axis legality is a judge tradeoff, not a fixable defect.** Contract §9 (souji-round-24.md:360–361):
   "A calibration claim must count mismatches between the lane's self-assessment (SCORECARD/SHONEN)
   and observed repo state."
   - C2's self-assessment surface is `corpus/README.md`'s coverage map, not SCORECARD or SHONEN.
   - The base SHONEN has no coverage-map reference. The base SCORECARD's r23 C3 row asserts "F2
     holds three entries" but is not counted.
   - If the judge reads §9 literally, C2 is not a calibration claim and the lowest-axis obligation
     (calibration 7; saturation line 8, so the stagnation nudge is inactive) goes unmet.
   - Mitigation: state in the preregistration and the report that the coverage map is the lane's
     declared-coverage self-assessment. Cite AXES "gaps named honestly", and the r23 spot-check's
     routing of exactly this map defect as a self-assessment defect. Let the operator rule.
   - Label: `pre-data-legal` (wording only). Changing the surface would be `would-invalidate`.
4. **C2 title implies a universal it does not enumerate.** Contract L358: "Use no universal clauses
   … unless the counting command enumerates the full set."
   - "Declared coverage vs entry files" is evaluated over the 4 grounded entries out of 12 `.md`
     entries at base. 8 entries (F1, F3, F5 and older F4) are invisible to MISSING-FROM-MAP.
   - The predicate also has no notion of superseded rows: README:40 still reads "F2 … frontier, no
     entry … —", while a superseded row can satisfy or dangle a mapping.
   - **Correction:** wording such as "agreement over grounded entries (G of N)". Disclose the
     superseded-row limit. Label: `pre-data-legal`.
5. **C1's no-write manifest is defeated by a transient write (CE1).** prereg:48–49: ".git manifest
   (sorted path+type+mode+size+mtime+sha256 of regular files; atime/ctime excluded)".
   - A tool that internally runs `git fsck --lost-found` and then removes `.git/lost-found` passes
     cases 1, 2 and 6: the manifest is identical and no lost-found remains.
   - Case 6 tests only the CLI argv.
   - Impacted axes: coverage (the claimed "measured no-write envelope") and operability.
   - **Correction:** add every directory entry with its mtime_ns to the manifest; CE1 shows the
     `.git` directory mtime moves. Alternatively, run cases 1–6 against a `chmod -R a-w` copy of
     `.git`, so any write attempt fails loudly.
   - Label: `pre-data-legal`. The manifest definition is part of four case oracles, so it would
     invalidate after scoring.
6. **C1 case 4 does not distinguish the claimed mechanism from a hard-coded discount (CE2).**
   prereg:53–54: "tool on a linked worktree path: garbage=0, while raw `git -C <linked>
   count-objects -v` reads garbage: 1".
   - A tool that hard-codes `if invoked_from==linked: garbage=0` passes cases 3 (run on the main
     path) and 4, but reports 0 where the true common-dir figure is 1 (CE2).
   - **Smallest correction inside the frozen text:** case 3 runs the junk repo through both its main
     path and a linked worktree path, each expecting `garbage=1`. Case 3's frozen text names no
     invocation path, and C stays 8.
   - Label: `pre-data-legal`, and arguably not a re-specification.
7. **C3 case a cannot see the lane's real non-durable class (CE3).**
   - prereg:104: "a well-formed receipt whose rev is a full commit reachable from no durable ref".
   - The draft fixture builds a commit held by no ref at all: `r24-receipt-verify.py:199`,
     `dangling = ctx.git("commit-tree", tree, "-p", rev, "-m", "r24 fixture: never stored in a ref")`.
   - A verify mutant using `for-each-ref --contains` over all refs also refuses that commit, but
     accepts a refs/jj-only commit (CE3: `allrefs=1`, durable=0). That breaks Q37, which the runner
     states at `tools/souji-receipt-run.py:127`: "True when rev is a commit reachable from a durable
     ref (never refs/jj/*)."
   - **Correction:** add a second case-a instance whose commit is held only by `refs/jj/keep/<x>`.
     This stays within the frozen sentence.
   - Label: `pre-data-legal`.
8. **C3's title asserts symmetry that the case set does not enumerate (CE4).** The title (prereg:95)
   is "Receipt verify/run symmetry (r23 named residuals)".
   - `run` refuses GIT-DIRECTED commands, `--lost-found` and mutating subcommands (`command_refusal`,
     `tools/souji-receipt-run.py:93–107`).
   - Draft `verify` accepts receipts carrying those argv shapes (Evidence 5).
   - Impacted axes: operability (the claimed outcome) and calibration (overreach).
   - **Correction:** either retitle to "two named r23 residuals" (wording), or add
     `command_refusal(shlex.split(cmd))` to verify with one frozen case.
   - Label: `pre-data-legal`. Adding a case after scoring would invalidate.
9. **C3's label predicate binds weakly.** "`tool=` path does not occur as an argv element of its
   `cmd=`" accepts `tool=` as a data argument (CE4 receipt rC: `python3 tools/other.py tools/t.py`
   gives `verify=ok`).
   - **Correction:** require `tool=` to be the script position: argv[0], or the first non-option
     argv after `python3`, `bash` or `sh`. All five regression receipts satisfy this (Evidence 6),
     so `regress=5/5` is unaffected.
   - Label: `pre-data-legal`. It would-invalidate after any seat scores C3.
10. **C3's after-value is not one concrete line.** prereg:101: "Last line: cases=C pass=P
    refusals=R/2 regress=N/5 ; exit 0 iff P==C."
    - C is never fixed. A fixture that silently drops a case still exits 0 with P equal to C.
    - **Correction:** pin the full target line, for example
      `cases=<n> pass=<n> refusals=2/2 regress=5/5`, with n stated.
    - Label: `pre-data-legal`.
11. **C3 really is operability by surface.** The change is the `verify` code path of a runnable tool,
    and the refusals arm executes it. Arm d (`regress=5/5`) is reachable by doing nothing, but it is
    a no-harm guard, not the claim. Arm b checks a receipt against itself (record-consistency), but
    §9's surface rule ("Name the axis by the surface the round changes") puts it in operability.
    One limit: durability is evaluated against live refs at verify time, not committed bytes, so
    deleting a ref could later flip a regression receipt. Disclose this. No amendment.
12. **The §9 control-receipt timing was missed.** Contract L366–368: "Before freezing, build the
    cheapest control that skips the claimed work, score it with the frozen counter, and commit that
    receipt".
    - The freeze tree has no control receipt (Evidence 7).
    - prereg:61–63 defers C1's control to "before any after-data", and C2 and C3 name controls with
      no commit point.
    - The deviation stands and must be reported. Remedy: commit the C1 stub, C2 base
      (`mismatches=2`) and C3 base-runner (`refusals=0/2`) receipts before any after-data.
    - Label: `pre-data-legal` remedy. The disclosure is mandatory.
13. **C1's before-value is shaped like an output that never ran.** prereg:61: "at base the fixture and
    tool are absent -> `cases=0 pass=0`". The counter cannot print that at base; it fails on a
    missing file.
    - **Correction:** state the before-value as `git cat-file -e a65fac9…:tests/fixtures/r24-size-census.py`
      exiting nonzero (prereg:31 already names this command).
    - Label: `pre-data-legal` (wording).
14. **Assimilation is not claim-slot abuse, but it carries risk.**
    - No counter credits the entry, and F2 is already held, so no expansion credit is claimed. That
      is consistent with §10: "it adds no claim slot and never relaxes the canonical contract."
    - **Risk (a):** §2b.4's sourced claim rides on an entry C1's verdict does not depend on. If
      re-opening admits zero entries, C1 still passes but §2b.4 and §10's "≥1 admit" fail. Name a
      fallback now: re-open S115/S116 this round and cite them from the C1 tool's or fixture's
      knowledge pointer.
    - **Risk (b):** the non-appendable own-work list (prereg:128, "S134/S141/S147/S153 staged ids")
      omits S130 and S131. Package `count-objects-garbage-semantics-r23.md` line 3 reads "source:
      S131 — lanes/souji/round2/evidence/r23-worktree-census.out". That entry's headline,
      "`garbage` is filesystem debris, not object-graph state — and the fleet is not currently
      exposed" (MERGE-REPORT.md:26), is a fleet claim the HARD BOUND and prereg:66–67 exclude. It is
      the same class r23 already rejected (staged S134), so it should not fill the "≥1 rejected"
      quota as a fresh discernment sample without saying so.
    - **Risk (c):** the r25, r26 and r27 package entries each cite one own-work fixture as their only
      source (line 2 of each). Admitting one means re-grounding wholly on new rows. Record that
      provenance honestly, as a lane-authored rewrite of a package claim. Do not let the C1 fixture
      become the entry's evidence: that would be circular, the tool justifying itself.
    - Label: all `pre-data-legal`.
15. **Small internal inconsistency.** Separability (prereg:116) says C1 touches "one knowledge
    entry", while Assimilation says "At most 2 admitted". Align them.
    - Lane measurement (prereg:66–68): wrap the single lane run with a manifest of `.git/objects`
      before and after; exclude `index`, since the helper and jj may write it concurrently. That
      makes "no write" observable on the lane itself. This is not a counter.
    - Label: `pre-data-legal`.

## Attack log

| # | attack | target | executed | result | amendment label |
|---|---|---|---|---|---|
| A1 | C1 entry inflates grounded while an existing entry is un-grounded | C2 kill rule | reasoning on prereg:91, base G=4 (Ev.1) | kill rule passes; defect | pre-data-legal |
| A2 | basename matched in status cell | C2 counter/fixture | Ev.1 `basename-only-outside-entries-cell` rows [68] | base would read 0; defect if unfenced | pre-data-legal |
| A3 | do-nothing C2 control | C2 target | Ev.1 | `mismatches=2`; cannot reach 0 | — (holds) |
| A4 | fsck --lost-found then cleanup | C1 manifest | CE1 | regular-file manifest identical; dir mtime differs | pre-data-legal |
| A5 | linked-path hard-coded `garbage=0` | C1 case 4 | CE2 | passes case 4; wrong on linked+junk | pre-data-legal |
| A6 | all-refs durability mutant | C3 case a | CE3 + draft fixture:199 | indistinguishable on dangling commit | pre-data-legal |
| A7 | verify accepts run-refused argv | C3 "symmetry" | CE4 rA, rB | `verify=ok` rc=0 vs run rc=2 | pre-data-legal |
| A8 | tool= as data argument | C3 case b predicate | CE4 rC | `verify=ok` rc=0 | pre-data-legal |
| A9 | new refusals break r23 receipts | C3 regress arm | Ev.6 | no; all 5 durable and tool in script position | — (holds) |
| A10 | C1 counter reads C2 files / C2 needs C1 | separability | read prereg:116–121, Ev.1 | separable; interference only | — (holds) |
| A11 | control receipt before freeze | §9 | Ev.7 | absent at freeze | pre-data-legal remedy + disclose |

Tool installs: none. Scratch `/var/tmp/souji-r24-CritPrereg/` removed after the report was written.
