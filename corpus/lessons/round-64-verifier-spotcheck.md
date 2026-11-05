author: hyaku closure (non-author integrator, @m_zfl)

# Round 64 verifier spot-check — souji (honest stop)

Non-author closure verification of `.ufo/reports/round-64/souji.md` against lane tip
`5888654e71cde8a00ba333d29335fd515e2171de` (base `ae2f4ece2c936ecd8c4260632ad7330c84f7882d`).
I did not author this round; every measurement below was re-run by me on committed bytes at closure.

## 1. Conformance results

| check | command | result |
|---|---|---|
| report committed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H' -- .ufo/reports/round-64/souji.md` | `souji-shokunin <souji@shokunin.local> 786750dcb54aab922e9b2315fecefe168a77375c` — PASS |
| `SHONEN` heading, one line per box | read report | 4 boxes, each `[~]` with pointer; no `[x]` — PASS |
| cited lane commits exist and are ancestors of branch | `git cat-file -t <h>` + `git merge-base --is-ancestor <h> refs/heads/master` for `04bc2769…`, `a722b476…`, `5888654e…` | all type=commit, all ancestor=yes — PASS (jj-colocated; ancestry tested against the branch ref, not `@{u}`) |
| no uncommitted round work; pushed | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `local=5888654e… remote=5888654e… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty — PASS |
| prompt carries template contract | rendered `templates/round-prompt.md` (LANE=souji, ROUND=64, fleet root, lane axes) and diffed against `.ufo/prompts/souji-round-64.md` sections 1–5 | byte-identical (`TEMPLATE-SECTIONS-MATCH`); §6 hyaku addendum present — PASS. Round-level items (mission/axes binding, L2 ≥8 = MISSION.md §L2, commit-then-push, push scope, L0 channel) and the five child-lane items (report path, commit-before-report, SHONEN heading, commit-hash citation, write scope) all present |
| dispatch evidence | `.ufo/watchdog.log` | `2026-11-05T07:45:37-03:00 launch souji round=64 pgid=253902 driver=hyaku-inline attempt=1` and `2026-11-05T09:43:00-03:00 complete souji round=64; hyaku-inline attempt=1` both present; prompt committed at `97aa456f` — PASS |
| report is a real report, not a marker | content | names real committed work with checkable hashes; all required sections present in order — status `ok` |
| report contract sections | read report | Work performed / Landed changes / Before→after / Sources & frontier / Trend verdicts / SHONEN — all present — PASS |
| append-only discipline | `git diff ae2f4ece 5888654e -- corpus/lessons/round-63.md` | pure append (`@@ -116,3 +116,15 @@`), original text not rewritten — PASS |

Conformance defects (named, status-neutral): see §6.

## 2. Per-claim re-check (both claims declared NOT admitted; honest stop)

**C1 — operability (in-run snapshot, `GIT_INDEX_FILE` refusal, `:(top)` scope; score 8, not moved).**
Before-state re-run by me at base, using the committed counter and matrix, base writer bytes extracted with
`git show ae2f4ece2c936ecd8c4260632ad7330c84f7882d:tools/souji-receipt-write.py`:

```
python3 -B census/round-64/c1-counter.py --root . --matrix census/round-64/c1-matrix.tsv \
  --base-rev ae2f4ece2c936ecd8c4260632ad7330c84f7882d --new-tool <base-writer bytes> \
  --work /fast/scratch/hyaku/souji-r64-closure/work-dn --receipt .../c1-rerun-receipt.txt
