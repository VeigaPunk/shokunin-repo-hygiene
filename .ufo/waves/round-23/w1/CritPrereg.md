# CritPrereg — falsification of the round-23 preregistration (w1, critic)

STATUS: FAIL — not admissible as frozen: C1's `mismatches=0` is unreachable on the real
`SCORECARD.md:14` shape, the preregistration and its counter were amended at 05:19:06 *after*
seats had already scored, C1's newest K1 depends on C2's field (separability broken), and C3 is
assimilation occupying a claim slot whose target a do-nothing control reaches. Base
`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`; nothing landed.

## Evidence

All runs read-only. Scratch under `/var/tmp/souji-r23-CritPrereg/`, removed; no lane write, no
`git add/commit/push/stash/checkout`, no `jj` mutation, no `rm`/`mv` in the lane, no pacman.

**The frozen contract and its counter moved four times inside the round.**

```
preregistration.txt  v1 05:05:48 (read by this seat) -> 05:19:06 sha 76ca4928a0e3899390726f5141eaf396ef511ab8d7cba51649b2a06bb3ba63f5
tools/souji-record-agreement.py
  05:08     303 lines
  05:11     327 lines  sha 7515bb29cf85f5a94e1b0fecb4368daad80ed9298b5d13d4dd9e2d991a7ab902
  05:19:06  333 lines  sha e41db3043b865acc292d2993a92d2a8a6f79df2d2c6f138b275192454e57e596
  05:21:56  350 lines  sha 66ee7ecfcbc749c368e39ce9f7c51420eacb58c6a6ee27f8c11183b3956239fc
```

`w1/MutCounter.md:1-24` scored 42 clause mutants against `7515bb29…` (327 lines) and watched the
file move 303→327. `w1/ExecGateReproduce.md:129-131` measured the v1 C3 command at rc 2. Both
precede the 05:19:06 rewrite (K4 exemption file, C3 counter command, entry-2 name) and every
later counter edit. The prereg annotates the K4 change "Amended pre-data … before any after-data"
— but §9's test is *after any seat has scored*.

**C1 control at base, by counter version** (worktree read; same `--rev`):

```
327-line bytes : keys=4 records=3 occurrences=13 mismatches=18  rc=1
333-line bytes : keys=4 records=3 occurrences=13 mismatches=20  rc=1
350-line bytes : keys=4 records=3 occurrences=13 mismatches=26  rc=1
350-line, --no-worktree : keys=4 records=3 occurrences=13 mismatches=6  rc=1   (K4 dropped, keys still 4)
```

**K1 on the real record shape, newest bytes** (scratch repo reproducing `SCORECARD.md:14`: base
tuple and after tuple and both revisions on ONE physical line; every other key satisfied):

```
MISMATCH K1 SCORECARD.md:1 value-disagree assertions=55 resolved=52 skipped=33 mismatches=3
         != receipt assertions=63 resolved=63 skipped=40 mismatches=0 at 9301d98c… (rc=1)
delete the base tuple from that row -> keys=4 records=4 occurrences=12 mismatches=0  (rc=0)
```

**C2 counter** (scratch: four receipts carrying the stale digest the claim says must be refused):

```
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
4        # each file: tool_sha256=5b8025a8aaaa…
```

**C3 command, v1 as frozen** (my run and `ExecGateReproduce.md:130`):

```
$ python3 tools/souji-gate-check.py --entries … --snapshot-dir <dir> --expect-slice 0
souji-gate-check.py: error: unrecognized arguments: --expect-slice 0    rc=2
```

**C3 command, current text**, and the do-nothing control on it:

```
$ python3 tools/souji-gate-check.py --root <lane> --round-date 2026-10-25 --entries
  corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md
  --snapshot-dir census/round-23/sources --slice …/empty-slice --slice-verdicts …/empty-verdicts
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=3   rc=1
$ python3 tools/souji-gate-check.py --round-date 2026-10-25 --entries
  corpus/knowledge/quarantine-staging-no-copy-r23.md corpus/knowledge/quarantine-origin-record-fields-r24.md …
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0   rc=0    # committed r22 entries, no round work
```

**Records measured at base.** `corpus/SOURCES.md` 114 rows, max `S114` = gio/`g_file_trash`/statx
(the quarantine rows). Staged entries cite `S112,S113,S114` and `S134,S138,S139`.
`census/round-22/attempt2/declared-evidence-before.tsv` counts `assertions=56 resolved=53
skipped=33 mismatches=3`; `…-before-final.tsv` counts `55/52/33/3`. `corpus/README.md:40` is the
r12 F2 row (`frontier, no entry`); `:64` is `## Round 13 current coverage (supersedes the r12 F2
row)` and `:68` gives F2 a bounded structure-census capability with
`knowledge/git-repo-structure-readonly.md` (S035/S036/S037). `SCORECARD.md:9-15` scores
calibration 7 / operability 8 / coverage 8; `:116-119` saturation line 8, window 3;
`:145-148` retired: none.

## Findings

**F1 — C1's after-state is unreachable without erasing the before measurement.** `prereg:27-31`
(K1) vs `tools/souji-record-agreement.py` `k1()` (350-line bytes) and `SCORECARD.md:14`. The row
carries `assertions=55 resolved=52 skipped=33 mismatches=3` **and** `63/63/40/0` plus both
revisions on one physical line; K1 binds every tuple on a line that contains the receipt's `rev`,
so the base tuple must equal the after receipt. Clean isolation on the newest bytes: exactly one
mismatch, `K1 value-disagree` on the base tuple; the only route to `0` is deleting that tuple from
the row AXES requires to carry before→after. *Amendment:* scope K1 to the tuple that follows the
receipt's rev token (or the last tuple on the row) — **would-invalidate** (mutants were scored
against `7515bb29…`; the counter has since changed twice).

**F2 — the frozen document and its counter were amended after seats scored.** `prereg` mtime
05:19:06, sha `76ca4928…`; v1 (05:05:48) carried `--expect-slice 0`,
`count-objects-garbage-semantics-r24.md`, and K4 over `corpus/pointer-exemptions.tsv` with an
`uncommitted:` prefix. The current text changes all three; the counter changed again at 05:21:56
(adding `K4_ALLOWED`, `K2_FILED`, `RECEIPT_TOOL_RE`). *Amendment:* none legal for the changed
clauses; the report must judge C3/K4 on the pre-amendment predicate — **would-invalidate**.

**F3 — C1's K4 is self-zeroing.** `prereg:41-45` says `corpus/pointer-exemptions.tsv` rows
prefixed `uncommitted:` for operator-owned paths; the counter reads
`census/round-23/records/uncommitted-exemptions.tsv` with `K4_EXEMPT_PREFIX = ""` plus a
hard-coded `K4_ALLOWED = {"census/operator-sweep-20261019/"}`. Scratch: a committed exemption
naming the lane's own unfinished file plus a dirty worktree → the named path is silently exempt;
only an unnamed path fires. D1's key measures "did the lane list its dirt". *Amendment:* restore
an ownership predicate or derive K4 from committed bytes — **would-invalidate**.

**F4 — C1's value is not re-derivable over committed bytes.** `prereg:22-25,47-48`; `k4()`.
At `--rev 1208bfb` the K4 rows include `tools/souji-receipt-run.py`, `.ufo/waves/round-23/`,
`tools/__pycache__/` — none in that tree; the base value moved 18→20→26 across counter versions
and untracked seat files. `--no-worktree` drops K4 and still prints `keys=4`.
*Amendment:* **would-invalidate**.

**F5 — C2's counter does not measure the claim.** `prereg:70-74`; the counter counts files, not
verifications. Four receipts carrying the stale `5b8025a8…` digest — the value the claim says
must be refused — score 4. `w1/SentinelScope.md:126` already filed the same observation as data.
*Amendment:* count receipts whose `verify` exits 0 — **would-invalidate**.

**F6 — C2's after-state is a threshold, not a value.** `prereg:72-75`: `>= 4` plus a per-receipt
second command. §9 asks for one concrete value, one command. **would-invalidate**.