→ SUMMARY matrix=13 base_forgeries=8 base_honest=3 new_forgeries=8 new_honest=3 class_mismatches=8 regress=PASS
→ EXIT=1  (instrument_sha256 aaaa…aed matches the committed control header; N4 base=accept reproduced)
```

Exact reproduction of `census/round-64/controls/c1-do-nothing.txt`. The M1 dispute is real: the counter's
N4 fixture gives `base=accept` while the design reviewer reports base-refusal; the 8/3 count is unresolved
and correctly not claimed. After-state: none — candidate `46a9388b…` is **not a git object** in the lane
(`git cat-file -t` → fatal), production bytes unchanged: `git diff ae2f4ece 5888654e -- tools SKILL.md
tests corpus/knowledge PROVINCE.md` → 0 bytes. Observed values match the report. **Verdict: unchanged.**

**C2 — calibration (3 SKILL.md statements vs writer bytes; lowest owned axis, score 7, not moved).**
Before-state re-run by me, bound to the committed population:

```
python3 -B census/round-64/c2-counter.py --root . --tsv census/round-64/c2-statements.tsv \
  --tsv-rev 04bc2769e14c5c5050a0c8b93a439e13adb8b69b --rev ae2f4ece2c936ecd8c4260632ad7330c84f7882d
→ FINDING SCOPE-OVERREACH s2 … SUMMARY rows=3 findings=1 verdict=FAIL rev=ae2f4ece… EXIT=1
```

Exact reproduction of `census/round-64/controls/c2-do-nothing.txt`. After-state: none (after-wording not
landed); SKILL.md unchanged. Observed values match the report. **Verdict: unchanged.**

Neither claim rests on a registered gate (the round-64 counters have no SKILL.md registry row); both were
re-measured by me, not evidence-verified from seat tallies. The seat-run diagnostics (selftest 26/26,
mutation kills) are correctly treated by the lane as non-admission evidence (lesson M2).

## 3. Per-axis verdicts

| axis | verdict | evidence |
|---|---|---|
| operability | **unchanged** | score 8 unchanged in SCORECARD; no after-state; before reproduced exactly (§2 C1); no harm (production bytes empty diff) |
| calibration | **unchanged** | score 7 unchanged in SCORECARD; no after-state; before reproduced exactly (§2 C2); no harm |
| coverage | **unchanged** | no claim declared; score 8 unchanged; SOURCES rows added (frontier), no capability row, `corpus/knowledge/` unchanged |

No owned axis harmed. No exploratory claim was declared, so no `unprovable-but-better` ruling was needed.

## 4. Discernment spot-check (LEARNING.md) — all four gate decisions sampled

Re-opened sources live at closure: `https://git-scm.com/docs/git` → HTTP 200, 244227 bytes,
sha256 `534c674f9929…f9d1`; `https://git-scm.com/docs/gitglossary` → HTTP 200, 109997 bytes,
sha256 `216bc0df7f50…f0129` — **byte-identical to the committed captures**, so the committed slice
assertions carry to the live pages. All six recorded slice assertions re-run by me → PASSED
(s295-located-quote `[113:230]`; s295-git-man `[30767:30884]`; s296-located-quote `[43:140]`;
s296-gitglossary-man `[15869:15966]`, `[15869:16033]`, `[15510:15647]`).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S295 git(1) `GIT_INDEX_FILE` | admit (mined, tier A) | live URL + committed captures + installed man page | **agree** | quote byte-verifiable on the live page (17 words ≤ 25; slice PASSED on two carriers); scope honest — the row claims only what the variable names |
| S296 gitglossary(7) `top` | admit (mined, tier A) | live URL + committed captures | **agree** | registered 18-word quote verified (slice PASSED); the 29-word full sentence is disclosed as over-limit with the 18-word registered form used; named limit records that `:(top)` is composed by the reader |
| "GIT_INDEX_FILE must be refused/scrubbed by any consumer that reads an index" | reject | live URL + man entry at offset 30767 | **agree** | the whole git(1) entry is the two descriptive sentences; no consumer-duty sentence exists on the page; flip is correctly stated |
| "`:(top)` is printed on the git-scm.com page" | reject | live URL + both captures | **agree** | 0 hits for the literal in the committed capture bytes and on the live page; binding is code (`pathspec.c` line 106), disclosed as a named limit with a routed code-row |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → **exit 0**
(`ok …/corpus/SOURCES.md`), with pre-existing-class `W04 duplicate url … across scopes` warnings
(informational). Census re-derived at both revisions: rows 217 → 219; malformed 0 → 0; tiers A=207→209,
B=7→7, C=3→3; status mined=179→181, queued=14→14, rejected=24→24 — matches the report. S294 `used-by`
at tip reads `corpus/lessons/round-63.md` (D2 applied, logged old→new). D1 re-proven mechanically:
`census/round-63/sources/s294-git-fast-import.html[109094:109103]` and `…txt[31190:31199]` are both
`A gitlink`; the recorded-then-corrected 109019/31053 land on the symlink-line tail / `100755` mode line;
the full 13-word quote is non-contiguous in both captures. The appended round-63 correction is accurate.

The lane's round-63 lesson carries the offsets in `## Post-review correction` with original text intact —
I grade this an honest, mechanically verified correction.

## 5. Trend verdicts (closure, with the outside spot-check now complete)

| trend | verdict | evidence |
|---|---|---|
| expansion | **unchanged** | `corpus/knowledge/` unchanged (empty diff); no capability row entered; 2 sourced frontier rows added but no admitted knowledge entry on uncovered ground |
| quality | **unchanged** | no admitted entry changed or re-verified; `QUALITY.md` untouched (not in the 31-file diff); D1 is a quality-positive correction to a lesson record, no criterion or score moved |
| discernment | **improved** | the lane filed `unchanged (spot-check pending)`; this closure's outside check now exists and **agrees with the gate on all admits and rejects** (2 admits + 2 rejects, §4) — the LEARNING.md improved condition; plus two self-caught overclaims (M1, M6) mined with evidence. Not claimed by the lane; established by this non-author check |

## 6. Routed defects and notes (status-neutral; none bars admission)

1. **Wave-dir evidence pointers do not resolve at closure.** `.ufo/waves/round-64/` (12 seat reports,
   `S64MutKill/kills.txt`, `S64ExecWriter/selftest.txt`, candidate writer) is absent on this host at
   closure time; gitignored, never pushed. The lane disclosed this as a durability named limit and no
   admitted claim rests on wave-dir bytes (both claims are not admitted; durable instruments and controls
   live in `census/round-64/` and all reproduce). The routed debt stands: **any future evidence a lesson
   cites must be committed before the freeze.**
2. **`census/round-64/SHA256SUMS.txt` pins the instruments, matrix and population but not the control
   receipts.** The controls carry inline `instrument_sha256` headers, which is what the freeze check
   binds; pinning the receipts too would close the gap. Lane hygiene, round 65.
3. **Round-64 `LOG.md` entry cites paths but no commit hashes** (the report's Landed-changes table
   carries the hashes). Minor observation only; the evidence standard binds hash citation where commits
   are cited, and none are miscited here.
4. **`W04` duplicate-URL warnings** from the census validator (S295/S296 reuse `git-scm.com/docs/git*`
   URLs already rowed under other scopes) — pre-existing tolerated warning class, exit 0; informational.
5. **Operator note (promotion is operator-owned):** all four SHONEN boxes carry resolvable pointers
   (SKILL.md decision tables/error patterns/checklists — 4 section hits; `LOG.md:362` operator sweep;
   `census/round-21/run-acceptance.py` + `accepted-matrix.json` exist; `PROVINCE.md` "Round21 privacy
   boundary" at line 195). The boxes look fully checkable by a non-author verifier; no `[x]` was written
   by me. Still-open operator L0 lines routed around, incl. `souji | round-64` planner-seat ruling
   (committed, durable).
6. **Carried to round 65 (lane's own routing, confirmed reasonable):** N4 realizability re-probe (M1),
   chronology gate landing before any freeze (M2), in-lane control builds (M3/M4), C2 green/decoy controls
   and dead-token falsifier, untracked-visibility claim, mode-only snapshot row, env-redirect named limit.

**Closure ruling:** report `ok`; claims rejected as honest stop (nothing frozen, nothing admitted); no
axis harmed; verdict `rejected-honest-stop`, `admitted=false`.