**F7 — C2 overstates its closure of D3.** `prereg:68-70` vs `:70-80`: the stale `5b8025a8…`
digest in the r22 report text is never counted; only receipt presence is. *Amendment:* wording —
**pre-data-legal** (no predicate change), but the claim's scope must shrink to what it counts.

**F8 — C3's counter was unrunnable as frozen; its replacement is post-scoring.** v1
`prereg:96-98` → rc 2; current `:95-101` runs (`fail=3` at base). The fix is the kumitate-r42
pattern §9 forbids. **would-invalidate**.

**F9 — C3's "2 entries, 3 rows" is false against the rows the claim needs.** `prereg:81,86-88`
vs `w1/ScribeEntryGarbage.md:162-164` (S138/S139 re-pointed to S118/S119) and
`w1/ScribeSourcesRows.md:5` (rows 114→119, five rows), enforced by `souji-gate-check.py` check5
(any cited id absent from the registry fails). The target `>=117` is met by five; the declared
shape and C1's `Sourced ground: S115/S116/S117` describe a three-row round. *Amendment:* freeze
the id set and the exact row count — **would-invalidate**.

**F10 — C3's slice arm cannot fail.** `prereg:97-99` binds `--slice …/empty-slice
--slice-verdicts …/empty-verdicts`; `check_slice` returns `(0,0,[])` for an existing empty slice
and `run()` passes when `v == t`. Zero verdicts → `fail=0`. *Amendment:* state that no register
slice lands this round and drop the arm — **pre-data-legal** (no target value changes),
disclosed.

**F11 — C3's coverage premise quotes a superseded row.** `prereg:83-86` cites
`corpus/README.md:40` (`frontier, no entry`), which `:64` supersedes; `:68` gives F2 an entry and
a capability. §10 allows expansion credit only on ground the lane did not hold. *Amendment:*
cite `:64-68` and state the delta over `git-repo-structure-readonly.md` — **pre-data-legal**
(counters untouched) if the delta is shown; if it cannot be, the claim is quality work, not
coverage (§9), and the coverage credit fails.

**F12 — Assimilation occupies a claim slot.** `prereg:83` vs the round contract §10 ("it adds no
claim slot … rides inside §2b") and §9 ("Prefer 2 claims. Add a 3rd only if it is independent and
cheap to verify"). C3 is neither cheap nor independently verifiable. *Amendment:* demote C3 to
§2b and keep C1+C2 — **pre-data-legal** structurally; C3's numbers then report as frontier
evidence, and its broken counter must still be disclosed.

**F13 — C3's re-grounding clause is a universal without an enumerating command.** `prereg:88-91`
("every cited source re-opened … with this lane's own access date") vs `souji-gate-check.py`
(the round date must appear once per Gate; one verbatim quote per entry; ids resolve). Five cited
rows pass with one opened date per entry. *Amendment:* scope the clause to the quoted sources or
enumerate per-source opened dates — **pre-data-legal** wording; an unmeasured universal stays a
§9 hit.

**F14 — C1's "four declared r22 bookkeeping defects are repaired" is not enumerated.** `prereg:12-16`
vs `K1_RECORDS = ("SCORECARD.md",)`: D2's second half (report tip vs SCORECARD measured commit)
is unchecked; K4 counts paths, not D1's "none uncommitted" text; D6/D7/D8 have no frozen
disposition anywhere in the prereg (contract §6.5 requires one). *Amendment:* add the textual
checks — **would-invalidate**; the D6/D7/D8 disposition lines — **pre-data-legal**.

**F15 — C1's control receipt is not committed before freezing and its value is contaminated.**
`prereg:52-56`; `census/round-23/records/` holds `declared-evidence-after.tsv`,
`gate-check-at-first-landing.tsv`, `gate-check-at-lane-base.tsv`, `uncommitted-exemptions.tsv` —
no `agreement-control-base.tsv`. The base value is 18/20/26 only because the round's own untracked
artifacts count; the record-only value is 6. *Amendment:* commit the control receipt now binding
the record-only value and disclose the contamination — **pre-data-legal**.

**F16 — K2's receipt path in the sentence is not the code's.** `prereg:32-34` names
`declared-evidence-before.tsv` (`56/53/33/3`, equal to LOG's filed occurrence → no correction
needed, D5's counts half is a non-defect); the counter uses `-final` (`55/52/33/3` → stale).
`w1/ScribeLesson.md:121` attributes `55/52/33/3` to the non-final file. *Amendment:* name
`-final` in the sentence — **would-invalidate**.

**F17 — at the newest counter, C1 cannot verify unless C2 lands.** 350-line `k1()` rejects a
receipt without a `tool_sha256=` header (`receipt-unbound`: "a hand-written counts line is not a
receipt"). C1's K1 receipt is therefore bound to C2's binding field, and the clause is absent
from the frozen K1 text (`prereg:27-31` lists only `receipt-absent`, `value-disagree`,
`rev-disagree`). The assigned separability question answers differently by version: separable at
v1 (a hand-made receipt satisfied K1), **not separable at the current bytes**. *Amendment:*
either freeze the clause in the prereg (C1 depends on C2 by construction) or drop it from K1 —
**would-invalidate** (the clause postdates the scored mutants).

## Assigned checks — direct answers

| check | answer |
|---|---|
| causal separability | At v1 separable in predicate; **at the current counter C1 requires C2's `tool_sha256=` field** (F17). Even at v1 the two claims share `census/round-23/records/declared-evidence-after.tsv`, which can be C1's evidence and refused by C2's verifier at once — no counter detects that contradiction (F5). C3 is separable but cannot verify (F1/F9). |
| one concrete value, one command | No for all three: C1 reads a live worktree and a file that moved four times (F1/F4); C2 is `>=4` plus a second command per receipt (F6); C3 is three targets, two commands, one vacuous arm (F9/F10). |
| universal clause without enumeration | C1 "the four … defects are repaired" (F14), C2 "a verifier that refuses a receipt whose digest is not the blob" (F5), C3 "every cited source re-opened" (F13). |
| lowest-axis obligation | Binds: calibration 7 is the lowest non-retired (`SCORECARD.md:9-15`; saturation 8 at `:116-119`; none retired at `:145-148`), so the stagnation nudge cannot waive it. C1 nominally targets it, but C1 cannot reach `mismatches=0` → the obligation is **unmet**. |
| axis named by surface | C1 and C2 yes. C3 names the process (Assimilation), and its surface is already held (`README:64-68`) — F11/F12. |
| do-nothing control | C1: exists, uncommitted and contaminated (F15). C2: a base observation, not a skip-the-work control — four invalid receipts reach 4 (F5). C3: a different counter; the frozen target string is reached on committed r22 entries (`entries=2 ok=2 … fail=0`, rc 0). |
| Assimilation a claim-slot abuse | Yes — F12. |

## Attack log

- **A1** K1 binds both ends of the row → M=0 unreachable. *Confirmed* on 327-, 333- and 350-line
  bytes; clean isolation on the newest (one mismatch; zero after deleting the base tuple).
- **A2** freeze-by-reference: prereg amended 05:19:06 and counter edited four times, all after
  scoring. *Confirmed* (mtimes, shas, seat reports).
- **A3** K4 self-exemption and live-worktree dependence. *Confirmed* (scratch; `--no-worktree`).
- **A4** C2 counter gameable by receipts the claim calls invalid. *Confirmed*; already on record
  as data in `w1/SentinelScope.md:126`.
- **A5** C3 target reachable by a do-nothing control. *Confirmed* (`fail=0` on committed r22
  entries); v1's command additionally could not execute.
- **A6** C3 "3 rows" vs the five rows the claim needs. *Confirmed* against the wave's own row
  plan; the frozen lower bound `>=117` happens to be satisfiable by five, so the defect is the
  declared shape and C1's id line, not the bound.
- **A7** C1↔C2 separability broken by K1's `receipt-unbound` clause. *Confirmed* on the 350-line
  bytes; absent from the frozen text.

No tool installs or upgrades; no pacman transactions (host pause respected). Scratch removed.
